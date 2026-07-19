import importlib.util
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
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

    def request(self, key, event_type="route_selected", parent=None, turn_id=None,
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
            "subject": subject or {"kind": "route", "ref": "fixture"},
            "references": [],
            "metrics": {},
            "dimensions": {},
        }
        value.update(overrides)
        return value

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
            "visited_skills": ["content-writer"],
            "chain_depth": 0,
            "pending_handoff": None,
            "next_action": {"code": "continue"},
        }

    def envelope_value(self, context, save_point, state, status="succeeded"):
        return {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "parent_run_id": None,
            "started_at": "2026-07-19T10:00:00Z",
            "ended_at": "2026-07-19T10:03:00Z",
            "status": status,
            "evidence_mode": "simulated",
            "route": {
                "skill": "content-writer",
                "version": "18.0.0",
                "reason_code": "fixture",
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
        with mock.patch.object(runtime, "MAX_EVENTS", 2):
            root_event = self.start()["event"]
            second = runtime.append_event(
                self.root, self.run_id,
                self.request("second", parent=root_event["event_id"]),
            )
            with self.assertRaisesRegex(runtime.RunEventError, "event limit"):
                runtime.append_event(
                    self.root, self.run_id,
                    self.request("overflow", parent=second["event"]["event_id"]),
                )
            self.assertEqual(2, len(runtime.load_events(self.root, self.run_id)))

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
        self.assertEqual(turn["event"]["event_id"], snapshot["event"]["parent_event_id"])

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
        with self.assertRaisesRegex(runtime.RunEventError, "current selected-branch skill"):
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
            envelope = self.envelope_value(bare_context, None, started["projection"])
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
        self.assertEqual(first_turn["event"]["event_id"], first_snapshot["event"]["parent_event_id"])

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
        self.assertEqual(turn["event"]["event_id"], snapshot["event"]["parent_event_id"])
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
        envelope = self.envelope_value(context, None, tool["projection"])
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


if __name__ == "__main__":
    unittest.main()
