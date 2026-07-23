#!/usr/bin/env python3
"""Canonical symbolic-pi closed-string lift for Brief 0019.

This module replaces the cut-open binary64 circumference by an exact
closed-string chart while preserving the already committed index-2 source
state coefficient-for-coefficient.  Its scalar boundary is the strict,
canonical atom

    {"numerator": q_num, "denominator": q_den, "pi_exponent": e}

with value ``(q_num/q_den) * pi**e``.  It is intentionally only a
fixed-index deterministic lift.  It does not assert a population
pushforward, a Jacobian, an entry law, or dimensional selection.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


FIXTURE_SCHEMA = "cyz-brief-0019-symbolic-pi-lift-fixture-v1"
REPORT_SCHEMA = "cyz-brief-0019-symbolic-pi-lift-report-v1"
SCALAR_SCHEMA = "cyz-canonical-rational-times-pi-power-v1"
LIFT_REGISTRY_SCHEMA = "cyz-brief-0019-symbolic-pi-lift-registry-v1"
PROBLEM_SCHEMA = "cyz-brief-0019-symbolic-pi-closed-string-problem-v1"
EQUATION_FAMILY_VERSION = "f1-normalized-closed-string-k1-v1"

SOURCE_BRIDGE_FIXTURE_SEMANTIC_SHA256 = (
    "5af600527155e1c1dbd68b8e531aa1a640e4ee2edb8317f46334ac6b219dee60"
)
LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)
SOURCE_REGISTRY_CANONICAL_SHA256 = (
    "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb"
)
SOURCE_DRAW_SHA256 = (
    "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4"
)
SOURCE_STATE_SHA256 = (
    "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c"
)
SOURCE_SAMPLE_INDEX = 2

# Filled after the canonical schemas were frozen.  These are source-code
# trust anchors in addition to the digests stored in the fixture.
LIFT_REGISTRY_SEMANTIC_SHA256 = (
    "c80acb64eeeb3133dff4422fc798f5b75c6feb52cf32502888cac452e2d210a1"
)
CLOSED_STRING_PROBLEM_SEMANTIC_SHA256 = (
    "3bb6599f211c26d98ecba2077051ad9d0339daf96d580a6399cc5a1ba7f030e0"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
SOURCE_BRIDGE_FIXTURE_PATH = ARTIFACT_DIR / "source_state_bridge_fixture.json"
FIXTURE_PATH = ARTIFACT_DIR / "symbolic_pi_lift_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "symbolic_pi_lift_report.json"

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
ATOM_KEYS = {"numerator", "denominator", "pi_exponent"}
DYADIC_KEYS = {"numerator", "exponent"}
VARIABLE_ORDER = ("u1", "u2", "t")
TARGET_DIMENSION = 9
TRANSVERSE_DIMENSION = 8
WINDING_AXIS = 8
PI_EXPONENT_MIN = -16
PI_EXPONENT_MAX = 16


class LiftError(ValueError):
    """A symbolic lift failed at a named semantic gate."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise LiftError(gate, message)


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


def _integer(value: Any, path: str, gate: str) -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer; booleans are forbidden")
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


def _list(
    value: Any, length: int | None, path: str, gate: str
) -> list[Any]:
    if type(value) is not list:
        fail(gate, f"{path} must be an array")
    if length is not None and len(value) != length:
        fail(gate, f"{path} must have length {length}")
    return value


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
        f"ordinary JSON float {token!r} is forbidden; use q*pi^e atoms",
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


def normalized_lf_sha256(path: Path) -> str:
    payload = (
        path.read_bytes()
        .replace(b"\r\n", b"\n")
        .replace(b"\r", b"\n")
    )
    return hashlib.sha256(payload).hexdigest()


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


def symbolic_atom(
    numerator: int | Fraction,
    denominator: int = 1,
    pi_exponent: int = 0,
) -> dict[str, int]:
    """Return the unique reduced encoding of ``q*pi**e``."""

    if type(denominator) is not int or type(pi_exponent) is not int:
        fail("symbolic_atom", "denominator and pi exponent must be integers")
    if denominator == 0:
        fail("symbolic_atom", "zero denominator is forbidden")
    if isinstance(numerator, Fraction):
        if denominator != 1:
            fail(
                "symbolic_atom",
                "a Fraction coefficient cannot have a second denominator",
            )
        coefficient = numerator
    else:
        if type(numerator) is not int:
            fail("symbolic_atom", "numerator must be an integer or Fraction")
        coefficient = Fraction(numerator, denominator)
    if coefficient == 0:
        return {"numerator": 0, "denominator": 1, "pi_exponent": 0}
    if not PI_EXPONENT_MIN <= pi_exponent <= PI_EXPONENT_MAX:
        fail(
            "symbolic_atom",
            "pi exponent lies outside the versioned grammar bound",
        )
    return {
        "numerator": coefficient.numerator,
        "denominator": coefficient.denominator,
        "pi_exponent": pi_exponent,
    }


def parse_symbolic_atom(value: Any, path: str = "$") -> tuple[Fraction, int]:
    """Parse and validate the strict canonical ``q*pi**e`` atom."""

    atom = _exact_keys(value, ATOM_KEYS, path, "symbolic_atom")
    numerator = _integer(
        atom["numerator"], f"{path}.numerator", "symbolic_atom"
    )
    denominator = _integer(
        atom["denominator"], f"{path}.denominator", "symbolic_atom"
    )
    exponent = _integer(
        atom["pi_exponent"], f"{path}.pi_exponent", "symbolic_atom"
    )
    if denominator <= 0:
        fail("symbolic_atom", f"{path}.denominator must be positive")
    if math.gcd(abs(numerator), denominator) != 1:
        fail("symbolic_atom", f"{path} rational coefficient is not reduced")
    if numerator == 0 and (denominator != 1 or exponent != 0):
        fail(
            "symbolic_atom",
            f"{path} zero must be encoded exactly as {{0,1,0}}",
        )
    if not PI_EXPONENT_MIN <= exponent <= PI_EXPONENT_MAX:
        fail(
            "symbolic_atom",
            f"{path}.pi_exponent lies outside the versioned grammar bound",
        )
    return Fraction(numerator, denominator), exponent


def atom_multiply(*values: Mapping[str, int]) -> dict[str, int]:
    coefficient = Fraction(1)
    exponent = 0
    for index, value in enumerate(values):
        q, power = parse_symbolic_atom(value, f"$multiply[{index}]")
        coefficient *= q
        exponent += power
    return symbolic_atom(coefficient, pi_exponent=exponent)


def atom_divide(
    numerator: Mapping[str, int], denominator: Mapping[str, int]
) -> dict[str, int]:
    q_num, e_num = parse_symbolic_atom(numerator, "$divide.numerator")
    q_den, e_den = parse_symbolic_atom(
        denominator, "$divide.denominator"
    )
    if q_den == 0:
        fail("symbolic_atom", "division by zero")
    return symbolic_atom(q_num / q_den, pi_exponent=e_num - e_den)


def atom_power(value: Mapping[str, int], exponent: int) -> dict[str, int]:
    if type(exponent) is not int:
        fail("symbolic_atom", "power must be an integer")
    q, pi_power = parse_symbolic_atom(value, "$power.base")
    if q == 0 and exponent < 0:
        fail("symbolic_atom", "negative power of zero")
    return symbolic_atom(q**exponent, pi_exponent=pi_power * exponent)


def parse_dyadic(value: Any, path: str = "$") -> Fraction:
    dyadic = _exact_keys(value, DYADIC_KEYS, path, "upstream_dyadic")
    numerator = _integer(
        dyadic["numerator"], f"{path}.numerator", "upstream_dyadic"
    )
    exponent = _integer(
        dyadic["exponent"], f"{path}.exponent", "upstream_dyadic"
    )
    if exponent < 0:
        fail("upstream_dyadic", f"{path}.exponent must be nonnegative")
    if numerator == 0:
        if exponent != 0:
            fail("upstream_dyadic", f"{path} has noncanonical zero")
    elif exponent > 0 and numerator % 2 == 0:
        fail("upstream_dyadic", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


def dyadic_to_atom(value: Any, path: str = "$") -> dict[str, int]:
    return symbolic_atom(parse_dyadic(value, path))


def _validate_upstream_fixture(fixture: Any) -> dict[str, Any]:
    if semantic_sha256(fixture) != SOURCE_BRIDGE_FIXTURE_SEMANTIC_SHA256:
        fail(
            "upstream_fixture",
            "source-state bridge fixture semantic hash differs",
        )
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
        "$.source_bridge_fixture",
        "upstream_fixture",
    )
    if (
        obj["schema_version"]
        != "cyz-brief-0019-source-state-bridge-fixture-v1"
    ):
        fail("upstream_fixture", "unexpected source bridge schema")
    if (
        obj["physical_problem_semantic_sha256"]
        != LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256
        or semantic_sha256(obj["physical_problem"])
        != LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256
    ):
        fail("upstream_fixture", "legacy physical problem hash differs")
    registry = obj["registry_commitment"]
    if (
        registry["registry_canonical_sha256"]
        != SOURCE_REGISTRY_CANONICAL_SHA256
        or registry["source_draw_sha256"] != SOURCE_DRAW_SHA256
    ):
        fail("upstream_fixture", "Brief 0018 source hashes differ")
    record = obj["selected_source_states"]["valid_physical_control"]
    if (
        record["sample_index"] != SOURCE_SAMPLE_INDEX
        or record["validity_status"] != "valid"
        or record["source_state_sha256"] != SOURCE_STATE_SHA256
    ):
        fail("upstream_fixture", "selected source is not valid index 2")
    problem_commitment = obj["physical_problem"]["source_commitment"]
    if (
        problem_commitment["source_sample_index"] != SOURCE_SAMPLE_INDEX
        or problem_commitment["source_state_sha256"] != SOURCE_STATE_SHA256
        or problem_commitment["source_draw_sha256"] != SOURCE_DRAW_SHA256
        or problem_commitment["source_registry_canonical_sha256"]
        != SOURCE_REGISTRY_CANONICAL_SHA256
    ):
        fail("upstream_fixture", "physical source commitment differs")
    return obj


def load_upstream_fixture() -> dict[str, Any]:
    return _validate_upstream_fixture(
        strict_json_load(SOURCE_BRIDGE_FIXTURE_PATH)
    )


def _source_provenance(upstream: Mapping[str, Any]) -> dict[str, Any]:
    record = upstream["selected_source_states"]["valid_physical_control"]
    source_state = record["complete_serialized_source_state_binary64"]
    return {
        "source_bridge_fixture_semantic_sha256": (
            SOURCE_BRIDGE_FIXTURE_SEMANTIC_SHA256
        ),
        "legacy_cut_open_physical_problem_semantic_sha256": (
            LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256
        ),
        "legacy_problem_role": (
            "provenance_only_not_a_closed_string_problem_identifier"
        ),
        "source_registry_canonical_sha256": (
            SOURCE_REGISTRY_CANONICAL_SHA256
        ),
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "source_sample_index": SOURCE_SAMPLE_INDEX,
        "source_sample_schema": source_state["schema_version"],
        "source_state_sha256": SOURCE_STATE_SHA256,
        "complete_exact_dyadic_projection_semantic_sha256": record[
            "complete_dyadic_projection_semantic_sha256"
        ],
        "complete_serialized_state_semantic_sha256": record[
            "complete_serialized_state_semantic_sha256"
        ],
    }


def build_lift_registry(
    upstream: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_upstream_fixture(upstream)
    zero = symbolic_atom(0)
    one = symbolic_atom(1)
    length = symbolic_atom(16, pi_exponent=1)
    tension = symbolic_atom(1, 2, -1)
    mass = symbolic_atom(8)
    k_one = symbolic_atom(1, 8)
    phase_one = symbolic_atom(2, pi_exponent=1)
    return {
        "schema_version": LIFT_REGISTRY_SCHEMA,
        "registry_id": "index2-symbolic-pi-closed-string-lift-v1",
        "scalar_grammar": {
            "schema_version": SCALAR_SCHEMA,
            "atom_keys": [
                "numerator",
                "denominator",
                "pi_exponent",
            ],
            "semantics": "(numerator/denominator)*pi^pi_exponent",
            "canonical_rational": (
                "gcd(abs(numerator),denominator)=1; denominator>0"
            ),
            "canonical_zero": zero,
            "pi_exponent_min": PI_EXPONENT_MIN,
            "pi_exponent_max": PI_EXPONENT_MAX,
            "ordinary_json_floats_forbidden": True,
            "booleans_as_integers_forbidden": True,
            "duplicate_object_keys_forbidden": True,
        },
        "upstream_provenance": _source_provenance(upstream),
        "exact_parameters": {
            "ell_s": one,
            "L_star": length,
            "T_F": tension,
            "M": mass,
            "K": 1,
            "k_1": k_one,
        },
        "exact_identities": {
            "T_F_times_L_star": {
                "lhs": atom_multiply(tension, length),
                "rhs_M": mass,
            },
            "k_1_times_L_star": {
                "lhs": atom_multiply(k_one, length),
                "rhs_2pi": phase_one,
            },
            "winding_metric": {
                "lhs_L_star_squared": atom_power(length, 2),
                "rhs_G_ww": symbolic_atom(256, pi_exponent=2),
            },
        },
        "coordinate_chart": {
            "variable_order": list(VARIABLE_ORDER),
            "normalized_worldsheet_quotients": {
                "u1": "R/Z",
                "u2": "R/Z",
                "t": "not_a_quotient",
            },
            "sigma_relation": "sigma_i=L_star*u_i",
            "transverse_mode_phase": "2*pi*n*u_i",
            "normalized_winding_coordinate": "xi_i^w=o_i*u_i",
            "target_periods": [symbolic_atom(8) for _ in range(8)]
            + [one],
            "target_metric_diagonal": [one for _ in range(8)]
            + [symbolic_atom(256, pi_exponent=2)],
        },
        "source_transport": {
            "coefficient_map": (
                "identity_after_exact_dyadic_to_q*pi^0_reencoding"
            ),
            "source_draw_bytes_changed": False,
            "source_coefficients_changed": False,
            "invariants": {
                "M": mass,
                "k_1": k_one,
            },
            "measure_scope": (
                "fixed_index_deterministic_identity_only"
            ),
            "does_not_claim": [
                "population_pushforward",
                "measure_preserving_jacobian",
                "entry_probability",
            ],
        },
        "arb_backend_registry": {
            "implementation": "python-flint Arb",
            "python_flint_version": "0.9.0",
            "flint_version": "3.6.0",
            "precision_bits": 192,
            "symbolic_ingress": (
                "construct rational exactly; evaluate pi with Arb outward "
                "rounding; never substitute binary64(pi)"
            ),
        },
        "scope": {
            "claim": (
                "exact fixed-index source-preserving closed-string "
                "coordinate lift"
            ),
            "does_not_claim": [
                "worldsheet entry or no-entry",
                "population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }


def _convert_vector(
    values: Any, length: int, path: str
) -> list[dict[str, int]]:
    return [
        dyadic_to_atom(item, f"{path}[{index}]")
        for index, item in enumerate(_list(values, length, path, "source"))
    ]


def _convert_strings(old_problem: Mapping[str, Any]) -> list[dict[str, Any]]:
    old_strings = _list(
        old_problem["kinematics"]["strings"],
        2,
        "$.old_problem.kinematics.strings",
        "source",
    )
    result: list[dict[str, Any]] = []
    for string_index, old_value in enumerate(old_strings):
        old = _exact_keys(
            old_value,
            {
                "string_id",
                "orientation",
                "centre_reference",
                "transverse_velocity",
                "modes",
            },
            f"$.old_problem.kinematics.strings[{string_index}]",
            "source",
        )
        modes = []
        for mode_index, mode_value in enumerate(
            _list(
                old["modes"],
                None,
                f"$.old_problem.kinematics.strings[{string_index}].modes",
                "source",
            )
        ):
            mode = _exact_keys(
                mode_value,
                {
                    "mode_number",
                    "wave_number",
                    "initial_x",
                    "initial_y",
                    "initial_p",
                    "initial_q",
                },
                (
                    "$.old_problem.kinematics.strings"
                    f"[{string_index}].modes[{mode_index}]"
                ),
                "source",
            )
            harmonic = _integer(
                mode["mode_number"],
                (
                    "$.old_problem.kinematics.strings"
                    f"[{string_index}].modes[{mode_index}].mode_number"
                ),
                "source",
            )
            if harmonic <= 0:
                fail("source", "Fourier harmonics must be positive")
            expected_frequency = Fraction(harmonic, 8)
            if parse_dyadic(mode["wave_number"]) != expected_frequency:
                fail(
                    "source",
                    "source wave number is not the invariant n/8",
                )
            base = (
                "$.old_problem.kinematics.strings"
                f"[{string_index}].modes[{mode_index}]"
            )
            modes.append(
                {
                    "mode_number": harmonic,
                    "temporal_angular_frequency": symbolic_atom(
                        expected_frequency
                    ),
                    "wave_number": symbolic_atom(expected_frequency),
                    "spatial_phase_coefficient": symbolic_atom(
                        2 * harmonic, pi_exponent=1
                    ),
                    "initial_x": _convert_vector(
                        mode["initial_x"], 8, f"{base}.initial_x"
                    ),
                    "initial_y": _convert_vector(
                        mode["initial_y"], 8, f"{base}.initial_y"
                    ),
                    "initial_p": _convert_vector(
                        mode["initial_p"], 8, f"{base}.initial_p"
                    ),
                    "initial_q": _convert_vector(
                        mode["initial_q"], 8, f"{base}.initial_q"
                    ),
                }
            )
        result.append(
            {
                "string_id": old["string_id"],
                "orientation": old["orientation"],
                "centre_reference": old["centre_reference"],
                "transverse_velocity": _convert_vector(
                    old["transverse_velocity"],
                    8,
                    (
                        "$.old_problem.kinematics.strings"
                        f"[{string_index}].transverse_velocity"
                    ),
                ),
                "modes": modes,
            }
        )
    return result


def build_closed_string_problem(
    upstream: Mapping[str, Any],
    lift_registry_semantic_sha256: str,
) -> dict[str, Any]:
    _validate_upstream_fixture(upstream)
    _sha256(
        lift_registry_semantic_sha256,
        "$.lift_registry_semantic_sha256",
        "lift_registry_hash",
    )
    old = upstream["physical_problem"]
    old_kinematics = old["kinematics"]
    old_observation = old["observation"]
    old_hysteresis = old["hysteresis"]
    old_centres = old_kinematics["centres_Q1_Q2"]
    zero = symbolic_atom(0)
    one = symbolic_atom(1)
    orientations = [
        string["orientation"] for string in old_kinematics["strings"]
    ]
    if orientations != [1, -1]:
        fail("orientation", "source orientations are not (+1,-1)")
    a1 = orientations[0]
    a2 = -orientations[1]
    corner = a1 + a2
    t0 = dyadic_to_atom(old_observation["t0"])
    t1 = dyadic_to_atom(old_observation["t1"])
    return {
        "schema_version": PROBLEM_SCHEMA,
        "problem_id": "index2-symbolic-pi-closed-string-v1",
        "equation_family_version": EQUATION_FAMILY_VERSION,
        "lift_registry_semantic_sha256": (
            lift_registry_semantic_sha256
        ),
        "source_commitment": {
            "source_registry_canonical_sha256": (
                SOURCE_REGISTRY_CANONICAL_SHA256
            ),
            "source_draw_sha256": SOURCE_DRAW_SHA256,
            "source_sample_index": SOURCE_SAMPLE_INDEX,
            "source_state_sha256": SOURCE_STATE_SHA256,
            "coefficient_transport": (
                "exact_dyadic_to_canonical_q*pi^0_identity"
            ),
        },
        "dimensions": {
            "target": TARGET_DIMENSION,
            "target_axis_order": list(range(TARGET_DIMENSION)),
            "transverse": TRANSVERSE_DIMENSION,
            "transverse_axis_order": list(range(TRANSVERSE_DIMENSION)),
            "winding_axis": WINDING_AXIS,
        },
        "exact_parameters": {
            "L_star": symbolic_atom(16, pi_exponent=1),
            "T_F": symbolic_atom(1, 2, -1),
            "M": symbolic_atom(8),
            "ell_s": one,
            "K": 1,
        },
        "variable_registry": {
            "variable_order": list(VARIABLE_ORDER),
            "domains": {
                "u1": {
                    "lower": zero,
                    "upper": one,
                    "closure": "lower_closed_upper_open",
                    "quotient": "R/Z",
                },
                "u2": {
                    "lower": zero,
                    "upper": one,
                    "closure": "lower_closed_upper_open",
                    "quotient": "R/Z",
                },
                "t": {
                    "lower": t0,
                    "upper": t1,
                    "closure": old_observation["window_closure"],
                    "quotient": "none",
                },
            },
        },
        "target_torus": {
            "periods": [symbolic_atom(8) for _ in range(8)]
            + [one],
            "lattice_matrix_diagonal": [
                symbolic_atom(8) for _ in range(8)
            ]
            + [one],
            "metric_diagonal": [one for _ in range(8)]
            + [symbolic_atom(256, pi_exponent=2)],
            "lattice_convention": (
                "Lambda=diag(8,...,8,1) in normalized coordinates"
            ),
            "metric_convention": (
                "G=diag(1,...,1,(16*pi)^2)"
            ),
            "image_separation": "s_n=d-Lambda*n for n in Z^9",
        },
        "solver_geometry": {
            "domain_metric_diagonal": [
                symbolic_atom(256, pi_exponent=2),
                symbolic_atom(256, pi_exponent=2),
                one,
            ],
            "coordinate_jacobian_chart": list(VARIABLE_ORDER),
            "krawczyk_rule": (
                "use the coordinate Jacobian in the registered "
                "(u1,u2,t) chart"
            ),
            "rank_rule": (
                "certify exact rank by minors or interval exclusion; "
                "rank is invariant under this invertible chart change"
            ),
            "physical_singular_value_formula": (
                "G^(1/2)*J*H^(-1/2)"
            ),
        },
        "worldsheet": {
            "coordinate_units": "u_i=sigma_i/L_star",
            "orientations": orientations,
            "winding_embedding": "xi_i^w=o_i*u_i",
            "winding_separation": "d_w=o1*u1-o2*u2",
            "seam_image_actions": {
                "u1_plus_1": {
                    "parameter_shift": [1, 0, 0],
                    "separation_winding_shift": a1,
                    "n8_reindex_shift": a1,
                    "exact_rule": "a1=o1",
                },
                "u2_plus_1": {
                    "parameter_shift": [0, 1, 0],
                    "separation_winding_shift": a2,
                    "n8_reindex_shift": a2,
                    "exact_rule": "a2=-o2",
                },
                "corner_plus_1_plus_1": {
                    "parameter_shift": [1, 1, 0],
                    "separation_winding_shift": corner,
                    "n8_reindex_shift": corner,
                    "exact_rule": "a12=a1+a2",
                },
            },
            "transverse_seam_identity": (
                "integer n gives exp(i*2*pi*n*(u+1))="
                "exp(i*2*pi*n*u)"
            ),
            "seam_claim": (
                "exact target-lattice reindexing, not endpoint "
                "floating-point comparison"
            ),
            "upper_to_lower_reindex_rule": (
                "n_lower=n_upper-a_i*e_w"
            ),
        },
        "kinematics": {
            "initial_time": dyadic_to_atom(
                old_kinematics["initial_time"]
            ),
            "centres_Q1_Q2": {
                "Q1": _convert_vector(
                    old_centres["Q1"],
                    8,
                    "$.old_problem.kinematics.centres_Q1_Q2.Q1",
                ),
                "Q2": _convert_vector(
                    old_centres["Q2"],
                    8,
                    "$.old_problem.kinematics.centres_Q1_Q2.Q2",
                ),
            },
            "strings": _convert_strings(old),
            "mode_ode": [
                "dot(x)=p",
                "dot(y)=q",
                "dot(p)=-(n/8)^2*x",
                "dot(q)=-(n/8)^2*y",
            ],
            "transverse_embedding": (
                "X_i^perp=Q_i+V_i*t+sum_n("
                "x_in(t)*cos(2*pi*n*u_i)+"
                "y_in(t)*sin(2*pi*n*u_i))"
            ),
            "separation": (
                "d_perp=(Q1-Q2)+(V1-V2)*t+(Y1-Y2); "
                "d_w=o1*u1-o2*u2"
            ),
            "centre_term_multiplicity": 1,
        },
        "hysteresis": {
            "distance_convention": old_hysteresis[
                "distance_convention"
            ],
            "r_in": dyadic_to_atom(old_hysteresis["r_in"]),
            "r_out": dyadic_to_atom(old_hysteresis["r_out"]),
        },
        "observation": {
            "t0": t0,
            "t1": t1,
            "window_closure": old_observation["window_closure"],
            "initial_history": old_observation["initial_history"],
            "continuation_convention": old_observation[
                "continuation_convention"
            ],
            "time_is_quotient": False,
            "window_transport": (
                "unchanged exact dyadic endpoints from the registered "
                "source bridge"
            ),
        },
        "arb_backend_ingress": {
            "variable_order": list(VARIABLE_ORDER),
            "target_component_order": list(range(TARGET_DIMENSION)),
            "implementation": "python-flint Arb",
            "python_flint_version": "0.9.0",
            "flint_version": "3.6.0",
            "precision_bits": 192,
            "scalar_ingress": (
                "canonical q*pi^e; rational exact and Arb pi outward-rounded"
            ),
            "required_outputs": [
                "d",
                "d_a",
                "d_ab",
                "F_a",
                "F_ab",
                "g_r",
                "Dg_r",
            ],
        },
        "scope": {
            "claim": (
                "exact source-bound normalized closed-string problem "
                "and seam algebra"
            ),
            "does_not_claim": [
                "entry or no-entry over the registered window",
                "population pushforward or Jacobian",
                "population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
    }


def _validate_against_template(
    value: Any, template: Any, path: str = "$"
) -> None:
    """Validate exact structure, parsing every scalar atom at its path."""

    if type(template) is dict and set(template) == ATOM_KEYS:
        parse_symbolic_atom(value, path)
        return
    if type(template) is dict:
        obj = _exact_keys(value, set(template), path, "schema")
        for key in template:
            _validate_against_template(
                obj[key], template[key], f"{path}.{key}"
            )
        return
    if type(template) is list:
        items = _list(value, len(template), path, "schema")
        for index, expected in enumerate(template):
            _validate_against_template(
                items[index], expected, f"{path}[{index}]"
            )
        return
    if type(value) is not type(template):
        fail(
            "schema",
            f"{path} has type {type(value).__name__}; "
            f"expected {type(template).__name__}",
        )


def _verify_source_coefficient_identity(
    problem: Mapping[str, Any], upstream: Mapping[str, Any]
) -> None:
    old = upstream["physical_problem"]["kinematics"]
    new = problem["kinematics"]
    for centre in ("Q1", "Q2"):
        for index, (old_value, new_value) in enumerate(
            zip(
                old["centres_Q1_Q2"][centre],
                new["centres_Q1_Q2"][centre],
            )
        ):
            q, power = parse_symbolic_atom(
                new_value, f"$.kinematics.centres.{centre}[{index}]"
            )
            if power != 0 or q != parse_dyadic(old_value):
                fail("source_identity", "centre coefficient changed")
    for string_index in range(2):
        old_string = old["strings"][string_index]
        new_string = new["strings"][string_index]
        for index, (old_value, new_value) in enumerate(
            zip(
                old_string["transverse_velocity"],
                new_string["transverse_velocity"],
            )
        ):
            q, power = parse_symbolic_atom(
                new_value,
                (
                    "$.kinematics.strings"
                    f"[{string_index}].transverse_velocity[{index}]"
                ),
            )
            if power != 0 or q != parse_dyadic(old_value):
                fail("source_identity", "velocity coefficient changed")
        for mode_index, old_mode in enumerate(old_string["modes"]):
            new_mode = new_string["modes"][mode_index]
            for name in ("initial_x", "initial_y", "initial_p", "initial_q"):
                for index, (old_value, new_value) in enumerate(
                    zip(old_mode[name], new_mode[name])
                ):
                    q, power = parse_symbolic_atom(
                        new_value,
                        (
                            "$.kinematics.strings"
                            f"[{string_index}].modes[{mode_index}]"
                            f".{name}[{index}]"
                        ),
                    )
                    if power != 0 or q != parse_dyadic(old_value):
                        fail(
                            "source_identity",
                            f"{name} coefficient changed",
                        )


def verify_exact_seam_algebra(problem: Mapping[str, Any]) -> dict[str, int]:
    orientations = problem["worldsheet"]["orientations"]
    if (
        type(orientations) is not list
        or len(orientations) != 2
        or any(type(value) is not int for value in orientations)
        or orientations != [1, -1]
    ):
        fail("seam_algebra", "registered orientations must be (+1,-1)")
    a1 = orientations[0]
    a2 = -orientations[1]
    corner = a1 + a2
    expected = {
        "u1_plus_1": a1,
        "u2_plus_1": a2,
        "corner_plus_1_plus_1": corner,
    }
    actions = problem["worldsheet"]["seam_image_actions"]
    for name, shift in expected.items():
        action = actions[name]
        if (
            action["separation_winding_shift"] != shift
            or action["n8_reindex_shift"] != shift
        ):
            fail("seam_algebra", f"{name} image shift is false")
    for string_index, string in enumerate(problem["kinematics"]["strings"]):
        if string["orientation"] != orientations[string_index]:
            fail("seam_algebra", "kinematic orientation differs")
        for mode in string["modes"]:
            harmonic = mode["mode_number"]
            if type(harmonic) is not int or harmonic <= 0:
                fail("seam_algebra", "mode harmonic must be positive integer")
            if parse_symbolic_atom(
                mode["wave_number"], "$.mode.wave_number"
            ) != (Fraction(harmonic, 8), 0):
                fail("seam_algebra", "temporal wave number is not n/8")
            if parse_symbolic_atom(
                mode["temporal_angular_frequency"],
                "$.mode.temporal_angular_frequency",
            ) != (Fraction(harmonic, 8), 0):
                fail("seam_algebra", "temporal frequency is not n/8")
            if parse_symbolic_atom(
                mode["spatial_phase_coefficient"],
                "$.mode.spatial_phase_coefficient",
            ) != (Fraction(2 * harmonic), 1):
                fail("seam_algebra", "spatial phase is not 2*pi*n")
    return {"a1": a1, "a2": a2, "corner": corner}


def _count_string(value: Any, needle: str) -> int:
    if type(value) is str:
        return int(value == needle)
    if type(value) is list:
        return sum(_count_string(item, needle) for item in value)
    if type(value) is dict:
        return sum(_count_string(item, needle) for item in value.values())
    return 0


def build_fixture() -> dict[str, Any]:
    upstream = load_upstream_fixture()
    registry = build_lift_registry(upstream)
    registry_digest = semantic_sha256(registry)
    problem = build_closed_string_problem(upstream, registry_digest)
    problem_digest = semantic_sha256(problem)
    if problem_digest == LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256:
        fail("problem_identity", "new problem reused the legacy digest")
    return {
        "schema_version": FIXTURE_SCHEMA,
        "lift_registry": registry,
        "lift_registry_semantic_sha256": registry_digest,
        "closed_string_problem": problem,
        "closed_string_problem_semantic_sha256": problem_digest,
    }


def verify_fixture(fixture: Any) -> dict[str, Any]:
    obj = _exact_keys(
        fixture,
        {
            "schema_version",
            "lift_registry",
            "lift_registry_semantic_sha256",
            "closed_string_problem",
            "closed_string_problem_semantic_sha256",
        },
        "$.fixture",
        "fixture_schema",
    )
    if obj["schema_version"] != FIXTURE_SCHEMA:
        fail("fixture_schema", "unsupported fixture schema")
    upstream = load_upstream_fixture()
    expected_registry = build_lift_registry(upstream)
    _validate_against_template(
        obj["lift_registry"], expected_registry, "$.lift_registry"
    )
    if not type_strict_equal(obj["lift_registry"], expected_registry):
        fail("lift_registry_reproduction", "lift registry differs")
    registry_digest = semantic_sha256(obj["lift_registry"])
    if (
        _sha256(
            obj["lift_registry_semantic_sha256"],
            "$.lift_registry_semantic_sha256",
            "lift_registry_hash",
        )
        != registry_digest
    ):
        fail("lift_registry_hash", "stored registry digest differs")
    if (
        LIFT_REGISTRY_SEMANTIC_SHA256
        and registry_digest != LIFT_REGISTRY_SEMANTIC_SHA256
    ):
        fail("lift_registry_hash", "registry source-code pin differs")

    expected_problem = build_closed_string_problem(
        upstream, registry_digest
    )
    _validate_against_template(
        obj["closed_string_problem"],
        expected_problem,
        "$.closed_string_problem",
    )
    if not type_strict_equal(
        obj["closed_string_problem"], expected_problem
    ):
        fail("problem_reproduction", "closed-string problem differs")
    problem_digest = semantic_sha256(obj["closed_string_problem"])
    if (
        _sha256(
            obj["closed_string_problem_semantic_sha256"],
            "$.closed_string_problem_semantic_sha256",
            "problem_hash",
        )
        != problem_digest
    ):
        fail("problem_hash", "stored closed-string problem digest differs")
    if (
        CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
        and problem_digest != CLOSED_STRING_PROBLEM_SEMANTIC_SHA256
    ):
        fail("problem_hash", "problem source-code pin differs")
    if problem_digest == LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256:
        fail("problem_identity", "legacy digest reused as new problem digest")
    if LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256 in canonical_bytes(
        obj["closed_string_problem"]
    ).decode("utf-8"):
        fail(
            "provenance_boundary",
            "legacy problem digest leaked into the new problem",
        )
    if (
        _count_string(
            obj, LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256
        )
        != 1
    ):
        fail(
            "provenance_boundary",
            "legacy digest must occur exactly once, as registry provenance",
        )

    problem = obj["closed_string_problem"]
    exact = problem["exact_parameters"]
    if atom_multiply(exact["T_F"], exact["L_star"]) != exact["M"]:
        fail("exact_identity", "T_F*L_star != M")
    if atom_multiply(
        problem["kinematics"]["strings"][0]["modes"][0]["wave_number"],
        exact["L_star"],
    ) != symbolic_atom(2, pi_exponent=1):
        fail("exact_identity", "k_1*L_star != 2*pi")
    if atom_power(exact["L_star"], 2) != problem["target_torus"][
        "metric_diagonal"
    ][8]:
        fail("exact_identity", "G_ww != L_star^2")
    if problem["target_torus"]["periods"] != (
        [symbolic_atom(8) for _ in range(8)] + [symbolic_atom(1)]
    ):
        fail("target_geometry", "target periods differ")

    old_observation = upstream["physical_problem"]["observation"]
    if (
        problem["observation"]["t0"]
        != dyadic_to_atom(old_observation["t0"])
        or problem["observation"]["t1"]
        != dyadic_to_atom(old_observation["t1"])
    ):
        fail("time_window", "registered exact-dyadic window changed")
    if parse_symbolic_atom(problem["observation"]["t1"])[1] != 0:
        fail("time_window", "time endpoint must remain dyadic, not 16*pi")

    _verify_source_coefficient_identity(problem, upstream)
    seam = verify_exact_seam_algebra(problem)
    return {
        "source_bridge_fixture_semantic_sha256": (
            SOURCE_BRIDGE_FIXTURE_SEMANTIC_SHA256
        ),
        "source_registry_canonical_sha256": (
            SOURCE_REGISTRY_CANONICAL_SHA256
        ),
        "source_draw_sha256": SOURCE_DRAW_SHA256,
        "source_state_sha256": SOURCE_STATE_SHA256,
        "source_sample_index": SOURCE_SAMPLE_INDEX,
        "legacy_cut_open_problem_semantic_sha256": (
            LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256
        ),
        "lift_registry_semantic_sha256": registry_digest,
        "closed_string_problem_semantic_sha256": problem_digest,
        "seam_actions": seam,
    }


def _hostile_checks(fixture: Mapping[str, Any]) -> dict[str, bool]:
    def rejected(mutator: Callable[[dict[str, Any]], None]) -> bool:
        hostile = copy.deepcopy(fixture)
        mutator(hostile)
        try:
            verify_fixture(hostile)
        except LiftError:
            return True
        return False

    problem = fixture["closed_string_problem"]
    binary64_length = dyadic_to_atom(
        load_upstream_fixture()["physical_problem"]["f1_convention"][
            "winding_length"
        ]
    )
    checks = {
        "binary64_pi_length_substitution_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ].__setitem__("L_star", binary64_length)
        ),
        "symbolic_time_endpoint_substitution_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "observation"
            ].__setitem__("t1", symbolic_atom(16, pi_exponent=1))
        ),
        "seam_shift_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"]["worldsheet"][
                "seam_image_actions"
            ]["u2_plus_1"].__setitem__("n8_reindex_shift", -1)
        ),
        "seam_action_deletion_rejected": rejected(
            lambda value: value["closed_string_problem"]["worldsheet"][
                "seam_image_actions"
            ].pop("u1_plus_1")
        ),
        "orientation_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "worldsheet"
            ].__setitem__("orientations", [1, 1])
        ),
        "spatial_phase_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"]["kinematics"][
                "strings"
            ][0]["modes"][0].__setitem__(
                "spatial_phase_coefficient",
                symbolic_atom(1, pi_exponent=1),
            )
        ),
        "metric_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "target_torus"
            ]["metric_diagonal"].__setitem__(
                8, symbolic_atom(64, pi_exponent=2)
            )
        ),
        "source_coefficient_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"]["kinematics"][
                "strings"
            ][0]["modes"][0]["initial_x"].__setitem__(
                0, symbolic_atom(1)
            )
        ),
        "legacy_hash_reuse_rejected": rejected(
            lambda value: value.__setitem__(
                "closed_string_problem_semantic_sha256",
                LEGACY_CUT_OPEN_PROBLEM_SEMANTIC_SHA256,
            )
        ),
        "atom_extra_key_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ]["M"].__setitem__("unit", "mass")
        ),
        "atom_missing_key_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ]["M"].pop("pi_exponent")
        ),
        "atom_nonreduced_rational_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ].__setitem__(
                "M",
                {
                    "numerator": 16,
                    "denominator": 2,
                    "pi_exponent": 0,
                },
            )
        ),
        "atom_noncanonical_zero_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "variable_registry"
            ]["domains"]["u1"].__setitem__(
                "lower",
                {
                    "numerator": 0,
                    "denominator": 1,
                    "pi_exponent": 1,
                },
            )
        ),
        "atom_boolean_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ]["M"].__setitem__("numerator", True)
        ),
        "atom_exponent_bound_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "exact_parameters"
            ]["M"].__setitem__(
                "pi_exponent", PI_EXPONENT_MAX + 1
            )
        ),
        "domain_metric_mutation_rejected": rejected(
            lambda value: value["closed_string_problem"][
                "solver_geometry"
            ]["domain_metric_diagonal"].__setitem__(
                0, symbolic_atom(1)
            )
        ),
    }
    try:
        strict_json_loads(
            '{"numerator":1,"denominator":1,'
            '"pi_exponent":0,"numerator":1}'
        )
    except LiftError:
        checks["duplicate_json_key_rejected"] = True
    else:
        checks["duplicate_json_key_rejected"] = False
    try:
        strict_json_loads('{"x":1.0}')
    except LiftError:
        checks["ordinary_json_float_rejected"] = True
    else:
        checks["ordinary_json_float_rejected"] = False
    if problem["observation"]["t1"] == problem["exact_parameters"]["L_star"]:
        fail("hostile_controls", "test fixture conflates time and circumference")
    return checks


def build_report(fixture: Mapping[str, Any]) -> dict[str, Any]:
    replay = verify_fixture(fixture)
    hostile = _hostile_checks(fixture)
    if not all(hostile.values()):
        fail("hostile_controls", "one or more hostile controls were accepted")
    report = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "fixture_semantic_sha256": semantic_sha256(fixture),
        "checks": {
            "strict_q_pi_power_atoms": True,
            "source_index_2_replayed": True,
            "brief_0018_hashes_unchanged": True,
            "source_coefficients_identity_transport": True,
            "M_equals_8": True,
            "k_1_equals_one_eighth": True,
            "L_star_equals_16_pi": True,
            "T_F_equals_inverse_2_pi": True,
            "normalized_periods_are_8x8_then_1": True,
            "normalized_metric_winding_entry_is_L_star_squared": True,
            "registered_time_window_is_unchanged_dyadic": True,
            "exact_seam_image_actions_replayed": True,
            "legacy_problem_hash_is_provenance_only": True,
            "new_problem_hash_is_distinct": True,
            "arb_backend_and_variable_order_registered": True,
            "physical_domain_metric_and_singular_value_formula_registered": True,
            "population_measure_claim_withheld": True,
        },
        "commitments": replay,
        "hostile_controls": hostile,
        "scope": {
            "claim": (
                "fixed-index exact symbolic-pi closed-string lift "
                "and seam algebra"
            ),
            "does_not_claim": [
                "population pushforward or Jacobian",
                "entry or no-entry",
                "population law",
                "dimension dynamics",
                "3+1 selection",
            ],
        },
        "normalized_lf_inventory": [
            {
                "path": "artifacts/0019/symbolic_pi_lift.py",
                "normalized_lf_sha256": normalized_lf_sha256(
                    ARTIFACT_DIR / "symbolic_pi_lift.py"
                ),
            },
            {
                "path": "artifacts/0019/test_symbolic_pi_lift.py",
                "normalized_lf_sha256": normalized_lf_sha256(
                    ARTIFACT_DIR / "test_symbolic_pi_lift.py"
                ),
            },
            {
                "path": "artifacts/0019/symbolic_pi_lift_fixture.json",
                "normalized_lf_sha256": normalized_lf_sha256(
                    FIXTURE_PATH
                ),
            },
        ],
    }
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def verify_report(
    report: Any, fixture: Mapping[str, Any]
) -> str:
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
            "hostile_controls",
            "scope",
            "normalized_lf_inventory",
        },
        "$.report",
        "report_schema",
    )
    if obj["schema_version"] != REPORT_SCHEMA or obj["status"] != "passed":
        fail("report_schema", "report is not a passed supported schema")
    if type(obj["failed_gates"]) is not list or obj["failed_gates"]:
        fail("report_status", "passed report must have no failed gates")
    for name in ("checks", "hostile_controls"):
        values = obj[name]
        if (
            type(values) is not dict
            or not values
            or any(type(flag) is not bool or not flag for flag in values.values())
        ):
            fail("report_status", f"all {name} flags must be true Booleans")
    replay = verify_fixture(fixture)
    if not type_strict_equal(obj["commitments"], replay):
        fail("report_replay", "report commitments differ")
    if obj["fixture_semantic_sha256"] != semantic_sha256(fixture):
        fail("report_hash", "report does not bind the fixture")
    stored = _sha256(
        obj["report_semantic_sha256"],
        "$.report.report_semantic_sha256",
        "report_hash",
    )
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    computed = semantic_sha256(payload)
    if stored != computed:
        fail("report_hash", "report semantic digest does not replay")
    return computed


def run(write: bool) -> dict[str, Any]:
    fixture = build_fixture()
    if write:
        write_json(FIXTURE_PATH, fixture)
    else:
        stored_fixture = strict_json_load(FIXTURE_PATH)
        verify_fixture(stored_fixture)
        if not type_strict_equal(stored_fixture, fixture):
            fail("fixture_reproduction", "stored fixture differs")
    report = build_report(fixture)
    verify_report(report, fixture)
    if write:
        write_json(REPORT_PATH, report)
    else:
        stored_report = strict_json_load(REPORT_PATH)
        verify_report(stored_report, stored_fixture)
        if not type_strict_equal(stored_report, report):
            fail("report_reproduction", "stored report differs")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build or replay the symbolic-pi closed-string lift"
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
