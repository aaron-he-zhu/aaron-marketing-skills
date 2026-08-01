#!/usr/bin/env python3
"""Bounded, event-sourced execution runtime for named workflow graphs.

This module is intentionally non-authoritative.  It stores an operational plan,
an append-only hash-chained event stream, and a rebuildable state projection
under an existing ``memory/runs/<run-id>/`` directory.  Every plan is anchored
to an event from ``scripts/run-events.py``; actions cite that same run stream;
memory output is proposal-only and must still be accepted by its owning
registry.

Python 3 stdlib only.  Public API: :func:`plan`, :func:`advance`,
:func:`verify`, and :func:`main`.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import contextlib
import copy
import datetime as dt
import hashlib
import hmac
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - mutation fails closed without POSIX locks
    fcntl = None


ROOT = Path(__file__).resolve().parents[1]
GRAPH_REL = Path("references/workflow-graph.json")
SOURCE_REL = Path("references/workflow-graph.source.json")
CATALOG_REL = Path("references/system-catalog.json")
PLAN_SCHEMA = "references/workflow-loop-plan.schema.json"
STATE_SCHEMA = "references/workflow-loop-state.schema.json"
SCHEMA_VERSION = "1.0"
AUTHORITY = "non-authoritative-operational-planning"
ZERO_HASH = "0" * 64
NAMESPACE = uuid.UUID("d26b1620-f996-4a14-b14d-937ca3d37f0a")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
EVENT_TYPES = {
    "planned",
    "action-completed",
    "action-failed",
    "verification-recorded",
    "decision-recorded",
    "memory-proposal-recorded",
    "terminal-recorded",
}
TERMINAL_OUTCOMES = {
    "converged", "waiting", "exhausted", "escalated", "failed", "aborted",
}
REFERENCE_KINDS = {"run-event", "artifact", "evaluation", "registry-projection"}
REGISTRIES = {"entities", "creators", "claims", "consent", "launches", "channels", "narrative"}
QUALIFYING_ACTION_EVENT_TYPES = {"turn_finished", "artifact_validated", "save_point_created"}
MAX_JSON_BYTES = 2_000_000
MAX_EVENT_BYTES = 64_000
MAX_ARTIFACT_BYTES = 32_000_000
MAX_TRUST_ANCHOR_BYTES = 32_000
MAX_APPROVAL_BYTES = 64_000
APPROVAL_SCHEMA = "references/workflow-execution-approval.schema.json"
TRUST_ANCHOR_PATH_ENV = "AARON_WORKFLOW_APPROVAL_TRUST_ANCHOR"
TRUST_ANCHOR_SHA_ENV = "AARON_WORKFLOW_APPROVAL_TRUST_ANCHOR_SHA256"
RSA_SHA256_DIGEST_INFO_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")


class WorkflowLoopError(ValueError):
    """The workflow loop request or persisted state violates its contract."""


class EventCommittedError(WorkflowLoopError):
    """The event is durable but its rebuildable projection was not installed."""


def canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise WorkflowLoopError("value must contain finite JSON data: %s" % exc) from exc


def pretty_json(value):
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False,
    ) + "\n"


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value):
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def strict_json_loads(raw, label="JSON"):
    def unique_pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise WorkflowLoopError("%s contains duplicate key %r" % (label, key))
            result[key] = value
        return result

    try:
        return json.loads(
            raw, object_pairs_hook=unique_pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(
                WorkflowLoopError("%s contains non-finite number %s" % (label, value))
            ),
        )
    except WorkflowLoopError:
        raise
    except (TypeError, UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise WorkflowLoopError("cannot parse %s as strict JSON: %s" % (label, exc)) from exc


def read_json(path, label="document"):
    path = Path(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise WorkflowLoopError("cannot read %s %s: %s" % (label, path, exc)) from exc
    if len(raw) > MAX_JSON_BYTES:
        raise WorkflowLoopError("%s exceeds %d bytes" % (label, MAX_JSON_BYTES))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise WorkflowLoopError("%s must be UTF-8" % label) from exc
    return strict_json_loads(text, label), raw


def _exact_keys(value, required, optional, label):
    if not isinstance(value, dict):
        raise WorkflowLoopError("%s must be an object" % label)
    missing = required - set(value)
    unknown = set(value) - required - optional
    if missing or unknown:
        raise WorkflowLoopError(
            "%s fields are invalid (missing=%s unknown=%s)"
            % (label, sorted(missing), sorted(unknown))
        )


def _safe_id(value, label, slug=False):
    pattern = SAFE_SLUG_RE if slug else SAFE_ID_RE
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise WorkflowLoopError("%s is not a safe identifier" % label)
    return value


def _uuid(value, label):
    try:
        parsed = uuid.UUID(value)
    except (AttributeError, TypeError, ValueError) as exc:
        raise WorkflowLoopError("%s must be a canonical UUID" % label) from exc
    if str(parsed) != value:
        raise WorkflowLoopError("%s must be a lowercase canonical UUID" % label)
    return value


def _digest(value, label):
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise WorkflowLoopError("%s must be a lowercase SHA-256 digest" % label)
    return value


def _timestamp(value, label):
    if not isinstance(value, str) or not RFC3339_RE.fullmatch(value):
        raise WorkflowLoopError("%s must be RFC3339 with an explicit timezone" % label)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))
    except ValueError as exc:
        raise WorkflowLoopError("%s is not a valid timestamp" % label) from exc
    if parsed.tzinfo is None:
        raise WorkflowLoopError("%s must have an explicit timezone" % label)
    return parsed.astimezone(dt.timezone.utc)


def _format_timestamp(value):
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _runtime_now():
    """Return the runtime-assigned UTC persistence time for a workflow event."""
    return _format_timestamp(dt.datetime.now(dt.timezone.utc))


def _relative_file(root, reference):
    if not isinstance(reference, str) or not reference or "\x00" in reference:
        raise WorkflowLoopError("artifact reference must be a non-empty relative path")
    relative = Path(reference)
    if relative.is_absolute() or ".." in relative.parts:
        raise WorkflowLoopError("artifact reference must stay inside the repository")
    root = Path(root).resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise WorkflowLoopError("artifact reference escapes the repository") from exc
    try:
        metadata = resolved.stat()
    except OSError as exc:
        raise WorkflowLoopError("referenced artifact is unavailable: %s" % reference) from exc
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > MAX_ARTIFACT_BYTES:
        raise WorkflowLoopError("referenced artifact must be a bounded regular file")
    return resolved


_RUN_EVENTS_MODULE = None
_AUDIT_ARTIFACT_MODULE = None


def _run_events_module():
    global _RUN_EVENTS_MODULE
    if _RUN_EVENTS_MODULE is None:
        path = Path(__file__).with_name("run-events.py")
        spec = importlib.util.spec_from_file_location("workflow_loop_run_events", path)
        if spec is None or spec.loader is None:
            raise WorkflowLoopError("cannot load scripts/run-events.py")
        module = importlib.util.module_from_spec(spec)
        source = path.read_bytes()
        exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
        _RUN_EVENTS_MODULE = module
    return _RUN_EVENTS_MODULE


def _audit_artifact_module():
    """Load the canonical auditor-artifact validator used by gate releases."""
    global _AUDIT_ARTIFACT_MODULE
    if _AUDIT_ARTIFACT_MODULE is None:
        path = Path(__file__).with_name("validate-audit-artifact.py")
        spec = importlib.util.spec_from_file_location(
            "workflow_loop_audit_artifact", path,
        )
        if spec is None or spec.loader is None:
            raise WorkflowLoopError("cannot load scripts/validate-audit-artifact.py")
        module = importlib.util.module_from_spec(spec)
        source = path.read_bytes()
        exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
        _AUDIT_ARTIFACT_MODULE = module
    return _AUDIT_ARTIFACT_MODULE


def _load_run_events(root, run_id):
    try:
        return _run_events_module().load_events(Path(root), run_id)
    except Exception as exc:
        raise WorkflowLoopError(
            "workflow planning requires an existing valid run-events stream: %s" % exc
        ) from exc


def _reference(value, label):
    _exact_keys(value, {"kind", "ref", "sha256"}, set(), label)
    if value["kind"] not in REFERENCE_KINDS:
        raise WorkflowLoopError("%s has unsupported kind" % label)
    if not isinstance(value["ref"], str) or not value["ref"]:
        raise WorkflowLoopError("%s ref must be non-empty" % label)
    _digest(value["sha256"], label + " sha256")
    return copy.deepcopy(value)


def _references(value, label, minimum=1):
    if not isinstance(value, list) or len(value) < minimum:
        raise WorkflowLoopError("%s must contain at least %d reference(s)" % (label, minimum))
    result = [_reference(item, "%s[%d]" % (label, index)) for index, item in enumerate(value)]
    identities = {(item["kind"], item["ref"], item["sha256"]) for item in result}
    if len(identities) != len(result):
        raise WorkflowLoopError("%s contains duplicate references" % label)
    return result


def _verify_reference(root, run_id, reference, run_events=None):
    if reference["kind"] == "run-event":
        _uuid(reference["ref"], "run-event ref")
        events = run_events if run_events is not None else _load_run_events(root, run_id)
        matched = [event for event in events if event["event_id"] == reference["ref"]]
        if len(matched) != 1 or matched[0]["event_hash"] != reference["sha256"]:
            raise WorkflowLoopError("run-event reference is missing or hash-mismatched")
        return
    path = _relative_file(root, reference["ref"])
    if sha256_bytes(path.read_bytes()) != reference["sha256"]:
        raise WorkflowLoopError("artifact reference hash mismatch: %s" % reference["ref"])


def _verify_references(root, run_id, references, require_run_event=False):
    run_events = _load_run_events(root, run_id)
    if require_run_event and not any(item["kind"] == "run-event" for item in references):
        raise WorkflowLoopError("action evidence must include a run-event reference")
    for reference in references:
        _verify_reference(root, run_id, reference, run_events)


def _selected_run_event_ids(run_events):
    if not run_events:
        return set()
    module = _run_events_module()
    return {
        event["event_id"]
        for event in module.event_ancestry(run_events, run_events[-1]["event_id"])
    }


def _selected_run_head(run_events):
    if not run_events:
        raise WorkflowLoopError("run-events stream has no current selected head")
    return run_events[-1]


def _run_event_cutoff(event):
    return {
        "kind": "run-event",
        "ref": event["event_id"],
        "sha256": event["event_hash"],
        "offset": event["offset"],
        "occurred_at": event["occurred_at"],
        "recorded_at": event["recorded_at"],
    }


def _evidence_cutoff(value, label="evidence_cutoff"):
    _exact_keys(
        value,
        {"kind", "ref", "sha256", "offset", "occurred_at", "recorded_at"},
        set(), label,
    )
    if value["kind"] != "run-event":
        raise WorkflowLoopError("%s must have kind run-event" % label)
    _uuid(value["ref"], label + " ref")
    _digest(value["sha256"], label + " sha256")
    if (
            not isinstance(value["offset"], int)
            or isinstance(value["offset"], bool)
            or value["offset"] < 1):
        raise WorkflowLoopError("%s offset must be a positive integer" % label)
    _timestamp(value["occurred_at"], label + " occurred_at")
    _timestamp(value["recorded_at"], label + " recorded_at")
    return copy.deepcopy(value)


def _plan_anchor_event(plan_value, run_events):
    anchor = plan_value["run_event_anchor"]
    matched = [event for event in run_events if event["event_id"] == anchor["ref"]]
    if len(matched) != 1 or matched[0]["event_hash"] != anchor["sha256"]:
        raise WorkflowLoopError("plan run-event anchor is missing or hash-mismatched")
    return matched[0]


def _validate_plan_anchor(plan_value, run_events, *, require_current_head=False):
    """Bind a plan to the selected head and reject temporal backdating.

    ``require_current_head`` is used only while creating a new plan.  A live
    run is expected to advance after planning, so replay/verification instead
    requires that the immutable anchor remain on the selected ancestry.
    """
    anchor = _plan_anchor_event(plan_value, run_events)
    selected = _selected_run_event_ids(run_events)
    if anchor["event_id"] not in selected:
        raise WorkflowLoopError("workflow plan anchor is outside the selected ancestry")
    if require_current_head and anchor["event_id"] != _selected_run_head(run_events)["event_id"]:
        raise WorkflowLoopError("run_event_anchor must equal the current selected run head")
    if _timestamp(plan_value["created_at"], "plan created_at") < _timestamp(
            anchor["occurred_at"], "anchor occurred_at"):
        raise WorkflowLoopError("plan created_at cannot precede anchor occurred_at")
    if "evidence_cutoff" in plan_value:
        cutoff = _evidence_cutoff(plan_value["evidence_cutoff"])
        if cutoff != _run_event_cutoff(anchor):
            raise WorkflowLoopError(
                "evidence_cutoff must equal the run head protected during plan persistence"
            )
    return anchor


def _is_fresh_post_plan_event(plan_value, event, anchor):
    cutoff_offset = plan_value.get("evidence_cutoff", {}).get(
        "offset", anchor["offset"],
    )
    cutoff_recorded_at = plan_value.get("evidence_cutoff", {}).get(
        "recorded_at", anchor["recorded_at"],
    )
    return (
        event["offset"] > cutoff_offset
        and _timestamp(event["recorded_at"], "evidence recorded_at")
            >= _timestamp(cutoff_recorded_at, "cutoff recorded_at")
    )


def _verify_run_event_artifacts(root, run_id, event):
    for reference in event.get("references", []):
        if reference.get("kind") in {"artifact", "evaluation", "registry-projection"}:
            _verify_reference(root, run_id, reference)


def _gate_release_edges(plan_value, node):
    return [
        edge for edge in plan_value["workflow"]["edge_snapshot"]
        if edge["from"] == node and edge["type"] == "gate" and edge["gate"] == node
    ]


def _workflow_requires_approval(workflow):
    return any(
        edge["type"] == "gate"
        and edge["gate"] == edge["from"]
        and "external-action-approval" in edge["permissions"]
        for edge in workflow["edge_snapshot"]
    )


def _approval_trust_snapshot(value, label="approval_trust"):
    if value is None:
        return None
    _exact_keys(
        value, {"key_id", "algorithm", "anchor_sha256"}, set(), label,
    )
    _safe_id(value["key_id"], label + " key_id")
    if value["algorithm"] != "RS256":
        raise WorkflowLoopError("%s algorithm must be RS256" % label)
    _digest(value["anchor_sha256"], label + " anchor_sha256")
    return copy.deepcopy(value)


def _strict_b64url_decode(value, label):
    if (
            not isinstance(value, str) or not value
            or "=" in value or not re.fullmatch(r"[A-Za-z0-9_-]+", value)):
        raise WorkflowLoopError("%s must be unpadded base64url" % label)
    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, binascii.Error) as exc:
        raise WorkflowLoopError("%s is invalid base64url" % label) from exc
    canonical = base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")
    if not hmac.compare_digest(canonical, value):
        raise WorkflowLoopError("%s must use canonical base64url encoding" % label)
    return decoded


def _load_approval_trust(root):
    """Load a host-pinned public trust anchor outside the repository."""
    supplied = os.environ.get(TRUST_ANCHOR_PATH_ENV)
    expected_digest = os.environ.get(TRUST_ANCHOR_SHA_ENV)
    if not supplied or not expected_digest:
        raise WorkflowLoopError(
            "external-action gate requires host-configured approval trust anchor "
            "path and SHA-256"
        )
    _digest(expected_digest, TRUST_ANCHOR_SHA_ENV)
    path = Path(supplied)
    if not path.is_absolute():
        raise WorkflowLoopError("approval trust anchor path must be absolute")
    try:
        metadata = os.lstat(path)
    except OSError as exc:
        raise WorkflowLoopError("approval trust anchor is unavailable: %s" % exc) from exc
    if (
            stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode)
            or metadata.st_nlink != 1 or metadata.st_size > MAX_TRUST_ANCHOR_BYTES):
        raise WorkflowLoopError(
            "approval trust anchor must be a bounded single-link regular file"
        )
    resolved = path.resolve()
    try:
        resolved.relative_to(Path(root).resolve())
    except ValueError:
        pass
    else:
        raise WorkflowLoopError("approval trust anchor must remain outside the repository")
    try:
        raw = resolved.read_bytes()
    except OSError as exc:
        raise WorkflowLoopError("cannot read approval trust anchor: %s" % exc) from exc
    if sha256_bytes(raw) != expected_digest:
        raise WorkflowLoopError("approval trust anchor does not match host-pinned SHA-256")
    try:
        document = strict_json_loads(raw.decode("utf-8"), "approval trust anchor")
    except UnicodeDecodeError as exc:
        raise WorkflowLoopError("approval trust anchor must be UTF-8") from exc
    _exact_keys(document, {
        "$schema", "schema_version", "key_id", "algorithm", "modulus_b64url",
        "exponent", "not_before", "not_after",
    }, set(), "approval trust anchor")
    if (
            document["$schema"] != "workflow-execution-approval-trust.schema.json"
            or document["schema_version"] != SCHEMA_VERSION
            or document["algorithm"] != "RS256"):
        raise WorkflowLoopError("approval trust anchor identity/algorithm is invalid")
    _safe_id(document["key_id"], "approval trust key_id")
    modulus_raw = _strict_b64url_decode(
        document["modulus_b64url"], "approval trust modulus_b64url",
    )
    modulus = int.from_bytes(modulus_raw, "big")
    if not 2048 <= modulus.bit_length() <= 4096 or modulus % 2 != 1:
        raise WorkflowLoopError("approval trust RSA modulus must be an odd 2048..4096-bit value")
    if document["exponent"] != 65537:
        raise WorkflowLoopError("approval trust RSA exponent must be 65537")
    not_before = _timestamp(document["not_before"], "approval trust not_before")
    not_after = _timestamp(document["not_after"], "approval trust not_after")
    if not_before >= not_after:
        raise WorkflowLoopError("approval trust validity window is invalid")
    document = {
        **document,
        "_modulus": modulus,
        "_modulus_bytes": len(modulus_raw),
        "_not_before": not_before,
        "_not_after": not_after,
    }
    snapshot = {
        "key_id": document["key_id"],
        "algorithm": "RS256",
        "anchor_sha256": expected_digest,
    }
    return document, snapshot


def _approval_trust_for_plan(root, plan_value):
    planned = _approval_trust_snapshot(plan_value.get("approval_trust"))
    if planned is None:
        raise WorkflowLoopError("gate plan has no pinned approval trust anchor")
    document, current = _load_approval_trust(root)
    if current != planned:
        raise WorkflowLoopError("approval trust anchor differs from the immutable plan")
    return document


def _gate_approval(value, label="gate_approval"):
    _exact_keys(value, {"kind", "ref", "sha256", "nonce"}, set(), label)
    if value["kind"] != "artifact":
        raise WorkflowLoopError("%s must reference an artifact" % label)
    reference = _reference(
        {key: value[key] for key in ("kind", "ref", "sha256")}, label,
    )
    _uuid(value["nonce"], label + " nonce")
    return {**reference, "nonce": value["nonce"]}


def _verify_rs256(document, trust):
    signature_raw = _strict_b64url_decode(
        document["signature"], "approval signature",
    )
    width = trust["_modulus_bytes"]
    if len(signature_raw) != width:
        raise WorkflowLoopError("approval signature width does not match trust anchor")
    signed = dict(document)
    signed.pop("signature")
    digest_info = RSA_SHA256_DIGEST_INFO_PREFIX + hashlib.sha256(
        canonical_json(signed).encode("utf-8")
    ).digest()
    padding_length = width - len(digest_info) - 3
    if padding_length < 8:
        raise WorkflowLoopError("approval trust key is too small for RS256")
    expected = b"\x00\x01" + b"\xff" * padding_length + b"\x00" + digest_info
    signature_number = int.from_bytes(signature_raw, "big")
    if signature_number >= trust["_modulus"]:
        raise WorkflowLoopError("approval signature is outside the RSA modulus")
    encoded = pow(
        signature_number, trust["exponent"], trust["_modulus"],
    ).to_bytes(width, "big")
    if not hmac.compare_digest(encoded, expected):
        raise WorkflowLoopError("approval signature verification failed")


def _validate_approval_artifact(
        root, plan_value, gate_approval, audit_reference, action,
        audit_event, approval_event, action_recorded_at):
    reference = {
        key: gate_approval[key] for key in ("kind", "ref", "sha256")
    }
    _verify_reference(root, plan_value["run_id"], reference)
    path = _relative_file(root, gate_approval["ref"])
    raw = path.read_bytes()
    if len(raw) > MAX_APPROVAL_BYTES:
        raise WorkflowLoopError("execution approval artifact exceeds its byte limit")
    # Validate the exact bytes parsed below.  The generic reference check above
    # is intentionally retained for the common evidence path, but cannot by
    # itself close a replace-between-read TOCTOU window.
    if sha256_bytes(raw) != gate_approval["sha256"]:
        raise WorkflowLoopError("execution approval artifact changed during validation")
    try:
        document = strict_json_loads(raw.decode("utf-8"), "execution approval")
    except UnicodeDecodeError as exc:
        raise WorkflowLoopError("execution approval artifact must be UTF-8") from exc
    _exact_keys(document, {
        "$schema", "schema_version", "approval_id", "key_id", "algorithm",
        "run_id", "loop_id", "action", "audit", "issued_at", "expires_at",
        "nonce", "signature",
    }, set(), "execution approval")
    if (
            document["$schema"] != APPROVAL_SCHEMA
            or document["schema_version"] != SCHEMA_VERSION
            or document["algorithm"] != "RS256"):
        raise WorkflowLoopError("execution approval identity/algorithm is invalid")
    _uuid(document["approval_id"], "approval_id")
    _uuid(document["nonce"], "approval nonce")
    _safe_id(document["key_id"], "approval key_id")
    _safe_id(document["action"], "approval action", slug=True)
    _exact_keys(document["audit"], {"ref", "sha256"}, set(), "approval audit")
    _digest(document["audit"]["sha256"], "approval audit sha256")
    expected_path = (
        "memory/runs/%s/approvals/%s.json"
        % (plan_value["run_id"], document["approval_id"])
    )
    if document["run_id"] != plan_value["run_id"] or document["loop_id"] != plan_value["loop_id"]:
        raise WorkflowLoopError("execution approval run/loop binding mismatch")
    if document["action"] != action:
        raise WorkflowLoopError("execution approval action binding mismatch")
    if document["audit"] != {
            "ref": audit_reference["ref"], "sha256": audit_reference["sha256"]}:
        raise WorkflowLoopError("execution approval audit binding mismatch")
    if document["nonce"] != gate_approval["nonce"]:
        raise WorkflowLoopError("execution approval nonce binding mismatch")
    if gate_approval["ref"] != expected_path:
        raise WorkflowLoopError("execution approval must use its canonical private run path")
    issued = _timestamp(document["issued_at"], "approval issued_at")
    expires = _timestamp(document["expires_at"], "approval expires_at")
    audit_time = _timestamp(audit_event["recorded_at"], "audit event recorded_at")
    approval_time = _timestamp(
        approval_event["recorded_at"], "approval event recorded_at",
    )
    action_time = _timestamp(action_recorded_at, "action recorded_at")
    if issued >= expires or expires - issued > dt.timedelta(hours=24):
        raise WorkflowLoopError("execution approval validity window must be positive and <=24h")
    if issued < audit_time:
        raise WorkflowLoopError("execution approval was issued before the bound audit")
    if not (
            issued <= approval_time <= expires
            and approval_time <= action_time <= expires):
        raise WorkflowLoopError("execution approval is not valid at evidence/action time")
    trust = _approval_trust_for_plan(root, plan_value)
    if document["key_id"] != trust["key_id"]:
        raise WorkflowLoopError("execution approval key_id is not trusted")
    if not (trust["_not_before"] <= issued and expires <= trust["_not_after"]):
        raise WorkflowLoopError("execution approval falls outside trust-anchor validity")
    _verify_rs256(document, trust)
    return document


def _auditor_contract(root, auditor):
    catalog, _raw = read_json(Path(root) / CATALOG_REL, "system catalog")
    matches = [item for item in catalog.get("auditors", []) if item.get("skill") == auditor]
    if len(matches) != 1:
        raise WorkflowLoopError("gate release does not identify one catalogued auditor")
    contract = matches[0]
    if (
            not isinstance(contract.get("framework"), str)
            or not isinstance(contract.get("sink"), str)
            or not contract["sink"].startswith("memory/audits/")
            or not contract["sink"].endswith("/")):
        raise WorkflowLoopError("catalogued auditor gate contract is invalid")
    return contract


def _validate_gate_release_evidence(
        root, plan_value, node, references, gate_approval, action_recorded_at,
        run_events, by_id, selected, anchor):
    """Require a validator-clean SHIP plus a signed trusted approval.

    A successful auditor action alone is not permission to traverse a release
    gate.  The cited run evidence must contain both the canonical audit result
    and an independent external-action approval event.
    """
    release_edges = _gate_release_edges(plan_value, node)
    if not release_edges:
        return
    if len(release_edges) != 1 or any(
            "external-action-approval" not in edge["permissions"]
            or "execution-approval" not in edge["required_inputs"]
            or "audit-evidence" not in edge["required_inputs"]
            for edge in release_edges):
        raise WorkflowLoopError("gate release edge lacks audit and execution-approval policy")
    if gate_approval is None:
        raise WorkflowLoopError(
            "gate release requires a signed execution approval artifact"
        )

    contract = _auditor_contract(root, node)
    audit_evidence = []
    approvals = []
    for reference in references:
        if reference["kind"] != "run-event":
            continue
        event = by_id[reference["ref"]]
        if event["event_id"] not in selected or not _is_fresh_post_plan_event(
                plan_value, event, anchor):
            continue
        route_state = _run_events_module().selected_route_state(
            run_events, event["event_id"],
        )
        if route_state is None or route_state["skill"] != node:
            continue
        if (
                event["event_type"] == "artifact_validated"
                and event["status"] == "succeeded"
                and event["dimensions"].get("validator") == "validate-audit-artifact"):
            artifact_references = [
                item for item in event.get("references", [])
                if item.get("kind") == "artifact"
            ]
            if len(artifact_references) != 1:
                continue
            artifact_reference = artifact_references[0]
            if not artifact_reference["ref"].startswith(contract["sink"]):
                continue
            path = _relative_file(root, artifact_reference["ref"])
            record, errors = _audit_artifact_module().validate(
                path, artifact_reference["ref"],
            )
            if errors:
                raise WorkflowLoopError(
                    "gate audit artifact is not validator-clean: %s" % "; ".join(errors[:3])
                )
            if (
                    record.get("framework") != contract["framework"]
                    or record.get("verdict") != "SHIP"
                    or record.get("status") != "DONE"):
                raise WorkflowLoopError(
                    "gate release requires an accepted validator-clean SHIP verdict"
                )
            audit_evidence.append((event, artifact_reference))
        elif (
                event["event_type"] == "artifact_validated"
                and event["status"] == "succeeded"
                and event["dimensions"].get("validator")
                    == "verify-workflow-execution-approval"
                and event.get("references") == [{
                    key: gate_approval[key] for key in ("kind", "ref", "sha256")
                }]):
            _verify_run_event_artifacts(root, plan_value["run_id"], event)
            approvals.append(event)
    if not audit_evidence:
        raise WorkflowLoopError(
            "gate release requires a post-plan validator-clean auditor artifact with verdict SHIP"
        )
    bound_pairs = [
        (audit_event, artifact_reference, approval)
        for audit_event, artifact_reference in audit_evidence
        for approval in approvals
        if approval["offset"] > audit_event["offset"]
        and _timestamp(approval["recorded_at"], "approval recorded_at")
            >= _timestamp(audit_event["recorded_at"], "audit recorded_at")
    ]
    if not bound_pairs:
        raise WorkflowLoopError(
            "gate release requires a post-SHIP signed execution approval event"
        )
    failures = []
    for audit_event, artifact_reference, approval in bound_pairs:
        try:
            _validate_approval_artifact(
                root, plan_value, gate_approval, artifact_reference,
                release_edges[0]["to"], audit_event, approval,
                action_recorded_at,
            )
            return
        except WorkflowLoopError as exc:
            failures.append(str(exc))
    raise WorkflowLoopError("signed execution approval rejected: %s" % failures[0])


def _validate_action_evidence(
        root, plan_value, node, references, failed=False, gate_approval=None,
        action_recorded_at=None):
    run_events = _load_run_events(root, plan_value["run_id"])
    by_id = {event["event_id"]: event for event in run_events}
    selected = _selected_run_event_ids(run_events)
    anchor = _plan_anchor_event(plan_value, run_events)
    qualified = []
    for reference in references:
        _verify_reference(root, plan_value["run_id"], reference, run_events)
        if reference["kind"] != "run-event":
            continue
        event = by_id[reference["ref"]]
        if event["event_id"] not in selected or not _is_fresh_post_plan_event(
                plan_value, event, anchor):
            continue
        if failed:
            if event["event_type"] != "turn_finished" or event["status"] != "failed":
                continue
        elif (
                event["event_type"] not in QUALIFYING_ACTION_EVENT_TYPES
                or event["status"] != "succeeded"):
            continue
        route_state = _run_events_module().selected_route_state(
            run_events, event["event_id"],
        )
        if route_state is None or route_state["skill"] != node:
            continue
        _verify_run_event_artifacts(root, plan_value["run_id"], event)
        qualified.append(event)
    if not qualified:
        kind = "failed" if failed else "completed"
        raise WorkflowLoopError(
            "%s action evidence must cite a post-plan selected-ancestry run event "
            "with a matching %s route" % (kind, node)
        )
    if not failed:
        _validate_gate_release_evidence(
            root, plan_value, node, references, gate_approval,
            action_recorded_at, run_events, by_id, selected, anchor,
        )


def _validate_verification_evidence(root, plan_value, payload):
    run_events = _load_run_events(root, plan_value["run_id"])
    by_id = {event["event_id"]: event for event in run_events}
    selected = _selected_run_event_ids(run_events)
    anchor = _plan_anchor_event(plan_value, run_events)
    criteria = {item["id"]: item for item in plan_value["success_criteria"]}
    for result in payload["criterion_results"]:
        qualified = []
        for reference in result["verified_evidence"]:
            _verify_reference(root, plan_value["run_id"], reference, run_events)
            if reference["kind"] != "run-event":
                continue
            event = by_id[reference["ref"]]
            if (
                    event["event_id"] not in selected
                    or not _is_fresh_post_plan_event(plan_value, event, anchor)
                    or event["event_type"] != "artifact_validated"
                    or event["status"] != "succeeded"
                    or event["dimensions"].get("validator")
                        != criteria[result["criterion_id"]]["validator"]):
                continue
            route_state = _run_events_module().selected_route_state(
                run_events, event["event_id"],
            )
            if route_state is None or route_state["skill"] not in plan_value["workflow"]["nodes"]:
                continue
            _verify_run_event_artifacts(root, plan_value["run_id"], event)
            qualified.append(event)
        if not qualified:
            raise WorkflowLoopError(
                "criterion %s requires a post-plan selected-ancestry artifact_validated event"
                % result["criterion_id"]
            )


def _validate_selected_evidence(root, plan_value, references, label):
    """Require at least one post-plan run event on the currently selected ancestry."""
    run_events = _load_run_events(root, plan_value["run_id"])
    by_id = {event["event_id"]: event for event in run_events}
    selected = _selected_run_event_ids(run_events)
    anchor = _plan_anchor_event(plan_value, run_events)
    qualified = []
    for reference in references:
        _verify_reference(root, plan_value["run_id"], reference, run_events)
        if reference["kind"] != "run-event":
            continue
        event = by_id[reference["ref"]]
        if event["event_id"] in selected and _is_fresh_post_plan_event(
                plan_value, event, anchor):
            qualified.append(event)
    if not qualified:
        raise WorkflowLoopError(
            "%s evidence must cite a post-plan event on the selected run ancestry" % label
        )


def _load_graph(root):
    graph, graph_raw = read_json(Path(root) / GRAPH_REL, "workflow graph")
    claimed = graph.get("graph_sha256")
    _digest(claimed, "workflow graph digest")
    without_digest = dict(graph)
    without_digest.pop("graph_sha256", None)
    if sha256_json(without_digest) != claimed:
        raise WorkflowLoopError("workflow graph digest is invalid")
    authority = graph.get("authority")
    if not isinstance(authority, dict):
        raise WorkflowLoopError("workflow graph authority block is missing")
    if (
            authority.get("source") != SOURCE_REL.as_posix()
            or authority.get("node_source") != CATALOG_REL.as_posix()):
        raise WorkflowLoopError("workflow graph authority paths are invalid")
    source, source_raw = read_json(Path(root) / SOURCE_REL, "workflow graph source")
    catalog, catalog_raw = read_json(Path(root) / CATALOG_REL, "system catalog")
    if sha256_bytes(source_raw) != authority.get("source_sha256"):
        raise WorkflowLoopError("workflow graph authoritative source drift")
    if sha256_bytes(catalog_raw) != authority.get("node_source_sha256"):
        raise WorkflowLoopError("workflow graph catalog source drift")
    if (
            graph.get("edge_shards") != source.get("edge_shards")
            or graph.get("workflows") != source.get("workflows")
            or graph.get("automatic_handoff_policy") != source.get("automatic_handoff_policy")):
        raise WorkflowLoopError("workflow graph is not a projection of its authoritative source")
    descriptors = source.get("edge_shards")
    if not isinstance(descriptors, list) or not descriptors:
        raise WorkflowLoopError("workflow graph source has no authoritative edge shards")
    edges = []
    for index, descriptor in enumerate(descriptors):
        if not isinstance(descriptor, dict):
            raise WorkflowLoopError("workflow graph edge shard descriptor is invalid")
        ref = descriptor.get("ref")
        expected_ref = "references/workflow-graph/%s.json" % descriptor.get("id")
        if ref != expected_ref:
            raise WorkflowLoopError("workflow graph edge shard ref is invalid")
        shard, shard_raw = read_json(Path(root) / ref, "workflow graph edge shard")
        if sha256_bytes(shard_raw) != descriptor.get("sha256"):
            raise WorkflowLoopError("workflow graph edge shard digest mismatch")
        if (
                shard.get("$schema") != "../workflow-graph-edge-shard.schema.json"
                or shard.get("schema_version") != SCHEMA_VERSION
                or shard.get("authority") != "authoritative-workflow-graph-source-shard"
                or shard.get("shard_id") != descriptor.get("id")
                or not isinstance(shard.get("edges"), list)
                or len(shard["edges"]) != descriptor.get("edge_count")
                or not shard["edges"]
                or shard["edges"][0].get("id") != descriptor.get("first_edge_id")
                or shard["edges"][-1].get("id") != descriptor.get("last_edge_id")):
            raise WorkflowLoopError(
                "workflow graph edge shard identity/count mismatch at index %d" % index
            )
        edges.extend(shard["edges"])
    terminals = set(source.get("terminal_nodes", []))
    exceptions = {item["node"]: item for item in source.get("node_exceptions", [])}
    stopping = {
        item["node"]: item["mode"]
        for item in source.get("node_stopping_policies", [])
    }
    expected_nodes = []
    seen = set()
    for discipline, declaration in catalog.get("disciplines", {}).items():
        for phase_index, phase in enumerate(declaration.get("phase_order", [])):
            for node_id in declaration.get("phases", {}).get(phase, []):
                if node_id in seen:
                    raise WorkflowLoopError("system catalog repeats workflow node %s" % node_id)
                seen.add(node_id)
                expected_nodes.append({
                    "id": node_id,
                    "layer": declaration.get("layer"),
                    "discipline": discipline,
                    "phase": phase,
                    "phase_index": phase_index,
                    "path": "%s/%s/%s/SKILL.md" % (discipline, phase, node_id),
                    "entrypoint": True,
                    "terminal": node_id in terminals,
                    "exception": exceptions.get(node_id),
                    "stopping_mode": stopping.get(node_id),
                })
    for node_id in catalog.get("protocol", {}).get("skills", []):
        if node_id in seen:
            raise WorkflowLoopError("system catalog repeats workflow node %s" % node_id)
        seen.add(node_id)
        expected_nodes.append({
            "id": node_id,
            "layer": catalog.get("protocol", {}).get("layer"),
            "discipline": "protocol",
            "phase": "protocol",
            "phase_index": None,
            "path": "protocol/%s/SKILL.md" % node_id,
            "entrypoint": True,
            "terminal": node_id in terminals,
            "exception": exceptions.get(node_id),
            "stopping_mode": stopping.get(node_id),
        })
    if graph.get("nodes") != expected_nodes:
        raise WorkflowLoopError("workflow graph node projection drift")
    expected_counts = {
        "nodes": len(expected_nodes),
        "edges": len(edges),
        "workflows": len(source.get("workflows", [])),
    }
    if graph.get("counts") != expected_counts:
        raise WorkflowLoopError("workflow graph count projection drift")
    expanded = dict(graph)
    expanded["edges"] = edges
    return expanded, graph_raw


def _workflow_from_graph(graph, workflow_id):
    workflows = [item for item in graph.get("workflows", []) if item.get("id") == workflow_id]
    if len(workflows) != 1:
        raise WorkflowLoopError("unknown or duplicated workflow_id %s" % workflow_id)
    return copy.deepcopy(workflows[0])


def _success_criteria(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 16:
        raise WorkflowLoopError("success_criteria must contain 1..16 typed criteria")
    result = []
    identifiers = set()
    for index, item in enumerate(value):
        _exact_keys(
            item, {"id", "description", "evidence_kind", "validator"}, set(),
            "success_criteria[%d]" % index,
        )
        criterion_id = _safe_id(item["id"], "success criterion id")
        if criterion_id in identifiers:
            raise WorkflowLoopError("success criterion ids must be unique")
        identifiers.add(criterion_id)
        if not isinstance(item["description"], str) or not item["description"].strip():
            raise WorkflowLoopError("success criterion description must be non-empty")
        if item["evidence_kind"] != "artifact-validation":
            raise WorkflowLoopError("success criterion evidence_kind must be artifact-validation")
        validator = _safe_id(item["validator"], "success criterion validator")
        result.append({
            "id": criterion_id,
            "description": item["description"].strip(),
            "evidence_kind": "artifact-validation",
            "validator": validator,
        })
    return result


def _plan_request(value):
    _exact_keys(value, {
        "schema_version", "run_id", "loop_id", "workflow_id",
        "idempotency_key", "occurred_at", "objective", "hypothesis",
        "success_criteria", "run_event_anchor",
    }, set(), "plan request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise WorkflowLoopError("unsupported plan schema_version")
    _uuid(value["run_id"], "run_id")
    _safe_id(value["loop_id"], "loop_id")
    _safe_id(value["workflow_id"], "workflow_id", slug=True)
    _safe_id(value["idempotency_key"], "idempotency_key")
    occurred = _timestamp(value["occurred_at"], "occurred_at")
    if not isinstance(value["objective"], str) or not value["objective"].strip():
        raise WorkflowLoopError("objective must be non-empty")
    if len(value["objective"].encode("utf-8")) > 16_000:
        raise WorkflowLoopError("objective exceeds 16000 bytes")
    if not isinstance(value["hypothesis"], str) or not value["hypothesis"].strip():
        raise WorkflowLoopError("hypothesis must be non-empty")
    if len(value["hypothesis"].encode("utf-8")) > 16_000:
        raise WorkflowLoopError("hypothesis exceeds 16000 bytes")
    criteria = _success_criteria(value["success_criteria"])
    anchor = _reference(value["run_event_anchor"], "run_event_anchor")
    if anchor["kind"] != "run-event":
        raise WorkflowLoopError("run_event_anchor must have kind run-event")
    return {
        **copy.deepcopy(value),
        "occurred_at": _format_timestamp(occurred),
        "objective": value["objective"].strip(),
        "hypothesis": value["hypothesis"].strip(),
        "success_criteria": criteria,
        "run_event_anchor": anchor,
    }


def _codes(value, label):
    if not isinstance(value, list) or not value:
        raise WorkflowLoopError("%s must be a non-empty array" % label)
    result = []
    for index, item in enumerate(value):
        result.append(_safe_id(item, "%s[%d]" % (label, index)))
    if len(result) != len(set(result)):
        raise WorkflowLoopError("%s must not contain duplicates" % label)
    return result


def _payload(event_type, value, workflow, success_criteria=None):
    label = event_type + " payload"
    if event_type == "planned":
        _exact_keys(value, {"plan_ref", "plan_sha256"}, set(), label)
        if not isinstance(value["plan_ref"], str) or not value["plan_ref"]:
            raise WorkflowLoopError("planned payload plan_ref must be non-empty")
        _digest(value["plan_sha256"], "plan_sha256")
        return copy.deepcopy(value)
    if event_type == "action-completed":
        _exact_keys(value, {"node", "evidence"}, {"gate_approval"}, label)
        _safe_id(value["node"], "action node", slug=True)
        if value["node"] not in workflow["nodes"]:
            raise WorkflowLoopError("action node is outside the named workflow")
        release_edges = [
            edge for edge in workflow["edge_snapshot"]
            if edge["from"] == value["node"]
            and edge["type"] == "gate" and edge["gate"] == value["node"]
        ]
        if release_edges and "gate_approval" not in value:
            raise WorkflowLoopError(
                "release-gate action requires a signed gate_approval artifact"
            )
        if not release_edges and "gate_approval" in value:
            raise WorkflowLoopError(
                "gate_approval is invalid for an action without a release gate"
            )
        result = {
            "node": value["node"],
            "evidence": _references(value["evidence"], "action evidence"),
        }
        if release_edges:
            result["gate_approval"] = _gate_approval(value["gate_approval"])
        return result
    if event_type == "action-failed":
        _exact_keys(
            value, {"node", "failure_code", "retryable", "evidence"}, set(), label,
        )
        _safe_id(value["node"], "failed action node", slug=True)
        if value["node"] not in workflow["nodes"]:
            raise WorkflowLoopError("failed action node is outside the named workflow")
        if not isinstance(value["retryable"], bool):
            raise WorkflowLoopError("failed action retryable must be boolean")
        return {
            "node": value["node"],
            "failure_code": _safe_id(value["failure_code"], "action failure_code"),
            "retryable": value["retryable"],
            "evidence": _references(value["evidence"], "failed action evidence"),
        }
    if event_type == "verification-recorded":
        _exact_keys(value, {"result", "finding_codes", "criterion_results"}, set(), label)
        if value["result"] not in {"pass", "fail", "inconclusive"}:
            raise WorkflowLoopError("verification result is unsupported")
        criteria = {item["id"]: item for item in (success_criteria or [])}
        results = value["criterion_results"]
        if not isinstance(results, list) or not results:
            raise WorkflowLoopError("verification requires typed criterion_results")
        normalized_results = []
        seen = set()
        for index, item in enumerate(results):
            _exact_keys(
                item, {"criterion_id", "status", "verified_evidence"}, set(),
                "criterion_results[%d]" % index,
            )
            criterion_id = item["criterion_id"]
            if criterion_id not in criteria or criterion_id in seen:
                raise WorkflowLoopError("criterion result is unknown or duplicated")
            seen.add(criterion_id)
            if item["status"] not in {"pass", "fail", "inconclusive"}:
                raise WorkflowLoopError("criterion status is unsupported")
            normalized_results.append({
                "criterion_id": criterion_id,
                "status": item["status"],
                "verified_evidence": _references(
                    item["verified_evidence"],
                    "criterion %s verified_evidence" % criterion_id,
                ),
            })
        if seen != set(criteria):
            raise WorkflowLoopError("verification must cover every planned success criterion")
        statuses = {item["status"] for item in normalized_results}
        derived = "fail" if "fail" in statuses else (
            "inconclusive" if "inconclusive" in statuses else "pass"
        )
        if value["result"] != derived:
            raise WorkflowLoopError("verification result disagrees with criterion_results")
        return {
            "result": value["result"],
            "finding_codes": _codes(value["finding_codes"], "finding_codes"),
            "criterion_results": sorted(
                normalized_results, key=lambda item: item["criterion_id"],
            ),
        }
    if event_type == "decision-recorded":
        _exact_keys(value, {"decision", "reason_codes", "evidence"}, set(), label)
        if value["decision"] not in {"accept", "revise", "escalate", "wait", "abort"}:
            raise WorkflowLoopError("decision is unsupported")
        return {
            "decision": value["decision"],
            "reason_codes": _codes(value["reason_codes"], "decision reason_codes"),
            "evidence": _references(value["evidence"], "decision evidence"),
        }
    if event_type == "memory-proposal-recorded":
        _exact_keys(
            value, {"target_registry", "proposal_only", "proposal", "reason_codes"},
            set(), label,
        )
        if value["target_registry"] not in REGISTRIES:
            raise WorkflowLoopError("target_registry is unsupported")
        if value["proposal_only"] is not True:
            raise WorkflowLoopError("memory output must remain proposal_only=true")
        proposal = _reference(value["proposal"], "memory proposal")
        if proposal["kind"] != "artifact":
            raise WorkflowLoopError("memory proposal must reference an immutable artifact")
        return {
            "target_registry": value["target_registry"],
            "proposal_only": True,
            "proposal": proposal,
            "reason_codes": _codes(value["reason_codes"], "memory reason_codes"),
        }
    if event_type == "terminal-recorded":
        _exact_keys(value, {"outcome", "reason_codes", "evidence"}, set(), label)
        if value["outcome"] not in TERMINAL_OUTCOMES:
            raise WorkflowLoopError("terminal outcome is unsupported")
        return {
            "outcome": value["outcome"],
            "reason_codes": _codes(value["reason_codes"], "terminal reason_codes"),
            "evidence": _references(value["evidence"], "terminal evidence"),
        }
    raise WorkflowLoopError("unsupported event_type %s" % event_type)


def _advance_request(value, plan_value):
    _exact_keys(value, {
        "schema_version", "run_id", "loop_id", "workflow_id",
        "idempotency_key", "event_type", "occurred_at",
        "expected_head_sha256", "payload",
    }, set(), "advance request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise WorkflowLoopError("unsupported advance schema_version")
    _uuid(value["run_id"], "run_id")
    _safe_id(value["loop_id"], "loop_id")
    _safe_id(value["workflow_id"], "workflow_id", slug=True)
    _safe_id(value["idempotency_key"], "idempotency_key")
    if value["event_type"] not in EVENT_TYPES - {"planned"}:
        raise WorkflowLoopError("event_type is not advanceable")
    occurred = _timestamp(value["occurred_at"], "occurred_at")
    _digest(value["expected_head_sha256"], "expected_head_sha256")
    return {
        **copy.deepcopy(value),
        "occurred_at": _format_timestamp(occurred),
        "payload": _payload(
            value["event_type"], value["payload"], plan_value["workflow"],
            plan_value["success_criteria"],
        ),
    }


def _workflow_paths(root, run_id, loop_id, create=False):
    root = Path(root).resolve()
    _uuid(run_id, "run_id")
    _safe_id(loop_id, "loop_id")
    run_dir = root / "memory" / "runs" / run_id
    if not run_dir.is_dir() or run_dir.is_symlink():
        raise WorkflowLoopError("workflow loop requires an existing real run directory")
    base = run_dir / "workflow-plans"
    work = base / loop_id
    if create:
        for path in (base, work):
            if path.exists() and (path.is_symlink() or not path.is_dir()):
                raise WorkflowLoopError("workflow runtime path must be a real directory")
            path.mkdir(mode=0o700, parents=False, exist_ok=True)
            os.chmod(path, 0o700)
    elif not work.is_dir() or work.is_symlink():
        raise WorkflowLoopError("workflow loop does not exist: %s" % loop_id)
    return {
        "dir": work,
        "plan": work / "plan.json",
        "events": work / "events.ndjson",
        "state": work / "state.json",
        "lock": work / ".lock",
    }


@contextlib.contextmanager
def _locked(path):
    if fcntl is None:
        raise WorkflowLoopError("workflow mutation requires POSIX advisory locking")
    path = Path(path)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise WorkflowLoopError("workflow lock path must be a regular file")
    with path.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _atomic_write(path, content):
    path = Path(path)
    temporary = path.parent / (".%s.workflow-loop-tmp" % path.name)
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(temporary, flags, 0o600)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _plan_snapshot(root, request, graph, workflow, anchor_event, approval_trust):
    started = _timestamp(request["occurred_at"], "occurred_at")
    deadline = started + dt.timedelta(seconds=workflow["deadline_seconds"])
    authority = graph["authority"]
    relative = (
        Path("memory") / "runs" / request["run_id"] / "workflow-plans"
        / request["loop_id"] / "plan.json"
    )
    return {
        "$schema": PLAN_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "authority": AUTHORITY,
        "run_id": request["run_id"],
        "loop_id": request["loop_id"],
        "workflow_id": request["workflow_id"],
        "objective": request["objective"],
        "hypothesis": request["hypothesis"],
        "success_criteria": request["success_criteria"],
        "created_at": request["occurred_at"],
        "deadline": _format_timestamp(deadline),
        "run_event_anchor": request["run_event_anchor"],
        "evidence_cutoff": _run_event_cutoff(anchor_event),
        "approval_trust": copy.deepcopy(approval_trust),
        "request_sha256": sha256_json(request),
        "graph": {
            "ref": GRAPH_REL.as_posix(),
            "sha256": graph["graph_sha256"],
            "source_ref": authority["source"],
            "source_sha256": authority["source_sha256"],
        },
        "workflow": workflow,
        "state_ref": (
            relative.parent / "state.json"
        ).as_posix(),
        "events_ref": (
            relative.parent / "events.ndjson"
        ).as_posix(),
    }


def _load_plan(path):
    value, raw = read_json(path, "workflow plan")
    required = {
        "$schema", "schema_version", "authoritative", "authority", "run_id",
        "loop_id", "workflow_id", "objective", "hypothesis", "success_criteria",
        "created_at", "deadline", "run_event_anchor", "request_sha256", "graph",
        "evidence_cutoff", "approval_trust", "workflow", "state_ref", "events_ref",
    }
    _exact_keys(value, required, set(), "workflow plan")
    if (
            value["$schema"] != PLAN_SCHEMA
            or value["schema_version"] != SCHEMA_VERSION
            or value["authoritative"] is not False
            or value["authority"] != AUTHORITY):
        raise WorkflowLoopError("workflow plan authority contract is invalid")
    _uuid(value["run_id"], "plan run_id")
    _safe_id(value["loop_id"], "plan loop_id")
    _safe_id(value["workflow_id"], "plan workflow_id", slug=True)
    _timestamp(value["created_at"], "plan created_at")
    _timestamp(value["deadline"], "plan deadline")
    _digest(value["request_sha256"], "plan request_sha256")
    if not isinstance(value["hypothesis"], str) or not value["hypothesis"].strip():
        raise WorkflowLoopError("plan hypothesis must be non-empty")
    value["success_criteria"] = _success_criteria(value["success_criteria"])
    _reference(value["run_event_anchor"], "plan run_event_anchor")
    if value["run_event_anchor"]["kind"] != "run-event":
        raise WorkflowLoopError("plan anchor must be a run event")
    value["evidence_cutoff"] = _evidence_cutoff(value["evidence_cutoff"])
    value["approval_trust"] = _approval_trust_snapshot(
        value["approval_trust"], "plan approval_trust",
    )
    if not isinstance(value["workflow"], dict) or value["workflow"].get("id") != value["workflow_id"]:
        raise WorkflowLoopError("plan workflow snapshot is invalid")
    return value, raw


def _event_request_hash(event):
    fields = {
        key: event[key] for key in (
            "schema_version", "run_id", "loop_id", "workflow_id",
            "idempotency_key", "event_type", "occurred_at",
            "expected_head_sha256", "payload",
        )
    }
    return sha256_json(fields)


def _stored_event(request, offset, previous_hash, recorded_at):
    event = {
        **copy.deepcopy(request),
        "authoritative": False,
        "authority": AUTHORITY,
        "event_id": str(uuid.uuid5(
            NAMESPACE,
            "%s:%s:%s" % (request["run_id"], request["loop_id"], request["idempotency_key"]),
        )),
        "offset": offset,
        "recorded_at": recorded_at,
        "request_hash": sha256_json(request),
        "previous_hash": previous_hash,
    }
    event["event_hash"] = sha256_json(event)
    return event


def _read_events(path, plan):
    path = Path(path)
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise WorkflowLoopError("workflow event stream must be a regular file")
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise WorkflowLoopError("cannot read workflow event stream: %s" % exc) from exc
    maximum = plan["workflow"]["budgets"]["max_events"] * MAX_EVENT_BYTES
    if len(raw) > maximum:
        raise WorkflowLoopError("workflow event stream exceeds its declared event budget")
    events = []
    previous = ZERO_HASH
    keys = set()
    identifiers = set()
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.strip():
            raise WorkflowLoopError("blank line in event stream at line %d" % line_number)
        if len(line) > MAX_EVENT_BYTES:
            raise WorkflowLoopError("event line %d exceeds %d bytes" % (line_number, MAX_EVENT_BYTES))
        try:
            text = line.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise WorkflowLoopError("event line %d must be UTF-8" % line_number) from exc
        event = strict_json_loads(text, "event line %d" % line_number)
        required = {
            "schema_version", "run_id", "loop_id", "workflow_id",
            "idempotency_key", "event_type", "occurred_at", "expected_head_sha256",
            "payload", "authoritative", "authority", "event_id", "offset",
            "recorded_at", "request_hash", "previous_hash", "event_hash",
        }
        _exact_keys(event, required, set(), "stored event")
        if (
                event["schema_version"] != SCHEMA_VERSION
                or event["run_id"] != plan["run_id"]
                or event["loop_id"] != plan["loop_id"]
                or event["workflow_id"] != plan["workflow_id"]
                or event["authoritative"] is not False
                or event["authority"] != AUTHORITY):
            raise WorkflowLoopError("event identity/authority mismatch at line %d" % line_number)
        _safe_id(event["idempotency_key"], "stored idempotency_key")
        if event["event_type"] not in EVENT_TYPES:
            raise WorkflowLoopError("unsupported stored event type at line %d" % line_number)
        _timestamp(event["occurred_at"], "stored occurred_at")
        _timestamp(event["recorded_at"], "stored recorded_at")
        _digest(event["expected_head_sha256"], "stored expected head")
        _payload(
            event["event_type"], event["payload"], plan["workflow"],
            plan["success_criteria"],
        )
        if event["offset"] != line_number:
            raise WorkflowLoopError("event offset mismatch at line %d" % line_number)
        _uuid(event["event_id"], "stored event_id")
        expected_id = str(uuid.uuid5(
            NAMESPACE,
            "%s:%s:%s" % (plan["run_id"], plan["loop_id"], event["idempotency_key"]),
        ))
        if event["event_id"] != expected_id:
            raise WorkflowLoopError("event_id mismatch at line %d" % line_number)
        if event["idempotency_key"] in keys or event["event_id"] in identifiers:
            raise WorkflowLoopError("duplicate event identity at line %d" % line_number)
        keys.add(event["idempotency_key"])
        identifiers.add(event["event_id"])
        if event["previous_hash"] != previous:
            raise WorkflowLoopError("event hash chain mismatch at line %d" % line_number)
        expected_head = ZERO_HASH if line_number == 1 else events[-1]["event_hash"]
        if event["expected_head_sha256"] != expected_head:
            raise WorkflowLoopError("stored compare-and-swap head mismatch at line %d" % line_number)
        _digest(event["request_hash"], "stored request_hash")
        if event["request_hash"] != _event_request_hash(event):
            raise WorkflowLoopError("stored request hash mismatch at line %d" % line_number)
        claimed = event["event_hash"]
        _digest(claimed, "stored event_hash")
        without_hash = dict(event)
        without_hash.pop("event_hash")
        if sha256_json(without_hash) != claimed:
            raise WorkflowLoopError("event hash mismatch at line %d" % line_number)
        if line_number == 1 and event["event_type"] != "planned":
            raise WorkflowLoopError("first workflow event must be planned")
        if line_number > 1 and event["event_type"] == "planned":
            raise WorkflowLoopError("planned event may occur only once")
        if events and _timestamp(event["occurred_at"], "occurred_at") < _timestamp(
                events[-1]["occurred_at"], "previous occurred_at"):
            raise WorkflowLoopError("event timestamps must be monotonic")
        if events and _timestamp(event["recorded_at"], "recorded_at") <= _timestamp(
                events[-1]["recorded_at"], "previous recorded_at"):
            raise WorkflowLoopError("event recorded_at timestamps must be strictly monotonic")
        events.append(event)
        previous = claimed
    return events


def _initial_state(plan):
    workflow = plan["workflow"]
    return {
        "$schema": STATE_SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "authoritative": False,
        "authority": AUTHORITY,
        "run_id": plan["run_id"],
        "loop_id": plan["loop_id"],
        "workflow_id": plan["workflow_id"],
        "objective": plan["objective"],
        "hypothesis": plan["hypothesis"],
        "success_criteria": copy.deepcopy(plan["success_criteria"]),
        "graph_sha256": plan["graph"]["sha256"],
        "run_event_anchor": plan["run_event_anchor"],
        "evidence_cutoff": plan["evidence_cutoff"],
        "approval_trust": plan["approval_trust"],
        "deadline": plan["deadline"],
        "limits": {
            "max_cycles": workflow["max_cycles"],
            **copy.deepcopy(workflow["budgets"]),
        },
        "status": "absent",
        "stage": "planned",
        "cycle": 1,
        "frontier": [],
        "completed_nodes": [],
        "failed_actions": [],
        "action_evidence": {},
        "cycle_summaries": [],
        "latest_verification": None,
        "last_verification_signature": None,
        "stall_count": 0,
        "accepted_decision": False,
        "memory_proposal": None,
        "consumed_approval_nonces": [],
        "forced_outcome": None,
        "terminal": None,
        "counts": {
            "events": 0,
            "actions": 0,
            "retries": 0,
            "verifications": 0,
            "decisions": 0,
            "memory_proposals": 0,
        },
        "last_event_id": None,
        "last_event_hash": ZERO_HASH,
        "last_occurred_at": None,
        "last_recorded_at": None,
    }


def _topology(plan):
    workflow = plan["workflow"]
    # Resolve only the edges selected by this immutable plan from its graph snapshot.
    # plan() stores a compact edge snapshot to avoid consulting a future graph version.
    edges = workflow["edge_snapshot"]
    outgoing = {}
    for node in workflow["nodes"]:
        outgoing[node] = []
    for edge in edges:
        outgoing[edge["from"]].append(edge["to"])
    for node in outgoing:
        outgoing[node] = sorted(outgoing[node])
    joins = {item["at"]: item for item in workflow["joins"]}
    return outgoing, joins


def _bound_reasons(state, occurred_at, event_type=None):
    reasons = []
    if _timestamp(occurred_at, "occurred_at") > _timestamp(state["deadline"], "deadline"):
        reasons.append("deadline")
    limits = state["limits"]
    counts = state["counts"]
    if counts["events"] >= limits["max_events"] - 1:
        reasons.append("event-budget")
    if (
            event_type in {"action-completed", "action-failed", None}
            and counts["actions"] >= limits["max_actions"]):
        reasons.append("action-budget")
    if (
            event_type in {"verification-recorded", None}
            and counts["verifications"] >= limits["max_verifications"]):
        reasons.append("verification-budget")
    if (
            event_type in {"memory-proposal-recorded", None}
            and counts["memory_proposals"] >= limits["max_memory_proposals"]):
        reasons.append("memory-proposal-budget")
    return reasons


def _apply_event(state, event, plan):
    workflow = plan["workflow"]
    event_type = event["event_type"]
    payload = event["payload"]
    if event_type == "planned":
        if state["counts"]["events"] or state["status"] != "absent":
            raise WorkflowLoopError("planned event may only initialize an absent loop")
        expected_ref = plan["events_ref"].rsplit("/", 1)[0] + "/plan.json"
        if payload["plan_ref"] != expected_ref:
            raise WorkflowLoopError("planned event references the wrong plan path")
        state["status"] = "active"
        state["stage"] = "action"
        state["frontier"] = [workflow["entry_node"]]
    else:
        if state["status"] == "terminal":
            raise WorkflowLoopError("workflow loop is already terminal")
        if state["counts"]["events"] >= state["limits"]["max_events"]:
            raise WorkflowLoopError("workflow event budget is fully exhausted")
        if event_type != "terminal-recorded":
            reasons = _bound_reasons(state, event["occurred_at"], event_type)
            if reasons:
                raise WorkflowLoopError(
                    "bounded loop requires terminal-recorded before further work: %s"
                    % ",".join(reasons)
                )

    if event_type == "action-completed":
        if state["stage"] != "action":
            raise WorkflowLoopError("action-completed is not valid in stage %s" % state["stage"])
        node = payload["node"]
        if node not in state["frontier"]:
            raise WorkflowLoopError("action node is not in the current frontier")
        if "gate_approval" in payload:
            nonce = payload["gate_approval"]["nonce"]
            if nonce in state["consumed_approval_nonces"]:
                raise WorkflowLoopError("execution approval nonce was already consumed")
            state["consumed_approval_nonces"].append(nonce)
            state["consumed_approval_nonces"] = sorted(
                state["consumed_approval_nonces"],
            )
        state["frontier"].remove(node)
        state["completed_nodes"].append(node)
        state["completed_nodes"] = sorted(set(state["completed_nodes"]))
        state["action_evidence"][node] = copy.deepcopy(payload["evidence"])
        state["counts"]["actions"] += 1
        outgoing, joins = _topology(plan)
        completed = set(state["completed_nodes"])
        frontier = set(state["frontier"])
        for target in outgoing[node]:
            if target in completed:
                continue
            join = joins.get(target)
            if join is not None and not set(join["requires"]).issubset(completed):
                continue
            frontier.add(target)
        state["frontier"] = sorted(frontier)
        if set(workflow["terminal_nodes"]).issubset(completed):
            if state["frontier"]:
                raise WorkflowLoopError("workflow terminals completed with unfinished frontier")
            state["stage"] = "verification"
        elif not state["frontier"]:
            raise WorkflowLoopError("workflow reached an undeclared operational dead end")

    elif event_type == "action-failed":
        if state["stage"] != "action":
            raise WorkflowLoopError("action-failed is not valid in stage %s" % state["stage"])
        node = payload["node"]
        if node not in state["frontier"]:
            raise WorkflowLoopError("failed action node is not in the current frontier")
        state["failed_actions"].append({
            "node": node,
            "failure_code": payload["failure_code"],
            "retryable": payload["retryable"],
            "evidence": copy.deepcopy(payload["evidence"]),
            "cycle": state["cycle"],
        })
        state["counts"]["actions"] += 1
        if payload["retryable"] and state["counts"]["retries"] < state["limits"]["max_retries"]:
            state["counts"]["retries"] += 1
            # The failed node remains in the frontier; this is an action retry,
            # not a new outer verification cycle.
        else:
            state["frontier"] = []
            fail_closed = any(
                join["branch_failure_policy"] == "fail-closed-escalate"
                for join in workflow["joins"]
            )
            state["stage"] = "escalation-required" if fail_closed else "terminal-ready"
            state["forced_outcome"] = "escalated" if fail_closed else "failed"

    elif event_type == "verification-recorded":
        if state["stage"] != "verification":
            raise WorkflowLoopError("verification-recorded is not valid in stage %s" % state["stage"])
        signature = sha256_json({
            "result": payload["result"],
            "finding_codes": sorted(payload["finding_codes"]),
            "criterion_statuses": {
                item["criterion_id"]: item["status"]
                for item in payload["criterion_results"]
            },
        })
        if payload["result"] == "pass":
            stall_count = 0
        elif signature == state["last_verification_signature"]:
            stall_count = state["stall_count"] + 1
        else:
            stall_count = 1
        state["last_verification_signature"] = signature
        state["stall_count"] = stall_count
        state["latest_verification"] = {
            "result": payload["result"],
            "finding_codes": sorted(payload["finding_codes"]),
            "signature": signature,
            "criterion_results": copy.deepcopy(payload["criterion_results"]),
        }
        state["counts"]["verifications"] += 1
        if payload["result"] != "pass" and stall_count >= state["limits"]["stall_limit"]:
            state["stage"] = "escalation-required"
            state["forced_outcome"] = "escalated"
        else:
            state["stage"] = "decision"

    elif event_type == "decision-recorded":
        if state["stage"] != "decision":
            raise WorkflowLoopError("decision-recorded is not valid in stage %s" % state["stage"])
        decision = payload["decision"]
        result = state["latest_verification"]["result"]
        state["counts"]["decisions"] += 1
        if decision == "accept":
            if result != "pass":
                raise WorkflowLoopError("accept requires a passing verification")
            state["accepted_decision"] = True
            state["stage"] = "memory-proposal"
        elif decision == "revise":
            if result == "pass":
                raise WorkflowLoopError("revise is invalid after a passing verification")
            state["cycle_summaries"].append({
                "cycle": state["cycle"],
                "verification_result": result,
                "verification_signature": state["latest_verification"]["signature"],
                "completed_nodes": copy.deepcopy(state["completed_nodes"]),
                "decision_reason_codes": copy.deepcopy(payload["reason_codes"]),
            })
            if state["cycle"] >= state["limits"]["max_cycles"]:
                state["stage"] = "terminal-ready"
                state["forced_outcome"] = "exhausted"
            else:
                state["cycle"] += 1
                state["stage"] = "action"
                state["frontier"] = [workflow["entry_node"]]
                state["completed_nodes"] = []
                state["failed_actions"] = []
                state["action_evidence"] = {}
                state["accepted_decision"] = False
        elif decision == "escalate":
            state["stage"] = "terminal-ready"
            state["forced_outcome"] = "escalated"
        elif decision == "wait":
            state["stage"] = "terminal-ready"
            state["forced_outcome"] = "waiting"
        else:
            state["stage"] = "terminal-ready"
            state["forced_outcome"] = "aborted"

    elif event_type == "memory-proposal-recorded":
        if state["stage"] != "memory-proposal" or not state["accepted_decision"]:
            raise WorkflowLoopError("memory proposal requires an accepted decision")
        state["memory_proposal"] = {
            "target_registry": payload["target_registry"],
            "proposal_only": True,
            "proposal": copy.deepcopy(payload["proposal"]),
            "reason_codes": copy.deepcopy(payload["reason_codes"]),
        }
        state["counts"]["memory_proposals"] += 1
        state["stage"] = "terminal-ready"
        state["forced_outcome"] = "converged"

    elif event_type == "terminal-recorded":
        outcome = payload["outcome"]
        bounds = _bound_reasons(state, event["occurred_at"], None)
        if outcome == "converged":
            if (
                    state["forced_outcome"] != "converged"
                    or not state["accepted_decision"]
                    or state["memory_proposal"] is None):
                raise WorkflowLoopError("converged requires acceptance and a proposal-only memory artifact")
        elif outcome == "exhausted":
            if state["forced_outcome"] != "exhausted" and not bounds:
                raise WorkflowLoopError("exhausted requires a reached cycle/deadline/budget bound")
        elif outcome == "escalated":
            deadline_escalation = (
                "deadline" in bounds
                and state["stage"] == "action"
                and any(
                    join["timeout_policy"] == "workflow-deadline-escalate"
                    for join in workflow["joins"]
                )
            )
            if (
                    state["forced_outcome"] != "escalated"
                    and state["stage"] != "escalation-required"
                    and not deadline_escalation):
                raise WorkflowLoopError("escalated requires an escalation decision or stall limit")
        elif outcome in {"waiting", "failed", "aborted"}:
            if state["forced_outcome"] != outcome:
                raise WorkflowLoopError(
                    "%s requires the matching typed decision or failure state" % outcome
                )
        state["status"] = "terminal"
        state["stage"] = "terminal"
        state["frontier"] = []
        state["terminal"] = {
            "outcome": outcome,
            "reason_codes": copy.deepcopy(payload["reason_codes"]),
            "evidence": copy.deepcopy(payload["evidence"]),
            "bounds": bounds,
        }

    state["counts"]["events"] += 1
    state["last_event_id"] = event["event_id"]
    state["last_event_hash"] = event["event_hash"]
    state["last_occurred_at"] = event["occurred_at"]
    state["last_recorded_at"] = event["recorded_at"]
    return state


def _project(plan, events):
    state = _initial_state(plan)
    for event in events:
        state = _apply_event(state, event, plan)
    return state


def _append_line(path, event):
    line = canonical_json(event).encode("utf-8") + b"\n"
    if len(line) > MAX_EVENT_BYTES:
        raise WorkflowLoopError("workflow event exceeds %d bytes" % MAX_EVENT_BYTES)
    flags = os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, 0o600)
    try:
        written = 0
        while written < len(line):
            count = os.write(descriptor, line[written:])
            if count <= 0:
                raise WorkflowLoopError("short write while appending workflow event")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _event_references(event):
    payload = event["payload"]
    if event["event_type"] in {
            "action-completed", "action-failed", "decision-recorded",
            "terminal-recorded"}:
        return payload["evidence"]
    if event["event_type"] == "verification-recorded":
        return [
            reference
            for result in payload["criterion_results"]
            for reference in result["verified_evidence"]
        ]
    if event["event_type"] == "memory-proposal-recorded":
        return [payload["proposal"]]
    return []


def _validate_event_evidence(root, plan_value, event):
    """Validate evidence semantics against the live, selected run-event branch."""
    event_type = event["event_type"]
    payload = event["payload"]
    if event_type == "action-completed":
        _validate_action_evidence(
            root, plan_value, payload["node"], payload["evidence"], failed=False,
            gate_approval=payload.get("gate_approval"),
            action_recorded_at=event["recorded_at"],
        )
    elif event_type == "action-failed":
        _validate_action_evidence(
            root, plan_value, payload["node"], payload["evidence"], failed=True,
        )
    elif event_type == "verification-recorded":
        _validate_verification_evidence(root, plan_value, payload)
    elif event_type in {"decision-recorded", "terminal-recorded"}:
        _validate_selected_evidence(
            root, plan_value, payload["evidence"], event_type,
        )
    elif event_type == "memory-proposal-recorded":
        _verify_reference(root, plan_value["run_id"], payload["proposal"])


def _append_locked(root, paths, plan_value, events, request):
    request_hash = sha256_json(request)
    existing = [event for event in events if event["idempotency_key"] == request["idempotency_key"]]
    if existing:
        if len(existing) != 1 or existing[0]["request_hash"] != request_hash:
            raise WorkflowLoopError("idempotency_key was already used with a different request")
        for event in events:
            _validate_event_evidence(root, plan_value, event)
        projected = _project(plan_value, events)
        _atomic_write(paths["state"], pretty_json(projected))
        return {"deduplicated": True, "event": existing[0], "state": projected}
    head = events[-1]["event_hash"] if events else ZERO_HASH
    if request["expected_head_sha256"] != head:
        raise WorkflowLoopError("stale expected_head_sha256")
    if events and events[-1]["event_type"] == "terminal-recorded":
        raise WorkflowLoopError("workflow loop is already terminal")
    if events and _timestamp(request["occurred_at"], "occurred_at") < _timestamp(
            events[-1]["occurred_at"], "previous occurred_at"):
        raise WorkflowLoopError("event timestamps must be monotonic")
    recorded_at = _runtime_now()
    _timestamp(recorded_at, "runtime recorded_at")
    if events and _timestamp(recorded_at, "runtime recorded_at") <= _timestamp(
            events[-1]["recorded_at"], "previous recorded_at"):
        raise WorkflowLoopError(
            "runtime recorded_at must be strictly later than the stored workflow head"
        )
    references = _event_references(request)
    if references:
        _verify_references(root, plan_value["run_id"], references)
    event = _stored_event(request, len(events) + 1, head, recorded_at)
    _validate_event_evidence(root, plan_value, event)
    projected = _apply_event(_project(plan_value, events), event, plan_value)
    _append_line(paths["events"], event)
    try:
        _atomic_write(paths["state"], pretty_json(projected))
    except Exception as exc:
        raise EventCommittedError(
            "event_committed=true event_id=%s: projection install failed (%s); "
            "retry the identical idempotency_key to rebuild state"
            % (event["event_id"], exc)
        ) from exc
    return {"deduplicated": False, "event": event, "state": projected}


def plan(root, request):
    """Create/recover a plan under the run coordinator's persistence cutoff."""
    root = Path(root).resolve()
    normalized = _plan_request(request)
    paths = _workflow_paths(root, normalized["run_id"], normalized["loop_id"], create=True)
    module = _run_events_module()
    try:
        # Global lock order is run coordinator -> workflow lock. Every run-event
        # writer takes the same coordinator, so no event can be committed after
        # the cutoff read but before plan.json is durable.
        with module.locked_run_coordinator(root, normalized["run_id"]):
            with _locked(paths["lock"]):
                run_events = _load_run_events(root, normalized["run_id"])
                _verify_reference(
                    root, normalized["run_id"], normalized["run_event_anchor"],
                    run_events,
                )
                if paths["plan"].exists():
                    plan_value, plan_raw = _load_plan(paths["plan"])
                    if (
                            plan_value["run_id"] != normalized["run_id"]
                            or plan_value["loop_id"] != normalized["loop_id"]
                            or plan_value["workflow_id"] != normalized["workflow_id"]
                            or plan_value["request_sha256"] != sha256_json(normalized)):
                        raise WorkflowLoopError(
                            "loop_id already identifies a different plan request"
                        )
                    _validate_plan_anchor(plan_value, run_events)
                    if _workflow_requires_approval(plan_value["workflow"]):
                        _approval_trust_for_plan(root, plan_value)
                else:
                    anchor_event = _validate_plan_anchor({
                        "run_event_anchor": normalized["run_event_anchor"],
                        "created_at": normalized["occurred_at"],
                    }, run_events, require_current_head=True)
                    graph, _ = _load_graph(root)
                    workflow = _workflow_from_graph(graph, normalized["workflow_id"])
                    edges_by_id = {edge["id"]: edge for edge in graph["edges"]}
                    workflow["edge_snapshot"] = [
                        copy.deepcopy(edges_by_id[edge_id])
                        for edge_id in workflow["edge_ids"]
                    ]
                    approval_trust = (
                        _load_approval_trust(root)[1]
                        if _workflow_requires_approval(workflow) else None
                    )
                    plan_value = _plan_snapshot(
                        root, normalized, graph, workflow, anchor_event,
                        approval_trust,
                    )
                    plan_raw = pretty_json(plan_value).encode("utf-8")
                    _atomic_write(paths["plan"], plan_raw.decode("utf-8"))
                plan_digest = sha256_bytes(plan_raw)
                relative_plan = paths["plan"].relative_to(root).as_posix()
                event_request = {
                    "schema_version": SCHEMA_VERSION,
                    "run_id": normalized["run_id"],
                    "loop_id": normalized["loop_id"],
                    "workflow_id": normalized["workflow_id"],
                    "idempotency_key": normalized["idempotency_key"],
                    "event_type": "planned",
                    "occurred_at": normalized["occurred_at"],
                    "expected_head_sha256": ZERO_HASH,
                    "payload": {"plan_ref": relative_plan, "plan_sha256": plan_digest},
                }
                events = _read_events(paths["events"], plan_value)
                return _append_locked(
                    root, paths, plan_value, events, event_request,
                )
    except module.RunEventError as exc:
        raise WorkflowLoopError(
            "workflow plan could not acquire the run persistence cutoff: %s" % exc
        ) from exc


def advance(root, request):
    """Append one typed transition using compare-and-swap and idempotency."""
    root = Path(root).resolve()
    if not isinstance(request, dict):
        raise WorkflowLoopError("advance request must be an object")
    run_id = request.get("run_id")
    loop_id = request.get("loop_id")
    _uuid(run_id, "run_id")
    _safe_id(loop_id, "loop_id")
    paths = _workflow_paths(root, run_id, loop_id, create=False)
    with _locked(paths["lock"]):
        plan_value, plan_raw = _load_plan(paths["plan"])
        normalized = _advance_request(request, plan_value)
        if normalized["workflow_id"] != plan_value["workflow_id"]:
            raise WorkflowLoopError("advance workflow_id does not match the immutable plan")
        events = _read_events(paths["events"], plan_value)
        if not events or events[0]["payload"]["plan_sha256"] != sha256_bytes(plan_raw):
            raise WorkflowLoopError("workflow plan digest does not match the planned event")
        return _append_locked(root, paths, plan_value, events, normalized)


def verify(root, run_id, loop_id, repair_projection=False):
    """Validate the plan, run anchor, evidence, stream, and state projection."""
    root = Path(root).resolve()
    paths = _workflow_paths(root, run_id, loop_id, create=False)
    with _locked(paths["lock"]):
        plan_value, plan_raw = _load_plan(paths["plan"])
        if plan_value["run_id"] != run_id or plan_value["loop_id"] != loop_id:
            raise WorkflowLoopError("workflow plan identity mismatch")
        run_events = _load_run_events(root, run_id)
        _verify_reference(root, run_id, plan_value["run_event_anchor"], run_events)
        _validate_plan_anchor(plan_value, run_events)
        if _workflow_requires_approval(plan_value["workflow"]):
            _approval_trust_for_plan(root, plan_value)
        events = _read_events(paths["events"], plan_value)
        if not events:
            raise WorkflowLoopError("workflow event stream is empty")
        if events[0]["payload"]["plan_sha256"] != sha256_bytes(plan_raw):
            raise WorkflowLoopError("workflow plan digest does not match the planned event")
        for event in events:
            _validate_event_evidence(root, plan_value, event)
        projected = _project(plan_value, events)
        projection_current = False
        if paths["state"].exists():
            stored, _ = read_json(paths["state"], "workflow state projection")
            projection_current = stored == projected
        if not projection_current:
            if not repair_projection:
                raise WorkflowLoopError("workflow state projection is missing or stale")
            _atomic_write(paths["state"], pretty_json(projected))
            projection_current = True
        current_graph_match = False
        try:
            graph, _ = _load_graph(root)
            current_graph_match = graph["graph_sha256"] == plan_value["graph"]["sha256"]
        except WorkflowLoopError:
            current_graph_match = False
        return {
            "valid": True,
            "authoritative": False,
            "authority": AUTHORITY,
            "run_id": run_id,
            "loop_id": loop_id,
            "workflow_id": plan_value["workflow_id"],
            "event_count": len(events),
            "head_event_hash": events[-1]["event_hash"],
            "status": projected["status"],
            "stage": projected["stage"],
            "projection_current": projection_current,
            "current_graph_match": current_graph_match,
        }


def _request_file(path):
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_JSON_BYTES + 1)
        if len(raw) > MAX_JSON_BYTES:
            raise WorkflowLoopError("stdin request exceeds %d bytes" % MAX_JSON_BYTES)
        try:
            return strict_json_loads(raw.decode("utf-8"), "stdin request")
        except UnicodeDecodeError as exc:
            raise WorkflowLoopError("stdin request must be UTF-8") from exc
    return read_json(path, "request")[0]


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("plan", "advance"):
        command = subparsers.add_parser(name)
        command.add_argument("--root", default=str(ROOT))
        command.add_argument("--request", required=True, help="strict JSON file or - for stdin")
    command = subparsers.add_parser("verify")
    command.add_argument("--root", default=str(ROOT))
    command.add_argument("--run-id", required=True)
    command.add_argument("--loop-id", required=True)
    command.add_argument("--repair-projection", action="store_true")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.command == "plan":
            result = plan(args.root, _request_file(args.request))
        elif args.command == "advance":
            result = advance(args.root, _request_file(args.request))
        else:
            result = verify(
                args.root, args.run_id, args.loop_id,
                repair_projection=args.repair_projection,
            )
        print(pretty_json(result), end="")
        return 0
    except WorkflowLoopError as exc:
        print("workflow loop error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
