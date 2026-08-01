import copy
import datetime as dt
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "engineering_maturity", ROOT / "scripts" / "check-engineering-maturity.py",
)
maturity = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = maturity
SPEC.loader.exec_module(maturity)


class EngineeringMaturityTests(unittest.TestCase):
    def rubric(self):
        return json.loads(
            (ROOT / "references/engineering-maturity-rubric.json").read_text(
                encoding="utf-8",
            )
        )

    def test_repository_rubric_is_exactly_five_by_twenty(self):
        rubric = maturity.validate_rubric(self.rubric())
        self.assertEqual(95, rubric["target_score"])
        self.assertEqual(90, rubric["hard_gate_cap"])
        self.assertEqual(
            {"prompt", "context", "harness", "loop", "graph"},
            set(rubric["dimensions"]),
        )
        self.assertEqual(100, sum(map(len, rubric["dimensions"].values())))
        self.assertEqual(100, len({
            control["id"]
            for controls in rubric["dimensions"].values()
            for control in controls
        }))

    def test_rubric_rejects_unknown_fields_and_identity_drift(self):
        unknown = self.rubric()
        unknown["bonus"] = True
        with self.assertRaisesRegex(maturity.MaturityError, "unknown or missing"):
            maturity.validate_rubric(unknown)

        missing = self.rubric()
        missing["dimensions"]["prompt"].pop()
        with self.assertRaisesRegex(maturity.MaturityError, "exactly 20"):
            maturity.validate_rubric(missing)

        reordered = self.rubric()
        reordered["dimensions"]["loop"][0]["id"] = "L20"
        with self.assertRaisesRegex(maturity.MaturityError, "identity/order"):
            maturity.validate_rubric(reordered)

    def test_nineteen_controls_reach_95_but_failed_hard_gate_caps_at_90(self):
        controls = copy.deepcopy(self.rubric()["dimensions"]["prompt"])
        facts = {
            control["id"]: maturity.Fact(True, "verified") for control in controls
        }
        non_hard = next(control for control in controls if not control["hard_gate"])
        facts[non_hard["id"]] = maturity.Fact(False, "failed")
        _rows, raw, final, failed_hard = maturity.score_dimension(
            controls, facts, 5, 90,
        )
        self.assertEqual((95, 95, []), (raw, final, failed_hard))

        hard = next(control for control in controls if control["hard_gate"])
        facts = {
            control["id"]: maturity.Fact(True, "verified") for control in controls
        }
        facts[hard["id"]] = maturity.Fact(False, "failed hard gate")
        rows, raw, final, failed_hard = maturity.score_dimension(
            controls, facts, 5, 90,
        )
        self.assertEqual((95, 90, [hard["id"]]), (raw, final, failed_hard))
        self.assertEqual(0, next(row for row in rows if row["id"] == hard["id"])["points"])

    def test_current_report_mapping_is_complete_and_missing_real_evidence_fails_closed(self):
        evaluated_at = dt.datetime(2026, 7, 22, 12, 0, tzinfo=dt.timezone.utc)
        result = maturity.audit(
            ROOT, run_dynamic=False, evidence_run_id=None, evaluated_at=evaluated_at,
        )
        schema = json.loads(
            (ROOT / "references/engineering-maturity-report.schema.json").read_text(
                encoding="utf-8",
            )
        )
        self.assertEqual(set(schema["required"]), set(result))
        self.assertEqual("2026-07-22T12:00:00Z", result["evaluated_at"])
        self.assertFalse(result["achieved"])
        self.assertIsNone(result["semantic_evidence"])
        self.assertEqual(100, sum(
            len(item["controls"]) for item in result["dimensions"].values()
        ))
        self.assertIn("P19", result["dimensions"]["prompt"]["failed_hard_gates"])
        self.assertIn("H20", result["dimensions"]["harness"]["failed_hard_gates"])
        self.assertRegex(result["checker"]["sha256"], r"^[0-9a-f]{64}$")

    def test_semantic_report_schema_covers_the_complete_hash_bound_summary(self):
        schema = json.loads(
            (ROOT / "references/engineering-maturity-report.schema.json").read_text(
                encoding="utf-8",
            )
        )
        semantic = schema["$defs"]["semantic_evidence"]
        required = set(semantic["required"])
        properties = set(semantic["properties"])
        self.assertEqual(required, properties)
        self.assertTrue({
            "total_judge_attempts",
            "retried_cases",
            "judge_protocol_retries",
            "selection_sha256",
            "protocol_schema_sha256",
            "result_stream_sha256",
            "head_record_hash",
        }.issubset(required))

    def test_p18_requires_semantic_suite_and_every_named_regression(self):
        runner_text = (ROOT / "scripts/run-behavior-evals.py").read_text(encoding="utf-8")
        semantic_tests = (ROOT / "tests/test_behavior_evals_adapter.py").read_text(
            encoding="utf-8",
        )
        adapter_tests = (ROOT / "tests/test_codex_behavior_adapter.py").read_text(
            encoding="utf-8",
        )
        passing_suite = maturity.Fact(True, "semantic request suite passed")
        self.assertTrue(
            maturity.p18_fact(
                passing_suite, runner_text, semantic_tests, adapter_tests,
            ).passed
        )
        failed_suite = maturity.p18_fact(
            maturity.Fact(False, "suite failed"),
            runner_text, semantic_tests, adapter_tests,
        )
        self.assertFalse(failed_suite.passed)
        self.assertIn("semantic_request_suite", failed_suite.evidence)

        for symbol in maturity.P18_RUNNER_SYMBOLS:
            with self.subTest(kind="runner-symbol", name=symbol):
                marker = "def %s(" % symbol
                self.assertIn(marker, runner_text)
                mutated = runner_text.replace(marker, "def removed_p18_symbol(", 1)
                fact = maturity.p18_fact(
                    passing_suite, mutated, semantic_tests, adapter_tests,
                )
                self.assertFalse(fact.passed)
                self.assertIn("runner:%s" % symbol, fact.evidence)

        for test_name in maturity.P18_SEMANTIC_REQUEST_TESTS:
            with self.subTest(kind="semantic-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, semantic_tests)
                mutated = semantic_tests.replace(marker, "def removed_p18_test(", 1)
                fact = maturity.p18_fact(
                    passing_suite, runner_text, mutated, adapter_tests,
                )
                self.assertFalse(fact.passed)
                self.assertIn("semantic-test:%s" % test_name, fact.evidence)

        for test_name in maturity.P18_CODEX_ADAPTER_TESTS:
            with self.subTest(kind="adapter-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, adapter_tests)
                mutated = adapter_tests.replace(marker, "def removed_p18_test(", 1)
                fact = maturity.p18_fact(
                    passing_suite, runner_text, semantic_tests, mutated,
                )
                self.assertFalse(fact.passed)
                self.assertIn("adapter-test:%s" % test_name, fact.evidence)

    def test_h17_requires_pinned_release_helpers_and_every_adversarial_regression(self):
        common = (ROOT / "scripts/publish-common.sh").read_text(encoding="utf-8")
        sync_about = (ROOT / "scripts/sync-about.sh").read_text(encoding="utf-8")
        sync_family = (ROOT / "scripts/sync-family.sh").read_text(encoding="utf-8")
        publisher_tests = (ROOT / "tests/test_publish_release.py").read_text(
            encoding="utf-8",
        )
        publishers = []
        for path in sorted((ROOT / "scripts").glob("publish*.sh")):
            text = path.read_text(encoding="utf-8")
            if "--live" in text or "PUBLISH_LIVE" in text or "publish" in path.name:
                publishers.append((path.name, text))
        passing_suite = maturity.Fact(True, "publisher suite passed")
        self.assertTrue(maturity.h17_fact(
            passing_suite, publishers, common, sync_about, sync_family, publisher_tests,
        ).passed)
        self.assertFalse(maturity.h17_fact(
            maturity.Fact(False, "suite failed"), publishers, common,
            sync_about, sync_family, publisher_tests,
        ).passed)

        for symbol in maturity.H17_COMMON_SYMBOLS:
            with self.subTest(kind="common-symbol", name=symbol):
                marker = "%s()" % symbol
                self.assertIn(marker, common)
                mutated = common.replace(marker, "removed_h17_symbol()", 1)
                fact = maturity.h17_fact(
                    passing_suite, publishers, mutated,
                    sync_about, sync_family, publisher_tests,
                )
                self.assertFalse(fact.passed)
                self.assertIn("common:%s" % symbol, fact.evidence)

        for path, markers in maturity.H17_PUBLISHER_WIRING.items():
            for marker in markers:
                with self.subTest(kind="publisher-wiring", name=path, marker=marker):
                    mutated_publishers = [
                        (name, text.replace(marker, "removed-h17-wiring", 1))
                        if name == path else (name, text)
                        for name, text in publishers
                    ]
                    fact = maturity.h17_fact(
                        passing_suite, mutated_publishers, common,
                        sync_about, sync_family, publisher_tests,
                    )
                    self.assertFalse(fact.passed)
                    self.assertIn("publisher-wiring:%s" % path, fact.evidence)

        for test_name in maturity.H17_PUBLISHER_TESTS:
            with self.subTest(kind="publisher-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, publisher_tests)
                mutated = publisher_tests.replace(marker, "def removed_h17_test(", 1)
                fact = maturity.h17_fact(
                    passing_suite, publishers, common,
                    sync_about, sync_family, mutated,
                )
                self.assertFalse(fact.passed)
                self.assertIn("publisher-test:%s" % test_name, fact.evidence)

    def test_h19_requires_bounded_judge_recovery_and_hash_bound_ledger_proof(self):
        adapter = (ROOT / "scripts/adapters/codex-behavior-adapter.py").read_text(
            encoding="utf-8",
        )
        runner = (ROOT / "scripts/run-behavior-evals.py").read_text(encoding="utf-8")
        verifier = (ROOT / "scripts/verify-semantic-evidence.py").read_text(
            encoding="utf-8",
        )
        behavior_tests = (ROOT / "tests/test_behavior_evals_adapter.py").read_text(
            encoding="utf-8",
        )
        adapter_tests = (ROOT / "tests/test_codex_behavior_adapter.py").read_text(
            encoding="utf-8",
        )
        verifier_tests = (ROOT / "tests/test_semantic_evidence_verifier.py").read_text(
            encoding="utf-8",
        )
        policy = json.loads(
            (ROOT / "evals/semantic-evidence-policy.json").read_text(encoding="utf-8")
        )
        ci = (ROOT / ".github/workflows/validate-skill.yml").read_text(encoding="utf-8")
        suites = json.loads(
            (ROOT / "evals/deterministic-suites.json").read_text(encoding="utf-8")
        )
        passing = maturity.Fact(True, "suite passed")

        def evaluate(
                adapter_text=adapter, runner_text=runner, verifier_text=verifier,
                behavior_text=behavior_tests, adapter_test_text=adapter_tests,
                verifier_test_text=verifier_tests, policy_value=policy,
                ci_text=ci, suite_value=suites, harness=passing, semantic=passing):
            return maturity.h19_fact(
                harness, semantic, adapter_text, runner_text, verifier_text,
                behavior_text, adapter_test_text, verifier_test_text,
                policy_value, ci_text, suite_value,
            )

        self.assertTrue(evaluate().passed)
        self.assertIn("ordered hash-bound", evaluate().evidence)
        self.assertIn("harness_suite", evaluate(
            harness=maturity.Fact(False, "failed"),
        ).evidence)
        self.assertIn("semantic_request_suite", evaluate(
            semantic=maturity.Fact(False, "failed"),
        ).evidence)

        for symbol in maturity.H19_ADAPTER_SYMBOLS:
            with self.subTest(kind="adapter-symbol", name=symbol):
                marker = "def %s(" % symbol
                self.assertIn(marker, adapter)
                fact = evaluate(adapter_text=adapter.replace(
                    marker, "def removed_h19_symbol(", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("adapter-symbol:%s" % symbol, fact.evidence)

        for marker in maturity.H19_ADAPTER_MARKERS:
            with self.subTest(kind="adapter-marker", marker=marker):
                self.assertIn(marker, adapter)
                fact = evaluate(adapter_text=adapter.replace(
                    marker, "removed-h19-adapter-marker", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("adapter-marker:%s" % marker, fact.evidence)

        v2_evaluate = maturity._top_level_function_source(adapter, "evaluate_request")
        v3_evaluate = maturity._top_level_function_source(adapter, "evaluate_request_v3")
        self.assertTrue(v2_evaluate)
        self.assertTrue(v3_evaluate)
        for marker in maturity.H19_V2_EVALUATE_MARKERS:
            with self.subTest(kind="adapter-v2-marker", marker=marker):
                self.assertIn(marker, v2_evaluate)
                # v3 intentionally contains the same control text. Removing it
                # from v2 must still fail H19 instead of matching the v3 copy.
                self.assertIn(marker, v3_evaluate)
                mutated_v2 = v2_evaluate.replace(
                    marker, "removed-h19-v2-evaluate-marker", 1,
                )
                mutated_adapter = adapter.replace(v2_evaluate, mutated_v2, 1)
                fact = evaluate(adapter_text=mutated_adapter)
                self.assertFalse(fact.passed)
                self.assertIn("adapter-v2-marker:%s" % marker, fact.evidence)

        for marker in maturity.H19_RUNNER_MARKERS:
            with self.subTest(kind="runner-marker", marker=marker):
                self.assertIn(marker, runner)
                fact = evaluate(runner_text=runner.replace(
                    marker, "removed-h19-runner-marker", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("runner-marker:%s" % marker, fact.evidence)

        for marker in maturity.H19_VERIFIER_MARKERS:
            with self.subTest(kind="verifier-marker", marker=marker):
                self.assertIn(marker, verifier)
                fact = evaluate(verifier_text=verifier.replace(
                    marker, "removed-h19-verifier-marker", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("verifier-marker:%s" % marker, fact.evidence)

        for test_name in maturity.H19_BEHAVIOR_EVAL_TESTS:
            with self.subTest(kind="behavior-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, behavior_tests)
                fact = evaluate(behavior_text=behavior_tests.replace(
                    marker, "def removed_h19_test(", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("behavior-test:%s" % test_name, fact.evidence)

        for test_name in maturity.H19_CODEX_ADAPTER_TESTS:
            with self.subTest(kind="adapter-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, adapter_tests)
                fact = evaluate(adapter_test_text=adapter_tests.replace(
                    marker, "def removed_h19_test(", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("adapter-test:%s" % test_name, fact.evidence)

        for test_name in maturity.H19_VERIFIER_TESTS:
            with self.subTest(kind="verifier-test", name=test_name):
                marker = "def %s(" % test_name
                self.assertIn(marker, verifier_tests)
                fact = evaluate(verifier_test_text=verifier_tests.replace(
                    marker, "def removed_h19_test(", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("verifier-test:%s" % test_name, fact.evidence)

        for marker in maturity.H19_VERIFIER_TEST_MARKERS:
            with self.subTest(kind="verifier-test-marker", marker=marker):
                self.assertIn(marker, verifier_tests)
                fact = evaluate(verifier_test_text=verifier_tests.replace(
                    marker, "removed-h19-verifier-test-marker", 1,
                ))
                self.assertFalse(fact.passed)
                self.assertIn("verifier-test-marker:%s" % marker, fact.evidence)

        for key in ("require_isolated_project_adapter", "require_staged_project_adapter"):
            with self.subTest(kind="policy", name=key):
                mutated = copy.deepcopy(policy)
                mutated[key] = False
                fact = evaluate(policy_value=mutated)
                self.assertFalse(fact.passed)
                self.assertIn("policy:%s" % key, fact.evidence)

        fact = evaluate(ci_text=ci.replace(
            "tests.test_semantic_evidence_verifier", "removed-h19-ci-test",
        ))
        self.assertFalse(fact.passed)
        self.assertIn("ci:semantic-evidence-verifier", fact.evidence)

        mutated_suites = copy.deepcopy(suites)
        maturity_suite = next(
            item for item in mutated_suites["suites"]
            if item["id"] == "five-engineering-maturity-contract"
        )
        maturity_suite["command"].remove("tests.test_semantic_evidence_verifier")
        fact = evaluate(suite_value=mutated_suites)
        self.assertFalse(fact.passed)
        self.assertIn("deterministic-suite:h19", fact.evidence)

    def test_semantic_evidence_verifier_is_wired_to_ci_and_deterministic_suite(self):
        ci = (ROOT / ".github/workflows/validate-skill.yml").read_text(encoding="utf-8")
        suites = json.loads(
            (ROOT / "evals/deterministic-suites.json").read_text(encoding="utf-8")
        )
        self.assertIn("tests.test_semantic_evidence_verifier", ci)
        maturity_suite = next(
            item for item in suites["suites"]
            if item["id"] == "five-engineering-maturity-contract"
        )
        self.assertIn("tests.test_semantic_evidence_verifier", maturity_suite["command"])

    def test_private_report_write_is_atomic_mode_0600_and_rejects_symlink(self):
        result = {"bounded": True}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "report.json"
            maturity.write_private_report(target, result)
            self.assertEqual(result, json.loads(target.read_text(encoding="utf-8")))
            self.assertEqual(0o600, stat.S_IMODE(target.stat().st_mode))
            maturity.write_private_report(target, {"bounded": False})
            self.assertEqual(
                {"bounded": False}, json.loads(target.read_text(encoding="utf-8")),
            )
            link = root / "link.json"
            os.symlink(target, link)
            with self.assertRaisesRegex(maturity.MaturityError, "regular file"):
                maturity.write_private_report(link, result)


if __name__ == "__main__":
    unittest.main()
