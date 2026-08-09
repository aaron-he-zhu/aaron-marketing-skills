#!/usr/bin/env python3
"""Tests for the fail-closed Agent Plugins v1 package validator."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = REPO_ROOT / "scripts" / "validate-agent-plugin.py"
SPEC = importlib.util.spec_from_file_location("agent_plugin_validator", VALIDATOR_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


class AgentPluginValidatorTests(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "portable-plugin"
        self.root.mkdir()
        self._build_valid_fixture()

    def tearDown(self):
        self.temporary.cleanup()

    @staticmethod
    def _json_bytes(value):
        return (json.dumps(
            value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True,
        ) + "\n").encode("utf-8")

    def _write(self, relative, content):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, str):
            content = content.encode("utf-8")
        path.write_bytes(content)
        return path

    def _skill_bytes(self, name):
        return (
            "---\n"
            "name: %s\n"
            "description: Fixture skill %s for strict package validation.\n"
            "license: Apache-2.0\n"
            "metadata:\n"
            "  discipline: fixture\n"
            "  phase: validation\n"
            "---\n\n"
            "# %s\n\n"
            "See [this skill](./SKILL.md#details).\n"
            "Inline code is not a link: `[example](/private/tmp/example)`.\n\n"
            "```text\n"
            "[Product name]: [differentiator] for [audience]\n"
            "[example](/private/tmp/example)\n"
            "```\n"
        ) % (name, name, name)

    def _build_valid_fixture(self):
        plugin = {
            "$schema": VALIDATOR.PLUGIN_SCHEMA,
            "name": "aaron-marketing-skills",
            "version": "19.1.0",
            "description": "Portable Agent Plugins v1 fixture.",
            "author": {
                "name": "Aaron He Zhu",
                "url": "https://example.test/author",
            },
            "homepage": "https://example.test/plugin",
            "repository": "https://example.test/repository",
            "license": "Apache-2.0",
            "keywords": ["marketing", "skills"],
        }
        self._write("plugin.json", self._json_bytes(plugin))

        mappings = []
        for index in range(120):
            name = "skill-%03d" % index
            skill_raw = self._skill_bytes(name).encode("utf-8")
            self._write("skills/%s/SKILL.md" % name, skill_raw)
            mappings.append({
                "name": name,
                "source_path": "fixture/validation/%s/SKILL.md" % name,
                "projected_path": "skills/%s/SKILL.md" % name,
                "source_sha256": hashlib.sha256(
                    ("source:" + name).encode("utf-8")
                ).hexdigest(),
                "projected_sha256": hashlib.sha256(skill_raw).hexdigest(),
            })
        projection = {
            "schema_version": "1.0",
            "kind": "agent-plugins-v1-projection",
            "plugin_version": plugin["version"],
            "source_root": ".",
            "frontmatter_policy_version": "1.0",
            "skill_count": len(mappings),
            "skills": mappings,
        }
        self._write(VALIDATOR.PROJECTION_FILE, self._json_bytes(projection))
        catalog = {
            "schema_version": "1.2",
            "architecture_version": plugin["version"],
            "bundle_version": plugin["version"],
            "counts": {"total_skills": 120},
            "logical_order": ["fixture", "protocol"],
            "disciplines": {
                "fixture": {
                    "phase_order": ["validation"],
                    "phases": {
                        "validation": [item["name"] for item in mappings],
                    },
                },
            },
            "protocol": {"skills": []},
        }
        self._write(VALIDATOR.SYSTEM_CATALOG_PATH, self._json_bytes(catalog))
        self._write(
            VALIDATOR.PORTABLE_PROFILE_PATH,
            (REPO_ROOT / VALIDATOR.PORTABLE_PROFILE_PATH).read_bytes(),
        )
        for relative in (
                VALIDATOR.STANDARD_SCHEMA_PATH,
                VALIDATOR.STANDARD_PROVENANCE_PATH):
            self._write(relative, (REPO_ROOT / relative).read_bytes())
        self._refresh_manifest()

    def _actual_records(self):
        records = []

        def visit(directory):
            for path in sorted(directory.iterdir(), key=lambda item: item.name):
                status = path.lstat()
                if stat.S_ISDIR(status.st_mode) and not stat.S_ISLNK(status.st_mode):
                    visit(path)
                    continue
                relative = path.relative_to(self.root).as_posix()
                if relative == VALIDATOR.DISTRIBUTION_MANIFEST:
                    continue
                if (stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode)
                        or status.st_nlink != 1):
                    continue
                raw = path.read_bytes()
                records.append({
                    "bytes": len(raw),
                    "mode": "%04o" % stat.S_IMODE(status.st_mode),
                    "path": relative,
                    "sha256": hashlib.sha256(raw).hexdigest(),
                })

        visit(self.root)
        return records

    def _refresh_manifest(self):
        projection_raw = (self.root / VALIDATOR.PROJECTION_FILE).read_bytes()
        try:
            projection = json.loads(projection_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            projection = {}
        records = self._actual_records()
        provenance_raw = (
            self.root / VALIDATOR.STANDARD_PROVENANCE_PATH
        ).read_bytes()
        profile_raw = (self.root / VALIDATOR.PORTABLE_PROFILE_PATH).read_bytes()
        catalog_raw = (self.root / VALIDATOR.SYSTEM_CATALOG_PATH).read_bytes()
        manifest = {
            "schema_version": "1.2",
            "kind": "agent-plugin",
            "profile": "portable-lite",
            "capability_ceiling": "portable-lite",
            "capabilities": VALIDATOR.PORTABLE_CAPABILITIES,
            "excluded_capabilities": VALIDATOR.PORTABLE_EXCLUDED_CAPABILITIES,
            "catalog_sha256": hashlib.sha256(catalog_raw).hexdigest(),
            "profile_definition_sha256": hashlib.sha256(profile_raw).hexdigest(),
            "host_profile": "agent-plugins-v1",
            "host_capabilities": VALIDATOR.PORTABLE_CAPABILITIES,
            "host_profile_definition_sha256": hashlib.sha256(profile_raw).hexdigest(),
            "routing_surface": "direct-skill",
            "reference_surface": "packaged-static-closure",
            "connector_surface": "none",
            "mcp_policy": "absent",
            "package_ceiling": VALIDATOR.PORTABLE_PACKAGE_CEILING,
            "plugin_version": projection.get("plugin_version", "19.1.0"),
            "hash_algorithm": "sha256",
            "manifest_path": VALIDATOR.DISTRIBUTION_MANIFEST,
            "manifest_excludes": [VALIDATOR.DISTRIBUTION_MANIFEST],
            "source": {"repository": None, "commit": None},
            "agent_plugin_projection": {
                "path": VALIDATOR.PROJECTION_FILE,
                "sha256": hashlib.sha256(projection_raw).hexdigest(),
                "skill_count": projection.get("skill_count", 120),
                "frontmatter_policy_version": projection.get(
                    "frontmatter_policy_version", "1.0"
                ),
            },
            "standard": {
                "name": "agent-plugins",
                "version": "1.0.0",
                "schema_url": VALIDATOR.PLUGIN_SCHEMA,
                "schema_path": VALIDATOR.STANDARD_SCHEMA_PATH,
                "schema_sha256": VALIDATOR.STANDARD_SCHEMA_SHA256,
                "provenance_path": VALIDATOR.STANDARD_PROVENANCE_PATH,
                "provenance_sha256": hashlib.sha256(provenance_raw).hexdigest(),
                "agent_skills_commit": VALIDATOR.AGENT_SKILLS_COMMIT,
            },
            "files": records,
            "files_sha256": hashlib.sha256(self._json_bytes(records)).hexdigest(),
        }
        self._write(VALIDATOR.DISTRIBUTION_MANIFEST, self._json_bytes(manifest))

    def _errors(self):
        return VALIDATOR.validate_agent_plugin(self.root)

    def assertHasError(self, errors, *fragments):
        for error in errors:
            if all(fragment in error for fragment in fragments):
                return
        self.fail("No error contained %r. Errors:\n%s" % (fragments, "\n".join(errors)))

    def test_valid_unpacked_package_and_cli(self):
        self.assertEqual([], self._errors())
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(self.root)],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("OK: valid Agent Plugins v1 package", completed.stdout)
        self.assertEqual("", completed.stderr)

    def test_plugin_manifest_is_closed_and_typed(self):
        path = self.root / "plugin.json"
        plugin = json.loads(path.read_text(encoding="utf-8"))
        plugin.update({
            "$schema": "https://example.test/not-the-schema.json",
            "name": "Bad--Name",
            "version": "019.1",
            "author": {"name": 7, "handle": "not-standard"},
            "keywords": ["valid", 9],
            "extensions": {"com.example.fixture": {}},
            "private": True,
        })
        path.write_bytes(self._json_bytes(plugin))
        self._refresh_manifest()
        errors = self._errors()
        self.assertHasError(errors, "plugin.json", "unknown fields", "private")
        self.assertHasError(errors, "plugin.json", "$schema must equal")
        self.assertHasError(errors, "plugin.json", "name must satisfy")
        self.assertHasError(errors, "plugin.json", "version must be a valid SemVer")
        self.assertHasError(errors, "plugin.json", "author has unknown fields", "handle")
        self.assertHasError(errors, "plugin.json", "author.name must be a string")
        self.assertHasError(errors, "plugin.json", "keywords[1] must be a string")
        self.assertHasError(errors, "plugin.json", "extensions are forbidden")

    def test_skills_are_exact_directories_with_uppercase_regular_skill_file(self):
        (self.root / "skills" / "extra-skill").mkdir()
        self._write("skills/not-a-directory.md", "not a skill\n")
        target = self.root / "skills" / "skill-000" / "SKILL.md"
        target.rename(target.with_name("skill.md"))
        self._refresh_manifest()
        errors = self._errors()
        self.assertHasError(errors, "skills:", "exactly 120", "121")
        self.assertHasError(errors, "skills/not-a-directory.md", "only direct child directories")
        self.assertHasError(errors, "skills/skill-000/SKILL.md", "exact uppercase SKILL.md")
        self.assertHasError(errors, "skills/extra-skill/SKILL.md", "exact uppercase SKILL.md")

    def test_frontmatter_enforces_agent_skills_shape_and_scalar_types(self):
        self._write(
            "skills/skill-000/SKILL.md",
            "---\n"
            "name: another-skill\n"
            "description: \"\"\n"
            "version: 1.0.0\n"
            "compatibility: 9\n"
            "metadata: {\"good\": \"yes\", \"bad\": 3}\n"
            "allowed-tools:\n"
            "---\n",
        )
        self._refresh_manifest()
        errors = self._errors()
        location = "skills/skill-000/SKILL.md"
        self.assertHasError(errors, location, "non-Agent-Skills fields", "version")
        self.assertHasError(errors, location, "does not match directory")
        self.assertHasError(errors, location, "description must be a string of 1-1024")
        self.assertHasError(errors, location, "compatibility must be a string")
        self.assertHasError(errors, location, "source compatibility is forbidden")
        self.assertHasError(errors, location, "metadata entry", "string to string")
        self.assertHasError(errors, location, "allowed-tools must be a string")
        self.assertHasError(errors, location, "host preapproval is forbidden")

    def test_frontmatter_rejects_client_specific_metadata(self):
        self._write(
            "skills/skill-000/SKILL.md",
            "---\n"
            "name: skill-000\n"
            "description: Fixture skill for client metadata rejection.\n"
            "metadata: {\"discipline\": \"fixture\", \"hermes\": \"{}\", \"openclaw\": \"{}\"}\n"
            "---\n",
        )
        self._refresh_manifest()
        errors = self._errors()
        location = "skills/skill-000/SKILL.md"
        self.assertHasError(errors, location, "metadata.hermes is forbidden")
        self.assertHasError(errors, location, "metadata.openclaw is forbidden")

    def test_forbids_mcp_runtime_and_client_specific_directories(self):
        self._write("mcp.json", "{}\n")
        self._write("commands/run.md", "# command\n")
        self._write("hooks/hook.json", "{}\n")
        self._write("scripts/run.py", "pass\n")
        self._write("memory/state.json", "{}\n")
        self._write(".claude-plugin/plugin.json", "{}\n")
        self._write("com.example.client/state.json", "{}\n")
        self._refresh_manifest()
        errors = self._errors()
        self.assertHasError(errors, "mcp.json", "MCP is excluded")
        for name in ("commands", "hooks", "scripts", "memory", ".claude-plugin"):
            self.assertHasError(errors, name + ":", "directory is forbidden")
        self.assertHasError(errors, "com.example.client", "reverse-domain client directory")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO is unavailable")
    def test_rejects_symlink_hardlink_and_special_file_without_following(self):
        outside = Path(self.temporary.name) / "outside.txt"
        outside.write_text("outside\n", encoding="utf-8")
        os.symlink(outside, self.root / "escape-link")
        first = self._write("hardlink-a.txt", "linked\n")
        os.link(first, self.root / "hardlink-b.txt")
        os.mkfifo(self.root / "special.fifo")
        errors = self._errors()
        self.assertHasError(errors, "escape-link", "symlinks are forbidden")
        self.assertHasError(errors, "escape-link", "outside the package root")
        self.assertHasError(errors, "hardlink-a.txt", "hard-linked files are forbidden")
        self.assertHasError(errors, "hardlink-b.txt", "hard-linked files are forbidden")
        self.assertHasError(errors, "special.fifo", "special files are forbidden")

    def test_rejects_absolute_escaping_and_missing_local_links(self):
        path = self.root / "skills" / "skill-000" / "SKILL.md"
        text = path.read_text(encoding="utf-8") + (
            "\n[absolute](/private/tmp/file.md)\n"
            "[windows](C:\\temp\\file.md)\n"
            "[escape](../../../outside.md)\n"
            "[encoded escape](..%2F..%2F..%2Foutside.md)\n"
            "[missing](./missing.md)\n"
        )
        path.write_text(text, encoding="utf-8")
        self._refresh_manifest()
        errors = self._errors()
        location = "skills/skill-000/SKILL.md"
        self.assertHasError(errors, location, "absolute local link", "/private/tmp")
        self.assertHasError(errors, location, "absolute local link", "C:\\temp")
        self.assertHasError(errors, location, "local link escapes", "../../../outside")
        self.assertHasError(errors, location, "local link escapes", "..%2F..")
        self.assertHasError(errors, location, "local link target does not exist", "missing.md")

    def test_projection_is_closed_sorted_and_bound_to_real_projected_hashes(self):
        path = self.root / VALIDATOR.PROJECTION_FILE
        projection = json.loads(path.read_text(encoding="utf-8"))
        projection["plugin_version"] = "20.0.0"
        projection["unexpected"] = True
        projection["skills"][0]["source_path"] = "../escape/SKILL.md"
        projection["skills"][0]["projected_sha256"] = "0" * 64
        projection["skills"][0], projection["skills"][1] = (
            projection["skills"][1], projection["skills"][0]
        )
        path.write_bytes(self._json_bytes(projection))
        self._refresh_manifest()
        errors = self._errors()
        self.assertHasError(errors, VALIDATOR.PROJECTION_FILE, "must contain exactly")
        self.assertHasError(errors, VALIDATOR.PROJECTION_FILE, "plugin_version does not match")
        self.assertHasError(errors, VALIDATOR.PROJECTION_FILE, "skills entries must be sorted")
        self.assertHasError(errors, VALIDATOR.PROJECTION_FILE + ":skills[1]", "source_path is not")
        self.assertHasError(errors, VALIDATOR.PROJECTION_FILE + ":skills[1]", "projected_sha256 does not match")

    def test_distribution_manifest_binds_projection_and_all_file_hashes(self):
        path = self.root / VALIDATOR.DISTRIBUTION_MANIFEST
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["host_profile"] = "claude-code-plugin-host"
        manifest["capability_ceiling"] = "governed"
        manifest["agent_plugin_projection"]["sha256"] = "0" * 64
        manifest["agent_plugin_projection"]["skill_count"] = 119
        plugin_record = next(
            item for item in manifest["files"] if item["path"] == "plugin.json"
        )
        plugin_record["sha256"] = "f" * 64
        path.write_bytes(self._json_bytes(manifest))
        errors = self._errors()
        self.assertHasError(errors, "distribution-manifest.json", "host_profile must be 'agent-plugins-v1'")
        self.assertHasError(errors, "distribution-manifest.json", "capability_ceiling must be 'portable-lite'")
        self.assertHasError(errors, "distribution-manifest.json", "agent_plugin_projection.sha256")
        self.assertHasError(errors, "distribution-manifest.json", "skill_count does not match")
        self.assertHasError(errors, "distribution-manifest.json", "file record does not match", "plugin.json")
        self.assertHasError(errors, "distribution-manifest.json", "files_sha256 does not match")

    def test_standard_schema_and_provenance_are_immutable_and_bound(self):
        schema_path = self.root / VALIDATOR.STANDARD_SCHEMA_PATH
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        schema["title"] = "Tampered title"
        schema_path.write_bytes(self._json_bytes(schema))

        provenance_path = self.root / VALIDATOR.STANDARD_PROVENANCE_PATH
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        provenance["agent_skills_baseline"]["commit"] = "0" * 40
        provenance_path.write_bytes(self._json_bytes(provenance))
        self._refresh_manifest()

        errors = self._errors()
        self.assertHasError(
            errors, VALIDATOR.STANDARD_SCHEMA_PATH,
            "does not match the pinned Agent Plugins v1 schema SHA-256",
        )
        self.assertHasError(
            errors, VALIDATOR.STANDARD_PROVENANCE_PATH,
            "Agent Skills baseline commit is invalid",
        )
        self.assertHasError(
            errors, "distribution-manifest.json", "standard.schema_sha256",
        )

    def test_malformed_documents_do_not_hide_independent_skill_failures(self):
        self._write("plugin.json", "{ not-json\n")
        self._write("skills/skill-000/SKILL.md", "no frontmatter\n")
        self._write(
            "skills/skill-001/SKILL.md",
            "---\nname: wrong\ndescription: valid\nunknown: value\n---\n",
        )
        self._refresh_manifest()
        errors = self._errors()
        self.assertHasError(errors, "plugin.json", "invalid JSON")
        self.assertHasError(errors, "skills/skill-000/SKILL.md", "frontmatter delimiter")
        self.assertHasError(errors, "skills/skill-001/SKILL.md", "does not match directory")
        self.assertHasError(errors, "skills/skill-001/SKILL.md", "non-Agent-Skills fields")

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(self.root)],
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("ERROR: plugin.json", completed.stderr)
        self.assertIn("ERROR: skills/skill-000/SKILL.md", completed.stderr)
        self.assertIn("FAILED:", completed.stderr)

    def test_missing_package_root_is_nonzero_and_locatable(self):
        missing = Path(self.temporary.name) / "not-created"
        errors = VALIDATOR.validate_agent_plugin(missing)
        self.assertHasError(errors, ".:", "package root is unavailable")
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), str(missing)],
            text=True, capture_output=True, check=False,
        )
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("ERROR: .: package root is unavailable", completed.stderr)


if __name__ == "__main__":
    unittest.main()
