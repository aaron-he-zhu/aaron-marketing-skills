#!/usr/bin/env python3
"""Create or read-only verify the immutable current v19 GitHub release.

The default mode is a network-free dry run.  ``--live`` is an owner-only
operation and requires both an out-of-repository private release receipt and
an out-of-repository directory containing the six deterministic release
assets.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "aaron-he-zhu/aaron-marketing-skills"
RELEASE_VERSION = "20.0.0"
TAG = "v" + RELEASE_VERSION
ASSET_NAMES = (
    "aaron-marketing-skills-%s-lite.tar.gz" % RELEASE_VERSION,
    "aaron-marketing-skills-%s-pro.tar.gz" % RELEASE_VERSION,
    "aaron-marketing-skills-%s-governed.tar.gz" % RELEASE_VERSION,
    "aaron-marketing-skills-%s-agent-plugin-v1-lite.tar.gz" % RELEASE_VERSION,
    "SHA256SUMS",
    "release-assets.json",
)
ASSET_LIMITS = {
    name: 32 * 1024 * 1024 if name.endswith(".tar.gz") else 1024 * 1024
    for name in ASSET_NAMES
}
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
REMOTE_PATTERNS = (
    re.compile(
        r"^https://github\.com/"
        r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$"
    ),
    re.compile(
        r"^ssh://git@github\.com/"
        r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$"
    ),
    re.compile(
        r"^git@github\.com:"
        r"(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?$"
    ),
)


class ReleaseError(RuntimeError):
    """A final-release invariant was not satisfied."""


def run(
    arguments: list[str],
    *,
    cwd: Path,
    input_text: str | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            arguments,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ReleaseError("cannot execute %s: %s" % (arguments[0], exc)) from exc
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "exit %d" % result.returncode
        raise ReleaseError("%s failed: %s" % (" ".join(arguments), detail))
    return result


def git(root: Path, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(["git", *arguments], cwd=root, check=check)


def gh(root: Path, *arguments: str, check: bool = True,
       input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return run(
        ["gh", *arguments],
        cwd=root,
        check=check,
        input_text=input_text,
    )


def repository_root() -> Path:
    result = run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=ROOT,
    ).stdout.strip()
    if not result:
        raise ReleaseError("cannot resolve the Git worktree root")
    try:
        root = Path(result).resolve(strict=True)
        script_root = ROOT.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError("cannot resolve the release worktree: %s" % exc) from exc
    if root != script_root:
        raise ReleaseError("release script must run from its own Git worktree")
    return root


def clean_tree(root: Path) -> None:
    status = git(
        root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ).stdout
    if status:
        raise ReleaseError(
            "working tree is dirty; commit or remove every tracked/untracked change"
        )


def origin_identity(root: Path) -> tuple[str, str]:
    result = git(
        root,
        "config",
        "--get-all",
        "remote.origin.url",
        check=False,
    )
    urls = result.stdout.splitlines()
    if result.returncode != 0 or len(urls) != 1 or not urls[0]:
        raise ReleaseError("origin must have exactly one URL")
    remote = urls[0]
    match = next(
        (candidate.fullmatch(remote) for candidate in REMOTE_PATTERNS
         if candidate.fullmatch(remote)),
        None,
    )
    if match is None:
        raise ReleaseError("origin must use a canonical github.com URL")
    repository = "%s/%s" % (match.group("owner"), match.group("repo"))
    if repository != REPOSITORY:
        raise ReleaseError(
            "origin resolves to %s, expected %s" % (repository, REPOSITORY)
        )
    rewrites = git(
        root,
        "config",
        "--get-regexp",
        r"^url\..*\.insteadof$",
        check=False,
    )
    if rewrites.returncode == 0 and rewrites.stdout.strip():
        raise ReleaseError("Git URL rewrite rules are forbidden for live release")
    return remote, repository


def head_commit(root: Path) -> str:
    commit = git(
        root,
        "rev-parse",
        "--verify",
        "HEAD^{commit}",
    ).stdout.strip()
    if COMMIT_RE.fullmatch(commit) is None:
        raise ReleaseError("HEAD is not an exact lowercase 40-hex commit")
    return commit


def committed_text(root: Path, commit: str, path: str) -> str:
    result = git(root, "show", "%s:%s" % (commit, path))
    return result.stdout


def committed_version(root: Path, commit: str) -> str:
    try:
        plugin = json.loads(
            committed_text(root, commit, ".claude-plugin/plugin.json")
        )
    except (TypeError, ValueError) as exc:
        raise ReleaseError("committed plugin metadata is invalid JSON") from exc
    version = plugin.get("version") if isinstance(plugin, dict) else None
    if version != RELEASE_VERSION:
        raise ReleaseError(
            "committed bundle is %r; this final releaser only accepts %s"
            % (version, RELEASE_VERSION)
        )
    return version


def release_notes(root: Path, commit: str, version: str) -> str:
    versions = committed_text(root, commit, "VERSIONS.md")
    current = re.search(
        r"^\*\*Current release\*\*: `([^`]+)` \([^)]+\)\.",
        versions,
        re.MULTILINE,
    )
    if current is None or current.group(1) != version:
        raise ReleaseError("VERSIONS.md does not declare the committed release")
    changelog = re.search(r"^## Changelog\s*$", versions, re.MULTILINE)
    if changelog is None:
        raise ReleaseError("VERSIONS.md has no Changelog section")
    lines = versions[changelog.end():].lstrip("\r\n").splitlines(keepends=True)
    heading = re.compile(r"^### v%s(?:\s|$)" % re.escape(version))
    start = next((index for index, line in enumerate(lines) if heading.match(line)), None)
    if start is None:
        raise ReleaseError("VERSIONS.md has no v%s changelog" % version)
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### ")
        ),
        len(lines),
    )
    notes = "".join(lines[start:end]).strip("\r\n") + "\n"
    if "\x00" in notes or len(notes.encode("utf-8")) > 1024 * 1024:
        raise ReleaseError("release notes are empty, unsafe, or exceed 1 MiB")
    if len(notes.splitlines()) < 2:
        raise ReleaseError("v%s changelog has no release body" % version)
    return notes


def require_outside(root: Path, candidate: Path, label: str) -> Path:
    try:
        resolved = candidate.expanduser().resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
    except ValueError:
        return resolved
    except OSError as exc:
        raise ReleaseError("%s is unavailable: %s" % (label, exc)) from exc
    raise ReleaseError("%s must stay outside the source repository" % label)


def require_evidence_root(candidate: Path) -> Path:
    if not candidate.is_absolute():
        raise ReleaseError("private semantic evidence root must be absolute")
    try:
        status = candidate.lstat()
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ReleaseError(
            "private semantic evidence root is unavailable: %s" % exc
        ) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ReleaseError("private semantic evidence root must be a real directory")
    return resolved


def refresh_main(root: Path, remote: str, commit: str) -> str:
    git(
        root,
        "fetch",
        "-q",
        "--",
        remote,
        "+refs/heads/main:refs/remotes/origin/main",
    )
    remote_commit = git(
        root,
        "rev-parse",
        "--verify",
        "refs/remotes/origin/main^{commit}",
    ).stdout.strip()
    if COMMIT_RE.fullmatch(remote_commit) is None:
        raise ReleaseError("refreshed origin/main is not an exact commit")
    ancestor = git(
        root,
        "merge-base",
        "--is-ancestor",
        commit,
        remote_commit,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ReleaseError(
            "%s is not reachable from refreshed origin/main %s"
            % (commit, remote_commit)
        )
    return remote_commit


def verify_receipt(
    root: Path,
    receipt: Path,
    maturity_report: Path,
    evidence_root: Path,
    commit: str,
    version: str,
) -> str:
    result = run(
        [
            sys.executable,
            str(root / "scripts" / "verify-release-receipt.py"),
            str(receipt),
            "--source-commit",
            commit,
            "--release-version",
            version,
            "--verifier",
            str(root / "scripts" / "verify-profile-outcomes.py"),
            "--maturity-report",
            str(maturity_report),
            "--evidence-root",
            str(evidence_root),
            "--required-gate",
            "engineering-validation-v19",
        ],
        cwd=root,
    )
    fields = result.stdout.strip().split("\t")
    if (
        len(fields) != 3
        or re.fullmatch(r"[0-9a-f]{64}", fields[0]) is None
        or re.fullmatch(
            re.escape(version) + r"-rc\.[1-9][0-9]*", fields[1]
        ) is None
        or fields[2] != commit
    ):
        raise ReleaseError("private release receipt returned a malformed identity")
    return fields[0]


def _copy_regular(source: Path, destination: Path) -> None:
    try:
        before = source.lstat()
    except OSError as exc:
        raise ReleaseError("release asset is unavailable: %s" % exc) from exc
    if (
        stat.S_ISLNK(before.st_mode)
        or not stat.S_ISREG(before.st_mode)
        or before.st_nlink != 1
    ):
        raise ReleaseError(
            "release asset must be a single-link regular file: %s" % source.name
        )
    limit = ASSET_LIMITS.get(source.name)
    if limit is None or before.st_size > limit:
        raise ReleaseError(
            "release asset %s exceeds its bounded size" % source.name
        )
    source_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        source_fd = os.open(source, source_flags)
    except OSError as exc:
        raise ReleaseError("cannot open release asset %s: %s" % (source.name, exc)) from exc
    try:
        destination_fd = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            0o600,
        )
    except OSError as exc:
        os.close(source_fd)
        raise ReleaseError("cannot snapshot release asset %s: %s" % (source.name, exc)) from exc
    try:
        opened = os.fstat(source_fd)
        if (
            opened.st_dev != before.st_dev
            or opened.st_ino != before.st_ino
            or opened.st_nlink != before.st_nlink
            or opened.st_size != before.st_size
        ):
            raise ReleaseError("release asset changed while opening: %s" % source.name)
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            view = memoryview(chunk)
            while view:
                written = os.write(destination_fd, view)
                if written <= 0:
                    raise ReleaseError(
                        "release asset copy made no progress: %s" % source.name
                    )
                view = view[written:]
        os.fsync(destination_fd)
    finally:
        os.close(source_fd)
        os.close(destination_fd)
    try:
        after = source.lstat()
    except OSError as exc:
        raise ReleaseError("release asset disappeared during snapshot: %s" % exc) from exc
    if (
        before.st_dev,
        before.st_ino,
        before.st_nlink,
        before.st_mode,
        before.st_size,
        before.st_mtime_ns,
        before.st_ctime_ns,
    ) != (
        after.st_dev,
        after.st_ino,
        after.st_nlink,
        after.st_mode,
        after.st_size,
        after.st_mtime_ns,
        after.st_ctime_ns,
    ):
        raise ReleaseError("release asset changed during snapshot: %s" % source.name)
    destination.chmod(0o644)


def snapshot_assets(source: Path, destination: Path) -> None:
    try:
        status = source.lstat()
        names = {entry.name for entry in source.iterdir()}
    except OSError as exc:
        raise ReleaseError("release asset directory is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ReleaseError("release asset path must be a real directory")
    if names != set(ASSET_NAMES):
        raise ReleaseError(
            "release asset directory must contain exactly: %s"
            % ", ".join(ASSET_NAMES)
        )
    destination.mkdir(mode=0o700)
    for name in ASSET_NAMES:
        _copy_regular(source / name, destination / name)


def verify_assets(
    root: Path,
    assets: Path,
    repository: str,
    commit: str,
    version: str,
) -> None:
    run(
        [
            sys.executable,
            str(root / "scripts" / "build-release-assets.py"),
            "--verify",
            str(assets),
            "--source-repo",
            str(root),
            "--source-repository",
            repository,
            "--source-commit",
            commit,
            "--version",
            version,
        ],
        cwd=root,
    )


def successful_owner_validation(root: Path, repository: str, commit: str) -> None:
    result = gh(
        root,
        "api",
        "--method",
        "GET",
        "repos/%s/actions/workflows/release-validation.yml/runs"
        "?head_sha=%s&status=completed&per_page=100" % (repository, commit),
    )
    try:
        payload = json.loads(result.stdout)
    except ValueError as exc:
        raise ReleaseError("release-validation response is not JSON") from exc
    runs = payload.get("workflow_runs") if isinstance(payload, dict) else None
    if not isinstance(runs, list):
        raise ReleaseError("release-validation response has no workflow_runs")
    owner = repository.split("/", 1)[0]
    matching = [
        item
        for item in runs
        if isinstance(item, dict)
        and item.get("head_sha") == commit
        and item.get("conclusion") == "success"
        and item.get("event") == "workflow_dispatch"
        and isinstance(item.get("actor"), dict)
        and item["actor"].get("login") == owner
    ]
    if not matching:
        raise ReleaseError(
            "no successful owner-run release-validation workflow exists for %s"
            % commit
        )


def remote_tag_commit(root: Path, remote: str, tag: str) -> str | None:
    result = git(
        root,
        "ls-remote",
        "--tags",
        remote,
        "refs/tags/%s" % tag,
        "refs/tags/%s^{}" % tag,
    )
    rows: dict[str, str] = {}
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) != 2 or COMMIT_RE.fullmatch(fields[0]) is None:
            raise ReleaseError("remote tag query returned malformed data")
        if fields[1] in rows:
            raise ReleaseError("remote tag query returned duplicate refs")
        rows[fields[1]] = fields[0]
    if not rows:
        return None
    direct = "refs/tags/%s" % tag
    peeled = direct + "^{}"
    if set(rows) != {direct, peeled}:
        raise ReleaseError("existing %s tag is not an annotated tag" % tag)
    return rows[peeled]


def local_tag_commit(root: Path, tag: str) -> str | None:
    exists = git(
        root,
        "rev-parse",
        "-q",
        "--verify",
        "refs/tags/%s" % tag,
        check=False,
    )
    if exists.returncode != 0:
        return None
    kind = git(root, "cat-file", "-t", "refs/tags/%s" % tag).stdout.strip()
    if kind != "tag":
        raise ReleaseError("local %s is not an annotated tag" % tag)
    commit = git(
        root,
        "rev-parse",
        "--verify",
        "refs/tags/%s^{commit}" % tag,
    ).stdout.strip()
    if COMMIT_RE.fullmatch(commit) is None:
        raise ReleaseError("local %s does not peel to an exact commit" % tag)
    return commit


def release_pages(root: Path, repository: str) -> list[dict[str, Any]]:
    result = gh(
        root,
        "api",
        "--paginate",
        "--slurp",
        "repos/%s/releases?per_page=100" % repository,
    )
    try:
        pages = json.loads(result.stdout)
    except ValueError as exc:
        raise ReleaseError("GitHub release list is not JSON") from exc
    if not isinstance(pages, list) or any(not isinstance(page, list) for page in pages):
        raise ReleaseError("GitHub release pagination has an invalid shape")
    releases: list[dict[str, Any]] = []
    for page in pages:
        for item in page:
            if not isinstance(item, dict):
                raise ReleaseError("GitHub release list contains a non-object")
            releases.append(item)
    return releases


def find_release(root: Path, repository: str, tag: str) -> dict[str, Any] | None:
    matches = [
        item for item in release_pages(root, repository)
        if item.get("tag_name") == tag
    ]
    if len(matches) > 1:
        raise ReleaseError("GitHub returned duplicate releases for %s" % tag)
    return matches[0] if matches else None


def validate_release_metadata(
    release: dict[str, Any],
    tag: str,
    notes: str,
) -> None:
    if (
        release.get("tag_name") != tag
        or release.get("name") != tag
        or release.get("draft") is not False
        or release.get("prerelease") is not False
    ):
        raise ReleaseError("%s is not the expected final GitHub release" % tag)
    body = release.get("body")
    if not isinstance(body, str) or body.rstrip("\n") != notes.rstrip("\n"):
        raise ReleaseError("%s release notes do not match VERSIONS.md" % tag)
    assets = release.get("assets")
    if not isinstance(assets, list):
        raise ReleaseError("%s release has no asset list" % tag)
    names = []
    for item in assets:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("name"), str)
            or item.get("state") != "uploaded"
        ):
            raise ReleaseError("%s contains an incomplete release asset" % tag)
        names.append(item["name"])
    if len(names) != len(set(names)) or set(names) != set(ASSET_NAMES):
        raise ReleaseError("%s does not have the exact six release assets" % tag)


def verify_downloaded_release(
    root: Path,
    repository: str,
    commit: str,
    version: str,
    temporary: Path,
) -> None:
    download = temporary / "downloaded-release"
    download.mkdir(mode=0o700)
    gh(
        root,
        "release",
        "download",
        TAG,
        "--repo",
        repository,
        "--dir",
        str(download),
    )
    canonical_download = temporary / "downloaded-release-snapshot"
    snapshot_assets(download, canonical_download)
    verify_assets(root, canonical_download, repository, commit, version)


def recheck_before_mutation(
    root: Path,
    remote: str,
    repository: str,
    commit: str,
    remote_main: str,
) -> None:
    clean_tree(root)
    current_remote, current_repository = origin_identity(root)
    if current_remote != remote or current_repository != repository:
        raise ReleaseError("origin changed during the final release gate")
    if head_commit(root) != commit:
        raise ReleaseError("HEAD changed during the final release gate")
    current_main = git(
        root,
        "rev-parse",
        "--verify",
        "refs/remotes/origin/main^{commit}",
    ).stdout.strip()
    if current_main != remote_main:
        raise ReleaseError("origin/main changed after release validation")
    ancestor = git(
        root,
        "merge-base",
        "--is-ancestor",
        commit,
        current_main,
        check=False,
    )
    if ancestor.returncode != 0:
        raise ReleaseError("release commit is no longer reachable from origin/main")


def create_or_resume_tag(
    root: Path,
    remote: str,
    commit: str,
) -> None:
    remote_commit = remote_tag_commit(root, remote, TAG)
    if remote_commit is not None:
        if remote_commit != commit:
            raise ReleaseError(
                "existing %s resolves to %s, not %s" % (TAG, remote_commit, commit)
            )
        return
    local_commit = local_tag_commit(root, TAG)
    if local_commit is None:
        git(
            root,
            "-c",
            "tag.gpgSign=false",
            "tag",
            "-a",
            TAG,
            commit,
            "-m",
            "Release %s" % TAG,
        )
    elif local_commit != commit:
        raise ReleaseError(
            "local %s resolves to %s, not %s" % (TAG, local_commit, commit)
        )
    pushed = git(
        root,
        "push",
        "--",
        remote,
        "refs/tags/%s:refs/tags/%s" % (TAG, TAG),
        check=False,
    )
    final_commit = remote_tag_commit(root, remote, TAG)
    if final_commit != commit:
        detail = pushed.stderr.strip() or pushed.stdout.strip() or "tag did not appear"
        raise ReleaseError("cannot publish immutable %s: %s" % (TAG, detail))


def create_release(
    root: Path,
    repository: str,
    assets: Path,
    notes: str,
) -> None:
    arguments = [
        "release",
        "create",
        TAG,
        "--repo",
        repository,
        "--verify-tag",
        "--title",
        TAG,
        "--notes-file",
        "-",
    ]
    arguments.extend(str(assets / name) for name in ASSET_NAMES)
    result = gh(
        root,
        *arguments,
        input_text=notes,
        check=False,
    )
    if result.returncode == 0:
        return
    # A concurrent owner may have completed the same immutable release after
    # our last read.  Only that exact final state is recoverable.
    existing = find_release(root, repository, TAG)
    if existing is None:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise ReleaseError("gh release create failed: %s" % detail)
    validate_release_metadata(existing, TAG, notes)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--live",
        action="store_true",
        help="Create the final tag/release after every owner-run gate passes.",
    )
    parser.add_argument(
        "--receipt",
        type=Path,
        help="Out-of-repository private release receipt (required with --live).",
    )
    parser.add_argument(
        "--asset-dir",
        type=Path,
        help="Out-of-repository six-asset directory (required with --live).",
    )
    parser.add_argument(
        "--maturity-report",
        type=Path,
        help="Absolute private dynamic maturity report (required with --live).",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="Absolute private raw semantic evidence root (required with --live).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        root = repository_root()
        clean_tree(root)
        remote, repository = origin_identity(root)
        commit = head_commit(root)
        version = committed_version(root, commit)
        notes = release_notes(root, commit, version)
        if not args.live:
            if any(
                value is not None
                for value in (
                    args.receipt,
                    args.asset_dir,
                    args.maturity_report,
                    args.evidence_root,
                )
            ):
                raise ReleaseError(
                    "--receipt/--asset-dir/--maturity-report/--evidence-root "
                    "are accepted only with --live"
                )
            print(
                "DRY RUN: would gate and create-or-verify %s for %s@%s"
                % (TAG, repository, commit)
            )
            print(
                "DRY RUN: no fetch, tag, push, GitHub mutation, or asset upload was performed"
            )
            return 0
        if any(
            value is None
            for value in (
                args.receipt,
                args.asset_dir,
                args.maturity_report,
                args.evidence_root,
            )
        ):
            raise ReleaseError(
                "--live requires --receipt, --asset-dir, --maturity-report, "
                "and --evidence-root"
            )
        receipt = require_outside(root, args.receipt, "private release receipt")
        asset_source = require_outside(root, args.asset_dir, "release asset directory")
        maturity_report = require_outside(
            root,
            args.maturity_report,
            "private maturity report",
        )
        evidence_root = require_evidence_root(args.evidence_root)
        remote_main = refresh_main(root, remote, commit)
        receipt_sha = verify_receipt(
            root,
            receipt,
            maturity_report,
            evidence_root,
            commit,
            version,
        )
        successful_owner_validation(root, repository, commit)

        with tempfile.TemporaryDirectory(prefix="aaron-github-release-") as temporary_name:
            temporary = Path(temporary_name)
            temporary.chmod(0o700)
            asset_snapshot = temporary / "verified-assets"
            snapshot_assets(asset_source, asset_snapshot)
            verify_assets(root, asset_snapshot, repository, commit, version)

            existing_tag = remote_tag_commit(root, remote, TAG)
            if existing_tag is not None and existing_tag != commit:
                raise ReleaseError(
                    "existing %s resolves to %s, not %s"
                    % (TAG, existing_tag, commit)
                )
            existing_release = find_release(root, repository, TAG)
            if existing_release is not None:
                if existing_tag != commit:
                    raise ReleaseError(
                        "existing %s release is not backed by the exact annotated tag"
                        % TAG
                    )
                validate_release_metadata(existing_release, TAG, notes)
                verify_downloaded_release(
                    root,
                    repository,
                    commit,
                    version,
                    temporary,
                )
                if remote_tag_commit(root, remote, TAG) != commit:
                    raise ReleaseError("%s changed during read-only verification" % TAG)
                final_release = find_release(root, repository, TAG)
                if final_release is None:
                    raise ReleaseError("%s disappeared during read-only verification" % TAG)
                validate_release_metadata(final_release, TAG, notes)
                print(
                    "GitHub release already verified (read-only): %s@%s %s receipt=%s"
                    % (repository, commit, TAG, receipt_sha)
                )
                return 0

            recheck_before_mutation(
                root,
                remote,
                repository,
                commit,
                remote_main,
            )
            create_or_resume_tag(root, remote, commit)
            if remote_tag_commit(root, remote, TAG) != commit:
                raise ReleaseError("%s changed after publication" % TAG)

            # Re-read before creating the release so a same-commit interrupted
            # run or concurrent owner invocation is safely resumable.
            existing_release = find_release(root, repository, TAG)
            if existing_release is None:
                create_release(root, repository, asset_snapshot, notes)
                existing_release = find_release(root, repository, TAG)
            if existing_release is None:
                raise ReleaseError("GitHub release did not appear after creation")
            validate_release_metadata(existing_release, TAG, notes)
            verify_downloaded_release(
                root,
                repository,
                commit,
                version,
                temporary,
            )
            if remote_tag_commit(root, remote, TAG) != commit:
                raise ReleaseError("%s changed during final verification" % TAG)
            final_release = find_release(root, repository, TAG)
            if final_release is None:
                raise ReleaseError("%s disappeared during final verification" % TAG)
            validate_release_metadata(final_release, TAG, notes)
        print(
            "GitHub final release verified: %s@%s %s receipt=%s"
            % (repository, commit, TAG, receipt_sha)
        )
        return 0
    except ReleaseError as exc:
        print("release refused: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
