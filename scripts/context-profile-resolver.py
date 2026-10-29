#!/usr/bin/env python3
"""Resolve verified host capabilities and the explicit model representation.

Compact prompt experiments have been retired. Historical experimental bundles
must be inspected with their pinned runtime; they cannot authorize deployment.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
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
HOST_PROFILE_ORDER = (
    "standalone-skill-host", "generic-shared-root-host", "claude-code-plugin-host",
)
PROMPT_PROFILE_ORDER = ("explicit",)
CONSUMER_ORDER = ("controller", "model", "tool")
LOAD_POLICY_ORDER = ("always", "activation", "conditional", "lookup-only")
SOURCE_ROLES = {
    "skill-definition", "machine-contract", "shared-skill-contract",
    "explicit-runtime-read", "authored-reference", "project-evidence",
    "routing-shard", "connector-catalog", "connector-implementation",
}
ALWAYS_ON_OVERLAYS = (
    "consent", "claims", "pii-secrets", "external-mutation",
    "audit-verdict", "release-provenance",
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


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
        host_catalog, _ = load_host_catalog(root)
    raw = _read_regular(
        root, str(PROMPT_CATALOG_RELATIVE), "prompt profile catalog", MAX_CATALOG_BYTES
    )
    value = _strict_json_loads(raw, "prompt profile catalog")
    _exact(value, {
        "$schema", "schema_version", "default_profile", "profile_order",
        "always_on_overlays", "profiles", "host_defaults",
    }, "prompt profile catalog")
    expected_profile = {
        "workflow_detail": "full", "example_budget": 4,
        "template_detail": "expanded", "rationale_detail": "full",
        "reminder_density": "repeated",
    }
    if (value["$schema"] != "./prompt-profiles.schema.json"
            or value["schema_version"] != "2.0"
            or value["default_profile"] != "explicit"
            or value["profile_order"] != ["explicit"]
            or value["always_on_overlays"] != list(ALWAYS_ON_OVERLAYS)
            or value["profiles"] != {"explicit": expected_profile}
            or value["host_defaults"] != {name: "explicit" for name in host_catalog["profile_order"]}):
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID",
            "only the verified explicit prompt catalog is supported; "
            "use a pinned historical runtime for retired experiments",
        )
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
            or value["schema_version"] != "2.0"
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
    if not isinstance(modules, list) or not 12 <= len(modules) <= 24:
        raise ContextProfileError(
            "CONTEXT_PROFILE_DOCUMENT_INVALID", "context modules must contain 12-24 entries"
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
        needs_condition = module["load_policy"] in {"conditional", "lookup-only"}
        if needs_condition:
            if not isinstance(condition, str) or not SAFE_ID.fullmatch(condition):
                raise ContextProfileError(
                    "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s requires condition_code" % label
                )
        elif condition is not None:
            raise ContextProfileError(
                "CONTEXT_PROFILE_DOCUMENT_INVALID", "%s condition_code must be null" % label
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
                and host_name in module["host_profiles"]
                and prompt_name in module["prompt_profiles"]
            ]
            policy_primary = [
                module for module in modules
                if module["exclusive_group"] == "model-policy-representation"
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
    """Return a deterministic host + explicit prompt resolution."""
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
    _parse_datetime(as_of, "as_of")
    if distribution_profile not in {"repository", "lite", "pro", "governed"}:
        raise ContextProfileError(
            "CONTEXT_DISTRIBUTION_PROFILE_UNKNOWN",
            "unknown physical distribution profile: %s" % distribution_profile,
        )

    if requested_prompt_profile not in {None, "explicit"}:
        raise ContextProfileError(
            "CONTEXT_PROMPT_PROFILE_UNSUPPORTED",
            "only explicit prompt deployment is supported; compact experiments are retired",
        )
    selected_name = "explicit"
    prompt_source = (
        "requested-safe-default" if requested_prompt_profile is not None else
        "unknown-model-fallback" if model_id == "unknown" else "host-default"
    )
    host = host_catalog["profiles"][host_profile]
    prompt = prompt_catalog["profiles"][selected_name]
    active_modules = {consumer: [] for consumer in CONSUMER_ORDER}
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
        "binding_id": None,
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
        "fallback_modules": [],
        "catalogs": {
            "host_sha256": hashlib.sha256(host_raw).hexdigest(),
            "prompt_sha256": hashlib.sha256(prompt_raw).hexdigest(),
            "context_modules_sha256": hashlib.sha256(module_raw).hexdigest(),
        },
    }
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Resolve verified host capabilities and explicit prompt context."
    )
    parser.add_argument("--bundle-root", default=str(ROOT))
    parser.add_argument("--host-profile", default="auto")
    parser.add_argument("--model-id", default="unknown")
    parser.add_argument(
        "--model-revision",
        help="Provider/model snapshot revision, when available.",
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
