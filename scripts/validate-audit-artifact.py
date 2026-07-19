#!/usr/bin/env python3
"""Normalize and validate a Markdown auditor artifact against the v3 contract.

No PyYAML/jsonschema dependency is required: auditor artifacts intentionally use a
small, deterministic YAML subset. The companion JSON Schema documents the
normalized object for other hosts and future tooling.
"""
from __future__ import annotations

import argparse
import datetime as dt
from functools import lru_cache
import json
import math
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import time

SCHEMA_VERSION = "3.0"
RUNBOOK_VERSION = "3.0.0"
MIN_SCORE_COVERAGE = 100
VETO_CEILING = 59
MAX_ARTIFACT_BYTES = 1_000_000
MAX_SINK_FILES = 256
MAX_SINK_ENTRIES = 1024
MAX_SINK_TOTAL_BYTES = 16_000_000
MAX_SINK_SECONDS = 20
MAX_HOOK_INPUT_BYTES = 4_000_000
MAX_HOOK_JSON_DEPTH = 64
MAX_HOOK_JSON_NODES = 10_000
MAX_CONTEXT_JSON_DEPTH = 64
MAX_CONTEXT_JSON_NODES = 10_000
MAX_JSON_NUMBER_DIGITS = 1000
FRAMEWORKS = {"CORE-EEAT", "CITE", "STAR", "ROAS", "SEND", "RAMP", "ECHO", "TALE", "MULTI"}
STATUSES = {"DONE", "DONE_WITH_CONCERNS", "BLOCKED", "NEEDS_INPUT"}
VERDICTS = {"SHIP", "FIX", "BLOCK", "UNDECIDED"}
SCORE_STATES = {"SCORED", "NOT_SCORED"}
CONFIDENCE = {"high", "medium", "low", "not_scored"}
SEVERITIES = {"veto", "high", "medium", "low"}
PATH_FRAMEWORK = {
    "content": "CORE-EEAT",
    "domain": "CITE",
    "influencer": "STAR",
    "ad": "ROAS",
    "email": "SEND",
    "launch": "RAMP",
    "social": "ECHO",
    "narrative": "TALE",
}
TOP_KEY = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")
PROFILE_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
ROOT = Path(__file__).resolve().parents[1]
FRAMEWORK_CATALOG = ROOT / "references" / "framework-catalog.json"
FRONTMATTER_FIELDS = {
    "class", "schema_version", "runbook_version", "catalog_version", "framework", "profile",
}
BODY_FIELDS = {
    "status", "verdict", "score_state", "objective", "target", "observed_at",
    "context", "key_findings", "evidence_summary", "evidence_coverage", "score_confidence",
    "open_loops", "recommended_next_skill", "veto_count", "cap_applied",
    "raw_overall_score", "final_overall_score",
}
MULTI_PROFILE = "cross-framework-summary"


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except ValueError:
            return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def split_document(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, lines, ["missing YAML frontmatter"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return {}, [], ["unterminated YAML frontmatter"]
    frontmatter = {}
    errors = []
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = TOP_KEY.match(line)
        if not match:
            errors.append("frontmatter line %d is not a scalar key/value" % number)
            continue
        key, value = match.groups()
        if key in frontmatter:
            errors.append("duplicate frontmatter field: %s" % key)
        frontmatter[key] = scalar(value)
    return frontmatter, lines[end + 1:], errors


def parse_findings(lines, start, inline):
    if inline.strip() == "[]":
        return [], start + 1, []
    if inline.strip():
        return [], start + 1, ["key_findings must be [] or a multiline list"]
    findings = []
    current = None
    errors = []
    index = start + 1
    while index < len(lines):
        line = lines[index]
        if TOP_KEY.match(line):
            break
        item = re.match(r"^\s*-\s+title:\s*(.+)$", line)
        field = re.match(r"^\s+(severity|evidence):\s*(.+)$", line)
        if item:
            if current:
                findings.append(current)
            current = {"title": scalar(item.group(1))}
        elif field and current is not None:
            name = field.group(1)
            if name in current:
                errors.append("key_findings item has duplicate %s at line %d" % (name, index + 1))
            current[name] = scalar(field.group(2))
        elif line.strip() and not line.lstrip().startswith("#"):
            errors.append("unrecognized key_findings line %d" % (index + 1))
        index += 1
    if current:
        findings.append(current)
    if not findings:
        errors.append("key_findings is empty but not written as []")
    for pos, finding in enumerate(findings, 1):
        for field_name in ("title", "severity", "evidence"):
            if not str(finding.get(field_name, "")).strip():
                errors.append("key_findings item %d missing %s" % (pos, field_name))
        if finding.get("severity") not in SEVERITIES:
            errors.append("key_findings item %d has invalid severity" % pos)
    return findings, index, errors


def parse_body(lines):
    values = {}
    errors = []
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        match = TOP_KEY.match(line)
        if not match:
            errors.append("body line %d is not a scalar key/value" % (index + 1))
            index += 1
            continue
        key, inline = match.groups()
        if key in values:
            errors.append("duplicate body field: %s" % key)
        if key == "key_findings":
            findings, index, finding_errors = parse_findings(lines, index, inline)
            values[key] = findings
            errors.extend(finding_errors)
            continue
        values[key] = scalar(inline)
        index += 1
    return values, errors


def as_int(name, value, errors, minimum=0, maximum=None):
    text = str(value) if value is not None else ""
    if not re.fullmatch(r"-?\d+", text):
        errors.append("%s must be an integer" % name)
        return None
    if len(text.lstrip("-")) > 20:
        errors.append("%s integer is too large" % name)
        return None
    try:
        number = int(text)
    except (ValueError, OverflowError):
        errors.append("%s must be a bounded integer" % name)
        return None
    if number < minimum or (maximum is not None and number > maximum):
        errors.append("%s must be between %d and %d" % (name, minimum, maximum))
    return number


def as_bool(name, value, errors):
    if value not in ("true", "false"):
        errors.append("%s must be true or false" % name)
        return None
    return value == "true"


def as_json_object(name, value, errors):
    if not isinstance(value, str) or not value.strip():
        errors.append("%s must be a non-empty strict JSON object" % name)
        return None

    def unique_object(pairs):
        result = {}
        for key, item in pairs:
            if key in result:
                raise ValueError("duplicate JSON key: %s" % key)
            result[key] = item
        return result

    def bounded_int(lexeme):
        if len(lexeme.lstrip("-")) > MAX_JSON_NUMBER_DIGITS:
            raise ValueError("JSON integer exceeds the digit limit")
        return int(lexeme)

    def bounded_float(lexeme):
        digits = sum(character.isdigit() for character in lexeme)
        if digits > MAX_JSON_NUMBER_DIGITS:
            raise ValueError("JSON number exceeds the digit limit")
        number = float(lexeme)
        if not math.isfinite(number):
            raise ValueError("JSON number must be finite")
        return number

    try:
        result = json.loads(
            value,
            object_pairs_hook=unique_object,
            parse_int=bounded_int,
            parse_float=bounded_float,
            parse_constant=lambda constant: (_ for _ in ()).throw(
                ValueError("non-finite JSON constant: %s" % constant)
            ),
        )
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        errors.append("%s must be a non-empty strict JSON object: %s" % (name, exc))
        return None
    if not isinstance(result, dict) or not result:
        errors.append("%s must be a non-empty strict JSON object" % name)
        return None
    stack = [(result, 0)]
    nodes = 0
    while stack:
        current, depth = stack.pop()
        nodes += 1
        if nodes > MAX_CONTEXT_JSON_NODES or depth > MAX_CONTEXT_JSON_DEPTH:
            errors.append("%s exceeds bounded JSON depth/node limits" % name)
            return None
        if isinstance(current, dict):
            stack.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            stack.extend((item, depth + 1) for item in current)
    return result


@lru_cache(maxsize=1)
def load_framework_catalog():
    try:
        with FRAMEWORK_CATALOG.open(encoding="utf-8") as handle:
            catalog = json.load(handle)
        frameworks = catalog["frameworks"]
        if (not isinstance(frameworks, dict)
                or not isinstance(catalog.get("catalog_version"), str)
                or not catalog["catalog_version"]):
            raise ValueError("catalog version/frameworks are invalid")
        return catalog, None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {}, "cannot load framework catalog fail-closed: %s" % exc


def validate(path, relative_path=None):
    if str(path) == "-":
        raw = sys.stdin.buffer.read(MAX_ARTIFACT_BYTES + 1)
    else:
        try:
            before = os.lstat(path)
            if stat.S_ISLNK(before.st_mode):
                return None, ["artifact cannot be a symlink"]
            if not stat.S_ISREG(before.st_mode):
                return None, ["artifact must be a regular file"]
            if before.st_nlink != 1:
                return None, ["artifact cannot be a hard-linked file"]
            flags = os.O_RDONLY
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            descriptor = os.open(path, flags)
            with os.fdopen(descriptor, "rb") as handle:
                opened = os.fstat(handle.fileno())
                if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                    return None, ["artifact changed while it was opened"]
                if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
                    return None, ["artifact must remain a single-link regular file"]
                raw = handle.read(MAX_ARTIFACT_BYTES + 1)
        except OSError as exc:
            return None, ["cannot read artifact: %s" % exc]
    if len(raw) > MAX_ARTIFACT_BYTES:
        return None, ["artifact exceeds %d-byte limit" % MAX_ARTIFACT_BYTES]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None, ["artifact must be UTF-8"]
    frontmatter, body_lines, errors = split_document(text)
    body, body_errors = parse_body(body_lines)
    errors.extend(body_errors)
    for name in sorted(set(frontmatter) - FRONTMATTER_FIELDS):
        errors.append("unknown frontmatter field: %s" % name)
    for name in sorted(set(body) - BODY_FIELDS):
        errors.append("unknown body field: %s" % name)
    record = dict(frontmatter)
    record.update(body)

    required_frontmatter = (
        "class", "schema_version", "runbook_version", "catalog_version", "framework", "profile",
    )
    required_body = (
        "status", "verdict", "score_state", "objective", "target", "observed_at",
        "context", "key_findings", "evidence_summary", "evidence_coverage", "score_confidence",
        "open_loops", "recommended_next_skill", "veto_count", "cap_applied",
    )
    for name in required_frontmatter:
        if not str(frontmatter.get(name, "")).strip():
            errors.append("missing frontmatter field: %s" % name)
    for name in required_body:
        if name not in body or (name != "key_findings" and not str(body.get(name, "")).strip()):
            errors.append("missing body field: %s" % name)

    if frontmatter.get("class") != "auditor-output":
        errors.append("class must be auditor-output")
    if frontmatter.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be %s" % SCHEMA_VERSION)
    if frontmatter.get("runbook_version") != RUNBOOK_VERSION:
        errors.append("runbook_version must be %s" % RUNBOOK_VERSION)
    framework = frontmatter.get("framework")
    if framework not in FRAMEWORKS:
        errors.append("framework must name one of the eight frameworks")
    profile = frontmatter.get("profile", "")
    if profile and not PROFILE_RE.fullmatch(profile):
        errors.append("profile must be a lowercase hyphenated slug")
    catalog_version = frontmatter.get("catalog_version", "")
    if catalog_version and not SEMVER_RE.fullmatch(catalog_version):
        errors.append("catalog_version must be a semantic version")
    context = as_json_object("context", body.get("context"), errors)
    catalog, catalog_error = load_framework_catalog()
    if catalog_error:
        errors.append(catalog_error)
    else:
        if catalog_version != catalog["catalog_version"]:
            errors.append(
                "catalog_version %s is not supported by the current validator; expected %s"
                % (catalog_version or "<missing>", catalog["catalog_version"])
            )
        frameworks = catalog["frameworks"]
        if framework == "MULTI":
            if profile != MULTI_PROFILE:
                errors.append("MULTI profile must be %s" % MULTI_PROFILE)
        elif framework in frameworks:
            specification = frameworks[framework]
            profiles = specification.get("profiles", {})
            if profile not in profiles:
                errors.append("profile %s is not declared for framework %s" % (profile, framework))
            if context is not None:
                for key in specification.get("required_context", []):
                    if key not in context or context[key] in (None, "", []):
                        errors.append("context is missing required field for %s: %s" % (framework, key))
                if profile in profiles:
                    for key, expected in profiles[profile].get("context_equals", {}).items():
                        if context.get(key) != expected:
                            errors.append(
                                "context.%s must be %r for profile %s" % (key, expected, profile)
                            )
                for key, allowed in specification.get("context_allowed", {}).items():
                    if context.get(key) not in allowed:
                        errors.append("context.%s must be one of %s" % (key, allowed))

    status = body.get("status")
    verdict = body.get("verdict")
    score_state = body.get("score_state")
    if status not in STATUSES:
        errors.append("invalid status")
    if verdict not in VERDICTS:
        errors.append("invalid verdict")
    if score_state not in SCORE_STATES:
        errors.append("invalid score_state")
    if body.get("score_confidence") not in CONFIDENCE:
        errors.append("invalid score_confidence")
    if score_state == "NOT_SCORED" and body.get("score_confidence") != "not_scored":
        errors.append("NOT_SCORED requires score_confidence: not_scored")
    if score_state == "SCORED" and body.get("score_confidence") == "not_scored":
        errors.append("SCORED requires low/medium/high score_confidence")
    try:
        dt.date.fromisoformat(str(body.get("observed_at", "")))
    except ValueError:
        errors.append("observed_at must be an ISO date")

    coverage = as_int("evidence_coverage", body.get("evidence_coverage"), errors, 0, 100)
    veto_count = as_int("veto_count", body.get("veto_count"), errors, 0)
    cap_applied = as_bool("cap_applied", body.get("cap_applied"), errors)
    raw = None
    final = None
    if "raw_overall_score" in body:
        raw = as_int("raw_overall_score", body.get("raw_overall_score"), errors, 0, 100)
    if "final_overall_score" in body:
        final = as_int("final_overall_score", body.get("final_overall_score"), errors, 0, 100)

    if relative_path:
        parts = relative_path.replace("\\", "/").split("/")
        if len(parts) >= 3 and parts[:2] == ["memory", "audits"]:
            if len(parts) == 3:
                if framework != "MULTI":
                    errors.append("only MULTI summaries may be stored directly under memory/audits/")
            else:
                expected = PATH_FRAMEWORK.get(parts[2])
                if expected is None:
                    errors.append("unknown auditor sink: %s" % parts[2])
                elif framework != expected:
                    errors.append("path %s requires framework %s" % (parts[2], expected))
                if framework == "MULTI":
                    errors.append("MULTI summaries belong directly under memory/audits/")

    veto_findings = sum(
        1 for finding in body.get("key_findings", [])
        if isinstance(finding, dict) and finding.get("severity") == "veto"
    )
    if veto_count is not None and veto_findings != veto_count:
        errors.append("veto_count must equal the number of veto key_findings")

    if framework == "MULTI":
        if status != "DONE":
            errors.append("MULTI summaries require status DONE")
        if score_state != "NOT_SCORED" or verdict != "UNDECIDED":
            errors.append("MULTI summaries require verdict UNDECIDED and NOT_SCORED")
        if veto_count not in (None, 0):
            errors.append("MULTI summaries must not aggregate veto_count")
        if cap_applied is not False:
            errors.append("MULTI summaries require cap_applied:false")
        if raw is not None or final is not None:
            errors.append("MULTI summaries must not emit a composite score")

    execution_stopped = status in {"BLOCKED", "NEEDS_INPUT"}
    if execution_stopped:
        if verdict != "UNDECIDED" or score_state != "NOT_SCORED":
            errors.append("execution BLOCKED/NEEDS_INPUT requires verdict UNDECIDED and NOT_SCORED")
        if raw is not None or final is not None:
            errors.append("an incomplete execution must not emit scores")
        if cap_applied is True:
            errors.append("an incomplete execution cannot apply a cap")
    if score_state == "NOT_SCORED":
        if raw is not None or final is not None:
            errors.append("NOT_SCORED must omit raw/final scores")
        if cap_applied is not False:
            errors.append("NOT_SCORED requires cap_applied:false")
        if framework != "MULTI":
            if veto_count is not None and veto_count >= 2:
                if status != "DONE" or verdict != "BLOCK":
                    errors.append(
                        "NOT_SCORED with two or more vetoes requires status DONE and verdict BLOCK"
                    )
            elif status not in {"BLOCKED", "NEEDS_INPUT"} or verdict != "UNDECIDED":
                errors.append(
                    "NOT_SCORED with fewer than two vetoes requires execution stop and UNDECIDED"
                )
    elif score_state == "SCORED":
        if coverage is not None and coverage < MIN_SCORE_COVERAGE:
            errors.append("SCORED requires evidence_coverage >= %d" % MIN_SCORE_COVERAGE)
        if raw is None:
            errors.append("SCORED requires raw_overall_score")
        if veto_count == 0:
            if cap_applied is not False or final != raw:
                errors.append("zero vetoes require cap_applied:false and final == raw")
            if verdict not in {"SHIP", "FIX"}:
                errors.append("zero vetoes require SHIP or FIX")
            if verdict == "SHIP" and raw is not None and raw < 75:
                errors.append("SHIP requires raw_overall_score >= 75")
        elif veto_count == 1:
            expected_final = min(raw, VETO_CEILING) if raw is not None else None
            if cap_applied is not True or final != expected_final or verdict != "FIX":
                errors.append("one veto requires FIX and final=min(raw, %d)" % VETO_CEILING)
        elif veto_count is not None and veto_count >= 2:
            if cap_applied is not False or final is not None or verdict != "BLOCK":
                errors.append("two or more vetoes require BLOCK, no final score, and no cap")

    if framework != "MULTI":
        expected_status = {
            "SHIP": "DONE",
            "FIX": "DONE_WITH_CONCERNS",
            "BLOCK": "DONE",
        }.get(verdict)
        if expected_status is not None and status != expected_status:
            errors.append("verdict %s requires status %s" % (verdict, expected_status))
        if verdict == "UNDECIDED" and status not in {"BLOCKED", "NEEDS_INPUT"}:
            errors.append("verdict UNDECIDED requires status BLOCKED or NEEDS_INPUT")

    for name in ("objective", "target", "evidence_summary", "open_loops", "recommended_next_skill"):
        if name in body and not str(body[name]).strip():
            errors.append("%s must be non-empty" % name)

    if not errors:
        record["context"] = context
        record["evidence_coverage"] = coverage
        record["veto_count"] = veto_count
        record["cap_applied"] = cap_applied
        if raw is not None:
            record["raw_overall_score"] = raw
        if final is not None:
            record["final_overall_score"] = final
    return record, sorted(set(errors))


def _directory_mode_is_traversable(mode):
    """Reject mode-bit-inaccessible trees even when the hook runs as root."""
    return any(
        mode & read_bit and mode & execute_bit
        for read_bit, execute_bit in (
            (stat.S_IRUSR, stat.S_IXUSR),
            (stat.S_IRGRP, stat.S_IXGRP),
            (stat.S_IROTH, stat.S_IXOTH),
        )
    )


def validate_sink(root, deadline_seconds=MAX_SINK_SECONDS):
    """Validate a reserved audit sink in one bounded, fail-closed traversal."""
    root = Path(root)
    errors = []
    try:
        root_before = os.lstat(root)
    except OSError as exc:
        return ["cannot inspect audit sink: %s" % exc]
    if stat.S_ISLNK(root_before.st_mode) or not stat.S_ISDIR(root_before.st_mode):
        return ["audit sink must be a real directory"]
    if not _directory_mode_is_traversable(root_before.st_mode):
        return ["audit sink directory is not readable and searchable: %s" % root]

    stack = [root]
    file_count = 0
    entry_count = 0
    total_bytes = 0
    deadline = time.monotonic() + deadline_seconds
    while stack:
        if time.monotonic() >= deadline:
            return errors + ["audit sink validation exceeded its internal deadline"]
        directory = stack.pop()
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(iterator, key=lambda entry: entry.name)
        except OSError as exc:
            errors.append("cannot traverse audit sink directory %s: %s" % (directory, exc))
            continue
        for entry in entries:
            if time.monotonic() >= deadline:
                return errors + ["audit sink validation exceeded its internal deadline"]
            entry_count += 1
            if entry_count > MAX_SINK_ENTRIES:
                return errors + ["audit sink exceeds %d-entry limit" % MAX_SINK_ENTRIES]
            path = Path(entry.path)
            try:
                metadata = entry.stat(follow_symlinks=False)
            except OSError as exc:
                errors.append("cannot inspect audit sink entry %s: %s" % (path, exc))
                continue
            if stat.S_ISLNK(metadata.st_mode):
                errors.append("symlinks are not allowed in the audit sink: %s" % path)
            elif stat.S_ISDIR(metadata.st_mode):
                if not _directory_mode_is_traversable(metadata.st_mode):
                    errors.append(
                        "audit sink directory is not readable and searchable: %s" % path
                    )
                else:
                    stack.append(path)
            elif stat.S_ISREG(metadata.st_mode):
                file_count += 1
                if file_count > MAX_SINK_FILES:
                    return errors + ["audit sink exceeds %d-file limit" % MAX_SINK_FILES]
                if metadata.st_nlink != 1:
                    errors.append("hard-linked files are not allowed in the audit sink: %s" % path)
                    continue
                total_bytes += metadata.st_size
                if total_bytes > MAX_SINK_TOTAL_BYTES:
                    return errors + [
                        "audit sink exceeds %d-byte aggregate limit" % MAX_SINK_TOTAL_BYTES
                    ]
                if path.suffix != ".md":
                    errors.append("audit sink files must use the .md artifact format: %s" % path)
                    continue
                relative = "memory/audits/" + path.relative_to(root).as_posix()
                _, artifact_errors = validate(path, relative)
                errors.extend("%s: %s" % (relative, error) for error in artifact_errors)
            else:
                errors.append("special files are not allowed in the audit sink: %s" % path)
    try:
        root_after = os.lstat(root)
    except OSError as exc:
        errors.append("cannot re-inspect audit sink after traversal: %s" % exc)
    else:
        if (root_after.st_dev, root_after.st_ino) != (root_before.st_dev, root_before.st_ino):
            errors.append("audit sink changed during traversal")
    return sorted(set(errors))


def _hook_string_leaves(value, key=""):
    stack = [(value, key, 0)]
    nodes = 0
    while stack:
        current, current_key, depth = stack.pop()
        nodes += 1
        if nodes > MAX_HOOK_JSON_NODES or depth > MAX_HOOK_JSON_DEPTH:
            raise ValueError("hook input exceeds bounded JSON traversal limits")
        if isinstance(current, str):
            yield current_key, current
        elif isinstance(current, dict):
            for child_key, child in current.items():
                normalized = re.sub(r"[^a-z]", "", str(child_key).lower())
                stack.append((child, normalized, depth + 1))
        elif isinstance(current, list):
            stack.extend((child, current_key, depth + 1) for child in current)


def preflight_hook_write(project_root, hook_input):
    """Allow only a validator-clean, full-content Write into memory/audits/."""
    if not isinstance(hook_input, dict) or not isinstance(hook_input.get("tool_input"), dict):
        return ["hook input must contain an object tool_input"]
    tool_name = hook_input.get("tool_name")
    tool_input = hook_input["tool_input"]
    if not isinstance(tool_name, str):
        return ["hook input must contain tool_name"]
    root = Path(project_root).resolve(strict=True)
    path_keys = {
        "destination", "destinationpath", "filepath", "notebookpath", "outputpath",
        "path", "target", "targetpath",
    }
    leaves = list(_hook_string_leaves(tool_input))
    path_values = [value for key, value in leaves if key in path_keys]
    audit_targets = []
    for raw_path in path_values:
        lexical = Path(raw_path)
        lexical = lexical if lexical.is_absolute() else root / lexical
        lexical = Path(os.path.abspath(lexical))
        try:
            relative = lexical.relative_to(root)
        except ValueError:
            continue
        if (len(relative.parts) >= 3
                and relative.parts[0].casefold() == "memory"
                and relative.parts[1].casefold() == "audits"):
            audit_targets.append(relative)
    command_mentions_sink = any(
        key in {"command", "script", "code", "chars"}
        and re.search(r"(?i)(?:^|[/\\])memory[/\\]audits(?:[/\\]|$)", value)
        for key, value in leaves
    )
    if not audit_targets and not command_mentions_sink:
        return []
    if tool_name != "Write" or len(audit_targets) != 1:
        return [
            "memory/audits accepts only one exact-target full-content Write; "
            "Edit, notebook, shell, monitor, PowerShell, and MCP mutations are unsupported"
        ]
    if audit_targets[0].suffix != ".md":
        return ["memory/audits accepts only .md artifact targets"]
    content = tool_input.get("content")
    if not isinstance(content, str):
        return ["an audit Write requires the complete UTF-8 artifact in tool_input.content"]
    relative_path = audit_targets[0].as_posix()
    try:
        encoded = content.encode("utf-8")
    except UnicodeEncodeError:
        return ["audit Write content must be UTF-8 encodable"]
    if len(encoded) > MAX_ARTIFACT_BYTES:
        return ["artifact exceeds %d-byte limit" % MAX_ARTIFACT_BYTES]
    descriptor, temporary_path = tempfile.mkstemp(prefix="aaron-audit-preflight-")
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
        _, errors = validate(temporary_path, relative_path)
        return errors
    finally:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?")
    parser.add_argument("--scan-root", help="Validate every entry in a reserved audit sink.")
    parser.add_argument(
        "--preflight-hook", action="store_true",
        help="Read PreToolUse JSON from stdin and prevalidate reserved-sink writes.",
    )
    parser.add_argument("--project-root", help="Host project root for --preflight-hook.")
    parser.add_argument("--relative-path")
    parser.add_argument("--json", action="store_true", help="Print the normalized record.")
    args = parser.parse_args(argv)
    modes = sum(bool(value) for value in (args.artifact, args.scan_root, args.preflight_hook))
    if modes != 1:
        parser.error("provide exactly one artifact, --scan-root, or --preflight-hook")
    if args.preflight_hook:
        if not args.project_root:
            parser.error("--preflight-hook requires --project-root")
        raw = sys.stdin.buffer.read(MAX_HOOK_INPUT_BYTES + 1)
        if len(raw) > MAX_HOOK_INPUT_BYTES:
            print("- hook input exceeds size limit", file=sys.stderr)
            return 1
        try:
            hook_input = json.loads(raw.decode("utf-8"))
            errors = preflight_hook_write(args.project_root, hook_input)
        except (OSError, UnicodeDecodeError, ValueError, RecursionError) as exc:
            errors = ["cannot preflight audit write: %s" % exc]
        if errors:
            for error in sorted(set(errors)):
                print("- " + error, file=sys.stderr)
            return 1
        return 0
    if args.scan_root:
        errors = validate_sink(args.scan_root)
        if errors:
            for error in errors:
                print("- " + error, file=sys.stderr)
            return 1
        return 0
    record, errors = validate(args.artifact, args.relative_path)
    if errors:
        for error in errors:
            print("- " + error, file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
