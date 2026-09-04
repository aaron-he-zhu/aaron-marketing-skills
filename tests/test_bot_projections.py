"""Regression coverage for the generated 8-bot roster projections."""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SMOKE_SPEC = importlib.util.spec_from_file_location(
    "smoke_bot_projections", ROOT / "scripts" / "smoke-bot-projections.py"
)
assert SMOKE_SPEC and SMOKE_SPEC.loader
smoke = importlib.util.module_from_spec(SMOKE_SPEC)
sys.modules[SMOKE_SPEC.name] = smoke
SMOKE_SPEC.loader.exec_module(smoke)
GENERATOR = ROOT / "scripts" / "generate-bot-projections.py"
CATALOG = ROOT / "references" / "system-catalog.json"
BOT_PREFIX = "aaron-"
CHIEF_BOT = "aaron-chief"
EXPECTED_BOTS = 8
EXPECTED_SKILLS = 120
MARKDOWN_LINK = re.compile(r"!?\[[^\]\n]*\]\((?P<destination>[^)\n]+)\)")
EXTERNAL_LINK = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
MENTION = re.compile(r"@(aaron-[a-z0-9-]+)")
FORBIDDEN_NAMES = {".env", "auth.json"}
FORBIDDEN_DIRS = {"memories", "sessions"}


class BotProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "roster"
        cls.build_result = subprocess.run(
            [sys.executable, str(GENERATOR), "--output", str(cls.output)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        cls.roster = json.loads(
            (cls.output / "bot-roster.json").read_text(encoding="utf-8")
        )
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def _bundle_dir(self, bot):
        return self.output / bot["hermes_bundle"]

    def test_cli_reports_roster_summary(self):
        self.assertIn("built bot-roster projection", self.build_result.stdout)
        self.assertIn("8 bots, 120 skills", self.build_result.stdout)
        self.assertEqual(
            self.roster["bundle_version"], self.catalog["bundle_version"]
        )

    def test_roster_covers_catalog_exactly_once(self):
        bots = self.roster["bots"]
        self.assertEqual(EXPECTED_BOTS, len(bots))
        owned = [name for bot in bots for name in bot["skills"]]
        self.assertEqual(EXPECTED_SKILLS, len(owned))
        self.assertEqual(EXPECTED_SKILLS, len(set(owned)))
        chief = [bot for bot in bots if bot["bot"] == CHIEF_BOT]
        self.assertEqual(1, len(chief))
        self.assertEqual(
            set(self.catalog["protocol"]["skills"]), set(chief[0]["skills"])
        )
        for bot in bots:
            if bot["bot"] == CHIEF_BOT:
                continue
            definition = self.catalog["disciplines"][bot["discipline"]]
            expected = [
                name
                for phase in definition["phase_order"]
                for name in definition["phases"][phase]
            ]
            self.assertEqual(expected, bot["skills"], bot["bot"])
            self.assertEqual(16, len(bot["skills"]), bot["bot"])

    def test_hermes_bundles_are_complete(self):
        for bot in self.roster["bots"]:
            bundle = self._bundle_dir(bot)
            for filename in (
                "distribution.yaml", "SOUL.md", "README.md", "PORTABILITY.md",
                "distribution-manifest.json",
            ):
                self.assertTrue((bundle / filename).is_file(), bundle / filename)
            yaml_text = (bundle / "distribution.yaml").read_text(encoding="utf-8")
            self.assertIn('name: "%s"' % bot["bot"], yaml_text)
            self.assertIn(
                'version: "%s"' % self.roster["bundle_version"], yaml_text
            )
            skill_dirs = sorted(
                entry.name for entry in (bundle / "skills").iterdir()
                if entry.is_dir()
            )
            self.assertEqual(sorted(bot["skills"]), skill_dirs, bot["bot"])
            for name in bot["skills"]:
                skill_file = bundle / "skills" / name / "SKILL.md"
                self.assertTrue(skill_file.is_file(), skill_file)
                content = skill_file.read_text(encoding="utf-8")
                self.assertIn("bot-roster static-skill boundary", content)
            self.assertTrue(
                (bundle / "references" / "policy-kernel.md").is_file(),
                "%s must bundle the policy kernel" % bot["bot"],
            )

    def test_soul_teaches_handoff_and_red_lines(self):
        for bot in self.roster["bots"]:
            soul = (self._bundle_dir(bot) / "SOUL.md").read_text(encoding="utf-8")
            self.assertIn("Red lines (non-reducible)", soul, bot["bot"])
            self.assertIn("NOT_SCORED", soul, bot["bot"])
            if bot["bot"] != CHIEF_BOT:
                self.assertIn("@" + CHIEF_BOT, soul, bot["bot"])
            else:
                for other in self.roster["bots"]:
                    if other["bot"] == CHIEF_BOT:
                        continue
                    self.assertIn("@" + other["bot"], soul, other["bot"])

    def test_mentions_and_command_surfaces_resolve(self):
        names = {bot["bot"] for bot in self.roster["bots"]}
        sources = [
            self._bundle_dir(bot) / "SOUL.md" for bot in self.roster["bots"]
        ] + [
            self.output / "grok" / "bot-cards.md",
            self.output / "grok" / "enable-lists.md",
            self.output / "grok" / "setup-checklist.md",
        ]
        for source in sources:
            text = source.read_text(encoding="utf-8")
            self.assertNotIn("/aaron-marketing:", text, source)
            for mention in MENTION.findall(text):
                self.assertIn(mention, names, "%s: @%s" % (source, mention))

    def test_markdown_links_are_contained(self):
        for bot in self.roster["bots"]:
            bundle = self._bundle_dir(bot)
            for markdown in sorted(bundle.rglob("*.md")):
                relative = markdown.relative_to(bundle).as_posix()
                text = markdown.read_text(encoding="utf-8")
                for match in MARKDOWN_LINK.finditer(text):
                    destination = match.group("destination").strip()
                    if destination.startswith("<"):
                        destination = destination[1:destination.find(">")]
                    destination = destination.split()[0] if destination else ""
                    path_text = destination.partition("#")[0]
                    if (
                        not path_text
                        or EXTERNAL_LINK.match(path_text)
                        or path_text.startswith("//")
                    ):
                        continue
                    self.assertFalse(
                        path_text.startswith("/"),
                        "%s links absolute path %s" % (relative, path_text),
                    )
                    resolved = posixpath.normpath(
                        posixpath.join(posixpath.dirname(relative), path_text)
                    )
                    self.assertFalse(
                        resolved.startswith(".."),
                        "%s escapes the bundle: %s" % (relative, path_text),
                    )
                    self.assertTrue(
                        (bundle / resolved).exists(),
                        "%s links missing target %s" % (relative, resolved),
                    )

    def test_no_secret_or_user_state_paths(self):
        for path in self.output.rglob("*"):
            self.assertNotIn(
                path.name, FORBIDDEN_NAMES, "forbidden file: %s" % path
            )
            if path.is_dir():
                self.assertNotIn(
                    path.name, FORBIDDEN_DIRS, "forbidden directory: %s" % path
                )

    def test_grok_artifacts_cover_roster(self):
        cards = (self.output / "grok" / "bot-cards.md").read_text(encoding="utf-8")
        enable = (self.output / "grok" / "enable-lists.md").read_text(
            encoding="utf-8"
        )
        checklist = (self.output / "grok" / "setup-checklist.md").read_text(
            encoding="utf-8"
        )
        for bot in self.roster["bots"]:
            self.assertIn("## @%s" % bot["bot"], cards)
            self.assertIn("## @%s (%d skills)" % (bot["bot"], len(bot["skills"])), enable)
            for name in bot["skills"]:
                self.assertIn(name, enable)
        self.assertIn("share one persistent", checklist)
        self.assertIn("NOT_SCORED", checklist)
        self.assertIn("written instructions", checklist)
        self.assertIn("macOS, Windows, and iOS", checklist)

    def test_manifests_bind_files(self):
        manifests = [
            self.output / "distribution-manifest.json",
            self.output / "grok" / "distribution-manifest.json",
        ] + [
            self._bundle_dir(bot) / "distribution-manifest.json"
            for bot in self.roster["bots"]
        ]
        for manifest_path in manifests:
            base = manifest_path.parent
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual("sha256", manifest["hash_algorithm"])
            listed = {item["path"]: item for item in manifest["files"]}
            actual = {
                path.relative_to(base).as_posix()
                for path in base.rglob("*")
                if path.is_file()
                and path.relative_to(base).as_posix() != "distribution-manifest.json"
            }
            self.assertEqual(actual, set(listed), manifest_path)
            for relative, item in listed.items():
                content = (base / relative).read_bytes()
                self.assertEqual(
                    hashlib.sha256(content).hexdigest(), item["sha256"],
                    "%s: %s" % (manifest_path, relative),
                )

    def test_host_profiles_are_roster_projection_only(self):
        catalog_path = ROOT / "references" / "bot-roster-profiles.json"
        raw = catalog_path.read_bytes()
        catalog = json.loads(raw.decode("utf-8"))
        self.assertEqual("bot-roster-profiles", catalog["kind"])
        self.assertEqual("excluded", catalog["context_assembly"])
        self.assertEqual(
            ["hermes-bot-host", "grok-bot-host"], catalog["profile_order"]
        )
        for name, definition in catalog["profiles"].items():
            self.assertEqual(
                "named-bot-roster", definition["routing_surface"], name
            )
            self.assertEqual(
                ["bot-roster"], definition["compatible_distributions"], name
            )
            self.assertEqual("propose-only", definition["persistence"], name)
            self.assertEqual(
                "not-scored-without-runtime", definition["audit_scoring"], name
            )
        host_catalog = json.loads(
            (ROOT / "references" / "host-capability-profiles.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            [
                "standalone-skill-host", "generic-shared-root-host",
                "claude-code-plugin-host",
            ],
            host_catalog["profile_order"],
            "roster profiles must not join the runtime host catalog",
        )
        self.assertNotIn("hermes-bot-host", host_catalog["profiles"])
        self.assertNotIn("grok-bot-host", host_catalog["profiles"])

        def definition_sha256(name):
            pinned = {"profile": name, **catalog["profiles"][name]}
            canonical = (
                json.dumps(
                    pinned, ensure_ascii=False, allow_nan=False, indent=2,
                    sort_keys=True,
                ) + "\n"
            ).encode("utf-8")
            return hashlib.sha256(canonical).hexdigest()

        catalog_sha256 = hashlib.sha256(raw).hexdigest()
        self.assertEqual(
            catalog_sha256, self.roster["host_profile_catalog_sha256"]
        )
        for bot in self.roster["bots"]:
            manifest = json.loads(
                (self._bundle_dir(bot) / "distribution-manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual("hermes-bot-host", manifest["host_profile"])
            self.assertEqual(
                catalog_sha256, manifest["host_profile_catalog_sha256"]
            )
            self.assertEqual(
                definition_sha256("hermes-bot-host"),
                manifest["host_profile_definition_sha256"],
            )
            self.assertEqual("named-bot-roster", manifest["routing_surface"])
        grok_manifest = json.loads(
            (self.output / "grok" / "distribution-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual("grok-bot-host", grok_manifest["host_profile"])
        self.assertEqual(
            catalog_sha256, grok_manifest["host_profile_catalog_sha256"]
        )
        self.assertEqual(
            definition_sha256("grok-bot-host"),
            grok_manifest["host_profile_definition_sha256"],
        )
        self.assertEqual("named-bot-roster", grok_manifest["routing_surface"])

    def test_output_inside_repository_is_refused(self):
        result = subprocess.run(
            [
                sys.executable, str(GENERATOR),
                "--output", str(ROOT / "tmp-bot-roster-refused"),
            ],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("outside the repository", result.stderr)
        self.assertFalse((ROOT / "tmp-bot-roster-refused").exists())

    def test_smoke_assertions_cover_generated_roster(self):
        smoke.assert_roster_complete(
            self.output, self.catalog, self.roster, self.build_result
        )


if __name__ == "__main__":
    unittest.main()
