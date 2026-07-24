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

**Current release**: `{bundle}` (2026-01-01).

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
        "disciplines": {
            "narrative": {
                "phase_order": ["trace"],
                "phases": {"trace": ["fixture-skill"]},
            },
        },
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
    write(root, "SECURITY.md",
          "# Security Policy\n\n"
          "| Version | Supported |\n"
          "|---------|-----------|\n"
          "| 1.x | Yes (current line) |\n"
          "| < 1 | No |\n")
    write(root, "VERSIONS.md", VERSIONS_MD.format(bundle=BUNDLE))
    write(root, ".github/repo-about.json",
          json.dumps({"description": "2 fixture skills"}))
    write(root, "narrative/trace/fixture-skill/SKILL.md",
          SKILL_MD.format(name="fixture-skill", bundle=BUNDLE))
    write(root, "protocol/protocol-skill/SKILL.md",
          SKILL_MD.format(name="protocol-skill", bundle=BUNDLE))
    write(root, "evals/auto-routing-scenarios.source.md",
          '- expected_route: "/aaron-marketing:narrative"\n')
    write(root, "commands/narrative.md", "Route: fixture-skill\n")
    write(root, "narrative/README.md", "skills: fixture-skill\n")
    write(root, "narrative/README.zh.md", "技能: fixture-skill\n")
    (root / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy(GUARD, root / "scripts" / "check-versions.sh")


def build_release_fixture(root: Path) -> None:
    """Build the exact 120-skill cohort required by release-only mode."""
    build_fixture(root)
    (root / "narrative/trace/fixture-skill/SKILL.md").unlink()
    narrative_skills = ["fixture-skill-%03d" % index for index in range(1, 120)]
    skill_paths = [
        "./narrative/trace/%s" % name for name in narrative_skills
    ] + ["./protocol/protocol-skill"]
    write(root, ".claude-plugin/plugin.json", json.dumps({
        "version": BUNDLE,
        "skills": skill_paths,
    }, indent=2) + "\n")
    write(root, "references/system-catalog.json", json.dumps({
        "bundle_version": BUNDLE,
        "commands": ["auto", "narrative"],
        "disciplines": {
            "narrative": {
                "phase_order": ["trace"],
                "phases": {"trace": narrative_skills},
            },
        },
        "protocol": {"skills": ["protocol-skill"]},
    }))
    for name in narrative_skills:
        write(
            root,
            "narrative/trace/%s/SKILL.md" % name,
            SKILL_MD.format(name=name, bundle=BUNDLE),
        )
    rows = [
        "| %s | narrative | %s | 2026-01-01 |" % (name, BUNDLE)
        for name in narrative_skills
    ]
    rows.append("| protocol-skill | protocol | %s | 2026-01-01 |" % BUNDLE)
    write(
        root,
        "VERSIONS.md",
        "# Versions\n\n"
        "**Current release**: `%s` (2026-01-01).\n\n"
        "### v%s — Fixture release (2026-01-01)\n\n"
        "| skill | category | version | date |\n"
        "|-------|----------|---------|------|\n%s\n"
        % (BUNDLE, BUNDLE, "\n".join(rows)),
    )
    topology_en = (
        "**120 marketing skills** in this bundle.\n\n"
        "| Layer | Skills | Loop | Frameworks | Entry |\n"
        "|-------|--------|------|------------|-------|\n"
        "| L1 | 119 | T | F | `/aaron-marketing:narrative` |\n"
        "| L4 | 1 | - | - | — |\n\n"
        "| `/aaron-marketing:auto` | auto |\n"
        "| `/aaron-marketing:narrative` | narrative |\n"
    )
    topology_zh = (
        "**120 个营销技能**。\n\n"
        "| 层 | 技能 | 循环 | 框架 | 入口 |\n"
        "|----|------|------|------|------|\n"
        "| L1 | 119 | T | F | `/aaron-marketing:narrative` |\n"
        "| L4 | 1 | - | - | — |\n\n"
        "| `/aaron-marketing:auto` | auto |\n"
        "| `/aaron-marketing:narrative` | narrative |\n"
    )
    write(
        root,
        "README.md",
        "![v](https://img.shields.io/badge/version-%s-orange)\n\n"
        "- **[VERSIONS.md](VERSIONS.md)** — changelog (current bundle: `%s`).\n\n"
        "current bundle: `%s`\n\n%s" % (BUNDLE, BUNDLE, BUNDLE, topology_en),
    )
    write(
        root,
        "docs/README.zh.md",
        "![v](https://img.shields.io/badge/version-%s-orange)\n\n"
        "- **[VERSIONS.md](VERSIONS.md)** — 更新日志（当前包：`%s`）。\n\n"
        "当前包：`%s`\n\n%s" % (BUNDLE, BUNDLE, BUNDLE, topology_zh),
    )
    all_names = narrative_skills + ["protocol-skill"]
    write(
        root,
        "CLAUDE.md",
        "Current bundle version: `%s`\n\n%s\n" % (BUNDLE, "\n".join(all_names)),
    )
    write(root, ".github/repo-about.json",
          json.dumps({"description": "120 fixture skills"}))
    skill_inventory = "\n".join(narrative_skills)
    write(root, "commands/narrative.md", "Route:\n%s\n" % skill_inventory)
    write(root, "narrative/README.md", "skills:\n%s\n" % skill_inventory)
    write(root, "narrative/README.zh.md", "技能:\n%s\n" % skill_inventory)


class CheckVersionsTests(unittest.TestCase):
    def run_guard(self, mutate=None, args=None, release_fixture=False):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            if release_fixture:
                build_release_fixture(fixture)
            else:
                build_fixture(fixture)
            if mutate is not None:
                mutate(fixture)
            result = subprocess.run(
                ["bash", "scripts/check-versions.sh", *(args or [])],
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
            write(root, "evals/auto-routing-scenarios.source.md", "# empty\n")
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

    def test_security_supported_major_drift_fails(self):
        def mutate(root):
            write(root, "SECURITY.md",
                  "# Security Policy\n\n"
                  "| Version | Supported |\n"
                  "|---------|-----------|\n"
                  "| 9.x | Yes (current line) |\n"
                  "| < 9 | No |\n")
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("current supported major 9 != bundle major 1", out)
        self.assertIn("unsupported boundary 9 != bundle major 1", out)

    def test_missing_security_policy_fails_closed(self):
        def mutate(root):
            (root / "SECURITY.md").unlink()
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("SECURITY.md missing", out)

    def test_extra_discipline_in_catalog_extends_routing_guard(self):
        # The discipline list is derived from the catalog: an 8th discipline
        # with no routing scenario must fail the routing guard automatically.
        def mutate(root):
            catalog = json.loads(
                (root / "references/system-catalog.json").read_text(encoding="utf-8"))
            catalog["disciplines"]["podcast"] = {
                "phase_order": ["plan"],
                "phases": {"plan": []},
            }
            write(root, "references/system-catalog.json", json.dumps(catalog))
        code, out = self.run_guard(mutate)
        self.assertEqual(1, code, out)
        self.assertIn("/aaron-marketing:podcast (auto routing coverage gap)", out)

    def test_normal_mode_allows_per_skill_patch_skew(self):
        def mutate(root):
            path = root / "narrative/trace/fixture-skill/SKILL.md"
            write(
                root,
                "narrative/trace/fixture-skill/SKILL.md",
                path.read_text(encoding="utf-8").replace(BUNDLE, "1.0.1"),
            )
            versions = (root / "VERSIONS.md").read_text(encoding="utf-8")
            write(
                root,
                "VERSIONS.md",
                versions.replace(
                    "| fixture-skill | narrative | 1.0.0 | 2026-01-01 |",
                    "| fixture-skill | narrative | 1.0.1 | 2026-01-02 |",
                ),
            )
        code, out = self.run_guard(mutate)
        self.assertEqual(0, code, out)
        self.assertIn("version-sync clean", out)

    def test_release_mode_accepts_exact_120_skill_cohort(self):
        code, out = self.run_guard(
            args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(0, code, out)
        self.assertIn("release-all-current cohort is exactly 120/120", out)

    def test_release_mode_rejects_non_120_cohort(self):
        code, out = self.run_guard(args=["--release-all-current"])
        self.assertEqual(1, code, out)
        self.assertIn(
            "release-all-current requires exactly 120 catalog skill targets; found 2",
            out,
        )

    def test_release_mode_ignores_incidental_skill_outside_catalog(self):
        def mutate(root):
            write(
                root,
                "narrative/trace/incidental-skill/SKILL.md",
                SKILL_MD.format(name="incidental-skill", bundle=BUNDLE),
            )
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(0, code, out)
        self.assertIn("release-all-current cohort is exactly 120/120", out)
        self.assertNotIn("incidental-skill", out)

    def test_release_mode_rejects_missing_catalog_target(self):
        def mutate(root):
            (
                root
                / "narrative/trace/fixture-skill-001/SKILL.md"
            ).unlink()
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn(
            "catalog target is missing: "
            "narrative/trace/fixture-skill-001/SKILL.md",
            out,
        )

    def test_release_mode_rejects_duplicate_catalog_target(self):
        def mutate(root):
            catalog_path = root / "references/system-catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["disciplines"]["narrative"]["phases"]["trace"].append(
                "fixture-skill-001"
            )
            write(root, "references/system-catalog.json", json.dumps(catalog))
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn("catalog has duplicate skill targets", out)
        self.assertIn("catalog has duplicate skill IDs: fixture-skill-001", out)

    def test_release_mode_rejects_noncanonical_catalog_path_component(self):
        def mutate(root):
            catalog_path = root / "references/system-catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["disciplines"]["narrative"]["phases"]["trace"][0] = (
                "../outside"
            )
            write(root, "references/system-catalog.json", json.dumps(catalog))
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn(
            "catalog skill is not a canonical path component: "
            "narrative/trace/'../outside'",
            out,
        )

    def test_release_mode_rejects_patch_skew(self):
        def mutate(root):
            relative = "narrative/trace/fixture-skill-001/SKILL.md"
            text = (root / relative).read_text(encoding="utf-8")
            write(root, relative, text.replace(BUNDLE, "1.0.1"))
            versions = (root / "VERSIONS.md").read_text(encoding="utf-8")
            write(
                root,
                "VERSIONS.md",
                versions.replace(
                    "| fixture-skill-001 | narrative | 1.0.0 | 2026-01-01 |",
                    "| fixture-skill-001 | narrative | 1.0.1 | 2026-01-02 |",
                ),
            )
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn("top-level version 1.0.1 != bundle 1.0.0", out)
        self.assertIn("metadata.version '1.0.1' != bundle 1.0.0", out)
        self.assertIn("date 2026-01-02 != release date 2026-01-01", out)

    def test_release_mode_rejects_row_date_drift(self):
        def mutate(root):
            versions = (root / "VERSIONS.md").read_text(encoding="utf-8")
            write(
                root,
                "VERSIONS.md",
                versions.replace(
                    "| fixture-skill-001 | narrative | 1.0.0 | 2026-01-01 |",
                    "| fixture-skill-001 | narrative | 1.0.0 | 2026-01-02 |",
                ),
            )
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn("date 2026-01-02 != release date 2026-01-01", out)

    def test_release_mode_rejects_invalid_iso_date(self):
        def mutate(root):
            versions = (root / "VERSIONS.md").read_text(encoding="utf-8")
            write(
                root,
                "VERSIONS.md",
                versions.replace(
                    "**Current release**: `1.0.0` (2026-01-01).",
                    "**Current release**: `1.0.0` (2026-99-99).",
                ).replace("2026-01-01 |", "2026-99-99 |"),
            )
        code, out = self.run_guard(
            mutate, args=["--release-all-current"], release_fixture=True,
        )
        self.assertEqual(1, code, out)
        self.assertIn("Current release date is invalid: 2026-99-99", out)
        self.assertIn("has an invalid date: 2026-99-99", out)

    def test_unknown_flag_fails_closed(self):
        code, out = self.run_guard(args=["--surprise"])
        self.assertEqual(2, code, out)
        self.assertIn("usage: scripts/check-versions.sh", out)


if __name__ == "__main__":
    unittest.main()
