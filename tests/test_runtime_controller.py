import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "runtime_controller_tests", ROOT / "scripts" / "runtime-controller.py"
)
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


class RuntimeControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)
        self.configure_profile(self.project)

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def offsets():
        return {name: None for name in controller.runtime.REGISTRIES}

    @staticmethod
    def configure_profile(project, profile="governed"):
        path = project / ".aaron-marketing" / "profile.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schema_version": "1.0", "profile": profile}) + "\n",
            encoding="utf-8",
        )

    def start_request(self, run_id=None, **overrides):
        value = {
            "schema_version": "1.0",
            "run_id": run_id or str(uuid.uuid4()),
            "parent_run_id": None,
            "turn_id": "turn-1",
            "as_of": "2026-07-22T13:00:00Z",
            "route": {
                "target_skill": "content-writer",
                "command": "seo-geo",
                "reason_code": "user-request",
            },
            "budget": {
                "max_tokens": 65_536,
                "bytes_per_token": 4,
                "max_resources": 128,
                "max_sensitivity": "confidential",
                "prefix_file_limit": 128,
            },
            "registry_offsets": self.offsets(),
            "host": {
                "adapter": "test-host",
                "adapter_version": "1.0.0",
                "model_provider": "test-provider",
                "model_id": "test-model",
            },
            "system_prompt_sha256": "1" * 64,
            "tools": [
                {"name": "Read", "mode": "read-only", "schema_sha256": "2" * 64}
            ],
            "permission_profile": {
                "mode": "read-only",
                "sandbox": "test",
                "network": False,
                "external_mutations": False,
            },
        }
        value.update(overrides)
        return value

    @staticmethod
    def checkpoint_request(head, checkpoint_id=None, **overrides):
        value = {
            "schema_version": "1.0",
            "checkpoint_id": checkpoint_id or str(uuid.uuid4()),
            "occurred_at": "2026-07-22T13:01:00Z",
            "expected_head": head,
            "status": "ready",
            "artifacts": [],
            "pending_handoff": None,
            "next_action": {"code": "finish"},
        }
        value.update(overrides)
        return value

    @staticmethod
    def finish_request(head, status="succeeded", **overrides):
        value = {
            "schema_version": "1.0",
            "occurred_at": "2026-07-22T13:02:00Z",
            "expected_head": head,
            "status": status,
            "evidence_mode": "simulated" if status == "succeeded" else "none",
            "artifacts": [],
            "metrics": {"host_turns": 1},
            "failure_class": "unknown" if status in {"failed", "blocked", "aborted"} else None,
            "next_action": None,
        }
        value.update(overrides)
        return value

    @staticmethod
    def read(project, relative):
        return json.loads((project / relative).read_text(encoding="utf-8"))

    def copy_selected_bundle(self, skill="content-writer"):
        bundle = Path(tempfile.mkdtemp(prefix="controller-bundle-", dir=self.project))
        index = json.loads((ROOT / controller.planner.INDEX_REF).read_text(encoding="utf-8"))
        entry = next(item for item in index["contracts"] if item["skill"] == skill)
        contract = json.loads((ROOT / entry["contract_ref"]).read_text(encoding="utf-8"))
        paths = {
            ".claude-plugin/plugin.json",
            "references/capability-profiles.json",
            controller.planner.INDEX_REF,
            entry["contract_ref"],
            index["contract_schema"]["path"],
            index["shared_contract"]["path"],
            index["source_catalog"]["path"],
            contract["identity"]["path"],
            *(item["path"] for item in contract["context_hints"]["bundle_references"]),
        }
        for relative in paths:
            target = bundle / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        return bundle, entry

    def test_start_consumes_machine_contract_and_materializes_verified_chain(self):
        request = self.start_request()
        result = controller.start_run(self.project, request)
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["route"]["reason_code"], "user-request")
        self.assertEqual(
            [event["event_type"] for event in controller.runtime.load_events(
                self.project, request["run_id"]
            )],
            [
                "run_started", "route_selected", "turn_started", "context_resolved",
                "turn_snapshot_created",
            ],
        )
        started_event = controller.runtime.load_events(
            self.project, request["run_id"]
        )[0]
        self.assertIn(
            {
                "kind": "source",
                "ref": "aaron-marketing-runtime:19.0.0",
                "sha256": controller.profile_runtime.load_profile_catalog(ROOT)["_sha256"],
            },
            started_event["references"],
        )
        manifest = self.read(self.project, result["context_manifest"]["ref"])
        self.assertEqual(
            result["machine_contract"], manifest["request"]["planner"]["skill_contract"]
        )
        snapshot = self.read(self.project, result["snapshot"]["ref"])
        self.assertEqual(snapshot["permission_profile"], request["permission_profile"])
        self.assertEqual(snapshot["skill"]["version"], manifest["route"]["skill_version"])
        self.assertEqual(os.stat(self.project / result["snapshot"]["ref"]).st_mode & 0o777, 0o600)
        resumed = controller.resume_run(self.project, request["run_id"])
        self.assertTrue(resumed["resumable"])
        self.assertEqual(resumed["latest_binding"]["machine_contract"], result["machine_contract"])

    def test_start_is_idempotent_and_conflicting_snapshot_replay_fails_closed(self):
        request = self.start_request()
        first = controller.start_run(self.project, request)
        second = controller.start_run(self.project, request)
        self.assertTrue(second["deduplicated"])
        self.assertEqual(first["head"], second["head"])
        self.assertEqual(
            len(controller.runtime.load_events(self.project, request["run_id"])), 5
        )

        conflict = copy.deepcopy(request)
        conflict["permission_profile"]["mode"] = "proposal-only"
        with self.assertRaisesRegex(controller.runtime.RunEventError, "different artifact content"):
            controller.start_run(self.project, conflict)
        events = controller.runtime.load_events(self.project, request["run_id"])
        self.assertEqual(len(events), 5)
        self.assertEqual(controller.runtime.project_events(request["run_id"], events)["status"], "active")

    def test_contract_drift_fails_before_a_run_is_created(self):
        request = self.start_request()
        bundle, entry = self.copy_selected_bundle()
        with (bundle / entry["contract_ref"]).open("ab") as handle:
            handle.write(b"\n")
        with self.assertRaisesRegex(controller.planner.ContextPlanError, "hash"):
            controller.start_run(self.project, request, bundle_root=bundle)
        self.assertFalse((self.project / "memory/runs" / request["run_id"]).exists())

    def test_checkpoint_requires_current_head_and_replays_exactly(self):
        request = self.start_request()
        started = controller.start_run(self.project, request)
        checkpoint_id = str(uuid.uuid4())
        checkpoint = self.checkpoint_request(started["head"], checkpoint_id)
        first = controller.checkpoint_run(self.project, request["run_id"], checkpoint)
        replay = controller.checkpoint_run(self.project, request["run_id"], checkpoint)
        self.assertTrue(replay["deduplicated"])
        self.assertEqual(first["save_point"], replay["save_point"])

        conflict = copy.deepcopy(checkpoint)
        conflict["status"] = "blocked"
        with self.assertRaisesRegex(controller.runtime.RunEventError, "different artifact content"):
            controller.checkpoint_run(self.project, request["run_id"], conflict)
        stale = self.checkpoint_request(started["head"])
        with self.assertRaisesRegex(controller.ControllerError, "stale"):
            controller.checkpoint_run(self.project, request["run_id"], stale)

    def test_successful_finish_is_idempotent_and_reports_controller_metrics(self):
        request = self.start_request()
        started = controller.start_run(self.project, request)
        checkpoint = controller.checkpoint_run(
            self.project, request["run_id"], self.checkpoint_request(started["head"]),
        )
        finish_request = self.finish_request(checkpoint["head"])
        first = controller.finish_run(self.project, request["run_id"], finish_request)
        replay = controller.finish_run(self.project, request["run_id"], finish_request)
        self.assertTrue(replay["deduplicated"])
        self.assertEqual(first["envelope"], replay["envelope"])
        envelope = self.read(self.project, first["envelope"]["ref"])
        self.assertEqual(envelope["route"]["skill"], "content-writer")
        self.assertEqual(envelope["metrics"]["controller.turns"], 1)
        self.assertEqual(envelope["metrics"]["controller.checkpoints"], 1)
        context_manifest = self.read(
            self.project, envelope["context_manifests"][0]["ref"]
        )
        self.assertEqual(
            envelope["metrics"]["controller.context_resources"],
            context_manifest["budget"]["selected_resources"],
        )

    def test_wait_failure_abort_and_success_all_create_typed_envelopes(self):
        for status in ("waiting", "failed", "aborted", "succeeded"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                project = Path(directory)
                self.configure_profile(project)
                request = self.start_request()
                started = controller.start_run(project, request)
                finished = controller.finish_run(
                    project, request["run_id"], self.finish_request(started["head"], status),
                )
                envelope = self.read(project, finished["envelope"]["ref"])
                self.assertEqual(envelope["status"], status)
                expected_event = {
                    "waiting": "run_waiting", "failed": "run_failed",
                    "aborted": "run_aborted", "succeeded": "run_finished",
                }[status]
                self.assertEqual(
                    controller.runtime.load_events(project, request["run_id"])[-1]["event_type"],
                    expected_event,
                )

    def test_resume_ignores_projection_but_rejects_live_context_drift(self):
        projection = self.project / "memory/projections/claims.json"
        projection.parent.mkdir(parents=True)
        projection.write_text("{}\n", encoding="utf-8")
        request = self.start_request()
        controller.start_run(self.project, request)
        session = self.project / "memory/runs" / request["run_id"] / "session.json"
        session.write_text("{}\n", encoding="utf-8")
        self.assertTrue(controller.resume_run(self.project, request["run_id"])["resumable"])
        projection.write_text('{"changed":true}\n', encoding="utf-8")
        with self.assertRaisesRegex(controller.runtime.RunEventError, "source no longer matches"):
            controller.resume_run(self.project, request["run_id"])

    def test_success_rejects_open_tool_and_start_failure_is_typed(self):
        request = self.start_request()
        started = controller.start_run(self.project, request)
        tool = controller.runtime.append_event(
            self.project, request["run_id"], controller._event_request(
                request["run_id"], "test-tool", "tool_requested",
                "2026-07-22T13:01:00Z", started["head"]["event_id"], "started",
                {"kind": "tool", "ref": "tool-1"}, turn_id="turn-1",
            ),
        )
        tool_state = tool["projection"]
        head = {
            "event_id": tool_state["head_event_id"], "offset": tool_state["last_offset"],
            "hash": tool_state["last_event_hash"],
        }
        with self.assertRaisesRegex(controller.runtime.RunEventError, "unfinished tool"):
            controller.finish_run(
                self.project, request["run_id"], self.finish_request(head),
            )

        failed_project = self.project / "failed-open"
        failed_project.mkdir()
        self.configure_profile(failed_project)
        failed_request = self.start_request()
        with mock.patch.object(
                controller.runtime, "write_snapshot",
                side_effect=controller.runtime.RunEventError("injected snapshot failure")):
            with self.assertRaisesRegex(controller.runtime.RunEventError, "injected"):
                controller.start_run(failed_project, failed_request)
        failed_events = controller.runtime.load_events(failed_project, failed_request["run_id"])
        self.assertEqual(failed_events[-1]["event_type"], "run_failed")
        failed_envelope = self.read(
            failed_project, failed_events[-1]["references"][0]["ref"]
        )
        self.assertEqual(failed_envelope["failure_class"], "context")

    def test_request_schema_is_closed_and_matches_controller_variants(self):
        schema = json.loads(
            (ROOT / "references/runtime-controller-request.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            schema["oneOf"], [
                {"$ref": "#/$defs/start"}, {"$ref": "#/$defs/checkpoint"},
                {"$ref": "#/$defs/finish"},
            ]
        )
        for variant in ("start", "checkpoint", "finish"):
            self.assertFalse(schema["$defs"][variant]["additionalProperties"])
        invalid = self.start_request()
        invalid["unexpected"] = True
        with self.assertRaisesRegex(controller.ControllerError, "unexpected"):
            controller.validate_start_request(invalid)
        invalid = self.start_request()
        invalid["permission_profile"]["external_mutations"] = True
        with self.assertRaisesRegex(controller.ControllerError, "write-gated"):
            controller.validate_start_request(invalid)


if __name__ == "__main__":
    unittest.main()
