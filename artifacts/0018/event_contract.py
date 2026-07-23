#!/usr/bin/env python3
"""Reference event-record contract for Brief 0018.

This standard-library artifact implements only the total, disjoint record
semantics upstream of a physical finite-K population calculation.  It does
not sample the microcanonical source, solve world-sheet roots, estimate
outcome masses, or certify any physical encounter.
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
from typing import Any, Iterable, Sequence

import coverage_proof as coverage


EVENT_SCHEMA_VERSION = "cyz-brief-0018-event-record-v2"
CONTROL_SCHEMA_VERSION = "cyz-brief-0018-event-schema-controls-v2"
TARGET_DIMENSION = 9
DOMAIN_DIMENSION = 3
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")

# These are external trust anchors for the exact synthetic controls.  They
# pin the complete typed problem commitment (including the fixture function
# registry), so editing equations and recomputing ordinary JSON hashes cannot
# silently turn one registered control into another.  Physical solver output
# is deliberately not admitted to this table; Brief 0019 must supply its
# independent pinned replayer.
PINNED_SYNTHETIC_PROBLEM_SHA256: dict[str, str | None] = {
    "hostile-source_invalid": None,
    "hostile-left_censored_active_episode": None,
    "hostile-torus_branch_ambiguous": None,
    "hostile-ambiguous_tie": (
        "8b86dc0d90c69f3e5513a0bac7e2990072c7d9d4e90b52debfe8c3ce8f3c10df"
    ),
    "hostile-numerically_unresolved": (
        "91e9bfd84a70dcd2fdb95ef59cc1db78362a6bcdbeb9d0ca23ac2bd08074d726"
    ),
    "hostile-no_entry_proved": (
        "6c59ecad012814bff806b50aca50523bd12190d9759f6f51ebc631731a2ff26f"
    ),
    "hostile-right_censored_no_entry": (
        "d3b6e86c589b93e6454c90673589c645082e16f2e46327d39820e616d9286117"
    ),
    "hostile-right_censored_active_episode": (
        "76e7db75e6ecb0732c09a934d6f75bb65f4c3f60df1e194fd2212c2f8607ce30"
    ),
    "hostile-tie_cluster": (
        "638926134b8288b2bcd6e995a699fd3909bad0c0d8689cf0821ce4924cbd82a3"
    ),
    "hostile-degenerate_spatial_minimum": (
        "2bd0fabab7670a13613147f8cf5cc3b31c125279be8288cb513023b9d0c63e91"
    ),
    "hostile-grazing_entry": (
        "6026fabafe5d44324fea77aa945ed6aa329d54847440ac66cd648b082ce9be9c"
    ),
    "hostile-regular_first_entry": (
        "087a2a7ec27e1e415ca5f427134497e2c359e32a74751b0be9dcfe99096dd644"
    ),
    "hostile-positive-dimensional-tie": (
        "aaea3ca2c52d446f7101920996e8eb585fd2e093caefd43311052c28e32f346c"
    ),
}

PINNED_SYNTHETIC_EVENT_MODEL_REGISTRY_SHA256 = {
    "hostile-source_invalid": (
        "76d61cfb41ea6b9589c8a52e4429562cc83b1175b0ff7a92e553067f8afae936"
    ),
    "hostile-left_censored_active_episode": (
        "909692ece2dbe144b6de4c1fa13e7d588d3e94f63c6671deaa82f65276c00886"
    ),
    "hostile-torus_branch_ambiguous": (
        "afd3cc200397269f29acfd61de9cc9ea11142262f1f2bb1dd8c1ec32c5aa0d38"
    ),
    "hostile-ambiguous_tie": (
        "b29e46703e8e9ee3582b284fc49449b6f8d0f9aeea648ff6a3cd2605a489b508"
    ),
    "hostile-numerically_unresolved": (
        "10ecdc037e2a3ae6d74ead4a265ab18579c13a38d5f7b5e73b53c105aa7cfed6"
    ),
    "hostile-no_entry_proved": (
        "9207eb75603a060289ecfff0e031caf8005dfe5b766a62131045abcbbfca383b"
    ),
    "hostile-right_censored_no_entry": (
        "c7a01808ed74399c3d0f8dadb2da854a37543220e65f0de6a567262e18ad5b8a"
    ),
    "hostile-right_censored_active_episode": (
        "4410b97208988e553ac567239485718fb22804a776189c12b18db069f21a6c45"
    ),
    "hostile-tie_cluster": (
        "6e4427e4440078481ccd7ab3d4527ad5c92d4c069c3edacacd9473e09122ea01"
    ),
    "hostile-degenerate_spatial_minimum": (
        "c099b2d53d086d8b76aeaa75dfe079860a7dc37e074812269ccd4f690549b94b"
    ),
    "hostile-grazing_entry": (
        "43668247b07b66083df18c2a8f1a01e11baac9e967b49d82c1606b8368536e8e"
    ),
    "hostile-regular_first_entry": (
        "1534e5d5300da490edb0ad7bfe8ab70dfab86cdfbb65242e8ae329919e30d818"
    ),
    "hostile-positive-dimensional-tie": (
        "50de2ecaf7e3dc905d55a1f938750c6e6d8d65ec31544ec7fa86c40b3536bce7"
    ),
}

PRIMARY_PRECEDENCE = (
    "source_invalid",
    "left_censored_active_episode",
    "torus_branch_ambiguous",
    "ambiguous_tie",
    "numerically_unresolved",
    "no_entry_proved",
    "right_censored_no_entry",
    "right_censored_active_episode",
    "tie_cluster",
    "degenerate_spatial_minimum",
    "grazing_entry",
    "regular_first_entry",
)

FLAG_NAMES = (
    "source_valid",
    "history_valid",
    "initial_armed",
    "left_censored",
    "right_censored",
    "solver_complete",
    "root_coverage_complete",
    "global_minimum_certified",
    "no_earlier_entry_certified",
    "torus_log_unique",
    "torus_branch_ambiguous",
    "ambiguous_tie",
    "entry_observed",
    "entry_earliest_certified",
    "entry_cluster_complete",
    "entry_tied",
    "entry_positive_dimensional",
    "entry_geometry_regular",
    "entry_has_grazing",
    "entry_has_spatial_degeneracy",
    "entry_direction_inconsistent",
    "outer_exit_observed",
    "outer_exit_certified",
    "outer_grazing_observed",
    "episode_complete",
    "rearmed",
    "closest_episode_identified",
    "closest_window_only",
    "closest_tied",
    "episode_has_secondary_inner_contact",
    "episode_has_component_merger",
    "episode_has_component_split",
    "episode_topology_unresolved",
    "rank_marks_complete",
    "normal_marks_complete",
    "no_entry_window_certified",
    "no_entry_complete_time_domain_certified",
)

ROOT_KEYS = {
    "schema_version",
    "registry_hash",
    "sample_id",
    "source",
    "observation",
    "primary_outcome",
    "flags",
    "entry_cluster",
    "episodes",
    "certificates",
    "precedence_trace",
    "scope",
}

SOURCE_KEYS = {
    "sampling_registry_hash",
    "classification_registry_hash",
    "source_valid",
    "history_valid",
    "invalid_reasons",
    "initial_state",
}

OBSERVATION_KEYS = {
    "t0",
    "t1",
    "window_semantics",
    "complete_time_domain",
    "continuation_state",
}

CERTIFICATE_KEYS = {
    "source_validity",
    "root_coverage",
    "global_minimum",
    "no_earlier_entry",
    "torus_log",
    "tie",
    "outer_exit",
    "no_entry",
    "unresolved",
    "closest",
}

CLUSTER_KEYS = {
    "representation",
    "complete",
    "unordered",
    "cardinality",
    "members",
    "member_hashes",
    "members_sha256",
    "implicit_set",
}

REPRESENTATIVE_KEYS = {
    "representative_id",
    "candidate_id",
    "box",
    "torus_image",
    "log_unique",
    "s",
    "F",
    "grad_sigma",
    "dF_dt",
    "H_sigma_sigma",
    "geometry_certificate",
    "jet_normal",
}

JET_NORMAL_KEYS = {
    "coordinate_basis",
    "G",
    "H",
    "J",
    "singular_value_intervals",
    "rank",
    "rank_certificate",
    "normal_dimension",
    "P_N",
    "normal_frame",
    "s",
    "b",
    "ell",
}


class ContractError(ValueError):
    """Raised when a record violates the event contract."""


def reject_duplicate_object_pairs(
    pairs: Sequence[tuple[str, Any]],
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON object key: {key!r}")
        result[key] = value
    return result


def reject_nonfinite_constant(token: str) -> None:
    raise ContractError(f"non-finite JSON number is forbidden: {token}")


def _reject_nonfinite_tree(value: Any, path: str = "$") -> None:
    if type(value) is float and not math.isfinite(value):
        raise ContractError(f"{path}: non-finite number")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite_tree(item, f"{path}[{index}]")
    elif isinstance(value, dict):
        for key, item in value.items():
            if type(key) is not str:
                raise ContractError(f"{path}: JSON object key is not a string")
            _reject_nonfinite_tree(item, f"{path}.{key}")


def strict_load_json(path: Path) -> Any:
    """Read type-preserving JSON with duplicate/non-finite rejection."""

    with path.open("r", encoding="utf-8", newline=None) as handle:
        value = json.load(
            handle,
            object_pairs_hook=reject_duplicate_object_pairs,
            parse_constant=reject_nonfinite_constant,
        )
    _reject_nonfinite_tree(value)
    return value


def type_strict_equal(left: Any, right: Any) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return (
            left.keys() == right.keys()
            and all(
                type_strict_equal(left[key], right[key])
                for key in left
            )
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            type_strict_equal(a, b) for a, b in zip(left, right)
        )
    return left == right


def serialize_json(value: Any) -> str:
    _reject_nonfinite_tree(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ) + "\n"


def canonical_bytes(value: Any) -> bytes:
    _reject_nonfinite_tree(value)
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_lf_sha256(path: Path) -> str:
    """Hash UTF-8 text after universal-newline decoding and LF encoding."""

    with path.open("r", encoding="utf-8", newline=None) as handle:
        text = handle.read()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _require(condition: bool, path: str, message: str) -> None:
    if not condition:
        raise ContractError(f"{path}: {message}")


def _require_exact_keys(
    value: Any, expected: set[str], path: str
) -> dict[str, Any]:
    _require(type(value) is dict, path, "expected an object")
    actual = set(value)
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    _require(not missing, path, f"missing keys {missing}")
    _require(not extra, path, f"unexpected keys {extra}")
    return value


def _require_bool(value: Any, path: str) -> bool:
    _require(type(value) is bool, path, "expected a boolean")
    return value


def _require_string(value: Any, path: str, *, nonempty: bool = True) -> str:
    _require(type(value) is str, path, "expected a string")
    if nonempty:
        _require(bool(value), path, "string must be nonempty")
    return value


def _require_number(value: Any, path: str) -> float | int:
    _require(
        type(value) in (int, float),
        path,
        "expected a number; booleans are not numbers",
    )
    if type(value) is float:
        _require(math.isfinite(value), path, "number must be finite")
    return value


def _require_integer(value: Any, path: str) -> int:
    _require(
        type(value) is int,
        path,
        "expected an integer; booleans are not integers",
    )
    return value


def _require_hash(value: Any, path: str) -> str:
    text = _require_string(value, path)
    _require(HASH_PATTERN.fullmatch(text) is not None, path, "invalid SHA-256")
    return text


def _require_enum(value: Any, options: Iterable[str], path: str) -> str:
    text = _require_string(value, path)
    allowed = tuple(options)
    _require(text in allowed, path, f"expected one of {allowed}")
    return text


def _validate_string_list(value: Any, path: str) -> list[str]:
    _require(type(value) is list, path, "expected an array")
    for index, item in enumerate(value):
        _require_string(item, f"{path}[{index}]")
    return value


def _validate_interval(value: Any, path: str) -> dict[str, Any]:
    obj = _require_exact_keys(value, {"lo", "hi"}, path)
    lower = _require_number(obj["lo"], f"{path}.lo")
    upper = _require_number(obj["hi"], f"{path}.hi")
    _require(lower <= upper, path, "interval endpoints are reversed")
    return obj


def _validate_dyadic(value: Any, path: str) -> Fraction:
    try:
        return coverage.as_fraction(value, path)
    except coverage.ProofError as error:
        raise ContractError(str(error)) from error


def _validate_exact_interval(
    value: Any, path: str
) -> tuple[Fraction, Fraction]:
    try:
        return coverage.interval_fractions(value, path)
    except coverage.ProofError as error:
        raise ContractError(str(error)) from error


def _hash_binding(value: Any, declared: Any, path: str) -> None:
    _require_hash(declared, path)
    _require(
        declared == canonical_sha256(value),
        path,
        "content hash does not match bound object",
    )


def _coverage_problem_context(
    certificate: dict[str, Any],
) -> tuple[str, dict[str, Any], dict[str, dict[str, Any]]]:
    exact_inputs = certificate["manifest"]["exact_inputs"]
    commitment_sha256 = exact_inputs["problem_commitment_sha256"]
    commitment = exact_inputs["problem_commitment"]
    model_rows = commitment["function_registry"]["models"]
    return (
        commitment_sha256,
        commitment,
        {row["model_id"]: row for row in model_rows},
    )


def _require_registered_problem_model(
    *,
    witness: dict[str, Any],
    expected_payload: dict[str, Any],
    commitment_sha256: str,
    model_map: dict[str, dict[str, Any]],
    expected_suffix: str,
    path: str,
) -> None:
    _require(
        witness["problem_commitment_sha256"] == commitment_sha256,
        f"{path}.problem_commitment_sha256",
        "witness is not bound to the event problem commitment",
    )
    model_id = witness["model_id"]
    _require(
        model_id.endswith(f"::{expected_suffix}") and model_id in model_map,
        f"{path}.model_id",
        "witness references the wrong registered problem model",
    )
    registered = model_map[model_id]
    _require(
        registered["model_kind"] == expected_payload["model_kind"]
        and registered["model"] == expected_payload["model"],
        path,
        "witness content differs from the pinned problem model",
    )
    _require(
        witness["model_sha256"]
        == registered["model_sha256"]
        == canonical_sha256(expected_payload),
        f"{path}.model_sha256",
        "witness model hash differs from the pinned problem model",
    )


def _fraction_matrix_rank(matrix: Sequence[Sequence[Any]]) -> int:
    """Exact Gaussian-elimination rank for integer/rational fixtures."""

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


def _interval_product(
    left: tuple[float, float], right: tuple[float, float]
) -> tuple[float, float]:
    values = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(values), max(values)


def _interval_subtract(
    left: tuple[float, float], right: tuple[float, float]
) -> tuple[float, float]:
    return left[0] - right[1], left[1] - right[0]


def _float_interval_tuple(value: dict[str, Any]) -> tuple[float, float]:
    return float(value["lo"]), float(value["hi"])


def _symmetric_eigenvalues_3(
    matrix: Sequence[Sequence[Any]],
) -> list[float]:
    """Deterministic Jacobi diagonalization for a real symmetric 3x3."""

    values = [[float(item) for item in row] for row in matrix]
    for _ in range(64):
        row, column = max(
            ((0, 1), (0, 2), (1, 2)),
            key=lambda pair: abs(values[pair[0]][pair[1]]),
        )
        if abs(values[row][column]) <= 1.0e-15:
            break
        angle = 0.5 * math.atan2(
            2.0 * values[row][column],
            values[column][column] - values[row][row],
        )
        cosine = math.cos(angle)
        sine = math.sin(angle)
        rotation = identity_matrix(3)
        rotation[row][row] = cosine
        rotation[column][column] = cosine
        rotation[row][column] = sine
        rotation[column][row] = -sine
        values = _matrix_multiply(
            _matrix_multiply(_matrix_transpose(rotation), values),
            rotation,
        )
    return sorted(
        (values[index][index] for index in range(3)), reverse=True
    )


def _validate_vector(
    value: Any, length: int, path: str, *, integer: bool = False
) -> list[Any]:
    _require(type(value) is list, path, "expected an array")
    _require(len(value) == length, path, f"expected length {length}")
    for index, item in enumerate(value):
        if integer:
            _require_integer(item, f"{path}[{index}]")
        else:
            _require_number(item, f"{path}[{index}]")
    return value


def _validate_interval_vector(
    value: Any, length: int, path: str
) -> list[dict[str, Any]]:
    _require(type(value) is list, path, "expected an array")
    _require(len(value) == length, path, f"expected length {length}")
    for index, item in enumerate(value):
        _validate_interval(item, f"{path}[{index}]")
    return value


def _validate_matrix(
    value: Any, rows: int, columns: int, path: str
) -> list[list[Any]]:
    _require(type(value) is list, path, "expected an array")
    _require(len(value) == rows, path, f"expected {rows} rows")
    for row, values in enumerate(value):
        _validate_vector(values, columns, f"{path}[{row}]")
    return value


def _matrix_multiply(
    left: Sequence[Sequence[float]],
    right: Sequence[Sequence[float]],
) -> list[list[float]]:
    if not left or not right:
        raise ValueError("matrix product needs nonempty matrices")
    inner = len(left[0])
    if any(len(row) != inner for row in left):
        raise ValueError("left matrix is ragged")
    if len(right) != inner:
        raise ValueError("matrix product dimensions differ")
    columns = len(right[0])
    if any(len(row) != columns for row in right):
        raise ValueError("right matrix is ragged")
    return [
        [
            math.fsum(
                float(left[row][index]) * float(right[index][column])
                for index in range(inner)
            )
            for column in range(columns)
        ]
        for row in range(len(left))
    ]


def _matrix_transpose(
    matrix: Sequence[Sequence[float]],
) -> list[list[float]]:
    if not matrix:
        raise ValueError("transpose needs a nonempty matrix")
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix is ragged")
    return [
        [float(matrix[row][column]) for row in range(len(matrix))]
        for column in range(columns)
    ]


def _max_matrix_residual(
    left: Sequence[Sequence[float]],
    right: Sequence[Sequence[float]],
) -> float:
    if len(left) != len(right) or any(
        len(a) != len(b) for a, b in zip(left, right)
    ):
        raise ValueError("matrix residual dimensions differ")
    return max(
        (
            abs(float(a) - float(b))
            for left_row, right_row in zip(left, right)
            for a, b in zip(left_row, right_row)
        ),
        default=0.0,
    )


def _require_symmetric_positive_definite(
    matrix: Sequence[Sequence[float]],
    path: str,
) -> None:
    size = len(matrix)
    tolerance = 1.0e-12
    for row in range(size):
        for column in range(size):
            _require(
                math.isclose(
                    float(matrix[row][column]),
                    float(matrix[column][row]),
                    rel_tol=tolerance,
                    abs_tol=tolerance,
                ),
                path,
                "metric is not symmetric",
            )
    lower = zero_matrix(size, size)
    for row in range(size):
        for column in range(row + 1):
            correction = math.fsum(
                lower[row][index] * lower[column][index]
                for index in range(column)
            )
            if row == column:
                residue = float(matrix[row][row]) - correction
                _require(
                    residue > 0.0,
                    path,
                    "metric is not positive definite",
                )
                lower[row][column] = math.sqrt(residue)
            else:
                lower[row][column] = (
                    float(matrix[row][column]) - correction
                ) / lower[column][column]


def _validate_optional_certificate(
    value: Any,
    required_keys: set[str],
    path: str,
) -> dict[str, Any] | None:
    if value is None:
        return None
    return _require_exact_keys(value, required_keys, path)


def _validate_source(value: Any, path: str) -> dict[str, Any]:
    source = _require_exact_keys(value, SOURCE_KEYS, path)
    _require_hash(source["sampling_registry_hash"], f"{path}.sampling_registry_hash")
    _require_hash(
        source["classification_registry_hash"],
        f"{path}.classification_registry_hash",
    )
    _require_bool(source["source_valid"], f"{path}.source_valid")
    _require_bool(source["history_valid"], f"{path}.history_valid")
    _validate_string_list(source["invalid_reasons"], f"{path}.invalid_reasons")
    _require_enum(
        source["initial_state"],
        ("armed", "active", "unknown"),
        f"{path}.initial_state",
    )
    if source["source_valid"] and source["history_valid"]:
        _require(
            not source["invalid_reasons"],
            f"{path}.invalid_reasons",
            "valid source/history cannot have invalid reasons",
        )
    else:
        _require(
            bool(source["invalid_reasons"]),
            f"{path}.invalid_reasons",
            "invalid source/history requires a reason",
        )
    return source


def _validate_observation(value: Any, path: str) -> dict[str, Any]:
    observation = _require_exact_keys(value, OBSERVATION_KEYS, path)
    t0 = _require_number(observation["t0"], f"{path}.t0")
    t1 = _require_number(observation["t1"], f"{path}.t1")
    _require(t0 < t1, path, "observation window must have positive length")
    _require(
        observation["window_semantics"] == "[t0,t1)",
        f"{path}.window_semantics",
        "only half-open [t0,t1) semantics are allowed",
    )
    _require_bool(
        observation["complete_time_domain"],
        f"{path}.complete_time_domain",
    )
    _require_enum(
        observation["continuation_state"],
        ("armed", "active", "terminal", "invalid", "unresolved"),
        f"{path}.continuation_state",
    )
    return observation


def _validate_flags(value: Any, path: str) -> dict[str, bool]:
    flags = _require_exact_keys(value, set(FLAG_NAMES), path)
    for name in FLAG_NAMES:
        _require_bool(flags[name], f"{path}.{name}")
    return flags


def _validate_rank(value: Any, path: str) -> dict[str, Any]:
    rank = _require_exact_keys(
        value,
        {"status", "exact_rank", "possible_ranks"},
        path,
    )
    status = _require_enum(
        rank["status"], ("certified", "unresolved"), f"{path}.status"
    )
    _require(type(rank["possible_ranks"]) is list, f"{path}.possible_ranks", "expected an array")
    possible: list[int] = []
    for index, item in enumerate(rank["possible_ranks"]):
        candidate = _require_integer(item, f"{path}.possible_ranks[{index}]")
        _require(0 <= candidate <= 3, f"{path}.possible_ranks[{index}]", "rank outside 0..3")
        possible.append(candidate)
    _require(possible == sorted(set(possible)), f"{path}.possible_ranks", "ranks must be unique and sorted")
    _require(bool(possible), f"{path}.possible_ranks", "at least one possible rank is required")
    if status == "certified":
        exact = _require_integer(rank["exact_rank"], f"{path}.exact_rank")
        _require(0 <= exact <= 3, f"{path}.exact_rank", "rank outside 0..3")
        _require(possible == [exact], f"{path}.possible_ranks", "certified rank must be the sole possible rank")
    else:
        _require(rank["exact_rank"] is None, f"{path}.exact_rank", "unresolved rank cannot have exact_rank")
        _require(len(possible) >= 2, f"{path}.possible_ranks", "unresolved rank requires at least two possible ranks")
    return rank


def _validate_jet_normal(value: Any, path: str) -> dict[str, Any]:
    jet = _require_exact_keys(value, JET_NORMAL_KEYS, path)
    _require_string(jet["coordinate_basis"], f"{path}.coordinate_basis")
    _validate_matrix(jet["G"], 9, 9, f"{path}.G")
    _validate_matrix(jet["H"], 3, 3, f"{path}.H")
    _require_symmetric_positive_definite(jet["G"], f"{path}.G")
    _require_symmetric_positive_definite(jet["H"], f"{path}.H")
    _validate_matrix(jet["J"], 9, 3, f"{path}.J")
    singular_intervals = _validate_interval_vector(
        jet["singular_value_intervals"],
        3,
        f"{path}.singular_value_intervals",
    )
    for index, singular_interval in enumerate(singular_intervals):
        _require(
            singular_interval["lo"] >= 0.0,
            f"{path}.singular_value_intervals[{index}].lo",
            "singular-value interval cannot be negative",
        )
        if index:
            previous = singular_intervals[index - 1]
            _require(
                previous["hi"] >= singular_interval["hi"]
                and previous["lo"] >= singular_interval["lo"],
                f"{path}.singular_value_intervals[{index}]",
                "singular-value intervals must be ordered",
            )
    rank = _validate_rank(jet["rank"], f"{path}.rank")
    rank_certificate = _require_exact_keys(
        jet["rank_certificate"],
        {
            "certificate_id",
            "method",
            "J_sha256",
            "G_sha256",
            "H_sha256",
            "singular_intervals_sha256",
            "declared_rank",
            "possible_ranks",
        },
        f"{path}.rank_certificate",
    )
    _require_string(
        rank_certificate["certificate_id"],
        f"{path}.rank_certificate.certificate_id",
    )
    method = _require_enum(
        rank_certificate["method"],
        ("exact_rational_elimination", "interval_singular_enclosure"),
        f"{path}.rank_certificate.method",
    )
    for matrix_name in ("J", "G", "H"):
        _hash_binding(
            jet[matrix_name],
            rank_certificate[f"{matrix_name}_sha256"],
            f"{path}.rank_certificate.{matrix_name}_sha256",
        )
    _hash_binding(
        jet["singular_value_intervals"],
        rank_certificate["singular_intervals_sha256"],
        f"{path}.rank_certificate.singular_intervals_sha256",
    )
    _require(
        type(rank_certificate["possible_ranks"]) is list,
        f"{path}.rank_certificate.possible_ranks",
        "expected an array",
    )
    for index, item in enumerate(rank_certificate["possible_ranks"]):
        _require_integer(
            item, f"{path}.rank_certificate.possible_ranks[{index}]"
        )
    _require(
        rank_certificate["possible_ranks"] == rank["possible_ranks"],
        f"{path}.rank_certificate.possible_ranks",
        "rank certificate is not bound to the rank record",
    )
    if rank["status"] == "certified":
        _require(
            method == "exact_rational_elimination",
            f"{path}.rank_certificate.method",
            "certified fixture rank requires exact elimination",
        )
        declared = _require_integer(
            rank_certificate["declared_rank"],
            f"{path}.rank_certificate.declared_rank",
        )
        _require(
            declared == rank["exact_rank"],
            f"{path}.rank_certificate.declared_rank",
            "declared rank disagrees with rank record",
        )
        _require(
            all(
                type(component) is int
                for row in jet["J"]
                for component in row
            ),
            f"{path}.J",
            "exact rank fixture requires integer J entries",
        )
        _require(
            _fraction_matrix_rank(jet["J"]) == declared,
            f"{path}.rank_certificate.declared_rank",
            "exact replay of rank(J) disagrees",
        )
        _require(
            type_strict_equal(jet["G"], identity_matrix(9))
            and type_strict_equal(jet["H"], identity_matrix(3)),
            f"{path}.rank_certificate.method",
            "exact fixture singular replay currently requires identity G,H",
        )
        gram = _matrix_multiply(
            _matrix_transpose(jet["J"]), jet["J"]
        )
        eigenvalues = _symmetric_eigenvalues_3(gram)
        replayed_singular_values = [
            math.sqrt(max(0.0, eigenvalue))
            for eigenvalue in eigenvalues
        ]
        for index, singular_value in enumerate(
            replayed_singular_values
        ):
            interval_row = jet["singular_value_intervals"][index]
            _require(
                interval_row["lo"] - 1.0e-12
                <= singular_value
                <= interval_row["hi"] + 1.0e-12,
                f"{path}.singular_value_intervals[{index}]",
                "singular interval does not contain replayed value from J,G,H",
            )
    else:
        _require(
            method == "interval_singular_enclosure",
            f"{path}.rank_certificate.method",
            "unresolved rank requires interval enclosure method",
        )
        _require(
            rank_certificate["declared_rank"] is None,
            f"{path}.rank_certificate.declared_rank",
            "unresolved rank cannot declare an exact rank",
        )
    _validate_vector(jet["s"], 9, f"{path}.s")

    minimum_rank = min(rank["possible_ranks"])
    maximum_rank = max(rank["possible_ranks"])
    for index in range(minimum_rank):
        _require(
            singular_intervals[index]["lo"] > 0.0,
            f"{path}.singular_value_intervals[{index}]",
            "certified minimum rank needs a positive lower bound",
        )
    for index in range(maximum_rank, 3):
        _require(
            singular_intervals[index]["lo"] == 0.0
            and singular_intervals[index]["hi"] == 0.0,
            f"{path}.singular_value_intervals[{index}]",
            "rank upper bound requires an exact zero singular value",
        )

    if rank["status"] == "unresolved":
        for name in ("normal_dimension", "P_N", "normal_frame", "b", "ell"):
            _require(
                jet[name] is None,
                f"{path}.{name}",
                "unresolved rank must not fabricate a normal object",
            )
        return jet

    exact_rank = rank["exact_rank"]
    normal_dimension = _require_integer(
        jet["normal_dimension"], f"{path}.normal_dimension"
    )
    _require(
        normal_dimension == TARGET_DIMENSION - exact_rank,
        f"{path}.normal_dimension",
        "normal dimension must equal 9-rank",
    )
    _validate_matrix(jet["P_N"], 9, 9, f"{path}.P_N")
    _validate_vector(jet["b"], 9, f"{path}.b")
    _validate_vector(jet["ell"], 9, f"{path}.ell")
    frame = jet["normal_frame"]
    if frame is not None:
        _validate_matrix(frame, 9, normal_dimension, f"{path}.normal_frame")

    for index, (s_value, b_value, ell_value) in enumerate(
        zip(jet["s"], jet["b"], jet["ell"])
    ):
        _require(
            math.isclose(
                float(s_value),
                float(b_value) + float(ell_value),
                rel_tol=1.0e-12,
                abs_tol=1.0e-12,
            ),
            f"{path}.s[{index}]",
            "s=b+ell reconstruction failed",
        )

    tolerance = 1.0e-10
    projector = jet["P_N"]
    target_metric = jet["G"]
    projector_squared = _matrix_multiply(projector, projector)
    _require(
        _max_matrix_residual(projector_squared, projector) <= tolerance,
        f"{path}.P_N",
        "projector is not idempotent",
    )
    trace = math.fsum(
        float(projector[index][index]) for index in range(TARGET_DIMENSION)
    )
    _require(
        math.isclose(
            trace,
            float(TARGET_DIMENSION - exact_rank),
            rel_tol=1.0e-12,
            abs_tol=1.0e-12,
        ),
        f"{path}.P_N",
        "trace(P_N) must equal 9-rank(J)",
    )
    projector_jacobian = _matrix_multiply(projector, jet["J"])
    _require(
        _max_matrix_residual(
            projector_jacobian, zero_matrix(TARGET_DIMENSION, DOMAIN_DIMENSION)
        )
        <= tolerance,
        f"{path}.P_N",
        "P_N J must vanish",
    )
    metric_projector = _matrix_multiply(target_metric, projector)
    projector_transpose_metric = _matrix_multiply(
        _matrix_transpose(projector),
        target_metric,
    )
    _require(
        _max_matrix_residual(
            metric_projector, projector_transpose_metric
        )
        <= tolerance,
        f"{path}.P_N",
        "projector is not G-self-adjoint",
    )
    projected_separation = [
        math.fsum(
            float(projector[row][column]) * float(jet["s"][column])
            for column in range(9)
        )
        for row in range(9)
    ]
    _require(
        max(
            abs(projected_separation[index] - float(jet["b"][index]))
            for index in range(9)
        )
        <= tolerance,
        f"{path}.b",
        "b differs from P_N s",
    )
    metric_projector_columns = metric_projector
    for tangent_column in range(3):
        for normal_column in range(9):
            residual = math.fsum(
                float(jet["J"][row][tangent_column])
                * float(metric_projector_columns[row][normal_column])
                for row in range(9)
            )
            _require(
                abs(residual) <= tolerance,
                f"{path}.P_N",
                "projector range is not G-normal to im(J)",
            )

    if frame is not None:
        frame_transpose_metric = _matrix_multiply(
            _matrix_transpose(frame),
            target_metric,
        )
        frame_gram = _matrix_multiply(frame_transpose_metric, frame)
        _require(
            _max_matrix_residual(
                frame_gram, identity_matrix(normal_dimension)
            )
            <= tolerance,
            f"{path}.normal_frame",
            "normal frame is not G-orthonormal",
        )
        frame_projector = _matrix_multiply(frame, frame_transpose_metric)
        _require(
            _max_matrix_residual(frame_projector, projector) <= tolerance,
            f"{path}.normal_frame",
            "normal frame does not reproduce P_N",
        )
    return jet


def _validate_geometry_certificate(
    value: Any,
    representative: dict[str, Any],
    path: str,
) -> dict[str, Any]:
    certificate = _require_exact_keys(
        value,
        {
            "certificate_id",
            "hessian_sha256",
            "flux_sha256",
            "hessian_class",
            "leading_minor_range",
            "determinant_range",
            "flux_class",
            "flux_range",
            "time_derivative_jet",
            "time_derivative_jet_sha256",
            "contact_multiplicity",
            "one_sided_behavior",
        },
        path,
    )
    _require_string(certificate["certificate_id"], f"{path}.certificate_id")
    _hash_binding(
        representative["H_sigma_sigma"],
        certificate["hessian_sha256"],
        f"{path}.hessian_sha256",
    )
    _hash_binding(
        representative["dF_dt"],
        certificate["flux_sha256"],
        f"{path}.flux_sha256",
    )
    hessian_class = _require_enum(
        certificate["hessian_class"],
        ("positive_definite", "psd_singular", "unresolved"),
        f"{path}.hessian_class",
    )
    flux_class = _require_enum(
        certificate["flux_class"],
        ("strict_inward", "exact_zero_multiplicity", "unresolved"),
        f"{path}.flux_class",
    )
    leading = _validate_interval(
        certificate["leading_minor_range"],
        f"{path}.leading_minor_range",
    )
    determinant = _validate_interval(
        certificate["determinant_range"],
        f"{path}.determinant_range",
    )
    flux_range = _validate_interval(
        certificate["flux_range"], f"{path}.flux_range"
    )
    derivative_jet = certificate["time_derivative_jet"]
    _require(
        type(derivative_jet) is list and bool(derivative_jet),
        f"{path}.time_derivative_jet",
        "time derivative jet must be a nonempty array",
    )
    for index, derivative in enumerate(derivative_jet):
        _validate_interval(
            derivative, f"{path}.time_derivative_jet[{index}]"
        )
    _hash_binding(
        derivative_jet,
        certificate["time_derivative_jet_sha256"],
        f"{path}.time_derivative_jet_sha256",
    )
    _require(
        type_strict_equal(derivative_jet[0], representative["dF_dt"]),
        f"{path}.time_derivative_jet[0]",
        "first time derivative must equal dF_dt",
    )
    hessian = representative["H_sigma_sigma"]
    expected_leading = _float_interval_tuple(hessian[0][0])
    product_diagonal = _interval_product(
        _float_interval_tuple(hessian[0][0]),
        _float_interval_tuple(hessian[1][1]),
    )
    product_off_diagonal = _interval_product(
        _float_interval_tuple(hessian[0][1]),
        _float_interval_tuple(hessian[1][0]),
    )
    expected_determinant = _interval_subtract(
        product_diagonal, product_off_diagonal
    )
    _require(
        _float_interval_tuple(leading) == expected_leading,
        f"{path}.leading_minor_range",
        "leading-minor interval does not replay from H",
    )
    _require(
        _float_interval_tuple(determinant) == expected_determinant,
        f"{path}.determinant_range",
        "determinant interval does not replay from H",
    )
    _require(
        type_strict_equal(flux_range, representative["dF_dt"]),
        f"{path}.flux_range",
        "flux range does not match dF_dt",
    )
    if hessian_class == "positive_definite":
        _require(
            expected_leading[0] > 0.0 and expected_determinant[0] > 0.0,
            f"{path}.hessian_class",
            "positive-definite claim lacks strict minor bounds",
        )
    elif hessian_class == "psd_singular":
        exact_entries = all(
            item["lo"] == item["hi"]
            for row in hessian
            for item in row
        )
        _require(
            exact_entries
            and hessian[0][1]["lo"] == hessian[1][0]["lo"]
            and hessian[0][0]["lo"] >= 0
            and hessian[1][1]["lo"] >= 0
            and expected_determinant == (0.0, 0.0),
            f"{path}.hessian_class",
            "PSD-singular claim requires exact symmetric PSD H with det=0",
        )
    if flux_class == "strict_inward":
        _require(
            flux_range["hi"] < 0.0,
            f"{path}.flux_class",
            "strict inward claim requires F_t<0",
        )
        _require(
            certificate["contact_multiplicity"] is None,
            f"{path}.contact_multiplicity",
            "transverse entry has no grazing multiplicity",
        )
        _require(
            len(derivative_jet) == 1,
            f"{path}.time_derivative_jet",
            "transverse entry needs only its certified first derivative",
        )
        _require(
            certificate["one_sided_behavior"] == "inward_crossing",
            f"{path}.one_sided_behavior",
            "strict entry needs inward one-sided behavior",
        )
    elif flux_class == "exact_zero_multiplicity":
        multiplicity = _require_integer(
            certificate["contact_multiplicity"],
            f"{path}.contact_multiplicity",
        )
        _require(
            multiplicity >= 2,
            f"{path}.contact_multiplicity",
            "grazing multiplicity must be at least two",
        )
        _require(
            len(derivative_jet) == multiplicity
            and all(
                derivative["lo"] == 0.0
                and derivative["hi"] == 0.0
                for derivative in derivative_jet[: multiplicity - 1]
            )
            and (
                derivative_jet[multiplicity - 1]["hi"] < 0.0
                or derivative_jet[multiplicity - 1]["lo"] > 0.0
            ),
            f"{path}.time_derivative_jet",
            "multiplicity must equal first certified nonzero time derivative",
        )
        _require(
            flux_range["lo"] == 0.0 and flux_range["hi"] == 0.0,
            f"{path}.flux_range",
            "grazing requires exact zero F_t",
        )
        _require(
            certificate["one_sided_behavior"] == "touch_or_plateau",
            f"{path}.one_sided_behavior",
            "grazing needs a certified touch/plateau",
        )
        _require(
            multiplicity % 2 == 0
            and derivative_jet[multiplicity - 1]["lo"] > 0.0,
            f"{path}.time_derivative_jet",
            "touch requires positive even-order first nonzero derivative",
        )
    else:
        _require(
            certificate["contact_multiplicity"] is None,
            f"{path}.contact_multiplicity",
            "unresolved flux cannot claim multiplicity",
        )
        _require(
            certificate["one_sided_behavior"] == "unresolved",
            f"{path}.one_sided_behavior",
            "unresolved flux needs unresolved one-sided behavior",
        )
        _require(
            len(derivative_jet) == 1,
            f"{path}.time_derivative_jet",
            "unresolved flux cannot append authoritative higher derivatives",
        )
    return certificate


def _geometry_marks(representative: dict[str, Any]) -> tuple[bool, bool, bool]:
    certificate = representative["geometry_certificate"]
    regular = (
        certificate["hessian_class"] == "positive_definite"
        and certificate["flux_class"] == "strict_inward"
    )
    grazing = certificate["flux_class"] == "exact_zero_multiplicity"
    degenerate = certificate["hessian_class"] == "psd_singular"
    return regular, grazing, degenerate


def _validate_representative(value: Any, path: str) -> dict[str, Any]:
    representative = _require_exact_keys(value, REPRESENTATIVE_KEYS, path)
    _require_string(
        representative["representative_id"],
        f"{path}.representative_id",
    )
    _require_string(representative["candidate_id"], f"{path}.candidate_id")
    box = _require_exact_keys(
        representative["box"],
        {"sigma1", "sigma2", "time"},
        f"{path}.box",
    )
    for name in ("sigma1", "sigma2", "time"):
        _validate_interval(box[name], f"{path}.box.{name}")
    _validate_vector(
        representative["torus_image"],
        9,
        f"{path}.torus_image",
        integer=True,
    )
    _require_bool(representative["log_unique"], f"{path}.log_unique")
    _validate_vector(representative["s"], 9, f"{path}.s")
    _validate_interval(representative["F"], f"{path}.F")
    _validate_interval_vector(
        representative["grad_sigma"],
        2,
        f"{path}.grad_sigma",
    )
    _validate_interval(representative["dF_dt"], f"{path}.dF_dt")
    _require(
        type(representative["H_sigma_sigma"]) is list,
        f"{path}.H_sigma_sigma",
        "expected an array",
    )
    _require(
        len(representative["H_sigma_sigma"]) == 2,
        f"{path}.H_sigma_sigma",
        "expected two rows",
    )
    for row, values in enumerate(representative["H_sigma_sigma"]):
        _validate_interval_vector(
            values, 2, f"{path}.H_sigma_sigma[{row}]"
        )
    _validate_geometry_certificate(
        representative["geometry_certificate"],
        representative,
        f"{path}.geometry_certificate",
    )
    jet = _validate_jet_normal(
        representative["jet_normal"], f"{path}.jet_normal"
    )
    _require(
        type_strict_equal(representative["s"], jet["s"]),
        f"{path}.jet_normal.s",
        "representative and jet separation vectors differ",
    )
    return representative


def _validate_cluster(value: Any, path: str) -> dict[str, Any]:
    cluster = _require_exact_keys(value, CLUSTER_KEYS, path)
    representation = _require_enum(
        cluster["representation"],
        ("singleton", "finite", "implicit"),
        f"{path}.representation",
    )
    _require_bool(cluster["complete"], f"{path}.complete")
    _require(
        cluster["unordered"] is True,
        f"{path}.unordered",
        "cluster semantics must be unordered",
    )
    _require(type(cluster["members"]) is list, f"{path}.members", "expected an array")
    for index, member in enumerate(cluster["members"]):
        _validate_representative(member, f"{path}.members[{index}]")
    representative_ids = [
        member["representative_id"] for member in cluster["members"]
    ]
    candidate_ids = [member["candidate_id"] for member in cluster["members"]]
    _require(
        len(representative_ids) == len(set(representative_ids)),
        f"{path}.members",
        "representative IDs must be unique",
    )
    _require(
        len(candidate_ids) == len(set(candidate_ids)),
        f"{path}.members",
        "candidate IDs must be unique",
    )
    member_hashes = [canonical_sha256(member) for member in cluster["members"]]
    _require(
        member_hashes == sorted(member_hashes),
        f"{path}.members",
        "unordered members must be serialized in canonical hash order",
    )
    _require(
        cluster["member_hashes"] == member_hashes,
        f"{path}.member_hashes",
        "member hashes do not match canonical members",
    )
    _hash_binding(
        member_hashes,
        cluster["members_sha256"],
        f"{path}.members_sha256",
    )

    if representation == "singleton":
        _require_integer(cluster["cardinality"], f"{path}.cardinality")
        _require(cluster["cardinality"] == 1, f"{path}.cardinality", "singleton cardinality must be one")
        _require(len(cluster["members"]) == 1, f"{path}.members", "singleton must contain one member")
        _require(cluster["implicit_set"] is None, f"{path}.implicit_set", "singleton cannot have implicit_set")
    elif representation == "finite":
        cardinality = _require_integer(
            cluster["cardinality"], f"{path}.cardinality"
        )
        _require(cardinality >= 2, f"{path}.cardinality", "finite tie cardinality must be at least two")
        _require(len(cluster["members"]) == cardinality, f"{path}.members", "member count differs from cardinality")
        _require(cluster["implicit_set"] is None, f"{path}.implicit_set", "finite cluster cannot have implicit_set")
    else:
        _require(
            cluster["cardinality"] in ("continuum", "unknown"),
            f"{path}.cardinality",
            "implicit cardinality must be continuum or unknown",
        )
        _require(not cluster["members"], f"{path}.members", "implicit cluster cannot enumerate members")
        _require(
            cluster["member_hashes"] == [],
            f"{path}.member_hashes",
            "implicit cluster cannot hash enumerated members",
        )
        implicit = _require_exact_keys(
            cluster["implicit_set"],
            {
                "defining_equations",
                "candidate_ids",
                "domain_boxes",
                "dimension_status",
                "set_certificate_ref",
                "jet_field_certificate_ref",
                "normal_field_certificate_ref",
            },
            f"{path}.implicit_set",
        )
        _validate_string_list(
            implicit["defining_equations"],
            f"{path}.implicit_set.defining_equations",
        )
        implicit_candidate_ids = _validate_string_list(
            implicit["candidate_ids"],
            f"{path}.implicit_set.candidate_ids",
        )
        _require(
            bool(implicit_candidate_ids)
            and len(implicit_candidate_ids)
            == len(set(implicit_candidate_ids)),
            f"{path}.implicit_set.candidate_ids",
            "implicit set requires unique coverage candidate IDs",
        )
        _require(
            type(implicit["domain_boxes"]) is list,
            f"{path}.implicit_set.domain_boxes",
            "expected an array",
        )
        _require(
            bool(implicit["domain_boxes"]),
            f"{path}.implicit_set.domain_boxes",
            "implicit cluster needs at least one certified box",
        )
        for index, box in enumerate(implicit["domain_boxes"]):
            box_obj = _require_exact_keys(
                box,
                {"sigma1", "sigma2", "time"},
                f"{path}.implicit_set.domain_boxes[{index}]",
            )
            for name in ("sigma1", "sigma2", "time"):
                _validate_interval(
                    box_obj[name],
                    f"{path}.implicit_set.domain_boxes[{index}].{name}",
                )
        _require_enum(
            implicit["dimension_status"],
            ("positive", "unknown"),
            f"{path}.implicit_set.dimension_status",
        )
        _require_string(
            implicit["set_certificate_ref"],
            f"{path}.implicit_set.set_certificate_ref",
        )
        for name in (
            "jet_field_certificate_ref",
            "normal_field_certificate_ref",
        ):
            if implicit[name] is not None:
                _require_string(
                    implicit[name], f"{path}.implicit_set.{name}"
                )
    return cluster


def _validate_episode(value: Any, path: str) -> dict[str, Any]:
    episode = _require_exact_keys(
        value,
        {
            "episode_id",
            "role",
            "left_censored",
            "right_censored",
            "complete",
            "T_in",
            "T_out",
            "secondary_inner_contacts",
            "component_events",
        },
        path,
    )
    _require_string(episode["episode_id"], f"{path}.episode_id")
    _require_enum(
        episode["role"],
        ("preexisting", "primary", "subsequent"),
        f"{path}.role",
    )
    for name in ("left_censored", "right_censored", "complete"):
        _require_bool(episode[name], f"{path}.{name}")
    for name in ("T_in", "T_out"):
        if episode[name] is not None:
            _validate_interval(episode[name], f"{path}.{name}")
    count = _require_integer(
        episode["secondary_inner_contacts"],
        f"{path}.secondary_inner_contacts",
    )
    _require(count >= 0, f"{path}.secondary_inner_contacts", "count must be nonnegative")
    _require(
        type(episode["component_events"]) is list,
        f"{path}.component_events",
        "expected an array",
    )
    for index, event in enumerate(episode["component_events"]):
        item = _require_exact_keys(
            event,
            {"component_id", "transition", "time"},
            f"{path}.component_events[{index}]",
        )
        _require_string(
            item["component_id"],
            f"{path}.component_events[{index}].component_id",
        )
        _require_enum(
            item["transition"],
            ("birth", "merge", "split", "disappear"),
            f"{path}.component_events[{index}].transition",
        )
        _validate_interval(
            item["time"], f"{path}.component_events[{index}].time"
        )
    if episode["complete"]:
        _require(episode["T_out"] is not None, f"{path}.T_out", "complete episode needs T_out")
        _require(not episode["right_censored"], path, "complete episode cannot be right censored")
    if episode["T_in"] is not None and episode["T_out"] is not None:
        _require(
            episode["T_in"]["hi"] <= episode["T_out"]["lo"],
            path,
            "episode requires T_in <= T_out",
        )
    for index, event in enumerate(episode["component_events"]):
        if episode["T_in"] is not None:
            _require(
                event["time"]["lo"] >= episode["T_in"]["lo"],
                f"{path}.component_events[{index}].time",
                "component event precedes episode entry",
            )
        if episode["T_out"] is not None:
            _require(
                event["time"]["hi"] <= episode["T_out"]["hi"],
                f"{path}.component_events[{index}].time",
                "component event follows episode exit",
            )
    return episode


def _validate_certificates(value: Any, path: str) -> dict[str, Any]:
    certs = _require_exact_keys(value, CERTIFICATE_KEYS, path)

    source = _validate_optional_certificate(
        certs["source_validity"],
        {"certificate_id", "status", "predicate_version", "reason_codes"},
        f"{path}.source_validity",
    )
    if source is not None:
        _require_string(source["certificate_id"], f"{path}.source_validity.certificate_id")
        _require_enum(source["status"], ("valid", "invalid"), f"{path}.source_validity.status")
        _require_string(source["predicate_version"], f"{path}.source_validity.predicate_version")
        _validate_string_list(source["reason_codes"], f"{path}.source_validity.reason_codes")

    if certs["root_coverage"] is not None:
        try:
            coverage.validate_coverage_certificate(certs["root_coverage"])
        except coverage.ProofError as error:
            raise ContractError(f"{path}.root_coverage: {error}") from error

    global_minimum = _validate_optional_certificate(
        certs["global_minimum"],
        {
            "certificate_id",
            "coverage_manifest_sha256",
            "earliest_time",
            "candidate_ids",
            "minimizer_candidate_ids",
            "candidate_time_bindings",
            "excluded_leaf_ids",
        },
        f"{path}.global_minimum",
    )
    if global_minimum is not None:
        _require_string(
            global_minimum["certificate_id"],
            f"{path}.global_minimum.certificate_id",
        )
        _require_hash(
            global_minimum["coverage_manifest_sha256"],
            f"{path}.global_minimum.coverage_manifest_sha256",
        )
        _validate_dyadic(
            global_minimum["earliest_time"],
            f"{path}.global_minimum.earliest_time",
        )
        for name in (
            "candidate_ids",
            "minimizer_candidate_ids",
            "excluded_leaf_ids",
        ):
            rows = _validate_string_list(
                global_minimum[name], f"{path}.global_minimum.{name}"
            )
            _require(
                len(rows) == len(set(rows)),
                f"{path}.global_minimum.{name}",
                "IDs must be unique",
            )
        bindings = global_minimum["candidate_time_bindings"]
        _require(
            type(bindings) is list,
            f"{path}.global_minimum.candidate_time_bindings",
            "expected an array",
        )
        for index, binding in enumerate(bindings):
            item = _require_exact_keys(
                binding,
                {"candidate_id", "time_interval_sha256"},
                f"{path}.global_minimum.candidate_time_bindings[{index}]",
            )
            _require_string(
                item["candidate_id"],
                f"{path}.global_minimum.candidate_time_bindings[{index}].candidate_id",
            )
            _require_hash(
                item["time_interval_sha256"],
                f"{path}.global_minimum.candidate_time_bindings[{index}].time_interval_sha256",
            )

    no_earlier = _validate_optional_certificate(
        certs["no_earlier_entry"],
        {
            "certificate_id",
            "coverage_manifest_sha256",
            "earliest_time",
            "candidate_ids",
            "excluded_before_leaf_ids",
            "history_interval",
            "initial_rho_lower_bound",
            "r_in",
            "hysteresis_registry_id",
            "initial_armed_witness",
        },
        f"{path}.no_earlier_entry",
    )
    if no_earlier is not None:
        _require_string(
            no_earlier["certificate_id"],
            f"{path}.no_earlier_entry.certificate_id",
        )
        _require_hash(
            no_earlier["coverage_manifest_sha256"],
            f"{path}.no_earlier_entry.coverage_manifest_sha256",
        )
        earliest = _validate_dyadic(
            no_earlier["earliest_time"],
            f"{path}.no_earlier_entry.earliest_time",
        )
        candidate_ids = _validate_string_list(
            no_earlier["candidate_ids"],
            f"{path}.no_earlier_entry.candidate_ids",
        )
        excluded_ids = _validate_string_list(
            no_earlier["excluded_before_leaf_ids"],
            f"{path}.no_earlier_entry.excluded_before_leaf_ids",
        )
        _require(
            len(candidate_ids) == len(set(candidate_ids))
            and len(excluded_ids) == len(set(excluded_ids)),
            f"{path}.no_earlier_entry",
            "certificate IDs must be unique",
        )
        history_lower, history_upper = _validate_exact_interval(
            no_earlier["history_interval"],
            f"{path}.no_earlier_entry.history_interval",
        )
        _require(
            history_upper == earliest and history_lower < history_upper,
            f"{path}.no_earlier_entry.history_interval",
            "history interval must terminate exactly at earliest_time",
        )
        rho_lower = _validate_dyadic(
            no_earlier["initial_rho_lower_bound"],
            f"{path}.no_earlier_entry.initial_rho_lower_bound",
        )
        r_in = _validate_dyadic(
            no_earlier["r_in"], f"{path}.no_earlier_entry.r_in"
        )
        _require_string(
            no_earlier["hysteresis_registry_id"],
            f"{path}.no_earlier_entry.hysteresis_registry_id",
        )
        armed_witness = _require_exact_keys(
            no_earlier["initial_armed_witness"],
            {
                "observable",
                "time",
                "rho_affine",
                "rho_range",
                "backend",
                "problem_commitment_sha256",
                "model_id",
                "model_sha256",
            },
            f"{path}.no_earlier_entry.initial_armed_witness",
        )
        _require(
            armed_witness["observable"] == "rho=sqrt(2F_min)",
            f"{path}.no_earlier_entry.initial_armed_witness.observable",
            "armed witness is bound to wrong observable",
        )
        _validate_dyadic(
            armed_witness["time"],
            f"{path}.no_earlier_entry.initial_armed_witness.time",
        )
        armed_affine = _require_exact_keys(
            armed_witness["rho_affine"],
            {"slope", "intercept"},
            f"{path}.no_earlier_entry.initial_armed_witness.rho_affine",
        )
        armed_slope = _validate_dyadic(
            armed_affine["slope"],
            f"{path}.no_earlier_entry.initial_armed_witness.rho_affine.slope",
        )
        armed_intercept = _validate_dyadic(
            armed_affine["intercept"],
            f"{path}.no_earlier_entry.initial_armed_witness.rho_affine.intercept",
        )
        armed_range = _validate_exact_interval(
            armed_witness["rho_range"],
            f"{path}.no_earlier_entry.initial_armed_witness.rho_range",
        )
        armed_time = _validate_dyadic(
            armed_witness["time"],
            f"{path}.no_earlier_entry.initial_armed_witness.time",
        )
        armed_value = armed_slope * armed_time + armed_intercept
        _require(
            armed_range == (armed_value, armed_value)
            and rho_lower == armed_range[0],
            f"{path}.no_earlier_entry.initial_armed_witness",
            "initial rho bound does not replay from witness",
        )
        _require_string(
            armed_witness["backend"],
            f"{path}.no_earlier_entry.initial_armed_witness.backend",
        )
        _require_hash(
            armed_witness["problem_commitment_sha256"],
            f"{path}.no_earlier_entry.initial_armed_witness.problem_commitment_sha256",
        )
        _require_string(
            armed_witness["model_id"],
            f"{path}.no_earlier_entry.initial_armed_witness.model_id",
        )
        _require_hash(
            armed_witness["model_sha256"],
            f"{path}.no_earlier_entry.initial_armed_witness.model_sha256",
        )
        _require(
            rho_lower > r_in,
            f"{path}.no_earlier_entry.initial_rho_lower_bound",
            "initial state is not certified armed",
        )

    torus = _validate_optional_certificate(
        certs["torus_log"],
        {"certificate_id", "unique", "image_manifest_hash"},
        f"{path}.torus_log",
    )
    if torus is not None:
        _require_string(torus["certificate_id"], f"{path}.torus_log.certificate_id")
        _require_bool(torus["unique"], f"{path}.torus_log.unique")
        _require_hash(torus["image_manifest_hash"], f"{path}.torus_log.image_manifest_hash")

    tie = _validate_optional_certificate(
        certs["tie"],
        {
            "certificate_id",
            "status",
            "candidate_ids",
            "equal_time_proof",
            "ordering_proof",
        },
        f"{path}.tie",
    )
    if tie is not None:
        _require_string(tie["certificate_id"], f"{path}.tie.certificate_id")
        _require_enum(
            tie["status"],
            ("none", "complete_cluster", "ordering_ambiguous"),
            f"{path}.tie.status",
        )
        candidate_ids = _validate_string_list(
            tie["candidate_ids"], f"{path}.tie.candidate_ids"
        )
        _require(
            len(candidate_ids) == len(set(candidate_ids)),
            f"{path}.tie.candidate_ids",
            "candidate IDs must be unique",
        )
        if tie["status"] == "complete_cluster":
            _require(
                bool(candidate_ids),
                f"{path}.tie.candidate_ids",
                "complete tie/set needs at least one coverage candidate",
            )
            proof = _require_exact_keys(
                tie["equal_time_proof"],
                {"exact_time", "bindings"},
                f"{path}.tie.equal_time_proof",
            )
            _validate_dyadic(
                proof["exact_time"], f"{path}.tie.equal_time_proof.exact_time"
            )
            _require(
                type(proof["bindings"]) is list,
                f"{path}.tie.equal_time_proof.bindings",
                "expected an array",
            )
            binding_ids: list[str] = []
            for index, binding in enumerate(proof["bindings"]):
                item = _require_exact_keys(
                    binding,
                    {
                        "candidate_id",
                        "representative_id",
                        "member_time_sha256",
                        "candidate_time_sha256",
                    },
                    f"{path}.tie.equal_time_proof.bindings[{index}]",
                )
                binding_ids.append(
                    _require_string(
                        item["candidate_id"],
                        f"{path}.tie.equal_time_proof.bindings[{index}].candidate_id",
                    )
                )
                _require_string(
                    item["representative_id"],
                    f"{path}.tie.equal_time_proof.bindings[{index}].representative_id",
                )
                for name in ("member_time_sha256", "candidate_time_sha256"):
                    _require_hash(
                        item[name],
                        f"{path}.tie.equal_time_proof.bindings[{index}].{name}",
                    )
            _require(
                sorted(binding_ids) == sorted(candidate_ids)
                and len(binding_ids) == len(set(binding_ids)),
                f"{path}.tie.equal_time_proof.bindings",
                "equal-time bindings must cover candidates exactly once",
            )
            _require(
                tie["ordering_proof"] is None,
                f"{path}.tie.ordering_proof",
                "complete tie cannot carry ordering ambiguity",
            )
        elif tie["status"] == "ordering_ambiguous":
            _require(
                len(candidate_ids) >= 2,
                f"{path}.tie.candidate_ids",
                "ordering ambiguity needs at least two candidates",
            )
            proof = _require_exact_keys(
                tie["ordering_proof"],
                {
                    "candidate_intervals",
                    "all_candidates_isolated",
                    "only_remaining_uncertainty",
                },
                f"{path}.tie.ordering_proof",
            )
            _require(
                proof["all_candidates_isolated"] is True,
                f"{path}.tie.ordering_proof.all_candidates_isolated",
                "ambiguous tie candidates must all be isolated",
            )
            _require(
                proof["only_remaining_uncertainty"] == "earliest_order",
                f"{path}.tie.ordering_proof.only_remaining_uncertainty",
                "only exact earliest ordering may remain unresolved",
            )
            intervals = proof["candidate_intervals"]
            _require(
                type(intervals) is list,
                f"{path}.tie.ordering_proof.candidate_intervals",
                "expected an array",
            )
            interval_ids: list[str] = []
            parsed_intervals: list[tuple[Fraction, Fraction]] = []
            for index, row in enumerate(intervals):
                item = _require_exact_keys(
                    row,
                    {"candidate_id", "time_interval"},
                    f"{path}.tie.ordering_proof.candidate_intervals[{index}]",
                )
                interval_ids.append(
                    _require_string(
                        item["candidate_id"],
                        f"{path}.tie.ordering_proof.candidate_intervals[{index}].candidate_id",
                    )
                )
                parsed_intervals.append(
                    _validate_exact_interval(
                        item["time_interval"],
                        f"{path}.tie.ordering_proof.candidate_intervals[{index}].time_interval",
                    )
                )
            _require(
                sorted(interval_ids) == sorted(candidate_ids)
                and len(interval_ids) == len(set(interval_ids)),
                f"{path}.tie.ordering_proof.candidate_intervals",
                "ordering intervals must cover candidates exactly once",
            )
            _require(
                all(
                    max(left[0], right[0]) <= min(left[1], right[1])
                    for left_index, left in enumerate(parsed_intervals)
                    for right in parsed_intervals[left_index + 1 :]
                ),
                f"{path}.tie.ordering_proof.candidate_intervals",
                "candidate time intervals do not overlap",
            )
            _require(
                tie["equal_time_proof"] is None,
                f"{path}.tie.equal_time_proof",
                "ambiguous ordering cannot assert exact equality",
            )
        else:
            _require(
                not candidate_ids
                and tie["equal_time_proof"] is None
                and tie["ordering_proof"] is None,
                f"{path}.tie",
                "none tie certificate must be empty",
            )

    outer = _validate_optional_certificate(
        certs["outer_exit"],
        {
            "certificate_id",
            "observed",
            "grazing_touch_count",
            "strict_overshoot",
            "boundary_time",
            "post_boundary_interval",
            "post_boundary_witness",
            "rho_lower_bound",
            "r_out",
            "hysteresis_registry_id",
            "global_minimum_certificate_id",
            "coverage_manifest_sha256",
            "image_manifest_sha256",
            "rearmed",
        },
        f"{path}.outer_exit",
    )
    if outer is not None:
        _require_string(outer["certificate_id"], f"{path}.outer_exit.certificate_id")
        for name in ("observed", "strict_overshoot", "rearmed"):
            _require_bool(outer[name], f"{path}.outer_exit.{name}")
        grazing_count = _require_integer(
            outer["grazing_touch_count"],
            f"{path}.outer_exit.grazing_touch_count",
        )
        _require(
            grazing_count >= 0,
            f"{path}.outer_exit.grazing_touch_count",
            "grazing touch count must be nonnegative",
        )
        for name in ("boundary_time", "post_boundary_interval"):
            if outer[name] is not None:
                _validate_interval(
                    outer[name], f"{path}.outer_exit.{name}"
                )
        if outer["post_boundary_witness"] is not None:
            witness = _require_exact_keys(
                outer["post_boundary_witness"],
                {
                    "observable",
                    "exact_time_interval",
                    "time_interval_sha256",
                    "rho_affine",
                    "rho_range",
                    "backend",
                    "problem_commitment_sha256",
                    "model_id",
                    "model_sha256",
                },
                f"{path}.outer_exit.post_boundary_witness",
            )
            _require(
                witness["observable"] == "rho=sqrt(2F_min)",
                f"{path}.outer_exit.post_boundary_witness.observable",
                "outer witness is bound to wrong observable",
            )
            exact_time = _validate_exact_interval(
                witness["exact_time_interval"],
                f"{path}.outer_exit.post_boundary_witness.exact_time_interval",
            )
            _require_hash(
                witness["time_interval_sha256"],
                f"{path}.outer_exit.post_boundary_witness.time_interval_sha256",
            )
            affine = _require_exact_keys(
                witness["rho_affine"],
                {"slope", "intercept"},
                f"{path}.outer_exit.post_boundary_witness.rho_affine",
            )
            slope = _validate_dyadic(
                affine["slope"],
                f"{path}.outer_exit.post_boundary_witness.rho_affine.slope",
            )
            intercept = _validate_dyadic(
                affine["intercept"],
                f"{path}.outer_exit.post_boundary_witness.rho_affine.intercept",
            )
            rho_range = _validate_exact_interval(
                witness["rho_range"],
                f"{path}.outer_exit.post_boundary_witness.rho_range",
            )
            endpoint_values = (
                slope * exact_time[0] + intercept,
                slope * exact_time[1] + intercept,
            )
            _require(
                rho_range
                == (min(endpoint_values), max(endpoint_values)),
                f"{path}.outer_exit.post_boundary_witness.rho_range",
                "rho range does not replay from exact affine witness",
            )
            _require_string(
                witness["backend"],
                f"{path}.outer_exit.post_boundary_witness.backend",
            )
            _require_hash(
                witness["problem_commitment_sha256"],
                f"{path}.outer_exit.post_boundary_witness.problem_commitment_sha256",
            )
            _require_string(
                witness["model_id"],
                f"{path}.outer_exit.post_boundary_witness.model_id",
            )
            _require_hash(
                witness["model_sha256"],
                f"{path}.outer_exit.post_boundary_witness.model_sha256",
            )
        if outer["rho_lower_bound"] is not None:
            _require_number(
                outer["rho_lower_bound"],
                f"{path}.outer_exit.rho_lower_bound",
            )
        if outer["r_out"] is not None:
            _require_number(outer["r_out"], f"{path}.outer_exit.r_out")
        _require_string(
            outer["hysteresis_registry_id"],
            f"{path}.outer_exit.hysteresis_registry_id",
        )
        _require(
            outer["r_out"] is not None and outer["r_out"] > 0,
            f"{path}.outer_exit.r_out",
            "outer threshold must be positive",
        )
        for name in (
            "global_minimum_certificate_id",
            "coverage_manifest_sha256",
            "image_manifest_sha256",
        ):
            if outer[name] is not None:
                if name.endswith("sha256"):
                    _require_hash(outer[name], f"{path}.outer_exit.{name}")
                else:
                    _require_string(outer[name], f"{path}.outer_exit.{name}")
        if outer["boundary_time"] is not None:
            _validate_interval(outer["boundary_time"], f"{path}.outer_exit.boundary_time")
        if outer["strict_overshoot"]:
            _require(outer["observed"], f"{path}.outer_exit.observed", "strict overshoot requires observed exit")
            _require(outer["boundary_time"] is not None, f"{path}.outer_exit.boundary_time", "strict overshoot requires boundary time")
            _require(
                outer["post_boundary_interval"] is not None
                and outer["post_boundary_interval"]["lo"]
                > outer["boundary_time"]["hi"],
                f"{path}.outer_exit.post_boundary_interval",
                "strict exit needs a later post-boundary interval",
            )
            _require(
                outer["rho_lower_bound"] is not None
                and outer["r_out"] is not None
                and outer["r_out"] > 0
                and outer["rho_lower_bound"] > outer["r_out"],
                f"{path}.outer_exit.rho_lower_bound",
                "post-boundary certificate must prove rho>r_out",
            )
            _require(
                outer["post_boundary_witness"] is not None,
                f"{path}.outer_exit.post_boundary_witness",
                "strict exit requires replayable post-boundary witness",
            )
            _hash_binding(
                outer["post_boundary_interval"],
                outer["post_boundary_witness"][
                    "time_interval_sha256"
                ],
                f"{path}.outer_exit.post_boundary_witness.time_interval_sha256",
            )
            exact_post = _validate_exact_interval(
                outer["post_boundary_witness"]["exact_time_interval"],
                f"{path}.outer_exit.post_boundary_witness.exact_time_interval",
            )
            _require(
                (
                    float(exact_post[0]),
                    float(exact_post[1]),
                )
                == _float_interval_tuple(
                    outer["post_boundary_interval"]
                ),
                f"{path}.outer_exit.post_boundary_witness.exact_time_interval",
                "exact and serialized post-boundary intervals differ",
            )
            rho_range = _validate_exact_interval(
                outer["post_boundary_witness"]["rho_range"],
                f"{path}.outer_exit.post_boundary_witness.rho_range",
            )
            _require(
                float(rho_range[0]) == outer["rho_lower_bound"],
                f"{path}.outer_exit.rho_lower_bound",
                "rho lower bound is not bound to witness range",
            )
            for name in (
                "global_minimum_certificate_id",
                "coverage_manifest_sha256",
                "image_manifest_sha256",
            ):
                _require(
                    outer[name] is not None,
                    f"{path}.outer_exit.{name}",
                    "strict exit requires this proof reference",
                )
        else:
            _require(
                all(
                    outer[name] is None
                    for name in (
                        "boundary_time",
                        "post_boundary_interval",
                        "post_boundary_witness",
                        "rho_lower_bound",
                        "global_minimum_certificate_id",
                        "coverage_manifest_sha256",
                        "image_manifest_sha256",
                    )
                ),
                f"{path}.outer_exit",
                "uncertified exit cannot carry authoritative proof fields",
            )
        if outer["rearmed"]:
            _require(outer["strict_overshoot"], f"{path}.outer_exit.strict_overshoot", "rearming requires strict overshoot")

    no_entry = _validate_optional_certificate(
        certs["no_entry"],
        {
            "certificate_id",
            "mode",
            "coverage_manifest_sha256",
            "finite_window",
            "recurrence",
            "global_lower_bound",
        },
        f"{path}.no_entry",
    )
    if no_entry is not None:
        _require_string(no_entry["certificate_id"], f"{path}.no_entry.certificate_id")
        mode = _require_enum(
            no_entry["mode"],
            ("finite_window", "exact_common_period", "global_lower_bound"),
            f"{path}.no_entry.mode",
        )
        _require_hash(
            no_entry["coverage_manifest_sha256"],
            f"{path}.no_entry.coverage_manifest_sha256",
        )
        if mode == "finite_window":
            window = _require_exact_keys(
                no_entry["finite_window"],
                {"t0", "t1", "excluded_leaf_ids"},
                f"{path}.no_entry.finite_window",
            )
            t0 = _validate_dyadic(
                window["t0"], f"{path}.no_entry.finite_window.t0"
            )
            t1 = _validate_dyadic(
                window["t1"], f"{path}.no_entry.finite_window.t1"
            )
            _require(
                t0 < t1,
                f"{path}.no_entry.finite_window",
                "finite window must have positive length",
            )
            _validate_string_list(
                window["excluded_leaf_ids"],
                f"{path}.no_entry.finite_window.excluded_leaf_ids",
            )
            _require(
                no_entry["recurrence"] is None
                and no_entry["global_lower_bound"] is None,
                f"{path}.no_entry",
                "finite-window proof cannot claim a global argument",
            )
        elif mode == "exact_common_period":
            recurrence = _require_exact_keys(
                no_entry["recurrence"],
                {
                    "m",
                    "L_w",
                    "P",
                    "relative_velocity",
                    "transverse_periods",
                    "lattice_vector",
                    "time_seam_cover",
                    "backend",
                    "problem_commitment_sha256",
                },
                f"{path}.no_entry.recurrence",
            )
            m = _require_integer(
                recurrence["m"], f"{path}.no_entry.recurrence.m"
            )
            _require(
                m > 0,
                f"{path}.no_entry.recurrence.m",
                "m must be positive",
            )
            length = _validate_dyadic(
                recurrence["L_w"], f"{path}.no_entry.recurrence.L_w"
            )
            period = _validate_dyadic(
                recurrence["P"], f"{path}.no_entry.recurrence.P"
            )
            _require(
                length > 0 and period == m * length,
                f"{path}.no_entry.recurrence.P",
                "exact recurrence requires P=m L_w",
            )
            for name in ("relative_velocity", "transverse_periods"):
                _require(
                    type(recurrence[name]) is list
                    and len(recurrence[name]) == 8,
                    f"{path}.no_entry.recurrence.{name}",
                    "expected eight exact components",
                )
            velocities = [
                _validate_dyadic(
                    item,
                    f"{path}.no_entry.recurrence.relative_velocity[{index}]",
                )
                for index, item in enumerate(recurrence["relative_velocity"])
            ]
            periods = [
                _validate_dyadic(
                    item,
                    f"{path}.no_entry.recurrence.transverse_periods[{index}]",
                )
                for index, item in enumerate(
                    recurrence["transverse_periods"]
                )
            ]
            lattice_vector = recurrence["lattice_vector"]
            _require(
                type(lattice_vector) is list and len(lattice_vector) == 8,
                f"{path}.no_entry.recurrence.lattice_vector",
                "expected eight integer components",
            )
            for index, integer_value in enumerate(lattice_vector):
                integer = _require_integer(
                    integer_value,
                    f"{path}.no_entry.recurrence.lattice_vector[{index}]",
                )
                _require(
                    velocities[index] * period == integer * periods[index],
                    f"{path}.no_entry.recurrence.lattice_vector[{index}]",
                    "drift-period lattice equality is not exact",
                )
            seam = _require_exact_keys(
                recurrence["time_seam_cover"],
                {
                    "t0",
                    "tP",
                    "lattice_vector",
                    "state_t0",
                    "state_tP",
                    "wrapped_state_t0",
                    "wrapped_state_tP",
                    "coverage_manifest_sha256",
                },
                f"{path}.no_entry.recurrence.time_seam_cover",
            )
            seam_t0 = _validate_dyadic(
                seam["t0"], f"{path}.no_entry.recurrence.time_seam_cover.t0"
            )
            seam_tP = _validate_dyadic(
                seam["tP"], f"{path}.no_entry.recurrence.time_seam_cover.tP"
            )
            _require(
                seam_tP - seam_t0 == period,
                f"{path}.no_entry.recurrence.time_seam_cover",
                "time seam does not span one exact period",
            )
            _require(
                seam["lattice_vector"] == lattice_vector,
                f"{path}.no_entry.recurrence.time_seam_cover.lattice_vector",
                "time seam lattice map disagrees with recurrence",
            )
            seam_states: dict[str, list[Fraction]] = {}
            for name in (
                "state_t0",
                "state_tP",
                "wrapped_state_t0",
                "wrapped_state_tP",
            ):
                _require(
                    type(seam[name]) is list and len(seam[name]) == 8,
                    f"{path}.no_entry.recurrence.time_seam_cover.{name}",
                    "expected eight exact state components",
                )
                seam_states[name] = [
                    _validate_dyadic(
                        component,
                        f"{path}.no_entry.recurrence.time_seam_cover.{name}[{index}]",
                    )
                    for index, component in enumerate(seam[name])
                ]
            for index in range(8):
                _require(
                    periods[index] > 0,
                    f"{path}.no_entry.recurrence.transverse_periods[{index}]",
                    "transverse period must be positive",
                )
                _require(
                    seam_states["state_tP"][index]
                    - seam_states["state_t0"][index]
                    == velocities[index] * period,
                    f"{path}.no_entry.recurrence.time_seam_cover.state_tP[{index}]",
                    "endpoint state does not replay exact drift",
                )
                _require(
                    seam_states["wrapped_state_t0"][index]
                    == seam_states["state_t0"][index]
                    and seam_states["wrapped_state_tP"][index]
                    == seam_states["state_tP"][index]
                    - lattice_vector[index] * periods[index]
                    and seam_states["wrapped_state_tP"][index]
                    == seam_states["wrapped_state_t0"][index],
                    f"{path}.no_entry.recurrence.time_seam_cover",
                    "endpoint states do not close under lattice image map",
                )
            _require_hash(
                seam["coverage_manifest_sha256"],
                f"{path}.no_entry.recurrence.time_seam_cover.coverage_manifest_sha256",
            )
            _require(
                no_entry["finite_window"] is None
                and no_entry["global_lower_bound"] is None,
                f"{path}.no_entry",
                "recurrence mode has incompatible proof branches",
            )
            _require_string(
                recurrence["backend"],
                f"{path}.no_entry.recurrence.backend",
            )
            _require_hash(
                recurrence["problem_commitment_sha256"],
                f"{path}.no_entry.recurrence.problem_commitment_sha256",
            )
        else:
            lower_bound = _require_exact_keys(
                no_entry["global_lower_bound"],
                {
                    "observable",
                    "time_domain",
                    "rho_affine",
                    "rho_lower_bound",
                    "r_in",
                    "witness_range",
                    "backend",
                    "problem_commitment_sha256",
                    "model_id",
                    "model_sha256",
                },
                f"{path}.no_entry.global_lower_bound",
            )
            _require(
                lower_bound["observable"] == "rho=sqrt(2F_min)"
                and lower_bound["time_domain"] == "all_real",
                f"{path}.no_entry.global_lower_bound",
                "global bound is not bound to rho on all real time",
            )
            affine = _require_exact_keys(
                lower_bound["rho_affine"],
                {"slope", "intercept"},
                f"{path}.no_entry.global_lower_bound.rho_affine",
            )
            slope = _validate_dyadic(
                affine["slope"],
                f"{path}.no_entry.global_lower_bound.rho_affine.slope",
            )
            intercept = _validate_dyadic(
                affine["intercept"],
                f"{path}.no_entry.global_lower_bound.rho_affine.intercept",
            )
            _require(
                slope == 0,
                f"{path}.no_entry.global_lower_bound.rho_affine.slope",
                "affine witness is global on all real time only when slope=0",
            )
            bound = _validate_dyadic(
                lower_bound["rho_lower_bound"],
                f"{path}.no_entry.global_lower_bound.rho_lower_bound",
            )
            r_in = _validate_dyadic(
                lower_bound["r_in"],
                f"{path}.no_entry.global_lower_bound.r_in",
            )
            witness_lower, witness_upper = _validate_exact_interval(
                lower_bound["witness_range"],
                f"{path}.no_entry.global_lower_bound.witness_range",
            )
            _require(
                (witness_lower, witness_upper)
                == (intercept, intercept)
                and witness_lower >= bound > r_in,
                f"{path}.no_entry.global_lower_bound",
                "global lower bound does not exclude r_in",
            )
            _require_string(
                lower_bound["backend"],
                f"{path}.no_entry.global_lower_bound.backend",
            )
            _require_hash(
                lower_bound["problem_commitment_sha256"],
                f"{path}.no_entry.global_lower_bound.problem_commitment_sha256",
            )
            _require_string(
                lower_bound["model_id"],
                f"{path}.no_entry.global_lower_bound.model_id",
            )
            _require_hash(
                lower_bound["model_sha256"],
                f"{path}.no_entry.global_lower_bound.model_sha256",
            )
            _require(
                no_entry["finite_window"] is None
                and no_entry["recurrence"] is None,
                f"{path}.no_entry",
                "global-bound mode has incompatible proof branches",
            )

    unresolved = _validate_optional_certificate(
        certs["unresolved"],
        {
            "certificate_id",
            "coverage_manifest_sha256",
            "reason_codes",
            "unresolved_leaf_ids",
        },
        f"{path}.unresolved",
    )
    if unresolved is not None:
        _require_string(unresolved["certificate_id"], f"{path}.unresolved.certificate_id")
        reasons = _validate_string_list(unresolved["reason_codes"], f"{path}.unresolved.reason_codes")
        _require(bool(reasons), f"{path}.unresolved.reason_codes", "unresolved record needs a reason")
        _require_hash(
            unresolved["coverage_manifest_sha256"],
            f"{path}.unresolved.coverage_manifest_sha256",
        )
        unresolved_ids = _validate_string_list(
            unresolved["unresolved_leaf_ids"],
            f"{path}.unresolved.unresolved_leaf_ids",
        )
        _require(
            bool(unresolved_ids)
            and len(unresolved_ids) == len(set(unresolved_ids)),
            f"{path}.unresolved.unresolved_leaf_ids",
            "unresolved manifest needs unique leaf IDs",
        )

    closest = _validate_optional_certificate(
        certs["closest"],
        {
            "certificate_id",
            "status",
            "time",
            "episode_id",
            "coverage_manifest_sha256",
            "global_minimum_certificate_id",
        },
        f"{path}.closest",
    )
    if closest is not None:
        _require_string(closest["certificate_id"], f"{path}.closest.certificate_id")
        _require_enum(
            closest["status"],
            ("none", "episode_complete", "window_only", "unresolved"),
            f"{path}.closest.status",
        )
        if closest["status"] in ("episode_complete", "window_only"):
            _require(
                closest["time"] is not None,
                f"{path}.closest.time",
                "identified closest point requires time",
            )
            _validate_interval(closest["time"], f"{path}.closest.time")
            _require_string(
                closest["episode_id"], f"{path}.closest.episode_id"
            )
            _require_hash(
                closest["coverage_manifest_sha256"],
                f"{path}.closest.coverage_manifest_sha256",
            )
            _require_string(
                closest["global_minimum_certificate_id"],
                f"{path}.closest.global_minimum_certificate_id",
            )
        else:
            _require(
                all(
                    closest[name] is None
                    for name in (
                        "time",
                        "episode_id",
                        "coverage_manifest_sha256",
                        "global_minimum_certificate_id",
                    )
                ),
                f"{path}.closest",
                "unidentified closest point cannot carry proof fields",
            )
    return certs


def classify_primary(flags: dict[str, bool]) -> str:
    """Apply the rank-blind, deterministic primary-outcome precedence."""

    if not flags["source_valid"] or not flags["history_valid"]:
        return "source_invalid"
    if flags["left_censored"]:
        return "left_censored_active_episode"
    if flags["torus_branch_ambiguous"]:
        return "torus_branch_ambiguous"
    if flags["ambiguous_tie"]:
        return "ambiguous_tie"
    if not flags["solver_complete"] or flags["entry_direction_inconsistent"]:
        return "numerically_unresolved"
    if not flags["entry_observed"]:
        if flags["no_entry_complete_time_domain_certified"]:
            return "no_entry_proved"
        return "right_censored_no_entry"
    if not flags["outer_exit_certified"]:
        return "right_censored_active_episode"
    if flags["entry_tied"] or flags["entry_positive_dimensional"]:
        return "tie_cluster"
    if flags["entry_has_spatial_degeneracy"]:
        return "degenerate_spatial_minimum"
    if flags["entry_has_grazing"]:
        return "grazing_entry"
    if flags["entry_geometry_regular"]:
        return "regular_first_entry"
    return "numerically_unresolved"


def precedence_trace(primary: str) -> list[str]:
    _require(primary in PRIMARY_PRECEDENCE, "$.primary_outcome", "unknown primary outcome")
    index = PRIMARY_PRECEDENCE.index(primary)
    return list(PRIMARY_PRECEDENCE[: index + 1])


def _validate_rank_mark_flags(
    cluster: dict[str, Any] | None,
    flags: dict[str, bool],
) -> None:
    if cluster is None:
        expected_rank = False
        expected_normal = False
    elif cluster["representation"] == "implicit":
        implicit = cluster["implicit_set"]
        expected_rank = implicit["jet_field_certificate_ref"] is not None
        expected_normal = (
            expected_rank
            and implicit["normal_field_certificate_ref"] is not None
        )
    else:
        statuses = [
            member["jet_normal"]["rank"]["status"]
            for member in cluster["members"]
        ]
        expected_rank = bool(statuses) and all(
            status == "certified" for status in statuses
        )
        expected_normal = expected_rank and all(
            member["jet_normal"]["P_N"] is not None
            for member in cluster["members"]
        )
    _require(
        flags["rank_marks_complete"] == expected_rank,
        "$.flags.rank_marks_complete",
        "rank completeness flag disagrees with cluster marks",
    )
    _require(
        flags["normal_marks_complete"] == expected_normal,
        "$.flags.normal_marks_complete",
        "normal completeness flag disagrees with cluster marks",
    )


def _require_certificate(
    certificates: dict[str, Any], name: str, primary: str
) -> dict[str, Any]:
    value = certificates[name]
    _require(
        value is not None,
        f"$.certificates.{name}",
        f"{primary} requires this certificate",
    )
    return value


def _validate_outcome_semantics(record: dict[str, Any]) -> None:
    flags = record["flags"]
    source = record["source"]
    observation = record["observation"]
    cluster = record["entry_cluster"]
    certs = record["certificates"]
    primary = record["primary_outcome"]

    _require(
        flags["source_valid"] == source["source_valid"]
        and flags["history_valid"] == source["history_valid"],
        "$.flags",
        "source/history flags disagree with source block",
    )
    _require(
        primary == classify_primary(flags),
        "$.primary_outcome",
        "primary outcome violates deterministic precedence",
    )
    _require(
        record["precedence_trace"] == precedence_trace(primary),
        "$.precedence_trace",
        "precedence trace does not end at selected primary",
    )
    source_certificate = _require_certificate(
        certs, "source_validity", primary
    )
    _require(
        source_certificate["reason_codes"]
        == source["invalid_reasons"],
        "$.certificates.source_validity.reason_codes",
        "source predicate reasons disagree with the source record",
    )

    if primary == "source_invalid":
        _require(
            source["source_valid"] is False
            and source["history_valid"] is False
            and source["initial_state"] == "unknown",
            "$.source",
            "source-invalid record must freeze source/history as invalid",
        )
        _require(
            all(value is False for value in flags.values()),
            "$.flags",
            "source-invalid record must freeze all event flags false",
        )
        _require(
            cluster is None and record["episodes"] == [],
            "$",
            "source-invalid record cannot contain events or episodes",
        )
        _require(
            source_certificate["status"] == "invalid",
            "$.certificates.source_validity.status",
            "invalid source needs invalid source certificate",
        )
        _require(
            all(
                value is None
                for name, value in certs.items()
                if name != "source_validity"
            ),
            "$.certificates",
            "source-invalid record may contain only source_validity",
        )
        _require(
            observation["continuation_state"] == "invalid",
            "$.observation.continuation_state",
            "source-invalid continuation must be invalid",
        )
        return

    _require(
        source["source_valid"] and source["history_valid"],
        "$.source",
        "non-invalid outcomes require valid source and history",
    )
    _require(
        source_certificate["status"] == "valid",
        "$.certificates.source_validity.status",
        "valid source needs valid source certificate",
    )
    _require(
        flags["initial_armed"] == (source["initial_state"] == "armed"),
        "$.flags.initial_armed",
        "initial-armed flag disagrees with source",
    )

    torus = certs["torus_log"]
    if torus is None:
        _require(
            not flags["torus_log_unique"]
            and not flags["torus_branch_ambiguous"],
            "$.flags.torus_log_unique",
            "torus flags require a certificate",
        )
    else:
        _require(
            flags["torus_log_unique"] == torus["unique"]
            and flags["torus_branch_ambiguous"] == (not torus["unique"]),
            "$.flags.torus_log_unique",
            "torus flags disagree with certificate",
        )

    coverage_certificate = certs["root_coverage"]
    coverage_maps: dict[str, Any] | None = None
    problem_commitment_sha256: str | None = None
    problem_commitment: dict[str, Any] | None = None
    problem_model_map: dict[str, dict[str, Any]] = {}
    representative_candidate_ids: list[str] = []
    unresolved_ids: list[str] = []
    event_order_unresolved: list[str] = []
    if coverage_certificate is not None:
        coverage_maps = coverage.manifest_maps(coverage_certificate)
        (
            problem_commitment_sha256,
            problem_commitment,
            problem_model_map,
        ) = _coverage_problem_context(coverage_certificate)
        representative_candidate_ids = (
            coverage.physical_representative_candidate_ids(
                coverage_certificate
            )
        )
        unresolved_ids = coverage.unresolved_leaf_ids(
            coverage_certificate
        )
        event_order_unresolved = coverage.unresolved_leaf_ids(
            coverage_certificate, event_order_relevant_only=True
        )
        committed_observation = coverage.interval_fractions(
            problem_commitment["observation_window"]
        )
        _require(
            (
                Fraction(str(observation["t0"])),
                Fraction(str(observation["t1"])),
            )
            == committed_observation,
            "$.observation",
            "observation window differs from the committed event problem",
        )
        committed_source_state = problem_commitment[
            "source_state_registry"
        ]
        _require(
            source["initial_state"]
            == committed_source_state["initial_state"],
            "$.source.initial_state",
            "initial history differs from the committed event problem",
        )
        _require(
            source["sampling_registry_hash"]
            == problem_commitment["source_draw_registry_sha256"]
            and source["classification_registry_hash"]
            == problem_commitment["source_registry_sha256"],
            "$.source",
            "source/event registries are not bound to the problem commitment",
        )
        expected_registry_hash = canonical_sha256(
            {
                "source_registry_sha256": problem_commitment[
                    "source_registry_sha256"
                ],
                "source_draw_registry_sha256": problem_commitment[
                    "source_draw_registry_sha256"
                ],
                "source_state_sha256": problem_commitment[
                    "source_state_sha256"
                ],
                "solver_registry_sha256": problem_commitment[
                    "solver_registry_sha256"
                ],
                "problem_commitment_sha256": (
                    problem_commitment_sha256
                ),
            }
        )
        _require(
            record["registry_hash"] == expected_registry_hash,
            "$.registry_hash",
            "run registry does not bind source, solver and problem commitments",
        )
    coverage_complete = (
        coverage_certificate is not None and not unresolved_ids
    )
    if torus is not None and coverage_certificate is not None:
        _require(
            torus["image_manifest_hash"]
            == coverage.image_manifest_sha256(coverage_certificate),
            "$.certificates.torus_log.image_manifest_hash",
            "torus certificate references wrong image manifest",
        )
    _require(
        flags["root_coverage_complete"] == coverage_complete,
        "$.flags.root_coverage_complete",
        "coverage flag must be derived from replayed leaves",
    )
    _require(
        flags["solver_complete"] == coverage_complete,
        "$.flags.solver_complete",
        "solver-complete flag must be derived from replayed coverage",
    )
    if event_order_unresolved:
        _require(
            primary == "numerically_unresolved",
            "$.primary_outcome",
            "event-order-relevant unresolved leaf forces numerical outcome",
        )

    if cluster is None:
        _require(
            not flags["entry_observed"]
            and not flags["entry_cluster_complete"]
            and not flags["entry_tied"]
            and not flags["entry_positive_dimensional"],
            "$.entry_cluster",
            "missing cluster cannot carry entry-cluster flags",
        )
        cluster_candidate_ids: list[str] = []
        derived_regular = derived_grazing = derived_degenerate = False
    else:
        cluster_candidate_ids = sorted(
            (
                cluster["implicit_set"]["candidate_ids"]
                if cluster["representation"] == "implicit"
                else [
                    member["candidate_id"]
                    for member in cluster["members"]
                ]
            )
        )
        _require(
            cluster_candidate_ids == sorted(representative_candidate_ids),
            "$.entry_cluster",
            "cluster candidate IDs must exactly match physical coverage candidates",
        )
        if cluster["representation"] == "implicit":
            _require(
                coverage_maps is not None,
                "$.entry_cluster.implicit_set",
                "implicit set requires coverage proof",
            )
            certified_boxes: list[dict[str, Any]] = []
            set_hashes: set[str] = set()
            for candidate_id in cluster_candidate_ids:
                candidate = coverage_maps["candidates"][candidate_id]
                leaf = coverage_maps["leaves"][candidate["leaf_id"]]
                _require(
                    leaf["classification"]
                    == "certified_singular_cluster",
                    "$.entry_cluster.implicit_set",
                    "implicit candidate lacks singular-set leaf",
                )
                witness = leaf["witness"]
                set_hashes.add(witness["set_certificate_sha256"])
                affine_set = witness["affine_set"]
                base = [
                    coverage.as_fraction(component)
                    for component in affine_set["base_point"]
                ]
                direction = [
                    coverage.as_fraction(component)
                    for component in affine_set["null_direction"]
                ]
                parameter_lower, parameter_upper = (
                    coverage.interval_fractions(
                        affine_set["parameter_interval"]
                    )
                )
                endpoints = [
                    [
                        base[index] + parameter * direction[index]
                        for index in range(3)
                    ]
                    for parameter in (
                        parameter_lower,
                        parameter_upper,
                    )
                ]
                certified_boxes.append(
                    {
                        axis: {
                            "lo": float(
                                min(
                                    endpoints[0][index],
                                    endpoints[1][index],
                                )
                            ),
                            "hi": float(
                                max(
                                    endpoints[0][index],
                                    endpoints[1][index],
                                )
                            ),
                        }
                        for index, axis in enumerate(
                            ("sigma1", "sigma2", "time")
                        )
                    }
                )
            _require(
                len(set_hashes) == 1
                and cluster["implicit_set"]["set_certificate_ref"]
                in set_hashes,
                "$.entry_cluster.implicit_set.set_certificate_ref",
                "implicit set reference does not bind singular proof content",
            )
            _require(
                sorted(
                    cluster["implicit_set"]["domain_boxes"],
                    key=canonical_sha256,
                )
                == sorted(certified_boxes, key=canonical_sha256),
                "$.entry_cluster.implicit_set.domain_boxes",
                "implicit domain boxes do not replay from singular set",
            )
        else:
            member_by_candidate = {
                member["candidate_id"]: member
                for member in cluster["members"]
            }
            for candidate_id in cluster_candidate_ids:
                member = member_by_candidate[candidate_id]
                candidate = coverage_maps["candidates"][candidate_id]
                sigma1, sigma2, exact_time = (
                    coverage.candidate_certified_coordinates(
                        coverage_certificate, candidate_id
                    )
                )
                _require(
                    member["box"]["sigma1"]
                    == {"lo": float(sigma1), "hi": float(sigma1)}
                    and member["box"]["sigma2"]
                    == {"lo": float(sigma2), "hi": float(sigma2)},
                    "$.entry_cluster.members",
                    "representative spatial box is not bound to root proof",
                )
                candidate_time = coverage.interval_fractions(
                    candidate["time_interval"]
                )
                expected_time = (
                    (exact_time, exact_time)
                    if exact_time is not None
                    else candidate_time
                )
                _require(
                    member["box"]["time"]
                    == {
                        "lo": float(expected_time[0]),
                        "hi": float(expected_time[1]),
                    },
                    "$.entry_cluster.members",
                    "representative time box is not bound to root proof",
                )
                image = coverage_maps["images"][candidate["image_id"]]
                _require(
                    member["torus_image"] == image["lattice_vector"],
                    "$.entry_cluster.members",
                    "representative torus image disagrees with coverage image",
                )
        _require(
            flags["entry_observed"],
            "$.flags.entry_observed",
            "entry cluster requires observed-entry flag",
        )
        _require(
            flags["entry_cluster_complete"] == cluster["complete"],
            "$.flags.entry_cluster_complete",
            "cluster completeness flag disagrees with cluster",
        )
        _require(
            flags["entry_tied"]
            == (cluster["representation"] != "singleton"),
            "$.flags.entry_tied",
            "tie flag disagrees with cluster representation",
        )
        _require(
            flags["entry_positive_dimensional"]
            == (cluster["representation"] == "implicit"),
            "$.flags.entry_positive_dimensional",
            "positive-dimensional flag disagrees with cluster",
        )
        marks = [
            _geometry_marks(member) for member in cluster["members"]
        ]
        derived_regular = (
            cluster["representation"] == "singleton"
            and bool(marks)
            and marks[0][0]
        )
        derived_grazing = any(mark[1] for mark in marks)
        derived_degenerate = any(mark[2] for mark in marks)
    _require(
        flags["entry_geometry_regular"] == derived_regular,
        "$.flags.entry_geometry_regular",
        "regular flag must be derived from H positive-definite and F_t<0",
    )
    _require(
        flags["entry_has_grazing"] == derived_grazing,
        "$.flags.entry_has_grazing",
        "grazing flag must be derived from exact-zero multiplicity proof",
    )
    _require(
        flags["entry_has_spatial_degeneracy"] == derived_degenerate,
        "$.flags.entry_has_spatial_degeneracy",
        "degeneracy flag must be derived from PSD singular Hessian proof",
    )
    _validate_rank_mark_flags(cluster, flags)

    global_certificate = certs["global_minimum"]
    no_earlier_certificate = certs["no_earlier_entry"]
    _require(
        flags["global_minimum_certified"]
        == (global_certificate is not None),
        "$.flags.global_minimum_certified",
        "global-minimum flag and certificate must be bidirectional",
    )
    _require(
        flags["no_earlier_entry_certified"]
        == (no_earlier_certificate is not None),
        "$.flags.no_earlier_entry_certified",
        "no-earlier flag and certificate must be bidirectional",
    )
    _require(
        flags["entry_earliest_certified"]
        == (
            global_certificate is not None
            and no_earlier_certificate is not None
        ),
        "$.flags.entry_earliest_certified",
        "earliest-entry flag must be derived from both certificates",
    )

    if coverage_maps is not None:
        manifest_hash = coverage_certificate["manifest_sha256"]
        candidates = coverage_maps["candidates"]
        leaves = coverage_maps["leaves"]
        excluded_leaf_ids = sorted(
            leaf_id
            for leaf_id, leaf in leaves.items()
            if leaf["classification"] == "excluded"
        )
        if global_certificate is not None:
            _require(
                global_certificate["coverage_manifest_sha256"]
                == manifest_hash,
                "$.certificates.global_minimum.coverage_manifest_sha256",
                "global proof references wrong coverage manifest",
            )
            _require(
                sorted(global_certificate["candidate_ids"])
                == sorted(representative_candidate_ids),
                "$.certificates.global_minimum.candidate_ids",
                "global proof does not cover all physical candidates",
            )
            _require(
                sorted(global_certificate["minimizer_candidate_ids"])
                == cluster_candidate_ids,
                "$.certificates.global_minimum.minimizer_candidate_ids",
                "global minimizers do not match cluster",
            )
            _require(
                sorted(global_certificate["excluded_leaf_ids"])
                == excluded_leaf_ids,
                "$.certificates.global_minimum.excluded_leaf_ids",
                "global proof does not bind every excluded leaf",
            )
            binding_map = {
                row["candidate_id"]: row
                for row in global_certificate["candidate_time_bindings"]
            }
            _require(
                set(binding_map) == set(representative_candidate_ids),
                "$.certificates.global_minimum.candidate_time_bindings",
                "global time bindings do not cover candidates exactly",
            )
            earliest = _validate_dyadic(
                global_certificate["earliest_time"],
                "$.certificates.global_minimum.earliest_time",
            )
            minimizers = set(
                global_certificate["minimizer_candidate_ids"]
            )
            for candidate_id in representative_candidate_ids:
                candidate = candidates[candidate_id]
                _hash_binding(
                    candidate["time_interval"],
                    binding_map[candidate_id]["time_interval_sha256"],
                    "$.certificates.global_minimum.candidate_time_bindings",
                )
                lower, upper = coverage.interval_fractions(
                    candidate["time_interval"]
                )
                if candidate_id in minimizers:
                    certified_time = coverage.candidate_certified_time(
                        coverage_certificate, candidate_id
                    )
                    _require(
                        certified_time is not None
                        and earliest == certified_time
                        and lower <= earliest <= upper,
                        "$.certificates.global_minimum.earliest_time",
                        "global earliest time is not bound to exact root witness",
                    )
                else:
                    _require(
                        lower > earliest,
                        "$.certificates.global_minimum",
                        "non-minimizer is not certified later",
                    )
        if no_earlier_certificate is not None:
            _require(
                no_earlier_certificate["coverage_manifest_sha256"]
                == manifest_hash,
                "$.certificates.no_earlier_entry.coverage_manifest_sha256",
                "no-earlier proof references wrong manifest",
            )
            _require(
                sorted(no_earlier_certificate["candidate_ids"])
                == cluster_candidate_ids,
                "$.certificates.no_earlier_entry.candidate_ids",
                "no-earlier candidates do not match cluster",
            )
            earliest = _validate_dyadic(
                no_earlier_certificate["earliest_time"],
                "$.certificates.no_earlier_entry.earliest_time",
            )
            if global_certificate is not None:
                _require(
                    earliest
                    == _validate_dyadic(
                        global_certificate["earliest_time"],
                        "$.certificates.global_minimum.earliest_time",
                    ),
                    "$.certificates.no_earlier_entry.earliest_time",
                    "global and no-earlier proofs must bind the same earliest time",
                )
            for candidate_id in no_earlier_certificate["candidate_ids"]:
                candidate_lower, candidate_upper = (
                    coverage.interval_fractions(
                        candidates[candidate_id]["time_interval"]
                    )
                )
                _require(
                    coverage.candidate_certified_time(
                        coverage_certificate, candidate_id
                    )
                    == earliest
                    and candidate_lower <= earliest <= candidate_upper,
                    "$.certificates.no_earlier_entry.earliest_time",
                    "no-earlier time is not bound to a declared candidate",
                )
            expected_earlier_leaves: list[str] = []
            for leaf_id, leaf in leaves.items():
                if leaf["classification"] != "excluded":
                    continue
                node = coverage_maps["nodes"][leaf["node_id"]]
                _, upper = coverage.interval_fractions(node["box"]["time"])
                if upper <= earliest:
                    expected_earlier_leaves.append(leaf_id)
            _require(
                sorted(no_earlier_certificate["excluded_before_leaf_ids"])
                == sorted(expected_earlier_leaves),
                "$.certificates.no_earlier_entry.excluded_before_leaf_ids",
                "no-earlier proof does not bind the complete earlier cover",
            )
            history_lower, _ = _validate_exact_interval(
                no_earlier_certificate["history_interval"],
                "$.certificates.no_earlier_entry.history_interval",
            )
            armed_time = _validate_dyadic(
                no_earlier_certificate["initial_armed_witness"]["time"],
                "$.certificates.no_earlier_entry.initial_armed_witness.time",
            )
            _require(
                armed_time == history_lower
                and float(armed_time) == observation["t0"],
                "$.certificates.no_earlier_entry.initial_armed_witness.time",
                "armed witness must bind observation/history start",
            )
            assert (
                problem_commitment_sha256 is not None
                and problem_commitment is not None
            )
            threshold_registry = problem_commitment[
                "threshold_registry"
            ]
            _require(
                no_earlier_certificate["hysteresis_registry_id"]
                == threshold_registry["registry_id"]
                and _validate_dyadic(
                    no_earlier_certificate["r_in"],
                    "$.certificates.no_earlier_entry.r_in",
                )
                == coverage.as_fraction(threshold_registry["r_in"]),
                "$.certificates.no_earlier_entry",
                "inner threshold differs from committed hysteresis registry",
            )
            armed_witness = no_earlier_certificate[
                "initial_armed_witness"
            ]
            source_state_registry = problem_commitment[
                "source_state_registry"
            ]
            _require(
                armed_witness["time"]
                == source_state_registry["initial_time"]
                and armed_witness["rho_affine"]
                == source_state_registry["initial_rho_affine"],
                "$.certificates.no_earlier_entry.initial_armed_witness",
                "armed witness differs from committed source history",
            )
            _require_registered_problem_model(
                witness=armed_witness,
                expected_payload={
                    "model_kind": "rho_affine",
                    "model": {
                        "observable": armed_witness["observable"],
                        "time_domain": "initial_time",
                        "rho_affine": armed_witness["rho_affine"],
                    },
                },
                commitment_sha256=problem_commitment_sha256,
                model_map=problem_model_map,
                expected_suffix="initial-armed-rho",
                path=(
                    "$.certificates.no_earlier_entry."
                    "initial_armed_witness"
                ),
            )

    tie_certificate = certs["tie"]
    if tie_certificate is not None and cluster is not None:
        _require(
            sorted(tie_certificate["candidate_ids"])
            == cluster_candidate_ids,
            "$.certificates.tie.candidate_ids",
            "tie candidate IDs must exactly match cluster members",
        )
        if tie_certificate["status"] == "complete_cluster":
            _require(
                cluster["complete"]
                and cluster["representation"] in ("finite", "implicit"),
                "$.entry_cluster",
                "complete tie requires a complete non-singleton cluster",
            )
            exact_time = _validate_dyadic(
                tie_certificate["equal_time_proof"]["exact_time"],
                "$.certificates.tie.equal_time_proof.exact_time",
            )
            member_map = {
                member["candidate_id"]: member
                for member in cluster["members"]
            }
            binding_map = {
                row["candidate_id"]: row
                for row in tie_certificate["equal_time_proof"]["bindings"]
            }
            for candidate_id in cluster_candidate_ids:
                candidate = coverage_maps["candidates"][candidate_id]
                binding = binding_map[candidate_id]
                if cluster["representation"] == "implicit":
                    member_time = cluster["implicit_set"]["domain_boxes"][0][
                        "time"
                    ]
                    expected_representative = cluster["implicit_set"][
                        "set_certificate_ref"
                    ]
                else:
                    member = member_map[candidate_id]
                    member_time = member["box"]["time"]
                    expected_representative = member["representative_id"]
                _require(
                    binding["representative_id"]
                    == expected_representative,
                    "$.certificates.tie.equal_time_proof.bindings",
                    "equal-time proof binds wrong representative/set",
                )
                _hash_binding(
                    member_time,
                    binding["member_time_sha256"],
                    "$.certificates.tie.equal_time_proof.bindings",
                )
                _hash_binding(
                    candidate["time_interval"],
                    binding["candidate_time_sha256"],
                    "$.certificates.tie.equal_time_proof.bindings",
                )
                _require(
                    member_time["lo"]
                    <= float(exact_time)
                    <= member_time["hi"],
                    "$.entry_cluster.members",
                    "member time box excludes exact tie time",
                )
                lower, upper = coverage.interval_fractions(
                    candidate["time_interval"]
                )
                _require(
                    lower <= exact_time <= upper,
                    "$.certificates.tie.equal_time_proof",
                    "candidate interval excludes exact tie time",
                )
                _require(
                    coverage.candidate_certified_time(
                        coverage_certificate, candidate_id
                    )
                    == exact_time,
                    "$.certificates.tie.equal_time_proof",
                    "equal-time proof is not bound to exact root witness",
                )
        elif tie_certificate["status"] == "ordering_ambiguous":
            _require(
                primary == "ambiguous_tie"
                and cluster["representation"] == "finite"
                and not cluster["complete"]
                and len(cluster_candidate_ids) >= 2
                and coverage_complete
                and not unresolved_ids,
                "$.entry_cluster",
                "ordering ambiguity is not an eligible ambiguous tie",
            )
            _require(
                all(
                    leaves[candidates[candidate_id]["leaf_id"]][
                        "classification"
                    ]
                    == "unique_root"
                    for candidate_id in cluster_candidate_ids
                ),
                "$.certificates.tie.ordering_proof",
                "ambiguous-tie candidates must all be isolated",
            )
            _require(
                all(
                    member["geometry_certificate"]["hessian_class"]
                    != "unresolved"
                    and member["geometry_certificate"]["flux_class"]
                    != "unresolved"
                    and member["jet_normal"]["rank"]["status"]
                    == "certified"
                    and member["log_unique"]
                    for member in cluster["members"]
                ),
                "$.entry_cluster.members",
                "ambiguous tie may leave only earliest ordering unresolved",
            )
            interval_map = {
                row["candidate_id"]: row["time_interval"]
                for row in tie_certificate["ordering_proof"][
                    "candidate_intervals"
                ]
            }
            for candidate_id in cluster_candidate_ids:
                _require(
                    type_strict_equal(
                        interval_map[candidate_id],
                        candidates[candidate_id]["time_interval"],
                    ),
                    "$.certificates.tie.ordering_proof.candidate_intervals",
                    "ordering interval is not bound to coverage candidate",
                )

    no_entry = certs["no_entry"]
    finite_no_entry = (
        no_entry is not None and no_entry["mode"] == "finite_window"
    )
    complete_no_entry = (
        no_entry is not None
        and no_entry["mode"]
        in ("exact_common_period", "global_lower_bound")
    )
    _require(
        flags["no_entry_window_certified"] == finite_no_entry,
        "$.flags.no_entry_window_certified",
        "finite-window no-entry flag must be bidirectional",
    )
    _require(
        flags["no_entry_complete_time_domain_certified"]
        == complete_no_entry,
        "$.flags.no_entry_complete_time_domain_certified",
        "complete-time no-entry flag must be bidirectional",
    )
    if no_entry is not None:
        _require(
            coverage_certificate is not None
            and no_entry["coverage_manifest_sha256"]
            == coverage_certificate["manifest_sha256"],
            "$.certificates.no_entry.coverage_manifest_sha256",
            "no-entry proof references wrong coverage",
        )
        _require(
            not representative_candidate_ids
            and coverage_complete
            and all(
                leaf["classification"] == "excluded"
                for leaf in coverage_certificate["manifest"]["leaves"]
            ),
            "$.certificates.root_coverage",
            "no-entry proof requires a complete all-excluded cover",
        )
        if finite_no_entry:
            expected_excluded = sorted(
                leaf["leaf_id"]
                for leaf in coverage_certificate["manifest"]["leaves"]
            )
            _require(
                sorted(no_entry["finite_window"]["excluded_leaf_ids"])
                == expected_excluded,
                "$.certificates.no_entry.finite_window.excluded_leaf_ids",
                "finite-window proof must bind all leaves",
            )
            finite_t0 = _validate_dyadic(
                no_entry["finite_window"]["t0"],
                "$.certificates.no_entry.finite_window.t0",
            )
            finite_t1 = _validate_dyadic(
                no_entry["finite_window"]["t1"],
                "$.certificates.no_entry.finite_window.t1",
            )
            _require(
                float(finite_t0) == observation["t0"]
                and float(finite_t1) == observation["t1"],
                "$.certificates.no_entry.finite_window",
                "finite-window proof endpoints must equal observation window",
            )
            _require(
                all(
                    coverage.interval_fractions(domain["box"]["time"])
                    == (finite_t0, finite_t1)
                    for domain in coverage_certificate["manifest"][
                        "initial_domains"
                    ]
                ),
                "$.certificates.root_coverage",
                "coverage domains do not span the finite observation window",
            )
        if complete_no_entry and no_entry["mode"] == "exact_common_period":
            _require(
                no_entry["recurrence"]["time_seam_cover"][
                    "coverage_manifest_sha256"
                ]
                == coverage_certificate["manifest_sha256"],
                "$.certificates.no_entry.recurrence.time_seam_cover",
                "time-seam cover references wrong manifest",
            )
            seam = no_entry["recurrence"]["time_seam_cover"]
            seam_interval = (
                _validate_dyadic(
                    seam["t0"],
                    "$.certificates.no_entry.recurrence.time_seam_cover.t0",
                ),
                _validate_dyadic(
                    seam["tP"],
                    "$.certificates.no_entry.recurrence.time_seam_cover.tP",
                ),
            )
            _require(
                all(
                    coverage.interval_fractions(domain["box"]["time"])
                    == seam_interval
                    for domain in coverage_certificate["manifest"][
                        "initial_domains"
                    ]
                ),
                "$.certificates.no_entry.recurrence.time_seam_cover",
                "coverage domains do not cover the exact time seam",
            )
        assert (
            problem_commitment_sha256 is not None
            and problem_commitment is not None
        )
        thresholds = problem_commitment["threshold_registry"]
        committed_r_in = coverage.as_fraction(thresholds["r_in"])
        if complete_no_entry:
            source_state_registry = problem_commitment[
                "source_state_registry"
            ]
            initial_time = coverage.as_fraction(
                source_state_registry["initial_time"]
            )
            initial_affine = source_state_registry[
                "initial_rho_affine"
            ]
            initial_rho = (
                coverage.as_fraction(initial_affine["slope"])
                * initial_time
                + coverage.as_fraction(initial_affine["intercept"])
            )
            _require(
                source_state_registry["initial_state"] == "armed"
                and initial_rho > committed_r_in,
                "$.certificates.no_entry",
                "complete-time no-entry lacks committed armed initial history",
            )
        if no_entry["mode"] == "exact_common_period":
            recurrence = no_entry["recurrence"]
            _require(
                recurrence["problem_commitment_sha256"]
                == problem_commitment_sha256,
                "$.certificates.no_entry.recurrence.problem_commitment_sha256",
                "recurrence is not bound to the event problem",
            )
        if no_entry["mode"] == "global_lower_bound":
            lower_bound = no_entry["global_lower_bound"]
            _require(
                _validate_dyadic(
                    lower_bound["r_in"],
                    "$.certificates.no_entry.global_lower_bound.r_in",
                )
                == committed_r_in,
                "$.certificates.no_entry.global_lower_bound.r_in",
                "global lower bound uses an unregistered inner threshold",
            )
            _require_registered_problem_model(
                witness=lower_bound,
                expected_payload={
                    "model_kind": "rho_affine",
                    "model": {
                        "observable": lower_bound["observable"],
                        "time_domain": lower_bound["time_domain"],
                        "rho_affine": lower_bound["rho_affine"],
                    },
                },
                commitment_sha256=problem_commitment_sha256,
                model_map=problem_model_map,
                expected_suffix="global-no-entry-rho",
                path="$.certificates.no_entry.global_lower_bound",
            )
    _require(
        observation["complete_time_domain"] == complete_no_entry,
        "$.observation.complete_time_domain",
        "complete-time-domain status must be proof derived",
    )

    outer = certs["outer_exit"]
    _require(
        flags["outer_exit_observed"]
        == (outer is not None and outer["observed"]),
        "$.flags.outer_exit_observed",
        "outer-exit observed flag must be certificate derived",
    )
    _require(
        flags["outer_exit_certified"]
        == (outer is not None and outer["strict_overshoot"]),
        "$.flags.outer_exit_certified",
        "outer-exit certified flag must be certificate derived",
    )
    _require(
        flags["rearmed"] == (outer is not None and outer["rearmed"]),
        "$.flags.rearmed",
        "rearmed flag must be certificate derived",
    )
    _require(
        flags["outer_grazing_observed"]
        == (
            outer is not None and outer["grazing_touch_count"] > 0
        ),
        "$.flags.outer_grazing_observed",
        "outer-grazing flag must be certificate derived",
    )
    _require(
        flags["episode_complete"]
        == any(episode["complete"] for episode in record["episodes"]),
        "$.flags.episode_complete",
        "episode-complete flag disagrees with episode ledger",
    )
    if outer is not None and problem_commitment is not None:
        threshold_registry = problem_commitment[
            "threshold_registry"
        ]
        _require(
            outer["hysteresis_registry_id"]
            == threshold_registry["registry_id"]
            and Fraction(str(outer["r_out"]))
            == coverage.as_fraction(threshold_registry["r_out"]),
            "$.certificates.outer_exit",
            "outer threshold differs from committed hysteresis registry",
        )
    if outer is not None and outer["strict_overshoot"]:
        _require(
            global_certificate is not None
            and coverage_certificate is not None
            and outer["global_minimum_certificate_id"]
            == global_certificate["certificate_id"]
            and outer["coverage_manifest_sha256"]
            == coverage_certificate["manifest_sha256"]
            and outer["image_manifest_sha256"]
            == coverage.image_manifest_sha256(coverage_certificate),
            "$.certificates.outer_exit",
            "outer-exit proof references wrong global/image coverage",
        )
        _require(
            observation["t0"] <= outer["boundary_time"]["lo"]
            <= outer["boundary_time"]["hi"] < observation["t1"]
            and outer["post_boundary_interval"]["hi"] < observation["t1"],
            "$.certificates.outer_exit",
            "outer-exit evidence is outside observation window",
        )
        assert problem_commitment_sha256 is not None
        outer_witness = outer["post_boundary_witness"]
        _require_registered_problem_model(
            witness=outer_witness,
            expected_payload={
                "model_kind": "rho_affine",
                "model": {
                    "observable": outer_witness["observable"],
                    "time_domain": (
                        "registered-post-boundary-interval"
                    ),
                    "rho_affine": outer_witness["rho_affine"],
                },
            },
            commitment_sha256=problem_commitment_sha256,
            model_map=problem_model_map,
            expected_suffix="outer-overshoot-rho",
            path="$.certificates.outer_exit.post_boundary_witness",
        )
    if no_earlier_certificate is not None and outer is not None:
        r_in = _validate_dyadic(
            no_earlier_certificate["r_in"],
            "$.certificates.no_earlier_entry.r_in",
        )
        _require(
            0 < r_in < Fraction(str(outer["r_out"]))
            and no_earlier_certificate["hysteresis_registry_id"]
            == outer["hysteresis_registry_id"],
            "$.certificates.outer_exit.hysteresis_registry_id",
            "entry/exit thresholds must share one registry with 0<r_in<r_out",
        )

    closest = certs["closest"]
    _require(
        flags["closest_episode_identified"]
        == (
            closest is not None
            and closest["status"] == "episode_complete"
        ),
        "$.flags.closest_episode_identified",
        "episode-closest flag must be certificate derived",
    )
    _require(
        flags["closest_window_only"]
        == (closest is not None and closest["status"] == "window_only"),
        "$.flags.closest_window_only",
        "window-closest flag must be certificate derived",
    )
    episode_map = {
        episode["episode_id"]: episode for episode in record["episodes"]
    }
    _require(
        len(episode_map) == len(record["episodes"]),
        "$.episodes",
        "episode IDs must be unique",
    )
    _require(
        flags["left_censored"]
        == any(
            episode["left_censored"]
            for episode in record["episodes"]
        ),
        "$.flags.left_censored",
        "left-censor flag disagrees with episode ledger",
    )
    expected_right_censor = any(
        episode["right_censored"] for episode in record["episodes"]
    ) or finite_no_entry
    _require(
        flags["right_censored"] == expected_right_censor,
        "$.flags.right_censored",
        "right-censor flag disagrees with episode/window proof",
    )
    _require(
        not flags["closest_tied"],
        "$.flags.closest_tied",
        "closest-tie certificates are not part of this schema version",
    )
    if closest is not None and closest["status"] in (
        "episode_complete",
        "window_only",
    ):
        _require(
            closest["episode_id"] in episode_map,
            "$.certificates.closest.episode_id",
            "closest certificate references unknown episode",
        )
        episode = episode_map[closest["episode_id"]]
        _require(
            coverage_certificate is not None
            and global_certificate is not None
            and closest["coverage_manifest_sha256"]
            == coverage_certificate["manifest_sha256"]
            and closest["global_minimum_certificate_id"]
            == global_certificate["certificate_id"],
            "$.certificates.closest",
            "closest certificate references wrong coverage/global proof",
        )
        if episode["T_in"] is not None:
            _require(
                closest["time"]["lo"] >= episode["T_in"]["hi"],
                "$.certificates.closest.time",
                "closest time precedes episode entry",
            )
        time_ceiling = (
            episode["T_out"]["lo"]
            if episode["T_out"] is not None
            else observation["t1"]
        )
        _require(
            closest["time"]["hi"] <= time_ceiling,
            "$.certificates.closest.time",
            "closest time follows episode/window end",
        )
    primary_episodes = [
        episode
        for episode in record["episodes"]
        if episode["role"] == "primary"
    ]
    if cluster is not None and primary_episodes:
        _require(
            len(primary_episodes) == 1,
            "$.episodes",
            "entry record requires exactly one primary episode",
        )
        primary_episode = primary_episodes[0]
        if primary_episode["T_in"] is not None:
            cluster_time_boxes = (
                [
                    box["time"]
                    for box in cluster["implicit_set"]["domain_boxes"]
                ]
                if cluster["representation"] == "implicit"
                else [
                    member["box"]["time"]
                    for member in cluster["members"]
                ]
            )
            entry_hull = {
                "lo": min(box["lo"] for box in cluster_time_boxes),
                "hi": max(box["hi"] for box in cluster_time_boxes),
            }
            _require(
                type_strict_equal(primary_episode["T_in"], entry_hull),
                "$.episodes",
                "episode T_in must equal certified cluster-time hull",
            )
        if outer is not None and outer["strict_overshoot"]:
            _require(
                primary_episode["T_out"] is not None
                and primary_episode["T_out"]["lo"]
                <= outer["boundary_time"]["lo"]
                <= outer["boundary_time"]["hi"]
                <= primary_episode["T_out"]["hi"],
                "$.certificates.outer_exit.boundary_time",
                "outer boundary time does not match episode T_out",
            )
            _require(
                outer["post_boundary_interval"]["lo"]
                > primary_episode["T_out"]["hi"],
                "$.certificates.outer_exit.post_boundary_interval",
                "post-boundary evidence must follow episode T_out",
            )

    secondary_contacts = sum(
        episode["secondary_inner_contacts"]
        for episode in record["episodes"]
    )
    transitions = [
        event["transition"]
        for episode in record["episodes"]
        for event in episode["component_events"]
    ]
    _require(
        flags["episode_has_secondary_inner_contact"]
        == (secondary_contacts > 0),
        "$.flags.episode_has_secondary_inner_contact",
        "secondary-contact flag disagrees with ledger",
    )
    _require(
        flags["episode_has_component_merger"] == ("merge" in transitions),
        "$.flags.episode_has_component_merger",
        "merger flag disagrees with ledger",
    )
    _require(
        flags["episode_has_component_split"] == ("split" in transitions),
        "$.flags.episode_has_component_split",
        "split flag disagrees with ledger",
    )

    certificate_ids: list[str] = []
    for certificate in certs.values():
        if certificate is not None:
            certificate_ids.append(certificate["certificate_id"])
    if cluster is not None:
        for member in cluster["members"]:
            certificate_ids.extend(
                (
                    member["geometry_certificate"]["certificate_id"],
                    member["jet_normal"]["rank_certificate"][
                        "certificate_id"
                    ],
                )
            )
    _require(
        len(certificate_ids) == len(set(certificate_ids)),
        "$.certificates",
        "certificate IDs must be globally unique",
    )

    if primary == "left_censored_active_episode":
        _require(
            source["initial_state"] == "active"
            and flags["left_censored"]
            and record["episodes"]
            and record["episodes"][0]["role"] == "preexisting",
            "$",
            "left-censored outcome needs a pre-existing active episode",
        )
        return
    if primary == "torus_branch_ambiguous":
        _require(
            torus is not None and not torus["unique"],
            "$.certificates.torus_log",
            "torus ambiguity needs non-unique log certificate",
        )
        return
    if primary == "ambiguous_tie":
        _require(
            tie_certificate is not None
            and tie_certificate["status"] == "ordering_ambiguous",
            "$.certificates.tie",
            "ambiguous tie requires ordering-only proof",
        )
        return
    if primary == "numerically_unresolved":
        unresolved = _require_certificate(certs, "unresolved", primary)
        _require(
            coverage_certificate is not None
            and unresolved["coverage_manifest_sha256"]
            == coverage_certificate["manifest_sha256"]
            and sorted(unresolved["unresolved_leaf_ids"])
            == unresolved_ids,
            "$.certificates.unresolved",
            "unresolved certificate must exactly bind unresolved leaves",
        )
        return
    if primary in ("no_entry_proved", "right_censored_no_entry"):
        _require(
            cluster is None and no_entry is not None,
            "$",
            "no-entry outcomes require no cluster and a proof",
        )
        if primary == "no_entry_proved":
            _require(
                complete_no_entry and not flags["right_censored"],
                "$.certificates.no_entry",
                "proved no-entry requires recurrence or global lower bound",
            )
        else:
            _require(
                finite_no_entry and flags["right_censored"],
                "$.certificates.no_entry",
                "right-censored no-entry requires finite-window proof",
            )
        return

    _require(
        cluster is not None
        and coverage_complete
        and global_certificate is not None
        and no_earlier_certificate is not None,
        "$",
        "entry outcome requires complete coverage, global and no-earlier proofs",
    )
    if primary == "right_censored_active_episode":
        _require(
            flags["right_censored"]
            and not flags["outer_exit_certified"]
            and closest is not None
            and closest["status"] == "window_only",
            "$",
            "active censor requires window-only closest and no strict exit",
        )
        return
    _require(
        outer is not None
        and outer["strict_overshoot"]
        and closest is not None
        and closest["status"] == "episode_complete",
        "$",
        "completed entry requires strict outer exit and episode closest",
    )
    if primary == "tie_cluster":
        _require(
            cluster["complete"]
            and cluster["representation"] != "singleton"
            and tie_certificate is not None
            and tie_certificate["status"] == "complete_cluster",
            "$.entry_cluster",
            "tie cluster requires complete cluster and equal-time proof",
        )
    elif primary == "degenerate_spatial_minimum":
        _require(
            cluster["representation"] == "singleton"
            and flags["entry_has_spatial_degeneracy"],
            "$.entry_cluster",
            "degenerate outcome requires singleton PSD-singular minimum",
        )
    elif primary == "grazing_entry":
        _require(
            cluster["representation"] == "singleton"
            and flags["entry_has_grazing"]
            and not flags["entry_has_spatial_degeneracy"],
            "$.entry_cluster",
            "grazing outcome requires exact-zero singleton contact",
        )
    else:
        _require(
            cluster["representation"] == "singleton"
            and flags["entry_geometry_regular"],
            "$.entry_cluster",
            "regular outcome requires H positive-definite and F_t<0",
        )


def _source_validity_binding(
    record: dict[str, Any],
) -> dict[str, Any]:
    """Canonical source-v2 validity view carried by every event envelope."""

    source = record["source"]
    certificate = record["certificates"]["source_validity"]
    return {
        "certificate_id": certificate["certificate_id"],
        "predicate_version": certificate["predicate_version"],
        "status": certificate["status"],
        "source_valid": source["source_valid"],
        "history_valid": source["history_valid"],
        "initial_state": source["initial_state"],
        "invalid_reasons": copy.deepcopy(source["invalid_reasons"]),
    }


def validate_record(value: Any) -> dict[str, Any]:
    """Validate strict shape plus all cross-field event semantics."""

    record = _require_exact_keys(value, ROOT_KEYS, "$")
    _require(
        record["schema_version"] == EVENT_SCHEMA_VERSION,
        "$.schema_version",
        f"expected {EVENT_SCHEMA_VERSION}",
    )
    _require_hash(record["registry_hash"], "$.registry_hash")
    _require_string(record["sample_id"], "$.sample_id")
    _validate_source(record["source"], "$.source")
    _validate_observation(record["observation"], "$.observation")
    _require_enum(
        record["primary_outcome"], PRIMARY_PRECEDENCE, "$.primary_outcome"
    )
    _validate_flags(record["flags"], "$.flags")
    if record["entry_cluster"] is not None:
        _validate_cluster(record["entry_cluster"], "$.entry_cluster")
    _require(type(record["episodes"]) is list, "$.episodes", "expected an array")
    for index, episode in enumerate(record["episodes"]):
        _validate_episode(episode, f"$.episodes[{index}]")
    _validate_certificates(record["certificates"], "$.certificates")
    _require(type(record["precedence_trace"]) is list, "$.precedence_trace", "expected an array")
    for index, item in enumerate(record["precedence_trace"]):
        _require_enum(item, PRIMARY_PRECEDENCE, f"$.precedence_trace[{index}]")
    scope = _require_exact_keys(
        record["scope"],
        {
            "record_kind",
            "physical_root_solver_run",
            "proof_backend",
            "solver_run_manifest",
            "solver_run_manifest_sha256",
            "problem_commitment_sha256",
            "source_state_sha256",
            "source_registry_sha256",
            "source_draw_registry_sha256",
            "source_validity",
            "source_validity_sha256",
            "solver_registry_sha256",
            "event_model_registry",
            "event_model_registry_sha256",
            "proof_provenance",
            "proof_provenance_sha256",
            "replay_authority",
            "independent_replayer",
            "authoritative_physical_certificate",
            "physical_outcome_mass_estimated",
            "rank_used_for_event_selection",
        },
        "$.scope",
    )
    record_kind = _require_enum(
        scope["record_kind"],
        ("synthetic_control", "certified_solver_output"),
        "$.scope.record_kind",
    )
    _require_string(scope["proof_backend"], "$.scope.proof_backend")
    for name in (
        "physical_root_solver_run",
        "authoritative_physical_certificate",
        "physical_outcome_mass_estimated",
        "rank_used_for_event_selection",
    ):
        _require_bool(scope[name], f"$.scope.{name}")
    _require(
        not scope["authoritative_physical_certificate"],
        "$.scope.authoritative_physical_certificate",
        "Brief 0018 cannot assert an authoritative physical certificate",
    )
    _require_string(
        scope["independent_replayer"],
        "$.scope.independent_replayer",
    )
    root_coverage = record["certificates"]["root_coverage"]
    if root_coverage is None:
        expected_commitment_fields = {
            "problem_commitment_sha256": None,
            "source_state_sha256": None,
            "source_registry_sha256": None,
            "source_draw_registry_sha256": None,
            "solver_registry_sha256": None,
        }
    else:
        problem_sha256, problem, _ = _coverage_problem_context(
            root_coverage
        )
        expected_commitment_fields = {
            "problem_commitment_sha256": problem_sha256,
            "source_state_sha256": problem["source_state_sha256"],
            "source_registry_sha256": problem[
                "source_registry_sha256"
            ],
            "source_draw_registry_sha256": problem[
                "source_draw_registry_sha256"
            ],
            "solver_registry_sha256": problem[
                "solver_registry_sha256"
            ],
        }
    _require(
        all(
            scope[name] == expected
            for name, expected in expected_commitment_fields.items()
        ),
        "$.scope",
        "scope commitments do not match the replayed event problem",
    )
    expected_source_validity = _source_validity_binding(record)
    _require(
        type_strict_equal(
            scope["source_validity"],
            expected_source_validity,
        ),
        "$.scope.source_validity",
        "source-validity envelope differs from the source predicate record",
    )
    _hash_binding(
        scope["source_validity"],
        scope["source_validity_sha256"],
        "$.scope.source_validity_sha256",
    )
    expected_event_registry = _event_model_registry(record)
    _require(
        type_strict_equal(
            scope["event_model_registry"],
            expected_event_registry,
        ),
        "$.scope.event_model_registry",
        "event proof-model registry differs from record proof content",
    )
    _hash_binding(
        scope["event_model_registry"],
        scope["event_model_registry_sha256"],
        "$.scope.event_model_registry_sha256",
    )
    if root_coverage is not None:
        problem_event_registry = root_coverage["manifest"][
            "exact_inputs"
        ]["problem_commitment"]["event_model_registry"]
        _require(
            type_strict_equal(
                problem_event_registry,
                expected_event_registry,
            ),
            "$.certificates.root_coverage.manifest.exact_inputs.problem_commitment.event_model_registry",
            "event proof models are not part of the problem commitment",
        )
    provenance = scope["proof_provenance"]
    _require(
        type(provenance) is list,
        "$.scope.proof_provenance",
        "expected an array",
    )
    parsed_provenance: list[dict[str, Any]] = []
    for index, row_value in enumerate(provenance):
        path = f"$.scope.proof_provenance[{index}]"
        row = _require_exact_keys(
            row_value,
            {
                "proof_id",
                "backend",
                "problem_commitment_sha256",
                "proof_content_sha256",
            },
            path,
        )
        _require_string(row["proof_id"], f"{path}.proof_id")
        _require_string(row["backend"], f"{path}.backend")
        if row["problem_commitment_sha256"] is not None:
            _require_hash(
                row["problem_commitment_sha256"],
                f"{path}.problem_commitment_sha256",
            )
        _require_hash(
            row["proof_content_sha256"],
            f"{path}.proof_content_sha256",
        )
        parsed_provenance.append(row)
    _require(
        [row["proof_id"] for row in parsed_provenance]
        == _required_proof_identifiers(record),
        "$.scope.proof_provenance",
        "provenance rows do not cover every proof object exactly once",
    )
    _hash_binding(
        parsed_provenance,
        scope["proof_provenance_sha256"],
        "$.scope.proof_provenance_sha256",
    )
    _require(
        all(
            row["backend"] == scope["proof_backend"]
            and row["problem_commitment_sha256"]
            == scope["problem_commitment_sha256"]
            and row["proof_content_sha256"]
            == {
                model["model_id"]: model["content_sha256"]
                for model in expected_event_registry["models"]
            }[row["proof_id"]]
            for row in parsed_provenance
        ),
        "$.scope.proof_provenance",
        "proof backend/problem provenance is not closed",
    )
    nested_backends = _nested_proof_backends(record)
    _require(
        not nested_backends
        or nested_backends == {scope["proof_backend"]},
        "$.scope.proof_backend",
        "declared backend must match every nested proof witness",
    )
    if record_kind == "synthetic_control":
        _require(
            not scope["physical_root_solver_run"]
            and scope["proof_backend"] == "exact-synthetic-fixture",
            "$.scope",
            "synthetic controls cannot claim a solver run",
        )
        _require(
            scope["solver_run_manifest"] is None
            and scope["solver_run_manifest_sha256"] is None,
            "$.scope",
            "synthetic control cannot carry solver-run provenance",
        )
        _require(
            scope["replay_authority"]
            == "builtin-pinned-synthetic-fixture"
            and scope["independent_replayer"]
            == "event-contract-builtin-synthetic-registry-v1",
            "$.scope",
            "synthetic control lacks the built-in pinned replay authority",
        )
        _require(
            record["sample_id"] in PINNED_SYNTHETIC_PROBLEM_SHA256
            and scope["problem_commitment_sha256"]
            == PINNED_SYNTHETIC_PROBLEM_SHA256[
                record["sample_id"]
            ],
            "$.scope.problem_commitment_sha256",
            "synthetic fixture differs from the code-pinned problem registry",
        )
        if root_coverage is None:
            _require(
                record["registry_hash"] == "0" * 64,
                "$.registry_hash",
                "no-coverage synthetic control has an unpinned registry hash",
            )
        _require(
            record["sample_id"]
            in PINNED_SYNTHETIC_EVENT_MODEL_REGISTRY_SHA256
            and scope["event_model_registry_sha256"]
            == PINNED_SYNTHETIC_EVENT_MODEL_REGISTRY_SHA256[
                record["sample_id"]
            ],
            "$.scope.event_model_registry_sha256",
            "synthetic proof content differs from the code-pinned event model registry",
        )
    else:
        _require(
            scope["physical_root_solver_run"]
            and scope["proof_backend"] != "exact-synthetic-fixture",
            "$.scope",
            "certified solver output requires a non-synthetic backend",
        )
        _require(
            root_coverage is not None,
            "$.scope",
            "certified solver output requires replayable root coverage",
        )
        _require(
            scope["replay_authority"]
            == "external-0019-independent-replay-required"
            and scope["independent_replayer"]
            == "brief-0019-independent-event-replayer",
            "$.scope",
            "physical envelope must require the external Brief 0019 replayer",
        )
        run_manifest = _require_exact_keys(
            scope["solver_run_manifest"],
            {
                "run_id",
                "backend",
                "executable_sha256",
                "input_manifest_sha256",
                "coverage_manifest_sha256",
                "proof_artifact_sha256",
                "problem_commitment_sha256",
                "source_state_sha256",
                "source_registry_sha256",
                "source_draw_registry_sha256",
                "source_validity_sha256",
                "solver_registry_sha256",
                "independent_replayer",
            },
            "$.scope.solver_run_manifest",
        )
        _require_string(
            run_manifest["run_id"], "$.scope.solver_run_manifest.run_id"
        )
        _require(
            run_manifest["backend"] == scope["proof_backend"],
            "$.scope.solver_run_manifest.backend",
            "run manifest backend disagrees with scope",
        )
        for name in (
            "executable_sha256",
            "input_manifest_sha256",
            "coverage_manifest_sha256",
            "proof_artifact_sha256",
            "problem_commitment_sha256",
            "source_state_sha256",
            "source_registry_sha256",
            "source_draw_registry_sha256",
            "source_validity_sha256",
            "solver_registry_sha256",
        ):
            _require_hash(
                run_manifest[name],
                f"$.scope.solver_run_manifest.{name}",
            )
        _hash_binding(
            run_manifest,
            scope["solver_run_manifest_sha256"],
            "$.scope.solver_run_manifest_sha256",
        )
        _require(
            run_manifest["input_manifest_sha256"]
            == root_coverage["manifest"]["exact_inputs_sha256"]
            and run_manifest["coverage_manifest_sha256"]
            == root_coverage["manifest_sha256"]
            and run_manifest["proof_artifact_sha256"]
            == canonical_sha256(root_coverage),
            "$.scope.solver_run_manifest",
            "run provenance is not bound to coverage input/output artifact",
        )
        _require(
            run_manifest["problem_commitment_sha256"]
            == scope["problem_commitment_sha256"]
            and run_manifest["source_state_sha256"]
            == scope["source_state_sha256"]
            and run_manifest["source_registry_sha256"]
            == scope["source_registry_sha256"]
            and run_manifest["source_draw_registry_sha256"]
            == scope["source_draw_registry_sha256"]
            and run_manifest["source_validity_sha256"]
            == scope["source_validity_sha256"]
            and run_manifest["solver_registry_sha256"]
            == scope["solver_registry_sha256"]
            and run_manifest["independent_replayer"]
            == scope["independent_replayer"],
            "$.scope.solver_run_manifest",
            "run manifest does not bind every external commitment",
        )
    _require(
        not scope["physical_outcome_mass_estimated"],
        "$.scope.physical_outcome_mass_estimated",
        "this reference artifact cannot claim outcome masses",
    )
    _require(
        not scope["rank_used_for_event_selection"],
        "$.scope.rank_used_for_event_selection",
        "rank-blind selection is mandatory",
    )
    _validate_outcome_semantics(record)
    return record


def validate_schema_document(schema: Any) -> dict[str, Any]:
    """Perform dependency-free integrity checks on the JSON Schema artifact."""

    _require(type(schema) is dict, "$schema", "expected an object")
    _require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "$schema.$schema",
        "expected JSON Schema draft 2020-12",
    )
    _require(
        schema.get("type") == "object",
        "$schema.type",
        "root schema must describe an object",
    )
    _require(
        schema.get("additionalProperties") is False,
        "$schema.additionalProperties",
        "root schema must reject extra properties",
    )
    required = schema.get("required")
    _require(
        type(required) is list and set(required) == ROOT_KEYS,
        "$schema.required",
        "root required keys disagree with semantic validator",
    )
    properties = schema.get("properties")
    _require(type(properties) is dict, "$schema.properties", "missing properties")
    version_schema = properties.get("schema_version", {})
    _require(
        version_schema.get("const") == EVENT_SCHEMA_VERSION,
        "$schema.properties.schema_version.const",
        "schema version mismatch",
    )
    outcome_enum = properties.get("primary_outcome", {}).get("enum")
    _require(
        outcome_enum == list(PRIMARY_PRECEDENCE),
        "$schema.properties.primary_outcome.enum",
        "primary outcome registry/order mismatch",
    )
    flag_schema = properties.get("flags", {})
    _require(
        set(flag_schema.get("required", [])) == set(FLAG_NAMES),
        "$schema.properties.flags.required",
        "flag registry mismatch",
    )
    _require(
        flag_schema.get("additionalProperties") is False,
        "$schema.properties.flags.additionalProperties",
        "flags must reject extra properties",
    )
    return schema


def interval(value: float, radius: float = 0.0) -> dict[str, float]:
    return {"lo": value - radius, "hi": value + radius}


def identity_matrix(size: int) -> list[list[float]]:
    return [
        [1.0 if row == column else 0.0 for column in range(size)]
        for row in range(size)
    ]


def zero_matrix(rows: int, columns: int) -> list[list[float]]:
    return [[0.0 for _ in range(columns)] for _ in range(rows)]


def make_jet_normal(
    rank: int | None,
    *,
    possible_ranks: Sequence[int] = (2, 3),
    longitudinal_phase: bool = True,
) -> dict[str, Any]:
    separation = [0.0] * 9
    separation[0] = 1.0
    if longitudinal_phase:
        separation[8] = 0.5
    jacobian = [[0 for _ in range(3)] for _ in range(9)]
    jacobian[7][0] = 1
    if rank == 3:
        jacobian[6][1] = 1
    else:
        jacobian[7][1] = 1
    jacobian[8][2] = -2
    target_metric = identity_matrix(9)
    domain_metric = identity_matrix(3)
    rank_certificate_base = {
        "certificate_id": (
            "rank-unresolved"
            if rank is None
            else f"rank-exact-{rank}"
        ),
        "J_sha256": canonical_sha256(jacobian),
        "G_sha256": canonical_sha256(target_metric),
        "H_sha256": canonical_sha256(domain_metric),
    }

    if rank is None:
        unresolved_singular_values = [
            interval(2.0),
            interval(math.sqrt(2.0)),
            {"lo": 0.0, "hi": 1.0e-6},
        ]
        return {
            "coordinate_basis": "physical-length orthonormal target basis",
            "G": target_metric,
            "H": domain_metric,
            "J": jacobian,
            "singular_value_intervals": unresolved_singular_values,
            "rank": {
                "status": "unresolved",
                "exact_rank": None,
                "possible_ranks": list(possible_ranks),
            },
            "rank_certificate": {
                **rank_certificate_base,
                "method": "interval_singular_enclosure",
                "singular_intervals_sha256": canonical_sha256(
                    unresolved_singular_values
                ),
                "declared_rank": None,
                "possible_ranks": list(possible_ranks),
            },
            "normal_dimension": None,
            "P_N": None,
            "normal_frame": None,
            "s": separation,
            "b": None,
            "ell": None,
        }

    normal_dimension = 9 - rank
    projector = zero_matrix(9, 9)
    for index in range(normal_dimension):
        projector[index][index] = 1.0
    frame = zero_matrix(9, normal_dimension)
    for index in range(normal_dimension):
        frame[index][index] = 1.0
    b = [0.0] * 9
    ell = [0.0] * 9
    for index in range(9):
        b[index] = sum(
            projector[index][column] * separation[column]
            for column in range(9)
        )
        ell[index] = separation[index] - b[index]
    singular_values = (
        [interval(2.0), interval(1.0), interval(1.0)]
        if rank == 3
        else [
            interval(2.0),
            interval(math.sqrt(2.0)),
            interval(0.0),
        ]
    )
    return {
        "coordinate_basis": "physical-length orthonormal target basis",
        "G": target_metric,
        "H": domain_metric,
        "J": jacobian,
        "singular_value_intervals": singular_values,
        "rank": {
            "status": "certified",
            "exact_rank": rank,
            "possible_ranks": [rank],
        },
        "rank_certificate": {
            **rank_certificate_base,
            "method": "exact_rational_elimination",
            "singular_intervals_sha256": canonical_sha256(
                singular_values
            ),
            "declared_rank": rank,
            "possible_ranks": [rank],
        },
        "normal_dimension": normal_dimension,
        "P_N": projector,
        "normal_frame": frame,
        "s": separation,
        "b": b,
        "ell": ell,
    }


def make_representative(
    representative_id: str,
    *,
    candidate_id: str | None = None,
    rank: int | None = 3,
    grazing: bool = False,
    degenerate: bool = False,
    time: float = 0.75,
    time_radius: float = 0.0,
) -> dict[str, Any]:
    jet = make_jet_normal(rank, longitudinal_phase=not grazing)
    jet["rank_certificate"][
        "certificate_id"
    ] = f"rank-{representative_id}"
    hessian = (
        [[interval(1.0), interval(0.0)], [interval(0.0), interval(0.0)]]
        if degenerate
        else [[interval(1.0), interval(0.0)], [interval(0.0), interval(1.0)]]
    )
    flux = interval(0.0) if grazing else interval(-1.0)
    derivative_jet = (
        [copy.deepcopy(flux), interval(2.0)]
        if grazing
        else [copy.deepcopy(flux)]
    )
    product_diagonal = _interval_product(
        _float_interval_tuple(hessian[0][0]),
        _float_interval_tuple(hessian[1][1]),
    )
    product_off = _interval_product(
        _float_interval_tuple(hessian[0][1]),
        _float_interval_tuple(hessian[1][0]),
    )
    determinant = _interval_subtract(product_diagonal, product_off)
    representative = {
        "representative_id": representative_id,
        "candidate_id": candidate_id or representative_id,
        "box": {
            "sigma1": interval(0.5),
            "sigma2": interval(0.5),
            "time": interval(time, time_radius),
        },
        "torus_image": [0] * 9,
        "log_unique": True,
        "s": copy.deepcopy(jet["s"]),
        "F": interval(
            0.5 * math.fsum(value * value for value in jet["s"]),
            1.0e-12,
        ),
        "grad_sigma": [interval(0.0, 1.0e-12), interval(0.0, 1.0e-12)],
        "dF_dt": flux,
        "H_sigma_sigma": hessian,
        "geometry_certificate": {
            "certificate_id": f"geometry-{representative_id}",
            "hessian_sha256": canonical_sha256(hessian),
            "flux_sha256": canonical_sha256(flux),
            "hessian_class": (
                "psd_singular" if degenerate else "positive_definite"
            ),
            "leading_minor_range": copy.deepcopy(hessian[0][0]),
            "determinant_range": {
                "lo": determinant[0],
                "hi": determinant[1],
            },
            "flux_class": (
                "exact_zero_multiplicity"
                if grazing
                else "strict_inward"
            ),
            "flux_range": copy.deepcopy(flux),
            "time_derivative_jet": derivative_jet,
            "time_derivative_jet_sha256": canonical_sha256(
                derivative_jet
            ),
            "contact_multiplicity": 2 if grazing else None,
            "one_sided_behavior": (
                "touch_or_plateau" if grazing else "inward_crossing"
            ),
        },
        "jet_normal": jet,
    }
    return representative


def _finalize_cluster(cluster: dict[str, Any]) -> dict[str, Any]:
    members = sorted(cluster["members"], key=canonical_sha256)
    cluster["members"] = members
    hashes = [canonical_sha256(member) for member in members]
    cluster["member_hashes"] = hashes
    cluster["members_sha256"] = canonical_sha256(hashes)
    return cluster


def make_cluster(
    representation: str = "singleton",
    *,
    complete: bool = True,
    rank: int | None = 3,
) -> dict[str, Any]:
    if representation == "singleton":
        return _finalize_cluster({
            "representation": "singleton",
            "complete": complete,
            "unordered": True,
            "cardinality": 1,
            "members": [
                make_representative(
                    "entry-0", candidate_id="candidate-0", rank=rank
                )
            ],
            "member_hashes": [],
            "members_sha256": "",
            "implicit_set": None,
        })
    if representation == "finite":
        return _finalize_cluster({
            "representation": "finite",
            "complete": complete,
            "unordered": True,
            "cardinality": 2,
            "members": [
                make_representative(
                    "entry-a",
                    candidate_id="candidate-a",
                    rank=rank,
                    grazing=True,
                    time=0.75,
                ),
                make_representative(
                    "entry-b",
                    candidate_id="candidate-b",
                    rank=2,
                    grazing=True,
                    degenerate=True,
                    time=0.75,
                ),
            ],
            "member_hashes": [],
            "members_sha256": "",
            "implicit_set": None,
        })
    if representation == "implicit":
        return _finalize_cluster({
            "representation": "implicit",
            "complete": complete,
            "unordered": True,
            "cardinality": "continuum",
            "members": [],
            "member_hashes": [],
            "members_sha256": "",
            "implicit_set": {
                "defining_equations": [
                    "d_sigma1 F = 0",
                    "d_sigma2 F = 0",
                    "F-r_in^2/2 = 0",
                ],
                "candidate_ids": ["candidate-singular-set"],
                "domain_boxes": [
                    {
                        "sigma1": {
                            "lo": 0.375,
                            "hi": 0.625,
                        },
                        "sigma2": interval(0.5),
                        "time": interval(0.75),
                    }
                ],
                "dimension_status": "positive",
                "set_certificate_ref": "synthetic-positive-dimensional-set",
                "jet_field_certificate_ref": None,
                "normal_field_certificate_ref": None,
            },
        })
    raise ValueError(f"unknown cluster representation: {representation}")


def make_flags() -> dict[str, bool]:
    flags = {name: False for name in FLAG_NAMES}
    flags.update(
        {
            "source_valid": True,
            "history_valid": True,
            "initial_armed": True,
        }
    )
    return flags


def make_certificates() -> dict[str, Any]:
    return {
        "source_validity": {
            "certificate_id": "source-validity",
            "status": "valid",
            "predicate_version": "brief-0018-source-validity-v1",
            "reason_codes": [],
        },
        "root_coverage": None,
        "global_minimum": None,
        "no_earlier_entry": None,
        "torus_log": None,
        "tie": None,
        "outer_exit": None,
        "no_entry": None,
        "unresolved": None,
        "closest": None,
    }


def complete_coverage_certificate(
    candidate_specs: Sequence[
        tuple[str, str, tuple[Fraction, Fraction]]
    ] = (
        (
            "candidate-0",
            "physical-root-0",
            (Fraction(3, 4), Fraction(3, 4)),
        ),
    ),
    *,
    no_entry: bool = False,
    time_domain: tuple[Fraction, Fraction] = (
        Fraction(0),
        Fraction(4),
    ),
) -> dict[str, Any]:
    return coverage.build_coverage_certificate(
        candidate_specs,
        no_entry=no_entry,
        time_domain=time_domain,
    )


def incomplete_coverage_certificate() -> dict[str, Any]:
    return coverage.build_coverage_certificate(unresolved=True)


def _registered_model_ref(
    commitment: dict[str, Any], suffix: str
) -> dict[str, str]:
    matches = [
        row
        for row in commitment["function_registry"]["models"]
        if row["model_id"].endswith(f"::{suffix}")
    ]
    _require(
        len(matches) == 1,
        "$.certificates.root_coverage",
        f"problem registry does not uniquely define {suffix}",
    )
    return {
        "model_id": matches[0]["model_id"],
        "model_sha256": matches[0]["model_sha256"],
    }


def _bind_record_to_coverage_problem(record: dict[str, Any]) -> None:
    root_coverage = record["certificates"]["root_coverage"]
    if root_coverage is None:
        return
    exact_inputs = root_coverage["manifest"]["exact_inputs"]
    problem = exact_inputs["problem_commitment"]
    record["source"]["sampling_registry_hash"] = problem[
        "source_draw_registry_sha256"
    ]
    record["source"]["classification_registry_hash"] = problem[
        "source_registry_sha256"
    ]
    event_registry = _event_model_registry(record)
    problem["event_model_registry"] = event_registry
    problem["event_model_registry_sha256"] = canonical_sha256(
        event_registry
    )
    problem_sha256 = canonical_sha256(problem)
    exact_inputs["problem_commitment_sha256"] = problem_sha256
    # exact_inputs_sha256 is a manifest sibling, not a member of exact_inputs.
    root_coverage["manifest"]["exact_inputs_sha256"] = canonical_sha256(
        exact_inputs
    )
    for leaf in root_coverage["manifest"]["leaves"]:
        leaf["witness"]["problem_commitment_sha256"] = problem_sha256
    coverage.recompute_manifest_hash(root_coverage)
    manifest_hash = root_coverage["manifest_sha256"]
    certs = record["certificates"]
    for name in (
        "global_minimum",
        "no_earlier_entry",
        "no_entry",
        "unresolved",
        "closest",
        "outer_exit",
    ):
        certificate = certs[name]
        if (
            certificate is not None
            and "coverage_manifest_sha256" in certificate
            and certificate["coverage_manifest_sha256"] is not None
        ):
            certificate["coverage_manifest_sha256"] = manifest_hash
    no_entry = certs["no_entry"]
    if (
        no_entry is not None
        and no_entry["recurrence"] is not None
    ):
        no_entry["recurrence"]["time_seam_cover"][
            "coverage_manifest_sha256"
        ] = manifest_hash
    record["registry_hash"] = canonical_sha256(
        {
            "source_registry_sha256": problem[
                "source_registry_sha256"
            ],
            "source_draw_registry_sha256": problem[
                "source_draw_registry_sha256"
            ],
            "source_state_sha256": problem[
                "source_state_sha256"
            ],
            "solver_registry_sha256": problem[
                "solver_registry_sha256"
            ],
            "problem_commitment_sha256": problem_sha256,
        }
    )
    no_earlier = certs["no_earlier_entry"]
    if no_earlier is not None:
        no_earlier["initial_armed_witness"].update(
            {
                "problem_commitment_sha256": problem_sha256,
                **_registered_model_ref(
                    problem, "initial-armed-rho"
                ),
            }
        )
    outer = certs["outer_exit"]
    if (
        outer is not None
        and outer["post_boundary_witness"] is not None
    ):
        outer["post_boundary_witness"].update(
            {
                "problem_commitment_sha256": problem_sha256,
                **_registered_model_ref(
                    problem, "outer-overshoot-rho"
                ),
            }
        )
    no_entry = certs["no_entry"]
    if no_entry is not None:
        if no_entry["recurrence"] is not None:
            no_entry["recurrence"].update(
                {
                    "backend": coverage.SYNTHETIC_PROOF_BACKEND,
                    "problem_commitment_sha256": problem_sha256,
                }
            )
        if no_entry["global_lower_bound"] is not None:
            no_entry["global_lower_bound"].update(
                {
                    "problem_commitment_sha256": problem_sha256,
                    **_registered_model_ref(
                        problem, "global-no-entry-rho"
                    ),
                }
            )


def _strip_model_volatile_fields(value: Any) -> Any:
    """Remove content-address/provenance fields from a physical model view."""

    if isinstance(value, list):
        return [_strip_model_volatile_fields(item) for item in value]
    if not isinstance(value, dict):
        return copy.deepcopy(value)
    volatile = {
        "backend",
        "coverage_manifest_sha256",
        "problem_commitment_sha256",
        "model_id",
        "model_sha256",
    }
    return {
        key: _strip_model_volatile_fields(item)
        for key, item in value.items()
        if key not in volatile
    }


def _proof_model_contents(
    record: dict[str, Any],
) -> dict[str, tuple[str, Any]]:
    """Canonical model inputs/claims that every proof row must commit."""

    source_view = copy.deepcopy(record["source"])
    result: dict[str, tuple[str, Any]] = {
        "event-header": (
            "event_header",
            {
                "schema_version": record["schema_version"],
                "sample_id": record["sample_id"],
                "source": source_view,
                "observation": copy.deepcopy(record["observation"]),
                "primary_outcome": record["primary_outcome"],
                "flags": copy.deepcopy(record["flags"]),
                "precedence_trace": copy.deepcopy(
                    record["precedence_trace"]
                ),
            },
        )
    }
    certs = record["certificates"]
    for name in sorted(CERTIFICATE_KEYS):
        certificate = certs[name]
        if certificate is not None and name != "root_coverage":
            proof_id = (
                f"certificate::{name}::"
                f"{certificate['certificate_id']}"
            )
            result[proof_id] = (
                f"certificate_{name}",
                _strip_model_volatile_fields(certificate),
            )
    root_coverage = certs["root_coverage"]
    if root_coverage is not None:
        for leaf in root_coverage["manifest"]["leaves"]:
            result[f"coverage-leaf::{leaf['leaf_id']}"] = (
                "coverage_leaf",
                _strip_model_volatile_fields(leaf),
            )
        for quotient in root_coverage["manifest"]["quotient_classes"]:
            result[
                "coverage-quotient::"
                + quotient["physical_root_id"]
            ] = (
                "coverage_quotient",
                copy.deepcopy(quotient),
            )
    cluster = record["entry_cluster"]
    if cluster is not None:
        result["entry-cluster"] = (
            "entry_cluster",
            copy.deepcopy(cluster),
        )
        for member in cluster["members"]:
            geometry_id = member["geometry_certificate"][
                "certificate_id"
            ]
            rank_id = member["jet_normal"]["rank_certificate"][
                "certificate_id"
            ]
            result[f"geometry::{geometry_id}"] = (
                "member_geometry_jet",
                {
                    "representative_id": member["representative_id"],
                    "candidate_id": member["candidate_id"],
                    "box": copy.deepcopy(member["box"]),
                    "torus_image": copy.deepcopy(
                        member["torus_image"]
                    ),
                    "log_unique": member["log_unique"],
                    "F": copy.deepcopy(member["F"]),
                    "grad_sigma": copy.deepcopy(
                        member["grad_sigma"]
                    ),
                    "dF_dt": copy.deepcopy(member["dF_dt"]),
                    "H_sigma_sigma": copy.deepcopy(
                        member["H_sigma_sigma"]
                    ),
                    "geometry_certificate": copy.deepcopy(
                        member["geometry_certificate"]
                    ),
                },
            )
            result[f"rank::{rank_id}"] = (
                "member_rank_jet",
                {
                    "representative_id": member["representative_id"],
                    "candidate_id": member["candidate_id"],
                    "s": copy.deepcopy(member["s"]),
                    "jet_normal": copy.deepcopy(member["jet_normal"]),
                },
            )
        if cluster["implicit_set"] is not None:
            result[
                "implicit-set::"
                + cluster["implicit_set"]["set_certificate_ref"]
            ] = (
                "implicit_entry_set",
                copy.deepcopy(cluster["implicit_set"]),
            )
    for episode in record["episodes"]:
        result[f"episode-ledger::{episode['episode_id']}"] = (
            "episode_ledger",
            copy.deepcopy(episode),
        )
    return result


def _event_model_registry(record: dict[str, Any]) -> dict[str, Any]:
    contents = _proof_model_contents(record)
    return {
        "schema_version": (
            "cyz-brief-0018-event-proof-model-registry-v1"
        ),
        "models": [
            {
                "model_id": model_id,
                "model_kind": contents[model_id][0],
                "content_sha256": canonical_sha256(
                    contents[model_id][1]
                ),
            }
            for model_id in sorted(contents)
        ],
    }


def _required_proof_identifiers(record: dict[str, Any]) -> list[str]:
    return sorted(_proof_model_contents(record))


def _make_proof_provenance(
    record: dict[str, Any], backend: str
) -> list[dict[str, Any]]:
    root_coverage = record["certificates"]["root_coverage"]
    problem_sha256 = (
        None
        if root_coverage is None
        else coverage.problem_commitment_sha256(root_coverage)
    )
    content_hashes = {
        row["model_id"]: row["content_sha256"]
        for row in _event_model_registry(record)["models"]
    }
    return [
        {
            "proof_id": proof_id,
            "backend": backend,
            "problem_commitment_sha256": problem_sha256,
            "proof_content_sha256": content_hashes[proof_id],
        }
        for proof_id in _required_proof_identifiers(record)
    ]


def _nested_proof_backends(record: dict[str, Any]) -> set[str]:
    certs = record["certificates"]
    backends: set[str] = set()
    root_coverage = certs["root_coverage"]
    if root_coverage is not None:
        backends.update(
            leaf["witness"]["backend"]
            for leaf in root_coverage["manifest"]["leaves"]
        )
    no_earlier = certs["no_earlier_entry"]
    if no_earlier is not None:
        backends.add(
            no_earlier["initial_armed_witness"]["backend"]
        )
    outer = certs["outer_exit"]
    if (
        outer is not None
        and outer["post_boundary_witness"] is not None
    ):
        backends.add(outer["post_boundary_witness"]["backend"])
    no_entry = certs["no_entry"]
    if no_entry is not None:
        if no_entry["recurrence"] is not None:
            backends.add(no_entry["recurrence"]["backend"])
        if no_entry["global_lower_bound"] is not None:
            backends.add(no_entry["global_lower_bound"]["backend"])
    return backends


def _bind_scope_provenance(record: dict[str, Any]) -> None:
    scope = record["scope"]
    event_registry = _event_model_registry(record)
    root_coverage = record["certificates"]["root_coverage"]
    if root_coverage is None:
        problem_sha256 = None
        source_state_sha256 = None
        source_registry_sha256 = None
        source_draw_registry_sha256 = None
        solver_registry_sha256 = None
    else:
        problem_sha256, problem, _ = _coverage_problem_context(
            root_coverage
        )
        source_state_sha256 = problem["source_state_sha256"]
        source_registry_sha256 = problem["source_registry_sha256"]
        source_draw_registry_sha256 = problem[
            "source_draw_registry_sha256"
        ]
        solver_registry_sha256 = problem["solver_registry_sha256"]
    source_validity = _source_validity_binding(record)
    rows = _make_proof_provenance(record, scope["proof_backend"])
    scope.update(
        {
            "problem_commitment_sha256": problem_sha256,
            "source_state_sha256": source_state_sha256,
            "source_registry_sha256": source_registry_sha256,
            "source_draw_registry_sha256": (
                source_draw_registry_sha256
            ),
            "source_validity": source_validity,
            "source_validity_sha256": canonical_sha256(
                source_validity
            ),
            "solver_registry_sha256": solver_registry_sha256,
            "event_model_registry": event_registry,
            "event_model_registry_sha256": canonical_sha256(
                event_registry
            ),
            "proof_provenance": rows,
            "proof_provenance_sha256": canonical_sha256(rows),
        }
    )


def make_episode(
    *,
    role: str = "primary",
    left_censored: bool = False,
    right_censored: bool = False,
    complete: bool = True,
) -> dict[str, Any]:
    return {
        "episode_id": f"{role}-episode",
        "role": role,
        "left_censored": left_censored,
        "right_censored": right_censored,
        "complete": complete,
        "T_in": None if left_censored else interval(0.75),
        "T_out": interval(2.0) if complete else None,
        "secondary_inner_contacts": 0,
        "component_events": [],
    }


def make_base_record() -> dict[str, Any]:
    return {
        "schema_version": EVENT_SCHEMA_VERSION,
        "registry_hash": "0" * 64,
        "sample_id": "synthetic-control",
        "source": {
            "sampling_registry_hash": "4" * 64,
            "classification_registry_hash": "5" * 64,
            "source_valid": True,
            "history_valid": True,
            "invalid_reasons": [],
            "initial_state": "armed",
        },
        "observation": {
            "t0": 0.0,
            "t1": 4.0,
            "window_semantics": "[t0,t1)",
            "complete_time_domain": False,
            "continuation_state": "terminal",
        },
        "primary_outcome": "regular_first_entry",
        "flags": make_flags(),
        "entry_cluster": None,
        "episodes": [],
        "certificates": make_certificates(),
        "precedence_trace": [],
        "scope": {
            "record_kind": "synthetic_control",
            "physical_root_solver_run": False,
            "proof_backend": "exact-synthetic-fixture",
            "solver_run_manifest": None,
            "solver_run_manifest_sha256": None,
            "problem_commitment_sha256": None,
            "source_state_sha256": None,
            "source_registry_sha256": None,
            "source_draw_registry_sha256": None,
            "source_validity": {
                "certificate_id": "source-validity",
                "predicate_version": (
                    "brief-0018-source-validity-v1"
                ),
                "status": "valid",
                "source_valid": True,
                "history_valid": True,
                "initial_state": "armed",
                "invalid_reasons": [],
            },
            "source_validity_sha256": canonical_sha256(
                {
                    "certificate_id": "source-validity",
                    "predicate_version": (
                        "brief-0018-source-validity-v1"
                    ),
                    "status": "valid",
                    "source_valid": True,
                    "history_valid": True,
                    "initial_state": "armed",
                    "invalid_reasons": [],
                }
            ),
            "solver_registry_sha256": None,
            "event_model_registry": {
                "schema_version": (
                    "cyz-brief-0018-event-proof-model-registry-v1"
                ),
                "models": [],
            },
            "event_model_registry_sha256": canonical_sha256(
                {
                    "schema_version": (
                        "cyz-brief-0018-event-proof-model-registry-v1"
                    ),
                    "models": [],
                }
            ),
            "proof_provenance": [],
            "proof_provenance_sha256": canonical_sha256([]),
            "replay_authority": "builtin-pinned-synthetic-fixture",
            "independent_replayer": (
                "event-contract-builtin-synthetic-registry-v1"
            ),
            "authoritative_physical_certificate": False,
            "physical_outcome_mass_estimated": False,
            "rank_used_for_event_selection": False,
        },
    }


def _configure_entry_certificates(
    record: dict[str, Any],
    cluster: dict[str, Any],
    *,
    complete_episode: bool,
    candidate_intervals: dict[
        str, tuple[Fraction, Fraction]
    ] | None = None,
) -> None:
    flags = record["flags"]
    certs = record["certificates"]
    candidate_intervals = candidate_intervals or {
        member["candidate_id"]: (Fraction(3, 4), Fraction(3, 4))
        for member in cluster["members"]
    }
    candidate_specs = [
        (
            candidate_id,
            f"physical-root-{candidate_id}",
            candidate_intervals[candidate_id],
        )
        for candidate_id in sorted(candidate_intervals)
    ]
    root_coverage = complete_coverage_certificate(candidate_specs)
    root_coverage["certificate_id"] = "coverage-entry"
    coverage_maps = coverage.manifest_maps(root_coverage)
    member_by_candidate = {
        member["candidate_id"]: member for member in cluster["members"]
    }
    for candidate_id, member in member_by_candidate.items():
        candidate = coverage_maps["candidates"][candidate_id]
        member["torus_image"] = copy.deepcopy(
            coverage_maps["images"][candidate["image_id"]][
                "lattice_vector"
            ]
        )
    _finalize_cluster(cluster)
    candidate_ids = coverage.physical_representative_candidate_ids(
        root_coverage
    )
    cluster_ids = sorted(
        member["candidate_id"] for member in cluster["members"]
    )
    earliest_time = coverage.dyadic(3, 2)
    excluded_leaf_ids = sorted(
        leaf_id
        for leaf_id, leaf in coverage_maps["leaves"].items()
        if leaf["classification"] == "excluded"
    )
    earlier_leaf_ids = sorted(
        leaf_id
        for leaf_id in excluded_leaf_ids
        if coverage.interval_fractions(
            coverage_maps["nodes"][
                coverage_maps["leaves"][leaf_id]["node_id"]
            ]["box"]["time"]
        )[1]
        <= Fraction(3, 4)
    )
    flags.update(
        {
            "solver_complete": True,
            "root_coverage_complete": True,
            "global_minimum_certified": True,
            "no_earlier_entry_certified": True,
            "entry_observed": True,
            "entry_earliest_certified": True,
            "entry_cluster_complete": True,
        }
    )
    certs["root_coverage"] = root_coverage
    certs["global_minimum"] = {
        "certificate_id": "global-minimum",
        "coverage_manifest_sha256": root_coverage["manifest_sha256"],
        "earliest_time": earliest_time,
        "candidate_ids": candidate_ids,
        "minimizer_candidate_ids": cluster_ids,
        "candidate_time_bindings": [
            {
                "candidate_id": candidate_id,
                "time_interval_sha256": canonical_sha256(
                    coverage_maps["candidates"][candidate_id][
                        "time_interval"
                    ]
                ),
            }
            for candidate_id in candidate_ids
        ],
        "excluded_leaf_ids": excluded_leaf_ids,
    }
    certs["no_earlier_entry"] = {
        "certificate_id": "no-earlier-entry",
        "coverage_manifest_sha256": root_coverage["manifest_sha256"],
        "earliest_time": earliest_time,
        "candidate_ids": cluster_ids,
        "excluded_before_leaf_ids": earlier_leaf_ids,
        "history_interval": coverage.exact_interval(0, Fraction(3, 4)),
        "initial_rho_lower_bound": coverage.dyadic(2),
        "r_in": coverage.dyadic(1),
        "hysteresis_registry_id": "hysteresis-r1-r2",
        "initial_armed_witness": {
            "observable": "rho=sqrt(2F_min)",
            "time": coverage.dyadic(0),
            "rho_affine": {
                "slope": coverage.dyadic(0),
                "intercept": coverage.dyadic(2),
            },
            "rho_range": coverage.exact_interval(2, 2),
            "backend": "exact-synthetic-fixture",
        },
    }
    certs["torus_log"] = {
        "certificate_id": "torus-log",
        "unique": True,
        "image_manifest_hash": coverage.image_manifest_sha256(
            root_coverage
        ),
    }
    record["entry_cluster"] = cluster
    flags["torus_log_unique"] = True
    if complete_episode:
        flags.update(
            {
                "outer_exit_observed": True,
                "outer_exit_certified": True,
                "episode_complete": True,
                "rearmed": True,
                "closest_episode_identified": True,
            }
        )
        certs["outer_exit"] = {
            "certificate_id": "outer-exit",
            "observed": True,
            "grazing_touch_count": 0,
            "strict_overshoot": True,
            "boundary_time": interval(2.0),
            "post_boundary_interval": {"lo": 2.25, "hi": 2.5},
            "post_boundary_witness": {
                "observable": "rho=sqrt(2F_min)",
                "exact_time_interval": coverage.exact_interval(
                    Fraction(9, 4), Fraction(5, 2)
                ),
                "time_interval_sha256": canonical_sha256(
                    {"lo": 2.25, "hi": 2.5}
                ),
                "rho_affine": {
                    "slope": coverage.dyadic(0),
                    "intercept": coverage.dyadic(5, 1),
                },
                "rho_range": coverage.exact_interval(
                    Fraction(5, 2), Fraction(5, 2)
                ),
                "backend": "exact-synthetic-fixture",
            },
            "rho_lower_bound": 2.5,
            "r_out": 2.0,
            "hysteresis_registry_id": "hysteresis-r1-r2",
            "global_minimum_certificate_id": "global-minimum",
            "coverage_manifest_sha256": root_coverage["manifest_sha256"],
            "image_manifest_sha256": coverage.image_manifest_sha256(
                root_coverage
            ),
            "rearmed": True,
        }
        certs["closest"] = {
            "certificate_id": "closest",
            "status": "episode_complete",
            "time": interval(1.0),
            "episode_id": "primary-episode",
            "coverage_manifest_sha256": root_coverage["manifest_sha256"],
            "global_minimum_certificate_id": "global-minimum",
        }
        record["episodes"] = [make_episode()]
        record["observation"]["continuation_state"] = "armed"


def build_hostile_record(primary: str) -> dict[str, Any]:
    """Build one synthetic, semantically valid fixture for a primary tag."""

    _require(primary in PRIMARY_PRECEDENCE, "$.primary_outcome", "unknown primary")
    record = make_base_record()
    record["sample_id"] = f"hostile-{primary}"
    flags = record["flags"]
    certs = record["certificates"]

    if primary == "source_invalid":
        record["source"].update(
            {
                "source_valid": False,
                "history_valid": False,
                "invalid_reasons": ["graph_bound_exceeded"],
                "initial_state": "unknown",
            }
        )
        record["flags"] = {name: False for name in FLAG_NAMES}
        flags = record["flags"]
        invalid_source = certs["source_validity"]
        certs.update({name: None for name in CERTIFICATE_KEYS})
        invalid_source.update(
            {
                "status": "invalid",
                "reason_codes": ["graph_bound_exceeded"],
            }
        )
        certs["source_validity"] = invalid_source
        record["observation"]["continuation_state"] = "invalid"

    elif primary == "left_censored_active_episode":
        record["source"]["initial_state"] = "active"
        flags.update(
            {
                "initial_armed": False,
                "left_censored": True,
                "right_censored": True,
            }
        )
        record["episodes"] = [
            make_episode(
                role="preexisting",
                left_censored=True,
                right_censored=True,
                complete=False,
            )
        ]
        record["observation"]["continuation_state"] = "active"

    elif primary == "torus_branch_ambiguous":
        flags["torus_branch_ambiguous"] = True
        certs["torus_log"] = {
            "certificate_id": "torus-ambiguity",
            "unique": False,
            "image_manifest_hash": "6" * 64,
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary == "ambiguous_tie":
        cluster = make_cluster("finite", complete=False)
        time_intervals = {
            "candidate-a": (Fraction(3, 4), Fraction(13, 16)),
            "candidate-b": (Fraction(25, 32), Fraction(27, 32)),
        }
        for member in cluster["members"]:
            lower, upper = time_intervals[member["candidate_id"]]
            member["box"]["time"] = {
                "lo": float(lower),
                "hi": float(upper),
            }
        _finalize_cluster(cluster)
        candidate_specs = [
            (
                candidate_id,
                f"physical-root-{candidate_id}",
                exact_interval,
            )
            for candidate_id, exact_interval in sorted(
                time_intervals.items()
            )
        ]
        root_coverage = complete_coverage_certificate(candidate_specs)
        root_coverage["certificate_id"] = "coverage-ambiguous-tie"
        ambiguous_maps = coverage.manifest_maps(root_coverage)
        for member in cluster["members"]:
            candidate = ambiguous_maps["candidates"][
                member["candidate_id"]
            ]
            member["torus_image"] = copy.deepcopy(
                ambiguous_maps["images"][candidate["image_id"]][
                    "lattice_vector"
                ]
            )
        _finalize_cluster(cluster)
        record["entry_cluster"] = cluster
        flags.update(
            {
                "ambiguous_tie": True,
                "solver_complete": True,
                "root_coverage_complete": True,
                "torus_log_unique": True,
                "entry_observed": True,
                "entry_tied": True,
                "rank_marks_complete": True,
                "normal_marks_complete": True,
                "entry_has_grazing": True,
                "entry_has_spatial_degeneracy": True,
            }
        )
        certs["root_coverage"] = root_coverage
        certs["torus_log"] = {
            "certificate_id": "torus-log-ambiguous-tie",
            "unique": True,
            "image_manifest_hash": coverage.image_manifest_sha256(
                root_coverage
            ),
        }
        certs["tie"] = {
            "certificate_id": "tie-order",
            "status": "ordering_ambiguous",
            "candidate_ids": ["candidate-a", "candidate-b"],
            "equal_time_proof": None,
            "ordering_proof": {
                "candidate_intervals": [
                    {
                        "candidate_id": candidate_id,
                        "time_interval": copy.deepcopy(
                            ambiguous_maps["candidates"][candidate_id][
                                "time_interval"
                            ]
                        ),
                    }
                    for candidate_id in ("candidate-a", "candidate-b")
                ],
                "all_candidates_isolated": True,
                "only_remaining_uncertainty": "earliest_order",
            },
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary == "numerically_unresolved":
        root_coverage = coverage.build_mixed_unresolved_certificate()
        root_coverage["certificate_id"] = "coverage-unresolved"
        cluster = make_cluster("singleton", rank=None)
        record["entry_cluster"] = cluster
        flags.update(
            {
                "entry_observed": True,
                "entry_cluster_complete": True,
                "entry_geometry_regular": True,
                "torus_log_unique": True,
            }
        )
        certs["root_coverage"] = root_coverage
        certs["torus_log"] = {
            "certificate_id": "torus-log-unresolved",
            "unique": True,
            "image_manifest_hash": coverage.image_manifest_sha256(
                root_coverage
            ),
        }
        unresolved_leaf_ids = coverage.unresolved_leaf_ids(root_coverage)
        certs["unresolved"] = {
            "certificate_id": "unresolved",
            "coverage_manifest_sha256": root_coverage["manifest_sha256"],
            "reason_codes": ["possible_earlier_root_box"],
            "unresolved_leaf_ids": unresolved_leaf_ids,
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary in ("no_entry_proved", "right_censored_no_entry"):
        root_coverage = complete_coverage_certificate(
            no_entry=True,
            time_domain=(
                (Fraction(0), Fraction(1))
                if primary == "no_entry_proved"
                else (Fraction(0), Fraction(4))
            ),
        )
        root_coverage["certificate_id"] = "coverage-no-entry"
        certs["root_coverage"] = root_coverage
        flags.update(
            {
                "solver_complete": True,
                "root_coverage_complete": True,
                "torus_log_unique": True,
            }
        )
        certs["torus_log"] = {
            "certificate_id": "torus-log-no-entry",
            "unique": True,
            "image_manifest_hash": coverage.image_manifest_sha256(
                root_coverage
            ),
        }
        if primary == "no_entry_proved":
            flags["no_entry_complete_time_domain_certified"] = True
            record["observation"]["complete_time_domain"] = True
            record["observation"]["continuation_state"] = "terminal"
            lattice = [1] * 8
            certs["no_entry"] = {
                "certificate_id": "no-entry-period",
                "mode": "exact_common_period",
                "coverage_manifest_sha256": root_coverage[
                    "manifest_sha256"
                ],
                "finite_window": None,
                "recurrence": {
                    "m": 1,
                    "L_w": coverage.dyadic(1),
                    "P": coverage.dyadic(1),
                    "relative_velocity": [coverage.dyadic(1)] * 8,
                    "transverse_periods": [coverage.dyadic(1)] * 8,
                    "lattice_vector": lattice,
                    "time_seam_cover": {
                        "t0": coverage.dyadic(0),
                        "tP": coverage.dyadic(1),
                        "lattice_vector": lattice,
                        "state_t0": [coverage.dyadic(0)] * 8,
                        "state_tP": [coverage.dyadic(1)] * 8,
                        "wrapped_state_t0": [coverage.dyadic(0)] * 8,
                        "wrapped_state_tP": [coverage.dyadic(0)] * 8,
                        "coverage_manifest_sha256": root_coverage[
                            "manifest_sha256"
                        ],
                    },
                },
                "global_lower_bound": None,
            }
        else:
            flags.update(
                {
                    "right_censored": True,
                    "no_entry_window_certified": True,
                }
            )
            record["observation"]["continuation_state"] = "armed"
            certs["no_entry"] = {
                "certificate_id": "no-entry-window",
                "mode": "finite_window",
                "coverage_manifest_sha256": root_coverage[
                    "manifest_sha256"
                ],
                "finite_window": {
                    "t0": coverage.dyadic(0),
                    "t1": coverage.dyadic(4),
                    "excluded_leaf_ids": sorted(
                        leaf["leaf_id"]
                        for leaf in root_coverage["manifest"]["leaves"]
                    ),
                },
                "recurrence": None,
                "global_lower_bound": None,
            }

    elif primary == "right_censored_active_episode":
        cluster = make_cluster("singleton")
        _configure_entry_certificates(
            record, cluster, complete_episode=False
        )
        flags.update(
            {
                "right_censored": True,
                "closest_window_only": True,
                "rank_marks_complete": True,
                "normal_marks_complete": True,
                "outer_grazing_observed": True,
                "entry_geometry_regular": True,
            }
        )
        root_coverage = certs["root_coverage"]
        certs["outer_exit"] = {
            "certificate_id": "outer-window",
            "observed": False,
            "grazing_touch_count": 1,
            "strict_overshoot": False,
            "boundary_time": None,
            "post_boundary_interval": None,
            "post_boundary_witness": None,
            "rho_lower_bound": None,
            "r_out": 2.0,
            "hysteresis_registry_id": "hysteresis-r1-r2",
            "global_minimum_certificate_id": None,
            "coverage_manifest_sha256": None,
            "image_manifest_sha256": None,
            "rearmed": False,
        }
        certs["closest"] = {
            "certificate_id": "closest-window",
            "status": "window_only",
            "time": interval(1.0),
            "episode_id": "primary-episode",
            "coverage_manifest_sha256": root_coverage["manifest_sha256"],
            "global_minimum_certificate_id": "global-minimum",
        }
        record["episodes"] = [
            make_episode(right_censored=True, complete=False)
        ]
        record["observation"]["continuation_state"] = "active"

    else:
        if primary == "tie_cluster":
            cluster = make_cluster("finite")
        else:
            rank = 2 if primary == "degenerate_spatial_minimum" else 3
            representative = make_representative(
                "entry-0",
                candidate_id="candidate-0",
                rank=rank,
                grazing=primary
                in ("grazing_entry", "degenerate_spatial_minimum"),
                degenerate=primary == "degenerate_spatial_minimum",
            )
            cluster = _finalize_cluster(
                {
                    "representation": "singleton",
                    "complete": True,
                    "unordered": True,
                    "cardinality": 1,
                    "members": [representative],
                    "member_hashes": [],
                    "members_sha256": "",
                    "implicit_set": None,
                }
            )
        _configure_entry_certificates(
            record, cluster, complete_episode=True
        )
        flags["rank_marks_complete"] = True
        flags["normal_marks_complete"] = True
        if primary == "tie_cluster":
            flags.update(
                {
                    "entry_tied": True,
                    "entry_has_grazing": True,
                    "entry_has_spatial_degeneracy": True,
                }
            )
            coverage_maps = coverage.manifest_maps(certs["root_coverage"])
            member_map = {
                member["candidate_id"]: member
                for member in cluster["members"]
            }
            certs["tie"] = {
                "certificate_id": "tie-complete",
                "status": "complete_cluster",
                "candidate_ids": ["candidate-a", "candidate-b"],
                "equal_time_proof": {
                    "exact_time": coverage.dyadic(3, 2),
                    "bindings": [
                        {
                            "candidate_id": candidate_id,
                            "representative_id": member_map[candidate_id][
                                "representative_id"
                            ],
                            "member_time_sha256": canonical_sha256(
                                member_map[candidate_id]["box"]["time"]
                            ),
                            "candidate_time_sha256": canonical_sha256(
                                coverage_maps["candidates"][candidate_id][
                                    "time_interval"
                                ]
                            ),
                        }
                        for candidate_id in ("candidate-a", "candidate-b")
                    ],
                },
                "ordering_proof": None,
            }
        elif primary == "degenerate_spatial_minimum":
            flags["entry_has_spatial_degeneracy"] = True
            flags["entry_has_grazing"] = True
        elif primary == "grazing_entry":
            flags["entry_has_grazing"] = True
        else:
            flags["entry_geometry_regular"] = True

    record["primary_outcome"] = classify_primary(flags)
    _require(
        record["primary_outcome"] == primary,
        "$.primary_outcome",
        f"fixture builder selected {record['primary_outcome']} instead of {primary}",
    )
    record["precedence_trace"] = precedence_trace(primary)
    _bind_record_to_coverage_problem(record)
    _bind_scope_provenance(record)
    validate_record(record)
    return record


def build_implicit_cluster_record() -> dict[str, Any]:
    record = build_hostile_record("tie_cluster")
    record["sample_id"] = "hostile-positive-dimensional-tie"
    cluster = make_cluster("implicit")
    record["entry_cluster"] = cluster
    root_coverage = coverage.build_singular_cluster_certificate()
    root_coverage["certificate_id"] = "coverage-implicit-set"
    maps = coverage.manifest_maps(root_coverage)
    candidate_id = "candidate-singular-set"
    singular_leaf = maps["leaves"][
        maps["candidates"][candidate_id]["leaf_id"]
    ]
    cluster["implicit_set"]["set_certificate_ref"] = singular_leaf[
        "witness"
    ]["set_certificate_sha256"]
    excluded_leaf_ids = sorted(
        leaf_id
        for leaf_id, leaf in maps["leaves"].items()
        if leaf["classification"] == "excluded"
    )
    earlier_leaf_ids = sorted(
        leaf_id
        for leaf_id in excluded_leaf_ids
        if coverage.interval_fractions(
            maps["nodes"][maps["leaves"][leaf_id]["node_id"]]["box"][
                "time"
            ]
        )[1]
        <= Fraction(3, 4)
    )
    certs = record["certificates"]
    certs["root_coverage"] = root_coverage
    certs["global_minimum"] = {
        "certificate_id": "global-minimum",
        "coverage_manifest_sha256": root_coverage["manifest_sha256"],
        "earliest_time": coverage.dyadic(3, 2),
        "candidate_ids": [candidate_id],
        "minimizer_candidate_ids": [candidate_id],
        "candidate_time_bindings": [
            {
                "candidate_id": candidate_id,
                "time_interval_sha256": canonical_sha256(
                    maps["candidates"][candidate_id]["time_interval"]
                ),
            }
        ],
        "excluded_leaf_ids": excluded_leaf_ids,
    }
    certs["no_earlier_entry"] = {
        "certificate_id": "no-earlier-entry",
        "coverage_manifest_sha256": root_coverage["manifest_sha256"],
        "earliest_time": coverage.dyadic(3, 2),
        "candidate_ids": [candidate_id],
        "excluded_before_leaf_ids": earlier_leaf_ids,
        "history_interval": coverage.exact_interval(0, Fraction(3, 4)),
        "initial_rho_lower_bound": coverage.dyadic(2),
        "r_in": coverage.dyadic(1),
        "hysteresis_registry_id": "hysteresis-r1-r2",
        "initial_armed_witness": {
            "observable": "rho=sqrt(2F_min)",
            "time": coverage.dyadic(0),
            "rho_affine": {
                "slope": coverage.dyadic(0),
                "intercept": coverage.dyadic(2),
            },
            "rho_range": coverage.exact_interval(2, 2),
            "backend": "exact-synthetic-fixture",
        },
    }
    certs["torus_log"]["image_manifest_hash"] = (
        coverage.image_manifest_sha256(root_coverage)
    )
    certs["tie"] = {
        "certificate_id": "tie-complete",
        "status": "complete_cluster",
        "candidate_ids": [candidate_id],
        "equal_time_proof": {
            "exact_time": coverage.dyadic(3, 2),
            "bindings": [
                {
                    "candidate_id": candidate_id,
                    "representative_id": cluster["implicit_set"][
                        "set_certificate_ref"
                    ],
                    "member_time_sha256": canonical_sha256(
                        cluster["implicit_set"]["domain_boxes"][0]["time"]
                    ),
                    "candidate_time_sha256": canonical_sha256(
                        maps["candidates"][candidate_id]["time_interval"]
                    ),
                }
            ],
        },
        "ordering_proof": None,
    }
    certs["outer_exit"]["coverage_manifest_sha256"] = root_coverage[
        "manifest_sha256"
    ]
    certs["outer_exit"]["image_manifest_sha256"] = (
        coverage.image_manifest_sha256(root_coverage)
    )
    certs["closest"]["coverage_manifest_sha256"] = root_coverage[
        "manifest_sha256"
    ]
    record["flags"]["entry_positive_dimensional"] = True
    record["flags"]["entry_has_grazing"] = False
    record["flags"]["entry_has_spatial_degeneracy"] = False
    record["flags"]["rank_marks_complete"] = False
    record["flags"]["normal_marks_complete"] = False
    _bind_record_to_coverage_problem(record)
    _bind_scope_provenance(record)
    validate_record(record)
    return record


def hysteresis_trace(
    radii: Sequence[float],
    *,
    r_in: float,
    r_out: float,
    initial_state: str = "armed",
) -> dict[str, Any]:
    """Synthetic discrete control for the strict-overshoot state machine."""

    if not 0.0 < r_in < r_out:
        raise ValueError("require 0<r_in<r_out")
    if initial_state not in ("armed", "active"):
        raise ValueError("initial state must be armed or active")
    state = initial_state
    transitions: list[dict[str, Any]] = []
    secondary_inner_contacts = 0
    outer_grazes = 0
    for index, radius in enumerate(radii):
        _require_number(radius, f"$radii[{index}]")
        if state == "armed" and radius <= r_in:
            state = "active"
            transitions.append(
                {"index": index, "transition": "inner_entry"}
            )
        elif state == "active":
            if radius > r_out:
                state = "armed"
                transitions.append(
                    {"index": index, "transition": "strict_outer_exit_rearm"}
                )
            elif radius == r_out:
                outer_grazes += 1
            elif radius <= r_in:
                secondary_inner_contacts += 1
    return {
        "initial_state": initial_state,
        "final_state": state,
        "transitions": transitions,
        "outer_grazes": outer_grazes,
        "secondary_inner_contacts": secondary_inner_contacts,
    }


def synthetic_primary_mass_rows(
    record: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return one synthetic incidence row per sample, never per tie member.

    The helper is a schema-control device only.  ``synthetic_count`` is not a
    physical probability or an outcome-mass estimate.
    """

    validate_record(record)
    return [
        {
            "sample_id": record["sample_id"],
            "primary_outcome": record["primary_outcome"],
            "synthetic_count": 1,
        }
    ]


def as_certified_solver_output(
    record: dict[str, Any], *, backend: str
) -> dict[str, Any]:
    """Rebind a validated fixture-shaped record to a formal solver backend."""

    converted = copy.deepcopy(record)
    root_coverage = converted["certificates"]["root_coverage"]
    _require(
        root_coverage is not None,
        "$.certificates.root_coverage",
        "solver conversion requires coverage",
    )
    for leaf in root_coverage["manifest"]["leaves"]:
        if "backend" in leaf["witness"]:
            leaf["witness"]["backend"] = backend
    coverage.recompute_manifest_hash(root_coverage)
    manifest_hash = root_coverage["manifest_sha256"]
    certs = converted["certificates"]
    for name in (
        "global_minimum",
        "no_earlier_entry",
        "no_entry",
        "unresolved",
        "closest",
        "outer_exit",
    ):
        certificate = certs[name]
        if (
            certificate is not None
            and "coverage_manifest_sha256" in certificate
            and certificate["coverage_manifest_sha256"] is not None
        ):
            certificate["coverage_manifest_sha256"] = manifest_hash
    no_entry = certs["no_entry"]
    if (
        no_entry is not None
        and no_entry["recurrence"] is not None
    ):
        no_entry["recurrence"]["backend"] = backend
        no_entry["recurrence"]["time_seam_cover"][
            "coverage_manifest_sha256"
        ] = manifest_hash
    if (
        no_entry is not None
        and no_entry["global_lower_bound"] is not None
    ):
        no_entry["global_lower_bound"]["backend"] = backend
    outer = certs["outer_exit"]
    if (
        outer is not None
        and outer["post_boundary_witness"] is not None
    ):
        outer["post_boundary_witness"]["backend"] = backend
    no_earlier = certs["no_earlier_entry"]
    if no_earlier is not None:
        no_earlier["initial_armed_witness"]["backend"] = backend
    problem_sha256, problem, _ = _coverage_problem_context(
        root_coverage
    )
    run_manifest = {
        "run_id": f"formal-{converted['sample_id']}",
        "backend": backend,
        "executable_sha256": hashlib.sha256(
            backend.encode("utf-8")
        ).hexdigest(),
        "input_manifest_sha256": root_coverage["manifest"][
            "exact_inputs_sha256"
        ],
        "coverage_manifest_sha256": root_coverage["manifest_sha256"],
        "proof_artifact_sha256": canonical_sha256(root_coverage),
        "problem_commitment_sha256": problem_sha256,
        "source_state_sha256": problem["source_state_sha256"],
        "source_registry_sha256": problem["source_registry_sha256"],
        "source_draw_registry_sha256": problem[
            "source_draw_registry_sha256"
        ],
        "source_validity_sha256": canonical_sha256(
            _source_validity_binding(converted)
        ),
        "solver_registry_sha256": problem["solver_registry_sha256"],
        "independent_replayer": "brief-0019-independent-event-replayer",
    }
    converted["scope"] = {
        "record_kind": "certified_solver_output",
        "physical_root_solver_run": True,
        "proof_backend": backend,
        "solver_run_manifest": run_manifest,
        "solver_run_manifest_sha256": canonical_sha256(run_manifest),
        "problem_commitment_sha256": problem_sha256,
        "source_state_sha256": problem["source_state_sha256"],
        "source_registry_sha256": problem["source_registry_sha256"],
        "source_draw_registry_sha256": problem[
            "source_draw_registry_sha256"
        ],
        "source_validity": _source_validity_binding(converted),
        "source_validity_sha256": canonical_sha256(
            _source_validity_binding(converted)
        ),
        "solver_registry_sha256": problem["solver_registry_sha256"],
        "proof_provenance": [],
        "proof_provenance_sha256": canonical_sha256([]),
        "replay_authority": (
            "external-0019-independent-replay-required"
        ),
        "independent_replayer": (
            "brief-0019-independent-event-replayer"
        ),
        "authoritative_physical_certificate": False,
        "physical_outcome_mass_estimated": False,
        "rank_used_for_event_selection": False,
    }
    _bind_scope_provenance(converted)
    validate_record(converted)
    return converted


def _coordinated_root_rewrite_is_rejected(
    baseline: dict[str, Any],
) -> bool:
    """Rewrite all ordinary root-time references but not the trust anchor."""

    hostile = copy.deepcopy(baseline)
    root_coverage = hostile["certificates"]["root_coverage"]
    manifest = root_coverage["manifest"]
    root_leaf = next(
        leaf
        for leaf in manifest["leaves"]
        if leaf["classification"] == "unique_root"
    )
    new_time = Fraction(13, 16)
    root_model = root_leaf["witness"]["root_model"]
    root_model["root"][2] = coverage.dyadic_from_fraction(new_time)
    root_model["constant"][2] = coverage.dyadic_from_fraction(new_time)
    candidate = manifest["candidates"][0]
    candidate["time_interval"] = coverage.exact_interval(
        new_time, new_time
    )
    coverage.recompute_manifest_hash(root_coverage)
    manifest_hash = root_coverage["manifest_sha256"]
    certs = hostile["certificates"]
    for name in (
        "global_minimum",
        "no_earlier_entry",
        "outer_exit",
        "closest",
    ):
        certs[name]["coverage_manifest_sha256"] = manifest_hash
    exact_time = coverage.dyadic_from_fraction(new_time)
    certs["global_minimum"]["earliest_time"] = exact_time
    certs["global_minimum"]["candidate_time_bindings"][0][
        "time_interval_sha256"
    ] = canonical_sha256(candidate["time_interval"])
    certs["no_earlier_entry"]["earliest_time"] = exact_time
    certs["no_earlier_entry"]["history_interval"]["hi"] = exact_time
    member = hostile["entry_cluster"]["members"][0]
    member["box"]["time"] = {
        "lo": float(new_time),
        "hi": float(new_time),
    }
    hostile["episodes"][0]["T_in"] = copy.deepcopy(
        member["box"]["time"]
    )
    _finalize_cluster(hostile["entry_cluster"])
    try:
        validate_record(hostile)
    except (ContractError, coverage.ProofError):
        return True
    return False


def _event_model_registry_covers_required_layers(
    fixtures: dict[str, dict[str, Any]],
) -> bool:
    rows = [
        row
        for fixture in fixtures.values()
        for row in fixture["scope"]["event_model_registry"]["models"]
    ]
    kinds = {row["model_kind"] for row in rows}
    ids = {row["model_id"] for row in rows}
    return {
        "event_header",
        "certificate_source_validity",
        "certificate_torus_log",
        "certificate_global_minimum",
        "certificate_no_earlier_entry",
        "certificate_closest",
        "certificate_outer_exit",
        "certificate_no_entry",
        "coverage_leaf",
        "coverage_quotient",
        "entry_cluster",
        "member_geometry_jet",
        "member_rank_jet",
        "episode_ledger",
    }.issubset(kinds) and any(
        model_id.startswith("implicit-set::") for model_id in ids
    )


def build_control_report(schema_path: Path) -> dict[str, Any]:
    schema = strict_load_json(schema_path)
    validate_schema_document(schema)
    fixtures = {
        primary: build_hostile_record(primary)
        for primary in PRIMARY_PRECEDENCE
    }
    implicit = build_implicit_cluster_record()
    registry_fixtures = {
        **fixtures,
        "positive_dimensional_tie": implicit,
    }
    formal_envelope = as_certified_solver_output(
        fixtures["regular_first_entry"],
        backend="formal-envelope-control",
    )
    tangent_trace = hysteresis_trace(
        (2.5, 1.5, 1.0, 1.4, 2.0, 1.5, 1.0, 2.1, 1.0),
        r_in=1.0,
        r_out=2.0,
    )
    transition_names = [
        row["transition"] for row in tangent_trace["transitions"]
    ]
    deleted_leaf_rejected = False
    try:
        coverage.validate_coverage_certificate(
            coverage.deleted_leaf_mutation(
                fixtures["regular_first_entry"]["certificates"][
                    "root_coverage"
                ]
            )
        )
    except coverage.ProofError:
        deleted_leaf_rejected = True
    tie_rows = synthetic_primary_mass_rows(fixtures["tie_cluster"])
    missing_geometry_flags = copy.deepcopy(
        fixtures["regular_first_entry"]["flags"]
    )
    missing_geometry_flags["entry_geometry_regular"] = False
    checks = {
        "all_primary_tags_have_valid_hostile_schema_fixtures": (
            set(fixtures) == set(PRIMARY_PRECEDENCE)
        ),
        "each_fixture_has_exactly_one_primary_value": all(
            fixture["primary_outcome"] == primary
            for primary, fixture in fixtures.items()
        ),
        "ambiguous_tie_precedes_generic_unresolved": (
            PRIMARY_PRECEDENCE.index("ambiguous_tie")
            < PRIMARY_PRECEDENCE.index("numerically_unresolved")
        ),
        "implicit_positive_dimensional_cluster_is_not_scalarized": (
            implicit["entry_cluster"]["members"] == []
            and implicit["entry_cluster"]["cardinality"] == "continuum"
        ),
        "outer_touch_does_not_rearm": (
            tangent_trace["outer_grazes"] == 1
            and transition_names.count("strict_outer_exit_rearm") == 1
        ),
        "active_inner_contact_is_secondary": (
            tangent_trace["secondary_inner_contacts"] >= 1
        ),
        "source_invalid_fixture_has_no_root_certificate": (
            fixtures["source_invalid"]["certificates"]["root_coverage"]
            is None
        ),
        "source_invalid_freezes_all_event_flags_and_certificates": (
            all(
                value is False
                for value in fixtures["source_invalid"]["flags"].values()
            )
            and all(
                value is None
                for name, value in fixtures["source_invalid"][
                    "certificates"
                ].items()
                if name != "source_validity"
            )
        ),
        "tied_grazing_degenerate_cluster_has_one_primary_row": (
            fixtures["tie_cluster"]["flags"]["entry_tied"]
            and fixtures["tie_cluster"]["flags"]["entry_has_grazing"]
            and fixtures["tie_cluster"]["flags"][
                "entry_has_spatial_degeneracy"
            ]
            and len(tie_rows) == 1
        ),
        "deleted_leaf_fails_structural_replay": deleted_leaf_rejected,
        "coordinated_root_rewrite_fails_pinned_replay": (
            _coordinated_root_rewrite_is_rejected(
                fixtures["regular_first_entry"]
            )
        ),
        "unified_proof_model_registry_covers_all_event_layers": (
            _event_model_registry_covers_required_layers(
                registry_fixtures
            )
        ),
        "source_v2_bindings_are_carried_by_formal_envelope": (
            formal_envelope["scope"]["source_registry_sha256"]
            is not None
            and formal_envelope["scope"][
                "source_draw_registry_sha256"
            ]
            is not None
            and formal_envelope["scope"]["source_state_sha256"]
            is not None
            and formal_envelope["scope"]["source_validity"][
                "status"
            ]
            == "valid"
        ),
        "physical_envelope_requires_external_0019_replay": (
            formal_envelope["scope"]["record_kind"]
            == "certified_solver_output"
            and not formal_envelope["scope"][
                "authoritative_physical_certificate"
            ]
            and formal_envelope["scope"]["independent_replayer"]
            == "brief-0019-independent-event-replayer"
        ),
        "missing_completed_geometry_routes_to_numerical_unresolved": (
            classify_primary(missing_geometry_flags)
            == "numerically_unresolved"
        ),
        "ambiguous_tie_uses_two_isolated_interval_root_proofs": (
            len(
                fixtures["ambiguous_tie"]["certificates"][
                    "root_coverage"
                ]["manifest"]["candidates"]
            )
            >= 2
            and all(
                leaf["witness"].get("root_model", {}).get("kind")
                == "separable_quadratic"
                for leaf in fixtures["ambiguous_tie"]["certificates"][
                    "root_coverage"
                ]["manifest"]["leaves"]
                if leaf["classification"] == "unique_root"
            )
        ),
        "finite_window_and_complete_time_no_entry_are_distinct": (
            fixtures["right_censored_no_entry"]["certificates"]["no_entry"][
                "mode"
            ]
            == "finite_window"
            and fixtures["no_entry_proved"]["certificates"]["no_entry"][
                "mode"
            ]
            in ("exact_common_period", "global_lower_bound")
        ),
        "rank_two_fixture_has_seven_dimensional_normal": (
            fixtures["degenerate_spatial_minimum"]["entry_cluster"]["members"][
                0
            ]["jet_normal"]["normal_dimension"]
            == 7
        ),
        "outer_exit_has_replayable_post_boundary_rho_bound": (
            fixtures["regular_first_entry"]["certificates"]["outer_exit"][
                "post_boundary_witness"
            ]
            is not None
        ),
        "no_physical_solver_or_mass_claim": all(
            not fixture["scope"]["physical_root_solver_run"]
            and not fixture["scope"]["physical_outcome_mass_estimated"]
            for fixture in fixtures.values()
        ),
    }
    status = "PASS" if all(checks.values()) else "FAIL"
    return {
        "schema_version": CONTROL_SCHEMA_VERSION,
        "event_schema_version": EVENT_SCHEMA_VERSION,
        "status": status,
        "scope": (
            "synthetic event-contract controls only; no physical root solver, "
            "source sampler, event population, or outcome mass"
        ),
        "event_schema_normalized_lf_sha256": normalized_lf_sha256(
            schema_path
        ),
        "event_schema_canonical_sha256": canonical_sha256(schema),
        "primary_precedence": list(PRIMARY_PRECEDENCE),
        "fixture_canonical_sha256": {
            primary: canonical_sha256(fixture)
            for primary, fixture in fixtures.items()
        },
        "implicit_cluster_fixture_canonical_sha256": canonical_sha256(
            implicit
        ),
        "hysteresis_control": tangent_trace,
        "checks": checks,
    }


def parse_arguments() -> argparse.Namespace:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--schema",
        type=Path,
        default=directory / "event_record.schema.json",
        help="strict event-record JSON Schema",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=directory / "event_schema_controls.json",
        help="deterministic control report",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare regenerated and stored parsed JSON semantics",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    report = build_control_report(arguments.schema)
    if report["status"] != "PASS":
        raise SystemExit("Brief 0018 event-contract controls failed")
    if arguments.check:
        if not arguments.output.exists():
            raise SystemExit(f"control report missing: {arguments.output}")
        try:
            stored = strict_load_json(arguments.output)
        except (OSError, UnicodeError, ContractError) as error:
            raise SystemExit(f"control report parse failure: {error}") from error
        if not type_strict_equal(stored, report):
            raise SystemExit("event-contract control report semantic mismatch")
        action = "verified canonical semantic JSON"
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(
            serialize_json(report),
            encoding="utf-8",
            newline="\n",
        )
        action = "wrote"
    print(
        f"{report['status']}: {action}: {arguments.output}; "
        f"canonical_sha256={canonical_sha256(report)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
