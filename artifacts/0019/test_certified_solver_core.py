#!/usr/bin/env python3
"""Hostile and positive tests for the Brief 0019 exact foundation."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import certified_solver_core as core


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_json_key_is_rejected(self) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.strict_json_loads('{"x":1,"x":2}')
        self.assertEqual(caught.exception.gate, "strict_json")

    def test_nonfinite_json_tokens_are_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(core.CertificateError) as caught:
                    core.strict_json_loads('{"x":' + token + "}")
                self.assertEqual(caught.exception.gate, "strict_json")

    def test_ordinary_json_float_is_rejected(self) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.strict_json_loads('{"x":0.125}')
        self.assertEqual(caught.exception.gate, "strict_json")

    def test_boolean_is_not_an_integer(self) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.Dyadic.from_json({"numerator": True, "exponent": 0})
        self.assertEqual(caught.exception.gate, "dyadic")

    def test_type_strict_equality_distinguishes_true_and_one(self) -> None:
        self.assertFalse(core.type_strict_equal({"x": True}, {"x": 1}))

    def test_lf_and_crlf_parse_to_one_semantic_hash(self) -> None:
        value = {"a": [1, True], "b": "dyadic"}
        lf = core.pretty_json(value)
        crlf = lf.replace("\n", "\r\n")
        parsed_lf = core.strict_json_loads(lf)
        parsed_crlf = core.strict_json_loads(crlf)
        self.assertTrue(core.type_strict_equal(parsed_lf, parsed_crlf))
        self.assertEqual(
            core.canonical_sha256(parsed_lf),
            core.canonical_sha256(parsed_crlf),
        )


class ExactArithmeticTests(unittest.TestCase):
    def test_dyadic_is_reduced_canonically(self) -> None:
        self.assertEqual(core.Dyadic.of(6, 2), core.Dyadic.of(3, 1))
        self.assertEqual(core.Dyadic.of(0, 30), core.ZERO)
        with self.assertRaises(core.CertificateError):
            core.Dyadic.from_json({"numerator": 2, "exponent": 1})

    def test_exact_dyadic_arithmetic(self) -> None:
        quarter = core.Dyadic.of(1, 2)
        three_eighths = core.Dyadic.of(3, 3)
        self.assertEqual(
            (quarter + three_eighths).to_fraction(), Fraction(5, 8)
        )
        self.assertEqual(
            (three_eighths - quarter).to_fraction(), Fraction(1, 8)
        )
        self.assertEqual(
            (quarter * three_eighths).to_fraction(), Fraction(3, 32)
        )
        self.assertEqual(
            (quarter / core.Dyadic.of(2)).to_fraction(), Fraction(1, 8)
        )

    def test_non_dyadic_quotient_is_not_silently_rounded(self) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            _ = core.ONE / core.Dyadic.of(3)
        self.assertEqual(caught.exception.gate, "dyadic")

    def test_half_open_split_is_disjoint_and_gap_free(self) -> None:
        parent = core.DyadicInterval(
            core.ZERO, core.ONE, True, False
        )
        point = core.Dyadic.of(1, 1)
        left, right = parent.split(point)
        self.assertEqual(left.lower, parent.lower)
        self.assertEqual(right.upper, parent.upper)
        self.assertEqual(left.upper, right.lower)
        self.assertFalse(left.upper_closed)
        self.assertTrue(right.lower_closed)
        self.assertTrue(left.lower_closed)
        self.assertFalse(right.upper_closed)

    def test_box_split_changes_only_declared_axis(self) -> None:
        x = core.DyadicInterval(core.ZERO, core.ONE, True, False)
        y = core.DyadicInterval(core.Dyadic.of(-1), core.ONE, True, True)
        box = core.DyadicBox(("x", "y"), (x, y))
        left, right = box.split("x", core.Dyadic.of(1, 1))
        self.assertEqual(left.intervals[1], y)
        self.assertEqual(right.intervals[1], y)
        self.assertEqual(left.intervals[0].upper, right.intervals[0].lower)

    def test_degenerate_open_interval_is_rejected(self) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.DyadicInterval(
                core.ONE, core.ONE, lower_closed=True, upper_closed=False
            )
        self.assertEqual(caught.exception.gate, "interval")


class ImageEnumerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = core.build_foundation_fixture()

    def test_nonunit_metric_fixture_enumerates_all_six_images(self) -> None:
        image_data = self.fixture["image_enumeration"]
        self.assertNotEqual(
            image_data["metric_diagonal"],
            [core.ONE.to_json(), core.ONE.to_json()],
        )
        identifiers = core.validate_image_enumeration(image_data)
        self.assertEqual(
            identifiers,
            [
                "n[0,0]",
                "n[0,1]",
                "n[1,0]",
                "n[1,1]",
                "n[2,0]",
                "n[2,1]",
            ],
        )

    def test_missing_image_fails_enumeration_gate(self) -> None:
        mutation = copy.deepcopy(self.fixture["image_enumeration"])
        mutation["manifest"].pop(2)
        with self.assertRaises(core.CertificateError) as caught:
            core.validate_image_enumeration(mutation)
        self.assertEqual(caught.exception.gate, "image_enumeration")

    def test_duplicate_image_id_fails_identity_gate(self) -> None:
        mutation = copy.deepcopy(self.fixture["image_enumeration"])
        mutation["manifest"][1]["image_id"] = mutation["manifest"][0][
            "image_id"
        ]
        with self.assertRaises(core.CertificateError) as caught:
            core.validate_image_enumeration(mutation)
        self.assertEqual(caught.exception.gate, "image_manifest_ids")

    def test_inexact_metric_inverse_witness_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture["image_enumeration"])
        mutation["metric_inverse_diagonal"][0] = core.ONE.to_json()
        with self.assertRaises(core.CertificateError) as caught:
            core.validate_image_enumeration(mutation)
        self.assertEqual(caught.exception.gate, "image_enumeration")


class CoverReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = core.build_foundation_fixture()

    def assert_gate(
        self, mutation: dict[str, object], expected_gate: str
    ) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.replay_bundle(mutation)
        self.assertEqual(caught.exception.gate, expected_gate)

    def test_valid_forest_replays_derived_counts(self) -> None:
        result = core.replay_bundle(self.fixture)
        self.assertEqual(result["image_count"], 6)
        self.assertEqual(result["root_count"], 6)
        self.assertEqual(result["node_count"], 10)
        self.assertEqual(result["leaf_count"], 8)
        self.assertEqual(
            result["status_counts"],
            {"excluded_range": 6, "unique_root": 1, "unresolved": 1},
        )
        self.assertEqual(result["coverage"], "gap_free_exact_partition")
        self.assertEqual(result["resolution"], "unresolved_present")

    def test_every_manifest_image_has_exactly_one_cover_root(self) -> None:
        image_ids = [
            item["image_id"]
            for item in self.fixture["image_enumeration"]["manifest"]
        ]
        roots = self.fixture["initial_cover"]["root_ids"]
        nodes = {
            node["node_id"]: node
            for node in self.fixture["initial_cover"]["nodes"]
        }
        self.assertEqual([nodes[root]["image_id"] for root in roots], image_ids)

    def test_deleted_leaf_fails_topology_after_cover_hash_refresh(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["initial_cover"]["nodes"] = [
            node
            for node in mutation["initial_cover"]["nodes"]
            if node["node_id"] != "leaf-0-0-unique"
        ]
        mutation["initial_cover"]["cover_hash"] = core._cover_hash(
            mutation["initial_cover"]
        )
        self.assertEqual(
            mutation["initial_cover"]["cover_hash"],
            core._cover_hash(mutation["initial_cover"]),
        )
        self.assert_gate(mutation, "cover_topology")

    def test_wrong_split_fails_partition_after_all_hashes_refresh(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        core._find_node(mutation, "root-0-0")[
            "split_point"
        ] = core.Dyadic.of(1, 3).to_json()
        mutation = core.refresh_declared_hashes(mutation)
        self.assertEqual(
            mutation["initial_cover"]["cover_hash"],
            core._cover_hash(mutation["initial_cover"]),
        )
        self.assert_gate(mutation, "cover_partition")

    def test_overlapping_child_box_fails_exact_partition(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        leaf = core._find_node(mutation, "leaf-0-0-excluded")
        leaf["box"]["intervals"][0]["upper"] = core.Dyadic.of(
            3, 2
        ).to_json()
        mutation = core.refresh_declared_hashes(mutation)
        self.assert_gate(mutation, "cover_partition")

    def test_duplicate_node_id_fails_before_dictionary_collapse(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["initial_cover"]["nodes"].append(
            copy.deepcopy(
                core._find_node(mutation, "leaf-0-0-excluded")
            )
        )
        mutation["initial_cover"]["cover_hash"] = core._cover_hash(
            mutation["initial_cover"]
        )
        self.assert_gate(mutation, "cover_ids")

    def test_empty_complete_cover_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["initial_cover"]["root_ids"] = []
        mutation["initial_cover"]["root_hashes"] = []
        mutation["initial_cover"]["nodes"] = []
        mutation["initial_cover"]["cover_hash"] = core._cover_hash(
            mutation["initial_cover"]
        )
        self.assert_gate(mutation, "cover_topology")

    def test_unreferenced_manifest_image_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["initial_cover"]["root_ids"].pop()
        mutation["initial_cover"]["root_hashes"].pop()
        removed_root = "root-2-1"
        mutation["initial_cover"]["nodes"] = [
            node
            for node in mutation["initial_cover"]["nodes"]
            if node["node_id"] != removed_root
        ]
        mutation["initial_cover"]["cover_hash"] = core._cover_hash(
            mutation["initial_cover"]
        )
        self.assert_gate(mutation, "cover_image_binding")


class WitnessReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = core.build_foundation_fixture()

    def assert_gate(
        self, mutation: dict[str, object], expected_gate: str
    ) -> None:
        with self.assertRaises(core.CertificateError) as caught:
            core.replay_bundle(mutation)
        self.assertEqual(caught.exception.gate, expected_gate)

    def test_unique_witness_contains_replay_data_not_success_boolean(self) -> None:
        node = core._find_node(self.fixture, "leaf-0-0-unique")
        witness = node["witness"]
        self.assertNotIn("success", witness)
        self.assertNotIn("included", witness)
        self.assertEqual(
            core.Dyadic.from_json(witness["midpoint"]),
            core.Dyadic.of(1, 1),
        )
        image = core.DyadicInterval.from_json(witness["krawczyk_image"])
        self.assertEqual(image.lower, core.Dyadic.of(1, 1))
        self.assertEqual(image.upper, core.Dyadic.of(1, 1))
        self.assertEqual(
            core.Dyadic.from_json(witness["inclusion_margins"]["lower"]),
            core.Dyadic.of(1, 2),
        )
        self.assertEqual(
            core.Dyadic.from_json(witness["inclusion_margins"]["upper"]),
            core.Dyadic.of(1, 2),
        )

    def test_fake_krawczyk_image_fails_after_hash_refresh(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        node = core._find_node(mutation, "leaf-0-0-unique")
        node["witness"]["krawczyk_image"] = core.DyadicInterval.closed(
            core.Dyadic.of(3, 3), core.Dyadic.of(5, 3)
        ).to_json()
        mutation = core.refresh_declared_hashes(mutation)
        self.assert_gate(mutation, "unique_root_witness")

    def test_false_range_exclusion_fails_after_hash_refresh(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        node = core._find_node(mutation, "leaf-0-0-excluded")
        node["witness"]["range"] = core.DyadicInterval.closed(
            core.Dyadic.of(-1), core.ONE
        ).to_json()
        mutation = core.refresh_declared_hashes(mutation)
        self.assert_gate(mutation, "excluded_range_witness")

    def test_unresolved_leaf_is_retained_and_not_hidden(self) -> None:
        node = core._find_node(self.fixture, "leaf-0-0-unresolved")
        self.assertEqual(node["status"], "unresolved")
        result = core.replay_bundle(self.fixture)
        self.assertEqual(result["resolution"], "unresolved_present")
        self.assertEqual(result["status_counts"]["unresolved"], 1)

    def test_fake_budget_exhaustion_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        node = core._find_node(mutation, "leaf-0-0-unresolved")
        node["witness"]["operations_used"] = 63
        mutation = core.refresh_declared_hashes(mutation)
        self.assert_gate(mutation, "unresolved_witness")

    def test_duplicate_function_id_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["function_registry"]["functions"].append(
            copy.deepcopy(mutation["function_registry"]["functions"][0])
        )
        self.assert_gate(mutation, "problem_commitment")


class StoredArtifactTests(unittest.TestCase):
    def test_hostile_suite_hits_each_intended_gate(self) -> None:
        fixture = core.build_foundation_fixture()
        outcomes = core.run_hostile_controls(fixture)
        self.assertEqual(len(outcomes), 6)
        self.assertTrue(
            all(item["result"] == "rejected_as_intended" for item in outcomes)
        )

    def test_fixture_has_no_ordinary_float_anywhere(self) -> None:
        fixture = core.build_foundation_fixture()
        core.assert_strict_json_tree(fixture)

        def walk(value: object) -> None:
            self.assertIsNot(type(value), float)
            if type(value) is list:
                for item in value:
                    walk(item)
            elif type(value) is dict:
                for item in value.values():
                    walk(item)

        walk(fixture)

    def test_pretty_json_round_trip_is_type_strict(self) -> None:
        fixture = core.build_foundation_fixture()
        replayed = core.strict_json_loads(core.pretty_json(fixture))
        self.assertTrue(core.type_strict_equal(fixture, replayed))

    def test_normalized_lf_inventory_ignores_checkout_newlines(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "sample.txt"
            path.write_bytes(b"a\r\nb\r\n")
            first = core.normalized_lf_sha256(path)
            path.write_bytes(b"a\nb\n")
            second = core.normalized_lf_sha256(path)
        self.assertEqual(first, second)

    def test_stored_artifacts_match_deterministic_replay(self) -> None:
        self.assertTrue(core.FIXTURE_PATH.is_file())
        self.assertTrue(core.REPORT_PATH.is_file())
        result = core.check_artifacts()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["resolution"], "unresolved_present")


if __name__ == "__main__":
    unittest.main(verbosity=2)
