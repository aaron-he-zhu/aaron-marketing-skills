import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN_SPEC = importlib.util.spec_from_file_location(
    "context_plan", ROOT / "scripts" / "context-plan.py"
)
planner = importlib.util.module_from_spec(PLAN_SPEC)
PLAN_SPEC.loader.exec_module(planner)
resolver = planner.resolver
RUN_ID = "123e4567-e89b-42d3-a456-426614174000"
AS_OF = "2026-07-22T12:00:00Z"


class ContextPlanTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "project"
        self.project.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def request(project_root, skill="content-writer", **overrides):
        values = {
            "skill": skill,
            "run_id": RUN_ID,
            "turn_id": "turn-1",
            "as_of": AS_OF,
            "project_root": project_root,
            "bundle_root": ROOT,
        }
        values.update(overrides)
        return planner.build_request(**values)

    @staticmethod
    def write(root, relative, content="fixture\n"):
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def copy_bundle(self, skill):
        bundle = Path(tempfile.mkdtemp(prefix="bundle-%s-" % skill, dir=self.root))
        index = json.loads((ROOT / planner.INDEX_REF).read_text(encoding="utf-8"))
        entry = next(item for item in index["contracts"] if item["skill"] == skill)
        contract = json.loads((ROOT / entry["contract_ref"]).read_text(encoding="utf-8"))
        paths = {
            planner.INDEX_REF,
            entry["contract_ref"],
            index["contract_schema"]["path"],
            index["shared_contract"]["path"],
            index["source_catalog"]["path"],
            contract["identity"]["path"],
            *(item["path"] for item in contract["context_hints"]["bundle_references"]),
            "references/auto-routing/seo-geo.md",
        }
        for relative in paths:
            target = bundle / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, target)
        return bundle, entry, contract

    def copy_bundle_with_skill_version(self, skill, version):
        bundle, entry, contract = self.copy_bundle(skill)
        skill_path = bundle / contract["identity"]["path"]
        lines = skill_path.read_text(encoding="utf-8").splitlines(keepends=True)
        version_lines = [
            offset for offset, line in enumerate(lines)
            if line.startswith("version:")
        ]
        self.assertEqual(1, len(version_lines))
        newline = "\n" if lines[version_lines[0]].endswith("\n") else ""
        lines[version_lines[0]] = 'version: "%s"%s' % (version, newline)
        skill_path.write_text("".join(lines), encoding="utf-8")

        old_skill_sha = contract["identity"]["sha256"]
        new_skill_sha = hashlib.sha256(skill_path.read_bytes()).hexdigest()

        def replace_skill_sha(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    if key == "sha256" and item == old_skill_sha:
                        value[key] = new_skill_sha
                    else:
                        replace_skill_sha(item)
            elif isinstance(value, list):
                for item in value:
                    replace_skill_sha(item)

        replace_skill_sha(contract)
        contract["identity"]["version"] = version
        contract_raw = (
            json.dumps(contract, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        (bundle / entry["contract_ref"]).write_bytes(contract_raw)

        index_path = bundle / planner.INDEX_REF
        index = json.loads(index_path.read_text(encoding="utf-8"))
        selected = next(
            item for item in index["contracts"] if item["skill"] == skill
        )
        selected["contract_sha256"] = hashlib.sha256(contract_raw).hexdigest()
        index_path.write_text(
            json.dumps(index, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return bundle

    def test_host_independent_output_for_equivalent_projects(self):
        other = self.root / "unrelated-absolute-location"
        other.mkdir()
        for project in (self.project, other):
            self.write(project, "memory/hot-cache.md", "same\n")
            self.write(project, "memory/projections/claims.json", "{}\n")
        first = self.request(self.project)
        second = self.request(other)
        self.assertEqual(first, second)
        self.assertEqual(
            first["planner"]["candidate_discovery"]["candidate_set_sha256"],
            resolver.sha256_json(first["candidates"]),
        )
        self.assertNotIn(str(self.project), json.dumps(first))

    def test_full_catalog_plans_with_missing_optional_project_memory(self):
        index = json.loads((ROOT / planner.INDEX_REF).read_text(encoding="utf-8"))
        requests = [self.request(self.project, entry["skill"]) for entry in index["contracts"]]
        self.assertEqual(len(requests), 120)
        self.assertTrue(all(request["planner"]["generator"] == "context-plan-v1"
                            for request in requests))
        self.assertTrue(all(request["candidates"] for request in requests))

    def test_protocol_skill_gets_explicit_auto_routing_shard(self):
        request = self.request(self.project, "consent-registry")
        self.assertEqual(request["route"]["command"], "auto")
        self.assertEqual(
            request["route"]["scenario_shards"], ["references/auto-routing/email.md"]
        )
        shard = [candidate for candidate in request["candidates"]
                 if candidate["role"] == "routing-scenario"]
        self.assertEqual(len(shard), 1)
        self.assertEqual(shard[0]["requirement"], "required")

    def test_explicit_route_reason_is_preserved_and_validated(self):
        request = self.request(self.project, reason_code="user-request")
        self.assertEqual(request["route"]["reason_code"], "user-request")
        with self.assertRaisesRegex(resolver.ContextResolutionError, "reason_code"):
            self.request(self.project, reason_code="unsafe reason")

    def test_skill_and_architecture_versions_are_independent(self):
        fixture_skill_version = "18.0.1"
        bundle = self.copy_bundle_with_skill_version(
            "memory-management", fixture_skill_version
        )
        request = self.request(
            self.project, "memory-management", bundle_root=bundle
        )
        planner.validate_planned_request(request, bundle_root=bundle)
        self.assertEqual(request["route"]["target_skill"], "memory-management")
        manifest = resolver.resolve_context(request, bundle, self.project)
        catalog_version = json.loads(
            (bundle / planner.CATALOG_REF).read_text(encoding="utf-8")
        )["architecture_version"]
        self.assertEqual(
            manifest["route"]["skill_version"], fixture_skill_version
        )
        self.assertEqual(
            manifest["route"]["catalog_version"], catalog_version
        )
        self.assertNotEqual(
            manifest["route"]["skill_version"],
            manifest["route"]["catalog_version"],
        )

    def test_project_prefix_discovery_is_closed_and_deterministic(self):
        self.write(self.project, "memory/channels/z.md", "z\n")
        self.write(self.project, "memory/channels/a.md", "a\n")
        request = self.request(self.project, "social-calendar-builder")
        paths = [item["path"] for item in request["candidates"] if item["scope"] == "project"]
        self.assertIn("memory/channels/a.md", paths)
        self.assertIn("memory/channels/z.md", paths)
        self.assertEqual(paths, sorted(paths))
        outcomes = request["planner"]["candidate_discovery"]["prefix_outcomes"]
        channel = next(item for item in outcomes if item["path"] == "memory/channels")
        self.assertEqual(channel, {
            "path": "memory/channels", "status": "enumerated",
            "file_count": 2, "reason_code": None,
        })
        with self.assertRaisesRegex(planner.ContextPlanError, "prefix_file_limit"):
            self.request(self.project, "social-calendar-builder", prefix_file_limit=1)

    def test_missing_prefix_is_typed_unresolved_and_symlink_fails_closed(self):
        request = self.request(self.project, "social-calendar-builder")
        outcomes = request["planner"]["candidate_discovery"]["prefix_outcomes"]
        self.assertTrue(outcomes)
        self.assertTrue(all(item["status"] == "unresolved" for item in outcomes))
        self.assertTrue(all(item["reason_code"] == "missing-prefix" for item in outcomes))

        external = self.write(self.root, "external.md")
        channel = self.project / "memory/channels"
        channel.mkdir(parents=True)
        (channel / "unsafe.md").symlink_to(external)
        with self.assertRaisesRegex(planner.ContextPlanError, "symlink"):
            self.request(self.project, "social-calendar-builder")

    def test_missing_optional_project_files_are_explicit_not_host_discovered(self):
        request = self.request(self.project)
        hot = next(item for item in request["candidates"]
                   if item["path"] == "memory/hot-cache.md")
        self.assertEqual(hot["requirement"], "optional")
        self.assertIsNone(hot["expected_sha256"])
        self.assertFalse((self.project / "memory").exists())

    def test_malformed_contract_and_missing_reference_fail_closed(self):
        bundle, entry, contract = self.copy_bundle("content-writer")
        contract.pop("completion_contract")
        contract_raw = (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode("utf-8")
        (bundle / entry["contract_ref"]).write_bytes(contract_raw)
        index_path = bundle / planner.INDEX_REF
        index = json.loads(index_path.read_text(encoding="utf-8"))
        selected = next(item for item in index["contracts"] if item["skill"] == "content-writer")
        selected["contract_sha256"] = hashlib.sha256(contract_raw).hexdigest()
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(planner.ContextPlanError, "missing fields"):
            self.request(self.project, bundle_root=bundle)

        bundle, _entry, contract = self.copy_bundle("content-writer")
        reference = contract["context_hints"]["bundle_references"][0]["path"]
        (bundle / reference).unlink()
        with self.assertRaises(resolver.ContextSourceMissing):
            self.request(self.project, bundle_root=bundle)

    def test_malformed_clause_span_fails_closed(self):
        bundle, entry, contract = self.copy_bundle("content-writer")
        contract["input_contract"]["clauses"][0]["source"]["end_char"] += 1
        contract_raw = (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode("utf-8")
        (bundle / entry["contract_ref"]).write_bytes(contract_raw)
        index_path = bundle / planner.INDEX_REF
        index = json.loads(index_path.read_text(encoding="utf-8"))
        selected = next(item for item in index["contracts"] if item["skill"] == "content-writer")
        selected["contract_sha256"] = hashlib.sha256(contract_raw).hexdigest()
        index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(planner.ContextPlanError, "source span"):
            self.request(self.project, bundle_root=bundle)

    def test_tampered_candidate_set_and_provenance_are_rejected(self):
        request = self.request(self.project)
        tampered = copy.deepcopy(request)
        tampered["candidates"][0]["priority"] -= 1
        with self.assertRaisesRegex(planner.ContextPlanError, "candidate_set_sha256"):
            planner.validate_planned_request(tampered, bundle_root=ROOT)
        tampered = copy.deepcopy(request)
        tampered["planner"]["skill_contract"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(planner.ContextPlanError, "live bundle"):
            planner.validate_planned_request(tampered, bundle_root=ROOT)

    def test_resolver_accepts_planner_request_and_embeds_it_without_ledger_write(self):
        request = self.request(self.project)
        before = sorted(path.relative_to(self.project) for path in self.project.rglob("*"))
        manifest = resolver.resolve_context(request, ROOT, self.project)
        after = sorted(path.relative_to(self.project) for path in self.project.rglob("*"))
        self.assertEqual(manifest["request"]["planner"], request["planner"])
        self.assertEqual(before, after)

    def test_schema_request_shapes_both_expose_optional_planner(self):
        request_schema = json.loads(
            (ROOT / "references/context-request.schema.json").read_text(encoding="utf-8")
        )
        manifest_schema = json.loads(
            (ROOT / "references/context-manifest.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            request_schema["properties"]["planner"], {"$ref": "#/$defs/planner"}
        )
        self.assertEqual(
            manifest_schema["$defs"]["request"]["properties"]["planner"],
            {"$ref": "#/$defs/planner"},
        )


if __name__ == "__main__":
    unittest.main()
