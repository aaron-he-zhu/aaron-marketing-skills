#!/usr/bin/env python3
"""Structural lint for the eval seed set — Python 3 stdlib only.

This is NOT an eval *runner*: it never calls a model and never executes a skill.
It only guards the *structure* of the manually-authored `evals/<skill>/cases.md`
corpus so capability-expansion edits cannot silently rot it. Two guards:

  1. Presence + parseability: every skill (a subdir of a phase dir) has a
     `cases.md`; every case object carries the required keys; every
     `target_skill` names a real skill slug.
  2. No-dropped-skill regression: the committed `evals/structure-manifest.json`
     records the structural facts (skill list, count, required keys). A skill
     that had a cases.md and lost it fails the run.

The manifest stores ONLY structural facts (never output scores) — a key
allowlist is enforced so it can never quietly grow into the rejected
"output-score baseline" runner.

Usage:
  python3 scripts/check-evals.py            # lint + compare to manifest (CI gate; exit 1 on fail)
  python3 scripts/check-evals.py --update    # regenerate the manifest after an intentional change
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVALS = os.path.join(ROOT, "evals")
MANIFEST = os.path.join(EVALS, "structure-manifest.json")
ROUTING_SOURCE = os.path.join(ROOT, "evals", "auto-routing-scenarios.source.md")
ROUTING_LABEL = "auto-routing-scenarios.source.md"

# Phase directories and command selectors derive from the system catalog — the
# single source of truth — so they can never drift from the real topology again.
_CATALOG = json.load(open(os.path.join(ROOT, "references", "system-catalog.json"), encoding="utf-8"))
PHASE_DIRS = [
    "%s/%s" % (discipline, phase)
    for discipline, spec in _CATALOG["disciplines"].items()
    for phase in spec["phase_order"]
] + ["protocol"]
REQUIRED_CASE_KEYS = [
    "id", "type", "target_skill", "scenario",
    "input_summary", "expected_behavior", "failure_modes",
]
# Manifest may carry ONLY these keys. Anything matching a score/metric word is a
# scope-creep attempt (the rejected output-score baseline) and fails the run.
MANIFEST_ALLOWED_KEYS = {"skills", "count", "required_case_keys", "note"}
SCORE_WORD = re.compile(r"score|rating|sqs|rqs|pass[_-]?rate|metric|baseline_score", re.I)

# Each case is a single-line flow object (optionally a `- ` list item). Line-based
# extraction (first `{` to last `}` on the line) so inner braces like /blog/{slug}
# inside a case do not confuse detection.
CASE_LINE = re.compile(r"^\s*-?\s*(\{.*\})\s*$")
# target_skill is quoted in the routing library ("skill-name") and bare in
# evals/*/cases.md (skill-name) — tolerate both.
TARGET_SKILL_RE = re.compile(r'target_skill:\s*"?([A-Za-z0-9_-]+)"?')
# expected_route is a quoted chain like "/aaron-marketing:ad --phase activate -> ...".
EXPECTED_ROUTE_RE = re.compile(r'expected_route:\s*"([^"]*)"')
CASE_ID_RE = re.compile(r'(?:(?:^|[{,])\s*)id:\s*"([^"]+)"')
SHARD_MARKER_RE = re.compile(r"^<!-- auto-routing-shard: ([a-z0-9-]+) -->$")
ROUTE_SEG_CMD_RE = re.compile(r'/aaron-marketing:([a-z-]+)')
ROUTE_SEG_SELECTOR_RE = re.compile(r'--(mode|phase)\s+([a-z-]+)')
ROUTE_SEG_FLAG_RE = re.compile(r'--([a-z][a-z-]*)')
# Each command's valid selector, derived from the catalog `command` contract:
# all seven disciplines use --phase (SEO/GEO's former --mode alias was removed in
# v18; the regex below still matches --mode only to reject any stray reintroduction),
# auto takes neither (only --deep).
# Guards expected_route against a typo'd command or an invalid/mismatched phase
# value (e.g. "ad --phase research" is valid, "ad --mode research" is not).
COMMAND_MODES = {
    spec["command"]["name"]: (spec["command"]["selector"], set(spec["command"]["values"]))
    for spec in _CATALOG["disciplines"].values()
}
COMMAND_MODES["auto"] = (None, set())
# Per-phase flags of /aaron-marketing:seo-geo — keep in step with the per-phase
# flag sections of commands/seo-geo.md. --competitors is legal in survey and
# (alongside --authority) in evaluate; --period rides --report in evaluate.
SEO_GEO_PHASE_FLAGS = {
    "survey": {"competitors", "map"},
    "implement": {"brief", "series", "refresh", "publish", "meta", "schema", "type"},
    "tune": {"full", "tech", "visibility"},
    "evaluate": {"authority", "alert", "report", "remember", "period", "competitors"},
}
# Slug-shaped token (two-plus hyphen-joined parts) — used to vet skill names
# inside parenthesized route chains without tripping on hyphenated prose.
SLUG_FORM = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)+$")

fails = []
def fail(msg):
    fails.append(msg)
    print("FAIL  " + msg)


def discover_skills():
    """Return sorted list of skill slugs = subdirs of existing phase dirs."""
    slugs = []
    for p in PHASE_DIRS:
        d = os.path.join(ROOT, p)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if os.path.isfile(os.path.join(d, name, "SKILL.md")):
                slugs.append(name)
    return sorted(set(slugs))


def lint_cases(slug):
    """Lint one skill's cases.md; return True if a cases.md exists (for presence)."""
    path = os.path.join(EVALS, slug, "cases.md")
    if not os.path.isfile(path):
        return False
    text = open(path, encoding="utf-8").read()
    objs = [m.group(1) for line in text.splitlines()
            for m in (CASE_LINE.match(line),) if m]
    if not objs:
        fail("%s/cases.md has no parseable case objects" % slug)
        return True
    for i, obj in enumerate(objs, 1):
        for key in REQUIRED_CASE_KEYS:
            # Match the key only at a key POSITION: line start, or right after '{'
            # or ',' (with optional whitespace), optionally quoted, then ':'. Using
            # '{' / ',' as the boundary (NOT bare \s) means a space-preceded '<key>:'
            # inside a quoted prose value no longer masks a truly-missing key.
            if not re.search(r'(?:^|[{,])\s*"?' + re.escape(key) + r'"?\s*:', obj):
                fail("%s/cases.md case #%d missing required key '%s'" % (slug, i, key))
        m = TARGET_SKILL_RE.search(obj)
        if m and m.group(1) not in VALID_SLUGS:
            fail("%s/cases.md case #%d target_skill '%s' is not a real skill" % (slug, i, m.group(1)))
    return True


VALID_SLUGS = set(discover_skills())


def lint_route_chain(route, lineno):
    """Validate one expected_route chain beyond the bare selector check:

    - every `/aaron-marketing:<cmd>` segment names a known command, its
      selector is `--phase <catalog value>` (never `--mode`), and
    - seo-geo segments carry only flags belonging to that segment's phase
      (the per-phase flag contract of commands/seo-geo.md) — the drift class
      where a bulk edit pairs `--phase survey` with a tune/evaluate flag, and
    - skill slugs inside parenthesized chains resolve to real skills.
    """
    # Segments join with "->" (a chain) or "|" (disambiguation alternatives).
    for seg in re.split(r"->|\|", route):
        m = ROUTE_SEG_CMD_RE.search(seg)
        if not m:
            continue  # paren-only fragment; slugs are vetted below
        cmd = m.group(1)
        spec = COMMAND_MODES.get(cmd)
        if spec is None:
            fail("%s line %d: expected_route names unknown "
                 "command '/aaron-marketing:%s'" % (ROUTING_LABEL, lineno, cmd))
            continue
        exp_flag, allowed = spec
        phase = None
        sel = ROUTE_SEG_SELECTOR_RE.search(seg)
        if sel:
            flag, val = sel.group(1), sel.group(2)
            if flag != exp_flag or val not in allowed:
                fail("%s line %d: expected_route '--%s %s' is not "
                     "valid for /aaron-marketing:%s" % (ROUTING_LABEL, lineno, flag, val, cmd))
            else:
                phase = val
        extra = [f for f in ROUTE_SEG_FLAG_RE.findall(seg) if f not in ("mode", "phase")]
        if cmd == "seo-geo":
            legal = SEO_GEO_PHASE_FLAGS.get(phase, set())
            for f in extra:
                if f not in legal:
                    fail("%s line %d: '--%s' is not a flag of "
                         "/aaron-marketing:seo-geo --phase %s (per-phase flag contract, "
                         "commands/seo-geo.md)" % (ROUTING_LABEL, lineno, f, phase or "<none>"))
        elif cmd == "auto":
            for f in extra:
                if f != "deep":
                    fail("%s line %d: /aaron-marketing:auto takes "
                         "only --deep, got '--%s'" % (ROUTING_LABEL, lineno, f))
        else:
            for f in extra:
                fail("%s line %d: /aaron-marketing:%s routes carry "
                     "no flags beyond --phase, got '--%s'" % (ROUTING_LABEL, lineno, cmd, f))
    for group in re.findall(r"\(([^)]*)\)", route):
        for element in re.split(r"->|,", group):
            element = element.strip()
            if not element:
                continue
            tok = element.split()[0].strip("`")
            if SLUG_FORM.match(tok) and tok not in VALID_SLUGS:
                fail("%s line %d: expected_route references unknown skill '%s'"
                     % (ROUTING_LABEL, lineno, tok))


def lint_routing_source():
    """Lint the one authoritative auto-routing source and its shard boundaries."""
    if not os.path.isfile(ROUTING_SOURCE):
        fail("evals/%s missing — the authoritative /aaron-marketing:auto cases"
             % ROUTING_LABEL)
        return
    text = open(ROUTING_SOURCE, encoding="utf-8").read()
    legal_markers = set(_CATALOG["disciplines"]) | {"cross-discipline"}
    marker_lines = {}
    marker_case_counts = {}
    case_lines = {}
    current_marker = None
    seen = 0

    for i, line in enumerate(text.splitlines(), 1):
        marker = SHARD_MARKER_RE.fullmatch(line)
        if marker:
            current_marker = marker.group(1)
            if current_marker in marker_lines:
                fail("%s line %d: duplicate shard marker '%s' (first at line %d)"
                     % (ROUTING_LABEL, i, current_marker, marker_lines[current_marker]))
            else:
                marker_lines[current_marker] = i
                marker_case_counts[current_marker] = 0
            continue
        if not CASE_LINE.match(line):
            continue
        seen += 1
        if current_marker is None:
            fail("%s line %d: routing case appears before a shard marker"
                 % (ROUTING_LABEL, i))
        else:
            marker_case_counts[current_marker] = marker_case_counts.get(current_marker, 0) + 1

        case_id = CASE_ID_RE.search(line)
        if not case_id:
            fail("%s line %d: routing case has no quoted id" % (ROUTING_LABEL, i))
        elif case_id.group(1) in case_lines:
            fail("%s line %d: duplicate routing case id '%s' (first at line %d)"
                 % (ROUTING_LABEL, i, case_id.group(1), case_lines[case_id.group(1)]))
        else:
            case_lines[case_id.group(1)] = i

        target = TARGET_SKILL_RE.search(line)
        if not target:
            fail("%s line %d: routing case has no target_skill" % (ROUTING_LABEL, i))
        elif target.group(1) not in VALID_SLUGS:
            fail("%s line %d: target_skill '%s' is not a real skill"
                 % (ROUTING_LABEL, i, target.group(1)))
        expected_route = EXPECTED_ROUTE_RE.search(line)
        if not expected_route:
            fail("%s line %d: routing case has no quoted expected_route"
                 % (ROUTING_LABEL, i))
        else:
            lint_route_chain(expected_route.group(1), i)

    actual_markers = set(marker_lines)
    for marker in sorted(actual_markers - legal_markers):
        fail("%s line %d: shard marker '%s' is not a catalog discipline"
             % (ROUTING_LABEL, marker_lines[marker], marker))
    for marker in sorted(legal_markers - actual_markers):
        fail("%s missing shard marker '%s'" % (ROUTING_LABEL, marker))
    for marker, count in sorted(marker_case_counts.items()):
        if marker in legal_markers and count == 0:
            fail("%s shard marker '%s' has no routing cases" % (ROUTING_LABEL, marker))

    print("== routing-source lint: %d routing cases across %d catalog-derived shards; "
          "unique id + target_skill + expected_route checked =="
          % (seen, len(marker_lines)))


def build_manifest():
    return {
        "skills": sorted(VALID_SLUGS),
        "count": len(VALID_SLUGS),
        "required_case_keys": REQUIRED_CASE_KEYS,
        "note": "Structural facts only — never output scores. Regenerate with check-evals.py --update.",
    }


def main():
    update = "--update" in sys.argv

    present = [s for s in sorted(VALID_SLUGS) if lint_cases(s)]
    missing = sorted(set(VALID_SLUGS) - set(present))
    for s in missing:
        fail("skill '%s' has no evals/%s/cases.md (presence gate)" % (s, s))

    print("== eval structural lint: %d skills, %d with cases.md ==" % (len(VALID_SLUGS), len(present)))

    lint_routing_source()

    if update:
        # Fail CLOSED: never write the regression baseline from a failing lint —
        # that would bake the current breakage in as the new "expected" structure.
        if fails:
            print("\nREFUSING to write structure-manifest.json — fix the %d lint "
                  "issue(s) above first." % len(fails))
            return 1
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(build_manifest(), f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("wrote %s (%d skills)" % (os.path.relpath(MANIFEST, ROOT), len(VALID_SLUGS)))
        return 0

    if os.path.isfile(MANIFEST):
        try:
            man = json.load(open(MANIFEST, encoding="utf-8"))
        except (ValueError, OSError) as e:
            fail("structure-manifest.json is unreadable/corrupt: %s" % e)
            man = {}
        stray = [k for k in man if k not in MANIFEST_ALLOWED_KEYS or SCORE_WORD.search(k)]
        if stray:
            fail("manifest has disallowed/score-like keys (scope creep): %s" % stray)
        for s in man.get("skills", []):
            if s not in present:
                fail("manifest skill '%s' lost its cases.md (regression)" % s)
        if man.get("required_case_keys") != REQUIRED_CASE_KEYS:
            fail("manifest required_case_keys drifted from the script — re-run --update")
        if man.get("count") != len(man.get("skills", [])):
            fail("manifest count (%s) != its skills list length (%d) — re-run --update"
                 % (man.get("count"), len(man.get("skills", []))))
        print("== compared against structure-manifest.json (%d skills) ==" % len(man.get("skills", [])))
    else:
        # Fail CLOSED: without the committed baseline the no-dropped-skill
        # regression guard is disabled, so a missing/deleted manifest must be
        # a hard failure, not a note.
        fail("structure-manifest.json missing — the no-dropped-skill regression "
             "baseline (restore it from git, or run --update after an intentional "
             "structural change)")

    if fails:
        print("\nEVAL STRUCTURE LINT FAILED — %d issue(s)." % len(fails))
        return 1
    print("\nAll eval structural-lint checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
