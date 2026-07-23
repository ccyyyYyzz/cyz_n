#!/usr/bin/env python3
"""Generator-side primitives for the fixed Brief 0015 certificate contract."""
from __future__ import annotations

import hashlib
import itertools
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


ARTIFACT_SCHEMA = "cyz-0015-kernel-artifact-v3"
GENERATOR_API = "cyz-0015-generator-v3"
SPEC_SCHEMA = "cyz-0015-constructor-v3"
MANIFEST_SCHEMA = "cyz-0015-control-manifest-v2"
INTERPRETATION_MODE = "fixed_registered_contract_not_general_dsl"

REGISTERED_SPEC_SHA256 = (
    "5a935b5e0cc415d73a783cb6e6d926a355f2c43d662fa94aed93e0a8f9a5af01"
)
REGISTERED_SEMANTIC_CONTRACT_SHA256 = (
    "38bb37210c33ae56944688607891b3fb99b89e4af48a159f419f9d96beb8c282"
)
REGISTERED_MANIFEST_SHA256 = (
    "14d9162a69137e85369bca24081f07e48df10b33f1bac83c45d9122e629b86bd"
)

REGISTERED_DEPENDENCIES = (
    "artifacts/0015/generate_0015.py",
    "artifacts/0015/generator_core.py",
    "artifacts/0015/generator_model.py",
    "artifacts/0015/generator_artifact.py",
    "artifacts/0015/verify_0015.py",
    "artifacts/0015/verifier_core.py",
    "artifacts/0015/verifier_model.py",
    "artifacts/0015/verifier_semantics.py",
    "artifacts/0015/verifier_replay.py",
    "artifacts/0015/verifier_replay_runtime.py",
    "artifacts/0015/verifier_hostile.py",
)

REGISTERED_INPUT_TYPES = {
    "amplitude_status": "enum[valid,unresolved]",
    "coupling": "nonnegative_fraction",
    "coupling_max": "nonnegative_fraction",
    "dilute_flag": "bool",
    "frame_arity": "integer[2,4]",
    "metric_radii": "tuple[9,positive_fraction]",
    "proposed_reverse_ratio": "fraction[0,1]",
    "relative_speed": "positive_fraction",
    "self_dual_radius": "positive_fraction",
    "separation_fraction": "positive_fraction",
    "source_registry_id": "enum[gkm_sparse_v1]",
    "speed_max": "positive_fraction",
    "speed_min": "positive_fraction",
}
REGISTERED_FORBIDDEN_INPUT_FIELDS = [
    "rank",
    "target_rank",
    "visible_count",
    "active_mask",
    "response_cell",
    "pole_band",
    "dimension_label",
    "large_direction_count",
    "instance_label_branch",
]

REGISTERED_CONTROL_ROLES = {
    "ordinary_full_t9",
    "three_large_metric_control",
    "four_large_metric_control",
    "velocity_invalid",
    "coupling_dilution_invalid",
    "geometry_invalid",
    "unresolved_amplitude",
    "arity_two_semantic_control",
    "arity_four_semantic_control",
    "closed_lower_speed_boundary",
    "precedence_probe",
}

ROLE_OBLIGATIONS = {
    "ordinary_full_t9": {
        "calibration_times": ["2/1", "4/1", "6/1", "8/1", "10/1"],
        "expected_valid_frames": 504,
    },
    "three_large_metric_control": {"expected_valid_frames": 6},
    "four_large_metric_control": {"expected_valid_frames": 24},
    "velocity_invalid": {"expected_uniform_source_case": "velocity"},
    "coupling_dilution_invalid": {
        "expected_uniform_source_case": "coupling_dilution"
    },
    "geometry_invalid": {"expected_uniform_source_case": "geometry"},
    "unresolved_amplitude": {
        "expected_uniform_source_case": "unresolved_amplitude"
    },
    "arity_two_semantic_control": {
        "expected_frame_arity": 2,
        "expected_valid_frames": 2,
    },
    "arity_four_semantic_control": {
        "expected_frame_arity": 4,
        "expected_valid_frames": 24,
    },
    "closed_lower_speed_boundary": {
        "expected_interval_boundary_valid": True,
        "expected_valid_frames": 504,
    },
    "precedence_probe": {
        "expected_uniform_source_case": "unresolved_amplitude"
    },
}

REGISTERED_SEMANTIC_COMPONENTS = (
    "process_type",
    "ctmc_export",
    "classification",
    "direction_set",
    "frame_prior",
    "alphabets",
    "input_schema",
    "validity",
    "mark_rule",
    "probability_registry",
    "state_rule",
    "schedule_rule",
    "channel_rule",
    "probability_composition",
    "destination_rule",
    "history_rule",
    "reverse_rule",
    "ledger_rule",
    "initial_law",
    "interpretation_mode",
    "s9",
    "type_system",
    "id_schemas",
    "record_schemas",
    "ordering_rules",
    "constitutive_rules",
    "parameter_influence",
    "constructor_program",
    "operation_schemas",
    "forbidden_capabilities",
)


class ConstructionError(RuntimeError):
    """A registered-contract, input, or generation failure."""


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value)
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+/[1-9]\d*", value):
        raise ConstructionError(f"invalid exact fraction {value!r}")
    fraction = Fraction(*(int(part) for part in value.split("/")))
    if f"{fraction.numerator}/{fraction.denominator}" != value:
        raise ConstructionError(f"noncanonical exact fraction {value}")
    return fraction


def frac(value: Any) -> str:
    fraction = Fraction(value)
    return f"{fraction.numerator}/{fraction.denominator}"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=str(destination.parent),
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(canonical_bytes(value) + b"\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def normalized_lf_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def normalized_lf_sha(path: Path) -> str:
    return hashlib.sha256(normalized_lf_bytes(path)).hexdigest()


def get_path(value: Mapping[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise ConstructionError(f"missing specification path {path}")
        current = current[part]
    return current


def semantic_contract_payload(spec: Mapping[str, Any]) -> dict[str, Any]:
    paths = spec.get("semantic_contract_components")
    if paths != list(REGISTERED_SEMANTIC_COMPONENTS):
        raise ConstructionError("semantic contract component registry mismatch")
    return {path: get_path(spec, path) for path in paths}


def semantic_contract_sha(spec: Mapping[str, Any]) -> str:
    return canonical_sha(semantic_contract_payload(spec))


def registered_repo_root(entrypoint: Path, requested_root: Path | None = None) -> Path:
    root = entrypoint.resolve().parents[2]
    if requested_root is not None and requested_root.resolve() != root:
        raise ConstructionError(
            "dependency root must equal the repository containing the executing launcher"
        )
    return root


def dependency_path(root: Path, relative: str) -> Path:
    if (
        not isinstance(relative, str)
        or "\\" in relative
        or not relative
        or PurePosixPath(relative).is_absolute()
        or any(part in {"", ".", ".."} for part in PurePosixPath(relative).parts)
        or any(":" in part for part in PurePosixPath(relative).parts)
        or PurePosixPath(relative).as_posix() != relative
    ):
        raise ConstructionError(f"unsafe executable dependency path {relative!r}")
    resolved_root = root.resolve()
    lexical = resolved_root / Path(*PurePosixPath(relative).parts)
    if lexical.is_symlink():
        raise ConstructionError(
            f"executable dependency may not be a symlink: {relative}"
        )
    resolved = lexical.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ConstructionError(
            f"executable dependency escapes repository root: {relative}"
        ) from exc
    if not resolved.is_file():
        raise ConstructionError(f"missing executable dependency {relative}")
    return resolved


def validate_dependency_declaration(spec: Mapping[str, Any]) -> None:
    dependencies = spec.get("executable_dependencies")
    if dependencies != list(REGISTERED_DEPENDENCIES):
        raise ConstructionError("registered executable dependency set/order mismatch")
    if len(dependencies) != len(set(dependencies)):
        raise ConstructionError("duplicate executable dependency")


def dependency_inventory(
    spec: Mapping[str, Any], root: Path
) -> list[dict[str, str]]:
    validate_dependency_declaration(spec)
    return [
        {
            "path": relative,
            "normalized_lf_sha256": normalized_lf_sha(
                dependency_path(root, relative)
            ),
        }
        for relative in REGISTERED_DEPENDENCIES
    ]


def validate_registered_python_surface(root: Path) -> None:
    directory = dependency_path(
        root, "artifacts/0015/generator_core.py"
    ).parent
    observed = {
        path.relative_to(root.resolve()).as_posix()
        for path in directory.glob("*.py")
        if path.is_file()
    }
    expected = set(REGISTERED_DEPENDENCIES)
    if observed != expected:
        raise ConstructionError(
            "registered Python surface mismatch "
            f"extra={sorted(observed - expected)} "
            f"missing={sorted(expected - observed)}"
        )


def assert_loaded_source(
    root: Path, relative: str, observed_file: str | Path | None
) -> None:
    if observed_file is None:
        raise ConstructionError(f"loaded module has no __file__: {relative}")
    expected = dependency_path(root, relative)
    if Path(observed_file).resolve() != expected:
        raise ConstructionError(
            f"executed source differs from registered dependency: {relative}"
        )


def _validate_record_schemas(spec: Mapping[str, Any]) -> None:
    allowed = {
        "string",
        "integer",
        "boolean",
        "fraction",
        "direction",
        "nullable_direction",
        "nullable_string",
        "nullable_integer",
        "nullable_fraction",
        "array",
        "nullable_array_direction",
        "enum",
        "nullable_enum",
        "record",
    }
    schemas = spec.get("record_schemas")
    if not isinstance(schemas, Mapping) or not schemas:
        raise ConstructionError("record_schemas missing")
    for name, schema in schemas.items():
        if (
            set(schema) != {"additional_fields", "field_order", "fields"}
            or schema["additional_fields"] is not False
        ):
            raise ConstructionError(f"record schema {name} not closed")
        if (
            set(schema["field_order"]) != set(schema["fields"])
            or len(schema["field_order"]) != len(schema["fields"])
        ):
            raise ConstructionError(f"record schema {name} field_order incomplete")
        for field, descriptor in schema["fields"].items():
            if (
                not isinstance(descriptor, Mapping)
                or descriptor.get("type") not in allowed
            ):
                raise ConstructionError(f"invalid type for {name}.{field}")
            if descriptor["type"] in {"enum", "nullable_enum"} and not isinstance(
                get_path(spec, descriptor["path"]), list
            ):
                raise ConstructionError(f"bad enum path {name}.{field}")
            if (
                descriptor["type"] == "record"
                and descriptor.get("schema") not in schemas
            ):
                raise ConstructionError(f"bad nested schema {name}.{field}")


def validate_spec(spec: Mapping[str, Any]) -> None:
    exact_top = {
        "schema_version",
        "semantic_contract_version",
        "semantic_contract_components",
        "interpretation_mode",
        "process_type",
        "ctmc_export",
        "classification",
        "direction_set",
        "frame_prior",
        "alphabets",
        "input_schema",
        "validity",
        "mark_rule",
        "probability_registry",
        "state_rule",
        "schedule_rule",
        "channel_rule",
        "probability_composition",
        "destination_rule",
        "history_rule",
        "reverse_rule",
        "ledger_rule",
        "initial_law",
        "s9",
        "forbidden_capabilities",
        "executable_dependencies",
        "type_system",
        "id_schemas",
        "record_schemas",
        "ordering_rules",
        "constitutive_rules",
        "parameter_influence",
        "operation_schemas",
        "constructor_program",
    }
    if set(spec) != exact_top:
        raise ConstructionError(
            f"spec keys mismatch extra={sorted(set(spec)-exact_top)} "
            f"missing={sorted(exact_top-set(spec))}"
        )
    if spec["schema_version"] != SPEC_SCHEMA:
        raise ConstructionError("unsupported constructor schema")
    if (
        spec["semantic_contract_version"]
        != "cyz-0015-fixed-registered-contract-v3"
        or spec["interpretation_mode"] != INTERPRETATION_MODE
    ):
        raise ConstructionError("fixed registered interpretation boundary absent")
    if canonical_sha(spec) != REGISTERED_SPEC_SHA256:
        raise ConstructionError("registered constructor specification hash mismatch")
    if semantic_contract_sha(spec) != REGISTERED_SEMANTIC_CONTRACT_SHA256:
        raise ConstructionError("registered semantic contract hash mismatch")

    validate_dependency_declaration(spec)
    if spec["semantic_contract_components"] != list(
        REGISTERED_SEMANTIC_COMPONENTS
    ):
        raise ConstructionError("semantic contract component registry mismatch")
    if spec["input_schema"] != {
        "allowed_fields": REGISTERED_INPUT_TYPES,
        "forbidden_fields": REGISTERED_FORBIDDEN_INPUT_FIELDS,
    }:
        raise ConstructionError("registered input type schema mismatch")
    if spec["process_type"] != "scheduled_markov_renewal":
        raise ConstructionError("process type is not scheduled Markov-renewal")
    if spec["ctmc_export"] != "forbidden":
        raise ConstructionError("CTMC export boundary violated")
    if spec["direction_set"] != list(range(9)):
        raise ConstructionError("direction_set must be anonymous 0..8")

    prior = spec["frame_prior"]
    if (
        prior["status"] != "proposed_microscopic_closure_parameter"
        or prior["enumeration"] != "ordered_distinct_roles"
        or prior["arity_input"] != "frame_arity"
        or prior["minimum_arity"] != 2
        or prior["maximum_arity"] != 4
        or prior["velocity_role_index"] != 1
    ):
        raise ConstructionError("registered frame prior contract mismatch")

    if spec["reverse_rule"]["claim"] != "proposed_reverse_ratio_not_detailed_balance":
        raise ConstructionError("unsupported detailed-balance claim")
    if spec["s9"]["adjacent_generators"] != [
        {"id": f"s{index}", "swap": [index, index + 1]} for index in range(8)
    ]:
        raise ConstructionError("S9 generator list invalid")
    if spec["s9"]["metric_and_kernel_transform_together"] is not True:
        raise ConstructionError("S9 metric/kernel joint action disabled")
    if (
        spec["mark_rule"]["include_central"] is not True
        or spec["mark_rule"]["signed_basis_marks"] is not True
        or spec["mark_rule"]["probability"] != "uniform_over_frame_local_marks"
    ):
        raise ConstructionError("registered mark rule mismatch")

    registry = spec["probability_registry"]["gkm_sparse_v1"]
    expected_registry_keys = {
        "central_ann_probability",
        "central_b2",
        "claim",
        "shell_ann_probability",
        "shell_b2",
        "shell_outward_interval",
        "unsupported_b2",
    }
    if set(registry) != expected_registry_keys:
        raise ConstructionError("probability registry schema mismatch")
    central_probability = parse_fraction(registry["central_ann_probability"])
    shell_probability = parse_fraction(registry["shell_ann_probability"])
    if not 0 <= central_probability <= 1 or not 0 <= shell_probability <= 1:
        raise ConstructionError("registered probability outside [0,1]")
    lower, upper = map(parse_fraction, registry["shell_outward_interval"])
    if not lower < shell_probability < upper:
        raise ConstructionError("shell probability outside registered interval")

    charge = spec["state_rule"]["global_charge_default"]
    if (
        not isinstance(charge, list)
        or len(charge) != 9
        or any(type(component) is not int for component in charge)
    ):
        raise ConstructionError("global charge basis must be an integer 9-vector")

    schedule = spec["schedule_rule"]
    phase_count = schedule["phase_count"]
    if (
        type(phase_count) is not int
        or phase_count <= 0
        or type(schedule["initial_countdown_phase"]) is not int
        or type(schedule["event_at_phase"]) is not int
        or not (
            0
            <= schedule["initial_countdown_phase"]
            < schedule["event_at_phase"]
            <= phase_count
        )
    ):
        raise ConstructionError("countdown phase contract invalid")

    _validate_record_schemas(spec)
    expected_id_schemas = {
        "frame_id": {
            "kind": "prefixed_join",
            "prefix": "f",
            "separator": "_",
            "components": "frame.axes",
        },
        "frame_mark_id": {
            "kind": "format",
            "template": "{frame_id}|M|{mark_template}",
            "components": ["frame_id", "mark_template"],
        },
        "cemetery_mark_id": {
            "kind": "format",
            "template": "CEM|{reason}",
            "components": ["reason"],
        },
        "present_state_id": {
            "kind": "format",
            "template": "{frame_id}|P|{history}",
            "components": ["frame_id", "history"],
        },
        "products_state_id": {
            "kind": "format",
            "template": "{frame_id}|A|{history}|{mark_template}",
            "components": ["frame_id", "history", "mark_template"],
        },
        "killed_state_id": {
            "kind": "format",
            "template": "{frame_id}|K|{history}|{reason}",
            "components": ["frame_id", "history", "reason"],
        },
        "catalog_killed_state_id": {
            "kind": "format",
            "template": "KC|{reason}",
            "components": ["reason"],
        },
        "event_id": {
            "kind": "format",
            "template": "{source_state_id}|E|{channel_id}|{mark_id}",
            "components": ["source_state_id", "channel_id", "mark_id"],
        },
    }
    if spec["id_schemas"] != expected_id_schemas:
        raise ConstructionError("ID grammar differs from registered contract")

    expected_operations = [
        "enumerate_ordered_distinct_frames",
        "construct_frame_local_marks",
        "evaluate_source_validity",
        "materialize_registered_marks",
        "construct_physical_and_killed_states",
        "construct_deterministic_schedules",
        "construct_complete_event_rows",
        "construct_exchangeable_initial_law",
        "construct_adjacent_s9_actions",
    ]
    if [node.get("op") for node in spec["constructor_program"]] != expected_operations:
        raise ConstructionError("registered constructor stage order mismatch")
    if set(spec["operation_schemas"]) != set(expected_operations):
        raise ConstructionError("registered operation schema set mismatch")

    seen: set[str] = set()
    valid_sources = set(REGISTERED_INPUT_TYPES) | {
        "direction_set",
        "histories",
        "cemetery_reasons",
        "adjacent_generators",
    }
    for node in spec["constructor_program"]:
        if set(node) != {"id", "op", "inputs", "params"} or node["id"] in seen:
            raise ConstructionError("constructor node schema or identity invalid")
        for name in node["inputs"]:
            if name not in valid_sources and name not in seen:
                raise ConstructionError(
                    f"unregistered or non-topological constructor input: {name}"
                )
        seen.add(node["id"])
        valid_sources.add(node["id"])
        operation = node["op"]
        schema = spec["operation_schemas"][operation]
        if set(schema) != {"inputs", "output", "semantic_dependencies", "params"}:
            raise ConstructionError(f"operation {operation} contract not closed")
        if [item.get("name") for item in schema["inputs"]] != node["inputs"]:
            raise ConstructionError(f"operation {operation} input binding mismatch")
        if any(
            set(item) != {"name", "type"} or not item["type"]
            for item in schema["inputs"]
        ):
            raise ConstructionError(f"operation {operation} inputs not fully typed")
        if set(schema["output"]) != {
            "container",
            "record_schema",
            "ordering_rule",
            "id_schema",
        }:
            raise ConstructionError(f"operation {operation} output not typed")
        if (
            set(schema["params"])
            != {
                "contract_id",
                "record_schema",
                "ordering_rule",
                "semantic_rule",
                "id_schema",
            }
            or node["params"] != schema["params"]
        ):
            raise ConstructionError(f"operation {operation} params unbound")
        if schema["params"]["semantic_rule"] not in spec["constitutive_rules"]:
            raise ConstructionError(f"operation {operation} semantic rule absent")
        if schema["output"]["ordering_rule"] not in spec["ordering_rules"]:
            raise ConstructionError(f"operation {operation} ordering absent")
        for dependency in schema["semantic_dependencies"]:
            get_path(spec, dependency)

    semantic_contract_payload(spec)


def _require_fraction_string(field: str, value: Any) -> Fraction:
    if not isinstance(value, str):
        raise ConstructionError(f"{field} must be a canonical fraction string")
    return parse_fraction(value)


def _validate_typed_value(field: str, descriptor: str, value: Any) -> None:
    if descriptor == "bool":
        if type(value) is not bool:
            raise ConstructionError(f"{field} must be boolean")
        return
    integer_match = re.fullmatch(r"integer\[(-?\d+),(-?\d+)\]", descriptor)
    if integer_match:
        lower, upper = map(int, integer_match.groups())
        if type(value) is not int or not lower <= value <= upper:
            raise ConstructionError(f"{field} must be an integer in [{lower},{upper}]")
        return
    enum_match = re.fullmatch(r"enum\[(.+)\]", descriptor)
    if enum_match:
        allowed = enum_match.group(1).split(",")
        if not isinstance(value, str) or value not in allowed:
            raise ConstructionError(f"{field} must be one of {allowed}")
        return
    tuple_match = re.fullmatch(r"tuple\[(\d+),(.+)\]", descriptor)
    if tuple_match:
        length = int(tuple_match.group(1))
        item_descriptor = tuple_match.group(2)
        if not isinstance(value, list) or len(value) != length:
            raise ConstructionError(f"{field} must contain exactly {length} items")
        for index, item in enumerate(value):
            _validate_typed_value(f"{field}[{index}]", item_descriptor, item)
        return
    if descriptor in {
        "fraction",
        "positive_fraction",
        "nonnegative_fraction",
        "fraction[0,1]",
    }:
        parsed = _require_fraction_string(field, value)
        if descriptor == "positive_fraction" and parsed <= 0:
            raise ConstructionError(f"{field} must be positive")
        if descriptor == "nonnegative_fraction" and parsed < 0:
            raise ConstructionError(f"{field} must be nonnegative")
        if descriptor == "fraction[0,1]" and not 0 <= parsed <= 1:
            raise ConstructionError(f"{field} must lie in [0,1]")
        return
    raise ConstructionError(f"unsupported registered type descriptor {descriptor}")


def validate_input(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> None:
    fields = spec["input_schema"]["allowed_fields"]
    if fields != REGISTERED_INPUT_TYPES:
        raise ConstructionError("registered input type schema mismatch")
    if set(vector) != set(fields):
        raise ConstructionError("control input fields mismatch registered schema")
    for field, descriptor in fields.items():
        _validate_typed_value(field, descriptor, vector[field])
    if parse_fraction(vector["speed_min"]) >= parse_fraction(vector["speed_max"]):
        raise ConstructionError("speed_min must be strictly less than speed_max")


def validate_manifest(
    spec: Mapping[str, Any], manifest: Mapping[str, Any]
) -> None:
    exact = {
        "schema_version",
        "constructor_spec_sha256",
        "constructor_reads_only",
        "controls",
        "opaque_id_renaming_control",
        "report_metadata_policy",
    }
    if set(manifest) != exact:
        raise ConstructionError("control manifest schema not closed")
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        raise ConstructionError("unsupported control manifest schema")
    if manifest["constructor_spec_sha256"] != REGISTERED_SPEC_SHA256:
        raise ConstructionError("control manifest does not bind registered spec")
    if canonical_sha(manifest) != REGISTERED_MANIFEST_SHA256:
        raise ConstructionError("registered control manifest hash mismatch")
    if (
        manifest["constructor_reads_only"]
        != "opaque_id_and_input; report_metadata_is_not_constructor_input"
        or manifest["report_metadata_policy"]
        != "human_label is a fixed verifier-suite role and is never passed to constructor stages"
    ):
        raise ConstructionError("constructor/report metadata boundary mismatch")

    controls = manifest["controls"]
    if not isinstance(controls, list) or len(controls) != len(
        REGISTERED_CONTROL_ROLES
    ):
        raise ConstructionError("registered control suite is incomplete")
    ids: set[str] = set()
    roles: set[str] = set()
    for control in controls:
        if set(control) != {"opaque_id", "input", "obligations", "report_metadata"}:
            raise ConstructionError("control record schema not closed")
        opaque_id = control["opaque_id"]
        if not isinstance(opaque_id, str) or not opaque_id or opaque_id in ids:
            raise ConstructionError("control opaque IDs must be nonempty and unique")
        ids.add(opaque_id)
        metadata = control["report_metadata"]
        if set(metadata) != {"human_label"}:
            raise ConstructionError("control report metadata schema not closed")
        role = metadata["human_label"]
        if role not in REGISTERED_CONTROL_ROLES or role in roles:
            raise ConstructionError("control role set is incomplete or duplicated")
        roles.add(role)
        if control["obligations"] != ROLE_OBLIGATIONS[role]:
            raise ConstructionError(f"control obligations mismatch role {role}")
        validate_input(spec, control["input"])
    if roles != REGISTERED_CONTROL_ROLES:
        raise ConstructionError("registered control roles incomplete")

    rename = manifest["opaque_id_renaming_control"]
    if set(rename) != {"source_opaque_id", "renamed_opaque_id", "expected"}:
        raise ConstructionError("opaque-ID renaming control schema not closed")
    if (
        rename["source_opaque_id"] not in ids
        or not isinstance(rename["renamed_opaque_id"], str)
        or not rename["renamed_opaque_id"]
        or rename["renamed_opaque_id"] in ids
        or rename["expected"] != "expanded_kernel_isomorphic"
    ):
        raise ConstructionError("opaque-ID renaming control is invalid")
    source_control = next(
        control
        for control in controls
        if control["opaque_id"] == rename["source_opaque_id"]
    )
    if (
        source_control["report_metadata"]["human_label"]
        != "three_large_metric_control"
        or "three" not in rename["renamed_opaque_id"].lower()
    ):
        raise ConstructionError(
            "opaque-ID renaming probe is not bound to the registered "
            "three-large control"
        )


def interval_contains(
    value: Fraction,
    lower: Fraction,
    upper: Fraction,
    lower_kind: str,
    upper_kind: str,
) -> bool:
    return (value >= lower if lower_kind == "closed" else value > lower) and (
        value <= upper if upper_kind == "closed" else value < upper
    )


def frame_id(axes: Sequence[int]) -> str:
    return "f" + "_".join(map(str, axes))


def mark_template(axis: int | None, sign: int) -> str:
    return (
        "central"
        if axis is None
        else f"axis_{axis}_{'plus' if sign > 0 else 'minus'}"
    )


def reverse_template(template: str) -> str:
    if template == "central":
        return template
    if template.endswith("_plus"):
        return template[:-5] + "_minus"
    if template.endswith("_minus"):
        return template[:-6] + "_plus"
    raise ConstructionError(f"bad mark template {template}")


def mark_id(frame: str, template: str) -> str:
    return f"{frame}|M|{template}"


def cemetery_mark_id(reason: str) -> str:
    return f"CEM|{reason}"


def present_id(frame: str, history: str) -> str:
    return f"{frame}|P|{history}"


def products_id(frame: str, history: str, template: str) -> str:
    return f"{frame}|A|{history}|{template}"


def killed_id(frame: str, history: str, reason: str) -> str:
    return f"{frame}|K|{history}|{reason}"


def catalog_killed_id(reason: str) -> str:
    return f"KC|{reason}"


def event_id(source: str, channel: str, mark: str) -> str:
    return f"{source}|E|{channel}|{mark}"


def zero_charge(spec: Mapping[str, Any]) -> list[int]:
    return list(spec["state_rule"]["global_charge_default"])


def physical_projection(
    spec: Mapping[str, Any], kind: str, axes: Sequence[int] | None
) -> dict[str, Any]:
    source = spec["state_rule"][
        "present_physical" if kind == "P" else "products_physical"
    ]
    return {
        "pair_present": source["pair_present"],
        "system_energy": source["system_energy"],
        "reservoir_energy": source["reservoir_energy"],
        "work_energy": source["work_energy"],
        "global_charge_vector": zero_charge(spec),
        "frame": list(axes) if axes is not None else None,
    }


def parse_metric_csv(text: str) -> list[str]:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 9 or any(not part for part in parts):
        raise ConstructionError("--metric-radii requires nine nonempty positions")
    for index, part in enumerate(parts):
        if parse_fraction(part) <= 0:
            raise ConstructionError(f"--metric-radii position {index} must be positive")
    return parts
