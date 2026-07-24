#!/usr/bin/env python3
"""Build minimal user distributions from the repository source tree."""
from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import re


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "system-catalog.json"
CAPABILITY_CATALOG = ROOT / "references" / "capability-profiles.json"
MANIFEST = ROOT / "references" / "distribution-files.json"
IGNORED_NAMES = {".DS_Store", "__pycache__"}
IGNORED_SUFFIXES = {".pyc", ".pyo"}
DISTRIBUTION_MANIFEST = "distribution-manifest.json"
MANIFEST_SCHEMA_VERSION = "1.1"
LEGACY_MANIFEST_SCHEMA_VERSION = "1.0"
PROFILE_NAMES = ("lite", "pro", "governed")
DERIVED_OUTPUT_NAMES = ("skill-contract-pack-v1",)
SKILL_CONTRACT_TREE = "references/skill-contracts"
SKILL_CONTRACT_PACK = "references/skill-contracts.pack.json.gz"
SKILL_CONTRACT_PACK_MAX_BYTES = 1_000_000
ENTRY_KEYS = (
    "root_files", "trees", "runtime_references",
    "runtime_scripts", "runtime_script_trees",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
BACKUP_FILE = re.compile(r".+ [0-9]+\.[A-Za-z0-9]+$")
RUNTIME_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\$\{CLAUDE_PLUGIN_ROOT\}/)?"
    r"((?:references|scripts/connectors)/[A-Za-z0-9_./-]+\.(?:md|json|py)"
    r"|scripts/[A-Za-z0-9_-]+\.py)"  # top-level runtimes referenced in prose ship too
)


class DistributionError(ValueError):
    pass


def canonical_json(value):
    try:
        return (json.dumps(
            value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True,
        ) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DistributionError("cannot encode distribution manifest: %s" % exc) from exc


def canonical_compact_json(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise DistributionError("cannot encode compact distribution data: %s" % exc) from exc


def _path_label(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _lstat(path, label=None):
    try:
        return path.lstat()
    except FileNotFoundError as exc:
        raise DistributionError(
            "required distribution input is missing: %s" % (label or _path_label(path))
        ) from exc
    except OSError as exc:
        raise DistributionError(
            "cannot inspect distribution input %s: %s"
            % (label or _path_label(path), exc)
        ) from exc


def validate_source_node(relative, *, allow_directory=True):
    """Resolve one repository input without following links in any component."""
    relative_path = validate_relative(relative)
    root = ROOT
    root_status = _lstat(root, "repository root")
    if stat.S_ISLNK(root_status.st_mode) or not stat.S_ISDIR(root_status.st_mode):
        raise DistributionError("repository root must be a real directory, not a symlink")
    current = root
    for index, component in enumerate(relative_path.parts):
        current = current / component
        status = _lstat(current, str(relative_path))
        if stat.S_ISLNK(status.st_mode):
            raise DistributionError(
                "distribution input contains a symlink: %s" % _path_label(current)
            )
        final = index == len(relative_path.parts) - 1
        if not final and not stat.S_ISDIR(status.st_mode):
            raise DistributionError(
                "distribution input parent is not a directory: %s" % _path_label(current)
            )
    if stat.S_ISREG(status.st_mode):
        if status.st_nlink != 1:
            raise DistributionError(
                "distribution input must be a single-link regular file: %s"
                % _path_label(current)
            )
    elif stat.S_ISDIR(status.st_mode):
        if not allow_directory:
            raise DistributionError(
                "distribution input must be a regular file: %s" % _path_label(current)
            )
    else:
        raise DistributionError(
            "distribution input is a special file: %s" % _path_label(current)
        )
    return current, status


def _checked_regular_reader(path, before, label):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise DistributionError("cannot safely open %s: %s" % (label, exc)) from exc
    try:
        opened = os.fstat(descriptor)
        identity = ("st_dev", "st_ino", "st_nlink", "st_mode")
        if (not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or any(getattr(opened, field) != getattr(before, field) for field in identity)):
            raise DistributionError(
                "%s changed or is unsafe while opening" % label
            )
        return descriptor, opened
    except Exception:
        os.close(descriptor)
        raise


def _safe_source_reader(path, before):
    return _checked_regular_reader(path, before, "distribution input %s" % _path_label(path))


def _read_checked_regular(path, before, label):
    descriptor, opened = _checked_regular_reader(path, before, label)
    try:
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            content = handle.read()
            after = os.fstat(handle.fileno())
    except OSError as exc:
        raise DistributionError("cannot read %s: %s" % (label, exc)) from exc
    stable = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(opened, field) != getattr(after, field) for field in stable):
        raise DistributionError("%s changed while reading" % label)
    return content


def read_source_bytes(relative):
    path, before = validate_source_node(relative, allow_directory=False)
    return _read_checked_regular(
        path, before, "distribution input %s" % _path_label(path)
    )


def load_json(path):
    try:
        relative = path.relative_to(ROOT)
        return json.loads(read_source_bytes(relative).decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise DistributionError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def _empty_entries():
    return {key: [] for key in ENTRY_KEYS}


def _validate_entries(entries, label):
    if not isinstance(entries, dict) or set(entries) != set(ENTRY_KEYS):
        raise DistributionError("%s must declare exactly %s" % (label, ", ".join(ENTRY_KEYS)))
    for key in ENTRY_KEYS:
        values = entries[key]
        if (not isinstance(values, list)
                or any(not isinstance(value, str) or not value for value in values)
                or len(values) != len(set(values))):
            raise DistributionError("%s.%s must be a unique string list" % (label, key))
        for value in values:
            validate_relative(value)


def resolve_plugin_profile(distribution, requested):
    """Validate and resolve shared inputs plus monotonic profile overlays."""
    if distribution.get("schema_version") != "2.1":
        raise DistributionError("distribution-files schema_version must be 2.1")
    plugin = distribution.get("plugin")
    if not isinstance(plugin, dict) or set(plugin) != {
            "profile_order", "shared", "profiles"}:
        raise DistributionError("plugin distribution profile shape is invalid")
    order = plugin["profile_order"]
    profiles = plugin["profiles"]
    if order != list(PROFILE_NAMES) or not isinstance(profiles, dict) or set(profiles) != set(order):
        raise DistributionError("plugin profile order must be lite -> pro -> governed")
    if requested not in profiles:
        raise DistributionError("unknown plugin profile: %s" % requested)
    _validate_entries(plugin["shared"], "plugin.shared")

    cumulative_entries = _empty_entries()
    for key in ENTRY_KEYS:
        cumulative_entries[key].extend(plugin["shared"][key])
    cumulative_capabilities = []
    cumulative_derived_outputs = []
    seen_capabilities = set()
    seen_derived_outputs = set()
    previous_ceiling = {"max_files": 0, "max_bytes": 0}
    selected_ceiling = None
    selected_index = order.index(requested)
    all_exact = set()
    all_trees = set()

    for index, name in enumerate(order):
        spec = profiles[name]
        if not isinstance(spec, dict) or set(spec) != {
                "capabilities", "package_ceiling", "add", "derived_outputs"}:
            raise DistributionError("plugin profile %s shape is invalid" % name)
        capabilities = spec["capabilities"]
        if (not isinstance(capabilities, list)
                or any(not isinstance(value, str) or not value for value in capabilities)
                or len(capabilities) != len(set(capabilities))):
            raise DistributionError("plugin profile %s capabilities are invalid" % name)
        duplicates = seen_capabilities.intersection(capabilities)
        if duplicates:
            raise DistributionError(
                "plugin capability overlays must be additive: %s" % ", ".join(sorted(duplicates))
            )
        seen_capabilities.update(capabilities)
        ceiling = spec["package_ceiling"]
        if (not isinstance(ceiling, dict)
                or set(ceiling) != {"max_files", "max_bytes"}
                or any(isinstance(ceiling[key], bool) or not isinstance(ceiling[key], int)
                       or ceiling[key] <= 0 for key in ceiling)):
            raise DistributionError("plugin profile %s package ceiling is invalid" % name)
        if any(ceiling[key] < previous_ceiling[key] for key in ceiling):
            raise DistributionError("plugin package ceilings must be monotonic")
        previous_ceiling = ceiling
        _validate_entries(spec["add"], "plugin.profiles.%s.add" % name)
        derived_outputs = spec["derived_outputs"]
        if (
                not isinstance(derived_outputs, list)
                or len(derived_outputs) != len(set(derived_outputs))
                or any(value not in DERIVED_OUTPUT_NAMES for value in derived_outputs)):
            raise DistributionError(
                "plugin profile %s derived_outputs are invalid" % name
            )
        duplicate_outputs = seen_derived_outputs.intersection(derived_outputs)
        if duplicate_outputs:
            raise DistributionError(
                "plugin derived outputs must be additive: %s"
                % ", ".join(sorted(duplicate_outputs))
            )
        seen_derived_outputs.update(derived_outputs)
        for key in ENTRY_KEYS:
            values = spec["add"][key]
            if key in {"trees", "runtime_script_trees"}:
                all_trees.update(values)
            else:
                all_exact.update(values)
            if index <= selected_index:
                cumulative_entries[key].extend(values)
        if index <= selected_index:
            cumulative_capabilities.extend(capabilities)
            cumulative_derived_outputs.extend(derived_outputs)
            selected_ceiling = dict(ceiling)

    for key in ("trees", "runtime_script_trees"):
        all_trees.update(plugin["shared"][key])
    for key in ("root_files", "runtime_references", "runtime_scripts"):
        all_exact.update(plugin["shared"][key])

    flattened = [
        value for key in ENTRY_KEYS for value in cumulative_entries[key]
    ]
    if len(flattened) != len(set(flattened)):
        raise DistributionError("resolved plugin profile contains duplicate entries")
    capability_catalog = load_json(CAPABILITY_CATALOG)
    try:
        expected_capabilities = capability_catalog["profiles"][requested]["capabilities"]
    except (KeyError, TypeError) as exc:
        raise DistributionError("capability profile catalog is incomplete") from exc
    if cumulative_capabilities != expected_capabilities:
        raise DistributionError(
            "distribution capabilities differ from capability-profiles.json for %s"
            % requested
        )
    definition = {
        "schema_version": "1.0",
        "profile": requested,
        "capabilities": cumulative_capabilities,
        "package_ceiling": selected_ceiling,
        "entries": cumulative_entries,
        "derived_outputs": cumulative_derived_outputs,
    }
    return {
        **definition,
        "definition_sha256": hashlib.sha256(canonical_json(definition)).hexdigest(),
        "reserved_exact": all_exact,
        "reserved_trees": all_trees,
    }


def standalone_profile(distribution):
    spec = distribution.get("standalone-skill")
    if (not isinstance(spec, dict)
            or set(spec) != {"profile", "capabilities", "package_ceiling"}
            or spec.get("profile") != "lite"):
        raise DistributionError("standalone-skill distribution profile is invalid")
    capabilities = spec["capabilities"]
    ceiling = spec["package_ceiling"]
    if (not isinstance(capabilities, list)
            or len(capabilities) != len(set(capabilities))
            or any(not isinstance(value, str) or not value for value in capabilities)
            or not isinstance(ceiling, dict)
            or set(ceiling) != {"max_files", "max_bytes"}
            or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0
                   for value in ceiling.values())):
        raise DistributionError("standalone-skill distribution profile is invalid")
    definition = {
        "schema_version": "1.0",
        "profile": "lite",
        "capabilities": capabilities,
        "package_ceiling": ceiling,
        "entries": None,
    }
    capability_catalog = load_json(CAPABILITY_CATALOG)
    try:
        known_capabilities = set(capability_catalog["capability_order"])
    except (KeyError, TypeError) as exc:
        raise DistributionError("capability profile catalog is incomplete") from exc
    if not set(capabilities).issubset(known_capabilities):
        raise DistributionError(
            "standalone capabilities are unknown to capability-profiles.json"
        )
    return {
        **definition,
        "definition_sha256": hashlib.sha256(canonical_json(definition)).hexdigest(),
    }


def _under_tree(relative, tree):
    path = Path(relative)
    parent = Path(tree)
    return path == parent or parent in path.parents


def dependency_allowed(relative, profile):
    """Keep closure inside the selected monotonic capability boundary."""
    if relative in profile["reserved_exact"]:
        return relative in {
            value for key in ("root_files", "runtime_references", "runtime_scripts")
            for value in profile["entries"][key]
        }
    matching = [tree for tree in profile["reserved_trees"] if _under_tree(relative, tree)]
    if matching:
        return any(
            _under_tree(relative, tree)
            for key in ("trees", "runtime_script_trees")
            for tree in profile["entries"][key]
        )
    # Executable code is opt-in only. Static root references remain available
    # unless a higher profile explicitly reserves them.
    return Path(relative).parts[0] != "scripts"


def skill_paths(catalog):
    paths = []
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            paths.extend("protocol/%s" % slug for slug in catalog["protocol"]["skills"])
            continue
        spec = catalog["disciplines"][discipline]
        for phase in spec["phase_order"]:
            paths.extend(
                "%s/%s/%s" % (discipline, phase, slug)
                for slug in spec["phases"][phase]
            )
    return paths


def validate_relative(relative):
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise DistributionError("unsafe distribution path: %s" % relative)
    return path


def ignored(_directory, names):
    return [
        name for name in names
        if (name in IGNORED_NAMES or Path(name).suffix in IGNORED_SUFFIXES
            or BACKUP_FILE.fullmatch(name))
    ]


_GIT_FILE_CACHE = {}


def _git_file_set(mode):
    """Return repository-relative tracked/ignored files, or None outside Git."""
    key = (str(ROOT.resolve()), mode)
    if key in _GIT_FILE_CACHE:
        return _GIT_FILE_CACHE[key]
    arguments = ["git", "-C", str(ROOT), "ls-files", "-z"]
    if mode == "ignored":
        arguments.extend(["--others", "--ignored", "--exclude-standard"])
    try:
        result = subprocess.run(
            arguments, check=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
    except OSError:
        result = None
    if result is None or result.returncode != 0:
        value = None
    else:
        value = {
            os.fsdecode(item)
            for item in result.stdout.split(b"\0") if item
        }
    _GIT_FILE_CACHE[key] = value
    return value


def _source_file_allowed(relative, allow_untracked=False, exact_declared=False):
    label = Path(relative).as_posix()
    if BACKUP_FILE.fullmatch(Path(label).name):
        return False
    ignored_files = _git_file_set("ignored")
    if ignored_files is not None and label in ignored_files:
        return exact_declared
    tracked = _git_file_set("tracked")
    if tracked is None:
        return True
    return label in tracked or allow_untracked or exact_declared


def _copy_regular_file(source, source_status, target):
    descriptor, opened = _safe_source_reader(source, source_status)
    target_flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    target_descriptor = None
    try:
        target_descriptor = os.open(target, target_flags, stat.S_IMODE(opened.st_mode) or 0o600)
        with os.fdopen(descriptor, "rb", closefd=True) as source_handle, os.fdopen(
                target_descriptor, "wb", closefd=True) as target_handle:
            descriptor = target_descriptor = None
            shutil.copyfileobj(source_handle, target_handle, length=1024 * 1024)
            target_handle.flush()
            os.fsync(target_handle.fileno())
            os.fchmod(target_handle.fileno(), stat.S_IMODE(opened.st_mode))
            after = os.fstat(source_handle.fileno())
        stable = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(after, field) for field in stable):
            raise DistributionError(
                "distribution input changed while copying: %s" % _path_label(source)
            )
        os.utime(target, ns=(opened.st_atime_ns, opened.st_mtime_ns), follow_symlinks=False)
    except Exception:
        if descriptor is not None:
            os.close(descriptor)
        if target_descriptor is not None:
            os.close(target_descriptor)
        try:
            target.unlink()
        except FileNotFoundError:
            pass
        raise


def _copy_node(
        source, target, tree_ignore, *, allow_untracked=False, exact_declared=False):
    relative = source.relative_to(ROOT)
    _, status = validate_source_node(relative)
    if stat.S_ISREG(status.st_mode):
        if not _source_file_allowed(
                relative, allow_untracked=allow_untracked,
                exact_declared=exact_declared):
            return False
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target_status = target.lstat()
        except FileNotFoundError:
            target_status = None
        if target_status is not None:
            if (stat.S_ISLNK(target_status.st_mode)
                    or not stat.S_ISREG(target_status.st_mode)
                    or target_status.st_nlink != 1):
                raise DistributionError(
                    "distribution target collision is unsafe: %s" % target
                )
            target_content = _read_checked_regular(
                target, target_status, "duplicate distribution target %s" % target,
            )
            if (target_content != read_source_bytes(relative)
                    or stat.S_IMODE(target_status.st_mode) != stat.S_IMODE(status.st_mode)):
                raise DistributionError(
                    "distribution inputs collide with different content or mode: %s" % target
                )
            return True
        _copy_regular_file(source, status, target)
        return True
    try:
        target_status = target.lstat()
    except FileNotFoundError:
        target_status = None
    if target_status is None:
        target.mkdir()
    elif stat.S_ISLNK(target_status.st_mode) or not stat.S_ISDIR(target_status.st_mode):
        raise DistributionError("distribution directory target collision is unsafe: %s" % target)
    os.chmod(target, stat.S_IMODE(status.st_mode))
    try:
        with os.scandir(source) as scanned:
            entries = sorted(scanned, key=lambda item: item.name)
    except OSError as exc:
        raise DistributionError("cannot scan %s: %s" % (_path_label(source), exc)) from exc
    skipped = set(tree_ignore(str(source), [entry.name for entry in entries]) or [])
    for entry in entries:
        if entry.name in skipped:
            continue
        _copy_node(
            source / entry.name, target / entry.name, tree_ignore,
            allow_untracked=allow_untracked, exact_declared=False,
        )
    return True


def copy_entry(
        relative, destination, tree_ignore=ignored, *, allow_untracked=False):
    relative_path = validate_relative(relative)
    source, status = validate_source_node(relative_path)
    target = destination / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    return _copy_node(
        source, target, tree_ignore,
        allow_untracked=allow_untracked,
        exact_declared=stat.S_ISREG(status.st_mode),
    )


def runtime_dependencies(relative):
    """Return repository runtime files directly named by one text source."""
    relative_path = validate_relative(relative)
    source, _ = validate_source_node(relative_path, allow_directory=False)
    if source.suffix != ".md":
        return set()
    try:
        text = read_source_bytes(relative_path).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DistributionError("runtime source is not UTF-8: %s" % relative) from exc
    dependencies = set()
    for raw_target in MARKDOWN_LINK.findall(text):
        target = raw_target.strip().lstrip("<").rstrip(">").split("#", 1)[0]
        if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue
        candidate = Path(os.path.normpath(str(relative_path.parent / target)))
        try:
            candidate = validate_relative(candidate)
        except DistributionError:
            continue
        if candidate.parts[0] in {"references", "scripts"}:
            try:
                validate_source_node(candidate, allow_directory=False)
            except DistributionError:
                continue
            dependencies.add(str(candidate))
    dependencies.update(match.group(1) for match in RUNTIME_PATH.finditer(text))
    available = set()
    for dependency in dependencies:
        try:
            validate_source_node(dependency, allow_directory=False)
        except DistributionError:
            continue
        available.add(dependency)
    return available


def copy_runtime_closure(seed_entries, destination, profile):
    explicit = set(seed_entries)
    pending = list(seed_entries)
    copied = set()
    while pending:
        relative = pending.pop()
        if relative in copied or not dependency_allowed(relative, profile):
            continue
        copied_ok = copy_entry(
            relative, destination, allow_untracked=relative in explicit,
        )
        if not copied_ok:
            continue
        copied.add(relative)
        pending.extend(
            sorted(
                dependency for dependency in runtime_dependencies(relative)
                if dependency_allowed(dependency, profile) and dependency not in copied
            )
        )
    return copied


def prepare_destination(destination):
    try:
        existing = destination.lstat()
    except FileNotFoundError:
        existing = None
    if existing is not None and (
            stat.S_ISLNK(existing.st_mode) or not stat.S_ISDIR(existing.st_mode)):
        raise DistributionError("destination must be a real directory, not a symlink")
    resolved = destination.resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        pass
    else:
        raise DistributionError("destination must be outside the source repository")
    if destination.exists() and any(destination.iterdir()):
        raise DistributionError("destination exists and is not empty: %s" % destination)
    destination.mkdir(parents=True, exist_ok=True)


def _distribution_files(destination):
    records = []

    def visit(directory):
        try:
            with os.scandir(directory) as scanned:
                entries = sorted(scanned, key=lambda item: item.name)
        except OSError as exc:
            raise DistributionError("cannot inspect built distribution: %s" % exc) from exc
        for entry in entries:
            path = directory / entry.name
            relative = path.relative_to(destination).as_posix()
            try:
                status = path.lstat()
            except OSError as exc:
                raise DistributionError("cannot inspect built output %s: %s" % (relative, exc)) from exc
            if stat.S_ISLNK(status.st_mode):
                raise DistributionError("built distribution contains a symlink: %s" % relative)
            if stat.S_ISDIR(status.st_mode):
                visit(path)
                continue
            if not stat.S_ISREG(status.st_mode):
                raise DistributionError("built distribution contains a special file: %s" % relative)
            if status.st_nlink != 1:
                raise DistributionError("built distribution contains a multi-link file: %s" % relative)
            if relative == DISTRIBUTION_MANIFEST:
                continue
            content = _read_checked_regular(path, status, "built output %s" % relative)
            records.append({
                "bytes": len(content),
                "mode": "%04o" % stat.S_IMODE(status.st_mode),
                "path": relative,
                "sha256": hashlib.sha256(content).hexdigest(),
            })

    visit(destination)
    return records


def validate_source_identity(source_repository, source_commit):
    if (source_repository is None) != (source_commit is None):
        raise DistributionError(
            "source repository and commit provenance must be supplied together"
        )
    if source_repository is not None and not isinstance(source_repository, str):
        raise DistributionError("source repository provenance must be text")
    if source_commit is not None and not isinstance(source_commit, str):
        raise DistributionError("source commit provenance must be text")
    if source_commit is not None and not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", source_commit):
        raise DistributionError("source commit must be a lowercase 40- or 64-hex object ID")
    if source_repository is not None and not re.fullmatch(
            r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source_repository):
        raise DistributionError("source repository must be an owner/repository slug")


def _validate_package_ceiling(
        files, ceiling, *, manifest_bytes=0, include_manifest=False):
    file_count = len(files) + (1 if include_manifest else 0)
    byte_count = sum(item["bytes"] for item in files) + manifest_bytes
    if file_count > ceiling["max_files"] or byte_count > ceiling["max_bytes"]:
        raise DistributionError(
            "distribution exceeds package ceiling: %d/%d files, %d/%d bytes"
            % (file_count, ceiling["max_files"], byte_count, ceiling["max_bytes"])
        )


def build_manifest(
        destination, kind, profile, source_repository=None, source_commit=None):
    validate_source_identity(source_repository, source_commit)
    files = _distribution_files(destination)
    _validate_package_ceiling(files, profile["package_ceiling"])
    files_sha256 = hashlib.sha256(canonical_json(files)).hexdigest()
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "kind": kind,
        "profile": profile["profile"],
        "capability_ceiling": profile["profile"],
        "capabilities": profile["capabilities"],
        "catalog_sha256": hashlib.sha256(read_source_bytes(
            CATALOG.relative_to(ROOT))).hexdigest(),
        "profile_definition_sha256": profile["definition_sha256"],
        "package_ceiling": profile["package_ceiling"],
        "hash_algorithm": "sha256",
        "manifest_path": DISTRIBUTION_MANIFEST,
        "manifest_excludes": [DISTRIBUTION_MANIFEST],
        "source": {"repository": source_repository, "commit": source_commit},
        "files_sha256": files_sha256,
        "files": files,
    }


def write_distribution_manifest(
        destination, kind, profile, source_repository=None, source_commit=None):
    manifest_path = destination / DISTRIBUTION_MANIFEST
    if manifest_path.exists() or manifest_path.is_symlink():
        raise DistributionError("distribution manifest path already exists")
    manifest = build_manifest(
        destination, kind, profile, source_repository, source_commit,
    )
    data = canonical_json(manifest)
    _validate_package_ceiling(
        manifest["files"], manifest["package_ceiling"],
        manifest_bytes=len(data), include_manifest=True,
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(manifest_path, flags, 0o600)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise DistributionError("cannot install distribution manifest: %s" % exc) from exc
    return manifest


def verify_distribution_manifest(
        destination, expected_repository=None, expected_commit=None,
        expected_profile=None):
    validate_source_identity(expected_repository, expected_commit)
    path = destination / DISTRIBUTION_MANIFEST
    try:
        status = path.lstat()
    except OSError as exc:
        raise DistributionError("distribution manifest is unavailable: %s" % exc) from exc
    if (stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode)
            or status.st_nlink != 1):
        raise DistributionError("distribution manifest must be a single-link regular file")
    try:
        manifest_bytes = _read_checked_regular(path, status, "distribution manifest")
        manifest = json.loads(manifest_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise DistributionError("distribution manifest is not valid UTF-8 JSON: %s" % exc) from exc
    legacy_required = {
        "schema_version", "kind", "hash_algorithm", "manifest_path",
        "manifest_excludes", "source", "files_sha256", "files",
    }
    current_required = legacy_required | {
        "profile", "capability_ceiling", "capabilities", "catalog_sha256",
        "profile_definition_sha256", "package_ceiling",
    }
    if not isinstance(manifest, dict):
        raise DistributionError("distribution manifest has unknown or missing fields")
    schema_version = manifest.get("schema_version")
    required = (
        legacy_required if schema_version == LEGACY_MANIFEST_SCHEMA_VERSION
        else current_required
    )
    if set(manifest) != required:
        raise DistributionError("distribution manifest has unknown or missing fields")
    if (schema_version not in {
                LEGACY_MANIFEST_SCHEMA_VERSION, MANIFEST_SCHEMA_VERSION}
            or manifest["hash_algorithm"] != "sha256"
            or manifest["manifest_path"] != DISTRIBUTION_MANIFEST
            or manifest["manifest_excludes"] != [DISTRIBUTION_MANIFEST]
            or manifest["kind"] not in {"plugin", "standalone-skill"}):
        raise DistributionError("distribution manifest identity is invalid")
    if schema_version == MANIFEST_SCHEMA_VERSION:
        capabilities = manifest["capabilities"]
        ceiling = manifest["package_ceiling"]
        catalog_digest = manifest["catalog_sha256"]
        profile_digest = manifest["profile_definition_sha256"]
        if (not isinstance(manifest["profile"], str)
                or manifest["profile"] not in PROFILE_NAMES
                or manifest["capability_ceiling"] != manifest["profile"]
                or (manifest["kind"] == "standalone-skill"
                    and manifest["profile"] != "lite")
                or not isinstance(capabilities, list)
                or len(capabilities) != len(set(capabilities))
                or any(not isinstance(item, str) or not item for item in capabilities)
                or not isinstance(ceiling, dict)
                or set(ceiling) != {"max_files", "max_bytes"}
                or any(isinstance(value, bool) or not isinstance(value, int) or value <= 0
                       for value in ceiling.values())
                or not isinstance(catalog_digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", catalog_digest)
                or not isinstance(profile_digest, str)
                or not re.fullmatch(r"[0-9a-f]{64}", profile_digest)):
            raise DistributionError("distribution manifest profile identity is invalid")
        if expected_profile is not None and manifest["profile"] != expected_profile:
            raise DistributionError("distribution manifest profile does not match")
    elif expected_profile is not None:
        raise DistributionError("legacy distribution manifest has no profile identity")
    source = manifest["source"]
    if not isinstance(source, dict) or set(source) != {"repository", "commit"}:
        raise DistributionError("distribution manifest source provenance is invalid")
    validate_source_identity(source["repository"], source["commit"])
    if expected_repository is not None and source != {
            "repository": expected_repository, "commit": expected_commit}:
        raise DistributionError("distribution manifest source provenance does not match")
    actual_files = _distribution_files(destination)
    if manifest["files"] != actual_files:
        raise DistributionError("distribution files do not match the SHA-256 manifest")
    if schema_version == MANIFEST_SCHEMA_VERSION:
        _validate_package_ceiling(
            actual_files, manifest["package_ceiling"],
            manifest_bytes=len(manifest_bytes), include_manifest=True,
        )
    expected = hashlib.sha256(canonical_json(actual_files)).hexdigest()
    if manifest["files_sha256"] != expected:
        raise DistributionError("distribution manifest aggregate SHA-256 is invalid")
    try:
        final_status = path.lstat()
    except OSError as exc:
        raise DistributionError("distribution manifest disappeared during verification: %s" % exc) from exc
    if _read_checked_regular(path, final_status, "distribution manifest") != manifest_bytes:
        raise DistributionError("distribution manifest changed during verification")
    return manifest


def build_plugin(
        destination, catalog, distribution, profile, slim_frontmatter=False):
    entries_by_kind = profile["entries"]
    skills = skill_paths(catalog)
    for key in ("root_files", "runtime_scripts"):
        for relative in entries_by_kind[key]:
            copy_entry(relative, destination, allow_untracked=True)
    for key in ("trees", "runtime_script_trees"):
        for relative in entries_by_kind[key]:
            copy_entry(relative, destination, allow_untracked=True)
    for relative in skills:
        copy_entry(relative, destination)
    markdown_seeds = [
        relative for relative in entries_by_kind["root_files"]
        if Path(relative).suffix == ".md"
    ]
    markdown_seeds += ["commands/%s.md" % command for command in catalog["commands"]]
    markdown_seeds += [path + "/SKILL.md" for path in skills]
    referenced = set(entries_by_kind["runtime_references"])
    for relative in markdown_seeds:
        referenced.update(
            dependency for dependency in runtime_dependencies(relative)
            if dependency_allowed(dependency, profile)
        )
    copy_runtime_closure(referenced, destination, profile)
    for forbidden in distribution["excluded_top_level"]:
        if (destination / forbidden).exists():
            raise DistributionError("maintenance path leaked into plugin: %s" % forbidden)
    if slim_frontmatter:
        for skill in skills:
            slim_skill_frontmatter(destination / skill / "SKILL.md")
    if "skill-contract-pack-v1" in profile["derived_outputs"]:
        build_skill_contract_pack(destination)


def _generated_skill_contracts(destination):
    """Build exact machine-contract bytes against the distribution sources."""
    source, _ = validate_source_node(
        "scripts/generate-skill-contracts.py", allow_directory=False
    )
    specification = importlib.util.spec_from_file_location(
        "distribution_skill_contracts", source
    )
    if specification is None or specification.loader is None:
        raise DistributionError("cannot load machine-contract generator")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    try:
        return module.build_outputs(destination)
    except module.ContractGenerationError as exc:
        raise DistributionError(
            "cannot build distribution machine contracts: %s" % exc
        ) from exc


def _deterministic_gzip(content):
    compressed = bytearray(gzip.compress(content, compresslevel=9, mtime=0))
    if len(compressed) < 10:
        raise DistributionError("compact skill-contract gzip output is malformed")
    # RFC 1952 byte 9 is the producer OS. Normalize it so archives built by
    # different Python/zlib platforms remain byte-identical.
    compressed[9] = 255
    return bytes(compressed)


def build_skill_contract_pack(destination):
    """Install one bounded, deterministic pack instead of 121 verbose files."""
    outputs = _generated_skill_contracts(destination)
    if (
            len(outputs) != 121
            or "%s/index.json" % SKILL_CONTRACT_TREE not in outputs
            or any(
                not relative.startswith(SKILL_CONTRACT_TREE + "/")
                or not relative.endswith(".json")
                for relative in outputs
            )):
        raise DistributionError(
            "compact skill-contract source must contain 120 contracts plus index"
        )
    files = []
    descriptors = []
    for relative, content in sorted(outputs.items()):
        try:
            content_value = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise DistributionError(
                "generated machine contract is not UTF-8 JSON: %s" % relative
            ) from exc
        descriptor = {
            "path": relative,
            "bytes": len(content),
            "sha256": hashlib.sha256(content).hexdigest(),
        }
        descriptors.append(descriptor)
        files.append({
            **descriptor,
            "content": content_value,
        })
    pack = {
        "schema_version": "1.0",
        "encoding": "canonical-json-v1",
        "source_tree": SKILL_CONTRACT_TREE,
        "file_count": len(files),
        "files_sha256": hashlib.sha256(
            canonical_compact_json(descriptors)
        ).hexdigest(),
        "files": files,
    }
    compressed = _deterministic_gzip(canonical_compact_json(pack))
    if len(compressed) > SKILL_CONTRACT_PACK_MAX_BYTES:
        raise DistributionError(
            "compact skill-contract pack is %d bytes (limit %d)"
            % (len(compressed), SKILL_CONTRACT_PACK_MAX_BYTES)
        )
    target = destination / SKILL_CONTRACT_PACK
    target.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(target, flags, 0o644)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            handle.write(compressed)
            handle.flush()
            os.fsync(handle.fileno())
    except OSError as exc:
        raise DistributionError(
            "cannot install compact skill-contract pack: %s" % exc
        ) from exc


# Frontmatter keys that exist only for publishing-time registries (SkillHub's
# `slug`/`displayName`/`summary` listing identity). They are dead weight on
# every installed host: `skillhub publish` runs from the source repo, so the
# distribution can drop them. Host extensions (metadata.hermes/openclaw) and
# the routing surface (description/when_to_use) stay untouched.
SLIM_FRONTMATTER_KEYS = ("slug", "displayName", "summary")


def slim_skill_frontmatter(skill_file):
    lines = skill_file.read_text(encoding="utf-8").splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        raise DistributionError("cannot slim frontmatter: %s has no frontmatter" % skill_file)
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise DistributionError("cannot slim frontmatter: %s is unterminated" % skill_file) from exc
    kept = [line for line in lines[1:end]
            if not any(line.startswith(key + ":") for key in SLIM_FRONTMATTER_KEYS)]
    required = ("name:", "version:", "description:", "metadata:")
    if any(not any(k.startswith(prefix) for k in kept) for prefix in required):
        raise DistributionError(
            "slimming %s would drop a required frontmatter key — refusing" % skill_file)
    skill_file.write_text("".join([lines[0], *kept, *lines[end:]]), encoding="utf-8")


def build_standalone(destination, catalog, requested):
    known = set(skill_paths(catalog))
    requested = str(validate_relative(requested)).rstrip("/")
    if requested not in known:
        raise DistributionError("unknown skill path: %s" % requested)
    source, _ = validate_source_node(requested)
    try:
        with os.scandir(source) as scanned:
            children = sorted(scanned, key=lambda item: item.name)
    except OSError as exc:
        raise DistributionError("cannot scan standalone skill %s: %s" % (requested, exc)) from exc
    skipped = set(ignored(str(source), [child.name for child in children]))
    for child in children:
        if child.name in skipped:
            continue
        _copy_node(source / child.name, destination / child.name, ignored)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plugin", action="store_true")
    group.add_argument("--skill", metavar="DISCIPLINE/PHASE/SKILL")
    group.add_argument(
        "--verify-manifest", type=Path, metavar="DISTRIBUTION",
        help="Read-only verification of an existing distribution manifest.",
    )
    parser.add_argument(
        "--slim-frontmatter",
        action="store_true",
        help="Plugin builds only: strip publishing-only frontmatter keys "
             "(slug/displayName/summary) from shipped SKILL.md files.",
    )
    parser.add_argument(
        "--profile", choices=PROFILE_NAMES,
        help="Plugin capability profile. Bare --plugin remains a governed alias "
             "with a deprecation warning through v20.",
    )
    parser.add_argument(
        "--source-repository",
        help="Optional owner/repository provenance bound into the output manifest.",
    )
    parser.add_argument(
        "--source-commit",
        help="Optional lowercase Git object ID bound into the output manifest.",
    )
    args = parser.parse_args(argv)
    try:
        if args.verify_manifest is not None:
            if args.output is not None or args.slim_frontmatter:
                raise DistributionError(
                    "--verify-manifest cannot be combined with build options"
                )
            verified = verify_distribution_manifest(
                args.verify_manifest, args.source_repository, args.source_commit,
                expected_profile=args.profile,
            )
            print(
                "verified %s distribution: %d files, manifest sha256:%s"
                % (verified["kind"], len(verified["files"]), verified["files_sha256"])
            )
            return 0
        if args.output is None:
            raise DistributionError("--output is required when building a distribution")
        catalog = load_json(CATALOG)
        distribution = load_json(MANIFEST)
        prepare_destination(args.output)
        if args.slim_frontmatter and not args.plugin:
            raise DistributionError("--slim-frontmatter applies to --plugin builds only")
        if args.plugin:
            selected_profile = args.profile
            if selected_profile is None:
                selected_profile = "governed"
                print(
                    "warning: bare --plugin is a deprecated governed alias through "
                    "v20; pass --profile governed explicitly",
                    file=sys.stderr,
                )
            profile = resolve_plugin_profile(distribution, selected_profile)
            build_plugin(args.output, catalog, distribution, profile,
                         slim_frontmatter=args.slim_frontmatter)
            kind = "plugin"
        else:
            if args.profile is not None:
                raise DistributionError("--profile applies to --plugin builds only")
            build_standalone(args.output, catalog, args.skill)
            kind = "standalone-skill"
            profile = standalone_profile(distribution)
        written = write_distribution_manifest(
            args.output, kind, profile, args.source_repository, args.source_commit,
        )
        verify_distribution_manifest(args.output, expected_profile=profile["profile"])
    except DistributionError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    files = sum(1 for path in args.output.rglob("*") if path.is_file())
    size = sum(path.stat().st_size for path in args.output.rglob("*") if path.is_file())
    display_kind = "standalone skill" if kind == "standalone-skill" else kind
    print(
        "built %s distribution: %d files, %d bytes, manifest sha256:%s"
        % (display_kind, files, size, written["files_sha256"])
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
