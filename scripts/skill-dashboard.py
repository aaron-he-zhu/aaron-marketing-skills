#!/usr/bin/env python3
"""Skill Dashboard — local read-only projection of skill-run artifacts.

Python 3 stdlib only. Reads existing run/memory/audit/control files under a
project root and writes HTML (default), plus optional JSON/Markdown. This is
not a Skill, not an OSS install surface, not a hosted Web product, and not a
Gateway.

Usage:
  python3 scripts/skill-dashboard.py --root PATH [--out skill-dashboard.html]
  python3 scripts/skill-dashboard.py --root PATH --out out/ --json --md
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import sys


PRODUCT = "Skill Dashboard"
SCHEMA_VERSION = "1.0"
SCHEMA_REF = "references/skill-dashboard.schema.json"
DEFAULT_OUT = "skill-dashboard.html"
SCRIPT_ROOT = Path(__file__).resolve().parents[1]

UNBOUND_OUTCOMES = (
    "Business results are unvalidated/unbound. Skill Dashboard shows numeric "
    "before/after only when a measurement-contract exists, with supporting "
    "evidence, receipt, or retro as available. It does not invent outcome numbers."
)
EMPTY_STAFF = (
    "No AI Staff handoff chain was found. This is the expected empty state "
    "when the 8-bot roster is not in use."
)
EMPTY_NEXT = "No next action, open loop, or blocker is recorded."
EMPTY_USAGE = "No run envelopes were found under memory/runs/."
EMPTY_DELTA = "No artifact or audit before/after pair is available."
EMPTY_DECISIONS = "No propose or Accept decision items were found."
EMPTY_TRUST = "No evidence gaps, conflicts, or confidence notes were found."
EMPTY_COVERAGE = "No visited skills and no catalog coverage to project."
QUALITY_VERDICTS = ("SHIP", "FIX", "BLOCK", "UNDECIDED", "NOT_SCORED")
HEADING = re.compile(r"^#{1,6}\s+(.*)$")
LIST_ITEM = re.compile(r"^[-*]\s+(.*)$")
CHECKPOINT_LINE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


class DashboardError(ValueError):
    """Raised when the generator cannot write a usable local view."""


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def as_posix(path):
    return path.as_posix() if isinstance(path, Path) else str(path)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_load_json(path, errors, label=None):
    try:
        value = load_json(path)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        errors.append("skip %s: %s" % (label or as_posix(path), exc))
        return None
    if not isinstance(value, dict):
        errors.append("skip %s: not a JSON object" % (label or as_posix(path)))
        return None
    return value


def relative_to(root, path):
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def iter_files(directory, pattern):
    if not directory.is_dir():
        return
    for path in sorted(directory.rglob(pattern)):
        if path.is_file():
            yield path


def ref_path(value):
    if isinstance(value, str) and not value.startswith("opaque:"):
        return value
    if isinstance(value, dict):
        ref = value.get("ref")
        if isinstance(ref, str) and not ref.startswith("opaque:"):
            return ref
    return None


def artifact_refs(items):
    refs = []
    for item in items or []:
        ref = ref_path(item) if not isinstance(item, str) else (
            item if not item.startswith("opaque:") else None
        )
        if ref:
            refs.append(ref)
    return refs


def parse_markdown_sections(text):
    sections = {}
    current = "_preamble"
    sections[current] = []
    for raw in text.splitlines():
        heading = HEADING.match(raw.strip())
        if heading:
            current = heading.group(1).strip().lower()
            sections.setdefault(current, [])
            continue
        line = raw.strip()
        if not line or line in {"_(empty)_", "*(empty)*"}:
            continue
        item = LIST_ITEM.match(line)
        sections[current].append(item.group(1).strip() if item else line)
    return sections


def parse_checkpoint(text):
    values = {}
    for raw in text.splitlines():
        match = CHECKPOINT_LINE.match(raw.strip())
        if match:
            values[match.group(1)] = match.group(2).strip()
    return values


def parse_audit(text):
    record = {}
    for raw in text.splitlines():
        match = CHECKPOINT_LINE.match(raw.strip())
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip().strip("'\"")
        if key in {
            "framework", "verdict", "score_state", "status", "target",
            "observed_at", "score_confidence", "open_loops",
            "recommended_next_skill",
        }:
            record[key] = value
    return record


def quality_state(record=None):
    if not record:
        return {
            "verdict": "NOT_SCORED",
            "score_state": "NOT_SCORED",
            "observed_at": None,
        }
    verdict = record.get("verdict")
    if record.get("score_state") == "NOT_SCORED" and verdict not in QUALITY_VERDICTS:
        verdict = "NOT_SCORED"
    if verdict not in QUALITY_VERDICTS:
        verdict = "NOT_SCORED"
    score_state = record.get("score_state")
    if score_state not in {"SCORED", "NOT_SCORED"}:
        score_state = "NOT_SCORED" if verdict == "NOT_SCORED" else "SCORED"
    return {
        "verdict": verdict,
        "score_state": score_state,
        "observed_at": record.get("observed_at"),
    }


def load_catalog(root):
    for candidate in (
        root / "references" / "system-catalog.json",
        SCRIPT_ROOT / "references" / "system-catalog.json",
    ):
        if candidate.is_file():
            try:
                catalog = load_json(candidate)
            except (OSError, ValueError):
                continue
            if isinstance(catalog, dict):
                return catalog
    return None


def catalog_skills(catalog):
    mapping = {}
    if not catalog:
        return mapping
    disciplines = catalog.get("disciplines") or {}
    for name, spec in disciplines.items():
        if name == "protocol":
            continue
        phases = spec.get("phases") if isinstance(spec, dict) else None
        if not isinstance(phases, dict):
            continue
        for slugs in phases.values():
            if isinstance(slugs, list):
                for slug in slugs:
                    if isinstance(slug, str):
                        mapping[slug] = name
    protocol = catalog.get("protocol") or {}
    for slug in protocol.get("skills") or []:
        if isinstance(slug, str):
            mapping[slug] = "protocol"
    return mapping


def discover(root):
    errors = []
    notes = []
    runs = {}
    memory = root / "memory"
    runs_root = memory / "runs"
    if runs_root.is_dir():
        for run_dir in sorted(path for path in runs_root.iterdir() if path.is_dir()):
            run_id = run_dir.name
            record = {
                "run_id": run_id,
                "envelopes": [],
                "save_points": [],
                "events": [],
                "controls": [],
            }
            for path in iter_files(run_dir / "envelopes", "*.json"):
                value = safe_load_json(path, errors, relative_to(root, path))
                if value:
                    value["_path"] = relative_to(root, path)
                    record["envelopes"].append(value)
            for path in iter_files(run_dir / "save-points", "*.json"):
                value = safe_load_json(path, errors, relative_to(root, path))
                if value:
                    value["_path"] = relative_to(root, path)
                    record["save_points"].append(value)
            events_path = run_dir / "events.ndjson"
            if events_path.is_file():
                try:
                    for index, line in enumerate(
                        events_path.read_text(encoding="utf-8").splitlines(), 1
                    ):
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                        except ValueError as exc:
                            errors.append(
                                "skip %s:%d: %s"
                                % (relative_to(root, events_path), index, exc)
                            )
                            continue
                        if isinstance(event, dict):
                            record["events"].append(event)
                except OSError as exc:
                    errors.append("skip %s: %s" % (relative_to(root, events_path), exc))
            for path in iter_files(run_dir / "artifacts", "*.json"):
                value = safe_load_json(path, errors, relative_to(root, path))
                if value:
                    value["_path"] = relative_to(root, path)
                    record["controls"].append(value)
            runs[run_id] = record
    elif not memory.exists():
        notes.append(
            "No memory/ directory under --root. Conventional discovery paths "
            "are memory/runs/, memory/audits/, memory/control/, WARM files, "
            "and optional memory/staff/."
        )

    audits = []
    for path in iter_files(memory / "audits", "*.md"):
        try:
            record = parse_audit(path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append("skip %s: %s" % (relative_to(root, path), exc))
            continue
        record["_path"] = relative_to(root, path)
        audits.append(record)

    controls = []
    for path in iter_files(memory / "control", "*.json"):
        value = safe_load_json(path, errors, relative_to(root, path))
        if value:
            value["_path"] = relative_to(root, path)
            controls.append(value)
    for record in runs.values():
        controls.extend(record["controls"])

    warm = {}
    for name in ("open-loops.md", "decisions.md", "session-checkpoint.md", "hot-cache.md"):
        path = memory / name
        if path.is_file():
            try:
                warm[name] = path.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append("skip %s: %s" % (relative_to(root, path), exc))

    staff = {"roster": None, "handoffs": []}
    roster_path = memory / "staff" / "bot-roster.json"
    if roster_path.is_file():
        staff["roster"] = safe_load_json(roster_path, errors, relative_to(root, roster_path))
        if staff["roster"]:
            staff["roster"]["_path"] = relative_to(root, roster_path)
    for path in iter_files(memory / "staff" / "handoffs", "*.json"):
        value = safe_load_json(path, errors, relative_to(root, path))
        if value:
            value["_path"] = relative_to(root, path)
            staff["handoffs"].append(value)

    return {
        "runs": runs,
        "audits": audits,
        "controls": controls,
        "warm": warm,
        "staff": staff,
        "notes": notes,
        "errors": errors,
    }


def latest_envelope(run):
    envelopes = run.get("envelopes") or []
    if not envelopes:
        return None
    return sorted(
        envelopes,
        key=lambda item: (item.get("ended_at") or item.get("started_at") or "", item.get("_path") or ""),
    )[-1]


def latest_save_point(run):
    points = run.get("save_points") or []
    if not points:
        return None
    return sorted(
        points,
        key=lambda item: (item.get("created_at") or "", item.get("_path") or ""),
    )[-1]


def earliest_save_point(run):
    points = run.get("save_points") or []
    if not points:
        return None
    return sorted(
        points,
        key=lambda item: (item.get("created_at") or "", item.get("_path") or ""),
    )[0]


def project_next(sources):
    next_action = None
    open_loops = []
    blockers = []
    for run in sources["runs"].values():
        envelope = latest_envelope(run)
        save_point = latest_save_point(run)
        for holder in (envelope, save_point):
            if not holder:
                continue
            action = holder.get("next_action")
            if isinstance(action, dict) and action.get("code") and not next_action:
                next_action = action["code"]
            elif isinstance(action, str) and action and not next_action:
                next_action = action
            if holder.get("status") in {"blocked", "failed", "needs-input"}:
                blockers.append(
                    "%s status=%s" % (holder.get("run_id") or run["run_id"], holder.get("status"))
                )
            pending = holder.get("pending_handoff") if isinstance(holder, dict) else None
            if isinstance(pending, dict) and pending.get("status") in {"blocked", "needs-input"}:
                blockers.append(
                    "pending_handoff %s (%s)"
                    % (pending.get("recommended_skill") or "unknown", pending.get("status"))
                )
            if holder.get("failure_class"):
                blockers.append("failure_class=%s" % holder["failure_class"])
    loops_text = sources["warm"].get("open-loops.md")
    if loops_text:
        sections = parse_markdown_sections(loops_text)
        for key, rows in sections.items():
            if "active" in key or key == "open loops":
                open_loops.extend(rows)
        if not open_loops:
            open_loops.extend(
                row for key, rows in sections.items()
                if key != "resolved" and "superseded" not in key
                for row in rows
            )
    checkpoint = sources["warm"].get("session-checkpoint.md")
    if checkpoint:
        values = parse_checkpoint(checkpoint)
        resume = values.get("resume_instruction")
        if resume and resume not in {"<the first concrete action on resume, one line>", ""}:
            if not next_action:
                next_action = resume
        pending = values.get("pending_handoff")
        if pending and pending not in {"none", "<next skill slug or none>"}:
            if pending not in open_loops:
                open_loops.append("pending_handoff: %s" % pending)
    for audit in sources["audits"]:
        if audit.get("verdict") == "BLOCK" or audit.get("status") == "BLOCKED":
            blockers.append(
                "audit %s %s"
                % (audit.get("framework") or "unknown", audit.get("target") or audit.get("_path"))
            )
        loops = audit.get("open_loops")
        if loops and loops not in {"none", "[]"}:
            open_loops.append("%s: %s" % (audit.get("framework") or "audit", loops))
    open_loops = unique(open_loops)
    blockers = unique(blockers)
    return {
        "next_action": next_action,
        "open_loops": open_loops,
        "blockers": blockers,
        "empty": not (next_action or open_loops or blockers),
    }


def unique(items):
    seen = []
    for item in items:
        if item not in seen:
            seen.append(item)
    return seen


def project_usage(sources):
    rows = []
    for run_id, run in sources["runs"].items():
        envelope = latest_envelope(run)
        save_point = latest_save_point(run)
        visited = []
        if save_point and isinstance(save_point.get("visited_skills"), list):
            visited = [item for item in save_point["visited_skills"] if isinstance(item, str)]
        route = (envelope or {}).get("route") if envelope else None
        skill = None
        if isinstance(route, dict):
            skill = route.get("skill")
        elif visited:
            skill = visited[-1]
        rows.append({
            "run_id": (envelope or {}).get("run_id") or run_id,
            "status": (envelope or {}).get("status") or (save_point or {}).get("status"),
            "started_at": (envelope or {}).get("started_at"),
            "ended_at": (envelope or {}).get("ended_at"),
            "skill": skill,
            "visited_skills": visited,
            "evidence_mode": (envelope or {}).get("evidence_mode"),
        })
    rows.sort(key=lambda item: item.get("started_at") or "", reverse=True)
    return {"runs": rows, "empty": not rows}


def project_delta(sources):
    before_refs = []
    after_refs = []
    for run in sources["runs"].values():
        first = earliest_save_point(run)
        last = latest_save_point(run)
        envelope = latest_envelope(run)
        if first:
            before_refs.extend(artifact_refs(first.get("artifacts")))
        if last and last is not first:
            after_refs.extend(artifact_refs(last.get("artifacts")))
        if envelope:
            after_refs.extend(artifact_refs(envelope.get("artifacts")))
    before_refs = unique(before_refs)
    after_refs = unique(after_refs)

    grouped = {}
    for audit in sources["audits"]:
        key = (audit.get("target") or audit.get("_path"), audit.get("framework"))
        grouped.setdefault(key, []).append(audit)
    quality = []
    for (target, framework), records in grouped.items():
        ordered = sorted(records, key=lambda item: (item.get("observed_at") or "", item.get("_path") or ""))
        after = ordered[-1]
        before = ordered[-2] if len(ordered) > 1 else None
        quality.append({
            "target": target,
            "framework": framework,
            "before": quality_state(before),
            "after": quality_state(after),
        })
    empty = not (before_refs or after_refs or quality)
    return {
        "work": {"before": before_refs, "after": after_refs},
        "quality": quality,
        "empty": empty,
    }


def control_kind(item):
    return item.get("kind") if isinstance(item, dict) else None


def resolve_numeric(root, ref):
    path = ref_path(ref)
    if not path:
        return None
    candidate = (root / path) if not Path(path).is_absolute() else Path(path)
    if not candidate.is_file():
        return None
    try:
        value = load_json(candidate)
    except (OSError, ValueError):
        return None
    if not isinstance(value, dict):
        return None
    number = value.get("value")
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        return None
    return {
        "value": number,
        "metric_id": value.get("metric_id"),
        "unit": value.get("unit"),
        "evidence_type": value.get("evidence_type"),
        "source": path,
        "observed_at": value.get("observed_at"),
    }


def observation_time(item):
    payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
    window = payload.get("observation_window") if isinstance(payload.get("observation_window"), dict) else {}
    return (
        window.get("end_at")
        or window.get("start_at")
        or item.get("created_at")
        or ""
    )


def project_outcomes(root, sources):
    contracts = [item for item in sources["controls"] if control_kind(item) == "measurement-contract"]
    evidence = [item for item in sources["controls"] if control_kind(item) == "evidence-observation"]
    receipts = [item for item in sources["controls"] if control_kind(item) == "action-receipt"]
    retros = [item for item in sources["controls"] if control_kind(item) == "cycle-retro"]
    if not contracts:
        return {
            "bound": False,
            "empty_state": UNBOUND_OUTCOMES,
            "contracts": [],
            "readings": [],
        }

    projected = []
    readings = []
    for contract in contracts:
        payload = contract.get("payload") if isinstance(contract.get("payload"), dict) else {}
        primary = payload.get("primary_metric") if isinstance(payload.get("primary_metric"), dict) else {}
        metric_id = primary.get("metric_id")
        contract_id = contract.get("artifact_id")
        supporting = {
            "evidence_observation": any(
                metric_id
                and metric_id in {
                    field.get("field_id")
                    for field in ((item.get("payload") or {}).get("fields") or [])
                    if isinstance(field, dict)
                }
                for item in evidence
            ) or bool(evidence),
            "action_receipt": bool(receipts),
            "cycle_retro": any(
                (item.get("payload") or {}).get("measurement_contract_id") == contract_id
                for item in retros
            ) or bool(retros),
        }
        projected.append({
            "artifact_id": contract_id or "measurement-contract",
            "metric_id": metric_id,
            "unit": primary.get("unit"),
            "direction": primary.get("direction"),
            "exploratory": bool(payload.get("exploratory")),
            "supporting": supporting,
        })
        numbers = []
        sources_used = []
        for item in sorted(evidence, key=observation_time):
            fields = ((item.get("payload") or {}).get("fields") or [])
            for field in fields:
                if not isinstance(field, dict):
                    continue
                if metric_id and field.get("field_id") not in {metric_id, None}:
                    continue
                if metric_id and field.get("field_id") != metric_id:
                    continue
                resolved = resolve_numeric(root, field.get("value_ref"))
                if resolved:
                    numbers.append(resolved)
                    sources_used.append(resolved["source"])
        before = numbers[0]["value"] if numbers else None
        after = numbers[-1]["value"] if len(numbers) > 1 else (numbers[0]["value"] if len(numbers) == 1 else None)
        if len(numbers) == 1:
            before = None
        delta = None
        if before is not None and after is not None:
            delta = after - before
        readings.append({
            "metric_id": metric_id or "unknown",
            "unit": primary.get("unit"),
            "before": before,
            "after": after,
            "delta": delta,
            "numeric_state": "measured" if (before is not None or after is not None) else "referenced-not-inlined",
            "sources": unique(sources_used),
        })
    return {
        "bound": True,
        "empty_state": None,
        "contracts": projected,
        "readings": readings,
    }


def project_decisions(sources):
    propose = []
    accept = []
    decisions_text = sources["warm"].get("decisions.md")
    if decisions_text:
        sections = parse_markdown_sections(decisions_text)
        for key, rows in sections.items():
            if "active" in key or "pending" in key or "propose" in key:
                propose.extend(rows)
            elif "accept" in key or "approved" in key or "superseded" in key:
                accept.extend(rows)
    loops_text = sources["warm"].get("open-loops.md")
    if loops_text:
        for row in parse_markdown_sections(loops_text).get("active", []):
            if "pending-decision" in row.lower() or "pending decision" in row.lower():
                propose.append(row)
    for run in sources["runs"].values():
        save_point = latest_save_point(run)
        pending = (save_point or {}).get("pending_handoff")
        if isinstance(pending, dict) and pending.get("recommended_skill"):
            propose.append(
                "handoff %s (%s)"
                % (pending.get("recommended_skill"), pending.get("status") or "proposed")
            )
    for audit in sources["audits"]:
        if audit.get("verdict") in {"FIX", "BLOCK", "UNDECIDED"}:
            propose.append(
                "audit %s → %s"
                % (audit.get("framework") or "gate", audit.get("recommended_next_skill") or audit.get("verdict"))
            )
        if audit.get("verdict") == "SHIP":
            accept.append(
                "audit %s SHIP %s"
                % (audit.get("framework") or "gate", audit.get("target") or "")
            )
    propose = unique(propose)
    accept = unique(accept)
    return {"propose": propose, "accept": accept, "empty": not (propose or accept)}


def project_trust(sources):
    gaps = []
    conflicts = []
    confidence = []
    for run in sources["runs"].values():
        envelope = latest_envelope(run)
        if envelope and envelope.get("evidence_mode") in {None, "none", "simulated"}:
            confidence.append(
                "run %s evidence_mode=%s"
                % (envelope.get("run_id") or run["run_id"], envelope.get("evidence_mode") or "unknown")
            )
    for item in sources["controls"]:
        if control_kind(item) != "evidence-observation":
            continue
        payload = item.get("payload") if isinstance(item.get("payload"), dict) else {}
        for field in payload.get("fields") or []:
            if not isinstance(field, dict):
                continue
            if field.get("state") in {"unknown", "not-applicable"} or field.get("missing_reason"):
                gaps.append(
                    "%s: %s"
                    % (field.get("field_id") or "field", field.get("missing_reason") or field.get("state"))
                )
            if field.get("state") == "conflict" or field.get("conflict_group"):
                conflicts.append(
                    "%s conflict_group=%s"
                    % (field.get("field_id") or "field", field.get("conflict_group") or "unspecified")
                )
        for group in payload.get("unresolved_conflicts") or []:
            conflicts.append(str(group))
        readiness = payload.get("readiness")
        if readiness and readiness != "ready":
            gaps.append("evidence readiness=%s" % readiness)
    for audit in sources["audits"]:
        conf = audit.get("score_confidence")
        if conf:
            confidence.append(
                "%s confidence=%s"
                % (audit.get("framework") or audit.get("_path"), conf)
            )
        if audit.get("score_state") == "NOT_SCORED":
            gaps.append(
                "%s is NOT_SCORED" % (audit.get("framework") or audit.get("_path"))
            )
    if not any(control_kind(item) == "measurement-contract" for item in sources["controls"]):
        gaps.append("no measurement-contract; business outcomes remain unbound")
    gaps = unique(gaps)
    conflicts = unique(conflicts)
    confidence = unique(confidence)
    return {
        "gaps": gaps,
        "conflicts": conflicts,
        "confidence": confidence,
        "empty": not (gaps or conflicts or confidence),
    }


def project_coverage(sources, catalog):
    visited = []
    for run in sources["runs"].values():
        save_point = latest_save_point(run)
        if save_point and isinstance(save_point.get("visited_skills"), list):
            visited.extend(
                item for item in save_point["visited_skills"] if isinstance(item, str)
            )
        envelope = latest_envelope(run)
        route = (envelope or {}).get("route")
        if isinstance(route, dict) and route.get("skill"):
            visited.append(route["skill"])
    visited = unique(visited)
    mapping = catalog_skills(catalog)
    disciplines = []
    if catalog:
        order = list(catalog.get("logical_order") or [])
        if not order:
            order = sorted(set(mapping.values()))
        for name in order:
            owned = [slug for slug, discipline in mapping.items() if discipline == name]
            seen = [slug for slug in visited if mapping.get(slug) == name]
            disciplines.append({
                "discipline": name,
                "visited": seen,
                "catalog_count": len(owned),
                "visited_count": len(seen),
            })
    return {
        "catalog_available": bool(catalog),
        "visited": visited,
        "disciplines": disciplines,
        "empty": not visited and not disciplines,
    }


def project_staff(sources):
    roster = sources["staff"].get("roster") or {}
    bots = []
    raw_bots = roster.get("bots") if isinstance(roster, dict) else None
    if isinstance(raw_bots, list):
        for item in raw_bots:
            if not isinstance(item, dict):
                continue
            bots.append({
                "bot": item.get("bot") or item.get("name") or "unknown",
                "kind": item.get("kind"),
                "discipline": item.get("discipline"),
            })
    handoffs = []
    for item in sources["staff"].get("handoffs") or []:
        handoffs.append({
            "from_bot": item.get("from_bot"),
            "to_bot": item.get("to_bot"),
            "skill": item.get("skill") or item.get("recommended_skill"),
            "status": item.get("status"),
        })
    present = bool(bots or handoffs)
    return {
        "present": present,
        "empty_state": None if present else EMPTY_STAFF,
        "bots": bots,
        "handoffs": handoffs,
    }


def project_timeline(sources):
    events = []
    for run in sources["runs"].values():
        for event in run.get("events") or []:
            events.append({
                "occurred_at": event.get("occurred_at") or event.get("recorded_at"),
                "event_type": event.get("event_type"),
                "status": event.get("status"),
            })
    events.sort(key=lambda item: item.get("occurred_at") or "")
    return {"present": bool(events), "events": events}


def project(root, catalog=None):
    root = Path(root).resolve()
    sources = discover(root)
    catalog = catalog if catalog is not None else load_catalog(root)
    modules = {
        "next": project_next(sources),
        "usage": project_usage(sources),
        "delta": project_delta(sources),
        "outcomes": project_outcomes(root, sources),
        "decisions": project_decisions(sources),
        "trust": project_trust(sources),
        "coverage": project_coverage(sources, catalog),
        "staff": project_staff(sources),
    }
    timeline = project_timeline(sources)
    if timeline["present"]:
        modules["timeline"] = timeline
    envelopes = sum(len(run["envelopes"]) for run in sources["runs"].values())
    save_points = sum(len(run["save_points"]) for run in sources["runs"].values())
    events = sum(len(run["events"]) for run in sources["runs"].values())
    return {
        "schema_version": SCHEMA_VERSION,
        "product": PRODUCT,
        "generated_at": utc_now(),
        "root": as_posix(root),
        "boundaries": {
            "install_surface": False,
            "hosted_web_product": False,
            "gateway": False,
            "billing": False,
            "social_signal_monitoring": False,
        },
        "source_summary": {
            "runs": len(sources["runs"]),
            "envelopes": envelopes,
            "save_points": save_points,
            "audits": len(sources["audits"]),
            "control_artifacts": len(sources["controls"]),
            "events": events,
            "staff_handoffs": len(sources["staff"]["handoffs"]),
            "notes": list(sources["notes"]),
            "errors": list(sources["errors"]),
        },
        "modules": modules,
    }


def render_md(view):
    modules = view["modules"]
    lines = [
        "# %s" % PRODUCT,
        "",
        "Local optional view. Not an OSS install surface, not a hosted Web product, and not a Gateway.",
        "",
        "Generated: %s" % view["generated_at"],
        "Root: `%s`" % view["root"],
        "",
    ]
    nxt = modules["next"]
    lines += ["## Next", ""]
    if nxt["empty"]:
        lines += [EMPTY_NEXT, ""]
    else:
        lines.append("- Next action: %s" % (nxt["next_action"] or "none"))
        for item in nxt["open_loops"]:
            lines.append("- Open loop: %s" % item)
        for item in nxt["blockers"]:
            lines.append("- Blocker: %s" % item)
        lines.append("")

    usage = modules["usage"]
    lines += ["## Usage", ""]
    if usage["empty"]:
        lines += [EMPTY_USAGE, ""]
    else:
        for run in usage["runs"]:
            chain = " → ".join(run["visited_skills"]) if run["visited_skills"] else "none"
            lines.append(
                "- `%s` status=%s skill=%s visited=%s"
                % (run["run_id"], run["status"], run["skill"] or "unknown", chain)
            )
        lines.append("")

    delta = modules["delta"]
    lines += ["## Delta", ""]
    if delta["empty"]:
        lines += [EMPTY_DELTA, ""]
    else:
        lines.append("Work before: %s" % (", ".join(delta["work"]["before"]) or "none"))
        lines.append("Work after: %s" % (", ".join(delta["work"]["after"]) or "none"))
        for item in delta["quality"]:
            lines.append(
                "- Quality %s/%s: %s → %s"
                % (
                    item["framework"] or "unknown",
                    item["target"] or "unknown",
                    item["before"]["verdict"],
                    item["after"]["verdict"],
                )
            )
        lines.append("")

    outcomes = modules["outcomes"]
    lines += ["## Outcomes", ""]
    if not outcomes["bound"]:
        lines += [outcomes["empty_state"] or UNBOUND_OUTCOMES, ""]
    else:
        for contract in outcomes["contracts"]:
            support = contract["supporting"]
            lines.append(
                "- Contract `%s` metric=%s unit=%s (evidence=%s receipt=%s retro=%s)"
                % (
                    contract["artifact_id"],
                    contract["metric_id"],
                    contract["unit"],
                    support["evidence_observation"],
                    support["action_receipt"],
                    support["cycle_retro"],
                )
            )
        for reading in outcomes["readings"]:
            lines.append(
                "- %s before=%s after=%s delta=%s (%s)"
                % (
                    reading["metric_id"],
                    reading["before"],
                    reading["after"],
                    reading["delta"],
                    reading["numeric_state"],
                )
            )
        lines.append("")

    decisions = modules["decisions"]
    lines += ["## Decisions", ""]
    if decisions["empty"]:
        lines += [EMPTY_DECISIONS, ""]
    else:
        for item in decisions["propose"]:
            lines.append("- Propose: %s" % item)
        for item in decisions["accept"]:
            lines.append("- Accept: %s" % item)
        lines.append("")

    trust = modules["trust"]
    lines += ["## Trust", ""]
    if trust["empty"]:
        lines += [EMPTY_TRUST, ""]
    else:
        for item in trust["gaps"]:
            lines.append("- Gap: %s" % item)
        for item in trust["conflicts"]:
            lines.append("- Conflict: %s" % item)
        for item in trust["confidence"]:
            lines.append("- Confidence: %s" % item)
        lines.append("")

    coverage = modules["coverage"]
    lines += ["## Coverage", ""]
    if coverage["empty"]:
        lines += [EMPTY_COVERAGE, ""]
    else:
        lines.append("Visited: %s" % (", ".join(coverage["visited"]) or "none"))
        for item in coverage["disciplines"]:
            lines.append(
                "- %s: %d/%d"
                % (item["discipline"], item["visited_count"], item["catalog_count"])
            )
        lines.append("")

    staff = modules["staff"]
    lines += ["## Staff", ""]
    if not staff["present"]:
        lines += [staff["empty_state"] or EMPTY_STAFF, ""]
    else:
        for bot in staff["bots"]:
            lines.append("- Bot `%s` (%s / %s)" % (bot["bot"], bot["kind"], bot["discipline"]))
        for item in staff["handoffs"]:
            lines.append(
                "- Handoff %s → %s skill=%s status=%s"
                % (item["from_bot"], item["to_bot"], item["skill"], item["status"])
            )
        lines.append("")

    timeline = modules.get("timeline")
    if timeline and timeline.get("present"):
        lines += ["## Timeline", ""]
        for event in timeline["events"]:
            lines.append(
                "- %s %s (%s)"
                % (event["occurred_at"], event["event_type"], event["status"])
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _esc(value):
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _list_html(items, empty_label):
    if not items:
        return '<p class="empty">%s</p>' % _esc(empty_label)
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % _esc(item) for item in items)


def render_html(view):
    modules = view["modules"]
    sections = []

    nxt = modules["next"]
    if nxt["empty"]:
        next_body = '<p class="empty">%s</p>' % _esc(EMPTY_NEXT)
    else:
        next_body = (
            "<dl><dt>Next action</dt><dd>%s</dd></dl>%s%s"
            % (
                _esc(nxt["next_action"] or "none"),
                _list_html(nxt["open_loops"], "No open loops"),
                _list_html(nxt["blockers"], "No blockers"),
            )
        )
    sections.append(("next", "Next", next_body))

    usage = modules["usage"]
    if usage["empty"]:
        usage_body = '<p class="empty">%s</p>' % _esc(EMPTY_USAGE)
    else:
        rows = []
        for run in usage["runs"]:
            chain = " → ".join(run["visited_skills"]) if run["visited_skills"] else "—"
            rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (
                    _esc(run["run_id"]),
                    _esc(run["status"]),
                    _esc(run["skill"]),
                    _esc(chain),
                    _esc(run["started_at"]),
                    _esc(run["evidence_mode"]),
                )
            )
        usage_body = (
            "<table><thead><tr><th>Run</th><th>Status</th><th>Skill</th>"
            "<th>Visited</th><th>Started</th><th>Evidence</th></tr></thead>"
            "<tbody>%s</tbody></table>" % "".join(rows)
        )
    sections.append(("usage", "Usage", usage_body))

    delta = modules["delta"]
    if delta["empty"]:
        delta_body = '<p class="empty">%s</p>' % _esc(EMPTY_DELTA)
    else:
        quality_rows = []
        for item in delta["quality"]:
            quality_rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (
                    _esc(item["framework"]),
                    _esc(item["target"]),
                    _esc(item["before"]["verdict"]),
                    _esc(item["after"]["verdict"]),
                )
            )
        delta_body = (
            "<h3>Work</h3><p>Before: %s</p><p>After: %s</p>"
            "<h3>Quality</h3>"
            "<table><thead><tr><th>Framework</th><th>Target</th><th>Before</th>"
            "<th>After</th></tr></thead><tbody>%s</tbody></table>"
            % (
                _esc(", ".join(delta["work"]["before"]) or "none"),
                _esc(", ".join(delta["work"]["after"]) or "none"),
                "".join(quality_rows) or '<tr><td colspan="4">No audit pair</td></tr>',
            )
        )
    sections.append(("delta", "Delta", delta_body))

    outcomes = modules["outcomes"]
    if not outcomes["bound"]:
        outcomes_body = '<p class="empty">%s</p>' % _esc(outcomes["empty_state"] or UNBOUND_OUTCOMES)
    else:
        contract_rows = []
        for contract in outcomes["contracts"]:
            support = contract["supporting"]
            contract_rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s / %s / %s</td></tr>"
                % (
                    _esc(contract["artifact_id"]),
                    _esc(contract["metric_id"]),
                    _esc(contract["unit"]),
                    _esc(contract["direction"]),
                    "evidence" if support["evidence_observation"] else "—",
                    "receipt" if support["action_receipt"] else "—",
                    "retro" if support["cycle_retro"] else "—",
                )
            )
        reading_rows = []
        for reading in outcomes["readings"]:
            reading_rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (
                    _esc(reading["metric_id"]),
                    _esc(reading["before"]),
                    _esc(reading["after"]),
                    _esc(reading["delta"]),
                    _esc(reading["numeric_state"]),
                )
            )
        outcomes_body = (
            "<table><thead><tr><th>Contract</th><th>Metric</th><th>Unit</th>"
            "<th>Direction</th><th>Supporting</th></tr></thead>"
            "<tbody>%s</tbody></table>"
            "<table><thead><tr><th>Metric</th><th>Before</th><th>After</th>"
            "<th>Delta</th><th>State</th></tr></thead>"
            "<tbody>%s</tbody></table>"
            % ("".join(contract_rows), "".join(reading_rows))
        )
    sections.append(("outcomes", "Outcomes", outcomes_body))

    decisions = modules["decisions"]
    if decisions["empty"]:
        decisions_body = '<p class="empty">%s</p>' % _esc(EMPTY_DECISIONS)
    else:
        decisions_body = (
            "<h3>Propose</h3>%s<h3>Accept</h3>%s"
            % (
                _list_html(decisions["propose"], "No propose items"),
                _list_html(decisions["accept"], "No Accept items"),
            )
        )
    sections.append(("decisions", "Decisions", decisions_body))

    trust = modules["trust"]
    if trust["empty"]:
        trust_body = '<p class="empty">%s</p>' % _esc(EMPTY_TRUST)
    else:
        trust_body = (
            "<h3>Gaps</h3>%s<h3>Conflicts</h3>%s<h3>Confidence</h3>%s"
            % (
                _list_html(trust["gaps"], "No gaps"),
                _list_html(trust["conflicts"], "No conflicts"),
                _list_html(trust["confidence"], "No confidence notes"),
            )
        )
    sections.append(("trust", "Trust", trust_body))

    coverage = modules["coverage"]
    if coverage["empty"]:
        coverage_body = '<p class="empty">%s</p>' % _esc(EMPTY_COVERAGE)
    else:
        rows = []
        for item in coverage["disciplines"]:
            rows.append(
                "<tr><td>%s</td><td>%s</td><td>%s / %s</td></tr>"
                % (
                    _esc(item["discipline"]),
                    _esc(", ".join(item["visited"]) or "—"),
                    _esc(item["visited_count"]),
                    _esc(item["catalog_count"]),
                )
            )
        coverage_body = (
            "<p>Visited: %s</p>"
            "<table><thead><tr><th>Discipline</th><th>Visited skills</th>"
            "<th>Coverage</th></tr></thead><tbody>%s</tbody></table>"
            % (_esc(", ".join(coverage["visited"]) or "none"), "".join(rows))
        )
    sections.append(("coverage", "Coverage", coverage_body))

    staff = modules["staff"]
    if not staff["present"]:
        staff_body = '<p class="empty">%s</p>' % _esc(staff["empty_state"] or EMPTY_STAFF)
    else:
        bots = "".join(
            "<li>%s (%s / %s)</li>"
            % (_esc(bot["bot"]), _esc(bot["kind"]), _esc(bot["discipline"]))
            for bot in staff["bots"]
        )
        handoffs = "".join(
            "<li>%s → %s · %s · %s</li>"
            % (
                _esc(item["from_bot"]),
                _esc(item["to_bot"]),
                _esc(item["skill"]),
                _esc(item["status"]),
            )
            for item in staff["handoffs"]
        )
        staff_body = "<ul>%s</ul><ul>%s</ul>" % (bots, handoffs)
    sections.append(("staff", "Staff", staff_body))

    timeline = modules.get("timeline")
    if timeline and timeline.get("present"):
        rows = "".join(
            "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (_esc(event["occurred_at"]), _esc(event["event_type"]), _esc(event["status"]))
            for event in timeline["events"]
        )
        sections.append((
            "timeline",
            "Timeline",
            "<table><thead><tr><th>When</th><th>Event</th><th>Status</th></tr></thead>"
            "<tbody>%s</tbody></table>" % rows,
        ))

    nav = "".join('<a href="#%s">%s</a>' % (key, title) for key, title, _ in sections)
    body = "".join(
        '<section id="%s"><h2>%s</h2>%s</section>' % (key, title, content)
        for key, title, content in sections
    )
    notes = view["source_summary"].get("notes") or []
    errors = view["source_summary"].get("errors") or []
    footer_notes = ""
    if notes or errors:
        footer_notes = "<h2>Source notes</h2>%s%s" % (
            _list_html(notes, ""),
            _list_html(errors, ""),
        )
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<style>
:root { color-scheme: light dark; --bg:#f6f4ef; --ink:#1c1916; --muted:#5c564e; --card:#fff; --line:#d9d2c6; --accent:#8a4b2f; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#161412; --ink:#f3ece4; --muted:#b3a89c; --card:#221f1b; --line:#3b352e; --accent:#e0a07a; }
}
body { margin:0 auto; max-width:960px; padding:24px; font:16px/1.5 ui-sans-serif,system-ui,sans-serif; background:var(--bg); color:var(--ink); }
header p, .empty, nav a { color:var(--muted); }
header { margin-bottom:16px; }
h1,h2,h3 { font-weight:650; }
h1 { font-size:1.8rem; margin:0 0 8px; }
nav { display:flex; flex-wrap:wrap; gap:10px 16px; margin:16px 0 24px; }
nav a { text-decoration:none; }
section { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:16px 20px; margin:0 0 16px; }
table { width:100%%; border-collapse:collapse; }
th,td { text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
.empty { font-style:italic; }
code { font-family:ui-monospace,monospace; }
</style>
</head>
<body>
<header>
<h1>%(title)s</h1>
<p>Local optional view of your own skill runs. Not an OSS install surface, not a hosted Web product, and not a Gateway.</p>
<p>Generated %(generated)s · root <code>%(root)s</code></p>
</header>
<nav>%(nav)s</nav>
%(body)s
%(notes)s
</body>
</html>
""" % {
        "title": _esc(PRODUCT),
        "generated": _esc(view["generated_at"]),
        "root": _esc(view["root"]),
        "nav": nav,
        "body": body,
        "notes": footer_notes,
    }


def resolve_out(path):
    out = Path(path)
    if out.exists() and out.is_dir():
        return out / DEFAULT_OUT
    if str(path).endswith(("/", "\\")):
        return Path(path) / DEFAULT_OUT
    return out


def write_outputs(view, out_path, write_json=False, write_md=False):
    html_path = resolve_out(out_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(view), encoding="utf-8")
    written = [html_path]
    stem = html_path.with_suffix("")
    if write_json:
        json_path = stem.with_suffix(".json")
        json_path.write_text(
            json.dumps(view, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(json_path)
    if write_md:
        md_path = stem.with_suffix(".md")
        md_path.write_text(render_md(view), encoding="utf-8")
        written.append(md_path)
    return written


def build_parser():
    parser = argparse.ArgumentParser(description="Generate a local Skill Dashboard view.")
    parser.add_argument("--root", default=".", help="Project root that contains memory/ artifacts")
    parser.add_argument("--out", default=DEFAULT_OUT, help="HTML output path (default skill-dashboard.html)")
    parser.add_argument("--json", action="store_true", help="Also write skill-dashboard.json")
    parser.add_argument("--md", action="store_true", help="Also write skill-dashboard.md")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if not root.exists():
        raise DashboardError("root does not exist: %s" % root)
    view = project(root)
    written = write_outputs(view, args.out, write_json=args.json, write_md=args.md)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except DashboardError as exc:
        print("skill-dashboard: %s" % exc, file=sys.stderr)
        sys.exit(2)
