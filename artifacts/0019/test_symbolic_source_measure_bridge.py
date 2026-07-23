#!/usr/bin/env python3
"""Tests for the symbolic-pi source-measure bridge."""

from __future__ import annotations

import copy
import sys
import unittest
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import symbolic_source_measure_bridge as bridge


class ScalarBoundaryTests(unittest.TestCase):
    def test_q_pi_zero_is_exact_binary64_transport(self) -> None:
        values = [
            0.0,
            -0.0,
            0.125,
            -3.75,
            float.fromhex("0x1.fffffffffffffp+10"),
        ]
        for value in values:
            with self.subTest(value=value.hex()):
                atom = bridge.q_pi_atom(Fraction.from_float(value))
                coefficient, exponent = bridge.parse_q_pi_atom(atom)
                self.assertEqual(exponent, 0)
                self.assertEqual(coefficient, Fraction.from_float(value))

    def test_noncanonical_atoms_and_strict_json_fail_closed(self) -> None:
        bad_atoms = [
            {"numerator": True, "denominator": 1, "pi_exponent": 0},
            {"numerator": 1, "denominator": 0, "pi_exponent": 0},
            {"numerator": 2, "denominator": 2, "pi_exponent": 0},
            {"numerator": 0, "denominator": 1, "pi_exponent": 1},
            {"numerator": 1, "denominator": 1},
            {
                "numerator": 1,
                "denominator": 1,
                "pi_exponent": 0,
                "extra": 1,
            },
        ]
        for atom in bad_atoms:
            with self.subTest(atom=atom):
                with self.assertRaises(bridge.MeasureBridgeError):
                    bridge.parse_q_pi_atom(atom)
        with self.assertRaises(bridge.MeasureBridgeError):
            bridge.strict_json_loads('{"x":1,"x":2}')
        with self.assertRaises(bridge.MeasureBridgeError):
            bridge.strict_json_loads('{"x":1.0}')


class SourceMeasureBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = bridge.build_report()

    def test_old_binary64_cell_hits_exact_invariants(self) -> None:
        cell = self.report["binary64_source_cell"]
        self.assertEqual(
            cell["M_equals_rounded_T_F_hat_times_L_hat"]["hex"],
            "0x1.0000000000000p+3",
        )
        self.assertEqual(
            cell["k_1_equals_rounded_2_pi_hat_over_L_hat"]["hex"],
            "0x1.0000000000000p-3",
        )
        self.assertEqual(cell["E_star"]["hex"], "0x1.0000000000000p+0")
        self.assertEqual(
            cell["M_equals_rounded_T_F_hat_times_L_hat"][
                "exact_dyadic"
            ],
            bridge.rational_record(8),
        )

    def test_new_exact_cell_preserves_derived_source_parameters(self) -> None:
        cell = self.report["exact_symbolic_source_cell"]
        self.assertEqual(
            bridge.parse_q_pi_atom(cell["T_F"]),
            (Fraction(1, 2), -1),
        )
        self.assertEqual(
            bridge.parse_q_pi_atom(cell["L_star"]),
            (Fraction(16), 1),
        )
        self.assertEqual(
            bridge.multiply_q_pi_atoms(cell["T_F"], cell["L_star"]),
            cell["M_equals_T_F_times_L_star"],
        )
        self.assertEqual(
            bridge.parse_q_pi_atom(cell["k_1"]),
            (Fraction(1, 8), 0),
        )
        self.assertEqual(cell["E_star"], bridge.rational_record(1))
        self.assertEqual(cell["orientations"], [1, -1])

    def test_registered_512_sequence_is_code_pinned(self) -> None:
        empirical = self.report["empirical_512_sequence"]
        self.assertEqual(empirical["sample_count"], 512)
        self.assertEqual(
            empirical["source_state_hash_sequence_sha256"],
            bridge.SOURCE_STATE_SEQUENCE_SHA256,
        )
        self.assertEqual(
            empirical["coefficient_payload_hash_sequence_sha256"],
            bridge.COEFFICIENT_HASH_SEQUENCE_SHA256,
        )
        self.assertEqual(
            empirical["symbolic_coefficient_transport_sequence_sha256"],
            bridge.SYMBOLIC_COEFFICIENT_SEQUENCE_SHA256,
        )
        self.assertTrue(
            empirical[
                "all_binary64_coefficients_exactly_round_trip_q_pi_zero"
            ]
        )
        self.assertFalse(empirical["source_states_redrawn"])
        self.assertEqual(
            (
                empirical["valid_count_annotation"],
                empirical["invalid_count_annotation"],
            ),
            (283, 229),
        )

    def test_fixed_index_2_compares_every_problem_transport_leaf(
        self,
    ) -> None:
        binding = self.report["fixed_index_2_binding"]
        self.assertEqual(binding["sample_index"], 2)
        self.assertEqual(
            binding["source_state_sha256"],
            bridge.SOURCE_INDEX_2_STATE_SHA256,
        )
        self.assertEqual(
            binding["complete_source_payload_float_leaf_count"], 109
        )
        self.assertEqual(
            binding["problem_carried_q_pi_zero_atom_leaf_count"], 98
        )
        self.assertEqual(
            binding["problem_transport_projection_semantic_sha256"],
            "deb44e6f85e643a3c286b0394379853f62c2dfa310f4ef3af8306adde17464df",
        )
        self.assertEqual(
            binding["complete_symbolic_source_payload_semantic_sha256"],
            "51448fad0fc225952b1016ab73e06a0b3cbec2510d7ccd14a9e771eef7713db0",
        )
        self.assertTrue(
            binding["all_problem_carried_leaves_type_strict_equal"]
        )
        self.assertTrue(
            binding[
                "all_complete_source_payload_leaves_exactly_round_trip"
            ]
        )

    def test_resealed_problem_coefficient_mutation_still_fails_direct_binding(
        self,
    ) -> None:
        source, registry, fixture = bridge._load_inputs()
        state = source.sample_source(registry, 2)
        hostile = copy.deepcopy(fixture)
        hostile["closed_string_problem"]["kinematics"]["strings"][0][
            "modes"
        ][0]["initial_x"][0]["numerator"] += 1
        hostile["closed_string_problem_semantic_sha256"] = (
            bridge.semantic_sha256(hostile["closed_string_problem"])
        )
        # Reseal every available outer semantic commitment.
        bridge.semantic_sha256(hostile)
        with self.assertRaises(bridge.MeasureBridgeError):
            bridge._fixed_index_2_binding(state, hostile)
        self.assertTrue(
            self.report["fixed_index_2_binding"][
                "resealed_problem_coefficient_mutation_rejected"
            ]
        )

    def test_analytic_source_law_ratio_is_exactly_one(self) -> None:
        law = self.report["analytic_source_law"]
        self.assertEqual(
            law["radial_factor"]["dirichlet_shape"], [4, 15, 15]
        )
        self.assertEqual(
            law["radial_factor"]["simplex_scale_E_star"],
            bridge.rational_record(1),
        )
        jacobian = law["linear_chiral_factor"]
        self.assertEqual(
            jacobian["old_exact_value"],
            bridge.rational_record(2**140),
        )
        self.assertEqual(
            jacobian["new_exact_value"],
            bridge.rational_record(2**140),
        )
        self.assertEqual(
            jacobian["new_over_old"], bridge.rational_record(1)
        )
        self.assertEqual(
            law["latent_random_variable_transport"]["jacobian"],
            bridge.rational_record(1),
        )
        self.assertEqual(
            law["coefficient_transport"]["jacobian"],
            bridge.rational_record(1),
        )
        self.assertEqual(
            law["analytic_radon_nikodym_derivative_new_over_old"],
            bridge.rational_record(1),
        )

    def test_empirical_and_analytic_claims_are_not_conflated(self) -> None:
        empirical = self.report["empirical_512_sequence"]
        analytic = self.report["analytic_source_law"]
        self.assertIn("finite registered sequence", empirical["claim"])
        self.assertIn("analytic Brief 0018", analytic["statement"])
        excluded = set(self.report["scope"]["does_not_claim"])
        self.assertIn("unchanged event pushforward", excluded)
        self.assertIn("physical first-entry mass", excluded)
        self.assertIn("population event law", excluded)
        self.assertIn("3+1 selection", excluded)

    def test_mutated_report_is_rejected_even_with_rehashed_self_digest(
        self,
    ) -> None:
        hostile = copy.deepcopy(self.report)
        hostile["analytic_source_law"]["coefficient_transport"][
            "jacobian"
        ] = bridge.rational_record(2)
        payload = {
            key: value
            for key, value in hostile.items()
            if key != "report_semantic_sha256"
        }
        hostile["report_semantic_sha256"] = bridge.semantic_sha256(payload)
        with self.assertRaises(bridge.MeasureBridgeError):
            bridge.verify_report(hostile)

    def test_report_hash_and_all_named_controls_replay(self) -> None:
        self.assertEqual(
            self.report["report_semantic_sha256"],
            bridge.REPORT_SEMANTIC_SHA256,
        )
        self.assertTrue(all(self.report["checks"].values()))
        self.assertTrue(all(self.report["hostile_controls"].values()))


if __name__ == "__main__":
    unittest.main()
