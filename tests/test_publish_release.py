import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
COMMON = ROOT / "scripts" / "publish-common.sh"
DISCIPLINES = (
    "narrative",
    "seo-geo",
    "social",
    "email",
    "ad",
    "influencer",
    "launch",
)
ENGINEERING_TOOL_REFS = {
    "issuer": "scripts/issue-engineering-release-receipt.py",
    "release_verifier": "scripts/verify-release-receipt.py",
    "maturity_checker": "scripts/check-engineering-maturity.py",
    "semantic_verifier": "scripts/verify-semantic-evidence.py",
    "maturity_rubric": "references/engineering-maturity-rubric.json",
    "semantic_policy": "evals/semantic-evidence-policy.json",
    "receipt_schema": "references/engineering-release-receipt.schema.json",
}
MOCK_SEMANTIC_VERIFIER = """#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[sys.argv.index("--evidence-root") + 1])
sys.stdout.buffer.write((root / "mock-revalidated-summary.json").read_bytes())
"""


def pilot_release_receipt(commit="a" * 40, version="19.0.0"):
    return {
        "schema_version": "1.0",
        "gate": "profile-pilots-v19",
        "passed": True,
        "release_version": version,
        "release_candidate": version + "-rc.1",
        "source_commit": commit,
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
            "release_candidate": version + "-rc.1",
            "source_commit": commit,
            "counts": {"pilot": 14},
            "discipline_counts": {
                discipline: 2 for discipline in DISCIPLINES
            },
            "randomized_order_counts": {
                discipline: {
                    "lite-first": 1,
                    "governed-first": 1,
                }
                for discipline in DISCIPLINES
            },
            "lite_completion_rate": 1.0,
            "governed_completion_rate": 1.0,
            "governed_required_counts": {
                discipline: 1 for discipline in DISCIPLINES
            },
            "safety_observation_counts": {
                key: 1
                for key in (
                    "mandatory_approval_hit",
                    "consent_hit",
                    "claims_hit",
                    "external_action_hit",
                )
            },
            "governed_median_time_ratio": 1.5,
            "governed_median_token_ratio": 1.5,
            "safety_failure_count": 0,
            "passed": True,
            "errors": [],
        },
    }


def engineering_release_receipt(
    *,
    source_tree_sha256,
    release_root=ROOT,
    commit="a" * 40,
    version="19.0.0",
):
    stamp = (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    return {
        "$schema": "references/engineering-release-receipt.schema.json",
        "schema_version": "1.0",
        "gate": "engineering-validation-v19",
        "passed": True,
        "release_version": version,
        "release_candidate": version + "-rc.1",
        "source_commit": commit,
        "issued_at": stamp,
        "repository": {
            "branch": "fixture",
            "worktree_clean": True,
            "source_tree_sha256": source_tree_sha256,
        },
        "tools": {
            name: {
                "ref": reference,
                "sha256": hashlib.sha256(
                    (release_root / reference).read_bytes()
                ).hexdigest(),
            }
            for name, reference in ENGINEERING_TOOL_REFS.items()
        },
        "maturity": {
            "evaluated_at": stamp,
            "report_sha256": "1" * 64,
            "target_score": 95,
            "achieved": True,
            "dimension_scores": {
                name: 100
                for name in ("prompt", "context", "harness", "loop", "graph")
            },
            "required_hard_gates": {
                "P19": True,
                "P20": True,
                "H20": True,
            },
        },
        "semantic_evidence": {
            "schema_version": "1.0",
            "valid": True,
            "run_id": "12345678-1234-1234-1234-123456789abc",
            "profile": "smoke",
            "case_count": 24,
            "case_provenance": {"simulated": 24},
            "execution_mode": "real",
            "model_provider": "fixture-provider",
            "model_id": "fixture-model",
            "judge_model_id": "fixture-judge",
            "distinct_judge_model": True,
            "total_judge_attempts": 24,
            "retried_cases": 0,
            "judge_protocol_retries": 0,
            "host_name": "fixture-host",
            "host_version": "1",
            "adapter_name": "fixture-adapter",
            "adapter_implementation_sha256": "2" * 64,
            "runner_sha256": "3" * 64,
            "selection_sha256": "4" * 64,
            "protocol_schema_sha256": "5" * 64,
            "request_stream_sha256": "6" * 64,
            "result_stream_sha256": "7" * 64,
            "head_record_hash": "8" * 64,
            "completion_sha256": "9" * 64,
            "oldest_result_at": stamp,
            "newest_evidence_at": stamp,
            "age_seconds": 0,
        },
        "claims": {
            "validation_scope": "engineering-only",
            "evidence_provenance": "simulated-semantic-cases",
            "real_project_outcomes_validated": False,
            "default_profile": "lite",
            "governed_outcome_claims_allowed": False,
            "governed_default_promotion_allowed": False,
        },
        "attestation": {
            "method": "explicit-owner-engineering-only-authorization",
            "statement": "release-v19-without-real-project-outcomes",
            "accepted_at": stamp,
        },
    }


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

    def run_receipt_verifier(
        self,
        receipt,
        *,
        expected_commit="a" * 40,
        expected_version="19.0.0",
        verifier=None,
    ):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            receipt_path = base / "private-receipt.json"
            receipt_path.write_text(
                json.dumps(receipt, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            receipt_path.chmod(0o600)
            command = [
                sys.executable,
                str(ROOT / "scripts" / "verify-release-receipt.py"),
                str(receipt_path),
                "--source-commit",
                expected_commit,
                "--release-version",
                expected_version,
            ]
            if verifier is not None:
                command.extend(("--verifier", str(verifier)))
            return subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

    def fake_release_environment(self, base, *, status="", fetch_failure=False,
                                 ancestor_failure=False):
        release_root = base / "mock-release-root"
        shutil.copytree(
            ROOT,
            release_root,
            ignore=shutil.ignore_patterns(
                ".git",
                ".planning",
                "__pycache__",
            ),
            copy_function=os.link,
        )
        mock_semantic_verifier = (
            release_root / "scripts" / "verify-semantic-evidence.py"
        )
        mock_semantic_verifier.unlink()
        mock_semantic_verifier.write_text(
            MOCK_SEMANTIC_VERIFIER,
            encoding="utf-8",
        )
        mock_semantic_verifier.chmod(0o755)
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
elif args == ["ls-tree", "-r", "--full-tree", commit]:
    print(os.environ["FAKE_GIT_LS_TREE"], end="")
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
    reference = args[1].split(":", 1)[1]
    tool_refs = {
        "scripts/issue-engineering-release-receipt.py",
        "scripts/verify-release-receipt.py",
        "scripts/check-engineering-maturity.py",
        "scripts/verify-semantic-evidence.py",
        "references/engineering-maturity-rubric.json",
        "evals/semantic-evidence-policy.json",
        "references/engineering-release-receipt.schema.json",
    }
    root = Path(
        os.environ["FAKE_REPOSITORY_ROOT"]
        if reference in tool_refs
        else os.environ.get(
            "FAKE_GIT_SHOW_ROOT",
            os.environ["FAKE_REPOSITORY_ROOT"],
        )
    )
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
            "FAKE_GIT_LS_TREE": (
                "100644 blob %s\\tpayload.txt\\n" % ("1" * 40)
            ),
            "FAKE_GIT_STATUS": status,
            "FAKE_GIT_FETCH_FAILURE": "1" if fetch_failure else "0",
            "FAKE_GIT_ANCESTOR_FAILURE": "1" if ancestor_failure else "0",
            "FAKE_GIT_ARCHIVE_FAILURE": "0",
            "FAKE_GATE_MUTATION_KIND": "",
            "FAKE_GIT_REWRITES": "",
            "FAKE_REPOSITORY_ROOT": str(release_root),
            "FAKE_PINNED_ROOT": str(release_root),
            "FAKE_RELEASE_CWD": str(release_root),
            "FAKE_PUSH_ROOT": str(base / "pushes"),
            "FAKE_MUTATION_LOG": str(base / "mutations.log"),
        })
        release_version = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )["version"]
        if int(release_version.split(".", 1)[0]) >= 19:
            receipt_path = base / "private-release-receipt.json"
            receipt = engineering_release_receipt(
                version=release_version,
                release_root=release_root,
                source_tree_sha256=hashlib.sha256(
                    environment["FAKE_GIT_LS_TREE"].encode("utf-8")
                ).hexdigest(),
            )
            rubric = json.loads(
                (
                    release_root
                    / "references"
                    / "engineering-maturity-rubric.json"
                ).read_text(encoding="utf-8")
            )
            report = {
                "$schema": "references/engineering-maturity-report.schema.json",
                "schema_version": "1.0",
                "evaluated_at": receipt["maturity"]["evaluated_at"],
                "repository": {
                    "git_available": True,
                    "commit": "a" * 40,
                    "branch": "fixture",
                    "worktree_clean": True,
                },
                "checker": receipt["tools"]["maturity_checker"],
                "rubric_sha256": receipt["tools"]["maturity_rubric"]["sha256"],
                "target_score": 95,
                "achieved": True,
                "semantic_evidence_run_id": receipt["semantic_evidence"]["run_id"],
                "semantic_evidence": receipt["semantic_evidence"],
                "dimensions": {
                    name: {
                        "raw_score": 100,
                        "final_score": 100,
                        "score_10": 10.0,
                        "target_met": True,
                        "failed_hard_gates": [],
                        "failed_controls": [],
                        "controls": [
                            {
                                **control,
                                "passed": True,
                                "points": 5,
                                "evidence": "mocked publisher gate boundary",
                            }
                            for control in controls
                        ],
                    }
                    for name, controls in rubric["dimensions"].items()
                },
            }
            report_path = base / "private-maturity-report.json"
            report_raw = (
                json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False)
                + "\n"
            ).encode("utf-8")
            report_path.write_bytes(report_raw)
            report_path.chmod(0o600)
            receipt["maturity"]["report_sha256"] = hashlib.sha256(
                report_raw
            ).hexdigest()
            evidence_root = base / "mock-raw-evidence-boundary"
            evidence_root.mkdir(mode=0o700)
            (evidence_root / "mock-revalidated-summary.json").write_text(
                json.dumps(receipt["semantic_evidence"], sort_keys=True) + "\n",
                encoding="utf-8",
            )
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
                    "AARON_RELEASE_MATURITY_REPORT": str(report_path),
                    "AARON_RELEASE_EVIDENCE_ROOT": str(evidence_root),
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
            self.assertIn(
                "blob/main/ad/phase/pinned-ad-skill/SKILL.md", ad_list,
            )
            self.assertNotIn("/tree/main/", ad_list)
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
                        command, cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                        command, cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                        command, cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                        command, cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                    cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Mode    : dry-run", result.stdout)
            self.assertIn("--dry-run", mutation_log.read_text(encoding="utf-8"))

    def test_package_live_requires_verified_build_before_any_upload(self):
        with tempfile.TemporaryDirectory() as temporary:
            environment, mutation_log = self.fake_release_environment(Path(temporary))
            result = subprocess.run(
                ["bash", "scripts/publish-package.sh", "--live"],
                cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                        cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
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
                    cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
                )
                self.assertNotEqual(0, result.returncode)
                self.assertIn(expected, result.stderr)
                self.assertFalse(mutation_log.exists())

            environment, mutation_log = self.fake_release_environment(base / "passing")
            result = subprocess.run(
                ["bash", "scripts/publish-package.sh", "--from-build", "--live"],
                cwd=Path(environment.get("FAKE_RELEASE_CWD", ROOT)), capture_output=True, text=True, env=environment,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            invocation = mutation_log.read_text(encoding="utf-8")
            self.assertIn("clawhub package publish ", invocation)
            self.assertIn("--source-commit " + "a" * 40, invocation)

    def test_release_pilot_receipt_is_accepted_with_exact_identity(self):
        result = self.run_receipt_verifier(pilot_release_receipt())
        self.assertEqual(0, result.returncode, result.stderr)
        fields = result.stdout.strip().split("\t")
        self.assertEqual(3, len(fields))
        self.assertEqual("19.0.0-rc.1", fields[1])
        self.assertEqual("a" * 40, fields[2])

        wrong_commit = self.run_receipt_verifier(
            pilot_release_receipt(),
            expected_commit="b" * 40,
        )
        self.assertNotEqual(0, wrong_commit.returncode)
        self.assertIn("source commit", wrong_commit.stderr)

        wrong_version = self.run_receipt_verifier(
            pilot_release_receipt(),
            expected_version="19.0.1",
        )
        self.assertNotEqual(0, wrong_version.returncode)
        self.assertIn("release version", wrong_version.stderr)

        with tempfile.TemporaryDirectory() as temporary:
            other_verifier = Path(temporary) / "other-verifier.py"
            other_verifier.write_text("# not the issuer\n", encoding="utf-8")
            wrong_verifier = self.run_receipt_verifier(
                pilot_release_receipt(),
                verifier=other_verifier,
            )
        self.assertNotEqual(0, wrong_verifier.returncode)
        self.assertIn("different outcome verifier", wrong_verifier.stderr)

    def test_release_pilot_receipt_rejects_forged_shape_and_thresholds(self):
        def mutation(callback):
            receipt = json.loads(json.dumps(pilot_release_receipt()))
            callback(receipt)
            return receipt

        def globally_unbalanced(receipt):
            summary = receipt["outcome_summary"]
            summary["counts"]["pilot"] = 21
            summary["discipline_counts"] = {
                discipline: 3 for discipline in DISCIPLINES
            }
            summary["randomized_order_counts"] = {
                discipline: {
                    "lite-first": 2,
                    "governed-first": 1,
                }
                for discipline in DISCIPLINES
            }

        invalid_receipts = {
            "unknown summary field": mutation(
                lambda value: value["outcome_summary"].update({"paired": 70})
            ),
            "unknown gate": mutation(
                lambda value: value.update({"gate": "profile-pilots-v20"})
            ),
            "full gate with pilot summary": mutation(
                lambda value: value.update({"gate": "profile-outcomes-v19"})
            ),
            "lite completion": mutation(
                lambda value: value["outcome_summary"].update(
                    {"lite_completion_rate": 0.89}
                )
            ),
            "governed completion": mutation(
                lambda value: value["outcome_summary"].update(
                    {"governed_completion_rate": 0.89}
                )
            ),
            "discipline total": mutation(
                lambda value: value["outcome_summary"]["discipline_counts"].update(
                    {"narrative": 3}
                )
            ),
            "randomized order": mutation(
                lambda value: value["outcome_summary"][
                    "randomized_order_counts"
                ]["narrative"].update(
                    {"lite-first": 2, "governed-first": 0}
                )
            ),
            "global randomized order": mutation(globally_unbalanced),
            "governed-required coverage": mutation(
                lambda value: value["outcome_summary"][
                    "governed_required_counts"
                ].update({"narrative": 0})
            ),
            "safety observation coverage": mutation(
                lambda value: value["outcome_summary"][
                    "safety_observation_counts"
                ].update({"consent_hit": 0})
            ),
            "cost ceiling": mutation(
                lambda value: value["outcome_summary"].update(
                    {"governed_median_token_ratio": 2.01}
                )
            ),
            "boolean safety count": mutation(
                lambda value: value["outcome_summary"].update(
                    {"safety_failure_count": False}
                )
            ),
        }
        for name, receipt in invalid_receipts.items():
            with self.subTest(name=name):
                result = self.run_receipt_verifier(receipt)
                self.assertNotEqual(0, result.returncode, result.stdout)
                self.assertIn("release receipt invalid", result.stderr)


if __name__ == "__main__":
    unittest.main()
