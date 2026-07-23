#!/usr/bin/env python3
"""Unit tests for the deterministic Brief 0017 analytic/event probe."""
from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import probe_0017 as p


class Brief0017Controls(unittest.TestCase):
    def test_hard_edge_constants(self) -> None:
        row = p.hard_edge_controls()
        c0 = row["fixed_point_iid_R8x2"]["C0_numeric"]
        self.assertAlmostEqual(c0, math.sqrt(math.pi / 2.0) / 48.0, places=15)
        self.assertEqual(
            row["all_regular_roots_affine_volume_surrogate"]["E_s1_s2"], 7
        )
        self.assertEqual(
            row["all_regular_roots_affine_volume_surrogate"]["constant_exact"],
            "1/105",
        )
        self.assertEqual(
            row["curved_closest_counterexample"]["conditional_local_exponent"], 6
        )

    def test_quadrature_approaches_exact_tails(self) -> None:
        rows = p.hard_edge_controls()["deterministic_quadrature"]
        self.assertLess(abs(rows[-1]["fixed_point_ratio_to_C0_eps7"] - 1.0), 0.01)
        self.assertLess(abs(rows[-1]["volume_ratio_to_eps8_over_105"] - 1.0), 0.01)

    def test_opposite_winding_identity_and_falsifiers(self) -> None:
        row = p.rank_controls()
        records = {x["id"]: x for x in row["records"]}
        self.assertEqual(records["straight_opposite"]["rank"], 2)
        self.assertEqual(records["excited_q_zero"]["rank"], 2)
        self.assertEqual(records["velocity_parallel_q"]["rank"], 2)
        self.assertEqual(records["full_rank"]["rank"], 3)
        self.assertTrue(
            all(x["identity_absolute_error"] < 1.0e-12 for x in records.values())
        )

    def test_near_degenerate_sequence_preserves_rank(self) -> None:
        rows = p.rank_controls()["near_degenerate_rank_three_sequence"]
        self.assertTrue(all(x["rank"] == 3 for x in rows))
        sigmas = [x["sigma_3"] for x in rows]
        self.assertTrue(all(sigmas[i + 1] < sigmas[i] for i in range(len(sigmas) - 1)))

    def test_first_entry_preserves_longitudinal_phase(self) -> None:
        row = p.first_entry_and_closest_control()
        self.assertFalse(row["entry"]["b_equals_s"])
        self.assertGreater(p.norm(row["entry"]["ell"]), 0.0)
        self.assertLess(row["entry"]["normal_residual"], 1.0e-12)
        self.assertLess(row["entry"]["reconstruction_residual"], 1.0e-12)

    def test_closest_approach_allows_b_equal_s(self) -> None:
        row = p.first_entry_and_closest_control()["closest_approach"]
        self.assertTrue(row["b_equals_s"])
        self.assertLess(row["full_stationarity_residual"], 1.0e-12)

    def test_stratified_normal_and_fixed_six_mutation(self) -> None:
        row = p.first_entry_and_closest_control()
        self.assertEqual(row["rank_strata"]["rank_three_normal_dimension"], 6)
        self.assertEqual(row["rank_strata"]["rank_two_normal_dimension"], 7)
        self.assertEqual(row["fixed_six_projector_mutation"]["status"], "REJECTED")

    def test_hysteresis_and_no_entry_semantics(self) -> None:
        row = p.hysteresis_control()
        self.assertLess(row["entry_time"], row["closest_time"])
        self.assertLess(row["closest_time"], row["outer_exit_time"])
        self.assertEqual(
            row["finite_window_no_entry"]["outcome"], "right_censored_no_entry"
        )
        self.assertEqual(
            row["complete_period_no_entry"]["outcome"], "no_entry_proved"
        )

    def test_all_exceptional_mass_is_retained(self) -> None:
        row = p.outcome_mass_ledger()
        self.assertEqual(set(row["weights"]), set(p.OUTCOME_TAGS))
        self.assertEqual(row["exact_total"], "1/1")
        self.assertTrue(row["regular_events_not_renormalized"])

    def test_finite_mode_flow_conserves_invariants(self) -> None:
        row = p.finite_mode_flow_control()
        self.assertLess(row["maximum_energy_drift"], 1.0e-14)
        self.assertLess(row["maximum_worldsheet_momentum_drift"], 1.0e-14)

    def test_dependency_boundary_is_rank_blind(self) -> None:
        row = p.dependency_audit()
        self.assertEqual(row["forbidden_seen"], [])
        self.assertTrue(row["rank_and_sigma_computed_only_as_output_marks"])

    def test_semantic_json_check_is_line_ending_independent(self) -> None:
        report = p.build_report()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.json"
            text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False)
            path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            stored = p.read_semantic_json(path)
            self.assertEqual(p.canonical_bytes(stored), p.canonical_bytes(report))


if __name__ == "__main__":
    unittest.main(verbosity=2)
