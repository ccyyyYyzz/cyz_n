#!/usr/bin/env python3
"""Tests for the normalized symbolic-pi closed-string Arb jets."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction
from typing import Any, Iterable

from flint import arb

import physical_arb_jets as old_jets
import symbolic_physical_arb_jets as jets
import symbolic_pi_lift as lift


def _point(value: Fraction | int) -> dict[str, Any]:
    return jets.point_interval(value)


def _point_box(
    u1: Fraction | int = 0,
    u2: Fraction | int = 0,
    t: Fraction | int = 0,
) -> dict[str, Any]:
    return {"u1": _point(u1), "u2": _point(u2), "t": _point(t)}


def _arb_leaves(value: Any) -> Iterable[arb]:
    if isinstance(value, arb):
        yield value
    elif type(value) in {list, tuple}:
        for item in value:
            yield from _arb_leaves(item)


def _canonical_problem() -> dict[str, Any]:
    fixture = lift.strict_json_load(lift.FIXTURE_PATH)
    lift.verify_fixture(fixture)
    return fixture["closed_string_problem"]


class SymbolicProblemAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.old_problem = old_jets.load_registered_physical_problem()
        cls.problem = jets.build_problem_adapter(cls.old_problem)

    def test_registered_symbolic_constants_and_domains(self) -> None:
        problem = self.problem
        self.assertEqual(
            jets._symbolic_scalar_parts(
                problem["exact_parameters"]["L_star"], "$.L_star"
            ),
            (Fraction(16), 1),
        )
        self.assertEqual(
            jets._symbolic_scalar_parts(
                problem["exact_parameters"]["T_F"], "$.T_F"
            ),
            (Fraction(1, 2), -1),
        )
        self.assertEqual(
            [
                jets._symbolic_scalar_parts(value, "$.period")
                for value in problem["target_torus"]["periods"]
            ],
            [(Fraction(8), 0)] * 8 + [(Fraction(1), 0)],
        )
        self.assertEqual(
            jets._symbolic_scalar_parts(
                problem["target_torus"]["metric_diagonal"][8],
                "$.metric[8]",
            ),
            (Fraction(256), 2),
        )
        jets._validate_convention(problem)

    def test_source_coefficients_are_exactly_preserved(self) -> None:
        old_mode = self.old_problem["kinematics"]["strings"][0]["modes"][0]
        new_mode = self.problem["kinematics"]["strings"][0]["modes"][0]
        for name in ("initial_x", "initial_y", "initial_p", "initial_q"):
            for component, (old_value, new_value) in enumerate(
                zip(old_mode[name], new_mode[name])
            ):
                self.assertEqual(
                    jets.dyadic_fraction(old_value),
                    jets._pi_zero_fraction(
                        new_value, f"$.{name}[{component}]"
                    ),
                )

    def test_strict_symbolic_atom_grammar(self) -> None:
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets._symbolic_scalar_parts(
                {"numerator": 1, "denominator": 2},
                "$.bad",
            )
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets._symbolic_scalar_parts(
                {"numerator": 2, "denominator": 4, "pi_exponent": 0},
                "$.bad",
            )
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets._symbolic_scalar_parts(
                {"numerator": 0, "denominator": 1, "pi_exponent": 1},
                "$.bad",
            )
        self.assertEqual(
            jets._symbolic_scalar_parts(
                {"numerator": 1, "denominator": 2, "pi_exponent": -1},
                "$.good",
            ),
            (Fraction(1, 2), -1),
        )

    def test_metric_winding_and_phase_mutants_are_rejected(self) -> None:
        canonical = _canonical_problem()
        metric_mutant = copy.deepcopy(canonical)
        metric_mutant["target_torus"]["metric_diagonal"][8] = (
            jets.symbolic_atom(64, 2)
        )
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets.evaluate_symbolic_physical_jets(
                metric_mutant, _point_box()
            )

        length_mutant = copy.deepcopy(canonical)
        length_mutant["exact_parameters"]["L_star"] = jets.symbolic_atom(
            8, 1
        )
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets.evaluate_symbolic_physical_jets(
                length_mutant, _point_box()
            )

        phase_mutant = copy.deepcopy(canonical)
        phase_mutant["kinematics"]["strings"][0]["modes"][0][
            "spatial_phase_coefficient"
        ] = jets.symbolic_atom(1, 1)
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets.evaluate_symbolic_physical_jets(
                phase_mutant, _point_box()
            )


class SymbolicPhysicalJetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.problem = _canonical_problem()
        cls.zero = jets.evaluate_symbolic_physical_jets(
            cls.problem, _point_box(), precision_bits=192
        )

    def test_shapes_and_derived_system(self) -> None:
        result = self.zero
        self.assertEqual(result["variable_order"], ("u1", "u2", "t"))
        self.assertEqual(len(result["d"]), 9)
        self.assertEqual([len(row) for row in result["d_a"]], [9, 9, 9])
        self.assertTrue(
            all(
                len(row) == 3 and all(len(vector) == 9 for vector in row)
                for row in result["d_ab"]
            )
        )
        self.assertEqual(len(result["F_a"]), 3)
        self.assertEqual([len(row) for row in result["F_ab"]], [3, 3, 3])
        expected_g = [
            result["F_a"][0],
            result["F_a"][1],
            result["F"] - result["radius"] * result["radius"] / 2,
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

    def test_normalized_winding_metric_factor(self) -> None:
        result = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(Fraction(1, 4), Fraction(1, 8), 0),
            precision_bits=256,
        )
        self.assertEqual(result["d"][8], jets.exact_arb(Fraction(3, 8)))
        transverse_twice_F = arb(0)
        for value in result["separation"][:8]:
            transverse_twice_F += value * value
        winding_twice_F = (
            result["winding_metric"]
            * result["separation"][8]
            * result["separation"][8]
        )
        self.assertTrue(
            (2 * result["F"] - transverse_twice_F - winding_twice_F).contains(
                arb(0)
            )
        )
        expected_metric = (16 * arb.pi()) ** 2
        self.assertTrue(
            (result["winding_metric"] - expected_metric).contains(arb(0))
        )

    def test_mixed_d_hessian_and_F_hessian(self) -> None:
        result = self.zero
        self.assertEqual(result["d_ab"][0][1], [arb(0)] * 9)
        self.assertEqual(result["d_ab"][1][0], [arb(0)] * 9)
        for component in (0, 3, 7):
            q1 = jets._pi_zero_fraction(
                self.problem["kinematics"]["strings"][0]["modes"][0][
                    "initial_q"
                ][component],
                "$.q1",
            )
            q2 = jets._pi_zero_fraction(
                self.problem["kinematics"]["strings"][1]["modes"][0][
                    "initial_q"
                ][component],
                "$.q2",
            )
            expected_u1_t = 2 * arb.pi() * jets._rational_arb(q1)
            expected_u2_t = -2 * arb.pi() * jets._rational_arb(q2)
            self.assertTrue(
                (
                    result["d_ab"][0][2][component] - expected_u1_t
                ).contains(arb(0))
            )
            self.assertTrue(
                (
                    result["d_ab"][1][2][component] - expected_u2_t
                ).contains(arb(0))
            )
            self.assertTrue(
                (
                    result["d_ab"][0][2][component]
                    - result["d_ab"][2][0][component]
                ).contains(arb(0))
            )
            self.assertTrue(
                (
                    result["d_ab"][1][2][component]
                    - result["d_ab"][2][1][component]
                ).contains(arb(0))
            )
        for row in range(3):
            for column in range(3):
                self.assertTrue(
                    (
                        result["F_ab"][row][column]
                        - result["F_ab"][column][row]
                    ).contains(arb(0))
                )

    def test_192_bit_box_contains_512_bit_point_jets(self) -> None:
        centre = {
            "u1": Fraction(5, 16),
            "u2": Fraction(3, 16),
            "t": Fraction(1, 8),
        }
        width = Fraction(1, 2**14)
        box = {
            name: jets.closed_interval(value - width, value + width)
            for name, value in centre.items()
        }
        point = {name: jets.point_interval(value) for name, value in centre.items()}
        enclosure = jets.evaluate_symbolic_physical_jets(
            self.problem, box, precision_bits=192
        )
        high_precision = jets.evaluate_symbolic_physical_jets(
            self.problem, point, precision_bits=512
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
            point_values = list(_arb_leaves(high_precision[key]))
            self.assertEqual(len(outer_values), len(point_values), key)
            for index, (outer, inner) in enumerate(
                zip(outer_values, point_values)
            ):
                self.assertTrue(
                    outer.contains(inner),
                    f"{key}[leaf {index}] misses the 512-bit point value",
                )

    def test_exact_seam_actions_and_endpoint_regression(self) -> None:
        shift1 = jets.exact_seam_image_shift(self.problem, 0)
        shift2 = jets.exact_seam_image_shift(self.problem, 1)
        self.assertEqual(shift1, (0,) * 8 + (1,))
        self.assertEqual(shift2, (0,) * 8 + (1,))
        self.assertEqual(
            tuple(a + b for a, b in zip(shift1, shift2)),
            (0,) * 8 + (2,),
        )

        fixed = {"u2": Fraction(3, 8), "t": Fraction(1, 8)}
        left = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(0, fixed["u2"], fixed["t"]),
            [0] * 9,
            precision_bits=256,
        )
        image1 = list(shift1)
        right = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(1, fixed["u2"], fixed["t"]),
            image1,
            precision_bits=256,
        )
        for key in ("separation", "d_a", "d_ab", "F", "F_a", "F_ab"):
            left_values = list(_arb_leaves(left[key]))
            right_values = list(_arb_leaves(right[key]))
            self.assertEqual(len(left_values), len(right_values), key)
            for a, b in zip(left_values, right_values):
                self.assertTrue((a - b).contains(arb(0)), key)

        fixed2 = {"u1": Fraction(5, 16), "t": Fraction(3, 16)}
        lower = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(fixed2["u1"], 0, fixed2["t"]),
            [0] * 9,
            precision_bits=256,
        )
        image2 = list(shift2)
        upper = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(fixed2["u1"], 1, fixed2["t"]),
            image2,
            precision_bits=256,
        )
        for key in ("separation", "d_a", "d_ab", "F", "F_a", "F_ab"):
            lower_values = list(_arb_leaves(lower[key]))
            upper_values = list(_arb_leaves(upper[key]))
            self.assertEqual(len(lower_values), len(upper_values), key)
            for a, b in zip(lower_values, upper_values):
                self.assertTrue((a - b).contains(arb(0)), key)

    def test_box_and_image_are_strict(self) -> None:
        bad = _point_box()
        bad["u1"] = _point(Fraction(9, 8))
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets.evaluate_symbolic_physical_jets(self.problem, bad)
        image = [0] * 9
        image[8] = True
        with self.assertRaises(jets.SymbolicPhysicalJetError):
            jets.evaluate_symbolic_physical_jets(
                self.problem, _point_box(), image
            )


class CanonicalLiftIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = lift.strict_json_load(lift.FIXTURE_PATH)
        lift.verify_fixture(cls.fixture)
        cls.problem = cls.fixture["closed_string_problem"]
        cls.adapter = jets.build_problem_adapter(
            old_jets.load_registered_physical_problem()
        )

    def test_canonical_problem_hash_and_direct_evaluation(self) -> None:
        self.assertEqual(
            lift.semantic_sha256(self.problem),
            lift.CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(
            lift.CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
            "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0",
        )
        result = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(Fraction(5, 16), Fraction(3, 16), Fraction(1, 8)),
            precision_bits=192,
        )
        self.assertEqual(
            result["problem_sha256"],
            lift.CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(result["variable_order"], ("u1", "u2", "t"))

    def test_production_apis_fail_closed_on_complete_problem_hash(self) -> None:
        mutants = []

        coefficient = copy.deepcopy(self.problem)
        coefficient["kinematics"]["strings"][0]["modes"][0][
            "initial_x"
        ][0]["numerator"] += 2
        mutants.append(coefficient)

        source = copy.deepcopy(self.problem)
        source["source_commitment"]["source_state_sha256"] = "0" * 64
        mutants.append(source)

        seam = copy.deepcopy(self.problem)
        seam["worldsheet"]["seam_image_actions"]["u2_plus_1"][
            "n8_reindex_shift"
        ] = -1
        mutants.append(seam)

        lattice = copy.deepcopy(self.problem)
        lattice["target_torus"]["lattice_matrix_diagonal"][0] = (
            jets.symbolic_atom(7)
        )
        mutants.append(lattice)

        for mutant in mutants:
            with self.subTest(
                digest=old_jets.semantic_sha256(mutant)
            ):
                with self.assertRaises(jets.SymbolicPhysicalJetError):
                    jets.evaluate_symbolic_physical_jets(
                        mutant, _point_box()
                    )
                with self.assertRaises(jets.SymbolicPhysicalJetError):
                    jets.exact_seam_image_shift(mutant, 0)

    def test_adapter_projection_matches_canonical_jet_inputs(self) -> None:
        for key in ("initial_time", "centres_Q1_Q2", "strings"):
            self.assertEqual(
                self.adapter["kinematics"][key],
                self.problem["kinematics"][key],
            )
        self.assertEqual(
            self.adapter["target_torus"]["periods"],
            self.problem["target_torus"]["periods"],
        )
        self.assertEqual(
            self.adapter["target_torus"]["metric_diagonal"],
            self.problem["target_torus"]["metric_diagonal"],
        )
        self.assertEqual(
            self.adapter["worldsheet"]["orientations"],
            self.problem["worldsheet"]["orientations"],
        )

    def test_canonical_192_bit_box_contains_512_bit_point(self) -> None:
        centre = {
            "u1": Fraction(7, 32),
            "u2": Fraction(9, 32),
            "t": Fraction(3, 16),
        }
        width = Fraction(1, 2**15)
        box = {
            name: jets.closed_interval(value - width, value + width)
            for name, value in centre.items()
        }
        point = {
            name: jets.point_interval(value)
            for name, value in centre.items()
        }
        enclosure = jets.evaluate_symbolic_physical_jets(
            self.problem, box, precision_bits=192
        )
        high_precision = jets.evaluate_symbolic_physical_jets(
            self.problem, point, precision_bits=512
        )
        for key in ("d", "d_a", "d_ab", "F", "F_a", "F_ab", "g_r", "Dg_r"):
            outer_values = list(_arb_leaves(enclosure[key]))
            point_values = list(_arb_leaves(high_precision[key]))
            self.assertEqual(len(outer_values), len(point_values), key)
            for index, (outer, inner) in enumerate(
                zip(outer_values, point_values)
            ):
                self.assertTrue(
                    outer.contains(inner),
                    f"{key}[leaf {index}] misses canonical 512-bit point",
                )

    def test_canonical_exact_seam_actions_drive_endpoint_relabeling(self) -> None:
        actions = self.problem["worldsheet"]["seam_image_actions"]
        shift1 = jets.exact_seam_image_shift(self.problem, 0)
        shift2 = jets.exact_seam_image_shift(self.problem, 1)
        expected1 = (0,) * 8 + (
            actions["u1_plus_1"]["n8_reindex_shift"],
        )
        expected2 = (0,) * 8 + (
            actions["u2_plus_1"]["n8_reindex_shift"],
        )
        self.assertEqual(expected1, shift1)
        self.assertEqual(expected2, shift2)
        self.assertEqual(
            (0,) * 8
            + (
                actions["corner_plus_1_plus_1"][
                    "n8_reindex_shift"
                ],
            ),
            tuple(a + b for a, b in zip(shift1, shift2)),
        )

        lower = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(0, Fraction(3, 8), Fraction(1, 8)),
            [0] * 9,
            precision_bits=256,
        )
        upper = jets.evaluate_symbolic_physical_jets(
            self.problem,
            _point_box(1, Fraction(3, 8), Fraction(1, 8)),
            list(shift1),
            precision_bits=256,
        )
        for key in ("separation", "d_a", "d_ab", "F", "F_a", "F_ab"):
            lower_values = list(_arb_leaves(lower[key]))
            upper_values = list(_arb_leaves(upper[key]))
            self.assertEqual(len(lower_values), len(upper_values), key)
            for a, b in zip(lower_values, upper_values):
                self.assertTrue((a - b).contains(arb(0)), key)


if __name__ == "__main__":
    unittest.main()
