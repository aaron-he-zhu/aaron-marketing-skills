#!/usr/bin/env python3
"""Resolve explicit bundle/project context into a bounded immutable manifest.

The resolver performs no natural-language inference and copies no source bodies.
It validates a caller-supplied route and candidate set, reads regular files through
directory descriptors, and emits only hashes, byte counts, provenance, conflicts,
and omission reasons. Python 3 standard library only.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat as statmod
import subprocess
import sys
import uuid


SCHEMA_VERSION = "1.0"
MAX_REQUEST_BYTES = 1_000_000
MAX_MANIFEST_BYTES = 2_000_000
MAX_CONTEXT_BYTES = 10_000_000
MAX_INSPECTION_BYTES = 64_000_000
MAX_CANDIDATES = 256
SKILL_CONTRACT_TREE = "references/skill-contracts"
SKILL_CONTRACT_PACK = "references/skill-contracts.pack.json.gz"
SKILL_CONTRACT_PACK_MAX_BYTES = 1_000_000
SKILL_CONTRACT_PACK_MAX_EXPANDED_BYTES = 5_000_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_PATH = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,511}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
CATALOG_SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
SKILL_SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
REGISTRIES = {
    "entities", "creators", "claims", "consent", "launches", "channels", "narrative",
}
COMMANDS = {"auto", "narrative", "seo-geo", "social", "email", "ad", "influencer", "launch"}
REQUIREMENTS = {"required", "optional", "forbidden"}
AUTHORITIES = {"canonical", "approved", "working", "untrusted"}
AUTHORITY_RANK = {"canonical": 0, "approved": 1, "working": 2, "untrusted": 3}
SENSITIVITIES = {"public", "internal", "confidential", "restricted"}
SENSITIVITY_RANK = {"public": 0, "internal": 1, "confidential": 2, "restricted": 3}
ALLOWED_SHARDS = {
    "references/auto-routing/narrative.md",
    "references/auto-routing/seo-geo.md",
    "references/auto-routing/social.md",
    "references/auto-routing/email.md",
    "references/auto-routing/ad.md",
    "references/auto-routing/influencer.md",
    "references/auto-routing/launch.md",
    "references/auto-routing/cross-discipline.md",
}
OMISSION_REASONS = {
    "forbidden", "missing", "stale", "sensitivity-budget", "hash-mismatch",
    "duplicate-content", "superseded", "byte-budget", "resource-budget",
    "inspection-budget",
}


class ContextResolutionError(ValueError):
    """A closed validation or resolution failure."""


class ContextSourceMissing(ContextResolutionError):
    """A source path was absent (distinct from an unsafe path)."""


class ContextSourceTooLarge(ContextResolutionError):
    """A source cannot fit the request's per-resource byte ceiling."""

    def __init__(self, path, size, limit):
        super().__init__("context source %s is %d bytes (limit %d)" % (path, size, limit))
        self.size = size
        self.limit = limit


class ContextInspectionBudgetExceeded(ContextResolutionError):
    """A stable double-read would exceed the request's aggregate work ceiling."""

    def __init__(self, path, required, remaining):
        super().__init__(
            "context source %s requires %d inspection bytes (%d remain)"
            % (path, required, remaining)
        )
        self.required = required
        self.remaining = remaining


def strict_json_loads(value, label="JSON"):
    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate key: %s" % key)
            result[key] = item
        return result

    try:
        return json.loads(
            value,
            object_pairs_hook=unique_object,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % constant)
            ),
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise ContextResolutionError("%s must be strict JSON: %s" % (label, exc)) from exc


def canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ContextResolutionError("value must contain finite JSON data: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def exact_object(value, required, optional, label):
    if not isinstance(value, dict):
        raise ContextResolutionError("%s must be an object" % label)
    missing = sorted(set(required) - set(value))
    extra = sorted(set(value) - set(required) - set(optional))
    if missing:
        raise ContextResolutionError("%s is missing fields: %s" % (label, ", ".join(missing)))
    if extra:
        raise ContextResolutionError("%s has unknown fields: %s" % (label, ", ".join(extra)))
    return value


def validate_int(value, label, minimum, maximum):
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise ContextResolutionError(
            "%s must be an integer from %d through %d" % (label, minimum, maximum)
        )
    return value


def validate_uuid(value, label):
    if not isinstance(value, str):
        raise ContextResolutionError("%s must be a UUID string" % label)
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise ContextResolutionError("%s must be a UUID string" % label) from exc
    if str(parsed) != value:
        raise ContextResolutionError("%s must use canonical lowercase UUID form" % label)
    if parsed.variant != uuid.RFC_4122 or parsed.version not in set(range(1, 9)):
        raise ContextResolutionError("%s must be a canonical RFC UUID version 1 through 8" % label)
    return value


def validate_safe_id(value, label):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ContextResolutionError("%s must be a non-PII safe identifier" % label)
    return value


def validate_sha(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ContextResolutionError("%s must be a lowercase SHA-256 digest" % label)
    return value


def validate_enum(value, allowed, label):
    if not isinstance(value, str) or value not in allowed:
        raise ContextResolutionError("%s is unsupported" % label)
    return value


def validate_relative_path(value, label):
    if not isinstance(value, str):
        raise ContextResolutionError("%s must be a project-relative path" % label)
    parts = value.split("/")
    if (
            value.startswith("/") or not SAFE_PATH.fullmatch(value)
            or any(part in {"", ".", ".."} for part in parts)):
        raise ContextResolutionError(
            "%s must not be absolute or contain empty/dot path components" % label
        )
    return value


def parse_datetime(value, label):
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise ContextResolutionError("%s must be an RFC 3339 date-time" % label)
    try:
        normalized = value.replace("t", "T").replace("z", "+00:00").replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ContextResolutionError("%s must be an RFC 3339 date-time" % label) from exc
    if parsed.tzinfo is None:
        raise ContextResolutionError("%s must include a timezone" % label)
    return parsed.astimezone(dt.timezone.utc)


def validate_offsets(value, label="registry_offsets"):
    exact_object(value, REGISTRIES, set(), label)
    for name, offset in value.items():
        if offset is not None:
            validate_int(offset, "%s.%s" % (label, name), 0, 2**63 - 1)
    return value


def _lstat(path, label, missing_ok=False):
    try:
        return os.lstat(path)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise ContextSourceMissing("%s does not exist: %s" % (label, path))
    except OSError as exc:
        raise ContextResolutionError("cannot inspect %s %s: %s" % (label, path, exc)) from exc


def normalized_root(root, label):
    supplied = Path(root)
    status = _lstat(supplied, label)
    if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISDIR(status.st_mode):
        raise ContextResolutionError("%s must be a real directory" % label)
    try:
        return supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ContextResolutionError("cannot resolve %s: %s" % (label, exc)) from exc


def has_git_marker(path):
    for candidate in (path, *path.parents):
        if _lstat(candidate / ".git", "Git marker", missing_ok=True) is not None:
            return True
    return False


def ensure_ignored(root, relatives):
    """Require private output paths to be ignored when the project is in Git."""
    try:
        probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        if has_git_marker(root):
            raise ContextResolutionError("cannot verify context-manifest privacy: %s" % exc) from exc
        return
    if probe.returncode != 0:
        if has_git_marker(root):
            raise ContextResolutionError("cannot verify context-manifest privacy: git rev-parse failed")
        return
    git_root = Path(probe.stdout.strip()).resolve()
    for relative in relatives:
        target = root.joinpath(*relative.split("/"))
        try:
            git_relative = target.absolute().relative_to(git_root)
        except ValueError as exc:
            raise ContextResolutionError("context manifest escapes the Git worktree") from exc
        try:
            checked = subprocess.run(
                ["git", "-C", str(git_root), "check-ignore", "--quiet", "--", str(git_relative)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ContextResolutionError("cannot verify context-manifest privacy: %s" % exc) from exc
        if checked.returncode != 0:
            raise ContextResolutionError(
                "refusing context-manifest write because %s is not Git-ignored" % git_relative
            )


def _open_root(root, label):
    root_path = normalized_root(root, label)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = None
    try:
        descriptor = os.open(os.path.sep, flags)
        for component in root_path.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
    except OSError as exc:
        if descriptor is not None:
            os.close(descriptor)
        raise ContextResolutionError("cannot anchor %s %s: %s" % (label, root_path, exc)) from exc
    opened = os.fstat(descriptor)
    return root_path, descriptor, (opened.st_dev, opened.st_ino)


def _entry_stat(parent_fd, name, label, missing_ok=False):
    try:
        return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise ContextSourceMissing("%s does not exist" % label)
    except OSError as exc:
        raise ContextResolutionError("cannot inspect %s: %s" % (label, exc)) from exc


def _same_entry(opened, entry):
    return (opened.st_dev, opened.st_ino) == (entry.st_dev, entry.st_ino)


def _read_fd(fd, limit):
    os.lseek(fd, 0, os.SEEK_SET)
    chunks = []
    total = 0
    while True:
        chunk = os.read(fd, min(1024 * 1024, limit + 1 - total))
        if not chunk:
            break
        chunks.append(chunk)
        total += len(chunk)
        if total > limit:
            break
    return b"".join(chunks)


def _anchored_file_read(root, relative, limit, root_label="context root",
                        inspection_limit=None, return_metadata=False):
    """Read a stable single-link regular file below a directory descriptor."""
    validate_relative_path(relative, "context path")
    root_path, root_fd, root_identity = _open_root(root, root_label)
    descriptors = [root_fd]
    links = []
    file_fd = None
    parts = relative.split("/")
    try:
        parent_fd = root_fd
        parent_path = root_path
        directory_flags = (
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        )
        for component in parts[:-1]:
            child_fd = None
            try:
                child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
                opened = os.fstat(child_fd)
                entry = _entry_stat(parent_fd, component, "context directory")
                if (
                        not statmod.S_ISDIR(opened.st_mode) or statmod.S_ISLNK(entry.st_mode)
                        or not _same_entry(opened, entry)):
                    raise ContextResolutionError(
                        "context directory changed or is unsafe: %s" % (parent_path / component)
                    )
                links.append((parent_fd, component, (opened.st_dev, opened.st_ino)))
                descriptors.append(child_fd)
            except FileNotFoundError as exc:
                if child_fd is not None:
                    os.close(child_fd)
                raise ContextSourceMissing(
                    "context source does not exist: %s" % (parent_path / component)
                ) from exc
            except OSError as exc:
                if child_fd is not None:
                    os.close(child_fd)
                raise ContextResolutionError(
                    "context directory is not a safe real directory: %s" % (parent_path / component)
                ) from exc
            except Exception:
                if child_fd is not None and child_fd not in descriptors:
                    os.close(child_fd)
                raise
            parent_fd = child_fd
            parent_path = parent_path / component

        name = parts[-1]
        pre_open = _entry_stat(parent_fd, name, "context source")
        if (
                statmod.S_ISLNK(pre_open.st_mode) or not statmod.S_ISREG(pre_open.st_mode)
                or pre_open.st_nlink != 1):
            raise ContextResolutionError(
                "context source must be a stable single-link regular file: %s" % (parent_path / name)
            )
        flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        )
        try:
            file_fd = os.open(name, flags, dir_fd=parent_fd)
        except FileNotFoundError as exc:
            raise ContextSourceMissing(
                "context source does not exist: %s" % (parent_path / name)
            ) from exc
        except OSError as exc:
            raise ContextResolutionError(
                "context source is not a safe regular file: %s" % (parent_path / name)
            ) from exc
        before = os.fstat(file_fd)
        entry = _entry_stat(parent_fd, name, "context source")
        if (
                not statmod.S_ISREG(before.st_mode) or before.st_nlink != 1
                or statmod.S_ISLNK(entry.st_mode) or not _same_entry(before, entry)):
            raise ContextResolutionError(
                "context source must be a stable single-link regular file: %s" % (parent_path / name)
            )
        if not _same_entry(before, pre_open):
            raise ContextResolutionError(
                "context source changed during inspection: %s" % relative
            )
        if before.st_size > limit:
            raise ContextSourceTooLarge(relative, before.st_size, limit)
        inspection_bytes = before.st_size * 2
        if inspection_limit is not None and inspection_bytes > inspection_limit:
            raise ContextInspectionBudgetExceeded(
                relative, inspection_bytes, inspection_limit,
            )
        first = _read_fd(file_fd, limit)
        if len(first) > limit:
            raise ContextSourceTooLarge(relative, len(first), limit)
        second = _read_fd(file_fd, limit)
        after = os.fstat(file_fd)
        if first != second or (
                before.st_dev, before.st_ino, before.st_nlink, before.st_size,
                before.st_mtime_ns, before.st_ctime_ns,
        ) != (
                after.st_dev, after.st_ino, after.st_nlink, after.st_size,
                after.st_mtime_ns, after.st_ctime_ns,
        ):
            raise ContextResolutionError("context source changed during inspection: %s" % relative)
        current = _entry_stat(parent_fd, name, "context source")
        if not _same_entry(after, current) or current.st_nlink != 1:
            raise ContextResolutionError("context source changed during inspection: %s" % relative)
        for ancestor_fd, component, identity in reversed(links):
            current = _entry_stat(ancestor_fd, component, "context directory")
            if statmod.S_ISLNK(current.st_mode) or (current.st_dev, current.st_ino) != identity:
                raise ContextResolutionError("context directory changed during inspection")
        root_now = _lstat(root_path, root_label)
        if (
                statmod.S_ISLNK(root_now.st_mode) or not statmod.S_ISDIR(root_now.st_mode)
                or (root_now.st_dev, root_now.st_ino) != root_identity):
            raise ContextResolutionError("%s changed during inspection" % root_label)
        if return_metadata:
            return first, after
        return first
    finally:
        if file_fd is not None:
            os.close(file_fd)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


_COMPACT_CONTRACT_CACHE = {}


def _compact_contract_files(root, root_label):
    compressed = _anchored_file_read(
        root,
        SKILL_CONTRACT_PACK,
        SKILL_CONTRACT_PACK_MAX_BYTES,
        root_label,
    )
    normalized = normalized_root(root, root_label)
    key = (str(normalized), hashlib.sha256(compressed).hexdigest())
    cached = _COMPACT_CONTRACT_CACHE.get(key)
    if cached is not None:
        return cached
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as handle:
            expanded = handle.read(SKILL_CONTRACT_PACK_MAX_EXPANDED_BYTES + 1)
    except (OSError, EOFError) as exc:
        raise ContextResolutionError(
            "compact skill-contract pack is not valid gzip: %s" % exc
        ) from exc
    if len(expanded) > SKILL_CONTRACT_PACK_MAX_EXPANDED_BYTES:
        raise ContextResolutionError(
            "compact skill-contract pack exceeds the expanded-byte limit"
        )
    try:
        pack = strict_json_loads(
            expanded.decode("utf-8"), "compact skill-contract pack"
        )
    except UnicodeDecodeError as exc:
        raise ContextResolutionError(
            "compact skill-contract pack must contain UTF-8 JSON"
        ) from exc
    exact_object(
        pack,
        {
            "schema_version", "encoding", "source_tree", "file_count",
            "files_sha256", "files",
        },
        set(),
        "compact skill-contract pack",
    )
    if (
            pack["schema_version"] != "1.0"
            or pack["encoding"] != "canonical-json-v1"
            or pack["source_tree"] != SKILL_CONTRACT_TREE
            or pack["file_count"] != 121
            or not isinstance(pack["files"], list)
            or len(pack["files"]) != pack["file_count"]):
        raise ContextResolutionError(
            "compact skill-contract pack identity/count is invalid"
        )
    validate_sha(pack["files_sha256"], "compact skill-contract files_sha256")
    files = {}
    descriptors = []
    for position, item in enumerate(pack["files"]):
        label = "compact skill-contract pack.files[%d]" % position
        exact_object(
            item,
            {"path", "bytes", "sha256", "content"},
            set(),
            label,
        )
        path = validate_relative_path(item["path"], label + ".path")
        if (
                not path.startswith(SKILL_CONTRACT_TREE + "/")
                or not path.endswith(".json")):
            raise ContextResolutionError(
                "%s path is outside the machine-contract tree" % label
            )
        if path in files:
            raise ContextResolutionError(
                "compact skill-contract pack contains duplicate path %s" % path
            )
        size = validate_int(
            item["bytes"], label + ".bytes", 1, MAX_CONTEXT_BYTES
        )
        validate_sha(item["sha256"], label + ".sha256")
        if not isinstance(item["content"], dict):
            raise ContextResolutionError(
                "%s.content must be an object" % label
            )
        try:
            content = (
                json.dumps(
                    item["content"],
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=2,
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8")
        except (TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise ContextResolutionError(
                "%s.content cannot be canonically encoded" % label
            ) from exc
        if len(content) != size or hashlib.sha256(content).hexdigest() != item["sha256"]:
            raise ContextResolutionError(
                "%s content differs from its size/hash" % label
            )
        files[path] = content
        descriptors.append({
            "path": path,
            "bytes": size,
            "sha256": item["sha256"],
        })
    if "%s/index.json" % SKILL_CONTRACT_TREE not in files:
        raise ContextResolutionError(
            "compact skill-contract pack has no index"
        )
    if sha256_json(descriptors) != pack["files_sha256"]:
        raise ContextResolutionError(
            "compact skill-contract pack aggregate hash is invalid"
        )
    if len(_COMPACT_CONTRACT_CACHE) >= 4:
        _COMPACT_CONTRACT_CACHE.clear()
    _COMPACT_CONTRACT_CACHE[key] = files
    return files


def anchored_read(root, relative, limit, root_label="context root", inspection_limit=None,
                  return_metadata=False):
    """Read a real file, or one exact machine-contract member from its pack."""
    try:
        return _anchored_file_read(
            root, relative, limit, root_label,
            inspection_limit=inspection_limit,
            return_metadata=return_metadata,
        )
    except ContextSourceMissing as original:
        if not relative.startswith(SKILL_CONTRACT_TREE + "/"):
            raise
        try:
            files = _compact_contract_files(root, root_label)
        except ContextSourceMissing:
            raise original
        try:
            content = files[relative]
        except KeyError as exc:
            raise ContextSourceMissing(
                "context source is absent from compact skill-contract pack: %s"
                % relative
            ) from exc
        if return_metadata:
            raise ContextResolutionError(
                "compact skill-contract members do not expose filesystem metadata"
            )
        if len(content) > limit:
            raise ContextSourceTooLarge(relative, len(content), limit)
        inspection_bytes = len(content) * 2
        if inspection_limit is not None and inspection_bytes > inspection_limit:
            raise ContextInspectionBudgetExceeded(
                relative, inspection_bytes, inspection_limit
            )
        return content


def read_json_document(path, label, limit):
    path = Path(path)
    root = path.parent if str(path.parent) else Path(".")
    raw = anchored_read(root, path.name, limit, label + " parent")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextResolutionError("%s must be UTF-8" % label) from exc
    return strict_json_loads(text, label)


def _validate_route(value, label, manifest=False):
    required = {"command", "target_skill", "reason_code", "scenario_shards"}
    if manifest:
        required |= {"catalog_version", "catalog_sha256", "skill_version", "skill_sha256"}
    exact_object(value, required, set(), label)
    validate_enum(value["command"], COMMANDS, label + ".command")
    validate_safe_id(value["target_skill"], label + ".target_skill")
    validate_safe_id(value["reason_code"], label + ".reason_code")
    shards = value["scenario_shards"]
    if not isinstance(shards, list):
        raise ContextResolutionError("%s.scenario_shards must be a unique array" % label)
    for index, shard in enumerate(shards):
        validate_relative_path(shard, "%s.scenario_shards[%d]" % (label, index))
        if shard not in ALLOWED_SHARDS:
            raise ContextResolutionError("%s.scenario_shards[%d] is not allowed" % (label, index))
    if len(shards) != len(set(shards)):
        raise ContextResolutionError("%s.scenario_shards must be a unique array" % label)
    if value["command"] == "auto":
        if not 1 <= len(shards) <= 3:
            raise ContextResolutionError("/auto requires one to three scenario shards")
        primary_shards = [shard for shard in shards if not shard.endswith("/cross-discipline.md")]
        has_cross = any(shard.endswith("/cross-discipline.md") for shard in shards)
        if not primary_shards:
            raise ContextResolutionError("/auto requires one primary discipline shard")
        if len(primary_shards) > 2:
            raise ContextResolutionError("/auto permits at most two primary discipline shards")
        if len(primary_shards) == 2 and not has_cross:
            raise ContextResolutionError(
                "/auto requires the cross-discipline shard for a two-discipline route"
            )
    elif shards:
        raise ContextResolutionError("only /auto may declare scenario shards")
    if manifest:
        if not isinstance(value["catalog_version"], str) or not CATALOG_SEMVER.fullmatch(
                value["catalog_version"]):
            raise ContextResolutionError("%s.catalog_version must be semver" % label)
        if not isinstance(value["skill_version"], str) or not SKILL_SEMVER.fullmatch(
                value["skill_version"]):
            raise ContextResolutionError("%s.skill_version must be semver" % label)
        validate_sha(value["catalog_sha256"], label + ".catalog_sha256")
        validate_sha(value["skill_sha256"], label + ".skill_sha256")
    return value


def _validate_budget(value, label="budget", manifest=False):
    required = {"max_bytes", "max_resources", "max_sensitivity", "max_inspection_bytes"}
    if manifest:
        required |= {"selected_bytes", "selected_resources", "inspected_bytes"}
    exact_object(value, required, set(), label)
    validate_int(value["max_bytes"], label + ".max_bytes", 1, MAX_CONTEXT_BYTES)
    validate_int(value["max_resources"], label + ".max_resources", 1, MAX_CANDIDATES)
    validate_int(
        value["max_inspection_bytes"], label + ".max_inspection_bytes",
        1, MAX_INSPECTION_BYTES,
    )
    validate_enum(value["max_sensitivity"], SENSITIVITIES, label + ".max_sensitivity")
    if manifest:
        validate_int(value["selected_bytes"], label + ".selected_bytes", 0, MAX_CONTEXT_BYTES)
        validate_int(value["selected_resources"], label + ".selected_resources", 0, MAX_CANDIDATES)
        validate_int(
            value["inspected_bytes"], label + ".inspected_bytes",
            0, MAX_INSPECTION_BYTES,
        )
        if value["selected_bytes"] > value["max_bytes"]:
            raise ContextResolutionError("selected_bytes exceeds max_bytes")
        if value["selected_resources"] > value["max_resources"]:
            raise ContextResolutionError("selected_resources exceeds max_resources")
        if value["inspected_bytes"] > value["max_inspection_bytes"]:
            raise ContextResolutionError("inspected_bytes exceeds max_inspection_bytes")
        if value["selected_bytes"] * 2 > value["inspected_bytes"]:
            raise ContextResolutionError("inspected_bytes cannot cover selected stable reads")
    return value


def _validate_planner(value, request):
    """Validate optional planner provenance without making planners mandatory."""
    exact_object(
        value,
        {
            "planner_version", "generator", "skill_contract", "contract_index",
            "system_catalog", "candidate_discovery", "freshness", "token_budget",
        },
        set(),
        "planner",
    )
    if value["planner_version"] != "1.0" or value["generator"] != "context-plan-v1":
        raise ContextResolutionError("planner identity is unsupported")
    for field in ("skill_contract", "contract_index", "system_catalog"):
        reference = value[field]
        exact_object(reference, {"path", "sha256"}, set(), "planner." + field)
        validate_relative_path(reference["path"], "planner.%s.path" % field)
        validate_sha(reference["sha256"], "planner.%s.sha256" % field)

    discovery = value["candidate_discovery"]
    exact_object(
        discovery,
        {
            "mode", "hints_sha256", "candidate_set_sha256", "prefix_file_limit",
            "prefix_outcomes",
        },
        set(),
        "planner.candidate_discovery",
    )
    if discovery["mode"] != "closed-machine-contract":
        raise ContextResolutionError("planner candidate discovery mode is unsupported")
    validate_sha(discovery["hints_sha256"], "planner.candidate_discovery.hints_sha256")
    validate_sha(
        discovery["candidate_set_sha256"],
        "planner.candidate_discovery.candidate_set_sha256",
    )
    validate_int(
        discovery["prefix_file_limit"],
        "planner.candidate_discovery.prefix_file_limit", 1, MAX_CANDIDATES,
    )
    outcomes = discovery["prefix_outcomes"]
    if not isinstance(outcomes, list) or len(outcomes) > MAX_CANDIDATES:
        raise ContextResolutionError("planner prefix_outcomes must be a bounded array")
    outcome_paths = []
    for index, outcome in enumerate(outcomes):
        label = "planner.candidate_discovery.prefix_outcomes[%d]" % index
        exact_object(
            outcome, {"path", "status", "file_count", "reason_code"}, set(), label
        )
        validate_relative_path(outcome["path"], label + ".path")
        validate_enum(outcome["status"], {"enumerated", "unresolved"}, label + ".status")
        validate_int(outcome["file_count"], label + ".file_count", 0, MAX_CANDIDATES)
        if outcome["status"] == "enumerated":
            if outcome["reason_code"] is not None:
                raise ContextResolutionError("enumerated prefix outcome cannot have a reason")
        elif outcome["reason_code"] != "missing-prefix" or outcome["file_count"] != 0:
            raise ContextResolutionError(
                "unresolved prefix outcome must use missing-prefix with zero files"
            )
        outcome_paths.append(outcome["path"])
    if outcome_paths != sorted(set(outcome_paths)):
        raise ContextResolutionError("planner prefix_outcomes must have unique sorted paths")
    if discovery["candidate_set_sha256"] != sha256_json(request["candidates"]):
        raise ContextResolutionError("planner candidate_set_sha256 does not match candidates")

    freshness = value["freshness"]
    exact_object(
        freshness, {"observed_at_basis", "default_max_age_seconds"}, set(),
        "planner.freshness",
    )
    if freshness["observed_at_basis"] != "planner-as-of-inspection":
        raise ContextResolutionError("planner freshness basis is unsupported")
    if freshness["default_max_age_seconds"] is not None:
        raise ContextResolutionError("planner default freshness must remain explicitly unbounded")
    if any(candidate["observed_at"] != request["as_of"] for candidate in request["candidates"]):
        raise ContextResolutionError("planner candidates must use request as_of as observation time")

    token_budget = value["token_budget"]
    exact_object(
        token_budget,
        {"max_tokens", "bytes_per_token", "derived_max_bytes", "estimator", "enforcement"},
        set(),
        "planner.token_budget",
    )
    max_tokens = validate_int(
        token_budget["max_tokens"], "planner.token_budget.max_tokens", 1, MAX_CONTEXT_BYTES,
    )
    bytes_per_token = validate_int(
        token_budget["bytes_per_token"], "planner.token_budget.bytes_per_token", 1, 16,
    )
    derived = validate_int(
        token_budget["derived_max_bytes"], "planner.token_budget.derived_max_bytes",
        1, MAX_CONTEXT_BYTES,
    )
    if token_budget["estimator"] != "utf8-bytes-per-token-proxy-v1":
        raise ContextResolutionError("planner token estimator is unsupported")
    if token_budget["enforcement"] != "derived-byte-ceiling":
        raise ContextResolutionError("planner token enforcement is unsupported")
    if derived != max_tokens * bytes_per_token or derived != request["budget"]["max_bytes"]:
        raise ContextResolutionError("planner token budget does not match request byte budget")
    return value


def _validate_candidate(value, index):
    label = "candidates[%d]" % index
    required = {
        "resource_id", "scope", "path", "role", "requirement", "authority",
        "observed_at", "max_age_seconds", "priority", "reason_code", "sensitivity",
        "expected_sha256", "conflict_group", "supersedes",
    }
    exact_object(value, required, set(), label)
    validate_safe_id(value["resource_id"], label + ".resource_id")
    validate_enum(value["scope"], {"bundle", "project"}, label + ".scope")
    validate_relative_path(value["path"], label + ".path")
    validate_safe_id(value["role"], label + ".role")
    validate_enum(value["requirement"], REQUIREMENTS, label + ".requirement")
    validate_enum(value["authority"], AUTHORITIES, label + ".authority")
    parse_datetime(value["observed_at"], label + ".observed_at")
    if value["max_age_seconds"] is not None:
        validate_int(value["max_age_seconds"], label + ".max_age_seconds", 0, 315_576_000)
    validate_int(value["priority"], label + ".priority", 0, 100)
    validate_safe_id(value["reason_code"], label + ".reason_code")
    validate_enum(value["sensitivity"], SENSITIVITIES, label + ".sensitivity")
    if value["expected_sha256"] is not None:
        validate_sha(value["expected_sha256"], label + ".expected_sha256")
    if value["conflict_group"] is not None:
        validate_safe_id(value["conflict_group"], label + ".conflict_group")
    supersedes = value["supersedes"]
    if not isinstance(supersedes, list) or len(supersedes) > 32:
        raise ContextResolutionError("%s.supersedes must be a unique array of at most 32 IDs" % label)
    for offset, resource_id in enumerate(supersedes):
        validate_safe_id(resource_id, "%s.supersedes[%d]" % (label, offset))
    if len(supersedes) != len(set(supersedes)):
        raise ContextResolutionError("%s.supersedes must be a unique array of at most 32 IDs" % label)
    return value


def _assert_acyclic(candidates):
    graph = {candidate["resource_id"]: candidate["supersedes"] for candidate in candidates}
    visiting = set()
    visited = set()

    def visit(resource_id):
        if resource_id in visiting:
            raise ContextResolutionError("candidate supersedes graph contains a cycle at %s" % resource_id)
        if resource_id in visited:
            return
        visiting.add(resource_id)
        for target in graph[resource_id]:
            visit(target)
        visiting.remove(resource_id)
        visited.add(resource_id)

    for resource_id in sorted(graph):
        visit(resource_id)


def validate_request(value):
    required = {
        "schema_version", "run_id", "turn_id", "as_of", "route", "budget",
        "registry_offsets", "candidates",
    }
    exact_object(value, required, {"planner"}, "context request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ContextResolutionError("context request schema_version must be %s" % SCHEMA_VERSION)
    validate_uuid(value["run_id"], "run_id")
    validate_safe_id(value["turn_id"], "turn_id")
    as_of = parse_datetime(value["as_of"], "as_of")
    _validate_route(value["route"], "route")
    _validate_budget(value["budget"])
    validate_offsets(value["registry_offsets"])
    candidates = value["candidates"]
    if not isinstance(candidates, list) or len(candidates) > MAX_CANDIDATES:
        raise ContextResolutionError("candidates must be an array with at most %d entries" % MAX_CANDIDATES)
    seen = {}
    for index, candidate in enumerate(candidates):
        _validate_candidate(candidate, index)
        resource_id = candidate["resource_id"]
        if resource_id in seen:
            raise ContextResolutionError("duplicate candidate resource_id: %s" % resource_id)
        seen[resource_id] = candidate
        if parse_datetime(candidate["observed_at"], "observed_at") > as_of:
            raise ContextResolutionError("candidate %s is observed after as_of" % resource_id)
    for candidate in candidates:
        for target in candidate["supersedes"]:
            if target not in seen:
                raise ContextResolutionError(
                    "candidate %s supersedes unknown resource %s"
                    % (candidate["resource_id"], target)
                )
            if target == candidate["resource_id"]:
                raise ContextResolutionError("candidate cannot supersede itself: %s" % target)
            if (
                    candidate["requirement"] == "forbidden"
                    or seen[target]["requirement"] == "forbidden"):
                raise ContextResolutionError("forbidden candidates cannot participate in supersedes")
    _assert_acyclic(candidates)
    if "planner" in value:
        _validate_planner(value["planner"], value)
    by_path = {}
    for candidate in candidates:
        by_path.setdefault((candidate["scope"], candidate["path"]), []).append(candidate)
    for (scope, path), entries in by_path.items():
        states = {entry["requirement"] == "forbidden" for entry in entries}
        if len(states) > 1:
            raise ContextResolutionError(
                "context path has contradictory forbidden policy: %s:%s" % (scope, path)
            )
    if value["route"]["command"] == "auto":
        declared_shards = set(value["route"]["scenario_shards"])
        for candidate in candidates:
            if (
                    candidate["scope"] == "bundle" and candidate["path"] in ALLOWED_SHARDS
                    and candidate["path"] not in declared_shards):
                raise ContextResolutionError(
                    "auto-routing candidate is absent from route.scenario_shards: %s"
                    % candidate["path"]
                )
        shard_resource_ids = set()
        for shard in value["route"]["scenario_shards"]:
            matches = [
                item for item in candidates
                if item["scope"] == "bundle" and item["path"] == shard
                and item["requirement"] == "required"
            ]
            if len(matches) != 1:
                raise ContextResolutionError(
                    "/auto scenario shard must have exactly one required bundle candidate: %s" % shard
                )
            shard_candidate = matches[0]
            if (
                    shard_candidate["role"] != "routing-scenario"
                    or shard_candidate["conflict_group"] is not None
                    or shard_candidate["supersedes"]):
                raise ContextResolutionError(
                    "/auto scenario shard candidates must be direct required routing-scenario resources"
                )
            shard_resource_ids.add(shard_candidate["resource_id"])
        for candidate in candidates:
            if any(target in shard_resource_ids for target in candidate["supersedes"]):
                raise ContextResolutionError("/auto scenario shard candidates cannot be superseded")
    elif any(
            candidate["scope"] == "bundle" and candidate["path"] in ALLOWED_SHARDS
            for candidate in candidates):
        raise ContextResolutionError("non-auto context requests cannot include auto-routing shards")
    return value


def _catalog_index(catalog):
    if not isinstance(catalog, dict):
        raise ContextResolutionError("system catalog must be an object")
    for field in ("architecture_version", "commands", "disciplines", "protocol"):
        if field not in catalog:
            raise ContextResolutionError("system catalog is missing %s" % field)
    version = catalog["architecture_version"]
    if not isinstance(version, str) or not CATALOG_SEMVER.fullmatch(version):
        raise ContextResolutionError("system catalog architecture_version must be semver")
    commands = catalog["commands"]
    if (
            not isinstance(commands, list)
            or any(not isinstance(command, str) for command in commands)
            or set(commands) != COMMANDS):
        raise ContextResolutionError("system catalog command set does not match the resolver contract")
    locations = {}
    skill_commands = {}
    disciplines = catalog["disciplines"]
    if not isinstance(disciplines, dict):
        raise ContextResolutionError("system catalog disciplines must be an object")
    for discipline, definition in disciplines.items():
        if not isinstance(definition, dict) or not isinstance(definition.get("phases"), dict):
            raise ContextResolutionError("system catalog discipline %s has invalid phases" % discipline)
        command = definition.get("command", {}).get("name")
        if command != discipline or command not in COMMANDS - {"auto"}:
            raise ContextResolutionError("system catalog discipline %s has invalid command" % discipline)
        for phase, skills in definition["phases"].items():
            if not isinstance(skills, list):
                raise ContextResolutionError("system catalog phase %s/%s must be an array" % (discipline, phase))
            for skill in skills:
                validate_safe_id(skill, "catalog skill")
                if skill in locations:
                    raise ContextResolutionError("system catalog contains duplicate skill %s" % skill)
                locations[skill] = "%s/%s/%s/SKILL.md" % (discipline, phase, skill)
                skill_commands[skill] = discipline
    protocol = catalog["protocol"]
    if not isinstance(protocol, dict) or not isinstance(protocol.get("skills"), list):
        raise ContextResolutionError("system catalog protocol skills must be an array")
    for skill in protocol["skills"]:
        validate_safe_id(skill, "catalog protocol skill")
        if skill in locations:
            raise ContextResolutionError("system catalog contains duplicate skill %s" % skill)
        locations[skill] = "protocol/%s/SKILL.md" % skill
        skill_commands[skill] = "protocol"
    return version, locations, skill_commands


def load_catalog(bundle_root):
    raw = anchored_read(
        bundle_root, "references/system-catalog.json", MAX_REQUEST_BYTES, "bundle root"
    )
    try:
        catalog = strict_json_loads(raw.decode("utf-8"), "system catalog")
    except UnicodeDecodeError as exc:
        raise ContextResolutionError("system catalog must be UTF-8") from exc
    version, locations, skill_commands = _catalog_index(catalog)
    return catalog, hashlib.sha256(raw).hexdigest(), version, locations, skill_commands


def _frontmatter_scalar(text, key):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    prefix = key + ":"
    matches = [line[len(prefix):].strip() for line in lines[1:end] if line.startswith(prefix)]
    if len(matches) != 1 or not matches[0]:
        return None
    value = matches[0]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return value


def validate_route_against_catalog(request, bundle_root, catalog_data=None):
    if catalog_data is None:
        catalog_data = load_catalog(bundle_root)
    _, catalog_sha, version, locations, skill_commands = catalog_data
    route = request["route"]
    skill = route["target_skill"]
    if skill not in locations:
        raise ContextResolutionError("route target_skill is absent from system catalog: %s" % skill)
    if route["command"] != "auto" and skill_commands[skill] != route["command"]:
        raise ContextResolutionError(
            "route command %s cannot target %s" % (route["command"], skill)
        )
    if route["command"] == "auto" and skill_commands[skill] != "protocol":
        target_shard = "references/auto-routing/%s.md" % skill_commands[skill]
        if target_shard not in route["scenario_shards"]:
            raise ContextResolutionError(
                "/auto target skill discipline is absent from route.scenario_shards: %s"
                % target_shard
            )
    skill_raw = anchored_read(bundle_root, locations[skill], 256_000, "bundle root")
    try:
        skill_text = skill_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextResolutionError("target SKILL.md must be UTF-8") from exc
    if _frontmatter_scalar(skill_text, "name") != skill:
        raise ContextResolutionError("target SKILL.md name does not match the catalog")
    # Skill versions are independently tracked and may move ahead of the
    # architecture/catalog version.  The route binds both hashes; requiring
    # equality between those two distinct version domains rejects valid skills.
    skill_version = _frontmatter_scalar(skill_text, "version")
    if not isinstance(skill_version, str) or not SKILL_SEMVER.fullmatch(skill_version):
        raise ContextResolutionError("target SKILL.md version must be semver")
    return catalog_sha, version, skill_version, hashlib.sha256(skill_raw).hexdigest()


def _age_microseconds(as_of, observed):
    delta = as_of - observed
    return ((delta.days * 86_400 + delta.seconds) * 1_000_000) + delta.microseconds


def _candidate_rank(state):
    candidate = state["candidate"]
    return (
        0 if candidate["requirement"] == "required" else 1,
        AUTHORITY_RANK[candidate["authority"]],
        state["age_microseconds"],
        -candidate["priority"],
        0 if candidate["scope"] == "bundle" else 1,
        candidate["path"],
        candidate["resource_id"],
    )


def _root_sources(resource_id, incoming, memo):
    if resource_id in memo:
        return memo[resource_id]
    sources = incoming.get(resource_id, [])
    if not sources:
        memo[resource_id] = {resource_id}
    else:
        roots = set()
        for source in sources:
            roots.update(_root_sources(source, incoming, memo))
        memo[resource_id] = roots
    return memo[resource_id]


def _omission(resource_id, reason_code, selected_resource_id=None):
    return {
        "resource_id": resource_id,
        "reason_code": reason_code,
        "selected_resource_id": selected_resource_id,
    }


def _signature_payload(manifest):
    return {
        "schema_version": manifest["schema_version"],
        "route": manifest["route"],
        "budget": manifest["budget"],
        "resources": manifest["resources"],
        "omitted": manifest["omitted"],
        "conflicts": manifest["conflicts"],
        "registry_offsets": manifest["registry_offsets"],
    }


def resolve_context(request, bundle_root, project_root):
    """Return a validated manifest for a validated explicit request."""
    validate_request(request)
    request = strict_json_loads(canonical_json(request), "normalized context request")
    request["route"]["scenario_shards"] = sorted(request["route"]["scenario_shards"])
    bundle_path = normalized_root(bundle_root, "bundle root")
    project_path = normalized_root(project_root, "project root")
    catalog_data = load_catalog(bundle_path)
    catalog_sha, catalog_version, skill_version, skill_sha = validate_route_against_catalog(
        request, bundle_path, catalog_data
    )
    roots = {"bundle": bundle_path, "project": project_path}
    as_of = parse_datetime(request["as_of"], "as_of")
    max_sensitivity = SENSITIVITY_RANK[request["budget"]["max_sensitivity"]]
    max_bytes = request["budget"]["max_bytes"]
    by_id = {candidate["resource_id"]: candidate for candidate in request["candidates"]}
    omitted = {}
    eligible = {}
    inspectable = []

    for candidate in request["candidates"]:
        resource_id = candidate["resource_id"]
        if candidate["requirement"] == "forbidden":
            omitted[resource_id] = _omission(resource_id, "forbidden")
            continue
        if SENSITIVITY_RANK[candidate["sensitivity"]] > max_sensitivity:
            if candidate["requirement"] == "required":
                raise ContextResolutionError(
                    "required context exceeds sensitivity budget: %s" % resource_id
                )
            omitted[resource_id] = _omission(resource_id, "sensitivity-budget")
            continue
        observed = parse_datetime(candidate["observed_at"], "observed_at")
        age = _age_microseconds(as_of, observed)
        max_age = candidate["max_age_seconds"]
        if max_age is not None and age > max_age * 1_000_000:
            if candidate["requirement"] == "required":
                raise ContextResolutionError("required context is stale: %s" % resource_id)
            omitted[resource_id] = _omission(resource_id, "stale")
            continue
        inspectable.append({"candidate": candidate, "age_microseconds": age})

    inspected_bytes = 0
    max_inspection_bytes = request["budget"]["max_inspection_bytes"]
    for pending in sorted(inspectable, key=_candidate_rank):
        candidate = pending["candidate"]
        resource_id = candidate["resource_id"]
        remaining_inspection = max_inspection_bytes - inspected_bytes
        try:
            raw = anchored_read(
                roots[candidate["scope"]], candidate["path"], max_bytes,
                candidate["scope"] + " root", inspection_limit=remaining_inspection,
            )
        except ContextSourceMissing:
            if candidate["requirement"] == "required":
                raise ContextResolutionError("required context is missing: %s" % resource_id)
            omitted[resource_id] = _omission(resource_id, "missing")
            continue
        except ContextSourceTooLarge:
            if candidate["requirement"] == "required":
                raise ContextResolutionError(
                    "required context exceeds byte budget: %s" % resource_id
                )
            omitted[resource_id] = _omission(resource_id, "byte-budget")
            continue
        except ContextInspectionBudgetExceeded:
            if candidate["requirement"] == "required":
                raise ContextResolutionError(
                    "required context exceeds inspection budget: %s" % resource_id
                )
            omitted[resource_id] = _omission(resource_id, "inspection-budget")
            continue
        inspected_bytes += len(raw) * 2
        digest = hashlib.sha256(raw).hexdigest()
        if candidate["expected_sha256"] is not None and candidate["expected_sha256"] != digest:
            if candidate["requirement"] == "required":
                raise ContextResolutionError("required context hash mismatch: %s" % resource_id)
            omitted[resource_id] = _omission(resource_id, "hash-mismatch")
            continue
        eligible[resource_id] = {
            "candidate": candidate,
            "sha256": digest,
            "bytes": len(raw),
            "age_microseconds": pending["age_microseconds"],
        }

    aliases = {resource_id: {resource_id} for resource_id in eligible}
    representative = {resource_id: resource_id for resource_id in eligible}
    logical_conflicts = []

    incoming = {}
    for source_id, state in eligible.items():
        for target_id in state["candidate"]["supersedes"]:
            if target_id in eligible:
                incoming.setdefault(target_id, []).append(source_id)
    roots_memo = {}
    superseded_by = {}
    for resource_id in eligible:
        roots_for_resource = _root_sources(resource_id, incoming, roots_memo)
        if resource_id not in roots_for_resource:
            winner = min(roots_for_resource, key=lambda item: _candidate_rank(eligible[item]))
            superseded_by[resource_id] = winner
    for loser, winner in sorted(superseded_by.items()):
        aliases[winner].add(loser)
        representative[loser] = winner
        omitted[loser] = _omission(loser, "superseded", winner)
    active = set(eligible) - set(superseded_by)
    by_winner = {}
    for loser, winner in superseded_by.items():
        by_winner.setdefault(winner, []).append(loser)
    for winner, losers in sorted(by_winner.items()):
        logical_conflicts.append({
            "kind": "supersedes", "key": winner, "winner_resource_id": winner,
            "loser_resource_ids": sorted(losers),
        })

    groups = {}
    for resource_id in active:
        group = eligible[resource_id]["candidate"]["conflict_group"]
        if group is not None:
            groups.setdefault(group, []).append(resource_id)
    for group, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        hashes = {eligible[item]["sha256"] for item in members}
        if len(hashes) != 1:
            raise ContextResolutionError(
                "unresolved context conflict group has different content: %s" % group
            )
        winner = min(members, key=lambda item: _candidate_rank(eligible[item]))
        losers = sorted(item for item in members if item != winner)
        for loser in losers:
            aliases[winner].update(aliases[loser])
            for alias in aliases[loser]:
                representative[alias] = winner
            active.remove(loser)
            omitted[loser] = _omission(loser, "duplicate-content", winner)
        logical_conflicts.append({
            "kind": "conflict-group", "key": group, "winner_resource_id": winner,
            "loser_resource_ids": losers,
        })

    by_hash = {}
    for resource_id in active:
        by_hash.setdefault(eligible[resource_id]["sha256"], []).append(resource_id)
    for members in by_hash.values():
        if len(members) < 2:
            continue
        winner = min(members, key=lambda item: _candidate_rank(eligible[item]))
        for loser in sorted(item for item in members if item != winner):
            aliases[winner].update(aliases[loser])
            for alias in aliases[loser]:
                representative[alias] = winner
            active.remove(loser)
            omitted[loser] = _omission(loser, "duplicate-content", winner)

    def effective_required(resource_id):
        return any(by_id[alias]["requirement"] == "required" for alias in aliases[resource_id])

    ordered = sorted(
        active,
        key=lambda item: (
            0 if effective_required(item) else 1,
            *_candidate_rank(eligible[item])[1:],
        ),
    )
    selected = []
    selected_bytes = 0
    max_resources = request["budget"]["max_resources"]
    for resource_id in ordered:
        size = eligible[resource_id]["bytes"]
        required = effective_required(resource_id)
        reason = None
        if len(selected) >= max_resources:
            reason = "resource-budget"
        elif selected_bytes + size > max_bytes:
            reason = "byte-budget"
        if reason is not None:
            if required:
                raise ContextResolutionError(
                    "required context exceeds %s: %s" % (reason, resource_id)
                )
            for alias in aliases[resource_id]:
                omitted[alias] = _omission(alias, reason)
            continue
        selected.append(resource_id)
        selected_bytes += size

    selected_set = set(selected)
    for item in omitted.values():
        target = item["selected_resource_id"]
        if target is not None:
            final = representative.get(target, target)
            item["selected_resource_id"] = final if final in selected_set else None

    resources = []
    for resource_id in selected:
        state = eligible[resource_id]
        candidate = state["candidate"]
        resources.append({
            "resource_id": resource_id,
            "scope": candidate["scope"],
            "path": candidate["path"],
            "role": candidate["role"],
            "requirement": "required" if effective_required(resource_id) else "optional",
            "authority": candidate["authority"],
            "observed_at": candidate["observed_at"],
            "max_age_seconds": candidate["max_age_seconds"],
            "priority": candidate["priority"],
            "reason_code": candidate["reason_code"],
            "sensitivity": candidate["sensitivity"],
            "sha256": state["sha256"],
            "bytes": state["bytes"],
            "conflict_group": candidate["conflict_group"],
            "supersedes": sorted(candidate["supersedes"]),
            "satisfies_resource_ids": sorted(aliases[resource_id]),
        })

    conflicts = []
    for item in logical_conflicts:
        normalized = dict(item)
        normalized["winner_resource_id"] = representative.get(
            item["winner_resource_id"], item["winner_resource_id"]
        )
        conflicts.append(normalized)
    conflicts.sort(key=lambda item: (item["kind"], item["key"]))
    route = dict(request["route"])
    route["scenario_shards"] = sorted(route["scenario_shards"])
    route["catalog_version"] = catalog_version
    route["catalog_sha256"] = catalog_sha
    route["skill_version"] = skill_version
    route["skill_sha256"] = skill_sha
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "request": strict_json_loads(canonical_json(request), "normalized context request"),
        "request_sha256": sha256_json(request),
        "run_id": request["run_id"],
        "turn_id": request["turn_id"],
        "as_of": request["as_of"],
        "route": route,
        "budget": {
            **request["budget"],
            "selected_bytes": selected_bytes,
            "selected_resources": len(resources),
            "inspected_bytes": inspected_bytes,
        },
        "resources": resources,
        "omitted": sorted(omitted.values(), key=lambda item: item["resource_id"]),
        "conflicts": conflicts,
        "registry_offsets": dict(request["registry_offsets"]),
        "token_estimate": None,
        "estimator": None,
        "context_signature": "",
    }
    manifest["context_signature"] = sha256_json(_signature_payload(manifest))
    validate_manifest(manifest)
    return manifest


def _validate_manifest_resource(value, index):
    label = "resources[%d]" % index
    required = {
        "resource_id", "scope", "path", "role", "requirement", "authority",
        "observed_at", "max_age_seconds", "priority", "reason_code", "sensitivity",
        "sha256", "bytes", "conflict_group", "supersedes", "satisfies_resource_ids",
    }
    exact_object(value, required, set(), label)
    candidate_shape = dict(value)
    candidate_shape["expected_sha256"] = value["sha256"]
    candidate_shape.pop("sha256")
    candidate_shape.pop("bytes")
    candidate_shape.pop("satisfies_resource_ids")
    _validate_candidate(candidate_shape, index)
    if value["requirement"] == "forbidden":
        raise ContextResolutionError("selected resource cannot be forbidden")
    validate_sha(value["sha256"], label + ".sha256")
    validate_int(value["bytes"], label + ".bytes", 0, MAX_CONTEXT_BYTES)
    satisfies = value["satisfies_resource_ids"]
    if not isinstance(satisfies, list) or not satisfies or len(satisfies) > MAX_CANDIDATES:
        raise ContextResolutionError("%s.satisfies_resource_ids must be a non-empty unique array" % label)
    for offset, resource_id in enumerate(satisfies):
        validate_safe_id(resource_id, "%s.satisfies_resource_ids[%d]" % (label, offset))
    if len(satisfies) != len(set(satisfies)):
        raise ContextResolutionError("%s.satisfies_resource_ids must be a non-empty unique array" % label)
    if value["resource_id"] not in satisfies:
        raise ContextResolutionError("%s must satisfy its own resource_id" % label)


def validate_manifest(value):
    required = {
        "schema_version", "request", "request_sha256", "run_id", "turn_id", "as_of",
        "route", "budget", "resources", "omitted", "conflicts", "registry_offsets",
        "token_estimate", "estimator", "context_signature",
    }
    exact_object(value, required, set(), "context manifest")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ContextResolutionError("context manifest schema_version must be %s" % SCHEMA_VERSION)
    validate_request(value["request"])
    validate_sha(value["request_sha256"], "request_sha256")
    if value["request_sha256"] != sha256_json(value["request"]):
        raise ContextResolutionError("request_sha256 does not match the embedded request")
    validate_uuid(value["run_id"], "run_id")
    validate_safe_id(value["turn_id"], "turn_id")
    parse_datetime(value["as_of"], "as_of")
    _validate_route(value["route"], "route", manifest=True)
    _validate_budget(value["budget"], manifest=True)
    validate_offsets(value["registry_offsets"])
    request = value["request"]
    if (
            value["run_id"] != request["run_id"]
            or value["turn_id"] != request["turn_id"]
            or value["as_of"] != request["as_of"]
            or value["registry_offsets"] != request["registry_offsets"]):
        raise ContextResolutionError("context manifest invocation identity does not match its request")
    request_route = {
        key: value["route"][key]
        for key in ("command", "target_skill", "reason_code", "scenario_shards")
    }
    if request_route != request["route"]:
        raise ContextResolutionError("context manifest route does not match its request")
    request_budget = {
        key: value["budget"][key]
        for key in ("max_bytes", "max_resources", "max_sensitivity", "max_inspection_bytes")
    }
    if request_budget != request["budget"]:
        raise ContextResolutionError("context manifest budget does not match its request")
    resources = value["resources"]
    if not isinstance(resources, list) or len(resources) > MAX_CANDIDATES:
        raise ContextResolutionError("resources must be an array with at most 256 entries")
    selected_ids = set()
    selected_bytes = 0
    satisfied_ids = set()
    for index, resource in enumerate(resources):
        _validate_manifest_resource(resource, index)
        resource_id = resource["resource_id"]
        if resource_id in selected_ids:
            raise ContextResolutionError("duplicate selected resource_id: %s" % resource_id)
        selected_ids.add(resource_id)
        selected_bytes += resource["bytes"]
        for satisfied in resource["satisfies_resource_ids"]:
            if satisfied in satisfied_ids:
                raise ContextResolutionError("resource is satisfied more than once: %s" % satisfied)
            satisfied_ids.add(satisfied)
    if selected_bytes != value["budget"]["selected_bytes"]:
        raise ContextResolutionError("budget.selected_bytes does not match resources")
    if len(resources) != value["budget"]["selected_resources"]:
        raise ContextResolutionError("budget.selected_resources does not match resources")
    selected_route_shards = [
        resource for resource in resources
        if resource["scope"] == "bundle" and resource["path"] in ALLOWED_SHARDS
    ]
    if value["route"]["command"] == "auto":
        declared = value["route"]["scenario_shards"]
        if sorted(resource["path"] for resource in selected_route_shards) != sorted(declared):
            raise ContextResolutionError(
                "/auto context manifest must select every declared scenario shard exactly once"
            )
        if any(
                resource["requirement"] != "required"
                or resource["role"] != "routing-scenario"
                or resource["conflict_group"] is not None
                or resource["supersedes"]
                for resource in selected_route_shards):
            raise ContextResolutionError(
                "/auto context manifest scenario shards must be direct required routing resources"
            )
    elif selected_route_shards:
        raise ContextResolutionError("non-auto context manifest cannot select auto-routing shards")
    omissions = value["omitted"]
    if not isinstance(omissions, list) or len(omissions) > MAX_CANDIDATES:
        raise ContextResolutionError("omitted must be an array with at most 256 entries")
    omitted_ids = set()
    for index, omission in enumerate(omissions):
        label = "omitted[%d]" % index
        exact_object(omission, {"resource_id", "reason_code", "selected_resource_id"}, set(), label)
        resource_id = validate_safe_id(omission["resource_id"], label + ".resource_id")
        if resource_id in omitted_ids:
            raise ContextResolutionError("duplicate omitted resource_id: %s" % resource_id)
        if resource_id in selected_ids:
            raise ContextResolutionError("selected resource cannot also be omitted: %s" % resource_id)
        omitted_ids.add(resource_id)
        validate_enum(omission["reason_code"], OMISSION_REASONS, label + ".reason_code")
        target = omission["selected_resource_id"]
        if target is not None:
            validate_safe_id(target, label + ".selected_resource_id")
            if target not in selected_ids:
                raise ContextResolutionError("omission selected_resource_id is not selected")
    conflicts = value["conflicts"]
    if not isinstance(conflicts, list) or len(conflicts) > MAX_CANDIDATES:
        raise ContextResolutionError("conflicts must be an array with at most 256 entries")
    seen_conflicts = set()
    for index, conflict in enumerate(conflicts):
        label = "conflicts[%d]" % index
        exact_object(
            conflict, {"kind", "key", "winner_resource_id", "loser_resource_ids"}, set(), label
        )
        validate_enum(conflict["kind"], {"conflict-group", "supersedes"}, label + ".kind")
        validate_safe_id(conflict["key"], label + ".key")
        validate_safe_id(conflict["winner_resource_id"], label + ".winner_resource_id")
        losers = conflict["loser_resource_ids"]
        if not isinstance(losers, list) or not losers:
            raise ContextResolutionError("%s.loser_resource_ids must be a non-empty unique array" % label)
        for offset, loser in enumerate(losers):
            validate_safe_id(loser, "%s.loser_resource_ids[%d]" % (label, offset))
        if len(losers) != len(set(losers)):
            raise ContextResolutionError("%s.loser_resource_ids must be a non-empty unique array" % label)
        identity = (conflict["kind"], conflict["key"])
        if identity in seen_conflicts:
            raise ContextResolutionError("duplicate conflict identity")
        seen_conflicts.add(identity)
    if value["token_estimate"] is not None or value["estimator"] is not None:
        raise ContextResolutionError("token_estimate and estimator must be null")
    validate_sha(value["context_signature"], "context_signature")
    expected = sha256_json(_signature_payload(value))
    if value["context_signature"] != expected:
        raise ContextResolutionError("context_signature does not match manifest semantics")
    return value


def verify_manifest_sources(value, bundle_root, project_root):
    """Rerun the embedded request and prove the manifest is its current result."""
    validate_manifest(value)
    bundle_path = normalized_root(bundle_root, "bundle root")
    project_path = normalized_root(project_root, "project root")
    current = resolve_context(value["request"], bundle_path, project_path)
    if canonical_json(current) != canonical_json(value):
        if any(
                current["route"][field] != value["route"][field]
                for field in ("catalog_version", "catalog_sha256")):
            raise ContextResolutionError(
                "context manifest catalog identity no longer matches the bundle"
            )
        if any(
                current["route"][field] != value["route"][field]
                for field in ("skill_version", "skill_sha256")):
            raise ContextResolutionError(
                "context manifest target skill no longer matches the bundle"
            )
        current_resources = {
            resource["resource_id"]: (resource["sha256"], resource["bytes"])
            for resource in current["resources"]
        }
        recorded_resources = {
            resource["resource_id"]: (resource["sha256"], resource["bytes"])
            for resource in value["resources"]
        }
        if current_resources != recorded_resources:
            raise ContextResolutionError(
                "context manifest source no longer matches deterministic bytes/hash"
            )
        raise ContextResolutionError(
            "context manifest no longer matches deterministic resolution of its request"
        )
    return value


@contextlib.contextmanager
def _open_output_parent(project_root, relative):
    validate_relative_path(relative, "output path")
    root_path, root_fd, root_identity = _open_root(project_root, "project root")
    descriptors = [root_fd]
    links = []
    parts = relative.split("/")
    try:
        parent_fd = root_fd
        parent_path = root_path
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        for component in parts[:-1]:
            child_fd = None
            try:
                child_fd = os.open(component, flags, dir_fd=parent_fd)
                opened = os.fstat(child_fd)
                entry = _entry_stat(parent_fd, component, "output directory")
                if (
                        not statmod.S_ISDIR(opened.st_mode) or statmod.S_ISLNK(entry.st_mode)
                        or not _same_entry(opened, entry)):
                    raise ContextResolutionError("output parent changed or is unsafe")
                links.append((parent_fd, component, (opened.st_dev, opened.st_ino)))
                descriptors.append(child_fd)
            except OSError as exc:
                if child_fd is not None:
                    os.close(child_fd)
                raise ContextResolutionError(
                    "output parent must be an existing safe directory: %s" % (parent_path / component)
                ) from exc
            except Exception:
                if child_fd is not None and child_fd not in descriptors:
                    os.close(child_fd)
                raise
            parent_fd = child_fd
            parent_path = parent_path / component
        yield parent_fd, parent_path, parts[-1]
        for ancestor_fd, component, identity in reversed(links):
            current = _entry_stat(ancestor_fd, component, "output directory")
            if statmod.S_ISLNK(current.st_mode) or (current.st_dev, current.st_ino) != identity:
                raise ContextResolutionError("output parent changed during install")
        root_now = _lstat(root_path, "project root")
        if (root_now.st_dev, root_now.st_ino) != root_identity:
            raise ContextResolutionError("project root changed during install")
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def recover_link_install_residue(parent_fd, name, existing):
    """Remove only crash residue proven to be another link to the target inode."""
    if (
            existing is None or statmod.S_ISLNK(existing.st_mode)
            or not statmod.S_ISREG(existing.st_mode) or existing.st_nlink <= 1):
        return existing
    prefix = ".%s.context-create." % name
    try:
        entries = os.listdir(parent_fd)
    except OSError as exc:
        raise ContextResolutionError("cannot inspect context-manifest crash residue: %s" % exc) from exc
    removed = False
    for entry_name in entries:
        if not entry_name.startswith(prefix):
            continue
        residue = _entry_stat(
            parent_fd, entry_name, "context manifest temporary", missing_ok=True
        )
        if residue is None or statmod.S_ISLNK(residue.st_mode) or not statmod.S_ISREG(residue.st_mode):
            continue
        if (residue.st_dev, residue.st_ino) == (existing.st_dev, existing.st_ino):
            os.unlink(entry_name, dir_fd=parent_fd)
            removed = True
    if removed:
        os.fsync(parent_fd)
    current = _entry_stat(parent_fd, name, "context manifest")
    if current.st_nlink != 1:
        raise ContextResolutionError("context manifest must be a single-link regular file")
    return current


def write_manifest(project_root, relative, manifest):
    """Install a manifest without replacement; accept only identical retries."""
    validate_manifest(manifest)
    expected_relative = "memory/runs/%s/turns/%s/context-manifest.json" % (
        manifest["run_id"], manifest["turn_id"],
    )
    if relative != expected_relative:
        raise ContextResolutionError(
            "output path must match the manifest run/turn identity: %s" % expected_relative
        )
    data = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"
    ).encode("utf-8")
    if len(data) > MAX_MANIFEST_BYTES:
        raise ContextResolutionError("context manifest exceeds %d bytes" % MAX_MANIFEST_BYTES)
    existed = False
    with _open_output_parent(project_root, relative) as (parent_fd, parent_path, name):
        # A unique temporary makes concurrent identical writers independent. The
        # hard-link install is the sole no-replace arbitration point; abandoned
        # crash residue can never alias or overwrite the target.
        temp_name = ".%s.context-create.%s" % (name, uuid.uuid4().hex)
        temp_relative = "/".join([*relative.split("/")[:-1], temp_name])
        ensure_ignored(normalized_root(project_root, "project root"), [relative, temp_relative])
        existing = _entry_stat(parent_fd, name, "context manifest", missing_ok=True)
        existing = recover_link_install_residue(parent_fd, name, existing)
        if existing is None:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
            fd = None
            try:
                fd = os.open(temp_name, flags, 0o600, dir_fd=parent_fd)
                os.fchmod(fd, 0o600)
                with os.fdopen(fd, "wb") as handle:
                    fd = None
                    handle.write(data)
                    handle.flush()
                    os.fsync(handle.fileno())
                try:
                    os.link(
                        temp_name, name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
                        follow_symlinks=False,
                    )
                except FileExistsError:
                    existed = True
                try:
                    os.unlink(temp_name, dir_fd=parent_fd)
                except FileNotFoundError:
                    # A concurrent identical retry may have recovered the
                    # post-link crash alias after this writer installed target.
                    pass
                os.fsync(parent_fd)
            finally:
                if fd is not None:
                    os.close(fd)
                residue = _entry_stat(
                    parent_fd, temp_name, "context manifest temporary", missing_ok=True
                )
                if residue is not None:
                    try:
                        os.unlink(temp_name, dir_fd=parent_fd)
                    except FileNotFoundError:
                        pass
        else:
            existed = True
    installed_raw, installed_metadata = anchored_read(
        project_root, relative, MAX_MANIFEST_BYTES, "project root", return_metadata=True,
    )
    if statmod.S_IMODE(installed_metadata.st_mode) != 0o600:
        raise ContextResolutionError("context manifest must use private file mode 0600")
    try:
        installed = strict_json_loads(installed_raw.decode("utf-8"), "installed context manifest")
    except UnicodeDecodeError as exc:
        raise ContextResolutionError("installed context manifest must be UTF-8") from exc
    validate_manifest(installed)
    if canonical_json(installed) != canonical_json(manifest):
        raise ContextResolutionError(
            "immutable context manifest already exists with different content: %s" % relative
        )
    return hashlib.sha256(installed_raw).hexdigest(), existed


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    resolve = subparsers.add_parser("resolve", help="resolve and immutably write a manifest")
    resolve.add_argument("--request", required=True, help="strict JSON context request")
    resolve.add_argument("--bundle-root", default=str(Path(__file__).resolve().parents[1]))
    resolve.add_argument("--project-root", required=True)
    resolve.add_argument("--output", required=True, help="project-relative manifest path")
    check_request = subparsers.add_parser("validate-request", help="validate request and route")
    check_request.add_argument("--request", required=True)
    check_request.add_argument("--bundle-root", default=str(Path(__file__).resolve().parents[1]))
    check_manifest = subparsers.add_parser("validate-manifest", help="validate a manifest")
    check_manifest.add_argument("--manifest", required=True)
    verify_manifest = subparsers.add_parser(
        "verify-manifest", help="validate a manifest and reopen its current sources"
    )
    verify_manifest.add_argument("--manifest", required=True)
    verify_manifest.add_argument("--bundle-root", default=str(Path(__file__).resolve().parents[1]))
    verify_manifest.add_argument("--project-root", required=True)
    return parser


def main(argv=None):
    args = _build_parser().parse_args(argv)
    try:
        if args.command in {"validate-manifest", "verify-manifest"}:
            manifest = read_json_document(args.manifest, "context manifest", MAX_MANIFEST_BYTES)
            validate_manifest(manifest)
            if args.command == "verify-manifest":
                verify_manifest_sources(manifest, args.bundle_root, args.project_root)
            print(canonical_json({
                "status": "verified" if args.command == "verify-manifest" else "valid",
                "context_signature": manifest["context_signature"],
            }))
            return 0
        request = read_json_document(args.request, "context request", MAX_REQUEST_BYTES)
        validate_request(request)
        if args.command == "validate-request":
            validate_route_against_catalog(request, args.bundle_root)
            print(canonical_json({"status": "valid", "run_id": request["run_id"]}))
            return 0
        manifest = resolve_context(request, args.bundle_root, args.project_root)
        digest, existed = write_manifest(args.project_root, args.output, manifest)
        print(canonical_json({
            "status": "resolved", "output": args.output, "sha256": digest,
            "context_signature": manifest["context_signature"],
            "selected_resources": manifest["budget"]["selected_resources"],
            "selected_bytes": manifest["budget"]["selected_bytes"],
            "idempotent_retry": existed,
        }))
        return 0
    except ContextResolutionError as exc:
        print("context-resolver: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
