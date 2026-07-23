#!/usr/bin/env python3
"""Tests for the independent physical no-entry certificate replayer."""

from __future__ import annotations

import ast
import copy
import json
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any

import physical_no_entry_replayer as replay


HERE = Path(__file__).resolve().parent


def load_certificate() -> dict[str, Any]:
    return replay.strict_load(replay.CERTIFICATE_PATH)


def reseal_certificate(certificate: dict[str, Any]) -> None:
    """Refresh all ordinary bundle hashes after an adversarial mutation."""

    nodes = certificate["tree"]["nodes"]
    by_id = {node["node_id"]: node for node in nodes}
    for node in reversed(nodes):
        if node["node_kind"] == "split":
            payload = node["payload"]
            left = by_id.get(payload["left_child_id"])
            right = by_id.get(payload["right_child_id"])
            if left is not None:
                payload["left_child_semantic_sha256"] = left[
                    "node_semantic_sha256"
                ]
            if right is not None:
                payload["right_child_semantic_sha256"] = right[
                    "node_semantic_sha256"
                ]
        node["node_semantic_sha256"] = replay.semantic_sha256(
            replay._node_payload_without_hash(node)
        )
    root = by_id.get(certificate["tree"]["root_node_id"])
    if root is not None:
        certificate["summary"]["root_node_semantic_sha256"] = root[
            "node_semantic_sha256"
        ]
    split_count = sum(node["node_kind"] == "split" for node in nodes)
    leaf_count = sum(node["node_kind"] == "leaf" for node in nodes)
    unresolved = sum(
        node["node_kind"] not in {"split", "leaf"} for node in nodes
    )
    certificate["summary"]["node_count"] = len(nodes)
    certificate["summary"]["split_nodes"] = split_count
    certificate["summary"]["leaf_count"] = leaf_count + unresolved
    certificate["summary"]["excluded_leaves"] = leaf_count
    certificate["summary"]["unresolved_leaves"] = unresolved
    certificate["summary"]["maximum_depth"] = max(
        node["depth"] for node in nodes
    )
    certificate["outcome"]["unresolved_leaves"] = unresolved
    certificate["outcome"]["all_leaves_excluded"] = unresolved == 0
    certificate["solver_registry_semantic_sha256"] = (
        replay.semantic_sha256(certificate["solver_registry"])
    )
    certificate["certificate_semantic_sha256"] = replay.semantic_sha256(
        replay._certificate_payload_without_hash(certificate)
    )


def first_leaf(certificate: dict[str, Any]) -> dict[str, Any]:
    return next(
        node
        for node in certificate["tree"]["nodes"]
        if node["node_kind"] == "leaf"
    )


class StrictPrimitiveTests(unittest.TestCase):
    def test_reduced_dyadic_round_trip(self) -> None:
        values = [
            Fraction(0),
            Fraction(3, 8),
            Fraction(-17, 4),
            Fraction(1 << 200, 1),
        ]
        for value in values:
            self.assertEqual(
                replay.parse_dyadic(replay.dyadic_json(value)), value
            )

    def test_noncanonical_dyadics_are_rejected(self) -> None:
        for value in (
            {"numerator": 0, "exponent": 1},
            {"numerator": 2, "exponent": 1},
            {"numerator": 1, "exponent": -1},
            {"numerator": True, "exponent": 0},
        ):
            with self.assertRaises(replay.NoEntryReplayError):
                replay.parse_dyadic(value)

    def test_strict_json_rejects_duplicates_and_floats(self) -> None:
        with self.assertRaises(replay.NoEntryReplayError):
            replay.strict_loads('{"a":1,"a":2}')
        with self.assertRaises(replay.NoEntryReplayError):
            replay.strict_loads('{"a":0.5}')
        with self.assertRaises(replay.NoEntryReplayError):
            replay.strict_loads('{"a":NaN}')

    def test_arb_endpoint_serialization_is_exact(self) -> None:
        with replay.precision(192):
            value = replay.interval_arb(Fraction(1, 3) * 0, Fraction(7, 8))
            lower, upper = replay.exact_arb_bounds(value, "$.control")
        self.assertLessEqual(lower, Fraction(0))
        self.assertGreaterEqual(upper, Fraction(7, 8))
        self.assertEqual(
            replay.parse_dyadic(replay.dyadic_json(lower)), lower
        )
        self.assertEqual(
            replay.parse_dyadic(replay.dyadic_json(upper)), upper
        )

    def test_boundary_contact_is_not_an_exclusion(self) -> None:
        self.assertIsNone(
            replay.derive_empty_image_witness(
                Fraction(1, 2),
                Fraction(1, 2),
                Fraction(8),
                Fraction(1, 2),
                0,
            )
        )

    def test_strict_coordinate_gap_is_positive(self) -> None:
        witness = replay.derive_empty_image_witness(
            Fraction(3, 4),
            Fraction(1),
            Fraction(8),
            Fraction(1, 2),
            0,
        )
        self.assertIsNotNone(witness)
        assert witness is not None
        self.assertGreater(
            replay.parse_dyadic(witness["margins"]["minimum"]), 0
        )
        self.assertGreater(witness["nmin"], witness["nmax"])


class TrustBoundaryTests(unittest.TestCase):
    def test_forbidden_modules_are_not_imported_or_loaded(self) -> None:
        source = Path(replay.__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported: set[str] = set()
        called_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
        self.assertTrue(replay.FORBIDDEN_DYNAMIC_NAMES.isdisjoint(imported))
        self.assertTrue({"exec", "eval", "__import__"}.isdisjoint(called_names))

    def test_source_binding_code_anchor_matches(self) -> None:
        self.assertEqual(
            replay.normalized_lf_sha256(replay.SOURCE_BINDING_PATH),
            replay.SOURCE_BINDING_REPLAYER_NORMALIZED_LF_SHA256,
        )

    def test_problem_binding_replays(self) -> None:
        problem, source = replay.replay_source_problem_binding()
        self.assertEqual(
            replay.source_semantic_sha256(problem),
            replay.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(source["first_valid_index"], 2)


class CertificateReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = load_certificate()
        cls.problem, _ = replay.replay_source_problem_binding()

    def test_full_certificate_replays(self) -> None:
        result = replay.replay_certificate_objects(
            copy.deepcopy(self.certificate)
        )
        self.assertEqual(result["outcome"], replay.SUCCESS_OUTCOME)
        self.assertEqual(result["excluded_leaves"], 90)
        self.assertEqual(result["unresolved_leaves"], 0)
        self.assertFalse(result["all_time_no_entry_claimed"])
        self.assertFalse(result["exact_seam_equivalence_claimed"])

    def test_each_stored_leaf_matches_independent_recomputation(self) -> None:
        precision_bits = self.certificate["solver_registry"][
            "arb_backend"
        ]["precision_bits"]
        leaves = [
            node
            for node in self.certificate["tree"]["nodes"]
            if node["node_kind"] == "leaf"
        ]
        self.assertEqual(len(leaves), 90)
        for node in leaves:
            expected, enclosures = replay.derive_leaf_witness(
                self.problem, node["box"], precision_bits
            )
            self.assertEqual(len(enclosures), 9)
            self.assertTrue(
                replay.type_strict_equal(
                    expected, node["payload"]["witness"]
                ),
                node["node_id"],
            )

    def test_domain_cover_is_not_relabelled_as_exact_seam_quotient(self) -> None:
        registry = self.certificate["solver_registry"]
        self.assertIn(
            "no_exact_seam_equivalence_claim",
            registry["domain_topology_scope"],
        )
        self.assertFalse(
            self.certificate["outcome"][
                "exact_seam_equivalence_claimed"
            ]
        )

    def test_report_replays(self) -> None:
        result = replay.replay_certificate_objects(
            copy.deepcopy(self.certificate)
        )
        report = replay.strict_load(replay.REPORT_PATH)
        replay.verify_report(report, result)


class ResealedAdversaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = load_certificate()
        cls.problem, _ = replay.replay_source_problem_binding()

    def assert_rejected(
        self,
        certificate: dict[str, Any],
        *,
        physical_problem: dict[str, Any] | None = None,
    ) -> None:
        reseal_certificate(certificate)
        with self.assertRaises(replay.NoEntryReplayError):
            replay.replay_certificate_objects(
                certificate, physical_problem=physical_problem
            )

    def test_deleted_leaf_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        leaf = first_leaf(certificate)
        certificate["tree"]["nodes"].remove(leaf)
        self.assert_rejected(certificate)

    def test_changed_leaf_box_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        leaf = first_leaf(certificate)
        interval = leaf["box"]["intervals"][0]
        lower = replay.parse_dyadic(interval["lower"])
        upper = replay.parse_dyadic(interval["upper"])
        interval["upper"] = replay.dyadic_json((lower + upper) / 2)
        self.assert_rejected(certificate)

    def test_changed_coefficient_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        problem = copy.deepcopy(self.problem)
        coefficient = problem["kinematics"]["strings"][0]["modes"][0][
            "initial_x"
        ][0]
        coefficient["numerator"] += 2
        self.assert_rejected(certificate, physical_problem=problem)

    def test_changed_physical_period_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        problem = copy.deepcopy(self.problem)
        problem["target_torus"]["periods_L_A"][0] = replay.dyadic_json(16)
        self.assert_rejected(certificate, physical_problem=problem)

    def test_changed_witness_period_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        witness = first_leaf(certificate)["payload"]["witness"]
        witness["period"] = replay.dyadic_json(16)
        self.assert_rejected(certificate)

    def test_changed_axis_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        witness = first_leaf(certificate)["payload"]["witness"]
        witness["axis"] = (witness["axis"] + 1) % 9
        self.assert_rejected(certificate)

    def test_later_valid_axis_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        problem = self.problem
        precision_bits = certificate["solver_registry"]["arb_backend"][
            "precision_bits"
        ]
        periods = replay._dyadic_vector(
            problem["target_torus"]["periods_L_A"], 9, "$.periods"
        )
        radius = replay.parse_dyadic(problem["hysteresis"]["r_out"])
        replacement = None
        target_leaf = None
        for node in certificate["tree"]["nodes"]:
            if node["node_kind"] != "leaf":
                continue
            enclosures = replay.evaluate_d_enclosures(
                problem, node["box"], precision_bits
            )
            valid = [
                replay.derive_empty_image_witness(
                    lower, upper, period, radius, axis
                )
                for axis, ((lower, upper), period) in enumerate(
                    zip(enclosures, periods)
                )
            ]
            valid = [item for item in valid if item is not None]
            if len(valid) > 1:
                target_leaf = node
                replacement = valid[1]
                break
        self.assertIsNotNone(target_leaf)
        self.assertIsNotNone(replacement)
        assert target_leaf is not None and replacement is not None
        target_leaf["payload"]["witness"] = replacement
        self.assert_rejected(certificate)

    def test_fabricated_interval_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        witness = first_leaf(certificate)["payload"]["witness"]
        witness["d_enclosure"]["hi"]["numerator"] += 2
        self.assert_rejected(certificate)

    def test_boundary_contact_witness_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        witness = first_leaf(certificate)["payload"]["witness"]
        half = replay.dyadic_json(Fraction(1, 2))
        zero = replay.dyadic_json(0)
        witness["d_enclosure"] = {"lo": half, "hi": copy.deepcopy(half)}
        witness["nmin"] = 0
        witness["nmax"] = 0
        witness["margins"] = {
            "above_previous_image": zero,
            "below_next_image": zero,
            "minimum": zero,
        }
        self.assert_rejected(certificate)

    def test_wrong_outcome_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        certificate["outcome"]["type"] = "first_entry"
        self.assert_rejected(certificate)

    def test_unresolved_leaf_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        leaf = first_leaf(certificate)
        leaf["node_kind"] = "unresolved"
        leaf["payload"] = {"reason": "budget"}
        self.assert_rejected(certificate)

    def test_registry_rewrite_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        certificate["solver_registry"]["budgets"]["max_nodes"] = 8191
        self.assert_rejected(certificate)

    def test_tree_reordering_is_rejected_after_resealing(self) -> None:
        certificate = copy.deepcopy(self.original)
        certificate["tree"]["nodes"][1:3] = reversed(
            certificate["tree"]["nodes"][1:3]
        )
        self.assert_rejected(certificate)

    def test_self_asserted_certificate_hash_is_rejected(self) -> None:
        certificate = copy.deepcopy(self.original)
        certificate["certificate_semantic_sha256"] = "0" * 64
        with self.assertRaises(replay.NoEntryReplayError):
            replay.replay_certificate_objects(certificate)


if __name__ == "__main__":
    unittest.main()
