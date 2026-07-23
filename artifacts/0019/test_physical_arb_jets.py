#!/usr/bin/env python3
"""Controls for the source-bound nine-dimensional physical Arb jets."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

from flint import arb

import physical_arb_jets as jets


def _point(value: Fraction | int) -> dict[str, Any]:
    return jets.point_interval(value)


def _zero_box() -> dict[str, Any]:
    return {name: _point(0) for name in jets.VARIABLE_ORDER}


def _arb_leaves(value: Any) -> Iterable[arb]:
    if isinstance(value, arb):
        yield value
    elif type(value) in {list, tuple}:
        for item in value:
            yield from _arb_leaves(item)


class PhysicalProblemBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = jets.load_strict_json(
            jets.DEFAULT_SOURCE_BRIDGE_FIXTURE
        )
        cls.problem = cls.fixture["physical_problem"]

    def test_registered_loader_and_hash(self) -> None:
        loaded = jets.load_registered_physical_problem()
        self.assertEqual(
            jets.validate_physical_problem(loaded),
            jets.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(
            self.fixture["physical_problem_semantic_sha256"],
            jets.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )

    def test_problem_mutation_is_rejected_before_evaluation(self) -> None:
        mutation = copy.deepcopy(self.problem)
        mutation["kinematics"]["centre_term_multiplicity"] = 2
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(mutation, _zero_box())

    def test_backend_is_pinned(self) -> None:
        self.assertEqual(
            jets.check_backend(),
            {
                "python_flint": "0.9.0",
                "flint": "3.6.0",
                "arithmetic": "arb outward-rounded balls",
            },
        )


class ExactInputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.problem = jets.load_registered_physical_problem()

    def test_dyadics_are_reduced_and_boolean_free(self) -> None:
        with self.assertRaises(jets.PhysicalJetError):
            jets.dyadic_fraction({"numerator": True, "exponent": 0})
        with self.assertRaises(jets.PhysicalJetError):
            jets.dyadic_fraction({"numerator": 0, "exponent": 2})
        with self.assertRaises(jets.PhysicalJetError):
            jets.dyadic_fraction({"numerator": 2, "exponent": 3})
        with self.assertRaises(jets.PhysicalJetError):
            jets.dyadic_fraction({"numerator": 1, "exponent": -1})
        with self.assertRaises(jets.PhysicalJetError):
            jets.dyadic_fraction(
                {"numerator": 1, "exponent": 3, "decimal": "0.125"}
            )

    def test_box_has_exact_keys_and_order_independent_meaning(self) -> None:
        bad = _zero_box()
        bad["time"] = bad.pop("t")
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(self.problem, bad)
        reversed_box = _zero_box()
        reversed_box["t"] = {
            "lo": jets.dyadic_json(1),
            "hi": jets.dyadic_json(0),
        }
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(self.problem, reversed_box)

    def test_box_must_lie_in_registered_domain_closure(self) -> None:
        bad_sigma = _zero_box()
        bad_sigma["sigma1"] = _point(Fraction(-1, 8))
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(self.problem, bad_sigma)
        bad_time = _zero_box()
        bad_time["t"] = _point(64)
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(self.problem, bad_time)

    def test_lattice_image_is_strict_integer_vector(self) -> None:
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(
                self.problem, _zero_box(), [0] * 8
            )
        image = [0] * 9
        image[0] = True
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(
                self.problem, _zero_box(), image
            )

    def test_radius_is_positive_exact_dyadic(self) -> None:
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(
                self.problem,
                _zero_box(),
                radius=jets.dyadic_json(0),
            )
        with self.assertRaises(jets.PhysicalJetError):
            jets.evaluate_physical_jets(
                self.problem,
                _zero_box(),
                radius={"numerator": 2, "exponent": 3},
            )

    def test_exact_endpoint_serialization(self) -> None:
        value = arb((-3, -2), (1, -4))
        self.assertEqual(
            jets.arb_exact_endpoints(value),
            {
                "lo": jets.dyadic_json(Fraction(-13, 16)),
                "hi": jets.dyadic_json(Fraction(-11, 16)),
            },
        )
        encoded = jets.serialize_arb_exact_endpoints(
            arb(2).sqrt(), precision_bits=256
        )
        enclosure = jets.interval_arb(encoded)
        self.assertTrue(enclosure.contains(arb(2).sqrt()))


class PhysicalJetFormulaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.problem = jets.load_registered_physical_problem()
        cls.zero = jets.evaluate_physical_jets(
            cls.problem, _zero_box(), precision_bits=192
        )
        cls.kinematics = cls.problem["kinematics"]
        cls.string1, cls.string2 = cls.kinematics["strings"]
        cls.mode1 = cls.string1["modes"][0]
        cls.mode2 = cls.string2["modes"][0]

    def assert_contains_fraction(
        self, value: arb, expected: Fraction | int
    ) -> None:
        self.assertTrue(
            value.contains(jets.exact_arb(expected)),
            f"{value!r} does not contain {expected}",
        )

    def test_result_shapes_and_registered_names(self) -> None:
        result = self.zero
        self.assertEqual(
            result["problem_sha256"],
            jets.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(result["precision_bits"], 192)
        self.assertEqual(result["variable_order"], ("sigma1", "sigma2", "t"))
        self.assertEqual(len(result["variables"]), 3)
        self.assertEqual(len(result["d"]), 9)
        self.assertEqual([len(row) for row in result["d_a"]], [9, 9, 9])
        self.assertEqual(len(result["d_ab"]), 3)
        self.assertTrue(
            all(
                len(row) == 3 and all(len(vector) == 9 for vector in row)
                for row in result["d_ab"]
            )
        )
        self.assertEqual(len(result["F_a"]), 3)
        self.assertEqual([len(row) for row in result["F_ab"]], [3, 3, 3])
        self.assertEqual(len(result["g_r"]), 3)
        self.assertEqual([len(row) for row in result["Dg_r"]], [3, 3, 3])

    def test_registered_seam_mismatch_is_quantified_not_erased(self) -> None:
        mismatch = jets.registered_seam_phase_mismatch(
            self.problem, precision_bits=256
        )
        self.assertTrue(mismatch.upper() < arb(0))
        endpoints = jets.arb_exact_endpoints(
            mismatch, precision_bits=256
        )
        lower = jets.dyadic_fraction(endpoints["lo"])
        upper = jets.dyadic_fraction(endpoints["hi"])
        # k*L_w - 2*pi is approximately -2.449293598...e-16.
        self.assertGreater(lower, Fraction(-245, 10**18))
        self.assertLess(upper, Fraction(-244, 10**18))

    def test_Q_occurs_exactly_once_at_zero(self) -> None:
        Q1 = self.kinematics["centres_Q1_Q2"]["Q1"]
        Q2 = self.kinematics["centres_Q1_Q2"]["Q2"]
        for component in range(8):
            expected = (
                jets.dyadic_fraction(Q1[component])
                - jets.dyadic_fraction(Q2[component])
                + jets.dyadic_fraction(self.mode1["initial_x"][component])
                - jets.dyadic_fraction(self.mode2["initial_x"][component])
            )
            self.assert_contains_fraction(self.zero["d"][component], expected)

    def test_string2_has_the_separation_minus_sign(self) -> None:
        k2 = jets.dyadic_fraction(self.mode2["wave_number"])
        for component in (0, 3, 7):
            expected_sigma2 = -k2 * jets.dyadic_fraction(
                self.mode2["initial_y"][component]
            )
            expected_sigma2_sigma2 = k2 * k2 * jets.dyadic_fraction(
                self.mode2["initial_x"][component]
            )
            self.assert_contains_fraction(
                self.zero["d_a"][1][component], expected_sigma2
            )
            self.assert_contains_fraction(
                self.zero["d_ab"][1][1][component],
                expected_sigma2_sigma2,
            )

    def test_relative_time_derivative_has_string2_minus_sign(self) -> None:
        V1 = self.string1["transverse_velocity"]
        V2 = self.string2["transverse_velocity"]
        for component in (0, 2, 6):
            expected = (
                jets.dyadic_fraction(V1[component])
                - jets.dyadic_fraction(V2[component])
                + jets.dyadic_fraction(self.mode1["initial_p"][component])
                - jets.dyadic_fraction(self.mode2["initial_p"][component])
            )
            self.assert_contains_fraction(
                self.zero["d_a"][2][component], expected
            )

    def test_opposite_winding_embedding(self) -> None:
        box = {
            "sigma1": _point(Fraction(1, 4)),
            "sigma2": _point(Fraction(1, 8)),
            "t": _point(0),
        }
        result = jets.evaluate_physical_jets(self.problem, box)
        self.assert_contains_fraction(result["d"][8], Fraction(3, 8))
        self.assertEqual(result["d_a"][0][8], arb(1))
        self.assertEqual(result["d_a"][1][8], arb(1))
        self.assertEqual(result["d_a"][2][8], arb(0))
        self.assertTrue(
            all(
                result["d_ab"][a][b][8] == arb(0)
                for a in range(3)
                for b in range(3)
            )
        )

    def test_lattice_image_shifts_separation_not_d(self) -> None:
        image = [0] * 9
        image[0] = 1
        shifted = jets.evaluate_physical_jets(
            self.problem, _zero_box(), image
        )
        self.assertEqual(shifted["d"], self.zero["d"])
        self.assertEqual(shifted["lattice_shift"][0], arb(8))
        self.assertEqual(shifted["lattice_shift"][1:], [arb(0)] * 8)
        self.assertEqual(
            shifted["separation"][0],
            shifted["d"][0] - arb(8),
        )
        self.assertEqual(
            shifted["separation"][1:],
            shifted["d"][1:],
        )

    def test_radius_only_changes_boundary_equation(self) -> None:
        inner = jets.evaluate_physical_jets(
            self.problem,
            _zero_box(),
            radius=self.problem["hysteresis"]["r_in"],
        )
        self.assertEqual(inner["d"], self.zero["d"])
        self.assertEqual(inner["F"], self.zero["F"])
        self.assertEqual(inner["g_r"][:2], self.zero["g_r"][:2])
        expected_difference = Fraction(3, 32)
        self.assert_contains_fraction(
            inner["g_r"][2] - self.zero["g_r"][2],
            expected_difference,
        )

    def test_g_and_jacobian_are_derived_from_F_jets(self) -> None:
        result = self.zero
        radius = result["radius"]
        expected_g = [
            result["F_a"][0],
            result["F_a"][1],
            result["F"] - radius * radius / 2,
        ]
        for actual, expected in zip(result["g_r"], expected_g):
            self.assertTrue((actual - expected).contains(arb(0)))
        self.assertEqual(
            result["Dg_r"],
            [
                result["F_ab"][0],
                result["F_ab"][1],
                result["F_a"],
            ],
        )
        for row in range(3):
            for column in range(3):
                self.assertTrue(
                    (
                        result["F_ab"][row][column]
                        - result["F_ab"][column][row]
                    ).contains(arb(0))
                )

    def test_interval_encloses_high_precision_point(self) -> None:
        centre = {
            "sigma1": Fraction(5, 16),
            "sigma2": Fraction(3, 16),
            "t": Fraction(1, 8),
        }
        width = Fraction(1, 2**14)
        box = {
            name: jets.closed_interval(value - width, value + width)
            for name, value in centre.items()
        }
        point_box = {
            name: jets.point_interval(value)
            for name, value in centre.items()
        }
        enclosure = jets.evaluate_physical_jets(
            self.problem, box, precision_bits=192
        )
        point = jets.evaluate_physical_jets(
            self.problem, point_box, precision_bits=384
        )
        for key in (
            "variables",
            "d",
            "d_a",
            "d_ab",
            "separation",
            "F",
            "F_a",
            "F_ab",
            "g_r",
            "Dg_r",
        ):
            outer_values = list(_arb_leaves(enclosure[key]))
            point_values = list(_arb_leaves(point[key]))
            self.assertEqual(len(outer_values), len(point_values), key)
            for index, (outer, inner) in enumerate(
                zip(outer_values, point_values)
            ):
                self.assertTrue(
                    outer.contains(inner),
                    f"{key}[leaf {index}] does not contain 384-bit point",
                )


if __name__ == "__main__":
    unittest.main()
