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

PHASE_DIRS = [
    "research", "build", "optimize", "monitor", "protocol",   # SEO/GEO
    "discover", "plan", "activate", "measure",      # influencer (4x4)
    "paid/research", "paid/orchestrate", "paid/activate", "paid/scale",                                                        # paid ads (when present)
    "email/setup", "email/engage", "email/nurture", "email/deliver",                                                          # email marketing
]
REQUIRED_CASE_KEYS = [
    "id", "type", "target_skill", "scenario",
    "input_summary", "expected_behavior", "failure_modes",
]
# Manifest may carry ONLY these keys. Anything matching a score/metric word is a
# scope-creep attempt (the rejected output-score baseline) and fails the run.
MANIFEST_ALLOWED_KEYS = {"skills", "count", "required_case_keys", "note"}
SCORE_WORD = re.compile(r"score|rating|cvi|rqs|pass[_-]?rate|metric|baseline_score", re.I)

# Each case is a single-line flow object (optionally a `- ` list item). Line-based
# extraction (first `{` to last `}` on the line) so inner braces like /blog/{slug}
# inside a case do not confuse detection.
CASE_LINE = re.compile(r"^\s*-?\s*(\{.*\})\s*$")

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
            if (key + ":") not in obj and ('"%s"' % key) not in obj:
                fail("%s/cases.md case #%d missing required key '%s'" % (slug, i, key))
        m = re.search(r"target_skill:\s*([A-Za-z0-9_-]+)", obj)
        if m and m.group(1) not in VALID_SLUGS:
            fail("%s/cases.md case #%d target_skill '%s' is not a real skill" % (slug, i, m.group(1)))
    return True


VALID_SLUGS = set(discover_skills())


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

    if update:
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(build_manifest(), f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("wrote %s (%d skills)" % (os.path.relpath(MANIFEST, ROOT), len(VALID_SLUGS)))
        return 0

    if os.path.isfile(MANIFEST):
        man = json.load(open(MANIFEST, encoding="utf-8"))
        stray = [k for k in man if k not in MANIFEST_ALLOWED_KEYS or SCORE_WORD.search(k)]
        if stray:
            fail("manifest has disallowed/score-like keys (scope creep): %s" % stray)
        for s in man.get("skills", []):
            if s not in present:
                fail("manifest skill '%s' lost its cases.md (regression)" % s)
        print("== compared against structure-manifest.json (%d skills) ==" % len(man.get("skills", [])))
    else:
        print("NOTE: no structure-manifest.json yet — run with --update to create it.")

    if fails:
        print("\nEVAL STRUCTURE LINT FAILED — %d issue(s)." % len(fails))
        return 1
    print("\nAll eval structural-lint checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
