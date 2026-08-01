import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-claude-index.py"
SPEC = importlib.util.spec_from_file_location("generate_claude_index", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ClaudeIndexTests(unittest.TestCase):
    def test_generated_index_is_current(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_index_covers_catalog_exactly_once(self):
        catalog = json.loads(
            (ROOT / "references/system-catalog.json").read_text(encoding="utf-8")
        )
        expected = []
        for discipline in catalog["logical_order"]:
            if discipline == "protocol":
                expected.extend(catalog["protocol"]["skills"])
            else:
                spec = catalog["disciplines"][discipline]
                for phase in spec["phase_order"]:
                    expected.extend(spec["phases"][phase])
        source = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        generated = source.split(MODULE.BEGIN, 1)[1].split(MODULE.END, 1)[0]
        actual = re.findall(r"`([a-z0-9][a-z0-9-]*)`", generated)
        self.assertEqual(120, len(actual))
        self.assertEqual(set(expected), set(actual))
        self.assertEqual(len(actual), len(set(actual)))

    def test_root_context_is_a_bounded_navigation_surface(self):
        source = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(source.encode("utf-8")), 16_000)
        self.assertNotIn("## Skills by Phase", source)
        self.assertNotIn("## Tool Connector Pattern", source)
        self.assertIn("## Progressive Context Loading", source)
        self.assertIn("references/context-modules.json", source)

    def test_marker_shape_fails_closed(self):
        with self.assertRaises(MODULE.ClaudeIndexError):
            MODULE.replace_index("no markers", MODULE.render(MODULE.load_catalog()))
        with self.assertRaises(MODULE.ClaudeIndexError):
            MODULE.replace_index(
                MODULE.BEGIN + "\n" + MODULE.BEGIN + "\n" + MODULE.END,
                MODULE.render(MODULE.load_catalog()),
            )


if __name__ == "__main__":
    unittest.main()
