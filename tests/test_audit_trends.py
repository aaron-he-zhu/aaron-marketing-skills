#!/usr/bin/env python3
"""Behavioral tests for evidence-bound audit convergence telemetry."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import uuid


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "audit-trends.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


trends = load_module("audit_trends_test_module", TOOL)
loop = load_module("audit_trends_test_loop", ROOT / "scripts" / "audit-loop.py")

SINKS = {
    "CORE-EEAT": "content", "ROAS": "ad", "SEND": "email", "ECHO": "social",
}
DEFAULTS = {
    "CORE-EEAT": (
        "blog-post",
        {"content_type": "blog-post", "market": "US", "publication_state": "draft"},
    ),
    "ROAS": (
        "direct-response",
        {
            "currency": "USD", "window": "2026-Q2", "conversion_lag": "30d",
            "business_constraint": "profitable-growth", "goal": "direct-response",
        },
    ),
    "SEND": (
        "newsletter",
        {
            "program_type": "newsletter", "provider": "fixture-provider",
            "window": "2026-Q2", "list_age": "mature", "market": "US",
            "mpp_share": "unknown",
        },
    ),
    "ECHO": (
        "asset-gate",
        {
            "assessment_mode": "asset", "program_archetype": "not-applicable",
            "channels": ["linkedin"], "window": "2026-Q2", "market": "US",
        },
    ),
}


def artifact(
        framework="CORE-EEAT", profile=None, target="asset-1",
        observed_at="2026-07-19", verdict="FIX", score=60,
        confidence="medium", coverage=None, context=None, catalog_version="18.0.0"):
    default_profile, default_context = DEFAULTS[framework]
    profile = profile or default_profile
    context = dict(context or default_context)
    if verdict == "FIX":
        status, score_state = "DONE_WITH_CONCERNS", "SCORED"
        coverage = 100 if coverage is None else coverage
        confidence_value = confidence
        scores = "raw_overall_score: %d\nfinal_overall_score: %d\n" % (score, score)
    elif verdict == "SHIP":
        status, score_state = "DONE", "SCORED"
        coverage = 100 if coverage is None else coverage
        confidence_value = confidence
        scores = "raw_overall_score: %d\nfinal_overall_score: %d\n" % (score, score)
    elif verdict == "UNDECIDED":
        status, score_state = "NEEDS_INPUT", "NOT_SCORED"
        coverage = 40 if coverage is None else coverage
        confidence_value = "not_scored"
        scores = ""
    else:
        raise ValueError("unsupported fixture verdict")
    return """---
class: auditor-output
schema_version: "3.0"
runbook_version: "3.0.0"
catalog_version: "{catalog_version}"
framework: {framework}
profile: {profile}
---
status: {status}
verdict: {verdict}
score_state: {score_state}
objective: Verify convergence for the declared fixture target
target: {target}
observed_at: {observed_at}
context: {context}
key_findings: []
evidence_summary: Exact deterministic fixture evidence was reviewed
evidence_coverage: {coverage}
score_confidence: {confidence}
open_loops: Owner remediation remains external to this telemetry
recommended_next_skill: content-brief-generator
veto_count: 0
cap_applied: false
{scores}""".format(
        catalog_version=catalog_version, framework=framework, profile=profile,
        status=status, verdict=verdict, score_state=score_state, target=target,
        observed_at=observed_at,
        context=json.dumps(context, sort_keys=True, separators=(",", ":")),
        coverage=coverage, confidence=confidence_value, scores=scores,
    )


def put_artifact(root, name, **values):
    framework = values.get("framework", "CORE-EEAT")
    sink = Path(root) / "memory" / "audits" / SINKS[framework]
    sink.mkdir(parents=True, exist_ok=True)
    path = sink / name
    path.write_text(artifact(**values), encoding="utf-8")
    return path


def run_tool(root, *extra):
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *extra],
        capture_output=True, text=True, cwd=root,
    )


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class LoopFixture:
    def __init__(self, root, baseline, reaudit):
        self.root = Path(root)
        self.baseline = Path(baseline)
        self.reaudit = Path(reaudit)
        self.run_id = str(uuid.uuid4())
        self.loop_id = str(uuid.uuid4())
        self.counter = 0
        loop.runtime.append_event(self.root, self.run_id, {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "idempotency_key": "run-start",
            "event_type": "run_started",
            "occurred_at": "2026-07-19T10:00:00Z",
            "actor": {"type": "system", "id": "test-host"},
            "parent_event_id": None,
            "turn_id": None,
            "status": "started",
            "subject": {"kind": "run", "ref": self.run_id},
            "references": [],
            "metrics": {},
            "dimensions": {},
        })
        records = self.root / "memory" / "runs" / "records"
        records.mkdir(parents=True, exist_ok=True)
        self.proposal = records / (self.loop_id + "-proposal.json")
        self.intervention = records / (self.loop_id + "-intervention.json")
        self.proposal.write_text('{"proposal":"owner review required"}\n', encoding="utf-8")
        self.intervention.write_text('{"result":"owner completed change"}\n', encoding="utf-8")

    def relative(self, path):
        return Path(path).relative_to(self.root).as_posix()

    def time(self):
        self.counter += 1
        return "2026-07-19T10:00:%02dZ" % self.counter

    def start(self):
        return loop.apply_action(
            "start", root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="start", expected_previous_sha256=loop.ZERO_HASH,
            occurred_at=self.time(), deadline="2026-07-19T11:00:00Z",
            max_cycles=2, max_retries=1,
            audit_ref=self.relative(self.baseline), audit_sha256=digest(self.baseline),
        )

    def lease(self, head, token):
        return loop.apply_action(
            "acquire-lease", root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="lease-" + token,
            expected_previous_sha256=head["step_sha256"], occurred_at=self.time(),
            lease_owner="workflow-host", lease_token=token, lease_ttl=60,
        )

    def action(self, action, head, token, **values):
        return loop.apply_action(
            action, root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key=action + "-1",
            expected_previous_sha256=head["step_sha256"], occurred_at=self.time(),
            lease_generation=head["step"]["lease"]["generation"],
            lease_token=token, **values,
        )

    def build(self):
        head = self.start()
        head = self.lease(head, "proposal")
        head = self.action(
            "proposal", head, "proposal", proposal_ref=self.relative(self.proposal),
            proposal_sha256=digest(self.proposal),
        )
        head = self.lease(head, "owner")
        head = self.action("owner", head, "owner", owner_id="owner-1", decision="accept")
        head = self.lease(head, "intervention")
        head = self.action(
            "intervention", head, "intervention",
            intervention_ref=self.relative(self.intervention),
            intervention_sha256=digest(self.intervention),
        )
        head = self.lease(head, "reaudit")
        return self.action(
            "reaudit", head, "reaudit", audit_ref=self.relative(self.reaudit),
            audit_sha256=digest(self.reaudit),
        )


class AuditTrendsTest(unittest.TestCase):
    def test_empty_project_reports_no_series_and_separate_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_tool(tmp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["artifacts"], 0)
            self.assertEqual(data["duplicate_artifacts"], 0)
            self.assertEqual(data["skipped_invalid_audits"], 0)
            self.assertEqual(data["skipped_invalid_loop_steps"], 0)

    def test_empty_project_human_output_escapes_hostile_root_controls(self):
        with tempfile.TemporaryDirectory() as parent:
            hostile = Path(parent) / "root\x1b[2J"
            hostile.mkdir()
            result = run_tool(hostile)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\x1b", result.stdout)
            self.assertIn("root\\x1b[2J", result.stdout)

    def test_context_change_makes_score_delta_non_comparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first = put_artifact(
                tmp, "a1.md", target="article-a", observed_at="2026-06-01",
                verdict="FIX", score=55, confidence="medium",
            )
            changed = dict(DEFAULTS["CORE-EEAT"][1], publication_state="published")
            latest = put_artifact(
                tmp, "a2.md", target="article-a", observed_at="2026-07-01",
                verdict="SHIP", score=78, confidence="high", context=changed,
            )
            result = run_tool(tmp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            row = json.loads(result.stdout)["series"][0]
            self.assertFalse(row["score_comparable"])
            self.assertIsNone(row["score_delta"])
            self.assertEqual(row["latest_verdict"], "SHIP")
            self.assertEqual(row["first_artifact_sha256"], digest(first))
            self.assertEqual(row["latest_artifact_sha256"], digest(latest))
            self.assertEqual(row["artifact_sha256"], digest(latest))
            self.assertEqual(row["schema_version"], "3.0")
            self.assertEqual(row["runbook_version"], "3.0.0")
            self.assertEqual(row["catalog_version"], "18.0.0")
            self.assertEqual(row["schema_versions"], ["3.0"])
            self.assertEqual(row["runbook_versions"], ["3.0.0"])
            self.assertEqual(row["catalog_versions"], ["18.0.0"])
            self.assertFalse(row["catalog_drift"])
            self.assertEqual(row["context_changes"], 1)
            self.assertNotEqual(row["first_context_sha256"], row["latest_context_sha256"])
            self.assertEqual(row["evidence_coverage_delta"], 0)
            self.assertEqual(row["confidence_delta"], 1)
            self.assertEqual(row["unlinked_audit_transitions"], 1)

    def test_same_catalog_and_context_scores_remain_comparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(
                tmp, "a1.md", target="article-a", observed_at="2026-06-01",
                verdict="FIX", score=55,
            )
            put_artifact(
                tmp, "a2.md", target="article-a", observed_at="2026-07-01",
                verdict="SHIP", score=78,
            )
            row = json.loads(run_tool(tmp, "--json").stdout)["series"][0]
            self.assertTrue(row["score_comparable"])
            self.assertEqual(row["score_delta"], 23)

    def test_stalled_series_and_framework_filter_preserve_prior_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, score in enumerate((50, 52, 51), 1):
                put_artifact(
                    tmp, "s%d.md" % index, framework="SEND", target="welcome-flow",
                    observed_at="2026-05-0%d" % index, verdict="FIX", score=score,
                )
            put_artifact(
                tmp, "paid.md", framework="ROAS", target="account-2",
                observed_at="2026-06-01", verdict="FIX", score=61,
            )
            human = run_tool(tmp, "--framework", "SEND")
            self.assertEqual(human.returncode, 0, human.stderr)
            self.assertIn("STALLED", human.stdout)
            self.assertIn("NOT converging", human.stdout)
            data = json.loads(run_tool(tmp, "--json", "--framework", "ROAS").stdout)
            self.assertEqual(len(data["series"]), 1)
            self.assertEqual(data["series"][0]["framework"], "ROAS")
            self.assertIn("latest_scored_score", data["series"][0])

    def test_latest_not_scored_never_reuses_score_and_uses_confidence_rank_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(
                tmp, "scored.md", framework="SEND", target="welcome-flow",
                observed_at="2026-06-01", verdict="FIX", score=55,
                confidence="medium",
            )
            put_artifact(
                tmp, "unscored.md", framework="SEND", target="welcome-flow",
                observed_at="2026-07-01", verdict="UNDECIDED", coverage=40,
            )
            result = run_tool(tmp, "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            row = json.loads(result.stdout)["series"][0]
            self.assertEqual(row["latest_score_state"], "NOT_SCORED")
            self.assertIsNone(row["latest_score"])
            self.assertEqual(row["latest_scored_score"], 55)
            self.assertEqual(row["latest_scored_at"], "2026-06-01")
            self.assertEqual(row["evidence_coverage_delta"], -60)
            self.assertEqual(row["confidence_delta"], -2)

    def test_invalid_audits_symlink_hardlink_and_duplicate_json_never_become_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            valid = put_artifact(
                tmp, "valid.md", target="valid", observed_at="2026-07-01",
                verdict="SHIP", score=82,
            )
            sink = valid.parent
            outside = Path(tmp) / "outside.md"
            outside.write_text(artifact(target="symlink"), encoding="utf-8")
            (sink / "symlink.md").symlink_to(outside)
            hard_source = put_artifact(tmp, "hard-source.md", target="hard")
            os.link(hard_source, sink / "hard-copy.md")
            duplicate = artifact(target="duplicate-json").replace(
                '"content_type":"blog-post"',
                '"content_type":"blog-post","content_type":"comparison"',
            )
            (sink / "duplicate-json.md").write_text(duplicate, encoding="utf-8")
            data = json.loads(run_tool(tmp, "--json").stdout)
            self.assertEqual(data["artifacts"], 1)
            self.assertEqual(data["skipped_invalid_audits"], 4)
            self.assertEqual(data["series"][0]["target"], "valid")

    def test_exact_duplicate_artifacts_are_counted_once_without_fake_stall(self):
        with tempfile.TemporaryDirectory() as tmp:
            original = put_artifact(
                tmp, "a.md", target="one-state", observed_at="2026-07-01",
                verdict="FIX", score=60,
            )
            for name in ("b.md", "c.md"):
                (original.parent / name).write_bytes(original.read_bytes())
            artifacts, skipped = trends.collect(tmp)
            self.assertEqual((len(artifacts), skipped), (1, 0))
            data = json.loads(run_tool(tmp, "--json").stdout)
            self.assertEqual(data["artifacts"], 1)
            self.assertEqual(data["duplicate_artifacts"], 2)
            self.assertEqual(data["series"][0]["audits"], 1)
            self.assertFalse(data["series"][0]["stalled"])
            self.assertEqual(data["unlinked_audit_transitions"], 0)

    def test_bounded_audit_scan_fails_closed_instead_of_returning_partial_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = Path(tmp) / "memory" / "audits" / "content"
            sink.mkdir(parents=True)
            for index in range(trends.MAX_AUDIT_FILES + 1):
                (sink / ("%03d.md" % index)).write_text("invalid\n", encoding="utf-8")
            result = run_tool(tmp, "--json")
            self.assertEqual(result.returncode, 1)
            self.assertIn("file limit", result.stderr)
            self.assertEqual(result.stdout, "")

    def test_exact_validated_loop_step_links_intervention_to_audit_hash_pair(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "baseline.md", target="article-a", observed_at="2026-07-18",
                verdict="FIX", score=60,
            )
            reaudit = put_artifact(
                tmp, "reaudit.md", target="article-a", observed_at="2026-07-20",
                verdict="SHIP", score=86, confidence="high",
            )
            fixture = LoopFixture(tmp, baseline, reaudit)
            final = fixture.build()
            data = json.loads(run_tool(tmp, "--json").stdout)
            row = data["series"][0]
            self.assertEqual(data["valid_loop_steps"], 9)
            self.assertEqual(data["skipped_invalid_loop_steps"], 0)
            self.assertEqual(data["linked_interventions"], 1)
            self.assertEqual(data["unlinked_audit_transitions"], 0)
            self.assertEqual(len(row["linked_interventions"]), 1)
            link = row["linked_interventions"][0]
            self.assertEqual(link["from_artifact_sha256"], digest(baseline))
            self.assertEqual(link["to_artifact_sha256"], digest(reaudit))
            self.assertEqual(link["loop_step_sha256"], final["step_sha256"])
            self.assertEqual(link["intervention_sha256"], digest(fixture.intervention))

    def test_nonadjacent_verified_loop_edge_is_preserved_as_series_intervention(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "a.md", target="article-a", observed_at="2026-07-18",
                verdict="FIX", score=60,
            )
            put_artifact(
                tmp, "b.md", target="article-a", observed_at="2026-07-19",
                verdict="FIX", score=70,
            )
            reaudit = put_artifact(
                tmp, "c.md", target="article-a", observed_at="2026-07-20",
                verdict="SHIP", score=86, confidence="high",
            )
            LoopFixture(tmp, baseline, reaudit).build()
            data = json.loads(run_tool(tmp, "--json").stdout)
            row = data["series"][0]
            self.assertEqual(row["audits"], 3)
            self.assertEqual(data["linked_interventions"], 1)
            self.assertEqual(data["unlinked_audit_transitions"], 2)
            self.assertEqual(len(row["linked_interventions"]), 1)
            self.assertEqual(
                row["linked_interventions"][0]["from_artifact_sha256"],
                digest(baseline),
            )
            self.assertEqual(
                row["linked_interventions"][0]["to_artifact_sha256"],
                digest(reaudit),
            )
            self.assertTrue(all(
                not transition["linked_interventions"]
                for transition in row["audit_transitions"]
            ))

    def test_loop_step_bytes_are_bounded_across_the_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "baseline.md", target="article-a", observed_at="2026-07-18",
                verdict="FIX", score=60,
            )
            reaudit = put_artifact(
                tmp, "reaudit.md", target="article-a", observed_at="2026-07-20",
                verdict="SHIP", score=86,
            )
            LoopFixture(tmp, baseline, reaudit).build()
            LoopFixture(tmp, baseline, reaudit).build()
            audits, skipped = trends.collect(tmp)
            self.assertEqual(skipped, 0)
            directories, unsafe = trends._loop_directories(
                Path(tmp), trends.time.monotonic() + 10,
            )
            self.assertEqual((len(directories), unsafe), (2, 0))
            loop_bytes = [
                trends._candidate_step_inventory(
                    loop_dir, trends.time.monotonic() + 10,
                )[1]
                for _run_id, _loop_id, loop_dir in directories
            ]
            self.assertTrue(all(value > 0 for value in loop_bytes))
            partial_second_loop = loop_bytes[0] + max(1, loop_bytes[1] // 2)
            with mock.patch.object(
                    trends, "MAX_LOOP_STEP_TOTAL_BYTES", partial_second_loop):
                with self.assertRaisesRegex(trends.AuditTrendError, "byte aggregate"):
                    trends.collect_loop_links(tmp, audits)

    def test_tampered_intervention_or_invalid_loop_json_is_separately_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "baseline.md", target="article-a", observed_at="2026-07-18",
                verdict="FIX", score=60,
            )
            reaudit = put_artifact(
                tmp, "reaudit.md", target="article-a", observed_at="2026-07-20",
                verdict="SHIP", score=86,
            )
            fixture = LoopFixture(tmp, baseline, reaudit)
            fixture.build()
            fixture.intervention.write_text('{"result":"tampered"}\n', encoding="utf-8")
            data = json.loads(run_tool(tmp, "--json").stdout)
            self.assertEqual(data["linked_interventions"], 0)
            self.assertEqual(data["unlinked_audit_transitions"], 1)
            self.assertEqual(data["skipped_invalid_audits"], 0)
            self.assertEqual(data["skipped_invalid_loop_steps"], 1)

        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "baseline.md", target="article-a", observed_at="2026-07-18",
                verdict="FIX", score=60,
            )
            reaudit = put_artifact(
                tmp, "reaudit.md", target="article-a", observed_at="2026-07-20",
                verdict="SHIP", score=86,
            )
            fixture = LoopFixture(tmp, baseline, reaudit)
            final = fixture.build()
            step = Path(tmp) / final["step_ref"]
            text = step.read_text(encoding="utf-8")
            step.write_text(text.replace('"state":', '"state":"converged","state":', 1),
                            encoding="utf-8")
            data = json.loads(run_tool(tmp, "--json").stdout)
            self.assertEqual(data["linked_interventions"], 0)
            self.assertEqual(data["unlinked_audit_transitions"], 1)
            self.assertGreaterEqual(data["skipped_invalid_loop_steps"], 1)

    def test_loop_audit_identity_requires_every_exact_bound_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            baseline = put_artifact(
                tmp, "baseline.md", target="article-a", observed_at="2026-07-01",
                verdict="FIX", score=60,
            )
            audits, skipped = trends.collect(tmp)
            self.assertEqual(skipped, 0)
            current = audits[0]
            identity = {
                "sha256": current["artifact_sha256"],
                **{name: current.get(name) for name in trends.AUDIT_IDENTITY_FIELDS},
            }
            self.assertTrue(trends._audit_identity_matches(identity, current))
            for field in (
                    "schema_version", "runbook_version", "catalog_version",
                    "target_identity_sha256", "context_sha256", "observed_at",
                    "evidence_coverage", "score_confidence"):
                misbound = dict(identity)
                misbound[field] = (
                    99 if field == "evidence_coverage" else "f" * 64
                )
                self.assertFalse(
                    trends._audit_identity_matches(misbound, current), field,
                )

    def test_same_date_unlinked_order_is_date_path_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(
                tmp, "a.md", target="same-date", observed_at="2026-07-01",
                verdict="FIX", score=60,
            )
            put_artifact(
                tmp, "z.md", target="same-date", observed_at="2026-07-01",
                verdict="SHIP", score=80,
            )
            row = json.loads(run_tool(tmp, "--json").stdout)["series"][0]
            self.assertEqual(row["latest_verdict"], "SHIP")
            self.assertEqual(row["unlinked_audit_transitions"], 1)
            self.assertEqual(row["order_basis"], "date-path")
            self.assertEqual(row["audit_transitions"][0]["order_basis"], "date-path")

    def test_relapse_and_compressed_verdict_and_score_oscillation_are_typed(self):
        with tempfile.TemporaryDirectory() as tmp:
            values = (
                ("a.md", "2026-07-01", "FIX", 60),
                ("b.md", "2026-07-02", "SHIP", 80),
                ("c.md", "2026-07-03", "FIX", 70),
                ("d.md", "2026-07-04", "SHIP", 90),
            )
            for name, date, verdict, score in values:
                put_artifact(
                    tmp, name, target="oscillating", observed_at=date,
                    verdict=verdict, score=score,
                )
            row = json.loads(run_tool(tmp, "--json").stdout)["series"][0]
            self.assertEqual(row["relapse_count"], 1)
            self.assertEqual(row["verdict_oscillation_count"], 2)
            self.assertEqual(row["score_oscillation_count"], 2)

    def test_cross_catalog_scores_are_explicitly_non_comparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            put_artifact(
                tmp, "a.md", target="catalog-change", observed_at="2026-07-01",
                verdict="FIX", score=60,
            )
            put_artifact(
                tmp, "b.md", target="catalog-change", observed_at="2026-07-02",
                verdict="SHIP", score=80,
            )
            artifacts, skipped = trends.collect(tmp)
            self.assertEqual(skipped, 0)
            migrated = [dict(item) for item in artifacts]
            migrated[-1]["catalog_version"] = "19.0.0"
            row = trends.series_report(migrated)[0]
            self.assertTrue(row["catalog_drift"])
            self.assertFalse(row["score_comparable"])
            self.assertIsNone(row["score_delta"])

    def test_mid_series_catalog_drift_makes_score_delta_non_comparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, score in enumerate((55, 60, 78), 1):
                put_artifact(
                    tmp, "m%d.md" % index, target="mid-drift",
                    observed_at="2026-07-0%d" % index,
                    verdict="FIX" if score < 78 else "SHIP", score=score,
                )
            artifacts, skipped = trends.collect(tmp)
            self.assertEqual(skipped, 0)
            migrated = [dict(item) for item in artifacts]
            migrated[1]["catalog_version"] = "19.0.0"
            row = trends.series_report(migrated)[0]
            self.assertTrue(row["catalog_drift"])
            self.assertFalse(row["score_comparable"])
            self.assertIsNone(row["score_delta"])

    def test_mid_series_context_drift_makes_score_delta_non_comparable(self):
        with tempfile.TemporaryDirectory() as tmp:
            for index, score in enumerate((55, 60, 78), 1):
                put_artifact(
                    tmp, "m%d.md" % index, target="mid-context",
                    observed_at="2026-07-0%d" % index,
                    verdict="FIX" if score < 78 else "SHIP", score=score,
                )
            artifacts, skipped = trends.collect(tmp)
            self.assertEqual(skipped, 0)
            migrated = [dict(item) for item in artifacts]
            migrated[1]["context_sha256"] = "0" * 64
            row = trends.series_report(migrated)[0]
            self.assertFalse(row["score_comparable"])
            self.assertIsNone(row["score_delta"])

    def test_human_output_escapes_terminal_control_sequences_in_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = put_artifact(
                tmp, "ansi.md", target="placeholder", observed_at="2026-07-01",
                verdict="SHIP", score=80,
            )
            payload = path.read_text(encoding="utf-8").replace(
                "target: placeholder", 'target: "\\u001b[2Jowned"',
            )
            path.write_text(payload, encoding="utf-8")
            result = run_tool(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("\x1b", result.stdout)
            self.assertIn("\\x1b[2Jowned", result.stdout)


if __name__ == "__main__":
    unittest.main()
