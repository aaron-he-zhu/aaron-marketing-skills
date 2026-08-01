#!/usr/bin/env python3
"""Run randomized explicit-vs-compact protocol-v3 paired ablations."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import uuid


ROOT = Path(__file__).resolve().parents[1]


def _load(name, relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load %s" % relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


behavior = _load("ablation_behavior_runner", "scripts/run-behavior-evals.py")
planner = _load("ablation_context_planner", "scripts/context-plan.py")
resolver = _load("ablation_context_resolver", "scripts/context-resolver.py")
assembly_runtime = _load("ablation_context_assembly", "scripts/context-assembly.py")
evidence_runtime = _load("ablation_prompt_evidence", "scripts/prompt_profile_evidence.py")


class AblationError(ValueError):
    pass


def _assembly_binding(assembly):
    assembly_runtime.validate_assembly(assembly)
    resources = sorted([
        {
            "ref": item["path"],
            "sha256": item["sha256"],
            "bytes": item["body_bytes"],
            "role": item["role"],
        }
        for item in assembly["consumers"]["model"] if item["body_bytes"] > 0
    ], key=lambda item: (item["ref"], item["role"]))
    if not resources or len({item["ref"] for item in resources}) != len(resources):
        raise AblationError("assembly model resources are empty or non-unique")
    prompt, catalogs = evidence_runtime.current_catalog_state(ROOT)
    del prompt
    binding = {
        "assembly_sha256": evidence_runtime.sha256_json(assembly),
        "assembly_signature": assembly["assembly_signature"],
        "context_signature": assembly["context_signature"],
        "host_catalog_sha256": catalogs["host_catalog_sha256"],
        "prompt_policy_sha256": catalogs["prompt_policy_sha256"],
        "context_modules_sha256": catalogs["context_modules_sha256"],
        "model_body_bytes": assembly["usage"]["model_body_bytes"],
        "model_reduction_ratio": assembly["usage"]["model_reduction_ratio"],
        "model_resources": resources,
        "model_resources_sha256": evidence_runtime.sha256_json(resources),
    }
    behavior.validate_v3_assembly_binding(binding)
    return binding


def _case_assemblies(case, *, pair_id, context_as_of, empty_project, host_profile,
                     model_id, candidate_profile):
    context_run_id = str(uuid.uuid4())
    turn_id = "pair-" + hashlib.sha256(pair_id.encode("utf-8")).hexdigest()[:24]
    contract, _raw, _entry, _index, _index_raw = planner._load_contract(
        ROOT, case["target_skill"],
    )
    direct_command = (
        "auto" if contract["identity"]["discipline"] == "protocol"
        else contract["identity"]["discipline"]
    )
    host_catalog = json.loads(
        (ROOT / "references/host-capability-profiles.json").read_text(encoding="utf-8")
    )
    host = host_catalog["profiles"].get(host_profile)
    if not isinstance(host, dict):
        raise AblationError("ablation host profile is absent from the current catalog")
    compatible = set(host.get("compatible_distributions", []))
    if compatible == {"standalone-skill"}:
        distribution_profile = "standalone-skill"
    elif compatible <= {"repository", "plugin"} and compatible:
        distribution_profile = (
            "plugin" if (ROOT / "distribution-manifest.json").exists() else "repository"
        )
    else:
        raise AblationError("ablation host has no supported planner distribution")
    request = planner.build_request(
        skill=case["target_skill"],
        run_id=context_run_id,
        turn_id=turn_id,
        as_of=context_as_of,
        project_root=empty_project,
        bundle_root=ROOT,
        command=direct_command,
        distribution_profile=distribution_profile,
        post_route=True,
    )
    manifest = resolver.resolve_context(request, ROOT, empty_project)
    explicit = assembly_runtime.build_assembly(
        manifest,
        bundle_root=ROOT,
        project_root=empty_project,
        host_profile=host_profile,
        model_id=model_id,
        requested_prompt_profile="explicit",
        as_of=context_as_of,
    )
    compact = assembly_runtime.build_assembly(
        manifest,
        bundle_root=ROOT,
        project_root=empty_project,
        host_profile=host_profile,
        model_id=model_id,
        evaluation_prompt_profile=candidate_profile,
        evaluation_run_id="ablation-" + hashlib.sha256(
            pair_id.encode("utf-8")
        ).hexdigest()[:32],
        as_of=context_as_of,
    )
    return {
        "control": _assembly_binding(explicit),
        "candidate": _assembly_binding(compact),
    }


def _run_arm(
        case, selection, *, role, profile, binding, adapter_command,
        adapter_implementation_ref, host_profile, model_id, judge_model_id,
        toolset_id, toolset_sha256, timeout, evidence_root):
    arm_selection = {
        "profile": selection["profile"],
        "cases": [case],
        "case_ids": [case["id"]],
        "selection_reasons": {
            case["id"]: list(selection["selection_reasons"][case["id"]])
        },
        "provenance": dict(selection["provenance"]),
    }
    run_id = str(uuid.uuid4())
    failures = behavior.run_adapter_v3(
        adapter_command,
        arm_selection,
        timeout,
        host_profile=host_profile,
        model_id=model_id,
        judge_model_id=judge_model_id,
        prompt_profile=profile,
        evaluation_only=(role == "candidate"),
        toolset_id=toolset_id,
        toolset_sha256=toolset_sha256,
        required_execution_mode="real",
        batch_size=1,
        evidence_run_id=run_id,
        evidence_root=Path(evidence_root),
        adapter_implementation_ref=adapter_implementation_ref,
        assembly_bindings={case["id"]: binding},
    )
    # Behavioral failures are experimental observations, not orchestration
    # exceptions. The validated result stream remains authoritative.
    del failures
    captured = evidence_runtime.capture_semantic_run(evidence_root, run_id)
    return evidence_runtime.arm_from_result(
        captured["result"], captured["request"], captured["provenance"],
        validation_token=captured["validation_token"],
    ), captured["result"]


def _write_json(path, value):
    raw = json.dumps(
        value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True
    ) + "\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(raw, encoding="utf-8")


def _pair_case_projection(case):
    """Bind evidence identity to a verifier-derived, model-invisible stratum."""
    return {
        "case_id": case["id"],
        "case_sha256": case["case_sha256"],
        "case_provenance": case["case_provenance"],
        "evidence_binding": case["evidence_binding"],
        "source_group": case["source_group"],
        "source_ref": case["source_ref"],
        "source_line": case["source_line"],
        "target_skill": case["target_skill"],
        "coverage_stratum": evidence_runtime.authoritative_coverage_stratum(
            case, ROOT
        ),
    }


def _release_model_identity(observed_results, model_id, judge_model_id):
    """Require one immutable, independent SUT/judge identity across all arms."""
    if model_id == judge_model_id:
        raise AblationError(
            "release ablation requires an independent judge model distinct from the SUT"
        )
    if not isinstance(observed_results, list) or not observed_results:
        raise AblationError("release ablation has no observed execution provenance")
    try:
        rows = [result["execution_provenance"] for result in observed_results]
        first = rows[0]
        identity_keys = (
            "host_name", "host_version", "model_provider", "model_id",
            "model_revision", "judge_model_provider", "judge_model_id",
            "judge_model_revision",
        )
        if any(row[key] != first[key] for row in rows for key in identity_keys):
            raise AblationError(
                "host/SUT/judge provenance changed within the paired run; "
                "moving model aliases or revisions cannot certify"
            )
    except (KeyError, TypeError, IndexError) as exc:
        raise AblationError(
            "release ablation lacks complete SUT/judge execution provenance"
        ) from exc
    if first["model_id"] != model_id or first["judge_model_id"] != judge_model_id:
        raise AblationError("observed SUT/judge identities differ from ablation inputs")
    for key in ("model_provider", "judge_model_provider"):
        if not isinstance(first[key], str) or not first[key]:
            raise AblationError("release ablation requires explicit provider identities")
    for key in ("model_revision", "judge_model_revision"):
        if not isinstance(first[key], str) or not first[key]:
            raise AblationError(
                "release ablation requires immutable SUT and judge revisions; "
                "moving aliases and null revisions cannot certify"
            )
    if (
            first["model_provider"] == first["judge_model_provider"]
            and first["model_revision"] == first["judge_model_revision"]):
        raise AblationError(
            "release ablation SUT and judge share one immutable provider revision"
        )
    return {
        "provider": first["model_provider"],
        "model_id": first["model_id"],
        "model_revision": first["model_revision"],
        "judge_provider": first["judge_model_provider"],
        "judge_model_id": first["judge_model_id"],
        "judge_model_revision": first["judge_model_revision"],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter-command", required=True)
    parser.add_argument("--adapter-implementation-ref", required=True)
    parser.add_argument("--host-profile", required=True)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--judge-model-id", required=True)
    parser.add_argument("--candidate-profile", choices=("balanced", "lean"), required=True)
    parser.add_argument("--toolset-id", default="read-only-no-tools-v1")
    parser.add_argument("--toolset-sha256")
    parser.add_argument("--profile", choices=("smoke", "change-aware", "nightly"), default="nightly")
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--seed", required=True, help="operator-provided randomization seed")
    parser.add_argument("--context-as-of", required=True)
    parser.add_argument("--adapter-timeout", type=int, default=1800)
    parser.add_argument("--evidence-root", default=str(ROOT))
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    if not 2 <= args.repeats <= 20:
        parser.error("--repeats must be 2..20")
    if not 1 <= args.adapter_timeout <= 7200:
        parser.error("--adapter-timeout must be 1..7200")
    if Path(args.evidence_root).resolve() != ROOT:
        parser.error(
            "release ablations require --evidence-root to be the repository root "
            "so promotion can re-verify stored run provenance"
        )

    selection = behavior.select_semantic_cases(args.profile, set(args.case))
    prompt_policy, unused_catalogs = evidence_runtime.current_catalog_state(ROOT)
    del unused_catalogs
    policy = prompt_policy["certification_policy"]
    nonreal = [
        case["id"] for case in selection["cases"]
        if case["case_provenance"] != "real" or not case["evidence_binding"]
    ]
    if nonreal:
        raise AblationError(
            "release ablation requires canonical evidence-bound real cases; "
            "%d selected case(s) are simulated" % len(nonreal)
        )
    if len(selection["cases"]) < policy["minimum_cases"]:
        raise AblationError("release ablation case coverage is below certification policy")
    if args.repeats < policy["minimum_repeats"]:
        raise AblationError("release ablation repeat count is below certification policy")
    seed_sha256 = hashlib.sha256(args.seed.encode("utf-8")).hexdigest()
    toolset_sha256 = args.toolset_sha256 or behavior.sha256_json({
        "toolset_id": args.toolset_id
    })
    created = datetime.now(timezone.utc)
    pairs = []
    observed_results = []
    with tempfile.TemporaryDirectory(prefix="prompt-ablation-empty-project-") as project:
        empty_project = Path(project)
        for case in selection["cases"]:
            for repeat in range(1, args.repeats + 1):
                pair_id = "%s-r%d" % (case["id"], repeat)
                bindings = _case_assemblies(
                    case, pair_id=pair_id, context_as_of=args.context_as_of,
                    empty_project=empty_project, host_profile=args.host_profile,
                    model_id=args.model_id, candidate_profile=args.candidate_profile,
                )
                order = evidence_runtime.deterministic_pair_order(seed_sha256, pair_id)
                arms = {}
                for role in order:
                    profile = "explicit" if role == "control" else args.candidate_profile
                    arms[role], result = _run_arm(
                        case, selection, role=role, profile=profile,
                        binding=bindings[role], adapter_command=args.adapter_command,
                        adapter_implementation_ref=args.adapter_implementation_ref,
                        host_profile=args.host_profile, model_id=args.model_id,
                        judge_model_id=args.judge_model_id,
                        toolset_id=args.toolset_id, toolset_sha256=toolset_sha256,
                        timeout=args.adapter_timeout, evidence_root=args.evidence_root,
                    )
                    observed_results.append(result)
                pairs.append({
                    "pair_id": pair_id,
                    **_pair_case_projection(case),
                    "repeat_index": repeat,
                    "order": order,
                    "invariant": {
                        "host_profile": args.host_profile,
                        "model_id": args.model_id,
                        "judge_model_id": args.judge_model_id,
                        "toolset_id": args.toolset_id,
                        "toolset_sha256": toolset_sha256,
                    },
                    "arms": arms,
                })
    completed = datetime.now(timezone.utc)
    first = observed_results[0]["execution_provenance"]
    model_identity = _release_model_identity(
        observed_results, args.model_id, args.judge_model_id
    )
    prompt, catalogs = evidence_runtime.current_catalog_state(ROOT)
    evaluated = completed
    latest_actual_completion = max(
        evidence_runtime.parse_datetime(
            result["execution_provenance"]["ended_at"], "arm ended_at"
        )
        for result in observed_results
    )
    expires = latest_actual_completion + timedelta(
        days=prompt["certification_policy"]["maximum_age_days"]
    )
    document = {
        "$schema": "../prompt-profile-paired-evidence.schema.json",
        "schema_version": "1.0", "kind": "prompt-profile-paired-evidence",
        "protocol_version": "3.0", "evidence_id": "ablation-%s" % str(uuid.uuid4()),
        "run_id": str(uuid.uuid4()),
        "created_at": evidence_runtime.format_datetime(created),
        "completed_at": evidence_runtime.format_datetime(completed),
        "evaluated_at": evidence_runtime.format_datetime(evaluated),
        "expires_at": evidence_runtime.format_datetime(expires),
        "distribution_profile": "governed",
        "host": {"host_profile": args.host_profile, "host_name": first["host_name"],
                 "host_version": first["host_version"]},
        "model": model_identity,
        "toolset": {"toolset_id": args.toolset_id, "toolset_sha256": toolset_sha256},
        "profiles": {"control": "explicit", "candidate": args.candidate_profile},
        "catalogs": catalogs,
        "design": {"randomization": "seeded-within-pair-v1", "seed_sha256": seed_sha256,
                   "repeats": args.repeats, "case_count": len(selection["cases"]),
                   "pair_count": len(pairs),
                   "coverage_strata": sorted({
                       item["coverage_stratum"] for item in pairs
                   })},
        "pairs": pairs,
        "policy_snapshot": prompt["certification_policy"],
        "aggregate": {}, "decision": {},
    }
    document = evidence_runtime.finalize_document(
        document, as_of=document["evaluated_at"], bundle_root=ROOT
    )
    evidence_runtime.validate_evidence(
        document, bundle_root=ROOT, as_of=document["evaluated_at"]
    )
    _write_json(args.output, document)
    print(json.dumps({
        "output": args.output,
        "case_count": document["aggregate"]["case_count"],
        "pair_count": document["aggregate"]["pair_count"],
        "valid": document["decision"]["valid"],
        "reasons": document["decision"]["reasons"],
        "evidence_scope": document["decision"]["evidence_scope"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
