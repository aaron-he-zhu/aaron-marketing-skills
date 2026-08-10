import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check-agent-plugins-standard.py"


def load_module():
    specification = importlib.util.spec_from_file_location(
        "agent_plugins_standard_check_under_test", SCRIPT
    )
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


MODULE = load_module()


class AgentPluginsStandardCheckTests(unittest.TestCase):
    def test_repository_pin_is_internally_consistent(self):
        verified = MODULE.verify_local(ROOT)
        self.assertEqual(
            "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883",
            verified["schema_sha256"],
        )
        self.assertEqual("1.0.0", verified["plugins"]["specification_version"])
        self.assertEqual(
            "217be548739f21d6008915c29aefe320ea1a90af",
            verified["skills"]["commit"],
        )

    def test_tampered_vendored_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)
            source = ROOT / "references" / "standards" / "agent-plugins" / "1.0.0"
            destination = (
                fixture / "references" / "standards" / "agent-plugins" / "1.0.0"
            )
            destination.parent.mkdir(parents=True)
            shutil.copytree(source, destination)
            schema_path = destination / "plugin.schema.json"
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            schema["title"] = "tampered"
            schema_path.write_text(json.dumps(schema) + "\n", encoding="utf-8")
            with self.assertRaises(MODULE.StandardError):
                MODULE.verify_local(fixture)

    def test_changed_upstream_baseline_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fixture = Path(temporary)
            source = ROOT / "references" / "standards" / "agent-plugins" / "1.0.0"
            destination = (
                fixture / "references" / "standards" / "agent-plugins" / "1.0.0"
            )
            destination.parent.mkdir(parents=True)
            shutil.copytree(source, destination)
            provenance_path = destination / "PROVENANCE.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            provenance["agent_plugins"]["release_commit"] = "0" * 40
            provenance_path.write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            with self.assertRaises(MODULE.StandardError):
                MODULE.verify_local(fixture)


if __name__ == "__main__":
    unittest.main()
