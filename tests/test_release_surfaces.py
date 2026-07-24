#!/usr/bin/env python3
"""Tests for deterministic, bounded release-surface projection."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_release_surfaces", ROOT / "scripts/generate-release-surfaces.py"
)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


def write(root: Path, relative: str, content: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def catalog() -> dict:
    return {
        "bundle_version": "1.2.3",
        "logical_order": ["narrative", "protocol"],
        "counts": {
            "total_skills": 2,
            "commands": 2,
            "disciplines": 1,
            "protocol_skills": 1,
            "registries": 1,
            "auditors": 1,
        },
        "disciplines": {
            "narrative": {
                "phase_order": ["trace"],
                "phases": {"trace": ["fixture-skill"]},
            },
        },
        "protocol": {"skills": ["fixture-protocol"]},
    }


def metadata(markdown_surfaces=None) -> dict:
    return {
        "schema_version": "1.0",
        "plugin": {
            "id": "fixture-plugin",
            "name": "fixture-plugin",
            "display_name": "Fixture Plugin",
            "description": "2 marketing skills and 2 commands for fixture tests.",
            "author": {
                "name": "Fixture Owner",
                "email": "owner@example.com",
                "url": "https://github.com/fixture-owner",
            },
            "homepage": "https://github.com/fixture-owner/fixture-plugin",
            "repository": "https://github.com/fixture-owner/fixture-plugin",
            "license": "Apache-2.0",
            "keywords": ["fixture", "marketing"],
            "marketplace": {
                "name": "fixture",
                "category": "marketing",
                "source": "./",
                "commands": "./commands/",
                "tags": ["marketing", "fixture"],
            },
        },
        "github_about": {
            "comment": "Fixture projection.",
            "description": "2 fixture skills.",
            "topics": ["fixture", "agent-skills"],
        },
        "skills_sh": {
            "schema": "https://skills.sh/schemas/skills.sh.schema.json",
            "not_grouped": "bottom",
            "groupings": [
                {
                    "catalog_key": "narrative",
                    "title": "Narrative fixture",
                    "description": "Narrative fixture group.",
                },
                {
                    "catalog_key": "protocol",
                    "title": "Protocol fixture",
                    "description": "Protocol fixture group.",
                },
            ],
        },
        "markdown_surfaces": list(markdown_surfaces or []),
    }


def build_fixture(root: Path, markdown_surfaces=None, readme=None) -> None:
    write(
        root,
        "references/system-catalog.json",
        json.dumps(catalog(), ensure_ascii=False, indent=2) + "\n",
    )
    write(
        root,
        "references/publication-metadata.json",
        json.dumps(metadata(markdown_surfaces), ensure_ascii=False, indent=2) + "\n",
    )
    for directory in (".claude-plugin", ".github"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    if readme is not None:
        write(root, "README.md", readme)


class ReleaseSurfaceTests(unittest.TestCase):
    def test_current_repository_json_projections_have_zero_drift(self):
        self.assertEqual([], generator.check_outputs(ROOT))

    def test_json_outputs_are_canonical_deterministic_and_mirrored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root)
            self.assertEqual(6, generator.write_outputs(root))
            self.assertEqual(0, generator.write_outputs(root))
            self.assertEqual([], generator.check_outputs(root))
            marketplace = (root / "marketplace.json").read_bytes()
            self.assertEqual(
                marketplace, (root / ".claude-plugin/marketplace.json").read_bytes()
            )
            for relative in generator.JSON_TARGETS:
                path = root / relative
                value = json.loads(path.read_text(encoding="utf-8"))
                canonical = (
                    json.dumps(value, ensure_ascii=False, indent=2) + "\n"
                ).encode("utf-8")
                self.assertEqual(canonical, path.read_bytes(), relative)

    def test_markdown_write_is_marker_bounded(self):
        surface = {
            "path": "README.md",
            "marker": "release-version",
            "template": "Version {bundle_version}; skills {total_skills}.",
        }
        begin, end = generator._marker_lines("release-version")
        original = (
            "prefix with historical version 0.9.0\n"
            + begin + "\n"
            + "stale generated body\n"
            + end + "\n"
            + "suffix with historical version 0.8.0\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root, [surface], original)
            generator.write_outputs(root)
            actual = (root / "README.md").read_text(encoding="utf-8")
            self.assertEqual(
                "prefix with historical version 0.9.0\n"
                + begin + "\n"
                + "Version 1.2.3; skills 2.\n"
                + end + "\n"
                + "suffix with historical version 0.8.0\n",
                actual,
            )
            self.assertEqual([], generator.check_outputs(root))

    def test_missing_markers_fail_before_any_write(self):
        surface = {
            "path": "README.md",
            "marker": "release-version",
            "template": "Version {bundle_version}.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root, [surface], "unmarked historical prose\n")
            with self.assertRaisesRegex(
                    generator.GenerationError, "requires exactly one marker pair"):
                generator.write_outputs(root)
            self.assertEqual(
                "unmarked historical prose\n",
                (root / "README.md").read_text(encoding="utf-8"),
            )
            self.assertFalse((root / ".claude-plugin/plugin.json").exists())

    def test_unallowlisted_markdown_target_is_rejected(self):
        surface = {
            "path": "VERSIONS.md",
            "marker": "release-version",
            "template": "Version {bundle_version}.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root, [surface])
            with self.assertRaisesRegex(
                    generator.GenerationError, "target is not allowlisted"):
                generator.check_outputs(root)

    def test_unknown_template_placeholder_is_rejected(self):
        surface = {
            "path": "README.md",
            "marker": "release-version",
            "template": "Version {unsafe.attribute}.",
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root, [surface], "body\n")
            with self.assertRaisesRegex(
                    generator.GenerationError, "unsafe or unknown"):
                generator.check_outputs(root)

    def test_stale_json_projection_is_reported_without_rewriting(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root)
            generator.write_outputs(root)
            plugin = root / ".claude-plugin/plugin.json"
            plugin.write_text('{"version":"9.9.9"}\n', encoding="utf-8")
            problems = generator.check_outputs(root)
            self.assertIn(
                "stale release projection: .claude-plugin/plugin.json", problems
            )
            self.assertEqual('{"version":"9.9.9"}\n', plugin.read_text())

    def test_symlink_projection_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_fixture(root)
            backing = root / "backing.json"
            backing.write_text("{}\n", encoding="utf-8")
            (root / ".claude-plugin/plugin.json").symlink_to(backing)
            with self.assertRaisesRegex(
                    generator.GenerationError, "single-link regular file"):
                generator.check_outputs(root)


if __name__ == "__main__":
    unittest.main()
