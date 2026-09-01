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
        self.assertEqual(len(authored), 606)
        self.assertEqual(len(routing), 88)
        self.assertEqual(len(self.cases), 694)
        self.assertEqual(len({case["id"] for case in self.cases}), 694)

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

    def test_competitor_gap_runtime_contract_names_both_gates_and_inputs(self):
        target = next(
            case for case in self.cases if case["id"] == "auto-competitor-gap-001"
        )
        self.assertEqual(target["scenario"], "competitor_gap")
        command = (ROOT / "commands/seo-geo.md").read_text(encoding="utf-8")
        for token in (
            "`competitor_gap`",
            "`data_insufficient`",
            "`geo_visibility_claim`",
            "competitors, market, and domain",
            "AI citation visibility is not an optional metric",
        ):
            self.assertIn(token, command)

    def test_influencer_gate_matches_typed_status_and_write_authority(self):
        target = next(
            case
            for case in self.cases
            if case["id"] == "influencer-content-review-gate-001"
        )
        expected = " ".join(target["expected_behavior"])
        failures = " ".join(target["failure_modes"])
        for token in (
            "NEEDS_INPUT/UNDECIDED/NOT_SCORED",
            "qualified item state unknown",
            "no raw or final score",
            "explicit exact-write permission",
        ):
            self.assertIn(token, expected)
        self.assertNotIn("DONE_WITH_CONCERNS/FIX", expected)
        self.assertNotIn("DONE/BLOCK", expected)
        self.assertNotIn("Treats a veto as a revise", failures)
        self.assertIn("Converts Unknown into a veto", failures)

    def test_launch_gate_binds_each_veto_to_its_real_evidence_class(self):
        target = next(
            case
            for case in self.cases
            if case["id"] == "launch-readiness-gate-001"
        )
        expected = " ".join(target["expected_behavior"])
        self.assertNotIn("R1/A1/M1/P1 controls against accepted projections", expected)
        for token in (
            "RAMP-R1",
            "accepted launch projection plus direct access/eligibility",
            "RAMP-A1",
            "accepted claims/canon projections plus rendered assets",
            "RAMP-M1",
            "dated platform-rule/embargo/launch-plan evidence",
            "RAMP-P1",
            "verified events/UTMs plus own-data destination checks",
            "NEEDS_INPUT/UNDECIDED/NOT_SCORED",
        ):
            self.assertIn(token, expected)
        command = (ROOT / "commands/launch.md").read_text(encoding="utf-8")
        self.assertIn("For `launch_go_no_go`", command)
        self.assertIn("A proposal, plan, or manifest alone proves none", command)

    def test_max_depth_case_names_the_known_deferred_successor(self):
        target = next(
            case
            for case in self.cases
            if case["id"] == "routing-chain-max-depth-001"
        )
        self.assertIn(
            "content-quality-auditor is the one unambiguous input-ready successor",
            target["input_summary"],
        )
        expected = " ".join(target["expected_behavior"])
        failures = " ".join(target["failure_modes"])
        self.assertIn("recommended_next_skill to content-quality-auditor", expected)
        self.assertIn("exhausted budget and visited chain in open_loops", expected)
        self.assertIn("recommended_next_skill to none", failures)

    def test_social_and_email_missingness_use_typed_item_and_run_states(self):
        social = next(
            case for case in self.cases if case["id"] == "social-prepublish-gate-001"
        )
        social_expected = " ".join(social["expected_behavior"])
        self.assertNotIn("Return a verdict only", social_expected)
        self.assertIn("ECHO asset profile, not the program-maturity profile", social_expected)
        self.assertIn("unknown rather than fail", social_expected)
        self.assertIn("NEEDS_INPUT/UNDECIDED/NOT_SCORED", social_expected)
        self.assertIn("complete typed audit result", social_expected)
        self.assertIn("separate explicit approval", social_expected)

        email = next(
            case for case in self.cases if case["id"] == "email-presend-audit-gate-001"
        )
        email_expected = " ".join(email["expected_behavior"])
        self.assertNotIn("set S sub-items or S2 to NEEDS_INPUT", email_expected)
        self.assertIn("qualified SEND item unknown", email_expected)
        self.assertIn("NEEDS_INPUT/UNDECIDED/NOT_SCORED", email_expected)

    def test_multi_veto_case_keeps_business_and_execution_states_orthogonal(self):
        target = next(
            case for case in self.cases if case["id"] == "multi-veto-blocked-001"
        )
        expected = " ".join(target["expected_behavior"])
        failures = " ".join(target["failure_modes"])
        self.assertIn("execution status DONE", expected)
        self.assertIn("business verdict BLOCK", expected)
        self.assertIn("score_state NOT_SCORED", expected)
        self.assertIn("no final score", expected)
        self.assertIn("business verdict BLOCK with execution status BLOCKED", failures)

    def test_authored_missing_evidence_cases_do_not_infer_vetoes(self):
        roi = next(
            case
            for case in self.cases
            if case["id"] == "framework-sqs-pending-veto-roi-calculator-001"
        )
        roi_expected = " ".join(roi["expected_behavior"])
        self.assertIn("candidate STAR-T1 evidence", roi_expected)
        self.assertIn("qualified items unknown", roi_expected)
        self.assertIn("NEEDS_INPUT/UNDECIDED/NOT_SCORED", roi_expected)
        self.assertIn("rather than independently applying a cap or BLOCK", roi_expected)

        subject = next(
            case for case in self.cases if case["id"] == "subject-line-lab-sim-004"
        )
        subject_expected = " ".join(subject["expected_behavior"])
        self.assertIn("SEND-D1 as unknown", subject_expected)
        self.assertIn("return NEEDS_INPUT for the run", subject_expected)
        self.assertIn("never infer a veto", subject_expected)

    def test_non_auditor_blocking_case_does_not_render_business_verdict(self):
        target = next(
            case
            for case in self.cases
            if case["id"] == "claim-policy-multiveto-blocked-004"
        )
        expected = " ".join(target["expected_behavior"])
        failures = " ".join(target["failure_modes"])
        self.assertIn("dependency/publish readiness blocked", expected)
        self.assertIn("do not render the ROAS business verdict", expected)
        self.assertIn("execution status remains DONE", expected)
        self.assertIn("business verdict is BLOCK", expected)
        self.assertIn("conflates business BLOCK with execution BLOCKED", failures)

    def test_persistent_outputs_require_operation_specific_authority(self):
        ids = (
            "core-trend-report-go-skip-trend-spotter-001",
            "core-tiered-shortlist-influencer-discovery-001",
            "core-competitor-roster-competitor-tracker-001",
            "core-blueprint-campaign-planner-001",
            "core-full-brief-all-sections-brief-generator-001",
            "core-outreach-pitch-negotiation-pipeline-outreach-manager-001",
            "core-message-match-conversion-plan-landing-optimizer-001",
            "core-scorecard-rankings-attribution-performance-analyzer-001",
            "core-client-report-report-generator-001",
        )
        by_id = {case["id"]: case for case in self.cases}
        for case_id in ids:
            with self.subTest(case=case_id):
                expected = " ".join(by_id[case_id]["expected_behavior"])
                failures = " ".join(by_id[case_id]["failure_modes"])
                self.assertIn("inline", expected)
                self.assertIn("authorization", expected)
                self.assertRegex(failures, r"(?i)(writes|write).*(without|beyond)")

        wrong_sink = next(
            case
            for case in self.cases
            if case["id"] == "content-quality-auditor-v17-005"
        )
        wrong_expected = " ".join(wrong_sink["expected_behavior"])
        self.assertIn("wrong-sink authorization does not transfer", wrong_expected)
        self.assertIn("write nothing yet", wrong_expected)

    def test_all_high_confidence_proposal_cases_require_exact_current_authority(self):
        authority_failure = (
            "Treats a capability, path, hook, or validation result as authority "
            "for the proposal append."
        )
        targets = [
            case for case in self.cases
            if authority_failure in case["failure_modes"]
        ]
        self.assertEqual(59, len(targets))
        for case in targets:
            with self.subTest(case=case["id"]):
                expected = " ".join(case["expected_behavior"])
                self.assertIn("separate explicit authorization", expected)
                self.assertIn("inline", expected)
                self.assertIn("NEEDS_INPUT", expected)

    def test_non_gate_and_incomplete_coverage_cases_keep_typed_ownership(self):
        by_id = {case["id"]: case for case in self.cases}

        fit = " ".join(by_id[
            "core-weighted-ranked-verdict-fit-scorer-001"
        ]["expected_behavior"])
        self.assertIn("supplied but undated fields", fit)
        self.assertIn("all applicable STAR-S1 through STAR-S10 items Unknown", fit)
        self.assertIn("do not emit a Suitability total or SQS", fit)
        self.assertIn("NEEDS_INPUT/NOT_SCORED", fit)
        self.assertIn("rather than inventing them", fit)
        self.assertIn("no save or promotion", fit)

        fit_veto = " ".join(by_id[
            "framework-suitability-veto-followerfraud-fit-scorer-001"
        ]["expected_behavior"])
        self.assertIn("other unsupported applicable item as Unknown", fit_veto)
        self.assertIn("no Suitability total, decisive business verdict, or cap", fit_veto)
        self.assertIn("potential STAR-S2 gate finding", fit_veto)
        self.assertIn("creator-content-auditor", fit_veto)

        paid = " ".join(by_id[
            "paid-readback-multi-veto-block-001"
        ]["expected_behavior"])
        self.assertIn("Mark the readback Unproven", paid)
        self.assertIn("potential ROAS-R1 and ROAS-R2 evidence", paid)
        self.assertIn("does not render the RQS business verdict", paid)
        self.assertNotIn("verdict BLOCK", paid)

        for case_id in (
            "deliverability-qa-sim-003",
            "deliverability-qa-sim-004",
            "deliverability-qa-sim-005",
            "email-spam-placement-001",
        ):
            with self.subTest(case=case_id):
                expected = " ".join(by_id[case_id]["expected_behavior"])
                self.assertRegex(expected, r"(?i)unknown")
                self.assertIn("NEEDS_INPUT/UNDECIDED/NOT_SCORED", expected)
                self.assertRegex(expected, r"(?i)(?:no|without a) (?:SEND-)?S score")

    def test_remaining_high_risk_routes_have_one_typed_stop_and_write_boundary(self):
        by_id = {case["id"]: case for case in self.cases}
        discovery = " ".join(by_id[
            "influencer-creator-discovery-001"
        ]["expected_behavior"])
        self.assertIn("stop with NEEDS_INPUT", discovery)
        self.assertIn("Give a resume plan, not a claimed execution", discovery)
        self.assertIn("leave all downstream scoring/gate work pending", discovery)

        whitelisting = " ".join(by_id[
            "cross-creator-whitelisting-001"
        ]["expected_behavior"])
        self.assertIn("content-amplifier", whitelisting)
        self.assertIn("/aaron-marketing:ad --phase activate", whitelisting)
        command = (ROOT / "commands/influencer.md").read_text(encoding="utf-8")
        self.assertIn("Paid creator whitelisting order", command)
        self.assertIn("creator-content-auditor", command)
        self.assertIn("contract-helper", command)
        self.assertIn("content-amplifier` in its paid-planning mode", command)
        self.assertNotIn("--mode", command)
        self.assertIn("ad-account-auditor", command)
        self.assertIn("explicit spend approval", command)

        launch_auditor = (
            ROOT / "launch/mobilize/launch-readiness-auditor/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("stable catalog ID verbatim", launch_auditor)
        self.assertIn("never substitute an evidence-subcheck label", launch_auditor)
        self.assertIn("RAMP-R1d", launch_auditor)

        claims_registry = (
            ROOT / "protocol/offer-claims-registry/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("read-only empty-projection check", claims_registry)
        self.assertIn("one exact verbatim claim or offer statement", claims_registry)
        self.assertIn("smallest real input", claims_registry)

        consent_case = by_id["consent-registry-v17-002"]
        self.assertIn("actor system:esp-webhook-ingestor", consent_case["input_summary"])
        self.assertIn(
            "authorization_ref consent-policy:unsubscribe-ingestion-v1",
            consent_case["input_summary"],
        )
        consent_registry = (
            ROOT / "protocol/consent-registry/SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("immediate-suppress-handoff", consent_registry)
        self.assertIn("do not route to another skill or prepare a proposal", consent_registry)
        self.assertIn("append consent", consent_registry)
        runtime_contract = (
            ROOT / "references/runtime-invocation.md"
        ).read_text(encoding="utf-8")
        self.assertIn("exception to **proposal degradation**", runtime_contract)
        registry_protocol = (
            ROOT / "references/registry-event-protocol.md"
        ).read_text(encoding="utf-8")
        self.assertIn("A deny-only `suppress` never degrades into a proposal", registry_protocol)
        self.assertNotIn("prepare a proposal only", registry_protocol)

        geo = " ".join(by_id[
            "routing-geo-content-optimizer-sim-003"
        ]["expected_behavior"])
        self.assertIn("execution status NEEDS_INPUT", geo)
        self.assertIn("dependency_status blocked", geo)
        self.assertIn("do not conflate dependency blocking with execution BLOCKED", geo)

        for case_id in (
            "launch-momentum-001", "social-listening-001", "narrative-drift-001",
        ):
            with self.subTest(case=case_id):
                expected = " ".join(by_id[case_id]["expected_behavior"])
                failures = " ".join(by_id[case_id]["failure_modes"])
                self.assertIn("inline", expected)
                self.assertIn("separate explicit authorization", expected)
                self.assertRegex(failures, r"(?i)without exact authorization")

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
