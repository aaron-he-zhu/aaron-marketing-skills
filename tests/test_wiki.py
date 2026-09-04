#!/usr/bin/env python3
"""Behavioral tests for scripts/check-wiki.py and the runtime-exclusion rule."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check-wiki.py"
SCHEMA = ROOT / "references" / "wiki" / "SCHEMA.md"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
MODULES = ROOT / "references" / "context-modules.json"
DISTRIBUTION = ROOT / "references" / "distribution-files.json"


class WikiLintTest(unittest.TestCase):
    def test_real_repository_passes(self):
        result = subprocess.run(
            ["python3", str(GUARD)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("runtime exclusion holds", result.stdout)

    def test_schema_forbids_runtime_injection(self):
        text = SCHEMA.read_text(encoding="utf-8")
        self.assertIn("Runtime must not inject wiki.", text)
        self.assertIn("not a Skill", text)

    def test_wiki_is_not_a_skill_and_not_in_runtime_defaults(self):
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(len(plugin["skills"]), 120)
        self.assertFalse((ROOT / "references" / "wiki" / "SKILL.md").exists())
        modules = MODULES.read_text(encoding="utf-8")
        self.assertNotIn("references/wiki", modules)
        distribution = DISTRIBUTION.read_text(encoding="utf-8")
        self.assertNotIn("references/wiki", distribution)


if __name__ == "__main__":
    unittest.main()
