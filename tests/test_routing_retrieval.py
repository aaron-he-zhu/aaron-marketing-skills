#!/usr/bin/env python3
"""Behavioral tests for scripts/check-routing-retrieval.py."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check-routing-retrieval.py"
CASES = ROOT / "evals" / "routing-retrieval" / "cases.json"


class RoutingRetrievalTest(unittest.TestCase):
    def test_real_repository_passes(self):
        result = subprocess.run(
            ["python3", str(GUARD)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Focused ≤3 modules beat exhaustive dumps", result.stdout)

    def test_cases_are_focused(self):
        payload = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(payload["k"], 3)
        self.assertLessEqual(len(payload["cases"]), 32)
        for case in payload["cases"]:
            expected = case["expected_skills"]
            self.assertGreaterEqual(len(expected), 1, case["id"])
            self.assertLessEqual(len(expected), 3, case["id"])

    def test_suite_is_not_a_skill_package(self):
        self.assertFalse((ROOT / "evals" / "routing-retrieval" / "SKILL.md").exists())
        plugin = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        slugs = [entry.rstrip("/").split("/")[-1] for entry in plugin["skills"]]
        self.assertEqual(len(slugs), 120)
        self.assertNotIn("routing-retrieval", slugs)


if __name__ == "__main__":
    unittest.main()
