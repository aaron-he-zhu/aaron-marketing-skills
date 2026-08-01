import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "generate_auditor_runtime", ROOT / "scripts" / "generate-auditor-runtime.py"
)
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class AuditorRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = generator.load_json(generator.SYSTEM_CATALOG)
        cls.catalog = generator.load_json(generator.FRAMEWORK_CATALOG)

    @staticmethod
    def snapshot_from_bundle(bundle):
        text = bundle.decode("utf-8")
        marker = "## Typed Framework Snapshot\n\n```json\n"
        payload = text.split(marker, 1)[1].split("\n```", 1)[0]
        return json.loads(payload)

    def test_all_standalone_bundles_contain_every_typed_item_definition(self):
        self.assertEqual(8, len(self.system["auditors"]))
        for auditor in self.system["auditors"]:
            with self.subTest(framework=auditor["framework"]):
                bundle = generator.build_bundle(auditor, self.catalog)
                snapshot = self.snapshot_from_bundle(bundle)
                framework = self.catalog["frameworks"][auditor["framework"]]
                expected = generator.expected_item_dimensions(framework)
                actual = snapshot["frameworks"][auditor["framework"]]["items"]
                self.assertEqual(set(expected), set(actual))
                self.assertEqual(
                    set(framework["veto_items"]),
                    {item_id for item_id, item in actual.items() if item["veto"]},
                )
                for item_id, dimension in expected.items():
                    item = actual[item_id]
                    self.assertEqual(dimension, item["dimension"])
                    self.assertTrue(item["criterion"])
                    self.assertEqual(
                        "%s-%s" % (auditor["framework"], item_id),
                        item["qualified_id"],
                    )
                result = snapshot["standalone_observation_contract"]["result"]
                self.assertEqual("UNDECIDED", result["verdict"])
                self.assertEqual("NOT_SCORED", result["score_state"])
                self.assertEqual("not_scored", result["score_confidence"])

    def test_missing_benchmark_item_fails_generation(self):
        framework = self.catalog["frameworks"]["CORE-EEAT"]
        source = (ROOT / framework["source"]).read_text(encoding="utf-8")
        source = source.replace(
            "| C01 | C | Intent Alignment | Dual ⚡ | Title promise = content delivery |\n",
            "",
            1,
        )
        with tempfile.TemporaryDirectory() as temporary:
            benchmark = Path(temporary) / "benchmark.md"
            benchmark.write_text(source, encoding="utf-8")
            with self.assertRaisesRegex(generator.GenerationError, "missing=.*C01"):
                generator.parse_item_definitions("CORE-EEAT", framework, benchmark)


if __name__ == "__main__":
    unittest.main()
