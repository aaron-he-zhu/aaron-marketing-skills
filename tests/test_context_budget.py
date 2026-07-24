#!/usr/bin/env python3
"""Behavioral tests for scripts/check-context-budget.py.

The guard derives ROOT from its own location, so copying it into a synthetic
fixture tree exercises pass/fail paths without touching the real repository.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check-context-budget.py"

AUDITOR_SKILL = """---
name: {name}
version: "1.0.0"
class: auditor
metadata: {{"author": "fixture", "version": "1.0.0"}}
---

# Auditor

## Instructions

### Runtime Contract

At activation, read these repository files:

1. `../../../references/auditor-runbook.md`
2. `../../../references/scoring-semantics.md`
3. `../../../references/{benchmark}`
4. `../../../references/framework-catalog.json` (`FIXTURE` entry)

For a standalone installation, read the bundled immutable `references/auditor-runtime.md` instead.
"""

PLAIN_SKILL = """---
name: {name}
version: "1.0.0"
metadata: {{"author": "fixture", "version": "1.0.0"}}
---

body
"""


def build_fixture(tmp, skill_name="fixture-auditor", body_lines=10,
                  benchmark="fixture-benchmark.md", benchmark_bytes=1000,
                  hot_lines=5, missing_hot=False, extra_skills=()):
    root = Path(tmp)
    (root / ".claude-plugin").mkdir(parents=True)
    skills = ["fixture/discipline/%s" % skill_name] + [
        "fixture/discipline/%s" % name for name in extra_skills]
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"skills": skills}), encoding="utf-8")
    body = "\n".join("line %d" % i for i in range(body_lines))
    for entry in skills:
        skill_dir = root / entry
        skill_dir.mkdir(parents=True)
        text = AUDITOR_SKILL if entry.endswith(skill_name) else PLAIN_SKILL
        (skill_dir / "SKILL.md").write_text(
            text.format(name=Path(entry).name, benchmark=benchmark) + body,
            encoding="utf-8")
    refs = root / "references"
    refs.mkdir()
    for name, size in (("auditor-runbook.md", 500), ("scoring-semantics.md", 400),
                       ("framework-catalog.json", 300), (benchmark, benchmark_bytes)):
        (refs / name).write_text("x" * size, encoding="utf-8")
    if not missing_hot:
        hot = root / "memory" / "templates"
        hot.mkdir(parents=True)
        (hot / "hot-cache.md").write_text(
            "\n".join("hot %d" % i for i in range(hot_lines)), encoding="utf-8")
    script_dir = root / "scripts"
    script_dir.mkdir()
    shutil.copy(GUARD, script_dir / GUARD.name)
    return root


def run_guard(root):
    return subprocess.run(
        ["python3", str(root / "scripts" / GUARD.name)],
        capture_output=True, text=True, cwd=root)


def add_auto_profile(root, shard_sizes):
    (root / "commands").mkdir(exist_ok=True)
    (root / "commands" / "auto.md").write_text("a" * 1000, encoding="utf-8")
    refs = root / "references"
    (refs / "aaron-product-api-contract.md").write_text("c" * 1000, encoding="utf-8")
    (refs / "auto-routing-scenarios.md").write_text("i" * 1000, encoding="utf-8")
    shards = refs / "auto-routing"
    shards.mkdir(exist_ok=True)
    sizes = list(shard_sizes)
    while len(sizes) < 8:
        sizes.append(100)
    for index, size in enumerate(sizes[:8]):
        (shards / ("shard-%d.md" % index)).write_text("s" * size, encoding="utf-8")


class ContextBudgetTest(unittest.TestCase):
    def test_real_repository_passes(self):
        result = subprocess.run(["python3", str(GUARD)], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_clean_fixture_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp))
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_oversized_skill_body_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, body_lines=300))
            self.assertEqual(result.returncode, 1)
            self.assertIn("extract detail into references/", result.stdout)

    def test_oversized_activation_chain_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, benchmark_bytes=200_000))
            self.assertEqual(result.returncode, 1)
            self.assertIn("activation chain", result.stdout)

    def test_generated_runtime_not_counted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture(tmp)
            # auditor-runtime.md is named in the fixture contract; if it were
            # counted as an activation read the (absent) file would error.
            result = run_guard(root)
            self.assertEqual(result.returncode, 0, result.stdout)

    def test_missing_hot_template_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, missing_hot=True))
            self.assertEqual(result.returncode, 1)
            self.assertIn("hot-cache.md missing", result.stdout)

    def test_oversized_hot_template_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_guard(build_fixture(tmp, hot_lines=120))
            self.assertEqual(result.returncode, 1)
            self.assertIn("HOT limit", result.stdout)

    def test_auditor_without_runtime_section_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture(tmp)
            skill = root / "fixture/discipline/fixture-auditor/SKILL.md"
            skill.write_text(skill.read_text().replace("### Runtime Contract", "### Other"),
                             encoding="utf-8")
            result = run_guard(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no references/ activation reads", result.stdout)

    def test_oversized_nested_reference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture(tmp)
            nested = root / "references" / "nested"
            nested.mkdir()
            (nested / "oversized.md").write_text("x" * 60_000, encoding="utf-8")
            result = run_guard(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("references/nested/oversized.md", result.stdout)

    def test_oversized_auto_assembly_fails_even_when_each_shard_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture(tmp)
            add_auto_profile(root, [40_000, 30_000, 20_000])
            result = run_guard(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("assembled context", result.stdout)

    def test_bounded_auto_assembly_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = build_fixture(tmp)
            add_auto_profile(root, [20_000, 10_000, 5_000])
            result = run_guard(root)
            self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
