#!/usr/bin/env python3
"""Resolve host capabilities and evidence-gated model prompt detail profiles."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]
HOST_CATALOG_RELATIVE = Path("references/host-capability-profiles.json")
PROMPT_CATALOG_RELATIVE = Path("references/prompt-profiles.json")
CONTEXT_MODULE_CATALOG_RELATIVE = Path("references/context-modules.json")
MAX_CATALOG_BYTES = 256_000
MAX_EVIDENCE_BYTES = 8_000_000
MAX_CONTRACT_PACK_BYTES = 2_000_000
MAX_CONTRACT_PACK_EXPANDED_BYTES = 16_000_000
HOST_PROFILE_ORDER = (
    "standalone-skill-host",
    "generic-shared-root-host",
    "claude-code-plugin-host",
)
PROMPT_PROFILE_ORDER = ("explicit", "balanced", "lean")
CONSUMER_ORDER = ("controller", "model", "tool")
LOAD_POLICY_ORDER = ("always", "activation", "conditional", "lookup-only", "fallback")
SOURCE_ROLES = {
    "skill-definition", "skill-capsule", "machine-contract", "shared-skill-contract",
    "policy-kernel", "explicit-runtime-read", "authored-reference", "project-evidence",
    "routing-shard", "connector-catalog", "connector-implementation",
}
ALWAYS_ON_OVERLAYS = (
    "consent",
    "claims",
    "pii-secrets",
    "external-mutation",
    "audit-verdict",
    "release-provenance",
)
REDUCIBLE_DIMENSIONS = (
    "workflow-detail", "examples", "templates", "rationale", "reminders",
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_EVIDENCE_REF = re.compile(
    r"^references/prompt-profile-evidence/"
    r"[A-Za-z0-9][A-Za-z0-9._/-]*\.json$"
)
CERTIFICATE_CATALOG_KEYS = {
    "host_catalog_sha256", "prompt_policy_sha256", "context_modules_sha256",
    "system_catalog_sha256", "skill_contract_index_sha256",
    "capsule_index_sha256", "behavior_protocol_base_sha256",
    "behavior_protocol_sha256", "behavior_adapter_sha256",
    "context_assembly_sha256", "eval_case_runtime_sha256",
}
PACKAGE_CATALOG_PATHS = {
    "host_catalog_sha256": "references/host-capability-profiles.json",
    "context_modules_sha256": "references/context-modules.json",
    "system_catalog_sha256": "references/system-catalog.json",
    "capsule_index_sha256": "references/skill-capsules/index.json",
    "context_assembly_sha256": "scripts/context-assembly.py",
}


class ContextProfileError(ValueError):
    """Raised when a host/prompt profile cannot be resolved safely."""

    def __init__(self, code, message):
        super().__init__("%s: %s" % (code, message))
        self.code = code


def _strict_json_loads(raw, label):
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate key: %s" % key)
            value[key] = item
        return value

    try:
        text = raw.decode("utf-8")
        return json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=lambda item: (_ for _ in ()).throw(
                ValueError("non-finite constant: %s" % item)
            ),
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "%s must be strict UTF-8 JSON: %s" % (label, exc),
        ) from exc


def _canonical_json(value):
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "value cannot be encoded as canonical JSON: %s" % exc,
        ) from exc


def _exact(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "%s has unknown or missing fields" % label,
        )
    return value


def _normalized_root(path):
    supplied = Path(path)
    try:
        status = supplied.lstat()
    except OSError as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID",
            "cannot inspect bundle root: %s" % exc,
        ) from exc
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID",
            "bundle root must be a real directory",
        )
    try:
        return supplied.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID",
            "cannot resolve bundle root: %s" % exc,
        ) from exc


def _safe_relative(relative, label):
    if not isinstance(relative, str) or not relative or len(relative) > 512:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s is invalid" % label
        )
    path = Path(relative)
    if (
            path.is_absolute() or "\\" in relative or "//" in relative
            or relative.endswith("/") or any(part in {"", ".", ".."} for part in path.parts)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s is not a safe relative path" % label
        )
    return path


def _read_regular(bundle_root, relative, label, maximum):
    relative_path = _safe_relative(relative, label)
    current = bundle_root
    for index, part in enumerate(relative_path.parts):
        current = current / part
        try:
            before = current.lstat()
        except OSError as exc:
            raise ContextProfileError(
                "CONTEXT_PROFILE_FILESYSTEM_INVALID",
                "cannot inspect %s: %s" % (label, exc),
            ) from exc
        if stat.S_ISLNK(before.st_mode):
            raise ContextProfileError(
                "CONTEXT_PROFILE_FILESYSTEM_INVALID", "%s traverses a symlink" % label
            )
        final = index == len(relative_path.parts) - 1
        if not final and not stat.S_ISDIR(before.st_mode):
            raise ContextProfileError(
                "CONTEXT_PROFILE_FILESYSTEM_INVALID", "%s parent is not a directory" % label
            )
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID",
            "%s must be a single-link regular file" % label,
        )
    if before.st_size > maximum:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s exceeds %d bytes" % (label, maximum)
        )
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    descriptor = None
    try:
        descriptor = os.open(current, flags)
        opened = os.fstat(descriptor)
        identity = ("st_dev", "st_ino", "st_nlink", "st_mode")
        if (
                not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1
                or any(getattr(opened, field) != getattr(before, field) for field in identity)):
            raise ContextProfileError(
                "CONTEXT_PROFILE_FILESYSTEM_INVALID", "%s changed while opening" % label
            )
        chunks = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
        stable = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
        if len(raw) > maximum:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s exceeds %d bytes" % (label, maximum)
            )
        if any(getattr(opened, field) != getattr(after, field) for field in stable):
            raise ContextProfileError(
                "CONTEXT_PROFILE_FILESYSTEM_INVALID", "%s changed while reading" % label
            )
        return raw
    except OSError as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID", "cannot read %s: %s" % (label, exc)
        ) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _parse_datetime(value, label):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s must be an RFC3339 UTC date-time" % label
        )
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s is not a valid date-time" % label
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s must be UTC" % label
        )
    return parsed


def _prompt_policy_sha256(prompt_catalog):
    projection = _strict_json_loads(
        _canonical_json(prompt_catalog).encode("utf-8"), "prompt policy projection"
    )
    projection["certified_bindings"] = []
    return hashlib.sha256(_canonical_json(projection).encode("utf-8")).hexdigest()


def _read_contract_index(root):
    """Read the raw contract index or its exact member from the Governed pack."""
    relative = "references/skill-contracts/index.json"
    raw_path = root / relative
    try:
        raw_path.lstat()
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_FILESYSTEM_INVALID",
            "cannot inspect packaged skill-contract index: %s" % exc,
        ) from exc
    else:
        return _read_regular(root, relative, "skill-contract index", MAX_CATALOG_BYTES)
    compressed = _read_regular(
        root,
        "references/skill-contracts.pack.json.gz",
        "skill-contract pack",
        MAX_CONTRACT_PACK_BYTES,
    )
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(compressed), mode="rb") as handle:
            expanded = handle.read(MAX_CONTRACT_PACK_EXPANDED_BYTES + 1)
    except (OSError, EOFError) as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "skill-contract pack is not valid gzip: %s" % exc,
        ) from exc
    if len(expanded) > MAX_CONTRACT_PACK_EXPANDED_BYTES:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "skill-contract pack expands beyond limit"
        )
    pack = _strict_json_loads(expanded, "skill-contract pack")
    if not isinstance(pack, dict) or not isinstance(pack.get("files"), list):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "skill-contract pack identity is invalid"
        )
    matches = [item for item in pack["files"] if isinstance(item, dict) and item.get("path") == relative]
    if len(matches) != 1:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "skill-contract pack has no unique index"
        )
    item = _exact(
        matches[0], {"path", "bytes", "sha256", "content"},
        "packed skill-contract index",
    )
    if not isinstance(item["content"], dict):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "packed skill-contract index is not an object"
        )
    try:
        raw = (json.dumps(
            item["content"], ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
        ) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "packed skill-contract index is not encodable"
        ) from exc
    if (
            isinstance(item["bytes"], bool) or not isinstance(item["bytes"], int)
            or item["bytes"] != len(raw)
            or not isinstance(item["sha256"], str)
            or not SHA256.fullmatch(item["sha256"])
            or item["sha256"] != hashlib.sha256(raw).hexdigest()):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "packed skill-contract index hash differs"
        )
    return raw


def _current_package_catalog_hashes(root, prompt_catalog):
    hashes = {
        key: hashlib.sha256(
            _read_regular(root, relative, key, MAX_EVIDENCE_BYTES)
        ).hexdigest()
        for key, relative in PACKAGE_CATALOG_PATHS.items()
    }
    hashes["skill_contract_index_sha256"] = hashlib.sha256(
        _read_contract_index(root)
    ).hexdigest()
    hashes["prompt_policy_sha256"] = _prompt_policy_sha256(prompt_catalog)
    return hashes


def _validate_binding_evidence(binding, evidence_raw, label, prompt_catalog, root):
    """Validate the compact promotion certificate carried by Governed packages.

    Full paired/source/catalog recomputation is repository-side promotion work.
    The package trusts only this exact hash-bound projection, while still
    checking its release gates, identity, lifecycle, and current prompt policy.
    """
    certificate = _strict_json_loads(evidence_raw, label + " certificate")
    _exact(certificate, {
        "$schema", "schema_version", "kind", "protocol_version", "certificate_id",
        "paired_evidence", "distribution_profile", "host", "model", "profiles",
        "catalogs", "policy_snapshot_sha256", "evaluated_at", "expires_at",
        "aggregate", "decision", "promotion",
    }, label + " certificate")
    if (
            certificate["$schema"] != "../prompt-profile-release-certificate.schema.json"
            or certificate["schema_version"] != "1.0"
            or certificate["kind"] != "prompt-profile-release-certificate"
            or certificate["protocol_version"] != "3.0"
            or certificate["distribution_profile"] != "governed"):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate identity is invalid" % label
        )
    if not isinstance(certificate["certificate_id"], str) or not SAFE_ID.fullmatch(
            certificate["certificate_id"]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate_id is invalid" % label
        )
    paired = _exact(
        certificate["paired_evidence"], {
            "evidence_id", "sha256", "arm_run_set_sha256",
        },
        label + " paired_evidence",
    )
    if (
            not isinstance(paired["evidence_id"], str)
            or not SAFE_ID.fullmatch(paired["evidence_id"])
            or not isinstance(paired["sha256"], str)
            or not SHA256.fullmatch(paired["sha256"])
            or not isinstance(paired["arm_run_set_sha256"], str)
            or not SHA256.fullmatch(paired["arm_run_set_sha256"])
            or certificate["certificate_id"] != "certificate:%s" % paired[
                "evidence_id"
            ]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s paired evidence identity is invalid" % label
        )
    host = _exact(certificate["host"], {"host_profile", "host_name", "host_version"},
                  label + " host")
    model = _exact(certificate["model"], {
        "provider", "model_id", "model_revision", "judge_provider",
        "judge_model_id", "judge_model_revision",
    }, label + " model")
    profiles = _exact(certificate["profiles"], {"control", "candidate"}, label + " profiles")
    if (
            host["host_profile"] != binding["host_profile"]
            or model["model_id"] != binding["model_id"]
            or model["model_revision"] != binding["model_revision"]
            or not isinstance(model["model_revision"], str) or not model["model_revision"]
            or model["model_id"] == model["judge_model_id"]
            or not isinstance(model["judge_model_revision"], str)
            or not model["judge_model_revision"]
            or (
                model["provider"] == model["judge_provider"]
                and model["model_revision"] == model["judge_model_revision"]
            )
            or any(
                not isinstance(model[key], str) or not SAFE_ID.fullmatch(model[key])
                for key in (
                    "provider", "model_id", "judge_provider", "judge_model_id",
                )
            )
            or profiles != {"control": "explicit", "candidate": binding["prompt_profile"]}
            or binding["distribution_profile"] != "governed"
            or certificate["evaluated_at"] != binding["certified_at"]
            or certificate["expires_at"] != binding["expires_at"]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate binding identity differs" % label
        )
    catalogs = certificate["catalogs"]
    if not isinstance(catalogs, dict) or set(catalogs) != CERTIFICATE_CATALOG_KEYS:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate catalog set is invalid" % label
        )
    current_catalogs = _current_package_catalog_hashes(root, prompt_catalog)
    if any(catalogs.get(key) != value for key, value in current_catalogs.items()):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate package catalogs are stale" % label
        )
    policy_hash = hashlib.sha256(
        _canonical_json(prompt_catalog["certification_policy"]).encode("utf-8")
    ).hexdigest()
    if certificate["policy_snapshot_sha256"] != policy_hash:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate policy snapshot is stale" % label
        )
    aggregate = _exact(certificate["aggregate"], {
        "case_count", "pair_count", "coverage_stratum_count", "repeats",
        "arm_run_set_sha256", "advisories", "evidence_scope", "gates",
    }, label + " aggregate")
    advisories = _exact(aggregate["advisories"], {
        "paired_model_body_above_target_maximum",
        "harness_only_above_target_maximum",
        "provider_telemetry_incomplete",
    }, label + " advisories")
    for advisory in (
            "paired_model_body_above_target_maximum",
            "harness_only_above_target_maximum"):
        if (
                not isinstance(advisories[advisory], int)
                or isinstance(advisories[advisory], bool)
                or advisories[advisory] < 0):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID",
                "%s certificate advisory %s is invalid" % (label, advisory),
            )
    if not isinstance(advisories["provider_telemetry_incomplete"], bool):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "%s certificate provider telemetry advisory is invalid" % label,
        )
    gates = aggregate["gates"]
    expected_gates = {
        "minimum_cases", "minimum_repeats", "minimum_coverage_strata",
        "complete_pairs", "real_execution", "real_case_evidence",
        "immutable_model_identity", "immutable_judge_identity",
        "adapter_provenance", "assembly_source_equivalence",
        "minimum_candidate_reduction", "same_invariants", "current_age",
        "minimum_control_routing_accuracy", "minimum_candidate_routing_accuracy",
        "minimum_control_quality_pass_rate", "minimum_candidate_quality_pass_rate",
        "routing_noninferior", "quality_noninferior", "zero_safety_regressions",
        "zero_candidate_safety_failures",
    }
    if not isinstance(gates, dict) or set(gates) != expected_gates or not all(
            value is True for value in gates.values()):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate release gates did not pass" % label
        )
    policy = prompt_catalog["certification_policy"]
    for count_key in ("case_count", "pair_count", "coverage_stratum_count", "repeats"):
        if (
                not isinstance(aggregate[count_key], int)
                or isinstance(aggregate[count_key], bool) or aggregate[count_key] < 0):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID",
                "%s certificate %s is invalid" % (label, count_key),
            )
    if (
            aggregate["case_count"] < policy["minimum_cases"]
            or aggregate["repeats"] < policy["minimum_repeats"]
            or aggregate["coverage_stratum_count"] < policy[
                "minimum_coverage_strata"
            ]
            or aggregate["pair_count"] != aggregate["case_count"] * aggregate["repeats"]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate coverage is insufficient" % label
        )
    decision = _exact(certificate["decision"], {
        "valid", "reasons", "evidence_scope", "token_savings_claims_permitted",
        "cost_savings_claims_permitted",
    }, label + " decision")
    if (
            decision["valid"] is not True or decision["reasons"] != []
            or decision["token_savings_claims_permitted"] is not False
            or decision["cost_savings_claims_permitted"] is not False
            or decision["evidence_scope"] != aggregate["evidence_scope"]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s certificate decision is invalid" % label
        )
    promotion = _exact(certificate["promotion"], {
        "verifier_ref", "verifier_sha256", "promoted_at",
    }, label + " promotion")
    if (
            promotion["verifier_ref"] != "scripts/verify-prompt-profile-release.py"
            or not isinstance(promotion["verifier_sha256"], str)
            or not SHA256.fullmatch(promotion["verifier_sha256"])
            or promotion["verifier_sha256"] != hashlib.sha256(_read_regular(
                root, promotion["verifier_ref"], "prompt profile verifier",
                MAX_CATALOG_BYTES,
            )).hexdigest()
            or aggregate["arm_run_set_sha256"] != paired["arm_run_set_sha256"]):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s promotion identity is invalid" % label
        )
    promoted = _parse_datetime(promotion["promoted_at"], label + ".promoted_at")
    evaluated = _parse_datetime(certificate["evaluated_at"], label + ".evaluated_at")
    expires = _parse_datetime(certificate["expires_at"], label + ".expires_at")
    if not evaluated <= promoted < expires:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s promotion lifecycle is invalid" % label
        )


def _ordered_subset(values, order, label, *, minimum=0):
    if (
            not isinstance(values, list) or len(values) < minimum
            or len(values) != len(set(values))
            or any(value not in order for value in values)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s is not a unique catalog subset" % label
        )
    expected = [value for value in order if value in set(values)]
    if values != expected:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s must follow catalog order" % label
        )


def load_host_catalog(bundle_root=ROOT):
    root = _normalized_root(bundle_root)
    raw = _read_regular(
        root, str(HOST_CATALOG_RELATIVE), "host capability catalog", MAX_CATALOG_BYTES
    )
    value = _strict_json_loads(raw, "host capability catalog")
    _exact(value, {
        "$schema", "schema_version", "default_profile", "profile_order",
        "capability_order", "profiles",
    }, "host capability catalog")
    if (
            value["$schema"] != "./host-capability-profiles.schema.json"
            or value["schema_version"] != "1.0"
            or value["default_profile"] != "standalone-skill-host"
            or value["profile_order"] != list(HOST_PROFILE_ORDER)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "host catalog identity is unsupported"
        )
    capabilities = value["capability_order"]
    if (
            not isinstance(capabilities, list) or not capabilities
            or len(capabilities) != len(set(capabilities))
            or any(not isinstance(item, str) or not SAFE_ID.fullmatch(item) for item in capabilities)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "host capability_order is invalid"
        )
    profiles = value["profiles"]
    if not isinstance(profiles, dict) or set(profiles) != set(HOST_PROFILE_ORDER):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "host profile set is invalid"
        )
    previous = set()
    for rank, name in enumerate(HOST_PROFILE_ORDER):
        profile = _exact(profiles[name], {
            "rank", "capabilities", "compatible_distributions", "routing_surface",
            "reference_surface", "connector_surface",
        }, "host profile %s" % name)
        if profile["rank"] != rank:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host profile rank is invalid"
            )
        _ordered_subset(
            profile["capabilities"], capabilities,
            "host profile %s capabilities" % name, minimum=2,
        )
        current = set(profile["capabilities"])
        if not previous.issubset(current):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host capabilities must be monotonic"
            )
        previous = current
        distributions = profile["compatible_distributions"]
        allowed_distributions = {"repository", "plugin", "standalone-skill"}
        if (
                not isinstance(distributions, list) or not distributions
                or len(distributions) != len(set(distributions))
                or any(item not in allowed_distributions for item in distributions)):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host distributions are invalid"
            )
        routing = profile["routing_surface"]
        reference = profile["reference_surface"]
        connector = profile["connector_surface"]
        if routing not in {"direct-skill", "router-skills", "slash-commands"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host routing surface is invalid"
            )
        if reference not in {"skill-local-only", "shared-root"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host reference surface is invalid"
            )
        if connector not in {"none", "sidecar", "native-plugin"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "host connector surface is invalid"
            )
        required_capabilities = {
            "router-skills": "router-skills",
            "slash-commands": "slash-commands",
            "shared-root": "shared-root-references",
            "sidecar": "connector-sidecars",
            "native-plugin": "native-plugin-connectors",
        }
        for surface in (routing, reference, connector):
            requirement = required_capabilities.get(surface)
            if requirement is not None and requirement not in current:
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID",
                    "host surface %s lacks capability %s" % (surface, requirement),
                )
    return value, raw


def load_prompt_catalog(bundle_root=ROOT, host_catalog=None):
    root = _normalized_root(bundle_root)
    if host_catalog is None:
        host_catalog, unused = load_host_catalog(root)
    raw = _read_regular(
        root, str(PROMPT_CATALOG_RELATIVE), "prompt profile catalog", MAX_CATALOG_BYTES
    )
    value = _strict_json_loads(raw, "prompt profile catalog")
    _exact(value, {
        "$schema", "schema_version", "default_profile", "unknown_model_profile",
        "profile_order", "always_on_overlays", "reducible_dimensions", "profiles",
        "host_defaults", "certified_bindings", "certification_policy",
    }, "prompt profile catalog")
    if (
            value["$schema"] != "./prompt-profiles.schema.json"
            or value["schema_version"] != "1.0"
            or value["default_profile"] != "explicit"
            or value["unknown_model_profile"] != "explicit"
            or value["profile_order"] != list(PROMPT_PROFILE_ORDER)
            or value["always_on_overlays"] != list(ALWAYS_ON_OVERLAYS)
            or value["reducible_dimensions"] != list(REDUCIBLE_DIMENSIONS)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt catalog identity is unsupported"
        )
    profiles = value["profiles"]
    if not isinstance(profiles, dict) or set(profiles) != set(PROMPT_PROFILE_ORDER):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt profile set is invalid"
        )
    previous_minimum = -1
    previous_maximum = -1
    for rank, name in enumerate(PROMPT_PROFILE_ORDER):
        profile = _exact(profiles[name], {
            "rank", "requires_certification", "workflow_detail", "example_budget",
            "template_detail", "rationale_detail", "reminder_density",
            "target_model_context_reduction",
        }, "prompt profile %s" % name)
        if profile["rank"] != rank or profile["requires_certification"] != (rank > 0):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt profile rank/gate is invalid"
            )
        if profile["workflow_detail"] not in {"full", "compact", "minimum"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "workflow_detail is invalid"
            )
        if (
                isinstance(profile["example_budget"], bool)
                or not isinstance(profile["example_budget"], int)
                or not 0 <= profile["example_budget"] <= 4):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "example_budget is invalid"
            )
        if profile["template_detail"] not in {"expanded", "compact", "schema-only"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "template_detail is invalid"
            )
        if profile["rationale_detail"] not in {"full", "decision-only", "omitted"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "rationale_detail is invalid"
            )
        if profile["reminder_density"] not in {"repeated", "boundary-only", "once"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "reminder_density is invalid"
            )
        target = _exact(
            profile["target_model_context_reduction"],
            {"minimum_percent", "maximum_percent"},
            "prompt profile %s target reduction" % name,
        )
        minimum = target["minimum_percent"]
        maximum = target["maximum_percent"]
        if (
                isinstance(minimum, bool) or isinstance(maximum, bool)
                or not isinstance(minimum, int) or not isinstance(maximum, int)
                or minimum < 0 or maximum > 90 or minimum > maximum
                or minimum < previous_minimum or maximum < previous_maximum):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt reduction targets are invalid"
            )
        previous_minimum, previous_maximum = minimum, maximum
    host_defaults = value["host_defaults"]
    if (
            not isinstance(host_defaults, dict)
            or set(host_defaults) != set(host_catalog["profile_order"])
            or any(item not in PROMPT_PROFILE_ORDER for item in host_defaults.values())):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt host defaults are invalid"
        )
    policy = _exact(value["certification_policy"], {
        "protocol_version", "minimum_cases", "minimum_coverage_strata",
        "minimum_repeats",
        "minimum_control_routing_accuracy", "minimum_candidate_routing_accuracy",
        "minimum_control_quality_pass_rate", "minimum_candidate_quality_pass_rate",
        "maximum_routing_accuracy_regression", "maximum_quality_pass_rate_regression",
        "maximum_safety_regressions", "maximum_age_days",
    }, "prompt certification policy")
    if policy["protocol_version"] != "3.0" or policy["maximum_safety_regressions"] != 0:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt certification safety policy is invalid"
        )
    for field in (
            "minimum_cases", "minimum_repeats", "minimum_coverage_strata",
            "maximum_age_days"):
        item = policy[field]
        if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt policy %s is invalid" % field
            )
    for field in (
            "minimum_control_routing_accuracy", "minimum_candidate_routing_accuracy",
            "minimum_control_quality_pass_rate", "minimum_candidate_quality_pass_rate",
            "maximum_routing_accuracy_regression", "maximum_quality_pass_rate_regression"):
        item = policy[field]
        if isinstance(item, bool) or not isinstance(item, (int, float)) or not 0 <= item <= 1:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "prompt policy %s is invalid" % field
            )
    bindings = value["certified_bindings"]
    if not isinstance(bindings, list) or len(bindings) > 256:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "certified_bindings is invalid"
        )
    if bindings:
        # Bundled compact certificates are only self-authenticating hashes: the
        # package does not currently ship the complete paired evidence and
        # trusted verifier needed to re-run certification, nor a signed release
        # attestation.  Treat every non-empty production binding as untrusted.
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "non-empty certified_bindings require a signed release-attestation "
            "trust path and are not deployable",
        )
    seen_ids = set()
    seen_keys = set()
    for offset, binding in enumerate(bindings):
        label = "certified_bindings[%d]" % offset
        _exact(binding, {
            "binding_id", "distribution_profile", "host_profile", "model_id",
            "model_revision", "prompt_profile", "evidence_ref",
            "evidence_sha256", "certified_at", "expires_at",
        }, label)
        if not SAFE_ID.fullmatch(binding["binding_id"]):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.binding_id is invalid" % label
            )
        if binding["distribution_profile"] != "governed":
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID",
                "%s compact binding must target governed distribution" % label,
            )
        if binding["host_profile"] not in host_catalog["profiles"]:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.host_profile is invalid" % label
            )
        if not isinstance(binding["model_id"], str) or not SAFE_ID.fullmatch(binding["model_id"]):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.model_id is invalid" % label
            )
        if (
                not isinstance(binding["model_revision"], str)
                or not SAFE_ID.fullmatch(binding["model_revision"])):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.model_revision is invalid" % label
            )
        prompt_profile = binding["prompt_profile"]
        if prompt_profile not in {"balanced", "lean"} or not profiles[prompt_profile][
                "requires_certification"]:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.prompt_profile is invalid" % label
            )
        evidence_ref = binding["evidence_ref"]
        if not isinstance(evidence_ref, str) or not SAFE_EVIDENCE_REF.fullmatch(evidence_ref):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.evidence_ref is invalid" % label
            )
        if not isinstance(binding["evidence_sha256"], str) or not SHA256.fullmatch(
                binding["evidence_sha256"]):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.evidence_sha256 is invalid" % label
            )
        certified_at = _parse_datetime(binding["certified_at"], label + ".certified_at")
        expires_at = _parse_datetime(binding["expires_at"], label + ".expires_at")
        if expires_at <= certified_at:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s expiry is not after certification" % label
            )
        if binding["binding_id"] in seen_ids:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "duplicate certified binding id"
            )
        key = (
            binding["host_profile"], binding["model_id"], binding["model_revision"],
            prompt_profile,
        )
        if key in seen_keys:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "duplicate certified binding tuple"
            )
        seen_ids.add(binding["binding_id"])
        seen_keys.add(key)
        evidence_raw = _read_regular(root, evidence_ref, label + " evidence", MAX_EVIDENCE_BYTES)
        if hashlib.sha256(evidence_raw).hexdigest() != binding["evidence_sha256"]:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s evidence hash differs" % label
            )
        _validate_binding_evidence(binding, evidence_raw, label, value, root)
    return value, raw


def load_context_module_catalog(
        bundle_root=ROOT, host_catalog=None, prompt_catalog=None):
    root = _normalized_root(bundle_root)
    if host_catalog is None:
        host_catalog, unused = load_host_catalog(root)
    if prompt_catalog is None:
        prompt_catalog, unused = load_prompt_catalog(root, host_catalog)
    raw = _read_regular(
        root, str(CONTEXT_MODULE_CATALOG_RELATIVE),
        "context module catalog", MAX_CATALOG_BYTES,
    )
    value = _strict_json_loads(raw, "context module catalog")
    _exact(value, {
        "$schema", "schema_version", "consumer_order", "load_policy_order",
        "prompt_profile_order", "host_profile_order", "exclusive_groups", "modules",
    }, "context module catalog")
    if (
            value["$schema"] != "./context-modules.schema.json"
            or value["schema_version"] != "1.0"
            or value["consumer_order"] != list(CONSUMER_ORDER)
            or value["load_policy_order"] != list(LOAD_POLICY_ORDER)
            or value["prompt_profile_order"] != list(PROMPT_PROFILE_ORDER)
            or value["host_profile_order"] != list(HOST_PROFILE_ORDER)):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "context module catalog identity is unsupported"
        )
    groups = value["exclusive_groups"]
    expected_groups = {"model-policy-representation", "model-skill-representation"}
    if not isinstance(groups, dict) or set(groups) != expected_groups:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "context exclusive groups are invalid"
        )
    for name, group in groups.items():
        _exact(group, {"consumer", "selection"}, "context exclusive group %s" % name)
        if group != {
                "consumer": "model",
                "selection": "exactly-one-primary-per-applicable-host-and-prompt-profile"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "context exclusive group policy is invalid"
            )
    modules = value["modules"]
    if not isinstance(modules, list) or not 12 <= len(modules) <= 32:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "context modules must contain 12-32 entries"
        )
    seen = set()
    for offset, module in enumerate(modules):
        label = "context modules[%d]" % offset
        _exact(module, {
            "module_id", "consumer", "load_policy", "source_role", "materialization",
            "prompt_profiles", "host_profiles", "exclusive_group", "condition_code",
        }, label)
        module_id = module["module_id"]
        if not isinstance(module_id, str) or not SAFE_ID.fullmatch(module_id):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.module_id is invalid" % label
            )
        if module_id in seen:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "duplicate context module id"
            )
        seen.add(module_id)
        if module["consumer"] not in CONSUMER_ORDER:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.consumer is invalid" % label
            )
        if module["load_policy"] not in LOAD_POLICY_ORDER:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.load_policy is invalid" % label
            )
        if module["source_role"] not in SOURCE_ROLES:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.source_role is invalid" % label
            )
        if module["materialization"] not in {"body", "metadata", "on-demand"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.materialization is invalid" % label
            )
        _ordered_subset(
            module["prompt_profiles"], list(PROMPT_PROFILE_ORDER),
            "%s.prompt_profiles" % label, minimum=1,
        )
        _ordered_subset(
            module["host_profiles"], list(HOST_PROFILE_ORDER),
            "%s.host_profiles" % label, minimum=1,
        )
        group = module["exclusive_group"]
        if group is not None and (
                group not in groups or module["consumer"] != groups[group]["consumer"]):
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s.exclusive_group is invalid" % label
            )
        condition = module["condition_code"]
        needs_condition = module["load_policy"] in {"conditional", "lookup-only", "fallback"}
        if needs_condition:
            if not isinstance(condition, str) or not SAFE_ID.fullmatch(condition):
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s requires condition_code" % label
                )
        elif condition is not None:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s condition_code must be null" % label
            )
        if module["load_policy"] == "fallback" and group is not None:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "fallback modules cannot join a primary XOR"
            )
        if module["materialization"] == "on-demand" and module["load_policy"] not in {
                "conditional", "lookup-only"}:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "on-demand module has eager load policy"
            )
        if module["consumer"] == "tool" and "standalone-skill-host" in module["host_profiles"]:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "standalone host cannot claim tool modules"
            )
    for host_name in HOST_PROFILE_ORDER:
        for prompt_name in PROMPT_PROFILE_ORDER:
            skill_primary = [
                module for module in modules
                if module["exclusive_group"] == "model-skill-representation"
                and module["load_policy"] != "fallback"
                and host_name in module["host_profiles"]
                and prompt_name in module["prompt_profiles"]
            ]
            policy_primary = [
                module for module in modules
                if module["exclusive_group"] == "model-policy-representation"
                and module["load_policy"] != "fallback"
                and host_name in module["host_profiles"]
                and prompt_name in module["prompt_profiles"]
            ]
            if len(skill_primary) > 1 or len(policy_primary) > 1:
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID",
                    "context module XOR has multiple primaries for host=%s prompt=%s"
                    % (host_name, prompt_name),
                )
            if bool(skill_primary) != bool(policy_primary):
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID",
                    "context skill/policy representations differ for host=%s prompt=%s"
                    % (host_name, prompt_name),
                )
            if prompt_catalog["host_defaults"][host_name] == prompt_name and (
                    len(skill_primary) != 1 or len(policy_primary) != 1):
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID",
                    "host default prompt profile lacks an exact context representation",
                )
    return value, raw


def resolve_context_profile(
        *, bundle_root=ROOT, host_profile=None, model_id="unknown",
        model_revision=None, requested_prompt_profile=None, as_of=None,
        distribution_profile="repository"):
    """Return a deterministic, evidence-gated host + prompt profile resolution."""
    root = _normalized_root(bundle_root)
    host_catalog, host_raw = load_host_catalog(root)
    prompt_catalog, prompt_raw = load_prompt_catalog(root, host_catalog)
    module_catalog, module_raw = load_context_module_catalog(
        root, host_catalog, prompt_catalog
    )
    if host_profile in {None, "auto"}:
        host_profile = host_catalog["default_profile"]
        host_source = "portable-fallback"
    elif host_profile not in host_catalog["profiles"]:
        raise ContextProfileError(
            "CONTEXT_HOST_PROFILE_UNKNOWN", "unknown host profile: %s" % host_profile
        )
    else:
        host_source = "explicit"
    if not isinstance(model_id, str) or not SAFE_ID.fullmatch(model_id):
        raise ContextProfileError(
            "CONTEXT_MODEL_ID_INVALID", "model_id must be a safe, non-empty identifier"
        )
    if model_revision is not None and (
            not isinstance(model_revision, str) or not SAFE_ID.fullmatch(model_revision)):
        raise ContextProfileError(
            "CONTEXT_MODEL_REVISION_INVALID",
            "model_revision must be an immutable safe identifier when supplied",
        )
    if as_of is None:
        as_of = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    instant = _parse_datetime(as_of, "as_of")
    if distribution_profile not in {"repository", "lite", "pro", "governed"}:
        raise ContextProfileError(
            "CONTEXT_DISTRIBUTION_PROFILE_UNKNOWN",
            "unknown physical distribution profile: %s" % distribution_profile,
        )

    matching = []
    for binding in prompt_catalog["certified_bindings"]:
        if (
                binding["host_profile"] != host_profile
                or binding["model_id"] != model_id
                or binding["model_revision"] != model_revision
                or binding["distribution_profile"] != distribution_profile):
            continue
        certified_at = _parse_datetime(binding["certified_at"], "binding.certified_at")
        expires_at = _parse_datetime(binding["expires_at"], "binding.expires_at")
        if certified_at <= instant < expires_at:
            matching.append(binding)
    if requested_prompt_profile is not None:
        if requested_prompt_profile not in prompt_catalog["profiles"]:
            raise ContextProfileError(
                "CONTEXT_PROMPT_PROFILE_UNKNOWN",
                "unknown prompt profile: %s" % requested_prompt_profile,
            )
        selected_name = requested_prompt_profile
        if prompt_catalog["profiles"][selected_name]["requires_certification"]:
            selected = [
                item for item in matching if item["prompt_profile"] == selected_name
            ]
            if len(selected) != 1:
                raise ContextProfileError(
                    "CONTEXT_PROMPT_PROFILE_UNCERTIFIED",
                    "%s is not certified for host=%s model=%s revision=%s at %s"
                    % (selected_name, host_profile, model_id, model_revision, as_of),
                )
            binding = selected[0]
            prompt_source = "requested-certified-binding"
        else:
            binding = None
            prompt_source = "requested-safe-default"
    else:
        if model_id == "unknown":
            selected_name = prompt_catalog["unknown_model_profile"]
            binding = None
            prompt_source = "unknown-model-fallback"
        elif matching:
            binding = max(
                matching,
                key=lambda item: prompt_catalog["profiles"][item["prompt_profile"]]["rank"],
            )
            selected_name = binding["prompt_profile"]
            prompt_source = "certified-binding"
        else:
            selected_name = prompt_catalog["host_defaults"][host_profile]
            binding = None
            prompt_source = "host-default"
    host = host_catalog["profiles"][host_profile]
    prompt = prompt_catalog["profiles"][selected_name]
    active_modules = {consumer: [] for consumer in CONSUMER_ORDER}
    fallback_modules = []
    for module in module_catalog["modules"]:
        if host_profile not in module["host_profiles"] or selected_name not in module[
                "prompt_profiles"]:
            continue
        projection = {
            "module_id": module["module_id"],
            "load_policy": module["load_policy"],
            "source_role": module["source_role"],
            "materialization": module["materialization"],
            "condition_code": module["condition_code"],
        }
        if module["load_policy"] == "fallback":
            fallback_modules.append(projection)
        else:
            active_modules[module["consumer"]].append(projection)
    result = {
        "schema_version": "1.0",
        "as_of": as_of,
        "host_profile": host_profile,
        "host_profile_source": host_source,
        "model_id": model_id,
        "model_revision": model_revision,
        "distribution_profile": distribution_profile,
        "prompt_profile": selected_name,
        "prompt_profile_source": prompt_source,
        "binding_id": None if binding is None else binding["binding_id"],
        "capabilities": list(host["capabilities"]),
        "compatible_distributions": list(host["compatible_distributions"]),
        "routing_surface": host["routing_surface"],
        "reference_surface": host["reference_surface"],
        "connector_surface": host["connector_surface"],
        "always_on_overlays": list(ALWAYS_ON_OVERLAYS),
        "reducible_settings": {
            "workflow_detail": prompt["workflow_detail"],
            "example_budget": prompt["example_budget"],
            "template_detail": prompt["template_detail"],
            "rationale_detail": prompt["rationale_detail"],
            "reminder_density": prompt["reminder_density"],
        },
        "context_modules": active_modules,
        "fallback_modules": fallback_modules,
        "catalogs": {
            "host_sha256": hashlib.sha256(host_raw).hexdigest(),
            "prompt_sha256": hashlib.sha256(prompt_raw).hexdigest(),
            "context_modules_sha256": hashlib.sha256(module_raw).hexdigest(),
        },
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Resolve a capability-based host and evidence-gated prompt profile."
    )
    parser.add_argument("--bundle-root", default=str(ROOT))
    parser.add_argument("--host-profile", default="auto")
    parser.add_argument("--model-id", default="unknown")
    parser.add_argument(
        "--model-revision",
        help="Immutable provider/model snapshot revision required for compact certification.",
    )
    parser.add_argument("--prompt-profile", choices=PROMPT_PROFILE_ORDER)
    parser.add_argument(
        "--distribution-profile",
        choices=("repository", "lite", "pro", "governed"),
        default="repository",
    )
    parser.add_argument("--as-of")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.validate:
            root = _normalized_root(args.bundle_root)
            host, host_raw = load_host_catalog(root)
            prompt, prompt_raw = load_prompt_catalog(root, host)
            modules, module_raw = load_context_module_catalog(root, host, prompt)
            result = {
                "schema_version": "1.0",
                "valid": True,
                "host_profile_count": len(host["profiles"]),
                "prompt_profile_count": len(prompt["profiles"]),
                "certified_binding_count": len(prompt["certified_bindings"]),
                "context_module_count": len(modules["modules"]),
                "host_sha256": hashlib.sha256(host_raw).hexdigest(),
                "prompt_sha256": hashlib.sha256(prompt_raw).hexdigest(),
                "context_modules_sha256": hashlib.sha256(module_raw).hexdigest(),
            }
        else:
            result = resolve_context_profile(
                bundle_root=args.bundle_root,
                host_profile=args.host_profile,
                model_id=args.model_id,
                model_revision=args.model_revision,
                distribution_profile=args.distribution_profile,
                requested_prompt_profile=args.prompt_profile,
                as_of=args.as_of,
            )
    except ContextProfileError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(_canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
