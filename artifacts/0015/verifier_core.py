#!/usr/bin/env python3
"""Independent primitives for the fixed Brief 0015 verifier contract.

The verifier imports no generator module.  The serialized constructor is
accepted only at the registered canonical digests below; this module does not
claim to implement a general constructor DSL.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence


ARTIFACT_SCHEMA = "cyz-0015-kernel-artifact-v3"
EXPECTED_GENERATOR_API = "cyz-0015-generator-v3"
SPEC_SCHEMA = "cyz-0015-constructor-v3"
MANIFEST_SCHEMA = "cyz-0015-control-manifest-v2"
INTERPRETATION_MODE = "fixed_registered_contract_not_general_dsl"
ACCEPTANCE_DOMAIN = "exact_registered_spec_and_manifest_digests_only"
SOURCE_BINDING_POLICY = (
    "executed_modules_must_resolve_to_registered_dependency_files"
)

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

REGISTERED_VERIFIER_DEPENDENCIES = (
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


class VerificationError(RuntimeError):
    """A localized fixed-contract verification failure."""

    def __init__(self, code: str, message: str, location: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.location = location

    def record(self) -> dict[str, str]:
        return {
            "code": self.code,
            "message": self.message,
            "location": self.location,
        }


def fail(code: str, message: str, location: str = "") -> None:
    raise VerificationError(code, message, location)


def parse_fraction(value: Any) -> Fraction:
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int) and not isinstance(value, bool):
        return Fraction(value)
    if not isinstance(value, str) or not re.fullmatch(r"-?\d+/[1-9]\d*", value):
        fail("fraction", f"invalid exact fraction {value!r}")
    parsed = Fraction(*(int(part) for part in value.split("/", 1)))
    if f"{parsed.numerator}/{parsed.denominator}" != value:
        fail("fraction", f"noncanonical exact fraction {value}")
    return parsed


def fraction_text(value: Any) -> str:
    parsed = Fraction(value)
    return f"{parsed.numerator}/{parsed.denominator}"


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def normalized_lf_bytes(path: Path) -> bytes:
    text = path.read_text(encoding="utf-8")
    return text.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


def normalized_lf_sha256(path: Path) -> str:
    return hashlib.sha256(normalized_lf_bytes(path)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail("json_load", f"cannot load {path}: {exc}", str(path))


def write_canonical_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value) + b"\n")


def write_canonical_json_atomic(path: Path, value: Any) -> None:
    """Atomically publish canonical JSON within the destination directory."""
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


def get_path(value: Mapping[str, Any], path: str) -> Any:
    current: Any = value
    for part in path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            fail(
                "spec_missing_path",
                f"missing constructor specification path {path}",
                path,
            )
        current = current[part]
    return current


def semantic_contract_payload(spec: Mapping[str, Any]) -> dict[str, Any]:
    paths = spec.get("semantic_contract_components")
    if paths != list(REGISTERED_SEMANTIC_COMPONENTS):
        fail(
            "semantic_contract_components",
            "semantic contract component registry mismatch",
        )
    return {path: get_path(spec, path) for path in paths}


def semantic_contract_sha256(spec: Mapping[str, Any]) -> str:
    return canonical_sha256(semantic_contract_payload(spec))


def _safe_relative_path(relative: str) -> PurePosixPath:
    if not isinstance(relative, str) or not relative or "\\" in relative:
        fail("dependency_path", f"unsafe registered path {relative!r}")
    posix = PurePosixPath(relative)
    if (
        posix.is_absolute()
        or posix.as_posix() != relative
        or any(part in {"", ".", ".."} for part in posix.parts)
        or any(":" in part for part in posix.parts)
    ):
        fail("dependency_path", f"unsafe registered path {relative!r}", relative)
    return posix


def registered_repo_root(
    entrypoint: Path, requested_root: Path | None = None
) -> Path:
    resolved_entrypoint = Path(entrypoint).resolve()
    if not resolved_entrypoint.is_file():
        fail(
            "loaded_source",
            f"executing entrypoint is not a file: {resolved_entrypoint}",
            str(entrypoint),
        )
    if (
        resolved_entrypoint.parent.name != "0015"
        or resolved_entrypoint.parent.parent.name != "artifacts"
    ):
        fail(
            "dependency_root",
            f"executing entrypoint is not under artifacts/0015: {entrypoint}",
            str(entrypoint),
        )
    try:
        root = resolved_entrypoint.parents[2]
    except IndexError:
        fail(
            "dependency_root",
            f"executing entrypoint is not below artifacts/0015: {entrypoint}",
            str(entrypoint),
        )
    relative_entrypoint = resolved_entrypoint.relative_to(root).as_posix()
    if relative_entrypoint not in REGISTERED_DEPENDENCIES:
        fail(
            "loaded_source",
            f"executing entrypoint is not registered: {relative_entrypoint}",
            relative_entrypoint,
        )
    if requested_root is not None and Path(requested_root).resolve() != root:
        fail(
            "dependency_root",
            "dependency root must equal the repository containing the executing launcher",
            str(requested_root),
        )
    return root


def registered_repo_path(
    root: Path,
    relative: str,
    *,
    require_file: bool = True,
    require_directory: bool = False,
) -> Path:
    posix = _safe_relative_path(relative)
    resolved_root = Path(root).resolve()
    if not resolved_root.is_dir():
        fail("dependency_root", f"repository root is not a directory: {root}")
    lexical = resolved_root.joinpath(*posix.parts)
    if lexical.is_symlink():
        fail("dependency_path", f"registered path may not be a symlink: {relative}")
    resolved = lexical.resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        fail(
            "dependency_path",
            f"registered path escapes repository root: {relative}",
            relative,
        )
    if require_file and not resolved.is_file():
        fail("dependency_missing", f"missing registered file {relative}", relative)
    if require_directory and not resolved.is_dir():
        fail(
            "dependency_missing",
            f"missing registered directory {relative}",
            relative,
        )
    return resolved


def dependency_path(root: Path, relative: str) -> Path:
    return registered_repo_path(root, relative)


def assert_registered_path(
    root: Path, relative: str, observed_path: str | Path
) -> Path:
    expected = registered_repo_path(root, relative)
    observed = Path(observed_path).resolve()
    if observed != expected:
        fail(
            "registered_path",
            f"supplied path differs from registered repository file: {relative}",
            str(observed),
        )
    return expected


def validate_dependency_declaration(spec: Mapping[str, Any]) -> None:
    dependencies = spec.get("executable_dependencies")
    if dependencies != list(REGISTERED_DEPENDENCIES):
        fail(
            "dependency_set",
            "registered executable dependency set/order mismatch",
        )
    if len(dependencies) != len(set(dependencies)):
        fail("dependency_set", "duplicate executable dependency")
    for relative in dependencies:
        _safe_relative_path(relative)


def verify_python_dependency_inventory(root: Path) -> None:
    directory = registered_repo_path(
        root,
        "artifacts/0015",
        require_file=False,
        require_directory=True,
    )
    actual = sorted(
        path.relative_to(Path(root).resolve()).as_posix()
        for path in directory.iterdir()
        if path.is_file() and path.suffix == ".py"
    )
    expected = sorted(REGISTERED_DEPENDENCIES)
    if actual != expected:
        fail(
            "dependency_set",
            f"Python dependency inventory mismatch; extra={sorted(set(actual)-set(expected))}, "
            f"missing={sorted(set(expected)-set(actual))}",
            "artifacts/0015",
        )


def validate_registered_python_surface(root: Path) -> None:
    """Compatibility name for the exact artifacts/0015 Python inventory check."""
    verify_python_dependency_inventory(root)


def dependency_inventory(
    spec: Mapping[str, Any], root: Path
) -> list[dict[str, str]]:
    validate_dependency_declaration(spec)
    verify_python_dependency_inventory(root)
    return [
        {
            "path": relative,
            "normalized_lf_sha256": normalized_lf_sha256(
                dependency_path(root, relative)
            ),
        }
        for relative in REGISTERED_DEPENDENCIES
    ]


def assert_loaded_source(
    root: Path, relative: str, observed_file: str | Path | None
) -> None:
    if relative not in REGISTERED_DEPENDENCIES:
        fail(
            "loaded_source",
            f"loaded source is not a registered dependency: {relative}",
            relative,
        )
    if observed_file is None:
        fail("loaded_source", f"loaded module has no __file__: {relative}", relative)
    expected = dependency_path(root, relative)
    observed = Path(observed_file).resolve()
    if observed != expected:
        fail(
            "loaded_source",
            f"executed source differs from registered dependency: {relative}",
            str(observed),
        )


def assert_loaded_sources(
    root: Path,
    observed_files: Mapping[str, str | Path | None],
    required_relatives: Sequence[str] = (),
) -> None:
    if len(observed_files) != len(set(observed_files)):
        fail("loaded_source", "duplicate loaded-source binding")
    for relative in required_relatives:
        if relative not in observed_files:
            fail(
                "loaded_source",
                f"required loaded-source binding absent: {relative}",
                relative,
            )
    for relative, observed_file in observed_files.items():
        assert_loaded_source(root, relative, observed_file)


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
        fail("record_schema", "record_schemas missing")
    for name, schema in schemas.items():
        if (
            set(schema) != {"additional_fields", "field_order", "fields"}
            or schema["additional_fields"] is not False
        ):
            fail("record_schema", f"record schema {name} must be closed", name)
        if (
            set(schema["field_order"]) != set(schema["fields"])
            or len(schema["field_order"]) != len(schema["fields"])
        ):
            fail(
                "record_schema",
                f"record schema {name} field_order incomplete",
                name,
            )
        for field, descriptor in schema["fields"].items():
            if (
                not isinstance(descriptor, Mapping)
                or descriptor.get("type") not in allowed
            ):
                fail(
                    "record_schema",
                    f"invalid type for {name}.{field}",
                    f"{name}.{field}",
                )
            if descriptor["type"] in {"enum", "nullable_enum"} and not isinstance(
                get_path(spec, descriptor["path"]), list
            ):
                fail(
                    "record_schema",
                    f"bad enum path for {name}.{field}",
                    f"{name}.{field}",
                )
            if (
                descriptor["type"] == "record"
                and descriptor.get("schema") not in schemas
            ):
                fail(
                    "record_schema",
                    f"unknown nested record schema for {name}.{field}",
                    f"{name}.{field}",
                )


def verify_record(
    spec: Mapping[str, Any],
    schema_name: str,
    record: Mapping[str, Any],
    location: str,
) -> None:
    if not isinstance(record, Mapping):
        fail("record_shape", f"{schema_name} record is not a mapping", location)
    schema = spec["record_schemas"][schema_name]
    if set(record) != set(schema["fields"]):
        fail(
            "record_shape",
            f"{schema_name} fields mismatch; "
            f"extra={sorted(set(record)-set(schema['fields']))}, "
            f"missing={sorted(set(schema['fields'])-set(record))}",
            location,
        )
    directions = set(spec["direction_set"])
    for field in schema["field_order"]:
        value = record[field]
        descriptor = schema["fields"][field]
        kind = descriptor["type"]
        valid = True
        if kind == "string":
            valid = isinstance(value, str)
        elif kind == "integer":
            valid = type(value) is int
        elif kind == "boolean":
            valid = type(value) is bool
        elif kind == "fraction":
            try:
                parse_fraction(value)
            except VerificationError:
                valid = False
        elif kind == "direction":
            valid = type(value) is int and value in directions
        elif kind == "nullable_direction":
            valid = value is None or (type(value) is int and value in directions)
        elif kind == "nullable_string":
            valid = value is None or isinstance(value, str)
        elif kind == "nullable_integer":
            valid = value is None or type(value) is int
        elif kind == "nullable_fraction":
            if value is not None:
                try:
                    parse_fraction(value)
                except VerificationError:
                    valid = False
        elif kind == "array":
            valid = isinstance(value, list)
        elif kind == "nullable_array_direction":
            valid = value is None or (
                isinstance(value, list)
                and all(type(item) is int and item in directions for item in value)
            )
        elif kind in {"enum", "nullable_enum"}:
            valid = (
                value is None
                if kind == "nullable_enum" and value is None
                else value in get_path(spec, descriptor["path"])
            )
        elif kind == "record":
            valid = isinstance(value, Mapping)
            if valid:
                verify_record(
                    spec,
                    descriptor["schema"],
                    value,
                    f"{location}.{field}",
                )
        if not valid:
            fail(
                "record_type",
                f"invalid {schema_name}.{field}: {value!r}",
                f"{location}.{field}",
            )
        if descriptor.get("nonnegative") and parse_fraction(value) < 0:
            fail(
                "record_type",
                f"negative value forbidden for {schema_name}.{field}",
                f"{location}.{field}",
            )
        if "allowed" in descriptor and value not in descriptor["allowed"]:
            fail(
                "record_type",
                f"value not allowed for {schema_name}.{field}",
                f"{location}.{field}",
            )


def verify_constructor_spec(spec: Mapping[str, Any]) -> None:
    if not isinstance(spec, Mapping):
        fail("spec_schema", "constructor specification must be a mapping")
    if canonical_sha256(spec) != REGISTERED_SPEC_SHA256:
        fail(
            "registered_spec_hash",
            "constructor specification is not the fixed registered contract",
        )

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
        fail(
            "spec_schema",
            f"spec keys mismatch extra={sorted(set(spec)-exact_top)} "
            f"missing={sorted(exact_top-set(spec))}",
        )
    if spec["schema_version"] != SPEC_SCHEMA:
        fail("spec_schema", "unsupported constructor schema")
    if (
        spec["semantic_contract_version"]
        != "cyz-0015-fixed-registered-contract-v3"
        or spec["interpretation_mode"] != INTERPRETATION_MODE
    ):
        fail(
            "interpretation_mode",
            "fixed registered interpretation boundary absent",
        )

    validate_dependency_declaration(spec)
    if spec["semantic_contract_components"] != list(
        REGISTERED_SEMANTIC_COMPONENTS
    ):
        fail(
            "semantic_contract_components",
            "semantic contract component registry mismatch",
        )
    if semantic_contract_sha256(spec) != REGISTERED_SEMANTIC_CONTRACT_SHA256:
        fail(
            "registered_semantic_hash",
            "semantic contract digest differs from the fixed registration",
        )
    if spec["input_schema"] != {
        "allowed_fields": REGISTERED_INPUT_TYPES,
        "forbidden_fields": REGISTERED_FORBIDDEN_INPUT_FIELDS,
    }:
        fail("input_schema", "registered input type schema mismatch")
    if spec["process_type"] != "scheduled_markov_renewal":
        fail(
            "scheduled_process_type",
            "process_type is not scheduled_markov_renewal",
        )
    if spec["ctmc_export"] != "forbidden":
        fail("ctmc_export", "CTMC export prohibition is absent")
    if spec["direction_set"] != list(range(9)):
        fail("direction_set", "direction_set must be anonymous 0..8")

    prior = spec["frame_prior"]
    if (
        prior["status"] != "proposed_microscopic_closure_parameter"
        or prior["enumeration"] != "ordered_distinct_roles"
        or prior["arity_input"] != "frame_arity"
        or prior["minimum_arity"] != 2
        or prior["maximum_arity"] != 4
        or prior["velocity_role_index"] != 1
        or len(prior["role_catalog"]) < prior["maximum_arity"]
    ):
        fail("frame_prior_schema", "registered frame prior contract mismatch")

    if (
        spec["reverse_rule"]["claim"]
        != "proposed_reverse_ratio_not_detailed_balance"
    ):
        fail(
            "unsupported_detailed_balance_claim",
            "reverse ratio mislabeled as detailed balance",
        )
    expected_s9 = [
        {"id": f"s{index}", "swap": [index, index + 1]} for index in range(8)
    ]
    if spec["s9"]["adjacent_generators"] != expected_s9:
        fail("s9_spec", "serialized adjacent S9 generators missing or corrupted")
    if spec["s9"]["metric_and_kernel_transform_together"] is not True:
        fail("s9_spec", "S9 metric/kernel joint action disabled")
    if (
        spec["mark_rule"]["include_central"] is not True
        or spec["mark_rule"]["signed_basis_marks"] is not True
        or spec["mark_rule"]["probability"]
        != "uniform_over_frame_local_marks"
    ):
        fail("mark_rule", "registered mark rule mismatch")

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
        fail("registry_schema", "probability registry schema mismatch")
    central_probability = parse_fraction(registry["central_ann_probability"])
    shell_probability = parse_fraction(registry["shell_ann_probability"])
    if not 0 <= central_probability <= 1 or not 0 <= shell_probability <= 1:
        fail("registry_probability", "registered probability outside [0,1]")
    lower, upper = map(parse_fraction, registry["shell_outward_interval"])
    if not lower < shell_probability < upper:
        fail("registry_interval", "shell probability outside registered interval")

    charge = spec["state_rule"]["global_charge_default"]
    if (
        not isinstance(charge, list)
        or len(charge) != 9
        or any(type(component) is not int for component in charge)
    ):
        fail(
            "state_schema",
            "global charge basis must be an integer 9-vector",
        )

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
        fail("schedule_schema", "countdown phase contract invalid")

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
        fail("id_schema", "ID grammar differs from registered contract")

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
    program = spec["constructor_program"]
    schemas = spec["operation_schemas"]
    if [node.get("op") for node in program] != expected_operations:
        fail("constructor_program", "registered constructor stage order mismatch")
    if set(schemas) != set(expected_operations):
        fail("operation_contract", "registered operation schema set mismatch")

    seen: set[str] = set()
    valid_sources = set(REGISTERED_INPUT_TYPES) | {
        "direction_set",
        "histories",
        "cemetery_reasons",
        "adjacent_generators",
    }
    for node in program:
        if (
            set(node) != {"id", "op", "inputs", "params"}
            or node["id"] in seen
        ):
            fail(
                "constructor_program",
                "constructor node schema or identity invalid",
                str(node.get("id", "")),
            )
        for name in node["inputs"]:
            if name not in valid_sources and name not in seen:
                fail(
                    "constructor_program",
                    f"unregistered or non-topological constructor input {name}",
                    node["id"],
                )
        seen.add(node["id"])
        valid_sources.add(node["id"])
        operation = node["op"]
        schema = schemas[operation]
        if set(schema) != {
            "inputs",
            "output",
            "semantic_dependencies",
            "params",
        }:
            fail(
                "operation_contract",
                f"operation {operation} contract not closed",
                operation,
            )
        if [item.get("name") for item in schema["inputs"]] != node["inputs"]:
            fail(
                "operation_input_schema",
                f"operation {operation} input binding mismatch",
                operation,
            )
        if any(
            set(item) != {"name", "type"} or not item["type"]
            for item in schema["inputs"]
        ):
            fail(
                "operation_input_schema",
                f"operation {operation} inputs not fully typed",
                operation,
            )
        if set(schema["output"]) != {
            "container",
            "record_schema",
            "ordering_rule",
            "id_schema",
        }:
            fail(
                "operation_output_schema",
                f"operation {operation} output not typed",
                operation,
            )
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
            fail(
                "operation_contract",
                f"operation {operation} params unbound",
                operation,
            )
        if schema["params"]["semantic_rule"] not in spec["constitutive_rules"]:
            fail(
                "operation_contract",
                f"operation {operation} semantic rule absent",
                operation,
            )
        if schema["output"]["ordering_rule"] not in spec["ordering_rules"]:
            fail(
                "operation_contract",
                f"operation {operation} ordering absent",
                operation,
            )
        for dependency in schema["semantic_dependencies"]:
            get_path(spec, dependency)


def _require_fraction_string(field: str, value: Any) -> Fraction:
    if not isinstance(value, str):
        fail(
            "input_type",
            f"{field} must be a canonical fraction string",
            field,
        )
    return parse_fraction(value)


def _verify_typed_value(field: str, descriptor: str, value: Any) -> None:
    if descriptor == "bool":
        if type(value) is not bool:
            fail("input_type", f"{field} must be boolean", field)
        return
    integer_match = re.fullmatch(r"integer\[(-?\d+),(-?\d+)\]", descriptor)
    if integer_match:
        lower, upper = map(int, integer_match.groups())
        if type(value) is not int or not lower <= value <= upper:
            fail(
                "input_type",
                f"{field} must be an integer in [{lower},{upper}]",
                field,
            )
        return
    enum_match = re.fullmatch(r"enum\[(.+)\]", descriptor)
    if enum_match:
        allowed = enum_match.group(1).split(",")
        if not isinstance(value, str) or value not in allowed:
            fail("input_type", f"{field} must be one of {allowed}", field)
        return
    tuple_match = re.fullmatch(r"tuple\[(\d+),(.+)\]", descriptor)
    if tuple_match:
        length = int(tuple_match.group(1))
        item_descriptor = tuple_match.group(2)
        if not isinstance(value, list) or len(value) != length:
            fail(
                "input_type",
                f"{field} must contain exactly {length} items",
                field,
            )
        for index, item in enumerate(value):
            _verify_typed_value(f"{field}[{index}]", item_descriptor, item)
        return
    if descriptor in {
        "fraction",
        "positive_fraction",
        "nonnegative_fraction",
        "fraction[0,1]",
    }:
        parsed = _require_fraction_string(field, value)
        if descriptor == "positive_fraction" and parsed <= 0:
            fail("input_type", f"{field} must be positive", field)
        if descriptor == "nonnegative_fraction" and parsed < 0:
            fail("input_type", f"{field} must be nonnegative", field)
        if descriptor == "fraction[0,1]" and not 0 <= parsed <= 1:
            fail("input_type", f"{field} must lie in [0,1]", field)
        return
    fail(
        "input_schema",
        f"unsupported registered type descriptor {descriptor}",
        field,
    )


def verify_input(spec: Mapping[str, Any], vector: Mapping[str, Any]) -> None:
    fields = spec["input_schema"]["allowed_fields"]
    if fields != REGISTERED_INPUT_TYPES:
        fail("input_schema", "registered input type schema mismatch")
    if not isinstance(vector, Mapping) or set(vector) != set(fields):
        extra = (
            sorted(set(vector) - set(fields))
            if isinstance(vector, Mapping)
            else []
        )
        missing = (
            sorted(set(fields) - set(vector))
            if isinstance(vector, Mapping)
            else sorted(fields)
        )
        fail(
            "control_unregistered_field",
            f"control fields mismatch extra={extra} missing={missing}",
        )
    for field, descriptor in fields.items():
        _verify_typed_value(field, descriptor, vector[field])
    if parse_fraction(vector["speed_min"]) >= parse_fraction(vector["speed_max"]):
        fail(
            "speed_input",
            "speed_min must be strictly less than speed_max",
        )


def verify_control_manifest(
    spec: Mapping[str, Any], manifest: Mapping[str, Any]
) -> None:
    verify_constructor_spec(spec)
    if not isinstance(manifest, Mapping):
        fail("manifest_schema", "control manifest must be a mapping")
    if canonical_sha256(manifest) != REGISTERED_MANIFEST_SHA256:
        fail(
            "registered_manifest_hash",
            "control manifest is not the fixed registered suite",
        )
    exact = {
        "schema_version",
        "constructor_spec_sha256",
        "constructor_reads_only",
        "controls",
        "opaque_id_renaming_control",
        "report_metadata_policy",
    }
    if set(manifest) != exact:
        fail("manifest_schema", "control-vector manifest schema not closed")
    if manifest["schema_version"] != MANIFEST_SCHEMA:
        fail("manifest_schema", "unsupported control manifest schema")
    if manifest["constructor_spec_sha256"] != REGISTERED_SPEC_SHA256:
        fail(
            "control_manifest_spec_hash",
            "manifest does not bind the registered constructor spec",
        )
    if (
        manifest["constructor_reads_only"]
        != "opaque_id_and_input; report_metadata_is_not_constructor_input"
        or manifest["report_metadata_policy"]
        != "human_label is a fixed verifier-suite role and is never passed to constructor stages"
    ):
        fail(
            "manifest_schema",
            "constructor/report metadata boundary mismatch",
        )

    controls = manifest["controls"]
    if not isinstance(controls, list) or len(controls) != len(
        REGISTERED_CONTROL_ROLES
    ):
        fail("manifest_schema", "registered control suite is incomplete")
    ids: set[str] = set()
    roles: set[str] = set()
    for control in controls:
        if (
            not isinstance(control, Mapping)
            or set(control)
            != {"opaque_id", "input", "obligations", "report_metadata"}
        ):
            fail("manifest_schema", "control record schema not closed")
        opaque_id = control["opaque_id"]
        if (
            not isinstance(opaque_id, str)
            or not opaque_id
            or opaque_id in ids
        ):
            fail(
                "manifest_schema",
                "control opaque IDs must be nonempty and unique",
            )
        ids.add(opaque_id)
        metadata = control["report_metadata"]
        if not isinstance(metadata, Mapping) or set(metadata) != {"human_label"}:
            fail(
                "manifest_schema",
                "control report metadata schema not closed",
                opaque_id,
            )
        role = metadata["human_label"]
        if role not in REGISTERED_CONTROL_ROLES or role in roles:
            fail(
                "manifest_schema",
                "control role set is incomplete or duplicated",
                opaque_id,
            )
        roles.add(role)
        if control["obligations"] != ROLE_OBLIGATIONS[role]:
            fail(
                "manifest_schema",
                f"control obligations mismatch role {role}",
                opaque_id,
            )
        verify_input(spec, control["input"])
    if roles != REGISTERED_CONTROL_ROLES:
        fail("manifest_schema", "registered control roles incomplete")

    rename = manifest["opaque_id_renaming_control"]
    if not isinstance(rename, Mapping) or set(rename) != {
        "source_opaque_id",
        "renamed_opaque_id",
        "expected",
    }:
        fail(
            "manifest_schema",
            "opaque-ID renaming control schema not closed",
        )
    if (
        rename["source_opaque_id"] not in ids
        or not isinstance(rename["renamed_opaque_id"], str)
        or not rename["renamed_opaque_id"]
        or rename["renamed_opaque_id"] in ids
        or rename["expected"] != "expanded_kernel_isomorphic"
    ):
        fail(
            "manifest_schema",
            "opaque-ID renaming control is invalid",
        )
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
        fail(
            "manifest_schema",
            "opaque-ID rename probe is not bound to the registered "
            "three-large role",
        )


def verify_dependency_bindings(
    spec: Mapping[str, Any], artifact: Mapping[str, Any], root: Path
) -> None:
    verify_constructor_spec(spec)
    observed_inventory = dependency_inventory(spec, root)
    records = artifact.get("executable_dependencies")
    if not isinstance(records, list) or records != observed_inventory:
        expected_paths = [row["path"] for row in observed_inventory]
        supplied_paths = (
            [row.get("path") for row in records if isinstance(row, Mapping)]
            if isinstance(records, list)
            else []
        )
        if supplied_paths != expected_paths:
            fail(
                "dependency_set",
                "artifact executable dependency set/order mismatch",
            )
        fail(
            "dependency_hash",
            "artifact executable dependency hashes do not match registered files",
        )
    for record in records:
        if set(record) != {"path", "normalized_lf_sha256"}:
            fail(
                "dependency_schema",
                "dependency record schema invalid",
                str(record),
            )
        if not re.fullmatch(r"[0-9a-f]{64}", record["normalized_lf_sha256"]):
            fail(
                "dependency_schema",
                "dependency hash is not lowercase SHA-256",
                record["path"],
            )
    assert_loaded_source(
        root,
        "artifacts/0015/verifier_core.py",
        __file__,
    )
