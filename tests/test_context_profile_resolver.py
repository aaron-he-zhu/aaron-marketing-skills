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
        (root / "scripts").mkdir()
        shutil.copy2(
            ROOT / "scripts/context-assembly.py",
            root / "scripts/context-assembly.py",
        )
        return temporary, root


    def test_catalogs_validate_and_keep_safety_overlays_invariant(self):
        host, unused = MODULE.load_host_catalog(ROOT)
        prompt, unused = MODULE.load_prompt_catalog(ROOT, host)
        modules, unused = MODULE.load_context_module_catalog(ROOT, host, prompt)
        self.assertEqual(list(MODULE.HOST_PROFILE_ORDER), host["profile_order"])
        self.assertEqual(list(MODULE.PROMPT_PROFILE_ORDER), prompt["profile_order"])
        self.assertEqual(list(MODULE.ALWAYS_ON_OVERLAYS), prompt["always_on_overlays"])
        self.assertEqual(["explicit"], prompt["profile_order"])
        self.assertNotIn("certified_bindings", prompt)
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
        self.assertEqual("CONTEXT_PROMPT_PROFILE_UNSUPPORTED", raised.exception.code)

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
                        "CONTEXT_PROMPT_PROFILE_UNSUPPORTED",
                        raised.exception.code,
                    )


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
        self.assertIn("explicit prompt catalog", str(raised.exception))

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
        self.assertEqual(1, payload["prompt_profile_count"])
        self.assertNotIn("certified_binding_count", payload)
        self.assertEqual(13, payload["context_module_count"])


if __name__ == "__main__":
    unittest.main()
