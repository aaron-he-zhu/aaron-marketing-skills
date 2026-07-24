import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


profiles = load_module("profile_resolver_tests", "scripts/profile-resolver.py")
controller = load_module("profile_controller_tests", "scripts/runtime-controller.py")


class ProfileResolverTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.project = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def configure(project, profile):
        path = project / ".aaron-marketing" / "profile.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schema_version": "1.0", "profile": profile}) + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def tree_digest(root):
        records = []
        for path in sorted(root.rglob("*")):
            relative = str(path.relative_to(root))
            if path.is_file():
                records.append((
                    relative, hashlib.sha256(path.read_bytes()).hexdigest(),
                ))
            else:
                records.append((relative, "directory"))
        return records

    @staticmethod
    def start_request(run_id=None):
        return {
            "schema_version": "1.0",
            "run_id": run_id or str(uuid.uuid4()),
            "parent_run_id": None,
            "turn_id": "turn-1",
            "as_of": "2026-07-24T10:00:00Z",
            "route": {
                "target_skill": "content-writer",
                "command": "seo-geo",
                "reason_code": "profile-test",
            },
            "budget": {
                "max_tokens": 65_536,
                "bytes_per_token": 4,
                "max_resources": 128,
                "max_sensitivity": "confidential",
                "prefix_file_limit": 128,
            },
            "registry_offsets": {
                name: None for name in controller.runtime.REGISTRIES
            },
            "host": {
                "adapter": "test-host",
                "adapter_version": "1.0.0",
                "model_provider": "test-provider",
                "model_id": "test-model",
            },
            "system_prompt_sha256": "1" * 64,
            "tools": [],
            "permission_profile": {
                "mode": "read-only",
                "sandbox": "test",
                "network": False,
                "external_mutations": False,
            },
        }

    @staticmethod
    def create_legacy_run(project):
        run_id = str(uuid.uuid4())
        result = controller.runtime.append_event(project, run_id, {
            "schema_version": "1.0",
            "run_id": run_id,
            "idempotency_key": "legacy-start",
            "event_type": "run_started",
            "occurred_at": "2026-07-23T10:00:00Z",
            "actor": {"type": "system", "id": "legacy-runtime"},
            "parent_event_id": None,
            "turn_id": None,
            "status": "started",
            "subject": {"kind": "run", "ref": run_id},
            "references": [],
            "metrics": {},
            "dimensions": {},
        })
        return run_id, result

    def test_fresh_defaults_to_lite_without_writing_anything(self):
        before = self.tree_digest(self.project)
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, environ={},
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["reason_code"], "FRESH_DEFAULT_LITE")
        self.assertEqual(result["origin"], "fresh-default")
        self.assertEqual(result["effective_profile"], "lite")
        self.assertFalse(result["policy"]["new_run_allowed"])
        self.assertFalse(result["policy"]["external_mutation_authorized"])
        self.assertEqual(before, self.tree_digest(self.project))
        self.assertFalse((self.project / ".aaron-marketing").exists())

    def test_cli_environment_and_config_precedence_is_explicit(self):
        self.configure(self.project, "lite")
        environment = {profiles.ENVIRONMENT_VARIABLE: "pro"}
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, cli_profile="governed",
            environ=environment,
        )
        self.assertEqual(result["origin"], "cli")
        self.assertEqual(result["effective_profile"], "governed")
        self.assertTrue(result["policy"]["new_run_allowed"])
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, environ=environment,
        )
        self.assertEqual(result["origin"], "environment")
        self.assertEqual(result["effective_profile"], "pro")
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, environ={},
        )
        self.assertEqual(result["origin"], "project-config")
        self.assertEqual(result["effective_profile"], "lite")

    def test_invalid_config_fails_closed_even_with_cli_override(self):
        path = self.project / ".aaron-marketing" / "profile.json"
        path.parent.mkdir(parents=True)
        path.write_text('{"schema_version":"1.0","profile":"lite","extra":true}\n')
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, cli_profile="governed",
            environ={},
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "PROFILE_CONFIG_INVALID")
        self.assertIsNone(result["effective_profile"])
        self.assertFalse(result["policy"]["canonical_write_allowed"])

    def test_symlinked_profile_directory_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory)
            (outside / "profile.json").write_text(
                '{"schema_version":"1.0","profile":"governed"}\n'
            )
            (self.project / ".aaron-marketing").symlink_to(
                outside, target_is_directory=True
            )
            result = profiles.resolve_profile(
                self.project, bundle_root=ROOT, cli_profile="governed",
                environ={},
            )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "PROFILE_CONFIG_INVALID")

    def test_invalid_environment_fails_closed(self):
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT,
            environ={profiles.ENVIRONMENT_VARIABLE: "unbounded"},
        )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "PROFILE_ENV_INVALID")
        overridden = profiles.resolve_profile(
            self.project, bundle_root=ROOT, cli_profile="lite",
            environ={profiles.ENVIRONMENT_VARIABLE: "unbounded"},
        )
        self.assertEqual(overridden["status"], "ready")
        self.assertEqual(overridden["origin"], "cli")

    def test_physical_ceiling_cannot_be_raised(self):
        with tempfile.TemporaryDirectory() as directory:
            bundle = Path(directory)
            target = bundle / "references" / "capability-profiles.json"
            target.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "references/capability-profiles.json", target)
            (bundle / "distribution-manifest.json").write_text(json.dumps({
                "schema_version": "1.1",
                "kind": "plugin",
                "capability_ceiling": "lite",
            }) + "\n")
            result = profiles.resolve_profile(
                self.project, bundle_root=bundle, cli_profile="governed",
                environ={},
            )
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["reason_code"], "PROFILE_CEILING_EXCEEDED")
        self.assertEqual(result["package_ceiling"], "lite")

    def test_existing_state_without_config_is_legacy_read_only(self):
        stream = self.project / "memory" / "events" / "claims.ndjson"
        stream.parent.mkdir(parents=True)
        stream.write_text('{"legacy":true}\n', encoding="utf-8")
        result = profiles.resolve_profile(
            self.project, bundle_root=ROOT, environ={},
        )
        self.assertEqual(result["status"], "read-only")
        self.assertEqual(result["reason_code"], "LEGACY_STATE_READ_ONLY")
        self.assertEqual(result["effective_profile"], "legacy-read-only")
        self.assertTrue(result["state"]["canonical_state_present"])
        self.assertFalse(result["policy"]["registry_write_allowed"])

    def test_pre_v19_run_allows_lite_read_only_but_blocks_governed(self):
        run_id, _ = self.create_legacy_run(self.project)
        lite = profiles.resolve_profile(
            self.project, bundle_root=ROOT, cli_profile="lite", environ={},
        )
        self.assertEqual(lite["status"], "read-only")
        self.assertEqual(lite["reason_code"], "LEGACY_RUN_BLOCKED")
        self.assertIn(run_id, lite["state"]["pre_v19_nonterminal_runs"])
        governed = profiles.resolve_profile(
            self.project, bundle_root=ROOT, cli_profile="governed", environ={},
        )
        self.assertEqual(governed["status"], "blocked")
        self.assertEqual(governed["reason_code"], "LEGACY_RUN_BLOCKED")
        self.assertFalse(governed["policy"]["new_run_allowed"])
        self.assertFalse(governed["policy"]["registry_write_allowed"])

    def test_controller_never_appends_to_pre_v19_run_or_starts_around_it(self):
        self.configure(self.project, "governed")
        run_id, created = self.create_legacy_run(self.project)
        stream = self.project / "memory" / "runs" / run_id / "events.ndjson"
        before = stream.read_bytes()
        with self.assertRaisesRegex(
                controller.profile_runtime.ProfileError, "LEGACY_RUN_BLOCKED"):
            controller.resume_run(self.project, run_id, environ={})
        head = {
            "event_id": created["event"]["event_id"],
            "offset": created["event"]["offset"],
            "hash": created["event"]["event_hash"],
        }
        checkpoint = {
            "schema_version": "1.0",
            "checkpoint_id": str(uuid.uuid4()),
            "occurred_at": "2026-07-24T10:01:00Z",
            "expected_head": head,
            "status": "ready",
            "artifacts": [],
            "pending_handoff": None,
            "next_action": None,
        }
        with self.assertRaisesRegex(
                controller.profile_runtime.ProfileError, "LEGACY_RUN_BLOCKED"):
            controller.checkpoint_run(
                self.project, run_id, checkpoint, environ={},
            )
        finish = {
            "schema_version": "1.0",
            "occurred_at": "2026-07-24T10:02:00Z",
            "expected_head": head,
            "status": "aborted",
            "evidence_mode": "none",
            "artifacts": [],
            "metrics": {},
            "failure_class": "unknown",
            "next_action": None,
        }
        with self.assertRaisesRegex(
                controller.profile_runtime.ProfileError, "LEGACY_RUN_BLOCKED"):
            controller.finish_run(self.project, run_id, finish, environ={})
        with self.assertRaisesRegex(
                controller.profile_runtime.ProfileError, "LEGACY_RUN_BLOCKED"):
            controller.start_run(
                self.project, self.start_request(), environ={},
            )
        self.assertEqual(before, stream.read_bytes())
        self.assertEqual(
            [run_id],
            [
                path.parent.name
                for path in (self.project / "memory" / "runs").glob(
                    "*/events.ndjson"
                )
            ],
        )

    def test_every_profile_keeps_safety_overlays_and_never_authorizes_external_mutation(self):
        for profile in profiles.PROFILE_NAMES:
            with self.subTest(profile=profile):
                result = profiles.resolve_profile(
                    self.project, bundle_root=ROOT, cli_profile=profile,
                    environ={},
                )
                self.assertTrue(all(result["safety_overlays"].values()))
                self.assertFalse(result["policy"]["external_mutation_authorized"])

    def test_profile_switching_has_zero_canonical_drift(self):
        stream = self.project / "memory" / "events" / "claims.ndjson"
        stream.parent.mkdir(parents=True)
        stream.write_bytes(b'{"immutable":"fixture"}\n')
        before = self.tree_digest(self.project)
        for profile in profiles.PROFILE_NAMES:
            profiles.resolve_profile(
                self.project, bundle_root=ROOT, cli_profile=profile,
                environ={},
            )
        self.assertEqual(before, self.tree_digest(self.project))

    def test_diagnose_json_is_stable_and_read_only(self):
        before = self.tree_digest(self.project)
        checked = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/profile-resolver.py"),
                "--root", str(self.project), "--bundle-root", str(ROOT),
                "diagnose", "--json",
            ],
            check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        self.assertEqual(checked.returncode, 0, checked.stderr)
        result = json.loads(checked.stdout)
        self.assertEqual(result["effective_profile"], "lite")
        self.assertEqual(before, self.tree_digest(self.project))

    def test_catalog_and_result_schemas_are_closed(self):
        catalog_schema = json.loads(
            (ROOT / "references/capability-profiles.schema.json").read_text()
        )
        result_schema = json.loads(
            (ROOT / "references/profile-resolution.schema.json").read_text()
        )
        config_schema = json.loads(
            (ROOT / "references/profile-config.schema.json").read_text()
        )
        self.assertFalse(catalog_schema["additionalProperties"])
        self.assertFalse(result_schema["additionalProperties"])
        self.assertFalse(config_schema["additionalProperties"])
        catalog = profiles.load_profile_catalog(ROOT)
        self.assertEqual(catalog["profile_order"], list(profiles.PROFILE_NAMES))
        self.assertEqual(
            catalog["always_on_overlays"], list(profiles.ALWAYS_ON_OVERLAYS)
        )


if __name__ == "__main__":
    unittest.main()
