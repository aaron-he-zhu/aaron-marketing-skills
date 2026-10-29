"""Keep full-CI de-duplication narrower than the commands it replaces."""
from collections import Counter
import contextlib
import copy
import importlib.util
import io
from pathlib import Path
import sys
from types import SimpleNamespace
import tempfile
import unittest
import uuid
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ci_selection_runner", ROOT / "scripts/run-behavior-evals.py")
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class DiscoveryCoverageTests(unittest.TestCase):
    @staticmethod
    def coverage():
        suite = unittest.TestLoader().loadTestsFromName("tests.test_ci_selection")
        identities, sources = runner._test_id_inventory(suite)
        return {"ids": Counter(identities), "sources": sources}

    def test_standard_script_and_module_commands_share_exact_test_ids(self):
        coverage = self.coverage()
        self.assertTrue(runner._covered_by_discovery(
            ["{python}", "tests/test_ci_selection.py"], coverage))
        self.assertTrue(runner._covered_by_discovery(
            ["{python}", "-m", "unittest", "tests.test_ci_selection"], coverage))

    def test_unexecuted_test_and_changed_source_are_not_covered(self):
        coverage = self.coverage()
        command = ["{python}", "tests/test_ci_selection.py"]
        missing = copy.deepcopy(coverage)
        missing["ids"].pop(next(iter(missing["ids"])))
        self.assertFalse(runner._covered_by_discovery(command, missing))
        changed = copy.deepcopy(coverage)
        changed["sources"]["tests/test_ci_selection.py"] = "0" * 64
        self.assertFalse(runner._covered_by_discovery(command, changed))
        self.assertFalse(runner._covered_by_discovery(command, None))

    def test_child_verified_coverage_does_not_import_test_modules_into_runner(self):
        coverage = self.coverage()
        command = ["{python}", "tests/test_ci_selection.py"]
        coverage["commands"] = [command]
        with mock.patch.object(runner.unittest, "TestLoader") as loader:
            self.assertTrue(runner._covered_by_discovery(command, coverage))
            loader.assert_not_called()
        coverage["sources"]["tests/test_ci_selection.py"] = "0" * 64
        self.assertFalse(runner._covered_by_discovery(command, coverage))

    def test_special_arguments_interpreters_and_repetitions_are_not_skipped(self):
        coverage = self.coverage()
        for command in (
                ["python3", "tests/test_ci_selection.py"],
                ["{python}", "tests/test_ci_selection.py", "-v"],
                ["{python}", "-m", "unittest", "-v", "tests.test_ci_selection"],
                ["env", "PYTHONPATH=other", "python3", "tests/test_ci_selection.py"],
                ["{python}", "-m", "unittest", "tests.test_ci_selection", "tests.test_ci_selection"]):
            with self.subTest(command=command):
                self.assertFalse(runner._covered_by_discovery(command, coverage))

    def test_custom_main_and_load_tests_keep_their_independent_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tests").mkdir()
            path = root / "tests/test_custom.py"
            for body in (
                    'import unittest\nif __name__ == "__main__":\n    unittest.main(verbosity=2)\n',
                    'import unittest\ndef load_tests(loader, tests, pattern):\n    return tests\n'
                    'if __name__ == "__main__":\n    unittest.main()\n',
                    'import unittest\nMODE=__name__\n'
                    'if __name__ == "__main__":\n    unittest.main()\n'):
                path.write_text(body, encoding="utf-8")
                with mock.patch.object(runner, "ROOT", root):
                    self.assertIsNone(runner._standard_test_sources(["{python}", "tests/test_custom.py"]))

    def test_full_mode_runs_checks_once_and_only_skips_proven_test_commands(self):
        manifest = {"schema_version": "1.0", "description": "fixture", "suites": [
            {"id": "covered", "command": ["{python}", "tests/test_ci_selection.py"], "timeout_seconds": 60},
            {"id": "independent", "command": ["{python}", "scripts/golden-auditor-math.py"], "timeout_seconds": 60},
        ]}
        with mock.patch.object(runner, "load_json", return_value=manifest), \
                mock.patch.object(runner, "_run_unittest_discovery", return_value=self.coverage()) as discovery, \
                mock.patch.object(runner.subprocess, "run", return_value=SimpleNamespace(returncode=0, stdout="ok")) as execute, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual([], runner.run_deterministic(set(), with_unittest_discovery=True))
            discovery.assert_called_once_with()
            execute.assert_called_once()
            self.assertEqual("scripts/golden-auditor-math.py", execute.call_args.args[0][1])

    def test_failed_discovery_never_authorizes_skipping_conformance(self):
        manifest = {"schema_version": "1.0", "description": "fixture", "suites": [
            {"id": "check", "command": ["{python}", "scripts/golden-auditor-math.py"], "timeout_seconds": 60},
        ]}
        with mock.patch.object(runner, "load_json", return_value=manifest), \
                mock.patch.object(runner, "_run_unittest_discovery", side_effect=runner.BehaviorEvalError("failed")), \
                mock.patch.object(runner.subprocess, "run") as execute:
            with self.assertRaisesRegex(runner.BehaviorEvalError, "failed"):
                runner.run_deterministic(set(), with_unittest_discovery=True)
            execute.assert_not_called()

    def test_real_discovery_must_execute_and_pass_before_returning_coverage(self):
        for assertion in ("self.assertTrue(True)", "self.fail('injected failure')"):
            name = "test_discovery_probe_" + uuid.uuid4().hex
            with self.subTest(assertion=assertion), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "tests").mkdir()
                (root / "tests" / (name + ".py")).write_text(
                    "import unittest\nclass Probe(unittest.TestCase):\n"
                    "    def test_probe(self):\n        " + assertion + "\n", encoding="utf-8")
                try:
                    with mock.patch.object(runner, "ROOT", root), mock.patch.object(sys, "path", sys.path[:]), \
                            contextlib.redirect_stdout(io.StringIO()):
                        if "fail(" in assertion:
                            with self.assertRaisesRegex(runner.BehaviorEvalError, "did not pass"):
                                runner._run_unittest_discovery()
                        else:
                            coverage = runner._run_unittest_discovery()
                            self.assertEqual(1, sum(coverage["ids"].values()))
                            self.assertEqual({"tests/" + name + ".py"}, set(coverage["sources"]))
                finally:
                    sys.modules.pop(name, None)

    def test_full_mode_rejects_filtered_and_model_execution(self):
        for arguments in (
                ["--with-unittest-discovery", "--suite", "framework-catalog-and-scorer"],
                ["--with-unittest-discovery", "--adapter-only", "--list-cases"],
                ["--with-unittest-discovery", "--adapter-command", "python3 example.py"]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    runner.main(arguments)
                self.assertEqual(2, raised.exception.code)


if __name__ == "__main__":
    unittest.main()
