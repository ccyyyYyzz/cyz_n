#!/usr/bin/env python3
"""Independent exact replayer for the Brief 0019 foundation certificate.

This file intentionally shares no project Python implementation with the
fixture generator.  Its only inputs are strict JSON bytes, the externally
committed problem registry, and Python's standard-library exact integers and
fractions.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
from dataclasses import dataclass
from fractions import Fraction
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
FIXTURE_PATH = ARTIFACT_DIR / "certified_solver_fixture.json"
REPORT_PATH = ARTIFACT_DIR / "certified_solver_report.json"
PROBLEM_REGISTRY_PATH = ARTIFACT_DIR / "foundation_problem_registry.json"

HEX_SHA256 = re.compile(r"[0-9a-f]{64}")


class CertificateReplayError(ValueError):
    """A certificate failed at a named independent semantic gate."""

    def __init__(self, gate: str, message: str):
        super().__init__(f"{gate}: {message}")
        self.gate = gate


def fail(gate: str, message: str) -> None:
    raise CertificateReplayError(gate, message)


def require_object(
    value: Any, keys: set[str], path: str, gate: str = "schema"
) -> dict[str, Any]:
    if type(value) is not dict:
        fail(gate, f"{path} must be an object")
    actual = set(value)
    if actual != keys:
        fail(
            gate,
            f"{path} keys differ; missing={sorted(keys - actual)}, "
            f"extra={sorted(actual - keys)}",
        )
    return value


def require_list(
    value: Any, path: str, gate: str = "schema"
) -> list[Any]:
    if type(value) is not list:
        fail(gate, f"{path} must be an array")
    return value


def require_string(
    value: Any, path: str, gate: str = "schema"
) -> str:
    if type(value) is not str or not value:
        fail(gate, f"{path} must be a nonempty string")
    return value


def require_int(value: Any, path: str, gate: str = "schema") -> int:
    if type(value) is not int:
        fail(gate, f"{path} must be an integer, not {type(value).__name__}")
    return value


def require_bool(value: Any, path: str, gate: str = "schema") -> bool:
    if type(value) is not bool:
        fail(gate, f"{path} must be a Boolean")
    return value


def require_sha(value: Any, path: str, gate: str) -> str:
    text = require_string(value, path, gate)
    if HEX_SHA256.fullmatch(text) is None:
        fail(gate, f"{path} is not a lowercase SHA-256 digest")
    return text


def unique_object(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail("strict_json", f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def forbidden_constant(token: str) -> None:
    fail("strict_json", f"non-finite JSON token {token!r} is forbidden")


def forbidden_float(token: str) -> None:
    fail(
        "strict_json",
        f"JSON floating token {token!r} is forbidden; serialize a dyadic",
    )


def assert_json_tree(value: Any, path: str = "$") -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        fail("strict_json", f"{path} contains an ordinary float")
    if type(value) is list:
        for index, item in enumerate(value):
            assert_json_tree(item, f"{path}[{index}]")
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str:
                fail("strict_json", f"{path} contains a non-string key")
            assert_json_tree(item, f"{path}.{key}")
        return
    fail("strict_json", f"{path} contains non-JSON type {type(value).__name__}")


def strict_json_loads(text: str) -> Any:
    value = json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_constant=forbidden_constant,
        parse_float=forbidden_float,
    )
    assert_json_tree(value)
    return value


def strict_json_load(path: Path) -> Any:
    with path.open("r", encoding="utf-8", newline=None) as handle:
        return strict_json_loads(handle.read())


def canonical_bytes(value: Any) -> bytes:
    assert_json_tree(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


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


def load_problem_registry(
    path: Path = PROBLEM_REGISTRY_PATH,
) -> dict[str, Any]:
    registry = strict_json_load(path)
    if canonical_sha256(registry) != PROBLEM_REGISTRY_CANONICAL_SHA256:
        fail(
            "problem_commitment",
            "external problem registry does not match the code-fixed SHA-256",
        )
    root = require_object(
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


def expected_commitment() -> dict[str, str]:
    return {
        "problem_id": PROBLEM_ID,
        "registry_schema": PROBLEM_REGISTRY_SCHEMA,
        "registry_canonical_sha256": PROBLEM_REGISTRY_CANONICAL_SHA256,
    }


@dataclass(frozen=True)
class Dyadic:
    numerator: int
    exponent: int

    def __post_init__(self) -> None:
        if type(self.numerator) is not int:
            fail("dyadic", "numerator must be an integer")
        if type(self.exponent) is not int or self.exponent < 0:
            fail("dyadic", "exponent must be a nonnegative integer")
        if self.numerator == 0 and self.exponent != 0:
            fail("dyadic", "zero must have exponent zero")
        if (
            self.numerator != 0
            and self.exponent > 0
            and self.numerator % 2 == 0
        ):
            fail("dyadic", "dyadic representation is not reduced")

    @classmethod
    def of(cls, numerator: int, exponent: int = 0) -> "Dyadic":
        if type(numerator) is not int or type(exponent) is not int:
            fail("dyadic", "dyadic constructor requires integers")
        if exponent < 0:
            fail("dyadic", "negative exponent is forbidden")
        if numerator == 0:
            return cls(0, 0)
        while exponent and numerator % 2 == 0:
            numerator //= 2
            exponent -= 1
        return cls(numerator, exponent)

    @classmethod
    def from_fraction(cls, value: Fraction) -> "Dyadic":
        denominator = value.denominator
        if denominator <= 0 or denominator & (denominator - 1):
            fail("dyadic", f"{value} is not a dyadic rational")
        return cls.of(value.numerator, denominator.bit_length() - 1)

    @classmethod
    def from_json(cls, value: Any, path: str) -> "Dyadic":
        obj = require_object(
            value, {"numerator", "exponent"}, path, "dyadic"
        )
        return cls(
            require_int(obj["numerator"], f"{path}.numerator", "dyadic"),
            require_int(obj["exponent"], f"{path}.exponent", "dyadic"),
        )

    def fraction(self) -> Fraction:
        return Fraction(self.numerator, 1 << self.exponent)

    def __lt__(self, other: "Dyadic") -> bool:
        return self.fraction() < other.fraction()

    def __le__(self, other: "Dyadic") -> bool:
        return self.fraction() <= other.fraction()

    def __gt__(self, other: "Dyadic") -> bool:
        return self.fraction() > other.fraction()

    def __ge__(self, other: "Dyadic") -> bool:
        return self.fraction() >= other.fraction()

    def __neg__(self) -> "Dyadic":
        return Dyadic.of(-self.numerator, self.exponent)

    def __add__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.fraction() + other.fraction())

    def __sub__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.fraction() - other.fraction())

    def __mul__(self, other: "Dyadic") -> "Dyadic":
        return Dyadic.from_fraction(self.fraction() * other.fraction())

    def __truediv__(self, other: "Dyadic") -> "Dyadic":
        if other.numerator == 0:
            fail("dyadic", "division by zero")
        return Dyadic.from_fraction(self.fraction() / other.fraction())

    def to_json(self) -> dict[str, int]:
        return {"numerator": self.numerator, "exponent": self.exponent}


ZERO = Dyadic.of(0)
ONE = Dyadic.of(1)


@dataclass(frozen=True)
class Interval:
    lower: Dyadic
    upper: Dyadic
    lower_closed: bool
    upper_closed: bool

    def __post_init__(self) -> None:
        if (
            type(self.lower_closed) is not bool
            or type(self.upper_closed) is not bool
        ):
            fail("interval", "endpoint flags must be Boolean")
        if self.upper < self.lower:
            fail("interval", "lower endpoint exceeds upper endpoint")
        if self.lower == self.upper and not (
            self.lower_closed and self.upper_closed
        ):
            fail("interval", "a point interval must be closed")

    @classmethod
    def from_json(cls, value: Any, path: str) -> "Interval":
        obj = require_object(
            value,
            {"lower", "upper", "lower_closed", "upper_closed"},
            path,
            "interval",
        )
        return cls(
            Dyadic.from_json(obj["lower"], f"{path}.lower"),
            Dyadic.from_json(obj["upper"], f"{path}.upper"),
            require_bool(
                obj["lower_closed"], f"{path}.lower_closed", "interval"
            ),
            require_bool(
                obj["upper_closed"], f"{path}.upper_closed", "interval"
            ),
        )

    @classmethod
    def closed(cls, lower: Dyadic, upper: Dyadic) -> "Interval":
        return cls(lower, upper, True, True)

    def to_json(self) -> dict[str, Any]:
        return {
            "lower": self.lower.to_json(),
            "upper": self.upper.to_json(),
            "lower_closed": self.lower_closed,
            "upper_closed": self.upper_closed,
        }

    def hull(self) -> "Interval":
        return Interval.closed(self.lower, self.upper)

    def split(self, point: Dyadic) -> tuple["Interval", "Interval"]:
        if not self.lower < point or not point < self.upper:
            fail("cover_partition", "split point must be strictly interior")
        return (
            Interval(self.lower, point, self.lower_closed, False),
            Interval(point, self.upper, True, self.upper_closed),
        )


@dataclass(frozen=True)
class Box:
    axes: tuple[str, ...]
    intervals: tuple[Interval, ...]

    def __post_init__(self) -> None:
        if not self.axes or len(self.axes) != len(self.intervals):
            fail("box", "box axes and intervals must have equal positive size")
        if len(set(self.axes)) != len(self.axes):
            fail("box", "box axes must be unique")
        if any(type(axis) is not str or not axis for axis in self.axes):
            fail("box", "box axis names must be nonempty strings")

    @classmethod
    def from_json(cls, value: Any, path: str) -> "Box":
        obj = require_object(value, {"axes", "intervals"}, path, "box")
        raw_axes = require_list(obj["axes"], f"{path}.axes", "box")
        raw_intervals = require_list(
            obj["intervals"], f"{path}.intervals", "box"
        )
        return cls(
            tuple(
                require_string(axis, f"{path}.axes[{index}]", "box")
                for index, axis in enumerate(raw_axes)
            ),
            tuple(
                Interval.from_json(raw, f"{path}.intervals[{index}]")
                for index, raw in enumerate(raw_intervals)
            ),
        )

    def split(self, axis: str, point: Dyadic) -> tuple["Box", "Box"]:
        if axis not in self.axes:
            fail("cover_partition", f"unknown split axis {axis!r}")
        index = self.axes.index(axis)
        left_interval, right_interval = self.intervals[index].split(point)
        left = list(self.intervals)
        right = list(self.intervals)
        left[index] = left_interval
        right[index] = right_interval
        return Box(self.axes, tuple(left)), Box(self.axes, tuple(right))


def interval_add(left: Interval, right: Interval) -> Interval:
    return Interval.closed(
        left.lower + right.lower, left.upper + right.upper
    )


def interval_sub(left: Interval, right: Interval) -> Interval:
    return Interval.closed(
        left.lower - right.upper, left.upper - right.lower
    )


def interval_mul(left: Interval, right: Interval) -> Interval:
    products = (
        left.lower * right.lower,
        left.lower * right.upper,
        left.upper * right.lower,
        left.upper * right.upper,
    )
    return Interval.closed(min(products), max(products))


def interval_scale(interval: Interval, scalar: Dyadic) -> Interval:
    return interval_mul(interval.hull(), Interval.closed(scalar, scalar))


@dataclass(frozen=True)
class Affine:
    identifier: str
    slope: Dyadic
    intercept: Dyadic

    def point(self, value: Dyadic) -> Dyadic:
        return self.slope * value + self.intercept

    def range_on(self, interval: Interval) -> Interval:
        first = self.point(interval.lower)
        second = self.point(interval.upper)
        return Interval.closed(min(first, second), max(first, second))


def parse_functions(value: Any) -> dict[str, Affine]:
    registry = require_object(
        value, {"schema_version", "functions"}, "$.function_registry"
    )
    if registry["schema_version"] != FUNCTION_REGISTRY_SCHEMA:
        fail("function_registry", "unknown function registry schema")
    entries = require_list(
        registry["functions"], "$.function_registry.functions"
    )
    if not entries:
        fail("function_registry", "function registry is empty")
    result: dict[str, Affine] = {}
    for index, raw in enumerate(entries):
        path = f"$.function_registry.functions[{index}]"
        entry = require_object(
            raw,
            {"function_id", "kind", "slope", "intercept"},
            path,
            "function_registry",
        )
        identifier = require_string(
            entry["function_id"], f"{path}.function_id", "function_registry"
        )
        if identifier in result:
            fail("function_registry", f"duplicate function ID {identifier!r}")
        if entry["kind"] != "affine_1d":
            fail("function_registry", f"{path}.kind is unsupported")
        result[identifier] = Affine(
            identifier,
            Dyadic.from_json(entry["slope"], f"{path}.slope"),
            Dyadic.from_json(entry["intercept"], f"{path}.intercept"),
        )
    return result


def one_axis(box: Box, gate: str) -> Interval:
    if box.axes != ("u",):
        fail(gate, "foundation witnesses require the one-dimensional u box")
    return box.intervals[0]


def expected_range_witness(function: Affine, box: Box) -> dict[str, Any]:
    interval = one_axis(box, "excluded_range_witness")
    result = function.range_on(interval)
    if result.lower > ZERO:
        separation = "strictly_positive"
    elif result.upper < ZERO:
        separation = "strictly_negative"
    else:
        fail("excluded_range_witness", "exact range does not exclude zero")
    return {
        "witness_type": "exact_affine_component_range",
        "function_id": function.identifier,
        "range": result.to_json(),
        "zero_separation": separation,
    }


def expected_krawczyk(function: Affine, box: Box) -> dict[str, Any]:
    domain = one_axis(box, "unique_root_witness")
    midpoint = Dyadic.from_fraction(
        (domain.lower.fraction() + domain.upper.fraction()) / 2
    )
    if function.slope == ZERO:
        fail("unique_root_witness", "zero derivative is not invertible")
    preconditioner = ONE / function.slope
    point_value = function.point(midpoint)
    derivative = Interval.closed(function.slope, function.slope)
    center = midpoint - preconditioner * point_value
    identity_minus_cd = interval_sub(
        Interval.closed(ONE, ONE),
        interval_scale(derivative, preconditioner),
    )
    centered_box = Interval.closed(
        domain.lower - midpoint, domain.upper - midpoint
    )
    image = interval_add(
        Interval.closed(center, center),
        interval_mul(identity_minus_cd, centered_box),
    )
    lower_margin = image.lower - domain.lower
    upper_margin = domain.upper - image.upper
    if not (
        domain.lower < image.lower
        and image.upper < domain.upper
        and lower_margin > ZERO
        and upper_margin > ZERO
    ):
        fail(
            "unique_root_witness",
            "recomputed Krawczyk image is not strictly inside the box",
        )
    return {
        "witness_type": "exact_interval_krawczyk_1d",
        "arithmetic": "exact_dyadic_rational",
        "function_id": function.identifier,
        "midpoint": midpoint.to_json(),
        "preconditioner": preconditioner.to_json(),
        "point_value": point_value.to_json(),
        "derivative_enclosure": derivative.to_json(),
        "krawczyk_image": image.to_json(),
        "inclusion_margins": {
            "lower": lower_margin.to_json(),
            "upper": upper_margin.to_json(),
        },
    }


def verify_leaf(
    node: Mapping[str, Any], box: Box, functions: Mapping[str, Affine]
) -> str:
    status = node["status"]
    witness = node["witness"]
    if status == "excluded_range":
        parsed = require_object(
            witness,
            {"witness_type", "function_id", "range", "zero_separation"},
            "$.leaf.witness",
            "excluded_range_witness",
        )
        identifier = require_string(
            parsed["function_id"],
            "$.leaf.witness.function_id",
            "excluded_range_witness",
        )
        if identifier not in functions:
            fail("excluded_range_witness", "unknown function ID")
        expected = expected_range_witness(functions[identifier], box)
        if not type_strict_equal(parsed, expected):
            fail(
                "excluded_range_witness",
                "stored affine range differs from exact replay",
            )
    elif status == "unique_root":
        parsed = require_object(
            witness,
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
        if parsed["witness_type"] != "exact_interval_krawczyk_1d":
            fail("unique_root_witness", "unsupported witness type")
        if parsed["arithmetic"] != "exact_dyadic_rational":
            fail("unique_root_witness", "non-exact arithmetic is forbidden")
        identifier = require_string(
            parsed["function_id"],
            "$.leaf.witness.function_id",
            "unique_root_witness",
        )
        if identifier not in functions:
            fail("unique_root_witness", "unknown function ID")
        expected = expected_krawczyk(functions[identifier], box)
        if not type_strict_equal(parsed, expected):
            fail(
                "unique_root_witness",
                "stored Krawczyk data differs from exact replay",
            )
    elif status == "unresolved":
        parsed = require_object(
            witness,
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
        if parsed["witness_type"] != "deterministic_budget_stop":
            fail("unresolved_witness", "unsupported witness type")
        if parsed["reason"] != "operation_budget_exhausted":
            fail("unresolved_witness", "unexpected stop reason")
        limit = require_int(
            parsed["operation_limit"],
            "$.leaf.witness.operation_limit",
            "unresolved_witness",
        )
        used = require_int(
            parsed["operations_used"],
            "$.leaf.witness.operations_used",
            "unresolved_witness",
        )
        if limit <= 0 or used != limit:
            fail("unresolved_witness", "used must equal the positive limit")
        if parsed["next_action"] != "bisect_box":
            fail("unresolved_witness", "unexpected continuation action")
    else:
        fail("leaf_status", f"unsupported foundation status {status!r}")
    return status


def parse_dyadic_list(
    value: Any, path: str, length: int, gate: str
) -> list[Dyadic]:
    items = require_list(value, path, gate)
    if len(items) != length:
        fail(gate, f"{path} has length {len(items)}, expected {length}")
    return [
        Dyadic.from_json(item, f"{path}[{index}]")
        for index, item in enumerate(items)
    ]


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def image_identifier(vector: Sequence[int]) -> str:
    return "n[" + ",".join(str(component) for component in vector) + "]"


def expected_vectors(
    periods: Sequence[Dyadic],
    inverse: Sequence[Dyadic],
    square_roots: Sequence[Dyadic],
    r_out: Dyadic,
    bounds: Sequence[Interval],
) -> list[tuple[int, ...]]:
    ranges: list[range] = []
    for axis, (period, inv, root, bound) in enumerate(
        zip(periods, inverse, square_roots, bounds)
    ):
        if period <= ZERO:
            fail("image_enumeration", f"period {axis} is not positive")
        if inv <= ZERO or root < ZERO or root * root != inv:
            fail("image_enumeration", f"metric root {axis} is invalid")
        radius = r_out * root
        lower = (bound.lower.fraction() - radius.fraction()) / period.fraction()
        upper = (bound.upper.fraction() + radius.fraction()) / period.fraction()
        first = ceil_fraction(lower)
        last = upper.numerator // upper.denominator
        ranges.append(range(first, last + 1) if first <= last else range(0))
    count = 1
    for values in ranges:
        count *= len(values)
    if count > 100_000:
        fail("image_enumeration", "enumeration budget exceeded")
    return [tuple(item) for item in itertools.product(*ranges)]


IMAGE_KEYS = {
    "dimension",
    "periods",
    "metric_diagonal",
    "metric_inverse_diagonal",
    "sqrt_metric_inverse_diagonal",
    "r_out",
    "separation_bounds",
    "manifest",
}


def replay_images(value: Any, committed_problem: Any) -> list[str]:
    image_data = require_object(
        value, IMAGE_KEYS, "$.image_enumeration", "image_enumeration"
    )
    source = {key: image_data[key] for key in image_data if key != "manifest"}
    if not type_strict_equal(source, committed_problem):
        fail(
            "image_enumeration",
            "bundle image inputs differ from the external problem commitment",
        )
    dimension = require_int(
        image_data["dimension"],
        "$.image_enumeration.dimension",
        "image_enumeration",
    )
    if dimension <= 0:
        fail("image_enumeration", "dimension must be positive")
    periods = parse_dyadic_list(
        image_data["periods"],
        "$.image_enumeration.periods",
        dimension,
        "image_enumeration",
    )
    metric = parse_dyadic_list(
        image_data["metric_diagonal"],
        "$.image_enumeration.metric_diagonal",
        dimension,
        "image_enumeration",
    )
    inverse = parse_dyadic_list(
        image_data["metric_inverse_diagonal"],
        "$.image_enumeration.metric_inverse_diagonal",
        dimension,
        "image_enumeration",
    )
    roots = parse_dyadic_list(
        image_data["sqrt_metric_inverse_diagonal"],
        "$.image_enumeration.sqrt_metric_inverse_diagonal",
        dimension,
        "image_enumeration",
    )
    for axis, (entry, inv) in enumerate(zip(metric, inverse)):
        if entry <= ZERO or entry * inv != ONE:
            fail("image_enumeration", f"metric pair {axis} is not exact")
    r_out = Dyadic.from_json(
        image_data["r_out"], "$.image_enumeration.r_out"
    )
    if r_out <= ZERO:
        fail("image_enumeration", "r_out must be positive")
    raw_bounds = require_list(
        image_data["separation_bounds"],
        "$.image_enumeration.separation_bounds",
        "image_enumeration",
    )
    if len(raw_bounds) != dimension:
        fail("image_enumeration", "separation-bound dimension mismatch")
    bounds = [
        Interval.from_json(
            item, f"$.image_enumeration.separation_bounds[{index}]"
        )
        for index, item in enumerate(raw_bounds)
    ]
    vectors = expected_vectors(periods, inverse, roots, r_out, bounds)
    expected = [
        {
            "image_id": image_identifier(vector),
            "lattice_vector": list(vector),
        }
        for vector in vectors
    ]
    manifest = require_list(
        image_data["manifest"],
        "$.image_enumeration.manifest",
        "image_enumeration",
    )
    parsed: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_vectors: set[tuple[int, ...]] = set()
    for index, raw in enumerate(manifest):
        path = f"$.image_enumeration.manifest[{index}]"
        entry = require_object(
            raw, {"image_id", "lattice_vector"}, path, "image_enumeration"
        )
        identifier = require_string(
            entry["image_id"], f"{path}.image_id", "image_enumeration"
        )
        raw_vector = require_list(
            entry["lattice_vector"],
            f"{path}.lattice_vector",
            "image_enumeration",
        )
        if len(raw_vector) != dimension:
            fail("image_enumeration", f"{path} dimension differs")
        vector = tuple(
            require_int(
                component,
                f"{path}.lattice_vector[{component_index}]",
                "image_enumeration",
            )
            for component_index, component in enumerate(raw_vector)
        )
        if identifier in seen_ids or vector in seen_vectors:
            fail("image_manifest_ids", "duplicate image identity")
        seen_ids.add(identifier)
        seen_vectors.add(vector)
        if identifier != image_identifier(vector):
            fail("image_enumeration", "image ID is not canonical")
        parsed.append(
            {"image_id": identifier, "lattice_vector": list(vector)}
        )
    if not type_strict_equal(parsed, expected):
        fail(
            "image_enumeration",
            "manifest is not the complete ordered Cartesian enumeration",
        )
    return [entry["image_id"] for entry in parsed]


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


def hash_without(value: Mapping[str, Any], excluded: str) -> str:
    return canonical_sha256(
        {key: item for key, item in value.items() if key != excluded}
    )


def replay_cover(
    value: Any,
    manifest_ids: Sequence[str],
    functions: Mapping[str, Affine],
    committed_domain: Any,
) -> dict[str, Any]:
    cover = require_object(
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
    domain = Box.from_json(
        cover["parameter_domain"], "$.initial_cover.parameter_domain"
    )
    if not type_strict_equal(cover["parameter_domain"], committed_domain):
        fail(
            "problem_commitment",
            "bundle parameter domain differs from the external registry",
        )
    root_ids = [
        require_string(item, f"$.initial_cover.root_ids[{index}]", "cover_topology")
        for index, item in enumerate(
            require_list(
                cover["root_ids"], "$.initial_cover.root_ids", "cover_topology"
            )
        )
    ]
    if not root_ids:
        fail("cover_topology", "complete cover cannot be empty")
    if len(set(root_ids)) != len(root_ids):
        fail("cover_ids", "duplicate root IDs")
    raw_nodes = require_list(
        cover["nodes"], "$.initial_cover.nodes", "cover_topology"
    )
    if not raw_nodes:
        fail("cover_topology", "complete cover contains no nodes")
    nodes: dict[str, dict[str, Any]] = {}
    for index, raw in enumerate(raw_nodes):
        path = f"$.initial_cover.nodes[{index}]"
        if type(raw) is not dict:
            fail("cover_schema", f"{path} must be an object")
        node_type = require_string(
            raw.get("node_type"), f"{path}.node_type", "cover_schema"
        )
        if node_type not in {"leaf", "split"}:
            fail("cover_schema", f"{path}.node_type is unknown")
        node = require_object(
            raw,
            LEAF_KEYS if node_type == "leaf" else SPLIT_KEYS,
            path,
            "cover_schema",
        )
        identifier = require_string(
            node["node_id"], f"{path}.node_id", "cover_ids"
        )
        if identifier in nodes:
            fail("cover_ids", f"duplicate node ID {identifier!r}")
        require_string(node["image_id"], f"{path}.image_id", "cover_schema")
        require_sha(node["node_hash"], f"{path}.node_hash", "node_hash")
        nodes[identifier] = node
    for root_id in root_ids:
        if root_id not in nodes:
            fail("cover_topology", f"root {root_id!r} is missing")
    if len(root_ids) != len(manifest_ids):
        fail("cover_image_binding", "cover needs exactly one root per image")
    if [nodes[item]["image_id"] for item in root_ids] != list(manifest_ids):
        fail(
            "cover_image_binding",
            "ordered roots do not bind every manifest image exactly once",
        )

    parent_count = {identifier: 0 for identifier in nodes}
    for identifier, node in nodes.items():
        if node["node_type"] != "split":
            continue
        left_id = require_string(
            node["left_child_id"],
            f"node {identifier}.left_child_id",
            "cover_topology",
        )
        right_id = require_string(
            node["right_child_id"],
            f"node {identifier}.right_child_id",
            "cover_topology",
        )
        if left_id == right_id:
            fail("cover_topology", f"node {identifier!r} repeats a child")
        for child_id in (left_id, right_id):
            if child_id not in nodes:
                fail(
                    "cover_topology",
                    f"node {identifier!r} references missing child {child_id!r}",
                )
            parent_count[child_id] += 1
            if parent_count[child_id] > 1:
                fail("cover_topology", f"node {child_id!r} has two parents")
    root_set = set(root_ids)
    for identifier, count in parent_count.items():
        expected = 0 if identifier in root_set else 1
        if count != expected:
            fail(
                "cover_topology",
                f"node {identifier!r} parent count is {count}, expected {expected}",
            )

    visiting: set[str] = set()
    visited: set[str] = set()
    hashes: dict[str, str] = {}
    counts = {"excluded_range": 0, "unique_root": 0, "unresolved": 0}

    def visit(identifier: str, expected_box: Box, expected_image: str) -> str:
        if identifier in visiting or identifier in visited:
            fail("cover_topology", f"node {identifier!r} is reached twice")
        visiting.add(identifier)
        node = nodes[identifier]
        if node["image_id"] != expected_image:
            fail("cover_image_binding", f"node {identifier!r} changes image")
        actual_box = Box.from_json(node["box"], f"node {identifier}.box")
        if actual_box != expected_box:
            fail(
                "cover_partition",
                f"node {identifier!r} is not the replayed child box",
            )
        if node["node_type"] == "leaf":
            status = verify_leaf(node, actual_box, functions)
            counts[status] += 1
        else:
            axis = require_string(
                node["axis"], f"node {identifier}.axis", "cover_partition"
            )
            point = Dyadic.from_json(
                node["split_point"], f"node {identifier}.split_point"
            )
            left_box, right_box = actual_box.split(axis, point)
            left_hash = visit(
                node["left_child_id"], left_box, expected_image
            )
            right_hash = visit(
                node["right_child_id"], right_box, expected_image
            )
            declared_children = require_object(
                node["child_hashes"],
                {"left", "right"},
                f"node {identifier}.child_hashes",
                "node_hash",
            )
            require_sha(
                declared_children["left"],
                f"node {identifier}.child_hashes.left",
                "node_hash",
            )
            require_sha(
                declared_children["right"],
                f"node {identifier}.child_hashes.right",
                "node_hash",
            )
            if not type_strict_equal(
                declared_children,
                {"left": left_hash, "right": right_hash},
            ):
                fail("node_hash", f"node {identifier!r} child hashes differ")
        derived = hash_without(node, "node_hash")
        if node["node_hash"] != derived:
            fail("node_hash", f"node {identifier!r} hash differs")
        visiting.remove(identifier)
        visited.add(identifier)
        hashes[identifier] = derived
        return derived

    for root_id, image_id in zip(root_ids, manifest_ids):
        visit(root_id, domain, image_id)
    if visited != set(nodes):
        fail(
            "cover_topology",
            f"unreachable nodes remain: {sorted(set(nodes) - visited)}",
        )

    declared_roots = require_list(
        cover["root_hashes"], "$.initial_cover.root_hashes", "root_hash"
    )
    for index, raw in enumerate(declared_roots):
        entry = require_object(
            raw,
            {"root_id", "node_hash"},
            f"$.initial_cover.root_hashes[{index}]",
            "root_hash",
        )
        require_string(
            entry["root_id"],
            f"$.initial_cover.root_hashes[{index}].root_id",
            "root_hash",
        )
        require_sha(
            entry["node_hash"],
            f"$.initial_cover.root_hashes[{index}].node_hash",
            "root_hash",
        )
    expected_roots = [
        {"root_id": root_id, "node_hash": hashes[root_id]}
        for root_id in root_ids
    ]
    if not type_strict_equal(declared_roots, expected_roots):
        fail("root_hash", "declared root hashes differ")
    declared_cover = require_sha(
        cover["cover_hash"], "$.initial_cover.cover_hash", "cover_hash"
    )
    if declared_cover != hash_without(cover, "cover_hash"):
        fail("cover_hash", "declared cover hash differs")

    leaf_count = sum(counts.values())
    return {
        "image_count": len(manifest_ids),
        "root_count": len(root_ids),
        "node_count": len(nodes),
        "leaf_count": leaf_count,
        "status_counts": counts,
        "coverage": "gap_free_exact_partition",
        "resolution": (
            "unresolved_present"
            if counts["unresolved"]
            else "all_leaves_certified"
        ),
    }


def replay_bundle(bundle: Any) -> dict[str, Any]:
    assert_json_tree(bundle)
    root = require_object(
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
    committed = load_problem_registry()
    commitment = require_object(
        root["problem_commitment"],
        {
            "problem_id",
            "registry_schema",
            "registry_canonical_sha256",
        },
        "$.problem_commitment",
        "problem_commitment",
    )
    if not type_strict_equal(commitment, expected_commitment()):
        fail("problem_commitment", "bundle names a different problem")
    arithmetic = require_object(
        root["arithmetic"],
        {"scalar", "interval", "partition_policy"},
        "$.arithmetic",
    )
    if not type_strict_equal(arithmetic, committed["arithmetic"]):
        fail("problem_commitment", "arithmetic conventions differ")
    if not type_strict_equal(
        root["function_registry"], committed["function_registry"]
    ):
        fail(
            "problem_commitment",
            "bundle affine system differs from the external registry",
        )
    functions = parse_functions(root["function_registry"])
    manifest_ids = replay_images(
        root["image_enumeration"], committed["image_problem"]
    )
    summary = replay_cover(
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


def check_artifacts() -> dict[str, Any]:
    fixture = strict_json_load(FIXTURE_PATH)
    replay = replay_bundle(fixture)
    report = strict_json_load(REPORT_PATH)
    report_root = require_object(
        report,
        {
            "schema_version",
            "brief",
            "implementation_scope",
            "fixture_semantic_sha256",
            "replay_summary",
            "hostile_controls",
            "normalized_lf_code_inventory",
            "proved",
            "open_items",
            "permitted_claim",
            "forbidden_claim",
        },
        "$.report",
        "artifact_check",
    )
    if report_root["schema_version"] != REPORT_SCHEMA:
        fail("artifact_check", "unexpected report schema")
    if report_root["fixture_semantic_sha256"] != canonical_sha256(fixture):
        fail("artifact_check", "report fixture hash differs")
    if not type_strict_equal(report_root["replay_summary"], replay):
        fail(
            "artifact_check",
            "report replay summary differs from independent replay",
        )
    return {
        "status": "PASS",
        "bundle_semantic_sha256": replay["bundle_semantic_sha256"],
        "report_semantic_sha256": canonical_sha256(report),
        "root_count": replay["root_count"],
        "leaf_count": replay["leaf_count"],
        "resolution": replay["resolution"],
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    result = check_artifacts() if args.check else replay_bundle(
        strict_json_load(FIXTURE_PATH)
    )
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
