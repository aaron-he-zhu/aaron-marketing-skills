"""Selection profile and semantic change-impact regression tests."""
from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import sys
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location("eval_cases_profiles", ROOT / "scripts/eval_cases.py")
assert SPEC and SPEC.loader
eval_cases = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = eval_cases
SPEC.loader.exec_module(eval_cases)


class BehaviorProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_cases = eval_cases.load_cases(ROOT)
        cls.derived_cases = eval_cases.load_derived_auditor_cases(ROOT)

    def test_profiles_and_generated_auditor_cases_are_complete(self):
        profiles = eval_cases.load_profiles(ROOT)
        self.assertEqual(set(profiles), {"smoke", "change-aware", "nightly"})
        self.assertEqual(len(profiles["smoke"]["case_ids"]), 24)
        self.assertEqual(len(self.derived_cases), 40)
        self.assertEqual(
            {case["target_skill"] for case in self.derived_cases},
            set(eval_cases._catalog_index(eval_cases.load_catalog(ROOT))["auditors"]),
        )
        self.assertEqual(
            sum(case["id"].endswith("-missing-evidence") for case in self.derived_cases),
            8,
        )

    def test_smoke_is_the_fixed_24_case_assessment_set(self):
        result = eval_cases.select_cases(
            ROOT,
            "smoke",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
        )
        expected = eval_cases.load_profiles(ROOT)["smoke"]["case_ids"]
        self.assertEqual(result["case_ids"], expected)
        self.assertEqual(len(result["cases"]), 24)
        self.assertTrue(
            all(reasons == ["profile:smoke-fixed"] for reasons in result["selection_reasons"].values())
        )

    def test_nightly_selects_all_734_without_truncation(self):
        result = eval_cases.select_cases(
            ROOT,
            "nightly",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
        )
        self.assertEqual(len(result["cases"]), 734)
        self.assertEqual(result["provenance"]["available_count"], 734)
        self.assertEqual(result["provenance"]["selected_count"], 734)

    def test_skill_change_adds_every_case_for_that_target(self):
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=["seo-geo/implement/content-writer/SKILL.md"],
        )
        selected = {case["id"] for case in result["cases"]}
        impacted = {
            case["id"]
            for case in self.base_cases + self.derived_cases
            if case["target_skill"] == "content-writer"
        }
        self.assertTrue(impacted)
        self.assertTrue(impacted <= selected)
        for case_id in impacted:
            self.assertIn(
                "change:skill-contract:%s"
                % hashlib.sha256(
                    b"seo-geo/implement/content-writer/SKILL.md"
                ).hexdigest(),
                result["selection_reasons"][case_id],
            )
        for reasons in result["selection_reasons"].values():
            for reason in reasons:
                self.assertRegex(reason, r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
                self.assertLessEqual(len(reason), 160)

    def test_case_source_change_adds_every_case_from_that_file(self):
        path = "evals/content-writer/cases.md"
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=[path],
        )
        impacted = {case["id"] for case in self.base_cases if case["source_ref"] == path}
        self.assertTrue(impacted)
        self.assertTrue(impacted <= set(result["case_ids"]))

    def test_prompt_contract_change_adds_every_case_for_that_auditor(self):
        path = "references/prompt-contracts/content-quality-auditor.json"
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=[path],
        )
        all_cases = self.base_cases + self.derived_cases
        impacted = {
            case["id"]
            for case in all_cases
            if case["target_skill"] == "content-quality-auditor"
        }
        authored = {
            case["id"]
            for case in self.base_cases
            if case["target_skill"] == "content-quality-auditor"
        }
        derived = {
            case["id"]
            for case in self.derived_cases
            if case["target_skill"] == "content-quality-auditor"
        }
        self.assertTrue(authored)
        self.assertTrue(derived)
        self.assertTrue(impacted <= set(result["case_ids"]))
        reason = "change:prompt-contract:%s" % hashlib.sha256(
            path.encode("utf-8")
        ).hexdigest()
        for case_id in impacted:
            self.assertIn(reason, result["selection_reasons"][case_id])

    def test_shared_prompt_contract_changes_add_every_auditor_case(self):
        auditors = set(
            eval_cases._catalog_index(eval_cases.load_catalog(ROOT))["auditors"]
        )
        impacted = {
            case["id"]
            for case in self.base_cases + self.derived_cases
            if case["target_skill"] in auditors
        }
        for path in (
            "references/prompt-contracts/index.json",
            "scripts/generate-auditor-prompt-contracts.py",
        ):
            with self.subTest(path=path):
                result = eval_cases.select_cases(
                    ROOT,
                    "change-aware",
                    cases=self.base_cases,
                    derived_cases=self.derived_cases,
                    changed_paths=[path],
                )
                self.assertTrue(impacted <= set(result["case_ids"]))
                self.assertEqual(result["provenance"]["unmatched_paths"], [])

    def test_adapter_schema_and_framework_catalog_changes_are_matched(self):
        changed_paths = [
            "scripts/adapters/codex-behavior-adapter.py",
            "evals/codex-behavior-candidate-output.schema.json",
            "evals/codex-behavior-routing-output.schema.json",
            "evals/codex-behavior-model-output.schema.json",
            "references/framework-catalog.json",
        ]
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=changed_paths,
        )
        self.assertEqual(result["provenance"]["unmatched_paths"], [])

    def test_git_diff_includes_type_changes(self):
        commit = "a" * 40
        with mock.patch.object(eval_cases.subprocess, "run") as run:
            run.side_effect = [
                mock.Mock(returncode=0, stdout=commit + "\n", stderr=""),
                mock.Mock(returncode=0, stdout=commit + "\n", stderr=""),
                mock.Mock(returncode=0, stdout=b"type-changed\x00", stderr=b""),
            ]
            changed = eval_cases.changed_paths_from_git(ROOT, "base", "head")

        self.assertEqual(changed, ["type-changed"])
        diff_command = run.call_args_list[2].args[0]
        self.assertIn("--diff-filter=ACMRDT", diff_command)

    def test_global_change_selects_all_cases_without_an_arbitrary_cap(self):
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=["references/system-catalog.json"],
        )
        self.assertEqual(len(result["cases"]), 734)
        self.assertEqual(result["provenance"]["unmatched_paths"], [])

    def test_unmatched_change_falls_back_to_smoke_and_is_reported(self):
        result = eval_cases.select_cases(
            ROOT,
            "change-aware",
            cases=self.base_cases,
            derived_cases=self.derived_cases,
            changed_paths=["README.md"],
        )
        self.assertEqual(len(result["cases"]), 24)
        self.assertEqual(result["provenance"]["unmatched_paths"], ["README.md"])

    def test_invalid_git_ref_and_changed_path_fail_closed(self):
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "base_ref does not resolve"):
            eval_cases.select_cases(
                ROOT,
                "change-aware",
                cases=self.base_cases,
                derived_cases=self.derived_cases,
                base_ref="refs/heads/definitely-does-not-exist",
            )
        with self.assertRaisesRegex(eval_cases.EvalCaseError, "unsafe or non-canonical"):
            eval_cases.select_cases(
                ROOT,
                "change-aware",
                cases=self.base_cases,
                derived_cases=self.derived_cases,
                changed_paths=["../escape"],
            )


if __name__ == "__main__":
    unittest.main()
