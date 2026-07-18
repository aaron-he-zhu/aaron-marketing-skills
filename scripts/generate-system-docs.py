#!/usr/bin/env python3
"""Generate/check the human system map from the typed system catalog."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import sys


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "system-catalog.json"
OUTPUT_PATH = ROOT / "docs" / "system-architecture.md"


def load_catalog():
    try:
        with CATALOG_PATH.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise ValueError("cannot load system catalog: %s" % exc) from exc


def render(catalog):
    canonical = json.dumps(catalog, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    lines = [
        "<!-- GENERATED FILE: run `python3 scripts/generate-system-docs.py --write`; do not edit. -->",
        "",
        "# System Architecture",
        "",
        "This is the generated human view of [`references/system-catalog.json`](../references/system-catalog.json). The JSON catalog is authoritative.",
        "",
        "- Architecture contract: `%s`" % catalog["architecture_version"],
        "- Bundle version: `%s`" % catalog["bundle_version"],
        "- Catalog digest: `sha256:%s`" % digest,
        "- Shape: **%d discipline skills across %d disciplines + %d protocol skills = %d skills; %d commands**"
        % (
            catalog["counts"]["discipline_skills"], catalog["counts"]["disciplines"],
            catalog["counts"]["protocol_skills"], catalog["counts"]["total_skills"],
            catalog["counts"]["commands"],
        ),
        "",
        "## Four Layers",
        "",
        "| Layer | Purpose | Disciplines | Cadence |",
        "|---|---|---|---|",
    ]
    for layer in catalog["layers"]:
        lines.append(
            "| **%s · %s** | %s | %s | %s |"
            % (layer["id"], layer["name"], layer["purpose"], " → ".join(layer["disciplines"]), layer["cadence"])
        )
    lines.extend([
        "",
        "Canonical logical order: **%s**." % " → ".join(catalog["logical_order"]),
        "",
        "## Discipline Topology",
        "",
        "| Discipline | Layer | Framework | Loop | Skills |",
        "|---|---|---|---|---:|",
    ])
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            continue
        spec = catalog["disciplines"][discipline]
        count = sum(len(spec["phases"][phase]) for phase in spec["phase_order"])
        lines.append(
            "| **%s** | %s | %s | %s | %d |"
            % (spec["display_name"], spec["layer"], " + ".join(spec["frameworks"]), spec["loop"], count)
        )
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            continue
        spec = catalog["disciplines"][discipline]
        lines.extend(["", "### %s" % spec["display_name"], ""])
        for phase in spec["phase_order"]:
            links = [
                "[`%s`](../%s/%s/%s/SKILL.md)" % (slug, discipline, phase, slug)
                for slug in spec["phases"][phase]
            ]
            lines.append("- **%s:** %s" % (phase, " · ".join(links)))
    lines.extend([
        "",
        "## Protocol Layer",
        "",
        "The protocol layer contains %d skills: %s."
        % (
            len(catalog["protocol"]["skills"]),
            " · ".join(
                "[`%s`](../protocol/%s/SKILL.md)" % (slug, slug)
                for slug in catalog["protocol"]["skills"]
            ),
        ),
        "",
        "### Truth Registries",
        "",
        "| Registry | Owner | Canonical stream | Projection | State machine |",
        "|---|---|---|---|---|",
    ])
    for registry in catalog["registries"]:
        machine = registry.get("state_machine")
        state_text = "—"
        if machine:
            edges = []
            for source, targets in machine["transitions"].items():
                edges.append("%s→%s" % (source, "/".join(targets) if targets else "terminal"))
            state_text = "initial %s; %s" % (machine["initial"], ", ".join(edges))
        lines.append(
            "| `%s` | [`%s`](../protocol/%s/SKILL.md) | `%s` | `%s` | %s |"
            % (
                registry["key"], registry["owner"], registry["owner"], registry["stream"],
                registry["projection"], state_text,
            )
        )
    lines.extend([
        "",
        "## Auditor Gates",
        "",
        "| Auditor | Framework | Exclusive sink | Standalone contract |",
        "|---|---|---|---|",
    ])
    for auditor in catalog["auditors"]:
        lines.append(
            "| [`%s`](../%s/SKILL.md) | %s | `%s` | generated `references/auditor-runtime.md` |"
            % (auditor["skill"], auditor["path"], auditor["framework"], auditor["sink"])
        )
    dependency = catalog["l1_dependency"]
    lines.extend([
        "",
        "## L1 Dependency",
        "",
        "The seven core downstream builders must carry `%s`; `dependency_status` is exactly `%s`."
        % ("`, `".join(dependency["required_fields"]), " | ".join(dependency["dependency_status_values"])),
        "",
    ])
    lines.extend(
        "- [`%s`](../%s/SKILL.md)" % (path.rsplit("/", 1)[-1], path)
        for path in dependency["builders"]
    )
    symmetry = catalog["symmetry"]
    deviations_by_scope = {}
    for deviation in symmetry["deviations"]:
        deviations_by_scope.setdefault(deviation["scope"], []).append(deviation["id"])
    surface_by_gate = {auditor["skill"]: auditor["score_surface"] for auditor in catalog["auditors"]}
    lines.extend([
        "",
        "## Symmetry Contract",
        "",
        "Every discipline satisfies each column or cites a licensed deviation (see below);"
        " `check-architecture.py` enforces conform-or-declared and fails stale deviations.",
        "",
        "| Discipline | Loop | Command | Registry | Gate(s) | Score surface |",
        "|---|---|---|---|---|---|",
    ])
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            continue
        spec = catalog["disciplines"][discipline]
        command = spec["command"]
        command_cell = "`/%s --phase %s`" % (command["name"], "\\|".join(command["values"]))
        alias = deviations_by_scope.get("command:%s" % command["name"])
        if alias:
            command_cell += " (%s)" % ", ".join(alias)
        registry_cell = "`%s`" % spec["registry"]
        view_deviation = deviations_by_scope.get("registry:%s" % spec["registry"])
        if view_deviation:
            registry_cell += " (%s)" % ", ".join(view_deviation)
        surfaces = []
        for gate in spec["gates"]:
            surface = surface_by_gate[gate]
            surfaces.append(
                surface["name"] and "%s (%s)" % (surface["name"], surface["rollup"])
                or "profiles-only"
            )
        lines.append(
            "| **%s** | %s (%s) | %s | %s | %s | %s |"
            % (
                spec["display_name"], spec["loop_name"], spec["loop"], command_cell,
                registry_cell, " · ".join("`%s`" % gate for gate in spec["gates"]),
                " · ".join(surfaces),
            )
        )
    lines.extend([
        "",
        "### Licensed Deviations",
        "",
        "| ID | Rule | Scope | Since | Rationale |",
        "|---|---|---|---|---|",
    ])
    for deviation in symmetry["deviations"]:
        rationale = deviation["rationale"]
        if deviation.get("source_doc"):
            rationale += " (source: `%s`)" % deviation["source_doc"]
        lines.append(
            "| `%s` | `%s` | `%s` | %s | %s |"
            % (
                deviation["id"], deviation["rule"], deviation["scope"],
                deviation["since_version"], rationale,
            )
        )
    lines.extend([
        "",
        "## Distribution Profiles",
        "",
        "| Profile | Shared root references | Executable runtime | Auditor contract |",
        "|---|---|---|---|",
    ])
    for name, profile in catalog["distribution_profiles"].items():
        lines.append(
            "| `%s` | %s | %s | %s |"
            % (name, profile["shared_references"], profile["executable_runtime"], profile["auditor_contract"])
        )
    lines.extend(["", "Generated from the typed catalog; edit the JSON source and regenerate.", ""])
    return "\n".join(str(line) for line in lines).encode("utf-8")


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        if path.exists():
            os.fchmod(fd, path.stat().st_mode & 0o777)
        else:
            os.fchmod(fd, 0o644)
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        expected = render(load_catalog())
        if args.write:
            atomic_write(OUTPUT_PATH, expected)
            print("wrote %s" % OUTPUT_PATH.relative_to(ROOT))
            return 0
        if not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_bytes() != expected:
            raise ValueError("generated system architecture is missing or stale; run with --write")
    except (OSError, ValueError, KeyError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("generated system architecture is current")
    return 0


if __name__ == "__main__":
    sys.exit(main())
