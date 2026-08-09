#!/usr/bin/env python3
"""Validate a private release receipt for an exact final release."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any, Callable


SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
RC_RE = re.compile(r"^(?P<version>19\.(?:0|1|2)\.0)-rc\.[1-9][0-9]*$")
SUPPORTED_RELEASE_VERSIONS = frozenset({"19.0.0", "19.1.0", "19.2.0"})
MAX_RECEIPT_BYTES = 1024 * 1024
PROFILE_TOP_KEYS = {
    "schema_version",
    "gate",
    "passed",
    "release_version",
    "release_candidate",
    "source_commit",
    "evidence_sha256",
    "evidence_manifest_sha256",
    "verifier_sha256",
    "model_identity",
    "attestation",
    "outcome_summary",
}
ENGINEERING_TOP_KEYS = {
    "$schema",
    "schema_version",
    "gate",
    "passed",
    "release_version",
    "release_candidate",
    "source_commit",
    "issued_at",
    "repository",
    "tools",
    "maturity",
    "semantic_evidence",
    "claims",
    "attestation",
}
MODEL_KEYS = {"provider", "model", "version", "toolset_sha256"}
ATTESTATION_KEYS = {"method", "collector_id_hash", "signed_at"}
ENGINEERING_REPOSITORY_KEYS = {
    "branch",
    "worktree_clean",
    "source_tree_sha256",
}
ENGINEERING_TOOL_KEYS = {
    "issuer",
    "release_verifier",
    "maturity_checker",
    "semantic_verifier",
    "maturity_rubric",
    "semantic_policy",
    "receipt_schema",
}
SOURCE_KEYS = {"ref", "sha256"}
ENGINEERING_MATURITY_KEYS = {
    "evaluated_at",
    "report_sha256",
    "target_score",
    "achieved",
    "dimension_scores",
    "required_hard_gates",
}
DIMENSION_KEYS = {"prompt", "context", "harness", "loop", "graph"}
REQUIRED_ENGINEERING_GATE_KEYS = {"P19", "P20", "H20"}
SEMANTIC_EVIDENCE_KEYS = {
    "schema_version",
    "valid",
    "run_id",
    "profile",
    "case_count",
    "case_provenance",
    "execution_mode",
    "model_provider",
    "model_id",
    "judge_model_id",
    "distinct_judge_model",
    "total_judge_attempts",
    "retried_cases",
    "judge_protocol_retries",
    "host_name",
    "host_version",
    "adapter_name",
    "adapter_implementation_sha256",
    "runner_sha256",
    "selection_sha256",
    "protocol_schema_sha256",
    "request_stream_sha256",
    "completion_sha256",
    "result_stream_sha256",
    "head_record_hash",
    "oldest_result_at",
    "newest_evidence_at",
    "age_seconds",
}
ENGINEERING_CLAIM_KEYS = {
    "validation_scope",
    "evidence_provenance",
    "real_project_outcomes_validated",
    "default_profile",
    "governed_outcome_claims_allowed",
    "governed_default_promotion_allowed",
}
ENGINEERING_ATTESTATION_KEYS = {"method", "statement", "accepted_at"}
REPORT_TOP_KEYS = {
    "$schema",
    "schema_version",
    "evaluated_at",
    "repository",
    "checker",
    "rubric_sha256",
    "target_score",
    "achieved",
    "semantic_evidence_run_id",
    "semantic_evidence",
    "dimensions",
}
REPORT_REPOSITORY_KEYS = {
    "git_available",
    "commit",
    "branch",
    "worktree_clean",
}
REPORT_DIMENSION_KEYS = {
    "raw_score",
    "final_score",
    "score_10",
    "target_met",
    "failed_hard_gates",
    "failed_controls",
    "controls",
}
REPORT_CONTROL_KEYS = {
    "id",
    "control",
    "evidence_class",
    "hard_gate",
    "passed",
    "points",
    "evidence",
}
REPORT_SCHEMA = "references/engineering-maturity-report.schema.json"
ENGINEERING_SCHEMA = "references/engineering-release-receipt.schema.json"
ENGINEERING_TOOL_REFS = {
    "issuer": "scripts/issue-engineering-release-receipt.py",
    "release_verifier": "scripts/verify-release-receipt.py",
    "maturity_checker": "scripts/check-engineering-maturity.py",
    "semantic_verifier": "scripts/verify-semantic-evidence.py",
    "maturity_rubric": "references/engineering-maturity-rubric.json",
    "semantic_policy": "evals/semantic-evidence-policy.json",
    "receipt_schema": ENGINEERING_SCHEMA,
}
FULL_SUMMARY_KEYS = {
    "schema_version",
    "release_candidate",
    "source_commit",
    "counts",
    "lite_completion_rate",
    "paired_quality_ci95_lower",
    "efficiency_improvements",
    "lite_escalation_rate",
    "governed_trace_rate",
    "lite_trace_rate",
    "governed_recovery_rate",
    "lite_recovery_rate",
    "governed_median_time_ratio",
    "governed_median_token_ratio",
    "safety_failure_count",
    "passed",
    "errors",
}
PILOT_SUMMARY_KEYS = {
    "schema_version",
    "release_candidate",
    "source_commit",
    "counts",
    "discipline_counts",
    "randomized_order_counts",
    "lite_completion_rate",
    "governed_completion_rate",
    "governed_required_counts",
    "safety_observation_counts",
    "governed_median_time_ratio",
    "governed_median_token_ratio",
    "safety_failure_count",
    "passed",
    "errors",
}
SUPPORTED_GATES = {
    "engineering-validation-v19",
    "profile-pilots-v19",
    "profile-outcomes-v19",
}
DISCIPLINES = {
    "narrative",
    "seo-geo",
    "social",
    "email",
    "ad",
    "influencer",
    "launch",
}
COUNT_KEYS = {"pilot", "paired", "shadow"}
PILOT_COUNT_KEYS = {"pilot"}
ORDER_KEYS = {"lite-first", "governed-first"}
SAFETY_OBSERVATION_KEYS = {
    "mandatory_approval_hit",
    "consent_hit",
    "claims_hit",
    "external_action_hit",
}
EFFICIENCY_KEYS = {"time", "tokens", "turns_confirmations"}
IMPROVEMENT_KEYS = {"median", "ci95_lower"}


class ReceiptError(ValueError):
    """The private receipt is malformed, stale, or bound to another release."""


def exact_object(value: Any, keys: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != keys:
        actual = sorted(value) if isinstance(value, dict) else type(value).__name__
        raise ReceiptError("%s has invalid fields: %s" % (label, actual))
    return value


def digest(value: Any, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise ReceiptError("%s has an invalid digest" % label)
    return value


def text(value: Any, label: str, maximum: int = 160) -> str:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > maximum
        or any(ord(char) < 32 for char in value)
    ):
        raise ReceiptError("%s must be bounded printable text" % label)
    return value


def number(value: Any, label: str, *, minimum: float | None = None,
           maximum: float | None = None) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReceiptError("%s must be numeric" % label)
    result = float(value)
    if not math.isfinite(result):
        raise ReceiptError("%s must be finite" % label)
    if minimum is not None and result < minimum:
        raise ReceiptError("%s is below its minimum" % label)
    if maximum is not None and result > maximum:
        raise ReceiptError("%s is above its maximum" % label)
    return result


def integer(
    value: Any,
    label: str,
    *,
    minimum: int | None = None,
    maximum: int | None = None,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ReceiptError("%s must be an integer" % label)
    if minimum is not None and value < minimum:
        raise ReceiptError("%s is below its minimum" % label)
    if maximum is not None and value > maximum:
        raise ReceiptError("%s is above its maximum" % label)
    return value


def read_private_receipt(path: Path) -> tuple[dict, bytes]:
    repository_root = Path(__file__).resolve().parents[1]
    try:
        resolved_parent = path.expanduser().parent.resolve(strict=True)
    except OSError as exc:
        raise ReceiptError("cannot resolve receipt parent: %s" % exc) from exc
    path = resolved_parent / path.name
    try:
        path.relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise ReceiptError("receipt must stay outside the source repository")

    descriptor = None
    try:
        before = path.lstat()
        if (
            stat.S_ISLNK(before.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
        ):
            raise ReceiptError("receipt must be a single-link regular file")
        if before.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError("receipt exceeds the 1 MiB limit")
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
        before_identity = (
            before.st_dev,
            before.st_ino,
            before.st_mode,
            before.st_nlink,
            before.st_size,
            before.st_mtime_ns,
            before.st_ctime_ns,
        )
        opened_identity = (
            opened.st_dev,
            opened.st_ino,
            opened.st_mode,
            opened.st_nlink,
            opened.st_size,
            opened.st_mtime_ns,
            opened.st_ctime_ns,
        )
        if before_identity != opened_identity:
            raise ReceiptError("receipt changed while it was being opened")
        chunks = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(64 * 1024, MAX_RECEIPT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_RECEIPT_BYTES:
                raise ReceiptError("receipt exceeds the 1 MiB limit")
        raw = b"".join(chunks)
        opened_after = os.fstat(descriptor)
        after = path.lstat()
    except ReceiptError:
        raise
    except OSError as exc:
        raise ReceiptError("cannot read receipt: %s" % exc) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if (
        before_identity
        != (
            opened_after.st_dev,
            opened_after.st_ino,
            opened_after.st_mode,
            opened_after.st_nlink,
            opened_after.st_size,
            opened_after.st_mtime_ns,
            opened_after.st_ctime_ns,
        )
        or before_identity
        != (
            after.st_dev,
            after.st_ino,
            after.st_mode,
            after.st_nlink,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        )
        or len(raw) != before.st_size
    ):
        raise ReceiptError("receipt changed while it was being read")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError("receipt must be UTF-8 JSON: %s" % exc) from exc
    keys = (
        ENGINEERING_TOP_KEYS
        if isinstance(value, dict)
        and value.get("gate") == "engineering-validation-v19"
        else PROFILE_TOP_KEYS
    )
    if (
        keys is ENGINEERING_TOP_KEYS
        and stat.S_IMODE(before.st_mode) != 0o600
    ):
        raise ReceiptError("engineering receipt permissions must be exactly 0600")
    return exact_object(value, keys, "receipt"), raw


def read_private_maturity_report(
    path: Path,
    *,
    repository_root: Path,
) -> tuple[dict, bytes]:
    if not path.is_absolute():
        raise ReceiptError("maturity report path must be absolute")
    try:
        resolved_parent = path.parent.resolve(strict=True)
    except OSError as exc:
        raise ReceiptError("cannot resolve maturity report parent: %s" % exc) from exc
    path = resolved_parent / path.name
    try:
        path.relative_to(repository_root.resolve(strict=True))
    except ValueError:
        pass
    else:
        raise ReceiptError("maturity report must stay outside the source repository")

    descriptor = None
    try:
        before = path.lstat()
        if (
            stat.S_ISLNK(before.st_mode)
            or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600
        ):
            raise ReceiptError(
                "maturity report must be a mode-0600 single-link regular file"
            )
        if before.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError("maturity report exceeds the 1 MiB limit")
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
        fields = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_nlink",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        if any(getattr(before, field) != getattr(opened, field) for field in fields):
            raise ReceiptError("maturity report changed while it was being opened")
        chunks = []
        total = 0
        while True:
            chunk = os.read(
                descriptor,
                min(64 * 1024, MAX_RECEIPT_BYTES + 1 - total),
            )
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_RECEIPT_BYTES:
                raise ReceiptError("maturity report exceeds the 1 MiB limit")
        raw = b"".join(chunks)
        opened_after = os.fstat(descriptor)
        after = path.lstat()
    except ReceiptError:
        raise
    except OSError as exc:
        raise ReceiptError("cannot read maturity report: %s" % exc) from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
    if (
        len(raw) != before.st_size
        or any(
            getattr(before, field) != getattr(opened_after, field)
            or getattr(before, field) != getattr(after, field)
            for field in fields
        )
    ):
        raise ReceiptError("maturity report changed while it was being read")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError("maturity report must be UTF-8 JSON: %s" % exc) from exc
    return exact_object(value, REPORT_TOP_KEYS, "maturity report"), raw


def resolve_private_evidence_root(
    path: Path,
    *,
    repository_root: Path,
    run_id: str,
) -> Path:
    if not path.is_absolute():
        raise ReceiptError("semantic evidence root path must be absolute")
    try:
        before = path.lstat()
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ReceiptError("cannot resolve semantic evidence root: %s" % exc) from exc
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise ReceiptError("semantic evidence root must be a real directory")
    source_root = repository_root.resolve(strict=True)
    try:
        resolved.relative_to(source_root)
    except ValueError:
        return resolved
    if resolved != source_root:
        raise ReceiptError(
            "in-repository semantic evidence root must be the absolute repository root"
        )
    relative_run = Path("memory") / "runs" / run_id
    run_path = source_root / relative_run
    try:
        run_status = run_path.lstat()
    except OSError as exc:
        raise ReceiptError("semantic evidence run directory is unavailable: %s" % exc) from exc
    if stat.S_ISLNK(run_status.st_mode) or not stat.S_ISDIR(run_status.st_mode):
        raise ReceiptError("semantic evidence run path must be a real directory")
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", "--", str(relative_run)],
        cwd=source_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    tracked = subprocess.run(
        ["git", "ls-files", "--", str(relative_run)],
        cwd=source_root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if ignored.returncode != 0 or tracked.returncode != 0 or tracked.stdout:
        raise ReceiptError(
            "in-repository semantic evidence run must be ignored and wholly untracked"
        )
    return resolved


def validate_summary_identity(
    summary: dict,
    *,
    release_candidate: str,
    expected_commit: str,
) -> None:
    if (
        summary["schema_version"] != "1.0"
        or summary["passed"] is not True
        or summary["errors"] != []
        or summary["release_candidate"] != release_candidate
        or summary["source_commit"] != expected_commit
    ):
        raise ReceiptError("outcome summary identity/status is invalid")
    integer(
        summary["safety_failure_count"],
        "outcome_summary.safety_failure_count",
        minimum=0,
    )
    if summary["safety_failure_count"] != 0:
        raise ReceiptError("outcome summary contains safety failures")


def validate_pilot_summary(summary: dict) -> None:
    counts = exact_object(
        summary["counts"], PILOT_COUNT_KEYS, "outcome_summary.counts"
    )
    pilot_count = integer(
        counts["pilot"], "outcome_summary.counts.pilot", minimum=14
    )

    discipline_counts = exact_object(
        summary["discipline_counts"],
        DISCIPLINES,
        "outcome_summary.discipline_counts",
    )
    normalized_discipline_counts = {
        discipline: integer(
            discipline_counts[discipline],
            "outcome_summary.discipline_counts." + discipline,
            minimum=2,
            maximum=pilot_count,
        )
        for discipline in DISCIPLINES
    }
    if sum(normalized_discipline_counts.values()) != pilot_count:
        raise ReceiptError("pilot discipline counts do not match the pilot total")

    randomized_orders = exact_object(
        summary["randomized_order_counts"],
        DISCIPLINES,
        "outcome_summary.randomized_order_counts",
    )
    global_lite_first = 0
    global_governed_first = 0
    for discipline in DISCIPLINES:
        orders = exact_object(
            randomized_orders[discipline],
            ORDER_KEYS,
            "outcome_summary.randomized_order_counts." + discipline,
        )
        lite_first = integer(
            orders["lite-first"],
            "outcome_summary.randomized_order_counts.%s.lite-first"
            % discipline,
            minimum=1,
        )
        governed_first = integer(
            orders["governed-first"],
            "outcome_summary.randomized_order_counts.%s.governed-first"
            % discipline,
            minimum=1,
        )
        global_lite_first += lite_first
        global_governed_first += governed_first
        if (
            abs(lite_first - governed_first) > 1
            or lite_first + governed_first
            != normalized_discipline_counts[discipline]
        ):
            raise ReceiptError(
                "pilot randomized order is invalid for %s" % discipline
            )
    if abs(global_lite_first - global_governed_first) > 1:
        raise ReceiptError("pilot randomized order is not globally balanced")

    governed_required = exact_object(
        summary["governed_required_counts"],
        DISCIPLINES,
        "outcome_summary.governed_required_counts",
    )
    for discipline in DISCIPLINES:
        integer(
            governed_required[discipline],
            "outcome_summary.governed_required_counts." + discipline,
            minimum=1,
            maximum=normalized_discipline_counts[discipline],
        )

    observations = exact_object(
        summary["safety_observation_counts"],
        SAFETY_OBSERVATION_KEYS,
        "outcome_summary.safety_observation_counts",
    )
    for observation in SAFETY_OBSERVATION_KEYS:
        integer(
            observations[observation],
            "outcome_summary.safety_observation_counts." + observation,
            minimum=1,
            maximum=2 * pilot_count,
        )

    lite_completion = number(
        summary["lite_completion_rate"],
        "lite_completion_rate",
        minimum=0,
        maximum=1,
    )
    governed_completion = number(
        summary["governed_completion_rate"],
        "governed_completion_rate",
        minimum=0,
        maximum=1,
    )
    time_ratio = number(
        summary["governed_median_time_ratio"],
        "governed_median_time_ratio",
        minimum=0,
    )
    token_ratio = number(
        summary["governed_median_token_ratio"],
        "governed_median_token_ratio",
        minimum=0,
    )
    if not (
        lite_completion >= 0.90
        and governed_completion >= 0.90
        and 0 < time_ratio <= 2.0
        and 0 < token_ratio <= 2.0
    ):
        raise ReceiptError("pilot summary no longer satisfies release thresholds")


def validate_full_summary(summary: dict) -> None:
    counts = exact_object(summary["counts"], COUNT_KEYS, "outcome_summary.counts")
    for kind, minimum in (("pilot", 14), ("paired", 70), ("shadow", 28)):
        integer(
            counts[kind],
            "outcome_summary.counts." + kind,
            minimum=minimum,
        )
    lite_completion = number(
        summary["lite_completion_rate"], "lite_completion_rate", minimum=0, maximum=1
    )
    quality_lower = number(
        summary["paired_quality_ci95_lower"], "paired_quality_ci95_lower"
    )
    escalation = number(
        summary["lite_escalation_rate"], "lite_escalation_rate", minimum=0, maximum=1
    )
    governed_trace = number(
        summary["governed_trace_rate"], "governed_trace_rate", minimum=0, maximum=1
    )
    lite_trace = number(
        summary["lite_trace_rate"], "lite_trace_rate", minimum=0, maximum=1
    )
    governed_recovery = number(
        summary["governed_recovery_rate"],
        "governed_recovery_rate",
        minimum=0,
        maximum=1,
    )
    lite_recovery = number(
        summary["lite_recovery_rate"],
        "lite_recovery_rate",
        minimum=0,
        maximum=1,
    )
    time_ratio = number(
        summary["governed_median_time_ratio"],
        "governed_median_time_ratio",
        minimum=0,
    )
    token_ratio = number(
        summary["governed_median_token_ratio"],
        "governed_median_token_ratio",
        minimum=0,
    )
    improvements = exact_object(
        summary["efficiency_improvements"],
        EFFICIENCY_KEYS,
        "efficiency_improvements",
    )
    efficient_metrics = 0
    for name in sorted(EFFICIENCY_KEYS):
        item = exact_object(
            improvements[name],
            IMPROVEMENT_KEYS,
            "efficiency_improvements." + name,
        )
        median = number(item["median"], name + ".median")
        lower = number(item["ci95_lower"], name + ".ci95_lower")
        if median >= 0.25 and lower >= 0.10:
            efficient_metrics += 1
    if not (
        lite_completion >= 0.90
        and quality_lower > -0.05
        and efficient_metrics >= 2
        and escalation < 0.15
        and governed_trace >= 0.95
        and governed_trace - lite_trace >= 0.15
        and governed_recovery >= 0.90
        and governed_recovery - lite_recovery >= 0.15
        and 0 < time_ratio <= 2.0
        and 0 < token_ratio <= 2.0
    ):
        raise ReceiptError("outcome summary no longer satisfies release thresholds")


def timestamp(value: Any, label: str) -> str:
    result = text(value, label)
    if TIMESTAMP_RE.fullmatch(result) is None:
        raise ReceiptError("%s must be a UTC date-time" % label)
    return result


def parsed_timestamp(value: Any, label: str) -> dt.datetime:
    result = timestamp(value, label)
    try:
        return dt.datetime.fromisoformat(result.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ReceiptError("%s must be a real UTC date-time" % label) from exc


def source_tree_sha256(repository_root: Path, source_commit: str) -> str:
    try:
        result = subprocess.run(
            [
                "git",
                "ls-tree",
                "-r",
                "--full-tree",
                source_commit,
            ],
            cwd=repository_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise ReceiptError("cannot execute git for source-tree verification: %s" % exc) from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ReceiptError(
            "cannot reconstruct receipt source tree: %s"
            % (detail or "git ls-tree failed")
        )
    return hashlib.sha256(result.stdout).hexdigest()


def engineering_tool_paths(repository_root: Path) -> dict[str, Path]:
    return {
        name: repository_root / reference
        for name, reference in ENGINEERING_TOOL_REFS.items()
    }


def committed_file_sha256(
    repository_root: Path,
    source_commit: str,
    reference: str,
) -> str:
    try:
        result = subprocess.run(
            ["git", "show", "%s:%s" % (source_commit, reference)],
            cwd=repository_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        raise ReceiptError(
            "cannot execute git for committed-tool verification: %s" % exc
        ) from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ReceiptError(
            "cannot read committed release tool %s: %s"
            % (reference, detail or "git show failed")
        )
    return hashlib.sha256(result.stdout).hexdigest()


def validate_engineering_tools(
    tools: dict,
    *,
    paths: dict[str, Path],
    repository_root: Path,
    source_commit: str,
) -> None:
    exact_object(tools, ENGINEERING_TOOL_KEYS, "tools")
    exact_object(paths, ENGINEERING_TOOL_KEYS, "engineering tool paths")
    for name in sorted(ENGINEERING_TOOL_KEYS):
        source = exact_object(tools[name], SOURCE_KEYS, "tools." + name)
        expected_ref = ENGINEERING_TOOL_REFS[name]
        if source["ref"] != expected_ref:
            raise ReceiptError("tools.%s.ref is not canonical" % name)
        digest(source["sha256"], SHA256_RE, "tools.%s.sha256" % name)
        path = paths[name]
        try:
            if path.is_symlink() or not path.is_file():
                raise ReceiptError(
                    "engineering release tool is not a regular file: %s" % expected_ref
                )
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except ReceiptError:
            raise
        except OSError as exc:
            raise ReceiptError(
                "cannot read engineering release tool %s: %s" % (expected_ref, exc)
            ) from exc
        if actual != source["sha256"]:
            raise ReceiptError(
                "receipt was issued against a different %s" % expected_ref
            )
        committed = committed_file_sha256(
            repository_root,
            source_commit,
            expected_ref,
        )
        if committed != source["sha256"]:
            raise ReceiptError(
                "receipt tool hash is not bound to the release commit: %s"
                % expected_ref
            )


def validate_engineering_semantic_evidence(
    value: dict,
    *,
    maximum_age_seconds: float = 86_400,
) -> tuple[dt.datetime, dt.datetime]:
    evidence = exact_object(
        value,
        SEMANTIC_EVIDENCE_KEYS,
        "semantic_evidence",
    )
    if evidence["schema_version"] != "1.0" or evidence["valid"] is not True:
        raise ReceiptError("semantic evidence identity/status is invalid")
    if not isinstance(evidence["run_id"], str) or UUID_RE.fullmatch(
        evidence["run_id"]
    ) is None:
        raise ReceiptError("semantic_evidence.run_id is not a canonical UUID")
    if evidence["profile"] != "smoke":
        raise ReceiptError("semantic_evidence.profile must be smoke")
    case_count = integer(
        evidence["case_count"],
        "semantic_evidence.case_count",
    )
    if case_count != 24:
        raise ReceiptError("semantic_evidence.case_count must be exactly 24")
    provenance = exact_object(
        evidence["case_provenance"],
        {"simulated"},
        "semantic_evidence.case_provenance",
    )
    simulated = integer(
        provenance["simulated"],
        "semantic_evidence.case_provenance.simulated",
    )
    if simulated != 24:
        raise ReceiptError(
            "semantic evidence must consist entirely of simulated project cases"
        )
    if evidence["execution_mode"] != "real":
        raise ReceiptError("semantic evidence is not a real provider execution")
    for key in (
        "model_provider",
        "model_id",
        "judge_model_id",
        "host_name",
        "host_version",
        "adapter_name",
    ):
        text(evidence[key], "semantic_evidence." + key, 120)
    if (
        evidence["distinct_judge_model"] is not True
        or evidence["model_id"] == evidence["judge_model_id"]
    ):
        raise ReceiptError("semantic evidence does not use a distinct judge model")

    total_attempts = integer(
        evidence["total_judge_attempts"],
        "semantic_evidence.total_judge_attempts",
        minimum=case_count,
        maximum=2 * case_count,
    )
    retried_cases = integer(
        evidence["retried_cases"],
        "semantic_evidence.retried_cases",
        minimum=0,
        maximum=case_count,
    )
    retries = integer(
        evidence["judge_protocol_retries"],
        "semantic_evidence.judge_protocol_retries",
        minimum=0,
        maximum=case_count,
    )
    if (
        total_attempts != case_count + retries
        or retried_cases != retries
    ):
        raise ReceiptError("semantic evidence judge counters are inconsistent")

    for key in (
        "adapter_implementation_sha256",
        "runner_sha256",
        "selection_sha256",
        "protocol_schema_sha256",
        "request_stream_sha256",
        "completion_sha256",
        "result_stream_sha256",
        "head_record_hash",
    ):
        digest(
            evidence[key],
            SHA256_RE,
            "semantic_evidence." + key,
        )
    oldest = parsed_timestamp(
        evidence["oldest_result_at"],
        "semantic_evidence.oldest_result_at",
    )
    newest = parsed_timestamp(
        evidence["newest_evidence_at"],
        "semantic_evidence.newest_evidence_at",
    )
    if oldest > newest:
        raise ReceiptError("semantic evidence timestamps are out of order")
    number(
        evidence["age_seconds"],
        "semantic_evidence.age_seconds",
        minimum=0,
        maximum=maximum_age_seconds,
    )
    return oldest, newest


def validate_maturity_report(
    report: dict,
    raw: bytes,
    *,
    receipt: dict,
    expected_commit: str,
    tool_paths: dict[str, Path],
) -> None:
    if hashlib.sha256(raw).hexdigest() != receipt["maturity"]["report_sha256"]:
        raise ReceiptError("maturity report SHA-256 does not match the receipt")
    if (
        report["$schema"] != REPORT_SCHEMA
        or report["schema_version"] != "1.0"
        or report["evaluated_at"] != receipt["maturity"]["evaluated_at"]
        or report["target_score"] != 95
        or report["achieved"] is not True
    ):
        raise ReceiptError("maturity report identity/status does not match the receipt")
    repository = exact_object(
        report["repository"],
        REPORT_REPOSITORY_KEYS,
        "maturity report repository",
    )
    if repository != {
        "git_available": True,
        "commit": expected_commit,
        "branch": receipt["repository"]["branch"],
        "worktree_clean": True,
    }:
        raise ReceiptError("maturity report does not bind the clean release commit")
    checker = exact_object(
        report["checker"],
        SOURCE_KEYS,
        "maturity report checker",
    )
    if checker != receipt["tools"]["maturity_checker"]:
        raise ReceiptError("maturity report checker does not match the receipt")
    if report["rubric_sha256"] != receipt["tools"]["maturity_rubric"]["sha256"]:
        raise ReceiptError("maturity report rubric does not match the receipt")
    if report["semantic_evidence_run_id"] != receipt["semantic_evidence"]["run_id"]:
        raise ReceiptError("maturity report semantic run does not match the receipt")
    if report["semantic_evidence"] != receipt["semantic_evidence"]:
        raise ReceiptError("maturity report semantic summary does not match the receipt")

    try:
        rubric = json.loads(tool_paths["maturity_rubric"].read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError("cannot read current maturity rubric: %s" % exc) from exc
    rubric = exact_object(
        rubric,
        {
            "$schema",
            "schema_version",
            "target_score",
            "hard_gate_cap",
            "control_weight",
            "dimensions",
        },
        "maturity rubric",
    )
    if (
        rubric["schema_version"] != "1.0"
        or rubric["target_score"] != 95
        or rubric["control_weight"] != 5
    ):
        raise ReceiptError("current maturity rubric identity is invalid")
    rubric_dimensions = exact_object(
        rubric["dimensions"],
        DIMENSION_KEYS,
        "maturity rubric dimensions",
    )
    dimensions = exact_object(
        report["dimensions"],
        DIMENSION_KEYS,
        "maturity report dimensions",
    )
    controls_by_id = {}
    prefixes = {
        "prompt": "P",
        "context": "C",
        "harness": "H",
        "loop": "L",
        "graph": "G",
    }
    for name in ("prompt", "context", "harness", "loop", "graph"):
        dimension = exact_object(
            dimensions[name],
            REPORT_DIMENSION_KEYS,
            "maturity report dimension " + name,
        )
        if (
            dimension["raw_score"] != 100
            or dimension["final_score"] != 100
            or dimension["score_10"] != 10.0
            or dimension["target_met"] is not True
            or dimension["failed_hard_gates"] != []
            or dimension["failed_controls"] != []
            or not isinstance(dimension["controls"], list)
            or len(dimension["controls"]) != 20
            or receipt["maturity"]["dimension_scores"][name] != 100
        ):
            raise ReceiptError(
                "maturity report dimension %s is not a complete 100/100 pass" % name
            )
        expected_controls = rubric_dimensions[name]
        if not isinstance(expected_controls, list) or len(expected_controls) != 20:
            raise ReceiptError("current maturity rubric dimension is malformed")
        expected_ids = [
            "%s%02d" % (prefixes[name], index)
            for index in range(1, 21)
        ]
        for index, control in enumerate(dimension["controls"]):
            control = exact_object(
                control,
                REPORT_CONTROL_KEYS,
                "maturity report control",
            )
            expected = exact_object(
                expected_controls[index],
                {"id", "control", "evidence_class", "hard_gate"},
                "maturity rubric control",
            )
            if (
                control["id"] != expected_ids[index]
                or {
                    key: control[key]
                    for key in ("id", "control", "evidence_class", "hard_gate")
                }
                != expected
                or control["passed"] is not True
                or control["points"] != 5
                or not isinstance(control["evidence"], str)
                or not control["evidence"]
                or control["id"] in controls_by_id
            ):
                raise ReceiptError(
                    "maturity report control %s is not a rubric-bound pass"
                    % expected_ids[index]
                )
            controls_by_id[control["id"]] = (name, control)
    if len(controls_by_id) != 100:
        raise ReceiptError("maturity report does not contain 100 unique controls")
    for control_id, dimension_name in (
        ("P19", "prompt"),
        ("P20", "prompt"),
        ("H20", "harness"),
    ):
        actual = controls_by_id.get(control_id)
        if (
            actual is None
            or actual[0] != dimension_name
            or actual[1]["passed"] is not True
            or actual[1]["points"] != 5
            or (
                control_id in {"P19", "H20"}
                and actual[1]["hard_gate"] is not True
            )
            or receipt["maturity"]["required_hard_gates"][control_id] is not True
        ):
            raise ReceiptError("maturity report required control %s did not pass" % control_id)


def rerun_semantic_evidence(
    *,
    semantic_verifier_path: Path,
    semantic_policy_path: Path,
    repository_root: Path,
    evidence_root: Path,
    run_id: str,
) -> dict:
    try:
        result = subprocess.run(
            [
                sys.executable,
                str(semantic_verifier_path),
                "--run-id",
                run_id,
                "--evidence-root",
                str(evidence_root),
                "--policy",
                str(semantic_policy_path),
                "--json",
            ],
            cwd=repository_root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=240,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ReceiptError("cannot revalidate raw semantic evidence: %s" % exc) from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ReceiptError(
            "raw semantic evidence failed current verification: %s"
            % (detail[-1000:] or "semantic verifier exited non-zero")
        )
    if len(result.stdout) > MAX_RECEIPT_BYTES:
        raise ReceiptError("semantic verifier summary exceeds the 1 MiB limit")
    try:
        value = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError("semantic verifier did not return strict JSON") from exc
    return exact_object(value, SEMANTIC_EVIDENCE_KEYS, "revalidated semantic evidence")


def semantic_policy_max_age_seconds(path: Path) -> int:
    try:
        policy = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError(
            "cannot read current semantic evidence policy: %s" % exc
        ) from exc
    if not isinstance(policy, dict):
        raise ReceiptError("current semantic evidence policy must be an object")
    maximum_age_days = policy.get("maximum_age_days")
    if (
        isinstance(maximum_age_days, bool)
        or not isinstance(maximum_age_days, int)
        or not 1 <= maximum_age_days <= 365
    ):
        raise ReceiptError(
            "current semantic evidence policy maximum_age_days is invalid"
        )
    return maximum_age_days * 86_400


def validate_raw_semantic_evidence(
    receipt_summary: dict,
    revalidated: dict,
    *,
    maximum_current_age_seconds: int = 86_400,
) -> None:
    _oldest, _newest = validate_engineering_semantic_evidence(
        revalidated,
        maximum_age_seconds=maximum_current_age_seconds,
    )
    for key in sorted(SEMANTIC_EVIDENCE_KEYS - {"age_seconds"}):
        if revalidated[key] != receipt_summary[key]:
            raise ReceiptError(
                "revalidated semantic evidence differs from receipt field %s" % key
            )
    current_age = number(
        revalidated["age_seconds"],
        "revalidated semantic evidence age_seconds",
        minimum=0,
        maximum=maximum_current_age_seconds,
    )
    oldest = parsed_timestamp(
        revalidated["oldest_result_at"],
        "revalidated semantic evidence oldest_result_at",
    )
    now_age = (dt.datetime.now(dt.timezone.utc) - oldest).total_seconds()
    if now_age < -300:
        raise ReceiptError("revalidated semantic evidence is timestamped in the future")
    if (
        now_age > maximum_current_age_seconds
        or current_age > maximum_current_age_seconds
    ):
        if maximum_current_age_seconds == 86_400:
            raise ReceiptError(
                "revalidated semantic evidence is not fresh within 24 hours"
            )
        raise ReceiptError(
            "revalidated semantic evidence exceeds the current semantic policy "
            "freshness window"
        )


def validate_engineering_receipt(
    receipt: dict,
    *,
    expected_commit: str,
    repository_root: Path,
    tool_paths: dict[str, Path],
    maturity_report_path: Path,
    evidence_root: Path,
    semantic_revalidator: Callable[..., dict] | None = None,
    post_release_continuation: bool = False,
) -> None:
    if receipt["$schema"] != ENGINEERING_SCHEMA:
        raise ReceiptError("engineering receipt schema identity is invalid")
    issued_at = parsed_timestamp(receipt["issued_at"], "issued_at")
    now = dt.datetime.now(dt.timezone.utc)
    if issued_at > now + dt.timedelta(minutes=5):
        raise ReceiptError("engineering receipt issued_at is in the future")
    if (
        not post_release_continuation
        and now - issued_at > dt.timedelta(hours=24)
    ):
        raise ReceiptError("engineering receipt is older than 24 hours")

    repository = exact_object(
        receipt["repository"],
        ENGINEERING_REPOSITORY_KEYS,
        "repository",
    )
    text(repository["branch"], "repository.branch", 255)
    if repository["worktree_clean"] is not True:
        raise ReceiptError("engineering receipt was not issued from a clean worktree")
    digest(
        repository["source_tree_sha256"],
        SHA256_RE,
        "repository.source_tree_sha256",
    )
    actual_tree = source_tree_sha256(repository_root, expected_commit)
    if repository["source_tree_sha256"] != actual_tree:
        raise ReceiptError("engineering receipt source tree does not match")

    validate_engineering_tools(
        receipt["tools"],
        paths=tool_paths,
        repository_root=repository_root,
        source_commit=expected_commit,
    )

    maturity = exact_object(
        receipt["maturity"],
        ENGINEERING_MATURITY_KEYS,
        "maturity",
    )
    evaluated_at = parsed_timestamp(
        maturity["evaluated_at"],
        "maturity.evaluated_at",
    )
    if evaluated_at > issued_at:
        raise ReceiptError("engineering maturity evaluation postdates the receipt")
    digest(
        maturity["report_sha256"],
        SHA256_RE,
        "maturity.report_sha256",
    )
    if (
        maturity["target_score"] != 95
        or maturity["achieved"] is not True
    ):
        raise ReceiptError("engineering maturity target/status is invalid")
    dimensions = exact_object(
        maturity["dimension_scores"],
        DIMENSION_KEYS,
        "maturity.dimension_scores",
    )
    for name in sorted(DIMENSION_KEYS):
        if (
            integer(
                dimensions[name],
                "maturity.dimension_scores." + name,
                minimum=0,
                maximum=100,
            )
            != 100
        ):
            raise ReceiptError("engineering maturity dimensions must all score 100")
    hard_gates = exact_object(
        maturity["required_hard_gates"],
        REQUIRED_ENGINEERING_GATE_KEYS,
        "maturity.required_hard_gates",
    )
    if any(hard_gates[name] is not True for name in REQUIRED_ENGINEERING_GATE_KEYS):
        raise ReceiptError("engineering maturity P19/P20/H20 must all pass")

    oldest, newest = validate_engineering_semantic_evidence(
        receipt["semantic_evidence"]
    )
    if newest > evaluated_at or oldest > evaluated_at:
        raise ReceiptError("semantic evidence postdates the maturity evaluation")
    if issued_at - oldest > dt.timedelta(hours=24):
        raise ReceiptError("semantic evidence is older than 24 hours")
    if (
        not post_release_continuation
        and now - oldest > dt.timedelta(hours=24)
    ):
        raise ReceiptError("semantic evidence is older than 24 hours")

    claims = exact_object(
        receipt["claims"],
        ENGINEERING_CLAIM_KEYS,
        "claims",
    )
    if (
        claims["validation_scope"] != "engineering-only"
        or claims["evidence_provenance"] != "simulated-semantic-cases"
        or claims["real_project_outcomes_validated"] is not False
        or claims["default_profile"] != "lite"
        or claims["governed_outcome_claims_allowed"] is not False
        or claims["governed_default_promotion_allowed"] is not False
    ):
        raise ReceiptError("engineering-only release claims are invalid")

    attestation = exact_object(
        receipt["attestation"],
        ENGINEERING_ATTESTATION_KEYS,
        "attestation",
    )
    if (
        attestation["method"]
        != "explicit-owner-engineering-only-authorization"
        or attestation["statement"]
        != "release-v19-without-real-project-outcomes"
    ):
        raise ReceiptError("engineering-only owner attestation is invalid")
    accepted_at = parsed_timestamp(
        attestation["accepted_at"],
        "attestation.accepted_at",
    )
    if accepted_at != issued_at:
        raise ReceiptError("owner authorization must coincide with receipt issuance")

    report, report_raw = read_private_maturity_report(
        maturity_report_path,
        repository_root=repository_root,
    )
    validate_maturity_report(
        report,
        report_raw,
        receipt=receipt,
        expected_commit=expected_commit,
        tool_paths=tool_paths,
    )
    resolved_evidence_root = resolve_private_evidence_root(
        evidence_root,
        repository_root=repository_root,
        run_id=receipt["semantic_evidence"]["run_id"],
    )
    if semantic_revalidator is None:
        revalidated = rerun_semantic_evidence(
            semantic_verifier_path=tool_paths["semantic_verifier"],
            semantic_policy_path=tool_paths["semantic_policy"],
            repository_root=repository_root,
            evidence_root=resolved_evidence_root,
            run_id=receipt["semantic_evidence"]["run_id"],
        )
    else:
        revalidated = semantic_revalidator(
            semantic_verifier_path=tool_paths["semantic_verifier"],
            semantic_policy_path=tool_paths["semantic_policy"],
            repository_root=repository_root,
            evidence_root=resolved_evidence_root,
            run_id=receipt["semantic_evidence"]["run_id"],
        )
        revalidated = exact_object(
            revalidated,
            SEMANTIC_EVIDENCE_KEYS,
            "revalidated semantic evidence",
        )
    validate_raw_semantic_evidence(
        receipt["semantic_evidence"],
        revalidated,
        maximum_current_age_seconds=(
            semantic_policy_max_age_seconds(tool_paths["semantic_policy"])
            if post_release_continuation
            else 86_400
        ),
    )


def validate_receipt(
    receipt: dict,
    *,
    expected_commit: str,
    expected_version: str,
    verifier_path: Path,
    repository_root: Path | None = None,
    engineering_paths: dict[str, Path] | None = None,
    maturity_report_path: Path | None = None,
    evidence_root: Path | None = None,
    semantic_revalidator: Callable[..., dict] | None = None,
    post_release_continuation: bool = False,
) -> dict:
    digest(expected_commit, SHA1_RE, "expected source commit")
    if not SEMVER_RE.fullmatch(expected_version):
        raise ReceiptError("expected release version must be numeric semver")
    if expected_version not in SUPPORTED_RELEASE_VERSIONS:
        raise ReceiptError(
            "expected release version is not supported by the v19 gate"
        )
    if not isinstance(receipt, dict):
        raise ReceiptError("receipt must be an object")
    gate = receipt.get("gate")
    receipt = exact_object(
        receipt,
        ENGINEERING_TOP_KEYS
        if gate == "engineering-validation-v19"
        else PROFILE_TOP_KEYS,
        "receipt",
    )
    if (
        receipt["schema_version"] != "1.0"
        or gate not in SUPPORTED_GATES
    ):
        raise ReceiptError("unsupported receipt identity")
    if receipt["passed"] is not True:
        raise ReceiptError("receipt is not a passing gate")
    if receipt["release_version"] != expected_version:
        raise ReceiptError("receipt release version does not match")
    matched_rc = (
        RC_RE.fullmatch(receipt["release_candidate"])
        if isinstance(receipt["release_candidate"], str)
        else None
    )
    if matched_rc is None or matched_rc.group("version") != expected_version:
        raise ReceiptError("receipt release candidate does not match final version")
    digest(receipt["source_commit"], SHA1_RE, "receipt.source_commit")
    if receipt["source_commit"] != expected_commit:
        raise ReceiptError("receipt source commit does not match")
    if gate == "engineering-validation-v19":
        if maturity_report_path is None or evidence_root is None:
            raise ReceiptError(
                "engineering release validation requires a private maturity report "
                "and raw semantic evidence root"
            )
        root = (
            repository_root
            if repository_root is not None
            else Path(__file__).resolve().parents[1]
        )
        paths = (
            engineering_paths
            if engineering_paths is not None
            else engineering_tool_paths(root)
        )
        validate_engineering_receipt(
            receipt,
            expected_commit=expected_commit,
            repository_root=root,
            tool_paths=paths,
            maturity_report_path=maturity_report_path,
            evidence_root=evidence_root,
            semantic_revalidator=semantic_revalidator,
            post_release_continuation=post_release_continuation,
        )
        return {
            "gate": gate,
            "release_candidate": receipt["release_candidate"],
            "release_version": expected_version,
            "source_commit": expected_commit,
        }

    for key in (
        "evidence_sha256",
        "evidence_manifest_sha256",
        "verifier_sha256",
    ):
        digest(receipt[key], SHA256_RE, "receipt." + key)
    try:
        verifier_digest = hashlib.sha256(verifier_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ReceiptError("cannot read outcome verifier: %s" % exc) from exc
    if verifier_digest != receipt["verifier_sha256"]:
        raise ReceiptError("receipt was issued by a different outcome verifier")

    model = exact_object(receipt["model_identity"], MODEL_KEYS, "model_identity")
    for key in ("provider", "model", "version"):
        text(model[key], "model_identity." + key, 120)
    digest(model["toolset_sha256"], SHA256_RE, "model_identity.toolset_sha256")
    attestation = exact_object(
        receipt["attestation"], ATTESTATION_KEYS, "attestation"
    )
    if attestation["method"] != "owner-attested-private-evidence":
        raise ReceiptError("receipt attestation method is invalid")
    digest(
        attestation["collector_id_hash"],
        SHA256_RE,
        "attestation.collector_id_hash",
    )
    signed_at = text(attestation["signed_at"], "attestation.signed_at")
    if "T" not in signed_at or not signed_at.endswith("Z"):
        raise ReceiptError("attestation.signed_at must be a UTC date-time")

    summary_keys = (
        PILOT_SUMMARY_KEYS
        if receipt["gate"] == "profile-pilots-v19"
        else FULL_SUMMARY_KEYS
    )
    summary = exact_object(
        receipt["outcome_summary"], summary_keys, "outcome_summary"
    )
    validate_summary_identity(
        summary,
        release_candidate=receipt["release_candidate"],
        expected_commit=expected_commit,
    )
    if receipt["gate"] == "profile-pilots-v19":
        validate_pilot_summary(summary)
    else:
        validate_full_summary(summary)
    return {
        "gate": gate,
        "release_candidate": receipt["release_candidate"],
        "release_version": expected_version,
        "source_commit": expected_commit,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--release-version", required=True)
    parser.add_argument(
        "--verifier",
        type=Path,
        default=Path(__file__).with_name("verify-profile-outcomes.py"),
    )
    parser.add_argument(
        "--required-gate",
        choices=sorted(SUPPORTED_GATES),
        help="Require one exact gate identity in addition to validating the receipt.",
    )
    parser.add_argument(
        "--maturity-report",
        type=Path,
        help="Absolute path to the private dynamic maturity report.",
    )
    parser.add_argument(
        "--evidence-root",
        type=Path,
        help="Absolute private root containing the receipt run's raw evidence chain.",
    )
    parser.add_argument(
        "--post-release-continuation",
        action="store_true",
        help=(
            "Revalidate an older engineering receipt only for a publisher that "
            "has already proved the immutable final GitHub release gates."
        ),
    )
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if (
            args.post_release_continuation
            and args.required_gate != "engineering-validation-v19"
        ):
            raise ReceiptError(
                "--post-release-continuation requires "
                "--required-gate engineering-validation-v19"
            )
        receipt, raw = read_private_receipt(args.receipt)
        identity = validate_receipt(
            receipt,
            expected_commit=args.source_commit,
            expected_version=args.release_version,
            verifier_path=args.verifier,
            maturity_report_path=args.maturity_report,
            evidence_root=args.evidence_root,
            post_release_continuation=args.post_release_continuation,
        )
        if (
            args.required_gate is not None
            and identity["gate"] != args.required_gate
        ):
            raise ReceiptError(
                "receipt gate is %s, required %s"
                % (identity["gate"], args.required_gate)
            )
        identity["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
        if args.json:
            print(json.dumps(identity, indent=2, sort_keys=True))
        else:
            print(
                "%s\t%s\t%s"
                % (
                    identity["receipt_sha256"],
                    identity["release_candidate"],
                    identity["source_commit"],
                )
            )
        return 0
    except ReceiptError as exc:
        print("release receipt invalid: %s" % exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
