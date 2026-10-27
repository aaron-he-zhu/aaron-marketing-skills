"""Fixed factual boundary examples, independent of the production item compiler.

These tests freeze the published examples and exercise their resulting states
through the original scorer. They do not classify arbitrary natural-language
evidence or substitute for the separate human reliability/outcome study.
"""
import copy
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
CATALOG = json.loads((ROOT / 'references/framework-catalog.json').read_text())
FIXTURE = json.loads((ROOT / 'tests/fixtures/benchmark-boundary-cases.json').read_text())
SPEC = importlib.util.spec_from_file_location('boundary_rubric_score', ROOT / 'scripts/rubric-score.py')
scorer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scorer)
PROFILES = {
    'CORE-EEAT': 'blog-post', 'CITE': 'default', 'STAR': 'awareness',
    'ROAS': 'direct-response', 'SEND': 'newsletter', 'RAMP': 'outcome',
    'ECHO': 'asset-gate', 'TALE': 'system',
}
EXPECTED_ITEMS = {
    'CORE-EEAT': {'A05', 'C03', 'R01', 'R02', 'O04'}, 'CITE': {'C01'},
    'STAR': {'S2', 'S6', 'A3'}, 'ROAS': {'R3', 'R4', 'R5', 'A5', 'S4'},
    'SEND': {'E2', 'N1', 'D2'}, 'RAMP': {'P6'}, 'ECHO': {'C3'}, 'TALE': {'A9'},
}


def documented_framework(name):
    text = (ROOT / 'references/benchmark-boundary-examples.md').read_text()
    section = text.split('## ' + name + '\n', 1)[1].split('\n## ', 1)[0]
    return '## Fixed Boundary Cases (2026-10-27-a)\n' + section


def documented_cases(text):
    """Read only the worked-example table, not the authoritative item parser."""
    section = text.split('## Fixed Boundary Cases (2026-10-27-a)\n', 1)[1].split('\n## ', 1)[0]
    result = {}
    for line in section.splitlines():
        if not line.startswith('|'):
            continue
        cells = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if cells[0] == 'Case' or set(cells[0]) <= {'-'}:
            continue
        if len(cells) != 4 or cells[0] in result:
            raise ValueError('ambiguous worked example')
        result[cells[0]] = {
            'item': cells[1], 'facts': json.loads(cells[2].strip('`')),
            'expected_state': cells[3],
        }
    return result


def assert_fixed_examples(test, text, cases):
    actual = documented_cases(text)
    expected = {row['case']: {key: row[key] for key in ('item', 'facts', 'expected_state')}
                for row in cases}
    test.assertEqual(expected, actual)


def complete_run(case):
    name = case['framework']
    spec = CATALOG['frameworks'][name]
    profile = PROFILES[name]
    context = {key: 'boundary-fixture' for key in spec['required_context']}
    context.update(spec['profiles'][profile].get('context_equals', {}))
    if name == 'STAR':
        context['assessment_time'] = 'actual'
    evidence = {
        'type': 'measured', 'source': 'fixed synthetic boundary fixture: ' + case['case'],
        'observed_at': '2026-10-27', 'confidence': 'high',
    }
    items = [{'id': item_id, 'state': 'pass', 'evidence': evidence}
             for ids in scorer.expected_items(spec, profile).values() for item_id in ids]
    observation = next(item for item in items if item['id'] == case['item'])
    state = case['expected_state']
    observation.clear()
    observation.update(id=case['item'], state=state)
    if state in {'unknown', 'na'}:
        observation['reason'] = case['facts'].get('reason', 'Declared required observation is unavailable in this frozen case.')
    else:
        observation['evidence'] = evidence
    return {
        'framework': name, 'profile': profile, 'target': case['case'],
        'observed_at': '2026-10-27', 'context': context, 'items': items,
    }


class BenchmarkAnchorTests(unittest.TestCase):
    def test_eighty_catalog_criterion_copies_are_retired_but_policy_is_present(self):
        for name, framework in CATALOG['frameworks'].items():
            with self.subTest(framework=name):
                self.assertNotIn('item_definitions', framework)
                self.assertIn('item_policies', framework)
        schema = json.loads((ROOT / 'references/framework-catalog.schema.json').read_text())
        self.assertIn('item_definitions', schema['$defs']['framework']['properties'])
        legacy = copy.deepcopy(CATALOG)
        legacy['frameworks']['STAR']['item_definitions'] = {'S2': 'legacy optional criterion'}
        self.assertEqual([], scorer.validate_catalog(legacy))

    def test_fixed_case_population_preserves_the_twenty_reviewed_items(self):
        by_framework = {}
        ids = []
        for case in FIXTURE['cases']:
            by_framework.setdefault(case['framework'], set()).add(case['item'])
            ids.append(case['case'])
            self.assertIsInstance(case['facts'], dict)
            self.assertTrue(case['facts'])
            self.assertIn(case['expected_state'], {'pass', 'partial', 'fail', 'unknown', 'na'})
        self.assertEqual(70, len(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(EXPECTED_ITEMS, by_framework)

    def test_documented_facts_and_states_match_fixed_expectations(self):
        for name, framework in CATALOG['frameworks'].items():
            with self.subTest(framework=name):
                cases = [case for case in FIXTURE['cases'] if case['framework'] == name]
                assert_fixed_examples(self, documented_framework(name), cases)

    def test_numeric_boundary_oracles_use_facts_not_parser_output(self):
        for case in FIXTURE['cases']:
            if case['framework'] != 'CORE-EEAT':
                continue
            facts = case['facts']
            if case['item'] == 'C03':
                count = facts['secondary_intents']
                expected = 'pass' if count >= 3 else 'partial' if count >= 1 else 'fail'
            elif case['item'] == 'R01':
                count = facts['distinct_relevant_measurements']
                expected = 'pass' if count >= 5 else 'partial' if count >= 1 else 'fail'
            elif case['item'] == 'R02':
                if facts['words'] is None:
                    expected = 'unknown'
                elif facts['claim_linked_citations'] * 500 >= facts['words'] and facts['source_types'] >= 3:
                    expected = 'pass'
                elif facts['claim_linked_citations'] * 1000 >= facts['words'] and facts['source_types'] >= 2:
                    expected = 'partial'
                else:
                    expected = 'fail'
            else:
                continue
            with self.subTest(case=case['case']):
                self.assertEqual(expected, case['expected_state'])

    def test_fixed_states_keep_unknown_na_and_veto_scoring_distinct(self):
        for case in FIXTURE['cases']:
            with self.subTest(case=case['case']):
                result = scorer.score_run(complete_run(case), CATALOG)
                state = case['expected_state']
                veto = case['item'] in CATALOG['frameworks'][case['framework']]['veto_items']
                if state == 'unknown':
                    self.assertEqual('NOT_SCORED', result['score_state'])
                    self.assertEqual('UNDECIDED', result['verdict'])
                    self.assertEqual(0, result['veto_count'])
                    self.assertLess(result['evidence_coverage'], 100)
                else:
                    self.assertEqual('SCORED', result['score_state'])
                    self.assertEqual(100, result['evidence_coverage'])
                    self.assertEqual(int(state == 'fail' and veto), result['veto_count'])
                    if state == 'fail' and veto:
                        self.assertTrue(result['cap_applied'])
                        self.assertEqual(59, result['final_overall_score'])
                    elif state == 'na':
                        self.assertEqual(100, result['final_overall_score'])

    def test_changing_a_case_to_the_old_unknown_equals_fail_rule_is_caught(self):
        text = documented_framework('CORE-EEAT')
        original = next(line for line in text.splitlines() if line.startswith('| brand-unobserved |'))
        altered = text.replace(original, original.rsplit('unknown', 1)[0] + 'fail |', 1)
        cases = [case for case in FIXTURE['cases'] if case['framework'] == 'CORE-EEAT']
        with self.assertRaises(AssertionError):
            assert_fixed_examples(self, altered, cases)

    def test_changed_observed_facts_cannot_reuse_the_old_case_label(self):
        text = documented_framework('CITE')
        altered = text.replace('"referring_domains":30', '"referring_domains":3', 1)
        self.assertTrue(text != altered)
        cases = [case for case in FIXTURE['cases'] if case['framework'] == 'CITE']
        with self.assertRaises(AssertionError):
            assert_fixed_examples(self, altered, cases)


if __name__ == '__main__':
    unittest.main()
