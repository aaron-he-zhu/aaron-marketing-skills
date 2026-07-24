import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "publish-state.py"


def load_runtime():
    specification = importlib.util.spec_from_file_location("publish_state_under_test", SCRIPT)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load publisher state runtime")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


RUNTIME = load_runtime()


class PublishStateTests(unittest.TestCase):
    def test_state_is_private_and_scoped_by_repository_version_and_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_root = Path(temporary) / "state"
            first_commit = "a" * 40
            second_commit = "b" * 40
            self.assertTrue(RUNTIME.operate(
                "owner/repo", "18.0.0", first_commit,
                "mark", "ch:18.0.0:%s:skill-a" % first_commit, state_root
            ))
            self.assertTrue(RUNTIME.operate(
                "owner/repo", "18.0.0", first_commit,
                "has", "ch:18.0.0:%s:skill-a" % first_commit, state_root
            ))
            self.assertFalse(RUNTIME.operate(
                "owner/repo", "18.0.0", second_commit,
                "has", "ch:18.0.0:%s:skill-a" % first_commit, state_root
            ))
            self.assertFalse(RUNTIME.operate(
                "owner/repo", "19.0.0", first_commit,
                "has", "ch:18.0.0:%s:skill-a" % first_commit, state_root
            ))
            self.assertFalse(RUNTIME.operate(
                "other/repo", "18.0.0", first_commit,
                "has", "ch:18.0.0:%s:skill-a" % first_commit, state_root
            ))
            state_path = Path(RUNTIME.operate(
                "owner/repo", "18.0.0", first_commit, "path", state_root=state_root
            ))
            self.assertIn(first_commit, state_path.name)
            self.assertEqual(0o600, stat.S_IMODE(state_path.stat().st_mode))
            self.assertEqual(0o700, stat.S_IMODE(state_path.parent.stat().st_mode))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_state_rejects_symlink_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_root = Path(temporary) / "state"
            commit = "a" * 40
            _, state_path, _ = RUNTIME.state_paths(
                "owner/repo", "18.0.0", commit, state_root
            )
            outside = Path(temporary) / "outside"
            outside.write_text("victim\n", encoding="utf-8")
            try:
                state_path.symlink_to(outside)
            except OSError as exc:
                self.skipTest("cannot create symlink: %s" % exc)
            with self.assertRaisesRegex(RUNTIME.StateError, "single-link regular file"):
                RUNTIME.operate(
                    "owner/repo", "18.0.0", commit,
                    "has", "ch:18.0.0:%s:skill" % commit, state_root
                )
            self.assertEqual("victim\n", outside.read_text(encoding="utf-8"))

    @unittest.skipUnless(hasattr(os, "link"), "hard links are unavailable")
    def test_state_rejects_hard_linked_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_root = Path(temporary) / "state"
            commit = "a" * 40
            RUNTIME.operate(
                "owner/repo", "18.0.0", commit,
                "mark", "ch:18.0.0:%s:skill" % commit, state_root
            )
            state_path = Path(RUNTIME.operate(
                "owner/repo", "18.0.0", commit, "path", state_root=state_root
            ))
            try:
                os.link(state_path, Path(temporary) / "alias")
            except OSError as exc:
                self.skipTest("cannot create hard link: %s" % exc)
            with self.assertRaisesRegex(RUNTIME.StateError, "single-link regular file"):
                RUNTIME.operate(
                    "owner/repo", "18.0.0", commit,
                    "has", "ch:18.0.0:%s:skill" % commit, state_root
                )

    def test_concurrent_marks_are_locked_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as temporary:
            state_root = Path(temporary) / "state"
            processes = []
            commit = "a" * 40
            keys = [
                "sh:18.0.0:%s:skill-%02d" % (commit, index % 8)
                for index in range(24)
            ]
            for key in keys:
                processes.append(subprocess.Popen(
                    [
                        sys.executable, str(SCRIPT), "--repo", "owner/repo",
                        "--version", "18.0.0", "--commit", commit,
                        "--state-root", str(state_root),
                        "mark", key,
                    ],
                    cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                ))
            failures = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=20)
                if process.returncode:
                    failures.append((process.returncode, stdout, stderr))
            self.assertEqual([], failures)
            state_path = Path(RUNTIME.operate(
                "owner/repo", "18.0.0", commit, "path", state_root=state_root
            ))
            self.assertEqual(
                sorted(set(keys)),
                sorted(state_path.read_text(encoding="utf-8").splitlines()),
            )


if __name__ == "__main__":
    unittest.main()
