#!/usr/bin/env python3
"""Independent controls for the Brief 0019 Arb interval-jet fixture."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from fractions import Fraction
from pathlib import Path

import arb_interval_jets as jets
from flint import arb


HERE = Path(__file__).resolve().parent


class StrictInputTests(unittest.TestCase):
    def test_duplicate_and_nonfinite_json_are_rejected(self) -> None:
        with self.assertRaises(jets.JetError):
            json.loads(
                '{"a":1,"a":2}',
                object_pairs_hook=jets.reject_duplicate_pairs,
                parse_constant=jets.reject_constant,
            )
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(jets.JetError):
                json.loads(
                    token,
                    object_pairs_hook=jets.reject_duplicate_pairs,
                    parse_constant=jets.reject_constant,
                )

    def test_boolean_and_ordinary_float_are_not_dyadics(self) -> None:
        with self.assertRaises(jets.JetError):
            jets.dyadic_fraction({"numerator": True, "exponent": 0})
        with self.assertRaises(jets.JetError):
            jets.dyadic_fraction(0.5)

    def test_dyadic_canonical_form_is_enforced(self) -> None:
        self.assertEqual(
            jets.dyadic_fraction({"numerator": 1, "exponent": 3}),
            Fraction(1, 8),
        )
        with self.assertRaises(jets.JetError):
            jets.dyadic_fraction({"numerator": 2, "exponent": 3})
        with self.assertRaises(jets.JetError):
            jets.dyadic_fraction({"numerator": 0, "exponent": 4})


class BackendAndFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = jets.load_strict_json(jets.DEFAULT_FIXTURE)

    def test_backend_versions_are_pinned(self) -> None:
        self.assertEqual(
            jets.check_backend(),
            {
                "python_flint": "0.9.0",
                "flint": "3.6.0",
                "arithmetic": "arb outward-rounded balls",
            },
        )

    def test_fixture_matches_regeneration(self) -> None:
        regenerated = jets.build_fixture()
        jets.validate_fixture(regenerated)
        self.assertTrue(jets.semantic_equal(self.fixture, regenerated))

    def test_wrong_shape_orientation_and_wave_number_fail(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["relative_centre"].pop()
        with self.assertRaises(jets.JetError):
            jets.validate_fixture(mutation)

        mutation = copy.deepcopy(self.fixture)
        mutation["winding_orientations"] = [1, 1]
        with self.assertRaises(jets.JetError):
            jets.validate_fixture(mutation)

        mutation = copy.deepcopy(self.fixture)
        mutation["wave_numbers"][0] = jets.dyadic_json(0)
        with self.assertRaises(jets.JetError):
            jets.validate_fixture(mutation)

    def test_proof_module_has_no_numpy_or_math_libm_import(self) -> None:
        source = Path(jets.__file__).read_text(encoding="utf-8")
        self.assertNotIn("import numpy", source)
        self.assertNotIn("from numpy", source)
        self.assertNotIn("import math", source)
        self.assertNotIn("from math", source)


class IntervalJetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = jets.load_strict_json(jets.DEFAULT_FIXTURE)
        cls.root = jets.evaluate_interval_jets(
            cls.fixture, "root_box", precision_bits=192
        )

    def assert_contains(self, value: arb, expected: Fraction | int) -> None:
        self.assertTrue(value.contains(jets.exact_arb(expected)))

    def test_registered_root_is_boundary_and_spatially_stationary(self) -> None:
        self.assert_contains(self.root["g"][0], 0)
        self.assert_contains(self.root["g"][1], 0)
        self.assert_contains(self.root["g"][2], 0)
        self.assertEqual(self.root["g"][0], arb(0))
        self.assertEqual(self.root["g"][1], arb(0))
        self.assertEqual(self.root["g"][2], arb(0))

    def test_root_has_positive_hessian_and_inward_flux(self) -> None:
        H = self.root["H_sigma_sigma"]
        self.assert_contains(H[0][0], 2)
        self.assert_contains(H[0][1], 0)
        self.assert_contains(H[1][0], 0)
        self.assert_contains(H[1][1], 2)
        self.assertTrue(H[0][0].lower() > arb(0))
        self.assertTrue(H[1][1].lower() > arb(0))
        self.assertTrue(self.root["det_H_sigma_sigma"].lower() > arb(0))
        self.assert_contains(self.root["F_first"][2], Fraction(-1, 2))
        self.assertTrue(self.root["F_first"][2].upper() < arb(0))

    def test_boundary_jacobian_factorization_is_replayed(self) -> None:
        self.assert_contains(self.root["det_Dg"], -2)
        self.assert_contains(self.root["Ft_det_H"], -2)
        self.assertTrue(
            self.root["det_identity_residual"].contains(arb(0))
        )
        self.assertEqual(self.root["det_identity_residual"], arb(0))

    def test_control_box_encloses_exact_dyadic_point_evaluation(self) -> None:
        control = jets.evaluate_interval_jets(
            self.fixture, "control_box", precision_bits=192
        )
        point_fixture = copy.deepcopy(self.fixture)
        point_fixture["root_box"] = {
            "sigma1": jets.point_interval(Fraction(1, 16)),
            "sigma2": jets.point_interval(Fraction(-1, 16)),
            "time": jets.point_interval(Fraction(1, 32)),
        }
        point = jets.evaluate_interval_jets(
            point_fixture, "root_box", precision_bits=256
        )
        for key in ("d", "separation", "F_first", "g"):
            for enclosure, value in zip(control[key], point[key]):
                self.assertTrue(enclosure.contains(value), msg=key)
        self.assertTrue(control["F"].contains(point["F"]))
        for row_enclosure, row_value in zip(
            control["F_second"], point["F_second"]
        ):
            for enclosure, value in zip(row_enclosure, row_value):
                self.assertTrue(enclosure.contains(value))
        for row_enclosure, row_value in zip(control["Dg"], point["Dg"]):
            for enclosure, value in zip(row_enclosure, row_value):
                self.assertTrue(enclosure.contains(value))

    def test_control_box_performs_real_trigonometric_interval_work(self) -> None:
        control = jets.evaluate_interval_jets(
            self.fixture, "control_box", precision_bits=192
        )
        self.assertNotEqual(control["d"][1].lower(), control["d"][1].upper())
        self.assertNotEqual(
            control["F_first"][0].lower(),
            control["F_first"][0].upper(),
        )
        self.assertTrue(control["F"].contains(self.root["F"]))


class StoredReportTests(unittest.TestCase):
    def test_stored_report_matches_regeneration_and_hash(self) -> None:
        fixture = jets.load_strict_json(jets.DEFAULT_FIXTURE)
        stored = jets.load_strict_json(jets.DEFAULT_REPORT)
        regenerated = jets.build_report(fixture)
        self.assertTrue(jets.semantic_equal(stored, regenerated))
        payload = copy.deepcopy(stored)
        declared = payload.pop("semantic_sha256")
        self.assertEqual(declared, jets.canonical_sha256(payload))
        self.assertEqual(stored["status"], "PASS")
        self.assertEqual(stored["failed_gates"], [])

    def test_report_refuses_physical_solver_or_population_claim(self) -> None:
        report = jets.load_strict_json(jets.DEFAULT_REPORT)
        scope = report["scope"]
        self.assertFalse(scope["physical_exhaustive_root_solver_complete"])
        self.assertFalse(scope["population_law_computed"])
        self.assertFalse(scope["three_plus_one_selected"])
        self.assertTrue(scope["finite_K_interval_jet_fixture"])

    def test_cli_inventory_is_normalized_lf(self) -> None:
        report = jets.load_strict_json(jets.DEFAULT_REPORT)
        self.assertEqual(
            report["code_inventory"]["arb_interval_jets.py"],
            jets.normalized_lf_sha256(Path(jets.__file__)),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
