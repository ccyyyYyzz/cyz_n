#!/usr/bin/env python3
"""Live, isolated negative-test suite for the Brief 0015 certificate."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import verifier_core as core
import verifier_replay as replay
import verifier_replay_runtime as runtime


# name, target, report role (when a model is patched), accepted error codes
MUTATIONS: list[tuple[str, str, str | None, set[str]]] = [
    ("change_row_probability", "model", "three_large_metric_control", {"row_sum"}),
    ("delete_state_row", "model", "three_large_metric_control", {"row_coverage"}),
    ("delete_schedule_row", "model", "three_large_metric_control", {"schedule_coverage"}),
    ("ghost_mark_id", "model", "three_large_metric_control", {"dangling_mark", "event_id"}),
    ("ghost_destination_id", "model", "three_large_metric_control", {"dangling_destination"}),
    ("change_reverse_event_id", "model", "three_large_metric_control", {"reverse_link"}),
    ("change_system_energy_quantum", "model", "three_large_metric_control", {"energy_ledger"}),
    ("change_charge_quantum", "model", "three_large_metric_control", {"charge_ledger"}),
    ("null_history_physical_jump", "model", "three_large_metric_control", {"energy_ledger", "null_projection"}),
    ("alter_age_hold", "model", "three_large_metric_control", {"scheduled_clock", "event_schedule"}),
    ("replace_scheduled_by_poisson", "model", "three_large_metric_control", {"scheduled_semantics"}),
    ("remove_cemetery_states", "model", "velocity_invalid", {"dangling_destination", "row_coverage", "schedule_coverage"}),
    ("remove_source_validity_routing", "model", "velocity_invalid", {"source_validity_routing"}),
    ("killed_payload", "model", "velocity_invalid", {"killed_payload"}),
    ("killed_ledger", "model", "velocity_invalid", {"energy_ledger", "killed_payload"}),
    ("killed_reason", "model", "velocity_invalid", {"state_id", "killed_reason"}),
    ("killed_absorbing_row", "model", "velocity_invalid", {"killed_absorbing_row"}),
    ("frame_arity_without_regeneration", "model", "arity_two_semantic_control", {"frame_arity_control", "expanded_hash", "control_obligation"}),
    ("hidden_count_if_three", "spec", None, {"registered_spec_hash"}),
    ("hidden_fraction_branch", "spec", None, {"registered_spec_hash"}),
    ("hidden_count_alias", "spec", None, {"registered_spec_hash"}),
    ("hidden_registry_three", "spec", None, {"registered_spec_hash"}),
    ("hidden_environment_global", "spec", None, {"registered_spec_hash"}),
    ("hidden_post_rank_override", "spec", None, {"registered_spec_hash"}),
    ("unregistered_constitutive_branch", "spec", None, {"registered_spec_hash"}),
    ("opaque_label_branch", "spec", None, {"registered_spec_hash"}),
    ("remove_s9_generators", "spec", None, {"registered_spec_hash"}),
    ("corrupt_s9_generator", "spec", None, {"registered_spec_hash"}),
    ("precedence_changed", "spec", None, {"registered_spec_hash"}),
    ("interval_closure_changed", "spec", None, {"registered_spec_hash"}),
    ("reverse_relabel_detailed_balance", "spec", None, {"registered_spec_hash"}),
    ("ctmc_process_type", "spec", None, {"registered_spec_hash"}),
    ("operation_empty_params", "spec", None, {"registered_spec_hash"}),
    ("record_schema_event_field_removed", "spec", None, {"registered_spec_hash"}),
    ("parameter_influence_probability_removed", "spec", None, {"registered_spec_hash"}),
    ("id_grammar_changed", "spec", None, {"registered_spec_hash"}),
    ("semantic_dependencies_removed", "spec", None, {"registered_spec_hash"}),
    ("output_record_schema_substituted", "spec", None, {"registered_spec_hash"}),
    ("constitutive_rule_text_rebound", "spec", None, {"registered_spec_hash"}),
    ("semantic_rule_retargeted_rebound", "spec", None, {"registered_spec_hash"}),
    ("contract_id_rebound", "spec", None, {"registered_spec_hash"}),
    ("param_record_order_id_rebound", "spec", None, {"registered_spec_hash"}),
    ("parameter_influence_values_rebound", "spec", None, {"registered_spec_hash"}),
    ("constructor_node_id_or_input_rebound", "spec", None, {"registered_spec_hash"}),
    ("semantic_contract_components_rebound", "spec", None, {"registered_spec_hash"}),
    ("must_consume_rebound", "spec", None, {"registered_spec_hash"}),
    ("mark_include_central_disabled", "spec", None, {"registered_spec_hash"}),
    ("mark_signed_basis_disabled", "spec", None, {"registered_spec_hash"}),
    ("probability_formula_zeroed", "spec", None, {"registered_spec_hash"}),
    ("destination_rule_rebound", "spec", None, {"registered_spec_hash"}),
    ("history_rule_rebound", "spec", None, {"registered_spec_hash"}),
    ("reverse_rule_rebound", "spec", None, {"registered_spec_hash"}),
    ("ledger_rule_rebound", "spec", None, {"registered_spec_hash"}),
    ("s9_joint_action_disabled", "spec", None, {"registered_spec_hash"}),
    ("input_schema_descriptor_changed", "spec", None, {"registered_spec_hash"}),
    ("dependency_declaration_empty", "spec", None, {"registered_spec_hash"}),
    ("dependency_declaration_duplicate", "spec", None, {"registered_spec_hash"}),
    ("dependency_declaration_traversal", "spec", None, {"registered_spec_hash"}),
    ("dependency_declaration_absolute", "spec", None, {"registered_spec_hash"}),
    ("dependency_declaration_backslash", "spec", None, {"registered_spec_hash"}),
    ("manifest_controls_empty", "manifest", None, {"registered_manifest_hash"}),
    ("manifest_obligations_empty", "manifest", None, {"registered_manifest_hash"}),
    ("manifest_obligations_extra", "manifest", None, {"registered_manifest_hash"}),
    ("manifest_rename_source_missing", "manifest", None, {"registered_manifest_hash"}),
    ("manifest_role_duplicate", "manifest", None, {"registered_manifest_hash"}),
    ("manifest_spec_binding_changed", "manifest", None, {"registered_manifest_hash"}),
    ("executable_dependency_file", "artifact", None, {"dependency_set"}),
    ("executable_dependency_hash", "artifact", None, {"dependency_hash"}),
    ("dependency_set_addition", "artifact", None, {"dependency_set"}),
    ("artifact_interpretation_mode", "artifact", None, {"artifact_schema"}),
    ("artifact_dependency_inventory_removed", "artifact", None, {"artifact_schema"}),
    ("artifact_consumed_trace_added", "artifact", None, {"instance_schema"}),
    ("artifact_instance_input_changed", "artifact", None, {"instance_binding"}),
    ("input_frame_arity_float", "input", None, {"input_type"}),
    ("input_frame_arity_string", "input", None, {"input_type"}),
    ("input_frame_arity_bool", "input", None, {"input_type"}),
    ("input_dilute_string", "input", None, {"input_type"}),
    ("input_separation_zero", "input", None, {"input_type"}),
    ("input_separation_negative", "input", None, {"input_type"}),
    ("input_coupling_negative", "input", None, {"input_type"}),
    ("input_metric_radius_zero", "input", None, {"input_type"}),
    ("input_relative_speed_zero", "input", None, {"input_type"}),
    ("input_unknown_enum", "input", None, {"input_type"}),
    ("input_noncanonical_fraction", "input", None, {"fraction"}),
    ("input_metric_short", "input", None, {"input_type"}),
    ("input_missing_field", "input", None, {"control_unregistered_field"}),
    ("input_forbidden_rank", "input", None, {"control_unregistered_field"}),
    ("input_speed_order", "input", None, {"speed_input"}),
    ("hardcoded_triple_generator", "source", None, {"generator_regeneration"}),
    ("hardcoded_triple_verifier", "source", None, {"frame_arity", "frame_arity_control", "expanded_hash", "control_obligation"}),
    ("opaque_generator_label_branch", "source", None, {"instance_binding", "opaque_id_isomorphism"}),
    ("dependency_shadowed_import", "source", None, {"loaded_source"}),
    ("dependency_extra_local_helper", "source", None, {"dependency_set"}),
    ("single_missing_dependency_inventory", "single", None, {"single_artifact_schema"}),
]


REBIND_DOCUMENT_MUTATIONS = {
    "constitutive_rule_text_rebound",
    "semantic_rule_retargeted_rebound",
    "contract_id_rebound",
    "param_record_order_id_rebound",
    "parameter_influence_values_rebound",
    "constructor_node_id_or_input_rebound",
    "semantic_contract_components_rebound",
    "must_consume_rebound",
}


def mutation_definition(
    name: str,
) -> tuple[str, str, str | None, set[str]]:
    for definition in MUTATIONS:
        if definition[0] == name:
            return definition
    core.fail("unknown_mutation", f"unknown hostile mutation {name}", name)


def _parse_child(process: subprocess.CompletedProcess[str]) -> Mapping[str, Any] | None:
    for stream in (process.stdout, process.stderr):
        for line in reversed(stream.splitlines()):
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, Mapping):
                return parsed
    return None


def _observed_error(parsed: Mapping[str, Any] | None) -> Mapping[str, Any]:
    if not isinstance(parsed, Mapping):
        return {}
    error = parsed.get("error")
    if isinstance(error, Mapping):
        return error
    if isinstance(parsed.get("code"), str):
        return {
            "code": parsed["code"],
            "message": parsed.get("message", ""),
            "location": "",
        }
    return {}


def _child_record(
    name: str,
    target: str,
    process: subprocess.CompletedProcess[str],
) -> dict[str, Any]:
    parsed = _parse_child(process)
    return {
        "mutation": name,
        "target": target,
        "exit_code": process.returncode,
        "protocol_status": (
            parsed.get("status") if isinstance(parsed, Mapping) else None
        ),
        "observed_error": dict(_observed_error(parsed)),
        "stdout_sha256": hashlib.sha256(
            process.stdout.encode("utf-8")
        ).hexdigest(),
        "stderr_sha256": hashlib.sha256(
            process.stderr.encode("utf-8")
        ).hexdigest(),
    }


def _require_rejection(
    record: Mapping[str, Any], expected_codes: set[str], name: str
) -> dict[str, Any]:
    code = record.get("observed_error", {}).get("code")
    if (
        record.get("exit_code") != 2
        or record.get("protocol_status") != "ERROR"
        or code not in expected_codes
    ):
        core.fail(
            "hostile_infrastructure",
            f"{name} did not produce the required semantic rejection; "
            f"exit={record.get('exit_code')} status="
            f"{record.get('protocol_status')} code={code}",
            name,
        )
    checked = dict(record)
    checked["expected_codes"] = sorted(expected_codes)
    checked["localized_rejection"] = True
    return checked


def _run(
    command: list[str],
    timeout: int,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=dict(environment) if environment is not None else None,
        )
    except subprocess.TimeoutExpired:
        core.fail(
            "hostile_infrastructure",
            f"hostile child timed out after {timeout}s",
        )


def _standard_mutation(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
    verifier: Path,
    name: str,
    target: str,
    role: str | None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"cyz0015-{name}-") as temp:
        patch_path = Path(temp) / "patch.json"
        core.write_canonical_json(
            patch_path,
            {
                "mutation": name,
                "target": target,
                "rebind_documents": name in REBIND_DOCUMENT_MUTATIONS,
            },
        )
        command = [
            sys.executable,
            str(verifier),
            "--artifact",
            str(artifact),
            "--spec",
            str(spec),
            "--manifest",
            str(manifest),
            "--generator",
            str(generator),
            "--dependency-root",
            str(root),
            "--patch",
            str(patch_path),
            "--skip-regeneration",
            "--skip-rename",
        ]
        if role is not None:
            command.extend(["--patch-role", role])
        process = _run(command, 240)
        return _child_record(name, target, process)


def _mutated_input(
    manifest: Mapping[str, Any], name: str
) -> dict[str, Any]:
    vector = copy.deepcopy(manifest["controls"][0]["input"])
    if name == "input_frame_arity_float":
        vector["frame_arity"] = 2.9
    elif name == "input_frame_arity_string":
        vector["frame_arity"] = "2"
    elif name == "input_frame_arity_bool":
        vector["frame_arity"] = True
    elif name == "input_dilute_string":
        vector["dilute_flag"] = "false"
    elif name == "input_separation_zero":
        vector["separation_fraction"] = "0/1"
    elif name == "input_separation_negative":
        vector["separation_fraction"] = "-1/1"
    elif name == "input_coupling_negative":
        vector["coupling"] = "-1/1"
    elif name == "input_metric_radius_zero":
        vector["metric_radii"][0] = "0/1"
    elif name == "input_relative_speed_zero":
        vector["relative_speed"] = "0/1"
    elif name == "input_unknown_enum":
        vector["source_registry_id"] = "unknown"
    elif name == "input_noncanonical_fraction":
        vector["speed_min"] = "01/2"
    elif name == "input_metric_short":
        vector["metric_radii"].pop()
    elif name == "input_missing_field":
        vector.pop("frame_arity")
    elif name == "input_forbidden_rank":
        vector["rank"] = 3
    elif name == "input_speed_order":
        vector["speed_min"] = vector["speed_max"]
    else:
        core.fail("unknown_mutation", f"unknown input mutation {name}")
    return vector


def _input_mutation(
    root: Path,
    spec: Path,
    manifest_path: Path,
    generator: Path,
    verifier: Path,
    name: str,
    expected_codes: set[str],
) -> dict[str, Any]:
    manifest = core.load_json(manifest_path)
    vector = _mutated_input(manifest, name)
    with tempfile.TemporaryDirectory(prefix=f"cyz0015-{name}-") as temp:
        directory = Path(temp)
        input_path = directory / "input.json"
        output_path = directory / "single.json"
        core.write_canonical_json(input_path, vector)
        verifier_process = _run(
            [
                sys.executable,
                str(verifier),
                "--input-worker",
                str(input_path),
                "--spec",
                str(spec),
                "--dependency-root",
                str(root),
            ],
            60,
        )
        generator_process = _run(
            [
                sys.executable,
                str(generator),
                "--single-input",
                str(input_path),
                "--single-output",
                str(output_path),
                "--manifest",
                str(manifest_path),
                "--spec",
                str(spec),
                "--dependency-root",
                str(root),
            ],
            60,
        )
        verifier_record = _require_rejection(
            _child_record(name, "verifier_input", verifier_process),
            expected_codes,
            name,
        )
        generator_record = _require_rejection(
            _child_record(name, "generator_input", generator_process),
            {"generator_construction_error"},
            name,
        )
        return {
            "mutation": name,
            "target": "input",
            "children": {
                "generator": generator_record,
                "verifier": verifier_record,
            },
            "localized_rejection": True,
        }


def _copy_registered_tree(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    target: Path,
) -> tuple[Path, Path, Path, Path, Path]:
    spec_object = core.load_json(spec)
    relative_files = [
        "artifacts/0015/constructor_spec.json",
        "artifacts/0015/control_vector_manifest.json",
        "artifacts/0015/scheduled_kernel.json",
        *spec_object["executable_dependencies"],
    ]
    for relative in relative_files:
        source = (
            artifact
            if relative == "artifacts/0015/scheduled_kernel.json"
            else manifest
            if relative == "artifacts/0015/control_vector_manifest.json"
            else spec
            if relative == "artifacts/0015/constructor_spec.json"
            else root.joinpath(*PurePosixPath(relative).parts)
        )
        destination = target.joinpath(*PurePosixPath(relative).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    directory = target / "artifacts" / "0015"
    return (
        directory / "scheduled_kernel.json",
        directory / "constructor_spec.json",
        directory / "control_vector_manifest.json",
        directory / "generate_0015.py",
        directory / "verify_0015.py",
    )


def _refresh_dependency_hash(
    artifact: Path, target_root: Path, source: Path
) -> None:
    payload = core.load_json(artifact)
    relative = source.relative_to(target_root).as_posix()
    for record in payload["executable_dependencies"]:
        if record["path"] == relative:
            record["normalized_lf_sha256"] = core.normalized_lf_sha256(
                source
            )
            core.write_canonical_json(artifact, payload)
            return
    core.fail("mutation_setup", f"mutated source is not registered: {relative}")


def _source_mutation(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    name: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"cyz0015-{name}-") as temp:
        target_root = Path(temp) / "repo"
        (
            target_artifact,
            target_spec,
            target_manifest,
            target_generator,
            target_verifier,
        ) = _copy_registered_tree(
            root, artifact, spec, manifest, target_root
        )
        options = [
            "--baseline",
            "--skip-covariance",
            "--artifact",
            str(target_artifact),
            "--spec",
            str(target_spec),
            "--manifest",
            str(target_manifest),
            "--generator",
            str(target_generator),
            "--dependency-root",
            str(target_root),
        ]
        if name == "hardcoded_triple_generator":
            source = target_root / "artifacts/0015/generator_model.py"
            text = source.read_text(encoding="utf-8")
            needle = "a=v['frame_arity']"
            if needle not in text:
                core.fail("mutation_setup", f"needle missing in {source}")
            source.write_text(
                text.replace(
                    needle,
                    "a=3",
                    1,
                ),
                encoding="utf-8",
            )
            _refresh_dependency_hash(target_artifact, target_root, source)
            options.append("--skip-rename")
        elif name == "hardcoded_triple_verifier":
            source = target_root / "artifacts/0015/verifier_model.py"
            text = source.read_text(encoding="utf-8")
            needle = 'arity = vector["frame_arity"]'
            if needle not in text:
                core.fail("mutation_setup", f"needle missing in {source}")
            source.write_text(
                text.replace(
                    needle,
                    "arity = 3  # HOSTILE fixed triple",
                    1,
                ),
                encoding="utf-8",
            )
            _refresh_dependency_hash(target_artifact, target_root, source)
            options.extend(["--skip-regeneration", "--skip-rename"])
        elif name == "opaque_generator_label_branch":
            source = target_root / "artifacts/0015/generator_artifact.py"
            text = source.read_text(encoding="utf-8")
            needle = (
                "    return {\n"
                '        "opaque_id": opaque_id,\n'
                "        **_semantic_instance_record(spec, manifest, vector),\n"
                "    }"
            )
            replacement = (
                "    if 'three' in opaque_id.lower():\n"
                "        vector = dict(vector)\n"
                "        vector['frame_arity'] = 2\n"
                "    return {\n"
                '        "opaque_id": opaque_id,\n'
                "        **_semantic_instance_record(spec, manifest, vector),\n"
                "    }"
            )
            if needle not in text:
                core.fail("mutation_setup", f"needle missing in {source}")
            source.write_text(
                text.replace(needle, replacement, 1),
                encoding="utf-8",
            )
            _refresh_dependency_hash(target_artifact, target_root, source)
        elif name == "dependency_shadowed_import":
            shadow = target_root / "shadow"
            shadow.mkdir()
            shutil.copyfile(
                target_root / "artifacts/0015/verifier_model.py",
                shadow / "verifier_model.py",
            )
            script = (
                "import sys;"
                f"sys.path[:0]=[{str(shadow)!r},"
                f"{str(target_root / 'artifacts/0015')!r}];"
                "import verifier_model;"
                "import verify_0015;"
                f"raise SystemExit(verify_0015.main({options!r}))"
            )
            process = _run([sys.executable, "-c", script], 120)
            return _child_record(name, "source", process)
        elif name == "dependency_extra_local_helper":
            helper = target_root / "artifacts/0015/json.py"
            helper.write_text(
                "raise RuntimeError('stdlib shadow executed before phase 0')\n",
                encoding="utf-8",
            )
            options.extend(["--skip-regeneration", "--skip-rename"])
        else:
            core.fail("unknown_mutation", f"unknown source mutation {name}")
        process = _run([sys.executable, str(target_verifier), *options], 360)
        return _child_record(name, "source", process)


def _single_schema_mutation(
    root: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
    verifier: Path,
    name: str,
) -> dict[str, Any]:
    manifest_object = core.load_json(manifest)
    vector = manifest_object["controls"][0]["input"]
    with tempfile.TemporaryDirectory(prefix=f"cyz0015-{name}-") as temp:
        directory = Path(temp)
        input_path = directory / "input.json"
        output_path = directory / "single.json"
        core.write_canonical_json(input_path, vector)
        generated = _run(
            [
                sys.executable,
                str(generator),
                "--single-input",
                str(input_path),
                "--single-output",
                str(output_path),
                "--spec",
                str(spec),
                "--manifest",
                str(manifest),
                "--dependency-root",
                str(root),
            ],
            120,
        )
        if generated.returncode != 0:
            core.fail(
                "mutation_setup",
                f"could not generate single artifact for {name}",
            )
        payload = core.load_json(output_path)
        if name == "single_missing_dependency_inventory":
            payload.pop("executable_dependencies")
        else:
            core.fail("unknown_mutation", f"unknown single mutation {name}")
        core.write_canonical_json(output_path, payload)
        process = _run(
            [
                sys.executable,
                str(verifier),
                "--single-artifact",
                str(output_path),
                "--spec",
                str(spec),
                "--manifest",
                str(manifest),
                "--dependency-root",
                str(root),
            ],
            120,
        )
        return _child_record(name, "single", process)


def run_named_mutation(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
    verifier: Path,
    name: str,
) -> dict[str, Any]:
    mutation, target, role, expected = mutation_definition(name)
    if target in {"model", "spec", "manifest", "artifact"}:
        record = _standard_mutation(
            root,
            artifact,
            spec,
            manifest,
            generator,
            verifier,
            mutation,
            target,
            role,
        )
        return _require_rejection(record, expected, mutation)
    if target == "input":
        return _input_mutation(
            root,
            spec,
            manifest,
            generator,
            verifier,
            mutation,
            expected,
        )
    if target == "source":
        record = _source_mutation(
            root, artifact, spec, manifest, mutation
        )
        return _require_rejection(record, expected, mutation)
    if target == "single":
        record = _single_schema_mutation(
            root, spec, manifest, generator, verifier, mutation
        )
        return _require_rejection(record, expected, mutation)
    core.fail("unknown_mutation", f"unsupported target {target}", mutation)


def _certificate_component(
    payload: Mapping[str, Any],
    role: str,
    generation_sha256: str,
) -> dict[str, Any]:
    """Mark a side report as evidence that is never a standalone certificate."""
    reserved = {
        "certificate_component_schema_version",
        "certificate_component_role",
        "certificate_generation_sha256",
        "component_acceptance_rule",
        "not_a_certificate",
    }
    if set(payload) & reserved:
        core.fail(
            "report_component",
            f"component payload collides with reserved metadata: "
            f"{sorted(set(payload) & reserved)}",
            role,
        )
    if payload.get("status") != "PASS":
        core.fail(
            "report_component",
            "only successful live evidence may be published as a component",
            role,
        )
    return {
        **payload,
        "certificate_component_schema_version": (
            "cyz-0015-certificate-component-v1"
        ),
        "certificate_component_role": role,
        "certificate_generation_sha256": generation_sha256,
        "component_acceptance_rule": (
            "valid_only_when_its_canonical_hash_is_committed_by_the_"
            "matching_generation_PASS_verification_report"
        ),
        "not_a_certificate": True,
    }


def hostile_report(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
    verifier: Path,
) -> dict[str, Any]:
    """Execute all evidence now; no prewritten report is accepted as input."""
    baseline = runtime.baseline_check(
        root,
        artifact,
        spec,
        manifest,
        generator,
        verifier,
        skip_covariance=False,
    )
    portability = runtime.portability_check(
        root, artifact, spec, manifest, generator
    )

    observations = [
        run_named_mutation(
            root,
            artifact,
            spec,
            manifest,
            generator,
            verifier,
            name,
        )
        for name, _, _, _ in MUTATIONS
    ]
    bindings = {
        "artifact_payload_sha256": core.canonical_sha256(
            core.load_json(artifact)
        ),
        "constructor_spec_sha256": core.REGISTERED_SPEC_SHA256,
        "semantic_contract_sha256": (
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256
        ),
        "control_vector_manifest_sha256": (
            core.REGISTERED_MANIFEST_SHA256
        ),
    }
    raw_observation_document = {
        "schema_version": "cyz-0015-live-hostile-observations-v3",
        "status": "PASS",
        "execution_policy": (
            "fresh_subprocess_exit_2_and_VerificationError_required"
        ),
        "mutation_count": len(observations),
        "mutations": observations,
        **bindings,
    }
    spec_object = core.load_json(spec)
    inventory = core.dependency_inventory(spec_object, root)
    generation_payload = {
        "artifact_payload_sha256": bindings["artifact_payload_sha256"],
        "constructor_spec_sha256": bindings["constructor_spec_sha256"],
        "semantic_contract_sha256": bindings[
            "semantic_contract_sha256"
        ],
        "control_vector_manifest_sha256": bindings[
            "control_vector_manifest_sha256"
        ],
        "source_hashes": {
            row["path"]: row["normalized_lf_sha256"]
            for row in inventory
        },
    }
    generation_sha256 = core.canonical_sha256(generation_payload)
    baseline = _certificate_component(
        baseline, "baseline", generation_sha256
    )
    portability = _certificate_component(
        portability, "portability", generation_sha256
    )
    observation_document = _certificate_component(
        raw_observation_document,
        "hostile_observations",
        generation_sha256,
    )
    return {
        "schema_version": "cyz-0015-live-verification-report-v3",
        "status": "PASS",
        "evidence_execution": "performed_during_this_report_invocation",
        "prewritten_observations_accepted": False,
        "all_mandated_mutations_rejected": True,
        "mutation_count": len(observations),
        "baseline": baseline,
        "portability": portability,
        "hostile_observations": observation_document,
        "baseline_payload_sha256": core.canonical_sha256(baseline),
        "portability_payload_sha256": core.canonical_sha256(portability),
        "hostile_observations_sha256": core.canonical_sha256(
            observation_document
        ),
        "component_acceptance_policy": (
            "components_are_not_certificates_and_require_matching_"
            "generation_hashes_committed_by_this_PASS_report"
        ),
        "freshness_requires_live_generation_recomputation": True,
        "report_trust_boundary": (
            "stored_execution_record_under_trusted_repository_provenance;"
            "rerun_report_for_independent_live_evidence"
        ),
        "source_hashes": generation_payload["source_hashes"],
        "certificate_generation_sha256": generation_sha256,
        **bindings,
    }
