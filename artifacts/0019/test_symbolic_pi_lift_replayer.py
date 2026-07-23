#!/usr/bin/env python3
"""Hostile and replay tests for the independent symbolic-pi lift replayer."""

from __future__ import annotations

import ast
import copy
import unittest
from fractions import Fraction

import symbolic_pi_lift_replayer as replay


class StrictBoundaryTests(unittest.TestCase):
    def test_q_pi_atom_round_trip_and_products(self) -> None:
        value = replay.make_atom(Fraction(3, 5), -2)
        self.assertEqual(
            replay.parse_atom(value), (Fraction(3, 5), -2)
        )
        self.assertEqual(
            replay.multiply_atoms(
                replay.make_atom(Fraction(1, 2), -1),
                replay.make_atom(16, 1),
            ),
            replay.make_atom(8),
        )
        self.assertEqual(
            replay.atom_power(replay.make_atom(16, 1), 2),
            replay.make_atom(256, 2),
        )

    def test_noncanonical_atoms_are_rejected(self) -> None:
        bad = [
            {"numerator": True, "denominator": 1, "pi_exponent": 0},
            {"numerator": 1, "denominator": 0, "pi_exponent": 0},
            {"numerator": 2, "denominator": 2, "pi_exponent": 0},
            {"numerator": 0, "denominator": 2, "pi_exponent": 0},
            {"numerator": 0, "denominator": 1, "pi_exponent": 1},
            {"numerator": 1, "denominator": 1, "pi_exponent": 17},
            {
                "numerator": 1,
                "denominator": 1,
                "pi_exponent": 0,
                "extra": 0,
            },
        ]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(replay.SymbolicLiftReplayError):
                    replay.parse_atom(value)

    def test_strict_json_rejects_duplicates_floats_and_nonfinite(self) -> None:
        for text in (
            '{"x":1,"x":2}',
            '{"x":1.0}',
            '{"x":NaN}',
        ):
            with self.subTest(text=text):
                with self.assertRaises(replay.SymbolicLiftReplayError):
                    replay.strict_json_loads(text)


class IndependentRebuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.material = replay._independent_source_material()
        cls.expected = replay.rebuild_fixture(cls.material)
        cls.stored = replay.strict_json_load(replay.LIFT_FIXTURE_PATH)
        cls.commitments = replay.replay_fixture_objects(
            cls.stored, cls.material
        )

    def test_independent_source_and_lift_hashes(self) -> None:
        self.assertEqual(
            replay.semantic_sha256(self.material["exact_state"]),
            replay.SOURCE_EXACT_STATE_SHA256,
        )
        self.assertEqual(
            replay.semantic_sha256(self.material["encoded_state"]),
            replay.SOURCE_BINARY64_STATE_SHA256,
        )
        self.assertEqual(
            replay.semantic_sha256(self.expected["lift_registry"]),
            replay.LIFT_REGISTRY_SHA256,
        )
        self.assertEqual(
            replay.semantic_sha256(
                self.expected["closed_string_problem"]
            ),
            replay.CLOSED_STRING_PROBLEM_SHA256,
        )
        self.assertTrue(
            replay.type_strict_equal(self.expected, self.stored)
        )

    def test_exact_M_k_L_metric_H_and_seams(self) -> None:
        problem = self.expected["closed_string_problem"]
        geometry = replay._verify_exact_geometry(problem, self.material)
        self.assertEqual(geometry["L_star"], "16*pi")
        self.assertEqual(geometry["T_F_times_L_star"], "8")
        self.assertEqual(geometry["mode_frequency_rule"], "k_n=n/8")
        self.assertEqual(geometry["winding_metric"], "L_star^2")
        self.assertEqual(
            geometry["domain_metric"],
            "diag(L_star^2,L_star^2,1)",
        )
        self.assertEqual(
            geometry["seam_shifts"],
            {"u1_plus_1": 1, "u2_plus_1": 1, "corner": 2},
        )

    def test_time_window_is_same_dyadic_not_symbolic_period(self) -> None:
        problem = self.expected["closed_string_problem"]
        t0 = problem["observation"]["t0"]
        t1 = problem["observation"]["t1"]
        self.assertEqual(replay.parse_atom(t0), (Fraction(0), 0))
        self.assertEqual(replay.parse_atom(t1)[1], 0)
        self.assertNotEqual(t1, problem["exact_parameters"]["L_star"])
        self.assertFalse(problem["observation"]["time_is_quotient"])

    def test_every_source_coefficient_is_identity_transport(self) -> None:
        replay._verify_source_identity(
            self.expected["closed_string_problem"],
            self.material["exact_state"],
        )
        self.assertEqual(
            self.commitments["source_state_sha256"],
            replay.SOURCE_STATE_SHA256,
        )

    def test_legal_source_mutation_resealed_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.stored)
        atom = hostile["closed_string_problem"]["kinematics"][
            "strings"
        ][0]["modes"][0]["initial_x"][0]
        atom["numerator"] += 2
        replay._reseal_fixture(hostile)
        with self.assertRaises(replay.SymbolicLiftReplayError):
            replay.replay_fixture_objects(hostile, self.material)

    def test_changed_seam_and_metrics_resealed_are_rejected(self) -> None:
        mutations = []
        seam = copy.deepcopy(self.stored)
        seam["closed_string_problem"]["worldsheet"][
            "seam_image_actions"
        ]["u2_plus_1"]["n8_reindex_shift"] = -1
        mutations.append(seam)
        target_metric = copy.deepcopy(self.stored)
        target_metric["closed_string_problem"]["target_torus"][
            "metric_diagonal"
        ][8] = replay.make_atom(64, 2)
        mutations.append(target_metric)
        domain_metric = copy.deepcopy(self.stored)
        domain_metric["closed_string_problem"]["solver_geometry"][
            "domain_metric_diagonal"
        ][0] = replay.make_atom(1)
        mutations.append(domain_metric)
        for hostile in mutations:
            replay._reseal_fixture(hostile)
            with self.subTest():
                with self.assertRaises(replay.SymbolicLiftReplayError):
                    replay.replay_fixture_objects(hostile, self.material)

    def test_full_hostile_matrix_is_closed(self) -> None:
        controls = replay.hostile_controls()
        self.assertGreaterEqual(len(controls), 18)
        self.assertTrue(all(controls.values()), controls)


class IndependenceAndReportTests(unittest.TestCase):
    def test_forbidden_modules_and_dynamic_loading_are_absent(self) -> None:
        path = replay.ARTIFACT_DIR / "symbolic_pi_lift_replayer.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        forbidden_calls: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in {"eval", "exec", "__import__"}:
                        forbidden_calls.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr in {
                        "import_module",
                        "spec_from_file_location",
                        "module_from_spec",
                    }:
                        forbidden_calls.add(node.func.attr)
        forbidden_modules = {
            "symbolic_pi_lift",
            "symbolic_physical_arb_jets",
            "physical_no_entry_solver",
            "physical_no_entry_replayer",
            "certified_solver_core",
        }
        self.assertFalse(imported & forbidden_modules)
        self.assertIn("source_binding_replayer", imported)
        self.assertFalse(forbidden_calls)

    def test_stored_report_replays_exactly(self) -> None:
        commitments = replay.replay_fixture_path()
        stored = replay.strict_json_load(replay.REPORT_PATH)
        digest = replay.verify_report(stored, commitments)
        self.assertEqual(digest, stored["report_semantic_sha256"])
        self.assertEqual(stored["status"], "passed")
        self.assertTrue(all(stored["checks"].values()))
        self.assertTrue(all(stored["hostile_controls"].values()))


if __name__ == "__main__":
    unittest.main()
