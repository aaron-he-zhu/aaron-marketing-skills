import copy
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import uuid
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "context_resolver", ROOT / "scripts" / "context-resolver.py"
)
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


class ContextResolverTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fixture = Path(self.temp.name)
        self.bundle = self.fixture / "bundle"
        self.project = self.fixture / "project"
        self.bundle.mkdir()
        self.project.mkdir()
        self.run_id = str(uuid.uuid4())
        self._write_catalog()
        self.write_bundle(
            "seo-geo/implement/content-writer/SKILL.md",
            "---\nname: content-writer\nversion: 1.2.3\n---\n\n# Content Writer\n",
        )
        for name in resolver.ALLOWED_SHARDS:
            self.write_bundle(name, "# %s\n" % Path(name).stem)

    def tearDown(self):
        self.temp.cleanup()

    def _write_catalog(self):
        catalog = {
            "architecture_version": "1.2.3",
            "commands": [
                "auto", "narrative", "seo-geo", "social", "email", "ad",
                "influencer", "launch",
            ],
            "disciplines": {
                "seo-geo": {
                    "command": {"name": "seo-geo"},
                    "phases": {"implement": ["content-writer"]},
                },
            },
            "protocol": {"skills": []},
        }
        self.write_bundle(
            "references/system-catalog.json",
            json.dumps(catalog, indent=2, sort_keys=True) + "\n",
        )

    @staticmethod
    def _write(root, relative, content):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def write_bundle(self, relative, content):
        return self._write(self.bundle, relative, content)

    def write_project(self, relative, content):
        return self._write(self.project, relative, content)

    @staticmethod
    def offsets(value=None):
        return {name: value for name in resolver.REGISTRIES}

    def candidate(self, resource_id, path, **overrides):
        value = {
            "resource_id": resource_id,
            "scope": "project",
            "path": path,
            "role": "evidence",
            "requirement": "optional",
            "authority": "working",
            "observed_at": "2026-07-18T12:00:00Z",
            "max_age_seconds": None,
            "priority": 50,
            "reason_code": "fixture",
            "sensitivity": "internal",
            "expected_sha256": None,
            "conflict_group": None,
            "supersedes": [],
        }
        value.update(overrides)
        return value

    def request(self, candidates, command="seo-geo", shards=None, **overrides):
        value = {
            "schema_version": "1.0",
            "run_id": self.run_id,
            "turn_id": "turn-1",
            "as_of": "2026-07-19T12:00:00Z",
            "route": {
                "command": command,
                "target_skill": "content-writer",
                "reason_code": "fixture-route",
                "scenario_shards": list(shards or []),
            },
            "budget": {
                "max_bytes": 100_000,
                "max_resources": 20,
                "max_inspection_bytes": 1_000_000,
                "max_sensitivity": "confidential",
            },
            "registry_offsets": self.offsets(None),
            "candidates": candidates,
        }
        value.update(overrides)
        return value

    def auto_request(self, candidates, shard="references/auto-routing/seo-geo.md", **overrides):
        shard_candidate = self.candidate(
            "route-shard", shard, scope="bundle", requirement="required",
            authority="approved", sensitivity="public", role="routing-scenario",
        )
        return self.request(
            [shard_candidate, *candidates], command="auto", shards=[shard], **overrides
        )

    def test_deterministic_selection_conflicts_dedupe_supersedes_and_budgets(self):
        contents = {
            "canonical.md": "canonical evidence\n",
            "approved.md": "approved evidence\n",
            "fresh-new.md": "fresh new\n",
            "fresh-old.md": "fresh old\n",
            "priority-high.md": "priority high\n",
            "priority-low.md": "priority low\n",
            "replacement.md": "replacement\n",
            "legacy.md": "legacy\n",
            "huge.md": "optional tail\n",
        }
        for path, content in contents.items():
            self.write_project(path, content)
        self.write_project("duplicate.md", contents["canonical.md"])
        candidates = [
            self.candidate(
                "canonical", "canonical.md", authority="canonical", priority=1,
                observed_at="2026-07-10T12:00:00Z", conflict_group="authority-choice",
                supersedes=["approved"],
            ),
            self.candidate(
                "approved", "approved.md", authority="approved", priority=100,
                observed_at="2026-07-19T11:00:00Z", conflict_group="authority-choice",
            ),
            self.candidate(
                "fresh-new", "fresh-new.md", observed_at="2026-07-19T11:00:00Z",
                priority=1, conflict_group="freshness-choice", supersedes=["fresh-old"],
            ),
            self.candidate(
                "fresh-old", "fresh-old.md", observed_at="2026-07-18T11:00:00Z",
                priority=100, conflict_group="freshness-choice",
            ),
            self.candidate(
                "priority-high", "priority-high.md", priority=90,
                conflict_group="priority-choice", supersedes=["priority-low"],
            ),
            self.candidate(
                "priority-low", "priority-low.md", priority=10,
                conflict_group="priority-choice",
            ),
            self.candidate(
                "replacement", "replacement.md", authority="canonical",
                supersedes=["legacy"],
            ),
            self.candidate("legacy", "legacy.md", requirement="required"),
            self.candidate("duplicate", "duplicate.md"),
            self.candidate("huge", "huge.md", authority="untrusted", priority=0),
            self.candidate("missing", "missing.md", authority="untrusted"),
            self.candidate(
                "forbidden", "never-read.md", requirement="forbidden",
                sensitivity="restricted",
            ),
        ]
        request = self.auto_request(candidates)
        request["budget"]["max_resources"] = 5
        manifest = resolver.resolve_context(request, self.bundle, self.project)

        selected = {item["resource_id"]: item for item in manifest["resources"]}
        self.assertEqual(
            {"route-shard", "replacement", "canonical", "fresh-new", "priority-high"},
            set(selected),
        )
        self.assertEqual("required", selected["replacement"]["requirement"])
        self.assertEqual(
            ["legacy", "replacement"], selected["replacement"]["satisfies_resource_ids"]
        )
        omitted = {item["resource_id"]: item for item in manifest["omitted"]}
        self.assertEqual("superseded", omitted["approved"]["reason_code"])
        self.assertEqual("superseded", omitted["fresh-old"]["reason_code"])
        self.assertEqual("superseded", omitted["priority-low"]["reason_code"])
        self.assertEqual("duplicate-content", omitted["duplicate"]["reason_code"])
        self.assertEqual("superseded", omitted["legacy"]["reason_code"])
        self.assertEqual("resource-budget", omitted["huge"]["reason_code"])
        self.assertEqual("missing", omitted["missing"]["reason_code"])
        self.assertEqual("forbidden", omitted["forbidden"]["reason_code"])
        self.assertIsNone(manifest["token_estimate"])
        self.assertIsNone(manifest["estimator"])
        resolver.validate_manifest(manifest)

        # Run/turn/as_of identify an invocation, not the reusable context selection.
        replay = copy.deepcopy(request)
        replay["run_id"] = str(uuid.uuid4())
        replay["turn_id"] = "turn-2"
        replay["as_of"] = "2026-07-20T12:00:00Z"
        replay_manifest = resolver.resolve_context(replay, self.bundle, self.project)
        self.assertEqual(manifest["context_signature"], replay_manifest["context_signature"])

    def test_unresolved_different_hash_conflict_fails_closed(self):
        self.write_project("left.md", "left")
        self.write_project("right.md", "right")
        request = self.request([
            self.candidate("left", "left.md", conflict_group="truth"),
            self.candidate("right", "right.md", conflict_group="truth"),
        ])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "unresolved context conflict"):
            resolver.resolve_context(request, self.bundle, self.project)

        self.write_project("right.md", "left")
        manifest = resolver.resolve_context(request, self.bundle, self.project)
        self.assertEqual(1, len(manifest["resources"]))
        self.assertEqual("duplicate-content", manifest["omitted"][0]["reason_code"])

    def test_candidate_order_invariance(self):
        self.write_project("alpha.md", "alpha")
        self.write_project("beta.md", "beta")
        candidates = [
            self.candidate("alpha", "alpha.md", priority=10),
            self.candidate("beta", "beta.md", priority=20),
        ]
        first = resolver.resolve_context(
            self.request(candidates), self.bundle, self.project,
        )
        reordered = self.request(list(reversed(candidates)))
        reordered["run_id"] = str(uuid.uuid4())
        reordered["turn_id"] = "turn-reordered"
        second = resolver.resolve_context(reordered, self.bundle, self.project)
        self.assertEqual(first["resources"], second["resources"])
        self.assertEqual(first["omitted"], second["omitted"])
        self.assertEqual(first["context_signature"], second["context_signature"])

    def test_required_resources_fail_closed(self):
        self.write_project("stale.md", "stale")
        self.write_project("secret.md", "secret")
        self.write_project("large.md", "large")
        self.write_project("hash.md", "hash")
        cases = [
            (
                self.candidate("required", "absent.md", requirement="required"),
                {}, "required context is missing",
            ),
            (
                self.candidate(
                    "required", "stale.md", requirement="required", max_age_seconds=0,
                    observed_at="2026-07-18T12:00:00Z",
                ),
                {}, "required context is stale",
            ),
            (
                self.candidate(
                    "required", "secret.md", requirement="required",
                    sensitivity="confidential",
                ),
                {"max_sensitivity": "internal"}, "sensitivity budget",
            ),
            (
                self.candidate("required", "large.md", requirement="required"),
                {"max_bytes": 2}, "byte budget",
            ),
            (
                self.candidate(
                    "required", "hash.md", requirement="required",
                    expected_sha256="0" * 64,
                ),
                {}, "hash mismatch",
            ),
        ]
        for candidate, budget, message in cases:
            with self.subTest(message=message):
                request = self.request([candidate])
                request["budget"].update(budget)
                with self.assertRaisesRegex(resolver.ContextResolutionError, message):
                    resolver.resolve_context(request, self.bundle, self.project)

    def test_auto_shards_catalog_and_closed_request_validation(self):
        valid = self.auto_request([])
        resolver.validate_request(valid)

        too_many = copy.deepcopy(valid)
        shards = sorted(resolver.ALLOWED_SHARDS)[:4]
        too_many["route"]["scenario_shards"] = shards
        too_many["candidates"] = [
            self.candidate(
                "shard-%d" % index, shard, scope="bundle", requirement="required",
                sensitivity="public",
            )
            for index, shard in enumerate(shards)
        ]
        with self.assertRaisesRegex(resolver.ContextResolutionError, "at most three"):
            resolver.validate_request(too_many)

        cross_only = copy.deepcopy(valid)
        cross = "references/auto-routing/cross-discipline.md"
        cross_only["route"]["scenario_shards"] = [cross]
        cross_only["candidates"][0]["path"] = cross
        with self.assertRaisesRegex(resolver.ContextResolutionError, "primary discipline"):
            resolver.validate_request(cross_only)

        second = "references/auto-routing/narrative.md"
        two_without_cross = copy.deepcopy(valid)
        two_without_cross["route"]["scenario_shards"].append(second)
        two_without_cross["candidates"].append(self.candidate(
            "second-shard", second, scope="bundle", requirement="required",
            sensitivity="public",
        ))
        with self.assertRaisesRegex(resolver.ContextResolutionError, "cross-discipline"):
            resolver.validate_request(two_without_cross)

        undeclared = copy.deepcopy(valid)
        undeclared["candidates"].append(self.candidate(
            "undeclared-shard", second, scope="bundle", requirement="required",
            sensitivity="public",
        ))
        with self.assertRaisesRegex(resolver.ContextResolutionError, "absent from route"):
            resolver.validate_request(undeclared)

        two_with_cross = copy.deepcopy(valid)
        two_with_cross["route"]["scenario_shards"].extend([cross, second])
        two_with_cross["candidates"].extend([
            self.candidate(
                "cross-shard", cross, scope="bundle", requirement="required",
                sensitivity="public", role="routing-scenario",
            ),
            self.candidate(
                "second-shard", second, scope="bundle", requirement="required",
                sensitivity="public", role="routing-scenario",
            ),
        ])
        resolver.validate_request(two_with_cross)

        mismatched_target = self.auto_request(
            [], shard="references/auto-routing/email.md"
        )
        resolver.validate_request(mismatched_target)
        with self.assertRaisesRegex(resolver.ContextResolutionError, "target skill discipline"):
            resolver.validate_route_against_catalog(mismatched_target, self.bundle)

        resolved = resolver.resolve_context(valid, self.bundle, self.project)
        forged = copy.deepcopy(resolved)
        forged["resources"] = []
        forged["budget"]["selected_bytes"] = 0
        forged["budget"]["selected_resources"] = 0
        with self.assertRaisesRegex(resolver.ContextResolutionError, "select every declared"):
            resolver.validate_manifest(forged)

        unknown = copy.deepcopy(valid)
        unknown["route"]["scenario_shards"] = ["references/auto-routing/unknown.md"]
        unknown["candidates"][0]["path"] = "references/auto-routing/unknown.md"
        with self.assertRaisesRegex(resolver.ContextResolutionError, "not allowed"):
            resolver.validate_request(unknown)

        missing_candidate = copy.deepcopy(valid)
        missing_candidate["candidates"] = []
        with self.assertRaisesRegex(resolver.ContextResolutionError, "required bundle candidate"):
            resolver.validate_request(missing_candidate)

        extra = copy.deepcopy(valid)
        extra["surprise"] = True
        with self.assertRaisesRegex(resolver.ContextResolutionError, "unknown fields"):
            resolver.validate_request(extra)

        wrong_target = copy.deepcopy(valid)
        wrong_target["route"]["target_skill"] = "not-a-skill"
        with self.assertRaisesRegex(resolver.ContextResolutionError, "absent from system catalog"):
            resolver.validate_route_against_catalog(wrong_target, self.bundle)

    def test_symlink_hardlink_special_traversal_and_future_observation_rejected(self):
        self.write_project("real.md", "source")
        os.symlink("real.md", self.project / "link.md")
        request = self.request([self.candidate("link", "link.md")])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "regular file"):
            resolver.resolve_context(request, self.bundle, self.project)

        hard = self.project / "hard.md"
        os.link(self.project / "real.md", hard)
        request = self.request([self.candidate("hard", "hard.md")])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "single-link"):
            resolver.resolve_context(request, self.bundle, self.project)

        fifo = self.project / "source.fifo"
        os.mkfifo(fifo)
        fifo_request = self.request([self.candidate("fifo", "source.fifo")])
        request_path = self.fixture / "fifo-request.json"
        request_path.write_text(json.dumps(fifo_request), encoding="utf-8")
        output = "memory/runs/%s/turns/turn-1/context-manifest.json" % self.run_id
        (self.project / Path(output).parent).mkdir(parents=True)
        completed = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts/context-resolver.py"), "resolve",
                "--request", str(request_path), "--bundle-root", str(self.bundle),
                "--project-root", str(self.project), "--output", output,
            ],
            capture_output=True, text=True, timeout=3,
        )
        self.assertEqual(2, completed.returncode)
        self.assertIn("regular file", completed.stderr)

        traversal = self.request([self.candidate("escape", "../outside.md")])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "dot path"):
            resolver.validate_request(traversal)

        future = self.request([
            self.candidate("future", "real.md", observed_at="2026-07-20T12:00:00Z")
        ])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "observed after as_of"):
            resolver.validate_request(future)

    def test_immutable_atomic_output_idempotency_and_no_source_body(self):
        secret = "never copy this source body"
        self.write_project("source.md", secret)
        manifest = resolver.resolve_context(
            self.request([self.candidate("source", "source.md", requirement="required")]),
            self.bundle,
            self.project,
        )
        output_dir = self.project / "memory" / "runs" / self.run_id / "turns" / "turn-1"
        output_dir.mkdir(parents=True)
        relative = "memory/runs/%s/turns/turn-1/context-manifest.json" % self.run_id

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(
                lambda _: resolver.write_manifest(self.project, relative, manifest), range(8)
            ))
        self.assertEqual(1, sum(not existed for _, existed in results))
        self.assertNotIn(secret, (self.project / relative).read_text(encoding="utf-8"))

        target = self.project / relative
        residue = target.parent / (".%s.context-create.crash" % target.name)
        os.link(target, residue)
        self.assertEqual(2, target.stat().st_nlink)
        _digest, existed = resolver.write_manifest(self.project, relative, manifest)
        self.assertTrue(existed)
        self.assertFalse(residue.exists())
        self.assertEqual(1, target.stat().st_nlink)

        target.chmod(0o400)
        with self.assertRaisesRegex(resolver.ContextResolutionError, "private file mode 0600"):
            resolver.write_manifest(self.project, relative, manifest)
        target.chmod(0o600)

        different = copy.deepcopy(manifest)
        different["budget"]["max_bytes"] -= 1
        different["request"]["budget"]["max_bytes"] -= 1
        different["request_sha256"] = resolver.sha256_json(different["request"])
        different["context_signature"] = resolver.sha256_json(
            resolver._signature_payload(different)
        )
        resolver.validate_manifest(different)
        with self.assertRaisesRegex(resolver.ContextResolutionError, "different content"):
            resolver.write_manifest(self.project, relative, different)

        tampered = copy.deepcopy(manifest)
        tampered["budget"]["selected_bytes"] += 1
        with self.assertRaisesRegex(
                resolver.ContextResolutionError,
                "cannot cover selected stable reads|does not match resources"):
            resolver.validate_manifest(tampered)

    def test_schema_documents_and_cli_round_trip(self):
        schemas = {}
        for name in ("context-request.schema.json", "context-manifest.schema.json"):
            with (ROOT / "references" / name).open(encoding="utf-8") as handle:
                document = json.load(handle)
            schemas[name] = document
            self.assertEqual("object", document["type"])
            self.assertFalse(document["additionalProperties"])

        request_schema = schemas["context-request.schema.json"]
        manifest_schema = schemas["context-manifest.schema.json"]
        self.assertEqual(request_schema["$defs"]["route"], manifest_schema["$defs"]["requestRoute"])
        self.assertEqual(request_schema["$defs"]["budget"], manifest_schema["$defs"]["requestBudget"])
        self.assertEqual(request_schema["$defs"]["candidate"], manifest_schema["$defs"]["candidate"])

        def assert_local_refs(node):
            if isinstance(node, dict):
                reference = node.get("$ref")
                if reference is not None:
                    self.assertTrue(reference.startswith("#/"), reference)
                    target = manifest_schema
                    for token in reference[2:].split("/"):
                        target = target[token.replace("~1", "/").replace("~0", "~")]
                for child in node.values():
                    assert_local_refs(child)
            elif isinstance(node, list):
                for child in node:
                    assert_local_refs(child)

        assert_local_refs(manifest_schema)

        self.write_project("source.md", "source")
        request = self.request([
            self.candidate("source", "source.md", requirement="required")
        ])
        request_path = self.fixture / "request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        relative = "memory/runs/%s/turns/turn-1/context-manifest.json" % self.run_id
        output_dir = self.project / Path(relative).parent
        output_dir.mkdir(parents=True)
        with redirect_stdout(io.StringIO()):
            exit_code = resolver.main([
                "resolve", "--request", str(request_path), "--bundle-root", str(self.bundle),
                "--project-root", str(self.project), "--output", relative,
            ])
        self.assertEqual(0, exit_code)
        manifest = json.loads((output_dir / "context-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(self.run_id, manifest["run_id"])
        self.assertEqual(64, len(manifest["context_signature"]))

    def test_git_worktree_requires_private_output_to_be_ignored(self):
        self.write_project("source.md", "source")
        manifest = resolver.resolve_context(
            self.request([self.candidate("source", "source.md", requirement="required")]),
            self.bundle,
            self.project,
        )
        relative = "memory/runs/%s/turns/turn-1/context-manifest.json" % self.run_id
        (self.project / Path(relative).parent).mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(self.project)], check=True)
        with self.assertRaisesRegex(resolver.ContextResolutionError, "not Git-ignored"):
            resolver.write_manifest(self.project, relative, manifest)
        (self.project / ".gitignore").write_text("memory/**\n", encoding="utf-8")
        digest, existed = resolver.write_manifest(self.project, relative, manifest)
        self.assertEqual(64, len(digest))
        self.assertFalse(existed)

    def test_safe_turn_identifier_round_trips_through_output_path(self):
        request = self.request([])
        request["turn_id"] = "sha256:abc123"
        manifest = resolver.resolve_context(request, self.bundle, self.project)
        relative = "memory/runs/%s/turns/sha256:abc123/context-manifest.json" % self.run_id
        (self.project / Path(relative).parent).mkdir(parents=True)
        digest, existed = resolver.write_manifest(self.project, relative, manifest)
        self.assertEqual(64, len(digest))
        self.assertFalse(existed)

    def test_manifest_reverification_detects_source_skill_and_catalog_drift(self):
        source = self.write_project("source.md", "source-v1")
        manifest = resolver.resolve_context(
            self.request([
                self.candidate("source", "source.md", requirement="required")
            ]),
            self.bundle,
            self.project,
        )
        self.assertIs(
            manifest,
            resolver.verify_manifest_sources(manifest, self.bundle, self.project),
        )

        source.write_text("source-v2", encoding="utf-8")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "source no longer matches"):
            resolver.verify_manifest_sources(manifest, self.bundle, self.project)
        source.write_text("source-v1", encoding="utf-8")

        skill = self.bundle / "seo-geo/implement/content-writer/SKILL.md"
        original_skill = skill.read_text(encoding="utf-8")
        skill.write_text(original_skill + "\nchanged\n", encoding="utf-8")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "target skill no longer matches"):
            resolver.verify_manifest_sources(manifest, self.bundle, self.project)
        skill.write_text(original_skill, encoding="utf-8")

        catalog = self.bundle / "references/system-catalog.json"
        catalog.write_text(catalog.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "catalog identity"):
            resolver.verify_manifest_sources(manifest, self.bundle, self.project)

    def test_budget_omission_and_required_overflow_fail_closed(self):
        self.write_project("required.md", "req!")
        self.write_project("optional.md", "opt")
        optional = self.candidate("optional", "optional.md", priority=100)
        required = self.candidate(
            "required", "required.md", requirement="required", priority=0,
        )
        request = self.request([optional, required])
        request["budget"]["max_inspection_bytes"] = 8
        manifest = resolver.resolve_context(request, self.bundle, self.project)
        self.assertEqual(["required"], [item["resource_id"] for item in manifest["resources"]])
        self.assertEqual(8, manifest["budget"]["inspected_bytes"])
        self.assertEqual(
            "inspection-budget",
            next(item for item in manifest["omitted"] if item["resource_id"] == "optional")
            ["reason_code"],
        )

        second_required = self.candidate(
            "required-two", "optional.md", requirement="required", priority=100,
        )
        request = self.request([required, second_required])
        request["budget"]["max_inspection_bytes"] = 8
        with self.assertRaisesRegex(resolver.ContextResolutionError, "inspection budget"):
            resolver.resolve_context(request, self.bundle, self.project)

    def test_nested_wrong_types_fail_closed_without_tracebacks(self):
        request = self.request([])
        request["route"]["command"] = {}
        with self.assertRaisesRegex(resolver.ContextResolutionError, "route.command"):
            resolver.validate_request(request)

        request = self.request([])
        request["budget"]["max_sensitivity"] = {}
        with self.assertRaisesRegex(resolver.ContextResolutionError, "max_sensitivity"):
            resolver.validate_request(request)

        request = self.request([
            self.candidate("bad", "bad.md", supersedes=[{}])
        ])
        with self.assertRaisesRegex(resolver.ContextResolutionError, "supersedes"):
            resolver.validate_request(request)

        request = self.request([])
        request["route"]["command"] = {}
        request_path = self.fixture / "malformed-request.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = resolver.main([
                "validate-request", "--request", str(request_path),
                "--bundle-root", str(self.bundle),
            ])
        self.assertEqual(2, result)
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_real_repository_quoted_skill_version_and_schema_contracts(self):
        manifest = resolver.resolve_context(self.request([]), ROOT, self.project)
        skill_path = ROOT / "seo-geo/implement/content-writer/SKILL.md"
        skill_version = resolver._frontmatter_scalar(
            skill_path.read_text(encoding="utf-8"), "version"
        )
        catalog_version = json.loads(
            (ROOT / "references/system-catalog.json").read_text(encoding="utf-8")
        )["architecture_version"]
        self.assertEqual(hashlib.sha256(skill_path.read_bytes()).hexdigest(), manifest["route"]["skill_sha256"])
        self.assertEqual(skill_version, manifest["route"]["skill_version"])
        self.assertEqual(catalog_version, manifest["route"]["catalog_version"])

        request_schema = json.loads(
            (ROOT / "references/context-request.schema.json").read_text(encoding="utf-8")
        )
        manifest_schema = json.loads(
            (ROOT / "references/context-manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertIn("skill_sha256", manifest_schema["$defs"]["route"]["required"])
        self.assertIn("skill_version", manifest_schema["$defs"]["route"]["required"])
        self.assertIn("inspected_bytes", manifest_schema["$defs"]["budget"]["required"])
        self.assertIn("max_inspection_bytes", request_schema["$defs"]["budget"]["required"])
        for schema in (request_schema, manifest_schema):
            safe_path = schema["$defs"]["safePath"]["pattern"]
            uuid_pattern = schema["$defs"]["uuid"]["pattern"]
            self.assertIsNone(re.fullmatch(safe_path, "source/"))
            self.assertIsNone(re.fullmatch(uuid_pattern, "00000000-0000-4000-0000-000000000000"))
            auto_rule = schema["$defs"]["route"]["allOf"][0]["then"]["properties"]["scenario_shards"]
            self.assertEqual(3, auto_rule["maxItems"])
            self.assertEqual(2, len(auto_rule["anyOf"]))
            empty, routed = auto_rule["anyOf"]
            self.assertEqual(0, empty["maxItems"])
            self.assertEqual(1, routed["minItems"])
            self.assertEqual(
                (1, 2), (routed["minContains"], routed["maxContains"])
            )

        resolver.validate_uuid("01890f3e-7b2d-7cc0-98c4-dc0c0c07398f", "uuid-v7")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "RFC UUID"):
            resolver.validate_uuid("00000000-0000-4000-0000-000000000000", "uuid")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "RFC 3339"):
            resolver.parse_datetime("2026-07-19 10:00:00+00:00", "timestamp")

    def test_concurrent_retry_can_recover_post_link_crash_window(self):
        request = self.request([])
        request["turn_id"] = "turn-race"
        manifest = resolver.resolve_context(request, self.bundle, self.project)
        relative = "memory/runs/%s/turns/turn-race/context-manifest.json" % self.run_id
        (self.project / Path(relative).parent).mkdir(parents=True)
        installed = threading.Event()
        release = threading.Event()
        real_link = os.link
        first = {"pending": True}
        first_lock = threading.Lock()

        def delayed_link(*args, **kwargs):
            real_link(*args, **kwargs)
            with first_lock:
                should_wait = first["pending"]
                first["pending"] = False
            if should_wait:
                installed.set()
                if not release.wait(5):
                    raise AssertionError("concurrent retry did not reach recovery window")

        with mock.patch.object(resolver.os, "link", side_effect=delayed_link):
            with ThreadPoolExecutor(max_workers=2) as pool:
                first_write = pool.submit(
                    resolver.write_manifest, self.project, relative, manifest
                )
                self.assertTrue(installed.wait(3))
                retry = pool.submit(
                    resolver.write_manifest, self.project, relative, manifest
                )
                retry_result = retry.result(timeout=3)
                release.set()
                first_result = first_write.result(timeout=3)
        self.assertTrue(retry_result[1])
        self.assertFalse(first_result[1])

    def test_directory_swap_failures_close_new_child_descriptors(self):
        self.write_project("nested/source.md", "source")
        real_open = os.open

        for operation in ("read", "write"):
            opened_children = []

            def tracked_open(path, *args, **kwargs):
                descriptor = real_open(path, *args, **kwargs)
                if path == "nested" and kwargs.get("dir_fd") is not None:
                    opened_children.append(descriptor)
                return descriptor

            with self.subTest(operation=operation), \
                    mock.patch.object(resolver.os, "open", side_effect=tracked_open), \
                    mock.patch.object(
                        resolver, "_entry_stat",
                        side_effect=resolver.ContextResolutionError("directory swapped"),
                    ):
                with self.assertRaisesRegex(resolver.ContextResolutionError, "directory swapped"):
                    if operation == "read":
                        resolver.anchored_read(self.project, "nested/source.md", 1024)
                    else:
                        with resolver._open_output_parent(self.project, "nested/context.json"):
                            pass
            self.assertEqual(1, len(opened_children))
            with self.assertRaises(OSError):
                os.fstat(opened_children[0])


if __name__ == "__main__":
    unittest.main()
