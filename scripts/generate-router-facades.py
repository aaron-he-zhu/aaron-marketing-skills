#!/usr/bin/env python3
"""Generate eight non-canonical router-skill facades for generic hosts.

The generated facades are a distribution sidecar.  They are never added to
the repository plugin manifest or counted as business skills.  The catalog's
seven disciplines plus Protocol form one closed partition of all 120 targets;
an overlapping auto facade is intentionally excluded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]
SYSTEM_CATALOG_REF = "references/system-catalog.json"
HOST_PROFILES_REF = "references/host-capability-profiles.json"
SIDECAR_SCHEMA_REF = "references/router-facade-sidecar.schema.json"
SIDECAR_REF = "router-facades/sidecar-manifest.json"
SCHEMA_VERSION = "1.0"
GENERATOR_ID = "generate-router-facades-v1"
ROUTER_PROFILE = "generic-shared-root-host"
SAFE_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
BOUNDARY_RE = re.compile(r"(?:^|\s)(Not for\b.*)$", re.I)


class RouterFacadeError(ValueError):
    """A source cannot produce a closed router-facade partition."""


def canonical_json(value):
    try:
        return (json.dumps(
            value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True,
        ) + "\n").encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise RouterFacadeError("cannot encode canonical JSON: %s" % exc) from exc


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def _strict_json_bytes(content, label):
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RouterFacadeError("%s is not UTF-8" % label) from exc

    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise RouterFacadeError("%s has duplicate JSON key %r" % (label, key))
            result[key] = value
        return result

    def nonfinite(token):
        raise RouterFacadeError("%s has non-finite number %s" % (label, token))

    def finite_float(token):
        value = float(token)
        if not math.isfinite(value):
            nonfinite(token)
        return value

    try:
        return json.loads(
            text,
            object_pairs_hook=pairs,
            parse_constant=nonfinite,
            parse_float=finite_float,
        )
    except RouterFacadeError:
        raise
    except (TypeError, ValueError) as exc:
        raise RouterFacadeError("cannot parse %s: %s" % (label, exc)) from exc


def load_json(root, relative):
    path = Path(root) / relative
    try:
        return _strict_json_bytes(path.read_bytes(), relative)
    except OSError as exc:
        raise RouterFacadeError("cannot read %s: %s" % (relative, exc)) from exc


def _frontmatter_value(raw, label):
    raw = raw.strip()
    if not raw:
        raise RouterFacadeError("%s is empty" % label)
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except ValueError as exc:
            raise RouterFacadeError("%s has invalid double quoting" % label) from exc
        if not isinstance(value, str):
            raise RouterFacadeError("%s must be a string" % label)
        return value
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise RouterFacadeError("%s has invalid single quoting" % label)
        return raw[1:-1].replace("''", "'")
    return raw


def parse_frontmatter(root, relative):
    try:
        text = (Path(root) / relative).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise RouterFacadeError("cannot read %s: %s" % (relative, exc)) from exc
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RouterFacadeError("%s has no frontmatter" % relative)
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise RouterFacadeError("%s has unterminated frontmatter" % relative) from exc
    result = {}
    for line_number, line in enumerate(lines[1:end], 2):
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*", line)
        if not match:
            raise RouterFacadeError(
                "%s:%d uses unsupported multiline frontmatter" % (relative, line_number)
            )
        key = match.group(1)
        if key in result:
            raise RouterFacadeError("%s has duplicate frontmatter key %s" % (relative, key))
        result[key] = _frontmatter_value(
            match.group(2), "%s:%s" % (relative, key)
        )
    return result, text.encode("utf-8")


def validate_host_profiles(catalog):
    expected_keys = {
        "$schema", "schema_version", "default_profile", "profile_order",
        "capability_order", "profiles",
    }
    if not isinstance(catalog, dict) or set(catalog) != expected_keys:
        raise RouterFacadeError("host capability catalog has unknown or missing fields")
    if (catalog["$schema"] != "./host-capability-profiles.schema.json"
            or catalog["schema_version"] != "1.0"):
        raise RouterFacadeError("host capability catalog identity is invalid")
    order = catalog["profile_order"]
    capabilities = catalog["capability_order"]
    profiles = catalog["profiles"]
    if (order != [
                "standalone-skill-host", "generic-shared-root-host",
                "claude-code-plugin-host",
            ]
            or not isinstance(capabilities, list)
            or not capabilities
            or len(capabilities) != len(set(capabilities))
            or any(not isinstance(value, str) or not SAFE_ID_RE.fullmatch(value)
                   for value in capabilities)
            or not isinstance(profiles, dict)
            or set(profiles) != set(order)
            or catalog["default_profile"] != order[0]):
        raise RouterFacadeError("host capability catalog order/set is invalid")
    capability_positions = {value: index for index, value in enumerate(capabilities)}
    surfaces = {
        "direct-skill": ("skill-discovery",),
        "router-skills": ("skill-discovery", "shared-root-references", "router-skills"),
        "slash-commands": ("skill-discovery", "slash-commands"),
    }
    for rank, name in enumerate(order):
        profile = profiles[name]
        required = {
            "rank", "capabilities", "compatible_distributions",
            "routing_surface", "reference_surface", "connector_surface",
        }
        if not isinstance(profile, dict) or set(profile) != required:
            raise RouterFacadeError("host profile %s has invalid fields" % name)
        selected = profile["capabilities"]
        if (profile["rank"] != rank
                or not isinstance(selected, list)
                or len(selected) != len(set(selected))
                or any(value not in capability_positions for value in selected)
                or selected != sorted(selected, key=capability_positions.__getitem__)):
            raise RouterFacadeError("host profile %s capabilities are invalid" % name)
        routing = profile["routing_surface"]
        if routing not in surfaces or any(value not in selected for value in surfaces[routing]):
            raise RouterFacadeError("host profile %s routing surface is unsupported" % name)
        compatible = profile["compatible_distributions"]
        if (not isinstance(compatible, list)
                or not compatible
                or len(compatible) != len(set(compatible))
                or any(value not in {"repository", "plugin", "standalone-skill"}
                       for value in compatible)):
            raise RouterFacadeError("host profile %s distributions are invalid" % name)
        reference = profile["reference_surface"]
        connector = profile["connector_surface"]
        if (reference not in {"skill-local-only", "shared-root"}
                or connector not in {"none", "sidecar", "native-plugin"}
                or (reference == "shared-root" and "shared-root-references" not in selected)
                or (connector == "sidecar" and "connector-sidecars" not in selected)
                or (connector == "native-plugin" and "native-plugin-connectors" not in selected)):
            raise RouterFacadeError("host profile %s surfaces are inconsistent" % name)
    return profiles


def _boundary(description, relative):
    match = BOUNDARY_RE.search(description)
    if not match:
        raise RouterFacadeError("%s description lacks a Not for boundary" % relative)
    return match.group(1).strip()


def _target(root, discipline, phase, name, relative):
    if not SAFE_ID_RE.fullmatch(name):
        raise RouterFacadeError("catalog contains invalid skill name %r" % name)
    frontmatter, content = parse_frontmatter(root, relative)
    required = {"name", "version", "description", "when_to_use", "metadata"}
    if not required.issubset(frontmatter):
        raise RouterFacadeError("%s lacks router frontmatter fields" % relative)
    if frontmatter["name"] != name or not SEMVER_RE.fullmatch(frontmatter["version"]):
        raise RouterFacadeError("%s identity/version does not match catalog" % relative)
    try:
        metadata = _strict_json_bytes(frontmatter["metadata"].encode("utf-8"), relative + ":metadata")
    except UnicodeEncodeError as exc:
        raise RouterFacadeError("%s metadata is not UTF-8" % relative) from exc
    if (not isinstance(metadata, dict)
            or metadata.get("discipline") != discipline
            or metadata.get("phase") != phase):
        raise RouterFacadeError("%s metadata discipline/phase does not match catalog" % relative)
    return {
        "name": name,
        "path": relative,
        "phase": phase,
        "version": frontmatter["version"],
        "skill_sha256": sha256_bytes(content),
        "when_to_use": frontmatter["when_to_use"].strip(),
        "boundary": _boundary(frontmatter["description"].strip(), relative),
    }


def catalog_groups(root, catalog):
    logical_order = catalog.get("logical_order")
    counts = catalog.get("counts")
    if (not isinstance(logical_order, list)
            or logical_order != [
                "narrative", "seo-geo", "social", "email", "ad",
                "influencer", "launch", "protocol",
            ]
            or not isinstance(counts, dict)
            or counts.get("total_skills") != 120):
        raise RouterFacadeError("system catalog does not declare the closed 120-skill topology")
    groups = []
    seen = set()
    for discipline in logical_order:
        targets = []
        if discipline == "protocol":
            specification = catalog.get("protocol")
            if not isinstance(specification, dict) or not isinstance(specification.get("skills"), list):
                raise RouterFacadeError("system catalog protocol shape is invalid")
            display_name = specification.get("display_name")
            phase_order = ["protocol"]
            phases = [("protocol", specification["skills"])]
        else:
            specification = catalog.get("disciplines", {}).get(discipline)
            if not isinstance(specification, dict):
                raise RouterFacadeError("system catalog discipline %s is invalid" % discipline)
            display_name = specification.get("display_name")
            phase_order = specification.get("phase_order")
            phase_map = specification.get("phases")
            if (not isinstance(phase_order, list)
                    or len(phase_order) != len(set(phase_order))
                    or not isinstance(phase_map, dict)
                    or set(phase_map) != set(phase_order)):
                raise RouterFacadeError("system catalog phases for %s are invalid" % discipline)
            phases = [(phase, phase_map[phase]) for phase in phase_order]
        if not isinstance(display_name, str) or not display_name:
            raise RouterFacadeError("system catalog display name for %s is invalid" % discipline)
        for phase, names in phases:
            if (not isinstance(names, list)
                    or not names
                    or len(names) != len(set(names))):
                raise RouterFacadeError("system catalog target list %s/%s is invalid" % (discipline, phase))
            for name in names:
                if name in seen:
                    raise RouterFacadeError("skill %s is covered more than once" % name)
                seen.add(name)
                relative = (
                    "protocol/%s/SKILL.md" % name
                    if discipline == "protocol"
                    else "%s/%s/%s/SKILL.md" % (discipline, phase, name)
                )
                targets.append(_target(root, discipline, phase, name, relative))
        groups.append({
            "discipline": discipline,
            "display_name": display_name,
            "phase_order": phase_order,
            "targets": targets,
        })
    if len(groups) != 8 or len(seen) != counts["total_skills"]:
        raise RouterFacadeError(
            "router partition covers %d groups/%d skills, expected 8/120"
            % (len(groups), len(seen))
        )
    return groups


def _frontmatter_json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))


def render_facade(group, bundle_version):
    discipline = group["discipline"]
    display_name = group["display_name"]
    name = "aaron-marketing-%s-router" % discipline
    metadata = {
        "canonical_business_skill": False,
        "class": "router",
        "discipline": discipline,
        "phase": "router",
        "target_count": len(group["targets"]),
        "version": bundle_version,
    }
    description = (
        "Use when a generic shared-root Agent Skills host without slash commands "
        "must select one %s workflow. Routes only to catalogued business skills; "
        "not for executing the selected workflow or for cross-discipline routing."
        % display_name
    )
    lines = [
        "---",
        "name: %s" % name,
        "version: %s" % bundle_version,
        "description: %s" % json.dumps(description, ensure_ascii=False),
        "license: Apache-2.0",
        "compatibility: Generic shared-root Agent Skills hosts without slash commands",
        "metadata: %s" % _frontmatter_json(metadata),
        "when_to_use: %s" % json.dumps(
            "Route a %s request to exactly one installed Aaron business skill."
            % display_name,
            ensure_ascii=False,
        ),
        "argument-hint: %s goal, inputs, and desired output" % display_name,
        "---",
        "",
        "# %s Router" % display_name,
        "",
        "> Generated distribution facade. It is not one of the 120 canonical business skills, "
        "does not execute domain work, and must not be promoted into the repository skill catalog.",
        "",
        "## Routing Contract",
        "",
        "Choose exactly one target below. Read and invoke that target's `SKILL.md`; the target's "
        "scope, evidence, permission, completion, and handoff rules take precedence. Never combine "
        "two targets into a synthetic workflow. If two targets remain equally plausible or the "
        "request crosses disciplines, return the candidates and stop for user selection.",
        "",
        "## Targets",
    ]
    targets_by_phase = {}
    for target in group["targets"]:
        targets_by_phase.setdefault(target["phase"], []).append(target)
    for phase in group["phase_order"]:
        lines.extend(["", "### %s" % phase])
        for target in targets_by_phase[phase]:
            link = "../../%s" % target["path"]
            lines.extend([
                "",
                "- [`%s`](%s)" % (target["name"], link),
                "  - Route when: %s" % target["when_to_use"],
                "  - Boundary: %s" % target["boundary"],
            ])
    lines.extend([
        "",
        "## Output",
        "",
        "Return `target_skill`, `target_path`, `reason`, `blocking_inputs`, and "
        "`ambiguity: none|needs-user-selection`. Then hand off without performing the target's work.",
        "",
    ])
    return ("\n".join(lines)).encode("utf-8")


def validate_sidecar(
        value, facade_contents, *, expected_host_profile_sha256=None,
        expected_catalog_sha256=None, target_contents=None):
    required = {
        "$schema", "schema_version", "kind", "generator", "host_profile",
        "host_profile_sha256", "routing_surface", "reference_surface",
        "connector_surface", "catalog", "canonical_business_skill_count",
        "facade_count", "coverage_sha256", "facades",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise RouterFacadeError("router sidecar has unknown or missing fields")
    if (value["$schema"] != "../references/router-facade-sidecar.schema.json"
            or value["schema_version"] != SCHEMA_VERSION
            or value["kind"] != "router-facade-sidecar"
            or value["generator"] != GENERATOR_ID
            or value["host_profile"] != ROUTER_PROFILE
            or value["routing_surface"] != "router-skills"
            or value["reference_surface"] != "shared-root"
            or value["connector_surface"] != "sidecar"
            or value["canonical_business_skill_count"] != 120
            or value["facade_count"] != 8):
        raise RouterFacadeError("router sidecar identity is invalid")
    for label in ("host_profile_sha256", "coverage_sha256"):
        if not isinstance(value[label], str) or not re.fullmatch(r"[0-9a-f]{64}", value[label]):
            raise RouterFacadeError("router sidecar %s is invalid" % label)
    if (expected_host_profile_sha256 is not None
            and value["host_profile_sha256"] != expected_host_profile_sha256):
        raise RouterFacadeError("router sidecar host profile binding is stale")
    catalog = value["catalog"]
    if (not isinstance(catalog, dict)
            or set(catalog) != {"path", "sha256", "architecture_version"}
            or catalog["path"] != SYSTEM_CATALOG_REF
            or not isinstance(catalog["sha256"], str)
            or not re.fullmatch(r"[0-9a-f]{64}", catalog["sha256"])
            or not SEMVER_RE.fullmatch(catalog["architecture_version"] or "")):
        raise RouterFacadeError("router sidecar catalog binding is invalid")
    if expected_catalog_sha256 is not None and catalog["sha256"] != expected_catalog_sha256:
        raise RouterFacadeError("router sidecar system catalog binding is stale")

    disciplines = [
        "narrative", "seo-geo", "social", "email", "ad",
        "influencer", "launch", "protocol",
    ]
    facades = value["facades"]
    if (not isinstance(facades, list)
            or len(facades) != 8
            or [item.get("discipline") if isinstance(item, dict) else None
                for item in facades] != disciplines):
        raise RouterFacadeError("router sidecar facade order/set is invalid")
    expected_facade_paths = {
        "router-facades/%s/SKILL.md" % discipline for discipline in disciplines
    }
    if set(facade_contents) != expected_facade_paths:
        raise RouterFacadeError("router sidecar facade file set is invalid")
    all_targets = []
    names = set()
    paths = set()
    for facade in facades:
        required_facade = {
            "id", "name", "discipline", "display_name", "path", "sha256",
            "phase_order", "target_count", "targets",
        }
        discipline = facade["discipline"]
        if (set(facade) != required_facade
                or facade["id"] != "router:%s" % discipline
                or facade["name"] != "aaron-marketing-%s-router" % discipline
                or not isinstance(facade["display_name"], str)
                or not facade["display_name"]
                or facade["path"] != "router-facades/%s/SKILL.md" % discipline
                or not isinstance(facade["phase_order"], list)
                or not facade["phase_order"]
                or len(facade["phase_order"]) != len(set(facade["phase_order"]))
                or any(not isinstance(phase, str) or not SAFE_ID_RE.fullmatch(phase)
                       for phase in facade["phase_order"])
                or facade["target_count"] != (8 if discipline == "protocol" else 16)
                or not isinstance(facade["targets"], list)
                or len(facade["targets"]) != facade["target_count"]):
            raise RouterFacadeError("router sidecar facade %s is invalid" % discipline)
        content = facade_contents[facade["path"]]
        if (not isinstance(content, bytes)
                or facade["sha256"] != sha256_bytes(content)):
            raise RouterFacadeError("router facade %s hash is invalid" % discipline)
        for target in facade["targets"]:
            if (not isinstance(target, dict)
                    or set(target) != {"name", "path", "phase", "skill_sha256"}
                    or not isinstance(target["name"], str)
                    or not SAFE_ID_RE.fullmatch(target["name"])
                    or target["phase"] not in facade["phase_order"]
                    or not isinstance(target["skill_sha256"], str)
                    or not re.fullmatch(r"[0-9a-f]{64}", target["skill_sha256"])):
                raise RouterFacadeError("router sidecar target is invalid")
            expected_path = (
                "protocol/%s/SKILL.md" % target["name"]
                if discipline == "protocol"
                else "%s/%s/%s/SKILL.md"
                % (discipline, target["phase"], target["name"])
            )
            if target["path"] != expected_path:
                raise RouterFacadeError("router sidecar target path is invalid")
            if target["name"] in names or target["path"] in paths:
                raise RouterFacadeError("router sidecar target is covered more than once")
            names.add(target["name"])
            paths.add(target["path"])
            all_targets.append(target)
    if len(all_targets) != 120:
        raise RouterFacadeError("router sidecar does not cover exactly 120 targets")
    if value["coverage_sha256"] != sha256_bytes(canonical_json(all_targets)):
        raise RouterFacadeError("router sidecar coverage hash is invalid")
    if target_contents is not None:
        if not isinstance(target_contents, dict) or set(target_contents) != paths:
            raise RouterFacadeError("router sidecar target file set is invalid")
        for target in all_targets:
            content = target_contents[target["path"]]
            if (not isinstance(content, bytes)
                    or target["skill_sha256"] != sha256_bytes(content)):
                raise RouterFacadeError(
                    "router sidecar target hash is invalid: %s" % target["path"]
                )
    return value


def build_outputs(root=ROOT, host_profile=ROUTER_PROFILE):
    root = Path(root).resolve()
    host_catalog = load_json(root, HOST_PROFILES_REF)
    profiles = validate_host_profiles(host_catalog)
    if host_profile not in profiles:
        raise RouterFacadeError("unknown host profile: %s" % host_profile)
    selected_host = profiles[host_profile]
    if selected_host["routing_surface"] != "router-skills":
        raise RouterFacadeError(
            "host profile %s does not select router-skills" % host_profile
        )
    system_catalog = load_json(root, SYSTEM_CATALOG_REF)
    groups = catalog_groups(root, system_catalog)
    bundle_version = system_catalog.get("bundle_version")
    architecture_version = system_catalog.get("architecture_version")
    if (not SEMVER_RE.fullmatch(bundle_version or "")
            or not SEMVER_RE.fullmatch(architecture_version or "")):
        raise RouterFacadeError("system catalog bundle/architecture version is invalid")

    host_definition = {"profile": host_profile, **selected_host}
    host_sha256 = sha256_bytes(canonical_json(host_definition))
    outputs = {}
    facade_records = []
    covered_targets = []
    for group in groups:
        discipline = group["discipline"]
        relative = "router-facades/%s/SKILL.md" % discipline
        content = render_facade(group, bundle_version)
        outputs[relative] = content
        targets = [{
            "name": target["name"],
            "path": target["path"],
            "phase": target["phase"],
            "skill_sha256": target["skill_sha256"],
        } for target in group["targets"]]
        covered_targets.extend(targets)
        facade_records.append({
            "id": "router:%s" % discipline,
            "name": "aaron-marketing-%s-router" % discipline,
            "discipline": discipline,
            "display_name": group["display_name"],
            "path": relative,
            "sha256": sha256_bytes(content),
            "phase_order": group["phase_order"],
            "target_count": len(targets),
            "targets": targets,
        })
    sidecar = {
        "$schema": "../%s" % SIDECAR_SCHEMA_REF,
        "schema_version": SCHEMA_VERSION,
        "kind": "router-facade-sidecar",
        "generator": GENERATOR_ID,
        "host_profile": host_profile,
        "host_profile_sha256": host_sha256,
        "routing_surface": selected_host["routing_surface"],
        "reference_surface": selected_host["reference_surface"],
        "connector_surface": selected_host["connector_surface"],
        "catalog": {
            "path": SYSTEM_CATALOG_REF,
            "sha256": sha256_bytes((root / SYSTEM_CATALOG_REF).read_bytes()),
            "architecture_version": architecture_version,
        },
        "canonical_business_skill_count": len(covered_targets),
        "facade_count": len(facade_records),
        "coverage_sha256": sha256_bytes(canonical_json(covered_targets)),
        "facades": facade_records,
    }
    validate_sidecar(
        sidecar,
        {path: content for path, content in outputs.items()},
        expected_host_profile_sha256=host_sha256,
        expected_catalog_sha256=sidecar["catalog"]["sha256"],
    )
    outputs[SIDECAR_REF] = canonical_json(sidecar)
    return outputs


def write_outputs(outputs, destination):
    destination = Path(destination)
    try:
        status = destination.lstat()
    except FileNotFoundError:
        destination.mkdir(parents=True)
    else:
        if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
            raise RouterFacadeError("output must be a real directory")
        if any(destination.iterdir()):
            raise RouterFacadeError("output directory must be empty")
    for relative, content in sorted(outputs.items()):
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        try:
            descriptor = os.open(target, flags, 0o644)
            with os.fdopen(descriptor, "wb", closefd=True) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError as exc:
            raise RouterFacadeError("cannot write %s: %s" % (relative, exc)) from exc


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host-profile", default=ROUTER_PROFILE)
    args = parser.parse_args(argv)
    try:
        outputs = build_outputs(ROOT, args.host_profile)
        write_outputs(outputs, args.output)
    except RouterFacadeError as exc:
        print("router-facade-generator: %s" % exc, file=sys.stderr)
        return 1
    print(
        "wrote %d router facades plus sidecar manifest for %s"
        % (len(outputs) - 1, args.host_profile)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
