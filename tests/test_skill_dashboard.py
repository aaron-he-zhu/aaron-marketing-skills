#!/usr/bin/env python3
"""Behavioral tests for Skill Dashboard projection, outcomes gating, and exclusion."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "skill-dashboard.py"
GUARD = ROOT / "scripts" / "check-skill-dashboard.py"
SCHEMA = ROOT / "references" / "skill-dashboard.schema.json"
BUILDER = ROOT / "scripts" / "build-distribution.py"
FIXTURES = ROOT / "tests" / "fixtures" / "skill-dashboard"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


dashboard = load_module("skill_dashboard_under_test", GENERATOR)


class SkillDashboardProjectionTests(unittest.TestCase):
    def test_schema_declares_required_modules_and_product_name(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual("Skill Dashboard view projection", schema["title"])
        self.assertEqual("Skill Dashboard", schema["properties"]["product"]["const"])
        modules = schema["properties"]["modules"]["properties"]
        for name in (
            "next", "usage", "delta", "outcomes", "decisions",
            "trust", "coverage", "staff",
        ):
            self.assertIn(name, modules)
        self.assertIn("timeline", modules)

    def test_empty_root_uses_honest_empty_states(self):
        view = dashboard.project(FIXTURES / "empty")
        self.assertEqual("Skill Dashboard", view["product"])
        self.assertFalse(view["boundaries"]["gateway"])
        self.assertFalse(view["boundaries"]["install_surface"])
        self.assertTrue(view["modules"]["next"]["empty"])
        self.assertTrue(view["modules"]["usage"]["empty"])
        self.assertTrue(view["modules"]["delta"]["empty"])
        self.assertFalse(view["modules"]["outcomes"]["bound"])
        self.assertIn("unvalidated/unbound", view["modules"]["outcomes"]["empty_state"])
        self.assertEqual([], view["modules"]["outcomes"]["readings"])
        self.assertFalse(view["modules"]["staff"]["present"])
        self.assertIn("8-bot", view["modules"]["staff"]["empty_state"])
        self.assertNotIn("timeline", view["modules"])
        html = dashboard.render_html(view)
        self.assertIn("<title>Skill Dashboard</title>", html)
        self.assertNotIn("Skill Usage Board", html)
        self.assertNotIn("0.99", html)

    def test_populated_projection_fills_required_modules(self):
        view = dashboard.project(FIXTURES / "populated")
        modules = view["modules"]
        self.assertEqual("review-cycle-retro", modules["next"]["next_action"])
        self.assertTrue(modules["next"]["open_loops"])
        usage = modules["usage"]["runs"][0]
        self.assertEqual(
            ["ad-creative-builder", "paid-measurement-loop"],
            usage["visited_skills"],
        )
        self.assertEqual("succeeded", usage["status"])
        self.assertIn("memory/ad/campaign-draft.md", modules["delta"]["work"]["before"])
        self.assertIn("memory/control/measurement-1.json", modules["delta"]["work"]["after"])
        quality = modules["delta"]["quality"][0]
        self.assertEqual("FIX", quality["before"]["verdict"])
        self.assertEqual("SHIP", quality["after"]["verdict"])
        outcomes = modules["outcomes"]
        self.assertTrue(outcomes["bound"])
        self.assertIsNone(outcomes["empty_state"])
        self.assertEqual("conversion_rate", outcomes["contracts"][0]["metric_id"])
        self.assertTrue(outcomes["contracts"][0]["supporting"]["evidence_observation"])
        self.assertTrue(outcomes["contracts"][0]["supporting"]["action_receipt"])
        self.assertTrue(outcomes["contracts"][0]["supporting"]["cycle_retro"])
        reading = outcomes["readings"][0]
        self.assertEqual(0.031, reading["before"])
        self.assertEqual(0.044, reading["after"])
        self.assertAlmostEqual(0.013, reading["delta"])
        self.assertEqual("measured", reading["numeric_state"])
        self.assertTrue(modules["decisions"]["propose"])
        self.assertTrue(modules["decisions"]["accept"])
        self.assertTrue(modules["trust"]["confidence"])
        ad = next(
            item for item in modules["coverage"]["disciplines"]
            if item["discipline"] == "ad"
        )
        self.assertGreaterEqual(ad["visited_count"], 1)
        self.assertEqual(16, ad["catalog_count"])
        self.assertTrue(modules["staff"]["present"])
        self.assertEqual(8, len(modules["staff"]["bots"]))
        self.assertEqual("aaron-ad", modules["staff"]["handoffs"][0]["from_bot"])
        self.assertTrue(modules["timeline"]["present"])
        self.assertEqual(3, len(modules["timeline"]["events"]))

    def test_outcomes_stay_unbound_without_measurement_contract(self):
        view = dashboard.project(FIXTURES / "unbound-outcomes")
        outcomes = view["modules"]["outcomes"]
        self.assertFalse(outcomes["bound"])
        self.assertEqual([], outcomes["readings"])
        self.assertEqual([], outcomes["contracts"])
        self.assertIn("unvalidated/unbound", outcomes["empty_state"])
        rendered = dashboard.render_html(view) + dashboard.render_md(view)
        self.assertNotIn("0.99", rendered)
        self.assertNotIn("12000", rendered)
        self.assertNotIn("conversion_rate", rendered)
        self.assertIn("unvalidated/unbound", rendered)
        self.assertEqual("content-writer", view["modules"]["usage"]["runs"][0]["skill"])
        self.assertFalse(view["modules"]["staff"]["present"])

    def test_cli_writes_html_json_and_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "skill-dashboard.html"
            result = subprocess.run(
                [
                    "python3",
                    str(GENERATOR),
                    "--root",
                    str(FIXTURES / "populated"),
                    "--out",
                    str(out),
                    "--json",
                    "--md",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertTrue(out.is_file())
            payload = json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))
            self.assertEqual("Skill Dashboard", payload["product"])
            markdown = out.with_suffix(".md").read_text(encoding="utf-8")
            self.assertTrue(markdown.startswith("# Skill Dashboard\n"))
            self.assertIn("## Next", markdown)
            self.assertIn("## Staff", markdown)


class SkillDashboardExclusionTests(unittest.TestCase):
    def test_guard_passes_on_the_real_repository(self):
        result = subprocess.run(
            ["python3", str(GUARD)], capture_output=True, text=True, cwd=ROOT
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("runtime exclusion holds", result.stdout)

    def test_dashboard_is_not_a_skill_and_stays_out_of_governed_closure(self):
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        self.assertEqual(120, len(plugin["skills"]))
        spec = importlib.util.spec_from_file_location("dashboard_builder_test", BUILDER)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        profile = module.resolve_plugin_profile(
            module.load_json(module.MANIFEST), "governed"
        )
        self.assertIn("apps", module.MAINTENANCE_TREES)
        for relative in (
            "scripts/skill-dashboard.py",
            "scripts/check-skill-dashboard.py",
            "references/skill-dashboard.schema.json",
            "docs/skill-dashboard.md",
        ):
            self.assertIn(relative, module.MAINTENANCE_EXACT)
            self.assertFalse(module.dependency_allowed(relative, profile))
        self.assertFalse(
            module.dependency_allowed("apps/skill-dashboard/index.html", profile)
        )
        leaked = [
            dep
            for dep in module.runtime_dependencies("README.md")
            if module.dependency_allowed(dep, profile)
            and "skill-dashboard" in dep
        ]
        self.assertEqual([], leaked)

    def test_user_facing_copy_keeps_the_official_product_name(self):
        for relative in (
            "docs/skill-dashboard.md",
            "docs/README.md",
            "README.md",
            "scripts/skill-dashboard.py",
        ):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("Skill Dashboard", text)
            self.assertNotIn("Skill Usage Board", text)
            self.assertNotIn("Skill Usage Dashboard", text)


if __name__ == "__main__":
    unittest.main()
