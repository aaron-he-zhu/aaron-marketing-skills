"""Shared live-publisher final-release gate tests."""
from __future__ import annotations

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
        for name in (
            "publish-common.sh",
            "verify-profile-outcomes.py",
            "verify-release-receipt.py",
            "build-release-assets.py",
        ):
            shutil.copy2(ROOT / "scripts" / name, repository / "scripts" / name)
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

    def private_receipt(self, path: Path, commit: str) -> str:
        evidence = outcome_fixtures.valid_evidence()
        evidence["source_commit"] = commit
        summary = outcome_fixtures.profile_outcomes.evaluate(evidence)
        evidence_bytes = json.dumps(evidence, sort_keys=True).encode("utf-8")
        receipt = outcome_fixtures.profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=evidence_bytes,
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

    def test_v19_release_requires_a_private_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository, commit = self.fixture_repo(Path(temporary), "19.0.0")
            result = self.run_gate(repository, commit)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("AARON_RELEASE_RECEIPT", result.stderr)

    def test_exact_parent_gate_token_allows_a_child_without_repeating_network_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            receipt = base / "private-receipt.json"
            receipt_sha = self.private_receipt(receipt, commit)
            environment = os.environ.copy()
            environment.update(
                {
                    "AARON_RELEASE_RECEIPT": str(receipt),
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


if __name__ == "__main__":
    unittest.main()
