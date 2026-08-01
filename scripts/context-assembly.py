#!/usr/bin/env python3
"""Project a verified manifest into separate controller/model/tool contexts."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat as statmod
import sys


ROOT = Path(__file__).resolve().parents[1]
CAPSULE_INDEX_REF = "references/skill-capsules/index.json"
DISTRIBUTION_MANIFEST_REF = "distribution-manifest.json"
MAX_DOCUMENT_BYTES = 8_000_000
TRUSTED_DISTRIBUTION_FILES = (
    "references/host-capability-profiles.json",
    "references/prompt-profiles.json",
    "references/context-modules.json",
    "scripts/context-profile-resolver.py",
    "scripts/context-resolver.py",
    "scripts/context-plan.py",
    "scripts/context-assembly.py",
)
TRUSTED_EXECUTED_RUNTIME_FILES = (
    "scripts/context-profile-resolver.py",
    "scripts/context-resolver.py",
    "scripts/context-plan.py",
    "scripts/context-assembly.py",
)
ROUTER_FACADE_SIDECAR_REF = "router-facades/sidecar-manifest.json"
SHARED_HOST_PROFILES = {"generic-shared-root-host", "claude-code-plugin-host"}
PHYSICAL_DISTRIBUTION_KINDS = {"repository", "plugin"}
PLANNER_DISTRIBUTION_PROFILES = {"repository", "plugin", "standalone-skill"}
ASSEMBLY_PROFILE_FIELDS = {
    "host_profile", "model_id", "model_revision", "distribution_profile",
    "physical_distribution_kind", "planner_distribution_profile",
    "distribution_evaluation_only", "distribution_manifest_sha256",
    "prompt_profile", "prompt_profile_source", "binding_id",
    "always_on_overlays", "catalogs",
}
PLUGIN_PACKAGE_CEILINGS = {
    "lite": {"max_files": 350, "max_bytes": 3_300_000},
    "pro": {"max_files": 400, "max_bytes": 3_800_000},
    "governed": {"max_files": 560, "max_bytes": 6_500_000},
}
MAX_DISTRIBUTION_SCAN_ENTRIES = 2048


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("context assembly dependency cannot be loaded: %s" % path)
    module = importlib.util.module_from_spec(spec)
    # SourceFileLoader writes ``__pycache__`` beside the runtime on Linux.
    # A governed distribution is a manifest-closed physical package, so that
    # otherwise harmless cache would mutate the package before identity checks.
    source = path.read_bytes()
    exec(compile(source, str(path), "exec", dont_inherit=True), module.__dict__)
    return module


context_resolver = _load_module(
    "context_assembly_context_resolver", ROOT / "scripts" / "context-resolver.py"
)
profile_resolver = _load_module(
    "context_assembly_profile_resolver", ROOT / "scripts" / "context-profile-resolver.py"
)


class ContextAssemblyError(ValueError):
    pass


def _canonical_json(value):
    try:
        return json.dumps(
            value, ensure_ascii=False, allow_nan=False, sort_keys=True,
            separators=(",", ":"),
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ContextAssemblyError("assembly cannot be encoded as canonical JSON: %s" % exc) from exc


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _builder_canonical_json(value):
    return (json.dumps(
        value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
    ) + "\n").encode("utf-8")


def _load_bundle_json(bundle_root, relative, label):
    try:
        raw = context_resolver.anchored_read(
            bundle_root, relative, MAX_DOCUMENT_BYTES, "bundle root"
        )
        value = context_resolver.strict_json_loads(raw.decode("utf-8"), label)
    except (UnicodeDecodeError, context_resolver.ContextResolutionError) as exc:
        raise ContextAssemblyError("cannot load %s: %s" % (label, exc)) from exc
    return value, raw


def _physical_distribution_files(root, manifest_raw, ceiling):
    """Inventory every package file with the same single-link rules as source reads."""
    if ceiling not in PLUGIN_PACKAGE_CEILINGS.values():
        raise ContextAssemblyError("distribution package ceiling is invalid")
    records = []
    scanned_entries = 0

    def visit(directory):
        nonlocal scanned_entries
        try:
            entries = sorted(os.scandir(directory), key=lambda item: item.name)
        except OSError as exc:
            raise ContextAssemblyError(
                "cannot inventory physical distribution: %s" % exc
            ) from exc
        for entry in entries:
            scanned_entries += 1
            if scanned_entries > MAX_DISTRIBUTION_SCAN_ENTRIES:
                raise ContextAssemblyError("physical distribution inventory is unbounded")
            path = Path(entry.path)
            relative = path.relative_to(root).as_posix()
            try:
                before = entry.stat(follow_symlinks=False)
            except OSError as exc:
                raise ContextAssemblyError(
                    "cannot inspect physical distribution path %s: %s" % (relative, exc)
                ) from exc
            if statmod.S_ISLNK(before.st_mode):
                raise ContextAssemblyError(
                    "physical distribution contains a symlink: %s" % relative
                )
            if statmod.S_ISDIR(before.st_mode):
                visit(path)
                continue
            if not statmod.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise ContextAssemblyError(
                    "physical distribution contains an unsafe file: %s" % relative
                )
            if relative == DISTRIBUTION_MANIFEST_REF:
                continue
            if len(records) + 2 > ceiling["max_files"]:
                raise ContextAssemblyError("physical distribution exceeds its file ceiling")
            descriptor = None
            try:
                descriptor = os.open(
                    path,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_NONBLOCK", 0),
                )
                opened = os.fstat(descriptor)
                if (
                        not statmod.S_ISREG(opened.st_mode)
                        or opened.st_nlink != 1
                        or (opened.st_dev, opened.st_ino, opened.st_mode)
                        != (before.st_dev, before.st_ino, before.st_mode)
                        or opened.st_size > MAX_DOCUMENT_BYTES):
                    raise ContextAssemblyError(
                        "physical distribution file is unsafe: %s" % relative
                    )
                raw = context_resolver._read_fd(descriptor, MAX_DOCUMENT_BYTES)
                repeated = context_resolver._read_fd(descriptor, MAX_DOCUMENT_BYTES)
                after = os.fstat(descriptor)
                current = path.lstat()
            except (OSError, context_resolver.ContextResolutionError) as exc:
                raise ContextAssemblyError(
                    "cannot verify physical distribution file %s: %s" % (relative, exc)
                ) from exc
            finally:
                if descriptor is not None:
                    os.close(descriptor)
            stable = ("st_dev", "st_ino", "st_mode", "st_nlink", "st_size",
                      "st_mtime_ns", "st_ctime_ns")
            if (
                    raw != repeated
                    or any(getattr(opened, field) != getattr(after, field)
                           for field in stable)
                    or any(getattr(after, field) != getattr(current, field)
                           for field in stable)):
                raise ContextAssemblyError(
                    "physical distribution changed during inventory: %s" % relative
                )
            records.append({
                "bytes": len(raw),
                "mode": "%04o" % statmod.S_IMODE(after.st_mode),
                "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
            })
    visit(root)
    total_bytes = sum(item["bytes"] for item in records) + len(manifest_raw)
    if total_bytes > ceiling["max_bytes"]:
        raise ContextAssemblyError("physical distribution exceeds its byte ceiling")
    try:
        current_manifest = context_resolver.anchored_read(
            root, DISTRIBUTION_MANIFEST_REF, MAX_DOCUMENT_BYTES, "bundle root"
        )
    except context_resolver.ContextResolutionError as exc:
        raise ContextAssemblyError(
            "cannot reverify physical distribution manifest: %s" % exc
        ) from exc
    if current_manifest != manifest_raw:
        raise ContextAssemblyError(
            "physical distribution manifest changed during inventory"
        )
    return records


def _verify_distribution_host_binding(root, manifest, by_path):
    """Bind the manifest host label to the typed catalog and its physical sidecar."""
    try:
        host_catalog, _host_raw = profile_resolver.load_host_catalog(root)
    except profile_resolver.ContextProfileError as exc:
        raise ContextAssemblyError(
            "cannot verify distribution host catalog: %s" % exc
        ) from exc
    host_name = manifest["host_profile"]
    expected = host_catalog["profiles"].get(host_name)
    if expected is None or "plugin" not in expected["compatible_distributions"]:
        raise ContextAssemblyError("distribution host is not plugin-compatible")
    definition = {"profile": host_name, **expected}
    catalog_sha = hashlib.sha256(_builder_canonical_json(host_catalog)).hexdigest()
    definition_sha = hashlib.sha256(_builder_canonical_json(definition)).hexdigest()
    if (
            manifest["host_capabilities"] != expected["capabilities"]
            or manifest["host_profile_catalog_sha256"] != catalog_sha
            or manifest["host_profile_definition_sha256"] != definition_sha
            or manifest["routing_surface"] != expected["routing_surface"]
            or manifest["reference_surface"] != expected["reference_surface"]
            or manifest["connector_surface"] != expected["connector_surface"]):
        raise ContextAssemblyError(
            "distribution host identity differs from the typed host catalog"
        )

    sidecar_record = manifest["routing_sidecar"]
    if expected["routing_surface"] == "router-skills":
        descriptor = by_path.get(ROUTER_FACADE_SIDECAR_REF)
        if descriptor is None:
            raise ContextAssemblyError("generic host distribution omits its router sidecar")
        try:
            raw = context_resolver.anchored_read(
                root, ROUTER_FACADE_SIDECAR_REF, MAX_DOCUMENT_BYTES, "bundle root"
            )
            sidecar = context_resolver.strict_json_loads(
                raw.decode("utf-8"), "router facade sidecar"
            )
        except (UnicodeDecodeError, context_resolver.ContextResolutionError) as exc:
            raise ContextAssemblyError(
                "generic host router sidecar is invalid: %s" % exc
            ) from exc
        expected_record = {
            "path": ROUTER_FACADE_SIDECAR_REF,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "facade_count": 8,
            "canonical_business_skill_count": 120,
        }
        if (
                sidecar_record != expected_record
                or descriptor["sha256"] != expected_record["sha256"]
                or sidecar.get("kind") != "router-facade-sidecar"
                or sidecar.get("host_profile") != host_name
                or sidecar.get("host_profile_sha256") != definition_sha
                or sidecar.get("routing_surface") != expected["routing_surface"]
                or sidecar.get("reference_surface") != expected["reference_surface"]
                or sidecar.get("connector_surface") != expected["connector_surface"]
                or sidecar.get("facade_count") != 8
                or sidecar.get("canonical_business_skill_count") != 120):
            raise ContextAssemblyError(
                "generic host router sidecar is not bound to its manifest"
            )
    elif sidecar_record is not None or any(
            path.startswith("router-facades/") for path in by_path):
        raise ContextAssemblyError(
            "non-router host distribution cannot carry router facade artifacts"
        )


def _distribution_identity(bundle_root, requested_host_profile):
    """Return a physical package identity, never a caller-supplied authority.

    A repository checkout has no distribution manifest and therefore receives
    the non-package identity ``repository``.  A built plugin must carry the
    current 1.2 manifest, bind the requested host profile, and hash-anchor the
    runtime files that can authorize compact prompt-profile selection.
    """
    root = profile_resolver._normalized_root(bundle_root)
    try:
        manifest_raw = context_resolver.anchored_read(
            root, DISTRIBUTION_MANIFEST_REF, MAX_DOCUMENT_BYTES, "bundle root"
        )
    except context_resolver.ContextSourceMissing:
        return {
            "kind": "repository",
            "profile": "repository",
            "host_profile": None,
            "manifest_sha256": None,
        }
    try:
        manifest = context_resolver.strict_json_loads(
            manifest_raw.decode("utf-8"), "distribution manifest"
        )
    except (UnicodeDecodeError, context_resolver.ContextResolutionError) as exc:
        raise ContextAssemblyError("distribution manifest is invalid: %s" % exc) from exc
    required = {
        "schema_version", "kind", "profile", "capability_ceiling", "capabilities",
        "catalog_sha256", "profile_definition_sha256", "host_profile",
        "host_capabilities", "host_profile_catalog_sha256",
        "host_profile_definition_sha256", "routing_surface", "reference_surface",
        "connector_surface", "routing_sidecar", "package_ceiling", "hash_algorithm",
        "manifest_path", "manifest_excludes", "source", "files_sha256", "files",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ContextAssemblyError("distribution manifest has unknown or missing fields")
    profile = manifest["profile"]
    kind = manifest["kind"]
    manifest_host = manifest["host_profile"]
    if kind == "standalone-skill":
        raise ContextAssemblyError(
            "physical standalone packages do not carry the trusted assembly runtime; "
            "use the explicit non-deployable repository projection"
        )
    if (
            manifest["schema_version"] != "1.2"
            or kind != "plugin"
            or profile not in {"lite", "pro", "governed"}
            or manifest["capability_ceiling"] != profile
            or manifest["package_ceiling"] != PLUGIN_PACKAGE_CEILINGS.get(profile)
            or manifest["hash_algorithm"] != "sha256"
            or manifest["manifest_path"] != DISTRIBUTION_MANIFEST_REF
            or manifest["manifest_excludes"] != [DISTRIBUTION_MANIFEST_REF]
            or manifest_host not in SHARED_HOST_PROFILES
            or (requested_host_profile not in {None, "auto"}
                and manifest_host != requested_host_profile)):
        raise ContextAssemblyError("distribution manifest identity does not authorize this host")
    files = manifest["files"]
    if not isinstance(files, list) or not files:
        raise ContextAssemblyError("distribution manifest file inventory is invalid")
    by_path = {}
    for offset, item in enumerate(files):
        if (
                not isinstance(item, dict)
                or set(item) != {"bytes", "mode", "path", "sha256"}
                or not isinstance(item["path"], str)
                or item["path"] in by_path
                or not isinstance(item["mode"], str)
                or not re.fullmatch(r"0[0-7]{3}", item["mode"])
                or isinstance(item["bytes"], bool)
                or not isinstance(item["bytes"], int)
                or item["bytes"] < 0
                or not isinstance(item["sha256"], str)
                or not profile_resolver.SHA256.fullmatch(item["sha256"])):
            raise ContextAssemblyError(
                "distribution manifest file descriptor %d is invalid" % offset
            )
        by_path[item["path"]] = item
    inventory_hash = hashlib.sha256(
        (json.dumps(
            files, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
        ) + "\n").encode("utf-8")
    ).hexdigest()
    if manifest["files_sha256"] != inventory_hash:
        raise ContextAssemblyError("distribution manifest inventory hash is invalid")
    actual_files = _physical_distribution_files(
        root, manifest_raw, manifest["package_ceiling"]
    )
    if files != actual_files:
        raise ContextAssemblyError(
            "physical distribution files do not match the complete manifest inventory"
        )
    _verify_distribution_host_binding(root, manifest, by_path)
    for relative in TRUSTED_DISTRIBUTION_FILES:
        descriptor = by_path.get(relative)
        if descriptor is None:
            raise ContextAssemblyError(
                "distribution manifest omits compact-profile runtime %s" % relative
            )
        try:
            raw = context_resolver.anchored_read(
                root, relative, MAX_DOCUMENT_BYTES, "bundle root"
            )
        except context_resolver.ContextResolutionError as exc:
            raise ContextAssemblyError(
                "cannot verify compact-profile runtime %s: %s" % (relative, exc)
            ) from exc
        if (
                descriptor["bytes"] != len(raw)
                or descriptor["sha256"] != hashlib.sha256(raw).hexdigest()):
            raise ContextAssemblyError(
                "compact-profile runtime differs from distribution manifest: %s" % relative
            )
        if relative in TRUSTED_EXECUTED_RUNTIME_FILES:
            try:
                executing_raw = (ROOT / relative).read_bytes()
            except OSError as exc:
                raise ContextAssemblyError(
                    "cannot verify executing assembly runtime %s: %s" % (relative, exc)
                ) from exc
            if raw != executing_raw:
                raise ContextAssemblyError(
                    "physical distribution runtime differs from the executing runtime: %s"
                    % relative
                )
    return {
        "kind": kind,
        "profile": profile,
        "host_profile": manifest_host,
        "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
    }


def _normal_distribution_matrix(physical_kind, resolved_host, planner_profile):
    if physical_kind == "repository":
        return resolved_host in SHARED_HOST_PROFILES and planner_profile == "repository"
    if physical_kind == "plugin":
        return resolved_host in SHARED_HOST_PROFILES and planner_profile == "plugin"
    return False


def _validate_evaluation_run_id(value):
    if not isinstance(value, str) or not profile_resolver.SAFE_ID.fullmatch(value):
        raise ContextAssemblyError(
            "evaluation_run_id must be a safe non-empty identifier"
        )


def _selected_modules(module_catalog, host_profile, prompt_profile):
    active = {consumer: [] for consumer in profile_resolver.CONSUMER_ORDER}
    fallback = []
    for module in module_catalog["modules"]:
        if (
                host_profile not in module["host_profiles"]
                or prompt_profile not in module["prompt_profiles"]):
            continue
        projection = {
            "module_id": module["module_id"],
            "load_policy": module["load_policy"],
            "source_role": module["source_role"],
            "materialization": module["materialization"],
            "condition_code": module["condition_code"],
        }
        if module["load_policy"] == "fallback":
            fallback.append(projection)
        else:
            active[module["consumer"]].append(projection)
    return active, fallback


def _evaluation_resolution(
        *, bundle_root, host_profile, model_id, model_revision, prompt_profile, as_of,
        evaluation_run_id):
    if (
            not isinstance(evaluation_run_id, str)
            or not profile_resolver.SAFE_ID.fullmatch(evaluation_run_id)):
        raise ContextAssemblyError("evaluation_run_id must be a safe non-empty identifier")
    if prompt_profile not in {"balanced", "lean"}:
        raise ContextAssemblyError("evaluation profile must be balanced or lean")
    try:
        root = profile_resolver._normalized_root(bundle_root)
        host_catalog, host_raw = profile_resolver.load_host_catalog(root)
        prompt_catalog, prompt_raw = profile_resolver.load_prompt_catalog(root, host_catalog)
        module_catalog, module_raw = profile_resolver.load_context_module_catalog(
            root, host_catalog, prompt_catalog
        )
        profile_resolver._parse_datetime(as_of, "as_of")
    except profile_resolver.ContextProfileError as exc:
        raise ContextAssemblyError(str(exc)) from exc
    if host_profile not in host_catalog["profiles"]:
        raise ContextAssemblyError("evaluation host profile is unknown: %s" % host_profile)
    if not isinstance(model_id, str) or not profile_resolver.SAFE_ID.fullmatch(model_id):
        raise ContextAssemblyError("evaluation model_id is invalid")
    active, fallback = _selected_modules(module_catalog, host_profile, prompt_profile)
    model_ids = {item["module_id"] for item in active["model"]}
    skill_representations = model_ids & {
        "model-skill-explicit", "model-skill-balanced-full", "model-skill-capsule"
    }
    policy_representations = model_ids & {
        "model-policy-explicit", "model-policy-kernel"
    }
    expected_representations = {
        "balanced": ({"model-skill-balanced-full"}, {"model-policy-kernel"}),
        "lean": ({"model-skill-capsule"}, {"model-policy-kernel"}),
    }[prompt_profile]
    if (skill_representations, policy_representations) != expected_representations:
        raise ContextAssemblyError(
            "evaluation profile has no exact model representation for host=%s profile=%s"
            % (host_profile, prompt_profile)
        )
    host = host_catalog["profiles"][host_profile]
    prompt = prompt_catalog["profiles"][prompt_profile]
    return {
        "schema_version": "1.0",
        "as_of": as_of,
        "host_profile": host_profile,
        "host_profile_source": "evaluation-explicit",
        "model_id": model_id,
        "model_revision": model_revision,
        "distribution_profile": "repository",
        "prompt_profile": prompt_profile,
        "prompt_profile_source": "evaluation-only-uncertified",
        "binding_id": None,
        "capabilities": list(host["capabilities"]),
        "compatible_distributions": list(host["compatible_distributions"]),
        "routing_surface": host["routing_surface"],
        "reference_surface": host["reference_surface"],
        "connector_surface": host["connector_surface"],
        "always_on_overlays": list(profile_resolver.ALWAYS_ON_OVERLAYS),
        "reducible_settings": {
            "workflow_detail": prompt["workflow_detail"],
            "example_budget": prompt["example_budget"],
            "template_detail": prompt["template_detail"],
            "rationale_detail": prompt["rationale_detail"],
            "reminder_density": prompt["reminder_density"],
        },
        "context_modules": active,
        "fallback_modules": fallback,
        "catalogs": {
            "host_sha256": _sha256(host_raw),
            "prompt_sha256": _sha256(prompt_raw),
            "context_modules_sha256": _sha256(module_raw),
        },
        "evaluation_run_id": evaluation_run_id,
    }


def _module_index(resolution):
    result = {}
    for consumer, modules in resolution["context_modules"].items():
        for module in modules:
            module_id = module["module_id"]
            if module_id in result:
                raise ContextAssemblyError("duplicate active context module: %s" % module_id)
            result[module_id] = (consumer, module)
    return result


def _require_module(modules, module_id, consumer=None):
    try:
        actual_consumer, module = modules[module_id]
    except KeyError as exc:
        raise ContextAssemblyError("required context module is inactive: %s" % module_id) from exc
    if consumer is not None and actual_consumer != consumer:
        raise ContextAssemblyError(
            "context module %s has consumer %s, expected %s"
            % (module_id, actual_consumer, consumer)
        )
    return module


def _project_manifest_resource(resource, module, *, materialization=None):
    materialization = materialization or module["materialization"]
    return {
        "resource_id": resource["resource_id"],
        "scope": resource["scope"],
        "path": resource["path"],
        "sha256": resource["sha256"],
        "bytes": resource["bytes"],
        "body_bytes": resource["bytes"] if materialization == "body" else 0,
        "role": resource["role"],
        "module_id": module["module_id"],
        "materialization": materialization,
        "load_policy": module["load_policy"],
        "source_resource_id": resource["resource_id"],
    }


def _generated_resource(relative, raw, role, module, source_resource_id):
    digest = _sha256(raw)
    return {
        "resource_id": "g.%s" % hashlib.sha256(relative.encode("utf-8")).hexdigest()[:24],
        "scope": "bundle",
        "path": relative,
        "sha256": digest,
        "bytes": len(raw),
        "body_bytes": len(raw) if module["materialization"] == "body" else 0,
        "role": role,
        "module_id": module["module_id"],
        "materialization": module["materialization"],
        "load_policy": module["load_policy"],
        "source_resource_id": source_resource_id,
    }


def _load_compact_index(bundle_root):
    index, index_raw = _load_bundle_json(
        bundle_root, CAPSULE_INDEX_REF, "skill capsule index"
    )
    if (
            not isinstance(index, dict) or index.get("schema_version") != "1.0"
            or index.get("capsule_count") != 120
            or not isinstance(index.get("capsules"), list)
            or len(index["capsules"]) != 120):
        raise ContextAssemblyError("skill capsule index identity/count is unsupported")
    kernel_ref = index.get("policy_kernel")
    if not isinstance(kernel_ref, dict) or set(kernel_ref) != {"path", "sha256"}:
        raise ContextAssemblyError("skill capsule index policy kernel reference is invalid")
    try:
        kernel_raw = context_resolver.anchored_read(
            bundle_root, kernel_ref["path"], MAX_DOCUMENT_BYTES, "bundle root"
        )
    except context_resolver.ContextResolutionError as exc:
        raise ContextAssemblyError("cannot read policy kernel: %s" % exc) from exc
    if _sha256(kernel_raw) != kernel_ref["sha256"]:
        raise ContextAssemblyError("policy kernel hash differs from capsule index")
    contract_index_ref = index.get("source_contract_index")
    if not isinstance(contract_index_ref, dict) or set(contract_index_ref) != {
            "path", "sha256"}:
        raise ContextAssemblyError("capsule source contract index reference is invalid")
    contract_index, source_index_raw = _load_bundle_json(
        bundle_root, contract_index_ref["path"], "capsule source contract index"
    )
    if _sha256(source_index_raw) != contract_index_ref["sha256"]:
        raise ContextAssemblyError("capsule source contract index hash differs")
    if (
            not isinstance(contract_index, dict)
            or contract_index.get("contract_count") != 120
            or not isinstance(contract_index.get("contracts"), list)
            or len(contract_index["contracts"]) != 120):
        raise ContextAssemblyError("capsule source contract index identity/count is invalid")
    return index, index_raw, kernel_ref, kernel_raw, contract_index


def _load_capsule(bundle_root, skill, manifest):
    index, index_raw, kernel_ref, kernel_raw, contract_index = _load_compact_index(
        bundle_root
    )
    matches = [item for item in index["capsules"] if item.get("skill") == skill]
    if len(matches) != 1:
        raise ContextAssemblyError("skill capsule index has no unique entry for %s" % skill)
    entry = matches[0]
    if entry.get("capsule_ref") != "references/skill-capsules/%s.json" % skill:
        raise ContextAssemblyError("skill capsule path differs from its target identity")
    capsule, capsule_raw = _load_bundle_json(
        bundle_root, entry["capsule_ref"], "skill capsule"
    )
    if _sha256(capsule_raw) != entry.get("capsule_sha256"):
        raise ContextAssemblyError("skill capsule hash differs from index")
    contracts = [
        item for item in contract_index["contracts"]
        if isinstance(item, dict) and item.get("skill") == skill
    ]
    if len(contracts) != 1:
        raise ContextAssemblyError("capsule source index has no unique contract for %s" % skill)
    source = capsule.get("provenance", {}).get("source")
    machine = capsule.get("provenance", {}).get("machine_contract")
    if (
            capsule.get("capsule_id") != "skill-capsule:" + skill
            or not isinstance(source, dict)
            or source.get("sha256") != manifest["route"]["skill_sha256"]
            or machine != {
                "path": contracts[0].get("contract_ref"),
                "sha256": contracts[0].get("contract_sha256"),
            }
            or capsule.get("policy", {}).get("kernel") != kernel_ref):
        raise ContextAssemblyError("skill capsule is stale for the manifest target")
    return entry, capsule_raw, kernel_ref, kernel_raw, index_raw


def build_assembly(
        manifest, *, bundle_root=ROOT, project_root=None, host_profile,
        model_id="unknown", model_revision=None, requested_prompt_profile=None, as_of=None,
        evaluation_prompt_profile=None, evaluation_run_id=None, verify_sources=True,
        distribution_evaluation_only=False):
    """Return consumer-separated metadata; never concatenate or copy source bodies."""
    if not isinstance(distribution_evaluation_only, bool):
        raise ContextAssemblyError("distribution_evaluation_only must be boolean")
    try:
        context_resolver.validate_manifest(manifest)
        if "planner" not in manifest["request"]:
            raise ContextAssemblyError(
                "assembly requires planner distribution provenance"
            )
        if project_root is None:
            raise ContextAssemblyError(
                "project_root is required to verify planner candidate closure"
            )
        if verify_sources:
            # verify_manifest_sources re-enters resolve_context, whose first
            # source-bearing step proves the exact planner candidate closure.
            context_resolver.verify_manifest_sources(manifest, bundle_root, project_root)
        else:
            # Skipping the full replay never skips planner closure validation.
            context_resolver.validate_planner_candidate_closure(
                manifest["request"], bundle_root, project_root
            )
    except context_resolver.ContextResolutionError as exc:
        raise ContextAssemblyError("context manifest is not verified: %s" % exc) from exc
    if as_of is None:
        as_of = manifest["as_of"]
    distribution = _distribution_identity(bundle_root, host_profile)
    planner_profile = manifest["request"]["planner"]["distribution_profile"]
    if distribution_evaluation_only:
        if evaluation_prompt_profile is not None:
            raise ContextAssemblyError(
                "distribution evaluation cannot authorize a compact prompt profile"
            )
        if requested_prompt_profile not in {None, "explicit"}:
            raise ContextAssemblyError(
                "distribution evaluation requires the explicit prompt profile"
            )
        _validate_evaluation_run_id(evaluation_run_id)
    if evaluation_prompt_profile is not None:
        if requested_prompt_profile is not None:
            raise ContextAssemblyError(
                "deployment prompt profile and evaluation prompt profile are mutually exclusive"
            )
        resolution = _evaluation_resolution(
            bundle_root=bundle_root,
            host_profile=host_profile,
            model_id=model_id,
            model_revision=model_revision,
            prompt_profile=evaluation_prompt_profile,
            as_of=as_of,
            evaluation_run_id=evaluation_run_id,
        )
        deployment_eligible = False
    else:
        if evaluation_run_id is not None and not distribution_evaluation_only:
            raise ContextAssemblyError(
                "evaluation_run_id is allowed only with evaluation_prompt_profile"
            )
        try:
            resolution = profile_resolver.resolve_context_profile(
                bundle_root=bundle_root,
                host_profile=host_profile,
                model_id=model_id,
                model_revision=model_revision,
                requested_prompt_profile=(
                    "explicit" if distribution_evaluation_only
                    else requested_prompt_profile
                ),
                as_of=as_of,
                distribution_profile=distribution["profile"],
            )
        except profile_resolver.ContextProfileError as exc:
            raise ContextAssemblyError(str(exc)) from exc
        deployment_eligible = not distribution_evaluation_only
    resolved_host = resolution["host_profile"]
    if (
            distribution["host_profile"] is not None
            and distribution["host_profile"] != resolved_host):
        raise ContextAssemblyError(
            "resolved host differs from the physical distribution manifest"
        )
    normal_distribution = _normal_distribution_matrix(
        distribution["kind"], resolved_host, planner_profile
    )
    projection_distribution = (
        distribution["kind"] == "repository"
        and resolved_host == "standalone-skill-host"
        and planner_profile == "standalone-skill"
    )
    if distribution_evaluation_only:
        if not projection_distribution:
            raise ContextAssemblyError(
                "distribution evaluation identity is not the repository standalone projection"
            )
        if (
                resolution["prompt_profile"] != "explicit"
                or resolution["binding_id"] is not None):
            raise ContextAssemblyError(
                "distribution evaluation must use unbound explicit context"
            )
        resolution = dict(resolution)
        resolution["prompt_profile_source"] = (
            "evaluation-only-distribution-projection"
        )
        deployment_eligible = False
    elif not normal_distribution:
        raise ContextAssemblyError(
            "planner distribution profile does not match physical distribution and resolved host"
        )
    prompt_profile = resolution["prompt_profile"]
    modules = _module_index(resolution)
    standalone_host = resolution["host_profile"] == "standalone-skill-host"
    consumers = {"controller": [], "model": [], "tool": [], "deferred": []}
    replacements = []
    source_skill = None
    source_policy = None
    common_model_bytes = 0

    for resource in sorted(
            manifest["resources"], key=lambda item: (item["scope"], item["path"], item["resource_id"])):
        role = resource["role"]
        if role == "skill-definition":
            source_skill = resource
            controller = _require_module(modules, "controller-skill-identity", "controller")
            consumers["controller"].append(_project_manifest_resource(resource, controller))
            if prompt_profile == "explicit":
                model = _require_module(modules, "model-skill-explicit", "model")
                consumers["model"].append(_project_manifest_resource(resource, model))
                if standalone_host:
                    # The standalone SKILL.md embeds the non-reducible policy.
                    # Require that host-specific policy representation, but do
                    # not project the same source body a second time.
                    _require_module(
                        modules, "model-policy-standalone-embedded", "model"
                    )
            elif prompt_profile == "balanced":
                model = _require_module(
                    modules, "model-skill-balanced-full", "model"
                )
                consumers["model"].append(_project_manifest_resource(resource, model))
        elif role == "skill-contract":
            if "controller-machine-contract" in modules:
                controller = _require_module(
                    modules, "controller-machine-contract", "controller"
                )
                consumers["controller"].append(
                    _project_manifest_resource(resource, controller)
                )
            elif not standalone_host:
                raise ContextAssemblyError(
                    "selected machine contract has no active controller module"
                )
        elif role == "shared-contract":
            source_policy = resource
            if "controller-shared-contract" in modules:
                controller = _require_module(
                    modules, "controller-shared-contract", "controller"
                )
                consumers["controller"].append(
                    _project_manifest_resource(resource, controller)
                )
            elif not standalone_host:
                raise ContextAssemblyError(
                    "selected shared contract has no active controller module"
                )
            if prompt_profile == "explicit" and not standalone_host:
                model = _require_module(modules, "model-policy-explicit", "model")
                consumers["model"].append(_project_manifest_resource(resource, model))
        elif role == "routing-scenario":
            model = _require_module(modules, "model-routing-shard", "model")
            projected = _project_manifest_resource(resource, model)
            consumers["model"].append(projected)
            common_model_bytes += projected["body_bytes"]
        elif role in {"working-memory", "skill-read"}:
            model = _require_module(modules, "model-project-evidence", "model")
            projected = _project_manifest_resource(resource, model)
            consumers["model"].append(projected)
            common_model_bytes += projected["body_bytes"]
        elif role == "skill-reference":
            if resource["reason_code"] == "explicit-runtime-read" or resource[
                    "requirement"] == "required":
                model = _require_module(modules, "model-runtime-read", "model")
                projected = _project_manifest_resource(resource, model)
                consumers["model"].append(projected)
                common_model_bytes += projected["body_bytes"]
            elif resource["path"] == "CONNECTORS.md":
                if "tool-connector-catalog" in modules:
                    tool = _require_module(modules, "tool-connector-catalog", "tool")
                    consumers["deferred"].append(
                        _project_manifest_resource(resource, tool)
                    )
                elif not standalone_host:
                    raise ContextAssemblyError(
                        "connector catalog has no active tool module"
                    )
            elif resource["path"].startswith("scripts/connectors/"):
                if "tool-connector-implementation" in modules:
                    tool = _require_module(
                        modules, "tool-connector-implementation", "tool"
                    )
                    consumers["deferred"].append(
                        _project_manifest_resource(resource, tool)
                    )
                elif not standalone_host:
                    raise ContextAssemblyError(
                        "connector implementation has no active tool module"
                    )
            else:
                model = _require_module(modules, "model-authored-reference", "model")
                consumers["deferred"].append(_project_manifest_resource(resource, model))
        else:
            raise ContextAssemblyError("unsupported selected manifest role: %s" % role)
    if source_skill is None or (source_policy is None and not standalone_host):
        raise ContextAssemblyError("manifest lacks selected skill/shared policy resources")

    if prompt_profile == "balanced":
        unused_index, unused_raw, kernel_ref, kernel_raw, unused_contracts = (
            _load_compact_index(bundle_root)
        )
        kernel_module = _require_module(modules, "model-policy-kernel", "model")
        kernel_model = _generated_resource(
            kernel_ref["path"], kernel_raw, "policy-kernel", kernel_module,
            source_policy["resource_id"],
        )
        consumers["model"].append(kernel_model)
        replacements.append({
            "source_resource_id": source_policy["resource_id"],
            "replacement_resource_ids": [kernel_model["resource_id"]],
            "reason_code": "certified-policy-kernel",
        })
    elif prompt_profile == "lean":
        entry, capsule_raw, kernel_ref, kernel_raw, unused = _load_capsule(
            bundle_root, manifest["route"]["target_skill"], manifest
        )
        capsule_module = _require_module(modules, "model-skill-capsule", "model")
        kernel_module = _require_module(modules, "model-policy-kernel", "model")
        controller_capsule = _require_module(
            modules, "controller-capsule-provenance", "controller"
        )
        capsule_model = _generated_resource(
            entry["capsule_ref"], capsule_raw, "skill-capsule", capsule_module,
            source_skill["resource_id"],
        )
        capsule_control = _generated_resource(
            entry["capsule_ref"], capsule_raw, "skill-capsule", controller_capsule,
            source_skill["resource_id"],
        )
        kernel_model = _generated_resource(
            kernel_ref["path"], kernel_raw, "policy-kernel", kernel_module,
            source_policy["resource_id"],
        )
        consumers["model"].extend([capsule_model, kernel_model])
        consumers["controller"].append(capsule_control)
        replacements.extend([
            {
                "source_resource_id": source_skill["resource_id"],
                "replacement_resource_ids": [capsule_model["resource_id"]],
                "reason_code": "certified-skill-capsule",
            },
            {
                "source_resource_id": source_policy["resource_id"],
                "replacement_resource_ids": [kernel_model["resource_id"]],
                "reason_code": "certified-policy-kernel",
            },
        ])

    for consumer in consumers:
        consumers[consumer].sort(key=lambda item: (item["path"], item["resource_id"]))
        ids = [item["resource_id"] for item in consumers[consumer]]
        if len(ids) != len(set(ids)):
            raise ContextAssemblyError("duplicate projected resource in %s context" % consumer)
    model_bytes = sum(item["body_bytes"] for item in consumers["model"])
    explicit_baseline = common_model_bytes + source_skill["bytes"]
    if not standalone_host:
        explicit_baseline += source_policy["bytes"]
    reduction = max(0, explicit_baseline - model_bytes)
    ratio = 0 if explicit_baseline == 0 else round(reduction / explicit_baseline, 6)
    result = {
        "$schema": "./context-assembly.schema.json",
        "schema_version": "1.0",
        "kind": "consumer-separated-context-assembly",
        "context_signature": manifest["context_signature"],
        "route": {
            "command": manifest["route"]["command"],
            "target_skill": manifest["route"]["target_skill"],
        },
        "profile": {
            "host_profile": resolution["host_profile"],
            "model_id": resolution["model_id"],
            "model_revision": resolution["model_revision"],
            "distribution_profile": distribution["profile"],
            "physical_distribution_kind": distribution["kind"],
            "planner_distribution_profile": planner_profile,
            "distribution_evaluation_only": distribution_evaluation_only,
            "distribution_manifest_sha256": distribution["manifest_sha256"],
            "prompt_profile": prompt_profile,
            "prompt_profile_source": resolution["prompt_profile_source"],
            "binding_id": resolution["binding_id"],
            "always_on_overlays": resolution["always_on_overlays"],
            "catalogs": resolution["catalogs"],
        },
        "deployment_eligible": deployment_eligible,
        "evaluation_run_id": evaluation_run_id,
        "consumers": consumers,
        "replacements": sorted(replacements, key=lambda item: item["source_resource_id"]),
        "usage": {
            "manifest_selected_bytes": manifest["budget"]["selected_bytes"],
            "controller_body_bytes": sum(
                item["body_bytes"] for item in consumers["controller"]
            ),
            "model_body_bytes": model_bytes,
            "tool_body_bytes": sum(item["body_bytes"] for item in consumers["tool"]),
            "deferred_bytes": sum(item["bytes"] for item in consumers["deferred"]),
            "model_reduction_bytes": reduction,
            "model_reduction_ratio": ratio,
        },
        "assembly_signature": "",
    }
    signature_payload = dict(result)
    signature_payload.pop("assembly_signature")
    result["assembly_signature"] = _sha256(
        _canonical_json(signature_payload).encode("utf-8")
    )
    validate_assembly(result)
    return result


def validate_assembly(value):
    required = {
        "$schema", "schema_version", "kind", "context_signature", "route", "profile",
        "deployment_eligible", "evaluation_run_id", "consumers", "replacements", "usage",
        "assembly_signature",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise ContextAssemblyError("context assembly has unknown or missing fields")
    if (
            value["$schema"] != "./context-assembly.schema.json"
            or value["schema_version"] != "1.0"
            or value["kind"] != "consumer-separated-context-assembly"):
        raise ContextAssemblyError("context assembly identity is invalid")
    for field in ("context_signature", "assembly_signature"):
        digest = value[field]
        if not isinstance(digest, str) or not profile_resolver.SHA256.fullmatch(digest):
            raise ContextAssemblyError("context assembly %s is invalid" % field)
    profile = value["profile"]
    if not isinstance(profile, dict) or set(profile) != ASSEMBLY_PROFILE_FIELDS:
        raise ContextAssemblyError("context assembly profile has unknown or missing fields")
    physical_kind = profile["physical_distribution_kind"]
    planner_profile = profile["planner_distribution_profile"]
    host_profile = profile["host_profile"]
    evaluation_only = profile["distribution_evaluation_only"]
    if physical_kind not in PHYSICAL_DISTRIBUTION_KINDS:
        raise ContextAssemblyError("physical distribution kind is invalid")
    if planner_profile not in PLANNER_DISTRIBUTION_PROFILES:
        raise ContextAssemblyError("planner distribution profile is invalid")
    if host_profile not in SHARED_HOST_PROFILES | {"standalone-skill-host"}:
        raise ContextAssemblyError("resolved host profile is invalid")
    if not isinstance(evaluation_only, bool):
        raise ContextAssemblyError("distribution_evaluation_only must be boolean")
    physical_profile = profile["distribution_profile"]
    manifest_digest = profile["distribution_manifest_sha256"]
    if physical_kind == "repository":
        if physical_profile != "repository" or manifest_digest is not None:
            raise ContextAssemblyError(
                "repository physical distribution_profile/"
                "distribution_manifest_sha256 identity is inconsistent"
            )
    else:
        if (
                physical_profile not in {"lite", "pro", "governed"}
                or not isinstance(manifest_digest, str)
                or not profile_resolver.SHA256.fullmatch(manifest_digest)
        ):
            raise ContextAssemblyError(
                "built physical distribution identity is inconsistent"
            )
    normal_distribution = _normal_distribution_matrix(
        physical_kind, host_profile, planner_profile
    )
    projection_distribution = (
        physical_kind == "repository"
        and host_profile == "standalone-skill-host"
        and planner_profile == "standalone-skill"
    )
    if evaluation_only:
        if (
                not projection_distribution
                or value["deployment_eligible"] is not False
                or profile["prompt_profile"] != "explicit"
                or profile["prompt_profile_source"]
                != "evaluation-only-distribution-projection"
                or profile["binding_id"] is not None):
            raise ContextAssemblyError(
                "repository standalone projection must remain explicit evaluation-only"
            )
    elif not normal_distribution:
        raise ContextAssemblyError(
            "assembly distribution matrix is inconsistent"
        )
    if set(value["consumers"]) != {"controller", "model", "tool", "deferred"}:
        raise ContextAssemblyError("context assembly consumers are invalid")
    for consumer, resources in value["consumers"].items():
        if not isinstance(resources, list) or len(resources) > 256:
            raise ContextAssemblyError("context assembly %s resources are invalid" % consumer)
        for resource in resources:
            if resource["materialization"] == "body":
                if resource["body_bytes"] != resource["bytes"]:
                    raise ContextAssemblyError("body resource byte accounting is invalid")
            elif resource["body_bytes"] != 0:
                raise ContextAssemblyError("non-body resource cannot count model bytes")
    if value["deployment_eligible"]:
        if value["evaluation_run_id"] is not None:
            raise ContextAssemblyError("deployment assembly cannot carry evaluation_run_id")
        if value["profile"]["prompt_profile_source"] in {
                "evaluation-only-uncertified",
                "evaluation-only-distribution-projection",
        }:
            raise ContextAssemblyError("evaluation-only profile cannot be deployment eligible")
    else:
        _validate_evaluation_run_id(value["evaluation_run_id"])
        expected_source = (
            "evaluation-only-distribution-projection"
            if evaluation_only else "evaluation-only-uncertified"
        )
        if value["profile"]["prompt_profile_source"] != expected_source:
            raise ContextAssemblyError(
                "evaluation assembly must remain explicitly non-deployable"
            )
    signature = value["assembly_signature"]
    payload = dict(value)
    payload.pop("assembly_signature")
    if signature != _sha256(_canonical_json(payload).encode("utf-8")):
        raise ContextAssemblyError(
            "assembly_signature SHA-256 does not match assembly semantics"
        )
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--bundle-root", default=str(ROOT))
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--host-profile", required=True)
    parser.add_argument("--model-id", default="unknown")
    parser.add_argument("--model-revision")
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument("--prompt-profile", choices=profile_resolver.PROMPT_PROFILE_ORDER)
    profile.add_argument(
        "--evaluation-prompt-profile", choices=("balanced", "lean")
    )
    parser.add_argument("--evaluation-run-id")
    parser.add_argument(
        "--distribution-evaluation-only", action="store_true",
        help="allow only an explicit non-deployable repository standalone projection",
    )
    parser.add_argument("--as-of")
    args = parser.parse_args(argv)
    try:
        manifest = context_resolver.read_json_document(
            args.manifest, "context manifest", context_resolver.MAX_MANIFEST_BYTES
        )
        result = build_assembly(
            manifest,
            bundle_root=args.bundle_root,
            project_root=args.project_root,
            host_profile=args.host_profile,
            model_id=args.model_id,
            model_revision=args.model_revision,
            requested_prompt_profile=args.prompt_profile,
            as_of=args.as_of,
            evaluation_prompt_profile=args.evaluation_prompt_profile,
            evaluation_run_id=args.evaluation_run_id,
            distribution_evaluation_only=args.distribution_evaluation_only,
            verify_sources=True,
        )
    except (ContextAssemblyError, OSError) as exc:
        print("context assembly failed: %s" % exc, file=sys.stderr)
        return 2
    print(_canonical_json(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
