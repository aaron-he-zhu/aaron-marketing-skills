#!/usr/bin/env python3
"""Render evidence-bound convergence telemetry from v3 audit artifacts.

The tool is read-only.  Audit files are accepted only after a bounded,
single-link, no-follow read of the exact bytes followed by the repository's v3
validator.  Intervention evidence is associated with an audit transition only
when a fully validated immutable audit-loop stream names the exact before and
after audit hashes.  Filenames and dates are never used to infer an
intervention.

  python3 scripts/audit-trends.py [--root DIR] [--framework CORE-EEAT] [--json]
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
FRAMEWORKS = {
    "CORE-EEAT", "CITE", "STAR", "ROAS", "SEND", "RAMP", "ECHO", "TALE", "MULTI",
}
CONFIDENCE_RANK = {"not_scored": 0, "low": 1, "medium": 2, "high": 3}

MAX_AUDIT_FILES = 256
MAX_AUDIT_ENTRIES = 1024
MAX_AUDIT_TOTAL_BYTES = 16_000_000
MAX_LOOP_DIRECTORIES = 256
MAX_LOOP_ENTRIES = 4096
MAX_LOOP_STEPS_TOTAL = 4096
MAX_LOOP_STEP_TOTAL_BYTES = 16_000_000
MAX_LOOP_EVIDENCE_TOTAL_BYTES = 32_000_000
MAX_SCAN_SECONDS = 20

AUDIT_IDENTITY_FIELDS = (
    "schema_version", "runbook_version", "catalog_version", "framework", "profile",
    "target", "target_identity_sha256", "context_sha256", "observed_at",
    "status", "verdict",
    "score_state", "evidence_coverage", "score_confidence",
    "raw_overall_score", "final_overall_score",
)


class AuditTrendError(ValueError):
    """Raised when a bounded scan cannot safely produce complete telemetry."""


def _load_module(name, path):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError("cannot load runtime module: %s" % path)
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


audit_validator = _load_module(
    "audit_trends_artifact_validator", ROOT / "scripts" / "validate-audit-artifact.py",
)
audit_loop = _load_module(
    "audit_trends_loop_runtime", ROOT / "scripts" / "audit-loop.py",
)


def canonical_json(value):
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    )


def sha256_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _path_reference(root, path):
    try:
        return path.relative_to(root).as_posix()
    except ValueError as exc:
        raise AuditTrendError("artifact path escapes the project root") from exc


def _real_directory_chain(root, parts):
    """Return ``(directory, invalid_count)`` without following ancestors."""
    current = root
    for part in parts:
        current = current / part
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            return None, 0
        except OSError as exc:
            raise AuditTrendError("cannot inspect directory %s: %s" % (current, exc)) from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            return None, 1
    return current, 0


def _directory_snapshot(path, deadline, entry_limit):
    if time.monotonic() >= deadline:
        raise AuditTrendError("convergence scan exceeded its internal deadline")
    try:
        before = os.lstat(path)
        if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
            raise AuditTrendError("scan directory must remain a real directory: %s" % path)
        entries = []
        with os.scandir(path) as iterator:
            for entry in iterator:
                if time.monotonic() >= deadline:
                    raise AuditTrendError(
                        "convergence scan exceeded its internal deadline"
                    )
                entries.append(entry)
                if len(entries) > entry_limit:
                    raise AuditTrendError(
                        "directory scan exceeds its bounded entry allowance: %s" % path
                    )
        entries.sort(key=lambda item: item.name)
        after = os.lstat(path)
    except OSError as exc:
        raise AuditTrendError("cannot scan directory %s: %s" % (path, exc)) from exc
    stable = ("st_dev", "st_ino", "st_mtime_ns", "st_ctime_ns")
    if any(getattr(before, field) != getattr(after, field) for field in stable):
        raise AuditTrendError("scan directory changed during inspection: %s" % path)
    return entries


def _audit_candidates(root, deadline):
    audits_dir, unsafe = _real_directory_chain(root, ("memory", "audits"))
    if audits_dir is None:
        return [], unsafe
    stack = [audits_dir]
    candidates = []
    skipped = 0
    entries_seen = 0
    while stack:
        directory = stack.pop()
        allowance = MAX_AUDIT_ENTRIES - entries_seen
        for entry in _directory_snapshot(directory, deadline, allowance):
            entries_seen += 1
            if entries_seen > MAX_AUDIT_ENTRIES:
                raise AuditTrendError(
                    "audit scan exceeds %d-entry limit" % MAX_AUDIT_ENTRIES
                )
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError:
                skipped += 1
                continue
            path = Path(entry.path)
            if stat.S_ISLNK(metadata.st_mode):
                skipped += 1
            elif stat.S_ISDIR(metadata.st_mode):
                stack.append(path)
            elif stat.S_ISREG(metadata.st_mode) and path.suffix == ".md":
                candidates.append(path)
                if len(candidates) > MAX_AUDIT_FILES:
                    raise AuditTrendError(
                        "audit scan exceeds %d-file limit" % MAX_AUDIT_FILES
                    )
            else:
                skipped += 1
    return sorted(candidates), skipped


def _validate_exact_artifact(root, path):
    """Validate a private copy of the exact no-follow bytes read from ``path``."""
    reference = _path_reference(root, path)
    try:
        candidate_size = os.lstat(path).st_size
    except OSError:
        candidate_size = 0
    inspected_bytes = min(candidate_size, audit_validator.MAX_ARTIFACT_BYTES + 1)
    try:
        _resolved, raw, _metadata, digest = audit_loop._stable_bytes(
            root, reference, audit_validator.MAX_ARTIFACT_BYTES, "audit artifact",
        )
    except Exception:
        return None, inspected_bytes

    descriptor = None
    temporary = None
    try:
        descriptor, temporary = tempfile.mkstemp(
            prefix="aaron-audit-trends-", suffix=".md",
        )
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        record, errors = audit_validator.validate(Path(temporary), reference)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary is not None:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
    if errors or not isinstance(record, dict):
        return None, len(raw)
    context = record.get("context")
    if not isinstance(context, dict) or not context:
        return None, len(raw)
    record = dict(record)
    record.update({
        "artifact_ref": reference,
        "artifact_sha256": digest,
        "target_identity_sha256": sha256_json({
            "framework": record["framework"],
            "profile": record["profile"],
            "target": record["target"],
        }),
        "context_sha256": sha256_json(context),
        "path": str(path),
    })
    return record, len(raw)


def collect_with_counts(root):
    """Collect unique validator-clean audits plus invalid and duplicate counts."""
    root = Path(root).resolve()
    deadline = time.monotonic() + MAX_SCAN_SECONDS
    candidates, skipped = _audit_candidates(root, deadline)
    artifacts = []
    seen_hashes = set()
    duplicates = 0
    total_bytes = 0
    for path in candidates:
        if time.monotonic() >= deadline:
            raise AuditTrendError("audit scan exceeded its internal deadline")
        artifact, byte_count = _validate_exact_artifact(root, path)
        total_bytes += byte_count
        if total_bytes > MAX_AUDIT_TOTAL_BYTES:
            raise AuditTrendError(
                "audit scan exceeds %d-byte aggregate limit" % MAX_AUDIT_TOTAL_BYTES
            )
        if artifact is None:
            skipped += 1
        elif artifact["artifact_sha256"] in seen_hashes:
            duplicates += 1
        else:
            seen_hashes.add(artifact["artifact_sha256"])
            artifacts.append(artifact)
    return artifacts, skipped, duplicates


def collect(root):
    """Collect unique validator-clean v3 audits and a separate invalid count."""
    artifacts, skipped, _duplicates = collect_with_counts(root)
    return artifacts, skipped


def _audit_identity_matches(identity, artifact):
    if not isinstance(identity, dict):
        return False
    if identity.get("sha256") != artifact.get("artifact_sha256"):
        return False
    return all(identity.get(field) == artifact.get(field) for field in AUDIT_IDENTITY_FIELDS)


def _loop_directories(root, deadline):
    runs_dir, unsafe = _real_directory_chain(root, ("memory", "runs"))
    if runs_dir is None:
        return [], unsafe
    result = []
    skipped = unsafe
    entries_seen = 0
    for run_entry in _directory_snapshot(
            runs_dir, deadline, MAX_LOOP_ENTRIES - entries_seen):
        entries_seen += 1
        if entries_seen > MAX_LOOP_ENTRIES:
            raise AuditTrendError("loop scan exceeds %d-entry limit" % MAX_LOOP_ENTRIES)
        try:
            run_meta = run_entry.stat(follow_symlinks=False)
        except OSError:
            skipped += 1
            continue
        if stat.S_ISLNK(run_meta.st_mode):
            skipped += 1
            continue
        if not stat.S_ISDIR(run_meta.st_mode):
            continue
        loops_dir = Path(run_entry.path) / "loops"
        try:
            loops_meta = os.lstat(loops_dir)
        except FileNotFoundError:
            continue
        except OSError:
            skipped += 1
            continue
        if stat.S_ISLNK(loops_meta.st_mode) or not stat.S_ISDIR(loops_meta.st_mode):
            skipped += 1
            continue
        for loop_entry in _directory_snapshot(
                loops_dir, deadline, MAX_LOOP_ENTRIES - entries_seen):
            entries_seen += 1
            if entries_seen > MAX_LOOP_ENTRIES:
                raise AuditTrendError("loop scan exceeds %d-entry limit" % MAX_LOOP_ENTRIES)
            try:
                loop_meta = loop_entry.stat(follow_symlinks=False)
            except OSError:
                skipped += 1
                continue
            if stat.S_ISLNK(loop_meta.st_mode) or not stat.S_ISDIR(loop_meta.st_mode):
                skipped += 1
                continue
            result.append((run_entry.name, loop_entry.name, Path(loop_entry.path)))
            if len(result) > MAX_LOOP_DIRECTORIES:
                raise AuditTrendError(
                    "loop scan exceeds %d-loop limit" % MAX_LOOP_DIRECTORIES
                )
    return sorted(result), skipped


def _candidate_step_inventory(loop_dir, deadline):
    count = 0
    total_bytes = 0
    for entry in _directory_snapshot(loop_dir, deadline, audit_loop.MAX_STEPS + 2):
        if entry.name.endswith(".json"):
            count += 1
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError:
                continue
            if stat.S_ISREG(metadata.st_mode):
                total_bytes += metadata.st_size
    return max(1, count), total_bytes


def _verified_intervention(root, evidence, remaining_bytes, deadline):
    if time.monotonic() >= deadline:
        raise AuditTrendError("loop scan exceeded its internal deadline")
    if not isinstance(evidence, dict) or set(evidence) != {"ref", "sha256", "bytes"}:
        return None, 0
    if evidence["bytes"] > remaining_bytes:
        raise AuditTrendError(
            "loop evidence scan exceeds %d-byte aggregate limit"
            % MAX_LOOP_EVIDENCE_TOTAL_BYTES
        )
    try:
        with audit_loop.runtime.anchored_project_file(
                root, evidence["ref"]) as (_path, handle):
            before = os.fstat(handle.fileno())
            if before.st_size > audit_loop.MAX_EVIDENCE_BYTES:
                return None, 0
            if before.st_size > remaining_bytes:
                raise AuditTrendError(
                    "loop evidence scan exceeds %d-byte aggregate limit"
                    % MAX_LOOP_EVIDENCE_TOTAL_BYTES
                )
            raw = handle.read(before.st_size + 1)
            after = os.fstat(handle.fileno())
            if time.monotonic() >= deadline:
                raise AuditTrendError("loop scan exceeded its internal deadline")
            stable = (
                "st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns",
            )
            if len(raw) != before.st_size or any(
                    getattr(before, field) != getattr(after, field) for field in stable):
                return None, len(raw)
    except AuditTrendError:
        raise
    except Exception:
        return None, 0
    digest = hashlib.sha256(raw).hexdigest()
    if after.st_size != evidence["bytes"] or digest != evidence["sha256"]:
        return None, len(raw)
    return {
        "intervention_ref": evidence["ref"],
        "intervention_sha256": evidence["sha256"],
        "intervention_bytes": evidence["bytes"],
    }, len(raw)


def collect_loop_links(root, artifacts):
    """Return exact audit-hash transition links from fully validated loops."""
    root = Path(root).resolve()
    deadline = time.monotonic() + MAX_SCAN_SECONDS
    directories, skipped = _loop_directories(root, deadline)
    by_hash = {}
    for artifact in artifacts:
        by_hash.setdefault(artifact["artifact_sha256"], []).append(artifact)
    links = {}
    valid_steps = 0
    step_bytes = 0
    evidence_bytes = 0
    for run_id, loop_id, loop_dir in directories:
        if time.monotonic() >= deadline:
            raise AuditTrendError("loop scan exceeded its internal deadline")
        candidate_steps, candidate_bytes = _candidate_step_inventory(loop_dir, deadline)
        remaining_step_bytes = MAX_LOOP_STEP_TOTAL_BYTES - step_bytes
        if candidate_bytes > remaining_step_bytes:
            raise AuditTrendError(
                "loop step scan exceeds %d-byte aggregate limit"
                % MAX_LOOP_STEP_TOTAL_BYTES
            )
        try:
            steps, consumed_step_bytes = audit_loop.read_loop_with_event_coverage(
                root, run_id, loop_id,
                max_total_bytes=remaining_step_bytes,
                deadline_monotonic=deadline,
                return_total_bytes=True,
            )
        except Exception:
            if time.monotonic() >= deadline:
                raise AuditTrendError("loop scan exceeded its internal deadline")
            step_bytes += candidate_bytes
            skipped += candidate_steps
            continue
        if (
                not isinstance(consumed_step_bytes, int)
                or isinstance(consumed_step_bytes, bool)
                or consumed_step_bytes < 0):
            raise AuditTrendError("loop reader returned an invalid byte count")
        charged_step_bytes = max(candidate_bytes, consumed_step_bytes)
        if charged_step_bytes > remaining_step_bytes:
            raise AuditTrendError(
                "loop step scan exceeds %d-byte aggregate limit"
                % MAX_LOOP_STEP_TOTAL_BYTES
            )
        step_bytes += charged_step_bytes
        if time.monotonic() >= deadline:
            raise AuditTrendError("loop scan exceeded its internal deadline")
        valid_steps += len(steps)
        if valid_steps > MAX_LOOP_STEPS_TOTAL:
            raise AuditTrendError(
                "loop scan exceeds %d-step aggregate limit" % MAX_LOOP_STEPS_TOTAL
            )
        for position, item in enumerate(steps):
            document = item["document"]
            if document.get("transition") != "reaudit-recorded" or position == 0:
                continue
            previous = steps[position - 1]["document"]
            before_identity = previous.get("latest_audit")
            after_identity = document.get("latest_audit")
            before_matches = by_hash.get(
                before_identity.get("sha256") if isinstance(before_identity, dict) else None, []
            )
            after_matches = by_hash.get(
                after_identity.get("sha256") if isinstance(after_identity, dict) else None, []
            )
            if not any(_audit_identity_matches(before_identity, audit) for audit in before_matches):
                skipped += 1
                continue
            if not any(_audit_identity_matches(after_identity, audit) for audit in after_matches):
                skipped += 1
                continue
            intervention, consumed = _verified_intervention(
                root, document.get("intervention"),
                MAX_LOOP_EVIDENCE_TOTAL_BYTES - evidence_bytes,
                deadline,
            )
            evidence_bytes += consumed
            if intervention is None:
                skipped += 1
                continue
            link = {
                "run_id": run_id,
                "loop_id": loop_id,
                "loop_step_ref": item["ref"],
                "loop_step_sha256": item["sha256"],
                "transition_id": document["transition_id"],
                "cycle": document["cycle"],
                "from_artifact_sha256": before_identity["sha256"],
                "to_artifact_sha256": after_identity["sha256"],
            }
            link.update(intervention)
            key = (before_identity["sha256"], after_identity["sha256"])
            links.setdefault(key, []).append(link)
    for values in links.values():
        values.sort(key=lambda value: (
            value["run_id"], value["loop_id"], value["loop_step_ref"],
        ))
    return links, skipped, valid_steps


def _comparable(left, right):
    return (
        left.get("catalog_version") == right.get("catalog_version")
        and left.get("context_sha256") == right.get("context_sha256")
    )


def _score(item):
    value = item.get("final_overall_score")
    if item.get("score_state") == "SCORED" and isinstance(value, int):
        return value
    return None


def _oscillation_counts(items):
    compressed = []
    for item in items:
        if not compressed or compressed[-1] != item["verdict"]:
            compressed.append(item["verdict"])
    verdict_oscillations = sum(
        1 for index in range(2, len(compressed))
        if compressed[index] == compressed[index - 2]
        and compressed[index] != compressed[index - 1]
    )

    score_oscillations = 0
    start = 0
    while start < len(items):
        catalog = items[start]["catalog_version"]
        end = start + 1
        while end < len(items) and items[end]["catalog_version"] == catalog:
            end += 1
        scores = [_score(item) for item in items[start:end] if _score(item) is not None]
        signs = []
        for left, right in zip(scores, scores[1:]):
            delta = right - left
            if delta:
                signs.append(1 if delta > 0 else -1)
        score_oscillations += sum(
            left != right for left, right in zip(signs, signs[1:])
        )
        start = end
    return verdict_oscillations, score_oscillations


def series_report(artifacts, loop_links=None):
    loop_links = loop_links or {}
    series = {}
    for item in artifacts:
        key = (item["framework"], item.get("profile", "?"), item["target"])
        series.setdefault(key, []).append(item)
    rows = []
    for (framework, profile, target), items in sorted(series.items()):
        items.sort(key=lambda item: (item["observed_at"], item["path"]))
        scored = [item for item in items if _score(item) is not None]
        score_comparable = len(scored) >= 2 and _comparable(scored[0], scored[-1])
        delta = _score(scored[-1]) - _score(scored[0]) if score_comparable else None
        latest = items[-1]
        latest_score = _score(latest)
        transitions = []
        series_hashes = {item["artifact_sha256"] for item in items}
        linked = []
        for edge in sorted(loop_links):
            if edge[0] in series_hashes and edge[1] in series_hashes:
                linked.extend(dict(value) for value in loop_links[edge])
        unlinked = 0
        relapse_count = 0
        for left, right in zip(items, items[1:]):
            key = (left["artifact_sha256"], right["artifact_sha256"])
            associations = [dict(value) for value in loop_links.get(key, [])]
            if not associations:
                unlinked += 1
            comparable = _comparable(left, right)
            if comparable and left["verdict"] == "SHIP" and right["verdict"] != "SHIP":
                relapse_count += 1
            transitions.append({
                "from_artifact_sha256": left["artifact_sha256"],
                "to_artifact_sha256": right["artifact_sha256"],
                "from_observed_at": left["observed_at"],
                "to_observed_at": right["observed_at"],
                "from_catalog_version": left["catalog_version"],
                "to_catalog_version": right["catalog_version"],
                "from_context_sha256": left["context_sha256"],
                "to_context_sha256": right["context_sha256"],
                "from_evidence_coverage": left["evidence_coverage"],
                "to_evidence_coverage": right["evidence_coverage"],
                "from_score_confidence": left["score_confidence"],
                "to_score_confidence": right["score_confidence"],
                "comparable": comparable,
                "order_basis": "date-path",
                "linked_interventions": associations,
            })
        verdict_oscillations, score_oscillations = _oscillation_counts(items)
        catalog_versions = list(dict.fromkeys(item["catalog_version"] for item in items))
        schema_versions = list(dict.fromkeys(item["schema_version"] for item in items))
        runbook_versions = list(dict.fromkeys(item["runbook_version"] for item in items))
        context_changes = sum(
            left["context_sha256"] != right["context_sha256"]
            for left, right in zip(items, items[1:])
        )
        first = items[0]
        rows.append({
            "framework": framework,
            "profile": profile,
            "target": target,
            "audits": len(items),
            "first": first["observed_at"],
            "latest": latest["observed_at"],
            "latest_verdict": latest["verdict"],
            "latest_score_state": latest["score_state"],
            "latest_score": latest_score,
            "latest_scored_at": scored[-1]["observed_at"] if scored else None,
            "latest_scored_score": _score(scored[-1]) if scored else None,
            "score_delta": delta,
            "score_comparable": score_comparable,
            "stalled": len(items) >= 3 and not any(
                item.get("verdict") == "SHIP" for item in items
            ),
            "first_artifact_sha256": first["artifact_sha256"],
            "latest_artifact_sha256": latest["artifact_sha256"],
            "artifact_sha256": latest["artifact_sha256"],
            "schema_version": latest["schema_version"],
            "runbook_version": latest["runbook_version"],
            "catalog_version": latest["catalog_version"],
            "schema_versions": schema_versions,
            "runbook_versions": runbook_versions,
            "catalog_versions": catalog_versions,
            "catalog_drift": len(set(catalog_versions)) > 1,
            "first_context_sha256": first["context_sha256"],
            "latest_context_sha256": latest["context_sha256"],
            "context_sha256": latest["context_sha256"],
            "context_changes": context_changes,
            "first_evidence_coverage": first["evidence_coverage"],
            "latest_evidence_coverage": latest["evidence_coverage"],
            "evidence_coverage": latest["evidence_coverage"],
            "evidence_coverage_delta": (
                latest["evidence_coverage"] - first["evidence_coverage"]
            ),
            "first_score_confidence": first["score_confidence"],
            "latest_score_confidence": latest["score_confidence"],
            "score_confidence": latest["score_confidence"],
            "confidence_delta": (
                CONFIDENCE_RANK[latest["score_confidence"]]
                - CONFIDENCE_RANK[first["score_confidence"]]
            ),
            "linked_interventions": linked,
            "unlinked_audit_transitions": unlinked,
            "relapse_count": relapse_count,
            "verdict_oscillation_count": verdict_oscillations,
            "score_oscillation_count": score_oscillations,
            "order_basis": "date-path",
            "audit_transitions": transitions,
        })
    return rows


def _human_cell(value, max_chars):
    """Escape terminal controls before bounding a human-readable table cell."""
    tokens = []
    for character in str(value):
        codepoint = ord(character)
        if character == "\\":
            token = "\\\\"
        elif codepoint <= 0x1F or 0x7F <= codepoint <= 0x9F:
            token = "\\x%02x" % codepoint
        elif (
                unicodedata.category(character).startswith("C")
                or codepoint in {0x2028, 0x2029}):
            token = (
                "\\u%04x" % codepoint if codepoint <= 0xFFFF
                else "\\U%08x" % codepoint
            )
        else:
            token = character
        tokens.append(token)
    rendered = "".join(tokens)
    if len(rendered) <= max_chars:
        return rendered
    if max_chars <= 3:
        return "." * max_chars
    allowance = max_chars - 3
    bounded = []
    used = 0
    for token in tokens:
        if used + len(token) > allowance:
            break
        bounded.append(token)
        used += len(token)
    return "".join(bounded) + "..."


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root containing memory/.")
    parser.add_argument("--framework", choices=sorted(FRAMEWORKS))
    parser.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    try:
        artifacts, skipped_audits, duplicate_artifacts = collect_with_counts(root)
        loop_links, skipped_loop_steps, valid_loop_steps = collect_loop_links(root, artifacts)
    except AuditTrendError as exc:
        parser.exit(1, "audit-trends: %s\n" % exc)
    if args.framework:
        artifacts = [item for item in artifacts if item["framework"] == args.framework]
    rows = series_report(artifacts, loop_links)
    linked_count = sum(len(row["linked_interventions"]) for row in rows)
    unlinked_count = sum(row["unlinked_audit_transitions"] for row in rows)

    if args.json:
        print(json.dumps({
            "root": str(root),
            "artifacts": len(artifacts),
            "duplicate_artifacts": duplicate_artifacts,
            "skipped_unparseable": skipped_audits,
            "skipped_invalid_audits": skipped_audits,
            "valid_loop_steps": valid_loop_steps,
            "skipped_invalid_loop_steps": skipped_loop_steps,
            "linked_interventions": linked_count,
            "unlinked_audit_transitions": unlinked_count,
            "series": rows,
        }, indent=2, ensure_ascii=False))
        return 0

    if not artifacts:
        audits_location = _human_cell(root / "memory" / "audits", 160)
        print(
            "No parseable v3 audit artifacts under %s "
            "(skipped %d invalid audit file(s); %d invalid loop step(s)). "
            "Gates have not produced a time series yet."
            % (
                audits_location, skipped_audits, skipped_loop_steps,
            )
        )
        return 0

    print("%-10s %-28s %-22s %-6s %-10s %-6s %-6s %s" % (
        "FRAMEWORK", "TARGET", "PROFILE", "#", "LATEST", "VERDICT", "SCORE", "DELTA",
    ))
    for row in rows:
        framework = _human_cell(row["framework"], 10)
        target = _human_cell(row["target"], 28)
        profile = _human_cell(row["profile"], 22)
        latest = _human_cell(row["latest"], 10)
        verdict = _human_cell(row["latest_verdict"], 6)
        delta = "%+d" % row["score_delta"] if row["score_delta"] is not None else "-"
        score = _human_cell(
            row["latest_score"] if row["latest_score"] is not None else "-", 6,
        )
        flag = "  STALLED" if row["stalled"] else ""
        print("%-10s %-28s %-22s %-6d %-10s %-6s %-6s %s%s" % (
            framework, target, profile, row["audits"], latest, verdict, score,
            delta, flag,
        ))
    stalled = [row for row in rows if row["stalled"]]
    print(
        "\n%d series across %d artifact(s); %d stalled; %d exact intervention "
        "link(s), %d unlinked transition(s); %d invalid audit file(s) and %d "
        "invalid loop step(s) skipped; %d exact duplicate artifact(s) ignored."
        % (
            len(rows), len(artifacts), len(stalled), linked_count, unlinked_count,
            skipped_audits, skipped_loop_steps, duplicate_artifacts,
        )
    )
    if stalled:
        print(
            "Stalled series are loops that are NOT converging — escalate the "
            "underlying veto/finding instead of re-auditing the same state."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
