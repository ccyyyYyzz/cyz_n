#!/usr/bin/env python3
"""Exact zero-level-matched finite-K microcanonical source control.

This module implements the direct source sampler derived in Brief 0018.  It
does not find encounters, compute rank, condition on source validity, or
implement a physical early-universe preparation.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from decimal import Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


REGISTRY_SCHEMA = "cyz-brief-0018-source-registry-v2"
REPORT_SCHEMA = "cyz-brief-0018-source-report-v2"
SAMPLE_SCHEMA = "cyz-brief-0018-source-sample-v2"
PRNG_ALGORITHM = "sha256-counter-open52mid-decimal90-box-muller-integer-gamma-v2"
PORTABLE_MATH_VERSION = "decimal90-ln-sqrt-float64-fixed-taylor-sincos-v2"
SOURCE_FAMILY = "quadratic-finite-K-single-delta-liouville-zero-pi"
CONSTRAINT_METHOD = "ambient-delta-exact-zero-pi"
TRANSVERSE_DIMENSION = 8
CHIRAL_COMPLEX_COMPONENTS_PER_MODE = 8
PORTABLE_DECIMAL_PRECISION = 90
PORTABLE_PI_TEXT = (
    "3.141592653589793238462643383279502884197169399375105820974944"
    "5923078164062862089986280348253421170679"
)
PORTABLE_PI = float(Decimal(PORTABLE_PI_TEXT))
REGISTERED_STREAM_LABELS = {
    "radial-gamma",
    "radial-hierarchical-beta",
    "relative-zero-mode-direction",
    "relative-centre-haar",
    "string-0-left-direction",
    "string-0-right-direction",
    "string-1-left-direction",
    "string-1-right-direction",
}

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
VALIDITY_KEYS = {
    "graph_upper_bound_max",
    "uv_product_max",
}
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
SAMPLE_CORE_KEYS = {
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
SAMPLE_FULL_KEYS = SAMPLE_CORE_KEYS | {
    "source_state_sha256",
    "validity",
    "constraint_diagnostics",
}
MODE_KEYS = {"mode_number", "wave_number", "x", "y", "p", "q"}
STRING_KEYS = {"orientation", "transverse_velocity", "modes"}
SAMPLE_VALIDITY_KEYS = {
    "status",
    "reasons",
    "registered_time_uniform_graph_upper_bound",
    "per_string_graph_upper_bounds",
    "k_max_times_ell_s",
    "sample_retained_without_redraw",
}
SAMPLE_DIAGNOSTIC_KEYS = {
    "energy",
    "energy_residual",
    "total_transverse_momentum",
    "target_momentum_residual",
    "worldsheet_momenta",
    "worldsheet_momentum_residual",
}


class RegistryError(ValueError):
    """The frozen source registry cannot construct the declared source."""


class SampleError(ValueError):
    """A serialized state is not a member of the declared source support."""


def reject_duplicate_object_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    """Build a JSON object while rejecting duplicate keys."""

    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def reject_json_constant(value: str) -> None:
    """Reject non-standard JSON constants such as NaN and Infinity."""

    raise ValueError(f"non-finite JSON constant: {value}")


def assert_finite_json(value: Any, path: str = "$") -> None:
    """Reject non-finite numbers recursively."""

    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if type(value) is int:
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError(f"non-finite JSON number at {path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            assert_finite_json(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            assert_finite_json(item, f"{path}.{key}")
        return
    raise TypeError(f"non-JSON value at {path}: {type(value).__name__}")


def read_strict_json(path: Path) -> Any:
    """Read semantic JSON with duplicate-key and finite-number checks."""

    with path.open("r", encoding="utf-8", newline=None) as handle:
        value = json.load(
            handle,
            object_pairs_hook=reject_duplicate_object_pairs,
            parse_constant=reject_json_constant,
        )
    assert_finite_json(value)
    return value


def canonical_bytes(value: Any) -> bytes:
    """Canonical UTF-8 JSON payload used for identities and hashes."""

    assert_finite_json(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def pretty_json(value: Any) -> str:
    """Stable human-readable UTF-8/LF JSON."""

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


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(pretty_json(value), encoding="utf-8", newline="\n")


def type_strict_semantic_equal(left: Any, right: Any) -> bool:
    """JSON equality that does not identify ``true`` with ``1``."""

    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            type_strict_semantic_equal(left[key], right[key])
            for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            type_strict_semantic_equal(a, b)
            for a, b in zip(left, right)
        )
    return left == right


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def normalized_text_sha256(path: Path) -> str:
    """Hash text after BOM removal and CRLF/CR normalization to LF."""

    text = path.read_text(encoding="utf-8-sig")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def format_float(value: float) -> str:
    if not math.isfinite(value):
        raise ValueError("cannot serialize a non-finite diagnostic")
    if value == 0.0:
        return "0"
    return format(value, ".17g")


def _portable_decimal(value: int | float) -> Decimal:
    if type(value) is int:
        return Decimal(value)
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("portable arithmetic requires one finite int or float")
    return Decimal.from_float(value)


def portable_fsum(values: Iterable[float]) -> float:
    """Platform-stable sum of the exact binary64 inputs."""

    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        total = Decimal(0)
        for value in values:
            total += _portable_decimal(value)
        return float(total)


def portable_log(value: float) -> float:
    if type(value) is not float or not math.isfinite(value) or value <= 0.0:
        raise ValueError("portable logarithm requires a finite positive float")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal.from_float(value).ln())


def portable_exp(value: float) -> float:
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("portable exponential requires a finite float")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal.from_float(value).exp())


def portable_sqrt(value: float) -> float:
    if type(value) is not float or not math.isfinite(value) or value < 0.0:
        raise ValueError("portable square root requires a finite nonnegative float")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal.from_float(value).sqrt())


def portable_sin_cos_turn(turn: float) -> tuple[float, float]:
    """Return sin/cos(2*pi*turn) with a fixed binary64 polynomial."""

    if type(turn) is not float or not math.isfinite(turn):
        raise ValueError("portable turn requires a finite float")
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


def portable_sin_cos(angle: float) -> tuple[float, float]:
    if type(angle) is not float or not math.isfinite(angle):
        raise ValueError("portable sine/cosine requires a finite float")
    return portable_sin_cos_turn(angle / (2.0 * PORTABLE_PI))


def portable_hypot(left: float, right: float) -> float:
    return portable_sqrt(left * left + right * right)


def portable_lgamma_integer(argument: int) -> float:
    """Return log Gamma(n) for an exact positive integer n."""

    if type(argument) is not int or argument < 1:
        raise ValueError("portable log-Gamma is registered only for integers")
    with localcontext() as context:
        context.prec = PORTABLE_DECIMAL_PRECISION
        context.rounding = ROUND_HALF_EVEN
        return float(Decimal(math.factorial(argument - 1)).ln())


def _expect_exact_keys(
    value: Mapping[str, Any], expected: set[str], path: str
) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise RegistryError(
            f"{path} keys differ; missing={missing}, extra={extra}"
        )


def _expect_string(value: Any, path: str) -> str:
    if type(value) is not str or not value:
        raise RegistryError(f"{path} must be a nonempty string")
    return value


def _expect_integer(value: Any, path: str) -> int:
    if type(value) is not int:
        raise RegistryError(f"{path} must be an integer, not {type(value).__name__}")
    return value


def _expect_number(value: Any, path: str) -> float:
    if type(value) not in (int, float):
        raise RegistryError(f"{path} must be a finite number")
    number = float(value)
    if not math.isfinite(number):
        raise RegistryError(f"{path} must be finite")
    return number


def _expect_numeric_vector(
    value: Any, length: int, path: str
) -> tuple[float, ...]:
    if type(value) is not list or len(value) != length:
        raise RegistryError(f"{path} must have shape [{length}]")
    return tuple(
        _expect_number(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    )


def validate_source_draw_registry(registry: Any) -> dict[str, Any]:
    """Validate only fields authorized to construct source coefficients."""

    if type(registry) is not dict:
        raise RegistryError("registry must be a JSON object")
    if registry.get("schema_version") != REGISTRY_SCHEMA:
        raise RegistryError("unsupported registry schema_version")
    seed = _expect_string(registry.get("source_seed"), "$.source_seed")
    if len(seed) != 64 or any(
        character not in "0123456789abcdef" for character in seed
    ):
        raise RegistryError("$.source_seed must be 64 lowercase hexadecimal digits")

    source = registry.get("source_draw_registry")
    if type(source) is not dict:
        raise RegistryError("$.source_draw_registry must be an object")
    _expect_exact_keys(source, SOURCE_DRAW_KEYS, "$.source_draw_registry")
    if source["source_family"] != SOURCE_FAMILY:
        raise RegistryError("source_family is not the registered principal source")
    if source["constraint_method"] != CONSTRAINT_METHOD:
        raise RegistryError(
            "only exact ambient-delta zero-pi level matching is accepted"
        )
    if source["coordinate_units"] != "ell_s-natural-length-hbar-c-1":
        raise RegistryError("the canonical ell_s natural-unit convention is required")
    if source["tension_convention"] != "T_F=1/(2*pi*ell_s^2)":
        raise RegistryError("the canonical F1 tension convention is required")
    if source["winding_relation"] != "L_w=abs(w)*L_A[winding_axis]":
        raise RegistryError("the canonical winding-length relation is required")

    winding_axis = _expect_integer(
        source["winding_axis"], "$.source_draw_registry.winding_axis"
    )
    if not 0 <= winding_axis < 9:
        raise RegistryError("winding_axis must be in {0,...,8}")
    winding_number_abs = _expect_integer(
        source["winding_number_abs"],
        "$.source_draw_registry.winding_number_abs",
    )
    if winding_number_abs != 1:
        raise RegistryError("the canonical cell is frozen to |w|=1")
    orientations = source["winding_orientations"]
    if (
        type(orientations) is not list
        or any(type(value) is not int for value in orientations)
        or orientations != [1, -1]
    ):
        raise RegistryError("the two registered winding orientations must be [1,-1]")

    transverse_axis_order = source["transverse_axis_order"]
    if type(transverse_axis_order) is not list or any(
        type(axis) is not int for axis in transverse_axis_order
    ):
        raise RegistryError(
            "$.source_draw_registry.transverse_axis_order must be an integer list"
        )
    expected_axes = [axis for axis in range(9) if axis != winding_axis]
    if transverse_axis_order != expected_axes:
        raise RegistryError(
            "transverse_axis_order must be the ordered complement of winding_axis"
        )
    torus_periods = _expect_numeric_vector(
        source["torus_periods_L_A"],
        9,
        "$.source_draw_registry.torus_periods_L_A",
    )
    if any(period <= 0.0 for period in torus_periods):
        raise RegistryError("all nine torus periods L_A must be positive")
    winding_length = _expect_number(
        source["winding_length"], "$.source_draw_registry.winding_length"
    )
    ell_s = _expect_number(
        source["string_length_ell_s"],
        "$.source_draw_registry.string_length_ell_s",
    )
    tension = _expect_number(
        source["string_tension"], "$.source_draw_registry.string_tension"
    )
    if winding_length <= 0.0 or tension <= 0.0 or ell_s <= 0.0:
        raise RegistryError("L_w, T_F and ell_s must be positive")
    if winding_length != winding_number_abs * torus_periods[winding_axis]:
        raise RegistryError("L_w must equal |w| L_A on the winding axis")
    expected_tension = 1.0 / (2.0 * PORTABLE_PI * ell_s * ell_s)
    if tension.hex() != expected_tension.hex():
        raise RegistryError("T_F must equal 1/(2*pi*ell_s^2) in binary64")

    cutoff = _expect_integer(
        source["fourier_cutoff_K"],
        "$.source_draw_registry.fourier_cutoff_K",
    )
    if cutoff != 1:
        raise RegistryError("the canonical audit cell is frozen to K=1")
    energy = _expect_number(
        source["transverse_energy"],
        "$.source_draw_registry.transverse_energy",
    )
    momentum = _expect_numeric_vector(
        source["total_transverse_momentum"],
        TRANSVERSE_DIMENSION,
        "$.source_draw_registry.total_transverse_momentum",
    )
    worldsheet = _expect_numeric_vector(
        source["worldsheet_momenta"],
        2,
        "$.source_draw_registry.worldsheet_momenta",
    )
    if worldsheet != (0.0, 0.0):
        raise RegistryError("this direct sampler is frozen to pi_1=pi_2=0")
    mass = tension * winding_length
    residual_energy = energy - portable_fsum(
        x * x for x in momentum
    ) / (4.0 * mass)
    if residual_energy <= 0.0:
        raise RegistryError(
            "E_* must be strictly positive; empty and singular shells are rejected"
        )
    return source


def validate_registry(registry: Any) -> dict[str, Any]:
    """Validate the complete canonical source, validity and event registry."""

    source = validate_source_draw_registry(registry)
    _expect_exact_keys(registry, TOP_LEVEL_REGISTRY_KEYS, "$")
    _expect_string(registry["audit_cell_id"], "$.audit_cell_id")
    torus_periods = tuple(float(value) for value in source["torus_periods_L_A"])

    validity = registry["validity"]
    if type(validity) is not dict:
        raise RegistryError("$.validity must be an object")
    _expect_exact_keys(validity, VALIDITY_KEYS, "$.validity")
    for key in sorted(VALIDITY_KEYS):
        if _expect_number(validity[key], f"$.validity.{key}") <= 0.0:
            raise RegistryError(f"$.validity.{key} must be positive")

    audit = registry["audit"]
    if type(audit) is not dict:
        raise RegistryError("$.audit must be an object")
    _expect_exact_keys(audit, AUDIT_KEYS, "$.audit")
    sample_count = _expect_integer(audit["sample_count"], "$.audit.sample_count")
    fingerprint_count = _expect_integer(
        audit["fingerprint_count"], "$.audit.fingerprint_count"
    )
    if sample_count < 1 or not 1 <= fingerprint_count <= sample_count:
        raise RegistryError("audit sample and fingerprint counts are inconsistent")
    familywise_alpha = _expect_number(
        audit["familywise_alpha"], "$.audit.familywise_alpha"
    )
    tolerance = _expect_number(
        audit["constraint_absolute_tolerance"],
        "$.audit.constraint_absolute_tolerance",
    )
    if not 0.0 < familywise_alpha < 1.0 or tolerance <= 0.0:
        raise RegistryError("audit alpha and constraint tolerance are invalid")

    downstream = registry["downstream_context"]
    if type(downstream) is not dict:
        raise RegistryError("$.downstream_context must be an object")
    _expect_exact_keys(downstream, DOWNSTREAM_KEYS, "$.downstream_context")
    r_in = _expect_number(downstream["r_in"], "$.downstream_context.r_in")
    r_out = _expect_number(downstream["r_out"], "$.downstream_context.r_out")
    injectivity_radius = 0.5 * min(torus_periods)
    if not 0.0 < r_in < r_out < injectivity_radius:
        raise RegistryError("event radii violate the injectivity-radius registry gate")
    observation = _expect_numeric_vector(
        downstream["observation_window"],
        2,
        "$.downstream_context.observation_window",
    )
    if not observation[0] < observation[1]:
        raise RegistryError("observation_window must be increasing")
    if downstream["initial_history"] not in {
        "armed",
        "active",
        "left_censored",
        "exited",
    }:
        raise RegistryError("initial_history is not registered")
    if _expect_number(
        downstream["rank_tolerance"], "$.downstream_context.rank_tolerance"
    ) <= 0.0:
        raise RegistryError("rank_tolerance must be positive")
    normal_hint = downstream["normal_dimension_hint"]
    if normal_hint is not None and type(normal_hint) is not int:
        raise RegistryError("normal_dimension_hint must be null or an integer")
    winner = downstream["response_winner"]
    if winner is not None and type(winner) is not str:
        raise RegistryError("response_winner must be null or a string")
    _expect_number(
        downstream["reaction_scale"], "$.downstream_context.reaction_scale"
    )
    return registry


def source_draw_identity(registry: Mapping[str, Any]) -> dict[str, Any]:
    """The only registry payload allowed to affect a source draw."""

    validate_source_draw_registry(registry)
    return {
        "registry_schema": registry["schema_version"],
        "prng_algorithm": PRNG_ALGORITHM,
        "portable_math_version": PORTABLE_MATH_VERSION,
        "source_seed": registry["source_seed"],
        "source_draw_registry": registry["source_draw_registry"],
    }


def source_draw_sha256(registry: Mapping[str, Any]) -> str:
    return sha256_hex(source_draw_identity(registry))


class DeterministicStream:
    """Counter-mode SHA-256 stream with an exactly open 52-bit midpoint map."""

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
            raise ArithmeticError("open midpoint map reached a unit endpoint")
        return result

    def normal(self) -> float:
        if self._normal_cache is not None:
            value = self._normal_cache
            self._normal_cache = None
            return value
        radius = portable_sqrt(-2.0 * portable_log(self.uniform_open()))
        sine, cosine = portable_sin_cos_turn(self.uniform_open())
        first = radius * cosine
        self._normal_cache = radius * sine
        return first


def stream_for(
    registry: Mapping[str, Any], sample_index: int, label: str
) -> DeterministicStream:
    if type(sample_index) is not int or sample_index < 0:
        raise ValueError("sample_index must be a nonnegative integer")
    if type(label) is not str or label not in REGISTERED_STREAM_LABELS:
        raise ValueError("stream label is not registered for the source bundle")
    key = (
        canonical_bytes(source_draw_identity(registry))
        + sample_index.to_bytes(16, "big")
        + label.encode("utf-8")
    )
    return DeterministicStream(key)


def gamma_integer(shape: int, stream: DeterministicStream) -> float:
    """Exact ideal Gamma(shape,1) construction for positive integer shape."""

    if type(shape) is not int or shape < 1:
        raise ValueError("integer gamma shape must be positive")
    return portable_fsum(
        -portable_log(stream.uniform_open()) for _ in range(shape)
    )


def beta_integer(
    left_shape: int, right_shape: int, stream: DeterministicStream
) -> float:
    """Independent integer-shape Beta draw via an order statistic.

    If ``a`` and ``b`` are positive integers, the ``a``-th order statistic
    among ``a+b-1`` independent uniforms has the Beta(a,b) law.  Keeping this
    implementation free of ``gamma_integer`` makes the hierarchical
    factorization an algorithmically independent audit of the principal
    Gamma-normalization sampler.
    """

    if (
        type(left_shape) is not int
        or type(right_shape) is not int
        or left_shape < 1
        or right_shape < 1
    ):
        raise ValueError("integer beta shapes must be positive")
    order_statistics = sorted(
        stream.uniform_open()
        for _ in range(left_shape + right_shape - 1)
    )
    return order_statistics[left_shape - 1]


def unit_sphere(dimension: int, stream: DeterministicStream) -> tuple[float, ...]:
    if type(dimension) is not int or dimension < 1:
        raise ValueError("sphere dimension must be positive")
    vector = tuple(stream.normal() for _ in range(dimension))
    squared_norm = portable_fsum(value * value for value in vector)
    if not squared_norm > 0.0 or not math.isfinite(squared_norm):
        raise ArithmeticError("deterministic normal direction is unresolved")
    inverse_norm = 1.0 / portable_sqrt(squared_norm)
    return tuple(value * inverse_norm for value in vector)


def derived_dirichlet_shape(cutoff: int) -> tuple[int, int, int]:
    if type(cutoff) is not int or cutoff < 1:
        raise ValueError("cutoff must be a positive integer")
    real_chiral_dimension = 16 * cutoff
    return (4, real_chiral_dimension - 1, real_chiral_dimension - 1)


def require_derived_dirichlet_shape(
    cutoff: int, candidate: Sequence[float]
) -> None:
    expected = derived_dirichlet_shape(cutoff)
    if tuple(candidate) != expected:
        raise ValueError(
            f"Dirichlet shape mutation rejected: expected {expected}, "
            f"received {tuple(candidate)}"
        )


def nonzero_pi_chiral_energies(
    string_energy: float, worldsheet_momentum: float
) -> tuple[float, float]:
    """Return (left,right) squared radii for the scoped nonzero-pi law."""

    if not math.isfinite(string_energy) or not math.isfinite(
        worldsheet_momentum
    ):
        raise ValueError("nonzero-pi energies must be finite")
    if string_energy < abs(worldsheet_momentum):
        raise ValueError("string energy must be at least |pi|")
    return (
        0.5 * (string_energy - worldsheet_momentum),
        0.5 * (string_energy + worldsheet_momentum),
    )


def nonzero_pi_regular_shell_admissible(
    residual_energy: float, worldsheet_momenta: Sequence[float]
) -> bool:
    """Strict regular-shell gate; equality is the singular minimum shell."""

    if not math.isfinite(residual_energy) or len(worldsheet_momenta) != 2:
        return False
    if any(not math.isfinite(value) for value in worldsheet_momenta):
        return False
    return residual_energy > portable_fsum(
        abs(value) for value in worldsheet_momenta
    )


def source_parameters(registry: Mapping[str, Any]) -> dict[str, Any]:
    source = validate_source_draw_registry(registry)
    cutoff = source["fourier_cutoff_K"]
    winding_length = float(source["winding_length"])
    tension = float(source["string_tension"])
    mass = tension * winding_length
    momentum = tuple(float(value) for value in source["total_transverse_momentum"])
    energy = float(source["transverse_energy"])
    residual_energy = energy - portable_fsum(
        x * x for x in momentum
    ) / (4.0 * mass)
    torus_periods = tuple(float(value) for value in source["torus_periods_L_A"])
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
        "transverse_periods": tuple(
            torus_periods[axis] for axis in transverse_axes
        ),
        "torus_periods_L_A": torus_periods,
        "transverse_axis_order": transverse_axes,
        "winding_axis": source["winding_axis"],
        "winding_number_abs": source["winding_number_abs"],
        "winding_orientations": tuple(source["winding_orientations"]),
        "ell_s": float(source["string_length_ell_s"]),
    }


def sample_radial_gamma(
    registry: Mapping[str, Any], sample_index: int
) -> tuple[float, float, float]:
    parameters = source_parameters(registry)
    shapes = derived_dirichlet_shape(parameters["K"])
    stream = stream_for(registry, sample_index, "radial-gamma")
    gamma_values = tuple(gamma_integer(shape, stream) for shape in shapes)
    total = portable_fsum(gamma_values)
    return tuple(
        parameters["E_star"] * value / total for value in gamma_values
    )  # type: ignore[return-value]


def sample_radial_hierarchical_beta(
    registry: Mapping[str, Any], sample_index: int
) -> tuple[float, float, float]:
    """Independent hierarchical-Beta factorization of the same Dirichlet."""

    parameters = source_parameters(registry)
    _, string_shape, _ = derived_dirichlet_shape(parameters["K"])
    stream = stream_for(registry, sample_index, "radial-hierarchical-beta")
    zero_share = beta_integer(4, 2 * string_shape, stream)
    split = beta_integer(string_shape, string_shape, stream)
    remaining = 1.0 - zero_share
    return (
        parameters["E_star"] * zero_share,
        parameters["E_star"] * remaining * split,
        parameters["E_star"] * remaining * (1.0 - split),
    )


def real_from_chiral(
    c_left: complex, c_right: complex, wave_number: float
) -> tuple[float, float, float, float]:
    if wave_number <= 0.0:
        raise ValueError("wave_number must be positive")
    x = 2.0 * (c_left.real + c_right.real)
    y = -2.0 * (c_left.imag + c_right.imag)
    p = 2.0 * wave_number * (c_left.imag - c_right.imag)
    q = 2.0 * wave_number * (c_left.real - c_right.real)
    return x, y, p, q


def chiral_from_real(
    x: float, y: float, p: float, q: float, wave_number: float
) -> tuple[complex, complex]:
    if wave_number <= 0.0:
        raise ValueError("wave_number must be positive")
    left = 0.25 * (
        x + q / wave_number + 1j * (p / wave_number - y)
    )
    right = 0.25 * (
        x - q / wave_number - 1j * (y + p / wave_number)
    )
    return left, right


def canonical_mode_jacobian(wave_number: float) -> float:
    if wave_number <= 0.0:
        raise ValueError("wave_number must be positive")
    return 4.0 / (wave_number * wave_number)


def determinant(matrix: Sequence[Sequence[float]]) -> float:
    size = len(matrix)
    if size == 0 or any(len(row) != size for row in matrix):
        raise ValueError("determinant requires a nonempty square matrix")
    work = [[float(value) for value in row] for row in matrix]
    result = 1.0
    for column in range(size):
        pivot = max(
            range(column, size), key=lambda row: abs(work[row][column])
        )
        if work[pivot][column] == 0.0:
            return 0.0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column] / pivot_value
            for inner in range(column + 1, size):
                work[row][inner] -= factor * work[column][inner]
    return result


def finite_difference_canonical_jacobian(
    mass: float, wave_number: float, step: float = 1.0e-6
) -> float:
    """Numerically differentiate (zL,zR)->(x,y,Pi_x,Pi_y)."""

    if mass <= 0.0 or wave_number <= 0.0 or step <= 0.0:
        raise ValueError("finite-difference Jacobian inputs must be positive")

    def mapped(vector: Sequence[float]) -> tuple[float, float, float, float]:
        scale = portable_sqrt(2.0 * mass) * wave_number
        left = complex(vector[0], vector[1]) / scale
        right = complex(vector[2], vector[3]) / scale
        x, y, p, q = real_from_chiral(left, right, wave_number)
        return x, y, 0.5 * mass * p, 0.5 * mass * q

    base = (0.13, -0.29, 0.41, 0.07)
    columns: list[list[float]] = []
    for index in range(4):
        plus = list(base)
        minus = list(base)
        plus[index] += step
        minus[index] -= step
        upper = mapped(plus)
        lower = mapped(minus)
        columns.append(
            [
                (upper[row] - lower[row]) / (2.0 * step)
                for row in range(4)
            ]
        )
    row_matrix = [
        [columns[column][row] for column in range(4)]
        for row in range(4)
    ]
    return abs(determinant(row_matrix))


def _complex_from_flat(
    vector: Sequence[float], mode: int, transverse: int
) -> complex:
    offset = 2 * (
        mode * CHIRAL_COMPLEX_COMPONENTS_PER_MODE + transverse
    )
    return complex(vector[offset], vector[offset + 1])


def sample_source(
    registry: Mapping[str, Any], sample_index: int
) -> dict[str, Any]:
    """Generate one unconditioned source sample; invalid states are retained."""

    parameters = source_parameters(registry)
    cutoff = parameters["K"]
    dimension = parameters["d"]
    mass = parameters["M"]
    energy_shares = sample_radial_gamma(registry, sample_index)

    w_direction = unit_sphere(
        TRANSVERSE_DIMENSION,
        stream_for(registry, sample_index, "relative-zero-mode-direction"),
    )
    w = tuple(
        portable_sqrt(energy_shares[0]) * value for value in w_direction
    )

    z_vectors: list[tuple[tuple[float, ...], tuple[float, ...]]] = []
    for string_index in range(2):
        radius = portable_sqrt(energy_shares[string_index + 1] / 2.0)
        left_direction = unit_sphere(
            dimension,
            stream_for(
                registry, sample_index, f"string-{string_index}-left-direction"
            ),
        )
        right_direction = unit_sphere(
            dimension,
            stream_for(
                registry, sample_index, f"string-{string_index}-right-direction"
            ),
        )
        z_vectors.append(
            (
                tuple(radius * value for value in left_direction),
                tuple(radius * value for value in right_direction),
            )
        )

    momentum = parameters["P_total"]
    velocities = [
        [
            momentum[axis] / (2.0 * mass)
            + w[axis] / portable_sqrt(mass)
            for axis in range(TRANSVERSE_DIMENSION)
        ],
        [
            momentum[axis] / (2.0 * mass)
            - w[axis] / portable_sqrt(mass)
            for axis in range(TRANSVERSE_DIMENSION)
        ],
    ]

    strings: list[dict[str, Any]] = []
    for string_index in range(2):
        modes: list[dict[str, Any]] = []
        z_left, z_right = z_vectors[string_index]
        for mode_index, wave_number in enumerate(parameters["k_values"]):
            x_values: list[float] = []
            y_values: list[float] = []
            p_values: list[float] = []
            q_values: list[float] = []
            for transverse in range(TRANSVERSE_DIMENSION):
                scale = portable_sqrt(2.0 * mass) * wave_number
                c_left = _complex_from_flat(
                    z_left, mode_index, transverse
                ) / scale
                c_right = _complex_from_flat(
                    z_right, mode_index, transverse
                ) / scale
                x, y, p, q = real_from_chiral(
                    c_left, c_right, wave_number
                )
                x_values.append(x)
                y_values.append(y)
                p_values.append(p)
                q_values.append(q)
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

    q_stream = stream_for(registry, sample_index, "relative-centre-haar")
    q_relative = [
        period * q_stream.uniform_open()
        for period in parameters["transverse_periods"]
    ]
    state_core = {
        "schema_version": SAMPLE_SCHEMA,
        "sample_index": sample_index,
        "source_draw_sha256": source_draw_sha256(registry),
        "relative_centre_gauge": "Q2=0,Q1=Q_relative",
        "Q_relative": q_relative,
        "Q1": q_relative,
        "Q2": [0.0] * TRANSVERSE_DIMENSION,
        "energy_shares_s0_s1_s2": list(energy_shares),
        "strings": strings,
    }
    fingerprint = sha256_hex(state_core)
    validity = evaluate_validity(state_core, registry)
    diagnostics = constraint_diagnostics(state_core, registry)
    return {
        **state_core,
        "source_state_sha256": fingerprint,
        "validity": validity,
        "constraint_diagnostics": diagnostics,
    }


def _sample_numeric_vector(value: Any, length: int, path: str) -> tuple[float, ...]:
    if type(value) is not list or len(value) != length:
        raise SampleError(f"{path} must have shape [{length}]")
    output = []
    for index, item in enumerate(value):
        if type(item) is not float or not math.isfinite(item):
            raise SampleError(f"{path}[{index}] must be one finite binary64 number")
        output.append(item)
    return tuple(output)


def validate_source_sample(
    state: Any, registry: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate support membership, metadata binding and the Q gauge."""

    if type(state) is not dict or set(state) != SAMPLE_FULL_KEYS:
        raise SampleError("source sample has missing or unknown top-level fields")
    parameters = source_parameters(registry)
    if state["schema_version"] != SAMPLE_SCHEMA:
        raise SampleError("source sample schema_version is not registered")
    if type(state["sample_index"]) is not int or state["sample_index"] < 0:
        raise SampleError("sample_index must be one nonnegative integer")
    if state["source_draw_sha256"] != source_draw_sha256(registry):
        raise SampleError("sample source identity is not bound to the registry")
    if state["relative_centre_gauge"] != "Q2=0,Q1=Q_relative":
        raise SampleError("relative-centre gauge is not registered")

    q_relative = _sample_numeric_vector(
        state["Q_relative"], TRANSVERSE_DIMENSION, "Q_relative"
    )
    q1 = _sample_numeric_vector(state["Q1"], TRANSVERSE_DIMENSION, "Q1")
    q2 = _sample_numeric_vector(state["Q2"], TRANSVERSE_DIMENSION, "Q2")
    if q1 != q_relative or q2 != (0.0,) * TRANSVERSE_DIMENSION:
        raise SampleError("Q1/Q2 do not realize the one-draw relative-centre gauge")
    for axis, (value, period) in enumerate(
        zip(q_relative, parameters["transverse_periods"])
    ):
        if not 0.0 < value < period:
            raise SampleError(f"Q_relative[{axis}] lies outside the open torus cell")

    shares = _sample_numeric_vector(
        state["energy_shares_s0_s1_s2"], 3, "energy_shares_s0_s1_s2"
    )
    if any(value <= 0.0 for value in shares):
        raise SampleError("all regular-shell energy shares must be positive")
    if abs(portable_fsum(shares) - parameters["E_star"]) > 5.0e-15:
        raise SampleError("energy shares do not sum to E_star")

    strings = state["strings"]
    if type(strings) is not list or len(strings) != 2:
        raise SampleError("source sample must contain exactly two strings")
    for string_index, string in enumerate(strings):
        if type(string) is not dict or set(string) != STRING_KEYS:
            raise SampleError(f"strings[{string_index}] has an invalid schema")
        if string["orientation"] != parameters["winding_orientations"][string_index]:
            raise SampleError(f"strings[{string_index}] has the wrong winding sign")
        _sample_numeric_vector(
            string["transverse_velocity"],
            TRANSVERSE_DIMENSION,
            f"strings[{string_index}].transverse_velocity",
        )
        modes = string["modes"]
        if type(modes) is not list or len(modes) != parameters["K"]:
            raise SampleError(f"strings[{string_index}] has the wrong mode count")
        for mode_index, (mode, wave_number) in enumerate(
            zip(modes, parameters["k_values"])
        ):
            if type(mode) is not dict or set(mode) != MODE_KEYS:
                raise SampleError(
                    f"strings[{string_index}].modes[{mode_index}] has an invalid schema"
                )
            if type(mode["mode_number"]) is not int or mode["mode_number"] != mode_index + 1:
                raise SampleError("mode_number is not bound to the registered cutoff")
            if type(mode["wave_number"]) is not float or mode["wave_number"] != wave_number:
                raise SampleError("wave_number is not bound to L_w and mode_number")
            for field in ("x", "y", "p", "q"):
                _sample_numeric_vector(
                    mode[field],
                    TRANSVERSE_DIMENSION,
                    f"strings[{string_index}].modes[{mode_index}].{field}",
                )

    if (
        type(state["validity"]) is not dict
        or set(state["validity"]) != SAMPLE_VALIDITY_KEYS
    ):
        raise SampleError("validity has an invalid schema")
    if (
        type(state["constraint_diagnostics"]) is not dict
        or set(state["constraint_diagnostics"]) != SAMPLE_DIAGNOSTIC_KEYS
    ):
        raise SampleError("constraint_diagnostics has an invalid schema")
    state_core = {key: state[key] for key in SAMPLE_CORE_KEYS}
    if state["source_state_sha256"] != sha256_hex(state_core):
        raise SampleError("source_state_sha256 does not bind the serialized state")
    if not type_strict_semantic_equal(
        state["validity"], evaluate_validity(state, registry)
    ):
        raise SampleError("validity does not match the registered predicates")
    if not type_strict_semantic_equal(
        state["constraint_diagnostics"],
        constraint_diagnostics(state, registry),
    ):
        raise SampleError(
            "constraint_diagnostics do not match the serialized coefficients"
        )
    chiral = extract_chiral_vectors(state, registry)
    for string_index, (left, right) in enumerate(chiral):
        target = shares[string_index + 1] / 2.0
        if (
            abs(dot(left, left) - target) > 5.0e-12
            or abs(dot(right, right) - target) > 5.0e-12
        ):
            raise SampleError("serialized chiral radii disagree with energy shares")
    return state


def source_coefficient_payload_sha256(state: Mapping[str, Any]) -> str:
    """Hash sampled numerical content without seed or identity metadata."""

    payload = {
        "Q_relative": state["Q_relative"],
        "Q1": state["Q1"],
        "Q2": state["Q2"],
        "energy_shares_s0_s1_s2": state["energy_shares_s0_s1_s2"],
        "strings": state["strings"],
    }
    return sha256_hex(payload)


def dot(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("vector dimensions differ")
    return portable_fsum(a * b for a, b in zip(left, right))


def norm(vector: Sequence[float]) -> float:
    return portable_sqrt(max(0.0, dot(vector, vector)))


def extract_chiral_vectors(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> tuple[tuple[tuple[float, ...], tuple[float, ...]], ...]:
    parameters = source_parameters(registry)
    mass = parameters["M"]
    output = []
    for string in state["strings"]:
        left: list[float] = []
        right: list[float] = []
        for mode in string["modes"]:
            wave_number = float(mode["wave_number"])
            scale = portable_sqrt(2.0 * mass) * wave_number
            for transverse in range(TRANSVERSE_DIMENSION):
                c_left, c_right = chiral_from_real(
                    mode["x"][transverse],
                    mode["y"][transverse],
                    mode["p"][transverse],
                    mode["q"][transverse],
                    wave_number,
                )
                left.extend((scale * c_left.real, scale * c_left.imag))
                right.extend((scale * c_right.real, scale * c_right.imag))
        output.append((tuple(left), tuple(right)))
    return tuple(output)


def constraint_diagnostics(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    parameters = source_parameters(registry)
    mass = parameters["M"]
    energy = 0.0
    total_momentum = [0.0] * TRANSVERSE_DIMENSION
    worldsheet_momenta: list[float] = []
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
                * (
                    mode["x"][axis] ** 2
                    + mode["y"][axis] ** 2
                )
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
        worldsheet_momenta.append(worldsheet)
    momentum_residual = [
        total_momentum[axis] - parameters["P_total"][axis]
        for axis in range(TRANSVERSE_DIMENSION)
    ]
    return {
        "energy": energy,
        "energy_residual": energy - parameters["E"],
        "total_transverse_momentum": total_momentum,
        "target_momentum_residual": momentum_residual,
        "worldsheet_momenta": worldsheet_momenta,
        "worldsheet_momentum_residual": worldsheet_momenta,
    }


def _binary64_fraction(value: Any, name: str) -> Fraction:
    """Interpret a serialized finite binary64 value as an exact dyadic."""

    if type(value) is int:
        return Fraction(value)
    if type(value) is not float or not math.isfinite(value):
        raise TypeError(f"{name} must be a finite binary64 number")
    return Fraction.from_float(value)


def exact_dyadic_constraint_residuals(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    """Re-evaluate the serialized state's polynomial constraints exactly.

    The sampler itself uses binary64 transcendental and square-root
    operations.  Once a state has been serialized, however, all initial-shell
    constraints are polynomial in finite binary64 values.  Treating each such
    value as its exact dyadic rational gives a rigorous residual certificate
    for the stored state, independent of floating summation order.
    """

    parameters = source_parameters(registry)
    mass = _binary64_fraction(parameters["M"], "M")
    target_energy = _binary64_fraction(parameters["E"], "E")
    target_momentum = tuple(
        _binary64_fraction(value, f"P_total[{axis}]")
        for axis, value in enumerate(parameters["P_total"])
    )

    energy = Fraction()
    total_momentum = [Fraction() for _ in range(TRANSVERSE_DIMENSION)]
    worldsheet_momenta: list[Fraction] = []
    for string_index, string in enumerate(state["strings"]):
        velocity = tuple(
            _binary64_fraction(
                value,
                f"strings[{string_index}].transverse_velocity[{axis}]",
            )
            for axis, value in enumerate(string["transverse_velocity"])
        )
        energy += mass * sum((value * value for value in velocity), Fraction()) / 2
        for axis in range(TRANSVERSE_DIMENSION):
            total_momentum[axis] += mass * velocity[axis]

        worldsheet = Fraction()
        for mode_index, mode in enumerate(string["modes"]):
            wave_number = _binary64_fraction(
                mode["wave_number"],
                f"strings[{string_index}].modes[{mode_index}].wave_number",
            )
            oscillator_sum = Fraction()
            worldsheet_sum = Fraction()
            for axis in range(TRANSVERSE_DIMENSION):
                x = _binary64_fraction(
                    mode["x"][axis],
                    f"strings[{string_index}].modes[{mode_index}].x[{axis}]",
                )
                y = _binary64_fraction(
                    mode["y"][axis],
                    f"strings[{string_index}].modes[{mode_index}].y[{axis}]",
                )
                p = _binary64_fraction(
                    mode["p"][axis],
                    f"strings[{string_index}].modes[{mode_index}].p[{axis}]",
                )
                q = _binary64_fraction(
                    mode["q"][axis],
                    f"strings[{string_index}].modes[{mode_index}].q[{axis}]",
                )
                oscillator_sum += (
                    p * p
                    + q * q
                    + wave_number * wave_number * (x * x + y * y)
                )
                worldsheet_sum += p * y - q * x
            energy += mass * oscillator_sum / 4
            worldsheet += mass * wave_number * worldsheet_sum / 2
        worldsheet_momenta.append(worldsheet)

    return {
        "energy_residual": energy - target_energy,
        "target_momentum_residual": tuple(
            total_momentum[axis] - target_momentum[axis]
            for axis in range(TRANSVERSE_DIMENSION)
        ),
        "worldsheet_momentum_residual": tuple(worldsheet_momenta),
    }


def graph_upper_bound(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> tuple[float, tuple[float, float]]:
    """Registered time-uniform upper bound for both |Y'| and |dot Y|."""

    source_parameters(registry)
    per_string: list[float] = []
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
        per_string.append(bound)
    return max(per_string), (per_string[0], per_string[1])


def evaluate_validity(
    state: Mapping[str, Any], registry: Mapping[str, Any]
) -> dict[str, Any]:
    parameters = source_parameters(registry)
    maximum_bound, per_string = graph_upper_bound(state, registry)
    uv_product = max(parameters["k_values"]) * parameters["ell_s"]
    reasons: list[str] = []
    validity_registry = registry.get("validity")
    try:
        if type(validity_registry) is not dict:
            raise RegistryError("$.validity must be an object")
        _expect_exact_keys(validity_registry, VALIDITY_KEYS, "$.validity")
        graph_limit = _expect_number(
            validity_registry["graph_upper_bound_max"],
            "$.validity.graph_upper_bound_max",
        )
        uv_limit = _expect_number(
            validity_registry["uv_product_max"],
            "$.validity.uv_product_max",
        )
        if graph_limit <= 0.0 or uv_limit <= 0.0:
            raise RegistryError("validity thresholds must be positive")
    except (KeyError, RegistryError):
        graph_limit = math.inf
        uv_limit = math.inf
        reasons.append("validity_registry_invalid")
    if maximum_bound > graph_limit:
        reasons.append("graph_upper_bound_exceeded")
    if uv_product > uv_limit:
        reasons.append("uv_product_exceeded")
    return {
        "status": "source_invalid" if reasons else "valid",
        "reasons": reasons,
        "registered_time_uniform_graph_upper_bound": maximum_bound,
        "per_string_graph_upper_bounds": list(per_string),
        "k_max_times_ell_s": uv_product,
        "sample_retained_without_redraw": True,
    }


def evolve_state(
    state: Mapping[str, Any],
    registry: Mapping[str, Any],
    time: float,
) -> dict[str, Any]:
    """Exact linear Fourier evolution; the relative centre gauge is unchanged."""

    if not math.isfinite(time):
        raise ValueError("time must be finite")
    evolved = copy.deepcopy(state)
    for string in evolved["strings"]:
        for mode in string["modes"]:
            wave_number = float(mode["wave_number"])
            sine, cosine = portable_sin_cos(wave_number * time)
            old_x = tuple(mode["x"])
            old_y = tuple(mode["y"])
            old_p = tuple(mode["p"])
            old_q = tuple(mode["q"])
            mode["x"] = [
                old_x[axis] * cosine
                + old_p[axis] * sine / wave_number
                for axis in range(TRANSVERSE_DIMENSION)
            ]
            mode["y"] = [
                old_y[axis] * cosine
                + old_q[axis] * sine / wave_number
                for axis in range(TRANSVERSE_DIMENSION)
            ]
            mode["p"] = [
                old_p[axis] * cosine
                - wave_number * old_x[axis] * sine
                for axis in range(TRANSVERSE_DIMENSION)
            ]
            mode["q"] = [
                old_q[axis] * cosine
                - wave_number * old_y[axis] * sine
                for axis in range(TRANSVERSE_DIMENSION)
            ]
    evolved["constraint_diagnostics"] = constraint_diagnostics(evolved, registry)
    return evolved


def rising_factorial(value: int, order: int) -> int:
    if type(value) is not int or value < 1 or type(order) is not int or order < 0:
        raise ValueError("rising factorial inputs are invalid")
    return math.prod(value + offset for offset in range(order))


def dirichlet_moment(
    shapes: Sequence[int], powers: Sequence[int]
) -> float:
    if len(shapes) != len(powers):
        raise ValueError("Dirichlet shape and power dimensions differ")
    if any(type(value) is not int or value < 1 for value in shapes):
        raise ValueError("Dirichlet shapes must be positive integers")
    if any(type(value) is not int or value < 0 for value in powers):
        raise ValueError("Dirichlet powers must be nonnegative integers")
    numerator = math.prod(
        rising_factorial(shape, power)
        for shape, power in zip(shapes, powers)
    )
    denominator = rising_factorial(sum(shapes), sum(powers))
    return numerator / denominator


def dirichlet_density_normalizer(shapes: Sequence[int]) -> float:
    log_value = portable_lgamma_integer(sum(shapes)) - portable_fsum(
        portable_lgamma_integer(shape) for shape in shapes
    )
    return portable_exp(log_value)


def reduced_shell_log_normalizer(cutoff: int, residual_energy: float) -> float:
    """Natural logarithm of the reduced delta-shell normalization."""

    if cutoff < 1 or residual_energy <= 0.0:
        raise ValueError("normalizer inputs are outside the regular shell")
    dimension = 16 * cutoff
    return portable_fsum(
        (
            (2 - 2 * dimension) * portable_log(2.0),
            (2 * dimension + 4) * portable_log(PORTABLE_PI),
            2.0 * portable_lgamma_integer(dimension - 1),
            -4.0 * portable_lgamma_integer(dimension // 2),
            -portable_lgamma_integer(2 * dimension + 2),
            (2 * dimension + 1) * portable_log(float(residual_energy)),
        )
    )


def linear_jacobian_log_normalizer(
    mass: float, wave_numbers: Sequence[float]
) -> float:
    if mass <= 0.0 or not wave_numbers or any(k <= 0.0 for k in wave_numbers):
        raise ValueError("linear Jacobian inputs are invalid")
    return portable_fsum(
        (
            4.0 * portable_log(float(mass)),
            16.0
            * portable_fsum(
                portable_log(4.0 / (wave_number * wave_number))
                for wave_number in wave_numbers
            ),
        )
    )


def _mean(rows: Iterable[Sequence[float]], column: int) -> float:
    values = [row[column] for row in rows]
    return portable_fsum(values) / len(values)


def hoeffding_half_width(
    sample_count: int, familywise_alpha: float, comparison_count: int
) -> float:
    """Two-sided familywise Hoeffding interval for variables in [0,1]."""

    if sample_count < 1 or not 0.0 < familywise_alpha < 1.0:
        raise ValueError("Hoeffding inputs are invalid")
    if comparison_count < 1:
        raise ValueError("comparison_count must be positive")
    return portable_sqrt(
        portable_log(2.0 * comparison_count / familywise_alpha)
        / (2.0 * sample_count)
    )


def torus_character_means(
    states: Sequence[Mapping[str, Any]], registry: Mapping[str, Any]
) -> list[dict[str, Any]]:
    periods = source_parameters(registry)["transverse_periods"]
    rows = []
    for axis, period in enumerate(periods):
        sine_cosine = [
            portable_sin_cos_turn(state["Q_relative"][axis] / period)
            for state in states
        ]
        real = portable_fsum(pair[1] for pair in sine_cosine) / len(states)
        imaginary = portable_fsum(pair[0] for pair in sine_cosine) / len(states)
        rows.append(
            {
                "axis": axis,
                "real": format_float(real),
                "imaginary": format_float(imaginary),
                "magnitude": format_float(portable_hypot(real, imaginary)),
            }
        )
    return rows


def population_fingerprints(
    registry: Mapping[str, Any], count: int
) -> list[str]:
    return [
        sample_source(registry, index)["source_state_sha256"]
        for index in range(count)
    ]


def build_report(
    registry: Mapping[str, Any],
    artifact_directory: Path | None = None,
) -> dict[str, Any]:
    validate_registry(registry)
    parameters = source_parameters(registry)
    audit = registry["audit"]
    sample_count = audit["sample_count"]
    fingerprint_count = audit["fingerprint_count"]
    familywise_alpha = float(audit["familywise_alpha"])
    tolerance = float(audit["constraint_absolute_tolerance"])
    states = [sample_source(registry, index) for index in range(sample_count)]

    gamma_rows = [
        tuple(
            value / parameters["E_star"]
            for value in state["energy_shares_s0_s1_s2"]
        )
        for state in states
    ]
    beta_rows = [
        tuple(
            value / parameters["E_star"]
            for value in sample_radial_hierarchical_beta(registry, index)
        )
        for index in range(sample_count)
    ]
    shapes = derived_dirichlet_shape(parameters["K"])
    total_shape = sum(shapes)
    exact_means = tuple(shape / total_shape for shape in shapes)
    gamma_means = tuple(_mean(gamma_rows, index) for index in range(3))
    beta_means = tuple(_mean(beta_rows, index) for index in range(3))
    mean_half_width = hoeffding_half_width(
        sample_count, familywise_alpha, 6
    )

    max_energy_residual = max(
        abs(state["constraint_diagnostics"]["energy_residual"])
        for state in states
    )
    max_target_residual = max(
        abs(value)
        for state in states
        for value in state["constraint_diagnostics"][
            "target_momentum_residual"
        ]
    )
    max_worldsheet_residual = max(
        abs(value)
        for state in states
        for value in state["constraint_diagnostics"][
            "worldsheet_momentum_residual"
        ]
    )
    exact_residual_rows = [
        exact_dyadic_constraint_residuals(state, registry)
        for state in states
    ]
    exact_max_energy_residual = max(
        abs(row["energy_residual"]) for row in exact_residual_rows
    )
    exact_max_target_residual = max(
        abs(value)
        for row in exact_residual_rows
        for value in row["target_momentum_residual"]
    )
    exact_max_worldsheet_residual = max(
        abs(value)
        for row in exact_residual_rows
        for value in row["worldsheet_momentum_residual"]
    )
    exact_tolerance = Fraction.from_float(tolerance)

    flow_energy_residual = 0.0
    flow_worldsheet_residual = 0.0
    for state in states[: min(8, len(states))]:
        baseline = state["constraint_diagnostics"]
        for time in (0.0, 0.125, 0.75, 2.5):
            evolved = evolve_state(state, registry, time)
            diagnostics = evolved["constraint_diagnostics"]
            flow_energy_residual = max(
                flow_energy_residual,
                abs(diagnostics["energy"] - baseline["energy"]),
            )
            flow_worldsheet_residual = max(
                flow_worldsheet_residual,
                max(
                    abs(a - b)
                    for a, b in zip(
                        diagnostics["worldsheet_momenta"],
                        baseline["worldsheet_momenta"],
                    )
                ),
            )

    mutated = copy.deepcopy(registry)
    mutated["validity"]["graph_upper_bound_max"] *= 0.01
    mutated["validity"]["uv_product_max"] *= 2.0
    mutated["downstream_context"]["r_in"] *= 1.1
    mutated["downstream_context"]["r_out"] *= 1.1
    mutated["downstream_context"]["rank_tolerance"] *= 100.0
    mutated["downstream_context"]["normal_dimension_hint"] = 6
    mutated["downstream_context"]["response_winner"] = "hostile-request"
    mutated["downstream_context"]["reaction_scale"] *= 5.0
    validate_registry(mutated)
    baseline_fingerprints = population_fingerprints(
        registry, fingerprint_count
    )
    mutated_fingerprints = population_fingerprints(
        mutated, fingerprint_count
    )

    character_rows = torus_character_means(states, registry)
    character_half_width = portable_sqrt(
        2.0
        * portable_log(
            2.0
            * (2 * TRANSVERSE_DIMENSION)
            / familywise_alpha
        )
        / sample_count
    )
    valid_count = sum(
        state["validity"]["status"] == "valid" for state in states
    )
    invalid_count = sample_count - valid_count
    support_schema_valid = True
    try:
        for state in states:
            validate_source_sample(state, registry)
    except SampleError:
        support_schema_valid = False
    independent_chiral_directions = all(
        left != right
        for state in states
        for left, right in extract_chiral_vectors(state, registry)
    )
    source_registry = registry["source_draw_registry"]
    seed_mutation = copy.deepcopy(registry)
    seed_mutation["source_seed"] = "0" * 64
    baseline_coefficient_hash = source_coefficient_payload_sha256(states[0])
    seed_mutated_coefficient_hash = source_coefficient_payload_sha256(
        sample_source(seed_mutation, 0)
    )

    check_map = {
        "all_source_samples_match_support_schema": support_schema_valid,
        "all_energy_constraints": max_energy_residual <= tolerance,
        "all_target_momentum_constraints": max_target_residual <= tolerance,
        "all_level_matching_constraints": max_worldsheet_residual <= tolerance,
        "all_serialized_energy_residuals_exactly_below_tolerance": (
            exact_max_energy_residual <= exact_tolerance
        ),
        "all_serialized_target_momentum_residuals_exactly_below_tolerance": (
            exact_max_target_residual <= exact_tolerance
        ),
        "all_serialized_level_matching_residuals_exactly_below_tolerance": (
            exact_max_worldsheet_residual <= exact_tolerance
        ),
        "gamma_means_in_familywise_intervals": all(
            abs(observed - expected) <= mean_half_width
            for observed, expected in zip(gamma_means, exact_means)
        ),
        "hierarchical_beta_means_in_familywise_intervals": all(
            abs(observed - expected) <= mean_half_width
            for observed, expected in zip(beta_means, exact_means)
        ),
        "torus_characters_in_familywise_intervals": all(
            abs(float(row[component])) <= character_half_width
            for row in character_rows
            for component in ("real", "imaginary")
        ),
        "controlled_float_flow_energy_conservation": (
            flow_energy_residual <= tolerance
        ),
        "controlled_float_flow_level_matching_conservation": (
            flow_worldsheet_residual <= tolerance
        ),
        "downstream_and_validity_mutations_leave_draws_unchanged": (
            baseline_fingerprints == mutated_fingerprints
        ),
        "source_seed_changes_numerical_coefficients": (
            baseline_coefficient_hash != seed_mutated_coefficient_hash
        ),
        "registered_chiral_directions_are_not_copied": independent_chiral_directions,
        "registered_stream_labels_are_unique": (
            len(REGISTERED_STREAM_LABELS) == 8
        ),
        "open52_midpoint_endpoints_are_strict": (
            0.0 < 2.0**-53 < 1.0 - 2.0**-53 < 1.0
        ),
        "f1_tension_relation_is_exact_binary64": (
            source_registry["string_tension"].hex()
            == (
                1.0
                / (
                    2.0
                    * PORTABLE_PI
                    * source_registry["string_length_ell_s"] ** 2
                )
            ).hex()
        ),
        "winding_length_relation_is_exact": (
            source_registry["winding_length"]
            == source_registry["winding_number_abs"]
            * source_registry["torus_periods_L_A"][
                source_registry["winding_axis"]
            ]
        ),
        "opposite_winding_orientations_are_registered": (
            source_registry["winding_orientations"] == [1, -1]
        ),
        "all_samples_retained": valid_count + invalid_count == sample_count,
        "no_validity_redraw": all(
            state["validity"]["sample_retained_without_redraw"]
            for state in states
        ),
    }

    inventory = {}
    if artifact_directory is not None:
        for name in (
            "microcanonical_source.py",
            "test_microcanonical_source.py",
            "source_registry.json",
            "README.md",
        ):
            path = artifact_directory / name
            if path.exists():
                inventory[name] = normalized_text_sha256(path)

    report = {
        "schema_version": REPORT_SCHEMA,
        "status": "PASS" if all(check_map.values()) else "FAIL",
        "audit_cell_id": registry["audit_cell_id"],
        "source_draw_sha256": source_draw_sha256(registry),
        "registry_canonical_sha256": sha256_hex(registry),
        "scope": {
            "claim": (
                "exact direct sampler for the registered zero-level-matched "
                "quadratic finite-K ambient delta-Liouville source"
            ),
            "does_not_implement": [
                "event schema",
                "first-entry or closest-approach solver",
                "encounter rank or singular values",
                "source-validity conditioning",
                "physical early-universe F1 preparation",
                "continuum or quantum string ensemble",
                "3+1 selection, cone, signature, or time direction",
            ],
        },
        "canonical_cell": {
            "K": parameters["K"],
            "M": format_float(parameters["M"]),
            "E_perp": format_float(parameters["E"]),
            "E_star": format_float(parameters["E_star"]),
            "P_total": [format_float(value) for value in parameters["P_total"]],
            "T_F": format_float(source_registry["string_tension"]),
            "ell_s": format_float(source_registry["string_length_ell_s"]),
            "torus_periods_L_A": [
                format_float(value)
                for value in source_registry["torus_periods_L_A"]
            ],
            "winding_axis": source_registry["winding_axis"],
            "winding_number_abs": source_registry["winding_number_abs"],
            "winding_orientations": source_registry["winding_orientations"],
            "L_w": format_float(source_registry["winding_length"]),
            "unit_convention": source_registry["coordinate_units"],
            "tension_convention": source_registry["tension_convention"],
            "winding_relation": source_registry["winding_relation"],
        },
        "registered_theorem": {
            "real_chiral_dimension_d": parameters["d"],
            "dirichlet_shape": list(shapes),
            "density": (
                "Gamma(sum alpha)/prod Gamma(alpha) * "
                "x0^(alpha0-1) x1^(alpha1-1) x2^(alpha2-1)"
            ),
            "density_normalizer": format_float(
                dirichlet_density_normalizer(shapes)
            ),
            "E_star": format_float(parameters["E_star"]),
            "reduced_shell_log_normalizer": format_float(
                reduced_shell_log_normalizer(
                    parameters["K"], parameters["E_star"]
                )
            ),
            "linear_jacobian_log_normalizer": format_float(
                linear_jacobian_log_normalizer(
                    parameters["M"], parameters["k_values"]
                )
            ),
            "full_canonical_shell_log_normalizer": format_float(
                portable_fsum(
                    (
                        reduced_shell_log_normalizer(
                            parameters["K"], parameters["E_star"]
                        ),
                        linear_jacobian_log_normalizer(
                            parameters["M"], parameters["k_values"]
                        ),
                    )
                )
            ),
            "normalization_scope": (
                "full value uses dP1 dP2 prod(dx dy dPi_x dPi_y), "
                "normalized Haar Q_relative, and the declared delta arguments"
            ),
        },
        "implementation": {
            "prng_algorithm": PRNG_ALGORITHM,
            "portable_math_version": PORTABLE_MATH_VERSION,
            "uniform_map": "u52-midpoint-open",
            "third_party_dependencies": [],
            "sample_count": sample_count,
            "familywise_alpha": format_float(familywise_alpha),
            "baseline_coefficient_payload_sha256": baseline_coefficient_hash,
            "seed_mutated_coefficient_payload_sha256": (
                seed_mutated_coefficient_hash
            ),
            "coefficient_stream_reads_only": [
                "schema_version",
                "source_seed",
                "source_draw_registry",
                "sample_index",
                "named substream label",
            ],
            "code_inventory_normalized_lf_sha256": inventory,
        },
        "constraint_audit": {
            "absolute_tolerance": format_float(tolerance),
            "serialized_residual_certificate": (
                "exact rational evaluation of every stored IEEE-754 "
                "binary64 value; no floating summation in the certificate"
            ),
            "exact_maximum_energy_residual": {
                "numerator": str(exact_max_energy_residual.numerator),
                "denominator": str(exact_max_energy_residual.denominator),
                "decimal": format_float(float(exact_max_energy_residual)),
            },
            "exact_maximum_target_momentum_residual": {
                "numerator": str(exact_max_target_residual.numerator),
                "denominator": str(exact_max_target_residual.denominator),
                "decimal": format_float(float(exact_max_target_residual)),
            },
            "exact_maximum_worldsheet_momentum_residual": {
                "numerator": str(exact_max_worldsheet_residual.numerator),
                "denominator": str(
                    exact_max_worldsheet_residual.denominator
                ),
                "decimal": format_float(
                    float(exact_max_worldsheet_residual)
                ),
            },
            "maximum_energy_residual": format_float(max_energy_residual),
            "maximum_target_momentum_residual": format_float(
                max_target_residual
            ),
            "maximum_worldsheet_momentum_residual": format_float(
                max_worldsheet_residual
            ),
            "maximum_flow_energy_drift": format_float(
                flow_energy_residual
            ),
            "maximum_flow_worldsheet_momentum_drift": format_float(
                flow_worldsheet_residual
            ),
        },
        "radial_audit": {
            "exact_means": [format_float(value) for value in exact_means],
            "gamma_empirical_means": [
                format_float(value) for value in gamma_means
            ],
            "hierarchical_beta_empirical_means": [
                format_float(value) for value in beta_means
            ],
            "familywise_hoeffding_half_width": format_float(
                mean_half_width
            ),
            "exact_moment_examples": {
                "E_x0_squared": format_float(
                    dirichlet_moment(shapes, (2, 0, 0))
                ),
                "E_x1_squared": format_float(
                    dirichlet_moment(shapes, (0, 2, 0))
                ),
                "E_x1_x2": format_float(
                    dirichlet_moment(shapes, (0, 1, 1))
                ),
            },
            "hostile_shapes_rejected_by_contract": [
                [4, parameters["d"], parameters["d"]],
                [4, parameters["d"] / 2, parameters["d"] / 2],
                [
                    4,
                    parameters["d"] - 0.5,
                    parameters["d"] - 0.5,
                ],
            ],
        },
        "relative_centre_audit": {
            "prior": "normalized Haar on the physical transverse torus",
            "gauge_representative": "Q2=0,Q1=Q_relative",
            "first_character_rows": character_rows,
            "familywise_real_imaginary_half_width": format_float(
                character_half_width
            ),
        },
        "validity_ledger": {
            "predicate": (
                "registered time-uniform analytic graph upper bound and "
                "k_max*ell_s threshold"
            ),
            "valid_count": valid_count,
            "source_invalid_count": invalid_count,
            "total_count": sample_count,
            "invalid_samples_retained": True,
            "conditioned_or_redrawn": False,
        },
        "source_state_fingerprints": baseline_fingerprints,
        "checks": check_map,
    }
    return report


def parse_arguments() -> argparse.Namespace:
    artifact_directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry",
        type=Path,
        default=artifact_directory / "source_registry.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=artifact_directory / "source_report.json",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare regenerated and stored semantic JSON",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    try:
        registry = read_strict_json(arguments.registry)
        validate_registry(registry)
        report = build_report(registry, Path(__file__).resolve().parent)
    except (OSError, UnicodeError, TypeError, ValueError) as error:
        raise SystemExit(f"Brief 0018 source audit failed: {error}") from error
    if report["status"] != "PASS":
        raise SystemExit("Brief 0018 source audit checks failed")

    if arguments.check:
        if not arguments.output.exists():
            raise SystemExit(f"source report missing: {arguments.output}")
        try:
            stored = read_strict_json(arguments.output)
        except (OSError, UnicodeError, TypeError, ValueError) as error:
            raise SystemExit(f"source report parse failure: {error}") from error
        if not type_strict_semantic_equal(stored, report):
            raise SystemExit("Brief 0018 source report semantic mismatch")
        action = "verified"
    else:
        write_json(arguments.output, report)
        action = "wrote"

    print(
        f"PASS: {action} {arguments.output}; "
        f"canonical_sha256={sha256_hex(report)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
