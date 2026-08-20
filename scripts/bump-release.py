#!/usr/bin/env python3
"""Prepare or apply one narrow, transactional product release version cut.

Only current product bindings are changed. Historical changelog entries,
licensed-deviation ``since_version`` values, schema/protocol versions,
compatibility fixtures, and measured-at-version comments are deliberately
outside this transaction.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
TOP_VERSION_RE = re.compile(r'^version: *"([0-9]+\.[0-9]+\.[0-9]+)" *$', re.MULTILINE)
NAME_RE = re.compile(r"^name: *([a-z0-9][a-z0-9-]*) *$", re.MULTILINE)
METADATA_RE = re.compile(r"^metadata: *(.+)$", re.MULTILINE)
CURRENT_RELEASE_RE = re.compile(
    r"^\*\*Current release\*\*: `([0-9]+\.[0-9]+\.[0-9]+)` "
    r"\(([0-9]{4}-[0-9]{2}-[0-9]{2})\)\..*$",
    re.MULTILINE,
)
VERSION_ROW_RE = re.compile(
    r"^\| ([a-z0-9-]+) \| ([a-z-]+) \| "
    r"([0-9]+\.[0-9]+\.[0-9]+) \| ([0-9]{4}-[0-9]{2}-[0-9]{2}) \|$",
    re.MULTILINE,
)

CURRENT_SUMMARY = (
    "**AI Staff positioning.** The same 120 canonical skills, seven mandatory "
    "4×4 discipline loops, eight commands, framework IDs, routes, and state "
    "paths remain intact. The bundle now presents as an installable AI "
    "marketing staff: the named-bot roster (Grok Bot, Hermes Bot Mode) becomes "
    "a first-class install surface alongside the plugin and portable skills, "
    "the README leads vendor-neutral, and the chief bot handle shortens to "
    "`aaron-chief`. Existing Claude, npx skills, SkillHub, ClawHub, OpenClaw, "
    "and Hermes surfaces remain separate compatibility channels generated from "
    "the same canonical source."
)
CHANGELOG_BODY = """\
### v{version} — Agent Plugins v1 Portable Lite ({date})

All 120 canonical skills align to `{version}` together while the exact 7 ×
(4 phases × 4 skills) shape, TALE/SITE/ECHO/SEND/ROAS/STAR/RAMP acronym
symmetry, eight public commands, framework/veto IDs, registry keys, and user
state paths remain unchanged.

- **Published-package conformance.** A fourth release archive exposes the
  versioned Agent Plugins 1.0.0 `plugin.json` contract and exactly 120 immediate
  `skills/<name>/SKILL.md` children. The repository source layout remains the
  single canonical authoring tree; no committed mirror is introduced.
- **Strict Agent Skills projection.** Portable frontmatter contains only the
  standard field set, uses string-valued metadata, and removes platform listing
  extensions from the generated copy. Source frontmatter remains unchanged for
  existing registry and client publishers.
- **Contained static delivery.** Cross-skill and shared-reference links are
  deterministically rewritten into the package. Client runtimes, hooks,
  commands, connectors, persistence, and excluded paths degrade to a documented
  Portable Lite boundary instead of becoming broken or over-claimed behavior.
- **No implicit MCP authority.** The portable archive deliberately omits
  `mcp.json`; the 19 documented endpoints remain opt-in client configuration.
- **Reproducible provenance.** The official Agent Plugins schema, versioned spec
  identity, Agent Skills baseline, source-to-projection hashes, host profile, and
  capability ceiling are bound into validation and release manifests.
- **Compatibility preserved.** The existing Lite, Pro, and Governed archives,
  Claude commands and hooks, `npx skills`, SkillHub, ClawHub, OpenClaw, and
  Hermes publication routes remain supported and receive full regression
  coverage alongside the new portable asset.
"""


class BumpError(ValueError):
    """A failed precondition; no files may be written."""


def _read(path: Path) -> str:
    try:
        if path.is_symlink() or not path.is_file():
            raise BumpError("%s must be a regular non-symlink file" % path)
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BumpError("cannot read %s: %s" % (path, exc)) from exc


def _load_json(path: Path) -> tuple[dict, str]:
    text = _read(path)
    try:
        value = json.loads(text)
    except ValueError as exc:
        raise BumpError("cannot parse %s: %s" % (path, exc)) from exc
    if not isinstance(value, dict):
        raise BumpError("%s must contain a JSON object" % path)
    return value, text


def _json_text(value: dict) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def _canonical_inventory(catalog: dict) -> list[tuple[str, str, str]]:
    inventory: list[tuple[str, str, str]] = []
    disciplines = catalog.get("disciplines")
    if not isinstance(disciplines, dict):
        raise BumpError("system catalog disciplines must be an object")
    for discipline, spec in disciplines.items():
        phases = spec.get("phases") if isinstance(spec, dict) else None
        if not isinstance(phases, dict):
            raise BumpError("discipline %s has no phase inventory" % discipline)
        for phase, slugs in phases.items():
            if not isinstance(slugs, list):
                raise BumpError("discipline %s phase %s is invalid" % (discipline, phase))
            for slug in slugs:
                if not isinstance(slug, str):
                    raise BumpError("catalog contains a non-string skill slug")
                inventory.append(
                    (slug, phase, "%s/%s/%s/SKILL.md" % (discipline, phase, slug))
                )
    protocol = catalog.get("protocol")
    protocol_skills = protocol.get("skills") if isinstance(protocol, dict) else None
    if not isinstance(protocol_skills, list):
        raise BumpError("system catalog protocol skill inventory is invalid")
    inventory.extend(
        (slug, "protocol", "protocol/%s/SKILL.md" % slug)
        for slug in protocol_skills
    )
    names = [row[0] for row in inventory]
    paths = [row[2] for row in inventory]
    if len(inventory) != 120 or len(set(names)) != 120 or len(set(paths)) != 120:
        raise BumpError(
            "release transaction requires exactly 120 unique catalog skills; "
            "found %d rows, %d names, %d paths"
            % (len(inventory), len(set(names)), len(set(paths)))
        )
    return inventory


def _replace_skill(text: str, slug: str, target: str, relative: str) -> str:
    name = NAME_RE.search(text)
    top = TOP_VERSION_RE.search(text)
    metadata = METADATA_RE.search(text)
    if name is None or top is None or metadata is None:
        raise BumpError("%s lacks a parseable name/version/metadata line" % relative)
    if name.group(1) != slug:
        raise BumpError("%s name %s != catalog slug %s" % (relative, name.group(1), slug))
    try:
        metadata_value = json.loads(metadata.group(1))
    except ValueError as exc:
        raise BumpError("%s metadata is not strict single-line JSON: %s" % (relative, exc))
    if not isinstance(metadata_value, dict):
        raise BumpError("%s metadata must be an object" % relative)
    old_top = top.group(1)
    old_meta = metadata_value.get("version")
    if old_top != old_meta:
        raise BumpError(
            "%s version %s != metadata.version %r before bump"
            % (relative, old_top, old_meta)
        )
    updated = text[: top.start()] + 'version: "%s"' % target + text[top.end() :]
    metadata_after_top = METADATA_RE.search(updated)
    assert metadata_after_top is not None
    metadata_value["version"] = target
    metadata_line = "metadata: " + json.dumps(
        metadata_value, ensure_ascii=False, separators=(", ", ": ")
    )
    return (
        updated[: metadata_after_top.start()]
        + metadata_line
        + updated[metadata_after_top.end() :]
    )


def _replace_versions(
    text: str,
    inventory: list[tuple[str, str, str]],
    target: str,
    date: str,
) -> str:
    current = CURRENT_RELEASE_RE.search(text)
    if current is None:
        raise BumpError("VERSIONS.md has no parseable dated Current release line")
    current_line = (
        "**Current release**: `%s` (%s). %s" % (target, date, CURRENT_SUMMARY)
    )
    updated = text[: current.start()] + current_line + text[current.end() :]
    rows = VERSION_ROW_RE.findall(updated)
    row_names = [row[0] for row in rows]
    expected_names = [row[0] for row in inventory]
    if len(rows) != 120 or set(row_names) != set(expected_names) or len(set(row_names)) != 120:
        raise BumpError(
            "VERSIONS.md must contain exactly one row for every canonical skill"
        )
    def replace_row(match: re.Match[str]) -> str:
        slug, category, _old_version, _old_date = match.groups()
        return "| %s | %s | %s | %s |" % (slug, category, target, date)

    updated = VERSION_ROW_RE.sub(replace_row, updated)
    heading = "### v%s " % target
    if heading not in updated:
        marker = "## Changelog\n"
        if updated.count(marker) != 1:
            raise BumpError("VERSIONS.md must contain one Changelog heading")
        body = CHANGELOG_BODY.format(version=target, date=date)
        updated = updated.replace(marker, marker + "\n" + body + "\n", 1)
    return updated


def _replace_current_text(
    text: str,
    replacements: list[tuple[str, str]],
    relative: str,
) -> str:
    updated = text
    for old, new in replacements:
        count = updated.count(old)
        if count != 1:
            raise BumpError(
                "%s expected one current binding %r; found %d" % (relative, old, count)
            )
        updated = updated.replace(old, new, 1)
    return updated


def prepare(root: Path, target: str, date: str) -> tuple[dict[Path, str], dict]:
    root = root.resolve()
    if not SEMVER_RE.fullmatch(target):
        raise BumpError("--to must be a numeric semver string")
    if not DATE_RE.fullmatch(date):
        raise BumpError("--date must be YYYY-MM-DD")

    system_path = root / "references" / "system-catalog.json"
    system, system_before = _load_json(system_path)
    current = system.get("bundle_version")
    architecture = system.get("architecture_version")
    if not isinstance(current, str) or not SEMVER_RE.fullmatch(current):
        raise BumpError("system catalog bundle_version is invalid")
    if architecture != current:
        raise BumpError(
            "system catalog architecture_version %r != bundle_version %r before bump"
            % (architecture, current)
        )
    inventory = _canonical_inventory(system)
    changes: dict[Path, str] = {}

    system["bundle_version"] = target
    system["architecture_version"] = target
    changes[system_path] = _json_text(system)

    framework_path = root / "references" / "framework-catalog.json"
    framework, _ = _load_json(framework_path)
    if framework.get("catalog_version") != current:
        raise BumpError("framework catalog is not aligned to current bundle")
    framework["catalog_version"] = target
    changes[framework_path] = _json_text(framework)

    graph_path = root / "references" / "workflow-graph.source.json"
    graph, _ = _load_json(graph_path)
    if graph.get("catalog_version") != current:
        raise BumpError("workflow graph source is not aligned to current bundle")
    graph["catalog_version"] = target
    changes[graph_path] = _json_text(graph)

    audit_path = root / "references" / "audit-artifact.schema.json"
    audit, _ = _load_json(audit_path)
    catalog_node = audit.get("properties", {}).get("catalog_version")
    if not isinstance(catalog_node, dict) or catalog_node.get("const") != current:
        raise BumpError("audit artifact current catalog const is not aligned")
    catalog_node["const"] = target
    changes[audit_path] = _json_text(audit)

    for slug, _category, relative in inventory:
        path = root / relative
        changes[path] = _replace_skill(_read(path), slug, target, relative)

    versions_path = root / "VERSIONS.md"
    changes[versions_path] = _replace_versions(
        _read(versions_path), inventory, target, date
    )

    runbook_path = root / "references" / "auditor-runbook.md"
    changes[runbook_path] = _replace_current_text(
        _read(runbook_path),
        [("catalog_version: %s" % current, "catalog_version: %s" % target)],
        "references/auditor-runbook.md",
    )

    submissions_path = root / "docs" / "registry-submissions.md"
    changes[submissions_path] = _replace_current_text(
        _read(submissions_path),
        [
            ("· v%s ·" % current, "· v%s ·" % target),
            ("Latest release: v%s." % current, "Latest release: v%s." % target),
            ("bundle %s;" % current, "bundle %s;" % target),
        ],
        "docs/registry-submissions.md",
    )

    skillhub_path = root / "scripts" / "publish-skillhub.sh"
    changes[skillhub_path] = _replace_current_text(
        _read(skillhub_path),
        [
            (
                '--changelog "v%s 更新说明"' % current,
                '--changelog "v%s 更新说明"' % target,
            )
        ],
        "scripts/publish-skillhub.sh",
    )

    effective: dict[Path, str] = {}
    summaries: list[dict] = []
    for path, new_text in sorted(changes.items(), key=lambda item: str(item[0])):
        old_text = _read(path)
        if old_text == new_text:
            continue
        effective[path] = new_text
        summaries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "before_sha256": hashlib.sha256(old_text.encode("utf-8")).hexdigest(),
                "after_sha256": hashlib.sha256(new_text.encode("utf-8")).hexdigest(),
                "before_bytes": len(old_text.encode("utf-8")),
                "after_bytes": len(new_text.encode("utf-8")),
            }
        )
    summary = {
        "schema_version": "1.0",
        "from_version": current,
        "to_version": target,
        "release_date": date,
        "canonical_skill_count": len(inventory),
        "changed_file_count": len(effective),
        "changes": summaries,
    }
    # Keep this local variable referenced: it makes an accidental future
    # in-place mutation of the loaded source visible during review/tests.
    if not system_before.endswith("\n"):
        raise BumpError("system catalog must end with a newline")
    return effective, summary


def _atomic_write(path: Path, text: str) -> None:
    mode = stat.S_IMODE(path.stat().st_mode)
    descriptor, temporary = tempfile.mkstemp(
        prefix=".%s." % path.name,
        suffix=".release-bump",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
    except Exception:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def apply_changes(changes: dict[Path, str]) -> None:
    # Every source, parse, identity, and target check has already completed in
    # ``prepare``. Each replacement is atomic within its directory.
    for path, text in sorted(changes.items(), key=lambda item: str(item[0])):
        _atomic_write(path, text)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", required=True, help="Target numeric semver")
    parser.add_argument("--date", required=True, help="Release date YYYY-MM-DD")
    parser.add_argument(
        "--align-all-skills",
        action="store_true",
        help="Required acknowledgement that all 120 skills move together",
    )
    parser.add_argument("--write", action="store_true", help="Apply after full validation")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if not args.align_all_skills:
            raise BumpError("--align-all-skills is required for this transaction")
        changes, summary = prepare(args.root, args.to, args.date)
        if args.write:
            apply_changes(changes)
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            action = "applied" if args.write else "dry-run"
            print(
                "%s: %s -> %s on %s; %d canonical skills; %d files change"
                % (
                    action,
                    summary["from_version"],
                    summary["to_version"],
                    summary["release_date"],
                    summary["canonical_skill_count"],
                    summary["changed_file_count"],
                )
            )
            for item in summary["changes"]:
                print(
                    "  %s  %s -> %s"
                    % (
                        item["path"],
                        item["before_sha256"][:12],
                        item["after_sha256"][:12],
                    )
                )
        return 0
    except (BumpError, OSError) as exc:
        print("release bump refused: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
