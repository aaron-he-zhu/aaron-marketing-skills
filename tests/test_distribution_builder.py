import ast
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-distribution.py"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_builder_module():
    specification = importlib.util.spec_from_file_location(
        "distribution_builder_under_test", BUILDER
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load distribution builder")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


BUILDER_MODULE = load_builder_module()


def packed_member(output, relative):
    path = output / "references/skill-contracts.pack.json.gz"
    pack = json.loads(gzip.decompress(path.read_bytes()).decode("utf-8"))
    matches = [item for item in pack["files"] if item["path"] == relative]
    if len(matches) != 1:
        raise AssertionError("packed member is missing or duplicated: %s" % relative)
    content = (
        json.dumps(
            matches[0]["content"],
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")
    return content, pack


def projected_strings(value, path=()):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from projected_strings(item, path + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from projected_strings(item, path + (index,))


class DistributionBuilderTests(unittest.TestCase):
    def build(self, *arguments):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output), *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return output

    @staticmethod
    def _compact_json(value):
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    def _prompt_projection_fixture(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        base = Path(temporary.name)
        source = base / "source"
        output = base / "output"
        source_references = source / "references"
        output_references = output / "references"
        source_references.mkdir(parents=True)
        output_references.mkdir(parents=True)
        for relative in (
            "references/host-capability-profiles.json",
            "references/context-modules.json",
            "references/system-catalog.json",
            "references/skill-capsules/index.json",
            "references/skill-contracts/index.json",
            "scripts/context-assembly.py",
        ):
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

        catalog = json.loads(
            (ROOT / "references/prompt-profiles.json").read_text(encoding="utf-8")
        )
        catalog["certified_bindings"] = []
        policy_projection = json.loads(json.dumps(catalog))
        policy_projection["certified_bindings"] = []
        gates = {
            key: True for key in (
                "minimum_cases", "minimum_repeats", "minimum_coverage_strata",
                "complete_pairs", "real_execution", "real_case_evidence",
                "immutable_model_identity", "immutable_judge_identity",
                "adapter_provenance",
                "assembly_source_equivalence", "minimum_candidate_reduction",
                "same_invariants", "current_age", "routing_noninferior",
                "minimum_control_routing_accuracy",
                "minimum_candidate_routing_accuracy",
                "minimum_control_quality_pass_rate",
                "minimum_candidate_quality_pass_rate",
                "quality_noninferior", "zero_safety_regressions",
                "zero_candidate_safety_failures",
            )
        }
        certificate = {
            "$schema": "../prompt-profile-release-certificate.schema.json",
            "schema_version": "1.0",
            "kind": "prompt-profile-release-certificate",
            "protocol_version": "3.0",
            "certificate_id": "certificate:distribution-fixture",
            "paired_evidence": {
                "evidence_id": "distribution-fixture", "sha256": "1" * 64,
                "arm_run_set_sha256": "7" * 64,
            },
            "distribution_profile": "governed",
            "host": {
                "host_profile": "claude-code-plugin-host",
                "host_name": "fixture-host",
                "host_version": "fixture-host-1",
            },
            "model": {
                "provider": "fixture-provider",
                "model_id": "fixture/model-1",
                "judge_model_id": "fixture/judge-1",
                "model_revision": "immutable-snapshot-2026-08-01",
                "judge_provider": "fixture-provider",
                "judge_model_revision": "immutable-judge-snapshot-2026-08-01",
            },
            "profiles": {"control": "explicit", "candidate": "balanced"},
            "catalogs": {
                "prompt_policy_sha256": hashlib.sha256(
                    self._compact_json(policy_projection)
                ).hexdigest(),
                "host_catalog_sha256": hashlib.sha256(
                    (output / "references/host-capability-profiles.json").read_bytes()
                ).hexdigest(),
                "context_modules_sha256": hashlib.sha256(
                    (output / "references/context-modules.json").read_bytes()
                ).hexdigest(),
                "system_catalog_sha256": hashlib.sha256(
                    (output / "references/system-catalog.json").read_bytes()
                ).hexdigest(),
                "skill_contract_index_sha256": hashlib.sha256(
                    (output / "references/skill-contracts/index.json").read_bytes()
                ).hexdigest(),
                "capsule_index_sha256": hashlib.sha256(
                    (output / "references/skill-capsules/index.json").read_bytes()
                ).hexdigest(),
                "context_assembly_sha256": hashlib.sha256(
                    (output / "scripts/context-assembly.py").read_bytes()
                ).hexdigest(),
                "behavior_protocol_base_sha256": "3" * 64,
                "behavior_protocol_sha256": "4" * 64,
                "behavior_adapter_sha256": "5" * 64,
                "eval_case_runtime_sha256": "6" * 64,
            },
            "policy_snapshot_sha256": hashlib.sha256(
                self._compact_json(catalog["certification_policy"])
            ).hexdigest(),
            "evaluated_at": "2026-08-01T00:02:00Z",
            "expires_at": "2026-10-30T00:02:00Z",
            "aggregate": {
                "case_count": 40,
                "pair_count": 120,
                "coverage_stratum_count": 8,
                "arm_run_set_sha256": "7" * 64,
                "repeats": 3,
                "advisories": {
                    "paired_model_body_above_target_maximum": 0,
                    "harness_only_above_target_maximum": 0,
                    "provider_telemetry_incomplete": True,
                },
                "evidence_scope": "context-bytes-and-behavior",
                "gates": gates,
            },
            "decision": {
                "valid": True,
                "reasons": [],
                "evidence_scope": "context-bytes-and-behavior",
                "token_savings_claims_permitted": False,
                "cost_savings_claims_permitted": False,
            },
            "promotion": {
                "verifier_ref": "scripts/verify-prompt-profile-release.py",
                "verifier_sha256": "2" * 64,
                "promoted_at": "2026-08-02T00:00:00Z",
            },
        }
        certificate_raw = (
            json.dumps(certificate, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n"
        ).encode("utf-8")
        evidence_ref = "references/prompt-profile-evidence/test-balanced.json"
        binding = {
            "binding_id": "distribution-test-balanced",
            "distribution_profile": "governed",
            "host_profile": "claude-code-plugin-host",
            "model_id": "fixture/model-1",
            "model_revision": "immutable-snapshot-2026-08-01",
            "prompt_profile": "balanced",
            "evidence_ref": evidence_ref,
            "evidence_sha256": hashlib.sha256(certificate_raw).hexdigest(),
            "certified_at": certificate["evaluated_at"],
            "expires_at": certificate["expires_at"],
        }
        catalog["certified_bindings"] = [binding]
        catalog_raw = BUILDER_MODULE.canonical_json(catalog)
        (source / "references/prompt-profiles.json").write_bytes(catalog_raw)
        (output / "references/prompt-profiles.json").write_bytes(catalog_raw)
        source_evidence = source / evidence_ref
        source_evidence.parent.mkdir(parents=True)
        source_evidence.write_bytes(certificate_raw)
        shutil.copy2(
            ROOT / "references/prompt-profile-release-certificate.schema.json",
            output / "references/prompt-profile-release-certificate.schema.json",
        )
        # Cache the trusted resolver before tests temporarily redirect builder ROOT.
        BUILDER_MODULE.context_profile_module()
        return source, output, catalog, binding, source_evidence

    @staticmethod
    def _write_fixture_catalog(source, output, catalog):
        raw = BUILDER_MODULE.canonical_json(catalog)
        (source / "references/prompt-profiles.json").write_bytes(raw)
        (output / "references/prompt-profiles.json").write_bytes(raw)

    def test_plugin_contains_runtime_and_excludes_maintenance(self):
        output = self.build("--plugin", "--profile", "governed")
        assembly_spec = importlib.util.spec_from_file_location(
            "built_governed_context_assembly",
            output / "scripts/context-assembly.py",
        )
        self.assertIsNotNone(assembly_spec)
        self.assertIsNotNone(assembly_spec.loader)
        built_assembly = importlib.util.module_from_spec(assembly_spec)
        assembly_path = output / "scripts/context-assembly.py"
        assembly_code = compile(
            assembly_path.read_bytes(), str(assembly_path), "exec", dont_inherit=True
        )
        # macOS redirects bytecode to a system cache, while Linux normally writes
        # it beside the source.  Execute the main script as a CLI would (without
        # caching __main__) while forcing Linux's cache policy for every dynamic
        # dependency; the governed package must remain physically unchanged.
        with (
                mock.patch.object(sys, "pycache_prefix", None),
                mock.patch.object(sys, "dont_write_bytecode", False)):
            exec(assembly_code, built_assembly.__dict__)
            built_assembly.context_resolver._load_context_planner()
        distribution_identity = built_assembly._distribution_identity(
            output, "claude-code-plugin-host"
        )
        self.assertEqual("governed", distribution_identity["profile"])
        self.assertRegex(distribution_identity["manifest_sha256"], r"^[0-9a-f]{64}$")
        plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(120, len(plugin["skills"]))
        self.assertEqual(120, len(list(output.glob("*/*/*/SKILL.md"))) + len(list(output.glob("protocol/*/SKILL.md"))))
        for path in (
            "scripts/audit-loop.py",
            "scripts/context-assembly.py",
            "scripts/context-profile-resolver.py",
            "scripts/rubric-score.py",
            "scripts/validate-audit-artifact.py",
            "scripts/registry-events.py",
            "scripts/run-events.py",
            "scripts/context-resolver.py",
            "scripts/context-plan.py",
            "scripts/runtime-controller.py",
            "scripts/validate-control-artifact.py",
            "scripts/workflow-loop.py",
            "scripts/workflow_loop.py",
            "references/context-request.schema.json",
            "references/context-manifest.schema.json",
            "references/context-assembly.schema.json",
            "references/context-modules.json",
            "references/context-modules.schema.json",
            "references/control-artifact.schema.json",
            "references/control-bindings.json",
            "references/control-bindings.schema.json",
            "references/runtime-controller-request.schema.json",
            "references/skill-contracts.pack.json.gz",
            "references/skill-machine-contract.schema.json",
            "references/skill-machine-contract-index.schema.json",
            "references/audit-loop-state.schema.json",
            "references/audit-loop-protocol.md",
            "references/auto-routing-scenarios.md",
            "references/run-event.schema.json",
            "references/turn-snapshot.schema.json",
            "references/workflow-graph.json",
            "references/workflow-graph.source.json",
            "references/workflow-graph.schema.json",
            "references/workflow-loop-protocol.md",
            "references/workflow-loop-request.schema.json",
            "references/workflow-loop-state.schema.json",
            "references/save-point.schema.json",
            "references/skill-capsule-index.schema.json",
            "references/skill-capsule.schema.json",
            "references/skill-capsules/index.json",
            "references/skill-capsules/content-writer.json",
            "references/run-envelope.schema.json",
            "references/runtime-protocol.md",
            "references/host-capability-profiles.json",
            "references/host-capability-profiles.schema.json",
            "references/policy-kernel.md",
            "references/prompt-profile-release-certificate.schema.json",
            "references/prompt-profiles.json",
            "references/prompt-profiles.schema.json",
            "references/router-facade-sidecar.schema.json",
            "references/system-catalog.json",
            "references/scheduling.md",
            "commands/auto.md",
            "hooks/hooks.json",
        ):
            self.assertTrue((output / path).is_file(), path)
        for shard in (
            "narrative", "seo-geo", "social", "email", "ad", "influencer",
            "launch", "cross-discipline",
        ):
            self.assertTrue((output / "references" / "auto-routing" / (shard + ".md")).is_file(), shard)
        self.assertFalse((output / "evals/auto-routing-scenarios.source.md").exists())
        self.assertFalse((output / "scripts/generate-auto-routing-shards.py").exists())
        self.assertFalse((output / "scripts/workflow-graph.py").exists())
        self.assertTrue((output / "scripts/connectors/resend.py").is_file())
        self.assertTrue((output / "references/skill-contract.md").is_file())
        for path in ("tests", "evals", ".github", ".githooks", "AGENTS.md", "CONTRIBUTING.md"):
            self.assertFalse((output / path).exists(), path)
        self.assertFalse((output / "docs").exists())
        self.assertFalse((output / "references/wiki").exists())
        self.assertFalse((output / "scripts/check-wiki.py").exists())
        self.assertFalse((output / "scripts/check-routing-retrieval.py").exists())
        self.assertFalse((output / "references/workflow-graph-protocol.md").exists())
        self.assertEqual(10, len(list((output / "references/workflow-graph").glob("edges-*.json"))))
        self.assertFalse(any(path.name == "__pycache__" for path in output.rglob("*")))
        self.assertFalse(any(path.suffix == ".pyc" for path in output.rglob("*")))
        self.assertEqual(
            8, sum(path.name == "auditor-runtime.md" for path in output.rglob("*"))
        )
        manifest = json.loads(
            (output / "distribution-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            BUILDER_MODULE.canonical_compact_json(manifest) + b"\n",
            (output / "distribution-manifest.json").read_bytes(),
        )
        self.assertEqual("1.2", manifest["schema_version"])
        self.assertEqual("plugin", manifest["kind"])
        self.assertEqual("governed", manifest["profile"])
        self.assertEqual("claude-code-plugin-host", manifest["host_profile"])
        self.assertEqual("slash-commands", manifest["routing_surface"])
        self.assertEqual("shared-root", manifest["reference_surface"])
        self.assertEqual("native-plugin", manifest["connector_surface"])
        self.assertIsNone(manifest["routing_sidecar"])
        self.assertRegex(manifest["host_profile_catalog_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["host_profile_definition_sha256"], r"^[0-9a-f]{64}$")
        self.assertIn("registry-write", manifest["capabilities"])
        self.assertEqual("governed", manifest["capability_ceiling"])
        self.assertRegex(manifest["catalog_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(manifest["profile_definition_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual("sha256", manifest["hash_algorithm"])
        self.assertEqual(
            hashlib.sha256(BUILDER_MODULE.canonical_json(manifest["files"])).hexdigest(),
            manifest["files_sha256"],
        )
        expected_paths = sorted(
            path.relative_to(output).as_posix()
            for path in output.rglob("*")
            if path.is_file() and path.name != "distribution-manifest.json"
        )
        self.assertEqual(expected_paths, sorted(item["path"] for item in manifest["files"]))
        source_references = {path.relative_to(ROOT / "references") for path in (ROOT / "references").rglob("*") if path.is_file()}
        shipped_references = {path.relative_to(output / "references") for path in (output / "references").rglob("*") if path.is_file()}
        self.assertLess(len(shipped_references), len(source_references))

        for runtime in (
                "context-assembly.py", "runtime-controller.py",
                "workflow-loop.py"):
            result = subprocess.run(
                [sys.executable, str(output / "scripts" / runtime), "--help"],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, "%s: %s" % (runtime, result.stderr))
        self.assertFalse((output / "references/skill-contracts").exists())
        with tempfile.TemporaryDirectory() as project:
            request = Path(project) / "request.json"
            planned = subprocess.run(
                [
                    sys.executable, str(output / "scripts/context-plan.py"), "plan",
                    "--skill", "content-writer",
                    "--run-id", "11111111-1111-4111-8111-111111111111",
                    "--turn-id", "turn-1",
                    "--as-of", "2026-07-24T00:00:00Z",
                    "--project-root", project,
                    "--bundle-root", str(output),
                    "--output", str(request),
                ],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, planned.returncode, planned.stderr)
            validated = subprocess.run(
                [
                    sys.executable, str(output / "scripts/context-plan.py"), "validate",
                    "--request", str(request),
                    "--project-root", project,
                    "--bundle-root", str(output),
                ],
                cwd=output, capture_output=True, text=True,
            )
            self.assertEqual(0, validated.returncode, validated.stderr)

    def test_governed_runtime_loading_is_bytecode_free_under_linux_policy(self):
        output = self.build("--plugin", "--profile", "governed")
        runtime_paths = tuple(
            path.relative_to(output).as_posix()
            for path in sorted((output / "scripts").rglob("*.py"))
        )
        self.assertIn("scripts/context-assembly.py", runtime_paths)
        self.assertIn("scripts/connectors/_loader.py", runtime_paths)

        def snapshot():
            return {
                path.relative_to(output).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in output.rglob("*") if path.is_file()
            }

        before = snapshot()
        loaded = {}
        with (
                mock.patch.object(sys, "pycache_prefix", None),
                mock.patch.object(sys, "dont_write_bytecode", False)):
            for offset, relative in enumerate(runtime_paths):
                path = output / relative
                source = path.read_bytes()
                syntax = ast.parse(source, filename=str(path))
                cache_writing_imports = []
                sibling_names = {
                    sibling.stem
                    for sibling in path.parent.glob("*.py")
                    if sibling != path and sibling.stem.isidentifier()
                }
                for node in ast.walk(syntax):
                    if isinstance(node, ast.Import):
                        cache_writing_imports.extend(
                            alias.name for alias in node.names
                            if alias.name.split(".", 1)[0] in sibling_names
                        )
                    elif (
                            isinstance(node, ast.ImportFrom)
                            and node.module is not None
                            and node.module.split(".", 1)[0] in sibling_names):
                        cache_writing_imports.append(node.module)
                    elif (
                            isinstance(node, ast.Call)
                            and isinstance(node.func, ast.Attribute)
                            and node.func.attr == "exec_module"):
                        cache_writing_imports.append("exec_module")
                self.assertEqual([], cache_writing_imports, relative)
                specification = importlib.util.spec_from_file_location(
                    "built_runtime_%d" % offset, path
                )
                self.assertIsNotNone(specification)
                self.assertIsNotNone(specification.loader)
                module = importlib.util.module_from_spec(specification)
                exec(
                    compile(source, str(path), "exec", dont_inherit=True),
                    module.__dict__,
                )
                loaded[relative] = module

            loaded["scripts/context-resolver.py"]._load_context_planner()
            loaded["scripts/run-events.py"]._load_context_resolver_validator()
            loaded["scripts/workflow_loop.py"]._run_events_module()
            loaded["scripts/workflow_loop.py"]._audit_artifact_module()
            connector_http = loaded["scripts/connectors/sitemap.py"]._http
            response = connector_http.get_hard_deadline(
                "http://127.0.0.1/",
                deadline=connector_http.time.monotonic() + 10,
                retries=1,
            )
            self.assertIn("non-public", response["error"])

        self.assertEqual(before, snapshot())
        self.assertFalse(any(path.name == "__pycache__" for path in output.rglob("*")))
        self.assertFalse(any(path.suffix == ".pyc" for path in output.rglob("*")))
        identity = loaded["scripts/context-assembly.py"]._distribution_identity(
            output, "claude-code-plugin-host"
        )
        self.assertEqual("governed", identity["profile"])

    def test_profiles_are_monotonic_closed_and_within_package_ceilings(self):
        distribution = json.loads(
            (ROOT / "references/distribution-files.json").read_text()
        )
        catalog_sha256 = hashlib.sha256(
            (ROOT / "references/system-catalog.json").read_bytes()
        ).hexdigest()
        capability_catalog = json.loads(
            (ROOT / "references/capability-profiles.json").read_text()
        )
        outputs = {
            profile: self.build("--plugin", "--profile", profile)
            for profile in ("lite", "pro", "governed")
        }
        paths = {}
        capabilities = {}
        expected_ceilings = {
            "lite": {"max_files": 350, "max_bytes": 3_450_000},
            "pro": {"max_files": 400, "max_bytes": 3_950_000},
            "governed": {"max_files": 560, "max_bytes": 6_700_000},
        }
        source_bindings = json.loads(
            (ROOT / "references/prompt-profiles.json").read_text()
        )["certified_bindings"]
        for profile, output in outputs.items():
            plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
            self.assertEqual(120, len(plugin["skills"]))
            manifest = json.loads((output / "distribution-manifest.json").read_text())
            self.assertEqual(profile, manifest["profile"])
            self.assertEqual(catalog_sha256, manifest["catalog_sha256"])
            self.assertEqual(
                BUILDER_MODULE.resolve_plugin_profile(
                    distribution, profile,
                )["definition_sha256"],
                manifest["profile_definition_sha256"],
            )
            paths[profile] = {item["path"] for item in manifest["files"]}
            capabilities[profile] = set(manifest["capabilities"])
            self.assertEqual(
                capability_catalog["profiles"][profile]["capabilities"],
                manifest["capabilities"],
            )
            ceiling = manifest["package_ceiling"]
            self.assertEqual(expected_ceilings[profile], ceiling)
            self.assertLessEqual(len(manifest["files"]) + 1, ceiling["max_files"])
            self.assertLessEqual(
                sum(item["bytes"] for item in manifest["files"])
                + (output / "distribution-manifest.json").stat().st_size,
                ceiling["max_bytes"],
            )
            self.assertEqual(
                8, sum(path.name == "auditor-runtime.md" for path in output.rglob("*"))
            )
            prompt_catalog = json.loads(
                (output / "references/prompt-profiles.json").read_text()
            )
            self.assertEqual(
                source_bindings if profile == "governed" else [],
                prompt_catalog["certified_bindings"],
            )
            evidence_root = output / "references/prompt-profile-evidence"
            certificate_paths = {
                path.relative_to(output).as_posix()
                for path in evidence_root.rglob("*.json")
            } if evidence_root.exists() else set()
            self.assertEqual(
                {
                    binding["evidence_ref"]
                    for binding in prompt_catalog["certified_bindings"]
                },
                certificate_paths,
            )
            self.assertEqual(
                profile == "governed",
                (output / "references/prompt-profile-release-certificate.schema.json").is_file(),
            )
            for relative in BUILDER_MODULE.AUTHORING_GUIDE_POINTERS:
                path = output / relative
                if path.is_file():
                    self.assertIn(
                        b"distribution-projection: authoring-guide-pointer-v1",
                        path.read_bytes(),
                    )
                    self.assertLess(path.stat().st_size, 1024)
            self.assertFalse(any(
                re.fullmatch(r".+ [0-9]+\.[A-Za-z0-9]+", path.name)
                for path in output.rglob("*") if path.is_file()
            ))
            for relative in (
                "references/control-bindings.json",
                "references/control-bindings.schema.json",
                "scripts/validate-control-artifact.py",
            ):
                self.assertEqual(
                    profile == "governed", (output / relative).is_file(),
                    "%s: %s" % (profile, relative),
                )
            with tempfile.TemporaryDirectory() as project:
                resolution = subprocess.run(
                    [
                        sys.executable, str(output / "scripts/profile-resolver.py"),
                        "--root", project, "--bundle-root", str(output),
                        "diagnose", "--json",
                    ],
                    cwd=output, capture_output=True, text=True,
                )
                self.assertEqual(0, resolution.returncode, resolution.stderr)
                resolved = json.loads(resolution.stdout)
                self.assertEqual(profile, resolved["package_ceiling"])
                self.assertEqual("lite", resolved["effective_profile"])

        self.assertLess(paths["lite"], paths["pro"])
        self.assertLess(paths["pro"], paths["governed"])
        self.assertLess(capabilities["lite"], capabilities["pro"])
        self.assertLess(capabilities["pro"], capabilities["governed"])

        lite = outputs["lite"]
        self.assertFalse((lite / "scripts/connectors/resend.py").exists())
        self.assertTrue((lite / "scripts/rubric-score.py").is_file())
        self.assertFalse((lite / "scripts/validate-audit-artifact.py").exists())
        self.assertFalse((lite / "scripts/registry-events.py").exists())
        self.assertFalse((lite / "scripts/context-assembly.py").exists())
        self.assertFalse((lite / "hooks").exists())
        self.assertFalse((lite / "references/skill-contracts").exists())

        pro = outputs["pro"]
        self.assertTrue((pro / "scripts/connectors/resend.py").is_file())
        self.assertTrue((pro / "scripts/rubric-score.py").is_file())
        self.assertTrue((pro / "scripts/validate-audit-artifact.py").is_file())
        self.assertFalse((pro / "scripts/registry-events.py").exists())
        self.assertFalse((pro / "scripts/context-assembly.py").exists())
        self.assertFalse((pro / "hooks").exists())
        self.assertFalse((pro / "references/skill-contracts").exists())

        governed = outputs["governed"]
        self.assertTrue((governed / "scripts/registry-events.py").is_file())
        self.assertTrue((governed / "scripts/context-assembly.py").is_file())
        self.assertTrue((governed / "scripts/runtime-controller.py").is_file())
        self.assertTrue(
            (governed / "references/control-artifact.schema.json").is_file()
        )
        self.assertTrue((governed / "hooks/hooks.json").is_file())
        self.assertTrue(
            (governed / "references/skill-contracts.pack.json.gz").is_file()
        )
        self.assertFalse((governed / "references/skill-contracts").exists())
        capsules = list((governed / "references/skill-capsules").glob("*.json"))
        self.assertEqual(121, len(capsules))
        self.assertFalse(any(
            path.name == "SKILL.md"
            for path in (governed / "references/skill-capsules").rglob("*")
            if path.is_file()
        ))
        self.assertFalse((lite / "references/skill-capsules").exists())
        self.assertFalse((pro / "references/skill-capsules").exists())
        self.assertLessEqual(
            (governed / "references/skill-contracts.pack.json.gz").stat().st_size,
            1_000_000,
        )
        _index_raw, pack = packed_member(
            governed, "references/skill-contracts/index.json"
        )
        self.assertEqual(121, pack["file_count"])
        for profile, runtimes in {
            "lite": (
                "context-profile-resolver.py", "profile-resolver.py",
                "rubric-score.py",
            ),
            "pro": ("validate-audit-artifact.py",),
            "governed": (
                "context-assembly.py", "registry-events.py",
                "runtime-controller.py", "validate-control-artifact.py",
            ),
        }.items():
            for runtime in runtimes:
                result = subprocess.run(
                    [sys.executable, str(outputs[profile] / "scripts" / runtime), "--help"],
                    cwd=outputs[profile], capture_output=True, text=True,
                )
                self.assertEqual(
                    0, result.returncode,
                    "%s/%s: %s" % (profile, runtime, result.stderr),
                )

    def test_profile_builds_are_reproducible(self):
        for profile in ("lite", "pro", "governed"):
            first = json.loads((
                self.build("--plugin", "--profile", profile)
                / "distribution-manifest.json"
            ).read_text())
            second = json.loads((
                self.build("--plugin", "--profile", profile)
                / "distribution-manifest.json"
            ).read_text())
            self.assertEqual(first["files_sha256"], second["files_sha256"], profile)
            self.assertEqual(
                first["profile_definition_sha256"],
                second["profile_definition_sha256"],
                profile,
            )
            self.assertEqual(
                first["host_profile_definition_sha256"],
                second["host_profile_definition_sha256"],
                profile,
            )
            self.assertEqual(first["files"], second["files"], profile)

    def test_bare_plugin_is_governed_alias_with_warning(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "distribution"
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(output), "--plugin"],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("deprecated governed alias through v20", result.stderr)
            manifest = json.loads((output / "distribution-manifest.json").read_text())
            self.assertEqual("governed", manifest["profile"])
            self.assertTrue((output / "scripts/registry-events.py").is_file())

    def test_profile_rejected_for_standalone_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable, str(BUILDER),
                    "--output", str(Path(temporary) / "distribution"),
                    "--skill", "narrative/evaluate/narrative-quality-auditor",
                    "--profile", "lite",
                ],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("--profile applies to --plugin builds only", result.stderr)

    def test_standalone_contains_only_one_skill_payload(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        self.assertTrue((output / "SKILL.md").is_file())
        self.assertTrue((output / "references/auditor-runtime.md").is_file())
        self.assertFalse((output / "scripts").exists())
        self.assertFalse((output / "references/control-bindings.json").exists())
        self.assertFalse(
            (output / "references/control-bindings.schema.json").exists()
        )
        self.assertFalse((output / ".claude-plugin").exists())
        manifest = json.loads((output / "distribution-manifest.json").read_text())
        self.assertEqual("1.2", manifest["schema_version"])
        self.assertEqual("lite", manifest["profile"])
        self.assertEqual("standalone-skill", manifest["kind"])
        self.assertEqual("standalone-skill-host", manifest["host_profile"])
        self.assertEqual("direct-skill", manifest["routing_surface"])
        self.assertEqual("skill-local-only", manifest["reference_surface"])
        self.assertEqual("none", manifest["connector_surface"])
        self.assertIsNone(manifest["routing_sidecar"])
        self.assertEqual(
            ["authored-workflows", "inline-delivery", "canonical-state-read"],
            manifest["capabilities"],
        )

    def test_generic_host_gets_eight_router_facades_without_changing_120_count(self):
        output = self.build(
            "--plugin", "--profile", "lite",
            "--host-profile", "generic-shared-root-host",
        )
        plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(120, len(plugin["skills"]))
        self.assertEqual([], plugin["commands"])
        self.assertFalse((output / "commands").exists())
        self.assertTrue((output / "references/policy-kernel.md").is_file())
        self.assertTrue((output / "scripts/context-profile-resolver.py").is_file())

        sidecar_path = output / "router-facades" / "sidecar-manifest.json"
        sidecar = json.loads(sidecar_path.read_text())
        self.assertEqual(
            BUILDER_MODULE.canonical_compact_json(sidecar) + b"\n",
            sidecar_path.read_bytes(),
        )
        self.assertEqual("router-facade-sidecar", sidecar["kind"])
        self.assertEqual("generic-shared-root-host", sidecar["host_profile"])
        self.assertEqual(8, sidecar["facade_count"])
        self.assertEqual(120, sidecar["canonical_business_skill_count"])
        self.assertEqual(8, len(list((output / "router-facades").glob("*/SKILL.md"))))

        targets = [
            target
            for facade in sidecar["facades"]
            for target in facade["targets"]
        ]
        business_paths = {
            value.removeprefix("./") + "/SKILL.md" for value in plugin["skills"]
        }
        self.assertEqual(120, len(targets))
        self.assertEqual(120, len({target["name"] for target in targets}))
        self.assertEqual(business_paths, {target["path"] for target in targets})
        self.assertTrue(all(
            facade["path"] not in business_paths for facade in sidecar["facades"]
        ))

        manifest = json.loads((output / "distribution-manifest.json").read_text())
        self.assertEqual("1.2", manifest["schema_version"])
        self.assertEqual("generic-shared-root-host", manifest["host_profile"])
        self.assertEqual("router-skills", manifest["routing_surface"])
        self.assertEqual("shared-root", manifest["reference_surface"])
        self.assertEqual("sidecar", manifest["connector_surface"])
        self.assertIn("router-skills", manifest["host_capabilities"])
        self.assertEqual(
            {
                "path": "router-facades/sidecar-manifest.json",
                "sha256": hashlib.sha256(sidecar_path.read_bytes()).hexdigest(),
                "facade_count": 8,
                "canonical_business_skill_count": 120,
            },
            manifest["routing_sidecar"],
        )
        self.assertEqual(
            manifest["host_profile_definition_sha256"],
            sidecar["host_profile_sha256"],
        )

    def test_generic_host_projection_respects_every_physical_profile_ceiling(self):
        outputs = {
            profile: self.build(
                "--plugin", "--profile", profile,
                "--host-profile", "generic-shared-root-host",
            )
            for profile in ("lite", "pro", "governed")
        }
        for profile, output in outputs.items():
            manifest = json.loads(
                (output / "distribution-manifest.json").read_text()
            )
            ceiling = manifest["package_ceiling"]
            self.assertLessEqual(len(manifest["files"]) + 1, ceiling["max_files"])
            self.assertLessEqual(
                sum(item["bytes"] for item in manifest["files"])
                + (output / "distribution-manifest.json").stat().st_size,
                ceiling["max_bytes"],
            )
            self.assertFalse((output / "commands").exists())
            self.assertEqual(
                8, len(list((output / "router-facades").glob("*/SKILL.md")))
            )
            self.assertEqual(
                profile == "governed",
                (output / "references/skill-capsules/index.json").is_file(),
            )
            self.assertEqual(
                profile == "governed",
                (output / "scripts/context-assembly.py").is_file(),
            )
            prompt_catalog = json.loads(
                (output / "references/prompt-profiles.json").read_text()
            )
            source_bindings = json.loads(
                (ROOT / "references/prompt-profiles.json").read_text()
            )["certified_bindings"]
            self.assertEqual(
                source_bindings if profile == "governed" else [],
                prompt_catalog["certified_bindings"],
            )
            self.assertEqual(
                profile == "governed",
                (output / "references/prompt-profile-release-certificate.schema.json").is_file(),
            )

    def test_hand_forged_prompt_binding_is_rejected_by_every_distribution(self):
        """A self-consistent certificate is not a production trust anchor."""
        for profile in ("lite", "pro", "governed"):
            with self.subTest(profile=profile):
                source, output, _catalog, binding, _evidence = (
                    self._prompt_projection_fixture()
                )
                with mock.patch.object(BUILDER_MODULE, "ROOT", source):
                    with self.assertRaisesRegex(
                            BUILDER_MODULE.DistributionError,
                            "non-empty certified_bindings are not distributable"):
                        BUILDER_MODULE.project_prompt_profile_distribution(
                            output, profile
                        )
                self.assertFalse((output / binding["evidence_ref"]).exists())

    def test_manifest_verification_rejects_hand_forged_prompt_binding(self):
        _source, output, _catalog, _binding, _evidence = (
            self._prompt_projection_fixture()
        )
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError,
                "non-empty certified_bindings require a signed release-attestation"):
            BUILDER_MODULE.validate_prompt_profile_distribution(output, "governed")

    def test_host_profile_distribution_compatibility_fails_closed(self):
        cases = (
            (
                ("--plugin", "--profile", "lite", "--host-profile", "standalone-skill-host"),
                "incompatible with plugin",
            ),
            (
                (
                    "--skill", "narrative/trace/narrative-baseline-mapper",
                    "--host-profile", "generic-shared-root-host",
                ),
                "incompatible with standalone-skill",
            ),
        )
        for arguments, message in cases:
            with self.subTest(arguments=arguments), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary) / "distribution"
                result = subprocess.run(
                    [sys.executable, str(BUILDER), "--output", str(output), *arguments],
                    cwd=ROOT, capture_output=True, text=True,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn(message, result.stderr)

    def test_slim_frontmatter_strips_publishing_keys_only(self):
        output = self.build(
            "--plugin", "--profile", "governed", "--slim-frontmatter",
        )
        skills = list(output.glob("*/*/*/SKILL.md")) + list(output.glob("protocol/*/SKILL.md"))
        self.assertEqual(120, len(skills))
        for skill in skills:
            frontmatter = skill.read_text(encoding="utf-8").split("---")[1]
            for stripped in ("slug:", "displayName:", "summary:"):
                self.assertNotIn(stripped, frontmatter, skill)
            for required in ("name:", "version:", "description:", "metadata:",
                             "license:", "compatibility:"):
                self.assertIn(required, frontmatter, skill)
        index_raw, _pack = packed_member(
            output, "references/skill-contracts/index.json"
        )
        index = json.loads(index_raw)
        entry = next(item for item in index["contracts"] if item["skill"] == "content-writer")
        contract_raw, _pack = packed_member(output, entry["contract_ref"])
        contract = json.loads(contract_raw)
        self.assertEqual(
            contract["identity"]["sha256"],
            hashlib.sha256((output / contract["identity"]["path"]).read_bytes()).hexdigest(),
        )

    def test_slim_frontmatter_rejects_standalone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output),
             "--skill", "narrative/evaluate/narrative-quality-auditor", "--slim-frontmatter"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--slim-frontmatter applies to --plugin builds only", result.stderr)

    def test_plugin_runtime_markdown_links_are_closed(self):
        distribution = json.loads(
            (ROOT / "references/distribution-files.json").read_text()
        )
        for profile_name in ("lite", "pro", "governed"):
            output = self.build("--plugin", "--profile", profile_name)
            profile = BUILDER_MODULE.resolve_plugin_profile(
                distribution, profile_name,
            )
            missing = []
            runtime_roots = [output / "commands", output / "references"]
            runtime_roots.extend(
                output / path.removeprefix("./") for path in json.loads(
                    (output / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
                )["skills"]
            )
            sources = [(path, True) for path in output.glob("*.md") if path.is_file()]
            for runtime_root in runtime_roots:
                sources.extend((path, False) for path in runtime_root.rglob("*.md"))
            for source, runtime_only in sources:
                for raw in MARKDOWN_LINK.findall(source.read_text(encoding="utf-8")):
                    target = raw.strip().lstrip("<").rstrip(">").split("#", 1)[0]
                    if (target == "url" or not target
                            or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)):
                        continue
                    resolved = (source.parent / target).resolve()
                    if runtime_only:
                        try:
                            relative = resolved.relative_to(output.resolve())
                        except ValueError:
                            continue
                        if (not relative.parts
                                or relative.parts[0] not in {"references", "scripts"}):
                            continue
                    try:
                        relative = resolved.relative_to(output.resolve())
                    except ValueError:
                        missing.append(
                            "%s -> %s" % (source.relative_to(output), target)
                        )
                    else:
                        if (not resolved.exists()
                                and BUILDER_MODULE.dependency_allowed(
                                    relative.as_posix(), profile)):
                            missing.append(
                                "%s -> %s" % (source.relative_to(output), target)
                            )
            if profile_name == "governed":
                capsule_link_count = 0
                for capsule_path in sorted(
                        (output / "references/skill-capsules").glob("*.json")):
                    if capsule_path.name == "index.json":
                        continue
                    capsule = json.loads(capsule_path.read_text(encoding="utf-8"))
                    for field, text in projected_strings(capsule):
                        for raw in MARKDOWN_LINK.findall(text):
                            target = raw.strip().lstrip("<").rstrip(">").split(
                                "#", 1
                            )[0]
                            if (not target or re.match(
                                    r"^[A-Za-z][A-Za-z0-9+.-]*:", target)):
                                continue
                            capsule_link_count += 1
                            resolved = (capsule_path.parent / target).resolve()
                            label = "capsule:%s.%s -> %s" % (
                                capsule_path.relative_to(output),
                                ".".join(map(str, field)),
                                target,
                            )
                            try:
                                resolved.relative_to(output.resolve())
                            except ValueError:
                                missing.append(label)
                            else:
                                if not resolved.exists():
                                    missing.append(label)
                self.assertGreater(capsule_link_count, 1200)
            self.assertEqual([], missing, profile_name)

    def test_unknown_skill_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(Path(temporary) / "out"), "--skill", "missing/skill"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown skill path", result.stderr)

    def _assert_tree_copy_rejected(self, setup, pattern):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_root = base / "source"
            source_root.mkdir()
            tree = source_root / "tree"
            tree.mkdir()
            setup(base, tree)
            output = base / "output"
            output.mkdir()
            with mock.patch.object(BUILDER_MODULE, "ROOT", source_root):
                with self.assertRaisesRegex(BUILDER_MODULE.DistributionError, pattern):
                    BUILDER_MODULE.copy_entry("tree", output)

    def test_tree_copy_skips_untracked_and_backup_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            tree = root / "tree"
            tree.mkdir(parents=True)
            (tree / "tracked.md").write_text("tracked", encoding="utf-8")
            (tree / "untracked.md").write_text("untracked", encoding="utf-8")
            (tree / "tracked 2.md").write_text("backup", encoding="utf-8")
            output = Path(temporary) / "output"
            output.mkdir()

            def git_files(mode):
                if mode == "tracked":
                    return {"tree/tracked.md", "tree/tracked 2.md"}
                return {"tree/untracked.md"}

            with (
                mock.patch.object(BUILDER_MODULE, "ROOT", root),
                mock.patch.object(BUILDER_MODULE, "_git_file_set", side_effect=git_files),
            ):
                BUILDER_MODULE.copy_entry("tree", output)
            self.assertTrue((output / "tree/tracked.md").is_file())
            self.assertFalse((output / "tree/untracked.md").exists())
            self.assertFalse((output / "tree/tracked 2.md").exists())

    def test_explicit_declared_file_may_be_untracked_but_not_ignored_backup(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "source"
            root.mkdir()
            (root / "generated.json").write_text("{}", encoding="utf-8")
            (root / "generated 2.json").write_text("{}", encoding="utf-8")
            output = Path(temporary) / "output"
            output.mkdir()
            with (
                mock.patch.object(BUILDER_MODULE, "ROOT", root),
                mock.patch.object(BUILDER_MODULE, "_git_file_set", return_value=set()),
            ):
                BUILDER_MODULE.copy_entry(
                    "generated.json", output, allow_untracked=True,
                )
                copied = BUILDER_MODULE.copy_entry(
                    "generated 2.json", output, allow_untracked=True,
                )
            self.assertTrue((output / "generated.json").is_file())
            self.assertFalse(copied)
            self.assertFalse((output / "generated 2.json").exists())

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_external_file_symlink(self):
        def setup(base, tree):
            external = base / "outside.txt"
            external.write_text("outside", encoding="utf-8")
            try:
                (tree / "external-file").symlink_to(external)
            except OSError as exc:
                self.skipTest("cannot create symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_external_directory_symlink(self):
        def setup(base, tree):
            external = base / "outside-dir"
            external.mkdir()
            (external / "secret.txt").write_text("outside", encoding="utf-8")
            try:
                (tree / "external-dir").symlink_to(external, target_is_directory=True)
            except OSError as exc:
                self.skipTest("cannot create directory symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_copy_rejects_circular_symlink(self):
        def setup(_base, tree):
            try:
                (tree / "cycle").symlink_to("cycle")
            except OSError as exc:
                self.skipTest("cannot create circular symlink: %s" % exc)

        self._assert_tree_copy_rejected(setup, "contains a symlink")

    @unittest.skipUnless(hasattr(os, "link"), "hard links are unavailable")
    def test_copy_rejects_multi_link_regular_file(self):
        def setup(_base, tree):
            original = tree / "original.txt"
            original.write_text("same inode", encoding="utf-8")
            try:
                os.link(original, tree / "alias.txt")
            except OSError as exc:
                self.skipTest("cannot create hard link: %s" % exc)

        self._assert_tree_copy_rejected(setup, "single-link regular file")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFOs are unavailable")
    def test_copy_rejects_special_file(self):
        def setup(_base, tree):
            try:
                os.mkfifo(tree / "pipe")
            except OSError as exc:
                self.skipTest("cannot create FIFO: %s" % exc)

        self._assert_tree_copy_rejected(setup, "special file")

    def test_manifest_verification_detects_post_build_tampering(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        (output / "SKILL.md").write_text("tampered\n", encoding="utf-8")
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError,
                "do not match the SHA-256 manifest"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_manifest_verifier_is_read_only_compatible_with_v1(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "1.0"
        for key in (
            "profile", "capability_ceiling", "capabilities", "catalog_sha256",
            "profile_definition_sha256", "package_ceiling", "host_profile",
            "host_capabilities", "host_profile_catalog_sha256",
            "host_profile_definition_sha256", "routing_surface",
            "reference_surface", "connector_surface", "routing_sidecar",
        ):
            manifest.pop(key)
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        verified = BUILDER_MODULE.verify_distribution_manifest(output)
        self.assertEqual("1.0", verified["schema_version"])
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "has no profile identity"):
            BUILDER_MODULE.verify_distribution_manifest(
                output, expected_profile="lite",
            )

    def test_manifest_verifier_is_read_only_compatible_with_v1_1(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "1.1"
        for key in (
            "host_profile", "host_capabilities", "host_profile_catalog_sha256",
            "host_profile_definition_sha256", "routing_surface",
            "reference_surface", "connector_surface", "routing_sidecar",
        ):
            manifest.pop(key)
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        verified = BUILDER_MODULE.verify_distribution_manifest(
            output, expected_profile="lite"
        )
        self.assertEqual("1.1", verified["schema_version"])
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "no host profile identity"):
            BUILDER_MODULE.verify_distribution_manifest(
                output, expected_host_profile="standalone-skill-host",
            )

    def test_legacy_manifest_cannot_bypass_prompt_binding_trust_gate(self):
        output = self.build("--plugin", "--profile", "governed")
        catalog_path = output / BUILDER_MODULE.PROMPT_PROFILES_REF
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["certified_bindings"] = [{"hand_forged": True}]
        catalog_path.write_bytes(BUILDER_MODULE.canonical_json(catalog))

        manifest_path = output / "distribution-manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["schema_version"] = "1.1"
        for key in (
            "host_profile", "host_capabilities", "host_profile_catalog_sha256",
            "host_profile_definition_sha256", "routing_surface",
            "reference_surface", "connector_surface", "routing_sidecar",
        ):
            manifest.pop(key)
        records = BUILDER_MODULE._distribution_files(output)
        manifest["files"] = records
        manifest["files_sha256"] = hashlib.sha256(
            BUILDER_MODULE.canonical_json(records)
        ).hexdigest()
        manifest_path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError,
                "non-empty certified_bindings are not distributable"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_manifest_profile_and_ceiling_are_enforced(self):
        output = self.build("--plugin", "--profile", "lite")
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "profile does not match"):
            BUILDER_MODULE.verify_distribution_manifest(
                output, expected_profile="pro",
            )
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["package_ceiling"]["max_files"] = 1
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "exceeds package ceiling"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_manifest_host_profile_is_bound_to_the_typed_catalog(self):
        output = self.build(
            "--plugin", "--profile", "lite",
            "--host-profile", "generic-shared-root-host",
        )
        path = output / "distribution-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["host_capabilities"].append("runtime-owner-capabilities")
        path.write_bytes(BUILDER_MODULE.canonical_json(manifest))
        with self.assertRaisesRegex(
                BUILDER_MODULE.DistributionError, "typed catalog"):
            BUILDER_MODULE.verify_distribution_manifest(output)

    def test_cli_verifies_manifest_and_bound_source_provenance(self):
        commit = "1" * 40
        output = self.build(
            "--skill", "narrative/evaluate/narrative-quality-auditor",
            "--source-repository", "owner/repository",
            "--source-commit", commit,
        )
        manifest = json.loads(
            (output / "distribution-manifest.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            {"repository": "owner/repository", "commit": commit},
            manifest["source"],
        )
        result = subprocess.run(
            [
                sys.executable, str(BUILDER), "--verify-manifest", str(output),
                "--source-repository", "owner/repository", "--source-commit", commit,
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("verified standalone-skill distribution", result.stdout)

        wrong = subprocess.run(
            [
                sys.executable, str(BUILDER), "--verify-manifest", str(output),
                "--source-repository", "owner/repository", "--source-commit", "2" * 40,
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(0, wrong.returncode)
        self.assertIn("source provenance does not match", wrong.stderr)

    def test_source_provenance_must_be_complete(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [
                    sys.executable, str(BUILDER), "--output", str(Path(temporary) / "out"),
                    "--skill", "narrative/evaluate/narrative-quality-auditor",
                    "--source-repository", "owner/repository",
                ],
                cwd=ROOT, capture_output=True, text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("must be supplied together", result.stderr)


if __name__ == "__main__":
    unittest.main()
