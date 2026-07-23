#!/usr/bin/env python3
"""Hostile standard-library tests for the Brief 0018 event contract."""

from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import event_contract as contract


DIRECTORY = Path(contract.__file__).resolve().parent
SCHEMA_PATH = DIRECTORY / "event_record.schema.json"
REPORT_PATH = DIRECTORY / "event_schema_controls.json"
EXPECTED_SCHEMA_NORMALIZED_LF_SHA256 = (
    "f4ccba32949690dcd9b00287741423925ef860ef166a4431df05b88ac813f89d"
)
EXPECTED_SCHEMA_CANONICAL_SHA256 = (
    "33207071ee5ae2933f8bd5d2032d01313586b17e3edd4fd8e38f97f50928d2b2"
)
EXPECTED_REPORT_CANONICAL_SHA256 = (
    "f7e0395b50839f281cf98fe0d2ac12d3db62b76a20fe5fb217e726becdef4dd8"
)


class SchemaAndFixtureTests(unittest.TestCase):
    def test_schema_registry_matches_semantic_validator(self) -> None:
        schema = contract.strict_load_json(SCHEMA_PATH)
        contract.validate_schema_document(schema)
        self.assertEqual(
            contract.normalized_lf_sha256(SCHEMA_PATH),
            EXPECTED_SCHEMA_NORMALIZED_LF_SHA256,
        )
        self.assertEqual(
            contract.canonical_sha256(schema),
            EXPECTED_SCHEMA_CANONICAL_SHA256,
        )
        self.assertEqual(
            schema["properties"]["primary_outcome"]["enum"],
            list(contract.PRIMARY_PRECEDENCE),
        )
        self.assertEqual(
            set(schema["properties"]["flags"]["required"]),
            set(contract.FLAG_NAMES),
        )

    def test_every_primary_has_one_valid_hostile_fixture(self) -> None:
        records = [
            contract.build_hostile_record(primary)
            for primary in contract.PRIMARY_PRECEDENCE
        ]
        self.assertEqual(
            [record["primary_outcome"] for record in records],
            list(contract.PRIMARY_PRECEDENCE),
        )
        self.assertTrue(
            all(
                record["precedence_trace"][-1]
                == record["primary_outcome"]
                for record in records
            )
        )

    def test_wrong_primary_is_rejected_even_when_shape_is_valid(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        record["primary_outcome"] = "grazing_entry"
        record["precedence_trace"] = contract.precedence_trace(
            "grazing_entry"
        )
        with self.assertRaisesRegex(
            contract.ContractError, "deterministic precedence"
        ):
            contract.validate_record(record)

    def test_extra_root_property_is_rejected(self) -> None:
        record = contract.build_hostile_record("source_invalid")
        record["unregistered"] = True
        with self.assertRaisesRegex(
            contract.ContractError, "unexpected keys"
        ):
            contract.validate_record(record)

    def test_scope_cannot_claim_physical_solver_or_mass(self) -> None:
        for field in (
            "physical_root_solver_run",
            "physical_outcome_mass_estimated",
            "rank_used_for_event_selection",
        ):
            with self.subTest(field=field):
                record = contract.build_hostile_record(
                    "regular_first_entry"
                )
                record["scope"][field] = True
                with self.assertRaises(contract.ContractError):
                    contract.validate_record(record)


class PrimaryPrecedenceTests(unittest.TestCase):
    def test_source_invalid_overrides_every_geometric_property(self) -> None:
        flags = contract.make_flags()
        flags.update(
            {
                "source_valid": False,
                "left_censored": True,
                "torus_branch_ambiguous": True,
                "torus_log_unique": False,
                "ambiguous_tie": True,
                "entry_tied": True,
                "entry_has_grazing": True,
                "entry_has_spatial_degeneracy": True,
            }
        )
        self.assertEqual(contract.classify_primary(flags), "source_invalid")

    def test_left_censor_overrides_later_solver_and_geometry(self) -> None:
        flags = contract.make_flags()
        flags.update(
            {
                "left_censored": True,
                "torus_log_unique": False,
                "torus_branch_ambiguous": True,
                "ambiguous_tie": True,
            }
        )
        self.assertEqual(
            contract.classify_primary(flags),
            "left_censored_active_episode",
        )

    def test_torus_ambiguity_overrides_tie_ambiguity(self) -> None:
        flags = contract.make_flags()
        flags.update(
            {
                "torus_log_unique": False,
                "torus_branch_ambiguous": True,
                "ambiguous_tie": True,
            }
        )
        self.assertEqual(
            contract.classify_primary(flags), "torus_branch_ambiguous"
        )

    def test_coverage_complete_ambiguous_tie_is_not_swallowed(self) -> None:
        flags = contract.make_flags()
        flags.update(
            {
                "ambiguous_tie": True,
                "root_coverage_complete": True,
                "solver_complete": False,
                "entry_observed": True,
                "entry_tied": True,
            }
        )
        self.assertEqual(contract.classify_primary(flags), "ambiguous_tie")

    def test_unresolved_earlier_box_overrides_later_clean_root(self) -> None:
        record = contract.build_hostile_record("numerically_unresolved")
        self.assertTrue(record["flags"]["entry_observed"])
        self.assertFalse(record["flags"]["root_coverage_complete"])
        self.assertEqual(
            record["certificates"]["unresolved"]["reason_codes"],
            ["possible_earlier_root_box"],
        )
        self.assertEqual(
            record["primary_outcome"], "numerically_unresolved"
        )

    def test_tie_precedes_degenerate_and_grazing_flags(self) -> None:
        record = contract.build_hostile_record("tie_cluster")
        self.assertTrue(record["flags"]["entry_tied"])
        self.assertTrue(record["flags"]["entry_has_grazing"])
        self.assertTrue(
            record["flags"]["entry_has_spatial_degeneracy"]
        )
        self.assertEqual(record["primary_outcome"], "tie_cluster")

    def test_degenerate_precedes_grazing(self) -> None:
        record = contract.build_hostile_record(
            "degenerate_spatial_minimum"
        )
        self.assertTrue(record["flags"]["entry_has_grazing"])
        self.assertTrue(
            record["flags"]["entry_has_spatial_degeneracy"]
        )
        self.assertEqual(
            record["primary_outcome"], "degenerate_spatial_minimum"
        )


class ClusterAndRankTests(unittest.TestCase):
    def test_finite_cluster_cardinality_mismatch_is_rejected(self) -> None:
        record = contract.build_hostile_record("tie_cluster")
        record["entry_cluster"]["cardinality"] = 3
        with self.assertRaisesRegex(
            contract.ContractError, "member count differs"
        ):
            contract.validate_record(record)

    def test_implicit_cluster_is_complete_without_scalar_members(self) -> None:
        record = contract.build_implicit_cluster_record()
        cluster = record["entry_cluster"]
        self.assertEqual(cluster["representation"], "implicit")
        self.assertEqual(cluster["cardinality"], "continuum")
        self.assertEqual(cluster["members"], [])
        self.assertFalse(record["flags"]["rank_marks_complete"])
        self.assertFalse(record["flags"]["normal_marks_complete"])

    def test_implicit_cluster_cannot_smuggle_scalar_member(self) -> None:
        record = contract.build_implicit_cluster_record()
        record["entry_cluster"]["members"].append(
            contract.make_representative("forbidden")
        )
        with self.assertRaisesRegex(
            contract.ContractError, "cannot enumerate members"
        ):
            contract.validate_record(record)

    def test_cluster_ordering_is_semantically_unordered(self) -> None:
        record = contract.build_hostile_record("tie_cluster")
        record["entry_cluster"]["unordered"] = False
        with self.assertRaisesRegex(
            contract.ContractError, "must be unordered"
        ):
            contract.validate_record(record)

    def test_rank_unresolved_entry_has_no_normal_object(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        member = record["entry_cluster"]["members"][0]
        member["jet_normal"] = contract.make_jet_normal(None)
        member["s"] = copy.deepcopy(member["jet_normal"]["s"])
        record["flags"]["rank_marks_complete"] = False
        record["flags"]["normal_marks_complete"] = False
        contract.validate_record(record)
        jet = member["jet_normal"]
        self.assertIsNone(jet["normal_dimension"])
        self.assertIsNone(jet["P_N"])
        self.assertIsNone(jet["normal_frame"])
        self.assertIsNone(jet["b"])
        self.assertIsNone(jet["ell"])
        self.assertEqual(
            record["primary_outcome"], "regular_first_entry"
        )

    def test_rank_unresolved_cannot_fabricate_projector(self) -> None:
        record = contract.build_hostile_record("numerically_unresolved")
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        jet["P_N"] = contract.identity_matrix(9)
        with self.assertRaisesRegex(
            contract.ContractError, "must not fabricate"
        ):
            contract.validate_record(record)

    def test_certified_rank_two_has_seven_dimensional_normal(self) -> None:
        record = contract.build_hostile_record(
            "degenerate_spatial_minimum"
        )
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        self.assertEqual(jet["rank"]["exact_rank"], 2)
        self.assertEqual(jet["normal_dimension"], 7)
        self.assertTrue(
            all(len(row) == 7 for row in jet["normal_frame"])
        )

    def test_fixed_six_frame_mutation_fails_on_rank_two(self) -> None:
        record = contract.build_hostile_record(
            "degenerate_spatial_minimum"
        )
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        jet["normal_frame"] = [row[:6] for row in jet["normal_frame"]]
        with self.assertRaisesRegex(
            contract.ContractError, "expected length 7"
        ):
            contract.validate_record(record)

    def test_boolean_is_not_accepted_as_normal_dimension(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        record["entry_cluster"]["members"][0]["jet_normal"][
            "normal_dimension"
        ] = True
        with self.assertRaisesRegex(
            contract.ContractError, "booleans are not integers"
        ):
            contract.validate_record(record)

    def test_nonprojector_mutation_is_rejected(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        jet["P_N"][0][0] = 0.5
        with self.assertRaisesRegex(
            contract.ContractError, "not idempotent"
        ):
            contract.validate_record(record)

    def test_b_must_equal_projected_separation(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        jet["b"][0] = 0.0
        jet["ell"][0] = 1.0
        with self.assertRaisesRegex(
            contract.ContractError, "differs from P_N s"
        ):
            contract.validate_record(record)

    def test_nonpositive_target_metric_is_rejected(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        jet = record["entry_cluster"]["members"][0]["jet_normal"]
        jet["G"][0][0] = 0.0
        with self.assertRaisesRegex(
            contract.ContractError, "not positive definite"
        ):
            contract.validate_record(record)


class ConditionalCertificateTests(unittest.TestCase):
    def test_source_invalid_needs_no_root_certificate(self) -> None:
        record = contract.build_hostile_record("source_invalid")
        self.assertIsNone(record["certificates"]["root_coverage"])
        contract.validate_record(record)

    def test_numerically_unresolved_requires_manifest(self) -> None:
        record = contract.build_hostile_record("numerically_unresolved")
        record["certificates"]["unresolved"] = None
        with self.assertRaisesRegex(
            contract.ContractError, "requires this certificate"
        ):
            contract.validate_record(record)

    def test_ambiguous_tie_requires_complete_root_coverage(self) -> None:
        record = contract.build_hostile_record("ambiguous_tie")
        record["flags"]["root_coverage_complete"] = False
        record["certificates"][
            "root_coverage"
        ] = contract.incomplete_coverage_certificate()
        with self.assertRaisesRegex(
            contract.ContractError, "complete root coverage"
        ):
            contract.validate_record(record)

    def test_finite_window_cannot_be_no_entry_proved(self) -> None:
        record = contract.build_hostile_record("no_entry_proved")
        record["observation"]["complete_time_domain"] = False
        record["flags"]["no_entry_complete_time_domain_certified"] = False
        record["flags"]["right_censored"] = True
        record["certificates"]["no_entry"] = {
            "certificate_id": "mutated-window",
            "mode": "finite_window",
            "complete": True,
            "period": None,
        }
        with self.assertRaisesRegex(
            contract.ContractError, "deterministic precedence"
        ):
            contract.validate_record(record)

    def test_oscillator_period_without_exact_common_period_is_rejected(
        self,
    ) -> None:
        record = contract.build_hostile_record("no_entry_proved")
        record["certificates"]["no_entry"]["mode"] = "finite_window"
        record["certificates"]["no_entry"]["period"] = None
        with self.assertRaisesRegex(
            contract.ContractError,
            "finite-window exclusion cannot prove no entry",
        ):
            contract.validate_record(record)

    def test_right_censor_requires_solver_complete_through_horizon(
        self,
    ) -> None:
        record = contract.build_hostile_record(
            "right_censored_active_episode"
        )
        record["flags"]["solver_complete"] = False
        with self.assertRaisesRegex(
            contract.ContractError, "deterministic precedence"
        ):
            contract.validate_record(record)

    def test_completed_episode_requires_strict_outer_overshoot(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        record["certificates"]["outer_exit"]["strict_overshoot"] = False
        record["certificates"]["outer_exit"]["rearmed"] = False
        record["flags"]["outer_exit_certified"] = False
        record["flags"]["rearmed"] = False
        record["flags"]["episode_complete"] = False
        with self.assertRaisesRegex(
            contract.ContractError, "deterministic precedence"
        ):
            contract.validate_record(record)

    def test_regular_entry_requires_global_and_no_earlier_certificates(
        self,
    ) -> None:
        for flag, certificate in (
            ("global_minimum_certified", "global_minimum"),
            ("no_earlier_entry_certified", "no_earlier_entry"),
        ):
            with self.subTest(certificate=certificate):
                record = contract.build_hostile_record(
                    "regular_first_entry"
                )
                record["certificates"][certificate] = None
                with self.assertRaisesRegex(
                    contract.ContractError, "requires this certificate"
                ):
                    contract.validate_record(record)


class HysteresisAndEpisodeTests(unittest.TestCase):
    def test_outer_tangent_touch_does_not_rearm(self) -> None:
        trace = contract.hysteresis_trace(
            (2.5, 1.0, 1.5, 2.0, 1.5),
            r_in=1.0,
            r_out=2.0,
        )
        self.assertEqual(trace["outer_grazes"], 1)
        self.assertEqual(trace["final_state"], "active")
        self.assertNotIn(
            "strict_outer_exit_rearm",
            [row["transition"] for row in trace["transitions"]],
        )

    def test_strict_outer_overshoot_rearms_exactly_once(self) -> None:
        trace = contract.hysteresis_trace(
            (2.5, 1.0, 1.5, 2.0, 2.1, 1.5),
            r_in=1.0,
            r_out=2.0,
        )
        transitions = [
            row["transition"] for row in trace["transitions"]
        ]
        self.assertEqual(
            transitions.count("strict_outer_exit_rearm"), 1
        )
        self.assertEqual(trace["final_state"], "armed")

    def test_inner_contact_while_active_is_secondary_not_new_episode(
        self,
    ) -> None:
        trace = contract.hysteresis_trace(
            (2.5, 1.0, 1.4, 1.0, 1.2),
            r_in=1.0,
            r_out=2.0,
        )
        transitions = [
            row["transition"] for row in trace["transitions"]
        ]
        self.assertEqual(transitions.count("inner_entry"), 1)
        self.assertEqual(trace["secondary_inner_contacts"], 1)

    def test_episode_merger_flag_must_match_lineage(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        record["episodes"][0]["component_events"].append(
            {
                "component_id": "component-b",
                "transition": "merge",
                "time": contract.interval(1.5),
            }
        )
        with self.assertRaisesRegex(
            contract.ContractError, "merger flag disagrees"
        ):
            contract.validate_record(record)
        record["flags"]["episode_has_component_merger"] = True
        contract.validate_record(record)

    def test_invalid_hysteresis_threshold_order_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "0<r_in<r_out"):
            contract.hysteresis_trace(
                (1.0,),
                r_in=2.0,
                r_out=1.0,
            )


class StrictJsonAndReplayTests(unittest.TestCase):
    def test_duplicate_keys_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "duplicate.json"
            path.write_text(
                '{"status":"PASS","status":"PASS"}\n',
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(
                contract.ContractError, "duplicate JSON object key"
            ):
                contract.strict_load_json(path)

    def test_nonfinite_json_numbers_are_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with tempfile.TemporaryDirectory() as temporary_directory:
                    path = Path(temporary_directory) / "nonfinite.json"
                    path.write_text(
                        '{"value":' + token + "}\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    with self.assertRaisesRegex(
                        contract.ContractError, "non-finite"
                    ):
                        contract.strict_load_json(path)

    def test_lf_crlf_semantic_replay_is_identical(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        text = contract.serialize_json(record)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "record.json"
            path.write_text(text, encoding="utf-8", newline="\n")
            lf = contract.strict_load_json(path)
            path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
            crlf = contract.strict_load_json(path)
        self.assertTrue(contract.type_strict_equal(lf, crlf))
        self.assertEqual(
            contract.canonical_sha256(lf),
            contract.canonical_sha256(crlf),
        )

    def test_boolean_to_integer_mutation_is_type_strict(self) -> None:
        record = contract.build_hostile_record("regular_first_entry")
        hostile = copy.deepcopy(record)
        hostile["entry_cluster"]["cardinality"] = True
        self.assertEqual(hostile["entry_cluster"]["cardinality"], 1)
        self.assertFalse(contract.type_strict_equal(record, hostile))
        with self.assertRaisesRegex(
            contract.ContractError, "booleans are not integers"
        ):
            contract.validate_record(hostile)

    def test_stored_report_matches_fresh_semantics(self) -> None:
        stored = contract.strict_load_json(REPORT_PATH)
        fresh = contract.build_control_report(SCHEMA_PATH)
        self.assertTrue(contract.type_strict_equal(stored, fresh))
        self.assertEqual(stored["status"], "PASS")
        self.assertTrue(all(stored["checks"].values()))
        self.assertEqual(
            contract.canonical_sha256(stored),
            EXPECTED_REPORT_CANONICAL_SHA256,
        )

    def test_cli_check_rejects_type_changing_report_mutation(self) -> None:
        report = contract.build_control_report(SCHEMA_PATH)
        first_key = next(iter(report["checks"]))
        report["checks"][first_key] = 1
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "hostile-report.json"
            path.write_text(
                contract.serialize_json(report),
                encoding="utf-8",
                newline="\n",
            )
            arguments = [
                "event_contract.py",
                "--schema",
                str(SCHEMA_PATH),
                "--output",
                str(path),
                "--check",
            ]
            with mock.patch("sys.argv", arguments):
                with self.assertRaisesRegex(
                    SystemExit, "semantic mismatch"
                ):
                    contract.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
