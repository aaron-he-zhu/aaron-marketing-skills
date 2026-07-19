import importlib.util
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import threading
import unittest
import uuid
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("run_events", ROOT / "scripts" / "run-events.py")
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)
CONTEXT_SPEC = importlib.util.spec_from_file_location(
    "context_resolver", ROOT / "scripts" / "context-resolver.py"
)
context_runtime = importlib.util.module_from_spec(CONTEXT_SPEC)
CONTEXT_SPEC.loader.exec_module(context_runtime)


class RunEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run_id = str(uuid.uuid4())

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def offsets(value=None):
        return {name: value for name in runtime.REGISTRIES}

    def request(self, key, event_type="context_resolved", parent=None, turn_id=None,
                status="succeeded", subject=None, **overrides):
        value = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "idempotency_key": key,
            "event_type": event_type,
            "occurred_at": "2026-07-19T10:00:00Z",
            "actor": {"type": "system", "id": "test-host"},
            "parent_event_id": parent,
            "turn_id": turn_id,
            "status": status,
            "subject": subject or {"kind": "context", "ref": "fixture"},
            "references": [],
            "metrics": {},
            "dimensions": {},
        }
        value.update(overrides)
        return value

    def route_request(self, key, parent, target="content-writer", command="seo-geo",
                      reason_code="fixture", transition="initial", actor_type="system"):
        return self.request(
            key,
            event_type="route_selected",
            parent=parent,
            status="succeeded",
            subject={"kind": "route", "ref": target},
            actor={"type": actor_type, "id": "test-host"},
            reason_code=reason_code,
            dimensions={
                "route_transition": transition,
                "route_command": command,
            },
        )

    def select_route(self, key="route-initial", target="content-writer",
                     command="seo-geo", reason_code="fixture",
                     transition="initial", parent=None, actor_type="system"):
        events = runtime.load_events(self.root, self.run_id)
        return runtime.append_event(
            self.root,
            self.run_id,
            self.route_request(
                key,
                parent or events[-1]["event_id"],
                target=target,
                command=command,
                reason_code=reason_code,
                transition=transition,
                actor_type=actor_type,
            ),
        )

    def ensure_initial_route(self):
        events = runtime.load_events(self.root, self.run_id)
        state = runtime.project_events(self.run_id, events)
        if state["route_skill"] is None:
            return self.select_route(
                key="route-initial-" + events[-1]["event_id"],
                parent=events[-1]["event_id"],
            )
        return None

    def start(self):
        return runtime.append_event(
            self.root,
            self.run_id,
            self.request(
                "start", event_type="run_started", parent=None,
                subject={"kind": "run", "ref": self.run_id}, status="started",
            ),
        )

    def write_json(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    @staticmethod
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def context_manifest_value(self, run_id=None, turn_id="turn-1", candidates=None,
                               target_skill="content-writer"):
        request = {
            "schema_version": "1.0",
            "run_id": run_id or self.run_id,
            "turn_id": turn_id,
            "as_of": "2026-07-19T10:00:00Z",
            "route": {
                "command": "seo-geo",
                "target_skill": target_skill,
                "reason_code": "fixture",
                "scenario_shards": [],
            },
            "budget": {
                "max_bytes": 1024,
                "max_resources": 1,
                "max_inspection_bytes": 2048,
                "max_sensitivity": "internal",
            },
            "registry_offsets": self.offsets(None),
            "candidates": list(candidates or []),
        }
        return context_runtime.resolve_context(request, ROOT, self.root)

    def context_reference(self, value=None):
        value = value or self.context_manifest_value()
        stream = self.root / "memory" / "runs" / self.run_id / "events.ndjson"
        if stream.is_file():
            self.ensure_initial_route()
        relative = "memory/runs/%s/turns/%s/context-manifest.json" % (
            value["run_id"], value["turn_id"],
        )
        (self.root / relative).parent.mkdir(parents=True, exist_ok=True)
        digest, _existed = context_runtime.write_manifest(self.root, relative, value)
        return {
            "ref": relative,
            "sha256": digest,
            "context_signature": value["context_signature"],
        }

    def snapshot_value(self, context, turn_id="turn-1", snapshot_id=None):
        tools = [{"name": "Read", "mode": "read-only", "schema_sha256": "2" * 64}]
        context_document = json.loads(
            (self.root / context["ref"]).read_text(encoding="utf-8")
        )
        return {
            "schema_version": "1.0",
            "snapshot_id": snapshot_id or str(uuid.uuid4()),
            "run_id": self.run_id,
            "turn_id": turn_id,
            "parent_turn_id": None,
            "created_at": "2026-07-19T10:01:00Z",
            "skill": {
                "name": context_document["route"]["target_skill"],
                "version": context_document["route"]["catalog_version"],
                "contract_sha256": context_document["route"]["skill_sha256"],
            },
            "host": {
                "adapter": "test-host",
                "adapter_version": "1.0.0",
                "model_provider": "test-provider",
                "model_id": "test-model",
            },
            "system_prompt_sha256": "3" * 64,
            "context_manifest": {
                "ref": context["ref"],
                "sha256": context["sha256"],
                "bytes": (self.root / context["ref"]).stat().st_size,
                "token_estimate": None,
                "estimator": None,
                "context_signature": context["context_signature"],
            },
            "tools": tools,
            "toolset_sha256": runtime.sha256_json(tools),
            "registry_offsets": self.offsets(None),
            "permission_profile": {
                "mode": "proposal-only",
                "sandbox": "test",
                "network": False,
                "external_mutations": False,
            },
        }

    def save_point_value(self, snapshot, context, state, save_point_id=None):
        return {
            "schema_version": "1.0",
            "save_point_id": save_point_id or str(uuid.uuid4()),
            "run_id": self.run_id,
            "turn_id": "turn-1",
            "created_at": "2026-07-19T10:02:00Z",
            "last_event_id": state["last_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "status": "ready",
            "turn_snapshot": snapshot,
            "context_manifest": context,
            "artifacts": [],
            "registry_offsets": self.offsets(None),
            "visited_skills": list(state["route_chain"]),
            "chain_depth": state["automatic_handoff_depth"],
            "pending_handoff": None,
            "next_action": {"code": "continue"},
        }

    def envelope_value(self, context, save_point, state, status="succeeded"):
        context_document = json.loads(
            (self.root / context["ref"]).read_text(encoding="utf-8")
        )
        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "parent_run_id": None,
            "started_at": "2026-07-19T10:00:00Z",
            "ended_at": "2026-07-19T10:03:00Z",
            "status": status,
            "evidence_mode": "simulated",
            "route": {
                "skill": context_document["route"]["target_skill"],
                "version": context_document["route"]["catalog_version"],
                "reason_code": context_document["route"]["reason_code"],
            },
            "context_manifests": [context],
            "last_event_id": state["last_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "save_point": save_point,
            "registry_offsets": self.offsets(None),
            "artifacts": [],
            "metrics": {"turns": 1, "tool_calls": 0},
            "failure_class": None,
            "next_action": None,
        }

    def degraded_envelope_value(self, state, status="failed"):
        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "parent_run_id": None,
            "started_at": "2026-07-19T10:00:00Z",
            "ended_at": "2026-07-19T10:03:00Z",
            "status": status,
            "evidence_mode": "none",
            "route": None,
            "context_manifests": [],
            "last_event_id": state["last_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "save_point": None,
            "registry_offsets": self.offsets(None),
            "artifacts": [],
            "metrics": {"turns": 0, "tool_calls": 0},
            "failure_class": "loop",
            "next_action": None,
        }

    @staticmethod
    def loop_audit_identity():
        return {
            "ref": "inputs/audit.md",
            "sha256": "a" * 64,
            "schema_version": "3.0",
            "runbook_version": "3.0.0",
            "catalog_version": "18.0.0",
            "framework": "CORE-EEAT",
            "profile": "blog-post",
            "target": "fixture",
            "observed_at": "2026-07-19",
            "target_identity_sha256": "b" * 64,
            "context_sha256": "c" * 64,
            "status": "DONE_WITH_CONCERNS",
            "verdict": "FIX",
            "score_state": "SCORED",
            "evidence_coverage": 100,
            "score_confidence": "medium",
            "raw_overall_score": 80,
            "final_overall_score": 80,
        }

    @staticmethod
    def loop_wrapper(step):
        return {
            "document": step["document"],
            "ref": step["ref"],
            "sha256": step["sha256"],
        }

    def loop_step_fixture(
            self, loop_id, parent_event, prior=None, *, transition=None,
            state=None, reason_code=None, materialize=True):
        sequence = 1 if prior is None else prior["document"]["sequence"] + 1
        transition = transition or ("start" if prior is None else "deadline-expired")
        state = state or ("awaiting-proposal" if prior is None else "exhausted")
        reason_code = reason_code or (
            "loop-started" if prior is None else "deadline-expired"
        )
        previous_ref = None if prior is None else prior["ref"]
        previous_sha = runtime.ZERO_HASH if prior is None else prior["sha256"]
        reference = "memory/runs/%s/loops/%s/%03d-%s.json" % (
            self.run_id, loop_id, sequence, transition,
        )
        occurred_at = "2026-07-19T10:%02d:00Z" % sequence
        document = {
            "schema_version": "2.0",
            "run_id": self.run_id,
            "loop_id": loop_id,
            "transition_id": str(uuid.uuid5(
                uuid.NAMESPACE_URL,
                "%s:%s:%d:%s" % (self.run_id, loop_id, sequence, transition),
            )),
            "sequence": sequence,
            "transition": transition,
            "from_state": None if prior is None else prior["document"]["state"],
            "state": state,
            "cycle": 1,
            "max_cycles": 3,
            "total_retries": 0,
            "state_retries": 0,
            "max_retries": 2,
            "backoff_seconds": 0,
            "retry_not_before": None,
            "deadline": "2026-07-19T11:00:00Z",
            "occurred_at": occurred_at,
            "recorded_at": occurred_at,
            "idempotency_key": "fixture-%s-%03d" % (loop_id[:12], sequence),
            "request_hash": runtime.sha256_json({
                "loop_id": loop_id, "sequence": sequence,
            }),
            "run_parent_event_id": parent_event["event_id"],
            "run_parent_event_sha256": parent_event["event_hash"],
            "previous_step_ref": previous_ref,
            "previous_step_sha256": previous_sha,
            "expected_previous_sha256": previous_sha,
            "proposal_only": True,
            "external_mutation_authorized": False,
            "baseline_audit": self.loop_audit_identity(),
            "latest_audit": self.loop_audit_identity(),
            "proposal": None,
            "owner": None,
            "intervention": None,
            "reason_code": reason_code,
            "lease": {
                "generation": 0,
                "active": False,
                "owner": None,
                "token_sha256": None,
                "acquired_at": None,
                "expires_at": None,
                "released_at": None,
            },
        }
        expected_sha = hashlib.sha256(
            runtime._serialized_immutable_json_bytes(document)
        ).hexdigest()
        _stream, _projection, run_dir = runtime.run_paths(
            self.root, self.run_id, create=False,
        )
        loop_dir = runtime.ensure_child_directories(
            runtime.normalized_root(self.root), run_dir, ["loops", loop_id],
        )
        path = loop_dir / Path(reference).name
        with runtime.locked_run_coordinator(self.root, self.run_id):
            anchored = runtime.anchor_loop_step(
                self.root, self.run_id, loop_id, reference, expected_sha,
                document, _coordinator_locked=True,
            )
            if materialize:
                self.assertEqual(
                    expected_sha,
                    runtime.write_immutable_json(self.root, path, document),
                )
        return {
            "document": document,
            "ref": reference,
            "sha256": expected_sha,
            "path": path,
            "event": anchored["event"],
        }

    def test_idempotency_hash_chain_and_projection_repair(self):
        original_atomic_write = runtime.atomic_write_json

        def broken(*args, **kwargs):
            raise OSError("disk full")

        runtime.atomic_write_json = broken
        try:
            with self.assertRaisesRegex(runtime.RunEventError, "event_committed=true"):
                self.start()
        finally:
            runtime.atomic_write_json = original_atomic_write

        stream, projection, _ = runtime.run_paths(self.root, self.run_id)
        self.assertEqual(1, len(stream.read_text(encoding="utf-8").splitlines()))
        repaired = self.start()
        self.assertTrue(repaired["deduplicated"])
        self.assertTrue(projection.is_file())
        self.assertEqual(runtime.ZERO_HASH, repaired["event"]["previous_hash"])
        self.assertEqual(1, repaired["projection"]["last_offset"])

        changed = self.request(
            "start", event_type="run_started", parent=None,
            subject={"kind": "run", "ref": self.run_id}, status="started",
            occurred_at="2026-07-19T11:00:00Z",
        )
        with self.assertRaisesRegex(runtime.RunEventError, "idempotency"):
            runtime.append_event(self.root, self.run_id, changed)

    def test_parent_links_form_a_session_tree(self):
        root = self.start()["event"]
        first = runtime.append_event(
            self.root, self.run_id,
            self.request("branch-a", parent=root["event_id"], subject={"kind": "route", "ref": "a"}),
        )
        second = runtime.append_event(
            self.root, self.run_id,
            self.request("branch-b", parent=root["event_id"], subject={"kind": "route", "ref": "b"}),
        )
        state = second["projection"]
        self.assertEqual([root["event_id"]], state["branch_points"])
        self.assertEqual(
            sorted([first["event"]["event_id"], second["event"]["event_id"]]),
            state["leaf_event_ids"],
        )

    def test_untyped_legacy_route_event_fails_closed(self):
        root = self.start()["event"]
        legacy = self.request(
            "legacy-route",
            event_type="route_selected",
            parent=root["event_id"],
            subject={"kind": "route", "ref": "content-writer"},
        )
        with self.assertRaisesRegex(runtime.RunEventError, "requires reason_code"):
            runtime.append_event(self.root, self.run_id, legacy)

        legacy["reason_code"] = "fixture"
        with self.assertRaisesRegex(runtime.RunEventError, "dimensions must contain exactly"):
            runtime.append_event(self.root, self.run_id, legacy)
        self.assertEqual(1, len(runtime.load_events(self.root, self.run_id)))

    def test_route_state_uses_only_selected_parent_ancestry(self):
        root = self.start()["event"]
        branch_a = self.select_route(
            key="route-a", parent=root["event_id"], target="skill-a", command="auto",
        )
        branch_b = self.select_route(
            key="route-b", parent=root["event_id"], target="skill-b", command="email",
        )
        self.assertEqual("skill-b", branch_b["projection"]["route_skill"])
        self.assertEqual(["skill-b"], branch_b["projection"]["route_chain"])
        self.assertEqual(0, branch_b["projection"]["automatic_handoff_depth"])

        continued_a = self.select_route(
            key="route-a-auto",
            parent=branch_a["event"]["event_id"],
            target="skill-b",
            command="email",
            transition="automatic-handoff",
        )
        projection = continued_a["projection"]
        self.assertEqual("skill-b", projection["route_skill"])
        self.assertEqual("email", projection["route_command"])
        self.assertEqual("fixture", projection["route_reason_code"])
        self.assertEqual("automatic-handoff", projection["route_transition"])
        self.assertEqual(["skill-a", "skill-b"], projection["route_chain"])
        self.assertEqual(1, projection["automatic_handoff_depth"])

        with self.assertRaisesRegex(runtime.RunEventError, "initial route may appear only once"):
            self.select_route(
                key="route-a-second-initial",
                parent=branch_a["event"]["event_id"],
                target="skill-c",
            )

    def test_route_loop_cap_and_user_reset_are_deterministic(self):
        root = self.start()["event"]
        current = self.select_route(
            key="initial-a", parent=root["event_id"], target="skill-a", command="auto",
        )
        current = self.select_route(
            key="auto-b", parent=current["event"]["event_id"], target="skill-b",
            command="auto", transition="automatic-handoff",
        )
        with self.assertRaisesRegex(runtime.RunEventError, "already visited"):
            self.select_route(
                key="auto-loop", parent=current["event"]["event_id"], target="skill-a",
                command="auto", transition="automatic-handoff",
            )
        for target in ("skill-c", "skill-d"):
            current = self.select_route(
                key="auto-" + target,
                parent=current["event"]["event_id"],
                target=target,
                command="auto",
                transition="automatic-handoff",
            )
        self.assertEqual(3, current["projection"]["automatic_handoff_depth"])
        with self.assertRaisesRegex(runtime.RunEventError, "three-handoff route limit"):
            self.select_route(
                key="auto-overflow", parent=current["event"]["event_id"],
                target="skill-e", command="auto", transition="automatic-handoff",
            )

        reset = self.select_route(
            key="user-reset",
            parent=current["event"]["event_id"],
            target="skill-a",
            command="auto",
            transition="user-reroute",
            actor_type="system",
        )
        self.assertEqual(["skill-a"], reset["projection"]["route_chain"])
        self.assertEqual(0, reset["projection"]["automatic_handoff_depth"])
        after_reset = self.select_route(
            key="auto-after-reset",
            parent=reset["event"]["event_id"],
            target="skill-b",
            command="auto",
            transition="automatic-handoff",
        )
        self.assertEqual(["skill-a", "skill-b"], after_reset["projection"]["route_chain"])
        with self.assertRaisesRegex(runtime.RunEventError, "requires a prior route"):
            self.select_route(
                key="actor-does-not-authorize",
                parent=root["event_id"],
                target="skill-z",
                command="auto",
                transition="user-reroute",
                actor_type="user",
            )

    def test_tampering_truncation_and_hardlinks_fail_closed(self):
        self.start()
        stream, _, _ = runtime.run_paths(self.root, self.run_id)
        line = json.loads(stream.read_text(encoding="utf-8"))
        line["status"] = "failed"
        stream.write_text(json.dumps(line) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(runtime.RunEventError, "status=started|hash mismatch"):
            runtime.load_events(self.root, self.run_id)

        stream.write_text(json.dumps(line), encoding="utf-8")
        with self.assertRaisesRegex(runtime.RunEventError, "truncated"):
            runtime.load_events(self.root, self.run_id)

        self.temp.cleanup()
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run_id = str(uuid.uuid4())
        self.start()
        stream, _, run_dir = runtime.run_paths(self.root, self.run_id)
        os.link(stream, run_dir / "events-alias.ndjson")
        with self.assertRaisesRegex(runtime.RunEventError, "single-link"):
            runtime.load_events(self.root, self.run_id)

    def test_concurrent_appends_have_unique_contiguous_offsets(self):
        root_event = self.start()["event"]

        def append(index):
            return runtime.append_event(
                self.root, self.run_id,
                self.request(
                    "concurrent-%d" % index,
                    parent=root_event["event_id"],
                    subject={"kind": "route", "ref": "route-%d" % index},
                ),
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(append, range(16)))
        events = runtime.load_events(self.root, self.run_id)
        self.assertEqual(list(range(1, 18)), [event["offset"] for event in events])
        self.assertEqual(17, len({event["event_hash"] for event in events}))

    def test_event_limit_is_rejected_before_the_stream_becomes_unverifiable(self):
        with mock.patch.object(runtime, "MAX_EVENTS", 3):
            root_event = self.start()["event"]
            second = runtime.append_event(
                self.root, self.run_id,
                self.request("second", parent=root_event["event_id"]),
            )
            with self.assertRaisesRegex(runtime.RunEventError, "final slot"):
                runtime.append_event(
                    self.root, self.run_id,
                    self.request("overflow", parent=second["event"]["event_id"]),
                )
            self.assertEqual(2, len(runtime.load_events(self.root, self.run_id)))

    def test_final_event_slot_rejects_waiting_but_allows_terminal_envelope(self):
        self.start()
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        event_count = len(runtime.load_events(self.root, self.run_id))
        waiting = self.envelope_value(
            context, None, snapshot["projection"], status="waiting",
        )
        waiting["ended_at"] = None
        waiting["next_action"] = {"code": "capacity-wait"}
        with mock.patch.object(runtime, "MAX_EVENTS", event_count + 1):
            with self.assertRaisesRegex(runtime.RunEventError, "final slot"):
                runtime.finish_run(self.root, self.run_id, waiting)
            terminal = self.envelope_value(context, None, snapshot["projection"])
            finished = runtime.finish_run(self.root, self.run_id, terminal)
        self.assertEqual("succeeded", finished["projection"]["status"])
        self.assertEqual(event_count + 1, finished["event"]["offset"])

    def test_terminal_loop_closure_is_scoped_to_the_selected_ancestry(self):
        self.start()
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        loop_id = str(uuid.uuid4())
        active = self.loop_step_fixture(loop_id, snapshot["event"])
        terminal = self.loop_step_fixture(
            loop_id, active["event"], active,
            transition="deadline-expired", state="exhausted",
            reason_code="deadline-expired",
        )

        sibling = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "sibling-from-active-loop",
                parent=active["event"]["event_id"],
                subject={"kind": "context", "ref": "sibling"},
            ),
        )
        envelope = self.envelope_value(context, None, sibling["projection"])
        with self.assertRaisesRegex(
                runtime.RunEventError, "requires selected audit loops to be terminal"):
            runtime.finish_run(self.root, self.run_id, envelope)

        historical = runtime.verify_loop_event_coverage(
            self.root, self.run_id, loop_id,
            [self.loop_wrapper(active), self.loop_wrapper(terminal)],
        )
        self.assertEqual(
            [active["event"]["event_id"], terminal["event"]["event_id"]],
            historical["event_ids"],
        )

    def test_sibling_only_loop_is_ignored_and_historical_chain_remains_valid(self):
        self.start()
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        loop_id = str(uuid.uuid4())
        active = self.loop_step_fixture(loop_id, snapshot["event"])
        terminal = self.loop_step_fixture(loop_id, active["event"], active)

        selected = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "branch-before-loop",
                parent=snapshot["event"]["event_id"],
                subject={"kind": "context", "ref": "selected-without-loop"},
            ),
        )
        closure = runtime.verify_run_audit_loops(
            self.root, self.run_id, require_terminal=True,
            branch_head_event_id=selected["event"]["event_id"],
        )
        self.assertEqual("none", closure["status"])
        self.assertEqual([], closure["loops"])

        envelope = self.envelope_value(context, None, selected["projection"])
        envelope["loop_closure"] = {
            "scope": "selected-ancestry",
            "selected_head_event_id": active["event"]["event_id"],
            "status": "verified",
            "loops": [],
        }
        finished = runtime.finish_run(self.root, self.run_id, envelope)
        stored = json.loads(
            (self.root / finished["artifact"]["ref"]).read_text(encoding="utf-8")
        )
        self.assertEqual("none", stored["loop_closure"]["status"])
        self.assertEqual(
            selected["event"]["event_id"],
            stored["loop_closure"]["selected_head_event_id"],
        )
        historical = runtime.verify_loop_event_coverage(
            self.root, self.run_id, loop_id,
            [self.loop_wrapper(active), self.loop_wrapper(terminal)],
        )
        self.assertEqual(2, historical["events"])

    def test_failed_finish_persists_bounded_unresolved_loop_evidence(self):
        self.start()
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        loop_id = str(uuid.uuid4())
        active = self.loop_step_fixture(loop_id, snapshot["event"])
        active["path"].unlink()

        state = runtime.project_events(
            self.run_id, runtime.load_events(self.root, self.run_id),
        )
        succeeded = self.envelope_value(context, None, state)
        with self.assertRaisesRegex(runtime.RunEventError, "does not exist"):
            runtime.finish_run(self.root, self.run_id, succeeded)

        failed = self.envelope_value(context, None, state, status="failed")
        failed["failure_class"] = "loop"
        result = runtime.finish_run(self.root, self.run_id, failed)
        stored = json.loads(
            (self.root / result["artifact"]["ref"]).read_text(encoding="utf-8")
        )
        self.assertEqual("run_failed", result["event"]["event_type"])
        self.assertEqual("unresolved", stored["loop_closure"]["status"])
        self.assertEqual("unresolved", stored["loop_closure"]["loops"][0]["validation_status"])
        self.assertEqual("missing-step", stored["loop_closure"]["loops"][0]["failure_code"])
        self.assertEqual(active["ref"], stored["loop_closure"]["loops"][0]["expected_step_ref"])
        self.assertEqual(active["sha256"], stored["loop_closure"]["loops"][0]["expected_step_sha256"])

    def test_failed_and_aborted_runs_can_seal_before_route_or_context(self):
        for status, event_type in (("failed", "run_failed"), ("aborted", "run_aborted")):
            with self.subTest(status=status):
                self.run_id = str(uuid.uuid4())
                started = self.start()
                envelope = self.degraded_envelope_value(
                    started["projection"], status=status,
                )
                claimed_offsets = json.loads(json.dumps(envelope))
                claimed_offsets["registry_offsets"]["claims"] = 0
                with self.assertRaisesRegex(
                        runtime.RunEventError, "unbound null registry offsets"):
                    runtime.finish_run(
                        self.root, self.run_id, claimed_offsets,
                    )
                result = runtime.finish_run(self.root, self.run_id, envelope)
                stored = json.loads(
                    (self.root / result["artifact"]["ref"]).read_text(encoding="utf-8")
                )
                self.assertEqual(event_type, result["event"]["event_type"])
                self.assertIsNone(stored["route"])
                self.assertEqual([], stored["context_manifests"])
                self.assertEqual("none", stored["loop_closure"]["status"])

    def test_loop_closure_uses_shared_step_and_byte_budgets(self):
        started = self.start()
        first_loop = str(uuid.uuid4())
        first = self.loop_step_fixture(first_loop, started["event"])
        second_loop = str(uuid.uuid4())
        second = self.loop_step_fixture(second_loop, first["event"])
        selected_head = second["event"]["event_id"]

        with mock.patch.object(runtime, "MAX_LOOP_CLOSURE_STEPS", 1):
            with self.assertRaisesRegex(runtime.RunEventError, "step budget"):
                runtime.verify_run_audit_loops(
                    self.root, self.run_id, require_terminal=False,
                    branch_head_event_id=selected_head,
                )
            unresolved = runtime.verify_run_audit_loops(
                self.root, self.run_id, require_terminal=False,
                branch_head_event_id=selected_head, allow_unresolved=True,
            )
            self.assertEqual("unresolved", unresolved["status"])
            self.assertEqual(
                ["valid", "unresolved"],
                [item["validation_status"] for item in unresolved["loops"]],
            )
            self.assertEqual("budget-exhausted", unresolved["loops"][1]["failure_code"])

        combined_minus_one = first["path"].stat().st_size + second["path"].stat().st_size - 1
        with mock.patch.object(runtime, "MAX_LOOP_CLOSURE_BYTES", combined_minus_one):
            with self.assertRaisesRegex(runtime.RunEventError, "byte budget"):
                runtime.verify_run_audit_loops(
                    self.root, self.run_id, require_terminal=False,
                    branch_head_event_id=selected_head,
                )

    def test_future_anchor_is_not_public_coverage_but_is_recoverable_internally(self):
        started = self.start()
        loop_id = str(uuid.uuid4())
        first = self.loop_step_fixture(loop_id, started["event"])
        pending = self.loop_step_fixture(
            loop_id, first["event"], first, materialize=False,
        )
        descendant = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "after-pending-loop-anchor",
                parent=pending["event"]["event_id"],
            ),
        )

        with self.assertRaisesRegex(runtime.RunEventError, "unmaterialized or forked"):
            runtime.verify_loop_event_coverage(
                self.root, self.run_id, loop_id, [self.loop_wrapper(first)],
            )
        allowed = runtime.verify_loop_event_coverage(
            self.root, self.run_id, loop_id, [self.loop_wrapper(first)],
            require_selected=True,
            _allowed_unmaterialized_event_id=pending["event"]["event_id"],
        )
        self.assertEqual([first["event"]["event_id"]], allowed["event_ids"])

        with runtime.locked_run_coordinator(self.root, self.run_id):
            recovered = runtime.anchor_loop_step(
                self.root, self.run_id, loop_id, pending["ref"], pending["sha256"],
                pending["document"], _coordinator_locked=True,
            )
            runtime.write_immutable_json(
                self.root, pending["path"], pending["document"],
            )
        self.assertTrue(recovered["deduplicated"])
        self.assertEqual(descendant["event"]["event_id"], runtime.load_events(
            self.root, self.run_id,
        )[-1]["event_id"])
        complete = runtime.verify_loop_event_coverage(
            self.root, self.run_id, loop_id,
            [self.loop_wrapper(first), self.loop_wrapper(pending)],
        )
        self.assertEqual(2, complete["events"])

    def test_complete_snapshot_save_point_and_envelope_lifecycle(self):
        root_event = self.start()["event"]
        turn = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-1-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot_value = self.snapshot_value(context)
        wrong_bytes = json.loads(json.dumps(snapshot_value))
        wrong_bytes["snapshot_id"] = str(uuid.uuid4())
        wrong_bytes["context_manifest"]["bytes"] += 1
        with self.assertRaisesRegex(runtime.RunEventError, "bytes does not match"):
            runtime.write_snapshot(self.root, self.run_id, wrong_bytes)
        snapshot = runtime.write_snapshot(self.root, self.run_id, snapshot_value)
        retry_snapshot = runtime.write_snapshot(self.root, self.run_id, snapshot_value)
        self.assertTrue(retry_snapshot["deduplicated"])
        changed_snapshot = json.loads(json.dumps(snapshot_value))
        changed_snapshot["host"]["model_id"] = "different-model"
        with self.assertRaisesRegex(runtime.RunEventError, "different artifact content"):
            runtime.write_snapshot(self.root, self.run_id, changed_snapshot)
        route_parent = runtime.load_events(self.root, self.run_id)[-2]
        self.assertEqual("route_selected", route_parent["event_type"])
        self.assertEqual(route_parent["event_id"], snapshot["event"]["parent_event_id"])

        state = snapshot["projection"]
        save_value = self.save_point_value(snapshot["artifact"], context, state)
        saved = runtime.write_save_point(self.root, self.run_id, save_value)
        self.assertTrue(runtime.write_save_point(self.root, self.run_id, save_value)["deduplicated"])
        changed_save = json.loads(json.dumps(save_value))
        changed_save["next_action"] = {"code": "different"}
        with self.assertRaisesRegex(runtime.RunEventError, "different artifact content"):
            runtime.write_save_point(self.root, self.run_id, changed_save)
        self.assertEqual(saved["artifact"]["ref"], saved["projection"]["last_save_point_ref"])

        envelope = self.envelope_value(context, saved["artifact"], saved["projection"])
        finished = runtime.finish_run(self.root, self.run_id, envelope)
        self.assertEqual("succeeded", finished["projection"]["status"])
        self.assertTrue(runtime.finish_run(self.root, self.run_id, envelope)["deduplicated"])
        changed_envelope = json.loads(json.dumps(envelope))
        changed_envelope["metrics"]["turns"] = 2
        with self.assertRaisesRegex(runtime.RunEventError, "different artifact content"):
            runtime.finish_run(self.root, self.run_id, changed_envelope)
        self.assertTrue((self.root / finished["artifact"]["ref"]).is_file())
        with self.assertRaisesRegex(runtime.RunEventError, "terminal run"):
            runtime.append_event(
                self.root, self.run_id,
                self.request("too-late", parent=finished["event"]["event_id"]),
            )

    def test_snapshot_binds_live_source_route_contract_offsets_and_private_ref(self):
        root_event = self.start()["event"]
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        source = self.root / "source.md"
        source.write_text("source-v1", encoding="utf-8")
        manifest = self.context_manifest_value(candidates=[{
            "resource_id": "source",
            "scope": "project",
            "path": "source.md",
            "role": "evidence",
            "requirement": "required",
            "authority": "working",
            "observed_at": "2026-07-19T10:00:00Z",
            "max_age_seconds": None,
            "priority": 50,
            "reason_code": "fixture",
            "sensitivity": "internal",
            "expected_sha256": None,
            "conflict_group": None,
            "supersedes": [],
        }])
        context = self.context_reference(manifest)

        source.write_text("source-v2", encoding="utf-8")
        with self.assertRaisesRegex(runtime.RunEventError, "source no longer matches"):
            runtime.write_snapshot(self.root, self.run_id, self.snapshot_value(context))
        source.write_text("source-v1", encoding="utf-8")

        snapshot = self.snapshot_value(context)
        snapshot["skill"]["name"] = "different-skill"
        with self.assertRaisesRegex(runtime.RunEventError, "skill does not match"):
            runtime.write_snapshot(self.root, self.run_id, snapshot)
        snapshot = self.snapshot_value(context)
        snapshot["skill"]["contract_sha256"] = "f" * 64
        with self.assertRaisesRegex(runtime.RunEventError, "contract hash"):
            runtime.write_snapshot(self.root, self.run_id, snapshot)
        snapshot = self.snapshot_value(context)
        snapshot["registry_offsets"]["claims"] = 9
        with self.assertRaisesRegex(runtime.RunEventError, "registry offsets"):
            runtime.write_snapshot(self.root, self.run_id, snapshot)
        snapshot = self.snapshot_value(context)
        snapshot["skill"]["prompt_contract_ref"] = "missing-prompt-contract.json"
        snapshot["skill"]["prompt_contract_sha256"] = "e" * 64
        with self.assertRaisesRegex(runtime.RunEventError, "missing-prompt-contract"):
            runtime.write_snapshot(self.root, self.run_id, snapshot)

        noncanonical = self.write_json("context-manifest.json", manifest)
        noncanonical.chmod(0o600)
        invalid_context = {
            "ref": "context-manifest.json",
            "sha256": self.digest(noncanonical),
            "context_signature": manifest["context_signature"],
        }
        with self.assertRaisesRegex(runtime.RunEventError, "canonical private"):
            runtime.write_snapshot(
                self.root, self.run_id, self.snapshot_value(invalid_context),
            )

    def test_snapshot_binds_context_to_latest_typed_route_event(self):
        root = self.start()["event"]
        self.select_route(
            key="route-command-mismatch",
            parent=root["event_id"],
            target="content-writer",
            command="auto",
            reason_code="fixture",
        )
        context = self.context_reference()
        with self.assertRaisesRegex(runtime.RunEventError, "latest typed route event"):
            runtime.write_snapshot(
                self.root, self.run_id, self.snapshot_value(context),
            )

    def test_save_point_uses_exact_route_chain_and_pending_handoff_is_inert(self):
        root = self.start()["event"]
        initial = self.select_route(
            key="route-content",
            parent=root["event_id"],
            target="content-writer",
            command="seo-geo",
        )
        automatic = self.select_route(
            key="route-auditor",
            parent=initial["event"]["event_id"],
            target="content-quality-auditor",
            command="seo-geo",
            transition="automatic-handoff",
        )
        context = self.context_reference(
            self.context_manifest_value(target_skill="content-quality-auditor")
        )
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        wrong = self.save_point_value(
            snapshot["artifact"], context, snapshot["projection"],
        )
        wrong["visited_skills"] = ["invented-skill", "content-quality-auditor"]
        with self.assertRaisesRegex(runtime.RunEventError, "exactly match"):
            runtime.write_save_point(self.root, self.run_id, wrong)

        value = self.save_point_value(
            snapshot["artifact"], context, snapshot["projection"],
        )
        value["pending_handoff"] = {
            "status": "proposed",
            "objective_code": "continue-review",
            "recommended_skill": "another-skill",
        }
        saved = runtime.write_save_point(self.root, self.run_id, value)
        self.assertEqual(
            ["content-writer", "content-quality-auditor"],
            saved["projection"]["route_chain"],
        )
        self.assertEqual(1, saved["projection"]["automatic_handoff_depth"])
        self.assertEqual(automatic["projection"]["route_chain"], saved["projection"]["route_chain"])

    def test_envelope_rejects_route_selected_after_terminal_snapshot(self):
        self.start()
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        rerouted = self.select_route(
            key="late-user-reroute",
            parent=snapshot["event"]["event_id"],
            target="content-quality-auditor",
            command="seo-geo",
            reason_code="late-reroute",
            transition="user-reroute",
        )
        envelope = self.envelope_value(context, None, rerouted["projection"])
        with self.assertRaisesRegex(runtime.RunEventError, "latest typed route event"):
            runtime.finish_run(self.root, self.run_id, envelope)

    def test_save_point_and_envelope_bind_branch_context_and_offsets(self):
        root_event = self.start()["event"]
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(self.root, self.run_id, self.snapshot_value(context))

        bad_save = self.save_point_value(snapshot["artifact"], context, snapshot["projection"])
        bad_save["registry_offsets"]["claims"] = 99
        with self.assertRaisesRegex(runtime.RunEventError, "save point registry offsets"):
            runtime.write_save_point(self.root, self.run_id, bad_save)
        bad_save = self.save_point_value(snapshot["artifact"], context, snapshot["projection"])
        bad_save["visited_skills"] = ["invented-skill"]
        with self.assertRaisesRegex(runtime.RunEventError, "exactly match the selected typed route chain"):
            runtime.write_save_point(self.root, self.run_id, bad_save)

        no_snapshot_root = tempfile.TemporaryDirectory()
        self.addCleanup(no_snapshot_root.cleanup)
        no_snapshot_path = Path(no_snapshot_root.name)
        other_run = str(uuid.uuid4())
        old_root, old_run = self.root, self.run_id
        self.root, self.run_id = no_snapshot_path, other_run
        try:
            started = self.start()
            bare_context = self.context_reference()
            live_state = runtime.project_events(
                self.run_id, runtime.load_events(self.root, self.run_id),
            )
            envelope = self.envelope_value(bare_context, None, live_state)
            with self.assertRaisesRegex(runtime.RunEventError, "ancestor turn snapshot"):
                runtime.finish_run(self.root, self.run_id, envelope)
        finally:
            self.root, self.run_id = old_root, old_run

        envelope = self.envelope_value(context, None, snapshot["projection"])
        envelope["route"]["reason_code"] = "invented-route"
        with self.assertRaisesRegex(runtime.RunEventError, "route does not match"):
            runtime.finish_run(self.root, self.run_id, envelope)
        envelope = self.envelope_value(context, None, snapshot["projection"])
        envelope["registry_offsets"]["claims"] = 1
        with self.assertRaisesRegex(runtime.RunEventError, "registry offsets"):
            runtime.finish_run(self.root, self.run_id, envelope)

    def test_snapshot_parent_turn_follows_selected_event_branch(self):
        root = self.start()["event"]
        first_turn = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-1", event_type="turn_started", parent=root["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        first_context = self.context_reference()
        first_snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(first_context),
        )
        first_route = runtime.load_events(self.root, self.run_id)[-2]
        self.assertEqual("route_selected", first_route["event_type"])
        self.assertEqual(first_route["event_id"], first_snapshot["event"]["parent_event_id"])

        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-2", event_type="turn_started",
                parent=first_snapshot["event"]["event_id"], turn_id="turn-2", status="started",
                subject={"kind": "turn", "ref": "turn-2"},
            ),
        )
        second_context = self.context_reference(self.context_manifest_value(turn_id="turn-2"))
        second = self.snapshot_value(second_context, turn_id="turn-2")
        second["parent_turn_id"] = "invented-turn"
        with self.assertRaisesRegex(runtime.RunEventError, "selected-branch parent turn"):
            runtime.write_snapshot(self.root, self.run_id, second)

        sibling = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-sibling", event_type="turn_started", parent=root["event_id"],
                turn_id="turn-sibling", status="started",
                subject={"kind": "turn", "ref": "turn-sibling"},
            ),
        )
        sibling_context = self.context_reference(
            self.context_manifest_value(turn_id="turn-sibling")
        )
        sibling_snapshot = self.snapshot_value(sibling_context, turn_id="turn-sibling")
        sibling_snapshot["parent_turn_id"] = "turn-1"
        with self.assertRaisesRegex(runtime.RunEventError, "selected-branch parent turn"):
            runtime.write_snapshot(self.root, self.run_id, sibling_snapshot)
        self.assertEqual(root["event_id"], sibling["event"]["parent_event_id"])

    def test_repeated_same_skill_turns_do_not_consume_handoff_depth(self):
        self.start()
        previous_turn = None
        latest_context = latest_snapshot = None
        for index in range(1, 6):
            turn_id = "turn-%d" % index
            latest_context = self.context_reference(
                self.context_manifest_value(turn_id=turn_id)
            )
            snapshot_value = self.snapshot_value(latest_context, turn_id=turn_id)
            snapshot_value["parent_turn_id"] = previous_turn
            latest_snapshot = runtime.write_snapshot(
                self.root, self.run_id, snapshot_value,
            )
            previous_turn = turn_id
        save = self.save_point_value(
            latest_snapshot["artifact"], latest_context, latest_snapshot["projection"],
        )
        save["turn_id"] = "turn-5"
        save["visited_skills"] = ["content-writer"]
        save["chain_depth"] = 0
        result = runtime.write_save_point(self.root, self.run_id, save)
        self.assertEqual("save_point_created", result["event"]["event_type"])

    def test_save_point_refuses_unfinished_tool_and_stale_head(self):
        root_event = self.start()["event"]
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(self.root, self.run_id, self.snapshot_value(context))
        tool = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "tool-open", event_type="tool_allowed", parent=snapshot["event"]["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "tool", "ref": "tool-1"},
            ),
        )
        save_value = self.save_point_value(snapshot["artifact"], context, tool["projection"])
        with self.assertRaisesRegex(runtime.RunEventError, "unfinished tool"):
            runtime.write_save_point(self.root, self.run_id, save_value)

        save_value["last_event_offset"] -= 1
        with self.assertRaisesRegex(runtime.RunEventError, "offset/hash"):
            runtime.write_save_point(self.root, self.run_id, save_value)

    def test_repeated_waiting_envelopes_are_distinct_and_projected(self):
        started = self.start()
        turn = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started",
                parent=started["event"]["event_id"], turn_id="turn-1", status="started",
                subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        self.assertEqual(
            "route_selected",
            runtime.load_events(self.root, self.run_id)[-2]["event_type"],
        )
        first_value = self.envelope_value(
            context, None, snapshot["projection"], status="waiting",
        )
        first_value["ended_at"] = None
        first_value["next_action"] = {"code": "readback", "not_before": "2026-07-20T10:00:00Z"}
        first = runtime.finish_run(self.root, self.run_id, first_value)
        self.assertEqual("waiting", first["projection"]["status"])
        self.assertEqual(first["artifact"]["ref"], first["projection"]["run_envelope_ref"])

        resumed = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "resume-after-wait", parent=first["event"]["event_id"],
                subject={"kind": "route", "ref": "resume"},
            ),
        )
        second_value = self.envelope_value(context, None, resumed["projection"], status="waiting")
        second_value["ended_at"] = None
        second_value["next_action"] = {"code": "second-readback"}
        second = runtime.finish_run(self.root, self.run_id, second_value)
        self.assertFalse(second["deduplicated"])
        self.assertNotEqual(first["event"]["idempotency_key"], second["event"]["idempotency_key"])
        self.assertEqual(second["artifact"]["ref"], second["projection"]["run_envelope_ref"])

    def test_generic_append_cannot_claim_reserved_artifacts_or_terminal_state(self):
        root_event = self.start()["event"]
        reserved = self.request("snapshot:forged", parent=root_event["event_id"])
        with self.assertRaisesRegex(runtime.RunEventError, "prefix is reserved"):
            runtime.append_event(self.root, self.run_id, reserved)

        forged = self.request(
            "forged-terminal", event_type="run_finished", parent=root_event["event_id"],
            turn_id=None, status="succeeded", subject={"kind": "run", "ref": self.run_id},
            references=[{
                "kind": "run-envelope",
                "ref": "memory/runs/%s/envelopes/%s.json" % (
                    self.run_id, root_event["event_id"],
                ),
                "sha256": "a" * 64,
            }],
        )
        with self.assertRaisesRegex(runtime.RunEventError, "reserved for its typed runtime command"):
            runtime.append_event(self.root, self.run_id, forged)

        loop_id = str(uuid.uuid4())
        forged_loop = self.request(
            "forged-loop", event_type="loop_state_changed",
            parent=root_event["event_id"], turn_id=None, status="succeeded",
            subject={"kind": "loop", "ref": loop_id},
            reason_code="forged-loop-state",
            references=[{
                "kind": "loop",
                "ref": "memory/runs/%s/loops/%s/001-start.json"
                % (self.run_id, loop_id),
                "sha256": "b" * 64,
            }],
            metrics={"sequence": 1, "cycle": 1, "total_retries": 0},
            dimensions={"loop_state": "awaiting-proposal"},
        )
        with self.assertRaisesRegex(runtime.RunEventError, "reserved for its typed runtime command"):
            runtime.append_event(self.root, self.run_id, forged_loop)

        invalid = dict(forged)
        invalid["status"] = "failed"
        with self.assertRaisesRegex(runtime.RunEventError, "status=succeeded"):
            runtime.validate_event_request(invalid)

    def test_save_point_parses_and_binds_typed_references(self):
        root_event = self.start()["event"]
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(self.root, self.run_id, self.snapshot_value(context))
        bogus = self.write_json("bogus-snapshot.json", {"schema_version": "1.0", "run_id": self.run_id})
        with self.assertRaisesRegex(runtime.RunEventError, "turn snapshot.*missing fields"):
            runtime.validate_snapshot_document(
                runtime.normalized_root(self.root), "bogus-snapshot.json",
                self.digest(bogus), self.run_id, "turn-1",
            )
        value = self.save_point_value(
            {"ref": "bogus-snapshot.json", "sha256": self.digest(bogus)},
            context, snapshot["projection"],
        )
        with self.assertRaisesRegex(runtime.RunEventError, "latest turn snapshot"):
            runtime.write_save_point(self.root, self.run_id, value)

        wrong_value = self.context_manifest_value(run_id=str(uuid.uuid4()))
        wrong_context_path = self.write_json("wrong-context.json", wrong_value)
        snapshot_value = self.snapshot_value({
            "ref": "wrong-context.json", "sha256": self.digest(wrong_context_path),
            "context_signature": wrong_value["context_signature"],
        }, snapshot_id=str(uuid.uuid4()))
        with self.assertRaisesRegex(runtime.RunEventError, "does not belong to this run"):
            runtime.write_snapshot(self.root, self.run_id, snapshot_value)

    def test_successful_finish_refuses_open_tool_on_selected_branch(self):
        root_event = self.start()["event"]
        tool = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "open-tool", event_type="tool_allowed", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "tool", "ref": "tool-1"},
            ),
        )
        context = self.context_reference()
        live_state = runtime.project_events(
            self.run_id, runtime.load_events(self.root, self.run_id),
        )
        envelope = self.envelope_value(context, None, live_state)
        with self.assertRaisesRegex(runtime.RunEventError, "unfinished tool"):
            runtime.finish_run(self.root, self.run_id, envelope)

    def test_run_envelope_rejects_mutable_runtime_artifacts(self):
        started = self.start()
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started",
                parent=started["event"]["event_id"], turn_id="turn-1", status="started",
                subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(
            self.root, self.run_id, self.snapshot_value(context),
        )
        stream, _, _ = runtime.run_paths(self.root, self.run_id)
        envelope = self.envelope_value(context, None, snapshot["projection"])
        envelope["artifacts"] = [{
            "ref": "memory/runs/%s/events.ndjson" % self.run_id,
            "sha256": self.digest(stream),
        }]
        with self.assertRaisesRegex(runtime.RunEventError, "mutable runtime files"):
            runtime.finish_run(self.root, self.run_id, envelope)

    def test_tool_close_requires_matching_open_ancestor_on_the_same_turn(self):
        root_event = self.start()["event"]
        with self.assertRaisesRegex(runtime.RunEventError, "matching open tool ancestor"):
            runtime.append_event(
                self.root, self.run_id,
                self.request(
                    "forged-close", event_type="tool_finished", parent=root_event["event_id"],
                    turn_id="turn-1", status="succeeded",
                    subject={"kind": "tool", "ref": "tool-1"},
                ),
            )
        opened = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "tool-open", event_type="tool_requested", parent=root_event["event_id"],
                turn_id="turn-1", status="started",
                subject={"kind": "tool", "ref": "tool-1"},
            ),
        )
        with self.assertRaisesRegex(runtime.RunEventError, "cannot be reused across turns"):
            runtime.append_event(
                self.root, self.run_id,
                self.request(
                    "cross-turn-reuse", event_type="tool_requested",
                    parent=opened["event"]["event_id"], turn_id="turn-2", status="started",
                    subject={"kind": "tool", "ref": "tool-1"},
                ),
            )
        with self.assertRaisesRegex(runtime.RunEventError, "cannot be reused across turns"):
            runtime.append_event(
                self.root, self.run_id,
                self.request(
                    "wrong-turn-close", event_type="tool_finished",
                    parent=opened["event"]["event_id"], turn_id="turn-2", status="failed",
                    subject={"kind": "tool", "ref": "tool-1"},
                ),
            )
        closed = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "legal-close", event_type="tool_finished",
                parent=opened["event"]["event_id"], turn_id="turn-1", status="succeeded",
                subject={"kind": "tool", "ref": "tool-1"},
            ),
        )
        self.assertEqual([], closed["projection"]["open_tool_refs"])

    def test_claimed_artifact_validation_requires_ancestor_evidence(self):
        root_event = self.start()["event"]
        runtime.append_event(
            self.root, self.run_id,
            self.request(
                "turn-start", event_type="turn_started", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "turn", "ref": "turn-1"},
            ),
        )
        context = self.context_reference()
        snapshot = runtime.write_snapshot(self.root, self.run_id, self.snapshot_value(context))
        artifact = self.root / "artifact.txt"
        artifact.write_text("bounded fixture\n", encoding="utf-8")
        reference = {
            "ref": "artifact.txt",
            "sha256": self.digest(artifact),
            "validator": "fixture-validator",
            "validation_status": "valid",
        }
        unsupported = self.save_point_value(snapshot["artifact"], context, snapshot["projection"])
        unsupported["artifacts"] = [reference]
        with self.assertRaisesRegex(runtime.RunEventError, "lacks a matching ancestor"):
            runtime.write_save_point(self.root, self.run_id, unsupported)

        validated = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "artifact-valid", event_type="artifact_validated",
                parent=snapshot["event"]["event_id"], turn_id="turn-1",
                status="succeeded", subject={"kind": "artifact", "ref": "artifact-1"},
                references=[{
                    "kind": "artifact", "ref": "artifact.txt", "sha256": self.digest(artifact),
                }],
                dimensions={"validator": "fixture-validator"},
            ),
        )
        supported = self.save_point_value(snapshot["artifact"], context, validated["projection"])
        supported["artifacts"] = [reference]
        saved = runtime.write_save_point(self.root, self.run_id, supported)
        self.assertEqual("save_point_created", saved["event"]["event_type"])

    def test_open_tools_are_projected_along_the_selected_branch_only(self):
        root_event = self.start()["event"]
        tool = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "branch-tool", event_type="tool_allowed", parent=root_event["event_id"],
                turn_id="turn-1", status="started", subject={"kind": "tool", "ref": "tool-1"},
            ),
        )
        sibling = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "sibling", parent=root_event["event_id"],
                subject={"kind": "route", "ref": "sibling"},
            ),
        )
        self.assertEqual([], sibling["projection"]["open_tool_refs"])
        back_to_tool_branch = runtime.append_event(
            self.root, self.run_id,
            self.request(
                "tool-branch-continues", parent=tool["event"]["event_id"],
                subject={"kind": "route", "ref": "tool-branch"},
            ),
        )
        self.assertEqual(["tool-1"], back_to_tool_branch["projection"]["open_tool_refs"])

    def test_hook_recording_is_opt_in_stable_and_metadata_only(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                {"recorded": False, "reason": "inactive"},
                runtime.record_hook(self.root, "pre-tool-use", {"prompt": "do not store me"}),
            )
        self.assertFalse((self.root / "memory").exists())

        self.start()
        payload = {
            "tool_use_id": "raw-tool-identifier",
            "tool_name": "Bash",
            "prompt": "customer@example.com secret-value",
            "tool_input": {"command": "echo secret-value"},
        }
        environment = {"AARON_ACTIVE_RUN_ID": self.run_id, "AARON_ACTIVE_TURN_ID": "turn-1"}
        with mock.patch.dict(os.environ, environment, clear=True):
            first = runtime.record_hook(self.root, "pre-tool-use", payload)
            second = runtime.record_hook(self.root, "pre-tool-use", payload)
        self.assertTrue(first["recorded"])
        self.assertTrue(second["deduplicated"])
        stream, _, _ = runtime.run_paths(self.root, self.run_id)
        stored = stream.read_text(encoding="utf-8")
        self.assertNotIn("customer@example.com", stored)
        self.assertNotIn("secret-value", stored)
        self.assertNotIn("raw-tool-identifier", stored)
        self.assertNotIn("turn-1", stored)
        self.assertNotEqual(
            runtime.hashed_identifier("same-host-id", self.run_id),
            runtime.hashed_identifier("same-host-id", str(uuid.uuid4())),
        )

    def test_hook_for_unknown_run_does_not_create_runtime_state(self):
        environment = {
            "AARON_ACTIVE_RUN_ID": self.run_id,
            "AARON_ACTIVE_TURN_ID": "raw-turn-id",
        }
        with mock.patch.dict(os.environ, environment, clear=True):
            result = runtime.record_hook(
                self.root, "pre-tool-use", {"tool_use_id": "raw-tool-id", "tool_name": "Read"},
            )
        self.assertEqual({"recorded": False, "reason": "run-not-active"}, result)
        self.assertFalse((self.root / "memory").exists())

    def test_concurrent_hook_events_extend_one_current_head_branch(self):
        self.start()
        processes = []
        for index in range(6):
            environment = dict(os.environ)
            environment.update({
                "AARON_ACTIVE_RUN_ID": self.run_id,
                "AARON_ACTIVE_TURN_ID": "raw-turn-id",
            })
            processes.append((
                subprocess.Popen(
                    [
                        os.environ.get("PYTHON", "python3"),
                        str(ROOT / "scripts" / "run-events.py"),
                        "--root", str(self.root), "record-hook", "pre-tool-use", "-",
                    ],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True, env=environment,
                ),
                json.dumps({"tool_use_id": "raw-tool-%d" % index, "tool_name": "Read"}),
            ))
        results = []
        for process, payload in processes:
            stdout, stderr = process.communicate(payload, timeout=20)
            results.append((stdout, stderr, process.returncode))
        self.assertTrue(all(code == 0 for _, _, code in results), results)
        state = runtime.project_events(self.run_id, runtime.load_events(self.root, self.run_id))
        self.assertEqual(6, len(state["open_tool_refs"]))
        self.assertEqual(7, len(state["selected_path_event_ids"]))

    def test_resume_is_bounded_read_only_and_marks_evidence_untrusted(self):
        self.start()
        stream, projection, run_dir = runtime.run_paths(self.root, self.run_id)
        before = {path: path.stat().st_mtime_ns for path in run_dir.iterdir()}
        summary = runtime.resume_summary(self.root, self.run_id, 1024)
        after = {path: path.stat().st_mtime_ns for path in run_dir.iterdir()}
        self.assertEqual(before, after)
        self.assertFalse(summary["authoritative"])
        self.assertLessEqual(len((runtime.canonical_json(summary) + "\n").encode("utf-8")), 1024)
        self.assertTrue(stream.is_file())
        self.assertTrue(projection.is_file())

        completed = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"), str(ROOT / "scripts" / "run-events.py"),
                "--root", str(self.root), "resume", self.run_id, "--max-bytes", "700",
            ],
            check=True, capture_output=True,
        )
        self.assertLessEqual(len(completed.stdout), 700)
        self.assertEqual(self.run_id, json.loads(completed.stdout)["run_id"])

    def test_git_unignored_and_symlinked_runtime_paths_are_rejected(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        with self.assertRaisesRegex(runtime.RunEventError, "not Git-ignored"):
            self.start()
        self.assertFalse((self.root / "memory").exists())

        (self.root / ".gitignore").write_text("memory/**\n", encoding="utf-8")
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / "memory").mkdir()
        (self.root / "memory" / "runs").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(runtime.RunEventError, "not Git-ignored|runtime path|secure runtime directory"):
            self.start()

    def test_fifo_request_is_rejected_without_blocking(self):
        fifo = self.root / "request.fifo"
        os.mkfifo(fifo)
        completed = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"), str(ROOT / "scripts/run-events.py"),
                "--root", str(self.root), "start", str(fifo),
            ],
            capture_output=True, text=True, timeout=3,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("regular file", completed.stderr)

    def test_stream_directory_entry_swap_is_detected_after_lock(self):
        self.start()
        stream, _, run_dir = runtime.run_paths(self.root, self.run_id)
        with self.assertRaisesRegex(runtime.RunEventError, "changed during operation"):
            with runtime.locked_stream(stream, exclusive=True) as handle:
                original = run_dir / "events-original.ndjson"
                stream.rename(original)
                stream.write_text("", encoding="utf-8")
                handle.seek(0, os.SEEK_END)

    def test_stream_fifo_is_rejected_without_blocking(self):
        run_dir = self.root / "memory" / "runs" / self.run_id
        run_dir.mkdir(parents=True)
        os.mkfifo(run_dir / "events.ndjson")
        completed = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"), str(ROOT / "scripts/run-events.py"),
                "--root", str(self.root), "verify", self.run_id,
            ],
            capture_output=True, text=True, timeout=3,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("single-link regular file", completed.stderr)

    def test_missing_reference_closes_directory_anchor(self):
        descriptor = os.open(self.root, os.O_RDONLY)
        identity = (os.fstat(descriptor).st_dev, os.fstat(descriptor).st_ino)
        with mock.patch.object(runtime, "open_directory_anchor", return_value=(descriptor, identity)), \
                mock.patch.object(
                    runtime, "anchored_lstat",
                    side_effect=runtime.RunEventError("missing fixture"),
                ):
            with self.assertRaisesRegex(runtime.RunEventError, "missing fixture"):
                with runtime.anchored_regular_file(self.root / "missing.json"):
                    pass
        with self.assertRaises(OSError):
            os.fstat(descriptor)

    def test_project_references_reject_intermediate_symlinks_and_oversized_files(self):
        with tempfile.TemporaryDirectory() as outside_name:
            outside = Path(outside_name)
            secret = outside / "nested" / "secret.txt"
            secret.parent.mkdir()
            secret.write_text("outside", encoding="utf-8")
            (self.root / "alias").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(runtime.RunEventError, "real directory|unsafe"):
                runtime.resolve_project_reference(
                    self.root, "alias/nested/secret.txt", self.digest(secret),
                )

        oversized = self.root / "oversized.bin"
        with oversized.open("wb") as handle:
            handle.truncate(runtime.MAX_REFERENCE_BYTES + 1)
        with self.assertRaisesRegex(runtime.RunEventError, "exceeds"):
            runtime.resolve_project_reference(
                self.root, "oversized.bin", "0" * 64,
            )

    def test_snapshot_capacity_preserves_a_finishable_envelope(self):
        events = [{"event_type": "turn_snapshot_created"}] * (runtime.MAX_CONTEXT_MANIFESTS - 1)
        self.assertEqual(runtime.MAX_CONTEXT_MANIFESTS - 1, runtime.ensure_snapshot_capacity(events))
        events.append({"event_type": "turn_snapshot_created"})
        with self.assertRaisesRegex(runtime.RunEventError, "start a child run"):
            runtime.ensure_snapshot_capacity(events)

    def test_immutable_link_install_crash_residue_is_recovered(self):
        self.start()
        root = runtime.normalized_root(self.root)
        _, _, run_dir = runtime.run_paths(root, self.run_id)
        target_dir = runtime.ensure_child_directories(root, run_dir, ["save-points"])
        target = target_dir / "recovery.json"
        runtime.atomic_create_json(root, target, {"fixture": True})
        temporary = target_dir / (".%s.run-create" % target.name)
        os.link(target, temporary)
        self.assertEqual(2, target.stat().st_nlink)
        runtime.recover_immutable_install(target)
        self.assertFalse(temporary.exists())
        self.assertEqual(1, target.stat().st_nlink)
        self.assertEqual(runtime.sha256_file(target), runtime.write_immutable_json(root, target, {"fixture": True}))

        target.chmod(0o400)
        with self.assertRaisesRegex(runtime.RunEventError, "private file mode 0600"):
            runtime.write_immutable_json(root, target, {"fixture": True})

    def test_immutable_final_read_binds_content_mode_and_returned_hash(self):
        self.start()
        root = runtime.normalized_root(self.root)
        _, _, run_dir = runtime.run_paths(root, self.run_id)
        target_dir = runtime.ensure_child_directories(root, run_dir, ["save-points"])
        target = target_dir / "binding.json"
        proposed = {"fixture": "proposed"}
        runtime.atomic_create_json(root, target, proposed)
        attacker_raw = b'{"fixture":"swapped"}\n'
        metadata = target.stat()
        with mock.patch.object(
                runtime, "_stable_project_read",
                return_value=(target, attacker_raw, metadata)):
            with self.assertRaisesRegex(runtime.RunEventError, "different content"):
                runtime.write_immutable_json(root, target, proposed)

        expected_raw = target.read_bytes()
        digest = runtime.write_immutable_json(root, target, proposed)
        self.assertEqual(hashlib.sha256(expected_raw).hexdigest(), digest)

    def test_oversized_immutable_document_is_rejected_before_install(self):
        self.start()
        root = runtime.normalized_root(self.root)
        _, _, run_dir = runtime.run_paths(root, self.run_id)
        target_dir = runtime.ensure_child_directories(root, run_dir, ["save-points"])
        target = target_dir / "oversized.json"
        with self.assertRaisesRegex(runtime.RunEventError, "exceeds"):
            runtime.write_immutable_json(
                root, target, {"payload": "x" * runtime.MAX_DOCUMENT_BYTES},
            )
        self.assertFalse(target.exists())
        self.assertFalse((target_dir / ".oversized.json.run-create").exists())

    def test_read_only_stream_operations_require_exact_private_mode(self):
        self.start()
        stream, _projection, _run_dir = runtime.run_paths(self.root, self.run_id)
        stream.chmod(0o644)
        with self.assertRaisesRegex(runtime.RunEventError, "private file mode 0600"):
            runtime.load_events(self.root, self.run_id)

    def test_multiprocess_appends_keep_one_hash_chain(self):
        root_event = self.start()["event"]
        processes = []
        for index in range(6):
            request_path = self.write_json(
                "requests/%d.json" % index,
                self.request(
                    "process-%d" % index, parent=root_event["event_id"],
                    subject={"kind": "route", "ref": "process-%d" % index},
                ),
            )
            processes.append(subprocess.Popen(
                [
                    os.environ.get("PYTHON", "python3"), str(ROOT / "scripts" / "run-events.py"),
                    "--root", str(self.root), "append", self.run_id, str(request_path),
                ],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            ))
        results = [process.communicate(timeout=20) + (process.returncode,) for process in processes]
        self.assertTrue(all(returncode == 0 for _, _, returncode in results), results)
        events = runtime.load_events(self.root, self.run_id)
        self.assertEqual(7, len(events))
        self.assertEqual(list(range(1, 8)), [event["offset"] for event in events])

    def test_existing_run_append_waits_for_per_run_coordinator(self):
        root_event = self.start()["event"]
        started = threading.Event()

        def append_after_signal():
            started.set()
            return runtime.append_event(
                self.root, self.run_id,
                self.request("coordinated", parent=root_event["event_id"]),
            )

        with ThreadPoolExecutor(max_workers=1) as executor:
            with runtime.locked_run_coordinator(self.root, self.run_id):
                future = executor.submit(append_after_signal)
                self.assertTrue(started.wait(timeout=2))
                with self.assertRaises(TimeoutError):
                    future.result(timeout=0.1)
            result = future.result(timeout=5)
        self.assertEqual("coordinated", result["event"]["idempotency_key"])
        self.assertEqual(2, result["event"]["offset"])

    def test_validators_reject_implicit_offsets_raw_metadata_and_pseudo_token_counts(self):
        context = self.context_reference()
        snapshot = self.snapshot_value(context)
        snapshot["registry_offsets"].pop("claims")
        with self.assertRaisesRegex(runtime.RunEventError, "missing fields"):
            runtime.validate_snapshot(snapshot)

        snapshot = self.snapshot_value(context)
        snapshot["context_manifest"]["token_estimate"] = 123
        with self.assertRaisesRegex(runtime.RunEventError, "estimator"):
            runtime.validate_snapshot(snapshot)

        root_event = self.start()["event"]
        request = self.request("raw", parent=root_event["event_id"])
        request["dimensions"] = {"prompt_text": "secret"}
        with self.assertRaisesRegex(runtime.RunEventError, "allowlist"):
            runtime.append_event(self.root, self.run_id, request)

        request = self.request("absolute", parent=root_event["event_id"])
        request["references"] = [{"kind": "source", "ref": "/tmp/private"}]
        with self.assertRaisesRegex(runtime.RunEventError, "absolute"):
            runtime.append_event(self.root, self.run_id, request)

    def test_hostile_enum_uuid_and_datetime_inputs_fail_closed(self):
        request = self.request("malformed", event_type={})
        with self.assertRaisesRegex(runtime.RunEventError, "event_type"):
            runtime.validate_event_request(request)

        context = self.context_reference()
        snapshot = self.snapshot_value(context)
        snapshot["tools"][0]["mode"] = {}
        with self.assertRaisesRegex(runtime.RunEventError, r"tools\[0\]\.mode"):
            runtime.validate_snapshot(snapshot)

        request_path = self.write_json("malformed-event.json", request)
        completed = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"), str(ROOT / "scripts/run-events.py"),
                "--root", str(self.root), "start", str(request_path),
            ],
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)

        huge_metric = self.request("huge-metric")
        huge_metric["metrics"] = {"huge": 10 ** 400}
        with self.assertRaisesRegex(runtime.RunEventError, "finite numeric metadata"):
            runtime.validate_event_request(huge_metric)
        huge_path = self.write_json("huge-metric.json", huge_metric)
        completed = subprocess.run(
            [
                os.environ.get("PYTHON", "python3"), str(ROOT / "scripts" / "run-events.py"),
                "--root", str(self.root), "start", str(huge_path),
            ],
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(1, completed.returncode)
        self.assertNotIn("Traceback", completed.stderr)
        self.assertIn("finite numeric metadata", completed.stderr)
        with self.assertRaisesRegex(runtime.RunEventError, "RFC UUID"):
            runtime.validate_uuid("00000000-0000-4000-0000-000000000000", "uuid")
        runtime.validate_uuid("01890f3e-7b2d-7cc0-98c4-dc0c0c07398f", "uuid-v7")
        with self.assertRaisesRegex(runtime.RunEventError, "RFC 3339"):
            runtime.parse_datetime("2026-07-19 10:00:00+00:00", "timestamp")

    def test_schema_contracts_are_strict_and_match_runtime_enums(self):
        event_schema = json.loads((ROOT / "references" / "run-event.schema.json").read_text())
        self.assertEqual(runtime.EVENT_TYPES, set(event_schema["properties"]["event_type"]["enum"]))
        route_clause = next(
            clause for clause in event_schema["allOf"]
            if clause["if"]["properties"]["event_type"].get("const") == "route_selected"
        )["then"]
        self.assertIn("reason_code", route_clause["required"])
        route_dimensions = route_clause["properties"]["dimensions"]
        self.assertFalse(route_dimensions["additionalProperties"])
        self.assertEqual(
            {"route_transition", "route_command"},
            set(route_dimensions["required"]),
        )
        self.assertEqual(
            runtime.ROUTE_TRANSITIONS,
            set(route_dimensions["properties"]["route_transition"]["enum"]),
        )
        loop_clause = next(
            clause for clause in event_schema["allOf"]
            if clause["if"]["properties"]["event_type"].get("const")
            == "loop_state_changed"
        )["then"]
        self.assertIn("reason_code", loop_clause["required"])
        loop_dimensions = loop_clause["properties"]["dimensions"]
        self.assertFalse(loop_dimensions["additionalProperties"])
        self.assertEqual(
            runtime.LOOP_STATES,
            set(loop_dimensions["properties"]["loop_state"]["enum"]),
        )
        loop_metrics = loop_clause["properties"]["metrics"]
        self.assertEqual(
            {"sequence", "cycle", "total_retries"}, set(loop_metrics["required"]),
        )
        self.assertEqual(128, loop_metrics["properties"]["total_retries"]["maximum"])
        self.assertIn("loop_state_changed", runtime.INTERNAL_EVENT_TYPES)
        reference_pattern = event_schema["$defs"]["reference"]["properties"]["ref"]["pattern"]
        self.assertIsNone(re.fullmatch(reference_pattern, "artifact/"))
        self.assertIsNone(re.fullmatch(reference_pattern, "artifact/../secret"))
        self.assertIsNotNone(re.fullmatch(reference_pattern, "artifact/result.json"))
        self.assertIn("semantic constraints", event_schema["description"])
        for name in ("turn-snapshot", "save-point", "run-envelope"):
            schema = json.loads((ROOT / "references" / (name + ".schema.json")).read_text())
            offsets = schema["$defs"]["offsets"]
            self.assertFalse(offsets["additionalProperties"])
            self.assertEqual(runtime.REGISTRIES, set(offsets["required"]))
        snapshot_schema = json.loads((ROOT / "references/turn-snapshot.schema.json").read_text())
        snapshot_ref_pattern = snapshot_schema["$defs"]["manifestRef"]["properties"]["ref"]["pattern"]
        snapshot_uuid_pattern = snapshot_schema["properties"]["run_id"]["pattern"]
        self.assertIsNone(re.fullmatch(snapshot_ref_pattern, "artifact/"))
        self.assertIsNone(re.fullmatch(snapshot_uuid_pattern, self.run_id.upper()))
        save_schema = json.loads((ROOT / "references/save-point.schema.json").read_text())
        self.assertEqual(1, save_schema["properties"]["visited_skills"]["minItems"])
        self.assertIn("exactly equal the typed route chain", save_schema["description"])
        envelope_schema = json.loads(
            (ROOT / "references/run-envelope.schema.json").read_text()
        )
        loop_closure = envelope_schema["$defs"]["loopClosure"]
        self.assertFalse(loop_closure["additionalProperties"])
        closure_statuses = {
            clause["if"]["properties"]["status"]["const"]
            for clause in loop_closure["allOf"]
        }
        self.assertEqual({"none", "verified", "unresolved"}, closure_statuses)
        none_clause = next(
            clause for clause in loop_closure["allOf"]
            if clause["if"]["properties"]["status"]["const"] == "none"
        )
        self.assertEqual(
            0, none_clause["then"]["properties"]["loops"]["maxItems"],
        )
        verified_clause = next(
            clause for clause in loop_closure["allOf"]
            if clause["if"]["properties"]["status"]["const"] == "verified"
        )
        self.assertEqual(
            "valid",
            verified_clause["then"]["properties"]["loops"]["items"]
            ["properties"]["validation_status"]["const"],
        )
        unresolved_clause = next(
            clause for clause in loop_closure["allOf"]
            if clause["if"]["properties"]["status"]["const"] == "unresolved"
        )
        self.assertEqual(
            "unresolved",
            unresolved_clause["then"]["properties"]["loops"]["contains"]
            ["properties"]["validation_status"]["const"],
        )
        degraded_clause = next(
            clause for clause in envelope_schema["allOf"]
            if clause["if"]["properties"].get("context_manifests", {}).get("maxItems") == 0
        )
        degraded_offsets = degraded_clause["then"]["properties"]["registry_offsets"]
        self.assertEqual(
            runtime.REGISTRIES,
            set(degraded_offsets["properties"]),
        )
        self.assertTrue(all(
            rule == {"type": "null"}
            for rule in degraded_offsets["properties"].values()
        ))


if __name__ == "__main__":
    unittest.main()
