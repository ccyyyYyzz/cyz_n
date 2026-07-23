#!/usr/bin/env python3
"""Controls for the symbolic-pi transverse no-entry solver."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

import symbolic_no_entry_solver as solver
import symbolic_physical_arb_jets as symbolic_jets
import symbolic_pi_lift as symbolic_lift


EXPECTED_SOLVER_REGISTRY_SHA256 = (
    "23e404021dcae9b4c75dca810feb404afe6786aa14280f0ae88b0fa4f24fcec5"
)
EXPECTED_CERTIFICATE_SHA256 = (
    "d2cd11d1f8fd1b3669d988f590ee619e9a7f5ee6af43b3a0671830abc69f7fe1"
)
EXPECTED_ROOT_SHA256 = (
    "78d1589b4049483b2865e434ef3b3227a576daee654be042c9cd63419474c636"
)


def load_certificate() -> dict[str, Any]:
    value = solver.strict_json_load(solver.DEFAULT_CERTIFICATE)
    assert type(value) is dict
    return value


def first_leaf(certificate: dict[str, Any]) -> dict[str, Any]:
    return next(
        node
        for node in certificate["tree"]["nodes"]
        if node["node_kind"] == "leaf"
    )


class PrimitiveControls(unittest.TestCase):
    def test_strict_json_rejects_duplicate_float_and_nonfinite(self) -> None:
        for text in (
            '{"x":1,"x":2}',
            '{"x":0.5}',
            '{"x":NaN}',
        ):
            with self.assertRaises(solver.SymbolicNoEntryError):
                solver.strict_json_loads(text)

    def test_dyadic_round_trip_and_noncanonical_rejection(self) -> None:
        for value in (
            Fraction(0),
            Fraction(1, 2),
            Fraction(-17, 64),
            Fraction(1 << 180),
        ):
            self.assertEqual(
                solver.dyadic_fraction(solver.dyadic_json(value)), value
            )
        for encoded in (
            {"numerator": 0, "exponent": 1},
            {"numerator": 2, "exponent": 1},
            {"numerator": True, "exponent": 0},
            {"numerator": 1, "exponent": -1},
        ):
            with self.assertRaises(solver.SymbolicNoEntryError):
                solver.dyadic_fraction(encoded)

    def test_floor_and_ceil_are_exact_for_negative_values(self) -> None:
        self.assertEqual(solver.floor_fraction(Fraction(-3, 2)), -2)
        self.assertEqual(solver.ceil_fraction(Fraction(-3, 2)), -1)
        self.assertEqual(solver.floor_fraction(Fraction(3, 2)), 1)
        self.assertEqual(solver.ceil_fraction(Fraction(3, 2)), 2)

    def test_boundary_contact_is_not_excluded(self) -> None:
        witness = solver.build_empty_coordinate_image_range(
            axis=0,
            d_enclosure={
                "lo": solver.dyadic_json(Fraction(1, 2)),
                "hi": solver.dyadic_json(Fraction(1, 2)),
            },
            period=solver.dyadic_json(8),
            radius=solver.dyadic_json(Fraction(1, 2)),
        )
        self.assertIsNone(witness)

    def test_winding_axis_is_forbidden(self) -> None:
        with self.assertRaises(solver.SymbolicNoEntryError):
            solver.build_empty_coordinate_image_range(
                axis=8,
                d_enclosure={
                    "lo": solver.dyadic_json(1),
                    "hi": solver.dyadic_json(2),
                },
                period=solver.dyadic_json(8),
                radius=solver.dyadic_json(Fraction(1, 2)),
            )

    def test_period_and_radius_are_frozen(self) -> None:
        for period, radius in (
            (solver.dyadic_json(16), solver.dyadic_json(Fraction(1, 2))),
            (solver.dyadic_json(8), solver.dyadic_json(Fraction(1, 4))),
        ):
            with self.assertRaises(solver.SymbolicNoEntryError):
                solver.build_empty_coordinate_image_range(
                    axis=0,
                    d_enclosure={
                        "lo": solver.dyadic_json(1),
                        "hi": solver.dyadic_json(2),
                    },
                    period=period,
                    radius=radius,
                )


class SymbolicBindingControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = symbolic_lift.strict_json_load(
            symbolic_lift.FIXTURE_PATH
        )
        cls.problem = cls.fixture["closed_string_problem"]

    def test_lift_fixture_and_problem_are_verified(self) -> None:
        replay = symbolic_lift.verify_fixture(copy.deepcopy(self.fixture))
        self.assertEqual(
            replay["closed_string_problem_semantic_sha256"],
            solver.CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
        )
        self.assertEqual(
            replay["lift_registry_semantic_sha256"],
            solver.SYMBOLIC_LIFT_REGISTRY_SEMANTIC_SHA256,
        )

    def test_solver_loader_runs_the_lift_gate(self) -> None:
        problem, replay = solver._load_registered_problem()
        self.assertTrue(solver.type_strict_equal(problem, self.problem))
        self.assertEqual(
            replay["closed_string_problem_semantic_sha256"],
            solver.CLOSED_STRING_PROBLEM_SEMANTIC_SHA256,
        )

    def test_symbolic_evaluator_is_fail_closed(self) -> None:
        hostile = copy.deepcopy(self.problem)
        coefficient = hostile["kinematics"]["strings"][0]["modes"][0][
            "initial_x"
        ][0]
        coefficient["numerator"] += 2
        root = solver._registered_domain(self.problem)
        with self.assertRaises(Exception):
            symbolic_jets.evaluate_symbolic_physical_jets(
                hostile,
                solver._box_for_arb(root),
                precision_bits=192,
            )

    def test_exact_seam_actions_are_algebraic(self) -> None:
        shift1 = symbolic_jets.exact_seam_image_shift(self.problem, 0)
        shift2 = symbolic_jets.exact_seam_image_shift(self.problem, 1)
        self.assertEqual(shift1[:8], (0,) * 8)
        self.assertEqual(shift2[:8], (0,) * 8)
        self.assertEqual(shift1[8], 1)
        self.assertEqual(shift2[8], 1)

    def test_transverse_period_radius_gate_ignores_winding_entries(self) -> None:
        periods, radius = solver._periods_and_radius(self.problem)
        self.assertEqual(len(periods), 8)
        self.assertEqual(
            [solver.dyadic_fraction(item) for item in periods],
            [Fraction(8)] * 8,
        )
        self.assertEqual(
            solver.dyadic_fraction(radius), Fraction(1, 2)
        )


class DefaultCertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = solver.build_certificate()

    def test_registry_is_code_pinned(self) -> None:
        registry_hash = solver.semantic_sha256(
            self.certificate["solver_registry"]
        )
        self.assertEqual(registry_hash, EXPECTED_SOLVER_REGISTRY_SHA256)
        self.assertEqual(
            registry_hash, solver.SOLVER_REGISTRY_SEMANTIC_SHA256
        )

    def test_default_tree_topology_is_pinned(self) -> None:
        summary = self.certificate["summary"]
        self.assertEqual(summary["node_count"], 259)
        self.assertEqual(summary["split_nodes"], 129)
        self.assertEqual(summary["leaf_count"], 130)
        self.assertEqual(summary["excluded_leaves"], 130)
        self.assertEqual(summary["unresolved_leaves"], 0)
        self.assertEqual(summary["maximum_depth"], 9)
        self.assertEqual(
            summary["transverse_axis_counts"],
            [14, 66, 12, 10, 4, 0, 0, 24],
        )
        self.assertEqual(
            summary["root_node_semantic_sha256"], EXPECTED_ROOT_SHA256
        )

    def test_default_certificate_hash_is_pinned(self) -> None:
        self.assertEqual(
            self.certificate["certificate_semantic_sha256"],
            EXPECTED_CERTIFICATE_SHA256,
        )

    def test_root_is_the_exact_half_open_quotient_domain(self) -> None:
        domain = self.certificate["domain"]
        self.assertEqual(domain["axes"], ["u1", "u2", "t"])
        for interval in domain["intervals"]:
            self.assertIs(interval["lower_closed"], True)
            self.assertIs(interval["upper_closed"], False)
        for interval in domain["intervals"][:2]:
            self.assertEqual(solver.dyadic_fraction(interval["lower"]), 0)
            self.assertEqual(solver.dyadic_fraction(interval["upper"]), 1)
        root = self.certificate["tree"]["nodes"][0]
        self.assertTrue(solver.type_strict_equal(root["box"], domain))

    def test_every_leaf_is_strict_and_transverse_only(self) -> None:
        leaves = [
            node
            for node in self.certificate["tree"]["nodes"]
            if node["node_kind"] == "leaf"
        ]
        self.assertEqual(len(leaves), 130)
        counts = [0] * 8
        for node in leaves:
            witness = node["payload"]["witness"]
            self.assertEqual(
                witness["witness_type"],
                "empty_transverse_coordinate_image_range",
            )
            axis = witness["axis"]
            self.assertIn(axis, range(8))
            counts[axis] += 1
            self.assertEqual(solver.dyadic_fraction(witness["period"]), 8)
            self.assertEqual(
                solver.dyadic_fraction(witness["radius"]), Fraction(1, 2)
            )
            self.assertGreater(witness["nmin"], witness["nmax"])
            self.assertGreater(
                solver.dyadic_fraction(witness["margins"]["minimum"]), 0
            )
            self.assertIs(witness["winding_image_used"], False)
            self.assertIs(witness["winding_metric_used"], False)
        self.assertEqual(counts, [14, 66, 12, 10, 4, 0, 0, 24])

    def test_outcome_is_quotient_safe_finite_window_only(self) -> None:
        outcome = self.certificate["outcome"]
        self.assertEqual(outcome["type"], "right_censored_no_entry")
        self.assertIs(outcome["exact_worldsheet_quotient_claimed"], True)
        self.assertIs(outcome["transverse_exclusion_only"], True)
        self.assertIs(outcome["winding_image_used"], False)
        self.assertIs(outcome["winding_metric_used"], False)
        self.assertIs(outcome["all_time_no_entry_claimed"], False)

    def test_tree_is_flat_preorder_and_bottom_up_bound(self) -> None:
        nodes = self.certificate["tree"]["nodes"]
        by_id = {node["node_id"]: node for node in nodes}
        self.assertEqual(len(by_id), len(nodes))
        preorder: list[str] = []

        def visit(node_id: str) -> str:
            node = by_id[node_id]
            preorder.append(node_id)
            if node["node_kind"] == "split":
                payload = node["payload"]
                left_hash = visit(payload["left_child_id"])
                right_hash = visit(payload["right_child_id"])
                self.assertEqual(
                    payload["left_child_semantic_sha256"], left_hash
                )
                self.assertEqual(
                    payload["right_child_semantic_sha256"], right_hash
                )
            expected = solver._node_hash(node)
            self.assertEqual(node["node_semantic_sha256"], expected)
            return expected

        visit("r")
        self.assertEqual(preorder, [node["node_id"] for node in nodes])

    def test_stored_certificate_and_report_replay(self) -> None:
        stored_certificate = solver.strict_json_load(
            solver.DEFAULT_CERTIFICATE
        )
        stored_report = solver.strict_json_load(solver.DEFAULT_REPORT)
        solver.verify_certificate(stored_certificate)
        solver.verify_report(stored_report, stored_certificate)


class ReservedBudgetControls(unittest.TestCase):
    def test_small_odd_budgets_end_in_typed_unresolved_leaves(self) -> None:
        for budget in (1, 3, 5, 7, 9, 15, 31, 63):
            with self.subTest(budget=budget):
                certificate = solver.build_certificate(
                    max_nodes=budget, max_depth=48
                )
                summary = certificate["summary"]
                self.assertLessEqual(summary["node_count"], budget)
                self.assertEqual(summary["node_count"] % 2, 1)
                self.assertEqual(
                    summary["node_count"],
                    2 * summary["split_nodes"] + 1,
                )
                self.assertGreater(summary["unresolved_leaves"], 0)
                self.assertEqual(
                    certificate["outcome"]["type"],
                    "finite_window_cover_unresolved",
                )
                unresolved = [
                    node
                    for node in certificate["tree"]["nodes"]
                    if node["node_kind"] == "leaf"
                    and node["payload"]["witness"]["witness_type"]
                    == "unresolved"
                ]
                self.assertEqual(
                    len(unresolved), summary["unresolved_leaves"]
                )
                for node in unresolved:
                    self.assertIn(
                        node["payload"]["witness"]["reason"],
                        {
                            "node_budget_exhausted",
                            "maximum_depth_exhausted",
                        },
                    )

    def test_budget_five_and_seven_do_not_raise_internal_errors(self) -> None:
        for budget in (5, 7):
            certificate = solver.build_certificate(max_nodes=budget)
            self.assertGreater(
                certificate["summary"]["unresolved_leaves"], 0
            )

    def test_depth_zero_is_a_typed_unresolved_root(self) -> None:
        certificate = solver.build_certificate(
            max_nodes=4095, max_depth=0
        )
        self.assertEqual(certificate["summary"]["node_count"], 1)
        witness = certificate["tree"]["nodes"][0]["payload"]["witness"]
        self.assertEqual(witness["witness_type"], "unresolved")
        self.assertEqual(witness["reason"], "maximum_depth_exhausted")

    def test_invalid_budgets_are_rejected(self) -> None:
        for budget in (0, 2, 4, True):
            with self.assertRaises(solver.SymbolicNoEntryError):
                solver.build_certificate(max_nodes=budget)
        with self.assertRaises(solver.SymbolicNoEntryError):
            solver.build_certificate(max_depth=-1)


class HostileCertificateControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.original = solver.build_certificate()

    def assert_rejected(
        self,
        mutator: Callable[[dict[str, Any]], None],
    ) -> None:
        hostile = copy.deepcopy(self.original)
        mutator(hostile)
        solver.reseal_certificate_hashes(hostile)
        with self.assertRaises(solver.SymbolicNoEntryError):
            solver.verify_certificate(hostile)

    def test_deleted_leaf_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value["tree"]["nodes"].remove(first_leaf(value))
        )

    def test_changed_leaf_box_is_rejected_after_resealing(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            interval = first_leaf(value)["box"]["intervals"][0]
            lower = solver.dyadic_fraction(interval["lower"])
            upper = solver.dyadic_fraction(interval["upper"])
            interval["upper"] = solver.dyadic_json((lower + upper) / 2)

        self.assert_rejected(mutate)

    def test_changed_axis_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: first_leaf(value)["payload"]["witness"].__setitem__(
                "axis", 8
            )
        )

    def test_changed_period_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: first_leaf(value)["payload"]["witness"].__setitem__(
                "period", solver.dyadic_json(16)
            )
        )

    def test_changed_radius_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: first_leaf(value)["payload"]["witness"].__setitem__(
                "radius", solver.dyadic_json(Fraction(1, 4))
            )
        )

    def test_fabricated_arb_interval_is_rejected_after_resealing(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            endpoint = first_leaf(value)["payload"]["witness"][
                "d_enclosure"
            ]["hi"]
            endpoint["numerator"] += 2

        self.assert_rejected(mutate)

    def test_changed_split_is_rejected_after_resealing(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            root = value["tree"]["nodes"][0]
            root["payload"]["split_axis"] = "u2"

        self.assert_rejected(mutate)

    def test_changed_closure_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: first_leaf(value)["box"]["intervals"][
                0
            ].__setitem__("upper_closed", True)
        )

    def test_wrong_outcome_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value["outcome"].__setitem__("type", "first_entry")
        )

    def test_false_quotient_scope_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value["outcome"].__setitem__(
                "exact_worldsheet_quotient_claimed", False
            )
        )

    def test_winding_dependency_claim_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value["outcome"].__setitem__(
                "winding_metric_used", True
            )
        )

    def test_registry_axis_expansion_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value["solver_registry"][
                "proof_target_axis_order"
            ].append(8)
        )

    def test_problem_hash_substitution_is_rejected_after_resealing(self) -> None:
        self.assert_rejected(
            lambda value: value.__setitem__(
                "closed_string_problem_semantic_sha256",
                "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca",
            )
        )

    def test_tree_reordering_is_rejected_after_resealing(self) -> None:
        def mutate(value: dict[str, Any]) -> None:
            value["tree"]["nodes"][1:3] = reversed(
                value["tree"]["nodes"][1:3]
            )

        self.assert_rejected(mutate)

    def test_false_self_hash_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.original)
        hostile["certificate_semantic_sha256"] = "0" * 64
        with self.assertRaises(solver.SymbolicNoEntryError):
            solver.verify_certificate(hostile)


if __name__ == "__main__":
    unittest.main()
