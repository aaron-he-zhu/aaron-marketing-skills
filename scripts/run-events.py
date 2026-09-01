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
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat as statmod
import subprocess
import sys
import time
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - writes fail closed without POSIX locking
    fcntl = None


SCHEMA_VERSION = "1.0"
AUDIT_LOOP_SCHEMA_VERSION = "2.0"
NAMESPACE = uuid.UUID("5a325540-897b-44fe-8022-a5c59dc12bcc")
ZERO_HASH = "0" * 64
MAX_EVENT_BYTES = 64_000
MAX_DOCUMENT_BYTES = 1_000_000
MAX_CONTEXT_MANIFEST_BYTES = 2_000_000
MAX_REFERENCE_BYTES = 10_000_000
MAX_REFERENCE_INSPECTION_BYTES = 64_000_000
MAX_CONTEXT_MANIFESTS = 256
MAX_EVENTS = 10_000
MAX_AUDIT_LOOPS = 256
MAX_LOOP_VALIDATION_SECONDS = 30
MAX_CONTROL_ARTIFACT_VALIDATION_SECONDS = 30
MAX_VALIDATED_ARTIFACTS_PER_BOUNDARY = 128
MAX_LOOP_CLOSURE_STEPS = 1_024
MAX_LOOP_CLOSURE_BYTES = 16_000_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,511}$")
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,63}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
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
    "model_id", "route_reason", "route_transition", "route_command",
    "failure_class", "loop_state", "branch_reason",
}
ROUTE_TRANSITIONS = {"initial", "automatic-handoff", "user-reroute"}
MAX_ROUTE_CHAIN_SKILLS = 4
LOOP_STATES = {
    "awaiting-proposal", "awaiting-owner", "awaiting-intervention",
    "awaiting-reaudit", "next", "converged", "exhausted",
    "gate-blocked", "needs-input",
}
LOOP_TERMINAL_STATES = {"converged", "exhausted", "gate-blocked", "needs-input"}
LOOP_STEP_FIELDS = {
    "schema_version", "run_id", "loop_id", "transition_id", "sequence",
    "transition", "from_state", "state", "cycle", "max_cycles", "total_retries",
    "state_retries", "max_retries", "backoff_seconds", "retry_not_before",
    "deadline", "occurred_at", "recorded_at", "idempotency_key", "request_hash",
    "run_parent_event_id", "run_parent_event_sha256",
    "previous_step_ref", "previous_step_sha256", "expected_previous_sha256",
    "proposal_only", "external_mutation_authorized", "baseline_audit", "latest_audit",
    "proposal", "owner", "intervention", "reason_code", "lease",
}
LOOP_CLOSURE_FAILURE_CODES = {
    "nonterminal", "missing-step", "hash-mismatch", "invalid-chain",
    "event-mismatch", "validation-timeout", "budget-exhausted", "validator-error",
}
INTERNAL_EVENT_TYPES = {
    "turn_snapshot_created", "save_point_created", "loop_state_changed", "run_waiting",
    "run_finished", "run_failed", "run_aborted",
}
RESERVED_IDEMPOTENCY_PREFIXES = ("snapshot:", "save:", "loop:", "envelope:", "hook:")
CONTROL_ARTIFACT_VALIDATOR = "validate-control-artifact"
CONTROL_ARTIFACT_SCHEMA_REF = "references/control-artifact.schema.json"


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
            with anchored_regular_file(Path(path)) as handle:
                raw = handle.read(MAX_DOCUMENT_BYTES + 1)
        except (OSError, RunEventError) as exc:
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


def sha256_file(path, max_bytes=MAX_REFERENCE_BYTES):
    digest = hashlib.sha256()
    try:
        with anchored_regular_file(path) as handle:
            size = os.fstat(handle.fileno()).st_size
            if size > max_bytes:
                raise RunEventError(
                    "referenced file exceeds %d bytes: %s" % (max_bytes, path)
                )
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                digest.update(chunk)
    except OSError as exc:
        raise RunEventError("cannot hash %s: %s" % (path, exc)) from exc
    return digest.hexdigest()


def validate_finite_metric(value, label):
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise RunEventError("%s must be finite numeric metadata" % label)
    try:
        finite = math.isfinite(value)
    except (OverflowError, TypeError, ValueError):
        finite = False
    if not finite:
        raise RunEventError("%s must be finite numeric metadata" % label)
    return value


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(value, label):
    if not isinstance(value, str) or not RFC3339.fullmatch(value):
        raise RunEventError("%s must be an RFC 3339 date-time" % label)
    try:
        normalized = value.replace("t", "T").replace("z", "+00:00").replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise RunEventError("%s must be an RFC 3339 date-time" % label) from exc
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
    if parsed.variant != uuid.RFC_4122 or parsed.version not in set(range(1, 9)):
        raise RunEventError("%s must be a canonical RFC UUID version 1 through 8" % label)
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


def validate_enum(value, allowed, label):
    if not isinstance(value, str) or value not in allowed:
        raise RunEventError("%s is unsupported" % label)
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
    validate_enum(value["kind"], REFERENCE_KINDS, label + ".kind")
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
    validate_enum(request["event_type"], EVENT_TYPES, "event_type")
    parse_datetime(request["occurred_at"], "occurred_at")
    exact_object(request["actor"], {"type", "id"}, set(), "actor")
    validate_enum(request["actor"]["type"], ACTOR_TYPES, "actor.type")
    validate_safe_id(request["actor"]["id"], "actor.id")
    parent = request["parent_event_id"]
    if parent is not None:
        validate_uuid(parent, "parent_event_id")
    turn_id = request["turn_id"]
    if turn_id is not None:
        validate_safe_id(turn_id, "turn_id")
    validate_enum(request["status"], STATUSES, "status")
    exact_object(request["subject"], {"kind", "ref"}, set(), "subject")
    validate_enum(request["subject"]["kind"], SUBJECT_KINDS, "subject.kind")
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
        validate_finite_metric(value, "metrics.%s" % key)
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
        "route_selected": ("succeeded", "route"),
        "turn_started": ("started", "turn"),
        "turn_snapshot_created": ("succeeded", "turn"),
        "tool_requested": ("started", "tool"),
        "tool_allowed": ("started", "tool"),
        "tool_blocked": ("blocked", "tool"),
        "save_point_created": ("succeeded", "save-point"),
        "loop_state_changed": ("succeeded", "loop"),
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
    if event_type == "route_selected":
        if "reason_code" not in request:
            raise RunEventError("route_selected requires reason_code")
        if set(request["dimensions"]) != {"route_transition", "route_command"}:
            raise RunEventError(
                "route_selected dimensions must contain exactly route_transition and route_command"
            )
        validate_enum(
            request["dimensions"]["route_transition"],
            ROUTE_TRANSITIONS,
            "dimensions.route_transition",
        )
    if event_type == "loop_state_changed":
        if turn_id is not None or "reason_code" not in request:
            raise RunEventError("loop_state_changed requires reason_code and no turn_id")
        validate_uuid(subject["ref"], "loop_state_changed subject.ref")
        if set(request["dimensions"]) != {"loop_state"}:
            raise RunEventError("loop_state_changed requires exactly the loop_state dimension")
        validate_enum(request["dimensions"]["loop_state"], LOOP_STATES, "dimensions.loop_state")
        if set(request["metrics"]) != {"sequence", "cycle", "total_retries"}:
            raise RunEventError(
                "loop_state_changed requires sequence, cycle, and total_retries metrics"
            )
        for name in ("sequence", "cycle", "total_retries"):
            value = request["metrics"][name]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise RunEventError("loop_state_changed metrics.%s must be a non-negative integer" % name)
        if not 1 <= request["metrics"]["sequence"] <= 128:
            raise RunEventError("loop_state_changed sequence must be 1..128")
        if not 1 <= request["metrics"]["cycle"] <= 3:
            raise RunEventError("loop_state_changed cycle must be 1..3")
        if request["metrics"]["total_retries"] > 128:
            raise RunEventError("loop_state_changed total_retries must be at most 128")
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
        "loop_state_changed": "loop",
    }.get(event_type)
    if typed_reference and (
            len(references) != 1 or references[0]["kind"] != typed_reference
            or "sha256" not in references[0]):
        raise RunEventError("%s requires one hashed %s reference" % (event_type, typed_reference))
    if event_type == "turn_snapshot_created":
        expected = "memory/runs/%s/turns/%s/snapshot.json" % (
            request["run_id"], turn_id,
        )
        if references[0]["ref"] != expected:
            raise RunEventError("turn_snapshot_created requires its canonical runtime reference")
    if event_type == "save_point_created":
        expected = "memory/runs/%s/save-points/%s.json" % (
            request["run_id"], subject["ref"],
        )
        if references[0]["ref"] != expected:
            raise RunEventError("save_point_created requires its canonical runtime reference")
    if event_type == "loop_state_changed":
        prefix = "memory/runs/%s/loops/%s/" % (request["run_id"], subject["ref"])
        reference = references[0]["ref"]
        if not reference.startswith(prefix) or not re.fullmatch(
                r"[0-9]{3}-[a-z][a-z-]*\.json", reference[len(prefix):]):
            raise RunEventError("loop_state_changed requires its canonical immutable step reference")
    if event_type in {"run_waiting", *TERMINAL_TYPES} and (
            len(references) != 1 or references[0]["kind"] != "run-envelope"
            or "sha256" not in references[0]
            or "/envelopes/" not in references[0]["ref"]):
        raise RunEventError("run envelope events require one hashed envelope artifact reference")
    if event_type in {"run_waiting", *TERMINAL_TYPES}:
        expected = "memory/runs/%s/envelopes/%s.json" % (
            request["run_id"], request["parent_event_id"],
        )
        if references[0]["ref"] != expected:
            raise RunEventError("run envelope event requires its canonical runtime reference")


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


def route_state_from_events(selected_events):
    """Derive the typed route chain from one already-selected event ancestry.

    There is intentionally no compatibility fallback for pre-contract route events.
    These runtime changes have not been published, so an untyped legacy event fails
    validation instead of being guessed from snapshots or actor metadata.
    """
    state = None
    for event in selected_events:
        if event["event_type"] != "route_selected":
            continue
        transition = event["dimensions"]["route_transition"]
        target = event["subject"]["ref"]
        if transition == "initial":
            if state is not None:
                raise RunEventError("initial route may appear only once on the selected ancestry")
            chain = [target]
        elif transition == "automatic-handoff":
            if state is None:
                raise RunEventError("automatic-handoff requires a prior route on the selected ancestry")
            if target in state["chain"]:
                raise RunEventError("automatic-handoff target was already visited in the current route chain")
            if len(state["chain"]) >= MAX_ROUTE_CHAIN_SKILLS:
                raise RunEventError("automatic-handoff exceeds the three-handoff route limit")
            chain = [*state["chain"], target]
        elif transition == "user-reroute":
            if state is None:
                raise RunEventError("user-reroute requires a prior route on the selected ancestry")
            # actor.type is observational provenance, not authorization. The typed
            # transition is what resets this operational chain.
            chain = [target]
        else:  # validate_event_semantics should make this unreachable.
            raise RunEventError("route transition is unsupported")
        state = {
            "skill": target,
            "command": event["dimensions"]["route_command"],
            "reason_code": event["reason_code"],
            "transition": transition,
            "chain": chain,
            "chain_depth": len(chain) - 1,
            "event_id": event.get("event_id"),
        }
    return state


def selected_route_state(events, parent_event_id):
    """Return route state from the root-to-parent ancestry, never sibling events."""
    return route_state_from_events(event_ancestry(events, parent_event_id))


def validate_event_transition(request, events):
    """Validate stream-relative lifecycle transitions on the selected branch."""
    event_type = request["event_type"]
    if event_type == "route_selected":
        # Include the proposed event in the reducer so every route invariant has a
        # single implementation shared by append and stream replay.
        route_state_from_events([
            *event_ancestry(events, request["parent_event_id"]), request,
        ])
        return
    if event_type == "loop_state_changed":
        ancestry = event_ancestry(events, request["parent_event_id"])
        prior = [
            event for event in ancestry
            if event["event_type"] == "loop_state_changed"
            and event["subject"]["ref"] == request["subject"]["ref"]
        ]
        expected_sequence = len(prior) + 1
        if request["metrics"]["sequence"] != expected_sequence:
            raise RunEventError(
                "loop_state_changed sequence does not extend the selected-ancestry loop"
            )
        return
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
            "route_skill": None, "route_command": None,
            "route_reason_code": None, "route_transition": None,
            "route_chain": [], "automatic_handoff_depth": None,
            "loop_states": [],
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
    route_state = route_state_from_events(selected_path)
    open_tools = set()
    last_snapshot = last_snapshot_hash = last_save = last_save_hash = None
    envelope = envelope_hash = None
    validated_artifacts = []
    loop_states = {}
    for event in selected_path:
        if event["event_type"] in {"tool_requested", "tool_allowed"}:
            open_tools.add(event["subject"]["ref"])
        elif event["event_type"] in {"tool_blocked", "tool_finished"}:
            open_tools.discard(event["subject"]["ref"])
        elif event["event_type"] == "loop_state_changed":
            reference = event["references"][0]
            loop_states[event["subject"]["ref"]] = {
                "loop_id": event["subject"]["ref"],
                "state": event["dimensions"]["loop_state"],
                "reason_code": event["reason_code"],
                "sequence": event["metrics"]["sequence"],
                "cycle": event["metrics"]["cycle"],
                "total_retries": event["metrics"]["total_retries"],
                "step_ref": reference["ref"],
                "step_sha256": reference["sha256"],
            }
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
        "route_skill": route_state["skill"] if route_state else None,
        "route_command": route_state["command"] if route_state else None,
        "route_reason_code": route_state["reason_code"] if route_state else None,
        "route_transition": route_state["transition"] if route_state else None,
        "route_chain": route_state["chain"] if route_state else [],
        "automatic_handoff_depth": route_state["chain_depth"] if route_state else None,
        "loop_states": [loop_states[key] for key in sorted(loop_states)],
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
    flags |= getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    pre_open = anchored_lstat(parent_fd, path.parent, path.name, missing_ok=True)
    if pre_open is not None and (
            statmod.S_ISLNK(pre_open.st_mode) or not statmod.S_ISREG(pre_open.st_mode)
            or pre_open.st_nlink != 1):
        os.close(parent_fd)
        raise RunEventError("run event stream must be a stable single-link regular file")
    preexisting = pre_open is not None
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
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
                or (
                    pre_open is not None
                    and (opened.st_dev, opened.st_ino) != (pre_open.st_dev, pre_open.st_ino)
                )):
            raise RunEventError("run event stream must be a stable single-link regular file")
        if exclusive:
            os.fchmod(fd, 0o600)
            if not preexisting:
                os.fsync(parent_fd)
        elif statmod.S_IMODE(opened.st_mode) != 0o600:
            raise RunEventError("run event stream must use private file mode 0600")
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


def ensure_coordinator_lock(path):
    """Publish one empty coordinator inode without acquiring a narrower lock."""
    parent_fd, identity = open_directory_anchor(path.parent)
    descriptor = None
    try:
        entry = anchored_lstat(parent_fd, path.parent, path.name, missing_ok=True)
        if entry is None:
            flags = (
                os.O_WRONLY | os.O_CREAT | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                descriptor = os.open(
                    path.name, flags, 0o600, dir_fd=parent_fd,
                )
            except FileExistsError:
                pass
            else:
                os.fchmod(descriptor, 0o600)
                os.fsync(descriptor)
                os.close(descriptor)
                descriptor = None
                os.fsync(parent_fd)
        entry = anchored_lstat(parent_fd, path.parent, path.name)
        if (
                statmod.S_ISLNK(entry.st_mode)
                or not statmod.S_ISREG(entry.st_mode)
                or entry.st_nlink != 1):
            raise RunEventError(
                "run coordinator lock must be a stable single-link regular file"
            )
        revalidate_anchor(parent_fd, path.parent, identity)
    except OSError as exc:
        raise RunEventError(
            "cannot publish run coordinator lock %s: %s" % (path, exc)
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent_fd)


@contextlib.contextmanager
def locked_run_coordinator(root, run_id, create=False):
    """Serialize a run mutation before any narrower stream or artifact lock."""
    root_path = normalized_root(root)
    stream, _projection, run_dir = run_paths(root_path, run_id, create=create)
    status = _lstat(run_dir, "run directory", missing_ok=True)
    if status is None:
        raise RunEventError("run does not exist: %s" % run_id)
    if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISDIR(status.st_mode):
        raise RunEventError("run directory must be a real directory")
    lock_path = run_dir / ".coordinator.lock"
    ensure_ignored(root_path, [lock_path])
    if (
            not create
            and _lstat(stream, "run event stream", missing_ok=True) is None):
        raise RunEventError("run does not exist: %s" % run_id)
    ensure_coordinator_lock(lock_path)
    with locked_stream(lock_path, exclusive=True, create=False) as handle:
        if (
                not create
                and _lstat(stream, "run event stream", missing_ok=True) is None):
            raise RunEventError("run does not exist: %s" % run_id)
        yield handle


@contextlib.contextmanager
def anchored_regular_file(path):
    resolved_parent = normalized_root(path.parent)
    parent_fd, identity = open_directory_anchor(resolved_parent)
    fd = None
    try:
        pre_open = anchored_lstat(parent_fd, resolved_parent, path.name)
        if (
                statmod.S_ISLNK(pre_open.st_mode) or not statmod.S_ISREG(pre_open.st_mode)
                or pre_open.st_nlink != 1):
            raise RunEventError(
                "referenced file must be a stable single-link regular file: %s" % path
            )
        flags = (
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        )
        fd = os.open(path.name, flags, dir_fd=parent_fd)
        opened = os.fstat(fd)
        entry = anchored_lstat(parent_fd, resolved_parent, path.name)
        if (
                not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or statmod.S_ISLNK(entry.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
                or (opened.st_dev, opened.st_ino) != (pre_open.st_dev, pre_open.st_ino)):
            raise RunEventError("referenced file must be a stable single-link regular file: %s" % path)
        with os.fdopen(fd, "rb") as handle:
            fd = None
            yield handle
            revalidate_anchor(parent_fd, resolved_parent, identity)
            opened = os.fstat(handle.fileno())
            entry = anchored_lstat(parent_fd, resolved_parent, path.name)
            if (
                    opened.st_nlink != 1
                    or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
                raise RunEventError("referenced file changed during inspection: %s" % path)
    except OSError as exc:
        raise RunEventError("cannot open referenced file %s: %s" % (path, exc)) from exc
    finally:
        if fd is not None:
            os.close(fd)
        os.close(parent_fd)


@contextlib.contextmanager
def anchored_project_file(root, reference):
    """Open a project-relative file without following any reference component."""
    validate_ref(reference, "artifact ref")
    root_path = normalized_root(root)
    root_fd, root_identity = open_directory_anchor(root_path)
    descriptors = [root_fd]
    links = []
    file_fd = None
    parts = reference.split("/")
    parent_fd = root_fd
    parent_path = root_path
    path = root_path.joinpath(*parts)
    directory_flags = (
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        for component in parts[:-1]:
            pre_open = anchored_lstat(parent_fd, parent_path, component)
            if statmod.S_ISLNK(pre_open.st_mode) or not statmod.S_ISDIR(pre_open.st_mode):
                raise RunEventError(
                    "project reference directory must be a real directory: %s"
                    % (parent_path / component)
                )
            child_fd = None
            try:
                child_fd = os.open(component, directory_flags, dir_fd=parent_fd)
                opened = os.fstat(child_fd)
                entry = anchored_lstat(parent_fd, parent_path, component)
                identity = (opened.st_dev, opened.st_ino)
                if (
                        not statmod.S_ISDIR(opened.st_mode) or statmod.S_ISLNK(entry.st_mode)
                        or identity != (entry.st_dev, entry.st_ino)
                        or identity != (pre_open.st_dev, pre_open.st_ino)):
                    raise RunEventError(
                        "project reference directory changed or is unsafe: %s"
                        % (parent_path / component)
                    )
            except Exception:
                if child_fd is not None:
                    os.close(child_fd)
                raise
            descriptors.append(child_fd)
            links.append((parent_fd, parent_path, component, child_fd, identity))
            parent_fd = child_fd
            parent_path = parent_path / component

        name = parts[-1]
        pre_open = anchored_lstat(parent_fd, parent_path, name)
        if (
                statmod.S_ISLNK(pre_open.st_mode) or not statmod.S_ISREG(pre_open.st_mode)
                or pre_open.st_nlink != 1):
            raise RunEventError(
                "referenced file must be a stable single-link regular file: %s" % path
            )
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        file_fd = os.open(name, flags, dir_fd=parent_fd)
        opened = os.fstat(file_fd)
        entry = anchored_lstat(parent_fd, parent_path, name)
        if (
                not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or statmod.S_ISLNK(entry.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)
                or (opened.st_dev, opened.st_ino) != (pre_open.st_dev, pre_open.st_ino)):
            raise RunEventError(
                "referenced file must be a stable single-link regular file: %s" % path
            )
        with os.fdopen(file_fd, "rb") as handle:
            file_fd = None
            yield path, handle
            after = os.fstat(handle.fileno())
            current = anchored_lstat(parent_fd, parent_path, name)
            if (
                    after.st_nlink != 1
                    or (after.st_dev, after.st_ino) != (current.st_dev, current.st_ino)):
                raise RunEventError("referenced file changed during inspection: %s" % path)
            for ancestor_fd, ancestor_path, component, child_fd, identity in reversed(links):
                child = os.fstat(child_fd)
                current = anchored_lstat(ancestor_fd, ancestor_path, component)
                if (
                        statmod.S_ISLNK(current.st_mode)
                        or (child.st_dev, child.st_ino) != identity
                        or (current.st_dev, current.st_ino) != identity):
                    raise RunEventError("project reference directory changed during inspection")
            revalidate_anchor(root_fd, root_path, root_identity)
    except OSError as exc:
        raise RunEventError("cannot open project reference %s: %s" % (reference, exc)) from exc
    finally:
        if file_fd is not None:
            os.close(file_fd)
        for descriptor in reversed(descriptors):
            os.close(descriptor)


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


def anchored_file_mode(path):
    with anchored_regular_file(path) as handle:
        return statmod.S_IMODE(os.fstat(handle.fileno()).st_mode)


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
    try:
        proposed_raw = (
            json.dumps(
                value, indent=2, sort_keys=True, ensure_ascii=False,
                allow_nan=False,
            ) + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise RunEventError("immutable runtime document must be finite JSON: %s" % exc) from exc
    if len(proposed_raw) > MAX_DOCUMENT_BYTES:
        raise RunEventError(
            "immutable runtime document exceeds %d bytes" % MAX_DOCUMENT_BYTES
        )
    recover_immutable_install(path)
    status = _lstat(path, "runtime document", missing_ok=True)
    if status is not None:
        if statmod.S_ISLNK(status.st_mode) or not statmod.S_ISREG(status.st_mode) or status.st_nlink != 1:
            raise RunEventError("immutable runtime document must be a single-link regular file")
    else:
        atomic_create_json(root, path, value)
    root_path = normalized_root(root)
    try:
        reference = str(Path(os.path.abspath(path)).relative_to(root_path))
    except ValueError as exc:
        raise RunEventError("immutable runtime document escapes the project root") from exc
    _installed_path, raw, metadata = _stable_project_read(
        root_path, reference, MAX_DOCUMENT_BYTES, "immutable runtime document",
    )
    try:
        installed = strict_json_loads(raw.decode("utf-8"), "immutable runtime document")
    except UnicodeDecodeError as exc:
        raise RunEventError("immutable runtime document must be UTF-8") from exc
    if canonical_json(installed) != canonical_json(value):
        raise RunEventError(
            "immutable runtime document already exists with different content: %s" % path
        )
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("immutable runtime document must use private file mode 0600")
    return hashlib.sha256(raw).hexdigest()


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


def ensure_event_capacity(events, event_type):
    """Reserve the final stream slot exclusively for a terminal envelope."""
    if len(events) >= MAX_EVENTS:
        raise RunEventError("event stream has reached the %d event limit" % MAX_EVENTS)
    if len(events) >= MAX_EVENTS - 1 and event_type not in TERMINAL_TYPES:
        raise RunEventError(
            "event stream reserves its final slot for a terminal run envelope"
        )


def _looks_like_control_artifact(raw):
    try:
        document = strict_json_loads(raw.decode("utf-8"), "artifact candidate")
    except (UnicodeDecodeError, RunEventError):
        return False
    return (
        isinstance(document, dict)
        and document.get("$schema") == CONTROL_ARTIFACT_SCHEMA_REF
    )


def validate_artifact_validation_event(root, request, control_session=None):
    """Verify the bytes behind an ``artifact_validated`` event before append."""
    if request["event_type"] != "artifact_validated":
        return None
    reference = request["references"][0]
    _path, raw, metadata = _stable_project_read(
        root, reference["ref"], MAX_REFERENCE_BYTES, "validated artifact",
    )
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise RunEventError(
            "referenced artifact hash mismatch: %s" % reference["ref"]
        )
    validator_id = request["dimensions"]["validator"]
    if _looks_like_control_artifact(raw) and validator_id != CONTROL_ARTIFACT_VALIDATOR:
        raise RunEventError(
            "control artifact schema requires validator=%s"
            % CONTROL_ARTIFACT_VALIDATOR
        )
    if validator_id == CONTROL_ARTIFACT_VALIDATOR:
        return validate_control_artifact_reference(
            root, reference["ref"], reference["sha256"], control_session,
        )
    return metadata.st_size


def _validated_control_record(root, event, record_cache=None):
    """Read the exact control bytes already attested by ``event``."""
    if (
            event["event_type"] != "artifact_validated"
            or event["dimensions"].get("validator") != CONTROL_ARTIFACT_VALIDATOR):
        return None
    reference = event["references"][0]
    identity = (reference["ref"], reference["sha256"])
    if record_cache is not None and identity in record_cache:
        return record_cache[identity]
    _path, raw, _metadata = _stable_project_read(
        root, reference["ref"], MAX_DOCUMENT_BYTES, "control artifact",
    )
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise RunEventError(
            "referenced control artifact hash mismatch: %s" % reference["ref"]
        )
    try:
        record = strict_json_loads(raw.decode("utf-8"), "control artifact")
    except UnicodeDecodeError as exc:
        raise RunEventError("control artifact must be UTF-8") from exc
    if (
            not isinstance(record, dict)
            or record.get("$schema") != CONTROL_ARTIFACT_SCHEMA_REF
            or record.get("schema_version") != SCHEMA_VERSION):
        raise RunEventError("validated control artifact identity is invalid")
    if record_cache is not None:
        record_cache[identity] = record
    return record


def _receipt_intent_identity(record):
    if not isinstance(record, dict) or record.get("kind") != "action-receipt":
        return None
    payload = record.get("payload", {})
    return ("action-intent", payload.get("intent_id"))


def ensure_single_use_receipt_available(
        root, events, request, proposed_record, control_session=None,
        record_cache=None):
    """Reject a second receipt for one logical single-use intent ancestry.

    The run coordinator and stream lock make this check-plus-append atomic.
    Copying or renaming the bound intent does not mint a new logical intent.
    Sibling branches intentionally do not consume one another; an exact retry
    is handled by the event idempotency check before reaching a new append.
    """
    intent_identity = _receipt_intent_identity(proposed_record)
    if intent_identity is None:
        return
    session = control_session or _control_validation_session()
    cache = record_cache if record_cache is not None else {}
    for event in event_ancestry(events, request["parent_event_id"]):
        if (
                event["event_type"] != "artifact_validated"
                or event["dimensions"].get("validator")
                    != CONTROL_ARTIFACT_VALIDATOR):
            continue
        validate_artifact_validation_event(root, event, session)
        ancestor_record = _validated_control_record(root, event, cache)
        if _receipt_intent_identity(ancestor_record) == intent_identity:
            raise RunEventError(
                "single-use action-intent already has a terminal receipt on "
                "the selected ancestry"
            )


def validate_artifact_validation_events(root, events, selected_event_ids=None):
    selected = set(selected_event_ids) if selected_event_ids is not None else None
    candidates = [
        event for event in events
        if (
            event["event_type"] == "artifact_validated"
            and (selected is None or event["event_id"] in selected)
        )
    ]
    identities = {
        (
            event["references"][0]["ref"],
            event["references"][0]["sha256"],
            event["dimensions"]["validator"],
        )
        for event in candidates
    }
    if len(identities) > MAX_VALIDATED_ARTIFACTS_PER_BOUNDARY:
        raise RunEventError(
            "artifact replay exceeds the %d-artifact boundary budget"
            % MAX_VALIDATED_ARTIFACTS_PER_BOUNDARY
        )
    session = _control_validation_session()
    records = {}
    inspected_bytes = 0
    seen = set()
    for event in candidates:
        identity = (
            event["references"][0]["ref"],
            event["references"][0]["sha256"],
            event["dimensions"]["validator"],
        )
        if identity in seen:
            continue
        seen.add(identity)
        inspected_bytes += validate_artifact_validation_event(
            root, event, session,
        )
        if event["dimensions"].get("validator") == CONTROL_ARTIFACT_VALIDATOR:
            _validated_control_record(root, event, records)
        if inspected_bytes > MAX_REFERENCE_INSPECTION_BYTES:
            raise RunEventError(
                "artifact replay exceeds %d inspected bytes"
                % MAX_REFERENCE_INSPECTION_BYTES
            )
    for event in candidates:
        record = _validated_control_record(root, event, records)
        if _receipt_intent_identity(record) is not None:
            ensure_single_use_receipt_available(
                root, events, event, record, session, records,
            )
    return len(seen)


def ensure_artifact_validation_capacity(events, request):
    if request["event_type"] != "artifact_validated":
        return
    identities = {
        (
            event["references"][0]["ref"],
            event["references"][0]["sha256"],
            event["dimensions"]["validator"],
        )
        for event in events if event["event_type"] == "artifact_validated"
    }
    reference = request["references"][0]
    identities.add((
        reference["ref"], reference["sha256"],
        request["dimensions"]["validator"],
    ))
    if len(identities) > MAX_VALIDATED_ARTIFACTS_PER_BOUNDARY:
        raise RunEventError(
            "run cannot exceed the %d-artifact replay boundary"
            % MAX_VALIDATED_ARTIFACTS_PER_BOUNDARY
        )


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
        validate_artifact_validation_event(root, normalized)
        projected = project_events(run_id, events)
        atomic_write_json(normalized_root(root), projection_path, projected)
        return {"deduplicated": True, "event": existing, "projection": projected}
    if events and events[-1]["event_type"] in TERMINAL_TYPES:
        raise RunEventError("terminal run cannot accept another event")
    ensure_event_capacity(events, normalized["event_type"])
    if not events and normalized["event_type"] != "run_started":
        raise RunEventError("new run must start with run_started")
    if events and normalized["parent_event_id"] not in {event["event_id"] for event in events}:
        raise RunEventError("parent_event_id must reference an existing event")
    validate_event_transition(normalized, events)
    ensure_artifact_validation_capacity(events, normalized)
    control_session = _control_validation_session()
    validate_artifact_validation_event(root, normalized, control_session)
    if (
            normalized["event_type"] == "artifact_validated"
            and normalized["dimensions"].get("validator")
                == CONTROL_ARTIFACT_VALIDATOR):
        record_cache = {}
        proposed_record = _validated_control_record(
            root, normalized, record_cache,
        )
        ensure_single_use_receipt_available(
            root, events, normalized, proposed_record,
            control_session, record_cache,
        )
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


def _append_event_under_coordinator(root, run_id, normalized, allow_hook_retry=False):
    """Append one already validated request while the caller owns coordination."""
    stream, projection, _ = run_paths(root, run_id, create=True)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        return append_locked(
            root, run_id, handle, events, normalized, projection, allow_hook_retry,
        )


def append_event(root, run_id, request, allow_hook_retry=False):
    normalized = validate_event_request(request)
    if normalized["event_type"] in INTERNAL_EVENT_TYPES:
        raise RunEventError("%s is reserved for its typed runtime command" % normalized["event_type"])
    reserved = next((prefix for prefix in RESERVED_IDEMPOTENCY_PREFIXES
                     if normalized["idempotency_key"].startswith(prefix)), None)
    if reserved and not (allow_hook_retry and reserved == "hook:"):
        raise RunEventError("idempotency key prefix is reserved for the runtime")
    root_path = normalized_root(root)
    stream, _projection, _run_dir = run_paths(root_path, run_id, create=False)
    stream_missing = _lstat(stream, "run event stream", missing_ok=True) is None
    if stream_missing and normalized["event_type"] != "run_started":
        raise RunEventError("new run must start with run_started")
    with locked_run_coordinator(root_path, run_id, create=stream_missing):
        return _append_event_under_coordinator(
            root_path, run_id, normalized, allow_hook_retry,
        )


def _append_hook_event_under_coordinator(root, run_id, request):
    """Append a hook event while the caller owns the per-run coordinator."""
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


def append_hook_event(root, run_id, request):
    """Append a hook event against the current head under run coordination."""
    root_path = normalized_root(root)
    stream, _projection, _run_dir = run_paths(root_path, run_id, create=False)
    if _lstat(stream, "run event stream", missing_ok=True) is None:
        return None
    with locked_run_coordinator(root_path, run_id):
        return _append_hook_event_under_coordinator(root_path, run_id, request)


def load_events(root, run_id):
    stream, _, _ = run_paths(root, run_id, create=False)
    if _lstat(stream, "run event stream", missing_ok=True) is None:
        raise RunEventError("run does not exist: %s" % run_id)
    with locked_stream(stream, exclusive=False) as handle:
        return read_stream(handle, run_id)


def _validate_loop_step_document(run_id, loop_id, reference, document):
    """Validate the branch-binding fields of one in-memory v2 loop step."""
    validate_ref(reference, "loop step ref")
    if not isinstance(document, dict):
        raise RunEventError("audit loop step must be an object")
    exact_object(document, LOOP_STEP_FIELDS, set(), "audit loop step")
    if document["schema_version"] != AUDIT_LOOP_SCHEMA_VERSION:
        raise RunEventError("audit loop step schema_version is unsupported")
    if document["run_id"] != run_id or document["loop_id"] != loop_id:
        raise RunEventError("audit loop step identity does not match the run and loop")
    validate_uuid(document["transition_id"], "audit loop transition_id")
    validate_uuid(document["run_parent_event_id"], "audit loop run_parent_event_id")
    validate_sha(
        document["run_parent_event_sha256"],
        "audit loop run_parent_event_sha256",
    )
    validate_enum(document["state"], LOOP_STATES, "audit loop state")
    validate_safe_id(document["reason_code"], "audit loop reason_code")
    parse_datetime(document["occurred_at"], "audit loop occurred_at")
    for name, minimum, maximum in (
            ("sequence", 1, 128), ("cycle", 1, 3), ("total_retries", 0, 128)):
        value = document[name]
        if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
            raise RunEventError("audit loop %s is out of range" % name)
    if document["proposal_only"] is not True or document["external_mutation_authorized"] is not False:
        raise RunEventError("audit loop step widened the proposal-only authority boundary")
    prefix = "memory/runs/%s/loops/%s/" % (run_id, loop_id)
    expected_name = "%03d-%s.json" % (document["sequence"], document["transition"])
    if reference != prefix + expected_name:
        raise RunEventError("audit loop step reference is not canonical for its identity")
    return strict_json_loads(canonical_json(document), "normalized audit loop step")


def _validate_loop_step_wrapper(root, run_id, loop_id, wrapper):
    root_path = normalized_root(root)
    exact_object(wrapper, {"document", "ref", "sha256"}, set(), "loop step wrapper")
    validate_ref(wrapper["ref"], "loop step wrapper.ref")
    validate_sha(wrapper["sha256"], "loop step wrapper.sha256")
    path, installed, metadata = verified_json_reference(
        root_path, wrapper["ref"], wrapper["sha256"], "immutable audit loop step",
    )
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("immutable audit loop step must use private file mode 0600")
    ensure_ignored(root_path, [path])
    if not isinstance(wrapper["document"], dict) or canonical_json(installed) != canonical_json(
            wrapper["document"]):
        raise RunEventError("loop step wrapper does not match the installed bytes")
    document = _validate_loop_step_document(run_id, loop_id, wrapper["ref"], installed)
    return {"document": document, "ref": wrapper["ref"], "sha256": wrapper["sha256"]}


def _resolve_loop_steps_via_cli(root, run_id, loop_id, reference, expected_sha256):
    tool = Path(__file__).with_name("audit-loop.py")
    if not tool.is_file():
        raise RunEventError("audit loop runtime is unavailable")
    try:
        completed = subprocess.run(
            [
                sys.executable, str(tool), "show", "--root", str(root),
                "--run-id", run_id, "--loop-id", loop_id,
            ],
            cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunEventError("audit loop chain validation could not run: %s" % exc) from exc
    if completed.returncode:
        detail = " ".join(
            completed.stdout.decode("utf-8", errors="replace").splitlines()[-3:]
        )[:500]
        raise RunEventError("audit loop chain validation failed: %s" % (detail or "invalid loop"))
    try:
        result = strict_json_loads(completed.stdout.decode("utf-8"), "audit loop show result")
    except UnicodeDecodeError as exc:
        raise RunEventError("audit loop show result must be UTF-8") from exc
    exact_object(
        result, {"steps", "head_ref", "head_sha256", "head", "chain"}, set(),
        "audit loop show result",
    )
    if (
            not isinstance(result["steps"], int) or isinstance(result["steps"], bool)
            or result["steps"] < 1 or result["steps"] > 128
            or not isinstance(result["chain"], list)
            or len(result["chain"]) != result["steps"]):
        raise RunEventError("audit loop show result has an invalid bounded chain")
    if result["head_ref"] != reference or result["head_sha256"] != expected_sha256:
        raise RunEventError("only the current verified audit loop head can be recorded")
    wrappers = []
    for index, identity in enumerate(result["chain"], 1):
        exact_object(identity, {"ref", "sha256"}, set(), "audit loop chain identity")
        validate_ref(identity["ref"], "audit loop chain ref")
        validate_sha(identity["sha256"], "audit loop chain sha256")
        _path, document, _metadata = verified_json_reference(
            root, identity["ref"], identity["sha256"], "immutable audit loop step",
        )
        wrapper = _validate_loop_step_wrapper(root, run_id, loop_id, {
            "document": document, "ref": identity["ref"],
            "sha256": identity["sha256"],
        })
        if wrapper["document"]["sequence"] != index:
            raise RunEventError("audit loop show chain sequence is not contiguous")
        wrappers.append(wrapper)
    if (
            wrappers[-1]["ref"] != result["head_ref"]
            or wrappers[-1]["sha256"] != result["head_sha256"]
            or canonical_json(wrappers[-1]["document"]) != canonical_json(result["head"])):
        raise RunEventError("audit loop show head does not match its verified chain")
    return wrappers


def _serialized_immutable_json_bytes(value):
    try:
        return (
            json.dumps(
                value, indent=2, sort_keys=True, ensure_ascii=False,
                allow_nan=False,
            ) + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise RunEventError("immutable runtime document must be finite JSON: %s" % exc) from exc


def _loop_event_matches_wrapper(event, wrapper, events_by_id):
    document = wrapper["document"]
    parent = events_by_id.get(document["run_parent_event_id"])
    return (
        event["event_type"] == "loop_state_changed"
        and event["idempotency_key"] == "loop:" + document["transition_id"]
        and event["parent_event_id"] == document["run_parent_event_id"]
        and parent is not None
        and parent["event_hash"] == document["run_parent_event_sha256"]
        and event["subject"] == {"kind": "loop", "ref": document["loop_id"]}
        and event.get("reason_code") == document["reason_code"]
        and event["references"] == [{
            "kind": "loop", "ref": wrapper["ref"], "sha256": wrapper["sha256"],
        }]
        and event["metrics"] == {
            "sequence": document["sequence"], "cycle": document["cycle"],
            "total_retries": document["total_retries"],
        }
        and event["dimensions"] == {"loop_state": document["state"]}
    )


def _verify_loop_event_coverage_in_events(
        run_id, loop_id, normalized, events, allow_missing_last=False,
        require_selected=False, _allowed_unmaterialized_event_id=None,
        _event_scope_ids=None):
    """Bind every supplied step to one event on one historical ancestry.

    Sibling events for the same loop are intentionally ignored here. Historical
    validity and current-branch selection are separate questions: trends use
    the former, while a mutator opts into ``require_selected``.
    """
    if not events:
        raise RunEventError("audit loop coverage requires a non-empty run")
    if _allowed_unmaterialized_event_id is not None:
        validate_uuid(
            _allowed_unmaterialized_event_id,
            "allowed unmaterialized loop event id",
        )
    events_by_id = {event["event_id"]: event for event in events}
    ancestry_cache = {}

    def ancestry_ids(parent_event_id):
        cached = ancestry_cache.get(parent_event_id)
        if cached is not None:
            return cached
        result = set()
        cursor = events_by_id.get(parent_event_id)
        while cursor is not None:
            result.add(cursor["event_id"])
            cursor = events_by_id.get(cursor["parent_event_id"])
        ancestry_cache[parent_event_id] = result
        return result
    all_loop_events = [
        event for event in events
        if event["event_type"] == "loop_state_changed"
        and event["subject"]["ref"] == loop_id
        and (_event_scope_ids is None or event["event_id"] in _event_scope_ids)
    ]
    matched_events = []
    for index, wrapper in enumerate(normalized):
        matches = [
            event for event in all_loop_events
            if _loop_event_matches_wrapper(event, wrapper, events_by_id)
        ]
        if len(matches) == 1:
            matched_events.append(matches[0])
            continue
        if allow_missing_last and index == len(normalized) - 1 and not matches:
            continue
        raise RunEventError("immutable audit loop step/event coverage is incomplete or ambiguous")
    required = len(normalized) - (1 if allow_missing_last else 0)
    if len(matched_events) < required:
        raise RunEventError("immutable audit loop step/event coverage is incomplete")
    for prior, current in zip(matched_events, matched_events[1:]):
        if prior["event_id"] not in ancestry_ids(current["parent_event_id"]):
            raise RunEventError("audit loop events do not form one event ancestry")
    matched_ids = {event["event_id"] for event in matched_events}
    comparable_extras = []
    for candidate in all_loop_events:
        if candidate["event_id"] in matched_ids:
            continue
        candidate_ancestors = ancestry_ids(candidate["parent_event_id"])
        if any(
                matched["event_id"] in candidate_ancestors
                or candidate["event_id"] in ancestry_ids(matched["parent_event_id"])
                for matched in matched_events):
            comparable_extras.append(candidate)
    if comparable_extras:
        allowed = (
            _allowed_unmaterialized_event_id is not None
            and len(comparable_extras) == 1
            and comparable_extras[0]["event_id"] == _allowed_unmaterialized_event_id
            and matched_events
            and matched_events[-1]["event_id"]
            in ancestry_ids(comparable_extras[0]["parent_event_id"])
            and comparable_extras[0]["metrics"]["sequence"] == len(normalized) + 1
            and comparable_extras[0]["references"][0]["ref"].startswith(
                "memory/runs/%s/loops/%s/%03d-"
                % (run_id, loop_id, len(normalized) + 1)
            )
        )
        if not allowed:
            raise RunEventError(
                "audit loop ancestry has an unmaterialized or forked event"
            )
    if require_selected:
        selected_ids = {
            event["event_id"]
            for event in event_ancestry(events, events[-1]["event_id"])
        }
        if any(event["event_id"] not in selected_ids for event in matched_events):
            raise RunEventError("audit loop history is not on the current selected branch")
    return {
        "steps": len(normalized),
        "events": len(matched_events),
        "event_ids": [event["event_id"] for event in matched_events],
    }


def verify_loop_event_coverage(
        root, run_id, loop_id, wrappers, allow_missing_last=False,
        require_selected=False, _allowed_unmaterialized_event_id=None,
        _event_scope_ids=None):
    """Require one exact same-ancestry event for every immutable loop step."""
    if not isinstance(wrappers, list) or not wrappers:
        raise RunEventError("audit loop coverage requires at least one step")
    normalized = [
        _validate_loop_step_wrapper(root, run_id, loop_id, wrapper) for wrapper in wrappers
    ]
    events = load_events(root, run_id)
    return _verify_loop_event_coverage_in_events(
        run_id, loop_id, normalized, events, allow_missing_last,
        require_selected=require_selected,
        _allowed_unmaterialized_event_id=_allowed_unmaterialized_event_id,
        _event_scope_ids=_event_scope_ids,
    )


def anchor_loop_step(
        root, run_id, loop_id, reference, expected_sha256, document, *,
        _coordinator_locked=False):
    """Anchor a deterministic v2 step event before its file is materialized.

    This is an internal transaction primitive for ``audit-loop.py``. It never
    reads the not-yet-created final file and therefore cannot be reached by the
    public ``loop-step`` command.
    """
    if not _coordinator_locked:
        raise RunEventError("loop step anchoring requires the run coordinator lock")
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    validate_sha(expected_sha256, "loop step sha256")
    normalized_document = _validate_loop_step_document(
        run_id, loop_id, reference, document,
    )
    derived_sha256 = hashlib.sha256(
        _serialized_immutable_json_bytes(normalized_document)
    ).hexdigest()
    if derived_sha256 != expected_sha256:
        raise RunEventError("loop step sha256 does not match its deterministic bytes")
    root_path = normalized_root(root)
    target_path = root_path.joinpath(*reference.split("/"))
    ensure_ignored(
        root_path,
        [
            target_path,
            target_path.parent / (".%s.run-create" % target_path.name),
        ],
    )
    wrapper = {
        "document": normalized_document,
        "ref": reference,
        "sha256": expected_sha256,
    }
    stream, projection, _run_dir = run_paths(root, run_id, create=False)
    with locked_stream(stream, exclusive=True, create=False) as handle:
        events = read_stream(handle, run_id)
        if not events:
            raise RunEventError("audit loop cannot attach to an empty run")
        events_by_id = {event["event_id"]: event for event in events}
        key = "loop:" + normalized_document["transition_id"]
        existing = [event for event in events if event["idempotency_key"] == key]
        if existing:
            if (
                    len(existing) != 1
                    or not _loop_event_matches_wrapper(
                        existing[0], wrapper, events_by_id,
                    )):
                raise RunEventError(
                    "loop event idempotency identity is occupied by another step"
                )
            selected_ids = {
                event["event_id"]
                for event in event_ancestry(events, events[-1]["event_id"])
            }
            target_status = _lstat(
                target_path, "anchored audit loop step", missing_ok=True,
            )
            if (
                    existing[0]["event_id"] not in selected_ids
                    and target_status is not None):
                raise RunEventError(
                    "materialized loop anchor is not on the current selected branch"
                )
            state = project_events(run_id, events)
            atomic_write_json(normalized_root(root), projection, state)
            return {
                "deduplicated": True,
                "event": existing[0],
                "projection": state,
                "artifact": {"ref": reference, "sha256": expected_sha256},
            }

        if events[-1]["event_type"] in TERMINAL_TYPES:
            raise RunEventError("terminal run cannot accept a loop step anchor")
        ensure_event_capacity(events, "loop_state_changed")
        parent = events_by_id.get(normalized_document["run_parent_event_id"])
        if parent is None:
            raise RunEventError("loop step run parent does not exist")
        if parent["event_hash"] != normalized_document["run_parent_event_sha256"]:
            raise RunEventError("loop step run parent hash mismatch")
        if parent["event_id"] != events[-1]["event_id"]:
            raise RunEventError("new loop step must anchor to the selected run head")

        selected_ids = {
            event["event_id"]
            for event in event_ancestry(events, parent["event_id"])
        }
        global_loop_events = [
            event for event in events
            if event["event_type"] == "loop_state_changed"
            and event["subject"]["ref"] == loop_id
        ]
        selected_loop_events = [
            event for event in global_loop_events
            if event["event_id"] in selected_ids
        ]
        if len(global_loop_events) != len(selected_loop_events):
            raise RunEventError("audit loop cannot fork across run branches")
        if normalized_document["sequence"] != len(selected_loop_events) + 1:
            raise RunEventError("loop step sequence does not extend its selected branch")
        if selected_loop_events:
            prior_reference = selected_loop_events[-1]["references"][0]
            if (
                    normalized_document["previous_step_ref"] != prior_reference["ref"]
                    or normalized_document["previous_step_sha256"]
                    != prior_reference["sha256"]):
                raise RunEventError("loop step does not extend its prior anchored step")
        elif (
                normalized_document["previous_step_ref"] is not None
                or normalized_document["previous_step_sha256"] != ZERO_HASH):
            raise RunEventError("first loop step must begin at the zero step hash")

        request = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "idempotency_key": key,
            "event_type": "loop_state_changed",
            "occurred_at": normalized_document["occurred_at"],
            "actor": {"type": "system", "id": "audit-loop"},
            "parent_event_id": normalized_document["run_parent_event_id"],
            "turn_id": None,
            "status": "succeeded",
            "subject": {"kind": "loop", "ref": loop_id},
            "reason_code": normalized_document["reason_code"],
            "references": [{
                "kind": "loop", "ref": reference,
                "sha256": expected_sha256,
            }],
            "metrics": {
                "sequence": normalized_document["sequence"],
                "cycle": normalized_document["cycle"],
                "total_retries": normalized_document["total_retries"],
            },
            "dimensions": {"loop_state": normalized_document["state"]},
        }
        result = append_locked(root, run_id, handle, events, request, projection)
        result["artifact"] = {"ref": reference, "sha256": expected_sha256}
        return result


def _record_loop_step_under_coordinator(
        root, run_id, loop_id, reference, expected_sha256, _resolved_steps=None):
    """Verify that the current immutable loop head already has its exact anchor."""
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    validate_ref(reference, "loop step ref")
    validate_sha(expected_sha256, "loop step sha256")
    external_resolution = _resolved_steps is None
    if external_resolution:
        loop_dir = (
            normalized_root(root) / "memory" / "runs" / run_id / "loops" / loop_id
        )
        loop_guard = locked_stream(
            loop_dir / ".loop.lock", exclusive=False, create=False,
        )
    else:
        loop_guard = contextlib.nullcontext()
    with loop_guard:
        if external_resolution:
            wrappers = _resolve_loop_steps_via_cli(
                root, run_id, loop_id, reference, expected_sha256,
            )
        else:
            if not isinstance(_resolved_steps, list) or not _resolved_steps:
                raise RunEventError("resolved audit loop steps must be a non-empty list")
            wrappers = [
                _validate_loop_step_wrapper(root, run_id, loop_id, item)
                for item in _resolved_steps
            ]
        matches = [
            item for item in wrappers
            if item["ref"] == reference and item["sha256"] == expected_sha256
        ]
        if len(matches) != 1:
            raise RunEventError("resolved audit loop step identity mismatch")
        wrapper = matches[0]
        document = wrapper["document"]
        stream, projection, _ = run_paths(root, run_id, create=False)
        with locked_stream(stream, exclusive=True, create=False) as handle:
            events = read_stream(handle, run_id)
            _verify_loop_event_coverage_in_events(
                run_id, loop_id, wrappers, events,
                require_selected=True,
            )
            key = "loop:" + document["transition_id"]
            existing = [event for event in events if event["idempotency_key"] == key]
            events_by_id = {event["event_id"]: event for event in events}
            if (
                    len(existing) != 1
                    or not _loop_event_matches_wrapper(
                        existing[0], wrapper, events_by_id,
                    )):
                raise RunEventError(
                    "public loop-step requires one exact pre-existing loop anchor"
                )
            state = project_events(run_id, events)
            atomic_write_json(normalized_root(root), projection, state)
            return {
                "deduplicated": True, "event": existing[0], "projection": state,
                "artifact": {"ref": reference, "sha256": expected_sha256},
            }


def record_loop_step(
        root, run_id, loop_id, reference, expected_sha256,
        _resolved_steps=None, _coordinator_locked=False):
    """Verify/dedupe an already anchored loop step; never create its event."""
    if _resolved_steps is not None and not _coordinator_locked:
        raise RunEventError(
            "pre-resolved audit loop steps require the run coordinator lock"
        )
    if _coordinator_locked:
        return _record_loop_step_under_coordinator(
            root, run_id, loop_id, reference, expected_sha256, _resolved_steps,
        )
    with locked_run_coordinator(root, run_id):
        return _record_loop_step_under_coordinator(
            root, run_id, loop_id, reference, expected_sha256, _resolved_steps,
        )


def rebuild_projection(root, run_id):
    stream, projection, _ = run_paths(root, run_id, create=True)
    with locked_stream(stream, exclusive=True) as handle:
        events = read_stream(handle, run_id)
        if not events:
            raise RunEventError("cannot project an empty run")
        validate_artifact_validation_events(root, events)
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
        validate_enum(
            tool["mode"], {"read-only", "proposal-only", "mutating", "external"},
            "tools[%d].mode" % index,
        )
        validate_sha(tool["schema_sha256"], "tools[%d].schema_sha256" % index)
    validate_sha(value["toolset_sha256"], "toolset_sha256")
    if value["toolset_sha256"] != sha256_json(value["tools"]):
        raise RunEventError("toolset_sha256 does not match canonical tools")
    validate_offsets(value["registry_offsets"])
    profile = exact_object(value["permission_profile"], {"mode", "sandbox", "network", "external_mutations"}, set(), "permission_profile")
    validate_enum(
        profile["mode"], {"disabled", "read-only", "proposal-only", "write-gated"},
        "permission_profile.mode",
    )
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
    validate_enum(
        value["status"], {"ready", "waiting", "needs-input", "blocked", "failed", "complete"},
        "save point status",
    )
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
        validate_enum(
            reference["validation_status"], {"valid", "not-required"},
            label + ".validation_status",
        )
    validate_offsets(value["registry_offsets"])
    visited = value["visited_skills"]
    if not isinstance(visited, list) or not visited or len(visited) > 4:
        raise RunEventError("visited_skills must contain 1 to 4 unique skills")
    for index, skill in enumerate(visited):
        validate_safe_id(skill, "visited_skills[%d]" % index)
    if len(visited) != len(set(visited)):
        raise RunEventError("visited_skills must contain 1 to 4 unique skills")
    if not isinstance(value["chain_depth"], int) or isinstance(value["chain_depth"], bool) or not 0 <= value["chain_depth"] <= 3:
        raise RunEventError("chain_depth must be an integer from 0 to 3")
    if value["chain_depth"] != len(visited) - 1:
        raise RunEventError("chain_depth must equal visited_skills length minus one")
    handoff = value["pending_handoff"]
    if handoff is not None:
        exact_object(handoff, {"status", "objective_code", "recommended_skill"}, set(), "pending_handoff")
        validate_enum(
            handoff["status"], {"proposed", "needs-input", "blocked"},
            "pending_handoff.status",
        )
        validate_safe_id(handoff["objective_code"], "pending_handoff.objective_code")
        validate_safe_id(handoff["recommended_skill"], "pending_handoff.recommended_skill")
    validate_next_action(value["next_action"])
    return strict_json_loads(canonical_json(value), "normalized save point")


def validate_loop_closure(value):
    exact_object(
        value,
        {"scope", "selected_head_event_id", "status", "loops"},
        set(),
        "loop_closure",
    )
    if value["scope"] != "selected-ancestry":
        raise RunEventError("loop_closure.scope must be selected-ancestry")
    validate_uuid(
        value["selected_head_event_id"],
        "loop_closure.selected_head_event_id",
    )
    validate_enum(
        value["status"], {"none", "verified", "unresolved"},
        "loop_closure.status",
    )
    loops = value["loops"]
    if not isinstance(loops, list) or len(loops) > MAX_AUDIT_LOOPS:
        raise RunEventError(
            "loop_closure.loops must contain at most %d entries"
            % MAX_AUDIT_LOOPS
        )
    seen = set()
    unresolved = 0
    for index, item in enumerate(loops):
        label = "loop_closure.loops[%d]" % index
        exact_object(
            item,
            {
                "loop_id", "last_loop_event_id", "expected_step_ref",
                "expected_step_sha256", "validation_status", "failure_code",
            },
            set(),
            label,
        )
        validate_uuid(item["loop_id"], label + ".loop_id")
        validate_uuid(item["last_loop_event_id"], label + ".last_loop_event_id")
        validate_ref(item["expected_step_ref"], label + ".expected_step_ref")
        validate_sha(item["expected_step_sha256"], label + ".expected_step_sha256")
        validate_enum(
            item["validation_status"], {"valid", "unresolved"},
            label + ".validation_status",
        )
        if item["validation_status"] == "valid":
            if item["failure_code"] is not None:
                raise RunEventError("valid loop_closure item cannot have failure_code")
        else:
            unresolved += 1
            validate_enum(
                item["failure_code"], LOOP_CLOSURE_FAILURE_CODES,
                label + ".failure_code",
            )
        if item["loop_id"] in seen:
            raise RunEventError("loop_closure cannot repeat a loop_id")
        seen.add(item["loop_id"])
    if value["status"] == "none" and loops:
        raise RunEventError("loop_closure status none requires no loops")
    if value["status"] == "verified" and (not loops or unresolved):
        raise RunEventError("loop_closure status verified requires only valid loops")
    if value["status"] == "unresolved" and not unresolved:
        raise RunEventError("loop_closure status unresolved requires an unresolved loop")
    return strict_json_loads(canonical_json(value), "normalized loop_closure")


def validate_envelope(value):
    required = {
        "schema_version", "run_id", "parent_run_id", "started_at", "ended_at", "status",
        "evidence_mode", "route", "context_manifests", "last_event_id",
        "last_event_offset", "last_event_hash", "save_point", "registry_offsets",
        "artifacts", "metrics", "failure_class", "next_action",
    }
    exact_object(value, required, {"loop_closure"}, "run envelope")
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
    validate_enum(
        value["status"], {"waiting", "needs-input", "blocked", "succeeded", "failed", "aborted"},
        "run envelope status",
    )
    if value["status"] in {"succeeded", "failed", "aborted"} and value["ended_at"] is None:
        raise RunEventError("terminal run envelope requires ended_at")
    validate_enum(value["evidence_mode"], {"none", "simulated", "real", "mixed"}, "evidence_mode")
    degraded_terminal = value["status"] in {"failed", "aborted"}
    route = value["route"]
    if route is None:
        if not degraded_terminal:
            raise RunEventError("only failed or aborted envelopes may omit route")
    else:
        route = exact_object(route, {"skill", "version", "reason_code"}, set(), "route")
        validate_safe_id(route["skill"], "route.skill")
        if not isinstance(route["version"], str) or not SEMVER.fullmatch(route["version"]):
            raise RunEventError("route.version must be semver")
        validate_safe_id(route["reason_code"], "route.reason_code")
    manifests = value["context_manifests"]
    minimum_manifests = 0 if degraded_terminal else 1
    if (
            not isinstance(manifests, list)
            or not minimum_manifests <= len(manifests) <= MAX_CONTEXT_MANIFESTS):
        raise RunEventError(
            "context_manifests must contain %d to %d entries"
            % (minimum_manifests, MAX_CONTEXT_MANIFESTS)
        )
    if not manifests and (route is not None or value["save_point"] is not None):
        raise RunEventError(
            "degraded envelope without context must omit route and save_point"
        )
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
    if (
            not manifests
            and any(offset is not None for offset in value["registry_offsets"].values())):
        raise RunEventError(
            "degraded envelope without context must use unbound null registry offsets"
        )
    if not isinstance(value["artifacts"], list) or len(value["artifacts"]) > 128:
        raise RunEventError("artifacts must be an array with at most 128 entries")
    for index, reference in enumerate(value["artifacts"]):
        validate_artifact_ref(reference, "artifacts[%d]" % index)
    if not isinstance(value["metrics"], dict) or len(value["metrics"]) > 64:
        raise RunEventError("metrics must be an object with at most 64 entries")
    for key, metric in value["metrics"].items():
        if not SAFE_FIELD.fullmatch(key):
            raise RunEventError("run envelope metrics must be finite numeric metadata")
        validate_finite_metric(metric, "run envelope metrics.%s" % key)
    failure_class = value["failure_class"]
    if failure_class is not None:
        validate_enum(
            failure_class,
            {"prompt", "routing", "context", "tool", "permission", "artifact", "loop", "unknown"},
            "failure_class",
        )
    if value["status"] in {"failed", "blocked", "aborted"} and failure_class is None:
        raise RunEventError("failed, blocked, or aborted run envelope requires failure_class")
    validate_next_action(value["next_action"])
    if "loop_closure" in value:
        validate_loop_closure(value["loop_closure"])
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


def _stable_project_read(root, reference, limit, label):
    with anchored_project_file(root, reference) as (path, handle):
        before = os.fstat(handle.fileno())
        if before.st_size > limit:
            raise RunEventError("%s exceeds %d bytes" % (label, limit))
        raw = handle.read(limit + 1)
        after = os.fstat(handle.fileno())
        stable_fields = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
        if len(raw) != before.st_size or any(
                getattr(before, field) != getattr(after, field) for field in stable_fields):
            raise RunEventError("%s changed during inspection" % label)
    return path, raw, after


def resolve_project_reference(root, reference, expected_sha, max_bytes=MAX_REFERENCE_BYTES):
    path, raw, metadata = _stable_project_read(
        root, reference, max_bytes, "referenced artifact",
    )
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise RunEventError("referenced artifact hash mismatch: %s" % reference)
    return path, metadata.st_size


def validate_non_control_artifact_reference(root, reference, expected_sha):
    path, raw, metadata = _stable_project_read(
        root, reference, MAX_REFERENCE_BYTES, "referenced artifact",
    )
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise RunEventError("referenced artifact hash mismatch: %s" % reference)
    if _looks_like_control_artifact(raw):
        raise RunEventError(
            "control artifact schema requires validator=%s"
            % CONTROL_ARTIFACT_VALIDATOR
        )
    return path, metadata.st_size


def _control_validation_session():
    return {
        "deadline": time.monotonic() + MAX_CONTROL_ARTIFACT_VALIDATION_SECONDS,
        "results": {},
    }


def validate_control_artifact_reference(
        root, reference, expected_sha, validation_session=None):
    """Live-validate one exact project-relative control artifact.

    The run event is only an observation that this validator succeeded.  The
    referenced bytes remain the evidence, so callers must re-run this check at
    append, checkpoint, and replay boundaries rather than trusting event
    metadata or a caller-supplied ``validation_status``.
    """
    session = validation_session or _control_validation_session()
    validate_ref(reference, "control artifact ref")
    validate_sha(expected_sha, "control artifact sha256")
    root_path = normalized_root(root)
    cache_key = (str(root_path), reference, expected_sha)
    if cache_key in session["results"]:
        return session["results"][cache_key]
    remaining = session["deadline"] - time.monotonic()
    if remaining <= 0:
        raise RunEventError(
            "control artifact validation exceeded the %d-second boundary budget"
            % MAX_CONTROL_ARTIFACT_VALIDATION_SECONDS
        )
    _path, raw, metadata = _stable_project_read(
        root_path, reference, MAX_DOCUMENT_BYTES, "control artifact",
    )
    actual_sha = hashlib.sha256(raw).hexdigest()
    if actual_sha != expected_sha:
        raise RunEventError(
            "referenced control artifact hash mismatch: %s" % reference
        )
    validator = Path(__file__).with_name("validate-control-artifact.py")
    validator_status = _lstat(
        validator, "control artifact validator", missing_ok=True,
    )
    if (
            validator_status is None or statmod.S_ISLNK(validator_status.st_mode)
            or not statmod.S_ISREG(validator_status.st_mode)):
        raise RunEventError("control artifact validator is unavailable or unsafe")
    try:
        result = subprocess.run(
            [
                sys.executable, "-I", str(validator), "validate", "-",
                "--project-root", str(root_path),
            ],
            cwd=root_path, input=raw, env={},
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=remaining,
        )
    except subprocess.TimeoutExpired as exc:
        raise RunEventError(
            "control artifact validation timed out within the %d-second boundary budget"
            % MAX_CONTROL_ARTIFACT_VALIDATION_SECONDS
        ) from exc
    except OSError as exc:
        raise RunEventError(
            "control artifact validation could not run: %s" % exc
        ) from exc
    output_lines = result.stdout.decode(
        "utf-8", errors="replace",
    ).splitlines()
    expected_attestation = re.compile(
        r"^valid [a-z0-9-]+ sha256:%s$" % re.escape(expected_sha)
    )
    if (
            result.returncode
            or len(output_lines) != 1
            or expected_attestation.fullmatch(output_lines[0]) is None):
        detail = " ".join(output_lines[-3:])[:500]
        raise RunEventError(
            "control artifact validation failed: %s"
            % (detail or "validator did not attest the exact artifact digest")
        )

    # Re-read after the subprocess inspected all linked bindings.  This catches
    # in-place mutation or replacement during validation before any event is
    # appended; subsequent checkpoint/replay checks catch later drift.
    _verified_path, verified_raw, verified_metadata = _stable_project_read(
        root_path, reference, MAX_DOCUMENT_BYTES, "control artifact",
    )
    stable_fields = (
        "st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns",
    )
    if raw != verified_raw or any(
            getattr(metadata, field) != getattr(verified_metadata, field)
            for field in stable_fields):
        raise RunEventError("control artifact changed during validation: %s" % reference)
    if time.monotonic() > session["deadline"]:
        raise RunEventError(
            "control artifact validation exceeded the %d-second boundary budget"
            % MAX_CONTROL_ARTIFACT_VALIDATION_SECONDS
        )
    session["results"][cache_key] = verified_metadata.st_size
    return verified_metadata.st_size


def verified_json_reference(root, reference, expected_sha, label, limit=MAX_DOCUMENT_BYTES):
    validate_ref(reference, label + " ref")
    path, raw, metadata = _stable_project_read(root, reference, limit, label)
    if hashlib.sha256(raw).hexdigest() != expected_sha:
        raise RunEventError("referenced artifact hash mismatch: %s" % reference)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RunEventError("%s must be UTF-8" % label) from exc
    return path, strict_json_loads(text, label), metadata


def _load_context_resolver_validator():
    validator_path = Path(__file__).with_name("context-resolver.py")
    if not validator_path.is_file():
        raise RunEventError("context resolver is unavailable for manifest validation")
    spec = importlib.util.spec_from_file_location("aaron_context_resolver", validator_path)
    if spec is None or spec.loader is None:
        raise RunEventError("context resolver cannot be loaded for manifest validation")
    validator = importlib.util.module_from_spec(spec)
    source = validator_path.read_bytes()
    exec(
        compile(source, str(validator_path), "exec", dont_inherit=True),
        validator.__dict__,
    )
    return validator


def validate_context_document(root, reference, expected_sha, expected_signature,
                              run_id, turn_id=None, verify_sources=False):
    path, document, metadata = verified_json_reference(
        root, reference, expected_sha, "context manifest", MAX_CONTEXT_MANIFEST_BYTES,
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
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("context manifest must use private file mode 0600")
    try:
        validator = _load_context_resolver_validator()
        validator.validate_manifest(document)
        expected_reference = "memory/runs/%s/turns/%s/context-manifest.json" % (
            document["run_id"], document["turn_id"],
        )
        if reference != expected_reference:
            raise RunEventError(
                "context manifest must use its canonical private run/turn reference: %s"
                % expected_reference
            )
        validator.ensure_ignored(root, [reference])
        if verify_sources:
            validator.verify_manifest_sources(
                document, Path(__file__).resolve().parents[1], root,
            )
    except RunEventError:
        raise
    except Exception as exc:
        raise RunEventError("context manifest fails the resolver contract: %s" % exc) from exc
    return path, document, metadata


def validate_snapshot_context_binding(snapshot, context, route_state=None):
    route = context["route"]
    if snapshot["skill"]["name"] != route["target_skill"]:
        raise RunEventError("turn snapshot skill does not match the context route")
    if snapshot["skill"]["version"] != route["skill_version"]:
        raise RunEventError("turn snapshot skill version does not match the context target skill")
    if snapshot["skill"]["contract_sha256"] != route["skill_sha256"]:
        raise RunEventError("turn snapshot contract hash does not match the context target skill")
    if snapshot["registry_offsets"] != context["registry_offsets"]:
        raise RunEventError("turn snapshot registry offsets do not match its context manifest")
    if route_state is not None:
        expected = {
            "target_skill": route_state["route_skill"],
            "command": route_state["route_command"],
            "reason_code": route_state["route_reason_code"],
        }
        actual = {field: route[field] for field in expected}
        if actual != expected:
            raise RunEventError(
                "turn snapshot context route does not match the latest typed route event"
            )
    return snapshot


def validate_snapshot_document(root, reference, expected_sha, run_id, turn_id):
    path, document, metadata = verified_json_reference(
        root, reference, expected_sha, "turn snapshot"
    )
    normalized = validate_snapshot(document)
    if normalized["run_id"] != run_id or normalized["turn_id"] != turn_id:
        raise RunEventError("turn snapshot does not belong to the save-point run/turn")
    expected_reference = "memory/runs/%s/turns/%s/snapshot.json" % (run_id, turn_id)
    if reference != expected_reference:
        raise RunEventError("turn snapshot must use its canonical private run/turn reference")
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("turn snapshot must use private file mode 0600")
    ensure_ignored(root, [path])
    return normalized


def validate_save_point_document(
        root, reference, expected_sha, run_id, events=None,
        parent_event_id=None, control_session=None):
    path, document, metadata = verified_json_reference(root, reference, expected_sha, "save point")
    normalized = validate_save_point(document)
    if normalized["run_id"] != run_id:
        raise RunEventError("save point does not belong to the envelope run")
    expected_reference = "memory/runs/%s/save-points/%s.json" % (
        run_id, normalized["save_point_id"],
    )
    if reference != expected_reference:
        raise RunEventError("save point must use its canonical private run reference")
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("save point must use private file mode 0600")
    ensure_ignored(root, [path])
    validate_save_point_artifact_references(
        root, normalized["artifacts"], events, parent_event_id, control_session,
    )
    return normalized


def selected_branch_snapshots(root, run_id, events, state):
    events_by_id = {event["event_id"]: event for event in events}
    snapshots = []
    parent_turn_id = None
    for event_id in state["selected_path_event_ids"]:
        event = events_by_id[event_id]
        if event["event_type"] != "turn_snapshot_created":
            continue
        reference = event["references"][0]
        document = validate_snapshot_document(
            root, reference["ref"], reference["sha256"], run_id, event["turn_id"],
        )
        if document["parent_turn_id"] != parent_turn_id:
            raise RunEventError(
                "turn snapshot parent_turn_id does not match selected-branch snapshot ancestry"
            )
        snapshots.append((event, document))
        parent_turn_id = document["turn_id"]
    return snapshots


def ensure_snapshot_capacity(selected_events):
    count = sum(
        event.get("event_type") == "turn_snapshot_created" for event in selected_events
    )
    if count >= MAX_CONTEXT_MANIFESTS:
        raise RunEventError(
            "selected branch already has %d turn snapshots; start a child run before another turn"
            % MAX_CONTEXT_MANIFESTS
        )
    return count


def validate_audit_reference(root, reference):
    if (
            reference["validation_status"] != "valid"
            or reference["validator"] != "validate-audit-artifact"):
        raise RunEventError(
            "memory/audits artifacts require validation_status=valid and validator=validate-audit-artifact"
        )
    _path, raw, metadata = _stable_project_read(
        root, reference["ref"], MAX_DOCUMENT_BYTES, "audit artifact",
    )
    if hashlib.sha256(raw).hexdigest() != reference["sha256"]:
        raise RunEventError("referenced artifact hash mismatch: %s" % reference["ref"])
    validator = Path(__file__).with_name("validate-audit-artifact.py")
    if not validator.is_file():
        raise RunEventError("audit artifact validator is unavailable")
    try:
        result = subprocess.run(
            [sys.executable, str(validator), "-",
             "--relative-path", reference["ref"]],
            cwd=root, input=raw, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            check=False, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RunEventError("audit artifact validation could not run: %s" % exc) from exc
    if result.returncode:
        detail = " ".join(result.stdout.decode("utf-8", errors="replace").splitlines()[-3:])[:500]
        raise RunEventError("audit artifact validation failed: %s" % (detail or "invalid artifact"))
    return metadata.st_size


def validate_save_point_artifact_references(
        root, artifacts, events=None, parent_event_id=None,
        control_session=None):
    """Revalidate save-point artifacts and, when available, their ancestry.

    ``artifact_validated`` is metadata-only evidence.  A checkpoint may claim
    ``valid`` only when the exact ref/hash/validator tuple appears on its
    selected ancestry.  Registered control artifacts additionally undergo live
    content validation on every checkpoint and replay.
    """
    selected_events = None
    if events is not None:
        selected_events = event_ancestry(events, parent_event_id)
    session = control_session or _control_validation_session()
    inspected_bytes = 0
    for reference in artifacts:
        if reference["ref"].endswith(("/events.ndjson", "/session.json")):
            raise RunEventError(
                "save point artifacts cannot reference mutable runtime files"
            )
        if reference["ref"].startswith("memory/audits/"):
            reference_bytes = validate_audit_reference(root, reference)
        elif (
                reference["validation_status"] == "valid"
                and reference["validator"] == CONTROL_ARTIFACT_VALIDATOR):
            reference_bytes = validate_control_artifact_reference(
                root, reference["ref"], reference["sha256"], session,
            )
        else:
            _path, reference_bytes = validate_non_control_artifact_reference(
                root, reference["ref"], reference["sha256"],
            )
        inspected_bytes += reference_bytes
        if inspected_bytes > MAX_REFERENCE_INSPECTION_BYTES:
            raise RunEventError(
                "save point artifact references exceed %d inspected bytes"
                % MAX_REFERENCE_INSPECTION_BYTES
            )
        if (
                selected_events is not None
                and not reference["ref"].startswith("memory/audits/")
                and reference["validation_status"] == "valid"):
            matches = [
                event for event in selected_events
                if (
                    event["event_type"] == "artifact_validated"
                    and event["references"][0]["ref"] == reference["ref"]
                    and event["references"][0]["sha256"] == reference["sha256"]
                    and event["dimensions"].get("validator") == reference["validator"]
                )
            ]
            if not matches:
                raise RunEventError(
                    "validated artifact lacks a matching ancestor artifact_validated event on selected ancestry"
                )
    return inspected_bytes


def validate_selected_save_point_replay(root, run_id, events, state):
    """Live-verify the selected save point and its pre-save artifact ancestry."""
    if state["last_save_point_ref"] is None:
        return None
    by_id = {event["event_id"]: event for event in events}
    selected = [by_id[event_id] for event_id in state["selected_path_event_ids"]]
    matching = [
        event for event in selected
        if (
            event["event_type"] == "save_point_created"
            and event["references"][0]["ref"] == state["last_save_point_ref"]
            and event["references"][0]["sha256"] == state["last_save_point_sha256"]
        )
    ]
    if len(matching) != 1:
        raise RunEventError(
            "selected save point lacks one exact selected-branch creation event"
        )
    return validate_save_point_document(
        root, state["last_save_point_ref"], state["last_save_point_sha256"],
        run_id, events, matching[0]["parent_event_id"],
    )


def existing_artifact_result(root, existing, proposed, projection, expected_kind):
    references = existing.get("references")
    if (
            not isinstance(references, list) or len(references) != 1
            or references[0].get("kind") != expected_kind
            or not isinstance(references[0].get("sha256"), str)):
        raise RunEventError("reserved idempotency key is occupied by an incompatible event")
    reference = references[0]
    path, stored, metadata = verified_json_reference(
        root, reference["ref"], reference["sha256"], "existing typed runtime artifact",
    )
    if statmod.S_IMODE(metadata.st_mode) != 0o600:
        raise RunEventError("existing typed runtime artifact must use private file mode 0600")
    ensure_ignored(root, [path])
    if canonical_json(stored) != canonical_json(proposed):
        raise RunEventError("idempotency key was already used with different artifact content")
    if expected_kind == "save-point":
        normalized_save_point = validate_save_point(stored)
        validate_save_point_artifact_references(
            root, normalized_save_point["artifacts"],
        )
    return {
        "deduplicated": True,
        "event": existing,
        "projection": projection,
        "artifact": {"ref": str(path.relative_to(root)), "sha256": reference["sha256"]},
    }


def _write_snapshot_under_coordinator(root, run_id, value):
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
        ensure_event_capacity(events, "turn_snapshot_created")
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("snapshot requires an active run")
        if state["route_skill"] is None:
            raise RunEventError("snapshot requires an ancestor typed route_selected event")
        events_by_id = {event["event_id"]: event for event in events}
        selected_events = [events_by_id[event_id] for event_id in state["selected_path_event_ids"]]
        ensure_snapshot_capacity(selected_events)
        turn_lifecycle = [
            event["event_type"] for event in selected_events
            if event["turn_id"] == normalized["turn_id"]
            and event["event_type"] in {"turn_started", "turn_finished"}
        ]
        if turn_lifecycle and turn_lifecycle[-1] != "turn_started":
            raise RunEventError("snapshot cannot follow a closed turn on the selected branch")
        ancestor_turns = [
            event["turn_id"] for event in selected_events
            if event["event_type"] == "turn_snapshot_created"
            and event["turn_id"] != normalized["turn_id"]
        ]
        expected_parent_turn = ancestor_turns[-1] if ancestor_turns else None
        if normalized["parent_turn_id"] != expected_parent_turn:
            raise RunEventError(
                "turn snapshot parent_turn_id must match the selected-branch parent turn"
            )
        _context_path, context_document, context_metadata = validate_context_document(
            root_path, normalized["context_manifest"]["ref"],
            normalized["context_manifest"]["sha256"],
            normalized["context_manifest"]["context_signature"],
            run_id, normalized["turn_id"], verify_sources=True,
        )
        validate_snapshot_context_binding(normalized, context_document, state)
        if "prompt_contract_ref" in normalized["skill"]:
            resolve_project_reference(
                root_path, normalized["skill"]["prompt_contract_ref"],
                normalized["skill"]["prompt_contract_sha256"],
                max_bytes=MAX_DOCUMENT_BYTES,
            )
        if context_metadata.st_size != normalized["context_manifest"]["bytes"]:
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


def write_snapshot(root, run_id, value):
    """Install a typed snapshot and its event under run coordination."""
    normalized = validate_snapshot(value)
    if normalized["run_id"] != run_id:
        raise RunEventError("snapshot run_id does not match command run_id")
    with locked_run_coordinator(root, run_id):
        return _write_snapshot_under_coordinator(root, run_id, normalized)


def _write_save_point_under_coordinator(root, run_id, value):
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
        ensure_event_capacity(events, "save_point_created")
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("save point requires an active run")
        if normalized["last_event_id"] != state["head_event_id"]:
            raise RunEventError("save point last_event_id must equal the verified stream head")
        if normalized["last_event_offset"] != state["last_offset"] or normalized["last_event_hash"] != state["last_event_hash"]:
            raise RunEventError("save point offset/hash must equal the verified stream head")
        if state["open_tool_refs"]:
            raise RunEventError("save point cannot be created with unfinished tool calls")
        if state["route_skill"] is None:
            raise RunEventError("save point requires an ancestor typed route_selected event")
        if (
                normalized["turn_snapshot"]["ref"] != state["last_turn_snapshot_ref"]
                or normalized["turn_snapshot"]["sha256"] != state["last_turn_snapshot_sha256"]):
            raise RunEventError("save point must reference the latest turn snapshot on the selected branch")
        snapshot_document = validate_snapshot_document(
            root_path, normalized["turn_snapshot"]["ref"],
            normalized["turn_snapshot"]["sha256"], run_id, normalized["turn_id"],
        )
        _context_path, context_document, _context_metadata = validate_context_document(
            root_path, normalized["context_manifest"]["ref"],
            normalized["context_manifest"]["sha256"],
            normalized["context_manifest"]["context_signature"],
            run_id, normalized["turn_id"], verify_sources=True,
        )
        if (
                snapshot_document["context_manifest"]["sha256"] != normalized["context_manifest"]["sha256"]
                or snapshot_document["context_manifest"]["context_signature"]
                != normalized["context_manifest"]["context_signature"]):
            raise RunEventError("save point context does not match its turn snapshot")
        validate_snapshot_context_binding(snapshot_document, context_document, state)
        if normalized["registry_offsets"] != context_document["registry_offsets"]:
            raise RunEventError("save point registry offsets do not match its context manifest")
        if normalized["visited_skills"] != state["route_chain"]:
            raise RunEventError(
                "save point visited_skills must exactly match the selected typed route chain"
            )
        if normalized["chain_depth"] != state["automatic_handoff_depth"]:
            raise RunEventError(
                "save point chain_depth must equal the derived automatic-handoff depth"
            )
        validate_save_point_artifact_references(
            root_path, normalized["artifacts"], events, normalized["last_event_id"],
        )
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


def write_save_point(root, run_id, value):
    """Install a typed save point and its event under run coordination."""
    normalized = validate_save_point(value)
    if normalized["run_id"] != run_id:
        raise RunEventError("save point run_id does not match command run_id")
    with locked_run_coordinator(root, run_id):
        return _write_save_point_under_coordinator(root, run_id, normalized)


def _loop_closure_failure_code(exc):
    if isinstance(exc, TimeoutError):
        return "validation-timeout"
    message = str(exc).lower()
    if "does not exist" in message or "no such file" in message:
        return "missing-step"
    if "hash mismatch" in message:
        return "hash-mismatch"
    if "budget" in message or "limit" in message:
        return "budget-exhausted"
    if any(token in message for token in (
            "event coverage", "event ancestry", "event does not", "event mismatch",
            "run parent", "selected branch")):
        return "event-mismatch"
    if isinstance(exc, RunEventError):
        return "invalid-chain"
    return "validator-error"


def _selected_loop_prefix(
        root, run_id, loop_id, loop_events, events, selected_ids, deadline,
        budget):
    wrappers = []
    for index, event in enumerate(loop_events, 1):
        if time.monotonic() >= deadline:
            raise TimeoutError("audit loop validation deadline exceeded")
        budget["steps"] += 1
        if budget["steps"] > MAX_LOOP_CLOSURE_STEPS:
            raise RunEventError("audit loop closure step budget exceeded")
        reference = event["references"][0]
        path, document, metadata = verified_json_reference(
            root, reference["ref"], reference["sha256"],
            "selected audit loop step",
        )
        budget["bytes"] += metadata.st_size
        if budget["bytes"] > MAX_LOOP_CLOSURE_BYTES:
            raise RunEventError("audit loop closure byte budget exceeded")
        if statmod.S_IMODE(metadata.st_mode) != 0o600:
            raise RunEventError("selected audit loop step must use private file mode 0600")
        ensure_ignored(normalized_root(root), [path])
        normalized = _validate_loop_step_document(
            run_id, loop_id, reference["ref"], document,
        )
        if normalized["sequence"] != index:
            raise RunEventError("selected audit loop sequence is not contiguous")
        wrapper = {
            "document": normalized,
            "ref": reference["ref"],
            "sha256": reference["sha256"],
        }
        if wrappers:
            prior = wrappers[-1]
            if (
                    normalized["previous_step_ref"] != prior["ref"]
                    or normalized["previous_step_sha256"] != prior["sha256"]
                    or normalized["expected_previous_sha256"] != prior["sha256"]
                    or normalized["from_state"] != prior["document"]["state"]):
                raise RunEventError("selected audit loop step chain is invalid")
        elif (
                normalized["previous_step_ref"] is not None
                or normalized["previous_step_sha256"] != ZERO_HASH
                or normalized["expected_previous_sha256"] != ZERO_HASH):
            raise RunEventError("selected audit loop start does not begin at zero hash")
        wrappers.append(wrapper)
    coverage = _verify_loop_event_coverage_in_events(
        run_id, loop_id, wrappers, events,
        _event_scope_ids=selected_ids,
    )
    expected_ids = [event["event_id"] for event in loop_events]
    if coverage["event_ids"] != expected_ids:
        raise RunEventError("selected audit loop event mismatch")
    if time.monotonic() >= deadline:
        raise TimeoutError("audit loop validation deadline exceeded")
    return wrappers[-1]["document"]["state"]


def verify_run_audit_loops(
        root, run_id, require_terminal, branch_head_event_id=None,
        allow_unresolved=False):
    """Derive bounded loop closure from exactly one selected event ancestry."""
    root_path = normalized_root(root)
    events = load_events(root_path, run_id)
    if not events:
        raise RunEventError("audit loop validation requires a non-empty run")
    selected_head = branch_head_event_id or events[-1]["event_id"]
    validate_uuid(selected_head, "selected loop branch head")
    if selected_head not in {event["event_id"] for event in events}:
        raise RunEventError("selected loop branch head does not exist")
    selected_events = event_ancestry(events, selected_head)
    selected_ids = {event["event_id"] for event in selected_events}
    groups = {}
    for event in selected_events:
        if event["event_type"] != "loop_state_changed":
            continue
        groups.setdefault(event["subject"]["ref"], []).append(event)
    if len(groups) > MAX_AUDIT_LOOPS:
        raise RunEventError(
            "selected branch exceeds the %d audit-loop limit" % MAX_AUDIT_LOOPS
        )

    deadline = time.monotonic() + MAX_LOOP_VALIDATION_SECONDS
    budget = {"steps": 0, "bytes": 0}
    items = []
    unresolved_count = 0
    for loop_id, loop_events in groups.items():
        last_event = loop_events[-1]
        expected = last_event["references"][0]
        item = {
            "loop_id": loop_id,
            "last_loop_event_id": last_event["event_id"],
            "expected_step_ref": expected["ref"],
            "expected_step_sha256": expected["sha256"],
            "validation_status": "valid",
            "failure_code": None,
        }
        try:
            if time.monotonic() >= deadline:
                raise TimeoutError("audit loop validation deadline exceeded")
            head_state = _selected_loop_prefix(
                root_path, run_id, loop_id, loop_events, events,
                selected_ids, deadline, budget,
            )
            if require_terminal and head_state not in LOOP_TERMINAL_STATES:
                if not allow_unresolved:
                    raise RunEventError(
                        "terminal run envelope requires selected audit loops to be terminal"
                    )
                item["validation_status"] = "unresolved"
                item["failure_code"] = "nonterminal"
        except Exception as exc:
            if not allow_unresolved:
                raise RunEventError(
                    "selected audit loop validation failed for %s: %s"
                    % (loop_id, exc)
                ) from exc
            item["validation_status"] = "unresolved"
            item["failure_code"] = _loop_closure_failure_code(exc)
        if item["validation_status"] == "unresolved":
            unresolved_count += 1
        items.append(item)
    status = "none" if not items else ("unresolved" if unresolved_count else "verified")
    return validate_loop_closure({
        "scope": "selected-ancestry",
        "selected_head_event_id": selected_head,
        "status": status,
        "loops": items,
    })


def _verify_envelope_artifact_references(root, references):
    inspected_bytes = 0
    for reference in references:
        if reference["ref"].endswith(("/events.ndjson", "/session.json")):
            raise RunEventError("run envelope artifacts cannot reference mutable runtime files")
        _path, reference_bytes = resolve_project_reference(
            root, reference["ref"], reference["sha256"],
        )
        inspected_bytes += reference_bytes
        if inspected_bytes > MAX_REFERENCE_INSPECTION_BYTES:
            raise RunEventError(
                "run envelope artifact references exceed %d inspected bytes"
                % MAX_REFERENCE_INSPECTION_BYTES
            )


def _install_envelope_locked(
        root, run_id, run_dir, projection, handle, events, normalized,
        event_key, intended_event_type):
    target_dir = ensure_child_directories(root, run_dir, ["envelopes"])
    target = target_dir / (normalized["last_event_id"] + ".json")
    digest = write_immutable_json(root, target, normalized)
    reference = str(target.relative_to(root))
    status = {
        "run_finished": "succeeded", "run_failed": "failed",
        "run_aborted": "cancelled", "run_waiting": "waiting",
    }[intended_event_type]
    request = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "idempotency_key": event_key,
        "event_type": intended_event_type,
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


def _finish_run_under_coordinator(root, run_id, value):
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
        intended_event_type = {
            "succeeded": "run_finished", "failed": "run_failed",
            "aborted": "run_aborted",
        }.get(normalized["status"], "run_waiting")
        ensure_event_capacity(events, intended_event_type)
        if not events or state["status"] not in {"active", "waiting"}:
            raise RunEventError("finish requires an active run")
        if normalized["last_event_id"] != state["head_event_id"]:
            raise RunEventError("run envelope last_event_id must equal the verified stream head")
        if normalized["last_event_offset"] != state["last_offset"] or normalized["last_event_hash"] != state["last_event_hash"]:
            raise RunEventError("run envelope offset/hash must equal the verified stream head")
        if normalized["started_at"] != state["started_at"]:
            raise RunEventError("run envelope started_at must match run_started")
        degraded_without_context = (
            normalized["status"] in {"failed", "aborted"}
            and not normalized["context_manifests"]
        )
        if degraded_without_context:
            _verify_envelope_artifact_references(
                root_path, normalized["artifacts"],
            )
            return _install_envelope_locked(
                root_path, run_id, run_dir, projection, handle, events,
                normalized, event_key, intended_event_type,
            )
        if state["route_skill"] is None:
            raise RunEventError("run envelope requires an ancestor typed route_selected event")
        if normalized["status"] == "succeeded" and state["open_tool_refs"]:
            raise RunEventError("successful run cannot finish with unfinished tool calls")
        context_documents = []
        for context_reference in normalized["context_manifests"]:
            _context_path, context_document, _context_metadata = validate_context_document(
                root_path, context_reference["ref"], context_reference["sha256"],
                context_reference["context_signature"], run_id,
            )
            context_documents.append((context_reference, context_document))
        context_by_identity = {
            (reference["ref"], reference["sha256"], reference["context_signature"]): document
            for reference, document in context_documents
        }
        observed_contexts = []
        branch_snapshots = selected_branch_snapshots(root_path, run_id, events, state)
        for snapshot_event, snapshot_document in branch_snapshots:
            snapshot_context = snapshot_document["context_manifest"]
            identity = (
                snapshot_context["ref"], snapshot_context["sha256"],
                snapshot_context["context_signature"],
            )
            observed_contexts.append({
                "ref": identity[0], "sha256": identity[1],
                "context_signature": identity[2],
            })
            if identity in context_by_identity:
                route_at_snapshot = selected_route_state(
                    events, snapshot_event["parent_event_id"],
                )
                if route_at_snapshot is None:
                    raise RunEventError(
                        "turn snapshot lacks an ancestor typed route_selected event"
                    )
                route_view = {
                    "route_skill": route_at_snapshot["skill"],
                    "route_command": route_at_snapshot["command"],
                    "route_reason_code": route_at_snapshot["reason_code"],
                }
                validate_snapshot_context_binding(
                    snapshot_document, context_by_identity[identity], route_view,
                )
        if not observed_contexts:
            raise RunEventError("run envelope requires an ancestor turn snapshot")
        if normalized["context_manifests"] != observed_contexts:
            raise RunEventError(
                "run envelope context manifests must match selected-branch turn snapshots"
            )
        terminal_context = context_documents[-1][1]
        terminal_route = terminal_context["route"]
        if {
                "target_skill": state["route_skill"],
                "command": state["route_command"],
                "reason_code": state["route_reason_code"],
        } != {
                "target_skill": terminal_route["target_skill"],
                "command": terminal_route["command"],
                "reason_code": terminal_route["reason_code"],
        }:
            raise RunEventError(
                "run envelope terminal context route does not match the latest typed route event"
            )
        if normalized["route"] != {
                "skill": terminal_route["target_skill"],
                "version": terminal_route["skill_version"],
                "reason_code": terminal_route["reason_code"],
        }:
            raise RunEventError("run envelope route does not match its terminal context manifest")
        if normalized["registry_offsets"] != terminal_context["registry_offsets"]:
            raise RunEventError(
                "run envelope registry offsets do not match its terminal context manifest"
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
            events_by_id = {event["event_id"]: event for event in events}
            selected_events = [events_by_id[event_id] for event_id in state["selected_path_event_ids"]]
            matching_save_events = [
                event for event in selected_events
                if event["event_type"] == "save_point_created"
                and event["references"][0]["ref"] == normalized["save_point"]["ref"]
                and event["references"][0]["sha256"] == normalized["save_point"]["sha256"]
            ]
            if len(matching_save_events) != 1:
                raise RunEventError("run envelope save point lacks one selected-branch event")
            save_parent = events_by_id[matching_save_events[0]["parent_event_id"]]
            if (
                    save_document["last_event_id"] != save_parent["event_id"]
                    or save_document["last_event_offset"] != save_parent["offset"]
                    or save_document["last_event_hash"] != save_parent["event_hash"]):
                raise RunEventError("run envelope save point head does not match its creation event")
            matching_contexts = [
                document for reference, document in context_documents
                if reference == save_document["context_manifest"]
            ]
            if not matching_contexts:
                raise RunEventError("run envelope omits the save point context manifest")
            save_context = matching_contexts[0]
            if save_document["registry_offsets"] != save_context["registry_offsets"]:
                raise RunEventError(
                    "run envelope save point offsets do not match its context manifest"
                )
            save_snapshot = validate_snapshot_document(
                root_path, save_document["turn_snapshot"]["ref"],
                save_document["turn_snapshot"]["sha256"], run_id,
                save_document["turn_id"],
            )
            if any(
                    save_snapshot["context_manifest"][field]
                    != save_document["context_manifest"][field]
                    for field in ("ref", "sha256", "context_signature")):
                raise RunEventError("run envelope save point context does not match its snapshot")
            validate_snapshot_context_binding(save_snapshot, save_context)
        _verify_envelope_artifact_references(root_path, references_to_verify)
        return _install_envelope_locked(
            root_path, run_id, run_dir, projection, handle, events,
            normalized, event_key, intended_event_type,
        )


def finish_run(root, run_id, value):
    """Install a waiting/terminal envelope under the per-run coordinator lock."""
    candidate = dict(value) if isinstance(value, dict) else value
    if isinstance(candidate, dict):
        candidate.pop("loop_closure", None)
    normalized = validate_envelope(candidate)
    if normalized["run_id"] != run_id:
        raise RunEventError("run envelope run_id does not match command run_id")
    with locked_run_coordinator(root, run_id):
        terminal_status = normalized["status"] in {"succeeded", "failed", "aborted"}
        normalized["loop_closure"] = verify_run_audit_loops(
            root, run_id,
            require_terminal=terminal_status,
            branch_head_event_id=normalized["last_event_id"],
            allow_unresolved=normalized["status"] in {"failed", "aborted"},
        )
        return _finish_run_under_coordinator(root, run_id, normalized)


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
    validate_artifact_validation_events(
        root, events, state["selected_path_event_ids"],
    )
    validate_selected_save_point_replay(root, run_id, events, state)
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
        "route_skill": state["route_skill"],
        "route_command": state["route_command"],
        "route_reason_code": state["route_reason_code"],
        "route_transition": state["route_transition"],
        "route_chain": state["route_chain"],
        "automatic_handoff_depth": state["automatic_handoff_depth"],
        "loop_states": state["loop_states"],
        "note": "Untrusted operational evidence; re-verify referenced state before acting.",
    }
    encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        summary["leaf_event_ids"] = summary["leaf_event_ids"][-4:]
        summary["turn_ids"] = summary["turn_ids"][-8:]
        summary["open_tool_refs"] = summary["open_tool_refs"][-8:]
        summary["loop_states"] = summary["loop_states"][-2:]
        summary["truncated"] = True
        encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        for key in ("leaf_event_ids", "turn_ids", "open_tool_refs", "loop_states"):
            summary[key] = []
        encoded = (canonical_json(summary) + "\n").encode("utf-8")
    if len(encoded) > max_bytes:
        summary = {
            "schema_version": SCHEMA_VERSION,
            "authoritative": False,
            "run_id": run_id,
            "status": state["status"],
            "last_offset": state["last_offset"],
            "last_event_id": state["last_event_id"],
            "last_event_hash": state["last_event_hash"],
            "truncated": True,
            "note": "Untrusted operational evidence; re-verify before acting.",
        }
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
    loop_step = sub.add_parser(
        "loop-step", help="verify an already event-bound immutable audit-loop head"
    )
    loop_step.add_argument("run_id")
    loop_step.add_argument("loop_id")
    loop_step.add_argument("reference")
    loop_step.add_argument("sha256")
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
        validate_artifact_validation_events(args.root, events)
        result = {"valid": True, "events": len(events), "projection": project_events(args.run_id, events)}
    elif args.command == "project":
        result = rebuild_projection(args.root, args.run_id)
    elif args.command == "validate":
        result = VALIDATORS[args.kind](read_json(args.document, args.kind))
    elif args.command == "snapshot":
        result = write_snapshot(args.root, args.run_id, read_json(args.document, "turn snapshot"))
    elif args.command == "save-point":
        result = write_save_point(args.root, args.run_id, read_json(args.document, "save point"))
    elif args.command == "loop-step":
        result = record_loop_step(
            args.root, args.run_id, args.loop_id, args.reference, args.sha256,
        )
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
