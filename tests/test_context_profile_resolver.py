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
SCRIPT = ROOT / "scripts" / "context-profile-resolver.py"
SPEC = importlib.util.spec_from_file_location("context_profile_resolver", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
class ContextProfileResolverTests(unittest.TestCase):
    def _bundle_copy(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        references = root / "references"
        references.mkdir()
        for name in (
            "host-capability-profiles.json",
            "prompt-profiles.json",
            "context-modules.json",
        ):
            shutil.copy2(ROOT / "references" / name, references / name)
        shutil.copy2(
            ROOT / "references/system-catalog.json",
            references / "system-catalog.json",
        )
        (references / "skill-contracts").mkdir()
        shutil.copy2(
            ROOT / "references/skill-contracts/index.json",
            references / "skill-contracts/index.json",
        )
        (references / "skill-capsules").mkdir()
        shutil.copy2(
            ROOT / "references/skill-capsules/index.json",
            references / "skill-capsules/index.json",
        )
        (root / "scripts").mkdir()
        shutil.copy2(
            ROOT / "scripts/context-assembly.py",
            root / "scripts/context-assembly.py",
        )
        return temporary, root

    def _add_binding(self, root):
        catalog_path = root / "references" / "prompt-profiles.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
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
            "certificate_id": "certificate:test-only-fixture",
            "paired_evidence": {
                "evidence_id": "test-only-fixture",
                "sha256": "1" * 64,
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
                "model_id": "test/model-1",
                "judge_model_id": "test/judge-1",
                "model_revision": "immutable-snapshot-2026-08-01",
                "judge_provider": "fixture-provider",
                "judge_model_revision": "immutable-judge-snapshot-2026-08-01",
            },
            "profiles": {"control": "explicit", "candidate": "balanced"},
            "catalogs": {
                **{
                    key: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                    for key, relative in MODULE.PACKAGE_CATALOG_PATHS.items()
                },
                "prompt_policy_sha256": MODULE._prompt_policy_sha256(catalog),
                "skill_contract_index_sha256": hashlib.sha256(
                    (root / "references/skill-contracts/index.json").read_bytes()
                ).hexdigest(),
                "behavior_protocol_base_sha256": "3" * 64,
                "behavior_protocol_sha256": "4" * 64,
                "behavior_adapter_sha256": "5" * 64,
                "eval_case_runtime_sha256": "6" * 64,
            },
            "policy_snapshot_sha256": hashlib.sha256(
                MODULE._canonical_json(catalog["certification_policy"]).encode()
            ).hexdigest(),
            "evaluated_at": "2026-08-01T00:02:00Z",
            "expires_at": "2026-10-30T00:02:00Z",
            "aggregate": {
                "case_count": 40, "pair_count": 120,
                "coverage_stratum_count": 8, "repeats": 3,
                "arm_run_set_sha256": "7" * 64,
                "advisories": {
                    "paired_model_body_above_target_maximum": 0,
                    "harness_only_above_target_maximum": 0,
                    "provider_telemetry_incomplete": True,
                },
                "evidence_scope": "context-bytes-and-behavior",
                "gates": gates,
            },
            "decision": {
                "valid": True, "reasons": [],
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
        evidence = (
            json.dumps(certificate, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        evidence_ref = Path("references/prompt-profile-evidence/test-balanced.json")
        evidence_path = root / evidence_ref
        evidence_path.parent.mkdir()
        evidence_path.write_bytes(evidence)
        catalog["certified_bindings"] = [{
            "binding_id": "test-balanced",
            "distribution_profile": "governed",
            "host_profile": "claude-code-plugin-host",
            "model_id": "test/model-1",
            "model_revision": "immutable-snapshot-2026-08-01",
            "prompt_profile": "balanced",
            "evidence_ref": evidence_ref.as_posix(),
            "evidence_sha256": hashlib.sha256(evidence).hexdigest(),
            "certified_at": certificate["evaluated_at"],
            "expires_at": certificate["expires_at"],
        }]
        catalog_path.write_text(
            json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return evidence_path

    def test_catalogs_validate_and_keep_safety_overlays_invariant(self):
        host, unused = MODULE.load_host_catalog(ROOT)
        prompt, unused = MODULE.load_prompt_catalog(ROOT, host)
        modules, unused = MODULE.load_context_module_catalog(ROOT, host, prompt)
        self.assertEqual(list(MODULE.HOST_PROFILE_ORDER), host["profile_order"])
        self.assertEqual(list(MODULE.PROMPT_PROFILE_ORDER), prompt["profile_order"])
        self.assertEqual(list(MODULE.ALWAYS_ON_OVERLAYS), prompt["always_on_overlays"])
        self.assertTrue(prompt["profiles"]["balanced"]["requires_certification"])
        self.assertTrue(prompt["profiles"]["lean"]["requires_certification"])
        self.assertGreaterEqual(len(modules["modules"]), 12)

    def test_unknown_host_falls_back_only_when_auto_was_requested(self):
        resolved = MODULE.resolve_context_profile(
            bundle_root=ROOT,
            host_profile="auto",
            model_id="unknown",
            as_of="2026-08-01T00:00:00Z",
        )
        self.assertEqual("standalone-skill-host", resolved["host_profile"])
        self.assertEqual("portable-fallback", resolved["host_profile_source"])
        self.assertEqual("explicit", resolved["prompt_profile"])
        self.assertEqual("unknown-model-fallback", resolved["prompt_profile_source"])
        with self.assertRaises(MODULE.ContextProfileError) as raised:
            MODULE.resolve_context_profile(
                bundle_root=ROOT,
                host_profile="made-up-host",
                model_id="unknown",
                as_of="2026-08-01T00:00:00Z",
            )
        self.assertEqual("CONTEXT_HOST_PROFILE_UNKNOWN", raised.exception.code)

    def test_uncertified_reduction_profile_fails_closed(self):
        with self.assertRaises(MODULE.ContextProfileError) as raised:
            MODULE.resolve_context_profile(
                bundle_root=ROOT,
                host_profile="claude-code-plugin-host",
                model_id="test/model-1",
                requested_prompt_profile="balanced",
                as_of="2026-08-01T00:00:00Z",
            )
        self.assertEqual("CONTEXT_PROMPT_PROFILE_UNCERTIFIED", raised.exception.code)

    def test_host_profile_matrix_selects_exact_explicit_policy_representation(self):
        expected_policy = {
            "standalone-skill-host": "model-policy-standalone-embedded",
            "generic-shared-root-host": "model-policy-explicit",
            "claude-code-plugin-host": "model-policy-explicit",
        }
        for host_profile, policy_module in expected_policy.items():
            with self.subTest(host_profile=host_profile):
                resolved = MODULE.resolve_context_profile(
                    bundle_root=ROOT,
                    host_profile=host_profile,
                    model_id="test/model-1",
                    requested_prompt_profile="explicit",
                    as_of="2026-08-01T00:00:00Z",
                )
                model_modules = {
                    item["module_id"]
                    for item in resolved["context_modules"]["model"]
                }
                self.assertIn("model-skill-explicit", model_modules)
                self.assertIn(policy_module, model_modules)
                self.assertEqual(
                    1,
                    len(
                        model_modules
                        & {
                            "model-policy-standalone-embedded",
                            "model-policy-explicit",
                            "model-policy-kernel",
                        }
                    ),
                )

    def test_compact_deployment_is_uncertified_for_every_host_profile(self):
        for host_profile in MODULE.HOST_PROFILE_ORDER:
            for prompt_profile in ("balanced", "lean"):
                with self.subTest(
                    host_profile=host_profile, prompt_profile=prompt_profile
                ):
                    with self.assertRaises(MODULE.ContextProfileError) as raised:
                        MODULE.resolve_context_profile(
                            bundle_root=ROOT,
                            host_profile=host_profile,
                            model_id="test/model-1",
                            requested_prompt_profile=prompt_profile,
                            as_of="2026-08-01T00:00:00Z",
                        )
                    self.assertEqual(
                        "CONTEXT_PROMPT_PROFILE_UNCERTIFIED",
                        raised.exception.code,
                    )

    def test_self_consistent_hand_forged_certificate_is_not_authoritative(self):
        """Package-local hashes cannot promote a compact production profile."""
        temporary, root = self._bundle_copy()
        self.addCleanup(temporary.cleanup)
        self._add_binding(root)
        host, unused = MODULE.load_host_catalog(root)
        with self.assertRaises(MODULE.ContextProfileError) as raised:
            MODULE.load_prompt_catalog(root, host)
        self.assertEqual("CONTEXT_PROFILE_DOCUMENT_INVALID", raised.exception.code)
        self.assertIn("signed release-attestation", str(raised.exception))

    def test_host_capabilities_are_monotonic(self):
        temporary, root = self._bundle_copy()
        self.addCleanup(temporary.cleanup)
        catalog_path = root / "references" / "host-capability-profiles.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["profiles"]["generic-shared-root-host"]["capabilities"].remove(
            "skill-local-references"
        )
        catalog_path.write_text(json.dumps(catalog) + "\n", encoding="utf-8")
        with self.assertRaises(MODULE.ContextProfileError) as raised:
            MODULE.load_host_catalog(root)
        self.assertIn("monotonic", str(raised.exception))

    def test_safety_overlay_catalog_drift_fails_closed(self):
        temporary, root = self._bundle_copy()
        self.addCleanup(temporary.cleanup)
        catalog_path = root / "references" / "prompt-profiles.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["always_on_overlays"].remove("consent")
        catalog_path.write_text(json.dumps(catalog) + "\n", encoding="utf-8")
        host, unused = MODULE.load_host_catalog(root)
        with self.assertRaises(MODULE.ContextProfileError) as raised:
            MODULE.load_prompt_catalog(root, host)
        self.assertIn("identity is unsupported", str(raised.exception))

    def test_cli_validate_is_machine_readable(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--validate"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["valid"])
        self.assertEqual(3, payload["host_profile_count"])
        self.assertEqual(3, payload["prompt_profile_count"])
        self.assertEqual(0, payload["certified_binding_count"])
        self.assertEqual(18, payload["context_module_count"])


if __name__ == "__main__":
    unittest.main()
