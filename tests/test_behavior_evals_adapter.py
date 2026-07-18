#!/usr/bin/env python3
"""Behavioral tests for the semantic-adapter path of scripts/run-behavior-evals.py.

Exercises run_adapter against synthetic NDJSON adapters (pure stdlib python
scripts in a temp dir) with a single real eval case selected by ID.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "routing-outreach-vs-contract-helper-outreach-manager-001"

PASS_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": True, "evidence": "fixture ok"}))
"""

FAIL_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": False, "evidence": "fixture failure"}))
"""

DROP_ADAPTER = """\
import sys
for line in sys.stdin:
    pass
"""

GARBAGE_ADAPTER = """\
print("not json")
"""

BAD_SHAPE_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": True}))
"""

CRASH_ADAPTER = """\
import sys
sys.exit(3)
"""


def load_module():
    path = ROOT / "scripts" / "run-behavior-evals.py"
    spec = importlib.util.spec_from_file_location("run_behavior_evals", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def run_with(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "adapter.py"
            script.write_text(textwrap.dedent(source), encoding="utf-8")
            return self.module.run_adapter(
                "python3 %s" % script, {CASE_ID}, 60)

    def test_passing_adapter_returns_no_failures(self):
        self.assertEqual([], self.run_with(PASS_ADAPTER))

    def test_failing_case_is_reported(self):
        failures = self.run_with(FAIL_ADAPTER)
        self.assertEqual(["semantic adapter failed 1/1 cases"], failures)

    def test_dropped_case_is_a_coverage_mismatch(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(DROP_ADAPTER)
        self.assertIn("coverage mismatch", str(ctx.exception))

    def test_non_json_stdout_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(GARBAGE_ADAPTER)
        self.assertIn("not JSON", str(ctx.exception))

    def test_missing_evidence_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(BAD_SHAPE_ADAPTER)
        self.assertIn("evidence is required", str(ctx.exception))

    def test_adapter_crash_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(CRASH_ADAPTER)
        self.assertIn("exited 3", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
