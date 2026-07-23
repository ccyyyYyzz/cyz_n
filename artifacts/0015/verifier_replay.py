#!/usr/bin/env python3
"""Independent artifact replay for the fixed Brief 0015 registration."""
from __future__ import annotations

import copy
import gc
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping

import verifier_core as core
import verifier_model as model
import verifier_semantics as semantics


SINGLE_ARTIFACT_SCHEMA = "cyz-0015-single-instance-v3"
EXPANDED_HASH_STREAM_FORMAT = (
    "registered section-name LF then canonical [key,value] records LF"
)


def _structured_generator_error(
    process: subprocess.CompletedProcess[str],
) -> Mapping[str, Any] | None:
    for line in reversed(process.stderr.splitlines()):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(parsed, Mapping)
            and parsed.get("status") == "ERROR"
            and isinstance(parsed.get("code"), str)
        ):
            return parsed
    return None


def controls_by_role(
    manifest: Mapping[str, Any],
) -> dict[str, Mapping[str, Any]]:
    controls = {
        control["report_metadata"]["human_label"]: control
        for control in manifest["controls"]
    }
    if set(controls) != core.REGISTERED_CONTROL_ROLES:
        core.fail("manifest_role_coverage", "registered role set is incomplete")
    return controls


def apply_spec_patch(spec: dict[str, Any], mutation: str) -> None:
    program = spec["constructor_program"]
    if mutation == "hidden_count_if_three":
        program[0]["op"] = "count_if"
    elif mutation == "hidden_fraction_branch":
        program[1]["params"]["hidden_exactly_three_branch"] = True
    elif mutation == "hidden_count_alias":
        program[1]["inputs"].append("number_above_boundary")
    elif mutation == "hidden_registry_three":
        spec["probability_registry"]["gkm_sparse_v1"][
            "special_three_case"
        ] = "1/1"
    elif mutation == "hidden_environment_global":
        program[1]["op"] = "environment_read"
    elif mutation == "hidden_post_rank_override":
        program[-1]["inputs"].append("response_rank")
    elif mutation == "remove_s9_generators":
        spec["s9"]["adjacent_generators"].pop()
    elif mutation == "corrupt_s9_generator":
        spec["s9"]["adjacent_generators"][0]["swap"] = [0, 2]
    elif mutation == "precedence_changed":
        spec["validity"]["precedence"] = [
            "velocity",
            "unresolved_amplitude",
            "coupling_dilution",
            "geometry",
            "valid",
        ]
    elif mutation == "interval_closure_changed":
        spec["validity"]["speed_interval"]["lower"] = "open"
    elif mutation == "reverse_relabel_detailed_balance":
        spec["reverse_rule"]["claim"] = "detailed_balance"
    elif mutation == "ctmc_process_type":
        spec["process_type"] = "ctmc_generator"
    elif mutation == "operation_empty_params":
        operation = "construct_complete_event_rows"
        spec["operation_schemas"][operation]["params"] = {}
        next(
            node for node in program if node["op"] == operation
        )["params"] = {}
    elif mutation == "record_schema_event_field_removed":
        event_schema = spec["record_schemas"]["event_record"]
        event_schema["fields"].pop("destination_state_id")
        event_schema["field_order"].remove("destination_state_id")
    elif mutation == "parameter_influence_probability_removed":
        spec["parameter_influence"]["events"].pop("probability")
    elif mutation == "id_grammar_changed":
        spec["id_schemas"]["event_id"][
            "template"
        ] = "{source_state_id}|BAD|{channel_id}|{mark_id}"
    elif mutation == "semantic_dependencies_removed":
        spec["operation_schemas"]["construct_complete_event_rows"][
            "semantic_dependencies"
        ] = []
    elif mutation == "output_record_schema_substituted":
        operation = "construct_complete_event_rows"
        schema = spec["operation_schemas"][operation]
        schema["output"]["record_schema"] = "frame_record"
        schema["params"]["record_schema"] = "frame_record"
        next(
            node for node in program if node["op"] == operation
        )["params"]["record_schema"] = "frame_record"
    elif mutation == "unregistered_constitutive_branch":
        program.insert(
            2,
            {
                "id": "hidden_branch",
                "op": "unregistered_branch",
                "inputs": ["metric_radii"],
                "params": {},
            },
        )
    elif mutation == "opaque_label_branch":
        program[1]["inputs"].append("opaque_id")
    elif mutation == "constitutive_rule_text_rebound":
        spec["constitutive_rules"]["events_v2"][
            "products"
        ] = "semantically meaningless rebound text"
    elif mutation == "semantic_rule_retargeted_rebound":
        operation = "construct_complete_event_rows"
        replacement = "frames_v2"
        spec["operation_schemas"][operation]["params"][
            "semantic_rule"
        ] = replacement
        next(
            node for node in program if node["op"] == operation
        )["params"]["semantic_rule"] = replacement
    elif mutation == "contract_id_rebound":
        operation = "construct_complete_event_rows"
        spec["operation_schemas"][operation]["params"][
            "contract_id"
        ] = "IGNORED"
        next(
            node for node in program if node["op"] == operation
        )["params"]["contract_id"] = "IGNORED"
    elif mutation == "param_record_order_id_rebound":
        operation = "construct_complete_event_rows"
        params = spec["operation_schemas"][operation]["params"]
        node_params = next(
            node for node in program if node["op"] == operation
        )["params"]
        for key in ("record_schema", "ordering_rule", "id_schema"):
            params[key] = "IGNORED"
            node_params[key] = "IGNORED"
    elif mutation == "parameter_influence_values_rebound":
        spec["parameter_influence"]["events"] = {
            key: ["ignored.path"]
            for key in spec["parameter_influence"]["events"]
        }
    elif mutation == "constructor_node_id_or_input_rebound":
        program[1]["id"] = "candidate_marks_rebound"
        for node in program[2:]:
            node["inputs"] = [
                "candidate_marks_rebound"
                if item == "candidate_marks"
                else item
                for item in node["inputs"]
            ]
    elif mutation == "semantic_contract_components_rebound":
        spec["semantic_contract_components"] = list(
            reversed(spec["semantic_contract_components"])
        )
    elif mutation == "must_consume_rebound":
        spec["must_consume"] = []
    elif mutation == "mark_include_central_disabled":
        spec["mark_rule"]["include_central"] = False
    elif mutation == "mark_signed_basis_disabled":
        spec["mark_rule"]["signed_basis_marks"] = False
    elif mutation == "probability_formula_zeroed":
        spec["probability_composition"]["annihilate"] = "0"
    elif mutation == "destination_rule_rebound":
        spec["destination_rule"]["annihilate"] = "source"
    elif mutation == "history_rule_rebound":
        spec["history_rule"]["miss"] = "preserve"
    elif mutation == "reverse_rule_rebound":
        spec["reverse_rule"]["event_pairing"] = "none"
    elif mutation == "ledger_rule_rebound":
        spec["ledger_rule"]["annihilate"]["delta_system_energy"] = "0/1"
    elif mutation == "s9_joint_action_disabled":
        spec["s9"]["metric_and_kernel_transform_together"] = False
    elif mutation == "input_schema_descriptor_changed":
        spec["input_schema"]["allowed_fields"][
            "frame_arity"
        ] = "fraction"
    elif mutation == "dependency_declaration_empty":
        spec["executable_dependencies"] = []
    elif mutation == "dependency_declaration_duplicate":
        spec["executable_dependencies"].append(
            spec["executable_dependencies"][0]
        )
    elif mutation == "dependency_declaration_traversal":
        spec["executable_dependencies"][0] = "../generate_0015.py"
    elif mutation == "dependency_declaration_absolute":
        spec["executable_dependencies"][0] = "/tmp/generate_0015.py"
    elif mutation == "dependency_declaration_backslash":
        spec["executable_dependencies"][0] = (
            r"artifacts\0015\generate_0015.py"
        )
    else:
        core.fail("unknown_patch", f"unknown spec mutation {mutation}")


def apply_manifest_patch(manifest: dict[str, Any], mutation: str) -> None:
    if mutation == "manifest_controls_empty":
        manifest["controls"] = []
    elif mutation == "manifest_obligations_empty":
        manifest["controls"][0]["obligations"] = {}
    elif mutation == "manifest_obligations_extra":
        manifest["controls"][0]["obligations"]["extra"] = True
    elif mutation == "manifest_rename_source_missing":
        manifest["opaque_id_renaming_control"][
            "source_opaque_id"
        ] = "missing"
    elif mutation == "manifest_role_duplicate":
        manifest["controls"][1]["report_metadata"] = copy.deepcopy(
            manifest["controls"][0]["report_metadata"]
        )
    elif mutation == "manifest_spec_binding_changed":
        manifest["constructor_spec_sha256"] = "0" * 64
    else:
        core.fail("unknown_patch", f"unknown manifest mutation {mutation}")


def apply_artifact_patch(artifact: dict[str, Any], mutation: str) -> None:
    if mutation == "executable_dependency_hash":
        artifact["executable_dependencies"][0][
            "normalized_lf_sha256"
        ] = "0" * 64
    elif mutation == "dependency_set_addition":
        artifact["executable_dependencies"].append(
            {
                "path": "artifacts/0015/ghost.py",
                "normalized_lf_sha256": "0" * 64,
            }
        )
    elif mutation == "executable_dependency_file":
        artifact["executable_dependencies"][0][
            "path"
        ] = "artifacts/0015/ghost.py"
    elif mutation == "artifact_interpretation_mode":
        artifact["interpretation_mode"] = "general_dsl"
    elif mutation == "artifact_dependency_inventory_removed":
        artifact.pop("executable_dependencies")
    elif mutation == "artifact_consumed_trace_added":
        artifact["instances"][0]["consumed_spec_paths_sha256"] = "0" * 64
    elif mutation == "artifact_instance_input_changed":
        artifact["instances"][0]["input"]["frame_arity"] = 2
    else:
        core.fail("unknown_patch", f"unknown artifact mutation {mutation}")


def refresh_untrusted_document_bindings(
    spec: Mapping[str, Any],
    manifest: dict[str, Any],
    artifact: dict[str, Any],
) -> None:
    """Hostile helper: refresh every non-registered document hash.

    The verifier must still reject because its independently compiled
    registration constants are deliberately not refreshed.
    """
    spec_hash = core.canonical_sha256(spec)
    manifest["constructor_spec_sha256"] = spec_hash
    manifest_hash = core.canonical_sha256(manifest)
    artifact["constructor_spec_sha256"] = spec_hash
    semantic_payload = {
        path: core.get_path(spec, path)
        for path in spec.get("semantic_contract_components", [])
    }
    semantic_hash = core.canonical_sha256(semantic_payload)
    artifact["semantic_contract_sha256"] = semantic_hash
    artifact["control_vector_manifest_sha256"] = manifest_hash
    artifact["constructor_program_sha256"] = core.canonical_sha256(
        spec["constructor_program"]
    )
    artifact["operation_schemas_sha256"] = core.canonical_sha256(
        spec["operation_schemas"]
    )
    artifact["record_schemas_sha256"] = core.canonical_sha256(
        spec["record_schemas"]
    )
    artifact["id_schemas_sha256"] = core.canonical_sha256(
        spec["id_schemas"]
    )
    artifact["parameter_influence_sha256"] = core.canonical_sha256(
        spec["parameter_influence"]
    )
    for record in artifact.get("instances", []):
        record["constructor_spec_sha256"] = spec_hash
        record["semantic_contract_sha256"] = semantic_hash
        record["control_vector_manifest_sha256"] = manifest_hash


def _artifact_schema_check(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    artifact: Mapping[str, Any],
) -> None:
    expected = {
        "schema_version",
        "generator_api_version",
        "interpretation_mode",
        "acceptance_domain",
        "source_binding_policy",
        "process_type",
        "ctmc_export",
        "classification",
        "constructor_spec_path",
        "constructor_spec_sha256",
        "semantic_contract_sha256",
        "control_vector_manifest_path",
        "control_vector_manifest_sha256",
        "constructor_program_sha256",
        "operation_schemas_sha256",
        "record_schemas_sha256",
        "id_schemas_sha256",
        "parameter_influence_sha256",
        "executable_dependencies",
        "instances",
        "opaque_instance_ids_are_nonsemantic",
        "expanded_hash_stream_format",
    }
    if not isinstance(artifact, Mapping) or set(artifact) != expected:
        actual = set(artifact) if isinstance(artifact, Mapping) else set()
        core.fail(
            "artifact_schema",
            f"artifact fields mismatch extra={sorted(actual-expected)} "
            f"missing={sorted(expected-actual)}",
        )
    if (
        artifact["schema_version"] != core.ARTIFACT_SCHEMA
        or artifact["generator_api_version"] != core.EXPECTED_GENERATOR_API
        or artifact["interpretation_mode"] != core.INTERPRETATION_MODE
        or artifact["acceptance_domain"] != core.ACCEPTANCE_DOMAIN
        or artifact["source_binding_policy"] != core.SOURCE_BINDING_POLICY
    ):
        core.fail("artifact_schema", "artifact registration boundary mismatch")
    if (
        artifact["process_type"] != spec["process_type"]
        or artifact["ctmc_export"] != spec["ctmc_export"]
        or artifact["classification"] != spec["classification"]
    ):
        core.fail(
            "scheduled_process_type",
            "artifact process declaration differs from registered spec",
        )
    if (
        artifact["constructor_spec_path"]
        != "artifacts/0015/constructor_spec.json"
        or artifact["control_vector_manifest_path"]
        != "artifacts/0015/control_vector_manifest.json"
    ):
        core.fail("artifact_binding", "registered document path mismatch")
    checks = {
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
        "constructor_program_sha256": core.canonical_sha256(
            spec["constructor_program"]
        ),
        "operation_schemas_sha256": core.canonical_sha256(
            spec["operation_schemas"]
        ),
        "record_schemas_sha256": core.canonical_sha256(
            spec["record_schemas"]
        ),
        "id_schemas_sha256": core.canonical_sha256(spec["id_schemas"]),
        "parameter_influence_sha256": core.canonical_sha256(
            spec["parameter_influence"]
        ),
    }
    for field, expected_value in checks.items():
        if artifact[field] != expected_value:
            core.fail(
                "artifact_binding",
                f"artifact {field} mismatch",
                field,
            )
    if artifact["opaque_instance_ids_are_nonsemantic"] is not True:
        core.fail(
            "instance_label_dependency",
            "artifact does not declare opaque IDs nonsemantic",
        )
    if artifact["expanded_hash_stream_format"] != EXPANDED_HASH_STREAM_FORMAT:
        core.fail("artifact_schema", "expanded-hash format mismatch")
    if not isinstance(artifact["instances"], list):
        core.fail("instance_schema", "artifact instances must be a list")


def _obligation_check(
    control: Mapping[str, Any],
    expanded: Mapping[str, Any],
    counts: Mapping[str, Any],
) -> None:
    role = control["report_metadata"]["human_label"]
    obligations = core.ROLE_OBLIGATIONS[role]
    if control["obligations"] != obligations:
        core.fail(
            "control_obligation",
            f"obligation schema differs for {role}",
            role,
        )
    if "expected_valid_frames" in obligations:
        if counts["valid_frames"] != obligations["expected_valid_frames"]:
            core.fail(
                "control_obligation",
                f"valid-frame obligation failed for {role}",
                role,
            )
    if "expected_uniform_source_case" in obligations:
        case = obligations["expected_uniform_source_case"]
        if counts["source_case_counts"] != {
            case: counts["frames_total"]
        }:
            core.fail(
                "control_obligation",
                f"uniform source-case obligation failed for {role}",
                role,
            )
    if "expected_frame_arity" in obligations:
        arities = {
            frame["arity"] for frame in expanded["frames"].values()
        }
        if arities != {obligations["expected_frame_arity"]}:
            core.fail(
                "frame_arity_control",
                f"arity obligation failed for {role}: {sorted(arities)}",
                role,
            )
    if obligations.get("expected_interval_boundary_valid") is True:
        if counts["source_case_counts"] != {
            "valid": counts["frames_total"]
        }:
            core.fail(
                "control_obligation",
                f"closed-boundary obligation failed for {role}",
                role,
            )
    if "calibration_times" in obligations:
        if (
            model.calibration_times(expanded)
            != obligations["calibration_times"]
        ):
            core.fail(
                "scheduled_clock",
                f"calibration obligation failed for {role}",
                role,
            )


def _rebuild_record(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    artifact_record: Mapping[str, Any],
    expected_id: str,
    expected_input: Mapping[str, Any],
    model_patch: Mapping[str, Any] | None = None,
    control: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    expected_fields = {
        "opaque_id",
        "input",
        "constructor_spec_sha256",
        "semantic_contract_sha256",
        "control_vector_manifest_sha256",
        "expanded_sha256",
        "expanded_counts",
        "calibration_event_times",
    }
    if not isinstance(artifact_record, Mapping) or set(
        artifact_record
    ) != expected_fields:
        core.fail(
            "instance_schema",
            "artifact instance schema mismatch",
            expected_id,
        )
    if (
        artifact_record["opaque_id"] != expected_id
        or artifact_record["input"] != expected_input
    ):
        core.fail(
            "instance_binding",
            "artifact instance input/ID differs from its binding",
            expected_id,
        )
    instance_bindings = {
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
    }
    for field, value in instance_bindings.items():
        if artifact_record[field] != value:
            core.fail(
                "instance_binding",
                f"instance {field} mismatch",
                expected_id,
            )
    vector = copy.deepcopy(expected_input)
    if (
        model_patch
        and model_patch.get("mutation")
        == "frame_arity_without_regeneration"
    ):
        vector["frame_arity"] = (
            3 if vector["frame_arity"] != 3 else 2
        )
    expanded = model.execute_registered_constructor(spec, vector)
    semantics.apply_model_patch(expanded, model_patch)
    counts = semantics.verify_model(spec, vector, expanded, expected_id)
    if control is not None:
        _obligation_check(control, expanded, counts)
    if model.expanded_hash(spec, expanded) != artifact_record["expanded_sha256"]:
        core.fail(
            "expanded_hash",
            f"expanded hash mismatch for {expected_id}",
            expected_id,
        )
    if counts != artifact_record["expanded_counts"]:
        core.fail(
            "expanded_counts",
            f"expanded counts mismatch for {expected_id}",
            expected_id,
        )
    if (
        model.calibration_times(expanded)
        != artifact_record["calibration_event_times"]
    ):
        core.fail(
            "scheduled_clock",
            "artifact calibration times mismatch",
            expected_id,
        )
    return expanded, counts


def verify_single_payload(
    payload: Mapping[str, Any],
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    root: Path,
    expected_id: str | None = None,
    expected_input: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    expected_fields = {
        "schema_version",
        "generator_api_version",
        "interpretation_mode",
        "acceptance_domain",
        "source_binding_policy",
        "constructor_spec_path",
        "constructor_spec_sha256",
        "semantic_contract_sha256",
        "control_vector_manifest_path",
        "control_vector_manifest_sha256",
        "constructor_program_sha256",
        "operation_schemas_sha256",
        "record_schemas_sha256",
        "id_schemas_sha256",
        "parameter_influence_sha256",
        "executable_dependencies",
        "instance",
    }
    if not isinstance(payload, Mapping) or set(payload) != expected_fields:
        core.fail("single_artifact_schema", "single artifact schema mismatch")
    if (
        payload["schema_version"] != SINGLE_ARTIFACT_SCHEMA
        or payload["generator_api_version"] != core.EXPECTED_GENERATOR_API
        or payload["interpretation_mode"] != core.INTERPRETATION_MODE
        or payload["acceptance_domain"] != core.ACCEPTANCE_DOMAIN
        or payload["source_binding_policy"] != core.SOURCE_BINDING_POLICY
    ):
        core.fail(
            "single_artifact_schema",
            "single artifact registration boundary mismatch",
        )
    synthetic = dict(payload)
    synthetic.update(
        {
            "schema_version": core.ARTIFACT_SCHEMA,
            "process_type": spec["process_type"],
            "ctmc_export": spec["ctmc_export"],
            "classification": spec["classification"],
            "instances": [payload["instance"]],
            "opaque_instance_ids_are_nonsemantic": True,
            "expanded_hash_stream_format": EXPANDED_HASH_STREAM_FORMAT,
        }
    )
    synthetic.pop("instance")
    _artifact_schema_check(spec, manifest, synthetic)
    core.verify_dependency_bindings(spec, synthetic, root)
    record = payload["instance"]
    identifier = expected_id if expected_id is not None else record.get("opaque_id")
    vector = (
        expected_input
        if expected_input is not None
        else record.get("input")
    )
    if not isinstance(identifier, str) or not isinstance(vector, Mapping):
        core.fail("single_artifact_schema", "single instance binding absent")
    _, counts = _rebuild_record(
        spec, manifest, record, identifier, vector
    )
    return {
        "status": "PASS",
        "opaque_id": identifier,
        "expanded_sha256": record["expanded_sha256"],
        "expanded_counts": counts,
    }


def verify_single_artifact(
    artifact_path: Path,
    spec_path: Path,
    manifest_path: Path,
    root: Path,
) -> dict[str, Any]:
    spec = core.load_json(spec_path)
    manifest = core.load_json(manifest_path)
    payload = core.load_json(artifact_path)
    core.verify_constructor_spec(spec)
    core.verify_control_manifest(spec, manifest)
    return verify_single_payload(payload, spec, manifest, root)


def _external_regeneration(
    generator: Path,
    spec_path: Path,
    manifest_path: Path,
    root: Path,
    artifact: Mapping[str, Any],
) -> dict[str, Any]:
    registered_generator = core.assert_registered_path(
        root,
        "artifacts/0015/generate_0015.py",
        generator,
    )
    with tempfile.TemporaryDirectory(prefix="cyz0015-regen-") as temp:
        output = Path(temp) / "kernel.json"
        command = [
            sys.executable,
            str(registered_generator),
            "--spec",
            str(spec_path),
            "--manifest",
            str(manifest_path),
            "--output",
            str(output),
            "--dependency-root",
            str(root),
        ]
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except subprocess.TimeoutExpired:
            core.fail(
                "generator_infrastructure",
                "external generator timed out",
                str(generator),
            )
        if process.returncode in {1, 3} or process.returncode < 0:
            core.fail(
                "generator_infrastructure",
                f"external generator infrastructure failure; "
                f"exit={process.returncode}: {process.stderr.strip()}",
                str(generator),
            )
        if process.returncode != 0:
            generator_error = _structured_generator_error(process)
            if process.returncode != 2 or generator_error is None:
                core.fail(
                    "generator_infrastructure",
                    "external generator did not return the structured "
                    f"semantic-error protocol; exit={process.returncode}",
                    str(generator),
                )
            core.fail(
                "generator_regeneration",
                "external generator semantically rejected the fixed "
                f"registration: {generator_error}",
                str(generator),
            )
        regenerated = core.load_json(output)
        if core.canonical_sha256(regenerated) != core.canonical_sha256(
            artifact
        ):
            core.fail(
                "generator_regeneration",
                "external generator did not reproduce canonical artifact",
                str(generator),
            )
        return {
            "exit_code": process.returncode,
            "canonical_payload_sha256": core.canonical_sha256(regenerated),
            "stdout_sha256": hashlib.sha256(
                process.stdout.encode("utf-8")
            ).hexdigest(),
            "stderr_sha256": hashlib.sha256(
                process.stderr.encode("utf-8")
            ).hexdigest(),
        }


def _run_single_generator(
    generator: Path,
    spec_path: Path,
    manifest_path: Path,
    root: Path,
    input_path: Path,
    output_path: Path,
    opaque_id: str,
) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(generator),
        "--spec",
        str(spec_path),
        "--manifest",
        str(manifest_path),
        "--single-input",
        str(input_path),
        "--single-output",
        str(output_path),
        "--opaque-id",
        opaque_id,
        "--dependency-root",
        str(root),
    ]
    try:
        return subprocess.run(
            command, capture_output=True, text=True, timeout=180
        )
    except subprocess.TimeoutExpired:
        core.fail(
            "generator_infrastructure",
            "single-instance generator timed out",
            opaque_id,
        )


def verify_opaque_rename(
    spec: Mapping[str, Any],
    manifest: Mapping[str, Any],
    spec_path: Path,
    manifest_path: Path,
    generator: Path,
    root: Path,
) -> dict[str, Any]:
    rename = manifest["opaque_id_renaming_control"]
    controls = {
        control["opaque_id"]: control for control in manifest["controls"]
    }
    source = controls[rename["source_opaque_id"]]
    renamed_id = rename["renamed_opaque_id"]
    with tempfile.TemporaryDirectory(prefix="cyz0015-opaque-") as temp:
        directory = Path(temp)
        input_path = directory / "input.json"
        source_path = directory / "source.json"
        renamed_path = directory / "renamed.json"
        core.write_canonical_json(input_path, source["input"])
        first = _run_single_generator(
            generator,
            spec_path,
            manifest_path,
            root,
            input_path,
            source_path,
            source["opaque_id"],
        )
        second = _run_single_generator(
            generator,
            spec_path,
            manifest_path,
            root,
            input_path,
            renamed_path,
            renamed_id,
        )
        for identifier, process in (
            (source["opaque_id"], first),
            (renamed_id, second),
        ):
            if process.returncode in {1, 3} or process.returncode < 0:
                core.fail(
                    "generator_infrastructure",
                    f"single generator infrastructure failure for "
                    f"{identifier}; exit={process.returncode}: "
                    f"{process.stderr.strip()}",
                    identifier,
                )
            if process.returncode != 0:
                generator_error = _structured_generator_error(process)
                if process.returncode != 2 or generator_error is None:
                    core.fail(
                        "generator_infrastructure",
                        "single generator did not return the structured "
                        f"semantic-error protocol for {identifier}",
                        identifier,
                    )
                core.fail(
                    "opaque_id_isomorphism",
                    f"single generator semantically rejected {identifier}: "
                    f"{generator_error}",
                    identifier,
                )
        source_payload = core.load_json(source_path)
        renamed_payload = core.load_json(renamed_path)
        verify_single_payload(
            source_payload,
            spec,
            manifest,
            root,
            source["opaque_id"],
            source["input"],
        )
        verify_single_payload(
            renamed_payload,
            spec,
            manifest,
            root,
            renamed_id,
            source["input"],
        )
        normalized_source = copy.deepcopy(source_payload)
        normalized_renamed = copy.deepcopy(renamed_payload)
        normalized_source["instance"]["opaque_id"] = "__opaque__"
        normalized_renamed["instance"]["opaque_id"] = "__opaque__"
        if normalized_source != normalized_renamed:
            core.fail(
                "opaque_id_isomorphism",
                "opaque-ID rename changed a semantic or certificate field",
                renamed_id,
            )
        return {
            "status": "PASS",
            "source_opaque_id": source["opaque_id"],
            "renamed_opaque_id": renamed_id,
            "normalized_payload_sha256": core.canonical_sha256(
                normalized_source
            ),
        }


def verify_full(
    artifact_path: Path,
    spec_path: Path,
    manifest_path: Path,
    generator: Path,
    root: Path,
    patch: Mapping[str, Any] | None = None,
    patch_role: str | None = None,
    regenerate: bool = True,
    verify_rename: bool = True,
) -> dict[str, Any]:
    spec = copy.deepcopy(core.load_json(spec_path))
    manifest = copy.deepcopy(core.load_json(manifest_path))
    artifact = copy.deepcopy(core.load_json(artifact_path))
    mutation = patch.get("mutation") if patch else None
    target = patch.get("target") if patch else None
    if target == "spec":
        apply_spec_patch(spec, mutation)
    elif target == "manifest":
        apply_manifest_patch(manifest, mutation)
    elif target == "artifact":
        apply_artifact_patch(artifact, mutation)
    elif target not in {None, "model"}:
        core.fail("unknown_patch", f"unknown patch target {target}")
    if patch and patch.get("rebind_documents"):
        refresh_untrusted_document_bindings(spec, manifest, artifact)

    core.verify_constructor_spec(spec)
    core.verify_control_manifest(spec, manifest)
    _artifact_schema_check(spec, manifest, artifact)
    core.verify_dependency_bindings(spec, artifact, root)
    regeneration = (
        _external_regeneration(
            generator, spec_path, manifest_path, root, artifact
        )
        if regenerate
        else {"skipped": True}
    )
    role_map = controls_by_role(manifest)
    controls = {
        control["opaque_id"]: control for control in manifest["controls"]
    }
    records = {
        record["opaque_id"]: record for record in artifact["instances"]
    }
    if len(records) != len(artifact["instances"]) or set(records) != set(
        controls
    ):
        core.fail(
            "instance_coverage",
            "artifact/manifest instance IDs differ or are duplicated",
        )
    if patch_role is not None and patch_role not in role_map:
        core.fail("patch_role", f"unknown patch role {patch_role}")
    selected = (
        [role_map[patch_role]]
        if patch_role is not None
        else list(manifest["controls"])
    )
    summaries: dict[str, Any] = {}
    for control in selected:
        opaque_id = control["opaque_id"]
        model_patch = patch if target == "model" else None
        expanded, counts = _rebuild_record(
            spec,
            manifest,
            records[opaque_id],
            opaque_id,
            control["input"],
            model_patch,
            control,
        )
        summaries[opaque_id] = counts
        del expanded
        gc.collect()

    rename_result = (
        verify_opaque_rename(
            spec,
            manifest,
            spec_path,
            manifest_path,
            generator,
            root,
        )
        if verify_rename and patch is None
        else {"skipped": True}
    )
    return {
        "status": "PASS",
        "artifact_payload_sha256": core.canonical_sha256(artifact),
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
        "summaries": summaries,
        "opaque_rename": rename_result,
        "regeneration": regeneration,
    }
