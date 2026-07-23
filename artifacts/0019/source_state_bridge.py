"""Pinned Brief 0018 source-to-Brief 0019 physical-problem binding.

This module is deliberately a binding layer, not an event solver.  It
regenerates the pre-registered source states from the canonical Brief 0018
registry, routes invalid states before any numerical backend can run, and
projects the first valid state into a float-free exact-dyadic physical
problem suitable for a later Arb nine-dimensional jet evaluator.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Mapping, Sequence


FIXTURE_SCHEMA = "cyz-brief-0019-source-state-bridge-fixture-v1"
REPORT_SCHEMA = "cyz-brief-0019-source-state-bridge-report-v1"
PROBLEM_SCHEMA = "cyz-brief-0019-exact-dyadic-f1-problem-v1"
EQUATION_FAMILY_VERSION = "f1-opposite-winding-worldsheet-k1-v1"

REGISTRY_CANONICAL_SHA256 = (
    "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb"
)
SOURCE_DRAW_SHA256 = (
    "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4"
)
FIRST_SOURCE_INVALID_INDEX = 0
FIRST_SOURCE_INVALID_STATE_SHA256 = (
    "bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b"
)
FIRST_VALID_INDEX = 2
FIRST_VALID_STATE_SHA256 = (
    "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c"
)

# Filled after the physical schema was frozen.  Verification treats this
# source-code pin, not a bundle-internal digest, as the trust anchor.
PHYSICAL_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parent.parent
SOURCE_DIR = ARTIFACT_DIR.parent / "0018"
SOURCE_MODULE_PATH = SOURCE_DIR / "microcanonical_source.py"
SOURCE_REGISTRY_PATH = SOURCE_DIR / "source_registry.json"
FIXTURE_PATH = ARTIFACT_DIR / "source_state_bridge_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "source_state_bridge_report.json"

BRIDGE_INVENTORY = (
    "artifacts/0019/source_state_bridge.py",
    "artifacts/0019/test_source_state_bridge.py",
    "artifacts/0019/source_state_bridge_fixture.json",
    "artifacts/0019/README.md",
)

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
BINARY64_HEX = re.compile(
    r"-?0x(?:0(?:\.0+)?|1\.[0-9a-f]{13})p[+-][0-9]+"
)
DYADIC_KEYS = {"numerator", "exponent"}
SOURCE_CORE_KEYS = {
    "schema_version",
    "sample_index",
    "source_draw_sha256",
    "relative_centre_gauge",
    "Q_relative",
    "Q1",
    "Q2",
    "energy_shares_s0_s1_s2",
    "strings",
}
FORBIDDEN_PHYSICAL_KEYS = {
    "rank",
    "rank_tolerance",
    "normal",
    "normal_dimension",
    "normal_dimension_hint",
    "response_rank",
    "response_winner",
    "requested_winner",
    "reaction",
    "reaction_data",
    "reaction_scale",
    "validity",
    "constraint_diagnostics",
    "energy_shares_s0_s1_s2",
    "Q_relative",
}


class BridgeError(ValueError):
    """A bridge artifact failed at a named semantic gate."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise BridgeError(gate, message)


def _exact_keys(
    value: Any, expected: set[str], path: str, gate: str = "schema"
) -> dict[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        fail(
            gate,
            f"{path} keys differ; missing={sorted(expected-actual)}, "
            f"extra={sorted(actual-expected)}",
        )
    return value


def _list(value: Any, length: int | None, path: str, gate: str) -> list[Any]:
    if type(value) is not list:
        fail(gate, f"{path} must be an array")
    if length is not None and len(value) != length:
        fail(gate, f"{path} must have length {length}")
    return value


def _integer(value: Any, path: str, gate: str) -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer")
    return value


def _string(value: Any, path: str, gate: str) -> str:
    if type(value) is not str or not value:
        fail(gate, f"{path} must be a nonempty string")
    return value


def _sha256(value: Any, path: str, gate: str) -> str:
    text = _string(value, path, gate)
    if HEX_SHA256.fullmatch(text) is None:
        fail(gate, f"{path} must be a lowercase SHA-256 digest")
    return text


def reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate object key {key!r}")
        result[key] = value
    return result


def reject_nonfinite(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def reject_float(token: str) -> None:
    fail(
        "strict_json",
        f"ordinary JSON float {token!r} is forbidden; use binary64/dyadic encoding",
    )


def assert_float_free_json(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        fail("strict_json", f"{path} contains an ordinary float")
    if type(value) is list:
        for index, item in enumerate(value):
            assert_float_free_json(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} contains a non-string key")
            assert_float_free_json(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains {type(value).__name__}")


def strict_json_loads(text: str) -> Any:
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicate_pairs,
        parse_constant=reject_nonfinite,
        parse_float=reject_float,
    )
    assert_float_free_json(value)
    return value


def strict_json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return strict_json_loads(handle.read())


def canonical_bytes(value: Any) -> bytes:
    assert_float_free_json(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def semantic_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def pretty_json(value: Any) -> str:
    assert_float_free_json(value)
    return (
        json.dumps(
            value,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


def write_json(path: Path, value: Any) -> None:
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(
            type_strict_equal(left[key], right[key]) for key in left
        )
    if type(left) is list:
        return len(left) == len(right) and all(
            type_strict_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def normalized_lf_sha256(path: Path) -> str:
    data = path.read_bytes()
    normalized = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def _load_source_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "brief0018_microcanonical_source_for_bridge", SOURCE_MODULE_PATH
    )
    if spec is None or spec.loader is None:
        fail("source_runtime", "cannot load Brief 0018 source implementation")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _read_registry(source: ModuleType) -> dict[str, Any]:
    registry = source.read_strict_json(SOURCE_REGISTRY_PATH)
    source.validate_registry(registry)
    digest = source.sha256_hex(registry)
    if digest != REGISTRY_CANONICAL_SHA256:
        fail(
            "registry_commitment",
            f"canonical registry digest {digest} is not the pinned digest",
        )
    draw_digest = source.source_draw_sha256(registry)
    if draw_digest != SOURCE_DRAW_SHA256:
        fail(
            "source_draw_commitment",
            f"source draw digest {draw_digest} is not the pinned digest",
        )
    return registry


def dyadic(value: float) -> dict[str, int]:
    """Encode one finite binary64 as its unique reduced dyadic."""

    if type(value) is not float or not math.isfinite(value):
        fail("dyadic_projection", "dyadic() requires one finite binary64")
    numerator, denominator = value.as_integer_ratio()
    if denominator <= 0 or denominator & (denominator - 1):
        fail("dyadic_projection", "binary64 denominator is not a power of two")
    exponent = denominator.bit_length() - 1
    if numerator == 0:
        exponent = 0
    else:
        while exponent > 0 and numerator % 2 == 0:
            numerator //= 2
            exponent -= 1
    return {"exponent": exponent, "numerator": numerator}


def parse_dyadic(value: Any, path: str = "$") -> Fraction:
    obj = _exact_keys(value, DYADIC_KEYS, path, "dyadic")
    numerator = _integer(obj["numerator"], f"{path}.numerator", "dyadic")
    exponent = _integer(obj["exponent"], f"{path}.exponent", "dyadic")
    if exponent < 0:
        fail("dyadic", f"{path}.exponent must be nonnegative")
    if numerator == 0 and exponent != 0:
        fail("dyadic", f"{path} zero must use exponent zero")
    if exponent > 0 and numerator % 2 == 0:
        fail("dyadic", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


def encode_binary64_tree(value: Any) -> Any:
    """Losslessly encode every binary64 while retaining the complete shape."""

    if type(value) is float:
        if not math.isfinite(value):
            fail("source_state", "source contains a non-finite binary64")
        return {"binary64_hex": value.hex()}
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [encode_binary64_tree(item) for item in value]
    if type(value) is dict:
        return {
            key: encode_binary64_tree(item)
            for key, item in value.items()
        }
    fail("source_state", f"unsupported source value {type(value).__name__}")


def decode_binary64_tree(value: Any, path: str = "$") -> Any:
    if type(value) is dict and set(value) == {"binary64_hex"}:
        token = value["binary64_hex"]
        if type(token) is not str or BINARY64_HEX.fullmatch(token) is None:
            fail("source_state", f"{path} has a noncanonical binary64 token")
        result = float.fromhex(token)
        if not math.isfinite(result) or result.hex() != token:
            fail("source_state", f"{path} does not round-trip canonically")
        return result
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [
            decode_binary64_tree(item, f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    if type(value) is dict:
        return {
            key: decode_binary64_tree(item, f"{path}.{key}")
            for key, item in value.items()
        }
    fail("source_state", f"{path} contains unsupported encoded data")


def exact_dyadic_tree(value: Any) -> Any:
    """Project every binary64 in a source tree to a canonical exact dyadic."""

    if type(value) is float:
        return dyadic(value)
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [exact_dyadic_tree(item) for item in value]
    if type(value) is dict:
        return {key: exact_dyadic_tree(item) for key, item in value.items()}
    fail("dyadic_projection", f"unsupported source value {type(value).__name__}")


def _assert_all_dyadics(value: Any, path: str = "$") -> None:
    if type(value) is dict and set(value) == DYADIC_KEYS:
        parse_dyadic(value, path)
        return
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _assert_all_dyadics(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            _assert_all_dyadics(item, f"{path}.{key}")
        return
    fail("dyadic_projection", f"{path} is not float-free")


def _source_core(state: Mapping[str, Any]) -> dict[str, Any]:
    if set(state) != SOURCE_CORE_KEYS | {
        "source_state_sha256",
        "validity",
        "constraint_diagnostics",
    }:
        fail("source_state", "complete source state schema changed")
    return {key: state[key] for key in state if key in SOURCE_CORE_KEYS}


def _registry_projection(registry: Mapping[str, Any]) -> dict[str, Any]:
    source = registry["source_draw_registry"]
    downstream = registry["downstream_context"]
    return {
        "ell_s": dyadic(source["string_length_ell_s"]),
        "string_tension": dyadic(source["string_tension"]),
        "portable_pi_binary64": dyadic(math.pi),
        "winding_length": dyadic(source["winding_length"]),
        "winding_number_abs": source["winding_number_abs"],
        "winding_axis": source["winding_axis"],
        "winding_orientations": list(source["winding_orientations"]),
        "transverse_axis_order": list(source["transverse_axis_order"]),
        "fourier_cutoff_K": source["fourier_cutoff_K"],
        "torus_periods": [
            dyadic(value) for value in source["torus_periods_L_A"]
        ],
        "r_in": dyadic(downstream["r_in"]),
        "r_out": dyadic(downstream["r_out"]),
        "time_window": [
            dyadic(value) for value in downstream["observation_window"]
        ],
        "initial_history": downstream["initial_history"],
    }


def _identity_metric(size: int) -> list[list[dict[str, int]]]:
    return [
        [dyadic(float(1 if row == column else 0)) for column in range(size)]
        for row in range(size)
    ]


def _diagonal_matrix(
    diagonal: Sequence[dict[str, int]],
) -> list[list[dict[str, int]]]:
    zero = dyadic(0.0)
    return [
        [
            copy.deepcopy(diagonal[row] if row == column else zero)
            for column in range(len(diagonal))
        ]
        for row in range(len(diagonal))
    ]


def build_physical_problem(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    """Project a valid serialized state into the frozen physical equations."""

    if state["sample_index"] != FIRST_VALID_INDEX:
        fail("source_index", "only the pre-registered first valid index is bound")
    if state["source_state_sha256"] != FIRST_VALID_STATE_SHA256:
        fail("source_state_hash", "valid source state hash is not pinned")
    if state["validity"]["status"] != "valid":
        fail("validity_route", "an invalid source cannot enter a physical problem")

    projection = _registry_projection(registry)
    if projection["winding_axis"] != 8:
        fail("physical_convention", "the target winding axis must be 8")
    if projection["transverse_axis_order"] != list(range(8)):
        fail("physical_convention", "the transverse axis order must be 0..7")
    if projection["winding_orientations"] != [1, -1]:
        fail("physical_convention", "opposite orientations must be [+1,-1]")
    if projection["fourier_cutoff_K"] != 1:
        fail("physical_convention", "this binding is frozen to K=1")

    strings = []
    for string_index, source_string in enumerate(state["strings"]):
        modes = []
        if len(source_string["modes"]) != 1:
            fail("physical_convention", "each string must contain exactly K=1 mode")
        for mode in source_string["modes"]:
            modes.append(
                {
                    "mode_number": mode["mode_number"],
                    "wave_number": dyadic(mode["wave_number"]),
                    "initial_x": [dyadic(value) for value in mode["x"]],
                    "initial_y": [dyadic(value) for value in mode["y"]],
                    "initial_p": [dyadic(value) for value in mode["p"]],
                    "initial_q": [dyadic(value) for value in mode["q"]],
                }
            )
        strings.append(
            {
                "string_id": string_index + 1,
                "orientation": source_string["orientation"],
                "centre_reference": f"Q{string_index + 1}",
                "transverse_velocity": [
                    dyadic(value)
                    for value in source_string["transverse_velocity"]
                ],
                "modes": modes,
            }
        )

    periods = projection["torus_periods"]
    return {
        "schema_version": PROBLEM_SCHEMA,
        "equation_family_version": EQUATION_FAMILY_VERSION,
        "source_commitment": {
            "source_registry_canonical_sha256": REGISTRY_CANONICAL_SHA256,
            "source_draw_sha256": SOURCE_DRAW_SHA256,
            "source_state_sha256": FIRST_VALID_STATE_SHA256,
            "source_sample_index": FIRST_VALID_INDEX,
            "source_sample_schema": state["schema_version"],
        },
        "dimensions": {
            "target": 9,
            "transverse": 8,
            "target_axis_order": list(range(9)),
            "transverse_axis_order": list(range(8)),
            "winding_axis": 8,
        },
        "f1_convention": {
            "coordinate_units": (
                registry["source_draw_registry"]["coordinate_units"]
            ),
            "string_length_ell_s": projection["ell_s"],
            "string_tension": projection["string_tension"],
            "portable_pi_binary64": projection["portable_pi_binary64"],
            "tension_relation": "T_F=1/(2*pi*ell_s^2), rounded once to binary64",
            "winding_number_abs": projection["winding_number_abs"],
            "winding_length": projection["winding_length"],
            "winding_relation": "L_w=abs(w)*L_A[winding_axis]",
        },
        "target_torus": {
            "metric_convention": "G=identity_9",
            "G": _identity_metric(9),
            "lattice_convention": "Lambda=diag(L_0,...,L_8)",
            "periods_L_A": periods,
            "Lambda": _diagonal_matrix(periods),
            "image_separation": "s_n=d-Lambda*n for n in Z^9",
        },
        "worldsheet": {
            "sigma_coordinate_units": "physical_length",
            "sigma_domains": [
                {
                    "lower": dyadic(0.0),
                    "upper": copy.deepcopy(projection["winding_length"]),
                    "closure": "lower_closed_upper_open",
                },
                {
                    "lower": dyadic(0.0),
                    "upper": copy.deepcopy(projection["winding_length"]),
                    "closure": "lower_closed_upper_open",
                },
            ],
            "winding_orientations": projection["winding_orientations"],
            "winding_embedding": "X_i^w=o_i*sigma_i on target axis 8",
        },
        "observation": {
            "t0": projection["time_window"][0],
            "t1": projection["time_window"][1],
            "window_closure": "lower_closed_upper_open",
            "initial_history": projection["initial_history"],
            "continuation_convention": (
                "right-censor at excluded t1; carry active/armed history "
                "to a subsequent adjacent window without boundary re-arming"
            ),
        },
        "hysteresis": {
            "r_in": projection["r_in"],
            "r_out": projection["r_out"],
            "distance_convention": "F_n=(1/2)*s_n^T*G*s_n",
        },
        "kinematics": {
            "transverse_embedding": (
                "X_i^perp=Q_i+V_i*t+Y_i(t,sigma_i)"
            ),
            "centre_term_multiplicity": 1,
            "separation": (
                "d_perp=(Q1-Q2)+(V1-V2)*t+(Y1-Y2); "
                "d_w=o1*sigma1-o2*sigma2"
            ),
            "mode_shape": (
                "Y_i=x_i(t)*cos(k*sigma_i)+y_i(t)*sin(k*sigma_i)"
            ),
            "mode_ode": [
                "dot(x)=p",
                "dot(y)=q",
                "dot(p)=-k^2*x",
                "dot(q)=-k^2*y",
            ],
            "initial_time": dyadic(0.0),
            "centres_Q1_Q2": {
                "Q1": [dyadic(value) for value in state["Q1"]],
                "Q2": [dyadic(value) for value in state["Q2"]],
            },
            "strings": strings,
        },
        "arb_9d_jet_ingress": {
            "scalar_encoding": "reduced exact dyadic numerator/2^exponent",
            "jet_variables": ["sigma1", "sigma2", "t"],
            "target_component_order": list(range(9)),
            "required_outputs": [
                "d",
                "d_a",
                "d_ab",
                "F_a",
                "F_ab",
                "g_r",
                "Dg_r",
            ],
            "proof_arithmetic_boundary": (
                "convert dyadics exactly to Arb balls; evaluate "
                "trigonometric functions with outward rounding"
            ),
        },
        "scope": {
            "claim": "exact source-to-physical-problem binding only",
            "does_not_claim": [
                "exhaustive worldsheet roots",
                "hysteretic population law",
                "3+1 selection",
            ],
        },
    }


def _walk_forbidden_keys(value: Any, path: str = "$") -> None:
    if type(value) is dict:
        for key, item in value.items():
            if key in FORBIDDEN_PHYSICAL_KEYS:
                fail(
                    "rank_blind_physical_problem",
                    f"forbidden physical key {key!r} at {path}",
                )
            _walk_forbidden_keys(item, f"{path}.{key}")
    elif type(value) is list:
        for index, item in enumerate(value):
            _walk_forbidden_keys(item, f"{path}[{index}]")


def _verify_identity_matrix(
    matrix: Any, size: int, path: str, gate: str
) -> None:
    rows = _list(matrix, size, path, gate)
    for row_index, row in enumerate(rows):
        columns = _list(row, size, f"{path}[{row_index}]", gate)
        for column_index, item in enumerate(columns):
            expected = Fraction(1 if row_index == column_index else 0)
            if parse_dyadic(item, f"{path}[{row_index}][{column_index}]") != expected:
                fail(gate, f"{path} is not the identity")


def verify_physical_problem(problem: Any) -> str:
    """Replay the closed physical schema before checking its semantic hash."""

    expected_top = {
        "schema_version",
        "equation_family_version",
        "source_commitment",
        "dimensions",
        "f1_convention",
        "target_torus",
        "worldsheet",
        "observation",
        "hysteresis",
        "kinematics",
        "arb_9d_jet_ingress",
        "scope",
    }
    obj = _exact_keys(problem, expected_top, "$.physical_problem", "problem_schema")
    if obj["schema_version"] != PROBLEM_SCHEMA:
        fail("problem_schema", "unsupported problem schema")
    if obj["equation_family_version"] != EQUATION_FAMILY_VERSION:
        fail("problem_commitment", "equation family changed")
    _walk_forbidden_keys(obj)
    _assert_all_dyadics(obj)

    commitment = _exact_keys(
        obj["source_commitment"],
        {
            "source_registry_canonical_sha256",
            "source_draw_sha256",
            "source_state_sha256",
            "source_sample_index",
            "source_sample_schema",
        },
        "$.physical_problem.source_commitment",
        "source_commitment",
    )
    pins = (
        (
            commitment["source_registry_canonical_sha256"],
            REGISTRY_CANONICAL_SHA256,
            "registry",
        ),
        (commitment["source_draw_sha256"], SOURCE_DRAW_SHA256, "draw"),
        (
            commitment["source_state_sha256"],
            FIRST_VALID_STATE_SHA256,
            "state",
        ),
    )
    for actual, expected, label in pins:
        _sha256(actual, f"source_commitment.{label}", "source_commitment")
        if actual != expected:
            fail("source_commitment", f"{label} commitment is not pinned")
    if commitment["source_sample_index"] != FIRST_VALID_INDEX:
        fail("source_index", "physical source index is not the registered index")

    dimensions = _exact_keys(
        obj["dimensions"],
        {
            "target",
            "transverse",
            "target_axis_order",
            "transverse_axis_order",
            "winding_axis",
        },
        "$.physical_problem.dimensions",
        "dimensions",
    )
    if dimensions != {
        "target": 9,
        "transverse": 8,
        "target_axis_order": list(range(9)),
        "transverse_axis_order": list(range(8)),
        "winding_axis": 8,
    }:
        fail("dimensions", "the problem must be 9D with transverse axes 0..7")

    f1 = _exact_keys(
        obj["f1_convention"],
        {
            "coordinate_units",
            "string_length_ell_s",
            "string_tension",
            "portable_pi_binary64",
            "tension_relation",
            "winding_number_abs",
            "winding_length",
            "winding_relation",
        },
        "$.physical_problem.f1_convention",
        "f1_convention",
    )
    ell_s = parse_dyadic(f1["string_length_ell_s"], "f1.ell_s")
    tension = parse_dyadic(f1["string_tension"], "f1.tension")
    portable_pi = parse_dyadic(
        f1["portable_pi_binary64"], "f1.portable_pi_binary64"
    )
    if (
        ell_s != Fraction.from_float(1.0)
        or tension != Fraction.from_float(0.15915494309189535)
        or portable_pi != Fraction.from_float(math.pi)
    ):
        fail("f1_convention", "the pinned binary64 F1 convention changed")
    expected_tension = 1.0 / (2.0 * float(portable_pi) * float(ell_s) ** 2)
    if Fraction.from_float(expected_tension) != tension:
        fail("f1_convention", "T_F is not one-rounding 1/(2*pi*ell_s^2)")
    if f1["winding_number_abs"] != 1:
        fail("f1_convention", "|w| must be one")

    torus = _exact_keys(
        obj["target_torus"],
        {
            "metric_convention",
            "G",
            "lattice_convention",
            "periods_L_A",
            "Lambda",
            "image_separation",
        },
        "$.physical_problem.target_torus",
        "target_torus",
    )
    _verify_identity_matrix(torus["G"], 9, "target_torus.G", "target_torus")
    periods = _list(
        torus["periods_L_A"], 9, "target_torus.periods_L_A", "target_torus"
    )
    lattice = _list(torus["Lambda"], 9, "target_torus.Lambda", "target_torus")
    for row_index, row in enumerate(lattice):
        columns = _list(
            row, 9, f"target_torus.Lambda[{row_index}]", "target_torus"
        )
        for column_index, item in enumerate(columns):
            actual = parse_dyadic(
                item, f"target_torus.Lambda[{row_index}][{column_index}]"
            )
            expected = (
                parse_dyadic(periods[row_index])
                if row_index == column_index
                else Fraction()
            )
            if actual != expected:
                fail("target_torus", "Lambda is not diag(periods_L_A)")
    winding_length = parse_dyadic(f1["winding_length"], "f1.winding_length")
    if winding_length != parse_dyadic(periods[8], "target_torus.periods_L_A[8]"):
        fail("f1_convention", "L_w != |w| L_A[winding_axis]")

    worldsheet = _exact_keys(
        obj["worldsheet"],
        {
            "sigma_coordinate_units",
            "sigma_domains",
            "winding_orientations",
            "winding_embedding",
        },
        "$.physical_problem.worldsheet",
        "orientation",
    )
    if worldsheet["winding_orientations"] != [1, -1]:
        fail("orientation", "worldsheet orientations must be [+1,-1]")
    domains = _list(
        worldsheet["sigma_domains"], 2, "worldsheet.sigma_domains", "worldsheet"
    )
    for index, domain in enumerate(domains):
        entry = _exact_keys(
            domain,
            {"lower", "upper", "closure"},
            f"worldsheet.sigma_domains[{index}]",
            "worldsheet",
        )
        if (
            parse_dyadic(entry["lower"]) != 0
            or parse_dyadic(entry["upper"]) != winding_length
            or entry["closure"] != "lower_closed_upper_open"
        ):
            fail("worldsheet", "sigma domain is not [0,L_w)")

    observation = _exact_keys(
        obj["observation"],
        {
            "t0",
            "t1",
            "window_closure",
            "initial_history",
            "continuation_convention",
        },
        "$.physical_problem.observation",
        "observation",
    )
    if (
        parse_dyadic(observation["t0"]) != 0
        or parse_dyadic(observation["t1"]) != winding_length
        or observation["window_closure"] != "lower_closed_upper_open"
        or observation["initial_history"] != "armed"
    ):
        fail("observation", "the pinned [t0,t1) history changed")

    hysteresis = _exact_keys(
        obj["hysteresis"],
        {"r_in", "r_out", "distance_convention"},
        "$.physical_problem.hysteresis",
        "hysteresis",
    )
    if not (
        parse_dyadic(hysteresis["r_in"]) == Fraction(1, 4)
        < parse_dyadic(hysteresis["r_out"]) == Fraction(1, 2)
    ):
        fail("hysteresis", "the exact inner/outer radii changed")

    kinematics = _exact_keys(
        obj["kinematics"],
        {
            "transverse_embedding",
            "centre_term_multiplicity",
            "separation",
            "mode_shape",
            "mode_ode",
            "initial_time",
            "centres_Q1_Q2",
            "strings",
        },
        "$.physical_problem.kinematics",
        "kinematics",
    )
    if (
        kinematics["centre_term_multiplicity"] != 1
        or kinematics["transverse_embedding"]
        != "X_i^perp=Q_i+V_i*t+Y_i(t,sigma_i)"
        or kinematics["separation"].count("(Q1-Q2)") != 1
    ):
        fail("q_once", "Q_i must enter each embedding exactly once")
    centres = _exact_keys(
        kinematics["centres_Q1_Q2"],
        {"Q1", "Q2"},
        "$.physical_problem.kinematics.centres_Q1_Q2",
        "q_once",
    )
    _list(centres["Q1"], 8, "kinematics.centres_Q1_Q2.Q1", "q_once")
    q2 = _list(centres["Q2"], 8, "kinematics.centres_Q1_Q2.Q2", "q_once")
    if any(parse_dyadic(value) != 0 for value in q2):
        fail("q_once", "the registered Q2=0 gauge changed")
    strings = _list(
        kinematics["strings"], 2, "kinematics.strings", "kinematics"
    )
    for string_index, string in enumerate(strings):
        entry = _exact_keys(
            string,
            {
                "string_id",
                "orientation",
                "centre_reference",
                "transverse_velocity",
                "modes",
            },
            f"kinematics.strings[{string_index}]",
            "kinematics",
        )
        if (
            entry["string_id"] != string_index + 1
            or entry["orientation"] != [1, -1][string_index]
            or entry["centre_reference"] != f"Q{string_index + 1}"
        ):
            fail("orientation", "string identity/orientation mismatch")
        _list(
            entry["transverse_velocity"],
            8,
            "transverse_velocity",
            "kinematics",
        )
        modes = _list(entry["modes"], 1, "modes", "wave_number")
        mode = _exact_keys(
            modes[0],
            {
                "mode_number",
                "wave_number",
                "initial_x",
                "initial_y",
                "initial_p",
                "initial_q",
            },
            "mode",
            "wave_number",
        )
        if (
            mode["mode_number"] != 1
            or parse_dyadic(mode["wave_number"], "mode.wave_number")
            != Fraction(1, 8)
        ):
            fail("wave_number", "K=1 wave number must be exactly 1/8")
        for field in ("initial_x", "initial_y", "initial_p", "initial_q"):
            _list(mode[field], 8, f"mode.{field}", "coefficient_projection")

    digest = semantic_sha256(obj)
    if not PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        return digest
    if digest != PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        fail(
            "problem_commitment",
            f"physical problem digest {digest} is not source-code pinned",
        )
    return digest


class NeverCalled:
    """Probe whose call is itself a routing failure."""

    def __init__(self, name: str):
        self.name = name
        self.calls = 0

    def __call__(self, *_args: Any, **_kwargs: Any) -> None:
        self.calls += 1
        fail("source_invalid_short_circuit", f"{self.name} was called")


def route_source_state(
    state: Mapping[str, Any],
    registry: Mapping[str, Any],
    event_solver: Callable[..., Any],
    arb_evaluator: Callable[..., Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Route validity before touching the solver or Arb evaluator."""

    status = state["validity"]["status"]
    if status == "source_invalid":
        return (
            {
                "sample_index": state["sample_index"],
                "source_state_sha256": state["source_state_sha256"],
                "validity_status_recomputed_from_registry": status,
                "route": "source_invalid",
                "event_solver_executed": False,
                "arb_evaluator_executed": False,
                "physical_problem_created": False,
            },
            None,
        )
    if status != "valid":
        fail("validity_route", f"unknown validity status {status!r}")
    problem = build_physical_problem(state, registry)
    return (
        {
            "sample_index": state["sample_index"],
            "source_state_sha256": state["source_state_sha256"],
            "validity_status_recomputed_from_registry": status,
            "route": "physical_problem_ready",
            "event_solver_executed": False,
            "arb_evaluator_executed": False,
            "physical_problem_created": True,
        },
        problem,
    )


def _state_record(state: Mapping[str, Any]) -> dict[str, Any]:
    encoded = encode_binary64_tree(state)
    projected = exact_dyadic_tree(state)
    return {
        "sample_index": state["sample_index"],
        "source_state_sha256": state["source_state_sha256"],
        "validity_status": state["validity"]["status"],
        "complete_serialized_source_state_binary64": encoded,
        "complete_exact_dyadic_projection": projected,
        "complete_serialized_state_semantic_sha256": semantic_sha256(encoded),
        "complete_dyadic_projection_semantic_sha256": semantic_sha256(projected),
    }


def build_fixture() -> dict[str, Any]:
    source = _load_source_module()
    registry = _read_registry(source)
    states = [source.sample_source(registry, index) for index in range(3)]
    for state in states:
        source.validate_source_sample(state, registry)

    if [state["validity"]["status"] for state in states] != [
        "source_invalid",
        "source_invalid",
        "valid",
    ]:
        fail("pre_registered_selection", "indices 0..2 have unexpected statuses")
    if states[0]["source_state_sha256"] != FIRST_SOURCE_INVALID_STATE_SHA256:
        fail("source_state_hash", "index 0 state hash changed")
    if states[2]["source_state_sha256"] != FIRST_VALID_STATE_SHA256:
        fail("source_state_hash", "index 2 state hash changed")

    solver_probe = NeverCalled("event solver")
    arb_probe = NeverCalled("Arb evaluator")
    invalid_route, invalid_problem = route_source_state(
        states[0], registry, solver_probe, arb_probe
    )
    if (
        invalid_problem is not None
        or solver_probe.calls != 0
        or arb_probe.calls != 0
    ):
        fail("source_invalid_short_circuit", "invalid route touched a backend")

    valid_route, physical_problem = route_source_state(
        states[2],
        registry,
        NeverCalled("event solver"),
        NeverCalled("Arb evaluator"),
    )
    if physical_problem is None:
        fail("validity_route", "valid source did not produce a physical problem")
    problem_digest = verify_physical_problem(physical_problem)

    return {
        "schema_version": FIXTURE_SCHEMA,
        "registry_commitment": {
            "path": "artifacts/0018/source_registry.json",
            "registry_canonical_sha256": REGISTRY_CANONICAL_SHA256,
            "source_draw_sha256": SOURCE_DRAW_SHA256,
        },
        "pre_registered_selection": {
            "rule": "least source index for each required validity status",
            "scanned_indices": [
                {
                    "sample_index": state["sample_index"],
                    "source_state_sha256": state["source_state_sha256"],
                    "validity_status": state["validity"]["status"],
                }
                for state in states
            ],
            "first_source_invalid_index": FIRST_SOURCE_INVALID_INDEX,
            "first_valid_index": FIRST_VALID_INDEX,
        },
        "selected_source_states": {
            "source_invalid_control": _state_record(states[0]),
            "valid_physical_control": _state_record(states[2]),
        },
        "routes": {
            "source_invalid_control": invalid_route,
            "valid_physical_control": valid_route,
        },
        "physical_problem": physical_problem,
        "physical_problem_semantic_sha256": problem_digest,
    }


def _verify_state_record(
    record: Any,
    expected_state: Mapping[str, Any],
    expected_index: int,
    expected_status: str,
    expected_hash: str,
    path: str,
) -> None:
    obj = _exact_keys(
        record,
        {
            "sample_index",
            "source_state_sha256",
            "validity_status",
            "complete_serialized_source_state_binary64",
            "complete_exact_dyadic_projection",
            "complete_serialized_state_semantic_sha256",
            "complete_dyadic_projection_semantic_sha256",
        },
        path,
        "source_state",
    )
    if obj["sample_index"] != expected_index:
        fail("source_index", f"{path} has the wrong source index")
    if obj["validity_status"] != expected_status:
        fail("validity_route", f"{path} has the wrong validity status")
    if obj["source_state_sha256"] != expected_hash:
        fail("source_state_hash", f"{path} has the wrong state hash")
    decoded = decode_binary64_tree(
        obj["complete_serialized_source_state_binary64"],
        f"{path}.complete_serialized_source_state_binary64",
    )
    if not type_strict_equal(decoded, expected_state):
        fail("source_replay", f"{path} serialized state differs from regeneration")
    core_digest = hashlib.sha256(
        json.dumps(
            _source_core(decoded),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    ).hexdigest()
    if core_digest != expected_hash or decoded["source_state_sha256"] != expected_hash:
        fail("source_state_hash", f"{path} regenerated core hash differs")
    encoded = obj["complete_serialized_source_state_binary64"]
    if semantic_sha256(encoded) != obj["complete_serialized_state_semantic_sha256"]:
        fail("source_state_hash", f"{path} complete state digest differs")
    projection = obj["complete_exact_dyadic_projection"]
    _assert_all_dyadics(projection, f"{path}.complete_exact_dyadic_projection")
    expected_projection = exact_dyadic_tree(decoded)
    if not type_strict_equal(projection, expected_projection):
        fail("coefficient_projection", f"{path} dyadic projection differs")
    if semantic_sha256(projection) != obj[
        "complete_dyadic_projection_semantic_sha256"
    ]:
        fail("coefficient_projection", f"{path} dyadic projection digest differs")


def verify_fixture(fixture: Any) -> dict[str, Any]:
    """Replay source generation, selection, route, projection and commitment."""

    obj = _exact_keys(
        fixture,
        {
            "schema_version",
            "registry_commitment",
            "pre_registered_selection",
            "selected_source_states",
            "routes",
            "physical_problem",
            "physical_problem_semantic_sha256",
        },
        "$",
        "fixture_schema",
    )
    if obj["schema_version"] != FIXTURE_SCHEMA:
        fail("fixture_schema", "unsupported fixture schema")

    source = _load_source_module()
    registry = _read_registry(source)
    registry_commitment = _exact_keys(
        obj["registry_commitment"],
        {
            "path",
            "registry_canonical_sha256",
            "source_draw_sha256",
        },
        "$.registry_commitment",
        "registry_commitment",
    )
    if (
        registry_commitment["path"] != "artifacts/0018/source_registry.json"
        or registry_commitment["registry_canonical_sha256"]
        != REGISTRY_CANONICAL_SHA256
        or registry_commitment["source_draw_sha256"] != SOURCE_DRAW_SHA256
    ):
        fail("registry_commitment", "fixture registry commitment is not pinned")

    states = [source.sample_source(registry, index) for index in range(3)]
    for state in states:
        source.validate_source_sample(state, registry)
    selection = _exact_keys(
        obj["pre_registered_selection"],
        {
            "rule",
            "scanned_indices",
            "first_source_invalid_index",
            "first_valid_index",
        },
        "$.pre_registered_selection",
        "pre_registered_selection",
    )
    if (
        selection["rule"]
        != "least source index for each required validity status"
        or selection["first_source_invalid_index"] != 0
        or selection["first_valid_index"] != 2
    ):
        fail("pre_registered_selection", "selection rule or selected index changed")
    expected_rows = [
        {
            "sample_index": state["sample_index"],
            "source_state_sha256": state["source_state_sha256"],
            "validity_status": state["validity"]["status"],
        }
        for state in states
    ]
    if not type_strict_equal(selection["scanned_indices"], expected_rows):
        fail(
            "pre_registered_selection",
            "indices 0..2 do not prove the least-status selection",
        )
    invalid_indices = [
        row["sample_index"]
        for row in expected_rows
        if row["validity_status"] == "source_invalid"
    ]
    valid_indices = [
        row["sample_index"]
        for row in expected_rows
        if row["validity_status"] == "valid"
    ]
    if min(invalid_indices) != 0 or min(valid_indices) != 2:
        fail("pre_registered_selection", "least-status witnesses are false")

    records = _exact_keys(
        obj["selected_source_states"],
        {"source_invalid_control", "valid_physical_control"},
        "$.selected_source_states",
        "source_state",
    )
    _verify_state_record(
        records["source_invalid_control"],
        states[0],
        0,
        "source_invalid",
        FIRST_SOURCE_INVALID_STATE_SHA256,
        "$.selected_source_states.source_invalid_control",
    )
    _verify_state_record(
        records["valid_physical_control"],
        states[2],
        2,
        "valid",
        FIRST_VALID_STATE_SHA256,
        "$.selected_source_states.valid_physical_control",
    )

    routes = _exact_keys(
        obj["routes"],
        {"source_invalid_control", "valid_physical_control"},
        "$.routes",
        "validity_route",
    )
    invalid_probe_solver = NeverCalled("event solver")
    invalid_probe_arb = NeverCalled("Arb evaluator")
    expected_invalid_route, invalid_problem = route_source_state(
        states[0], registry, invalid_probe_solver, invalid_probe_arb
    )
    if invalid_problem is not None:
        fail("source_invalid_short_circuit", "invalid problem was constructed")
    if (
        invalid_probe_solver.calls != 0
        or invalid_probe_arb.calls != 0
        or not type_strict_equal(
            routes["source_invalid_control"], expected_invalid_route
        )
    ):
        fail("source_invalid_short_circuit", "invalid route did not short-circuit")

    expected_problem = build_physical_problem(states[2], registry)
    valid_route, routed_problem = route_source_state(
        states[2],
        registry,
        NeverCalled("event solver"),
        NeverCalled("Arb evaluator"),
    )
    if routed_problem is None or not type_strict_equal(routed_problem, expected_problem):
        fail("physical_projection", "valid route did not reproduce the problem")
    if not type_strict_equal(routes["valid_physical_control"], valid_route):
        fail("validity_route", "valid route record differs")

    problem_digest = verify_physical_problem(obj["physical_problem"])
    if obj["physical_problem_semantic_sha256"] != problem_digest:
        fail("problem_commitment", "stored physical problem digest differs")
    if not type_strict_equal(obj["physical_problem"], expected_problem):
        fail(
            "physical_projection",
            "physical problem differs from regenerated source projection",
        )
    return {
        "registry_canonical_sha256": REGISTRY_CANONICAL_SHA256,
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "first_source_invalid_index": 0,
        "first_valid_index": 2,
        "source_invalid_backends_executed": False,
        "physical_problem_semantic_sha256": problem_digest,
    }


def build_report(fixture: Mapping[str, Any]) -> dict[str, Any]:
    replay = verify_fixture(fixture)
    hostile = _hostile_checks(fixture)
    if not all(hostile.values()):
        fail("hostile_controls", "one or more hostile mutations were accepted")
    inventory = []
    for relative in BRIDGE_INVENTORY:
        path = REPOSITORY_ROOT / relative
        inventory.append(
            {
                "path": relative,
                "normalized_lf_sha256": normalized_lf_sha256(path),
            }
        )
    report = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "fixture_semantic_sha256": semantic_sha256(fixture),
        "checks": {
            "registry_hash_recomputed_and_pinned": True,
            "source_draw_hash_recomputed_and_pinned": True,
            "index_0_is_least_source_invalid": True,
            "index_2_is_least_valid": True,
            "state_hashes_match_brief": True,
            "complete_source_state_recomputed": True,
            "every_binary64_has_canonical_dyadic_projection": True,
            "source_invalid_executes_no_solver_or_arb": True,
            "physical_problem_is_rank_blind": True,
            "q_enters_each_embedding_once": True,
            "f1_tension_and_winding_relations_replayed": True,
            "arb_9d_jet_ingress_declared": True,
        },
        "commitments": replay,
        "hostile_controls": hostile,
        "normalized_lf_inventory": inventory,
        "scope": {
            "claim": (
                "index 2 is bound to one exact-dyadic rank-blind 9D physical "
                "problem and index 0 is routed source_invalid before backends"
            ),
            "does_not_claim": [
                "source-separated independent binding replay",
                "exhaustive worldsheet roots",
                "population law",
                "3+1 selection",
            ],
        },
    }
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def verify_report(report: Any, fixture: Mapping[str, Any]) -> str:
    """Replay report status and both artifact-level semantic commitments."""

    obj = _exact_keys(
        report,
        {
            "schema_version",
            "status",
            "failed_gates",
            "fixture_semantic_sha256",
            "report_semantic_sha256",
            "checks",
            "commitments",
            "normalized_lf_inventory",
            "scope",
            "hostile_controls",
        },
        "$.report",
        "report_schema",
    )
    if obj["schema_version"] != REPORT_SCHEMA:
        fail("report_schema", "unsupported report schema")
    if obj["status"] != "passed":
        fail("report_status", "committed report status must be passed")
    if type(obj["failed_gates"]) is not list or obj["failed_gates"]:
        fail("report_status", "passed report must have no failed gates")
    checks = obj["checks"]
    hostile = obj["hostile_controls"]
    if (
        type(checks) is not dict
        or not checks
        or any(type(value) is not bool or not value for value in checks.values())
    ):
        fail("report_status", "all named report checks must be true Booleans")
    if (
        type(hostile) is not dict
        or not hostile
        or any(type(value) is not bool or not value for value in hostile.values())
    ):
        fail("report_status", "all named hostile controls must be true Booleans")
    replay = verify_fixture(fixture)
    if not type_strict_equal(obj["commitments"], replay):
        fail("report_replay", "report commitments differ from fixture replay")
    expected_inventory = [
        {
            "path": relative,
            "normalized_lf_sha256": normalized_lf_sha256(
                REPOSITORY_ROOT / relative
            ),
        }
        for relative in BRIDGE_INVENTORY
    ]
    if not type_strict_equal(obj["normalized_lf_inventory"], expected_inventory):
        fail("report_inventory", "normalized-LF inventory differs")
    fixture_digest = _sha256(
        obj["fixture_semantic_sha256"],
        "$.report.fixture_semantic_sha256",
        "report_hash",
    )
    if fixture_digest != semantic_sha256(fixture):
        fail("report_hash", "report does not bind the complete fixture")
    stored_digest = _sha256(
        obj["report_semantic_sha256"],
        "$.report.report_semantic_sha256",
        "report_hash",
    )
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    computed_digest = semantic_sha256(payload)
    if stored_digest != computed_digest:
        fail("report_hash", "report semantic digest does not replay")
    return computed_digest


def _hostile_checks(fixture: Mapping[str, Any]) -> dict[str, bool]:
    def rejected(mutator: Callable[[dict[str, Any]], None]) -> bool:
        hostile = copy.deepcopy(fixture)
        mutator(hostile)
        try:
            verify_fixture(hostile)
        except BridgeError:
            return True
        return False

    one = dyadic(1.0)
    return {
        "coefficient_mutation_rejected": rejected(
            lambda value: value["physical_problem"]["kinematics"]["strings"][0][
                "modes"
            ][0]["initial_x"].__setitem__(0, one)
        ),
        "state_hash_mutation_rejected": rejected(
            lambda value: value["selected_source_states"][
                "valid_physical_control"
            ].__setitem__("source_state_sha256", "0" * 64)
        ),
        "registry_hash_mutation_rejected": rejected(
            lambda value: value["registry_commitment"].__setitem__(
                "registry_canonical_sha256", "0" * 64
            )
        ),
        "orientation_mutation_rejected": rejected(
            lambda value: value["physical_problem"]["worldsheet"].__setitem__(
                "winding_orientations", [-1, 1]
            )
        ),
        "wave_number_mutation_rejected": rejected(
            lambda value: value["physical_problem"]["kinematics"]["strings"][0][
                "modes"
            ][0].__setitem__("wave_number", dyadic(0.25))
        ),
        "validity_mutation_rejected": rejected(
            lambda value: value["selected_source_states"][
                "source_invalid_control"
            ].__setitem__("validity_status", "valid")
        ),
        "index_mutation_rejected": rejected(
            lambda value: value["physical_problem"]["source_commitment"].__setitem__(
                "source_sample_index", 3
            )
        ),
        "rank_field_mutation_rejected": rejected(
            lambda value: value["physical_problem"].__setitem__("rank", 2)
        ),
    }


def run(write: bool) -> dict[str, Any]:
    fixture = build_fixture()
    if not PHYSICAL_PROBLEM_SEMANTIC_SHA256:
        fail(
            "problem_commitment",
            "PHYSICAL_PROBLEM_SEMANTIC_SHA256 has not been source-code pinned",
        )
    if write:
        write_json(FIXTURE_PATH, fixture)
    else:
        stored_fixture = strict_json_load(FIXTURE_PATH)
        verify_fixture(stored_fixture)
        if not type_strict_equal(stored_fixture, fixture):
            fail("fixture_reproduction", "stored fixture differs from fresh build")

    report = build_report(fixture)
    verify_report(report, fixture)
    if write:
        write_json(REPORT_PATH, report)
    else:
        stored_report = strict_json_load(REPORT_PATH)
        verify_report(stored_report, stored_fixture)
        if not type_strict_equal(stored_report, report):
            fail("report_reproduction", "stored report differs from fresh replay")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or replay the pinned Brief 0019 source bridge"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    report = run(write=arguments.write)
    print(pretty_json(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
