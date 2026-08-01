#!/usr/bin/env python3
"""Semantically verify one paired prompt-profile release-evidence document."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_RUNTIME = ROOT / "scripts" / "prompt_profile_evidence.py"
MAX_EVIDENCE_BYTES = 8_000_000


def _load_runtime():
    spec = importlib.util.spec_from_file_location(
        "aaron_prompt_profile_evidence", EVIDENCE_RUNTIME
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load prompt-profile evidence runtime")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _read_regular(path):
    try:
        status = path.lstat()
        if path.is_symlink() or not path.is_file() or status.st_nlink != 1:
            raise OSError("not a single-link regular file")
        if status.st_size > MAX_EVIDENCE_BYTES:
            raise OSError("file exceeds %d bytes" % MAX_EVIDENCE_BYTES)
        raw = path.read_bytes()
    except OSError as exc:
        raise RuntimeError("cannot read evidence: %s" % exc) from exc
    if len(raw) > MAX_EVIDENCE_BYTES:
        raise RuntimeError("evidence exceeds %d bytes" % MAX_EVIDENCE_BYTES)
    return raw


def _write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(
        value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
    ) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=".%s." % target.name, dir=target.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    return hashlib.sha256(raw).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", help="paired evidence JSON file")
    parser.add_argument("--bundle-root", default=str(ROOT))
    parser.add_argument(
        "--as-of",
        help="RFC3339 UTC verification instant; defaults to the current UTC time",
    )
    parser.add_argument(
        "--allow-noncertifying",
        action="store_true",
        help="validate semantics but do not require every release gate to pass",
    )
    parser.add_argument(
        "--certificate-out",
        help="write a compact Governed promotion certificate (requires certifying evidence)",
    )
    parser.add_argument(
        "--previous-certificate",
        action="append",
        default=[],
        help=(
            "previous promotion certificate; repeat to reject arm-run-set replay "
            "and duplicate ledger entries"
        ),
    )
    args = parser.parse_args(argv)
    runtime = _load_runtime()
    try:
        raw = _read_regular(Path(args.evidence))
        document = runtime.strict_json_loads(raw, "prompt profile evidence")
        as_of = args.as_of or runtime.format_datetime(runtime.datetime.now(runtime.timezone.utc))
        result = runtime.validate_evidence(
            document,
            bundle_root=Path(args.bundle_root),
            as_of=as_of,
            require_valid=not args.allow_noncertifying,
        )
        if args.certificate_out:
            if args.allow_noncertifying:
                raise RuntimeError(
                    "--certificate-out cannot be combined with --allow-noncertifying"
                )
            previous_certificates = [
                runtime.strict_json_loads(
                    _read_regular(Path(path)),
                    "previous prompt profile certificate",
                )
                for path in args.previous_certificate
            ]
            certificate = runtime.build_release_certificate(
                document,
                hashlib.sha256(raw).hexdigest(),
                promoted_at=as_of,
                bundle_root=Path(args.bundle_root),
                previous_certificates=previous_certificates,
            )
            result = dict(result)
            result["certificate_sha256"] = _write_json(
                args.certificate_out, certificate
            )
            result["certificate_out"] = str(Path(args.certificate_out))
        elif args.previous_certificate:
            raise RuntimeError(
                "--previous-certificate requires --certificate-out"
            )
    except (RuntimeError, runtime.PromptProfileEvidenceError) as exc:
        print("prompt-profile release evidence invalid: %s" % exc, file=sys.stderr)
        return 1
    result = dict(result)
    result["verified_as_of"] = as_of
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
