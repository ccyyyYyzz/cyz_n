#!/usr/bin/env python3
"""Hostile replay tests for the Brief 0018 coverage proof artifact."""

from __future__ import annotations

import copy
import unittest
from fractions import Fraction

import coverage_proof as proof


class CoverageProofHostileTests(unittest.TestCase):
    """Exercise proof replay, not merely JSON shape or declared hashes."""

    def assert_replay_rejected(self, certificate: dict) -> None:
        with self.assertRaises(proof.ProofError):
            proof.validate_coverage_certificate(certificate)

    @staticmethod
    def rehash(certificate: dict) -> dict:
        proof.recompute_manifest_hash(certificate)
        return certificate

    def test_baseline_exact_fixtures_replay(self) -> None:
        fixtures = (
            proof.build_coverage_certificate(),
            proof.build_coverage_certificate(no_entry=True),
            proof.build_mixed_unresolved_certificate(),
            proof.build_seam_duplicate_certificate(),
            proof.build_singular_cluster_certificate(),
        )
        for certificate in fixtures:
            with self.subTest(certificate=certificate["certificate_id"]):
                self.assertIs(
                    proof.validate_coverage_certificate(certificate),
                    certificate,
                )

    # Brief 0018 test 25.
    def test_unique_root_without_inclusion_witness_is_rejected(self) -> None:
        certificate = proof.build_coverage_certificate()
        root_leaf = next(
            leaf
            for leaf in certificate["manifest"]["leaves"]
            if leaf["classification"] == "unique_root"
        )
        del root_leaf["witness"]
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

    def test_fake_inclusion_witnesses_are_rejected(self) -> None:
        mutations = {}

        wrong_type = proof.build_coverage_certificate()
        root_leaf = next(
            leaf
            for leaf in wrong_type["manifest"]["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_leaf["witness"]["type"] = "interval_exclusion"
        mutations["wrong witness type"] = wrong_type

        determinant_contains_zero = proof.build_coverage_certificate()
        root_leaf = next(
            leaf
            for leaf in determinant_contains_zero["manifest"]["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_leaf["witness"]["determinant_range"] = proof.exact_interval(-1, 1)
        mutations["determinant interval contains zero"] = (
            determinant_contains_zero
        )

        operator_not_interior = proof.build_coverage_certificate()
        manifest = operator_not_interior["manifest"]
        root_leaf = next(
            leaf
            for leaf in manifest["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_node = next(
            node
            for node in manifest["nodes"]
            if node["node_id"] == root_leaf["node_id"]
        )
        root_leaf["witness"]["operator_box"] = copy.deepcopy(root_node["box"])
        mutations["K(B) is not strictly inside B"] = operator_not_interior

        candidate_binding_mismatch = proof.build_coverage_certificate()
        root_leaf = next(
            leaf
            for leaf in candidate_binding_mismatch["manifest"]["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_leaf["witness"]["candidate_id"] = "candidate-not-recorded"
        mutations["witness candidate is not recorded"] = (
            candidate_binding_mismatch
        )

        candidate_outside_operator = proof.build_coverage_certificate()
        candidate_outside_operator["manifest"]["candidates"][0][
            "time_interval"
        ] = proof.exact_interval(Fraction(15, 16), Fraction(15, 16))
        mutations["candidate outside inclusion operator"] = (
            candidate_outside_operator
        )

        for label, certificate in mutations.items():
            with self.subTest(label=label):
                self.rehash(certificate)
                self.assert_replay_rejected(certificate)

        wrong_candidate_time = proof.build_coverage_certificate()
        wrong_candidate_time["manifest"]["candidates"][0][
            "time_interval"
        ] = proof.exact_interval(Fraction(11, 16), Fraction(11, 16))
        self.rehash(wrong_candidate_time)
        self.assert_replay_rejected(wrong_candidate_time)

    def test_leaf_ranges_replay_from_exact_affine_content(self) -> None:
        exclusion = proof.build_coverage_certificate()
        excluded_leaf = next(
            leaf
            for leaf in exclusion["manifest"]["leaves"]
            if leaf["classification"] == "excluded"
        )
        excluded_leaf["witness"]["range"] = proof.exact_interval(2, 2)
        self.rehash(exclusion)
        self.assert_replay_rejected(exclusion)

        inclusion = proof.build_coverage_certificate()
        root_leaf = next(
            leaf
            for leaf in inclusion["manifest"]["leaves"]
            if leaf["classification"] == "unique_root"
        )
        root_leaf["witness"]["root_model"]["root"][2] = proof.dyadic(
            13, 4
        )
        self.rehash(inclusion)
        self.assert_replay_rejected(inclusion)

    def test_singular_set_hash_rank_and_parameterization_replay(self) -> None:
        wrong_rank = proof.build_singular_cluster_certificate()
        leaf = next(
            leaf
            for leaf in wrong_rank["manifest"]["leaves"]
            if leaf["classification"] == "certified_singular_cluster"
        )
        leaf["witness"]["affine_set"]["declared_rank"] = 1
        leaf["witness"]["set_certificate_sha256"] = proof.canonical_sha256(
            leaf["witness"]["affine_set"]
        )
        self.rehash(wrong_rank)
        self.assert_replay_rejected(wrong_rank)

        false_null = proof.build_singular_cluster_certificate()
        leaf = next(
            leaf
            for leaf in false_null["manifest"]["leaves"]
            if leaf["classification"] == "certified_singular_cluster"
        )
        leaf["witness"]["affine_set"]["null_direction"][1] = proof.dyadic(1)
        leaf["witness"]["set_certificate_sha256"] = proof.canonical_sha256(
            leaf["witness"]["affine_set"]
        )
        self.rehash(false_null)
        self.assert_replay_rejected(false_null)

    # Brief 0018 test 25.
    def test_missing_image_manifest_is_rejected_after_rehash(self) -> None:
        certificate = proof.build_coverage_certificate()
        certificate["manifest"]["images"].clear()
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

    def test_exact_input_commitment_rejects_domain_or_hash_reauthoring(
        self,
    ) -> None:
        certificate = proof.build_coverage_certificate()
        certificate["manifest"]["exact_inputs_sha256"] = "f" * 64
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

        certificate = proof.build_coverage_certificate(
            (
                (
                    "candidate-a",
                    "physical-root-a",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
                (
                    "candidate-b",
                    "physical-root-b",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
            )
        )
        manifest = certificate["manifest"]
        for key in ("initial_domains", "images"):
            manifest[key].pop()
        manifest["nodes"] = [
            row for row in manifest["nodes"] if row["domain_id"] != "domain-1"
        ]
        manifest["leaves"] = [
            row for row in manifest["leaves"] if row["domain_id"] != "domain-1"
        ]
        manifest["candidates"] = [
            row
            for row in manifest["candidates"]
            if row["candidate_id"] != "candidate-b"
        ]
        manifest["quotient_classes"] = [
            row
            for row in manifest["quotient_classes"]
            if row["physical_root_id"] != "physical-root-b"
        ]
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

    def test_unique_leaves_and_candidates_are_one_to_one(self) -> None:
        certificate = proof.build_coverage_certificate(
            (
                (
                    "candidate-a",
                    "physical-root-a",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
                (
                    "candidate-b",
                    "physical-root-b",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
            )
        )
        second_leaf = next(
            leaf
            for leaf in certificate["manifest"]["leaves"]
            if leaf["leaf_id"] == "leaf-1-root"
        )
        second_leaf["witness"]["candidate_id"] = "candidate-a"
        certificate["manifest"]["candidates"] = [
            row
            for row in certificate["manifest"]["candidates"]
            if row["candidate_id"] != "candidate-b"
        ]
        certificate["manifest"]["quotient_classes"] = [
            row
            for row in certificate["manifest"]["quotient_classes"]
            if row["physical_root_id"] != "physical-root-b"
        ]
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

    # Brief 0018 test 25.
    def test_gap_free_tree_break_is_rejected_after_rehash(self) -> None:
        certificate = proof.build_coverage_certificate()
        left = next(
            node
            for node in certificate["manifest"]["nodes"]
            if node["node_id"] == "node-0-left"
        )
        left["box"]["time"]["hi"] = proof.dyadic(3, 3)
        self.rehash(certificate)
        self.assert_replay_rejected(certificate)

    # Brief 0018 test 30: the event layer consumes this replayed signal and
    # must force numerical_unresolved whenever it is nonempty.
    def test_event_order_relevant_unresolved_leaf_is_exposed(self) -> None:
        certificate = proof.build_mixed_unresolved_certificate()
        self.assertEqual(
            proof.unresolved_leaf_ids(certificate),
            ["leaf-1-unresolved"],
        )
        self.assertEqual(
            proof.unresolved_leaf_ids(
                certificate,
                event_order_relevant_only=True,
            ),
            ["leaf-1-unresolved"],
        )
        self.assertEqual(
            proof.physical_representative_candidate_ids(certificate),
            ["candidate-0"],
        )

        irrelevant = copy.deepcopy(certificate)
        unresolved_leaf = next(
            leaf
            for leaf in irrelevant["manifest"]["leaves"]
            if leaf["classification"] == "unresolved"
        )
        unresolved_leaf["witness"]["event_order_relevant"] = False
        self.rehash(irrelevant)
        proof.validate_coverage_certificate(irrelevant)
        self.assertEqual(
            proof.unresolved_leaf_ids(
                irrelevant,
                event_order_relevant_only=True,
            ),
            [],
        )
        self.assertEqual(
            proof.unresolved_leaf_ids(irrelevant),
            ["leaf-1-unresolved"],
        )

    # Brief 0018 test 31.
    def test_seam_duplicates_are_quotiented_exactly_once(self) -> None:
        certificate = proof.build_seam_duplicate_certificate()
        proof.validate_coverage_certificate(certificate)
        self.assertEqual(certificate["candidate_count"], 2)
        self.assertEqual(certificate["physical_root_count"], 1)
        self.assertEqual(
            proof.physical_representative_candidate_ids(certificate),
            ["candidate-seam-a"],
        )
        quotient = certificate["manifest"]["quotient_classes"][0]
        self.assertEqual(
            set(quotient["candidate_ids"]),
            {"candidate-seam-a", "candidate-seam-b"},
        )
        self.assertEqual(quotient["proof_type"], "seam_equivalence")

    # Brief 0018 test 31.
    def test_two_distinct_simultaneous_roots_remain_two_classes(self) -> None:
        same_time = (Fraction(3, 4), Fraction(3, 4))
        certificate = proof.build_coverage_certificate(
            (
                ("candidate-a", "physical-root-a", same_time),
                ("candidate-b", "physical-root-b", same_time),
            )
        )
        proof.validate_coverage_certificate(certificate)
        self.assertEqual(certificate["candidate_count"], 2)
        self.assertEqual(certificate["physical_root_count"], 2)
        self.assertEqual(
            proof.physical_representative_candidate_ids(certificate),
            ["candidate-a", "candidate-b"],
        )

        falsely_merged = copy.deepcopy(certificate)
        candidates = falsely_merged["manifest"]["candidates"]
        candidates[1]["physical_root_id"] = "physical-root-a"
        quotients = falsely_merged["manifest"]["quotient_classes"]
        quotients[1]["physical_root_id"] = "physical-root-a"
        self.rehash(falsely_merged)
        self.assert_replay_rejected(falsely_merged)

    def test_fake_seam_equivalence_is_rejected(self) -> None:
        wrong_delta = proof.build_seam_duplicate_certificate()
        binding = wrong_delta["manifest"]["quotient_classes"][0][
            "seam_proof"
        ]["lattice_delta_bindings"][1]
        binding["lattice_delta"] = [0] * 9
        self.rehash(wrong_delta)
        self.assert_replay_rejected(wrong_delta)

        duplicate_binding = proof.build_seam_duplicate_certificate()
        bindings = duplicate_binding["manifest"]["quotient_classes"][0][
            "seam_proof"
        ]["lattice_delta_bindings"]
        bindings[1]["candidate_id"] = bindings[0]["candidate_id"]
        self.rehash(duplicate_binding)
        self.assert_replay_rejected(duplicate_binding)

        different_root = proof.build_seam_duplicate_certificate()
        second_leaf = next(
            leaf
            for leaf in different_root["manifest"]["leaves"]
            if leaf["leaf_id"] == "leaf-1-root"
        )
        second_leaf["witness"]["root_model"]["root"][2] = proof.dyadic(
            13, 4
        )
        second_leaf["witness"]["root_model"]["constant"][2] = (
            proof.dyadic(13, 4)
        )
        different_root["manifest"]["candidates"][1]["time_interval"] = (
            proof.exact_interval(Fraction(13, 16), Fraction(13, 16))
        )
        self.rehash(different_root)
        self.assert_replay_rejected(different_root)

    # Brief 0018 test 32.
    def test_deleted_leaf_fails_even_after_hashes_and_counts_recomputed(
        self,
    ) -> None:
        baseline = proof.build_coverage_certificate()
        hostile = proof.deleted_leaf_mutation(baseline)
        self.assertEqual(
            hostile["manifest_sha256"],
            proof.canonical_sha256(hostile["manifest"]),
        )
        recomputed_leaf_total = sum(hostile["leaf_counts"].values())
        self.assertEqual(
            recomputed_leaf_total,
            len(hostile["manifest"]["leaves"]),
        )
        self.assert_replay_rejected(hostile)

    def test_duplicate_identifiers_are_rejected_after_rehash(self) -> None:
        mutations = {}

        duplicate_image = proof.build_seam_duplicate_certificate()
        duplicate_image["manifest"]["images"][1]["image_id"] = "image-0"
        mutations["image"] = duplicate_image

        duplicate_domain = proof.build_seam_duplicate_certificate()
        duplicate_domain["manifest"]["initial_domains"][1][
            "domain_id"
        ] = "domain-0"
        mutations["domain"] = duplicate_domain

        duplicate_node = proof.build_coverage_certificate()
        duplicate_node["manifest"]["nodes"].append(
            copy.deepcopy(duplicate_node["manifest"]["nodes"][0])
        )
        mutations["node"] = duplicate_node

        duplicate_leaf = proof.build_coverage_certificate()
        duplicate_leaf["manifest"]["leaves"].append(
            copy.deepcopy(duplicate_leaf["manifest"]["leaves"][0])
        )
        mutations["leaf"] = duplicate_leaf

        duplicate_candidate = proof.build_seam_duplicate_certificate()
        duplicate_candidate["manifest"]["candidates"].append(
            copy.deepcopy(duplicate_candidate["manifest"]["candidates"][0])
        )
        mutations["candidate"] = duplicate_candidate

        duplicate_quotient_candidate = (
            proof.build_seam_duplicate_certificate()
        )
        duplicate_quotient_candidate["manifest"]["quotient_classes"][0][
            "candidate_ids"
        ].append("candidate-seam-a")
        mutations["candidate within quotient"] = (
            duplicate_quotient_candidate
        )

        duplicate_physical_root = proof.build_coverage_certificate(
            (
                (
                    "candidate-a",
                    "physical-root-a",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
                (
                    "candidate-b",
                    "physical-root-b",
                    (Fraction(3, 4), Fraction(3, 4)),
                ),
            )
        )
        duplicate_physical_root["manifest"]["quotient_classes"][1][
            "physical_root_id"
        ] = "physical-root-a"
        duplicate_physical_root["manifest"]["candidates"][1][
            "physical_root_id"
        ] = "physical-root-a"
        mutations["physical root class"] = duplicate_physical_root

        for label, certificate in mutations.items():
            with self.subTest(identifier=label):
                self.rehash(certificate)
                self.assert_replay_rejected(certificate)

    def test_declared_count_tampering_is_rejected(self) -> None:
        count_fields = (
            "node_count",
            "image_count",
            "domain_count",
            "candidate_count",
            "physical_root_count",
        )
        for field in count_fields:
            with self.subTest(field=field):
                certificate = proof.build_coverage_certificate()
                certificate[field] += 1
                self.assert_replay_rejected(certificate)

        for leaf_class in proof.LEAF_CLASSES:
            with self.subTest(leaf_class=leaf_class):
                certificate = proof.build_coverage_certificate()
                certificate["leaf_counts"][leaf_class] += 1
                self.assert_replay_rejected(certificate)


if __name__ == "__main__":
    unittest.main(verbosity=2)
