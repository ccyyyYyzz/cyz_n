"""Tests for the pinned Brief 0018 -> Brief 0019 physical source bridge."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable


ARTIFACT_DIR = Path(__file__).resolve().parent
MODULE_PATH = ARTIFACT_DIR / "source_state_bridge.py"
SPEC = importlib.util.spec_from_file_location("source_state_bridge", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
bridge = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = bridge
SPEC.loader.exec_module(bridge)


class SourceStateBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = bridge.build_fixture()
        cls.replay = bridge.verify_fixture(cls.fixture)

    def assert_gate(
        self,
        mutator: Callable[[dict[str, Any]], None],
        *accepted_gates: str,
    ) -> None:
        hostile = copy.deepcopy(self.fixture)
        mutator(hostile)
        with self.assertRaises(bridge.BridgeError) as raised:
            bridge.verify_fixture(hostile)
        self.assertIn(raised.exception.gate, accepted_gates)

    def test_pinned_upstream_hashes_and_selection(self) -> None:
        self.assertEqual(
            self.replay["registry_canonical_sha256"],
            "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb",
        )
        self.assertEqual(
            self.replay["source_draw_sha256"],
            "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4",
        )
        rows = self.fixture["pre_registered_selection"]["scanned_indices"]
        self.assertEqual(
            [(row["sample_index"], row["validity_status"]) for row in rows],
            [(0, "source_invalid"), (1, "source_invalid"), (2, "valid")],
        )
        self.assertEqual(
            rows[0]["source_state_sha256"],
            "bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b",
        )
        self.assertEqual(
            rows[2]["source_state_sha256"],
            "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c",
        )

    def test_binary64_hex_and_dyadic_projections_are_bijective(self) -> None:
        for record in self.fixture["selected_source_states"].values():
            decoded = bridge.decode_binary64_tree(
                record["complete_serialized_source_state_binary64"]
            )
            exact = bridge.exact_dyadic_tree(decoded)
            self.assertTrue(
                bridge.type_strict_equal(
                    exact, record["complete_exact_dyadic_projection"]
                )
            )

            def walk_pair(encoded: Any, projected: Any) -> None:
                if (
                    type(encoded) is dict
                    and set(encoded) == {"binary64_hex"}
                ):
                    binary64 = float.fromhex(encoded["binary64_hex"])
                    self.assertEqual(
                        bridge.parse_dyadic(projected),
                        Fraction.from_float(binary64),
                    )
                    return
                if type(encoded) is list:
                    self.assertEqual(len(encoded), len(projected))
                    for left, right in zip(encoded, projected):
                        walk_pair(left, right)
                elif type(encoded) is dict:
                    self.assertEqual(encoded.keys(), projected.keys())
                    for key in encoded:
                        walk_pair(encoded[key], projected[key])
                else:
                    self.assertEqual(type(encoded), type(projected))
                    self.assertEqual(encoded, projected)

            walk_pair(
                record["complete_serialized_source_state_binary64"],
                record["complete_exact_dyadic_projection"],
            )

    def test_invalid_route_calls_neither_solver_nor_arb(self) -> None:
        source = bridge._load_source_module()
        registry = bridge._read_registry(source)
        invalid = source.sample_source(registry, 0)

        calls = {"solver": 0, "arb": 0}

        def solver(*_args: Any, **_kwargs: Any) -> None:
            calls["solver"] += 1

        def arb(*_args: Any, **_kwargs: Any) -> None:
            calls["arb"] += 1

        route, problem = bridge.route_source_state(
            invalid, registry, solver, arb
        )
        self.assertEqual(route["route"], "source_invalid")
        self.assertIsNone(problem)
        self.assertEqual(calls, {"solver": 0, "arb": 0})

    def test_physical_problem_is_complete_and_rank_blind(self) -> None:
        problem = self.fixture["physical_problem"]
        self.assertEqual(problem["dimensions"]["target"], 9)
        self.assertEqual(problem["dimensions"]["transverse"], 8)
        self.assertEqual(problem["dimensions"]["winding_axis"], 8)
        self.assertEqual(
            problem["worldsheet"]["winding_orientations"], [1, -1]
        )
        self.assertEqual(len(problem["kinematics"]["strings"]), 2)
        self.assertEqual(
            set(problem["kinematics"]["centres_Q1_Q2"]), {"Q1", "Q2"}
        )
        for centre in problem["kinematics"]["centres_Q1_Q2"].values():
            self.assertEqual(len(centre), 8)
        for string in problem["kinematics"]["strings"]:
            self.assertIn(string["centre_reference"], {"Q1", "Q2"})
            self.assertEqual(len(string["transverse_velocity"]), 8)
            self.assertEqual(len(string["modes"]), 1)
            mode = string["modes"][0]
            self.assertEqual(bridge.parse_dyadic(mode["wave_number"]), Fraction(1, 8))
            for key in ("initial_x", "initial_y", "initial_p", "initial_q"):
                self.assertEqual(len(mode[key]), 8)
        self.assertEqual(
            bridge.verify_physical_problem(problem),
            bridge.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )
        serialized = json.dumps(problem, sort_keys=True)
        for forbidden in (
            '"rank"',
            '"normal_dimension"',
            '"response_winner"',
            '"reaction_scale"',
        ):
            self.assertNotIn(forbidden, serialized)

    def test_q_is_added_once(self) -> None:
        kinematics = self.fixture["physical_problem"]["kinematics"]
        self.assertEqual(kinematics["centre_term_multiplicity"], 1)
        self.assertEqual(
            kinematics["transverse_embedding"],
            "X_i^perp=Q_i+V_i*t+Y_i(t,sigma_i)",
        )
        self.assertEqual(kinematics["separation"].count("(Q1-Q2)"), 1)
        self.assertNotIn(
            "Q_relative",
            json.dumps(self.fixture["physical_problem"], sort_keys=True),
        )

    def test_f1_tension_and_winding_relations(self) -> None:
        problem = self.fixture["physical_problem"]
        f1 = problem["f1_convention"]
        torus = problem["target_torus"]
        tension = bridge.parse_dyadic(f1["string_tension"])
        ell_s = bridge.parse_dyadic(f1["string_length_ell_s"])
        portable_pi = bridge.parse_dyadic(f1["portable_pi_binary64"])
        self.assertEqual(
            tension,
            Fraction.from_float(
                1.0 / (2.0 * float(portable_pi) * float(ell_s) ** 2)
            ),
        )
        self.assertEqual(
            bridge.parse_dyadic(f1["winding_length"]),
            f1["winding_number_abs"]
            * bridge.parse_dyadic(torus["periods_L_A"][8]),
        )

    def test_coefficient_mutation_is_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["physical_problem"]["kinematics"]["strings"][0][
                "modes"
            ][0]["initial_x"].__setitem__(0, bridge.dyadic(1.0)),
            "problem_commitment",
            "physical_projection",
        )
        self.assert_gate(
            lambda value: value["selected_source_states"][
                "valid_physical_control"
            ]["complete_exact_dyadic_projection"]["strings"][0]["modes"][0][
                "x"
            ].__setitem__(0, bridge.dyadic(1.0)),
            "coefficient_projection",
        )

    def test_state_hash_mutation_is_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["selected_source_states"][
                "valid_physical_control"
            ].__setitem__("source_state_sha256", "0" * 64),
            "source_state_hash",
        )

    def test_registry_mutation_is_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["registry_commitment"].__setitem__(
                "registry_canonical_sha256", "0" * 64
            ),
            "registry_commitment",
        )

    def test_orientation_mutations_are_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["physical_problem"]["worldsheet"].__setitem__(
                "winding_orientations", [-1, 1]
            ),
            "orientation",
        )
        self.assert_gate(
            lambda value: value["physical_problem"]["kinematics"]["strings"][
                0
            ].__setitem__("orientation", -1),
            "orientation",
        )

    def test_wave_number_mutation_is_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["physical_problem"]["kinematics"]["strings"][0][
                "modes"
            ][0].__setitem__("wave_number", bridge.dyadic(0.25)),
            "wave_number",
        )

    def test_validity_mutation_is_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["selected_source_states"][
                "source_invalid_control"
            ].__setitem__("validity_status", "valid"),
            "validity_route",
        )
        self.assert_gate(
            lambda value: value["selected_source_states"][
                "valid_physical_control"
            ]["complete_serialized_source_state_binary64"]["validity"].__setitem__(
                "status", "source_invalid"
            ),
            "source_replay",
        )

    def test_index_mutations_are_rejected(self) -> None:
        self.assert_gate(
            lambda value: value["physical_problem"]["source_commitment"].__setitem__(
                "source_sample_index", 3
            ),
            "source_index",
        )
        self.assert_gate(
            lambda value: value["pre_registered_selection"].__setitem__(
                "first_valid_index", 3
            ),
            "pre_registered_selection",
        )

    def test_rank_normal_response_and_reaction_fields_are_rejected(self) -> None:
        for key, value in (
            ("rank", 2),
            ("normal_dimension", 7),
            ("response_winner", "string-1"),
            ("reaction_scale", bridge.dyadic(1.0)),
        ):
            with self.subTest(key=key):
                self.assert_gate(
                    lambda fixture, key=key, value=value: fixture[
                        "physical_problem"
                    ].__setitem__(key, value),
                    "problem_schema",
                )

    def test_strict_json_rejects_duplicate_float_and_nonfinite(self) -> None:
        with self.assertRaises(bridge.BridgeError) as duplicate:
            bridge.strict_json_loads('{"a":1,"a":1}')
        self.assertEqual(duplicate.exception.gate, "strict_json")
        for token in ("1.0", "NaN", "Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(bridge.BridgeError):
                    bridge.strict_json_loads('{"value":' + token + "}")

    def test_dyadic_grammar_is_canonical(self) -> None:
        for value in (0.0, -0.0, 0.125, -0.5, float.fromhex("0x0.0000000000001p-1022")):
            with self.subTest(value=value.hex()):
                encoded = bridge.dyadic(value)
                self.assertEqual(
                    bridge.parse_dyadic(encoded), Fraction.from_float(value)
                )
        for bad in (
            {"numerator": 0, "exponent": 1},
            {"numerator": 2, "exponent": 1},
            {"numerator": 1, "exponent": -1},
            {"numerator": True, "exponent": 0},
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(bridge.BridgeError):
                    bridge.parse_dyadic(bad)

    def test_check_mode_matches_committed_artifacts(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--check"],
            cwd=ARTIFACT_DIR.parent.parent,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = bridge.strict_json_load(bridge.REPORT_PATH)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["failed_gates"], [])
        self.assertEqual(
            report["fixture_semantic_sha256"],
            bridge.semantic_sha256(bridge.strict_json_load(bridge.FIXTURE_PATH)),
        )
        self.assertEqual(
            bridge.verify_report(
                report, bridge.strict_json_load(bridge.FIXTURE_PATH)
            ),
            report["report_semantic_sha256"],
        )
        self.assertEqual(
            report["commitments"]["physical_problem_semantic_sha256"],
            bridge.PHYSICAL_PROBLEM_SEMANTIC_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
