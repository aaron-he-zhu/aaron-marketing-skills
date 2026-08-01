#!/usr/bin/env python3
"""Measure actual planner/resolver assemblies for every skill and route.

Unlike the single-file budget guard, this checker executes the live
``context-plan`` and ``context-resolver`` APIs against an empty project root.
It therefore measures the same required/selected resources, de-duplication,
conditions, and inspection limits that a governed run would use.  Run it from
a normal checkout or through ``scripts/run-isolated-evals.py`` when the source
worktree is sync-backed and hard-linked.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "references" / "skill-contracts" / "index.json"
CATALOG = ROOT / "references" / "system-catalog.json"
PLANNER_PATH = ROOT / "scripts" / "context-plan.py"
RESOLVER_PATH = ROOT / "scripts" / "context-resolver.py"
POLICY_PATH = ROOT / "evals" / "context-efficiency-policy.json"
FIXED_RUN_ID = "00000000-0000-4000-8000-000000000001"
DEFAULT_AS_OF = "2026-08-01T00:00:00Z"
CONTROL_ROLES = {"skill-contract"}


class EfficiencyError(ValueError):
    pass


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise EfficiencyError("cannot load %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_json(path, label):
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError) as exc:
        raise EfficiencyError("cannot load %s: %s" % (label, exc)) from exc


def _sha256_path(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as exc:
        raise EfficiencyError("cannot hash %s: %s" % (path, exc)) from exc


def _percentile(values, fraction):
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(len(ordered) * fraction + 0.999999) - 1))
    return ordered[index]


def _summary(records):
    result = {}
    for route_kind in ("direct", "auto"):
        rows = [record for record in records if record["route_kind"] == route_kind]
        metrics = {}
        for field in ("required_bytes", "selected_bytes", "inspection_bytes"):
            values = [row[field] for row in rows]
            metrics[field] = {
                "p50": _percentile(values, 0.50),
                "p90": _percentile(values, 0.90),
                "p95": _percentile(values, 0.95),
                "max": max(values),
            }
        worst_required = max(rows, key=lambda row: row["required_bytes"])
        worst_selected = max(rows, key=lambda row: row["selected_bytes"])
        result[route_kind] = {
            "records": len(rows),
            **metrics,
            "worst_required": {
                "target_skill": worst_required["target_skill"],
                "distribution_profile": worst_required["distribution_profile"],
                "bytes": worst_required["required_bytes"],
                "budget_share": worst_required["required_budget_share"],
            },
            "worst_selected": {
                "target_skill": worst_selected["target_skill"],
                "distribution_profile": worst_selected["distribution_profile"],
                "bytes": worst_selected["selected_bytes"],
                "budget_share": worst_selected["selected_budget_share"],
            },
        }
    return result


def _discovery_metrics(index):
    description_bytes = 0
    when_to_use_bytes = 0
    trigger_bytes = 0
    for entry in index["contracts"]:
        contract = _load_json(ROOT / entry["contract_ref"], entry["contract_ref"])
        routing = contract["routing_contract"]
        description_bytes += len(routing["description"].encode("utf-8"))
        when_to_use_bytes += len(routing["when_to_use"].encode("utf-8"))
        trigger_bytes += sum(
            len(item.encode("utf-8")) for item in routing["trigger_phrases"]
        )
    return {
        "skills": len(index["contracts"]),
        "description_bytes": description_bytes,
        "when_to_use_bytes": when_to_use_bytes,
        "description_plus_when_to_use_bytes": description_bytes + when_to_use_bytes,
        "trigger_phrase_bytes": trigger_bytes,
    }


def _group_bytes(resources, field):
    totals = {}
    for resource in resources:
        key = resource[field]
        totals[key] = totals.get(key, 0) + resource["bytes"]
    return {key: totals[key] for key in sorted(totals)}


def measure(*, as_of=DEFAULT_AS_OF, distribution_profiles=("repository",)):
    planner = _load_module("aaron_efficiency_context_plan", PLANNER_PATH)
    resolver = planner.resolver
    index = _load_json(INDEX, "skill contract index")
    skills = [entry["skill"] for entry in index["contracts"]]
    if len(skills) != 120 or len(set(skills)) != 120:
        raise EfficiencyError("skill contract index must contain 120 unique skills")
    supported_profiles = set(getattr(resolver, "DISTRIBUTION_PROFILES", {"repository"}))
    unknown_profiles = sorted(set(distribution_profiles) - supported_profiles)
    if unknown_profiles:
        raise EfficiencyError(
            "unsupported distribution profile(s): %s" % ", ".join(unknown_profiles)
        )
    supports_profile = "distribution_profile" in inspect.signature(
        planner.build_request
    ).parameters
    if set(distribution_profiles) != {"repository"} and not supports_profile:
        raise EfficiencyError("planner does not expose distribution_profile")
    records = []
    with tempfile.TemporaryDirectory(prefix="aaron-context-efficiency-project-") as temporary:
        project_root = Path(temporary)
        for skill_index, skill in enumerate(skills):
            contract, _raw, _entry, _index, _index_raw = planner._load_contract(ROOT, skill)
            # Protocol skills have no standalone discipline command in the
            # route contract; their normal/native entry is `/auto`.  Keep one
            # row in each 120-skill cohort for distribution comparability while
            # preserving the resolver's real route constraint.
            direct_command = (
                "auto" if contract["identity"]["discipline"] == "protocol"
                else planner._primary_discipline(contract)
            )
            for distribution_profile in distribution_profiles:
                for route_offset, (route_kind, command) in enumerate(
                        (("direct", direct_command), ("auto", "auto"))):
                    kwargs = {
                        "skill": skill,
                        "run_id": FIXED_RUN_ID,
                        "turn_id": "baseline-%03d-%s-%s" % (
                            skill_index + 1, route_kind, distribution_profile,
                        ),
                        "as_of": as_of,
                        "project_root": project_root,
                        "bundle_root": ROOT,
                        "command": command,
                    }
                    if supports_profile:
                        kwargs["distribution_profile"] = distribution_profile
                    try:
                        request = planner.build_request(**kwargs)
                        manifest = resolver.resolve_context(request, ROOT, project_root)
                    except Exception as exc:
                        message = str(exc)
                        if "single-link" in message or "hard" in message.lower():
                            raise EfficiencyError(
                                "bundle cannot be measured in place because a source is multiply "
                                "linked; run `python3 scripts/run-isolated-evals.py -- "
                                "--suite context-efficiency`"
                            ) from exc
                        raise EfficiencyError(
                            "%s/%s/%s assembly failed: %s"
                            % (skill, distribution_profile, route_kind, exc)
                        ) from exc
                    resources = manifest["resources"]
                    required_bytes = sum(
                        resource["bytes"] for resource in resources
                        if resource["requirement"] == "required"
                    )
                    selected_bytes = manifest["budget"]["selected_bytes"]
                    capacity = manifest["budget"]["max_bytes"]
                    control_bytes = sum(
                        resource["bytes"] for resource in resources
                        if resource["role"] in CONTROL_ROLES
                    )
                    records.append({
                        "target_skill": skill,
                        "discipline": contract["identity"]["discipline"],
                        "phase": contract["identity"]["phase"],
                        "route_kind": route_kind,
                        "command": command,
                        "distribution_profile": distribution_profile,
                        "candidate_resources": len(request["candidates"]),
                        "required_resources": sum(
                            resource["requirement"] == "required" for resource in resources
                        ),
                        "selected_resources": manifest["budget"]["selected_resources"],
                        "omitted_resources": len(manifest["omitted"]),
                        "capacity_bytes": capacity,
                        "required_bytes": required_bytes,
                        "selected_bytes": selected_bytes,
                        "inspection_bytes": manifest["budget"]["inspected_bytes"],
                        "control_plane_role_bytes": control_bytes,
                        "required_budget_share": round(required_bytes / capacity, 6),
                        "selected_budget_share": round(selected_bytes / capacity, 6),
                        "remaining_budget_bytes": capacity - selected_bytes,
                        "bytes_by_role": _group_bytes(resources, "role"),
                        "bytes_by_reason": _group_bytes(resources, "reason_code"),
                    })
    output = {
        "schema_version": "1.0",
        "generated_at": as_of,
        "method": {
            "name": "live-planner-resolver-empty-project-v1",
            "project_fixture": "empty-directory",
            "routes_per_skill": ["direct", "auto"],
            "direct_route_note": (
                "Direct means the normal entry command; protocol skills use auto because "
                "the catalog exposes no protocol discipline command."
            ),
            "distribution_profiles": list(distribution_profiles),
            "token_estimate": None,
            "note": (
                "Bytes are actual selected assemblies. model-visible versus control-plane "
                "consumers remain separate telemetry fields and are not inferred here."
            ),
        },
        "source": {
            "system_catalog_sha256": _sha256_path(CATALOG),
            "contract_index_sha256": _sha256_path(INDEX),
            "planner_sha256": _sha256_path(PLANNER_PATH),
            "resolver_sha256": _sha256_path(RESOLVER_PATH),
        },
        "discovery": _discovery_metrics(index),
        "summary": _summary(records),
        "records": records,
    }
    return output


def evaluate_policy(report, policy):
    if set(policy) != {
            "schema_version", "guardrails", "targets", "description"}:
        raise EfficiencyError("context efficiency policy fields are invalid")
    if policy["schema_version"] != "1.0":
        raise EfficiencyError("context efficiency policy schema_version must be 1.0")
    guardrails = policy["guardrails"]
    required_fields = {
        "max_required_bytes", "max_required_budget_share", "max_p50_selected_bytes",
        "max_description_plus_when_to_use_bytes",
    }
    if not isinstance(guardrails, dict) or set(guardrails) != required_fields:
        raise EfficiencyError("context efficiency guardrail fields are invalid")
    failures = []
    max_required = max(row["required_bytes"] for row in report["records"])
    max_required_share = max(row["required_budget_share"] for row in report["records"])
    p50_selected = max(
        report["summary"][route]["selected_bytes"]["p50"] for route in ("direct", "auto")
    )
    discovery = report["discovery"]["description_plus_when_to_use_bytes"]
    checks = (
        (max_required <= guardrails["max_required_bytes"],
         "max required bytes %d exceeds %d" % (max_required, guardrails["max_required_bytes"])),
        (max_required_share <= guardrails["max_required_budget_share"],
         "max required budget share %.3f exceeds %.3f" % (
             max_required_share, guardrails["max_required_budget_share"])),
        (p50_selected <= guardrails["max_p50_selected_bytes"],
         "largest route p50 selected bytes %d exceeds %d" % (
             p50_selected, guardrails["max_p50_selected_bytes"])),
        (discovery <= guardrails["max_description_plus_when_to_use_bytes"],
         "description + when_to_use bytes %d exceeds %d" % (
             discovery, guardrails["max_description_plus_when_to_use_bytes"])),
    )
    failures.extend(message for passed, message in checks if not passed)
    return failures


def write_json(value, output):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, indent=2) + "\n"
    if output == "-":
        sys.stdout.write(text)
    else:
        Path(output).write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=DEFAULT_AS_OF)
    parser.add_argument(
        "--distribution-profile", action="append", dest="profiles",
        help="repeat to measure more than one profile (default: repository)",
    )
    parser.add_argument("--json", action="store_true", help="emit the complete report as JSON")
    parser.add_argument("--output", default="-", help="JSON output path; default stdout")
    parser.add_argument(
        "--policy", default=str(POLICY_PATH),
        help="guardrail/target policy used by --check",
    )
    parser.add_argument("--check", action="store_true", help="enforce policy guardrails")
    args = parser.parse_args(argv)
    try:
        profiles = tuple(args.profiles or ["repository"])
        if len(profiles) != len(set(profiles)):
            raise EfficiencyError("distribution profiles must be unique")
        report = measure(as_of=args.as_of, distribution_profiles=profiles)
        failures = []
        if args.check:
            failures = evaluate_policy(
                report, _load_json(args.policy, "context efficiency policy"),
            )
        if args.json:
            write_json(report, args.output)
        else:
            for route in ("direct", "auto"):
                summary = report["summary"][route]
                print(
                    "%s: required p50=%d p95=%d max=%d; selected p50=%d p95=%d max=%d"
                    % (
                        route,
                        summary["required_bytes"]["p50"],
                        summary["required_bytes"]["p95"],
                        summary["required_bytes"]["max"],
                        summary["selected_bytes"]["p50"],
                        summary["selected_bytes"]["p95"],
                        summary["selected_bytes"]["max"],
                    )
                )
            print(
                "discovery: description=%d bytes; description+when_to_use=%d bytes"
                % (
                    report["discovery"]["description_bytes"],
                    report["discovery"]["description_plus_when_to_use_bytes"],
                )
            )
        if failures:
            for failure in failures:
                print("FAIL  " + failure, file=sys.stderr if args.json else sys.stdout)
            print(
                "CONTEXT EFFICIENCY FAILED — %d issue(s)." % len(failures),
                file=sys.stderr if args.json else sys.stdout,
            )
            return 1
        if args.check and not args.json:
            print("Context efficiency guardrails passed for %d assemblies." % len(report["records"]))
        return 0
    except (EfficiencyError, OSError, ValueError) as exc:
        message = str(exc)
        if "single-link" in message or "multiply linked" in message:
            message += (
                "; run `python3 scripts/run-isolated-evals.py -- "
                "--suite context-efficiency` for a sync-backed worktree"
            )
        print("context-efficiency: %s" % message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
