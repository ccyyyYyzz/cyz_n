#!/usr/bin/env python3
"""Regression and replay tests for the independent Brief 0018 source audit."""

from __future__ import annotations

import copy
import json
import os
import subprocess
import sys
import unittest
from fractions import Fraction
from pathlib import Path
from unittest import mock

import numpy as np

import microcanonical_source as production
import stat_audit_core as core
import statistical_audit as audit


DIRECTORY = Path(__file__).resolve().parent
REPORT = DIRECTORY / "stat_audit_report.json"
RUNNER = DIRECTORY / "run_stat_audit.py"


class StrictJsonTests(unittest.TestCase):
    def test_registered_json_is_strict_and_exact(self) -> None:
        registry, cell = core.load_registered_cell()
        self.assertEqual(
            core.canonical_sha256(registry), core.REGISTRY_CANONICAL_SHA256
        )
        self.assertEqual(cell.mass.hex(), "0x1.0000000000000p+3")
        self.assertEqual(cell.k1.hex(), "0x1.0000000000000p-3")
        self.assertEqual(cell.e_star.hex(), "0x1.0000000000000p+0")
        self.assertEqual(cell.d, 16)

    def test_duplicate_keys_are_rejected(self) -> None:
        with self.assertRaises(core.AuditError):
            core.loads_strict_json('{"x":1,"x":1}')

    def test_every_nonfinite_spelling_is_rejected(self) -> None:
        for token in ("NaN", "Infinity", "-Infinity", "1e9999", "-1e9999"):
            with self.subTest(token=token):
                with self.assertRaises(core.AuditError):
                    core.loads_strict_json(f'{{"x":{token}}}')

    def test_boolean_numeric_substitution_is_rejected(self) -> None:
        registry = core.load_canonical_source_registry()
        mutated = copy.deepcopy(registry)
        mutated["source_draw_registry"]["fourier_cutoff_K"] = True
        with self.assertRaises(production.RegistryError):
            production.validate_registry(mutated)

    def test_unknown_level_matching_tolerance_is_rejected(self) -> None:
        registry = core.load_canonical_source_registry()
        mutated = copy.deepcopy(registry)
        mutated["source_draw_registry"]["level_match_tolerance"] = "1e-6"
        with self.assertRaises(production.RegistryError):
            production.validate_registry(mutated)

    def test_lf_crlf_semantic_equality_is_type_strict(self) -> None:
        registry_text = core.registry_path().read_text(encoding="utf-8")
        left = core.loads_strict_json(registry_text)
        right = core.loads_strict_json(
            registry_text.replace("\n", "\r\n")
        )
        self.assertTrue(core.type_strict_equal(left, right))
        self.assertFalse(core.type_strict_equal({"x": 1}, {"x": True}))

    def test_semantic_hash_detects_value_and_type_mutation(self) -> None:
        report = core.attach_semantic_hash({"status": "PASS", "count": 1})
        self.assertTrue(core.verify_semantic_hash(report))
        changed = copy.deepcopy(report)
        changed["count"] = 2
        self.assertFalse(core.verify_semantic_hash(changed))
        changed_type = copy.deepcopy(report)
        changed_type["count"] = True
        self.assertFalse(core.verify_semantic_hash(changed_type))

    def test_numpy_scalars_are_normalized_before_strict_replay(self) -> None:
        native = core.to_json_native(
            {"float": np.float64(0.5), "integer": np.int64(3)}
        )
        self.assertIs(type(native["float"]), float)
        self.assertIs(type(native["integer"]), int)


class RegisteredRandomStreamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry, cls.cell = core.load_registered_cell()

    def test_seed_derivation_and_raw_golden_vectors(self) -> None:
        result = core.verify_golden_raw_streams()
        self.assertEqual(result["status"], "PASS")
        for label, expected in core.SEED_HEX.items():
            self.assertEqual(f"{core.seed_from_label(label):032x}", expected)

    def test_open_uniform_map_never_returns_endpoint(self) -> None:
        values = core.uniform_open(core.make_rng("golden_replay"), 10000)
        self.assertTrue(np.all(values > 0.0))
        self.assertTrue(np.all(values < 1.0))

    def test_exact_shape_and_energy_guards(self) -> None:
        core.validate_gamma_shapes((4, 15, 15))
        for mutation in ((4, 16, 16), (4, 8, 8), (4, 15.5, 15.5)):
            with self.subTest(mutation=mutation):
                with self.assertRaises(core.AuditError):
                    core.validate_gamma_shapes(mutation)
        self.assertEqual(core.validate_positive_e_star(1.0), 1.0)
        for value in (0.0, -0.5, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(core.AuditError):
                    core.validate_positive_e_star(value)

    def test_source_subregistry_hash_has_domain_separation(self) -> None:
        registry = core.load_canonical_source_registry()
        baseline = core.source_draw_registry_sha256(registry)
        event = copy.deepcopy(registry)
        event["downstream_context"]["r_in"] = 0.125
        self.assertEqual(
            baseline, core.source_draw_registry_sha256(event)
        )
        source = copy.deepcopy(registry)
        source["source_draw_registry"]["total_transverse_momentum"][0] = 2.0
        self.assertNotEqual(
            baseline, core.source_draw_registry_sha256(source)
        )

    def test_stat_registry_binds_without_duplicating_source_cell(self) -> None:
        self.assertNotIn("source_draw_registry", self.registry)
        self.assertNotIn("non_source_registry", self.registry)
        binding = self.registry["canonical_source_binding"]
        self.assertEqual(binding["registry_file"], "source_registry.json")
        source_registry = core.load_canonical_source_registry()
        self.assertEqual(
            binding["expected_source_draw_sha256"],
            core.source_draw_registry_sha256(source_registry),
        )


class SamplerConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry, cls.cell = core.load_registered_cell()

    def test_gamma_and_beta_are_distinct_implementations(self) -> None:
        gamma = core.gamma_radial_chunk(
            core.make_rng("gamma_radial"), 256, self.cell.e_star
        )
        with mock.patch.object(
            core,
            "gamma_radial_chunk",
            side_effect=AssertionError("Beta called Gamma"),
        ):
            beta = core.beta_radial_chunk(
                core.make_rng("beta_radial"), 256, self.cell.e_star
            )
        for values in (gamma, beta):
            self.assertEqual(values.shape, (256, 3))
            self.assertTrue(np.all(values > 0.0))
            self.assertLess(
                float(np.max(np.abs(values.sum(axis=1) - 1.0))),
                1.0e-14,
            )
        self.assertFalse(np.array_equal(gamma, beta))

    def test_full_source_has_fixed_word_count_and_shapes(self) -> None:
        source = core.full_source_chunk(
            core.make_rng("golden_replay"), 64, self.cell
        )
        self.assertEqual(source["raw_uniforms_per_sample"], 114)
        self.assertEqual(source["radial"].shape, (64, 3))
        self.assertEqual(source["u0"].shape, (64, 8))
        self.assertEqual([row.shape for row in source["chiral"]], [(64, 16)] * 4)
        self.assertEqual(source["q_unit"].shape, (64, 8))
        for block in [source["u0"], *source["chiral"]]:
            self.assertLess(
                float(np.max(np.abs((block * block).sum(axis=1) - 1.0))),
                1.0e-14,
            )

    def test_chiral_roundtrip_and_constraints_fast_profile(self) -> None:
        report = audit.build_report("fast")
        self.assertEqual(report["status"], "PASS_FAST_NONAUTHORITATIVE")
        self.assertFalse(report["authoritative_preregistered_profile"])
        self.assertEqual(report["ledger_size_executed"], 0)
        self.assertEqual(report["ledger_size_registered"], 514)
        self.assertEqual(report["constraint_checks"]["status"], "PASS")
        self.assertEqual(
            report["implementation_analytic_controls"]["chiral_jacobian"][
                "status"
            ],
            "PASS",
        )
        self.assertTrue(all(row["passed"] for row in report["hostile_mutations"]))

    def test_source_fingerprint_is_reproducible(self) -> None:
        first = audit.source_fingerprint(self.cell)
        second = audit.source_fingerprint(self.cell)
        self.assertEqual(first, second)
        self.assertEqual(first["samples"], 64)
        self.assertEqual(len(first["coefficient_sha256"]), 64)


class AnalyticLedgerTests(unittest.TestCase):
    def test_exact_dirichlet_moment_manifest(self) -> None:
        indices = core.moment_multi_indices()
        self.assertEqual(len(indices), 34)
        self.assertEqual(core.dirichlet_moment((1, 0, 0)), Fraction(2, 17))
        self.assertEqual(core.dirichlet_moment((0, 1, 0)), Fraction(15, 34))
        self.assertEqual(core.dirichlet_moment((2, 0, 0)), Fraction(2, 119))
        self.assertEqual(core.dirichlet_moment((1, 1, 0)), Fraction(6, 119))

    def test_fixed_familywise_contract(self) -> None:
        self.assertEqual(core.LEDGER_SIZE, 514)
        self.assertAlmostEqual(core.BERNSTEIN_LOG, 25.356051189967477)
        self.assertAlmostEqual(
            core.bernstein_threshold(
                core.dirichlet_variance((1, 0, 0)),
                core.FULL_RADIAL_SAMPLES,
            ),
            0.0003868795736665473,
        )
        decomposition = 34 + 34 + 34 + 64 + 48 + 216 + 72 + 12
        self.assertEqual(decomposition, core.LEDGER_SIZE)
        self.assertEqual(len(audit.torus_characters()), 32)


class CommittedReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not REPORT.exists():
            raise unittest.SkipTest("full report has not been generated")
        cls.report = core.load_strict_json(REPORT)

    def test_report_hash_status_and_ledger(self) -> None:
        self.assertTrue(core.verify_semantic_hash(self.report))
        self.assertEqual(self.report["status"], "PASS")
        self.assertEqual(self.report["failed_gates"], [])
        self.assertEqual(self.report["profile"], "full")
        self.assertEqual(len(self.report["ledger"]), 514)
        self.assertTrue(all(row["passed"] for row in self.report["ledger"]))
        self.assertLess(
            max(row["normalized_deviation"] for row in self.report["ledger"]),
            0.5,
        )

    def test_report_family_counts_and_hostile_rejections(self) -> None:
        family = self.report["family_summary"]
        self.assertEqual(sum(row["count"] for row in family.values()), 514)
        self.assertTrue(all(row["failed"] == 0 for row in family.values()))
        self.assertTrue(
            all(row["passed"] for row in self.report["hostile_mutations"])
        )
        shape_rows = [
            row
            for row in self.report["hostile_mutations"]
            if "normalized_rejection_margin" in row
        ]
        self.assertEqual(len(shape_rows), 3)
        self.assertGreater(
            min(row["normalized_rejection_margin"] for row in shape_rows),
            8.0,
        )

    def test_report_constraints_and_source_boundary(self) -> None:
        self.assertEqual(self.report["constraint_checks"]["status"], "PASS")
        self.assertEqual(
            self.report["source_draw_registry_sha256"],
            core.source_draw_registry_sha256(
                core.load_canonical_source_registry()
            ),
        )
        self.assertEqual(
            self.report["source_golden_fingerprint"],
            audit.source_fingerprint(core.load_registered_cell()[1]),
        )
        bridge = self.report["production_output_bridge"]
        self.assertEqual(bridge["status"], "PASS")
        self.assertEqual(
            bridge["production_source_draw_sha256"],
            self.report["source_draw_registry_sha256"],
        )

    def test_normalized_code_inventory_matches_checkout(self) -> None:
        self.assertEqual(self.report["code_inventory"], core.source_inventory())

    def test_report_semantics_survive_crlf_reformatting(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        crlf = core.loads_strict_json(text.replace("\n", "\r\n"))
        self.assertTrue(core.type_strict_equal(self.report, crlf))
        self.assertTrue(core.verify_semantic_hash(crlf))

    @unittest.skipUnless(
        os.environ.get("CYZ_RUN_FULL_0018_AUDIT") == "1",
        "set CYZ_RUN_FULL_0018_AUDIT=1 for full statistical replay",
    )
    def test_full_report_regenerates_semantically(self) -> None:
        regenerated = audit.build_report("full")
        core.strict_report_compare(self.report, regenerated)


class CliTests(unittest.TestCase):
    def test_fast_cli_is_explicitly_nonauthoritative(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--profile", "fast"],
            cwd=DIRECTORY.parent.parent,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads(completed.stdout)
        self.assertEqual(summary["status"], "PASS_FAST_NONAUTHORITATIVE")
        self.assertIsNone(summary["output"])


if __name__ == "__main__":
    unittest.main()
