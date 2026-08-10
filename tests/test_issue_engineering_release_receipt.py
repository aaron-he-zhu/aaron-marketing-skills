"""Engineering-only current-v19 release-receipt issuer tests."""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "engineering_release_receipt_issuer",
    ROOT / "scripts" / "issue-engineering-release-receipt.py",
)
assert SPEC and SPEC.loader
issuer = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = issuer
SPEC.loader.exec_module(issuer)

NOW = dt.datetime(2026, 7, 24, 12, 0, tzinfo=dt.timezone.utc)
RUN_ID = "123e4567-e89b-42d3-a456-426614174099"


def source_bindings() -> dict:
    return {
        name: {"ref": reference, "sha256": ("%x" % (index + 1)) * 64}
        for index, (name, reference) in enumerate(issuer.TOOL_REFS.items())
    }


def repository() -> dict:
    return {
        "commit": "a" * 40,
        "branch": "codex/v19-runtime-distribution",
        "worktree_clean": True,
        "source_tree_sha256": "f" * 64,
    }


def semantic_evidence() -> dict:
    return {
        "schema_version": "1.0",
        "valid": True,
        "run_id": RUN_ID,
        "profile": "smoke",
        "case_count": 24,
        "case_provenance": {"simulated": 24},
        "execution_mode": "real",
        "model_provider": "openai",
        "model_id": "candidate-model",
        "judge_model_id": "distinct-judge-model",
        "distinct_judge_model": True,
        "total_judge_attempts": 24,
        "retried_cases": 0,
        "judge_protocol_retries": 0,
        "host_name": "codex",
        "host_version": "1.0",
        "adapter_name": "codex-project-adapter",
        "adapter_implementation_sha256": "1" * 64,
        "runner_sha256": "2" * 64,
        "selection_sha256": "3" * 64,
        "protocol_schema_sha256": "4" * 64,
        "request_stream_sha256": "5" * 64,
        "result_stream_sha256": "6" * 64,
        "head_record_hash": "7" * 64,
        "completion_sha256": "8" * 64,
        "oldest_result_at": "2026-07-24T11:58:00Z",
        "newest_evidence_at": "2026-07-24T11:59:00Z",
        "age_seconds": 120.0,
    }


def maturity_report() -> dict:
    tools = source_bindings()
    semantic = semantic_evidence()
    dimensions = {}
    for name, prefix in (
        ("prompt", "P"),
        ("context", "C"),
        ("harness", "H"),
        ("loop", "L"),
        ("graph", "G"),
    ):
        controls = []
        for index in range(1, 21):
            control_id = "%s%02d" % (prefix, index)
            controls.append(
                {
                    "id": control_id,
                    "control": "verified control %s" % control_id,
                    "evidence_class": "R" if control_id in {"P19", "P20", "H20"} else "S",
                    "hard_gate": control_id in {"P19", "H20"},
                    "passed": True,
                    "points": 5,
                    "evidence": "verified",
                }
            )
        dimensions[name] = {
            "raw_score": 100,
            "final_score": 100,
            "score_10": 10.0,
            "target_met": True,
            "failed_hard_gates": [],
            "failed_controls": [],
            "controls": controls,
        }
    return {
        "$schema": issuer.REPORT_SCHEMA_REF,
        "schema_version": "1.0",
        "evaluated_at": "2026-07-24T12:00:00Z",
        "repository": {
            "git_available": True,
            "commit": "a" * 40,
            "branch": "codex/v19-runtime-distribution",
            "worktree_clean": True,
        },
        "checker": copy.deepcopy(tools["maturity_checker"]),
        "rubric_sha256": tools["maturity_rubric"]["sha256"],
        "target_score": 95,
        "achieved": True,
        "semantic_evidence_run_id": RUN_ID,
        "semantic_evidence": semantic,
        "dimensions": dimensions,
    }


def private_json_bytes(value: dict) -> bytes:
    return (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


class EngineeringReleaseReceiptIssuerTests(unittest.TestCase):
    def validate(self, report: dict | None = None) -> dict:
        return issuer.validate_maturity_report(
            report or maturity_report(),
            repository=repository(),
            tools=source_bindings(),
            run_id=RUN_ID,
            issued_at=NOW,
        )

    def test_schema_is_closed_and_encodes_non_outcome_claims(self):
        schema = json.loads(
            (ROOT / "references/engineering-release-receipt.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(
            "engineering-validation-v19",
            schema["properties"]["gate"]["const"],
        )
        self.assertEqual(
            ["19.0.0", "19.1.0", "19.2.0"],
            schema["properties"]["release_version"]["enum"],
        )
        claims = schema["properties"]["claims"]
        self.assertFalse(claims["additionalProperties"])
        self.assertEqual(
            {
                "validation_scope",
                "evidence_provenance",
                "real_project_outcomes_validated",
                "default_profile",
                "governed_outcome_claims_allowed",
                "governed_default_promotion_allowed",
            },
            set(claims["required"]),
        )
        self.assertFalse(
            claims["properties"]["real_project_outcomes_validated"]["const"]
        )
        self.assertEqual("lite", claims["properties"]["default_profile"]["const"])
        self.assertFalse(
            claims["properties"]["governed_outcome_claims_allowed"]["const"]
        )
        self.assertFalse(
            claims["properties"]["governed_default_promotion_allowed"]["const"]
        )
        semantic = schema["$defs"]["semantic_evidence"]
        self.assertEqual(
            {"simulated"},
            set(semantic["properties"]["case_provenance"]["required"]),
        )
        self.assertEqual(
            24,
            semantic["properties"]["case_provenance"]["properties"]["simulated"][
                "const"
            ],
        )
        self.assertIn("release_verifier", schema["properties"]["tools"]["required"])

    def test_valid_dynamic_report_builds_exact_engineering_only_receipt(self):
        report = maturity_report()
        semantic = self.validate(report)
        receipt = issuer.build_receipt(
            report,
            repository=repository(),
            tools=source_bindings(),
            release_candidate="19.2.0-rc.1",
            semantic=semantic,
            report_sha256=hashlib.sha256(private_json_bytes(report)).hexdigest(),
            issued_at=NOW,
        )
        self.assertEqual(set(json.loads(
            (ROOT / "references/engineering-release-receipt.schema.json").read_text(
                encoding="utf-8"
            )
        )["required"]), set(receipt))
        self.assertEqual("19.2.0", receipt["release_version"])
        self.assertEqual({"simulated": 24}, receipt["semantic_evidence"]["case_provenance"])
        self.assertEqual("engineering-only", receipt["claims"]["validation_scope"])
        self.assertFalse(receipt["claims"]["real_project_outcomes_validated"])
        self.assertEqual("lite", receipt["claims"]["default_profile"])
        self.assertFalse(receipt["claims"]["governed_outcome_claims_allowed"])
        self.assertFalse(receipt["claims"]["governed_default_promotion_allowed"])
        self.assertEqual(
            {
                "P19": True,
                "P20": True,
                "H20": True,
            },
            receipt["maturity"]["required_hard_gates"],
        )
        self.assertEqual(
            hashlib.sha256(private_json_bytes(report)).hexdigest(),
            receipt["maturity"]["report_sha256"],
        )

    def test_report_validation_fails_closed_on_score_gate_or_semantic_drift(self):
        mutations = []
        low_score = maturity_report()
        low_score["dimensions"]["context"]["final_score"] = 95
        mutations.append(("100/100", low_score))

        failed_gate = maturity_report()
        failed_gate["dimensions"]["prompt"]["controls"][18]["passed"] = False
        mutations.append(("P19", failed_gate))

        project_claim = maturity_report()
        project_claim["semantic_evidence"]["case_provenance"] = {"real-project": 24}
        mutations.append(("simulated", project_claim))

        same_judge = maturity_report()
        same_judge["semantic_evidence"]["judge_model_id"] = same_judge[
            "semantic_evidence"
        ]["model_id"]
        mutations.append(("distinct-judge", same_judge))

        missing_chain = maturity_report()
        missing_chain["semantic_evidence"].pop("head_record_hash")
        mutations.append(("unknown or missing", missing_chain))

        stale = maturity_report()
        stale["semantic_evidence"]["age_seconds"] = 86401
        mutations.append(("24 hours", stale))

        postdated = maturity_report()
        postdated["evaluated_at"] = "2026-07-24T11:58:30Z"
        mutations.append(("postdates the maturity", postdated))

        checker_drift = maturity_report()
        checker_drift["checker"]["sha256"] = "9" * 64
        mutations.append(("current source bytes", checker_drift))

        for message, report in mutations:
            with self.subTest(message=message), self.assertRaisesRegex(
                issuer.EngineeringReceiptError, message
            ):
                self.validate(report)

    def test_private_writer_is_exclusive_outside_repo_and_mode_0600(self):
        report = maturity_report()
        receipt = issuer.build_receipt(
            report,
            repository=repository(),
            tools=source_bindings(),
            release_candidate="19.2.0-rc.1",
            semantic=self.validate(report),
            report_sha256=hashlib.sha256(private_json_bytes(report)).hexdigest(),
            issued_at=NOW,
        )
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "engineering-receipt.json"
            digest, identity = issuer.write_private_receipt(path, ROOT, receipt)
            raw = path.read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), digest)
            self.assertEqual(identity, (path.stat().st_dev, path.stat().st_ino))
            self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
            with self.assertRaisesRegex(
                issuer.EngineeringReceiptError, "refusing to overwrite"
            ):
                issuer.write_private_receipt(path, ROOT, receipt)

        inside = ROOT / ".engineering-release-receipt-test.json"
        with self.assertRaisesRegex(
            issuer.EngineeringReceiptError, "outside the source repository"
        ):
            issuer.write_private_receipt(inside, ROOT, receipt)
        self.assertFalse(inside.exists())

    def test_private_writer_removes_a_partial_file_after_write_failure(self):
        report = maturity_report()
        receipt = issuer.build_receipt(
            report,
            repository=repository(),
            tools=source_bindings(),
            release_candidate="19.2.0-rc.1",
            semantic=self.validate(report),
            report_sha256=hashlib.sha256(private_json_bytes(report)).hexdigest(),
            issued_at=NOW,
        )
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "partial-receipt.json"
            with mock.patch.object(
                issuer.os, "write", side_effect=OSError("forced write failure")
            ), self.assertRaisesRegex(OSError, "forced write failure"):
                issuer.write_private_receipt(output, ROOT, receipt)
            self.assertFalse(output.exists())

    def test_issue_runs_dynamic_audit_and_rechecks_source_after_write(self):
        report = maturity_report()
        calls = []

        def audit(*args, **kwargs):
            calls.append((args, kwargs))
            return copy.deepcopy(report)

        checker = types.SimpleNamespace(audit=audit)
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            issuer, "repository_snapshot", return_value=repository()
        ) as repo_snapshot, mock.patch.object(
            issuer, "source_snapshot", return_value=source_bindings()
        ) as tool_snapshot, mock.patch.object(
            issuer, "committed_release_version", return_value="19.2.0"
        ), mock.patch.object(
            issuer, "_load_maturity_checker", return_value=checker
        ):
            output = Path(temporary) / "engineering-receipt.json"
            report_output = Path(temporary) / "maturity-report.json"
            receipt, digest = issuer.issue_receipt(
                root=ROOT,
                run_id=RUN_ID,
                evidence_root=Path(temporary),
                release_candidate="19.2.0-rc.7",
                owner_authorization=issuer.AUTHORIZATION,
                output=output,
                maturity_report_output=report_output,
                timeout=321,
                now=NOW,
            )
            self.assertTrue(output.is_file())
            self.assertTrue(report_output.is_file())
            self.assertEqual(hashlib.sha256(output.read_bytes()).hexdigest(), digest)
            self.assertEqual(
                hashlib.sha256(report_output.read_bytes()).hexdigest(),
                receipt["maturity"]["report_sha256"],
            )
            self.assertEqual(0o600, stat.S_IMODE(report_output.stat().st_mode))
            self.assertEqual("19.2.0-rc.7", receipt["release_candidate"])
            self.assertEqual(3, repo_snapshot.call_count)
            self.assertEqual(3, tool_snapshot.call_count)
        self.assertEqual(1, len(calls))
        _args, kwargs = calls[0]
        self.assertTrue(kwargs["run_dynamic"])
        self.assertEqual(RUN_ID, kwargs["evidence_run_id"])
        self.assertEqual(321, kwargs["timeout"])

    def test_issue_rejects_missing_authorization_and_revokes_on_post_write_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "engineering-receipt.json"
            report_output = Path(temporary) / "maturity-report.json"
            with self.assertRaisesRegex(
                issuer.EngineeringReceiptError, "owner engineering-only"
            ):
                issuer.issue_receipt(
                    root=ROOT,
                    run_id=RUN_ID,
                    evidence_root=Path(temporary),
                    release_candidate="19.2.0-rc.1",
                    owner_authorization="",
                    output=output,
                    maturity_report_output=report_output,
                    now=NOW,
                )
            self.assertFalse(output.exists())
            self.assertFalse(report_output.exists())

        checker = types.SimpleNamespace(audit=lambda *args, **kwargs: maturity_report())
        clean = repository()
        drifted = {**clean, "commit": "b" * 40}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            issuer,
            "repository_snapshot",
            side_effect=[clean, clean, drifted],
        ), mock.patch.object(
            issuer, "source_snapshot", return_value=source_bindings()
        ), mock.patch.object(
            issuer, "committed_release_version", return_value="19.2.0"
        ), mock.patch.object(
            issuer, "_load_maturity_checker", return_value=checker
        ):
            output = Path(temporary) / "engineering-receipt.json"
            report_output = Path(temporary) / "maturity-report.json"
            with self.assertRaisesRegex(
                issuer.EngineeringReceiptError, "changed while the receipt was issued"
            ):
                issuer.issue_receipt(
                    root=ROOT,
                    run_id=RUN_ID,
                    evidence_root=Path(temporary),
                    release_candidate="19.2.0-rc.1",
                    owner_authorization=issuer.AUTHORIZATION,
                    output=output,
                    maturity_report_output=report_output,
                    now=NOW,
                )
            self.assertFalse(output.exists())
            self.assertFalse(report_output.exists())

    def test_receipt_creation_failure_revokes_only_the_new_report(self):
        checker = types.SimpleNamespace(audit=lambda *args, **kwargs: maturity_report())
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            issuer, "repository_snapshot", return_value=repository()
        ), mock.patch.object(
            issuer, "source_snapshot", return_value=source_bindings()
        ), mock.patch.object(
            issuer, "committed_release_version", return_value="19.2.0"
        ), mock.patch.object(
            issuer, "_load_maturity_checker", return_value=checker
        ):
            output = Path(temporary) / "existing-receipt.json"
            output.write_text("belongs to caller\n", encoding="utf-8")
            report_output = Path(temporary) / "maturity-report.json"
            with self.assertRaisesRegex(
                issuer.EngineeringReceiptError, "refusing to overwrite"
            ):
                issuer.issue_receipt(
                    root=ROOT,
                    run_id=RUN_ID,
                    evidence_root=Path(temporary),
                    release_candidate="19.2.0-rc.1",
                    owner_authorization=issuer.AUTHORIZATION,
                    output=output,
                    maturity_report_output=report_output,
                    now=NOW,
                )
            self.assertEqual(
                "belongs to caller\n", output.read_text(encoding="utf-8")
            )
            self.assertFalse(report_output.exists())

    def test_report_and_receipt_paths_must_be_distinct(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "one-artifact.json"
            with self.assertRaisesRegex(
                issuer.EngineeringReceiptError, "must be distinct"
            ):
                issuer.issue_receipt(
                    root=ROOT,
                    run_id=RUN_ID,
                    evidence_root=Path(temporary),
                    release_candidate="19.2.0-rc.1",
                    owner_authorization=issuer.AUTHORIZATION,
                    output=output,
                    maturity_report_output=output,
                    now=NOW,
                )


if __name__ == "__main__":
    unittest.main()
