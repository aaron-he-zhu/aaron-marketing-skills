#!/usr/bin/env python3
"""Run offline conformance suites and, optionally, a semantic host adapter.

The default path is deterministic and network-free. ``--adapter-command`` is an
explicit extension point for a host/model harness: cases are sent as NDJSON on
stdin and one schema-valid result per case must be returned as NDJSON on stdout.
Protocol-v2 results can be retained as private run evidence, never as golden baselines.
"""
from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
import eval_cases as eval_case_runtime
SUITES_PATH = ROOT / "evals" / "deterministic-suites.json"
PROFILES_PATH = ROOT / "evals" / "behavior-profiles.json"
RUN_EVENTS_PATH = ROOT / "scripts" / "run-events.py"
PROTOCOL_SCHEMA_REF = "evals/behavior-adapter-v2.schema.json"
OFFICIAL_PROJECT_ADAPTER_REF = "scripts/adapters/codex-behavior-adapter.py"
OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES = (
    "evals/codex-behavior-candidate-output.schema.json",
    "evals/codex-behavior-model-output.schema.json",
)
OFFICIAL_ADAPTER_PYTHON_FLAGS = ("-I", "-S")
OFFICIAL_ADAPTER_STAGE_LAYOUT = "private-python-runtime-v1"
OFFICIAL_ADAPTER_ENVIRONMENT_POLICY = "isolated-allowlist-v1"
OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST = (
    "CODEX_HOME", "HOME", "LANG", "LC_ALL", "PATH", "TMPDIR",
)
MACHINE_CONTRACT_INDEX_REF = "references/skill-contracts/index.json"
ZERO_HASH = "0" * 64
TERMINAL_EVAL_OUTCOMES = {"passed", "behavior-failed", "inconclusive"}
MAX_EVIDENCE_LINE_BYTES = 1_500_000
_RUN_EVENT_RUNTIME = None
CASE_LINE = re.compile(r"^\s*-?\s*(\{.*\})\s*$")
ID_RE = re.compile(r'(?:^|[{,])\s*"?id"?\s*:\s*"?([A-Za-z0-9._-]+)"?')
TARGET_RE = re.compile(r'(?:^|[{,])\s*"?target_skill"?\s*:\s*"?([A-Za-z0-9_-]+)"?')
RESULT_KEYS = {
    "id", "passed", "evidence", "observed_assertions", "failure_modes_seen",
    "adapter_version",
}
V2_RESULT_KEYS = {
    "kind", "protocol_version", "case_id", "request_sha256", "outcome",
    "execution_provenance", "assertions", "failures",
}
EXECUTION_KEYS = {
    "execution_mode", "adapter_name", "adapter_version", "host_name", "host_version",
    "model_provider", "model_id", "judge_model_id", "model_revision", "prompt_template_version",
    "adapter_implementation_sha256", "prompt_template_sha256", "parameters_sha256",
    "candidate_response_sha256",
    "judge_response_sha256", "judge_attempts", "response_sha256",
    "started_at", "ended_at", "latency_ms",
}
JUDGE_ATTEMPT_KEYS = {
    "attempt", "response_sha256", "size_bytes", "disposition", "diagnostic_code",
}
JUDGE_DIAGNOSTIC_CODES = {
    "JUDGE_EMPTY_OUTPUT", "JUDGE_INVALID_UTF8", "JUDGE_INVALID_JSON",
    "JUDGE_TOP_LEVEL_SHAPE", "JUDGE_OUTCOME", "JUDGE_ASSERTION_COVERAGE",
    "JUDGE_ASSERTION_IDENTITY", "JUDGE_ASSERTION_SHAPE", "JUDGE_ASSERTION_VALUE",
    "JUDGE_FAILURE_SHAPE", "JUDGE_FAILURE_TAXONOMY", "JUDGE_OUTCOME_INVARIANT",
}
ASSERTION_KEYS = {"id", "kind", "verdict", "evidence"}
FAILURE_KEYS = {"code", "class", "retryable", "summary"}
FAILURE_CLASSES = {
    "prompt", "routing", "context", "tool", "permission", "artifact", "loop",
    "host", "adapter", "unknown",
}
BEHAVIOR_FAILURE_CODES = {
    "PROMPT_REQUIRED_BEHAVIOR_MISSING", "PROMPT_FORBIDDEN_BEHAVIOR",
    "PROMPT_INJECTION_FOLLOWED", "OUTPUT_CONTRACT",
    "ROUTING_WRONG_TARGET_OR_ORDER", "CONTEXT_MISSINGNESS_OR_AUTHORITY",
    "PERMISSION_OR_AUTHORITY_BYPASS", "ARTIFACT_SINK_OR_VALIDATION",
    "TOOL_OR_EXTERNAL_SIDE_EFFECT", "LOOP_HANDOFF_OR_TERMINATION",
}
HOST_FAILURE_CODES = {
    "HOST_TIMEOUT", "HOST_RATE_LIMIT", "HOST_AUTH", "HOST_UNAVAILABLE",
    "HOST_CONTEXT_LIMIT", "HOST_REFUSAL", "HOST_TOOL_ERROR",
}
ADAPTER_FAILURE_CODES = {
    "ADAPTER_PROTOCOL", "ADAPTER_CRASH", "ADAPTER_COVERAGE", "ADAPTER_PROVENANCE",
}
INCONCLUSIVE_FAILURE_CODES = {"EVALUATOR_INCONCLUSIVE"}
INFRA_FAILURE_CODES = HOST_FAILURE_CODES | ADAPTER_FAILURE_CODES | INCONCLUSIVE_FAILURE_CODES
FAILURE_CODES = BEHAVIOR_FAILURE_CODES | INFRA_FAILURE_CODES
FAILURE_CODE_CLASS = {
    "PROMPT_REQUIRED_BEHAVIOR_MISSING": "prompt",
    "PROMPT_FORBIDDEN_BEHAVIOR": "prompt",
    "PROMPT_INJECTION_FOLLOWED": "prompt",
    "OUTPUT_CONTRACT": "prompt",
    "ROUTING_WRONG_TARGET_OR_ORDER": "routing",
    "CONTEXT_MISSINGNESS_OR_AUTHORITY": "context",
    "PERMISSION_OR_AUTHORITY_BYPASS": "permission",
    "ARTIFACT_SINK_OR_VALIDATION": "artifact",
    "TOOL_OR_EXTERNAL_SIDE_EFFECT": "tool",
    "LOOP_HANDOFF_OR_TERMINATION": "loop",
    "HOST_TIMEOUT": "host",
    "HOST_RATE_LIMIT": "host",
    "HOST_AUTH": "host",
    "HOST_UNAVAILABLE": "host",
    "HOST_CONTEXT_LIMIT": "host",
    "HOST_REFUSAL": "host",
    "HOST_TOOL_ERROR": "host",
    "ADAPTER_PROTOCOL": "adapter",
    "ADAPTER_CRASH": "adapter",
    "ADAPTER_COVERAGE": "adapter",
    "ADAPTER_PROVENANCE": "adapter",
    "EVALUATOR_INCONCLUSIVE": "unknown",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SAFE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
PROTOCOL_ROUTING_COMMAND = {
    "channel-registry": "social",
    "consent-registry": "email",
    "creator-registry": "influencer",
    "entity-registry": "seo-geo",
    "launch-registry": "launch",
    "memory-management": "seo-geo",
    "narrative-registry": "narrative",
    "offer-claims-registry": "ad",
}


class BehaviorEvalError(ValueError):
    pass


def _reject_json_constant(value):
    raise BehaviorEvalError("non-finite JSON number: %s" % value)


def _reject_json_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise BehaviorEvalError("duplicate JSON key: %s" % key)
        value[key] = item
    return value


def strict_json_loads(raw, label):
    try:
        return json.loads(
            raw,
            object_pairs_hook=_reject_json_duplicate_keys,
            parse_constant=_reject_json_constant,
        )
    except BehaviorEvalError:
        raise
    except (TypeError, ValueError, RecursionError) as exc:
        raise BehaviorEvalError("%s is not strict JSON" % label) from exc


def load_json(path):
    try:
        return strict_json_loads(path.read_text(encoding="utf-8"), str(path))
    except (OSError, ValueError) as exc:
        raise BehaviorEvalError("cannot load %s: %s" % (path, exc)) from exc


def canonical_json(value):
    try:
        return json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise BehaviorEvalError("value is not finite canonical JSON: %s" % exc) from exc


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_path(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise BehaviorEvalError("cannot hash %s: %s" % (path, exc)) from exc


def project_bytes(reference):
    try:
        return eval_case_runtime._read_project_bytes(ROOT, reference)
    except eval_case_runtime.EvalCaseError as exc:
        raise BehaviorEvalError("cannot read bound project reference %s: %s" % (reference, exc)) from exc


def load_project_json(reference):
    raw = project_bytes(reference)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BehaviorEvalError("bound project reference is not UTF-8: %s" % reference) from exc
    return strict_json_loads(text, reference), hashlib.sha256(raw).hexdigest()


def exact_object(value, required, label):
    if not isinstance(value, dict) or set(value) != set(required):
        raise BehaviorEvalError(
            "%s keys must be exactly %s" % (label, sorted(required))
        )
    return value


def nonempty_string(value, label, maximum=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise BehaviorEvalError("%s must be a non-empty string up to %d characters" % (label, maximum))
    return value


def parse_timestamp(value, label):
    nonempty_string(value, label, 128)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BehaviorEvalError("%s must be an RFC 3339 timestamp" % label) from exc
    if parsed.tzinfo is None:
        raise BehaviorEvalError("%s must include a timezone" % label)
    return parsed


def validate_suite_manifest(manifest):
    if set(manifest) != {"schema_version", "description", "suites"}:
        raise BehaviorEvalError("deterministic suite manifest has unknown or missing keys")
    if manifest["schema_version"] != "1.0" or not isinstance(manifest["suites"], list):
        raise BehaviorEvalError("invalid deterministic suite manifest")
    seen = set()
    for suite in manifest["suites"]:
        if set(suite) != {"id", "command", "timeout_seconds"}:
            raise BehaviorEvalError("suite entries require exactly id, command, timeout_seconds")
        if suite["id"] in seen:
            raise BehaviorEvalError("duplicate suite id: %s" % suite["id"])
        seen.add(suite["id"])
        if not isinstance(suite["command"], list) or not suite["command"] or not all(
                isinstance(part, str) and part for part in suite["command"]):
            raise BehaviorEvalError("suite %s command must be a non-empty argument array" % suite["id"])
        timeout = suite["timeout_seconds"]
        if not isinstance(timeout, int) or isinstance(timeout, bool) or not 1 <= timeout <= 600:
            raise BehaviorEvalError("suite %s timeout must be 1..600 seconds" % suite["id"])


def expand_command(parts):
    replacements = {"{python}": sys.executable, "{root}": str(ROOT)}
    return [replacements.get(part, part) for part in parts]


def run_deterministic(selected):
    manifest = load_json(SUITES_PATH)
    validate_suite_manifest(manifest)
    suites = manifest["suites"]
    if selected:
        unknown = sorted(set(selected) - {suite["id"] for suite in suites})
        if unknown:
            raise BehaviorEvalError("unknown deterministic suite(s): %s" % ", ".join(unknown))
        suites = [suite for suite in suites if suite["id"] in selected]
    failures = []
    for suite in suites:
        command = expand_command(suite["command"])
        print("RUN   %s" % suite["id"])
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=suite["timeout_seconds"],
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            failures.append("%s: %s" % (suite["id"], exc))
            print("FAIL  " + failures[-1])
            continue
        if result.returncode:
            tail = "\n".join(result.stdout.splitlines()[-30:])
            failures.append("%s exited %d\n%s" % (suite["id"], result.returncode, tail))
            print("FAIL  %s exited %d" % (suite["id"], result.returncode))
        else:
            summary = next((line for line in reversed(result.stdout.splitlines()) if line.strip()), "passed")
            print("PASS  %s: %s" % (suite["id"], summary.strip()))
    return failures


def discover_semantic_cases(filters):
    cases = []
    for path in sorted((ROOT / "evals").glob("*/cases.md")):
        if " 2" in path.name:
            continue
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            matched = CASE_LINE.match(line)
            if not matched:
                continue
            raw = matched.group(1)
            case_id = ID_RE.search(raw)
            target = TARGET_RE.search(raw)
            if not case_id or not target:
                continue
            if filters and not any(value in {case_id.group(1), target.group(1)} for value in filters):
                continue
            cases.append({
                "protocol_version": "1.0",
                "id": case_id.group(1),
                "target_skill": target.group(1),
                "case_source": str(path.relative_to(ROOT)),
                "case_line": line_number,
                "skill_path": find_skill_path(target.group(1)),
                "raw_case": raw,
            })
    ids = [case["id"] for case in cases]
    duplicates = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicates:
        raise BehaviorEvalError("semantic case IDs are not unique: %s" % ", ".join(duplicates))
    if filters and not cases:
        raise BehaviorEvalError("no semantic cases matched --case filters")
    return cases


def find_skill_path(slug):
    matches = list(ROOT.glob("*/*/%s/SKILL.md" % slug)) + list(ROOT.glob("protocol/%s/SKILL.md" % slug))
    if len(matches) != 1:
        raise BehaviorEvalError("target skill %s resolves to %d paths" % (slug, len(matches)))
    return str(matches[0].relative_to(ROOT))


def skill_identity(slug):
    relative = find_skill_path(slug)
    try:
        raw = project_bytes(relative)
        text = raw.decode("utf-8")
    except (BehaviorEvalError, UnicodeDecodeError) as exc:
        raise BehaviorEvalError("cannot read target skill %s: %s" % (relative, exc)) from exc
    match = re.search(r"(?m)^version:\s*['\"]?([^'\"\s]+)", text)
    if not match or not SEMVER_RE.fullmatch(match.group(1)):
        raise BehaviorEvalError("target skill %s has no valid version" % slug)
    return {
        "skill": slug,
        "path": relative,
        "version": match.group(1),
        "skill_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _current_source_binding(reference, digest, label):
    if (
            not isinstance(reference, str) or not reference
            or not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
            or hashlib.sha256(project_bytes(reference)).hexdigest() != digest):
        raise BehaviorEvalError("%s binding is invalid or stale" % label)
    return {"ref": reference, "sha256": digest}


def _merge_source_refs(*groups):
    merged = []
    seen = {}
    for group in groups:
        for binding in group:
            exact_object(binding, {"ref", "sha256"}, "prompt source binding")
            reference = binding["ref"]
            digest = binding["sha256"]
            _current_source_binding(reference, digest, "prompt source")
            if reference in seen:
                if seen[reference] != digest:
                    raise BehaviorEvalError("one prompt source has conflicting hashes")
                continue
            seen[reference] = digest
            merged.append({"ref": reference, "sha256": digest})
    if not 1 <= len(merged) <= 32:
        raise BehaviorEvalError("prompt source expansion must contain 1..32 unique bindings")
    return merged


def load_skill_machine_contracts():
    index, _index_sha = load_project_json(MACHINE_CONTRACT_INDEX_REF)
    exact_object(
        index,
        {
            "$schema", "schema_version", "source_catalog", "shared_contract",
            "contract_schema", "contract_count", "contracts",
        },
        "skill machine-contract index",
    )
    if index["schema_version"] != "1.0":
        raise BehaviorEvalError("skill machine-contract index version is unsupported")
    for key in ("source_catalog", "shared_contract", "contract_schema"):
        binding = index[key]
        required = {"path", "sha256"} | ({"version"} if key == "source_catalog" else set())
        exact_object(binding, required, "skill machine-contract index.%s" % key)
        _current_source_binding(
            binding["path"], binding["sha256"],
            "skill machine-contract index.%s" % key,
        )
        if key == "source_catalog":
            nonempty_string(binding["version"], "skill machine-contract source version", 128)

    entries = index["contracts"]
    if (
            not isinstance(entries, list)
            or not isinstance(index["contract_count"], int)
            or isinstance(index["contract_count"], bool)
            or index["contract_count"] != 120
            or len(entries) != index["contract_count"]):
        raise BehaviorEvalError("skill machine-contract index coverage is invalid")

    result = {}
    seen_refs = set()
    for entry in entries:
        exact_object(
            entry, {"skill", "contract_ref", "contract_sha256"},
            "skill machine-contract index entry",
        )
        skill = entry["skill"]
        contract_ref = entry["contract_ref"]
        digest = entry["contract_sha256"]
        if (
                not isinstance(skill, str) or not SAFE_ID_RE.fullmatch(skill)
                or contract_ref != "references/skill-contracts/%s.json" % skill
                or skill in result or contract_ref in seen_refs):
            raise BehaviorEvalError("skill machine-contract index entry is malformed")
        contract, actual_digest = load_project_json(contract_ref)
        if actual_digest != digest:
            raise BehaviorEvalError("skill machine contract hash drift: %s" % contract_ref)
        identity = contract.get("identity")
        context_hints = contract.get("context_hints")
        expected_identity = skill_identity(skill)
        if (
                contract.get("schema_version") != "1.0"
                or contract.get("contract_id") != "skill:%s" % skill
                or not isinstance(identity, dict)
                or identity.get("name") != skill
                or identity.get("path") != expected_identity["path"]
                or identity.get("version") != expected_identity["version"]
                or identity.get("sha256") != expected_identity["skill_sha256"]
                or not isinstance(identity.get("discipline"), str)
                or not isinstance(context_hints, dict)
                or not isinstance(context_hints.get("bundle_references"), list)):
            raise BehaviorEvalError("skill machine contract identity is invalid: %s" % contract_ref)

        sources = [
            _current_source_binding(contract_ref, digest, "skill machine contract"),
            _current_source_binding(
                expected_identity["path"], expected_identity["skill_sha256"], "target skill",
            ),
            _current_source_binding(
                index["shared_contract"]["path"], index["shared_contract"]["sha256"],
                "shared skill execution contract",
            ),
            _current_source_binding(
                index["source_catalog"]["path"], index["source_catalog"]["sha256"],
                "system catalog",
            ),
        ]
        for position, source in enumerate(context_hints["bundle_references"], 1):
            exact_object(
                source,
                {"path", "reason_code", "requirement", "sha256", "source_line"},
                "skill machine-contract context reference",
            )
            if source["requirement"] not in {"required", "optional"}:
                raise BehaviorEvalError("skill machine-contract context requirement is invalid")
            sources.append(_current_source_binding(
                source["path"], source["sha256"],
                "skill machine-contract context reference %d" % position,
            ))
        result[skill] = {
            "kind": "machine-skill",
            "contract_id": contract["contract_id"],
            "contract_ref": contract_ref,
            "contract_sha256": digest,
            "source_refs": _merge_source_refs(sources),
            "discipline": identity["discipline"],
        }
        seen_refs.add(contract_ref)
    if len(result) != index["contract_count"]:
        raise BehaviorEvalError("skill machine-contract index coverage is incomplete")
    return result


def auto_routing_source_refs(skill, discipline):
    command = discipline
    if discipline == "protocol":
        command = PROTOCOL_ROUTING_COMMAND.get(skill)
    if command not in {"narrative", "seo-geo", "social", "email", "ad", "influencer", "launch"}:
        raise BehaviorEvalError("auto-routing case has no deterministic discipline command")
    references = [
        "commands/auto.md",
        "commands/%s.md" % command,
        "references/aaron-product-api-contract.md",
    ]
    return [
        _current_source_binding(
            reference, hashlib.sha256(project_bytes(reference)).hexdigest(),
            "auto-routing runtime source",
        )
        for reference in references
    ]


def load_auditor_prompt_contracts():
    index_ref = "references/prompt-contracts/index.json"
    index, _index_sha = load_project_json(index_ref)
    exact_object(
        index,
        {
            "$schema", "schema_version", "source_catalog", "framework_catalog",
            "contract_schema", "contract_count", "variant_count", "contracts",
        },
        "auditor prompt-contract index",
    )
    if index["schema_version"] != "1.0":
        raise BehaviorEvalError("auditor prompt-contract index version is unsupported")
    for key in ("source_catalog", "framework_catalog", "contract_schema"):
        binding = index[key]
        required = {"path", "sha256"} | ({"version"} if key != "contract_schema" else set())
        exact_object(binding, required, "auditor prompt-contract index.%s" % key)
        if (
                not isinstance(binding["path"], str)
                or not isinstance(binding["sha256"], str)
                or not SHA256_RE.fullmatch(binding["sha256"])
                or hashlib.sha256(project_bytes(binding["path"])).hexdigest() != binding["sha256"]):
            raise BehaviorEvalError("auditor prompt-contract index %s binding is invalid" % key)
        if key != "contract_schema":
            nonempty_string(binding["version"], "auditor prompt-contract index.%s.version" % key, 128)
    contracts = index["contracts"]
    if (
            not isinstance(contracts, list)
            or not isinstance(index["contract_count"], int)
            or isinstance(index["contract_count"], bool)
            or index["contract_count"] != len(contracts)
            or index["contract_count"] != 8
            or index["variant_count"] != 40):
        raise BehaviorEvalError("auditor prompt-contract index counts are invalid")
    result = {}
    derived_case_bindings = {}
    seen_contract_refs = set()
    variant_total = 0
    for entry in contracts:
        exact_object(
            entry,
            {
                "skill", "skill_version", "skill_sha256", "framework", "ref", "sha256",
                "evaluation_variant_count", "evaluation_variant_ids",
            },
            "auditor prompt-contract index entry",
        )
        skill = entry["skill"]
        reference = entry["ref"]
        digest = entry["sha256"]
        if (
                not isinstance(skill, str) or not SAFE_ID_RE.fullmatch(skill)
                or not isinstance(reference, str)
                or reference != "references/prompt-contracts/%s.json" % skill
                or not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)
                or skill in result or reference in seen_contract_refs):
            raise BehaviorEvalError("auditor prompt-contract index entry is malformed")
        contract, actual_digest = load_project_json(reference)
        if actual_digest != digest:
            raise BehaviorEvalError("auditor prompt contract hash drift: %s" % reference)
        contract_id = contract.get("contract_id")
        contract_skill = contract.get("skill")
        framework_contract = contract.get("framework_contract")
        gate = contract.get("gate")
        variants = contract.get("evaluation_variants")
        expected_identity = skill_identity(skill)
        if (
                contract.get("contract_kind") != "auditor-gate"
                or contract_id != "auditor-gate:%s" % skill
                or not isinstance(contract_skill, dict)
                or contract_skill != {
                    "name": skill,
                    "path": expected_identity["path"],
                    "version": expected_identity["version"],
                    "sha256": expected_identity["skill_sha256"],
                }
                or entry["skill_version"] != expected_identity["version"]
                or entry["skill_sha256"] != expected_identity["skill_sha256"]
                or not isinstance(framework_contract, dict)
                or framework_contract.get("catalog_path") != index["framework_catalog"]["path"]
                or framework_contract.get("catalog_sha256") != index["framework_catalog"]["sha256"]
                or framework_contract.get("catalog_version") != index["framework_catalog"]["version"]
                or not isinstance(gate, dict)
                or gate.get("framework") != entry["framework"]
                or contract.get("source_catalog") != index["source_catalog"]
                or not isinstance(variants, list)
                or not all(isinstance(item, dict) for item in variants)
                or not isinstance(entry["evaluation_variant_count"], int)
                or isinstance(entry["evaluation_variant_count"], bool)
                or not isinstance(entry["evaluation_variant_ids"], list)
                or entry["evaluation_variant_count"] != len(variants)
                or entry["evaluation_variant_ids"] != [item.get("id") for item in variants]
                or len(variants) != 5):
            raise BehaviorEvalError("auditor prompt contract identity is invalid: %s" % reference)
        variant_total += len(variants)
        for variant in variants:
            variant_id = variant.get("id")
            semantic = variant.get("semantic_case")
            if (
                    not isinstance(variant_id, str)
                    or not SAFE_ID_RE.fullmatch(variant_id)
                    or not isinstance(semantic, dict)
                    or set(semantic) != {
                        "scenario", "input_summary", "expected_behavior", "failure_modes",
                    }
                    or not isinstance(semantic["scenario"], str)
                    or not isinstance(semantic["input_summary"], str)
                    or not isinstance(semantic["expected_behavior"], list)
                    or not isinstance(semantic["failure_modes"], list)
                    or not all(isinstance(item, str) for item in (
                        semantic["expected_behavior"] + semantic["failure_modes"]
                    ))):
                raise BehaviorEvalError(
                    "auditor prompt contract semantic variant is invalid: %s" % reference
                )
            case_id = "derived-%s-%s" % (skill, variant_id)
            if case_id in derived_case_bindings:
                raise BehaviorEvalError("auditor prompt contract variant IDs are not unique")
            derived_case_bindings[case_id] = {
                "id": case_id,
                "type": "eval-case",
                "case_provenance": "simulated",
                "evidence_binding": None,
                "target_skill": skill,
                "scenario": semantic["scenario"],
                "input_summary": semantic["input_summary"],
                "expected_behavior": semantic["expected_behavior"],
                "failure_modes": semantic["failure_modes"],
                "source_ref": reference,
                "case_sha256": sha256_json(variant),
                "source_group": "derived-auditor",
            }
        # The contract manifest contains generated evaluation variants, including
        # their assertions. It is host-verified via contract_ref/contract_sha256
        # but must never enter the SUT-visible source list.
        source_refs = []
        catalog = contract.get("source_catalog")
        framework = framework_contract
        if not isinstance(catalog, dict) or not isinstance(framework, dict) or not isinstance(gate, dict):
            raise BehaviorEvalError("auditor prompt contract provenance is malformed: %s" % reference)
        bound = [
            (catalog.get("path"), catalog.get("sha256")),
            (framework.get("catalog_path"), framework.get("catalog_sha256")),
        ]
        runtime_sources = gate.get("runtime_sources")
        if not isinstance(runtime_sources, list) or not runtime_sources:
            raise BehaviorEvalError("auditor prompt contract has no runtime sources: %s" % reference)
        for source in runtime_sources:
            if not isinstance(source, dict):
                raise BehaviorEvalError("auditor prompt contract runtime source is malformed")
            bound.append((source.get("path"), source.get("sha256")))
        seen_source_refs = {reference}
        for source_ref, source_sha in bound:
            if (
                    not isinstance(source_ref, str)
                    or not isinstance(source_sha, str)
                    or not SHA256_RE.fullmatch(source_sha)
                    or source_ref in seen_source_refs):
                raise BehaviorEvalError("auditor prompt contract source binding is malformed")
            if hashlib.sha256(project_bytes(source_ref)).hexdigest() != source_sha:
                raise BehaviorEvalError("auditor prompt contract source hash drift: %s" % source_ref)
            seen_source_refs.add(source_ref)
            source_refs.append({"ref": source_ref, "sha256": source_sha})
        result[skill] = {
            "kind": "derived-auditor",
            "contract_id": contract_id,
            "contract_ref": reference,
            "contract_sha256": digest,
            "source_refs": source_refs,
        }
        seen_contract_refs.add(reference)
    if len(result) != index["contract_count"] or variant_total != index["variant_count"]:
        raise BehaviorEvalError("auditor prompt-contract index coverage is incomplete")
    return result, derived_case_bindings


def build_v2_requests(cases, profile, selection_reasons):
    contracts, derived_case_bindings = load_auditor_prompt_contracts()
    machine_contracts = load_skill_machine_contracts()
    requests = []
    required_case_keys = {
        "id", "type", "case_provenance", "evidence_binding", "target_skill", "scenario",
        "input_summary", "expected_behavior", "failure_modes", "source_ref",
        "source_line", "case_sha256", "source_group",
    }
    for case in cases:
        exact_object(case, required_case_keys, "semantic case")
        if case["source_group"] == "derived-auditor":
            current = derived_case_bindings.get(case["id"])
            comparable = {key: value for key, value in case.items() if key != "source_line"}
            if current is None or comparable != current:
                raise BehaviorEvalError(
                    "derived auditor case does not match its current prompt-contract variant"
                )
        target = skill_identity(case["target_skill"])
        machine_contract = machine_contracts.get(case["target_skill"])
        if machine_contract is None:
            raise BehaviorEvalError("semantic case has no current skill machine contract")
        auditor_contract = contracts.get(case["target_skill"])
        if auditor_contract is None and case["source_group"] == "derived-auditor":
            raise BehaviorEvalError("derived auditor case has no bound prompt contract")
        if auditor_contract is None:
            prompt_contract = {
                key: machine_contract[key]
                for key in (
                    "kind", "contract_id", "contract_ref", "contract_sha256", "source_refs",
                )
            }
        else:
            prompt_contract = {
                key: auditor_contract[key]
                for key in (
                    "kind", "contract_id", "contract_ref", "contract_sha256", "source_refs",
                )
            }
            prompt_contract["source_refs"] = _merge_source_refs(
                prompt_contract["source_refs"], machine_contract["source_refs"],
            )
        if case["source_group"] == "auto-routing":
            prompt_contract["source_refs"] = _merge_source_refs(
                prompt_contract["source_refs"],
                auto_routing_source_refs(
                    case["target_skill"], machine_contract["discipline"],
                ),
            )
        reasons = selection_reasons.get(case["id"], ["profile:%s" % profile])
        if not isinstance(reasons, list) or not reasons:
            raise BehaviorEvalError("semantic case selection reasons are missing")
        request = {
            "kind": "behavior-eval-request",
            "protocol_version": "2.0",
            "case": case,
            "selection": {"profile": profile, "reasons": sorted(set(reasons))},
            "target": target,
            "prompt_contract": prompt_contract,
        }
        request["request_sha256"] = sha256_json(request)
        requests.append(request)
    return requests


def validate_v2_request_hash(request):
    if not isinstance(request, dict) or not isinstance(request.get("request_sha256"), str):
        raise BehaviorEvalError("adapter v2 request has no request_sha256")
    payload = dict(request)
    recorded = payload.pop("request_sha256")
    if recorded != sha256_json(payload):
        raise BehaviorEvalError("adapter v2 request_sha256 does not match canonical request")
    return request


def validate_adapter_result(value):
    if not isinstance(value, dict):
        raise BehaviorEvalError("adapter result must be an object")
    if set(value) - RESULT_KEYS:
        raise BehaviorEvalError("adapter result has unknown keys: %s" % sorted(set(value) - RESULT_KEYS))
    if not isinstance(value.get("id"), str) or not value["id"]:
        raise BehaviorEvalError("adapter result id is required")
    if not isinstance(value.get("passed"), bool):
        raise BehaviorEvalError("adapter result passed must be boolean")
    if not isinstance(value.get("evidence"), str) or not value["evidence"].strip():
        raise BehaviorEvalError("adapter result evidence is required")
    for key in ("observed_assertions", "failure_modes_seen"):
        if key in value and (not isinstance(value[key], list) or not all(
                isinstance(item, str) for item in value[key])):
            raise BehaviorEvalError("adapter result %s must be an array of strings" % key)


def validate_v2_adapter_result(
        value, request, required_execution_mode="real",
        expected_adapter_implementation_sha256=None):
    exact_object(value, V2_RESULT_KEYS, "adapter v2 result")
    if value["kind"] != "behavior-eval-result" or value["protocol_version"] != "2.0":
        raise BehaviorEvalError("adapter v2 result kind/protocol_version is invalid")
    case = request["case"]
    if value["case_id"] != case["id"]:
        raise BehaviorEvalError("adapter v2 result case_id does not match its request")
    if value["request_sha256"] != request["request_sha256"]:
        raise BehaviorEvalError("adapter v2 result request_sha256 does not match")
    outcome = value["outcome"]
    if outcome not in {"passed", "behavior-failed", "inconclusive", "host-failed", "adapter-failed"}:
        raise BehaviorEvalError("adapter v2 result outcome is unsupported")

    execution = exact_object(
        value["execution_provenance"], EXECUTION_KEYS, "execution_provenance",
    )
    if execution["execution_mode"] not in {"real", "simulated"}:
        raise BehaviorEvalError("execution_provenance.execution_mode is unsupported")
    if required_execution_mode and execution["execution_mode"] != required_execution_mode:
        raise BehaviorEvalError(
            "semantic profile requires %s execution provenance" % required_execution_mode
        )
    if (
            expected_adapter_implementation_sha256 is not None
            and execution["adapter_implementation_sha256"]
            != expected_adapter_implementation_sha256):
        raise BehaviorEvalError(
            "ADAPTER_PROVENANCE: execution provenance does not match the bound adapter implementation"
        )
    for key in ("adapter_name", "host_name", "model_provider"):
        if not isinstance(execution[key], str) or not SAFE_ID_RE.fullmatch(execution[key]):
            raise BehaviorEvalError("execution_provenance.%s must be a safe ID" % key)
    for key in ("adapter_version", "host_version", "prompt_template_version"):
        nonempty_string(execution[key], "execution_provenance.%s" % key, 128)
    for key in ("model_id", "judge_model_id"):
        nonempty_string(execution[key], "execution_provenance.%s" % key, 256)
    if execution["model_revision"] is not None:
        nonempty_string(execution["model_revision"], "execution_provenance.model_revision", 256)
    for key in (
            "adapter_implementation_sha256", "prompt_template_sha256", "parameters_sha256",
            "candidate_response_sha256", "judge_response_sha256", "response_sha256"):
        if not isinstance(execution[key], str) or not SHA256_RE.fullmatch(execution[key]):
            raise BehaviorEvalError("execution_provenance.%s must be SHA-256" % key)
    judge_attempts = execution["judge_attempts"]
    if not isinstance(judge_attempts, list) or len(judge_attempts) > 2:
        raise BehaviorEvalError(
            "execution_provenance.judge_attempts must contain at most two entries"
        )
    accepted_attempts = []
    for position, attempt in enumerate(judge_attempts, 1):
        exact_object(
            attempt, JUDGE_ATTEMPT_KEYS,
            "execution_provenance.judge_attempts[%d]" % (position - 1),
        )
        if attempt["attempt"] != position:
            raise BehaviorEvalError("judge attempt indexes must be contiguous from one")
        if (
                not isinstance(attempt["response_sha256"], str)
                or not SHA256_RE.fullmatch(attempt["response_sha256"])):
            raise BehaviorEvalError("judge attempt response_sha256 must be SHA-256")
        if (
                not isinstance(attempt["size_bytes"], int)
                or isinstance(attempt["size_bytes"], bool)
                or not 0 <= attempt["size_bytes"] <= 1_000_000):
            raise BehaviorEvalError("judge attempt size_bytes is out of range")
        disposition = attempt["disposition"]
        diagnostic = attempt["diagnostic_code"]
        if disposition == "accepted":
            if diagnostic is not None:
                raise BehaviorEvalError("accepted judge attempt cannot carry a diagnostic")
            if attempt["size_bytes"] == 0:
                raise BehaviorEvalError("accepted judge attempt cannot be empty")
            accepted_attempts.append(position)
        elif disposition == "protocol-rejected":
            if diagnostic not in JUDGE_DIAGNOSTIC_CODES:
                raise BehaviorEvalError(
                    "protocol-rejected judge attempt requires a closed diagnostic"
                )
        else:
            raise BehaviorEvalError("judge attempt disposition is unsupported")
    empty_sha256 = hashlib.sha256(b"").hexdigest()
    expected_judge_sha256 = (
        judge_attempts[-1]["response_sha256"] if judge_attempts else empty_sha256
    )
    if execution["judge_response_sha256"] != expected_judge_sha256:
        raise BehaviorEvalError(
            "execution_provenance.judge_response_sha256 does not bind the last judge attempt"
        )
    expected_response_sha256 = sha256_json({
        "candidate_response_sha256": execution["candidate_response_sha256"],
        "judge_attempts": judge_attempts,
    })
    if execution["response_sha256"] != expected_response_sha256:
        raise BehaviorEvalError(
            "execution_provenance.response_sha256 does not bind the full judge ledger"
        )
    if outcome in {"passed", "behavior-failed", "inconclusive"}:
        if accepted_attempts != [len(judge_attempts)] or not judge_attempts:
            raise BehaviorEvalError(
                "terminal judge outcome requires exactly one accepted final attempt"
            )
    elif accepted_attempts:
        raise BehaviorEvalError("failed execution cannot contain an accepted judge attempt")
    started = parse_timestamp(execution["started_at"], "execution_provenance.started_at")
    ended = parse_timestamp(execution["ended_at"], "execution_provenance.ended_at")
    if ended < started:
        raise BehaviorEvalError("execution_provenance ended_at precedes started_at")
    if (
            not isinstance(execution["latency_ms"], int)
            or isinstance(execution["latency_ms"], bool)
            or not 0 <= execution["latency_ms"] <= 86_400_000):
        raise BehaviorEvalError("execution_provenance.latency_ms is out of range")

    expected_ids = {
        "expected-%d" % index for index in range(1, len(case["expected_behavior"]) + 1)
    }
    forbidden_ids = {
        "forbidden-%d" % index for index in range(1, len(case["failure_modes"]) + 1)
    }
    assertion_by_id = {}
    assertions = value["assertions"]
    if not isinstance(assertions, list) or len(assertions) > 128:
        raise BehaviorEvalError("adapter v2 assertions must be an array with at most 128 entries")
    for index, assertion in enumerate(assertions):
        exact_object(assertion, ASSERTION_KEYS, "assertions[%d]" % index)
        assertion_id = assertion["id"]
        if assertion_id in assertion_by_id:
            raise BehaviorEvalError("adapter v2 assertion IDs must be unique")
        if assertion_id in expected_ids:
            expected_kind = "expected"
        elif assertion_id in forbidden_ids:
            expected_kind = "forbidden"
        else:
            raise BehaviorEvalError("adapter v2 result has an unknown assertion ID: %s" % assertion_id)
        if assertion["kind"] != expected_kind:
            raise BehaviorEvalError("adapter v2 assertion kind does not match its ID")
        if assertion["verdict"] not in {"met", "violated", "not-observed"}:
            raise BehaviorEvalError("adapter v2 assertion verdict is unsupported")
        if expected_kind == "forbidden" and assertion["verdict"] == "met":
            raise BehaviorEvalError("a forbidden assertion cannot have verdict met")
        nonempty_string(assertion["evidence"], "assertions[%d].evidence" % index, 2000)
        assertion_by_id[assertion_id] = assertion
    if set(assertion_by_id) != expected_ids | forbidden_ids:
        missing = sorted((expected_ids | forbidden_ids) - set(assertion_by_id))
        raise BehaviorEvalError("adapter v2 assertion coverage mismatch; missing=%s" % missing)

    failures = value["failures"]
    if not isinstance(failures, list) or len(failures) > 64:
        raise BehaviorEvalError("adapter v2 failures must be an array with at most 64 entries")
    failure_codes = []
    for index, failure in enumerate(failures):
        exact_object(failure, FAILURE_KEYS, "failures[%d]" % index)
        code = failure["code"]
        if code not in FAILURE_CODES:
            raise BehaviorEvalError("adapter v2 failure code is unsupported: %s" % code)
        if failure["class"] != FAILURE_CODE_CLASS[code]:
            raise BehaviorEvalError("adapter v2 failure class does not match code %s" % code)
        if not isinstance(failure["retryable"], bool):
            raise BehaviorEvalError("adapter v2 failure retryable must be boolean")
        if code in BEHAVIOR_FAILURE_CODES | INCONCLUSIVE_FAILURE_CODES and failure["retryable"]:
            raise BehaviorEvalError("behavior and inconclusive failures cannot be retryable")
        nonempty_string(failure["summary"], "failures[%d].summary" % index, 2000)
        failure_codes.append(code)

    expected_verdicts = [assertion_by_id[item]["verdict"] for item in sorted(expected_ids)]
    forbidden_verdicts = [assertion_by_id[item]["verdict"] for item in sorted(forbidden_ids)]
    deterministic_failure = (
        any(item == "violated" for item in expected_verdicts)
        or any(item == "violated" for item in forbidden_verdicts)
    )
    unknown_evidence = any(item == "not-observed" for item in expected_verdicts)
    if outcome == "passed":
        if failures or any(item != "met" for item in expected_verdicts) or any(
                item != "not-observed" for item in forbidden_verdicts):
            raise BehaviorEvalError("passed result violates assertion/failure invariants")
    elif outcome == "behavior-failed":
        if not failures or any(code not in BEHAVIOR_FAILURE_CODES for code in failure_codes):
            raise BehaviorEvalError("behavior-failed result requires only behavior failure codes")
        if not deterministic_failure:
            raise BehaviorEvalError("behavior-failed result requires a deterministic failed assertion")
    elif outcome == "inconclusive":
        if failure_codes != ["EVALUATOR_INCONCLUSIVE"]:
            raise BehaviorEvalError("inconclusive result requires exactly EVALUATOR_INCONCLUSIVE")
        if deterministic_failure or not unknown_evidence:
            raise BehaviorEvalError(
                "inconclusive result requires unknown evidence and no deterministic failure"
            )
    elif outcome == "host-failed":
        if not failures or any(code not in HOST_FAILURE_CODES for code in failure_codes):
            raise BehaviorEvalError("host-failed result requires only HOST_* failures")
        if any(item != "not-observed" for item in expected_verdicts + forbidden_verdicts):
            raise BehaviorEvalError("host-failed result assertions must be not-observed")
    elif outcome == "adapter-failed":
        if not failures or any(code not in ADAPTER_FAILURE_CODES for code in failure_codes):
            raise BehaviorEvalError("adapter-failed result requires only ADAPTER_* failures")
        if any(item != "not-observed" for item in expected_verdicts + forbidden_verdicts):
            raise BehaviorEvalError("adapter-failed result assertions must be not-observed")
    return value


def run_event_runtime():
    """Load the existing private-run filesystem runtime without creating a package dependency."""
    global _RUN_EVENT_RUNTIME
    if _RUN_EVENT_RUNTIME is not None:
        return _RUN_EVENT_RUNTIME
    spec = importlib.util.spec_from_file_location(
        "aaron_semantic_eval_run_events", RUN_EVENTS_PATH,
    )
    if spec is None or spec.loader is None:
        raise BehaviorEvalError("cannot load the private run-evidence runtime")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    _RUN_EVENT_RUNTIME = module
    return module


def _stable_evidence_bytes(runtime, path, maximum, label):
    try:
        with runtime.anchored_regular_file(path) as handle:
            before = os.fstat(handle.fileno())
            raw = handle.read(maximum + 1)
            after = os.fstat(handle.fileno())
    except (OSError, runtime.RunEventError) as exc:
        raise BehaviorEvalError("cannot read %s: %s" % (label, exc)) from exc
    fields = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    if len(raw) > maximum or len(raw) != before.st_size or any(
            getattr(before, field) != getattr(after, field) for field in fields):
        raise BehaviorEvalError("%s is oversized or changed while read" % label)
    return raw


def _stable_file_digest(path, maximum, label):
    runtime = run_event_runtime()
    try:
        resolved = Path(path).resolve(strict=True)
        with runtime.anchored_regular_file(resolved) as handle:
            before = os.fstat(handle.fileno())
            if before.st_size > maximum:
                raise BehaviorEvalError("%s exceeds its byte bound" % label)
            digest = hashlib.sha256()
            total = 0
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                digest.update(chunk)
            after = os.fstat(handle.fileno())
    except BehaviorEvalError:
        raise
    except (OSError, runtime.RunEventError) as exc:
        raise BehaviorEvalError("cannot bind %s: %s" % (label, exc)) from exc
    fields = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    if total != before.st_size or any(
            getattr(before, field) != getattr(after, field) for field in fields):
        raise BehaviorEvalError("%s changed while it was hashed" % label)
    return resolved, {"sha256": digest.hexdigest(), "size_bytes": total}


def _staged_file_identity(reference, raw, mode):
    return {
        "ref": reference,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "size_bytes": len(raw),
        "mode": mode,
    }


def _staged_runtime_identity(implementation, dependencies):
    files = [implementation, *dependencies]
    payload = {
        "layout_version": OFFICIAL_ADAPTER_STAGE_LAYOUT,
        "files": files,
    }
    return {
        "layout_version": OFFICIAL_ADAPTER_STAGE_LAYOUT,
        "implementation": implementation,
        "runtime_dependencies": dependencies,
        "aggregate_sha256": sha256_json(payload),
    }


def _bind_adapter_command_details(command, implementation_ref=None):
    executable = command[0] if os.path.isabs(command[0]) else shutil.which(command[0])
    if not executable:
        raise BehaviorEvalError("ADAPTER_CRASH: semantic adapter executable is unavailable")
    executable_path, executable_identity = _stable_file_digest(
        executable, 536_870_912, "semantic adapter command executable",
    )
    bound_command = list(command)
    bound_command[0] = str(executable_path)

    implementation_path = None
    implementation_index = None
    runtime_dependencies = []
    staged_runtime = None
    source_snapshots = {}
    execution_binding = {"kind": "unconstrained", "script_argv_index": None}
    if implementation_ref is not None:
        raw = project_bytes(implementation_ref)
        expected = (ROOT / implementation_ref).resolve(strict=True)
        for index, argument in enumerate(bound_command):
            candidate = Path(argument)
            if not candidate.is_absolute():
                candidate = ROOT / candidate
            try:
                if candidate.resolve(strict=True) == expected:
                    implementation_path = expected
                    implementation_index = index
                    bound_command[index] = str(expected)
                    break
            except OSError:
                continue
        if implementation_path is None:
            raise BehaviorEvalError(
                "--adapter-implementation-ref must identify a file in --adapter-command"
            )
        current_python = Path(sys.executable).resolve(strict=True)
        if implementation_index != 1 or executable_path != current_python:
            raise BehaviorEvalError(
                "ADAPTER_PROVENANCE: an explicit project adapter must be argv[1] "
                "of the current Python interpreter"
            )
        if expected.suffix != ".py":
            raise BehaviorEvalError(
                "ADAPTER_PROVENANCE: an explicit project adapter must be a Python script"
            )
        implementation_identity = {
            "ref": implementation_ref,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "size_bytes": len(raw),
            "argv_index": implementation_index,
        }
        execution_binding = {
            "kind": "current-python-script",
            "interpreter_path": str(current_python),
            "script_argv_index": implementation_index,
        }
        if implementation_ref == OFFICIAL_PROJECT_ADAPTER_REF:
            if any(
                    argument == "--project-root"
                    or argument.startswith("--project-root=")
                    for argument in bound_command[2:]):
                raise BehaviorEvalError(
                    "ADAPTER_PROVENANCE: --project-root is reserved to the isolated runner"
                )
            source_snapshots[implementation_ref] = raw
            for reference in OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES:
                dependency_raw = project_bytes(reference)
                source_snapshots[reference] = dependency_raw
                runtime_dependencies.append({
                    "ref": reference,
                    "sha256": hashlib.sha256(dependency_raw).hexdigest(),
                    "size_bytes": len(dependency_raw),
                })
            staged_implementation = _staged_file_identity(
                implementation_ref, raw, "0400",
            )
            staged_dependencies = [
                _staged_file_identity(reference, source_snapshots[reference], "0400")
                for reference in OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES
            ]
            staged_runtime = _staged_runtime_identity(
                staged_implementation, staged_dependencies,
            )
            execution_binding = {
                "kind": "isolated-staged-current-python-script",
                "interpreter_path": str(current_python),
                "source_script_argv_index": implementation_index,
                "staged_script_argv_index": 3,
                "python_flags": list(OFFICIAL_ADAPTER_PYTHON_FLAGS),
                "environment_policy": OFFICIAL_ADAPTER_ENVIRONMENT_POLICY,
                "environment_allowlist": list(OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST),
                "site_import": False,
                "project_root_mode": "runner-root-argument",
            }
    else:
        for index, argument in enumerate(bound_command[1:], 1):
            if not argument.endswith((".py", ".sh")):
                continue
            candidate = Path(argument)
            if not candidate.is_absolute():
                candidate = ROOT / candidate
            try:
                implementation_path, identity = _stable_file_digest(
                    candidate, 32_000_000, "semantic adapter implementation",
                )
            except BehaviorEvalError:
                continue
            implementation_index = index
            bound_command[index] = str(implementation_path)
            implementation_identity = dict(
                identity, ref="argv:%d" % index, argv_index=index,
            )
            break
        if implementation_path is None:
            implementation_identity = dict(
                executable_identity, ref="command-executable", argv_index=0,
            )
    return bound_command, {
        "executable_sha256": executable_identity["sha256"],
        "executable_size_bytes": executable_identity["size_bytes"],
        "implementation": implementation_identity,
        "execution_binding": execution_binding,
        "runtime_dependencies": runtime_dependencies,
        "staged_runtime": staged_runtime,
    }, source_snapshots


def bind_adapter_command(command, implementation_ref=None):
    """Return the stable public command identity without exposing staged bytes."""
    bound_command, identity, _source_snapshots = _bind_adapter_command_details(
        command, implementation_ref=implementation_ref,
    )
    return bound_command, identity


def _write_private_stage_file(path, raw, mode):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags, mode)
    try:
        offset = 0
        while offset < len(raw):
            offset += os.write(descriptor, raw[offset:])
        os.fchmod(descriptor, mode)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _verify_staged_file(path, expected, label):
    try:
        entry = os.lstat(path)
    except OSError as exc:
        raise BehaviorEvalError("ADAPTER_PROVENANCE: cannot inspect %s" % label) from exc
    expected_mode = int(expected["mode"], 8)
    if (
            not stat.S_ISREG(entry.st_mode) or stat.S_ISLNK(entry.st_mode)
            or entry.st_nlink != 1 or stat.S_IMODE(entry.st_mode) != expected_mode):
        raise BehaviorEvalError(
            "ADAPTER_PROVENANCE: %s is not the staged private regular file" % label
        )
    resolved, actual = _stable_file_digest(path, 32_000_000, label)
    if (
            resolved != path.resolve(strict=True)
            or actual["sha256"] != expected["sha256"]
            or actual["size_bytes"] != expected["size_bytes"]):
        raise BehaviorEvalError("ADAPTER_PROVENANCE: %s identity changed" % label)


def _official_adapter_environment(stage_root):
    environment = {
        "LANG": "C",
        "LC_ALL": "C",
        "PATH": os.defpath,
        "TMPDIR": str(stage_root / "tmp"),
    }
    home = os.environ.get("HOME") or str(Path.home())
    if not home or "\x00" in home or not Path(home).is_absolute():
        raise BehaviorEvalError(
            "ADAPTER_PROVENANCE: HOME must be absolute for isolated adapter"
        )
    environment["HOME"] = home
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        if "\x00" in codex_home or not Path(codex_home).is_absolute():
            raise BehaviorEvalError(
                "ADAPTER_PROVENANCE: CODEX_HOME must be absolute for isolated adapter"
            )
        environment["CODEX_HOME"] = codex_home
    if not set(environment) <= set(OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST):
        raise BehaviorEvalError("ADAPTER_PROVENANCE: isolated adapter environment escaped allowlist")
    return environment


@contextlib.contextmanager
def stage_bound_adapter(command, identity, source_snapshots):
    """Install and execute the official adapter from one already-bound byte snapshot."""
    binding = identity.get("execution_binding")
    if not isinstance(binding, dict) or binding.get("kind") != (
            "isolated-staged-current-python-script"):
        yield command, None, ROOT
        return
    staged = identity.get("staged_runtime")
    if not isinstance(staged, dict):
        raise BehaviorEvalError("ADAPTER_PROVENANCE: staged adapter identity is missing")
    expected_files = [staged["implementation"], *staged["runtime_dependencies"]]
    if set(source_snapshots) != {item["ref"] for item in expected_files}:
        raise BehaviorEvalError("ADAPTER_PROVENANCE: staged adapter source snapshot is incomplete")
    temporary = tempfile.TemporaryDirectory(prefix="aaron-semantic-adapter-")
    stage_root = Path(temporary.name).resolve()
    try:
        os.chmod(stage_root, 0o700)
        (stage_root / "tmp").mkdir(mode=0o700)
        for item in expected_files:
            raw = source_snapshots[item["ref"]]
            if (
                    hashlib.sha256(raw).hexdigest() != item["sha256"]
                    or len(raw) != item["size_bytes"]):
                raise BehaviorEvalError(
                    "ADAPTER_PROVENANCE: staged adapter source snapshot identity changed"
                )
            _write_private_stage_file(stage_root / item["ref"], raw, int(item["mode"], 8))
        for directory in (
                stage_root / "scripts" / "adapters", stage_root / "scripts",
                stage_root / "evals"):
            os.chmod(directory, 0o500)
        os.chmod(stage_root, 0o500)
        staged_script = stage_root / staged["implementation"]["ref"]
        execution_command = [
            command[0], *binding["python_flags"], str(staged_script),
            "--project-root", str(ROOT), *command[2:],
        ]
        environment = _official_adapter_environment(stage_root)
        verify_bound_adapter_command(execution_command, identity)
        yield execution_command, environment, stage_root
    finally:
        for directory in (
                stage_root, stage_root / "scripts", stage_root / "scripts" / "adapters",
                stage_root / "evals", stage_root / "tmp"):
            try:
                os.chmod(directory, 0o700)
            except OSError:
                pass
        temporary.cleanup()


def verify_bound_adapter_command(command, identity):
    """Re-hash the executable and every actual runtime file around each batch."""
    executable_path, executable_identity = _stable_file_digest(
        command[0], 536_870_912, "bound semantic adapter command executable",
    )
    if str(executable_path) != command[0] or executable_identity != {
            "sha256": identity["executable_sha256"],
            "size_bytes": identity["executable_size_bytes"],
    }:
        raise BehaviorEvalError(
            "ADAPTER_PROVENANCE: semantic adapter command executable identity changed"
        )
    binding = identity.get("execution_binding")
    if not isinstance(binding, dict):
        raise BehaviorEvalError("ADAPTER_PROVENANCE: adapter execution binding is missing")
    implementation = identity["implementation"]
    source_index = implementation["argv_index"]
    if binding.get("kind") == "isolated-staged-current-python-script":
        expected_binding = {
            "kind": "isolated-staged-current-python-script",
            "interpreter_path": str(Path(sys.executable).resolve(strict=True)),
            "source_script_argv_index": 1,
            "staged_script_argv_index": 3,
            "python_flags": list(OFFICIAL_ADAPTER_PYTHON_FLAGS),
            "environment_policy": OFFICIAL_ADAPTER_ENVIRONMENT_POLICY,
            "environment_allowlist": list(OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST),
            "site_import": False,
            "project_root_mode": "runner-root-argument",
        }
        staged = identity.get("staged_runtime")
        if binding != expected_binding or source_index != 1 or not isinstance(staged, dict):
            raise BehaviorEvalError("ADAPTER_PROVENANCE: isolated adapter binding is invalid")
        index = binding["staged_script_argv_index"]
        if (
                command[1:3] != list(OFFICIAL_ADAPTER_PYTHON_FLAGS)
                or command[4:6] != ["--project-root", str(ROOT)]
                or not 0 <= index < len(command)
                or executable_path != Path(sys.executable).resolve(strict=True)):
            raise BehaviorEvalError("ADAPTER_PROVENANCE: isolated Python bootstrap is invalid")
        stage_root = Path(command[index]).resolve(strict=True).parents[2]
        expected_command_path = stage_root / staged["implementation"]["ref"]
        if Path(command[index]).resolve(strict=True) != expected_command_path:
            raise BehaviorEvalError("ADAPTER_PROVENANCE: staged adapter path is invalid")
        expected_staged = _staged_runtime_identity(
            staged["implementation"], staged["runtime_dependencies"],
        )
        if staged != expected_staged:
            raise BehaviorEvalError("ADAPTER_PROVENANCE: staged adapter aggregate is invalid")
        _verify_staged_file(
            expected_command_path, staged["implementation"], "staged semantic adapter",
        )
        for dependency in staged["runtime_dependencies"]:
            _verify_staged_file(
                stage_root / dependency["ref"], dependency,
                "staged semantic adapter dependency %s" % dependency["ref"],
            )
        return
    index = source_index
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(command):
        raise BehaviorEvalError("ADAPTER_PROVENANCE: adapter implementation binding is invalid")
    implementation_path, implementation_identity = _stable_file_digest(
        command[index], 32_000_000 if index else 536_870_912,
        "bound semantic adapter implementation",
    )
    if (
            str(implementation_path) != command[index]
            or implementation_identity["sha256"] != implementation["sha256"]
            or implementation_identity["size_bytes"] != implementation["size_bytes"]):
        raise BehaviorEvalError(
            "ADAPTER_PROVENANCE: semantic adapter implementation identity changed"
        )
    if binding.get("kind") == "current-python-script":
        current_python = Path(sys.executable).resolve(strict=True)
        if (
                set(binding) != {"kind", "interpreter_path", "script_argv_index"}
                or binding["script_argv_index"] != 1
                or index != 1
                or executable_path != current_python
                or binding["interpreter_path"] != str(current_python)):
            raise BehaviorEvalError(
                "ADAPTER_PROVENANCE: project adapter is not executed by the current Python runtime"
            )


def _path_entry_exists(path):
    try:
        os.lstat(path)
        return True
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise BehaviorEvalError("cannot inspect semantic evidence path %s: %s" % (path, exc)) from exc


class SemanticEvidenceStore:
    """Incremental hash-chained v2 results held under one private run lock."""

    def __init__(
            self, runtime, root, run_id, requests, results_path, completion_path,
            handle, required_execution_mode, adapter_implementation_sha256):
        self.runtime = runtime
        self.root = root
        self.run_id = run_id
        self.requests = requests
        self.request_by_id = {request["case"]["id"]: request for request in requests}
        self.results_path = results_path
        self.completion_path = completion_path
        self.handle = handle
        self.required_execution_mode = required_execution_mode
        self.adapter_implementation_sha256 = adapter_implementation_sha256
        self.records = []
        self.raw_lines = []
        self.latest = {}
        self._load_existing()
        self._validate_completion_prefix()

    def _load_existing(self):
        self.handle.seek(0)
        previous_hash = ZERO_HASH
        terminal_seen = set()
        for line_number, line in enumerate(self.handle, 1):
            if not line.strip():
                raise BehaviorEvalError(
                    "semantic evidence results contain a blank record at line %d" % line_number
                )
            raw = line.encode("utf-8")
            if len(raw) > MAX_EVIDENCE_LINE_BYTES:
                raise BehaviorEvalError("semantic evidence result line exceeds its byte bound")
            record = strict_json_loads(line, "semantic evidence result line %d" % line_number)
            exact_object(
                record,
                {"sequence", "previous_record_hash", "result", "record_hash"},
                "semantic evidence record",
            )
            if record["sequence"] != line_number:
                raise BehaviorEvalError("semantic evidence result sequence is not contiguous")
            if record["previous_record_hash"] != previous_hash:
                raise BehaviorEvalError("semantic evidence result hash chain is broken")
            claimed_hash = record["record_hash"]
            if not isinstance(claimed_hash, str) or not SHA256_RE.fullmatch(claimed_hash):
                raise BehaviorEvalError("semantic evidence record_hash is invalid")
            unhashed = dict(record)
            unhashed.pop("record_hash")
            if sha256_json(unhashed) != claimed_hash:
                raise BehaviorEvalError("semantic evidence record_hash does not bind its record")
            if line != canonical_json(record) + "\n":
                raise BehaviorEvalError("semantic evidence results must use canonical NDJSON")
            result = record["result"]
            case_id = result.get("case_id") if isinstance(result, dict) else None
            request = self.request_by_id.get(case_id)
            if request is None:
                raise BehaviorEvalError("semantic evidence contains an unknown case result")
            validate_v2_adapter_result(
                result, request, required_execution_mode=self.required_execution_mode,
                expected_adapter_implementation_sha256=self.adapter_implementation_sha256,
            )
            if case_id in terminal_seen:
                raise BehaviorEvalError("semantic evidence contains a result after a terminal outcome")
            if result["outcome"] in TERMINAL_EVAL_OUTCOMES:
                terminal_seen.add(case_id)
            self.records.append(record)
            self.raw_lines.append(raw)
            self.latest[case_id] = result
            previous_hash = claimed_hash

    def _prefix_state(self, count):
        latest = {}
        for record in self.records[:count]:
            result = record["result"]
            latest[result["case_id"]] = result
        terminal = sum(
            1 for result in latest.values()
            if result["outcome"] in TERMINAL_EVAL_OUTCOMES
        )
        return latest, terminal

    def _validate_completion_prefix(self):
        if not _path_entry_exists(self.completion_path):
            return
        try:
            value = self.runtime.read_anchored_json(
                self.completion_path, "semantic evidence completion",
            )
        except self.runtime.RunEventError as exc:
            raise BehaviorEvalError("cannot read semantic evidence completion: %s" % exc) from exc
        required = {
            "schema_version", "kind", "run_id", "request_count", "attempt_count",
            "terminal_count", "complete", "status", "outcome_counts",
            "result_stream_sha256", "head_record_hash", "completed_at",
        }
        exact_object(value, required, "semantic evidence completion")
        count = value["attempt_count"]
        if (
                value["schema_version"] != "1.0"
                or value["kind"] != "semantic-eval-completion"
                or value["run_id"] != self.run_id
                or value["request_count"] != len(self.requests)
                or not isinstance(count, int) or isinstance(count, bool)
                or not 0 <= count <= len(self.records)):
            raise BehaviorEvalError("semantic evidence completion identity is invalid")
        prefix = b"".join(self.raw_lines[:count])
        expected_head = ZERO_HASH if count == 0 else self.records[count - 1]["record_hash"]
        latest, terminal = self._prefix_state(count)
        counts = {
            outcome: sum(1 for result in latest.values() if result["outcome"] == outcome)
            for outcome in ("passed", "behavior-failed", "inconclusive", "host-failed", "adapter-failed")
        }
        complete = terminal == len(self.requests)
        status = "passed" if complete and counts["passed"] == len(self.requests) else (
            "failed" if complete else "incomplete"
        )
        if (
                value["result_stream_sha256"] != hashlib.sha256(prefix).hexdigest()
                or value["head_record_hash"] != expected_head
                or value["terminal_count"] != terminal
                or value["outcome_counts"] != counts
                or value["complete"] is not complete
                or value["status"] != status):
            raise BehaviorEvalError("semantic evidence completion does not bind a valid result prefix")
        parse_timestamp(value["completed_at"], "semantic evidence completion.completed_at")

    def pending_requests(self):
        return [
            request for request in self.requests
            if request["case"]["id"] not in self.latest
            or self.latest[request["case"]["id"]]["outcome"] not in TERMINAL_EVAL_OUTCOMES
        ]

    def append_result(self, result):
        case_id = result["case_id"]
        request = self.request_by_id.get(case_id)
        if request is None:
            raise BehaviorEvalError("cannot persist an unknown semantic case result")
        validate_v2_adapter_result(
            result, request, required_execution_mode=self.required_execution_mode,
            expected_adapter_implementation_sha256=self.adapter_implementation_sha256,
        )
        prior = self.latest.get(case_id)
        if prior and prior["outcome"] in TERMINAL_EVAL_OUTCOMES:
            raise BehaviorEvalError("cannot append a result after a terminal semantic outcome")
        record = {
            "sequence": len(self.records) + 1,
            "previous_record_hash": (
                self.records[-1]["record_hash"] if self.records else ZERO_HASH
            ),
            "result": result,
        }
        record["record_hash"] = sha256_json(record)
        raw = (canonical_json(record) + "\n").encode("utf-8")
        if len(raw) > MAX_EVIDENCE_LINE_BYTES:
            raise BehaviorEvalError("semantic evidence result line exceeds its byte bound")
        self.handle.seek(0, os.SEEK_END)
        self.handle.write(raw.decode("utf-8"))
        self.handle.flush()
        os.fsync(self.handle.fileno())
        self.records.append(record)
        self.raw_lines.append(raw)
        self.latest[case_id] = result

    def ordered_latest_results(self):
        missing = [
            request["case"]["id"] for request in self.requests
            if request["case"]["id"] not in self.latest
        ]
        if missing:
            raise BehaviorEvalError("semantic evidence is missing results for %s" % missing)
        return [self.latest[request["case"]["id"]] for request in self.requests]

    def finalize(self):
        latest = list(self.latest.values())
        counts = {
            outcome: sum(1 for result in latest if result["outcome"] == outcome)
            for outcome in ("passed", "behavior-failed", "inconclusive", "host-failed", "adapter-failed")
        }
        terminal = sum(
            1 for result in latest if result["outcome"] in TERMINAL_EVAL_OUTCOMES
        )
        complete = terminal == len(self.requests)
        status = "passed" if complete and counts["passed"] == len(self.requests) else (
            "failed" if complete else "incomplete"
        )
        value = {
            "schema_version": "1.0",
            "kind": "semantic-eval-completion",
            "run_id": self.run_id,
            "request_count": len(self.requests),
            "attempt_count": len(self.records),
            "terminal_count": terminal,
            "complete": complete,
            "status": status,
            "outcome_counts": counts,
            "result_stream_sha256": hashlib.sha256(b"".join(self.raw_lines)).hexdigest(),
            "head_record_hash": self.records[-1]["record_hash"] if self.records else ZERO_HASH,
            "completed_at": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        try:
            self.runtime.atomic_write_json(self.root, self.completion_path, value)
        except self.runtime.RunEventError as exc:
            raise BehaviorEvalError("cannot write semantic evidence completion: %s" % exc) from exc


@contextlib.contextmanager
def semantic_evidence_session(
        run_id, resume, requests, selection, command, command_identity,
        required_execution_mode,
        evidence_root=ROOT):
    if run_id is None:
        yield None
        return
    runtime = run_event_runtime()
    root = Path(evidence_root)
    try:
        runtime.validate_uuid(run_id, "semantic evidence run_id")
        if resume:
            _stream, _projection, run_dir = runtime.run_paths(root, run_id, create=False)
            evidence_dir = run_dir / "semantic-eval"
            descriptor, _identity = runtime.open_directory_anchor(evidence_dir)
            os.close(descriptor)
        else:
            _stream, _projection, run_dir = runtime.run_paths(root, run_id, create=True)
            evidence_dir = runtime.ensure_child_directories(root, run_dir, ["semantic-eval"])
    except (OSError, runtime.RunEventError) as exc:
        raise BehaviorEvalError("cannot prepare semantic evidence directory: %s" % exc) from exc

    requests_path = evidence_dir / "requests.ndjson"
    manifest_path = evidence_dir / "manifest.json"
    results_path = evidence_dir / "results.ndjson"
    completion_path = evidence_dir / "completion.json"
    lock_path = evidence_dir / "execution.lock"
    paths = [requests_path, manifest_path, results_path, completion_path, lock_path]
    paths.extend(evidence_dir / (".%s.run-tmp" % item.name) for item in (manifest_path, completion_path))
    try:
        runtime.ensure_ignored(root, paths)
        request_bytes = b"".join(
            (canonical_json(request) + "\n").encode("utf-8") for request in requests
        )
        manifest = {
            "schema_version": "1.0",
            "kind": "semantic-eval-evidence",
            "protocol_version": "2.0",
            "run_id": run_id,
            "profile": selection["profile"],
            "request_count": len(requests),
            "request_stream_sha256": hashlib.sha256(request_bytes).hexdigest(),
            "selection_sha256": sha256_json({
                "profile": selection["profile"],
                "case_ids": [request["case"]["id"] for request in requests],
                "provenance": selection["provenance"],
            }),
            "adapter_command_sha256": sha256_json(command),
            "adapter_command_identity": command_identity,
            "runner": {
                "ref": "scripts/run-behavior-evals.py",
                "sha256": hashlib.sha256(
                    project_bytes("scripts/run-behavior-evals.py")
                ).hexdigest(),
            },
            "protocol_schema": {
                "ref": PROTOCOL_SCHEMA_REF,
                "sha256": hashlib.sha256(project_bytes(PROTOCOL_SCHEMA_REF)).hexdigest(),
            },
            "required_execution_mode": required_execution_mode,
        }
        with runtime.locked_stream(lock_path, exclusive=True) as _lock:
            if resume:
                if not _path_entry_exists(manifest_path) or not _path_entry_exists(requests_path):
                    raise BehaviorEvalError("semantic evidence resume requires manifest and requests")
                installed_manifest = runtime.read_anchored_json(
                    manifest_path, "semantic evidence manifest",
                )
                if canonical_json(installed_manifest) != canonical_json(manifest):
                    raise BehaviorEvalError("semantic evidence manifest does not match this run")
                installed_requests = _stable_evidence_bytes(
                    runtime, requests_path, 32_000_000, "semantic evidence requests",
                )
                if installed_requests != request_bytes:
                    raise BehaviorEvalError("semantic evidence requests do not match this run")
            else:
                collisions = [
                    path.name for path in (manifest_path, requests_path, results_path, completion_path)
                    if _path_entry_exists(path)
                ]
                if collisions:
                    raise BehaviorEvalError(
                        "semantic evidence run already exists; use --resume-evidence: %s"
                        % ", ".join(collisions)
                    )
                with runtime.locked_stream(requests_path, exclusive=True) as request_handle:
                    request_handle.write(request_bytes.decode("utf-8"))
                    request_handle.flush()
                    os.fsync(request_handle.fileno())
                runtime.write_immutable_json(root, manifest_path, manifest)
            with runtime.locked_stream(results_path, exclusive=True) as result_handle:
                store = SemanticEvidenceStore(
                    runtime, root, run_id, requests, results_path, completion_path,
                    result_handle, required_execution_mode,
                    command_identity["implementation"]["sha256"],
                )
                yield store
    except runtime.RunEventError as exc:
        raise BehaviorEvalError("semantic evidence runtime failed: %s" % exc) from exc


def run_adapter_v1(command_text, filters, timeout):
    try:
        command = shlex.split(command_text)
    except ValueError as exc:
        raise BehaviorEvalError("cannot parse --adapter-command: %s" % exc) from exc
    if not command:
        raise BehaviorEvalError("--adapter-command cannot be empty")
    cases = discover_semantic_cases(filters)
    payload = "".join(json.dumps(case, ensure_ascii=False) + "\n" for case in cases)
    print("RUN   semantic-adapter: %d case(s)" % len(cases))
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            input=payload,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BehaviorEvalError("semantic adapter failed: %s" % exc) from exc
    if result.returncode:
        raise BehaviorEvalError(
            "semantic adapter exited %d: %s" % (result.returncode, result.stderr[-2000:])
        )
    outputs = []
    for line_number, line in enumerate(result.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except ValueError as exc:
            raise BehaviorEvalError("adapter stdout line %d is not JSON" % line_number) from exc
        validate_adapter_result(value)
        outputs.append(value)
    expected = {case["id"] for case in cases}
    returned = [value["id"] for value in outputs]
    duplicates = sorted({case_id for case_id in returned if returned.count(case_id) > 1})
    if duplicates:
        raise BehaviorEvalError("adapter returned duplicate IDs: %s" % ", ".join(duplicates))
    missing = sorted(expected - set(returned))
    unknown = sorted(set(returned) - expected)
    if missing or unknown:
        raise BehaviorEvalError("adapter coverage mismatch; missing=%s unknown=%s" % (missing, unknown))
    failed = [value for value in outputs if not value["passed"]]
    for value in failed:
        print("FAIL  %s: %s" % (value["id"], value["evidence"]))
    if failed:
        return ["semantic adapter failed %d/%d cases" % (len(failed), len(outputs))]
    print("PASS  semantic-adapter: %d/%d" % (len(outputs), len(cases)))
    return []


def run_adapter_v2(
    command_text,
    selection,
    timeout,
    required_execution_mode="real",
    batch_size=None,
    evidence_run_id=None,
    resume_evidence=False,
    evidence_root=ROOT,
    adapter_implementation_ref=None,
):
    try:
        command = shlex.split(command_text)
    except ValueError as exc:
        raise BehaviorEvalError("cannot parse --adapter-command: %s" % exc) from exc
    if not command:
        raise BehaviorEvalError("--adapter-command cannot be empty")
    logical_command, command_identity, source_snapshots = _bind_adapter_command_details(
        command, implementation_ref=adapter_implementation_ref,
    )
    cases = selection["cases"]
    profile = selection["profile"]
    requests = build_v2_requests(cases, profile, selection["selection_reasons"])
    for request in requests:
        validate_v2_request_hash(request)
    if batch_size is None:
        batch_size = len(requests) or 1
    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or not 1 <= batch_size <= 1000:
        raise BehaviorEvalError("adapter v2 batch_size must be 1..1000")
    with contextlib.ExitStack() as stack:
        command, adapter_environment, adapter_cwd = stack.enter_context(
            stage_bound_adapter(logical_command, command_identity, source_snapshots)
        )
        evidence = stack.enter_context(semantic_evidence_session(
            evidence_run_id, resume_evidence, requests, selection,
            logical_command, command_identity, required_execution_mode,
            evidence_root=evidence_root,
        ))
        pending = evidence.pending_requests() if evidence else requests
        batch_count = (len(pending) + batch_size - 1) // batch_size
        print(
            "RUN   semantic-adapter-v2[%s]: %d case(s), %d pending, %d batch(es)"
            % (profile, len(requests), len(pending), batch_count)
        )
        outputs = []
        for batch_number, start in enumerate(range(0, len(pending), batch_size), 1):
            batch = pending[start:start + batch_size]
            payload = "".join(canonical_json(request) + "\n" for request in batch)
            if batch_count > 1:
                print("BATCH %d/%d: %d case(s)" % (batch_number, batch_count, len(batch)))
            verify_bound_adapter_command(command, command_identity)
            try:
                try:
                    result = subprocess.run(
                        command,
                        cwd=adapter_cwd,
                        env=adapter_environment,
                        input=payload,
                        text=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=timeout,
                        check=False,
                    )
                except subprocess.TimeoutExpired as exc:
                    raise BehaviorEvalError(
                        "HOST_TIMEOUT: semantic adapter batch %d/%d exceeded %d seconds"
                        % (batch_number, batch_count, timeout)
                    ) from exc
                except OSError as exc:
                    raise BehaviorEvalError(
                        "ADAPTER_CRASH: semantic adapter batch %d/%d could not start: %s"
                        % (batch_number, batch_count, exc)
                    ) from exc
            finally:
                verify_bound_adapter_command(command, command_identity)
            if result.returncode:
                raise BehaviorEvalError(
                    "ADAPTER_CRASH: semantic adapter batch %d/%d exited %d: %s"
                    % (batch_number, batch_count, result.returncode, result.stderr[-2000:])
                )

            request_by_id = {request["case"]["id"]: request for request in batch}
            batch_outputs = []
            returned = []
            for line_number, line in enumerate(result.stdout.splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    value = strict_json_loads(
                        line, "adapter batch %d stdout line %d" % (batch_number, line_number),
                    )
                except BehaviorEvalError as exc:
                    raise BehaviorEvalError(
                        "ADAPTER_PROTOCOL: adapter batch %d stdout line %d is not JSON"
                        % (batch_number, line_number)
                    ) from exc
                if not isinstance(value, dict) or not isinstance(value.get("case_id"), str):
                    raise BehaviorEvalError(
                        "ADAPTER_PROTOCOL: adapter batch %d stdout line %d has no case_id"
                        % (batch_number, line_number)
                    )
                case_id = value["case_id"]
                if case_id not in request_by_id:
                    raise BehaviorEvalError(
                        "ADAPTER_COVERAGE: adapter batch %d returned unknown ID %s"
                        % (batch_number, case_id)
                    )
                validate_v2_adapter_result(
                    value, request_by_id[case_id], required_execution_mode=required_execution_mode,
                    expected_adapter_implementation_sha256=(
                        command_identity["implementation"]["sha256"]
                    ),
                )
                batch_outputs.append(value)
                returned.append(case_id)
            duplicates = sorted({case_id for case_id in returned if returned.count(case_id) > 1})
            missing = sorted(set(request_by_id) - set(returned))
            if duplicates or missing:
                raise BehaviorEvalError(
                    "ADAPTER_COVERAGE: adapter batch %d coverage mismatch; missing=%s duplicates=%s"
                    % (batch_number, missing, duplicates)
                )
            if evidence:
                for value in batch_outputs:
                    evidence.append_result(value)
            else:
                outputs.extend(batch_outputs)
        if evidence:
            outputs = evidence.ordered_latest_results()
            evidence.finalize()

    behavior_failed = [value for value in outputs if value["outcome"] == "behavior-failed"]
    inconclusive = [value for value in outputs if value["outcome"] == "inconclusive"]
    host_failed = [value for value in outputs if value["outcome"] == "host-failed"]
    adapter_failed = [value for value in outputs if value["outcome"] == "adapter-failed"]
    for value in behavior_failed:
        print("FAIL  %s [behavior]: %s" % (
            value["case_id"], ",".join(failure["code"] for failure in value["failures"]),
        ))
    for value in inconclusive:
        print("FAIL  %s [inconclusive]" % value["case_id"])
    for value in host_failed:
        print("FAIL  %s [host]: %s" % (
            value["case_id"], ",".join(failure["code"] for failure in value["failures"]),
        ))
    for value in adapter_failed:
        print("FAIL  %s [adapter]: %s" % (
            value["case_id"], ",".join(failure["code"] for failure in value["failures"]),
        ))
    provenance_counts = {}
    for request in requests:
        status = request["case"]["case_provenance"]
        provenance_counts[status] = provenance_counts.get(status, 0) + 1
    if behavior_failed or inconclusive or host_failed or adapter_failed:
        return [
            "semantic adapter v2 failed: behavior=%d inconclusive=%d host=%d adapter=%d total=%d"
            % (len(behavior_failed), len(inconclusive), len(host_failed),
               len(adapter_failed), len(outputs))
        ]
    print(
        "PASS  semantic-adapter-v2: %d/%d execution=%s case_provenance=%s"
        % (len(outputs), len(requests), required_execution_mode,
           ",".join("%s:%d" % item for item in sorted(provenance_counts.items())))
    )
    return []


def run_adapter(command_text, filters, timeout):
    """Compatibility entry point for the v1 adapter during the v2 migration window."""
    return run_adapter_v1(command_text, filters, timeout)


def select_semantic_cases(profile, filters, changed_from=None, changed_files=None):
    try:
        if filters:
            cases = (
                eval_case_runtime.load_cases(ROOT)
                + eval_case_runtime.load_derived_auditor_cases(ROOT)
            )
            selected = [
                case for case in cases
                if case["id"] in filters or case["target_skill"] in filters
            ]
            if not selected:
                raise BehaviorEvalError("no semantic cases matched --case filters")
            reasons = {
                case["id"]: [
                    "filter:id" if case["id"] in filters else "filter:target-skill"
                ]
                for case in selected
            }
            return {
                "profile": "filtered",
                "cases": selected,
                "case_ids": [case["id"] for case in selected],
                "selection_reasons": reasons,
                "provenance": {
                    "selected_count": len(selected),
                    "available_count": len(cases),
                    "filters": sorted(filters),
                },
            }
        return eval_case_runtime.select_cases(
            ROOT,
            profile,
            base_ref=changed_from,
            changed_paths=changed_files,
        )
    except eval_case_runtime.EvalCaseError as exc:
        raise BehaviorEvalError("semantic case selection failed: %s" % exc) from exc


def semantic_plan(selection):
    return {
        "schema_version": "1.0",
        "profile": selection["profile"],
        "selected_count": len(selection["cases"]),
        "cases": [
            {
                "id": case["id"],
                "target_skill": case["target_skill"],
                "case_provenance": case["case_provenance"],
                "evidence_binding": case["evidence_binding"],
                "source_group": case["source_group"],
                "source_ref": case["source_ref"],
                "source_line": case["source_line"],
                "case_sha256": case["case_sha256"],
                "selection_reasons": selection["selection_reasons"][case["id"]],
            }
            for case in selection["cases"]
        ],
        "selection_provenance": selection["provenance"],
    }


def emit_semantic_plan(selection, destination):
    document = semantic_plan(selection)
    rendered = json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if destination == "-":
        sys.stdout.write(rendered)
        return
    path = Path(destination)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
    except OSError as exc:
        raise BehaviorEvalError("cannot write semantic plan %s: %s" % (destination, exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", action="append", default=[], help="Run only this deterministic suite ID.")
    parser.add_argument("--adapter-command", help="Optional NDJSON semantic-eval adapter command.")
    parser.add_argument(
        "--adapter-implementation-ref",
        help=(
            "Project-relative protocol-v2 adapter implementation present in "
            "--adapter-command; its exact bytes are bound to evidence."
        ),
    )
    parser.add_argument(
        "--adapter-protocol", choices=("1", "2"),
        help="Semantic adapter protocol. Existing adapter commands default to v1; plan output implies v2.",
    )
    parser.add_argument("--adapter-only", action="store_true", help="Skip deterministic suites.")
    parser.add_argument("--case", action="append", default=[], help="Adapter case ID or target-skill filter.")
    parser.add_argument(
        "--profile", choices=("smoke", "change-aware", "nightly"),
        help="Semantic case-selection profile for adapter v2 or plan output.",
    )
    parser.add_argument("--changed-from", help="Base Git commit/ref for change-aware selection.")
    parser.add_argument(
        "--changed-file", action="append", default=[],
        help="Explicit changed repository path; repeat for change-aware tests/worktrees.",
    )
    parser.add_argument(
        "--plan-json", help="Write the metadata-only semantic selection plan to this path or '-'.",
    )
    parser.add_argument(
        "--list-cases", action="store_true",
        help="Print the metadata-only semantic selection plan as JSON.",
    )
    parser.add_argument("--adapter-timeout", type=int, default=1800)
    parser.add_argument(
        "--adapter-batch-size", type=int, default=25,
        help="Protocol-v2 cases per adapter subprocess; timeout applies to each batch.",
    )
    parser.add_argument(
        "--evidence-run-id",
        help="Canonical UUID under ignored memory/runs/ for protocol-v2 request/result evidence.",
    )
    parser.add_argument(
        "--resume-evidence", action="store_true",
        help="Resume the exact protocol-v2 request set recorded by --evidence-run-id.",
    )
    args = parser.parse_args(argv)
    if args.adapter_only and not (args.adapter_command or args.plan_json or args.list_cases):
        parser.error("--adapter-only requires --adapter-command or semantic plan output")
    if args.plan_json and args.list_cases:
        parser.error("choose only one of --plan-json or --list-cases")
    adapter_protocol = args.adapter_protocol or (
        "2" if (args.plan_json or args.list_cases) else "1"
    )
    profile = args.profile or "smoke"
    if args.adapter_command and args.adapter_protocol is None and args.profile is not None:
        parser.error("--profile with an adapter requires explicit --adapter-protocol 2")
    if (args.changed_from or args.changed_file) and profile != "change-aware":
        parser.error("--changed-from/--changed-file require --profile change-aware")
    if args.changed_from and args.changed_file:
        parser.error("choose --changed-from or explicit --changed-file values, not both")
    if adapter_protocol == "1" and (args.plan_json or args.list_cases):
        parser.error("semantic plan output uses adapter protocol v2 cases")
    if args.resume_evidence and not args.evidence_run_id:
        parser.error("--resume-evidence requires --evidence-run-id")
    if args.adapter_command and adapter_protocol == "2" and not args.evidence_run_id:
        parser.error("protocol-v2 adapter execution requires --evidence-run-id")
    if args.adapter_command and adapter_protocol == "2" and not args.adapter_implementation_ref:
        parser.error("protocol-v2 adapter execution requires --adapter-implementation-ref")
    if args.adapter_implementation_ref and not (
            args.adapter_command and adapter_protocol == "2"):
        parser.error("--adapter-implementation-ref requires a protocol-v2 adapter execution")
    if (args.evidence_run_id or args.resume_evidence) and not (
            args.adapter_command and adapter_protocol == "2"):
        parser.error("semantic evidence options require a protocol-v2 adapter execution")
    if not 1 <= args.adapter_timeout <= 7200:
        parser.error("--adapter-timeout must be 1..7200 seconds")
    if not 1 <= args.adapter_batch_size <= 1000:
        parser.error("--adapter-batch-size must be 1..1000")
    failures = []
    try:
        if not args.adapter_only:
            failures.extend(run_deterministic(set(args.suite)))
        selection = None
        if adapter_protocol == "2" and (
                args.adapter_command or args.plan_json or args.list_cases):
            selection = select_semantic_cases(
                profile,
                set(args.case),
                changed_from=args.changed_from,
                changed_files=(args.changed_file if args.changed_file else None),
            )
        if args.plan_json or args.list_cases:
            emit_semantic_plan(selection, "-" if args.list_cases else args.plan_json)
        if args.adapter_command:
            if adapter_protocol == "1":
                failures.extend(
                    run_adapter_v1(args.adapter_command, set(args.case), args.adapter_timeout)
                )
            else:
                failures.extend(
                    run_adapter_v2(
                        args.adapter_command,
                        selection,
                        args.adapter_timeout,
                        batch_size=args.adapter_batch_size,
                        evidence_run_id=args.evidence_run_id,
                        resume_evidence=args.resume_evidence,
                        adapter_implementation_ref=args.adapter_implementation_ref,
                    )
                )
    except BehaviorEvalError as exc:
        failures.append(str(exc))
    if failures:
        print("\nBEHAVIOR CONFORMANCE FAILED: %d issue(s)" % len(failures))
        for failure in failures:
            print("- " + failure)
        return 1
    print("\nBehavior conformance passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
