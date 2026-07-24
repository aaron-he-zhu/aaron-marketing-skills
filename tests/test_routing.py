#!/usr/bin/env python3
"""Behavioral tests for scripts/check-routing.py against fixture skill trees.

The lint derives ROOT from its own location, so copying it into a synthetic
fixture exercises pass/fail paths without touching the real repository.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check-routing.py"

SKILL_MD = """---
name: {name}
version: "1.0.0"
description: '{description}'
metadata: {{"author": "fixture", "version": "1.0.0"}}
---

body

## Next Best Skill

{next_best}
"""


def build_fixture(tmp, descriptions, next_best=None):
    """descriptions: {skill_name: description}; returns fixture root."""
    root = Path(tmp)
    (root / ".claude-plugin").mkdir(parents=True)
    skills = ["fixture/discipline/%s" % name for name in descriptions]
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"skills": skills}), encoding="utf-8")
    for entry, description in zip(skills, descriptions.values()):
        skill_dir = root / entry
        skill_dir.mkdir(parents=True)
        handoff = (next_best or {}).get(skill_dir.name, "chain-complete")
        (skill_dir / "SKILL.md").write_text(
            SKILL_MD.format(name=skill_dir.name, description=description,
                            next_best=handoff),
            encoding="utf-8")
    script_dir = root / "scripts"
    script_dir.mkdir()
    shutil.copy(GUARD, script_dir / GUARD.name)
    return root


def run_guard(root):
    return subprocess.run(
        ["python3", str(root / "scripts" / GUARD.name)],
        capture_output=True, text=True, cwd=root)


class RoutingLintTest(unittest.TestCase):
    def test_real_repository_passes(self):
        result = subprocess.run(["python3", str(GUARD)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_distinct_triggers_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do alpha work". Not for beta — use beta-skill.',
                "beta-skill": 'Use when the user asks to "do beta work". Not for alpha — use alpha-skill.',
            }))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_shared_quoted_trigger_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do the work" or "alpha it". Not for beta.',
                "beta-skill": 'Use when the user asks to "do the work" or "beta it". Not for alpha.',
            }))
            self.assertEqual(result.returncode, 1)
            self.assertIn("do the work", result.stdout)
            self.assertIn("coin-flip", result.stdout)

    def test_case_insensitive_collision_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "Audit Our Content". Not for beta.',
                "beta-skill": 'Use when the user asks to "audit our content". Not for alpha.',
            }))
            self.assertEqual(result.returncode, 1)

    def test_missing_boundary_clause_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do alpha work" and produce reports.',
                "beta-skill": 'Use when the user asks to "do beta work". Not for alpha.',
            }))
            self.assertEqual(result.returncode, 1)
            self.assertIn("boundary clause", result.stdout)

    def test_short_quoted_fragments_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "alpha" and more. Not for beta.',
                "beta-skill": 'Use when the user asks to "beta" and more. Not for alpha.',
            }))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_dangling_bare_name_handoff_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do alpha work". Not for beta.',
                "beta-skill": 'Use when the user asks to "do beta work". Not for alpha.',
            }, next_best={
                "alpha-skill": "Route to `gamma-skill` when beta is not needed.",
                "beta-skill": "chain-complete",
            }))
            self.assertEqual(result.returncode, 1)
            self.assertIn("gamma-skill", result.stdout)
            self.assertIn("dangling", result.stdout)

    def test_resolving_bare_name_handoff_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do alpha work". Not for beta.',
                "beta-skill": 'Use when the user asks to "do beta work". Not for alpha.',
            }, next_best={
                "alpha-skill": "Route to `beta-skill` when beta is needed.",
                "beta-skill": "chain-complete",
            }))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_link_form_handoff_not_double_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, {
                "alpha-skill": 'Use when the user asks to "do alpha work". Not for beta.',
                "beta-skill": 'Use when the user asks to "do beta work". Not for alpha.',
            }, next_best={
                "alpha-skill": "Primary: [beta-skill](../beta-skill/SKILL.md).",
                "beta-skill": "chain-complete",
            }))
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
