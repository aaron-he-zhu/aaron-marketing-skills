#!/usr/bin/env python3
"""Resolve Aaron capability profiles without mutating project state."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
CATALOG_RELATIVE = Path("references/capability-profiles.json")
CONFIG_RELATIVE = Path(".aaron-marketing/profile.json")
ENVIRONMENT_VARIABLE = "AARON_MARKETING_PROFILE"
MAX_CONFIG_BYTES = 4_096
MAX_CATALOG_BYTES = 256_000
MAX_MANIFEST_BYTES = 8_000_000
MAX_EVENT_BYTES = 64_000
MAX_EVENTS = 10_000
MAX_STREAM_BYTES = 64_000_000
ZERO_HASH = "0" * 64
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PROFILE_NAMES = ("lite", "pro", "governed")
TERMINAL_EVENTS = {"run_finished", "run_failed", "run_aborted"}
LIVE_MEMORY_FILES = {
    "hot-cache.md", "decisions.md", "glossary.md", "open-loops.md",
    "session-checkpoint.md",
}
ALWAYS_ON_OVERLAYS = (
    "consent", "claims", "pii-secrets", "external-mutation",
    "audit-verdict", "release-provenance",
)


class ProfileError(ValueError):
    """Raised when a profile boundary cannot be established safely."""

    def __init__(self, code, message):
        super().__init__("%s: %s" % (code, message))
        self.code = code


def _strict_json_loads(text, label):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate key: %s" % key)
            value[key] = item
        return value

    try:
        return json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % item)
            ),
        )
    except (TypeError, ValueError, RecursionError) as exc:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "%s must be strict JSON: %s" % (label, exc)
        ) from exc


def _canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "value is not canonical JSON: %s" % exc
        ) from exc


def _normalized_root(path, label):
    supplied = Path(path)
    try:
        status = supplied.lstat()
    except OSError as exc:
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID", "cannot inspect %s: %s" % (label, exc)
        ) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID", "%s must be a real directory" % label
        )
    try:
        return supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID", "cannot resolve %s: %s" % (label, exc)
        ) from exc


def _read_regular(path, label, maximum, *, missing_ok=False):
    try:
        before = path.lstat()
    except FileNotFoundError:
        if missing_ok:
            return None
        raise ProfileError("PROFILE_FILESYSTEM_INVALID", "%s is missing" % label)
    except OSError as exc:
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID", "cannot inspect %s: %s" % (label, exc)
        ) from exc
    if (
            stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1):
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID",
            "%s must be a single-link regular file" % label,
        )
    if before.st_size > maximum:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "%s exceeds %d bytes" % (label, maximum)
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = None
    try:
        descriptor = os.open(path, flags)
        opened = os.fstat(descriptor)
        if (
                not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino)):
            raise ProfileError(
                "PROFILE_FILESYSTEM_INVALID", "%s changed while opening" % label
            )
        chunks = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        if len(raw) > maximum:
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID", "%s exceeds %d bytes" % (label, maximum)
            )
        stable = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(opened, field) != getattr(after, field) for field in stable):
            raise ProfileError(
                "PROFILE_FILESYSTEM_INVALID", "%s changed while reading" % label
            )
        return raw
    except OSError as exc:
        raise ProfileError(
            "PROFILE_FILESYSTEM_INVALID", "cannot read %s: %s" % (label, exc)
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _decode_json(raw, label):
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "%s must be UTF-8" % label
        ) from exc
    return _strict_json_loads(text, label)


def _exact_object(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID",
            "%s has unknown or missing fields" % label,
        )
    return value


def load_profile_catalog(bundle_root=ROOT):
    bundle = _normalized_root(bundle_root, "bundle root")
    raw = _read_regular(
        bundle / CATALOG_RELATIVE, "capability profile catalog", MAX_CATALOG_BYTES
    )
    value = _decode_json(raw, "capability profile catalog")
    _exact_object(value, {
        "$schema", "schema_version", "runtime_identity", "project_config",
        "environment_variable", "precedence", "profile_order", "capability_order",
        "always_on_overlays", "profiles",
    }, "capability profile catalog")
    if (
            value["$schema"] != "./capability-profiles.schema.json"
            or value["schema_version"] != "1.0"
            or value["project_config"] != str(CONFIG_RELATIVE)
            or value["environment_variable"] != ENVIRONMENT_VARIABLE
            or value["precedence"] != [
                "cli", "environment", "project-config", "state-default"
            ]
            or value["profile_order"] != list(PROFILE_NAMES)
            or value["always_on_overlays"] != list(ALWAYS_ON_OVERLAYS)):
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "capability profile catalog identity is invalid"
        )
    identity = _exact_object(
        value["runtime_identity"], {"major", "ref"}, "runtime_identity"
    )
    if identity != {"major": 19, "ref": "aaron-marketing-runtime:19.0.0"}:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "runtime identity is not v19.0.0"
        )
    capabilities = value["capability_order"]
    if (
            not isinstance(capabilities, list) or not capabilities
            or len(capabilities) != len(set(capabilities))
            or not all(isinstance(item, str) and item for item in capabilities)):
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "capability_order must be unique strings"
        )
    profiles = value["profiles"]
    _exact_object(profiles, PROFILE_NAMES, "profiles")
    previous = set()
    for rank, name in enumerate(PROFILE_NAMES):
        profile = _exact_object(profiles[name], {"rank", "capabilities"}, name)
        declared = profile["capabilities"]
        if (
                profile["rank"] != rank or not isinstance(declared, list)
                or len(declared) != len(set(declared))
                or not set(declared).issubset(capabilities)
                or not previous.issubset(declared)):
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID",
                "profile %s does not form the ordered capability lattice" % name,
            )
        previous = set(declared)
    value["_sha256"] = hashlib.sha256(raw).hexdigest()
    return value


def runtime_identity_reference(bundle_root=ROOT):
    catalog = load_profile_catalog(bundle_root)
    return {
        "kind": "source",
        "ref": catalog["runtime_identity"]["ref"],
        "sha256": catalog["_sha256"],
    }


def _profile_config(project_root):
    path = project_root / CONFIG_RELATIVE
    try:
        parent_status = path.parent.lstat()
    except FileNotFoundError:
        return None, None
    except OSError as exc:
        return None, "PROFILE_FILESYSTEM_INVALID: cannot inspect profile directory: %s" % exc
    if (
            stat.S_ISLNK(parent_status.st_mode)
            or not stat.S_ISDIR(parent_status.st_mode)):
        return None, (
            "PROFILE_FILESYSTEM_INVALID: project profile directory must be a real directory"
        )
    try:
        raw = _read_regular(
            path, "project profile config", MAX_CONFIG_BYTES, missing_ok=True
        )
        if raw is None:
            return None, None
        value = _decode_json(raw, "project profile config")
        _exact_object(value, {"schema_version", "profile"}, "project profile config")
        if value["schema_version"] != "1.0" or value["profile"] not in PROFILE_NAMES:
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID",
                "project profile config identity is invalid",
            )
        return value["profile"], None
    except ProfileError as exc:
        return None, str(exc)


def _distribution_ceiling(bundle_root):
    manifest_path = bundle_root / "distribution-manifest.json"
    raw = _read_regular(
        manifest_path, "distribution manifest", MAX_MANIFEST_BYTES, missing_ok=True
    )
    if raw is not None:
        try:
            value = _decode_json(raw, "distribution manifest")
        except ProfileError:
            return None
        if not isinstance(value, dict):
            return None
        ceiling = value.get("capability_ceiling")
        if ceiling in PROFILE_NAMES:
            return ceiling
        if value.get("schema_version") == "1.0":
            if value.get("kind") == "plugin":
                return "governed"
            if value.get("kind") == "standalone-skill":
                return "lite"
        return None
    required = (
        bundle_root / ".claude-plugin/plugin.json",
        bundle_root / "references/system-catalog.json",
        bundle_root / CATALOG_RELATIVE,
    )
    for path in required:
        try:
            status = path.lstat()
        except OSError:
            return None
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
            return None
    return "governed"


def _safe_directory(path):
    try:
        status = path.lstat()
    except FileNotFoundError:
        return "missing"
    except OSError:
        return "unsafe"
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        return "unsafe"
    return "directory"


def _nonempty_regular(path):
    try:
        status = path.lstat()
    except FileNotFoundError:
        return False, False
    except OSError:
        return False, True
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
        return False, True
    return status.st_size > 0, status.st_nlink != 1


def _canonical_hash(event):
    material = dict(event)
    material.pop("event_hash", None)
    return hashlib.sha256(_canonical_json(material).encode("utf-8")).hexdigest()


def inspect_run_stream(stream, run_id, runtime_ref):
    """Return a verified minimal identity/terminal classification."""
    raw = _read_regular(
        stream, "run event stream %s" % run_id,
        MAX_STREAM_BYTES,
    )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "run event stream must be UTF-8"
        ) from exc
    lines = text.splitlines(keepends=True)
    if not lines or len(lines) > MAX_EVENTS:
        raise ProfileError(
            "PROFILE_DOCUMENT_INVALID", "run event stream has an invalid event count"
        )
    previous_hash = ZERO_HASH
    terminal_seen = False
    first = None
    last = None
    for offset, line in enumerate(lines, 1):
        if not line.endswith("\n") or len(line.encode("utf-8")) > MAX_EVENT_BYTES:
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID",
                "run event %d is truncated or oversized" % offset,
            )
        event = _strict_json_loads(line, "run event %d" % offset)
        if not isinstance(event, dict):
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID", "run event %d must be an object" % offset
            )
        if terminal_seen:
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID", "run event appears after terminal state"
            )
        if (
                event.get("run_id") != run_id or event.get("offset") != offset
                or not SHA256.fullmatch(str(event.get("previous_hash", "")))
                or not SHA256.fullmatch(str(event.get("event_hash", "")))
                or event["previous_hash"] != previous_hash
                or event["event_hash"] != _canonical_hash(event)):
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID",
                "run event %d fails identity/hash continuity" % offset,
            )
        if offset == 1 and event.get("event_type") != "run_started":
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID", "first run event is not run_started"
            )
        if offset > 1 and event.get("event_type") == "run_started":
            raise ProfileError(
                "PROFILE_DOCUMENT_INVALID", "run_started is not the first event"
            )
        if first is None:
            first = event
        last = event
        previous_hash = event["event_hash"]
        terminal_seen = event.get("event_type") in TERMINAL_EVENTS
    references = first.get("references")
    is_v19 = bool(
        isinstance(references, list)
        and any(
            isinstance(item, dict)
            and item.get("kind") == "source"
            and item.get("ref") == runtime_ref
            and SHA256.fullmatch(str(item.get("sha256", "")))
            for item in references
        )
    )
    return {
        "identity": "v19" if is_v19 else "pre-v19",
        "terminal": last.get("event_type") in TERMINAL_EVENTS,
        "event_type": last.get("event_type"),
    }


def _scan_state(project_root, catalog):
    canonical = False
    live = False
    unsafe = []
    memory = project_root / "memory"
    memory_kind = _safe_directory(memory)
    if memory_kind == "unsafe":
        return {
            "live_state_present": True,
            "canonical_state_present": True,
            "pre_v19_nonterminal_runs": [],
            "v19_nonterminal_runs": [],
            "unverifiable_runs": [],
            "unverifiable_state_paths": ["memory"],
        }
    if memory_kind == "missing":
        return {
            "live_state_present": False,
            "canonical_state_present": False,
            "pre_v19_nonterminal_runs": [],
            "v19_nonterminal_runs": [],
            "unverifiable_runs": [],
            "unverifiable_state_paths": [],
        }
    for name in LIVE_MEMORY_FILES:
        present, bad = _nonempty_regular(memory / name)
        live |= present
        if bad:
            unsafe.append("memory/" + name)
    for directory_name in ("events", "projections"):
        directory = memory / directory_name
        kind = _safe_directory(directory)
        if kind == "unsafe":
            unsafe.append("memory/" + directory_name)
            canonical = True
            live = True
            continue
        if kind == "missing":
            continue
        try:
            entries = list(os.scandir(directory))
        except OSError:
            unsafe.append("memory/" + directory_name)
            canonical = True
            live = True
            continue
        for entry in entries:
            path = directory / entry.name
            present, bad = _nonempty_regular(path)
            canonical |= present
            live |= present
            if bad:
                unsafe.append("memory/%s/%s" % (directory_name, entry.name))
    pre_v19 = []
    v19 = []
    unverifiable = []
    runs = memory / "runs"
    runs_kind = _safe_directory(runs)
    if runs_kind == "unsafe":
        unsafe.append("memory/runs")
    elif runs_kind == "directory":
        try:
            entries = sorted(os.scandir(runs), key=lambda item: item.name)
        except OSError:
            entries = []
            unsafe.append("memory/runs")
        for entry in entries:
            try:
                uuid.UUID(entry.name)
            except (ValueError, AttributeError):
                continue
            run_dir = runs / entry.name
            try:
                status = run_dir.lstat()
            except OSError:
                unverifiable.append(entry.name)
                pre_v19.append(entry.name)
                live = True
                continue
            if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
                unverifiable.append(entry.name)
                pre_v19.append(entry.name)
                live = True
                continue
            stream = run_dir / "events.ndjson"
            try:
                stream_status = stream.lstat()
            except FileNotFoundError:
                continue
            except OSError:
                unverifiable.append(entry.name)
                pre_v19.append(entry.name)
                live = True
                continue
            live = True
            if (
                    stat.S_ISLNK(stream_status.st_mode)
                    or not stat.S_ISREG(stream_status.st_mode)
                    or stream_status.st_nlink != 1):
                unverifiable.append(entry.name)
                pre_v19.append(entry.name)
                continue
            try:
                inspected = inspect_run_stream(
                    stream, entry.name, catalog["runtime_identity"]["ref"]
                )
            except ProfileError:
                unverifiable.append(entry.name)
                pre_v19.append(entry.name)
                continue
            if inspected["terminal"]:
                continue
            if inspected["identity"] == "v19":
                v19.append(entry.name)
            else:
                pre_v19.append(entry.name)
    return {
        "live_state_present": bool(live or canonical),
        "canonical_state_present": bool(canonical),
        "pre_v19_nonterminal_runs": sorted(set(pre_v19)),
        "v19_nonterminal_runs": sorted(set(v19)),
        "unverifiable_runs": sorted(set(unverifiable)),
        "unverifiable_state_paths": sorted(set(unsafe)),
    }


def _capability_map(catalog, profile):
    enabled = set()
    if profile == "legacy-read-only":
        enabled.update(catalog["profiles"]["lite"]["capabilities"])
    elif profile in PROFILE_NAMES:
        enabled.update(catalog["profiles"][profile]["capabilities"])
    return {
        name: name in enabled
        for name in catalog["capability_order"]
    }


def _base_resolution(catalog, ceiling, state):
    return {
        "schema_version": "1.0",
        "status": "blocked",
        "reason_code": "PHYSICAL_CEILING_UNKNOWN",
        "origin": "unknown-ceiling",
        "requested_profile": None,
        "effective_profile": None,
        "package_ceiling": ceiling,
        "runtime_identity": {
            **catalog["runtime_identity"],
            "sha256": catalog["_sha256"],
        },
        "capabilities": _capability_map(catalog, None),
        "safety_overlays": {
            name: True for name in catalog["always_on_overlays"]
        },
        "state": state,
        "policy": {
            "inline_read_allowed": True,
            "canonical_read_allowed": True,
            "canonical_write_allowed": False,
            "new_run_allowed": False,
            "registry_write_allowed": False,
            "external_mutation_authorized": False,
        },
        "required_action": "install-verifiable-package",
    }


def resolve_profile(
        project_root, *, bundle_root=ROOT, cli_profile=None, environ=None,
):
    """Resolve the effective profile and policy without writing any path."""
    project = _normalized_root(project_root, "project root")
    bundle = _normalized_root(bundle_root, "bundle root")
    catalog = load_profile_catalog(bundle)
    ceiling = _distribution_ceiling(bundle)
    state = _scan_state(project, catalog)
    result = _base_resolution(catalog, ceiling, state)
    config_profile, config_error = _profile_config(project)
    if config_error is not None:
        result.update({
            "reason_code": "PROFILE_CONFIG_INVALID",
            "origin": "invalid-config",
            "required_action": "repair-profile-config",
        })
        return result
    environment = os.environ if environ is None else environ
    env_present = ENVIRONMENT_VARIABLE in environment
    env_profile = environment.get(ENVIRONMENT_VARIABLE)
    if cli_profile is not None and cli_profile not in PROFILE_NAMES:
        result.update({
            "reason_code": "PROFILE_CLI_INVALID",
            "origin": "invalid-cli",
            "required_action": "choose-supported-profile",
        })
        return result
    if cli_profile is None and env_present and env_profile not in PROFILE_NAMES:
        result.update({
            "reason_code": "PROFILE_ENV_INVALID",
            "origin": "invalid-environment",
            "required_action": "repair-profile-environment",
        })
        return result
    if ceiling not in PROFILE_NAMES:
        return result
    if cli_profile is not None:
        requested = cli_profile
        origin = "cli"
    elif env_present:
        requested = env_profile
        origin = "environment"
    elif config_profile is not None:
        requested = config_profile
        origin = "project-config"
    elif state["live_state_present"]:
        requested = None
        origin = "legacy-state"
    else:
        requested = "lite"
        origin = "fresh-default"
    if requested is not None:
        ranks = {
            name: catalog["profiles"][name]["rank"] for name in PROFILE_NAMES
        }
        if ranks[requested] > ranks[ceiling]:
            result.update({
                "reason_code": "PROFILE_CEILING_EXCEEDED",
                "origin": origin,
                "requested_profile": requested,
                "required_action": "choose-supported-profile",
            })
            return result
        effective = requested
    else:
        effective = "legacy-read-only"
    unsafe_state = bool(
        state["unverifiable_runs"] or state["unverifiable_state_paths"]
    )
    legacy_active = bool(state["pre_v19_nonterminal_runs"])
    if unsafe_state:
        status = "read-only" if effective in {"lite", "legacy-read-only"} else "blocked"
        reason = "PROJECT_STATE_UNVERIFIABLE"
        action = "repair-project-state"
    elif legacy_active:
        status = "read-only" if effective in {"lite", "legacy-read-only"} else "blocked"
        reason = "LEGACY_RUN_BLOCKED"
        action = "drain-pre-v19-runs"
    elif effective == "legacy-read-only":
        status = "read-only"
        reason = "LEGACY_STATE_READ_ONLY"
        action = "select-profile"
    else:
        status = "ready"
        reason = "FRESH_DEFAULT_LITE" if origin == "fresh-default" else "PROFILE_RESOLVED"
        action = None
    activated = effective if status != "blocked" else None
    capabilities = _capability_map(catalog, activated)
    governed_write = status == "ready" and activated == "governed"
    result.update({
        "status": status,
        "reason_code": reason,
        "origin": origin,
        "requested_profile": requested,
        "effective_profile": activated,
        "capabilities": capabilities,
        "policy": {
            "inline_read_allowed": True,
            "canonical_read_allowed": True,
            "canonical_write_allowed": governed_write,
            "new_run_allowed": governed_write,
            "registry_write_allowed": governed_write,
            "external_mutation_authorized": False,
        },
        "required_action": action,
    })
    return result


def classify_run(project_root, run_id, *, bundle_root=ROOT):
    project = _normalized_root(project_root, "project root")
    catalog = load_profile_catalog(bundle_root)
    try:
        uuid.UUID(run_id)
    except (TypeError, ValueError, AttributeError) as exc:
        raise ProfileError("RUN_ID_INVALID", "run_id must be a UUID") from exc
    stream = project / "memory" / "runs" / run_id / "events.ndjson"
    raw = _read_regular(
        stream, "run event stream %s" % run_id,
        MAX_STREAM_BYTES, missing_ok=True,
    )
    if raw is None:
        return {"identity": "missing", "terminal": False, "event_type": None}
    return inspect_run_stream(
        stream, run_id, catalog["runtime_identity"]["ref"]
    )


def require_new_run(
        project_root, *, bundle_root=ROOT, cli_profile=None, environ=None,
):
    resolution = resolve_profile(
        project_root, bundle_root=bundle_root, cli_profile=cli_profile,
        environ=environ,
    )
    if resolution["reason_code"] == "LEGACY_RUN_BLOCKED":
        raise ProfileError(
            "LEGACY_RUN_BLOCKED",
            "drain every pre-v19 nonterminal run before a v19 run or registry write",
        )
    if not resolution["policy"]["new_run_allowed"]:
        raise ProfileError(
            resolution["reason_code"]
            if resolution["status"] == "blocked"
            else "PROFILE_CAPABILITY_BLOCKED",
            "a new verified run requires an effective Governed profile",
        )
    return resolution


def require_existing_run(
        project_root, run_id, *, bundle_root=ROOT, cli_profile=None, environ=None,
):
    classification = classify_run(project_root, run_id, bundle_root=bundle_root)
    if classification["identity"] == "missing":
        return classification
    if classification["identity"] != "v19" and not classification["terminal"]:
        raise ProfileError(
            "LEGACY_RUN_BLOCKED",
            "v19 cannot append to or resume a pre-v19 nonterminal run",
        )
    resolution = resolve_profile(
        project_root, bundle_root=bundle_root, cli_profile=cli_profile,
        environ=environ,
    )
    if resolution["reason_code"] in {
            "PROFILE_CONFIG_INVALID", "PROFILE_ENV_INVALID", "PROFILE_CLI_INVALID",
            "PHYSICAL_CEILING_UNKNOWN", "PROJECT_STATE_UNVERIFIABLE",
            "LEGACY_RUN_BLOCKED"}:
        raise ProfileError(
            resolution["reason_code"],
            "repair the profile boundary before operating an existing run",
        )
    return classification


def _output(value, compact):
    if compact:
        print(_canonical_json(value))
    else:
        print(json.dumps(
            value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False
        ))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root (default: current directory).")
    parser.add_argument(
        "--bundle-root", default=str(ROOT),
        help="Immutable Aaron bundle root.",
    )
    commands = parser.add_subparsers(dest="operation", required=True)
    diagnose = commands.add_parser(
        "diagnose", help="Resolve and print the effective read/write policy."
    )
    diagnose.add_argument(
        "--profile", choices=PROFILE_NAMES,
        help="One-invocation requested profile; does not write project config.",
    )
    diagnose.add_argument(
        "--json", action="store_true",
        help="Emit compact JSON for a host hook fast path.",
    )
    args = parser.parse_args(argv)
    try:
        result = resolve_profile(
            args.root, bundle_root=args.bundle_root, cli_profile=args.profile,
        )
        _output(result, args.json)
        return 2 if result["status"] == "blocked" else 0
    except ProfileError as exc:
        print("profile-resolver: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
