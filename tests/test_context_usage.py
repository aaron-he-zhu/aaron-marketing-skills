#!/usr/bin/env python3
"""Regression tests for context-usage-v1 telemetry."""
from __future__ import annotations

from argparse import Namespace
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "context-usage.py"
SCHEMA = ROOT / "evals" / "context-usage-v1.schema.json"


def load_module():
    spec = importlib.util.spec_from_file_location("aaron_context_usage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_script(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def valid_record():
    return {
        "schema_version": "1.0",
        "record_id": "run-1:turn-1",
        "recorded_at": "2026-08-01T00:00:00Z",
        "route": {
            "command": "seo-geo", "target_skill": "content-writer",
            "reason_code": "user-request",
        },
        "profiles": {"capability": "governed", "prompt": None, "host": None},
        "experiment": {
            "pair_id": None, "arm_id": None, "repeat_index": None,
            "randomized_order": None, "context_profile_sha256": None,
            "prompt_sha256": None, "toolset_sha256": None,
        },
        "context": {
            "context_signature": "a" * 64,
            "request_sha256": "b" * 64,
            "bytes": {
                "discovery": None, "repository_instructions": None,
                "control_plane": None, "model_visible_static": None,
                "tool_schemas": None, "references": None, "evidence": None,
                "required_total": 100, "selected_total": 200, "capacity": 1000,
            },
            "tokens": {
                "input": None, "cache_creation": None, "cache_read": None,
                "output": None, "reasoning": None,
            },
            "resources": {"candidates": 4, "required": 2, "selected": 3, "omitted": 1},
            "disclosure": {
                "events": None, "required": None, "satisfied": None,
                "recall": None, "precision": None,
            },
            "reference_bytes_by_reason": [
                {"reason_code": "machine-contract", "bytes": 75, "resources": 1},
            ],
        },
        "provider": {"name": None, "model_id": None, "model_revision": None},
        "outcome": {
            "status": "measured", "route_outcome": None, "task_outcome": None,
            "latency_ms": None, "tool_calls": None, "cost_usd": None,
        },
        "provenance": {
            "source": "static-baseline", "manifest_sha256": None, "notes": [],
        },
    }


def assembly_resource(resource_id, *, consumer, size, materialization="body"):
    return {
        "resource_id": resource_id,
        "scope": "bundle",
        "path": "references/%s.json" % resource_id,
        "sha256": (resource_id[-1] if resource_id[-1] in "abcdef" else "a") * 64,
        "bytes": size,
        "body_bytes": size if materialization == "body" else 0,
        "role": "skill-reference" if consumer == "deferred" else "skill-definition",
        "module_id": "model-authored-reference" if consumer == "deferred" else "%s-context" % consumer,
        "materialization": materialization,
        "load_policy": "conditional" if consumer == "deferred" else "always",
        "source_resource_id": "source-%s" % resource_id,
    }


def valid_assembly(module):
    consumers = {
        "controller": [assembly_resource("a-controller", consumer="controller", size=10)],
        "model": [assembly_resource("b-model", consumer="model", size=20)],
        "tool": [assembly_resource("c-tool", consumer="tool", size=30)],
        "deferred": [assembly_resource(
            "d-reference", consumer="deferred", size=40, materialization="on-demand",
        )],
    }
    value = {
        "$schema": "./context-assembly.schema.json",
        "schema_version": "1.0",
        "kind": "consumer-separated-context-assembly",
        "context_signature": "c" * 64,
        "route": {"command": "seo-geo", "target_skill": "content-writer"},
        "profile": {
            "host_profile": "claude-code-plugin-host",
            "model_id": "test-model-1",
            "model_revision": None,
            "distribution_profile": "repository",
            "physical_distribution_kind": "repository",
            "planner_distribution_profile": "repository",
            "distribution_evaluation_only": False,
            "distribution_manifest_sha256": None,
            "prompt_profile": "explicit",
            "prompt_profile_source": "host-default",
            "binding_id": None,
            "always_on_overlays": [
                "consent", "claims", "pii-secrets", "external-mutation",
                "audit-verdict", "release-provenance",
            ],
            "catalogs": {
                "host_sha256": "d" * 64,
                "prompt_sha256": "e" * 64,
                "context_modules_sha256": "f" * 64,
            },
        },
        "deployment_eligible": True,
        "evaluation_run_id": None,
        "consumers": consumers,
        "replacements": [],
        "usage": {
            "manifest_selected_bytes": 100,
            "controller_body_bytes": 10,
            "model_body_bytes": 20,
            "tool_body_bytes": 30,
            "deferred_bytes": 40,
            "model_reduction_bytes": 0,
            "model_reduction_ratio": 0,
        },
        "assembly_signature": "",
    }
    payload = dict(value)
    payload.pop("assembly_signature")
    value["assembly_signature"] = module.hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return value


def resign_assembly(module, value):
    payload = dict(value)
    payload.pop("assembly_signature")
    value["assembly_signature"] = module.hashlib.sha256(
        json.dumps(
            payload, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return value


def current_manifest():
    """Resolve a complete current manifest from a private bundle copy."""
    planner = load_script(
        "context_usage_manifest_planner_%s" % uuid.uuid4().hex,
        "scripts/context-plan.py",
    )
    with tempfile.TemporaryDirectory() as temporary:
        workspace = Path(temporary)
        bundle = workspace / "bundle"
        shutil.copytree(
            ROOT,
            bundle,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        project = workspace / "project"
        project.mkdir()
        request = planner.build_request(
            skill="content-writer",
            run_id=str(uuid.uuid4()),
            turn_id="context-usage-manifest",
            as_of="2026-08-01T00:00:00Z",
            project_root=project,
            bundle_root=bundle,
            distribution_profile="repository",
        )
        manifest = planner.resolver.resolve_context(request, bundle, project)
    return planner.resolver, manifest


class ContextUsageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_schema_is_strict_and_has_expected_identity(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.0")
        self.assertEqual(
            set(schema["required"]), self.module.TOP_FIELDS,
        )
        self.assertIn(
            "assembly",
            schema["properties"]["provenance"]["properties"]["source"]["enum"],
        )

    def test_valid_record_accepts_unknown_provider_usage_as_null(self):
        self.assertEqual(self.module.validate_record(valid_record()), valid_record())

    def test_unknown_field_and_impossible_arithmetic_fail_closed(self):
        record = valid_record()
        record["extra"] = True
        with self.assertRaisesRegex(self.module.ContextUsageError, "keys must be exactly"):
            self.module.validate_record(record)
        record = valid_record()
        record["context"]["bytes"]["required_total"] = 201
        with self.assertRaisesRegex(self.module.ContextUsageError, "required_total"):
            self.module.validate_record(record)

    def test_experiment_identity_and_disclosure_arithmetic_are_closed(self):
        record = valid_record()
        record["experiment"].update({
            "pair_id": "pair-1", "arm_id": "candidate", "repeat_index": 2,
            "randomized_order": 1, "context_profile_sha256": "e" * 64,
            "prompt_sha256": "f" * 64, "toolset_sha256": "0" * 64,
        })
        record["context"]["disclosure"].update({
            "events": 4, "required": 3, "satisfied": 3,
            "recall": 1.0, "precision": 0.75,
        })
        self.module.validate_record(record)
        record["context"]["disclosure"]["satisfied"] = 4
        with self.assertRaisesRegex(self.module.ContextUsageError, "disclosure satisfied"):
            self.module.validate_record(record)

    def test_manifest_projection_keeps_unavailable_token_fields_null(self):
        _resolver, manifest = current_manifest()
        args = Namespace(
            record_id="run-1:turn-1", recorded_at="2026-08-01T00:00:00Z",
            capability_profile="governed", prompt_profile=None, host_profile="claude-code",
        )
        raw = json.dumps(manifest, sort_keys=True).encode()
        record = self.module.record_from_manifest(manifest, raw, args)
        self.assertEqual(
            record["context"]["bytes"]["selected_total"],
            manifest["budget"]["selected_bytes"],
        )
        self.assertEqual(
            record["context"]["bytes"]["required_total"],
            sum(
                resource["bytes"] for resource in manifest["resources"]
                if resource["requirement"] == "required"
            ),
        )
        self.assertIsNone(record["context"]["bytes"]["model_visible_static"])
        self.assertTrue(all(value is None for value in record["context"]["tokens"].values()))
        self.assertEqual(
            sum(
                item["bytes"]
                for item in record["context"]["reference_bytes_by_reason"]
            ),
            manifest["budget"]["selected_bytes"],
        )

    def test_manifest_projection_rejects_arithmetic_and_identity_hash_tampering(self):
        resolver, manifest = current_manifest()
        args = Namespace(
            record_id="run-1:tamper", recorded_at="2026-08-01T00:00:00Z",
            capability_profile=None, prompt_profile=None, host_profile=None,
        )

        arithmetic_tamper = copy.deepcopy(manifest)
        arithmetic_tamper["budget"]["selected_bytes"] -= 1
        arithmetic_tamper["context_signature"] = resolver.sha256_json(
            resolver._signature_payload(arithmetic_tamper)
        )
        with self.assertRaisesRegex(
                self.module.ContextUsageError,
                "budget.selected_bytes does not match resources"):
            self.module.record_from_manifest(
                arithmetic_tamper,
                json.dumps(arithmetic_tamper, sort_keys=True).encode(),
                args,
            )

        identity_tamper = copy.deepcopy(manifest)
        identity_tamper["request"]["turn_id"] = "forged-turn"
        with self.assertRaisesRegex(
                self.module.ContextUsageError,
                "request_sha256 does not match the embedded request"):
            self.module.record_from_manifest(
                identity_tamper,
                json.dumps(identity_tamper, sort_keys=True).encode(),
                args,
            )

    def test_assembly_projection_populates_measured_consumer_bytes(self):
        assembly = valid_assembly(self.module)
        args = Namespace(
            record_id="run-assembly:turn-1",
            recorded_at="2026-08-01T00:00:00Z",
            capability_profile="governed",
        )
        raw = json.dumps(assembly, sort_keys=True).encode()
        record = self.module.record_from_assembly(assembly, raw, args)
        self.assertEqual(
            {
                "control_plane": 10,
                "model_visible_static": 20,
                "tool_schemas": 30,
                "references": 40,
                "selected_total": 100,
            },
            {
                field: record["context"]["bytes"][field]
                for field in (
                    "control_plane", "model_visible_static", "tool_schemas",
                    "references", "selected_total",
                )
            },
        )
        self.assertEqual(record["profiles"]["prompt"], "explicit")
        self.assertEqual(record["profiles"]["host"], "claude-code-plugin-host")
        self.assertEqual(record["provider"]["model_id"], "test-model-1")
        self.assertIsNone(record["provider"]["model_revision"])
        self.assertEqual(record["provenance"]["source"], "assembly")
        self.assertEqual(record["context"]["resources"]["selected"], 4)
        self.assertEqual(
            record["context"]["reference_bytes_by_reason"],
            [{
                "reason_code": "model-authored-reference",
                "bytes": 40,
                "resources": 1,
            }],
        )
        self.assertTrue(all(value is None for value in record["context"]["tokens"].values()))

    def test_assembly_profile_distribution_and_revision_semantics_fail_closed(self):
        args = Namespace(
            record_id="run-assembly:profile-validation",
            recorded_at="2026-08-01T00:00:00Z",
            capability_profile=None,
        )
        for field, invalid, message in (
                ("model_revision", "", "model_revision"),
                ("distribution_profile", "enterprise", "distribution_profile"),
                (
                    "distribution_manifest_sha256", "not-a-hash",
                    "distribution_manifest_sha256",
                )):
            with self.subTest(field=field):
                assembly = valid_assembly(self.module)
                assembly["profile"][field] = invalid
                resign_assembly(self.module, assembly)
                with self.assertRaisesRegex(self.module.ContextUsageError, message):
                    self.module.record_from_assembly(
                        assembly, json.dumps(assembly).encode(), args
                    )

    def test_current_build_assembly_projects_end_to_end(self):
        planner = load_script("context_usage_e2e_planner", "scripts/context-plan.py")
        assembly_runtime = load_script(
            "context_usage_e2e_assembly", "scripts/context-assembly.py"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            bundle = workspace / "bundle"
            shutil.copytree(
                ROOT,
                bundle,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            project = workspace / "project"
            project.mkdir()
            request = planner.build_request(
                skill="content-writer",
                run_id=str(uuid.uuid4()),
                turn_id="context-usage-e2e",
                as_of="2026-08-01T00:00:00Z",
                project_root=project,
                bundle_root=bundle,
                distribution_profile="repository",
            )
            manifest = planner.resolver.resolve_context(request, bundle, project)
            assembly = assembly_runtime.build_assembly(
                manifest,
                bundle_root=bundle,
                project_root=project,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                model_revision="immutable-snapshot-1",
                as_of="2026-08-01T00:00:00Z",
                verify_sources=True,
            )
        args = Namespace(
            record_id="run-assembly:e2e",
            recorded_at="2026-08-01T00:00:00Z",
            capability_profile="governed",
        )
        raw = json.dumps(assembly, sort_keys=True).encode()
        record = self.module.record_from_assembly(assembly, raw, args)
        self.assertEqual(assembly["profile"]["distribution_profile"], "repository")
        self.assertIsNone(assembly["profile"]["distribution_manifest_sha256"])
        self.assertEqual(record["provider"]["model_revision"], "immutable-snapshot-1")
        self.assertEqual(
            record["context"]["bytes"]["model_visible_static"],
            assembly["usage"]["model_body_bytes"],
        )

    def test_assembly_projection_rejects_integrity_checked_usage_that_misses_resources(self):
        assembly = valid_assembly(self.module)
        assembly["usage"]["deferred_bytes"] = 41
        resign_assembly(self.module, assembly)
        args = Namespace(
            record_id="run-assembly:turn-2",
            recorded_at="2026-08-01T00:00:00Z",
            capability_profile=None,
        )
        with self.assertRaisesRegex(
                self.module.ContextUsageError, "deferred_bytes does not match"):
            self.module.record_from_assembly(assembly, json.dumps(assembly).encode(), args)

    def test_cli_projects_assembly_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            assembly_path = Path(temporary) / "assembly.json"
            output_path = Path(temporary) / "usage.json"
            assembly_path.write_text(json.dumps(valid_assembly(self.module)), encoding="utf-8")
            self.assertEqual(self.module.main([
                "from-assembly", "--assembly", str(assembly_path),
                "--record-id", "run-cli:turn-1",
                "--recorded-at", "2026-08-01T00:00:00Z",
                "--output", str(output_path),
            ]), 0)
            record = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(record["context"]["bytes"]["model_visible_static"], 20)

    def test_summarize_uses_nearest_rank_percentiles(self):
        records = []
        for index, selected in enumerate((100, 200, 300, 400), 1):
            record = valid_record()
            record["record_id"] = "record-%d" % index
            record["context"]["bytes"]["selected_total"] = selected
            records.append(record)
        summary = self.module.summarize(records)
        self.assertEqual(summary["bytes"]["selected_total"]["p50"], 200)
        self.assertEqual(summary["bytes"]["selected_total"]["p95"], 400)

    def test_cli_validates_record(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "record.json"
            path.write_text(json.dumps(valid_record()), encoding="utf-8")
            self.assertEqual(self.module.main(["validate", str(path)]), 0)


if __name__ == "__main__":
    unittest.main()
