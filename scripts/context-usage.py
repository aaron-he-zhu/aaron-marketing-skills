#!/usr/bin/env python3
"""Create, validate, and summarize context-usage-v1 telemetry records.

The record keeps deterministic byte counts separate from provider-reported
tokens.  Unavailable provider fields remain JSON ``null``; the tool never
estimates them or relabels the repository's byte proxy as model tokens.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import statistics
import sys


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "evals" / "context-usage-v1.schema.json"
CONTEXT_ASSEMBLY_SCRIPT = ROOT / "scripts" / "context-assembly.py"
CONTEXT_RESOLVER_SCRIPT = ROOT / "scripts" / "context-resolver.py"
MAX_DOCUMENT_BYTES = 8_000_000
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")

TOP_FIELDS = {
    "schema_version", "record_id", "recorded_at", "route", "profiles",
    "experiment", "context", "provider", "outcome", "provenance",
}
ROUTE_FIELDS = {"command", "target_skill", "reason_code"}
PROFILE_FIELDS = {"capability", "prompt", "host"}
CONTEXT_FIELDS = {
    "context_signature", "request_sha256", "bytes", "tokens", "resources",
    "disclosure", "reference_bytes_by_reason",
}
EXPERIMENT_FIELDS = {
    "pair_id", "arm_id", "repeat_index", "randomized_order",
    "context_profile_sha256", "prompt_sha256", "toolset_sha256",
}
BYTE_FIELDS = {
    "discovery", "repository_instructions", "control_plane",
    "model_visible_static", "tool_schemas", "references", "evidence",
    "required_total", "selected_total", "capacity",
}
TOKEN_FIELDS = {"input", "cache_creation", "cache_read", "output", "reasoning"}
RESOURCE_FIELDS = {"candidates", "required", "selected", "omitted"}
DISCLOSURE_FIELDS = {"events", "required", "satisfied", "recall", "precision"}
PROVIDER_FIELDS = {"name", "model_id", "model_revision"}
OUTCOME_FIELDS = {
    "status", "route_outcome", "task_outcome", "latency_ms", "tool_calls",
    "cost_usd",
}
PROVENANCE_FIELDS = {"source", "manifest_sha256", "notes"}
REFERENCE_FIELDS = {"reason_code", "bytes", "resources"}
ASSEMBLY_PROFILE_FIELDS = {
    "host_profile", "model_id", "model_revision", "distribution_profile",
    "physical_distribution_kind", "planner_distribution_profile",
    "distribution_evaluation_only",
    "distribution_manifest_sha256", "prompt_profile", "prompt_profile_source",
    "binding_id", "always_on_overlays", "catalogs",
}
ASSEMBLY_USAGE_FIELDS = {
    "manifest_selected_bytes", "controller_body_bytes", "model_body_bytes",
    "tool_body_bytes", "deferred_bytes", "model_reduction_bytes",
    "model_reduction_ratio",
}
ASSEMBLY_RESOURCE_FIELDS = {
    "resource_id", "scope", "path", "sha256", "bytes", "body_bytes",
    "role", "module_id", "materialization", "load_policy",
    "source_resource_id",
}


class ContextUsageError(ValueError):
    pass


def _reject_constant(value):
    raise ContextUsageError("non-finite JSON number: %s" % value)


def _reject_duplicates(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ContextUsageError("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def strict_json_loads(raw, label):
    try:
        return json.loads(
            raw, object_pairs_hook=_reject_duplicates, parse_constant=_reject_constant,
        )
    except ContextUsageError:
        raise
    except (TypeError, ValueError, RecursionError) as exc:
        raise ContextUsageError("%s is not strict JSON" % label) from exc


def load_json(path, label):
    path = Path(path)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContextUsageError("cannot read %s: %s" % (label, exc)) from exc
    if len(raw) > MAX_DOCUMENT_BYTES:
        raise ContextUsageError("%s exceeds %d bytes" % (label, MAX_DOCUMENT_BYTES))
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextUsageError("%s must be UTF-8" % label) from exc
    return strict_json_loads(text, label), raw


def _exact(value, fields, label):
    if not isinstance(value, dict) or set(value) != fields:
        raise ContextUsageError("%s keys must be exactly %s" % (label, sorted(fields)))
    return value


def _nullable_text(value, label, maximum=500):
    if value is None:
        return
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise ContextUsageError("%s must be null or non-empty text" % label)


def _nullable_sha(value, label):
    if value is not None and (not isinstance(value, str) or not SHA256.fullmatch(value)):
        raise ContextUsageError("%s must be null or lowercase SHA-256" % label)


def _nullable_count(value, label, *, positive=False):
    if value is None:
        return
    minimum = 1 if positive else 0
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ContextUsageError("%s must be null or an integer >= %d" % (label, minimum))


def _timestamp(value, label):
    if not isinstance(value, str) or len(value) > 128:
        raise ContextUsageError("%s must be an RFC 3339 timestamp" % label)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContextUsageError("%s must be an RFC 3339 timestamp" % label) from exc
    if parsed.tzinfo is None:
        raise ContextUsageError("%s must include a timezone" % label)


def validate_record(record):
    _exact(record, TOP_FIELDS, "record")
    if record["schema_version"] != "1.0":
        raise ContextUsageError("schema_version must be 1.0")
    if not isinstance(record["record_id"], str) or not SAFE_ID.fullmatch(record["record_id"]):
        raise ContextUsageError("record_id is invalid")
    _timestamp(record["recorded_at"], "recorded_at")

    route = _exact(record["route"], ROUTE_FIELDS, "route")
    for field in ROUTE_FIELDS:
        _nullable_text(route[field], "route.%s" % field, 160)
    profiles = _exact(record["profiles"], PROFILE_FIELDS, "profiles")
    for field in PROFILE_FIELDS:
        _nullable_text(profiles[field], "profiles.%s" % field, 160)
    experiment = _exact(record["experiment"], EXPERIMENT_FIELDS, "experiment")
    for field in ("pair_id", "arm_id"):
        value = experiment[field]
        if value is not None and (
                not isinstance(value, str) or not SAFE_ID.fullmatch(value)):
            raise ContextUsageError("experiment.%s is invalid" % field)
    for field in ("repeat_index", "randomized_order"):
        _nullable_count(experiment[field], "experiment.%s" % field)
    for field in ("context_profile_sha256", "prompt_sha256", "toolset_sha256"):
        _nullable_sha(experiment[field], "experiment.%s" % field)

    context = _exact(record["context"], CONTEXT_FIELDS, "context")
    _nullable_sha(context["context_signature"], "context.context_signature")
    _nullable_sha(context["request_sha256"], "context.request_sha256")
    byte_metrics = _exact(context["bytes"], BYTE_FIELDS, "context.bytes")
    for field in BYTE_FIELDS:
        _nullable_count(
            byte_metrics[field], "context.bytes.%s" % field,
            positive=field == "capacity",
        )
    required = byte_metrics["required_total"]
    selected = byte_metrics["selected_total"]
    capacity = byte_metrics["capacity"]
    if required is not None and selected is not None and required > selected:
        raise ContextUsageError("required_total cannot exceed selected_total")
    if selected is not None and capacity is not None and selected > capacity:
        raise ContextUsageError("selected_total cannot exceed capacity")
    token_metrics = _exact(context["tokens"], TOKEN_FIELDS, "context.tokens")
    for field in TOKEN_FIELDS:
        _nullable_count(token_metrics[field], "context.tokens.%s" % field)
    resources = _exact(context["resources"], RESOURCE_FIELDS, "context.resources")
    for field in RESOURCE_FIELDS:
        _nullable_count(resources[field], "context.resources.%s" % field)
    if (
            resources["required"] is not None and resources["selected"] is not None
            and resources["required"] > resources["selected"]):
        raise ContextUsageError("required resources cannot exceed selected resources")
    disclosure = _exact(context["disclosure"], DISCLOSURE_FIELDS, "context.disclosure")
    for field in ("events", "required", "satisfied"):
        _nullable_count(disclosure[field], "context.disclosure.%s" % field)
    if (
            disclosure["required"] is not None and disclosure["satisfied"] is not None
            and disclosure["satisfied"] > disclosure["required"]):
        raise ContextUsageError("disclosure satisfied cannot exceed required")
    for field in ("recall", "precision"):
        value = disclosure[field]
        if value is not None and (
                not isinstance(value, (int, float)) or isinstance(value, bool)
                or value < 0 or value > 1):
            raise ContextUsageError("context.disclosure.%s must be null or 0..1" % field)
    references = context["reference_bytes_by_reason"]
    if not isinstance(references, list) or len(references) > 256:
        raise ContextUsageError("reference_bytes_by_reason must be an array up to 256 items")
    seen_reasons = set()
    for index, item in enumerate(references):
        _exact(item, REFERENCE_FIELDS, "reference_bytes_by_reason[%d]" % index)
        reason = item["reason_code"]
        if not isinstance(reason, str) or not SAFE_ID.fullmatch(reason):
            raise ContextUsageError("reference reason_code is invalid")
        if reason in seen_reasons:
            raise ContextUsageError("reference reason_code values must be unique")
        seen_reasons.add(reason)
        _nullable_count(item["bytes"], "reference bytes")
        _nullable_count(item["resources"], "reference resources")

    provider = _exact(record["provider"], PROVIDER_FIELDS, "provider")
    for field in PROVIDER_FIELDS:
        _nullable_text(provider[field], "provider.%s" % field, 500)
    outcome = _exact(record["outcome"], OUTCOME_FIELDS, "outcome")
    if outcome["status"] not in {None, "measured", "passed", "failed", "inconclusive"}:
        raise ContextUsageError("outcome.status is invalid")
    for field in ("route_outcome", "task_outcome"):
        _nullable_text(outcome[field], "outcome.%s" % field, 500)
    for field in ("latency_ms", "tool_calls"):
        _nullable_count(outcome[field], "outcome.%s" % field)
    cost = outcome["cost_usd"]
    if cost is not None and (
            not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0):
        raise ContextUsageError("outcome.cost_usd must be null or non-negative")
    provenance = _exact(record["provenance"], PROVENANCE_FIELDS, "provenance")
    if provenance["source"] not in {
            "manifest", "assembly", "adapter", "static-baseline", "manual"}:
        raise ContextUsageError("provenance.source is invalid")
    _nullable_sha(provenance["manifest_sha256"], "provenance.manifest_sha256")
    notes = provenance["notes"]
    if (
            not isinstance(notes, list) or len(notes) > 32
            or any(not isinstance(item, str) or not item or len(item) > 500 for item in notes)):
        raise ContextUsageError("provenance.notes must contain up to 32 bounded strings")
    return record


def _nullable_metrics(fields):
    return {field: None for field in fields}


def _load_context_resolver_module():
    try:
        spec = importlib.util.spec_from_file_location(
            "context_usage_context_resolver", CONTEXT_RESOLVER_SCRIPT,
        )
        if spec is None or spec.loader is None:
            raise ContextUsageError("cannot load context manifest validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (ImportError, OSError, AttributeError, TypeError) as exc:
        raise ContextUsageError("cannot load context manifest validator: %s" % exc) from exc


def _validated_manifest(manifest):
    """Validate manifest structure, identity hashes, and semantic arithmetic."""
    module = _load_context_resolver_module()
    try:
        module.validate_manifest(manifest)
        return (
            manifest["route"], manifest["budget"], manifest["request"],
            manifest["resources"], manifest["omitted"],
        )
    except (KeyError, TypeError, ValueError, IndexError, AttributeError) as exc:
        raise ContextUsageError("context manifest is invalid: %s" % exc) from exc


def record_from_manifest(manifest, raw, args):
    route, budget, request, resources, omitted = _validated_manifest(manifest)
    reason_totals = {}
    for resource in resources:
        reason = resource["reason_code"]
        size = resource["bytes"]
        total = reason_totals.setdefault(reason, {"bytes": 0, "resources": 0})
        total["bytes"] += size
        total["resources"] += 1
    required_resources = sum(
        resource["requirement"] == "required" for resource in resources
    )
    byte_metrics = _nullable_metrics(BYTE_FIELDS)
    byte_metrics.update({
        "required_total": sum(
            item["bytes"] for item in resources
            if item["requirement"] == "required"
        ),
        "selected_total": budget["selected_bytes"],
        "capacity": budget["max_bytes"],
    })
    record = {
        "schema_version": "1.0",
        "record_id": args.record_id,
        "recorded_at": args.recorded_at,
        "route": {
            "command": route["command"],
            "target_skill": route["target_skill"],
            "reason_code": route["reason_code"],
        },
        "profiles": {
            "capability": args.capability_profile,
            "prompt": args.prompt_profile,
            "host": args.host_profile,
        },
        "experiment": {
            "pair_id": None, "arm_id": None, "repeat_index": None,
            "randomized_order": None, "context_profile_sha256": None,
            "prompt_sha256": None, "toolset_sha256": None,
        },
        "context": {
            "context_signature": manifest.get("context_signature"),
            "request_sha256": manifest.get("request_sha256"),
            "bytes": byte_metrics,
            "tokens": _nullable_metrics(TOKEN_FIELDS),
            "resources": {
                "candidates": len(request["candidates"]),
                "required": required_resources,
                "selected": budget["selected_resources"],
                "omitted": len(omitted),
            },
            "disclosure": {
                "events": None, "required": None, "satisfied": None,
                "recall": None, "precision": None,
            },
            "reference_bytes_by_reason": [
                {"reason_code": reason, **reason_totals[reason]}
                for reason in sorted(reason_totals)
            ],
        },
        "provider": {"name": None, "model_id": None, "model_revision": None},
        "outcome": {
            "status": "measured", "route_outcome": None, "task_outcome": None,
            "latency_ms": None, "tool_calls": None, "cost_usd": None,
        },
        "provenance": {
            "source": "manifest",
            "manifest_sha256": hashlib.sha256(raw).hexdigest(),
            "notes": [
                "Manifest bytes are deterministic; provider token fields are unavailable and remain null.",
                "selected_total is not assumed to equal model_visible_static until consumer boundaries are recorded.",
            ],
        },
    }
    return validate_record(record)


def _load_context_assembly_module():
    try:
        spec = importlib.util.spec_from_file_location(
            "context_usage_context_assembly", CONTEXT_ASSEMBLY_SCRIPT,
        )
        if spec is None or spec.loader is None:
            raise ContextUsageError("cannot load context assembly validator")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except (ImportError, OSError, AttributeError, TypeError) as exc:
        raise ContextUsageError("cannot load context assembly validator: %s" % exc) from exc


def _validated_assembly(assembly):
    """Validate the hash-bound assembly and the fields used by this projection."""
    module = _load_context_assembly_module()
    try:
        module.validate_assembly(assembly)
        route = _exact(assembly["route"], {"command", "target_skill"}, "assembly.route")
        profile = _exact(
            assembly["profile"], ASSEMBLY_PROFILE_FIELDS, "assembly.profile",
        )
        usage = _exact(assembly["usage"], ASSEMBLY_USAGE_FIELDS, "assembly.usage")
        consumers = _exact(
            assembly["consumers"], {"controller", "model", "tool", "deferred"},
            "assembly.consumers",
        )
    except (KeyError, TypeError, ValueError, IndexError, AttributeError) as exc:
        raise ContextUsageError("context assembly is invalid: %s" % exc) from exc

    for field in ("command", "target_skill"):
        _nullable_text(route[field], "assembly.route.%s" % field, 160)
        if route[field] is None:
            raise ContextUsageError("assembly.route.%s cannot be null" % field)
    for field in ("host_profile", "model_id", "prompt_profile"):
        _nullable_text(profile[field], "assembly.profile.%s" % field, 160)
        if profile[field] is None:
            raise ContextUsageError("assembly.profile.%s cannot be null" % field)
    _nullable_text(
        profile["model_revision"], "assembly.profile.model_revision", 256,
    )
    if profile["distribution_profile"] not in {
            "repository", "lite", "pro", "governed"}:
        raise ContextUsageError("assembly.profile.distribution_profile is invalid")
    if profile["physical_distribution_kind"] not in {
            "repository", "plugin"}:
        raise ContextUsageError(
            "assembly.profile.physical_distribution_kind is invalid"
        )
    if profile["planner_distribution_profile"] not in {
            "repository", "plugin", "standalone-skill"}:
        raise ContextUsageError(
            "assembly.profile.planner_distribution_profile is invalid"
        )
    if not isinstance(profile["distribution_evaluation_only"], bool):
        raise ContextUsageError(
            "assembly.profile.distribution_evaluation_only must be boolean"
        )
    _nullable_sha(
        profile["distribution_manifest_sha256"],
        "assembly.profile.distribution_manifest_sha256",
    )
    for field in ASSEMBLY_USAGE_FIELDS - {"model_reduction_ratio"}:
        _nullable_count(usage[field], "assembly.usage.%s" % field)
        if usage[field] is None:
            raise ContextUsageError("assembly.usage.%s cannot be null" % field)
    ratio = usage["model_reduction_ratio"]
    if (
            not isinstance(ratio, (int, float)) or isinstance(ratio, bool)
            or ratio < 0 or ratio > 1):
        raise ContextUsageError("assembly.usage.model_reduction_ratio must be 0..1")

    measured = {}
    for consumer, resources in consumers.items():
        if not isinstance(resources, list) or len(resources) > 256:
            raise ContextUsageError("assembly consumer resources are invalid")
        body_bytes = 0
        total_bytes = 0
        for index, resource in enumerate(resources):
            _exact(
                resource, ASSEMBLY_RESOURCE_FIELDS,
                "assembly.consumers.%s[%d]" % (consumer, index),
            )
            for field in ("resource_id", "role", "module_id"):
                value = resource[field]
                if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
                    raise ContextUsageError(
                        "assembly resource %s is invalid" % field
                    )
            source_id = resource["source_resource_id"]
            if source_id is not None and (
                    not isinstance(source_id, str) or not SAFE_ID.fullmatch(source_id)):
                raise ContextUsageError(
                    "assembly resource source_resource_id is invalid"
                )
            _nullable_sha(resource["sha256"], "assembly resource sha256")
            if resource["sha256"] is None:
                raise ContextUsageError("assembly resource sha256 cannot be null")
            _nullable_count(resource["bytes"], "assembly resource bytes")
            _nullable_count(resource["body_bytes"], "assembly resource body_bytes")
            body_bytes += resource["body_bytes"]
            total_bytes += resource["bytes"]
        measured[consumer] = {"body_bytes": body_bytes, "bytes": total_bytes}

    expected = {
        "controller_body_bytes": measured["controller"]["body_bytes"],
        "model_body_bytes": measured["model"]["body_bytes"],
        "tool_body_bytes": measured["tool"]["body_bytes"],
        "deferred_bytes": measured["deferred"]["bytes"],
    }
    for field, value in expected.items():
        if usage[field] != value:
            raise ContextUsageError(
                "assembly.usage.%s does not match consumer resources" % field
            )
    return route, profile, usage, consumers


def record_from_assembly(assembly, raw, args):
    """Project integrity-checked consumer assembly measurements into telemetry."""
    route, profile, usage, consumers = _validated_assembly(assembly)
    reference_totals = {}
    for resource in consumers["deferred"]:
        reason = resource["module_id"]
        total = reference_totals.setdefault(reason, {"bytes": 0, "resources": 0})
        total["bytes"] += resource["bytes"]
        total["resources"] += 1
    selected_sources = {
        resource["source_resource_id"] or resource["resource_id"]
        for resources in consumers.values()
        for resource in resources
    }
    byte_metrics = _nullable_metrics(BYTE_FIELDS)
    byte_metrics.update({
        "control_plane": usage["controller_body_bytes"],
        "model_visible_static": usage["model_body_bytes"],
        "tool_schemas": usage["tool_body_bytes"],
        "references": usage["deferred_bytes"],
        "selected_total": usage["manifest_selected_bytes"],
    })
    assembly_sha256 = hashlib.sha256(raw).hexdigest()
    record = {
        "schema_version": "1.0",
        "record_id": args.record_id,
        "recorded_at": args.recorded_at,
        "route": {
            "command": route["command"],
            "target_skill": route["target_skill"],
            "reason_code": None,
        },
        "profiles": {
            "capability": args.capability_profile,
            "prompt": profile["prompt_profile"],
            "host": profile["host_profile"],
        },
        "experiment": {
            "pair_id": None, "arm_id": None, "repeat_index": None,
            "randomized_order": None, "context_profile_sha256": None,
            "prompt_sha256": None, "toolset_sha256": None,
        },
        "context": {
            "context_signature": assembly["context_signature"],
            "request_sha256": None,
            "bytes": byte_metrics,
            "tokens": _nullable_metrics(TOKEN_FIELDS),
            "resources": {
                "candidates": None, "required": None,
                "selected": len(selected_sources), "omitted": None,
            },
            "disclosure": {
                "events": None, "required": None, "satisfied": None,
                "recall": None, "precision": None,
            },
            "reference_bytes_by_reason": [
                {"reason_code": reason, **reference_totals[reason]}
                for reason in sorted(reference_totals)
            ],
        },
        "provider": {
            "name": None, "model_id": profile["model_id"],
            "model_revision": profile["model_revision"],
        },
        "outcome": {
            "status": "measured", "route_outcome": None, "task_outcome": None,
            "latency_ms": None, "tool_calls": None, "cost_usd": None,
        },
        "provenance": {
            "source": "assembly",
            "manifest_sha256": None,
            "notes": [
                "Assembly document SHA-256: %s; assembly_signature integrity SHA-256: %s."
                % (assembly_sha256, assembly["assembly_signature"]),
                "assembly_signature is an integrity hash, not a cryptographic signature or attestation.",
                "Consumer byte fields are measured from the integrity-checked assembly; provider token fields remain null.",
                "references records the deferred/on-demand consumer bytes and is not model-visible static context.",
                "Distribution identity: %s; manifest SHA-256: %s."
                % (
                    profile["distribution_profile"],
                    profile["distribution_manifest_sha256"] or "unavailable",
                ),
            ],
        },
    }
    return validate_record(record)


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * fraction) + 0.999999) - 1))
    return ordered[index]


def summarize(records):
    fields = ("required_total", "selected_total", "model_visible_static")
    result = {"schema_version": "1.0", "records": len(records), "bytes": {}}
    for field in fields:
        values = [record["context"]["bytes"][field] for record in records]
        values = [value for value in values if value is not None]
        result["bytes"][field] = {
            "observations": len(values),
            "p50": _percentile(values, 0.50),
            "p90": _percentile(values, 0.90),
            "p95": _percentile(values, 0.95),
            "max": max(values) if values else None,
        }
    latencies = [record["outcome"]["latency_ms"] for record in records]
    latencies = [value for value in latencies if value is not None]
    result["latency_ms"] = {
        "observations": len(latencies),
        "median": statistics.median(latencies) if latencies else None,
        "p95": _percentile(latencies, 0.95),
    }
    return result


def write_json(value, output=None):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n"
    if output is None or str(output) == "-":
        sys.stdout.write(text)
        return
    path = Path(output)
    path.write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    validate = subparsers.add_parser("validate", help="validate one context-usage-v1 record")
    validate.add_argument("record")
    from_manifest = subparsers.add_parser(
        "from-manifest", help="project deterministic fields from a context manifest",
    )
    from_manifest.add_argument("--manifest", required=True)
    from_manifest.add_argument("--record-id", required=True)
    from_manifest.add_argument("--recorded-at", required=True)
    from_manifest.add_argument("--capability-profile")
    from_manifest.add_argument("--prompt-profile")
    from_manifest.add_argument("--host-profile")
    from_manifest.add_argument("--output", default="-")
    from_assembly = subparsers.add_parser(
        "from-assembly",
        help="project measured fields from a hash-bound context assembly",
    )
    from_assembly.add_argument("--assembly", required=True)
    from_assembly.add_argument("--record-id", required=True)
    from_assembly.add_argument("--recorded-at", required=True)
    from_assembly.add_argument("--capability-profile")
    from_assembly.add_argument("--output", default="-")
    aggregate = subparsers.add_parser("summarize", help="summarize one or more records")
    aggregate.add_argument("records", nargs="+")
    aggregate.add_argument("--output", default="-")
    args = parser.parse_args(argv)
    try:
        # Loading the schema on every command makes accidental deletion or
        # malformed JSON fail before records are accepted, while the stdlib
        # validator below remains the executable contract.
        schema, _schema_raw = load_json(SCHEMA, "context usage schema")
        if schema.get("title") != "Aaron Marketing Skills context usage record v1":
            raise ContextUsageError("context usage schema identity is invalid")
        if args.operation == "validate":
            record, _raw = load_json(args.record, "context usage record")
            validate_record(record)
            print("context usage record is valid")
            return 0
        if args.operation == "from-manifest":
            manifest, raw = load_json(args.manifest, "context manifest")
            write_json(record_from_manifest(manifest, raw, args), args.output)
            return 0
        if args.operation == "from-assembly":
            assembly, raw = load_json(args.assembly, "context assembly")
            write_json(record_from_assembly(assembly, raw, args), args.output)
            return 0
        records = []
        for path in args.records:
            record, _raw = load_json(path, "context usage record")
            records.append(validate_record(record))
        write_json(summarize(records), args.output)
        return 0
    except (ContextUsageError, OSError, ValueError) as exc:
        print("context-usage: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
