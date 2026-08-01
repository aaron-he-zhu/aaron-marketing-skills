#!/usr/bin/env python3
"""Generate/check immutable standalone auditor runtime bundles.

Each auditor ships one local ``references/auditor-runtime.md`` assembled from
the typed framework slice and the exact repository sources declared in
``references/system-catalog.json``. This removes mutable-branch fallbacks while
keeping the root references authoritative in repository mode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import sys


ROOT = Path(__file__).resolve().parents[1]
SYSTEM_CATALOG = ROOT / "references" / "system-catalog.json"
FRAMEWORK_CATALOG = ROOT / "references" / "framework-catalog.json"
OUTPUT_NAME = "auditor-runtime.md"


class GenerationError(ValueError):
    pass


ITEM_ID = re.compile(r"([A-Za-z]+[0-9]{1,2})$")


def expected_item_dimensions(framework):
    expected = {}
    for dimension, spec in framework.get("dimensions", {}).items():
        try:
            prefix = spec["item_prefix"]
            count = spec["item_count"]
            width = spec["id_width"]
        except (KeyError, TypeError) as exc:
            raise GenerationError("framework dimension item identity is incomplete") from exc
        if (not isinstance(prefix, str) or not prefix
                or not isinstance(count, int) or isinstance(count, bool) or count < 1
                or not isinstance(width, int) or isinstance(width, bool) or width < 1):
            raise GenerationError("framework dimension item identity is invalid")
        for item_number in range(1, count + 1):
            item_id = "%s%s" % (prefix, str(item_number).zfill(width))
            if item_id in expected:
                raise GenerationError("framework contains duplicate item identity: %s" % item_id)
            expected[item_id] = dimension
    if not expected:
        raise GenerationError("framework contains no item identities")
    return expected


def _clean_cell(value):
    return value.strip().strip("`").strip()


def parse_item_definitions(framework_name, framework, benchmark_path):
    """Compile complete human item anchors into a deterministic typed slice."""
    expected = expected_item_dimensions(framework)
    try:
        text = benchmark_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise GenerationError("cannot read framework benchmark: %s" % exc) from exc
    parsed = {}

    # CORE-EEAT, CITE, STAR, ROAS, and SEND declare item tables. Ignore later
    # qualified veto tables: their first cell is not an unqualified expected ID.
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        if not cells:
            continue
        raw_item_id = cells[0].replace("`", "").replace("⛔", "").strip()
        match = ITEM_ID.fullmatch(raw_item_id)
        if match is None or match.group(1) not in expected or len(cells) < 2:
            continue
        item_id = match.group(1)
        dimension = expected[item_id]
        dimension_name = framework["dimensions"][dimension]["name"]
        middle = []
        for cell in cells[1:-1]:
            if cell in {dimension, dimension_name}:
                continue
            if any(marker in cell for marker in ("GEO", "SEO", "Dual")):
                continue
            middle.append(cell)
        parsed.setdefault(item_id, {
            "dimension": dimension,
            "name": middle[0] if middle else None,
            "criterion": cells[-1],
        })

    # RAMP, ECHO, and TALE use compact stable-anchor paragraphs. First
    # occurrence wins so later explanatory prose such as "`T1` does not..."
    # cannot replace the canonical anchor.
    marker = "## Stable Item Anchors"
    if marker in text:
        anchor_section = text.split(marker, 1)[1].split("Per item:", 1)[0]
        for match in re.finditer(r"`([A-Za-z]+[0-9]{1,2})`\s+([^·\n]+)", anchor_section):
            item_id = match.group(1)
            if item_id not in expected:
                continue
            parsed.setdefault(item_id, {
                "dimension": expected[item_id],
                "name": None,
                "criterion": match.group(2).strip().rstrip("."),
            })

    missing = sorted(set(expected) - set(parsed))
    extra = sorted(set(parsed) - set(expected))
    if missing or extra:
        raise GenerationError(
            "%s item definitions differ from the typed catalog (missing=%s extra=%s)"
            % (framework_name, missing, extra)
        )
    veto_items = set(framework.get("veto_items", []))
    if not veto_items.issubset(expected):
        raise GenerationError("%s veto items are absent from item identity" % framework_name)
    policies = framework.get("item_policies", {})
    if not isinstance(policies, dict) or not set(policies).issubset(expected):
        raise GenerationError("%s item policies are absent from item identity" % framework_name)
    compiled = {}
    for item_id, dimension in expected.items():
        definition = parsed[item_id]
        if definition["dimension"] != dimension or not definition["criterion"]:
            raise GenerationError("%s item definition is invalid: %s" % (framework_name, item_id))
        policy = dict(policies.get(item_id, {}))
        if "veto" in policy and bool(policy["veto"]) != (item_id in veto_items):
            raise GenerationError("%s veto policy differs for %s" % (framework_name, item_id))
        compiled[item_id] = {
            "qualified_id": "%s-%s" % (framework_name, item_id),
            "dimension": dimension,
            "name": definition["name"],
            "criterion": definition["criterion"],
            "veto": item_id in veto_items,
            "policy": policy,
        }
    return compiled


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise GenerationError("cannot load %s: %s" % (path, exc)) from exc


def safe_source(relative):
    path = (ROOT / relative).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GenerationError("runtime source escapes repository: %s" % relative) from exc
    if not path.is_file():
        raise GenerationError("runtime source is missing: %s" % relative)
    return path


def build_bundle(auditor, framework_catalog):
    framework_name = auditor["framework"]
    framework = framework_catalog.get("frameworks", {}).get(framework_name)
    if framework is None:
        raise GenerationError("unknown framework for %s: %s" % (auditor["skill"], framework_name))
    source_paths = [(relative, safe_source(relative)) for relative in auditor["runtime_sources"]]
    benchmark_path = safe_source(framework["source"])
    if framework["source"] not in auditor["runtime_sources"]:
        raise GenerationError(
            "%s benchmark is absent from its declared runtime sources" % framework_name
        )
    items = parse_item_definitions(framework_name, framework, benchmark_path)
    snapshot = {
        "catalog_version": framework_catalog["catalog_version"],
        "semantics": framework_catalog["semantics"],
        "frameworks": {
            framework_name: {
                **framework,
                "items": items,
            },
        },
        "standalone_observation_contract": {
            "item_states": ["pass", "partial", "fail", "unknown", "na"],
            "evidence_types": [
                "measured", "user-provided", "calculated", "estimated", "proxy"
            ],
            "result": {
                "status": ["NEEDS_INPUT", "BLOCKED"],
                "verdict": "UNDECIDED",
                "score_state": "NOT_SCORED",
                "score_confidence": "not_scored",
            },
        },
    }
    snapshot_text = json.dumps(snapshot, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    digest = hashlib.sha256()
    digest.update(snapshot_text.encode("utf-8"))
    for relative, path in source_paths:
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    lines = [
        "<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->",
        "",
        "# Standalone Auditor Runtime",
        "",
        "- **Runtime version:** 3.0.0",
        "- **Catalog version:** %s" % framework_catalog["catalog_version"],
        "- **Framework:** %s" % framework_name,
        "- **Auditor:** %s" % auditor["skill"],
        "- **Complete item definitions:** %d" % len(items),
        "- **Source digest:** `sha256:%s`" % digest.hexdigest(),
        "",
        "This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.",
        "",
        "## Typed Framework Snapshot",
        "",
        "```json",
        snapshot_text.rstrip("\n"),
        "```",
    ]
    lines.extend([
        "",
        "## Standalone Execution Policy",
        "",
        "1. Select exactly one declared profile from the typed snapshot and record it with the catalog version and source digest above.",
        "2. Collect one state per applicable item using the run-schema vocabulary: `pass`, `partial`, `fail`, `na`, or `unknown` — the same states the root scorer replays later. Every non-unknown state needs evidence; never convert missing evidence into a pass.",
        "3. Record veto observations by their qualified framework item IDs, but do not calculate dimension, raw, capped, or final scores without the root deterministic scorer.",
        "4. Return `status: NEEDS_INPUT` or `status: BLOCKED` with `verdict: UNDECIDED`, `score_state: NOT_SCORED`, and `score_confidence: not_scored`. Clearly identify the unavailable root runtime as the reason.",
        "5. Do not write under `memory/audits/`, mutate registries, or claim a publish/ship decision. Offer the observation set for later execution in a full plugin or repository install.",
        "6. Do not search parent directories, accept an unverified runtime root, download repository files, or hand-calculate a substitute score.",
        "",
        "The complete item definitions above are compiled from the authoritative benchmark. The source digest binds this compact fallback to the runbook, scoring semantics, benchmark, run schema, and artifact schema; those maintenance documents remain repository-only and are not misrepresented as separately bundled files.",
    ])
    lines.extend(["", "---", "", "End of generated standalone runtime.", ""])
    return "\n".join(lines).encode("utf-8")


def output_path(auditor):
    skill_dir = (ROOT / auditor["path"]).resolve()
    try:
        skill_dir.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise GenerationError("auditor path escapes repository") from exc
    if not (skill_dir / "SKILL.md").is_file():
        raise GenerationError("auditor skill path is invalid: %s" % auditor["path"])
    return skill_dir / "references" / OUTPUT_NAME


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
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
    mode.add_argument("--write", action="store_true", help="Regenerate all eight bundles.")
    mode.add_argument("--check", action="store_true", help="Fail if a bundle is missing or stale.")
    args = parser.parse_args(argv)
    try:
        system = load_json(SYSTEM_CATALOG)
        frameworks = load_json(FRAMEWORK_CATALOG)
        auditors = system.get("auditors", [])
        if len(auditors) != system.get("counts", {}).get("auditors"):
            raise GenerationError("system catalog auditor count is inconsistent")
        stale = []
        for auditor in auditors:
            path = output_path(auditor)
            expected = build_bundle(auditor, frameworks)
            if args.write:
                atomic_write(path, expected)
                print("wrote %s" % path.relative_to(ROOT))
            elif not path.is_file() or path.read_bytes() != expected:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            raise GenerationError(
                "standalone auditor runtime bundle(s) missing/stale: %s; run with --write"
                % ", ".join(stale)
            )
    except GenerationError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 1
    print("standalone auditor runtime bundles %s (%d/%d)" % ("generated" if args.write else "current", len(auditors), len(auditors)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
