from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "0015"
sys.path.insert(0, str(ARTIFACTS))

import generator_core as core  # noqa: E402


class GeneratorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = core.load_json(ARTIFACTS / "constructor_spec.json")
        cls.manifest = core.load_json(
            ARTIFACTS / "control_vector_manifest.json"
        )
        cls.valid_input = copy.deepcopy(
            cls.manifest["controls"][0]["input"]
        )

    def test_registered_documents_are_exact(self) -> None:
        core.validate_spec(self.spec)
        core.validate_manifest(self.spec, self.manifest)
        self.assertEqual(
            core.canonical_sha(self.spec), core.REGISTERED_SPEC_SHA256
        )
        self.assertEqual(
            core.semantic_contract_sha(self.spec),
            core.REGISTERED_SEMANTIC_CONTRACT_SHA256,
        )
        self.assertEqual(
            core.canonical_sha(self.manifest),
            core.REGISTERED_MANIFEST_SHA256,
        )

    def assert_input_rejected(self, field: str, value: object) -> None:
        vector = copy.deepcopy(self.valid_input)
        vector[field] = value
        with self.assertRaises(core.ConstructionError):
            core.validate_input(self.spec, vector)

    def test_input_types_and_ranges_are_strict(self) -> None:
        for value in (2.9, "2", True):
            with self.subTest(field="frame_arity", value=value):
                self.assert_input_rejected("frame_arity", value)
        self.assert_input_rejected("dilute_flag", "false")
        for value in ("0/1", "-1/1"):
            self.assert_input_rejected("separation_fraction", value)
        self.assert_input_rejected("coupling", "-1/1")
        self.assert_input_rejected("relative_speed", "0/1")
        self.assert_input_rejected("source_registry_id", "unknown")
        self.assert_input_rejected("speed_min", "01/2")
        self.assert_input_rejected("metric_radii", ["2/1"] * 8)
        self.assert_input_rejected(
            "metric_radii", ["2/1"] * 8 + ["0/1"]
        )

    def test_input_field_set_is_closed(self) -> None:
        missing = copy.deepcopy(self.valid_input)
        missing.pop("frame_arity")
        extra = copy.deepcopy(self.valid_input)
        extra["rank"] = 3
        for vector in (missing, extra):
            with self.assertRaises(core.ConstructionError):
                core.validate_input(self.spec, vector)

    def test_metric_csv_preserves_empty_positions(self) -> None:
        for text in (
            ",1/1,2/1,3/1,4/1,5/1,6/1,7/1,8/1",
            "1/1,,2/1,3/1,4/1,5/1,6/1,7/1,8/1",
            "1/1,2/1,3/1,4/1,5/1,6/1,7/1,8/1,",
        ):
            with self.subTest(text=text), self.assertRaises(
                core.ConstructionError
            ):
                core.parse_metric_csv(text)

    def test_dependency_paths_are_posix_relative_and_closed(self) -> None:
        for relative in (
            "",
            "../escape.py",
            "artifacts/0015/../escape.py",
            "/absolute.py",
            r"artifacts\0015\generator_core.py",
            "C:/absolute.py",
        ):
            with self.subTest(relative=relative), self.assertRaises(
                core.ConstructionError
            ):
                core.dependency_path(ROOT, relative)

    def test_loaded_source_binding_rejects_shadow(self) -> None:
        with self.assertRaises(core.ConstructionError):
            core.assert_loaded_source(
                ROOT,
                "artifacts/0015/generator_core.py",
                __file__,
            )

    def test_python_surface_rejects_unregistered_helper(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-surface-") as tmp:
            copied_root = Path(tmp) / "repo"
            target = copied_root / "artifacts" / "0015"
            target.mkdir(parents=True)
            for relative in core.REGISTERED_DEPENDENCIES:
                source = ROOT / Path(*relative.split("/"))
                destination = copied_root / Path(*relative.split("/"))
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, destination)
            (target / "unregistered_helper.py").write_text(
                "VALUE = 1\n", encoding="utf-8"
            )
            with self.assertRaises(core.ConstructionError):
                core.validate_registered_python_surface(copied_root)

    def test_single_mode_requires_full_explicit_input(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-single-") as tmp:
            temp = Path(tmp)
            vector_path = temp / "input.json"
            output_path = temp / "single.json"
            vector_path.write_text(
                json.dumps(self.valid_input), encoding="utf-8"
            )
            command = [
                sys.executable,
                str(ARTIFACTS / "generate_0015.py"),
                "--single-input",
                str(vector_path),
                "--single-output",
                str(output_path),
                "--dependency-root",
                str(ROOT),
            ]
            accepted = subprocess.run(
                command, capture_output=True, text=True, timeout=60
            )
            self.assertEqual(accepted.returncode, 0, accepted.stderr)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(
                payload["schema_version"],
                "cyz-0015-single-instance-v3",
            )
            self.assertEqual(len(payload["executable_dependencies"]), 11)
            self.assertNotIn(
                "consumed_spec_paths_sha256", payload["instance"]
            )

            incomplete = copy.deepcopy(self.valid_input)
            incomplete.pop("frame_arity")
            vector_path.write_text(
                json.dumps(incomplete), encoding="utf-8"
            )
            rejected = subprocess.run(
                command, capture_output=True, text=True, timeout=60
            )
            self.assertEqual(rejected.returncode, 2)

    def test_outputs_cannot_overwrite_registered_inputs(self) -> None:
        spec_path = ARTIFACTS / "constructor_spec.json"
        before = spec_path.read_bytes()
        result = subprocess.run(
            [
                sys.executable,
                str(ARTIFACTS / "generate_0015.py"),
                "--output",
                str(spec_path),
                "--dependency-root",
                str(ROOT),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(spec_path.read_bytes(), before)

        with tempfile.TemporaryDirectory(prefix="cyz0015-redirect-") as tmp:
            redirected_spec = Path(tmp) / "constructor_spec.json"
            shutil.copyfile(spec_path, redirected_spec)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ARTIFACTS / "generate_0015.py"),
                    "--spec",
                    str(redirected_spec),
                    "--output",
                    str(spec_path),
                    "--dependency-root",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(spec_path.read_bytes(), before)

    def test_dependency_root_must_be_launcher_root(self) -> None:
        command = [
            sys.executable,
            str(ARTIFACTS / "generate_0015.py"),
            "--dependency-root",
            str(ROOT.parent),
        ]
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=30
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("dependency root", result.stderr)


if __name__ == "__main__":
    unittest.main()
