#!/usr/bin/env python3
"""Independent replay of the Brief 0018 source-to-state binding.

This module deliberately has only two semantic inputs:

* ``artifacts/0018/source_registry.json``; and
* ``artifacts/0019/source_state_bridge_fixture.json``.

It contains its own strict JSON readers, deterministic source sampler,
source-state validator, exact-dyadic projection, constraint replay, and
physical-problem projection.  The hashes below are source-code trust anchors;
bundle-internal hashes are checked only after the bound mathematics has been
reconstructed.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REGISTRY_SCHEMA = "cyz-brief-0018-source-registry-v2"
SAMPLE_SCHEMA = "cyz-brief-0018-source-sample-v2"
FIXTURE_SCHEMA = "cyz-brief-0019-source-state-bridge-fixture-v1"
PROBLEM_SCHEMA = "cyz-brief-0019-exact-dyadic-f1-problem-v1"
REPORT_SCHEMA = "cyz-brief-0019-independent-source-binding-report-v1"
EQUATION_FAMILY_VERSION = "f1-opposite-winding-worldsheet-k1-v1"

PRNG_ALGORITHM = (
    "sha256-counter-open52mid-decimal90-box-muller-integer-gamma-v2"
)
PORTABLE_MATH_VERSION = "decimal90-ln-sqrt-float64-fixed-taylor-sincos-v2"
SOURCE_FAMILY = "quadratic-finite-K-single-delta-liouville-zero-pi"
CONSTRAINT_METHOD = "ambient-delta-exact-zero-pi"
PORTABLE_DECIMAL_PRECISION = 90
PORTABLE_PI_TEXT = (
    "3.141592653589793238462643383279502884197169399375105820974944"
    "5923078164062862089986280348253421170679"
)
PORTABLE_PI = float(Decimal(PORTABLE_PI_TEXT))
TRANSVERSE_DIMENSION = 8
CHIRAL_COMPLEX_COMPONENTS_PER_MODE = 8

REGISTRY_CANONICAL_SHA256 = (
    "35d31a64e45d9a3ea9cc346e19d8bc5d8d40d1f9eac68eb07385fb291aed8cdb"
)
SOURCE_DRAW_SHA256 = (
    "4bc0d8eadef9ad8aea8752f25e105127311b83edebc99ebe1b1b7561999e1bd4"
)
PINNED_STATE_SHA256 = {
    0: "bafc85014205bbdbb8156e059606a73a0c899911745f189a4ac4e0c90742670b",
    1: "5ffab438ce4cefe8ce278aecee6cab6e5939def96469f6327b7509113c0d6c3c",
    2: "1c671b6bf8e737d238c21de8b0f694a57b8bfab7006ebb1401136176567f118c",
}
PINNED_COEFFICIENT_SHA256 = {
    0: "490500d615188ed95587d7a5ef4cb4762ebbd6c92d140840ed44c7ea849ce5f6",
    1: "b88b1299b2aeb03064b3423a7d1f26fbf06f4cb9991fd743193d7b939cb915fa",
    2: "e6e0a59bcadb38855c1d54a928a642cbe592d2348742cc68387569d3c6a97f04",
}
PINNED_VALIDITY_STATUS = {
    0: "source_invalid",
    1: "source_invalid",
    2: "valid",
}
PHYSICAL_PROBLEM_SEMANTIC_SHA256 = (
    "1560b7df34dcec7dfa46a744d6bbb26424b6a1bf2ce3d2b94b80d308363660ca"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parent.parent
REGISTRY_PATH = ARTIFACT_DIR.parent / "0018" / "source_registry.json"
FIXTURE_PATH = ARTIFACT_DIR / "source_state_bridge_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "source_binding_replayer_report.json"
INVENTORY_PATHS = (
    "artifacts/0018/source_registry.json",
    "artifacts/0019/source_state_bridge_fixture.json",
    "artifacts/0019/source_binding_replayer.py",
    "artifacts/0019/test_source_binding_replayer.py",
    "artifacts/0019/README.md",
)

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")
BINARY64_HEX = re.compile(
    r"-?0x(?:0\.0|0\.[0-9a-f]{13}|1\.[0-9a-f]{13})p[+-][0-9]+"
)
DYADIC_KEYS = {"exponent", "numerator"}
TOP_LEVEL_REGISTRY_KEYS = {
    "schema_version",
    "audit_cell_id",
    "source_seed",
    "source_draw_registry",
    "validity",
    "audit",
    "downstream_context",
}
SOURCE_DRAW_KEYS = {
    "source_family",
    "constraint_method",
    "coordinate_units",
    "tension_convention",
    "winding_relation",
    "winding_axis",
    "winding_number_abs",
    "winding_orientations",
    "transverse_axis_order",
    "torus_periods_L_A",
    "winding_length",
    "string_length_ell_s",
    "string_tension",
    "fourier_cutoff_K",
    "transverse_energy",
    "total_transverse_momentum",
    "worldsheet_momenta",
}
VALIDITY_REGISTRY_KEYS = {"graph_upper_bound_max", "uv_product_max"}
AUDIT_KEYS = {
    "sample_count",
    "fingerprint_count",
    "familywise_alpha",
    "constraint_absolute_tolerance",
}
DOWNSTREAM_KEYS = {
    "r_in",
    "r_out",
    "observation_window",
    "initial_history",
    "rank_tolerance",
    "normal_dimension_hint",
    "response_winner",
    "reaction_scale",
}
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
SOURCE_FULL_KEYS = SOURCE_CORE_KEYS | {
    "source_state_sha256",
    "validity",
    "constraint_diagnostics",
}
STRING_KEYS = {"orientation", "transverse_velocity", "modes"}
MODE_KEYS = {"mode_number", "wave_number", "x", "y", "p", "q"}
SOURCE_VALIDITY_KEYS = {
    "status",
    "reasons",
    "registered_time_uniform_graph_upper_bound",
    "per_string_graph_upper_bounds",
    "k_max_times_ell_s",
    "sample_retained_without_redraw",
}
SOURCE_DIAGNOSTIC_KEYS = {
    "energy",
    "energy_residual",
    "total_transverse_momentum",
    "target_momentum_residual",
    "worldsheet_momenta",
    "worldsheet_momentum_residual",
}
FIXTURE_KEYS = {
    "schema_version",
    "registry_commitment",
    "pre_registered_selection",
    "selected_source_states",
    "routes",
    "physical_problem",
    "physical_problem_semantic_sha256",
}
RECORD_KEYS = {
    "sample_index",
    "source_state_sha256",
    "validity_status",
    "complete_serialized_source_state_binary64",
    "complete_serialized_state_semantic_sha256",
    "complete_exact_dyadic_projection",
    "complete_dyadic_projection_semantic_sha256",
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
}
REGISTERED_STREAM_LABELS = {
    "radial-gamma",
    "relative-zero-mode-direction",
    "relative-centre-haar",
    "string-0-left-direction",
    "string-0-right-direction",
    "string-1-left-direction",
    "string-1-right-direction",
}


class BindingReplayError(ValueError):
    """One independently replayed semantic gate failed."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise BindingReplayError(gate, message)


def _exact_keys(
    value: Any,
    expected: set[str],
    path: str,
    gate: str,
) -> dict[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        fail(
            gate,
            f"{path} keys differ; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}",
        )
    return value


def _integer(value: Any, path: str, gate: str) -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer")
    return value


def _number(value: Any, path: str, gate: str) -> float:
    if type(value) not in (int, float):
        fail(gate, f"{path} must be a number")
    result = float(value)
    if not math.isfinite(result):
        fail(gate, f"{path} must be finite")
    return result


def _numeric_vector(
    value: Any,
    length: int,
    path: str,
    gate: str,
    *,
    require_float: bool = False,
) -> tuple[float, ...]:
    if type(value) is not list or len(value) != length:
        fail(gate, f"{path} must have shape [{length}]")
    result = []
    for index, item in enumerate(value):
        if require_float:
            if type(item) is not float or not math.isfinite(item):
                fail(gate, f"{path}[{index}] must be a finite binary64")
            result.append(item)
        else:
            result.append(_number(item, f"{path}[{index}]", gate))
    return tuple(result)


def _sha256_token(value: Any, path: str, gate: str) -> str:
    if type(value) is not str or HEX_SHA256.fullmatch(value) is None:
        fail(gate, f"{path} must be 64 lowercase hexadecimal digits")
    return value


def reject_duplicate_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def reject_nonfinite(token: str) -> None:
    fail("strict_json", f"non-finite JSON constant {token}")


def reject_raw_float(token: str) -> None:
    fail("strict_json", f"raw JSON float token {token} is forbidden")


def assert_finite_json(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            fail("strict_json", f"non-finite number at {path}")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            assert_finite_json(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            assert_finite_json(item, f"{path}.{key}")
        return
    fail("strict_json", f"non-JSON type {type(value).__name__} at {path}")


def strict_registry_loads(text: str) -> Any:
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_constant=reject_nonfinite,
        )
    except BindingReplayError:
        raise
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
    assert_finite_json(value)
    return value


def strict_float_free_loads(text: str) -> Any:
    try:
        value = json.loads(
            text,
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=reject_raw_float,
            parse_constant=reject_nonfinite,
        )
    except BindingReplayError:
        raise
    except (ValueError, TypeError, json.JSONDecodeError) as error:
        fail("strict_json", str(error))
    assert_finite_json(value)
    return value


def strict_registry_load(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")
    value = strict_registry_loads(text)
    if type(value) is not dict:
        fail("registry_schema", "registry must be an object")
    return value


def strict_fixture_load(path: Path = FIXTURE_PATH) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")
    value = strict_float_free_loads(text)
    if type(value) is not dict:
        fail("fixture_schema", "fixture must be an object")
    return value


def strict_report_load(path: Path = REPORT_PATH) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        fail("strict_json", f"cannot read {path}: {error}")
    value = strict_float_free_loads(text)
    if type(value) is not dict:
        fail("report_schema", "report must be an object")
    return value


def canonical_bytes(value: Any) -> bytes:
    assert_finite_json(value)
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
    assert_finite_json(value)
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


def type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return set(left) == set(right) and all(
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


def validate_registry(registry: Any) -> dict[str, Any]:
    obj = _exact_keys(
        registry, TOP_LEVEL_REGISTRY_KEYS, "$", "registry_schema"
    )
    if obj["schema_version"] != REGISTRY_SCHEMA:
        fail("registry_schema", "unsupported source registry schema")
    if type(obj["audit_cell_id"]) is not str or not obj["audit_cell_id"]:
        fail("registry_schema", "$.audit_cell_id must be a nonempty string")
    seed = obj["source_seed"]
    if (
        type(seed) is not str
        or len(seed) != 64
        or any(character not in "0123456789abcdef" for character in seed)
    ):
        fail("registry_schema", "$.source_seed is not lowercase SHA-256")

    source = _exact_keys(
        obj["source_draw_registry"],
        SOURCE_DRAW_KEYS,
        "$.source_draw_registry",
        "source_v2_schema",
    )
    expected_strings = {
        "source_family": SOURCE_FAMILY,
        "constraint_method": CONSTRAINT_METHOD,
        "coordinate_units": "ell_s-natural-length-hbar-c-1",
        "tension_convention": "T_F=1/(2*pi*ell_s^2)",
        "winding_relation": "L_w=abs(w)*L_A[winding_axis]",
    }
    for key, expected in expected_strings.items():
        if source[key] != expected:
            fail("source_v2_schema", f"{key} is not the registered convention")
    winding_axis = _integer(
        source["winding_axis"],
        "$.source_draw_registry.winding_axis",
        "torus",
    )
    if winding_axis != 8:
        fail("torus", "the registered winding axis must be 8")
    if _integer(
        source["winding_number_abs"],
        "$.source_draw_registry.winding_number_abs",
        "f1_relation",
    ) != 1:
        fail("f1_relation", "the registered winding number must have |w|=1")
    if (
        type(source["winding_orientations"]) is not list
        or source["winding_orientations"] != [1, -1]
        or any(type(value) is not int for value in source["winding_orientations"])
    ):
        fail("orientation", "the two orientations must be [1,-1]")
    expected_axes = list(range(8))
    if (
        type(source["transverse_axis_order"]) is not list
        or source["transverse_axis_order"] != expected_axes
        or any(type(value) is not int for value in source["transverse_axis_order"])
    ):
        fail("torus", "transverse axes must be the ordered complement 0..7")
    periods = _numeric_vector(
        source["torus_periods_L_A"],
        9,
        "$.source_draw_registry.torus_periods_L_A",
        "torus",
    )
    if any(period <= 0.0 for period in periods):
        fail("torus", "all torus periods must be positive")
    winding_length = _number(
        source["winding_length"],
        "$.source_draw_registry.winding_length",
        "f1_relation",
    )
    ell_s = _number(
        source["string_length_ell_s"],
        "$.source_draw_registry.string_length_ell_s",
        "f1_relation",
    )
    tension = _number(
        source["string_tension"],
        "$.source_draw_registry.string_tension",
        "f1_relation",
    )
    if min(winding_length, ell_s, tension) <= 0.0:
        fail("f1_relation", "L_w, ell_s, and T_F must be positive")
    if winding_length != source["winding_number_abs"] * periods[winding_axis]:
        fail("f1_relation", "L_w != |w| L_A[winding_axis]")
    expected_tension = 1.0 / (2.0 * PORTABLE_PI * ell_s * ell_s)
    if tension.hex() != expected_tension.hex():
        fail("f1_relation", "T_F is not the once-rounded F1 relation")
    if _integer(
        source["fourier_cutoff_K"],
        "$.source_draw_registry.fourier_cutoff_K",
        "wave_number",
    ) != 1:
        fail("wave_number", "this registry must have K=1")
    energy = _number(
        source["transverse_energy"],
        "$.source_draw_registry.transverse_energy",
        "source_v2_schema",
    )
    momentum = _numeric_vector(
        source["total_transverse_momentum"],
        8,
        "$.source_draw_registry.total_transverse_momentum",
        "source_v2_schema",
    )
    worldsheet = _numeric_vector(
        source["worldsheet_momenta"],
        2,
        "$.source_draw_registry.worldsheet_momenta",
        "level_matching",
    )
    if worldsheet != (0.0, 0.0):
        fail("level_matching", "registered worldsheet momenta must be zero")
    mass = tension * winding_length
    residual = energy - portable_fsum(x * x for x in momentum) / (4.0 * mass)
    if residual <= 0.0:
        fail("source_v2_schema", "the regular residual shell is empty")

    validity = _exact_keys(
        obj["validity"], VALIDITY_REGISTRY_KEYS, "$.validity", "validity"
    )
    for key in sorted(VALIDITY_REGISTRY_KEYS):
        if _number(validity[key], f"$.validity.{key}", "validity") <= 0.0:
            fail("validity", f"{key} must be positive")

    audit = _exact_keys(
        obj["audit"], AUDIT_KEYS, "$.audit", "registry_schema"
    )
    sample_count = _integer(
        audit["sample_count"], "$.audit.sample_count", "registry_schema"
    )
    fingerprint_count = _integer(
        audit["fingerprint_count"],
        "$.audit.fingerprint_count",
        "registry_schema",
    )
    if sample_count < 1 or not 1 <= fingerprint_count <= sample_count:
        fail("registry_schema", "audit counts are inconsistent")
    alpha = _number(
        audit["familywise_alpha"],
        "$.audit.familywise_alpha",
        "registry_schema",
    )
    tolerance = _number(
        audit["constraint_absolute_tolerance"],
        "$.audit.constraint_absolute_tolerance",
        "registry_schema",
    )
    if not 0.0 < alpha < 1.0 or tolerance <= 0.0:
        fail("registry_schema", "audit alpha/tolerance is invalid")

    downstream = _exact_keys(
        obj["downstream_context"],
        DOWNSTREAM_KEYS,
        "$.downstream_context",
        "registry_schema",
    )
    r_in = _number(
        downstream["r_in"], "$.downstream_context.r_in", "torus"
    )
    r_out = _number(
        downstream["r_out"], "$.downstream_context.r_out", "torus"
    )
    if not 0.0 < r_in < r_out < 0.5 * min(periods):
        fail("torus", "hysteresis radii violate the injectivity gate")
    window = _numeric_vector(
        downstream["observation_window"],
        2,
        "$.downstream_context.observation_window",
        "registry_schema",
    )
    if not window[0] < window[1]:
        fail("registry_schema", "observation window must increase")
    if downstream["initial_history"] not in {
        "armed",
        "active",
        "left_censored",
        "exited",
    }:
        fail("registry_schema", "initial history is not registered")
    if _number(
        downstream["rank_tolerance"],
        "$.downstream_context.rank_tolerance",
        "registry_schema",
    ) <= 0.0:
        fail("registry_schema", "rank tolerance must be positive")
    if (
        downstream["normal_dimension_hint"] is not None
        and type(downstream["normal_dimension_hint"]) is not int
    ):
        fail("registry_schema", "normal_dimension_hint has the wrong type")
    if (
        downstream["response_winner"] is not None
        and type(downstream["response_winner"]) is not str
    ):
        fail("registry_schema", "response_winner has the wrong type")
    _number(
        downstream["reaction_scale"],
        "$.downstream_context.reaction_scale",
        "registry_schema",
    )

    registry_digest = semantic_sha256(obj)
    if registry_digest != REGISTRY_CANONICAL_SHA256:
        fail(
            "registry_commitment",
            f"registry digest {registry_digest} is not code-pinned",
        )
    draw_digest = semantic_sha256(source_draw_identity(obj))
    if draw_digest != SOURCE_DRAW_SHA256:
        fail(
            "source_draw_commitment",
            f"source-draw digest {draw_digest} is not code-pinned",
        )
    return obj


def source_draw_identity(registry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "registry_schema": registry["schema_version"],
        "prng_algorithm": PRNG_ALGORITHM,
        "portable_math_version": PORTABLE_MATH_VERSION,
        "source_seed": registry["source_seed"],
        "source_draw_registry": registry["source_draw_registry"],
    }


def _portable_decimal(value: int | float) -> Decimal:
    if type(value) is int:
        return Decimal(value)
    if type(value) is not float or not math.isfinite(value):
        fail("portable_math", "portable arithmetic requires a finite number")
    return Decimal.from_float(value)


def portable_fsum(values: Iterable[float]) -> float:
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        total = Decimal(0)
        for value in values:
            total += _portable_decimal(value)
        return float(total)


def portable_log(value: float) -> float:
    if type(value) is not float or not math.isfinite(value) or value <= 0.0:
        fail("portable_math", "log requires one finite positive binary64")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal.from_float(value).ln())


def portable_sqrt(value: float) -> float:
    if type(value) is not float or not math.isfinite(value) or value < 0.0:
        fail("portable_math", "sqrt requires one finite nonnegative binary64")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal.from_float(value).sqrt())


def portable_sin_cos_turn(turn: float) -> tuple[float, float]:
    if type(turn) is not float or not math.isfinite(turn):
        fail("portable_math", "turn must be one finite binary64")
    reduced = turn - math.floor(turn)
    if reduced > 0.5:
        reduced -= 1.0
    cosine_sign = 1.0
    if reduced > 0.25:
        reduced = 0.5 - reduced
        cosine_sign = -1.0
    elif reduced < -0.25:
        reduced = -0.5 - reduced
        cosine_sign = -1.0
    angle = (2.0 * PORTABLE_PI) * reduced
    square = angle * angle
    sine = angle
    cosine = 1.0
    sine_term = angle
    cosine_term = 1.0
    for index in range(1, 15):
        sine_term *= -square / ((2 * index) * (2 * index + 1))
        cosine_term *= -square / ((2 * index - 1) * (2 * index))
        sine += sine_term
        cosine += cosine_term
    return sine, cosine_sign * cosine


class DeterministicStream:
    """Counter-mode SHA-256 stream with an open 52-bit midpoint map."""

    def __init__(self, key: bytes):
        self._key = hashlib.sha256(key).digest()
        self._counter = 0
        self._words: list[int] = []
        self._normal_cache: float | None = None

    def _refill(self) -> None:
        block = hashlib.sha256(
            self._key + self._counter.to_bytes(16, "big")
        ).digest()
        self._counter += 1
        self._words.extend(
            int.from_bytes(block[offset : offset + 8], "big")
            for offset in range(0, 32, 8)
        )

    def uint64(self) -> int:
        if not self._words:
            self._refill()
        return self._words.pop(0)

    def uniform_open(self) -> float:
        integer = self.uint64() >> 12
        result = (integer + 0.5) * 2.0**-52
        if not 0.0 < result < 1.0:
            fail("source_generation", "uniform midpoint reached an endpoint")
        return result

    def normal(self) -> float:
        if self._normal_cache is not None:
            result = self._normal_cache
            self._normal_cache = None
            return result
        radius = portable_sqrt(-2.0 * portable_log(self.uniform_open()))
        sine, cosine = portable_sin_cos_turn(self.uniform_open())
        self._normal_cache = radius * sine
        return radius * cosine


def stream_for(
    registry: Mapping[str, Any], sample_index: int, label: str
) -> DeterministicStream:
    if type(sample_index) is not int or sample_index < 0:
        fail("source_generation", "sample index must be nonnegative")
    if label not in REGISTERED_STREAM_LABELS:
        fail("source_generation", "unregistered source stream label")
    key = (
        canonical_bytes(source_draw_identity(registry))
        + sample_index.to_bytes(16, "big")
        + label.encode("utf-8")
    )
    return DeterministicStream(key)


def gamma_integer(shape: int, stream: DeterministicStream) -> float:
    if type(shape) is not int or shape < 1:
        fail("source_generation", "integer Gamma shape must be positive")
    return portable_fsum(
        -portable_log(stream.uniform_open()) for _ in range(shape)
    )


def unit_sphere(
    dimension: int, stream: DeterministicStream
) -> tuple[float, ...]:
    if type(dimension) is not int or dimension < 1:
        fail("source_generation", "sphere dimension must be positive")
    vector = tuple(stream.normal() for _ in range(dimension))
    squared_norm = portable_fsum(value * value for value in vector)
    if not squared_norm > 0.0 or not math.isfinite(squared_norm):
        fail("source_generation", "normal direction is unresolved")
    inverse_norm = 1.0 / portable_sqrt(squared_norm)
    return tuple(value * inverse_norm for value in vector)


def source_parameters(registry: Mapping[str, Any]) -> dict[str, Any]:
    source = registry["source_draw_registry"]
    cutoff = source["fourier_cutoff_K"]
    winding_length = float(source["winding_length"])
    tension = float(source["string_tension"])
    mass = tension * winding_length
    momentum = tuple(float(value) for value in source["total_transverse_momentum"])
    energy = float(source["transverse_energy"])
    residual_energy = energy - portable_fsum(
        value * value for value in momentum
    ) / (4.0 * mass)
    periods = tuple(float(value) for value in source["torus_periods_L_A"])
    transverse_axes = tuple(source["transverse_axis_order"])
    return {
        "K": cutoff,
        "d": 16 * cutoff,
        "M": mass,
        "E": energy,
        "E_star": residual_energy,
        "P_total": momentum,
        "k_values": tuple(
            2.0 * PORTABLE_PI * mode / winding_length
            for mode in range(1, cutoff + 1)
        ),
        "transverse_periods": tuple(periods[axis] for axis in transverse_axes),
        "torus_periods_L_A": periods,
        "winding_axis": source["winding_axis"],
        "winding_number_abs": source["winding_number_abs"],
        "winding_orientations": tuple(source["winding_orientations"]),
        "ell_s": float(source["string_length_ell_s"]),
    }


def sample_radial_shares(
    registry: Mapping[str, Any], sample_index: int
) -> tuple[float, float, float]:
    parameters = source_parameters(registry)
    shapes = (4, 16 * parameters["K"] - 1, 16 * parameters["K"] - 1)
    stream = stream_for(registry, sample_index, "radial-gamma")
    values = tuple(gamma_integer(shape, stream) for shape in shapes)
    total = portable_fsum(values)
    return tuple(
        parameters["E_star"] * value / total for value in values
    )  # type: ignore[return-value]


def real_from_chiral(
    left: complex, right: complex, wave_number: float
) -> tuple[float, float, float, float]:
    if wave_number <= 0.0:
        fail("source_generation", "wave number must be positive")
    x_value = 2.0 * (left.real + right.real)
    y_value = -2.0 * (left.imag + right.imag)
    p_value = 2.0 * wave_number * (left.imag - right.imag)
    q_value = 2.0 * wave_number * (left.real - right.real)
    return x_value, y_value, p_value, q_value


def _complex_from_flat(
    vector: Sequence[float], mode: int, transverse: int
) -> complex:
    offset = 2 * (
        mode * CHIRAL_COMPLEX_COMPONENTS_PER_MODE + transverse
    )
    return complex(vector[offset], vector[offset + 1])


def independently_generate_source(
    registry: Mapping[str, Any], sample_index: int
) -> dict[str, Any]:
    """Generate one unconditioned source state without an upstream runtime."""

    parameters = source_parameters(registry)
    shares = sample_radial_shares(registry, sample_index)
    w_direction = unit_sphere(
        TRANSVERSE_DIMENSION,
        stream_for(registry, sample_index, "relative-zero-mode-direction"),
    )
    w_vector = tuple(
        portable_sqrt(shares[0]) * value for value in w_direction
    )

    chiral_vectors: list[tuple[tuple[float, ...], tuple[float, ...]]] = []
    for string_index in range(2):
        radius = portable_sqrt(shares[string_index + 1] / 2.0)
        left = unit_sphere(
            parameters["d"],
            stream_for(
                registry,
                sample_index,
                f"string-{string_index}-left-direction",
            ),
        )
        right = unit_sphere(
            parameters["d"],
            stream_for(
                registry,
                sample_index,
                f"string-{string_index}-right-direction",
            ),
        )
        chiral_vectors.append(
            (
                tuple(radius * value for value in left),
                tuple(radius * value for value in right),
            )
        )

    momentum = parameters["P_total"]
    mass_root = portable_sqrt(parameters["M"])
    velocities = [
        [
            momentum[axis] / (2.0 * parameters["M"])
            + w_vector[axis] / mass_root
            for axis in range(TRANSVERSE_DIMENSION)
        ],
        [
            momentum[axis] / (2.0 * parameters["M"])
            - w_vector[axis] / mass_root
            for axis in range(TRANSVERSE_DIMENSION)
        ],
    ]

    strings: list[dict[str, Any]] = []
    for string_index in range(2):
        modes: list[dict[str, Any]] = []
        left_vector, right_vector = chiral_vectors[string_index]
        for mode_index, wave_number in enumerate(parameters["k_values"]):
            x_values: list[float] = []
            y_values: list[float] = []
            p_values: list[float] = []
            q_values: list[float] = []
            scale = portable_sqrt(2.0 * parameters["M"]) * wave_number
            for transverse in range(TRANSVERSE_DIMENSION):
                left = (
                    _complex_from_flat(left_vector, mode_index, transverse)
                    / scale
                )
                right = (
                    _complex_from_flat(right_vector, mode_index, transverse)
                    / scale
                )
                x_value, y_value, p_value, q_value = real_from_chiral(
                    left, right, wave_number
                )
                x_values.append(x_value)
                y_values.append(y_value)
                p_values.append(p_value)
                q_values.append(q_value)
            modes.append(
                {
                    "mode_number": mode_index + 1,
                    "wave_number": wave_number,
                    "x": x_values,
                    "y": y_values,
                    "p": p_values,
                    "q": q_values,
                }
            )
        strings.append(
            {
                "orientation": parameters["winding_orientations"][string_index],
                "transverse_velocity": velocities[string_index],
                "modes": modes,
            }
        )

    centre_stream = stream_for(
        registry, sample_index, "relative-centre-haar"
    )
    relative_centre = [
        period * centre_stream.uniform_open()
        for period in parameters["transverse_periods"]
    ]
    core = {
        "schema_version": SAMPLE_SCHEMA,
        "sample_index": sample_index,
        "source_draw_sha256": semantic_sha256(source_draw_identity(registry)),
        "relative_centre_gauge": "Q2=0,Q1=Q_relative",
        "Q_relative": relative_centre,
        "Q1": relative_centre,
        "Q2": [0.0] * TRANSVERSE_DIMENSION,
        "energy_shares_s0_s1_s2": list(shares),
        "strings": strings,
    }
    state_hash = semantic_sha256(core)
    return {
        **core,
        "source_state_sha256": state_hash,
        "validity": evaluate_validity(core, registry),
        "constraint_diagnostics": constraint_diagnostics(core, registry),
    }


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        fail("source_constraints", "vector dimensions differ")
    return portable_fsum(a * b for a, b in zip(left, right))


def norm(vector: Sequence[float]) -> float:
    return portable_sqrt(max(0.0, dot(vector, vector)))


def chiral_from_real(
    x_value: float,
    y_value: float,
    p_value: float,
    q_value: float,
    wave_number: float,
) -> tuple[complex, complex]:
    left = 0.25 * (
        x_value
        + q_value / wave_number
        + 1j * (p_value / wave_number - y_value)
    )
    right = 0.25 * (
        x_value
        - q_value / wave_number
        - 1j * (y_value + p_value / wave_number)
    )
    return left, right


def extract_chiral_vectors(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> tuple[tuple[tuple[float, ...], tuple[float, ...]], ...]:
    parameters = source_parameters(registry)
    output = []
    for string in state["strings"]:
        left_vector: list[float] = []
        right_vector: list[float] = []
        for mode in string["modes"]:
            wave_number = float(mode["wave_number"])
            scale = portable_sqrt(2.0 * parameters["M"]) * wave_number
            for transverse in range(TRANSVERSE_DIMENSION):
                left, right = chiral_from_real(
                    mode["x"][transverse],
                    mode["y"][transverse],
                    mode["p"][transverse],
                    mode["q"][transverse],
                    wave_number,
                )
                left_vector.extend((scale * left.real, scale * left.imag))
                right_vector.extend((scale * right.real, scale * right.imag))
        output.append((tuple(left_vector), tuple(right_vector)))
    return tuple(output)


def graph_upper_bound(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> tuple[float, tuple[float, float]]:
    source_parameters(registry)
    bounds: list[float] = []
    for string in state["strings"]:
        bound = norm(string["transverse_velocity"])
        for mode in string["modes"]:
            wave_number = float(mode["wave_number"])
            x_radius = portable_sqrt(
                dot(mode["x"], mode["x"])
                + dot(mode["p"], mode["p"]) / wave_number**2
            )
            y_radius = portable_sqrt(
                dot(mode["y"], mode["y"])
                + dot(mode["q"], mode["q"]) / wave_number**2
            )
            bound += wave_number * (x_radius + y_radius)
        bounds.append(bound)
    return max(bounds), (bounds[0], bounds[1])


def evaluate_validity(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    parameters = source_parameters(registry)
    maximum, per_string = graph_upper_bound(state, registry)
    uv_product = max(parameters["k_values"]) * parameters["ell_s"]
    reasons: list[str] = []
    if maximum > float(registry["validity"]["graph_upper_bound_max"]):
        reasons.append("graph_upper_bound_exceeded")
    if uv_product > float(registry["validity"]["uv_product_max"]):
        reasons.append("uv_product_exceeded")
    return {
        "status": "source_invalid" if reasons else "valid",
        "reasons": reasons,
        "registered_time_uniform_graph_upper_bound": maximum,
        "per_string_graph_upper_bounds": list(per_string),
        "k_max_times_ell_s": uv_product,
        "sample_retained_without_redraw": True,
    }


def constraint_diagnostics(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    parameters = source_parameters(registry)
    mass = parameters["M"]
    energy = 0.0
    total_momentum = [0.0] * TRANSVERSE_DIMENSION
    worldsheet_values: list[float] = []
    for string in state["strings"]:
        velocity = string["transverse_velocity"]
        energy += 0.5 * mass * dot(velocity, velocity)
        for axis in range(TRANSVERSE_DIMENSION):
            total_momentum[axis] += mass * velocity[axis]
        worldsheet = 0.0
        for mode in string["modes"]:
            wave_number = mode["wave_number"]
            oscillator_sum = portable_fsum(
                mode["p"][axis] ** 2
                + mode["q"][axis] ** 2
                + wave_number**2
                * (mode["x"][axis] ** 2 + mode["y"][axis] ** 2)
                for axis in range(TRANSVERSE_DIMENSION)
            )
            energy += 0.25 * mass * oscillator_sum
            worldsheet += (
                0.5
                * mass
                * wave_number
                * portable_fsum(
                    mode["p"][axis] * mode["y"][axis]
                    - mode["q"][axis] * mode["x"][axis]
                    for axis in range(TRANSVERSE_DIMENSION)
                )
            )
        worldsheet_values.append(worldsheet)
    momentum_residual = [
        total_momentum[axis] - parameters["P_total"][axis]
        for axis in range(TRANSVERSE_DIMENSION)
    ]
    return {
        "energy": energy,
        "energy_residual": energy - parameters["E"],
        "total_transverse_momentum": total_momentum,
        "target_momentum_residual": momentum_residual,
        "worldsheet_momenta": worldsheet_values,
        "worldsheet_momentum_residual": worldsheet_values,
    }


def exact_dyadic_constraint_residuals(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    parameters = source_parameters(registry)
    mass = Fraction.from_float(parameters["M"])
    target_energy = Fraction.from_float(parameters["E"])
    target_momentum = tuple(
        Fraction.from_float(value) for value in parameters["P_total"]
    )
    energy = Fraction()
    momentum = [Fraction() for _ in range(TRANSVERSE_DIMENSION)]
    worldsheet_values: list[Fraction] = []
    for string in state["strings"]:
        velocity = tuple(
            Fraction.from_float(value)
            for value in string["transverse_velocity"]
        )
        energy += mass * sum(
            (value * value for value in velocity), Fraction()
        ) / 2
        for axis in range(TRANSVERSE_DIMENSION):
            momentum[axis] += mass * velocity[axis]
        worldsheet = Fraction()
        for mode in string["modes"]:
            wave_number = Fraction.from_float(mode["wave_number"])
            oscillator_sum = Fraction()
            worldsheet_sum = Fraction()
            for axis in range(TRANSVERSE_DIMENSION):
                x_value = Fraction.from_float(mode["x"][axis])
                y_value = Fraction.from_float(mode["y"][axis])
                p_value = Fraction.from_float(mode["p"][axis])
                q_value = Fraction.from_float(mode["q"][axis])
                oscillator_sum += (
                    p_value * p_value
                    + q_value * q_value
                    + wave_number
                    * wave_number
                    * (x_value * x_value + y_value * y_value)
                )
                worldsheet_sum += p_value * y_value - q_value * x_value
            energy += mass * oscillator_sum / 4
            worldsheet += mass * wave_number * worldsheet_sum / 2
        worldsheet_values.append(worldsheet)
    return {
        "energy_residual": energy - target_energy,
        "target_momentum_residual": tuple(
            momentum[axis] - target_momentum[axis]
            for axis in range(TRANSVERSE_DIMENSION)
        ),
        "worldsheet_momentum_residual": tuple(worldsheet_values),
    }


def source_coefficient_payload_sha256(state: Mapping[str, Any]) -> str:
    return semantic_sha256(
        {
            "Q_relative": state["Q_relative"],
            "Q1": state["Q1"],
            "Q2": state["Q2"],
            "energy_shares_s0_s1_s2": state[
                "energy_shares_s0_s1_s2"
            ],
            "strings": state["strings"],
        }
    )


def validate_source_sample(
    state: Any, registry: Mapping[str, Any]
) -> dict[str, Any]:
    obj = _exact_keys(state, SOURCE_FULL_KEYS, "$.state", "source_v2_schema")
    if obj["schema_version"] != SAMPLE_SCHEMA:
        fail("source_v2_schema", "unsupported source sample schema")
    sample_index = _integer(
        obj["sample_index"], "$.state.sample_index", "source_v2_schema"
    )
    if sample_index < 0:
        fail("source_v2_schema", "sample index must be nonnegative")
    if obj["source_draw_sha256"] != SOURCE_DRAW_SHA256:
        fail("source_draw_commitment", "state has the wrong source-draw identity")
    if obj["relative_centre_gauge"] != "Q2=0,Q1=Q_relative":
        fail("q_gauge", "relative-centre gauge is not registered")
    parameters = source_parameters(registry)
    relative = _numeric_vector(
        obj["Q_relative"], 8, "$.state.Q_relative", "q_gauge", require_float=True
    )
    q1 = _numeric_vector(
        obj["Q1"], 8, "$.state.Q1", "q_gauge", require_float=True
    )
    q2 = _numeric_vector(
        obj["Q2"], 8, "$.state.Q2", "q_gauge", require_float=True
    )
    if q1 != relative or q2 != (0.0,) * 8:
        fail("q_gauge", "Q2=0,Q1=Q_relative is not realized")
    if any(
        not 0.0 < value < period
        for value, period in zip(relative, parameters["transverse_periods"])
    ):
        fail("torus", "relative centre lies outside the open torus cell")
    shares = _numeric_vector(
        obj["energy_shares_s0_s1_s2"],
        3,
        "$.state.energy_shares_s0_s1_s2",
        "source_constraints",
        require_float=True,
    )
    if any(value <= 0.0 for value in shares):
        fail("source_constraints", "regular-shell shares must be positive")
    if abs(portable_fsum(shares) - parameters["E_star"]) > 5.0e-15:
        fail("energy_constraint", "energy shares do not sum to E_star")

    strings = obj["strings"]
    if type(strings) is not list or len(strings) != 2:
        fail("source_v2_schema", "state must contain two strings")
    for string_index, string in enumerate(strings):
        item = _exact_keys(
            string,
            STRING_KEYS,
            f"$.state.strings[{string_index}]",
            "source_v2_schema",
        )
        if item["orientation"] != parameters["winding_orientations"][
            string_index
        ]:
            fail("orientation", "serialized string orientation is wrong")
        _numeric_vector(
            item["transverse_velocity"],
            8,
            f"$.state.strings[{string_index}].transverse_velocity",
            "source_v2_schema",
            require_float=True,
        )
        modes = item["modes"]
        if type(modes) is not list or len(modes) != 1:
            fail("wave_number", "each string must contain exactly K=1 mode")
        mode = _exact_keys(
            modes[0],
            MODE_KEYS,
            f"$.state.strings[{string_index}].modes[0]",
            "source_v2_schema",
        )
        if type(mode["mode_number"]) is not int or mode["mode_number"] != 1:
            fail("wave_number", "mode number is not 1")
        expected_wave = parameters["k_values"][0]
        if (
            type(mode["wave_number"]) is not float
            or mode["wave_number"].hex() != expected_wave.hex()
        ):
            fail("wave_number", "k_1 != 2*pi/L_w")
        for field in ("x", "y", "p", "q"):
            _numeric_vector(
                mode[field],
                8,
                f"$.state.strings[{string_index}].modes[0].{field}",
                "source_coefficients",
                require_float=True,
            )

    _exact_keys(
        obj["validity"],
        SOURCE_VALIDITY_KEYS,
        "$.state.validity",
        "validity",
    )
    _exact_keys(
        obj["constraint_diagnostics"],
        SOURCE_DIAGNOSTIC_KEYS,
        "$.state.constraint_diagnostics",
        "constraint_diagnostics",
    )
    core = {key: obj[key] for key in SOURCE_CORE_KEYS}
    core_hash = semantic_sha256(core)
    if obj["source_state_sha256"] != core_hash:
        fail("source_state_hash", "state hash does not bind the source core")
    expected_validity = evaluate_validity(obj, registry)
    if not type_strict_equal(obj["validity"], expected_validity):
        fail("validity", "registered validity predicates do not replay")
    expected_diagnostics = constraint_diagnostics(obj, registry)
    if not type_strict_equal(
        obj["constraint_diagnostics"], expected_diagnostics
    ):
        fail(
            "constraint_diagnostics",
            "serialized diagnostics do not replay from coefficients",
        )

    tolerance = float(registry["audit"]["constraint_absolute_tolerance"])
    residuals = (
        [expected_diagnostics["energy_residual"]]
        + expected_diagnostics["target_momentum_residual"]
        + expected_diagnostics["worldsheet_momentum_residual"]
    )
    if any(abs(value) > tolerance for value in residuals):
        fail("source_constraints", "registered float constraints fail tolerance")
    exact_residuals = exact_dyadic_constraint_residuals(obj, registry)
    exact_values = (
        [exact_residuals["energy_residual"]]
        + list(exact_residuals["target_momentum_residual"])
        + list(exact_residuals["worldsheet_momentum_residual"])
    )
    if any(abs(float(value)) > tolerance for value in exact_values):
        fail("source_constraints", "exact-dyadic constraints fail tolerance")
    for string_index, (left, right) in enumerate(
        extract_chiral_vectors(obj, registry)
    ):
        target = shares[string_index + 1] / 2.0
        if (
            abs(dot(left, left) - target) > tolerance
            or abs(dot(right, right) - target) > tolerance
        ):
            fail("level_matching", "left/right chiral radii do not match")
    return {
        "state_core_sha256": core_hash,
        "coefficient_payload_sha256": source_coefficient_payload_sha256(obj),
        "validity": expected_validity,
        "constraint_diagnostics": expected_diagnostics,
        "exact_constraint_residuals": exact_residuals,
    }


def encode_binary64_tree(value: Any) -> Any:
    if type(value) is float:
        if not math.isfinite(value):
            fail("binary64", "cannot encode a non-finite binary64")
        return {"binary64_hex": value.hex()}
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [encode_binary64_tree(item) for item in value]
    if type(value) is dict:
        return {key: encode_binary64_tree(item) for key, item in value.items()}
    fail("binary64", f"unsupported value type {type(value).__name__}")


def decode_binary64_tree(value: Any, path: str = "$") -> Any:
    if type(value) is dict and set(value) == {"binary64_hex"}:
        token = value["binary64_hex"]
        if type(token) is not str or BINARY64_HEX.fullmatch(token) is None:
            fail("binary64", f"{path} has a noncanonical binary64 token")
        result = float.fromhex(token)
        if not math.isfinite(result) or result.hex() != token:
            fail("binary64", f"{path} does not round-trip canonically")
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
    fail("binary64", f"{path} contains unsupported encoded data")


def dyadic(value: float) -> dict[str, int]:
    if type(value) is not float or not math.isfinite(value):
        fail("dyadic", "dyadic encoding requires a finite binary64")
    numerator, denominator = value.as_integer_ratio()
    exponent = denominator.bit_length() - 1
    if denominator != 1 << exponent:
        fail("dyadic", "binary64 denominator is not a power of two")
    if numerator == 0:
        exponent = 0
    else:
        while exponent and numerator % 2 == 0:
            numerator //= 2
            exponent -= 1
    return {"exponent": exponent, "numerator": numerator}


def fraction_to_dyadic(value: Fraction) -> dict[str, int]:
    denominator = value.denominator
    exponent = denominator.bit_length() - 1
    if denominator != 1 << exponent:
        fail("dyadic", "exact residual is not dyadic")
    numerator = value.numerator
    if numerator == 0:
        exponent = 0
    else:
        while exponent and numerator % 2 == 0:
            numerator //= 2
            exponent -= 1
    return {"exponent": exponent, "numerator": numerator}


def parse_dyadic(value: Any, path: str = "$") -> Fraction:
    obj = _exact_keys(value, DYADIC_KEYS, path, "dyadic")
    exponent = _integer(obj["exponent"], f"{path}.exponent", "dyadic")
    numerator = _integer(obj["numerator"], f"{path}.numerator", "dyadic")
    if exponent < 0 or exponent > 4096:
        fail("dyadic", f"{path}.exponent is outside the accepted range")
    if numerator == 0 and exponent != 0:
        fail("dyadic", f"{path} zero is not canonical")
    if exponent > 0 and numerator % 2 == 0:
        fail("dyadic", f"{path} is not reduced")
    return Fraction(numerator, 1 << exponent)


def exact_dyadic_tree(value: Any) -> Any:
    if type(value) is float:
        return dyadic(value)
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is list:
        return [exact_dyadic_tree(item) for item in value]
    if type(value) is dict:
        return {key: exact_dyadic_tree(item) for key, item in value.items()}
    fail("dyadic", f"unsupported value type {type(value).__name__}")


def verify_binary64_dyadic_bijection(
    encoded: Any, projected: Any, path: str = "$"
) -> None:
    if type(encoded) is dict and set(encoded) == {"binary64_hex"}:
        token = encoded["binary64_hex"]
        decoded = decode_binary64_tree(encoded, path)
        rational = parse_dyadic(projected, path)
        if rational != Fraction.from_float(decoded):
            fail("dyadic_bijection", f"{path} dyadic differs from binary64")
        reconstructed = float(rational)
        if (
            not math.isfinite(reconstructed)
            or Fraction.from_float(reconstructed) != rational
            or reconstructed.hex() != token
        ):
            fail("dyadic_bijection", f"{path} does not map back to one binary64")
        return
    if type(encoded) is not type(projected):
        fail("dyadic_bijection", f"{path} projection changes value type")
    if type(encoded) is list:
        if len(encoded) != len(projected):
            fail("dyadic_bijection", f"{path} projection changes list length")
        for index, (left, right) in enumerate(zip(encoded, projected)):
            verify_binary64_dyadic_bijection(
                left, right, f"{path}[{index}]"
            )
        return
    if type(encoded) is dict:
        if set(encoded) != set(projected):
            fail("dyadic_bijection", f"{path} projection changes object keys")
        for key in encoded:
            verify_binary64_dyadic_bijection(
                encoded[key], projected[key], f"{path}.{key}"
            )
        return
    if encoded != projected:
        fail("dyadic_bijection", f"{path} changes a non-binary64 leaf")


def _state_record(state: Mapping[str, Any]) -> dict[str, Any]:
    encoded = encode_binary64_tree(state)
    projected = exact_dyadic_tree(state)
    return {
        "sample_index": state["sample_index"],
        "source_state_sha256": state["source_state_sha256"],
        "validity_status": state["validity"]["status"],
        "complete_serialized_source_state_binary64": encoded,
        "complete_serialized_state_semantic_sha256": semantic_sha256(encoded),
        "complete_exact_dyadic_projection": projected,
        "complete_dyadic_projection_semantic_sha256": semantic_sha256(projected),
    }


def verify_state_record(
    record: Any,
    expected_state: Mapping[str, Any],
    registry: Mapping[str, Any],
    label: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    obj = _exact_keys(record, RECORD_KEYS, f"$.{label}", "state_record")
    index = expected_state["sample_index"]
    if type(obj["sample_index"]) is not int or obj["sample_index"] != index:
        fail("source_index", f"{label} has the wrong source index")
    if obj["validity_status"] != PINNED_VALIDITY_STATUS[index]:
        fail("validity", f"{label} has the wrong envelope status")
    encoded = obj["complete_serialized_source_state_binary64"]
    decoded = decode_binary64_tree(encoded, f"$.{label}.binary64")
    replay = validate_source_sample(decoded, registry)
    if decoded["sample_index"] != index:
        fail("source_index", f"{label} payload has the wrong source index")
    pinned_state = PINNED_STATE_SHA256[index]
    for actual in (
        decoded["source_state_sha256"],
        obj["source_state_sha256"],
        replay["state_core_sha256"],
    ):
        if actual != pinned_state:
            fail(
                "source_state_commitment",
                f"index {index} state is not the code-pinned state",
            )
    pinned_coefficients = PINNED_COEFFICIENT_SHA256[index]
    if replay["coefficient_payload_sha256"] != pinned_coefficients:
        fail(
            "source_coefficient_commitment",
            f"index {index} coefficient payload is not code-pinned",
        )
    if not type_strict_equal(decoded, expected_state):
        fail(
            "source_coefficients",
            f"index {index} state differs from independent regeneration",
        )
    if (
        _sha256_token(
            obj["complete_serialized_state_semantic_sha256"],
            f"$.{label}.complete_serialized_state_semantic_sha256",
            "state_record_hash",
        )
        != semantic_sha256(encoded)
    ):
        fail("state_record_hash", f"{label} binary64 tree hash does not replay")
    projected = obj["complete_exact_dyadic_projection"]
    expected_projection = exact_dyadic_tree(decoded)
    if not type_strict_equal(projected, expected_projection):
        fail("dyadic_projection", f"{label} exact projection differs")
    verify_binary64_dyadic_bijection(encoded, projected, f"$.{label}")
    if (
        _sha256_token(
            obj["complete_dyadic_projection_semantic_sha256"],
            f"$.{label}.complete_dyadic_projection_semantic_sha256",
            "state_record_hash",
        )
        != semantic_sha256(projected)
    ):
        fail("state_record_hash", f"{label} dyadic tree hash does not replay")
    return decoded, projected, replay


def _dyadic_registry_number(value: Any, path: str) -> dict[str, int]:
    number = _number(value, path, "physical_projection")
    return dyadic(number)


def _identity_matrix(size: int) -> list[list[dict[str, int]]]:
    return [
        [
            dyadic(float(1 if row == column else 0))
            for column in range(size)
        ]
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


def build_physical_problem_from_exact_state(
    exact_state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    """Reconstruct every physical primitive from the index-2 exact state."""

    if exact_state["sample_index"] != 2:
        fail("source_index", "physical projection must use source index 2")
    if exact_state["source_state_sha256"] != PINNED_STATE_SHA256[2]:
        fail("source_state_commitment", "physical source state is not pinned")
    if exact_state["validity"]["status"] != "valid":
        fail("validity", "invalid source cannot enter physical projection")
    source = registry["source_draw_registry"]
    downstream = registry["downstream_context"]
    periods = [
        _dyadic_registry_number(value, f"$.torus_periods[{index}]")
        for index, value in enumerate(source["torus_periods_L_A"])
    ]
    winding_length = _dyadic_registry_number(
        source["winding_length"], "$.winding_length"
    )
    strings = []
    for string_index, source_string in enumerate(exact_state["strings"]):
        if len(source_string["modes"]) != 1:
            fail("wave_number", "physical source must have K=1")
        mode = source_string["modes"][0]
        strings.append(
            {
                "string_id": string_index + 1,
                "orientation": source_string["orientation"],
                "centre_reference": f"Q{string_index + 1}",
                "transverse_velocity": copy.deepcopy(
                    source_string["transverse_velocity"]
                ),
                "modes": [
                    {
                        "mode_number": mode["mode_number"],
                        "wave_number": copy.deepcopy(mode["wave_number"]),
                        "initial_x": copy.deepcopy(mode["x"]),
                        "initial_y": copy.deepcopy(mode["y"]),
                        "initial_p": copy.deepcopy(mode["p"]),
                        "initial_q": copy.deepcopy(mode["q"]),
                    }
                ],
            }
        )
    return {
        "schema_version": PROBLEM_SCHEMA,
        "equation_family_version": EQUATION_FAMILY_VERSION,
        "source_commitment": {
            "source_registry_canonical_sha256": REGISTRY_CANONICAL_SHA256,
            "source_draw_sha256": SOURCE_DRAW_SHA256,
            "source_state_sha256": PINNED_STATE_SHA256[2],
            "source_sample_index": 2,
            "source_sample_schema": exact_state["schema_version"],
        },
        "dimensions": {
            "target": 9,
            "transverse": 8,
            "target_axis_order": list(range(9)),
            "transverse_axis_order": list(range(8)),
            "winding_axis": 8,
        },
        "f1_convention": {
            "coordinate_units": source["coordinate_units"],
            "string_length_ell_s": _dyadic_registry_number(
                source["string_length_ell_s"], "$.ell_s"
            ),
            "string_tension": _dyadic_registry_number(
                source["string_tension"], "$.string_tension"
            ),
            "portable_pi_binary64": dyadic(PORTABLE_PI),
            "tension_relation": (
                "T_F=1/(2*pi*ell_s^2), rounded once to binary64"
            ),
            "winding_number_abs": source["winding_number_abs"],
            "winding_length": winding_length,
            "winding_relation": "L_w=abs(w)*L_A[winding_axis]",
        },
        "target_torus": {
            "metric_convention": "G=identity_9",
            "G": _identity_matrix(9),
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
                    "upper": copy.deepcopy(winding_length),
                    "closure": "lower_closed_upper_open",
                },
                {
                    "lower": dyadic(0.0),
                    "upper": copy.deepcopy(winding_length),
                    "closure": "lower_closed_upper_open",
                },
            ],
            "winding_orientations": [1, -1],
            "winding_embedding": "X_i^w=o_i*sigma_i on target axis 8",
        },
        "observation": {
            "t0": _dyadic_registry_number(
                downstream["observation_window"][0], "$.observation.t0"
            ),
            "t1": _dyadic_registry_number(
                downstream["observation_window"][1], "$.observation.t1"
            ),
            "window_closure": "lower_closed_upper_open",
            "initial_history": downstream["initial_history"],
            "continuation_convention": (
                "right-censor at excluded t1; carry active/armed history "
                "to a subsequent adjacent window without boundary re-arming"
            ),
        },
        "hysteresis": {
            "r_in": _dyadic_registry_number(
                downstream["r_in"], "$.hysteresis.r_in"
            ),
            "r_out": _dyadic_registry_number(
                downstream["r_out"], "$.hysteresis.r_out"
            ),
            "distance_convention": "F_n=(1/2)*s_n^T*G*s_n",
        },
        "kinematics": {
            "transverse_embedding": "X_i^perp=Q_i+V_i*t+Y_i(t,sigma_i)",
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
                "Q1": copy.deepcopy(exact_state["Q1"]),
                "Q2": copy.deepcopy(exact_state["Q2"]),
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


def _reject_forbidden_physical_keys(value: Any, path: str = "$") -> None:
    if type(value) is dict:
        for key, item in value.items():
            if key in FORBIDDEN_PHYSICAL_KEYS:
                fail(
                    "forbidden_physical_input",
                    f"forbidden key {key!r} at {path}",
                )
            _reject_forbidden_physical_keys(item, f"{path}.{key}")
    elif type(value) is list:
        for index, item in enumerate(value):
            _reject_forbidden_physical_keys(item, f"{path}[{index}]")


def _route(
    state: Mapping[str, Any], physical_problem_created: bool
) -> dict[str, Any]:
    return {
        "sample_index": state["sample_index"],
        "source_state_sha256": state["source_state_sha256"],
        "validity_status_recomputed_from_registry": state["validity"]["status"],
        "route": (
            "physical_problem_ready"
            if physical_problem_created
            else "source_invalid"
        ),
        "physical_problem_created": physical_problem_created,
        "event_solver_executed": False,
        "arb_evaluator_executed": False,
    }


def _fraction_tree_to_dyadic(value: Any) -> Any:
    if type(value) is Fraction:
        return fraction_to_dyadic(value)
    if type(value) is tuple:
        return [_fraction_tree_to_dyadic(item) for item in value]
    if type(value) is list:
        return [_fraction_tree_to_dyadic(item) for item in value]
    if type(value) is dict:
        return {
            key: _fraction_tree_to_dyadic(item) for key, item in value.items()
        }
    return value


def _source_row(
    state: Mapping[str, Any], replay: Mapping[str, Any]
) -> dict[str, Any]:
    validity = replay["validity"]
    diagnostics = replay["constraint_diagnostics"]
    return {
        "sample_index": state["sample_index"],
        "source_state_sha256": replay["state_core_sha256"],
        "source_coefficient_payload_sha256": replay[
            "coefficient_payload_sha256"
        ],
        "validity_status": validity["status"],
        "validity_reasons": copy.deepcopy(validity["reasons"]),
        "registered_time_uniform_graph_upper_bound": dyadic(
            validity["registered_time_uniform_graph_upper_bound"]
        ),
        "per_string_graph_upper_bounds": [
            dyadic(value) for value in validity["per_string_graph_upper_bounds"]
        ],
        "k_max_times_ell_s": dyadic(validity["k_max_times_ell_s"]),
        "constraint_diagnostics_binary64_sha256": semantic_sha256(
            encode_binary64_tree(diagnostics)
        ),
        "exact_dyadic_constraint_residuals": _fraction_tree_to_dyadic(
            replay["exact_constraint_residuals"]
        ),
    }


def replay_binding_objects(
    registry: Any, fixture: Any
) -> dict[str, Any]:
    registry_obj = validate_registry(registry)
    fixture_obj = _exact_keys(
        fixture, FIXTURE_KEYS, "$.fixture", "fixture_schema"
    )
    if fixture_obj["schema_version"] != FIXTURE_SCHEMA:
        fail("fixture_schema", "unsupported source bridge fixture schema")

    generated: list[dict[str, Any]] = []
    generated_replay: list[dict[str, Any]] = []
    for index in range(3):
        state = independently_generate_source(registry_obj, index)
        replay = validate_source_sample(state, registry_obj)
        if replay["state_core_sha256"] != PINNED_STATE_SHA256[index]:
            fail(
                "source_state_commitment",
                f"independently generated index {index} is not code-pinned",
            )
        if (
            replay["coefficient_payload_sha256"]
            != PINNED_COEFFICIENT_SHA256[index]
        ):
            fail(
                "source_coefficient_commitment",
                f"independently generated index {index} coefficients drifted",
            )
        if replay["validity"]["status"] != PINNED_VALIDITY_STATUS[index]:
            fail(
                "validity",
                f"independently generated index {index} status drifted",
            )
        generated.append(state)
        generated_replay.append(replay)

    statuses = [replay["validity"]["status"] for replay in generated_replay]
    first_invalid = next(
        (index for index, status in enumerate(statuses) if status == "source_invalid"),
        None,
    )
    first_valid = next(
        (index for index, status in enumerate(statuses) if status == "valid"),
        None,
    )
    if first_invalid != 0 or first_valid != 2:
        fail("least_status_rule", "least validity statuses do not occur at 0 and 2")

    expected_registry_commitment = {
        "path": "artifacts/0018/source_registry.json",
        "registry_canonical_sha256": REGISTRY_CANONICAL_SHA256,
        "source_draw_sha256": SOURCE_DRAW_SHA256,
    }
    if not type_strict_equal(
        fixture_obj["registry_commitment"], expected_registry_commitment
    ):
        fail("registry_commitment", "fixture registry commitment differs")
    expected_selection = {
        "rule": "least source index for each required validity status",
        "first_source_invalid_index": 0,
        "first_valid_index": 2,
        "scanned_indices": [
            {
                "sample_index": index,
                "source_state_sha256": PINNED_STATE_SHA256[index],
                "validity_status": PINNED_VALIDITY_STATUS[index],
            }
            for index in range(3)
        ],
    }
    selected = _exact_keys(
        fixture_obj["selected_source_states"],
        {"source_invalid_control", "valid_physical_control"},
        "$.fixture.selected_source_states",
        "fixture_schema",
    )
    decoded_zero, exact_zero, replay_zero = verify_state_record(
        selected["source_invalid_control"],
        generated[0],
        registry_obj,
        "source_invalid_control",
    )
    decoded_two, exact_two, replay_two = verify_state_record(
        selected["valid_physical_control"],
        generated[2],
        registry_obj,
        "valid_physical_control",
    )
    if exact_zero["validity"]["status"] != "source_invalid":
        fail("validity", "exact index-0 projection changed status")
    if exact_two["validity"]["status"] != "valid":
        fail("validity", "exact index-2 projection changed status")
    if not type_strict_equal(
        fixture_obj["pre_registered_selection"], expected_selection
    ):
        fail("least_status_rule", "fixture least-status ledger differs")

    routes = _exact_keys(
        fixture_obj["routes"],
        {"source_invalid_control", "valid_physical_control"},
        "$.fixture.routes",
        "route",
    )
    expected_routes = {
        "source_invalid_control": _route(decoded_zero, False),
        "valid_physical_control": _route(decoded_two, True),
    }
    if not type_strict_equal(routes, expected_routes):
        fail("route", "source routing does not replay")
    invalid_route = routes["source_invalid_control"]
    if any(
        key in invalid_route
        for key in (
            "solver_payload",
            "event_record",
            "certificate_bundle",
            "physical_problem",
        )
    ):
        fail("invalid_route_payload", "index 0 carries a solver payload")
    if (
        invalid_route["event_solver_executed"]
        or invalid_route["arb_evaluator_executed"]
        or invalid_route["physical_problem_created"]
    ):
        fail("invalid_route_payload", "index 0 executed a downstream backend")

    physical_problem = fixture_obj["physical_problem"]
    _reject_forbidden_physical_keys(physical_problem)
    expected_problem = build_physical_problem_from_exact_state(
        exact_two, registry_obj
    )
    if not type_strict_equal(physical_problem, expected_problem):
        fail(
            "physical_projection",
            "physical problem differs from exact index-2 reconstruction",
        )
    problem_digest = semantic_sha256(physical_problem)
    if (
        problem_digest != PHYSICAL_PROBLEM_SEMANTIC_SHA256
        or fixture_obj["physical_problem_semantic_sha256"]
        != PHYSICAL_PROBLEM_SEMANTIC_SHA256
    ):
        fail("problem_commitment", "physical problem is not code-pinned")

    expected_fixture = {
        "schema_version": FIXTURE_SCHEMA,
        "registry_commitment": expected_registry_commitment,
        "pre_registered_selection": expected_selection,
        "selected_source_states": {
            "source_invalid_control": _state_record(generated[0]),
            "valid_physical_control": _state_record(generated[2]),
        },
        "routes": expected_routes,
        "physical_problem": expected_problem,
        "physical_problem_semantic_sha256": PHYSICAL_PROBLEM_SEMANTIC_SHA256,
    }
    if not type_strict_equal(fixture_obj, expected_fixture):
        fail("fixture_binding", "fixture differs from full independent replay")

    rows = [
        _source_row(state, replay)
        for state, replay in zip(generated, generated_replay)
    ]
    return {
        "registry_canonical_sha256": semantic_sha256(registry_obj),
        "source_draw_sha256": semantic_sha256(
            source_draw_identity(registry_obj)
        ),
        "fixture_semantic_sha256": semantic_sha256(fixture_obj),
        "source_rows": rows,
        "first_source_invalid_index": first_invalid,
        "first_valid_index": first_valid,
        "physical_problem_semantic_sha256": problem_digest,
        "invalid_route_has_no_solver_payload": True,
        "binary64_exact_dyadic_bijection": True,
        "rank_normal_response_reaction_absent": True,
        "selected_record_constraint_replay": {
            "index_0": semantic_sha256(
                _fraction_tree_to_dyadic(
                    replay_zero["exact_constraint_residuals"]
                )
            ),
            "index_2": semantic_sha256(
                _fraction_tree_to_dyadic(
                    replay_two["exact_constraint_residuals"]
                )
            ),
        },
    }


def replay_binding_paths(
    registry_path: Path = REGISTRY_PATH,
    fixture_path: Path = FIXTURE_PATH,
) -> dict[str, Any]:
    return replay_binding_objects(
        strict_registry_load(registry_path),
        strict_fixture_load(fixture_path),
    )


def _inventory() -> list[dict[str, str]]:
    return [
        {
            "path": relative,
            "normalized_lf_sha256": normalized_lf_sha256(
                REPOSITORY_ROOT / relative
            ),
        }
        for relative in INVENTORY_PATHS
    ]


def build_report(replay: Mapping[str, Any]) -> dict[str, Any]:
    report = {
        "schema_version": REPORT_SCHEMA,
        "status": "passed",
        "failed_gates": [],
        "checks": {
            "strict_registry_and_fixture_json": True,
            "registry_and_source_draw_code_pinned": True,
            "source_indices_0_1_2_independently_regenerated": True,
            "source_v2_q_orientation_wave_and_torus_replayed": True,
            "graph_uv_energy_momentum_level_matching_replayed": True,
            "least_source_invalid_0_and_first_valid_2_proved": True,
            "binary64_exact_dyadic_bijection_replayed": True,
            "index_2_exact_physical_projection_code_pinned": True,
            "index_0_has_no_solver_payload": True,
            "rank_normal_response_reaction_inputs_rejected": True,
        },
        "commitments": copy.deepcopy(replay),
        "normalized_lf_inventory": _inventory(),
        "scope": {
            "claim": (
                "independent source-state binding replay for the fixed "
                "Brief 0018 indices 0, 1, and 2"
            ),
            "does_not_claim": [
                "9D exhaustive worldsheet solver",
                "unconditioned source population pushforward",
                "3+1 selection",
            ],
        },
    }
    report["report_semantic_sha256"] = semantic_sha256(report)
    return report


def verify_report(
    report: Any, replay: Mapping[str, Any]
) -> str:
    expected = build_report(replay)
    obj = _exact_keys(
        report, set(expected), "$.report", "report_schema"
    )
    if obj["schema_version"] != REPORT_SCHEMA:
        fail("report_schema", "unsupported report schema")
    stored_hash = _sha256_token(
        obj["report_semantic_sha256"],
        "$.report.report_semantic_sha256",
        "report_hash",
    )
    payload = copy.deepcopy(obj)
    del payload["report_semantic_sha256"]
    if stored_hash != semantic_sha256(payload):
        fail("report_hash", "report semantic hash does not replay")
    if not type_strict_equal(obj, expected):
        fail("report_replay", "stored report differs from fresh replay")
    return stored_hash


def run(write: bool) -> dict[str, Any]:
    replay = replay_binding_paths()
    report = build_report(replay)
    if write:
        REPORT_PATH.write_text(pretty_json(report), encoding="utf-8", newline="\n")
    else:
        stored = strict_report_load()
        verify_report(stored, replay)
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Independently replay the pinned source-state binding"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    arguments = parser.parse_args(argv)
    print(pretty_json(run(write=arguments.write)), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
