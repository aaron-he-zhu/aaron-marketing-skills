import base64
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import textwrap
import threading
import unittest
import uuid
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CURRENT_CATALOG_VERSION = json.loads(
    (ROOT / "references" / "audit-artifact.schema.json").read_text(encoding="utf-8")
)["properties"]["catalog_version"]["const"]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_events = load_module("workflow_test_run_events", ROOT / "scripts" / "run-events.py")
workflow_loop = load_module("workflow_loop", ROOT / "scripts" / "workflow_loop.py")


TEST_RSA_MODULUS = int(
    "BA9EBFF414F76556E643B471235D863F645E6F24FFEFE999E721B7D15CF06930385808FA2BA65804B5C17395541C0B2B80CF9929B7751BD2D22EB8405768092F857E0AEFD9E8D0EE6B862839FAD7A50D17CEEC151E3CC416172639DC6760CA07FB95516F37BCAE021D37A6AA80F778E361F444FC3E583FF89A3EC47CD5C6C9E63B0AE76B9384F79050A29A7E7C962727E71C5B7DFB57718F45BB930903825500F3AF2A8B5F3F8B4B97F22C9DF91895BA97D89D6C56D4FF2CCEB240EA6BA3FA38BFEBBC47AF974A18E03EBC5F094D9A3A6A32A23F9A13CA2060E383141150A3222DC889B30EA26D99FAF37163E3ABC7187DB259AD8ABE1F99DD6EB352C3211D1B",
    16,
)
TEST_RSA_PRIVATE_EXPONENT = int(
    "01ccee1961439afbfec023e009913654ab3e2266fbe25c61840c0fbbdaad32b8357af4c26abdfe9d34381e4a76a394a06885d83a8e4edea426f861d2e77e952a814ee91b80b4d108070c26029b987407b5cefe92b5fcac4cd842eea76139f4bc3ec80bb8fdad2cd902f95a6132f389e2beee7e4b7eba17718315dc8ba5c9904e186cd918545e3a59dd0eb1174d72a041f89709233c92c2674b474215e45976d776fe7630a866d4898f8cac532aff023bbf88d7ac669cbfdf75dfedd7a06dbdbbed5f54a71219b54f0560471af9a5c424e5d8ca0f893a75292bf74e13919c82f5e8004fc91161496090642b8c2a2aa2cfbc47e9f35f7503a15ba4e68030e8b5c5",
    16,
)
TEST_KEY_ID = "workflow-test-rs256"


def b64url(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


class WorkflowLoopTests(unittest.TestCase):
    WORKFLOW_NODES = (
        "launch-asset-packager",
        "community-launch-runner",
        "launch-readiness-auditor",
        "press-media-relations",
        "launch-day-conductor",
        "launch-monitor",
        "launch-retro-analyzer",
    )

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run_recorded_tick = 0
        self.workflow_recorded_tick = 0

        def next_run_recorded_at():
            value = (
                dt.datetime(2026, 7, 22, 10, 0, tzinfo=dt.timezone.utc)
                + dt.timedelta(seconds=self.run_recorded_tick)
            )
            self.run_recorded_tick += 1
            return value.isoformat().replace("+00:00", "Z")

        def next_workflow_recorded_at():
            value = (
                dt.datetime(2026, 7, 22, 10, 10, tzinfo=dt.timezone.utc)
                + dt.timedelta(seconds=self.workflow_recorded_tick)
            )
            self.workflow_recorded_tick += 1
            return value.isoformat().replace("+00:00", "Z")

        self.run_clock = mock.patch.object(
            run_events, "now_iso", side_effect=next_run_recorded_at,
        )
        self.workflow_clock = mock.patch.object(
            workflow_loop, "_runtime_now", side_effect=next_workflow_recorded_at,
        )
        self.run_clock.start()
        self.workflow_clock.start()
        self.trust_temp = tempfile.TemporaryDirectory()
        self.trust_path = Path(self.trust_temp.name) / "workflow-trust.json"
        modulus_raw = TEST_RSA_MODULUS.to_bytes(
            (TEST_RSA_MODULUS.bit_length() + 7) // 8, "big",
        )
        trust = {
            "$schema": "workflow-execution-approval-trust.schema.json",
            "schema_version": "1.0",
            "key_id": TEST_KEY_ID,
            "algorithm": "RS256",
            "modulus_b64url": b64url(modulus_raw),
            "exponent": 65537,
            "not_before": "2026-01-01T00:00:00Z",
            "not_after": "2027-01-01T00:00:00Z",
        }
        self.trust_path.write_text(
            json.dumps(trust, sort_keys=True) + "\n", encoding="utf-8",
        )
        self.trust_sha256 = hashlib.sha256(self.trust_path.read_bytes()).hexdigest()
        self.trust_environment = mock.patch.dict(os.environ, {
            workflow_loop.TRUST_ANCHOR_PATH_ENV: str(self.trust_path),
            workflow_loop.TRUST_ANCHOR_SHA_ENV: self.trust_sha256,
        })
        self.trust_environment.start()
        (self.root / "references").mkdir()
        for name in (
                "workflow-graph.json", "workflow-graph.source.json",
                "system-catalog.json"):
            shutil.copy2(ROOT / "references" / name, self.root / "references" / name)
        shutil.copytree(
            ROOT / "references" / "workflow-graph",
            self.root / "references" / "workflow-graph",
        )
        self.run_id = str(uuid.uuid4())
        self.loop_minute = 2
        self.run_second = 2
        self.evidence_counter = 0
        self.latest_evidence = None
        started = run_events.append_event(
            self.root,
            self.run_id,
            self.run_request(
                "start", "run_started", None, "started",
                {"kind": "run", "ref": self.run_id},
            ),
        )["event"]
        self.anchor = self.event_reference(started)
        self.run_second += 1

    def tearDown(self):
        self.trust_environment.stop()
        self.workflow_clock.stop()
        self.run_clock.stop()
        self.trust_temp.cleanup()
        self.temp.cleanup()

    def run_request(self, key, event_type, parent, status, subject, *, turn_id=None,
                    references=None, dimensions=None, reason_code=None,
                    actor_type="system", occurred_at=None):
        value = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "idempotency_key": key,
            "event_type": event_type,
            "occurred_at": occurred_at or (
                "2026-07-22T10:00:%02dZ" % self.run_second
            ),
            "actor": {"type": actor_type, "id": "workflow-test"},
            "parent_event_id": parent,
            "turn_id": turn_id,
            "status": status,
            "subject": subject,
            "references": references or [],
            "metrics": {},
            "dimensions": dimensions or {},
        }
        if reason_code is not None:
            value["reason_code"] = reason_code
        return value

    @staticmethod
    def event_reference(event):
        return {
            "kind": "run-event",
            "ref": event["event_id"],
            "sha256": event["event_hash"],
        }

    def append_route(self, node, *, parent=None, prefix="route"):
        events = run_events.load_events(self.root, self.run_id)
        parent = parent or events[-1]["event_id"]
        transition = (
            "initial"
            if run_events.selected_route_state(events, parent) is None
            else "user-reroute"
        )
        self.evidence_counter += 1
        key = "%s-%d-%s" % (prefix, self.evidence_counter, node)
        result = run_events.append_event(
            self.root,
            self.run_id,
            self.run_request(
                key, "route_selected", parent, "succeeded",
                {"kind": "route", "ref": node},
                dimensions={
                    "route_transition": transition,
                    "route_command": "launch",
                },
                reason_code="workflow-evidence",
            ),
        )
        self.run_second += 1
        return result["event"]

    def action_evidence(self, node, *, failed=False, parent=None, prefix="action"):
        route = self.append_route(node, parent=parent, prefix=prefix + "-route")
        self.evidence_counter += 1
        suffix = "%d-%s" % (self.evidence_counter, node)
        if failed:
            turn_id = "failed-" + suffix
            result = run_events.append_event(
                self.root,
                self.run_id,
                self.run_request(
                    prefix + "-failed-" + suffix,
                    "turn_finished",
                    route["event_id"],
                    "failed",
                    {"kind": "turn", "ref": turn_id},
                    turn_id=turn_id,
                ),
            )
        else:
            relative = Path("evidence") / (prefix + "-" + suffix + ".txt")
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("verified workflow action\n", encoding="utf-8")
            artifact_ref = {
                "kind": "artifact",
                "ref": relative.as_posix(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            result = run_events.append_event(
                self.root,
                self.run_id,
                self.run_request(
                    prefix + "-valid-" + suffix,
                    "artifact_validated",
                    route["event_id"],
                    "succeeded",
                    {"kind": "artifact", "ref": "action-" + suffix},
                    references=[artifact_ref],
                    dimensions={"validator": "workflow-action-validator"},
                ),
            )
        self.run_second += 1
        self.latest_evidence = self.event_reference(result["event"])
        return self.latest_evidence

    def verification_evidence(self, prefix="verification", validator="launch-outcome-verifier"):
        route = self.append_route("launch-retro-analyzer", prefix=prefix + "-route")
        self.evidence_counter += 1
        relative = Path("evidence") / ("%s-%d.txt" % (prefix, self.evidence_counter))
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("independently validated launch outcome\n", encoding="utf-8")
        artifact_ref = {
            "kind": "artifact",
            "ref": relative.as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        result = run_events.append_event(
            self.root,
            self.run_id,
            self.run_request(
                "%s-valid-%d" % (prefix, self.evidence_counter),
                "artifact_validated",
                route["event_id"],
                "succeeded",
                {"kind": "artifact", "ref": "%s-%d" % (prefix, self.evidence_counter)},
                references=[artifact_ref],
                dimensions={"validator": validator},
            ),
        )
        self.run_second += 1
        self.latest_evidence = self.event_reference(result["event"])
        return self.latest_evidence

    @staticmethod
    def launch_audit_artifact(verdict="SHIP", validator_clean=True):
        values = {
            "SHIP": {
                "status": "DONE", "score_state": "SCORED", "coverage": 100,
                "confidence": "high", "findings": "[]", "veto_count": 0,
                "cap": "false", "scores": (
                    "raw_overall_score: 90\nfinal_overall_score: 90"
                ),
            },
            "FIX": {
                "status": "DONE_WITH_CONCERNS", "score_state": "SCORED",
                "coverage": 100, "confidence": "high", "findings": "[]",
                "veto_count": 0, "cap": "false", "scores": (
                    "raw_overall_score: 70\nfinal_overall_score: 70"
                ),
            },
            "BLOCK": {
                "status": "DONE", "score_state": "NOT_SCORED", "coverage": 100,
                "confidence": "not_scored", "findings": (
                    "\n  - title: launch access is ineligible\n"
                    "    severity: veto\n"
                    "    evidence: verified access contradicts launch eligibility\n"
                    "  - title: required launch asset is absent\n"
                    "    severity: veto\n"
                    "    evidence: the required asset inventory is incomplete"
                ),
                "veto_count": 2, "cap": "false", "scores": "",
            },
            "UNDECIDED": {
                "status": "NEEDS_INPUT", "score_state": "NOT_SCORED",
                "coverage": 0, "confidence": "not_scored", "findings": "[]",
                "veto_count": 0, "cap": "false", "scores": "",
            },
        }[verdict]
        text = textwrap.dedent(
            """\
            ---
            class: auditor-output
            schema_version: "3.0"
            runbook_version: "3.0.0"
            catalog_version: "{catalog_version}"
            framework: RAMP
            profile: preflight
            ---
            status: {status}
            verdict: {verdict}
            score_state: {score_state}
            objective: verify launch readiness
            target: launch-fixture
            observed_at: 2026-07-22
            context: {{"launch_type":"product","lifecycle_read":"preflight","market":"US","access_model":"first-party"}}
            key_findings: {findings}
            evidence_summary: launch evidence was independently inspected
            evidence_coverage: {coverage}
            score_confidence: {confidence}
            open_loops: none
            recommended_next_skill: launch-day-conductor
            veto_count: {veto_count}
            cap_applied: {cap}
            {scores}
            """
        ).format(
            catalog_version=CURRENT_CATALOG_VERSION,
            verdict=verdict,
            **values,
        )
        if not validator_clean:
            text += "unknown_field: invalid\n"
        return text

    def gate_evidence(
            self, prefix, verdict="SHIP", include_approval=True,
            validator_clean=True, bind_approval=True, signature_valid=True,
            expired=False, approval_overrides=None, approval_actor="system",
            approval_event_occurred_at=None,
            loop_id="launch-loop"):
        node = "launch-readiness-auditor"
        route = self.append_route(node, prefix=prefix + "-route")
        self.evidence_counter += 1
        relative = Path("memory/audits/launch") / (
            "%s-%d.md" % (prefix, self.evidence_counter)
        )
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            self.launch_audit_artifact(verdict, validator_clean), encoding="utf-8",
        )
        artifact_reference = {
            "kind": "artifact",
            "ref": relative.as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        audit = run_events.append_event(
            self.root,
            self.run_id,
            self.run_request(
                "%s-audit-%d" % (prefix, self.evidence_counter),
                "artifact_validated",
                route["event_id"],
                "succeeded",
                {"kind": "artifact", "ref": "audit-%d" % self.evidence_counter},
                references=[artifact_reference],
                dimensions={"validator": "validate-audit-artifact"},
            ),
        )["event"]
        self.run_second += 1
        evidence = [self.event_reference(audit)]
        gate_approval = None
        if include_approval:
            self.evidence_counter += 1
            approval_id = str(uuid.uuid4())
            nonce = str(uuid.uuid4())
            audit_recorded_at = dt.datetime.fromisoformat(
                audit["recorded_at"].replace("Z", "+00:00")
            )
            issued_at = audit_recorded_at + dt.timedelta(seconds=1)
            expires_at = issued_at + (
                dt.timedelta(seconds=1) if expired else dt.timedelta(hours=1)
            )
            approval_document = {
                "$schema": workflow_loop.APPROVAL_SCHEMA,
                "schema_version": "1.0",
                "approval_id": approval_id,
                "key_id": TEST_KEY_ID,
                "algorithm": "RS256",
                "run_id": self.run_id,
                "loop_id": loop_id,
                "action": "launch-day-conductor",
                "audit": {
                    "ref": artifact_reference["ref"],
                    "sha256": artifact_reference["sha256"],
                } if bind_approval else {
                    "ref": "memory/audits/launch/different.md",
                    "sha256": "f" * 64,
                },
                "issued_at": issued_at.isoformat().replace("+00:00", "Z"),
                "expires_at": expires_at.isoformat().replace("+00:00", "Z"),
                "nonce": nonce,
            }
            approval_document.update(approval_overrides or {})
            approval_document["signature"] = self.sign_approval(approval_document)
            if not signature_valid:
                signature_raw = bytearray(base64.urlsafe_b64decode(
                    approval_document["signature"]
                    + "=" * (-len(approval_document["signature"]) % 4)
                ))
                signature_raw[-1] ^= 1
                approval_document["signature"] = b64url(bytes(signature_raw))
            approval_relative = (
                Path("memory/runs") / self.run_id / "approvals"
                / (approval_id + ".json")
            )
            approval_path = self.root / approval_relative
            approval_path.parent.mkdir(parents=True, exist_ok=True)
            approval_path.write_text(
                json.dumps(approval_document, sort_keys=True) + "\n", encoding="utf-8",
            )
            approval_reference = {
                "kind": "artifact",
                "ref": approval_relative.as_posix(),
                "sha256": hashlib.sha256(approval_path.read_bytes()).hexdigest(),
            }
            approval = run_events.append_event(
                self.root,
                self.run_id,
                self.run_request(
                    "%s-approval-%d" % (prefix, self.evidence_counter),
                    "artifact_validated",
                    audit["event_id"],
                    "succeeded",
                    {"kind": "artifact", "ref": approval_id},
                    references=[approval_reference],
                    dimensions={"validator": "verify-workflow-execution-approval"},
                    actor_type=approval_actor,
                    occurred_at=approval_event_occurred_at,
                ),
            )["event"]
            self.run_second += 1
            evidence.append(self.event_reference(approval))
            gate_approval = {
                **approval_reference,
                "nonce": approval_document["nonce"],
            }
        self.latest_evidence = evidence[-1]
        return evidence, gate_approval

    @staticmethod
    def sign_approval(document):
        signed = dict(document)
        signed.pop("signature", None)
        digest_info = (
            workflow_loop.RSA_SHA256_DIGEST_INFO_PREFIX
            + hashlib.sha256(
                workflow_loop.canonical_json(signed).encode("utf-8")
            ).digest()
        )
        width = (TEST_RSA_MODULUS.bit_length() + 7) // 8
        padding = b"\xff" * (width - len(digest_info) - 3)
        encoded = b"\x00\x01" + padding + b"\x00" + digest_info
        signature = pow(
            int.from_bytes(encoded, "big"),
            TEST_RSA_PRIVATE_EXPONENT,
            TEST_RSA_MODULUS,
        ).to_bytes(width, "big")
        return b64url(signature)

    def plan_request(self, loop_id="launch-loop"):
        current_head = run_events.load_events(self.root, self.run_id)[-1]
        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "loop_id": loop_id,
            "workflow_id": "product-launch-execution",
            "idempotency_key": "plan-v1",
            "occurred_at": "2026-07-22T10:00:%02dZ" % self.run_second,
            "objective": "Execute the approved launch and preserve evidence.",
            "hypothesis": "All required launch lanes can produce independently validated evidence.",
            "success_criteria": [{
                "id": "launch-proof",
                "description": "The joined launch outcome artifact passes independent validation.",
                "evidence_kind": "artifact-validation",
                "validator": "launch-outcome-verifier",
            }],
            "run_event_anchor": self.event_reference(current_head),
        }

    def plan(self, loop_id="launch-loop"):
        return workflow_loop.plan(self.root, self.plan_request(loop_id))

    def advance(self, result, event_type, payload, key, occurred_at=None,
                loop_id="launch-loop"):
        if occurred_at is None:
            occurred_at = "2026-07-22T10:%02d:00Z" % self.loop_minute
            self.loop_minute += 1
        request = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "loop_id": loop_id,
            "workflow_id": "product-launch-execution",
            "idempotency_key": key,
            "event_type": event_type,
            "occurred_at": occurred_at,
            "expected_head_sha256": result["state"]["last_event_hash"],
            "payload": payload,
        }
        return workflow_loop.advance(self.root, request), request

    def complete_action(self, result, node, key, *, loop_id="launch-loop"):
        if node == "launch-readiness-auditor":
            evidence, gate_approval = self.gate_evidence(key, loop_id=loop_id)
        else:
            evidence = [self.action_evidence(node, prefix=key)]
            gate_approval = None
        payload = {"node": node, "evidence": evidence}
        if gate_approval is not None:
            payload["gate_approval"] = gate_approval
        result, _ = self.advance(
            result,
            "action-completed",
            payload,
            key,
            loop_id=loop_id,
        )
        return result

    def complete_actions(self, result, prefix="c1", loop_id="launch-loop"):
        for node in self.WORKFLOW_NODES:
            result = self.complete_action(
                result, node, "%s-%s" % (prefix, node), loop_id=loop_id,
            )
        return result

    def verification_payload(self, result, finding_code, prefix):
        evidence = self.verification_evidence(prefix)
        return {
            "result": result,
            "finding_codes": [finding_code],
            "criterion_results": [{
                "criterion_id": "launch-proof",
                "status": result,
                "verified_evidence": [evidence],
            }],
        }

    def test_full_fanout_join_converges_only_after_proposal(self):
        result = self.plan()
        self.assertEqual(["launch-asset-packager"], result["state"]["frontier"])
        result = self.complete_action(result, "launch-asset-packager", "asset-complete")
        self.assertEqual(
            [
                "community-launch-runner", "launch-readiness-auditor",
                "press-media-relations",
            ],
            result["state"]["frontier"],
        )
        for node in (
                "community-launch-runner", "launch-readiness-auditor",
                "press-media-relations"):
            result = self.complete_action(result, node, "complete-" + node)
        self.assertNotIn("launch-monitor", result["state"]["frontier"])
        result = self.complete_action(result, "launch-day-conductor", "complete-conductor")
        self.assertEqual(["launch-monitor"], result["state"]["frontier"])
        result = self.complete_action(result, "launch-monitor", "complete-monitor")
        result = self.complete_action(result, "launch-retro-analyzer", "complete-retro")
        self.assertEqual("verification", result["state"]["stage"])

        result, _ = self.advance(
            result, "verification-recorded",
            self.verification_payload("pass", "launch-evidence-complete", "verify-pass"),
            "verify-pass",
        )
        result, _ = self.advance(
            result, "decision-recorded",
            {
                "decision": "accept", "reason_codes": ["owner-approved"],
                "evidence": [self.latest_evidence],
            },
            "accept",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "converged requires"):
            self.advance(
                result, "terminal-recorded",
                {
                    "outcome": "converged", "reason_codes": ["premature"],
                    "evidence": [self.latest_evidence],
                },
                "premature-terminal",
            )
        proposal = self.root / "launch-outcome-proposal.json"
        proposal.write_text("{}\n", encoding="utf-8")
        proposal_ref = {
            "kind": "artifact",
            "ref": proposal.relative_to(self.root).as_posix(),
            "sha256": hashlib.sha256(proposal.read_bytes()).hexdigest(),
        }
        result, _ = self.advance(
            result, "memory-proposal-recorded",
            {
                "target_registry": "launches", "proposal_only": True,
                "proposal": proposal_ref, "reason_codes": ["verified-outcome"],
            },
            "memory-proposal",
        )
        result, _ = self.advance(
            result, "terminal-recorded",
            {
                "outcome": "converged", "reason_codes": ["verified"],
                "evidence": [self.latest_evidence],
            },
            "terminal",
        )
        self.assertEqual("terminal", result["state"]["status"])
        verified = workflow_loop.verify(self.root, self.run_id, "launch-loop")
        self.assertTrue(verified["valid"])
        self.assertTrue(verified["current_graph_match"])

    def test_plan_anchor_must_be_the_current_selected_head(self):
        self.append_route("launch-asset-packager", prefix="newer-head")
        request = self.plan_request("old-ancestor-anchor")
        request["run_event_anchor"] = self.anchor
        with self.assertRaisesRegex(
                workflow_loop.WorkflowLoopError, "current selected run head"):
            workflow_loop.plan(self.root, request)

    def test_plan_created_at_cannot_precede_anchor_timestamp(self):
        request = self.plan_request("future-anchor")
        request["occurred_at"] = "2026-07-22T10:00:01Z"
        with self.assertRaisesRegex(
                workflow_loop.WorkflowLoopError, "cannot precede anchor occurred_at"):
            workflow_loop.plan(self.root, request)

    def test_post_cutoff_recorded_event_is_fresh_despite_historical_occurred_at(self):
        request = self.plan_request("backdated-evidence")
        request["occurred_at"] = "2026-07-22T10:00:10Z"
        result = workflow_loop.plan(self.root, request)
        evidence = self.action_evidence(
            "launch-asset-packager", prefix="backdated-evidence",
        )
        result, _ = self.advance(
            result,
            "action-completed",
            {"node": "launch-asset-packager", "evidence": [evidence]},
            "accept-recorded-post-cutoff-evidence",
            loop_id="backdated-evidence",
        )
        self.assertIn("launch-asset-packager", result["state"]["completed_nodes"])

    def test_plan_persistence_cutoff_serializes_concurrent_run_event_append(self):
        plan_path = (
            self.root.resolve() / "memory" / "runs" / self.run_id / "workflow-plans"
            / "cutoff-race" / "plan.json"
        )
        artifact_path = self.root / "evidence" / "cutoff-race.txt"
        artifact_path.parent.mkdir(parents=True, exist_ok=True)
        artifact_path.write_text("race evidence\n", encoding="utf-8")
        artifact_reference = {
            "kind": "artifact",
            "ref": artifact_path.relative_to(self.root).as_posix(),
            "sha256": hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
        }
        attempted = threading.Event()
        finished = threading.Event()
        captured = {}

        def append_during_plan_write():
            try:
                attempted.set()
                route = run_events.append_event(
                    self.root,
                    self.run_id,
                    self.run_request(
                        "cutoff-race-route", "route_selected", self.anchor["ref"],
                        "succeeded", {"kind": "route", "ref": "launch-asset-packager"},
                        dimensions={
                            "route_transition": "initial", "route_command": "launch",
                        },
                        reason_code="cutoff-race",
                        occurred_at="2026-07-22T10:00:03Z",
                    ),
                )["event"]
                captured["plan_exists_when_route_committed"] = plan_path.is_file()
                artifact = run_events.append_event(
                    self.root,
                    self.run_id,
                    self.run_request(
                        "cutoff-race-artifact", "artifact_validated",
                        route["event_id"], "succeeded",
                        {"kind": "artifact", "ref": "cutoff-race-artifact"},
                        references=[artifact_reference],
                        dimensions={"validator": "workflow-action-validator"},
                        occurred_at="2026-07-22T10:00:04Z",
                    ),
                )["event"]
                captured["evidence"] = self.event_reference(artifact)
            except Exception as exc:  # surfaced deterministically in the main thread
                captured["error"] = exc
            finally:
                finished.set()

        original = workflow_loop._atomic_write
        thread = threading.Thread(target=append_during_plan_write, daemon=True)
        started = False

        def interleave(path, content):
            nonlocal started
            if Path(path) == plan_path and not started:
                started = True
                thread.start()
                self.assertTrue(attempted.wait(2))
                self.assertFalse(
                    finished.wait(0.1),
                    "run append bypassed the coordinator before plan persistence",
                )
            return original(path, content)

        request = self.plan_request("cutoff-race")
        with mock.patch.object(workflow_loop, "_atomic_write", side_effect=interleave):
            result = workflow_loop.plan(self.root, request)
        self.assertTrue(finished.wait(3))
        thread.join(timeout=1)
        self.assertNotIn("error", captured)
        self.assertTrue(captured["plan_exists_when_route_committed"])
        plan_document = json.loads(plan_path.read_text(encoding="utf-8"))
        self.assertEqual(1, plan_document["evidence_cutoff"]["offset"])
        self.assertEqual(self.anchor["ref"], plan_document["evidence_cutoff"]["ref"])
        result, _ = self.advance(
            result,
            "action-completed",
            {
                "node": "launch-asset-packager",
                "evidence": [captured["evidence"]],
            },
            "cutoff-race-action",
            loop_id="cutoff-race",
        )
        self.assertIn("launch-asset-packager", result["state"]["completed_nodes"])

    def test_preplan_artifact_validation_cannot_satisfy_verification(self):
        stale = self.verification_evidence("preplan-verification")
        request = self.plan_request("backdated-verification")
        result = workflow_loop.plan(self.root, request)
        result = self.complete_actions(
            result, "fresh-verification-actions", loop_id="backdated-verification",
        )
        payload = {
            "result": "pass",
            "finding_codes": ["claimed-fresh"],
            "criterion_results": [{
                "criterion_id": "launch-proof",
                "status": "pass",
                "verified_evidence": [stale],
            }],
        }
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "post-plan"):
            self.advance(
                result, "verification-recorded", payload,
                "reject-backdated-verification",
                loop_id="backdated-verification",
            )

    def test_preplan_run_event_cannot_satisfy_decision_evidence(self):
        stale = self.action_evidence(
            "launch-asset-packager", prefix="preplan-decision",
        )
        request = self.plan_request("backdated-decision")
        result = workflow_loop.plan(self.root, request)
        result = self.complete_actions(
            result, "fresh-decision-actions", loop_id="backdated-decision",
        )
        result, _ = self.advance(
            result, "verification-recorded",
            self.verification_payload(
                "pass", "fresh-verification", "fresh-decision-verification",
            ),
            "fresh-decision-verification",
            loop_id="backdated-decision",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "post-plan"):
            self.advance(
                result,
                "decision-recorded",
                {
                    "decision": "accept", "reason_codes": ["claimed-fresh"],
                    "evidence": [stale],
                },
                "reject-backdated-decision",
                loop_id="backdated-decision",
            )

    def assert_gate_verdict_stays_closed(
            self, verdict, *, include_approval=True, validator_clean=True,
            bind_approval=True, signature_valid=True, expired=False,
            approval_overrides=None, approval_actor="system",
            approval_event_occurred_at=None,
            expected="SHIP|validator-clean|execution approval"):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "gate-start",
        )
        evidence, gate_approval = self.gate_evidence(
            "gate-%s" % verdict.lower(), verdict=verdict,
            include_approval=include_approval, validator_clean=validator_clean,
            bind_approval=bind_approval, signature_valid=signature_valid,
            expired=expired, approval_overrides=approval_overrides,
            approval_actor=approval_actor,
            approval_event_occurred_at=approval_event_occurred_at,
        )
        payload = {"node": "launch-readiness-auditor", "evidence": evidence}
        if gate_approval is not None:
            payload["gate_approval"] = gate_approval
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, expected):
            self.advance(
                result,
                "action-completed",
                payload,
                "reject-gate-%s" % verdict.lower(),
            )
        self.assertIn("launch-readiness-auditor", result["state"]["frontier"])
        self.assertNotIn("launch-day-conductor", result["state"]["frontier"])

    def test_fix_verdict_cannot_release_launch_day(self):
        self.assert_gate_verdict_stays_closed("FIX")

    def test_block_verdict_cannot_release_launch_day(self):
        self.assert_gate_verdict_stays_closed("BLOCK")

    def test_undecided_verdict_cannot_release_launch_day(self):
        self.assert_gate_verdict_stays_closed("UNDECIDED")

    def test_ship_without_independent_execution_approval_stays_closed(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", include_approval=False, expected="signed gate_approval",
        )

    def test_ship_approval_not_bound_to_exact_audit_artifact_stays_closed(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", bind_approval=False, expected="audit binding",
        )

    def test_non_validator_clean_ship_stays_closed(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", validator_clean=False, expected="validator-clean",
        )

    def test_self_reported_host_tool_allowed_cannot_release_gate(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "self-reported-start",
        )
        evidence, _ = self.gate_evidence(
            "self-reported", include_approval=False,
        )
        parent = run_events.load_events(self.root, self.run_id)[-1]
        claimed = run_events.append_event(
            self.root,
            self.run_id,
            self.run_request(
                "self-reported-host-approval", "tool_allowed",
                parent["event_id"], "started",
                {"kind": "tool", "ref": "launch-execution-approval-self"},
                turn_id="self-reported-approval",
                dimensions={"tool_name": "launch-execution-approval"},
                reason_code="execution-approved",
                actor_type="host",
            ),
        )["event"]
        evidence.append(self.event_reference(claimed))
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "signed gate_approval"):
            self.advance(
                result, "action-completed",
                {"node": "launch-readiness-auditor", "evidence": evidence},
                "reject-self-reported-host",
            )

    def test_bad_approval_signature_cannot_release_gate(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", signature_valid=False, expected="signature verification failed",
        )

    def test_valid_signature_with_wrong_action_binding_cannot_release_gate(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", approval_overrides={"action": "launch-monitor"},
            expected="action binding mismatch",
        )

    def test_expired_signed_approval_cannot_release_gate(self):
        self.assert_gate_verdict_stays_closed(
            "SHIP", expired=True, expected="not valid at evidence/action time",
        )

    def test_backdated_occurred_at_cannot_hide_runtime_approval_expiry(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "runtime-expiry-start",
        )
        with mock.patch.object(run_events, "now_iso", side_effect=[
                "2026-07-22T10:00:20Z",
                "2026-07-22T10:00:21Z",
                "2026-07-22T20:18:00Z"]):
            evidence, gate_approval = self.gate_evidence(
                "runtime-expiry", approval_event_occurred_at="2026-07-22T10:00:30Z",
                approval_overrides={
                    "issued_at": "2026-07-22T10:00:22Z",
                    "expires_at": "2026-07-22T11:00:00Z",
                },
            )
        with mock.patch.object(
                workflow_loop, "_runtime_now",
                return_value="2026-07-22T20:18:01Z"):
            with self.assertRaisesRegex(
                    workflow_loop.WorkflowLoopError,
                    "not valid at evidence/action time"):
                self.advance(
                    result, "action-completed", {
                        "node": "launch-readiness-auditor",
                        "evidence": evidence,
                        "gate_approval": gate_approval,
                    }, "reject-runtime-expired-approval",
                    occurred_at="2026-07-22T10:05:00Z",
                )

    def test_historical_valid_approval_remains_valid_on_later_verify(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "historical-start",
        )
        evidence, gate_approval = self.gate_evidence("historical-gate")
        result, _ = self.advance(
            result, "action-completed", {
                "node": "launch-readiness-auditor",
                "evidence": evidence,
                "gate_approval": gate_approval,
            }, "historical-gate-action",
        )
        with mock.patch.object(
                workflow_loop, "_runtime_now",
                return_value="2036-07-22T20:18:01Z"):
            verified = workflow_loop.verify(
                self.root, self.run_id, "launch-loop",
            )
        self.assertTrue(verified["valid"])
        self.assertIn(
            "launch-readiness-auditor", result["state"]["completed_nodes"],
        )

    def test_missing_or_drifted_external_trust_anchor_fails_closed(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(
                    workflow_loop.WorkflowLoopError, "host-configured approval trust"):
                self.plan("missing-trust")

        result = self.plan("trust-drift")
        with mock.patch.dict(os.environ, {
                workflow_loop.TRUST_ANCHOR_SHA_ENV: "f" * 64}):
            with self.assertRaisesRegex(
                    workflow_loop.WorkflowLoopError, "host-pinned SHA-256"):
                workflow_loop.verify(self.root, self.run_id, "trust-drift")

    def test_signed_approval_nonce_cannot_be_replayed_in_next_cycle(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "replay-cycle-one-asset",
        )
        result = self.complete_action(
            result, "community-launch-runner", "replay-cycle-one-community",
        )
        evidence, gate_approval = self.gate_evidence("replay-cycle-one-gate")
        result, _ = self.advance(
            result, "action-completed", {
                "node": "launch-readiness-auditor",
                "evidence": evidence,
                "gate_approval": gate_approval,
            }, "replay-cycle-one-gate",
        )
        for node in (
                "press-media-relations", "launch-day-conductor",
                "launch-monitor", "launch-retro-analyzer"):
            result = self.complete_action(
                result, node, "replay-cycle-one-" + node,
            )
        result, _ = self.advance(
            result, "verification-recorded",
            self.verification_payload(
                "fail", "replay-revision", "replay-cycle-one-verification",
            ),
            "replay-cycle-one-verification",
        )
        result, _ = self.advance(
            result, "decision-recorded", {
                "decision": "revise", "reason_codes": ["repeat-cycle"],
                "evidence": [self.latest_evidence],
            }, "replay-cycle-one-revise",
        )
        result = self.complete_action(
            result, "launch-asset-packager", "replay-cycle-two-asset",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "already consumed"):
            self.advance(
                result, "action-completed", {
                    "node": "launch-readiness-auditor",
                    "evidence": evidence,
                    "gate_approval": gate_approval,
                }, "replay-cycle-two-old-approval",
            )

    def test_compare_and_swap_and_idempotent_retry(self):
        first = self.plan()
        duplicate = self.plan()
        self.assertTrue(duplicate["deduplicated"])
        evidence = self.action_evidence("launch-asset-packager", prefix="cas")
        result, request = self.advance(
            first, "action-completed",
            {"node": "launch-asset-packager", "evidence": [evidence]},
            "asset",
        )
        exact = workflow_loop.advance(self.root, request)
        self.assertTrue(exact["deduplicated"])
        changed = dict(request)
        changed["payload"] = {
            "node": "community-launch-runner", "evidence": [evidence],
        }
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "idempotency_key"):
            workflow_loop.advance(self.root, changed)
        stale = dict(request)
        stale["idempotency_key"] = "stale-new-key"
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "stale expected"):
            workflow_loop.advance(self.root, stale)
        self.assertEqual(2, result["state"]["counts"]["events"])

    def test_projection_failure_recovers_and_tampering_fails_closed(self):
        result = self.plan()
        evidence = self.action_evidence("launch-asset-packager", prefix="durable")
        request = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "loop_id": "launch-loop",
            "workflow_id": "product-launch-execution",
            "idempotency_key": "durable-action",
            "event_type": "action-completed",
            "occurred_at": "2026-07-22T10:02:00Z",
            "expected_head_sha256": result["state"]["last_event_hash"],
            "payload": {"node": "launch-asset-packager", "evidence": [evidence]},
        }
        original = workflow_loop._atomic_write

        def fail_state(path, content):
            if Path(path).name == "state.json":
                raise OSError("simulated projection failure")
            return original(path, content)

        with mock.patch.object(workflow_loop, "_atomic_write", side_effect=fail_state):
            with self.assertRaisesRegex(workflow_loop.EventCommittedError, "event_committed=true"):
                workflow_loop.advance(self.root, request)
        recovered = workflow_loop.advance(self.root, request)
        self.assertTrue(recovered["deduplicated"])
        state_path = (
            self.root / "memory" / "runs" / self.run_id / "workflow-plans"
            / "launch-loop" / "state.json"
        )
        state_path.write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "projection"):
            workflow_loop.verify(self.root, self.run_id, "launch-loop")
        repaired = workflow_loop.verify(
            self.root, self.run_id, "launch-loop", repair_projection=True,
        )
        self.assertTrue(repaired["projection_current"])
        stream = state_path.with_name("events.ndjson")
        text = stream.read_text(encoding="utf-8")
        stream.write_text(
            text.replace("launch-asset-packager", "launch-retro-analyzer", 1),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "hash"):
            workflow_loop.verify(self.root, self.run_id, "launch-loop")

    def test_recorded_at_tampering_breaks_the_event_hash(self):
        self.plan()
        stream = (
            self.root / "memory" / "runs" / self.run_id / "workflow-plans"
            / "launch-loop" / "events.ndjson"
        )
        event = json.loads(stream.read_text(encoding="utf-8"))
        event["recorded_at"] = "2026-07-22T09:00:00Z"
        stream.write_text(
            json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "event hash mismatch"):
            workflow_loop.verify(self.root, self.run_id, "launch-loop")

    def test_runtime_recorded_at_must_advance_monotonically(self):
        result = self.plan()
        evidence = self.action_evidence(
            "launch-asset-packager", prefix="recorded-monotonic",
        )
        with mock.patch.object(
                workflow_loop, "_runtime_now",
                return_value=result["event"]["recorded_at"]):
            with self.assertRaisesRegex(
                    workflow_loop.WorkflowLoopError,
                    "runtime recorded_at must be strictly later"):
                self.advance(
                    result, "action-completed", {
                        "node": "launch-asset-packager", "evidence": [evidence],
                    }, "reject-nonmonotonic-recorded-at",
                )

    def test_recomputed_nonmonotonic_recorded_at_fails_replay(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "persisted-monotonic",
        )
        stream = (
            self.root / "memory" / "runs" / self.run_id / "workflow-plans"
            / "launch-loop" / "events.ndjson"
        )
        events = [
            json.loads(line) for line in stream.read_text(encoding="utf-8").splitlines()
        ]
        events[1]["recorded_at"] = events[0]["recorded_at"]
        without_hash = dict(events[1])
        without_hash.pop("event_hash")
        events[1]["event_hash"] = workflow_loop.sha256_json(without_hash)
        stream.write_text(
            "".join(
                json.dumps(event, sort_keys=True, separators=(",", ":")) + "\n"
                for event in events
            ),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
                workflow_loop.WorkflowLoopError,
                "recorded_at timestamps must be strictly monotonic"):
            workflow_loop.verify(self.root, self.run_id, "launch-loop")
        self.assertEqual(
            result["event"]["recorded_at"], result["state"]["last_recorded_at"],
        )

    def test_repeated_failed_verification_forces_escalation(self):
        result = self.complete_actions(self.plan(), "cycle-one")
        result, _ = self.advance(
            result, "verification-recorded",
            self.verification_payload("fail", "missing-proof", "verify-one"),
            "verify-one",
        )
        result, _ = self.advance(
            result, "decision-recorded",
            {
                "decision": "revise", "reason_codes": ["repair-proof"],
                "evidence": [self.latest_evidence],
            },
            "revise-one",
        )
        result = self.complete_actions(result, "cycle-two")
        result, _ = self.advance(
            result, "verification-recorded",
            self.verification_payload("fail", "missing-proof", "verify-two"),
            "verify-two",
        )
        self.assertEqual("escalation-required", result["state"]["stage"])
        self.assertEqual(2, result["state"]["stall_count"])
        result, _ = self.advance(
            result, "terminal-recorded",
            {
                "outcome": "escalated", "reason_codes": ["stalled"],
                "evidence": [self.latest_evidence],
            },
            "escalate-terminal",
        )
        self.assertEqual("escalated", result["state"]["terminal"]["outcome"])

    def test_retry_budget_is_separate_from_cycle_budget(self):
        result = self.plan()
        for attempt in range(3):
            evidence = self.action_evidence(
                "launch-asset-packager", failed=True, prefix="retry-%d" % attempt,
            )
            result, _ = self.advance(
                result,
                "action-failed",
                {
                    "node": "launch-asset-packager",
                    "failure_code": "transient-provider",
                    "retryable": True,
                    "evidence": [evidence],
                },
                "retry-failed-%d" % attempt,
            )
        self.assertEqual(1, result["state"]["cycle"])
        self.assertEqual(2, result["state"]["counts"]["retries"])
        self.assertEqual("escalation-required", result["state"]["stage"])

    def test_cycle_cap_exhausts_without_conflating_retries(self):
        result = self.plan()
        for cycle in range(1, 4):
            result = self.complete_actions(result, "cap-cycle-%d" % cycle)
            result, _ = self.advance(
                result,
                "verification-recorded",
                self.verification_payload(
                    "fail", "distinct-finding-%d" % cycle, "cap-verify-%d" % cycle,
                ),
                "cap-verify-%d" % cycle,
            )
            result, _ = self.advance(
                result,
                "decision-recorded",
                {
                    "decision": "revise",
                    "reason_codes": ["cycle-revision-%d" % cycle],
                    "evidence": [self.latest_evidence],
                },
                "cap-revise-%d" % cycle,
            )
        self.assertEqual(3, result["state"]["cycle"])
        self.assertEqual(0, result["state"]["counts"]["retries"])
        self.assertEqual("exhausted", result["state"]["forced_outcome"])
        result, _ = self.advance(
            result,
            "terminal-recorded",
            {
                "outcome": "exhausted", "reason_codes": ["cycle-cap"],
                "evidence": [self.latest_evidence],
            },
            "cycle-cap-terminal",
        )
        self.assertEqual("exhausted", result["state"]["terminal"]["outcome"])

    def test_wait_and_abort_require_matching_typed_decisions(self):
        for decision, outcome in (("wait", "waiting"), ("abort", "aborted")):
            loop_id = outcome + "-loop"
            result = self.complete_actions(
                self.plan(loop_id), outcome + "-actions", loop_id=loop_id,
            )
            result, _ = self.advance(
                result,
                "verification-recorded",
                self.verification_payload(
                    "inconclusive", outcome + "-uncertain", outcome + "-verify",
                ),
                outcome + "-verify",
                loop_id=loop_id,
            )
            result, _ = self.advance(
                result,
                "decision-recorded",
                {
                    "decision": decision, "reason_codes": [outcome + "-requested"],
                    "evidence": [self.latest_evidence],
                },
                outcome + "-decision",
                loop_id=loop_id,
            )
            with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "matching typed"):
                self.advance(
                    result,
                    "terminal-recorded",
                    {
                        "outcome": "failed", "reason_codes": ["mismatched"],
                        "evidence": [self.latest_evidence],
                    },
                    outcome + "-wrong-terminal",
                    loop_id=loop_id,
                )
            result, _ = self.advance(
                result,
                "terminal-recorded",
                {
                    "outcome": outcome, "reason_codes": [outcome + "-confirmed"],
                    "evidence": [self.latest_evidence],
                },
                outcome + "-terminal",
                loop_id=loop_id,
            )
            self.assertEqual(outcome, result["state"]["terminal"]["outcome"])

    def test_branch_action_failure_fails_closed_before_partial_join(self):
        result = self.complete_action(
            self.plan(), "launch-asset-packager", "fanout-start",
        )
        failure = self.action_evidence(
            "community-launch-runner", failed=True, prefix="community-failure",
        )
        result, _ = self.advance(
            result,
            "action-failed",
            {
                "node": "community-launch-runner",
                "failure_code": "non-retryable-policy",
                "retryable": False,
                "evidence": [failure],
            },
            "community-failed",
        )
        self.assertEqual([], result["state"]["frontier"])
        self.assertEqual("escalation-required", result["state"]["stage"])

    def test_deadline_requires_typed_escalation_terminal(self):
        result = self.plan()
        evidence = self.action_evidence("launch-asset-packager", prefix="deadline")
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "terminal-recorded"):
            self.advance(
                result,
                "action-completed",
                {"node": "launch-asset-packager", "evidence": [evidence]},
                "late-action",
                occurred_at="2026-07-30T10:00:00Z",
            )
        result, _ = self.advance(
            result,
            "terminal-recorded",
            {
                "outcome": "escalated", "reason_codes": ["deadline"],
                "evidence": [evidence],
            },
            "deadline-terminal",
            occurred_at="2026-07-30T10:00:00Z",
        )
        self.assertIn("deadline", result["state"]["terminal"]["bounds"])

    def test_illegal_transition_and_self_asserted_verification_fail_closed(self):
        result = self.plan()
        payload = self.verification_payload("pass", "premature", "illegal-verify")
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "not valid in stage"):
            self.advance(result, "verification-recorded", payload, "illegal-verification")

        result = self.complete_actions(result, "valid-actions")
        wrong = self.verification_evidence(
            "wrong-validator", validator="self-asserted-validator",
        )
        payload = {
            "result": "pass",
            "finding_codes": ["claimed-pass"],
            "criterion_results": [{
                "criterion_id": "launch-proof",
                "status": "pass",
                "verified_evidence": [wrong],
            }],
        }
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "artifact_validated"):
            self.advance(result, "verification-recorded", payload, "self-asserted")

    def test_sibling_run_branch_cannot_satisfy_selected_action(self):
        result = self.plan()
        sibling = self.action_evidence(
            "launch-asset-packager", parent=self.anchor["ref"], prefix="sibling",
        )
        # Append a different branch from the plan anchor after the sibling, making
        # it the selected run ancestry while excluding the cited sibling event.
        self.action_evidence(
            "community-launch-runner", parent=self.anchor["ref"], prefix="selected",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "selected-ancestry"):
            self.advance(
                result,
                "action-completed",
                {"node": "launch-asset-packager", "evidence": [sibling]},
                "sibling-evidence",
            )

    def test_event_budget_reserves_the_terminal_slot(self):
        source_path = self.root / "references" / "workflow-graph.source.json"
        graph_path = self.root / "references" / "workflow-graph.json"
        source = json.loads(source_path.read_text(encoding="utf-8"))
        source["workflows"][0]["budgets"]["max_events"] = 8
        source_path.write_text(
            json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
        graph = json.loads(graph_path.read_text(encoding="utf-8"))
        graph["workflows"] = source["workflows"]
        graph["authority"]["source_sha256"] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        graph.pop("graph_sha256")
        graph["graph_sha256"] = workflow_loop.sha256_json(graph)
        graph_path.write_text(
            json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
        result = self.plan("small-budget")
        for index, node in enumerate(self.WORKFLOW_NODES[:-1]):
            result = self.complete_action(
                result, node, "small-%d" % index, loop_id="small-budget",
            )
        final_evidence = self.action_evidence(
            "launch-retro-analyzer", prefix="budget-final",
        )
        with self.assertRaisesRegex(workflow_loop.WorkflowLoopError, "terminal-recorded"):
            self.advance(
                result,
                "action-completed",
                {"node": "launch-retro-analyzer", "evidence": [final_evidence]},
                "no-final-action",
                loop_id="small-budget",
            )
        result, _ = self.advance(
            result,
            "terminal-recorded",
            {
                "outcome": "exhausted", "reason_codes": ["event-budget"],
                "evidence": [final_evidence],
            },
            "reserved-terminal",
            loop_id="small-budget",
        )
        self.assertEqual(8, result["state"]["counts"]["events"])
        self.assertEqual("exhausted", result["state"]["terminal"]["outcome"])


if __name__ == "__main__":
    unittest.main()
