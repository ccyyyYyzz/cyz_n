#!/usr/bin/env python3
"""Exact certificate primitives for the first Brief 0019 solver foundation.

This module deliberately implements only the proof-container layer needed
before the physical world-sheet functions are connected:

* canonical dyadic scalars, endpoint-aware intervals and boxes;
* strict, type-preserving JSON and semantic hashes;
* exact replay of a gap-free split forest, one root per torus image;
* complete rectangular-lattice image enumeration for an exact fixture; and
* replayed one-dimensional range and Krawczyk witnesses.

It does not implement the finite-K trigonometric jets, event ordering,
hysteresis, recurrence, or population law.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from fractions import Fraction
from functools import total_ordering
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


BUNDLE_SCHEMA = "cyz-brief-0019-certified-solver-foundation-v2"
REPORT_SCHEMA = "cyz-brief-0019-certified-solver-foundation-report-v2"
FUNCTION_REGISTRY_SCHEMA = "cyz-brief-0019-exact-affine-registry-v1"
PROBLEM_REGISTRY_SCHEMA = (
    "cyz-brief-0019-foundation-problem-registry-v1"
)
PROBLEM_ID = "brief-0019-foundation-affine-cover"
PROBLEM_REGISTRY_CANONICAL_SHA256 = (
    "ac2e14bef595c1e152f32bddfcdea7b5ba295fd0c80e62e19e843cc34a01ce66"
)

ARTIFACT_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = ARTIFACT_DIR.parent.parent
FIXTURE_PATH = ARTIFACT_DIR / "certified_solver_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "certified_solver_report.json"
PROBLEM_REGISTRY_PATH = ARTIFACT_DIR / "foundation_problem_registry.json"

FOUNDATION_INVENTORY = (
    "artifacts/0019/certified_solver_core.py",
    "artifacts/0019/test_certified_solver_core.py",
    "artifacts/0019/certificate_replayer.py",
    "artifacts/0019/test_certificate_replayer.py",
    "artifacts/0019/foundation_problem_registry.json",
    "artifacts/0019/README.md",
    "README.md",
)

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")


class CertificateError(ValueError):
    """A certificate failed at a named semantic replay gate."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise CertificateError(gate, message)


def _require_exact_keys(
    value: Any,
    expected: set[str],
    path: str,
    gate: str = "schema",
) -> dict[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        fail(gate, f"{path} keys differ; missing={missing}, extra={extra}")
    return value


def _require_string(value: Any, path: str, gate: str = "schema") -> str:
    if type(value) is not str or not value:
        fail(gate, f"{path} must be a nonempty string")
    return value


def _require_int(value: Any, path: str, gate: str = "schema") -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer, not {type(value).__name__}")
    return value


def _require_bool(value: Any, path: str, gate: str = "schema") -> bool:
    if type(value) is not bool:
        fail(gate, f"{path} must be a Boolean")
    return value


def _require_list(value: Any, path: str, gate: str = "schema") -> list[Any]:
    if type(value) is not list:
        fail(gate, f"{path} must be an array")
    return value


def _require_sha256(value: Any, path: str, gate: str = "hash") -> str:
    text = _require_string(value, path, gate)
    if HEX_SHA256.fullmatch(text) is None:
        fail(gate, f"{path} is not a lowercase SHA-256 digest")
    return text


def reject_duplicate_object_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def reject_json_float(token: str) -> None:
    fail(
        "strict_json",
        f"JSON floating token {token!r} is forbidden; serialize a dyadic",
    )


def assert_strict_json_tree(value: Any, path: str = "$") -> None:
    """Accept only the exact JSON types used by the foundation grammar."""

    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        fail("strict_json", f"{path} contains an ordinary float")
    if type(value) is list:
        for index, item in enumerate(value):
            assert_strict_json_tree(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} contains a non-string key")
            assert_strict_json_tree(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains non-JSON type {type(value).__name__}")


def strict_json_loads(text: str) -> Any:
    value = json.loads(
        text,
        object_pairs_hook=reject_duplicate_object_pairs,
        parse_constant=reject_nonfinite_constant,
        parse_float=reject_json_float,
    )
    assert_strict_json_tree(value)
    return value


def strict_json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return strict_json_loads(handle.read())


def canonical_bytes(value: Any) -> bytes:
    assert_strict_json_tree(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def pretty_json(value: Any) -> str:
    assert_strict_json_tree(value)
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
    text = path.read_text(encoding="utf-8")
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_committed_problem_registry(
    path: Path = PROBLEM_REGISTRY_PATH,
) -> dict[str, Any]:
    """Load the external problem only if it matches the code-fixed commitment."""

    registry = strict_json_load(path)
    digest = canonical_sha256(registry)
    if digest != PROBLEM_REGISTRY_CANONICAL_SHA256:
        fail(
            "problem_commitment",
            "external problem registry does not match the code-fixed SHA-256",
        )
    root = _require_exact_keys(
        registry,
        {
            "schema_version",
            "problem_id",
            "arithmetic",
            "function_registry",
            "image_problem",
            "parameter_domain",
        },
        "$.problem_registry",
        "problem_commitment",
    )
    if root["schema_version"] != PROBLEM_REGISTRY_SCHEMA:
        fail("problem_commitment", "unknown problem registry schema")
    if root["problem_id"] != PROBLEM_ID:
        fail("problem_commitment", "unexpected committed problem ID")
    return root


def problem_commitment_json() -> dict[str, str]:
    return {
        "problem_id": PROBLEM_ID,
        "registry_schema": PROBLEM_REGISTRY_SCHEMA,
        "registry_canonical_sha256": PROBLEM_REGISTRY_CANONICAL_SHA256,
    }


@total_ordering
@dataclass(frozen=True)
class Dyadic:
    """Canonical integer times a non-positive power of two."""

    numerator: int
    exponent: int

    def __post_init__(self) -> None:
        if type(self.numerator) is not int:
            fail("dyadic", "numerator must be an integer")
        if type(self.exponent) is not int or self.exponent < 0:
            fail("dyadic", "exponent must be a nonnegative integer")
        if self.numerator == 0 and self.exponent != 0:
            fail("dyadic", "zero must be serialized with exponent zero")
        if (
            self.numerator != 0
            and self.exponent > 0
            and self.numerator % 2 == 0
        ):
            fail("dyadic", "dyadic representation is not reduced")

    @classmethod
    def of(cls, numerator: int, exponent: int = 0) -> "Dyadic":
        if type(numerator) is not int or type(exponent) is not int:
            fail("dyadic", "dyadic constructor requires integer arguments")
        if exponent < 0:
            fail("dyadic", "negative exponent is forbidden")
        if numerator == 0:
            return cls(0, 0)
        while exponent > 0 and numerator % 2 == 0:
            numerator //= 2
            exponent -= 1
        return cls(numerator, exponent)

    @classmethod
    def from_fraction(cls, value: Fraction) -> "Dyadic":
        if type(value) is not Fraction:
            value = Fraction(value)
        denominator = value.denominator
        if denominator <= 0 or denominator & (denominator - 1):
            fail("dyadic", f"{value} is not a dyadic rational")
        return cls.of(value.numerator, denominator.bit_length() - 1)

    @classmethod
    def from_json(cls, value: Any, path: str = "$") -> "Dyadic":
        obj = _require_exact_keys(
            value, {"numerator", "exponent"}, path, "dyadic"
        )
        return cls(
            _require_int(obj["numerator"], f"{path}.numerator", "dyadic"),
            _require_int(obj["exponent"], f"{path}.exponent", "dyadic"),
        )

    def to_fraction(self) -> Fraction:
        return Fraction(self.numerator, 1 << self.exponent)

    def to_json(self) -> dict[str, int]:
        return {"numerator": self.numerator, "exponent": self.exponent}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dyadic):
            return NotImplemented
        return (
            self.numerator == other.numerator
            and self.exponent == other.exponent
        )

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Dyadic):
            return NotImplemented
        return self.to_fraction() < other.to_fraction()

    def __neg__(self) -> "Dyadic":
        return Dyadic.of(-self.numerator, self.exponent)

    def __add__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.to_fraction() + other.to_fraction())

    def __sub__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.to_fraction() - other.to_fraction())

    def __mul__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.to_fraction() * other.to_fraction())

    def __truediv__(self, other: "Dyadic") -> "Dyadic":
        if other.numerator == 0:
            fail("dyadic", "division by zero")
        return Dyadic.from_fraction(self.to_fraction() / other.to_fraction())

    def midpoint(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(
            (self.to_fraction() + other.to_fraction()) / 2
        )


ZERO = Dyadic.of(0)
ONE = Dyadic.of(1)
TWO = Dyadic.of(2)


@dataclass(frozen=True)
class DyadicInterval:
    lower: Dyadic
    upper: Dyadic
    lower_closed: bool = True
    upper_closed: bool = True

    def __post_init__(self) -> None:
        if type(self.lower_closed) is not bool or type(self.upper_closed) is not bool:
            fail("interval", "endpoint-closure flags must be Boolean")
        if self.upper < self.lower:
            fail("interval", "lower endpoint exceeds upper endpoint")
        if self.lower == self.upper and not (
            self.lower_closed and self.upper_closed
        ):
            fail("interval", "a degenerate interval must contain its point")

    @classmethod
    def closed(cls, lower: Dyadic, upper: Dyadic) -> "DyadicInterval":
        return cls(lower, upper, True, True)

    @classmethod
    def from_json(cls, value: Any, path: str = "$") -> "DyadicInterval":
        obj = _require_exact_keys(
            value,
            {"lower", "upper", "lower_closed", "upper_closed"},
            path,
            "interval",
        )
        return cls(
            Dyadic.from_json(obj["lower"], f"{path}.lower"),
            Dyadic.from_json(obj["upper"], f"{path}.upper"),
            _require_bool(
                obj["lower_closed"], f"{path}.lower_closed", "interval"
            ),
            _require_bool(
                obj["upper_closed"], f"{path}.upper_closed", "interval"
            ),
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "lower": self.lower.to_json(),
            "upper": self.upper.to_json(),
            "lower_closed": self.lower_closed,
            "upper_closed": self.upper_closed,
        }

    def closed_hull(self) -> "DyadicInterval":
        return DyadicInterval.closed(self.lower, self.upper)

    def midpoint(self) -> Dyadic:
        return self.lower.midpoint(self.upper)

    def split(
        self, point: Dyadic
    ) -> tuple["DyadicInterval", "DyadicInterval"]:
        if not self.lower < point or not point < self.upper:
            fail("cover_partition", "split point must be strictly interior")
        left = DyadicInterval(
            self.lower, point, self.lower_closed, False
        )
        right = DyadicInterval(
            point, self.upper, True, self.upper_closed
        )
        return left, right

    def strictly_contains(self, other: "DyadicInterval") -> bool:
        return self.lower < other.lower and other.upper < self.upper


@dataclass(frozen=True)
class DyadicBox:
    axes: tuple[str, ...]
    intervals: tuple[DyadicInterval, ...]

    def __post_init__(self) -> None:
        if not self.axes or len(self.axes) != len(self.intervals):
            fail("box", "box must have equally many axes and intervals")
        if len(set(self.axes)) != len(self.axes):
            fail("box", "box axis names must be unique")
        if any(type(axis) is not str or not axis for axis in self.axes):
            fail("box", "box axes must be nonempty strings")

    @classmethod
    def from_json(cls, value: Any, path: str = "$") -> "DyadicBox":
        obj = _require_exact_keys(
            value, {"axes", "intervals"}, path, "box"
        )
        raw_axes = _require_list(obj["axes"], f"{path}.axes", "box")
        raw_intervals = _require_list(
            obj["intervals"], f"{path}.intervals", "box"
        )
        axes = tuple(
            _require_string(axis, f"{path}.axes[{index}]", "box")
            for index, axis in enumerate(raw_axes)
        )
        intervals = tuple(
            DyadicInterval.from_json(interval, f"{path}.intervals[{index}]")
            for index, interval in enumerate(raw_intervals)
        )
        return cls(axes, intervals)

    def to_json(self) -> dict[str, Any]:
        return {
            "axes": list(self.axes),
            "intervals": [interval.to_json() for interval in self.intervals],
        }

    def split(
        self, axis: str, point: Dyadic
    ) -> tuple["DyadicBox", "DyadicBox"]:
        if axis not in self.axes:
            fail("cover_partition", f"unknown split axis {axis!r}")
        index = self.axes.index(axis)
        left_interval, right_interval = self.intervals[index].split(point)
        left = list(self.intervals)
        right = list(self.intervals)
        left[index] = left_interval
        right[index] = right_interval
        return (
            DyadicBox(self.axes, tuple(left)),
            DyadicBox(self.axes, tuple(right)),
        )


def _closed_interval_add(
    left: DyadicInterval, right: DyadicInterval
) -> DyadicInterval:
    return DyadicInterval.closed(
        left.lower + right.lower, left.upper + right.upper
    )


def _closed_interval_sub(
    left: DyadicInterval, right: DyadicInterval
) -> DyadicInterval:
    return DyadicInterval.closed(
        left.lower - right.upper, left.upper - right.lower
    )


def _closed_interval_mul(
    left: DyadicInterval, right: DyadicInterval
) -> DyadicInterval:
    products = (
        left.lower * right.lower,
        left.lower * right.upper,
        left.upper * right.lower,
        left.upper * right.upper,
    )
    return DyadicInterval.closed(min(products), max(products))


def _closed_interval_scale(
    interval: DyadicInterval, scalar: Dyadic
) -> DyadicInterval:
    return _closed_interval_mul(
        interval.closed_hull(), DyadicInterval.closed(scalar, scalar)
    )


@dataclass(frozen=True)
class AffineFunction:
    function_id: str
    slope: Dyadic
    intercept: Dyadic

    def point_value(self, point: Dyadic) -> Dyadic:
        return self.slope * point + self.intercept

    def range_on(self, interval: DyadicInterval) -> DyadicInterval:
        first = self.point_value(interval.lower)
        second = self.point_value(interval.upper)
        return DyadicInterval.closed(min(first, second), max(first, second))

    def derivative_interval(self) -> DyadicInterval:
        return DyadicInterval.closed(self.slope, self.slope)


def _parse_function_registry(value: Any) -> dict[str, AffineFunction]:
    registry = _require_exact_keys(
        value, {"schema_version", "functions"}, "$.function_registry"
    )
    if registry["schema_version"] != FUNCTION_REGISTRY_SCHEMA:
        fail("function_registry", "unknown function registry schema")
    entries = _require_list(
        registry["functions"], "$.function_registry.functions"
    )
    if not entries:
        fail("function_registry", "function registry is empty")
    result: dict[str, AffineFunction] = {}
    for index, raw in enumerate(entries):
        path = f"$.function_registry.functions[{index}]"
        entry = _require_exact_keys(
            raw,
            {"function_id", "kind", "slope", "intercept"},
            path,
            "function_registry",
        )
        function_id = _require_string(
            entry["function_id"], f"{path}.function_id", "function_registry"
        )
        if function_id in result:
            fail(
                "function_registry",
                f"duplicate function ID {function_id!r}",
            )
        if entry["kind"] != "affine_1d":
            fail("function_registry", f"{path}.kind is unsupported")
        result[function_id] = AffineFunction(
            function_id,
            Dyadic.from_json(entry["slope"], f"{path}.slope"),
            Dyadic.from_json(entry["intercept"], f"{path}.intercept"),
        )
    return result


def _one_dimensional_interval(box: DyadicBox, gate: str) -> DyadicInterval:
    if box.axes != ("u",):
        fail(gate, "foundation witnesses require the one-dimensional u box")
    return box.intervals[0]


def build_excluded_range_witness(
    function: AffineFunction, box: DyadicBox
) -> dict[str, Any]:
    interval = _one_dimensional_interval(box, "excluded_range_witness")
    range_interval = function.range_on(interval)
    if range_interval.lower > ZERO:
        separation = "strictly_positive"
    elif range_interval.upper < ZERO:
        separation = "strictly_negative"
    else:
        fail(
            "excluded_range_witness",
            "the exact affine range does not exclude zero",
        )
    return {
        "witness_type": "exact_affine_component_range",
        "function_id": function.function_id,
        "range": range_interval.to_json(),
        "zero_separation": separation,
    }


def _krawczyk_data(
    function: AffineFunction, box: DyadicBox
) -> dict[str, Any]:
    domain = _one_dimensional_interval(box, "unique_root_witness")
    midpoint = domain.midpoint()
    if function.slope == ZERO:
        fail(
            "unique_root_witness",
            "zero derivative has no exact scalar preconditioner",
        )
    preconditioner = ONE / function.slope
    point_value = function.point_value(midpoint)
    derivative = function.derivative_interval()
    center = midpoint - preconditioner * point_value
    identity_minus_cd = _closed_interval_sub(
        DyadicInterval.closed(ONE, ONE),
        _closed_interval_scale(derivative, preconditioner),
    )
    centered_box = DyadicInterval.closed(
        domain.lower - midpoint, domain.upper - midpoint
    )
    correction = _closed_interval_mul(identity_minus_cd, centered_box)
    krawczyk_image = _closed_interval_add(
        DyadicInterval.closed(center, center), correction
    )
    lower_margin = krawczyk_image.lower - domain.lower
    upper_margin = domain.upper - krawczyk_image.upper
    if not domain.closed_hull().strictly_contains(krawczyk_image):
        fail(
            "unique_root_witness",
            "recomputed Krawczyk image is not strictly inside the box",
        )
    if not lower_margin > ZERO or not upper_margin > ZERO:
        fail(
            "unique_root_witness",
            "strict inclusion margins are not positive",
        )
    return {
        "witness_type": "exact_interval_krawczyk_1d",
        "arithmetic": "exact_dyadic_rational",
        "function_id": function.function_id,
        "midpoint": midpoint.to_json(),
        "preconditioner": preconditioner.to_json(),
        "point_value": point_value.to_json(),
        "derivative_enclosure": derivative.to_json(),
        "krawczyk_image": krawczyk_image.to_json(),
        "inclusion_margins": {
            "lower": lower_margin.to_json(),
            "upper": upper_margin.to_json(),
        },
    }


def build_unique_root_witness(
    function: AffineFunction, box: DyadicBox
) -> dict[str, Any]:
    return _krawczyk_data(function, box)


def _verify_excluded_range_witness(
    raw: Any,
    box: DyadicBox,
    functions: Mapping[str, AffineFunction],
) -> None:
    witness = _require_exact_keys(
        raw,
        {"witness_type", "function_id", "range", "zero_separation"},
        "$.leaf.witness",
        "excluded_range_witness",
    )
    if witness["witness_type"] != "exact_affine_component_range":
        fail("excluded_range_witness", "unsupported witness type")
    function_id = _require_string(
        witness["function_id"],
        "$.leaf.witness.function_id",
        "excluded_range_witness",
    )
    if function_id not in functions:
        fail(
            "excluded_range_witness",
            f"unknown function ID {function_id!r}",
        )
    expected = build_excluded_range_witness(functions[function_id], box)
    if not type_strict_equal(witness, expected):
        fail(
            "excluded_range_witness",
            "stored range or zero separation differs from exact replay",
        )


def _verify_unique_root_witness(
    raw: Any,
    box: DyadicBox,
    functions: Mapping[str, AffineFunction],
) -> None:
    witness = _require_exact_keys(
        raw,
        {
            "witness_type",
            "arithmetic",
            "function_id",
            "midpoint",
            "preconditioner",
            "point_value",
            "derivative_enclosure",
            "krawczyk_image",
            "inclusion_margins",
        },
        "$.leaf.witness",
        "unique_root_witness",
    )
    if witness["witness_type"] != "exact_interval_krawczyk_1d":
        fail("unique_root_witness", "unsupported witness type")
    if witness["arithmetic"] != "exact_dyadic_rational":
        fail("unique_root_witness", "ordinary floating arithmetic is forbidden")
    function_id = _require_string(
        witness["function_id"],
        "$.leaf.witness.function_id",
        "unique_root_witness",
    )
    if function_id not in functions:
        fail("unique_root_witness", f"unknown function ID {function_id!r}")
    expected = _krawczyk_data(functions[function_id], box)
    if not type_strict_equal(witness, expected):
        fail(
            "unique_root_witness",
            "stored Krawczyk data differs from exact replay",
        )


def _verify_unresolved_witness(raw: Any) -> None:
    witness = _require_exact_keys(
        raw,
        {
            "witness_type",
            "reason",
            "operation_limit",
            "operations_used",
            "next_action",
        },
        "$.leaf.witness",
        "unresolved_witness",
    )
    if witness["witness_type"] != "deterministic_budget_stop":
        fail("unresolved_witness", "unsupported unresolved witness type")
    if witness["reason"] != "operation_budget_exhausted":
        fail("unresolved_witness", "unresolved reason is not the frozen reason")
    operation_limit = _require_int(
        witness["operation_limit"],
        "$.leaf.witness.operation_limit",
        "unresolved_witness",
    )
    operations_used = _require_int(
        witness["operations_used"],
        "$.leaf.witness.operations_used",
        "unresolved_witness",
    )
    if operation_limit <= 0 or operations_used != operation_limit:
        fail(
            "unresolved_witness",
            "deterministic exhaustion requires used == positive limit",
        )
    if witness["next_action"] != "bisect_box":
        fail("unresolved_witness", "unknown continuation action")


def floor_fraction(value: Fraction) -> int:
    return value.numerator // value.denominator


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def image_id(vector: Sequence[int]) -> str:
    return "n[" + ",".join(str(component) for component in vector) + "]"


def _parse_dyadic_list(
    raw: Any, path: str, expected_length: int, gate: str
) -> list[Dyadic]:
    values = _require_list(raw, path, gate)
    if len(values) != expected_length:
        fail(gate, f"{path} has length {len(values)}, expected {expected_length}")
    return [
        Dyadic.from_json(value, f"{path}[{index}]")
        for index, value in enumerate(values)
    ]


def _enumerate_expected_images(
    periods: Sequence[Dyadic],
    inverse_diagonal: Sequence[Dyadic],
    square_roots: Sequence[Dyadic],
    r_out: Dyadic,
    separation_bounds: Sequence[DyadicInterval],
) -> list[tuple[int, ...]]:
    coordinate_ranges: list[range] = []
    for axis, (
        period,
        inverse_entry,
        square_root,
        separation,
    ) in enumerate(
        zip(
            periods,
            inverse_diagonal,
            square_roots,
            separation_bounds,
        )
    ):
        if period <= ZERO:
            fail("image_enumeration", f"period {axis} is not positive")
        if inverse_entry <= ZERO or square_root < ZERO:
            fail("image_enumeration", f"metric inverse witness {axis} is invalid")
        if square_root * square_root != inverse_entry:
            fail(
                "image_enumeration",
                f"sqrt(G^-1) witness {axis} does not square exactly",
            )
        coordinate_radius = r_out * square_root
        lower_ratio = (
            separation.lower.to_fraction()
            - coordinate_radius.to_fraction()
        ) / period.to_fraction()
        upper_ratio = (
            separation.upper.to_fraction()
            + coordinate_radius.to_fraction()
        ) / period.to_fraction()
        lower_integer = ceil_fraction(lower_ratio)
        upper_integer = floor_fraction(upper_ratio)
        if lower_integer > upper_integer:
            coordinate_ranges.append(range(0))
        else:
            coordinate_ranges.append(range(lower_integer, upper_integer + 1))
    count = 1
    for coordinate_range in coordinate_ranges:
        count *= len(coordinate_range)
    if count > 100_000:
        fail(
            "image_enumeration",
            "foundation image fixture exceeds deterministic enumeration budget",
        )
    return [tuple(vector) for vector in itertools.product(*coordinate_ranges)]


def validate_image_enumeration(
    value: Any,
    expected_problem: Mapping[str, Any] | None = None,
) -> list[str]:
    image_data = _require_exact_keys(
        value,
        {
            "dimension",
            "periods",
            "metric_diagonal",
            "metric_inverse_diagonal",
            "sqrt_metric_inverse_diagonal",
            "r_out",
            "separation_bounds",
            "manifest",
        },
        "$.image_enumeration",
        "image_enumeration",
    )
    if expected_problem is None:
        expected_problem = load_committed_problem_registry()["image_problem"]
    source_payload = {
        key: image_data[key] for key in image_data if key != "manifest"
    }
    if not type_strict_equal(source_payload, expected_problem):
        fail(
            "image_enumeration",
            "bundle image inputs differ from the externally committed problem",
        )
    dimension = _require_int(
        image_data["dimension"],
        "$.image_enumeration.dimension",
        "image_enumeration",
    )
    if dimension <= 0:
        fail("image_enumeration", "image dimension must be positive")
    periods = _parse_dyadic_list(
        image_data["periods"],
        "$.image_enumeration.periods",
        dimension,
        "image_enumeration",
    )
    metric = _parse_dyadic_list(
        image_data["metric_diagonal"],
        "$.image_enumeration.metric_diagonal",
        dimension,
        "image_enumeration",
    )
    inverse = _parse_dyadic_list(
        image_data["metric_inverse_diagonal"],
        "$.image_enumeration.metric_inverse_diagonal",
        dimension,
        "image_enumeration",
    )
    square_roots = _parse_dyadic_list(
        image_data["sqrt_metric_inverse_diagonal"],
        "$.image_enumeration.sqrt_metric_inverse_diagonal",
        dimension,
        "image_enumeration",
    )
    for axis, (entry, inverse_entry) in enumerate(zip(metric, inverse)):
        if entry <= ZERO or entry * inverse_entry != ONE:
            fail(
                "image_enumeration",
                f"metric/inverse diagonal pair {axis} is not exact",
            )
    r_out = Dyadic.from_json(
        image_data["r_out"], "$.image_enumeration.r_out"
    )
    if r_out <= ZERO:
        fail("image_enumeration", "r_out must be positive")
    bounds_raw = _require_list(
        image_data["separation_bounds"],
        "$.image_enumeration.separation_bounds",
        "image_enumeration",
    )
    if len(bounds_raw) != dimension:
        fail("image_enumeration", "separation-bound dimension mismatch")
    bounds = [
        DyadicInterval.from_json(
            item, f"$.image_enumeration.separation_bounds[{index}]"
        )
        for index, item in enumerate(bounds_raw)
    ]
    expected_vectors = _enumerate_expected_images(
        periods, inverse, square_roots, r_out, bounds
    )
    expected_entries = [
        {"image_id": image_id(vector), "lattice_vector": list(vector)}
        for vector in expected_vectors
    ]
    manifest = _require_list(
        image_data["manifest"],
        "$.image_enumeration.manifest",
        "image_enumeration",
    )
    seen_ids: set[str] = set()
    seen_vectors: set[tuple[int, ...]] = set()
    parsed_entries: list[dict[str, Any]] = []
    for index, raw in enumerate(manifest):
        path = f"$.image_enumeration.manifest[{index}]"
        entry = _require_exact_keys(
            raw,
            {"image_id", "lattice_vector"},
            path,
            "image_enumeration",
        )
        identifier = _require_string(
            entry["image_id"], f"{path}.image_id", "image_enumeration"
        )
        vector_raw = _require_list(
            entry["lattice_vector"],
            f"{path}.lattice_vector",
            "image_enumeration",
        )
        if len(vector_raw) != dimension:
            fail("image_enumeration", f"{path} has the wrong dimension")
        vector = tuple(
            _require_int(
                component,
                f"{path}.lattice_vector[{component_index}]",
                "image_enumeration",
            )
            for component_index, component in enumerate(vector_raw)
        )
        if identifier in seen_ids:
            fail("image_manifest_ids", f"duplicate image ID {identifier!r}")
        if vector in seen_vectors:
            fail(
                "image_manifest_ids",
                f"duplicate lattice vector {vector!r}",
            )
        seen_ids.add(identifier)
        seen_vectors.add(vector)
        if identifier != image_id(vector):
            fail(
                "image_enumeration",
                f"{path}.image_id is not canonical for its vector",
            )
        parsed_entries.append(
            {"image_id": identifier, "lattice_vector": list(vector)}
        )
    if not type_strict_equal(parsed_entries, expected_entries):
        actual_vectors = [entry["lattice_vector"] for entry in parsed_entries]
        fail(
            "image_enumeration",
            "manifest is not the complete ordered exact enumeration; "
            f"expected={expected_vectors}, actual={actual_vectors}",
        )
    return [entry["image_id"] for entry in parsed_entries]


LEAF_KEYS = {
    "node_id",
    "node_type",
    "image_id",
    "box",
    "status",
    "witness",
    "node_hash",
}
SPLIT_KEYS = {
    "node_id",
    "node_type",
    "image_id",
    "box",
    "axis",
    "split_point",
    "left_child_id",
    "right_child_id",
    "child_hashes",
    "node_hash",
}


def _node_payload(node: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in node.items() if key != "node_hash"}


def _node_hash(node: Mapping[str, Any]) -> str:
    return canonical_sha256(_node_payload(node))


def _cover_payload(cover: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in cover.items() if key != "cover_hash"}


def _cover_hash(cover: Mapping[str, Any]) -> str:
    return canonical_sha256(_cover_payload(cover))


def refresh_declared_hashes(bundle: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute ordinary node/cover hashes without proving semantics."""

    refreshed = copy.deepcopy(bundle)
    cover = refreshed["initial_cover"]
    raw_nodes = cover["nodes"]
    nodes: dict[str, dict[str, Any]] = {}
    for raw in raw_nodes:
        identifier = raw["node_id"]
        if identifier in nodes:
            raise ValueError(f"cannot hash duplicate node ID {identifier!r}")
        nodes[identifier] = raw
    visiting: set[str] = set()
    completed: dict[str, str] = {}

    def visit(identifier: str) -> str:
        if identifier in completed:
            return completed[identifier]
        if identifier in visiting:
            raise ValueError("cannot hash a cyclic tree")
        if identifier not in nodes:
            raise ValueError(f"cannot hash missing node {identifier!r}")
        visiting.add(identifier)
        node = nodes[identifier]
        if node["node_type"] == "split":
            left_hash = visit(node["left_child_id"])
            right_hash = visit(node["right_child_id"])
            node["child_hashes"] = {
                "left": left_hash,
                "right": right_hash,
            }
        node["node_hash"] = _node_hash(node)
        visiting.remove(identifier)
        completed[identifier] = node["node_hash"]
        return node["node_hash"]

    root_hashes = []
    for root_id in cover["root_ids"]:
        root_hashes.append({"root_id": root_id, "node_hash": visit(root_id)})
    cover["root_hashes"] = root_hashes
    cover["cover_hash"] = _cover_hash(cover)
    return refreshed


def _verify_leaf(
    node: Mapping[str, Any],
    box: DyadicBox,
    functions: Mapping[str, AffineFunction],
) -> str:
    status = node["status"]
    if status == "excluded_range":
        _verify_excluded_range_witness(node["witness"], box, functions)
    elif status == "unique_root":
        _verify_unique_root_witness(node["witness"], box, functions)
    elif status == "unresolved":
        _verify_unresolved_witness(node["witness"])
    else:
        fail(
            "leaf_status",
            f"foundation leaf status {status!r} is not implemented",
        )
    return status


def validate_initial_cover(
    value: Any,
    manifest_ids: Sequence[str],
    functions: Mapping[str, AffineFunction],
    committed_parameter_domain: Any,
) -> dict[str, Any]:
    cover = _require_exact_keys(
        value,
        {
            "parameter_domain",
            "root_ids",
            "root_hashes",
            "nodes",
            "cover_hash",
        },
        "$.initial_cover",
        "cover_schema",
    )
    parameter_domain = DyadicBox.from_json(
        cover["parameter_domain"], "$.initial_cover.parameter_domain"
    )
    if not type_strict_equal(
        cover["parameter_domain"], committed_parameter_domain
    ):
        fail(
            "problem_commitment",
            "bundle parameter domain differs from the external registry",
        )
    root_ids_raw = _require_list(
        cover["root_ids"], "$.initial_cover.root_ids", "cover_topology"
    )
    root_ids = [
        _require_string(
            identifier,
            f"$.initial_cover.root_ids[{index}]",
            "cover_topology",
        )
        for index, identifier in enumerate(root_ids_raw)
    ]
    if not root_ids:
        fail("cover_topology", "complete cover cannot be empty")
    if len(set(root_ids)) != len(root_ids):
        fail("cover_ids", "root IDs are duplicated")
    raw_nodes = _require_list(
        cover["nodes"], "$.initial_cover.nodes", "cover_topology"
    )
    if not raw_nodes:
        fail("cover_topology", "complete cover contains no nodes")
    nodes: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_nodes):
        path = f"$.initial_cover.nodes[{index}]"
        if type(raw) is not dict:
            fail("cover_schema", f"{path} must be an object")
        node_type = _require_string(
            raw.get("node_type"), f"{path}.node_type", "cover_schema"
        )
        expected_keys = LEAF_KEYS if node_type == "leaf" else SPLIT_KEYS
        if node_type not in {"leaf", "split"}:
            fail("cover_schema", f"{path}.node_type is unknown")
        node = _require_exact_keys(
            raw, expected_keys, path, "cover_schema"
        )
        identifier = _require_string(
            node["node_id"], f"{path}.node_id", "cover_ids"
        )
        if identifier in nodes:
            fail("cover_ids", f"duplicate node ID {identifier!r}")
        _require_string(node["image_id"], f"{path}.image_id", "cover_schema")
        _require_sha256(node["node_hash"], f"{path}.node_hash", "node_hash")
        nodes[identifier] = node
    for root_id in root_ids:
        if root_id not in nodes:
            fail("cover_topology", f"root node {root_id!r} is missing")
    if len(root_ids) != len(manifest_ids):
        fail(
            "cover_image_binding",
            "initial cover must have exactly one root per enumerated image",
        )
    root_images = [nodes[root_id]["image_id"] for root_id in root_ids]
    if list(root_images) != list(manifest_ids):
        fail(
            "cover_image_binding",
            "ordered cover roots do not reference every manifest image once",
        )

    parent_count = {identifier: 0 for identifier in nodes}
    for identifier, node in nodes.items():
        if node["node_type"] != "split":
            continue
        left_id = _require_string(
            node["left_child_id"],
            f"node {identifier}.left_child_id",
            "cover_topology",
        )
        right_id = _require_string(
            node["right_child_id"],
            f"node {identifier}.right_child_id",
            "cover_topology",
        )
        if left_id == right_id:
            fail("cover_topology", f"node {identifier!r} repeats one child")
        for child_id in (left_id, right_id):
            if child_id not in nodes:
                fail(
                    "cover_topology",
                    f"node {identifier!r} references missing child {child_id!r}",
                )
            parent_count[child_id] += 1
            if parent_count[child_id] > 1:
                fail(
                    "cover_topology",
                    f"node {child_id!r} has multiple parents",
                )
    root_set = set(root_ids)
    for identifier, count in parent_count.items():
        expected_count = 0 if identifier in root_set else 1
        if count != expected_count:
            fail(
                "cover_topology",
                f"node {identifier!r} has parent count {count}, "
                f"expected {expected_count}",
            )

    visiting: set[str] = set()
    visited: set[str] = set()
    derived_hashes: dict[str, str] = {}
    status_counts = {
        "excluded_range": 0,
        "unique_root": 0,
        "unresolved": 0,
    }

    def visit(
        identifier: str,
        expected_box: DyadicBox,
        expected_image: str,
    ) -> str:
        if identifier in visiting:
            fail("cover_topology", f"cycle reaches node {identifier!r}")
        if identifier in visited:
            fail(
                "cover_topology",
                f"node {identifier!r} is reached more than once",
            )
        visiting.add(identifier)
        node = nodes[identifier]
        if node["image_id"] != expected_image:
            fail(
                "cover_image_binding",
                f"node {identifier!r} changes image branch",
            )
        actual_box = DyadicBox.from_json(
            node["box"], f"node {identifier}.box"
        )
        if actual_box != expected_box:
            fail(
                "cover_partition",
                f"node {identifier!r} box is not the exact replayed child",
            )
        if node["node_type"] == "leaf":
            status = _verify_leaf(node, actual_box, functions)
            status_counts[status] += 1
        else:
            axis = _require_string(
                node["axis"], f"node {identifier}.axis", "cover_partition"
            )
            split_point = Dyadic.from_json(
                node["split_point"], f"node {identifier}.split_point"
            )
            left_box, right_box = actual_box.split(axis, split_point)
            left_hash = visit(
                node["left_child_id"], left_box, expected_image
            )
            right_hash = visit(
                node["right_child_id"], right_box, expected_image
            )
            child_hashes = _require_exact_keys(
                node["child_hashes"],
                {"left", "right"},
                f"node {identifier}.child_hashes",
                "node_hash",
            )
            _require_sha256(
                child_hashes["left"],
                f"node {identifier}.child_hashes.left",
                "node_hash",
            )
            _require_sha256(
                child_hashes["right"],
                f"node {identifier}.child_hashes.right",
                "node_hash",
            )
            expected_child_hashes = {
                "left": left_hash,
                "right": right_hash,
            }
            if not type_strict_equal(child_hashes, expected_child_hashes):
                fail(
                    "node_hash",
                    f"node {identifier!r} child hashes do not replay",
                )
        derived_hash = _node_hash(node)
        if node["node_hash"] != derived_hash:
            fail("node_hash", f"node {identifier!r} hash does not replay")
        visiting.remove(identifier)
        visited.add(identifier)
        derived_hashes[identifier] = derived_hash
        return derived_hash

    for root_id, expected_image in zip(root_ids, manifest_ids):
        visit(root_id, parameter_domain, expected_image)
    if visited != set(nodes):
        unreachable = sorted(set(nodes) - visited)
        fail("cover_topology", f"unreachable nodes remain: {unreachable}")

    root_hashes_raw = _require_list(
        cover["root_hashes"],
        "$.initial_cover.root_hashes",
        "root_hash",
    )
    expected_root_hashes = [
        {"root_id": root_id, "node_hash": derived_hashes[root_id]}
        for root_id in root_ids
    ]
    for index, raw in enumerate(root_hashes_raw):
        entry = _require_exact_keys(
            raw,
            {"root_id", "node_hash"},
            f"$.initial_cover.root_hashes[{index}]",
            "root_hash",
        )
        _require_string(
            entry["root_id"],
            f"$.initial_cover.root_hashes[{index}].root_id",
            "root_hash",
        )
        _require_sha256(
            entry["node_hash"],
            f"$.initial_cover.root_hashes[{index}].node_hash",
            "root_hash",
        )
    if not type_strict_equal(root_hashes_raw, expected_root_hashes):
        fail("root_hash", "declared root hashes do not replay")
    declared_cover_hash = _require_sha256(
        cover["cover_hash"], "$.initial_cover.cover_hash", "cover_hash"
    )
    derived_cover_hash = _cover_hash(cover)
    if declared_cover_hash != derived_cover_hash:
        fail("cover_hash", "initial-cover semantic hash does not replay")

    leaf_count = sum(status_counts.values())
    resolution = (
        "unresolved_present"
        if status_counts["unresolved"]
        else "all_leaves_certified"
    )
    return {
        "image_count": len(manifest_ids),
        "root_count": len(root_ids),
        "node_count": len(nodes),
        "leaf_count": leaf_count,
        "status_counts": status_counts,
        "coverage": "gap_free_exact_partition",
        "resolution": resolution,
    }


def replay_bundle(bundle: Any) -> dict[str, Any]:
    assert_strict_json_tree(bundle)
    root = _require_exact_keys(
        bundle,
        {
            "schema_version",
            "problem_commitment",
            "arithmetic",
            "function_registry",
            "image_enumeration",
            "initial_cover",
        },
        "$",
    )
    if root["schema_version"] != BUNDLE_SCHEMA:
        fail("schema", "unknown foundation bundle schema")
    committed = load_committed_problem_registry()
    commitment = _require_exact_keys(
        root["problem_commitment"],
        {
            "problem_id",
            "registry_schema",
            "registry_canonical_sha256",
        },
        "$.problem_commitment",
        "problem_commitment",
    )
    if not type_strict_equal(commitment, problem_commitment_json()):
        fail(
            "problem_commitment",
            "bundle does not name the code-fixed external problem commitment",
        )
    arithmetic = _require_exact_keys(
        root["arithmetic"],
        {"scalar", "interval", "partition_policy"},
        "$.arithmetic",
    )
    expected_arithmetic = committed["arithmetic"]
    if not type_strict_equal(arithmetic, expected_arithmetic):
        fail(
            "problem_commitment",
            "arithmetic conventions differ from the committed problem",
        )
    if not type_strict_equal(
        root["function_registry"], committed["function_registry"]
    ):
        fail(
            "problem_commitment",
            "bundle affine functions differ from the external registry",
        )
    functions = _parse_function_registry(root["function_registry"])
    manifest_ids = validate_image_enumeration(
        root["image_enumeration"], committed["image_problem"]
    )
    summary = validate_initial_cover(
        root["initial_cover"],
        manifest_ids,
        functions,
        committed["parameter_domain"],
    )
    summary["problem_registry_canonical_sha256"] = (
        PROBLEM_REGISTRY_CANONICAL_SHA256
    )
    summary["bundle_semantic_sha256"] = canonical_sha256(bundle)
    return summary


def _dyadic(numerator: int, exponent: int = 0) -> dict[str, int]:
    return Dyadic.of(numerator, exponent).to_json()


def _interval(
    lower: Dyadic,
    upper: Dyadic,
    lower_closed: bool = True,
    upper_closed: bool = True,
) -> DyadicInterval:
    return DyadicInterval(lower, upper, lower_closed, upper_closed)


def _leaf(
    node_id: str,
    branch_image_id: str,
    box: DyadicBox,
    status: str,
    witness: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": "leaf",
        "image_id": branch_image_id,
        "box": box.to_json(),
        "status": status,
        "witness": dict(witness),
        "node_hash": "0" * 64,
    }


def _split(
    node_id: str,
    branch_image_id: str,
    box: DyadicBox,
    axis: str,
    split_point: Dyadic,
    left_child_id: str,
    right_child_id: str,
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "node_type": "split",
        "image_id": branch_image_id,
        "box": box.to_json(),
        "axis": axis,
        "split_point": split_point.to_json(),
        "left_child_id": left_child_id,
        "right_child_id": right_child_id,
        "child_hashes": {"left": "0" * 64, "right": "0" * 64},
        "node_hash": "0" * 64,
    }


def build_foundation_fixture() -> dict[str, Any]:
    """Build the deterministic exact fixture used by generator and replay."""

    committed = load_committed_problem_registry()
    function_registry = copy.deepcopy(committed["function_registry"])
    functions = _parse_function_registry(function_registry)
    unique_function = functions["affine_unique_root"]
    guard_function = functions["affine_positive_guard"]

    image_problem = copy.deepcopy(committed["image_problem"])
    dimension = _require_int(
        image_problem["dimension"],
        "$.problem_registry.image_problem.dimension",
        "problem_commitment",
    )
    periods = _parse_dyadic_list(
        image_problem["periods"],
        "$.problem_registry.image_problem.periods",
        dimension,
        "problem_commitment",
    )
    inverse = _parse_dyadic_list(
        image_problem["metric_inverse_diagonal"],
        "$.problem_registry.image_problem.metric_inverse_diagonal",
        dimension,
        "problem_commitment",
    )
    square_roots = _parse_dyadic_list(
        image_problem["sqrt_metric_inverse_diagonal"],
        "$.problem_registry.image_problem.sqrt_metric_inverse_diagonal",
        dimension,
        "problem_commitment",
    )
    r_out = Dyadic.from_json(
        image_problem["r_out"], "$.problem_registry.image_problem.r_out"
    )
    separation_bounds = [
        DyadicInterval.from_json(
            raw,
            f"$.problem_registry.image_problem.separation_bounds[{index}]",
        )
        for index, raw in enumerate(image_problem["separation_bounds"])
    ]
    vectors = _enumerate_expected_images(
        periods, inverse, square_roots, r_out, separation_bounds
    )
    manifest = [
        {"image_id": image_id(vector), "lattice_vector": list(vector)}
        for vector in vectors
    ]
    image_enumeration = copy.deepcopy(image_problem)
    image_enumeration["manifest"] = manifest

    domain = DyadicBox.from_json(
        committed["parameter_domain"],
        "$.problem_registry.parameter_domain",
    )
    quarter = Dyadic.of(1, 2)
    three_quarters = Dyadic.of(3, 2)
    root_ids: list[str] = []
    nodes: list[dict[str, Any]] = []
    for vector in vectors:
        branch_image_id = image_id(vector)
        suffix = "-".join(str(component) for component in vector)
        root_id = f"root-{suffix}"
        root_ids.append(root_id)
        if vector == vectors[0]:
            left_box, right_box = domain.split("u", quarter)
            unique_box, unresolved_box = right_box.split(
                "u", three_quarters
            )
            excluded_id = f"leaf-{suffix}-excluded"
            split_right_id = f"split-{suffix}-right"
            unique_id = f"leaf-{suffix}-unique"
            unresolved_id = f"leaf-{suffix}-unresolved"
            nodes.extend(
                [
                    _split(
                        root_id,
                        branch_image_id,
                        domain,
                        "u",
                        quarter,
                        excluded_id,
                        split_right_id,
                    ),
                    _leaf(
                        excluded_id,
                        branch_image_id,
                        left_box,
                        "excluded_range",
                        build_excluded_range_witness(
                            unique_function, left_box
                        ),
                    ),
                    _split(
                        split_right_id,
                        branch_image_id,
                        right_box,
                        "u",
                        three_quarters,
                        unique_id,
                        unresolved_id,
                    ),
                    _leaf(
                        unique_id,
                        branch_image_id,
                        unique_box,
                        "unique_root",
                        build_unique_root_witness(
                            unique_function, unique_box
                        ),
                    ),
                    _leaf(
                        unresolved_id,
                        branch_image_id,
                        unresolved_box,
                        "unresolved",
                        {
                            "witness_type": "deterministic_budget_stop",
                            "reason": "operation_budget_exhausted",
                            "operation_limit": 64,
                            "operations_used": 64,
                            "next_action": "bisect_box",
                        },
                    ),
                ]
            )
        else:
            nodes.append(
                _leaf(
                    root_id,
                    branch_image_id,
                    domain,
                    "excluded_range",
                    build_excluded_range_witness(
                        guard_function, domain
                    ),
                )
            )

    bundle = {
        "schema_version": BUNDLE_SCHEMA,
        "problem_commitment": problem_commitment_json(),
        "arithmetic": copy.deepcopy(committed["arithmetic"]),
        "function_registry": function_registry,
        "image_enumeration": image_enumeration,
        "initial_cover": {
            "parameter_domain": domain.to_json(),
            "root_ids": root_ids,
            "root_hashes": [],
            "nodes": nodes,
            "cover_hash": "0" * 64,
        },
    }
    return refresh_declared_hashes(bundle)


def _find_node(bundle: Mapping[str, Any], node_id: str) -> dict[str, Any]:
    for node in bundle["initial_cover"]["nodes"]:
        if node["node_id"] == node_id:
            return node
    raise KeyError(node_id)


def build_hostile_mutations(
    fixture: Mapping[str, Any],
) -> list[tuple[str, str, dict[str, Any]]]:
    """Return adversarial fixtures and the semantic gate each must hit."""

    controls: list[tuple[str, str, dict[str, Any]]] = []

    deleted_leaf = copy.deepcopy(fixture)
    removed_root = deleted_leaf["initial_cover"]["root_ids"].pop()
    deleted_leaf["initial_cover"]["nodes"] = [
        node
        for node in deleted_leaf["initial_cover"]["nodes"]
        if node["node_id"] != removed_root
    ]
    deleted_leaf = refresh_declared_hashes(deleted_leaf)
    controls.append(
        ("deleted_leaf", "cover_image_binding", deleted_leaf)
    )

    wrong_split = copy.deepcopy(fixture)
    _find_node(wrong_split, "root-0-0")["split_point"] = _dyadic(1, 3)
    wrong_split = refresh_declared_hashes(wrong_split)
    controls.append(("wrong_split", "cover_partition", wrong_split))

    fake_inclusion = copy.deepcopy(fixture)
    unique_node = _find_node(fake_inclusion, "leaf-0-0-unique")
    unique_node["witness"]["krawczyk_image"] = DyadicInterval.closed(
        Dyadic.of(3, 3), Dyadic.of(5, 3)
    ).to_json()
    fake_inclusion = refresh_declared_hashes(fake_inclusion)
    controls.append(
        ("fake_krawczyk_inclusion", "unique_root_witness", fake_inclusion)
    )

    replaced_system = copy.deepcopy(fixture)
    replacement_entry = replaced_system["function_registry"]["functions"][0]
    replacement_entry["slope"] = _dyadic(4)
    replacement_entry["intercept"] = _dyadic(-3, 1)
    replacement = AffineFunction(
        "affine_unique_root", Dyadic.of(4), Dyadic.of(-3, 1)
    )
    excluded_node = _find_node(
        replaced_system, "leaf-0-0-excluded"
    )
    unique_node = _find_node(replaced_system, "leaf-0-0-unique")
    excluded_node["witness"] = build_excluded_range_witness(
        replacement, DyadicBox.from_json(excluded_node["box"])
    )
    unique_node["witness"] = build_unique_root_witness(
        replacement, DyadicBox.from_json(unique_node["box"])
    )
    replaced_system = refresh_declared_hashes(replaced_system)
    controls.append(
        (
            "replaced_affine_root_system",
            "problem_commitment",
            replaced_system,
        )
    )

    missing_image = copy.deepcopy(fixture)
    missing_image["image_enumeration"]["manifest"].pop()
    controls.append(("missing_image", "image_enumeration", missing_image))

    duplicate_id = copy.deepcopy(fixture)
    duplicate_id["initial_cover"]["nodes"].append(
        copy.deepcopy(_find_node(duplicate_id, "leaf-0-0-excluded"))
    )
    duplicate_id["initial_cover"]["cover_hash"] = _cover_hash(
        duplicate_id["initial_cover"]
    )
    controls.append(("duplicate_node_id", "cover_ids", duplicate_id))

    return controls


def run_hostile_controls(
    fixture: Mapping[str, Any],
) -> list[dict[str, str]]:
    outcomes: list[dict[str, str]] = []
    for name, expected_gate, mutation in build_hostile_mutations(fixture):
        try:
            replay_bundle(mutation)
        except CertificateError as error:
            if error.gate != expected_gate:
                raise AssertionError(
                    f"{name} failed at {error.gate}, expected {expected_gate}"
                ) from error
            outcomes.append(
                {
                    "control": name,
                    "expected_gate": expected_gate,
                    "observed_gate": error.gate,
                    "result": "rejected_as_intended",
                }
            )
        else:
            raise AssertionError(f"hostile control {name} was accepted")
    return outcomes


def build_report(
    fixture: Mapping[str, Any],
    repository_root: Path = REPOSITORY_ROOT,
) -> dict[str, Any]:
    replay = replay_bundle(fixture)
    inventory = []
    for relative in FOUNDATION_INVENTORY:
        path = repository_root / Path(relative)
        if not path.is_file():
            raise FileNotFoundError(path)
        inventory.append(
            {
                "path": relative,
                "normalized_lf_sha256": normalized_lf_sha256(path),
            }
        )
    return {
        "schema_version": REPORT_SCHEMA,
        "brief": "0019",
        "implementation_scope": (
            "source_separated_independent_foundation_replayer"
        ),
        "fixture_semantic_sha256": canonical_sha256(fixture),
        "replay_summary": replay,
        "hostile_controls": run_hostile_controls(fixture),
        "normalized_lf_code_inventory": inventory,
        "proved": [
            "canonical exact dyadic scalar grammar",
            "code-fixed external problem-registry commitment",
            "source-separated independent strict-JSON certificate replay",
            "endpoint-aware gap-free split-forest replay",
            "complete exact rectangular-lattice image fixture",
            "recomputed affine range exclusion",
            "recomputed one-dimensional exact Krawczyk strict inclusion",
            "explicit preservation of deterministic-budget unresolved leaves",
        ],
        "open_items": [
            "source-bound nine-dimensional Arb interval jets and physical Krawczyk replay",
            "nine-dimensional production image enumeration and metric pruning",
            "singular-cluster, seam-equivalence and tie certificates",
            "first-entry globality and no-earlier-sublevel cover",
            "hysteretic outer exit, re-arm and episode closest-point replay",
            "exact recurrence no-entry certificates",
            "clean independent Linux replay",
            "unconditioned population-law execution",
        ],
        "permitted_claim": (
            "The exact foundation fixture replays a gap-free image-indexed "
            "cover with proof-checked excluded and unique leaves while "
            "retaining its unresolved leaf."
        ),
        "forbidden_claim": (
            "The physical finite-K hysteretic world-sheet solver or the "
            "3+1 selection law is complete."
        ),
    }


def check_artifacts() -> dict[str, Any]:
    stored_fixture = strict_json_load(FIXTURE_PATH)
    expected_fixture = build_foundation_fixture()
    if not type_strict_equal(stored_fixture, expected_fixture):
        fail("artifact_check", "stored fixture differs from deterministic build")
    replay = replay_bundle(stored_fixture)
    stored_report = strict_json_load(REPORT_PATH)
    expected_report = build_report(stored_fixture)
    if not type_strict_equal(stored_report, expected_report):
        fail("artifact_check", "stored report differs from deterministic replay")
    return {
        "status": "PASS",
        "bundle_semantic_sha256": replay["bundle_semantic_sha256"],
        "report_semantic_sha256": canonical_sha256(stored_report),
        "root_count": replay["root_count"],
        "leaf_count": replay["leaf_count"],
        "resolution": replay["resolution"],
    }


def write_artifacts() -> dict[str, Any]:
    fixture = build_foundation_fixture()
    write_json(FIXTURE_PATH, fixture)
    report = build_report(fixture)
    write_json(REPORT_PATH, report)
    return {
        "status": "WROTE",
        "fixture": str(FIXTURE_PATH),
        "report": str(REPORT_PATH),
        "bundle_semantic_sha256": canonical_sha256(fixture),
        "report_semantic_sha256": canonical_sha256(report),
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.write:
        result = write_artifacts()
    elif args.check:
        result = check_artifacts()
    else:
        fixture = build_foundation_fixture()
        result = replay_bundle(fixture)
        result["hostile_controls"] = run_hostile_controls(fixture)
    print(
        json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
