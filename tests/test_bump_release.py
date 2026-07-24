"""Transactional release-bump tests against a copied canonical fixture."""
from __future__ import annotations

import json
from pathlib import Path
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
        "references/auditor-runbook.md",
        "docs/registry-submissions.md",
        "scripts/publish-skillhub.sh",
        "scripts/bump-release.py",
    ] + canonical_skill_paths()
    for relative in files:
        source = ROOT / relative
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


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
        self.assertGreaterEqual(payload["changed_file_count"], 128)
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
            self.assertIn("### v99.0.0 — Runtime and distribution", versions)
            self.assertIn("### v18.0.0 — Seven-discipline", versions)
            for relative in canonical_skill_paths():
                text = (fixture / relative).read_text(encoding="utf-8")
                self.assertIn('version: "99.0.0"', text)
                metadata = next(
                    line.removeprefix("metadata: ")
                    for line in text.splitlines()
                    if line.startswith("metadata: ")
                )
                self.assertEqual(json.loads(metadata)["version"], "99.0.0")

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


if __name__ == "__main__":
    unittest.main()
