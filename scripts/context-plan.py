#!/usr/bin/env python3
"""Build a closed context-resolver request from a generated skill contract.

The planner performs candidate discovery itself.  It never asks a host to search
for context, never writes a run ledger, and never silently truncates a project
prefix.  Token limits are represented honestly as a deterministic UTF-8 byte
proxy because the repository intentionally has no tokenizer dependency.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat as statmod
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
INDEX_REF = "references/skill-contracts/index.json"
SHARED_CONTRACT_REF = "references/skill-contract.md"
CATALOG_REF = "references/system-catalog.json"
MAX_DOCUMENT_BYTES = 10_000_000
DEFAULT_PROJECT_PATHS = (
    "memory/hot-cache.md",
    "memory/decisions.md",
    "memory/open-loops.md",
    "memory/session-checkpoint.md",
)
PROTOCOL_DISCIPLINES = {
    "narrative-registry": "narrative",
    "entity-registry": "seo-geo",
    "memory-management": "seo-geo",
    "channel-registry": "social",
    "consent-registry": "email",
    "offer-claims-registry": "ad",
    "creator-registry": "influencer",
    "launch-registry": "launch",
}
AUTHORITY_RANK = {"canonical": 0, "approved": 1, "working": 2, "untrusted": 3}
REQUIREMENT_RANK = {"required": 0, "optional": 1, "forbidden": 2}
AUDITOR_EXCLUSIVE_GROUP = "auditor-runtime-chain"


def _load_resolver():
    specification = importlib.util.spec_from_file_location(
        "aaron_context_resolver", ROOT / "scripts" / "context-resolver.py"
    )
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load context resolver")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


resolver = _load_resolver()
ContextPlanError = resolver.ContextResolutionError


def _sha256(content):
    return hashlib.sha256(content).hexdigest()


def _json_hash(value):
    return resolver.sha256_json(value)


def _read(root, relative, limit=MAX_DOCUMENT_BYTES, missing_ok=False):
    try:
        return resolver.anchored_read(root, relative, limit, "context-plan root")
    except resolver.ContextSourceMissing:
        if missing_ok:
            return None
        raise


def _load_json(root, relative, label):
    raw = _read(root, relative)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextPlanError("%s must be UTF-8" % label) from exc
    return resolver.strict_json_loads(text, label), raw


def _exact(value, fields, label):
    resolver.exact_object(value, set(fields), set(), label)
    return value


def _file_ref(value, label):
    _exact(value, {"path", "sha256"}, label)
    resolver.validate_relative_path(value["path"], label + ".path")
    resolver.validate_sha(value["sha256"], label + ".sha256")
    return value


def _verify_live_ref(bundle_root, reference, label):
    _file_ref(reference, label)
    raw = _read(bundle_root, reference["path"])
    if _sha256(raw) != reference["sha256"]:
        raise ContextPlanError("%s hash differs from the live bundle" % label)
    return raw


def _validate_extraction_items(items, display, identity, section, label, item_fields):
    if not isinstance(items, list) or not items:
        raise ContextPlanError("%s must be a non-empty array" % label)
    statuses = []
    for offset, item in enumerate(items):
        item_label = "%s[%d]" % (label, offset)
        _exact(item, item_fields, item_label)
        if not isinstance(item["text"], str) or not item["text"]:
            raise ContextPlanError("%s text must be non-empty" % item_label)
        if item["extraction_status"] not in {
                "classified", "partially-classified", "unclassified"}:
            raise ContextPlanError("%s extraction_status is unsupported" % item_label)
        statuses.append(item["extraction_status"])
        source = item["source"]
        _exact(
            source,
            {"path", "sha256", "section", "span_basis", "start_char", "end_char"},
            item_label + ".source",
        )
        if (
                source["path"] != identity["path"]
                or source["sha256"] != identity["sha256"]
                or source["section"] != section
                or source["span_basis"] != "field-text"):
            raise ContextPlanError("%s source does not bind its authored field" % item_label)
        start = source["start_char"]
        end = source["end_char"]
        if (
                not isinstance(start, int) or isinstance(start, bool)
                or not isinstance(end, int) or isinstance(end, bool)
                or start < 0 or end <= start or end > len(display)
                or display[start:end] != item["text"]):
            raise ContextPlanError("%s source span does not reproduce text" % item_label)
    if all(status == "classified" for status in statuses):
        aggregate = "classified"
    elif all(status == "unclassified" for status in statuses):
        aggregate = "unclassified"
    else:
        aggregate = "partially-classified"
    return aggregate


def _validate_machine_projection(contract):
    identity = contract["identity"]
    input_contract = contract["input_contract"]
    _exact(
        input_contract,
        {"argument_hint", "reads", "clauses", "extraction_status", "source"},
        "skill machine contract.input_contract",
    )
    input_status = _validate_extraction_items(
        input_contract["clauses"], input_contract["reads"], identity,
        "Skill Contract/Reads", "input clauses",
        {"clause_id", "text", "kind", "requirement", "extraction_status", "source"},
    )
    for item in input_contract["clauses"]:
        if item["kind"] not in {
                "project-resource", "bundle-resource", "evidence-input", "unclassified"}:
            raise ContextPlanError("input clause kind is unsupported")
        if item["requirement"] not in {"required", "optional", "unclassified"}:
            raise ContextPlanError("input clause requirement is unsupported")
    if input_contract["extraction_status"] != input_status:
        raise ContextPlanError("input clause extraction_status aggregate differs")

    output_contract = contract["output_contract"]
    _exact(
        output_contract,
        {"summary", "summary_source", "writes", "clauses", "extraction_status", "source"},
        "skill machine contract.output_contract",
    )
    output_status = _validate_extraction_items(
        output_contract["clauses"], output_contract["writes"], identity,
        "Skill Contract/Writes", "output clauses",
        {
            "clause_id", "text", "kind", "side_effect", "permission_posture",
            "extraction_status", "source",
        },
    )
    for item in output_contract["clauses"]:
        if item["kind"] not in {
                "project-artifact", "registry-event", "external-action", "mixed", "unclassified"}:
            raise ContextPlanError("output clause kind is unsupported")
        if item["side_effect"] not in {
                "project-write", "registry-proposal", "external-mutation", "mixed", "unclassified"}:
            raise ContextPlanError("output clause side_effect is unsupported")
        if item["permission_posture"] not in {
                "permission-required", "prohibited", "unclassified"}:
            raise ContextPlanError("output clause permission_posture is unsupported")
    if output_contract["extraction_status"] != output_status:
        raise ContextPlanError("output clause extraction_status aggregate differs")

    completion = contract["completion_contract"]
    _exact(
        completion, {"done_when", "clauses", "extraction_status", "source"},
        "skill machine contract.completion_contract",
    )
    completion_status = _validate_extraction_items(
        completion["clauses"], completion["done_when"], identity,
        "Skill Contract/Done when", "completion clauses",
        {
            "clause_id", "text", "condition_kind", "requirement",
            "extraction_status", "source",
        },
    )
    for item in completion["clauses"]:
        if (
                item["condition_kind"] not in {"success", "blocking"}
                or item["requirement"] != "required"
                or item["extraction_status"] != "classified"):
            raise ContextPlanError("completion clause classification is unsupported")
    if completion["extraction_status"] != completion_status:
        raise ContextPlanError("completion clause extraction_status aggregate differs")

    handoff = contract["handoff_contract"]
    _exact(
        handoff,
        {
            "summary_source", "summary", "summary_ref", "next_best", "target_skills",
            "items", "extraction_status",
        },
        "skill machine contract.handoff_contract",
    )
    handoff_status = _validate_extraction_items(
        handoff["items"], handoff["next_best"], identity,
        "Next Best Skill", "handoff items",
        {
            "item_id", "text", "kind", "condition", "target_skills",
            "extraction_status", "source",
        },
    )
    item_targets = set()
    for item in handoff["items"]:
        if item["kind"] not in {
                "primary", "conditional", "outcome", "termination", "unclassified"}:
            raise ContextPlanError("handoff item kind is unsupported")
        if item["condition"] is not None and (
                not isinstance(item["condition"], str) or item["condition"] not in item["text"]):
            raise ContextPlanError("handoff item condition is not source-derived")
        if not isinstance(item["target_skills"], list):
            raise ContextPlanError("handoff item target_skills must be an array")
        item_targets.update(item["target_skills"])
    if sorted(item_targets) != handoff["target_skills"]:
        raise ContextPlanError("handoff item targets differ from handoff target_skills")
    if handoff["extraction_status"] != handoff_status:
        raise ContextPlanError("handoff item extraction_status aggregate differs")


def _load_contract(bundle_root, skill):
    resolver.validate_safe_id(skill, "skill")
    index, index_raw = _load_json(bundle_root, INDEX_REF, "skill contract index")
    _exact(
        index,
        {
            "$schema", "schema_version", "contract_count", "contract_schema",
            "source_catalog", "shared_contract", "contracts",
        },
        "skill contract index",
    )
    if index["schema_version"] != "1.0" or index["contract_count"] != 120:
        raise ContextPlanError("skill contract index version/count is unsupported")
    _file_ref(index["contract_schema"], "skill contract index.contract_schema")
    _file_ref(index["shared_contract"], "skill contract index.shared_contract")
    source_catalog = index["source_catalog"]
    _exact(source_catalog, {"path", "sha256", "version"}, "skill contract index.source_catalog")
    resolver.validate_relative_path(source_catalog["path"], "source catalog path")
    resolver.validate_sha(source_catalog["sha256"], "source catalog hash")
    if source_catalog["path"] != CATALOG_REF:
        raise ContextPlanError("skill contract index points at an unsupported catalog")
    entries = index["contracts"]
    if not isinstance(entries, list) or len(entries) != index["contract_count"]:
        raise ContextPlanError("skill contract index contracts do not match contract_count")
    names = []
    selected = None
    for offset, entry in enumerate(entries):
        label = "skill contract index.contracts[%d]" % offset
        _exact(entry, {"skill", "contract_ref", "contract_sha256"}, label)
        resolver.validate_safe_id(entry["skill"], label + ".skill")
        resolver.validate_relative_path(entry["contract_ref"], label + ".contract_ref")
        resolver.validate_sha(entry["contract_sha256"], label + ".contract_sha256")
        names.append(entry["skill"])
        if entry["skill"] == skill:
            if selected is not None:
                raise ContextPlanError("skill contract index contains duplicate skill %s" % skill)
            selected = entry
    if len(names) != len(set(names)):
        raise ContextPlanError("skill contract index contains duplicate skills")
    if selected is None:
        raise ContextPlanError("skill is absent from machine-contract index: %s" % skill)

    contract, contract_raw = _load_json(
        bundle_root, selected["contract_ref"], "skill machine contract"
    )
    if _sha256(contract_raw) != selected["contract_sha256"]:
        raise ContextPlanError("skill machine contract hash differs from its index")
    _exact(
        contract,
        {
            "$schema", "schema_version", "contract_id", "identity", "routing_contract",
            "input_contract", "output_contract", "completion_contract", "handoff_contract",
            "context_hints", "provenance",
        },
        "skill machine contract",
    )
    if contract["schema_version"] != "1.0" or contract["contract_id"] != "skill:" + skill:
        raise ContextPlanError("skill machine contract identity is unsupported")
    identity = contract["identity"]
    _exact(
        identity, {"name", "path", "sha256", "version", "discipline", "phase", "class"},
        "skill machine contract.identity",
    )
    if identity["name"] != skill:
        raise ContextPlanError("skill machine contract name does not match index")
    resolver.validate_relative_path(identity["path"], "skill machine contract.identity.path")
    resolver.validate_sha(identity["sha256"], "skill machine contract.identity.sha256")
    skill_raw = _read(bundle_root, identity["path"])
    if _sha256(skill_raw) != identity["sha256"]:
        raise ContextPlanError("skill source hash differs from machine contract")
    try:
        skill_text = skill_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContextPlanError("skill source must be UTF-8") from exc
    if resolver._frontmatter_scalar(skill_text, "name") != skill:
        raise ContextPlanError("skill source name differs from machine contract")
    if resolver._frontmatter_scalar(skill_text, "version") != identity["version"]:
        raise ContextPlanError("skill source version differs from machine contract")
    if not resolver.SKILL_SEMVER.fullmatch(identity["version"]):
        raise ContextPlanError("skill machine contract version must be semver")
    if identity["discipline"] not in resolver.COMMANDS | {"protocol"}:
        raise ContextPlanError("skill machine contract discipline is unsupported")
    _validate_machine_projection(contract)

    hints = contract["context_hints"]
    _exact(hints, {"bundle_references", "project_paths"}, "skill machine contract.context_hints")
    if not isinstance(hints["bundle_references"], list) or not isinstance(
            hints["project_paths"], list):
        raise ContextPlanError("skill machine contract context hints must be arrays")
    provenance = contract["provenance"]
    _exact(
        provenance, {"generator", "system_catalog", "shared_contract"},
        "skill machine contract.provenance",
    )
    if provenance["generator"] != "generate-skill-contracts-v1":
        raise ContextPlanError("skill machine contract generator is unsupported")
    contract_catalog = provenance["system_catalog"]
    _exact(contract_catalog, {"path", "sha256", "version"}, "contract system catalog")
    if contract_catalog != source_catalog:
        raise ContextPlanError("contract and index catalog provenance differ")
    contract_shared = provenance["shared_contract"]
    _exact(contract_shared, {"path", "sha256", "section"}, "contract shared contract")
    if {"path": contract_shared["path"], "sha256": contract_shared["sha256"]} != index[
            "shared_contract"]:
        raise ContextPlanError("contract and index shared-contract provenance differ")

    _verify_live_ref(bundle_root, index["contract_schema"], "contract schema")
    _verify_live_ref(bundle_root, index["shared_contract"], "shared contract")
    _verify_live_ref(
        bundle_root,
        {"path": source_catalog["path"], "sha256": source_catalog["sha256"]},
        "system catalog",
    )
    return contract, contract_raw, selected, index, index_raw


def _resource_id(scope, path):
    prefix = "b" if scope == "bundle" else "p"
    return "%s.%s" % (prefix, hashlib.sha256(path.encode("utf-8")).hexdigest()[:20])


def _candidate(scope, path, role, requirement, authority, observed_at, priority,
               reason_code, sensitivity, expected_sha256, *,
               load_policy="conditional", exclusive_group=None, condition_code=None):
    return {
        "resource_id": _resource_id(scope, path),
        "scope": scope,
        "path": path,
        "role": role,
        "requirement": requirement,
        "authority": authority,
        "observed_at": observed_at,
        "max_age_seconds": None,
        "priority": priority,
        "reason_code": reason_code,
        "sensitivity": sensitivity,
        "expected_sha256": expected_sha256,
        "conflict_group": None,
        "load_policy": load_policy,
        "exclusive_group": exclusive_group,
        "condition_code": condition_code,
        "supersedes": [],
    }


def _merge_candidate(candidates, candidate):
    key = (candidate["scope"], candidate["path"])
    current = candidates.get(key)
    if current is None:
        candidates[key] = candidate
        return
    if REQUIREMENT_RANK[candidate["requirement"]] < REQUIREMENT_RANK[current["requirement"]]:
        current["requirement"] = candidate["requirement"]
    if AUTHORITY_RANK[candidate["authority"]] < AUTHORITY_RANK[current["authority"]]:
        current["authority"] = candidate["authority"]
    if candidate["priority"] > current["priority"]:
        current["priority"] = candidate["priority"]
        current["role"] = candidate["role"]
        current["reason_code"] = candidate["reason_code"]
    if candidate["sensitivity"] == "restricted":
        current["sensitivity"] = "restricted"
    if candidate["expected_sha256"] is not None:
        if current["expected_sha256"] not in {None, candidate["expected_sha256"]}:
            raise ContextPlanError("candidate path has conflicting hashes: %s" % candidate["path"])
        current["expected_sha256"] = candidate["expected_sha256"]


def _project_hash(project_root, relative):
    raw = _read(project_root, relative, missing_ok=True)
    return _sha256(raw) if raw is not None else None


def _validate_prefix_root(project_root, relative):
    resolver.validate_relative_path(relative, "project prefix")
    current = Path(project_root)
    for part in relative.split("/"):
        current = current / part
        try:
            status = os.lstat(current)
        except FileNotFoundError:
            return None
        except OSError as exc:
            raise ContextPlanError("cannot inspect project prefix %s: %s" % (relative, exc)) from exc
        if statmod.S_ISLNK(status.st_mode):
            raise ContextPlanError("project prefix traverses a symlink: %s" % relative)
        if not statmod.S_ISDIR(status.st_mode):
            raise ContextPlanError("project prefix is not a directory: %s" % relative)
    return current


def _enumerate_prefix(project_root, relative, remaining):
    directory = _validate_prefix_root(project_root, relative)
    if directory is None:
        return "unresolved", []
    discovered = []
    stack = [directory]
    while stack:
        current = stack.pop()
        try:
            entries = sorted(os.scandir(current), key=lambda entry: entry.name, reverse=True)
        except OSError as exc:
            raise ContextPlanError("cannot enumerate project prefix %s: %s" % (relative, exc)) from exc
        for entry in entries:
            try:
                if entry.is_symlink():
                    raise ContextPlanError("project prefix contains a symlink: %s" % entry.path)
                if entry.is_dir(follow_symlinks=False):
                    stack.append(Path(entry.path))
                    continue
                if not entry.is_file(follow_symlinks=False):
                    raise ContextPlanError("project prefix contains a non-regular entry: %s" % entry.path)
            except OSError as exc:
                raise ContextPlanError("cannot inspect project prefix entry: %s" % exc) from exc
            path = Path(entry.path).relative_to(project_root).as_posix()
            resolver.validate_relative_path(path, "discovered project path")
            discovered.append(path)
            if len(discovered) > remaining:
                raise ContextPlanError(
                    "project prefix discovery exceeds prefix_file_limit; increase the explicit limit"
                )
    return "enumerated", sorted(discovered)


def _bundle_reference_candidates(bundle_root, contract, observed_at, auditor=None):
    result = []
    fallback_path = None
    if auditor is not None:
        fallback_path = "%s/references/auditor-runtime.md" % auditor["path"]
    for offset, reference in enumerate(contract["context_hints"]["bundle_references"]):
        label = "bundle_references[%d]" % offset
        _exact(reference, {"path", "sha256", "requirement", "reason_code", "source_line"}, label)
        resolver.validate_relative_path(reference["path"], label + ".path")
        resolver.validate_sha(reference["sha256"], label + ".sha256")
        if reference["requirement"] not in {"required", "optional"}:
            raise ContextPlanError("%s requirement is unsupported" % label)
        raw = _read(bundle_root, reference["path"])
        if _sha256(raw) != reference["sha256"]:
            raise ContextPlanError("%s differs from its recorded hash" % label)
        exclusive_group = None
        condition_code = None
        load_policy = "activation" if reference["requirement"] == "required" else "conditional"
        if fallback_path is not None and reference["path"] == fallback_path:
            exclusive_group = AUDITOR_EXCLUSIVE_GROUP
            condition_code = "standalone-skill"
            load_policy = "fallback"
        elif auditor is not None and reference["path"].startswith("references/"):
            exclusive_group = AUDITOR_EXCLUSIVE_GROUP
            condition_code = "repository-or-plugin"
        result.append(_candidate(
            "bundle", reference["path"], "skill-reference", reference["requirement"],
            "approved", observed_at, 85 if reference["requirement"] == "required" else 50,
            reference["reason_code"], "public", reference["sha256"],
            load_policy=load_policy, exclusive_group=exclusive_group,
            condition_code=condition_code,
        ))
    if auditor is not None:
        branches = {
            candidate["condition_code"] for candidate in result
            if candidate["exclusive_group"] == AUDITOR_EXCLUSIVE_GROUP
        }
        if branches != {"repository-or-plugin", "standalone-skill"}:
            raise ContextPlanError(
                "auditor context must declare repository/plugin and standalone runtime branches"
            )
    return result


def _auditor_spec(bundle_root, skill):
    catalog, _raw = _load_json(bundle_root, CATALOG_REF, "system catalog")
    matches = [
        auditor for auditor in catalog.get("auditors", [])
        if auditor.get("skill") == skill
    ]
    if len(matches) > 1:
        raise ContextPlanError("system catalog contains duplicate auditor: %s" % skill)
    return matches[0] if matches else None


def _condition_applies(candidate, distribution_profile):
    condition = candidate.get("condition_code")
    if condition is None:
        return True
    if condition == "repository-or-plugin":
        return distribution_profile in {"repository", "plugin"}
    if condition == "standalone-skill":
        return distribution_profile == "standalone-skill"
    raise ContextPlanError("unsupported context condition: %s" % condition)


def _planned_bundle_candidates(
        bundle_root, contract, entry, index, observed_at, *, command,
        post_route, distribution_profile, auditor=None):
    """Rebuild the exact bundle closure from current authoritative sources."""
    if not isinstance(post_route, bool):
        raise ContextPlanError("post_route must be boolean")
    if distribution_profile not in resolver.DISTRIBUTION_PROFILES:
        raise ContextPlanError("distribution_profile is unsupported")
    if command not in resolver.COMMANDS:
        raise ContextPlanError("command is unsupported")

    candidates = {}
    bases = (
        (contract["identity"]["path"], "skill-definition", "required", 100,
         "machine-contract-skill", contract["identity"]["sha256"], "always"),
        (entry["contract_ref"], "skill-contract", "required", 99,
         "machine-contract", entry["contract_sha256"], "always"),
        (SHARED_CONTRACT_REF, "shared-contract", "required", 90,
         "shared-skill-contract", index["shared_contract"]["sha256"], "activation"),
    )
    for path, role, requirement, priority, reason, digest, load_policy in bases:
        _merge_candidate(candidates, _candidate(
            "bundle", path, role, requirement, "approved", observed_at,
            priority, reason, "public", digest, load_policy=load_policy,
        ))
    for candidate in _bundle_reference_candidates(
            bundle_root, contract, observed_at, auditor=auditor):
        _merge_candidate(candidates, candidate)

    shards = []
    if command == "auto" and not post_route:
        shards = ["references/auto-routing/%s.md" % _primary_discipline(contract)]
    for shard in shards:
        raw = _read(bundle_root, shard)
        _merge_candidate(candidates, _candidate(
            "bundle", shard, "routing-scenario", "required", "approved",
            observed_at, 100, "auto-routing-shard", "public", _sha256(raw),
            load_policy="activation",
        ))

    # Validate every closed condition against the selected planner profile,
    # while retaining both declared auditor branches in the candidate set.
    for candidate in candidates.values():
        _condition_applies(candidate, distribution_profile)
    return sorted(
        candidates.values(),
        key=lambda item: (item["scope"], item["path"], item["resource_id"]),
    ), shards


def _project_candidates(project_root, contract, observed_at, prefix_file_limit):
    candidates = {}
    prefix_outcomes = []
    for relative in DEFAULT_PROJECT_PATHS:
        authority = "approved" if relative == "memory/decisions.md" else "working"
        _merge_candidate(candidates, _candidate(
            "project", relative, "working-memory", "optional", authority, observed_at,
            40, "working-memory-default", "confidential", _project_hash(project_root, relative),
        ))
    discovered_count = 0
    for offset, hint in enumerate(contract["context_hints"]["project_paths"]):
        label = "project_paths[%d]" % offset
        _exact(
            hint, {"path", "kind", "access", "authority", "sensitivity", "reason_code"}, label
        )
        resolver.validate_relative_path(hint["path"], label + ".path")
        if hint["kind"] == "file":
            paths = [hint["path"]]
        elif hint["kind"] == "prefix":
            status, paths = _enumerate_prefix(
                project_root, hint["path"], prefix_file_limit - discovered_count
            )
            discovered_count += len(paths)
            prefix_outcomes.append({
                "path": hint["path"],
                "status": status,
                "file_count": len(paths),
                "reason_code": "missing-prefix" if status == "unresolved" else None,
            })
        else:
            raise ContextPlanError("%s kind is unsupported" % label)
        for relative in paths:
            _merge_candidate(candidates, _candidate(
                "project", relative, "skill-read", "optional", hint["authority"], observed_at,
                70, hint["reason_code"], hint["sensitivity"],
                _project_hash(project_root, relative),
            ))
    return list(candidates.values()), sorted(
        prefix_outcomes, key=lambda item: (item["path"], item["status"])
    )


def _primary_discipline(contract):
    discipline = contract["identity"]["discipline"]
    if discipline != "protocol":
        return discipline
    skill = contract["identity"]["name"]
    try:
        return PROTOCOL_DISCIPLINES[skill]
    except KeyError as exc:
        raise ContextPlanError("protocol skill has no explicit routing-shard mapping: %s" % skill) from exc


def build_request(
        *, skill, run_id, turn_id, as_of, project_root, bundle_root=ROOT, command=None,
        reason_code="machine-contract-plan",
        max_tokens=65_536, bytes_per_token=4, max_resources=128,
        max_sensitivity="confidential", prefix_file_limit=128, registry_offsets=None,
        distribution_profile="repository", post_route=False):
    """Return a deterministic, resolver-valid request; do not write any files."""
    bundle_root = resolver.normalized_root(bundle_root, "bundle root")
    project_root = resolver.normalized_root(project_root, "project root")
    resolver.validate_uuid(run_id, "run_id")
    resolver.validate_safe_id(turn_id, "turn_id")
    resolver.validate_safe_id(reason_code, "reason_code")
    resolver.parse_datetime(as_of, "as_of")
    max_tokens = resolver.validate_int(max_tokens, "max_tokens", 1, MAX_DOCUMENT_BYTES)
    bytes_per_token = resolver.validate_int(bytes_per_token, "bytes_per_token", 1, 16)
    max_bytes = max_tokens * bytes_per_token
    if max_bytes > resolver.MAX_CONTEXT_BYTES:
        raise ContextPlanError("token proxy exceeds the resolver's maximum byte budget")
    max_resources = resolver.validate_int(max_resources, "max_resources", 1, 256)
    prefix_file_limit = resolver.validate_int(prefix_file_limit, "prefix_file_limit", 1, 256)
    if max_sensitivity not in resolver.SENSITIVITIES:
        raise ContextPlanError("max_sensitivity is unsupported")
    if distribution_profile not in resolver.DISTRIBUTION_PROFILES:
        raise ContextPlanError("distribution_profile is unsupported")
    if not isinstance(post_route, bool):
        raise ContextPlanError("post_route must be boolean")

    contract, contract_raw, entry, index, index_raw = _load_contract(bundle_root, skill)
    auditor = _auditor_spec(bundle_root, skill)
    primary = _primary_discipline(contract)
    if command is None:
        command = "auto" if contract["identity"]["discipline"] == "protocol" else primary
    if command not in resolver.COMMANDS:
        raise ContextPlanError("command is unsupported")
    bundle_candidates, shards = _planned_bundle_candidates(
        bundle_root, contract, entry, index, as_of, command=command,
        post_route=post_route, distribution_profile=distribution_profile,
        auditor=auditor,
    )
    candidates = {
        (candidate["scope"], candidate["path"]): candidate
        for candidate in bundle_candidates
    }
    project_candidates, prefix_outcomes = _project_candidates(
        project_root, contract, as_of, prefix_file_limit
    )
    for candidate in project_candidates:
        _merge_candidate(candidates, candidate)
    candidate_list = sorted(
        candidates.values(), key=lambda item: (item["scope"], item["path"], item["resource_id"])
    )
    if len(candidate_list) > resolver.MAX_CANDIDATES:
        raise ContextPlanError("discovered candidate set exceeds resolver maximum")
    required_bytes = 0
    for candidate in candidate_list:
        if (candidate["requirement"] != "required"
                or not _condition_applies(candidate, distribution_profile)):
            continue
        raw = _read(bundle_root if candidate["scope"] == "bundle" else project_root,
                    candidate["path"])
        required_bytes += len(raw)
    if required_bytes > max_bytes:
        raise ContextPlanError(
            "required context is %d bytes, above the %d-byte token proxy; increase --max-tokens"
            % (required_bytes, max_bytes)
        )
    required_resources = sum(
        candidate["requirement"] == "required"
        and _condition_applies(candidate, distribution_profile)
        for candidate in candidate_list
    )
    if required_resources > max_resources:
        raise ContextPlanError(
            "required context has %d resources, above --max-resources %d"
            % (required_resources, max_resources)
        )

    offsets = {name: None for name in resolver.REGISTRIES}
    if registry_offsets is not None:
        offsets.update(registry_offsets)
    resolver.validate_offsets(offsets)
    request = {
        "schema_version": "1.0",
        "run_id": run_id,
        "turn_id": turn_id,
        "as_of": as_of,
        "route": {
            "command": command,
            "target_skill": skill,
            "reason_code": reason_code,
            "scenario_shards": shards,
        },
        "budget": {
            "max_bytes": max_bytes,
            "max_resources": max_resources,
            "max_sensitivity": max_sensitivity,
            "max_inspection_bytes": min(resolver.MAX_INSPECTION_BYTES, max_bytes * 2),
        },
        "planner": {
            "planner_version": "1.1",
            "generator": "context-plan-v1.1",
            "post_route": post_route,
            "skill_contract": {"path": entry["contract_ref"], "sha256": _sha256(contract_raw)},
            "contract_index": {"path": INDEX_REF, "sha256": _sha256(index_raw)},
            "system_catalog": {
                "path": index["source_catalog"]["path"],
                "sha256": index["source_catalog"]["sha256"],
            },
            "distribution_profile": distribution_profile,
            "candidate_discovery": {
                "mode": "closed-machine-contract",
                "hints_sha256": _json_hash(contract["context_hints"]),
                "candidate_set_sha256": _json_hash(candidate_list),
                "prefix_file_limit": prefix_file_limit,
                "prefix_outcomes": prefix_outcomes,
            },
            "freshness": {
                "observed_at_basis": "planner-as-of-inspection",
                "default_max_age_seconds": None,
            },
            "token_budget": {
                "max_tokens": max_tokens,
                "bytes_per_token": bytes_per_token,
                "derived_max_bytes": max_bytes,
                "estimator": "utf8-bytes-per-token-proxy-v1",
                "enforcement": "derived-byte-ceiling",
            },
        },
        "registry_offsets": offsets,
        "candidates": candidate_list,
    }
    resolver.validate_request(request)
    resolver.validate_route_against_catalog(request, bundle_root)
    return request


def validate_planned_request(
        request, *, bundle_root=ROOT, project_root=None, resolve_sources=False,
        _skip_resolve=False):
    """Validate planner semantics and pinned provenance; optionally read all sources."""
    bundle_root = resolver.normalized_root(bundle_root, "bundle root")
    resolver.validate_request(request)
    if "planner" not in request:
        raise ContextPlanError("request has no context-plan provenance")
    planner = request["planner"]
    for field in ("skill_contract", "contract_index", "system_catalog"):
        _verify_live_ref(bundle_root, planner[field], "planner." + field)
    contract, contract_raw, entry, index, _index_raw = _load_contract(
        bundle_root, request["route"]["target_skill"]
    )
    if planner["skill_contract"] != {
            "path": entry["contract_ref"], "sha256": _sha256(contract_raw)}:
        raise ContextPlanError("planner selected contract differs from indexed contract")
    if planner["candidate_discovery"]["hints_sha256"] != _json_hash(
            contract["context_hints"]):
        raise ContextPlanError("planner hints hash differs from selected contract")
    expected_prefixes = sorted(
        hint["path"] for hint in contract["context_hints"]["project_paths"]
        if hint["kind"] == "prefix"
    )
    outcomes = planner["candidate_discovery"]["prefix_outcomes"]
    if [item["path"] for item in outcomes] != expected_prefixes:
        raise ContextPlanError("planner prefix outcomes do not cover contract prefix hints")
    resolver.validate_route_against_catalog(request, bundle_root)
    auditor = _auditor_spec(bundle_root, request["route"]["target_skill"])
    expected_bundle, expected_shards = _planned_bundle_candidates(
        bundle_root, contract, entry, index, request["as_of"],
        command=request["route"]["command"],
        post_route=planner["post_route"],
        distribution_profile=planner["distribution_profile"],
        auditor=auditor,
    )
    if request["route"]["scenario_shards"] != expected_shards:
        raise ContextPlanError(
            "planned route shards differ from the current route stage"
        )
    planned_bundle = [
        candidate for candidate in request["candidates"]
        if candidate["scope"] == "bundle"
    ]
    if expected_bundle != planned_bundle:
        raise ContextPlanError(
            "bundle candidate closure differs from current machine contract"
        )
    if resolve_sources:
        if project_root is None:
            raise ContextPlanError("project_root is required to validate candidate sources")
        normalized_project = resolver.normalized_root(project_root, "project root")
        current_candidates, current_outcomes = _project_candidates(
            normalized_project, contract, request["as_of"],
            planner["candidate_discovery"]["prefix_file_limit"],
        )
        if current_outcomes != outcomes:
            raise ContextPlanError("project prefix discovery differs from planned outcomes")
        expected_project = sorted(
            current_candidates,
            key=lambda item: (item["scope"], item["path"], item["resource_id"]),
        )
        planned_project = [
            candidate for candidate in request["candidates"] if candidate["scope"] == "project"
        ]
        if expected_project != planned_project:
            raise ContextPlanError("project candidate discovery differs from planned candidates")
        expected_candidates = sorted(
            [*expected_bundle, *expected_project],
            key=lambda item: (item["scope"], item["path"], item["resource_id"]),
        )
        if request["candidates"] != expected_candidates:
            raise ContextPlanError(
                "complete candidate closure differs from current planner discovery"
            )
        if planner["candidate_discovery"]["candidate_set_sha256"] != _json_hash(
                expected_candidates):
            raise ContextPlanError(
                "planner candidate_set_sha256 differs from current candidate closure"
            )
        if not _skip_resolve:
            resolver.resolve_context(request, bundle_root, project_root)
    return request


def _parse_offsets(values):
    offsets = {}
    for raw in values:
        if "=" not in raw:
            raise ContextPlanError("registry offsets must use NAME=INTEGER")
        name, text = raw.split("=", 1)
        if name in offsets:
            raise ContextPlanError("duplicate registry offset: %s" % name)
        if name not in resolver.REGISTRIES:
            raise ContextPlanError("unsupported registry offset: %s" % name)
        try:
            value = int(text)
        except ValueError as exc:
            raise ContextPlanError("registry offset must be an integer: %s" % name) from exc
        offsets[name] = value
    return offsets


def _write_json(path, value):
    content = (json.dumps(
        value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
    ) + "\n").encode("utf-8")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".%s." % target.name, dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="operation", required=True)
    plan = subparsers.add_parser("plan", help="write a closed context request")
    plan.add_argument("--skill", required=True)
    plan.add_argument("--run-id", required=True)
    plan.add_argument("--turn-id", required=True)
    plan.add_argument("--as-of", required=True, help="explicit RFC 3339 planner inspection time")
    plan.add_argument("--project-root", required=True)
    plan.add_argument("--bundle-root", default=str(ROOT))
    plan.add_argument("--command", choices=sorted(resolver.COMMANDS))
    plan.add_argument("--reason-code", default="machine-contract-plan")
    plan.add_argument("--max-tokens", type=int, default=65_536)
    plan.add_argument("--bytes-per-token", type=int, default=4)
    plan.add_argument("--max-resources", type=int, default=128)
    plan.add_argument("--max-sensitivity", choices=sorted(resolver.SENSITIVITIES),
                      default="confidential")
    plan.add_argument("--prefix-file-limit", type=int, default=128)
    plan.add_argument(
        "--distribution-profile", choices=sorted(resolver.DISTRIBUTION_PROFILES),
        default="repository",
        help="select repository/plugin policy sources or the standalone auditor fallback",
    )
    plan.add_argument(
        "--post-route", action="store_true",
        help="assemble a selected protocol Skill without its routing-only shard",
    )
    plan.add_argument("--registry-offset", action="append", default=[], metavar="NAME=INTEGER")
    plan.add_argument("--output", required=True)

    validate = subparsers.add_parser("validate", help="validate provenance and candidate sources")
    validate.add_argument("--request", required=True)
    validate.add_argument("--project-root", required=True)
    validate.add_argument("--bundle-root", default=str(ROOT))
    args = parser.parse_args(argv)
    try:
        if args.operation == "plan":
            request = build_request(
                skill=args.skill, run_id=args.run_id, turn_id=args.turn_id, as_of=args.as_of,
                project_root=args.project_root, bundle_root=args.bundle_root, command=args.command,
                reason_code=args.reason_code,
                max_tokens=args.max_tokens, bytes_per_token=args.bytes_per_token,
                max_resources=args.max_resources, max_sensitivity=args.max_sensitivity,
                prefix_file_limit=args.prefix_file_limit,
                registry_offsets=_parse_offsets(args.registry_offset),
                distribution_profile=args.distribution_profile,
                post_route=args.post_route,
            )
            _write_json(args.output, request)
            print("wrote context request with %d explicit candidates" % len(request["candidates"]))
            return 0
        request, _raw = _load_json(
            Path(args.request).parent, Path(args.request).name, "context request"
        )
        validate_planned_request(
            request, bundle_root=args.bundle_root, project_root=args.project_root,
            resolve_sources=True,
        )
        print("context request is valid and source-pinned")
        return 0
    except (ContextPlanError, OSError, ValueError) as exc:
        print("context-plan: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
