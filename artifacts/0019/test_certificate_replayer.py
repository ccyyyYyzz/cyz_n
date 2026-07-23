#!/usr/bin/env python3
"""Independent-replayer and problem-commitment tests for Brief 0019."""

from __future__ import annotations

import ast
import copy
import json
import tempfile
import unittest
from pathlib import Path

import certificate_replayer as replayer
import certified_solver_core as core


def assert_gate(
    testcase: unittest.TestCase,
    bundle: object,
    expected_gate: str,
) -> None:
    with testcase.assertRaises(replayer.CertificateReplayError) as caught:
        replayer.replay_bundle(bundle)
    testcase.assertEqual(caught.exception.gate, expected_gate)


class SourceSeparationTests(unittest.TestCase):
    def test_replayer_has_no_project_import_or_dynamic_execution(self) -> None:
        source = replayer.__file__
        self.assertIsNotNone(source)
        tree = ast.parse(Path(source).read_text(encoding="utf-8"))
        forbidden_modules = {
            "certified_solver_core",
            "arb_interval_jets",
            "arb_krawczyk_control",
            "importlib",
            "pickle",
            "shelve",
            "marshal",
            "functools",
        }
        imported: set[str] = set()
        called: set[str] = set()
        decorators: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    called.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    called.add(node.func.attr)
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.add(decorator.id)
                    elif isinstance(decorator, ast.Attribute):
                        decorators.add(decorator.attr)
        self.assertTrue(forbidden_modules.isdisjoint(imported))
        self.assertTrue({"exec", "eval", "__import__"}.isdisjoint(called))
        self.assertTrue(
            {"cache", "lru_cache", "cached_property"}.isdisjoint(decorators)
        )

    def test_independent_types_are_not_generator_types(self) -> None:
        self.assertIsNot(replayer.Dyadic, core.Dyadic)
        self.assertIsNot(replayer.Interval, core.DyadicInterval)
        self.assertIsNot(
            replayer.CertificateReplayError, core.CertificateError
        )


class PositiveReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = core.build_foundation_fixture()

    def test_two_replayers_return_type_strict_same_summary(self) -> None:
        generated = core.replay_bundle(self.fixture)
        independent = replayer.replay_bundle(self.fixture)
        self.assertTrue(core.type_strict_equal(generated, independent))
        self.assertEqual(
            generated["bundle_semantic_sha256"],
            independent["bundle_semantic_sha256"],
        )
        self.assertEqual(
            independent["problem_registry_canonical_sha256"],
            replayer.PROBLEM_REGISTRY_CANONICAL_SHA256,
        )

    def test_external_registry_is_fixed_by_code_sha(self) -> None:
        registry = replayer.load_problem_registry()
        self.assertEqual(
            replayer.canonical_sha256(registry),
            replayer.PROBLEM_REGISTRY_CANONICAL_SHA256,
        )
        mutation = copy.deepcopy(registry)
        mutation["function_registry"]["functions"][0]["intercept"] = {
            "numerator": -3,
            "exponent": 1,
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "rewritten_registry.json"
            path.write_text(
                json.dumps(mutation, sort_keys=True),
                encoding="utf-8",
                newline="\n",
            )
            with self.assertRaises(
                replayer.CertificateReplayError
            ) as caught:
                replayer.load_problem_registry(path)
        self.assertEqual(caught.exception.gate, "problem_commitment")


class HostileReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = core.build_foundation_fixture()

    def test_deleted_leaf_and_refreshed_ordinary_hashes_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        removed_root = mutation["initial_cover"]["root_ids"].pop()
        mutation["initial_cover"]["nodes"] = [
            node
            for node in mutation["initial_cover"]["nodes"]
            if node["node_id"] != removed_root
        ]
        mutation = core.refresh_declared_hashes(mutation)
        self.assertEqual(
            mutation["initial_cover"]["cover_hash"],
            core._cover_hash(mutation["initial_cover"]),
        )
        assert_gate(self, mutation, "cover_image_binding")

    def test_replaced_root_system_and_location_cannot_self_commit(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        entry = mutation["function_registry"]["functions"][0]
        entry["slope"] = core.Dyadic.of(4).to_json()
        entry["intercept"] = core.Dyadic.of(-3, 1).to_json()
        replacement = core.AffineFunction(
            "affine_unique_root",
            core.Dyadic.of(4),
            core.Dyadic.of(-3, 1),
        )
        excluded = core._find_node(mutation, "leaf-0-0-excluded")
        unique = core._find_node(mutation, "leaf-0-0-unique")
        excluded_box = core.DyadicBox.from_json(excluded["box"])
        unique_box = core.DyadicBox.from_json(unique["box"])
        excluded["witness"] = core.build_excluded_range_witness(
            replacement, excluded_box
        )
        unique["witness"] = core.build_unique_root_witness(
            replacement, unique_box
        )
        self.assertEqual(
            core.Dyadic.from_json(unique["witness"]["krawczyk_image"]["lower"]),
            core.Dyadic.of(3, 3),
        )
        mutation = core.refresh_declared_hashes(mutation)
        self.assertEqual(
            mutation["initial_cover"]["cover_hash"],
            core._cover_hash(mutation["initial_cover"]),
        )
        assert_gate(self, mutation, "problem_commitment")

    def test_missing_image_is_rejected_by_complete_enumeration(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["image_enumeration"]["manifest"].pop(2)
        assert_gate(self, mutation, "image_enumeration")

    def test_fake_krawczyk_after_all_hash_refresh_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        unique = core._find_node(mutation, "leaf-0-0-unique")
        unique["witness"]["krawczyk_image"] = (
            core.DyadicInterval.closed(
                core.Dyadic.of(3, 3), core.Dyadic.of(5, 3)
            ).to_json()
        )
        mutation = core.refresh_declared_hashes(mutation)
        assert_gate(self, mutation, "unique_root_witness")

    def test_duplicate_node_identity_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["initial_cover"]["nodes"].append(
            copy.deepcopy(
                core._find_node(mutation, "leaf-0-0-excluded")
            )
        )
        mutation["initial_cover"]["cover_hash"] = core._cover_hash(
            mutation["initial_cover"]
        )
        assert_gate(self, mutation, "cover_ids")

    def test_duplicate_json_key_is_rejected_before_schema(self) -> None:
        with self.assertRaises(replayer.CertificateReplayError) as caught:
            replayer.strict_json_loads('{"schema_version":"a","x":1,"x":2}')
        self.assertEqual(caught.exception.gate, "strict_json")

    def test_nonfinite_and_float_tokens_are_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity", "0.5", "1e3"):
            with self.subTest(token=token):
                with self.assertRaises(
                    replayer.CertificateReplayError
                ) as caught:
                    replayer.strict_json_loads('{"x":' + token + "}")
                self.assertEqual(caught.exception.gate, "strict_json")

    def test_boolean_for_integer_type_substitution_is_rejected(self) -> None:
        mutation = copy.deepcopy(self.fixture)
        mutation["image_enumeration"]["manifest"][0][
            "lattice_vector"
        ][0] = True
        assert_gate(self, mutation, "image_enumeration")


class StoredArtifactTests(unittest.TestCase):
    def test_independent_check_replays_stored_fixture_and_report(self) -> None:
        result = replayer.check_artifacts()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["resolution"], "unresolved_present")


if __name__ == "__main__":
    unittest.main(verbosity=2)
