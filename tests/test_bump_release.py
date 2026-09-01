"""Transactional release-bump tests against a copied canonical fixture."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "bump-release.py"


def canonical_skill_paths() -> list[str]:
    catalog = json.loads(
        (ROOT / "references" / "system-catalog.json").read_text(encoding="utf-8")
    )
    result = []
    for discipline, spec in catalog["disciplines"].items():
        for phase, slugs in spec["phases"].items():
            result.extend(
                "%s/%s/%s/SKILL.md" % (discipline, phase, slug) for slug in slugs
            )
    result.extend(
        "protocol/%s/SKILL.md" % slug for slug in catalog["protocol"]["skills"]
    )
    return result


def build_fixture(target: Path) -> None:
    files = [
        "VERSIONS.md",
        "references/system-catalog.json",
        "references/framework-catalog.json",
        "references/workflow-graph.source.json",
        "references/audit-artifact.schema.json",
        "references/capability-profiles.json",
        "references/engineering-release-receipt.schema.json",
        "references/profile-outcome-evidence.schema.json",
        "references/profile-outcome-receipt.schema.json",
        "references/auditor-runbook.md",
        "docs/registry-submissions.md",
        "scripts/create-github-release.py",
        "scripts/issue-engineering-release-receipt.py",
        "scripts/publish-skillhub.sh",
        "scripts/bump-release.py",
        "scripts/verify-profile-outcomes.py",
        "scripts/verify-release-receipt.py",
    ] + canonical_skill_paths()
    for relative in files:
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def python_constant(path: Path, name: str):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    matches = [
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == name
    ]
    if len(matches) != 1:
        raise AssertionError("%s does not define exactly one %s" % (path, name))
    return ast.literal_eval(matches[0])


class BumpReleaseTests(unittest.TestCase):
    def run_bump(self, root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "python3",
                "scripts/bump-release.py",
                "--root",
                str(root),
                "--to",
                "99.0.0",
                "--date",
                "2099-01-02",
                "--align-all-skills",
                *extra,
            ],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dry_run_changes_nothing_and_reports_exact_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            build_fixture(fixture)
            before = (fixture / "VERSIONS.md").read_bytes()
            result = self.run_bump(fixture, "--json")
            after = (fixture / "VERSIONS.md").read_bytes()
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["canonical_skill_count"], 120)
        self.assertGreaterEqual(payload["changed_file_count"], 135)
        self.assertEqual(before, after)

    def test_write_aligns_all_current_bindings_and_preserves_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            build_fixture(fixture)
            historical = (
                fixture / "references" / "system-catalog.json"
            ).read_text(encoding="utf-8").count('"since_version": "18.0.0"')
            result = self.run_bump(fixture, "--write")
            self.assertEqual(result.returncode, 0, result.stderr)
            catalog = json.loads(
                (fixture / "references" / "system-catalog.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(catalog["bundle_version"], "99.0.0")
            self.assertEqual(catalog["architecture_version"], "99.0.0")
            self.assertEqual(
                (fixture / "references" / "system-catalog.json")
                .read_text(encoding="utf-8")
                .count('"since_version": "18.0.0"'),
                historical,
            )
            versions = (fixture / "VERSIONS.md").read_text(encoding="utf-8")
            self.assertIn(
                "### v99.0.0 — Cross-discipline control plane",
                versions,
            )
            self.assertIn("### v18.0.0 — Seven-discipline", versions)
            self.assertIn("One protocol, domain-owned semantics", versions)
            self.assertIn("Seven-discipline adoption", versions)
            self.assertIn("Selected-ancestry runtime proof", versions)
            self.assertIn("Typed handoffs, bounded context", versions)
            self.assertIn("NOT_VERIFIED", versions)
            self.assertIn("strict semantic corpus grows to 734", versions)
            for relative in canonical_skill_paths():
                text = (fixture / relative).read_text(encoding="utf-8")
                self.assertIn('version: "99.0.0"', text)
                metadata = next(
                    line.removeprefix("metadata: ")
                    for line in text.splitlines()
                    if line.startswith("metadata: ")
                )
                self.assertEqual(json.loads(metadata)["version"], "99.0.0")

            expected_support = (
                "19.0.0",
                "19.1.0",
                "19.2.0",
                "20.0.0",
                "20.1.0",
                "99.0.0",
            )
            for relative in (
                "scripts/verify-release-receipt.py",
                "scripts/verify-profile-outcomes.py",
            ):
                self.assertEqual(
                    expected_support,
                    python_constant(
                        fixture / relative, "SUPPORTED_RELEASE_VERSIONS"
                    ),
                )
            for relative in (
                "references/profile-outcome-receipt.schema.json",
                "references/engineering-release-receipt.schema.json",
            ):
                schema = json.loads((fixture / relative).read_text(encoding="utf-8"))
                self.assertEqual(
                    list(expected_support),
                    schema["properties"]["release_version"]["enum"],
                )
                pattern = schema["properties"]["release_candidate"]["pattern"]
                for version in expected_support:
                    self.assertIsNotNone(re.fullmatch(pattern, version + "-rc.1"))
            evidence_schema = json.loads(
                (
                    fixture / "references" / "profile-outcome-evidence.schema.json"
                ).read_text(encoding="utf-8")
            )
            evidence_pattern = evidence_schema["properties"]["release_candidate"][
                "pattern"
            ]
            for version in expected_support:
                self.assertIsNotNone(
                    re.fullmatch(evidence_pattern, version + "-rc.1")
                )
            self.assertEqual(
                "99.0.0",
                python_constant(
                    fixture / "scripts" / "issue-engineering-release-receipt.py",
                    "RELEASE_VERSION",
                ),
            )
            self.assertEqual(
                "99.0.0",
                python_constant(
                    fixture / "scripts" / "create-github-release.py",
                    "RELEASE_VERSION",
                ),
            )
            runtime = json.loads(
                (
                    fixture / "references" / "capability-profiles.json"
                ).read_text(encoding="utf-8")
            )["runtime_identity"]
            self.assertEqual("aaron-marketing-runtime:19.0.0", runtime["ref"])

    def test_missing_canonical_skill_refuses_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            build_fixture(fixture)
            missing = fixture / canonical_skill_paths()[0]
            missing.unlink()
            before = (fixture / "references" / "system-catalog.json").read_bytes()
            result = self.run_bump(fixture, "--write")
            after = (fixture / "references" / "system-catalog.json").read_bytes()
        self.assertEqual(result.returncode, 2)
        self.assertIn("regular non-symlink file", result.stderr)
        self.assertEqual(before, after)

    def test_release_support_drift_refuses_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            fixture = Path(tmp)
            build_fixture(fixture)
            verifier = fixture / "scripts" / "verify-profile-outcomes.py"
            verifier.write_text(
                verifier.read_text(encoding="utf-8").replace(
                    '    "20.1.0",\n)',
                    ")",
                    1,
                ),
                encoding="utf-8",
            )
            before = (fixture / "references" / "system-catalog.json").read_bytes()
            result = self.run_bump(fixture, "--write")
            after = (fixture / "references" / "system-catalog.json").read_bytes()
        self.assertEqual(2, result.returncode)
        self.assertIn("release support is not aligned", result.stderr)
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
