#!/usr/bin/env python3
"""CLI for the fixed registered Brief 0015 generator."""
from __future__ import annotations

import sys

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
from pathlib import Path
from typing import Any, Sequence


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

generator_artifact: Any = None
generator_core: Any = None


def _paths_alias(left: Path, right: Path) -> bool:
    left = Path(left)
    right = Path(right)
    if left.resolve() == right.resolve():
        return True
    try:
        return left.exists() and right.exists() and os.path.samefile(left, right)
    except OSError:
        return False


def _load_generator_modules() -> None:
    global generator_artifact, generator_core
    if generator_core is not None:
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
                raise RuntimeError(
                    f"preloaded module {name} is not registered: "
                    f"{present_file!r}"
                )
            return present
        module_spec = importlib.util.spec_from_file_location(name, expected)
        if module_spec is None or module_spec.loader is None:
            raise RuntimeError(f"cannot load registered module {expected}")
        loaded = importlib.util.module_from_spec(module_spec)
        sys.modules[name] = loaded
        loaded_new.append((name, loaded))
        module_spec.loader.exec_module(loaded)
        return loaded

    try:
        loaded_core = load_exact("generator_core")
        load_exact("generator_model")
        loaded_artifact = load_exact("generator_artifact")
    except Exception:
        for name, loaded in reversed(loaded_new):
            if sys.modules.get(name) is loaded:
                del sys.modules[name]
        raise
    generator_core, generator_artifact = loaded_core, loaded_artifact


def _validate_output_paths(args: argparse.Namespace, root: Path) -> None:
    single_mode = args.single_input is not None
    output = args.single_output if single_mode else args.output
    if output is None:
        return
    protected = [
        root / Path(*relative.split("/"))
        for relative in REGISTERED_DEPENDENCIES
    ]
    protected.extend(
        [
            root / "artifacts" / "0015" / "constructor_spec.json",
            root / "artifacts" / "0015" / "control_vector_manifest.json",
        ]
    )
    protected.extend([args.spec, args.manifest])
    if single_mode:
        protected.append(
            root / "artifacts" / "0015" / "scheduled_kernel.json"
        )
        protected.append(args.single_input)
    for path in protected:
        if _paths_alias(output, path):
            raise generator_core.ConstructionError(
                "generator output may not alias a registered or active input"
            )


def _error(code: str, message: str) -> str:
    return json.dumps(
        {"status": "ERROR", "code": code, "message": message},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )


def main(argv: Sequence[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description=(
            "Generate the one exact registered target-rank-free "
            "scheduled Markov-renewal artifact."
        )
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
        "--output", type=Path, default=here / "scheduled_kernel.json"
    )
    parser.add_argument(
        "--dependency-root", type=Path, default=here.parents[1]
    )
    parser.add_argument(
        "--single-input",
        type=Path,
        help="JSON object containing every registered microscopic input field",
    )
    parser.add_argument(
        "--single-output",
        type=Path,
        help="output path required when --single-input is used",
    )
    parser.add_argument("--opaque-id", default="opaque_cli")
    args = parser.parse_args(argv)

    try:
        _load_generator_modules()
        if tuple(generator_core.REGISTERED_DEPENDENCIES) != (
            REGISTERED_DEPENDENCIES
        ):
            raise generator_core.ConstructionError(
                "generator bootstrap dependency registry mismatch"
            )
        root = generator_core.registered_repo_root(
            Path(__file__), args.dependency_root
        )
        _validate_output_paths(args, root)
        if args.single_input is not None:
            if args.single_output is None:
                raise generator_core.ConstructionError(
                    "--single-output is required with --single-input"
                )
            payload = generator_artifact.build_single_artifact(
                args.spec,
                args.manifest,
                args.single_input,
                root,
                Path(__file__),
                args.opaque_id,
            )
            generator_core.write_json(args.single_output, payload)
        else:
            if args.single_output is not None:
                raise generator_core.ConstructionError(
                    "--single-output requires --single-input"
                )
            payload = generator_artifact.build_artifact(
                args.spec,
                args.manifest,
                root,
                Path(__file__),
            )
            generator_core.write_json(args.output, payload)
        return 0
    except Exception as exc:  # pragma: no cover - infrastructure guard
        if (
            generator_core is not None
            and isinstance(exc, generator_core.ConstructionError)
        ) or isinstance(exc, (json.JSONDecodeError, OSError)):
            print(
                _error("generator_construction_error", str(exc)),
                file=sys.stderr,
            )
            return 2
        print(_error("generator_internal", repr(exc)), file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
