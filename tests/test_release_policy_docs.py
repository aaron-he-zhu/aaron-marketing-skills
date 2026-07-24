"""Keep the public v19 validation boundary explicit across release surfaces."""
from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ReleasePolicyDocumentationTests(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def normalized(self, relative: str) -> str:
        return " ".join(self.read(relative).lower().split())

    def test_public_release_surfaces_disclose_the_validation_boundary(self):
        for relative in (
            "README.md",
            "VERSIONS.md",
            "references/capability-profiles.md",
        ):
            with self.subTest(relative=relative):
                text = self.normalized(relative)
                self.assertIn("engineering-validated", text)
                self.assertIn("real-project outcomes remain unvalidated", text)
                self.assertIn("lite remains", text)
                self.assertIn("default", text)
                self.assertIn("14", text)
                self.assertIn("70", text)
                self.assertIn("28", text)

    def test_runbooks_separate_release_from_outcome_promotion(self):
        for relative in ("CONTRIBUTING.md", "docs/distribution.md"):
            with self.subTest(relative=relative):
                text = self.normalized(relative)
                self.assertIn("engineering-validation-v19", text)
                self.assertIn("--maturity-report-output", text)
                self.assertIn("same invocation", text)
                self.assertNotIn("external report", text)
                self.assertIn("verify-release-receipt.py", text)
                self.assertIn(
                    '--maturity-report "$aaron_release_maturity_report"', text
                )
                self.assertIn(
                    '--evidence-root "$aaron_release_evidence_root"', text
                )
                self.assertIn("aaron_release_receipt", text)
                self.assertIn("aaron_release_maturity_report", text)
                self.assertIn("aaron_release_evidence_root", text)
                self.assertIn("git-ignored and wholly untracked", text)
                self.assertIn("never upload", text)
                self.assertIn("post-release", text)
                self.assertIn("post-release-continuation", text)
                self.assertIn("24-hour", text)
                self.assertIn("currently 30 days", text)
                self.assertIn("same immutable release commit", text)
                self.assertIn("neither authorizes a release", text)
                self.assertIn("simulated semantic fixtures", text)

    def test_owner_workflow_reminder_does_not_claim_project_validation(self):
        text = self.normalized(".github/workflows/release-validation.yml")
        self.assertIn("engineering-validation-v19", text)
        self.assertIn("--maturity-report-output", text)
        self.assertIn("same invocation", text)
        self.assertIn("exact report bytes", text)
        self.assertNotIn("external report", text)
        self.assertIn("verify-release-receipt.py", text)
        self.assertIn("create-github-release.py --live", text)
        self.assertIn("--maturity-report <private-report>", text)
        self.assertIn("--evidence-root <absolute-evidence-root>", text)
        self.assertIn("aaron_release_receipt", text)
        self.assertIn("aaron_release_maturity_report", text)
        self.assertIn("aaron_release_evidence_root", text)
        self.assertIn("git-ignored and wholly untracked", text)
        self.assertIn("does **not** receive or upload", text)
        self.assertIn("strict 24-hour freshness gate", text)
        self.assertIn("currently 30 days", text)
        self.assertIn("real-project outcomes remain unvalidated", text)
        self.assertIn("lite remains the default", text)


if __name__ == "__main__":
    unittest.main()
