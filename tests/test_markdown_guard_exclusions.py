#!/usr/bin/env python3
"""Undeclared dependency trees remain visible to repository guards."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class MarkdownGuardDirectoryExclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.architecture = load_module('architecture_guard', 'scripts/check-architecture.py')
        cls.local_links = load_module('link_guard', 'scripts/check-local-links.py')

    def test_local_link_guard_scans_undeclared_dependencies_and_authored_sources(self):
        for relative in ('evals/other-probe/node_modules/package/README.md',
                         'evals/other-probe/README.md'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_text('[missing](does-not-exist.md)\n')
                output = io.StringIO()
                with mock.patch.object(self.local_links, 'ROOT', root), redirect_stdout(output):
                    self.assertEqual(1, self.local_links.main())
                self.assertIn(relative + ':1 missing local target', output.getvalue())

    def test_architecture_guard_scans_undeclared_dependencies_and_authored_sources(self):
        for relative in ('evals/other-probe/node_modules/package/README.md',
                         'evals/other-probe/README.md'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_text('Run python3 scripts/run-events.py verify run-id\n')
                with mock.patch.object(self.architecture, 'ROOT', root):
                    failures = []
                    self.architecture.check_recursive_markdown(failures)
                self.assertEqual([
                    'root runtime command does not resolve AARON_SKILLS_ROOT in ' + relative,
                ], failures)

    def test_no_dependency_manifest_is_exempt_from_the_stdlib_repository(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = ('evals/other-probe/package.json',
                     'evals/other-probe/node_modules/dep/package.json')
            for relative in paths:
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text('{}\n')
            with mock.patch.object(self.architecture, 'ROOT', root):
                failures = []
                self.architecture.check_isolated_dependency_trees(failures)
            self.assertEqual(
                {'undeclared dependency tree manifest: ' + p for p in paths},
                set(failures),
            )


if __name__ == '__main__':
    unittest.main()
