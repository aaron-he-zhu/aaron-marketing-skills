#!/usr/bin/env python3
"""Proposal-only, evidence-bound audit remediation loop.

This runtime coordinates a bounded FIX -> intervention -> re-audit cycle.  It
never executes a remediation and never authorizes an external mutation.  Every
transition is an immutable, private JSON step under
``memory/runs/<run-id>/loops/<loop-id>/``.

Typical flow::

    start -> acquire-lease -> proposal -> acquire-lease -> owner
          -> acquire-lease -> intervention -> acquire-lease -> reaudit

Use ``advance`` after a FIX re-audit enters ``next``.  Use ``retry`` to record a
bounded retry schedule; the command reports deterministic backoff metadata and
does not sleep.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time
import uuid


ROOT = Path(__file__).resolve().parents[1]


def _load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load runtime module: %s" % path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


runtime = _load_module("audit_loop_run_events", ROOT / "scripts" / "run-events.py")
audit_validator = _load_module(
    "audit_loop_artifact_validator", ROOT / "scripts" / "validate-audit-artifact.py"
)

SCHEMA_VERSION = "2.0"
ZERO_HASH = "0" * 64
MAX_STEPS = 128
MAX_RETRIES = 10
MAX_AUDIT_BYTES = 1_000_000
MAX_EVIDENCE_BYTES = 10_000_000
LEASE_MIN_SECONDS = 30
LEASE_MAX_SECONDS = 900
BACKOFF_MAX_SECONDS = 32
NAMESPACE = uuid.UUID("986edcad-bdf7-46bf-b09e-88d7811b9933")
STEP_NAME = re.compile(
    r"^(\d{3})-(start|lease-acquired|proposal-recorded|owner-accepted|"
    r"owner-rejected|intervention-recorded|reaudit-recorded|cycle-advanced|retry-scheduled|"
    r"retry-exhausted|deadline-expired)\.json$"
)
RESIDUE_NAME = re.compile(r"^\.(\d{3}-.+\.json)\.run-create$")
ACTIVE_STATES = {
    "awaiting-proposal", "awaiting-owner", "awaiting-intervention",
    "awaiting-reaudit", "next",
}
TERMINAL_STATES = {"converged", "exhausted", "gate-blocked", "needs-input"}
ALL_STATES = ACTIVE_STATES | TERMINAL_STATES
LEASED_ACTIONS = {"proposal", "owner", "intervention", "reaudit", "advance", "retry"}
SUPPORTED_ACTIONS = {"start", "acquire-lease", *LEASED_ACTIONS}


class AuditLoopError(ValueError):
    pass


def _translate_error(exc):
    if isinstance(exc, AuditLoopError):
        return exc
    return AuditLoopError(str(exc))


def canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise AuditLoopError("value must be finite JSON: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def parse_time(value, label):
    try:
        parsed = runtime.parse_datetime(value, label)
    except Exception as exc:
        raise _translate_error(exc) from exc
    return parsed.astimezone(dt.timezone.utc)


def iso_time(value):
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def validate_sha(value, label):
    try:
        return runtime.validate_sha(value, label)
    except Exception as exc:
        raise _translate_error(exc) from exc


def validate_uuid(value, label):
    try:
        return runtime.validate_uuid(value, label)
    except Exception as exc:
        raise _translate_error(exc) from exc


def validate_safe_id(value, label):
    try:
        return runtime.validate_safe_id(value, label)
    except Exception as exc:
        raise _translate_error(exc) from exc


def validate_ref(value, label):
    try:
        return runtime.validate_ref(value, label)
    except Exception as exc:
        raise _translate_error(exc) from exc


def _bounded_integer(value, label, minimum, maximum):
    if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
        raise AuditLoopError("%s must be an integer between %d and %d" % (
            label, minimum, maximum,
        ))
    return value


def _stable_bytes(root, reference, maximum, label, expected_sha=None):
    validate_ref(reference, label + " ref")
    try:
        path, raw, metadata = runtime._stable_project_read(root, reference, maximum, label)
    except Exception as exc:
        raise _translate_error(exc) from exc
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha is not None:
        validate_sha(expected_sha, label + " sha256")
        if digest != expected_sha:
            raise AuditLoopError("%s hash mismatch: %s" % (label, reference))
    return path, raw, metadata, digest


def _validate_exact_audit(root, reference, expected_sha, label):
    """Validate a private copy of the exact bytes read from the project tree."""
    _path, raw, _metadata, digest = _stable_bytes(
        root, reference, MAX_AUDIT_BYTES, label, expected_sha,
    )
    descriptor, temporary = tempfile.mkstemp(prefix="aaron-audit-loop-", suffix=".md")
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        relative_path = reference if reference.startswith("memory/audits/") else None
        record, errors = audit_validator.validate(Path(temporary), relative_path)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    if errors:
        raise AuditLoopError("%s is invalid: %s" % (label, "; ".join(errors)))
    if not isinstance(record, dict) or record.get("framework") == "MULTI":
        raise AuditLoopError("%s must be one concrete auditor-gate artifact" % label)
    context = record.get("context")
    if not isinstance(context, dict) or not context:
        raise AuditLoopError("%s must contain typed context" % label)
    identity = {
        "ref": reference,
        "sha256": digest,
        "schema_version": record["schema_version"],
        "runbook_version": record["runbook_version"],
        "catalog_version": record["catalog_version"],
        "framework": record["framework"],
        "profile": record["profile"],
        "target": record["target"],
        "observed_at": record["observed_at"],
        "target_identity_sha256": sha256_json({
            "framework": record["framework"],
            "profile": record["profile"],
            "target": record["target"],
        }),
        "context_sha256": sha256_json(context),
        "status": record["status"],
        "verdict": record["verdict"],
        "score_state": record["score_state"],
        "evidence_coverage": record["evidence_coverage"],
        "score_confidence": record["score_confidence"],
        "raw_overall_score": record.get("raw_overall_score"),
        "final_overall_score": record.get("final_overall_score"),
    }
    return identity


def _verify_evidence(root, reference, expected_sha, label):
    _path, _raw, metadata, digest = _stable_bytes(
        root, reference, MAX_EVIDENCE_BYTES, label, expected_sha,
    )
    if metadata.st_size <= 0:
        raise AuditLoopError("%s must not be empty" % label)
    return {"ref": reference, "sha256": digest, "bytes": metadata.st_size}


def _ensure_loop_directory(root, run_id, loop_id):
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    parent_fd = None
    child_fd = None
    try:
        _stream, _projection, run_dir = runtime.run_paths(root, run_id, create=True)
        loops_dir = Path(runtime.ensure_child_directories(root, run_dir, ["loops"]))
        loop_dir = loops_dir / loop_id
        runtime.ensure_ignored(root, [loop_dir / ".loop.lock"])
        parent_fd, parent_identity = runtime.open_directory_anchor(loops_dir)
        try:
            os.mkdir(loop_id, mode=0o700, dir_fd=parent_fd)
        except FileExistsError as exc:
            # The earlier absence check is advisory. Only mkdirat success gives
            # this invocation cleanup ownership over the new UUID directory.
            entry = runtime.anchored_lstat(
                parent_fd, loops_dir, loop_id, missing_ok=True,
            )
            if (entry is None or stat.S_ISLNK(entry.st_mode)
                    or not stat.S_ISDIR(entry.st_mode)):
                raise AuditLoopError("loop path appeared concurrently and is unsafe") from exc
            raise AuditLoopError("loop directory appeared concurrently; retry") from exc
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        child_fd = os.open(loop_id, flags, dir_fd=parent_fd)
        os.fchmod(child_fd, 0o700)
        metadata = os.fstat(child_fd)
        entry = runtime.anchored_lstat(parent_fd, loops_dir, loop_id)
        if ((entry.st_dev, entry.st_ino) != (metadata.st_dev, metadata.st_ino)
                or stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode)):
            raise AuditLoopError("new loop directory identity changed during creation")
        runtime.revalidate_anchor(parent_fd, loops_dir, parent_identity)
        os.fsync(parent_fd)
        return loop_dir, (metadata.st_dev, metadata.st_ino)
    except Exception as exc:
        raise _translate_error(exc) from exc
    finally:
        if child_fd is not None:
            os.close(child_fd)
        if parent_fd is not None:
            os.close(parent_fd)


def _loop_directory(root, run_id, loop_id):
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    try:
        root_path = runtime.normalized_root(root)
    except Exception as exc:
        raise _translate_error(exc) from exc
    loop_dir = root_path / "memory" / "runs" / run_id / "loops" / loop_id
    try:
        metadata = os.lstat(loop_dir)
    except OSError as exc:
        raise AuditLoopError("loop does not exist: %s" % loop_id) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise AuditLoopError("loop directory must be a real directory")
    return loop_dir


def _step_ref(root, path):
    root_path = runtime.normalized_root(root)
    try:
        return Path(os.path.abspath(path)).relative_to(root_path).as_posix()
    except ValueError as exc:
        raise AuditLoopError("loop step escapes project root") from exc


def _read_step(root, reference):
    _path, raw, metadata, digest = _stable_bytes(
        root, reference, runtime.MAX_DOCUMENT_BYTES, "loop step",
    )
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise AuditLoopError("loop step must use private file mode 0600")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise AuditLoopError("loop step must be UTF-8") from exc
    try:
        document = runtime.strict_json_loads(text, "loop step")
    except Exception as exc:
        raise _translate_error(exc) from exc
    if not isinstance(document, dict):
        raise AuditLoopError("loop step must be an object")
    return document, digest, len(raw)


def _parse_audit_date(value, label):
    if not isinstance(value, str):
        raise AuditLoopError("%s must be an ISO date" % label)
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise AuditLoopError("%s must be an ISO date" % label) from exc
    if parsed.isoformat() != value:
        raise AuditLoopError("%s must be an ISO date" % label)
    return parsed


def _validate_audit_identity(value, label):
    required = {
        "ref", "sha256", "schema_version", "runbook_version", "catalog_version",
        "framework", "profile", "target", "observed_at", "target_identity_sha256",
        "context_sha256", "status", "verdict", "score_state", "evidence_coverage",
        "score_confidence", "raw_overall_score", "final_overall_score",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AuditLoopError("%s has invalid fields" % label)
    validate_ref(value["ref"], label + ".ref")
    for name in ("sha256", "target_identity_sha256", "context_sha256"):
        validate_sha(value[name], label + "." + name)
    for name in (
        "schema_version", "runbook_version", "catalog_version", "framework", "profile",
        "target", "status", "verdict", "score_state", "score_confidence",
    ):
        if not isinstance(value[name], str) or not value[name]:
            raise AuditLoopError("%s.%s must be a non-empty string" % (label, name))
    _parse_audit_date(value["observed_at"], label + ".observed_at")
    _bounded_integer(value["evidence_coverage"], label + ".evidence_coverage", 0, 100)
    for name in ("raw_overall_score", "final_overall_score"):
        if value[name] is not None:
            _bounded_integer(value[name], label + "." + name, 0, 100)


def _validate_lease(value, label):
    required = {
        "generation", "active", "owner", "token_sha256", "acquired_at",
        "expires_at", "released_at",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise AuditLoopError("%s has invalid fields" % label)
    _bounded_integer(value["generation"], label + ".generation", 0, MAX_STEPS)
    if not isinstance(value["active"], bool):
        raise AuditLoopError("%s.active must be boolean" % label)
    optional = ("owner", "token_sha256", "acquired_at", "expires_at", "released_at")
    if value["generation"] == 0:
        if value["active"] or any(value[name] is not None for name in optional):
            raise AuditLoopError("generation-zero lease must be empty and inactive")
        return
    if value["owner"] is None or value["token_sha256"] is None:
        raise AuditLoopError("nonzero lease requires owner and token hash")
    validate_safe_id(value["owner"], label + ".owner")
    validate_sha(value["token_sha256"], label + ".token_sha256")
    acquired = parse_time(value["acquired_at"], label + ".acquired_at")
    expires = parse_time(value["expires_at"], label + ".expires_at")
    if expires <= acquired:
        raise AuditLoopError("lease expiry must follow acquisition")
    ttl = (expires - acquired).total_seconds()
    if not LEASE_MIN_SECONDS <= ttl <= LEASE_MAX_SECONDS:
        raise AuditLoopError("lease TTL must be between %d and %d seconds" % (
            LEASE_MIN_SECONDS, LEASE_MAX_SECONDS,
        ))
    if value["active"]:
        if value["released_at"] is not None:
            raise AuditLoopError("active lease cannot have released_at")
    else:
        released = parse_time(value["released_at"], label + ".released_at")
        if released < acquired:
            raise AuditLoopError("lease release cannot precede acquisition")


def _empty_lease():
    return {
        "generation": 0, "active": False, "owner": None, "token_sha256": None,
        "acquired_at": None, "expires_at": None, "released_at": None,
    }


def _validate_step(
        document, sequence, run_id, loop_id, prior, prior_ref, prior_sha,
        intervention_occurred_at=None):
    required = {
        "schema_version", "run_id", "loop_id", "transition_id", "sequence",
        "transition", "from_state", "state", "run_parent_event_id",
        "run_parent_event_sha256", "cycle", "max_cycles", "total_retries",
        "state_retries", "max_retries", "backoff_seconds", "retry_not_before",
        "deadline", "occurred_at", "recorded_at", "idempotency_key", "request_hash",
        "previous_step_ref", "previous_step_sha256", "expected_previous_sha256",
        "proposal_only", "external_mutation_authorized", "baseline_audit", "latest_audit",
        "proposal", "owner", "intervention", "reason_code", "lease",
    }
    if set(document) != required:
        raise AuditLoopError("loop step %d has invalid fields" % sequence)
    if document["schema_version"] != SCHEMA_VERSION:
        raise AuditLoopError("loop step schema_version must be %s" % SCHEMA_VERSION)
    if document["run_id"] != run_id or document["loop_id"] != loop_id:
        raise AuditLoopError("loop step identity mismatch")
    if document["sequence"] != sequence:
        raise AuditLoopError("loop step sequence mismatch")
    validate_uuid(document["transition_id"], "transition_id")
    validate_safe_id(document["idempotency_key"], "idempotency_key")
    validate_sha(document["request_hash"], "request_hash")
    expected_id = str(uuid.uuid5(NAMESPACE, loop_id + ":" + document["idempotency_key"]))
    if document["transition_id"] != expected_id:
        raise AuditLoopError("transition ID mismatch")
    if document["state"] not in ALL_STATES:
        raise AuditLoopError("unsupported loop state")
    if document["from_state"] is not None and document["from_state"] not in ALL_STATES:
        raise AuditLoopError("unsupported previous loop state")
    validate_uuid(document["run_parent_event_id"], "run_parent_event_id")
    validate_sha(document["run_parent_event_sha256"], "run_parent_event_sha256")
    _bounded_integer(document["cycle"], "cycle", 1, 3)
    _bounded_integer(document["max_cycles"], "max_cycles", 1, 3)
    if document["cycle"] > document["max_cycles"]:
        raise AuditLoopError("cycle exceeds max_cycles")
    _bounded_integer(document["total_retries"], "total_retries", 0, MAX_STEPS)
    _bounded_integer(document["state_retries"], "state_retries", 0, MAX_RETRIES + 1)
    _bounded_integer(document["max_retries"], "max_retries", 0, MAX_RETRIES)
    _bounded_integer(document["backoff_seconds"], "backoff_seconds", 0, BACKOFF_MAX_SECONDS)
    parse_time(document["deadline"], "deadline")
    parse_time(document["occurred_at"], "occurred_at")
    parse_time(document["recorded_at"], "recorded_at")
    if document["recorded_at"] != document["occurred_at"]:
        raise AuditLoopError("recorded_at must preserve the deterministic occurrence time")
    if document["retry_not_before"] is not None:
        parse_time(document["retry_not_before"], "retry_not_before")
    if document["proposal_only"] is not True or document["external_mutation_authorized"] is not False:
        raise AuditLoopError("loop steps must remain proposal-only without external mutation authority")
    _validate_audit_identity(document["baseline_audit"], "baseline_audit")
    _validate_audit_identity(document["latest_audit"], "latest_audit")
    _validate_lease(document["lease"], "lease")
    for name in ("proposal", "intervention"):
        item = document[name]
        if item is not None:
            if not isinstance(item, dict) or set(item) != {"ref", "sha256", "bytes"}:
                raise AuditLoopError("%s evidence has invalid fields" % name)
            validate_ref(item["ref"], name + ".ref")
            validate_sha(item["sha256"], name + ".sha256")
            _bounded_integer(item["bytes"], name + ".bytes", 1, MAX_EVIDENCE_BYTES)
    if document["owner"] is not None:
        validate_safe_id(document["owner"], "owner")
    validate_safe_id(document["reason_code"], "reason_code")

    if sequence == 1:
        if document["transition"] != "start" or document["from_state"] is not None:
            raise AuditLoopError("first loop step must be start")
        if document["previous_step_ref"] is not None:
            raise AuditLoopError("first loop step cannot have previous_step_ref")
        if document["previous_step_sha256"] != ZERO_HASH:
            raise AuditLoopError("first loop step must begin the hash chain")
        if document["cycle"] != 1 or document["total_retries"] != 0 or document["state_retries"] != 0:
            raise AuditLoopError("loop start counters are invalid")
        if document["baseline_audit"] != document["latest_audit"]:
            raise AuditLoopError("loop start latest audit must equal its baseline")
        if any(document[name] is not None for name in ("proposal", "owner", "intervention")):
            raise AuditLoopError("loop start cannot contain workflow payloads")
        if document["lease"] != _empty_lease():
            raise AuditLoopError("loop start cannot hold a lease")
    else:
        if prior["state"] in TERMINAL_STATES:
            raise AuditLoopError("terminal loop step cannot have a successor")
        if document["from_state"] != prior["state"]:
            raise AuditLoopError("loop state chain mismatch")
        if parse_time(document["occurred_at"], "occurred_at") < parse_time(
                prior["occurred_at"], "prior.occurred_at"):
            raise AuditLoopError("loop step occurred_at cannot precede its predecessor")
        if document["previous_step_ref"] != prior_ref:
            raise AuditLoopError("previous loop step reference mismatch")
        if document["previous_step_sha256"] != prior_sha:
            raise AuditLoopError("loop step hash chain mismatch")
        if document["max_cycles"] != prior["max_cycles"] or document["max_retries"] != prior["max_retries"]:
            raise AuditLoopError("loop bounds cannot change")
        if document["deadline"] != prior["deadline"]:
            raise AuditLoopError("loop deadline cannot change")
        if document["baseline_audit"] != prior["baseline_audit"]:
            raise AuditLoopError("baseline audit identity cannot change")
        if document["lease"]["generation"] < prior["lease"]["generation"]:
            raise AuditLoopError("lease generation moved backwards")

    if document["expected_previous_sha256"] != document["previous_step_sha256"]:
        raise AuditLoopError("optimistic concurrency hash was not preserved")
    allowed = {
        "start": (None, "awaiting-proposal"),
        "proposal-recorded": ("awaiting-proposal", "awaiting-owner"),
        "owner-accepted": ("awaiting-owner", "awaiting-intervention"),
        "owner-rejected": ("awaiting-owner", "needs-input"),
        "intervention-recorded": ("awaiting-intervention", "awaiting-reaudit"),
        "cycle-advanced": ("next", "awaiting-proposal"),
    }
    if document["transition"] in allowed:
        expected_from, expected_to = allowed[document["transition"]]
        if document["from_state"] != expected_from or document["state"] != expected_to:
            raise AuditLoopError("invalid %s state transition" % document["transition"])
    elif document["transition"] == "lease-acquired":
        if document["state"] != document["from_state"] or not document["lease"]["active"]:
            raise AuditLoopError("lease acquisition must preserve state and activate a lease")
    elif document["transition"] == "retry-scheduled":
        if document["state"] != document["from_state"] or document["backoff_seconds"] <= 0:
            raise AuditLoopError("retry scheduling must preserve state and set backoff")
    elif document["transition"] in {"retry-exhausted", "deadline-expired"}:
        if document["state"] != "exhausted":
            raise AuditLoopError("budget/deadline transition must enter exhausted")
    elif document["transition"] == "reaudit-recorded":
        if document["from_state"] != "awaiting-reaudit" or document["state"] not in {
            "converged", "next", "exhausted", "gate-blocked", "needs-input",
        }:
            raise AuditLoopError("invalid re-audit state transition")
    else:
        raise AuditLoopError("unsupported transition")

    if prior is None:
        return
    transition = document["transition"]
    if transition == "lease-acquired":
        if document["lease"]["generation"] != prior["lease"]["generation"] + 1:
            raise AuditLoopError("lease acquisition must increment the fencing generation")
        for name in (
            "cycle", "total_retries", "state_retries", "retry_not_before",
            "baseline_audit", "latest_audit", "proposal", "owner", "intervention",
        ):
            if document[name] != prior[name]:
                raise AuditLoopError("lease acquisition changed protected field: %s" % name)
    else:
        if document["lease"]["generation"] != prior["lease"]["generation"]:
            raise AuditLoopError("business transition changed the fencing generation")
        if document["lease"]["generation"] and document["lease"]["active"]:
            raise AuditLoopError("business transition must release its lease")
        for name in ("owner", "token_sha256", "acquired_at", "expires_at"):
            if document["lease"][name] != prior["lease"][name]:
                raise AuditLoopError("business transition changed lease identity: %s" % name)
        if document["lease"]["generation"] and document["lease"]["released_at"] != document["occurred_at"]:
            raise AuditLoopError("business transition must record immediate lease release")
        if transition != "deadline-expired" and not prior["lease"]["active"]:
            raise AuditLoopError("business transition lacks an active predecessor lease")

    if transition == "proposal-recorded":
        if prior["proposal"] is not None or document["proposal"] is None:
            raise AuditLoopError("proposal transition must install the first proposal evidence")
        for name in ("cycle", "total_retries", "baseline_audit", "latest_audit"):
            if document[name] != prior[name]:
                raise AuditLoopError("proposal transition changed protected field: %s" % name)
        if document["owner"] is not None or document["intervention"] is not None:
            raise AuditLoopError("proposal transition cannot pre-populate later workflow stages")
    elif transition in {"owner-accepted", "owner-rejected"}:
        if document["owner"] is None or document["proposal"] != prior["proposal"]:
            raise AuditLoopError("owner transition must preserve a proposal and record one owner")
        for name in (
            "cycle", "total_retries", "baseline_audit", "latest_audit", "intervention",
        ):
            if document[name] != prior[name]:
                raise AuditLoopError("owner transition changed protected field: %s" % name)
        expected_reason = transition
        if document["reason_code"] != expected_reason:
            raise AuditLoopError("owner transition reason_code must match its typed decision")
    elif transition == "intervention-recorded":
        if document["intervention"] is None:
            raise AuditLoopError("intervention transition requires evidence")
        for name in (
            "cycle", "total_retries", "baseline_audit", "latest_audit", "proposal", "owner",
        ):
            if document[name] != prior[name]:
                raise AuditLoopError("intervention transition changed protected field: %s" % name)
    elif transition == "reaudit-recorded":
        if document["latest_audit"]["sha256"] == prior["latest_audit"]["sha256"]:
            raise AuditLoopError("re-audit transition did not install distinct audit bytes")
        if document["latest_audit"]["target_identity_sha256"] != document["baseline_audit"]["target_identity_sha256"]:
            raise AuditLoopError("stored re-audit target identity mismatch")
        latest_observed = _parse_audit_date(
            document["latest_audit"]["observed_at"], "latest_audit.observed_at",
        )
        baseline_observed = _parse_audit_date(
            document["baseline_audit"]["observed_at"], "baseline_audit.observed_at",
        )
        if latest_observed <= baseline_observed:
            raise AuditLoopError("re-audit observed_at must follow the baseline audit date")
        if intervention_occurred_at is None:
            raise AuditLoopError("re-audit chain is missing intervention occurrence time")
        intervention_date = parse_time(
            intervention_occurred_at, "intervention.occurred_at",
        ).date()
        if latest_observed < intervention_date:
            raise AuditLoopError("re-audit observed_at cannot precede the intervention date")
        for name in ("cycle", "total_retries", "proposal", "owner", "intervention"):
            if document[name] != prior[name]:
                raise AuditLoopError("re-audit transition changed protected field: %s" % name)
    elif transition == "cycle-advanced":
        if document["cycle"] != prior["cycle"] + 1:
            raise AuditLoopError("cycle advance must increment cycle exactly once")
        if any(document[name] is not None for name in ("proposal", "owner", "intervention")):
            raise AuditLoopError("cycle advance must clear prior workflow payloads")
        for name in ("total_retries", "baseline_audit", "latest_audit"):
            if document[name] != prior[name]:
                raise AuditLoopError("cycle advance changed protected field: %s" % name)
    elif transition in {"retry-scheduled", "retry-exhausted"}:
        if document["cycle"] != prior["cycle"]:
            raise AuditLoopError("retry consumed a cycle")
        if document["total_retries"] != prior["total_retries"] + 1:
            raise AuditLoopError("retry total did not increment exactly once")
        if document["state_retries"] != prior["state_retries"] + 1:
            raise AuditLoopError("state retry count did not increment exactly once")
        for name in ("baseline_audit", "latest_audit", "proposal", "owner", "intervention"):
            if document[name] != prior[name]:
                raise AuditLoopError("retry changed protected field: %s" % name)
        if (transition == "retry-exhausted"
                and document["reason_code"] != "retry-budget-exhausted"):
            raise AuditLoopError("retry exhaustion requires retry-budget-exhausted reason_code")
    elif transition == "deadline-expired":
        for name in (
            "cycle", "total_retries", "state_retries", "baseline_audit", "latest_audit",
            "proposal", "owner", "intervention",
        ):
            if document[name] != prior[name]:
                raise AuditLoopError("deadline transition changed protected field: %s" % name)
        if document["reason_code"] != "deadline-expired":
            raise AuditLoopError("deadline exhaustion requires deadline-expired reason_code")

    if transition in {
        "proposal-recorded", "owner-accepted", "intervention-recorded",
        "owner-rejected", "reaudit-recorded", "cycle-advanced",
    }:
        if document["state_retries"] != 0 or document["backoff_seconds"] != 0:
            raise AuditLoopError("forward transition must reset state retry metadata")
        if document["retry_not_before"] is not None:
            raise AuditLoopError("forward transition must clear retry_not_before")
    if transition == "reaudit-recorded":
        audit = document["latest_audit"]
        if audit["verdict"] == "SHIP":
            expected_state = (
                "converged" if audit["score_confidence"] in {"medium", "high"}
                else "needs-input"
            )
        elif audit["verdict"] == "FIX":
            expected_state = (
                "next" if document["cycle"] < document["max_cycles"] else "exhausted"
            )
        elif audit["verdict"] == "BLOCK":
            expected_state = "gate-blocked"
        else:
            expected_state = "needs-input"
        if document["state"] != expected_state:
            raise AuditLoopError("re-audit verdict/confidence does not match terminal decision")


def _recover_residue(loop_dir, name):
    match = RESIDUE_NAME.fullmatch(name)
    if match is None or STEP_NAME.fullmatch(match.group(1)) is None:
        raise AuditLoopError("unsafe loop temporary residue: %s" % name)
    try:
        runtime.recover_immutable_install(loop_dir / match.group(1))
    except Exception as exc:
        raise _translate_error(exc) from exc


def _check_read_deadline(deadline_monotonic):
    if deadline_monotonic is None:
        return
    if (not isinstance(deadline_monotonic, (int, float))
            or isinstance(deadline_monotonic, bool)):
        raise AuditLoopError("deadline_monotonic must be a monotonic timestamp")
    if time.monotonic() > deadline_monotonic:
        raise AuditLoopError("loop read deadline exceeded")


def _validate_total_byte_budget(max_total_bytes):
    if max_total_bytes is None:
        return
    if (not isinstance(max_total_bytes, int) or isinstance(max_total_bytes, bool)
            or max_total_bytes < 0):
        raise AuditLoopError("max_total_bytes must be a non-negative integer")


def _load_steps(
        root, run_id, loop_id, loop_dir, recover=False, *,
        max_total_bytes=None, deadline_monotonic=None, return_total_bytes=False):
    _validate_total_byte_budget(max_total_bytes)
    _check_read_deadline(deadline_monotonic)
    try:
        descriptor, identity = runtime.open_directory_anchor(loop_dir)
    except Exception as exc:
        raise _translate_error(exc) from exc
    try:
        with os.scandir(descriptor) as entries:
            names = sorted(entry.name for entry in entries)
        runtime.revalidate_anchor(descriptor, loop_dir, identity)
    finally:
        os.close(descriptor)
    residues = [name for name in names if name.endswith(".run-create")]
    if residues and not recover:
        raise AuditLoopError("loop contains recoverable write residue")
    for name in residues:
        _recover_residue(loop_dir, name)
    if residues:
        return _load_steps(
            root, run_id, loop_id, loop_dir, recover=False,
            max_total_bytes=max_total_bytes,
            deadline_monotonic=deadline_monotonic,
            return_total_bytes=return_total_bytes,
        )
    unexpected = [
        name for name in names
        if name != ".loop.lock" and STEP_NAME.fullmatch(name) is None
    ]
    if unexpected:
        raise AuditLoopError("loop directory contains unexpected entry: %s" % unexpected[0])
    step_names = [name for name in names if STEP_NAME.fullmatch(name)]
    if len(step_names) > MAX_STEPS:
        raise AuditLoopError("loop exceeds %d immutable steps" % MAX_STEPS)
    steps = []
    prior = None
    prior_ref = None
    prior_sha = ZERO_HASH
    seen_ids = set()
    seen_keys = set()
    total_bytes = 0
    intervention_occurred_at = None
    for expected_sequence, name in enumerate(step_names, 1):
        _check_read_deadline(deadline_monotonic)
        match = STEP_NAME.fullmatch(name)
        if int(match.group(1)) != expected_sequence:
            raise AuditLoopError("loop step sequence is not contiguous")
        reference = _step_ref(root, loop_dir / name)
        document, digest, raw_length = _read_step(root, reference)
        _check_read_deadline(deadline_monotonic)
        total_bytes += raw_length
        if max_total_bytes is not None and total_bytes > max_total_bytes:
            raise AuditLoopError("loop steps exceed max_total_bytes")
        if document.get("transition") != match.group(2):
            raise AuditLoopError("loop step filename does not match its transition")
        _validate_step(
            document, expected_sequence, run_id, loop_id, prior, prior_ref, prior_sha,
            intervention_occurred_at=intervention_occurred_at,
        )
        if document["transition_id"] in seen_ids or document["idempotency_key"] in seen_keys:
            raise AuditLoopError("duplicate loop transition identity")
        seen_ids.add(document["transition_id"])
        seen_keys.add(document["idempotency_key"])
        steps.append({"document": document, "ref": reference, "sha256": digest})
        prior = document
        prior_ref = reference
        prior_sha = digest
        if document["transition"] == "intervention-recorded":
            intervention_occurred_at = document["occurred_at"]
        elif document["transition"] == "cycle-advanced":
            intervention_occurred_at = None
    _check_read_deadline(deadline_monotonic)
    try:
        descriptor, identity = runtime.open_directory_anchor(loop_dir)
        try:
            with os.scandir(descriptor) as entries:
                final_names = sorted(entry.name for entry in entries)
            runtime.revalidate_anchor(descriptor, loop_dir, identity)
        finally:
            os.close(descriptor)
    except Exception as exc:
        raise _translate_error(exc) from exc
    if final_names != names:
        raise AuditLoopError("loop directory changed during verification")
    _check_read_deadline(deadline_monotonic)
    if return_total_bytes:
        return steps, total_bytes
    return steps


def _read_loop_event_bound(
        root, run_id, loop_id, *,
        max_total_bytes=None, deadline_monotonic=None, return_total_bytes=False):
    _validate_total_byte_budget(max_total_bytes)
    _check_read_deadline(deadline_monotonic)
    loop_dir = _loop_directory(root, run_id, loop_id)
    try:
        with runtime.locked_stream(loop_dir / ".loop.lock", exclusive=False, create=False):
            _check_read_deadline(deadline_monotonic)
            loaded = _load_steps(
                root, run_id, loop_id, loop_dir,
                max_total_bytes=max_total_bytes,
                deadline_monotonic=deadline_monotonic,
                return_total_bytes=return_total_bytes,
            )
            if return_total_bytes:
                steps, total_bytes = loaded
            else:
                steps = loaded
            if not steps:
                raise AuditLoopError("loop has no immutable steps")
            runtime.verify_loop_event_coverage(
                root, run_id, loop_id, steps,
            )
            _check_read_deadline(deadline_monotonic)
    except Exception as exc:
        raise _translate_error(exc) from exc
    if return_total_bytes:
        return steps, total_bytes
    return steps


def read_loop(
        root, run_id, loop_id, *, max_total_bytes=None,
        deadline_monotonic=None, return_total_bytes=False):
    """Return a fully step/event-bound immutable loop snapshot.

    Each wrapper has ``document``, project-relative ``ref``, and exact file
    ``sha256`` keys. A step chain without one exact historical event ancestry
    is not a valid public read; mutation separately requires that ancestry to
    be selected now.
    """
    return _read_loop_event_bound(
        root, run_id, loop_id,
        max_total_bytes=max_total_bytes,
        deadline_monotonic=deadline_monotonic,
        return_total_bytes=return_total_bytes,
    )


def read_loop_with_event_coverage(
        root, run_id, loop_id, *, max_total_bytes=None,
        deadline_monotonic=None, return_total_bytes=False):
    """Compatibility alias for the default event-bound read surface."""
    return read_loop(
        root, run_id, loop_id,
        max_total_bytes=max_total_bytes,
        deadline_monotonic=deadline_monotonic,
        return_total_bytes=return_total_bytes,
    )


def resolve_loop_step(root, run_id, loop_id, reference, expected_sha256):
    """Resolve one exact step only after validating its complete loop chain."""
    validate_ref(reference, "loop step ref")
    validate_sha(expected_sha256, "loop step sha256")
    matches = [item for item in read_loop(root, run_id, loop_id) if item["ref"] == reference]
    if len(matches) != 1:
        raise AuditLoopError("loop step reference is not present exactly once in the loop")
    if matches[0]["sha256"] != expected_sha256:
        raise AuditLoopError("loop step hash mismatch")
    return matches[0]


def _request_material(action, options):
    material = {"action": action}
    for key, value in sorted(options.items()):
        if key in {"root", "lease_token"} or value is None:
            continue
        material[key] = value
    if options.get("lease_token") is not None:
        material["lease_token_sha256"] = hashlib.sha256(
            options["lease_token"].encode("utf-8")
        ).hexdigest()
    return material


def _released_lease(lease, occurred_at):
    result = dict(lease)
    result["active"] = False
    result["released_at"] = occurred_at
    return result


def _base_from_head(head, transition, state, occurred_at, request_hash, options):
    document = dict(head)
    document.update({
        "transition_id": str(uuid.uuid5(
            NAMESPACE, options["loop_id"] + ":" + options["idempotency_key"]
        )),
        "sequence": head["sequence"] + 1,
        "transition": transition,
        "from_state": head["state"],
        "state": state,
        "run_parent_event_id": options["_run_parent_event_id"],
        "run_parent_event_sha256": options["_run_parent_event_sha256"],
        "occurred_at": occurred_at,
        "recorded_at": occurred_at,
        "idempotency_key": options["idempotency_key"],
        "request_hash": request_hash,
        "previous_step_ref": options["_head_ref"],
        "previous_step_sha256": options["_head_sha256"],
        "expected_previous_sha256": options["expected_previous_sha256"],
        "reason_code": options.get("reason_code") or transition,
    })
    return document


def _require_active_lease(head, options, occurred):
    generation = options.get("lease_generation")
    token = options.get("lease_token")
    if not isinstance(generation, int) or isinstance(generation, bool):
        raise AuditLoopError("leased action requires lease_generation")
    if not isinstance(token, str) or not token:
        raise AuditLoopError("leased action requires lease_token")
    validate_safe_id(token, "lease_token")
    lease = head["lease"]
    if generation != lease["generation"]:
        raise AuditLoopError("stale lease generation is fenced")
    if not lease["active"]:
        raise AuditLoopError("lease is not active")
    if hashlib.sha256(token.encode("utf-8")).hexdigest() != lease["token_sha256"]:
        raise AuditLoopError("lease token mismatch")
    if occurred >= parse_time(lease["expires_at"], "lease.expires_at"):
        raise AuditLoopError("lease expired; acquire a new generation")


def _deadline_step(head, occurred_at, request_hash, options):
    document = _base_from_head(
        head, "deadline-expired", "exhausted", occurred_at, request_hash, options,
    )
    document.update({
        "state_retries": head["state_retries"], "backoff_seconds": 0,
        "retry_not_before": None,
        "lease": _released_lease(head["lease"], occurred_at)
        if head["lease"]["generation"] else head["lease"],
        "reason_code": "deadline-expired",
    })
    return document


def _build_transition(action, head, occurred_at, request_hash, options, root):
    occurred = parse_time(occurred_at, "occurred_at")
    if head["state"] in TERMINAL_STATES:
        raise AuditLoopError("terminal loop cannot accept another transition")
    deadline = parse_time(head["deadline"], "deadline")
    if occurred > deadline:
        return _deadline_step(head, occurred_at, request_hash, options)
    retry_not_before = head.get("retry_not_before")
    if retry_not_before is not None and occurred < parse_time(retry_not_before, "retry_not_before"):
        raise AuditLoopError("retry backoff has not elapsed")

    if action == "acquire-lease":
        owner = options.get("lease_owner")
        token = options.get("lease_token")
        ttl = options.get("lease_ttl")
        validate_safe_id(owner, "lease_owner")
        validate_safe_id(token, "lease_token")
        _bounded_integer(ttl, "lease_ttl", LEASE_MIN_SECONDS, LEASE_MAX_SECONDS)
        prior = head["lease"]
        if prior["active"] and occurred < parse_time(prior["expires_at"], "lease.expires_at"):
            raise AuditLoopError("an unexpired lease is already active")
        expires = occurred + dt.timedelta(seconds=ttl)
        document = _base_from_head(
            head, "lease-acquired", head["state"], occurred_at, request_hash, options,
        )
        document.update({
            "backoff_seconds": 0,
            "lease": {
                "generation": prior["generation"] + 1,
                "active": True,
                "owner": owner,
                "token_sha256": hashlib.sha256(token.encode("utf-8")).hexdigest(),
                "acquired_at": occurred_at,
                "expires_at": iso_time(expires),
                "released_at": None,
            },
        })
        return document

    if action in LEASED_ACTIONS:
        _require_active_lease(head, options, occurred)

    if action == "proposal":
        if head["state"] != "awaiting-proposal":
            raise AuditLoopError("proposal requires awaiting-proposal state")
        proposal = _verify_evidence(
            root, options.get("proposal_ref"), options.get("proposal_sha256"), "proposal",
        )
        document = _base_from_head(
            head, "proposal-recorded", "awaiting-owner", occurred_at, request_hash, options,
        )
        document.update({
            "proposal": proposal, "owner": None, "intervention": None,
            "state_retries": 0, "backoff_seconds": 0, "retry_not_before": None,
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    if action == "owner":
        if head["state"] != "awaiting-owner":
            raise AuditLoopError("owner decision requires awaiting-owner state")
        owner = options.get("owner_id")
        decision = options.get("decision")
        validate_safe_id(owner, "owner_id")
        if decision not in {"accept", "reject"}:
            raise AuditLoopError("owner decision must be accept or reject")
        transition = "owner-accepted" if decision == "accept" else "owner-rejected"
        state = "awaiting-intervention" if decision == "accept" else "needs-input"
        document = _base_from_head(
            head, transition, state, occurred_at, request_hash, options,
        )
        document.update({
            "owner": owner, "state_retries": 0, "backoff_seconds": 0,
            "retry_not_before": None,
            "reason_code": "owner-accepted" if decision == "accept" else "owner-rejected",
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    if action == "intervention":
        if head["state"] != "awaiting-intervention":
            raise AuditLoopError("intervention evidence requires awaiting-intervention state")
        intervention = _verify_evidence(
            root, options.get("intervention_ref"), options.get("intervention_sha256"),
            "intervention evidence",
        )
        document = _base_from_head(
            head, "intervention-recorded", "awaiting-reaudit", occurred_at,
            request_hash, options,
        )
        document.update({
            "intervention": intervention, "state_retries": 0, "backoff_seconds": 0,
            "retry_not_before": None,
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    if action == "reaudit":
        if head["state"] != "awaiting-reaudit":
            raise AuditLoopError("re-audit requires awaiting-reaudit state")
        audit = _validate_exact_audit(
            root, options.get("audit_ref"), options.get("audit_sha256"), "re-audit",
        )
        if audit["sha256"] == head["latest_audit"]["sha256"]:
            raise AuditLoopError("re-audit must use distinct artifact bytes")
        if audit["target_identity_sha256"] != head["baseline_audit"]["target_identity_sha256"]:
            raise AuditLoopError("re-audit framework/profile/target identity mismatch")
        observed = _parse_audit_date(audit["observed_at"], "re-audit.observed_at")
        baseline_observed = _parse_audit_date(
            head["baseline_audit"]["observed_at"], "baseline_audit.observed_at",
        )
        if observed <= baseline_observed:
            raise AuditLoopError("re-audit observed_at must follow the baseline audit date")
        intervention_occurred_at = options.get("_intervention_occurred_at")
        if intervention_occurred_at is None:
            raise AuditLoopError("re-audit requires a recorded intervention occurrence time")
        if observed < parse_time(
                intervention_occurred_at, "intervention.occurred_at").date():
            raise AuditLoopError("re-audit observed_at cannot precede the intervention date")
        if audit["verdict"] == "SHIP":
            state = "converged" if audit["score_confidence"] in {"medium", "high"} else "needs-input"
            reason = "ship-confirmed" if state == "converged" else "ship-confidence-low"
        elif audit["verdict"] == "FIX":
            state = "next" if head["cycle"] < head["max_cycles"] else "exhausted"
            reason = "fix-remains" if state == "next" else "cycle-budget-exhausted"
        elif audit["verdict"] == "BLOCK":
            state, reason = "gate-blocked", "verified-gate-block"
        else:
            state, reason = "needs-input", "reaudit-undecided"
        document = _base_from_head(
            head, "reaudit-recorded", state, occurred_at, request_hash, options,
        )
        document.update({
            "latest_audit": audit, "state_retries": 0, "backoff_seconds": 0,
            "retry_not_before": None, "reason_code": reason,
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    if action == "advance":
        if head["state"] != "next":
            raise AuditLoopError("advance requires next state")
        if head["cycle"] >= head["max_cycles"]:
            raise AuditLoopError("cycle budget is exhausted")
        document = _base_from_head(
            head, "cycle-advanced", "awaiting-proposal", occurred_at, request_hash, options,
        )
        document.update({
            "cycle": head["cycle"] + 1, "proposal": None, "owner": None,
            "intervention": None, "state_retries": 0, "backoff_seconds": 0,
            "retry_not_before": None,
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    if action == "retry":
        if head["state"] not in ACTIVE_STATES - {"next"}:
            raise AuditLoopError("retry is supported only in an awaiting state")
        next_retry = head["state_retries"] + 1
        total = head["total_retries"] + 1
        if next_retry > head["max_retries"]:
            document = _base_from_head(
                head, "retry-exhausted", "exhausted", occurred_at, request_hash, options,
            )
            document.update({
                "total_retries": total, "state_retries": next_retry,
                "backoff_seconds": 0, "retry_not_before": None,
                "reason_code": "retry-budget-exhausted",
                "lease": _released_lease(head["lease"], occurred_at),
            })
            return document
        backoff = min(2 ** (next_retry - 1), BACKOFF_MAX_SECONDS)
        document = _base_from_head(
            head, "retry-scheduled", head["state"], occurred_at, request_hash, options,
        )
        document.update({
            "total_retries": total, "state_retries": next_retry,
            "backoff_seconds": backoff,
            "retry_not_before": iso_time(occurred + dt.timedelta(seconds=backoff)),
            "lease": _released_lease(head["lease"], occurred_at),
        })
        return document

    raise AuditLoopError("unsupported action: %s" % action)


def _serialized_step_bytes(document):
    try:
        return (
            json.dumps(
                document, indent=2, sort_keys=True, ensure_ascii=False,
                allow_nan=False,
            ) + "\n"
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise AuditLoopError("loop step must be finite JSON: %s" % exc) from exc


def _validate_step_size(document):
    if len(_serialized_step_bytes(document)) > runtime.MAX_DOCUMENT_BYTES:
        raise AuditLoopError(
            "loop step exceeds the %d-byte document limit"
            % runtime.MAX_DOCUMENT_BYTES
        )


def _build_validated_start_document(root, options, request_hash):
    if options["expected_previous_sha256"] != ZERO_HASH:
        raise AuditLoopError("loop start must expect the zero previous SHA")
    reason_code = options.get("reason_code")
    if reason_code is not None:
        validate_safe_id(reason_code, "reason_code")
    baseline = _validate_exact_audit(
        root, options.get("audit_ref"), options.get("audit_sha256"),
        "baseline audit",
    )
    if not (
        baseline["status"] == "DONE_WITH_CONCERNS"
        and baseline["verdict"] == "FIX"
        and baseline["score_state"] == "SCORED"
    ):
        raise AuditLoopError(
            "baseline must be validated DONE_WITH_CONCERNS + FIX + SCORED"
        )
    max_cycles = options.get("max_cycles")
    max_retries = options.get("max_retries")
    _bounded_integer(max_cycles, "max_cycles", 1, 3)
    _bounded_integer(max_retries, "max_retries", 0, MAX_RETRIES)
    deadline = options.get("deadline")
    if parse_time(deadline, "deadline") <= parse_time(
            options["occurred_at"], "occurred_at"):
        raise AuditLoopError("deadline must follow loop start")
    document = {
        "schema_version": SCHEMA_VERSION,
        "run_id": options["run_id"],
        "loop_id": options["loop_id"],
        "transition_id": str(uuid.uuid5(
            NAMESPACE, options["loop_id"] + ":" + options["idempotency_key"]
        )),
        "sequence": 1,
        "transition": "start",
        "from_state": None,
        "state": "awaiting-proposal",
        "run_parent_event_id": options["_run_parent_event_id"],
        "run_parent_event_sha256": options["_run_parent_event_sha256"],
        "cycle": 1,
        "max_cycles": max_cycles,
        "total_retries": 0,
        "state_retries": 0,
        "max_retries": max_retries,
        "backoff_seconds": 0,
        "retry_not_before": None,
        "deadline": deadline,
        "occurred_at": options["occurred_at"],
        "recorded_at": options["occurred_at"],
        "idempotency_key": options["idempotency_key"],
        "request_hash": request_hash,
        "previous_step_ref": None,
        "previous_step_sha256": ZERO_HASH,
        "expected_previous_sha256": ZERO_HASH,
        "proposal_only": True,
        "external_mutation_authorized": False,
        "baseline_audit": baseline,
        "latest_audit": baseline,
        "proposal": None,
        "owner": None,
        "intervention": None,
        "reason_code": reason_code or "verified-fix-baseline",
        "lease": _empty_lease(),
    }
    _validate_step(
        document, 1, options["run_id"], options["loop_id"],
        None, None, ZERO_HASH,
    )
    _validate_step_size(document)
    return document


def _existing_loop_directory(root, run_id, loop_id):
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    try:
        root_path = runtime.normalized_root(root)
    except Exception as exc:
        raise _translate_error(exc) from exc
    loop_dir = root_path / "memory" / "runs" / run_id / "loops" / loop_id
    try:
        metadata = os.lstat(loop_dir)
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise AuditLoopError("cannot inspect loop directory: %s" % loop_id) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise AuditLoopError("loop directory must be a real directory")
    return loop_dir


def _cleanup_new_empty_loop(loop_dir, created_identity):
    """Remove only a loop directory created by this failed start attempt.

    This deliberately refuses cleanup if any step, residue, or unexpected
    entry exists. It must never turn recovery of a committed step into data
    loss merely to make a failed start look tidy.
    """
    parent_fd = None
    child_fd = None
    try:
        parent_fd, parent_identity = runtime.open_directory_anchor(loop_dir.parent)
        entry = runtime.anchored_lstat(
            parent_fd, loop_dir.parent, loop_dir.name, missing_ok=True,
        )
        if entry is None or (entry.st_dev, entry.st_ino) != created_identity:
            return False
        if stat.S_ISLNK(entry.st_mode) or not stat.S_ISDIR(entry.st_mode):
            return False
        flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        child_fd = os.open(loop_dir.name, flags, dir_fd=parent_fd)
        opened = os.fstat(child_fd)
        if (opened.st_dev, opened.st_ino) != created_identity:
            return False
        with os.scandir(child_fd) as entries:
            names = sorted(item.name for item in entries)
        if names != [".loop.lock"]:
            return False
        lock_metadata = os.stat(
            ".loop.lock", dir_fd=child_fd, follow_symlinks=False,
        )
        if (stat.S_ISLNK(lock_metadata.st_mode)
                or not stat.S_ISREG(lock_metadata.st_mode)
                or lock_metadata.st_nlink != 1):
            return False
        # Revalidate both anchors immediately before deletion. All deletion is
        # relative to those descriptors; a path replacement cannot redirect
        # it into a different directory tree.
        runtime.revalidate_anchor(parent_fd, loop_dir.parent, parent_identity)
        current = runtime.anchored_lstat(
            parent_fd, loop_dir.parent, loop_dir.name, missing_ok=True,
        )
        if current is None or (current.st_dev, current.st_ino) != created_identity:
            return False
        os.unlink(".loop.lock", dir_fd=child_fd)
        with os.scandir(child_fd) as entries:
            if any(True for _item in entries):
                return False
        current = runtime.anchored_lstat(
            parent_fd, loop_dir.parent, loop_dir.name, missing_ok=True,
        )
        if current is None or (current.st_dev, current.st_ino) != created_identity:
            return False
        os.rmdir(loop_dir.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        return True
    except (OSError, ValueError):
        return False
    finally:
        if child_fd is not None:
            os.close(child_fd)
        if parent_fd is not None:
            os.close(parent_fd)


def _current_intervention_occurred_at(steps):
    for wrapper in reversed(steps):
        transition = wrapper["document"]["transition"]
        if transition == "intervention-recorded":
            return wrapper["document"]["occurred_at"]
        if transition == "cycle-advanced":
            return None
    return None


def _run_anchor_context(events, loop_id, transition_id):
    """Return the immutable run parent for a new or reserved loop event."""
    key = "loop:" + transition_id
    existing = [event for event in events if event["idempotency_key"] == key]
    if len(existing) > 1:
        raise AuditLoopError("audit loop anchor identity is ambiguous")
    if existing:
        anchor = existing[0]
        if (anchor["event_type"] != "loop_state_changed"
                or anchor["subject"] != {"kind": "loop", "ref": loop_id}):
            raise AuditLoopError("audit loop anchor identity is occupied")
        parent_id = anchor["parent_event_id"]
        parents = [event for event in events if event["event_id"] == parent_id]
        if len(parents) != 1:
            raise AuditLoopError("audit loop anchor parent is missing or ambiguous")
        return parent_id, parents[0]["event_hash"], anchor
    if not events:
        raise AuditLoopError("audit loop cannot attach to an empty run")
    head = events[-1]
    return head["event_id"], head["event_hash"], None


def _apply_action_under_coordinator(action, **options):
    root = Path(options.get("root", "."))
    run_id = options.get("run_id")
    loop_id = options.get("loop_id")
    idempotency_key = options.get("idempotency_key")
    expected_previous = options.get("expected_previous_sha256")
    occurred_at = options.get("occurred_at")
    if action not in SUPPORTED_ACTIONS:
        raise AuditLoopError("unsupported action: %s" % action)
    if occurred_at is None:
        raise AuditLoopError("occurred_at must be supplied explicitly")
    validate_uuid(run_id, "run_id")
    validate_uuid(loop_id, "loop_id")
    validate_safe_id(idempotency_key, "idempotency_key")
    validate_sha(expected_previous, "expected_previous_sha256")
    parse_time(occurred_at, "occurred_at")
    options = dict(options)
    options.update({
        "root": root, "run_id": run_id, "loop_id": loop_id,
        "idempotency_key": idempotency_key,
        "expected_previous_sha256": expected_previous, "occurred_at": occurred_at,
    })
    request_hash = sha256_json(_request_material(action, options))
    try:
        initial_run_events = runtime.load_events(root, run_id)
    except Exception as exc:
        raise _translate_error(exc) from exc
    transition_id = str(uuid.uuid5(NAMESPACE, loop_id + ":" + idempotency_key))
    parent_event_id, parent_event_sha256, initial_anchor = _run_anchor_context(
        initial_run_events, loop_id, transition_id,
    )
    if (
            initial_run_events[-1]["event_type"] in runtime.TERMINAL_TYPES
            and initial_anchor is None):
        raise AuditLoopError("terminal run cannot accept a new audit loop action")
    options["_run_parent_event_id"] = parent_event_id
    options["_run_parent_event_sha256"] = parent_event_sha256
    loop_dir = _existing_loop_directory(root, run_id, loop_id)
    created_loop_identity = None
    if loop_dir is None:
        if action != "start":
            raise AuditLoopError("loop must start before %s" % action)
        if initial_anchor is None and len(initial_run_events) >= runtime.MAX_EVENTS - 1:
            raise AuditLoopError(
                "run event stream must preserve one terminal-envelope event slot"
            )
        # Validate the complete derived start step before creating any loop
        # directory or lock. The same exact-byte validation runs again under
        # the loop lock below to close the source-artifact TOCTOU window.
        _build_validated_start_document(root, options, request_hash)
        loop_dir, created_loop_identity = _ensure_loop_directory(root, run_id, loop_id)
    lock_path = loop_dir / ".loop.lock"
    try:
        with runtime.locked_stream(lock_path, exclusive=True):
            steps = _load_steps(root, run_id, loop_id, loop_dir, recover=True)
            duplicate = next(
                (item for item in steps
                 if item["document"]["idempotency_key"] == idempotency_key),
                None,
            )
            if duplicate is not None:
                if duplicate["document"]["request_hash"] != request_hash:
                    raise AuditLoopError(
                        "idempotency key was already used with different request content"
                    )
            recovering_unmaterialized = (
                initial_anchor is not None and duplicate is None
            )
            if steps:
                try:
                    runtime.verify_loop_event_coverage(
                        root, run_id, loop_id, steps,
                        require_selected=not recovering_unmaterialized,
                        _allowed_unmaterialized_event_id=(
                            initial_anchor["event_id"]
                            if recovering_unmaterialized
                            else None
                        ),
                    )
                except Exception as exc:
                    raise _translate_error(exc) from exc
            if duplicate is not None:
                wrapper = duplicate
                document = wrapper["document"]
                reference = wrapper["ref"]
                predicted_digest = wrapper["sha256"]
                needs_materialization = False
            else:
                try:
                    run_events = runtime.load_events(root, run_id)
                except Exception as exc:
                    raise _translate_error(exc) from exc
                parent_event_id, parent_event_sha256, existing_anchor = (
                    _run_anchor_context(run_events, loop_id, transition_id)
                )
                if (
                        run_events[-1]["event_type"] in runtime.TERMINAL_TYPES
                        and existing_anchor is None):
                    raise AuditLoopError(
                        "terminal run cannot accept a new audit loop step"
                    )
                options["_run_parent_event_id"] = parent_event_id
                options["_run_parent_event_sha256"] = parent_event_sha256
                if existing_anchor is None and len(run_events) >= runtime.MAX_EVENTS - 1:
                    raise AuditLoopError(
                        "run event stream must preserve one terminal-envelope event slot"
                    )
                head_sha = steps[-1]["sha256"] if steps else ZERO_HASH
                if expected_previous != head_sha:
                    raise AuditLoopError("optimistic concurrency conflict: expected previous SHA mismatch")
                if len(steps) >= MAX_STEPS:
                    raise AuditLoopError("loop reached the %d-step limit" % MAX_STEPS)

                if action == "start":
                    if steps:
                        raise AuditLoopError("start requires an empty loop")
                    document = _build_validated_start_document(
                        root, options, request_hash,
                    )
                else:
                    if not steps:
                        raise AuditLoopError("loop must start before %s" % action)
                    options["_head_ref"] = steps[-1]["ref"]
                    options["_head_sha256"] = steps[-1]["sha256"]
                    options["_intervention_occurred_at"] = (
                        _current_intervention_occurred_at(steps)
                    )
                    document = _build_transition(
                        action, steps[-1]["document"], occurred_at, request_hash,
                        options, root,
                    )

                sequence = document["sequence"]
                filename = "%03d-%s.json" % (sequence, document["transition"])
                path = loop_dir / filename
                reference = _step_ref(root, path)
                prior = steps[-1] if steps else None
                intervention_occurred_at = _current_intervention_occurred_at(steps)
                _validate_step(
                    document, sequence, run_id, loop_id,
                    prior["document"] if prior else None,
                    prior["ref"] if prior else None,
                    prior["sha256"] if prior else ZERO_HASH,
                    intervention_occurred_at=intervention_occurred_at,
                )
                _validate_step_size(document)
                predicted_digest = hashlib.sha256(
                    _serialized_step_bytes(document)
                ).hexdigest()
                needs_materialization = True

            try:
                anchor_result = runtime.anchor_loop_step(
                    root, run_id, loop_id, reference, predicted_digest, document,
                    _coordinator_locked=True,
                )
            except Exception as exc:
                raise AuditLoopError(
                    "loop event anchor failed before step materialization: %s" % exc
                ) from exc

            if needs_materialization:
                try:
                    digest = runtime.write_immutable_json(root, path, document)
                except Exception as exc:
                    raise AuditLoopError(
                        "event_committed=true step_ref=%s step_sha256=%s: "
                        "step materialization failed (%s); retry the same request"
                        % (reference, predicted_digest, exc)
                    ) from exc
                installed, installed_digest, _installed_bytes = _read_step(root, reference)
                if (digest != predicted_digest or installed_digest != predicted_digest
                        or canonical_json(installed) != canonical_json(document)):
                    raise AuditLoopError("installed loop step failed exact verification")
                _validate_step(
                    installed, sequence, run_id, loop_id,
                    prior["document"] if prior else None,
                    prior["ref"] if prior else None,
                    prior["sha256"] if prior else ZERO_HASH,
                    intervention_occurred_at=intervention_occurred_at,
                )
                wrapper = {
                    "document": installed, "ref": reference,
                    "sha256": installed_digest,
                }
                steps = [*steps, wrapper]
            return {
                "deduplicated": anchor_result["deduplicated"],
                "step_ref": wrapper["ref"],
                "step_sha256": wrapper["sha256"],
                "step": wrapper["document"],
                "event": {
                    "deduplicated": anchor_result["deduplicated"],
                    "event_id": anchor_result["event"]["event_id"],
                    "event_hash": anchor_result["event"]["event_hash"],
                },
            }
    except AuditLoopError:
        if created_loop_identity is not None:
            _cleanup_new_empty_loop(loop_dir, created_loop_identity)
        raise
    except Exception as exc:
        if created_loop_identity is not None:
            _cleanup_new_empty_loop(loop_dir, created_loop_identity)
        raise _translate_error(exc) from exc


def apply_action(action, **options):
    """Apply one mutation while fencing run terminal/waiting transitions."""
    root = Path(options.get("root", "."))
    run_id = options.get("run_id")
    validate_uuid(run_id, "run_id")
    try:
        runtime.load_events(root, run_id)
        with runtime.locked_run_coordinator(root, run_id):
            return _apply_action_under_coordinator(action, **options)
    except AuditLoopError:
        raise
    except Exception as exc:
        raise _translate_error(exc) from exc


def _common_mutation(parser):
    parser.add_argument("--root", default=".")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--loop-id", required=True)
    parser.add_argument("--idempotency-key", required=True)
    parser.add_argument("--expected-previous-sha256", required=True)
    parser.add_argument("--occurred-at", required=True)
    parser.add_argument("--reason-code")


def _leased(parser):
    parser.add_argument("--lease-generation", required=True, type=int)
    parser.add_argument("--lease-token", required=True)


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)

    start = subparsers.add_parser("start", help="Start from a verified FIX audit.")
    _common_mutation(start)
    start.add_argument("--audit-ref", required=True)
    start.add_argument("--audit-sha256", required=True)
    start.add_argument("--deadline", required=True)
    start.add_argument("--max-cycles", type=int, default=3)
    start.add_argument("--max-retries", type=int, default=2)

    lease = subparsers.add_parser("acquire-lease", help="Acquire a short fencing lease.")
    _common_mutation(lease)
    lease.add_argument("--lease-owner", required=True)
    lease.add_argument("--lease-token", required=True)
    lease.add_argument("--lease-ttl", type=int, default=60)

    proposal = subparsers.add_parser("proposal", help="Record a proposal artifact.")
    _common_mutation(proposal)
    _leased(proposal)
    proposal.add_argument("--proposal-ref", required=True)
    proposal.add_argument("--proposal-sha256", required=True)

    owner = subparsers.add_parser("owner", help="Record an explicit owner decision.")
    _common_mutation(owner)
    _leased(owner)
    owner.add_argument("--owner-id", required=True)
    owner.add_argument("--decision", required=True, choices=("accept", "reject"))

    intervention = subparsers.add_parser(
        "intervention", help="Record evidence of an owner-executed intervention."
    )
    _common_mutation(intervention)
    _leased(intervention)
    intervention.add_argument("--intervention-ref", required=True)
    intervention.add_argument("--intervention-sha256", required=True)

    reaudit = subparsers.add_parser("reaudit", help="Record a distinct validated re-audit.")
    _common_mutation(reaudit)
    _leased(reaudit)
    reaudit.add_argument("--audit-ref", required=True)
    reaudit.add_argument("--audit-sha256", required=True)

    advance = subparsers.add_parser("advance", help="Advance next into a new cycle.")
    _common_mutation(advance)
    _leased(advance)

    retry = subparsers.add_parser("retry", help="Schedule one bounded retry without sleeping.")
    _common_mutation(retry)
    _leased(retry)

    show = subparsers.add_parser("show", help="Verify and render the immutable loop.")
    show.add_argument("--root", default=".")
    show.add_argument("--run-id", required=True)
    show.add_argument("--loop-id", required=True)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    values = vars(args)
    action = values.pop("action")
    try:
        if action == "show":
            steps = read_loop(values["root"], values["run_id"], values["loop_id"])
            result = {
                "steps": len(steps), "head_ref": steps[-1]["ref"],
                "head_sha256": steps[-1]["sha256"], "head": steps[-1]["document"],
                "chain": [
                    {"ref": item["ref"], "sha256": item["sha256"]}
                    for item in steps
                ],
            }
        else:
            result = apply_action(action, **values)
    except AuditLoopError as exc:
        parser.exit(1, "audit-loop: %s\n" % exc)
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
