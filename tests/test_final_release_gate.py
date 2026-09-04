"""Shared live-publisher final-release gate tests."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FinalReleaseGateTests(unittest.TestCase):
    def fixture_repo(self, base: Path, version: str) -> tuple[Path, str]:
        repository = base / "repository"
        repository.mkdir()
        (repository / ".claude-plugin").mkdir()
        (repository / "scripts").mkdir()
        (repository / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"version": version}) + "\n", encoding="utf-8"
        )
        for reference in (
            "scripts/publish-common.sh",
            "scripts/build-release-assets.py",
        ):
            destination = repository / reference
            destination.parent.mkdir(parents=True, exist_ok=True)
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

    def final_release_environment(
        self,
        base: Path,
        repository: Path,
        commit: str,
        *,
        release_exists: bool,
        version: str = "19.0.0",
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
tag = "v" + os.environ["FAKE_FINAL_VERSION"]
if args[:2] == ["api", "repos/owner/repository/commits/" + tag]:
    if not release_exists:
        raise SystemExit(1)
    print(commit)
elif args[:3] == ["release", "view", tag]:
    if not release_exists:
        raise SystemExit(1)
    print(json.dumps({
        "tagName": tag,
        "isDraft": False,
        "isPrerelease": False,
    }))
elif args[:3] == ["api", "--method", "GET"]:
    print(json.dumps({"workflow_runs": [{
        "head_sha": commit,
        "conclusion": "success",
        "event": "workflow_dispatch",
    }]}))
elif args[:3] == ["release", "download", tag]:
    destination = Path(args[args.index("--dir") + 1])
    version = os.environ["FAKE_FINAL_VERSION"]
    for name in (
        "aaron-marketing-skills-%s-lite.tar.gz" % version,
        "aaron-marketing-skills-%s-pro.tar.gz" % version,
        "aaron-marketing-skills-%s-governed.tar.gz" % version,
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
                "FAKE_FINAL_COMMIT": commit,
                "FAKE_FINAL_VERSION": version,
                "FAKE_FINAL_RELEASE_EXISTS": "1" if release_exists else "0",
            }
        )
        for name in (
            "AARON_RELEASE_RECEIPT",
            "AARON_RELEASE_MATURITY_REPORT",
            "AARON_RELEASE_EVIDENCE_ROOT",
            "AARON_PUBLISH_EXPECTED_REPO",
            "AARON_PUBLISH_EXPECTED_COMMIT",
            "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN",
        ):
            environment.pop(name, None)
        return environment

    @staticmethod
    def token(repository: str, commit: str, version: str) -> str:
        value = "\0".join((repository, commit, version))
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def test_pre_v19_release_does_not_require_the_new_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository, commit = self.fixture_repo(Path(temporary), "18.0.0")
            result = self.run_gate(repository, commit)
            self.assertEqual(0, result.returncode, result.stderr)

    def test_supported_v19_releases_do_not_require_private_receipt_env(self):
        current = json.loads(
            (ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )["version"]
        versions = ("19.0.0", "19.1.0", "19.2.0", "20.0.0", current)
        for version in dict.fromkeys(versions):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as temporary:
                repository, commit = self.fixture_repo(Path(temporary), version)
                result = self.run_gate(repository, commit)
                self.assertNotEqual(0, result.returncode)
                self.assertNotIn("AARON_RELEASE_RECEIPT", result.stderr)
                self.assertNotIn("AARON_RELEASE_MATURITY_REPORT", result.stderr)
                self.assertNotIn("AARON_RELEASE_EVIDENCE_ROOT", result.stderr)
                self.assertRegex(
                    result.stderr,
                    r"GitHub CLI is required|cannot resolve immutable GitHub tag",
                )

    def test_exact_parent_gate_token_allows_a_child_without_repeating_network_checks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            environment = os.environ.copy()
            environment.update(
                {
                    "AARON_PUBLISH_EXPECTED_REPO": "owner/repository",
                    "AARON_PUBLISH_EXPECTED_COMMIT": commit,
                    "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN": self.token(
                        "owner/repository", commit, "19.0.0"
                    ),
                    "PATH": "/usr/bin:/bin",
                }
            )
            for name in (
                "AARON_RELEASE_RECEIPT",
                "AARON_RELEASE_MATURITY_REPORT",
                "AARON_RELEASE_EVIDENCE_ROOT",
            ):
                environment.pop(name, None)
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

    def test_v19_gate_ignores_private_receipt_environment(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")
            environment = self.final_release_environment(
                base,
                repository,
                commit,
                release_exists=True,
            )
            environment["AARON_RELEASE_RECEIPT"] = "/does-not-exist/receipt.json"
            environment["AARON_RELEASE_MATURITY_REPORT"] = (
                "/does-not-exist/maturity-report.json"
            )
            environment["AARON_RELEASE_EVIDENCE_ROOT"] = "/does-not-exist/evidence"
            result = self.run_gate(
                repository, commit, environment=environment
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("assets and CI verified", result.stderr)
            self.assertNotIn("AARON_RELEASE_RECEIPT", result.stderr)

    def test_final_release_gates_run_without_private_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, commit = self.fixture_repo(base, "19.0.0")

            missing_environment = self.final_release_environment(
                base,
                repository,
                commit,
                release_exists=False,
            )
            missing = self.run_gate(
                repository,
                commit,
                environment=missing_environment,
            )
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("cannot resolve immutable GitHub tag", missing.stderr)
            self.assertNotIn("AARON_RELEASE_RECEIPT", missing.stderr)

            final_environment = self.final_release_environment(
                base,
                repository,
                commit,
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
