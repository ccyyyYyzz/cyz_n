#!/usr/bin/env python3
"""Controls for the independent symbolic-pi no-entry replayer."""

from __future__ import annotations

import ast
import copy
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import symbolic_no_entry_replayer as replay


EXPECTED_CERTIFICATE_SHA256 = (
    "d2cd11d1f8fd1b3669d988f590ee619e9a7f5ee6af43b3a0671830abc69f7fe1"
)
EXPECTED_ROOT_SHA256 = (
    "78d1589b4049483b2865e434ef3b3227a576daee654be042c9cd63419474c636"
)
EXPECTED_SOLVER_REGISTRY_SHA256 = (
    "23e404021dcae9b4c75dca810feb404afe6786aa14280f0ae88b0fa4f24fcec5"
)


def load_certificate() -> dict[str, Any]:
    return replay.strict_json_load(replay.CERTIFICATE_PATH)


def first_leaf(certificate: dict[str, Any]) -> dict[str, Any]:
    return next(
        node
        for node in certificate["tree"]["nodes"]
        if node["node_kind"] == "leaf"
    )


class StrictPrimitiveControls(unittest.TestCase):
    def test_strict_json_rejects_duplicates_floats_and_nonfinite(self) -> None:
        for text in ('{"x":1,"x":2}', '{"x":0.5}', '{"x":NaN}'):
            with self.subTest(text=text):
                with self.assertRaises(
                    replay.SymbolicNoEntryReplayError
                ):
                    replay.strict_json_loads(text)

    def test_q_pi_atom_is_strict_and_canonical(self) -> None:
        self.assertEqual(
            replay.parse_atom(
                {
                    "numerator": 3,
                    "denominator": 8,
                    "pi_exponent": -2,
                }
            ),
            (Fraction(3, 8), -2),
        )
        hostile_atoms = (
            {
                "numerator": 2,
                "denominator": 2,
                "pi_exponent": 0,
            },
            {
                "numerator": 0,
                "denominator": 1,
                "pi_exponent": 1,
            },
            {
                "numerator": True,
                "denominator": 1,
                "pi_exponent": 0,
            },
            {
                "numerator": 1,
                "denominator": 1,
                "pi_exponent": 17,
            },
        )
        for atom in hostile_atoms:
            with self.subTest(atom=atom):
                with self.assertRaises(
                    replay.SymbolicNoEntryReplayError
                ):
                    replay.parse_atom(atom)

    def test_dyadic_round_trip_and_noncanonical_rejection(self) -> None:
        for value in (
            Fraction(0),
            Fraction(1, 2),
            Fraction(-17, 64),
            Fraction((1 << 180) + 1, 1 << 120),
        ):
            self.assertEqual(
                replay.parse_dyadic(replay.dyadic_json(value)), value
            )
        for value in (
            {"numerator": 0, "exponent": 1},
            {"numerator": 2, "exponent": 1},
            {"numerator": True, "exponent": 0},
            {"numerator": 1, "exponent": -1},
        ):
            with self.subTest(value=value):
                with self.assertRaises(
                    replay.SymbolicNoEntryReplayError
                ):
                    replay.parse_dyadic(value)

    def test_boundary_equality_is_not_excluded(self) -> None:
        self.assertIsNone(
            replay.derive_empty_image_witness(
                axis=0,
                lower=Fraction(1, 2),
                upper=Fraction(1, 2),
            )
        )
        self.assertIsNone(
            replay.derive_empty_image_witness(
                axis=0,
                lower=Fraction(15, 2),
                upper=Fraction(15, 2),
            )
        )

    def test_strict_gap_and_negative_floor_ceil(self) -> None:
        self.assertEqual(replay.floor_fraction(Fraction(-3, 2)), -2)
        self.assertEqual(replay.ceil_fraction(Fraction(-3, 2)), -1)
        witness = replay.derive_empty_image_witness(
            axis=0,
            lower=Fraction(1, 2) + Fraction(1, 1 << 20),
            upper=Fraction(3, 4),
        )
        self.assertIsNotNone(witness)
        assert witness is not None
        self.assertGreater(witness["nmin"], witness["nmax"])
        self.assertGreater(
            replay.parse_dyadic(witness["margins"]["minimum"]), 0
        )

    def test_typed_unresolved_budget_semantics(self) -> None:
        depth_witness = {
            "witness_type": "unresolved",
            "reason": "maximum_depth_exhausted",
            "max_nodes": 4095,
            "max_depth": 48,
            "nodes_created_before_stop": 17,
            "reserved_nodes": 3,
            "next_action": "bisect_registered_box",
        }
        replay._validate_unresolved_witness(
            depth_witness,
            depth=48,
            nodes_created=17,
            reserved_nodes=3,
            max_nodes=4095,
            max_depth=48,
        )
        budget_witness = {
            "witness_type": "unresolved",
            "reason": "node_budget_exhausted",
            "max_nodes": 7,
            "max_depth": 48,
            "nodes_created_before_stop": 5,
            "reserved_nodes": 1,
            "next_action": "bisect_registered_box",
        }
        replay._validate_unresolved_witness(
            budget_witness,
            depth=3,
            nodes_created=5,
            reserved_nodes=1,
            max_nodes=7,
            max_depth=48,
        )
        hostile = copy.deepcopy(budget_witness)
        hostile["reserved_nodes"] = 0
        with self.assertRaises(replay.SymbolicNoEntryReplayError):
            replay._validate_unresolved_witness(
                hostile,
                depth=3,
                nodes_created=5,
                reserved_nodes=1,
                max_nodes=7,
                max_depth=48,
            )


class IndependentLiftAndEvaluatorControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.problem, cls.parsed, cls.lift = replay.replay_symbolic_lift()
        cls.certificate = load_certificate()

    def test_independent_lift_problem_and_registry_commitments(self) -> None:
        self.assertEqual(
            replay.semantic_sha256(self.problem),
            replay.CLOSED_STRING_PROBLEM_SHA256,
        )
        self.assertEqual(
            self.lift["lift_registry_semantic_sha256"],
            replay.LIFT_REGISTRY_SHA256,
        )
        self.assertEqual(
            replay.normalized_lf_sha256(replay.LIFT_REPLAYER_PATH),
            replay.LIFT_REPLAYER_NORMALIZED_LF_SHA256,
        )

    def test_problem_has_exact_integer_harmonic_seams(self) -> None:
        self.assertEqual(
            self.parsed["transverse_seam"],
            "integer harmonics make axes 0..7 exactly periodic mod one",
        )
        self.assertEqual(self.parsed["winding_seam_shifts"], [1, 1])
        for string in self.parsed["strings"]:
            for mode in string["modes"]:
                self.assertGreater(mode["mode_number"], 0)

    def test_independent_evaluator_rebuilds_first_leaf_exactly(self) -> None:
        leaf = first_leaf(self.certificate)
        witness, bounds = replay.derive_leaf_witness(
            self.problem,
            self.parsed,
            leaf["box"],
            replay.PRECISION_BITS,
        )
        self.assertEqual(len(bounds), 8)
        self.assertTrue(
            replay.type_strict_equal(
                witness, leaf["payload"]["witness"]
            )
        )

    def test_evaluator_returns_transverse_axes_only(self) -> None:
        values = replay.evaluate_transverse_d(
            self.problem,
            self.parsed,
            self.certificate["domain"],
            replay.PRECISION_BITS,
        )
        self.assertEqual(len(values), 8)

    def test_root_domain_is_problem_bound_and_half_open(self) -> None:
        expected = replay.expected_registered_domain(self.parsed)
        self.assertTrue(
            replay.type_strict_equal(
                expected, self.certificate["domain"]
            )
        )
        parsed = replay.parse_box(expected, "$.domain")
        self.assertEqual(parsed["u1"], (Fraction(0), Fraction(1)))
        self.assertEqual(parsed["u2"], (Fraction(0), Fraction(1)))
        self.assertEqual(parsed["t"], (self.parsed["t0"], self.parsed["t1"]))


class CompleteCertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.replayed = replay.replay_certificate_path()

    def test_all_commitments_and_topology_are_pinned(self) -> None:
        self.assertEqual(
            self.replayed["solver_registry_semantic_sha256"],
            EXPECTED_SOLVER_REGISTRY_SHA256,
        )
        self.assertEqual(
            self.replayed["certificate_semantic_sha256"],
            EXPECTED_CERTIFICATE_SHA256,
        )
        self.assertEqual(
            self.replayed["root_node_semantic_sha256"],
            EXPECTED_ROOT_SHA256,
        )
        self.assertEqual(self.replayed["node_count"], 259)
        self.assertEqual(self.replayed["split_nodes"], 129)
        self.assertEqual(self.replayed["excluded_leaves"], 130)
        self.assertEqual(self.replayed["unresolved_leaves"], 0)
        self.assertEqual(self.replayed["maximum_depth"], 9)
        self.assertEqual(
            self.replayed["transverse_axis_counts"],
            [14, 66, 12, 10, 4, 0, 0, 24],
        )

    def test_minimum_margin_is_strict(self) -> None:
        self.assertGreater(
            replay.parse_dyadic(
                self.replayed["minimum_strict_coordinate_margin"]
            ),
            0,
        )

    def test_scope_is_finite_quotient_safe_and_winding_free(self) -> None:
        self.assertEqual(
            self.replayed["outcome"], "right_censored_no_entry"
        )
        self.assertEqual(
            self.replayed["scope"],
            "registered_finite_closed_string_window_only",
        )
        self.assertIs(
            self.replayed["exact_worldsheet_quotient_claimed"], True
        )
        self.assertIs(self.replayed["all_time_no_entry_claimed"], False)
        self.assertIs(self.replayed["winding_axis_used"], False)
        self.assertIs(self.replayed["winding_image_used"], False)
        self.assertIs(self.replayed["winding_metric_used"], False)


class HostileCertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.baseline = load_certificate()

    def rejection_gate(
        self, mutator: Callable[[dict[str, Any]], None]
    ) -> str:
        hostile = copy.deepcopy(self.baseline)
        mutator(hostile)
        replay._reseal_certificate(hostile)
        with self.assertRaises(
            replay.SymbolicNoEntryReplayError
        ) as caught:
            replay.replay_certificate_objects(hostile)
        return caught.exception.gate

    def test_fabricated_interval_reaches_independent_leaf_gate(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            endpoint = first_leaf(value)["payload"]["witness"][
                "d_enclosure"
            ]["hi"]
            endpoint["numerator"] += 2

        self.assertEqual(self.rejection_gate(mutate), "leaf_witness")

    def test_gap_overlap_and_closure_reach_cover_gates(self) -> None:
        def gap(value: dict[str, Any]) -> None:
            interval = first_leaf(value)["box"]["intervals"][0]
            lower = replay.parse_dyadic(interval["lower"])
            upper = replay.parse_dyadic(interval["upper"])
            interval["upper"] = replay.dyadic_json((lower + upper) / 2)

        self.assertEqual(self.rejection_gate(gap), "tree_cover")
        self.assertEqual(
            self.rejection_gate(
                lambda value: first_leaf(value)["box"]["intervals"][
                    0
                ].__setitem__("upper_closed", True)
            ),
            "half_open_cover",
        )

    def test_split_axis_reaches_deterministic_split_gate(self) -> None:
        self.assertEqual(
            self.rejection_gate(
                lambda value: value["tree"]["nodes"][0][
                    "payload"
                ].__setitem__("split_axis", "u2")
            ),
            "split_rule",
        )

    def test_false_unresolved_reaches_fresh_exclusion_gate(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            first_leaf(value)["payload"]["witness"] = {
                "witness_type": "unresolved",
                "reason": "node_budget_exhausted",
                "max_nodes": 4095,
                "max_depth": 48,
                "nodes_created_before_stop": 1,
                "reserved_nodes": 0,
                "next_action": "bisect_registered_box",
            }

        self.assertEqual(self.rejection_gate(mutate), "false_unresolved")

    def test_outcome_and_scope_reach_outcome_gate(self) -> None:
        self.assertEqual(
            self.rejection_gate(
                lambda value: value["outcome"].__setitem__(
                    "type", "first_entry"
                )
            ),
            "outcome",
        )
        self.assertEqual(
            self.rejection_gate(
                lambda value: value["outcome"].__setitem__(
                    "scope", "all_time"
                )
            ),
            "outcome",
        )

    def test_full_rehashed_hostile_matrix_is_closed(self) -> None:
        controls = replay.hostile_controls()
        required = {
            "fabricated_interval_rejected",
            "deleted_leaf_rejected",
            "reordered_nodes_rejected",
            "reordered_leaf_rejected",
            "gap_or_overlap_rejected",
            "overlap_rejected",
            "closure_mutation_rejected",
            "split_mutation_rejected",
            "axis_mutation_rejected",
            "period_mutation_rejected",
            "radius_mutation_rejected",
            "problem_hash_mutation_rejected",
            "registry_mutation_rejected",
            "outcome_mutation_rejected",
            "scope_mutation_rejected",
            "false_unresolved_complete_rejected",
            "false_self_hash_rejected",
            "boundary_equality_not_excluded",
            "coefficient_mutation_lift_gate_rejected",
            "source_commitment_lift_gate_rejected",
            "seam_mutation_lift_gate_rejected",
            "metric_mutation_lift_gate_rejected",
        }
        self.assertTrue(required <= set(controls))
        self.assertTrue(all(controls.values()), controls)


class IndependenceAndReportControls(unittest.TestCase):
    def test_only_allowed_project_module_is_imported(self) -> None:
        tree = ast.parse(
            Path(replay.__file__).read_text(encoding="utf-8")
        )
        imported: set[str] = set()
        forbidden_calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
            elif isinstance(node, ast.Call):
                if (
                    isinstance(node.func, ast.Name)
                    and node.func.id in {"eval", "exec", "__import__"}
                ):
                    forbidden_calls.add(node.func.id)
                elif (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr
                    in {
                        "import_module",
                        "spec_from_file_location",
                        "module_from_spec",
                    }
                ):
                    forbidden_calls.add(node.func.attr)
        self.assertIn("symbolic_pi_lift_replayer", imported)
        self.assertFalse(
            imported & replay.FORBIDDEN_PROJECT_IMPORTS,
            imported & replay.FORBIDDEN_PROJECT_IMPORTS,
        )
        self.assertNotIn("importlib", imported)
        self.assertFalse(forbidden_calls)

    def test_stored_report_replays_exactly(self) -> None:
        commitments = replay.replay_certificate_path()
        stored = replay.strict_json_load(replay.REPORT_PATH)
        digest = replay.verify_report(stored, commitments)
        self.assertEqual(digest, stored["report_semantic_sha256"])
        self.assertEqual(stored["status"], "passed")
        self.assertTrue(all(stored["checks"].values()))
        self.assertTrue(all(stored["hostile_controls"].values()))
        self.assertEqual(
            stored["independent_boundary"]["only_project_import"],
            "symbolic_pi_lift_replayer",
        )
        windows = stored["validation_protocol"]["windows"]
        self.assertEqual(windows["registered_test_count"], 22)
        self.assertEqual(windows["required_test_result"], "OK")
        self.assertEqual(windows["required_check_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
