#!/usr/bin/env python3
"""Regression tests for dependency-directory exclusions in Markdown guards."""
from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative_path):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarkdownGuardDirectoryExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architecture = load_module(
            "check_architecture_directory_exclusions",
            "scripts/check-architecture.py",
        )
        cls.local_links = load_module(
            "check_local_links_directory_exclusions",
            "scripts/check-local-links.py",
        )

    def test_local_link_guard_ignores_probe_dependencies_but_scans_source(self):
        bad_markdown = "[missing](does-not-exist.md)\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dependency_file = (
                root / "evals" / "pi-agent-poc" / "node_modules" / "package" / "README.md"
            )
            dependency_file.parent.mkdir(parents=True)
            dependency_file.write_text(bad_markdown, encoding="utf-8")

            with mock.patch.object(self.local_links, "ROOT", root), redirect_stdout(io.StringIO()):
                self.assertEqual(0, self.local_links.main())

            source_file = root / "evals" / "pi-agent-poc" / "README.md"
            source_file.write_text(bad_markdown, encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(self.local_links, "ROOT", root), redirect_stdout(output):
                self.assertEqual(1, self.local_links.main())
            self.assertIn("evals/pi-agent-poc/README.md:1 missing local target", output.getvalue())

    def test_local_link_guard_scans_undeclared_node_modules(self):
        bad_markdown = "[missing](does-not-exist.md)\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "evals" / "other-probe" / "node_modules" / "package" / "README.md"
            stray.parent.mkdir(parents=True)
            stray.write_text(bad_markdown, encoding="utf-8")
            output = io.StringIO()
            with mock.patch.object(self.local_links, "ROOT", root), redirect_stdout(output):
                self.assertEqual(1, self.local_links.main())
            self.assertIn("node_modules/package/README.md:1", output.getvalue())

    def test_architecture_guard_ignores_probe_dependencies_but_scans_source(self):
        bad_markdown = "Run python3 scripts/run-events.py verify run-id\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dependency_file = (
                root / "evals" / "pi-agent-poc" / "node_modules" / "package" / "README.md"
            )
            dependency_file.parent.mkdir(parents=True)
            dependency_file.write_text(bad_markdown, encoding="utf-8")

            with mock.patch.object(self.architecture, "ROOT", root):
                failures = []
                self.architecture.check_recursive_markdown(failures)
                self.assertEqual([], failures)

                source_file = root / "evals" / "pi-agent-poc" / "README.md"
                source_file.write_text(bad_markdown, encoding="utf-8")
                self.architecture.check_recursive_markdown(failures)
            self.assertEqual(
                ["root runtime command does not resolve AARON_SKILLS_ROOT in evals/pi-agent-poc/README.md"],
                failures,
            )

    def test_architecture_guard_scans_undeclared_node_modules(self):
        bad_markdown = "Run python3 scripts/run-events.py verify run-id\n"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stray = root / "evals" / "other-probe" / "node_modules" / "package" / "README.md"
            stray.parent.mkdir(parents=True)
            stray.write_text(bad_markdown, encoding="utf-8")
            with mock.patch.object(self.architecture, "ROOT", root):
                failures = []
                self.architecture.check_recursive_markdown(failures)
            self.assertEqual(
                ["root runtime command does not resolve AARON_SKILLS_ROOT in evals/other-probe/node_modules/package/README.md"],
                failures,
            )

    def test_isolated_dependency_tree_manifests_are_enforced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            declared = root / "evals" / "pi-agent-poc" / "package.json"
            declared.parent.mkdir(parents=True)
            declared.write_text("{}\n", encoding="utf-8")
            vendored = (
                root / "evals" / "pi-agent-poc" / "node_modules" / "dep" / "package.json"
            )
            vendored.parent.mkdir(parents=True)
            vendored.write_text("{}\n", encoding="utf-8")

            with mock.patch.object(self.architecture, "ROOT", root):
                failures = []
                self.architecture.check_isolated_dependency_trees(failures)
                self.assertEqual([], failures)

                stray = root / "tools" / "helper" / "package.json"
                stray.parent.mkdir(parents=True)
                stray.write_text("{}\n", encoding="utf-8")
                self.architecture.check_isolated_dependency_trees(failures)
            self.assertEqual(
                ["undeclared dependency tree manifest: tools/helper/package.json"],
                failures,
            )


if __name__ == "__main__":
    unittest.main()
