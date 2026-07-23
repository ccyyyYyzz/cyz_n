from __future__ import annotations

import ast
import copy
import contextlib
import inspect
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "0015"
sys.path.insert(0, str(ARTIFACTS))

import generator_model  # noqa: E402
import verifier_core as core  # noqa: E402
import verifier_hostile as hostile  # noqa: E402
import verifier_model as verifier_model  # noqa: E402
import verifier_replay as replay  # noqa: E402
import verifier_replay_runtime as runtime  # noqa: E402
import verifier_semantics as semantics  # noqa: E402
import verify_0015 as verifier_cli  # noqa: E402

verifier_cli._load_runtime_modules()


class VerifierContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec = core.load_json(ARTIFACTS / "constructor_spec.json")
        cls.manifest = core.load_json(
            ARTIFACTS / "control_vector_manifest.json"
        )
        cls.artifact = core.load_json(ARTIFACTS / "scheduled_kernel.json")

    def test_verifier_sources_do_not_import_generator_modules(self) -> None:
        verifier_files = [
            "verifier_core.py",
            "verifier_model.py",
            "verifier_semantics.py",
            "verifier_replay.py",
            "verifier_replay_runtime.py",
            "verifier_hostile.py",
            "verify_0015.py",
        ]
        for name in verifier_files:
            tree = ast.parse(
                (ARTIFACTS / name).read_text(encoding="utf-8")
            )
            imported: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module)
            with self.subTest(name=name):
                self.assertFalse(
                    any(module.startswith("generator") for module in imported),
                    imported,
                )

    def test_registered_documents_and_runtime_sources(self) -> None:
        core.verify_constructor_spec(self.spec)
        core.verify_control_manifest(self.spec, self.manifest)
        observed = runtime.verify_loaded_verifier_sources(ROOT)
        self.assertIn("artifacts/0015/verifier_core.py", observed)
        self.assertEqual(len(core.dependency_inventory(self.spec, ROOT)), 11)
        self.assertEqual(
            tuple(core.REGISTERED_DEPENDENCIES),
            verifier_cli.PHASE0_REGISTERED_DEPENDENCIES,
        )

    def test_independent_model_matches_two_small_controls(self) -> None:
        roles = replay.controls_by_role(self.manifest)
        for role in (
            "three_large_metric_control",
            "arity_two_semantic_control",
        ):
            vector = roles[role]["input"]
            generated = generator_model.execute_registered_constructor(
                self.spec, vector
            )
            verified = verifier_model.execute_registered_constructor(
                self.spec, vector
            )
            with self.subTest(role=role):
                self.assertEqual(
                    verifier_model.expanded_hash(self.spec, verified),
                    generator_model.expanded_hash(self.spec, generated),
                )
                semantics.verify_model(
                    self.spec, vector, verified, role
                )

    def test_all_serialized_semantic_mutations_hit_registration(self) -> None:
        for name, target, _, _ in hostile.MUTATIONS:
            if target != "spec":
                continue
            mutated = copy.deepcopy(self.spec)
            replay.apply_spec_patch(mutated, name)
            with self.subTest(name=name), self.assertRaises(
                core.VerificationError
            ) as raised:
                core.verify_constructor_spec(mutated)
            self.assertEqual(raised.exception.code, "registered_spec_hash")

    def test_all_manifest_mutations_hit_registration(self) -> None:
        for name, target, _, _ in hostile.MUTATIONS:
            if target != "manifest":
                continue
            mutated = copy.deepcopy(self.manifest)
            replay.apply_manifest_patch(mutated, name)
            with self.subTest(name=name), self.assertRaises(
                core.VerificationError
            ) as raised:
                core.verify_control_manifest(self.spec, mutated)
            self.assertEqual(
                raised.exception.code, "registered_manifest_hash"
            )

    def test_artifact_schema_rejects_consumption_self_attestation(self) -> None:
        mutated = copy.deepcopy(self.artifact)
        mutated["instances"][0]["consumed_spec_paths_sha256"] = "0" * 64
        with self.assertRaises(core.VerificationError) as raised:
            control = self.manifest["controls"][0]
            replay._rebuild_record(
                self.spec,
                self.manifest,
                mutated["instances"][0],
                control["opaque_id"],
                control["input"],
            )
        self.assertEqual(raised.exception.code, "instance_schema")

    def test_single_artifact_is_independently_verified(self) -> None:
        vector = self.manifest["controls"][0]["input"]
        with tempfile.TemporaryDirectory(prefix="cyz0015-single-test-") as tmp:
            directory = Path(tmp)
            input_path = directory / "input.json"
            output_path = directory / "single.json"
            core.write_canonical_json(input_path, vector)
            generated = subprocess.run(
                [
                    sys.executable,
                    str(ARTIFACTS / "generate_0015.py"),
                    "--single-input",
                    str(input_path),
                    "--single-output",
                    str(output_path),
                    "--dependency-root",
                    str(ROOT),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            result = replay.verify_single_artifact(
                output_path,
                ARTIFACTS / "constructor_spec.json",
                ARTIFACTS / "control_vector_manifest.json",
                ROOT,
            )
            self.assertEqual(result["status"], "PASS")
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload.pop("executable_dependencies")
            core.write_canonical_json(output_path, payload)
            with self.assertRaises(core.VerificationError) as raised:
                replay.verify_single_artifact(
                    output_path,
                    ARTIFACTS / "constructor_spec.json",
                    ARTIFACTS / "control_vector_manifest.json",
                    ROOT,
                )
            self.assertEqual(
                raised.exception.code, "single_artifact_schema"
            )

    def test_report_accepts_no_prewritten_evidence_input(self) -> None:
        signature = inspect.signature(hostile.hostile_report)
        self.assertNotIn("observations", signature.parameters)
        self.assertNotIn("baseline_record", signature.parameters)
        self.assertNotIn("portability_record", signature.parameters)
        source = inspect.getsource(hostile.hostile_report)
        self.assertIn("runtime.baseline_check", source)
        self.assertIn("runtime.portability_check", source)
        self.assertIn("run_named_mutation", source)

    def test_report_generation_invalidates_old_pass_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-sentinel-") as tmp:
            paths = [
                Path(tmp) / name
                for name in (
                    "report.json",
                    "baseline.json",
                    "portability.json",
                    "observations.json",
                )
            ]
            for path in paths:
                core.write_canonical_json(path, {"status": "PASS"})
            verifier_cli._mark_report_generation_in_progress(
                paths, "a" * 64
            )
            for path in paths:
                payload = core.load_json(path)
                self.assertEqual(payload["status"], "IN_PROGRESS")
                self.assertTrue(payload["not_a_certificate"])

    def test_report_outputs_unconditionally_protect_registered_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-alias-") as tmp:
            directory = Path(tmp)
            args = SimpleNamespace(
                report=ARTIFACTS / "scheduled_kernel.json",
                baseline_output=directory / "baseline.json",
                portability_output=directory / "portability.json",
                observations_output=directory / "observations.json",
                artifact=directory / "redirected-artifact.json",
                spec=ARTIFACTS / "constructor_spec.json",
                manifest=ARTIFACTS / "control_vector_manifest.json",
                generator=ARTIFACTS / "generate_0015.py",
                record=None,
            )
            with self.assertRaises(verifier_cli.BootstrapError) as raised:
                verifier_cli._report_paths(args, ROOT)
            self.assertEqual(raised.exception.code, "report_output")

    def test_report_mode_forbids_record_and_record_protects_inputs(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-record-") as tmp:
            directory = Path(tmp)
            report_args = SimpleNamespace(
                report=directory / "report.json",
                baseline_output=directory / "baseline.json",
                portability_output=directory / "portability.json",
                observations_output=directory / "observations.json",
                artifact=ARTIFACTS / "scheduled_kernel.json",
                spec=ARTIFACTS / "constructor_spec.json",
                manifest=ARTIFACTS / "control_vector_manifest.json",
                generator=ARTIFACTS / "generate_0015.py",
                record=directory / "record.json",
            )
            with self.assertRaises(verifier_cli.BootstrapError) as raised:
                verifier_cli._report_paths(report_args, ROOT)
            self.assertEqual(raised.exception.code, "report_output")

            record_args = SimpleNamespace(
                record=ARTIFACTS / "scheduled_kernel.json",
                artifact=directory / "redirected-artifact.json",
                spec=ARTIFACTS / "constructor_spec.json",
                manifest=ARTIFACTS / "control_vector_manifest.json",
                generator=ARTIFACTS / "generate_0015.py",
                patch=None,
                single_artifact=None,
                input_worker=None,
            )
            with self.assertRaises(core.VerificationError) as raised:
                verifier_cli._validate_record_path(
                    record_args, ROOT, None
                )
            self.assertEqual(raised.exception.code, "record_output")
            before = (ARTIFACTS / "scheduled_kernel.json").read_bytes()
            with contextlib.redirect_stdout(io.StringIO()):
                exit_code = verifier_cli.main(
                    [
                        "--record",
                        str(ARTIFACTS / "scheduled_kernel.json"),
                        "--dependency-root",
                        str(ROOT),
                    ]
                )
            self.assertEqual(exit_code, 2)
            self.assertEqual(
                (ARTIFACTS / "scheduled_kernel.json").read_bytes(),
                before,
            )

            check_args = SimpleNamespace(
                record=directory / "baseline.json",
                artifact=ARTIFACTS / "scheduled_kernel.json",
                spec=ARTIFACTS / "constructor_spec.json",
                manifest=ARTIFACTS / "control_vector_manifest.json",
                generator=ARTIFACTS / "generate_0015.py",
                patch=None,
                check_report=directory / "report.json",
                single_artifact=None,
                input_worker=None,
                baseline_output=directory / "baseline.json",
                portability_output=directory / "portability.json",
                observations_output=directory / "observations.json",
            )
            with self.assertRaises(core.VerificationError) as raised:
                verifier_cli._validate_record_path(
                    check_args, ROOT, None
                )
            self.assertEqual(raised.exception.code, "record_output")

    def test_report_components_are_never_standalone_certificates(self) -> None:
        component = hostile._certificate_component(
            {"status": "PASS", "evidence": "live"},
            "baseline",
            "b" * 64,
        )
        self.assertEqual(component["status"], "PASS")
        self.assertTrue(component["not_a_certificate"])
        self.assertEqual(
            component["certificate_component_role"], "baseline"
        )
        self.assertEqual(
            component["certificate_generation_sha256"], "b" * 64
        )
        self.assertIn(
            "matching_generation_PASS_verification_report",
            component["component_acceptance_rule"],
        )

    def test_invalid_generation_input_cannot_leave_old_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-start-fail-") as tmp:
            directory = Path(tmp)
            artifact = directory / "malformed-artifact.json"
            artifact.write_text("{", encoding="utf-8")
            paths = [
                directory / name
                for name in (
                    "report.json",
                    "baseline.json",
                    "portability.json",
                    "observations.json",
                )
            ]
            for path in paths:
                core.write_canonical_json(path, {"status": "PASS"})
            process = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(ARTIFACTS / "verify_0015.py"),
                    "--artifact",
                    str(artifact),
                    "--spec",
                    str(ARTIFACTS / "constructor_spec.json"),
                    "--manifest",
                    str(ARTIFACTS / "control_vector_manifest.json"),
                    "--generator",
                    str(ARTIFACTS / "generate_0015.py"),
                    "--dependency-root",
                    str(ROOT),
                    "--report",
                    str(paths[0]),
                    "--baseline-output",
                    str(paths[1]),
                    "--portability-output",
                    str(paths[2]),
                    "--observations-output",
                    str(paths[3]),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(process.returncode, 2, process.stdout)
            for path in paths:
                payload = core.load_json(path)
                self.assertEqual(payload["status"], "IN_PROGRESS")
                self.assertTrue(payload["not_a_certificate"])
                self.assertEqual(
                    payload["phase"], "validating_generation"
                )
                self.assertIsNone(
                    payload["certificate_generation_sha256"]
                )

    def test_root_preflight_failure_cannot_leave_old_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-root-fail-") as tmp:
            directory = Path(tmp)
            paths = [
                directory / name
                for name in (
                    "report.json",
                    "baseline.json",
                    "portability.json",
                    "observations.json",
                )
            ]
            for path in paths:
                core.write_canonical_json(path, {"status": "PASS"})
            process = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(ARTIFACTS / "verify_0015.py"),
                    "--dependency-root",
                    str(directory),
                    "--report",
                    str(paths[0]),
                    "--baseline-output",
                    str(paths[1]),
                    "--portability-output",
                    str(paths[2]),
                    "--observations-output",
                    str(paths[3]),
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            self.assertEqual(process.returncode, 2, process.stdout)
            for path in paths:
                payload = core.load_json(path)
                self.assertEqual(payload["status"], "IN_PROGRESS")
                self.assertTrue(payload["not_a_certificate"])

    def test_report_publication_requires_isolated_cli(self) -> None:
        with tempfile.TemporaryDirectory(prefix="cyz0015-isolated-") as tmp:
            directory = Path(tmp)
            paths = [
                directory / name
                for name in (
                    "report.json",
                    "baseline.json",
                    "portability.json",
                    "observations.json",
                )
            ]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exit_code = verifier_cli.main(
                    [
                        "--report",
                        str(paths[0]),
                        "--baseline-output",
                        str(paths[1]),
                        "--portability-output",
                        str(paths[2]),
                        "--observations-output",
                        str(paths[3]),
                    ]
                )
            self.assertEqual(exit_code, 2)
            payload = json.loads(output.getvalue())
            self.assertEqual(
                payload["error"]["code"], "report_entrypoint"
            )
            for path in paths:
                sentinel = core.load_json(path)
                self.assertEqual(sentinel["status"], "IN_PROGRESS")
                self.assertTrue(sentinel["not_a_certificate"])

    def test_hostile_protocol_requires_exact_exit_two(self) -> None:
        base = {
            "protocol_status": "ERROR",
            "observed_error": {"code": "registered_spec_hash"},
        }
        for exit_code in (0, 1, 3):
            record = dict(base, exit_code=exit_code)
            with self.subTest(exit_code=exit_code), self.assertRaises(
                core.VerificationError
            ):
                hostile._require_rejection(
                    record, {"registered_spec_hash"}, "probe"
                )
        structured = subprocess.CompletedProcess(
            ["generator"], 2, "", '{"status":"ERROR","code":"x"}\n'
        )
        unstructured = subprocess.CompletedProcess(
            ["generator"], 2, "", "plain failure\n"
        )
        self.assertEqual(
            replay._structured_generator_error(structured)["code"], "x"
        )
        self.assertIsNone(
            replay._structured_generator_error(unstructured)
        )

    def test_suite_is_explicit_unique_and_role_based(self) -> None:
        names = [row[0] for row in hostile.MUTATIONS]
        self.assertEqual(len(names), 94)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            set(runtime.COVARIANCE_ROLES),
            {
                "ordinary_full_t9",
                "three_large_metric_control",
                "four_large_metric_control",
                "arity_two_semantic_control",
                "arity_four_semantic_control",
            },
        )
        for path in (
            ARTIFACTS / "verifier_replay_runtime.py",
            ARTIFACTS / "verifier_hostile.py",
        ):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn('["u0"', text)
            self.assertNotIn('"u7"', text)


if __name__ == "__main__":
    unittest.main()
