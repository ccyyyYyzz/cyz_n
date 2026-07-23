#!/usr/bin/env python3
"""Hostile standard-library tests for the Brief 0018 source sampler."""

from __future__ import annotations

import copy
import json
import math
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

import microcanonical_source as source


ARTIFACT_DIRECTORY = Path(source.__file__).resolve().parent
REGISTRY_PATH = ARTIFACT_DIRECTORY / "source_registry.json"
REPORT_PATH = ARTIFACT_DIRECTORY / "source_report.json"


def registry_copy() -> dict:
    return copy.deepcopy(source.read_strict_json(REGISTRY_PATH))


class RegistryAndMeasureTests(unittest.TestCase):
    def test_frozen_registry_and_regular_shell(self) -> None:
        registry = registry_copy()
        source.validate_registry(registry)
        parameters = source.source_parameters(registry)
        self.assertEqual(parameters["K"], 2)
        self.assertEqual(parameters["d"], 32)
        self.assertGreater(parameters["E_star"], 0.0)
        self.assertEqual(
            source.derived_dirichlet_shape(parameters["K"]),
            (4, 31, 31),
        )
        self.assertEqual(
            registry["source_draw"]["transverse_axis_order"],
            list(range(8)),
        )

    def test_winding_label_and_transverse_axis_order_move_together(self) -> None:
        registry = registry_copy()
        registry["source_draw"]["winding_cycle"] = 0
        with self.assertRaisesRegex(
            source.RegistryError, "ordered complement"
        ):
            source.validate_registry(registry)

    def test_empty_and_singular_shells_are_registry_failures(self) -> None:
        registry = registry_copy()
        draw = registry["source_draw"]
        mass = draw["string_tension"] * draw["winding_length"]
        minimum = math.fsum(
            value * value for value in draw["total_transverse_momentum"]
        ) / (4.0 * mass)

        singular = copy.deepcopy(registry)
        singular["source_draw"]["transverse_energy"] = minimum
        with self.assertRaisesRegex(source.RegistryError, "strictly positive"):
            source.validate_registry(singular)

        empty = copy.deepcopy(registry)
        empty["source_draw"]["transverse_energy"] = minimum - 0.01
        with self.assertRaisesRegex(source.RegistryError, "strictly positive"):
            source.validate_registry(empty)

    def test_nonzero_pi_and_tolerance_conditioning_are_rejected(self) -> None:
        nonzero = registry_copy()
        nonzero["source_draw"]["worldsheet_momenta"] = [0.25, 0.0]
        with self.assertRaisesRegex(source.RegistryError, "pi_1=pi_2=0"):
            source.validate_registry(nonzero)

        tolerance_band = registry_copy()
        tolerance_band["source_draw"]["constraint_method"] = (
            "absolute-worldsheet-momentum-tolerance"
        )
        with self.assertRaisesRegex(source.RegistryError, "ambient-delta"):
            source.validate_registry(tolerance_band)

    def test_scoped_nonzero_pi_sign_and_strict_boundary(self) -> None:
        left, right = source.nonzero_pi_chiral_energies(3.0, 1.0)
        self.assertEqual((left, right), (1.0, 2.0))
        swapped_left, swapped_right = source.nonzero_pi_chiral_energies(
            3.0, -1.0
        )
        self.assertEqual((swapped_left, swapped_right), (right, left))
        self.assertFalse(
            source.nonzero_pi_regular_shell_admissible(
                1.5, (1.0, -0.5)
            )
        )
        self.assertTrue(
            source.nonzero_pi_regular_shell_admissible(
                math.nextafter(1.5, math.inf), (1.0, -0.5)
            )
        )
        with self.assertRaisesRegex(ValueError, "at least"):
            source.nonzero_pi_chiral_energies(0.9, 1.0)

    def test_integer_and_boolean_types_are_not_conflated(self) -> None:
        registry = registry_copy()
        registry["source_draw"]["fourier_cutoff_K"] = True
        with self.assertRaisesRegex(source.RegistryError, "integer"):
            source.validate_registry(registry)

    def test_source_draw_identity_excludes_all_downstream_fields(self) -> None:
        registry = registry_copy()
        identity = source.source_draw_identity(registry)
        self.assertEqual(
            set(identity),
            {
                "registry_schema",
                "prng_algorithm",
                "source_seed",
                "source_draw",
            },
        )
        serialized = source.canonical_bytes(identity).decode("utf-8")
        for forbidden in (
            "r_in",
            "r_out",
            "rank_tolerance",
            "normal_dimension_hint",
            "response_winner",
            "reaction_scale",
            "graph_upper_bound_max",
            "uv_product_max",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_shape_mutations_are_rejected_analytically(self) -> None:
        dimension = source.source_parameters(registry_copy())["d"]
        source.require_derived_dirichlet_shape(2, (4, 31, 31))
        for mutation in (
            (4, dimension, dimension),
            (4, dimension // 2, dimension // 2),
            (4, dimension - 0.5, dimension - 0.5),
        ):
            with self.assertRaisesRegex(ValueError, "shape mutation"):
                source.require_derived_dirichlet_shape(2, mutation)

    def test_reduced_normalizer_has_the_derived_energy_power(self) -> None:
        cutoff = 2
        dimension = 16 * cutoff
        lower = source.reduced_shell_log_normalizer(cutoff, 3.0)
        upper = source.reduced_shell_log_normalizer(cutoff, 6.0)
        self.assertAlmostEqual(
            upper - lower,
            (2 * dimension + 1) * math.log(2.0),
            places=12,
        )

    def test_exact_dirichlet_moments(self) -> None:
        shapes = (4, 31, 31)
        total = sum(shapes)
        self.assertAlmostEqual(
            source.dirichlet_moment(shapes, (1, 0, 0)),
            4 / total,
            places=16,
        )
        self.assertAlmostEqual(
            source.dirichlet_moment(shapes, (0, 1, 1)),
            31 * 31 / (total * (total + 1)),
            places=16,
        )
        self.assertAlmostEqual(
            source.dirichlet_moment(shapes, (2, 0, 0)),
            4 * 5 / (total * (total + 1)),
            places=16,
        )


class ChiralAlgebraTests(unittest.TestCase):
    def test_forward_inverse_round_trip(self) -> None:
        values = (
            (0.3, -0.7, 1.1, -0.2),
            (-1.2, 0.0, 0.4, 0.8),
            (1.0e-5, -2.0e-5, 3.0e-5, -4.0e-5),
        )
        for wave_number in (0.17, 1.0, 7.5):
            for x, y, p, q in values:
                left, right = source.chiral_from_real(
                    x, y, p, q, wave_number
                )
                recovered = source.real_from_chiral(
                    left, right, wave_number
                )
                for actual, expected in zip(recovered, (x, y, p, q)):
                    self.assertAlmostEqual(actual, expected, places=14)

    def test_pure_left_and_right_worldsheet_signs(self) -> None:
        mass = 3.25
        wave_number = 1.7
        for left, right, sign in (
            (complex(0.4, -0.3), 0j, -1.0),
            (0j, complex(0.4, -0.3), 1.0),
        ):
            x, y, p, q = source.real_from_chiral(
                left, right, wave_number
            )
            hamiltonian = 0.25 * mass * (
                p * p
                + q * q
                + wave_number**2 * (x * x + y * y)
            )
            worldsheet = (
                0.5
                * mass
                * wave_number
                * (p * y - q * x)
            )
            self.assertAlmostEqual(worldsheet, sign * hamiltonian, places=14)

    def test_analytic_and_finite_difference_jacobian(self) -> None:
        for mass in (0.4, 2.3, 11.0):
            for wave_number in (0.37, 2.0, 9.0):
                expected = source.canonical_mode_jacobian(wave_number)
                actual = source.finite_difference_canonical_jacobian(
                    mass, wave_number
                )
                self.assertAlmostEqual(
                    actual / expected,
                    1.0,
                    delta=2.0e-9,
                )

    def test_sampled_chiral_norms_match_but_directions_do_not_copy(self) -> None:
        registry = registry_copy()
        for index in range(12):
            state = source.sample_source(registry, index)
            vectors = source.extract_chiral_vectors(state, registry)
            for string_index, (left, right) in enumerate(vectors):
                self.assertAlmostEqual(
                    source.dot(left, left),
                    source.dot(right, right),
                    delta=2.0e-12,
                )
                self.assertNotEqual(left, right)
                target = state["energy_shares_s0_s1_s2"][
                    string_index + 1
                ] / 2.0
                self.assertAlmostEqual(
                    source.dot(left, left), target, delta=2.0e-12
                )


class SamplerAndConservationTests(unittest.TestCase):
    def test_every_sample_satisfies_all_eleven_constraints(self) -> None:
        registry = registry_copy()
        tolerance = registry["audit"]["constraint_absolute_tolerance"]
        for index in range(64):
            diagnostics = source.sample_source(
                registry, index
            )["constraint_diagnostics"]
            self.assertLessEqual(
                abs(diagnostics["energy_residual"]), tolerance
            )
            self.assertLessEqual(
                max(
                    abs(value)
                    for value in diagnostics["target_momentum_residual"]
                ),
                tolerance,
            )
            self.assertLessEqual(
                max(
                    abs(value)
                    for value in diagnostics[
                        "worldsheet_momentum_residual"
                    ]
                ),
                tolerance,
            )

    def test_serialized_constraint_residuals_have_exact_dyadic_certificates(
        self,
    ) -> None:
        registry = registry_copy()
        exact_tolerance = Fraction.from_float(
            registry["audit"]["constraint_absolute_tolerance"]
        )
        for index in range(32):
            state = source.sample_source(registry, index)
            row = source.exact_dyadic_constraint_residuals(
                state, registry
            )
            residuals = [
                row["energy_residual"],
                *row["target_momentum_residual"],
                *row["worldsheet_momentum_residual"],
            ]
            self.assertTrue(
                all(type(value) is Fraction for value in residuals)
            )
            self.assertTrue(
                all(abs(value) <= exact_tolerance for value in residuals)
            )

        hostile = source.sample_source(registry, 0)
        hostile["strings"][0]["transverse_velocity"][0] += 1.0e-3
        hostile_row = source.exact_dyadic_constraint_residuals(
            hostile, registry
        )
        self.assertGreater(
            abs(hostile_row["target_momentum_residual"][0]),
            exact_tolerance,
        )

    def test_gamma_and_hierarchical_beta_shares_are_on_exact_shell(self) -> None:
        registry = registry_copy()
        residual_energy = source.source_parameters(registry)["E_star"]
        for index in range(32):
            gamma = source.sample_radial_gamma(registry, index)
            beta = source.sample_radial_hierarchical_beta(registry, index)
            self.assertTrue(all(value > 0.0 for value in gamma))
            self.assertTrue(all(value > 0.0 for value in beta))
            self.assertAlmostEqual(
                math.fsum(gamma), residual_energy, places=13
            )
            self.assertAlmostEqual(
                math.fsum(beta), residual_energy, places=13
            )

    def test_hierarchical_beta_is_algorithmically_gamma_independent(self) -> None:
        registry = registry_copy()
        residual_energy = source.source_parameters(registry)["E_star"]
        with mock.patch.object(
            source,
            "gamma_integer",
            side_effect=AssertionError("Gamma primitive must not be called"),
        ):
            shares = source.sample_radial_hierarchical_beta(registry, 19)
        self.assertTrue(all(value > 0.0 for value in shares))
        self.assertAlmostEqual(
            math.fsum(shares), residual_energy, places=13
        )

    def test_exact_flow_conserves_energy_and_worldsheet_momentum(self) -> None:
        registry = registry_copy()
        for index in range(8):
            state = source.sample_source(registry, index)
            baseline = state["constraint_diagnostics"]
            for time in (0.0, 0.013, 0.7, 3.1, 11.0):
                evolved = source.evolve_state(state, registry, time)
                actual = evolved["constraint_diagnostics"]
                self.assertAlmostEqual(
                    actual["energy"], baseline["energy"], delta=5.0e-12
                )
                for left, right in zip(
                    actual["worldsheet_momenta"],
                    baseline["worldsheet_momenta"],
                ):
                    self.assertAlmostEqual(left, right, delta=5.0e-12)

    def test_relative_centre_has_one_gauge_representative(self) -> None:
        state = source.sample_source(registry_copy(), 7)
        self.assertEqual(state["Q1"], state["Q_relative"])
        self.assertEqual(state["Q2"], [0.0] * 8)
        self.assertEqual(
            state["relative_centre_gauge"], "Q2=0,Q1=Q_relative"
        )

    def test_sigma_average_does_not_double_count_Q(self) -> None:
        registry = registry_copy()
        state = source.sample_source(registry, 3)
        cutoff = source.source_parameters(registry)["K"]
        grid_size = 2 * cutoff + 3
        winding_length = registry["source_draw"]["winding_length"]
        for string_index, string in enumerate(state["strings"]):
            y_average = [0.0] * 8
            for grid_index in range(grid_size):
                sigma = winding_length * grid_index / grid_size
                for mode in string["modes"]:
                    phase = mode["wave_number"] * sigma
                    cosine = math.cos(phase)
                    sine = math.sin(phase)
                    for axis in range(8):
                        y_average[axis] += (
                            mode["x"][axis] * cosine
                            + mode["y"][axis] * sine
                        ) / grid_size
            self.assertLess(max(abs(value) for value in y_average), 2.0e-15)
            q = state["Q1"] if string_index == 0 else state["Q2"]
            x_average = [
                q[axis] + y_average[axis] for axis in range(8)
            ]
            for actual, expected in zip(x_average, q):
                self.assertAlmostEqual(actual, expected, places=14)


class IndependenceAndValidityTests(unittest.TestCase):
    def test_downstream_mutations_leave_source_states_bitwise_identical(self) -> None:
        registry = registry_copy()
        mutated = copy.deepcopy(registry)
        mutated["downstream_context"].update(
            {
                "r_in": 0.6,
                "r_out": 1.1,
                "rank_tolerance": 1.0e-4,
                "normal_dimension_hint": 6,
                "response_winner": "rank-three",
                "reaction_scale": 9.0,
            }
        )
        source.validate_registry(mutated)
        for index in range(20):
            baseline = source.sample_source(registry, index)
            hostile = source.sample_source(mutated, index)
            self.assertEqual(
                baseline["source_state_sha256"],
                hostile["source_state_sha256"],
            )
            self.assertTrue(
                source.type_strict_semantic_equal(
                    {
                        key: value
                        for key, value in baseline.items()
                        if key not in {"validity", "constraint_diagnostics"}
                    },
                    {
                        key: value
                        for key, value in hostile.items()
                        if key not in {"validity", "constraint_diagnostics"}
                    },
                )
            )

    def test_validity_mutation_changes_labels_without_redraw(self) -> None:
        registry = registry_copy()
        hostile = copy.deepcopy(registry)
        hostile["validity"]["graph_upper_bound_max"] = 1.0e-12
        hostile["validity"]["uv_product_max"] = 1.0e-12
        source.validate_registry(hostile)

        baseline = [source.sample_source(registry, index) for index in range(32)]
        mutated = [source.sample_source(hostile, index) for index in range(32)]
        self.assertEqual(len(baseline), len(mutated))
        self.assertTrue(
            all(
                left["source_state_sha256"] == right["source_state_sha256"]
                for left, right in zip(baseline, mutated)
            )
        )
        self.assertTrue(
            all(
                state["validity"]["status"] == "source_invalid"
                for state in mutated
            )
        )
        self.assertTrue(
            all(
                state["validity"]["sample_retained_without_redraw"]
                for state in mutated
            )
        )

    def test_frozen_audit_cell_retains_both_valid_and_invalid_records(self) -> None:
        registry = registry_copy()
        statuses = [
            source.sample_source(registry, index)["validity"]["status"]
            for index in range(registry["audit"]["sample_count"])
        ]
        self.assertIn("valid", statuses)
        self.assertIn("source_invalid", statuses)
        self.assertEqual(len(statuses), registry["audit"]["sample_count"])


class ReportAndSerializationTests(unittest.TestCase):
    def test_report_passes_and_scope_is_source_only(self) -> None:
        registry = registry_copy()
        report = source.build_report(registry, ARTIFACT_DIRECTORY)
        self.assertEqual(report["status"], "PASS")
        self.assertTrue(all(report["checks"].values()))
        exclusions = " ".join(report["scope"]["does_not_implement"])
        self.assertIn("event schema", exclusions)
        self.assertIn("first-entry", exclusions)
        self.assertIn("encounter rank", exclusions)
        self.assertIn("3+1", exclusions)

    def test_stored_report_matches_regeneration_and_hash(self) -> None:
        stored = source.read_strict_json(REPORT_PATH)
        regenerated = source.build_report(
            registry_copy(), ARTIFACT_DIRECTORY
        )
        self.assertTrue(
            source.type_strict_semantic_equal(stored, regenerated)
        )
        canonical_hash = source.sha256_hex(regenerated)
        self.assertEqual(len(canonical_hash), 64)
        self.assertEqual(canonical_hash, source.sha256_hex(stored))

    def test_lf_crlf_semantic_replay_and_type_strictness(self) -> None:
        report = source.build_report(registry_copy(), ARTIFACT_DIRECTORY)
        serialized = source.pretty_json(report)
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "report.json"
            path.write_text(serialized, encoding="utf-8", newline="\n")
            lf = source.read_strict_json(path)
            path.write_bytes(serialized.replace("\n", "\r\n").encode("utf-8"))
            crlf = source.read_strict_json(path)
            self.assertTrue(source.type_strict_semantic_equal(lf, crlf))

            hostile = copy.deepcopy(report)
            hostile["checks"]["all_samples_retained"] = 1
            self.assertFalse(
                source.type_strict_semantic_equal(hostile, report)
            )

    def test_duplicate_keys_and_nonfinite_numbers_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "hostile.json"
            path.write_text(
                '{"schema":"x","schema":"x"}\n',
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "duplicate JSON"):
                source.read_strict_json(path)

            path.write_text(
                '{"value":1e999}\n',
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaisesRegex(ValueError, "non-finite JSON"):
                source.read_strict_json(path)

    def test_cli_check_rejects_boolean_to_integer_report_mutation(self) -> None:
        report = source.build_report(registry_copy(), ARTIFACT_DIRECTORY)
        report["checks"]["all_samples_retained"] = 1
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "hostile-report.json"
            source.write_json(path, report)
            arguments = [
                "microcanonical_source.py",
                "--registry",
                str(REGISTRY_PATH),
                "--output",
                str(path),
                "--check",
            ]
            with mock.patch("sys.argv", arguments):
                with self.assertRaisesRegex(
                    SystemExit, "semantic mismatch"
                ):
                    source.main()


if __name__ == "__main__":
    unittest.main(verbosity=2)
