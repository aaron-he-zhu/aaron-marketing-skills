#!/usr/bin/env python3
"""Validate a private profile-outcome receipt for an exact final release."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any


SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SEMVER_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
RC_RE = re.compile(r"^(?P<version>19\.0\.0)-rc\.[1-9][0-9]*$")
RELEASE_VERSION = "19.0.0"
MAX_RECEIPT_BYTES = 1024 * 1024
TOP_KEYS = {
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
MODEL_KEYS = {"provider", "model", "version", "toolset_sha256"}
ATTESTATION_KEYS = {"method", "collector_id_hash", "signed_at"}
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
SUPPORTED_GATES = {"profile-pilots-v19", "profile-outcomes-v19"}
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
    try:
        before = path.lstat()
        if path.is_symlink() or not path.is_file() or before.st_nlink != 1:
            raise ReceiptError("receipt must be a single-link regular file")
        if before.st_size > MAX_RECEIPT_BYTES:
            raise ReceiptError("receipt exceeds the 1 MiB limit")
        raw = path.read_bytes()
        after = path.lstat()
    except ReceiptError:
        raise
    except OSError as exc:
        raise ReceiptError("cannot read receipt: %s" % exc) from exc
    if (
        (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
        != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
        or len(raw) != after.st_size
    ):
        raise ReceiptError("receipt changed while it was being read")
    repository_root = Path(__file__).resolve().parents[1]
    try:
        path.resolve().relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise ReceiptError("receipt must stay outside the source repository")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise ReceiptError("receipt must be UTF-8 JSON: %s" % exc) from exc
    return exact_object(value, TOP_KEYS, "receipt"), raw


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


def validate_receipt(
    receipt: dict,
    *,
    expected_commit: str,
    expected_version: str,
    verifier_path: Path,
) -> dict:
    receipt = exact_object(receipt, TOP_KEYS, "receipt")
    digest(expected_commit, SHA1_RE, "expected source commit")
    if not SEMVER_RE.fullmatch(expected_version):
        raise ReceiptError("expected release version must be numeric semver")
    if expected_version != RELEASE_VERSION:
        raise ReceiptError("expected release version is not supported by the v19 gate")
    if (
        receipt["schema_version"] != "1.0"
        or receipt["gate"] not in SUPPORTED_GATES
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
        "gate": receipt["gate"],
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
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        receipt, raw = read_private_receipt(args.receipt)
        identity = validate_receipt(
            receipt,
            expected_commit=args.source_commit,
            expected_version=args.release_version,
            verifier_path=args.verifier,
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
