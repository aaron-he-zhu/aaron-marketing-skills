#!/usr/bin/env python3
"""Behavioral tests for the semantic-adapter path of scripts/run-behavior-evals.py.

Exercises run_adapter against synthetic NDJSON adapters (pure stdlib python
scripts in a temp dir) with a single real eval case selected by ID.
"""
from __future__ import annotations

import copy
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "routing-outreach-vs-contract-helper-outreach-manager-001"


def python_command(script):
    """Bind fixtures to the same already-isolated interpreter as the runner."""
    return shlex.join([sys.executable, str(script)])

PASS_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": True, "evidence": "fixture ok"}))
"""

FAIL_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": False, "evidence": "fixture failure"}))
"""

DROP_ADAPTER = """\
import sys
for line in sys.stdin:
    pass
"""

GARBAGE_ADAPTER = """\
print("not json")
"""

BAD_SHAPE_ADAPTER = """\
import json, sys
for line in sys.stdin:
    line = line.strip()
    if line:
        case = json.loads(line)
        print(json.dumps({"id": case["id"], "passed": True}))
"""

CRASH_ADAPTER = """\
import sys
sys.exit(3)
"""

PASS_V2_ADAPTER = """\
import hashlib, json, sys
for line in sys.stdin:
    if not line.strip():
        continue
    request = json.loads(line)
    assertions = []
    for index, _ in enumerate(request["case"]["expected_behavior"], 1):
        assertions.append({"id": "expected-%d" % index, "kind": "expected", "verdict": "met", "evidence": "observed"})
    for index, _ in enumerate(request["case"]["failure_modes"], 1):
        assertions.append({"id": "forbidden-%d" % index, "kind": "forbidden", "verdict": "not-observed", "evidence": "not observed"})
    candidate_sha256 = "3" * 64
    judge_attempt = {
        "attempt": 1, "response_sha256": "4" * 64, "size_bytes": 1,
        "disposition": "accepted", "diagnostic_code": None,
    }
    judge_attempts = [judge_attempt]
    judge_sha256 = judge_attempts[-1]["response_sha256"] if judge_attempts else hashlib.sha256(b"").hexdigest()
    response_sha256 = hashlib.sha256(json.dumps({
        "candidate_response_sha256": candidate_sha256,
        "judge_attempts": judge_attempts,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    print(json.dumps({
        "kind": "behavior-eval-result", "protocol_version": "2.0",
        "case_id": request["case"]["id"], "request_sha256": request["request_sha256"],
        "outcome": "passed",
        "execution_provenance": {
            "execution_mode": "real", "adapter_name": "fixture-adapter", "adapter_version": "2.0.0",
            "host_name": "fixture-host", "host_version": "1.0.0", "model_provider": "fixture",
            "model_id": "fixture-model", "judge_model_id": "fixture-judge", "model_revision": None,
            "adapter_implementation_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
            "prompt_template_version": "1.0.0", "prompt_template_sha256": "1" * 64,
            "parameters_sha256": "2" * 64, "candidate_response_sha256": candidate_sha256,
            "judge_response_sha256": judge_sha256, "judge_attempts": judge_attempts,
            "response_sha256": response_sha256,
            "started_at": "2026-07-19T10:00:00Z", "ended_at": "2026-07-19T10:00:01Z",
            "latency_ms": 1000
        },
        "assertions": assertions, "failures": []
    }))
"""

PASS_V3_ADAPTER = """\
import hashlib, json, sys
for line in sys.stdin:
    if not line.strip():
        continue
    request = json.loads(line)
    judge = request["judge_contract"]
    assertions = []
    for index, _ in enumerate(judge["assertions"], 1):
        assertions.append({"id": "expected-%d" % index, "kind": "expected", "verdict": "met", "evidence": "observed"})
    for index, _ in enumerate(judge["must_not"], 1):
        assertions.append({"id": "forbidden-%d" % index, "kind": "forbidden", "verdict": "not-observed", "evidence": "not observed"})
    candidate_sha256 = "3" * 64
    judge_attempts = [{
        "attempt": 1, "response_sha256": "4" * 64, "size_bytes": 1,
        "disposition": "accepted", "diagnostic_code": None,
    }]
    response_sha256 = hashlib.sha256(json.dumps({
        "candidate_response_sha256": candidate_sha256,
        "judge_attempts": judge_attempts,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    execution = request["execution"]
    assembly = execution["assembly_binding"]
    context = {
        "prompt_profile": execution["prompt_profile"],
        "host_profile": execution["host_profile"],
        "toolset_id": execution["toolset_id"],
        "toolset_sha256": execution["toolset_sha256"],
        "candidate_context_sha256": "5" * 64,
        "candidate_sources_sha256": (
            assembly["model_resources_sha256"] if assembly is not None else "7" * 64
        ),
        "assembly_sha256": None, "assembly_signature": None, "context_signature": None,
        "host_catalog_sha256": None, "prompt_policy_sha256": None,
        "context_modules_sha256": None,
        "capsule_index_sha256": request["routing_index"]["capsule_index"]["sha256"],
        "model_body_bytes": None, "model_reduction_ratio": None,
        "model_resources_sha256": None,
    }
    if assembly is not None:
        context.update({key: value for key, value in assembly.items() if key != "model_resources"})
    print(json.dumps({
        "kind": "behavior-eval-result", "protocol_version": "3.0",
        "case_id": request["case"]["id"], "request_sha256": request["request_sha256"],
        "outcome": "passed",
        "routing": {
            "selected_skill": judge["expected_route"], "expected_skill": judge["expected_route"],
            "correct": True, "routing_index_sha256": request["routing_index"]["index_sha256"],
            "routing_response_sha256": "6" * 64,
        },
        "execution_provenance": {
            "execution_mode": "real", "adapter_name": "fixture-adapter", "adapter_version": "3.0.0",
            "host_name": "fixture-host", "host_version": "1.0.0", "model_provider": "fixture",
            "model_id": execution["model_id"], "judge_model_id": execution["judge_model_id"],
            "model_revision": None, "judge_model_provider": "fixture",
            "judge_model_revision": None,
            "adapter_implementation_sha256": hashlib.sha256(open(__file__, "rb").read()).hexdigest(),
            "prompt_template_version": "3.0.0", "prompt_template_sha256": "1" * 64,
            "parameters_sha256": "2" * 64, "candidate_response_sha256": candidate_sha256,
            "judge_response_sha256": "4" * 64, "judge_attempts": judge_attempts,
            "response_sha256": response_sha256,
            "started_at": "2026-08-01T00:00:00Z", "ended_at": "2026-08-01T00:00:01Z",
            "latency_ms": 1000
        },
        "provider_metrics": {"input_tokens": None, "output_tokens": None, "total_tokens": None, "latency_ms": None, "tool_calls": None},
        "context_binding": context,
        "stage_latency_ms": {"routing_ms": 100, "execution_ms": 500, "judge_ms": 400},
        "assertions": assertions, "failures": []
    }))
"""

BAD_HASH_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    '"request_sha256": request["request_sha256"]', '"request_sha256": "0" * 64'
)
SIMULATED_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    '"execution_mode": "real"', '"execution_mode": "simulated"'
)
MISSING_ASSERTION_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    '"assertions": assertions, "failures": []', '"assertions": assertions[:-1], "failures": []'
)
BEHAVIOR_FAIL_V2_ADAPTER = (
    PASS_V2_ADAPTER
    .replace('"verdict": "met"', '"verdict": "violated"', 1)
    .replace('"outcome": "passed"', '"outcome": "behavior-failed"')
    .replace(
        '"assertions": assertions, "failures": []',
        '"assertions": assertions, "failures": [{"code": '
        '"PROMPT_REQUIRED_BEHAVIOR_MISSING", "class": "prompt", '
        '"retryable": False, "summary": "required behavior missing"}]',
    )
)
HOST_FAIL_V2_ADAPTER = (
    PASS_V2_ADAPTER
    .replace("judge_attempts = [judge_attempt]", "judge_attempts = []")
    .replace('"verdict": "met"', '"verdict": "not-observed"')
    .replace('"outcome": "passed"', '"outcome": "host-failed"')
    .replace(
        '"assertions": assertions, "failures": []',
        '"assertions": assertions, "failures": [{"code": "HOST_TIMEOUT", '
        '"class": "host", "retryable": True, "summary": "host timed out"}]',
    )
)
BAD_FAILURE_CLASS_V2_ADAPTER = BEHAVIOR_FAIL_V2_ADAPTER.replace(
    '"class": "prompt"', '"class": "host"'
)
HOST_WITH_INCONCLUSIVE_V2_ADAPTER = HOST_FAIL_V2_ADAPTER.replace(
    '"code": "HOST_TIMEOUT", "class": "host", "retryable": True',
    '"code": "EVALUATOR_INCONCLUSIVE", "class": "unknown", "retryable": False',
)
INCONCLUSIVE_WITH_DETERMINISTIC_FAILURE_V2_ADAPTER = (
    BEHAVIOR_FAIL_V2_ADAPTER
    .replace('"outcome": "behavior-failed"', '"outcome": "inconclusive"')
    .replace(
        '"code": "PROMPT_REQUIRED_BEHAVIOR_MISSING", "class": "prompt", ',
        '"code": "EVALUATOR_INCONCLUSIVE", "class": "unknown", ',
    )
)
VALID_INCONCLUSIVE_V2_ADAPTER = (
    PASS_V2_ADAPTER
    .replace('"verdict": "met"', '"verdict": "not-observed"', 1)
    .replace('"outcome": "passed"', '"outcome": "inconclusive"')
    .replace(
        '"assertions": assertions, "failures": []',
        '"assertions": assertions, "failures": [{"code": '
        '"EVALUATOR_INCONCLUSIVE", "class": "unknown", "retryable": False, '
        '"summary": "candidate evidence is insufficient"}]',
    )
)
RETRYABLE_BEHAVIOR_V2_ADAPTER = BEHAVIOR_FAIL_V2_ADAPTER.replace(
    '"retryable": False', '"retryable": True', 1,
)
RETRYABLE_INCONCLUSIVE_V2_ADAPTER = VALID_INCONCLUSIVE_V2_ADAPTER.replace(
    '"retryable": False', '"retryable": True', 1,
)
ADAPTER_FAIL_V2_ADAPTER = (
    HOST_FAIL_V2_ADAPTER
    .replace('"outcome": "host-failed"', '"outcome": "adapter-failed"')
    .replace(
        '"code": "HOST_TIMEOUT", "class": "host", "retryable": True',
        '"code": "ADAPTER_PROTOCOL", "class": "adapter", "retryable": False',
    )
)
LEDGER_TAMPER_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    "    print(json.dumps({\n",
    "    judge_attempts[0]['size_bytes'] = 2\n    print(json.dumps({\n",
)
EMPTY_ACCEPTED_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    '"attempt": 1, "response_sha256": "4" * 64, "size_bytes": 1,',
    '"attempt": 1, "response_sha256": "4" * 64, "size_bytes": 0,',
)
ACCEPTED_NOT_LAST_V2_ADAPTER = PASS_V2_ADAPTER.replace(
    "    judge_attempts = [judge_attempt]\n",
    "    judge_attempts = [judge_attempt, {\n"
    "        'attempt': 2, 'response_sha256': '6' * 64, 'size_bytes': 1,\n"
    "        'disposition': 'protocol-rejected', 'diagnostic_code': 'JUDGE_INVALID_JSON',\n"
    "    }]\n",
)


def load_module():
    path = ROOT / "scripts" / "run-behavior-evals.py"
    spec = importlib.util.spec_from_file_location("run_behavior_evals", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_module()

    def run_with(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "adapter.py"
            script.write_text(textwrap.dedent(source), encoding="utf-8")
            return self.module.run_adapter(
                python_command(script), {CASE_ID}, 60)

    @staticmethod
    def v2_selection(count=1):
        case_template = {
            "type": "eval-case",
            "case_provenance": "simulated",
            "evidence_binding": None,
            "target_skill": "outreach-manager",
            "scenario": "A bounded semantic adapter fixture.",
            "input_summary": "Return the expected behavior without the forbidden behavior.",
            "expected_behavior": ["Return a bounded plan."],
            "failure_modes": ["Claim an external mutation occurred."],
            "source_ref": "evals/outreach-manager/cases.md",
            "source_line": 1,
            "source_group": "authored",
        }
        cases = []
        reasons = {}
        for index in range(1, count + 1):
            case = dict(case_template)
            case["id"] = "fixture-v2-%03d" % index
            case["case_sha256"] = ("%064x" % index)[-64:]
            cases.append(case)
            reasons[case["id"]] = ["filter:fixture"]
        return {
            "profile": "filtered",
            "cases": cases,
            "case_ids": [case["id"] for case in cases],
            "selection_reasons": reasons,
            "provenance": {"simulated": count, "real": 0},
        }

    def run_v2_with(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "adapter.py"
            script.write_text(textwrap.dedent(source), encoding="utf-8")
            return self.module.run_adapter_v2(
                python_command(script), self.v2_selection(), 60,
            )

    def run_v3_with(self, source, *, count=1, evidence_run_id=None, evidence_root=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        script = Path(temporary.name) / "adapter.py"
        script.write_text(textwrap.dedent(source), encoding="utf-8")
        return self.module.run_adapter_v3(
            python_command(script), self.v2_selection(count), 60,
            host_profile="claude-code-plugin-host",
            model_id="fixture-model", judge_model_id="fixture-judge",
            evidence_run_id=evidence_run_id,
            evidence_root=(ROOT if evidence_root is None else evidence_root),
        )

    def test_fixture_commands_bind_the_current_isolated_interpreter(self):
        command = shlex.split(python_command("fixture adapter.py"))
        self.assertEqual(command, [sys.executable, "fixture adapter.py"])
        self.assertEqual(
            Path(command[0]).resolve(strict=True),
            Path(self.module.sys.executable).resolve(strict=True),
        )

    def test_passing_adapter_returns_no_failures(self):
        self.assertEqual([], self.run_with(PASS_ADAPTER))

    def test_existing_adapter_command_defaults_to_protocol_v1(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "adapter.py"
            script.write_text(textwrap.dedent(PASS_ADAPTER), encoding="utf-8")
            self.assertEqual(
                0,
                self.module.main([
                    "--adapter-only",
                    "--adapter-command", python_command(script),
                    "--case", CASE_ID,
                ]),
            )

    def test_failing_case_is_reported(self):
        failures = self.run_with(FAIL_ADAPTER)
        self.assertEqual(["semantic adapter failed 1/1 cases"], failures)

    def test_dropped_case_is_a_coverage_mismatch(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(DROP_ADAPTER)
        self.assertIn("coverage mismatch", str(ctx.exception))

    def test_non_json_stdout_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(GARBAGE_ADAPTER)
        self.assertIn("not JSON", str(ctx.exception))

    def test_missing_evidence_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(BAD_SHAPE_ADAPTER)
        self.assertIn("evidence is required", str(ctx.exception))

    def test_adapter_crash_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_with(CRASH_ADAPTER)
        self.assertIn("exited 3", str(ctx.exception))

    def test_v2_passing_adapter_carries_real_execution_and_case_provenance(self):
        self.assertEqual([], self.run_v2_with(PASS_V2_ADAPTER))

    def test_v3_passing_adapter_runs_official_batch_path(self):
        self.assertEqual([], self.run_v3_with(PASS_V3_ADAPTER, count=2))

    def test_v3_evidence_manifest_binds_protocol_and_schema(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence_root = Path(tmp) / "evidence-root"
            evidence_root.mkdir()
            run_id = "123e4567-e89b-42d3-a456-426614174099"
            self.assertEqual([], self.run_v3_with(
                PASS_V3_ADAPTER, count=2, evidence_run_id=run_id,
                evidence_root=evidence_root,
            ))
            evidence = evidence_root / "memory" / "runs" / run_id / "semantic-eval"
            manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
            completion = json.loads((evidence / "completion.json").read_text(encoding="utf-8"))
            self.assertEqual("3.0", manifest["protocol_version"])
            self.assertEqual("evals/behavior-adapter-v3.schema.json", manifest["protocol_schema"]["ref"])
            self.assertEqual(
                hashlib.sha256((ROOT / "evals/behavior-adapter-v3.schema.json").read_bytes()).hexdigest(),
                manifest["protocol_schema"]["sha256"],
            )
            self.assertTrue(completion["complete"])
            self.assertEqual(2, completion["request_count"])

    def test_v3_cli_dispatches_to_official_entry_point(self):
        with mock.patch.object(self.module, "run_adapter_v3", return_value=[]) as run:
            code = self.module.main([
                "--adapter-only", "--adapter-protocol", "3",
                "--case", CASE_ID,
                "--adapter-command", "python3 scripts/adapters/codex-behavior-adapter.py",
                "--adapter-implementation-ref", "scripts/adapters/codex-behavior-adapter.py",
                "--evidence-run-id", "123e4567-e89b-42d3-a456-426614174098",
                "--host-profile", "claude-code-plugin-host",
                "--model-id", "fixture-model", "--judge-model-id", "fixture-judge",
            ])
        self.assertEqual(0, code)
        run.assert_called_once()

    def test_v2_auditor_request_expands_every_bound_prompt_source(self):
        selection = self.module.select_semantic_cases(
            "smoke", {"derived-content-quality-auditor-missing-evidence"}
        )
        request = self.module.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )[0]
        references = {item["ref"] for item in request["prompt_contract"]["source_refs"]}
        self.assertNotIn("references/prompt-contracts/content-quality-auditor.json", references)
        self.assertIn("references/system-catalog.json", references)
        self.assertIn("references/framework-catalog.json", references)
        self.assertIn("references/auditor-runbook.md", references)
        self.assertIn("references/core-eeat-benchmark.md", references)
        self.assertIn("references/skill-contracts/content-quality-auditor.json", references)
        self.assertIn("references/skill-contract.md", references)

    def test_v2_authored_case_consumes_machine_contract_and_runtime_context(self):
        selection = self.module.select_semantic_cases(
            "smoke", {"routing-chain-visited-set-001"}
        )
        request = self.module.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )[0]
        contract = request["prompt_contract"]
        references = {item["ref"] for item in contract["source_refs"]}
        self.assertEqual("machine-skill", contract["kind"])
        self.assertEqual("skill:keyword-research", contract["contract_id"])
        self.assertEqual(
            "references/skill-contracts/keyword-research.json", contract["contract_ref"],
        )
        self.assertIn(contract["contract_ref"], references)
        self.assertIn("seo-geo/survey/keyword-research/SKILL.md", references)
        self.assertIn("references/skill-contract.md", references)

    def test_auto_routing_case_binds_router_and_primary_command_without_case_corpus(self):
        selection = self.module.select_semantic_cases(
            "smoke", {"paid-prelaunch-account-audit-001"}
        )
        request = self.module.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )[0]
        references = {item["ref"] for item in request["prompt_contract"]["source_refs"]}
        self.assertIn("commands/auto.md", references)
        self.assertIn("commands/ad.md", references)
        self.assertIn("references/aaron-product-api-contract.md", references)
        self.assertNotIn("evals/auto-routing-scenarios.source.md", references)
        self.assertNotIn("references/auto-routing/ad.md", references)

    def test_nightly_700_requests_are_constructible_with_bounded_refs(self):
        selection = self.module.select_semantic_cases("nightly", set())
        self.assertEqual("nightly", selection["profile"])
        self.assertEqual(700, len(selection["cases"]))

        requests = self.module.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )
        self.assertEqual(700, len(requests))
        self.assertEqual(
            [case["id"] for case in selection["cases"]],
            [request["case"]["id"] for request in requests],
        )
        self.assertEqual(700, len({request["request_sha256"] for request in requests}))
        for request in requests:
            references = [
                item["ref"] for item in request["prompt_contract"]["source_refs"]
            ]
            self.assertLessEqual(1, len(references), request["case"]["id"])
            self.assertLessEqual(len(references), 32, request["case"]["id"])
            self.assertEqual(len(references), len(set(references)), request["case"]["id"])

    def test_memory_management_auto_requests_bind_seo_command_without_case_corpus(self):
        case_ids = {"auto-memory-cleanup-001", "auto-privacy-erasure-001"}
        selection = self.module.select_semantic_cases("nightly", case_ids)
        requests = self.module.build_v2_requests(
            selection["cases"], selection["profile"], selection["selection_reasons"]
        )
        self.assertEqual(case_ids, {request["case"]["id"] for request in requests})
        self.assertEqual(2, len(requests))
        for request in requests:
            self.assertEqual("memory-management", request["target"]["skill"])
            self.assertEqual("auto-routing", request["case"]["source_group"])
            references = {
                item["ref"] for item in request["prompt_contract"]["source_refs"]
            }
            self.assertIn("commands/auto.md", references)
            self.assertIn("commands/seo-geo.md", references)
            self.assertFalse(
                any(reference.startswith("evals/") for reference in references),
                references,
            )
            self.assertFalse(
                any(reference.startswith("references/auto-routing/")
                    for reference in references),
                references,
            )

    def test_prompt_source_expansion_rejects_33_unique_refs(self):
        paths = [
            path for path in sorted((ROOT / "references").rglob("*"))
            if path.is_file() and not path.is_symlink()
        ][:33]
        self.assertEqual(33, len(paths))
        bindings = [
            {
                "ref": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            for path in paths
        ]
        with self.assertRaisesRegex(
                self.module.BehaviorEvalError, "1\\.\\.32 unique bindings"):
            self.module._merge_source_refs(bindings)

    def test_machine_contract_index_hash_drift_fails_closed(self):
        index, digest = self.module.load_project_json(self.module.MACHINE_CONTRACT_INDEX_REF)
        stale = copy.deepcopy(index)
        stale["contracts"][0]["contract_sha256"] = "0" * 64
        original = self.module.load_project_json

        def load(reference):
            if reference == self.module.MACHINE_CONTRACT_INDEX_REF:
                return stale, digest
            return original(reference)

        with mock.patch.object(self.module, "load_project_json", side_effect=load):
            with self.assertRaises(self.module.BehaviorEvalError) as ctx:
                self.module.load_skill_machine_contracts()
        self.assertIn("hash drift", str(ctx.exception))

    def test_prompt_contract_index_is_required_and_cannot_be_a_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            (project / "references" / "prompt-contracts").mkdir(parents=True)
            with mock.patch.object(self.module, "ROOT", project):
                with self.assertRaises(self.module.BehaviorEvalError):
                    self.module.load_auditor_prompt_contracts()
            outside = Path(tmp) / "outside.json"
            outside.write_text("{}\n", encoding="utf-8")
            (project / "references" / "prompt-contracts" / "index.json").symlink_to(outside)
            with mock.patch.object(self.module, "ROOT", project):
                with self.assertRaises(self.module.BehaviorEvalError):
                    self.module.load_auditor_prompt_contracts()

    def test_prompt_contract_index_cannot_swap_skill_bindings(self):
        index_ref = "references/prompt-contracts/index.json"
        index, digest = self.module.load_project_json(index_ref)
        swapped = copy.deepcopy(index)
        swapped["contracts"][0]["skill"] = swapped["contracts"][1]["skill"]
        original = self.module.load_project_json

        def load(reference):
            if reference == index_ref:
                return swapped, digest
            return original(reference)

        with mock.patch.object(self.module, "load_project_json", side_effect=load):
            with self.assertRaises(self.module.BehaviorEvalError) as ctx:
                self.module.load_auditor_prompt_contracts()
        self.assertIn("index entry", str(ctx.exception))

    def test_selected_derived_case_must_match_current_contract_variant(self):
        selection = self.module.select_semantic_cases(
            "smoke", {"derived-content-quality-auditor-missing-evidence"}
        )
        stale = copy.deepcopy(selection["cases"])
        stale[0]["expected_behavior"].append("Stale assertion injected after selection.")
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.module.build_v2_requests(
                stale, selection["profile"], selection["selection_reasons"]
            )
        self.assertIn("current prompt-contract variant", str(ctx.exception))

    def test_v2_request_hash_mismatch_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(BAD_HASH_V2_ADAPTER)
        self.assertIn("request_sha256", str(ctx.exception))

    def test_v2_incomplete_assertion_coverage_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(MISSING_ASSERTION_V2_ADAPTER)
        self.assertIn("assertion coverage", str(ctx.exception))

    def test_v2_judge_ledger_tamper_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(LEDGER_TAMPER_V2_ADAPTER)
        self.assertIn("full judge ledger", str(ctx.exception))

    def test_v2_accepted_judge_attempt_cannot_be_empty(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(EMPTY_ACCEPTED_V2_ADAPTER)
        self.assertIn("cannot be empty", str(ctx.exception))

    def test_v2_terminal_outcome_requires_accepted_final_attempt(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(ACCEPTED_NOT_LAST_V2_ADAPTER)
        self.assertIn("accepted final attempt", str(ctx.exception))

    def test_v2_simulated_execution_cannot_satisfy_real_profile(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(SIMULATED_V2_ADAPTER)
        self.assertIn("requires real execution", str(ctx.exception))

    def test_v2_behavior_failure_is_reported_separately(self):
        self.assertEqual(
            ["semantic adapter v2 failed: behavior=1 inconclusive=0 host=0 adapter=0 total=1"],
            self.run_v2_with(BEHAVIOR_FAIL_V2_ADAPTER),
        )

    def test_v2_host_failure_is_reported_separately(self):
        self.assertEqual(
            ["semantic adapter v2 failed: behavior=0 inconclusive=0 host=1 adapter=0 total=1"],
            self.run_v2_with(HOST_FAIL_V2_ADAPTER),
        )

    def test_v2_adapter_failure_is_reported_separately(self):
        self.assertEqual(
            ["semantic adapter v2 failed: behavior=0 inconclusive=0 host=0 adapter=1 total=1"],
            self.run_v2_with(ADAPTER_FAIL_V2_ADAPTER),
        )

    def test_v2_host_failure_cannot_smuggle_an_inconclusive_code(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(HOST_WITH_INCONCLUSIVE_V2_ADAPTER)
        self.assertIn("only HOST", str(ctx.exception))

    def test_v2_failure_class_mismatch_fails_closed(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(BAD_FAILURE_CLASS_V2_ADAPTER)
        self.assertIn("failure class", str(ctx.exception))

    def test_v2_inconclusive_requires_unknown_without_deterministic_failure(self):
        with self.assertRaises(self.module.BehaviorEvalError) as ctx:
            self.run_v2_with(INCONCLUSIVE_WITH_DETERMINISTIC_FAILURE_V2_ADAPTER)
        self.assertIn("unknown evidence", str(ctx.exception))
        self.assertEqual(
            ["semantic adapter v2 failed: behavior=0 inconclusive=1 host=0 adapter=0 total=1"],
            self.run_v2_with(VALID_INCONCLUSIVE_V2_ADAPTER),
        )

    def test_v2_behavior_and_inconclusive_failures_are_not_retryable(self):
        for source in (RETRYABLE_BEHAVIOR_V2_ADAPTER, RETRYABLE_INCONCLUSIVE_V2_ADAPTER):
            with self.subTest(source=source[:80]):
                with self.assertRaises(self.module.BehaviorEvalError) as ctx:
                    self.run_v2_with(source)
                self.assertIn("cannot be retryable", str(ctx.exception))

    def test_v2_700_case_batches_are_persisted_without_loss(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            evidence_root = base / "evidence-root"
            evidence_root.mkdir()
            script = base / "adapter.py"
            script.write_text(textwrap.dedent(PASS_V2_ADAPTER), encoding="utf-8")
            run_id = "123e4567-e89b-42d3-a456-426614174000"
            selection = self.v2_selection(700)
            self.assertEqual(
                [],
                self.module.run_adapter_v2(
                    python_command(script), selection, 60, batch_size=113,
                    evidence_run_id=run_id, evidence_root=evidence_root,
                ),
            )
            evidence = evidence_root / "memory" / "runs" / run_id / "semantic-eval"
            completion = json.loads((evidence / "completion.json").read_text(encoding="utf-8"))
            manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(700, completion["request_count"])
            self.assertEqual(700, completion["attempt_count"])
            self.assertEqual(700, completion["terminal_count"])
            self.assertTrue(completion["complete"])
            self.assertEqual(700, len((evidence / "requests.ndjson").read_text(encoding="utf-8").splitlines()))
            self.assertEqual(700, len((evidence / "results.ndjson").read_text(encoding="utf-8").splitlines()))
            self.assertEqual(
                hashlib.sha256(script.read_bytes()).hexdigest(),
                manifest["adapter_command_identity"]["implementation"]["sha256"],
            )
            self.assertEqual(
                selection["provenance"], manifest["selection_provenance"]
            )
            self.assertEqual(
                self.module.sha256_json({
                    "profile": selection["profile"],
                    "case_ids": selection["case_ids"],
                    "provenance": selection["provenance"],
                }),
                manifest["selection_sha256"],
            )
            self.assertEqual(
                self.module.sha256_json(
                    manifest["adapter_command_identity"]["logical_argv"]
                ),
                manifest["adapter_command_sha256"],
            )
            self.assertEqual(
                hashlib.sha256((ROOT / "scripts/run-behavior-evals.py").read_bytes()).hexdigest(),
                manifest["runner"]["sha256"],
            )
            self.assertEqual(
                hashlib.sha256((ROOT / "evals/behavior-adapter-v2.schema.json").read_bytes()).hexdigest(),
                manifest["protocol_schema"]["sha256"],
            )

    def test_v2_resume_skips_terminal_prefix_after_later_batch_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            evidence_root = base / "evidence-root"
            evidence_root.mkdir()
            marker = base / "fail-once.marker"
            source = PASS_V2_ADAPTER.replace(
                "import hashlib, json, sys\n",
                "import hashlib, json, sys\nfrom pathlib import Path\nmarker = Path(%r)\n" % str(marker),
            ).replace(
                "    request = json.loads(line)\n",
                "    request = json.loads(line)\n"
                "    if request['case']['id'] == 'fixture-v2-002' and not marker.exists():\n"
                "        marker.write_text('failed once', encoding='utf-8')\n"
                "        sys.exit(7)\n",
            )
            script = base / "adapter.py"
            script.write_text(textwrap.dedent(source), encoding="utf-8")
            command = python_command(script)
            run_id = "123e4567-e89b-42d3-a456-426614174001"
            selection = self.v2_selection(3)
            with self.assertRaises(self.module.BehaviorEvalError) as ctx:
                self.module.run_adapter_v2(
                    command, selection, 60, batch_size=1,
                    evidence_run_id=run_id, evidence_root=evidence_root,
                )
            self.assertIn("exited 7", str(ctx.exception))
            results = (
                evidence_root / "memory" / "runs" / run_id
                / "semantic-eval" / "results.ndjson"
            )
            self.assertEqual(1, len(results.read_text(encoding="utf-8").splitlines()))
            self.assertEqual(
                [],
                self.module.run_adapter_v2(
                    command, selection, 60, batch_size=1, evidence_run_id=run_id,
                    resume_evidence=True, evidence_root=evidence_root,
                ),
            )
            self.assertEqual(3, len(results.read_text(encoding="utf-8").splitlines()))
            completion = json.loads(
                results.with_name("completion.json").read_text(encoding="utf-8")
            )
            self.assertTrue(completion["complete"])
            self.assertEqual(3, completion["terminal_count"])
            script.write_text(textwrap.dedent(source) + "\n# implementation drift\n", encoding="utf-8")
            with self.assertRaises(self.module.BehaviorEvalError) as ctx:
                self.module.run_adapter_v2(
                    command, selection, 60, batch_size=1, evidence_run_id=run_id,
                    resume_evidence=True, evidence_root=evidence_root,
                )
            self.assertIn("manifest does not match", str(ctx.exception))

    def test_v2_cli_requires_an_explicit_project_implementation_binding(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                self.module.main([
                    "--adapter-only", "--adapter-protocol", "2",
                    "--adapter-command", python_command(
                        "scripts/adapters/codex-behavior-adapter.py"
                    ),
                    "--evidence-run-id", "123e4567-e89b-42d3-a456-426614174002",
                ])
        self.assertEqual(2, ctx.exception.code)

    def test_explicit_project_adapter_cannot_be_a_dummy_argv_argument(self):
        with tempfile.TemporaryDirectory() as tmp:
            dummy = Path(tmp) / "dummy.py"
            dummy.write_text("raise SystemExit(0)\n", encoding="utf-8")
            with self.assertRaisesRegex(
                    self.module.BehaviorEvalError, "must be argv\\[1\\]"):
                self.module.bind_adapter_command(
                    [
                        self.module.sys.executable,
                        str(dummy),
                        "scripts/adapters/codex-behavior-adapter.py",
                    ],
                    implementation_ref="scripts/adapters/codex-behavior-adapter.py",
                )

    def test_official_project_adapter_binds_current_python_and_runtime_schemas(self):
        command, identity, snapshots = self.module._bind_adapter_command_details(
            [
                self.module.sys.executable,
                "scripts/adapters/codex-behavior-adapter.py",
            ],
            implementation_ref="scripts/adapters/codex-behavior-adapter.py",
        )
        self.assertEqual(1, identity["implementation"]["argv_index"])
        self.assertEqual(command, identity["logical_argv"])
        self.assertEqual(
            "isolated-staged-current-python-script",
            identity["execution_binding"]["kind"],
        )
        self.assertEqual(["-I", "-S"], identity["execution_binding"]["python_flags"])
        self.assertEqual(
            list(self.module.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES),
            [item["ref"] for item in identity["runtime_dependencies"]],
        )
        self.assertEqual("private-python-runtime-v1", identity["staged_runtime"]["layout_version"])
        with self.module.stage_bound_adapter(command, identity, snapshots) as staged:
            staged_command, environment, stage_root = staged
            self.assertEqual(["-I", "-S"], staged_command[1:3])
            self.assertNotEqual(
                str(ROOT / self.module.OFFICIAL_PROJECT_ADAPTER_REF), staged_command[3],
            )
            self.assertEqual(
                set(environment),
                set(environment) & set(self.module.OFFICIAL_ADAPTER_ENVIRONMENT_ALLOWLIST),
            )
            self.assertFalse(any(key.startswith("PYTHON") for key in environment))
            self.assertEqual(stage_root, Path(staged_command[3]).parents[2])
            self.module.verify_bound_adapter_command(staged_command, identity)

    def test_official_adapter_bootstrap_ignores_pythonpath_sitecustomize(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            marker = base / "sitecustomize-ran"
            poison = base / "poison"
            poison.mkdir()
            (poison / "sitecustomize.py").write_text(
                "from pathlib import Path\n"
                "Path(%r).write_text('ran', encoding='utf-8')\n"
                "raise SystemExit(73)\n" % str(marker),
                encoding="utf-8",
            )
            codex = base / "codex"
            codex.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
            os.chmod(codex, 0o700)
            command, identity, snapshots = self.module._bind_adapter_command_details(
                [
                    self.module.sys.executable,
                    self.module.OFFICIAL_PROJECT_ADAPTER_REF,
                    "--codex-bin", str(codex),
                    "--codex-sha256", hashlib.sha256(codex.read_bytes()).hexdigest(),
                    "--model", "fixture-model",
                ],
                implementation_ref=self.module.OFFICIAL_PROJECT_ADAPTER_REF,
            )
            with mock.patch.dict(
                    os.environ,
                    {"PYTHONPATH": str(poison), "PYTHONSTARTUP": str(poison / "sitecustomize.py")},
                    clear=False):
                with self.module.stage_bound_adapter(command, identity, snapshots) as staged:
                    staged_command, environment, stage_root = staged
                    completed = subprocess.run(
                        staged_command, cwd=stage_root, env=environment, input="", text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                    )
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertFalse(marker.exists())

    def test_official_adapter_rejects_caller_supplied_project_root_override(self):
        for override in ("--project-root", "--project-root=/tmp/evil"):
            command = [
                self.module.sys.executable,
                self.module.OFFICIAL_PROJECT_ADAPTER_REF,
                override,
            ]
            if override == "--project-root":
                command.append("/tmp/evil")
            with self.subTest(override=override), self.assertRaisesRegex(
                    self.module.BehaviorEvalError, "reserved to the isolated runner"):
                self.module.bind_adapter_command(
                    command,
                    implementation_ref=self.module.OFFICIAL_PROJECT_ADAPTER_REF,
                )

    def test_official_adapter_schema_source_swap_cannot_reach_staged_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "project"
            adapter = project / self.module.OFFICIAL_PROJECT_ADAPTER_REF
            candidate = project / self.module.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES[0]
            adapter.parent.mkdir(parents=True)
            candidate.parent.mkdir(parents=True, exist_ok=True)
            adapter.write_text(
                "from pathlib import Path\n"
                "root = Path(__file__).resolve().parents[2]\n"
                "print((root / %r).read_text(encoding='utf-8'))\n" % str(
                    self.module.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES[0]
                ),
                encoding="utf-8",
            )
            for index, dependency in enumerate(
                    self.module.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES):
                dependency_path = project / dependency
                dependency_path.parent.mkdir(parents=True, exist_ok=True)
                dependency_path.write_text(
                    "bound-schema" if index == 0 else "bound-dependency-%d" % index,
                    encoding="utf-8",
                )
            with mock.patch.object(self.module, "ROOT", project):
                command, identity, snapshots = self.module._bind_adapter_command_details(
                    [self.module.sys.executable, self.module.OFFICIAL_PROJECT_ADAPTER_REF],
                    implementation_ref=self.module.OFFICIAL_PROJECT_ADAPTER_REF,
                )
                with self.module.stage_bound_adapter(command, identity, snapshots) as staged:
                    staged_command, environment, stage_root = staged
                    candidate.write_text("transient-attacker-schema", encoding="utf-8")
                    try:
                        completed = subprocess.run(
                            staged_command, cwd=stage_root, env=environment, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
                        )
                    finally:
                        candidate.write_text("bound-schema", encoding="utf-8")
                    self.module.verify_bound_adapter_command(staged_command, identity)
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertEqual("bound-schema", completed.stdout.strip())

    def test_staged_runtime_dependency_mutation_fails_batch_verification(self):
        command, identity, snapshots = self.module._bind_adapter_command_details(
            [self.module.sys.executable, self.module.OFFICIAL_PROJECT_ADAPTER_REF],
            implementation_ref=self.module.OFFICIAL_PROJECT_ADAPTER_REF,
        )
        with self.module.stage_bound_adapter(command, identity, snapshots) as staged:
            staged_command, _environment, stage_root = staged
            dependency = (
                stage_root / self.module.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES[0]
            )
            os.chmod(dependency.parent, 0o700)
            os.chmod(dependency, 0o600)
            dependency.write_bytes(dependency.read_bytes() + b"\n")
            with self.assertRaisesRegex(
                    self.module.BehaviorEvalError, "staged semantic adapter dependency"):
                self.module.verify_bound_adapter_command(staged_command, identity)

    def test_strict_json_rejects_duplicate_keys_and_non_finite_numbers(self):
        for raw in ('{"value": 1, "value": 2}', '{"value": NaN}'):
            with self.subTest(raw=raw):
                with self.assertRaises(self.module.BehaviorEvalError):
                    self.module.strict_json_loads(raw, "fixture")


if __name__ == "__main__":
    unittest.main()
