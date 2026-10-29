"""Author refresh remains a small, fail-fast dependency sequence."""
import contextlib
import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("maintain_projections", ROOT / "scripts/maintain.py")
maintain = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(maintain)


class MaintenanceTests(unittest.TestCase):
    def test_source_generators_precede_hash_bound_contracts(self):
        names = maintain.GENERATORS
        self.assertEqual(len(names), len(set(names)))
        self.assertLess(names.index("generate-release-surfaces.py"), names.index("generate-claude-index.py"))
        self.assertLess(names.index("generate-auditor-runtime.py"), names.index("generate-skill-contracts.py"))
        self.assertLess(names.index("generate-auditor-runtime.py"), names.index("workflow-graph.py"))
        self.assertLess(names.index("workflow-graph.py"), names.index("generate-skill-contracts.py"))
        self.assertLess(names.index("generate-auditor-runtime.py"), names.index("generate-auditor-prompt-contracts.py"))
        self.assertNotIn("generate-skill-capsules.py", names)

    def test_default_checks_without_writing_or_publishing(self):
        with mock.patch.object(maintain.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as execute, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, maintain.refresh())
        self.assertEqual(len(maintain.GENERATORS), execute.call_count)
        for call in execute.call_args_list:
            self.assertEqual("--check", call.args[0][-1])
            self.assertNotIn("--live", call.args[0])
            self.assertNotIn("--to", call.args[0])

    def test_write_stops_on_first_failure_and_preserves_remaining_generators(self):
        with mock.patch.object(maintain.subprocess, "run", side_effect=[
                SimpleNamespace(returncode=0), SimpleNamespace(returncode=7)]) as execute, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(7, maintain.refresh(write=True))
        self.assertEqual(2, execute.call_count)
        self.assertTrue(all(call.args[0][-1] == "--write" for call in execute.call_args_list))

    def test_missing_generator_is_detected_before_any_write(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(maintain.subprocess, "run") as execute:
            with self.assertRaisesRegex(ValueError, "required generator is missing"):
                maintain.refresh(Path(directory), write=True)
            execute.assert_not_called()

    def test_list_only_never_executes(self):
        output = io.StringIO()
        with mock.patch.object(maintain.subprocess, "run") as execute, \
                contextlib.redirect_stdout(output):
            self.assertEqual(0, maintain.refresh(list_only=True))
            execute.assert_not_called()
        self.assertEqual(len(maintain.GENERATORS), len(output.getvalue().splitlines()))


if __name__ == "__main__":
    unittest.main()
