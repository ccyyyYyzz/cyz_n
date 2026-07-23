"""Hostile tests for the independent Brief 0018 source binding replay."""

from __future__ import annotations

import ast
import copy
import importlib.util
import json
import math
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ARTIFACT_DIR = Path(__file__).resolve().parent
MODULE_PATH = ARTIFACT_DIR / "source_binding_replayer.py"
SPEC = importlib.util.spec_from_file_location(
    "independent_source_binding_replayer", MODULE_PATH
)
assert SPEC is not None and SPEC.loader is not None
replayer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = replayer
SPEC.loader.exec_module(replayer)


class SourceBindingReplayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = replayer.strict_registry_load()
        cls.fixture = replayer.strict_fixture_load()
        cls.replay = replayer.replay_binding_objects(
            cls.registry, cls.fixture
        )

    def assert_gate(
        self,
        mutator: Callable[[dict[str, Any], dict[str, Any]], None],
        *accepted: str,
    ) -> None:
        registry = copy.deepcopy(self.registry)
        fixture = copy.deepcopy(self.fixture)
        mutator(registry, fixture)
        with self.assertRaises(replayer.BindingReplayError) as raised:
            replayer.replay_binding_objects(registry, fixture)
        self.assertIn(raised.exception.gate, accepted)

    def test_registry_source_draw_state_and_coefficient_commitments(self) -> None:
        self.assertEqual(
            self.replay["registry_canonical_sha256"],
            replayer.REGISTRY_CANONICAL_SHA256,
        )
        self.assertEqual(
            self.replay["source_draw_sha256"], replayer.SOURCE_DRAW_SHA256
        )
        rows = self.replay["source_rows"]
        self.assertEqual(
            [row["source_state_sha256"] for row in rows],
            [replayer.PINNED_STATE_SHA256[index] for index in range(3)],
        )
        self.assertEqual(
            [row["source_coefficient_payload_sha256"] for row in rows],
            [
                replayer.PINNED_COEFFICIENT_SHA256[index]
                for index in range(3)
            ],
        )

    def test_validity_diagnostics_and_least_status_rule(self) -> None:
        rows = self.replay["source_rows"]
        self.assertEqual(
            [row["validity_status"] for row in rows],
            ["source_invalid", "source_invalid", "valid"],
        )
        self.assertEqual(rows[0]["validity_reasons"], ["graph_upper_bound_exceeded"])
        self.assertEqual(rows[1]["validity_reasons"], ["graph_upper_bound_exceeded"])
        self.assertEqual(rows[2]["validity_reasons"], [])
        self.assertEqual(self.replay["first_source_invalid_index"], 0)
        self.assertEqual(self.replay["first_valid_index"], 2)
        for row in rows:
            self.assertEqual(
                replayer.parse_dyadic(row["k_max_times_ell_s"]),
                Fraction(1, 8),
            )
            residuals = row["exact_dyadic_constraint_residuals"]
            for value in (
                [residuals["energy_residual"]]
                + residuals["target_momentum_residual"]
                + residuals["worldsheet_momentum_residual"]
            ):
                self.assertLess(
                    abs(float(replayer.parse_dyadic(value))),
                    self.registry["audit"]["constraint_absolute_tolerance"],
                )

    def test_source_v2_q_orientation_wave_torus_and_f1_relations(self) -> None:
        state = replayer.independently_generate_source(self.registry, 2)
        self.assertEqual(state["schema_version"], replayer.SAMPLE_SCHEMA)
        self.assertEqual(state["relative_centre_gauge"], "Q2=0,Q1=Q_relative")
        self.assertEqual(state["Q1"], state["Q_relative"])
        self.assertEqual(state["Q2"], [0.0] * 8)
        self.assertEqual(
            [string["orientation"] for string in state["strings"]], [1, -1]
        )
        periods = self.registry["source_draw_registry"]["torus_periods_L_A"]
        for value, period in zip(state["Q_relative"], periods[:8]):
            self.assertTrue(0.0 < value < period)
        for string in state["strings"]:
            self.assertEqual(len(string["modes"]), 1)
            self.assertEqual(string["modes"][0]["wave_number"].hex(), (0.125).hex())
        source = self.registry["source_draw_registry"]
        self.assertEqual(
            source["winding_length"],
            source["winding_number_abs"]
            * source["torus_periods_L_A"][source["winding_axis"]],
        )
        self.assertEqual(
            source["string_tension"].hex(),
            (
                1.0
                / (
                    2.0
                    * replayer.PORTABLE_PI
                    * source["string_length_ell_s"] ** 2
                )
            ).hex(),
        )

    def test_binary64_hex_exact_dyadic_bijection_and_state_hash(self) -> None:
        for label in ("source_invalid_control", "valid_physical_control"):
            record = self.fixture["selected_source_states"][label]
            encoded = record["complete_serialized_source_state_binary64"]
            projected = record["complete_exact_dyadic_projection"]
            replayer.verify_binary64_dyadic_bijection(encoded, projected)
            state = replayer.decode_binary64_tree(encoded)
            core = {key: state[key] for key in replayer.SOURCE_CORE_KEYS}
            self.assertEqual(
                replayer.semantic_sha256(core), state["source_state_sha256"]
            )

    def test_physical_projection_contains_all_primitives_and_is_pinned(self) -> None:
        record = self.fixture["selected_source_states"]["valid_physical_control"]
        rebuilt = replayer.build_physical_problem_from_exact_state(
            record["complete_exact_dyadic_projection"], self.registry
        )
        self.assertTrue(
            replayer.type_strict_equal(rebuilt, self.fixture["physical_problem"])
        )
        self.assertEqual(
            replayer.semantic_sha256(rebuilt),
            "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca",
        )
        self.assertEqual(rebuilt["dimensions"]["target"], 9)
        self.assertEqual(rebuilt["dimensions"]["transverse"], 8)
        self.assertEqual(len(rebuilt["target_torus"]["G"]), 9)
        self.assertEqual(len(rebuilt["target_torus"]["Lambda"]), 9)
        self.assertEqual(len(rebuilt["kinematics"]["strings"]), 2)
        for string in rebuilt["kinematics"]["strings"]:
            self.assertEqual(len(string["transverse_velocity"]), 8)
            self.assertEqual(len(string["modes"]), 1)
            mode = string["modes"][0]
            for field in ("initial_x", "initial_y", "initial_p", "initial_q"):
                self.assertEqual(len(mode[field]), 8)

    def test_rank_normal_response_reaction_inputs_are_rejected(self) -> None:
        for key, value in (
            ("rank", 2),
            ("normal", [1]),
            ("normal_dimension", 7),
            ("response_rank", 2),
            ("response_winner", "string-1"),
            ("reaction", {"scale": 1}),
            ("reaction_scale", {"exponent": 0, "numerator": 1}),
        ):
            with self.subTest(key=key):
                self.assert_gate(
                    lambda _registry, fixture, key=key, value=value: fixture[
                        "physical_problem"
                    ].__setitem__(key, value),
                    "forbidden_physical_input",
                )

    def test_index_zero_route_has_no_solver_payload(self) -> None:
        route = self.fixture["routes"]["source_invalid_control"]
        self.assertEqual(route["route"], "source_invalid")
        self.assertFalse(route["physical_problem_created"])
        self.assertFalse(route["event_solver_executed"])
        self.assertFalse(route["arb_evaluator_executed"])
        for key in (
            "solver_payload",
            "event_record",
            "certificate_bundle",
            "physical_problem",
        ):
            self.assertNotIn(key, route)
        self.assert_gate(
            lambda _registry, fixture: fixture["routes"][
                "source_invalid_control"
            ].__setitem__("solver_payload", {}),
            "route",
            "invalid_route_payload",
        )

    def test_source_coefficient_mutation_rejected_after_ordinary_resealing(self) -> None:
        def mutate(_registry: dict[str, Any], fixture: dict[str, Any]) -> None:
            record = fixture["selected_source_states"]["valid_physical_control"]
            encoded = record["complete_serialized_source_state_binary64"]
            leaf = encoded["strings"][0]["modes"][0]["x"][0]
            original = float.fromhex(leaf["binary64_hex"])
            leaf["binary64_hex"] = math.nextafter(original, math.inf).hex()
            state = replayer.decode_binary64_tree(encoded)
            state["validity"] = replayer.evaluate_validity(
                state, self.registry
            )
            state["constraint_diagnostics"] = replayer.constraint_diagnostics(
                state, self.registry
            )
            core = {key: state[key] for key in replayer.SOURCE_CORE_KEYS}
            changed_hash = replayer.semantic_sha256(core)
            state["source_state_sha256"] = changed_hash
            encoded = replayer.encode_binary64_tree(state)
            projected = replayer.exact_dyadic_tree(state)
            record["source_state_sha256"] = changed_hash
            record["complete_serialized_source_state_binary64"] = encoded
            record["complete_serialized_state_semantic_sha256"] = (
                replayer.semantic_sha256(encoded)
            )
            record["complete_exact_dyadic_projection"] = projected
            record["complete_dyadic_projection_semantic_sha256"] = (
                replayer.semantic_sha256(projected)
            )
            fixture["pre_registered_selection"]["scanned_indices"][2][
                "source_state_sha256"
            ] = changed_hash
            fixture["routes"]["valid_physical_control"][
                "source_state_sha256"
            ] = changed_hash
            fixture["physical_problem"]["source_commitment"][
                "source_state_sha256"
            ] = changed_hash
            fixture["physical_problem_semantic_sha256"] = (
                replayer.semantic_sha256(fixture["physical_problem"])
            )

        self.assert_gate(
            mutate,
            "source_state_commitment",
            "source_coefficient_commitment",
            "source_coefficients",
        )

    def test_validity_and_diagnostic_mutations_are_rejected(self) -> None:
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "source_invalid_control"
            ]["complete_serialized_source_state_binary64"]["validity"].__setitem__(
                "status", "valid"
            ),
            "validity",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"][
                "constraint_diagnostics"
            ].__setitem__("energy", {"binary64_hex": (0.0).hex()}),
            "constraint_diagnostics",
        )

    def test_q_orientation_wave_and_source_draw_mutations_are_rejected(self) -> None:
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"].__setitem__(
                "relative_centre_gauge", "Q1=0,Q2=-Q_relative"
            ),
            "q_gauge",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"]["strings"][0].__setitem__(
                "orientation", -1
            ),
            "orientation",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"]["strings"][0]["modes"][
                0
            ].__setitem__("wave_number", {"binary64_hex": (0.25).hex()}),
            "wave_number",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["registry_commitment"].__setitem__(
                "source_draw_sha256", "0" * 64
            ),
            "registry_commitment",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"].__setitem__(
                "source_draw_sha256", "0" * 64
            ),
            "source_draw_commitment",
        )

    def test_state_and_problem_hash_variants_are_rejected(self) -> None:
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ].__setitem__("source_state_sha256", "0" * 64),
            "source_state_commitment",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture.__setitem__(
                "physical_problem_semantic_sha256", "0" * 64
            ),
            "problem_commitment",
        )

    def test_registry_and_problem_code_pins_reject_self_consistent_variants(self) -> None:
        self.assert_gate(
            lambda registry, _fixture: registry["validity"].__setitem__(
                "graph_upper_bound_max", 2.0
            ),
            "registry_commitment",
        )

        def mutate_problem(
            _registry: dict[str, Any], fixture: dict[str, Any]
        ) -> None:
            problem = fixture["physical_problem"]
            problem["hysteresis"]["r_in"] = {
                "exponent": 3,
                "numerator": 1,
            }
            fixture["physical_problem_semantic_sha256"] = (
                replayer.semantic_sha256(problem)
            )

        self.assert_gate(
            mutate_problem, "physical_projection", "problem_commitment"
        )

    def test_type_duplicate_float_and_nonfinite_variants_are_rejected(self) -> None:
        self.assert_gate(
            lambda _registry, fixture: fixture[
                "pre_registered_selection"
            ].__setitem__("first_valid_index", True),
            "least_status_rule",
        )
        with self.assertRaises(replayer.BindingReplayError):
            replayer.strict_float_free_loads('{"a":1,"a":1}')
        for text in ('{"value":1.0}', '{"value":NaN}', '{"value":Infinity}'):
            with self.subTest(text=text):
                with self.assertRaises(replayer.BindingReplayError):
                    replayer.strict_float_free_loads(text)
        with self.assertRaises(replayer.BindingReplayError):
            replayer.strict_registry_loads('{"value":NaN}')

    def test_noncanonical_binary64_and_dyadic_variants_are_rejected(self) -> None:
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"]["Q1"].__setitem__(
                0, {"binary64_hex": "0X1.0P+0"}
            ),
            "binary64",
        )
        self.assert_gate(
            lambda _registry, fixture: fixture["selected_source_states"][
                "valid_physical_control"
            ]["complete_exact_dyadic_projection"]["Q1"].__setitem__(
                0, {"exponent": 1, "numerator": 2}
            ),
            "dyadic_projection",
            "dyadic",
        )

    def test_replayer_source_has_no_forbidden_dependency_or_dynamic_execution(
        self,
    ) -> None:
        source = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imported = set()
        called_names = set()
        attributes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.add(node.module or "")
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                called_names.add(node.func.id)
            elif isinstance(node, ast.Attribute):
                attributes.add(node.attr)
        allowed_roots = {
            "__future__",
            "argparse",
            "copy",
            "hashlib",
            "json",
            "math",
            "re",
            "decimal",
            "fractions",
            "pathlib",
            "typing",
        }
        self.assertTrue(
            all(name.split(".")[0] in allowed_roots for name in imported),
            imported,
        )
        self.assertTrue(
            {"exec", "eval", "compile", "__import__"}.isdisjoint(called_names)
        )
        self.assertTrue(
            {
                "exec_module",
                "spec_from_file_location",
                "SourceFileLoader",
            }.isdisjoint(attributes)
        )

    def test_check_mode_report_and_normalized_lf_inventory(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--check"],
            cwd=ARTIFACT_DIR.parent.parent,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = replayer.strict_report_load()
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["failed_gates"], [])
        self.assertEqual(
            replayer.verify_report(report, self.replay),
            report["report_semantic_sha256"],
        )
        inventory = {row["path"]: row["normalized_lf_sha256"] for row in report["normalized_lf_inventory"]}
        self.assertEqual(set(inventory), set(replayer.INVENTORY_PATHS))
        for relative, digest in inventory.items():
            self.assertEqual(
                digest,
                replayer.normalized_lf_sha256(replayer.REPOSITORY_ROOT / relative),
            )


if __name__ == "__main__":
    unittest.main()
