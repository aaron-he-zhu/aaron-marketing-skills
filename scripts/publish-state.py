#!/usr/bin/env python3
"""Private, repository/version/commit-scoped resume state for registry publishers."""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import stat
import sys
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - live publishing is POSIX-only
    fcntl = None


MAX_STATE_BYTES = 1_000_000
MAX_STATE_ENTRIES = 20_000
SAFE_REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SAFE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
SAFE_COMMIT = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:._/-]{0,511}$")


class StateError(ValueError):
    pass


def _default_state_root():
    configured = os.environ.get("XDG_STATE_HOME")
    if configured:
        return Path(configured) / "aaron-marketing-skills" / "publish-registries"
    return Path.home() / ".local" / "state" / "aaron-marketing-skills" / "publish-registries"


def _ensure_real_directory(path, *, private=False):
    """Create/open the selected directory without following its final component.

    Ancestors are intentionally left to the OS: macOS exposes temporary paths
    through ``/var`` -> ``/private/var`` and rejecting that platform alias makes
    every secure temporary state root unusable.  The state root itself, each
    repository scope, and every state/lock file are still opened fail-closed
    with ``O_NOFOLLOW``.
    """
    path = path.expanduser().absolute()
    try:
        path.mkdir(mode=0o700, parents=True, exist_ok=True)
        before = path.lstat()
    except OSError as exc:
        raise StateError("cannot create or inspect state directory %s: %s" % (path, exc)) from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise StateError("state path component is not a real directory: %s" % path)

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise StateError("cannot safely open state directory %s: %s" % (path, exc)) from exc
    try:
        opened = os.fstat(descriptor)
        if (not stat.S_ISDIR(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
            raise StateError("state directory changed while opening: %s" % path)
        if hasattr(opened, "st_uid") and opened.st_uid != os.getuid():
            raise StateError("state directory is not owned by the current user: %s" % path)
        if private:
            os.fchmod(descriptor, 0o700)
    except OSError as exc:
        raise StateError("cannot make state directory private: %s" % exc) from exc
    finally:
        os.close(descriptor)
    return path


def state_paths(repository, version, commit, state_root=None):
    if not SAFE_REPOSITORY.fullmatch(repository):
        raise StateError("repository must be an owner/repository slug")
    if not SAFE_VERSION.fullmatch(version):
        raise StateError("version must be semantic version text")
    if not SAFE_COMMIT.fullmatch(commit):
        raise StateError("commit must be a lowercase 40- or 64-hex object ID")
    root = _ensure_real_directory(state_root or _default_state_root(), private=True)
    scope = hashlib.sha256(repository.encode("utf-8")).hexdigest()[:24]
    directory = _ensure_real_directory(root / scope, private=True)
    release = "%s-%s" % (version, commit)
    state = directory / (release + ".state")
    lock = directory / (release + ".lock")
    return directory, state, lock


def _open_lock(path):
    if fcntl is None:
        raise StateError("publisher state requires POSIX advisory locking")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(path, flags, 0o600)
    except OSError as exc:
        raise StateError("cannot open publisher state lock: %s" % exc) from exc
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        os.close(descriptor)
        raise StateError("publisher state lock must be a single-link regular file")
    if hasattr(metadata, "st_uid") and metadata.st_uid != os.getuid():
        os.close(descriptor)
        raise StateError("publisher state lock is not owned by the current user")
    os.fchmod(descriptor, 0o600)
    return descriptor


def _read_state(path):
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return []
    except OSError as exc:
        raise StateError("cannot inspect publisher state: %s" % exc) from exc
    if (stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1):
        raise StateError("publisher state must be a single-link regular file")
    if hasattr(metadata, "st_uid") and metadata.st_uid != os.getuid():
        raise StateError("publisher state is not owned by the current user")
    if metadata.st_size > MAX_STATE_BYTES:
        raise StateError("publisher state exceeds the bounded size limit")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino)):
            raise StateError("publisher state changed while opening")
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            raw = handle.read(MAX_STATE_BYTES + 1)
    except StateError:
        raise
    except OSError as exc:
        raise StateError("cannot read publisher state: %s" % exc) from exc
    if len(raw) > MAX_STATE_BYTES:
        raise StateError("publisher state exceeds the bounded size limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise StateError("publisher state is not UTF-8") from exc
    entries = text.splitlines()
    if len(entries) > MAX_STATE_ENTRIES:
        raise StateError("publisher state exceeds the bounded entry limit")
    if len(entries) != len(set(entries)):
        raise StateError("publisher state contains duplicate entries")
    if any(not SAFE_KEY.fullmatch(entry) for entry in entries):
        raise StateError("publisher state contains an invalid entry")
    return entries


def _atomic_write(directory, path, entries):
    content = ("\n".join(entries) + ("\n" if entries else "")).encode("utf-8")
    if len(content) > MAX_STATE_BYTES:
        raise StateError("publisher state exceeds the bounded size limit")
    temporary = directory / (".%s.%s.%s.tmp" % (path.name, os.getpid(), uuid.uuid4().hex))
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(temporary, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            os.fchmod(handle.fileno(), 0o600)
        os.replace(temporary, path)
        directory_descriptor = os.open(
            directory, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    except OSError as exc:
        if descriptor is not None:
            os.close(descriptor)
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass
        raise StateError("cannot atomically update publisher state: %s" % exc) from exc


def operate(repository, version, commit, operation, key=None, state_root=None):
    directory, state_path, lock_path = state_paths(repository, version, commit, state_root)
    if operation in {"has", "mark"} and (not isinstance(key, str) or not SAFE_KEY.fullmatch(key)):
        raise StateError("state key must be a bounded safe identifier")
    lock_descriptor = _open_lock(lock_path)
    try:
        fcntl.flock(
            lock_descriptor,
            fcntl.LOCK_EX if operation == "mark" else fcntl.LOCK_SH,
        )
        entries = _read_state(state_path)
        if operation == "path":
            return str(state_path)
        if operation == "has":
            return key in entries
        if key not in entries:
            if len(entries) >= MAX_STATE_ENTRIES:
                raise StateError("publisher state exceeds the bounded entry limit")
            _atomic_write(directory, state_path, entries + [key])
        return True
    finally:
        try:
            fcntl.flock(lock_descriptor, fcntl.LOCK_UN)
        finally:
            os.close(lock_descriptor)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--state-root", type=Path)
    subcommands = parser.add_subparsers(dest="operation", required=True)
    subcommands.add_parser("path")
    for operation in ("has", "mark"):
        command = subcommands.add_parser(operation)
        command.add_argument("key")
    args = parser.parse_args(argv)
    try:
        result = operate(
            args.repo, args.version, args.commit, args.operation,
            getattr(args, "key", None), args.state_root,
        )
    except StateError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if args.operation == "path":
        print(result)
    if args.operation == "has" and not result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
