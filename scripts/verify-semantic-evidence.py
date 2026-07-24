#!/usr/bin/env python3
"""Verify current, complete protocol-v2 real-provider semantic evidence.

The verifier reads only bounded provenance/completion data from ignored private
run storage. It reconstructs the selected cases and requests from the current
repository, validates the result hash chain with the existing semantic runner,
and never emits raw prompts or model responses.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "evals" / "semantic-evidence-policy.json"
RUNNER_PATH = ROOT / "scripts" / "run-behavior-evals.py"
POLICY_KEYS = {
    "schema_version", "profile", "minimum_cases", "maximum_age_days",
    "required_execution_mode", "required_status", "require_current_case_selection",
    "require_current_runner", "require_current_protocol_schema",
    "require_project_adapter", "require_single_execution_identity",
    "require_distinct_judge_model", "required_project_adapter_ref",
    "required_project_adapter_dependencies", "require_isolated_project_adapter",
    "require_staged_project_adapter",
}


class EvidenceError(ValueError):
    """Evidence is missing, stale, malformed, or does not bind current inputs."""


def load_runner():
    spec = importlib.util.spec_from_file_location("aaron_behavior_evidence_runner", RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise EvidenceError("cannot load semantic evaluation runner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def strict_policy(value):
    if not isinstance(value, dict) or set(value) != POLICY_KEYS:
        raise EvidenceError("semantic evidence policy has unknown or missing keys")
    if value["schema_version"] != "1.0":
        raise EvidenceError("semantic evidence policy schema_version must be 1.0")
    if value["profile"] not in {"smoke", "nightly"}:
        raise EvidenceError("semantic evidence policy profile must be smoke or nightly")
    for key, lower, upper in (
        ("minimum_cases", 1, 10_000),
        ("maximum_age_days", 1, 365),
    ):
        item = value[key]
        if not isinstance(item, int) or isinstance(item, bool) or not lower <= item <= upper:
            raise EvidenceError("%s must be an integer in %d..%d" % (key, lower, upper))
    if value["required_execution_mode"] != "real":
        raise EvidenceError("required_execution_mode must be real")
    if value["required_status"] != "passed":
        raise EvidenceError("required_status must be passed")
    reference = value["required_project_adapter_ref"]
    if (
            not isinstance(reference, str)
            or not reference.startswith("scripts/")
            or not reference.endswith(".py")):
        raise EvidenceError("required_project_adapter_ref must name a project Python adapter")
    dependencies = value["required_project_adapter_dependencies"]
    if (
            not isinstance(dependencies, list)
            or not dependencies
            or len(dependencies) != len(set(dependencies))
            or any(not isinstance(item, str) or not item.startswith("evals/")
                   for item in dependencies)):
        raise EvidenceError(
            "required_project_adapter_dependencies must be unique project eval references"
        )
    for key in POLICY_KEYS - {
        "schema_version", "profile", "minimum_cases", "maximum_age_days",
            "required_execution_mode", "required_status", "required_project_adapter_ref",
            "required_project_adapter_dependencies",
    }:
        if not isinstance(value[key], bool):
            raise EvidenceError("%s must be boolean" % key)
    return value


def load_policy(path=DEFAULT_POLICY, runner=None):
    runner = runner or load_runner()
    try:
        value = runner.strict_json_loads(Path(path).read_text(encoding="utf-8"), str(path))
    except (OSError, runner.BehaviorEvalError) as exc:
        raise EvidenceError("cannot load semantic evidence policy: %s" % exc) from exc
    return strict_policy(value)


def canonical_request_bytes(runner, requests):
    return b"".join(
        (runner.canonical_json(request) + "\n").encode("utf-8") for request in requests
    )


def stable_bytes(runtime, path, maximum, label):
    try:
        with runtime.anchored_regular_file(path) as handle:
            before = os.fstat(handle.fileno())
            raw = handle.read(maximum + 1)
            after = os.fstat(handle.fileno())
    except (OSError, runtime.RunEventError) as exc:
        raise EvidenceError("cannot read %s: %s" % (label, exc)) from exc
    if len(raw) > maximum:
        raise EvidenceError("%s exceeds its byte bound" % label)
    if (
            len(raw) != before.st_size
            or any(getattr(before, field) != getattr(after, field) for field in (
                "st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns"
            ))):
        raise EvidenceError("%s changed while read" % label)
    return raw


def _manifest_shape(manifest):
    required = {
        "schema_version", "kind", "protocol_version", "run_id", "profile",
        "request_count", "request_stream_sha256", "selection_sha256",
        "adapter_command_sha256", "adapter_command_identity", "runner",
        "protocol_schema", "required_execution_mode",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise EvidenceError("semantic evidence manifest has unknown or missing keys")
    if (
            manifest["schema_version"] != "1.0"
            or manifest["kind"] != "semantic-eval-evidence"
            or manifest["protocol_version"] != "2.0"):
        raise EvidenceError("semantic evidence manifest identity is invalid")


def _project_adapter_current(runner, identity, policy):
    if not isinstance(identity, dict) or set(identity) != {
            "executable_sha256", "executable_size_bytes", "implementation",
            "execution_binding", "runtime_dependencies", "staged_runtime"}:
        raise EvidenceError("adapter command identity is invalid")
    implementation = identity["implementation"]
    if not isinstance(implementation, dict) or set(implementation) != {
            "ref", "sha256", "size_bytes", "argv_index"}:
        raise EvidenceError("adapter implementation identity is invalid")
    reference = implementation.get("ref")
    digest = implementation.get("sha256")
    if reference != policy["required_project_adapter_ref"]:
        raise EvidenceError("real-provider evidence must bind a project adapter implementation")
    if implementation.get("argv_index") != 1:
        raise EvidenceError("project adapter must be the executed Python script at argv[1]")
    try:
        current_raw = runner.project_bytes(reference)
    except runner.BehaviorEvalError as exc:
        raise EvidenceError("cannot verify project adapter implementation: %s" % exc) from exc
    if (
            hashlib.sha256(current_raw).hexdigest() != digest
            or implementation.get("size_bytes") != len(current_raw)):
        raise EvidenceError("semantic adapter implementation has drifted")

    binding = identity["execution_binding"]
    try:
        current_python, python_identity = runner._stable_file_digest(
            sys.executable, 536_870_912, "semantic evidence verifier Python runtime",
        )
    except runner.BehaviorEvalError as exc:
        raise EvidenceError("cannot verify the adapter Python runtime") from exc
    expected_binding = {
        "kind": "isolated-staged-current-python-script",
        "interpreter_path": str(current_python),
        "source_script_argv_index": 1,
        "staged_script_argv_index": 3,
        "python_flags": list(runner.OFFICIAL_ADAPTER_PYTHON_FLAGS),
        "environment_policy": runner.OFFICIAL_ADAPTER_ENVIRONMENT_POLICY,
        "environment_allowlist": list(runner.OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST),
        "site_import": False,
        "project_root_mode": "runner-root-argument",
    }
    if (
            (policy["require_isolated_project_adapter"] and binding != expected_binding)
            or identity["executable_sha256"] != python_identity["sha256"]
            or identity["executable_size_bytes"] != python_identity["size_bytes"]):
        raise EvidenceError(
            "project adapter was not executed by the isolated current Python runtime"
        )

    dependencies = identity["runtime_dependencies"]
    expected_refs = policy["required_project_adapter_dependencies"]
    if (
            not isinstance(dependencies, list)
            or [item.get("ref") if isinstance(item, dict) else None
                for item in dependencies] != expected_refs):
        raise EvidenceError("project adapter runtime dependency binding is incomplete")
    for item in dependencies:
        if set(item) != {"ref", "sha256", "size_bytes"}:
            raise EvidenceError("project adapter runtime dependency identity is invalid")
        try:
            raw = runner.project_bytes(item["ref"])
        except runner.BehaviorEvalError as exc:
            raise EvidenceError("cannot verify project adapter runtime dependency") from exc
        if (
                hashlib.sha256(raw).hexdigest() != item["sha256"]
                or len(raw) != item["size_bytes"]):
            raise EvidenceError("project adapter runtime dependency has drifted")

    staged = identity["staged_runtime"]
    if policy["require_staged_project_adapter"]:
        if not isinstance(staged, dict) or set(staged) != {
                "layout_version", "implementation", "runtime_dependencies",
                "aggregate_sha256"}:
            raise EvidenceError("project adapter staged runtime identity is invalid")
        staged_implementation = staged["implementation"]
        staged_dependencies = staged["runtime_dependencies"]
        if (
                staged.get("layout_version") != runner.OFFICIAL_ADAPTER_STAGE_LAYOUT
                or not isinstance(staged_implementation, dict)
                or staged_implementation != {
                    "ref": implementation["ref"],
                    "sha256": implementation["sha256"],
                    "size_bytes": implementation["size_bytes"],
                    "mode": "0400",
                }
                or not isinstance(staged_dependencies, list)
                or staged_dependencies != [
                    {
                        "ref": item["ref"],
                        "sha256": item["sha256"],
                        "size_bytes": item["size_bytes"],
                        "mode": "0400",
                    }
                    for item in dependencies
                ]
                or staged != runner._staged_runtime_identity(
                    staged_implementation, staged_dependencies,
                )):
            raise EvidenceError(
                "project adapter staged runtime does not bind its current source identities"
            )


def _execution_identity(result):
    provenance = result["execution_provenance"]
    fields = (
        "execution_mode", "adapter_name", "adapter_version", "host_name",
        "host_version", "model_provider", "model_id", "judge_model_id",
        "model_revision", "adapter_implementation_sha256",
        "prompt_template_version", "prompt_template_sha256", "parameters_sha256",
    )
    return tuple(provenance[field] for field in fields)


def _freshness(runner, completion, results, maximum_age_days, now):
    now = now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise EvidenceError("verification time must include a timezone")
    timestamps = [runner.parse_timestamp(completion["completed_at"], "completed_at")]
    timestamps.extend(
        runner.parse_timestamp(result["execution_provenance"]["ended_at"], "ended_at")
        for result in results
    )
    newest = max(timestamps)
    oldest = min(timestamps)
    if newest > now + dt.timedelta(minutes=5):
        raise EvidenceError("semantic evidence timestamp is in the future")
    age = now - oldest
    if age > dt.timedelta(days=maximum_age_days):
        raise EvidenceError(
            "semantic evidence is stale: %.2f days old (maximum %d)"
            % (age.total_seconds() / 86_400, maximum_age_days)
        )
    return oldest, newest, age


def verify_evidence(evidence_root, run_id, policy=None, now=None, runner=None):
    runner = runner or load_runner()
    policy = strict_policy(dict(policy)) if policy is not None else load_policy(runner=runner)
    runtime = runner.run_event_runtime()
    root = Path(evidence_root)
    try:
        runtime.validate_uuid(run_id, "semantic evidence run_id")
        _stream, _projection, run_dir = runtime.run_paths(root, run_id, create=False)
        evidence_dir = run_dir / "semantic-eval"
        manifest = runtime.read_anchored_json(evidence_dir / "manifest.json", "semantic evidence manifest")
    except (OSError, runtime.RunEventError) as exc:
        raise EvidenceError("cannot open semantic evidence run: %s" % exc) from exc

    _manifest_shape(manifest)
    if manifest["run_id"] != run_id or manifest["profile"] != policy["profile"]:
        raise EvidenceError("semantic evidence run/profile does not match policy")
    if manifest["required_execution_mode"] != policy["required_execution_mode"]:
        raise EvidenceError("semantic evidence execution mode does not match policy")

    try:
        selection = runner.select_semantic_cases(policy["profile"], set())
        requests = runner.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )
        for request in requests:
            runner.validate_v2_request_hash(request)
    except runner.BehaviorEvalError as exc:
        raise EvidenceError("cannot reconstruct current semantic requests: %s" % exc) from exc
    if len(requests) < policy["minimum_cases"]:
        raise EvidenceError("current semantic profile is below the minimum case count")
    request_bytes = canonical_request_bytes(runner, requests)
    request_hash = hashlib.sha256(request_bytes).hexdigest()
    expected_selection_hash = runner.sha256_json({
        "profile": selection["profile"],
        "case_ids": [request["case"]["id"] for request in requests],
        "provenance": selection["provenance"],
    })
    if policy["require_current_case_selection"] and (
            manifest["request_count"] != len(requests)
            or manifest["request_stream_sha256"] != request_hash
            or manifest["selection_sha256"] != expected_selection_hash):
        raise EvidenceError("semantic evidence does not bind the current case selection and sources")

    stored_requests = stable_bytes(
        runtime, evidence_dir / "requests.ndjson", 32_000_000,
        "semantic evidence requests",
    )
    if stored_requests != request_bytes:
        raise EvidenceError("stored semantic requests differ from current reconstructed requests")
    if policy["require_current_runner"] and manifest["runner"] != {
            "ref": "scripts/run-behavior-evals.py",
            "sha256": hashlib.sha256(runner.project_bytes("scripts/run-behavior-evals.py")).hexdigest(),
    }:
        raise EvidenceError("semantic runner has drifted since evidence collection")
    if policy["require_current_protocol_schema"] and manifest["protocol_schema"] != {
            "ref": runner.PROTOCOL_SCHEMA_REF,
            "sha256": hashlib.sha256(runner.project_bytes(runner.PROTOCOL_SCHEMA_REF)).hexdigest(),
    }:
        raise EvidenceError("semantic protocol schema has drifted since evidence collection")

    identity = manifest.get("adapter_command_identity")
    if not isinstance(identity, dict) or not isinstance(identity.get("implementation"), dict):
        raise EvidenceError("semantic adapter command identity is invalid")
    implementation = identity["implementation"]
    implementation_sha256 = implementation.get("sha256")
    if policy["require_project_adapter"]:
        _project_adapter_current(runner, identity, policy)

    results_path = evidence_dir / "results.ndjson"
    try:
        with runtime.locked_stream(results_path, exclusive=False, create=False) as handle:
            store = runner.SemanticEvidenceStore(
                runtime, root, run_id, requests, results_path,
                evidence_dir / "completion.json", handle,
                policy["required_execution_mode"], implementation_sha256,
            )
            results = store.ordered_latest_results()
            completion = runtime.read_anchored_json(
                evidence_dir / "completion.json", "semantic evidence completion"
            )
            completion_raw = stable_bytes(
                runtime, evidence_dir / "completion.json", 1_000_000,
                "semantic evidence completion",
            )
    except (runtime.RunEventError, runner.BehaviorEvalError) as exc:
        raise EvidenceError("semantic result stream is invalid: %s" % exc) from exc

    if (
            completion.get("run_id") != run_id
            or completion.get("request_count") != len(requests)
            or completion.get("terminal_count") != len(requests)
            or completion.get("complete") is not True
            or completion.get("status") != policy["required_status"]
            or completion.get("outcome_counts", {}).get("passed") != len(requests)):
        raise EvidenceError("semantic evidence completion is not a complete passing run")
    if [result["case_id"] for result in results] != [request["case"]["id"] for request in requests]:
        raise EvidenceError("semantic result order/coverage differs from current requests")
    if any(result["outcome"] != "passed" for result in results):
        raise EvidenceError("semantic evidence includes a non-passing outcome")
    identities = {_execution_identity(result) for result in results}
    if policy["require_single_execution_identity"] and len(identities) != 1:
        raise EvidenceError("semantic evidence mixes execution identities")
    provenance = results[0]["execution_provenance"]
    if policy["require_distinct_judge_model"] and provenance["model_id"] == provenance["judge_model_id"]:
        raise EvidenceError("semantic evidence policy requires a distinct judge model")
    total_judge_attempts = sum(
        len(result["execution_provenance"]["judge_attempts"])
        for result in results
    )
    retried_cases = sum(
        len(result["execution_provenance"]["judge_attempts"]) > 1
        for result in results
    )
    judge_protocol_retries = sum(
        sum(
            attempt["disposition"] == "protocol-rejected"
            for attempt in result["execution_provenance"]["judge_attempts"][:-1]
        )
        for result in results
    )
    oldest, newest, age = _freshness(
        runner, completion, results, policy["maximum_age_days"], now,
    )
    case_provenance = {}
    for request in requests:
        item = request["case"]["case_provenance"]
        case_provenance[item] = case_provenance.get(item, 0) + 1
    return {
        "schema_version": "1.0",
        "valid": True,
        "run_id": run_id,
        "profile": policy["profile"],
        "case_count": len(requests),
        "case_provenance": case_provenance,
        "execution_mode": provenance["execution_mode"],
        "model_provider": provenance["model_provider"],
        "model_id": provenance["model_id"],
        "judge_model_id": provenance["judge_model_id"],
        "distinct_judge_model": provenance["model_id"] != provenance["judge_model_id"],
        "total_judge_attempts": total_judge_attempts,
        "retried_cases": retried_cases,
        "judge_protocol_retries": judge_protocol_retries,
        "host_name": provenance["host_name"],
        "host_version": provenance["host_version"],
        "adapter_name": provenance["adapter_name"],
        "adapter_implementation_sha256": implementation_sha256,
        "runner_sha256": manifest["runner"]["sha256"],
        "selection_sha256": manifest["selection_sha256"],
        "protocol_schema_sha256": manifest["protocol_schema"]["sha256"],
        "request_stream_sha256": request_hash,
        "result_stream_sha256": completion["result_stream_sha256"],
        "head_record_hash": completion["head_record_hash"],
        "completion_sha256": hashlib.sha256(completion_raw).hexdigest(),
        "oldest_result_at": oldest.isoformat().replace("+00:00", "Z"),
        "newest_evidence_at": newest.isoformat().replace("+00:00", "Z"),
        "age_seconds": round(age.total_seconds(), 3),
    }


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="Canonical UUID under memory/runs/")
    parser.add_argument("--evidence-root", default=".", help="Project root containing memory/runs/")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="Strict evidence policy JSON")
    parser.add_argument("--json", action="store_true", help="Emit the bounded verification summary as JSON")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    runner = load_runner()
    policy = load_policy(args.policy, runner=runner)
    result = verify_evidence(args.evidence_root, args.run_id, policy=policy, runner=runner)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(
            "PASS semantic evidence: %s %d/%d real execution, model=%s judge=%s retries=%d age=%.2fd"
            % (
                result["profile"], result["case_count"], result["case_count"],
                result["model_id"], result["judge_model_id"],
                result["judge_protocol_retries"],
                result["age_seconds"] / 86_400,
            )
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceError as exc:
        print("verify-semantic-evidence: %s" % exc, file=sys.stderr)
        raise SystemExit(1)
