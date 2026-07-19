#!/usr/bin/env python3
"""Fail-closed architecture conformance checks for the system catalog."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "references" / "system-catalog.json"
FRAMEWORK_PATH = ROOT / "references" / "framework-catalog.json"
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
GROUPINGS_PATH = ROOT / "skills.sh.json"
MARKETPLACE_PATHS = [ROOT / "marketplace.json", ROOT / ".claude-plugin" / "marketplace.json"]
OPENCLAW_PATH = ROOT / "openclaw.plugin.json"
HOOKS_PATH = ROOT / "hooks" / "hooks.json"
REGISTRY_RUNTIME = ROOT / "scripts" / "registry-events.py"
LEGACY_COMPOSITE = re.compile(r"\b(?:LQS|NQS)\b|goal-weight(?:ed)? column", re.I)
LEGACY_SCORING = re.compile(r"min\s*\(\s*raw\s*,\s*60\s*\)|\bgoal[- /]?weight(?:s|ed)?\b|\bgoal column\b", re.I)
FAIL_OPEN_GATE = re.compile(r"unmarked.{0,80}(?:pass|allow|放行|通過|통과)", re.I)
MUTABLE_RUNTIME = re.compile(
    r"raw\.githubusercontent\.com/aaron-he-zhu/aaron-marketing-skills/(?:main|master)/references/",
    re.I,
)
BARE_ROOT_RUNTIME_COMMAND = re.compile(
    r"\bpython3\s+(?:\./)?scripts/(?:rubric-score|validate-audit-artifact|registry-events|run-events)\.py\b"
)
AUDIT_WRITE_INTENT = re.compile(
    r"\b(?:write|writes|save|saves|persist|persists|store|stores|storable)\b|ready for",
    re.I,
)
AUDIT_WRITE_NEGATION = re.compile(r"\b(?:never|must not|does not|do not|reserved)\b", re.I)


class ArchitectureError(ValueError):
    pass


def load_json(path):
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise ArchitectureError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def frontmatter(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ArchitectureError("%s has no frontmatter" % path.relative_to(ROOT))
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ArchitectureError("%s has unterminated frontmatter" % path.relative_to(ROOT)) from exc
    values = {}
    for line in lines[1:end]:
        matched = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if matched:
            values[matched.group(1)] = matched.group(2).strip().strip('"\'')
    metadata_line = next((line for line in lines[1:end] if line.startswith("metadata:")), None)
    if metadata_line is None:
        raise ArchitectureError("%s has no metadata" % path.relative_to(ROOT))
    try:
        metadata = json.loads(metadata_line.split(":", 1)[1].strip())
    except ValueError as exc:
        raise ArchitectureError("%s metadata is not strict JSON" % path.relative_to(ROOT)) from exc
    return values, metadata


def expected_skill_paths(catalog, failures):
    paths = []
    logical = catalog.get("logical_order", [])
    disciplines = catalog.get("disciplines", {})
    if logical != ["narrative", "seo-geo", "social", "email", "ad", "influencer", "launch", "protocol"]:
        failures.append("logical_order must preserve the canonical four-layer order")
    for discipline in logical:
        if discipline == "protocol":
            continue
        spec = disciplines.get(discipline)
        if not isinstance(spec, dict):
            failures.append("logical discipline %s is missing" % discipline)
            continue
        phases = spec.get("phase_order", [])
        if set(phases) != set(spec.get("phases", {})) or len(phases) != 4:
            failures.append("%s must declare exactly four ordered phases" % discipline)
        if spec.get("layer") not in {"L1", "L2", "L3"}:
            failures.append("%s has an invalid layer" % discipline)
        for phase in phases:
            slugs = spec["phases"].get(phase, [])
            if len(slugs) != 4 or len(slugs) != len(set(slugs)):
                failures.append("%s/%s must contain four unique skills" % (discipline, phase))
            paths.extend("%s/%s/%s" % (discipline, phase, slug) for slug in slugs)
    protocol = catalog.get("protocol", {}).get("skills", [])
    if len(protocol) != 8 or len(protocol) != len(set(protocol)):
        failures.append("protocol must contain eight unique skills")
    paths.extend("protocol/%s" % slug for slug in protocol)
    if len(paths) != len(set(paths)):
        failures.append("system catalog contains duplicate skill paths")
    return paths


def discover_skill_paths(catalog):
    paths = []
    for discipline in catalog.get("disciplines", {}):
        for skill_file in ROOT.glob("%s/*/*/SKILL.md" % discipline):
            paths.append(str(skill_file.parent.relative_to(ROOT)))
    for skill_file in ROOT.glob("protocol/*/SKILL.md"):
        paths.append(str(skill_file.parent.relative_to(ROOT)))
    return sorted(paths)


def check_catalog_shape(catalog, expected_paths, failures):
    required_top = {
        "$schema", "schema_version", "architecture_version", "bundle_version", "counts",
        "logical_order", "layers", "commands", "disciplines", "protocol", "registries",
        "auditors", "l1_dependency", "symmetry", "distribution_profiles",
    }
    if set(catalog) != required_top:
        failures.append("system catalog top-level keys differ from the strict contract")
    if catalog.get("$schema") != "./system-catalog.schema.json" or catalog.get("schema_version") != "1.1":
        failures.append("system catalog schema identity/version is invalid")
    counts = catalog.get("counts", {})
    actual = {
        "disciplines": len(catalog.get("disciplines", {})),
        "discipline_skills": len([path for path in expected_paths if not path.startswith("protocol/")]),
        "protocol_skills": len([path for path in expected_paths if path.startswith("protocol/")]),
        "total_skills": len(expected_paths),
        "commands": len(catalog.get("commands", [])),
        "registries": len(catalog.get("registries", [])),
        "auditors": len(catalog.get("auditors", [])),
    }
    if counts != actual:
        failures.append("catalog counts do not match catalog contents: expected %s, got %s" % (actual, counts))
    layers = catalog.get("layers", [])
    if [layer.get("id") for layer in layers] != ["L1", "L2", "L3", "L4"]:
        failures.append("layers must be ordered L1 through L4")
    layer_membership = {}
    flattened = []
    for layer in layers:
        layer_id = layer.get("id")
        for discipline in layer.get("disciplines", []):
            flattened.append(discipline)
            if discipline in layer_membership:
                failures.append("discipline %s appears in more than one layer" % discipline)
            else:
                layer_membership[discipline] = layer_id
    if flattened != catalog.get("logical_order"):
        failures.append("layer discipline order must equal logical_order")
    declared_layers = {
        discipline: spec.get("layer")
        for discipline, spec in catalog.get("disciplines", {}).items()
        if isinstance(spec, dict)
    }
    protocol = catalog.get("protocol", {})
    if isinstance(protocol, dict):
        declared_layers["protocol"] = protocol.get("layer")
    for discipline in catalog.get("logical_order", []):
        membership = layer_membership.get(discipline)
        declared = declared_layers.get(discipline)
        if membership != declared:
            failures.append(
                "%s declares layer %r but layer membership is %r"
                % (discipline, declared, membership)
            )


def check_skills(catalog, expected_paths, failures):
    discovered = discover_skill_paths(catalog)
    if sorted(expected_paths) != discovered:
        failures.append(
            "catalog/filesystem skill mismatch; missing=%s unknown=%s"
            % (sorted(set(expected_paths) - set(discovered)), sorted(set(discovered) - set(expected_paths)))
        )
    discipline_lookup = {}
    for discipline, spec in catalog["disciplines"].items():
        for phase, slugs in spec["phases"].items():
            for slug in slugs:
                discipline_lookup["%s/%s/%s" % (discipline, phase, slug)] = (discipline, phase, slug)
    for slug in catalog["protocol"]["skills"]:
        discipline_lookup["protocol/%s" % slug] = ("protocol", "protocol", slug)
    auditor_slugs = set()
    for path in expected_paths:
        skill_file = ROOT / path / "SKILL.md"
        if not skill_file.is_file():
            continue
        try:
            values, metadata = frontmatter(skill_file)
        except ArchitectureError as exc:
            failures.append(str(exc))
            continue
        discipline, phase, slug = discipline_lookup[path]
        if values.get("name") != slug:
            failures.append("%s frontmatter name does not match directory" % path)
        if metadata.get("discipline") != discipline or metadata.get("phase") != phase:
            failures.append("%s metadata discipline/phase drift" % path)
        if metadata.get("version") != values.get("version"):
            failures.append("%s top-level and metadata versions differ" % path)
        if values.get("class") == "auditor":
            auditor_slugs.add(slug)
    declared_auditors = {auditor["skill"] for auditor in catalog["auditors"]}
    if auditor_slugs != declared_auditors:
        failures.append("class: auditor set differs from catalog auditors")


def check_distribution(catalog, expected_paths, failures):
    plugin = load_json(PLUGIN_PATH)
    expected_plugin = ["./" + path for path in expected_paths]
    if plugin.get("skills") != expected_plugin:
        failures.append("plugin skill list must exactly follow system-catalog logical/phase order")
    if plugin.get("version") != catalog.get("bundle_version"):
        failures.append("system catalog bundle_version differs from plugin version")
    if plugin.get("commands") != ["./commands/"]:
        failures.append("plugin commands declaration must be ./commands/")
    commands = catalog.get("commands", [])
    actual_commands = sorted(path.stem for path in (ROOT / "commands").glob("*.md"))
    if sorted(commands) != actual_commands or len(commands) != len(set(commands)):
        failures.append("command files differ from catalog commands")
    groupings = load_json(GROUPINGS_PATH)
    grouped = [slug for group in groupings.get("groupings", []) for slug in group.get("skills", [])]
    expected_slugs = [path.rsplit("/", 1)[-1] for path in expected_paths]
    if grouped != expected_slugs or len(grouped) != len(set(grouped)):
        failures.append("skills.sh groupings must follow catalog order and cover every skill exactly once")
    for marketplace_path in MARKETPLACE_PATHS:
        marketplace = load_json(marketplace_path)
        plugins = marketplace.get("plugins", [])
        if len(plugins) != 1 or plugins[0].get("skills") != expected_plugin:
            failures.append("%s skill list must exactly follow catalog order" % marketplace_path.relative_to(ROOT))
        if plugins and plugins[0].get("description") != plugin.get("description"):
            failures.append("%s plugin description differs from plugin.json" % marketplace_path.relative_to(ROOT))
    if MARKETPLACE_PATHS[0].read_bytes() != MARKETPLACE_PATHS[1].read_bytes():
        failures.append("marketplace mirrors are not byte-identical")
    openclaw = load_json(OPENCLAW_PATH)
    if openclaw.get("version") != catalog.get("bundle_version"):
        failures.append("openclaw.plugin.json version differs from catalog bundle_version")
    if openclaw.get("description") != plugin.get("description"):
        failures.append("openclaw.plugin.json description differs from plugin.json")
    hooks = load_json(HOOKS_PATH).get("hooks", {})
    expected_hook_events = {
        "SessionStart", "UserPromptSubmit", "PreToolUse", "PostToolUse",
        "PostToolUseFailure", "PostToolBatch", "Stop",
    }
    if set(hooks) != expected_hook_events:
        failures.append("plugin hooks must declare the seven operated events")
    expected_hook_modes = {
        "SessionStart": "session-start",
        "UserPromptSubmit": "user-prompt-submit",
        "PreToolUse": "pre-tool-use",
        "PostToolUse": "post-tool-use",
        "PostToolUseFailure": "post-tool-failure",
        "PostToolBatch": "post-tool-batch",
        "Stop": "stop",
    }
    for event, mode in expected_hook_modes.items():
        entries = hooks.get(event, [])
        commands = entries[0].get("hooks", []) if len(entries) == 1 else []
        command = commands[0] if len(commands) == 1 else {}
        expected_args = ["${CLAUDE_PLUGIN_ROOT}/hooks/claude-hook.sh", mode]
        if (
                command.get("type") != "command" or command.get("command") != "bash"
                or command.get("args") != expected_args):
            failures.append("%s must invoke claude-hook.sh with mode %s" % (event, mode))
    for event in ("PreToolUse", "PostToolUse", "PostToolUseFailure"):
        entries = hooks.get(event, [])
        matcher = entries[0].get("matcher", "") if len(entries) == 1 else ""
        for tool in ("Write", "Edit", "NotebookEdit", "Bash", "PowerShell", "Monitor", "mcp__"):
            if tool not in matcher:
                failures.append("%s hook matcher does not cover %s" % (event, tool))
    for event in ("PreToolUse", "PostToolUse", "PostToolUseFailure", "PostToolBatch", "Stop"):
        entries = hooks.get(event, [])
        commands = entries[0].get("hooks", []) if len(entries) == 1 else []
        timeout = commands[0].get("timeout") if len(commands) == 1 else None
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or timeout < 60:
            failures.append("%s operated guard must retain a timeout of at least 60 seconds" % event)
    hook_runner = (ROOT / "hooks" / "claude-hook.sh").read_text(encoding="utf-8")
    for token in (
        "pre-tool-use", "check-memory-private.py", "--preflight-hook", "post-tool-use",
        "post-tool-failure", "post-tool-batch", "run-events.py", "record-hook", "resume",
        "AARON_ACTIVE_RUN_ID", "pma", "saa", "stop_hook_active",
    ):
        if token not in hook_runner:
            failures.append("hook runner is missing operated guard %r" % token)
    if "check-pii.py\" --staged" not in (ROOT / ".githooks" / "pre-commit").read_text(
            encoding="utf-8"):
        failures.append("pre-commit must scan staged index blobs")
    if "check-pii.py --tracked" not in (
            ROOT / ".github" / "workflows" / "validate-skill.yml").read_text(encoding="utf-8"):
        failures.append("CI must scan every tracked index blob")
    if "git config core.hooksPath .githooks" not in (
            ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"):
        failures.append("CONTRIBUTING must document pre-commit hook activation")


def check_frameworks(catalog, failures):
    framework_catalog = load_json(FRAMEWORK_PATH)
    declared = {
        framework
        for discipline in catalog["disciplines"].values()
        for framework in discipline.get("frameworks", [])
    }
    actual = set(framework_catalog.get("frameworks", {}))
    if declared != actual or len(actual) != 8:
        failures.append("discipline frameworks and framework catalog differ")
    auditor_frameworks = {auditor["framework"] for auditor in catalog["auditors"]}
    if auditor_frameworks != actual:
        failures.append("every framework must have exactly one catalogued auditor")


def load_registry_runtime():
    spec = importlib.util.spec_from_file_location("registry_events", REGISTRY_RUNTIME)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_registries(catalog, failures):
    runtime = load_registry_runtime()
    registries = catalog["registries"]
    keys = [entry["key"] for entry in registries]
    owners = {entry["key"]: entry["owner"] for entry in registries}
    if len(keys) != len(set(keys)) or set(keys) != runtime.REGISTRIES:
        failures.append("system catalog registry keys differ from runtime")
    if owners != runtime.OWNERS:
        failures.append("system catalog registry owners differ from runtime")
    protocol_skills = set(catalog["protocol"]["skills"])
    for entry in registries:
        key = entry["key"]
        owner = entry["owner"]
        if owner not in protocol_skills:
            failures.append("registry owner is not a protocol skill: %s" % owner)
        if entry.get("stream") != "memory/events/%s.ndjson" % key:
            failures.append("registry %s stream path is not canonical" % key)
        if entry.get("projection") != "memory/projections/%s.json" % key:
            failures.append("registry %s projection path is not canonical" % key)
        owner_path = ROOT / "protocol" / owner / "SKILL.md"
        text = owner_path.read_text(encoding="utf-8") if owner_path.is_file() else ""
        for token in (
                entry["stream"], "registry-events.py", "accept", "reject", "expected_revision", "verify",
                "AARON_SKILLS_ROOT", "CLAUDE_PLUGIN_ROOT", "standalone",
        ):
            present = token.lower() in text.lower() if token == "standalone" else token in text
            if not present:
                failures.append("%s owner contract is missing %r" % (owner, token))
        machine = entry.get("state_machine")
        runtime_graph = runtime.TRANSITION_GRAPHS.get(key)
        if machine is None and runtime_graph is not None:
            failures.append("registry %s runtime state machine is absent from catalog" % key)
        elif machine is not None:
            expected_initial = {machine["initial"]}
            expected_graph = {state: set(targets) for state, targets in machine["transitions"].items()}
            if runtime_graph is None or runtime_graph.get(None) != expected_initial:
                failures.append("registry %s initial state differs from runtime" % key)
            elif {state: targets for state, targets in runtime_graph.items() if state is not None} != expected_graph:
                failures.append("registry %s transitions differ from runtime" % key)


def check_auditors(catalog, failures):
    seen_skills = set()
    seen_sinks = set()
    for auditor in catalog["auditors"]:
        skill = auditor["skill"]
        path = ROOT / auditor["path"] / "SKILL.md"
        if skill in seen_skills or auditor["sink"] in seen_sinks:
            failures.append("auditor skills and sinks must be one-to-one")
        seen_skills.add(skill)
        seen_sinks.add(auditor["sink"])
        if path.parent.name != skill or not path.is_file():
            failures.append("auditor path is invalid for %s" % skill)
            continue
        text = path.read_text(encoding="utf-8")
        runtime = path.parent / "references" / "auditor-runtime.md"
        for token in (
                "class: auditor", "references/auditor-runtime.md", auditor["sink"],
                "status", "verdict", "explicit", "validate-audit-artifact.py",
                "runtime-invocation.md", "AARON_SKILLS_ROOT", "score_state: NOT_SCORED",
                "full-content Write"):
            if token not in text:
                failures.append("%s contract is missing %r" % (skill, token))
        if not runtime.is_file() or "GENERATED FILE" not in runtime.read_text(encoding="utf-8")[:200]:
            failures.append("%s standalone runtime is missing or not generated" % skill)
        sinks = {"memory/audits/%s/" % match for match in re.findall(r"memory/audits/([^/\s`]+)/?", text)}
        if sinks - {auditor["sink"]}:
            failures.append("%s references another auditor's write sink: %s" % (skill, sorted(sinks)))
        if MUTABLE_RUNTIME.search(text):
            failures.append("%s contains a mutable-main runtime fallback" % skill)


def check_l1_dependency(catalog, failures):
    dependency = catalog["l1_dependency"]
    required = dependency.get("required_fields", [])
    statuses = dependency.get("dependency_status_values", [])
    if required != ["narrative_canon_id", "narrative_canon_version", "claims_projection_offset", "dependency_status"]:
        failures.append("L1 dependency fields differ from the system-catalog contract")
    if statuses != ["verified", "approved-fallback", "blocked"]:
        failures.append("L1 dependency statuses differ from the system-catalog contract")
    builders = dependency.get("builders", [])
    if len(builders) != 7 or len(builders) != len(set(builders)):
        failures.append("L1 dependency must cover seven unique core builders")
    for path in builders:
        skill_path = ROOT / path / "SKILL.md"
        if not skill_path.is_file():
            failures.append("L1 builder path is missing: %s" % path)
            continue
        text = skill_path.read_text(encoding="utf-8")
        for token in required + statuses + [
                "memory/projections/narrative.json", "memory/projections/claims.json"]:
            if token.lower() not in text.lower():
                failures.append("L1 builder %s is missing dependency token %r" % (path, token))


SYMMETRY_RULES = {
    "SYM-01-loop-derived", "SYM-02-loop-acronym", "SYM-03-command-selector",
    "SYM-04-registry-link", "SYM-05-owner-naming", "SYM-06-gate-naming",
    "SYM-07-auditor-suffix", "SYM-08-gate-topology", "SYM-09-human-view",
    "SYM-10-score-surface-typed", "SYM-11-score-surface-consistent",
    "SYM-12-grouping-title", "SYM-13-scope-edge", "SYM-14-command-h1",
    "SYM-15-metadata-keys", "SYM-16-deviation-hygiene", "SYM-17-auto-order",
}
METADATA_KEYS = {"author", "version", "discipline", "phase", "geo-relevance", "hermes", "openclaw"}
RESERVED_SCORE_TOKEN = re.compile(r"\b(?:RQS|EQS|SQS)\b")


def command_text(name):
    path = ROOT / "commands" / ("%s.md" % name)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def check_symmetry(catalog, expected_paths, failures):
    """Conform-or-declared: every SYM rule violation must be licensed by a deviation,
    and every deviation must still license a live violation (stale deviations fail)."""
    symmetry = catalog.get("symmetry", {})
    rules = symmetry.get("rules", {})
    deviations = symmetry.get("deviations", [])
    if set(rules) != SYMMETRY_RULES:
        failures.append("symmetry.rules keys differ from the implemented SYM rule set")

    disciplines = catalog.get("disciplines", {})
    registries = catalog.get("registries", [])
    auditors = catalog.get("auditors", [])
    fw_catalog = load_json(FRAMEWORK_PATH).get("frameworks", {})
    violations = set()

    # SYM-01 / SYM-02 — loop string and loop_name acronym derive from phase_order.
    for name, spec in disciplines.items():
        order = spec.get("phase_order", [])
        if spec.get("loop") != " -> ".join(phase.title() for phase in order):
            violations.add(("SYM-01-loop-derived", "discipline:%s" % name))
        if "".join(phase[:1] for phase in order).upper() != spec.get("loop_name"):
            violations.add(("SYM-02-loop-acronym", "discipline:%s" % name))

    # SYM-03 — --phase is the only documented selector and matches phase_order.
    for name, spec in disciplines.items():
        command = spec.get("command", {})
        scope = "command:%s" % command.get("name", name)
        text = command_text(command.get("name", name))
        advertised = "--phase %s" % "|".join(command.get("values", []))
        conforms = (
            command.get("name") == name
            and command.get("selector") == "phase"
            and command.get("values") == spec.get("phase_order")
            and text is not None
            and advertised in text
            and "--mode" not in text
        )
        if not conforms:
            violations.add(("SYM-03-command-selector", scope))

    # SYM-04 — registry bijection + each command names its stream or owner.
    registry_by_key = {entry["key"]: entry for entry in registries}
    used_keys = [spec.get("registry") for spec in disciplines.values()]
    if sorted(used_keys) != sorted(registry_by_key):
        failures.append("discipline registry links are not a bijection with the catalog registries")
    for name, spec in disciplines.items():
        entry = registry_by_key.get(spec.get("registry"))
        text = command_text(spec.get("command", {}).get("name", name)) or ""
        if entry is None or (entry["stream"] not in text and entry["owner"] not in text):
            violations.add(("SYM-04-registry-link", "discipline:%s" % name))

    # SYM-05 / SYM-09 — registry owner naming and human-view canonical path.
    for entry in registries:
        if not entry.get("owner", "").endswith("-registry"):
            violations.add(("SYM-05-owner-naming", "registry:%s" % entry["key"]))
        if entry.get("human_view") != "memory/%s/" % entry["key"]:
            violations.add(("SYM-09-human-view", "registry:%s" % entry["key"]))

    # SYM-06 / SYM-08 — gate naming, and gates == the 8 auditors in their home disciplines.
    auditor_by_skill = {entry["skill"]: entry for entry in auditors}
    all_gates = []
    for name, spec in disciplines.items():
        for gate in spec.get("gates", []):
            all_gates.append(gate)
            if not gate.endswith("-auditor"):
                violations.add(("SYM-06-gate-naming", "auditor:%s" % gate))
            entry = auditor_by_skill.get(gate)
            if entry is None or not entry["path"].startswith("%s/" % name):
                failures.append("gate %s is not a catalog auditor resident in %s/" % (gate, name))
    if sorted(all_gates) != sorted(auditor_by_skill):
        failures.append("discipline gates do not enumerate exactly the 8 catalog auditors")

    # SYM-07 / SYM-15 — the -auditor suffix is reserved; metadata key set is uniform.
    for path in expected_paths:
        skill_file = ROOT / path / "SKILL.md"
        values, metadata = frontmatter(skill_file)
        if path.rsplit("/", 1)[-1].endswith("-auditor") and values.get("class") != "auditor":
            violations.add(("SYM-07-auditor-suffix", "skill:%s" % path))
        if set(metadata) != METADATA_KEYS:
            violations.add(("SYM-15-metadata-keys", "skill:%s" % path))

    # SYM-10 / SYM-11 — score surface typing and consistency with benchmark + framework catalog.
    for entry in auditors:
        scope = "auditor:%s" % entry["skill"]
        surface = entry.get("score_surface")
        if (
            not isinstance(surface, dict)
            or surface.get("type") not in {"composite", "diagnostic", "profiles-only"}
            or surface.get("rollup") not in {"weighted-arithmetic-mean", "geometric-mean", "none"}
        ):
            violations.add(("SYM-10-score-surface-typed", scope))
            continue
        benchmark = next(
            (source for source in entry.get("runtime_sources", [])
             if source.endswith("-benchmark.md") or source.endswith("-domain-rating.md")),
            None,
        )
        benchmark_text = (ROOT / benchmark).read_text(encoding="utf-8") if benchmark else ""
        framework = fw_catalog.get(entry.get("framework"), {})
        if surface["type"] in {"composite", "diagnostic"}:
            consistent = (
                isinstance(surface.get("name"), str)
                and surface["name"] in benchmark_text
                and surface["rollup"] != "none"
            )
            if surface["rollup"] == "geometric-mean":
                consistent = consistent and (
                    framework.get("cross_scope_rollup", {}).get("method") == "geometric-mean"
                )
        else:
            consistent = (
                surface.get("name") is None
                and surface["rollup"] == "none"
                and framework.get("composite_score") is False
                and not RESERVED_SCORE_TOKEN.search(benchmark_text)
            )
        if not consistent:
            violations.add(("SYM-11-score-surface-consistent", scope))

    # SYM-12 — skills.sh grouping titles carry loop_name, frameworks, phase chain, count.
    groupings = load_json(GROUPINGS_PATH).get("groupings", [])
    ordered = [name for name in catalog.get("logical_order", []) if name in disciplines]
    for index, name in enumerate(ordered):
        if index >= len(groupings):
            break
        spec = disciplines[name]
        title = groupings[index].get("title", "").translate(str.maketrans({"³": "3"}))
        chain = " → ".join(spec["phase_order"])
        wanted = [spec["loop_name"], chain, "(16)"] + [
            framework.replace("³", "3") for framework in spec["frameworks"]
        ]
        if any(token not in title for token in wanted):
            violations.add(("SYM-12-grouping-title", "discipline:%s" % name))

    # SYM-13 / SYM-14 — Scope edge blocks and command H1 convention.
    display_names = {spec["command"]["name"]: spec["display_name"] for spec in disciplines.values()}
    for name in catalog.get("commands", []):
        text = command_text(name)
        if text is None:
            failures.append("commands/%s.md is missing" % name)
            continue
        if name in display_names and "**Scope edge" not in text:
            violations.add(("SYM-13-scope-edge", "command:%s" % name))
        heading = next((line for line in text.splitlines() if line.startswith("# ")), "")
        titles = {name.title(), name.replace("-", " ").title(), display_names.get(name, "")}
        if heading not in {"# %s Command" % title for title in titles if title}:
            violations.add(("SYM-14-command-h1", "command:%s" % name))

    # SYM-17 — auto.md resolver enumerates discipline commands in logical order.
    auto_text = command_text("auto") or ""
    positions = [auto_text.find("/aaron-marketing:%s`" % name) for name in ordered]
    if -1 in positions or positions != sorted(positions):
        violations.add(("SYM-17-auto-order", "command:auto"))

    # SYM-16 + engine — subtract licensed deviations; leftovers and stale licenses fail.
    licensed = set()
    known_scopes = (
        {"discipline:%s" % name for name in disciplines}
        | {"registry:%s" % entry["key"] for entry in registries}
        | {"auditor:%s" % entry["skill"] for entry in auditors}
        | {"command:%s" % name for name in catalog.get("commands", [])}
        | {"skill:%s" % path for path in expected_paths}
    )
    for deviation in deviations:
        rule = deviation.get("rule")
        scope = deviation.get("scope")
        if rule not in SYMMETRY_RULES or scope not in known_scopes:
            failures.append("deviation %s names an unknown rule or scope" % deviation.get("id"))
            continue
        source = deviation.get("source_doc")
        if source and not (ROOT / source).is_file():
            failures.append("deviation %s cites a missing source_doc" % deviation.get("id"))
        licensed.add((rule, scope))
    for rule, scope in sorted(violations - licensed):
        failures.append("symmetry violation %s at %s has no licensed deviation" % (rule, scope))
    for rule, scope in sorted(licensed - violations):
        failures.append("stale deviation: %s at %s no longer violates and must be removed" % (rule, scope))


def markdown_files():
    excluded_parts = {".git", ".planning", ".agents", ".codex", "reference-oss"}
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in excluded_parts for part in relative.parts):
            continue
        if re.search(r"(?:^| )\d+\.md$", path.name) or " 2" in path.name:
            continue
        yield path


def check_legacy_and_producers(catalog, failures):
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        if BARE_ROOT_RUNTIME_COMMAND.search(text):
            failures.append(
                "root runtime command does not resolve AARON_SKILLS_ROOT in %s" % relative
            )
        if relative != "VERSIONS.md" and "candidates.md" in text:
            failures.append("legacy destructive candidate path remains in %s" % relative)
        if relative != "VERSIONS.md" and re.search(
                r"\bbatch-promote\b|\bday close\b|3\+ candidate", text, re.I):
            failures.append("legacy batch/threshold registry semantics remain in %s" % relative)
    normative = [
        "README.md", "CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md",
        "commands/ad.md", "commands/email.md", "commands/launch.md", "commands/social.md", "commands/narrative.md",
        "references/ramp-benchmark.md", "references/echo-benchmark.md", "references/tale-benchmark.md",
        "launch/mobilize/launch-readiness-auditor/SKILL.md",
        "social/host/social-quality-auditor/SKILL.md",
        "narrative/evaluate/narrative-quality-auditor/SKILL.md",
    ]
    normative.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / "docs").glob("README.*.md")))
    for relative in normative:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if LEGACY_COMPOSITE.search(text):
            failures.append("obsolete RAMP/ECHO/TALE composite terminology remains in %s" % relative)
        if LEGACY_SCORING.search(text):
            failures.append("obsolete scoring terminology remains in %s" % relative)
    readmes = [ROOT / "README.md", *sorted((ROOT / "docs").glob("README.*.md"))]
    for path in readmes:
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        missing_hook_terms = [
            term for term in (
                "PreToolUse", "PostToolUse", "PostToolUseFailure", "PostToolBatch",
                "Stop", "Artifact Gate",
            )
            if term not in text
        ]
        if missing_hook_terms:
            failures.append(
                "%s does not document the operated privacy/artifact hooks: %s"
                % (relative, ", ".join(missing_hook_terms))
            )
        if FAIL_OPEN_GATE.search(text):
            failures.append("%s still documents a fail-open unmarked audit path" % relative)
    experiment_contracts = [
        ROOT / "ad" / "orchestrate" / "ad-test-designer" / "SKILL.md",
        ROOT / "email" / "deliver" / "send-experiment-designer" / "SKILL.md",
    ]
    for path in experiment_contracts:
        text = path.read_text(encoding="utf-8")
        relative = str(path.relative_to(ROOT))
        for token in ("Calculated", "decision: UNDECIDED", "precommitted", "helper"):
            if token not in text:
                failures.append("%s experiment contract is missing %r" % (relative, token))
    compatibility = ROOT / "docs" / "agent-compatibility.md"
    if MUTABLE_RUNTIME.search(compatibility.read_text(encoding="utf-8")):
        failures.append("agent compatibility still prescribes mutable-main auditor runtime fallback")
    owner_paths = {"protocol/%s/SKILL.md" % entry["owner"] for entry in catalog["registries"]}
    auditor_paths = {auditor["path"] + "/SKILL.md" for auditor in catalog["auditors"]}
    skill_paths = [*ROOT.glob("*/*/*/SKILL.md"), *ROOT.glob("protocol/*/SKILL.md")]
    for skill_path in skill_paths:
        relative = str(skill_path.relative_to(ROOT))
        text = skill_path.read_text(encoding="utf-8")
        if relative not in auditor_paths:
            for line_number, line in enumerate(text.splitlines(), 1):
                audit_path = line.find("memory/audits/")
                prefix = line[max(0, audit_path - 180):audit_path] if audit_path >= 0 else ""
                if (audit_path >= 0 and AUDIT_WRITE_INTENT.search(prefix)
                        and not AUDIT_WRITE_NEGATION.search(prefix)):
                    failures.append(
                        "non-auditor declares an auditor-sink write: %s:%d"
                        % (relative, line_number)
                    )
        if relative not in owner_paths and "memory/events/" in text:
            if "registry-events.py" not in text or "operation: propose" not in text:
                failures.append("event producer lacks runtime/propose boundary: %s" % relative)


def main():
    failures = []
    try:
        catalog = load_json(CATALOG_PATH)
        expected_paths = expected_skill_paths(catalog, failures)
        check_catalog_shape(catalog, expected_paths, failures)
        check_skills(catalog, expected_paths, failures)
        check_distribution(catalog, expected_paths, failures)
        check_frameworks(catalog, failures)
        check_registries(catalog, failures)
        check_auditors(catalog, failures)
        check_l1_dependency(catalog, failures)
        check_symmetry(catalog, expected_paths, failures)
        check_legacy_and_producers(catalog, failures)
    except (ArchitectureError, OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        failures.append("architecture check aborted safely: %s" % exc)
    if failures:
        print("ARCHITECTURE CONFORMANCE FAILED: %d issue(s)" % len(failures))
        for failure in failures:
            print("- " + failure)
        return 1
    print("architecture conformance clean: 4 layers, 7 disciplines, 120 skills, 8 auditors, 7 registries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
