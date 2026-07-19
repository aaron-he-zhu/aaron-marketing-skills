#!/usr/bin/env python3
"""Behavioral tests for scripts/audit-trends.py against fixture artifacts."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "audit-trends.py"

ARTIFACT = """---
class: auditor-output
schema_version: "3.0"
runbook_version: "3.0.0"
catalog_version: "1.0"
framework: {framework}
profile: {profile}
---
status: DONE
verdict: {verdict}
score_state: SCORED
objective: fixture audit
target: {target}
observed_at: {observed_at}
veto_count: 0
cap_applied: false
raw_overall_score: {score}
final_overall_score: {score}
"""


def put_artifact(root, framework, profile, target, observed_at, verdict, score, name):
    sink = Path(root) / "memory" / "audits" / "content"
    sink.mkdir(parents=True, exist_ok=True)
    (sink / name).write_text(
        ARTIFACT.format(framework=framework, profile=profile, target=target,
                        observed_at=observed_at, verdict=verdict, score=score),
        encoding="utf-8")


def run_tool(root, *extra):
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *extra],
        capture_output=True, text=True, cwd=root)


class AuditTrendsTest(unittest.TestCase):
    def test_empty_project_reports_no_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_tool(tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("No parseable", result.stdout)

    def test_converging_series_shows_positive_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(tmp, "CORE-EEAT", "blog-post", "https://x.test/a",
                         "2026-06-01", "FIX", 55, "a1.md")
            put_artifact(tmp, "CORE-EEAT", "blog-post", "https://x.test/a",
                         "2026-07-01", "SHIP", 78, "a2.md")
            result = run_tool(tmp, "--json")
            self.assertEqual(result.returncode, 0)
            data = json.loads(result.stdout)
            self.assertEqual(len(data["series"]), 1)
            series = data["series"][0]
            self.assertEqual(series["score_delta"], 23)
            self.assertEqual(series["latest_verdict"], "SHIP")
            self.assertFalse(series["stalled"])

    def test_stalled_series_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            for i, score in enumerate((50, 52, 51), 1):
                put_artifact(tmp, "SEND", "lifecycle", "welcome-flow",
                             "2026-05-0%d" % i, "FIX", score, "s%d.md" % i)
            result = run_tool(tmp)
            self.assertEqual(result.returncode, 0)
            self.assertIn("STALLED", result.stdout)
            self.assertIn("NOT converging", result.stdout)

    def test_framework_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(tmp, "CORE-EEAT", "blog-post", "t1", "2026-06-01", "SHIP", 80, "a.md")
            put_artifact(tmp, "ROAS", "account", "t2", "2026-06-01", "FIX", 61, "b.md")
            data = json.loads(run_tool(tmp, "--json", "--framework", "ROAS").stdout)
            self.assertEqual(len(data["series"]), 1)
            self.assertEqual(data["series"][0]["framework"], "ROAS")

    def test_unparseable_files_are_skipped_not_fatal(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = Path(tmp) / "memory" / "audits" / "content"
            sink.mkdir(parents=True)
            (sink / "junk.md").write_text("not an artifact\n", encoding="utf-8")
            put_artifact(tmp, "ECHO", "program", "t", "2026-06-01", "SHIP", 88, "ok.md")
            data = json.loads(run_tool(tmp, "--json").stdout)
            self.assertEqual(data["artifacts"], 1)
            self.assertEqual(data["skipped_unparseable"], 1)


if __name__ == "__main__":
    unittest.main()
