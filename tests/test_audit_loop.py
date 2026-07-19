import concurrent.futures
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import unittest
from unittest import mock
import uuid


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "audit_loop", ROOT / "scripts" / "audit-loop.py"
)
loop = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(loop)


def artifact(
        verdict="FIX", confidence="medium", target="asset-1", context=None,
        observed_at="2026-07-19", score=80):
    context = context or {
        "content_type": "blog-post", "market": "US", "publication_state": "draft",
    }
    if verdict == "FIX":
        status = "DONE_WITH_CONCERNS"
        score_state = "SCORED"
        coverage = 100
        confidence_value = confidence
        scores = "raw_overall_score: %d\nfinal_overall_score: %d\n" % (score, score)
        findings = (
            "key_findings:\n"
            "  - title: Verified remediation need\n"
            "    severity: medium\n"
            "    evidence: Reproducible issue in the declared target\n"
        )
    elif verdict == "SHIP":
        status = "DONE"
        score_state = "SCORED"
        coverage = 100
        confidence_value = confidence
        scores = "raw_overall_score: %d\nfinal_overall_score: %d\n" % (score, score)
        findings = "key_findings: []\n"
    elif verdict == "UNDECIDED":
        status = "NEEDS_INPUT"
        score_state = "NOT_SCORED"
        coverage = 80
        confidence_value = "not_scored"
        scores = ""
        findings = "key_findings: []\n"
    else:
        raise ValueError("unsupported fixture verdict")
    return """---
class: auditor-output
schema_version: 3.0
runbook_version: 3.0.0
catalog_version: 18.0.0
framework: CORE-EEAT
profile: blog-post
---
status: {status}
verdict: {verdict}
score_state: {score_state}
objective: Verify the declared content target
target: {target}
observed_at: {observed_at}
context: {context}
{findings}evidence_summary: Exact fixture evidence was collected
evidence_coverage: {coverage}
score_confidence: {confidence}
open_loops: Owner intervention remains explicitly external
recommended_next_skill: content-brief-generator
veto_count: 0
cap_applied: false
{scores}""".format(
        status=status,
        verdict=verdict,
        score_state=score_state,
        target=target,
        observed_at=observed_at,
        context=json.dumps(context, sort_keys=True, separators=(",", ":")),
        findings=findings,
        coverage=coverage,
        confidence=confidence_value,
        scores=scores,
    )


class AuditLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run_id = str(uuid.uuid4())
        self.loop_id = str(uuid.uuid4())
        self.inputs = self.root / "inputs"
        self.inputs.mkdir()
        self.create_run(self.run_id)
        self.baseline = self.write("inputs/baseline.md", artifact())
        self.proposal = self.write("inputs/proposal.json", '{"change":"proposal only"}\n')
        self.intervention = self.write(
            "inputs/intervention.json", '{"owner":"completed outside runtime"}\n'
        )
        self.times = 0

    def tearDown(self):
        self.temp.cleanup()

    def write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def relative(self, path):
        return path.relative_to(self.root).as_posix()

    def create_run(self, run_id):
        return loop.runtime.append_event(self.root, run_id, {
            "schema_version": loop.runtime.SCHEMA_VERSION,
            "run_id": run_id,
            "idempotency_key": "run:start",
            "event_type": "run_started",
            "occurred_at": "2026-07-19T09:59:00Z",
            "actor": {"type": "host", "id": "audit-loop-test"},
            "parent_event_id": None,
            "turn_id": None,
            "status": "started",
            "subject": {"kind": "run", "ref": run_id},
            "references": [],
            "metrics": {},
            "dimensions": {},
        })

    def time(self, seconds=None):
        if seconds is None:
            self.times += 1
            seconds = self.times
        return "2026-07-19T10:00:%02dZ" % seconds

    def start(self, max_cycles=3, max_retries=2, deadline="2026-07-19T11:00:00Z",
              baseline=None, key="start"):
        baseline = baseline or self.baseline
        result = loop.apply_action(
            "start", root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key=key, expected_previous_sha256=loop.ZERO_HASH,
            occurred_at=self.time(), deadline=deadline, max_cycles=max_cycles,
            max_retries=max_retries, audit_ref=self.relative(baseline),
            audit_sha256=self.digest(baseline),
        )
        return result

    def lease(self, head, token, seconds=None, key=None, ttl=60):
        return loop.apply_action(
            "acquire-lease", root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key=key or "lease-" + token,
            expected_previous_sha256=head["step_sha256"],
            occurred_at=self.time(seconds), lease_owner="workflow-host",
            lease_token=token, lease_ttl=ttl,
        )

    def leased_action(self, action, head, token, seconds=None, key=None, **values):
        return loop.apply_action(
            action, root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key=key or action + "-1",
            expected_previous_sha256=head["step_sha256"],
            occurred_at=self.time(seconds),
            lease_generation=head["step"]["lease"]["generation"],
            lease_token=token, **values,
        )

    def to_reaudit(self, max_cycles=3, max_retries=2):
        head = self.start(max_cycles=max_cycles, max_retries=max_retries)
        head = self.lease(head, "proposal-token")
        head = self.leased_action(
            "proposal", head, "proposal-token",
            proposal_ref=self.relative(self.proposal),
            proposal_sha256=self.digest(self.proposal),
        )
        head = self.lease(head, "owner-token")
        head = self.leased_action(
            "owner", head, "owner-token", owner_id="owner-1", decision="accept",
        )
        head = self.lease(head, "intervention-token")
        head = self.leased_action(
            "intervention", head, "intervention-token",
            intervention_ref=self.relative(self.intervention),
            intervention_sha256=self.digest(self.intervention),
        )
        return head

    def test_full_proposal_only_flow_converges_on_strong_distinct_ship(self):
        baseline_before = self.baseline.read_bytes()
        proposal_before = self.proposal.read_bytes()
        intervention_before = self.intervention.read_bytes()
        head = self.to_reaudit()
        changed_context = {
            "content_type": "blog-post", "market": "US", "publication_state": "published",
        }
        reaudit = self.write(
            "inputs/ship.md", artifact(
                verdict="SHIP", confidence="high", context=changed_context,
                observed_at="2026-07-20", score=91,
            ),
        )
        head = self.lease(head, "reaudit-token")
        result = self.leased_action(
            "reaudit", head, "reaudit-token", audit_ref=self.relative(reaudit),
            audit_sha256=self.digest(reaudit),
        )

        self.assertEqual("converged", result["step"]["state"])
        self.assertEqual("ship-confirmed", result["step"]["reason_code"])
        self.assertNotEqual(
            result["step"]["baseline_audit"]["context_sha256"],
            result["step"]["latest_audit"]["context_sha256"],
        )
        self.assertTrue(result["step"]["proposal_only"])
        self.assertFalse(result["step"]["external_mutation_authorized"])
        self.assertFalse(result["step"]["lease"]["active"])
        self.assertEqual(baseline_before, self.baseline.read_bytes())
        self.assertEqual(proposal_before, self.proposal.read_bytes())
        self.assertEqual(intervention_before, self.intervention.read_bytes())

        steps = loop.read_loop(self.root, self.run_id, self.loop_id)
        self.assertEqual(9, len(steps))
        coverage = loop.runtime.verify_loop_event_coverage(
            self.root, self.run_id, self.loop_id, steps,
        )
        self.assertEqual(9, coverage["steps"])
        self.assertEqual(9, coverage["events"])
        self.assertEqual(9, len(coverage["event_ids"]))
        self.assertEqual(
            result["step_sha256"],
            loop.read_loop_with_event_coverage(
                self.root, self.run_id, self.loop_id,
            )[-1]["sha256"],
        )
        projection = loop.runtime.project_events(
            self.run_id, loop.runtime.load_events(self.root, self.run_id)
        )
        self.assertEqual("converged", projection["loop_states"][0]["state"])
        self.assertEqual(result["step_sha256"], projection["loop_states"][0]["step_sha256"])
        resolved = loop.resolve_loop_step(
            self.root, self.run_id, self.loop_id,
            result["step_ref"], result["step_sha256"],
        )
        self.assertEqual("converged", resolved["document"]["state"])
        with self.assertRaisesRegex(loop.AuditLoopError, "hash mismatch"):
            loop.resolve_loop_step(
                self.root, self.run_id, self.loop_id, result["step_ref"], "f" * 64,
            )
        for item in steps:
            mode = stat.S_IMODE((self.root / item["ref"]).stat().st_mode)
            self.assertEqual(0o600, mode)
        loop_dir = (self.root / steps[-1]["ref"]).parent
        self.assertEqual(0o700, stat.S_IMODE(loop_dir.stat().st_mode))
        self.assertEqual(0o600, stat.S_IMODE((loop_dir / ".loop.lock").stat().st_mode))

    def test_entry_requires_exact_valid_scored_fix(self):
        missing_run = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "run does not exist"):
            loop.apply_action(
                "start", root=self.root, run_id=missing_run,
                loop_id=str(uuid.uuid4()), idempotency_key="missing-run",
                expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z",
                deadline="2026-07-19T11:00:00Z", max_cycles=2, max_retries=1,
                audit_ref=self.relative(self.baseline),
                audit_sha256=self.digest(self.baseline),
            )
        self.assertFalse((self.root / "memory" / "runs" / missing_run).exists())

        ship = self.write("inputs/not-fix.md", artifact(verdict="SHIP", score=90))
        with self.assertRaisesRegex(loop.AuditLoopError, "baseline must be validated"):
            self.start(baseline=ship)
        loop_root = self.root / "memory" / "runs" / self.run_id / "loops"
        self.assertFalse((loop_root / self.loop_id).exists())

        other_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "hash mismatch"):
            loop.apply_action(
                "start", root=self.root, run_id=self.run_id, loop_id=other_loop,
                idempotency_key="wrong-hash", expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z", deadline="2026-07-19T11:00:00Z",
                max_cycles=2, max_retries=1, audit_ref=self.relative(self.baseline),
                audit_sha256="a" * 64,
            )
        self.assertFalse((loop_root / other_loop).exists())

        deadline_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "deadline must follow"):
            loop.apply_action(
                "start", root=self.root, run_id=self.run_id, loop_id=deadline_loop,
                idempotency_key="bad-deadline",
                expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z",
                deadline="2026-07-19T10:01:00Z", max_cycles=2, max_retries=1,
                audit_ref=self.relative(self.baseline),
                audit_sha256=self.digest(self.baseline),
            )
        self.assertFalse((loop_root / deadline_loop).exists())

        unsupported_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "unsupported action"):
            loop.apply_action(
                "unsupported", root=self.root, run_id=self.run_id,
                loop_id=unsupported_loop, idempotency_key="unsupported",
                expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z",
            )
        self.assertFalse((loop_root / unsupported_loop).exists())

        omitted_time_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "supplied explicitly"):
            loop.apply_action(
                "start", root=self.root, run_id=self.run_id,
                loop_id=omitted_time_loop, idempotency_key="missing-time",
                expected_previous_sha256=loop.ZERO_HASH,
                deadline="2026-07-19T11:00:00Z", max_cycles=2, max_retries=1,
                audit_ref=self.relative(self.baseline),
                audit_sha256=self.digest(self.baseline),
            )
        self.assertFalse((loop_root / omitted_time_loop).exists())

        missing_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "loop must start"):
            loop.apply_action(
                "acquire-lease", root=self.root, run_id=self.run_id,
                loop_id=missing_loop, idempotency_key="premature-lease",
                expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z", lease_owner="worker",
                lease_token="token", lease_ttl=60,
            )
        self.assertFalse((loop_root / missing_loop).exists())

        hardlink = self.root / "inputs" / "hardlink.md"
        os.link(self.baseline, hardlink)
        third_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "single-link"):
            loop.apply_action(
                "start", root=self.root, run_id=self.run_id, loop_id=third_loop,
                idempotency_key="hardlink", expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:01:00Z", deadline="2026-07-19T11:00:00Z",
                max_cycles=2, max_retries=1, audit_ref=self.relative(hardlink),
                audit_sha256=self.digest(hardlink),
            )
        self.assertFalse((loop_root / third_loop).exists())
        hardlink.unlink()

        retried = self.start(key="valid-retry-after-rejections")
        self.assertEqual("awaiting-proposal", retried["step"]["state"])

    def test_new_step_preserves_terminal_event_capacity_without_residue(self):
        capacity_loop = str(uuid.uuid4())
        with mock.patch.object(loop.runtime, "MAX_EVENTS", 2):
            with self.assertRaisesRegex(
                    loop.AuditLoopError, "terminal-envelope event slot"):
                loop.apply_action(
                    "start", root=self.root, run_id=self.run_id,
                    loop_id=capacity_loop, idempotency_key="capacity-start",
                    expected_previous_sha256=loop.ZERO_HASH,
                    occurred_at="2026-07-19T10:00:01Z",
                    deadline="2026-07-19T11:00:00Z",
                    max_cycles=2, max_retries=1,
                    audit_ref=self.relative(self.baseline),
                    audit_sha256=self.digest(self.baseline),
                )
        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / capacity_loop
        )
        self.assertFalse(loop_dir.exists())

    def test_reaudit_must_be_distinct_and_keep_framework_profile_target(self):
        head = self.to_reaudit()
        head = self.lease(head, "reaudit-token")
        with self.assertRaisesRegex(loop.AuditLoopError, "distinct artifact bytes"):
            self.leased_action(
                "reaudit", head, "reaudit-token", key="same-audit",
                audit_ref=self.relative(self.baseline),
                audit_sha256=self.digest(self.baseline),
            )

        mismatch = self.write(
            "inputs/mismatch.md",
            artifact(verdict="SHIP", confidence="high", target="asset-2", score=90),
        )
        with self.assertRaisesRegex(loop.AuditLoopError, "identity mismatch"):
            self.leased_action(
                "reaudit", head, "reaudit-token", key="identity-mismatch",
                audit_ref=self.relative(mismatch), audit_sha256=self.digest(mismatch),
            )

        stale = self.write(
            "inputs/stale-ship.md",
            artifact(
                verdict="SHIP", confidence="high", observed_at="2026-07-19",
                score=91, context={
                    "content_type": "blog-post", "market": "US",
                    "publication_state": "published",
                },
            ),
        )
        with self.assertRaisesRegex(loop.AuditLoopError, "must follow the baseline"):
            self.leased_action(
                "reaudit", head, "reaudit-token", key="stale-ship",
                audit_ref=self.relative(stale), audit_sha256=self.digest(stale),
            )

    def test_low_confidence_ship_needs_input(self):
        head = self.to_reaudit()
        low = self.write(
            "inputs/low-ship.md",
            artifact(verdict="SHIP", confidence="low", observed_at="2026-07-20", score=86),
        )
        head = self.lease(head, "low-token")
        result = self.leased_action(
            "reaudit", head, "low-token", audit_ref=self.relative(low),
            audit_sha256=self.digest(low),
        )
        self.assertEqual("needs-input", result["step"]["state"])
        self.assertEqual("ship-confidence-low", result["step"]["reason_code"])

    def test_owner_rejection_is_typed_preserves_identity_and_needs_input(self):
        head = self.start()
        head = self.lease(head, "proposal-token")
        head = self.leased_action(
            "proposal", head, "proposal-token",
            proposal_ref=self.relative(self.proposal),
            proposal_sha256=self.digest(self.proposal),
        )
        head = self.lease(head, "owner-reject-token")
        rejected = self.leased_action(
            "owner", head, "owner-reject-token", key="owner-reject",
            owner_id="owner-42", decision="reject",
        )
        self.assertEqual("owner-rejected", rejected["step"]["transition"])
        self.assertEqual("needs-input", rejected["step"]["state"])
        self.assertEqual("owner-rejected", rejected["step"]["reason_code"])
        self.assertEqual("owner-42", rejected["step"]["owner"])
        self.assertEqual(self.digest(self.proposal), rejected["step"]["proposal"]["sha256"])
        self.assertIsNone(rejected["step"]["intervention"])
        self.assertFalse(rejected["step"]["external_mutation_authorized"])

        other_run, other_loop = str(uuid.uuid4()), str(uuid.uuid4())
        original_run, original_loop, original_times = self.run_id, self.loop_id, self.times
        try:
            self.run_id, self.loop_id, self.times = other_run, other_loop, 0
            self.create_run(other_run)
            missing = self.start()
            missing = self.lease(missing, "missing-proposal-token")
            missing = self.leased_action(
                "proposal", missing, "missing-proposal-token",
                proposal_ref=self.relative(self.proposal),
                proposal_sha256=self.digest(self.proposal),
            )
            missing = self.lease(missing, "missing-decision-token")
            with self.assertRaisesRegex(loop.AuditLoopError, "must be accept or reject"):
                self.leased_action(
                    "owner", missing, "missing-decision-token", key="missing-decision",
                    owner_id="owner-42",
                )
        finally:
            self.run_id, self.loop_id, self.times = original_run, original_loop, original_times

    def test_optimistic_concurrency_allows_only_one_writer(self):
        head = self.start()

        def acquire(number):
            return loop.apply_action(
                "acquire-lease", root=self.root, run_id=self.run_id,
                loop_id=self.loop_id, idempotency_key="writer-%d" % number,
                expected_previous_sha256=head["step_sha256"],
                occurred_at="2026-07-19T10:00:02Z", lease_owner="worker-%d" % number,
                lease_token="token-%d" % number, lease_ttl=60,
            )

        results = []
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(acquire, number) for number in (1, 2)]
            for future in futures:
                try:
                    results.append(future.result())
                except loop.AuditLoopError as exc:
                    errors.append(str(exc))
        self.assertEqual(1, len(results))
        self.assertEqual(1, len(errors))
        self.assertIn("optimistic concurrency conflict", errors[0])

    def test_existing_loop_advances_only_on_its_selected_run_branch(self):
        head = self.start()
        root_event = loop.runtime.load_events(self.root, self.run_id)[0]

        def append_turn(key, turn_id, parent, occurred_at):
            return loop.runtime.append_event(self.root, self.run_id, {
                "schema_version": loop.runtime.SCHEMA_VERSION,
                "run_id": self.run_id,
                "idempotency_key": key,
                "event_type": "turn_started",
                "occurred_at": occurred_at,
                "actor": {"type": "host", "id": "audit-loop-test"},
                "parent_event_id": parent,
                "turn_id": turn_id,
                "status": "started",
                "subject": {"kind": "turn", "ref": turn_id},
                "references": [], "metrics": {}, "dimensions": {},
            })

        append_turn(
            "sibling-turn", "turn-sibling", root_event["event_id"],
            "2026-07-19T10:00:02Z",
        )
        lease_options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="branch-lease",
            expected_previous_sha256=head["step_sha256"],
            occurred_at="2026-07-19T10:00:04Z",
            lease_owner="workflow-host", lease_token="branch-token", lease_ttl=60,
        )
        with self.assertRaisesRegex(
                loop.AuditLoopError, "current selected branch"):
            loop.apply_action("acquire-lease", **lease_options)
        self.assertEqual(1, len(loop.read_loop(self.root, self.run_id, self.loop_id)))

        append_turn(
            "resume-loop-branch", "turn-loop-branch", head["event"]["event_id"],
            "2026-07-19T10:00:03Z",
        )
        resumed = loop.apply_action("acquire-lease", **lease_options)
        self.assertEqual("lease-acquired", resumed["step"]["transition"])
        self.assertEqual(
            "turn-loop-branch",
            next(
                event["turn_id"] for event in loop.runtime.load_events(
                    self.root, self.run_id,
                )
                if event["event_id"] == resumed["step"]["run_parent_event_id"]
            ),
        )

    def test_idempotency_and_safe_crash_residue_recovery(self):
        head = self.start()
        loop_dir = self.root / "memory" / "runs" / self.run_id / "loops" / self.loop_id
        residue = loop_dir / ".002-lease-acquired.json.run-create"
        residue.write_text("{}\n", encoding="utf-8")
        os.chmod(residue, 0o600)
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="lease-after-crash",
            expected_previous_sha256=head["step_sha256"],
            occurred_at="2026-07-19T10:00:02Z", lease_owner="worker",
            lease_token="crash-token", lease_ttl=60,
        )
        first = loop.apply_action("acquire-lease", **options)
        self.assertFalse(residue.exists())
        second = loop.apply_action("acquire-lease", **options)
        self.assertTrue(second["deduplicated"])
        self.assertEqual(first["step_sha256"], second["step_sha256"])
        changed = dict(options, occurred_at="2026-07-19T10:00:03Z")
        with self.assertRaisesRegex(loop.AuditLoopError, "idempotency key"):
            loop.apply_action("acquire-lease", **changed)

    def test_event_anchor_recovers_missing_step_with_same_request(self):
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="recover-start",
            expected_previous_sha256=loop.ZERO_HASH,
            occurred_at="2026-07-19T10:00:01Z",
            deadline="2026-07-19T11:00:00Z", max_cycles=2, max_retries=1,
            audit_ref=self.relative(self.baseline),
            audit_sha256=self.digest(self.baseline),
        )
        with mock.patch.object(
                loop.runtime, "write_immutable_json",
                side_effect=loop.runtime.RunEventError("simulated step install failure")):
            with self.assertRaisesRegex(
                    loop.AuditLoopError,
                    r"event_committed=true .* retry the same request"):
                loop.apply_action("start", **options)

        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / self.loop_id
        )
        self.assertFalse(loop_dir.exists())
        anchors = [
            event for event in loop.runtime.load_events(self.root, self.run_id)
            if event["idempotency_key"] == "loop:" + str(uuid.uuid5(
                loop.NAMESPACE, self.loop_id + ":recover-start",
            ))
        ]
        self.assertEqual(1, len(anchors))
        self.assertEqual("loop_state_changed", anchors[0]["event_type"])
        with self.assertRaisesRegex(loop.AuditLoopError, "loop does not exist"):
            loop.read_loop(self.root, self.run_id, self.loop_id)

        recovered = loop.apply_action("start", **options)
        self.assertTrue(recovered["deduplicated"])
        self.assertTrue(recovered["event"]["deduplicated"])
        steps = loop.read_loop(self.root, self.run_id, self.loop_id)
        coverage = loop.runtime.verify_loop_event_coverage(
            self.root, self.run_id, self.loop_id, steps,
        )
        self.assertEqual(1, coverage["steps"])
        self.assertEqual(1, coverage["events"])
        self.assertEqual(anchors[0]["event_id"], coverage["event_ids"][0])
        self.assertEqual(
            anchors[0]["parent_event_id"],
            recovered["step"]["run_parent_event_id"],
        )

        completed = subprocess.run(
            [
                "python3", str(ROOT / "scripts" / "run-events.py"),
                "--root", str(self.root), "loop-step", self.run_id, self.loop_id,
                recovered["step_ref"], recovered["step_sha256"],
            ],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertTrue(json.loads(completed.stdout)["deduplicated"])

    def test_missing_step_recovery_survives_switch_to_sibling_branch(self):
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="recover-off-selected",
            expected_previous_sha256=loop.ZERO_HASH,
            occurred_at="2026-07-19T10:00:01Z",
            deadline="2026-07-19T11:00:00Z", max_cycles=2, max_retries=1,
            audit_ref=self.relative(self.baseline),
            audit_sha256=self.digest(self.baseline),
        )
        with mock.patch.object(
                loop.runtime, "write_immutable_json",
                side_effect=loop.runtime.RunEventError("simulated step install failure")):
            with self.assertRaisesRegex(loop.AuditLoopError, "event_committed=true"):
                loop.apply_action("start", **options)

        events = loop.runtime.load_events(self.root, self.run_id)
        anchor = next(
            event for event in events
            if event["idempotency_key"] == "loop:" + str(uuid.uuid5(
                loop.NAMESPACE, self.loop_id + ":recover-off-selected",
            ))
        )
        sibling = loop.runtime.append_event(self.root, self.run_id, {
            "schema_version": loop.runtime.SCHEMA_VERSION,
            "run_id": self.run_id,
            "idempotency_key": "switch-to-anchor-sibling",
            "event_type": "context_resolved",
            "occurred_at": "2026-07-19T10:00:02Z",
            "actor": {"type": "system", "id": "audit-loop-test"},
            "parent_event_id": anchor["parent_event_id"],
            "turn_id": None,
            "status": "succeeded",
            "subject": {"kind": "context", "ref": "sibling"},
            "references": [],
            "metrics": {},
            "dimensions": {},
        })
        state = sibling["projection"]
        failed = loop.runtime.finish_run(self.root, self.run_id, {
            "schema_version": loop.runtime.SCHEMA_VERSION,
            "run_id": self.run_id,
            "parent_run_id": None,
            "started_at": state["started_at"],
            "ended_at": "2026-07-19T10:00:03Z",
            "status": "failed",
            "evidence_mode": "none",
            "route": None,
            "context_manifests": [],
            "last_event_id": state["last_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "save_point": None,
            "registry_offsets": {
                name: None for name in loop.runtime.REGISTRIES
            },
            "artifacts": [],
            "metrics": {"turns": 0, "tool_calls": 0},
            "failure_class": "loop",
            "next_action": None,
        })
        envelope_path = self.root / failed["artifact"]["ref"]
        envelope_before = envelope_path.read_bytes()
        stored = json.loads(envelope_before)
        self.assertEqual("none", stored["loop_closure"]["status"])
        before = loop.runtime.load_events(self.root, self.run_id)

        recovered = loop.apply_action("start", **options)
        after = loop.runtime.load_events(self.root, self.run_id)
        self.assertTrue(recovered["deduplicated"])
        self.assertTrue(recovered["event"]["deduplicated"])
        self.assertEqual(len(before), len(after))
        self.assertEqual(failed["event"]["event_id"], after[-1]["event_id"])
        self.assertEqual(anchor["event_id"], recovered["event"]["event_id"])
        self.assertEqual(envelope_before, envelope_path.read_bytes())

        steps = loop.read_loop(self.root, self.run_id, self.loop_id)
        coverage = loop.runtime.verify_loop_event_coverage(
            self.root, self.run_id, self.loop_id, steps,
        )
        self.assertEqual([anchor["event_id"]], coverage["event_ids"])
        with self.assertRaisesRegex(loop.AuditLoopError, "selected branch"):
            loop.apply_action("start", **options)
        final_events = loop.runtime.load_events(self.root, self.run_id)
        self.assertEqual(len(after), len(final_events))
        self.assertEqual(failed["event"]["event_id"], final_events[-1]["event_id"])
        self.assertEqual(envelope_before, envelope_path.read_bytes())

    def test_later_missing_step_recovers_with_off_selected_historical_prefix(self):
        first = self.start(key="historical-prefix-start")
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="recover-off-selected-lease",
            expected_previous_sha256=first["step_sha256"],
            occurred_at="2026-07-19T10:00:02Z",
            lease_owner="workflow-host", lease_token="historical-token",
            lease_ttl=60,
        )
        with mock.patch.object(
                loop.runtime, "write_immutable_json",
                side_effect=loop.runtime.RunEventError("simulated step install failure")):
            with self.assertRaisesRegex(loop.AuditLoopError, "event_committed=true"):
                loop.apply_action("acquire-lease", **options)

        events = loop.runtime.load_events(self.root, self.run_id)
        first_anchor = next(
            event for event in events
            if event["event_id"] == first["event"]["event_id"]
        )
        pending_anchor = next(
            event for event in events
            if event["idempotency_key"] == "loop:" + str(uuid.uuid5(
                loop.NAMESPACE,
                self.loop_id + ":recover-off-selected-lease",
            ))
        )
        sibling = loop.runtime.append_event(self.root, self.run_id, {
            "schema_version": loop.runtime.SCHEMA_VERSION,
            "run_id": self.run_id,
            "idempotency_key": "switch-before-loop-prefix",
            "event_type": "context_resolved",
            "occurred_at": "2026-07-19T10:00:03Z",
            "actor": {"type": "system", "id": "audit-loop-test"},
            "parent_event_id": first_anchor["parent_event_id"],
            "turn_id": None,
            "status": "succeeded",
            "subject": {"kind": "context", "ref": "pre-loop-sibling"},
            "references": [],
            "metrics": {},
            "dimensions": {},
        })
        state = sibling["projection"]
        failed = loop.runtime.finish_run(self.root, self.run_id, {
            "schema_version": loop.runtime.SCHEMA_VERSION,
            "run_id": self.run_id,
            "parent_run_id": None,
            "started_at": state["started_at"],
            "ended_at": "2026-07-19T10:00:04Z",
            "status": "failed",
            "evidence_mode": "none",
            "route": None,
            "context_manifests": [],
            "last_event_id": state["last_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "save_point": None,
            "registry_offsets": {
                name: None for name in loop.runtime.REGISTRIES
            },
            "artifacts": [],
            "metrics": {"turns": 0, "tool_calls": 0},
            "failure_class": "loop",
            "next_action": None,
        })
        envelope_path = self.root / failed["artifact"]["ref"]
        envelope_before = envelope_path.read_bytes()
        self.assertEqual(
            "none", json.loads(envelope_before)["loop_closure"]["status"],
        )
        before = loop.runtime.load_events(self.root, self.run_id)

        recovered = loop.apply_action("acquire-lease", **options)
        after = loop.runtime.load_events(self.root, self.run_id)
        self.assertTrue(recovered["event"]["deduplicated"])
        self.assertEqual(pending_anchor["event_id"], recovered["event"]["event_id"])
        self.assertEqual(len(before), len(after))
        self.assertEqual(failed["event"]["event_id"], after[-1]["event_id"])
        self.assertEqual(envelope_before, envelope_path.read_bytes())

        steps = loop.read_loop(self.root, self.run_id, self.loop_id)
        coverage = loop.runtime.verify_loop_event_coverage(
            self.root, self.run_id, self.loop_id, steps,
        )
        self.assertEqual(
            [first_anchor["event_id"], pending_anchor["event_id"]],
            coverage["event_ids"],
        )
        with self.assertRaisesRegex(loop.AuditLoopError, "selected branch"):
            loop.apply_action("acquire-lease", **options)
        final_events = loop.runtime.load_events(self.root, self.run_id)
        self.assertEqual(len(after), len(final_events))
        self.assertEqual(failed["event"]["event_id"], final_events[-1]["event_id"])
        self.assertEqual(envelope_before, envelope_path.read_bytes())

    def test_public_loop_step_never_upgrades_eventless_file(self):
        loop_id = str(uuid.uuid4())
        options = {
            "root": self.root, "run_id": self.run_id, "loop_id": loop_id,
            "idempotency_key": "forged-eventless-start",
            "expected_previous_sha256": loop.ZERO_HASH,
            "occurred_at": "2026-07-19T10:00:01Z",
            "deadline": "2026-07-19T11:00:00Z",
            "max_cycles": 2, "max_retries": 1,
            "audit_ref": self.relative(self.baseline),
            "audit_sha256": self.digest(self.baseline),
        }
        request_hash = loop.sha256_json(loop._request_material("start", options))
        run_head = loop.runtime.load_events(self.root, self.run_id)[-1]
        options["_run_parent_event_id"] = run_head["event_id"]
        options["_run_parent_event_sha256"] = run_head["event_hash"]
        document = loop._build_validated_start_document(
            self.root, options, request_hash,
        )
        loop_dir, _identity = loop._ensure_loop_directory(
            self.root, self.run_id, loop_id,
        )
        lock_path = loop_dir / ".loop.lock"
        lock_path.write_bytes(b"")
        os.chmod(lock_path, 0o600)
        step_path = loop_dir / "001-start.json"
        digest = loop.runtime.write_immutable_json(
            self.root, step_path, document,
        )
        before = loop.runtime.load_events(self.root, self.run_id)

        completed = subprocess.run(
            [
                "python3", str(ROOT / "scripts" / "run-events.py"),
                "--root", str(self.root), "loop-step", self.run_id, loop_id,
                loop._step_ref(self.root, step_path), digest,
            ],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("coverage", completed.stderr)
        after = loop.runtime.load_events(self.root, self.run_id)
        self.assertEqual(len(before), len(after))
        self.assertFalse(any(
            event["event_type"] == "loop_state_changed"
            and event["subject"]["ref"] == loop_id
            for event in after
        ))

    def test_reserved_reaudit_hash_rejects_tampered_false_ship_file(self):
        head = self.to_reaudit()
        head = self.lease(head, "crash-reaudit-token")
        fix = self.write(
            "inputs/crash-fix.md",
            artifact(verdict="FIX", observed_at="2026-07-20", score=82),
        )
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="crash-reaudit",
            expected_previous_sha256=head["step_sha256"],
            occurred_at=self.time(),
            lease_generation=head["step"]["lease"]["generation"],
            lease_token="crash-reaudit-token",
            audit_ref=self.relative(fix), audit_sha256=self.digest(fix),
        )
        captured = {}

        def fail_materialization(_root, path, document):
            captured["path"] = Path(path)
            captured["document"] = json.loads(json.dumps(document))
            raise loop.runtime.RunEventError("simulated step install failure")

        with mock.patch.object(
                loop.runtime, "write_immutable_json",
                side_effect=fail_materialization):
            with self.assertRaisesRegex(loop.AuditLoopError, "event_committed=true"):
                loop.apply_action("reaudit", **options)

        step_path = captured["path"]
        self.assertFalse(step_path.exists())
        tampered = captured["document"]
        tampered["state"] = "converged"
        tampered["reason_code"] = "ship-confirmed"
        tampered["latest_audit"]["status"] = "DONE"
        tampered["latest_audit"]["verdict"] = "SHIP"
        step_path.write_bytes(loop._serialized_step_bytes(tampered))
        os.chmod(step_path, 0o600)

        tampered_sha = self.digest(step_path)
        external_repair = subprocess.run(
            [
                "python3", str(ROOT / "scripts" / "run-events.py"),
                "--root", str(self.root), "loop-step", self.run_id,
                self.loop_id, Path(os.path.relpath(step_path, self.root)).as_posix(),
                tampered_sha,
            ],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(0, external_repair.returncode)
        with self.assertRaisesRegex(loop.AuditLoopError, "coverage|anchor|occupied"):
            loop.apply_action("reaudit", **options)

        step_path.unlink()
        recovered = loop.apply_action("reaudit", **options)
        self.assertTrue(recovered["deduplicated"])
        self.assertEqual("next", recovered["step"]["state"])
        self.assertEqual("FIX", recovered["step"]["latest_audit"]["verdict"])
        anchor = next(
            event for event in loop.runtime.load_events(self.root, self.run_id)
            if event["event_id"] == recovered["event"]["event_id"]
        )
        self.assertEqual(recovered["step_sha256"], anchor["references"][0]["sha256"])

    def test_expired_lease_is_replaced_and_old_generation_is_fenced(self):
        head = self.start()
        first = self.lease(head, "old-token", seconds=2, ttl=30)
        with self.assertRaisesRegex(loop.AuditLoopError, "lease expired"):
            self.leased_action(
                "proposal", first, "old-token", seconds=32, key="expired-use",
                proposal_ref=self.relative(self.proposal),
                proposal_sha256=self.digest(self.proposal),
            )
        second = self.lease(first, "new-token", seconds=32, key="lease-generation-2")
        self.assertEqual(2, second["step"]["lease"]["generation"])
        with self.assertRaisesRegex(loop.AuditLoopError, "stale lease generation"):
            loop.apply_action(
                "proposal", root=self.root, run_id=self.run_id, loop_id=self.loop_id,
                idempotency_key="stale-use",
                expected_previous_sha256=second["step_sha256"],
                occurred_at="2026-07-19T10:00:33Z", lease_generation=1,
                lease_token="old-token", proposal_ref=self.relative(self.proposal),
                proposal_sha256=self.digest(self.proposal),
            )
        result = self.leased_action(
            "proposal", second, "new-token", seconds=33, key="new-use",
            proposal_ref=self.relative(self.proposal),
            proposal_sha256=self.digest(self.proposal),
        )
        self.assertEqual("awaiting-owner", result["step"]["state"])
        self.assertFalse(result["step"]["lease"]["active"])

    def test_fix_reaudit_advances_cycle_then_exhausts_at_bound(self):
        head = self.to_reaudit(max_cycles=2)
        fix_two = self.write(
            "inputs/fix-two.md",
            artifact(verdict="FIX", observed_at="2026-07-20", score=82),
        )
        head = self.lease(head, "fix-token")
        head = self.leased_action(
            "reaudit", head, "fix-token", audit_ref=self.relative(fix_two),
            audit_sha256=self.digest(fix_two),
        )
        self.assertEqual("next", head["step"]["state"])
        self.assertEqual(1, head["step"]["cycle"])
        head = self.lease(head, "advance-token")
        head = self.leased_action("advance", head, "advance-token")
        self.assertEqual("awaiting-proposal", head["step"]["state"])
        self.assertEqual(2, head["step"]["cycle"])
        self.assertEqual(0, head["step"]["state_retries"])

        other_run = str(uuid.uuid4())
        other_loop = str(uuid.uuid4())
        original_run, original_loop, original_times = self.run_id, self.loop_id, self.times
        try:
            self.run_id, self.loop_id, self.times = other_run, other_loop, 0
            self.create_run(other_run)
            exhausted_head = self.to_reaudit(max_cycles=1)
            exhausted_fix = self.write(
                "inputs/exhausted-fix.md",
                artifact(verdict="FIX", observed_at="2026-07-21", score=83),
            )
            exhausted_head = self.lease(exhausted_head, "last-token")
            exhausted = self.leased_action(
                "reaudit", exhausted_head, "last-token",
                audit_ref=self.relative(exhausted_fix),
                audit_sha256=self.digest(exhausted_fix),
            )
            self.assertEqual("exhausted", exhausted["step"]["state"])
        finally:
            self.run_id, self.loop_id, self.times = original_run, original_loop, original_times

    def test_retries_do_not_consume_cycles_and_backoff_is_enforced(self):
        head = self.start(max_cycles=3, max_retries=1)
        head = self.lease(head, "retry-token", seconds=2)
        retry = self.leased_action(
            "retry", head, "retry-token", seconds=3, key="retry-1",
            reason_code="owner-unavailable",
        )
        self.assertEqual("awaiting-proposal", retry["step"]["state"])
        self.assertEqual(1, retry["step"]["cycle"])
        self.assertEqual(1, retry["step"]["state_retries"])
        self.assertEqual(1, retry["step"]["total_retries"])
        self.assertEqual(1, retry["step"]["backoff_seconds"])
        with self.assertRaisesRegex(loop.AuditLoopError, "backoff has not elapsed"):
            self.lease(retry, "too-early", seconds=3, key="too-early")
        head = self.lease(retry, "retry-two-token", seconds=4, key="retry-lease-2")
        exhausted = self.leased_action(
            "retry", head, "retry-two-token", seconds=5, key="retry-2",
        )
        self.assertEqual("exhausted", exhausted["step"]["state"])
        self.assertEqual("retry-budget-exhausted", exhausted["step"]["reason_code"])
        self.assertEqual(1, exhausted["step"]["cycle"])
        self.assertEqual(2, exhausted["step"]["total_retries"])

    def test_deadline_expiry_is_an_immutable_exhausted_step(self):
        head = self.start(deadline="2026-07-19T10:00:05Z")
        expired = self.lease(head, "late-token", seconds=6)
        self.assertEqual("exhausted", expired["step"]["state"])
        self.assertEqual("deadline-expired", expired["step"]["transition"])
        self.assertEqual("deadline-expired", expired["step"]["reason_code"])
        self.assertFalse(expired["step"]["external_mutation_authorized"])

    def test_terminal_heads_reject_post_deadline_successors(self):
        head = self.start(deadline="2026-07-19T10:00:05Z")["step"]
        for state in sorted(loop.TERMINAL_STATES):
            terminal = json.loads(json.dumps(head))
            terminal["state"] = state
            options = {
                "loop_id": self.loop_id,
                "idempotency_key": "after-" + state,
                "expected_previous_sha256": "a" * 64,
                "_run_parent_event_id": head["run_parent_event_id"],
                "_run_parent_event_sha256": head["run_parent_event_sha256"],
                "_head_ref": "memory/runs/%s/loops/%s/001-start.json"
                             % (self.run_id, self.loop_id),
                "_head_sha256": "a" * 64,
                "lease_owner": "worker",
                "lease_token": "token",
                "lease_ttl": 60,
            }
            with self.subTest(state=state):
                with self.assertRaisesRegex(
                        loop.AuditLoopError, "terminal loop cannot accept"):
                    loop._build_transition(
                        "acquire-lease", terminal, "2026-07-19T10:00:06Z",
                        "b" * 64, options, self.root,
                    )
                candidate = loop._deadline_step(
                    terminal, "2026-07-19T10:00:06Z", "b" * 64, options,
                )
                with self.assertRaisesRegex(
                        loop.AuditLoopError, "terminal loop step cannot have"):
                    loop._validate_step(
                        candidate, 2, self.run_id, self.loop_id, terminal,
                        options["_head_ref"], options["_head_sha256"],
                    )

    def test_backdated_successor_and_invalid_reason_leave_no_step(self):
        head = self.start()
        with self.assertRaisesRegex(loop.AuditLoopError, "cannot precede"):
            self.lease(head, "backdated", seconds=0, key="backdated")

        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / self.loop_id
        )
        self.assertEqual([], sorted(loop_dir.glob("002-*.json")))
        options = dict(
            root=self.root, run_id=self.run_id, loop_id=self.loop_id,
            idempotency_key="reason-retry",
            expected_previous_sha256=head["step_sha256"],
            occurred_at="2026-07-19T10:00:02Z", lease_owner="worker",
            lease_token="valid-token", lease_ttl=60,
            reason_code="not a safe reason",
        )
        with self.assertRaisesRegex(loop.AuditLoopError, "reason_code"):
            loop.apply_action("acquire-lease", **options)
        self.assertEqual([], sorted(loop_dir.glob("002-*.json")))

        options["reason_code"] = "lease-acquired"
        result = loop.apply_action("acquire-lease", **options)
        self.assertEqual("lease-acquired", result["step"]["transition"])
        self.assertTrue((loop_dir / "002-lease-acquired.json").is_file())

    def test_empty_proposal_and_intervention_evidence_fail_closed(self):
        empty_proposal = self.write("inputs/empty-proposal.json", "")
        head = self.start()
        head = self.lease(head, "empty-proposal-token")
        with self.assertRaisesRegex(loop.AuditLoopError, "proposal must not be empty"):
            self.leased_action(
                "proposal", head, "empty-proposal-token",
                proposal_ref=self.relative(empty_proposal),
                proposal_sha256=self.digest(empty_proposal),
            )

        head = self.leased_action(
            "proposal", head, "empty-proposal-token", key="valid-proposal",
            proposal_ref=self.relative(self.proposal),
            proposal_sha256=self.digest(self.proposal),
        )
        head = self.lease(head, "owner-after-empty")
        head = self.leased_action(
            "owner", head, "owner-after-empty", owner_id="owner-1",
            decision="accept", key="accept-after-empty",
        )
        head = self.lease(head, "empty-intervention-token")
        empty_intervention = self.write("inputs/empty-intervention.json", "")
        with self.assertRaisesRegex(
                loop.AuditLoopError, "intervention evidence must not be empty"):
            self.leased_action(
                "intervention", head, "empty-intervention-token",
                intervention_ref=self.relative(empty_intervention),
                intervention_sha256=self.digest(empty_intervention),
            )

        steps = loop.read_loop(self.root, self.run_id, self.loop_id)
        proposal_index = next(
            index for index, item in enumerate(steps)
            if item["document"]["transition"] == "proposal-recorded"
        )
        proposal_step = json.loads(json.dumps(steps[proposal_index]["document"]))
        proposal_step["proposal"]["bytes"] = 0
        prior = steps[proposal_index - 1]
        with self.assertRaisesRegex(loop.AuditLoopError, "between 1 and"):
            loop._validate_step(
                proposal_step, proposal_step["sequence"], self.run_id,
                self.loop_id, prior["document"], prior["ref"], prior["sha256"],
            )

    def test_event_bound_read_enforces_aggregate_bytes_and_deadline(self):
        self.start()
        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / self.loop_id
        )
        exact_bytes = (loop_dir / "001-start.json").stat().st_size
        steps, total_bytes = loop.read_loop_with_event_coverage(
            self.root, self.run_id, self.loop_id,
            max_total_bytes=exact_bytes,
            deadline_monotonic=loop.time.monotonic() + 5,
            return_total_bytes=True,
        )
        self.assertEqual(1, len(steps))
        self.assertEqual(exact_bytes, total_bytes)
        with self.assertRaisesRegex(loop.AuditLoopError, "max_total_bytes"):
            loop.read_loop_with_event_coverage(
                self.root, self.run_id, self.loop_id,
                max_total_bytes=exact_bytes - 1,
            )
        with self.assertRaisesRegex(loop.AuditLoopError, "deadline exceeded"):
            loop.read_loop_with_event_coverage(
                self.root, self.run_id, self.loop_id,
                deadline_monotonic=loop.time.monotonic() - 1,
            )

    def test_oversized_derived_start_step_is_never_installed(self):
        # The audit itself remains below MAX_AUDIT_BYTES, while duplicating its
        # large identity into baseline_audit/latest_audit would exceed the
        # immutable runtime document limit.
        oversized = self.write(
            "inputs/oversized-identity.md", artifact(target="x" * 520_000),
        )
        oversized_loop = str(uuid.uuid4())
        with self.assertRaisesRegex(loop.AuditLoopError, "document limit"):
            loop.apply_action(
                "start", root=self.root, run_id=self.run_id,
                loop_id=oversized_loop, idempotency_key="oversized-start",
                expected_previous_sha256=loop.ZERO_HASH,
                occurred_at="2026-07-19T10:00:01Z",
                deadline="2026-07-19T11:00:00Z", max_cycles=2, max_retries=1,
                audit_ref=self.relative(oversized),
                audit_sha256=self.digest(oversized),
            )
        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / oversized_loop
        )
        self.assertFalse(loop_dir.exists())

    def test_start_toctou_failure_cleans_only_its_new_empty_loop(self):
        loop_id = str(uuid.uuid4())
        original = self.baseline.read_bytes()
        real_ensure = loop._ensure_loop_directory

        def create_then_mutate(*args, **kwargs):
            directory = real_ensure(*args, **kwargs)
            self.baseline.write_bytes(original + b"\n")
            return directory

        try:
            with mock.patch.object(
                    loop, "_ensure_loop_directory", side_effect=create_then_mutate):
                with self.assertRaisesRegex(loop.AuditLoopError, "hash mismatch"):
                    loop.apply_action(
                        "start", root=self.root, run_id=self.run_id,
                        loop_id=loop_id, idempotency_key="toctou-start",
                        expected_previous_sha256=loop.ZERO_HASH,
                        occurred_at="2026-07-19T10:00:01Z",
                        deadline="2026-07-19T11:00:00Z",
                        max_cycles=2, max_retries=1,
                        audit_ref=self.relative(self.baseline),
                        audit_sha256=hashlib.sha256(original).hexdigest(),
                    )
        finally:
            self.baseline.write_bytes(original)

        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / loop_id
        )
        self.assertFalse(loop_dir.exists())
        verification = loop.runtime.verify_run_audit_loops(
            self.root, self.run_id, require_terminal=True,
        )
        self.assertEqual([], verification["loops"])

    def test_empty_loop_cleanup_refuses_replacement_inode(self):
        loop_id = str(uuid.uuid4())
        loop_dir, created_identity = loop._ensure_loop_directory(
            self.root, self.run_id, loop_id,
        )
        original_lock = loop_dir / ".loop.lock"
        original_lock.write_bytes(b"")
        os.chmod(original_lock, 0o600)
        original_dir = loop_dir.parent / ("." + loop_id + ".original")
        os.rename(loop_dir, original_dir)
        loop_dir.mkdir(mode=0o700)
        replacement_lock = loop_dir / ".loop.lock"
        replacement_lock.write_bytes(b"")
        os.chmod(replacement_lock, 0o600)

        self.assertFalse(
            loop._cleanup_new_empty_loop(loop_dir, created_identity),
        )
        self.assertTrue(replacement_lock.is_file())
        self.assertTrue(loop_dir.is_dir())

        replacement_lock.unlink()
        loop_dir.rmdir()
        os.rename(original_dir, loop_dir)
        self.assertTrue(
            loop._cleanup_new_empty_loop(loop_dir, created_identity),
        )
        self.assertFalse(loop_dir.exists())

    def test_atomic_loop_create_never_claims_concurrent_directory(self):
        loop_id = str(uuid.uuid4())
        real_ensure = loop._ensure_loop_directory
        loop_dir = (
            self.root / "memory" / "runs" / self.run_id / "loops" / loop_id
        )

        def create_before_runtime(*args, **kwargs):
            loop_dir.mkdir(parents=True, mode=0o700)
            return real_ensure(*args, **kwargs)

        with mock.patch.object(
                loop, "_ensure_loop_directory", side_effect=create_before_runtime):
            with self.assertRaisesRegex(loop.AuditLoopError, "appeared concurrently"):
                loop.apply_action(
                    "start", root=self.root, run_id=self.run_id,
                    loop_id=loop_id, idempotency_key="concurrent-create",
                    expected_previous_sha256=loop.ZERO_HASH,
                    occurred_at="2026-07-19T10:00:01Z",
                    deadline="2026-07-19T11:00:00Z",
                    max_cycles=2, max_retries=1,
                    audit_ref=self.relative(self.baseline),
                    audit_sha256=self.digest(self.baseline),
                )

        self.assertTrue(loop_dir.is_dir())
        self.assertEqual([], list(loop_dir.iterdir()))
        loop_dir.rmdir()

    def test_schema_documents_proposal_only_and_convergence_guards(self):
        schema = json.loads(
            (ROOT / "references" / "audit-loop-state.schema.json").read_text(encoding="utf-8")
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual("2.0", schema["properties"]["schema_version"]["const"])
        self.assertIn("run_parent_event_id", schema["required"])
        self.assertIn("run_parent_event_sha256", schema["required"])
        self.assertEqual(True, schema["properties"]["proposal_only"]["const"])
        self.assertEqual(
            False, schema["properties"]["external_mutation_authorized"]["const"]
        )
        self.assertEqual(1, schema["$defs"]["evidence"]["properties"]["bytes"]["minimum"])
        self.assertIn(
            "observed_at", schema["$defs"]["auditIdentity"]["required"],
        )
        convergence = schema["allOf"][1]["then"]["properties"]["latest_audit"]
        self.assertEqual(
            ["medium", "high"],
            convergence["properties"]["score_confidence"]["enum"],
        )
        owner_accept = schema["allOf"][2]["then"]["properties"]
        owner_reject = schema["allOf"][3]["then"]["properties"]
        retry_exhausted = schema["allOf"][4]["then"]["properties"]
        deadline_exhausted = schema["allOf"][5]["then"]["properties"]
        self.assertEqual("awaiting-intervention", owner_accept["state"]["const"])
        self.assertEqual("needs-input", owner_reject["state"]["const"])
        self.assertEqual("owner-rejected", owner_reject["reason_code"]["const"])
        self.assertEqual("exhausted", retry_exhausted["state"]["const"])
        self.assertEqual(
            "retry-budget-exhausted", retry_exhausted["reason_code"]["const"]
        )
        self.assertEqual("exhausted", deadline_exhausted["state"]["const"])
        self.assertEqual("deadline-expired", deadline_exhausted["reason_code"]["const"])
        reference = schema["$defs"]["reference"]
        self.assertEqual(512, reference["maxLength"])
        reference_pattern = reference["pattern"]
        for invalid in (
                "artifact//result.json", "artifact/../secret.json",
                "artifact/./result.json", "artifact/"):
            self.assertIsNone(re.fullmatch(reference_pattern, invalid))
        self.assertIsNotNone(
            re.fullmatch(reference_pattern, "artifact/result.json"),
        )
        lease_conditions = schema["$defs"]["lease"]["allOf"]
        nonzero = next(
            clause for clause in lease_conditions
            if clause["if"]["properties"].get("generation", {}).get("minimum") == 1
            and "active" not in clause["if"]["properties"]
        )["then"]["properties"]
        self.assertEqual("#/$defs/safeId", nonzero["owner"]["$ref"])
        self.assertEqual("#/$defs/sha256", nonzero["token_sha256"]["$ref"])
        self.assertEqual("string", nonzero["acquired_at"]["type"])
        self.assertEqual("string", nonzero["expires_at"]["type"])
        released = next(
            clause for clause in lease_conditions
            if clause["if"]["properties"].get("generation", {}).get("minimum") == 1
            and clause["if"]["properties"].get("active", {}).get("const") is False
        )["then"]["properties"]["released_at"]
        self.assertEqual("string", released["type"])

        parsed = loop.build_parser().parse_args([
            "owner", "--root", str(self.root), "--run-id", self.run_id,
            "--loop-id", self.loop_id, "--idempotency-key", "typed-owner",
            "--expected-previous-sha256", "a" * 64,
            "--occurred-at", "2026-07-19T10:00:01Z",
            "--lease-generation", "1", "--lease-token", "typed-token",
            "--owner-id", "owner-1", "--decision", "reject",
        ])
        self.assertEqual("reject", parsed.decision)
        with mock.patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                loop.build_parser().parse_args([
                    "start", "--root", str(self.root), "--run-id", self.run_id,
                    "--loop-id", str(uuid.uuid4()),
                    "--idempotency-key", "missing-cli-time",
                    "--expected-previous-sha256", loop.ZERO_HASH,
                    "--audit-ref", self.relative(self.baseline),
                    "--audit-sha256", self.digest(self.baseline),
                    "--deadline", "2026-07-19T11:00:00Z",
                ])


if __name__ == "__main__":
    unittest.main()
