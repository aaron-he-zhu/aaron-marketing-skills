#!/usr/bin/env python3
"""Strict behavior-eval case loading and deterministic profile selection.

The authored corpus deliberately uses a tiny, single-line YAML-flow subset.
This module parses that subset without PyYAML, projects every case into the
runner's flat request shape, and selects smoke/change-aware/nightly profiles.
It is importable by ``run-behavior-evals.py`` and has no third-party runtime
dependencies.
"""
from __future__ import annotations

import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parent.parent
BASE_CASE_FIELDS = (
    "id",
    "type",
    "status",
    "target_skill",
    "scenario",
    "input_summary",
    "expected_behavior",
    "failure_modes",
)
AUTO_CASE_FIELDS = (
    "scenario_family",
    "risk_gates",
    "expected_route",
    "blocking_inputs",
    "must_not",
)
EVIDENCE_FIELDS = ("evidence_ref", "evidence_sha256")
RUNNER_CASE_FIELDS = (
    "id",
    "type",
    "case_provenance",
    "evidence_binding",
    "target_skill",
    "scenario",
    "input_summary",
    "expected_behavior",
    "failure_modes",
    "source_ref",
    "source_line",
    "case_sha256",
    "source_group",
)
PROFILE_NAMES = ("smoke", "change-aware", "nightly")
MAX_SOURCE_BYTES = 16_000_000
MAX_LINE_BYTES = 1_000_000
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
BARE_RE = re.compile(r"^[A-Za-z0-9_./+-]+(?:-[A-Za-z0-9_./+-]+)*$")
SHARD_MARKER_RE = re.compile(r"^<!-- auto-routing-shard: ([a-z0-9-]+) -->$")
SAFE_REF_RE = re.compile(
    r"^(?!/)(?!.*//)(?!.*(?:^|/)\.\.?(?:/|$))(?!.*\/$)"
    r"[A-Za-z0-9][A-Za-z0-9._/-]*$"
)


class EvalCaseError(ValueError):
    """A corpus, profile, provenance, or selection contract is invalid."""


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _strict_json(raw: str, label: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise EvalCaseError("%s contains duplicate key %r" % (label, key))
            result[key] = value
        return result

    try:
        def reject_constant(value: str) -> None:
            raise EvalCaseError("%s contains non-JSON numeric constant %s" % (label, value))

        return json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)
    except EvalCaseError:
        raise
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise EvalCaseError("%s is not strict JSON: %s" % (label, exc)) from None


def _normalize_root(root: os.PathLike[str] | str) -> Path:
    path = Path(root).resolve()
    if not path.is_dir():
        raise EvalCaseError("project root is not a directory: %s" % path)
    return path


def _normalize_ref(reference: str, label: str = "reference") -> str:
    if (
        not isinstance(reference, str)
        or len(reference) > 512
        or not SAFE_REF_RE.fullmatch(reference)
    ):
        raise EvalCaseError("%s is not a safe project-relative path: %r" % (label, reference))
    normalized = PurePosixPath(reference).as_posix()
    if normalized != reference:
        raise EvalCaseError("%s is not canonical: %r" % (label, reference))
    return normalized


def _read_project_bytes(root: Path, reference: str) -> bytes:
    reference = _normalize_ref(reference)
    parts = PurePosixPath(reference).parts
    descriptor: int | None = None
    directory_descriptors: list[int] = []
    try:
        # Anchor every component below the already-resolved project root.  A
        # final-only O_NOFOLLOW check would still permit an intermediate
        # directory symlink to escape the repository.
        if os.open in os.supports_dir_fd and hasattr(os, "O_NOFOLLOW"):
            directory_flags = os.O_RDONLY | os.O_NOFOLLOW
            if hasattr(os, "O_DIRECTORY"):
                directory_flags |= os.O_DIRECTORY
            directory = os.open(root, directory_flags)
            directory_descriptors.append(directory)
            for component in parts[:-1]:
                directory = os.open(component, directory_flags, dir_fd=directory)
                directory_descriptors.append(directory)
            descriptor = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory
            )
        else:  # pragma: no cover - exercised only on platforms without dir_fd
            current = root
            for component in parts:
                current = current / component
                metadata = os.lstat(current)
                if stat.S_ISLNK(metadata.st_mode):
                    raise EvalCaseError("%s traverses a symbolic link" % reference)
            resolved = current.resolve(strict=True)
            try:
                resolved.relative_to(root)
            except ValueError:
                raise EvalCaseError("%s escapes the project root" % reference) from None
            descriptor = os.open(resolved, os.O_RDONLY)
    except EvalCaseError:
        for item in reversed(directory_descriptors):
            os.close(item)
        raise
    except OSError as exc:
        for item in reversed(directory_descriptors):
            os.close(item)
        raise EvalCaseError("cannot open %s: %s" % (reference, exc)) from None
    assert descriptor is not None
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise EvalCaseError("%s is not a regular file" % reference)
        if metadata.st_size > MAX_SOURCE_BYTES:
            raise EvalCaseError(
                "%s exceeds the %d-byte source limit" % (reference, MAX_SOURCE_BYTES)
            )
        chunks: list[bytes] = []
        remaining = MAX_SOURCE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_SOURCE_BYTES:
            raise EvalCaseError(
                "%s exceeds the %d-byte source limit" % (reference, MAX_SOURCE_BYTES)
            )
        after = os.fstat(descriptor)
        if (
            metadata.st_dev,
            metadata.st_ino,
            metadata.st_size,
            metadata.st_mtime_ns,
            metadata.st_ctime_ns,
        ) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise EvalCaseError("%s changed while it was read" % reference)
        return raw
    finally:
        os.close(descriptor)
        for item in reversed(directory_descriptors):
            os.close(item)


def _read_project_text(root: Path, reference: str) -> tuple[str, bytes]:
    raw = _read_project_bytes(root, reference)
    try:
        return raw.decode("utf-8"), raw
    except UnicodeDecodeError as exc:
        raise EvalCaseError("%s is not valid UTF-8: %s" % (reference, exc)) from None


class _FlowParser:
    """Parser for the corpus' mapping/list/string/bare-token flow subset."""

    def __init__(self, text: str, label: str):
        self.text = text
        self.label = label
        self.pos = 0

    def error(self, message: str) -> EvalCaseError:
        return EvalCaseError("%s at column %d: %s" % (self.label, self.pos + 1, message))

    def skip_space(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in " \t":
            self.pos += 1

    def peek(self) -> str | None:
        return self.text[self.pos] if self.pos < len(self.text) else None

    def expect(self, token: str) -> None:
        self.skip_space()
        if self.peek() != token:
            raise self.error("expected %r" % token)
        self.pos += 1

    def quoted_string(self) -> str:
        start = self.pos
        try:
            value, end = json.JSONDecoder().raw_decode(self.text, self.pos)
        except json.JSONDecodeError as exc:
            raise self.error("invalid quoted string: %s" % exc.msg) from None
        if not isinstance(value, str):
            raise self.error("only quoted strings are supported")
        if end <= start:
            raise self.error("empty parser advance")
        self.pos = end
        return value

    def bare_token(self, *, key: bool = False) -> str:
        start = self.pos
        stops = ":,{}[] \t" if key else ",]} \t"
        while self.pos < len(self.text) and self.text[self.pos] not in stops:
            self.pos += 1
        value = self.text[start:self.pos]
        if not value or not BARE_RE.fullmatch(value):
            raise self.error("invalid bare %s %r" % ("key" if key else "value", value))
        return value

    def value(self) -> Any:
        self.skip_space()
        current = self.peek()
        if current == '"':
            return self.quoted_string()
        if current == "[":
            return self.list_value()
        if current == "{":
            raise self.error("nested mappings are not part of the eval-case subset")
        if current is None:
            raise self.error("missing value")
        return self.bare_token()

    def list_value(self) -> list[Any]:
        self.expect("[")
        result: list[Any] = []
        self.skip_space()
        if self.peek() == "]":
            self.pos += 1
            return result
        while True:
            result.append(self.value())
            self.skip_space()
            current = self.peek()
            if current == "]":
                self.pos += 1
                return result
            if current != ",":
                raise self.error("expected ',' or ']' in list")
            self.pos += 1
            self.skip_space()
            if self.peek() == "]":
                raise self.error("trailing commas are not allowed")

    def mapping(self) -> dict[str, Any]:
        self.expect("{")
        result: dict[str, Any] = {}
        self.skip_space()
        if self.peek() == "}":
            self.pos += 1
            return result
        while True:
            self.skip_space()
            if self.peek() == '"':
                key = self.quoted_string()
            else:
                key = self.bare_token(key=True)
            if key in result:
                raise self.error("duplicate key %r" % key)
            self.expect(":")
            result[key] = self.value()
            self.skip_space()
            current = self.peek()
            if current == "}":
                self.pos += 1
                return result
            if current != ",":
                raise self.error("expected ',' or '}' in mapping")
            self.pos += 1
            self.skip_space()
            if self.peek() == "}":
                raise self.error("trailing commas are not allowed")

    def parse(self) -> dict[str, Any]:
        value = self.mapping()
        self.skip_space()
        if self.pos != len(self.text):
            raise self.error("unexpected trailing content")
        return value


def parse_flow_object(text: str, label: str = "eval case") -> dict[str, Any]:
    """Parse one strict single-line eval flow object."""
    if not isinstance(text, str) or "\n" in text or "\r" in text:
        raise EvalCaseError("%s must be one text line" % label)
    if len(text.encode("utf-8")) > MAX_LINE_BYTES:
        raise EvalCaseError("%s exceeds the %d-byte line limit" % (label, MAX_LINE_BYTES))
    return _FlowParser(text.strip(), label).parse()


def _case_text_from_line(line: str) -> str | None:
    stripped = line.strip()
    if stripped.startswith("-"):
        stripped = stripped[1:].lstrip()
    if not stripped.startswith("{"):
        return None
    return stripped


def load_catalog(root: os.PathLike[str] | str = ROOT) -> dict[str, Any]:
    """Load the topology SSOT with duplicate-key and basic shape validation."""
    project = _normalize_root(root)
    text, _ = _read_project_text(project, "references/system-catalog.json")
    value = _strict_json(text, "references/system-catalog.json")
    if not isinstance(value, dict):
        raise EvalCaseError("system catalog must be an object")
    if not isinstance(value.get("logical_order"), list) or not isinstance(
        value.get("disciplines"), dict
    ):
        raise EvalCaseError("system catalog lacks logical_order/disciplines")
    if not isinstance(value.get("protocol"), dict):
        raise EvalCaseError("system catalog lacks protocol")
    return value


def _catalog_index(catalog: Mapping[str, Any]) -> dict[str, Any]:
    skills: dict[str, dict[str, str]] = {}
    commands: dict[str, str] = {}
    logical_order = catalog.get("logical_order")
    disciplines = catalog.get("disciplines")
    if not isinstance(logical_order, list) or not isinstance(disciplines, dict):
        raise EvalCaseError("invalid catalog topology")
    for discipline in logical_order:
        if discipline == "protocol":
            continue
        spec = disciplines.get(discipline)
        if not isinstance(discipline, str) or not isinstance(spec, dict):
            raise EvalCaseError("catalog logical discipline is invalid: %r" % discipline)
        phase_order = spec.get("phase_order")
        phases = spec.get("phases")
        command = spec.get("command")
        if not isinstance(phase_order, list) or not isinstance(phases, dict):
            raise EvalCaseError("catalog discipline %s has invalid phases" % discipline)
        if not isinstance(command, dict) or not isinstance(command.get("name"), str):
            raise EvalCaseError("catalog discipline %s has invalid command" % discipline)
        commands[command["name"]] = discipline
        for phase in phase_order:
            slugs = phases.get(phase)
            if not isinstance(phase, str) or not isinstance(slugs, list):
                raise EvalCaseError("catalog discipline %s phase is invalid" % discipline)
            for slug in slugs:
                if not isinstance(slug, str) or not ID_RE.fullmatch(slug):
                    raise EvalCaseError("catalog contains invalid skill slug %r" % slug)
                if slug in skills:
                    raise EvalCaseError("catalog duplicates skill %s" % slug)
                skills[slug] = {
                    "discipline": discipline,
                    "phase": phase,
                    "path": "%s/%s/%s/SKILL.md" % (discipline, phase, slug),
                }
    protocol = catalog.get("protocol")
    if not isinstance(protocol, dict) or not isinstance(protocol.get("skills"), list):
        raise EvalCaseError("catalog protocol skills are invalid")
    for slug in protocol["skills"]:
        if not isinstance(slug, str) or not ID_RE.fullmatch(slug):
            raise EvalCaseError("catalog contains invalid protocol skill %r" % slug)
        if slug in skills:
            raise EvalCaseError("catalog duplicates skill %s" % slug)
        skills[slug] = {
            "discipline": "protocol",
            "phase": "protocol",
            "path": "protocol/%s/SKILL.md" % slug,
        }
    commands["auto"] = "auto"
    auditors: list[str] = []
    for discipline in logical_order:
        if discipline == "protocol":
            continue
        gates = disciplines[discipline].get("gates")
        if not isinstance(gates, list):
            raise EvalCaseError("catalog discipline %s has invalid gates" % discipline)
        for slug in gates:
            if slug not in skills or slug in auditors:
                raise EvalCaseError("catalog contains invalid/duplicate gate %r" % slug)
            auditors.append(slug)
    return {
        "skills": skills,
        "commands": commands,
        "auditors": auditors,
        "disciplines": [item for item in logical_order if item != "protocol"] + ["protocol"],
    }


def _validate_string(value: Any, label: str, maximum: int | None = None) -> str:
    if (
        not isinstance(value, str)
        or not value.strip()
        or (maximum is not None and len(value) > maximum)
    ):
        raise EvalCaseError("%s must be a non-empty string" % label)
    return value


def _validate_string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value or len(value) > 64:
        raise EvalCaseError("%s must be a non-empty list" % label)
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_validate_string(item, "%s[%d]" % (label, index), 4000))
    return result


def _validate_source_case(
    value: dict[str, Any],
    *,
    root: Path,
    kind: str,
    label: str,
    valid_skills: set[str],
    expected_target: str | None = None,
) -> None:
    expected = set(BASE_CASE_FIELDS)
    if kind == "auto":
        expected.update(AUTO_CASE_FIELDS)
    status = value.get("status")
    if status == "real":
        expected.update(EVIDENCE_FIELDS)
    actual = set(value)
    missing = sorted(expected - actual)
    unknown = sorted(actual - expected)
    if missing:
        raise EvalCaseError("%s is missing fields: %s" % (label, ", ".join(missing)))
    if unknown:
        raise EvalCaseError("%s has unknown fields: %s" % (label, ", ".join(unknown)))
    if value["type"] != "eval-case":
        raise EvalCaseError("%s type must be eval-case" % label)
    if status not in {"simulated", "real"}:
        raise EvalCaseError("%s status must be simulated or real" % label)
    case_id = _validate_string(value["id"], label + ".id")
    if len(case_id) > 160 or not ID_RE.fullmatch(case_id):
        raise EvalCaseError("%s id is not a canonical slug" % label)
    target = _validate_string(value["target_skill"], label + ".target_skill")
    if target not in valid_skills:
        raise EvalCaseError("%s names unknown target_skill %r" % (label, target))
    if expected_target is not None and target != expected_target:
        raise EvalCaseError(
            "%s target_skill %r does not match its authored source %r"
            % (label, target, expected_target)
        )
    for field in ("scenario", "input_summary"):
        _validate_string(value[field], "%s.%s" % (label, field), 16000)
    for field in ("expected_behavior", "failure_modes"):
        _validate_string_list(value[field], "%s.%s" % (label, field))
    if kind == "auto":
        for field in ("scenario_family", "expected_route"):
            _validate_string(value[field], "%s.%s" % (label, field))
        for field in ("risk_gates", "blocking_inputs", "must_not"):
            _validate_string_list(value[field], "%s.%s" % (label, field))
    if status == "real":
        reference = _validate_string(value["evidence_ref"], label + ".evidence_ref")
        _normalize_ref(reference, label + ".evidence_ref")
        digest = _validate_string(value["evidence_sha256"], label + ".evidence_sha256")
        if not SHA256_RE.fullmatch(digest):
            raise EvalCaseError("%s evidence_sha256 must be lowercase SHA-256" % label)
        actual = _sha256(_read_project_bytes(root, reference))
        if actual != digest:
            raise EvalCaseError(
                "%s evidence_sha256 does not match %s" % (label, reference)
            )


def _runner_case(
    value: Mapping[str, Any],
    *,
    source_ref: str,
    source_line: int,
    source_group: str,
    case_hash_value: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "id": value["id"],
        "type": "eval-case",
        "case_provenance": value.get("status", "simulated"),
        "evidence_binding": (
            {
                "ref": value["evidence_ref"],
                "sha256": value["evidence_sha256"],
            }
            if value.get("status") == "real"
            else None
        ),
        "target_skill": value["target_skill"],
        "scenario": value["scenario"],
        "input_summary": value["input_summary"],
        "expected_behavior": list(value["expected_behavior"]),
        "failure_modes": list(value["failure_modes"]),
        "source_ref": source_ref,
        "source_line": source_line,
        "case_sha256": _sha256(_canonical_json(case_hash_value or value)),
        "source_group": source_group,
    }
    if tuple(result) != RUNNER_CASE_FIELDS:
        raise AssertionError("runner case projection drifted")
    return result


def _load_authored_cases(
    root: Path, catalog_index: Mapping[str, Any]
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    valid_skills = set(catalog_index["skills"])
    for slug in catalog_index["skills"]:
        source_ref = "evals/%s/cases.md" % slug
        text, _ = _read_project_text(root, source_ref)
        found = 0
        for line_number, line in enumerate(text.splitlines(), 1):
            candidate = _case_text_from_line(line)
            if candidate is None:
                continue
            found += 1
            label = "%s line %d" % (source_ref, line_number)
            parsed = parse_flow_object(candidate, label)
            _validate_source_case(
                parsed,
                root=root,
                kind="authored",
                label=label,
                valid_skills=valid_skills,
                expected_target=slug,
            )
            cases.append(
                _runner_case(
                    parsed,
                    source_ref=source_ref,
                    source_line=line_number,
                    source_group="authored",
                )
            )
        if not found:
            raise EvalCaseError("%s has no eval case objects" % source_ref)
    return cases


def _load_auto_cases(root: Path, catalog_index: Mapping[str, Any]) -> list[dict[str, Any]]:
    source_ref = "evals/auto-routing-scenarios.source.md"
    text, _ = _read_project_text(root, source_ref)
    valid_skills = set(catalog_index["skills"])
    legal_shards = set(catalog_index["disciplines"]) - {"protocol"}
    legal_shards.add("cross-discipline")
    seen_shards: set[str] = set()
    current_shard: str | None = None
    cases: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        marker = SHARD_MARKER_RE.fullmatch(line)
        if marker:
            current_shard = marker.group(1)
            if current_shard not in legal_shards:
                raise EvalCaseError(
                    "%s line %d has unknown shard %r"
                    % (source_ref, line_number, current_shard)
                )
            if current_shard in seen_shards:
                raise EvalCaseError(
                    "%s line %d duplicates shard %r"
                    % (source_ref, line_number, current_shard)
                )
            seen_shards.add(current_shard)
            continue
        candidate = _case_text_from_line(line)
        if candidate is None:
            continue
        if current_shard is None:
            raise EvalCaseError(
                "%s line %d has a case before a shard marker" % (source_ref, line_number)
            )
        label = "%s line %d" % (source_ref, line_number)
        parsed = parse_flow_object(candidate, label)
        _validate_source_case(
            parsed,
            root=root,
            kind="auto",
            label=label,
            valid_skills=valid_skills,
        )
        cases.append(
            _runner_case(
                parsed,
                source_ref=source_ref,
                source_line=line_number,
                source_group="auto-routing",
            )
        )
    missing_shards = sorted(legal_shards - seen_shards)
    if missing_shards:
        raise EvalCaseError("%s lacks shards: %s" % (source_ref, ", ".join(missing_shards)))
    if not cases:
        raise EvalCaseError("%s has no eval case objects" % source_ref)
    return cases


def index_cases(cases: Iterable[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Validate the flat runner shape and return a unique ID index."""
    result: dict[str, dict[str, Any]] = {}
    for position, case in enumerate(cases, 1):
        if not isinstance(case, Mapping) or set(case) != set(RUNNER_CASE_FIELDS):
            raise EvalCaseError("runner case #%d does not have the exact request fields" % position)
        if case.get("type") != "eval-case":
            raise EvalCaseError("runner case #%d type must be eval-case" % position)
        if case.get("case_provenance") not in {"simulated", "real"}:
            raise EvalCaseError("runner case #%d has invalid provenance" % position)
        evidence = case.get("evidence_binding")
        if case.get("case_provenance") == "simulated":
            if evidence is not None:
                raise EvalCaseError("runner case #%d simulated provenance has evidence" % position)
        elif not isinstance(evidence, Mapping) or set(evidence) != {"ref", "sha256"}:
            raise EvalCaseError("runner case #%d real provenance lacks evidence binding" % position)
        else:
            _normalize_ref(evidence.get("ref"), "runner case evidence ref")
            if not isinstance(evidence.get("sha256"), str) or not SHA256_RE.fullmatch(
                evidence["sha256"]
            ):
                raise EvalCaseError("runner case #%d has invalid evidence hash" % position)
        case_id = case.get("id")
        if (
            not isinstance(case_id, str)
            or len(case_id) > 160
            or not ID_RE.fullmatch(case_id)
        ):
            raise EvalCaseError("runner case #%d has invalid id" % position)
        if case_id in result:
            raise EvalCaseError("duplicate eval case id %r" % case_id)
        if not isinstance(case.get("source_line"), int) or isinstance(
            case.get("source_line"), bool
        ) or case["source_line"] < 1:
            raise EvalCaseError("runner case %s has invalid source_line" % case_id)
        if not isinstance(case.get("case_sha256"), str) or not SHA256_RE.fullmatch(
            case["case_sha256"]
        ):
            raise EvalCaseError("runner case %s has invalid case_sha256" % case_id)
        _normalize_ref(case.get("source_ref"), "runner case %s source_ref" % case_id)
        source_group = _validate_string(
            case.get("source_group"), "runner case %s source_group" % case_id
        )
        if source_group not in {"authored", "auto-routing", "derived-auditor"}:
            raise EvalCaseError("runner case %s has invalid source_group" % case_id)
        _validate_string(case.get("target_skill"), "runner case %s target_skill" % case_id)
        _validate_string(case.get("scenario"), "runner case %s scenario" % case_id, 16000)
        _validate_string(
            case.get("input_summary"), "runner case %s input_summary" % case_id, 16000
        )
        _validate_string_list(
            case.get("expected_behavior"), "runner case %s expected_behavior" % case_id
        )
        _validate_string_list(
            case.get("failure_modes"), "runner case %s failure_modes" % case_id
        )
        result[case_id] = dict(case)
    return result


def load_cases(
    root: os.PathLike[str] | str = ROOT,
    *,
    include_authored: bool = True,
    include_auto: bool = True,
) -> list[dict[str, Any]]:
    """Load the 606 authored and/or 88 authoritative auto-routing cases."""
    if not include_authored and not include_auto:
        return []
    project = _normalize_root(root)
    catalog_index = _catalog_index(load_catalog(project))
    cases: list[dict[str, Any]] = []
    if include_authored:
        cases.extend(_load_authored_cases(project, catalog_index))
    if include_auto:
        cases.extend(_load_auto_cases(project, catalog_index))
    index_cases(cases)
    return cases


def _contract_ref(entry: Mapping[str, Any], label: str) -> tuple[str, str]:
    reference = entry.get("ref", entry.get("contract_ref"))
    digest = entry.get("sha256", entry.get("contract_sha256"))
    if not isinstance(reference, str):
        raise EvalCaseError("%s lacks ref" % label)
    _normalize_ref(reference, label + ".ref")
    if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
        raise EvalCaseError("%s lacks a lowercase SHA-256" % label)
    return reference, digest


def load_derived_auditor_cases(
    root: os.PathLike[str] | str = ROOT,
) -> list[dict[str, Any]]:
    """Project the 8 x 5 generated auditor contract variants into eval cases."""
    project = _normalize_root(root)
    catalog = load_catalog(project)
    catalog_index = _catalog_index(catalog)
    index_ref = "references/prompt-contracts/index.json"
    index_text, _ = _read_project_text(project, index_ref)
    index_value = _strict_json(index_text, index_ref)
    if not isinstance(index_value, dict) or not isinstance(index_value.get("contracts"), list):
        raise EvalCaseError("%s must contain a contracts array" % index_ref)
    expected_auditors = set(catalog_index["auditors"])
    if index_value.get("contract_count") != len(expected_auditors):
        raise EvalCaseError("%s contract_count does not match the catalog" % index_ref)
    if index_value.get("variant_count") != len(expected_auditors) * 5:
        raise EvalCaseError("%s variant_count does not match the contract" % index_ref)
    source_catalog = index_value.get("source_catalog")
    if not isinstance(source_catalog, dict) or source_catalog.get("path") != (
        "references/system-catalog.json"
    ):
        raise EvalCaseError("%s lacks canonical source_catalog provenance" % index_ref)
    if source_catalog.get("sha256") != _sha256(
        _read_project_bytes(project, "references/system-catalog.json")
    ):
        raise EvalCaseError("%s was generated from a stale system catalog" % index_ref)
    if source_catalog.get("version") != catalog.get("bundle_version"):
        raise EvalCaseError("%s source catalog version is stale" % index_ref)
    framework_catalog = index_value.get("framework_catalog")
    if not isinstance(framework_catalog, dict) or framework_catalog.get("path") != (
        "references/framework-catalog.json"
    ):
        raise EvalCaseError("%s lacks canonical framework_catalog provenance" % index_ref)
    if framework_catalog.get("sha256") != _sha256(
        _read_project_bytes(project, "references/framework-catalog.json")
    ):
        raise EvalCaseError("%s was generated from a stale framework catalog" % index_ref)
    seen_auditors: set[str] = set()
    cases: list[dict[str, Any]] = []
    for position, entry in enumerate(index_value["contracts"], 1):
        label = "%s contracts[%d]" % (index_ref, position - 1)
        if not isinstance(entry, dict):
            raise EvalCaseError("%s must be an object" % label)
        reference, expected_hash = _contract_ref(entry, label)
        raw = _read_project_bytes(project, reference)
        if _sha256(raw) != expected_hash:
            raise EvalCaseError("%s hash does not match %s" % (reference, index_ref))
        try:
            contract_text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise EvalCaseError("%s is not valid UTF-8: %s" % (reference, exc)) from None
        contract = _strict_json(contract_text, reference)
        if not isinstance(contract, dict):
            raise EvalCaseError("%s must be an object" % reference)
        skill_contract = contract.get("skill")
        auditor = contract.get("target_skill")
        if auditor is None and isinstance(skill_contract, dict):
            auditor = skill_contract.get("name")
        if auditor is None:
            auditor = entry.get("target_skill", entry.get("skill"))
        if auditor not in expected_auditors:
            raise EvalCaseError("%s names non-catalog auditor %r" % (reference, auditor))
        indexed_auditor = entry.get("target_skill", entry.get("skill"))
        if indexed_auditor != auditor:
            raise EvalCaseError(
                "%s auditor %r does not match index value %r"
                % (reference, auditor, indexed_auditor)
            )
        if entry.get("evaluation_variant_count") != 5:
            raise EvalCaseError("%s must declare 5 evaluation variants" % label)
        if auditor in seen_auditors:
            raise EvalCaseError("prompt contract index duplicates auditor %s" % auditor)
        seen_auditors.add(auditor)
        variants = contract.get("evaluation_variants")
        if not isinstance(variants, list) or len(variants) != 5:
            raise EvalCaseError("%s must contain exactly 5 evaluation_variants" % reference)
        declared_variant_ids = entry.get("evaluation_variant_ids")
        actual_variant_ids = [variant.get("id") if isinstance(variant, dict) else None for variant in variants]
        if declared_variant_ids != actual_variant_ids:
            raise EvalCaseError("%s variant ids do not match the index" % reference)
        if not isinstance(skill_contract, dict):
            raise EvalCaseError("%s skill provenance must be an object" % reference)
        expected_skill_path = catalog_index["skills"][auditor]["path"]
        if skill_contract.get("path") != expected_skill_path:
            raise EvalCaseError("%s skill path does not match the catalog" % reference)
        skill_hash = _sha256(_read_project_bytes(project, expected_skill_path))
        if skill_contract.get("sha256") != skill_hash or entry.get("skill_sha256") != skill_hash:
            raise EvalCaseError("%s was generated from a stale skill contract" % reference)
        if skill_contract.get("version") != entry.get("skill_version"):
            raise EvalCaseError("%s skill version does not match the index" % reference)
        variant_lines = {
            match.group(1): line_number
            for line_number, line in enumerate(contract_text.splitlines(), 1)
            for match in [re.fullmatch(r'\s*"id":\s*"([a-z0-9-]+)",?\s*', line)]
            if match
        }
        seen_variants: set[str] = set()
        for variant_position, variant in enumerate(variants, 1):
            variant_label = "%s evaluation_variants[%d]" % (reference, variant_position - 1)
            if not isinstance(variant, dict):
                raise EvalCaseError("%s must be an object" % variant_label)
            variant_id = variant.get("id", variant.get("slug"))
            if not isinstance(variant_id, str) or not ID_RE.fullmatch(variant_id):
                raise EvalCaseError("%s has invalid id/slug" % variant_label)
            if variant_id in seen_variants:
                raise EvalCaseError("%s duplicates variant %s" % (reference, variant_id))
            seen_variants.add(variant_id)
            semantic = variant.get("semantic_case")
            if not isinstance(semantic, dict) or set(semantic) != {
                "scenario",
                "input_summary",
                "expected_behavior",
                "failure_modes",
            }:
                raise EvalCaseError("%s has invalid semantic_case fields" % variant_label)
            for field in ("scenario", "input_summary"):
                _validate_string(semantic[field], "%s.%s" % (variant_label, field), 16000)
            for field in ("expected_behavior", "failure_modes"):
                _validate_string_list(semantic[field], "%s.%s" % (variant_label, field))
            value = {
                "id": "derived-%s-%s" % (auditor, variant_id),
                "type": "eval-case",
                "status": "simulated",
                "target_skill": auditor,
                **semantic,
            }
            cases.append(
                _runner_case(
                    value,
                    source_ref=reference,
                    source_line=variant_lines.get(variant_id, 1),
                    source_group="derived-auditor",
                    case_hash_value=variant,
                )
            )
    missing = sorted(expected_auditors - seen_auditors)
    extra = sorted(seen_auditors - expected_auditors)
    if missing or extra:
        raise EvalCaseError(
            "prompt contracts do not match catalog auditors (missing=%s extra=%s)"
            % (missing, extra)
        )
    if len(cases) != len(expected_auditors) * 5:
        raise EvalCaseError("prompt contracts did not produce exactly 5 cases per auditor")
    index_cases(cases)
    return cases


def load_profiles(root: os.PathLike[str] | str = ROOT) -> dict[str, dict[str, Any]]:
    """Load and strictly validate the three behavior selection profiles."""
    project = _normalize_root(root)
    reference = "evals/behavior-profiles.json"
    text, _ = _read_project_text(project, reference)
    value = _strict_json(text, reference)
    if not isinstance(value, dict) or set(value) != {"schema_version", "profiles"}:
        raise EvalCaseError("%s has invalid top-level fields" % reference)
    if value["schema_version"] != "1.0":
        raise EvalCaseError("%s has unsupported schema_version" % reference)
    profiles = value["profiles"]
    if not isinstance(profiles, dict) or set(profiles) != set(PROFILE_NAMES):
        raise EvalCaseError("%s must define exactly %s" % (reference, ", ".join(PROFILE_NAMES)))
    expected_modes = {"smoke": "fixed", "change-aware": "change-aware", "nightly": "all"}
    result: dict[str, dict[str, Any]] = {}
    for name in PROFILE_NAMES:
        profile = profiles[name]
        if not isinstance(profile, dict):
            raise EvalCaseError("profile %s must be an object" % name)
        allowed = {"description", "mode"}
        if name == "smoke":
            allowed.add("case_ids")
        elif name == "change-aware":
            allowed.update({"include_profiles", "impact_map"})
        if set(profile) != allowed:
            raise EvalCaseError("profile %s has invalid fields" % name)
        _validate_string(profile["description"], "profile %s description" % name)
        if profile["mode"] != expected_modes[name]:
            raise EvalCaseError("profile %s has invalid mode" % name)
        if name == "smoke":
            case_ids = _validate_string_list(profile["case_ids"], "smoke.case_ids")
            if len(case_ids) != len(set(case_ids)):
                raise EvalCaseError("smoke.case_ids contains duplicates")
            for case_id in case_ids:
                if not ID_RE.fullmatch(case_id):
                    raise EvalCaseError("smoke.case_ids contains invalid id %r" % case_id)
        elif name == "change-aware":
            if profile["include_profiles"] != ["smoke"]:
                raise EvalCaseError("change-aware must include exactly the smoke profile")
            if profile["impact_map"] != "evals/change-impact.json":
                raise EvalCaseError("change-aware impact_map must use evals/change-impact.json")
        result[name] = dict(profile)
    return result


def _load_impact_map(root: Path) -> dict[str, Any]:
    reference = "evals/change-impact.json"
    text, _ = _read_project_text(root, reference)
    value = _strict_json(text, reference)
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "unmatched_policy",
        "rules",
    }:
        raise EvalCaseError("%s has invalid top-level fields" % reference)
    if value["schema_version"] != "1.1" or value["unmatched_policy"] != "smoke-only":
        raise EvalCaseError("%s has unsupported policy/version" % reference)
    if not isinstance(value["rules"], list) or not value["rules"]:
        raise EvalCaseError("%s rules must be a non-empty list" % reference)
    seen: set[str] = set()
    legal_selectors = {
        "all",
        "source-ref",
        "auto-routing",
        "skill-contract",
        "command-contract",
        "auditors",
        "prompt-contract",
        "reference-consumers",
    }
    for position, rule in enumerate(value["rules"]):
        label = "%s rules[%d]" % (reference, position)
        if not isinstance(rule, dict) or set(rule) != {
            "id",
            "patterns",
            "selector",
            "severity",
        }:
            raise EvalCaseError("%s has invalid fields" % label)
        rule_id = _validate_string(rule["id"], label + ".id")
        if not ID_RE.fullmatch(rule_id) or rule_id in seen:
            raise EvalCaseError("%s has invalid/duplicate id" % label)
        seen.add(rule_id)
        patterns = _validate_string_list(rule["patterns"], label + ".patterns")
        for pattern in patterns:
            if pattern.startswith("/") or ".." in PurePosixPath(pattern).parts:
                raise EvalCaseError("%s has unsafe pattern %r" % (label, pattern))
        if rule["selector"] not in legal_selectors:
            raise EvalCaseError("%s has unknown selector %r" % (label, rule["selector"]))
        if rule["severity"] not in {"S0", "S1", "S2", "S3"}:
            raise EvalCaseError("%s has unknown severity %r" % (label, rule["severity"]))
    return value


def _normalize_changed_paths(changed_paths: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in changed_paths:
        if not isinstance(value, str) or not value or "\x00" in value:
            raise EvalCaseError("changed path must be a non-empty text path")
        path = PurePosixPath(value)
        normalized = path.as_posix()
        if path.is_absolute() or normalized != value or ".." in path.parts or "." in path.parts:
            raise EvalCaseError("changed path is unsafe or non-canonical: %r" % value)
        if normalized not in seen:
            result.append(normalized)
            seen.add(normalized)
    return sorted(result)


def _verify_git_commit(root: Path, reference: str, label: str) -> str:
    if not isinstance(reference, str) or not reference or reference.startswith("-"):
        raise EvalCaseError("%s is not a valid Git reference" % label)
    process = subprocess.run(
        ["git", "rev-parse", "--verify", "--end-of-options", reference + "^{commit}"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    if process.returncode != 0:
        raise EvalCaseError("%s does not resolve to a Git commit: %s" % (label, reference))
    commit = process.stdout.strip()
    if not SHA256_RE.fullmatch(commit) and not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise EvalCaseError("%s resolved to an invalid object id" % label)
    return commit


def changed_paths_from_git(
    root: os.PathLike[str] | str,
    base_ref: str,
    head_ref: str = "HEAD",
) -> list[str]:
    """Resolve two commits and return their canonical changed paths, failing closed."""
    project = _normalize_root(root)
    base = _verify_git_commit(project, base_ref, "base_ref")
    head = _verify_git_commit(project, head_ref, "head_ref")
    process = subprocess.run(
        ["git", "diff", "--name-only", "-z", "--diff-filter=ACMRDT", base, head, "--"],
        cwd=project,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        raise EvalCaseError("git diff failed while selecting change-aware cases")
    try:
        values = process.stdout.decode("utf-8").split("\x00")
    except UnicodeDecodeError as exc:
        raise EvalCaseError("git diff emitted a non-UTF-8 path: %s" % exc) from None
    return _normalize_changed_paths(value for value in values if value)


def _case_discipline(case: Mapping[str, Any], catalog_index: Mapping[str, Any]) -> str:
    return catalog_index["skills"][case["target_skill"]]["discipline"]


def _skill_for_path(path: str, catalog_index: Mapping[str, Any]) -> str | None:
    for slug, spec in catalog_index["skills"].items():
        if path == spec["path"]:
            return slug
    return None


def _command_for_path(path: str, catalog_index: Mapping[str, Any]) -> str | None:
    if not path.startswith("commands/") or not path.endswith(".md"):
        return None
    command = path[len("commands/") : -len(".md")]
    return command if command in catalog_index["commands"] else None


def _reference_consumers(root: Path, path: str, catalog_index: Mapping[str, Any]) -> set[str]:
    consumers: set[str] = set()
    probes = {path, "../../" + path, "../" + path, PurePosixPath(path).name}
    for slug, spec in catalog_index["skills"].items():
        try:
            text, _ = _read_project_text(root, spec["path"])
        except EvalCaseError:
            continue
        if any(probe in text for probe in probes):
            consumers.add(slug)
    return consumers


def _select_for_rule(
    *,
    selector: str,
    path: str,
    cases: Sequence[Mapping[str, Any]],
    catalog_index: Mapping[str, Any],
    root: Path,
) -> list[str]:
    if selector == "all":
        return [case["id"] for case in cases]
    if selector == "source-ref":
        return [case["id"] for case in cases if case["source_ref"] == path]
    if selector == "auto-routing":
        return [case["id"] for case in cases if case["source_group"] == "auto-routing"]
    if selector == "skill-contract":
        skill = _skill_for_path(path, catalog_index)
        return [case["id"] for case in cases if skill and case["target_skill"] == skill]
    if selector == "command-contract":
        command = _command_for_path(path, catalog_index)
        if command == "auto":
            return [case["id"] for case in cases]
        discipline = catalog_index["commands"].get(command)
        return [
            case["id"]
            for case in cases
            if discipline and _case_discipline(case, catalog_index) == discipline
        ]
    if selector == "auditors":
        auditors = set(catalog_index["auditors"])
        return [case["id"] for case in cases if case["target_skill"] in auditors]
    if selector == "prompt-contract":
        auditors = set(catalog_index["auditors"])
        if path.endswith("/index.json") or not path.startswith("references/prompt-contracts/"):
            return [case["id"] for case in cases if case["target_skill"] in auditors]
        stem = PurePosixPath(path).stem
        return [
            case["id"]
            for case in cases
            if stem in auditors and case["target_skill"] == stem
        ]
    if selector == "reference-consumers":
        consumers = _reference_consumers(root, path, catalog_index)
        return [case["id"] for case in cases if case["target_skill"] in consumers]
    raise EvalCaseError("unsupported change-impact selector %r" % selector)


def select_cases(
    root: os.PathLike[str] | str = ROOT,
    profile: str = "smoke",
    *,
    cases: Sequence[Mapping[str, Any]] | None = None,
    derived_cases: Sequence[Mapping[str, Any]] | None = None,
    base_ref: str | None = None,
    head_ref: str = "HEAD",
    changed_paths: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Select one deterministic profile and return cases plus stable reasons.

    ``changed_paths`` is an explicit, testable alternative to Git discovery.
    When it is omitted for ``change-aware``, ``base_ref`` is mandatory and both
    refs must resolve to commits. Selection is a set union and is never capped.
    """
    project = _normalize_root(root)
    profiles = load_profiles(project)
    if profile not in profiles:
        raise EvalCaseError("unknown behavior profile %r" % profile)
    base_cases = [dict(case) for case in (cases if cases is not None else load_cases(project))]
    if derived_cases is None:
        derived = load_derived_auditor_cases(project)
    else:
        derived = [dict(case) for case in derived_cases]
    all_cases = base_cases + derived
    by_id = index_cases(all_cases)
    catalog_index = _catalog_index(load_catalog(project))
    unknown_targets = sorted(
        {case["target_skill"] for case in all_cases} - set(catalog_index["skills"])
    )
    if unknown_targets:
        raise EvalCaseError("cases name unknown target skills: %s" % ", ".join(unknown_targets))

    selected: set[str] = set()
    selection_order: list[str] = []
    reasons: dict[str, list[str]] = {}

    def add(case_id: str, reason: str) -> None:
        if case_id not in by_id:
            raise EvalCaseError("profile %s names missing case %r" % (profile, case_id))
        if case_id not in selected:
            selected.add(case_id)
            selection_order.append(case_id)
        reasons.setdefault(case_id, [])
        if reason not in reasons[case_id]:
            reasons[case_id].append(reason)

    changed: list[str] = []
    unmatched: list[str] = []
    if profile in {"smoke", "change-aware"}:
        for case_id in profiles["smoke"]["case_ids"]:
            add(case_id, "profile:smoke-fixed")
    if profile == "nightly":
        for case_id in by_id:
            add(case_id, "profile:nightly-all")
    elif profile == "change-aware":
        if changed_paths is None:
            if base_ref is None:
                raise EvalCaseError("change-aware selection requires changed_paths or base_ref")
            changed = changed_paths_from_git(project, base_ref, head_ref)
        else:
            changed = _normalize_changed_paths(changed_paths)
        impact = _load_impact_map(project)
        for path in changed:
            matched = False
            selected_by_path = False
            for rule in impact["rules"]:
                if not any(fnmatch.fnmatchcase(path, pattern) for pattern in rule["patterns"]):
                    continue
                matched = True
                case_ids = _select_for_rule(
                    selector=rule["selector"],
                    path=path,
                    cases=all_cases,
                    catalog_index=catalog_index,
                    root=project,
                )
                for case_id in case_ids:
                    # Adapter v2 reasons are safe IDs, not paths.  Keep the
                    # human-readable path in provenance and bind this reason to
                    # it with a full digest (no lossy/truncated path token).
                    path_digest = _sha256(path.encode("utf-8"))
                    add(case_id, "change:%s:%s" % (rule["id"], path_digest))
                    selected_by_path = True
            if not matched or not selected_by_path:
                unmatched.append(path)

    ordered_ids = selection_order
    return {
        "profile": profile,
        "cases": [by_id[case_id] for case_id in ordered_ids],
        "case_ids": ordered_ids,
        "selection_reasons": {
            case_id: sorted(reasons[case_id]) for case_id in ordered_ids
        },
        "provenance": {
            "profile_ref": "evals/behavior-profiles.json",
            "profile_sha256": _sha256(
                _read_project_bytes(project, "evals/behavior-profiles.json")
            ),
            "change_impact_ref": (
                "evals/change-impact.json" if profile == "change-aware" else None
            ),
            "changed_paths": changed,
            "unmatched_paths": sorted(unmatched),
            "selected_count": len(ordered_ids),
            "available_count": len(all_cases),
        },
    }


__all__ = [
    "AUTO_CASE_FIELDS",
    "BASE_CASE_FIELDS",
    "EvalCaseError",
    "RUNNER_CASE_FIELDS",
    "changed_paths_from_git",
    "index_cases",
    "load_cases",
    "load_catalog",
    "load_derived_auditor_cases",
    "load_profiles",
    "parse_flow_object",
    "select_cases",
]
