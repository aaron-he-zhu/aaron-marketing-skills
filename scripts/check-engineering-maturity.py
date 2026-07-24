#!/usr/bin/env python3
"""Execute the five-dimension engineering maturity acceptance contract.

The checker awards only binary, repository-observable controls from
``references/engineering-maturity-rubric.json``. Static controls inspect the
current artifacts and hashes; dynamic/execution controls run their registered
test suites; real-provider controls require a private protocol-v2 evidence UUID
that passes the current-source verifier. A failed hard gate caps its dimension
below the 95/100 target regardless of the raw point total.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
RUBRIC_PATH = ROOT / "references" / "engineering-maturity-rubric.json"
EXPECTED_DIMENSIONS = {"prompt", "context", "harness", "loop", "graph"}
REPORT_SCHEMA = "references/engineering-maturity-report.schema.json"


class MaturityError(ValueError):
    pass


@dataclass(frozen=True)
class Fact:
    passed: bool
    evidence: str


@dataclass(frozen=True)
class CommandEvidence:
    passed: bool
    summary: str


P18_RUNNER_SYMBOLS = (
    "load_skill_machine_contracts",
    "auto_routing_source_refs",
)
P18_SEMANTIC_REQUEST_TESTS = (
    "test_v2_authored_case_consumes_machine_contract_and_runtime_context",
    "test_auto_routing_case_binds_router_and_primary_command_without_case_corpus",
    "test_nightly_700_requests_are_constructible_with_bounded_refs",
    "test_memory_management_auto_requests_bind_seo_command_without_case_corpus",
    "test_prompt_source_expansion_rejects_33_unique_refs",
)
P18_CODEX_ADAPTER_TESTS = (
    "test_true_two_stage_execution_isolated_and_provenance_bound",
    "test_derived_contract_assertions_are_not_visible_to_sut",
    "test_single_reference_over_byte_limit_fails_before_model_calls",
    "test_aggregate_bound_sources_over_byte_limit_fails_before_model_calls",
)
H17_COMMON_SYMBOLS = (
    "publish_require_release_identity",
    "publish_require_expected_release_identity",
    "publish_prepare_release_source",
    "publish_parse_github_slug",
)
H17_PUBLISHER_WIRING = {
    "publish-clawhub.sh": ('publish_prepare_release_source "$SOURCE_ROOT"',),
    "publish-skillhub.sh": ('publish_prepare_release_source "$SOURCE_ROOT"',),
    "publish-package.sh": ('RELEASE_IDENTITY="$(publish_require_release_identity)"',),
    "publish-registries.sh": (
        'RELEASE_IDENTITY="$(publish_require_release_identity)"',
        'AARON_PUBLISH_EXPECTED_REPO="$REPO_SLUG"',
        'AARON_PUBLISH_EXPECTED_COMMIT="$head_commit"',
    ),
}
H17_PUBLISHER_TESTS = (
    "test_every_release_live_entrypoint_rejects_dirty_source_before_mutation",
    "test_every_release_live_entrypoint_rejects_github_host_spoofing",
    "test_every_release_live_entrypoint_consumes_one_identity_snapshot",
    "test_registry_orchestrator_rejects_child_origin_switch",
    "test_release_identity_rejects_origin_switch_inside_gate",
    "test_live_provenance_rejects_git_url_rewrites",
    "test_sync_about_live_uses_pinned_ssot_after_gate_race",
    "test_sync_family_live_uses_pinned_plugin_and_references_after_gate_race",
)
H19_ADAPTER_SYMBOLS = (
    "build_judge_retry_prompt",
    "parse_and_validate_judge_output",
    "judge_attempt_record",
    "combined_response_sha256",
)
H19_ADAPTER_MARKERS = (
    "MAX_JUDGE_ATTEMPTS = 2",
    "JUDGE_DIAGNOSTIC_CODES = {",
    "JUDGE_PROTOCOL_RETRY_TEMPLATE =",
    '"judge_protocol_retry": JUDGE_PROTOCOL_RETRY_TEMPLATE',
    '"judge_protocol_max_attempts": MAX_JUDGE_ATTEMPTS',
    '"judge_protocol_retry_policy": "full-regeneration-no-rejected-raw-v1"',
    "for attempt in range(1, MAX_JUDGE_ATTEMPTS + 1):",
    'judge_project = case_root / ("judge-project-%d" % attempt)',
    'judge_output = outputs / ("judge-%d.json" % attempt)',
    '"response_sha256": sha256_bytes(rejected_response)',
    '"size_bytes": len(rejected_response)',
    '"judge_attempts": attempts',
    '"response_sha256": combined_response_sha256(candidate_response, attempts)',
)
H19_RUNNER_MARKERS = (
    "JUDGE_ATTEMPT_KEYS = {",
    "JUDGE_DIAGNOSTIC_CODES = {",
    'judge_attempts = execution["judge_attempts"]',
    "execution_provenance.judge_response_sha256 does not bind the last judge attempt",
    "execution_provenance.response_sha256 does not bind the full judge ledger",
    "terminal judge outcome requires exactly one accepted final attempt",
    "accepted judge attempt cannot be empty",
)
H19_VERIFIER_MARKERS = (
    "total_judge_attempts = sum(",
    "retried_cases = sum(",
    "judge_protocol_retries = sum(",
    '"total_judge_attempts": total_judge_attempts',
    '"retried_cases": retried_cases',
    '"judge_protocol_retries": judge_protocol_retries',
)
H19_BEHAVIOR_EVAL_TESTS = (
    "test_official_adapter_bootstrap_ignores_pythonpath_sitecustomize",
    "test_official_adapter_schema_source_swap_cannot_reach_staged_runtime",
    "test_v2_judge_ledger_tamper_fails_closed",
    "test_v2_terminal_outcome_requires_accepted_final_attempt",
    "test_v2_accepted_judge_attempt_cannot_be_empty",
)
H19_CODEX_ADAPTER_TESTS = (
    "test_true_two_stage_execution_isolated_and_provenance_bound",
    "test_invalid_judge_protocol_is_retried_once_without_rerunning_candidate",
    "test_locally_invalid_judge_shape_is_retried_once",
    "test_two_invalid_judge_protocol_attempts_fail_closed",
    "test_valid_behavior_failure_and_inconclusive_are_not_retried",
    "test_judge_schema_rejection_is_terminal_without_regeneration",
    "test_judge_retry_policy_is_hard_bounded_and_hash_bound",
)
H19_VERIFIER_TESTS = (
    "test_complete_current_real_evidence_passes",
)
H19_VERIFIER_TEST_MARKERS = (
    'self.assertEqual(24, result["total_judge_attempts"])',
    'self.assertEqual(0, result["retried_cases"])',
    'self.assertEqual(0, result["judge_protocol_retries"])',
)


def p18_fact(semantic_request_suite, semantic_runner_text,
             semantic_request_tests, codex_adapter_tests):
    missing = []
    if not semantic_request_suite.passed:
        missing.append("semantic_request_suite")
    for symbol in P18_RUNNER_SYMBOLS:
        if "def %s(" % symbol not in semantic_runner_text:
            missing.append("runner:%s" % symbol)
    for test_name in P18_SEMANTIC_REQUEST_TESTS:
        if "def %s(" % test_name not in semantic_request_tests:
            missing.append("semantic-test:%s" % test_name)
    for test_name in P18_CODEX_ADAPTER_TESTS:
        if "def %s(" % test_name not in codex_adapter_tests:
            missing.append("adapter-test:%s" % test_name)
    if missing:
        return Fact(
            False,
            "P18 semantic machine/router context, nightly/ref-bound, or assertion-isolation "
            "proof is missing: %s" % ", ".join(missing),
        )
    return Fact(
        True,
        "semantic_request_suite proves all 700 nightly requests bind 1..32 current refs; "
        "memory-management auto cases bind commands/seo-geo.md without eval/routing "
        "corpora; 33 refs and per-ref/aggregate byte overflow fail closed before model "
        "execution; machine, auto-router, and assertion-isolation tests pass",
    )


def h17_fact(harness_suite, publishers, common_publish, sync_about,
             sync_family, publisher_tests):
    missing = []
    if not harness_suite.passed:
        missing.append("harness_suite")
    if not publishers:
        missing.append("publisher_entrypoints")
    elif not all(
            path == "publish-common.sh"
            or "publish-common.sh" in text or "publish_release_source" in text
            for path, text in publishers):
        missing.append("shared_provenance_import")
    for symbol in H17_COMMON_SYMBOLS:
        if "%s()" % symbol not in common_publish:
            missing.append("common:%s" % symbol)
    if "git fetch -q -- \"$remote\"" not in common_publish:
        missing.append("validated_literal_origin_fetch")
    if "origin or Git URL rewrites changed during the release gate" not in common_publish:
        missing.append("post_fetch_identity_recheck")
    publisher_map = dict(publishers)
    for path, markers in H17_PUBLISHER_WIRING.items():
        text = publisher_map.get(path, "")
        for marker in markers:
            required_count = (
                2 if path == "publish-registries.sh"
                and marker.startswith("AARON_PUBLISH_EXPECTED_") else 1
            )
            if text.count(marker) < required_count:
                missing.append("publisher-wiring:%s:%s" % (path, marker))
    if "publish_prepare_release_source \"$SOURCE_ROOT\"" not in sync_about:
        missing.append("sync-about:pinned_source")
    if "publish_prepare_release_source \"$SOURCE_ROOT\"" not in sync_family:
        missing.append("sync-family:pinned_source")
    for test_name in H17_PUBLISHER_TESTS:
        if "def %s(" % test_name not in publisher_tests:
            missing.append("publisher-test:%s" % test_name)
    if missing:
        return Fact(
            False,
            "H17 live release provenance/pinned-source proof is missing: %s" %
            ", ".join(missing),
        )
    return Fact(
        True,
        "publisher-release-safety proves every live entrypoint rejects dirty or "
        "spoofed origins before mutation; URL rewrites and in-gate origin drift fail "
        "closed; every entrypoint consumes one repository+commit snapshot, orchestrated "
        "children must match it, and About/plugin/reference payloads stay commit-pinned",
    )


def h19_fact(harness_suite, semantic_request_suite, adapter_text, runner_text,
             verifier_text, behavior_eval_tests, codex_adapter_tests,
             verifier_tests, policy, ci_text, suites):
    missing = []
    if not harness_suite.passed:
        missing.append("harness_suite")
    if not semantic_request_suite.passed:
        missing.append("semantic_request_suite")
    for symbol in H19_ADAPTER_SYMBOLS:
        if "def %s(" % symbol not in adapter_text:
            missing.append("adapter-symbol:%s" % symbol)
    for marker in H19_ADAPTER_MARKERS:
        if marker not in adapter_text:
            missing.append("adapter-marker:%s" % marker)
    for marker in H19_RUNNER_MARKERS:
        if marker not in runner_text:
            missing.append("runner-marker:%s" % marker)
    for marker in H19_VERIFIER_MARKERS:
        if marker not in verifier_text:
            missing.append("verifier-marker:%s" % marker)
    for test_name in H19_BEHAVIOR_EVAL_TESTS:
        if "def %s(" % test_name not in behavior_eval_tests:
            missing.append("behavior-test:%s" % test_name)
    for test_name in H19_CODEX_ADAPTER_TESTS:
        if "def %s(" % test_name not in codex_adapter_tests:
            missing.append("adapter-test:%s" % test_name)
    for test_name in H19_VERIFIER_TESTS:
        if "def %s(" % test_name not in verifier_tests:
            missing.append("verifier-test:%s" % test_name)
    for marker in H19_VERIFIER_TEST_MARKERS:
        if marker not in verifier_tests:
            missing.append("verifier-test-marker:%s" % marker)
    for key in ("require_isolated_project_adapter", "require_staged_project_adapter"):
        if policy.get(key) is not True:
            missing.append("policy:%s" % key)
    if "tests.test_semantic_evidence_verifier" not in ci_text:
        missing.append("ci:semantic-evidence-verifier")
    if not any(
            suite.get("id") == "five-engineering-maturity-contract"
            and "tests.test_semantic_evidence_verifier" in suite.get("command", [])
            and "tests.test_behavior_evals_adapter" in suite.get("command", [])
            for suite in suites.get("suites", [])):
        missing.append("deterministic-suite:h19")
    if missing:
        return Fact(
            False,
            "H19 isolated staged adapter, bounded judge recovery, or hash-bound ledger "
            "proof is missing: %s" % ", ".join(missing),
        )
    return Fact(
        True,
        "harness and semantic suites prove current-source staged isolation; each candidate "
        "runs once, judge protocol recovery is capped at two fresh attempts without raw "
        "repair echo, and the runner/verifier enforce and report the ordered hash-bound "
        "judge-attempt ledger",
    )


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise MaturityError("cannot load %s: %s" % (path, exc)) from exc


def repository_provenance(root):
    def git(*arguments):
        try:
            result = subprocess.run(
                ["git", *arguments], cwd=root, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                timeout=10, check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            return None
        return result.stdout.strip() if result.returncode == 0 else None

    commit = git("rev-parse", "--verify", "HEAD^{commit}")
    branch = git("branch", "--show-current")
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    return {
        "git_available": commit is not None,
        "commit": commit,
        "branch": branch or None,
        "worktree_clean": status == "" if status is not None else None,
    }


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise MaturityError("cannot load module %s" % path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def validate_rubric(value):
    required = {
        "$schema", "schema_version", "target_score", "hard_gate_cap",
        "control_weight", "dimensions",
    }
    if not isinstance(value, dict) or set(value) != required:
        raise MaturityError("maturity rubric has unknown or missing fields")
    if value["schema_version"] != "1.0" or set(value["dimensions"]) != EXPECTED_DIMENSIONS:
        raise MaturityError("maturity rubric identity/dimensions are invalid")
    if value["target_score"] != 95 or value["hard_gate_cap"] >= value["target_score"]:
        raise MaturityError("maturity target or hard-gate cap is invalid")
    if value["control_weight"] != 5:
        raise MaturityError("maturity rubric must use five-point controls")
    seen = set()
    for name, controls in value["dimensions"].items():
        if not isinstance(controls, list) or len(controls) != 20:
            raise MaturityError("dimension %s must contain exactly 20 controls" % name)
        prefix = name[0].upper()
        for index, control in enumerate(controls, 1):
            if not isinstance(control, dict) or set(control) != {
                    "id", "control", "evidence_class", "hard_gate"}:
                raise MaturityError("control shape is invalid in %s" % name)
            expected = "%s%02d" % (prefix, index)
            if control["id"] != expected or control["id"] in seen:
                raise MaturityError("control identity/order is invalid: %s" % control["id"])
            if control["evidence_class"] not in {"S", "D", "E", "O", "R"}:
                raise MaturityError("control evidence class is invalid: %s" % control["id"])
            if not isinstance(control["hard_gate"], bool):
                raise MaturityError("control hard_gate must be boolean")
            seen.add(control["id"])
    return value


def score_dimension(controls, facts, weight, hard_gate_cap):
    rows = []
    for control in controls:
        fact = facts[control["id"]]
        rows.append({
            **control,
            "passed": fact.passed,
            "points": weight if fact.passed else 0,
            "evidence": fact.evidence,
        })
    raw = sum(item["points"] for item in rows)
    failed_hard = [item["id"] for item in rows if item["hard_gate"] and not item["passed"]]
    final = min(raw, hard_gate_cap) if failed_hard else raw
    return rows, raw, final, failed_hard


class Auditor:
    def __init__(self, root=ROOT, *, run_dynamic=True, evidence_run_id=None,
                 evidence_root=None, timeout=240):
        self.root = Path(root).resolve()
        self.run_dynamic = run_dynamic
        self.evidence_run_id = evidence_run_id
        self.evidence_root = Path(evidence_root or self.root).resolve()
        self.timeout = timeout
        self.commands = {}
        self._facts = None
        self.semantic_result = None
        self.catalog = load_json(self.root / "references/system-catalog.json")
        self.contract_index = load_json(self.root / "references/skill-contracts/index.json")
        self.contracts = [
            load_json(self.root / entry["contract_ref"])
            for entry in self.contract_index["contracts"]
        ]
        self.graph_source = load_json(self.root / "references/workflow-graph.source.json")
        self.graph = load_json(self.root / "references/workflow-graph.json")
        self.graph_edges = []
        for shard in self.graph_source["edge_shards"]:
            self.graph_edges.extend(load_json(self.root / shard["ref"])["edges"])
        self.ci = (self.root / ".github/workflows/validate-skill.yml").read_text(encoding="utf-8")
        self.distribution = load_json(self.root / "references/distribution-files.json")
        self.suites = load_json(self.root / "evals/deterministic-suites.json")

    def command(self, key, command):
        if key in self.commands:
            return self.commands[key]
        if not self.run_dynamic:
            result = CommandEvidence(False, "dynamic execution disabled")
            self.commands[key] = result
            return result
        try:
            completed = subprocess.run(
                command, cwd=self.root, text=True, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, timeout=self.timeout, check=False,
            )
            tail = " ".join(completed.stdout.strip().splitlines()[-3:])[-500:]
            result = CommandEvidence(
                completed.returncode == 0,
                "exit=%d%s" % (completed.returncode, ("; " + tail) if tail else ""),
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            result = CommandEvidence(False, "execution error: %s" % exc)
        self.commands[key] = result
        return result

    @staticmethod
    def fact(value, success, failure):
        return Fact(bool(value), success if value else failure)

    def suite_fact(self, key, command, label):
        result = self.command(key, command)
        return Fact(result.passed, "%s: %s" % (label, result.summary))

    def _catalog_skill_names(self):
        names = []
        for discipline in self.catalog["disciplines"].values():
            for phase in discipline["phase_order"]:
                names.extend(discipline["phases"][phase])
        names.extend(self.catalog["protocol"]["skills"])
        return names

    def _contract_hashes_current(self):
        entries = {item["skill"]: item for item in self.contract_index["contracts"]}
        for contract in self.contracts:
            identity = contract["identity"]
            skill_raw = (self.root / identity["path"]).read_bytes()
            contract_raw = (self.root / entries[identity["name"]]["contract_ref"]).read_bytes()
            if sha256_bytes(skill_raw) != identity["sha256"]:
                return False
            if sha256_bytes(contract_raw) != entries[identity["name"]]["contract_sha256"]:
                return False
        return True

    def _source_spans_valid(self):
        for contract in self.contracts:
            for section in ("input_contract", "output_contract", "completion_contract"):
                for clause in contract[section].get("clauses", []):
                    source = clause["source"]
                    if (
                            source["start_char"] < 0
                            or source["end_char"] <= source["start_char"]
                            or source["sha256"] != contract["identity"]["sha256"]
                            or clause["extraction_status"] not in {
                                "classified", "partially-classified", "unclassified"}):
                        return False
            for item in contract["handoff_contract"].get("items", []):
                source = item["source"]
                if source["end_char"] <= source["start_char"]:
                    return False
        return True

    def _controller_ci(self):
        return all(token in self.ci for token in (
            "tests.test_runtime_controller", "tests.test_context_plan",
            "scripts/generate-skill-contracts.py --check",
        ))

    def _semantic_evidence(self):
        if not self.evidence_run_id:
            return Fact(False, "no --semantic-evidence-run-id supplied"), None
        try:
            verifier = _load_module(
                "aaron_maturity_semantic_verifier",
                self.root / "scripts/verify-semantic-evidence.py",
            )
            result = verifier.verify_evidence(self.evidence_root, self.evidence_run_id)
            return Fact(
                True,
                "verified %s %d-case real run %s (model=%s judge=%s)" % (
                    result["profile"], result["case_count"], result["run_id"],
                    result["model_id"], result["judge_model_id"],
                ),
            ), result
        except Exception as exc:
            return Fact(False, "semantic evidence rejected: %s" % exc), None

    def _publisher_scripts(self):
        candidates = []
        for path in sorted((self.root / "scripts").glob("publish*.sh")):
            text = path.read_text(encoding="utf-8")
            if "--live" in text or "PUBLISH_LIVE" in text or "publish" in path.name:
                candidates.append((path.name, text))
        return candidates

    def build_facts(self):
        if self._facts is not None:
            return self._facts
        facts = {}
        names = self._catalog_skill_names()
        identities = [item["identity"]["name"] for item in self.contracts]
        prompt_suite = self.suite_fact("prompt-suite", [
            "python3", "-m", "unittest", "tests.test_skill_contracts",
            "tests.test_auditor_prompt_contracts", "tests.test_behavior_profiles",
            "tests.test_eval_cases",
        ], "prompt contract suite")
        prompt_drift = self.suite_fact("prompt-drift", [
            "python3", "scripts/generate-skill-contracts.py", "--check",
        ], "machine-contract drift gate")
        semantic_request_suite = self.suite_fact("semantic-request-suite", [
            "python3", "-m", "unittest", "tests.test_behavior_evals_adapter",
            "tests.test_codex_behavior_adapter",
        ], "semantic request/context isolation suite")
        context_suite = self.suite_fact("context-suite", [
            "python3", "-m", "unittest", "tests.test_context_plan",
            "tests.test_context_resolver", "tests.test_runtime_controller",
        ], "context/controller suite")
        context_budget = self.suite_fact("context-budget", [
            "python3", "scripts/check-context-budget.py",
        ], "context budget gate")
        harness_suite = self.suite_fact("harness-suite", [
            "python3", "-m", "unittest", "tests.test_runtime_controller",
            "tests.test_run_events", "tests.test_distribution_builder",
            "tests.test_publish_release", "tests.test_publish_state",
            "tests.test_semantic_evidence_verifier",
        ], "harness hardening suite")
        graph_suite = self.suite_fact("graph-suite", [
            "python3", "-m", "unittest", "tests.test_workflow_graph",
        ], "workflow graph suite")
        graph_check = self.suite_fact("graph-check", [
            "python3", "scripts/workflow-graph.py", "--check",
        ], "authoritative graph drift gate")
        loop_suite = self.suite_fact("loop-suite", [
            "python3", "-m", "unittest", "tests.test_workflow_loop",
        ], "generic workflow-loop suite")
        semantic_fact, semantic_result = self._semantic_evidence()
        self.semantic_result = semantic_result

        # Prompt engineering controls.
        facts["P01"] = self.fact(
            len(identities) == 120 and len(set(identities)) == 120 and set(identities) == set(names),
            "120 unique contracts exactly cover the catalog", "contract/catalog coverage differs",
        )
        contract_schema = load_json(self.root / "references/skill-machine-contract.schema.json")
        facts["P02"] = self.fact(
            contract_schema.get("additionalProperties") is False
            and all(item.get("$schema") == "../skill-machine-contract.schema.json"
                    for item in self.contracts),
            "closed schema governs every contract", "contract schema/artifact is not closed",
        )
        facts["P03"] = self.fact(
            self._contract_hashes_current(), "skill and contract bytes match indexed SHA-256",
            "skill or contract hash drift detected",
        )
        facts["P04"] = self.fact(
            all(
                item["identity"]["discipline"] in {*self.catalog["disciplines"], "protocol"}
                and item["identity"]["phase"]
                and item["provenance"]["system_catalog"]["version"]
                    == self.catalog["architecture_version"]
                for item in self.contracts
            ), "identity/discipline/phase/catalog provenance is bound",
            "contract identity or catalog provenance is incomplete",
        )
        facts["P05"] = self.fact(
            all(item["routing_contract"]["trigger_source"] and item["routing_contract"]["source"]
                and (item["routing_contract"]["trigger_phrases"]
                     or item["routing_contract"]["when_to_use"])
                for item in self.contracts),
            "all routing triggers carry a source", "one or more trigger contracts are empty",
        )
        facts["P06"] = self.fact(
            all("boundary" in item["routing_contract"] and item["routing_contract"]["source"]
                for item in self.contracts),
            "scope boundary field and source exist for all contracts",
            "scope boundary representation is missing",
        )
        facts["P07"] = self.fact(
            self._source_spans_valid()
            and all(all(clause["requirement"] in {"required", "optional", "unclassified"}
                        for clause in item["input_contract"]["clauses"])
                    for item in self.contracts),
            "input clauses preserve exact spans and explicit uncertainty",
            "input clause provenance/classification is invalid",
        )
        facts["P08"] = self.fact(
            all(item["output_contract"]["summary"] and "writes" in item["output_contract"]
                for item in self.contracts),
            "all outputs expose summary and write expectations", "output contract is incomplete",
        )
        facts["P09"] = self.fact(
            all(item["input_contract"]["source"] and "reads" in item["input_contract"]
                and "bundle_references" in item["context_hints"] for item in self.contracts),
            "read dependencies and provenance are present", "read dependency projection is missing",
        )
        facts["P10"] = self.fact(
            all(all(set(clause) >= {
                "side_effect", "permission_posture", "extraction_status", "source"}
                for clause in item["output_contract"]["clauses"])
                for item in self.contracts),
            "write clauses type side effects and permissions",
            "write side-effect/permission typing is incomplete",
        )
        facts["P11"] = self.fact(
            all(item["completion_contract"]["done_when"]
                and all(clause["condition_kind"] in {"success", "blocking", "unclassified"}
                        for clause in item["completion_contract"]["clauses"])
                for item in self.contracts),
            "completion clauses type success/blocking conditions",
            "completion condition typing is incomplete",
        )
        facts["P12"] = self.fact(
            all("target_skills" in item["handoff_contract"]
                and all(set(edge) >= {"condition", "target_skills", "source"}
                        for edge in item["handoff_contract"]["items"])
                for item in self.contracts),
            "handoff targets and conditions are machine-readable",
            "handoff target/condition projection is incomplete",
        )
        facts["P13"] = self.fact(
            all(section.get("extraction_status") in {
                "classified", "partially-classified", "unclassified"}
                for item in self.contracts for section in (
                    item["input_contract"], item["output_contract"],
                    item["completion_contract"], item["handoff_contract"]))
            and any(
                clause.get("extraction_status") == "unclassified"
                for item in self.contracts
                for clause in item["input_contract"]["clauses"]
                    + item["output_contract"]["clauses"]
                    + item["completion_contract"]["clauses"]
                    + item["handoff_contract"]["items"]
            ), "explicit unclassified states are preserved", "extraction uncertainty is hidden",
        )
        facts["P14"] = prompt_suite
        facts["P15"] = prompt_drift
        facts["P16"] = self.fact(
            "generate-skill-contracts.py --check" in self.ci
            and "tests.test_skill_contracts" in self.ci,
            "machine contract generator/tests are wired into CI",
            "machine contract CI wiring is missing",
        )
        facts["P17"] = self.fact(
            context_suite.passed
            and "planner.build_request" in (self.root / "scripts/runtime-controller.py").read_text(),
            "controller suite proves selected contract consumption",
            "supported controller does not prove contract consumption",
        )
        semantic_runner_text = (self.root / "scripts/run-behavior-evals.py").read_text()
        semantic_request_tests = (self.root / "tests/test_behavior_evals_adapter.py").read_text()
        codex_adapter_tests = (self.root / "tests/test_codex_behavior_adapter.py").read_text()
        facts["P18"] = p18_fact(
            semantic_request_suite, semantic_runner_text,
            semantic_request_tests, codex_adapter_tests,
        )
        facts["P19"] = semantic_fact
        facts["P20"] = self.fact(
            bool(semantic_result and semantic_result["distinct_judge_model"]),
            "real evidence uses model=%s and distinct judge=%s" % (
                semantic_result["model_id"], semantic_result["judge_model_id"])
                if semantic_result else "distinct judge evidence unavailable",
            "real evidence has no verified distinct judge model",
        )

        # Context engineering controls.
        planner_text = (self.root / "scripts/context-plan.py").read_text(encoding="utf-8")
        resolver_text = (self.root / "scripts/context-resolver.py").read_text(encoding="utf-8")
        context_tests = (self.root / "tests/test_context_plan.py").read_text(encoding="utf-8") + (
            self.root / "tests/test_context_resolver.py").read_text(encoding="utf-8")
        facts["C01"] = self.fact(
            context_suite.passed and "test_full_catalog_plans" in context_tests,
            "full-catalog first-party planning test passes", "full catalog planning is not proven",
        )
        facts["C02"] = self.fact(
            "closed-machine-contract" in planner_text and "host" not in planner_text.lower().split("discovery itself")[0],
            "planner owns closed candidate discovery", "planner appears host-search dependent",
        )
        facts["C03"] = self.fact(
            all(item["identity"]["path"] for item in self.contracts) and context_suite.passed,
            "target skill and runtime-source candidate tests pass",
            "required target/runtime sources are not proven",
        )
        facts["C04"] = self.fact(
            "test_missing_optional_project_files" in context_tests and context_suite.passed,
            "missing project memory remains explicit optional context",
            "optional project-memory behavior is unproven",
        )
        facts["C05"] = self.fact(
            '"authority"' in planner_text and context_suite.passed,
            "candidate authority is generated and resolver-tested",
            "candidate authority is not enforced",
        )
        facts["C06"] = self.fact(
            all(token in planner_text for token in ("observed_at", "max_age_seconds", "freshness"))
            and context_suite.passed,
            "freshness evidence/policy is explicit", "freshness fields or tests are missing",
        )
        facts["C07"] = self.fact(
            "max_sensitivity" in resolver_text and context_suite.passed,
            "resolver enforces explicit sensitivity ceiling", "sensitivity enforcement is unproven",
        )
        facts["C08"] = self.fact(
            "utf8-bytes-per-token-proxy-v1" in planner_text and context_suite.passed,
            "token intent maps to deterministic byte proxy", "token/byte budget mapping is missing",
        )
        facts["C09"] = self.fact(
            all(all(reference["sha256"] for reference in item["context_hints"]["bundle_references"])
                for item in self.contracts),
            "all stable bundle hints are SHA-256 pinned", "an authored bundle hint is unpinned",
        )
        facts["C10"] = self.fact(
            all(token in planner_text for token in (
                "skill_contract", "contract_index", "system_catalog", "candidate_set_sha256"))
            and context_suite.passed,
            "plans bind planner/contract/index/catalog provenance",
            "planner provenance binding is incomplete",
        )
        request_schema = load_json(self.root / "references/context-request.schema.json")
        facts["C11"] = self.fact(
            request_schema.get("additionalProperties") is False and context_suite.passed,
            "planned requests conform to a closed schema", "context request schema is not closed",
        )
        facts["C12"] = self.fact(
            "_validate_planner" in resolver_text and context_suite.passed,
            "resolver validates planner provenance and derived budgets",
            "resolver/planner binding is unproven",
        )
        facts["C13"] = self.fact(
            context_suite.passed and "fails_closed" in context_tests,
            "required context drift/missing tests fail closed", "required context failure tests missing",
        )
        facts["C14"] = self.fact(
            context_suite.passed and all(token in context_tests for token in ("supersed", "duplicate")),
            "conflict/supersession/duplicate tests pass", "deterministic conflict tests missing",
        )
        facts["C15"] = self.fact(
            context_suite.passed
            and "test_budget_omission_and_required_overflow_fail_closed" in context_tests,
            "typed omission and required-overflow tests pass", "budget omission/overflow tests missing",
        )
        facts["C16"] = self.fact(
            context_suite.passed
            and "test_symlink_hardlink_special_traversal" in context_tests
            and "test_directory_swap_failures_close_new_child_descriptors" in context_tests,
            "context filesystem adversarial tests pass", "context filesystem hardening tests missing",
        )
        facts["C17"] = self.fact(
            context_suite.passed and "test_candidate_order_invariance" in context_tests,
            "candidate order invariance test passes", "candidate-order invariance is unproven",
        )
        facts["C18"] = self.fact(
            context_suite.passed and "test_start_consumes_machine_contract" in (
                self.root / "tests/test_runtime_controller.py").read_text(),
            "controller route-plan-resolve-snapshot E2E passes",
            "supported route-to-snapshot path is unproven",
        )
        facts["C19"] = self.fact(
            context_suite.passed and "verify_manifest_sources" in resolver_text
            and "rejects_live_context_drift" in (
                self.root / "tests/test_runtime_controller.py").read_text(),
            "manifest replay/live-source verification tests pass",
            "manifest live replay is unproven",
        )
        facts["C20"] = self.fact(
            self._controller_ci() and "tests.test_context_resolver" in self.ci,
            "planner/resolver/controller adversarial tests are in CI",
            "context/controller CI wiring is incomplete",
        )

        # Harness engineering controls.
        controller_tests = (self.root / "tests/test_runtime_controller.py").read_text()
        run_tests = (self.root / "tests/test_run_events.py").read_text()
        facts["H01"] = self.fact(
            harness_suite.passed and (self.root / "scripts/runtime-controller.py").is_file(),
            "supported lifecycle controller and hardening suite pass",
            "controller lifecycle suite failed or is absent",
        )
        facts["H02"] = self.fact(
            harness_suite.passed and "route_selected" in controller_tests,
            "controller initial typed route is E2E-tested", "typed initial route is unproven",
        )
        facts["H03"] = self.fact(
            harness_suite.passed and "turn_snapshot_created" in controller_tests,
            "immutable context snapshot is E2E-tested", "snapshot installation is unproven",
        )
        facts["H04"] = self.fact(
            harness_suite.passed and "test_checkpoint_requires_current_head" in controller_tests,
            "verified save-point checkpoint tests pass", "checkpoint verification is unproven",
        )
        facts["H05"] = self.fact(
            harness_suite.passed and all(token in controller_tests for token in (
                '"waiting"', '"failed"', '"aborted"', '"succeeded"')),
            "wait/failure/abort/success typed-envelope test passes",
            "lifecycle terminal/wait envelope coverage is incomplete",
        )
        facts["H06"] = self.fact(
            harness_suite.passed and "ignores_projection" in controller_tests,
            "resume rebuilds verified state without projection trust",
            "projection-independent recovery is unproven",
        )
        facts["H07"] = self.fact(
            harness_suite.passed and "conflicting_snapshot_replay" in controller_tests
            and "replays_exactly" in controller_tests,
            "lifecycle idempotency/conflict tests pass", "lifecycle replay safety is unproven",
        )
        facts["H08"] = self.fact(
            harness_suite.passed and "permission_profile" in controller_tests,
            "snapshots bind explicit permission/sandbox profile",
            "permission profile snapshot binding is unproven",
        )
        facts["H09"] = self.fact(
            harness_suite.passed and "rejects_open_tool" in controller_tests,
            "success rejects unfinished selected-branch tools",
            "open-tool terminal rejection is unproven",
        )
        facts["H10"] = self.fact(
            harness_suite.passed and "selected-branch" in run_tests
            and "hash-chain" in (
                self.root / "references/runtime-protocol.md"
            ).read_text(encoding="utf-8"),
            "hash-chain and selected-ancestry tests pass", "run ancestry/hash-chain safety missing",
        )
        facts["H11"] = self.fact(
            "Standalone degradation is fail-closed" in (
                self.root / "references/runtime-invocation.md").read_text()
            and harness_suite.passed,
            "standalone/missing-runtime degradation is explicit",
            "standalone degradation contract is missing",
        )
        facts["H12"] = self.fact(
            harness_suite.passed and all(token in (
                self.root / "scripts/runtime-controller.py").read_text() for token in (
                    "controller.turns", "controller.tool_calls", "controller.loops")),
            "bounded controller status/route/loop/evidence metrics are emitted",
            "controller operational metrics are incomplete",
        )
        registered = {item["id"] for item in self.suites.get("suites", [])}
        facts["H13"] = self.fact(
            harness_suite.passed and {"distribution-supply-chain", "publisher-release-safety"}
                <= registered,
            "registered harness behavior suites and unit tests pass",
            "registered deterministic harness suites are missing/failing",
        )
        facts["H14"] = self.fact(
            "tests.test_runtime_controller" in self.ci
            and "tests.test_distribution_builder" in self.ci
            and "tests.test_publish_release" in self.ci,
            "controller/hardening tests are mandatory in CI",
            "controller/hardening CI wiring is incomplete",
        )
        distribution_tests = (self.root / "tests/test_distribution_builder.py").read_text()
        facts["H15"] = self.fact(
            harness_suite.passed and all(token in distribution_tests for token in (
                "symlink", "special", "multi_link")),
            "distribution link/special/multi-link attacks are rejected",
            "distribution input hardening is incomplete",
        )
        facts["H16"] = self.fact(
            harness_suite.passed and "distribution-manifest.json" in (
                self.root / "scripts/build-distribution.py").read_text(),
            "per-file verified distribution manifest is generated",
            "distribution digest manifest is missing/unverified",
        )
        publishers = self._publisher_scripts()
        common_publish = (self.root / "scripts/publish-common.sh").read_text(
            encoding="utf-8") if (self.root / "scripts/publish-common.sh").is_file() else ""
        publisher_tests = (self.root / "tests/test_publish_release.py").read_text(
            encoding="utf-8",
        )
        facts["H17"] = h17_fact(
            harness_suite,
            publishers,
            common_publish,
            (self.root / "scripts/sync-about.sh").read_text(encoding="utf-8"),
            (self.root / "scripts/sync-family.sh").read_text(encoding="utf-8"),
            publisher_tests,
        )
        state_text = (self.root / "scripts/publish-state.py").read_text(
            encoding="utf-8") if (self.root / "scripts/publish-state.py").is_file() else ""
        facts["H18"] = self.fact(
            harness_suite.passed and all(token in state_text for token in (
                "flock", "0o600", "os.replace")),
            "publish resume state is private/scoped/locked/atomic",
            "publish resume-state hardening is incomplete",
        )
        facts["H19"] = h19_fact(
            harness_suite,
            semantic_request_suite,
            (self.root / "scripts/adapters/codex-behavior-adapter.py").read_text(
                encoding="utf-8",
            ),
            semantic_runner_text,
            ((self.root / "scripts/verify-semantic-evidence.py").read_text(
                encoding="utf-8",
            ) if (self.root / "scripts/verify-semantic-evidence.py").is_file() else ""),
            semantic_request_tests,
            codex_adapter_tests,
            ((self.root / "tests/test_semantic_evidence_verifier.py").read_text(
                encoding="utf-8",
            ) if (self.root / "tests/test_semantic_evidence_verifier.py").is_file() else ""),
            load_json(self.root / "evals/semantic-evidence-policy.json"),
            self.ci,
            self.suites,
        )
        facts["H20"] = semantic_fact

        # Loop engineering controls.
        loop_plan_schema = load_json(self.root / "references/workflow-loop-plan.schema.json")
        loop_event_schema = load_json(self.root / "references/workflow-loop-event.schema.json")
        loop_state_schema = load_json(self.root / "references/workflow-loop-state.schema.json")
        loop_request_schema = load_json(self.root / "references/workflow-loop-request.schema.json")
        loop_text = (self.root / "scripts/workflow_loop.py").read_text(encoding="utf-8")
        loop_tests = (self.root / "tests/test_workflow_loop.py").read_text(encoding="utf-8")
        workflow = self.graph["workflows"][0]
        facts["L01"] = self.fact(
            all(schema.get("additionalProperties") is False for schema in (
                loop_plan_schema, loop_event_schema, loop_state_schema))
            and all(loop_request_schema["$defs"][name].get("additionalProperties") is False
                    for name in ("plan_request", "advance_request"))
            and loop_suite.passed,
            "closed loop plan/event/state/request contracts pass",
            "loop schema closure or suite failed",
        )
        facts["L02"] = self.fact(
            all(field in loop_plan_schema["required"] for field in (
                "objective", "hypothesis", "success_criteria"))
            and loop_suite.passed,
            "plan binds objective, hypothesis, and success criteria",
            "loop plan lacks tested hypothesis/success criteria",
        )
        stage_enum = set(loop_state_schema["properties"]["stage"]["enum"])
        facts["L03"] = self.fact(
            {"action", "verification", "decision", "memory-proposal"} <= stage_enum
            and loop_suite.passed,
            "action/verification/decision/memory proposal are distinct stages",
            "loop stage separation is incomplete",
        )
        facts["L04"] = self.fact(
            loop_suite.passed and "illegal" in loop_tests,
            "illegal transition tests fail closed", "illegal transition test is absent/failing",
        )
        facts["L05"] = self.fact(
            1 <= workflow["max_cycles"] <= 3 and loop_suite.passed,
            "workflow has tested hard cycle cap <=3", "cycle cap is missing/unbounded",
        )
        facts["L06"] = self.fact(
            workflow["deadline_seconds"] > 0 and "deadline" in loop_tests and loop_suite.passed,
            "absolute deadline and expiry test pass", "deadline enforcement is unproven",
        )
        facts["L07"] = self.fact(
            all(workflow["budgets"].get(key, 0) > 0 for key in (
                "max_events", "max_actions", "max_verifications", "max_memory_proposals"))
            and loop_suite.passed,
            "action/event/verification/proposal budgets are bounded",
            "loop budget policy is incomplete",
        )
        facts["L08"] = self.fact(
            "max_retries" in loop_text and "max_cycles" in loop_text
            and "retry" in loop_tests and loop_suite.passed,
            "retry budget is tested separately from cycle budget",
            "separate bounded retry policy is unproven",
        )
        facts["L09"] = self.fact(
            loop_suite.passed and "_validate_verification_evidence" in loop_text
            and "success_criteria" in loop_text,
            "convergence uses typed verifier evidence and criteria",
            "typed verifier convergence is unproven",
        )
        facts["L10"] = self.fact(
            loop_suite.passed and "stall_count" in loop_text and "repeated_failed" in loop_tests,
            "repeated finding/no-progress stalls are tested",
            "stall detection is missing/failing",
        )
        facts["L11"] = self.fact(
            loop_suite.passed and "escalation-required" in loop_text,
            "exhaustion/stall escalation is typed", "typed escalation is missing",
        )
        terminal_outcomes = set(
            loop_request_schema["$defs"].get("terminal_payload", {}).get(
                "properties", {}).get("outcome", {}).get("enum", [])
        )
        facts["L12"] = self.fact(
            loop_suite.passed and {"converged", "exhausted", "escalated", "failed"}
                <= terminal_outcomes,
            "terminal outcomes are explicit and closed", "terminal outcome contract is incomplete",
        )
        facts["L13"] = self.fact(
            loop_suite.passed and "reserves_the_terminal_slot" in loop_tests,
            "event budget reserves one terminal slot", "terminal-slot preservation is unproven",
        )
        facts["L14"] = self.fact(
            loop_suite.passed and "compare_and_swap_and_idempotent_retry" in loop_tests,
            "advance CAS/idempotency/conflict replay tests pass",
            "loop idempotency/CAS is unproven",
        )
        facts["L15"] = self.fact(
            loop_suite.passed and "projection_failure_recovers" in loop_tests,
            "interrupted loop recovers from verified immutable head",
            "loop recovery/tamper test is missing/failing",
        )
        facts["L16"] = self.fact(
            loop_suite.passed
            and all(token in loop_text for token in (
                "_validate_plan_anchor", "_is_fresh_post_plan_event",
                "require_current_head=True", "plan created_at cannot precede",
                "locked_run_coordinator", "evidence_cutoff",
            ))
            and all(token in loop_tests for token in (
                "plan_anchor_must_be_the_current_selected_head",
                "plan_created_at_cannot_precede_anchor_timestamp",
                "post_cutoff_recorded_event_is_fresh_despite_historical_occurred_at",
                "preplan_artifact_validation_cannot_satisfy_verification",
                "preplan_run_event_cannot_satisfy_decision_evidence",
                "plan_persistence_cutoff_serializes_concurrent_run_event_append",
            )),
            "coordinator-protected persisted cutoff and evidence freshness tests pass",
            "atomic run-event cutoff or temporal evidence isolation is unproven",
        )
        facts["L17"] = self.fact(
            loop_suite.passed and "sibling" in loop_tests and "selected" in loop_text,
            "sibling branch cannot satisfy selected-ancestry evidence",
            "selected-ancestry sibling isolation is unproven",
        )
        facts["L18"] = self.fact(
            all(key in loop_state_schema["properties"]["counts"]["properties"]
                for key in ("events", "actions", "verifications", "decisions"))
            and "stall_count" in loop_state_schema["properties"],
            "loop state reports cycle/action/verification/stall closure metrics",
            "loop operational metrics are incomplete",
        )
        facts["L19"] = self.fact(
            loop_suite.passed and all(token in loop_tests for token in (
                "converge", "deadline", "budget", "stall", "recover")),
            "loop suite covers convergence/timeout/budget/stall/recovery",
            "loop adversarial coverage is incomplete",
        )
        release_edges = [
            edge for edge in self.graph_edges
            if edge["id"] == "launch-readiness-auditor--launch-day-conductor"
        ]
        release_contract = release_edges[0] if len(release_edges) == 1 else {}
        facts["L20"] = self.fact(
            loop_suite.passed and graph_suite.passed
            and "full_fanout_join" in loop_tests
            and release_contract.get("type") == "gate"
            and release_contract.get("gate") == "launch-readiness-auditor"
            and "audit-evidence" in release_contract.get("required_inputs", [])
            and "execution-approval" in release_contract.get("required_inputs", [])
            and "external-action-approval" in release_contract.get("permissions", [])
            and all(token in loop_text for token in (
                "_verify_rs256", "_approval_trust_for_plan",
                "consumed_approval_nonces", "TRUST_ANCHOR_SHA_ENV",
                "action_recorded_at=event[\"recorded_at\"]",
                "event recorded_at timestamps must be strictly monotonic",
            ))
            and (self.root / "references/workflow-execution-approval.schema.json").is_file()
            and (self.root / "references/workflow-execution-approval-trust.schema.json").is_file()
            and all(token in loop_tests for token in (
                "fix_verdict_cannot_release_launch_day",
                "block_verdict_cannot_release_launch_day",
                "undecided_verdict_cannot_release_launch_day",
                "ship_without_independent_execution_approval_stays_closed",
                "ship_approval_not_bound_to_exact_audit_artifact_stays_closed",
                "non_validator_clean_ship_stays_closed",
                "self_reported_host_tool_allowed_cannot_release_gate",
                "bad_approval_signature_cannot_release_gate",
                "valid_signature_with_wrong_action_binding_cannot_release_gate",
                "expired_signed_approval_cannot_release_gate",
                "backdated_occurred_at_cannot_hide_runtime_approval_expiry",
                "historical_valid_approval_remains_valid_on_later_verify",
                "recorded_at_tampering_breaks_the_event_hash",
                "runtime_recorded_at_must_advance_monotonically",
                "recomputed_nonmonotonic_recorded_at_fails_replay",
                "missing_or_drifted_external_trust_anchor_fails_closed",
                "signed_approval_nonce_cannot_be_replayed_in_next_cycle",
            ))
            and "tests.test_workflow_loop" in self.ci,
            "Product Launch executes with validator-clean SHIP and host-signed approval gate",
            "graph-through-loop SHIP/signed-approval gate execution is unproven",
        )

        # Graph engineering controls.
        graph_nodes = self.graph["nodes"]
        node_names = [node["id"] for node in graph_nodes]
        edge_schema = load_json(self.root / "references/workflow-graph-source.schema.json")[
            "$defs"]["edge"]
        facts["G01"] = self.fact(
            len(node_names) == 120 and len(set(node_names)) == 120
            and set(node_names) == set(names) and graph_check.passed,
            "120 graph nodes exactly cover catalog", "graph/catalog node coverage differs",
        )
        facts["G02"] = self.fact(
            graph_check.passed and all(set(node) >= {"id", "layer", "discipline", "phase"}
                                       for node in graph_nodes),
            "node identity/layer/discipline/phase match catalog",
            "node metadata/catalog validation failed",
        )
        edge_ids = [edge["id"] for edge in self.graph_edges]
        facts["G03"] = self.fact(
            edge_schema.get("additionalProperties") is False
            and len(edge_ids) == len(set(edge_ids))
            and all(edge["from"] in node_names and edge["to"] in node_names
                    for edge in self.graph_edges) and graph_check.passed,
            "%d closed typed edges have valid unique endpoints" % len(edge_ids),
            "edge identity/endpoint/schema validation failed",
        )
        facts["G04"] = graph_check
        facts["G05"] = self.fact(
            graph_suite.passed and "both_directions" in (
                self.root / "tests/test_workflow_graph.py").read_text(),
            "Markdown/source edge drift is checked bidirectionally",
            "bidirectional handoff drift test is absent/failing",
        )
        facts["G06"] = self.fact(
            all(edge["precondition_codes"] and edge["required_inputs"]
                for edge in self.graph_edges),
            "every edge declares precondition codes and required inputs",
            "an edge lacks typed preconditions/inputs",
        )
        facts["G07"] = self.fact(
            all(edge["permissions"] for edge in self.graph_edges),
            "every edge declares permission posture", "an edge lacks permission posture",
        )
        facts["G08"] = self.fact(
            all(edge["gate"] is not None for edge in self.graph_edges if edge["type"] == "gate"),
            "every gate edge identifies verifier/auditor", "a gate edge lacks gate identity",
        )
        allowed_conditions = set(edge_schema["properties"]["condition_code"]["enum"])
        facts["G09"] = self.fact(
            all(edge["condition_code"] in allowed_conditions for edge in self.graph_edges)
            and len({edge["condition_code"] for edge in self.graph_edges}) >= 5,
            "conditional edges use a closed, non-degenerate condition-code set",
            "condition codes are invalid or degenerate",
        )
        facts["G10"] = self.fact(
            graph_check.passed and graph_suite.passed and workflow["terminal_nodes"],
            "required workflow entry reaches declared terminal",
            "workflow terminal reachability failed",
        )
        graph_tests = (self.root / "tests/test_workflow_graph.py").read_text()
        facts["G11"] = self.fact(
            graph_suite.passed and "orphan" in graph_tests,
            "unexpected orphan validation is tested", "orphan validation test is missing",
        )
        facts["G12"] = self.fact(
            graph_suite.passed and "dead" in graph_tests,
            "unexpected non-terminal dead ends are tested", "dead-end validation is unproven",
        )
        facts["G13"] = self.fact(
            graph_suite.passed and "unbounded_cycle" in graph_tests
            and all(edge["loop_policy"]["max_traversals"] <= 1 for edge in self.graph_edges),
            "cycles require explicit one-traversal bounded policy",
            "bounded cycle policy/test is incomplete",
        )
        facts["G14"] = self.fact(
            graph_suite.passed and "phase_inversion" in graph_tests,
            "illegal phase/layer inversion test passes", "phase inversion validation is unproven",
        )
        stopping = self.graph_source["node_stopping_policies"]
        facts["G15"] = self.fact(
            len(stopping) == 120 and len({item["node"] for item in stopping}) == 120
            and all(item["mode"] in {"natural-stop", "terminal", "human-decision"}
                    for item in stopping),
            "all nodes have explicit natural/terminal/human stopping policy",
            "node stopping policy coverage is incomplete",
        )
        facts["G16"] = self.fact(
            loop_suite.passed and "_plan_snapshot" in loop_text,
            "supported loop planner materializes validated graph paths",
            "supported executable graph planner is unproven",
        )
        facts["G17"] = self.fact(
            graph_suite.passed and len(workflow["fan_outs"][0]["branches"]) >= 3,
            "Product Launch has tested three-lane fan-out", "Product Launch fan-out missing",
        )
        join = workflow["joins"][0]
        facts["G18"] = self.fact(
            graph_suite.passed and len(join["requires"]) >= 3
            and join["policy"] == "all-required",
            "three launch branches converge at typed all-required join",
            "evidence-bearing launch join is incomplete",
        )
        facts["G19"] = self.fact(
            all(join.get(key) for key in (
                "requires", "branch_failure_policy", "timeout_policy", "partial_evidence_policy")),
            "join declares branches, failure, timeout, and partial-evidence policy",
            "join failure/timeout/partial policy is incomplete",
        )
        facts["G20"] = self.fact(
            "tests.test_workflow_graph" in self.ci and "workflow-graph.py --check" in self.ci,
            "graph drift/reachability/cycle/fan-out/join tests are in CI",
            "graph CI wiring is incomplete",
        )

        expected = {
            "%s%02d" % (name[0].upper(), index)
            for name in EXPECTED_DIMENSIONS for index in range(1, 21)
        }
        if set(facts) != expected:
            raise MaturityError(
                "checker control mapping drift: missing=%s extra=%s"
                % (sorted(expected - set(facts)), sorted(set(facts) - expected))
            )
        self._facts = facts
        return facts


def audit(root=ROOT, *, run_dynamic=True, evidence_run_id=None, evidence_root=None,
          timeout=240, evaluated_at=None):
    rubric = validate_rubric(load_json(Path(root) / RUBRIC_PATH.relative_to(ROOT)))
    auditor = Auditor(
        root, run_dynamic=run_dynamic, evidence_run_id=evidence_run_id,
        evidence_root=evidence_root, timeout=timeout,
    )
    facts = auditor.build_facts()
    dimensions = {}
    for name, controls in rubric["dimensions"].items():
        rows, raw, final, failed_hard = score_dimension(
            controls, facts, rubric["control_weight"], rubric["hard_gate_cap"],
        )
        dimensions[name] = {
            "raw_score": raw,
            "final_score": final,
            "score_10": round(final / 10, 1),
            "target_met": final >= rubric["target_score"] and not failed_hard,
            "failed_hard_gates": failed_hard,
            "failed_controls": [row["id"] for row in rows if not row["passed"]],
            "controls": rows,
        }
    achieved = all(item["target_met"] for item in dimensions.values())
    evaluated_at = evaluated_at or dt.datetime.now(dt.timezone.utc)
    if evaluated_at.tzinfo is None:
        raise MaturityError("evaluated_at must include a timezone")
    return {
        "$schema": REPORT_SCHEMA,
        "schema_version": "1.0",
        "evaluated_at": evaluated_at.astimezone(dt.timezone.utc).isoformat().replace(
            "+00:00", "Z"
        ),
        "repository": repository_provenance(Path(root).resolve()),
        "checker": {
            "ref": "scripts/check-engineering-maturity.py",
            "sha256": sha256_bytes(
                (Path(root) / "scripts/check-engineering-maturity.py").read_bytes()
            ),
        },
        "rubric_sha256": sha256_bytes(
            (Path(root) / RUBRIC_PATH.relative_to(ROOT)).read_bytes()
        ),
        "target_score": rubric["target_score"],
        "achieved": achieved,
        "semantic_evidence_run_id": evidence_run_id,
        "semantic_evidence": auditor.semantic_result,
        "dimensions": dimensions,
    }


def write_private_report(path, result):
    path = Path(path)
    if path.parent.is_symlink():
        raise MaturityError("report parent must not be a symlink")
    parent = path.parent.resolve()
    if not parent.is_dir() or parent.is_symlink():
        raise MaturityError("report parent must be an existing real directory")
    target = parent / path.name
    if target.exists() and (target.is_symlink() or not target.is_file()):
        raise MaturityError("report target must be a regular file")
    temporary = parent / (".%s.maturity-tmp" % path.name)
    if temporary.exists() or temporary.is_symlink():
        raise MaturityError("maturity report temporary path already exists")
    raw = (json.dumps(
        result, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False,
    ) + "\n").encode("utf-8")
    try:
        descriptor = os.open(
            temporary,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, target)
        os.chmod(target, 0o600)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def print_human(result):
    for name in ("prompt", "context", "harness", "loop", "graph"):
        item = result["dimensions"][name]
        marker = "PASS" if item["target_met"] else "FAIL"
        print(
            "%s %-7s %.1f/10 (raw=%d, hard=%s, failed=%s)"
            % (
                marker, name, item["score_10"], item["raw_score"],
                ",".join(item["failed_hard_gates"]) or "none",
                ",".join(item["failed_controls"]) or "none",
            )
        )
        for control in item["controls"]:
            if not control["passed"]:
                print("  - %s: %s" % (control["id"], control["evidence"]))
    print("ACHIEVED" if result["achieved"] else "NOT ACHIEVED")


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--semantic-evidence-run-id")
    parser.add_argument("--evidence-root")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--skip-dynamic", action="store_true",
                        help="Do not run tests; dynamic controls fail rather than being assumed")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", help="Atomically write the bounded JSON report with mode 0600")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        result = audit(
            args.root, run_dynamic=not args.skip_dynamic,
            evidence_run_id=args.semantic_evidence_run_id,
            evidence_root=args.evidence_root, timeout=args.timeout,
        )
    except (MaturityError, OSError, ValueError) as exc:
        print("engineering-maturity: %s" % exc, file=sys.stderr)
        return 2
    if args.output:
        try:
            write_private_report(args.output, result)
        except (MaturityError, OSError, ValueError) as exc:
            print("engineering-maturity: %s" % exc, file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print_human(result)
    return 0 if result["achieved"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
