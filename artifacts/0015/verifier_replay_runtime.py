#!/usr/bin/env python3
"""Live baseline, covariance, and LF/CRLF replay for Brief 0015."""
from __future__ import annotations

import hashlib
import json
import py_compile
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

import verifier_core as core
import verifier_model as verifier_model_module
import verifier_replay as verifier_replay_module
import verifier_semantics as verifier_semantics_module


COVARIANCE_ROLES = (
    "ordinary_full_t9",
    "three_large_metric_control",
    "four_large_metric_control",
    "arity_two_semantic_control",
    "arity_four_semantic_control",
)


def _registered_runtime_paths(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path | None = None,
) -> tuple[Path, Path, Path, Path, Path | None]:
    resolved_root = Path(root).resolve()
    registered_artifact = core.assert_registered_path(
        resolved_root,
        "artifacts/0015/scheduled_kernel.json",
        artifact,
    )
    registered_spec = core.assert_registered_path(
        resolved_root,
        "artifacts/0015/constructor_spec.json",
        spec,
    )
    registered_manifest = core.assert_registered_path(
        resolved_root,
        "artifacts/0015/control_vector_manifest.json",
        manifest,
    )
    registered_generator = (
        core.assert_registered_path(
            resolved_root,
            "artifacts/0015/generate_0015.py",
            generator,
        )
        if generator is not None
        else None
    )
    return (
        resolved_root,
        registered_artifact,
        registered_spec,
        registered_manifest,
        registered_generator,
    )


def verify_loaded_verifier_sources(root: Path) -> dict[str, str]:
    """Bind every verifier module loaded in this process to registered files."""
    required: dict[str, str | Path | None] = {
        "artifacts/0015/verifier_core.py": core.__file__,
        "artifacts/0015/verifier_model.py": verifier_model_module.__file__,
        "artifacts/0015/verifier_semantics.py": (
            verifier_semantics_module.__file__
        ),
        "artifacts/0015/verifier_replay.py": verifier_replay_module.__file__,
        "artifacts/0015/verifier_replay_runtime.py": __file__,
    }
    observed = dict(required)
    for module_name, relative in (
        ("verifier_hostile", "artifacts/0015/verifier_hostile.py"),
        ("verify_0015", "artifacts/0015/verify_0015.py"),
    ):
        module = sys.modules.get(module_name)
        if module is not None:
            observed[relative] = getattr(module, "__file__", None)
    main_module = sys.modules.get("__main__")
    main_file = getattr(main_module, "__file__", None)
    if main_file is not None and Path(main_file).name == "verify_0015.py":
        observed["artifacts/0015/verify_0015.py"] = main_file
    core.assert_loaded_sources(
        root,
        observed,
        required_relatives=tuple(required),
    )
    core.verify_python_dependency_inventory(root)
    return {
        relative: str(Path(path).resolve())
        for relative, path in sorted(observed.items())
        if path is not None
    }


def _last_json_object(stdout: str, location: str) -> Mapping[str, Any]:
    for line in reversed(stdout.splitlines()):
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            return parsed
    core.fail(
        "subprocess_protocol",
        "child process emitted no JSON object",
        location,
    )


def live_covariance_check(
    root: Path,
    spec: Path,
    manifest: Path,
    verifier: Path,
) -> dict[str, Any]:
    """Run all eight S9 generators in fresh processes for five control roles."""
    results: dict[str, Any] = {}
    for role in COVARIANCE_ROLES:
        command = [
            sys.executable,
            str(verifier),
            "--covariance-worker",
            role,
            "--spec",
            str(spec),
            "--manifest",
            str(manifest),
            "--dependency-root",
            str(root),
        ]
        try:
            process = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=600,
            )
        except subprocess.TimeoutExpired:
            core.fail(
                "s9_infrastructure",
                f"covariance worker timed out for {role}",
                role,
            )
        parsed = _last_json_object(process.stdout, role)
        if (
            process.returncode != 0
            or parsed.get("status") != "PASS"
            or not isinstance(parsed.get("result"), Mapping)
            or set(parsed["result"]) != {f"s{index}" for index in range(8)}
        ):
            core.fail(
                "s9_infrastructure",
                f"covariance worker failed for {role}; "
                f"exit={process.returncode} output={parsed}",
                role,
            )
        results[role] = {
            "exit_code": process.returncode,
            "generators": parsed["result"],
            "stdout_sha256": hashlib.sha256(
                process.stdout.encode("utf-8")
            ).hexdigest(),
            "stderr_sha256": hashlib.sha256(
                process.stderr.encode("utf-8")
            ).hexdigest(),
        }
    return results


def baseline_check(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
    verifier: Path,
    skip_covariance: bool = False,
    skip_regeneration: bool = False,
    skip_rename: bool = False,
) -> dict[str, Any]:
    (
        root,
        artifact,
        spec,
        manifest,
        generator_path,
    ) = _registered_runtime_paths(
        root, artifact, spec, manifest, generator
    )
    assert generator_path is not None
    verifier_path = core.assert_registered_path(
        root,
        "artifacts/0015/verify_0015.py",
        verifier,
    )
    spec_object = core.load_json(spec)
    manifest_object = core.load_json(manifest)
    core.verify_constructor_spec(spec_object)
    core.verify_control_manifest(spec_object, manifest_object)
    loaded_sources = verify_loaded_verifier_sources(root)
    result = verifier_replay_module.verify_full(
        artifact,
        spec,
        manifest,
        generator_path,
        root,
        regenerate=not skip_regeneration,
        verify_rename=not skip_rename,
    )
    result["s9"] = (
        {"skipped": True}
        if skip_covariance
        else live_covariance_check(root, spec, manifest, verifier_path)
    )

    inventory = core.dependency_inventory(spec_object, root)
    python_files = [
        core.dependency_path(root, record["path"]) for record in inventory
    ]
    for path in python_files:
        try:
            py_compile.compile(str(path), doraise=True)
        except Exception as exc:
            core.fail(
                "py_compile",
                f"py_compile failed for {path}: {exc}",
                str(path),
            )
    help_results: dict[str, int] = {}
    for path in (generator_path, verifier_path):
        process = subprocess.run(
            [sys.executable, str(path), "--help"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if process.returncode != 0:
            core.fail(
                "help",
                f"--help failed for {path}: {process.stderr}",
                str(path),
            )
        help_results[path.relative_to(root).as_posix()] = process.returncode

    result["py_compile"] = {
        "files": [
            path.relative_to(root).as_posix() for path in python_files
        ],
        "exit_code": 0,
    }
    result["help"] = help_results
    result["source_hashes"] = {
        row["path"]: row["normalized_lf_sha256"] for row in inventory
    }
    result["loaded_source_files"] = loaded_sources
    result["source_binding_policy"] = core.SOURCE_BINDING_POLICY
    return result


PORTABILITY_RUNNER = r'''import json
import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
A = ROOT / "artifacts" / "0015"
sys.path.insert(0, str(A))

import generator_core
import generator_artifact
import verifier_core
import verifier_replay
import verifier_replay_runtime

spec = json.loads((A / "constructor_spec.json").read_text(encoding="utf-8"))
for relative in spec["executable_dependencies"]:
    py_compile.compile(str(ROOT / Path(*relative.split("/"))), doraise=True)

generator_artifact_payload = generator_artifact.build_artifact(
    A / "constructor_spec.json",
    A / "control_vector_manifest.json",
    ROOT,
    A / "generate_0015.py",
)
generator_core.write_json(A / "crlf_regenerated.json", generator_artifact_payload)
verifier_replay_runtime.verify_loaded_verifier_sources(ROOT)
result = verifier_replay.verify_full(
    A / "scheduled_kernel.json",
    A / "constructor_spec.json",
    A / "control_vector_manifest.json",
    A / "generate_0015.py",
    ROOT,
    regenerate=False,
    verify_rename=False,
)
print(json.dumps({"status": "PASS", "result": result}, sort_keys=True, separators=(",", ":")))
'''


def portability_check(
    root: Path,
    artifact: Path,
    spec: Path,
    manifest: Path,
    generator: Path,
) -> dict[str, Any]:
    (
        root,
        artifact,
        spec,
        manifest,
        generator_path,
    ) = _registered_runtime_paths(
        root, artifact, spec, manifest, generator
    )
    assert generator_path is not None
    spec_object = core.load_json(spec)
    manifest_object = core.load_json(manifest)
    core.verify_constructor_spec(spec_object)
    core.verify_control_manifest(spec_object, manifest_object)
    verify_loaded_verifier_sources(root)
    inventory = core.dependency_inventory(spec_object, root)

    with tempfile.TemporaryDirectory(prefix="cyz0015-crlf-") as temporary:
        target = Path(temporary) / "repo"
        (target / "artifacts" / "0015").mkdir(parents=True)
        copy_relative = [
            "artifacts/0015/constructor_spec.json",
            "artifacts/0015/control_vector_manifest.json",
            "artifacts/0015/scheduled_kernel.json",
            *core.REGISTERED_DEPENDENCIES,
        ]
        if len(copy_relative) != len(set(copy_relative)):
            core.fail("portability", "clean-copy file list has duplicates")
        for relative in copy_relative:
            source = core.registered_repo_path(root, relative)
            destination = target.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.suffix == ".py":
                normalized = (
                    source.read_text(encoding="utf-8")
                    .replace("\r\n", "\n")
                    .replace("\r", "\n")
                )
                destination.write_bytes(
                    normalized.replace("\n", "\r\n").encode("utf-8")
                )
            else:
                value = core.load_json(source)
                pretty = (
                    json.dumps(
                        value,
                        sort_keys=True,
                        indent=2,
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                destination.write_bytes(
                    pretty.replace("\n", "\r\n").encode("utf-8")
                )

        runner = target / "portability_runner.py"
        runner.write_text(PORTABILITY_RUNNER, encoding="utf-8", newline="\n")
        try:
            process = subprocess.run(
                [sys.executable, str(runner)],
                cwd=str(target),
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired:
            core.fail("portability", "CRLF replay timed out")
        if process.returncode != 0:
            core.fail(
                "portability",
                f"CRLF runner failed: {process.stdout} {process.stderr}",
            )
        parsed = _last_json_object(process.stdout, "portability")
        if parsed.get("status") != "PASS":
            core.fail("portability", "CRLF semantic replay did not PASS")
        regenerated = core.load_json(
            target / "artifacts/0015/crlf_regenerated.json"
        )
        supplied = core.load_json(
            target / "artifacts/0015/scheduled_kernel.json"
        )
        if core.canonical_sha256(regenerated) != core.canonical_sha256(
            supplied
        ):
            core.fail(
                "portability",
                "CRLF regeneration changed canonical artifact",
            )
        original_hashes = {
            row["path"]: row["normalized_lf_sha256"] for row in inventory
        }
        crlf_hashes = {
            relative: core.normalized_lf_sha256(
                target.joinpath(*PurePosixPath(relative).parts)
            )
            for relative in core.REGISTERED_DEPENDENCIES
        }
        if original_hashes != crlf_hashes:
            core.fail(
                "portability",
                "LF-normalized source hashes changed under CRLF copy",
            )
        return {
            "status": "PASS",
            "runner_exit_code": process.returncode,
            "runner_stdout_sha256": hashlib.sha256(
                process.stdout.encode("utf-8")
            ).hexdigest(),
            "runner_stderr_sha256": hashlib.sha256(
                process.stderr.encode("utf-8")
            ).hexdigest(),
            "artifact_payload_sha256": core.canonical_sha256(supplied),
            "regenerated_payload_sha256": core.canonical_sha256(
                regenerated
            ),
            "normalized_source_hashes": crlf_hashes,
            "clean_lf_source_hashes": original_hashes,
            "py_compile_exit_code": 0,
            "crlf_semantic_replay_status": parsed["status"],
            "source_binding_policy": core.SOURCE_BINDING_POLICY,
        }
