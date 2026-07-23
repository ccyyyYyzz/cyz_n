#!/usr/bin/env python3
"""Hostile unit tests for the deterministic Brief 0017 controls."""
from __future__ import annotations

import json
import math
import tempfile
import unittest
from pathlib import Path

import probe_0017 as p


class Brief0017Controls(unittest.TestCase):
    def test_hard_edge_exact_surrogate_facts(self) -> None:
        row = p.hard_edge_controls()
        fixed = row["fixed_point_iid_R8x2"]
        volume = row["pure_volume_palm_surrogate"]
        self.assertAlmostEqual(fixed["C0_numeric"], math.sqrt(math.pi / 2.0) / 48.0, places=15)
        self.assertEqual(fixed["singular_value_exponent"], 7)
        self.assertEqual(fixed["gram_eigenvalue_exponent"], "7/2")
        self.assertEqual(volume["exponent"], 8)
        self.assertEqual(volume["constant_exact"], "1/105")
        affine = row["affine_closest_scaling_control"]
        self.assertTrue(all(item["delta2_ratio"] == item["delta_minus1_ratio"] == item["delta_ratio"] == 1.0 for item in affine))
        self.assertEqual(row["curvature_lifted_conditional_counterexample"]["conditional_local_tail_exponent"], 6)

    def test_relative_error_controlled_quadrature(self) -> None:
        rows = p.hard_edge_controls()["relative_error_controlled_high_precision_quadrature"]
        last = rows[-1]
        self.assertAlmostEqual(last["fixed_point_ratio_to_C0_eps7"], 0.9987507809245811, places=14)
        self.assertAlmostEqual(last["volume_ratio_to_eps8_over_105"], 0.9987507809245810, places=14)
        self.assertLess(last["fixed_point_ratio_richardson_error_estimate"], 1.0e-15)
        self.assertLess(last["volume_ratio_richardson_error_estimate"], 1.0e-15)

    def test_opposite_winding_identity_and_lower_rank_falsifiers(self) -> None:
        row = p.rank_controls()
        records = {item["id"]: item for item in row["records"]}
        self.assertEqual(records["straight_opposite"]["exact_rank"], 2)
        self.assertEqual(records["excited_q_zero"]["exact_rank"], 2)
        self.assertEqual(records["velocity_parallel_q"]["exact_rank"], 2)
        self.assertEqual(records["full_rank"]["exact_rank"], 3)
        self.assertTrue(all(item["identity_certified_exact"] for item in records.values()))

    def test_hostile_near_degeneracy_preserves_raw_singular_values(self) -> None:
        rows = p.rank_controls()["near_degenerate_exact_rank_three_sequence"]
        self.assertTrue(all(item["exact_rank"] == 3 for item in rows))
        self.assertTrue(all(item["sigma_3_raw"] > 0.0 for item in rows))
        sigmas = [item["sigma_3_raw"] for item in rows]
        self.assertTrue(all(sigmas[index + 1] < sigmas[index] for index in range(len(sigmas) - 1)))
        by_id = {item["id"]: item for item in rows}
        self.assertEqual(by_id["near_degenerate_1e-08"]["numerical_rank"], 3)
        self.assertEqual(by_id["near_degenerate_1e-12"]["numerical_rank"], 3)
        self.assertEqual(by_id["near_degenerate_1e-16"]["exact_rank"], 3)
        self.assertEqual(by_id["near_degenerate_1e-16"]["numerical_rank"], 2)
        self.assertGreater(by_id["near_degenerate_1e-16"]["sigma_3_raw"], 0.0)

    def test_vector_shape_and_type_contracts(self) -> None:
        with self.assertRaisesRegex(ValueError, "shape mismatch"):
            p.dot([1.0] * 8, [1.0] * 7)
        with self.assertRaisesRegex(ValueError, r"shape \(8,\)"):
            p.vector([0.0] * 7, expected_dim=8, name="R8")
        with self.assertRaisesRegex(TypeError, "bool"):
            p.vector([0.0] * 7 + [True], expected_dim=8, name="R8")
        with self.assertRaisesRegex(ValueError, "column-shape mismatch"):
            p.gram([[1.0] * 8, [1.0] * 7])

    def test_fourier_Q_once_and_exact_flow_invariants(self) -> None:
        flow = p.finite_mode_flow_control()
        fourier = flow["fourier_convention_control"]
        self.assertEqual(fourier["Q_occurrences_in_embedding"], 1)
        self.assertLess(fourier["maximum_roundtrip_residual"], 1.0e-15)
        self.assertGreater(fourier["double_count_mutation_displacement_norm"], 0.0)
        self.assertLess(flow["maximum_energy_drift"], 1.0e-14)
        self.assertLess(flow["maximum_worldsheet_momentum_drift"], 1.0e-14)

    def test_entry_closest_and_executed_fixed_six_mutation(self) -> None:
        row = p.first_entry_and_closest_control()
        self.assertFalse(row["entry"]["b_equals_s"])
        self.assertGreater(p.norm(row["entry"]["ell"]), 0.0)
        self.assertTrue(row["closest_approach"]["b_equals_s"])
        self.assertEqual(row["rank_strata"]["rank_two_normal_dimension"], 7)
        mutation = row["fixed_six_projector_mutation"]
        self.assertEqual(mutation["status"], "REJECTED_BY_EXECUTED_GEOMETRY")
        self.assertGreater(mutation["mutation_error_norm"], 0.9)

    def test_executable_hysteresis_merger_and_rearm(self) -> None:
        result = p.hysteresis_control()["trace_result"]
        self.assertEqual(result["final_state"], "armed")
        self.assertEqual(len(result["episodes"]), 2)
        self.assertEqual(result["episodes"][0]["merged_components"], ["A", "B"])
        self.assertEqual(result["episodes"][0]["subentries_merged"], 1)
        transitions = [item["transition"] for item in result["transitions"]]
        self.assertEqual(transitions.count("active_to_armed_outer_exit"), 2)

    def test_total_primary_precedence_preserves_overlap_flags(self) -> None:
        row = p.event_schema_control()
        outcomes = [item["primary_outcome"] for item in row["classified_cases"].values()]
        self.assertEqual(set(outcomes), set(p.PRIMARY_OUTCOMES))
        overlap = row["classified_cases"]["constraint_invalid_censored_overlap"]
        self.assertEqual(overlap["primary_outcome"], "source_constraint_unresolved")
        self.assertTrue(overlap["flags"]["source_invalid"])
        degenerate = row["classified_cases"]["degenerate_grazing_tie"]
        self.assertEqual(degenerate["primary_outcome"], "degenerate_spatial_minimum")
        self.assertTrue(degenerate["flags"]["grazing_entry"])
        self.assertTrue(degenerate["flags"]["tie"])

    def test_full_cluster_policy_is_permutation_invariant(self) -> None:
        first = p.full_cluster([{"id": "b", "value": 2}, {"id": "a", "value": 1}])
        second = p.full_cluster([{"id": "a", "value": 1}, {"id": "b", "value": 2}])
        self.assertEqual(first, second)
        self.assertEqual(first["member_count"], 2)
        self.assertIn("no_scalar_representative", first["policy"])

    def test_principal_measure_and_dependency_mutations(self) -> None:
        source = p.source_measure_control()
        principal = source["principal_delta_liouville_law"]
        self.assertEqual(principal["coarea_branch_weights_omega_r"], ["1/5", "3/10", "1/2"])
        self.assertEqual(principal["exact_total"], "1")
        self.assertEqual(source["constraint_singular_strata"]["primary_outcome"], "source_constraint_unresolved")
        dependency = p.dependency_audit()
        self.assertTrue(dependency["all_hostile_mutations_rejected"])
        self.assertEqual(set(dependency["hostile_mutations"]), {"sigma_filter", "rank_filter"})

    def test_semantic_JSON_and_honest_report_ledger(self) -> None:
        report = p.build_report()
        self.assertEqual(report["verdict"], "inconclusive")
        ledger = report["physical_result_ledger"]
        self.assertEqual(ledger["physical_finite_K_first_entry_law"], "not computed")
        self.assertEqual(ledger["three_plus_one_selection"], "not computed")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "report.json"
            text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False)
            path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            stored = p.read_semantic_json(path)
            self.assertTrue(p.strict_json_equal(stored, report))
            self.assertEqual(p.canonical_bytes(stored), p.canonical_bytes(report))
            path.write_text('{"x":1,"x":2}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate JSON object key"):
                p.read_semantic_json(path)
            self.assertFalse(p.strict_json_equal({"x": 1}, {"x": 1.0}))


if __name__ == "__main__":
    unittest.main(verbosity=2)
