#!/usr/bin/env python3
"""Behavioral tests for scripts/check-versions.sh against a minimal fixture repo.

The guard cds to its own parent directory, so copying it into a synthetic
fixture tree lets us exercise both the clean pass and per-surface failures
without touching the real repository.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "check-versions.sh"
BUNDLE = "1.0.0"

FRAMEWORK_LINES = [
    "**CORE-EEAT** (80 items, 8 dimensions)",
    "**CITE** (40 items, 4 dimensions)",
    "**STAR** (S Suitability / T Trust / A Appeal / R Return",
    "**ROAS** (R Return / O Offer / A Audience / S Spend-efficiency",
    "**SEND** (S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response",
    "**RAMP** (40 stable IDs across R Readiness / A Assets / M Momentum / P Proof",
    "**ECHO** (40 stable IDs across E Embeddedness / C Craft / H Hosting / O Observability",
    "**TALE** (T Truth / A Architecture / L Landing / E Evidence",
]

SKILL_MD = """---
name: {name}
version: "{bundle}"
metadata: {{"author": "fixture", "version": "{bundle}"}}
---

body
"""

VERSIONS_MD = """# Versions

**Current release**: `{bundle}`

### v{bundle} — Fixture release (2026-01-01)

| skill | category | version | date |
|-------|----------|---------|------|
| fixture-skill | narrative | {bundle} | 2026-01-01 |
| protocol-skill | protocol | {bundle} | 2026-01-01 |
"""

TOPOLOGY_EN = """**2 marketing skills** in this bundle.

| Layer | Skills | Loop | Frameworks | Entry |
|-------|--------|------|------------|-------|
| L1 | 1 | T | F | `/aaron-marketing:narrative` |
| L4 | 1 | - | - | — |

| `/aaron-marketing:auto` | auto |
| `/aaron-marketing:narrative` | narrative |
"""

TOPOLOGY_ZH = """**2 个营销技能**。

| 层 | 技能 | 循环 | 框架 | 入口 |
|----|------|------|------|------|
| L1 | 1 | T | F | `/aaron-marketing:narrative` |
| L4 | 1 | - | - | — |

| `/aaron-marketing:auto` | auto |
| `/aaron-marketing:narrative` | narrative |
"""


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_fixture(root: Path) -> None:
    write(root, ".claude-plugin/plugin.json",
          '{\n  "version": "%s",\n  "skills": []\n}\n' % BUNDLE)
    write(root, "marketplace.json", '{"plugins": [{"version": "%s"}]}\n' % BUNDLE)
    write(root, ".claude-plugin/marketplace.json",
          '{"plugins": [{"version": "%s"}]}\n' % BUNDLE)
    write(root, "openclaw.plugin.json", '{"version": "%s"}\n' % BUNDLE)
    write(root, "references/system-catalog.json", json.dumps({
        "bundle_version": BUNDLE,
        "commands": ["auto", "narrative"],
        "disciplines": {"narrative": {"phases": {"trace": ["fixture-skill"]}}},
        "protocol": {"skills": ["protocol-skill"]},
    }))
    write(root, "references/framework-catalog.json",
          '{"catalog_version": "%s"}\n' % BUNDLE)
    write(root, "README.md",
          "![v](https://img.shields.io/badge/version-%s-orange)\n\n"
          "- **[VERSIONS.md](VERSIONS.md)** — changelog (current bundle: `%s`).\n\n"
          "current bundle: `%s`\n\n%s" % (BUNDLE, BUNDLE, BUNDLE, TOPOLOGY_EN))
    write(root, "docs/README.zh.md",
          "![v](https://img.shields.io/badge/version-%s-orange)\n\n"
          "- **[VERSIONS.md](VERSIONS.md)** — 更新日志（当前包：`%s`）。\n\n"
          "当前包：`%s`\n\n%s" % (BUNDLE, BUNDLE, BUNDLE, TOPOLOGY_ZH))
    for lang in ("de", "es", "fr", "it", "ja", "ko", "pt", "zh-Hant"):
        write(root, "docs/README.%s.md" % lang,
              "![v](https://img.shields.io/badge/version-%s-orange)\n\n"
              "- **[VERSIONS.md](VERSIONS.md)** — changelog (current bundle: `%s`).\n"
              % (BUNDLE, BUNDLE))
    write(root, "CLAUDE.md",
          "Current bundle version: `%s`\n\nfixture-skill\nprotocol-skill\n" % BUNDLE)
    write(root, "AGENTS.md",
          "- **Current bundle**: %s\n"
          "120 skills (16 × 7 disciplines + 8 protocol)\n"
          "8 commands\n%s\n" % (BUNDLE, "\n".join(FRAMEWORK_LINES)))
    write(root, "VERSIONS.md", VERSIONS_MD.format(bundle=BUNDLE))
    write(root, ".github/repo-about.json",
          json.dumps({"description": "2 fixture skills"}))
    write(root, "narrative/trace/fixture-skill/SKILL.md",
          SKILL_MD.format(name="fixture-skill", bundle=BUNDLE))
    write(root, "protocol/protocol-skill/SKILL.md",
          SKILL_MD.format(name="protocol-skill", bundle=BUNDLE))
    write(root, "references/auto-routing-scenarios.md",
          '- expected_route: "/aaron-marketing:narrative"\n')
    write(root, "commands/narrative.md", "Route: fixture-skill\n")
    write(root, "narrative/README.md", "skills: fixture-skill\n")
    write(root, "narrative/README.zh.md", "技能: fixture-skill\n")
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(GUARD, root / "scripts" / "check-versions.sh")


class CheckVersionsTests(unittest.TestCase):
    def run_guard(self, mutate=None):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            build_fixture(fixture)
            if mutate is not None:
                mutate(fixture)
            result = subprocess.run(
                ["bash", "scripts/check-versions.sh"],
                cwd=fixture, capture_output=True, text=True,
            )
            return result.returncode, result.stdout + result.stderr

    def test_pristine_fixture_passes(self):
        code, out = self.run_guard()
        self.assertEqual(0, code, out)
        self.assertIn("version-sync clean", out)

    def test_marketplace_version_drift_fails(self):
        def mutate(root):
            write(root, "marketplace.json", '{"plugins": [{"version": "9.9.9"}]}\n')
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("9.9.9 != bundle 1.0.0", out)

    def test_missing_versions_row_fails(self):
        def mutate(root):
            text = (root / "VERSIONS.md").read_text(encoding="utf-8")
            write(root, "VERSIONS.md",
                  text.replace("| protocol-skill | protocol | 1.0.0 | 2026-01-01 |\n", ""))
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("protocol-skill: no row in VERSIONS.md", out)

    def test_missing_routing_scenario_fails(self):
        def mutate(root):
            write(root, "references/auto-routing-scenarios.md", "# empty\n")
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("auto routing coverage gap", out)

    def test_command_coverage_gap_fails(self):
        def mutate(root):
            write(root, "commands/narrative.md", "Route: nothing\n")
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("command coverage gap", out)

    def test_catalog_bundle_drift_fails(self):
        def mutate(root):
            catalog = json.loads(
                (root / "references/system-catalog.json").read_text(encoding="utf-8"))
            catalog["bundle_version"] = "9.9.9"
            write(root, "references/system-catalog.json", json.dumps(catalog))
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("bundle_version 9.9.9 != bundle 1.0.0", out)

    def test_extra_discipline_in_catalog_extends_routing_guard(self):
        # The discipline list is derived from the catalog: an 8th discipline
        # with no routing scenario must fail the routing guard automatically.
        def mutate(root):
            catalog = json.loads(
                (root / "references/system-catalog.json").read_text(encoding="utf-8"))
            catalog["disciplines"]["podcast"] = {"phases": {"plan": []}}
            write(root, "references/system-catalog.json", json.dumps(catalog))
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("/aaron-marketing:podcast (auto routing coverage gap)", out)


if __name__ == "__main__":
    unittest.main()
