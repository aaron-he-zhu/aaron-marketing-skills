#!/usr/bin/env python3
"""Behavioral tests for scripts/validate-skill.sh per-skill mode.

Builds a minimal spec-compliant fixture skill in a temp directory and
asserts both the clean pass and one failure per frontmatter/contract rule.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.sh"

VALID_SKILL = """---
name: fixture-skill
version: "1.0.0"
description: 'Use when the user asks to "exercise the fixture validator"; produces a fixed report. Not for real skills.'
license: Apache-2.0
compatibility: claude-code
metadata: {"author": "fixture", "version": "1.0.0", "discipline": "narrative", "phase": "trace"}
slug: fixture-skill
displayName: Fixture Skill · 夹具技能
summary: 用于验证校验器的夹具技能
when_to_use: exercising the validator fixture
argument-hint: "<input>"
---

# Fixture Skill

## Quick Start

Run the fixture.

## Skill Contract

- Reads: nothing.

## Data Sources

None.

## Instructions

1. Do nothing.

## Reference Materials

None.

## Next Best Skill

- stop — terminal fixture, no handoff.

### Handoff Summary

- status: complete
"""


class ValidateSkillTests(unittest.TestCase):
    def run_validator(self, content: str, dirname: str = "fixture-skill"):
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "narrative" / "trace" / dirname
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
            result = subprocess.run(
                ["bash", str(VALIDATOR), str(skill_dir)],
                capture_output=True, text=True,
            )
            return result.returncode, result.stdout + result.stderr

    def test_valid_fixture_passes(self):
        code, out = self.run_validator(VALID_SKILL)
        self.assertEqual(0, code, out)
        self.assertIn("0 failed", out)

    def test_missing_slug_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "slug: fixture-skill\n", ""))
        self.assertEqual(1, code, out)
        self.assertIn("Missing required field: slug", out)

    def test_yaml_block_metadata_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            'metadata: {"author": "fixture", "version": "1.0.0", "discipline": "narrative", "phase": "trace"}\n',
            'metadata:\n  author: fixture\n  version: "1.0.0"\n'))
        self.assertEqual(1, code, out)
        self.assertIn("single-line JSON", out)

    def test_name_must_match_directory(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "name: fixture-skill", "name: other-skill", 1), dirname="fixture-skill")
        self.assertEqual(1, code, out)
        self.assertIn("does not match directory", out)

    def test_missing_handoff_summary_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "### Handoff Summary\n", "### Notes\n"))
        self.assertEqual(1, code, out)
        self.assertIn("Missing shared contract handoff section", out)

    def test_unescaped_apostrophe_in_single_quoted_scalar_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "summary: 用于验证校验器的夹具技能",
            "summary: 'it's broken'"))
        self.assertEqual(1, code, out)
        self.assertIn("unescaped apostrophe", out)

    def test_blob_main_url_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "Run the fixture.",
            "See https://github.com/x/y/blob/main/references/z.md"))
        self.assertEqual(1, code, out)
        self.assertIn("blob/tree URL", out)

    def test_hyphenated_when_to_use_key_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "when_to_use:", "when-to-use:"))
        self.assertEqual(1, code, out)
        self.assertIn("underscores", out)

    def test_slug_outside_convention_fails(self):
        code, out = self.run_validator(VALID_SKILL.replace(
            "slug: fixture-skill", "slug: someone-elses-skill"))
        self.assertEqual(1, code, out)
        self.assertIn("must be 'fixture-skill' (preferred) or 'aaron-fixture-skill'", out)


if __name__ == "__main__":
    unittest.main()
