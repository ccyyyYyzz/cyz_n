#!/usr/bin/env python3
"""Hostile controls for the physical three-variable Arb Krawczyk fixture."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction

from flint import arb

import arb_interval_jets as jets
import arb_krawczyk_control as control


class ArbKrawczykTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = jets.load_strict_json(jets.DEFAULT_FIXTURE)
        cls.box = control.uniqueness_box()
        cls.result = control.compute_krawczyk(cls.fixture, cls.box)

    def test_registered_box_has_strict_inclusion_on_all_axes(self) -> None:
        self.assertTrue(self.result["strict_inclusion"])
        self.assertEqual(self.result["axis_inclusion"], [True, True, True])
        for margins in self.result["strict_margins"]:
            self.assertTrue(margins["lower"] > arb(0))
            self.assertTrue(margins["upper"] > arb(0))

    def test_krawczyk_centre_uses_replayed_zero_not_boolean(self) -> None:
        self.assertTrue(
            all(value == arb(0) for value in self.result["point"]["g"])
        )
        self.assertTrue(
            all(value == arb(0) for value in self.result["centre_term"])
        )

    def test_wider_box_fails_strict_inclusion(self) -> None:
        wide = {
            axis: jets.closed_interval(Fraction(-1, 16), Fraction(1, 16))
            for axis in control.AXES
        }
        result = control.compute_krawczyk(self.fixture, wide)
        self.assertFalse(result["strict_inclusion"])
        self.assertEqual(result["axis_inclusion"], [True, True, False])

    def test_false_preconditioner_does_not_inherit_success(self) -> None:
        false_C = [
            [Fraction(), Fraction(), Fraction()],
            [Fraction(), Fraction(), Fraction()],
            [Fraction(), Fraction(), Fraction()],
        ]
        result = control.compute_krawczyk(
            self.fixture,
            self.box,
            C_fraction=false_C,
        )
        self.assertFalse(result["strict_inclusion"])

    def test_outward_root_is_not_certified_by_the_same_box(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["relative_velocity"][0] = jets.dyadic_json(1)
        outward_inverse = [
            [Fraction(1, 2), Fraction(), Fraction()],
            [Fraction(), Fraction(1, 2), Fraction()],
            [Fraction(), Fraction(), Fraction(2)],
        ]
        result = control.compute_krawczyk(
            mutation, self.box, C_fraction=outward_inverse
        )
        self.assertTrue(result["strict_inclusion"])
        self.assertTrue(result["point"]["F_first"][2].lower() > arb(0))
        report = jets.build_report(mutation)
        self.assertFalse(report["gates"]["inward_flux_strictly_negative"])
        self.assertEqual(report["status"], "FAIL")

    def test_stored_report_matches_replay_and_scope(self) -> None:
        stored = jets.load_strict_json(control.DEFAULT_REPORT)
        replay = control.build_report(self.fixture)
        self.assertTrue(jets.semantic_equal(stored, replay))
        payload = copy.deepcopy(stored)
        declared = payload.pop("semantic_sha256")
        self.assertEqual(declared, jets.canonical_sha256(payload))
        self.assertEqual(stored["status"], "PASS")
        self.assertTrue(
            stored["scope"]["three_variable_arb_krawczyk_inclusion"]
        )
        self.assertFalse(stored["scope"]["physical_solver_complete"])
        self.assertFalse(stored["scope"]["source_population_bound"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
