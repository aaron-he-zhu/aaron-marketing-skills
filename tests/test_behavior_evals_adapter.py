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
from pathlib import Path
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
CASE_ID = "routing-outreach-vs-contract-helper-outreach-manager-001"

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
            "parameters_sha256": "2" * 64, "candidate_response_sha256": "3" * 64,
            "judge_response_sha256": "4" * 64, "response_sha256": "5" * 64,
            "started_at": "2026-07-19T10:00:00Z", "ended_at": "2026-07-19T10:00:01Z",
            "latency_ms": 1000
        },
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
                "python3 %s" % script, {CASE_ID}, 60)

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
                "python3 %s" % script, self.v2_selection(), 60,
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
                    "--adapter-command", "python3 %s" % script,
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
                    "python3 %s" % script, selection, 60, batch_size=113,
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
            command = "python3 %s" % script
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
                    "--adapter-command", "python3 scripts/adapters/codex-behavior-adapter.py",
                    "--evidence-run-id", "123e4567-e89b-42d3-a456-426614174002",
                ])
        self.assertEqual(2, ctx.exception.code)

    def test_strict_json_rejects_duplicate_keys_and_non_finite_numbers(self):
        for raw in ('{"value": 1, "value": 2}', '{"value": NaN}'):
            with self.subTest(raw=raw):
                with self.assertRaises(self.module.BehaviorEvalError):
                    self.module.strict_json_loads(raw, "fixture")


if __name__ == "__main__":
    unittest.main()
