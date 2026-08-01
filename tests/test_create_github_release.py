"""Owner-run immutable GitHub final-release orchestration tests."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RELEASER = ROOT / "scripts" / "create-github-release.py"
COMMIT = "a" * 40
OTHER_COMMIT = "d" * 40
VERSION = "19.1.0"
TAG = "v" + VERSION
ASSET_NAMES = (
    "aaron-marketing-skills-19.1.0-lite.tar.gz",
    "aaron-marketing-skills-19.1.0-pro.tar.gz",
    "aaron-marketing-skills-19.1.0-governed.tar.gz",
    "SHA256SUMS",
    "release-assets.json",
)
NOTES = (
    "### v19.1.0 — Progressive context disclosure (2026-08-01)\n\n"
    "Default Lite keeps the 4×4 and acronym symmetry contracts intact.\n"
)


FAKE_GIT = r"""#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
root = Path(os.environ["FAKE_ROOT"])
state_path = Path(os.environ["FAKE_STATE"])
state = json.loads(state_path.read_text(encoding="utf-8"))

def save():
    state_path.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")

def mutate(kind):
    with Path(os.environ["FAKE_MUTATIONS"]).open("a", encoding="utf-8") as handle:
        handle.write(kind + "\n")

if args == ["rev-parse", "--show-toplevel"]:
    print(root)
elif args == ["status", "--porcelain=v1", "--untracked-files=all"]:
    print(os.environ.get("FAKE_DIRTY", ""), end="")
elif args == ["config", "--get-all", "remote.origin.url"]:
    print("https://github.com/aaron-he-zhu/aaron-marketing-skills.git")
elif args == ["config", "--get-regexp", r"^url\..*\.insteadof$"]:
    raise SystemExit(1)
elif args == ["rev-parse", "--verify", "HEAD^{commit}"]:
    print(state["commit"])
elif args == ["rev-parse", "--verify", "refs/remotes/origin/main^{commit}"]:
    print(state["remote_main"])
elif args[:1] == ["show"] and len(args) == 2:
    relative = args[1].split(":", 1)[1]
    sys.stdout.write((root / relative).read_text(encoding="utf-8"))
elif args[:4] == ["fetch", "-q", "--", "https://github.com/aaron-he-zhu/aaron-marketing-skills.git"]:
    mutate("fetch")
elif args[:2] == ["merge-base", "--is-ancestor"]:
    raise SystemExit(0 if state.get("ancestor", True) else 1)
elif args[:2] == ["ls-remote", "--tags"]:
    target = state.get("remote_tag")
    if target:
        print("%s\trefs/tags/v19.1.0" % ("b" * 40))
        print("%s\trefs/tags/v19.1.0^{}" % target)
elif args == ["rev-parse", "-q", "--verify", "refs/tags/v19.1.0"]:
    target = state.get("local_tag")
    if not target:
        raise SystemExit(1)
    print("c" * 40)
elif args == ["cat-file", "-t", "refs/tags/v19.1.0"]:
    if not state.get("local_tag"):
        raise SystemExit(1)
    print("tag")
elif args == ["rev-parse", "--verify", "refs/tags/v19.1.0^{commit}"]:
    target = state.get("local_tag")
    if not target:
        raise SystemExit(1)
    print(target)
elif len(args) >= 8 and args[:4] == ["-c", "tag.gpgSign=false", "tag", "-a"]:
    state["local_tag"] = args[5]
    save()
    mutate("tag")
elif args[:3] == ["push", "--", "https://github.com/aaron-he-zhu/aaron-marketing-skills.git"]:
    target = state.get("local_tag")
    if not target:
        raise SystemExit(1)
    state["remote_tag"] = target
    save()
    mutate("push")
else:
    print("unsupported fake git call: %r" % args, file=sys.stderr)
    raise SystemExit(91)
"""


FAKE_GH = r"""#!/usr/bin/env python3
import json
import os
from pathlib import Path
import shutil
import sys

args = sys.argv[1:]
state_path = Path(os.environ["FAKE_STATE"])
state = json.loads(state_path.read_text(encoding="utf-8"))
remote_assets = Path(os.environ["FAKE_REMOTE_ASSETS"])

def save():
    state_path.write_text(json.dumps(state, sort_keys=True), encoding="utf-8")

def mutate(kind):
    with Path(os.environ["FAKE_MUTATIONS"]).open("a", encoding="utf-8") as handle:
        handle.write(kind + "\n")

if args[:3] == ["api", "--method", "GET"] and "release-validation.yml/runs" in args[3]:
    runs = []
    if state.get("ci_success"):
        runs.append({
            "head_sha": state["commit"],
            "conclusion": "success",
            "event": "workflow_dispatch",
            "actor": {"login": "aaron-he-zhu"},
        })
    print(json.dumps({"workflow_runs": runs}))
elif args[:3] == ["api", "--paginate", "--slurp"]:
    print(json.dumps([state.get("releases", [])]))
elif args[:3] == ["release", "create", "v19.1.0"]:
    notes_index = args.index("--notes-file")
    if args[notes_index + 1] != "-":
        raise SystemExit(93)
    title_index = args.index("--title")
    if args[title_index + 1] != "v19.1.0" or "--verify-tag" not in args:
        raise SystemExit(94)
    paths = [Path(value) for value in args[notes_index + 2:]]
    if {path.name for path in paths} != {
        "aaron-marketing-skills-19.1.0-lite.tar.gz",
        "aaron-marketing-skills-19.1.0-pro.tar.gz",
        "aaron-marketing-skills-19.1.0-governed.tar.gz",
        "SHA256SUMS",
        "release-assets.json",
    }:
        raise SystemExit(95)
    remote_assets.mkdir(parents=True, exist_ok=True)
    for path in paths:
        shutil.copy2(path, remote_assets / path.name)
    release = {
        "tag_name": "v19.1.0",
        "name": "v19.1.0",
        "draft": False,
        "prerelease": False,
        "body": sys.stdin.read(),
        "assets": [
            {"name": path.name, "state": "uploaded"} for path in paths
        ],
    }
    state["releases"] = [release]
    save()
    mutate("release")
elif args[:3] == ["release", "download", "v19.1.0"]:
    destination = Path(args[args.index("--dir") + 1])
    for source in remote_assets.iterdir():
        shutil.copy2(source, destination / source.name)
else:
    print("unsupported fake gh call: %r" % args, file=sys.stderr)
    raise SystemExit(92)
"""


FAKE_RECEIPT_VERIFIER = r"""#!/usr/bin/env python3
import hashlib
import os
from pathlib import Path
import sys

receipt = Path(sys.argv[1])
commit = sys.argv[sys.argv.index("--source-commit") + 1]
version = sys.argv[sys.argv.index("--release-version") + 1]
required_gate = sys.argv[sys.argv.index("--required-gate") + 1]
maturity_report = Path(sys.argv[sys.argv.index("--maturity-report") + 1])
evidence_root = Path(sys.argv[sys.argv.index("--evidence-root") + 1])
if "--post-release-continuation" in sys.argv:
    print("release creation must not use post-release continuation", file=sys.stderr)
    raise SystemExit(2)
if os.environ.get("FAKE_STALE_RECEIPT") == "1":
    print("engineering receipt is older than 24 hours", file=sys.stderr)
    raise SystemExit(3)
if (
    version != "19.1.0"
    or required_gate != "engineering-validation-v19"
    or not receipt.is_file()
    or not maturity_report.is_absolute()
    or not maturity_report.is_file()
    or not evidence_root.is_absolute()
    or not evidence_root.is_dir()
):
    raise SystemExit(1)
print("%s\t19.1.0-rc.1\t%s" % (hashlib.sha256(receipt.read_bytes()).hexdigest(), commit))
"""


FAKE_ASSET_VERIFIER = r"""#!/usr/bin/env python3
from pathlib import Path
import sys

directory = Path(sys.argv[sys.argv.index("--verify") + 1])
expected = {
    "aaron-marketing-skills-19.1.0-lite.tar.gz",
    "aaron-marketing-skills-19.1.0-pro.tar.gz",
    "aaron-marketing-skills-19.1.0-governed.tar.gz",
    "SHA256SUMS",
    "release-assets.json",
}
if {path.name for path in directory.iterdir()} != expected:
    raise SystemExit(1)
if sys.argv[sys.argv.index("--source-commit") + 1] != "a" * 40:
    raise SystemExit(1)
"""


class CreateGitHubReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.repository = self.base / "repository"
        self.repository.mkdir()
        (self.repository / "scripts").mkdir()
        shutil.copy2(RELEASER, self.repository / "scripts" / RELEASER.name)
        (self.repository / "scripts" / "verify-release-receipt.py").write_text(
            FAKE_RECEIPT_VERIFIER,
            encoding="utf-8",
        )
        (self.repository / "scripts" / "verify-profile-outcomes.py").write_text(
            "# verifier fixture\n",
            encoding="utf-8",
        )
        (self.repository / "scripts" / "build-release-assets.py").write_text(
            FAKE_ASSET_VERIFIER,
            encoding="utf-8",
        )
        (self.repository / ".claude-plugin").mkdir()
        (self.repository / ".claude-plugin" / "plugin.json").write_text(
            json.dumps({"version": VERSION}) + "\n",
            encoding="utf-8",
        )
        (self.repository / "VERSIONS.md").write_text(
            "# Versions\n\n"
            "**Current release**: `19.1.0` (2026-08-01). Current.\n\n"
            "## Changelog\n\n"
            + NOTES
            + "\n### v18.0.0 — Previous (2026-07-12)\n\nOld.\n",
            encoding="utf-8",
        )
        self.assets = self.base / "assets"
        self.assets.mkdir(mode=0o700)
        for index, name in enumerate(ASSET_NAMES):
            path = self.assets / name
            path.write_text("asset-%d\n" % index, encoding="utf-8")
            path.chmod(0o644)
        self.receipt = self.base / "private-receipt.json"
        self.receipt.write_text('{"private":true}\n', encoding="utf-8")
        self.receipt.chmod(0o600)
        self.maturity_report = self.base / "private-maturity-report.json"
        self.maturity_report.write_text('{"private":true}\n', encoding="utf-8")
        self.maturity_report.chmod(0o600)
        self.evidence_root = self.base / "private-evidence"
        self.evidence_root.mkdir(mode=0o700)
        self.remote_assets = self.base / "remote-assets"
        self.state_path = self.base / "state.json"
        self.mutations = self.base / "mutations.log"
        self.fake_bin = self.base / "bin"
        self.fake_bin.mkdir()
        for name, content in (("git", FAKE_GIT), ("gh", FAKE_GH)):
            path = self.fake_bin / name
            path.write_text(content, encoding="utf-8")
            path.chmod(0o755)
        self.state = {
            "commit": COMMIT,
            "remote_main": COMMIT,
            "ancestor": True,
            "ci_success": True,
            "local_tag": None,
            "remote_tag": None,
            "releases": [],
        }
        self.save_state()
        self.environment = os.environ.copy()
        self.environment.update(
            {
                "PATH": str(self.fake_bin) + os.pathsep + self.environment.get("PATH", ""),
                "FAKE_ROOT": str(self.repository),
                "FAKE_STATE": str(self.state_path),
                "FAKE_MUTATIONS": str(self.mutations),
                "FAKE_REMOTE_ASSETS": str(self.remote_assets),
            }
        )

    def tearDown(self):
        self.temporary.cleanup()

    def save_state(self):
        self.state_path.write_text(
            json.dumps(self.state, sort_keys=True),
            encoding="utf-8",
        )

    def read_state(self):
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def mutation_kinds(self):
        if not self.mutations.exists():
            return []
        return self.mutations.read_text(encoding="utf-8").splitlines()

    def run_release(self, *arguments):
        return subprocess.run(
            [
                sys.executable,
                str(self.repository / "scripts" / RELEASER.name),
                *arguments,
            ],
            cwd=self.repository,
            env=self.environment,
            capture_output=True,
            text=True,
        )

    def live_arguments(self):
        return (
            "--live",
            "--receipt",
            str(self.receipt),
            "--asset-dir",
            str(self.assets),
            "--maturity-report",
            str(self.maturity_report),
            "--evidence-root",
            str(self.evidence_root),
        )

    def install_existing_release(self):
        self.state["remote_tag"] = COMMIT
        self.state["releases"] = [
            {
                "tag_name": TAG,
                "name": TAG,
                "draft": False,
                "prerelease": False,
                "body": NOTES,
                "assets": [
                    {"name": name, "state": "uploaded"} for name in ASSET_NAMES
                ],
            }
        ]
        self.save_state()
        self.remote_assets.mkdir(parents=True, exist_ok=True)
        for name in ASSET_NAMES:
            shutil.copy2(self.assets / name, self.remote_assets / name)

    def test_dry_run_has_zero_mutations_and_no_network_calls(self):
        result = self.run_release()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertEqual([], self.mutation_kinds())

    def test_live_requires_receipt_and_asset_directory_before_mutation(self):
        result = self.run_release("--live")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires --receipt, --asset-dir", result.stderr)
        self.assertEqual([], self.mutation_kinds())

    def test_repository_root_evidence_path_is_accepted_and_forwarded(self):
        arguments = list(self.live_arguments())
        evidence_index = arguments.index("--evidence-root") + 1
        arguments[evidence_index] = str(self.repository)
        result = self.run_release(*arguments)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("GitHub final release verified", result.stdout)

    def test_ci_failure_refuses_tag_and_release(self):
        self.state["ci_success"] = False
        self.save_state()
        result = self.run_release(*self.live_arguments())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("no successful owner-run", result.stderr)
        self.assertEqual(["fetch"], self.mutation_kinds())

    def test_stale_receipt_is_not_relaxed_for_release_creation(self):
        self.environment["FAKE_STALE_RECEIPT"] = "1"
        result = self.run_release(*self.live_arguments())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("older than 24 hours", result.stderr)
        self.assertEqual(["fetch"], self.mutation_kinds())

    def test_existing_tag_on_another_commit_is_rejected(self):
        self.state["remote_tag"] = OTHER_COMMIT
        self.save_state()
        result = self.run_release(*self.live_arguments())
        self.assertNotEqual(0, result.returncode)
        self.assertIn("not %s" % COMMIT, result.stderr)
        self.assertEqual(["fetch"], self.mutation_kinds())

    def test_success_creates_annotated_tag_release_and_reverifies_download(self):
        result = self.run_release(*self.live_arguments())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("GitHub final release verified", result.stdout)
        self.assertEqual(["fetch", "tag", "push", "release"], self.mutation_kinds())
        state = self.read_state()
        self.assertEqual(COMMIT, state["remote_tag"])
        self.assertEqual(TAG, state["releases"][0]["tag_name"])
        self.assertEqual(NOTES.rstrip("\n"), state["releases"][0]["body"].rstrip("\n"))

    def test_same_commit_remote_tag_resumes_release_without_moving_tag(self):
        self.state["remote_tag"] = COMMIT
        self.save_state()
        result = self.run_release(*self.live_arguments())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(["fetch", "release"], self.mutation_kinds())

    def test_existing_release_is_read_only_and_idempotent(self):
        self.install_existing_release()
        result = self.run_release(*self.live_arguments())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("already verified (read-only)", result.stdout)
        self.assertEqual(["fetch"], self.mutation_kinds())


if __name__ == "__main__":
    unittest.main()
