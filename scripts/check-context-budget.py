#!/usr/bin/env python3
"""Fail-closed context-budget guard — Python 3 stdlib only.

Progressive disclosure is the bundle's core context-engineering rule ("keep
SKILL.md focused; put detail in references/"), but without an enforced budget
it silently rots: SKILL.md bodies grow, and auditor activation chains (the
files an auditor must Read before scoring) accumulate bytes until the read
itself crowds out the evidence window. This guard makes the budget a CI
contract. It is structural only — it never calls a model and never estimates
tokens; bytes and lines are the stable, host-independent proxy.

Budgets (each ~25-30% above the measured v18 baseline; tighten only after a
deliberate redesign, never because one file "needs" more room — extract to
references/ or split the reference instead):

  1. SKILL.md total length <= SKILL_MD_MAX_LINES lines (current max: 172).
  2. Auditor activation chain: the byte sum of every references/ file listed
     in an auditor's "Runtime Contract" Read list <= ACTIVATION_MAX_BYTES
     (current worst: CORE-EEAT at ~93 KB).
  3. Any single root references/*.md|*.json runtime file <= REFERENCE_MAX_BYTES
     (current max: core-eeat-benchmark.md at ~40 KB).
  4. memory/templates/hot-cache.md stays within the runtime HOT limits the
     hook enforces (80 lines / 25 KB) so the committed template can never
     ship over budget.

Usage:
  python3 scripts/check-context-budget.py   # CI gate; exit 1 on fail
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
HOT_TEMPLATE = ROOT / "memory" / "templates" / "hot-cache.md"

SKILL_MD_MAX_LINES = 220
ACTIVATION_MAX_BYTES = 125_000
REFERENCE_MAX_BYTES = 51_200
HOT_MAX_LINES = 80
HOT_MAX_BYTES = 25_600

# Backticked repo-root reference paths inside an auditor runtime section,
# e.g. `../../../references/auditor-runbook.md`.
ACTIVATION_REF = re.compile(r"`(?:\.\./)+references/([A-Za-z0-9_./-]+\.(?:md|json))`")
# Bare backticked filenames that resolve against root references/
# (e.g. `scoring-semantics.md` in the six non-CORE-EEAT auditor skills).
BARE_REF = re.compile(r"`([a-z][a-z0-9-]*\.(?:md|json))`")
FRONTMATTER_CLASS = re.compile(r"^class:\s*([A-Za-z-]+)\s*$", re.M)
RUNTIME_HEADING = re.compile(r"^### Runtime[^\n]*\n(.*?)(?=^#{2,3} |\Z)", re.M | re.S)
# Generated only into standalone distributions, where it REPLACES the listed
# repo files — counting it would double-book the chain.
GENERATED_RUNTIME = "auditor-runtime.md"

# Conform-or-declared: known over-budget references are exempt from the
# default cap only up to their own declared ceiling (~10% growth headroom),
# so an exemption can never silently balloon. New references get no entry.
DECLARED_REFERENCE_CEILINGS = {
    # The /aaron-marketing:auto scenario library is a single runtime-consulted
    # resource (commands/auto.md); splitting it is a deliberate redesign, not
    # a budget fix. Baseline 94,820 bytes at v18.
    "auto-routing-scenarios.md": 105_000,
}


class BudgetError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise BudgetError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def skill_dirs():
    plugin = load_json(PLUGIN_PATH)
    return [ROOT / entry for entry in plugin["skills"]]


def runtime_contract_section(text):
    """Return the auditor runtime block ('### Runtime Contract' or '### Runtime and Setup')."""
    match = RUNTIME_HEADING.search(text)
    return match.group(1) if match else ""


def activation_chain(skill_file):
    """Unique repo-relative references/ files an auditor declares for activation."""
    section = runtime_contract_section(skill_file.read_text(encoding="utf-8"))
    seen = []
    for name in ACTIVATION_REF.findall(section):
        if name != GENERATED_RUNTIME and name not in seen:
            seen.append(name)
    for name in BARE_REF.findall(section):
        if name != GENERATED_RUNTIME and "/" not in name and name not in seen:
            if (ROOT / "references" / name).is_file():
                seen.append(name)
    return seen


def main():
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL  " + msg)

    for skill_dir in skill_dirs():
        skill_file = skill_dir / "SKILL.md"
        rel = skill_file.relative_to(ROOT)
        try:
            text = skill_file.read_text(encoding="utf-8")
        except OSError as exc:
            fail("cannot read %s: %s" % (rel, exc))
            continue
        lines = text.count("\n") + 1
        if lines > SKILL_MD_MAX_LINES:
            fail("%s is %d lines (budget %d) — extract detail into references/"
                 % (rel, lines, SKILL_MD_MAX_LINES))
        class_match = FRONTMATTER_CLASS.search(text)
        if not class_match or class_match.group(1) != "auditor":
            continue
        chain = activation_chain(skill_file)
        if not chain:
            fail("%s declares class auditor but its Runtime Contract lists no "
                 "references/ activation reads — contract drift or parser break" % rel)
            continue
        total = 0
        for name in chain:
            path = ROOT / "references" / name
            try:
                total += path.stat().st_size
            except OSError as exc:
                fail("%s activation read %s: %s" % (rel, name, exc))
        if total > ACTIVATION_MAX_BYTES:
            fail("%s activation chain is %d bytes (budget %d): %s"
                 % (rel, total, ACTIVATION_MAX_BYTES, ", ".join(chain)))

    for path in sorted((ROOT / "references").iterdir()):
        if path.suffix not in (".md", ".json") or not path.is_file():
            continue
        size = path.stat().st_size
        ceiling = DECLARED_REFERENCE_CEILINGS.get(path.name, REFERENCE_MAX_BYTES)
        if size > ceiling:
            fail("references/%s is %d bytes (budget %d) — split the reference"
                 % (path.name, size, ceiling))

    if HOT_TEMPLATE.is_file():
        hot = HOT_TEMPLATE.read_text(encoding="utf-8")
        hot_lines = hot.count("\n") + 1
        hot_bytes = len(hot.encode("utf-8"))
        if hot_lines > HOT_MAX_LINES or hot_bytes > HOT_MAX_BYTES:
            fail("memory/templates/hot-cache.md is %d lines / %d bytes "
                 "(runtime HOT limit %d lines / %d bytes)"
                 % (hot_lines, hot_bytes, HOT_MAX_LINES, HOT_MAX_BYTES))
    else:
        fail("memory/templates/hot-cache.md missing — HOT template baseline is gone")

    if fails:
        print("\nCONTEXT BUDGET FAILED — %d issue(s)." % len(fails))
        return 1
    print("Context budget passed: %d skills, auditor activation chains, root "
          "references, HOT template all within budget." % len(skill_dirs()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
