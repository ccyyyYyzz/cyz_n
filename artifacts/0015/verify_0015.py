#!/usr/bin/env python3
"""Independent CLI verifier for the fixed registered Brief 0015 contract."""
from __future__ import annotations

import sys

# Direct script execution prepends artifacts/0015 to sys.path. Remove that
# untrusted entry before importing even the standard library, so an added
# json.py/pathlib.py/etc. cannot execute ahead of the report sentinel.
if (
    __name__ == "__main__"
    and sys.path
    and not sys.flags.safe_path
):
    _SCRIPT_PATH_ENTRY = sys.path.pop(0)
    sys.path[:] = [
        entry
        for entry in sys.path
        if entry and entry != _SCRIPT_PATH_ENTRY
    ]

import argparse
import importlib.util
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


PHASE0_REGISTERED_DEPENDENCIES = (
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
PHASE0_REGISTERED_DOCUMENTS = (
    "artifacts/0015/scheduled_kernel.json",
    "artifacts/0015/constructor_spec.json",
    "artifacts/0015/control_vector_manifest.json",
)

core: Any = None
hostile: Any = None
model: Any = None
replay: Any = None
runtime: Any = None
semantics: Any = None


class BootstrapError(RuntimeError):
    """Safe report-start failure before verifier modules are imported."""

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


def _load_runtime_modules() -> None:
    global core, hostile, model, replay, runtime, semantics
    if core is not None:
        return
    module_directory = Path(__file__).resolve().parent
    sys.path[:] = [
        entry
        for entry in sys.path
        if entry
        and not _paths_alias(Path(entry), module_directory)
    ]

    loaded_new: list[tuple[str, Any]] = []

    def load_exact(name: str) -> Any:
        expected = (module_directory / f"{name}.py").resolve()
        present = sys.modules.get(name)
        if present is not None:
            present_file = getattr(present, "__file__", None)
            if present_file is None or not _paths_alias(
                Path(present_file), expected
            ):
                raise BootstrapError(
                    "loaded_source",
                    f"preloaded module {name} is not the registered file",
                    str(present_file or ""),
                )
            return present
        module_spec = importlib.util.spec_from_file_location(name, expected)
        if module_spec is None or module_spec.loader is None:
            raise BootstrapError(
                "loaded_source",
                f"cannot create exact module specification for {name}",
                str(expected),
            )
        loaded = importlib.util.module_from_spec(module_spec)
        sys.modules[name] = loaded
        loaded_new.append((name, loaded))
        module_spec.loader.exec_module(loaded)
        return loaded

    try:
        loaded_core = load_exact("verifier_core")
        loaded_model = load_exact("verifier_model")
        loaded_semantics = load_exact("verifier_semantics")
        loaded_replay = load_exact("verifier_replay")
        loaded_runtime = load_exact("verifier_replay_runtime")
        loaded_hostile = load_exact("verifier_hostile")
    except Exception:
        for name, loaded in reversed(loaded_new):
            if sys.modules.get(name) is loaded:
                del sys.modules[name]
        raise
    (
        core,
        hostile,
        model,
        replay,
        runtime,
        semantics,
    ) = (
        loaded_core,
        loaded_hostile,
        loaded_model,
        loaded_replay,
        loaded_runtime,
        loaded_semantics,
    )


def _compact(value: Mapping[str, Any]) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def _emit(value: Mapping[str, Any]) -> None:
    try:
        print(_compact(value))
    except (BrokenPipeError, OSError, UnicodeError):
        # Once a report commit marker is durable, an unavailable stdout must
        # not turn a successful certificate publication into exit 3.
        pass


def _phase0_write_canonical_json_atomic(path: Path, value: Any) -> None:
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
            handle.write(
                json.dumps(
                    value,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode("utf-8")
                + b"\n"
            )
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _paths_alias(left: Path, right: Path) -> bool:
    left = Path(left)
    right = Path(right)
    if left.resolve() == right.resolve():
        return True
    try:
        return left.exists() and right.exists() and os.path.samefile(left, right)
    except OSError:
        return False


def _registered_paths(root: Path) -> list[Path]:
    return [
        root / Path(*relative.split("/"))
        for relative in (
            *PHASE0_REGISTERED_DEPENDENCIES,
            *PHASE0_REGISTERED_DOCUMENTS,
        )
    ]


def _certificate_generation(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
) -> tuple[str, dict[str, Any]]:
    spec_object = core.load_json(spec)
    manifest_object = core.load_json(manifest)
    core.verify_constructor_spec(spec_object)
    core.verify_control_manifest(spec_object, manifest_object)
    inventory = core.dependency_inventory(spec_object, root)
    payload = {
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
        "source_hashes": {
            row["path"]: row["normalized_lf_sha256"]
            for row in inventory
        },
    }
    return core.canonical_sha256(payload), payload


def _report_paths(args: argparse.Namespace, root: Path) -> list[Path]:
    paths = [
        Path(args.report).resolve(),
        Path(args.baseline_output).resolve(),
        Path(args.portability_output).resolve(),
        Path(args.observations_output).resolve(),
    ]
    for index, left in enumerate(paths):
        for right in paths[index + 1 :]:
            if _paths_alias(left, right):
                raise BootstrapError(
                    "report_output",
                    "report output paths must be distinct",
                )
    if args.record is not None:
        raise BootstrapError(
            "report_output",
            "--record is forbidden during certificate publication",
        )
    protected = _registered_paths(root)
    protected.extend(
        Path(path)
        for path in (
            args.artifact,
            args.spec,
            args.manifest,
            args.generator,
        )
    )
    for output in paths:
        for registered in protected:
            if _paths_alias(output, registered):
                raise BootstrapError(
                    "report_output",
                    "report output aliases a registered or active input",
                    str(output),
                )
    return paths


def _validate_record_path(
    args: argparse.Namespace,
    root: Path,
    report_paths: Sequence[Path] | None,
) -> None:
    if args.record is None:
        return
    record = Path(args.record).resolve()
    protected = _registered_paths(root)
    active_names = [
        "artifact",
        "spec",
        "manifest",
        "generator",
        "patch",
        "check_report",
        "single_artifact",
        "input_worker",
    ]
    if getattr(args, "check_report", None) is not None:
        active_names.extend(
            [
                "baseline_output",
                "portability_output",
                "observations_output",
            ]
        )
    for name in active_names:
        value = getattr(args, name, None)
        if value is not None:
            protected.append(Path(value))
    if report_paths is not None:
        protected.extend(report_paths)
    for path in protected:
        if _paths_alias(record, path):
            core.fail(
                "record_output",
                "--record may not alias any registered or active input",
                str(record),
            )


def _mark_report_generation_in_progress(
    paths: Sequence[Path],
    generation_sha256: str | None,
) -> None:
    sentinel = {
        "schema_version": "cyz-0015-report-generation-sentinel-v1",
        "status": "IN_PROGRESS",
        "not_a_certificate": True,
        "certificate_generation_sha256": generation_sha256,
        "phase": (
            "live_evidence"
            if generation_sha256 is not None
            else "validating_generation"
        ),
    }
    for path in paths:
        _phase0_write_canonical_json_atomic(path, sentinel)


def _publish_report_generation(
    paths: Sequence[Path],
    result: Mapping[str, Any],
    expected_generation: str,
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
) -> None:
    observed_generation, _ = _certificate_generation(
        root, artifact, spec, manifest
    )
    if (
        result.get("status") != "PASS"
        or result.get("certificate_generation_sha256")
        != expected_generation
        or observed_generation != expected_generation
    ):
        core.fail(
            "report_generation_changed",
            "artifact, documents, or executable sources changed during "
            "the live report run",
        )
    report_path, baseline_path, portability_path, observations_path = paths
    component_payloads = (
        (
            baseline_path,
            result["baseline"],
            "baseline_payload_sha256",
            "baseline",
        ),
        (
            portability_path,
            result["portability"],
            "portability_payload_sha256",
            "portability",
        ),
        (
            observations_path,
            result["hostile_observations"],
            "hostile_observations_sha256",
            "hostile_observations",
        ),
    )
    for path, payload, hash_field, role in component_payloads:
        if (
            payload.get("not_a_certificate") is not True
            or payload.get("certificate_component_role") != role
            or payload.get("certificate_generation_sha256")
            != expected_generation
        ):
            core.fail(
                "report_component",
                f"component metadata mismatch: {role}",
                str(path),
            )
        core.write_canonical_json_atomic(path, payload)
        if core.canonical_sha256(core.load_json(path)) != result[hash_field]:
            core.fail(
                "report_publish",
                f"published component hash mismatch: {path}",
                str(path),
            )
    final_generation, _ = _certificate_generation(
        root, artifact, spec, manifest
    )
    if final_generation != expected_generation:
        core.fail(
            "report_generation_changed",
            "artifact, documents, or executable sources changed during "
            "report publication",
        )
    # The PASS report is the commit marker and is therefore published last.
    core.write_canonical_json_atomic(report_path, result)
    published = core.load_json(report_path)
    post_commit_generation, _ = _certificate_generation(
        root, artifact, spec, manifest
    )
    if (
        core.canonical_sha256(published) != core.canonical_sha256(result)
        or post_commit_generation != expected_generation
    ):
        _mark_report_generation_in_progress(paths, post_commit_generation)
        core.fail(
            "report_generation_changed",
            "published report or bound generation changed at commit",
        )


def _verify_published_report(
    report_path: Path,
    baseline_path: Path,
    portability_path: Path,
    observations_path: Path,
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
) -> dict[str, Any]:
    """Check stored-report freshness/consistency, not execution authenticity."""
    report = core.load_json(report_path)
    expected_fields = {
        "schema_version",
        "status",
        "evidence_execution",
        "prewritten_observations_accepted",
        "all_mandated_mutations_rejected",
        "mutation_count",
        "baseline",
        "portability",
        "hostile_observations",
        "baseline_payload_sha256",
        "portability_payload_sha256",
        "hostile_observations_sha256",
        "component_acceptance_policy",
        "freshness_requires_live_generation_recomputation",
        "report_trust_boundary",
        "source_hashes",
        "certificate_generation_sha256",
        "artifact_payload_sha256",
        "constructor_spec_sha256",
        "semantic_contract_sha256",
        "control_vector_manifest_sha256",
    }
    if not isinstance(report, Mapping) or set(report) != expected_fields:
        core.fail(
            "published_report_schema",
            "published verification report schema is not closed",
            str(report_path),
        )
    generation_sha256, generation = _certificate_generation(
        root, artifact, spec, manifest
    )
    if (
        report["schema_version"]
        != "cyz-0015-live-verification-report-v3"
        or report["status"] != "PASS"
        or report["evidence_execution"]
        != "performed_during_this_report_invocation"
        or report["prewritten_observations_accepted"] is not False
        or report["all_mandated_mutations_rejected"] is not True
        or report["mutation_count"] != len(hostile.MUTATIONS)
        or report["freshness_requires_live_generation_recomputation"]
        is not True
        or report["certificate_generation_sha256"] != generation_sha256
        or report["source_hashes"] != generation["source_hashes"]
        or report["artifact_payload_sha256"]
        != generation["artifact_payload_sha256"]
        or report["constructor_spec_sha256"]
        != generation["constructor_spec_sha256"]
        or report["semantic_contract_sha256"]
        != generation["semantic_contract_sha256"]
        or report["control_vector_manifest_sha256"]
        != generation["control_vector_manifest_sha256"]
    ):
        core.fail(
            "published_report_generation",
            "published report does not certify the current generation",
            str(report_path),
        )
    component_policy = (
        "components_are_not_certificates_and_require_matching_"
        "generation_hashes_committed_by_this_PASS_report"
    )
    if report["component_acceptance_policy"] != component_policy:
        core.fail(
            "published_report_schema",
            "component acceptance policy mismatch",
            str(report_path),
        )
    if report["report_trust_boundary"] != (
        "stored_execution_record_under_trusted_repository_provenance;"
        "rerun_report_for_independent_live_evidence"
    ):
        core.fail(
            "published_report_schema",
            "stored-report trust boundary mismatch",
            str(report_path),
        )
    component_records = (
        (
            "baseline",
            Path(baseline_path),
            "baseline_payload_sha256",
        ),
        (
            "portability",
            Path(portability_path),
            "portability_payload_sha256",
        ),
        (
            "hostile_observations",
            Path(observations_path),
            "hostile_observations_sha256",
        ),
    )
    accepted_hashes: dict[str, str] = {}
    component_rule = (
        "valid_only_when_its_canonical_hash_is_committed_by_the_"
        "matching_generation_PASS_verification_report"
    )
    for role, path, hash_field in component_records:
        component = core.load_json(path)
        expected_hash = report[hash_field]
        if (
            component != report[role]
            or core.canonical_sha256(component) != expected_hash
            or component.get("status") != "PASS"
            or component.get("not_a_certificate") is not True
            or component.get("certificate_component_role") != role
            or component.get("certificate_generation_sha256")
            != generation_sha256
            or component.get("certificate_component_schema_version")
            != "cyz-0015-certificate-component-v1"
            or component.get("component_acceptance_rule")
            != component_rule
        ):
            core.fail(
                "published_report_component",
                f"component is not committed by the report: {role}",
                str(path),
            )
        accepted_hashes[role] = expected_hash
    post_component_generation, _ = _certificate_generation(
        root, artifact, spec, manifest
    )
    if post_component_generation != generation_sha256:
        core.fail(
            "published_report_generation",
            "bound generation changed while checking report components",
            str(report_path),
        )
    return {
        "schema_version": "cyz-0015-report-consistency-check-v1",
        "status": "PASS",
        "scope": (
            "trusted_filesystem_freshness_and_internal_consistency_only"
        ),
        "live_evidence_reexecuted": False,
        "certificate_generation_sha256": generation_sha256,
        "verification_report_sha256": core.canonical_sha256(report),
        "accepted_component_hashes": accepted_hashes,
    }


def main(argv: Sequence[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description=(
            "Independently verify the one exact registered Brief 0015 "
            "scheduled constructor. No generator module is imported."
        )
    )
    parser.add_argument(
        "--artifact", type=Path, default=here / "scheduled_kernel.json"
    )
    parser.add_argument(
        "--spec", type=Path, default=here / "constructor_spec.json"
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=here / "control_vector_manifest.json",
    )
    parser.add_argument(
        "--generator", type=Path, default=here / "generate_0015.py"
    )
    parser.add_argument(
        "--dependency-root", type=Path, default=here.parents[1]
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--baseline", action="store_true")
    mode.add_argument("--portability", action="store_true")
    mode.add_argument("--report", type=Path)
    mode.add_argument(
        "--check-report",
        type=Path,
        help=(
            "check stored-report freshness and internal consistency; "
            "does not rerun live evidence"
        ),
    )
    mode.add_argument("--patch", type=Path)
    mode.add_argument("--single-artifact", type=Path)
    mode.add_argument("--input-worker", type=Path)
    mode.add_argument("--covariance-worker")
    mode.add_argument("--mutation-worker")
    parser.add_argument("--patch-role")
    parser.add_argument("--skip-regeneration", action="store_true")
    parser.add_argument("--skip-rename", action="store_true")
    parser.add_argument("--skip-covariance", action="store_true")
    parser.add_argument("--record", type=Path)
    parser.add_argument(
        "--baseline-output",
        type=Path,
        default=here / "baseline_report.json",
    )
    parser.add_argument(
        "--portability-output",
        type=Path,
        default=here / "portability_report.json",
    )
    parser.add_argument(
        "--observations-output",
        type=Path,
        default=here / "hostile_observations.json",
    )
    args = parser.parse_args(argv)

    report_paths: list[Path] | None = None
    generation_sha256: str | None = None
    record_path_validated = args.record is None
    try:
        if args.report is not None:
            phase0_root = here.parents[1]
            report_paths = _report_paths(args, phase0_root)
            # This happens before importing any verifier module. Dependency
            # import, root, inventory, generator, document and artifact
            # failures therefore cannot preserve a prior PASS generation.
            _mark_report_generation_in_progress(report_paths, None)
            if not sys.flags.isolated or __name__ != "__main__":
                raise BootstrapError(
                    "report_entrypoint",
                    "certificate publication requires the direct isolated "
                    "CLI: python -I artifacts/0015/verify_0015.py --report ...",
                )

        _load_runtime_modules()
        if tuple(core.REGISTERED_DEPENDENCIES) != (
            PHASE0_REGISTERED_DEPENDENCIES
        ):
            core.fail(
                "bootstrap_registry",
                "phase-0 and verifier dependency registries differ",
            )
        root = core.registered_repo_root(
            Path(__file__), args.dependency_root
        )
        _validate_record_path(args, root, report_paths)
        record_path_validated = True
        core.assert_loaded_source(
            root, "artifacts/0015/verify_0015.py", __file__
        )
        runtime.verify_loaded_verifier_sources(root)
        generator = core.assert_registered_path(
            root,
            "artifacts/0015/generate_0015.py",
            args.generator,
        )

        if args.input_worker is not None:
            spec_object = core.load_json(args.spec)
            vector = core.load_json(args.input_worker)
            core.verify_constructor_spec(spec_object)
            core.verify_input(spec_object, vector)
            result: dict[str, Any] = {
                "status": "PASS",
                "input_sha256": core.canonical_sha256(vector),
            }
        elif args.covariance_worker is not None:
            spec_object = core.load_json(args.spec)
            manifest_object = core.load_json(args.manifest)
            core.verify_constructor_spec(spec_object)
            core.verify_control_manifest(spec_object, manifest_object)
            roles = replay.controls_by_role(manifest_object)
            if args.covariance_worker not in roles:
                core.fail(
                    "s9_worker",
                    f"unknown covariance role {args.covariance_worker}",
                    args.covariance_worker,
                )
            control = roles[args.covariance_worker]
            expanded = model.execute_registered_constructor(
                spec_object, control["input"]
            )
            semantics.verify_model(
                spec_object,
                control["input"],
                expanded,
                args.covariance_worker,
            )
            result = {
                "status": "PASS",
                "role": args.covariance_worker,
                "result": semantics.verify_s9_covariance(
                    spec_object, control["input"], expanded
                ),
            }
        elif args.mutation_worker is not None:
            result = {
                "status": "PASS",
                "observation": hostile.run_named_mutation(
                    root,
                    args.artifact,
                    args.spec,
                    args.manifest,
                    generator,
                    Path(__file__),
                    args.mutation_worker,
                ),
            }
        elif args.single_artifact is not None:
            result = replay.verify_single_artifact(
                args.single_artifact,
                args.spec,
                args.manifest,
                root,
            )
        elif args.patch is not None:
            patch = core.load_json(args.patch)
            if not isinstance(patch, Mapping):
                core.fail("patch_schema", "patch must be a JSON object")
            result = replay.verify_full(
                args.artifact,
                args.spec,
                args.manifest,
                generator,
                root,
                patch,
                args.patch_role,
                regenerate=not args.skip_regeneration,
                verify_rename=not args.skip_rename,
            )
        elif args.portability:
            result = runtime.portability_check(
                root,
                args.artifact,
                args.spec,
                args.manifest,
                generator,
            )
        elif args.check_report is not None:
            result = _verify_published_report(
                args.check_report,
                args.baseline_output,
                args.portability_output,
                args.observations_output,
                root,
                args.artifact,
                args.spec,
                args.manifest,
            )
        elif args.report is not None:
            assert report_paths is not None
            generation_sha256, _ = _certificate_generation(
                root, args.artifact, args.spec, args.manifest
            )
            _mark_report_generation_in_progress(
                report_paths, generation_sha256
            )
            result = hostile.hostile_report(
                root,
                args.artifact,
                args.spec,
                args.manifest,
                generator,
                Path(__file__),
            )
            _publish_report_generation(
                report_paths,
                result,
                generation_sha256,
                root,
                args.artifact,
                args.spec,
                args.manifest,
            )
        else:
            result = runtime.baseline_check(
                root,
                args.artifact,
                args.spec,
                args.manifest,
                generator,
                Path(__file__),
                skip_covariance=args.skip_covariance,
                skip_regeneration=args.skip_regeneration,
                skip_rename=args.skip_rename,
            )
        if args.record is not None:
            core.write_canonical_json_atomic(args.record, result)
        _emit(result)
        return 0
    except Exception as exc:  # pragma: no branch - unified bootstrap guard
        if report_paths is not None:
            try:
                _mark_report_generation_in_progress(
                    report_paths, generation_sha256
                )
            except Exception:
                pass
        if isinstance(exc, BootstrapError) or (
            core is not None
            and isinstance(exc, core.VerificationError)
        ):
            result = {"status": "ERROR", "error": exc.record()}
            exit_code = 2
        else:
            result = {
                "status": "ERROR",
                "error": {
                    "code": "verifier_internal",
                    "message": repr(exc),
                    "location": "",
                },
            }
            exit_code = 3
        if (
            args.record is not None
            and args.report is None
            and record_path_validated
        ):
            try:
                if core is not None:
                    core.write_canonical_json_atomic(args.record, result)
                else:
                    _phase0_write_canonical_json_atomic(args.record, result)
            except Exception:
                pass
        _emit(result)
        return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
