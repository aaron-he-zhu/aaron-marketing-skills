#!/usr/bin/env python3
"""Generate compact, source-anchored model capsules for all 120 business skills."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_INDEX = ROOT / "references" / "skill-contracts" / "index.json"
CAPSULE_DIR = ROOT / "references" / "skill-capsules"
CAPSULE_INDEX = CAPSULE_DIR / "index.json"
CAPSULE_SCHEMA = ROOT / "references" / "skill-capsule.schema.json"
CAPSULE_INDEX_SCHEMA = ROOT / "references" / "skill-capsule-index.schema.json"
POLICY_KERNEL = ROOT / "references" / "policy-kernel.md"
ALWAYS_ON_OVERLAYS = [
    "consent",
    "claims",
    "pii-secrets",
    "external-mutation",
    "audit-verdict",
    "release-provenance",
]
OMITTED_STANDARD_SECTIONS = {
    "Quick Start",
    "Skill Contract",
    "Data Sources",
    "Reference Materials",
    "Save Results",
    "Next Best Skill",
}
TOP_LEVEL_SECTION = re.compile(r"(?m)^## ([^\n]+)\n")
MARKDOWN_LINK = re.compile(
    r"(?<!!)(?P<prefix>\[[^\]]+\]\()(?P<target>[^)]+)(?P<suffix>\))"
)
URI_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


class CapsuleError(ValueError):
    pass


def _sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def _canonical_bytes(value):
    try:
        return (json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ) + "\n").encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise CapsuleError("cannot encode capsule JSON: %s" % exc) from exc


def _load_json(path, label):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise CapsuleError("cannot load %s: %s" % (label, exc)) from exc


def _read_bytes(path, label):
    try:
        return path.read_bytes()
    except OSError as exc:
        raise CapsuleError("cannot read %s: %s" % (label, exc)) from exc


def _relative(path):
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError as exc:
        raise CapsuleError("path is outside repository: %s" % path) from exc


def _strip_frontmatter(text):
    if not text.startswith("---\n"):
        raise CapsuleError("Skill source has no opening YAML frontmatter")
    boundary = text.find("\n---\n", 4)
    if boundary < 0:
        raise CapsuleError("Skill source has no closing YAML frontmatter")
    return text[boundary + 5:]


def _operational_markdown(source_text):
    body = _strip_frontmatter(source_text)
    matches = list(TOP_LEVEL_SECTION.finditer(body))
    if not matches:
        raise CapsuleError("Skill source has no level-two sections")
    retained = []
    for index, match in enumerate(matches):
        title = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        if title not in OMITTED_STANDARD_SECTIONS:
            section = body[match.start():end].strip()
            if section:
                retained.append(section)
    if not retained:
        raise CapsuleError("Skill source has no operational sections after projection")
    result = "\n\n".join(retained)
    for title in OMITTED_STANDARD_SECTIONS:
        if re.search(r"(?m)^## %s\s*$" % re.escape(title), result):
            raise CapsuleError("standard section leaked into operational capsule: %s" % title)
    return result


def _rebase_projected_markdown(markdown, source_path, capsule_path, *, root=ROOT):
    """Rebase repository-local links in Skill-derived prose to its capsule.

    Skill-derived Markdown is embedded in a JSON file under
    ``references/skill-capsules``. Relative links copied byte-for-byte from a
    deeply nested ``SKILL.md`` therefore point somewhere else (and often escape
    the repository). External URIs and same-document anchors remain unchanged;
    every repository-local target must resolve inside ``root`` and already
    exist before it is rewritten relative to the capsule location. Callers use
    this only for projected prose, never identifiers, enums, or path fields.
    """
    root = Path(root).resolve()
    source_path = Path(source_path).resolve()
    capsule_path = Path(capsule_path).resolve()
    try:
        source_label = source_path.relative_to(root).as_posix()
        capsule_path.relative_to(root)
    except ValueError as exc:
        raise CapsuleError("capsule link endpoint is outside repository") from exc

    def replace(match):
        raw_target = match.group("target")
        target = raw_target.strip()
        angled = target.startswith("<") and target.endswith(">")
        if angled:
            target = target[1:-1].strip()
        path_text, separator, fragment = target.partition("#")
        if not path_text or URI_SCHEME.match(path_text):
            return match.group(0)
        if any(character.isspace() for character in path_text):
            raise CapsuleError(
                "%s has an unsupported local Markdown link target: %s"
                % (source_label, raw_target)
            )
        resolved = (source_path.parent / path_text).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise CapsuleError(
                "%s Markdown link escapes repository: %s"
                % (source_label, raw_target)
            ) from exc
        if not resolved.exists():
            raise CapsuleError(
                "%s Markdown link target does not exist: %s"
                % (source_label, raw_target)
            )
        rebased = Path(os.path.relpath(resolved, capsule_path.parent)).as_posix()
        if separator:
            rebased += "#" + fragment
        if angled:
            rebased = "<%s>" % rebased
        return match.group("prefix") + rebased + match.group("suffix")

    return MARKDOWN_LINK.sub(replace, markdown)


def _file_ref(path, raw=None):
    if raw is None:
        raw = _read_bytes(path, _relative(path))
    return {"path": _relative(path), "sha256": _sha256(raw)}


def _contract_entry_map(index):
    if (
            not isinstance(index, dict) or index.get("schema_version") != "1.0"
            or index.get("contract_count") != 120
            or not isinstance(index.get("contracts"), list)
            or len(index["contracts"]) != 120):
        raise CapsuleError("skill contract index identity/count is unsupported")
    entries = {}
    for item in index["contracts"]:
        if not isinstance(item, dict) or set(item) != {
                "skill", "contract_ref", "contract_sha256"}:
            raise CapsuleError("skill contract index entry shape is invalid")
        skill = item["skill"]
        if skill in entries:
            raise CapsuleError("duplicate skill contract index entry: %s" % skill)
        entries[skill] = item
    if len(entries) != 120:
        raise CapsuleError("skill contract index does not contain 120 unique skills")
    return entries


def _write_controls(clauses):
    """Keep only distinct control semantics; full wording remains controller-side."""
    result = []
    seen = set()
    for item in clauses:
        key = (item["kind"], item["side_effect"], item["permission_posture"])
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "kind": key[0],
            "side_effect": key[1],
            "permission_posture": key[2],
        })
    if not result:
        raise CapsuleError("machine contract has no write controls")
    return result


def _build_capsule(skill, entry, policy_ref):
    contract_path = ROOT / entry["contract_ref"]
    contract_raw = _read_bytes(contract_path, entry["contract_ref"])
    if _sha256(contract_raw) != entry["contract_sha256"]:
        raise CapsuleError("machine contract hash differs for %s" % skill)
    contract = _load_json(contract_path, "machine contract %s" % skill)
    if (
            contract.get("schema_version") != "1.0"
            or contract.get("contract_id") != "skill:" + skill):
        raise CapsuleError("machine contract identity is invalid for %s" % skill)
    identity = contract["identity"]
    if identity["name"] != skill:
        raise CapsuleError("machine contract name differs for %s" % skill)
    source_path = ROOT / identity["path"]
    source_raw = _read_bytes(source_path, identity["path"])
    if _sha256(source_raw) != identity["sha256"]:
        raise CapsuleError("Skill source hash differs for %s" % skill)
    try:
        source_text = source_raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CapsuleError("Skill source is not UTF-8: %s" % skill) from exc
    routing = contract["routing_contract"]
    inputs = contract["input_contract"]
    outputs = contract["output_contract"]
    handoff = contract["handoff_contract"]
    capsule_path = CAPSULE_DIR / ("%s.json" % skill)

    def projected_markdown(value, label):
        if value is None:
            return None
        if not isinstance(value, str):
            raise CapsuleError("%s projected prose is not text for %s" % (label, skill))
        return _rebase_projected_markdown(
            value, source_path, capsule_path
        )

    operational_markdown = projected_markdown(
        _operational_markdown(source_text), "operational_markdown"
    )
    runtime_reads = [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in contract["context_hints"]["bundle_references"]
        if item["requirement"] == "required"
    ]
    if runtime_reads != sorted(runtime_reads, key=lambda item: item["path"]):
        raise CapsuleError("runtime reads are not path-sorted for %s" % skill)
    capsule = {
        "$schema": "../skill-capsule.schema.json",
        "schema_version": "1.0",
        "capsule_id": "skill-capsule:" + skill,
        "identity": {
            "name": skill,
            "version": identity["version"],
            "discipline": identity["discipline"],
            "phase": identity["phase"],
            "class": identity["class"],
        },
        "routing": {
            "argument_hint": projected_markdown(
                inputs["argument_hint"], "argument_hint"
            ),
            "boundary": projected_markdown(routing["boundary"], "boundary"),
        },
        "execution": {
            "reads": projected_markdown(inputs["reads"], "reads"),
            "writes": projected_markdown(outputs["writes"], "writes"),
            "write_controls": _write_controls(outputs["clauses"]),
            "done_when": projected_markdown(
                contract["completion_contract"]["done_when"], "done_when"
            ),
            "operational_markdown": operational_markdown,
        },
        "runtime_reads": runtime_reads,
        "handoff": {
            "items": [
                {
                    "kind": item["kind"],
                    "condition": projected_markdown(
                        item["condition"], "handoff condition"
                    ),
                    "target_skills": item["target_skills"],
                    "text": projected_markdown(item["text"], "handoff text"),
                }
                for item in handoff["items"]
            ],
        },
        "policy": {
            "kernel": policy_ref,
            "always_on_overlays": list(ALWAYS_ON_OVERLAYS),
        },
        "provenance": {
            "generator": "generate-skill-capsules-v1",
            "source": {"path": identity["path"], "sha256": identity["sha256"]},
            "machine_contract": {
                "path": entry["contract_ref"],
                "sha256": entry["contract_sha256"],
            },
        },
    }
    return capsule


def render_all():
    contract_index_raw = _read_bytes(CONTRACT_INDEX, _relative(CONTRACT_INDEX))
    contract_index = _load_json(CONTRACT_INDEX, "skill contract index")
    entries = _contract_entry_map(contract_index)
    policy_raw = _read_bytes(POLICY_KERNEL, _relative(POLICY_KERNEL))
    policy_ref = _file_ref(POLICY_KERNEL, policy_raw)
    capsule_schema_raw = _read_bytes(CAPSULE_SCHEMA, _relative(CAPSULE_SCHEMA))
    rendered = {}
    index_entries = []
    for skill in sorted(entries):
        capsule = _build_capsule(skill, entries[skill], policy_ref)
        raw = _canonical_bytes(capsule)
        relative = "references/skill-capsules/%s.json" % skill
        rendered[relative] = raw
        index_entries.append({
            "skill": skill,
            "capsule_ref": relative,
            "capsule_sha256": _sha256(raw),
            "model_bytes": len(raw) + len(policy_raw),
        })
    index = {
        "$schema": "../skill-capsule-index.schema.json",
        "schema_version": "1.0",
        "capsule_count": 120,
        "capsule_schema": _file_ref(CAPSULE_SCHEMA, capsule_schema_raw),
        "policy_kernel": policy_ref,
        "source_contract_index": _file_ref(CONTRACT_INDEX, contract_index_raw),
        "capsules": index_entries,
    }
    rendered["references/skill-capsules/index.json"] = _canonical_bytes(index)
    return rendered


def _existing_generated_paths():
    if not CAPSULE_DIR.exists():
        return set()
    return {
        path.relative_to(ROOT).as_posix()
        for path in CAPSULE_DIR.glob("*.json")
        if path.is_file()
    }


def check(rendered):
    expected = set(rendered)
    existing = _existing_generated_paths()
    problems = []
    for relative in sorted(expected):
        path = ROOT / relative
        if not path.is_file():
            problems.append("missing %s" % relative)
        elif path.read_bytes() != rendered[relative]:
            problems.append("stale %s" % relative)
    for relative in sorted(existing - expected):
        problems.append("unexpected generated capsule %s" % relative)
    if problems:
        raise CapsuleError("; ".join(problems))


def write(rendered):
    # Replace individual generated files instead of swapping the directory.
    # Cloud-synced workspaces can interpret directory swaps as sync conflicts
    # and rename the canonical tree (for example, ``skill-capsules 2``).
    CAPSULE_DIR.mkdir(parents=True, exist_ok=True)
    expected = set(rendered)
    for relative, raw in rendered.items():
        destination = ROOT / relative
        temporary = destination.with_name(".%s.tmp" % destination.name)
        temporary.write_bytes(raw)
        temporary.replace(destination)
    for relative in sorted(_existing_generated_paths() - expected):
        (ROOT / relative).unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        rendered = render_all()
        if args.write:
            write(rendered)
            print("wrote %d model-facing skill capsules" % (len(rendered) - 1))
        else:
            check(rendered)
            print("skill capsules are current (%d skills)" % (len(rendered) - 1))
    except (CapsuleError, OSError) as exc:
        print("skill capsule generation failed: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
