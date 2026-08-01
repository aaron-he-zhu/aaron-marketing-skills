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
  3. Any single references/**/*.md|*.json runtime file <= REFERENCE_MAX_BYTES
     (current max: an auto-routing shard at ~46 KB).
  4. memory/templates/hot-cache.md stays within the runtime HOT limits the
     hook enforces (80 lines / 25 KB) so the committed template can never
     ship over budget.
  5. The largest valid `/auto` assembly (command + API contract + routing
     index + three shards) <= AUTO_ASSEMBLY_MAX_BYTES.
  6. Root host instructions remain navigation surfaces: CLAUDE.md and
     AGENTS.md have individual and combined byte ceilings.
  7. Every generated model capsule plus the portable policy kernel stays
     under the compact activation ceiling recorded in its generated index.

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
AUTO_COMMAND = ROOT / "commands" / "auto.md"
AUTO_CONTRACT = ROOT / "references" / "aaron-product-api-contract.md"
AUTO_INDEX = ROOT / "references" / "auto-routing-scenarios.md"
AUTO_SHARDS = ROOT / "references" / "auto-routing"
CLAUDE_CONTEXT = ROOT / "CLAUDE.md"
AGENT_CONTEXT = ROOT / "AGENTS.md"
CAPSULE_INDEX = ROOT / "references" / "skill-capsules" / "index.json"

SKILL_MD_MAX_LINES = 220
ACTIVATION_MAX_BYTES = 125_000
REFERENCE_MAX_BYTES = 51_200
HOT_MAX_LINES = 80
HOT_MAX_BYTES = 25_600
AUTO_ASSEMBLY_MAX_BYTES = 90_000
AUTO_MAX_SHARDS = 3
CLAUDE_CONTEXT_MAX_BYTES = 16_000
AGENT_CONTEXT_MAX_BYTES = 14_000
ROOT_CONTEXT_COMBINED_MAX_BYTES = 28_000
CAPSULE_MODEL_MAX_BYTES = 24_000

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

    for path in sorted((ROOT / "references").rglob("*")):
        if path.suffix not in (".md", ".json") or not path.is_file():
            continue
        size = path.stat().st_size
        if size > REFERENCE_MAX_BYTES:
            fail("%s is %d bytes (budget %d) — split the reference"
                 % (path.relative_to(ROOT), size, REFERENCE_MAX_BYTES))

    auto_surfaces = (AUTO_COMMAND, AUTO_CONTRACT, AUTO_INDEX)
    if any(path.exists() for path in auto_surfaces) and all(path.exists() for path in auto_surfaces):
        shards = sorted(AUTO_SHARDS.glob("*.md")) if AUTO_SHARDS.is_dir() else []
        if len(shards) != 8:
            fail("auto-routing assembled profile requires exactly 8 generated shards (found %d)"
                 % len(shards))
        else:
            base_bytes = sum(path.stat().st_size for path in auto_surfaces)
            largest = sorted((path.stat().st_size for path in shards), reverse=True)[:AUTO_MAX_SHARDS]
            assembled = base_bytes + sum(largest)
            if assembled > AUTO_ASSEMBLY_MAX_BYTES:
                fail("largest /auto assembled context is %d bytes (budget %d, max %d shards)"
                     % (assembled, AUTO_ASSEMBLY_MAX_BYTES, AUTO_MAX_SHARDS))
    elif any(path.exists() for path in auto_surfaces):
        missing = [str(path.relative_to(ROOT)) for path in auto_surfaces if not path.exists()]
        fail("auto-routing assembled profile is incomplete: missing %s" % ", ".join(missing))

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

    root_context_bytes = 0
    for path, ceiling in (
            (CLAUDE_CONTEXT, CLAUDE_CONTEXT_MAX_BYTES),
            (AGENT_CONTEXT, AGENT_CONTEXT_MAX_BYTES)):
        try:
            size = path.stat().st_size
        except OSError as exc:
            fail("cannot inspect root context %s: %s" % (path.name, exc))
            continue
        root_context_bytes += size
        if size > ceiling:
            fail("%s is %d bytes (navigation-context budget %d)"
                 % (path.name, size, ceiling))
    if root_context_bytes > ROOT_CONTEXT_COMBINED_MAX_BYTES:
        fail("root host contexts total %d bytes (combined budget %d)"
             % (root_context_bytes, ROOT_CONTEXT_COMBINED_MAX_BYTES))

    if CAPSULE_INDEX.is_file():
        try:
            capsule_index = load_json(CAPSULE_INDEX)
            entries = capsule_index["capsules"]
        except (BudgetError, KeyError, TypeError) as exc:
            fail("cannot validate skill capsule budget: %s" % exc)
            entries = []
        if len(entries) != 120:
            fail("skill capsule index must contain 120 entries (found %d)" % len(entries))
        for entry in entries:
            model_bytes = entry.get("model_bytes") if isinstance(entry, dict) else None
            skill = entry.get("skill", "unknown") if isinstance(entry, dict) else "unknown"
            if (not isinstance(model_bytes, int) or isinstance(model_bytes, bool)
                    or model_bytes <= 0):
                fail("skill capsule %s has invalid model_bytes" % skill)
            elif model_bytes > CAPSULE_MODEL_MAX_BYTES:
                fail("skill capsule %s model context is %d bytes (budget %d)"
                     % (skill, model_bytes, CAPSULE_MODEL_MAX_BYTES))
    else:
        fail("references/skill-capsules/index.json missing — compact model context is gone")

    if fails:
        print("\nCONTEXT BUDGET FAILED — %d issue(s)." % len(fails))
        return 1
    print("Context budget passed: %d skills, root navigation contexts, model capsules, "
          "auditor activation chains, recursive references, assembled /auto profile, "
          "and HOT template all within budget."
          % len(skill_dirs()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
