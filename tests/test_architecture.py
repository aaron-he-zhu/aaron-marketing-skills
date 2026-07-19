#!/usr/bin/env python3
"""Regression tests for typed system-catalog architecture invariants."""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module():
    path = ROOT / "scripts" / "check-architecture.py"
    spec = importlib.util.spec_from_file_location("check_architecture", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_generator_module():
    path = ROOT / "scripts" / "generate-system-docs.py"
    spec = importlib.util.spec_from_file_location("generate_system_docs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GeneratorAtomicWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_generator_module()

    def test_atomic_write_preserves_existing_permissions(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "generated.md"
            target.write_bytes(b"old")
            target.chmod(0o640)
            self.module.atomic_write(target, b"new")
            self.assertEqual(target.read_bytes(), b"new")
            self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o640)

    def test_atomic_write_does_not_require_os_fchmod(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(
                self.module.os, "fchmod", None):
            target = Path(tmp) / "generated.md"
            self.module.atomic_write(target, b"portable")
            self.assertEqual(target.read_bytes(), b"portable")

    def test_atomic_write_closes_fd_and_cleans_temp_when_fdopen_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "generated.md"
            real_close = os.close
            with mock.patch.object(
                    self.module.os, "fdopen", side_effect=OSError("fixture failure")), \
                    mock.patch.object(self.module.os, "close", wraps=real_close) as close:
                with self.assertRaisesRegex(OSError, "fixture failure"):
                    self.module.atomic_write(target, b"new")
            close.assert_called_once()
            self.assertEqual(list(Path(tmp).iterdir()), [])


class CatalogLayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        with (ROOT / "references" / "system-catalog.json").open(encoding="utf-8") as handle:
            cls.catalog = json.load(handle)

    def failures_for(self, catalog):
        failures = []
        paths = self.module.expected_skill_paths(catalog, failures)
        self.module.check_catalog_shape(catalog, paths, failures)
        return failures

    def test_current_layer_declarations_match_membership(self):
        self.assertEqual([], self.failures_for(copy.deepcopy(self.catalog)))

    def test_discipline_layer_declaration_cannot_contradict_membership(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["disciplines"]["narrative"]["layer"] = "L2"
        failures = self.failures_for(catalog)
        self.assertTrue(
            any("narrative declares layer 'L2' but layer membership is 'L1'" in item for item in failures),
            failures,
        )

    def test_protocol_layer_declaration_cannot_contradict_membership(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["protocol"]["layer"] = "L3"
        failures = self.failures_for(catalog)
        self.assertTrue(
            any("protocol declares layer 'L3' but layer membership is 'L4'" in item for item in failures),
            failures,
        )

    def test_bare_root_runtime_commands_are_detected(self):
        self.assertIsNotNone(
            self.module.BARE_ROOT_RUNTIME_COMMAND.search(
                "Run python3 scripts/rubric-score.py score run.json"
            )
        )
        self.assertIsNone(
            self.module.BARE_ROOT_RUNTIME_COMMAND.search(
                'python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score run.json'
            )
        )


class SymmetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        with (ROOT / "references" / "system-catalog.json").open(encoding="utf-8") as handle:
            cls.catalog = json.load(handle)

    def symmetry_failures(self, catalog):
        failures = []
        paths = self.module.expected_skill_paths(catalog, failures)
        self.module.check_symmetry(catalog, paths, failures)
        return failures

    def test_pristine_catalog_has_no_symmetry_failures(self):
        self.assertEqual([], self.symmetry_failures(copy.deepcopy(self.catalog)))

    def test_dropped_deviation_surfaces_the_licensed_violation(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["symmetry"]["deviations"] = [
            item for item in catalog["symmetry"]["deviations"]
            if item["id"] != "DEV-HUMANVIEW-LAUNCHES"
        ]
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("SYM-09-human-view at registry:launches" in item for item in failures),
            failures,
        )

    def test_stale_deviation_fails(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["symmetry"]["deviations"].append({
            "id": "DEV-STALE-EXAMPLE",
            "rule": "SYM-05-owner-naming",
            "scope": "registry:consent",
            "rationale": "test",
            "since_version": "18.0.0",
        })
        failures = self.symmetry_failures(catalog)
        self.assertTrue(any("stale deviation" in item for item in failures), failures)

    def test_corrupted_loop_string_fails(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["disciplines"]["email"]["loop"] = "Setup -> Engage -> Nurture -> Delivery"
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("SYM-01-loop-derived at discipline:email" in item for item in failures),
            failures,
        )

    def test_loop_name_must_match_phase_initials(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["disciplines"]["influencer"]["loop_name"] = "CAST"
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("SYM-02-loop-acronym at discipline:influencer" in item for item in failures),
            failures,
        )

    def test_wrong_score_surface_name_fails(self):
        catalog = copy.deepcopy(self.catalog)
        for entry in catalog["auditors"]:
            if entry["skill"] == "ad-account-auditor":
                entry["score_surface"]["name"] = "XQS"
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("SYM-11-score-surface-consistent at auditor:ad-account-auditor" in item
                for item in failures),
            failures,
        )

    def test_composite_score_on_profiles_only_gate_fails(self):
        catalog = copy.deepcopy(self.catalog)
        for entry in catalog["auditors"]:
            if entry["skill"] == "launch-readiness-auditor":
                entry["score_surface"] = {
                    "type": "composite", "name": "LRS", "rollup": "weighted-arithmetic-mean",
                }
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("auditor:launch-readiness-auditor" in item for item in failures),
            failures,
        )

    def test_unknown_deviation_rule_or_scope_fails(self):
        catalog = copy.deepcopy(self.catalog)
        catalog["symmetry"]["deviations"].append({
            "id": "DEV-BOGUS",
            "rule": "SYM-99-nonexistent",
            "scope": "discipline:seo-geo",
            "rationale": "test",
            "since_version": "18.0.0",
        })
        failures = self.symmetry_failures(catalog)
        self.assertTrue(
            any("unknown rule or scope" in item for item in failures),
            failures,
        )


class DistributionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()
        with (ROOT / "references" / "system-catalog.json").open(encoding="utf-8") as handle:
            cls.catalog = json.load(handle)

    def distribution_failures(self):
        failures = []
        paths = self.module.expected_skill_paths(self.catalog, failures)
        self.module.check_distribution(self.catalog, paths, failures)
        return failures

    def test_pristine_distribution_surfaces_have_no_failures(self):
        self.assertEqual([], self.distribution_failures())

    def test_openclaw_version_drift_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted = Path(tmp) / "openclaw.plugin.json"
            payload = json.loads((ROOT / "openclaw.plugin.json").read_text(encoding="utf-8"))
            payload["version"] = "0.0.0"
            drifted.write_text(json.dumps(payload), encoding="utf-8")
            original = self.module.OPENCLAW_PATH
            self.module.OPENCLAW_PATH = drifted
            try:
                failures = self.distribution_failures()
            finally:
                self.module.OPENCLAW_PATH = original
        self.assertTrue(
            any("openclaw.plugin.json version" in item for item in failures),
            failures,
        )

    def test_openclaw_description_drift_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            drifted = Path(tmp) / "openclaw.plugin.json"
            payload = json.loads((ROOT / "openclaw.plugin.json").read_text(encoding="utf-8"))
            payload["description"] = "stale"
            drifted.write_text(json.dumps(payload), encoding="utf-8")
            original = self.module.OPENCLAW_PATH
            self.module.OPENCLAW_PATH = drifted
            try:
                failures = self.distribution_failures()
            finally:
                self.module.OPENCLAW_PATH = original
        self.assertTrue(
            any("openclaw.plugin.json description" in item for item in failures),
            failures,
        )


if __name__ == "__main__":
    unittest.main()
