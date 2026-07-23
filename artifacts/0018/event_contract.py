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
from pathlib import Path
from typing import Any, Iterable, Sequence


EVENT_SCHEMA_VERSION = "cyz-brief-0018-event-record-v1"
CONTROL_SCHEMA_VERSION = "cyz-brief-0018-event-schema-controls-v1"
TARGET_DIMENSION = 9
DOMAIN_DIMENSION = 3
HASH_PATTERN = re.compile(r"^[0-9a-f]{64}$")

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
    "implicit_set",
}

REPRESENTATIVE_KEYS = {
    "representative_id",
    "box",
    "torus_image",
    "log_unique",
    "s",
    "F",
    "grad_sigma",
    "dF_dt",
    "H_sigma_sigma",
    "jet_normal",
}

JET_NORMAL_KEYS = {
    "coordinate_basis",
    "G",
    "H",
    "J",
    "singular_value_intervals",
    "rank",
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
        {"status", "exact_rank", "possible_ranks", "proof_kind"},
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
    _require_string(rank["proof_kind"], f"{path}.proof_kind")
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


def _validate_representative(value: Any, path: str) -> dict[str, Any]:
    representative = _require_exact_keys(value, REPRESENTATIVE_KEYS, path)
    _require_string(
        representative["representative_id"],
        f"{path}.representative_id",
    )
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
        implicit = _require_exact_keys(
            cluster["implicit_set"],
            {
                "defining_equations",
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

    coverage = _validate_optional_certificate(
        certs["root_coverage"],
        {
            "certificate_id",
            "complete",
            "coverage_tree_hash",
            "deterministic_budget_hash",
            "leaf_counts",
        },
        f"{path}.root_coverage",
    )
    if coverage is not None:
        _require_string(coverage["certificate_id"], f"{path}.root_coverage.certificate_id")
        _require_bool(coverage["complete"], f"{path}.root_coverage.complete")
        _require_hash(coverage["coverage_tree_hash"], f"{path}.root_coverage.coverage_tree_hash")
        _require_hash(coverage["deterministic_budget_hash"], f"{path}.root_coverage.deterministic_budget_hash")
        leaves = _require_exact_keys(
            coverage["leaf_counts"],
            {"excluded", "unique_root", "singular_cluster", "unresolved"},
            f"{path}.root_coverage.leaf_counts",
        )
        for name, count in leaves.items():
            integer = _require_integer(count, f"{path}.root_coverage.leaf_counts.{name}")
            _require(integer >= 0, f"{path}.root_coverage.leaf_counts.{name}", "count must be nonnegative")
        if coverage["complete"]:
            _require(leaves["unresolved"] == 0, f"{path}.root_coverage.leaf_counts.unresolved", "complete coverage cannot have unresolved leaves")

    for name in ("global_minimum", "no_earlier_entry"):
        certificate = _validate_optional_certificate(
            certs[name],
            {"certificate_id", "complete"},
            f"{path}.{name}",
        )
        if certificate is not None:
            _require_string(certificate["certificate_id"], f"{path}.{name}.certificate_id")
            _require_bool(certificate["complete"], f"{path}.{name}.complete")

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
        {"certificate_id", "status", "candidate_ids"},
        f"{path}.tie",
    )
    if tie is not None:
        _require_string(tie["certificate_id"], f"{path}.tie.certificate_id")
        _require_enum(
            tie["status"],
            ("none", "complete_cluster", "ordering_ambiguous"),
            f"{path}.tie.status",
        )
        _validate_string_list(tie["candidate_ids"], f"{path}.tie.candidate_ids")

    outer = _validate_optional_certificate(
        certs["outer_exit"],
        {
            "certificate_id",
            "observed",
            "strict_overshoot",
            "boundary_time",
            "rearmed",
        },
        f"{path}.outer_exit",
    )
    if outer is not None:
        _require_string(outer["certificate_id"], f"{path}.outer_exit.certificate_id")
        for name in ("observed", "strict_overshoot", "rearmed"):
            _require_bool(outer[name], f"{path}.outer_exit.{name}")
        if outer["boundary_time"] is not None:
            _validate_interval(outer["boundary_time"], f"{path}.outer_exit.boundary_time")
        if outer["strict_overshoot"]:
            _require(outer["observed"], f"{path}.outer_exit.observed", "strict overshoot requires observed exit")
            _require(outer["boundary_time"] is not None, f"{path}.outer_exit.boundary_time", "strict overshoot requires boundary time")
        if outer["rearmed"]:
            _require(outer["strict_overshoot"], f"{path}.outer_exit.strict_overshoot", "rearming requires strict overshoot")

    no_entry = _validate_optional_certificate(
        certs["no_entry"],
        {"certificate_id", "mode", "complete", "period"},
        f"{path}.no_entry",
    )
    if no_entry is not None:
        _require_string(no_entry["certificate_id"], f"{path}.no_entry.certificate_id")
        mode = _require_enum(
            no_entry["mode"],
            ("finite_window", "exact_common_period", "global_lower_bound"),
            f"{path}.no_entry.mode",
        )
        _require_bool(no_entry["complete"], f"{path}.no_entry.complete")
        if no_entry["period"] is not None:
            _validate_interval(no_entry["period"], f"{path}.no_entry.period")
        if mode == "exact_common_period":
            _require(no_entry["period"] is not None, f"{path}.no_entry.period", "exact period mode requires a period")
        else:
            _require(no_entry["period"] is None, f"{path}.no_entry.period", "period is allowed only for exact_common_period")

    unresolved = _validate_optional_certificate(
        certs["unresolved"],
        {"certificate_id", "reason_codes", "unresolved_leaf_count"},
        f"{path}.unresolved",
    )
    if unresolved is not None:
        _require_string(unresolved["certificate_id"], f"{path}.unresolved.certificate_id")
        reasons = _validate_string_list(unresolved["reason_codes"], f"{path}.unresolved.reason_codes")
        _require(bool(reasons), f"{path}.unresolved.reason_codes", "unresolved record needs a reason")
        count = _require_integer(unresolved["unresolved_leaf_count"], f"{path}.unresolved.unresolved_leaf_count")
        _require(count >= 0, f"{path}.unresolved.unresolved_leaf_count", "count must be nonnegative")

    closest = _validate_optional_certificate(
        certs["closest"],
        {"certificate_id", "status"},
        f"{path}.closest",
    )
    if closest is not None:
        _require_string(closest["certificate_id"], f"{path}.closest.certificate_id")
        _require_enum(
            closest["status"],
            ("none", "episode_complete", "window_only", "unresolved"),
            f"{path}.closest.status",
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
    raise ContractError(
        "$.flags: completed singleton entry has no certified geometry class"
    )


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
        flags["source_valid"] == source["source_valid"],
        "$.flags.source_valid",
        "source flag disagrees with source block",
    )
    _require(
        flags["history_valid"] == source["history_valid"],
        "$.flags.history_valid",
        "history flag disagrees with source block",
    )
    _require(
        flags["initial_armed"] == (source["initial_state"] == "armed"),
        "$.flags.initial_armed",
        "initial armed flag disagrees with source state",
    )
    _require(
        flags["torus_log_unique"]
        != flags["torus_branch_ambiguous"],
        "$.flags.torus_log_unique",
        "torus uniqueness and branch ambiguity must be complements",
    )
    _require(
        primary == classify_primary(flags),
        "$.primary_outcome",
        "primary outcome violates deterministic precedence",
    )
    _require(
        record["precedence_trace"] == precedence_trace(primary),
        "$.precedence_trace",
        "precedence trace does not end at the selected primary outcome",
    )

    source_certificate = _require_certificate(
        certs, "source_validity", primary
    )
    expected_source_status = (
        "valid"
        if flags["source_valid"] and flags["history_valid"]
        else "invalid"
    )
    _require(
        source_certificate["status"] == expected_source_status,
        "$.certificates.source_validity.status",
        "source certificate status disagrees with source validity",
    )

    _validate_rank_mark_flags(cluster, flags)

    if cluster is None:
        _require(
            not flags["entry_observed"]
            or primary == "left_censored_active_episode",
            "$.entry_cluster",
            "observed entry requires an entry cluster",
        )
        _require(
            not flags["entry_cluster_complete"],
            "$.flags.entry_cluster_complete",
            "missing cluster cannot be complete",
        )
    else:
        _require(
            flags["entry_cluster_complete"] == cluster["complete"],
            "$.flags.entry_cluster_complete",
            "cluster-complete flag disagrees with cluster",
        )
        if cluster["representation"] == "singleton":
            _require(
                not flags["entry_tied"],
                "$.flags.entry_tied",
                "singleton cluster cannot be tied",
            )
        else:
            _require(
                flags["entry_tied"],
                "$.flags.entry_tied",
                "non-singleton/implicit cluster must be tied",
            )
        _require(
            flags["entry_positive_dimensional"]
            == (cluster["representation"] == "implicit"),
            "$.flags.entry_positive_dimensional",
            "positive-dimensional flag disagrees with representation",
        )

    if flags["outer_exit_certified"]:
        _require(flags["outer_exit_observed"], "$.flags.outer_exit_observed", "certified exit must be observed")
        _require(flags["episode_complete"], "$.flags.episode_complete", "certified exit must complete episode")
        _require(flags["rearmed"], "$.flags.rearmed", "strict exit must re-arm")
    if flags["rearmed"]:
        _require(flags["outer_exit_certified"], "$.flags.outer_exit_certified", "rearming without strict exit is forbidden")
    if flags["outer_grazing_observed"] and not flags["outer_exit_certified"]:
        _require(not flags["rearmed"], "$.flags.rearmed", "outer grazing alone cannot re-arm")

    if flags["closest_episode_identified"]:
        _require(flags["episode_complete"], "$.flags.episode_complete", "episode closest requires a completed episode")
        _require(not flags["closest_window_only"], "$.flags.closest_window_only", "episode closest and window-only are disjoint")
    if flags["closest_window_only"]:
        _require(not flags["episode_complete"], "$.flags.episode_complete", "window-only closest requires incomplete episode")

    outer_certificate = certs["outer_exit"]
    if outer_certificate is not None:
        _require(
            flags["outer_exit_observed"] == outer_certificate["observed"],
            "$.flags.outer_exit_observed",
            "outer-exit flag disagrees with certificate",
        )
        _require(
            flags["outer_exit_certified"]
            == outer_certificate["strict_overshoot"],
            "$.flags.outer_exit_certified",
            "strict-overshoot flag disagrees with certificate",
        )
        _require(
            flags["rearmed"] == outer_certificate["rearmed"],
            "$.flags.rearmed",
            "re-arm flag disagrees with certificate",
        )

    closest_certificate = certs["closest"]
    if closest_certificate is not None:
        _require(
            flags["closest_episode_identified"]
            == (closest_certificate["status"] == "episode_complete"),
            "$.flags.closest_episode_identified",
            "closest-episode flag disagrees with certificate",
        )
        _require(
            flags["closest_window_only"]
            == (closest_certificate["status"] == "window_only"),
            "$.flags.closest_window_only",
            "window-only flag disagrees with certificate",
        )

    secondary_contacts = sum(
        episode["secondary_inner_contacts"]
        for episode in record["episodes"]
    )
    component_transitions = [
        event["transition"]
        for episode in record["episodes"]
        for event in episode["component_events"]
    ]
    _require(
        flags["episode_has_secondary_inner_contact"]
        == (secondary_contacts > 0),
        "$.flags.episode_has_secondary_inner_contact",
        "secondary-contact flag disagrees with episode ledger",
    )
    _require(
        flags["episode_has_component_merger"]
        == ("merge" in component_transitions),
        "$.flags.episode_has_component_merger",
        "merger flag disagrees with component lineage",
    )
    _require(
        flags["episode_has_component_split"]
        == ("split" in component_transitions),
        "$.flags.episode_has_component_split",
        "split flag disagrees with component lineage",
    )

    if flags["root_coverage_complete"]:
        coverage = _require_certificate(certs, "root_coverage", primary)
        _require(coverage["complete"], "$.certificates.root_coverage.complete", "coverage flag requires complete certificate")
    if flags["global_minimum_certified"]:
        certificate = _require_certificate(certs, "global_minimum", primary)
        _require(certificate["complete"], "$.certificates.global_minimum.complete", "global-minimum flag requires complete certificate")
    if flags["no_earlier_entry_certified"]:
        certificate = _require_certificate(certs, "no_earlier_entry", primary)
        _require(certificate["complete"], "$.certificates.no_earlier_entry.complete", "no-earlier flag requires complete certificate")

    if primary == "source_invalid":
        _require(
            not (flags["source_valid"] and flags["history_valid"]),
            "$.flags",
            "source_invalid needs a source/history failure",
        )
        _require(cluster is None, "$.entry_cluster", "invalid source cannot have authoritative entry marks")
        return

    _require(flags["source_valid"], "$.flags.source_valid", "non-invalid outcome requires valid source")
    _require(flags["history_valid"], "$.flags.history_valid", "non-invalid outcome requires valid history")

    if primary == "left_censored_active_episode":
        _require(flags["left_censored"], "$.flags.left_censored", "left-censored primary requires flag")
        _require(source["initial_state"] == "active", "$.source.initial_state", "left-censored episode must start active")
        _require(bool(record["episodes"]), "$.episodes", "left-censored record needs its pre-existing episode")
        _require(record["episodes"][0]["role"] == "preexisting", "$.episodes[0].role", "first episode must be preexisting")
        return

    if primary == "torus_branch_ambiguous":
        torus = _require_certificate(certs, "torus_log", primary)
        _require(not torus["unique"], "$.certificates.torus_log.unique", "ambiguous branch cannot have unique log")
        return

    if primary == "ambiguous_tie":
        _require(flags["root_coverage_complete"], "$.flags.root_coverage_complete", "ambiguous tie requires complete root coverage")
        _require(flags["ambiguous_tie"], "$.flags.ambiguous_tie", "ambiguous tie flag missing")
        _require(cluster is not None, "$.entry_cluster", "ambiguous tie needs candidate cluster")
        _require(not cluster["complete"], "$.entry_cluster.complete", "ambiguous tie is not an authoritative complete cluster")
        tie = _require_certificate(certs, "tie", primary)
        _require(tie["status"] == "ordering_ambiguous", "$.certificates.tie.status", "wrong tie certificate status")
        return

    if primary == "numerically_unresolved":
        _require(not flags["solver_complete"] or flags["entry_direction_inconsistent"], "$.flags.solver_complete", "unresolved primary needs an incomplete/contradictory solver state")
        _require_certificate(certs, "unresolved", primary)
        return

    if primary in ("no_entry_proved", "right_censored_no_entry"):
        _require(not flags["entry_observed"], "$.flags.entry_observed", "no-entry outcome cannot observe entry")
        _require(cluster is None, "$.entry_cluster", "no-entry outcome cannot have cluster")
        _require(flags["root_coverage_complete"], "$.flags.root_coverage_complete", "censoring/no-entry proof requires complete window coverage")
        no_entry = _require_certificate(certs, "no_entry", primary)
        _require(no_entry["complete"], "$.certificates.no_entry.complete", "no-entry certificate must be complete")
        if primary == "no_entry_proved":
            _require(observation["complete_time_domain"], "$.observation.complete_time_domain", "proved no-entry requires complete time domain")
            _require(flags["no_entry_complete_time_domain_certified"], "$.flags.no_entry_complete_time_domain_certified", "complete-domain flag missing")
            _require(
                no_entry["mode"] in ("exact_common_period", "global_lower_bound"),
                "$.certificates.no_entry.mode",
                "finite-window exclusion cannot prove no entry",
            )
            _require(not flags["right_censored"], "$.flags.right_censored", "proved no-entry is not censoring")
        else:
            _require(not observation["complete_time_domain"], "$.observation.complete_time_domain", "finite-window censoring cannot claim complete domain")
            _require(no_entry["mode"] == "finite_window", "$.certificates.no_entry.mode", "right censoring needs finite-window certificate")
            _require(flags["right_censored"], "$.flags.right_censored", "right-censor flag missing")
        return

    _require(flags["entry_observed"], "$.flags.entry_observed", "entry outcome requires observed entry")
    _require(cluster is not None, "$.entry_cluster", "entry outcome requires cluster")
    _require(flags["root_coverage_complete"], "$.flags.root_coverage_complete", "entry outcome requires complete root coverage")
    _require(flags["global_minimum_certified"], "$.flags.global_minimum_certified", "entry outcome requires global minimum proof")
    _require(flags["no_earlier_entry_certified"], "$.flags.no_earlier_entry_certified", "entry outcome requires no-earlier proof")

    if primary == "right_censored_active_episode":
        _require(flags["right_censored"], "$.flags.right_censored", "right-censor flag missing")
        _require(not flags["outer_exit_certified"], "$.flags.outer_exit_certified", "active censor cannot have exit")
        outer = _require_certificate(certs, "outer_exit", primary)
        _require(not outer["strict_overshoot"], "$.certificates.outer_exit.strict_overshoot", "active censor cannot certify overshoot")
        closest = _require_certificate(certs, "closest", primary)
        _require(closest["status"] == "window_only", "$.certificates.closest.status", "active censor has window-only minimum")
        return

    outer = _require_certificate(certs, "outer_exit", primary)
    _require(outer["strict_overshoot"], "$.certificates.outer_exit.strict_overshoot", "completed episode requires strict overshoot")
    _require(outer["rearmed"], "$.certificates.outer_exit.rearmed", "completed episode must re-arm")
    closest = _require_certificate(certs, "closest", primary)
    _require(closest["status"] == "episode_complete", "$.certificates.closest.status", "completed episode requires episode closest status")

    if primary == "tie_cluster":
        _require(cluster["complete"], "$.entry_cluster.complete", "tie cluster must be complete")
        _require(cluster["representation"] != "singleton", "$.entry_cluster.representation", "tie cluster cannot be singleton")
        tie = _require_certificate(certs, "tie", primary)
        _require(tie["status"] == "complete_cluster", "$.certificates.tie.status", "tie cluster needs complete-cluster certificate")
    elif primary == "degenerate_spatial_minimum":
        _require(cluster["representation"] == "singleton", "$.entry_cluster.representation", "degenerate primary requires singleton")
        _require(flags["entry_has_spatial_degeneracy"], "$.flags.entry_has_spatial_degeneracy", "degenerate flag missing")
    elif primary == "grazing_entry":
        _require(cluster["representation"] == "singleton", "$.entry_cluster.representation", "grazing primary requires singleton")
        _require(flags["entry_has_grazing"], "$.flags.entry_has_grazing", "grazing flag missing")
        _require(not flags["entry_has_spatial_degeneracy"], "$.flags.entry_has_spatial_degeneracy", "degeneracy has precedence over grazing")
    else:
        _require(cluster["representation"] == "singleton", "$.entry_cluster.representation", "regular primary requires singleton")
        _require(flags["entry_geometry_regular"], "$.flags.entry_geometry_regular", "regular geometry flag missing")
        _require(not flags["entry_has_grazing"], "$.flags.entry_has_grazing", "regular entry cannot graze")
        _require(not flags["entry_has_spatial_degeneracy"], "$.flags.entry_has_spatial_degeneracy", "regular entry cannot be degenerate")


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
            "physical_root_solver_run",
            "physical_outcome_mass_estimated",
            "rank_used_for_event_selection",
        },
        "$.scope",
    )
    for name in scope:
        _require_bool(scope[name], f"$.scope.{name}")
    _require(
        not scope["physical_root_solver_run"],
        "$.scope.physical_root_solver_run",
        "this reference artifact cannot claim a physical solver run",
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
    jacobian = zero_matrix(9, 3)
    jacobian[7][0] = 1.0
    if rank == 3:
        jacobian[6][1] = 1.0
    else:
        jacobian[7][1] = 1.0
    jacobian[8][2] = -2.0

    if rank is None:
        return {
            "coordinate_basis": "physical-length orthonormal target basis",
            "G": identity_matrix(9),
            "H": identity_matrix(3),
            "J": jacobian,
            "singular_value_intervals": [
                interval(2.0),
                interval(math.sqrt(2.0)),
                {"lo": 0.0, "hi": 1.0e-6},
            ],
            "rank": {
                "status": "unresolved",
                "exact_rank": None,
                "possible_ranks": list(possible_ranks),
                "proof_kind": "interval spans zero",
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
        "G": identity_matrix(9),
        "H": identity_matrix(3),
        "J": jacobian,
        "singular_value_intervals": singular_values,
        "rank": {
            "status": "certified",
            "exact_rank": rank,
            "possible_ranks": [rank],
            "proof_kind": "synthetic exact minor control",
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
    rank: int | None = 3,
    grazing: bool = False,
    degenerate: bool = False,
    time: float = 1.0,
) -> dict[str, Any]:
    jet = make_jet_normal(rank, longitudinal_phase=not grazing)
    hessian = (
        [[interval(1.0), interval(0.0)], [interval(0.0), interval(0.0)]]
        if degenerate
        else [[interval(1.0), interval(0.0)], [interval(0.0), interval(1.0)]]
    )
    return {
        "representative_id": representative_id,
        "box": {
            "sigma1": interval(0.25, 1.0e-12),
            "sigma2": interval(0.75, 1.0e-12),
            "time": interval(time, 1.0e-12),
        },
        "torus_image": [0] * 9,
        "log_unique": True,
        "s": copy.deepcopy(jet["s"]),
        "F": interval(
            0.5 * math.fsum(value * value for value in jet["s"]),
            1.0e-12,
        ),
        "grad_sigma": [interval(0.0, 1.0e-12), interval(0.0, 1.0e-12)],
        "dF_dt": interval(0.0) if grazing else interval(-1.0, 1.0e-12),
        "H_sigma_sigma": hessian,
        "jet_normal": jet,
    }


def make_cluster(
    representation: str = "singleton",
    *,
    complete: bool = True,
    rank: int | None = 3,
) -> dict[str, Any]:
    if representation == "singleton":
        return {
            "representation": "singleton",
            "complete": complete,
            "unordered": True,
            "cardinality": 1,
            "members": [make_representative("entry-0", rank=rank)],
            "implicit_set": None,
        }
    if representation == "finite":
        return {
            "representation": "finite",
            "complete": complete,
            "unordered": True,
            "cardinality": 2,
            "members": [
                make_representative(
                    "entry-a",
                    rank=rank,
                    grazing=True,
                    time=1.0,
                ),
                make_representative(
                    "entry-b",
                    rank=2,
                    grazing=True,
                    degenerate=True,
                    time=1.0,
                ),
            ],
            "implicit_set": None,
        }
    if representation == "implicit":
        return {
            "representation": "implicit",
            "complete": complete,
            "unordered": True,
            "cardinality": "continuum",
            "members": [],
            "implicit_set": {
                "defining_equations": [
                    "d_sigma1 F = 0",
                    "d_sigma2 F = 0",
                    "F-r_in^2/2 = 0",
                ],
                "domain_boxes": [
                    {
                        "sigma1": interval(0.0, 0.25),
                        "sigma2": interval(0.0, 0.25),
                        "time": interval(1.0, 1.0e-12),
                    }
                ],
                "dimension_status": "positive",
                "set_certificate_ref": "synthetic-positive-dimensional-set",
                "jet_field_certificate_ref": None,
                "normal_field_certificate_ref": None,
            },
        }
    raise ValueError(f"unknown cluster representation: {representation}")


def make_flags() -> dict[str, bool]:
    flags = {name: False for name in FLAG_NAMES}
    flags.update(
        {
            "source_valid": True,
            "history_valid": True,
            "initial_armed": True,
            "torus_log_unique": True,
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


def complete_coverage_certificate() -> dict[str, Any]:
    return {
        "certificate_id": "coverage",
        "complete": True,
        "coverage_tree_hash": "1" * 64,
        "deterministic_budget_hash": "2" * 64,
        "leaf_counts": {
            "excluded": 8,
            "unique_root": 1,
            "singular_cluster": 0,
            "unresolved": 0,
        },
    }


def incomplete_coverage_certificate() -> dict[str, Any]:
    return {
        "certificate_id": "coverage-partial",
        "complete": False,
        "coverage_tree_hash": "3" * 64,
        "deterministic_budget_hash": "2" * 64,
        "leaf_counts": {
            "excluded": 7,
            "unique_root": 1,
            "singular_cluster": 0,
            "unresolved": 1,
        },
    }


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
        "T_in": None if left_censored else interval(1.0, 1.0e-12),
        "T_out": interval(2.0, 1.0e-12) if complete else None,
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
            "physical_root_solver_run": False,
            "physical_outcome_mass_estimated": False,
            "rank_used_for_event_selection": False,
        },
    }


def _configure_entry_certificates(
    record: dict[str, Any], *, complete_episode: bool
) -> None:
    flags = record["flags"]
    certs = record["certificates"]
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
    certs["root_coverage"] = complete_coverage_certificate()
    certs["global_minimum"] = {
        "certificate_id": "global-minimum",
        "complete": True,
    }
    certs["no_earlier_entry"] = {
        "certificate_id": "no-earlier-entry",
        "complete": True,
    }
    certs["torus_log"] = {
        "certificate_id": "torus-log",
        "unique": True,
        "image_manifest_hash": "6" * 64,
    }
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
            "strict_overshoot": True,
            "boundary_time": interval(2.0, 1.0e-12),
            "rearmed": True,
        }
        certs["closest"] = {
            "certificate_id": "closest",
            "status": "episode_complete",
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
        record["source"]["source_valid"] = False
        record["source"]["invalid_reasons"] = ["graph_bound_exceeded"]
        flags["source_valid"] = False
        certs["source_validity"]["status"] = "invalid"
        certs["source_validity"]["reason_codes"] = ["graph_bound_exceeded"]
        record["observation"]["continuation_state"] = "invalid"

    elif primary == "left_censored_active_episode":
        record["source"]["initial_state"] = "active"
        flags["initial_armed"] = False
        flags["left_censored"] = True
        flags["right_censored"] = True
        flags["closest_window_only"] = True
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
        flags["torus_log_unique"] = False
        flags["torus_branch_ambiguous"] = True
        certs["torus_log"] = {
            "certificate_id": "torus-ambiguity",
            "unique": False,
            "image_manifest_hash": "6" * 64,
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary == "ambiguous_tie":
        flags.update(
            {
                "ambiguous_tie": True,
                "root_coverage_complete": True,
                "entry_observed": True,
                "entry_tied": True,
                "rank_marks_complete": True,
                "normal_marks_complete": True,
            }
        )
        record["entry_cluster"] = make_cluster("finite", complete=False)
        certs["root_coverage"] = complete_coverage_certificate()
        certs["tie"] = {
            "certificate_id": "tie-order",
            "status": "ordering_ambiguous",
            "candidate_ids": ["entry-a", "entry-b"],
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary == "numerically_unresolved":
        flags.update(
            {
                "entry_observed": True,
                "entry_cluster_complete": True,
            }
        )
        record["entry_cluster"] = make_cluster("singleton", rank=None)
        flags["rank_marks_complete"] = False
        flags["normal_marks_complete"] = False
        certs["root_coverage"] = incomplete_coverage_certificate()
        certs["unresolved"] = {
            "certificate_id": "unresolved",
            "reason_codes": ["possible_earlier_root_box"],
            "unresolved_leaf_count": 1,
        }
        record["observation"]["continuation_state"] = "unresolved"

    elif primary in ("no_entry_proved", "right_censored_no_entry"):
        flags.update(
            {
                "solver_complete": True,
                "root_coverage_complete": True,
                "no_entry_window_certified": True,
            }
        )
        certs["root_coverage"] = complete_coverage_certificate()
        if primary == "no_entry_proved":
            flags["no_entry_complete_time_domain_certified"] = True
            record["observation"]["complete_time_domain"] = True
            record["observation"]["continuation_state"] = "terminal"
            certs["no_entry"] = {
                "certificate_id": "no-entry-period",
                "mode": "exact_common_period",
                "complete": True,
                "period": interval(4.0),
            }
        else:
            flags["right_censored"] = True
            record["observation"]["continuation_state"] = "armed"
            certs["no_entry"] = {
                "certificate_id": "no-entry-window",
                "mode": "finite_window",
                "complete": True,
                "period": None,
            }

    elif primary == "right_censored_active_episode":
        _configure_entry_certificates(record, complete_episode=False)
        record["entry_cluster"] = make_cluster("singleton")
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
        certs["outer_exit"] = {
            "certificate_id": "outer-window",
            "observed": False,
            "strict_overshoot": False,
            "boundary_time": None,
            "rearmed": False,
        }
        certs["closest"] = {
            "certificate_id": "closest-window",
            "status": "window_only",
        }
        record["episodes"] = [
            make_episode(right_censored=True, complete=False)
        ]
        record["observation"]["continuation_state"] = "active"

    else:
        _configure_entry_certificates(record, complete_episode=True)
        if primary == "tie_cluster":
            record["entry_cluster"] = make_cluster("finite")
            flags.update(
                {
                    "entry_tied": True,
                    "entry_has_grazing": True,
                    "entry_has_spatial_degeneracy": True,
                    "rank_marks_complete": True,
                    "normal_marks_complete": True,
                }
            )
            certs["tie"] = {
                "certificate_id": "tie-complete",
                "status": "complete_cluster",
                "candidate_ids": ["entry-a", "entry-b"],
            }
        else:
            rank = 2 if primary == "degenerate_spatial_minimum" else 3
            representative = make_representative(
                "entry-0",
                rank=rank,
                grazing=primary
                in (
                    "grazing_entry",
                    "degenerate_spatial_minimum",
                ),
                degenerate=primary == "degenerate_spatial_minimum",
            )
            record["entry_cluster"] = {
                "representation": "singleton",
                "complete": True,
                "unordered": True,
                "cardinality": 1,
                "members": [representative],
                "implicit_set": None,
            }
            flags["rank_marks_complete"] = True
            flags["normal_marks_complete"] = True
            if primary == "degenerate_spatial_minimum":
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
    validate_record(record)
    return record


def build_implicit_cluster_record() -> dict[str, Any]:
    record = build_hostile_record("tie_cluster")
    record["sample_id"] = "hostile-positive-dimensional-tie"
    record["entry_cluster"] = make_cluster("implicit")
    record["flags"]["entry_positive_dimensional"] = True
    record["flags"]["rank_marks_complete"] = False
    record["flags"]["normal_marks_complete"] = False
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


def build_control_report(schema_path: Path) -> dict[str, Any]:
    schema = strict_load_json(schema_path)
    validate_schema_document(schema)
    fixtures = {
        primary: build_hostile_record(primary)
        for primary in PRIMARY_PRECEDENCE
    }
    implicit = build_implicit_cluster_record()
    tangent_trace = hysteresis_trace(
        (2.5, 1.5, 1.0, 1.4, 2.0, 1.5, 1.0, 2.1, 1.0),
        r_in=1.0,
        r_out=2.0,
    )
    transition_names = [
        row["transition"] for row in tangent_trace["transitions"]
    ]
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
