import importlib.util
import io
import json
import os
import pathlib
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIT_SCHEMA = json.loads(
    (ROOT / "references" / "audit-artifact.schema.json").read_text(encoding="utf-8")
)
CURRENT_CATALOG_VERSION = AUDIT_SCHEMA["properties"]["catalog_version"]["const"]
SPEC = importlib.util.spec_from_file_location(
    "audit_validator", ROOT / "scripts" / "validate-audit-artifact.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def artifact(**overrides):
    values = {
        "framework": "ROAS",
        "profile": "direct-response",
        "catalog_version": CURRENT_CATALOG_VERSION,
        "status": "DONE",
        "verdict": "SHIP",
        "score_state": "SCORED",
        "context": (
            '{"currency":"USD","window":"2026-Q2","conversion_lag":"30d",'
            '"business_constraint":"profitable-growth","goal":"direct-response"}'
        ),
        "coverage": 100,
        "confidence": "high",
        "veto_count": 0,
        "cap": "false",
        "raw": "80",
        "final": "final_overall_score: 80",
    }
    values.update(overrides)
    return textwrap.dedent(
        """\
        ---
        class: auditor-output
        schema_version: "3.0"
        runbook_version: "3.0.0"
        catalog_version: "{catalog_version}"
        framework: {framework}
        profile: {profile}
        ---
        status: {status}
        verdict: {verdict}
        score_state: {score_state}
        objective: audit account
        target: account-1
        observed_at: 2026-07-10
        context: {context}
        key_findings: []
        evidence_summary: export reviewed
        evidence_coverage: {coverage}
        score_confidence: {confidence}
        open_loops: none
        recommended_next_skill: paid-measurement-loop
        veto_count: {veto_count}
        cap_applied: {cap}
        raw_overall_score: {raw}
        {final}
        """
    ).format(**values)


class AuditArtifactValidatorTests(unittest.TestCase):
    def validate(self, text, relative="memory/audits/ad/test.md"):
        with tempfile.NamedTemporaryFile("w", suffix=".md", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            return validator.validate(handle.name, relative)

    def test_valid_scored_artifact(self):
        record, errors = self.validate(artifact())
        self.assertEqual(errors, [])
        self.assertEqual(record["final_overall_score"], 80)
        self.assertEqual(record["catalog_version"], CURRENT_CATALOG_VERSION)
        self.assertEqual(record["context"]["currency"], "USD")

    def test_stdin_validation_uses_the_supplied_bytes(self):
        stdin = type("BinaryStdin", (), {"buffer": io.BytesIO(artifact().encode("utf-8"))})()
        with mock.patch.object(validator.sys, "stdin", stdin):
            record, errors = validator.validate("-", "memory/audits/ad/test.md")
        self.assertEqual([], errors)
        self.assertEqual("ROAS", record["framework"])

    def test_companion_schema_declares_current_catalog_and_state_machine(self):
        self.assertEqual(
            AUDIT_SCHEMA["properties"]["catalog_version"],
            {"const": CURRENT_CATALOG_VERSION},
        )
        branches = json.dumps(AUDIT_SCHEMA["allOf"], sort_keys=True)
        for required_fragment in (
            '"score_state": {"const": "SCORED"}',
            '"required": ["raw_overall_score", "final_overall_score"]',
            '"veto_count": {"const": 1}',
            '"final_overall_score": {"maximum": 59}',
            '"profile": {"const": "cross-framework-summary"}',
            '"status": {"const": "DONE"}',
            '"framework": {"const": "STAR"}',
            '"additionalProperties": false',
            '"market": {"minLength": 1, "type": "string"}',
        ):
            self.assertIn(required_fragment, branches)

    def test_low_coverage_cannot_emit_score(self):
        _, errors = self.validate(artifact(coverage=99))
        self.assertTrue(any("coverage" in error for error in errors))

    def test_single_veto_cap_math_is_exact(self):
        valid = artifact(status="DONE_WITH_CONCERNS", verdict="FIX", veto_count=1,
                         cap="true", raw="80", final="final_overall_score: 59")
        valid = valid.replace(
            "key_findings: []",
            "key_findings:\n  - title: missing disclosure\n    severity: veto\n"
            "    evidence: paid relationship confirmed without disclosure",
        )
        self.assertEqual(self.validate(valid)[1], [])
        invalid = valid.replace("final_overall_score: 59", "final_overall_score: 60")
        self.assertTrue(any("one veto" in error for error in self.validate(invalid)[1]))

    def test_completed_block_is_not_execution_blocked(self):
        valid = artifact(verdict="BLOCK", veto_count=2, cap="false", raw="80", final="")
        valid = valid.replace(
            "key_findings: []",
            "key_findings:\n  - title: attribution mismatch\n    severity: veto\n"
            "    evidence: platform conversions do not reconcile\n"
            "  - title: policy violation\n    severity: veto\n"
            "    evidence: restricted claim is unsubstantiated",
        )
        self.assertEqual(self.validate(valid)[1], [])
        invalid = valid.replace("status: DONE", "status: BLOCKED")
        self.assertTrue(any("execution" in error for error in self.validate(invalid)[1]))

    def test_path_framework_ownership(self):
        _, errors = self.validate(artifact(framework="SEND"))
        self.assertTrue(any("requires framework ROAS" in error for error in errors))

    def test_profile_must_belong_to_framework(self):
        _, errors = self.validate(artifact(profile="newsletter"))
        self.assertTrue(any("not declared for framework ROAS" in error for error in errors))

    def test_unknown_fields_and_free_text_fail_closed(self):
        unknown = artifact().replace("framework: ROAS", "framework: ROAS\nextra: value")
        self.assertTrue(any("unknown frontmatter" in error for error in self.validate(unknown)[1]))
        prose = artifact() + "this prose is outside the deterministic body subset\n"
        self.assertTrue(any("not a scalar key/value" in error for error in self.validate(prose)[1]))

    def test_artifact_size_and_encoding_are_bounded(self):
        with tempfile.NamedTemporaryFile("wb", suffix=".md") as handle:
            handle.write(b"x" * (validator.MAX_ARTIFACT_BYTES + 1))
            handle.flush()
            self.assertTrue(any("exceeds" in error
                                for error in validator.validate(handle.name)[1]))
        with tempfile.NamedTemporaryFile("wb", suffix=".md") as handle:
            handle.write(b"\xff\xfe")
            handle.flush()
            self.assertTrue(any("UTF-8" in error
                                for error in validator.validate(handle.name)[1]))

    def test_numeric_and_context_parser_limits_fail_without_traceback(self):
        _, integer_errors = self.validate(artifact(coverage="9" * 10_000))
        self.assertTrue(any("integer is too large" in error for error in integer_errors))

        nested = {"leaf": "value"}
        for _ in range(validator.MAX_CONTEXT_JSON_DEPTH + 2):
            nested = {"nested": nested}
        _, depth_errors = self.validate(artifact(context=json.dumps(nested)))
        self.assertTrue(any("depth/node limits" in error for error in depth_errors))

        _, finite_errors = self.validate(artifact(context='{"value":1e999}'))
        self.assertTrue(any("finite" in error for error in finite_errors))

        parser_errors = []
        with mock.patch.object(
                validator.json, "loads", side_effect=RecursionError("deep JSON")):
            self.assertIsNone(validator.as_json_object("context", "{}", parser_errors))
        self.assertTrue(any("strict JSON object" in error for error in parser_errors))

    def test_sink_traversal_rejects_unreadable_non_markdown_and_hardlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            hidden = root / "hidden"
            hidden.mkdir()
            hidden.chmod(0)
            try:
                errors = validator.validate_sink(root)
                self.assertTrue(any("not readable" in error for error in errors), errors)
            finally:
                hidden.chmod(0o700)

        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / "notes.txt").write_text("not an artifact\n", encoding="utf-8")
            errors = validator.validate_sink(root)
            self.assertTrue(any(".md artifact format" in error for error in errors), errors)

        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            outside = root.parent / (root.name + "-outside.md")
            outside.write_text(artifact(), encoding="utf-8")
            linked = root / "linked.md"
            try:
                os.link(outside, linked)
            except (OSError, NotImplementedError) as exc:
                self.skipTest("hard links unavailable: %s" % exc)
            try:
                errors = validator.validate_sink(root)
                self.assertTrue(any("hard-linked" in error for error in errors), errors)
            finally:
                outside.unlink(missing_ok=True)

    def test_sink_has_an_aggregate_byte_budget_below_hook_timeout_work(self):
        original = validator.MAX_SINK_TOTAL_BYTES
        try:
            validator.MAX_SINK_TOTAL_BYTES = 8
            with tempfile.TemporaryDirectory() as directory:
                root = pathlib.Path(directory)
                (root / "oversized.md").write_bytes(b"x" * 9)
                errors = validator.validate_sink(root)
                self.assertTrue(any("aggregate limit" in error for error in errors), errors)
        finally:
            validator.MAX_SINK_TOTAL_BYTES = original

    def test_preflight_allows_only_clean_full_content_write_to_reserved_sink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            valid = {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": "memory/audits/ad/report.md",
                    "content": artifact(),
                },
            }
            self.assertEqual(validator.preflight_hook_write(root, valid), [])
            invalid = json.loads(json.dumps(valid))
            invalid["tool_input"]["content"] = "# untyped notes\n"
            self.assertTrue(validator.preflight_hook_write(root, invalid))
            edit = json.loads(json.dumps(valid))
            edit["tool_name"] = "Edit"
            self.assertTrue(any(
                "only one exact-target full-content Write" in error
                for error in validator.preflight_hook_write(root, edit)
            ))
            wrong_suffix = json.loads(json.dumps(valid))
            wrong_suffix["tool_input"]["file_path"] = "memory/audits/ad/report.txt"
            self.assertTrue(any(
                "only .md" in error
                for error in validator.preflight_hook_write(root, wrong_suffix)
            ))
            ordinary = {
                "tool_name": "Write",
                "tool_input": {"file_path": "README.md", "content": "memory/audits docs"},
            }
            self.assertEqual(validator.preflight_hook_write(root, ordinary), [])

    def test_veto_count_requires_matching_findings(self):
        text = artifact(status="DONE_WITH_CONCERNS", verdict="FIX", veto_count=1,
                        cap="true", final="final_overall_score: 59")
        self.assertTrue(any("veto_count" in error for error in self.validate(text)[1]))

    def test_status_and_verdict_pairing_is_enforced(self):
        text = artifact(status="DONE", verdict="FIX")
        self.assertTrue(any("requires status DONE_WITH_CONCERNS" in error
                            for error in self.validate(text)[1]))

    def test_ship_requires_the_scorer_threshold(self):
        _, errors = self.validate(artifact(raw="74", final="final_overall_score: 74"))
        self.assertTrue(any("SHIP requires raw_overall_score >= 75" in error for error in errors))
        low_fix = artifact(
            status="DONE_WITH_CONCERNS", verdict="FIX", raw="74",
            final="final_overall_score: 74",
        )
        self.assertEqual(self.validate(low_fix)[1], [])
        high_fix = artifact(
            status="DONE_WITH_CONCERNS", verdict="FIX", raw="80",
            final="final_overall_score: 80",
        )
        self.assertEqual(self.validate(high_fix)[1], [])

    def test_every_not_scored_state_requires_not_scored_confidence(self):
        text = artifact(
            status="NEEDS_INPUT", verdict="UNDECIDED", score_state="NOT_SCORED",
            coverage=75, confidence="high", cap="false", raw="0", final="",
        ).replace("raw_overall_score: 0\n", "")
        _, errors = self.validate(text)
        self.assertTrue(any("NOT_SCORED requires score_confidence: not_scored" in error
                            for error in errors))

    def test_multi_veto_with_gaps_is_completed_unscored_block(self):
        text = artifact(
            status="DONE", verdict="BLOCK", score_state="NOT_SCORED", coverage=90,
            confidence="not_scored", veto_count=2, cap="false", raw="0", final="",
        ).replace("raw_overall_score: 0\n", "")
        text = text.replace(
            "key_findings: []",
            "key_findings:\n  - title: tracking is broken\n    severity: veto\n"
            "    evidence: checkout tag did not fire\n"
            "  - title: conversions are duplicated\n    severity: veto\n"
            "    evidence: the same order IDs appear twice",
        )
        self.assertEqual(self.validate(text)[1], [])
        undecided = text.replace("status: DONE", "status: NEEDS_INPUT").replace(
            "verdict: BLOCK", "verdict: UNDECIDED"
        )
        self.assertTrue(any("two or more vetoes" in error
                            for error in self.validate(undecided)[1]))

    def test_catalog_version_and_typed_material_context_are_required(self):
        missing_version = artifact().replace(
            'catalog_version: "%s"\n' % CURRENT_CATALOG_VERSION, ""
        )
        self.assertTrue(any("catalog_version" in error
                            for error in self.validate(missing_version)[1]))
        invalid_version = artifact(catalog_version="v17")
        self.assertTrue(any("semantic version" in error
                            for error in self.validate(invalid_version)[1]))
        old_errors = self.validate(artifact(catalog_version="16.0.0"))[1]
        self.assertTrue(any("not supported by the current validator" in error
                            for error in old_errors))
        forged = artifact(
            catalog_version="999.0.0", profile="fabricated-profile", context='{"x":"y"}',
        )
        forged_errors = self.validate(forged)[1]
        self.assertTrue(any("not supported by the current validator" in error
                            for error in forged_errors))
        self.assertTrue(any("not declared for framework ROAS" in error
                            for error in forged_errors))

        missing_context = artifact().replace(
            "context: {\"currency\":\"USD\",\"window\":\"2026-Q2\","
            "\"conversion_lag\":\"30d\",\"business_constraint\":"
            "\"profitable-growth\",\"goal\":\"direct-response\"}\n",
            "",
        )
        self.assertTrue(any("context" in error for error in self.validate(missing_context)[1]))

        duplicate_key = artifact(context=(
            '{"currency":"USD","currency":"EUR","window":"2026-Q2",'
            '"conversion_lag":"30d","business_constraint":"growth",'
            '"goal":"direct-response"}'
        ))
        self.assertTrue(any("duplicate JSON key" in error
                            for error in self.validate(duplicate_key)[1]))

        mismatched = artifact(context=(
            '{"currency":"USD","window":"2026-Q2","conversion_lag":"30d",'
            '"business_constraint":"growth","goal":"prospecting"}'
        ))
        self.assertTrue(any("context.goal" in error for error in self.validate(mismatched)[1]))

    def test_star_artifact_context_matches_the_scorer_closed_type(self):
        valid = artifact(
            framework="STAR", profile="awareness",
            context=(
                '{"goal":"awareness","assessment_time":"actual",'
                '"platform":"tiktok","market":"US"}'
            ),
        )
        self.assertEqual(
            self.validate(valid, "memory/audits/influencer/result.md")[1], []
        )

        malformed = artifact(
            framework="STAR", profile="awareness",
            context=(
                '{"goal":"awareness","assessment_time":"someday",'
                '"platform":"tiktok","market":"US"}'
            ),
        )
        errors = self.validate(malformed, "memory/audits/influencer/result.md")[1]
        self.assertTrue(any("assessment_time must be one of" in error for error in errors))

    def test_direct_audit_path_is_reserved_for_unscored_multi_summary(self):
        _, individual_errors = self.validate(artifact(), "memory/audits/result.md")
        self.assertTrue(any("only MULTI" in error for error in individual_errors))

        multi = artifact(
            framework="MULTI", profile="cross-framework-summary", status="DONE",
            verdict="UNDECIDED", score_state="NOT_SCORED", coverage=0,
            confidence="not_scored", veto_count=0, cap="false", raw="0", final="",
            context='{"summary_period":"2026-07"}',
        )
        multi = multi.replace("raw_overall_score: 0\n", "")
        self.assertEqual(self.validate(multi, "memory/audits/2026-07.md")[1], [])
        incomplete = multi.replace("status: DONE", "status: NEEDS_INPUT")
        self.assertTrue(any("MULTI summaries require status DONE" in error
                            for error in self.validate(
                                incomplete, "memory/audits/2026-07.md"
                            )[1]))


if __name__ == "__main__":
    unittest.main()
