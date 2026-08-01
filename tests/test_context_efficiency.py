#!/usr/bin/env python3
"""Unit tests for assembled-context efficiency measurement and policy gates."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-context-efficiency.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aaron_context_efficiency", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(skill, route, required, selected):
    return {
        "target_skill": skill,
        "route_kind": route,
        "distribution_profile": "repository",
        "required_bytes": required,
        "selected_bytes": selected,
        "inspection_bytes": selected * 2,
        "required_budget_share": round(required / 1000, 6),
        "selected_budget_share": round(selected / 1000, 6),
    }


class ContextEfficiencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_summary_separates_direct_and_auto_and_names_worst(self):
        records = [
            record("a", "direct", 100, 200),
            record("b", "direct", 300, 400),
            record("a", "auto", 200, 300),
            record("b", "auto", 500, 600),
        ]
        summary = self.module._summary(records)
        self.assertEqual(summary["direct"]["required_bytes"]["p50"], 100)
        self.assertEqual(summary["auto"]["required_bytes"]["max"], 500)
        self.assertEqual(summary["auto"]["worst_required"]["target_skill"], "b")

    def test_policy_distinguishes_guardrails_from_non_gating_targets(self):
        records = [
            record("a", "direct", 100, 200),
            record("a", "auto", 200, 300),
        ]
        report = {
            "records": records,
            "summary": self.module._summary(records),
            "discovery": {"description_plus_when_to_use_bytes": 400},
        }
        policy = {
            "schema_version": "1.0",
            "description": "fixture",
            "guardrails": {
                "max_required_bytes": 250,
                "max_required_budget_share": 0.25,
                "max_p50_selected_bytes": 350,
                "max_description_plus_when_to_use_bytes": 500,
            },
            # A deliberately impossible target is advisory and does not fail
            # the Phase-0 regression guard.
            "targets": {"max_normal_initial_model_visible_bytes": 1},
        }
        self.assertEqual(self.module.evaluate_policy(report, policy), [])
        policy["guardrails"]["max_required_bytes"] = 199
        failures = self.module.evaluate_policy(report, policy)
        self.assertEqual(len(failures), 1)
        self.assertIn("max required bytes", failures[0])


if __name__ == "__main__":
    unittest.main()
