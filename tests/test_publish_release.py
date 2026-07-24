import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "scripts" / "publish-common.sh"


class PublishReleaseTests(unittest.TestCase):
    def git(self, repository, *arguments, check=True):
        return subprocess.run(
            ["git", *arguments], cwd=repository, check=check,
            capture_output=True, text=True,
        )

    def make_pushed_repository(self, base):
        remote = base / "remote.git"
        repository = base / "repository"
        self.git(base, "init", "--bare", str(remote))
        repository.mkdir()
        self.git(repository, "init")
        self.git(repository, "checkout", "-b", "main")
        self.git(repository, "config", "user.name", "Release Test")
        self.git(repository, "config", "user.email", "release-test" + "@" + "example.invalid")
        (repository / "payload.txt").write_text("pushed\n", encoding="utf-8")
        (repository / "scripts").mkdir()
        (repository / "scripts" / "build-distribution.py").write_text(
            "# pinned builder fixture\n", encoding="utf-8",
        )
        self.git(repository, "add", "payload.txt", "scripts/build-distribution.py")
        self.git(repository, "commit", "-m", "initial")
        self.git(repository, "remote", "add", "origin", str(remote))
        self.git(repository, "push", "-u", "origin", "main")
        return repository

    def run_helper(self, repository, function, *arguments, environment=None):
        command = 'source "$1"; shift; %s "$@"' % function
        return subprocess.run(
            ["bash", "-c", command, "publish-test", str(COMMON), *map(str, arguments)],
            cwd=repository, capture_output=True, text=True, env=environment,
        )

    def fake_release_environment(self, base, *, status="", fetch_failure=False,
                                 ancestor_failure=False):
        fake_bin = base / "bin"
        fake_bin.mkdir(parents=True)
        fake_git = fake_bin / "git"
        fake_git.write_text(
            """#!/usr/bin/env python3
import os
from pathlib import Path
import sys

args = sys.argv[1:]
commit = os.environ["FAKE_GIT_COMMIT"]
if args == ["config", "--get-all", "remote.origin.url"]:
    counter_path = Path(os.environ["FAKE_GIT_REMOTE_COUNTER"])
    try:
        count = int(counter_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        count = 0
    counter_path.write_text(str(count + 1), encoding="utf-8")
    switch_after = int(os.environ.get("FAKE_GIT_REMOTE_SWITCH_AFTER", "999999"))
    if count >= switch_after:
        print(os.environ.get("FAKE_GIT_REMOTE_AFTER", os.environ["FAKE_GIT_REMOTE"]))
    else:
        print(os.environ["FAKE_GIT_REMOTE"])
elif args == ["config", "--get-regexp", "^url\\\\..*\\\\.insteadof$"]:
    rewrite = os.environ.get("FAKE_GIT_REWRITES", "")
    if rewrite:
        print(rewrite)
    else:
        raise SystemExit(1)
elif args == ["rev-parse", "--is-inside-work-tree"]:
    print("true")
elif args == ["status", "--porcelain=v1", "--untracked-files=all"]:
    print(os.environ.get("FAKE_GIT_STATUS", ""), end="")
elif args == ["rev-parse", "--verify", "HEAD^{commit}"]:
    print(commit)
elif args == ["rev-parse", "--verify", "refs/remotes/origin/main^{commit}"]:
    print(os.environ.get("FAKE_GIT_REMOTE_COMMIT", commit))
elif args[:3] == ["fetch", "-q", "--"]:
    raise SystemExit(1 if os.environ.get("FAKE_GIT_FETCH_FAILURE") == "1" else 0)
elif args[:2] == ["merge-base", "--is-ancestor"]:
    if os.environ.get("FAKE_GIT_ANCESTOR_FAILURE") == "1":
        raise SystemExit(1)
    mutation = os.environ.get("FAKE_GATE_MUTATION_KIND", "")
    root = Path(os.environ["FAKE_REPOSITORY_ROOT"])
    if mutation == "about":
        import json
        (root / ".github/repo-about.json").write_text(json.dumps({
            "description": "EVIL WORKTREE DESCRIPTION",
            "topics": ["evil-worktree-topic"],
        }), encoding="utf-8")
        (root / ".about-race-fired").write_text("fired\\n", encoding="utf-8")
    elif mutation == "family":
        import json
        plugin_path = root / ".claude-plugin/plugin.json"
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        plugin["version"] = "9.9.9"
        plugin["skills"] = [
            path.replace("pinned-", "evil-worktree-") for path in plugin["skills"]
        ]
        plugin_path.write_text(json.dumps(plugin), encoding="utf-8")
        for source in (root / "references").glob("*.md"):
            source.write_text("EVIL WORKTREE BODY **Z9**\\n", encoding="utf-8")
        (root / ".family-race-fired").write_text("fired\\n", encoding="utf-8")
    raise SystemExit(0)
elif len(args) == 3 and args[:2] == ["cat-file", "-e"] and args[2].endswith("^{commit}"):
    raise SystemExit(0)
elif args and args[0] == "archive":
    if os.environ.get("FAKE_GIT_ARCHIVE_FAILURE") == "1":
        raise SystemExit(1)
    import tarfile
    output_arg = next((item for item in args if item.startswith("--output=")), None)
    if output_arg is None:
        raise SystemExit(92)
    output = Path(output_arg.split("=", 1)[1])
    root = Path(os.environ.get("FAKE_PINNED_ROOT", os.environ["FAKE_REPOSITORY_ROOT"]))
    with tarfile.open(output, "w") as archive:
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                continue
            archive.add(path, arcname=str(path.relative_to(root)), recursive=False)
elif args[:4] == ["clone", "--quiet", "--depth", "1"]:
    clone = Path(args[5])
    clone.mkdir(parents=True)
    (clone / "README.md").write_text(
        "fixture header\\n<!-- SYNC:BEGIN -->\\nstale\\n<!-- SYNC:END -->\\nfixture footer\\n",
        encoding="utf-8",
    )
elif len(args) >= 4 and args[0] == "-C" and args[2] == "commit":
    raise SystemExit(0)
elif len(args) >= 4 and args[0] == "-C" and args[2] == "push":
    clone = Path(args[1])
    push_root = Path(os.environ["FAKE_PUSH_ROOT"])
    push_root.mkdir(parents=True, exist_ok=True)
    (push_root / (clone.name.removeprefix("clone-") + ".README.md")).write_bytes(
        (clone / "README.md").read_bytes()
    )
elif len(args) == 2 and args[0] == "show":
    root = Path(os.environ.get("FAKE_GIT_SHOW_ROOT", os.environ["FAKE_REPOSITORY_ROOT"]))
    reference = args[1].split(":", 1)[1]
    sys.stdout.buffer.write((root / reference).read_bytes())
else:
    print("unsupported fake git call: %r" % args, file=sys.stderr)
    raise SystemExit(91)
""",
            encoding="utf-8",
        )
        fake_git.chmod(0o755)
        for name in ("clawhub", "skillhub", "gh", "curl"):
            executable = fake_bin / name
            executable.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$0 $*\" >> \"$FAKE_MUTATION_LOG\"\nexit 0\n",
                encoding="utf-8",
            )
            executable.chmod(0o755)
        environment = os.environ.copy()
        environment.update({
            "PATH": str(fake_bin) + os.pathsep + environment.get("PATH", ""),
            "FAKE_GIT_COMMIT": "a" * 40,
            "FAKE_GIT_REMOTE_COMMIT": "b" * 40,
            "FAKE_GIT_REMOTE": "https://github.com/aaron-he-zhu/aaron-marketing-skills.git",
            "FAKE_GIT_REMOTE_AFTER": "https://github.com/other-owner/other-repository.git",
            "FAKE_GIT_REMOTE_SWITCH_AFTER": "999999",
            "FAKE_GIT_REMOTE_COUNTER": str(base / "origin-read-count.txt"),
            "FAKE_GIT_STATUS": status,
            "FAKE_GIT_FETCH_FAILURE": "1" if fetch_failure else "0",
            "FAKE_GIT_ANCESTOR_FAILURE": "1" if ancestor_failure else "0",
            "FAKE_GIT_ARCHIVE_FAILURE": "0",
            "FAKE_GATE_MUTATION_KIND": "",
            "FAKE_GIT_REWRITES": "",
            "FAKE_REPOSITORY_ROOT": str(ROOT),
            "FAKE_PINNED_ROOT": str(ROOT),
            "FAKE_PUSH_ROOT": str(base / "pushes"),
            "FAKE_MUTATION_LOG": str(base / "mutations.log"),
        })
        release_version = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        if int(release_version.split(".", 1)[0]) >= 19:
            receipt_path = base / "private-release-receipt.json"
            receipt = {
                "schema_version": "1.0",
                "gate": "profile-outcomes-v19",
                "passed": True,
                "release_version": release_version,
                "release_candidate": release_version + "-rc.1",
                "source_commit": "a" * 40,
                "evidence_sha256": "c" * 64,
                "evidence_manifest_sha256": "d" * 64,
                "verifier_sha256": hashlib.sha256(
                    (ROOT / "scripts/verify-profile-outcomes.py").read_bytes()
                ).hexdigest(),
                "model_identity": {
                    "provider": "fixture",
                    "model": "fixture-model",
                    "version": "1",
                    "toolset_sha256": "e" * 64,
                },
                "attestation": {
                    "method": "owner-attested-private-evidence",
                    "collector_id_hash": "f" * 64,
                    "signed_at": "2026-07-24T00:00:00Z",
                },
                "outcome_summary": {
                    "schema_version": "1.0",
                    "release_candidate": release_version + "-rc.1",
                    "source_commit": "a" * 40,
                    "counts": {"pilot": 14, "paired": 70, "shadow": 28},
                    "lite_completion_rate": 1.0,
                    "paired_quality_ci95_lower": 0.0,
                    "efficiency_improvements": {
                        key: {"median": 0.3, "ci95_lower": 0.3}
                        for key in ("time", "tokens", "turns_confirmations")
                    },
                    "lite_escalation_rate": 0.1,
                    "governed_trace_rate": 1.0,
                    "lite_trace_rate": 0.0,
                    "governed_recovery_rate": 1.0,
                    "lite_recovery_rate": 0.0,
                    "governed_median_time_ratio": 1.5,
                    "governed_median_token_ratio": 1.5,
                    "safety_failure_count": 0,
                    "passed": True,
                    "errors": [],
                },
            }
            receipt_path.write_text(
                json.dumps(receipt, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            os.chmod(receipt_path, 0o600)
            receipt_sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            gate_token = hashlib.sha256(
                "\0".join(
                    (
                        "aaron-he-zhu/aaron-marketing-skills",
                        "a" * 40,
                        release_version,
                        receipt_sha,
                    )
                ).encode("utf-8")
            ).hexdigest()
            environment.update(
                {
                    "AARON_RELEASE_RECEIPT": str(receipt_path),
                    "AARON_PUBLISH_EXPECTED_REPO": (
                        "aaron-he-zhu/aaron-marketing-skills"
                    ),
                    "AARON_PUBLISH_EXPECTED_COMMIT": "a" * 40,
                    "AARON_PUBLISH_PARENT_FINAL_GATE_TOKEN": gate_token,
                }
            )
        return environment, base / "mutations.log"

    def make_sync_fixture(self, base):
        repository = base / "repository"
        (repository / "scripts").mkdir(parents=True)
        for name in ("publish-common.sh", "sync-about.sh", "sync-family.sh"):
            shutil.copy2(ROOT / "scripts" / name, repository / "scripts" / name)
        (repository / "scripts" / "build-distribution.py").write_text(
            "# pinned export fixture\n", encoding="utf-8",
        )
        (repository / ".github").mkdir()
        (repository / ".github" / "repo-about.json").write_text(json.dumps({
            "description": "PINNED ABOUT DESCRIPTION",
            "topics": ["pinned-topic", "release-snapshot"],
        }), encoding="utf-8")
        (repository / ".claude-plugin").mkdir()
        disciplines = (
            "ad", "email", "seo-geo", "influencer", "launch", "social", "narrative",
        )
        (repository / ".claude-plugin" / "plugin.json").write_text(json.dumps({
            "version": "1.2.3",
            "skills": [
                "./%s/phase/pinned-%s-skill" % (discipline, discipline)
                for discipline in disciplines
            ],
        }), encoding="utf-8")
        references = repository / "references"
        references.mkdir()
        bodies = {
            "roas-benchmark.md": "PINNED ROAS BODY **R1**\n",
            "send-benchmark.md": "PINNED SEND BODY **S1**\n",
            "ramp-benchmark.md": "PINNED RAMP BODY **R1**\n",
            "echo-benchmark.md": "PINNED ECHO BODY **E1**\n",
            "tale-benchmark.md": "PINNED TALE BODY **T1**\n",
            "core-eeat-benchmark.md": "PINNED CORE BODY **T1**\n",
            "cite-domain-rating.md": "PINNED CITE BODY **T1**\n",
            "star-benchmark.md": "PINNED STAR BODY **S1**\n",
        }
        for name, body in bodies.items():
            (references / name).write_text(body, encoding="utf-8")
        pinned = base / "pinned"
        shutil.copytree(repository, pinned)
        return repository, pinned

    def canonical_registry_snapshot(
            self, *, commit="a" * 40, repository="aaron-he-zhu/aaron-marketing-skills",
            clawhub_behind=None, skillhub_behind=None, package_current=True,
            use_worktree=False):
        if use_worktree:
            plugin = json.loads(
                (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
            )
        else:
            plugin = json.loads(self.git(
                ROOT, "show", "HEAD:.claude-plugin/plugin.json"
            ).stdout)
        version = plugin["version"]
        rows = []
        for declared in plugin["skills"]:
            relative = declared[2:] if declared.startswith("./") else declared
            if use_worktree:
                skill_text = (ROOT / relative / "SKILL.md").read_text(
                    encoding="utf-8"
                )
            else:
                skill_text = self.git(
                    ROOT, "show", "HEAD:%s/SKILL.md" % relative
                ).stdout
            slug = next(
                line.split(":", 1)[1].strip()
                for line in skill_text.splitlines()
                if line.startswith("slug:")
            )
            skill_version = next(
                line.split(":", 1)[1].strip().strip("\"'")
                for line in skill_text.splitlines()
                if line.startswith("version:")
            )
            name = Path(relative).name
            clawhub = "0.0.1" if name == clawhub_behind else skill_version
            skillhub = "0.0.1" if name == skillhub_behind else skill_version
            rows.append({
                "skill": name,
                "slug": slug,
                "repo": skill_version,
                "clawhub": clawhub,
                "skillhub": skillhub,
                "clawhub_ok": clawhub == skill_version,
                "skillhub_ok": skillhub == skill_version,
            })
        package_version = version if package_current else "0.0.1"
        return {
            "schema_version": "1.0",
            "repository": repository,
            "commit": commit,
            "bundle": version,
            "platform": "both",
            "package": {
                "name": "aaron-marketing",
                "clawhub": package_version,
                "ok": package_version == version,
            },
            "skills": rows,
        }

    def make_committed_registry_identity(self, base):
        destination = base / "committed-registry-identity"
        plugin_path = destination / ".claude-plugin/plugin.json"
        catalog_path = destination / "references/system-catalog.json"
        plugin_path.parent.mkdir(parents=True)
        catalog_path.parent.mkdir(parents=True)
        plugin_path.write_text(
            self.git(ROOT, "show", "HEAD:.claude-plugin/plugin.json").stdout,
            encoding="utf-8",
        )
        catalog_path.write_text(
            self.git(ROOT, "show", "HEAD:references/system-catalog.json").stdout,
            encoding="utf-8",
        )
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
        for declared in plugin["skills"]:
            relative = declared[2:] if declared.startswith("./") else declared
            skill_path = destination / relative / "SKILL.md"
            skill_path.parent.mkdir(parents=True)
            skill_path.write_text(
                self.git(ROOT, "show", "HEAD:%s/SKILL.md" % relative).stdout,
                encoding="utf-8",
            )
        return destination

    def make_minimal_package_build_fixture(self, base):
        destination = base / "minimal-package-source"
        scripts = destination / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "build-distribution.py").write_text(
            """#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--plugin", action="store_true")
parser.add_argument("--profile")
parser.add_argument("--output")
parser.add_argument("--verify-manifest")
parser.add_argument("--source-repository")
parser.add_argument("--source-commit")
args = parser.parse_args()
if args.verify_manifest:
    raise SystemExit(0)
output = Path(args.output)
output.mkdir(parents=True)
(output / "distribution-manifest.json").write_text(json.dumps({
    "profile": "governed",
    "source": {
        "repository": args.source_repository,
        "commit": args.source_commit,
    },
    "files_sha256": "d" * 64,
}), encoding="utf-8")
""",
            encoding="utf-8",
        )
        return destination

    def install_transport_error_clawhub(self, environment, *, mode="matching"):
        fake_bin = Path(environment["PATH"].split(os.pathsep)[0])
        executable = fake_bin / "clawhub"
        executable.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
state = Path(os.environ["FAKE_PACKAGE_REMOTE_STATE"])
mode = os.environ["FAKE_PACKAGE_REMOTE_MODE"]
if args[:2] == ["package", "publish"]:
    manifest = json.loads(
        (Path(args[2]) / "distribution-manifest.json").read_text(encoding="utf-8")
    )
    state.write_text(json.dumps(manifest), encoding="utf-8")
    raise SystemExit(55)
if args[:2] == ["package", "inspect"]:
    if mode == "unsupported":
        raise SystemExit(2)
    manifest = json.loads(state.read_text(encoding="utf-8"))
    repository = manifest["source"]["repository"]
    commit = manifest["source"]["commit"]
    if mode == "source-mismatch":
        commit = "f" * 40
    if mode == "digest-mismatch":
        manifest["files_sha256"] = "e" * 64
    print(json.dumps({
        "package": {"name": "aaron-marketing"},
        "version": {
            "version": os.environ["FAKE_PACKAGE_VERSION"],
            "verification": {
                "sourceRepo": repository,
                "sourceCommit": commit,
            },
        },
        "versions": None,
        "file": {
            "path": "distribution-manifest.json",
            "content": json.dumps(manifest),
        },
    }))
    raise SystemExit(0)
raise SystemExit(0)
""",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        environment.update({
            "FAKE_PACKAGE_REMOTE_MODE": mode,
            "FAKE_PACKAGE_REMOTE_STATE": str(fake_bin / "remote-package.json"),
            "FAKE_PACKAGE_VERSION": json.loads(
                (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
            )["version"],
        })

    def test_live_provenance_accepts_clean_pushed_head(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, _ = self.fake_release_environment(Path(temporary))
            result = self.run_helper(
                ROOT, "publish_require_release_provenance", environment=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("a" * 40, result.stdout.strip())

    def test_live_provenance_rejects_dirty_or_untracked_tree(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_pushed_repository(Path(temporary))
            (repository / "payload.txt").write_text("dirty\n", encoding="utf-8")
            result = self.run_helper(repository, "publish_require_release_provenance")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("working tree is dirty", result.stderr)

            self.git(repository, "checkout", "--", "payload.txt")
            (repository / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            result = self.run_helper(repository, "publish_require_release_provenance")
            self.assertNotEqual(0, result.returncode)
            self.assertIn("working tree is dirty", result.stderr)

    def test_live_provenance_rejects_clean_unpushed_head(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, _ = self.fake_release_environment(
                Path(temporary), ancestor_failure=True,
            )
            result = self.run_helper(
                ROOT, "publish_require_release_provenance", environment=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("not reachable from origin/main", result.stderr)

    def test_live_provenance_fails_closed_when_origin_cannot_be_refreshed(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, _ = self.fake_release_environment(
                Path(temporary), fetch_failure=True,
            )
            result = self.run_helper(
                ROOT, "publish_require_release_provenance", environment=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("cannot refresh origin/main", result.stderr)

    def test_repository_slug_parser_accepts_common_git_urls_and_rejects_local_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            repository = self.make_pushed_repository(Path(temporary))
            for remote in (
                    "https://github.com/owner/repository.git",
                    "https://github.com/owner/repository",
                    "git" + "@" + "github.com:owner/repository.git",
                    "ssh://git" + "@" + "github.com/owner/repository.git"):
                with self.subTest(remote=remote):
                    self.git(repository, "remote", "set-url", "origin", remote)
                    result = self.run_helper(repository, "publish_repo_slug")
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertEqual("owner/repository", result.stdout.strip())
            for remote in (
                    str(Path(temporary) / "remote.git"),
                    "https://github.com.evil.invalid/owner/repository.git",
                    "https://github.com" + "@" + "evil.invalid/owner/repository.git",
                    "ssh://git" + "@" + "github.com.evil.invalid/owner/repository.git",
                    "git" + "@" + "github.com.evil.invalid:owner/repository.git",
                    "http://github.com/owner/repository.git"):
                with self.subTest(remote=remote):
                    self.git(repository, "remote", "set-url", "origin", remote)
                    result = self.run_helper(repository, "publish_repo_slug")
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("canonical github.com", result.stderr)

    def test_live_provenance_rejects_git_url_rewrites(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, mutation_log = self.fake_release_environment(Path(temporary))
            environment["FAKE_GIT_REWRITES"] = (
                "url.https://evil.invalid/.insteadof https://github.com/"
            )
            result = self.run_helper(
                ROOT, "publish_require_release_provenance", environment=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("URL rewrite rules are not allowed", result.stderr)
            self.assertFalse(mutation_log.exists())

    def test_release_identity_rejects_origin_switch_inside_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment, mutation_log = self.fake_release_environment(base)
            # First read resolves repo A; the post-fetch identity check sees B.
            environment["FAKE_GIT_REMOTE_SWITCH_AFTER"] = "1"
            result = self.run_helper(
                ROOT, "publish_require_release_identity", environment=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("changed during the release gate", result.stderr)
            self.assertFalse(mutation_log.exists())

    def test_pinned_source_is_exported_from_commit_not_worktree(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository = self.make_pushed_repository(base)
            commit = self.git(repository, "rev-parse", "HEAD").stdout.strip()
            (repository / "payload.txt").write_text("changed after guard\n", encoding="utf-8")
            exported = base / "exported"
            result = self.run_helper(
                repository, "publish_prepare_pinned_source", exported, commit,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual("pushed\n", (exported / "payload.txt").read_text(encoding="utf-8"))

    def test_sync_about_live_uses_pinned_ssot_after_gate_race(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, pinned = self.make_sync_fixture(base)
            environment, mutation_log = self.fake_release_environment(base / "fake")
            environment.update({
                "FAKE_PINNED_ROOT": str(pinned),
                "FAKE_REPOSITORY_ROOT": str(repository),
                "FAKE_WORKTREE": str(repository),
                "FAKE_GATE_MUTATION_KIND": "about",
            })
            fake_gh = Path(environment["PATH"].split(os.pathsep)[0]) / "gh"
            fake_gh.write_text(
                """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

args = sys.argv[1:]
worktree = Path(os.environ["FAKE_WORKTREE"])
marker = worktree / ".about-race-fired"
if not marker.exists():
    (worktree / ".github/repo-about.json").write_text(json.dumps({
        "description": "EVIL WORKTREE DESCRIPTION",
        "topics": ["evil-worktree-topic"],
    }), encoding="utf-8")
    marker.write_text("fired\\n", encoding="utf-8")
stdin = sys.stdin.read()
with open(os.environ["FAKE_MUTATION_LOG"], "a", encoding="utf-8") as stream:
    stream.write(json.dumps({"args": args, "stdin": stdin}, sort_keys=True) + "\\n")
if "--jq" in args and args[-1] == ".description":
    print("OLD REMOTE DESCRIPTION")
elif "--jq" in args and args[-1] == ".topics[]":
    print("old-remote-topic")
""",
                encoding="utf-8",
            )
            fake_gh.chmod(0o755)
            result = subprocess.run(
                ["bash", "scripts/sync-about.sh", "--live"], cwd=repository,
                capture_output=True, text=True, env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            calls = mutation_log.read_text(encoding="utf-8")
            self.assertIn("PINNED ABOUT DESCRIPTION", calls)
            self.assertIn("pinned-topic", calls)
            self.assertIn("release-snapshot", calls)
            self.assertNotIn("EVIL WORKTREE", calls)
            self.assertNotIn("evil-worktree-topic", calls)
            self.assertIn("pinned commit export", result.stdout)
            self.assertTrue((repository / ".about-race-fired").is_file())

    def test_sync_family_live_uses_pinned_plugin_and_references_after_gate_race(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            repository, pinned = self.make_sync_fixture(base)
            environment, _ = self.fake_release_environment(base / "fake")
            environment.update({
                "FAKE_PINNED_ROOT": str(pinned),
                "FAKE_REPOSITORY_ROOT": str(repository),
                "FAKE_WORKTREE": str(repository),
                "FAKE_GATE_MUTATION_KIND": "family",
                "GITHUB_TOKEN": "fixture-token",
            })
            fake_curl = Path(environment["PATH"].split(os.pathsep)[0]) / "curl"
            fake_curl.write_text(
                """#!/usr/bin/env python3
import json
import os
from pathlib import Path

worktree = Path(os.environ["FAKE_WORKTREE"])
marker = worktree / ".family-race-fired"
if not marker.exists():
    plugin = json.loads((worktree / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    plugin["version"] = "9.9.9"
    plugin["skills"] = [path.replace("pinned-", "evil-worktree-") for path in plugin["skills"]]
    (worktree / ".claude-plugin/plugin.json").write_text(json.dumps(plugin), encoding="utf-8")
    for source in (worktree / "references").glob("*.md"):
        source.write_text("EVIL WORKTREE BODY **Z9**\\n", encoding="utf-8")
    marker.write_text("fired\\n", encoding="utf-8")
print("fixture header")
print("<!-- SYNC:BEGIN -->")
print("stale remote body")
print("<!-- SYNC:END -->")
print("fixture footer **T1** **S1**")
""",
                encoding="utf-8",
            )
            fake_curl.chmod(0o755)
            result = subprocess.run(
                ["bash", "scripts/sync-family.sh", "--live"], cwd=repository,
                capture_output=True, text=True, env=environment,
            )
            self.assertEqual(1, result.returncode, result.stderr)
            pushes = Path(environment["FAKE_PUSH_ROOT"])
            roas = (pushes / "paid-ads-roas-benchmark.README.md").read_text(encoding="utf-8")
            ad_list = (pushes / "paid-ads-agent-skills.README.md").read_text(encoding="utf-8")
            self.assertIn("PINNED ROAS BODY", roas)
            self.assertNotIn("EVIL WORKTREE BODY", roas)
            self.assertIn("umbrella=v1.2.3", roas)
            self.assertIn("pinned-ad-skill", ad_list)
            self.assertNotIn("evil-worktree-ad-skill", ad_list)
            self.assertNotIn("umbrella=v9.9.9", ad_list)
            self.assertIn("pinned commit export", result.stdout)
            self.assertTrue((repository / ".family-race-fired").is_file())

    def test_direct_publishers_keep_dry_run_independent_of_git_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            fake_bin = Path(temporary) / "bin"
            fake_bin.mkdir()
            for name in ("clawhub", "skillhub"):
                executable = fake_bin / name
                executable.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
                executable.chmod(0o755)
            environment = os.environ.copy()
            environment["PATH"] = str(fake_bin) + os.pathsep + environment.get("PATH", "")
            environment["GIT_DIR"] = str(Path(temporary) / "missing-git-dir")
            commands = (
                ["bash", "scripts/publish-clawhub.sh", "--dry-run", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-skillhub.sh", "--dry-run", "--skill", "narrative-quality-auditor"],
            )
            for command in commands:
                with self.subTest(script=command[1]):
                    result = subprocess.run(
                        command, cwd=ROOT, capture_output=True, text=True, env=environment,
                    )
                    self.assertEqual(0, result.returncode, result.stderr)
                    self.assertIn("dry-run", result.stdout)

    def test_every_release_live_entrypoint_rejects_dirty_source_before_mutation(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment, mutation_log = self.fake_release_environment(
                base, status="?? uncommitted-release-input\n",
            )
            status_snapshot = base / "registry-status.json"
            status_snapshot.write_text('{"skills": []}\n', encoding="utf-8")
            commands = (
                ["bash", "scripts/publish-clawhub.sh", "--i-accept-mit0", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-skillhub.sh", "--live", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-package.sh", "--live"],
                ["bash", "scripts/publish-registries.sh", "--live", "--from-json", str(status_snapshot)],
                ["bash", "scripts/sync-about.sh", "--live"],
                ["bash", "scripts/sync-family.sh", "--live"],
            )
            for command in commands:
                with self.subTest(script=command[1]):
                    result = subprocess.run(
                        command, cwd=ROOT, capture_output=True, text=True, env=environment,
                    )
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("working tree is dirty", result.stderr)
            self.assertFalse(mutation_log.exists(), "a live tool ran before provenance passed")

    def test_every_release_live_entrypoint_rejects_github_host_spoofing(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            status_snapshot = base / "registry-status.json"
            status_snapshot.write_text('{"skills": []}\n', encoding="utf-8")
            commands = (
                ["bash", "scripts/publish-clawhub.sh", "--i-accept-mit0", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-skillhub.sh", "--live", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-package.sh", "--live"],
                ["bash", "scripts/publish-registries.sh", "--live", "--from-json", str(status_snapshot)],
                ["bash", "scripts/sync-about.sh", "--live"],
                ["bash", "scripts/sync-family.sh", "--live"],
            )
            for index, command in enumerate(commands):
                with self.subTest(script=command[1]):
                    environment, mutation_log = self.fake_release_environment(base / str(index))
                    environment["FAKE_GIT_REMOTE"] = (
                        "https://github.com.evil.invalid/aaron-he-zhu/aaron-marketing-skills.git"
                    )
                    result = subprocess.run(
                        command, cwd=ROOT, capture_output=True, text=True, env=environment,
                    )
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("canonical github.com", result.stderr)
                    self.assertFalse(mutation_log.exists())

    def test_every_release_live_entrypoint_consumes_one_identity_snapshot(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            status_snapshot = base / "registry-status.json"
            status_snapshot.write_text('{"skills": []}\n', encoding="utf-8")
            commands = (
                ["bash", "scripts/publish-clawhub.sh", "--i-accept-mit0", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-skillhub.sh", "--live", "--skill", "narrative-quality-auditor"],
                ["bash", "scripts/publish-package.sh", "--live"],
                ["bash", "scripts/publish-registries.sh", "--live", "--from-json", str(status_snapshot)],
                ["bash", "scripts/sync-about.sh", "--live"],
                ["bash", "scripts/sync-family.sh", "--live"],
            )
            for index, command in enumerate(commands):
                with self.subTest(script=command[1]):
                    environment, _mutation_log = self.fake_release_environment(base / str(index))
                    # Repo B becomes visible only on a third origin read.  A
                    # live entrypoint must consume the A tuple returned by its
                    # one two-read gate and never independently reopen origin.
                    environment["FAKE_GIT_REMOTE_SWITCH_AFTER"] = "2"
                    environment["FAKE_GIT_ARCHIVE_FAILURE"] = "1"
                    result = subprocess.run(
                        command, cwd=ROOT, capture_output=True, text=True, env=environment,
                    )
                    count = int(Path(environment["FAKE_GIT_REMOTE_COUNTER"]).read_text(
                        encoding="utf-8",
                    ))
                    self.assertEqual(2, count, result.stdout + result.stderr)
                    self.assertNotIn("other-owner/other-repository", result.stdout + result.stderr)

    def test_registry_orchestrator_rejects_child_origin_switch(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            status_snapshot = base / "registry-status.json"
            status_snapshot.write_text(json.dumps(self.canonical_registry_snapshot(
                clawhub_behind="narrative-quality-auditor",
            )) + "\n", encoding="utf-8")
            environment, mutation_log = self.fake_release_environment(base / "fake")
            environment["FAKE_GIT_SHOW_ROOT"] = str(
                self.make_committed_registry_identity(base)
            )
            # Parent sees A for its two-read gate; the independently gated
            # child sees B and must reject it against the inherited A tuple.
            environment["FAKE_GIT_REMOTE_SWITCH_AFTER"] = "2"
            result = subprocess.run(
                [
                    "bash", "scripts/publish-registries.sh", "--live", "clawhub",
                    "--from-json", str(status_snapshot),
                ],
                cwd=ROOT, capture_output=True, text=True, env=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("does not match parent", result.stdout + result.stderr)
            self.assertEqual(
                4,
                int(Path(environment["FAKE_GIT_REMOTE_COUNTER"]).read_text(encoding="utf-8")),
            )
            self.assertFalse(mutation_log.exists(), "child registry CLI ran after identity drift")

    def test_registry_snapshot_is_bound_to_repository_commit_and_full_canonical_set(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            environment, _mutation_log = self.fake_release_environment(base / "fake")
            commit = environment["FAKE_GIT_COMMIT"]
            snapshot = self.canonical_registry_snapshot(
                commit=commit,
                clawhub_behind="narrative-quality-auditor",
                use_worktree=True,
            )

            def run(candidate):
                path = base / "registry-status.json"
                path.write_text(json.dumps(candidate) + "\n", encoding="utf-8")
                return subprocess.run(
                    [
                        "bash", "scripts/publish-registries.sh", "clawhub",
                        "--from-json", str(path),
                    ],
                    cwd=ROOT, capture_output=True, text=True, env=environment,
                )

            valid = run(snapshot)
            self.assertEqual(0, valid.returncode, valid.stderr)
            self.assertIn("would publish (clawhub) narrative-quality-auditor", valid.stdout)

            wrong_repository = json.loads(json.dumps(snapshot))
            wrong_repository["repository"] = "other-owner/other-repository"
            rejected = run(wrong_repository)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("repository/version/commit identity", rejected.stderr)

            wrong_commit = json.loads(json.dumps(snapshot))
            wrong_commit["commit"] = "f" * 40
            rejected = run(wrong_commit)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("repository/version/commit identity", rejected.stderr)

            truncated = json.loads(json.dumps(snapshot))
            truncated["skills"].pop()
            rejected = run(truncated)
            self.assertNotEqual(0, rejected.returncode)
            self.assertIn("exactly 120 records", rejected.stderr)

    def test_package_dry_run_does_not_apply_live_clean_tree_gate(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, mutation_log = self.fake_release_environment(
                Path(temporary), status="?? local-preview-only\n",
            )
            result = subprocess.run(
                ["bash", "scripts/publish-package.sh", "--dry-run"],
                cwd=ROOT, capture_output=True, text=True, env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Mode    : dry-run", result.stdout)
            self.assertIn("--dry-run", mutation_log.read_text(encoding="utf-8"))

    def test_package_live_requires_verified_build_before_any_upload(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, mutation_log = self.fake_release_environment(Path(temporary))
            result = subprocess.run(
                ["bash", "scripts/publish-package.sh", "--live"],
                cwd=ROOT, capture_output=True, text=True, env=environment,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("requires --from-build", result.stderr)
            self.assertFalse(mutation_log.exists())

    def test_package_transport_recovery_requires_remote_source_and_content_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for mode, expected_success in (
                    ("matching", True),
                    ("source-mismatch", False),
                    ("digest-mismatch", False),
                    ("unsupported", False)):
                with self.subTest(mode=mode):
                    environment, _mutation_log = self.fake_release_environment(base / mode)
                    environment["FAKE_PINNED_ROOT"] = str(
                        self.make_minimal_package_build_fixture(base / (mode + "-source"))
                    )
                    self.install_transport_error_clawhub(environment, mode=mode)
                    result = subprocess.run(
                        ["bash", "scripts/publish-package.sh", "--from-build", "--live"],
                        cwd=ROOT, capture_output=True, text=True, env=environment,
                    )
                    if expected_success:
                        self.assertEqual(0, result.returncode, result.stderr)
                        self.assertIn(
                            "matching source commit and content digest", result.stdout
                        )
                    else:
                        self.assertNotEqual(0, result.returncode)
                        self.assertIn(
                            "exact remote source/content identity could not be confirmed",
                            result.stderr,
                        )

    def test_package_live_fails_closed_on_fetch_or_reachability_and_publishes_pinned_commit(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            for option, expected in (
                    ({"fetch_failure": True}, "cannot refresh origin/main"),
                    ({"ancestor_failure": True}, "not reachable from origin/main")):
                environment, mutation_log = self.fake_release_environment(base / expected.split()[0], **option)
                result = subprocess.run(
                    ["bash", "scripts/publish-package.sh", "--live"],
                    cwd=ROOT, capture_output=True, text=True, env=environment,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, result.stderr)
                self.assertFalse(mutation_log.exists())

            environment, mutation_log = self.fake_release_environment(base / "passing")
            result = subprocess.run(
                ["bash", "scripts/publish-package.sh", "--from-build", "--live"],
                cwd=ROOT, capture_output=True, text=True, env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            invocation = mutation_log.read_text(encoding="utf-8")
            self.assertIn("clawhub package publish ", invocation)
            self.assertIn("--source-commit " + "a" * 40, invocation)


if __name__ == "__main__":
    unittest.main()
