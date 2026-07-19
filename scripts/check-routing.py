#!/usr/bin/env python3
"""Fail-closed routing lint — Python 3 stdlib only.

With 120 skills sharing one description namespace, routing errors are the
bundle's largest quality risk: a host picks skills by description, so two
skills claiming the same trigger phrase is a silent coin-flip, and a skill
without an exclusion clause competes with its siblings forever. This guard
makes the description-routing contract a CI gate. It is structural only —
no model calls, no embeddings; exact quoted-trigger collisions and the
boundary clause are the deterministic proxy for routing health.

Checks:
  1. Quoted-trigger uniqueness: a normalized "..." trigger phrase may be
     claimed by exactly one skill's description. Collisions route randomly.
  2. Boundary clause: every description names what it is NOT for (the
     CONTRIBUTING craft checklist's `Not for X — use Y` rule), so the host
     can route *away*, not just *to*.
  3. Handoff slug resolution: hyphenated `backticked` skill names inside a
     Next Best Skill block must resolve to a real skill. Link-form handoffs
     (](../slug/SKILL.md)) are already covered by the relative-link check;
     bare-name handoffs (memory-management style) silently dangle on a
     rename without this guard. Mode/channel tokens that are not skills
     (e.g. `ai-referrals`) are declared exemptions, never silent passes.

Usage:
  python3 scripts/check-routing.py   # CI gate; exit 1 on fail
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"

QUOTED = re.compile(r'"([^"]{3,})"')
WS = re.compile(r"\s+")
NEXT_BEST = re.compile(r"^## Next Best Skill\s*$(.*?)(?=^## |\Z)", re.M | re.S)
LINK_TARGET = re.compile(r"\]\([^)]*\)")
BACKTICK = re.compile(r"`([^`]+)`")
SLUG_FORM = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+$")
# Conform-or-declared: hyphenated tokens allowed in Next Best Skill blocks
# that are NOT skill slugs (mode/channel names). Everything else must resolve.
HANDOFF_TOKEN_EXEMPTIONS = {"ai-referrals"}


class RoutingError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise RoutingError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def frontmatter(text, rel):
    if not text.startswith("---"):
        raise RoutingError("%s has no frontmatter" % rel)
    try:
        end = text.index("\n---", 3)
    except ValueError as exc:
        raise RoutingError("%s has unterminated frontmatter" % rel) from exc
    return text[3:end]


def description_of(text, rel):
    block = frontmatter(text, rel)
    match = re.search(r"^description:\s*(.*)$", block, re.M)
    if not match:
        raise RoutingError("%s frontmatter has no description" % rel)
    return match.group(1).strip().strip("'\"")


def normalized_triggers(description):
    return {WS.sub(" ", phrase.lower()).strip() for phrase in QUOTED.findall(description)}


def main():
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL  " + msg)

    owners = {}
    count = 0
    skill_dirs = []
    for entry in load_json(PLUGIN_PATH)["skills"]:
        skill_file = ROOT / entry / "SKILL.md"
        rel = skill_file.relative_to(ROOT)
        skill_dirs.append((entry, skill_file, rel))
        try:
            description = description_of(skill_file.read_text(encoding="utf-8"), rel)
        except OSError as exc:
            fail("cannot read %s: %s" % (rel, exc))
            continue
        count += 1
        if "not for" not in description.lower():
            fail("%s description has no 'Not for X — use Y' boundary clause — "
                 "it competes with its siblings on every overlapping request" % rel)
        for trigger in normalized_triggers(description):
            owners.setdefault(trigger, set()).add(entry)

    for trigger, entries in sorted(owners.items()):
        if len(entries) > 1:
            fail("trigger \"%s\" is claimed by %d skills %s — the host routes "
                 "this phrase by coin-flip; differentiate or drop it"
                 % (trigger, len(entries), sorted(entries)))

    slugs = {entry.rstrip("/").split("/")[-1] for entry, _, _ in skill_dirs}
    for entry, skill_file, rel in skill_dirs:
        try:
            text = skill_file.read_text(encoding="utf-8")
        except OSError:
            continue
        match = NEXT_BEST.search(text)
        if not match:
            fail("%s has no ## Next Best Skill block — the chain contract is missing" % rel)
            continue
        block = LINK_TARGET.sub("]", match.group(1))
        for token in BACKTICK.findall(block):
            if SLUG_FORM.fullmatch(token.strip()) \
                    and token.strip() not in slugs \
                    and token.strip() not in HANDOFF_TOKEN_EXEMPTIONS:
                fail("%s Next Best Skill names `%s`, which is not a skill — a "
                     "rename left a dangling bare-name handoff" % (rel, token.strip()))

    if fails:
        print("\nROUTING LINT FAILED — %d issue(s)." % len(fails))
        return 1
    print("Routing lint passed: %d skills, every quoted trigger uniquely owned, "
          "every description carries a boundary clause, every bare-name handoff "
          "resolves." % count)
    return 0


if __name__ == "__main__":
    sys.exit(main())
