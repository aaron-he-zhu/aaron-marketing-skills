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
        if contract.get("control_requirements"):
            paths.add(contract["provenance"]["control_bindings"]["path"])
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

    @staticmethod
    def rehash_candidates(request):
        request["candidates"].sort(
            key=lambda item: (item["scope"], item["path"], item["resource_id"])
        )
        request["planner"]["candidate_discovery"]["candidate_set_sha256"] = (
            resolver.sha256_json(request["candidates"])
        )

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
        self.assertTrue(all(request["planner"]["generator"] == "context-plan-v1.1"
                            for request in requests))
        self.assertTrue(all(request["candidates"] for request in requests))

    def test_control_bindings_are_validated_without_schema_context_injection(self):
        bound = self.request(self.project, "campaign-planner")
        unbound = self.request(self.project, "technical-seo-checker")
        bound_controls = [
            item for item in bound["candidates"]
            if item["path"] == planner.CONTROL_ARTIFACT_SCHEMA_REF
        ]
        unbound_controls = [
            item for item in unbound["candidates"]
            if item["path"] == planner.CONTROL_ARTIFACT_SCHEMA_REF
        ]
        self.assertEqual([], bound_controls)
        self.assertEqual([], unbound_controls)
        self.assertFalse(any(
            item["path"] == planner.CONTROL_BINDINGS_REF
            for item in bound["candidates"]
        ))

    def test_context_plan_rejects_invalid_handoffs_without_loading_graph_or_schema(self):
        bindings = json.loads(
            (ROOT / planner.CONTROL_BINDINGS_REF).read_text(encoding="utf-8")
        )
        edge_id = "campaign-planner--performance-analyzer"
        bindings["handoff_requirements"][edge_id] = list(reversed(
            bindings["handoff_requirements"][edge_id]
        ))
        with self.assertRaisesRegex(
                resolver.ContextResolutionError,
                "requirements are invalid or not sorted"):
            planner._validate_control_handoff_requirements(bindings)

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

    def test_post_route_protocol_assembly_has_no_answer_shard(self):
        bundle, _entry, _contract = self.copy_bundle("memory-management")
        request = self.request(
            self.project, "memory-management", command="auto", post_route=True,
            bundle_root=bundle,
        )
        self.assertEqual("auto", request["route"]["command"])
        self.assertEqual([], request["route"]["scenario_shards"])
        self.assertFalse(
            any(item["role"] == "routing-scenario" for item in request["candidates"])
        )

    def test_nonprotocol_auto_without_shard_fails_closed(self):
        bundle, _entry, _contract = self.copy_bundle("content-writer")
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "discipline is absent"):
            self.request(
                self.project, "content-writer", command="auto", post_route=True,
                bundle_root=bundle,
            )

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

    def test_exact_bundle_closure_rejects_rehashed_omission_extra_and_field_tampering(self):
        bundle, entry, _contract = self.copy_bundle("entity-registry")
        request = self.request(
            self.project, "entity-registry", bundle_root=bundle,
        )
        required_runtime_reads = {
            item["path"] for item in request["candidates"]
            if item["requirement"] == "required"
            and item["reason_code"] == "explicit-runtime-read"
        }
        self.assertTrue({
            "references/registry-event-protocol.md",
            "references/runtime-invocation.md",
            "references/entity-geo-handoff-schema.md",
        }.issubset(required_runtime_reads))
        planner.validate_planned_request(
            request, bundle_root=bundle, project_root=self.project,
            resolve_sources=True,
        )

        def omit_runtime(value):
            value["candidates"] = [
                item for item in value["candidates"]
                if item["path"] != "references/runtime-invocation.md"
            ]

        def add_valid_extra(value):
            path = json.loads(
                (bundle / planner.INDEX_REF).read_text(encoding="utf-8")
            )["contract_schema"]["path"]
            raw = (bundle / path).read_bytes()
            value["candidates"].append(planner._candidate(
                "bundle", path, "skill-reference", "optional", "approved",
                value["as_of"], 1, "authored-reference", "public",
                hashlib.sha256(raw).hexdigest(), load_policy="lookup",
            ))

        def remove_optional_hash(value):
            item = next(candidate for candidate in value["candidates"] if (
                candidate["scope"] == "bundle"
                and candidate["requirement"] == "optional"
                and candidate["expected_sha256"] is not None
            ))
            item["expected_sha256"] = None

        def change_load_policy(value):
            item = next(candidate for candidate in value["candidates"] if (
                candidate["path"] == "references/runtime-invocation.md"
            ))
            item["load_policy"] = "lookup"

        for label, mutation in (
                ("required omission", omit_runtime),
                ("extra valid candidate", add_valid_extra),
                ("expected hash removal", remove_optional_hash),
                ("load policy change", change_load_policy)):
            with self.subTest(label=label):
                tampered = copy.deepcopy(request)
                mutation(tampered)
                self.rehash_candidates(tampered)
                with self.assertRaisesRegex(
                        planner.ContextPlanError, "bundle candidate closure"):
                    planner.validate_planned_request(
                        tampered, bundle_root=bundle, project_root=self.project,
                        resolve_sources=True,
                    )

        direct = copy.deepcopy(request)
        omit_runtime(direct)
        self.rehash_candidates(direct)
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "planner candidate closure"):
            resolver.resolve_context(direct, bundle, self.project)

    def test_exact_auditor_closure_rejects_rehashed_condition_swap(self):
        bundle, _entry, _contract = self.copy_bundle("narrative-quality-auditor")
        request = self.request(
            self.project, "narrative-quality-auditor", bundle_root=bundle,
        )
        branches = [
            item for item in request["candidates"]
            if item.get("exclusive_group") == planner.AUDITOR_EXCLUSIVE_GROUP
        ]
        fallback = next(
            item for item in branches if item["load_policy"] == "fallback"
        )
        root_chain = next(
            item for item in branches
            if item["path"] == "references/auditor-runbook.md"
        )
        fallback["condition_code"], root_chain["condition_code"] = (
            root_chain["condition_code"], fallback["condition_code"]
        )
        self.rehash_candidates(request)
        # The generic branch-set shape remains valid; exact machine-contract
        # reconstruction must still reject the semantic branch swap.
        resolver.validate_request(request)
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "planner candidate closure"):
            resolver.resolve_context(request, bundle, self.project)

    def test_post_route_provenance_rejects_rehashed_shard_removal_and_injection(self):
        bundle, _entry, _contract = self.copy_bundle("memory-management")
        pre_route = self.request(
            self.project, "memory-management", bundle_root=bundle,
            command="auto", post_route=False,
        )
        post_route = self.request(
            self.project, "memory-management", bundle_root=bundle,
            command="auto", post_route=True,
        )
        shard_candidate = next(
            item for item in pre_route["candidates"]
            if item["role"] == "routing-scenario"
        )

        removed = copy.deepcopy(pre_route)
        removed["route"]["scenario_shards"] = []
        removed["candidates"] = [
            item for item in removed["candidates"]
            if item["role"] != "routing-scenario"
        ]
        self.rehash_candidates(removed)
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "post_route"):
            resolver.resolve_context(removed, bundle, self.project)

        injected = copy.deepcopy(post_route)
        injected["route"]["scenario_shards"] = [shard_candidate["path"]]
        injected["candidates"].append(copy.deepcopy(shard_candidate))
        self.rehash_candidates(injected)
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "post_route"):
            resolver.resolve_context(injected, bundle, self.project)

    def test_resolver_accepts_planner_request_and_embeds_it_without_ledger_write(self):
        request = self.request(self.project)
        before = sorted(path.relative_to(self.project) for path in self.project.rglob("*"))
        manifest = resolver.resolve_context(request, ROOT, self.project)
        after = sorted(path.relative_to(self.project) for path in self.project.rglob("*"))
        self.assertEqual(manifest["request"]["planner"], request["planner"])
        self.assertEqual(before, after)

    def test_all_auditors_select_exactly_one_distribution_runtime_chain(self):
        catalog = json.loads((ROOT / planner.CATALOG_REF).read_text(encoding="utf-8"))
        self.assertEqual(8, len(catalog["auditors"]))
        for auditor in catalog["auditors"]:
            bundle, _entry, _contract = self.copy_bundle(auditor["skill"])
            fallback = "%s/references/auditor-runtime.md" % auditor["path"]
            for profile, expected_branch in (
                    ("repository", "repository-or-plugin"),
                    ("plugin", "repository-or-plugin"),
                    ("standalone-skill", "standalone-skill")):
                with self.subTest(skill=auditor["skill"], profile=profile):
                    request = self.request(
                        self.project, auditor["skill"], distribution_profile=profile,
                        bundle_root=bundle,
                    )
                    self.assertEqual(profile, request["planner"]["distribution_profile"])
                    branches = [
                        item for item in request["candidates"]
                        if item.get("exclusive_group") == planner.AUDITOR_EXCLUSIVE_GROUP
                    ]
                    self.assertEqual(
                        {"repository-or-plugin", "standalone-skill"},
                        {item["condition_code"] for item in branches},
                    )
                    manifest = resolver.resolve_context(request, bundle, self.project)
                    selected = {item["resource_id"] for item in manifest["resources"]}
                    omitted = {
                        item["resource_id"]: item["reason_code"]
                        for item in manifest["omitted"]
                    }
                    selected_branches = {
                        item["condition_code"] for item in branches
                        if item["resource_id"] in selected
                    }
                    self.assertEqual({expected_branch}, selected_branches)
                    for item in branches:
                        if item["condition_code"] != expected_branch:
                            self.assertEqual(
                                "condition-not-met", omitted[item["resource_id"]]
                            )
                    fallback_candidate = next(
                        item for item in branches if item["path"] == fallback
                    )
                    self.assertEqual("fallback", fallback_candidate["load_policy"])
                    self.assertEqual(
                        profile == "standalone-skill",
                        fallback_candidate["resource_id"] in selected,
                    )

    def test_incomplete_auditor_exclusive_group_fails_closed(self):
        bundle, _entry, _contract = self.copy_bundle("narrative-quality-auditor")
        request = self.request(
            self.project, "narrative-quality-auditor", bundle_root=bundle,
        )
        request["candidates"] = [
            item for item in request["candidates"]
            if item.get("condition_code") != "standalone-skill"
        ]
        request["planner"]["candidate_discovery"]["candidate_set_sha256"] = (
            resolver.sha256_json(request["candidates"])
        )
        with self.assertRaisesRegex(
                resolver.ContextResolutionError, "must declare repository/plugin and standalone"):
            resolver.validate_request(request)

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
        self.assertEqual(
            {"repository", "plugin", "standalone-skill"},
            set(request_schema["$defs"]["planner"]["properties"]
                ["distribution_profile"]["enum"]),
        )
        for schema in (request_schema, manifest_schema):
            planner_schema = schema["$defs"]["planner"]
            self.assertIn("post_route", planner_schema["required"])
            self.assertEqual(
                {"type": "boolean"}, planner_schema["properties"]["post_route"]
            )


if __name__ == "__main__":
    unittest.main()
