import importlib.util
import json
import copy
import os
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

    def test_ambiguous_or_duplicated_authoritative_item_blocks_fail(self):
        framework = self.catalog['frameworks']['ROAS']
        source = (ROOT / framework['source']).read_text()
        duplicate_row = '| `R1` | Return | A second, conflicting criterion. |\n'
        mutations = (
            source.replace('<!-- AUDITOR-ITEMS:END -->', duplicate_row + '<!-- AUDITOR-ITEMS:END -->'),
            source + '\n<!-- AUDITOR-ITEMS:BEGIN -->\n<!-- AUDITOR-ITEMS:END -->',
            source.replace('<!-- AUDITOR-ITEMS:BEGIN -->', ''),
            source.replace('<!-- AUDITOR-ITEMS:END -->', '| `R99` | Return | Unknown identity. |\n<!-- AUDITOR-ITEMS:END -->'),
        )
        for modified in mutations:
            with self.subTest(modified=modified[-100:]), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'benchmark.md'
                path.write_text(modified)
                with self.assertRaises(generator.GenerationError):
                    generator.parse_item_definitions('ROAS', framework, path)

    def test_explanatory_prose_outside_item_block_cannot_replace_a_criterion(self):
        framework = self.catalog['frameworks']['ROAS']
        path = ROOT / framework['source']
        original = generator.parse_item_definitions('ROAS', framework, path)
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / 'benchmark.md'
            changed.write_text(path.read_text() + '\n| `R1` | Return | Untrusted later rewrite. |\n')
            self.assertEqual(original, generator.parse_item_definitions('ROAS', framework, changed))

    def test_item_rows_must_match_their_authoritative_header_columns(self):
        framework = self.catalog['frameworks']['ROAS']
        source = (ROOT / framework['source']).read_text()
        original = '| `R1` | Return | Conversion instrumentation is verified against an own-data truth set. |'
        malformed = (
            '| `R1` | Return | Mandatory conversion validation | accidental trailing cell |',
            '| `R1` | Return |',
            '| `R1` | Return | Conversion validation with an escaped \\| separator |',
        )
        for row in malformed:
            with self.subTest(row=row), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'benchmark.md'
                path.write_text(source.replace(original, row))
                with self.assertRaisesRegex(generator.GenerationError, 'columns differ'):
                    generator.parse_item_definitions('ROAS', framework, path)

    def test_declared_dimension_must_match_typed_item_identity(self):
        framework = self.catalog['frameworks']['ROAS']
        source = (ROOT / framework['source']).read_text()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'benchmark.md'
            path.write_text(source.replace('| `R1` | Return |', '| `R1` | Offer |', 1))
            with self.assertRaisesRegex(generator.GenerationError, 'dimension differs'):
                generator.parse_item_definitions('ROAS', framework, path)

    def test_item_names_follow_named_columns_and_never_priority_labels(self):
        framework = self.catalog['frameworks']['CORE-EEAT']
        source = (ROOT / framework['source']).read_text()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'benchmark.md'
            path.write_text(source.replace('| C01 | C | Intent Alignment | Dual ⚡ |',
                                           '| C01 | C | GEO Intent Alignment | Dual ⚡ |', 1))
            item = generator.parse_item_definitions('CORE-EEAT', framework, path)['C01']
            self.assertEqual('GEO Intent Alignment', item['name'])
            self.assertEqual('Title promise = content delivery', item['criterion'])
        framework = self.catalog['frameworks']['CITE']
        item = generator.parse_item_definitions('CITE', framework, ROOT / framework['source'])['C01']
        self.assertEqual('C', item['dimension'])
        self.assertEqual('Referring Domains Volume', item['name'])

    def test_standalone_missingness_contract_does_not_require_na_evidence(self):
        for auditor in self.system['auditors']:
            text = generator.build_bundle(auditor, self.catalog).decode()
            self.assertIn('Observed pass/partial/fail states need evidence.', text)
            self.assertIn('na needs a reason and no evidence', text)
            self.assertNotIn('Every non-unknown state needs evidence', text)

    def test_shared_skill_rules_come_from_one_authored_source(self):
        runbook = (ROOT / generator.RUNBOOK_REF).read_text()
        changed = runbook.replace('Record the bound schema', 'Record the exact bound schema', 1)
        for auditor in self.system['auditors']:
            path, content = generator.render_shared_skill(auditor, changed)
            self.assertIn('Record the exact bound schema', content.decode())
            self.assertNotEqual(path.read_bytes(), content)
        with self.assertRaises(generator.GenerationError):
            generator.render_shared_skill(self.system['auditors'][0], changed.replace(
                '<!-- AUTHORING:END auditor-shared:activation -->', ''))

    def test_catalog_policy_projection_does_not_create_a_second_policy_source(self):
        runbook = (ROOT / generator.RUNBOOK_REF).read_text()
        changed = copy.deepcopy(self.catalog)
        changed['frameworks']['ROAS']['veto_items'] = ['R1']
        projected = generator.render_policy_runbook(runbook, changed)
        section = projected.split('<!-- GENERATED:BEGIN auditor-policy:vetoes -->')[1].split(
            '<!-- GENERATED:END auditor-policy:vetoes -->')[0]
        row = next(line for line in section.splitlines() if line.startswith('| ROAS |'))
        self.assertIn('`ROAS-R1`', row)
        self.assertNotIn('`ROAS-R2`', row)

    def test_public_projection_mode_is_stable_under_restrictive_umask(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'public.md'
            previous = os.umask(0o077)
            try:
                generator.atomic_write(path, b'public source\n')
            finally:
                os.umask(previous)
            self.assertEqual(b'public source\n', path.read_bytes())
            self.assertEqual(0o644, path.stat().st_mode & 0o777)

    def test_all_profile_views_come_from_catalog_and_preserve_authored_guidance(self):
        count = 0
        for framework in self.catalog['frameworks'].values():
            text = (ROOT / framework['source']).read_text()
            projected = generator.render_profile_policy(text, framework)
            begin = '<!-- GENERATED:BEGIN auditor-policy:profiles -->'
            end = '<!-- GENERATED:END auditor-policy:profiles -->'
            self.assertEqual(text.split(begin)[0], projected.split(begin)[0])
            self.assertEqual(text.split(end)[1], projected.split(end)[1])
            region = projected.split(begin)[1].split(end)[0]
            for name in framework['profiles']:
                self.assertIn('| `' + name + '` |', region)
                count += 1
        self.assertEqual(37, count)
        echo = self.catalog['frameworks']['ECHO']
        view = generator.render_profile_policy((ROOT / echo['source']).read_text(), echo)
        self.assertIn('E 28.5% · H 21.5% · O 50%', view)
        self.assertIn('include_items:', view)


if __name__ == "__main__":
    unittest.main()
