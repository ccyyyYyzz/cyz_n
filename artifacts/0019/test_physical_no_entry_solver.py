from __future__ import annotations

import copy
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

import physical_no_entry_solver as solver


class PhysicalNoEntrySolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = solver.build_certificate()
        cls.report = solver.build_report(cls.certificate)

    def assertReplayRejects(self, value: dict) -> None:
        with self.assertRaises(solver.NoEntryError):
            solver.verify_certificate(value)

    def test_real_index2_cover_closes_without_unresolved(self) -> None:
        replay = solver.verify_certificate(self.certificate)
        self.assertEqual(replay["physical_problem_semantic_sha256"],
                         solver.PHYSICAL_PROBLEM_SEMANTIC_SHA256)
        self.assertEqual(replay["solver_registry_semantic_sha256"],
                         solver.SOLVER_REGISTRY_SEMANTIC_SHA256)
        self.assertEqual(replay["node_count"], 179)
        self.assertEqual(replay["split_nodes"], 89)
        self.assertEqual(replay["excluded_leaves"], 90)
        self.assertEqual(replay["unresolved_leaves"], 0)
        self.assertEqual(replay["maximum_depth"], 9)
        self.assertEqual(replay["outcome"], "right_censored_no_entry")

    def test_scope_is_finite_half_open_window_not_all_time_or_seam(self) -> None:
        outcome = self.certificate["outcome"]
        self.assertEqual(
            outcome["scope"], "registered_finite_half_open_window_only"
        )
        self.assertIs(outcome["all_time_no_entry_claimed"], False)
        self.assertIs(outcome["exact_seam_equivalence_claimed"], False)
        self.assertIs(self.report["claims"]["all_time_no_entry"], False)
        self.assertIs(
            self.report["claims"]["exact_worldsheet_seam_equivalence"],
            False,
        )

    def test_every_leaf_has_strict_exact_dyadic_empty_range(self) -> None:
        leaves = [
            node
            for node in self.certificate["tree"]["nodes"]
            if node["node_kind"] == "leaf"
        ]
        self.assertEqual(len(leaves), 90)
        for node in leaves:
            witness = node["payload"]["witness"]
            self.assertEqual(
                witness["witness_type"], "empty_coordinate_image_range"
            )
            self.assertIn(witness["axis"], range(9))
            self.assertGreater(witness["nmin"], witness["nmax"])
            lower = solver.dyadic_fraction(witness["d_enclosure"]["lo"])
            upper = solver.dyadic_fraction(witness["d_enclosure"]["hi"])
            period = solver.dyadic_fraction(witness["period"])
            radius = solver.dyadic_fraction(witness["radius"])
            self.assertLessEqual(lower, upper)
            self.assertEqual(
                witness["nmin"],
                solver.ceil_fraction((lower - radius) / period),
            )
            self.assertEqual(
                witness["nmax"],
                solver.floor_fraction((upper + radius) / period),
            )
            margins = witness["margins"]
            above = solver.dyadic_fraction(
                margins["above_previous_image"]
            )
            below = solver.dyadic_fraction(margins["below_next_image"])
            minimum = solver.dyadic_fraction(margins["minimum"])
            self.assertGreater(above, 0)
            self.assertGreater(below, 0)
            self.assertEqual(minimum, min(above, below))

    def test_half_open_tree_has_gap_free_endpoint_ownership(self) -> None:
        nodes = {
            node["node_id"]: node
            for node in self.certificate["tree"]["nodes"]
        }
        root = nodes["r"]
        for interval in root["box"]["intervals"]:
            self.assertIs(interval["lower_closed"], True)
            self.assertIs(interval["upper_closed"], False)
        for node in nodes.values():
            if node["node_kind"] != "split":
                continue
            payload = node["payload"]
            left = nodes[payload["left_child_id"]]
            right = nodes[payload["right_child_id"]]
            solver._validate_split(
                node["box"],
                left["box"],
                right["box"],
                payload["split_axis"],
                payload["split_point"],
            )
            self.assertEqual(left["parent_id"], node["node_id"])
            self.assertEqual(right["parent_id"], node["node_id"])

    def test_touching_radius_boundary_is_not_excluded(self) -> None:
        # d=8.5 is exactly r_out=0.5 from the n=1 image at L=8.
        witness = solver.build_empty_coordinate_image_range(
            axis=0,
            d_enclosure={
                "lo": solver.dyadic_json(Fraction(17, 2)),
                "hi": solver.dyadic_json(Fraction(17, 2)),
            },
            period=solver.dyadic_json(8),
            radius=solver.dyadic_json(Fraction(1, 2)),
        )
        self.assertIsNone(witness)
        strict = solver.build_empty_coordinate_image_range(
            axis=0,
            d_enclosure={
                "lo": solver.dyadic_json(Fraction(35, 4)),
                "hi": solver.dyadic_json(Fraction(35, 4)),
            },
            period=solver.dyadic_json(8),
            radius=solver.dyadic_json(Fraction(1, 2)),
        )
        self.assertIsNotNone(strict)

    def test_budget_exhaustion_is_typed_and_forbids_success_outcome(self) -> None:
        certificate = solver.build_certificate(max_nodes=1, max_depth=0)
        self.assertEqual(certificate["summary"]["node_count"], 1)
        self.assertEqual(certificate["summary"]["unresolved_leaves"], 1)
        self.assertEqual(
            certificate["tree"]["nodes"][0]["payload"]["witness"][
                "witness_type"
            ],
            "unresolved",
        )
        self.assertEqual(
            certificate["outcome"]["type"],
            "finite_window_cover_unresolved",
        )

    def test_small_budgets_reserve_pending_right_siblings(self) -> None:
        for max_nodes in (3, 5, 7):
            for max_depth in (0, 1, 2, 48):
                with self.subTest(
                    max_nodes=max_nodes, max_depth=max_depth
                ):
                    certificate = solver.build_certificate(
                        max_nodes=max_nodes, max_depth=max_depth
                    )
                    nodes = certificate["tree"]["nodes"]
                    summary = certificate["summary"]
                    self.assertLessEqual(len(nodes), max_nodes)
                    self.assertEqual(summary["node_count"], len(nodes))
                    self.assertEqual(
                        summary["node_count"],
                        2 * summary["split_nodes"] + 1,
                    )
                    self.assertEqual(
                        summary["leaf_count"],
                        summary["split_nodes"] + 1,
                    )
                    self.assertGreater(summary["unresolved_leaves"], 0)
                    self.assertEqual(
                        certificate["outcome"]["type"],
                        "finite_window_cover_unresolved",
                    )

                    by_id = {node["node_id"]: node for node in nodes}
                    self.assertEqual(len(by_id), len(nodes))
                    for node in nodes:
                        if node["node_kind"] == "split":
                            payload = node["payload"]
                            left = by_id[payload["left_child_id"]]
                            right = by_id[payload["right_child_id"]]
                            solver._validate_split(
                                node["box"],
                                left["box"],
                                right["box"],
                                payload["split_axis"],
                                payload["split_point"],
                            )
                            continue
                        witness = node["payload"]["witness"]
                        self.assertIn(
                            witness["witness_type"],
                            {
                                "empty_coordinate_image_range",
                                "unresolved",
                            },
                        )

    def test_deleted_and_rewired_subtree_fails_after_hash_reseal(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        root = hostile["tree"]["nodes"][0]
        removed_id = root["payload"]["right_child_id"]
        kept_id = root["payload"]["left_child_id"]
        hostile["tree"]["nodes"] = [
            node
            for node in hostile["tree"]["nodes"]
            if not (
                node["node_id"] == removed_id
                or node["node_id"].startswith(removed_id + "L")
                or node["node_id"].startswith(removed_id + "R")
            )
        ]
        root["payload"]["right_child_id"] = kept_id
        solver.reseal_certificate_hashes(hostile)
        self.assertReplayRejects(hostile)

    def test_overlap_fails_after_hash_reseal(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        nodes = {node["node_id"]: node for node in hostile["tree"]["nodes"]}
        root = nodes["r"]
        right = nodes[root["payload"]["right_child_id"]]
        split_axis = solver.DOMAIN_AXES.index(
            root["payload"]["split_axis"]
        )
        right["box"]["intervals"][split_axis]["lower"] = copy.deepcopy(
            root["box"]["intervals"][split_axis]["lower"]
        )
        solver.reseal_certificate_hashes(hostile)
        self.assertReplayRejects(hostile)

    def test_forged_arb_endpoint_and_floor_ceil_fail_after_reseal(self) -> None:
        for mutation in ("endpoint", "nmin"):
            hostile = copy.deepcopy(self.certificate)
            leaf = next(
                node
                for node in hostile["tree"]["nodes"]
                if node["node_kind"] == "leaf"
            )
            witness = leaf["payload"]["witness"]
            if mutation == "endpoint":
                endpoint = witness["d_enclosure"]["lo"]
                endpoint["numerator"] += 2
            else:
                witness["nmin"] += 1
            solver.reseal_certificate_hashes(hostile)
            self.assertReplayRejects(hostile)

    def test_forged_axis_period_radius_and_margin_fail_after_reseal(self) -> None:
        for mutation in ("axis", "period", "radius", "margin"):
            hostile = copy.deepcopy(self.certificate)
            leaf = next(
                node
                for node in hostile["tree"]["nodes"]
                if node["node_kind"] == "leaf"
            )
            witness = leaf["payload"]["witness"]
            if mutation == "axis":
                witness["axis"] = (witness["axis"] + 1) % 9
            elif mutation == "period":
                witness["period"] = solver.dyadic_json(16)
            elif mutation == "radius":
                witness["radius"] = solver.dyadic_json(Fraction(1, 4))
            else:
                witness["margins"]["minimum"]["numerator"] += 2
            solver.reseal_certificate_hashes(hostile)
            self.assertReplayRejects(hostile)

    def test_hash_resealed_outcome_upgrade_is_rejected(self) -> None:
        hostile = copy.deepcopy(self.certificate)
        hostile["outcome"]["all_time_no_entry_claimed"] = True
        hostile["outcome"]["exact_seam_equivalence_claimed"] = True
        solver.reseal_certificate_hashes(hostile)
        self.assertReplayRejects(hostile)

    def test_solver_registry_and_problem_hash_are_code_pinned(self) -> None:
        for path in ("registry", "problem"):
            hostile = copy.deepcopy(self.certificate)
            if path == "registry":
                hostile["solver_registry"]["budgets"]["max_depth"] += 1
            else:
                hostile["physical_problem_semantic_sha256"] = "0" * 64
            solver.reseal_certificate_hashes(hostile)
            self.assertReplayRejects(hostile)

    def test_report_replays_exactly(self) -> None:
        self.assertEqual(
            solver.verify_report(self.report, self.certificate), self.report
        )
        hostile = copy.deepcopy(self.report)
        hostile["claims"]["all_time_no_entry"] = True
        with self.assertRaises(solver.NoEntryError):
            solver.verify_report(hostile, self.certificate)

    def test_cli_write_then_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            certificate_path = Path(directory) / "certificate.json"
            report_path = Path(directory) / "report.json"
            self.assertEqual(
                solver.main(
                    [
                        "--write",
                        "--certificate",
                        str(certificate_path),
                        "--report",
                        str(report_path),
                    ]
                ),
                0,
            )
            self.assertEqual(
                solver.main(
                    [
                        "--check",
                        "--certificate",
                        str(certificate_path),
                        "--report",
                        str(report_path),
                    ]
                ),
                0,
            )


if __name__ == "__main__":
    unittest.main()
