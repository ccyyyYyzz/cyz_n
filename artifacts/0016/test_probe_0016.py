#!/usr/bin/env python3
"""Standard-library regression tests for the Brief 0016 probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import probe_0016


class KinematicRankTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controls = {
            item["name"]: item for item in probe_0016.build_kinematic_controls()
        }

    def test_declared_rank_strata(self) -> None:
        self.assertEqual(self.controls["jjp_noncollinear_rank3"]["kinematic_rank"], 3)
        self.assertEqual(
            self.controls["near_opposite_rank3_below_margin"]["kinematic_rank"], 3
        )
        self.assertEqual(
            self.controls["full_rank_rescaled_domain_metric"]["kinematic_rank"],
            3,
        )
        self.assertEqual(
            self.controls["strict_opposite_winding_rank2"]["kinematic_rank"], 2
        )
        self.assertEqual(
            self.controls[
                "independent_tangents_velocity_in_span_rank2"
            ]["kinematic_rank"],
            2,
        )
        self.assertEqual(
            self.controls["opposite_winding_collinear_velocity_rank1"][
                "kinematic_rank"
            ],
            1,
        )

    def test_near_degenerate_is_rank3_but_fails_open_margin(self) -> None:
        control = self.controls["near_opposite_rank3_below_margin"]
        self.assertEqual(control["kinematic_rank"], 3)
        self.assertFalse(control["passes_declared_rank3_margin"])

    def test_domain_metric_changes_margin_not_rank(self) -> None:
        control = self.controls["full_rank_rescaled_domain_metric"]
        self.assertEqual(control["kinematic_rank"], 3)
        self.assertEqual(control["domain_metric_diag"], ["4", "1", "1"])
        self.assertAlmostEqual(
            float(control["smallest_singular_value"]),
            0.5,
            places=14,
        )

    def test_gkm_D_minus_4_matches_exactly_rank3_stratum(self) -> None:
        for control in self.controls.values():
            self.assertEqual(
                control["gkm_dimension_matches_local_normal"],
                control["kinematic_rank"] == 3,
                control["name"],
            )

    def test_fixed_scattering_axis_does_not_repair_incoming_rank(self) -> None:
        """Counterexample required by Brief 0016.

        A nonzero fixed e3 axis is orthogonal to all columns of the strict
        opposite-winding rank-2 incoming Jacobian.  Declaring that outgoing
        axis nevertheless leaves the incoming rank equal to two and its
        normal dimension equal to d-2, not the GKM d-3 count.
        """

        counterexample = probe_0016.build_scattering_axis_counterexample(
            list(self.controls.values())
        )
        self.assertTrue(
            counterexample[
                "axis_is_nonzero_and_orthogonal_to_every_incoming_column"
            ]
        )
        self.assertEqual(counterexample["incoming_rank_before_declaring_axis"], 2)
        self.assertEqual(counterexample["incoming_rank_after_declaring_axis"], 2)
        self.assertEqual(
            counterexample["incoming_normal_dimension_after_declaring_axis"],
            probe_0016.SPATIAL_DIMENSION - 2,
        )
        self.assertNotEqual(
            counterexample["incoming_normal_dimension_after_declaring_axis"],
            counterexample["gkm_D_minus_4_dimension"],
        )
        self.assertTrue(counterexample["counterexample_passes"])


class SuppressionAndOnsetTests(unittest.TestCase):
    def test_suppression_is_strictly_monotone_in_codimension(self) -> None:
        _, checks = probe_0016.build_suppression_table()
        self.assertTrue(
            checks["ball_codimension_ordering_holds_on_declared_grid"]
        )
        self.assertTrue(
            checks["box_codimension_ordering_holds_on_declared_grid"]
        )
        self.assertTrue(
            checks["declared_large_rho_bounds_hold_for_rho_at_least_one"]
        )
        self.assertTrue(
            checks[
                "ball_strictly_decreasing_across_rho_for_positive_codimension"
            ]
        )
        self.assertTrue(
            checks[
                "box_strictly_decreasing_across_rho_for_positive_codimension"
            ]
        )
        self.assertTrue(checks["ball_at_least_box_on_declared_grid"])

    def test_exact_valid_frame_onset(self) -> None:
        self.assertEqual(probe_0016.valid_frame_count(2, 3), 0)
        self.assertEqual(probe_0016.valid_frame_count(3, 3), 6)
        self.assertEqual(probe_0016.valid_frame_count(5, 3), 60)
        self.assertEqual(probe_0016.valid_frame_count(9, 4), 3024)

    def test_report_is_deterministic_and_passes(self) -> None:
        first = probe_0016.serialize_report(probe_0016.build_report())
        second = probe_0016.serialize_report(probe_0016.build_report())
        self.assertEqual(first, second)
        decoded = json.loads(first)
        self.assertEqual(decoded["status"], "PASS")
        self.assertEqual(
            probe_0016.canonical_report_sha256(decoded),
            "08cc622e415d0594b85fa04230f0e87d68184402e9ec1500e1923f42f20e274b",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            output = (
                Path(temporary_directory)
                / "source_to_return_kinematic_probe.json"
            )
            output.write_text(first, encoding="utf-8", newline="\n")
            self.assertEqual(output.read_text(encoding="utf-8"), first)

            # Parsed-JSON replay must be invariant under a CRLF checkout.
            output.write_bytes(first.replace("\n", "\r\n").encode("utf-8"))
            self.assertEqual(
                probe_0016.read_semantic_json(output),
                decoded,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
