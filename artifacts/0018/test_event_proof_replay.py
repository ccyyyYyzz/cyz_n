#!/usr/bin/env python3
"""Hostile proof-replay tests for the Brief 0018 v2 event record."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction

import coverage_proof as coverage
import event_contract as contract


class EventProofReplayTests(unittest.TestCase):
    def assert_rejected(self, record: dict) -> None:
        with self.assertRaises(contract.ContractError):
            contract.validate_record(record)

    def test_18_tied_grazing_degenerate_cluster_is_one_primary_row(
        self,
    ) -> None:
        record = contract.build_hostile_record("tie_cluster")
        self.assertEqual(record["primary_outcome"], "tie_cluster")
        self.assertTrue(record["flags"]["entry_tied"])
        self.assertTrue(record["flags"]["entry_has_grazing"])
        self.assertTrue(
            record["flags"]["entry_has_spatial_degeneracy"]
        )
        rows = contract.synthetic_primary_mass_rows(record)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["primary_outcome"], "tie_cluster")
        self.assertFalse(
            record["scope"]["physical_outcome_mass_estimated"]
        )

    def test_source_invalid_freezes_every_event_field(self) -> None:
        record = contract.build_hostile_record("source_invalid")
        self.assertTrue(all(value is False for value in record["flags"].values()))
        self.assertEqual(record["episodes"], [])
        self.assertIsNone(record["entry_cluster"])
        self.assertTrue(
            all(
                value is None
                for key, value in record["certificates"].items()
                if key != "source_validity"
            )
        )
        hostile = copy.deepcopy(record)
        hostile["flags"]["right_censored"] = True
        self.assert_rejected(hostile)

    def test_ambiguous_tie_requires_two_exactly_matched_isolated_candidates(
        self,
    ) -> None:
        record = contract.build_hostile_record("ambiguous_tie")
        hostile = copy.deepcopy(record)
        hostile["certificates"]["tie"]["candidate_ids"].pop()
        self.assert_rejected(hostile)

        hostile = copy.deepcopy(record)
        hostile["certificates"]["root_coverage"] = (
            coverage.build_mixed_unresolved_certificate()
        )
        hostile["flags"]["root_coverage_complete"] = False
        hostile["flags"]["solver_complete"] = False
        self.assert_rejected(hostile)

        hostile = copy.deepcopy(record)
        hostile["entry_cluster"]["members"].pop()
        hostile["entry_cluster"]["cardinality"] = 1
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_missing_completed_geometry_class_classifies_numerically(
        self,
    ) -> None:
        flags = contract.build_hostile_record("regular_first_entry")[
            "flags"
        ]
        flags["entry_geometry_regular"] = False
        self.assertEqual(
            contract.classify_primary(flags), "numerically_unresolved"
        )

    def test_26_regular_entry_requires_global_and_no_earlier_proofs(
        self,
    ) -> None:
        for certificate in ("global_minimum", "no_earlier_entry"):
            hostile = contract.build_hostile_record("regular_first_entry")
            hostile["certificates"][certificate] = None
            self.assert_rejected(hostile)

    def test_26_regular_entry_requires_positive_hessian_and_inward_flux(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["H_sigma_sigma"][1][1] = contract.interval(0.0)
        member["geometry_certificate"]["hessian_sha256"] = (
            contract.canonical_sha256(member["H_sigma_sigma"])
        )
        member["geometry_certificate"]["hessian_class"] = "psd_singular"
        member["geometry_certificate"]["determinant_range"] = (
            contract.interval(0.0)
        )
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["dF_dt"] = contract.interval(0.0)
        certificate = member["geometry_certificate"]
        certificate["flux_sha256"] = contract.canonical_sha256(
            member["dF_dt"]
        )
        certificate["flux_range"] = copy.deepcopy(member["dF_dt"])
        certificate["flux_class"] = "exact_zero_multiplicity"
        certificate["contact_multiplicity"] = 2
        certificate["one_sided_behavior"] = "touch_or_plateau"
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_27_overlap_without_equal_time_proof_is_not_complete_tie(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("tie_cluster")
        hostile["certificates"]["tie"]["equal_time_proof"] = None
        self.assert_rejected(hostile)

    def test_28_finite_or_approximate_recurrence_cannot_prove_no_entry(
        self,
    ) -> None:
        finite = contract.build_hostile_record(
            "right_censored_no_entry"
        )
        finite["primary_outcome"] = "no_entry_proved"
        finite["precedence_trace"] = contract.precedence_trace(
            "no_entry_proved"
        )
        self.assert_rejected(finite)

        approximate = contract.build_hostile_record("no_entry_proved")
        approximate["certificates"]["no_entry"]["recurrence"][
            "relative_velocity"
        ][0] = 0.999999999
        self.assert_rejected(approximate)

        missing_lattice = contract.build_hostile_record("no_entry_proved")
        del missing_lattice["certificates"]["no_entry"]["recurrence"][
            "lattice_vector"
        ]
        self.assert_rejected(missing_lattice)

    def test_29_outer_exit_needs_post_boundary_strict_bound(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["outer_exit"][
            "post_boundary_interval"
        ] = None
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["outer_exit"]["rho_lower_bound"] = 2.0
        self.assert_rejected(hostile)

    def test_30_order_relevant_unresolved_leaf_forces_unresolved_primary(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("numerically_unresolved")
        hostile["primary_outcome"] = "regular_first_entry"
        hostile["precedence_trace"] = contract.precedence_trace(
            "regular_first_entry"
        )
        self.assert_rejected(hostile)

    def test_rank_certificate_replays_J_projector_and_trace(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["jet_normal"]["J"][0][0] = 1
        member["jet_normal"]["rank_certificate"]["J_sha256"] = (
            contract.canonical_sha256(member["jet_normal"]["J"])
        )
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["jet_normal"]["P_N"][0][0] = 0.0
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

        record = contract.build_hostile_record("regular_first_entry")
        member = record["entry_cluster"]["members"][0]
        member["jet_normal"]["normal_frame"] = None
        contract._finalize_cluster(record["entry_cluster"])
        contract._bind_record_to_coverage_problem(record)
        record = contract.as_certified_solver_output(
            record, backend="formal-rank-representation-control"
        )
        member = record["entry_cluster"]["members"][0]
        self.assertIsNotNone(member["jet_normal"]["P_N"])
        self.assertEqual(
            sum(
                member["jet_normal"]["P_N"][index][index]
                for index in range(9)
            ),
            6.0,
        )

    def test_certificate_and_candidate_ids_are_exact_and_unique(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["closest"]["certificate_id"] = (
            hostile["certificates"]["outer_exit"]["certificate_id"]
        )
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("tie_cluster")
        hostile["entry_cluster"]["members"][1]["candidate_id"] = (
            hostile["entry_cluster"]["members"][0]["candidate_id"]
        )
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_certified_solver_output_scope_is_distinct_from_fixture(
        self,
    ) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        record = contract.as_certified_solver_output(
            record, backend="arb-interval-newton-v1"
        )
        contract.validate_record(record)

    def test_source_v2_draw_state_validity_and_external_envelope_bind(
        self,
    ) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        problem = record["certificates"]["root_coverage"]["manifest"][
            "exact_inputs"
        ]["problem_commitment"]
        draw_registry = problem["source_draw_registry"]
        self.assertEqual(
            problem["source_draw_registry_sha256"],
            contract.canonical_sha256(draw_registry),
        )
        self.assertEqual(
            record["source"]["sampling_registry_hash"],
            problem["source_draw_registry_sha256"],
        )
        self.assertNotEqual(
            problem["source_draw_registry_sha256"],
            problem["source_registry_sha256"],
        )
        self.assertTrue(
            {
                "L_A",
                "T_F",
                "L_w",
                "K",
                "E_perp",
                "P_tot",
                "pi_1",
                "pi_2",
                "prng",
            }.issubset(draw_registry)
        )
        self.assertTrue(
            {
                "r_in",
                "r_out",
                "rank_tolerance",
                "solver_budget",
                "reaction_data",
            }.isdisjoint(draw_registry)
        )

        formal = contract.as_certified_solver_output(
            record, backend="formal-source-v2-control"
        )
        manifest = formal["scope"]["solver_run_manifest"]
        self.assertEqual(
            manifest["source_draw_registry_sha256"],
            formal["scope"]["source_draw_registry_sha256"],
        )
        self.assertEqual(
            manifest["source_validity_sha256"],
            formal["scope"]["source_validity_sha256"],
        )
        self.assertFalse(
            formal["scope"]["authoritative_physical_certificate"]
        )
        self.assertEqual(
            formal["scope"]["independent_replayer"],
            "brief-0019-independent-event-replayer",
        )

    def test_source_draw_registry_reauthor_cannot_replace_pinned_fixture(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        problem = hostile["certificates"]["root_coverage"]["manifest"][
            "exact_inputs"
        ]["problem_commitment"]
        problem["source_draw_registry"]["K"] = 2
        problem["source_draw_registry_sha256"] = (
            contract.canonical_sha256(
                problem["source_draw_registry"]
            )
        )
        problem["source_registry"][
            "source_draw_registry_sha256"
        ] = problem["source_draw_registry_sha256"]
        problem["source_registry_sha256"] = (
            contract.canonical_sha256(problem["source_registry"])
        )
        contract._bind_record_to_coverage_problem(hostile)
        contract._bind_scope_provenance(hostile)
        self.assert_rejected(hostile)

    def test_no_earlier_and_global_time_bind_exact_root_witness(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["no_earlier_entry"]["earliest_time"] = (
            coverage.dyadic(7, 3)
        )
        hostile["certificates"]["no_earlier_entry"]["history_interval"][
            "hi"
        ] = coverage.dyadic(7, 3)
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        candidate = hostile["certificates"]["root_coverage"]["manifest"][
            "candidates"
        ][0]
        candidate["time_interval"] = coverage.exact_interval(
            Fraction(11, 16), Fraction(3, 4)
        )
        coverage.recompute_manifest_hash(
            hostile["certificates"]["root_coverage"]
        )
        self.assert_rejected(hostile)

    def test_negative_outer_threshold_cannot_be_self_certified(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        outer = hostile["certificates"]["outer_exit"]
        outer["rho_lower_bound"] = -999.0
        outer["r_out"] = -1000.0
        witness = outer["post_boundary_witness"]
        witness["rho_affine"]["intercept"] = coverage.dyadic(-999)
        witness["rho_range"] = coverage.exact_interval(-999, -999)
        self.assert_rejected(hostile)

    def test_recurrence_zero_period_lattice_shell_is_rejected(self) -> None:
        hostile = contract.build_hostile_record("no_entry_proved")
        recurrence = hostile["certificates"]["no_entry"]["recurrence"]
        recurrence["relative_velocity"] = [coverage.dyadic(0)] * 8
        recurrence["transverse_periods"] = [coverage.dyadic(0)] * 8
        recurrence["lattice_vector"] = [0] * 8
        seam = recurrence["time_seam_cover"]
        seam["lattice_vector"] = [0] * 8
        seam["state_tP"] = [coverage.dyadic(0)] * 8
        seam["wrapped_state_tP"] = [coverage.dyadic(0)] * 8
        self.assert_rejected(hostile)

    def test_ambiguous_tie_cannot_hide_geometry_uncertainty(self) -> None:
        hostile = contract.build_hostile_record("ambiguous_tie")
        for member in hostile["entry_cluster"]["members"]:
            certificate = member["geometry_certificate"]
            certificate["hessian_class"] = "unresolved"
            certificate["flux_class"] = "unresolved"
            certificate["contact_multiplicity"] = None
            certificate["one_sided_behavior"] = "unresolved"
            certificate["time_derivative_jet"] = [
                copy.deepcopy(member["dF_dt"])
            ]
            certificate["time_derivative_jet_sha256"] = (
                contract.canonical_sha256(
                    certificate["time_derivative_jet"]
                )
            )
        hostile["flags"]["entry_has_grazing"] = False
        hostile["flags"]["entry_has_spatial_degeneracy"] = False
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_scope_label_alone_cannot_forge_solver_output(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["scope"].update(
            {
                "record_kind": "certified_solver_output",
                "physical_root_solver_run": True,
                "proof_backend": "made-up",
            }
        )
        self.assert_rejected(hostile)

    def test_episode_entry_and_closest_bind_root_time(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        episode = hostile["episodes"][0]
        episode["T_in"] = {"lo": 0.5, "hi": 0.75}
        hostile["certificates"]["closest"]["time"] = {
            "lo": 0.5,
            "hi": 0.5,
        }
        self.assert_rejected(hostile)

    def test_singular_values_are_replayed_from_J_G_H(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        intervals = [
            contract.interval(99.0),
            contract.interval(98.0),
            contract.interval(97.0),
        ]
        member["jet_normal"]["singular_value_intervals"] = intervals
        member["jet_normal"]["rank_certificate"][
            "singular_intervals_sha256"
        ] = contract.canonical_sha256(intervals)
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_grazing_multiplicity_replays_derivative_jet(self) -> None:
        hostile = contract.build_hostile_record("grazing_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["geometry_certificate"]["contact_multiplicity"] = 999
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_representative_box_and_torus_image_bind_coverage_root(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["box"]["time"] = {"lo": 0.8, "hi": 0.8}
        hostile["episodes"][0]["T_in"] = {"lo": 0.8, "hi": 0.8}
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        member = hostile["entry_cluster"]["members"][0]
        member["torus_image"] = [999] * 9
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_torus_certificate_binds_image_manifest(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["torus_log"][
            "image_manifest_hash"
        ] = "f" * 64
        self.assert_rejected(hostile)

    def test_hysteresis_thresholds_share_registry_and_order(self) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["outer_exit"]["r_out"] = 0.5
        self.assert_rejected(hostile)

        hostile = contract.build_hostile_record("regular_first_entry")
        no_earlier = hostile["certificates"]["no_earlier_entry"]
        no_earlier["r_in"] = coverage.dyadic(999)
        no_earlier["initial_rho_lower_bound"] = coverage.dyadic(1000)
        witness = no_earlier["initial_armed_witness"]
        witness["rho_affine"]["intercept"] = coverage.dyadic(1000)
        witness["rho_range"] = coverage.exact_interval(1000, 1000)
        self.assert_rejected(hostile)

    def test_finite_window_and_coverage_equal_observation_window(self) -> None:
        hostile = contract.build_hostile_record(
            "right_censored_no_entry"
        )
        finite = hostile["certificates"]["no_entry"]["finite_window"]
        finite["t0"] = coverage.dyadic(100)
        finite["t1"] = coverage.dyadic(101)
        self.assert_rejected(hostile)

    def test_coordinated_root_rewrite_cannot_keep_problem_commitment(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        root_coverage = hostile["certificates"]["root_coverage"]
        manifest = root_coverage["manifest"]
        root_leaf = next(
            leaf
            for leaf in manifest["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_model = root_leaf["witness"]["root_model"]
        new_time = Fraction(13, 16)
        root_model["root"][2] = coverage.dyadic_from_fraction(new_time)
        root_model["constant"][2] = coverage.dyadic_from_fraction(
            new_time
        )
        candidate = manifest["candidates"][0]
        candidate["time_interval"] = coverage.exact_interval(
            new_time, new_time
        )
        coverage.recompute_manifest_hash(root_coverage)
        manifest_hash = root_coverage["manifest_sha256"]
        certs = hostile["certificates"]
        for name in (
            "global_minimum",
            "no_earlier_entry",
            "outer_exit",
            "closest",
        ):
            certs[name]["coverage_manifest_sha256"] = manifest_hash
        certs["global_minimum"]["earliest_time"] = (
            coverage.dyadic_from_fraction(new_time)
        )
        certs["global_minimum"]["candidate_time_bindings"][0][
            "time_interval_sha256"
        ] = contract.canonical_sha256(candidate["time_interval"])
        certs["no_earlier_entry"]["earliest_time"] = (
            coverage.dyadic_from_fraction(new_time)
        )
        certs["no_earlier_entry"]["history_interval"]["hi"] = (
            coverage.dyadic_from_fraction(new_time)
        )
        member = hostile["entry_cluster"]["members"][0]
        member["box"]["time"] = {
            "lo": float(new_time),
            "hi": float(new_time),
        }
        hostile["episodes"][0]["T_in"] = copy.deepcopy(
            member["box"]["time"]
        )
        contract._finalize_cluster(hostile["entry_cluster"])
        self.assert_rejected(hostile)

    def test_global_lower_bound_uses_registered_model_and_backend(
        self,
    ) -> None:
        record = contract.build_hostile_record("no_entry_proved")
        no_entry = record["certificates"]["no_entry"]
        no_entry["mode"] = "global_lower_bound"
        no_entry["recurrence"] = None
        problem = record["certificates"]["root_coverage"]["manifest"][
            "exact_inputs"
        ]["problem_commitment"]
        model = next(
            row
            for row in problem["function_registry"]["models"]
            if row["model_id"].endswith("::global-no-entry-rho")
        )
        problem_sha256 = record["scope"][
            "problem_commitment_sha256"
        ]
        no_entry["global_lower_bound"] = {
            "observable": "rho=sqrt(2F_min)",
            "time_domain": "all_real",
            "rho_affine": {
                "slope": coverage.dyadic(0),
                "intercept": coverage.dyadic(2),
            },
            "rho_lower_bound": coverage.dyadic(2),
            "r_in": coverage.dyadic(1),
            "witness_range": coverage.exact_interval(2, 2),
            "backend": "exact-synthetic-fixture",
            "problem_commitment_sha256": problem_sha256,
            "model_id": model["model_id"],
            "model_sha256": model["model_sha256"],
        }
        record["sample_id"] = "formal-global-lower-control"
        contract._bind_record_to_coverage_problem(record)
        formal = contract.as_certified_solver_output(
            record, backend="formal-root"
        )
        formal["certificates"]["no_entry"]["global_lower_bound"][
            "backend"
        ] = "made-up-lower"
        self.assert_rejected(formal)

        fabricated = copy.deepcopy(formal)
        lower = fabricated["certificates"]["no_entry"][
            "global_lower_bound"
        ]
        lower["rho_affine"]["intercept"] = coverage.dyadic(100)
        lower["rho_lower_bound"] = coverage.dyadic(100)
        lower["witness_range"] = coverage.exact_interval(100, 100)
        self.assert_rejected(fabricated)

    def test_pinned_models_cover_member_geometry_rank_and_observables(
        self,
    ) -> None:
        geometry = contract.build_hostile_record(
            "regular_first_entry"
        )
        member = geometry["entry_cluster"]["members"][0]
        member["F"] = contract.interval(100.0)
        member["grad_sigma"] = [
            contract.interval(5.0),
            contract.interval(-7.0),
        ]
        contract._finalize_cluster(geometry["entry_cluster"])
        self.assert_rejected(geometry)

        rank = contract.build_hostile_record("regular_first_entry")
        member = rank["entry_cluster"]["members"][0]
        certificate_id = member["jet_normal"]["rank_certificate"][
            "certificate_id"
        ]
        member["jet_normal"] = contract.make_jet_normal(2)
        member["jet_normal"]["rank_certificate"][
            "certificate_id"
        ] = certificate_id
        member["s"] = copy.deepcopy(member["jet_normal"]["s"])
        contract._finalize_cluster(rank["entry_cluster"])
        self.assert_rejected(rank)

        grazing = contract.build_hostile_record("grazing_entry")
        member = grazing["entry_cluster"]["members"][0]
        certificate = member["geometry_certificate"]
        certificate["time_derivative_jet"] = [
            contract.interval(0.0),
            contract.interval(0.0),
            contract.interval(0.0),
            contract.interval(1.0),
        ]
        certificate["time_derivative_jet_sha256"] = (
            contract.canonical_sha256(
                certificate["time_derivative_jet"]
            )
        )
        certificate["contact_multiplicity"] = 4
        contract._finalize_cluster(grazing["entry_cluster"])
        self.assert_rejected(grazing)

    def test_pinned_models_cover_closest_outer_and_recurrence(self) -> None:
        closest = contract.build_hostile_record("regular_first_entry")
        closest["certificates"]["closest"]["time"] = (
            contract.interval(1.75)
        )
        self.assert_rejected(closest)

        outer = contract.build_hostile_record("regular_first_entry")
        outer["certificates"]["outer_exit"]["boundary_time"] = (
            contract.interval(1.9)
        )
        outer["episodes"][0]["T_out"] = contract.interval(1.9)
        self.assert_rejected(outer)

        recurrence = contract.build_hostile_record("no_entry_proved")
        proof = recurrence["certificates"]["no_entry"]["recurrence"]
        proof["relative_velocity"] = [coverage.dyadic(0)] * 8
        proof["lattice_vector"] = [0] * 8
        seam = proof["time_seam_cover"]
        seam["lattice_vector"] = [0] * 8
        seam["state_tP"] = [coverage.dyadic(0)] * 8
        seam["wrapped_state_tP"] = [coverage.dyadic(0)] * 8
        self.assert_rejected(recurrence)

    def test_pinned_models_cover_source_and_torus_classification(
        self,
    ) -> None:
        source = contract.build_hostile_record("source_invalid")
        source["source"]["invalid_reasons"] = ["reason-A"]
        source["certificates"]["source_validity"]["reason_codes"] = [
            "reason-B"
        ]
        self.assert_rejected(source)

        torus = contract.build_hostile_record("regular_first_entry")
        torus["certificates"]["torus_log"]["unique"] = False
        torus["flags"]["torus_log_unique"] = False
        torus["flags"]["torus_branch_ambiguous"] = True
        torus["primary_outcome"] = "torus_branch_ambiguous"
        torus["precedence_trace"] = contract.precedence_trace(
            "torus_branch_ambiguous"
        )
        self.assert_rejected(torus)

    def test_local_registry_reauthor_cannot_replace_pinned_fixture(
        self,
    ) -> None:
        hostile = contract.build_hostile_record("regular_first_entry")
        hostile["certificates"]["closest"]["time"] = (
            contract.interval(1.75)
        )
        contract._bind_record_to_coverage_problem(hostile)
        contract._bind_scope_provenance(hostile)
        self.assert_rejected(hostile)


if __name__ == "__main__":
    unittest.main(verbosity=2)
