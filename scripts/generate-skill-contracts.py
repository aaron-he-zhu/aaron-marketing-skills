#!/usr/bin/env python3
"""Generate deterministic machine contracts for every catalogued skill.

The generator deliberately extracts only authored facts.  It does not infer
missing business semantics from a skill name or neighboring skills.  Required
frontmatter, contract fields, and handoff sections therefore fail closed when
they cannot be recovered from the checked-in Markdown.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CATALOG_REF = "references/system-catalog.json"
PLUGIN_REF = ".claude-plugin/plugin.json"
SHARED_CONTRACT_REF = "references/skill-contract.md"
CONTRACT_SCHEMA_REF = "references/skill-machine-contract.schema.json"
INDEX_SCHEMA_REF = "references/skill-machine-contract-index.schema.json"
OUTPUT_DIR_REF = "references/skill-contracts"
INDEX_REF = OUTPUT_DIR_REF + "/index.json"
SCHEMA_VERSION = "1.0"

SAFE_SKILL_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$")
QUOTED_TRIGGER_RE = re.compile(r'"([^"\n]{3,})"')
BOUNDARY_RE = re.compile(r"\bnot\s+for\b", re.I)
HEADING_RE = re.compile(r"^## ([^\n]+)\s*$", re.M)
SUBHEADING_RE = re.compile(r"^### ([^\n]+)\s*$", re.M)
CONTRACT_MARKER_RE = re.compile(
    r"(?:^|(?<=\s))(?:-\s*)?\*\*"
    r"(?P<label>[A-Za-z][A-Za-z /-]{1,48}?)(?P<inside_colon>:?)"
    r"\*\*\s*:?[ \t]*",
    re.M,
)
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
INLINE_PATH_RE = re.compile(r"`([^`]+\.(?:md|json))`")
MEMORY_PATH_RE = re.compile(r"`(memory/[A-Za-z0-9._/<>-]+)`")
BACKTICK_TOKEN_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")


class ContractGenerationError(ValueError):
    """A source cannot be represented honestly by the machine contract."""


def canonical_json(value):
    try:
        rendered = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ContractGenerationError("cannot encode canonical JSON: %s" % exc) from exc
    return (rendered + "\n").encode("utf-8")


def sha256_bytes(content):
    return hashlib.sha256(content).hexdigest()


def sha256_path(path):
    try:
        return sha256_bytes(path.read_bytes())
    except OSError as exc:
        raise ContractGenerationError("cannot hash %s: %s" % (path, exc)) from exc


def strict_json_bytes(content, label):
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractGenerationError("%s is not UTF-8" % label) from exc

    def pairs(values):
        result = {}
        for key, value in values:
            if key in result:
                raise ContractGenerationError("%s has duplicate JSON key %r" % (label, key))
            result[key] = value
        return result

    def nonfinite(token):
        raise ContractGenerationError("%s has non-finite number %s" % (label, token))

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
    except ContractGenerationError:
        raise
    except (TypeError, ValueError) as exc:
        raise ContractGenerationError("cannot parse %s: %s" % (label, exc)) from exc


def load_json(root, relative):
    path = root / relative
    try:
        return strict_json_bytes(path.read_bytes(), relative)
    except OSError as exc:
        raise ContractGenerationError("cannot read %s: %s" % (relative, exc)) from exc


def catalog_skill_paths(catalog):
    result = []
    logical_order = catalog.get("logical_order")
    if not isinstance(logical_order, list):
        raise ContractGenerationError("system catalog lacks logical_order")
    for discipline in logical_order:
        if discipline == "protocol":
            protocol = catalog.get("protocol", {})
            skills = protocol.get("skills")
            if not isinstance(skills, list):
                raise ContractGenerationError("system catalog protocol.skills is invalid")
            for skill in skills:
                result.append((skill, "protocol/%s" % skill, "protocol", "protocol"))
            continue
        specification = catalog.get("disciplines", {}).get(discipline)
        if not isinstance(specification, dict):
            raise ContractGenerationError("unknown catalog discipline: %s" % discipline)
        for phase in specification.get("phase_order", []):
            skills = specification.get("phases", {}).get(phase)
            if not isinstance(skills, list):
                raise ContractGenerationError(
                    "catalog phase is not a skill list: %s/%s" % (discipline, phase)
                )
            for skill in skills:
                result.append((skill, "%s/%s/%s" % (discipline, phase, skill), discipline, phase))
    declared = catalog.get("counts", {}).get("total_skills")
    if declared != len(result):
        raise ContractGenerationError(
            "catalog declares %r skills but enumerates %d" % (declared, len(result))
        )
    names = [item[0] for item in result]
    if len(names) != len(set(names)):
        raise ContractGenerationError("system catalog contains duplicate skill names")
    return result


def frontmatter_value(raw, label):
    raw = raw.strip()
    if not raw:
        raise ContractGenerationError("%s is empty" % label)
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except ValueError as exc:
            raise ContractGenerationError("%s has invalid double quoting" % label) from exc
        if not isinstance(value, str):
            raise ContractGenerationError("%s must be a string" % label)
        return value
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise ContractGenerationError("%s has invalid single quoting" % label)
        return raw[1:-1].replace("''", "'")
    return raw


def parse_frontmatter(text, relative):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractGenerationError("%s has no frontmatter" % relative)
    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ContractGenerationError("%s has unterminated frontmatter" % relative) from exc
    values = {}
    for line_number, line in enumerate(lines[1:end], 2):
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if not match:
            raise ContractGenerationError(
                "%s:%d uses unsupported multiline/non-scalar frontmatter" % (relative, line_number)
            )
        key = match.group(1)
        if key in values:
            raise ContractGenerationError("%s has duplicate frontmatter key %s" % (relative, key))
        values[key] = frontmatter_value(match.group(2), "%s:%s" % (relative, key))
    return values, "\n".join(lines[end + 1:]) + "\n"


def normalize_markdown(value):
    lines = [line.rstrip() for line in value.strip().splitlines()]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines).strip()


def section(text, heading, relative, required=True):
    matches = list(HEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip() != heading:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = normalize_markdown(text[start:end])
        if required and not value:
            raise ContractGenerationError("%s has empty ## %s" % (relative, heading))
        return value
    if required:
        raise ContractGenerationError("%s is missing ## %s" % (relative, heading))
    return None


def subsection(text, heading):
    matches = list(SUBHEADING_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group(1).strip() != heading:
            continue
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return normalize_markdown(text[start:end])
    return None


def contract_fields(contract_text, relative):
    markers = []
    for match in CONTRACT_MARKER_RE.finditer(contract_text):
        label = match.group("label").strip().rstrip(":").lower()
        markers.append((match.start(), match.end(), label))
    fields = {}
    selected = {"expected output", "reads", "writes", "done when", "primary next skill"}
    for index, (_start, value_start, label) in enumerate(markers):
        if label not in selected or label in fields:
            continue
        value_end = markers[index + 1][0] if index + 1 < len(markers) else len(contract_text)
        heading = re.search(r"(?m)^###?\s+", contract_text[value_start:value_end])
        if heading:
            value_end = value_start + heading.start()
        value = normalize_markdown(contract_text[value_start:value_end])
        if value:
            fields[label] = value
    for required in ("reads", "writes", "done when"):
        if not fields.get(required):
            raise ContractGenerationError(
                "%s Skill Contract has no extractable %s field" % (relative, required)
            )
    return fields


def clause_spans(value, label):
    """Split only on authored semicolon/newline boundaries and retain exact spans."""
    clauses = []
    for match in re.finditer(r"[^;\n]+", value):
        raw = match.group(0)
        left = len(raw) - len(raw.lstrip())
        right = len(raw.rstrip())
        if right <= left:
            continue
        start = match.start() + left
        end = match.start() + right
        clauses.append((value[start:end], start, end))
    if not clauses:
        raise ContractGenerationError("%s has no extractable clauses" % label)
    return clauses


def clause_source(path, sha256, section_name, start, end):
    return {
        "path": path,
        "sha256": sha256,
        "section": section_name,
        "span_basis": "field-text",
        "start_char": start,
        "end_char": end,
    }


def extraction_status(values):
    states = [value["extraction_status"] for value in values]
    if all(state == "classified" for state in states):
        return "classified"
    if all(state == "unclassified" for state in states):
        return "unclassified"
    return "partially-classified"


def item_status(*values):
    known = [value != "unclassified" and value is not None for value in values]
    if all(known):
        return "classified"
    if any(known):
        return "partially-classified"
    return "unclassified"


def input_clauses(value, skill_ref, skill_hash):
    result = []
    optional = re.compile(
        r"\b(?:optional|if available|when available|where available|as available|"
        r"if provided|when provided|where provided)\b", re.I,
    )
    required = re.compile(r"\b(?:must|required|requires?|needs?)\b", re.I)
    for offset, (text, start, end) in enumerate(clause_spans(value, "Reads"), 1):
        lower = text.lower()
        if re.search(r"`memory/", text):
            kind = "project-resource"
        elif re.search(r"`[^`]+\.(?:md|json)`", text):
            kind = "bundle-resource"
        elif re.search(
                r"\b(?:artifact|brief|data|dataset|evidence|export|input|report|url|"
                r"content|analytics|transcript|record|research)\b", lower):
            kind = "evidence-input"
        else:
            kind = "unclassified"
        if optional.search(text):
            requirement = "optional"
        elif required.search(text):
            requirement = "required"
        else:
            requirement = "unclassified"
        result.append({
            "clause_id": "read-%02d" % offset,
            "text": text,
            "kind": kind,
            "requirement": requirement,
            "extraction_status": item_status(kind, requirement),
            "source": clause_source(
                skill_ref, skill_hash, "Skill Contract/Reads", start, end
            ),
        })
    return result


def output_clauses(value, skill_ref, skill_hash):
    result = []
    for offset, (text, start, end) in enumerate(clause_spans(value, "Writes"), 1):
        lower = text.lower()
        signals = []
        if re.search(r"`memory/|\bmemory/", text):
            signals.append(("project-artifact", "project-write"))
        if "registry-events.py" in text or re.search(r"\bregistry\b.*\bpropos", lower):
            signals.append(("registry-event", "registry-proposal"))
        if re.search(
                r"\b(?:send|publish|post|deploy|delete|erase)(?:s|ed|ing)?\b", lower):
            signals.append(("external-action", "external-mutation"))
        unique = sorted(set(signals))
        if len(unique) == 1:
            kind, side_effect = unique[0]
        elif len(unique) > 1:
            kind, side_effect = "mixed", "mixed"
        else:
            kind, side_effect = "unclassified", "unclassified"
        if re.search(
                r"\b(?:with permission|permissioned|with consent|only after approval|"
                r"requires? approval)\b", lower):
            permission = "permission-required"
        elif re.search(
                r"\b(?:read-only|no mutation|does not write|do not write|"
                r"(?:never|must not) (?:write|send|publish|post|delete|update))\b", lower):
            permission = "prohibited"
        elif side_effect in {
                "project-write", "registry-proposal", "external-mutation", "mixed"}:
            # The shared Write and Action Permission contract is authoritative:
            # a skill-local destination never grants current-request authority.
            permission = "permission-required"
        else:
            permission = "unclassified"
        result.append({
            "clause_id": "write-%02d" % offset,
            "text": text,
            "kind": kind,
            "side_effect": side_effect,
            "permission_posture": permission,
            "extraction_status": item_status(kind, side_effect, permission),
            "source": clause_source(
                skill_ref, skill_hash, "Skill Contract/Writes", start, end
            ),
        })
    return result


def completion_clauses(value, skill_ref, skill_hash):
    result = []
    blocking = re.compile(
        r"\b(?:block(?:ed|ing)?|cannot complete|must not proceed|not complete|stop)\b",
        re.I,
    )
    for offset, (text, start, end) in enumerate(clause_spans(value, "Done when"), 1):
        result.append({
            "clause_id": "done-%02d" % offset,
            "text": text,
            "condition_kind": "blocking" if blocking.search(text) else "success",
            "requirement": "required",
            "extraction_status": "classified",
            "source": clause_source(
                skill_ref, skill_hash, "Skill Contract/Done when", start, end
            ),
        })
    return result


def targets_in_fragment(root, skill_ref, value, known_skills):
    targets = set()
    for raw in MARKDOWN_LINK_RE.findall(value):
        relative = repository_link(root, skill_ref, raw)
        if relative and relative.endswith("/SKILL.md"):
            slug = Path(relative).parent.name
            if slug in known_skills:
                targets.add(slug)
    for token in BACKTICK_TOKEN_RE.findall(value):
        if token in known_skills:
            targets.add(token)
    return sorted(targets)


def handoff_items(root, skill_ref, skill_hash, value, known_skills):
    result = []
    for offset, (text, start, end) in enumerate(clause_spans(value, "Next Best Skill"), 1):
        label_match = re.search(r"\*\*([^*]+)\*\*", text)
        label = label_match.group(1).strip().lower() if label_match else ""
        if label == "primary":
            kind = "primary"
        elif label == "conditional":
            kind = "conditional"
        elif label == "termination":
            kind = "termination"
        elif re.search(r"\b(?:ship|fix|block|undecided)\b", label):
            kind = "outcome"
        else:
            kind = "unclassified"
        condition_match = re.search(r"\b(?:when|if|after|before|unless)\b.+", text, re.I)
        condition = condition_match.group(0).strip() if condition_match else None
        targets = targets_in_fragment(root, skill_ref, text, known_skills)
        if kind == "termination":
            status = "classified"
        elif kind == "conditional":
            status = (
                "classified" if condition is not None and targets
                else "partially-classified" if condition is not None or targets
                else "unclassified"
            )
        else:
            status = item_status(kind, targets[0] if targets else None)
        result.append({
            "item_id": "handoff-%02d" % offset,
            "text": text,
            "kind": kind,
            "condition": condition,
            "target_skills": targets,
            "extraction_status": status,
            "source": clause_source(
                skill_ref, skill_hash, "Next Best Skill", start, end
            ),
        })
    return result


def source_locator(path, sha256, section_name):
    return {"path": path, "sha256": sha256, "section": section_name}


def repository_link(root, skill_ref, raw_target):
    target = raw_target.strip().lstrip("<").rstrip(">").split("#", 1)[0]
    if not target or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
        return None
    candidate = (root / Path(skill_ref).parent / target).resolve()
    try:
        relative = candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    return relative.as_posix()


def bundle_references(root, skill_ref, body):
    references = {}
    lines = body.splitlines()
    required_list = False
    for line_number, line in enumerate(lines, 1):
        stripped = line.strip()
        line_declares_read = bool(re.search(r"\bread\b", line, re.I))
        list_item = bool(re.match(r"^(?:\d+\.|[-*])\s+", stripped))
        if stripped and required_list and not list_item:
            required_list = False
        required = line_declares_read or (required_list and list_item)
        raw_targets = list(MARKDOWN_LINK_RE.findall(line))
        raw_targets.extend(INLINE_PATH_RE.findall(line))
        for raw in raw_targets:
            relative = repository_link(root, skill_ref, raw)
            if relative is None and "/" not in raw:
                fallback = root / "references" / raw.split("#", 1)[0]
                if fallback.is_file():
                    relative = fallback.relative_to(root).as_posix()
            if relative is None or relative.endswith("/SKILL.md"):
                continue
            current = references.get(relative)
            item = {
                "path": relative,
                "sha256": sha256_path(root / relative),
                "requirement": "required" if required else "optional",
                "reason_code": "explicit-runtime-read" if required else "authored-reference",
                "source_line": line_number,
            }
            if current is None or (
                    current["requirement"] == "optional" and item["requirement"] == "required"):
                references[relative] = item
        if line_declares_read and stripped.endswith(":"):
            required_list = True
    return [references[key] for key in sorted(references)]


def path_policy(path):
    if path.startswith("memory/projections/"):
        authority = "canonical"
    elif path == "memory/decisions.md":
        authority = "approved"
    else:
        authority = "working"
    sensitivity = "restricted" if "consent" in path.lower() else "confidential"
    return authority, sensitivity


def project_path_hints(reads):
    hints = {}
    for match in MEMORY_PATH_RE.finditer(reads):
        raw = match.group(1).rstrip(".,;:")
        if any(character in raw for character in "<>{}*[]"):
            prefix = raw.split("<", 1)[0].rstrip("/")
            if not prefix or not re.fullmatch(r"memory/[A-Za-z0-9._/-]+", prefix):
                continue
            path = prefix
            kind = "prefix"
        else:
            path = raw.rstrip("/")
            kind = "prefix" if raw.endswith("/") else "file"
        authority, sensitivity = path_policy(path)
        hints[(path, kind)] = {
            "path": path,
            "kind": kind,
            "access": "read",
            "authority": authority,
            "sensitivity": sensitivity,
            "reason_code": "explicit-skill-read",
        }
    return [hints[key] for key in sorted(hints)]


def handoff_targets(root, skill_ref, next_best, known_skills):
    targets = set()
    for raw in MARKDOWN_LINK_RE.findall(next_best):
        relative = repository_link(root, skill_ref, raw)
        if relative and relative.endswith("/SKILL.md"):
            slug = Path(relative).parent.name
            if slug in known_skills:
                targets.add(slug)
    for token in BACKTICK_TOKEN_RE.findall(next_best):
        if token in known_skills:
            targets.add(token)
    return sorted(targets)


def build_contract(
        root, skill, skill_dir, discipline, phase, catalog_record,
        shared_record, known_skills):
    skill_ref = skill_dir + "/SKILL.md"
    skill_path = root / skill_ref
    try:
        content = skill_path.read_bytes()
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractGenerationError("%s is not UTF-8" % skill_ref) from exc
    except OSError as exc:
        raise ContractGenerationError("cannot read %s: %s" % (skill_ref, exc)) from exc
    skill_hash = sha256_bytes(content)
    frontmatter, body = parse_frontmatter(text, skill_ref)
    for key in (
            "name", "version", "description", "when_to_use", "argument-hint", "metadata"):
        if key not in frontmatter:
            raise ContractGenerationError("%s is missing frontmatter %s" % (skill_ref, key))
    if frontmatter["name"] != skill:
        raise ContractGenerationError("%s name does not match catalog" % skill_ref)
    if not SAFE_SKILL_RE.fullmatch(skill):
        raise ContractGenerationError("invalid catalog skill name: %s" % skill)
    version = frontmatter["version"]
    if not SEMVER_RE.fullmatch(version):
        raise ContractGenerationError("%s has invalid version %s" % (skill_ref, version))
    metadata = strict_json_bytes(frontmatter["metadata"].encode("utf-8"), skill_ref + ":metadata")
    if not isinstance(metadata, dict):
        raise ContractGenerationError("%s metadata must be an object" % skill_ref)
    if metadata.get("version") != version:
        raise ContractGenerationError("%s metadata.version differs from version" % skill_ref)
    if metadata.get("discipline") != discipline or metadata.get("phase") != phase:
        raise ContractGenerationError("%s metadata discipline/phase differs from catalog" % skill_ref)

    description = frontmatter["description"]
    boundary_match = BOUNDARY_RE.search(description)
    if not boundary_match:
        raise ContractGenerationError("%s description has no Not for boundary" % skill_ref)
    trigger_text = description[:boundary_match.start()].strip()
    boundary = description[boundary_match.start():].strip()
    triggers = sorted(set(match.strip() for match in QUOTED_TRIGGER_RE.findall(trigger_text)))
    if triggers:
        trigger_source = "description-quoted"
    else:
        # Some authored descriptions use prose instead of quoted examples.  Keep
        # that distinction machine-visible and fall back to the complete,
        # explicitly authored when_to_use field rather than inventing phrases.
        fallback_trigger = frontmatter["when_to_use"].strip()
        if not fallback_trigger:
            raise ContractGenerationError(
                "%s has neither quoted description triggers nor when_to_use" % skill_ref
            )
        triggers = [fallback_trigger]
        trigger_source = "when-to-use-fallback"

    for required_heading in (
            "Quick Start", "Skill Contract", "Data Sources", "Instructions",
            "Reference Materials", "Next Best Skill"):
        section(body, required_heading, skill_ref)
    contract_text = section(body, "Skill Contract", skill_ref)
    fields = contract_fields(contract_text, skill_ref)
    next_best = section(body, "Next Best Skill", skill_ref)
    handoff_summary = subsection(contract_text, "Handoff Summary")
    if handoff_summary:
        handoff_source = "skill-section"
        handoff_ref = source_locator(skill_ref, skill_hash, "Skill Contract/Handoff Summary")
    else:
        if frontmatter.get("class") != "auditor" or "auditor-runbook.md" not in body:
            raise ContractGenerationError(
                "%s lacks Handoff Summary and is not an auditor with shared runbook" % skill_ref
            )
        handoff_source = "shared-skill-contract"
        handoff_ref = source_locator(
            shared_record["path"], shared_record["sha256"], "Handoff Summary Format"
        )

    output_source = "expected-output" if fields.get("expected output") else "writes-fallback"
    output_summary = fields.get("expected output", fields["writes"])
    references = bundle_references(root, skill_ref, body)
    targets = handoff_targets(root, skill_ref, next_best, known_skills)
    reads_items = input_clauses(fields["reads"], skill_ref, skill_hash)
    writes_items = output_clauses(fields["writes"], skill_ref, skill_hash)
    done_items = completion_clauses(fields["done when"], skill_ref, skill_hash)
    next_items = handoff_items(root, skill_ref, skill_hash, next_best, known_skills)
    source = source_locator(skill_ref, skill_hash, "frontmatter")
    return {
        "$schema": "../skill-machine-contract.schema.json",
        "schema_version": SCHEMA_VERSION,
        "contract_id": "skill:%s" % skill,
        "identity": {
            "name": skill,
            "path": skill_ref,
            "sha256": skill_hash,
            "version": version,
            "discipline": discipline,
            "phase": phase,
            "class": frontmatter.get("class"),
        },
        "routing_contract": {
            "description": description,
            "when_to_use": frontmatter["when_to_use"],
            "trigger_phrases": triggers,
            "trigger_source": trigger_source,
            "boundary": boundary,
            "source": source,
        },
        "input_contract": {
            "argument_hint": frontmatter["argument-hint"],
            "reads": fields["reads"],
            "clauses": reads_items,
            "extraction_status": extraction_status(reads_items),
            "source": source_locator(skill_ref, skill_hash, "Skill Contract/Reads"),
        },
        "output_contract": {
            "summary": output_summary,
            "summary_source": output_source,
            "writes": fields["writes"],
            "clauses": writes_items,
            "extraction_status": extraction_status(writes_items),
            "source": source_locator(skill_ref, skill_hash, "Skill Contract"),
        },
        "completion_contract": {
            "done_when": fields["done when"],
            "clauses": done_items,
            "extraction_status": extraction_status(done_items),
            "source": source_locator(skill_ref, skill_hash, "Skill Contract/Done when"),
        },
        "handoff_contract": {
            "summary_source": handoff_source,
            "summary": handoff_summary,
            "summary_ref": handoff_ref,
            "next_best": next_best,
            "target_skills": targets,
            "items": next_items,
            "extraction_status": extraction_status(next_items),
        },
        "context_hints": {
            "bundle_references": references,
            "project_paths": project_path_hints(fields["reads"]),
        },
        "provenance": {
            "generator": "generate-skill-contracts-v1",
            "system_catalog": catalog_record,
            "shared_contract": source_locator(
                shared_record["path"], shared_record["sha256"], "Skill Contract"
            ),
        },
    }


def build_contracts(root=ROOT):
    root = Path(root).resolve()
    catalog = load_json(root, CATALOG_REF)
    plugin = load_json(root, PLUGIN_REF)
    ordered = catalog_skill_paths(catalog)
    plugin_paths = [entry.removeprefix("./").rstrip("/") for entry in plugin.get("skills", [])]
    catalog_paths = [item[1] for item in ordered]
    if plugin_paths != catalog_paths:
        raise ContractGenerationError("plugin skill order/set differs from system catalog")
    catalog_record = {
        "path": CATALOG_REF,
        "sha256": sha256_path(root / CATALOG_REF),
        "version": catalog.get("architecture_version"),
    }
    if not SEMVER_RE.fullmatch(catalog_record["version"] or ""):
        raise ContractGenerationError("system catalog architecture_version is invalid")
    shared_record = {
        "path": SHARED_CONTRACT_REF,
        "sha256": sha256_path(root / SHARED_CONTRACT_REF),
    }
    known = {item[0] for item in ordered}
    contracts = []
    for skill, skill_dir, discipline, phase in ordered:
        contracts.append(build_contract(
            root, skill, skill_dir, discipline, phase, catalog_record,
            shared_record, known,
        ))
    return contracts


def build_outputs(root=ROOT):
    root = Path(root).resolve()
    contracts = build_contracts(root)
    outputs = {}
    index_entries = []
    for contract in contracts:
        skill = contract["identity"]["name"]
        relative = "%s/%s.json" % (OUTPUT_DIR_REF, skill)
        content = canonical_json(contract)
        outputs[relative] = content
        index_entries.append({
            "skill": skill,
            "contract_ref": relative,
            "contract_sha256": sha256_bytes(content),
        })
    catalog = contracts[0]["provenance"]["system_catalog"] if contracts else None
    shared_source = contracts[0]["provenance"]["shared_contract"] if contracts else None
    shared = (
        {"path": shared_source["path"], "sha256": shared_source["sha256"]}
        if shared_source else None
    )
    index = {
        "$schema": "../skill-machine-contract-index.schema.json",
        "schema_version": SCHEMA_VERSION,
        "contract_count": len(index_entries),
        "contract_schema": {
            "path": CONTRACT_SCHEMA_REF,
            "sha256": sha256_path(root / CONTRACT_SCHEMA_REF),
        },
        "source_catalog": catalog,
        "shared_contract": shared,
        "contracts": index_entries,
    }
    outputs[INDEX_REF] = canonical_json(index)
    return outputs


def check_outputs(outputs, root=ROOT):
    root = Path(root).resolve()
    failures = []
    expected = set(outputs)
    for relative, content in sorted(outputs.items()):
        path = root / relative
        try:
            current = path.read_bytes()
        except FileNotFoundError:
            failures.append("missing generated contract: %s" % relative)
            continue
        except OSError as exc:
            failures.append("cannot read %s: %s" % (relative, exc))
            continue
        if current != content:
            failures.append("stale generated contract: %s" % relative)
    output_dir = root / OUTPUT_DIR_REF
    if output_dir.is_dir():
        for path in sorted(output_dir.glob("*.json")):
            relative = path.relative_to(root).as_posix()
            if relative not in expected:
                failures.append("unexpected generated contract: %s" % relative)
    return failures


def write_outputs(outputs, root=ROOT):
    root = Path(root).resolve()
    output_dir = root / OUTPUT_DIR_REF
    output_dir.mkdir(parents=True, exist_ok=True)
    expected = set(outputs)
    for relative, content in sorted(outputs.items()):
        target = root / relative
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
    for path in output_dir.glob("*.json"):
        if path.relative_to(root).as_posix() not in expected:
            path.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = build_outputs(ROOT)
        if args.check:
            failures = check_outputs(outputs, ROOT)
            if failures:
                for failure in failures:
                    print("FAIL  " + failure, file=sys.stderr)
                return 1
            print("skill machine contracts current (%d contracts)" % (len(outputs) - 1))
            return 0
        write_outputs(outputs, ROOT)
        print("wrote %d skill machine contracts plus index" % (len(outputs) - 1))
        return 0
    except ContractGenerationError as exc:
        print("skill-contract-generator: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
