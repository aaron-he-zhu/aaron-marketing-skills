#!/usr/bin/env python3
"""Generate bounded runtime routing shards from the authoritative case source.

The source remains useful to structural eval tooling, while hosts only need the
small generated index plus one to three relevant shards.  Shard names are not a
second hand-maintained discipline inventory: the legal set comes from the typed
system catalog, with one additional cross-discipline disambiguation shard.

Usage:
  python3 scripts/generate-auto-routing-shards.py --write
  python3 scripts/generate-auto-routing-shards.py --check
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = Path("evals/auto-routing-scenarios.source.md")
CATALOG_REL = Path("references/system-catalog.json")
INDEX_REL = Path("references/auto-routing-scenarios.md")
SHARD_DIR_REL = Path("references/auto-routing")
MARKER_RE = re.compile(r"^<!-- auto-routing-shard: ([a-z0-9-]+) -->$")
CASE_RE = re.compile(r'^\s*-\s*\{id:\s*"([^"]+)"')
CROSS_SHARD = "cross-discipline"


class SourceError(ValueError):
    """The authoritative routing source cannot be projected safely."""


def _catalog_disciplines(root: Path) -> list[str]:
    path = root / CATALOG_REL
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
        disciplines = catalog["disciplines"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SourceError("cannot read disciplines from %s: %s" % (CATALOG_REL, exc)) from exc
    if not isinstance(disciplines, dict) or not disciplines:
        raise SourceError("%s has no non-empty disciplines object" % CATALOG_REL)
    invalid = sorted(name for name in disciplines if not re.fullmatch(r"[a-z0-9-]+", name))
    if invalid:
        raise SourceError("catalog has invalid discipline names: %s" % ", ".join(invalid))
    return list(disciplines)


def parse_source(root: Path = ROOT) -> tuple[list[str], dict[str, str], dict[str, list[str]]]:
    """Return marker order, section bodies, and case IDs after fail-closed lint."""
    path = root / SOURCE_REL
    try:
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    except OSError as exc:
        raise SourceError("cannot read %s: %s" % (SOURCE_REL, exc)) from exc

    order: list[str] = []
    starts: list[tuple[str, int, int]] = []
    for line_number, line in enumerate(lines, 1):
        marker = MARKER_RE.fullmatch(line.rstrip("\r\n"))
        if marker:
            name = marker.group(1)
            if name in order:
                raise SourceError("%s:%d duplicates shard marker %r" % (SOURCE_REL, line_number, name))
            order.append(name)
            starts.append((name, line_number, line_number))
        elif CASE_RE.match(line) and not starts:
            raise SourceError("%s:%d has a case before the first shard marker" % (SOURCE_REL, line_number))

    legal_disciplines = _catalog_disciplines(root)
    legal = set(legal_disciplines) | {CROSS_SHARD}
    missing = sorted(legal - set(order))
    unknown = sorted(set(order) - legal)
    if missing or unknown:
        details = []
        if missing:
            details.append("missing markers: %s" % ", ".join(missing))
        if unknown:
            details.append("unknown markers: %s" % ", ".join(unknown))
        raise SourceError("%s marker set does not match catalog (%s)" % (SOURCE_REL, "; ".join(details)))

    bodies: dict[str, str] = {}
    case_ids: dict[str, list[str]] = {}
    all_ids: dict[str, tuple[str, int]] = {}
    for position, (name, marker_line, marker_index) in enumerate(starts):
        end_index = starts[position + 1][2] - 1 if position + 1 < len(starts) else len(lines)
        body_lines = lines[marker_index:end_index]
        body = "".join(body_lines).strip() + "\n"
        ids: list[str] = []
        for offset, line in enumerate(body_lines, marker_line + 1):
            match = CASE_RE.match(line)
            if not match:
                continue
            case_id = match.group(1)
            if case_id in all_ids:
                prior_shard, prior_line = all_ids[case_id]
                raise SourceError(
                    "%s:%d duplicates case id %r (first in %s at line %d)"
                    % (SOURCE_REL, offset, case_id, prior_shard, prior_line)
                )
            all_ids[case_id] = (name, offset)
            ids.append(case_id)
        if not ids:
            raise SourceError("%s shard %r has no cases" % (SOURCE_REL, name))
        bodies[name] = body
        case_ids[name] = ids

    return order, bodies, case_ids


def _display_name(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("## "):
            return line[3:].removesuffix(" routing scenarios").strip()
    return fallback


def render_outputs(root: Path = ROOT) -> dict[Path, str]:
    order, bodies, case_ids = parse_source(root)
    outputs: dict[Path, str] = {}
    rows: dict[str, str] = {}

    for name in order:
        display = _display_name(bodies[name], name)
        relative = SHARD_DIR_REL / (name + ".md")
        if name == CROSS_SHARD:
            role = "Boundary disambiguation only; load it when the goal genuinely spans disciplines."
        else:
            role = "Primary routing cases for `/aaron-marketing:%s`." % name
            rows[name] = (
                "| `%s` | [%s](auto-routing/%s.md) | %d |"
                % (name, display, name, len(case_ids[name]))
            )
        body = bodies[name].replace(
            "(../references/aaron-product-api-contract.md)",
            "(../aaron-product-api-contract.md)",
        )
        outputs[relative] = (
            "<!-- Generated routing projection; do not edit directly. -->\n"
            "# Auto Routing Shard: %s\n\n" % display
            + "%s This projection contains %d cases. Read the " % (role, len(case_ids[name]))
            + "[routing boundary contract](../aaron-product-api-contract.md) before execution.\n\n"
            + body
        )

    cross_count = len(case_ids[CROSS_SHARD])
    outputs[INDEX_REL] = (
        "<!-- Generated routing projection; do not edit directly. -->\n"
        "# Auto Routing Scenario Index\n\n"
        "Small runtime index for `/aaron-marketing:auto`. The full case corpus is split so a host can load only the routing evidence needed for the current goal. Read the [routing boundary contract](aaron-product-api-contract.md) first.\n\n"
        "## Shard selection contract\n\n"
        "1. Choose exactly one primary discipline shard from the table after lightweight goal triage.\n"
        "2. Add [cross-discipline](auto-routing/cross-discipline.md) only when the goal crosses a discipline boundary or a listed word sense is unresolved.\n"
        "3. Load at most **3 shards total**. A third shard is allowed only when the selected route has a concrete two-discipline handoff; never load every shard speculatively.\n"
        "4. If the available object and outcome still do not identify a primary shard, ask one concise blocking question before loading case data.\n\n"
        "## Primary shards\n\n"
        "| Command discipline | Runtime shard | Cases |\n"
        "|---|---|---:|\n"
        + "\n".join(rows[name] for name in _catalog_disciplines(root))
        + "\n\n"
        "The cross-discipline shard contains %d boundary cases and is never the sole primary shard.\n"
        % cross_count
    )
    return outputs


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=".%s." % path.name,
            suffix=".tmp", delete=False,
        ) as handle:
            handle.write(content)
            temp_name = handle.name
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass


def write_outputs(root: Path = ROOT) -> None:
    outputs = render_outputs(root)
    shard_dir = root / SHARD_DIR_REL
    expected_shards = {path.name for path in outputs if path.parent == SHARD_DIR_REL}
    if shard_dir.is_dir():
        for stale in sorted(shard_dir.glob("*.md")):
            if stale.name not in expected_shards:
                stale.unlink()
    for relative, content in outputs.items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            _atomic_write(path, content)


def check_outputs(root: Path = ROOT) -> list[str]:
    outputs = render_outputs(root)
    problems: list[str] = []
    for relative, expected in outputs.items():
        path = root / relative
        if not path.is_file():
            problems.append("missing generated file: %s" % relative)
        elif path.read_text(encoding="utf-8") != expected:
            problems.append("stale generated file: %s" % relative)
    shard_dir = root / SHARD_DIR_REL
    expected_shards = {path.name for path in outputs if path.parent == SHARD_DIR_REL}
    if shard_dir.is_dir():
        for path in sorted(shard_dir.glob("*.md")):
            if path.name not in expected_shards:
                problems.append("unexpected generated shard: %s" % path.relative_to(root))
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write generated index and shards")
    mode.add_argument("--check", action="store_true", help="fail if generated files are missing or stale")
    args = parser.parse_args(argv)
    try:
        if args.write:
            outputs = render_outputs(ROOT)
            write_outputs(ROOT)
            print("wrote %d auto-routing projections" % len(outputs))
            return 0
        problems = check_outputs(ROOT)
    except SourceError as exc:
        print("FAIL  %s" % exc, file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print("FAIL  %s" % problem, file=sys.stderr)
        print("run: python3 scripts/generate-auto-routing-shards.py --write", file=sys.stderr)
        return 1
    print("auto-routing projections are current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
