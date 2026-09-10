#!/usr/bin/env python3
"""Fail-closed Skill Dashboard exclusion lint — Python 3 stdlib only.

Keeps the local Skill Dashboard generator out of plugin / Portable Lite /
governed payloads, and keeps the official product name stable.

Usage:
  python3 scripts/check-skill-dashboard.py   # CI; exit 1 on fail
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
CONTEXT_MODULES = ROOT / "references" / "context-modules.json"
DISTRIBUTION = ROOT / "references" / "distribution-files.json"
BUILDER = ROOT / "scripts" / "build-distribution.py"
SCHEMA = ROOT / "references" / "skill-dashboard.schema.json"
DOC = ROOT / "docs" / "skill-dashboard.md"
GENERATOR = ROOT / "scripts" / "skill-dashboard.py"
GUARD = Path(__file__).resolve()

MAINTENANCE_PATHS = (
    "scripts/skill-dashboard.py",
    "scripts/check-skill-dashboard.py",
    "references/skill-dashboard.schema.json",
    "docs/skill-dashboard.md",
)
PRODUCT = "Skill Dashboard"
FORBIDDEN_TITLES = (
    "Skill Usage Board",
    "Skill Usage Dashboard",
    "Usage Board",
    "Usage Dashboard",
)
REQUIRED_MODULES = (
    "next", "usage", "delta", "outcomes", "decisions", "trust", "coverage", "staff",
)
DASHBOARD_MARKERS = (
    "skill-dashboard",
    "Skill Dashboard",
)


class DashboardLintError(ValueError):
    pass


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DashboardLintError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def load_builder():
    spec = importlib.util.spec_from_file_location("dashboard_distribution_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise DashboardLintError("cannot load scripts/build-distribution.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def contains_dashboard(value):
    if isinstance(value, str):
        lowered = value.lower()
        return "skill-dashboard" in lowered or "usage-board" in lowered
    if isinstance(value, list):
        return any(contains_dashboard(item) for item in value)
    if isinstance(value, dict):
        return any(contains_dashboard(item) for item in value.values())
    return False


def walk_allowlist(dist):
    declared = []
    plugin = dist.get("plugin") if isinstance(dist, dict) else None
    shared = plugin.get("shared") if isinstance(plugin, dict) else {}
    for key in ("root_files", "trees", "runtime_references", "runtime_scripts",
                "runtime_script_trees"):
        declared.extend(shared.get(key) or [])
    for spec in (plugin.get("profiles") or {}).values() if isinstance(plugin, dict) else []:
        added = spec.get("add") if isinstance(spec, dict) else {}
        for key in ("root_files", "trees", "runtime_references", "runtime_scripts",
                    "runtime_script_trees"):
            declared.extend(added.get(key) or [])
    return declared


def main():
    fails = []

    def fail(message):
        fails.append(message)
        print("FAIL: %s" % message)

    for relative in (
        "scripts/skill-dashboard.py",
        "scripts/check-skill-dashboard.py",
        "references/skill-dashboard.schema.json",
        "docs/skill-dashboard.md",
        "tests/test_skill_dashboard.py",
    ):
        if not (ROOT / relative).is_file():
            fail("missing required Skill Dashboard file %s" % relative)

    plugin = load_json(PLUGIN)
    skills = plugin.get("skills") if isinstance(plugin, dict) else None
    if not isinstance(skills, list) or len(skills) != 120:
        fail("plugin.json must remain exactly 120 skills")
    if (ROOT / "apps" / "skill-dashboard" / "SKILL.md").exists():
        fail("apps/skill-dashboard must not become a Skill")
    if (ROOT / "references" / "skill-dashboard" / "SKILL.md").exists():
        fail("references/skill-dashboard must not become a Skill")

    modules_text = CONTEXT_MODULES.read_text(encoding="utf-8")
    if "skill-dashboard" in modules_text or "usage-board" in modules_text:
        fail("context-modules.json must not wire Skill Dashboard")

    dist = load_json(DISTRIBUTION)
    if contains_dashboard(dist.get("plugin")):
        fail("distribution-files.json allowlists Skill Dashboard")
    excluded = dist.get("excluded_top_level") or []
    if "apps" not in excluded:
        fail("distribution-files.json excluded_top_level must include apps")
    declared = walk_allowlist(dist)
    for relative in MAINTENANCE_PATHS:
        if relative in declared:
            fail("distribution-files.json allowlists maintenance path %s" % relative)

    schema = load_json(SCHEMA)
    if schema.get("title") != "Skill Dashboard view projection":
        fail("schema title must use the Skill Dashboard product name")
    if schema.get("properties", {}).get("product", {}).get("const") != PRODUCT:
        fail("schema product const must be Skill Dashboard")
    module_props = (
        schema.get("properties", {}).get("modules", {}).get("properties") or {}
    )
    missing = [name for name in REQUIRED_MODULES if name not in module_props]
    if missing:
        fail("schema modules missing %s" % missing)

    named_surfaces = (DOC, GENERATOR, SCHEMA, ROOT / "README.md", ROOT / "docs" / "README.md")
    for path in named_surfaces:
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN_TITLES:
            if forbidden in text:
                fail("%s uses forbidden product title %r" % (path.relative_to(ROOT), forbidden))
    doc = DOC.read_text(encoding="utf-8")
    plain = doc.replace("*", "").replace("_", "").replace("`", "")
    if PRODUCT not in doc:
        fail("docs/skill-dashboard.md must use the Skill Dashboard product name")
    if "Gateway" in plain and "not a Gateway" not in plain and "No Gateway" not in plain:
        fail("docs/skill-dashboard.md must keep Gateway as a boundary, not a feature")
    if "local optional" not in doc.lower() and "optional local" not in doc.lower():
        fail("docs/skill-dashboard.md must state the local optional-tool boundary")

    builder = load_builder()
    if "apps" not in builder.MAINTENANCE_TREES:
        fail("build-distribution.py MAINTENANCE_TREES must include apps")
    missing_exact = [
        relative for relative in MAINTENANCE_PATHS
        if relative not in builder.MAINTENANCE_EXACT
    ]
    if missing_exact:
        fail("build-distribution.py MAINTENANCE_EXACT missing %s" % missing_exact)
    profile = builder.resolve_plugin_profile(builder.load_json(builder.MANIFEST), "governed")
    for relative in MAINTENANCE_PATHS:
        if builder.dependency_allowed(relative, profile):
            fail("governed closure would ship %s" % relative)
    if builder.dependency_allowed("docs/skill-dashboard.md", profile):
        fail("governed closure would ship docs/skill-dashboard.md")
    if builder.dependency_allowed("apps/skill-dashboard/index.html", profile):
        fail("governed closure would ship apps/skill-dashboard")
    readme_deps = builder.runtime_dependencies("README.md")
    leaked = [
        dep for dep in sorted(readme_deps)
        if builder.dependency_allowed(dep, profile)
        and (dep in MAINTENANCE_PATHS or "skill-dashboard" in dep or "usage-board" in dep)
    ]
    if leaked:
        fail("README runtime closure would ship Skill Dashboard paths: %s" % leaked)

    if fails:
        print("\nSKILL DASHBOARD LINT FAILED — %d issue(s)." % len(fails))
        return 1
    print(
        "Skill Dashboard lint passed: product name holds, 120 skills unchanged, "
        "runtime exclusion holds."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
