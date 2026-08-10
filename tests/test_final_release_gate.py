"""Shared live-publisher final-release gate tests."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "scripts" / "publish-common.sh"
ENGINEERING_TOOL_REFS = {
    "issuer": "scripts/issue-engineering-release-receipt.py",
    "release_verifier": "scripts/verify-release-receipt.py",
    "maturity_checker": "scripts/check-engineering-maturity.py",
    "semantic_verifier": "scripts/verify-semantic-evidence.py",
    "maturity_rubric": "references/engineering-maturity-rubric.json",
    "semantic_policy": "evals/semantic-evidence-policy.json",
    "receipt_schema": "references/engineering-release-receipt.schema.json",
}
MOCK_SEMANTIC_VERIFIER = """#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[sys.argv.index("--evidence-root") + 1])
sys.stdout.buffer.write((root / "mock-revalidated-summary.json").read_bytes())
"""
OUTCOME_SPEC = importlib.util.spec_from_file_location(
    "final_gate_outcome_fixtures", ROOT / "tests" / "test_profile_outcomes.py"
)
assert OUTCOME_SPEC and OUTCOME_SPEC.loader
outcome_fixtures = importlib.util.module_from_spec(OUTCOME_SPEC)
OUTCOME_SPEC.loader.exec_module(outcome_fixtures)


class FinalReleaseGateTests(unittest.TestCase):
    def fixture_repo(self, base: Path, version: str) -> tuple[Path, str]:
        repository = base / "repository"
        repository.mkdir()
        (repository / ".claude-plugin").mkdir()
        (repository / "scripts").mkdir()
        (repository / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"version": version}) + "\n", encoding="utf-8"
        )
        copied = {
            "scripts/publish-common.sh",
            "scripts/verify-profile-outcomes.py",
            "scripts/build-release-assets.py",
            *ENGINEERING_TOOL_REFS.values(),
        }
        for reference in sorted(copied):
            destination = repository / reference
            destination.parent.mkdir(parents=True, exist_ok=True)
            if reference == "scripts/verify-semantic-evidence.py":
                destination.write_text(MOCK_SEMANTIC_VERIFIER, encoding="utf-8")
                destination.chmod(0o755)
            else:
                shutil.copy2(ROOT / reference, destination)
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        subprocess.run(
            ["git", "config", "user.name", "Final Gate Test"],
            cwd=repository,
            check=True,
        )
        subprocess.run(
            ["git", "config", "user.email", "final-gate@example.com"],
            cwd=repository,
            check=True,
        )
        subprocess.run(["git", "add", "-A"], cwd=repository, check=True)
        subprocess.run(
            ["git", "commit", "-q", "-m", "fixture"],
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
        return repository, commit

    def run_gate(
        self,
        repository: Path,
        commit: str,
        *,
        environment: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess:
        command = (
            'source scripts/publish-common.sh; '
            'publish_require_final_release "owner/repository" "$1"'
        )
        return subprocess.run(
            ["bash", "-c", command, "final-gate-test", commit],
            cwd=repository,
            env=environment,
            capture_output=True,
            text=True,
        )

    def private_receipt(
        self,
        path: Path,
        commit: str,
        *,
        age_hours: int = 0,
    ) -> tuple[str, Path, Path]:
        repository = path.parent / "repository"
        tree = subprocess.run(
            ["git", "ls-tree", "-r", "--full-tree", commit],
            cwd=repository,
            check=True,
            capture_output=True,
        ).stdout
        stamp = (
            dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=age_hours)
        )
        stamp = (
            stamp
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )
        receipt = {
            "$schema": "references/engineering-release-receipt.schema.json",
            "schema_version": "1.0",
            "gate": "engineering-validation-v19",
            "passed": True,
            "release_version": "19.0.0",
            "release_candidate": "19.0.0-rc.1",
            "source_commit": commit,
            "issued_at": stamp,
            "repository": {
                "branch": "fixture",
                "worktree_clean": True,
                "source_tree_sha256": hashlib.sha256(tree).hexdigest(),
            },
            "tools": {
                name: {
                    "ref": reference,
                    "sha256": hashlib.sha256(
                        (repository / reference).read_bytes()
                    ).hexdigest(),
                }
                for name, reference in ENGINEERING_TOOL_REFS.items()
            },
            "maturity": {
                "evaluated_at": stamp,
                "report_sha256": "1" * 64,
                "target_score": 95,
                "achieved": True,
                "dimension_scores": {
                    name: 100
                    for name in ("prompt", "context", "harness", "loop", "graph")
                },
                "required_hard_gates": {
                    "P19": True,
                    "P20": True,
                    "H20": True,
                },
            },
            "semantic_evidence": {
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
            },
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
        rubric = json.loads(
            (repository / "references/engineering-maturity-rubric.json").read_text(
                encoding="utf-8"
            )
        )
        dimensions = {
            name: {
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
                        "evidence": "mocked owner-gate integration boundary",
                    }
                    for control in controls
                ],
            }
            for name, controls in rubric["dimensions"].items()
        }
        report = {
            "$schema": "references/engineering-maturity-report.schema.json",
            "schema_version": "1.0",
            "evaluated_at": stamp,
            "repository": {
                "git_available": True,
                "commit": commit,
                "branch": "fixture",
                "worktree_clean": True,
            },
            "checker": receipt["tools"]["maturity_checker"],
            "rubric_sha256": receipt["tools"]["maturity_rubric"]["sha256"],
            "target_score": 95,
            "achieved": True,
            "semantic_evidence_run_id": receipt["semantic_evidence"]["run_id"],
            "semantic_evidence": receipt["semantic_evidence"],
            "dimensions": dimensions,
        }
        report_path = path.parent / "private-maturity-report.json"
        report_raw = (
            json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
            + "\n"
        ).encode("utf-8")
        report_path.write_bytes(report_raw)
        report_path.chmod(0o600)
        receipt["maturity"]["report_sha256"] = hashlib.sha256(report_raw).hexdigest()
        evidence_root = path.parent / "mock-raw-evidence-boundary"
        evidence_root.mkdir(mode=0o700)
        (evidence_root / "mock-revalidated-summary.json").write_text(
            json.dumps(receipt["semantic_evidence"], sort_keys=True) + "\n",
            encoding="utf-8",
        )
        path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(path, 0o600)
        return (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            report_path,
            evidence_root,
        )

    def final_release_environment(
        self,
        base: Path,
        repository: Path,
        commit: str,
        receipt: Path,
        maturity_report: Path,
        evidence_root: Path,
        *,
        release_exists: bool,
    ) -> dict[str, str]:
        fake_bin = base / ("final-release-bin" if release_exists else "missing-release-bin")
        fake_bin.mkdir()
        fake_gh = fake_bin / "gh"
        fake_gh.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
commit = os.environ["FAKE_FINAL_COMMIT"]
release_exists = os.environ["FAKE_FINAL_RELEASE_EXISTS"] == "1"
if args[:2] == ["api", "repos/owner/repository/commits/v19.0.0"]:
    if not release_exists:
        raise SystemExit(1)
    print(commit)
elif args[:3] == ["release", "view", "v19.0.0"]:
    if not release_exists:
        raise SystemExit(1)
    print(json.dumps({
        "tagName": "v19.0.0",
        "isDraft": False,
        "isPrerelease": False,
    }))
elif args[:3] == ["api", "--method", "GET"]:
    print(json.dumps({"workflow_runs": [{
        "head_sha": commit,
        "conclusion": "success",
        "event": "workflow_dispatch",
    }]}))
elif args[:3] == ["release", "download", "v19.0.0"]:
    destination = Path(args[args.index("--dir") + 1])
    for name in (
        "aaron-marketing-skills-19.0.0-lite.tar.gz",
        "aaron-marketing-skills-19.0.0-pro.tar.gz",
        "aaron-marketing-skills-19.0.0-governed.tar.gz",
        "SHA256SUMS",
        "release-assets.json",
    ):
        (destination / name).write_text("fixture\\n", encoding="utf-8")
else:
    print("unsupported fake gh call: %r" % args, file=sys.stderr)
    raise SystemExit(91)
""",
            encoding="utf-8",
        )
        fake_gh.chmod(0o755)
        (repository / "scripts" / "build-release-assets.py").write_text(
            "#!/usr/bin/env python3\nraise SystemExit(0)\n",
            encoding="utf-8",
        )
        environment = os.environ.copy()
        environment.update(
            {
                "PATH": str(fake_bin) + os.pathsep + "/usr/bin:/bin",
                "AARON_RELEASE_RECEIPT": str(receipt),
                "AARON_RELEASE_MATURITY_REPORT": str(maturity_report),
                "AARON_RELEASE_EVIDENCE_ROOT": str(evidence_root),
                "FAKE_FINAL_COMMIT": commit,
                "FAKE_FINAL_RELEASE_EXISTS": "1" if release_exists else "0",
            }
        )
        for name in (
            "AARON_PUBLISH_EXPECTED_REPO",
            "AARON_PUBLISH_EXPECTED_COMMIT",
            "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN",
        ):
            environment.pop(name, None)
        return environment

    def private_profile_receipt(self, path: Path, commit: str) -> str:
        evidence = outcome_fixtures.valid_evidence()
        evidence["source_commit"] = commit
        summary = outcome_fixtures.profile_outcomes.evaluate(evidence)
        receipt = outcome_fixtures.profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=json.dumps(evidence, sort_keys=True).encode("utf-8"),
            evidence_manifest_sha256=outcome_fixtures.digest("private-manifest"),
        )
        path.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        os.chmod(path, 0o600)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @staticmethod
    def token(repository: str, commit: str, version: str, receipt_sha: str) -> str:
        value = "\0".join((repository, commit, version, receipt_sha))
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def test_pre_v19_release_does_not_require_the_new_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository, commit = self.fixture_repo(Path(temporary), "18.0.0")
            result = self.run_gate(repository, commit)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_supported_v19_releases_require_a_private_receipt(self):
        for version in ("19.0.0", "19.1.0", "19.2.0"):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temporary:
                repository, commit = self.fixture_repo(Path(temporary), version)
                result = self.run_gate(repository, commit)
                self.assertNotEqual(0, result.returncode)
                self.assertIn("AARON_RELEASE_RECEIPT", result.stderr)

    def test_exact_parent_gate_token_allows_a_child_without_repeating_network_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            receipt = base / "private-receipt.json"
            receipt_sha, maturity_report, evidence_root = self.private_receipt(
                receipt,
                commit,
            )
            environment = os.environ.copy()
            environment.update(
                {
                    "AARON_RELEASE_RECEIPT": str(receipt),
                    "AARON_RELEASE_MATURITY_REPORT": str(maturity_report),
                    "AARON_RELEASE_EVIDENCE_ROOT": str(evidence_root),
                    "AARON_PUBLISH_EXPECTED_REPO": "owner/repository",
                    "AARON_PUBLISH_EXPECTED_COMMIT": commit,
                    "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN": self.token(
                        "owner/repository", commit, "19.0.0", receipt_sha
                    ),
                    "PATH": "/usr/bin:/bin",
                }
            )
            result = self.run_gate(
                repository, commit, environment=environment
            )
            self.assertEqual(0, result.returncode, result.stderr)
            environment["AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN"] = "0" * 64
            result = self.run_gate(
                repository, commit, environment=environment
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("inherited final-release gate", result.stderr)

    def test_profile_outcome_receipt_cannot_bypass_engineering_release_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            receipt = base / "private-profile-receipt.json"
            receipt_sha = self.private_profile_receipt(receipt, commit)
            maturity_report = base / "unused-profile-maturity.json"
            maturity_report.write_text("{}\n", encoding="utf-8")
            maturity_report.chmod(0o600)
            evidence_root = base / "unused-profile-evidence"
            evidence_root.mkdir()
            environment = os.environ.copy()
            environment.update(
                {
                    "AARON_RELEASE_RECEIPT": str(receipt),
                    "AARON_RELEASE_MATURITY_REPORT": str(maturity_report),
                    "AARON_RELEASE_EVIDENCE_ROOT": str(evidence_root),
                    "AARON_PUBLISH_EXPECTED_REPO": "owner/repository",
                    "AARON_PUBLISH_EXPECTED_COMMIT": commit,
                    "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN": self.token(
                        "owner/repository", commit, "19.0.0", receipt_sha
                    ),
                    "PATH": "/usr/bin:/bin",
                }
            )
            result = self.run_gate(repository, commit, environment=environment)
        self.assertNotEqual(0, result.returncode)
        self.assertIn("required engineering-validation-v19", result.stderr)

    def test_v19_gate_requires_report_and_raw_evidence_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            receipt = base / "private-receipt.json"
            receipt_sha, maturity_report, evidence_root = self.private_receipt(
                receipt,
                commit,
            )
            environment = os.environ.copy()
            environment["AARON_RELEASE_RECEIPT"] = str(receipt)
            result = self.run_gate(repository, commit, environment=environment)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("AARON_RELEASE_MATURITY_REPORT", result.stderr)
            environment["AARON_RELEASE_MATURITY_REPORT"] = str(maturity_report)
            result = self.run_gate(repository, commit, environment=environment)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("AARON_RELEASE_EVIDENCE_ROOT", result.stderr)
            self.assertTrue(receipt_sha)
            self.assertTrue(evidence_root.is_dir())

    def test_stale_receipt_continues_only_after_final_release_gates(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            receipt = base / "private-stale-receipt.json"
            _receipt_sha, maturity_report, evidence_root = self.private_receipt(
                receipt,
                commit,
                age_hours=25,
            )

            missing_environment = self.final_release_environment(
                base,
                repository,
                commit,
                receipt,
                maturity_report,
                evidence_root,
                release_exists=False,
            )
            missing = self.run_gate(
                repository,
                commit,
                environment=missing_environment,
            )
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("cannot resolve immutable GitHub tag", missing.stderr)

            final_environment = self.final_release_environment(
                base,
                repository,
                commit,
                receipt,
                maturity_report,
                evidence_root,
                release_exists=True,
            )
            continued = self.run_gate(
                repository,
                commit,
                environment=final_environment,
            )
            self.assertEqual(0, continued.returncode, continued.stderr)
            self.assertIn("assets and CI verified", continued.stderr)


if __name__ == "__main__":
    unittest.main()
