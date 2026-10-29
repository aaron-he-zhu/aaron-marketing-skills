#!/usr/bin/env python3
"""Generate/check immutable standalone auditor runtime bundles.

Each auditor ships one local ``references/auditor-runtime.md`` assembled from
the typed framework slice and the exact repository sources declared in
``references/system-catalog.json``. This removes mutable-branch fallbacks while
keeping the root references authoritative in repository mode.
"""
from __future__ import annotations

import argparse
from decimal import Decimal
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
    begin, end = "<!-- AUDITOR-ITEMS:BEGIN -->", "<!-- AUDITOR-ITEMS:END -->"
    if text.count(begin) != 1 or text.count(end) != 1:
        raise GenerationError("%s needs one authoritative item-table block" % framework_name)
    start, finish = text.index(begin) + len(begin), text.index(end)
    if finish <= start:
        raise GenerationError("%s item-table markers are reversed" % framework_name)
    parsed = {}
    header = None
    for line in text[start:finish].splitlines():
        if not line.startswith("|"):
            continue
        cells = [_clean_cell(cell) for cell in line.strip().strip("|").split("|")]
        raw_item_id = cells[0].replace("⛔", "").replace("`", "").strip()
        if raw_item_id == "ID":
            allowed = {"ID", "Dim", "Dimension", "Check Item", "Name", "Priority",
                       "Criterion", "One-Line Standard", "One-Line Diagnostic Anchor"}
            if (len(cells) < 2 or len(set(cells)) != len(cells)
                    or not set(cells).issubset(allowed)
                    or cells[-1] not in {"Criterion", "One-Line Standard", "One-Line Diagnostic Anchor"}
                    or {"Dim", "Dimension"}.issubset(cells)
                    or {"Check Item", "Name"}.issubset(cells)):
                raise GenerationError("%s has an invalid item-table header" % framework_name)
            header = cells
            continue
        if all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
            if header is None or len(cells) != len(header):
                raise GenerationError("%s has an invalid item-table separator" % framework_name)
            continue
        if header is None or len(cells) != len(header):
            raise GenerationError("%s item-table columns differ from its header: %s" % (framework_name, raw_item_id))
        match = ITEM_ID.fullmatch(raw_item_id)
        if match is None or raw_item_id not in expected:
            raise GenerationError("%s has an invalid item-table row: %s" % (framework_name, raw_item_id))
        item_id = match.group(1)
        if item_id in parsed:
            raise GenerationError("%s has duplicate authoritative item: %s" % (framework_name, item_id))
        dimension = expected[item_id]
        dimension_name = framework["dimensions"][dimension]["name"]
        row = dict(zip(header, cells))
        declared_dimension = row.get("Dim", row.get("Dimension"))
        if declared_dimension is not None and declared_dimension not in {dimension, dimension_name}:
            raise GenerationError("%s item dimension differs from the typed catalog: %s" % (framework_name, item_id))
        parsed[item_id] = {
            "dimension": dimension,
            "name": row.get("Check Item", row.get("Name")),
            "criterion": cells[-1],
        }

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


def build_bundle(auditor, framework_catalog, source_overrides=None):
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
        digest.update((source_overrides or {}).get(relative, path.read_bytes()))
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
        "2. Collect one state per applicable item using the run-schema vocabulary: `pass`, `partial`, `fail`, `na`, or `unknown` — the same states the root scorer replays later. Observed pass/partial/fail states need evidence. Unknown needs a gap reason; catalog-authorized na needs a reason and no evidence. Never convert missing evidence into a pass.",
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
            # These are public source/projection files, independent of the
            # maintainer's restrictive process umask.
            os.fchmod(handle.fileno(), 0o644)
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


SHARED_KEYS = ("activation", "result-header")
RUNBOOK_REF = "references/auditor-runbook.md"


def _marked_body(source, begin, end):
    if source.count(begin) != 1 or source.count(end) != 1:
        raise GenerationError("expected one marker pair: %s" % begin)
    start = source.index(begin) + len(begin)
    finish = source.index(end)
    if finish <= start:
        raise GenerationError("reversed marker pair: %s" % begin)
    return source[start:finish].strip()


def render_shared_skill(auditor, runbook_text):
    path = safe_source(auditor["path"] + "/SKILL.md")
    source = path.read_text(encoding="utf-8")
    for key in SHARED_KEYS:
        begin = "<!-- GENERATED:BEGIN auditor-shared:%s -->" % key
        end = "<!-- GENERATED:END auditor-shared:%s -->" % key
        _marked_body(source, begin, end)
        body = _marked_body(
            runbook_text,
            "<!-- AUTHORING:BEGIN auditor-shared:%s -->" % key,
            "<!-- AUTHORING:END auditor-shared:%s -->" % key,
        )
        start = source.index(begin) + len(begin)
        finish = source.index(end)
        source = source[:start] + "\n" + body + "\n" + source[finish:]
    return path, source.encode("utf-8")


def render_policy_runbook(runbook_text, frameworks):
    begin = "<!-- GENERATED:BEGIN auditor-policy:vetoes -->"
    end = "<!-- GENERATED:END auditor-policy:vetoes -->"
    _marked_body(runbook_text, begin, end)
    rows = ["| Framework | Veto IDs |", "|---|---|"]
    for name, framework in frameworks["frameworks"].items():
        rows.append("| %s | %s |" % (
            name, ", ".join("`%s-%s`" % (name, item)
                            for item in framework["veto_items"]),
        ))
    start = runbook_text.index(begin) + len(begin)
    finish = runbook_text.index(end)
    return runbook_text[:start] + "\n\n" + "\n".join(rows) + "\n\n" + runbook_text[finish:]


def render_profile_policy(benchmark_text, framework):
    """Project policy values; domain guidance stays authored outside markers."""
    begin = "<!-- GENERATED:BEGIN auditor-policy:profiles -->"
    end = "<!-- GENERATED:END auditor-policy:profiles -->"
    _marked_body(benchmark_text, begin, end)
    rows = ["| Profile | Dimension weights | Context match | Item subset |",
            "|---|---|---|---|"]
    for profile, spec in framework['profiles'].items():
        weights = []
        for dimension, weight in spec['dimensions'].items():
            percentage = format(Decimal(str(weight)) * 100, 'f')
            if '.' in percentage:
                percentage = percentage.rstrip('0').rstrip('.')
            weights.append('%s %s%%' % (dimension, percentage))
        context = json.dumps(spec['context_equals'], ensure_ascii=False, sort_keys=True) if spec.get('context_equals') else 'none'
        subset = '; '.join('%s: %s' % (kind, json.dumps(spec[kind], ensure_ascii=False, sort_keys=True))
                           for kind in ('include_items', 'exclude_items') if kind in spec) or 'all items in included dimensions'
        rows.append('| `%s` | %s | %s | %s |' % (
            profile, ' · '.join(weights), context.replace('|', '\\|'), subset.replace('|', '\\|'),
        ))
    start = benchmark_text.index(begin) + len(begin)
    finish = benchmark_text.index(end)
    return benchmark_text[:start] + '\n\n' + '\n'.join(rows) + '\n\n' + benchmark_text[finish:]


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
        runbook = safe_source(RUNBOOK_REF)
        expected_runbook = render_policy_runbook(runbook.read_text(encoding="utf-8"), frameworks)
        outputs = {runbook: expected_runbook.encode("utf-8")}
        for framework in frameworks['frameworks'].values():
            benchmark = safe_source(framework['source'])
            outputs[benchmark] = render_profile_policy(
                benchmark.read_text(encoding='utf-8'), framework,
            ).encode('utf-8')
        for auditor in auditors:
            path, content = render_shared_skill(auditor, expected_runbook)
            outputs[path] = content
        overrides = {str(path.relative_to(ROOT)): content for path, content in outputs.items()}
        for auditor in auditors:
            outputs[output_path(auditor)] = build_bundle(auditor, frameworks, overrides)
        stale = []
        for path, expected in outputs.items():
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
