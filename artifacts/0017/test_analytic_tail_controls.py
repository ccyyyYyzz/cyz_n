#!/usr/bin/env python3
"""Standard-library regression tests for Brief 0017 analytic controls."""

from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import analytic_tail_controls as controls


EXPECTED_CANONICAL_SHA256 = (
    "7c6120573e17b0e8fa4c8a9d036bd213fbc8354376d3ae623241716012aebc22"
)


class WishartTailTests(unittest.TestCase):
    def test_exact_declared_constants(self) -> None:
        self.assertAlmostEqual(
            controls.FIXED_POINT_CONSTANT,
            math.sqrt(math.pi / 2.0) / 48.0,
            places=16,
        )
        self.assertEqual(controls.VOLUME_PALM_CONSTANT, 1.0 / 105.0)
        self.assertAlmostEqual(
            controls.expected_standard_pair_volume(),
            7.0,
            places=14,
        )
        self.assertAlmostEqual(
            controls.fixed_point_constant_from_density_leading_term(),
            controls.FIXED_POINT_CONSTANT,
            places=15,
        )
        self.assertAlmostEqual(
            controls.volume_palm_constant_from_density_leading_term(),
            controls.VOLUME_PALM_CONSTANT,
            places=15,
        )

    def test_fixed_point_hard_edge_constant_and_exponents(self) -> None:
        tail = controls.build_wishart_tail_controls()
        final = tail["rows"][-1]
        self.assertLess(
            abs(
                float(final["fixed_point_ratio_cdf_over_epsilon7"])
                / controls.FIXED_POINT_CONSTANT
                - 1.0
            ),
            0.003,
        )
        self.assertLess(
            abs(
                float(final["fixed_point_local_singular_exponent"])
                - 7.0
            ),
            0.01,
        )
        self.assertLess(
            abs(float(final["fixed_point_local_gram_exponent"]) - 3.5),
            0.005,
        )

    def test_volume_palm_constant_and_exponent(self) -> None:
        tail = controls.build_wishart_tail_controls()
        final = tail["rows"][-1]
        self.assertLess(
            abs(
                float(final["volume_palm_ratio_cdf_over_epsilon8"])
                / controls.VOLUME_PALM_CONSTANT
                - 1.0
            ),
            0.003,
        )
        self.assertLess(
            abs(
                float(final["volume_palm_local_singular_exponent"])
                - 8.0
            ),
            0.01,
        )

    def test_reference_quadrature_values(self) -> None:
        self.assertAlmostEqual(
            controls.fixed_point_cdf(0.0625),
            9.7080184076331e-11,
            delta=2.0e-24,
        )
        self.assertAlmostEqual(
            controls.volume_palm_cdf(0.0625),
            2.213108000983e-12,
            delta=1.0e-25,
        )


class EventGeometryTests(unittest.TestCase):
    def test_affine_closest_complete_weight_is_linear(self) -> None:
        affine = controls.build_affine_closest_controls()
        self.assertTrue(all(affine["checks"].values()))
        final = affine["rows"][-1]
        self.assertAlmostEqual(
            float(final["hessian_over_delta_squared"]),
            1.0,
            places=14,
        )
        self.assertAlmostEqual(
            float(final["constraint_density_times_delta"]),
            1.0,
            places=14,
        )
        self.assertAlmostEqual(
            float(final["effective_scale_over_delta"]),
            1.0,
            places=14,
        )

    def test_curvature_lifted_conditional_counterexample(self) -> None:
        curved = controls.build_curvature_lifted_controls()
        self.assertTrue(all(curved["checks"].values()))
        final = curved["rows"][-1]
        radius = float(curved["impact_radius_r"])
        self.assertAlmostEqual(
            float(final["morse_hessian_determinant"]),
            radius,
            delta=2.0e-9,
        )
        self.assertAlmostEqual(
            float(final["effective_scale_times_delta"]),
            radius,
            delta=2.0e-9,
        )
        self.assertTrue(curved["not_a_first_entry_claim"])
        self.assertTrue(curved["not_a_global_closest_selection_claim"])

    def test_hessian_and_constraint_density_are_derived_from_jets(self) -> None:
        e1 = (1.0, 0.0, 0.0, 0.0)
        e2 = (0.0, 1.0, 0.0, 0.0)
        delta_e3 = (0.0, 0.0, 0.2, 0.0)
        e4 = (0.0, 0.0, 0.0, 1.0)
        zero = (0.0, 0.0, 0.0, 0.0)
        jacobian = (e1, e2, delta_e3)
        separation = tuple(0.25 * value for value in e4)

        affine_hessian = controls.squared_distance_hessian(
            jacobian,
            separation,
            controls.zero_second_derivatives(3, 4),
        )
        curved_second_jet = (
            (zero, zero, zero),
            (zero, zero, zero),
            (zero, zero, e4),
        )
        curved_hessian = controls.squared_distance_hessian(
            jacobian,
            separation,
            curved_second_jet,
        )

        self.assertAlmostEqual(
            controls.matrix_determinant_3(affine_hessian),
            0.2**2,
            places=14,
        )
        self.assertAlmostEqual(
            controls.matrix_determinant_3(curved_hessian),
            0.2**2 + 0.25,
            places=14,
        )
        self.assertAlmostEqual(
            controls.normalised_gaussian_constraint_zero_density(jacobian),
            1.0 / 0.2,
            places=14,
        )

    def test_opposite_winding_rank_identity(self) -> None:
        identity = controls.build_opposite_winding_identity_controls()
        self.assertTrue(all(identity["checks"].values()))
        generic = identity["controls"][0]
        collinear = identity["controls"][1]
        straight = identity["controls"][2]
        excited_q_zero = identity["controls"][3]
        self.assertEqual(generic["pair_rank"], 2)
        self.assertEqual(generic["encounter_rank"], 3)
        self.assertEqual(collinear["pair_rank"], 1)
        self.assertEqual(collinear["encounter_rank"], 2)
        self.assertEqual(straight["encounter_rank"], 2)
        self.assertTrue(all(value == "0" for value in straight["p1"]))
        self.assertTrue(all(value == "0" for value in straight["p2"]))
        self.assertEqual(excited_q_zero["encounter_rank"], 2)
        self.assertTrue(
            all(
                value == "0"
                for value in excited_q_zero["q_equals_p1_plus_p2"]
            )
        )
        near_rows = identity["near_degenerate_exact_rank3_sequence"]["rows"]
        self.assertTrue(
            all(
                row["exact_encounter_rank_from_positive_minor"] == 3
                for row in near_rows
            )
        )

    def test_first_entry_and_closest_bundle_coordinates_differ(self) -> None:
        projection = controls.build_event_bundle_projection_controls()
        self.assertTrue(all(projection["checks"].values()))
        first = projection["first_entry"]
        closest = projection["closest_approach"]
        self.assertEqual(projection["event_jacobian_rank"], 3)
        self.assertEqual(float(first["entry_radius_squared"]), 13.0)
        self.assertTrue(
            first["boundary_equation_F_equals_r_squared_over_2"]
        )
        self.assertTrue(first["s_is_stationary_in_material_coordinates"])
        self.assertTrue(first["spatial_hessian_is_positive_definite"])
        self.assertTrue(first["unique_spatial_minimizer"])
        self.assertTrue(first["inward_crossing_is_regular"])
        self.assertGreater(float(first["inward_flux_minus_s_dot_u"]), 0.0)
        self.assertTrue(first["ell_is_nonzero"])
        self.assertFalse(first["b_equals_s"])
        self.assertTrue(closest["ell_is_zero"])
        self.assertTrue(closest["b_equals_s"])
        self.assertTrue(closest["is_same_affine_episode_as_first_entry"])

        e1 = (1.0, 0.0, 0.0, 0.0)
        e2 = (0.0, 1.0, 0.0, 0.0)
        e3 = (0.0, 0.0, 1.0, 0.0)
        self.assertFalse(
            controls.orthonormal_basis_spans_columns(
                (e1, e2),
                (e1, e2, e3),
            )
        )

    def test_unique_curved_rank2_control(self) -> None:
        control = controls.build_unique_curved_rank2_control()
        self.assertTrue(all(control["checks"].values()))
        self.assertEqual(control["kinematic_rank"], 2)
        self.assertTrue(control["unique_strict_minimum"])
        self.assertTrue(control["hessian_is_positive_definite"])


class ReportAndPortabilityTests(unittest.TestCase):
    def test_report_is_deterministic_and_scope_bounded(self) -> None:
        first = controls.build_report()
        second = controls.build_report()
        self.assertEqual(first, second)
        self.assertEqual(first["status"], "PASS")
        self.assertEqual(
            controls.canonical_report_sha256(first),
            EXPECTED_CANONICAL_SHA256,
        )
        exclusions = first["boundary"]["does_not_implement_or_prove"]
        joined = " ".join(exclusions)
        self.assertIn("finite-K", joined)
        self.assertIn("physical first-entry", joined)
        self.assertIn("coverage", joined)

    def test_semantic_json_replay_is_lf_crlf_invariant(self) -> None:
        report = controls.build_report()
        serialized = controls.serialize_report(report)
        decoded = json.loads(serialized)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "report.json"

            path.write_text(serialized, encoding="utf-8", newline="\n")
            self.assertTrue(
                controls.type_strict_semantic_equal(
                    controls.read_semantic_json(path),
                    decoded,
                )
            )

            path.write_bytes(serialized.replace("\n", "\r\n").encode("utf-8"))
            self.assertTrue(
                controls.type_strict_semantic_equal(
                    controls.read_semantic_json(path),
                    decoded,
                )
            )

            hostile = json.loads(serialized)
            hostile["checks"]["all_declared_controls_pass"] = 1
            self.assertEqual(
                hostile["checks"]["all_declared_controls_pass"],
                True,
            )
            self.assertFalse(
                controls.type_strict_semantic_equal(hostile, decoded)
            )

    def test_stored_report_matches_fresh_semantics(self) -> None:
        path = Path(controls.__file__).with_name("analytic_tail_controls.json")
        self.assertTrue(path.exists())
        self.assertTrue(
            controls.type_strict_semantic_equal(
                controls.read_semantic_json(path),
                controls.build_report(),
            )
        )

    def test_semantic_json_rejects_duplicate_object_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "duplicate-key.json"
            path.write_text(
                '{"status":"PASS","status":"PASS"}\n',
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                ValueError,
                "duplicate JSON object key",
            ):
                controls.read_semantic_json(path)

    def test_cli_check_rejects_boolean_to_integer_mutation(self) -> None:
        hostile = controls.build_report()
        hostile["checks"]["all_declared_controls_pass"] = 1
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "hostile.json"
            path.write_text(
                controls.serialize_report(hostile),
                encoding="utf-8",
                newline="\n",
            )
            arguments = [
                "analytic_tail_controls.py",
                "--check",
                "--output",
                str(path),
            ]
            with mock.patch("sys.argv", arguments):
                with self.assertRaisesRegex(
                    SystemExit,
                    "semantic mismatch",
                ):
                    controls.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
