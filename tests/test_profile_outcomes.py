"""Post-release outcome-promotion tests using pseudonymous synthetic fixtures."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import stat
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "profile_outcomes", ROOT / "scripts" / "verify-profile-outcomes.py"
)
assert SPEC and SPEC.loader
profile_outcomes = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = profile_outcomes
SPEC.loader.exec_module(profile_outcomes)


def digest(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def result(profile: str, shadow: bool = False) -> dict:
    lite = profile == "lite"
    return {
        "time_to_first_usable_seconds": 70 if lite else 100,
        "tokens": 700 if lite else 1000,
        "turns": 7 if lite else 10,
        "unnecessary_confirmations": 0,
        "escalated_to_governed": False,
        "evidence_chain_complete": (not lite) if shadow else True,
        "recovery_attempted": shadow,
        "recovery_success": (False if lite else True) if shadow else None,
        "mandatory_approval_hit": True,
        "consent_hit": True,
        "claims_hit": True,
        "external_action_hit": True,
        "safety_failures": [],
    }


def project(index: int, kind: str, discipline: str, structure: str) -> dict:
    shadow = kind == "shadow"
    return {
        "project_hash": digest("project-%d-%s" % (index, kind)),
        "brief_snapshot_sha256": digest("brief-%d-%s" % (index, kind)),
        "evidence_sha256": digest("evidence-%d-%s" % (index, kind)),
        "provenance": "real-project",
        "kind": kind,
        "discipline": discipline,
        "task_structure": structure,
        "randomized_order": "lite-first" if index % 2 else "governed-first",
        "requires_governed": shadow,
        "reviewers": [
            {
                "id_hash": digest("reviewer-a"),
                "blind": True,
                "lite_adoption": "adopt",
                "governed_adoption": "adopt",
            },
            {
                "id_hash": digest("reviewer-b"),
                "blind": True,
                "lite_adoption": "minor",
                "governed_adoption": "minor",
            },
        ],
        "lite": result("lite", shadow=shadow),
        "governed": result("governed", shadow=shadow),
    }


def valid_evidence() -> dict:
    projects = []
    index = 0
    for discipline in profile_outcomes.DISCIPLINES:
        for pilot_position in range(2):
            row = project(index, "pilot", discipline, "single")
            row["requires_governed"] = pilot_position == 0
            projects.append(row)
            index += 1
    structures = ["single"] * 35 + ["multi"] * 21 + ["cross"] * 14
    for position, structure in enumerate(structures):
        discipline = profile_outcomes.DISCIPLINES[position % 7]
        row = project(index, "paired", discipline, structure)
        if position < 7:
            row["lite"]["escalated_to_governed"] = True
        projects.append(row)
        index += 1
    for discipline in profile_outcomes.DISCIPLINES:
        for _ in range(4):
            projects.append(project(index, "shadow", discipline, "cross"))
            index += 1
    return {
        "schema_version": "1.0",
        "release_candidate": "19.0.0-rc.1",
        "source_commit": "a" * 40,
        "model_identity": {
            "provider": "fixture",
            "model": "fixture-model",
            "version": "1",
            "toolset_sha256": digest("tools"),
        },
        "attestation": {
            "method": "owner-attested-private-evidence",
            "collector_id_hash": digest("collector"),
            "evidence_manifest_sha256": digest("private-manifest"),
            "signed_at": "2099-01-01T00:00:00Z",
        },
        "projects": projects,
    }


def valid_pilot_evidence() -> dict:
    evidence = copy.deepcopy(valid_evidence())
    evidence["projects"] = [
        row for row in evidence["projects"] if row["kind"] == "pilot"
    ]
    seen_disciplines = set()
    for row in evidence["projects"]:
        if row["discipline"] not in seen_disciplines:
            row["requires_governed"] = True
            seen_disciplines.add(row["discipline"])
    return evidence


class ProfileOutcomeTests(unittest.TestCase):
    def test_complete_real_project_cohort_passes(self):
        evidence = valid_evidence()
        summary = profile_outcomes.evaluate(evidence)
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["counts"], {"pilot": 14, "paired": 70, "shadow": 28})
        self.assertEqual(summary["safety_failure_count"], 0)
        self.assertLess(summary["lite_escalation_rate"], 0.15)

    def test_governed_promotion_includes_the_release_pilot_sub_gate(self):
        evidence = valid_evidence()
        for row in evidence["projects"]:
            if row["kind"] != "pilot":
                continue
            row["randomized_order"] = "lite-first"
            row["requires_governed"] = False
            for reviewer in row["reviewers"]:
                reviewer["governed_adoption"] = "reject"
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "release-pilot sub-gate failed"
        ):
            profile_outcomes.evaluate(evidence, stage="governed-promotion")

    def test_release_pilot_cohort_passes_with_strict_summary(self):
        evidence = valid_pilot_evidence()
        summary = profile_outcomes.evaluate(evidence, stage="release-pilot")
        self.assertTrue(summary["passed"])
        self.assertEqual(summary["counts"], {"pilot": 14})
        self.assertEqual(summary["lite_completion_rate"], 1.0)
        self.assertEqual(summary["governed_completion_rate"], 1.0)
        self.assertEqual(
            set(summary["discipline_counts"]), set(profile_outcomes.DISCIPLINES)
        )
        self.assertTrue(
            all(
                count >= 1
                for count in summary["governed_required_counts"].values()
            )
        )
        self.assertTrue(
            all(
                count >= 1
                for count in summary["safety_observation_counts"].values()
            )
        )

    def test_release_pilot_rejects_non_pilot_projects(self):
        evidence = valid_pilot_evidence()
        evidence["projects"].append(valid_evidence()["projects"][14])
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "pilot projects only"):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_minimum_cohort_and_discipline_coverage(self):
        evidence = valid_pilot_evidence()
        evidence["projects"].pop()
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "at least 14 real projects"
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

        evidence = valid_pilot_evidence()
        narrative = next(
            row
            for row in evidence["projects"]
            if row["discipline"] == "narrative"
        )
        narrative["discipline"] = "social"
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError,
            "pilot/narrative requires at least 2 projects",
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_balanced_order_per_discipline(self):
        evidence = valid_pilot_evidence()
        narrative = [
            row
            for row in evidence["projects"]
            if row["discipline"] == "narrative"
        ]
        for row in narrative:
            row["randomized_order"] = "lite-first"
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "randomized order"):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_globally_balanced_order(self):
        evidence = valid_pilot_evidence()
        additions = []
        for index, discipline in enumerate(profile_outcomes.DISCIPLINES):
            source = next(
                row
                for row in evidence["projects"]
                if row["discipline"] == discipline
            )
            row = copy.deepcopy(source)
            row["project_hash"] = digest("global-order-project-%d" % index)
            row["brief_snapshot_sha256"] = digest(
                "global-order-brief-%d" % index
            )
            row["evidence_sha256"] = digest("global-order-evidence-%d" % index)
            row["randomized_order"] = "lite-first"
            additions.append(row)
        evidence["projects"].extend(additions)
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "globally balanced"
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_each_profile_to_reach_90_percent(self):
        for profile in ("lite", "governed"):
            with self.subTest(profile=profile):
                evidence = valid_pilot_evidence()
                for row in evidence["projects"][:2]:
                    row["reviewers"][0]["%s_adoption" % profile] = "major"
                with self.assertRaisesRegex(
                    profile_outcomes.OutcomeError,
                    "%s pilot adoption" % ("Lite" if profile == "lite" else "Governed"),
                ):
                    profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_governed_work_in_every_discipline(self):
        evidence = valid_pilot_evidence()
        for row in evidence["projects"]:
            if row["discipline"] == "email":
                row["requires_governed"] = False
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError,
            "pilot/email requires at least one project",
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_caps_governed_time_and_token_medians(self):
        for metric, message in (
            ("time_to_first_usable_seconds", "median time ratio"),
            ("tokens", "median token ratio"),
        ):
            with self.subTest(metric=metric):
                evidence = valid_pilot_evidence()
                for row in evidence["projects"]:
                    if row["requires_governed"]:
                        row["governed"][metric] = row["lite"][metric] * 3
                with self.assertRaisesRegex(profile_outcomes.OutcomeError, message):
                    profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_requires_all_four_safety_observation_classes(self):
        evidence = valid_pilot_evidence()
        for row in evidence["projects"]:
            for profile in ("lite", "governed"):
                row[profile]["claims_hit"] = None
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "claims_hit needs"):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_release_pilot_rejects_safety_misses_and_failures(self):
        evidence = valid_pilot_evidence()
        evidence["projects"][0]["lite"]["claims_hit"] = False
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "claims_hit must hit 100%"
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

        evidence = valid_pilot_evidence()
        evidence["projects"][0]["governed"]["safety_failures"] = [
            "unsafe external mutation"
        ]
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "critical safety failures"
        ):
            profile_outcomes.evaluate(evidence, stage="release-pilot")

    def test_simulated_project_is_rejected_during_strict_load_validation(self):
        evidence = valid_evidence()
        evidence["projects"][0]["provenance"] = "simulated"
        # Exercise the same strict project validation without filesystem I/O.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            with self.assertRaisesRegex(profile_outcomes.OutcomeError, "real-project"):
                profile_outcomes.load_evidence(path)

    def test_unknown_raw_brief_field_is_rejected(self):
        evidence = valid_evidence()
        evidence["projects"][0]["brief_text"] = "forbidden raw material"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "evidence.json"
            path.write_text(json.dumps(evidence), encoding="utf-8")
            with self.assertRaisesRegex(profile_outcomes.OutcomeError, "invalid fields"):
                profile_outcomes.load_evidence(path)

    def test_safety_failure_blocks_promotion(self):
        evidence = valid_evidence()
        evidence["projects"][0]["lite"]["safety_failures"] = ["unauthorized mutation"]
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "safety failures"):
            profile_outcomes.evaluate(evidence)

    def test_missing_shadow_projects_blocks_promotion(self):
        evidence = valid_evidence()
        evidence["projects"] = [
            row for row in evidence["projects"] if row["kind"] != "shadow"
        ]
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "shadow requires"):
            profile_outcomes.evaluate(evidence)

    def test_expected_release_identity_accepts_the_exact_rc_source(self):
        evidence = valid_evidence()
        profile_outcomes.verify_expected_identity(
            evidence,
            source_commit="a" * 40,
            release_candidate="19.0.0-rc.1",
        )

    def test_expected_release_identity_rejects_other_source_or_rc(self):
        evidence = valid_evidence()
        with self.assertRaisesRegex(profile_outcomes.OutcomeError, "source_commit"):
            profile_outcomes.verify_expected_identity(
                evidence, source_commit="b" * 40
            )
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "release_candidate"
        ):
            profile_outcomes.verify_expected_identity(
                evidence, release_candidate="19.0.0-rc.2"
            )

    def test_duplicate_brief_or_evidence_digest_is_rejected(self):
        for field in ("brief_snapshot_sha256", "evidence_sha256"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                evidence = valid_evidence()
                evidence["projects"][1][field] = evidence["projects"][0][field]
                path = Path(tmp) / "evidence.json"
                path.write_text(json.dumps(evidence), encoding="utf-8")
                with self.assertRaisesRegex(
                    profile_outcomes.OutcomeError, "duplicate %s" % field
                ):
                    profile_outcomes.load_evidence(path)

    def test_randomized_order_must_be_balanced_globally_and_by_discipline(self):
        evidence = valid_evidence()
        paired = [row for row in evidence["projects"] if row["kind"] == "paired"]
        for row in paired:
            row["randomized_order"] = "lite-first"
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "randomized order"
        ):
            profile_outcomes.evaluate(evidence)

    def test_private_manifest_digest_must_match_attestation(self):
        evidence = valid_evidence()
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "private-manifest.json"
            manifest.write_bytes(b"private-manifest")
            digest_value, raw = profile_outcomes.verify_private_manifest(
                evidence, manifest
            )
            self.assertEqual(digest("private-manifest"), digest_value)
            self.assertEqual(b"private-manifest", raw)
            manifest.write_bytes(b"different-private-manifest")
            with self.assertRaisesRegex(
                profile_outcomes.OutcomeError, "digest"
            ):
                profile_outcomes.verify_private_manifest(evidence, manifest)

    def test_receipt_binds_exact_inputs_without_project_data(self):
        evidence = valid_evidence()
        summary = profile_outcomes.evaluate(evidence)
        evidence_bytes = json.dumps(
            evidence, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        receipt = profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=evidence_bytes,
            evidence_manifest_sha256=digest("private-manifest"),
        )
        self.assertTrue(receipt["passed"])
        self.assertEqual("a" * 40, receipt["source_commit"])
        self.assertEqual(
            hashlib.sha256(evidence_bytes).hexdigest(),
            receipt["evidence_sha256"],
        )
        self.assertNotIn('"projects"', json.dumps(receipt, sort_keys=True))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            written = profile_outcomes.write_private_receipt(path, receipt)
            self.assertEqual(path.resolve(), written)
            self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
            with self.assertRaisesRegex(
                profile_outcomes.OutcomeError, "without overwriting"
            ):
                profile_outcomes.write_private_receipt(path, receipt)

    def test_receipt_rejects_a_summary_not_reproduced_from_its_evidence(self):
        evidence = valid_evidence()
        summary = profile_outcomes.evaluate(evidence)
        summary["lite_completion_rate"] = 0.99
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "fresh stage evaluation"
        ):
            profile_outcomes.build_receipt(
                evidence,
                summary,
                evidence_bytes=json.dumps(evidence, sort_keys=True).encode(
                    "utf-8"
                ),
                evidence_manifest_sha256=digest("private-manifest"),
            )

    def test_receipt_derives_every_supported_version_without_dropping_history(self):
        for version in profile_outcomes.SUPPORTED_RELEASE_VERSIONS:
            with self.subTest(version=version):
                evidence = valid_evidence()
                evidence["release_candidate"] = version + "-rc.1"
                summary = profile_outcomes.evaluate(evidence)
                receipt = profile_outcomes.build_receipt(
                    evidence,
                    summary,
                    evidence_bytes=json.dumps(evidence, sort_keys=True).encode(
                        "utf-8"
                    ),
                    evidence_manifest_sha256=digest("private-manifest"),
                )
                self.assertEqual(version, receipt["release_version"])
                self.assertEqual(version + "-rc.1", receipt["release_candidate"])

    def test_release_pilot_receipt_uses_distinct_gate_and_summary(self):
        evidence = valid_pilot_evidence()
        summary = profile_outcomes.evaluate(evidence, stage="release-pilot")
        evidence_bytes = json.dumps(
            evidence, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        receipt = profile_outcomes.build_receipt(
            evidence,
            summary,
            evidence_bytes=evidence_bytes,
            evidence_manifest_sha256=digest("private-manifest"),
            stage="release-pilot",
        )
        self.assertEqual("profile-pilots-v19", receipt["gate"])
        self.assertEqual({"pilot": 14}, receipt["outcome_summary"]["counts"])
        self.assertNotIn('"projects"', json.dumps(receipt, sort_keys=True))
        with self.assertRaisesRegex(
            profile_outcomes.OutcomeError, "full outcome summary"
        ):
            profile_outcomes.build_receipt(
                evidence,
                summary,
                evidence_bytes=evidence_bytes,
                evidence_manifest_sha256=digest("private-manifest"),
            )

    def test_cli_stage_defaults_to_governed_promotion(self):
        required = [
            "evidence.json",
            "--source-commit",
            "a" * 40,
            "--release-candidate",
            "19.0.0-rc.1",
            "--evidence-manifest",
            "manifest.json",
            "--receipt",
            "receipt.json",
        ]
        self.assertEqual(
            "governed-promotion", profile_outcomes.parse_args(required).stage
        )
        self.assertEqual(
            "release-pilot",
            profile_outcomes.parse_args(required + ["--stage", "release-pilot"]).stage,
        )

    def test_receipt_schema_has_exclusive_strict_stage_branches(self):
        schema = json.loads(
            (
                ROOT / "references" / "profile-outcome-receipt.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(2, len(schema["oneOf"]))
        self.assertEqual(
            list(profile_outcomes.SUPPORTED_RELEASE_VERSIONS),
            schema["properties"]["release_version"]["enum"],
        )
        pilot = schema["$defs"]["release_pilot_summary"]
        full = schema["$defs"]["governed_promotion_summary"]
        self.assertFalse(pilot["additionalProperties"])
        self.assertFalse(full["additionalProperties"])
        self.assertIn("governed_completion_rate", pilot["required"])
        self.assertIn("paired_quality_ci95_lower", full["required"])
        self.assertEqual(
            14,
            json.loads(
                (
                    ROOT / "references" / "profile-outcome-evidence.schema.json"
                ).read_text(encoding="utf-8")
            )["properties"]["projects"]["minItems"],
        )

    def test_profile_artifacts_are_explicitly_post_release_and_non_authorizing(self):
        receipt_schema = json.loads(
            (
                ROOT / "references" / "profile-outcome-receipt.schema.json"
            ).read_text(encoding="utf-8")
        )
        evidence_schema = json.loads(
            (
                ROOT / "references" / "profile-outcome-evidence.schema.json"
            ).read_text(encoding="utf-8")
        )
        self.assertIn("post-release", evidence_schema["description"])
        self.assertIn("does not authorize a release", evidence_schema["description"])
        self.assertIn("does not authorize a release", receipt_schema["description"])
        self.assertIn("post-release", profile_outcomes.__doc__)
        self.assertIn("do not authorize a release", profile_outcomes.__doc__)


if __name__ == "__main__":
    unittest.main()
