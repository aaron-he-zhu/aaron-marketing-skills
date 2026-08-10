from __future__ import annotations

import contextlib
import copy
import datetime as dt
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shlex
import tempfile
import textwrap
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load("semantic_evidence_test_runner", ROOT / "scripts" / "run-behavior-evals.py")
verifier = load("semantic_evidence_verifier", ROOT / "scripts" / "verify-semantic-evidence.py")


PASS_ADAPTER = """\
import datetime as dt, hashlib, json, sys
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
    response_sha256 = hashlib.sha256(json.dumps({
        "candidate_response_sha256": candidate_sha256,
        "judge_attempts": judge_attempts,
    }, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
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
            "judge_response_sha256": judge_attempts[-1]["response_sha256"],
            "judge_attempts": judge_attempts, "response_sha256": response_sha256,
            "started_at": now, "ended_at": now, "latency_ms": 1
        },
        "assertions": assertions, "failures": []
    }))
"""


class SemanticEvidenceVerifierTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.evidence_root = Path(self.temporary.name) / "project"
        self.evidence_root.mkdir()
        self.adapter = Path(self.temporary.name) / "fixture-adapter.py"
        self.adapter.write_text(textwrap.dedent(PASS_ADAPTER), encoding="utf-8")
        self.run_id = "123e4567-e89b-42d3-a456-426614174099"
        self.selection = runner.select_semantic_cases("smoke", set())
        with contextlib.redirect_stdout(io.StringIO()):
            failures = runner.run_adapter_v2(
                shlex.join([runner.sys.executable, str(self.adapter)]),
                self.selection,
                60,
                batch_size=7,
                evidence_run_id=self.run_id,
                evidence_root=self.evidence_root,
            )
        self.assertEqual([], failures)
        self.policy = {
            "schema_version": "1.0",
            "profile": "smoke",
            "minimum_cases": 24,
            "maximum_age_days": 30,
            "required_execution_mode": "real",
            "required_status": "passed",
            "require_current_case_selection": True,
            "require_current_runner": True,
            "require_current_protocol_schema": True,
            "require_project_adapter": False,
            "require_isolated_project_adapter": True,
            "require_staged_project_adapter": True,
            "required_project_adapter_ref": runner.OFFICIAL_PROJECT_ADAPTER_REF,
            "required_project_adapter_dependencies": list(
                runner.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES
            ),
            "require_single_execution_identity": True,
            "require_distinct_judge_model": True,
        }

    def tearDown(self):
        self.temporary.cleanup()

    @property
    def directory(self):
        return self.evidence_root / "memory" / "runs" / self.run_id / "semantic-eval"

    def test_committed_policy_tracks_official_adapter_dependency_closure(self):
        policy = verifier.load_policy(runner=runner)
        self.assertEqual(
            list(runner.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES),
            policy["required_project_adapter_dependencies"],
        )

    def test_complete_current_real_evidence_passes(self):
        result = verifier.verify_evidence(
            self.evidence_root, self.run_id, policy=self.policy, runner=runner,
        )
        self.assertTrue(result["valid"])
        self.assertEqual(24, result["case_count"])
        self.assertTrue(result["distinct_judge_model"])
        self.assertEqual("real", result["execution_mode"])
        self.assertEqual(24, result["total_judge_attempts"])
        self.assertEqual(0, result["retried_cases"])
        self.assertEqual(0, result["judge_protocol_retries"])
        self.assertEqual(
            hashlib.sha256(self.adapter.read_bytes()).hexdigest(),
            result["adapter_implementation_sha256"],
        )

    def test_request_tamper_fails_closed(self):
        requests = self.directory / "requests.ndjson"
        requests.chmod(0o600)
        requests.write_bytes(requests.read_bytes() + b"\n")
        with self.assertRaisesRegex(verifier.EvidenceError, "stored semantic requests"):
            verifier.verify_evidence(
                self.evidence_root, self.run_id, policy=self.policy, runner=runner,
            )

    def test_manifest_command_digest_tamper_fails_closed(self):
        path = (
            self.evidence_root / "memory" / "runs" / self.run_id
            / "semantic-eval" / "manifest.json"
        )
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["adapter_command_sha256"] = "f" * 64
        path.write_text(
            json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(verifier.EvidenceError, "command digest"):
            verifier.verify_evidence(
                self.evidence_root, self.run_id, policy=self.policy, runner=runner,
            )

    def test_manifest_selection_provenance_tamper_fails_closed(self):
        path = (
            self.evidence_root / "memory" / "runs" / self.run_id
            / "semantic-eval" / "manifest.json"
        )
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["selection_provenance"]["selected_count"] += 1
        manifest["selection_sha256"] = runner.sha256_json({
            "profile": manifest["profile"],
            "case_ids": self.selection["case_ids"],
            "provenance": manifest["selection_provenance"],
        })
        path.write_text(
            json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(verifier.EvidenceError, "current case selection"):
            verifier.verify_evidence(
                self.evidence_root, self.run_id, policy=self.policy, runner=runner,
            )

    def test_stale_result_fails_closed(self):
        with self.assertRaisesRegex(verifier.EvidenceError, "stale"):
            verifier.verify_evidence(
                self.evidence_root,
                self.run_id,
                policy=self.policy,
                now=dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=31),
                runner=runner,
            )

    def test_policy_can_require_project_adapter_and_distinct_judge(self):
        project_policy = copy.deepcopy(self.policy)
        project_policy["require_project_adapter"] = True
        with self.assertRaisesRegex(verifier.EvidenceError, "project adapter"):
            verifier.verify_evidence(
                self.evidence_root, self.run_id, policy=project_policy, runner=runner,
            )

        same_judge_adapter = Path(self.temporary.name) / "same-judge-adapter.py"
        same_judge_adapter.write_text(
            textwrap.dedent(PASS_ADAPTER).replace(
                '"judge_model_id": "fixture-judge"',
                '"judge_model_id": "fixture-model"',
            ),
            encoding="utf-8",
        )
        same_judge_run = "123e4567-e89b-42d3-a456-426614174100"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(
                [],
                runner.run_adapter_v2(
                    shlex.join([runner.sys.executable, str(same_judge_adapter)]),
                    self.selection,
                    60,
                    batch_size=8,
                    evidence_run_id=same_judge_run,
                    evidence_root=self.evidence_root,
                ),
            )
        with self.assertRaisesRegex(verifier.EvidenceError, "distinct judge"):
            verifier.verify_evidence(
                self.evidence_root, same_judge_run, policy=self.policy, runner=runner,
            )

    def test_project_adapter_must_be_executed_and_runtime_schemas_stay_current(self):
        project_policy = copy.deepcopy(self.policy)
        project_policy["require_project_adapter"] = True
        _command, identity = runner.bind_adapter_command(
            [runner.sys.executable, runner.OFFICIAL_PROJECT_ADAPTER_REF],
            implementation_ref=runner.OFFICIAL_PROJECT_ADAPTER_REF,
        )
        verifier._project_adapter_current(runner, identity, project_policy)

        unisolated = copy.deepcopy(identity)
        unisolated["execution_binding"] = {
            "kind": "current-python-script",
            "interpreter_path": str(Path(runner.sys.executable).resolve()),
            "script_argv_index": 1,
        }
        with self.assertRaisesRegex(verifier.EvidenceError, "isolated current Python"):
            verifier._project_adapter_current(runner, unisolated, project_policy)

        staged_drift = copy.deepcopy(identity)
        staged_drift["staged_runtime"]["runtime_dependencies"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(verifier.EvidenceError, "staged runtime"):
            verifier._project_adapter_current(runner, staged_drift, project_policy)

        original = runner.project_bytes
        dependency = runner.OFFICIAL_PROJECT_ADAPTER_DEPENDENCIES[0]

        def drift(reference):
            if reference == dependency:
                return original(reference) + b"\n"
            return original(reference)

        with mock.patch.object(runner, "project_bytes", side_effect=drift):
            with self.assertRaisesRegex(verifier.EvidenceError, "dependency has drifted"):
                verifier._project_adapter_current(runner, identity, project_policy)


if __name__ == "__main__":
    unittest.main()
