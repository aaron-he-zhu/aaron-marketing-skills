#!/usr/bin/env python3
"""Generate/check the compact skill discovery index inside CLAUDE.md."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "references" / "system-catalog.json"
TARGET = ROOT / "CLAUDE.md"
BEGIN = "<!-- GENERATED:BEGIN compact-skill-index -->"
END = "<!-- GENERATED:END compact-skill-index -->"


class ClaudeIndexError(ValueError):
    pass


def load_catalog():
    try:
        value = json.loads(CATALOG.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ClaudeIndexError("cannot load system catalog: %s" % exc) from exc
    if (
            not isinstance(value, dict)
            or value.get("counts", {}).get("total_skills") != 120
            or value.get("counts", {}).get("commands") != 8
            or value.get("logical_order") != [
                "narrative", "seo-geo", "social", "email", "ad",
                "influencer", "launch", "protocol"]):
        raise ClaudeIndexError("system catalog identity/count is unsupported")
    return value


def render(catalog):
    lines = [BEGIN]
    names = []
    for discipline in catalog["logical_order"]:
        if discipline == "protocol":
            protocol = catalog["protocol"]
            skills = protocol["skills"]
            names.extend(skills)
            lines.append(
                "- **%s (8):** %s"
                % (
                    protocol["display_name"],
                    " · ".join("`%s`" % skill for skill in skills),
                )
            )
            continue
        spec = catalog["disciplines"][discipline]
        phase_parts = []
        count = 0
        for phase in spec["phase_order"]:
            skills = spec["phases"][phase]
            names.extend(skills)
            count += len(skills)
            phase_parts.append(
                "**%s:** %s"
                % (phase.title(), " · ".join("`%s`" % skill for skill in skills))
            )
        lines.append(
            "- **%s · %s (%d):** %s"
            % (
                spec["display_name"],
                "+".join(spec["frameworks"]),
                count,
                "; ".join(phase_parts),
            )
        )
    if len(names) != 120 or len(names) != len(set(names)):
        raise ClaudeIndexError("compact index does not cover 120 unique skills")
    lines.append(END)
    return "\n".join(lines)


def replace_index(source, rendered):
    if source.count(BEGIN) != 1 or source.count(END) != 1:
        raise ClaudeIndexError("CLAUDE.md must contain one compact-index marker pair")
    start = source.index(BEGIN)
    finish = source.index(END, start) + len(END)
    if finish <= start:
        raise ClaudeIndexError("CLAUDE.md compact-index markers are malformed")
    return source[:start] + rendered + source[finish:]


def atomic_write(path, content):
    descriptor, temporary = tempfile.mkstemp(prefix=".%s." % path.name, dir=str(path.parent))
    try:
        mode = path.stat().st_mode & 0o777
        os.chmod(temporary, mode)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        source = TARGET.read_text(encoding="utf-8")
        expected = replace_index(source, render(load_catalog()))
        if args.write:
            atomic_write(TARGET, expected)
            print("wrote compact CLAUDE.md skill index")
        elif source != expected:
            raise ClaudeIndexError("CLAUDE.md compact skill index is stale; run with --write")
        else:
            print("compact CLAUDE.md skill index is current")
    except (OSError, UnicodeError, ClaudeIndexError) as exc:
        print("CLAUDE.md index generation failed: %s" % exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
