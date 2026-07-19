#!/usr/bin/env python3
"""Private, append-only operational run evidence.

This runtime intentionally has no registry authority. It records bounded metadata,
hashes, and references under ignored ``memory/runs/`` paths. Its hook adapter hashes
host identities and never copies prompt/tool payloads; other callers must supply
opaque non-sensitive IDs and references.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat as statmod
import subprocess
import sys
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - writes fail closed without POSIX locking
    fcntl = None


SCHEMA_VERSION = "1.0"
NAMESPACE = uuid.UUID("5a325540-897b-44fe-8022-a5c59dc12bcc")
ZERO_HASH = "0" * 64
MAX_EVENT_BYTES = 64_000
MAX_DOCUMENT_BYTES = 1_000_000
MAX_EVENTS = 10_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,511}$")
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
EVENT_TYPES = {
    "run_started", "route_selected", "context_resolved", "turn_started",
    "turn_snapshot_created", "hook_observed", "tool_requested", "tool_allowed",
    "tool_blocked", "tool_finished", "artifact_validated", "branch_created",
    "turn_finished", "save_point_created", "loop_state_changed", "run_waiting",
    "run_finished", "run_failed", "run_aborted",
}
TERMINAL_TYPES = {"run_finished", "run_failed", "run_aborted"}
STATUSES = {"started", "succeeded", "failed", "blocked", "waiting", "skipped", "cancelled"}
ACTOR_TYPES = {"user", "host", "skill", "system", "tool", "adapter"}
SUBJECT_KINDS = {"run", "route", "context", "turn", "hook", "tool", "artifact", "save-point", "loop", "adapter"}
REFERENCE_KINDS = {
    "artifact", "schema", "context-manifest", "turn-snapshot", "save-point",
    "run-envelope", "run", "registry-projection", "evaluation", "loop", "source",
}
REGISTRIES = {"entities", "creators", "claims", "consent", "launches", "channels", "narrative"}
REQUEST_FIELDS = {
    "schema_version", "run_id", "idempotency_key", "event_type", "occurred_at",
    "actor", "parent_event_id", "turn_id", "status", "subject", "reason_code",
    "references", "metrics", "dimensions",
}
ASSIGNED_FIELDS = {"event_id", "offset", "recorded_at", "request_hash", "previous_hash", "event_hash"}
DIMENSION_FIELDS = {
    "hook_name", "tool_name", "validator", "evidence_mode", "adapter_name",
    "model_id", "route_reason", "failure_class", "loop_state", "branch_reason",
}
INTERNAL_EVENT_TYPES = {
    "turn_snapshot_created", "save_point_created", "run_waiting",
    "run_finished", "run_failed", "run_aborted",
}
RESERVED_IDEMPOTENCY_PREFIXES = ("snapshot:", "save:", "envelope:", "hook:")


class RunEventError(ValueError):
    pass


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
        raise RunEventError("%s must be strict JSON: %s" % (label, exc)) from exc


def read_json(path, label="document"):
    if str(path) == "-":
        raw = sys.stdin.buffer.read(MAX_DOCUMENT_BYTES + 1)
    else:
        try:
            with open(path, "rb") as handle:
                raw = handle.read(MAX_DOCUMENT_BYTES + 1)
        except OSError as exc:
            raise RunEventError("cannot read %s %s: %s" % (label, path, exc)) from exc
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise RunEventError("%s exceeds %d bytes" % (label, MAX_DOCUMENT_BYTES))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunEventError("%s must be UTF-8" % label) from exc
    return strict_json_loads(text, label)


def canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise RunEventError("value must contain finite JSON data: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    try:
        with anchored_regular_file(path) as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise RunEventError("cannot hash %s: %s" % (path, exc)) from exc
    return digest.hexdigest()


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value, label):
    if not isinstance(value, str) or not value:
        raise RunEventError("%s must be a non-empty ISO date-time" % label)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RunEventError("%s must be an ISO date-time" % label) from exc
    if parsed.tzinfo is None:
        raise RunEventError("%s must include a timezone" % label)
    return parsed


def validate_uuid(value, label):
    if not isinstance(value, str):
        raise RunEventError("%s must be a UUID string" % label)
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError) as exc:
        raise RunEventError("%s must be a UUID string" % label) from exc
    if str(parsed) != value:
        raise RunEventError("%s must use canonical lowercase UUID form" % label)
    return value


def validate_safe_id(value, label):
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or "@" in value:
        raise RunEventError("%s must be a non-PII safe identifier" % label)
    return value


def validate_ref(value, label):
    if isinstance(value, str) and (
            value.startswith("/") or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise RunEventError("%s must not be absolute or contain empty/dot path components" % label)
    if not isinstance(value, str) or not SAFE_REF.fullmatch(value) or "@" in value:
        raise RunEventError("%s must be an opaque or project-relative safe reference" % label)
    return value


def validate_sha(value, label):
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise RunEventError("%s must be a lowercase SHA-256 digest" % label)
    return value


def exact_object(value, required, optional, label):
    if not isinstance(value, dict):
        raise RunEventError("%s must be an object" % label)
    missing = sorted(set(required) - set(value))
    extra = sorted(set(value) - set(required) - set(optional))
    if missing:
        raise RunEventError("%s is missing fields: %s" % (label, ", ".join(missing)))
    if extra:
        raise RunEventError("%s has unknown fields: %s" % (label, ", ".join(extra)))
    return value


def validate_offsets(value, label="registry_offsets"):
    exact_object(value, REGISTRIES, set(), label)
    for name, offset in value.items():
        if offset is not None and (
                not isinstance(offset, int) or isinstance(offset, bool) or offset < 0):
            raise RunEventError("%s.%s must be null or a non-negative integer" % (label, name))
    return value


def validate_reference(value, label):
    exact_object(value, {"kind", "ref"}, {"sha256", "revision", "offset"}, label)
    if value["kind"] not in REFERENCE_KINDS:
        raise RunEventError("%s.kind is unsupported" % label)
    validate_ref(value["ref"], label + ".ref")
    if "sha256" in value:
        validate_sha(value["sha256"], label + ".sha256")
    for key in ("revision", "offset"):
        if key in value and (
                not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] < 0):
            raise RunEventError("%s.%s must be a non-negative integer" % (label, key))
    return value


def validate_event_request(request):
    exact_object(request, REQUEST_FIELDS - {"reason_code"}, {"reason_code"}, "event request")
    if request["schema_version"] != SCHEMA_VERSION:
        raise RunEventError("event request schema_version must be %s" % SCHEMA_VERSION)
    validate_uuid(request["run_id"], "run_id")
    validate_safe_id(request["idempotency_key"], "idempotency_key")
    if request["event_type"] not in EVENT_TYPES:
        raise RunEventError("event_type is unsupported")
    parse_datetime(request["occurred_at"], "occurred_at")
    exact_object(request["actor"], {"type", "id"}, set(), "actor")
    if request["actor"]["type"] not in ACTOR_TYPES:
        raise RunEventError("actor.type is unsupported")
    validate_safe_id(request["actor"]["id"], "actor.id")
    parent = request["parent_event_id"]
    if parent is not None:
        validate_uuid(parent, "parent_event_id")
    turn_id = request["turn_id"]
    if turn_id is not None:
        validate_safe_id(turn_id, "turn_id")
    if request["status"] not in STATUSES:
        raise RunEventError("status is unsupported")
    exact_object(request["subject"], {"kind", "ref"}, set(), "subject")
    if request["subject"]["kind"] not in SUBJECT_KINDS:
        raise RunEventError("subject.kind is unsupported")
    validate_safe_id(request["subject"]["ref"], "subject.ref")
    if "reason_code" in request:
        validate_safe_id(request["reason_code"], "reason_code")
    references = request["references"]
    if not isinstance(references, list) or len(references) > 32:
        raise RunEventError("references must be an array with at most 32 entries")
    for index, reference in enumerate(references):
        validate_reference(reference, "references[%d]" % index)
    metrics = request["metrics"]
    if not isinstance(metrics, dict) or len(metrics) > 32:
        raise RunEventError("metrics must be an object with at most 32 entries")
    for key, value in metrics.items():
        if not SAFE_FIELD.fullmatch(key):
            raise RunEventError("metrics contains an unsafe field name")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
            raise RunEventError("metrics.%s must be finite numeric metadata" % key)
    dimensions = request["dimensions"]
    if not isinstance(dimensions, dict) or len(dimensions) > 16:
        raise RunEventError("dimensions must be an object with at most 16 entries")
    for key, value in dimensions.items():
        if key not in DIMENSION_FIELDS:
            raise RunEventError("dimensions.%s is not in the metadata field allowlist" % key)
        validate_safe_id(value, "dimensions.%s" % key)
    if request["event_type"] == "run_started":
        if parent is not None or turn_id is not None or request["subject"] != {"kind": "run", "ref": request["run_id"]}:
            raise RunEventError("run_started must be a root run subject with no parent or turn")
    elif parent is None:
        raise RunEventError("non-root events require parent_event_id")
    validate_event_semantics(request)
    return strict_json_loads(canonical_json(request), "normalized event request")


def validate_event_semantics(request):
    event_type = request["event_type"]
    status = request["status"]
    subject = request["subject"]
    references = request["references"]
    turn_id = request["turn_id"]
    required = {
        "run_started": ("started", "run"),
        "turn_started": ("started", "turn"),
        "turn_snapshot_created": ("succeeded", "turn"),
        "tool_requested": ("started", "tool"),
        "tool_allowed": ("started", "tool"),
        "tool_blocked": ("blocked", "tool"),
        "save_point_created": ("succeeded", "save-point"),
        "run_waiting": ("waiting", "run"),
        "run_finished": ("succeeded", "run"),
        "run_failed": ("failed", "run"),
        "run_aborted": ("cancelled", "run"),
    }
    if event_type in required:
        expected_status, expected_subject = required[event_type]
        if status != expected_status or subject["kind"] != expected_subject:
            raise RunEventError(
                "%s requires status=%s and subject.kind=%s"
                % (event_type, expected_status, expected_subject)
            )
    if event_type in {"run_started", "run_waiting", *TERMINAL_TYPES}:
        if subject["ref"] != request["run_id"] or turn_id is not None:
            raise RunEventError("run lifecycle events require the matching run subject and no turn_id")
    if event_type in {"turn_started", "turn_snapshot_created", "turn_finished"}:
        if turn_id is None or subject["kind"] != "turn" or subject["ref"] != turn_id:
            raise RunEventError("turn lifecycle events require a matching turn subject")
    if event_type in {"tool_requested", "tool_allowed", "tool_blocked", "tool_finished"}:
        if turn_id is None or subject["kind"] != "tool":
            raise RunEventError("tool lifecycle events require turn_id and a tool subject")
    if event_type == "tool_finished" and status not in {"succeeded", "failed"}:
        raise RunEventError("tool_finished requires status=succeeded or status=failed")
    if event_type == "artifact_validated":
        if (
                status != "succeeded" or subject["kind"] != "artifact"
                or len(references) != 1 or references[0]["kind"] != "artifact"
                or "sha256" not in references[0]
                or "validator" not in request["dimensions"]):
            raise RunEventError(
                "artifact_validated requires a succeeded artifact subject, one hashed artifact reference, and validator dimension"
            )
    typed_reference = {
        "turn_snapshot_created": "turn-snapshot",
        "save_point_created": "save-point",
    }.get(event_type)
    if typed_reference and (
            len(references) != 1 or references[0]["kind"] != typed_reference
            or "sha256" not in references[0]):
        raise RunEventError("%s requires one hashed %s reference" % (event_type, typed_reference))
    if event_type in {"run_waiting", *TERMINAL_TYPES} and (
            len(references) != 1 or references[0]["kind"] != "run-envelope"
            or "sha256" not in references[0]
            or "/envelopes/" not in references[0]["ref"]):
        raise RunEventError("run envelope events require one hashed envelope artifact reference")


def event_ancestry(events, parent_event_id):
    """Return the root-to-parent ancestry selected by ``parent_event_id``."""
    if parent_event_id is None:
        return []
    by_id = {event["event_id"]: event for event in events}
    ancestry = []
    cursor = by_id.get(parent_event_id)
    while cursor is not None:
        ancestry.append(cursor)
        cursor = by_id.get(cursor["parent_event_id"])
    ancestry.reverse()
    return ancestry


def validate_event_transition(request, events):
    """Validate stream-relative lifecycle transitions on the selected branch."""
    event_type = request["event_type"]
    if event_type not in {"tool_requested", "tool_allowed", "tool_blocked", "tool_finished"}:
        return
    turn_id = request["turn_id"]
    tool_ref = request["subject"]["ref"]
    state = None
    seen_on_other_turn = False
    for event in event_ancestry(events, request["parent_event_id"]):
        if event["subject"]["kind"] != "tool" or event["subject"]["ref"] != tool_ref:
            continue
        if event["turn_id"] != turn_id:
            seen_on_other_turn = True
            continue
        if event["event_type"] == "tool_requested":
            state = "requested"
        elif event["event_type"] == "tool_allowed":
            state = "allowed"
        elif event["event_type"] in {"tool_blocked", "tool_finished"}:
            state = "closed"
    if seen_on_other_turn:
        raise RunEventError("tool identity cannot be reused across turns on the selected branch")
    if event_type == "tool_requested" and state is not None:
        raise RunEventError("tool_requested cannot reuse a tool identity on the selected turn branch")
    if event_type == "tool_allowed" and state not in {None, "requested"}:
        raise RunEventError("tool_allowed requires a new or requested tool on the selected turn branch")
    if event_type in {"tool_blocked", "tool_finished"} and state not in {"requested", "allowed"}:
        raise RunEventError(
            "%s requires a matching open tool ancestor on the same turn branch" % event_type
        )


def event_hash(event):
    material = dict(event)
    material.pop("event_hash", None)
    return sha256_json(material)


def validate_stored_event(event, line_number, run_id, previous_hash, seen_ids, seen_keys):
    exact_object(event, REQUEST_FIELDS - {"reason_code"} | ASSIGNED_FIELDS,
                 {"reason_code"}, "event line %d" % line_number)
    request = {key: event[key] for key in REQUEST_FIELDS if key in event}
    validate_event_request(request)
    if request["run_id"] != run_id:
        raise RunEventError("run_id mismatch at line %d" % line_number)
    if event["offset"] != line_number or not isinstance(event["offset"], int) or isinstance(event["offset"], bool):
        raise RunEventError("event offset discontinuity at line %d" % line_number)
    validate_uuid(event["event_id"], "event_id at line %d" % line_number)
    parse_datetime(event["recorded_at"], "recorded_at at line %d" % line_number)
    for field in ("request_hash", "previous_hash", "event_hash"):
        validate_sha(event[field], "%s at line %d" % (field, line_number))
    if event["request_hash"] != sha256_json(request):
        raise RunEventError("request hash mismatch at line %d" % line_number)
    expected_id = str(uuid.uuid5(NAMESPACE, run_id + ":" + request["idempotency_key"]))
    if event["event_id"] != expected_id:
        raise RunEventError("event ID mismatch at line %d" % line_number)
    if event["previous_hash"] != previous_hash:
        raise RunEventError("event hash chain mismatch at line %d" % line_number)
    if event["event_hash"] != event_hash(event):
        raise RunEventError("event hash mismatch at line %d" % line_number)
    if event["event_id"] in seen_ids or request["idempotency_key"] in seen_keys:
        raise RunEventError("duplicate event identity at line %d" % line_number)
    if line_number == 1:
        if event["event_type"] != "run_started":
            raise RunEventError("first event must be run_started")
    else:
        if event["event_type"] == "run_started":
            raise RunEventError("run_started may appear only at line 1")
        if event["parent_event_id"] not in seen_ids:
            raise RunEventError("parent_event_id must reference an earlier event at line %d" % line_number)
    seen_ids.add(event["event_id"])
    seen_keys.add(request["idempotency_key"])
    return event


def read_stream(handle, run_id):
    handle.seek(0)
    events = []
    previous_hash = ZERO_HASH
    seen_ids = set()
    seen_keys = set()
    terminal = False
    line_number = 0
    try:
        while True:
            raw = handle.readline(MAX_EVENT_BYTES + 1)
            if not raw:
                break
            line_number += 1
            if line_number > MAX_EVENTS:
                raise RunEventError("event stream exceeds %d events" % MAX_EVENTS)
            if not raw.endswith("\n"):
                if len(raw) >= MAX_EVENT_BYTES + 1:
                    raise RunEventError("event at line %d exceeds size limit" % line_number)
                raise RunEventError("event stream has a truncated final line")
            if len(raw.encode("utf-8")) > MAX_EVENT_BYTES:
                raise RunEventError("event at line %d exceeds size limit" % line_number)
            event = strict_json_loads(raw, "event line %d" % line_number)
            if terminal:
                raise RunEventError("event appears after terminal run event at line %d" % line_number)
            validate_stored_event(event, line_number, run_id, previous_hash, seen_ids, seen_keys)
            validate_event_transition(event, events)
            terminal = event["event_type"] in TERMINAL_TYPES
            previous_hash = event["event_hash"]
            events.append(event)
    except UnicodeDecodeError as exc:
        raise RunEventError("event stream must be UTF-8") from exc
    return events


def project_events(run_id, events):
    if not events:
        return {
            "schema_version": SCHEMA_VERSION, "authoritative": False, "run_id": run_id,
            "status": "absent", "last_offset": 0, "last_event_id": None,
            "last_event_hash": ZERO_HASH, "root_event_id": None, "head_event_id": None,
            "leaf_event_ids": [], "branch_points": [], "turn_ids": [],
            "open_tool_refs": [], "selected_path_event_ids": [],
            "validated_artifacts": [], "last_turn_snapshot_ref": None,
            "last_turn_snapshot_sha256": None, "last_save_point_ref": None,
            "last_save_point_sha256": None, "run_envelope_ref": None,
            "run_envelope_sha256": None,
            "started_at": None, "updated_at": None,
        }
    children = {event["event_id"]: 0 for event in events}
    turn_ids = set()
    for event in events:
        parent = event["parent_event_id"]
        if parent is not None:
            children[parent] += 1
        if event["turn_id"]:
            turn_ids.add(event["turn_id"])
    last = events[-1]
    by_id = {event["event_id"]: event for event in events}
    selected_path = []
    cursor = last
    while cursor is not None:
        selected_path.append(cursor)
        parent_id = cursor["parent_event_id"]
        cursor = by_id.get(parent_id) if parent_id is not None else None
    selected_path.reverse()
    open_tools = set()
    last_snapshot = last_snapshot_hash = last_save = last_save_hash = None
    envelope = envelope_hash = None
    validated_artifacts = []
    for event in selected_path:
        if event["event_type"] in {"tool_requested", "tool_allowed"}:
            open_tools.add(event["subject"]["ref"])
        elif event["event_type"] in {"tool_blocked", "tool_finished"}:
            open_tools.discard(event["subject"]["ref"])
        for reference in event["references"]:
            if reference["kind"] == "turn-snapshot":
                last_snapshot = reference["ref"]
                last_snapshot_hash = reference.get("sha256")
            elif reference["kind"] == "save-point":
                last_save = reference["ref"]
                last_save_hash = reference.get("sha256")
            elif event["event_type"] in {"run_waiting", *TERMINAL_TYPES} and reference["kind"] == "run-envelope":
                envelope = reference["ref"]
                envelope_hash = reference.get("sha256")
            elif event["event_type"] == "artifact_validated" and reference["kind"] == "artifact":
                validated_artifacts.append({
                    "ref": reference["ref"], "sha256": reference.get("sha256"),
                    "validator": event["dimensions"].get("validator"),
                })
    status = {
        "run_finished": "succeeded", "run_failed": "failed", "run_aborted": "aborted",
        "run_waiting": "waiting",
    }.get(last["event_type"], "active")
    return {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "run_id": run_id,
        "status": status,
        "last_offset": last["offset"],
        "last_event_id": last["event_id"],
        "last_event_hash": last["event_hash"],
        "root_event_id": events[0]["event_id"],
        "head_event_id": last["event_id"],
        "leaf_event_ids": sorted(event_id for event_id, count in children.items() if count == 0),
        "branch_points": sorted(event_id for event_id, count in children.items() if count > 1),
        "turn_ids": sorted(turn_ids),
        "open_tool_refs": sorted(open_tools),
        "selected_path_event_ids": [event["event_id"] for event in selected_path],
        "validated_artifacts": validated_artifacts,
        "last_turn_snapshot_ref": last_snapshot,
        "last_turn_snapshot_sha256": last_snapshot_hash,
        "last_save_point_ref": last_save,
        "last_save_point_sha256": last_save_hash,
        "run_envelope_ref": envelope,
        "run_envelope_sha256": envelope_hash,
        "started_at": events[0]["occurred_at"],
        "updated_at": last["recorded_at"],
    }


def _lstat(path, label, missing_ok=False):
    try:
        return os.lstat(path)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise RunEventError("%s does not exist: %s" % (label, path))
    except OSError as exc:
        raise RunEventError("cannot inspect %s %s: %s" % (label, path, exc)) from exc


def normalized_root(root):
    supplied = Path(root)
    status = _lstat(supplied, "project root")
    if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISDIR(status.st_mode):
        raise RunEventError("project root must be a real directory")
    try:
        return supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RunEventError("cannot resolve project root: %s" % exc) from exc


def _dir_fd_supported(function):
    return function in getattr(os, "supports_dir_fd", set())


def safe_mutation_available():
    return (
        os.name == "posix" and fcntl is not None and callable(getattr(os, "fchmod", None))
        and all(_dir_fd_supported(function) for function in (os.open, os.stat, os.mkdir, os.rename, os.unlink, os.link))
    )


def open_directory_anchor(path):
    status = _lstat(path, "runtime directory")
    if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISDIR(status.st_mode):
        raise RunEventError("runtime path must be a real directory: %s" % path)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    absolute = Path(os.path.abspath(path))
    descriptor = None
    try:
        descriptor = os.open(os.path.sep, flags)
        for component in absolute.parts[1:]:
            child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
    except OSError as exc:
        if descriptor is not None:
            os.close(descriptor)
        raise RunEventError("cannot anchor runtime directory %s: %s" % (path, exc)) from exc
    opened = os.fstat(descriptor)
    return descriptor, (opened.st_dev, opened.st_ino)


def anchored_lstat(parent_fd, parent_path, name, missing_ok=False):
    try:
        return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise RunEventError("runtime file does not exist: %s" % (parent_path / name))
    except OSError as exc:
        raise RunEventError("cannot inspect runtime file %s: %s" % (parent_path / name, exc)) from exc


def revalidate_anchor(parent_fd, parent_path, identity):
    opened = os.fstat(parent_fd)
    current = _lstat(parent_path, "runtime directory")
    if (
            statmod.S_ISLNK(current.st_mode) or not statmod.S_ISDIR(current.st_mode)
            or (opened.st_dev, opened.st_ino) != identity
            or (current.st_dev, current.st_ino) != identity):
        raise RunEventError("runtime directory changed during operation: %s" % parent_path)


def open_or_create_directory(parent_fd, parent_path, name):
    child_path = parent_path / name
    created = False
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
        created = True
    except FileExistsError:
        pass
    except OSError as exc:
        raise RunEventError("cannot create runtime directory %s: %s" % (child_path, exc)) from exc
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        child_fd = os.open(name, flags, dir_fd=parent_fd)
        opened = os.fstat(child_fd)
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if (
                statmod.S_ISLNK(entry.st_mode) or not statmod.S_ISDIR(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
            raise RunEventError("runtime path must remain a real directory: %s" % child_path)
        os.fchmod(child_fd, 0o700)
        if created:
            os.fsync(parent_fd)
        return child_fd
    except RunEventError:
        if "child_fd" in locals():
            os.close(child_fd)
        raise
    except OSError as exc:
        if "child_fd" in locals():
            os.close(child_fd)
        raise RunEventError("cannot secure runtime directory %s: %s" % (child_path, exc)) from exc


def ensure_ignored(root, targets):
    try:
        probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        if has_git_marker(root):
            raise RunEventError("cannot verify runtime privacy: %s" % exc) from exc
        return
    if probe.returncode != 0:
        if has_git_marker(root):
            raise RunEventError("cannot verify runtime privacy: git rev-parse failed")
        return
    git_root = Path(probe.stdout.strip()).resolve()
    for target in targets:
        try:
            relative = target.absolute().relative_to(git_root)
        except ValueError as exc:
            raise RunEventError("runtime evidence escapes the Git worktree") from exc
        try:
            checked = subprocess.run(
                ["git", "-C", str(git_root), "check-ignore", "--quiet", "--", str(relative)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RunEventError("cannot verify runtime privacy: %s" % exc) from exc
        if checked.returncode != 0:
            raise RunEventError("refusing run evidence write because %s is not Git-ignored" % relative)


def has_git_marker(path):
    for candidate in (path, *path.parents):
        if _lstat(candidate / ".git", "Git marker", missing_ok=True) is not None:
            return True
    return False


def run_paths(root, run_id, create=False):
    validate_uuid(run_id, "run_id")
    root_path = normalized_root(root)
    run_dir = root_path / "memory" / "runs" / run_id
    stream = run_dir / "events.ndjson"
    projection = run_dir / "session.json"
    if create:
        if not safe_mutation_available():
            raise RunEventError("run mutation requires POSIX dirfd operations and advisory locking")
        ensure_ignored(root_path, [stream, projection,
                                   run_dir / ".session.json.run-tmp"])
        root_fd, _ = open_directory_anchor(root_path)
        descriptors = [root_fd]
        try:
            parent_fd = root_fd
            parent_path = root_path
            for name in ("memory", "runs", run_id):
                child_fd = open_or_create_directory(parent_fd, parent_path, name)
                descriptors.append(child_fd)
                parent_fd = child_fd
                parent_path = parent_path / name
            os.fsync(parent_fd)
        finally:
            for descriptor in reversed(descriptors):
                os.close(descriptor)
    else:
        parent = root_path
        for name in ("memory", "runs", run_id):
            path = parent / name
            status = _lstat(path, "runtime path", missing_ok=True)
            if status is None:
                return stream, projection, run_dir
            if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISDIR(status.st_mode):
                raise RunEventError("runtime path must be a real directory: %s" % path)
            parent = path
    return stream, projection, run_dir


@contextlib.contextmanager
def locked_stream(path, exclusive, create=True):
    if fcntl is None:
        raise RunEventError("run stream access requires POSIX advisory locking")
    parent_fd, identity = open_directory_anchor(path.parent)
    flags = (os.O_RDWR | os.O_APPEND) if exclusive else os.O_RDONLY
    if exclusive and create:
        flags |= os.O_CREAT
    flags |= getattr(os, "O_NOFOLLOW", 0)
    preexisting = anchored_lstat(parent_fd, path.parent, path.name, missing_ok=True) is not None
    try:
        fd = os.open(path.name, flags, 0o600, dir_fd=parent_fd)
    except OSError as exc:
        os.close(parent_fd)
        raise RunEventError("cannot open run event stream %s: %s" % (path, exc)) from exc
    try:
        opened = os.fstat(fd)
        entry = anchored_lstat(parent_fd, path.parent, path.name)
        if (
                not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or statmod.S_ISLNK(entry.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
            raise RunEventError("run event stream must be a stable single-link regular file")
        if exclusive:
            os.fchmod(fd, 0o600)
            if not preexisting:
                os.fsync(parent_fd)
        fcntl.flock(fd, fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        with os.fdopen(fd, "r+" if exclusive else "r", encoding="utf-8") as handle:
            fd = None
            yield handle
            revalidate_anchor(parent_fd, path.parent, identity)
            opened = os.fstat(handle.fileno())
            entry = anchored_lstat(parent_fd, path.parent, path.name)
            if (
                    not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                    or statmod.S_ISLNK(entry.st_mode)
                    or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
                raise RunEventError("run event stream changed during operation")
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent_fd)


@contextlib.contextmanager
def anchored_regular_file(path):
    parent_fd, identity = open_directory_anchor(path.parent)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path.name, flags, dir_fd=parent_fd)
    except OSError as exc:
        os.close(parent_fd)
        raise RunEventError("cannot open referenced file %s: %s" % (path, exc)) from exc
    try:
        opened = os.fstat(fd)
        entry = anchored_lstat(parent_fd, path.parent, path.name)
        if (
                not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or statmod.S_ISLNK(entry.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
            raise RunEventError("referenced file must be a stable single-link regular file: %s" % path)
        with os.fdopen(fd, "rb") as handle:
            fd = None
            yield handle
            revalidate_anchor(parent_fd, path.parent, identity)
            opened = os.fstat(handle.fileno())
            entry = anchored_lstat(parent_fd, path.parent, path.name)
            if (
                    opened.st_nlink != 1
                    or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
                raise RunEventError("referenced file changed during inspection: %s" % path)
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent_fd)


def read_anchored_json(path, label):
    with anchored_regular_file(path) as handle:
        raw = handle.read(MAX_DOCUMENT_BYTES + 1)
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise RunEventError("%s exceeds %d bytes" % (label, MAX_DOCUMENT_BYTES))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunEventError("%s must be UTF-8" % label) from exc
    return strict_json_loads(text, label)


def anchored_file_size(path):
    with anchored_regular_file(path) as handle:
        return os.fstat(handle.fileno()).st_size


def atomic_write_json(root, path, value):
    ensure_ignored(root, [path, path.parent / (".%s.run-tmp" % path.name)])
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    parent_fd, identity = open_directory_anchor(path.parent)
    temp_name = ".%s.run-tmp" % path.name
    try:
        existing = anchored_lstat(parent_fd, path.parent, path.name, missing_ok=True)
        if existing is not None and (
                statmod.S_ISLNK(existing.st_mode) or not statmod.S_ISREG(existing.st_mode)
                or existing.st_nlink != 1):
            raise RunEventError("runtime document must be a single-link regular file: %s" % path)
        leftover = anchored_lstat(parent_fd, path.parent, temp_name, missing_ok=True)
        if leftover is not None:
            if statmod.S_ISLNK(leftover.st_mode) or not statmod.S_ISREG(leftover.st_mode) or leftover.st_nlink != 1:
                raise RunEventError("runtime temporary is not a single-link regular file")
            os.unlink(temp_name, dir_fd=parent_fd)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temp_name, flags, 0o600, dir_fd=parent_fd)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle:
                fd = None
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            if fd is not None:
                os.close(fd)
        revalidate_anchor(parent_fd, path.parent, identity)
        os.rename(temp_name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        installed = anchored_lstat(parent_fd, path.parent, path.name)
        if not statmod.S_ISREG(installed.st_mode) or installed.st_nlink != 1:
            raise RunEventError("installed runtime document is unsafe")
        os.fsync(parent_fd)
    finally:
        try:
            if anchored_lstat(parent_fd, path.parent, temp_name, missing_ok=True) is not None:
                os.unlink(temp_name, dir_fd=parent_fd)
        finally:
            os.close(parent_fd)


def write_immutable_json(root, path, value):
    recover_immutable_install(path)
    status = _lstat(path, "runtime document", missing_ok=True)
    if status is not None:
        if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISREG(status.st_mode) or status.st_nlink != 1:
            raise RunEventError("immutable runtime document must be a single-link regular file")
        current = read_anchored_json(path, "existing runtime document")
        if canonical_json(current) != canonical_json(value):
            raise RunEventError("immutable runtime document already exists with different content: %s" % path)
    else:
        atomic_create_json(root, path, value)
    return sha256_file(path)


def recover_immutable_install(path):
    """Reclaim only provably safe residue from the temp-link install sequence."""
    if _lstat(path.parent, "immutable runtime parent", missing_ok=True) is None:
        return
    parent_fd, identity = open_directory_anchor(path.parent)
    temp_name = ".%s.run-create" % path.name
    try:
        temp = anchored_lstat(parent_fd, path.parent, temp_name, missing_ok=True)
        if temp is None:
            return
        target = anchored_lstat(parent_fd, path.parent, path.name, missing_ok=True)
        plain_temp = (
            statmod.S_ISREG(temp.st_mode) and not statmod.S_ISLNK(temp.st_mode)
            and temp.st_nlink == 1 and target is None
        )
        linked_install = (
            target is not None and statmod.S_ISREG(temp.st_mode)
            and statmod.S_ISREG(target.st_mode) and not statmod.S_ISLNK(temp.st_mode)
            and not statmod.S_ISLNK(target.st_mode) and temp.st_nlink == 2
            and target.st_nlink == 2
            and (temp.st_dev, temp.st_ino) == (target.st_dev, target.st_ino)
        )
        if not plain_temp and not linked_install:
            raise RunEventError("immutable runtime temporary residue is unsafe")
        revalidate_anchor(parent_fd, path.parent, identity)
        os.unlink(temp_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def atomic_create_json(root, path, value):
    if not _dir_fd_supported(os.link):
        raise RunEventError("immutable runtime install requires dirfd-anchored hard-link support")
    ensure_ignored(root, [path, path.parent / (".%s.run-create" % path.name)])
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    parent_fd, identity = open_directory_anchor(path.parent)
    temp_name = ".%s.run-create" % path.name
    try:
        leftover = anchored_lstat(parent_fd, path.parent, temp_name, missing_ok=True)
        if leftover is not None:
            raise RunEventError("immutable runtime temporary residue was not reclaimed")
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(temp_name, flags, 0o600, dir_fd=parent_fd)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle:
                fd = None
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
        finally:
            if fd is not None:
                os.close(fd)
        revalidate_anchor(parent_fd, path.parent, identity)
        try:
            os.link(
                temp_name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileExistsError:
            pass
        os.unlink(temp_name, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        try:
            if anchored_lstat(parent_fd, path.parent, temp_name, missing_ok=True) is not None:
                os.unlink(temp_name, dir_fd=parent_fd)
        finally:
            os.close(parent_fd)
    installed = read_anchored_json(path, "immutable runtime document")
    if canonical_json(installed) != canonical_json(value):
        raise RunEventError("immutable runtime document won a race with different content: %s" % path)


def hook_retry_equivalent(existing, normalized):
    prior = {key: existing[key] for key in REQUEST_FIELDS if key in existing}
    if not normalized["idempotency_key"].startswith("hook:"):
        return False
    for value in (prior, normalized):
        value.pop("occurred_at", None)
        value.pop("parent_event_id", None)
    return canonical_json(prior) == canonical_json(normalized)


def append_locked(root, run_id, handle, events, request, projection_path, allow_hook_retry=False):
    normalized = validate_event_request(request)
    if normalized["run_id"] != run_id:
        raise RunEventError("request run_id does not match command run_id")
    request_hash = sha256_json(normalized)
    existing = next((event for event in events if event["idempotency_key"] == normalized["idempotency_key"]), None)
    if existing:
        if existing["request_hash"] != request_hash:
            if not allow_hook_retry or not hook_retry_equivalent(existing, normalized):
                raise RunEventError("idempotency key was already used with different content")
        projected = project_events(run_id, events)
        atomic_write_json(normalized_root(root), projection_path, projected)
        return {"deduplicated": True, "event": existing, "projection": projected}
    if events and events[-1]["event_type"] in TERMINAL_TYPES:
        raise RunEventError("terminal run cannot accept another event")
    if len(events) >= MAX_EVENTS:
        raise RunEventError("event stream has reached the %d event limit" % MAX_EVENTS)
    if not events and normalized["event_type"] != "run_started":
        raise RunEventError("new run must start with run_started")
    if events and normalized["parent_event_id"] not in {event["event_id"] for event in events}:
        raise RunEventError("parent_event_id must reference an existing event")
    validate_event_transition(normalized, events)
    event = dict(normalized)
    event.update({
        "event_id": str(uuid.uuid5(NAMESPACE, run_id + ":" + normalized["idempotency_key"])),
        "offset": len(events) + 1,
        "recorded_at": now_iso(),
        "request_hash": request_hash,
        "previous_hash": events[-1]["event_hash"] if events else ZERO_HASH,
    })
    event["event_hash"] = event_hash(event)
    line = canonical_json(event) + "\n"
    if len(line.encode("utf-8")) > MAX_EVENT_BYTES:
        raise RunEventError("event exceeds size limit")
    projected = project_events(run_id, events + [event])
    handle.seek(0, os.SEEK_END)
    handle.write(line)
    handle.flush()
    os.fsync(handle.fileno())
    try:
        atomic_write_json(normalized_root(root), projection_path, projected)
    except Exception as exc:
        raise RunEventError(
            "event_committed=true offset=%s event_id=%s: projection install failed (%s); "
            "run `project %s` and do not retry with a new idempotency key"
            % (event["offset"], event["event_id"], exc, run_id)
        ) from exc
    return {"deduplicated": False, "event": event, "projection": projected}


def append_event(root, run_id, request, allow_hook_retry=False):
    normalized = validate_event_request(request)
    if normalized["event_type"] in INTERNAL_EVENT_TYPES:
        raise RunEventError("%s is reserved for its typed runtime command" % normalized["event_type"])
    reserved = next((prefix for prefix in RESERVED_IDEMPOTENCY_PREFIXES
                     if normalized["idempotency_key"].startswith(prefix)), None)
    if reserved and not (allow_hook_retry and reserved == "hook:"):
        raise RunEventError("idempotency key prefix is reserved for the runtime")
    stream, projection, _ = run_paths(root, run_id, create=True)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        return append_locked(root, run_id, handle, events, normalized, projection, allow_hook_retry)


def append_hook_event(root, run_id, request):
    """Append a hook event against the current head under one exclusive lock."""
    stream, projection, _ = run_paths(root, run_id, create=False)
    if _lstat(stream, "run event stream", missing_ok=True) is None:
        return None
    with locked_stream(stream, exclusive=True, create=False) as handle:
        events = read_stream(handle, run_id)
        if not events or events[-1]["event_type"] in TERMINAL_TYPES:
            return None
        current = dict(request)
        current["parent_event_id"] = events[-1]["event_id"]
        normalized = validate_event_request(current)
        return append_locked(
            root, run_id, handle, events, normalized, projection, allow_hook_retry=True
        )


def load_events(root, run_id):
    stream, _, _ = run_paths(root, run_id, create=False)
    if _lstat(stream, "run event stream", missing_ok=True) is None:
        raise RunEventError("run does not exist: %s" % run_id)
    with locked_stream(stream, exclusive=False) as handle:
        return read_stream(handle, run_id)


def rebuild_projection(root, run_id):
    stream, projection, _ = run_paths(root, run_id, create=True)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        if not events:
            raise RunEventError("cannot project an empty run")
        state = project_events(run_id, events)
        atomic_write_json(normalized_root(root), projection, state)
        return state


def validate_snapshot(value):
    required = {
        "schema_version", "snapshot_id", "run_id", "turn_id", "parent_turn_id", "created_at", "skill",
        "host", "system_prompt_sha256", "context_manifest", "tools", "toolset_sha256",
        "registry_offsets", "permission_profile",
    }
    exact_object(value, required, set(), "turn snapshot")
    if value["schema_version"] != SCHEMA_VERSION:
        raise RunEventError("turn snapshot schema_version must be 1.0")
    validate_uuid(value["snapshot_id"], "snapshot_id")
    validate_uuid(value["run_id"], "run_id")
    validate_safe_id(value["turn_id"], "turn_id")
    if value["parent_turn_id"] is not None:
        validate_safe_id(value["parent_turn_id"], "parent_turn_id")
    parse_datetime(value["created_at"], "created_at")
    skill = exact_object(value["skill"], {"name", "version", "contract_sha256"},
                         {"prompt_contract_ref", "prompt_contract_sha256"}, "skill")
    validate_safe_id(skill["name"], "skill.name")
    if not isinstance(skill["version"], str) or not SEMVER.fullmatch(skill["version"]):
        raise RunEventError("skill.version must be semver")
    validate_sha(skill["contract_sha256"], "skill.contract_sha256")
    if ("prompt_contract_ref" in skill) != ("prompt_contract_sha256" in skill):
        raise RunEventError("prompt contract ref and hash must appear together")
    if "prompt_contract_ref" in skill:
        validate_ref(skill["prompt_contract_ref"], "skill.prompt_contract_ref")
        validate_sha(skill["prompt_contract_sha256"], "skill.prompt_contract_sha256")
    host = exact_object(value["host"], {"adapter", "model_provider", "model_id"},
                        {"adapter_version"}, "host")
    for field in host:
        validate_safe_id(host[field], "host.%s" % field)
    validate_sha(value["system_prompt_sha256"], "system_prompt_sha256")
    manifest = exact_object(
        value["context_manifest"],
        {"ref", "sha256", "bytes", "token_estimate", "estimator", "context_signature"},
        set(), "context_manifest",
    )
    validate_ref(manifest["ref"], "context_manifest.ref")
    validate_sha(manifest["sha256"], "context_manifest.sha256")
    if not isinstance(manifest["bytes"], int) or isinstance(manifest["bytes"], bool) or manifest["bytes"] < 0:
        raise RunEventError("context_manifest.bytes must be non-negative")
    estimate = manifest["token_estimate"]
    estimator = manifest["estimator"]
    if estimate is None:
        if estimator is not None:
            raise RunEventError("context_manifest.estimator must be null when token_estimate is null")
    else:
        if not isinstance(estimate, int) or isinstance(estimate, bool) or estimate < 0:
            raise RunEventError("context_manifest.token_estimate must be null or non-negative")
        validate_safe_id(estimator, "context_manifest.estimator")
    validate_sha(manifest["context_signature"], "context_manifest.context_signature")
    if not isinstance(value["tools"], list) or len(value["tools"]) > 128:
        raise RunEventError("tools must be an array with at most 128 entries")
    for index, tool in enumerate(value["tools"]):
        exact_object(tool, {"name", "mode", "schema_sha256"}, set(), "tools[%d]" % index)
        validate_safe_id(tool["name"], "tools[%d].name" % index)
        if tool["mode"] not in {"read-only", "proposal-only", "mutating", "external"}:
            raise RunEventError("tools[%d].mode is unsupported" % index)
        validate_sha(tool["schema_sha256"], "tools[%d].schema_sha256" % index)
    validate_sha(value["toolset_sha256"], "toolset_sha256")
    if value["toolset_sha256"] != sha256_json(value["tools"]):
        raise RunEventError("toolset_sha256 does not match canonical tools")
    validate_offsets(value["registry_offsets"])
    profile = exact_object(value["permission_profile"], {"mode", "sandbox", "network", "external_mutations"}, set(), "permission_profile")
    if profile["mode"] not in {"disabled", "read-only", "proposal-only", "write-gated"}:
        raise RunEventError("permission_profile.mode is unsupported")
    validate_safe_id(profile["sandbox"], "permission_profile.sandbox")
    for field in ("network", "external_mutations"):
        if not isinstance(profile[field], bool):
            raise RunEventError("permission_profile.%s must be boolean" % field)
    return strict_json_loads(canonical_json(value), "normalized turn snapshot")


def validate_artifact_ref(value, label):
    exact_object(value, {"ref", "sha256"}, set(), label)
    validate_ref(value["ref"], label + ".ref")
    validate_sha(value["sha256"], label + ".sha256")
    return value


def validate_next_action(value, label="next_action"):
    if value is None:
        return value
    exact_object(value, {"code"}, {"not_before"}, label)
    validate_safe_id(value["code"], label + ".code")
    if "not_before" in value:
        parse_datetime(value["not_before"], label + ".not_before")
    return value


def validate_save_point(value):
    required = {
        "schema_version", "save_point_id", "run_id", "turn_id", "created_at",
        "last_event_id", "last_event_offset", "last_event_hash", "status",
        "turn_snapshot", "context_manifest", "artifacts", "registry_offsets",
        "visited_skills", "chain_depth", "pending_handoff", "next_action",
    }
    exact_object(value, required, set(), "save point")
    if value["schema_version"] != SCHEMA_VERSION:
        raise RunEventError("save point schema_version must be 1.0")
    validate_uuid(value["save_point_id"], "save_point_id")
    validate_uuid(value["run_id"], "run_id")
    validate_safe_id(value["turn_id"], "turn_id")
    parse_datetime(value["created_at"], "created_at")
    validate_uuid(value["last_event_id"], "last_event_id")
    if not isinstance(value["last_event_offset"], int) or isinstance(value["last_event_offset"], bool) or value["last_event_offset"] < 1:
        raise RunEventError("last_event_offset must be a positive integer")
    validate_sha(value["last_event_hash"], "last_event_hash")
    if value["status"] not in {"ready", "waiting", "needs-input", "blocked", "failed", "complete"}:
        raise RunEventError("save point status is unsupported")
    validate_artifact_ref(value["turn_snapshot"], "turn_snapshot")
    context_reference = exact_object(
        value["context_manifest"], {"ref", "sha256", "context_signature"}, set(),
        "context_manifest",
    )
    validate_ref(context_reference["ref"], "context_manifest.ref")
    validate_sha(context_reference["sha256"], "context_manifest.sha256")
    validate_sha(context_reference["context_signature"], "context_manifest.context_signature")
    if not isinstance(value["artifacts"], list) or len(value["artifacts"]) > 128:
        raise RunEventError("artifacts must be an array with at most 128 entries")
    for index, reference in enumerate(value["artifacts"]):
        label = "artifacts[%d]" % index
        exact_object(reference, {"ref", "sha256", "validator", "validation_status"}, set(), label)
        validate_ref(reference["ref"], label + ".ref")
        validate_sha(reference["sha256"], label + ".sha256")
        validate_safe_id(reference["validator"], label + ".validator")
        if reference["validation_status"] not in {"valid", "not-required"}:
            raise RunEventError("%s.validation_status is unsupported" % label)
    validate_offsets(value["registry_offsets"])
    visited = value["visited_skills"]
    if not isinstance(visited, list) or len(visited) > 4 or len(visited) != len(set(visited)):
        raise RunEventError("visited_skills must contain at most 4 unique skills")
    for index, skill in enumerate(visited):
        validate_safe_id(skill, "visited_skills[%d]" % index)
    if not isinstance(value["chain_depth"], int) or isinstance(value["chain_depth"], bool) or not 0 <= value["chain_depth"] <= 3:
        raise RunEventError("chain_depth must be an integer from 0 to 3")
    if visited and value["chain_depth"] != len(visited) - 1:
        raise RunEventError("chain_depth must equal visited_skills length minus one")
    handoff = value["pending_handoff"]
    if handoff is not None:
        exact_object(handoff, {"status", "objective_code", "recommended_skill"}, set(), "pending_handoff")
        if handoff["status"] not in {"proposed", "needs-input", "blocked"}:
            raise RunEventError("pending_handoff.status is unsupported")
        validate_safe_id(handoff["objective_code"], "pending_handoff.objective_code")
        validate_safe_id(handoff["recommended_skill"], "pending_handoff.recommended_skill")
    validate_next_action(value["next_action"])
    return strict_json_loads(canonical_json(value), "normalized save point")


def validate_envelope(value):
    required = {
        "schema_version", "run_id", "parent_run_id", "started_at", "ended_at", "status",
        "evidence_mode", "route", "context_manifests", "last_event_id",
        "last_event_offset", "last_event_hash", "save_point", "registry_offsets",
        "artifacts", "metrics", "failure_class", "next_action",
    }
    exact_object(value, required, set(), "run envelope")
    if value["schema_version"] != SCHEMA_VERSION:
        raise RunEventError("run envelope schema_version must be 1.0")
    validate_uuid(value["run_id"], "run_id")
    if value["parent_run_id"] is not None:
        validate_uuid(value["parent_run_id"], "parent_run_id")
    started = parse_datetime(value["started_at"], "started_at")
    if value["ended_at"] is not None:
        ended = parse_datetime(value["ended_at"], "ended_at")
        if ended < started:
            raise RunEventError("ended_at cannot precede started_at")
    if value["status"] not in {"waiting", "needs-input", "blocked", "succeeded", "failed", "aborted"}:
        raise RunEventError("run envelope status is unsupported")
    if value["status"] in {"succeeded", "failed", "aborted"} and value["ended_at"] is None:
        raise RunEventError("terminal run envelope requires ended_at")
    if value["evidence_mode"] not in {"none", "simulated", "real", "mixed"}:
        raise RunEventError("evidence_mode is unsupported")
    route = exact_object(value["route"], {"skill", "version", "reason_code"}, set(), "route")
    validate_safe_id(route["skill"], "route.skill")
    if not isinstance(route["version"], str) or not SEMVER.fullmatch(route["version"]):
        raise RunEventError("route.version must be semver")
    validate_safe_id(route["reason_code"], "route.reason_code")
    manifests = value["context_manifests"]
    if not isinstance(manifests, list) or not 1 <= len(manifests) <= 256:
        raise RunEventError("context_manifests must contain 1 to 256 entries")
    for index, reference in enumerate(manifests):
        label = "context_manifests[%d]" % index
        exact_object(reference, {"ref", "sha256", "context_signature"}, set(), label)
        validate_ref(reference["ref"], label + ".ref")
        validate_sha(reference["sha256"], label + ".sha256")
        validate_sha(reference["context_signature"], label + ".context_signature")
    validate_uuid(value["last_event_id"], "last_event_id")
    if not isinstance(value["last_event_offset"], int) or isinstance(value["last_event_offset"], bool) or value["last_event_offset"] < 1:
        raise RunEventError("last_event_offset must be a positive integer")
    validate_sha(value["last_event_hash"], "last_event_hash")
    if value["save_point"] is not None:
        validate_artifact_ref(value["save_point"], "save_point")
    validate_offsets(value["registry_offsets"])
    if not isinstance(value["artifacts"], list) or len(value["artifacts"]) > 128:
        raise RunEventError("artifacts must be an array with at most 128 entries")
    for index, reference in enumerate(value["artifacts"]):
        validate_artifact_ref(reference, "artifacts[%d]" % index)
    if not isinstance(value["metrics"], dict) or len(value["metrics"]) > 64:
        raise RunEventError("metrics must be an object with at most 64 entries")
    for key, metric in value["metrics"].items():
        if not SAFE_FIELD.fullmatch(key) or not isinstance(metric, (int, float)) or isinstance(metric, bool) or not math.isfinite(metric):
            raise RunEventError("run envelope metrics must be finite numeric metadata")
    failure_class = value["failure_class"]
    if failure_class not in {None, "prompt", "routing", "context", "tool", "permission", "artifact", "loop", "unknown"}:
        raise RunEventError("failure_class is unsupported")
    if value["status"] in {"failed", "blocked", "aborted"} and failure_class is None:
        raise RunEventError("failed, blocked, or aborted run envelope requires failure_class")
    validate_next_action(value["next_action"])
    return strict_json_loads(canonical_json(value), "normalized run envelope")


VALIDATORS = {"turn-snapshot": validate_snapshot, "save-point": validate_save_point, "run-envelope": validate_envelope}


def ensure_child_directories(root, run_dir, parts):
    if not safe_mutation_available():
        raise RunEventError("run mutation requires POSIX dirfd operations and advisory locking")
    run_fd, _ = open_directory_anchor(run_dir)
    descriptors = [run_fd]
    parent_fd = run_fd
    parent_path = run_dir
    try:
        for name in parts:
            validate_safe_id(name, "runtime path component")
            child_fd = open_or_create_directory(parent_fd, parent_path, name)
            descriptors.append(child_fd)
            parent_fd = child_fd
            parent_path = parent_path / name
        return parent_path
    finally:
        for descriptor in reversed(descriptors):
            os.close(descriptor)


def resolve_project_reference(root, reference, expected_sha):
    validate_ref(reference, "artifact ref")
    path = root.joinpath(*reference.split("/"))
    if sha256_file(path) != expected_sha:
        raise RunEventError("referenced artifact hash mismatch: %s" % reference)
    return path


def verified_json_reference(root, reference, expected_sha, label):
    path = resolve_project_reference(root, reference, expected_sha)
    return path, read_anchored_json(path, label)


def validate_context_document(root, reference, expected_sha, expected_signature,
                              run_id, turn_id=None):
    path, document = verified_json_reference(
        root, reference, expected_sha, "context manifest",
    )
    if not isinstance(document, dict):
        raise RunEventError("context manifest must be an object")
    required = {"schema_version", "run_id", "turn_id", "context_signature"}
    if not required.issubset(document):
        raise RunEventError("context manifest is missing runtime identity fields")
    if document["schema_version"] != SCHEMA_VERSION or document["run_id"] != run_id:
        raise RunEventError("context manifest does not belong to this run")
    if turn_id is not None and document["turn_id"] != turn_id:
        raise RunEventError("context manifest does not belong to this turn")
    if document["context_signature"] != expected_signature:
        raise RunEventError("context manifest signature does not match its reference")
    validate_sha(document["context_signature"], "context manifest context_signature")
    return path, document


def validate_snapshot_document(root, reference, expected_sha, run_id, turn_id):
    _, document = verified_json_reference(root, reference, expected_sha, "turn snapshot")
    normalized = validate_snapshot(document)
    if normalized["run_id"] != run_id or normalized["turn_id"] != turn_id:
        raise RunEventError("turn snapshot does not belong to the save-point run/turn")
    return normalized


def validate_save_point_document(root, reference, expected_sha, run_id):
    _, document = verified_json_reference(root, reference, expected_sha, "save point")
    normalized = validate_save_point(document)
    if normalized["run_id"] != run_id:
        raise RunEventError("save point does not belong to the envelope run")
    return normalized


def validate_audit_reference(root, reference):
    if (
            reference["validation_status"] != "valid"
            or reference["validator"] != "validate-audit-artifact"):
        raise RunEventError(
            "memory/audits artifacts require validation_status=valid and validator=validate-audit-artifact"
        )
    validator = Path(__file__).with_name("validate-audit-artifact.py")
    if not validator.is_file():
        raise RunEventError("audit artifact validator is unavailable")
    try:
        result = subprocess.run(
            [sys.executable, str(validator), str(root / reference["ref"]),
             "--relative-path", reference["ref"]],
            cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunEventError("audit artifact validation could not run: %s" % exc) from exc
    if result.returncode:
        detail = " ".join(result.stdout.splitlines()[-3:])[:500]
        raise RunEventError("audit artifact validation failed: %s" % (detail or "invalid artifact"))


def existing_artifact_result(root, existing, proposed, projection, expected_kind):
    references = existing.get("references")
    if (
            not isinstance(references, list) or len(references) != 1
            or references[0].get("kind") != expected_kind
            or not isinstance(references[0].get("sha256"), str)):
        raise RunEventError("reserved idempotency key is occupied by an incompatible event")
    reference = references[0]
    path, stored = verified_json_reference(
        root, reference["ref"], reference["sha256"], "existing typed runtime artifact",
    )
    if canonical_json(stored) != canonical_json(proposed):
        raise RunEventError("idempotency key was already used with different artifact content")
    return {
        "deduplicated": True,
        "event": existing,
        "projection": projection,
        "artifact": {"ref": str(path.relative_to(root)), "sha256": reference["sha256"]},
    }


def write_snapshot(root, run_id, value):
    normalized = validate_snapshot(value)
    if normalized["run_id"] != run_id:
        raise RunEventError("snapshot run_id does not match command run_id")
    stream, projection, run_dir = run_paths(root, run_id, create=True)
    root_path = normalized_root(root)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        state = project_events(run_id, events)
        event_key = "snapshot:%s" % normalized["snapshot_id"]
        existing = next((event for event in events if event["idempotency_key"] == event_key), None)
        if existing:
            return existing_artifact_result(
                root_path, existing, normalized, state, "turn-snapshot",
            )
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("snapshot requires an active run")
        context_path, _ = validate_context_document(
            root_path, normalized["context_manifest"]["ref"],
            normalized["context_manifest"]["sha256"],
            normalized["context_manifest"]["context_signature"],
            run_id, normalized["turn_id"],
        )
        if anchored_file_size(context_path) != normalized["context_manifest"]["bytes"]:
            raise RunEventError("context_manifest.bytes does not match the referenced file")
        target_dir = ensure_child_directories(root_path, run_dir, ["turns", normalized["turn_id"]])
        target = target_dir / "snapshot.json"
        digest = write_immutable_json(root_path, target, normalized)
        reference = str(target.relative_to(root_path))
        request = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "idempotency_key": event_key,
            "event_type": "turn_snapshot_created",
            "occurred_at": normalized["created_at"],
            "actor": {"type": "system", "id": "run-events"},
            "parent_event_id": events[-1]["event_id"],
            "turn_id": normalized["turn_id"],
            "status": "succeeded",
            "subject": {"kind": "turn", "ref": normalized["turn_id"]},
            "references": [{"kind": "turn-snapshot", "ref": reference, "sha256": digest}],
            "metrics": {},
            "dimensions": {},
        }
        result = append_locked(root, run_id, handle, events, request, projection)
        result["artifact"] = {"ref": reference, "sha256": digest}
        return result


def write_save_point(root, run_id, value):
    normalized = validate_save_point(value)
    if normalized["run_id"] != run_id:
        raise RunEventError("save point run_id does not match command run_id")
    stream, projection, run_dir = run_paths(root, run_id, create=True)
    root_path = normalized_root(root)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        state = project_events(run_id, events)
        event_key = "save:%s" % normalized["save_point_id"]
        existing = next((event for event in events if event["idempotency_key"] == event_key), None)
        if existing:
            return existing_artifact_result(
                root_path, existing, normalized, state, "save-point",
            )
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("save point requires an active run")
        if normalized["last_event_id"] != state["head_event_id"]:
            raise RunEventError("save point last_event_id must equal the verified stream head")
        if normalized["last_event_offset"] != state["last_offset"] or normalized["last_event_hash"] != state["last_event_hash"]:
            raise RunEventError("save point offset/hash must equal the verified stream head")
        if state["open_tool_refs"]:
            raise RunEventError("save point cannot be created with unfinished tool calls")
        if (
                normalized["turn_snapshot"]["ref"] != state["last_turn_snapshot_ref"]
                or normalized["turn_snapshot"]["sha256"] != state["last_turn_snapshot_sha256"]):
            raise RunEventError("save point must reference the latest turn snapshot on the selected branch")
        snapshot_document = validate_snapshot_document(
            root_path, normalized["turn_snapshot"]["ref"],
            normalized["turn_snapshot"]["sha256"], run_id, normalized["turn_id"],
        )
        validate_context_document(
            root_path, normalized["context_manifest"]["ref"],
            normalized["context_manifest"]["sha256"],
            normalized["context_manifest"]["context_signature"],
            run_id, normalized["turn_id"],
        )
        if (
                snapshot_document["context_manifest"]["sha256"] != normalized["context_manifest"]["sha256"]
                or snapshot_document["context_manifest"]["context_signature"]
                != normalized["context_manifest"]["context_signature"]):
            raise RunEventError("save point context does not match its turn snapshot")
        for reference in normalized["artifacts"]:
            resolve_project_reference(root_path, reference["ref"], reference["sha256"])
            if reference["ref"].endswith(("/events.ndjson", "/session.json")):
                raise RunEventError("save point artifacts cannot reference mutable runtime files")
            if reference["ref"].startswith("memory/audits/"):
                validate_audit_reference(root_path, reference)
            elif reference["validation_status"] == "valid":
                matches = [entry for entry in state["validated_artifacts"] if (
                    entry["ref"] == reference["ref"]
                    and entry["sha256"] == reference["sha256"]
                    and entry["validator"] == reference["validator"]
                )]
                if not matches:
                    raise RunEventError("validated artifact lacks a matching ancestor artifact_validated event")
        target_dir = ensure_child_directories(root_path, run_dir, ["save-points"])
        target = target_dir / (normalized["save_point_id"] + ".json")
        digest = write_immutable_json(root_path, target, normalized)
        reference = str(target.relative_to(root_path))
        request = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "idempotency_key": event_key,
            "event_type": "save_point_created",
            "occurred_at": normalized["created_at"],
            "actor": {"type": "system", "id": "run-events"},
            "parent_event_id": events[-1]["event_id"],
            "turn_id": normalized["turn_id"],
            "status": "succeeded",
            "subject": {"kind": "save-point", "ref": normalized["save_point_id"]},
            "references": [{"kind": "save-point", "ref": reference, "sha256": digest}],
            "metrics": {},
            "dimensions": {},
        }
        result = append_locked(root, run_id, handle, events, request, projection)
        result["artifact"] = {"ref": reference, "sha256": digest}
        return result


def finish_run(root, run_id, value):
    normalized = validate_envelope(value)
    if normalized["run_id"] != run_id:
        raise RunEventError("run envelope run_id does not match command run_id")
    stream, projection, run_dir = run_paths(root, run_id, create=True)
    root_path = normalized_root(root)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        state = project_events(run_id, events)
        event_key = "envelope:%s:%s" % (normalized["status"], normalized["last_event_id"])
        existing = next((event for event in events if event["idempotency_key"] == event_key), None)
        if existing:
            return existing_artifact_result(
                root_path, existing, normalized, state, "run-envelope",
            )
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("finish requires an active run")
        if normalized["last_event_id"] != state["head_event_id"]:
            raise RunEventError("run envelope last_event_id must equal the verified stream head")
        if normalized["last_event_offset"] != state["last_offset"] or normalized["last_event_hash"] != state["last_event_hash"]:
            raise RunEventError("run envelope offset/hash must equal the verified stream head")
        if normalized["started_at"] != state["started_at"]:
            raise RunEventError("run envelope started_at must match run_started")
        if normalized["status"] == "succeeded" and state["open_tool_refs"]:
            raise RunEventError("successful run cannot finish with unfinished tool calls")
        for context_reference in normalized["context_manifests"]:
            validate_context_document(
                root_path, context_reference["ref"], context_reference["sha256"],
                context_reference["context_signature"], run_id,
            )
        references_to_verify = [*normalized["artifacts"]]
        if normalized["save_point"] is not None:
            save_document = validate_save_point_document(
                root_path, normalized["save_point"]["ref"],
                normalized["save_point"]["sha256"], run_id,
            )
            if save_document["last_event_offset"] > normalized["last_event_offset"]:
                raise RunEventError("run envelope save point is ahead of its summarized head")
            if (
                    normalized["save_point"]["ref"] != state["last_save_point_ref"]
                    or normalized["save_point"]["sha256"] != state["last_save_point_sha256"]):
                raise RunEventError("run envelope must reference the latest save point on the selected branch")
            if not any(
                    reference["sha256"] == save_document["context_manifest"]["sha256"]
                    and reference["context_signature"] == save_document["context_manifest"]["context_signature"]
                    for reference in normalized["context_manifests"]):
                raise RunEventError("run envelope omits the save point context manifest")
        for reference in references_to_verify:
            resolve_project_reference(root_path, reference["ref"], reference["sha256"])
            if reference["ref"].endswith(("/events.ndjson", "/session.json")):
                raise RunEventError("run envelope artifacts cannot reference mutable runtime files")
        target_dir = ensure_child_directories(root_path, run_dir, ["envelopes"])
        target = target_dir / (normalized["last_event_id"] + ".json")
        digest = write_immutable_json(root_path, target, normalized)
        reference = str(target.relative_to(root_path))
        event_type = {
            "succeeded": "run_finished", "failed": "run_failed", "aborted": "run_aborted",
        }.get(normalized["status"], "run_waiting")
        status = {
            "run_finished": "succeeded", "run_failed": "failed", "run_aborted": "cancelled",
            "run_waiting": "waiting",
        }[event_type]
        request = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "idempotency_key": event_key,
            "event_type": event_type,
            "occurred_at": normalized["ended_at"] or now_iso(),
            "actor": {"type": "system", "id": "run-events"},
            "parent_event_id": events[-1]["event_id"],
            "turn_id": None,
            "status": status,
            "subject": {"kind": "run", "ref": run_id},
            "references": [{"kind": "run-envelope", "ref": reference, "sha256": digest}],
            "metrics": normalized["metrics"],
            "dimensions": {"evidence_mode": normalized["evidence_mode"]},
        }
        result = append_locked(root, run_id, handle, events, request, projection)
        result["artifact"] = {"ref": reference, "sha256": digest}
        return result


def hashed_identifier(value, run_id):
    if not isinstance(value, str) or not value:
        return None
    material = (run_id + "\0" + value).encode("utf-8")
    return "sha256:" + hashlib.sha256(material).hexdigest()[:24]


def safe_tool_name(value, run_id):
    if isinstance(value, str) and SAFE_ID.fullmatch(value) and "@" not in value:
        return value[:128]
    return hashed_identifier(value, run_id) if isinstance(value, str) and value else "unknown"


def record_hook(root, mode, payload):
    run_id = os.environ.get("AARON_ACTIVE_RUN_ID", "")
    if not run_id:
        return {"recorded": False, "reason": "inactive"}
    validate_uuid(run_id, "AARON_ACTIVE_RUN_ID")
    if not isinstance(payload, dict):
        raise RunEventError("hook input must be a JSON object")
    raw_turn_id = os.environ.get("AARON_ACTIVE_TURN_ID") or None
    turn_id = hashed_identifier(raw_turn_id, run_id)
    session_ref = hashed_identifier(payload.get("session_id"), run_id)
    tool_ref = hashed_identifier(payload.get("tool_use_id"), run_id)
    identity = None
    event_type = "hook_observed"
    status = "succeeded"
    subject = {"kind": "hook", "ref": mode}
    reason_code = None
    dimensions = {"hook_name": mode}
    if mode == "session-start":
        identity = session_ref
    elif mode == "user-prompt-submit":
        identity = turn_id
        event_type = "turn_started"
        subject = {"kind": "turn", "ref": turn_id or "unknown"}
    elif mode == "pre-tool-use":
        identity = tool_ref
        event_type = "tool_requested"
        subject = {"kind": "tool", "ref": tool_ref or "unknown"}
        dimensions["tool_name"] = safe_tool_name(payload.get("tool_name"), run_id)
        status = "started"
    elif mode in {"post-tool-use", "post-tool-failure"}:
        identity = tool_ref
        event_type = "tool_finished"
        subject = {"kind": "tool", "ref": tool_ref or "unknown"}
        dimensions["tool_name"] = safe_tool_name(payload.get("tool_name"), run_id)
        status = "failed" if mode == "post-tool-failure" else "succeeded"
        reason_code = "tool-failure" if mode == "post-tool-failure" else None
    elif mode == "stop":
        identity = turn_id
        event_type = "turn_finished"
        subject = {"kind": "turn", "ref": turn_id or "unknown"}
    elif mode == "post-tool-batch":
        identity = hashed_identifier(os.environ.get("AARON_ACTIVE_HOOK_ID"), run_id)
    else:
        raise RunEventError("unsupported hook mode")
    if not identity:
        return {"recorded": False, "reason": "stable-identity-unavailable"}
    key_material = "%s:%s:%s" % (run_id, mode, identity)
    request = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "idempotency_key": "hook:" + hashlib.sha256(key_material.encode("utf-8")).hexdigest()[:48],
        "event_type": event_type,
        "occurred_at": now_iso(),
        "actor": {"type": "host", "id": "claude-code"},
        "parent_event_id": None,
        "turn_id": turn_id,
        "status": status,
        "subject": subject,
        "references": [],
        "metrics": {},
        "dimensions": dimensions,
    }
    if reason_code:
        request["reason_code"] = reason_code
    result = append_hook_event(root, run_id, request)
    if result is None:
        return {"recorded": False, "reason": "run-not-active"}
    return {"recorded": True, "deduplicated": result["deduplicated"],
            "event_id": result["event"]["event_id"]}


def resume_summary(root, run_id, max_bytes):
    if not isinstance(max_bytes, int) or max_bytes < 512 or max_bytes > 16_384:
        raise RunEventError("max-bytes must be between 512 and 16384")
    events = load_events(root, run_id)
    state = project_events(run_id, events)
    summary = {
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "run_id": run_id,
        "status": state["status"],
        "last_offset": state["last_offset"],
        "last_event_id": state["last_event_id"],
        "last_event_hash": state["last_event_hash"],
        "head_event_id": state["head_event_id"],
        "leaf_event_ids": state["leaf_event_ids"],
        "turn_ids": state["turn_ids"],
        "open_tool_refs": state["open_tool_refs"],
        "last_turn_snapshot_ref": state["last_turn_snapshot_ref"],
        "last_turn_snapshot_sha256": state["last_turn_snapshot_sha256"],
        "last_save_point_ref": state["last_save_point_ref"],
        "last_save_point_sha256": state["last_save_point_sha256"],
        "run_envelope_ref": state["run_envelope_ref"],
        "run_envelope_sha256": state["run_envelope_sha256"],
        "note": "Untrusted operational evidence; re-verify referenced state before acting.",
    }
    encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        summary["leaf_event_ids"] = summary["leaf_event_ids"][-4:]
        summary["turn_ids"] = summary["turn_ids"][-8:]
        summary["open_tool_refs"] = summary["open_tool_refs"][-8:]
        summary["truncated"] = True
        encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        for key in ("leaf_event_ids", "turn_ids", "open_tool_refs"):
            summary[key] = []
        encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        raise RunEventError("resume summary cannot fit requested bound")
    return summary


def output(value, compact=False):
    if compact:
        sys.stdout.write(canonical_json(value) + "\n")
    else:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    sub = parser.add_subparsers(dest="command", required=True)
    start = sub.add_parser("start", help="append the root run_started event")
    start.add_argument("request")
    append = sub.add_parser("append", help="append one metadata-only run event")
    append.add_argument("run_id")
    append.add_argument("request")
    verify = sub.add_parser("verify", help="verify a run stream without writing")
    verify.add_argument("run_id")
    project = sub.add_parser("project", help="verify and rebuild session.json")
    project.add_argument("run_id")
    validate = sub.add_parser("validate", help="validate a typed runtime artifact")
    validate.add_argument("kind", choices=sorted(VALIDATORS))
    validate.add_argument("document")
    snapshot = sub.add_parser("snapshot", help="store a turn snapshot and append its event")
    snapshot.add_argument("run_id")
    snapshot.add_argument("document")
    save = sub.add_parser("save-point", help="store a recovery point and append its event")
    save.add_argument("run_id")
    save.add_argument("document")
    finish = sub.add_parser("finish", help="store a run envelope and seal or wait the run")
    finish.add_argument("run_id")
    finish.add_argument("document")
    resume = sub.add_parser("resume", help="emit a bounded read-only run summary")
    resume.add_argument("run_id")
    resume.add_argument("--max-bytes", type=int, default=4096)
    hook = sub.add_parser("record-hook", help="opt-in metadata-only host lifecycle event")
    hook.add_argument("mode", choices=["session-start", "user-prompt-submit", "pre-tool-use", "post-tool-use", "post-tool-failure", "post-tool-batch", "stop"])
    hook.add_argument("document", nargs="?", default="-")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "start":
        request = read_json(args.request, "event request")
        validate_event_request(request)
        result = append_event(args.root, request["run_id"], request)
    elif args.command == "append":
        result = append_event(args.root, args.run_id, read_json(args.request, "event request"))
    elif args.command == "verify":
        events = load_events(args.root, args.run_id)
        result = {"valid": True, "events": len(events), "projection": project_events(args.run_id, events)}
    elif args.command == "project":
        result = rebuild_projection(args.root, args.run_id)
    elif args.command == "validate":
        result = VALIDATORS[args.kind](read_json(args.document, args.kind))
    elif args.command == "snapshot":
        result = write_snapshot(args.root, args.run_id, read_json(args.document, "turn snapshot"))
    elif args.command == "save-point":
        result = write_save_point(args.root, args.run_id, read_json(args.document, "save point"))
    elif args.command == "finish":
        result = finish_run(args.root, args.run_id, read_json(args.document, "run envelope"))
    elif args.command == "resume":
        result = resume_summary(args.root, args.run_id, args.max_bytes)
    elif args.command == "record-hook":
        result = record_hook(args.root, args.mode, read_json(args.document, "hook input"))
    else:  # pragma: no cover
        raise AssertionError(args.command)
    output(result, compact=args.command == "resume")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RunEventError as exc:
        print("run-events: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
