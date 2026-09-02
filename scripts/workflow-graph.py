#!/usr/bin/env python3
"""Generate and validate the authoritative inter-skill workflow graph.

The compact JSON source is authoritative.  The expanded graph and Markdown
view are deterministic projections.  Existing ``## Next Best Skill`` blocks
are a documentation surface only: ``--check`` requires their explicit skill
targets to agree bidirectionally with source edges marked
``documentation_required``.

Python 3 stdlib only.
"""
from __future__ import annotations

from collections import defaultdict, deque
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = Path("references/workflow-graph.source.json")
GRAPH_REL = Path("references/workflow-graph.json")
DOC_REL = Path("docs/workflow-graph.md")
CATALOG_REL = Path("references/system-catalog.json")
CONTROL_BINDINGS_REL = Path("references/control-bindings.json")
EDGE_SHARD_DIR = Path("references/workflow-graph")
EDGE_SHARD_SCHEMA = "../workflow-graph-edge-shard.schema.json"
EDGE_SHARD_AUTHORITY = "authoritative-workflow-graph-source-shard"
EDGES_PER_SHARD = 40
SCHEMA_VERSION = "1.0"

NEXT_BEST_RE = re.compile(
    r"^## Next Best Skill\s*$(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL
)
SKILL_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+/SKILL\.md)\)")
BACKTICK_RE = re.compile(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`")
SAFE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")
EDGE_TYPES = {
    "sequential", "conditional", "gate", "memory", "cross-discipline",
    "reentry", "fan-out", "join",
}
LOOP_MODES = {"acyclic", "visited-set", "bounded-cycle"}
PERMISSIONS = {
    "none", "persistent-write-approval", "external-action-approval",
    "owner-capability", "safety-capability",
}
CONDITION_CODES = {
    "primary", "conditional", "alternate", "quality-gate", "governance",
    "remediation", "unclassified",
}
CONTROL_REQUIREMENT_CODES = {
    "action-intent", "action-receipt", "artifact-binding",
    "cycle-retro", "evidence-observation", "measurement-contract",
}
REQUIRED_INPUT_CODES = CONTROL_REQUIREMENT_CODES | {
    "handoff-summary", "condition-evidence", "audit-evidence",
    "registry-proposal", "failure-evidence", "cross-discipline-context",
    "execution-approval",
}
PRECONDITION_CODES = {
    "handoff-unambiguous", "required-inputs-present", "target-not-visited",
    "automatic-handoff-cap-available", "permission-approved", "gate-evidence-ready",
}
STOPPING_MODES = {"natural-stop", "terminal", "human-decision"}
STOPPING_CONDITION_CODES = {
    "objective-complete", "handoff-ambiguous", "automatic-handoff-cap-reached",
    "declared-terminal", "owner-decision-required", "permission-required",
}


class GraphError(ValueError):
    """The workflow graph contract is invalid or out of date."""


def canonical_json(value):
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    )


def pretty_json(value):
    return json.dumps(
        value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False,
    ) + "\n"


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_json_loads(raw, label):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise GraphError("%s contains duplicate JSON key %r" % (label, key))
            result[key] = value
        return result

    try:
        return json.loads(raw, object_pairs_hook=pairs)
    except GraphError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise GraphError("cannot parse %s as strict JSON: %s" % (label, exc)) from exc


def load_json(path, label=None):
    try:
        raw = Path(path).read_bytes()
    except OSError as exc:
        raise GraphError("cannot read %s: %s" % (label or path, exc)) from exc
    return strict_json_loads(raw.decode("utf-8"), label or str(path)), raw


def load_control_handoff_requirements(root, edges=None):
    """Load and close the edge-specific control handoff SSOT.

    The central document may omit ``handoff_requirements`` for compatibility.
    When present, every row is sorted, source-producible, and—when ``edges``
    are supplied—bound to one exact authoritative edge.
    """
    document, _raw = load_json(
        root / CONTROL_BINDINGS_REL, CONTROL_BINDINGS_REL.as_posix(),
    )
    required = {
        "$schema", "schema_version", "authority", "catalog_ref",
        "control_artifact_schema", "bindings",
    }
    optional = {"handoff_requirements"}
    _exact_keys(document, required, optional, "control bindings")
    if (
            document["$schema"] != "./control-bindings.schema.json"
            or document["schema_version"] != "1.0"
            or document["authority"] != "cross-discipline-control-bindings"
            or document["catalog_ref"] != CATALOG_REL.as_posix()
            or document["control_artifact_schema"]
            != "references/control-artifact.schema.json"):
        raise GraphError("control bindings identity is unsupported")
    bindings = document["bindings"]
    if not isinstance(bindings, dict):
        raise GraphError("control bindings.bindings must be an object")
    source_requirements = {}
    for skill_id, binding in bindings.items():
        if not isinstance(skill_id, str) or not SAFE_ID_RE.fullmatch(skill_id):
            raise GraphError("control binding has an invalid skill identity")
        _exact_keys(
            binding, {"skill_path", "control_requirements"}, set(),
            "control binding %s" % skill_id,
        )
        requirements = binding["control_requirements"]
        if (
                not isinstance(requirements, list)
                or not 1 <= len(requirements) <= len(CONTROL_REQUIREMENT_CODES)
                or requirements != sorted(requirements)
                or len(requirements) != len(set(requirements))
                or any(item not in CONTROL_REQUIREMENT_CODES for item in requirements)):
            raise GraphError(
                "control binding %s requirements are invalid or not sorted" % skill_id
            )
        source_requirements[skill_id] = set(requirements)

    handoffs = document.get("handoff_requirements")
    if handoffs is None:
        return {}
    if not isinstance(handoffs, dict) or not handoffs:
        raise GraphError(
            "control handoff requirements must be a non-empty object when present"
        )
    edge_by_id = None
    if edges is not None:
        edge_by_id = {
            edge.get("id"): edge for edge in edges
            if isinstance(edge, dict) and isinstance(edge.get("id"), str)
        }
    result = {}
    for edge_id, requirements in handoffs.items():
        if not isinstance(edge_id, str) or edge_id.count("--") != 1:
            raise GraphError("control handoff has invalid edge identity")
        source, target = edge_id.split("--", 1)
        if not SAFE_ID_RE.fullmatch(source) or not SAFE_ID_RE.fullmatch(target):
            raise GraphError("control handoff has invalid edge identity")
        if (
                not isinstance(requirements, list)
                or not 1 <= len(requirements) <= len(CONTROL_REQUIREMENT_CODES)
                or requirements != sorted(requirements)
                or len(requirements) != len(set(requirements))
                or any(item not in CONTROL_REQUIREMENT_CODES for item in requirements)):
            raise GraphError(
                "control handoff %s requirements are invalid or not sorted" % edge_id
            )
        if source not in source_requirements:
            raise GraphError("control handoff source is not bound: %s" % source)
        if not set(requirements) <= source_requirements[source]:
            raise GraphError(
                "control handoff %s exceeds source skill requirements" % edge_id
            )
        if edge_by_id is not None:
            edge = edge_by_id.get(edge_id)
            if edge is None:
                raise GraphError(
                    "control handoff references an unknown edge: %s" % edge_id
                )
            if edge.get("from") != source or edge.get("to") != target:
                raise GraphError(
                    "control handoff identity differs from edge endpoints: %s" % edge_id
                )
        result[edge_id] = list(requirements)
    return result


def catalog_nodes(catalog):
    """Return the complete typed node inventory from the system catalog."""
    nodes = []
    seen = set()
    for discipline, declaration in catalog.get("disciplines", {}).items():
        phases = declaration.get("phase_order", [])
        for phase_index, phase in enumerate(phases):
            for name in declaration.get("phases", {}).get(phase, []):
                if name in seen:
                    raise GraphError("system catalog repeats skill %s" % name)
                seen.add(name)
                nodes.append({
                    "id": name,
                    "layer": declaration.get("layer"),
                    "discipline": discipline,
                    "phase": phase,
                    "phase_index": phase_index,
                    "path": "%s/%s/%s/SKILL.md" % (discipline, phase, name),
                })
    for name in catalog.get("protocol", {}).get("skills", []):
        if name in seen:
            raise GraphError("system catalog repeats skill %s" % name)
        seen.add(name)
        nodes.append({
            "id": name,
            "layer": catalog.get("protocol", {}).get("layer"),
            "discipline": "protocol",
            "phase": "protocol",
            "phase_index": None,
            "path": "protocol/%s/SKILL.md" % name,
        })
    expected = catalog.get("counts", {}).get("total_skills")
    if expected is not None and len(nodes) != expected:
        raise GraphError(
            "system catalog declares %s skills but resolves %d" % (expected, len(nodes))
        )
    return nodes


def _condition_text(line):
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
    value = value.replace("**", "").replace("`", "")
    value = re.sub(r"^\s*[-*]\s*", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _condition_code(text, edge_type, target_id, auditors):
    lowered = text.lower()
    if target_id in auditors or edge_type == "gate":
        return "quality-gate"
    if edge_type == "memory":
        return "governance"
    if any(token in lowered for token in (
            " fix", "fix ", "resolve", "repair", "blocked", "mismatch",
            "failed", "failure", "remediat", "drift")):
        return "remediation"
    if "primary" in lowered:
        return "primary"
    if any(token in lowered for token in (
            "alternate", "also consider", "sibling", "otherwise", "or ")):
        return "alternate"
    if any(token in lowered for token in (
            "if ", "when ", "once ", "after ", "for each ", "next gap",
            "next question", "needs ", "need ")):
        return "conditional"
    return "unclassified"


def _required_inputs(
        edge_type, condition_code, permissions=None, control_requirements=None):
    values = {"handoff-summary"}
    if condition_code == "conditional":
        values.add("condition-evidence")
    if condition_code == "quality-gate":
        values.add("audit-evidence")
    if condition_code == "governance" or edge_type == "memory":
        values.add("registry-proposal")
    if condition_code == "remediation" or edge_type == "reentry":
        values.add("failure-evidence")
    if edge_type == "cross-discipline":
        values.add("cross-discipline-context")
    if "external-action-approval" in (permissions or []):
        values.add("execution-approval")
    values.update(control_requirements or ())
    return sorted(values)


def _precondition_codes(edge_type, permissions, condition_code=None):
    values = {
        "handoff-unambiguous", "required-inputs-present", "target-not-visited",
        "automatic-handoff-cap-available",
    }
    if permissions != ["none"]:
        values.add("permission-approved")
    if edge_type == "gate" or condition_code == "quality-gate":
        values.add("gate-evidence-ready")
    return sorted(values)


def _node_stopping_policies(nodes, auditors, terminal_nodes):
    policies = []
    terminals = set(terminal_nodes)
    for node in sorted(nodes, key=lambda item: item["id"]):
        if node["id"] in terminals:
            mode = "terminal"
            codes = ["declared-terminal"]
        elif node["id"] in auditors or node["discipline"] == "protocol":
            mode = "human-decision"
            codes = [
                "automatic-handoff-cap-reached", "owner-decision-required",
                "permission-required",
            ]
        else:
            mode = "natural-stop"
            codes = [
                "automatic-handoff-cap-reached", "handoff-ambiguous",
                "objective-complete",
            ]
        policies.append({"node": node["id"], "mode": mode, "condition_codes": codes})
    return policies


def markdown_declarations(root, nodes, auditors=None):
    """Read explicit targets and source-derived conditions from handoff blocks."""
    by_slug = {node["id"]: node for node in nodes}
    auditors = set(auditors or ())
    declarations = {}
    details = {}
    missing_blocks = []
    for node in nodes:
        skill_path = root / node["path"]
        try:
            text = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise GraphError("cannot read %s: %s" % (node["path"], exc)) from exc
        match = NEXT_BEST_RE.search(text)
        if not match:
            missing_blocks.append(node["id"])
            declarations[node["id"]] = set()
            continue
        block = match.group(1)
        targets = set()
        block_start_line = text[:match.start(1)].count("\n") + 1
        for offset, line in enumerate(block.splitlines(), 1):
            line_targets = []
            for _label, relative in SKILL_LINK_RE.findall(line):
                target_path = (skill_path.parent / relative).resolve()
                try:
                    target_path.relative_to(root.resolve())
                except ValueError as exc:
                    raise GraphError(
                        "%s Next Best Skill link escapes the repository: %s"
                        % (node["path"], relative)
                    ) from exc
                if target_path.name != "SKILL.md" or not target_path.is_file():
                    raise GraphError(
                        "%s Next Best Skill link is dangling: %s" % (node["path"], relative)
                    )
                slug = target_path.parent.name
                if slug not in by_slug:
                    raise GraphError(
                        "%s Next Best Skill link resolves outside the catalog: %s"
                        % (node["path"], slug)
                    )
                line_targets.append(slug)
            link_free = SKILL_LINK_RE.sub("", line)
            line_targets.extend(
                slug for slug in BACKTICK_RE.findall(link_free) if slug in by_slug
            )
            normalized = _condition_text(line)
            for slug in line_targets:
                targets.add(slug)
                pair = (node["id"], slug)
                if pair not in details:
                    edge_type = _edge_type(node, by_slug[slug], auditors)
                    details[pair] = {
                        "condition_text": normalized,
                        "condition_source": "%s:%d" % (
                            node["path"], block_start_line + offset - 1,
                        ),
                        "condition_code": _condition_code(
                            normalized, edge_type, slug, auditors,
                        ),
                    }
        declarations[node["id"]] = targets
    return declarations, missing_blocks, details


def _edge_type(source, target, auditors):
    if target["id"] in auditors:
        return "gate"
    if target["discipline"] == "protocol":
        return "memory"
    if source["discipline"] != target["discipline"]:
        return "cross-discipline"
    if source["phase_index"] is not None and target["phase_index"] is not None:
        if target["phase_index"] > source["phase_index"]:
            return "sequential"
        if target["phase_index"] < source["phase_index"]:
            return "reentry"
    return "conditional"


def _edge_permissions(target):
    if target["discipline"] != "protocol":
        return ["none"]
    if target["id"] == "consent-registry":
        return ["persistent-write-approval", "owner-capability", "safety-capability"]
    if target["id"].endswith("-registry"):
        return ["persistent-write-approval", "owner-capability"]
    return ["persistent-write-approval"]


def _strongly_connected_components(node_ids, edges):
    adjacency = defaultdict(list)
    for edge in edges:
        adjacency[edge["from"]].append(edge["to"])
    index = 0
    stack = []
    on_stack = set()
    indexes = {}
    lowlinks = {}
    result = []

    def visit(node):
        nonlocal index
        indexes[node] = lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in adjacency[node]:
            if target not in indexes:
                visit(target)
                lowlinks[node] = min(lowlinks[node], lowlinks[target])
            elif target in on_stack:
                lowlinks[node] = min(lowlinks[node], indexes[target])
        if lowlinks[node] == indexes[node]:
            component = set()
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.add(member)
                if member == node:
                    break
            result.append(component)

    for node in node_ids:
        if node not in indexes:
            visit(node)
    return result


def _edge_shard_documents(edges):
    documents = []
    descriptors = []
    for index in range(0, len(edges), EDGES_PER_SHARD):
        shard_edges = edges[index:index + EDGES_PER_SHARD]
        shard_id = "edges-%02d" % (index // EDGES_PER_SHARD)
        document = {
            "$schema": EDGE_SHARD_SCHEMA,
            "schema_version": SCHEMA_VERSION,
            "authority": EDGE_SHARD_AUTHORITY,
            "shard_id": shard_id,
            "edges": shard_edges,
        }
        raw = pretty_json(document).encode("utf-8")
        relative = EDGE_SHARD_DIR / (shard_id + ".json")
        documents.append((relative, document, raw))
        descriptors.append({
            "id": shard_id,
            "ref": relative.as_posix(),
            "sha256": sha256_bytes(raw),
            "edge_count": len(shard_edges),
            "first_edge_id": shard_edges[0]["id"],
            "last_edge_id": shard_edges[-1]["id"],
        })
    return documents, descriptors


def bootstrap_source(root):
    """Create a one-time explicit source from current Markdown declarations.

    This operation is intentionally separate from normal generation.  Once the
    source exists, it is the authority and must be edited directly; ``--write``
    never re-imports prose.
    """
    source_path = root / SOURCE_REL
    if source_path.exists():
        raise GraphError("refusing to overwrite existing authoritative source")
    catalog, _ = load_json(root / CATALOG_REL, str(CATALOG_REL))
    nodes = catalog_nodes(catalog)
    by_id = {node["id"]: node for node in nodes}
    auditors = {item["skill"] for item in catalog.get("auditors", [])}
    declarations, _missing, handoff_details = markdown_declarations(root, nodes, auditors)
    edges = []
    for source_id, targets in sorted(declarations.items()):
        for target_id in sorted(targets):
            source = by_id[source_id]
            target = by_id[target_id]
            edge_type = _edge_type(source, target, auditors)
            permissions = _edge_permissions(target)
            detail = handoff_details[(source_id, target_id)]
            edge = {
                "id": "%s--%s" % (source_id, target_id),
                "from": source_id,
                "to": target_id,
                "type": edge_type,
                "condition_code": detail["condition_code"],
                "condition_text": detail["condition_text"],
                "condition_source": detail["condition_source"],
                "required_inputs": _required_inputs(
                    edge_type, detail["condition_code"], permissions,
                ),
                "precondition_codes": _precondition_codes(
                    edge_type, permissions, detail["condition_code"],
                ),
                "permissions": permissions,
                "gate": target_id if target_id in auditors else None,
                "loop_policy": {"mode": "acyclic", "max_traversals": 1},
                "documentation_required": True,
                "exception": None,
            }
            if (
                    source["discipline"] == target["discipline"]
                    and source["discipline"] != "protocol"
                    and target["phase_index"] < source["phase_index"]):
                edge["exception"] = {
                    "code": "documented-bounded-reentry",
                    "reason": (
                        "Remediation returns to an earlier phase and remains bounded by "
                        "the global visited-set and three-handoff limit."
                    ),
                }
            edges.append(edge)

    handoff_requirements = load_control_handoff_requirements(root, edges)
    for edge in edges:
        edge["required_inputs"] = _required_inputs(
            edge["type"], edge["condition_code"], edge["permissions"],
            handoff_requirements.get(edge["id"]),
        )

    components = _strongly_connected_components(by_id, edges)
    cyclic_pairs = set()
    for component in components:
        self_loop = any(
            edge["from"] == edge["to"] and edge["from"] in component for edge in edges
        )
        if len(component) > 1 or self_loop:
            for edge in edges:
                if edge["from"] in component and edge["to"] in component:
                    cyclic_pairs.add((edge["from"], edge["to"]))
    for edge in edges:
        if (edge["from"], edge["to"]) in cyclic_pairs:
            edge["loop_policy"] = {"mode": "visited-set", "max_traversals": 1}

    outgoing = defaultdict(int)
    incoming = defaultdict(int)
    for edge in edges:
        outgoing[edge["from"]] += 1
        incoming[edge["to"]] += 1
    terminal_nodes = sorted(node for node in by_id if not outgoing[node])
    node_exceptions = []
    for node in sorted(by_id):
        if not outgoing[node] and not incoming[node]:
            node_exceptions.append({
                "node": node,
                "code": "direct-router-standalone",
                "reason": (
                    "The skill is directly routable but has no declared inter-skill edge; "
                    "it is an explicit standalone terminal until a handoff is authored."
                ),
            })

    shard_documents, shard_descriptors = _edge_shard_documents(edges)
    source = {
        "$schema": "./workflow-graph-source.schema.json",
        "schema_version": SCHEMA_VERSION,
        "catalog_version": catalog["architecture_version"],
        "node_source": CATALOG_REL.as_posix(),
        "entrypoint_policy": "all-catalog-skills-directly-routable",
        "automatic_handoff_policy": {
            "max_automatic_handoffs": 3,
            "visited_set_required": True,
            "ambiguity_stop": True,
        },
        "terminal_nodes": terminal_nodes,
        "node_exceptions": node_exceptions,
        "node_stopping_policies": _node_stopping_policies(
            nodes, auditors, terminal_nodes,
        ),
        "edge_shards": shard_descriptors,
        "workflows": [],
        "bootstrap_provenance": {
            "method": "one-time-explicit-import",
            "source_surface": "Markdown Next Best Skill declarations",
            "authority_after_import": SOURCE_REL.as_posix(),
            "inference_rules": [
                "Only explicit SKILL.md links and exact backticked catalog skill IDs were imported.",
                "Auditor targets were typed as gates; protocol targets as memory edges; cross-discipline targets as cross-discipline edges; same-discipline phase order supplied sequential or reentry types.",
                "Protocol targets inherited persistent-write and owner/safety capability requirements; all other imported targets defaulted to no additional permission.",
                "Strongly connected imported edges received a one-traversal visited-set policy under the graph-level three-handoff cap; cycles do not receive blanket exceptions.",
                "Every node received an explicit natural-stop, terminal, or human-decision stopping policy; earlier-phase returns alone received a documented-bounded-reentry exception.",
            ],
            "curation_overrides": [],
            "note": (
                "Markdown was used only to create the initial explicit edge inventory; "
                "normal generation never treats prose as authoritative."
            ),
        },
    }
    edge_shard_dir_path = root / EDGE_SHARD_DIR
    edge_shard_dir_path.mkdir(parents=True, exist_ok=True)
    for relative, _document, raw in shard_documents:
        (root / relative).write_bytes(raw)
    source_path.write_text(pretty_json(source), encoding="utf-8")
    return source


def _exact_keys(value, required, optional, label):
    if not isinstance(value, dict):
        raise GraphError("%s must be an object" % label)
    missing = required - set(value)
    unknown = set(value) - required - optional
    if missing or unknown:
        raise GraphError(
            "%s fields are invalid (missing=%s unknown=%s)"
            % (label, sorted(missing), sorted(unknown))
        )


def load_authoritative_source(root):
    source, source_raw = load_json(root / SOURCE_REL, str(SOURCE_REL))
    if "edges" in source:
        raise GraphError(
            "legacy inline edge inventory detected; run --split-source once"
        )
    descriptors = source.get("edge_shards")
    if not isinstance(descriptors, list) or not descriptors:
        raise GraphError("workflow graph source requires edge_shards")
    edges = []
    seen_shards = set()
    seen_refs = set()
    shard_raws = {}
    for index, descriptor in enumerate(descriptors):
        label = "edge_shards[%d]" % index
        _exact_keys(
            descriptor,
            {"id", "ref", "sha256", "edge_count", "first_edge_id", "last_edge_id"},
            set(), label,
        )
        shard_id = descriptor["id"]
        expected_ref = (EDGE_SHARD_DIR / (shard_id + ".json")).as_posix()
        if (
                not SAFE_ID_RE.fullmatch(shard_id)
                or shard_id in seen_shards
                or descriptor["ref"] in seen_refs
                or descriptor["ref"] != expected_ref):
            raise GraphError("%s identity/ref is unsafe or duplicated" % label)
        seen_shards.add(shard_id)
        seen_refs.add(descriptor["ref"])
        if not isinstance(descriptor["edge_count"], int) or descriptor["edge_count"] < 1:
            raise GraphError("%s edge_count must be positive" % label)
        if not re.fullmatch(r"[0-9a-f]{64}", descriptor["sha256"]):
            raise GraphError("%s sha256 is invalid" % label)
        document, raw = load_json(root / descriptor["ref"], descriptor["ref"])
        if sha256_bytes(raw) != descriptor["sha256"]:
            raise GraphError("%s digest mismatch" % label)
        _exact_keys(
            document,
            {"$schema", "schema_version", "authority", "shard_id", "edges"},
            set(), label + " document",
        )
        if (
                document["$schema"] != EDGE_SHARD_SCHEMA
                or document["schema_version"] != SCHEMA_VERSION
                or document["authority"] != EDGE_SHARD_AUTHORITY
                or document["shard_id"] != shard_id):
            raise GraphError("%s document identity/authority mismatch" % label)
        shard_edges = document["edges"]
        if (
                not isinstance(shard_edges, list)
                or len(shard_edges) != descriptor["edge_count"]
                or not shard_edges
                or shard_edges[0].get("id") != descriptor["first_edge_id"]
                or shard_edges[-1].get("id") != descriptor["last_edge_id"]):
            raise GraphError("%s boundary/count metadata mismatch" % label)
        edges.extend(shard_edges)
        shard_raws[descriptor["ref"]] = raw
    return source, source_raw, edges, shard_raws


def validate_source(source, catalog, root, edges):
    required = {
        "$schema", "schema_version", "catalog_version", "node_source",
        "entrypoint_policy", "automatic_handoff_policy", "terminal_nodes",
        "node_exceptions", "node_stopping_policies", "edge_shards", "workflows",
        "bootstrap_provenance",
    }
    _exact_keys(source, required, set(), "workflow graph source")
    if source["schema_version"] != SCHEMA_VERSION:
        raise GraphError("unsupported workflow graph source schema_version")
    if source["catalog_version"] != catalog.get("architecture_version"):
        raise GraphError("workflow graph source catalog_version drift")
    if source["node_source"] != CATALOG_REL.as_posix():
        raise GraphError("workflow graph node_source must be %s" % CATALOG_REL)
    if source["entrypoint_policy"] != "all-catalog-skills-directly-routable":
        raise GraphError("unsupported workflow graph entrypoint policy")
    automatic_policy = source["automatic_handoff_policy"]
    _exact_keys(
        automatic_policy,
        {"max_automatic_handoffs", "visited_set_required", "ambiguity_stop"},
        set(), "automatic_handoff_policy",
    )
    if (
            automatic_policy["max_automatic_handoffs"] != 3
            or automatic_policy["visited_set_required"] is not True
            or automatic_policy["ambiguity_stop"] is not True):
        raise GraphError(
            "automatic handoffs require a three-hop cap, visited set, and ambiguity stop"
        )
    provenance = source["bootstrap_provenance"]
    _exact_keys(
        provenance,
        {
            "method", "source_surface", "authority_after_import", "inference_rules",
            "curation_overrides", "note",
        },
        set(), "bootstrap_provenance",
    )
    if (
            provenance["method"] != "one-time-explicit-import"
            or provenance["authority_after_import"] != SOURCE_REL.as_posix()
            or not isinstance(provenance["source_surface"], str)
            or not provenance["source_surface"].strip()
            or not isinstance(provenance["note"], str)
            or not provenance["note"].strip()):
        raise GraphError("bootstrap provenance identity is invalid")
    if not isinstance(provenance["inference_rules"], list) or not provenance["inference_rules"] or not all(
            isinstance(rule, str) and rule.strip() for rule in provenance["inference_rules"]):
        raise GraphError("bootstrap provenance requires explicit inference_rules")
    if not isinstance(provenance["curation_overrides"], list):
        raise GraphError("bootstrap provenance curation_overrides must be an array")
    nodes = catalog_nodes(catalog)
    by_id = {node["id"]: node for node in nodes}
    terminals = source["terminal_nodes"]
    if not isinstance(terminals, list) or len(terminals) != len(set(terminals)):
        raise GraphError("terminal_nodes must be a unique array")
    if any(item not in by_id for item in terminals):
        raise GraphError("terminal_nodes contains a dangling node")

    stopping_by_node = {}
    policies = source["node_stopping_policies"]
    if not isinstance(policies, list):
        raise GraphError("node_stopping_policies must be an array")
    for item in policies:
        _exact_keys(
            item, {"node", "mode", "condition_codes"}, set(),
            "node stopping policy",
        )
        node_id = item["node"]
        if node_id not in by_id or node_id in stopping_by_node:
            raise GraphError("node stopping policy is dangling or duplicated")
        if item["mode"] not in STOPPING_MODES:
            raise GraphError("node stopping policy mode is unsupported")
        codes = item["condition_codes"]
        if (
                not isinstance(codes, list) or not codes
                or len(codes) != len(set(codes))
                or any(code not in STOPPING_CONDITION_CODES for code in codes)):
            raise GraphError("node stopping policy condition_codes are invalid")
        if item["mode"] == "terminal" and node_id not in terminals:
            raise GraphError("terminal stopping policy requires terminal_nodes membership")
        if node_id in terminals and item["mode"] != "terminal":
            raise GraphError("terminal node requires terminal stopping policy")
        stopping_by_node[node_id] = item
    if set(stopping_by_node) != set(by_id):
        raise GraphError(
            "every catalog node requires an explicit stopping policy (missing=%s extra=%s)"
            % (sorted(set(by_id) - set(stopping_by_node)), sorted(set(stopping_by_node) - set(by_id)))
        )

    exception_nodes = set()
    if not isinstance(source["node_exceptions"], list):
        raise GraphError("node_exceptions must be an array")
    for index, item in enumerate(source["node_exceptions"]):
        _exact_keys(item, {"node", "code", "reason"}, set(), "node exception")
        if item["node"] not in by_id or item["node"] in exception_nodes:
            raise GraphError("node exception is dangling or duplicated")
        if not SAFE_ID_RE.fullmatch(item["code"]) or not item["reason"].strip():
            raise GraphError("node exception requires a safe code and non-empty reason")
        exception_nodes.add(item["node"])

    if not isinstance(edges, list):
        raise GraphError("edges must be an array")
    if sum(item["edge_count"] for item in source["edge_shards"]) != len(edges):
        raise GraphError("edge shard counts do not match the loaded edge inventory")
    ids = set()
    pairs = set()
    for index, edge in enumerate(edges):
        label = "edge[%d]" % index
        _exact_keys(edge, {
            "id", "from", "to", "type", "condition_code", "condition_text",
            "condition_source", "required_inputs", "precondition_codes", "permissions",
            "gate", "loop_policy", "documentation_required", "exception",
        }, set(), label)
        if not SAFE_ID_RE.fullmatch(edge["id"]):
            raise GraphError("%s id is unsafe" % label)
        if edge["id"] in ids or (edge["from"], edge["to"]) in pairs:
            raise GraphError("%s duplicates an edge identity or pair" % label)
        ids.add(edge["id"])
        pairs.add((edge["from"], edge["to"]))
        if edge["from"] not in by_id or edge["to"] not in by_id:
            raise GraphError("%s is dangling" % label)
        if edge["from"] == edge["to"]:
            raise GraphError("%s self-loop is not permitted" % label)
        if edge["type"] not in EDGE_TYPES:
            raise GraphError("%s has unsupported type" % label)
        if edge["condition_code"] not in CONDITION_CODES:
            raise GraphError("%s condition_code is unsupported" % label)
        if not isinstance(edge["condition_text"], str) or not edge["condition_text"].strip():
            raise GraphError("%s condition_text must be source-derived and non-empty" % label)
        if not isinstance(edge["condition_source"], str) or not re.fullmatch(
                r"[A-Za-z0-9_./-]+/SKILL\.md:[1-9][0-9]*", edge["condition_source"]):
            raise GraphError("%s condition_source must identify a SKILL.md line" % label)
        if (
                not isinstance(edge["required_inputs"], list)
                or not edge["required_inputs"]
                or len(edge["required_inputs"]) != len(set(edge["required_inputs"]))
                or edge["required_inputs"] != sorted(edge["required_inputs"])
                or any(value not in REQUIRED_INPUT_CODES for value in edge["required_inputs"])):
            raise GraphError("%s required_inputs are invalid" % label)
        if (
                not isinstance(edge["precondition_codes"], list)
                or not edge["precondition_codes"]
                or len(edge["precondition_codes"]) != len(set(edge["precondition_codes"]))
                or any(value not in PRECONDITION_CODES for value in edge["precondition_codes"])):
            raise GraphError("%s precondition_codes are invalid" % label)
        if not isinstance(edge["permissions"], list) or not edge["permissions"]:
            raise GraphError("%s permissions must be non-empty" % label)
        if any(value not in PERMISSIONS for value in edge["permissions"]):
            raise GraphError("%s has unsupported permission" % label)
        if edge["gate"] is not None and edge["gate"] not in by_id:
            raise GraphError("%s gate is dangling" % label)
        if edge["type"] == "gate" and (
                edge["gate"] not in {edge["from"], edge["to"]}
                or edge["condition_code"] != "quality-gate"
                or "audit-evidence" not in edge["required_inputs"]):
            raise GraphError("%s gate edge lacks a bound quality-gate contract" % label)
        if edge["type"] == "gate" and edge["gate"] == edge["from"] and (
                "external-action-approval" not in edge["permissions"]
                or "execution-approval" not in edge["required_inputs"]
                or "permission-approved" not in edge["precondition_codes"]
                or "gate-evidence-ready" not in edge["precondition_codes"]):
            raise GraphError(
                "%s release gate requires independent execution approval" % label
            )
        if not isinstance(edge["documentation_required"], bool):
            raise GraphError("%s documentation_required must be boolean" % label)
        loop_policy = edge["loop_policy"]
        _exact_keys(loop_policy, {"mode", "max_traversals"}, set(), label + " loop_policy")
        if loop_policy["mode"] not in LOOP_MODES:
            raise GraphError("%s has unsupported loop mode" % label)
        maximum = loop_policy["max_traversals"]
        if not isinstance(maximum, int) or isinstance(maximum, bool) or not 1 <= maximum <= 3:
            raise GraphError("%s max_traversals must be 1..3" % label)
        exception = edge["exception"]
        if exception is not None:
            _exact_keys(exception, {"code", "reason"}, set(), label + " exception")
            if not SAFE_ID_RE.fullmatch(exception["code"]) or not exception["reason"].strip():
                raise GraphError("%s exception must be explicit" % label)
            if exception["code"] != "documented-bounded-reentry":
                raise GraphError("%s uses a blanket or unsupported edge exception" % label)

        source_node, target_node = by_id[edge["from"]], by_id[edge["to"]]
        inversion = (
            source_node["discipline"] == target_node["discipline"]
            and source_node["discipline"] != "protocol"
            and target_node["phase_index"] < source_node["phase_index"]
        )
        if inversion and (
                exception is None or exception["code"] != "documented-bounded-reentry"):
            raise GraphError("illegal phase inversion on %s requires an explicit exception" % edge["id"])
        if not inversion and exception is not None:
            raise GraphError("%s exception is unnecessary outside a phase reentry" % edge["id"])

    handoff_requirements = load_control_handoff_requirements(root, edges)
    for edge in edges:
        expected_inputs = _required_inputs(
            edge["type"], edge["condition_code"], edge["permissions"],
            handoff_requirements.get(edge["id"]),
        )
        if edge["required_inputs"] != expected_inputs:
            raise GraphError(
                "edge %s required_inputs drift from derived semantics and control handoff"
                % edge["id"]
            )

    override_ids = set()
    for item in provenance["curation_overrides"]:
        _exact_keys(
            item, {"id", "edges", "field", "value", "reason"}, set(),
            "curation override",
        )
        if not SAFE_ID_RE.fullmatch(item["id"]) or item["id"] in override_ids:
            raise GraphError("curation override id is unsafe or duplicated")
        override_ids.add(item["id"])
        if (
                not isinstance(item["edges"], list) or not item["edges"]
                or len(item["edges"]) != len(set(item["edges"]))
                or any(edge_id not in ids for edge_id in item["edges"])):
            raise GraphError("curation override contains a dangling or duplicated edge")
        if item["field"] != "type" or item["value"] not in EDGE_TYPES:
            raise GraphError("curation override field/value is unsupported")
        if not isinstance(item["reason"], str) or not item["reason"].strip():
            raise GraphError("curation override reason must be non-empty")
        edge_by_id = {edge["id"]: edge for edge in edges}
        if any(edge_by_id[edge_id]["type"] != item["value"] for edge_id in item["edges"]):
            raise GraphError("curation override no longer matches its declared edge values")

    components = _strongly_connected_components(by_id, edges)
    for component in components:
        if len(component) <= 1:
            continue
        internal = [
            edge for edge in edges
            if edge["from"] in component and edge["to"] in component
        ]
        unsafe = [
            edge["id"] for edge in internal
            if edge["loop_policy"] != {"mode": "visited-set", "max_traversals": 1}
        ]
        if unsafe:
            raise GraphError(
                "illegal cycle %s includes acyclic edges %s"
                % (sorted(component), sorted(unsafe))
            )

    outgoing = defaultdict(int)
    incoming = defaultdict(int)
    for edge in edges:
        outgoing[edge["from"]] += 1
        incoming[edge["to"]] += 1
    for node in by_id:
        if not outgoing[node] and node not in terminals:
            raise GraphError("dead end %s is not declared terminal" % node)
        if not outgoing[node] and not incoming[node] and node not in exception_nodes:
            raise GraphError("orphan node %s requires an explicit exception" % node)

    validate_workflows(
        source["workflows"], by_id,
        {(edge["from"], edge["to"]): edge for edge in edges},
    )
    auditors = {item["skill"] for item in catalog.get("auditors", [])}
    declarations, missing_blocks, handoff_details = markdown_declarations(
        root, nodes, auditors,
    )
    documented_pairs = {
        (edge["from"], edge["to"]) for edge in edges if edge["documentation_required"]
    }
    markdown_pairs = {
        (source_id, target_id)
        for source_id, targets in declarations.items() for target_id in targets
    }
    missing_in_markdown = sorted(documented_pairs - markdown_pairs)
    missing_in_source = sorted(markdown_pairs - documented_pairs)
    if missing_in_markdown or missing_in_source:
        raise GraphError(
            "Next Best Skill/source drift (missing_in_markdown=%s missing_in_source=%s)"
            % (missing_in_markdown, missing_in_source)
        )
    by_pair = {(edge["from"], edge["to"]): edge for edge in edges}
    semantic_drift = []
    for pair in sorted(documented_pairs):
        edge = by_pair[pair]
        detail = handoff_details[pair]
        expected_code = _condition_code(
            detail["condition_text"], edge["type"], edge["to"], auditors,
        )
        expected_inputs = _required_inputs(
            edge["type"], expected_code, edge["permissions"],
            handoff_requirements.get(edge["id"]),
        )
        expected_preconditions = _precondition_codes(
            edge["type"], edge["permissions"], expected_code,
        )
        if (
                edge["condition_code"] != expected_code
                or edge["condition_text"] != detail["condition_text"]
                or edge["condition_source"] != detail["condition_source"]
                or edge["required_inputs"] != expected_inputs
                or edge["precondition_codes"] != expected_preconditions):
            semantic_drift.append(edge["id"])
    if semantic_drift:
        raise GraphError(
            "source-derived edge semantic drift for %s" % semantic_drift
        )
    if missing_blocks:
        # Auditor skills currently use a compact runbook-owned handoff surface.
        # They may omit the heading only if they still declare graph targets nowhere.
        offenders = [node for node in missing_blocks if declarations[node]]
        if offenders:
            raise GraphError("skills with declarations are missing Next Best Skill blocks")
    return nodes


def validate_workflows(workflows, by_id, edge_by_pair):
    if not isinstance(workflows, list) or not workflows:
        raise GraphError("at least one named workflow is required")
    ids = set()
    for index, workflow in enumerate(workflows):
        label = "workflow[%d]" % index
        _exact_keys(workflow, {
            "id", "objective", "entry_node", "nodes", "fan_outs", "joins",
            "terminal_nodes", "edge_ids", "max_cycles", "deadline_seconds", "budgets",
        }, set(), label)
        if not SAFE_ID_RE.fullmatch(workflow["id"]) or workflow["id"] in ids:
            raise GraphError("%s id is unsafe or duplicated" % label)
        ids.add(workflow["id"])
        if not isinstance(workflow["objective"], str) or not workflow["objective"].strip():
            raise GraphError("%s objective must be non-empty" % label)
        node_set = set(workflow["nodes"])
        if (
                not node_set or len(node_set) != len(workflow["nodes"])
                or any(node not in by_id for node in node_set)):
            raise GraphError("%s nodes are empty, duplicated, or dangling" % label)
        if workflow["entry_node"] not in node_set:
            raise GraphError("%s entry_node must belong to the workflow" % label)
        terminals = workflow["terminal_nodes"]
        if not terminals or any(node not in node_set for node in terminals):
            raise GraphError("%s terminal_nodes are invalid" % label)
        if not 1 <= workflow["max_cycles"] <= 3:
            raise GraphError("%s max_cycles must be 1..3" % label)
        if not 60 <= workflow["deadline_seconds"] <= 2_592_000:
            raise GraphError("%s deadline_seconds must be 60..2592000" % label)
        budgets = workflow["budgets"]
        _exact_keys(
            budgets,
            {
                "max_events", "max_actions", "max_retries", "max_verifications",
                "max_memory_proposals", "stall_limit",
            },
            set(), label + " budgets",
        )
        for name, minimum, maximum in (
                ("max_events", 8, 512), ("max_actions", 1, 256),
                ("max_retries", 0, 32),
                ("max_verifications", 1, 64), ("max_memory_proposals", 0, 16),
                ("stall_limit", 2, 8)):
            value = budgets[name]
            if not isinstance(value, int) or isinstance(value, bool) or not minimum <= value <= maximum:
                raise GraphError("%s budget %s is out of range" % (label, name))

        all_edges_by_id = {edge["id"]: edge for edge in edge_by_pair.values()}
        selected_ids = workflow["edge_ids"]
        if (
                not isinstance(selected_ids, list)
                or len(selected_ids) != len(set(selected_ids))
                or any(edge_id not in all_edges_by_id for edge_id in selected_ids)):
            raise GraphError("%s edge_ids are empty, duplicated, or dangling" % label)
        selected_edges = {edge_id: all_edges_by_id[edge_id] for edge_id in selected_ids}
        if not selected_edges:
            raise GraphError("%s must select at least one authoritative edge" % label)
        if any(
                edge["from"] not in node_set or edge["to"] not in node_set
                for edge in selected_edges.values()):
            raise GraphError("%s selected edge escapes the workflow node set" % label)
        selected_by_pair = {
            (edge["from"], edge["to"]): edge for edge in selected_edges.values()
        }
        selected_components = _strongly_connected_components(node_set, selected_edges.values())
        if any(len(component) > 1 for component in selected_components):
            raise GraphError(
                "%s selected execution topology must be acyclic; outer loop cycles "
                "are governed by max_cycles" % label
            )
        adjacency = defaultdict(set)
        for source, target in selected_by_pair:
            adjacency[source].add(target)
        fanout_sources = set()
        branch_starts = set()
        for fanout in workflow["fan_outs"]:
            _exact_keys(fanout, {"from", "branches"}, set(), label + " fan-out")
            if fanout["from"] not in node_set or fanout["from"] in fanout_sources:
                raise GraphError("%s fan-out source is invalid or duplicated" % label)
            fanout_sources.add(fanout["from"])
            branches = fanout["branches"]
            if not isinstance(branches, dict) or len(branches) < 2:
                raise GraphError("%s fan-out requires at least two named branches" % label)
            for branch, start in branches.items():
                if not SAFE_ID_RE.fullmatch(branch) or start not in node_set:
                    raise GraphError("%s fan-out branch is invalid" % label)
                edge = selected_by_pair.get((fanout["from"], start))
                if edge is None:
                    raise GraphError("%s fan-out lacks an authoritative graph edge" % label)
                if edge["type"] != "fan-out":
                    raise GraphError("%s fan-out edge must have type fan-out" % label)
                branch_starts.add(start)
        join_nodes = set()
        for join in workflow["joins"]:
            _exact_keys(
                join,
                {
                    "id", "at", "requires", "policy", "branch_failure_policy",
                    "timeout_policy", "partial_evidence_policy",
                },
                set(), label + " join",
            )
            if (
                    not SAFE_ID_RE.fullmatch(join["id"])
                    or join["at"] not in node_set
                    or join["at"] in join_nodes
                    or join["policy"] != "all-required"
                    or join["branch_failure_policy"] != "fail-closed-escalate"
                    or join["timeout_policy"] != "workflow-deadline-escalate"
                    or join["partial_evidence_policy"] != "reject-partial"
                    or len(join["requires"]) < 2):
                raise GraphError("%s join is invalid" % label)
            join_nodes.add(join["at"])
            for required_node in join["requires"]:
                edge = selected_by_pair.get((required_node, join["at"]))
                if required_node not in node_set or edge is None:
                    raise GraphError("%s join lacks a required authoritative edge" % label)
                if edge["type"] != "join":
                    raise GraphError("%s join edge must have type join" % label)

        reachable = set()
        queue = deque([workflow["entry_node"]])
        while queue:
            node = queue.popleft()
            if node in reachable:
                continue
            reachable.add(node)
            queue.extend(sorted(adjacency[node]))
        if node_set - reachable:
            raise GraphError(
                "%s has unreachable workflow nodes %s" % (label, sorted(node_set - reachable))
            )
        for node in node_set - set(terminals):
            if not adjacency[node]:
                raise GraphError("%s has undeclared dead end %s" % (label, node))
        if any(adjacency[node] for node in terminals):
            raise GraphError("%s terminal node has an outgoing selected edge" % label)


def build_graph(source, catalog, source_raw, catalog_raw, root, edges):
    nodes = validate_source(source, catalog, root, edges)
    terminals = set(source["terminal_nodes"])
    exceptions = {item["node"]: item for item in source["node_exceptions"]}
    stopping = {item["node"]: item for item in source["node_stopping_policies"]}
    expanded_nodes = []
    for node in nodes:
        expanded_nodes.append({
            **node,
            "entrypoint": True,
            "terminal": node["id"] in terminals,
            "exception": exceptions.get(node["id"]),
            "stopping_mode": stopping[node["id"]]["mode"],
        })
    graph = {
        "$schema": "./workflow-graph.schema.json",
        "schema_version": SCHEMA_VERSION,
        "catalog_version": source["catalog_version"],
        "automatic_handoff_policy": source["automatic_handoff_policy"],
        "authority": {
            "source": SOURCE_REL.as_posix(),
            "source_sha256": sha256_bytes(source_raw),
            "node_source": CATALOG_REL.as_posix(),
            "node_source_sha256": sha256_bytes(catalog_raw),
            "markdown_role": "bidirectionally-checked-documentation-only",
        },
        "counts": {
            "nodes": len(expanded_nodes),
            "edges": len(edges),
            "workflows": len(source["workflows"]),
        },
        "nodes": expanded_nodes,
        "edge_shards": source["edge_shards"],
        "workflows": source["workflows"],
    }
    graph["graph_sha256"] = sha256_bytes(
        canonical_json(graph).encode("utf-8")
    )
    return graph


def render_doc(graph):
    lines = [
        "<!-- GENERATED FILE: run `python3 scripts/workflow-graph.py --write`; do not edit. -->",
        "",
        "# Workflow Graph",
        "",
        "The authoritative source is [`references/workflow-graph.source.json`](../references/workflow-graph.source.json). Existing `Next Best Skill` prose is a bidirectionally checked documentation surface, never the authority.",
        "The source manifest pins context-budgeted authoritative edge shards by SHA-256; consumers load only the shards they need.",
        "",
        "- Nodes: **%d**" % graph["counts"]["nodes"],
        "- Edges: **%d**" % graph["counts"]["edges"],
        "- Named workflows: **%d**" % graph["counts"]["workflows"],
        "- Graph digest: `sha256:%s`" % graph["graph_sha256"],
        "",
        "## Named Workflows",
        "",
    ]
    for workflow in graph["workflows"]:
        lines.extend([
            "### %s" % workflow["id"],
            "",
            workflow["objective"],
            "",
            "- Entry: `%s`" % workflow["entry_node"],
            "- Terminals: %s" % ", ".join("`%s`" % value for value in workflow["terminal_nodes"]),
            "- Selected authoritative edges: **%d**" % len(workflow["edge_ids"]),
            "- Maximum cycles: %d" % workflow["max_cycles"],
            "",
        ])
        for fanout in workflow["fan_outs"]:
            branches = ", ".join(
                "%s → `%s`" % (name, target)
                for name, target in sorted(fanout["branches"].items())
            )
            lines.append("- Fan-out from `%s`: %s" % (fanout["from"], branches))
        for join in workflow["joins"]:
            lines.append(
                "- Join `%s` at `%s` requires %s (%s)."
                % (
                    join["id"], join["at"],
                    ", ".join("`%s`" % value for value in join["requires"]),
                    join["policy"],
                )
            )
        lines.append("")
    lines.extend([
        "## Contract",
        "",
        "An edge typed `gate` with `gate` bound to its source auditor is a release gate: `audit-evidence` and an independent `execution-approval` are both required before its successor may open. Non-SHIP verdicts remain closed.",
        "",
        "`python3 scripts/workflow-graph.py --check` detects projection drift, dangling edges, documentation drift, orphan nodes, unreachable workflow nodes, illegal cycles, undeclared phase inversions, and undeclared dead ends.",
        "",
    ])
    return "\n".join(lines)


def outputs(root):
    source, source_raw, edges, _shard_raws = load_authoritative_source(root)
    catalog, catalog_raw = load_json(root / CATALOG_REL, str(CATALOG_REL))
    graph = build_graph(source, catalog, source_raw, catalog_raw, root, edges)
    return {
        GRAPH_REL: pretty_json(graph),
        DOC_REL: render_doc(graph),
    }, graph


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / (".%s.workflow-tmp" % path.name)
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def split_legacy_source(root):
    """One-time mechanical migration from an inline edge array to shards."""
    source, _raw = load_json(root / SOURCE_REL, str(SOURCE_REL))
    edges = source.pop("edges", None)
    if not isinstance(edges, list) or not edges:
        raise GraphError("source has no legacy inline edges to split")
    documents, descriptors = _edge_shard_documents(edges)
    source["edge_shards"] = descriptors
    for relative, document, _raw in documents:
        atomic_write(root / relative, pretty_json(document))
    atomic_write(root / SOURCE_REL, pretty_json(source))
    return len(edges), len(documents)


def reindex_edge_shards(root):
    """Validate edited authoritative shards and refresh manifest metadata."""
    source, _raw = load_json(root / SOURCE_REL, str(SOURCE_REL))
    descriptors = source.get("edge_shards")
    if not isinstance(descriptors, list) or not descriptors:
        raise GraphError("source has no edge_shards to reindex")
    refreshed = []
    edges = []
    for index, descriptor in enumerate(descriptors):
        shard_id = descriptor.get("id") if isinstance(descriptor, dict) else None
        if not isinstance(shard_id, str) or not SAFE_ID_RE.fullmatch(shard_id):
            raise GraphError("edge shard %d has an invalid id" % index)
        relative = EDGE_SHARD_DIR / (shard_id + ".json")
        document, raw = load_json(root / relative, relative.as_posix())
        _exact_keys(
            document,
            {"$schema", "schema_version", "authority", "shard_id", "edges"},
            set(), "edge shard %s" % shard_id,
        )
        shard_edges = document["edges"]
        if (
                document["$schema"] != EDGE_SHARD_SCHEMA
                or document["schema_version"] != SCHEMA_VERSION
                or document["authority"] != EDGE_SHARD_AUTHORITY
                or document["shard_id"] != shard_id
                or not isinstance(shard_edges, list)
                or not 1 <= len(shard_edges) <= EDGES_PER_SHARD):
            raise GraphError("edge shard %s identity/count contract is invalid" % shard_id)
        refreshed.append({
            "id": shard_id,
            "ref": relative.as_posix(),
            "sha256": sha256_bytes(raw),
            "edge_count": len(shard_edges),
            "first_edge_id": shard_edges[0].get("id"),
            "last_edge_id": shard_edges[-1].get("id"),
        })
        edges.extend(shard_edges)
    candidate = dict(source)
    candidate["edge_shards"] = refreshed
    catalog, _catalog_raw = load_json(root / CATALOG_REL, str(CATALOG_REL))
    validate_source(candidate, catalog, root, edges)
    atomic_write(root / SOURCE_REL, pretty_json(candidate))
    return len(edges), len(refreshed)


def upgrade_edge_semantics(root):
    """One-time semantic migration from generic prose fields to typed evidence."""
    source, _source_raw, edges, _shards = load_authoritative_source(root)
    catalog, _catalog_raw = load_json(root / CATALOG_REL, str(CATALOG_REL))
    nodes = catalog_nodes(catalog)
    by_id = {node["id"]: node for node in nodes}
    auditors = {item["skill"] for item in catalog.get("auditors", [])}
    declarations, _missing, details = markdown_declarations(root, nodes, auditors)
    declared_pairs = {
        (source_id, target_id)
        for source_id, targets in declarations.items() for target_id in targets
    }
    edge_pairs = {(edge["from"], edge["to"]) for edge in edges}
    if declared_pairs != edge_pairs:
        raise GraphError("cannot upgrade while Markdown/source edge identities drift")
    handoff_requirements = load_control_handoff_requirements(root, edges)

    components = _strongly_connected_components(by_id, edges)
    cyclic_pairs = set()
    for component in components:
        if len(component) > 1:
            cyclic_pairs.update(
                (edge["from"], edge["to"])
                for edge in edges
                if edge["from"] in component and edge["to"] in component
            )
    condition_counts = defaultdict(int)
    reentry_count = 0
    for edge in edges:
        pair = (edge["from"], edge["to"])
        detail = details[pair]
        code = _condition_code(
            detail["condition_text"], edge["type"], edge["to"], auditors,
        )
        edge.pop("condition", None)
        edge.pop("preconditions", None)
        edge["condition_code"] = code
        edge["condition_text"] = detail["condition_text"]
        edge["condition_source"] = detail["condition_source"]
        edge["required_inputs"] = _required_inputs(
            edge["type"], code, edge["permissions"],
            handoff_requirements.get(edge["id"]),
        )
        edge["precondition_codes"] = _precondition_codes(
            edge["type"], edge["permissions"], code,
        )
        edge["loop_policy"] = {
            "mode": "visited-set" if pair in cyclic_pairs else "acyclic",
            "max_traversals": 1,
        }
        source_node, target_node = by_id[edge["from"]], by_id[edge["to"]]
        inversion = (
            source_node["discipline"] == target_node["discipline"]
            and source_node["discipline"] != "protocol"
            and target_node["phase_index"] < source_node["phase_index"]
        )
        if inversion:
            edge["exception"] = {
                "code": "documented-bounded-reentry",
                "reason": (
                    "Remediation returns to an earlier phase and remains bounded by "
                    "the graph-level visited set and three-automatic-handoff cap."
                ),
            }
            reentry_count += 1
        else:
            edge["exception"] = None
        condition_counts[code] += 1

    terminal_nodes = source.get("terminal_nodes", [])
    source["automatic_handoff_policy"] = {
        "max_automatic_handoffs": 3,
        "visited_set_required": True,
        "ambiguity_stop": True,
    }
    source["node_stopping_policies"] = _node_stopping_policies(
        nodes, auditors, terminal_nodes,
    )
    for workflow in source.get("workflows", []):
        for join in workflow.get("joins", []):
            join["branch_failure_policy"] = "fail-closed-escalate"
            join["timeout_policy"] = "workflow-deadline-escalate"
            join["partial_evidence_policy"] = "reject-partial"
    source["bootstrap_provenance"]["inference_rules"] = [
        "Only explicit SKILL.md links and exact backticked catalog skill IDs were imported.",
        "Each condition_text and condition_source is the normalized authored Next Best Skill line; a closed classifier assigns primary, conditional, alternate, quality-gate, governance, remediation, or explicit unclassified.",
        "Required-input and precondition codes are deterministically derived from the classified condition, edge type, permissions, and gate metadata.",
        "Auditor targets are gates; protocol targets are memory edges; cross-discipline targets are cross-discipline edges; same-discipline phase order supplies sequential or reentry types, subject to recorded curation overrides.",
        "Strongly connected edges use one-traversal visited-set policies under the graph-level three-handoff cap; cycles receive no blanket exceptions and earlier-phase reentries alone require an exception.",
        "Every node has an explicit natural-stop, terminal, or human-decision stopping policy.",
    ]
    documents, descriptors = _edge_shard_documents(edges)
    source["edge_shards"] = descriptors
    validate_source(source, catalog, root, edges)
    for relative, document, _raw in documents:
        atomic_write(root / relative, pretty_json(document))
    atomic_write(root / SOURCE_REL, pretty_json(source))
    return len(edges), len(documents), dict(sorted(condition_counts.items())), reentry_count


def check(root):
    generated, graph = outputs(root)
    failures = []
    for relative, expected in generated.items():
        path = root / relative
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError:
            failures.append("missing generated file: %s" % relative)
            continue
        if actual != expected:
            failures.append("stale generated file: %s" % relative)
    return failures, graph


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--bootstrap-source", action="store_true")
    group.add_argument("--split-source", action="store_true")
    group.add_argument("--reindex-shards", action="store_true")
    group.add_argument("--upgrade-edge-semantics", action="store_true")
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--root", default=str(ROOT))
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    try:
        if args.bootstrap_source:
            source = bootstrap_source(root)
            print(
                "bootstrapped authoritative source with %d explicit edges; review and edit the JSON source"
                % sum(item["edge_count"] for item in source["edge_shards"])
            )
            return 0
        if args.split_source:
            edge_count, shard_count = split_legacy_source(root)
            print(
                "split %d authoritative edges into %d context-budgeted shards"
                % (edge_count, shard_count)
            )
            return 0
        if args.reindex_shards:
            edge_count, shard_count = reindex_edge_shards(root)
            print(
                "reindexed %d authoritative edges across %d shards"
                % (edge_count, shard_count)
            )
            return 0
        if args.upgrade_edge_semantics:
            edge_count, shard_count, condition_counts, reentry_count = upgrade_edge_semantics(root)
            print(
                "upgraded %d edges across %d shards; conditions=%s reentry_exceptions=%d"
                % (edge_count, shard_count, condition_counts, reentry_count)
            )
            return 0
        if args.write:
            generated, graph = outputs(root)
            for relative, content in generated.items():
                atomic_write(root / relative, content)
            print(
                "wrote workflow graph projection: %d nodes, %d edges, %d workflows"
                % (graph["counts"]["nodes"], graph["counts"]["edges"], graph["counts"]["workflows"])
            )
            return 0
        failures, graph = check(root)
        if failures:
            for failure in failures:
                print("FAIL " + failure)
            return 1
        print(
            "workflow graph current: %d nodes, %d edges, %d workflows"
            % (graph["counts"]["nodes"], graph["counts"]["edges"], graph["counts"]["workflows"])
        )
        return 0
    except GraphError as exc:
        print("workflow graph error: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
