import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build-distribution.py"
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class DistributionBuilderTests(unittest.TestCase):
    def build(self, *arguments):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output), *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return output

    def test_plugin_contains_runtime_and_excludes_maintenance(self):
        output = self.build("--plugin")
        plugin = json.loads((output / ".claude-plugin/plugin.json").read_text())
        self.assertEqual(120, len(plugin["skills"]))
        self.assertEqual(120, len(list(output.glob("*/*/*/SKILL.md"))) + len(list(output.glob("protocol/*/SKILL.md"))))
        for path in (
            "scripts/audit-loop.py",
            "scripts/rubric-score.py",
            "scripts/validate-audit-artifact.py",
            "scripts/registry-events.py",
            "scripts/run-events.py",
            "scripts/context-resolver.py",
            "references/context-request.schema.json",
            "references/context-manifest.schema.json",
            "references/context-resolution.md",
            "references/audit-loop-state.schema.json",
            "references/audit-loop-protocol.md",
            "references/auto-routing-scenarios.md",
            "references/run-event.schema.json",
            "references/turn-snapshot.schema.json",
            "references/save-point.schema.json",
            "references/run-envelope.schema.json",
            "references/runtime-protocol.md",
            "references/system-catalog.json",
            "references/scheduling.md",
            "commands/auto.md",
            "hooks/hooks.json",
        ):
            self.assertTrue((output / path).is_file(), path)
        for shard in (
            "narrative", "seo-geo", "social", "email", "ad", "influencer",
            "launch", "cross-discipline",
        ):
            self.assertTrue((output / "references" / "auto-routing" / (shard + ".md")).is_file(), shard)
        self.assertFalse((output / "evals/auto-routing-scenarios.source.md").exists())
        self.assertFalse((output / "scripts/generate-auto-routing-shards.py").exists())
        self.assertTrue((output / "scripts/connectors/resend.py").is_file())
        self.assertTrue((output / "references/skill-contract.md").is_file())
        for path in ("tests", "evals", ".github", ".githooks", "docs", "AGENTS.md", "CONTRIBUTING.md"):
            self.assertFalse((output / path).exists(), path)
        self.assertFalse(any(path.name == "__pycache__" for path in output.rglob("*")))
        self.assertFalse(any(path.suffix == ".pyc" for path in output.rglob("*")))
        self.assertFalse(any(path.name == "auditor-runtime.md" for path in output.rglob("*")))
        source_references = {path.relative_to(ROOT / "references") for path in (ROOT / "references").rglob("*") if path.is_file()}
        shipped_references = {path.relative_to(output / "references") for path in (output / "references").rglob("*") if path.is_file()}
        self.assertLess(len(shipped_references), len(source_references))

    def test_standalone_contains_only_one_skill_payload(self):
        output = self.build("--skill", "narrative/evaluate/narrative-quality-auditor")
        self.assertTrue((output / "SKILL.md").is_file())
        self.assertTrue((output / "references/auditor-runtime.md").is_file())
        self.assertFalse((output / "scripts").exists())
        self.assertFalse((output / ".claude-plugin").exists())

    def test_slim_frontmatter_strips_publishing_keys_only(self):
        output = self.build("--plugin", "--slim-frontmatter")
        skills = list(output.glob("*/*/*/SKILL.md")) + list(output.glob("protocol/*/SKILL.md"))
        self.assertEqual(120, len(skills))
        for skill in skills:
            frontmatter = skill.read_text(encoding="utf-8").split("---")[1]
            for stripped in ("slug:", "displayName:", "summary:"):
                self.assertNotIn(stripped, frontmatter, skill)
            for required in ("name:", "version:", "description:", "metadata:",
                             "license:", "compatibility:"):
                self.assertIn(required, frontmatter, skill)

    def test_slim_frontmatter_rejects_standalone(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        output = Path(temporary.name) / "distribution"
        result = subprocess.run(
            [sys.executable, str(BUILDER), "--output", str(output),
             "--skill", "narrative/evaluate/narrative-quality-auditor", "--slim-frontmatter"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--slim-frontmatter applies to --plugin builds only", result.stderr)

    def test_plugin_runtime_markdown_links_are_closed(self):
        output = self.build("--plugin")
        missing = []
        runtime_roots = [output / "commands", output / "references"]
        runtime_roots.extend(output / path.removeprefix("./") for path in json.loads(
            (output / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["skills"])
        sources = [(path, True) for path in output.glob("*.md") if path.is_file()]
        for runtime_root in runtime_roots:
            sources.extend((path, False) for path in runtime_root.rglob("*.md"))
        for source, runtime_only in sources:
            for raw in MARKDOWN_LINK.findall(source.read_text(encoding="utf-8")):
                target = raw.strip().lstrip("<").rstrip(">").split("#", 1)[0]
                if target == "url" or not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                    continue
                resolved = (source.parent / target).resolve()
                if runtime_only:
                    try:
                        relative = resolved.relative_to(output.resolve())
                    except ValueError:
                        continue
                    if not relative.parts or relative.parts[0] not in {"references", "scripts"}:
                        continue
                try:
                    resolved.relative_to(output.resolve())
                except ValueError:
                    missing.append("%s -> %s" % (source.relative_to(output), target))
                else:
                    if not resolved.exists():
                        missing.append("%s -> %s" % (source.relative_to(output), target))
        self.assertEqual([], missing)

    def test_unknown_skill_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run(
                [sys.executable, str(BUILDER), "--output", str(Path(temporary) / "out"), "--skill", "missing/skill"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown skill path", result.stderr)


if __name__ == "__main__":
    unittest.main()
