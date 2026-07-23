#!/usr/bin/env python3
"""Assemble artifacts for the fixed registered Brief 0015 constructor."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import generator_core as core
import generator_model as model


SINGLE_ARTIFACT_SCHEMA = "cyz-0015-single-instance-v3"
ACCEPTANCE_DOMAIN = "exact_registered_spec_and_manifest_digests_only"
SOURCE_BINDING_POLICY = (
    "executed_modules_must_resolve_to_registered_dependency_files"
)


def assert_generator_runtime(root: Path, entrypoint: Path) -> None:
    """Bind the executing generator modules to the registered repository files."""
    core.assert_loaded_source(
        root, "artifacts/0015/generate_0015.py", entrypoint
    )
    core.assert_loaded_source(
        root, "artifacts/0015/generator_core.py", core.__file__
    )
    core.assert_loaded_source(
        root, "artifacts/0015/generator_model.py", model.__file__
    )
    core.assert_loaded_source(
        root, "artifacts/0015/generator_artifact.py", __file__
    )
    core.validate_registered_python_surface(root)


def _assert_control_obligations(
    control: Mapping[str, Any],
    expanded: Mapping[str, Any],
    counts: Mapping[str, Any],
) -> None:
    role = control["report_metadata"]["human_label"]
    obligations = control["obligations"]
    if "expected_valid_frames" in obligations:
        if counts["valid_frames"] != obligations["expected_valid_frames"]:
            raise core.ConstructionError(
                f"generated output violates valid-frame obligation for {role}"
            )
    if "expected_uniform_source_case" in obligations:
        expected = obligations["expected_uniform_source_case"]
        if counts["source_case_counts"] != {
            expected: counts["frames_total"]
        }:
            raise core.ConstructionError(
                f"generated output violates source-case obligation for {role}"
            )
    if "expected_frame_arity" in obligations:
        arities = {
            frame["arity"] for frame in expanded["frames"].values()
        }
        if arities != {obligations["expected_frame_arity"]}:
            raise core.ConstructionError(
                f"generated output violates arity obligation for {role}"
            )
    if obligations.get("expected_interval_boundary_valid") is True:
        if counts["source_case_counts"] != {
            "valid": counts["frames_total"]
        }:
            raise core.ConstructionError(
                f"generated output violates interval obligation for {role}"
            )
    if "calibration_times" in obligations:
        if model.calibration_times(expanded) != obligations["calibration_times"]:
            raise core.ConstructionError(
                f"generated output violates calibration obligation for {role}"
            )


def _instance_record(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    opaque_id: str,
    vector: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(opaque_id, str) or not opaque_id:
        raise core.ConstructionError("opaque instance ID must be nonempty")
    return {
        "opaque_id": opaque_id,
        **_semantic_instance_record(spec, manifest, vector),
    }


def _semantic_instance_record(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    vector: Mapping[str, Any],
) -> dict[str, Any]:
    """Construct the semantic record without receiving an opaque ID."""
    core.validate_input(spec, vector)
    expanded = model.execute_registered_constructor(spec, vector)
    return _record_from_expanded(
        spec, manifest, vector, expanded
    )


def _record_from_expanded(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    vector: Mapping[str, Any],
    expanded: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "input": dict(vector),
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
        "expanded_sha256": model.expanded_hash(spec, expanded),
        "expanded_counts": model.summary(expanded),
        "calibration_event_times": model.calibration_times(expanded),
    }


def _control_instance_record(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    control: Mapping[str, Any],
) -> dict[str, Any]:
    core.validate_input(spec, control["input"])
    expanded = model.execute_registered_constructor(
        spec, control["input"]
    )
    record = _record_from_expanded(
        spec,
        manifest,
        control["input"],
        expanded,
    )
    record = {"opaque_id": control["opaque_id"], **record}
    _assert_control_obligations(
        control, expanded, record["expanded_counts"]
    )
    return record


def _document_bindings(
    spec: Mapping[str, Any], manifest: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "constructor_spec_path": "artifacts/0015/constructor_spec.json",
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_path": (
            "artifacts/0015/control_vector_manifest.json"
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
        "constructor_program_sha256": core.canonical_sha(
            spec["constructor_program"]
        ),
        "operation_schemas_sha256": core.canonical_sha(
            spec["operation_schemas"]
        ),
        "record_schemas_sha256": core.canonical_sha(
            spec["record_schemas"]
        ),
        "id_schemas_sha256": core.canonical_sha(spec["id_schemas"]),
        "parameter_influence_sha256": core.canonical_sha(
            spec["parameter_influence"]
        ),
    }


def _load_registered_documents(
    spec_path: Path, manifest_path: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    spec = core.load_json(spec_path)
    manifest = core.load_json(manifest_path)
    if not isinstance(spec, dict) or not isinstance(manifest, dict):
        raise core.ConstructionError(
            "specification and manifest must be JSON objects"
        )
    core.validate_spec(spec)
    core.validate_manifest(spec, manifest)
    return spec, manifest


def build_artifact(
    spec_path: Path,
    manifest_path: Path,
    root: Path,
    entrypoint: Path,
) -> dict[str, Any]:
    assert_generator_runtime(root, entrypoint)
    spec, manifest = _load_registered_documents(spec_path, manifest_path)
    records = [
        _control_instance_record(spec, manifest, control)
        for control in manifest["controls"]
    ]
    artifact = {
        "schema_version": core.ARTIFACT_SCHEMA,
        "generator_api_version": core.GENERATOR_API,
        "interpretation_mode": core.INTERPRETATION_MODE,
        "acceptance_domain": ACCEPTANCE_DOMAIN,
        "source_binding_policy": SOURCE_BINDING_POLICY,
        "process_type": spec["process_type"],
        "ctmc_export": spec["ctmc_export"],
        "classification": spec["classification"],
        **_document_bindings(spec, manifest),
        "executable_dependencies": core.dependency_inventory(spec, root),
        "instances": records,
        "opaque_instance_ids_are_nonsemantic": True,
        "expanded_hash_stream_format": (
            "registered section-name LF then canonical [key,value] records LF"
        ),
    }
    return artifact


def build_single_artifact(
    spec_path: Path,
    manifest_path: Path,
    input_path: Path,
    root: Path,
    entrypoint: Path,
    opaque_id: str,
) -> dict[str, Any]:
    """Build one explicit input without borrowing defaults from a manifest row."""
    assert_generator_runtime(root, entrypoint)
    spec, manifest = _load_registered_documents(spec_path, manifest_path)
    vector = core.load_json(input_path)
    if not isinstance(vector, dict):
        raise core.ConstructionError("--single-input must contain a JSON object")
    record = _instance_record(spec, manifest, opaque_id, vector)
    return {
        "schema_version": SINGLE_ARTIFACT_SCHEMA,
        "generator_api_version": core.GENERATOR_API,
        "interpretation_mode": core.INTERPRETATION_MODE,
        "acceptance_domain": ACCEPTANCE_DOMAIN,
        "source_binding_policy": SOURCE_BINDING_POLICY,
        **_document_bindings(spec, manifest),
        "executable_dependencies": core.dependency_inventory(spec, root),
        "instance": record,
    }
