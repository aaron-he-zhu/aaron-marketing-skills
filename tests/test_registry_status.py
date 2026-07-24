import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RegistryStatusTests(unittest.TestCase):
    def local_registry_versions(self):
        plugin = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        clawhub = {}
        skillhub = {}
        for declared in plugin["skills"]:
            relative = declared[2:] if declared.startswith("./") else declared
            lines = (ROOT / relative / "SKILL.md").read_text(
                encoding="utf-8"
            ).splitlines()
            name = Path(relative).name
            version = next(
                line.split(":", 1)[1].strip().strip("\"'")
                for line in lines if line.startswith("version:")
            )
            slug = next(
                line.split(":", 1)[1].strip()
                for line in lines if line.startswith("slug:")
            )
            clawhub[name] = version
            skillhub[slug] = version
        return plugin["version"], clawhub, skillhub

    def fake_environment(self, base, *, stale_skill=None, stale_package=False):
        bundle, clawhub_versions, skillhub_versions = self.local_registry_versions()
        fake_bin = base / "bin"
        fake_bin.mkdir(parents=True)
        versions_path = base / "versions.json"
        versions_path.write_text(json.dumps({
            "clawhub": clawhub_versions,
            "skillhub": skillhub_versions,
        }), encoding="utf-8")
        clawhub = fake_bin / "clawhub"
        clawhub.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
versions = json.loads(Path(os.environ["FAKE_REGISTRY_VERSIONS"]).read_text())
if args[:2] == ["package", "inspect"]:
    print(json.dumps({"package": {
        "latestVersion": os.environ["FAKE_PACKAGE_VERSION"],
    }}))
elif args and args[0] == "inspect":
    name = args[1].rsplit("/", 1)[-1]
    version = versions["clawhub"][name]
    if name == os.environ.get("FAKE_STALE_SKILL"):
        version = "0.0.1"
    print("Latest: %s" % version)
else:
    raise SystemExit(2)
""",
            encoding="utf-8",
        )
        clawhub.chmod(0o755)
        skillhub = fake_bin / "skillhub"
        skillhub.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
versions = json.loads(Path(os.environ["FAKE_REGISTRY_VERSIONS"]).read_text())
if args and args[0] == "search":
    slug = args[1]
    version = versions["skillhub"][slug]
    stale = os.environ.get("FAKE_STALE_SKILL", "")
    if stale and slug.endswith(stale):
        version = "0.0.1"
    print(json.dumps([{"slug": slug, "version": version}]))
else:
    raise SystemExit(2)
""",
            encoding="utf-8",
        )
        skillhub.chmod(0o755)
        environment = os.environ.copy()
        environment.update({
            "PATH": str(fake_bin) + os.pathsep + environment.get("PATH", ""),
            "FAKE_REGISTRY_VERSIONS": str(versions_path),
            "FAKE_PACKAGE_VERSION": "0.0.1" if stale_package else bundle,
            "FAKE_STALE_SKILL": stale_skill or "",
        })
        return environment

    def run_status(self, environment, *arguments):
        return subprocess.run(
            ["bash", "scripts/registry-status.sh", *arguments],
            cwd=ROOT, capture_output=True, text=True, env=environment,
        )

    def test_require_current_accepts_exact_canonical_120_and_current_package(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = self.fake_environment(Path(temporary))
            result = self.run_status(
                environment, "--json", "--require-current", "--workers", "16",
            )
            self.assertEqual(0, result.returncode, result.stderr)
            snapshot = json.loads(result.stdout)
            self.assertEqual("1.0", snapshot["schema_version"])
            self.assertEqual("aaron-he-zhu/aaron-marketing-skills", snapshot["repository"])
            self.assertRegex(snapshot["commit"], r"^[0-9a-f]{40}$")
            self.assertEqual(120, len(snapshot["skills"]))
            self.assertEqual(120, len({row["skill"] for row in snapshot["skills"]}))
            self.assertTrue(all(
                row["clawhub_ok"] and row["skillhub_ok"]
                for row in snapshot["skills"]
            ))
            self.assertTrue(snapshot["package"]["ok"])

    def test_require_current_rejects_registry_or_package_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            stale_registry = self.run_status(
                self.fake_environment(base / "registry", stale_skill="narrative-quality-auditor"),
                "--require-current", "--workers", "16",
            )
            self.assertNotEqual(0, stale_registry.returncode)
            self.assertIn("not current for platform scope both", stale_registry.stderr)

            stale_package = self.run_status(
                self.fake_environment(base / "package", stale_package=True),
                "--require-current", "--workers", "16",
            )
            self.assertNotEqual(0, stale_package.returncode)
            self.assertIn("not current for platform scope both", stale_package.stderr)

    def test_require_current_supports_selected_platform_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment = self.fake_environment(Path(temporary))
            for platform in ("clawhub", "skillhub"):
                with self.subTest(platform=platform):
                    result = self.run_status(
                        environment, "--require-current", "--platform", platform,
                        "--workers", "16",
                    )
                    self.assertEqual(0, result.returncode, result.stderr)


if __name__ == "__main__":
    unittest.main()
