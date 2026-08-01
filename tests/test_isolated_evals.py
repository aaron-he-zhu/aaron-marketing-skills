#!/usr/bin/env python3
"""Regression tests for the sync-worktree isolated evaluation launcher."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run-isolated-evals.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aaron_isolated_evals", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(root, *arguments):
    return subprocess.run(
        ["git", "-C", str(root), *arguments],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def fixture_repository(base):
    source = Path(base) / "source"
    source.mkdir()
    git(source, "init", "--quiet")
    git(source, "config", "user.name", "Fixture")
    git(source, "config", "user.email", "fixture" + "@" + "example.invalid")
    (source / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
    scripts = source / "scripts"
    scripts.mkdir()
    runner = scripts / "run-behavior-evals.py"
    runner.write_text(
        "import os, pathlib, shutil, sys\n"
        "root = pathlib.Path.cwd()\n"
        "assert pathlib.Path(__file__).resolve().parents[1] == root\n"
        "assert os.stat(root / 'payload.txt').st_nlink == 1\n"
        "assert os.stat(pathlib.Path(shutil.which('python3')).resolve()).st_nlink == 1\n"
        "assert sys.argv[1:] == ['--suite', 'fixture']\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)
    original = Path(base) / "original.txt"
    original.write_text("committed\n", encoding="utf-8")
    os.link(original, source / "payload.txt")
    (source / "ignored.txt").write_text("private\n", encoding="utf-8")
    git(source, "add", ".gitignore", "scripts/run-behavior-evals.py", "payload.txt")
    git(source, "commit", "--quiet", "-m", "fixture")
    # The staged copy must contain current working-tree edits and untracked,
    # non-ignored files, not only committed HEAD.
    (source / "payload.txt").write_text("modified\n", encoding="utf-8")
    (source / "untracked.txt").write_text("included\n", encoding="utf-8")
    return source


class IsolatedEvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def test_stage_is_clean_single_link_snapshot_of_current_worktree(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = fixture_repository(temporary)
            stage = Path(temporary) / "stage"
            provenance = self.module.stage_repository(source, stage)
            self.assertEqual((stage / "payload.txt").read_text(), "modified\n")
            self.assertEqual((stage / "untracked.txt").read_text(), "included\n")
            self.assertFalse((stage / "ignored.txt").exists())
            self.assertEqual(os.stat(stage / "payload.txt").st_nlink, 1)
            self.assertTrue(stat.S_IMODE((stage / "scripts/run-behavior-evals.py").stat().st_mode) & 0o100)
            self.assertEqual(git(stage, "status", "--porcelain").stdout, "")
            self.assertIn("payload.txt", provenance["files"])
            self.assertEqual(provenance["files"]["payload.txt"]["size_bytes"], 9)

    def test_run_isolated_forwards_suite_arguments(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = fixture_repository(temporary)
            temp_root = Path(temporary) / "isolated"
            temp_root.mkdir()
            status, provenance = self.module.run_isolated(
                source, temp_root, ["--suite", "fixture"], python=sys.executable,
            )
            self.assertEqual(status, 0)
            self.assertGreater(provenance["file_count"], 0)

    def test_snapshot_rejects_tracked_symlink(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlinks unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            source = fixture_repository(temporary)
            os.symlink("payload.txt", source / "alias.txt")
            git(source, "add", "alias.txt")
            with self.assertRaisesRegex(
                    self.module.IsolatedEvalError, "cannot open snapshot source"):
                self.module.stage_repository(source, Path(temporary) / "stage")

    def test_explicit_multi_link_interpreter_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = Path(temporary) / "python-a"
            second = Path(temporary) / "python-b"
            first.write_bytes(b"not executed")
            first.chmod(0o700)
            os.link(first, second)
            with self.assertRaisesRegex(
                    self.module.IsolatedEvalError, "single-link Python"):
                self.module.select_single_link_python(str(first))

    def test_oversize_source_is_refused_before_target_creation(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.bin"
            target = Path(temporary) / "target.bin"
            source.write_bytes(b"0123456789")
            with self.assertRaisesRegex(
                    self.module.IsolatedEvalError, "before copy"):
                self.module._copy_stable_file(
                    source, target, remaining_bytes=9
                )
            self.assertFalse(target.exists())

    def test_snapshot_git_ignores_ambient_hooks_filters_and_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = fixture_repository(root)
            (source / ".gitattributes").write_text(
                "*.txt filter=ambient\n", encoding="utf-8"
            )
            ambient_home = root / "ambient-home"
            hooks = root / "ambient-hooks"
            ambient_home.mkdir()
            hooks.mkdir()
            hook_marker = root / "ambient-hook-ran"
            filter_marker = root / "ambient-filter-ran"
            hook = hooks / "post-commit"
            hook.write_text(
                "#!/bin/sh\n: > %s\n" % hook_marker,
                encoding="utf-8",
            )
            hook.chmod(0o700)
            filter_script = root / "ambient-filter"
            filter_script.write_text(
                "#!/bin/sh\n: > %s\ncat\n" % filter_marker,
                encoding="utf-8",
            )
            filter_script.chmod(0o700)
            global_config = ambient_home / ".gitconfig"
            global_config.write_text(
                "[core]\n\thooksPath = %s\n"
                "[filter \"ambient\"]\n\tclean = %s\n\trequired = true\n"
                % (hooks, filter_script),
                encoding="utf-8",
            )
            stage = root / "stage"
            with mock.patch.dict(os.environ, {
                "HOME": str(ambient_home),
                "GIT_CONFIG_GLOBAL": str(global_config),
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.hooksPath",
                "GIT_CONFIG_VALUE_0": str(hooks),
            }, clear=False):
                self.module.stage_repository(source, stage)
            self.assertFalse(hook_marker.exists())
            self.assertFalse(filter_marker.exists())
            self.assertEqual((stage / "payload.txt").read_text(), "modified\n")


if __name__ == "__main__":
    unittest.main()
