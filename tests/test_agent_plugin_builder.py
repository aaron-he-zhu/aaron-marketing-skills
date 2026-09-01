"""Regression coverage for the generated Agent Plugins v1 projection."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-distribution.py"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
ALLOWED_SKILL_FIELDS = {
    "name", "description", "license", "allowed-tools", "metadata",
    "compatibility",
}
MANIFEST_FIELDS = {
    "schema_version", "kind", "plugin_version", "profile",
    "capability_ceiling", "capabilities", "excluded_capabilities",
    "catalog_sha256", "profile_definition_sha256", "host_profile",
    "host_capabilities", "host_profile_definition_sha256", "routing_surface",
    "reference_surface", "connector_surface", "mcp_policy", "package_ceiling",
    "hash_algorithm", "manifest_path", "manifest_excludes", "source",
    "standard", "agent_plugin_projection", "files_sha256", "files",
}


class AgentPluginBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "portable"
        cls.build_result = subprocess.run(
            [
                sys.executable, str(BUILDER),
                "--output", str(cls.output),
                "--agent-plugin", "--profile", "portable-lite",
                "--source-repository", "aaron-he-zhu/aaron-marketing-skills",
                "--source-commit", "1" * 40,
            ],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cls.manifest = json.loads(
            (cls.output / "distribution-manifest.json").read_text(encoding="utf-8")
        )
        cls.projection = json.loads(
            (cls.output / "agent-plugin-projection.json").read_text(encoding="utf-8")
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_cli_builds_closed_portable_layout_with_typed_identity(self):
        self.assertIn("built agent-plugin distribution", self.build_result.stdout)
        self.assertEqual(MANIFEST_FIELDS, set(self.manifest))
        self.assertEqual("1.2", self.manifest["schema_version"])
        self.assertEqual("agent-plugin", self.manifest["kind"])
        self.assertEqual("portable-lite", self.manifest["profile"])
        self.assertEqual("portable-lite", self.manifest["capability_ceiling"])
        self.assertEqual("agent-plugins-v1", self.manifest["host_profile"])
        self.assertEqual(
            self.manifest["capabilities"], self.manifest["host_capabilities"]
        )
        self.assertEqual("direct-skill", self.manifest["routing_surface"])
        self.assertEqual(
            "packaged-static-closure", self.manifest["reference_surface"]
        )
        self.assertEqual("none", self.manifest["connector_surface"])
        self.assertEqual("absent", self.manifest["mcp_policy"])
        self.assertEqual(
            self.manifest["profile_definition_sha256"],
            self.manifest["host_profile_definition_sha256"],
        )
        self.assertEqual(
            {
                "repository": "aaron-he-zhu/aaron-marketing-skills",
                "commit": "1" * 40,
            },
            self.manifest["source"],
        )
        self.assertLessEqual(
            len(self.manifest["files"]) + 1,
            self.manifest["package_ceiling"]["max_files"],
        )
        self.assertLessEqual(
            sum(item["bytes"] for item in self.manifest["files"])
            + (self.output / "distribution-manifest.json").stat().st_size,
            self.manifest["package_ceiling"]["max_bytes"],
        )

        for forbidden in (
            "commands", "hooks", "scripts", "memory", ".claude-plugin",
            "mcp.json",
        ):
            self.assertFalse((self.output / forbidden).exists(), forbidden)

    def test_control_shape_is_static_but_governed_verification_is_absent(self):
        self.assertTrue(
            (self.output / "references/control-artifact.schema.json").is_file()
        )
        for forbidden in (
            "references/control-bindings.json",
            "references/control-bindings.schema.json",
            "scripts/validate-control-artifact.py",
        ):
            self.assertFalse((self.output / forbidden).exists(), forbidden)

        portability = (self.output / "PORTABILITY.md").read_text(encoding="utf-8")
        self.assertIn("NOT_VERIFIED", portability)
        for unavailable_claim in (
            "selected ancestry", "current head", "verified receipt",
            "permission", "persisted",
        ):
            self.assertIn(unavailable_claim, portability)

    def test_root_manifest_is_agent_plugins_v1_and_portable_specific(self):
        plugin = json.loads((self.output / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(PLUGIN_SCHEMA, plugin["$schema"])
        self.assertEqual("aaron-marketing", plugin["name"])
        self.assertEqual(self.manifest["plugin_version"], plugin["version"])
        self.assertNotIn("commands", plugin)
        self.assertNotIn("skills", plugin)
        self.assertNotIn("extensions", plugin)
        self.assertIn("static instructions and references only", plugin["description"])
        for unavailable in (
            "commands", "hooks", "MCP servers", "connectors",
            "persistent writes", "deterministic scoring runtimes",
        ):
            self.assertIn(unavailable, plugin["description"])
        self.assertFalse((self.output / "mcp.json").exists())

    def test_projection_binds_exactly_120_sorted_unique_skills(self):
        self.assertEqual(
            {
                "schema_version", "kind", "plugin_version", "source_root",
                "frontmatter_policy_version", "skill_count", "skills",
            },
            set(self.projection),
        )
        self.assertEqual("1.0", self.projection["schema_version"])
        self.assertEqual("agent-plugins-v1-projection", self.projection["kind"])
        self.assertEqual(".", self.projection["source_root"])
        self.assertEqual("1.0", self.projection["frontmatter_policy_version"])
        self.assertEqual(120, self.projection["skill_count"])
        names = [item["name"] for item in self.projection["skills"]]
        self.assertEqual(sorted(names), names)
        self.assertEqual(120, len(set(names)))
        self.assertEqual(
            names,
            sorted(path.parent.name for path in self.output.glob("skills/*/SKILL.md")),
        )
        for item in self.projection["skills"]:
            self.assertEqual(
                {
                    "name", "source_path", "projected_path", "source_sha256",
                    "projected_sha256",
                },
                set(item),
            )
            self.assertEqual(
                "skills/%s/SKILL.md" % item["name"], item["projected_path"]
            )
            self.assertEqual(
                hashlib.sha256((ROOT / item["source_path"]).read_bytes()).hexdigest(),
                item["source_sha256"],
            )
            self.assertEqual(
                hashlib.sha256((self.output / item["projected_path"]).read_bytes()).hexdigest(),
                item["projected_sha256"],
            )
        projection_raw = (self.output / "agent-plugin-projection.json").read_bytes()
        self.assertEqual(
            {
                "path": "agent-plugin-projection.json",
                "sha256": hashlib.sha256(projection_raw).hexdigest(),
                "skill_count": 120,
                "frontmatter_policy_version": "1.0",
            },
            self.manifest["agent_plugin_projection"],
        )

    def test_projected_frontmatter_uses_only_agent_skills_fields(self):
        for skill_file in sorted(self.output.glob("skills/*/SKILL.md")):
            lines = skill_file.read_text(encoding="utf-8").splitlines()
            self.assertEqual("---", lines[0], skill_file)
            end = lines.index("---", 1)
            fields = {}
            for line in lines[1:end]:
                if line:
                    key, value = line.split(":", 1)
                    fields[key] = value.strip()
            self.assertTrue({"name", "description"}.issubset(fields), skill_file)
            self.assertFalse(set(fields) - ALLOWED_SKILL_FIELDS, skill_file)
            self.assertNotIn("allowed-tools", fields, skill_file)
            self.assertNotIn("compatibility", fields, skill_file)
            self.assertEqual(skill_file.parent.name, fields["name"])
            metadata = json.loads(fields["metadata"])
            self.assertTrue(metadata, skill_file)
            self.assertTrue(
                all(isinstance(key, str) and isinstance(value, str)
                    for key, value in metadata.items()),
                skill_file,
            )
            self.assertNotIn("hermes", metadata, skill_file)
            self.assertNotIn("openclaw", metadata, skill_file)
            self.assertIn(
                "<!-- GENERATED: agent-plugins-v1 portable-lite boundary -->",
                "\n".join(lines[end + 1:]),
                skill_file,
            )
        auditor = (self.output / "skills/narrative-quality-auditor/SKILL.md").read_text()
        metadata_line = next(
            line for line in auditor.splitlines() if line.startswith("metadata: ")
        )
        self.assertEqual("auditor", json.loads(metadata_line[10:])["class"])
        source_with_preapproval = (
            self.output / "skills/ad-account-auditor/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertNotIn("allowed-tools:", source_with_preapproval)

    def test_static_links_are_rebased_and_runtime_links_redirect(self):
        skill = (
            self.output / "skills/email-sequence-designer/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "[email-creative-builder](../email-creative-builder/SKILL.md)", skill
        )
        self.assertIn(
            "[skill-contract.md §Handoff Summary Format]"
            "(../../references/skill-contract.md)",
            skill,
        )
        self.assertIn(
            "[scripts/connectors/README.md]"
            "(../../PORTABILITY.md#runtime-and-persistence-boundary)",
            skill,
        )
        self.assertTrue((self.output / "references/skill-contract.md").is_file())
        self.assertTrue(
            self.output.joinpath(
                "skills/influencer-discovery/references/templates.md"
            ).is_file()
        )
        self.assertFalse((self.output / "scripts/connectors/README.md").exists())

    def test_standard_profile_catalog_and_file_aggregate_are_byte_bound(self):
        standard = self.manifest["standard"]
        self.assertEqual(
            {
                "name", "version", "schema_url", "schema_path",
                "schema_sha256", "provenance_path", "provenance_sha256",
                "agent_skills_commit",
            },
            set(standard),
        )
        self.assertEqual("agent-plugins", standard["name"])
        self.assertEqual("1.0.0", standard["version"])
        self.assertEqual(PLUGIN_SCHEMA, standard["schema_url"])
        for path_key, hash_key in (
            ("schema_path", "schema_sha256"),
            ("provenance_path", "provenance_sha256"),
        ):
            raw = (self.output / standard[path_key]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), standard[hash_key])
        self.assertEqual(
            hashlib.sha256(
                (self.output / "references/system-catalog.json").read_bytes()
            ).hexdigest(),
            self.manifest["catalog_sha256"],
        )
        profile_digest = hashlib.sha256(
            (self.output / "references/agent-plugin-portable-profile.json").read_bytes()
        ).hexdigest()
        self.assertEqual(profile_digest, self.manifest["profile_definition_sha256"])
        self.assertEqual(
            hashlib.sha256(
                (
                    json.dumps(
                        self.manifest["files"], ensure_ascii=False,
                        allow_nan=False, indent=2, sort_keys=True,
                    ) + "\n"
                ).encode("utf-8")
            ).hexdigest(),
            self.manifest["files_sha256"],
        )

    def test_existing_verify_cli_dispatches_to_portable_verifier(self):
        result = subprocess.run(
            [
                sys.executable, str(BUILDER),
                "--verify-manifest", str(self.output),
                "--profile", "portable-lite",
                "--host-profile", "agent-plugins-v1",
                "--source-repository", "aaron-he-zhu/aaron-marketing-skills",
                "--source-commit", "1" * 40,
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("verified agent-plugin distribution", result.stdout)

    def test_verifier_rejects_projected_skill_tampering(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        tampered = Path(temporary.name) / "tampered"
        shutil.copytree(self.output, tampered)
        target = tampered / "skills/email-sequence-designer/SKILL.md"
        target.write_bytes(target.read_bytes() + b"\nunsafe mutation\n")
        result = subprocess.run(
            [
                sys.executable, str(BUILDER),
                "--verify-manifest", str(tampered),
                "--profile", "portable-lite",
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertRegex(result.stderr, r"projection output hash differs|files do not match")

    def test_agent_plugin_requires_explicit_portable_lite_profile(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        result = subprocess.run(
            [
                sys.executable, str(BUILDER), "--agent-plugin",
                "--output", str(Path(temporary.name) / "missing-profile"),
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires --profile portable-lite", result.stderr)


if __name__ == "__main__":
    unittest.main()
