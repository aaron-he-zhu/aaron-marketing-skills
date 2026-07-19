#!/usr/bin/env python3
"""Append-only, idempotent event runtime for the seven truth registries."""
from __future__ import annotations

import argparse
import base64
import contextlib
import datetime as dt
import hashlib
import hmac
import json
import math
import os
from pathlib import Path
import re
import stat as statmod
import subprocess
import sys
import time
import unicodedata
import uuid

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised only on non-POSIX hosts
    fcntl = None


SCHEMA_VERSION = "1.0"
REGISTRIES = {"entities", "creators", "claims", "consent", "launches", "channels", "narrative"}
OWNERS = {
    "entities": "entity-registry",
    "creators": "creator-registry",
    "claims": "offer-claims-registry",
    "consent": "consent-registry",
    "launches": "launch-registry",
    "channels": "channel-registry",
    "narrative": "narrative-registry",
}
OPERATIONS = {"propose", "accept", "reject", "upsert", "transition", "tombstone", "suppress", "restore", "erase"}
PROPOSED_OPERATIONS = {"upsert", "transition", "tombstone"}
REQUEST_FIELDS = {
    "schema_version", "idempotency_key", "aggregate_id", "operation",
    "proposed_operation", "proposal_event_id", "occurred_at", "actor",
    "authorized_by", "authorization_ref", "source", "expected_revision", "payload",
}
ASSIGNED_EVENT_FIELDS = {
    "registry", "event_id", "offset", "recorded_at", "request_hash",
    "previous_hash", "event_hash", "principal", "authority_signature",
}
TRANSITION_GRAPHS = {
    "channels": {
        None: {"proposed"},
        "proposed": {"warming", "retired"},
        "warming": {"active", "paused", "retired"},
        "active": {"paused", "retired"},
        "paused": {"warming", "retired"},
        "retired": set(),
    },
    "launches": {
        None: {"draft"},
        "draft": {"concept"},
        "concept": {"alpha"},
        "alpha": {"beta"},
        "beta": {"general-availability"},
        "general-availability": {"archived"},
        "archived": set(),
    },
}
SOURCE_TYPES = {"measured", "user-provided", "calculated", "estimated", "proxy"}
ACTOR_TYPES = {"user", "skill", "system", "data-subject"}
HOST_KEY_ENV = "AARON_REGISTRY_HOST_KEY"
HOST_CAPABILITY_ENV = "AARON_REGISTRY_CAPABILITY"
HOST_CAPABILITY_VERSION = "2"
AUTHORITY_SIGNATURE_VERSION = "1"
CANONICAL_OWNER_OPERATIONS = {"accept", "reject", "upsert", "transition", "restore"}
CAPABILITY_OPERATIONS = CANONICAL_OWNER_OPERATIONS | {"tombstone", "erase"}
TRUSTED_CONSENT_BASIS_TYPES = {"measured", "user-provided"}
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
SAFE_FIELD = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]*$")
RAW_PHONE_CANDIDATE = re.compile(
    r"(?<![A-Za-z0-9])\+?\d[\d ().-]{7,}\d(?![A-Za-z0-9])"
)
NAMESPACE = uuid.UUID("a59b2db7-8dc7-4e9c-91a6-2ad614327f4b")
MAX_EVENT_BYTES = 1_000_000
MAX_JSON_DEPTH = 64
MAX_JSON_NODES = 10_000
MAX_INTEGER_BITS = 4096
FORBIDDEN_CONSENT_KEYS = {
    "email", "email_address", "phone", "phone_number", "name", "full_name",
    "first_name", "last_name", "address", "postal_address", "raw_identifier",
}
CONSENT_SET_FIELDS = {
    "subscription_status", "basis_ref", "proof_ref", "capture_ref",
    "lawful_basis", "consented_at", "expires_at", "jurisdiction", "channel",
}
CONSENT_REFERENCE_FIELDS = {"basis_ref", "proof_ref", "capture_ref"}
CONSENT_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,511}$")
CONSENT_STATUS_VALUES = {"subscribed"}
CONSENT_LAWFUL_BASIS_VALUES = {
    "consent", "contract", "legal-obligation", "vital-interests",
    "public-task", "legitimate-interests", "none-on-file", "unknown",
}
CONSENT_CHANNEL_VALUES = {"email", "sms", "push"}
CONSENT_REASON_CODES = {
    "unsubscribe", "complaint", "hard-bounce", "withdrawal",
    "data-subject-erasure", "new-confirmed-opt-in", "consent-correction",
    "retention-expiry", "user-request",
}


class RegistryError(ValueError):
    pass


def strict_json_loads(value, label="JSON"):
    """Parse strict JSON without duplicate keys or non-finite constants."""
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
        raise RegistryError("%s must be strict JSON: %s" % (label, exc)) from exc


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False)
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise RegistryError("event must contain finite JSON values: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _lstat(path, label, missing_ok=False):
    """Inspect a path without turning access errors into apparent absence."""
    try:
        return os.lstat(path)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise RegistryError("%s does not exist: %s" % (label, path))
    except OSError as exc:
        raise RegistryError("cannot inspect %s %s: %s" % (label, path, exc)) from exc


def _normalized_project_root(root, require_exists=True):
    supplied = Path(root)
    supplied_stat = _lstat(supplied, "project root", missing_ok=not require_exists)
    if supplied_stat is None:
        return supplied.absolute()
    if statmod.S_ISLNK(supplied_stat.st_mode):
        raise RegistryError("project root cannot be a symlink")
    if not statmod.S_ISDIR(supplied_stat.st_mode):
        raise RegistryError("project root must be a directory")
    try:
        resolved = supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise RegistryError("cannot resolve project root %s: %s" % (supplied, exc)) from exc
    return resolved


def project_root_hash(root):
    normalized = _normalized_project_root(root)
    return hashlib.sha256(os.fsencode(str(normalized))).hexdigest()


def _capability_key(secret):
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise RegistryError("host capability key must contain at least 32 bytes")
    return secret


def _b64url_encode(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value):
    if not isinstance(value, str) or not value:
        raise RegistryError("invalid host capability")
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except (ValueError, TypeError) as exc:
        raise RegistryError("invalid host capability encoding") from exc


def issue_host_capability(secret, registry, principal_id, operations, expires_at,
                          capability_id=None, *, request, project_root,
                          capability_kind="owner"):
    """Issue an out-of-band owner capability for a trusted host integration.

    Event producers must never call this with request-controlled key material. The
    host owns ``secret`` and injects only the resulting token into owner-append.
    """
    key = _capability_key(secret)
    if registry not in REGISTRIES:
        raise RegistryError("unknown capability registry")
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise RegistryError("capability principal is required")
    if not isinstance(operations, (list, tuple, set)) or len(operations) != 1:
        raise RegistryError("a request capability authorizes exactly one operation")
    operation_set = set(operations)
    if operation_set - CAPABILITY_OPERATIONS:
        raise RegistryError("capability contains an invalid operation")
    normalized = validate_request(registry, request)
    operation = next(iter(operation_set))
    if normalized["operation"] != operation:
        raise RegistryError("capability operation does not match the bound request")
    if normalized["actor"]["id"] != principal_id:
        raise RegistryError("capability principal does not match the bound request")
    if capability_kind not in {"owner", "safety"}:
        raise RegistryError("capability_kind must be owner or safety")
    is_subject_erasure = (
        registry == "consent" and operation == "erase"
        and normalized["authorized_by"] == "data-subject"
        and normalized["actor"]["type"] == "data-subject"
        and normalized["actor"]["id"] == normalized["aggregate_id"]
    )
    if capability_kind == "safety" and not is_subject_erasure:
        raise RegistryError("safety capability is limited to bound consent erasure")
    if capability_kind == "owner" and is_subject_erasure:
        raise RegistryError("data-subject erasure requires a safety capability")
    if capability_kind == "owner":
        owner = OWNERS[registry]
        if operation in CANONICAL_OWNER_OPERATIONS and principal_id != owner:
            raise RegistryError("%s may be emitted only by %s" % (operation, owner))
        if operation in {"tombstone", "erase"} and principal_id not in {
                owner, "memory-management"}:
            raise RegistryError("%s requires the registry owner or memory-management" % operation)
    parse_datetime(expires_at, "capability.expires_at")
    capability_id = capability_id or str(uuid.uuid4())
    if not isinstance(capability_id, str) or not SAFE_ID.fullmatch(capability_id):
        raise RegistryError("capability_id must be a safe identifier")
    payload = {
        "version": HOST_CAPABILITY_VERSION,
        "capability_id": capability_id,
        "capability_kind": capability_kind,
        "registry": registry,
        "principal_id": principal_id,
        "operation": operation,
        "request_hash": sha256_json(normalized),
        "aggregate_id": normalized["aggregate_id"],
        "idempotency_key": normalized["idempotency_key"],
        "project_root_hash": project_root_hash(project_root),
        "expires_at": expires_at,
    }
    material = canonical_json(payload).encode("utf-8")
    signature = hmac.new(key, material, hashlib.sha256).hexdigest()
    return _b64url_encode(material) + "." + signature


def verify_host_capability(token, registry, request, root_hash, now=None):
    secret = os.environ.get(HOST_KEY_ENV)
    if not secret:
        raise RegistryError("canonical operation requires a host capability")
    key = _capability_key(secret)
    if not isinstance(token, str) or token.count(".") != 1:
        raise RegistryError("canonical operation requires a valid host capability")
    encoded, supplied_signature = token.split(".", 1)
    material = _b64url_decode(encoded)
    expected_signature = hmac.new(key, material, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise RegistryError("host capability signature is invalid")
    try:
        decoded_material = material.decode("utf-8")
        payload = strict_json_loads(decoded_material, "host capability payload")
        if decoded_material != canonical_json(payload):
            raise RegistryError("host capability payload is not canonical JSON")
    except (UnicodeDecodeError, RegistryError) as exc:
        raise RegistryError("host capability payload is invalid") from exc
    required = {
        "version", "capability_id", "capability_kind", "registry", "principal_id",
        "operation", "request_hash", "aggregate_id", "idempotency_key",
        "project_root_hash", "expires_at",
    }
    if not isinstance(payload, dict) or set(payload) != required:
        raise RegistryError("host capability payload has invalid fields")
    if payload["version"] != HOST_CAPABILITY_VERSION or payload["registry"] != registry:
        raise RegistryError("host capability is not valid for this registry")
    operation = request["operation"]
    actor_id = request["actor"]["id"]
    if payload["principal_id"] != actor_id:
        raise RegistryError("host capability principal does not match actor attribution")
    if payload["operation"] != operation or operation not in CAPABILITY_OPERATIONS:
        raise RegistryError("host capability does not authorize this operation")
    expected_request_hash = sha256_json(request)
    if payload["request_hash"] != expected_request_hash:
        raise RegistryError("host capability does not match the normalized request")
    if payload["aggregate_id"] != request["aggregate_id"]:
        raise RegistryError("host capability does not match the aggregate_id")
    if payload["idempotency_key"] != request["idempotency_key"]:
        raise RegistryError("host capability does not match the idempotency_key")
    if payload["project_root_hash"] != root_hash:
        raise RegistryError("host capability does not match the project root")
    expires = parse_datetime(payload["expires_at"], "capability.expires_at")
    current = now or dt.datetime.now(dt.timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=dt.timezone.utc)
    if expires <= current:
        raise RegistryError("host capability has expired")
    if not isinstance(payload["capability_id"], str) or not SAFE_ID.fullmatch(payload["capability_id"]):
        raise RegistryError("host capability ID is invalid")
    kind = payload["capability_kind"]
    is_subject_erasure = (
        registry == "consent" and operation == "erase"
        and request["authorized_by"] == "data-subject"
        and request["actor"]["type"] == "data-subject"
        and request["actor"]["id"] == request["aggregate_id"]
    )
    if kind == "safety":
        if not is_subject_erasure:
            raise RegistryError("safety capability is limited to bound consent erasure")
        principal_type = "safety-capability"
    elif kind == "owner":
        if is_subject_erasure:
            raise RegistryError("data-subject erasure requires a safety capability")
        principal_type = "host-capability"
    else:
        raise RegistryError("host capability kind is invalid")
    return {
        "type": principal_type,
        "id": payload["principal_id"],
        "capability_id": payload["capability_id"],
        "request_hash": payload["request_hash"],
        "project_root_hash": payload["project_root_hash"],
        "expires_at": payload["expires_at"],
    }


def authority_signature(event, secret=None):
    key_material = secret if secret is not None else os.environ.get(HOST_KEY_ENV)
    if not key_material:
        raise RegistryError("trusted event verification requires the host authority key")
    key = _capability_key(key_material)
    material = dict(event)
    material.pop("event_hash", None)
    material.pop("authority_signature", None)
    domain = ("registry-event-authority-v%s\0" % AUTHORITY_SIGNATURE_VERSION).encode("ascii")
    return hmac.new(
        key, domain + canonical_json(material).encode("utf-8"), hashlib.sha256,
    ).hexdigest()


def event_hash(event):
    material = dict(event)
    material.pop("event_hash", None)
    return sha256_json(material)


def parse_datetime(value, label):
    if not isinstance(value, str) or not value.strip():
        raise RegistryError("%s is required" % label)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RegistryError("%s must be an ISO date-time" % label) from exc
    if parsed.tzinfo is None:
        raise RegistryError("%s must include a timezone" % label)
    return parsed


def validate_observed_at(value):
    if not isinstance(value, str) or not value:
        raise RegistryError("source.observed_at is required")
    try:
        dt.date.fromisoformat(value)
        return
    except ValueError:
        parse_datetime(value, "source.observed_at")


def walk_json(value, path="payload"):
    stack = [(value, path, 0)]
    nodes = 0
    while stack:
        current, current_path, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise RegistryError("%s exceeds the JSON node limit" % path)
        if depth > MAX_JSON_DEPTH:
            raise RegistryError("%s exceeds the JSON depth limit" % path)
        if current is None or isinstance(current, (str, bool)):
            continue
        if isinstance(current, int):
            if current.bit_length() > MAX_INTEGER_BITS:
                raise RegistryError("%s contains an oversized integer" % current_path)
            continue
        if isinstance(current, float):
            if not math.isfinite(current):
                raise RegistryError("%s contains a non-finite number" % current_path)
            continue
        if isinstance(current, list):
            stack.extend(
                (item, "%s[%d]" % (current_path, index), depth + 1)
                for index, item in enumerate(current)
            )
            continue
        if isinstance(current, dict):
            for key, item in current.items():
                if not isinstance(key, str):
                    raise RegistryError("%s has a non-string key" % current_path)
                stack.append((item, "%s.%s" % (current_path, key), depth + 1))
            continue
        raise RegistryError(
            "%s contains unsupported value %r" % (current_path, type(current).__name__)
        )


def consent_keys(value):
    found = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, item in current.items():
                if not isinstance(key, str):
                    continue
                normalized = unicodedata.normalize("NFKC", key).lower().replace("-", "_")
                if normalized in FORBIDDEN_CONSENT_KEYS:
                    found.add(key)
                stack.append(item)
        elif isinstance(current, list):
            stack.extend(current)
    return found


def string_leaves(value, path="request"):
    stack = [(value, path, 0)]
    nodes = 0
    while stack:
        current, current_path, depth = stack.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES or depth > MAX_JSON_DEPTH:
            raise RegistryError("request exceeds bounded JSON traversal limits")
        if isinstance(current, str):
            yield current_path, current
        elif isinstance(current, list):
            stack.extend(
                (item, "%s[%d]" % (current_path, index), depth + 1)
                for index, item in enumerate(current)
            )
        elif isinstance(current, dict):
            for key, item in current.items():
                if isinstance(key, str):
                    yield "%s.<key>" % current_path, key
                    stack.append((item, "%s.%s" % (current_path, key), depth + 1))


def raw_contact_kind(value, allow_datetime=False):
    normalized = unicodedata.normalize("NFKC", value)
    if "@" in normalized:
        return "email address"
    if allow_datetime:
        try:
            dt.datetime.fromisoformat(normalized.strip().replace("Z", "+00:00"))
            return None
        except ValueError:
            pass
    for candidate in RAW_PHONE_CANDIDATE.finditer(normalized):
        digit_count = sum(character.isdigit() for character in candidate.group(0))
        if 10 <= digit_count <= 15:
            return "phone number"
    return None


def validate_consent_minimum_payload(request):
    """Keep consent records closed and reference-only instead of storing free text."""
    payload = request.get("payload", {})
    reason = payload.get("reason")
    if reason is not None and (
            not isinstance(reason, str) or reason not in CONSENT_REASON_CODES):
        raise RegistryError(
            "consent payload.reason must be a subject-free reason code: %s"
            % ", ".join(sorted(CONSENT_REASON_CODES))
        )
    fields = payload.get("set", {})
    unknown = sorted(set(fields) - CONSENT_SET_FIELDS)
    if unknown:
        raise RegistryError(
            "consent payload.set contains non-minimized fields: %s" % ", ".join(unknown)
        )
    unknown_unset = sorted(set(payload.get("unset", [])) - CONSENT_SET_FIELDS)
    if unknown_unset:
        raise RegistryError(
            "consent payload.unset contains non-minimized fields: %s"
            % ", ".join(unknown_unset)
        )
    for field in CONSENT_REFERENCE_FIELDS & set(fields):
        value = fields[field]
        if not isinstance(value, str) or not CONSENT_REFERENCE.fullmatch(value):
            raise RegistryError("consent %s must be an opaque, non-PII reference" % field)
    if "subscription_status" in fields and (
            not isinstance(fields["subscription_status"], str)
            or fields["subscription_status"] not in CONSENT_STATUS_VALUES):
        raise RegistryError("consent subscription_status may only be set to subscribed")
    if "lawful_basis" in fields and (
            not isinstance(fields["lawful_basis"], str)
            or fields["lawful_basis"] not in CONSENT_LAWFUL_BASIS_VALUES):
        raise RegistryError("consent lawful_basis is not a supported code")
    if "channel" in fields and (
            not isinstance(fields["channel"], str)
            or fields["channel"] not in CONSENT_CHANNEL_VALUES):
        raise RegistryError("consent channel is not a supported code")
    if "jurisdiction" in fields:
        jurisdiction = fields["jurisdiction"]
        if (not isinstance(jurisdiction, str)
                or not re.fullmatch(r"(?:[A-Z]{2}(?:-[A-Z0-9]{1,3})?|unknown)", jurisdiction)):
            raise RegistryError("consent jurisdiction must be an uppercase region code or unknown")
    for field in ("consented_at", "expires_at"):
        if field in fields:
            parse_datetime(fields[field], "consent payload.set.%s" % field)
    for field in ("authorization_ref",):
        value = request[field]
        if not CONSENT_REFERENCE.fullmatch(value):
            raise RegistryError("consent %s must be an opaque, non-PII reference" % field)
    if not CONSENT_REFERENCE.fullmatch(request["source"]["ref"]):
        raise RegistryError("consent source.ref must be an opaque, non-PII reference")


def validate_principal_attestation(registry, request, principal, root_hash=None,
                                   recorded_at=None):
    operation = request["operation"]
    actor_id = request["actor"]["id"]
    if operation == "propose":
        expected = {"type": "ordinary", "id": actor_id}
        if principal != expected:
            raise RegistryError("proposal principal attestation is invalid")
        return
    if registry == "consent" and operation == "suppress":
        expected = {"type": "privacy-suppression", "id": actor_id}
        if principal != expected:
            raise RegistryError("consent suppression principal attestation is invalid")
        return
    subject_erasure = (
        registry == "consent" and operation == "erase"
        and request.get("authorized_by") == "data-subject"
        and request["actor"]["type"] == "data-subject"
        and actor_id == request["aggregate_id"]
    )
    principal_fields = {
        "type", "id", "capability_id", "request_hash", "project_root_hash", "expires_at",
    }
    if (not isinstance(principal, dict)
            or set(principal) != principal_fields
            or principal.get("type") not in {"host-capability", "safety-capability"}
            or principal.get("id") != actor_id
            or not isinstance(principal.get("capability_id"), str)
            or not SAFE_ID.fullmatch(principal["capability_id"])):
        raise RegistryError("canonical event lacks a trusted host principal")
    expected_type = "safety-capability" if subject_erasure else "host-capability"
    if principal["type"] != expected_type:
        raise RegistryError("canonical event has the wrong capability kind")
    if principal.get("request_hash") != sha256_json(request):
        raise RegistryError("canonical principal is not bound to the request")
    if root_hash is not None and principal.get("project_root_hash") != root_hash:
        raise RegistryError("canonical principal is not bound to this project root")
    expiry = parse_datetime(principal.get("expires_at"), "principal.expires_at")
    if recorded_at is not None and expiry <= parse_datetime(recorded_at, "recorded_at"):
        raise RegistryError("canonical event was recorded after capability expiry")
    if subject_erasure:
        return
    owner = OWNERS[registry]
    if operation in CANONICAL_OWNER_OPERATIONS and principal["id"] != owner:
        raise RegistryError("%s may be emitted only by %s" % (operation, owner))
    if operation in {"tombstone", "erase"} and principal["id"] not in {owner, "memory-management"}:
        raise RegistryError("%s requires the registry owner or memory-management" % operation)


def authorize_request(registry, request, root_hash, capability_token=None, now=None):
    operation = request["operation"]
    actor_id = request["actor"]["id"]
    if operation == "propose":
        principal = {"type": "ordinary", "id": actor_id}
    elif registry == "consent" and operation == "suppress":
        # Suppression is deliberately deny-only and privacy-first: any validated
        # producer may add suppression for a pseudonymous ID, but it cannot erase,
        # restore, authorize delivery, or mutate other canonical state.
        principal = {"type": "privacy-suppression", "id": actor_id}
    else:
        principal = verify_host_capability(
            capability_token, registry, request, root_hash, now=now,
        )
    validate_principal_attestation(registry, request, principal, root_hash=root_hash)
    return principal


def validate_operation_payload(operation, payload):
    """Enforce one unambiguous mutation shape for the effective operation."""
    has_set = bool(payload.get("set"))
    has_unset = bool(payload.get("unset"))
    has_transition = "transition" in payload
    if operation == "upsert":
        if has_transition:
            raise RegistryError("upsert payload cannot carry transition")
        if not (has_set or has_unset):
            raise RegistryError("upsert requires a non-empty set or unset")
    elif operation == "transition":
        if not has_transition:
            raise RegistryError("transition operation requires payload.transition")
        if "set" in payload or "unset" in payload:
            raise RegistryError("transition payload cannot carry set or unset")
    elif operation in {"tombstone", "suppress", "erase"}:
        if any(key in payload for key in ("set", "unset", "transition")):
            raise RegistryError("%s payload cannot carry a second mutation" % operation)
        if not str(payload.get("reason", "")).strip():
            raise RegistryError("%s requires payload.reason" % operation)
    elif operation == "restore":
        if "unset" in payload or has_transition:
            raise RegistryError("restore payload cannot carry unset or transition")
        if not has_set or not str(payload.get("reason", "")).strip():
            raise RegistryError("restore requires payload.reason and a non-empty set")


def validate_request(registry, request):
    if not isinstance(registry, str) or registry not in REGISTRIES:
        raise RegistryError("unknown registry: %s" % registry)
    if not isinstance(request, dict):
        raise RegistryError("event request must be an object")
    extra = sorted(set(request) - REQUEST_FIELDS)
    if extra:
        raise RegistryError("unknown request fields: %s" % ", ".join(extra))
    if request.get("schema_version") != SCHEMA_VERSION:
        raise RegistryError("schema_version must be %s" % SCHEMA_VERSION)
    for name in ("idempotency_key", "aggregate_id"):
        value = request.get(name)
        if not isinstance(value, str) or not SAFE_ID.fullmatch(value) or "@" in value:
            raise RegistryError("%s must be a non-PII safe identifier" % name)
    operation = request.get("operation")
    if not isinstance(operation, str) or operation not in OPERATIONS:
        raise RegistryError("invalid operation")
    parse_datetime(request.get("occurred_at"), "occurred_at")

    actor = request.get("actor")
    if not isinstance(actor, dict) or set(actor) != {"type", "id"}:
        raise RegistryError("actor requires exactly type and id")
    if (not isinstance(actor.get("type"), str) or actor.get("type") not in ACTOR_TYPES
            or not isinstance(actor.get("id"), str)
            or not actor["id"].strip() or len(actor["id"]) > 128):
        raise RegistryError("invalid actor")
    authorized_by = request.get("authorized_by")
    if not isinstance(authorized_by, str) or authorized_by not in {"user", "data-subject"}:
        raise RegistryError("authorized_by must be user or data-subject")
    auth_ref = request.get("authorization_ref")
    if not isinstance(auth_ref, str) or not auth_ref.strip() or len(auth_ref) > 256:
        raise RegistryError("authorization_ref is required and limited to 256 characters")
    if authorized_by == "data-subject":
        if not (registry == "consent" and operation in {"suppress", "erase"}):
            raise RegistryError("data-subject authorization is limited to consent suppress/erase")
        if actor.get("type") != "data-subject" or actor.get("id") != request.get("aggregate_id"):
            raise RegistryError("data-subject actor must match the consent aggregate_id")

    source = request.get("source")
    if not isinstance(source, dict) or set(source) != {"type", "ref", "observed_at"}:
        raise RegistryError("source requires exactly type, ref, and observed_at")
    if not isinstance(source.get("type"), str) or source.get("type") not in SOURCE_TYPES:
        raise RegistryError("invalid source.type")
    if not isinstance(source.get("ref"), str) or not source["ref"].strip() or len(source["ref"]) > 512:
        raise RegistryError("source.ref is required and limited to 512 characters")
    validate_observed_at(source.get("observed_at"))

    revision = request.get("expected_revision")
    if revision is not None and (not isinstance(revision, int) or isinstance(revision, bool) or revision < 0):
        raise RegistryError("expected_revision must be a non-negative integer")
    payload = request.get("payload", {})
    if not isinstance(payload, dict):
        raise RegistryError("payload must be an object")
    allowed_payload = {"set", "unset", "transition", "reason"}
    if set(payload) - allowed_payload:
        raise RegistryError("payload contains unknown fields")
    walk_json(payload)
    if "set" in payload and not isinstance(payload["set"], dict):
        raise RegistryError("payload.set must be an object")
    if registry == "consent":
        forbidden = sorted(consent_keys(payload))
        if forbidden:
            raise RegistryError(
                "consent payload contains raw PII fields: %s" % ", ".join(forbidden)
            )
    if "set" in payload and any(
            not isinstance(field, str) or not SAFE_FIELD.fullmatch(field)
            for field in payload["set"]):
        raise RegistryError("payload.set must use safe field names")
    if "unset" in payload:
        if not isinstance(payload["unset"], list) or any(
                not isinstance(item, str) or not SAFE_FIELD.fullmatch(item) for item in payload["unset"]):
            raise RegistryError("payload.unset must contain safe field names")
        if len(set(payload["unset"])) != len(payload["unset"]):
            raise RegistryError("payload.unset cannot contain duplicates")
    overlap = set(payload.get("set", {})) & set(payload.get("unset", []))
    if overlap:
        raise RegistryError("payload cannot set and unset the same field: %s" % ", ".join(sorted(overlap)))
    if "reason" in payload and (not isinstance(payload["reason"], str) or len(payload["reason"]) > 1024):
        raise RegistryError("payload.reason must be a string limited to 1024 characters")
    transition = payload.get("transition")
    if transition is not None:
        if not isinstance(transition, dict) or set(transition) != {"from", "to"}:
            raise RegistryError("payload.transition requires exactly from and to")
        if transition["from"] is not None and not isinstance(transition["from"], str):
            raise RegistryError("transition.from must be a string or null")
        if not isinstance(transition["to"], str) or not transition["to"].strip():
            raise RegistryError("transition.to must be non-empty")
    if len(canonical_json(payload).encode("utf-8")) > 256_000:
        raise RegistryError("payload exceeds 256 KB")

    if operation == "propose":
        if (not isinstance(request.get("proposed_operation"), str)
                or request.get("proposed_operation") not in PROPOSED_OPERATIONS):
            raise RegistryError("propose requires proposed_operation")
        validate_operation_payload(request["proposed_operation"], payload)
    elif "proposed_operation" in request:
        raise RegistryError("proposed_operation is valid only for propose")
    if operation in {"accept", "reject"}:
        try:
            uuid.UUID(str(request.get("proposal_event_id")))
        except (ValueError, TypeError, AttributeError) as exc:
            raise RegistryError("accept/reject requires proposal_event_id") from exc
        if any(key in payload for key in ("set", "unset", "transition")):
            raise RegistryError("accept/reject decision payload cannot carry a second mutation")
        if operation == "reject" and not str(payload.get("reason", "")).strip():
            raise RegistryError("reject requires payload.reason")
        if revision is not None:
            raise RegistryError("accept/reject inherit the proposal revision and must omit expected_revision")
    elif "proposal_event_id" in request:
        raise RegistryError("proposal_event_id is valid only for accept/reject")
    elif operation not in {"accept", "reject", "propose"}:
        validate_operation_payload(operation, payload)
    if operation == "suppress" and registry != "consent":
        raise RegistryError("suppress is valid only for consent")
    if operation == "restore" and registry != "consent":
        raise RegistryError("restore is valid only for consent")

    effective_operation = request.get("proposed_operation") if operation == "propose" else operation
    if registry in TRANSITION_GRAPHS and effective_operation == "upsert":
        if "state" in payload.get("unset", []):
            raise RegistryError("governed state cannot be unset or reinitialized")
        if "state" in payload.get("set", {}) and (
                not isinstance(payload["set"]["state"], str)
                or not payload["set"]["state"].strip()):
            raise RegistryError("governed state must be a non-empty string")

    subject_erasure = (
        registry == "consent" and operation == "erase"
        and authorized_by == "data-subject" and actor["type"] == "data-subject"
        and actor["id"] == request["aggregate_id"]
    )
    revision_required = operation in {"propose", "upsert", "transition", "tombstone", "restore"}
    if operation == "erase" and not subject_erasure:
        revision_required = True
    if revision_required and revision is None:
        raise RegistryError("%s requires expected_revision" % operation)

    if registry == "consent":
        if not SAFE_ID.fullmatch(actor["id"]) or "@" in actor["id"]:
            raise RegistryError("consent actor.id must be a non-PII safe identifier")
        if effective_operation == "transition":
            raise RegistryError("consent state changes use typed upsert/suppress/restore, not transition")
        for label, value in string_leaves(request):
            contact_kind = raw_contact_kind(
                value,
                allow_datetime=label in {
                    "request.occurred_at", "request.source.observed_at",
                    "request.payload.set.consented_at", "request.payload.set.expires_at",
                },
            )
            if contact_kind:
                raise RegistryError(
                    "consent %s must not contain a raw %s" % (label, contact_kind)
                )
        forbidden = sorted(consent_keys(payload))
        if forbidden:
            raise RegistryError("consent payload contains raw PII fields: %s" % ", ".join(forbidden))
        validate_consent_minimum_payload(request)
        if operation == "restore":
            restored = payload.get("set", {})
            basis_ref = restored.get("basis_ref")
            if (restored.get("subscription_status") != "subscribed"
                    or not isinstance(basis_ref, str) or not basis_ref.strip()):
                raise RegistryError(
                    "restore requires subscription_status=subscribed and a string basis_ref"
                )
            if source.get("type") not in TRUSTED_CONSENT_BASIS_TYPES:
                raise RegistryError("restore requires measured or user-provided basis evidence")
            if source.get("ref") != basis_ref:
                raise RegistryError("restore basis_ref must equal source.ref")
            parse_datetime(source.get("observed_at"), "restore source.observed_at")
    return json.loads(canonical_json(request))


def _has_git_marker(path):
    for candidate in (path, *path.parents):
        marker = candidate / ".git"
        if _lstat(marker, "Git marker", missing_ok=True) is not None:
            return True
    return False


def ensure_git_ignored(root_path, targets):
    """Fail closed before operational memory is written inside a Git worktree."""
    try:
        probe = subprocess.run(
            ["git", "-C", str(root_path), "rev-parse", "--show-toplevel"],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        if _has_git_marker(root_path):
            raise RegistryError("cannot verify that runtime memory is Git-ignored: %s" % exc) from exc
        return
    if probe.returncode != 0:
        if _has_git_marker(root_path):
            raise RegistryError(
                "cannot verify that runtime memory is Git-ignored: %s"
                % (probe.stderr.strip() or "git rev-parse failed")
            )
        return
    git_root = Path(probe.stdout.strip()).resolve()
    guarded_targets = []
    for target in targets:
        guarded_targets.append(target)
        # Projection writes use an atomic sibling temporary file. Non-POSIX
        # writer locking uses a sibling lock file. Check their exact names as
        # well as the final files so a narrow ignore rule cannot leak either.
        guarded_targets.append(
            target.parent / (".%s.registry-tmp" % target.name)
        )
        if target.suffix == ".ndjson":
            guarded_targets.append(target.parent / (target.name + ".lock"))
    for target in guarded_targets:
        try:
            relative = target.resolve(strict=False).relative_to(git_root)
        except ValueError as exc:
            raise RegistryError("runtime memory escapes the Git worktree") from exc
        try:
            checked = subprocess.run(
                ["git", "-C", str(git_root), "check-ignore", "--quiet", "--", str(relative)],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False, timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise RegistryError("cannot verify that runtime memory is Git-ignored: %s" % exc) from exc
        if checked.returncode != 0:
            detail = checked.stderr.strip() if checked.returncode > 1 else "path is not ignored"
            raise RegistryError(
                "refusing registry write because %s is not Git-ignored: %s"
                % (relative, detail)
            )


def _secure_fd(fd, path, mode):
    fchmod = getattr(os, "fchmod", None)
    if not callable(fchmod):
        raise RegistryError(
            "registry mutation requires descriptor-anchored permission changes"
        )
    try:
        fchmod(fd, mode)
    except OSError as exc:
        raise RegistryError("cannot secure runtime file %s: %s" % (path, exc)) from exc


def memory_paths(root, registry, create=False):
    root_path = _normalized_project_root(root, require_exists=create)
    if create and not _safe_mutation_dirfd_available():
        raise RegistryError(
            "registry mutation is unsupported on this platform because safe dirfd-anchored "
            "open/stat/mkdir/rename/unlink and descriptor-permission operations are unavailable"
        )
    memory = root_path / "memory"
    events_dir = memory / "events"
    projections_dir = memory / "projections"
    stream_path = events_dir / (registry + ".ndjson")
    projection_path = projections_dir / (registry + ".json")
    suppressions_path = projections_dir / "consent-suppressions.json"
    parent_exists = _lstat(root_path, "project root", missing_ok=not create) is not None
    for path in (memory, events_dir, projections_dir):
        if not parent_exists:
            break
        status = _lstat(path, "runtime path", missing_ok=True)
        if status is None:
            parent_exists = False
            continue
        if statmod.S_ISLNK(status.st_mode):
            raise RegistryError("runtime path cannot be a symlink: %s" % path)
        if not statmod.S_ISDIR(status.st_mode):
            raise RegistryError("runtime path must be a directory: %s" % path)
    if parent_exists:
        for path in (stream_path, projection_path, suppressions_path):
            status = _lstat(path, "runtime file", missing_ok=True)
            if status is not None and statmod.S_ISLNK(status.st_mode):
                raise RegistryError("runtime file cannot be a symlink: %s" % path)
    if create:
        write_targets = [stream_path, projection_path]
        if registry == "consent":
            write_targets.append(suppressions_path)
        ensure_git_ignored(root_path, write_targets)
        _ensure_runtime_directories(root_path)
    return stream_path, projection_path, suppressions_path


def _open_directory_anchor(path):
    current = _lstat(path, "runtime directory")
    if statmod.S_ISLNK(current.st_mode) or not statmod.S_ISDIR(current.st_mode):
        raise RegistryError("runtime parent is not a real directory: %s" % path)
    identity = (current.st_dev, current.st_ino)
    if os.name != "posix":  # pragma: no cover - Windows has no safe directory fd API
        return None, identity
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
        raise RegistryError("cannot open runtime directory %s: %s" % (path, exc)) from exc
    fd = descriptor
    current = os.fstat(fd)
    if not statmod.S_ISDIR(current.st_mode):
        os.close(fd)
        raise RegistryError("runtime parent is not a directory: %s" % path)
    identity = (current.st_dev, current.st_ino)
    try:
        _revalidate_directory_anchor(path, identity)
    except RegistryError:
        os.close(fd)
        raise
    return fd, identity


def _revalidate_directory_anchor(path, identity):
    current = _lstat(path, "runtime directory")
    if (statmod.S_ISLNK(current.st_mode) or not statmod.S_ISDIR(current.st_mode)
            or (current.st_dev, current.st_ino) != identity):
        raise RegistryError("runtime directory changed during operation: %s" % path)


def _dir_fd_supported(function):
    return function in getattr(os, "supports_dir_fd", set())


def _safe_mutation_dirfd_available():
    return (os.name == "posix" and callable(getattr(os, "fchmod", None)) and all(
        _dir_fd_supported(function)
        for function in (os.open, os.stat, os.rename, os.unlink, os.mkdir)
    ))


def _open_or_create_runtime_directory(parent_fd, parent_path, name):
    """Create/open one child without following a swapped parent or symlink."""
    child_path = parent_path / name
    try:
        os.mkdir(name, 0o700, dir_fd=parent_fd)
    except FileExistsError:
        pass
    except OSError as exc:
        raise RegistryError("cannot create runtime directory %s: %s" % (child_path, exc)) from exc
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        child_fd = os.open(name, flags, dir_fd=parent_fd)
        opened = os.fstat(child_fd)
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if (not statmod.S_ISDIR(opened.st_mode)
                or statmod.S_ISLNK(entry.st_mode)
                or (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino)):
            raise RegistryError("runtime path must remain a real directory: %s" % child_path)
        os.fchmod(child_fd, 0o700)
        return child_fd, (opened.st_dev, opened.st_ino)
    except RegistryError:
        if "child_fd" in locals():
            os.close(child_fd)
        raise
    except OSError as exc:
        if "child_fd" in locals():
            os.close(child_fd)
        raise RegistryError("cannot secure runtime directory %s: %s" % (child_path, exc)) from exc


def _assert_child_identity(parent_fd, parent_path, name, identity):
    try:
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as exc:
        raise RegistryError(
            "cannot re-inspect runtime directory %s: %s" % (parent_path / name, exc)
        ) from exc
    if (statmod.S_ISLNK(entry.st_mode) or not statmod.S_ISDIR(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != identity):
        raise RegistryError("runtime directory changed during creation: %s" % (parent_path / name))


def _ensure_runtime_directories(root_path):
    """Create memory/events and memory/projections through retained dirfds."""
    if not _safe_mutation_dirfd_available():
        raise RegistryError(
            "registry mutation is unsupported on this platform because safe dirfd-anchored "
            "directory creation and permission operations are unavailable"
        )
    root_fd, _ = _open_directory_anchor(root_path)
    memory_fd = events_fd = projections_fd = None
    try:
        memory_fd, memory_identity = _open_or_create_runtime_directory(
            root_fd, root_path, "memory"
        )
        events_fd, events_identity = _open_or_create_runtime_directory(
            memory_fd, root_path / "memory", "events"
        )
        projections_fd, projections_identity = _open_or_create_runtime_directory(
            memory_fd, root_path / "memory", "projections"
        )
        _assert_child_identity(root_fd, root_path, "memory", memory_identity)
        _assert_child_identity(
            memory_fd, root_path / "memory", "events", events_identity
        )
        _assert_child_identity(
            memory_fd, root_path / "memory", "projections", projections_identity
        )
    finally:
        for descriptor in (projections_fd, events_fd, memory_fd, root_fd):
            if descriptor is not None:
                os.close(descriptor)


def _open_anchored(parent_fd, parent_path, name, flags, mode=0o600,
                   parent_identity=None):
    try:
        if parent_fd is not None and _dir_fd_supported(os.open):
            try:
                return os.open(name, flags, mode, dir_fd=parent_fd)
            except FileNotFoundError:
                # macOS can return ENOENT when two O_NOFOLLOW|O_CREAT opens race
                # and the other process has just created the regular file.
                if not (flags & os.O_CREAT) or (flags & os.O_EXCL):
                    raise
                entry = _anchored_lstat(
                    parent_fd, parent_path, name, missing_ok=True,
                    parent_identity=parent_identity,
                )
                if entry is None or statmod.S_ISLNK(entry.st_mode):
                    raise
                return os.open(name, flags & ~os.O_CREAT, mode, dir_fd=parent_fd)
        identity = parent_identity
        if identity is None and parent_fd is not None:
            parent_status = os.fstat(parent_fd)
            identity = (parent_status.st_dev, parent_status.st_ino)
        _revalidate_directory_anchor(parent_path, identity)
        return os.open(str(parent_path / name), flags, mode)
    except FileExistsError:
        raise
    except OSError as exc:
        raise RegistryError("cannot open runtime file %s: %s" % (parent_path / name, exc)) from exc


def _anchored_lstat(parent_fd, parent_path, name, missing_ok=False,
                    parent_identity=None):
    try:
        if parent_fd is not None and _dir_fd_supported(os.stat):
            return os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        if parent_identity is not None:
            _revalidate_directory_anchor(parent_path, parent_identity)
        return os.lstat(parent_path / name)
    except FileNotFoundError:
        if missing_ok:
            return None
        raise RegistryError("runtime file does not exist: %s" % (parent_path / name))
    except OSError as exc:
        raise RegistryError("cannot inspect runtime file %s: %s" % (parent_path / name, exc)) from exc


def _validate_stream_fd(fd, parent_fd, parent_path, name, parent_identity=None):
    opened = os.fstat(fd)
    if not statmod.S_ISREG(opened.st_mode):
        raise RegistryError("event stream must be a regular file")
    if opened.st_nlink != 1:
        raise RegistryError("event stream must have exactly one hard link")
    entry = _anchored_lstat(
        parent_fd, parent_path, name, parent_identity=parent_identity,
    )
    if (statmod.S_ISLNK(entry.st_mode) or not statmod.S_ISREG(entry.st_mode)
            or (entry.st_dev, entry.st_ino) != (opened.st_dev, opened.st_ino)):
        raise RegistryError("event stream changed while it was opened")


def _read_bounded_runtime_file(path, label, max_bytes):
    """Read one stable regular single-link runtime file without following links."""
    parent_status = _lstat(path.parent, "%s parent" % label, missing_ok=True)
    if parent_status is None:
        return None
    if statmod.S_ISLNK(parent_status.st_mode) or not statmod.S_ISDIR(parent_status.st_mode):
        raise RegistryError("%s parent must be a real directory" % label)

    parent_fd, parent_identity = _open_directory_anchor(path.parent)
    fd = None
    try:
        entry = _anchored_lstat(
            parent_fd, path.parent, path.name, missing_ok=True,
            parent_identity=parent_identity,
        )
        if entry is None:
            return None
        if (statmod.S_ISLNK(entry.st_mode) or not statmod.S_ISREG(entry.st_mode)
                or entry.st_nlink != 1):
            raise RegistryError("%s must be a regular single-link file" % label)

        flags = (
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0)
        )
        fd = _open_anchored(
            parent_fd, path.parent, path.name, flags,
            parent_identity=parent_identity,
        )
        opened = os.fstat(fd)
        current = _anchored_lstat(
            parent_fd, path.parent, path.name,
            parent_identity=parent_identity,
        )
        if (not statmod.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or statmod.S_ISLNK(current.st_mode)
                or not statmod.S_ISREG(current.st_mode) or current.st_nlink != 1
                or (opened.st_dev, opened.st_ino) != (current.st_dev, current.st_ino)):
            raise RegistryError("%s changed while it was opened" % label)
        if opened.st_size > max_bytes:
            raise RegistryError("%s exceeds size limit" % label)

        before = (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
        data = bytearray()
        while len(data) <= max_bytes:
            chunk = os.read(fd, min(65_536, max_bytes + 1 - len(data)))
            if not chunk:
                break
            data.extend(chunk)
        if len(data) > max_bytes:
            raise RegistryError("%s exceeds size limit" % label)

        after = os.fstat(fd)
        _revalidate_directory_anchor(path.parent, parent_identity)
        current = _anchored_lstat(
            parent_fd, path.parent, path.name,
            parent_identity=parent_identity,
        )
        if (statmod.S_ISLNK(current.st_mode) or not statmod.S_ISREG(current.st_mode)
                or current.st_nlink != 1
                or (after.st_dev, after.st_ino) != (current.st_dev, current.st_ino)
                or before != (after.st_size, after.st_mtime_ns, after.st_ctime_ns)):
            raise RegistryError("%s changed while it was read" % label)
        return bytes(data)
    except OSError as exc:
        raise RegistryError("cannot read %s: %s" % (label, exc)) from exc
    finally:
        if fd is not None:
            os.close(fd)
        if parent_fd is not None:
            os.close(parent_fd)


@contextlib.contextmanager
def locked_stream(path, exclusive=True):
    if exclusive and not _safe_mutation_dirfd_available():
        raise RegistryError(
            "exclusive registry mutation requires safe dirfd-anchored filesystem operations"
        )
    parent_fd, parent_identity = _open_directory_anchor(path.parent)
    if exclusive:
        flags = os.O_RDWR | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0)
        mode = "r+"
    else:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        mode = "r"
    stream_preexisting = _anchored_lstat(
        parent_fd, path.parent, path.name, missing_ok=True,
        parent_identity=parent_identity,
    ) is not None
    try:
        fd = _open_anchored(
            parent_fd, path.parent, path.name, flags, 0o600,
            parent_identity=parent_identity,
        )
    except RegistryError:
        if parent_fd is not None:
            os.close(parent_fd)
        raise
    try:
        _validate_stream_fd(
            fd, parent_fd, path.parent, path.name, parent_identity,
        )
    except RegistryError:
        os.close(fd)
        if parent_fd is not None:
            os.close(parent_fd)
        raise
    if exclusive and not stream_preexisting and parent_fd is not None:
        # Make a freshly created stream's directory entry durable so a crash
        # cannot lose the whole new stream file.
        os.fsync(parent_fd)
    if exclusive:
        try:
            _secure_fd(fd, path, 0o600)
        except RegistryError:
            os.close(fd)
            if parent_fd is not None:
                os.close(parent_fd)
            raise
    handle = os.fdopen(fd, mode, encoding="utf-8")
    lock_name = path.name + ".lock"
    lock_path = path.parent / lock_name
    fallback_fd = None
    fallback_read_snapshot = None
    try:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
        elif exclusive:  # pragma: no cover - non-POSIX writer lock
            for _ in range(200):
                try:
                    fallback_fd = _open_anchored(
                        parent_fd, path.parent, lock_name,
                        os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0),
                        0o600, parent_identity=parent_identity,
                    )
                    break
                except FileExistsError:
                    time.sleep(0.05)
            if fallback_fd is None:
                raise RegistryError("timed out acquiring event lock")
        else:  # pragma: no cover - non-POSIX read without mutating lock state
            if _anchored_lstat(
                    parent_fd, path.parent, lock_name, missing_ok=True,
                    parent_identity=parent_identity) is not None:
                raise RegistryError("event stream is being written; retry the read")
            current = os.fstat(handle.fileno())
            fallback_read_snapshot = (current.st_size, current.st_mtime_ns)
        yield handle
        _revalidate_directory_anchor(path.parent, parent_identity)
        _validate_stream_fd(
            handle.fileno(), parent_fd, path.parent, path.name, parent_identity,
        )
        if fallback_read_snapshot is not None:
            current = os.fstat(handle.fileno())
            after = (current.st_size, current.st_mtime_ns)
            if (_anchored_lstat(
                    parent_fd, path.parent, lock_name, missing_ok=True,
                    parent_identity=parent_identity) is not None
                    or after != fallback_read_snapshot):
                raise RegistryError("event stream changed during unlocked read; retry")
    finally:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        if fallback_fd is not None:  # pragma: no cover
            os.close(fallback_fd)
            try:
                if parent_fd is not None and _dir_fd_supported(os.unlink):
                    os.unlink(lock_name, dir_fd=parent_fd)
                else:
                    _revalidate_directory_anchor(path.parent, parent_identity)
                    os.unlink(lock_path)
            except FileNotFoundError:
                pass
        handle.close()
        if parent_fd is not None:
            os.close(parent_fd)


def read_stream(handle, registry, root_hash, verify_authority=True):
    handle.seek(0)
    events = []
    previous_hash = "0" * 64
    seen_ids = set()
    seen_keys = set()
    seen_capabilities = set()
    line_number = 0
    while True:
        line_number += 1
        try:
            raw = handle.readline(MAX_EVENT_BYTES + 1)
        except UnicodeDecodeError as exc:
            raise RegistryError(
                "event stream is not valid UTF-8 at line %d" % line_number
            ) from exc
        if raw == "":
            break
        if len(raw.encode("utf-8")) > MAX_EVENT_BYTES:
            raise RegistryError("event line %d exceeds size limit" % line_number)
        if not raw.strip():
            raise RegistryError("blank line in event stream at %d" % line_number)
        try:
            event = strict_json_loads(raw, "event")
        except RegistryError as exc:
            raise RegistryError("invalid JSON at event line %d" % line_number) from exc
        if raw != canonical_json(event) + "\n":
            raise RegistryError("event line %d is not canonical JSON" % line_number)
        if not isinstance(event, dict) or set(event) - (REQUEST_FIELDS | ASSIGNED_EVENT_FIELDS):
            raise RegistryError("invalid event fields at line %d" % line_number)
        missing_assigned = ASSIGNED_EVENT_FIELDS - set(event)
        if missing_assigned:
            raise RegistryError("event line %d is missing assigned fields" % line_number)
        if event.get("registry") != registry:
            raise RegistryError("event line %d has wrong registry" % line_number)
        request = {key: event[key] for key in REQUEST_FIELDS if key in event}
        try:
            normalized = validate_request(registry, request)
            parse_datetime(event.get("recorded_at"), "recorded_at")
            validate_principal_attestation(
                registry, normalized, event.get("principal"),
                root_hash=root_hash, recorded_at=event.get("recorded_at"),
            )
        except RegistryError as exc:
            raise RegistryError("stored event is invalid at line %d: %s" % (line_number, exc)) from exc
        if event.get("request_hash") != sha256_json(normalized):
            raise RegistryError("event request hash mismatch at line %d" % line_number)
        principal = event["principal"]
        signed = principal.get("type") in {"host-capability", "safety-capability"}
        supplied_signature = event.get("authority_signature")
        if signed and not verify_authority:
            # Advisory read mode (pending_report only): the public hash chain,
            # offsets, request hashes, and principal bindings above have all
            # been checked; only the HMAC authority signature needs the host
            # key. A capability ID is still tracked so reuse stays visible.
            if (not isinstance(supplied_signature, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", supplied_signature)):
                raise RegistryError("event authority signature is malformed at line %d" % line_number)
            capability_id = principal["capability_id"]
            if capability_id in seen_capabilities:
                raise RegistryError("host capability was reused at line %d" % line_number)
            seen_capabilities.add(capability_id)
        elif signed:
            if (not isinstance(supplied_signature, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", supplied_signature)
                    or not hmac.compare_digest(supplied_signature, authority_signature(event))):
                raise RegistryError("event authority signature mismatch at line %d" % line_number)
            capability_id = principal["capability_id"]
            if capability_id in seen_capabilities:
                raise RegistryError("host capability was reused at line %d" % line_number)
            seen_capabilities.add(capability_id)
        elif supplied_signature is not None:
            raise RegistryError("untrusted event carries an authority signature at line %d" % line_number)
        if not isinstance(event.get("offset"), int) or isinstance(event.get("offset"), bool):
            raise RegistryError("event offset must be an integer at line %d" % line_number)
        if event.get("offset") != line_number:
            raise RegistryError("event offset discontinuity at line %d" % line_number)
        if event.get("previous_hash") != previous_hash:
            raise RegistryError("event hash chain mismatch at line %d" % line_number)
        if event.get("event_hash") != event_hash(event):
            raise RegistryError("event hash mismatch at line %d" % line_number)
        expected_id = str(uuid.uuid5(NAMESPACE, registry + ":" + str(event.get("idempotency_key"))))
        if event.get("event_id") != expected_id:
            raise RegistryError("event ID mismatch at line %d" % line_number)
        if event["event_id"] in seen_ids or event.get("idempotency_key") in seen_keys:
            raise RegistryError("duplicate event identity at line %d" % line_number)
        seen_ids.add(event["event_id"])
        seen_keys.add(event["idempotency_key"])
        previous_hash = event["event_hash"]
        events.append(event)
    return events


def new_projection(registry):
    return {
        "schema_version": SCHEMA_VERSION,
        "registry": registry,
        "last_offset": 0,
        "last_event_hash": "0" * 64,
        "records": {},
        "pending": {},
        "proposal_decisions": {},
    }


def current_record(state, aggregate_id):
    return state["records"].get(aggregate_id, {
        "revision": 0,
        "status": "active",
        "suppressed": False,
        "data": {},
        "last_event_id": None,
        "updated_at": None,
        "last_occurred_at": None,
        "last_source": None,
        "source_occurred_at": None,
        "last_suppressed_at": None,
        "last_suppression_source": None,
    })


def check_revision(event, record, expected=None):
    wanted = event.get("expected_revision") if expected is None else expected
    if wanted is not None and wanted != record["revision"]:
        raise RegistryError(
            "stale expected_revision for %s: expected %d, current %d"
            % (event["aggregate_id"], wanted, record["revision"])
        )


def apply_mutation(registry, state, event, operation, payload, expected_revision=None,
                   provenance=None):
    aggregate_id = event["aggregate_id"]
    record = json.loads(canonical_json(current_record(state, aggregate_id)))
    check_revision(event, record, expected_revision)
    terminal = record.get("status") in {"tombstoned", "erased"}
    consent_terminal_exception = (
        registry == "consent"
        and (
            operation == "suppress"
            or (operation == "restore" and record.get("status") == "erased")
        )
    )
    if terminal and not consent_terminal_exception:
        raise RegistryError(
            "%s record %s is terminal; use a new aggregate ID"
            % (record["status"], aggregate_id)
        )
    if operation == "restore" and (record["revision"] == 0 or not record.get("suppressed")):
        raise RegistryError("restore requires an existing suppressed consent record")
    if operation == "transition":
        transition = payload.get("transition")
        if not transition:
            raise RegistryError("transition payload is missing")
        current = record["data"].get("state")
        if current is None:
            raise RegistryError("governed state must be initialized once by owner upsert")
        if current != transition["from"]:
            raise RegistryError(
                "transition conflict for %s: expected state %r, current %r"
                % (aggregate_id, transition["from"], current)
            )
        graph = TRANSITION_GRAPHS.get(registry)
        if graph is not None and transition["to"] not in graph.get(current, set()):
            raise RegistryError(
                "invalid %s transition for %s: %r -> %r"
                % (registry, aggregate_id, current, transition["to"])
            )
        record["data"]["state"] = transition["to"]
    if operation == "upsert" and "state" in payload.get("set", {}):
        graph = TRANSITION_GRAPHS.get(registry)
        proposed_state = payload["set"]["state"]
        if graph is not None and (
                record["revision"] != 0 or proposed_state not in graph.get(None, set())):
            raise RegistryError(
                "%s state may be initialized once to %s; later changes require transition"
                % (registry, sorted(graph.get(None, set())))
            )
    if (operation == "upsert" and registry in TRANSITION_GRAPHS
            and record["revision"] == 0 and "state" not in payload.get("set", {})):
        raise RegistryError(
            "%s initial upsert must initialize state to %s"
            % (registry, sorted(TRANSITION_GRAPHS[registry].get(None, set())))
        )
    if registry in TRANSITION_GRAPHS and "state" in payload.get("unset", []):
        raise RegistryError("governed state cannot be unset or reinitialized")
    for key, value in payload.get("set", {}).items():
        record["data"][key] = value
    for key in payload.get("unset", []):
        record["data"].pop(key, None)
    if operation == "tombstone":
        record["status"] = "tombstoned"
    elif operation == "suppress":
        record["suppressed"] = True
        latest_withdrawal = record.get("last_suppressed_at")
        if (not latest_withdrawal
                or parse_datetime(event["occurred_at"], "occurred_at")
                > parse_datetime(latest_withdrawal, "record.last_suppressed_at")):
            record["last_suppressed_at"] = event["occurred_at"]
            record["last_suppression_source"] = event["source"]
        if record.get("status") not in {"erased", "tombstoned"}:
            record["data"]["subscription_status"] = "suppressed"
    elif operation == "restore":
        if record.get("last_occurred_at"):
            previous = parse_datetime(record["last_occurred_at"], "record.last_occurred_at")
            current = parse_datetime(event["occurred_at"], "occurred_at")
            if current <= previous:
                raise RegistryError("restore must occur after the current consent event")
        withdrawal_value = record.get("last_suppressed_at")
        if not withdrawal_value:
            raise RegistryError("restore requires a recorded withdrawal time")
        withdrawal = parse_datetime(withdrawal_value, "record.last_suppressed_at")
        basis_time = parse_datetime(event["source"]["observed_at"], "restore source.observed_at")
        restore_time = parse_datetime(event["occurred_at"], "occurred_at")
        if basis_time <= withdrawal:
            raise RegistryError("restore basis evidence must be newer than the withdrawal")
        if basis_time > restore_time:
            raise RegistryError("restore basis evidence cannot be dated after the restore event")
        record["suppressed"] = False
        record["status"] = "active"
    elif operation == "erase":
        record["data"] = {}
        record["status"] = "erased"
        if registry == "consent":
            record["suppressed"] = True
            latest_withdrawal = record.get("last_suppressed_at")
            if (not latest_withdrawal
                    or parse_datetime(event["occurred_at"], "occurred_at")
                    > parse_datetime(latest_withdrawal, "record.last_suppressed_at")):
                record["last_suppressed_at"] = event["occurred_at"]
                record["last_suppression_source"] = event["source"]
    record["revision"] += 1
    record["last_event_id"] = event["event_id"]
    record["updated_at"] = event["recorded_at"]
    record["last_occurred_at"] = event["occurred_at"]
    source_event = provenance or event
    record["last_source"] = source_event["source"]
    record["source_occurred_at"] = source_event["occurred_at"]
    state["records"][aggregate_id] = record


def project_events(registry, events):
    state = new_projection(registry)
    for event in events:
        operation = event["operation"]
        if operation == "propose":
            state["pending"][event["event_id"]] = {
                "aggregate_id": event["aggregate_id"],
                "proposed_operation": event["proposed_operation"],
                "payload": event.get("payload", {}),
                "expected_revision": event.get("expected_revision"),
                "source": event["source"],
                "occurred_at": event["occurred_at"],
                "actor": event["actor"],
                "event_id": event["event_id"],
            }
        elif operation in {"accept", "reject"}:
            proposal_id = event["proposal_event_id"]
            proposal = state["pending"].get(proposal_id)
            if proposal is None:
                raise RegistryError("proposal is missing or already resolved: %s" % proposal_id)
            if proposal["aggregate_id"] != event["aggregate_id"]:
                raise RegistryError("proposal aggregate_id does not match decision")
            if operation == "accept":
                apply_mutation(
                    registry, state, event, proposal["proposed_operation"], proposal["payload"],
                    proposal.get("expected_revision"), provenance=proposal,
                )
            state["proposal_decisions"][proposal_id] = {
                "decision": operation,
                "event_id": event["event_id"],
                "recorded_at": event["recorded_at"],
                "proposal_source": proposal["source"],
                "proposal_occurred_at": proposal["occurred_at"],
            }
            del state["pending"][proposal_id]
        else:
            apply_mutation(registry, state, event, operation, event.get("payload", {}))
        state["last_offset"] = event["offset"]
        state["last_event_hash"] = event["event_hash"]
    return state


def atomic_write_json(path, value):
    data = (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")
    parent_fd, parent_identity = _open_directory_anchor(path.parent)
    existing = _anchored_lstat(
        parent_fd, path.parent, path.name, missing_ok=True,
        parent_identity=parent_identity,
    )
    if existing is not None and (
            statmod.S_ISLNK(existing.st_mode) or not statmod.S_ISREG(existing.st_mode)
            or existing.st_nlink != 1):
        if parent_fd is not None:
            os.close(parent_fd)
        raise RegistryError("projection path must be a regular single-link file")
    temp_name = ".%s.registry-tmp" % path.name
    temp_path = path.parent / temp_name
    leftover = _anchored_lstat(
        parent_fd, path.parent, temp_name, missing_ok=True,
        parent_identity=parent_identity)
    if leftover is not None:
        # Every caller holds the exclusive stream lock, so an existing
        # temporary can only be dead-process residue; reclaim it instead of
        # permanently wedging the registry. Anything but a plain single-link
        # regular file is suspicious and still fails closed.
        if (statmod.S_ISLNK(leftover.st_mode) or not statmod.S_ISREG(leftover.st_mode)
                or leftover.st_nlink != 1):
            if parent_fd is not None:
                os.close(parent_fd)
            raise RegistryError(
                "projection temporary file is not a regular single-link file: %s" % temp_path)
        try:
            if parent_fd is not None and _dir_fd_supported(os.unlink):
                os.unlink(temp_name, dir_fd=parent_fd)
            else:
                os.unlink(temp_path)
        except OSError as exc:
            if parent_fd is not None:
                os.close(parent_fd)
            raise RegistryError(
                "cannot reclaim stale projection temporary file %s: %s" % (temp_path, exc)
            ) from exc
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = _open_anchored(
            parent_fd, path.parent, temp_name, flags, 0o600,
            parent_identity=parent_identity,
        )
    except FileExistsError as exc:
        if parent_fd is not None:
            os.close(parent_fd)
        raise RegistryError(
            "stale or concurrent projection temporary file exists: %s" % temp_path
        ) from exc
    except RegistryError:
        if parent_fd is not None:
            os.close(parent_fd)
        raise
    try:
        try:
            _secure_fd(fd, temp_path, 0o600)
        except RegistryError:
            os.close(fd)
            raise
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        _revalidate_directory_anchor(path.parent, parent_identity)
        if parent_fd is None or not _dir_fd_supported(os.rename):
            raise RegistryError(
                "projection install requires safe dirfd-anchored rename support"
            )
        os.rename(temp_name, path.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        installed = _anchored_lstat(
            parent_fd, path.parent, path.name, parent_identity=parent_identity,
        )
        if (not statmod.S_ISREG(installed.st_mode) or installed.st_nlink != 1):
            raise RegistryError("installed projection is not a regular single-link file")
        try:
            if parent_fd is not None:
                os.fsync(parent_fd)
        except OSError as exc:
            if os.name == "posix":
                raise RegistryError(
                    "cannot fsync projection directory %s: %s" % (path.parent, exc)
                ) from exc
    finally:
        try:
            if _anchored_lstat(
                    parent_fd, path.parent, temp_name, missing_ok=True,
                    parent_identity=parent_identity) is not None:
                if parent_fd is not None and _dir_fd_supported(os.unlink):
                    os.unlink(temp_name, dir_fd=parent_fd)
                else:  # pragma: no cover - Windows
                    _revalidate_directory_anchor(path.parent, parent_identity)
                    os.unlink(temp_path)
        finally:
            if parent_fd is not None:
                os.close(parent_fd)


def write_projections(registry, state, projection_path, suppressions_path):
    atomic_write_json(projection_path, state)
    if registry == "consent":
        suppressed = sorted(
            aggregate_id for aggregate_id, record in state["records"].items()
            if record.get("suppressed")
        )
        atomic_write_json(suppressions_path, {
            "schema_version": SCHEMA_VERSION,
            "registry": "consent",
            "last_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "suppressed": suppressed,
        })


def append_event(root, registry, request, capability_token=None):
    normalized = validate_request(registry, request)
    request_hash = sha256_json(normalized)
    root_hash = project_root_hash(root)
    # Reject invalid authority before creating runtime paths, then repeat the
    # complete verification while holding the exclusive append lock.
    authorize_request(registry, normalized, root_hash, capability_token)
    stream_path, projection_path, suppressions_path = memory_paths(root, registry, create=True)
    with locked_stream(stream_path, exclusive=True) as handle:
        events = read_stream(handle, registry, root_hash)
        principal = authorize_request(registry, normalized, root_hash, capability_token)
        existing = next((event for event in events
                         if event["idempotency_key"] == normalized["idempotency_key"]), None)
        if existing:
            if existing.get("request_hash") != request_hash:
                raise RegistryError("idempotency key was already used with different content")
            state = project_events(registry, events)
            write_projections(registry, state, projection_path, suppressions_path)
            return {"deduplicated": True, "event": existing,
                    "record": state["records"].get(existing["aggregate_id"])}

        if principal.get("type") in {"host-capability", "safety-capability"}:
            capability_id = principal["capability_id"]
            if any(
                    event["principal"].get("capability_id") == capability_id
                    for event in events
                    if isinstance(event.get("principal"), dict)):
                raise RegistryError("host capability has already been consumed")

        offset = len(events) + 1
        recorded_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
        event = dict(normalized)
        event.update({
            "registry": registry,
            "event_id": str(uuid.uuid5(NAMESPACE, registry + ":" + normalized["idempotency_key"])),
            "offset": offset,
            "recorded_at": recorded_at,
            "request_hash": request_hash,
            "previous_hash": events[-1]["event_hash"] if events else "0" * 64,
            "principal": principal,
            "authority_signature": None,
        })
        validate_principal_attestation(
            registry, normalized, principal, root_hash=root_hash, recorded_at=recorded_at,
        )
        if principal.get("type") in {"host-capability", "safety-capability"}:
            event["authority_signature"] = authority_signature(event)
        event["event_hash"] = event_hash(event)
        state = project_events(registry, events + [event])
        line = canonical_json(event) + "\n"
        if len(line.encode("utf-8")) > MAX_EVENT_BYTES:
            raise RegistryError("event exceeds size limit")
        handle.seek(0, os.SEEK_END)
        handle.write(line)
        handle.flush()
        os.fsync(handle.fileno())
        try:
            write_projections(registry, state, projection_path, suppressions_path)
        except Exception as exc:
            # The canonical event is already durable; the caller must repair
            # projections, never retry the append under a fresh idempotency key.
            raise RegistryError(
                "event_committed=true offset=%s event_id=%s: the canonical event is "
                "durably appended but projection install failed (%s); run "
                "`project %s` to repair — do not retry the append with a new "
                "idempotency key" % (event["offset"], event["event_id"], exc, registry)
            ) from exc
        return {"deduplicated": False, "event": event,
                "record": state["records"].get(event["aggregate_id"])}


def load_state(root, registry, create=False, verify_authority=True):
    if registry not in REGISTRIES:
        raise RegistryError("unknown registry: %s" % registry)
    stream_path, projection_path, suppressions_path = memory_paths(root, registry, create=create)
    stream_status = _lstat(stream_path, "event stream", missing_ok=True)
    if stream_status is None and not create:
        return new_projection(registry)
    root_hash = project_root_hash(root)
    with locked_stream(stream_path, exclusive=False) as handle:
        events = read_stream(handle, registry, root_hash, verify_authority=verify_authority)
        state = project_events(registry, events)
    return state


def rebuild_projection(root, registry):
    stream_path, projection_path, suppressions_path = memory_paths(root, registry, create=True)
    root_hash = project_root_hash(root)
    # Use the writer lock on every platform. On hosts without shared locks this
    # prevents an old unlocked snapshot from being installed before its race is noticed.
    with locked_stream(stream_path, exclusive=True) as handle:
        events = read_stream(handle, registry, root_hash)
        state = project_events(registry, events)
        write_projections(registry, state, projection_path, suppressions_path)
    return state


def get_record(root, registry, aggregate_id):
    if not SAFE_ID.fullmatch(aggregate_id) or "@" in aggregate_id:
        raise RegistryError("aggregate_id must be a safe pseudonymous identifier")
    return load_state(root, registry)["records"].get(aggregate_id)


def is_suppressed(root, aggregate_id):
    record = get_record(root, "consent", aggregate_id)
    return bool(record and record.get("suppressed"))


def _observed_age_days(value, now):
    """Whole days between a timezone-aware occurred_at and now."""
    try:
        parsed = parse_datetime(value, "occurred_at")
    except RegistryError:
        return None
    return max(0, (now - parsed).days)


def pending_report(root, now=None):
    """Read-only cross-registry intake/lag report. Never creates runtime paths.

    Per registry: pending proposal count, the oldest pending proposal's
    occurred_at and age in days, plus an explicit projection status. A valid
    projection is current, behind, or ahead; an absent projection is either
    not-required for an empty stream or missing for a non-empty stream; malformed
    or unreadable projections are invalid. ``projection_lag`` remains a
    backward-compatible non-negative value only for current/behind projections.
    When the host authority key is
    available the stream is fully verified (authority_verified: true); without
    it the report falls back to the publicly verifiable structure — canonical
    JSON, offsets, hash chain, request hashes, principal bindings — and labels
    the entry authority_verified: false. The pending signal is advisory (a
    user-facing nudge), never an authorization input, so a signature-skipped
    read cannot widen authority. A stream that cannot be parsed at all is
    reported as unverifiable rather than as zero-pending.
    """
    now = now or dt.datetime.now(dt.timezone.utc)
    authority_verified = bool(os.environ.get(HOST_KEY_ENV))
    registries = {}
    total = 0
    for registry in sorted(REGISTRIES):
        entry = {"verifiable": True, "authority_verified": authority_verified,
                 "pending": 0,
                 "oldest_pending_occurred_at": None, "oldest_pending_age_days": None,
                 "stream_offset": 0, "projection_offset": None,
                 "projection_lag": None, "projection_status": "unknown"}
        try:
            state = load_state(root, registry, create=False,
                               verify_authority=authority_verified)
        except RegistryError as exc:
            entry["verifiable"] = False
            entry["error"] = str(exc)
            registries[registry] = entry
            continue
        pending = list(state["pending"].values())
        entry["pending"] = len(pending)
        entry["stream_offset"] = state["last_offset"]
        if pending:
            oldest = min(
                pending,
                key=lambda item: parse_datetime(item["occurred_at"], "occurred_at"),
            )
            entry["oldest_pending_occurred_at"] = oldest["occurred_at"]
            entry["oldest_pending_age_days"] = _observed_age_days(oldest["occurred_at"], now)
        try:
            _, projection_path, _ = memory_paths(root, registry, create=False)
            projection_bytes = _read_bounded_runtime_file(
                projection_path, "projection", MAX_EVENT_BYTES,
            )
            if projection_bytes is None:
                entry["projection_status"] = (
                    "not-required" if state["last_offset"] == 0 else "missing"
                )
                total += len(pending)
                registries[registry] = entry
                continue
            try:
                raw_projection = projection_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise RegistryError("projection must be UTF-8 JSON") from exc
        except RegistryError as exc:
            entry["projection_status"] = "invalid"
            entry["projection_error"] = "cannot read projection: %s" % exc
        else:
            try:
                stored = strict_json_loads(raw_projection, "projection")
                if not isinstance(stored, dict):
                    raise RegistryError("projection must be a JSON object")
                if stored.get("schema_version") != SCHEMA_VERSION:
                    raise RegistryError("projection has an unsupported schema_version")
                if stored.get("registry") != registry:
                    raise RegistryError("projection has the wrong registry")
                stored_offset = stored.get("last_offset")
                if (not isinstance(stored_offset, int)
                        or isinstance(stored_offset, bool) or stored_offset < 0):
                    raise RegistryError("projection last_offset must be a non-negative integer")
            except RegistryError as exc:
                entry["projection_status"] = "invalid"
                entry["projection_error"] = str(exc)
            else:
                entry["projection_offset"] = stored_offset
                delta = state["last_offset"] - stored_offset
                if delta > 0:
                    entry["projection_status"] = "behind"
                    entry["projection_lag"] = delta
                elif delta < 0:
                    entry["projection_status"] = "ahead"
                else:
                    entry["projection_status"] = "current"
                    entry["projection_lag"] = 0
        total += len(pending)
        registries[registry] = entry
    return {"registries": registries, "total_pending": total,
            "authority_verified": authority_verified}


def load_request(path):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise RegistryError("cannot read event request: %s" % exc) from exc
    if len(raw) > MAX_EVENT_BYTES:
        raise RegistryError("event request exceeds size limit")
    try:
        return strict_json_loads(raw.decode("utf-8"), "event request")
    except (UnicodeDecodeError, RegistryError) as exc:
        raise RegistryError("event request must be UTF-8 JSON") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=os.getcwd(), help="Project root containing memory/.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    append = sub.add_parser("append")
    append.add_argument("registry", choices=sorted(REGISTRIES))
    append.add_argument("event_json")
    owner_append = sub.add_parser(
        "owner-append",
        help="Append a canonical owner event using a host-injected capability.",
    )
    owner_append.add_argument("registry", choices=sorted(REGISTRIES))
    owner_append.add_argument("event_json")
    safety_append = sub.add_parser(
        "safety-append",
        help="Append one host-verified data-subject consent erasure.",
    )
    safety_append.add_argument("registry", choices=["consent"])
    safety_append.add_argument("event_json")
    verify = sub.add_parser("verify")
    verify.add_argument("registry", choices=sorted(REGISTRIES))
    project = sub.add_parser("project")
    project.add_argument("registry", choices=sorted(REGISTRIES))
    get = sub.add_parser("get")
    get.add_argument("registry", choices=sorted(REGISTRIES))
    get.add_argument("aggregate_id")
    suppressed = sub.add_parser("is-suppressed")
    suppressed.add_argument("aggregate_id")
    sub.add_parser(
        "pending",
        help="Read-only cross-registry pending-proposal and projection-lag report.",
    )
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            for registry in sorted(REGISTRIES):
                memory_paths(args.root, registry, create=True)
            result = {"initialized": True, "registries": sorted(REGISTRIES)}
        elif args.command == "append":
            result = append_event(args.root, args.registry, load_request(args.event_json))
        elif args.command in {"owner-append", "safety-append"}:
            capability = os.environ.get(HOST_CAPABILITY_ENV)
            if not capability:
                raise RegistryError(
                    "%s requires a host-injected %s" % (args.command, HOST_CAPABILITY_ENV)
                )
            request = load_request(args.event_json)
            if args.command == "safety-append" and not (
                    request.get("operation") == "erase"
                    and request.get("authorized_by") == "data-subject"):
                raise RegistryError("safety-append is limited to data-subject consent erase")
            normalized = validate_request(args.registry, request)
            principal = verify_host_capability(
                capability, args.registry, normalized, project_root_hash(args.root),
            )
            expected_principal = (
                "safety-capability" if args.command == "safety-append"
                else "host-capability"
            )
            if principal.get("type") != expected_principal:
                raise RegistryError(
                    "%s requires a %s" % (args.command, expected_principal)
                )
            result = append_event(
                args.root, args.registry, normalized,
                capability_token=capability,
            )
        elif args.command == "verify":
            state = load_state(args.root, args.registry, create=False)
            result = {"valid": True, "registry": args.registry,
                      "last_offset": state["last_offset"], "records": len(state["records"]),
                      "pending": len(state["pending"])}
        elif args.command == "project":
            state = rebuild_projection(args.root, args.registry)
            result = {"projected": True, "registry": args.registry,
                      "last_offset": state["last_offset"]}
        elif args.command == "get":
            result = {"registry": args.registry, "aggregate_id": args.aggregate_id,
                      "record": get_record(args.root, args.registry, args.aggregate_id)}
        elif args.command == "pending":
            result = pending_report(args.root)
        else:
            result = {"aggregate_id": args.aggregate_id,
                      "suppressed": is_suppressed(args.root, args.aggregate_id)}
    except RegistryError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
