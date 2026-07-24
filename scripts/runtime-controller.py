#!/usr/bin/env python3
"""Supported controller for the verified Aaron run lifecycle.

The controller is deliberately an orchestration boundary, not an agent or a
truth registry. ``start`` materializes route -> machine-contract context plan
-> deterministic resolution -> immutable turn snapshot. ``checkpoint`` and
``finish`` require an exact verified event head so stale callers cannot advance
or close a different branch. ``resume`` rebuilds state from the hash-chained
event stream and live-verifies the latest context sources.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "1.0"
CONTROLLER_NAMESPACE = uuid.UUID("d9de63e9-1d85-4fba-bb71-f1d5af9fe4fd")
MAX_REQUEST_BYTES = 1_000_000
TERMINAL_STATUSES = {"succeeded", "failed", "aborted"}
FAILURE_CLASSES = {
    "prompt", "routing", "context", "tool", "permission", "artifact", "loop", "unknown",
}


class ControllerError(ValueError):
    pass


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ControllerError("controller dependency cannot be loaded: %s" % path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


planner = _load_module("aaron_context_plan_controller", ROOT / "scripts" / "context-plan.py")
resolver = planner.resolver
runtime = _load_module("aaron_run_events_controller", ROOT / "scripts" / "run-events.py")
profile_runtime = _load_module(
    "aaron_profile_resolver_controller", ROOT / "scripts" / "profile-resolver.py"
)


def _canonical(value):
    return runtime.strict_json_loads(runtime.canonical_json(value), "controller value")


def _exact(value, required, optional, label):
    try:
        return runtime.exact_object(value, set(required), set(optional), label)
    except runtime.RunEventError as exc:
        raise ControllerError(str(exc)) from exc


def _integer(value, label, minimum, maximum):
    if (
            not isinstance(value, int) or isinstance(value, bool)
            or value < minimum or value > maximum):
        raise ControllerError("%s must be an integer from %d to %d" % (label, minimum, maximum))
    return value


def _validate_head(value, label="expected_head"):
    _exact(value, {"event_id", "offset", "hash"}, set(), label)
    runtime.validate_uuid(value["event_id"], label + ".event_id")
    _integer(value["offset"], label + ".offset", 1, runtime.MAX_EVENTS)
    runtime.validate_sha(value["hash"], label + ".hash")
    return _canonical(value)


def _head(state):
    return {
        "event_id": state["head_event_id"],
        "offset": state["last_offset"],
        "hash": state["last_event_hash"],
    }


def _validate_tools(value):
    if not isinstance(value, list) or len(value) > 128:
        raise ControllerError("tools must be an array with at most 128 entries")
    for index, tool in enumerate(value):
        label = "tools[%d]" % index
        _exact(tool, {"name", "mode", "schema_sha256"}, set(), label)
        runtime.validate_safe_id(tool["name"], label + ".name")
        runtime.validate_enum(
            tool["mode"], {"read-only", "proposal-only", "mutating", "external"},
            label + ".mode",
        )
        runtime.validate_sha(tool["schema_sha256"], label + ".schema_sha256")
    return _canonical(value)


def _validate_permission(value):
    _exact(value, {"mode", "sandbox", "network", "external_mutations"}, set(),
           "permission_profile")
    runtime.validate_enum(
        value["mode"], {"disabled", "read-only", "proposal-only", "write-gated"},
        "permission_profile.mode",
    )
    runtime.validate_safe_id(value["sandbox"], "permission_profile.sandbox")
    for field in ("network", "external_mutations"):
        if not isinstance(value[field], bool):
            raise ControllerError("permission_profile.%s must be boolean" % field)
    if value["external_mutations"] and value["mode"] != "write-gated":
        raise ControllerError("external mutations require permission_profile.mode=write-gated")
    return _canonical(value)


def validate_start_request(value):
    _exact(value, {
        "schema_version", "run_id", "parent_run_id", "turn_id", "as_of", "route",
        "budget", "registry_offsets", "host", "system_prompt_sha256", "tools",
        "permission_profile",
    }, set(), "controller start request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ControllerError("controller start schema_version must be 1.0")
    runtime.validate_uuid(value["run_id"], "run_id")
    if value["parent_run_id"] is not None:
        runtime.validate_uuid(value["parent_run_id"], "parent_run_id")
        if value["parent_run_id"] == value["run_id"]:
            raise ControllerError("parent_run_id cannot equal run_id")
    runtime.validate_safe_id(value["turn_id"], "turn_id")
    runtime.parse_datetime(value["as_of"], "as_of")
    route = _exact(
        value["route"], {"target_skill", "command", "reason_code"}, set(), "route",
    )
    runtime.validate_safe_id(route["target_skill"], "route.target_skill")
    if route["command"] is not None:
        runtime.validate_enum(route["command"], resolver.COMMANDS, "route.command")
    runtime.validate_safe_id(route["reason_code"], "route.reason_code")
    budget = _exact(value["budget"], {
        "max_tokens", "bytes_per_token", "max_resources", "max_sensitivity",
        "prefix_file_limit",
    }, set(), "budget")
    _integer(budget["max_tokens"], "budget.max_tokens", 1, MAX_REQUEST_BYTES)
    _integer(budget["bytes_per_token"], "budget.bytes_per_token", 1, 16)
    _integer(budget["max_resources"], "budget.max_resources", 1, 256)
    _integer(budget["prefix_file_limit"], "budget.prefix_file_limit", 1, 256)
    runtime.validate_enum(
        budget["max_sensitivity"], resolver.SENSITIVITIES, "budget.max_sensitivity",
    )
    runtime.validate_offsets(value["registry_offsets"])
    host = _exact(
        value["host"], {"adapter", "model_provider", "model_id"}, {"adapter_version"},
        "host",
    )
    for field, item in host.items():
        runtime.validate_safe_id(item, "host.%s" % field)
    runtime.validate_sha(value["system_prompt_sha256"], "system_prompt_sha256")
    _validate_tools(value["tools"])
    _validate_permission(value["permission_profile"])
    return _canonical(value)


def _validate_checkpoint_artifacts(value):
    if not isinstance(value, list) or len(value) > 128:
        raise ControllerError("artifacts must be an array with at most 128 entries")
    for index, item in enumerate(value):
        label = "artifacts[%d]" % index
        _exact(item, {"ref", "sha256", "validator", "validation_status"}, set(), label)
        runtime.validate_ref(item["ref"], label + ".ref")
        runtime.validate_sha(item["sha256"], label + ".sha256")
        runtime.validate_safe_id(item["validator"], label + ".validator")
        runtime.validate_enum(
            item["validation_status"], {"valid", "not-required"},
            label + ".validation_status",
        )
    return _canonical(value)


def _validate_pending_handoff(value):
    if value is None:
        return None
    _exact(value, {"status", "objective_code", "recommended_skill"}, set(),
           "pending_handoff")
    runtime.validate_enum(
        value["status"], {"proposed", "needs-input", "blocked"},
        "pending_handoff.status",
    )
    runtime.validate_safe_id(value["objective_code"], "pending_handoff.objective_code")
    runtime.validate_safe_id(value["recommended_skill"], "pending_handoff.recommended_skill")
    return _canonical(value)


def validate_checkpoint_request(value):
    _exact(value, {
        "schema_version", "checkpoint_id", "occurred_at", "expected_head", "status",
        "artifacts", "pending_handoff", "next_action",
    }, set(), "controller checkpoint request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ControllerError("controller checkpoint schema_version must be 1.0")
    runtime.validate_uuid(value["checkpoint_id"], "checkpoint_id")
    runtime.parse_datetime(value["occurred_at"], "occurred_at")
    _validate_head(value["expected_head"])
    runtime.validate_enum(
        value["status"], {"ready", "waiting", "needs-input", "blocked", "failed", "complete"},
        "checkpoint status",
    )
    _validate_checkpoint_artifacts(value["artifacts"])
    _validate_pending_handoff(value["pending_handoff"])
    runtime.validate_next_action(value["next_action"])
    return _canonical(value)


def _validate_envelope_artifacts(value):
    if not isinstance(value, list) or len(value) > 128:
        raise ControllerError("artifacts must be an array with at most 128 entries")
    for index, item in enumerate(value):
        runtime.validate_artifact_ref(item, "artifacts[%d]" % index)
    return _canonical(value)


def validate_finish_request(value):
    _exact(value, {
        "schema_version", "occurred_at", "expected_head", "status", "evidence_mode",
        "artifacts", "metrics", "failure_class", "next_action",
    }, set(), "controller finish request")
    if value["schema_version"] != SCHEMA_VERSION:
        raise ControllerError("controller finish schema_version must be 1.0")
    runtime.parse_datetime(value["occurred_at"], "occurred_at")
    _validate_head(value["expected_head"])
    runtime.validate_enum(
        value["status"], {"waiting", "needs-input", "blocked", *TERMINAL_STATUSES},
        "finish status",
    )
    runtime.validate_enum(
        value["evidence_mode"], {"none", "simulated", "real", "mixed"},
        "evidence_mode",
    )
    _validate_envelope_artifacts(value["artifacts"])
    if not isinstance(value["metrics"], dict) or len(value["metrics"]) > 48:
        raise ControllerError("metrics must be an object with at most 48 entries")
    for key, metric in value["metrics"].items():
        if not runtime.SAFE_FIELD.fullmatch(key) or key.startswith("controller."):
            raise ControllerError("metrics contains a reserved or unsafe key")
        runtime.validate_finite_metric(metric, "metrics.%s" % key)
    if value["failure_class"] is not None:
        runtime.validate_enum(value["failure_class"], FAILURE_CLASSES, "failure_class")
    if value["status"] in {"failed", "blocked", "aborted"}:
        if value["failure_class"] is None:
            raise ControllerError("failed, blocked, or aborted finish requires failure_class")
    elif value["failure_class"] is not None:
        raise ControllerError("failure_class must be null for a non-failure finish")
    runtime.validate_next_action(value["next_action"])
    return _canonical(value)


def _event_request(run_id, key, event_type, occurred_at, parent_event_id, status,
                   subject, *, turn_id=None, reason_code=None, references=None,
                   metrics=None, dimensions=None):
    value = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "idempotency_key": key,
        "event_type": event_type,
        "occurred_at": occurred_at,
        "actor": {"type": "system", "id": "runtime-controller"},
        "parent_event_id": parent_event_id,
        "turn_id": turn_id,
        "status": status,
        "subject": subject,
        "references": references or [],
        "metrics": metrics or {},
        "dimensions": dimensions or {},
    }
    if reason_code is not None:
        value["reason_code"] = reason_code
    return value


def _append_start_events(project_root, request, planned_route, runtime_reference):
    run_id = request["run_id"]
    parent_refs = [runtime_reference]
    if request["parent_run_id"] is not None:
        parent_refs.append({"kind": "run", "ref": request["parent_run_id"]})
    started = runtime.append_event(project_root, run_id, _event_request(
        run_id, "controller-start-v1", "run_started", request["as_of"], None, "started",
        {"kind": "run", "ref": run_id}, references=parent_refs,
    ))
    route = runtime.append_event(project_root, run_id, _event_request(
        run_id, "controller-route-" + request["turn_id"], "route_selected",
        request["as_of"], started["event"]["event_id"], "succeeded",
        {"kind": "route", "ref": planned_route["target_skill"]},
        reason_code=planned_route["reason_code"], dimensions={
            "route_transition": "initial", "route_command": planned_route["command"],
        },
    ))
    turn = runtime.append_event(project_root, run_id, _event_request(
        run_id, "controller-turn-" + request["turn_id"], "turn_started",
        request["as_of"], route["event"]["event_id"], "started",
        {"kind": "turn", "ref": request["turn_id"]}, turn_id=request["turn_id"],
    ))
    return started, route, turn


def _manifest_reference(project_root, manifest, digest):
    relative = "memory/runs/%s/turns/%s/context-manifest.json" % (
        manifest["run_id"], manifest["turn_id"],
    )
    _path, raw, metadata = runtime._stable_project_read(
        project_root, relative, runtime.MAX_CONTEXT_MANIFEST_BYTES, "context manifest",
    )
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ControllerError("installed context manifest digest changed")
    return {
        "ref": relative,
        "sha256": digest,
        "bytes": metadata.st_size,
        "token_estimate": None,
        "estimator": None,
        "context_signature": manifest["context_signature"],
    }


def _parent_run_id(events):
    parents = [item for item in events[0]["references"] if item["kind"] == "run"]
    if len(parents) > 1:
        raise ControllerError("run_started has ambiguous parent run references")
    return parents[0]["ref"] if parents else None


def start_run(
        project_root, request, *, bundle_root=ROOT, profile=None, environ=None):
    request = validate_start_request(request)
    profile_resolution = profile_runtime.require_new_run(
        project_root, bundle_root=bundle_root, cli_profile=profile,
        environ=environ,
    )
    project_root = runtime.normalized_root(project_root)
    bundle_root = resolver.normalized_root(bundle_root, "bundle root")
    budget = request["budget"]
    planned = planner.build_request(
        skill=request["route"]["target_skill"], run_id=request["run_id"],
        turn_id=request["turn_id"], as_of=request["as_of"], project_root=project_root,
        bundle_root=bundle_root, command=request["route"]["command"],
        reason_code=request["route"]["reason_code"], max_tokens=budget["max_tokens"],
        bytes_per_token=budget["bytes_per_token"], max_resources=budget["max_resources"],
        max_sensitivity=budget["max_sensitivity"],
        prefix_file_limit=budget["prefix_file_limit"],
        registry_offsets=request["registry_offsets"],
    )
    planner.validate_planned_request(
        planned, bundle_root=bundle_root, project_root=project_root, resolve_sources=True,
    )
    manifest = resolver.resolve_context(planned, bundle_root, project_root)
    start_result = None
    try:
        start_result, _route_result, turn_result = _append_start_events(
            project_root, request, manifest["route"], {
                "kind": "source",
                "ref": profile_resolution["runtime_identity"]["ref"],
                "sha256": profile_resolution["runtime_identity"]["sha256"],
            },
        )
        _stream, _projection, run_dir = runtime.run_paths(
            project_root, request["run_id"], create=True,
        )
        runtime.ensure_child_directories(project_root, run_dir, ["turns", request["turn_id"]])
        manifest_relative = "memory/runs/%s/turns/%s/context-manifest.json" % (
            request["run_id"], request["turn_id"],
        )
        manifest_sha, manifest_existed = resolver.write_manifest(
            project_root, manifest_relative, manifest,
        )
        context_event = runtime.append_event(project_root, request["run_id"], _event_request(
            request["run_id"], "controller-context-" + request["turn_id"],
            "context_resolved", request["as_of"], turn_result["event"]["event_id"],
            "succeeded", {"kind": "context", "ref": request["turn_id"]},
            turn_id=request["turn_id"], references=[{
                "kind": "context-manifest", "ref": manifest_relative, "sha256": manifest_sha,
            }], metrics={
                "selected_bytes": manifest["budget"]["selected_bytes"],
                "selected_resources": manifest["budget"]["selected_resources"],
            },
        ))
        manifest_ref = _manifest_reference(project_root, manifest, manifest_sha)
        snapshot_id = str(uuid.uuid5(
            CONTROLLER_NAMESPACE, request["run_id"] + ":" + request["turn_id"],
        ))
        snapshot_value = {
            "schema_version": SCHEMA_VERSION,
            "snapshot_id": snapshot_id,
            "run_id": request["run_id"],
            "turn_id": request["turn_id"],
            "parent_turn_id": None,
            "created_at": request["as_of"],
            "skill": {
                "name": manifest["route"]["target_skill"],
                "version": manifest["route"]["skill_version"],
                "contract_sha256": manifest["route"]["skill_sha256"],
            },
            "host": request["host"],
            "system_prompt_sha256": request["system_prompt_sha256"],
            "context_manifest": manifest_ref,
            "tools": request["tools"],
            "toolset_sha256": runtime.sha256_json(request["tools"]),
            "registry_offsets": manifest["registry_offsets"],
            "permission_profile": request["permission_profile"],
        }
        snapshot = runtime.write_snapshot(project_root, request["run_id"], snapshot_value)
        events = runtime.load_events(project_root, request["run_id"])
        state = runtime.project_events(request["run_id"], events)
        return {
            "schema_version": SCHEMA_VERSION,
            "operation": "start",
            "run_id": request["run_id"],
            "status": state["status"],
            "route": manifest["route"],
            "machine_contract": manifest["request"]["planner"]["skill_contract"],
            "context_manifest": {
                "ref": manifest_ref["ref"], "sha256": manifest_ref["sha256"],
                "context_signature": manifest_ref["context_signature"],
            },
            "snapshot": snapshot["artifact"],
            "permission_profile": request["permission_profile"],
            "head": _head(state),
            "deduplicated": bool(
                start_result["deduplicated"] or context_event["deduplicated"]
                or snapshot["deduplicated"] or manifest_existed
            ),
        }
    except Exception:
        if start_result is not None and not start_result["deduplicated"]:
            _best_effort_failed_open(project_root, request)
        raise


def _best_effort_failed_open(project_root, request):
    """Seal only a run created by this failed invocation; never alter a prior run."""
    try:
        events = runtime.load_events(project_root, request["run_id"])
        state = runtime.project_events(request["run_id"], events)
        if state["status"] != "active":
            return
        value = {
            "schema_version": SCHEMA_VERSION,
            "run_id": request["run_id"],
            "parent_run_id": _parent_run_id(events),
            "started_at": state["started_at"],
            "ended_at": request["as_of"],
            "status": "failed",
            "evidence_mode": "none",
            "route": None,
            "context_manifests": [],
            "last_event_id": state["head_event_id"],
            "last_event_offset": state["last_offset"],
            "last_event_hash": state["last_event_hash"],
            "save_point": None,
            "registry_offsets": {name: None for name in runtime.REGISTRIES},
            "artifacts": [],
            "metrics": {"turns": 0, "tool_calls": 0, "controller_open_failure": 1},
            "failure_class": "context",
            "next_action": {"code": "inspect-controller-failure"},
        }
        runtime.finish_run(project_root, request["run_id"], value)
    except Exception:
        return


def _ancestry_at(events, expected_head):
    matches = [event for event in events if event["event_id"] == expected_head["event_id"]]
    if len(matches) != 1:
        raise ControllerError("expected_head.event_id is absent from the verified run")
    event = matches[0]
    if event["offset"] != expected_head["offset"] or event["event_hash"] != expected_head["hash"]:
        raise ControllerError("expected_head offset/hash does not match the verified event")
    return runtime.event_ancestry(events, event["event_id"])


def _require_current_head(state, expected):
    if _head(state) != expected:
        raise ControllerError("expected_head is stale; resume and retry against the verified head")


def checkpoint_run(
        project_root, run_id, request, *, bundle_root=ROOT, profile=None,
        environ=None):
    runtime.validate_uuid(run_id, "run_id")
    request = validate_checkpoint_request(request)
    profile_runtime.require_existing_run(
        project_root, run_id, bundle_root=bundle_root, cli_profile=profile,
        environ=environ,
    )
    project_root = runtime.normalized_root(project_root)
    events = runtime.load_events(project_root, run_id)
    ancestry = _ancestry_at(events, request["expected_head"])
    expected_state = runtime.project_events(run_id, ancestry)
    checkpoint_relative = "memory/runs/%s/save-points/%s.json" % (
        run_id, request["checkpoint_id"],
    )
    target = project_root / checkpoint_relative
    if not target.exists():
        current_state = runtime.project_events(run_id, events)
        _require_current_head(current_state, request["expected_head"])
    snapshots = runtime.selected_branch_snapshots(
        project_root, run_id, ancestry, expected_state,
    )
    if not snapshots:
        raise ControllerError("checkpoint requires a verified turn snapshot")
    _snapshot_event, snapshot_document = snapshots[-1]
    snapshot_ref = {
        "ref": expected_state["last_turn_snapshot_ref"],
        "sha256": expected_state["last_turn_snapshot_sha256"],
    }
    context_ref = {
        field: snapshot_document["context_manifest"][field]
        for field in ("ref", "sha256", "context_signature")
    }
    save_value = {
        "schema_version": SCHEMA_VERSION,
        "save_point_id": request["checkpoint_id"],
        "run_id": run_id,
        "turn_id": snapshot_document["turn_id"],
        "created_at": request["occurred_at"],
        "last_event_id": request["expected_head"]["event_id"],
        "last_event_offset": request["expected_head"]["offset"],
        "last_event_hash": request["expected_head"]["hash"],
        "status": request["status"],
        "turn_snapshot": snapshot_ref,
        "context_manifest": context_ref,
        "artifacts": request["artifacts"],
        "registry_offsets": snapshot_document["registry_offsets"],
        "visited_skills": expected_state["route_chain"],
        "chain_depth": expected_state["automatic_handoff_depth"],
        "pending_handoff": request["pending_handoff"],
        "next_action": request["next_action"],
    }
    saved = runtime.write_save_point(project_root, run_id, save_value)
    state = runtime.project_events(run_id, runtime.load_events(project_root, run_id))
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "checkpoint",
        "run_id": run_id,
        "status": request["status"],
        "save_point": saved["artifact"],
        "head": _head(state),
        "deduplicated": saved["deduplicated"],
    }


def _context_for_snapshot(project_root, run_id, snapshot_document, *, verify_sources):
    reference = snapshot_document["context_manifest"]
    return runtime.validate_context_document(
        project_root, reference["ref"], reference["sha256"],
        reference["context_signature"], run_id, snapshot_document["turn_id"],
        verify_sources=verify_sources,
    )[1]


def _build_envelope(project_root, run_id, request, ancestry):
    state = runtime.project_events(run_id, ancestry)
    snapshots = runtime.selected_branch_snapshots(project_root, run_id, ancestry, state)
    contexts = []
    context_documents = []
    for _event, snapshot in snapshots:
        ref = snapshot["context_manifest"]
        contexts.append({
            "ref": ref["ref"], "sha256": ref["sha256"],
            "context_signature": ref["context_signature"],
        })
        context_documents.append(
            _context_for_snapshot(project_root, run_id, snapshot, verify_sources=True)
        )
    if not contexts:
        raise ControllerError("finish requires a verified turn snapshot")
    terminal_context = context_documents[-1]
    selected_ids = set(state["selected_path_event_ids"])
    selected = [event for event in ancestry if event["event_id"] in selected_ids]
    derived_metrics = {
        "controller.turns": len(snapshots),
        "controller.tool_calls": sum(e["event_type"] == "tool_requested" for e in selected),
        "controller.checkpoints": sum(e["event_type"] == "save_point_created" for e in selected),
        "controller.loops": len(state["loop_states"]),
        "controller.automatic_handoffs": state["automatic_handoff_depth"],
        "controller.context_resources": sum(
            item["budget"]["selected_resources"] for item in context_documents
        ),
    }
    metrics = dict(request["metrics"])
    metrics.update(derived_metrics)
    save_point = None
    if state["last_save_point_ref"] is not None:
        save_point = {
            "ref": state["last_save_point_ref"],
            "sha256": state["last_save_point_sha256"],
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "parent_run_id": _parent_run_id(ancestry),
        "started_at": state["started_at"],
        # Bind every finish request, including a resumable wait, to its explicit
        # operation timestamp. This makes conflicting retries observable instead
        # of collapsing two distinct wait requests onto the same envelope.
        "ended_at": request["occurred_at"],
        "status": request["status"],
        "evidence_mode": request["evidence_mode"],
        "route": {
            "skill": terminal_context["route"]["target_skill"],
            "version": terminal_context["route"]["skill_version"],
            "reason_code": terminal_context["route"]["reason_code"],
        },
        "context_manifests": contexts,
        "last_event_id": request["expected_head"]["event_id"],
        "last_event_offset": request["expected_head"]["offset"],
        "last_event_hash": request["expected_head"]["hash"],
        "save_point": save_point,
        "registry_offsets": terminal_context["registry_offsets"],
        "artifacts": request["artifacts"],
        "metrics": metrics,
        "failure_class": request["failure_class"],
        "next_action": request["next_action"],
    }


def finish_run(
        project_root, run_id, request, *, bundle_root=ROOT, profile=None,
        environ=None):
    runtime.validate_uuid(run_id, "run_id")
    request = validate_finish_request(request)
    profile_runtime.require_existing_run(
        project_root, run_id, bundle_root=bundle_root, cli_profile=profile,
        environ=environ,
    )
    project_root = runtime.normalized_root(project_root)
    events = runtime.load_events(project_root, run_id)
    ancestry = _ancestry_at(events, request["expected_head"])
    envelope_relative = "memory/runs/%s/envelopes/%s.json" % (
        run_id, request["expected_head"]["event_id"],
    )
    if not (project_root / envelope_relative).exists():
        _require_current_head(runtime.project_events(run_id, events), request["expected_head"])
    envelope = _build_envelope(project_root, run_id, request, ancestry)
    finished = runtime.finish_run(project_root, run_id, envelope)
    state = runtime.project_events(run_id, runtime.load_events(project_root, run_id))
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "finish",
        "run_id": run_id,
        "status": request["status"],
        "evidence_mode": request["evidence_mode"],
        "envelope": finished["artifact"],
        "head": _head(state),
        "deduplicated": finished["deduplicated"],
    }


def resume_run(
        project_root, run_id, max_bytes=8192, *, bundle_root=ROOT, profile=None,
        environ=None):
    runtime.validate_uuid(run_id, "run_id")
    profile_runtime.require_existing_run(
        project_root, run_id, bundle_root=bundle_root, cli_profile=profile,
        environ=environ,
    )
    project_root = runtime.normalized_root(project_root)
    events = runtime.load_events(project_root, run_id)
    state = runtime.project_events(run_id, events)
    summary = runtime.resume_summary(project_root, run_id, max_bytes)
    snapshots = runtime.selected_branch_snapshots(project_root, run_id, events, state)
    binding = None
    if snapshots:
        _event, snapshot = snapshots[-1]
        manifest = _context_for_snapshot(
            project_root, run_id, snapshot, verify_sources=True,
        )
        binding = {
            "turn_id": snapshot["turn_id"],
            "machine_contract": manifest["request"]["planner"]["skill_contract"],
            "context_manifest": {
                field: snapshot["context_manifest"][field]
                for field in ("ref", "sha256", "context_signature")
            },
            "permission_profile": snapshot["permission_profile"],
        }
    if state["last_save_point_ref"] is not None:
        runtime.validate_save_point_document(
            project_root, state["last_save_point_ref"],
            state["last_save_point_sha256"], run_id,
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "operation": "resume",
        "run_id": run_id,
        "resumable": state["status"] in {"active", "waiting"},
        "verified_summary": summary,
        "latest_binding": binding,
        "head": _head(state),
    }


def _output(value, compact=False):
    if compact:
        print(runtime.canonical_json(value))
    else:
        print(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="project root (default: current directory)")
    parser.add_argument("--bundle-root", default=str(ROOT), help="immutable skills bundle root")
    parser.add_argument(
        "--profile", choices=profile_runtime.PROFILE_NAMES,
        help="one-invocation requested capability profile; does not persist config",
    )
    parser.add_argument("--compact", action="store_true")
    sub = parser.add_subparsers(dest="operation", required=True)
    start = sub.add_parser("start", help="plan context and create the initial immutable turn")
    start.add_argument("request")
    checkpoint = sub.add_parser("checkpoint", help="create a verified save point")
    checkpoint.add_argument("run_id")
    checkpoint.add_argument("request")
    finish = sub.add_parser("finish", help="write a waiting or terminal run envelope")
    finish.add_argument("run_id")
    finish.add_argument("request")
    resume = sub.add_parser("resume", help="rebuild and live-verify resumable state")
    resume.add_argument("run_id")
    resume.add_argument("--max-bytes", type=int, default=8192)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.operation == "start":
            value = start_run(
                args.root, runtime.read_json(args.request, "controller start request"),
                bundle_root=args.bundle_root, profile=args.profile,
            )
        elif args.operation == "checkpoint":
            value = checkpoint_run(
                args.root, args.run_id,
                runtime.read_json(args.request, "controller checkpoint request"),
                bundle_root=args.bundle_root, profile=args.profile,
            )
        elif args.operation == "finish":
            value = finish_run(
                args.root, args.run_id,
                runtime.read_json(args.request, "controller finish request"),
                bundle_root=args.bundle_root, profile=args.profile,
            )
        else:
            value = resume_run(
                args.root, args.run_id, args.max_bytes,
                bundle_root=args.bundle_root, profile=args.profile,
            )
        _output(value, args.compact)
        return 0
    except (
            ControllerError, planner.ContextPlanError, resolver.ContextResolutionError,
            profile_runtime.ProfileError, runtime.RunEventError, OSError, ValueError,
    ) as exc:
        print("runtime-controller: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
