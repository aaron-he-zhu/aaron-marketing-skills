#!/usr/bin/env python3
"""Issue a private engineering-only v19 release receipt.

The issuer runs the current five-dimension maturity checker dynamically against
an exact clean commit and a fresh real-provider semantic-evidence UUID. It
requires 24 simulated semantic cases, a distinct judge, 100/100 in every
engineering dimension, and passing P19/P20/H20 controls. The receipt explicitly
does not claim real-project outcomes and cannot promote Governed to the default.

Receipts must be written outside the repository. Creation is single-use,
O_EXCL, no-follow, and mode 0600; an existing target is never overwritten.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RECEIPT_SCHEMA_REF = "references/engineering-release-receipt.schema.json"
REPORT_SCHEMA_REF = "references/engineering-maturity-report.schema.json"
RELEASE_VERSION = "19.0.0"
GATE = "engineering-validation-v19"
AUTHORIZATION = "release-v19-without-real-project-outcomes"
MAX_EVIDENCE_AGE_SECONDS = 24 * 60 * 60
RC_RE = re.compile(r"^19\.0\.0-rc\.[1-9][0-9]*$")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
)
TIMESTAMP_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)
DIMENSIONS = ("prompt", "context", "harness", "loop", "graph")
REQUIRED_CONTROLS = {"P19": "prompt", "P20": "prompt", "H20": "harness"}
TOOL_REFS = {
    "issuer": "scripts/issue-engineering-release-receipt.py",
    "maturity_checker": "scripts/check-engineering-maturity.py",
    "semantic_verifier": "scripts/verify-semantic-evidence.py",
    "release_verifier": "scripts/verify-release-receipt.py",
    "maturity_rubric": "references/engineering-maturity-rubric.json",
    "semantic_policy": "evals/semantic-evidence-policy.json",
    "receipt_schema": RECEIPT_SCHEMA_REF,
}
REPORT_KEYS = {
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
SEMANTIC_KEYS = {
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
    "result_stream_sha256",
    "head_record_hash",
    "completion_sha256",
    "oldest_result_at",
    "newest_evidence_at",
    "age_seconds",
}
SOURCE_KEYS = {"ref", "sha256"}
MAX_RECEIPT_BYTES = 512_000


class EngineeringReceiptError(ValueError):
    """The engineering release receipt cannot be safely issued."""


def _canonical_json_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise EngineeringReceiptError("receipt evidence is not canonical JSON") from exc


def _utc_timestamp(value: dt.datetime) -> str:
    if value.tzinfo is None:
        raise EngineeringReceiptError("receipt clock must include a timezone")
    return value.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_timestamp(value: Any, label: str) -> dt.datetime:
    if not isinstance(value, str) or not TIMESTAMP_RE.fullmatch(value):
        raise EngineeringReceiptError("%s must be a UTC timestamp" % label)
    try:
        parsed = dt.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise EngineeringReceiptError("%s is not a valid timestamp" % label) from exc
    return parsed


def _exact_object(value: Any, keys: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        raise EngineeringReceiptError("%s has unknown or missing fields" % label)
    return value


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _git(root: Path, *arguments: str) -> bytes:
    try:
        result = subprocess.run(
            ["git", *arguments],
            cwd=root,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise EngineeringReceiptError("cannot inspect release repository: %s" % exc) from exc
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise EngineeringReceiptError(
            "git %s failed%s"
            % (" ".join(arguments), (": " + message[-500:]) if message else "")
        )
    return result.stdout


def repository_snapshot(root: Path) -> dict[str, Any]:
    """Return the exact clean HEAD identity and a SHA-256 tree manifest."""
    root = root.resolve()
    top = Path(
        _git(root, "rev-parse", "--show-toplevel")
        .decode("utf-8", errors="strict")
        .strip()
    ).resolve()
    if top != root:
        raise EngineeringReceiptError("release root must be the Git worktree root")
    commit = (
        _git(root, "rev-parse", "--verify", "HEAD^{commit}")
        .decode("ascii", errors="strict")
        .strip()
    )
    if not SHA1_RE.fullmatch(commit):
        raise EngineeringReceiptError("release HEAD must be a 40-character commit")
    branch = (
        _git(root, "branch", "--show-current")
        .decode("utf-8", errors="strict")
        .strip()
    )
    if not branch or len(branch) > 255:
        raise EngineeringReceiptError("release HEAD must be attached to a named branch")
    status_bytes = _git(root, "status", "--porcelain=v1", "--untracked-files=all")
    if status_bytes:
        raise EngineeringReceiptError("release worktree must be clean")
    tree_manifest = _git(root, "ls-tree", "-r", "--full-tree", commit)
    if not tree_manifest:
        raise EngineeringReceiptError("release commit tree is empty")
    return {
        "commit": commit,
        "branch": branch,
        "worktree_clean": True,
        "source_tree_sha256": _sha256(tree_manifest),
    }


def _stable_regular_bytes(path: Path, label: str, maximum: int = 8_000_000) -> bytes:
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise EngineeringReceiptError("cannot open %s: %s" % (label, exc)) from exc
    try:
        before = os.fstat(descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > maximum
        ):
            raise EngineeringReceiptError(
                "%s must be a bounded single-link regular file" % label
            )
        chunks = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(descriptor, min(131_072, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(descriptor)
    finally:
        os.close(descriptor)
    if len(raw) > maximum:
        raise EngineeringReceiptError("%s exceeds its byte bound" % label)
    identity = ("st_dev", "st_ino", "st_nlink", "st_size", "st_mtime_ns", "st_ctime_ns")
    if (
        len(raw) != before.st_size
        or any(getattr(before, field) != getattr(after, field) for field in identity)
    ):
        raise EngineeringReceiptError("%s changed while it was read" % label)
    return raw


def source_snapshot(root: Path) -> dict[str, dict[str, str]]:
    result = {}
    for name, reference in TOOL_REFS.items():
        raw = _stable_regular_bytes(root / reference, reference)
        result[name] = {"ref": reference, "sha256": _sha256(raw)}
    return result


def committed_release_version(root: Path, commit: str) -> str:
    raw = _git(root, "show", "%s:.claude-plugin/plugin.json" % commit)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise EngineeringReceiptError("committed plugin manifest is invalid JSON") from exc
    version = value.get("version") if isinstance(value, dict) else None
    if version != RELEASE_VERSION:
        raise EngineeringReceiptError(
            "committed release version %r != %s" % (version, RELEASE_VERSION)
        )
    return version


def _load_maturity_checker(root: Path):
    path = root / TOOL_REFS["maturity_checker"]
    spec = importlib.util.spec_from_file_location(
        "aaron_engineering_release_maturity_checker", path
    )
    if spec is None or spec.loader is None:
        raise EngineeringReceiptError("cannot load the current maturity checker")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:
        raise EngineeringReceiptError(
            "cannot execute the current maturity checker: %s" % exc
        ) from exc
    return module


def _validate_source(value: Any, expected: dict[str, str], label: str) -> None:
    source = _exact_object(value, SOURCE_KEYS, label)
    if source != expected:
        raise EngineeringReceiptError("%s does not bind the current source bytes" % label)


def validate_maturity_report(
    report: Any,
    *,
    repository: dict[str, Any],
    tools: dict[str, dict[str, str]],
    run_id: str,
    issued_at: dt.datetime,
) -> dict[str, Any]:
    """Validate the dynamic checker result and return the exact semantic summary."""
    report = _exact_object(report, REPORT_KEYS, "maturity report")
    if report["$schema"] != REPORT_SCHEMA_REF or report["schema_version"] != "1.0":
        raise EngineeringReceiptError("maturity report schema identity is invalid")
    if (
        report["repository"]
        != {
            "git_available": True,
            "commit": repository["commit"],
            "branch": repository["branch"],
            "worktree_clean": True,
        }
    ):
        raise EngineeringReceiptError("maturity report does not bind the clean release HEAD")
    _validate_source(
        report["checker"], tools["maturity_checker"], "maturity report checker"
    )
    if report["rubric_sha256"] != tools["maturity_rubric"]["sha256"]:
        raise EngineeringReceiptError("maturity report does not bind the current rubric")
    if report["target_score"] != 95 or report["achieved"] is not True:
        raise EngineeringReceiptError("engineering maturity target was not achieved")
    maturity_time = _parse_timestamp(
        report["evaluated_at"], "maturity report evaluated_at"
    )
    if maturity_time > issued_at.astimezone(dt.timezone.utc):
        raise EngineeringReceiptError("maturity report timestamp is after issuance")

    dimensions = _exact_object(
        report["dimensions"], set(DIMENSIONS), "maturity report dimensions"
    )
    controls_by_id = {}
    for name in DIMENSIONS:
        dimension = dimensions[name]
        if not isinstance(dimension, dict):
            raise EngineeringReceiptError("maturity dimension %s is invalid" % name)
        required = {
            "raw_score",
            "final_score",
            "score_10",
            "target_met",
            "failed_hard_gates",
            "failed_controls",
            "controls",
        }
        _exact_object(dimension, required, "maturity dimension %s" % name)
        if (
            dimension["raw_score"] != 100
            or dimension["final_score"] != 100
            or dimension["score_10"] != 10.0
            or dimension["target_met"] is not True
            or dimension["failed_hard_gates"] != []
            or dimension["failed_controls"] != []
            or not isinstance(dimension["controls"], list)
            or len(dimension["controls"]) != 20
        ):
            raise EngineeringReceiptError(
                "maturity dimension %s must pass at 100/100" % name
            )
        expected_ids = [
            "%s%02d" % (name[0].upper(), index) for index in range(1, 21)
        ]
        actual_ids = [
            control.get("id") if isinstance(control, dict) else None
            for control in dimension["controls"]
        ]
        if actual_ids != expected_ids:
            raise EngineeringReceiptError(
                "maturity dimension %s control order is invalid" % name
            )
        for control in dimension["controls"]:
            _exact_object(
                control,
                {
                    "id",
                    "control",
                    "evidence_class",
                    "hard_gate",
                    "passed",
                    "points",
                    "evidence",
                },
                "maturity control %s" % control.get("id", "unknown"),
            )
            if (
                not isinstance(control["control"], str)
                or len(control["control"]) < 8
                or control["evidence_class"] not in {"S", "D", "E", "R", "O"}
                or not isinstance(control["hard_gate"], bool)
                or control["passed"] is not True
                or control["points"] != 5
                or not isinstance(control["evidence"], str)
                or not control["evidence"]
            ):
                raise EngineeringReceiptError(
                    "maturity control %s is not a complete pass" % control["id"]
                )
            if control["id"] in controls_by_id:
                raise EngineeringReceiptError(
                    "maturity control %s is duplicated" % control["id"]
                )
            controls_by_id[control["id"]] = (name, control)
    if len(controls_by_id) != 100:
        raise EngineeringReceiptError("maturity report must contain 100 unique controls")
    for control_id, expected_dimension in REQUIRED_CONTROLS.items():
        actual = controls_by_id.get(control_id)
        if actual is None or actual[0] != expected_dimension:
            raise EngineeringReceiptError(
                "required maturity control %s is missing" % control_id
            )
        control = actual[1]
        if (
            control.get("passed") is not True
            or control.get("points") != 5
            or control_id in {"P19", "H20"} and control.get("hard_gate") is not True
        ):
            raise EngineeringReceiptError(
                "required maturity control %s did not pass" % control_id
            )

    if report["semantic_evidence_run_id"] != run_id:
        raise EngineeringReceiptError("maturity report semantic run ID does not match")
    semantic = _exact_object(
        report["semantic_evidence"], SEMANTIC_KEYS, "semantic evidence"
    )
    if (
        semantic["schema_version"] != "1.0"
        or semantic["valid"] is not True
        or semantic["run_id"] != run_id
        or semantic["profile"] != "smoke"
        or semantic["case_count"] != 24
        or semantic["case_provenance"] != {"simulated": 24}
        or semantic["execution_mode"] != "real"
        or semantic["distinct_judge_model"] is not True
        or not isinstance(semantic["model_id"], str)
        or not 1 <= len(semantic["model_id"]) <= 120
        or not isinstance(semantic["judge_model_id"], str)
        or not 1 <= len(semantic["judge_model_id"]) <= 120
        or semantic["model_id"] == semantic["judge_model_id"]
    ):
        raise EngineeringReceiptError(
            "semantic evidence must be a 24-case simulated, real-provider, distinct-judge run"
        )
    if not UUID_RE.fullmatch(run_id):
        raise EngineeringReceiptError("semantic evidence run ID must be a canonical UUID")
    for key in (
        "adapter_implementation_sha256",
        "runner_sha256",
        "selection_sha256",
        "protocol_schema_sha256",
        "request_stream_sha256",
        "result_stream_sha256",
        "head_record_hash",
        "completion_sha256",
    ):
        if not isinstance(semantic[key], str) or not SHA256_RE.fullmatch(semantic[key]):
            raise EngineeringReceiptError("semantic evidence %s is invalid" % key)
    for key in (
        "model_provider",
        "host_name",
        "host_version",
        "adapter_name",
    ):
        if not isinstance(semantic[key], str) or not semantic[key] or len(semantic[key]) > 120:
            raise EngineeringReceiptError("semantic evidence %s is invalid" % key)
    attempts = semantic["total_judge_attempts"]
    retried = semantic["retried_cases"]
    protocol_retries = semantic["judge_protocol_retries"]
    if (
        not isinstance(attempts, int)
        or isinstance(attempts, bool)
        or not isinstance(retried, int)
        or isinstance(retried, bool)
        or not isinstance(protocol_retries, int)
        or isinstance(protocol_retries, bool)
        or not 24 <= attempts <= 48
        or not 0 <= retried <= 24
        or protocol_retries != retried
        or attempts != 24 + retried
    ):
        raise EngineeringReceiptError("semantic judge-attempt ledger is inconsistent")
    age = semantic["age_seconds"]
    if (
        isinstance(age, bool)
        or not isinstance(age, (int, float))
        or not 0 <= age <= MAX_EVIDENCE_AGE_SECONDS
    ):
        raise EngineeringReceiptError("semantic evidence must be at most 24 hours old")
    oldest = _parse_timestamp(
        semantic["oldest_result_at"], "semantic evidence oldest_result_at"
    )
    newest = _parse_timestamp(
        semantic["newest_evidence_at"], "semantic evidence newest_evidence_at"
    )
    if oldest > newest or issued_at.astimezone(dt.timezone.utc) < newest:
        raise EngineeringReceiptError("semantic evidence timestamps are inconsistent")
    if oldest > maturity_time or newest > maturity_time:
        raise EngineeringReceiptError(
            "semantic evidence postdates the maturity evaluation"
        )
    if issued_at.astimezone(dt.timezone.utc) - oldest > dt.timedelta(
        seconds=MAX_EVIDENCE_AGE_SECONDS
    ):
        raise EngineeringReceiptError("semantic evidence is not fresh enough to release")
    return semantic


def build_receipt(
    report: dict[str, Any],
    *,
    repository: dict[str, Any],
    tools: dict[str, dict[str, str]],
    release_candidate: str,
    semantic: dict[str, Any],
    report_sha256: str,
    issued_at: dt.datetime,
) -> dict[str, Any]:
    if not SHA256_RE.fullmatch(report_sha256):
        raise EngineeringReceiptError("maturity report file digest is invalid")
    timestamp = _utc_timestamp(issued_at)
    return {
        "$schema": RECEIPT_SCHEMA_REF,
        "schema_version": "1.0",
        "gate": GATE,
        "passed": True,
        "release_version": RELEASE_VERSION,
        "release_candidate": release_candidate,
        "source_commit": repository["commit"],
        "issued_at": timestamp,
        "repository": {
            "branch": repository["branch"],
            "worktree_clean": True,
            "source_tree_sha256": repository["source_tree_sha256"],
        },
        "tools": tools,
        "maturity": {
            "evaluated_at": report["evaluated_at"],
            "report_sha256": report_sha256,
            "target_score": 95,
            "achieved": True,
            "dimension_scores": {
                name: report["dimensions"][name]["final_score"] for name in DIMENSIONS
            },
            "required_hard_gates": {control_id: True for control_id in REQUIRED_CONTROLS},
        },
        "semantic_evidence": semantic,
        "claims": {
            "validation_scope": "engineering-only",
            "evidence_provenance": "simulated-semantic-cases",
            "real_project_outcomes_validated": False,
            "default_profile": "lite",
            "governed_outcome_claims_allowed": False,
            "governed_default_promotion_allowed": False,
        },
        "attestation": {
            "method": "explicit-owner-engineering-only-authorization",
            "statement": AUTHORIZATION,
            "accepted_at": timestamp,
        },
    }


def _outside_repository(path: Path, root: Path) -> tuple[Path, Path]:
    if not path.is_absolute():
        raise EngineeringReceiptError("receipt output path must be absolute")
    if path.name in {"", ".", ".."}:
        raise EngineeringReceiptError("receipt output filename is invalid")
    try:
        parent = path.parent.resolve(strict=True)
    except OSError as exc:
        raise EngineeringReceiptError("receipt parent does not exist: %s" % exc) from exc
    if not parent.is_dir() or path.parent.is_symlink():
        raise EngineeringReceiptError("receipt parent must be an existing real directory")
    target = parent / path.name
    try:
        target.relative_to(root.resolve())
    except ValueError:
        pass
    else:
        raise EngineeringReceiptError("receipt must remain outside the source repository")
    return parent, target


def _write_private_json(
    path: Path,
    root: Path,
    value: dict[str, Any],
    *,
    label: str,
    maximum: int,
) -> tuple[str, tuple[int, int]]:
    """Create one private JSON artifact and return its digest and inode identity."""
    parent, target = _outside_repository(Path(path), root)
    raw = (
        json.dumps(
            value,
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    if len(raw) > maximum:
        raise EngineeringReceiptError("%s exceeds its byte bound" % label)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    try:
        directory_fd = os.open(parent, directory_flags)
    except OSError as exc:
        raise EngineeringReceiptError("cannot anchor receipt parent: %s" % exc) from exc
    file_fd = None
    identity = None
    try:
        parent_before = os.fstat(directory_fd)
        try:
            file_fd = os.open(
                target.name,
                os.O_WRONLY
                | os.O_CREAT
                | os.O_EXCL
                | getattr(os, "O_NOFOLLOW", 0),
                0o600,
                dir_fd=directory_fd,
            )
        except FileExistsError as exc:
            raise EngineeringReceiptError(
                "%s output already exists; refusing to overwrite" % label
            ) from exc
        file_before = os.fstat(file_fd)
        identity = (file_before.st_dev, file_before.st_ino)
        if not stat.S_ISREG(file_before.st_mode) or file_before.st_nlink != 1:
            raise EngineeringReceiptError(
                "%s target is not a single-link regular file" % label
            )
        os.fchmod(file_fd, 0o600)
        view = memoryview(raw)
        while view:
            written = os.write(file_fd, view)
            if written <= 0:
                raise EngineeringReceiptError("%s write made no progress" % label)
            view = view[written:]
        os.fsync(file_fd)
        file_after = os.fstat(file_fd)
        if (
            file_after.st_dev != file_before.st_dev
            or file_after.st_ino != file_before.st_ino
            or file_after.st_nlink != 1
            or file_after.st_size != len(raw)
            or stat.S_IMODE(file_after.st_mode) != 0o600
        ):
            raise EngineeringReceiptError(
                "%s identity or permissions changed while written" % label
            )
        os.close(file_fd)
        file_fd = None
        os.fsync(directory_fd)
        parent_after = os.fstat(directory_fd)
        if (
            parent_after.st_dev != parent_before.st_dev
            or parent_after.st_ino != parent_before.st_ino
        ):
            raise EngineeringReceiptError("%s parent changed while written" % label)
        final = os.stat(target.name, dir_fd=directory_fd, follow_symlinks=False)
        if (
            (final.st_dev, final.st_ino) != identity
            or final.st_nlink != 1
            or final.st_size != len(raw)
            or stat.S_IMODE(final.st_mode) != 0o600
        ):
            raise EngineeringReceiptError("%s target changed after creation" % label)
    except Exception:
        if file_fd is not None:
            os.close(file_fd)
        if identity is not None:
            try:
                current = os.stat(
                    target.name, dir_fd=directory_fd, follow_symlinks=False
                )
                if (current.st_dev, current.st_ino) == identity:
                    os.unlink(target.name, dir_fd=directory_fd)
            except OSError:
                pass
        raise
    finally:
        os.close(directory_fd)
    return _sha256(raw), identity


def write_private_receipt(
    path: Path, root: Path, receipt: dict[str, Any]
) -> tuple[str, tuple[int, int]]:
    """Create a receipt exactly once and return its digest and inode identity."""
    return _write_private_json(
        path,
        root,
        receipt,
        label="engineering receipt",
        maximum=MAX_RECEIPT_BYTES,
    )


def write_private_maturity_report(
    path: Path, root: Path, report: dict[str, Any]
) -> tuple[str, tuple[int, int]]:
    """Persist the exact dynamic audit report once, outside the repository."""
    return _write_private_json(
        path,
        root,
        report,
        label="maturity report",
        maximum=MAX_RECEIPT_BYTES,
    )


def remove_owned_receipt(path: Path, identity: tuple[int, int]) -> None:
    """Remove a just-created receipt only when its anchored inode still matches."""
    parent = path.parent.resolve(strict=True)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(parent, directory_flags)
    try:
        current = os.stat(path.name, dir_fd=directory_fd, follow_symlinks=False)
        if (current.st_dev, current.st_ino) != identity:
            raise EngineeringReceiptError(
                "cannot revoke drifted receipt because its identity changed"
            )
        os.unlink(path.name, dir_fd=directory_fd)
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def verify_owned_private_artifact(
    path: Path,
    identity: tuple[int, int],
    expected_sha256: str,
    *,
    maximum: int = MAX_RECEIPT_BYTES,
) -> None:
    """Re-read one issued artifact through an anchored descriptor."""
    parent = path.parent.resolve(strict=True)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    directory_flags |= getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(parent, directory_flags)
    file_fd = None
    try:
        file_fd = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=directory_fd,
        )
        before = os.fstat(file_fd)
        if (
            (before.st_dev, before.st_ino) != identity
            or not stat.S_ISREG(before.st_mode)
            or before.st_nlink != 1
            or before.st_size > maximum
            or stat.S_IMODE(before.st_mode) != 0o600
        ):
            raise EngineeringReceiptError("private release artifact identity changed")
        chunks = []
        remaining = maximum + 1
        while remaining:
            chunk = os.read(file_fd, min(131_072, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        after = os.fstat(file_fd)
        if (
            len(raw) != before.st_size
            or (after.st_dev, after.st_ino) != identity
            or after.st_nlink != 1
            or after.st_size != before.st_size
            or after.st_mtime_ns != before.st_mtime_ns
            or after.st_ctime_ns != before.st_ctime_ns
            or _sha256(raw) != expected_sha256
        ):
            raise EngineeringReceiptError("private release artifact changed after creation")
    finally:
        if file_fd is not None:
            os.close(file_fd)
        os.close(directory_fd)


def issue_receipt(
    *,
    root: Path,
    run_id: str,
    evidence_root: Path,
    release_candidate: str,
    owner_authorization: str,
    output: Path,
    maturity_report_output: Path,
    timeout: int = 240,
    now: dt.datetime | None = None,
) -> tuple[dict[str, Any], str]:
    root = Path(root).resolve()
    if not RC_RE.fullmatch(release_candidate):
        raise EngineeringReceiptError(
            "release_candidate must match 19.0.0-rc.N with N >= 1"
        )
    if owner_authorization != AUTHORIZATION:
        raise EngineeringReceiptError(
            "explicit owner engineering-only authorization is required"
        )
    if not UUID_RE.fullmatch(run_id):
        raise EngineeringReceiptError("semantic evidence run ID must be a canonical UUID")
    if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1:
        raise EngineeringReceiptError("timeout must be a positive integer")
    _receipt_parent, receipt_target = _outside_repository(Path(output), root)
    _report_parent, report_target = _outside_repository(
        Path(maturity_report_output), root
    )
    if receipt_target == report_target:
        raise EngineeringReceiptError(
            "receipt and maturity report outputs must be distinct paths"
        )

    before_repository = repository_snapshot(root)
    committed_release_version(root, before_repository["commit"])
    before_tools = source_snapshot(root)
    maturity = _load_maturity_checker(root)
    evaluated_at = now or dt.datetime.now(dt.timezone.utc)
    if evaluated_at.tzinfo is None:
        raise EngineeringReceiptError("receipt clock must include a timezone")
    try:
        report = maturity.audit(
            root,
            run_dynamic=True,
            evidence_run_id=run_id,
            evidence_root=Path(evidence_root).resolve(),
            timeout=timeout,
            evaluated_at=evaluated_at,
        )
    except Exception as exc:
        raise EngineeringReceiptError("dynamic maturity audit failed: %s" % exc) from exc
    issued_at = now or dt.datetime.now(dt.timezone.utc)
    semantic = validate_maturity_report(
        report,
        repository=before_repository,
        tools=before_tools,
        run_id=run_id,
        issued_at=issued_at,
    )

    if repository_snapshot(root) != before_repository or source_snapshot(root) != before_tools:
        raise EngineeringReceiptError(
            "release source or bound tools changed during the dynamic audit"
        )
    report_digest, report_identity = write_private_maturity_report(
        Path(maturity_report_output), root, report
    )
    try:
        receipt = build_receipt(
            report,
            repository=before_repository,
            tools=before_tools,
            release_candidate=release_candidate,
            semantic=semantic,
            report_sha256=report_digest,
            issued_at=issued_at,
        )
        digest, receipt_identity = write_private_receipt(Path(output), root, receipt)
    except Exception:
        remove_owned_receipt(Path(maturity_report_output), report_identity)
        raise
    try:
        if (
            repository_snapshot(root) != before_repository
            or source_snapshot(root) != before_tools
        ):
            raise EngineeringReceiptError(
                "release source or bound tools changed while the receipt was issued"
            )
        verify_owned_private_artifact(
            Path(maturity_report_output), report_identity, report_digest
        )
        verify_owned_private_artifact(Path(output), receipt_identity, digest)
    except Exception:
        remove_owned_receipt(Path(output), receipt_identity)
        remove_owned_receipt(Path(maturity_report_output), report_identity)
        raise
    return receipt, digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Clean release worktree root")
    parser.add_argument("--semantic-evidence-run-id", required=True)
    parser.add_argument(
        "--evidence-root",
        required=True,
        help="Project root containing private memory/runs semantic evidence",
    )
    parser.add_argument("--release-candidate", required=True)
    parser.add_argument(
        "--owner-authorization",
        required=True,
        help="Must be the explicit engineering-only authorization statement",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Absolute, non-existing private receipt path outside the repository",
    )
    parser.add_argument(
        "--maturity-report-output",
        required=True,
        help="Distinct absolute, non-existing private audit-report path outside the repository",
    )
    parser.add_argument("--timeout", type=int, default=240)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        receipt, digest = issue_receipt(
            root=Path(args.root),
            run_id=args.semantic_evidence_run_id,
            evidence_root=Path(args.evidence_root),
            release_candidate=args.release_candidate,
            owner_authorization=args.owner_authorization,
            output=Path(args.output),
            maturity_report_output=Path(args.maturity_report_output),
            timeout=args.timeout,
        )
    except (EngineeringReceiptError, OSError, ValueError) as exc:
        print("issue-engineering-release-receipt: %s" % exc, file=sys.stderr)
        return 2
    print(
        "PASS engineering release receipt: %s %s %s"
        % (receipt["source_commit"], receipt["release_candidate"], digest)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
