#!/usr/bin/env python3
"""Classify repository changes into the v19 S0-S3 validation tiers.

The semantic selector and the CI classifier share ``evals/change-impact.json``.
The selector decides which behavior cases are relevant; this script decides
how much repository validation is required. Safety-sensitive paths have
fail-closed overrides, and an unrecognized runtime, hook, schema, or workflow
path is always S3.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
IMPACT_MAP = ROOT / "evals" / "change-impact.json"
CATALOG = ROOT / "references" / "system-catalog.json"
TIERS = ("S0", "S1", "S2", "S3")
TIER_RANK = {tier: rank for rank, tier in enumerate(TIERS)}

S3_PREFIXES = (
    ".github/workflows/",
    ".githooks/",
    "hooks/",
)
S3_EXACT = {
    "SECURITY.md",
    "references/control-bindings.json",
    "scripts/check-pii.py",
    "scripts/check-stdlib-only.sh",
    "scripts/check-versions.sh",
    "scripts/profile-resolver.py",
    "scripts/registry-events.py",
    "scripts/run-events.py",
    "scripts/runtime-controller.py",
    "scripts/validate-audit-artifact.py",
}
S3_SCRIPT_PREFIXES = (
    "scripts/publish-",
    "scripts/sync-",
)
S3_REFERENCE_TERMS = (
    "approval",
    "audit-",
    "consent",
    "claims",
    "external",
    "owner-capability",
    "pii",
    "profile",
    "registry",
    "run-",
    "runtime-controller",
    "workflow-execution",
    "workflow-loop",
)
S0_PREFIXES = (
    "badges/",
    "docs/README.",
)
S0_EXACT = {
    "README.md",
    "CHANGELOG.md",
    "CODE_OF_CONDUCT.md",
}


class ImpactError(ValueError):
    """A fail-closed change-impact input or policy error."""


def _load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ImpactError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc
    if not isinstance(value, dict):
        raise ImpactError("%s must contain an object" % path.relative_to(ROOT))
    return value


def load_policy(root: Path = ROOT) -> dict:
    path = root / "evals" / "change-impact.json"
    value = _load_json(path)
    if set(value) != {"schema_version", "unmatched_policy", "rules"}:
        raise ImpactError("evals/change-impact.json has invalid top-level fields")
    if value["schema_version"] != "1.1" or value["unmatched_policy"] != "smoke-only":
        raise ImpactError("evals/change-impact.json has unsupported policy/version")
    if not isinstance(value["rules"], list) or not value["rules"]:
        raise ImpactError("evals/change-impact.json rules must be a non-empty list")
    for index, rule in enumerate(value["rules"]):
        if not isinstance(rule, dict) or set(rule) != {
            "id",
            "patterns",
            "selector",
            "severity",
        }:
            raise ImpactError("change-impact rule %d has invalid fields" % index)
        if rule["severity"] not in TIER_RANK:
            raise ImpactError("change-impact rule %d has invalid severity" % index)
        if not isinstance(rule["patterns"], list) or not rule["patterns"]:
            raise ImpactError("change-impact rule %d has no patterns" % index)
    return value


def _canonical_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ImpactError("changed path must be non-empty UTF-8 text")
    path = PurePosixPath(value)
    normalized = path.as_posix()
    if path.is_absolute() or normalized != value or "." in path.parts or ".." in path.parts:
        raise ImpactError("unsafe or non-canonical changed path: %r" % value)
    return normalized


def _catalog_sets(root: Path) -> tuple[set[str], set[str]]:
    value = _load_json(root / "references" / "system-catalog.json")
    skills: set[str] = set()
    disciplines = value.get("disciplines")
    if not isinstance(disciplines, dict):
        raise ImpactError("system catalog disciplines must be an object")
    for discipline, spec in disciplines.items():
        phases = spec.get("phases") if isinstance(spec, dict) else None
        if not isinstance(phases, dict):
            raise ImpactError("system catalog discipline %s has no phases" % discipline)
        for phase, slugs in phases.items():
            if not isinstance(slugs, list):
                raise ImpactError("system catalog phase %s/%s is invalid" % (discipline, phase))
            for slug in slugs:
                skills.add("%s/%s/%s/SKILL.md" % (discipline, phase, slug))
    protocol = value.get("protocol")
    protocol_skills = protocol.get("skills") if isinstance(protocol, dict) else None
    if not isinstance(protocol_skills, list):
        raise ImpactError("system catalog protocol skills are invalid")
    skills.update("protocol/%s/SKILL.md" % slug for slug in protocol_skills)
    if len(skills) != 120:
        raise ImpactError("system catalog must expose exactly 120 SKILL.md paths")
    auditor_specs = value.get("auditors")
    if not isinstance(auditor_specs, list):
        raise ImpactError("system catalog auditors must be a list")
    auditors = {
        spec["path"] + "/SKILL.md"
        for spec in auditor_specs
        if isinstance(spec, dict) and isinstance(spec.get("path"), str)
    }
    if len(auditors) != 8 or not auditors <= skills:
        raise ImpactError("system catalog must expose exactly eight canonical auditors")
    return skills, auditors


def _at_least(current: str, required: str) -> str:
    return required if TIER_RANK[required] > TIER_RANK[current] else current


def _hard_override(path: str, skill_paths: set[str], auditor_paths: set[str]) -> str | None:
    if path in S3_EXACT or path.startswith(S3_PREFIXES):
        return "S3"
    if path.startswith(S3_SCRIPT_PREFIXES):
        return "S3"
    if path in auditor_paths:
        return "S3"
    if path in {
        "protocol/consent-registry/SKILL.md",
        "protocol/offer-claims-registry/SKILL.md",
    }:
        return "S3"
    lowered = path.lower()
    if path.startswith("references/") and any(term in lowered for term in S3_REFERENCE_TERMS):
        return "S3"
    if path.startswith("scripts/") and (
        "controller" in lowered
        or "event" in lowered
        or "loop" in lowered
        or "permission" in lowered
        or "provenance" in lowered
    ):
        return "S3"
    if path.startswith(S0_PREFIXES) or path in S0_EXACT:
        return "S0"
    if path in skill_paths:
        return "S1"
    return None


def classify_paths(paths: list[str], root: Path = ROOT) -> dict:
    policy = load_policy(root)
    skill_paths, auditor_paths = _catalog_sets(root)
    results: list[dict] = []
    overall = "S0"
    for raw in sorted(set(paths)):
        path = _canonical_path(raw)
        matched_rules: list[str] = []
        tier = "S0"
        for rule in policy["rules"]:
            if any(fnmatch.fnmatchcase(path, pattern) for pattern in rule["patterns"]):
                matched_rules.append(rule["id"])
                tier = _at_least(tier, rule["severity"])
        override = _hard_override(path, skill_paths, auditor_paths)
        if override is not None:
            tier = _at_least(tier, override)
        elif not matched_rules:
            if (
                path.startswith(("scripts/", "hooks/", ".github/workflows/"))
                or path.endswith((".schema.json", ".yml", ".yaml"))
            ):
                tier = "S3"
            elif path.startswith(("references/", "evals/", ".claude-plugin/")):
                tier = "S2"
            elif path.endswith(".md"):
                tier = "S0"
            else:
                tier = "S2"
        overall = _at_least(overall, tier)
        results.append(
            {
                "path": path,
                "severity": tier,
                "matched_rules": matched_rules,
                "hard_override": override,
            }
        )
    changed_skills = sorted(path for path in paths if path in skill_paths)
    return {
        "schema_version": "1.0",
        "severity": overall,
        "changed_count": len(results),
        "changed_skills": changed_skills,
        "paths": results,
    }


def changed_paths_from_git(root: Path, base_ref: str, head_ref: str) -> list[str]:
    for label, reference in (("base", base_ref), ("head", head_ref)):
        if not reference or reference.startswith("-"):
            raise ImpactError("%s ref is invalid" % label)
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "--end-of-options", reference + "^{commit}"],
            cwd=root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            check=False,
        )
        if probe.returncode:
            raise ImpactError("%s ref does not resolve: %s" % (label, reference))
    process = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "-z",
            "--diff-filter=ACMRDT",
            base_ref,
            head_ref,
            "--",
        ],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode:
        raise ImpactError("git diff failed while classifying changes")
    try:
        return [
            _canonical_path(path)
            for path in process.stdout.decode("utf-8").split("\x00")
            if path
        ]
    except UnicodeDecodeError as exc:
        raise ImpactError("git emitted a non-UTF-8 path: %s" % exc) from None


def _write_github_output(path: Path, result: dict) -> None:
    payload = (
        "tier=%s\nchanged_count=%d\nchanged_skills=%s\n"
        % (
            result["severity"],
            result["changed_count"],
            json.dumps(result["changed_skills"], separators=(",", ":")),
        )
    )
    try:
        with path.open("a", encoding="utf-8") as handle:
            handle.write(payload)
    except OSError as exc:
        raise ImpactError("cannot append GitHub output: %s" % exc) from exc


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", default=[], help="Changed path; repeatable")
    parser.add_argument("--base-ref", help="Git base ref used when --path is omitted")
    parser.add_argument("--head-ref", default="HEAD")
    parser.add_argument("--json", action="store_true", help="Print the complete result as JSON")
    parser.add_argument("--github-output", type=Path, help="Append tier outputs for GitHub Actions")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.path and args.base_ref:
            raise ImpactError("--path and --base-ref are mutually exclusive")
        if not args.path and not args.base_ref:
            raise ImpactError("provide --path or --base-ref")
        paths = args.path or changed_paths_from_git(ROOT, args.base_ref, args.head_ref)
        result = classify_paths(paths)
        if args.github_output:
            _write_github_output(args.github_output, result)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(result["severity"])
        return 0
    except ImpactError as exc:
        print("change-impact error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
