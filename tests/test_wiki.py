#!/usr/bin/env python3
"""Behavioral tests for scripts/check-wiki.py and the runtime-exclusion rule."""
from __future__ import annotations

import importlib.util
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
BUILDER = ROOT / "scripts" / "build-distribution.py"


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

    def test_governed_closure_rejects_wiki_and_check_scripts(self):
        spec = importlib.util.spec_from_file_location("wiki_builder_test", BUILDER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        profile = module.resolve_plugin_profile(
            module.load_json(module.MANIFEST), "governed")
        self.assertIn("references/wiki", module.MAINTENANCE_TREES)
        self.assertIn("scripts/check-wiki.py", module.MAINTENANCE_EXACT)
        self.assertIn("scripts/check-routing-retrieval.py", module.MAINTENANCE_EXACT)
        self.assertFalse(module.dependency_allowed("references/wiki/index.md", profile))
        self.assertFalse(module.dependency_allowed("scripts/check-wiki.py", profile))
        self.assertFalse(
            module.dependency_allowed("scripts/check-routing-retrieval.py", profile))
        readme_deps = module.runtime_dependencies("README.md")
        shipped = [
            dep for dep in readme_deps
            if module.dependency_allowed(dep, profile)
            and (dep.startswith("references/wiki") or dep.startswith("scripts/check-"))
        ]
        self.assertEqual([], shipped)


if __name__ == "__main__":
    unittest.main()
