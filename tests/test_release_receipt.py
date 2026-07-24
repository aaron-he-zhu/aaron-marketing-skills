"""Private release-receipt validation tests."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
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


class ReleaseReceiptTests(unittest.TestCase):
    def receipt(self) -> dict:
        evidence = test_profile_outcomes.valid_evidence()
        summary = test_profile_outcomes.profile_outcomes.evaluate(evidence)
        return test_profile_outcomes.profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=json.dumps(evidence, sort_keys=True).encode("utf-8"),
            evidence_manifest_sha256=test_profile_outcomes.digest(
                "private-manifest"
            ),
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
