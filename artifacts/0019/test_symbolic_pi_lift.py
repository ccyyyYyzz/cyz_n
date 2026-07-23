#!/usr/bin/env python3
from __future__ import annotations

import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import symbolic_pi_lift as lift


class SymbolicAtomTests(unittest.TestCase):
    def test_canonical_atoms_and_exact_products(self) -> None:
        atom = lift.symbolic_atom(
            Fraction(3, 5), pi_exponent=-2
        )
        self.assertEqual(
            lift.parse_symbolic_atom(atom),
            (Fraction(3, 5), -2),
        )
        self.assertEqual(
            lift.atom_multiply(
                lift.symbolic_atom(1, 2, -1),
                lift.symbolic_atom(16, pi_exponent=1),
            ),
            lift.symbolic_atom(8),
        )
        self.assertEqual(
            lift.atom_power(
                lift.symbolic_atom(16, pi_exponent=1), 2
            ),
            lift.symbolic_atom(256, pi_exponent=2),
        )
        self.assertEqual(
            lift.symbolic_atom(0, pi_exponent=7),
            lift.symbolic_atom(0),
        )

    def test_noncanonical_atoms_are_rejected(self) -> None:
        bad = [
            {"numerator": True, "denominator": 1, "pi_exponent": 0},
            {"numerator": 1, "denominator": 0, "pi_exponent": 0},
            {"numerator": 2, "denominator": 2, "pi_exponent": 0},
            {"numerator": 0, "denominator": 2, "pi_exponent": 0},
            {"numerator": 0, "denominator": 1, "pi_exponent": 1},
            {
                "numerator": 1,
                "denominator": 1,
                "pi_exponent": lift.PI_EXPONENT_MAX + 1,
            },
            {
                "numerator": 1,
                "denominator": 1,
                "pi_exponent": 0,
                "extra": 0,
            },
        ]
        for value in bad:
            with self.subTest(value=value):
                with self.assertRaises(lift.LiftError):
                    lift.parse_symbolic_atom(value)
        with self.assertRaises(lift.LiftError):
            lift.parse_symbolic_atom(
                {"numerator": 1.0, "denominator": 1, "pi_exponent": 0}
            )

    def test_strict_json_rejects_duplicates_floats_and_bool(self) -> None:
        with self.assertRaises(lift.LiftError):
            lift.strict_json_loads('{"x":1,"x":2}')
        with self.assertRaises(lift.LiftError):
            lift.strict_json_loads('{"x":1.0}')
        with self.assertRaises(lift.LiftError):
            lift.parse_symbolic_atom(
                {"numerator": 1, "denominator": 1, "pi_exponent": False}
            )


class SymbolicLiftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.upstream = lift.load_upstream_fixture()
        cls.fixture = lift.build_fixture()
        cls.registry = cls.fixture["lift_registry"]
        cls.problem = cls.fixture["closed_string_problem"]

    def test_exact_relations_and_distinct_problem_identity(self) -> None:
        exact = self.problem["exact_parameters"]
        self.assertEqual(
            lift.atom_multiply(exact["T_F"], exact["L_star"]),
            exact["M"],
        )
        self.assertEqual(exact["K"], 1)
        for string in self.problem["kinematics"]["strings"]:
            for mode in string["modes"]:
                harmonic = mode["mode_number"]
                self.assertEqual(
                    lift.atom_multiply(
                        mode["temporal_angular_frequency"],
                        exact["L_star"],
                    ),
                    lift.symbolic_atom(
                        2 * harmonic, pi_exponent=1
                    ),
                )
        self.assertNotEqual(
            self.fixture["closed_string_problem_semantic_sha256"],
            lift.LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertNotIn(
            lift.LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256,
            lift.canonical_bytes(self.problem).decode("utf-8"),
        )
        self.assertEqual(
            self.registry["upstream_provenance"][
                "legacy_cut_open_physical_problem_semantic_sha256"
            ],
            lift.LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256,
        )

    def test_source_coefficients_and_time_window_are_identity_bound(self) -> None:
        old = self.upstream["physical_problem"]
        self.assertEqual(
            self.problem["source_commitment"]["source_state_sha256"],
            lift.SOURCE_STATE_SHA256,
        )
        self.assertEqual(
            self.problem["observation"]["t0"],
            lift.dyadic_to_atom(old["observation"]["t0"]),
        )
        self.assertEqual(
            self.problem["observation"]["t1"],
            lift.dyadic_to_atom(old["observation"]["t1"]),
        )
        self.assertNotEqual(
            self.problem["observation"]["t1"],
            self.problem["exact_parameters"]["L_star"],
        )
        for string_index in range(2):
            old_mode = old["kinematics"]["strings"][string_index]["modes"][0]
            new_mode = self.problem["kinematics"]["strings"][string_index][
                "modes"
            ][0]
            for field in ("initial_x", "initial_y", "initial_p", "initial_q"):
                self.assertEqual(
                    new_mode[field],
                    [
                        lift.dyadic_to_atom(value)
                        for value in old_mode[field]
                    ],
                )

    def test_target_domain_metrics_and_exact_seams(self) -> None:
        L_squared = lift.symbolic_atom(256, pi_exponent=2)
        self.assertEqual(
            self.problem["target_torus"]["metric_diagonal"],
            [lift.symbolic_atom(1) for _ in range(8)] + [L_squared],
        )
        self.assertEqual(
            self.problem["solver_geometry"]["domain_metric_diagonal"],
            [L_squared, L_squared, lift.symbolic_atom(1)],
        )
        self.assertEqual(
            self.problem["solver_geometry"][
                "physical_singular_value_formula"
            ],
            "G^(1/2)*J*H^(-1/2)",
        )
        self.assertEqual(
            lift.verify_exact_seam_algebra(self.problem),
            {"a1": 1, "a2": 1, "corner": 2},
        )
        actions = self.problem["worldsheet"]["seam_image_actions"]
        self.assertEqual(actions["u1_plus_1"]["n8_reindex_shift"], 1)
        self.assertEqual(actions["u2_plus_1"]["n8_reindex_shift"], 1)
        self.assertEqual(
            actions["corner_plus_1_plus_1"]["n8_reindex_shift"], 2
        )
        self.assertEqual(
            self.problem["worldsheet"]["upper_to_lower_reindex_rule"],
            "n_lower=n_upper-a_i*e_w",
        )

    def test_fixture_replay_and_hostile_controls(self) -> None:
        replay = lift.verify_fixture(self.fixture)
        self.assertEqual(replay["seam_actions"], {"a1": 1, "a2": 1, "corner": 2})
        self.assertTrue(all(lift._hostile_checks(self.fixture).values()))

        mutations = []
        metric = copy.deepcopy(self.fixture)
        metric["closed_string_problem"]["target_torus"][
            "metric_diagonal"
        ][8] = lift.symbolic_atom(256, pi_exponent=1)
        mutations.append(metric)

        domain_metric = copy.deepcopy(self.fixture)
        domain_metric["closed_string_problem"]["solver_geometry"][
            "domain_metric_diagonal"
        ][0] = lift.symbolic_atom(1)
        mutations.append(domain_metric)

        seam = copy.deepcopy(self.fixture)
        seam["closed_string_problem"]["worldsheet"][
            "seam_image_actions"
        ]["u2_plus_1"]["n8_reindex_shift"] = -1
        mutations.append(seam)

        time = copy.deepcopy(self.fixture)
        time["closed_string_problem"]["observation"]["t1"] = (
            lift.symbolic_atom(16, pi_exponent=1)
        )
        mutations.append(time)

        coefficient = copy.deepcopy(self.fixture)
        coefficient["closed_string_problem"]["kinematics"]["strings"][0][
            "modes"
        ][0]["initial_x"][0]["numerator"] += 1
        mutations.append(coefficient)

        for hostile in mutations:
            hostile["closed_string_problem_semantic_sha256"] = (
                lift.semantic_sha256(hostile["closed_string_problem"])
            )
            with self.subTest():
                with self.assertRaises(lift.LiftError):
                    lift.verify_fixture(hostile)

    def test_scope_withholds_downstream_claims(self) -> None:
        problem_scope = set(self.problem["scope"]["does_not_claim"])
        registry_scope = set(self.registry["scope"]["does_not_claim"])
        self.assertIn(
            "entry or no-entry over the registered window",
            problem_scope,
        )
        self.assertIn("population law", problem_scope)
        self.assertIn("3+1 selection", problem_scope)
        self.assertIn("worldsheet entry or no-entry", registry_scope)
        self.assertIn("population law", registry_scope)


if __name__ == "__main__":
    unittest.main()
