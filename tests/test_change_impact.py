"""Risk-tier classification tests for the v19 CI split."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location(
    "change_impact", ROOT / "scripts" / "classify-change-impact.py"
)
assert SPEC and SPEC.loader
change_impact = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = change_impact
SPEC.loader.exec_module(change_impact)


class ChangeImpactTests(unittest.TestCase):
    def test_documentation_and_localization_are_s0(self):
        result = change_impact.classify_paths(["README.md", "docs/README.zh.md"])
        self.assertEqual(result["severity"], "S0")

    def test_ordinary_skill_is_s1_but_auditor_and_consent_are_s3(self):
        ordinary = change_impact.classify_paths(
            ["seo-geo/implement/content-writer/SKILL.md"]
        )
        self.assertEqual(ordinary["severity"], "S1")
        for path in (
            "seo-geo/tune/content-quality-auditor/SKILL.md",
            "protocol/consent-registry/SKILL.md",
        ):
            with self.subTest(path=path):
                self.assertEqual(
                    change_impact.classify_paths([path])["severity"],
                    "S3",
                )

    def test_catalog_and_routing_are_s2(self):
        result = change_impact.classify_paths(
            ["references/system-catalog.json", "commands/auto.md"]
        )
        self.assertEqual(result["severity"], "S2")

    def test_runtime_publisher_hook_schema_and_workflow_default_s3(self):
        for path in (
            "scripts/new-runtime-helper.py",
            "scripts/publish-package.sh",
            "hooks/new-hook.sh",
            "references/new-control.schema.json",
            ".github/workflows/new.yml",
        ):
            with self.subTest(path=path):
                self.assertEqual(
                    change_impact.classify_paths([path])["severity"],
                    "S3",
                )

    def test_highest_severity_wins_and_paths_are_deterministic(self):
        result = change_impact.classify_paths(
            [
                "README.md",
                "seo-geo/implement/content-writer/SKILL.md",
                "scripts/runtime-controller.py",
            ]
        )
        self.assertEqual(result["severity"], "S3")
        self.assertEqual(
            [entry["path"] for entry in result["paths"]],
            sorted(entry["path"] for entry in result["paths"]),
        )

    def test_unsafe_paths_fail_closed(self):
        for path in ("../escape", "/absolute", "a/./b"):
            with self.subTest(path=path):
                with self.assertRaises(change_impact.ImpactError):
                    change_impact.classify_paths([path])

    def test_github_output_is_compact_and_machine_readable(self):
        result = change_impact.classify_paths(
            ["seo-geo/implement/content-writer/SKILL.md"]
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "output"
            change_impact._write_github_output(path, result)
            text = path.read_text(encoding="utf-8")
        self.assertIn("tier=S1\n", text)
        self.assertIn("changed_count=1\n", text)
        self.assertIn(
            'changed_skills=["seo-geo/implement/content-writer/SKILL.md"]\n',
            text,
        )


if __name__ == "__main__":
    unittest.main()
