"""Strict parser/provenance regression tests for the behavior-eval corpus."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("eval_cases", ROOT / "scripts/eval_cases.py")
assert SPEC and SPEC.loader
eval_cases = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = eval_cases
SPEC.loader.exec_module(eval_cases)


class FlowParserTests(unittest.TestCase):
    def test_parses_the_supported_single_line_subset(self):
        value = eval_cases.parse_flow_object(
            '{id: example-001, type: eval-case, status: simulated, '
            'target_skill: example-skill, scenario: "A {brace} and colon: value", '
            'input_summary: "input", expected_behavior: ["one","two"], '
            'failure_modes: ["bad"]}'
        )
        self.assertEqual(value["id"], "example-001")
        self.assertEqual(value["scenario"], "A {brace} and colon: value")
        self.assertEqual(value["expected_behavior"], ["one", "two"])

    def test_rejects_duplicate_unknown_and_malformed_fields(self):
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "duplicate key"):
            eval_cases.parse_flow_object("{id: one, id: two}")
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "trailing commas"):
            eval_cases.parse_flow_object("{id: one,}")
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "nested mappings"):
            eval_cases.parse_flow_object("{id: {nested: no}}")
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "one text line"):
            eval_cases.parse_flow_object("{id: one}\n{id: two}")

    def test_rejects_non_subset_scalars(self):
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "invalid bare value"):
            eval_cases.parse_flow_object("{id: @not-supported}")


class CorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = eval_cases.load_cases(ROOT)

    def test_loads_exact_current_authored_and_routing_counts(self):
        authored = [case for case in self.cases if case["source_group"] == "authored"]
        routing = [case for case in self.cases if case["source_group"] == "auto-routing"]
        self.assertEqual(len(authored), 572)
        self.assertEqual(len(routing), 88)
        self.assertEqual(len(self.cases), 660)
        self.assertEqual(len({case["id"] for case in self.cases}), 660)

    def test_every_case_has_the_exact_runner_request_shape(self):
        expected = set(eval_cases.RUNNER_CASE_FIELDS)
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(set(case), expected)
                self.assertEqual(case["type"], "eval-case")
                self.assertIn(case["case_provenance"], {"simulated", "real"})
                if case["case_provenance"] == "simulated":
                    self.assertIsNone(case["evidence_binding"])
                else:
                    self.assertIsInstance(case["evidence_binding"], dict)
                    self.assertEqual(
                        set(case["evidence_binding"]), {"ref", "sha256"}
                    )
                    self.assertRegex(
                        case["evidence_binding"]["ref"],
                        eval_cases.SAFE_REF_RE,
                    )
                    self.assertRegex(
                        case["evidence_binding"]["sha256"], r"^[0-9a-f]{64}$"
                    )
                self.assertRegex(case["case_sha256"], r"^[0-9a-f]{64}$")
                self.assertGreaterEqual(case["source_line"], 1)

    def test_case_hash_and_source_provenance_are_deterministic(self):
        again = eval_cases.load_cases(ROOT)
        self.assertEqual(self.cases, again)
        target = next(case for case in self.cases if case["id"] == "auto-competitor-gap-001")
        self.assertEqual(target["source_ref"], "evals/auto-routing-scenarios.source.md")
        self.assertEqual(target["source_group"], "auto-routing")
        self.assertGreater(target["source_line"], 1)

    def test_authored_target_must_match_its_catalog_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._minimal_root(Path(directory))
            case_path = root / "evals/example-skill/cases.md"
            case_path.write_text(self._case(target="other-skill") + "\n", encoding="utf-8")
            with self.assertRaisesRegex(eval_cases.EvalCaseError, "unknown target_skill"):
                eval_cases.load_cases(root, include_auto=False)

    def test_unknown_source_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._minimal_root(Path(directory))
            case_path = root / "evals/example-skill/cases.md"
            case_path.write_text(
                self._case()[:-1] + ", invented: \"no\"}\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(eval_cases.EvalCaseError, "unknown fields: invented"):
                eval_cases.load_cases(root, include_auto=False)

    def test_malformed_case_candidate_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._minimal_root(Path(directory))
            case_path = root / "evals/example-skill/cases.md"
            case_path.write_text(self._case()[:-1] + "\n", encoding="utf-8")
            with self.assertRaises(eval_cases.EvalCaseError):
                eval_cases.load_cases(root, include_auto=False)

    def test_real_case_requires_existing_hash_matching_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self._minimal_root(Path(directory))
            evidence = root / "evidence/report.json"
            evidence.parent.mkdir()
            evidence.write_text('{"signal":"real"}\n', encoding="utf-8")
            digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
            case_path = root / "evals/example-skill/cases.md"
            real_case = self._case().replace(
                "status: simulated",
                'status: real, evidence_ref: "evidence/report.json", '
                'evidence_sha256: "%s"' % digest,
            )
            case_path.write_text(real_case + "\n", encoding="utf-8")
            loaded = eval_cases.load_cases(root, include_auto=False)[0]
            self.assertEqual(loaded["case_provenance"], "real")
            self.assertEqual(
                loaded["evidence_binding"],
                {"ref": "evidence/report.json", "sha256": digest},
            )

            case_path.write_text(real_case.replace(digest, "0" * 64) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(eval_cases.EvalCaseError, "does not match"):
                eval_cases.load_cases(root, include_auto=False)

            case_path.write_text(
                real_case.replace("evidence/report.json", "evidence/missing.json") + "\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(eval_cases.EvalCaseError, "cannot open"):
                eval_cases.load_cases(root, include_auto=False)

    def test_intermediate_directory_symlink_cannot_escape_project(self):
        if not hasattr(Path, "symlink_to"):
            self.skipTest("symbolic links unavailable")
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            outside_root = Path(outside)
            (outside_root / "system-catalog.json").write_text("{}", encoding="utf-8")
            try:
                (root / "references").symlink_to(outside_root, target_is_directory=True)
            except OSError as exc:
                self.skipTest("symbolic links unavailable: %s" % exc)
            with self.assertRaisesRegex(eval_cases.EvalCaseError, "cannot open"):
                eval_cases.load_catalog(root)

    @staticmethod
    def _case(target="example-skill"):
        return (
            "{id: example-001, type: eval-case, status: simulated, "
            "target_skill: %s, scenario: \"scenario\", input_summary: \"input\", "
            "expected_behavior: [\"expected\"], failure_modes: [\"failure\"]}"
            % target
        )

    @staticmethod
    def _minimal_root(root: Path) -> Path:
        (root / "references").mkdir(parents=True)
        catalog = {
            "logical_order": ["example", "protocol"],
            "disciplines": {
                "example": {
                    "phase_order": ["phase"],
                    "command": {"name": "example"},
                    "gates": ["example-skill"],
                    "phases": {"phase": ["example-skill"]},
                }
            },
            "protocol": {"skills": []},
        }
        (root / "references/system-catalog.json").write_text(
            json.dumps(catalog), encoding="utf-8"
        )
        (root / "example/phase/example-skill").mkdir(parents=True)
        (root / "example/phase/example-skill/SKILL.md").write_text("# skill\n", encoding="utf-8")
        (root / "evals/example-skill").mkdir(parents=True)
        (root / "evals/example-skill/cases.md").write_text(
            CorpusTests._case() + "\n", encoding="utf-8"
        )
        return root


class IndexValidationTests(unittest.TestCase):
    def test_duplicate_ids_are_rejected(self):
        case = eval_cases.load_cases(ROOT, include_auto=False)[0]
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "duplicate eval case id"):
            eval_cases.index_cases([case, dict(case)])

    def test_request_shape_is_exact(self):
        case = eval_cases.load_cases(ROOT, include_auto=False)[0]
        altered = dict(case)
        altered["extra"] = True
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "exact request fields"):
            eval_cases.index_cases([altered])

    def test_source_group_is_the_runner_v2_enum(self):
        case = eval_cases.load_cases(ROOT, include_auto=False)[0]
        altered = dict(case)
        altered["source_group"] = "authored:seo-geo"
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "invalid source_group"):
            eval_cases.index_cases([altered])


if __name__ == "__main__":
    unittest.main()
