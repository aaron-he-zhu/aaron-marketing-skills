import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = load_module("context_assembly_test_planner", ROOT / "scripts" / "context-plan.py")
assembly = load_module(
    "context_assembly_under_test", ROOT / "scripts" / "context-assembly.py"
)


class ContextAssemblyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        cls.bundle = cls.root / "bundle"
        shutil.copytree(
            ROOT,
            cls.bundle,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        cls.project = cls.root / "project"
        cls.project.mkdir()
        cls.request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174000",
            turn_id="turn-assembly",
            as_of="2026-08-01T00:00:00Z",
            project_root=cls.project,
            bundle_root=cls.bundle,
            distribution_profile="repository",
        )
        cls.manifest = planner.resolver.resolve_context(
            cls.request, cls.bundle, cls.project
        )
        cls.standalone_request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174010",
            turn_id="turn-assembly-standalone",
            as_of="2026-08-01T00:00:00Z",
            project_root=cls.project,
            bundle_root=cls.bundle,
            distribution_profile="standalone-skill",
            post_route=True,
        )
        cls.standalone_manifest = planner.resolver.resolve_context(
            cls.standalone_request, cls.bundle, cls.project
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def build(self, **overrides):
        values = {
            "bundle_root": self.bundle,
            "project_root": self.project,
            "host_profile": "claude-code-plugin-host",
            "model_id": "test/model-1",
            "as_of": "2026-08-01T00:00:00Z",
            "verify_sources": True,
        }
        values.update(overrides)
        return assembly.build_assembly(self.manifest, **values)

    def build_for_host(self, host_profile, **overrides):
        values = {
            "bundle_root": self.bundle,
            "project_root": self.project,
            "host_profile": host_profile,
            "model_id": "test/model-1",
            "as_of": "2026-08-01T00:00:00Z",
            "verify_sources": True,
        }
        values.update(overrides)
        manifest = (
            self.standalone_manifest
            if host_profile == "standalone-skill-host"
            else self.manifest
        )
        if host_profile == "standalone-skill-host":
            values.setdefault("distribution_evaluation_only", True)
            values.setdefault(
                "evaluation_run_id", "repository-standalone-projection"
            )
        return assembly.build_assembly(manifest, **values)

    def physical_bundle(self, *, kind="plugin", profile="governed",
                        host_profile="claude-code-plugin-host"):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        bundle = Path(temporary.name) / "bundle"
        if kind == "plugin":
            completed = subprocess.run(
                [
                    sys.executable,
                    str(self.bundle / "scripts/build-distribution.py"),
                    "--plugin", "--profile", profile,
                    "--host-profile", host_profile,
                    "--output", str(bundle),
                ],
                cwd=self.bundle,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            if completed.returncode != 0:
                self.fail("plugin build failed: %s" % completed.stderr)
            return bundle
        shutil.copytree(self.bundle, bundle)
        files = []
        for relative in assembly.TRUSTED_DISTRIBUTION_FILES:
            raw = (bundle / relative).read_bytes()
            files.append({
                "bytes": len(raw), "mode": "0644", "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
        files.sort(key=lambda item: item["path"])
        manifest = {
            "schema_version": "1.2",
            "kind": kind,
            "profile": profile,
            "capability_ceiling": profile,
            "capabilities": [],
            "catalog_sha256": "0" * 64,
            "profile_definition_sha256": "1" * 64,
            "host_profile": host_profile,
            "host_capabilities": [],
            "host_profile_catalog_sha256": "2" * 64,
            "host_profile_definition_sha256": "3" * 64,
            "routing_surface": (
                "direct-skill" if host_profile == "standalone-skill-host"
                else "slash-commands"
            ),
            "reference_surface": (
                "skill-local-only" if host_profile == "standalone-skill-host"
                else "shared-root"
            ),
            "connector_surface": (
                "none" if host_profile == "standalone-skill-host"
                else "native-plugin"
            ),
            "routing_sidecar": None,
            "package_ceiling": {"max_files": 560, "max_bytes": 6500000},
            "hash_algorithm": "sha256",
            "manifest_path": "distribution-manifest.json",
            "manifest_excludes": ["distribution-manifest.json"],
            "source": {"repository": None, "commit": None},
            "files_sha256": hashlib.sha256((json.dumps(
                files, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
            ) + "\n").encode("utf-8")).hexdigest(),
            "files": files,
        }
        (bundle / "distribution-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, allow_nan=False,
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return bundle

    def test_explicit_profile_separates_controller_model_and_deferred_context(self):
        result = self.build()
        self.assertTrue(result["deployment_eligible"])
        self.assertEqual("explicit", result["profile"]["prompt_profile"])
        controller_roles = {item["role"] for item in result["consumers"]["controller"]}
        model_roles = {item["role"] for item in result["consumers"]["model"]}
        self.assertIn("skill-contract", controller_roles)
        self.assertIn("shared-contract", controller_roles)
        self.assertIn("skill-definition", model_roles)
        self.assertIn("shared-contract", model_roles)
        self.assertNotIn("skill-contract", model_roles)
        self.assertGreater(len(result["consumers"]["deferred"]), 0)
        self.assertLess(
            result["usage"]["model_body_bytes"],
            result["usage"]["manifest_selected_bytes"],
        )
        self.assertEqual(0, result["usage"]["model_reduction_bytes"])

    def test_host_profile_matrix_keeps_explicit_deployable_and_compact_eval_exact(self):
        expected_compact_support = {
            "standalone-skill-host": False,
            "generic-shared-root-host": True,
            "claude-code-plugin-host": True,
        }
        for host_profile, compact_supported in expected_compact_support.items():
            with self.subTest(host_profile=host_profile, prompt_profile="explicit"):
                explicit = self.build_for_host(
                    host_profile, requested_prompt_profile="explicit"
                )
                self.assertEqual(
                    host_profile != "standalone-skill-host",
                    explicit["deployment_eligible"],
                )
                self.assertEqual(
                    (host_profile, "explicit"),
                    (
                        explicit["profile"]["host_profile"],
                        explicit["profile"]["prompt_profile"],
                    ),
                )

            for prompt_profile in ("balanced", "lean"):
                with self.subTest(
                    host_profile=host_profile,
                    prompt_profile=prompt_profile,
                    mode="evaluation",
                ):
                    if compact_supported:
                        compact = self.build_for_host(
                            host_profile,
                            evaluation_prompt_profile=prompt_profile,
                            evaluation_run_id="matrix-%s-%s"
                            % (host_profile, prompt_profile),
                        )
                        self.assertFalse(compact["deployment_eligible"])
                        self.assertEqual(
                            prompt_profile, compact["profile"]["prompt_profile"]
                        )
                    else:
                        with self.assertRaisesRegex(
                            assembly.ContextAssemblyError,
                            "cannot authorize a compact prompt profile",
                        ):
                            self.build_for_host(
                                host_profile,
                                evaluation_prompt_profile=prompt_profile,
                                evaluation_run_id="matrix-%s-%s"
                                % (host_profile, prompt_profile),
                            )

                with self.subTest(
                    host_profile=host_profile,
                    prompt_profile=prompt_profile,
                    mode="deployment",
                ):
                    with self.assertRaisesRegex(
                        assembly.ContextAssemblyError,
                        ("explicit prompt profile"
                         if host_profile == "standalone-skill-host"
                         else "UNCERTIFIED"),
                    ):
                        self.build_for_host(
                            host_profile, requested_prompt_profile=prompt_profile
                        )

    def test_standalone_explicit_embedded_policy_is_counted_once(self):
        result = self.build_for_host(
            "standalone-skill-host", requested_prompt_profile="explicit"
        )
        self.assertFalse(result["deployment_eligible"])
        self.assertEqual(
            {
                "physical_distribution_kind": "repository",
                "planner_distribution_profile": "standalone-skill",
                "distribution_evaluation_only": True,
            },
            {key: result["profile"][key] for key in (
                "physical_distribution_kind", "planner_distribution_profile",
                "distribution_evaluation_only",
            )},
        )
        self.assertEqual(
            "evaluation-only-distribution-projection",
            result["profile"]["prompt_profile_source"],
        )
        selected_skill = next(
            item for item in self.standalone_manifest["resources"]
            if item["role"] == "skill-definition"
        )
        model = result["consumers"]["model"]
        model_skill = [
            item for item in model
            if item["source_resource_id"] == selected_skill["resource_id"]
        ]
        self.assertEqual(1, len(model_skill))
        self.assertEqual("model-skill-explicit", model_skill[0]["module_id"])
        self.assertEqual(selected_skill["bytes"], model_skill[0]["body_bytes"])
        self.assertEqual(selected_skill["bytes"], result["usage"]["model_body_bytes"])
        self.assertEqual(0, result["usage"]["model_reduction_bytes"])
        self.assertEqual(0, result["usage"]["model_reduction_ratio"])
        projected_paths = {
            item["path"]
            for consumer in result["consumers"].values()
            for item in consumer
        }
        self.assertNotIn("references/skill-contract.md", projected_paths)
        self.assertNotIn(
            "references/skill-contracts/content-writer.json", projected_paths
        )
        self.assertNotIn("CONNECTORS.md", projected_paths)

    def test_uncertified_compact_profile_cannot_be_deployed(self):
        with self.assertRaises(assembly.ContextAssemblyError) as raised:
            self.build(requested_prompt_profile="balanced")
        self.assertIn("UNCERTIFIED", str(raised.exception))

    def test_balanced_evaluation_keeps_full_skill_and_replaces_only_policy(self):
        result = self.build(
            evaluation_prompt_profile="balanced",
            evaluation_run_id="ablation-001",
        )
        self.assertFalse(result["deployment_eligible"])
        self.assertEqual("ablation-001", result["evaluation_run_id"])
        self.assertEqual("balanced", result["profile"]["prompt_profile"])
        self.assertEqual(
            "evaluation-only-uncertified",
            result["profile"]["prompt_profile_source"],
        )
        model_paths = {item["path"] for item in result["consumers"]["model"]}
        self.assertIn("references/policy-kernel.md", model_paths)
        self.assertIn("seo-geo/implement/content-writer/SKILL.md", model_paths)
        self.assertNotIn(
            "references/skill-capsules/content-writer.json", model_paths
        )
        self.assertNotIn("references/skill-contract.md", model_paths)
        self.assertEqual(1, len(result["replacements"]))
        self.assertEqual(
            "certified-policy-kernel", result["replacements"][0]["reason_code"]
        )
        self.assertGreater(result["usage"]["model_reduction_ratio"], 0.20)
        self.assertLess(result["usage"]["model_reduction_ratio"], 0.55)
        self.assertGreater(result["usage"]["model_reduction_bytes"], 0)

    def test_lean_evaluation_uses_capsule_kernel_and_distinct_context(self):
        balanced = self.build(
            evaluation_prompt_profile="balanced",
            evaluation_run_id="ablation-balanced-compare",
        )
        result = self.build(
            evaluation_prompt_profile="lean",
            evaluation_run_id="ablation-lean-001",
        )
        self.assertFalse(result["deployment_eligible"])
        self.assertEqual("lean", result["profile"]["prompt_profile"])
        self.assertEqual(
            list(assembly.profile_resolver.ALWAYS_ON_OVERLAYS),
            result["profile"]["always_on_overlays"],
        )
        kernel = next(
            item for item in result["consumers"]["model"]
            if item["role"] == "policy-kernel"
        )
        self.assertEqual(kernel["bytes"], kernel["body_bytes"])
        model_paths = {item["path"] for item in result["consumers"]["model"]}
        self.assertIn("references/skill-capsules/content-writer.json", model_paths)
        self.assertNotIn("seo-geo/implement/content-writer/SKILL.md", model_paths)
        self.assertEqual(2, len(result["replacements"]))
        self.assertGreater(
            result["usage"]["model_reduction_ratio"],
            balanced["usage"]["model_reduction_ratio"],
        )
        self.assertNotEqual(
            result["assembly_signature"], balanced["assembly_signature"]
        )

    def test_evaluation_requires_a_bounded_run_identity(self):
        with self.assertRaisesRegex(assembly.ContextAssemblyError, "evaluation_run_id"):
            self.build(evaluation_prompt_profile="balanced")

    def test_profile_and_module_catalog_hashes_are_bound(self):
        result = self.build()
        self.assertEqual("repository", result["profile"]["distribution_profile"])
        self.assertIsNone(result["profile"]["distribution_manifest_sha256"])
        self.assertIsNone(result["profile"]["model_revision"])
        catalogs = result["profile"]["catalogs"]
        self.assertEqual(
            {
                "host_sha256",
                "prompt_sha256",
                "context_modules_sha256",
            },
            set(catalogs),
        )
        self.assertTrue(all(len(value) == 64 for value in catalogs.values()))
        schema = json.loads(
            (ROOT / "references/context-assembly.schema.json").read_text(
                encoding="utf-8"
            )
        )
        profile_schema = schema["properties"]["profile"]
        for field in (
                "physical_distribution_kind", "planner_distribution_profile",
                "distribution_evaluation_only"):
            self.assertIn(field, profile_schema["required"])
        self.assertEqual(
            {"repository", "plugin"},
            set(profile_schema["properties"]["physical_distribution_kind"]["enum"]),
        )

    def test_built_distribution_identity_is_manifest_derived_and_hash_anchored(self):
        bundle = self.physical_bundle()
        manifest_raw = (bundle / "distribution-manifest.json").read_bytes()
        identity = assembly._distribution_identity(
            bundle, "claude-code-plugin-host"
        )
        manifest = json.loads(manifest_raw.decode("utf-8"))
        self.assertTrue(
            set(assembly.TRUSTED_DISTRIBUTION_FILES).issubset({
                item["path"] for item in manifest["files"]
            })
        )
        self.assertEqual("governed", identity["profile"])
        self.assertEqual(hashlib.sha256(manifest_raw).hexdigest(), identity["manifest_sha256"])
        with self.assertRaisesRegex(assembly.ContextAssemblyError, "authorize this host"):
            assembly._distribution_identity(bundle, "generic-shared-root-host")
        (bundle / "scripts/context-profile-resolver.py").write_text("tampered\n")
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "complete manifest inventory"):
            assembly._distribution_identity(bundle, "claude-code-plugin-host")

    def test_plugin_identity_rejects_missing_and_extra_physical_inventory(self):
        extra_bundle = self.physical_bundle()
        (extra_bundle / "unexpected-extra.txt").write_text(
            "not in manifest\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "complete manifest inventory"):
            assembly._distribution_identity(
                extra_bundle, "claude-code-plugin-host"
            )

        missing_bundle = self.physical_bundle()
        manifest_path = missing_bundle / "distribution-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        trusted = set(assembly.TRUSTED_DISTRIBUTION_FILES)
        removed = next(
            item for item in manifest["files"] if item["path"] not in trusted
        )
        manifest["files"] = [
            item for item in manifest["files"] if item is not removed
        ]
        manifest["files_sha256"] = hashlib.sha256((json.dumps(
            manifest["files"], ensure_ascii=False, allow_nan=False,
            indent=2, sort_keys=True
        ) + "\n").encode("utf-8")).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, allow_nan=False,
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "complete manifest inventory"):
            assembly._distribution_identity(
                missing_bundle, "claude-code-plugin-host"
            )

        mismatched_runtime_bundle = self.physical_bundle()
        runtime_path = mismatched_runtime_bundle / "scripts/context-resolver.py"
        runtime_path.write_bytes(runtime_path.read_bytes() + b"\n# mismatched runtime\n")
        manifest_path = mismatched_runtime_bundle / "distribution-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        runtime_raw = runtime_path.read_bytes()
        descriptor = next(
            item for item in manifest["files"]
            if item["path"] == "scripts/context-resolver.py"
        )
        descriptor["bytes"] = len(runtime_raw)
        descriptor["sha256"] = hashlib.sha256(runtime_raw).hexdigest()
        manifest["files_sha256"] = hashlib.sha256((json.dumps(
            manifest["files"], ensure_ascii=False, allow_nan=False,
            indent=2, sort_keys=True
        ) + "\n").encode("utf-8")).hexdigest()
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, allow_nan=False,
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "executing runtime"):
            assembly._distribution_identity(
                mismatched_runtime_bundle, "claude-code-plugin-host"
            )

        relabeled_host_bundle = self.physical_bundle()
        manifest_path = relabeled_host_bundle / "distribution-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["host_profile"] = "generic-shared-root-host"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, allow_nan=False,
                       indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "typed host catalog"):
            assembly._distribution_identity(
                relabeled_host_bundle, "generic-shared-root-host"
            )

    def test_distribution_matrix_binds_physical_package_planner_and_resolved_host(self):
        common = {
            "bundle_root": self.bundle,
            "project_root": self.project,
            "model_id": "test/model-1",
            "as_of": "2026-08-01T00:00:00Z",
            "verify_sources": True,
        }
        # Repository + shared host requires repository planner provenance.
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner distribution profile"):
            assembly.build_assembly(
                self.standalone_manifest,
                host_profile="claude-code-plugin-host", **common
            )
        # Neither repository planner nor standalone planner may silently turn a
        # repository checkout into a deployable standalone package.
        for manifest in (self.manifest, self.standalone_manifest):
            with self.subTest(planner=manifest["request"]["planner"][
                    "distribution_profile"]):
                with self.assertRaisesRegex(
                        assembly.ContextAssemblyError,
                        "planner distribution profile"):
                    assembly.build_assembly(
                        manifest, host_profile="standalone-skill-host",
                        requested_prompt_profile="explicit", **common
                    )

        # `auto` resolves to standalone; that result is subject to the same
        # matrix instead of being compared with the raw string "auto".
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner distribution profile"):
            assembly.build_assembly(
                self.manifest, host_profile="auto", **common
            )
        projected = assembly.build_assembly(
            self.standalone_manifest,
            host_profile="auto",
            requested_prompt_profile="explicit",
            evaluation_run_id="auto-standalone-projection",
            distribution_evaluation_only=True,
            **common,
        )
        self.assertEqual("standalone-skill-host", projected["profile"]["host_profile"])
        self.assertFalse(projected["deployment_eligible"])

    def test_repository_standalone_projection_cannot_authorize_compact_or_deployment(self):
        common = {
            "bundle_root": self.bundle,
            "project_root": self.project,
            "host_profile": "standalone-skill-host",
            "model_id": "test/model-1",
            "as_of": "2026-08-01T00:00:00Z",
            "verify_sources": True,
            "distribution_evaluation_only": True,
            "evaluation_run_id": "projection-negative",
        }
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "compact prompt profile"):
            assembly.build_assembly(
                self.standalone_manifest,
                evaluation_prompt_profile="balanced", **common
            )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "explicit prompt profile"):
            assembly.build_assembly(
                self.standalone_manifest,
                requested_prompt_profile="balanced", **common
            )

        result = assembly.build_assembly(
            self.standalone_manifest,
            requested_prompt_profile="explicit", **common
        )
        forged = copy.deepcopy(result)
        forged["deployment_eligible"] = True
        forged["evaluation_run_id"] = None
        payload = dict(forged)
        payload.pop("assembly_signature")
        forged["assembly_signature"] = hashlib.sha256(
            assembly._canonical_json(payload).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "evaluation-only"):
            assembly.validate_assembly(forged)

        forged_physical = copy.deepcopy(result)
        forged_physical["profile"].update({
            "physical_distribution_kind": "standalone-skill",
            "distribution_profile": "lite",
            "distribution_manifest_sha256": "a" * 64,
            "distribution_evaluation_only": False,
            "prompt_profile_source": "host-default",
        })
        forged_physical["deployment_eligible"] = True
        forged_physical["evaluation_run_id"] = None
        payload = dict(forged_physical)
        payload.pop("assembly_signature")
        forged_physical["assembly_signature"] = hashlib.sha256(
            assembly._canonical_json(payload).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "physical distribution kind"):
            assembly.validate_assembly(forged_physical)

    def test_plugin_matrix_requires_plugin_planner_and_explicit_matching_host(self):
        bundle = self.physical_bundle()
        request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174020",
            turn_id="turn-plugin-matrix",
            as_of="2026-08-01T00:00:00Z",
            project_root=self.project,
            bundle_root=bundle,
            distribution_profile="plugin",
        )
        manifest = planner.resolver.resolve_context(request, bundle, self.project)
        common = {
            "bundle_root": bundle,
            "project_root": self.project,
            "model_id": "test/model-1",
            "as_of": "2026-08-01T00:00:00Z",
            "verify_sources": True,
        }
        result = assembly.build_assembly(
            manifest, host_profile="claude-code-plugin-host", **common
        )
        self.assertEqual("plugin", result["profile"]["physical_distribution_kind"])
        self.assertEqual("plugin", result["profile"]["planner_distribution_profile"])
        self.assertTrue(result["deployment_eligible"])

        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "resolved host differs"):
            assembly.build_assembly(manifest, host_profile="auto", **common)
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner distribution profile"):
            assembly.build_assembly(
                self.manifest, host_profile="claude-code-plugin-host", **common
            )

        generic_bundle = self.physical_bundle(
            host_profile="generic-shared-root-host"
        )
        generic_request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174022",
            turn_id="turn-generic-plugin-matrix",
            as_of="2026-08-01T00:00:00Z",
            project_root=self.project,
            bundle_root=generic_bundle,
            distribution_profile="plugin",
        )
        generic_manifest = planner.resolver.resolve_context(
            generic_request, generic_bundle, self.project
        )
        generic = assembly.build_assembly(
            generic_manifest,
            bundle_root=generic_bundle,
            project_root=self.project,
            host_profile="generic-shared-root-host",
            model_id="test/model-1",
            as_of="2026-08-01T00:00:00Z",
            verify_sources=True,
        )
        self.assertEqual(
            ("plugin", "plugin", "generic-shared-root-host"),
            (
                generic["profile"]["physical_distribution_kind"],
                generic["profile"]["planner_distribution_profile"],
                generic["profile"]["host_profile"],
            ),
        )

    def test_self_signed_fake_standalone_manifest_cannot_become_deployable(self):
        bundle = self.physical_bundle(
            kind="standalone-skill", profile="lite",
            host_profile="standalone-skill-host",
        )
        request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174021",
            turn_id="turn-fake-standalone",
            as_of="2026-08-01T00:00:00Z",
            project_root=self.project,
            bundle_root=bundle,
            distribution_profile="standalone-skill",
        )
        manifest = planner.resolver.resolve_context(request, bundle, self.project)
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError,
                "physical standalone packages do not carry"):
            assembly.build_assembly(
                manifest,
                bundle_root=bundle,
                project_root=self.project,
                host_profile="standalone-skill-host",
                model_id="test/model-1",
                requested_prompt_profile="explicit",
                as_of="2026-08-01T00:00:00Z",
                verify_sources=True,
            )

    def test_evaluation_path_and_direct_assembly_bypass_fail_closed(self):
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner distribution profile"):
            assembly.build_assembly(
                self.standalone_manifest,
                bundle_root=self.bundle,
                project_root=self.project,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                as_of="2026-08-01T00:00:00Z",
                evaluation_prompt_profile="balanced",
                evaluation_run_id="cross-matrix-eval",
                verify_sources=True,
            )

        tampered = copy.deepcopy(self.manifest)
        candidate = next(
            item for item in tampered["request"]["candidates"]
            if item["scope"] == "bundle" and item["load_policy"] == "activation"
        )
        candidate["load_policy"] = "lookup"
        tampered["request"]["planner"]["candidate_discovery"][
            "candidate_set_sha256"
        ] = planner.resolver.sha256_json(tampered["request"]["candidates"])
        tampered["request_sha256"] = planner.resolver.sha256_json(
            tampered["request"]
        )
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner candidate closure"):
            assembly.build_assembly(
                tampered,
                bundle_root=self.bundle,
                project_root=self.project,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                as_of="2026-08-01T00:00:00Z",
                verify_sources=False,
            )

    def test_auditor_runtime_chain_follows_the_bound_distribution_matrix(self):
        fallback = (
            "narrative/evaluate/narrative-quality-auditor/"
            "references/auditor-runtime.md"
        )
        root_chain = "references/auditor-runbook.md"

        def manifest_for(bundle, profile, suffix):
            request = planner.build_request(
                skill="narrative-quality-auditor",
                run_id="123e4567-e89b-42d3-a456-42661417403%s" % suffix,
                turn_id="turn-auditor-%s" % suffix,
                as_of="2026-08-01T00:00:00Z",
                project_root=self.project,
                bundle_root=bundle,
                distribution_profile=profile,
            )
            return planner.resolver.resolve_context(request, bundle, self.project)

        repository_manifest = manifest_for(self.bundle, "repository", "0")
        repository = assembly.build_assembly(
            repository_manifest,
            bundle_root=self.bundle,
            project_root=self.project,
            host_profile="claude-code-plugin-host",
            model_id="test/model-1",
            as_of="2026-08-01T00:00:00Z",
        )
        repository_paths = {
            item["path"] for item in repository["consumers"]["model"]
        }
        self.assertIn(root_chain, repository_paths)
        self.assertNotIn(fallback, repository_paths)

        standalone_manifest = manifest_for(self.bundle, "standalone-skill", "1")
        standalone = assembly.build_assembly(
            standalone_manifest,
            bundle_root=self.bundle,
            project_root=self.project,
            host_profile="standalone-skill-host",
            model_id="test/model-1",
            requested_prompt_profile="explicit",
            as_of="2026-08-01T00:00:00Z",
            evaluation_run_id="auditor-standalone-projection",
            distribution_evaluation_only=True,
        )
        standalone_paths = {
            item["path"] for item in standalone["consumers"]["model"]
        }
        self.assertIn(fallback, standalone_paths)
        self.assertNotIn(root_chain, standalone_paths)
        self.assertFalse(standalone["deployment_eligible"])

        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "planner distribution profile"):
            assembly.build_assembly(
                standalone_manifest,
                bundle_root=self.bundle,
                project_root=self.project,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                as_of="2026-08-01T00:00:00Z",
            )

        plugin_bundle = self.physical_bundle()
        plugin_manifest = manifest_for(plugin_bundle, "plugin", "2")
        plugin = assembly.build_assembly(
            plugin_manifest,
            bundle_root=plugin_bundle,
            project_root=self.project,
            host_profile="claude-code-plugin-host",
            model_id="test/model-1",
            as_of="2026-08-01T00:00:00Z",
        )
        plugin_paths = {item["path"] for item in plugin["consumers"]["model"]}
        self.assertIn(root_chain, plugin_paths)
        self.assertNotIn(fallback, plugin_paths)

    def test_model_revision_is_forwarded_to_profile_resolution(self):
        result = self.build(model_revision="immutable-snapshot-2026-08-01")
        self.assertEqual(
            "immutable-snapshot-2026-08-01", result["profile"]["model_revision"]
        )

    def test_tampered_assembly_signature_is_rejected(self):
        result = self.build()
        forged = copy.deepcopy(result)
        forged["usage"]["model_body_bytes"] += 1
        with self.assertRaisesRegex(assembly.ContextAssemblyError, "signature"):
            assembly.validate_assembly(forged)

        cross_matrix = copy.deepcopy(result)
        cross_matrix["profile"]["planner_distribution_profile"] = "plugin"
        payload = dict(cross_matrix)
        payload.pop("assembly_signature")
        cross_matrix["assembly_signature"] = hashlib.sha256(
            assembly._canonical_json(payload).encode("utf-8")
        ).hexdigest()
        with self.assertRaisesRegex(
                assembly.ContextAssemblyError, "distribution matrix"):
            assembly.validate_assembly(cross_matrix)

    def test_capsule_source_hash_is_verified_against_manifest_target(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        bundle = Path(temporary.name) / "bundle"
        shutil.copytree(self.bundle, bundle)
        project = Path(temporary.name) / "project"
        project.mkdir()
        request = planner.build_request(
            skill="content-writer",
            run_id="123e4567-e89b-42d3-a456-426614174001",
            turn_id="turn-tamper",
            as_of="2026-08-01T00:00:00Z",
            project_root=project,
            bundle_root=bundle,
            distribution_profile="repository",
        )
        manifest = planner.resolver.resolve_context(request, bundle, project)
        capsule_path = bundle / "references/skill-capsules/content-writer.json"
        capsule = json.loads(capsule_path.read_text(encoding="utf-8"))
        capsule["identity"]["phase"] = "tampered"
        capsule_path.write_text(json.dumps(capsule) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(assembly.ContextAssemblyError, "hash differs"):
            assembly.build_assembly(
                manifest,
                bundle_root=bundle,
                project_root=project,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                as_of="2026-08-01T00:00:00Z",
                evaluation_prompt_profile="lean",
                evaluation_run_id="tamper-eval",
                verify_sources=True,
            )


if __name__ == "__main__":
    unittest.main()
