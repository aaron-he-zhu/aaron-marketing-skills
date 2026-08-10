"""Private release-receipt validation tests."""
from __future__ import annotations

import copy
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OUTCOME_TEST_SPEC = importlib.util.spec_from_file_location(
    "profile_outcome_fixtures", ROOT / "tests" / "test_profile_outcomes.py"
)
assert OUTCOME_TEST_SPEC and OUTCOME_TEST_SPEC.loader
test_profile_outcomes = importlib.util.module_from_spec(OUTCOME_TEST_SPEC)
OUTCOME_TEST_SPEC.loader.exec_module(test_profile_outcomes)

SPEC = importlib.util.spec_from_file_location(
    "release_receipt", ROOT / "scripts" / "verify-release-receipt.py"
)
assert SPEC and SPEC.loader
release_receipt = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release_receipt)


MOCK_SEMANTIC_VERIFIER = """#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[sys.argv.index("--evidence-root") + 1])
sys.stdout.buffer.write((root / "mock-revalidated-summary.json").read_bytes())
"""


def engineering_fixture(
    base: Path,
    *,
    age_hours: int = 0,
    release_version: str = "19.0.0",
) -> tuple[Path, str, dict, dict[str, Path], Path, Path]:
    repository = base / "engineering-repository"
    repository.mkdir()
    (repository / ".gitignore").write_text(
        "memory/runs/\n",
        encoding="utf-8",
    )
    paths = {}
    for index, (name, reference) in enumerate(
        sorted(release_receipt.ENGINEERING_TOOL_REFS.items())
    ):
        path = repository / reference
        path.parent.mkdir(parents=True, exist_ok=True)
        if name == "release_verifier":
            path.write_bytes(
                (ROOT / "scripts" / "verify-release-receipt.py").read_bytes()
            )
        elif name == "semantic_verifier":
            path.write_text(MOCK_SEMANTIC_VERIFIER, encoding="utf-8")
            path.chmod(0o755)
        elif name == "maturity_rubric":
            path.write_bytes(
                (ROOT / "references" / "engineering-maturity-rubric.json").read_bytes()
            )
        elif name == "semantic_policy":
            path.write_bytes(
                (ROOT / "evals" / "semantic-evidence-policy.json").read_bytes()
            )
        else:
            path.write_text("# %s fixture %d\n" % (name, index), encoding="utf-8")
        paths[name] = path
    subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
    subprocess.run(
        ["git", "config", "user.name", "Receipt Test"],
        cwd=repository,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "receipt-test" + chr(64) + "example.invalid"],
        cwd=repository,
        check=True,
    )
    subprocess.run(["git", "add", "-A"], cwd=repository, check=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "engineering fixture"],
        cwd=repository,
        check=True,
    )
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    tree = subprocess.run(
        ["git", "ls-tree", "-r", "--full-tree", commit],
        cwd=repository,
        check=True,
        capture_output=True,
    ).stdout
    now = (
        dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=age_hours)
    ).replace(microsecond=0)
    stamp = now.isoformat().replace("+00:00", "Z")
    semantic_summary = {
        "schema_version": "1.0",
        "valid": True,
        "run_id": "12345678-1234-1234-1234-123456789abc",
        "profile": "smoke",
        "case_count": 24,
        "case_provenance": {"simulated": 24},
        "execution_mode": "real",
        "model_provider": "fixture-provider",
        "model_id": "fixture-model",
        "judge_model_id": "fixture-judge",
        "distinct_judge_model": True,
        "total_judge_attempts": 24,
        "retried_cases": 0,
        "judge_protocol_retries": 0,
        "host_name": "fixture-host",
        "host_version": "1",
        "adapter_name": "fixture-adapter",
        "adapter_implementation_sha256": "2" * 64,
        "runner_sha256": "3" * 64,
        "selection_sha256": "4" * 64,
        "protocol_schema_sha256": "5" * 64,
        "request_stream_sha256": "6" * 64,
        "result_stream_sha256": "7" * 64,
        "head_record_hash": "8" * 64,
        "completion_sha256": "9" * 64,
        "oldest_result_at": stamp,
        "newest_evidence_at": stamp,
        "age_seconds": 0,
    }
    receipt = {
        "$schema": "references/engineering-release-receipt.schema.json",
        "schema_version": "1.0",
        "gate": "engineering-validation-v19",
        "passed": True,
        "release_version": release_version,
        "release_candidate": release_version + "-rc.1",
        "source_commit": commit,
        "issued_at": stamp,
        "repository": {
            "branch": "test",
            "worktree_clean": True,
            "source_tree_sha256": hashlib.sha256(tree).hexdigest(),
        },
        "tools": {
            name: {
                "ref": release_receipt.ENGINEERING_TOOL_REFS[name],
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for name, path in paths.items()
        },
        "maturity": {
            "evaluated_at": stamp,
            "report_sha256": "1" * 64,
            "target_score": 95,
            "achieved": True,
            "dimension_scores": {
                name: 100 for name in release_receipt.DIMENSION_KEYS
            },
            "required_hard_gates": {
                name: True
                for name in release_receipt.REQUIRED_ENGINEERING_GATE_KEYS
            },
        },
        "semantic_evidence": semantic_summary,
        "claims": {
            "validation_scope": "engineering-only",
            "evidence_provenance": "simulated-semantic-cases",
            "real_project_outcomes_validated": False,
            "default_profile": "lite",
            "governed_outcome_claims_allowed": False,
            "governed_default_promotion_allowed": False,
        },
        "attestation": {
            "method": "explicit-owner-engineering-only-authorization",
            "statement": "release-v19-without-real-project-outcomes",
            "accepted_at": stamp,
        },
    }
    rubric = json.loads(paths["maturity_rubric"].read_text(encoding="utf-8"))
    dimensions = {}
    for name, controls in rubric["dimensions"].items():
        dimensions[name] = {
            "raw_score": 100,
            "final_score": 100,
            "score_10": 10.0,
            "target_met": True,
            "failed_hard_gates": [],
            "failed_controls": [],
            "controls": [
                {
                    **control,
                    "passed": True,
                    "points": 5,
                    "evidence": "mocked dynamic-audit boundary for verifier unit test",
                }
                for control in controls
            ],
        }
    report = {
        "$schema": "references/engineering-maturity-report.schema.json",
        "schema_version": "1.0",
        "evaluated_at": stamp,
        "repository": {
            "git_available": True,
            "commit": commit,
            "branch": "test",
            "worktree_clean": True,
        },
        "checker": receipt["tools"]["maturity_checker"],
        "rubric_sha256": receipt["tools"]["maturity_rubric"]["sha256"],
        "target_score": 95,
        "achieved": True,
        "semantic_evidence_run_id": semantic_summary["run_id"],
        "semantic_evidence": semantic_summary,
        "dimensions": dimensions,
    }
    report_path = base / "private-maturity-report.json"
    report_raw = (
        json.dumps(
            report,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    report_path.write_bytes(report_raw)
    report_path.chmod(0o600)
    receipt["maturity"]["report_sha256"] = hashlib.sha256(report_raw).hexdigest()
    evidence_root = base / "mock-raw-evidence-boundary"
    evidence_root.mkdir(mode=0o700)
    (evidence_root / "mock-revalidated-summary.json").write_text(
        json.dumps(semantic_summary, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return repository, commit, receipt, paths, report_path, evidence_root


def mocked_semantic_revalidator(**arguments):
    return json.loads(
        (
            arguments["evidence_root"] / "mock-revalidated-summary.json"
        ).read_text(encoding="utf-8")
    )


class ReleaseReceiptTests(unittest.TestCase):
    def receipt(self, stage: str = "governed-promotion") -> dict:
        evidence = (
            test_profile_outcomes.valid_pilot_evidence()
            if stage == "release-pilot"
            else test_profile_outcomes.valid_evidence()
        )
        summary = test_profile_outcomes.profile_outcomes.evaluate(
            evidence, stage=stage
        )
        return test_profile_outcomes.profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=json.dumps(evidence, sort_keys=True).encode("utf-8"),
            evidence_manifest_sha256=test_profile_outcomes.digest(
                "private-manifest"
            ),
            stage=stage,
        )

    def validate(self, receipt: dict) -> dict:
        return release_receipt.validate_receipt(
            receipt,
            expected_commit="a" * 40,
            expected_version="19.0.0",
            verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
        )

    def test_exact_passing_receipt_is_accepted(self):
        identity = self.validate(self.receipt())
        self.assertEqual("19.0.0-rc.1", identity["release_candidate"])
        self.assertEqual("a" * 40, identity["source_commit"])
        self.assertEqual("profile-outcomes-v19", identity["gate"])

    def test_exact_release_pilot_receipt_is_accepted(self):
        identity = self.validate(self.receipt(stage="release-pilot"))
        self.assertEqual("19.0.0-rc.1", identity["release_candidate"])
        self.assertEqual("a" * 40, identity["source_commit"])
        self.assertEqual("profile-pilots-v19", identity["gate"])

    def test_exact_engineering_receipt_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(base)
            identity = release_receipt.validate_receipt(
                receipt,
                expected_commit=commit,
                expected_version="19.0.0",
                verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
                repository_root=repository,
                engineering_paths=paths,
                maturity_report_path=report_path,
                evidence_root=evidence_root,
                semantic_revalidator=mocked_semantic_revalidator,
            )
            receipt_path = base / "private-engineering-receipt.json"
            receipt_path.write_text(
                json.dumps(receipt, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            receipt_path.chmod(0o600)
            command = subprocess.run(
                [
                    sys.executable,
                    str(paths["release_verifier"]),
                    str(receipt_path),
                    "--source-commit",
                    commit,
                    "--release-version",
                    "19.0.0",
                    "--maturity-report",
                    str(report_path),
                    "--evidence-root",
                    str(evidence_root),
                    "--required-gate",
                    "engineering-validation-v19",
                ],
                cwd=repository,
                capture_output=True,
                text=True,
            )
        self.assertEqual("engineering-validation-v19", identity["gate"])
        self.assertEqual(commit, identity["source_commit"])
        self.assertEqual(0, command.returncode, command.stderr)
        fields = command.stdout.strip().split("\t")
        self.assertEqual(3, len(fields))
        self.assertRegex(fields[0], r"^[0-9a-f]{64}$")
        self.assertEqual("19.0.0-rc.1", fields[1])
        self.assertEqual(commit, fields[2])

    def test_19_1_engineering_receipt_is_accepted_without_dropping_19_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(Path(tmp), release_version="19.2.0")
            identity = release_receipt.validate_receipt(
                receipt,
                expected_commit=commit,
                expected_version="19.2.0",
                verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
                repository_root=repository,
                engineering_paths=paths,
                maturity_report_path=report_path,
                evidence_root=evidence_root,
                semantic_revalidator=mocked_semantic_revalidator,
            )
        self.assertEqual("engineering-validation-v19", identity["gate"])
        self.assertEqual("19.2.0-rc.1", identity["release_candidate"])

    def test_engineering_receipt_reasserts_provenance_scores_claims_and_tools(self):
        def rejected(path, value):
            with tempfile.TemporaryDirectory() as tmp:
                (
                    repository,
                    commit,
                    receipt,
                    paths,
                    report_path,
                    evidence_root,
                ) = engineering_fixture(Path(tmp))
                target = receipt
                for key in path[:-1]:
                    target = target[key]
                target[path[-1]] = value
                with self.assertRaises(release_receipt.ReceiptError):
                    release_receipt.validate_receipt(
                        receipt,
                        expected_commit=commit,
                        expected_version="19.0.0",
                        verifier_path=(
                            ROOT / "scripts" / "verify-profile-outcomes.py"
                        ),
                        repository_root=repository,
                        engineering_paths=paths,
                        maturity_report_path=report_path,
                        evidence_root=evidence_root,
                        semantic_revalidator=mocked_semantic_revalidator,
                    )

        mutations = (
            (("semantic_evidence", "profile"), "nightly"),
            (("semantic_evidence", "case_count"), 25),
            (("semantic_evidence", "case_provenance"), {"simulated": 23}),
            (("semantic_evidence", "execution_mode"), "dry-run"),
            (("semantic_evidence", "distinct_judge_model"), False),
            (("semantic_evidence", "selection_sha256"), "bad"),
            (("maturity", "dimension_scores", "prompt"), 99),
            (("maturity", "required_hard_gates", "P19"), False),
            (("claims", "real_project_outcomes_validated"), True),
            (("claims", "default_profile"), "governed"),
            (("claims", "governed_outcome_claims_allowed"), True),
            (("claims", "governed_default_promotion_allowed"), True),
            (("tools", "release_verifier", "sha256"), "0" * 64),
        )
        for path, value in mutations:
            with self.subTest(path=path):
                rejected(path, value)

    def test_engineering_receipt_rejects_stale_evidence_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(Path(tmp))
            stale = (
                dt.datetime.now(dt.timezone.utc)
                - dt.timedelta(hours=25)
            ).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            for container, key in (
                (receipt, "issued_at"),
                (receipt["maturity"], "evaluated_at"),
                (receipt["semantic_evidence"], "oldest_result_at"),
                (receipt["semantic_evidence"], "newest_evidence_at"),
                (receipt["attestation"], "accepted_at"),
            ):
                container[key] = stale
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "older than 24 hours",
            ):
                release_receipt.validate_receipt(
                    receipt,
                    expected_commit=commit,
                    expected_version="19.0.0",
                    verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
                    repository_root=repository,
                    engineering_paths=paths,
                    maturity_report_path=report_path,
                    evidence_root=evidence_root,
                    semantic_revalidator=mocked_semantic_revalidator,
                )

    def test_post_release_continuation_relaxes_clock_only_and_keeps_integrity(self):
        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(Path(tmp), age_hours=25)
            common = {
                "expected_commit": commit,
                "expected_version": "19.0.0",
                "verifier_path": ROOT / "scripts" / "verify-profile-outcomes.py",
                "repository_root": repository,
                "engineering_paths": paths,
                "maturity_report_path": report_path,
                "evidence_root": evidence_root,
                "semantic_revalidator": mocked_semantic_revalidator,
            }
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "older than 24 hours",
            ):
                release_receipt.validate_receipt(receipt, **common)

            identity = release_receipt.validate_receipt(
                receipt,
                post_release_continuation=True,
                **common,
            )
            self.assertEqual("engineering-validation-v19", identity["gate"])
            self.assertEqual(commit, identity["source_commit"])

            tampered = copy.deepcopy(receipt)
            tampered["maturity"]["report_sha256"] = "0" * 64
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "report SHA-256",
            ):
                release_receipt.validate_receipt(
                    tampered,
                    post_release_continuation=True,
                    **common,
                )

        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(Path(tmp))
            tool = paths["issuer"]
            tool.write_text("# uncommitted replacement\n", encoding="utf-8")
            receipt["tools"]["issuer"]["sha256"] = hashlib.sha256(
                tool.read_bytes()
            ).hexdigest()
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "not bound to the release commit",
            ):
                release_receipt.validate_receipt(
                    receipt,
                    expected_commit=commit,
                    expected_version="19.0.0",
                    verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
                    repository_root=repository,
                    engineering_paths=paths,
                    maturity_report_path=report_path,
                    evidence_root=evidence_root,
                    semantic_revalidator=mocked_semantic_revalidator,
                )

    def test_engineering_gate_requires_bound_report_and_revalidated_raw_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                evidence_root,
            ) = engineering_fixture(Path(tmp))
            common = {
                "expected_commit": commit,
                "expected_version": "19.0.0",
                "verifier_path": ROOT / "scripts" / "verify-profile-outcomes.py",
                "repository_root": repository,
                "engineering_paths": paths,
            }
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "requires a private maturity report",
            ):
                release_receipt.validate_receipt(receipt, **common)

            wrong_hash = copy.deepcopy(receipt)
            wrong_hash["maturity"]["report_sha256"] = "0" * 64
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "report SHA-256",
            ):
                release_receipt.validate_receipt(
                    wrong_hash,
                    maturity_report_path=report_path,
                    evidence_root=evidence_root,
                    semantic_revalidator=mocked_semantic_revalidator,
                    **common,
                )

            missing_root = Path(tmp) / "missing-evidence"
            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "cannot resolve semantic evidence root",
            ):
                release_receipt.validate_receipt(
                    receipt,
                    maturity_report_path=report_path,
                    evidence_root=missing_root,
                    semantic_revalidator=mocked_semantic_revalidator,
                    **common,
                )

            def broken_chain(**arguments):
                result = mocked_semantic_revalidator(**arguments)
                result["head_record_hash"] = "0" * 64
                return result

            with self.assertRaisesRegex(
                release_receipt.ReceiptError,
                "differs from receipt field head_record_hash",
            ):
                release_receipt.validate_receipt(
                    receipt,
                    maturity_report_path=report_path,
                    evidence_root=evidence_root,
                    semantic_revalidator=broken_chain,
                    **common,
                )

    def test_ignored_untracked_repository_evidence_root_is_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            (
                repository,
                commit,
                receipt,
                paths,
                report_path,
                _outside_evidence,
            ) = engineering_fixture(Path(tmp))
            run_path = (
                repository
                / "memory"
                / "runs"
                / receipt["semantic_evidence"]["run_id"]
            )
            run_path.mkdir(parents=True)

            def repository_evidence_mock(**_arguments):
                return copy.deepcopy(receipt["semantic_evidence"])

            identity = release_receipt.validate_receipt(
                receipt,
                expected_commit=commit,
                expected_version="19.0.0",
                verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
                repository_root=repository,
                engineering_paths=paths,
                maturity_report_path=report_path,
                evidence_root=repository.resolve(),
                semantic_revalidator=repository_evidence_mock,
            )
        self.assertEqual("engineering-validation-v19", identity["gate"])

    def test_required_gate_rejects_legacy_profile_receipt_for_release_consumers(self):
        with tempfile.TemporaryDirectory() as tmp:
            receipt_path = Path(tmp) / "receipt.json"
            receipt_path.write_text(
                json.dumps(self.receipt(), sort_keys=True) + "\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-release-receipt.py"),
                    str(receipt_path),
                    "--source-commit",
                    "a" * 40,
                    "--release-version",
                    "19.0.0",
                    "--required-gate",
                    "engineering-validation-v19",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("required engineering-validation-v19", result.stderr)

    def test_release_pilot_receipt_rejects_cross_gate_summary(self):
        receipt = self.receipt(stage="release-pilot")
        receipt["gate"] = "profile-outcomes-v19"
        with self.assertRaisesRegex(
            release_receipt.ReceiptError, "invalid fields"
        ):
            self.validate(receipt)

    def test_receipt_rejects_other_commit_version_or_verifier(self):
        receipt = self.receipt()
        with self.assertRaisesRegex(
            release_receipt.ReceiptError, "source commit"
        ):
            release_receipt.validate_receipt(
                receipt,
                expected_commit="b" * 40,
                expected_version="19.0.0",
                verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
            )
        with self.assertRaisesRegex(
            release_receipt.ReceiptError, "release version"
        ):
            release_receipt.validate_receipt(
                receipt,
                expected_commit="a" * 40,
                expected_version="19.0.1",
                verifier_path=ROOT / "scripts" / "verify-profile-outcomes.py",
            )
        with tempfile.TemporaryDirectory() as tmp:
            other = Path(tmp) / "verifier.py"
            other.write_text("# different verifier\n", encoding="utf-8")
            with self.assertRaisesRegex(
                release_receipt.ReceiptError, "different outcome verifier"
            ):
                release_receipt.validate_receipt(
                    receipt,
                    expected_commit="a" * 40,
                    expected_version="19.0.0",
                    verifier_path=other,
                )

    def test_receipt_reasserts_thresholds_and_strict_shape(self):
        mutations = []
        below_completion = copy.deepcopy(self.receipt())
        below_completion["outcome_summary"]["lite_completion_rate"] = 0.5
        mutations.append(below_completion)
        safety_failure = copy.deepcopy(self.receipt())
        safety_failure["outcome_summary"]["safety_failure_count"] = 1
        mutations.append(safety_failure)
        extra_field = copy.deepcopy(self.receipt())
        extra_field["projects"] = []
        mutations.append(extra_field)
        for receipt in mutations:
            with self.subTest(receipt=receipt), self.assertRaises(
                release_receipt.ReceiptError
            ):
                self.validate(receipt)

    def test_private_receipt_reader_rejects_repository_path_and_tamper(self):
        repository_receipt = ROOT / ".private-release-receipt-test.json"
        repository_receipt.write_text(
            json.dumps(self.receipt()), encoding="utf-8"
        )
        self.addCleanup(repository_receipt.unlink, missing_ok=True)
        with self.assertRaisesRegex(
            release_receipt.ReceiptError, "outside the source repository"
        ):
            release_receipt.read_private_receipt(repository_receipt)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(json.dumps({"passed": True}), encoding="utf-8")
            with self.assertRaisesRegex(
                release_receipt.ReceiptError, "invalid fields"
            ):
                release_receipt.read_private_receipt(path)


if __name__ == "__main__":
    unittest.main()
