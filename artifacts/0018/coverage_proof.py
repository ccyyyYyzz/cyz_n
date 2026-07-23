#!/usr/bin/env python3
"""Replayable typed coverage-tree certificates for Brief 0018.

The objects in this module are deliberately small exact fixtures.  They test
proof serialization and replay logic; they are not certificates emitted by a
physical world-sheet root solver.
"""

from __future__ import annotations

import copy
import hashlib
import json
from fractions import Fraction
from typing import Any, Iterable, Sequence


COVERAGE_SCHEMA_VERSION = "cyz-brief-0018-coverage-manifest-v1"
PROBLEM_COMMITMENT_SCHEMA_VERSION = (
    "cyz-brief-0018-event-problem-commitment-v1"
)
FUNCTION_REGISTRY_SCHEMA_VERSION = (
    "cyz-brief-0018-synthetic-function-registry-v1"
)
SYNTHETIC_PROOF_BACKEND = "exact-synthetic-fixture"
AXES = ("sigma1", "sigma2", "time")
LEAF_CLASSES = (
    "excluded",
    "unique_root",
    "certified_singular_cluster",
    "unresolved",
)


class ProofError(ValueError):
    """Raised when a replayable proof object is incomplete or inconsistent."""


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise ProofError(f"{path}: {message}")


def _exact_keys(
    value: Any, expected: set[str], path: str
) -> dict[str, Any]:
    _require(type(value) is dict, path, "expected an object")
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    _require(not missing, path, f"missing keys {missing}")
    _require(not extra, path, f"unexpected keys {extra}")
    return value


def _string(value: Any, path: str) -> str:
    _require(type(value) is str and bool(value), path, "expected nonempty string")
    return value


def _integer(value: Any, path: str) -> int:
    _require(type(value) is int, path, "expected integer; booleans forbidden")
    return value


def _boolean(value: Any, path: str) -> bool:
    _require(type(value) is bool, path, "expected boolean")
    return value


def _string_list(value: Any, path: str) -> list[str]:
    _require(type(value) is list, path, "expected array")
    for index, item in enumerate(value):
        _string(item, f"{path}[{index}]")
    return value


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def _digest(value: Any, path: str) -> str:
    result = _string(value, path)
    _require(
        len(result) == 64
        and all(character in "0123456789abcdef" for character in result),
        path,
        "expected lowercase SHA-256",
    )
    return result


def dyadic(numerator: int, power: int = 0) -> dict[str, int]:
    if power < 0:
        raise ValueError("dyadic power must be nonnegative")
    if numerator == 0:
        power = 0
    while power > 0 and numerator % 2 == 0:
        numerator //= 2
        power -= 1
    return {"numerator": numerator, "power_of_two": power}


def as_fraction(value: Any, path: str = "$dyadic") -> Fraction:
    item = _exact_keys(value, {"numerator", "power_of_two"}, path)
    numerator = _integer(item["numerator"], f"{path}.numerator")
    power = _integer(item["power_of_two"], f"{path}.power_of_two")
    _require(power >= 0, f"{path}.power_of_two", "power must be nonnegative")
    _require(
        power == 0 or numerator % 2 != 0,
        path,
        "dyadic must be in canonical reduced form",
    )
    return Fraction(numerator, 2**power)


def dyadic_from_fraction(value: Fraction) -> dict[str, int]:
    denominator = value.denominator
    _require(
        denominator & (denominator - 1) == 0,
        "$fraction",
        "fraction is not dyadic",
    )
    return dyadic(value.numerator, denominator.bit_length() - 1)


def exact_interval(
    lower: Fraction | int, upper: Fraction | int
) -> dict[str, Any]:
    lower_fraction = Fraction(lower)
    upper_fraction = Fraction(upper)
    if lower_fraction > upper_fraction:
        raise ValueError("interval endpoints reversed")
    return {
        "lo": dyadic_from_fraction(lower_fraction),
        "hi": dyadic_from_fraction(upper_fraction),
    }


def interval_fractions(
    value: Any, path: str = "$interval"
) -> tuple[Fraction, Fraction]:
    interval = _exact_keys(value, {"lo", "hi"}, path)
    lower = as_fraction(interval["lo"], f"{path}.lo")
    upper = as_fraction(interval["hi"], f"{path}.hi")
    _require(lower <= upper, path, "interval endpoints reversed")
    return lower, upper


def exact_box(
    sigma1: tuple[Fraction | int, Fraction | int],
    sigma2: tuple[Fraction | int, Fraction | int],
    time: tuple[Fraction | int, Fraction | int],
) -> dict[str, Any]:
    return {
        "sigma1": exact_interval(*sigma1),
        "sigma2": exact_interval(*sigma2),
        "time": exact_interval(*time),
    }


def validate_box(value: Any, path: str) -> dict[str, Any]:
    box = _exact_keys(value, set(AXES), path)
    for axis in AXES:
        interval_fractions(box[axis], f"{path}.{axis}")
    return box


def box_equal(left: dict[str, Any], right: dict[str, Any]) -> bool:
    return all(
        interval_fractions(left[axis])
        == interval_fractions(right[axis])
        for axis in AXES
    )


def interval_strictly_inside(
    inner: dict[str, Any], outer: dict[str, Any]
) -> bool:
    for axis in AXES:
        inner_lower, inner_upper = interval_fractions(inner[axis])
        outer_lower, outer_upper = interval_fractions(outer[axis])
        if not (
            outer_lower < inner_lower
            and inner_upper < outer_upper
        ):
            return False
    return True


def _exact_matrix_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    rows = [[Fraction(item) for item in row] for row in matrix]
    if not rows:
        return 0
    row_count = len(rows)
    column_count = len(rows[0])
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if rows[row][column] != 0
            ),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(row_count):
            if row == pivot_row:
                continue
            coefficient = rows[row][column]
            if coefficient:
                rows[row] = [
                    value - coefficient * pivot_value
                    for value, pivot_value in zip(
                        rows[row], rows[pivot_row]
                    )
                ]
        pivot_row += 1
        if pivot_row == row_count:
            break
    return pivot_row


def _validate_exact_vector(
    value: Any, length: int, path: str
) -> list[Fraction]:
    _require(
        type(value) is list and len(value) == length,
        path,
        f"expected exact vector of length {length}",
    )
    return [
        as_fraction(item, f"{path}[{index}]")
        for index, item in enumerate(value)
    ]


def _validate_exact_matrix(
    value: Any, rows: int, columns: int, path: str
) -> list[list[Fraction]]:
    _require(
        type(value) is list and len(value) == rows,
        path,
        f"expected {rows} rows",
    )
    return [
        _validate_exact_vector(row, columns, f"{path}[{index}]")
        for index, row in enumerate(value)
    ]


def _determinant_3(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )


def _affine_value_range(
    coefficients: Sequence[Fraction],
    constant: Fraction,
    box: dict[str, Any],
) -> tuple[Fraction, Fraction]:
    lower = constant
    upper = constant
    for coefficient, axis in zip(coefficients, AXES):
        axis_lower, axis_upper = interval_fractions(box[axis])
        if coefficient >= 0:
            lower += coefficient * axis_lower
            upper += coefficient * axis_upper
        else:
            lower += coefficient * axis_upper
            upper += coefficient * axis_lower
    return lower, upper


def _validate_image(value: Any, path: str) -> dict[str, Any]:
    image = _exact_keys(
        value,
        {
            "image_id",
            "lattice_vector",
            "physical_image_key",
            "seam_equivalence_key",
        },
        path,
    )
    _string(image["image_id"], f"{path}.image_id")
    _require(
        type(image["lattice_vector"]) is list
        and len(image["lattice_vector"]) == 9,
        f"{path}.lattice_vector",
        "expected 9-vector",
    )
    for index, item in enumerate(image["lattice_vector"]):
        _integer(item, f"{path}.lattice_vector[{index}]")
    _string(image["physical_image_key"], f"{path}.physical_image_key")
    _string(
        image["seam_equivalence_key"],
        f"{path}.seam_equivalence_key",
    )
    return image


def _validate_domain(value: Any, path: str) -> dict[str, Any]:
    domain = _exact_keys(
        value,
        {"domain_id", "image_id", "root_node_id", "box"},
        path,
    )
    _string(domain["domain_id"], f"{path}.domain_id")
    _string(domain["image_id"], f"{path}.image_id")
    _string(domain["root_node_id"], f"{path}.root_node_id")
    validate_box(domain["box"], f"{path}.box")
    return domain


def _validate_node(value: Any, path: str) -> dict[str, Any]:
    node = _exact_keys(
        value,
        {
            "node_id",
            "domain_id",
            "kind",
            "box",
            "split_axis",
            "split_value",
            "children",
            "leaf_id",
        },
        path,
    )
    _string(node["node_id"], f"{path}.node_id")
    _string(node["domain_id"], f"{path}.domain_id")
    kind = _string(node["kind"], f"{path}.kind")
    _require(kind in ("split", "leaf"), f"{path}.kind", "unknown node kind")
    validate_box(node["box"], f"{path}.box")
    _require(type(node["children"]) is list, f"{path}.children", "expected array")
    if kind == "split":
        _require(
            node["split_axis"] in AXES,
            f"{path}.split_axis",
            "invalid split axis",
        )
        as_fraction(node["split_value"], f"{path}.split_value")
        _require(
            len(node["children"]) == 2,
            f"{path}.children",
            "split node requires left/right children",
        )
        for index, child in enumerate(node["children"]):
            _string(child, f"{path}.children[{index}]")
        _require(node["leaf_id"] is None, f"{path}.leaf_id", "split node cannot have leaf")
    else:
        _require(node["split_axis"] is None, f"{path}.split_axis", "leaf cannot split")
        _require(node["split_value"] is None, f"{path}.split_value", "leaf cannot split")
        _require(not node["children"], f"{path}.children", "leaf cannot have children")
        _string(node["leaf_id"], f"{path}.leaf_id")
    return node


def _validate_exclusion_witness(
    witness: Any, leaf_box: dict[str, Any], path: str
) -> dict[str, Any]:
    item = _exact_keys(
        witness,
        {
            "type",
            "function_component",
            "affine_model",
            "range",
            "backend",
            "problem_commitment_sha256",
            "model_id",
            "model_sha256",
        },
        path,
    )
    _require(
        item["type"] == "interval_exclusion",
        f"{path}.type",
        "wrong witness type",
    )
    _string(item["function_component"], f"{path}.function_component")
    model = _exact_keys(
        item["affine_model"],
        {"variable_order", "coefficients", "constant"},
        f"{path}.affine_model",
    )
    _require(
        model["variable_order"] == list(AXES),
        f"{path}.affine_model.variable_order",
        "affine variable order mismatch",
    )
    coefficients = _validate_exact_vector(
        model["coefficients"], 3, f"{path}.affine_model.coefficients"
    )
    constant = as_fraction(
        model["constant"], f"{path}.affine_model.constant"
    )
    lower, upper = interval_fractions(item["range"], f"{path}.range")
    _require(
        (lower, upper)
        == _affine_value_range(coefficients, constant, leaf_box),
        f"{path}.range",
        "declared exclusion range does not replay from affine model",
    )
    _require(
        upper < 0 or lower > 0,
        f"{path}.range",
        "exclusion range contains zero",
    )
    _string(item["backend"], f"{path}.backend")
    _digest(
        item["problem_commitment_sha256"],
        f"{path}.problem_commitment_sha256",
    )
    _string(item["model_id"], f"{path}.model_id")
    _digest(item["model_sha256"], f"{path}.model_sha256")
    return item


def _validate_unique_witness(
    witness: Any, leaf_box: dict[str, Any], path: str
) -> dict[str, Any]:
    item = _exact_keys(
        witness,
        {
            "type",
            "candidate_id",
            "operator_box",
            "determinant_range",
            "root_model",
            "backend",
            "problem_commitment_sha256",
            "model_id",
            "model_sha256",
        },
        path,
    )
    _require(
        item["type"] == "interval_newton_inclusion",
        f"{path}.type",
        "wrong witness type",
    )
    _string(item["candidate_id"], f"{path}.candidate_id")
    validate_box(item["operator_box"], f"{path}.operator_box")
    _require(
        interval_strictly_inside(item["operator_box"], leaf_box),
        f"{path}.operator_box",
        "K(B) is not strictly inside B",
    )
    lower, upper = interval_fractions(
        item["determinant_range"], f"{path}.determinant_range"
    )
    _require(
        upper < 0 or lower > 0,
        f"{path}.determinant_range",
        "Jacobian determinant range contains zero",
    )
    model = item["root_model"]
    _require(type(model) is dict, f"{path}.root_model", "expected object")
    kind = model.get("kind")
    if kind == "exact_affine":
        system = _exact_keys(
            model,
            {
                "kind",
                "variable_order",
                "matrix",
                "constant",
                "root",
            },
            f"{path}.root_model",
        )
        _require(
            system["variable_order"] == list(AXES),
            f"{path}.root_model.variable_order",
            "affine variable order mismatch",
        )
        matrix = _validate_exact_matrix(
            system["matrix"], 3, 3, f"{path}.root_model.matrix"
        )
        constant = _validate_exact_vector(
            system["constant"], 3, f"{path}.root_model.constant"
        )
        root = _validate_exact_vector(
            system["root"], 3, f"{path}.root_model.root"
        )
        _require(
            all(
                sum(
                    matrix[row][column] * root[column]
                    for column in range(3)
                )
                + constant[row]
                == 0
                for row in range(3)
            ),
            f"{path}.root_model.root",
            "declared root does not solve exact affine system",
        )
        determinant = _determinant_3(matrix)
        _require(
            (lower, upper) == (determinant, determinant),
            f"{path}.determinant_range",
            "determinant range does not replay from affine Jacobian",
        )
        _require(
            all(
                interval_fractions(item["operator_box"][axis])[0]
                <= root[index]
                <= interval_fractions(item["operator_box"][axis])[1]
                for index, axis in enumerate(AXES)
            ),
            f"{path}.root_model.root",
            "exact root lies outside inclusion operator box",
        )
    elif kind == "separable_quadratic":
        polynomial = _exact_keys(
            model,
            {
                "kind",
                "variable_order",
                "spatial_root",
                "time_coefficients",
                "time_isolating_interval",
                "endpoint_values",
                "derivative_range",
            },
            f"{path}.root_model",
        )
        _require(
            polynomial["variable_order"] == list(AXES),
            f"{path}.root_model.variable_order",
            "polynomial variable order mismatch",
        )
        spatial_root = _validate_exact_vector(
            polynomial["spatial_root"],
            2,
            f"{path}.root_model.spatial_root",
        )
        coefficients = _validate_exact_vector(
            polynomial["time_coefficients"],
            3,
            f"{path}.root_model.time_coefficients",
        )
        time_lower, time_upper = interval_fractions(
            polynomial["time_isolating_interval"],
            f"{path}.root_model.time_isolating_interval",
        )
        endpoint_values = _exact_keys(
            polynomial["endpoint_values"],
            {"lo", "hi"},
            f"{path}.root_model.endpoint_values",
        )
        value_lower = sum(
            coefficient * time_lower**power
            for power, coefficient in enumerate(coefficients)
        )
        value_upper = sum(
            coefficient * time_upper**power
            for power, coefficient in enumerate(coefficients)
        )
        _require(
            as_fraction(
                endpoint_values["lo"],
                f"{path}.root_model.endpoint_values.lo",
            )
            == value_lower
            and as_fraction(
                endpoint_values["hi"],
                f"{path}.root_model.endpoint_values.hi",
            )
            == value_upper,
            f"{path}.root_model.endpoint_values",
            "endpoint values do not replay from polynomial",
        )
        _require(
            value_lower * value_upper < 0,
            f"{path}.root_model.endpoint_values",
            "isolating endpoints do not bracket a root",
        )
        derivative_endpoints = (
            coefficients[1] + 2 * coefficients[2] * time_lower,
            coefficients[1] + 2 * coefficients[2] * time_upper,
        )
        derivative_range = interval_fractions(
            polynomial["derivative_range"],
            f"{path}.root_model.derivative_range",
        )
        expected_derivative = (
            min(derivative_endpoints),
            max(derivative_endpoints),
        )
        _require(
            derivative_range == expected_derivative
            and (
                derivative_range[1] < 0
                or derivative_range[0] > 0
            ),
            f"{path}.root_model.derivative_range",
            "derivative does not certify a unique root",
        )
        _require(
            (lower, upper) == derivative_range,
            f"{path}.determinant_range",
            "determinant range does not replay from polynomial derivative",
        )
        _require(
            all(
                interval_fractions(item["operator_box"][axis])[0]
                <= spatial_root[index]
                <= interval_fractions(item["operator_box"][axis])[1]
                for index, axis in enumerate(("sigma1", "sigma2"))
            )
            and interval_fractions(item["operator_box"]["time"])[0]
            <= time_lower
            <= time_upper
            <= interval_fractions(item["operator_box"]["time"])[1],
            f"{path}.root_model",
            "isolating root box lies outside operator box",
        )
    else:
        raise ProofError(f"{path}.root_model.kind: unknown root model")
    _string(item["backend"], f"{path}.backend")
    _digest(
        item["problem_commitment_sha256"],
        f"{path}.problem_commitment_sha256",
    )
    _string(item["model_id"], f"{path}.model_id")
    _digest(item["model_sha256"], f"{path}.model_sha256")
    return item


def _validate_singular_witness(
    witness: Any, leaf_box: dict[str, Any], path: str
) -> dict[str, Any]:
    item = _exact_keys(
        witness,
        {
            "type",
            "candidate_ids",
            "affine_set",
            "set_certificate_sha256",
            "backend",
            "problem_commitment_sha256",
            "model_id",
            "model_sha256",
        },
        path,
    )
    _require(
        item["type"] == "singular_set_certificate",
        f"{path}.type",
        "wrong witness type",
    )
    candidates = _string_list(item["candidate_ids"], f"{path}.candidate_ids")
    _require(bool(candidates), f"{path}.candidate_ids", "singular set needs candidate")
    _require(
        len(candidates) == len(set(candidates)),
        f"{path}.candidate_ids",
        "duplicate candidate ID",
    )
    digest = _string(
        item["set_certificate_sha256"],
        f"{path}.set_certificate_sha256",
    )
    _require(len(digest) == 64, f"{path}.set_certificate_sha256", "invalid hash")
    _require(
        digest == canonical_sha256(item["affine_set"]),
        f"{path}.set_certificate_sha256",
        "set certificate hash does not bind affine-set content",
    )
    affine_set = _exact_keys(
        item["affine_set"],
        {
            "variable_order",
            "matrix",
            "constant",
            "base_point",
            "null_direction",
            "parameter_interval",
            "declared_rank",
            "declared_dimension",
        },
        f"{path}.affine_set",
    )
    _require(
        affine_set["variable_order"] == list(AXES),
        f"{path}.affine_set.variable_order",
        "affine variable order mismatch",
    )
    matrix = _validate_exact_matrix(
        affine_set["matrix"], 3, 3, f"{path}.affine_set.matrix"
    )
    constant = _validate_exact_vector(
        affine_set["constant"], 3, f"{path}.affine_set.constant"
    )
    base = _validate_exact_vector(
        affine_set["base_point"], 3, f"{path}.affine_set.base_point"
    )
    direction = _validate_exact_vector(
        affine_set["null_direction"],
        3,
        f"{path}.affine_set.null_direction",
    )
    parameter_lower, parameter_upper = interval_fractions(
        affine_set["parameter_interval"],
        f"{path}.affine_set.parameter_interval",
    )
    rank = _integer(
        affine_set["declared_rank"], f"{path}.affine_set.declared_rank"
    )
    dimension = _integer(
        affine_set["declared_dimension"],
        f"{path}.affine_set.declared_dimension",
    )
    _require(
        _exact_matrix_rank(matrix) == rank
        and dimension == 3 - rank
        and dimension > 0,
        f"{path}.affine_set",
        "declared positive dimension does not replay from exact rank",
    )
    _require(
        any(component != 0 for component in direction),
        f"{path}.affine_set.null_direction",
        "null direction must be nonzero",
    )
    _require(
        all(
            sum(
                matrix[row][column] * base[column]
                for column in range(3)
            )
            + constant[row]
            == 0
            and sum(
                matrix[row][column] * direction[column]
                for column in range(3)
            )
            == 0
            for row in range(3)
        ),
        f"{path}.affine_set",
        "base/null parameterization does not solve affine system",
    )
    for parameter in (parameter_lower, parameter_upper):
        point = [
            base[index] + parameter * direction[index]
            for index in range(3)
        ]
        _require(
            all(
                interval_fractions(leaf_box[axis])[0]
                <= point[index]
                <= interval_fractions(leaf_box[axis])[1]
                for index, axis in enumerate(AXES)
            ),
            f"{path}.affine_set.parameter_interval",
            "parameterized set leaves certified leaf box",
        )
    _string(item["backend"], f"{path}.backend")
    _digest(
        item["problem_commitment_sha256"],
        f"{path}.problem_commitment_sha256",
    )
    _string(item["model_id"], f"{path}.model_id")
    _digest(item["model_sha256"], f"{path}.model_sha256")
    return item


def _validate_unresolved_witness(
    witness: Any, path: str
) -> dict[str, Any]:
    item = _exact_keys(
        witness,
        {
            "type",
            "reason_code",
            "event_order_relevant",
            "backend",
            "problem_commitment_sha256",
            "model_id",
            "model_sha256",
        },
        path,
    )
    _require(
        item["type"] == "unresolved",
        f"{path}.type",
        "wrong witness type",
    )
    _string(item["reason_code"], f"{path}.reason_code")
    _boolean(item["event_order_relevant"], f"{path}.event_order_relevant")
    _string(item["backend"], f"{path}.backend")
    _digest(
        item["problem_commitment_sha256"],
        f"{path}.problem_commitment_sha256",
    )
    _string(item["model_id"], f"{path}.model_id")
    _digest(item["model_sha256"], f"{path}.model_sha256")
    return item


def _validate_leaf(
    value: Any, node_box: dict[str, Any], path: str
) -> dict[str, Any]:
    leaf = _exact_keys(
        value,
        {
            "leaf_id",
            "node_id",
            "domain_id",
            "image_id",
            "classification",
            "witness",
        },
        path,
    )
    for name in ("leaf_id", "node_id", "domain_id", "image_id"):
        _string(leaf[name], f"{path}.{name}")
    classification = _string(
        leaf["classification"], f"{path}.classification"
    )
    _require(
        classification in LEAF_CLASSES,
        f"{path}.classification",
        "unknown leaf class",
    )
    if classification == "excluded":
        _validate_exclusion_witness(
            leaf["witness"], node_box, f"{path}.witness"
        )
    elif classification == "unique_root":
        _validate_unique_witness(
            leaf["witness"], node_box, f"{path}.witness"
        )
    elif classification == "certified_singular_cluster":
        _validate_singular_witness(
            leaf["witness"], node_box, f"{path}.witness"
        )
    else:
        _validate_unresolved_witness(leaf["witness"], f"{path}.witness")
    return leaf


def _validate_candidate(value: Any, path: str) -> dict[str, Any]:
    candidate = _exact_keys(
        value,
        {
            "candidate_id",
            "leaf_id",
            "image_id",
            "physical_root_id",
            "time_interval",
        },
        path,
    )
    for name in (
        "candidate_id",
        "leaf_id",
        "image_id",
        "physical_root_id",
    ):
        _string(candidate[name], f"{path}.{name}")
    interval_fractions(candidate["time_interval"], f"{path}.time_interval")
    return candidate


def _validate_quotient(value: Any, path: str) -> dict[str, Any]:
    quotient = _exact_keys(
        value,
        {
            "physical_root_id",
            "candidate_ids",
            "representative_candidate_id",
            "proof_type",
            "seam_equivalence_key",
            "seam_proof",
        },
        path,
    )
    _string(quotient["physical_root_id"], f"{path}.physical_root_id")
    candidates = _string_list(
        quotient["candidate_ids"], f"{path}.candidate_ids"
    )
    _require(bool(candidates), f"{path}.candidate_ids", "empty quotient class")
    _require(
        len(candidates) == len(set(candidates)),
        f"{path}.candidate_ids",
        "duplicate candidate ID",
    )
    representative = _string(
        quotient["representative_candidate_id"],
        f"{path}.representative_candidate_id",
    )
    _require(
        representative in candidates,
        f"{path}.representative_candidate_id",
        "representative is not in quotient class",
    )
    proof_type = _string(quotient["proof_type"], f"{path}.proof_type")
    _require(
        proof_type in ("identity", "seam_equivalence"),
        f"{path}.proof_type",
        "unknown quotient proof",
    )
    if proof_type == "identity":
        _require(
            len(candidates) == 1,
            f"{path}.candidate_ids",
            "identity quotient must be singleton",
        )
        _require(
            quotient["seam_proof"] is None,
            f"{path}.seam_proof",
            "identity quotient cannot carry a seam proof",
        )
    else:
        _require(
            len(candidates) >= 2,
            f"{path}.candidate_ids",
            "seam equivalence needs duplicates",
        )
        proof = _exact_keys(
            quotient["seam_proof"],
            {"base_candidate_id", "lattice_delta_bindings"},
            f"{path}.seam_proof",
        )
        base = _string(
            proof["base_candidate_id"],
            f"{path}.seam_proof.base_candidate_id",
        )
        _require(
            base in candidates,
            f"{path}.seam_proof.base_candidate_id",
            "base candidate is not in quotient class",
        )
        bindings = proof["lattice_delta_bindings"]
        _require(
            type(bindings) is list,
            f"{path}.seam_proof.lattice_delta_bindings",
            "expected array",
        )
        binding_ids: list[str] = []
        for index, binding in enumerate(bindings):
            item = _exact_keys(
                binding,
                {"candidate_id", "image_id", "lattice_delta"},
                f"{path}.seam_proof.lattice_delta_bindings[{index}]",
            )
            binding_ids.append(
                _string(
                    item["candidate_id"],
                    f"{path}.seam_proof.lattice_delta_bindings[{index}].candidate_id",
                )
            )
            _string(
                item["image_id"],
                f"{path}.seam_proof.lattice_delta_bindings[{index}].image_id",
            )
            _require(
                type(item["lattice_delta"]) is list
                and len(item["lattice_delta"]) == 9,
                f"{path}.seam_proof.lattice_delta_bindings[{index}].lattice_delta",
                "expected 9-vector",
            )
            for coordinate, component in enumerate(item["lattice_delta"]):
                _integer(
                    component,
                    f"{path}.seam_proof.lattice_delta_bindings[{index}].lattice_delta[{coordinate}]",
                )
        _require(
            sorted(binding_ids) == sorted(candidates),
            f"{path}.seam_proof.lattice_delta_bindings",
            "bindings must cover quotient candidates exactly once",
        )
        _require(
            len(binding_ids) == len(set(binding_ids)),
            f"{path}.seam_proof.lattice_delta_bindings",
            "duplicate seam binding",
        )
    _string(
        quotient["seam_equivalence_key"],
        f"{path}.seam_equivalence_key",
    )
    return quotient


def _witness_model_payload(
    classification: str, witness: dict[str, Any]
) -> dict[str, Any]:
    """Return only the equation/problem content carried by a leaf witness."""

    if classification == "excluded":
        return {
            "model_kind": "exclusion_affine",
            "model": {
                "function_component": witness["function_component"],
                "affine_model": copy.deepcopy(witness["affine_model"]),
            },
        }
    if classification == "unique_root":
        return {
            "model_kind": "root_system",
            "model": copy.deepcopy(witness["root_model"]),
        }
    if classification == "certified_singular_cluster":
        return {
            "model_kind": "singular_root_system",
            "model": copy.deepcopy(witness["affine_set"]),
        }
    if classification == "unresolved":
        return {
            "model_kind": "unresolved_problem_partition",
            "model": {
                "equation_status": "registered-but-not-resolved",
            },
        }
    raise ProofError(f"$witness: unknown classification {classification!r}")


def _validate_problem_commitment(
    value: Any,
    *,
    images: list[dict[str, Any]],
    domains: list[dict[str, Any]],
    path: str,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    commitment = _exact_keys(
        value,
        {
            "schema_version",
            "authority_mode",
            "fixture_registry_id",
            "equation_family",
            "equation_version",
            "source_state_registry",
            "source_state_sha256",
            "source_registry",
            "source_registry_sha256",
            "source_draw_registry",
            "source_draw_registry_sha256",
            "solver_registry",
            "solver_registry_sha256",
            "metric_registry",
            "metric_sha256",
            "lattice_registry",
            "lattice_sha256",
            "threshold_registry",
            "threshold_registry_sha256",
            "observation_window",
            "observation_window_sha256",
            "function_registry",
            "function_registry_sha256",
            "event_model_registry",
            "event_model_registry_sha256",
            "physical_replay_boundary",
        },
        path,
    )
    _require(
        commitment["schema_version"]
        == PROBLEM_COMMITMENT_SCHEMA_VERSION,
        f"{path}.schema_version",
        "problem commitment schema mismatch",
    )
    _require(
        commitment["authority_mode"] == "pinned_synthetic_fixture",
        f"{path}.authority_mode",
        "coverage fixtures require the pinned synthetic authority mode",
    )
    for name in (
        "fixture_registry_id",
        "equation_family",
        "equation_version",
        "physical_replay_boundary",
    ):
        _string(commitment[name], f"{path}.{name}")

    registry_pairs = (
        ("source_state_registry", "source_state_sha256"),
        ("source_registry", "source_registry_sha256"),
        ("source_draw_registry", "source_draw_registry_sha256"),
        ("solver_registry", "solver_registry_sha256"),
        ("metric_registry", "metric_sha256"),
        ("lattice_registry", "lattice_sha256"),
        ("threshold_registry", "threshold_registry_sha256"),
        ("observation_window", "observation_window_sha256"),
        ("function_registry", "function_registry_sha256"),
        ("event_model_registry", "event_model_registry_sha256"),
    )
    for content_name, digest_name in registry_pairs:
        _digest(commitment[digest_name], f"{path}.{digest_name}")
        _require(
            commitment[digest_name]
            == canonical_sha256(commitment[content_name]),
            f"{path}.{digest_name}",
            f"does not bind {content_name}",
        )

    source_state = _exact_keys(
        commitment["source_state_registry"],
        {
            "schema_version",
            "initial_state",
            "initial_time",
            "initial_rho_affine",
        },
        f"{path}.source_state_registry",
    )
    _string(
        source_state["schema_version"],
        f"{path}.source_state_registry.schema_version",
    )
    _require(
        source_state["initial_state"] == "armed",
        f"{path}.source_state_registry.initial_state",
        "synthetic coverage fixture must start armed",
    )
    as_fraction(
        source_state["initial_time"],
        f"{path}.source_state_registry.initial_time",
    )
    initial_rho = _exact_keys(
        source_state["initial_rho_affine"],
        {"slope", "intercept"},
        f"{path}.source_state_registry.initial_rho_affine",
    )
    as_fraction(
        initial_rho["slope"],
        f"{path}.source_state_registry.initial_rho_affine.slope",
    )
    as_fraction(
        initial_rho["intercept"],
        f"{path}.source_state_registry.initial_rho_affine.intercept",
    )

    source_registry = _exact_keys(
        commitment["source_registry"],
        {
            "schema_version",
            "registry_role",
            "preparation_name",
            "source_draw_registry_sha256",
            "source_state_sha256",
            "validity_predicate_version",
            "redraw_on_invalid",
        },
        f"{path}.source_registry",
    )
    _string(
        source_registry["schema_version"],
        f"{path}.source_registry.schema_version",
    )
    _require(
        source_registry["registry_role"]
        == "canonical-source-registry",
        f"{path}.source_registry.registry_role",
        "unexpected source registry role",
    )
    _string(
        source_registry["preparation_name"],
        f"{path}.source_registry.preparation_name",
    )
    _string(
        source_registry["validity_predicate_version"],
        f"{path}.source_registry.validity_predicate_version",
    )
    _require(
        source_registry["source_draw_registry_sha256"]
        == commitment["source_draw_registry_sha256"]
        and source_registry["source_state_sha256"]
        == commitment["source_state_sha256"],
        f"{path}.source_registry",
        "canonical source registry does not bind draw and state registries",
    )
    _require(
        _boolean(
            source_registry["redraw_on_invalid"],
            f"{path}.source_registry.redraw_on_invalid",
        )
        is False,
        f"{path}.source_registry.redraw_on_invalid",
        "invalid source draws must be retained without redraw",
    )
    source_draw_registry = _exact_keys(
        commitment["source_draw_registry"],
        {
            "schema_version",
            "registry_role",
            "L_A",
            "T_F",
            "L_w",
            "K",
            "E_perp",
            "P_tot",
            "pi_1",
            "pi_2",
            "prng",
        },
        f"{path}.source_draw_registry",
    )
    _string(
        source_draw_registry["schema_version"],
        f"{path}.source_draw_registry.schema_version",
    )
    _require(
        source_draw_registry["registry_role"]
        == "source-substream-seed-input-only",
        f"{path}.source_draw_registry.registry_role",
        "source-draw registry may contain only coefficient-stream inputs",
    )
    for name in ("L_A", "T_F", "L_w", "E_perp"):
        _require(
            as_fraction(
                source_draw_registry[name],
                f"{path}.source_draw_registry.{name}",
            )
            > 0,
            f"{path}.source_draw_registry.{name}",
            "source-draw scale must be positive",
        )
    _require(
        _integer(
            source_draw_registry["K"],
            f"{path}.source_draw_registry.K",
        )
        > 0,
        f"{path}.source_draw_registry.K",
        "mode cutoff must be positive",
    )
    p_tot = source_draw_registry["P_tot"]
    _require(
        type(p_tot) is list and len(p_tot) == 8,
        f"{path}.source_draw_registry.P_tot",
        "target total momentum must have eight components",
    )
    _require(
        all(
            as_fraction(
                component,
                f"{path}.source_draw_registry.P_tot[{index}]",
            )
            == 0
            for index, component in enumerate(p_tot)
        ),
        f"{path}.source_draw_registry.P_tot",
        "synthetic source-draw control fixes zero target momentum",
    )
    for name in ("pi_1", "pi_2"):
        _require(
            as_fraction(
                source_draw_registry[name],
                f"{path}.source_draw_registry.{name}",
            )
            == 0,
            f"{path}.source_draw_registry.{name}",
            "level matching requires zero world-sheet momentum",
        )
    prng = _exact_keys(
        source_draw_registry["prng"],
        {"algorithm", "version", "seed_convention"},
        f"{path}.source_draw_registry.prng",
    )
    for name in ("algorithm", "version", "seed_convention"):
        _string(prng[name], f"{path}.source_draw_registry.prng.{name}")
    solver_registry = _exact_keys(
        commitment["solver_registry"],
        {
            "schema_version",
            "proof_backend",
            "budget_semantics",
            "rank_blind_selection",
        },
        f"{path}.solver_registry",
    )
    _string(
        solver_registry["schema_version"],
        f"{path}.solver_registry.schema_version",
    )
    _require(
        solver_registry["proof_backend"] == SYNTHETIC_PROOF_BACKEND,
        f"{path}.solver_registry.proof_backend",
        "unexpected synthetic proof backend",
    )
    _require(
        solver_registry["budget_semantics"]
        == "deterministic-finite-fixture"
        and solver_registry["rank_blind_selection"] is True,
        f"{path}.solver_registry",
        "solver registry violates fixture contract",
    )

    metric_registry = _exact_keys(
        commitment["metric_registry"],
        {"dimension", "basis", "matrix"},
        f"{path}.metric_registry",
    )
    _require(
        _integer(
            metric_registry["dimension"],
            f"{path}.metric_registry.dimension",
        )
        == 9,
        f"{path}.metric_registry.dimension",
        "target metric dimension must be nine",
    )
    _require(
        metric_registry["basis"] == "registered-target-coordinate-basis",
        f"{path}.metric_registry.basis",
        "metric basis mismatch",
    )
    metric = _validate_exact_matrix(
        metric_registry["matrix"],
        9,
        9,
        f"{path}.metric_registry.matrix",
    )
    _require(
        metric
        == [
            [
                Fraction(1) if row == column else Fraction(0)
                for column in range(9)
            ]
            for row in range(9)
        ],
        f"{path}.metric_registry.matrix",
        "synthetic fixture metric is not the pinned identity metric",
    )

    lattice_registry = _exact_keys(
        commitment["lattice_registry"],
        {"dimension", "images"},
        f"{path}.lattice_registry",
    )
    _require(
        _integer(
            lattice_registry["dimension"],
            f"{path}.lattice_registry.dimension",
        )
        == 9
        and lattice_registry["images"] == images,
        f"{path}.lattice_registry",
        "lattice registry differs from committed image enumeration",
    )

    thresholds = _exact_keys(
        commitment["threshold_registry"],
        {"registry_id", "r_in", "r_out", "injectivity_radius"},
        f"{path}.threshold_registry",
    )
    _string(
        thresholds["registry_id"],
        f"{path}.threshold_registry.registry_id",
    )
    r_in = as_fraction(
        thresholds["r_in"], f"{path}.threshold_registry.r_in"
    )
    r_out = as_fraction(
        thresholds["r_out"], f"{path}.threshold_registry.r_out"
    )
    injectivity = as_fraction(
        thresholds["injectivity_radius"],
        f"{path}.threshold_registry.injectivity_radius",
    )
    _require(
        0 < r_in < r_out < injectivity,
        f"{path}.threshold_registry",
        "require 0<r_in<r_out<injectivity radius",
    )

    observation_lower, observation_upper = interval_fractions(
        commitment["observation_window"],
        f"{path}.observation_window",
    )
    _require(
        observation_lower < observation_upper,
        f"{path}.observation_window",
        "observation window must have positive length",
    )
    for index, domain in enumerate(domains):
        search_lower, search_upper = interval_fractions(
            domain["box"]["time"],
            f"$manifest.initial_domains[{index}].box.time",
        )
        _require(
            observation_lower <= search_lower < search_upper
            <= observation_upper,
            f"{path}.observation_window",
            "search domain lies outside committed observation window",
        )

    function_registry = _exact_keys(
        commitment["function_registry"],
        {"schema_version", "models"},
        f"{path}.function_registry",
    )
    _require(
        function_registry["schema_version"]
        == FUNCTION_REGISTRY_SCHEMA_VERSION,
        f"{path}.function_registry.schema_version",
        "function registry schema mismatch",
    )
    models = function_registry["models"]
    _require(
        type(models) is list and bool(models),
        f"{path}.function_registry.models",
        "function registry must be a nonempty array",
    )
    model_map: dict[str, dict[str, Any]] = {}
    for index, model_value in enumerate(models):
        model_path = f"{path}.function_registry.models[{index}]"
        model = _exact_keys(
            model_value,
            {"model_id", "model_kind", "model", "model_sha256"},
            model_path,
        )
        model_id = _string(model["model_id"], f"{model_path}.model_id")
        _string(model["model_kind"], f"{model_path}.model_kind")
        _digest(model["model_sha256"], f"{model_path}.model_sha256")
        _require(
            model["model_sha256"]
            == canonical_sha256(
                {
                    "model_kind": model["model_kind"],
                    "model": model["model"],
                }
            ),
            f"{model_path}.model_sha256",
            "model hash does not bind typed equation content",
        )
        _require(
            model_id not in model_map,
            f"{model_path}.model_id",
            "duplicate model ID",
        )
        model_map[model_id] = model
    _require(
        [model["model_id"] for model in models] == sorted(model_map),
        f"{path}.function_registry.models",
        "models must be serialized in model-ID order",
    )
    event_registry = _exact_keys(
        commitment["event_model_registry"],
        {"schema_version", "models"},
        f"{path}.event_model_registry",
    )
    _require(
        event_registry["schema_version"]
        == "cyz-brief-0018-event-proof-model-registry-v1",
        f"{path}.event_model_registry.schema_version",
        "event proof-model registry schema mismatch",
    )
    event_models = event_registry["models"]
    _require(
        type(event_models) is list,
        f"{path}.event_model_registry.models",
        "expected an array",
    )
    event_ids: list[str] = []
    for index, event_model_value in enumerate(event_models):
        event_path = f"{path}.event_model_registry.models[{index}]"
        event_model = _exact_keys(
            event_model_value,
            {"model_id", "model_kind", "content_sha256"},
            event_path,
        )
        event_ids.append(
            _string(event_model["model_id"], f"{event_path}.model_id")
        )
        _string(event_model["model_kind"], f"{event_path}.model_kind")
        _digest(
            event_model["content_sha256"],
            f"{event_path}.content_sha256",
        )
    _require(
        event_ids == sorted(event_ids)
        and len(event_ids) == len(set(event_ids)),
        f"{path}.event_model_registry.models",
        "event models must have unique sorted IDs",
    )
    return commitment, model_map


def _verify_split(
    parent: dict[str, Any],
    left: dict[str, Any],
    right: dict[str, Any],
    path: str,
) -> None:
    axis = parent["split_axis"]
    split = as_fraction(parent["split_value"], f"{path}.split_value")
    parent_box = parent["box"]
    left_box = left["box"]
    right_box = right["box"]
    parent_lower, parent_upper = interval_fractions(
        parent_box[axis], f"{path}.box.{axis}"
    )
    _require(
        parent_lower < split < parent_upper,
        f"{path}.split_value",
        "split is not in the strict interior",
    )
    for other_axis in AXES:
        p_interval = interval_fractions(parent_box[other_axis])
        l_interval = interval_fractions(left_box[other_axis])
        r_interval = interval_fractions(right_box[other_axis])
        if other_axis == axis:
            _require(
                l_interval == (p_interval[0], split),
                f"{path}.children[0]",
                "left child does not meet split exactly",
            )
            _require(
                r_interval == (split, p_interval[1]),
                f"{path}.children[1]",
                "right child does not meet split exactly",
            )
        else:
            _require(
                l_interval == p_interval and r_interval == p_interval,
                path,
                "child changed a non-split axis",
            )


def validate_manifest(
    value: Any,
    *,
    expected_problem_commitment_sha256: str | None = None,
) -> dict[str, Any]:
    manifest = _exact_keys(
        value,
        {
            "schema_version",
            "exact_inputs",
            "exact_inputs_sha256",
            "images",
            "initial_domains",
            "nodes",
            "leaves",
            "candidates",
            "quotient_classes",
        },
        "$manifest",
    )
    _require(
        manifest["schema_version"] == COVERAGE_SCHEMA_VERSION,
        "$manifest.schema_version",
        "coverage schema version mismatch",
    )
    input_hash = _string(
        manifest["exact_inputs_sha256"], "$manifest.exact_inputs_sha256"
    )
    _require(len(input_hash) == 64, "$manifest.exact_inputs_sha256", "invalid hash")
    exact_inputs = _exact_keys(
        manifest["exact_inputs"],
        {
            "coordinate_order",
            "images",
            "initial_domains",
            "problem_commitment",
            "problem_commitment_sha256",
        },
        "$manifest.exact_inputs",
    )
    _require(
        exact_inputs["coordinate_order"] == list(AXES),
        "$manifest.exact_inputs.coordinate_order",
        "exact input coordinate order mismatch",
    )
    _require(
        type(exact_inputs["images"]) is list
        and type(exact_inputs["initial_domains"]) is list,
        "$manifest.exact_inputs",
        "exact input images/domains must be arrays",
    )
    problem_commitment_sha256 = _digest(
        exact_inputs["problem_commitment_sha256"],
        "$manifest.exact_inputs.problem_commitment_sha256",
    )
    _require(
        problem_commitment_sha256
        == canonical_sha256(exact_inputs["problem_commitment"]),
        "$manifest.exact_inputs.problem_commitment_sha256",
        "problem commitment hash does not bind its content",
    )
    if expected_problem_commitment_sha256 is not None:
        _digest(
            expected_problem_commitment_sha256,
            "$expected_problem_commitment_sha256",
        )
        _require(
            problem_commitment_sha256
            == expected_problem_commitment_sha256,
            "$manifest.exact_inputs.problem_commitment_sha256",
            "problem commitment differs from the external pinned registry",
        )
    _require(
        input_hash == canonical_sha256(exact_inputs),
        "$manifest.exact_inputs_sha256",
        "exact input hash does not bind problem manifest",
    )

    images = manifest["images"]
    domains = manifest["initial_domains"]
    nodes = manifest["nodes"]
    leaves = manifest["leaves"]
    candidates = manifest["candidates"]
    quotients = manifest["quotient_classes"]
    for name, items in (
        ("images", images),
        ("initial_domains", domains),
        ("nodes", nodes),
        ("leaves", leaves),
        ("candidates", candidates),
        ("quotient_classes", quotients),
    ):
        _require(type(items) is list, f"$manifest.{name}", "expected array")
    _require(
        exact_inputs["images"] == images
        and exact_inputs["initial_domains"] == domains,
        "$manifest.exact_inputs",
        "active image/domain cover differs from committed exact inputs",
    )

    image_map: dict[str, dict[str, Any]] = {}
    for index, image in enumerate(images):
        parsed = _validate_image(image, f"$manifest.images[{index}]")
        image_id = parsed["image_id"]
        _require(image_id not in image_map, f"$manifest.images[{index}].image_id", "duplicate image ID")
        image_map[image_id] = parsed
    _require(bool(image_map), "$manifest.images", "at least one image is required")

    domain_map: dict[str, dict[str, Any]] = {}
    for index, domain in enumerate(domains):
        parsed = _validate_domain(
            domain, f"$manifest.initial_domains[{index}]"
        )
        domain_id = parsed["domain_id"]
        _require(domain_id not in domain_map, f"$manifest.initial_domains[{index}].domain_id", "duplicate domain ID")
        _require(parsed["image_id"] in image_map, f"$manifest.initial_domains[{index}].image_id", "unknown image")
        domain_map[domain_id] = parsed
    _require(bool(domain_map), "$manifest.initial_domains", "at least one domain is required")
    problem_commitment, registered_models = _validate_problem_commitment(
        exact_inputs["problem_commitment"],
        images=images,
        domains=domains,
        path="$manifest.exact_inputs.problem_commitment",
    )

    node_map: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        parsed = _validate_node(node, f"$manifest.nodes[{index}]")
        node_id = parsed["node_id"]
        _require(node_id not in node_map, f"$manifest.nodes[{index}].node_id", "duplicate node ID")
        _require(parsed["domain_id"] in domain_map, f"$manifest.nodes[{index}].domain_id", "unknown domain")
        node_map[node_id] = parsed

    leaf_by_id_raw: dict[str, dict[str, Any]] = {}
    for index, leaf in enumerate(leaves):
        _require(type(leaf) is dict, f"$manifest.leaves[{index}]", "expected object")
        leaf_id = _string(leaf.get("leaf_id"), f"$manifest.leaves[{index}].leaf_id")
        _require(leaf_id not in leaf_by_id_raw, f"$manifest.leaves[{index}].leaf_id", "duplicate leaf ID")
        leaf_by_id_raw[leaf_id] = leaf

    reached_nodes: set[str] = set()
    reached_leaves: set[str] = set()

    def walk(node_id: str, domain_id: str, ancestry: set[str]) -> None:
        _require(node_id in node_map, "$manifest.nodes", f"missing node {node_id}")
        _require(node_id not in ancestry, f"$manifest.nodes.{node_id}", "coverage tree cycle")
        _require(node_id not in reached_nodes, f"$manifest.nodes.{node_id}", "node reached more than once")
        node = node_map[node_id]
        _require(node["domain_id"] == domain_id, f"$manifest.nodes.{node_id}.domain_id", "node crosses domains")
        reached_nodes.add(node_id)
        if node["kind"] == "split":
            left_id, right_id = node["children"]
            _require(left_id in node_map and right_id in node_map, f"$manifest.nodes.{node_id}.children", "missing split child")
            _verify_split(
                node,
                node_map[left_id],
                node_map[right_id],
                f"$manifest.nodes.{node_id}",
            )
            walk(left_id, domain_id, ancestry | {node_id})
            walk(right_id, domain_id, ancestry | {node_id})
        else:
            leaf_id = node["leaf_id"]
            _require(leaf_id in leaf_by_id_raw, f"$manifest.nodes.{node_id}.leaf_id", "leaf node lacks leaf record")
            leaf = _validate_leaf(
                leaf_by_id_raw[leaf_id],
                node["box"],
                f"$manifest.leaves.{leaf_id}",
            )
            _require(leaf["node_id"] == node_id, f"$manifest.leaves.{leaf_id}.node_id", "leaf points to wrong node")
            _require(leaf["domain_id"] == domain_id, f"$manifest.leaves.{leaf_id}.domain_id", "leaf points to wrong domain")
            _require(
                leaf["image_id"] == domain_map[domain_id]["image_id"],
                f"$manifest.leaves.{leaf_id}.image_id",
                "leaf image disagrees with domain",
            )
            reached_leaves.add(leaf_id)

    for domain_id, domain in domain_map.items():
        root_id = domain["root_node_id"]
        _require(root_id in node_map, f"$manifest.initial_domains.{domain_id}.root_node_id", "missing root node")
        _require(
            box_equal(domain["box"], node_map[root_id]["box"]),
            f"$manifest.initial_domains.{domain_id}.box",
            "root node does not cover the initial domain",
        )
        walk(root_id, domain_id, set())

    _require(
        reached_nodes == set(node_map),
        "$manifest.nodes",
        "orphan or deleted coverage-tree node",
    )
    _require(
        reached_leaves == set(leaf_by_id_raw),
        "$manifest.leaves",
        "leaf records do not exactly match reachable leaf nodes",
    )
    referenced_model_ids: list[str] = []
    for leaf_id, leaf in leaf_by_id_raw.items():
        witness = leaf["witness"]
        witness_path = f"$manifest.leaves.{leaf_id}.witness"
        _require(
            witness["problem_commitment_sha256"]
            == problem_commitment_sha256,
            f"{witness_path}.problem_commitment_sha256",
            "leaf witness is not bound to the committed problem",
        )
        model_id = witness["model_id"]
        _require(
            model_id in registered_models,
            f"{witness_path}.model_id",
            "leaf witness references an unknown registered model",
        )
        registered = registered_models[model_id]
        payload = _witness_model_payload(
            leaf["classification"], witness
        )
        _require(
            registered["model_kind"] == payload["model_kind"]
            and registered["model"] == payload["model"],
            witness_path,
            "leaf proof model differs from the externally committed fixture model",
        )
        _require(
            witness["model_sha256"]
            == registered["model_sha256"]
            == canonical_sha256(payload),
            f"{witness_path}.model_sha256",
            "leaf model digest differs from the committed function registry",
        )
        referenced_model_ids.append(model_id)
    reserved_suffixes = {
        "initial-armed-rho",
        "outer-overshoot-rho",
        "global-no-entry-rho",
    }
    unreferenced_models = set(registered_models) - set(
        referenced_model_ids
    )
    _require(
        len(referenced_model_ids) == len(set(referenced_model_ids))
        and set(referenced_model_ids).issubset(registered_models)
        and {
            model_id.rsplit("::", 1)[-1]
            for model_id in unreferenced_models
        }
        == reserved_suffixes,
        "$manifest.exact_inputs.problem_commitment.function_registry",
        "registered leaf models and witness references do not close",
    )

    parsed_candidates: dict[str, dict[str, Any]] = {}
    for index, candidate in enumerate(candidates):
        parsed = _validate_candidate(
            candidate, f"$manifest.candidates[{index}]"
        )
        candidate_id = parsed["candidate_id"]
        _require(candidate_id not in parsed_candidates, f"$manifest.candidates[{index}].candidate_id", "duplicate candidate ID")
        _require(parsed["leaf_id"] in leaf_by_id_raw, f"$manifest.candidates[{index}].leaf_id", "unknown leaf")
        leaf = leaf_by_id_raw[parsed["leaf_id"]]
        _require(
            leaf["classification"]
            in ("unique_root", "certified_singular_cluster"),
            f"$manifest.candidates[{index}].leaf_id",
            "candidate is not backed by a root leaf",
        )
        _require(parsed["image_id"] == leaf["image_id"], f"$manifest.candidates[{index}].image_id", "candidate image mismatch")
        node_box = node_map[leaf["node_id"]]["box"]
        candidate_time = interval_fractions(
            parsed["time_interval"],
            f"$manifest.candidates[{index}].time_interval",
        )
        leaf_time = interval_fractions(
            node_box["time"],
            f"$manifest.nodes.{leaf['node_id']}.box.time",
        )
        _require(
            leaf_time[0] <= candidate_time[0]
            and candidate_time[1] <= leaf_time[1],
            f"$manifest.candidates[{index}].time_interval",
            "candidate time is outside its certified leaf",
        )
        if leaf["classification"] == "unique_root":
            operator_time = interval_fractions(
                leaf["witness"]["operator_box"]["time"],
                f"$manifest.leaves.{leaf['leaf_id']}.witness.operator_box.time",
            )
            _require(
                operator_time[0] <= candidate_time[0]
                and candidate_time[1] <= operator_time[1],
                f"$manifest.candidates[{index}].time_interval",
                "candidate time is outside its inclusion operator box",
            )
            model = leaf["witness"]["root_model"]
            if model["kind"] == "exact_affine":
                exact_root = [
                    as_fraction(
                        component,
                        f"$manifest.leaves.{leaf['leaf_id']}.witness.root_model.root[{axis}]",
                    )
                    for axis, component in enumerate(model["root"])
                ]
                _require(
                    candidate_time[0]
                    <= exact_root[2]
                    <= candidate_time[1],
                    f"$manifest.candidates[{index}].time_interval",
                    "candidate time interval excludes exact affine root",
                )
            else:
                _require(
                    candidate_time
                    == interval_fractions(
                        model["time_isolating_interval"]
                    ),
                    f"$manifest.candidates[{index}].time_interval",
                    "candidate time must equal polynomial isolating interval",
                )
        parsed_candidates[candidate_id] = parsed

    witness_candidates: list[str] = []
    for leaf in leaf_by_id_raw.values():
        if leaf["classification"] == "unique_root":
            witness_candidates.append(leaf["witness"]["candidate_id"])
        elif leaf["classification"] == "certified_singular_cluster":
            witness_candidates.extend(leaf["witness"]["candidate_ids"])
    _require(
        sorted(witness_candidates) == sorted(parsed_candidates)
        and len(witness_candidates) == len(set(witness_candidates)),
        "$manifest.candidates",
        "candidate records do not match leaf witnesses one-to-one",
    )
    for candidate_id, candidate in parsed_candidates.items():
        leaf = leaf_by_id_raw[candidate["leaf_id"]]
        declared = (
            [leaf["witness"]["candidate_id"]]
            if leaf["classification"] == "unique_root"
            else leaf["witness"]["candidate_ids"]
        )
        _require(
            candidate_id in declared,
            f"$manifest.candidates.{candidate_id}.leaf_id",
            "candidate leaf does not witness this candidate",
        )

    parsed_quotients: list[dict[str, Any]] = []
    quotient_candidate_ids: list[str] = []
    physical_root_ids: set[str] = set()
    for index, quotient in enumerate(quotients):
        parsed = _validate_quotient(
            quotient, f"$manifest.quotient_classes[{index}]"
        )
        _require(parsed["physical_root_id"] not in physical_root_ids, f"$manifest.quotient_classes[{index}].physical_root_id", "duplicate physical root class")
        physical_root_ids.add(parsed["physical_root_id"])
        for candidate_id in parsed["candidate_ids"]:
            _require(candidate_id in parsed_candidates, f"$manifest.quotient_classes[{index}].candidate_ids", "unknown candidate")
            candidate = parsed_candidates[candidate_id]
            _require(
                candidate["physical_root_id"] == parsed["physical_root_id"],
                f"$manifest.quotient_classes[{index}].physical_root_id",
                "candidate physical-root ID mismatch",
            )
            image = image_map[candidate["image_id"]]
            _require(
                image["seam_equivalence_key"]
                == parsed["seam_equivalence_key"],
                f"$manifest.quotient_classes[{index}].seam_equivalence_key",
                "image lacks the declared seam equivalence",
            )
            quotient_candidate_ids.append(candidate_id)
        if parsed["proof_type"] == "seam_equivalence":
            proof = parsed["seam_proof"]
            base_candidate = parsed_candidates[proof["base_candidate_id"]]
            base_image = image_map[base_candidate["image_id"]]
            binding_map = {
                row["candidate_id"]: row
                for row in proof["lattice_delta_bindings"]
            }
            for candidate_id in parsed["candidate_ids"]:
                candidate = parsed_candidates[candidate_id]
                image = image_map[candidate["image_id"]]
                binding = binding_map[candidate_id]
                _require(
                    binding["image_id"] == candidate["image_id"],
                    f"$manifest.quotient_classes[{index}].seam_proof",
                    "seam binding image does not match candidate",
                )
                expected_delta = [
                    int(component) - int(base_component)
                    for component, base_component in zip(
                        image["lattice_vector"],
                        base_image["lattice_vector"],
                    )
                ]
                _require(
                    binding["lattice_delta"] == expected_delta,
                    f"$manifest.quotient_classes[{index}].seam_proof",
                    "lattice delta does not replay from image manifest",
                )
                base_leaf = leaf_by_id_raw[base_candidate["leaf_id"]]
                candidate_leaf = leaf_by_id_raw[candidate["leaf_id"]]
                _require(
                    base_leaf["classification"] == "unique_root"
                    and candidate_leaf["classification"] == "unique_root",
                    f"$manifest.quotient_classes[{index}]",
                    "seam quotient fixture requires isolated roots",
                )
                base_model = base_leaf["witness"]["root_model"]
                candidate_model = candidate_leaf["witness"]["root_model"]
                _require(
                    base_model["kind"] == candidate_model["kind"],
                    f"$manifest.quotient_classes[{index}].seam_proof",
                    "seam candidates use incompatible root models",
                )
                if base_model["kind"] == "exact_affine":
                    base_root = [
                        as_fraction(component)
                        for component in base_model["root"]
                    ]
                    candidate_root = [
                        as_fraction(component)
                        for component in candidate_model["root"]
                    ]
                    equivalent = candidate_root == base_root
                else:
                    equivalent = (
                        canonical_sha256(candidate_model)
                        == canonical_sha256(base_model)
                    )
                _require(
                    equivalent,
                    f"$manifest.quotient_classes[{index}].seam_proof",
                    "seam-equivalent candidates have different root proofs",
                )
        parsed_quotients.append(parsed)
    _require(
        len(quotient_candidate_ids) == len(set(quotient_candidate_ids)),
        "$manifest.quotient_classes",
        "candidate appears in more than one quotient class",
    )
    _require(
        set(quotient_candidate_ids) == set(parsed_candidates),
        "$manifest.quotient_classes",
        "quotient classes do not partition all candidates",
    )
    return manifest


def validate_coverage_certificate(
    value: Any,
    *,
    expected_problem_commitment_sha256: str | None = None,
) -> dict[str, Any]:
    certificate = _exact_keys(
        value,
        {
            "certificate_id",
            "manifest",
            "manifest_sha256",
            "leaf_counts",
            "node_count",
            "image_count",
            "domain_count",
            "candidate_count",
            "physical_root_count",
        },
        "$coverage",
    )
    _string(certificate["certificate_id"], "$coverage.certificate_id")
    manifest = validate_manifest(
        certificate["manifest"],
        expected_problem_commitment_sha256=(
            expected_problem_commitment_sha256
        ),
    )
    declared_hash = _string(
        certificate["manifest_sha256"], "$coverage.manifest_sha256"
    )
    _require(len(declared_hash) == 64, "$coverage.manifest_sha256", "invalid hash")
    _require(
        declared_hash == canonical_sha256(manifest),
        "$coverage.manifest_sha256",
        "content hash does not match replayed manifest",
    )
    counts = _exact_keys(
        certificate["leaf_counts"],
        set(LEAF_CLASSES),
        "$coverage.leaf_counts",
    )
    recomputed_counts = {name: 0 for name in LEAF_CLASSES}
    for leaf in manifest["leaves"]:
        recomputed_counts[leaf["classification"]] += 1
    for name in LEAF_CLASSES:
        _integer(counts[name], f"$coverage.leaf_counts.{name}")
    _require(
        counts == recomputed_counts,
        "$coverage.leaf_counts",
        "leaf counts do not match replayed manifest",
    )
    for field, rows in (
        ("node_count", manifest["nodes"]),
        ("image_count", manifest["images"]),
        ("domain_count", manifest["initial_domains"]),
        ("candidate_count", manifest["candidates"]),
        ("physical_root_count", manifest["quotient_classes"]),
    ):
        declared = _integer(certificate[field], f"$coverage.{field}")
        _require(
            declared == len(rows),
            f"$coverage.{field}",
            "declared count does not match replayed manifest",
        )
    return certificate


def problem_commitment_sha256(certificate: dict[str, Any]) -> str:
    validate_coverage_certificate(certificate)
    return certificate["manifest"]["exact_inputs"][
        "problem_commitment_sha256"
    ]


def manifest_maps(
    certificate: dict[str, Any],
) -> dict[str, Any]:
    validate_coverage_certificate(certificate)
    manifest = certificate["manifest"]
    return {
        "images": {row["image_id"]: row for row in manifest["images"]},
        "domains": {
            row["domain_id"]: row for row in manifest["initial_domains"]
        },
        "nodes": {row["node_id"]: row for row in manifest["nodes"]},
        "leaves": {row["leaf_id"]: row for row in manifest["leaves"]},
        "candidates": {
            row["candidate_id"]: row for row in manifest["candidates"]
        },
        "quotients": {
            row["physical_root_id"]: row
            for row in manifest["quotient_classes"]
        },
    }


def physical_representative_candidate_ids(
    certificate: dict[str, Any],
) -> list[str]:
    validate_coverage_certificate(certificate)
    return sorted(
        row["representative_candidate_id"]
        for row in certificate["manifest"]["quotient_classes"]
    )


def candidate_certified_time(
    certificate: dict[str, Any], candidate_id: str
) -> Fraction | None:
    """Return an exact proof-derived time, or ``None`` for an enclosure."""

    maps = manifest_maps(certificate)
    _require(
        candidate_id in maps["candidates"],
        "$coverage",
        f"unknown candidate {candidate_id}",
    )
    candidate = maps["candidates"][candidate_id]
    leaf = maps["leaves"][candidate["leaf_id"]]
    if leaf["classification"] == "unique_root":
        model = leaf["witness"]["root_model"]
        if model["kind"] == "exact_affine":
            return as_fraction(model["root"][2])
        return None
    if leaf["classification"] == "certified_singular_cluster":
        affine_set = leaf["witness"]["affine_set"]
        direction = [
            as_fraction(component)
            for component in affine_set["null_direction"]
        ]
        if direction[2] == 0:
            return as_fraction(affine_set["base_point"][2])
    return None


def candidate_certified_coordinates(
    certificate: dict[str, Any], candidate_id: str
) -> tuple[Fraction, Fraction, Fraction | None]:
    """Return proof-derived spatial coordinates and optional exact time."""

    maps = manifest_maps(certificate)
    candidate = maps["candidates"][candidate_id]
    leaf = maps["leaves"][candidate["leaf_id"]]
    _require(
        leaf["classification"] == "unique_root",
        "$coverage",
        "scalar representative requires a unique-root leaf",
    )
    model = leaf["witness"]["root_model"]
    if model["kind"] == "exact_affine":
        root = tuple(as_fraction(component) for component in model["root"])
        return root[0], root[1], root[2]
    spatial = tuple(
        as_fraction(component) for component in model["spatial_root"]
    )
    return spatial[0], spatial[1], None


def unresolved_leaf_ids(
    certificate: dict[str, Any], *, event_order_relevant_only: bool = False
) -> list[str]:
    validate_coverage_certificate(certificate)
    result: list[str] = []
    for leaf in certificate["manifest"]["leaves"]:
        if leaf["classification"] != "unresolved":
            continue
        if (
            event_order_relevant_only
            and not leaf["witness"]["event_order_relevant"]
        ):
            continue
        result.append(leaf["leaf_id"])
    return sorted(result)


def image_manifest_sha256(certificate: dict[str, Any]) -> str:
    validate_coverage_certificate(certificate)
    return canonical_sha256(certificate["manifest"]["images"])


def _certificate(
    certificate_id: str, manifest: dict[str, Any]
) -> dict[str, Any]:
    """Attach replayed content hashes and counts to a manifest."""

    leaf_counts = {name: 0 for name in LEAF_CLASSES}
    for leaf in manifest["leaves"]:
        leaf_counts[leaf["classification"]] += 1
    return {
        "certificate_id": certificate_id,
        "manifest": manifest,
        "manifest_sha256": canonical_sha256(manifest),
        "leaf_counts": leaf_counts,
        "node_count": len(manifest["nodes"]),
        "image_count": len(manifest["images"]),
        "domain_count": len(manifest["initial_domains"]),
        "candidate_count": len(manifest["candidates"]),
        "physical_root_count": len(manifest["quotient_classes"]),
    }


def _exact_inputs(
    images: list[dict[str, Any]],
    domains: list[dict[str, Any]],
    leaves: list[dict[str, Any]],
    *,
    fixture_registry_id: str,
    observation_window: tuple[Fraction, Fraction] = (
        Fraction(0),
        Fraction(4),
    ),
) -> dict[str, Any]:
    function_models: list[dict[str, Any]] = []
    for leaf in sorted(leaves, key=lambda row: row["leaf_id"]):
        payload = _witness_model_payload(
            leaf["classification"], leaf["witness"]
        )
        model_id = f"{fixture_registry_id}::{leaf['leaf_id']}"
        function_models.append(
            {
                "model_id": model_id,
                "model_kind": payload["model_kind"],
                "model": payload["model"],
                "model_sha256": canonical_sha256(payload),
            }
        )
    registered_event_models = {
        "initial-armed-rho": {
            "model_kind": "rho_affine",
            "model": {
                "observable": "rho=sqrt(2F_min)",
                "time_domain": "initial_time",
                "rho_affine": {
                    "slope": dyadic(0),
                    "intercept": dyadic(2),
                },
            },
        },
        "outer-overshoot-rho": {
            "model_kind": "rho_affine",
            "model": {
                "observable": "rho=sqrt(2F_min)",
                "time_domain": "registered-post-boundary-interval",
                "rho_affine": {
                    "slope": dyadic(0),
                    "intercept": dyadic(5, 1),
                },
            },
        },
        "global-no-entry-rho": {
            "model_kind": "rho_affine",
            "model": {
                "observable": "rho=sqrt(2F_min)",
                "time_domain": "all_real",
                "rho_affine": {
                    "slope": dyadic(0),
                    "intercept": dyadic(2),
                },
            },
        },
    }
    for suffix, payload in registered_event_models.items():
        function_models.append(
            {
                "model_id": f"{fixture_registry_id}::{suffix}",
                "model_kind": payload["model_kind"],
                "model": payload["model"],
                "model_sha256": canonical_sha256(payload),
            }
        )
    function_models.sort(key=lambda row: row["model_id"])
    function_registry = {
        "schema_version": FUNCTION_REGISTRY_SCHEMA_VERSION,
        "models": function_models,
    }
    source_state_registry = {
        "schema_version": "cyz-brief-0018-synthetic-source-state-v1",
        "initial_state": "armed",
        "initial_time": dyadic(0),
        "initial_rho_affine": {
            "slope": dyadic(0),
            "intercept": dyadic(2),
        },
    }
    source_draw_registry = {
        "schema_version": "cyz-brief-0018-source-draw-registry-v2",
        "registry_role": "source-substream-seed-input-only",
        # This is a software/measure audit cell, not a physical selection.
        "L_A": dyadic(8),
        "T_F": dyadic(1),
        "L_w": dyadic(4),
        "K": 1,
        "E_perp": dyadic(1),
        "P_tot": [dyadic(0) for _ in range(8)],
        "pi_1": dyadic(0),
        "pi_2": dyadic(0),
        "prng": {
            "algorithm": "exact-synthetic-no-random-draw",
            "version": "v1",
            "seed_convention": "fixture-registry-id",
        },
    }
    source_registry = {
        "schema_version": "cyz-brief-0018-canonical-source-registry-v2",
        "registry_role": "canonical-source-registry",
        "preparation_name": "synthetic-software-measure-audit-cell",
        "source_draw_registry_sha256": canonical_sha256(
            source_draw_registry
        ),
        "source_state_sha256": canonical_sha256(
            source_state_registry
        ),
        "validity_predicate_version": (
            "brief-0018-source-validity-v1"
        ),
        "redraw_on_invalid": False,
    }
    solver_registry = {
        "schema_version": "cyz-brief-0018-synthetic-solver-registry-v1",
        "proof_backend": SYNTHETIC_PROOF_BACKEND,
        "budget_semantics": "deterministic-finite-fixture",
        "rank_blind_selection": True,
    }
    metric_registry = {
        "dimension": 9,
        "basis": "registered-target-coordinate-basis",
        "matrix": [
            [
                dyadic(1 if row == column else 0)
                for column in range(9)
            ]
            for row in range(9)
        ],
    }
    lattice_registry = {
        "dimension": 9,
        "images": copy.deepcopy(images),
    }
    threshold_registry = {
        "registry_id": "hysteresis-r1-r2",
        "r_in": dyadic(1),
        "r_out": dyadic(2),
        "injectivity_radius": dyadic(3),
    }
    committed_observation_window = exact_interval(*observation_window)
    event_model_registry = {
        "schema_version": (
            "cyz-brief-0018-event-proof-model-registry-v1"
        ),
        "models": [],
    }
    problem_commitment = {
        "schema_version": PROBLEM_COMMITMENT_SCHEMA_VERSION,
        "authority_mode": "pinned_synthetic_fixture",
        "fixture_registry_id": fixture_registry_id,
        "equation_family": "typed-exact-synthetic-event-control",
        "equation_version": "v1",
        "source_state_registry": source_state_registry,
        "source_state_sha256": canonical_sha256(source_state_registry),
        "source_registry": source_registry,
        "source_registry_sha256": canonical_sha256(source_registry),
        "source_draw_registry": source_draw_registry,
        "source_draw_registry_sha256": canonical_sha256(
            source_draw_registry
        ),
        "solver_registry": solver_registry,
        "solver_registry_sha256": canonical_sha256(solver_registry),
        "metric_registry": metric_registry,
        "metric_sha256": canonical_sha256(metric_registry),
        "lattice_registry": lattice_registry,
        "lattice_sha256": canonical_sha256(lattice_registry),
        "threshold_registry": threshold_registry,
        "threshold_registry_sha256": canonical_sha256(
            threshold_registry
        ),
        "observation_window": committed_observation_window,
        "observation_window_sha256": canonical_sha256(
            committed_observation_window
        ),
        "function_registry": function_registry,
        "function_registry_sha256": canonical_sha256(
            function_registry
        ),
        "event_model_registry": event_model_registry,
        "event_model_registry_sha256": canonical_sha256(
            event_model_registry
        ),
        "physical_replay_boundary": (
            "synthetic models replay here; physical equations require "
            "the independent Brief 0019 replayer"
        ),
    }
    commitment_sha256 = canonical_sha256(problem_commitment)
    model_map = {row["model_id"]: row for row in function_models}
    for leaf in leaves:
        model_id = f"{fixture_registry_id}::{leaf['leaf_id']}"
        leaf["witness"].update(
            {
                "problem_commitment_sha256": commitment_sha256,
                "model_id": model_id,
                "model_sha256": model_map[model_id][
                    "model_sha256"
                ],
            }
        )
    return {
        "coordinate_order": list(AXES),
        "images": copy.deepcopy(images),
        "initial_domains": copy.deepcopy(domains),
        "problem_commitment": problem_commitment,
        "problem_commitment_sha256": commitment_sha256,
    }


def _image(
    index: int, *, seam_key: str | None = None
) -> dict[str, Any]:
    lattice = [0] * 9
    lattice[0] = index
    return {
        "image_id": f"image-{index}",
        "lattice_vector": lattice,
        "physical_image_key": f"physical-image-{index}",
        "seam_equivalence_key": seam_key or f"seam-{index}",
    }


def _root_domain_rows(
    index: int,
    *,
    candidate_id: str | None,
    physical_root_id: str | None,
    candidate_time: tuple[Fraction, Fraction] = (
        Fraction(3, 4),
        Fraction(3, 4),
    ),
    unresolved: bool = False,
    seam_key: str | None = None,
    time_domain: tuple[Fraction, Fraction] = (
        Fraction(0),
        Fraction(4),
    ),
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any] | None,
    dict[str, Any] | None,
]:
    domain_id = f"domain-{index}"
    root_id = f"node-{index}-root"
    left_id = f"node-{index}-left"
    right_id = f"node-{index}-right"
    left_leaf_id = f"leaf-{index}-excluded"
    right_leaf_id = (
        f"leaf-{index}-unresolved"
        if unresolved
        else (
            f"leaf-{index}-root"
            if candidate_id is not None
            else f"leaf-{index}-excluded-right"
        )
    )
    _require(
        time_domain[0] == 0 and Fraction(1, 2) < time_domain[1],
        "$builder.time_domain",
        "fixture time domain must contain the split at 1/2",
    )
    whole = exact_box((0, 1), (0, 1), time_domain)
    left_box = exact_box((0, 1), (0, 1), (0, Fraction(1, 2)))
    right_box = exact_box(
        (0, 1), (0, 1), (Fraction(1, 2), time_domain[1])
    )
    domain = {
        "domain_id": domain_id,
        "image_id": f"image-{index}",
        "root_node_id": root_id,
        "box": whole,
    }
    nodes = [
        {
            "node_id": root_id,
            "domain_id": domain_id,
            "kind": "split",
            "box": whole,
            "split_axis": "time",
            "split_value": dyadic(1, 1),
            "children": [left_id, right_id],
            "leaf_id": None,
        },
        {
            "node_id": left_id,
            "domain_id": domain_id,
            "kind": "leaf",
            "box": left_box,
            "split_axis": None,
            "split_value": None,
            "children": [],
            "leaf_id": left_leaf_id,
        },
        {
            "node_id": right_id,
            "domain_id": domain_id,
            "kind": "leaf",
            "box": right_box,
            "split_axis": None,
            "split_value": None,
            "children": [],
            "leaf_id": right_leaf_id,
        },
    ]
    leaves = [
        {
            "leaf_id": left_leaf_id,
            "node_id": left_id,
            "domain_id": domain_id,
            "image_id": f"image-{index}",
            "classification": "excluded",
            "witness": {
                "type": "interval_exclusion",
                "function_component": "F-r^2/2",
                "affine_model": {
                    "variable_order": list(AXES),
                    "coefficients": [dyadic(0)] * 3,
                    "constant": dyadic(1),
                },
                "range": exact_interval(1, 1),
                "backend": SYNTHETIC_PROOF_BACKEND,
            },
        }
    ]
    candidate: dict[str, Any] | None = None
    quotient: dict[str, Any] | None = None
    if unresolved:
        leaves.append(
            {
                "leaf_id": right_leaf_id,
                "node_id": right_id,
                "domain_id": domain_id,
                "image_id": f"image-{index}",
                "classification": "unresolved",
                "witness": {
                    "type": "unresolved",
                    "reason_code": "possible_earlier_root",
                    "event_order_relevant": True,
                    "backend": SYNTHETIC_PROOF_BACKEND,
                },
            }
        )
    elif candidate_id is None:
        leaves.append(
            {
                "leaf_id": right_leaf_id,
                "node_id": right_id,
                "domain_id": domain_id,
                "image_id": f"image-{index}",
                "classification": "excluded",
                "witness": {
                    "type": "interval_exclusion",
                    "function_component": "F-r^2/2",
                    "affine_model": {
                        "variable_order": list(AXES),
                        "coefficients": [dyadic(0)] * 3,
                        "constant": dyadic(2),
                    },
                    "range": exact_interval(2, 2),
                    "backend": SYNTHETIC_PROOF_BACKEND,
                },
            }
        )
    else:
        operator_box = exact_box(
            (Fraction(1, 4), Fraction(3, 4)),
            (Fraction(1, 4), Fraction(3, 4)),
            (Fraction(5, 8), Fraction(7, 8)),
        )
        if candidate_time[0] == candidate_time[1]:
            time_root = candidate_time[0]
            root_model = {
                "kind": "exact_affine",
                "variable_order": list(AXES),
                "matrix": [
                    [dyadic(1), dyadic(0), dyadic(0)],
                    [dyadic(0), dyadic(1), dyadic(0)],
                    [dyadic(0), dyadic(0), dyadic(-1)],
                ],
                "constant": [
                    dyadic(-1, 1),
                    dyadic(-1, 1),
                    dyadic_from_fraction(time_root),
                ],
                "root": [
                    dyadic(1, 1),
                    dyadic(1, 1),
                    dyadic_from_fraction(time_root),
                ],
            }
            determinant_range = exact_interval(-1, -1)
        else:
            midpoint = (candidate_time[0] + candidate_time[1]) / 2
            coefficients = (-midpoint * midpoint, Fraction(0), Fraction(1))
            endpoint_values = (
                sum(
                    coefficient * candidate_time[0] ** power
                    for power, coefficient in enumerate(coefficients)
                ),
                sum(
                    coefficient * candidate_time[1] ** power
                    for power, coefficient in enumerate(coefficients)
                ),
            )
            derivative_range = (
                2 * candidate_time[0],
                2 * candidate_time[1],
            )
            root_model = {
                "kind": "separable_quadratic",
                "variable_order": list(AXES),
                "spatial_root": [dyadic(1, 1), dyadic(1, 1)],
                "time_coefficients": [
                    dyadic_from_fraction(value) for value in coefficients
                ],
                "time_isolating_interval": exact_interval(*candidate_time),
                "endpoint_values": {
                    "lo": dyadic_from_fraction(endpoint_values[0]),
                    "hi": dyadic_from_fraction(endpoint_values[1]),
                },
                "derivative_range": exact_interval(*derivative_range),
            }
            determinant_range = exact_interval(*derivative_range)
        leaves.append(
            {
                "leaf_id": right_leaf_id,
                "node_id": right_id,
                "domain_id": domain_id,
                "image_id": f"image-{index}",
                "classification": "unique_root",
                "witness": {
                    "type": "interval_newton_inclusion",
                    "candidate_id": candidate_id,
                    "operator_box": operator_box,
                    "determinant_range": determinant_range,
                    "root_model": root_model,
                    "backend": SYNTHETIC_PROOF_BACKEND,
                },
            }
        )
        candidate = {
            "candidate_id": candidate_id,
            "leaf_id": right_leaf_id,
            "image_id": f"image-{index}",
            "physical_root_id": physical_root_id,
            "time_interval": exact_interval(*candidate_time),
        }
        quotient = {
            "physical_root_id": physical_root_id,
            "candidate_ids": [candidate_id],
            "representative_candidate_id": candidate_id,
            "proof_type": "identity",
            "seam_equivalence_key": seam_key or f"seam-{index}",
            "seam_proof": None,
        }
    return domain, nodes, leaves, [_image(index, seam_key=seam_key)], candidate, quotient


def build_coverage_certificate(
    candidate_specs: Sequence[
        tuple[str, str, tuple[Fraction, Fraction]]
    ] = (("candidate-0", "physical-root-0", (Fraction(3, 4), Fraction(3, 4))),),
    *,
    no_entry: bool = False,
    unresolved: bool = False,
    time_domain: tuple[Fraction, Fraction] = (
        Fraction(0),
        Fraction(4),
    ),
) -> dict[str, Any]:
    if no_entry and candidate_specs:
        candidate_specs = ()
    domain_rows: list[dict[str, Any]] = []
    node_rows: list[dict[str, Any]] = []
    leaf_rows: list[dict[str, Any]] = []
    image_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    quotient_rows: list[dict[str, Any]] = []
    specs = list(candidate_specs)
    if unresolved:
        specs = []
    count = max(len(specs), 1)
    for index in range(count):
        if unresolved:
            candidate_id = None
            physical_root_id = None
            candidate_time = (Fraction(3, 4), Fraction(3, 4))
        elif index < len(specs):
            candidate_id, physical_root_id, candidate_time = specs[index]
        else:
            candidate_id = None
            physical_root_id = None
            candidate_time = (Fraction(3, 4), Fraction(3, 4))
        domain, nodes, leaves, images, candidate, quotient = (
            _root_domain_rows(
                index,
                candidate_id=candidate_id,
                physical_root_id=physical_root_id,
                candidate_time=candidate_time,
                unresolved=unresolved,
                time_domain=time_domain,
            )
        )
        domain_rows.append(domain)
        node_rows.extend(nodes)
        leaf_rows.extend(leaves)
        image_rows.extend(images)
        if candidate is not None:
            candidate_rows.append(candidate)
        if quotient is not None:
            quotient_rows.append(quotient)
    fixture_registry_id = "coverage-fixture::" + canonical_sha256(
        {
            "candidate_specs": [
                {
                    "candidate_id": candidate_id,
                    "physical_root_id": physical_root_id,
                    "time_interval": exact_interval(*candidate_time),
                }
                for candidate_id, physical_root_id, candidate_time in specs
            ],
            "no_entry": no_entry,
            "unresolved": unresolved,
            "time_domain": exact_interval(*time_domain),
        }
    )
    exact_inputs = _exact_inputs(
        image_rows,
        domain_rows,
        leaf_rows,
        fixture_registry_id=fixture_registry_id,
    )
    manifest = {
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "exact_inputs": exact_inputs,
        "exact_inputs_sha256": canonical_sha256(exact_inputs),
        "images": image_rows,
        "initial_domains": domain_rows,
        "nodes": node_rows,
        "leaves": leaf_rows,
        "candidates": candidate_rows,
        "quotient_classes": quotient_rows,
    }
    certificate = _certificate("coverage-proof", manifest)
    validate_coverage_certificate(certificate)
    return certificate


def build_seam_duplicate_certificate() -> dict[str, Any]:
    rows = []
    for index, candidate_id in enumerate(("candidate-seam-a", "candidate-seam-b")):
        rows.append(
            _root_domain_rows(
                index,
                candidate_id=candidate_id,
                physical_root_id="physical-root-seam",
                seam_key="same-seam-orbit",
            )
        )
    domains: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    leaves: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    for domain, node_rows, leaf_rows, image_rows, candidate, _ in rows:
        domains.append(domain)
        nodes.extend(node_rows)
        leaves.extend(leaf_rows)
        images.extend(image_rows)
        assert candidate is not None
        candidates.append(candidate)
    quotient = {
        "physical_root_id": "physical-root-seam",
        "candidate_ids": ["candidate-seam-a", "candidate-seam-b"],
        "representative_candidate_id": "candidate-seam-a",
        "proof_type": "seam_equivalence",
        "seam_equivalence_key": "same-seam-orbit",
        "seam_proof": {
            "base_candidate_id": "candidate-seam-a",
            "lattice_delta_bindings": [
                {
                    "candidate_id": "candidate-seam-a",
                    "image_id": "image-0",
                    "lattice_delta": [0] * 9,
                },
                {
                    "candidate_id": "candidate-seam-b",
                    "image_id": "image-1",
                    "lattice_delta": [1] + [0] * 8,
                },
            ],
        },
    }
    exact_inputs = _exact_inputs(
        images,
        domains,
        leaves,
        fixture_registry_id="coverage-fixture::seam-duplicate",
    )
    manifest = {
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "exact_inputs": exact_inputs,
        "exact_inputs_sha256": canonical_sha256(exact_inputs),
        "images": images,
        "initial_domains": domains,
        "nodes": nodes,
        "leaves": leaves,
        "candidates": candidates,
        "quotient_classes": [quotient],
    }
    certificate = _certificate("coverage-seam-proof", manifest)
    validate_coverage_certificate(certificate)
    return certificate


def build_singular_cluster_certificate() -> dict[str, Any]:
    """Build a small typed positive-dimensional root-set fixture."""

    (
        domain,
        nodes,
        leaves,
        images,
        candidate,
        quotient,
    ) = _root_domain_rows(
        0,
        candidate_id="candidate-singular-set",
        physical_root_id="physical-root-singular-set",
    )
    assert candidate is not None and quotient is not None
    root_leaf = next(
        leaf for leaf in leaves if leaf["classification"] == "unique_root"
    )
    affine_set = {
        "variable_order": list(AXES),
        "matrix": [
            [dyadic(0), dyadic(1), dyadic(0)],
            [dyadic(0), dyadic(0), dyadic(1)],
            [dyadic(0), dyadic(0), dyadic(0)],
        ],
        "constant": [
            dyadic(-1, 1),
            dyadic(-3, 2),
            dyadic(0),
        ],
        "base_point": [
            dyadic(1, 1),
            dyadic(1, 1),
            dyadic(3, 2),
        ],
        "null_direction": [
            dyadic(1),
            dyadic(0),
            dyadic(0),
        ],
        "parameter_interval": exact_interval(
            Fraction(-1, 8), Fraction(1, 8)
        ),
        "declared_rank": 2,
        "declared_dimension": 1,
    }
    root_leaf["classification"] = "certified_singular_cluster"
    root_leaf["witness"] = {
        "type": "singular_set_certificate",
        "candidate_ids": ["candidate-singular-set"],
        "affine_set": affine_set,
        "set_certificate_sha256": canonical_sha256(affine_set),
        "backend": SYNTHETIC_PROOF_BACKEND,
    }
    exact_inputs = _exact_inputs(
        images,
        [domain],
        leaves,
        fixture_registry_id="coverage-fixture::singular-cluster",
    )
    manifest = {
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "exact_inputs": exact_inputs,
        "exact_inputs_sha256": canonical_sha256(exact_inputs),
        "images": images,
        "initial_domains": [domain],
        "nodes": nodes,
        "leaves": leaves,
        "candidates": [candidate],
        "quotient_classes": [quotient],
    }
    certificate = _certificate("coverage-singular-set", manifest)
    validate_coverage_certificate(certificate)
    return certificate


def build_mixed_unresolved_certificate() -> dict[str, Any]:
    """Build one isolated candidate plus one earlier-order unresolved leaf."""

    root_rows = _root_domain_rows(
        0,
        candidate_id="candidate-0",
        physical_root_id="physical-root-0",
    )
    unresolved_rows = _root_domain_rows(
        1,
        candidate_id=None,
        physical_root_id=None,
        unresolved=True,
    )
    domains: list[dict[str, Any]] = []
    nodes: list[dict[str, Any]] = []
    leaves: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    quotients: list[dict[str, Any]] = []
    for domain, node_rows, leaf_rows, image_rows, candidate, quotient in (
        root_rows,
        unresolved_rows,
    ):
        domains.append(domain)
        nodes.extend(node_rows)
        leaves.extend(leaf_rows)
        images.extend(image_rows)
        if candidate is not None:
            candidates.append(candidate)
        if quotient is not None:
            quotients.append(quotient)
    exact_inputs = _exact_inputs(
        images,
        domains,
        leaves,
        fixture_registry_id="coverage-fixture::mixed-unresolved",
    )
    manifest = {
        "schema_version": COVERAGE_SCHEMA_VERSION,
        "exact_inputs": exact_inputs,
        "exact_inputs_sha256": canonical_sha256(exact_inputs),
        "images": images,
        "initial_domains": domains,
        "nodes": nodes,
        "leaves": leaves,
        "candidates": candidates,
        "quotient_classes": quotients,
    }
    certificate = _certificate("coverage-mixed-unresolved", manifest)
    validate_coverage_certificate(certificate)
    return certificate


def recompute_manifest_hash(certificate: dict[str, Any]) -> None:
    certificate["manifest_sha256"] = canonical_sha256(
        certificate["manifest"]
    )
    leaf_counts = {name: 0 for name in LEAF_CLASSES}
    for leaf in certificate["manifest"]["leaves"]:
        leaf_counts[leaf["classification"]] += 1
    certificate["leaf_counts"] = leaf_counts
    certificate["node_count"] = len(certificate["manifest"]["nodes"])
    certificate["image_count"] = len(certificate["manifest"]["images"])
    certificate["domain_count"] = len(
        certificate["manifest"]["initial_domains"]
    )
    certificate["candidate_count"] = len(
        certificate["manifest"]["candidates"]
    )
    certificate["physical_root_count"] = len(
        certificate["manifest"]["quotient_classes"]
    )


def deleted_leaf_mutation(
    certificate: dict[str, Any],
) -> dict[str, Any]:
    hostile = copy.deepcopy(certificate)
    hostile["manifest"]["leaves"].pop()
    recompute_manifest_hash(hostile)
    return hostile
