"""Independent frozen public identities and numerical-policy regression gate."""
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = json.loads((ROOT / 'tests/fixtures/v3-compatibility-baseline.json').read_text())


class V3CompatibilityTests(unittest.TestCase):
    def test_every_original_skill_path_slug_and_install_entry_is_preserved(self):
        expected = {row['path']: row for row in BASELINE['skills']}
        plugin = json.loads((ROOT / '.claude-plugin/plugin.json').read_text())
        actual = {p.removeprefix('./').rstrip('/') + '/SKILL.md' for p in plugin['skills']}
        self.assertEqual(set(expected), actual)
        for relative, identity in expected.items():
            with self.subTest(skill=identity['name']):
                text = (ROOT / relative).read_text()
                self.assertEqual(identity['name'], re.search(r'^name:\s*(.+)$', text, re.M)[1])
                self.assertEqual(identity['slug'], re.search(r'^slug:\s*(.+)$', text, re.M)[1])
                self.assertEqual('/skills/s/' + identity['name'], identity['url'])
                self.assertIn('## Quick Start', text)

    def test_all_item_and_profile_identities_and_numerical_policies_are_preserved(self):
        current = json.loads((ROOT / 'references/framework-catalog.json').read_text())
        self.assertEqual(BASELINE['semantics'], current['semantics'])
        self.assertEqual(set(BASELINE['frameworks']), set(current['frameworks']))
        for name, frozen in BASELINE['frameworks'].items():
            with self.subTest(framework=name):
                spec = current['frameworks'][name]
                ids = [f'{name}-{d["item_prefix"]}{i:0{d["id_width"]}d}'
                       for d in spec['dimensions'].values()
                       for i in range(1, d['item_count'] + 1)]
                self.assertEqual(frozen['item_ids'], ids)
                self.assertEqual(frozen['profiles'], list(spec['profiles']))
                policy = {k: v for k, v in spec.items()
                          if k not in {'source', 'construct', 'unit_of_analysis', 'item_definitions'}}
                policy['dimensions'] = {
                    k: {a: b for a, b in v.items() if a != 'name'}
                    for k, v in spec['dimensions'].items()
                }
                content = json.dumps(policy, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()
                self.assertEqual(frozen['policy_sha256'], hashlib.sha256(content).hexdigest())


if __name__ == '__main__':
    unittest.main()
