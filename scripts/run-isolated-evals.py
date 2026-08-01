#!/usr/bin/env python3
"""Run deterministic behavior suites from a private single-link snapshot.

Some sync providers materialize a worktree as hard-linked files.  The runtime
correctly rejects those files at trust boundaries, but that also prevents a
developer from exercising the fail-closed behavior suites in place.  This
launcher copies the current tracked plus non-ignored untracked worktree into a
private temporary Git repository, verifies every copied file is a regular
single-link file, and runs ``run-behavior-evals.py`` there.

The source repository is never modified.  The snapshot includes current
uncommitted edits so it tests the code under review, not only ``HEAD``.  Ignored
files (including private ``memory/runs`` evidence) are deliberately excluded.

Usage:
  python3 scripts/run-isolated-evals.py
  python3 scripts/run-isolated-evals.py -- --suite context-budget
  python3 scripts/run-isolated-evals.py --keep-stage -- --suite shared-http-and-connectors
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MAX_SNAPSHOT_FILES = 20_000
MAX_SNAPSHOT_BYTES = 2_000_000_000
COPY_CHUNK_BYTES = 1024 * 1024
IDENTITY_FIELDS = (
    "st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns",
)


class IsolatedEvalError(ValueError):
    pass


def _run(arguments, *, cwd, input_bytes=None, timeout=120, environment=None):
    try:
        return subprocess.run(
            arguments,
            cwd=cwd,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise IsolatedEvalError("cannot run %s: %s" % (arguments[0], exc)) from exc


def _git(
        source_root, *arguments, input_bytes=None, timeout=120,
        git_context=None):
    if not isinstance(git_context, dict):
        raise IsolatedEvalError("private Git context is required")
    result = _run(
        [
            "git", *git_context["config_arguments"],
            "-C", str(source_root), *arguments,
        ],
        cwd=source_root,
        input_bytes=input_bytes,
        timeout=timeout,
        environment=git_context["environment"],
    )
    if result.returncode:
        diagnostic = result.stderr.decode("utf-8", "replace").strip()
        raise IsolatedEvalError(
            "git %s failed: %s" % (" ".join(arguments), diagnostic or result.returncode)
        )
    return result


def _private_git_context(parent, stem):
    """Create a Git environment isolated from ambient config, hooks, and filters."""
    root = Path(parent) / (".%s-git-control" % stem)
    if root.exists():
        raise IsolatedEvalError("private Git control path already exists: %s" % root)
    home = root / "home"
    xdg = root / "xdg"
    template = root / "empty-template"
    hooks = root / "empty-hooks"
    for directory in (root, home, xdg, template, hooks):
        directory.mkdir(mode=0o700)
    environment = {
        "HOME": str(home),
        "XDG_CONFIG_HOME": str(xdg),
        "PATH": os.environ.get("PATH", os.defpath),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_ATTR_NOSYSTEM": "1",
        "GIT_TEMPLATE_DIR": str(template),
    }
    for key in ("LANG", "LC_ALL", "LC_CTYPE", "TMPDIR"):
        value = os.environ.get(key)
        if value:
            environment[key] = value
    return {
        "environment": environment,
        "config_arguments": (
            "-c", "core.hooksPath=%s" % hooks,
            "-c", "init.templateDir=%s" % template,
        ),
        "template": str(template),
    }


def _snapshot_paths(source_root, git_context):
    result = _git(
        source_root, "ls-files", "-z", "--cached", "--others", "--exclude-standard",
        git_context=git_context,
    )
    raw_paths = result.stdout.split(b"\0")
    if raw_paths and raw_paths[-1] == b"":
        raw_paths.pop()
    if len(raw_paths) > MAX_SNAPSHOT_FILES:
        raise IsolatedEvalError(
            "snapshot has %d files (limit %d)" % (len(raw_paths), MAX_SNAPSHOT_FILES)
        )
    decoded = []
    seen = set()
    for raw in raw_paths:
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise IsolatedEvalError("snapshot paths must be UTF-8") from exc
        path = PurePosixPath(value)
        if (
                not value or value.startswith("/") or "\x00" in value
                or any(part in {"", ".", "..", ".git"} for part in path.parts)):
            raise IsolatedEvalError("unsafe Git path in snapshot: %r" % value)
        normalized = path.as_posix()
        if normalized in seen:
            raise IsolatedEvalError("duplicate Git path in snapshot: %s" % normalized)
        seen.add(normalized)
        decoded.append(normalized)
    return sorted(decoded)


def _open_source(path):
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise IsolatedEvalError("cannot open snapshot source %s: %s" % (path, exc)) from exc
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode):
        os.close(descriptor)
        raise IsolatedEvalError("snapshot source is not a regular file: %s" % path)
    return descriptor, metadata


def _copy_stable_file(source, target, remaining_bytes):
    source_fd, before = _open_source(source)
    if (
            not isinstance(remaining_bytes, int) or isinstance(remaining_bytes, bool)
            or remaining_bytes < 0):
        os.close(source_fd)
        raise IsolatedEvalError("snapshot remaining-byte budget is invalid")
    if before.st_size > remaining_bytes:
        os.close(source_fd)
        raise IsolatedEvalError(
            "snapshot source %s exceeds remaining %d-byte budget before copy"
            % (source, remaining_bytes)
        )
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = (
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        target_fd = os.open(target, flags, 0o600)
    except OSError as exc:
        os.close(source_fd)
        raise IsolatedEvalError("cannot create snapshot target %s: %s" % (target, exc)) from exc
    digest = hashlib.sha256()
    copied = 0
    try:
        while True:
            chunk = os.read(source_fd, COPY_CHUNK_BYTES)
            if not chunk:
                break
            if len(chunk) > remaining_bytes - copied:
                raise IsolatedEvalError(
                    "snapshot source exceeded its streaming byte budget while copied: %s"
                    % source
                )
            offset = 0
            while offset < len(chunk):
                offset += os.write(target_fd, chunk[offset:])
            digest.update(chunk)
            copied += len(chunk)
        after = os.fstat(source_fd)
        if copied != before.st_size or any(
                getattr(before, field) != getattr(after, field) for field in IDENTITY_FIELDS):
            raise IsolatedEvalError("snapshot source changed while copied: %s" % source)
        mode = stat.S_IMODE(before.st_mode) & 0o777
        os.fchmod(target_fd, mode)
        os.fsync(target_fd)
    finally:
        os.close(source_fd)
        os.close(target_fd)
    installed = os.lstat(target)
    if (
            not stat.S_ISREG(installed.st_mode) or stat.S_ISLNK(installed.st_mode)
            or installed.st_nlink != 1 or installed.st_size != copied):
        raise IsolatedEvalError("snapshot target is not a stable single-link file: %s" % target)
    return {"sha256": digest.hexdigest(), "size_bytes": copied, "mode": "%04o" % mode}


def _initialize_snapshot_git(stage_root, git_context):
    # Keep Git's mutable object database beside the staged worktree.  A number
    # of repository checks recursively walk the source root; putting loose Git
    # objects under that root creates a race with Git's automatic object
    # maintenance and can make an otherwise read-only walk observe a directory
    # disappearing.  The worktree still has a normal `.git` marker file and all
    # Git commands behave normally.
    git_metadata = stage_root.parent / (".%s-git-metadata" % stage_root.name)
    init = _run(
        [
            "git", *git_context["config_arguments"], "init", "--quiet",
            "--template", git_context["template"],
            "--separate-git-dir", str(git_metadata),
            str(stage_root),
        ],
        cwd=stage_root.parent,
        environment=git_context["environment"],
    )
    if init.returncode:
        raise IsolatedEvalError(
            "cannot initialize isolated Git metadata: %s"
            % (init.stderr.decode("utf-8", "replace").strip() or init.returncode)
        )
    _git(stage_root, "config", "gc.auto", "0", git_context=git_context)
    _git(stage_root, "config", "maintenance.auto", "false", git_context=git_context)
    _git(
        stage_root, "config", "user.name", "Isolated Eval Snapshot",
        git_context=git_context,
    )
    _git(
        stage_root,
        "config",
        "user.email",
        "isolated-eval" + "@" + "example.invalid",
        git_context=git_context,
    )
    _git(stage_root, "add", "-A", git_context=git_context)
    _git(
        stage_root, "-c", "commit.gpgsign=false", "commit", "--quiet", "--no-verify",
        "-m", "isolated evaluation snapshot",
        git_context=git_context,
    )
    status = _git(
        stage_root, "status", "--porcelain=v1", "--untracked-files=all",
        git_context=git_context,
    )
    if status.stdout:
        raise IsolatedEvalError("isolated evaluation snapshot is not clean after commit")


def stage_repository(source_root, stage_root):
    """Copy the current Git worktree into ``stage_root`` and return provenance."""
    source_root = Path(source_root).resolve(strict=True)
    stage_root = Path(stage_root)
    if stage_root.exists():
        raise IsolatedEvalError("stage destination already exists: %s" % stage_root)
    stage_root.mkdir(parents=True, mode=0o700)
    stage_root = stage_root.resolve(strict=True)
    git_context = _private_git_context(stage_root.parent, stage_root.name)
    paths = _snapshot_paths(source_root, git_context)
    identities = {}
    total = 0
    for relative in paths:
        source = source_root / relative
        # A tracked deletion is intentionally absent from the snapshot.
        if not source.exists() and not source.is_symlink():
            continue
        identity = _copy_stable_file(
            source, stage_root / relative, MAX_SNAPSHOT_BYTES - total
        )
        total += identity["size_bytes"]
        if total > MAX_SNAPSHOT_BYTES:
            raise IsolatedEvalError(
                "snapshot exceeds %d bytes" % MAX_SNAPSHOT_BYTES
            )
        identities[relative] = identity
    if "scripts/run-behavior-evals.py" not in identities:
        raise IsolatedEvalError("snapshot is missing scripts/run-behavior-evals.py")
    _initialize_snapshot_git(stage_root, git_context)
    aggregate = hashlib.sha256()
    for relative in sorted(identities):
        aggregate.update(relative.encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(identities[relative]["sha256"].encode("ascii"))
        aggregate.update(b"\0")
        aggregate.update(identities[relative]["mode"].encode("ascii"))
        aggregate.update(b"\n")
    return {
        "schema_version": "1.0",
        "source_root": str(source_root),
        "file_count": len(identities),
        "total_bytes": total,
        "aggregate_sha256": aggregate.hexdigest(),
        "files": identities,
    }


def _python_candidates(explicit=None):
    raw = []
    if explicit:
        raw.append(
            shutil.which(explicit)
            if not Path(explicit).is_absolute() and os.sep not in explicit
            else explicit
        )
    else:
        raw.extend((sys.executable, shutil.which("python3")))
        for name in ("python3.13", "python3.12", "python3.11", "python3.10", "python3.9"):
            raw.append(shutil.which(name))
    seen = set()
    for value in raw:
        if not value:
            continue
        try:
            path = Path(value).resolve(strict=True)
        except OSError:
            continue
        if path in seen:
            continue
        seen.add(path)
        yield path


def select_single_link_python(explicit=None):
    diagnostics = []
    for path in _python_candidates(explicit):
        try:
            metadata = os.stat(path)
        except OSError as exc:
            diagnostics.append("%s (%s)" % (path, exc))
            continue
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            diagnostics.append("%s (link-count %d)" % (path, metadata.st_nlink))
            continue
        probe = _run(
            [str(path), "-I", "-S", "-c", "import sys; assert sys.flags.isolated"],
            cwd=path.parent,
            timeout=15,
        )
        if probe.returncode == 0:
            return path
        diagnostics.append(
            "%s (probe exit %d)" % (path, probe.returncode)
        )
    detail = "; ".join(diagnostics) or "no Python candidates found"
    raise IsolatedEvalError(
        "a working single-link Python interpreter is required; use --python with "
        "an explicit interpreter (%s)" % detail
    )


def run_isolated(source_root, temp_root, eval_arguments, *, python=None):
    temp_root = Path(temp_root).resolve(strict=True)
    stage_root = temp_root / "repository"
    provenance = stage_repository(source_root, stage_root)
    interpreter = select_single_link_python(python)
    command = [
        str(interpreter), str(stage_root / "scripts" / "run-behavior-evals.py"),
        *eval_arguments,
    ]
    print(
        "Isolated snapshot: %d files, %d bytes, sha256=%s"
        % (
            provenance["file_count"], provenance["total_bytes"],
            provenance["aggregate_sha256"],
        )
    )
    print("Single-link Python: %s" % interpreter)
    print("Staged repository: %s" % stage_root)
    sys.stdout.flush()
    environment = os.environ.copy()
    # Deterministic suites intentionally launch child Python fixtures by the
    # portable name `python3`. Put the already-validated interpreter directory
    # first so those children cannot fall back to a multiply-linked system stub
    # (notably `/usr/bin/python3` on macOS) and fail before the behavior under
    # test is reached.
    environment["PATH"] = str(interpreter.parent) + os.pathsep + environment.get("PATH", "")
    try:
        return subprocess.run(
            command, cwd=stage_root, env=environment, check=False,
        ).returncode, provenance
    except OSError as exc:
        raise IsolatedEvalError("cannot execute isolated behavior suites: %s" % exc) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python", help="explicit single-link Python interpreter for the staged run",
    )
    parser.add_argument(
        "--stage-parent", help="existing private directory in which to create the stage",
    )
    parser.add_argument(
        "--keep-stage", action="store_true", help="retain and print the staged repository",
    )
    parser.add_argument(
        "eval_arguments", nargs=argparse.REMAINDER,
        help="arguments after -- are forwarded to run-behavior-evals.py",
    )
    args = parser.parse_args(argv)
    eval_arguments = list(args.eval_arguments)
    if eval_arguments and eval_arguments[0] == "--":
        eval_arguments.pop(0)
    parent = None
    if args.stage_parent:
        supplied_parent = Path(args.stage_parent)
        if supplied_parent.is_symlink():
            print("isolated-evals: --stage-parent must be a real directory", file=sys.stderr)
            return 2
        parent = supplied_parent.resolve(strict=True)
        if not parent.is_dir():
            print("isolated-evals: --stage-parent must be a real directory", file=sys.stderr)
            return 2
        try:
            parent.relative_to(ROOT)
        except ValueError:
            pass
        else:
            print(
                "isolated-evals: --stage-parent must be outside the source repository",
                file=sys.stderr,
            )
            return 2
    temp_root = Path(tempfile.mkdtemp(prefix="aaron-isolated-evals-", dir=parent)).resolve()
    temp_root.chmod(0o700)
    try:
        status, provenance = run_isolated(
            ROOT, temp_root, eval_arguments, python=args.python,
        )
        provenance_path = temp_root / "snapshot-provenance.json"
        provenance_path.write_text(
            json.dumps(provenance, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        provenance_path.chmod(0o600)
        if args.keep_stage:
            print("Retained isolated evaluation tree: %s" % temp_root)
            temp_root = None
        return status
    except (IsolatedEvalError, OSError, ValueError) as exc:
        print("isolated-evals: %s" % exc, file=sys.stderr)
        return 2
    finally:
        if temp_root is not None:
            # Git maintenance is disabled in the isolated snapshot, but a
            # platform process can still make an already-enumerated temporary
            # entry disappear. Cleanup is best-effort for this exact mkdtemp
            # path and must not turn a successful evaluation into a false fail.
            shutil.rmtree(temp_root, ignore_errors=True)
            if temp_root.exists():
                print(
                    "isolated-evals: warning: temporary stage cleanup was incomplete: %s"
                    % temp_root,
                    file=sys.stderr,
                )


if __name__ == "__main__":
    raise SystemExit(main())
