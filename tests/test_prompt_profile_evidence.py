import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prompt_profile_evidence.py"
RUNNER = ROOT / "scripts" / "run-prompt-profile-ablation.py"
SPEC = importlib.util.spec_from_file_location("prompt_profile_evidence_test", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
RUNNER_SPEC = importlib.util.spec_from_file_location(
    "prompt_profile_ablation_test", RUNNER
)
RUNNER_MODULE = importlib.util.module_from_spec(RUNNER_SPEC)
RUNNER_SPEC.loader.exec_module(RUNNER_MODULE)
BEHAVIOR = RUNNER_MODULE.behavior
PYTHON_SHA256 = hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()


class PromptProfileEvidenceTests(unittest.TestCase):
    def test_judge_identity_is_required_across_v3_evidence_and_certificate_schemas(self):
        v3 = json.loads(
            (ROOT / "evals/behavior-adapter-v3.schema.json").read_text(
                encoding="utf-8"
            )
        )
        paired = json.loads(
            (ROOT / "references/prompt-profile-paired-evidence.schema.json").read_text(
                encoding="utf-8"
            )
        )
        certificate = json.loads(
            (ROOT / "references/prompt-profile-release-certificate.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue({
            "judge_model_provider", "judge_model_id", "judge_model_revision",
        }.issubset(v3["$defs"]["executionProvenance"]["required"]))
        self.assertTrue({
            "judge_provider", "judge_model_id", "judge_model_revision",
        }.issubset(paired["properties"]["model"]["required"]))
        self.assertIn(
            "judge_model_revision",
            paired["$defs"]["arm"]["properties"]["execution"]["required"],
        )
        self.assertIn(
            "immutable_judge_identity",
            paired["$defs"]["aggregate"]["properties"]["gates"]["required"],
        )
        self.assertTrue({
            "judge_provider", "judge_model_id", "judge_model_revision",
        }.issubset(certificate["properties"]["model"]["required"]))

    def _semantic_run(self, root, *, mutate_request=None, mutate_result=None):
        shutil.copytree(
            ROOT,
            root,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(
                ".git", "memory", "__pycache__", "*.pyc"
            ),
        )
        run_id = str(uuid.uuid4())
        evidence = root / "memory" / "runs" / run_id / "semantic-eval"
        evidence.mkdir(parents=True)
        selection = BEHAVIOR.select_semantic_cases("nightly", set())
        case = selection["cases"][0]
        request = BEHAVIOR.build_v3_requests(
            [case], selection["profile"], {
                case["id"]: selection["selection_reasons"][case["id"]]
            },
            host_profile="claude-code-plugin-host",
            model_id="fixture/model",
            judge_model_id="fixture/judge",
            prompt_profile="explicit",
            toolset_id="read-only-no-tools-v1",
        )[0]
        if mutate_request is not None:
            request.pop("request_sha256")
            mutate_request(request)
            request["request_sha256"] = MODULE.sha256_json(request)
        request_raw = (MODULE.canonical_json(request) + "\n").encode()
        candidate_sha256 = "3" * 64
        judge_attempts = [{
            "attempt": 1,
            "response_sha256": "4" * 64,
            "size_bytes": 1,
            "disposition": "accepted",
            "diagnostic_code": None,
        }]
        response_sha256 = MODULE.sha256_json({
            "candidate_response_sha256": candidate_sha256,
            "judge_attempts": judge_attempts,
        })
        assertions = [
            {
                "id": "expected-%d" % index,
                "kind": "expected",
                "verdict": "met",
                "evidence": "observed",
            }
            for index, unused in enumerate(
                request["judge_contract"]["assertions"], 1
            )
        ] + [
            {
                "id": "forbidden-%d" % index,
                "kind": "forbidden",
                "verdict": "not-observed",
                "evidence": "not observed",
            }
            for index, unused in enumerate(
                request["judge_contract"]["must_not"], 1
            )
        ]
        current_behavior = MODULE._load_behavior_runtime(root)
        python_path = str(Path(current_behavior.sys.executable).resolve())
        command_argv = [
            python_path,
            str(root / current_behavior.OFFICIAL_PROJECT_ADAPTER_REF),
            "--codex-bin", python_path,
            "--codex-sha256", PYTHON_SHA256,
            "--model", "fixture/model",
            "--judge-model", "fixture/judge",
        ]
        command_argv, command_identity = current_behavior.bind_adapter_command(
            command_argv,
            implementation_ref=current_behavior.OFFICIAL_PROJECT_ADAPTER_REF,
        )
        adapter_sha256 = command_identity["implementation"]["sha256"]
        execution = request["execution"]
        result = {
            "kind": "behavior-eval-result",
            "protocol_version": "3.0",
            "case_id": request["case"]["id"],
            "request_sha256": request["request_sha256"],
            "outcome": "passed",
            "routing": {
                "selected_skill": request["judge_contract"]["expected_route"],
                "expected_skill": request["judge_contract"]["expected_route"],
                "correct": True,
                "routing_index_sha256": request["routing_index"]["index_sha256"],
                "routing_response_sha256": "6" * 64,
            },
            "execution_provenance": {
                "execution_mode": "real",
                "adapter_name": "fixture-adapter",
                "adapter_version": "3.0.0",
                "host_name": "fixture-host",
                "host_version": "1.0.0",
                "model_provider": "fixture",
                "model_id": execution["model_id"],
                "judge_model_id": execution["judge_model_id"],
                "model_revision": "fixture-snapshot-1",
                "judge_model_provider": "fixture",
                "judge_model_revision": "fixture-judge-snapshot-1",
                "prompt_template_version": "3.0.0",
                "adapter_implementation_sha256": adapter_sha256,
                "prompt_template_sha256": "1" * 64,
                "parameters_sha256": "2" * 64,
                "candidate_response_sha256": candidate_sha256,
                "judge_response_sha256": "4" * 64,
                "judge_attempts": judge_attempts,
                "response_sha256": response_sha256,
                "started_at": "2026-08-01T00:00:00Z",
                "ended_at": "2026-08-01T00:00:01Z",
                "latency_ms": 1000,
            },
            "provider_metrics": {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
                "latency_ms": None,
                "tool_calls": None,
            },
            "context_binding": {
                "prompt_profile": execution["prompt_profile"],
                "host_profile": execution["host_profile"],
                "toolset_id": execution["toolset_id"],
                "toolset_sha256": execution["toolset_sha256"],
                "candidate_context_sha256": "5" * 64,
                "candidate_sources_sha256": "7" * 64,
                "assembly_sha256": None,
                "assembly_signature": None,
                "context_signature": None,
                "host_catalog_sha256": None,
                "prompt_policy_sha256": None,
                "context_modules_sha256": None,
                "capsule_index_sha256": request["routing_index"][
                    "capsule_index"
                ]["sha256"],
                "model_body_bytes": None,
                "model_reduction_ratio": None,
                "model_resources_sha256": None,
            },
            "stage_latency_ms": {
                "routing_ms": 100,
                "execution_ms": 500,
                "judge_ms": 400,
            },
            "assertions": assertions,
            "failures": [],
        }
        if mutate_result is not None:
            mutate_result(result)
        record = {
            "sequence": 1,
            "previous_record_hash": MODULE.ZERO_HASH,
            "result": result,
        }
        record["record_hash"] = MODULE.sha256_json(record)
        result_raw = (MODULE.canonical_json(record) + "\n").encode()
        manifest = {
            "schema_version": "1.0",
            "kind": "semantic-eval-evidence",
            "protocol_version": "3.0",
            "run_id": run_id,
            "profile": selection["profile"],
            "request_count": 1,
            "request_stream_sha256": hashlib.sha256(request_raw).hexdigest(),
            "selection_provenance": selection["provenance"],
            "selection_sha256": MODULE.sha256_json({
                "profile": selection["profile"],
                "case_ids": [request["case"]["id"]],
                "provenance": selection["provenance"],
            }),
            "adapter_command_sha256": MODULE.sha256_json(command_argv),
            "adapter_command_identity": command_identity,
            "runner": {
                "ref": "scripts/run-behavior-evals.py",
                "sha256": hashlib.sha256(
                    (root / "scripts" / "run-behavior-evals.py").read_bytes()
                ).hexdigest(),
            },
            "protocol_schema": {
                "ref": "evals/behavior-adapter-v3.schema.json",
                "sha256": hashlib.sha256(
                    (root / "evals" / "behavior-adapter-v3.schema.json").read_bytes()
                ).hexdigest(),
            },
            "required_execution_mode": "real",
        }
        completion = {
            "schema_version": "1.0",
            "kind": "semantic-eval-completion",
            "run_id": run_id,
            "request_count": 1,
            "attempt_count": 1,
            "terminal_count": 1,
            "complete": True,
            "status": "passed" if result["outcome"] == "passed" else "failed",
            "outcome_counts": {
                outcome: int(outcome == result["outcome"])
                for outcome in MODULE.OUTCOMES
            },
            "result_stream_sha256": hashlib.sha256(result_raw).hexdigest(),
            "head_record_hash": record["record_hash"],
            "completed_at": "2026-08-01T00:00:01Z",
        }
        (evidence / "manifest.json").write_text(
            json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
        )
        (evidence / "requests.ndjson").write_bytes(request_raw)
        (evidence / "results.ndjson").write_bytes(result_raw)
        (evidence / "completion.json").write_text(
            json.dumps(completion, sort_keys=True) + "\n", encoding="utf-8"
        )
        return run_id, evidence

    def test_current_corpus_has_no_release_eligible_real_cases(self):
        cases = MODULE.current_case_index(ROOT)
        self.assertEqual(734, len(cases))
        self.assertTrue(all(case["case_provenance"] == "simulated" for case in cases.values()))
        self.assertTrue(all(case["evidence_binding"] is None for case in cases.values()))

    def test_pair_case_provenance_is_rechecked_against_canonical_corpus(self):
        current = next(
            case for case in MODULE.current_case_index(ROOT).values()
            if case["source_group"] == "auto-routing"
        )
        pair = {
            key: copy.deepcopy(current[key])
            for key in (
                "case_sha256", "case_provenance", "evidence_binding", "source_group",
                "source_ref", "source_line", "target_skill",
            )
        }
        pair["coverage_stratum"] = MODULE.authoritative_coverage_stratum(
            current, ROOT
        )
        self.assertFalse(MODULE.validate_pair_case_binding(pair, current))
        pair["case_provenance"] = "real"
        pair["evidence_binding"] = {
            "ref": "memory/fake-release-case.json",
            "sha256": "0" * 64,
        }
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "canonical eval corpus"):
            MODULE.validate_pair_case_binding(pair, current)
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "absent from the canonical"):
            MODULE.validate_pair_case_binding(pair, None)

    def test_coverage_strata_derive_from_all_current_source_groups(self):
        cases = MODULE.current_case_index(ROOT)
        disciplines = MODULE.canonical_skill_disciplines(ROOT)
        self.assertEqual(120, len(disciplines))
        for source_group in ("auto-routing", "authored", "derived-auditor"):
            current = next(
                case for case in cases.values()
                if case["source_group"] == source_group
            )
            with self.subTest(source_group=source_group):
                observed = MODULE.authoritative_coverage_stratum(current, ROOT)
                if source_group == "auto-routing":
                    self.assertEqual(
                        "auto:%s" % MODULE.authoritative_case_scenario_family(
                            current, ROOT
                        ),
                        observed,
                    )
                else:
                    self.assertEqual(
                        "discipline:%s" % disciplines[current["target_skill"]],
                        observed,
                    )

    def test_forged_coverage_stratum_is_rejected_for_every_source_group(self):
        cases = MODULE.current_case_index(ROOT)
        for source_group in ("auto-routing", "authored", "derived-auditor"):
            current = next(
                case for case in cases.values()
                if case["source_group"] == source_group
            )
            pair = {
                key: copy.deepcopy(current[key])
                for key in (
                    "case_sha256", "case_provenance", "evidence_binding",
                    "source_group", "source_ref", "source_line", "target_skill",
                )
            }
            pair["coverage_stratum"] = "discipline:forged"
            with self.subTest(source_group=source_group):
                with self.assertRaisesRegex(
                        MODULE.PromptProfileEvidenceError,
                        "canonical eval corpus"):
                    MODULE.validate_pair_case_binding(pair, current)

    def test_arm_run_provenance_is_unique_within_pair_and_across_evidence(self):
        first, second, third = tuple(str(uuid.uuid4()) for _ in range(3))

        def pair(control, candidate):
            return {"arms": {
                "control": {"run_provenance": {"run_id": control}},
                "candidate": {"run_provenance": {"run_id": candidate}},
            }}

        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "control and candidate"):
            MODULE.validate_arm_run_id_uniqueness([pair(first, first)])
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "unique across evidence"):
            MODULE.validate_arm_run_id_uniqueness([
                pair(first, second), pair(third, first),
            ])
        observed = MODULE.validate_arm_run_id_uniqueness([
            pair(first, second), pair(third, str(uuid.uuid4())),
        ])
        self.assertEqual(4, len(observed))
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "document run_id"):
            MODULE.validate_arm_run_id_uniqueness(
                [pair(first, second)], document_run_id=first
            )
        expected = MODULE.sha256_json(sorted((first, second)))
        self.assertEqual(
            expected,
            MODULE.arm_run_set_sha256(
                [pair(first, second)], document_run_id=str(uuid.uuid4())
            ),
        )

    def test_runner_projects_verifier_owned_coverage_not_public_family(self):
        cases = MODULE.current_case_index(ROOT)
        for source_group in ("auto-routing", "authored", "derived-auditor"):
            current = next(
                case for case in cases.values()
                if case["source_group"] == source_group
            )
            projection = RUNNER_MODULE._pair_case_projection(current)
            with self.subTest(source_group=source_group):
                self.assertEqual(
                    MODULE.authoritative_coverage_stratum(current, ROOT),
                    projection["coverage_stratum"],
                )
                self.assertNotIn("scenario_family", projection)

    def test_stored_v3_request_result_completion_hash_chain_is_required(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        run_id, evidence = self._semantic_run(root)
        captured = MODULE.capture_semantic_run(root, run_id)
        self.assertEqual(run_id, captured["provenance"]["run_id"])
        self.assertIs(MODULE._VALIDATED_SEMANTIC_RUN, captured["validation_token"])
        self.assertNotIn("coverage_stratum", captured["request"]["case"])
        self.assertNotIn("scenario_family", captured["request"]["case"])
        self.assertEqual(
            captured["provenance"]["record_hash"],
            captured["provenance"]["head_record_hash"],
        )
        raw = bytearray((evidence / "results.ndjson").read_bytes())
        raw[-2] = ord("x")
        (evidence / "results.ndjson").write_bytes(bytes(raw))
        with self.assertRaises(MODULE.PromptProfileEvidenceError):
            MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_manifest_profile_different_from_arm_selection(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, evidence = self._semantic_run(root)
            path = evidence / "manifest.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["profile"] = "smoke"
            path.write_text(
                json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError,
                    "profile differs from its arm request"):
                MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_selection_digest_or_current_provenance_tamper(self):
        for mutation in ("digest", "self-consistent-provenance"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                run_id, evidence = self._semantic_run(root)
                path = evidence / "manifest.json"
                manifest = json.loads(path.read_text(encoding="utf-8"))
                if mutation == "digest":
                    manifest["selection_sha256"] = "f" * 64
                    expected = "selection digest"
                else:
                    manifest["selection_provenance"]["selected_count"] += 1
                    request = json.loads(
                        (evidence / "requests.ndjson").read_text(encoding="utf-8")
                    )
                    manifest["selection_sha256"] = MODULE.sha256_json({
                        "profile": manifest["profile"],
                        "case_ids": [request["case"]["id"]],
                        "provenance": manifest["selection_provenance"],
                    })
                    expected = "current canonical selection"
                path.write_text(
                    json.dumps(manifest, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                        MODULE.PromptProfileEvidenceError, expected):
                    MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_adapter_command_digest_or_exact_argv_tamper(self):
        for mutation in ("digest", "self-consistent-model-argv"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                run_id, evidence = self._semantic_run(root)
                path = evidence / "manifest.json"
                manifest = json.loads(path.read_text(encoding="utf-8"))
                if mutation == "digest":
                    manifest["adapter_command_sha256"] = "f" * 64
                    expected = "command digest"
                else:
                    argv = manifest["adapter_command_identity"]["logical_argv"]
                    model_index = argv.index("--model") + 1
                    argv[model_index] = "fixture/forged-model"
                    manifest["adapter_command_sha256"] = MODULE.sha256_json(argv)
                    expected = "model identities differ"
                path.write_text(
                    json.dumps(manifest, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                        MODULE.PromptProfileEvidenceError, expected):
                    MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_self_consistent_public_case_forgery(self):
        def forge_case(request):
            request["case"]["scenario"] = "Forged scenario with a valid self-hash."
            request["case"]["input_summary"] = "Forged input summary."

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(root, mutate_request=forge_case)
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "canonical v3 request"):
                MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_self_consistent_judge_contract_forgery(self):
        def forge_judge(request):
            request["judge_contract"]["assertions"][0] = "Forged assertion."
            request["judge_contract"]["must_not"][0] = "Forged prohibition."

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(root, mutate_request=forge_judge)
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "canonical v3 request"):
                MODULE.capture_semantic_run(root, run_id)

    def test_capture_rejects_self_consistent_routing_index_forgery(self):
        def forge_routing(request):
            routing = request["routing_index"]
            routing["entries"][0]["description"] = "Forged routing description."
            payload = dict(routing)
            payload.pop("index_sha256")
            routing["index_sha256"] = MODULE.sha256_json(payload)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(root, mutate_request=forge_routing)
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "canonical v3 request"):
                MODULE.capture_semantic_run(root, run_id)

    def test_full_v3_validator_rejects_incomplete_or_violated_assertions(self):
        mutations = {
            "omitted": lambda result: result["assertions"].pop(),
            "violated-pass": lambda result: result["assertions"][0].update({
                "verdict": "violated"
            }),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                run_id, unused = self._semantic_run(
                    root, mutate_result=mutation
                )
                with self.assertRaisesRegex(
                        MODULE.PromptProfileEvidenceError, "current v3 validator"):
                    MODULE.capture_semantic_run(root, run_id)

    def test_full_v3_validator_rejects_wrong_failure_taxonomy(self):
        def wrong_taxonomy(result):
            result["outcome"] = "behavior-failed"
            result["assertions"][0]["verdict"] = "violated"
            result["failures"] = [{
                "code": "PROMPT_REQUIRED_BEHAVIOR_MISSING",
                "class": "host",
                "retryable": False,
                "summary": "forged taxonomy",
            }]

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(
                root, mutate_result=wrong_taxonomy
            )
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "current v3 validator"):
                MODULE.capture_semantic_run(root, run_id)

    def test_full_v3_validator_rejects_forged_real_adapter_provenance(self):
        def forge_provenance(result):
            result["execution_provenance"][
                "adapter_implementation_sha256"
            ] = "b" * 64

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(
                root, mutate_result=forge_provenance
            )
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "current v3 validator"):
                MODULE.capture_semantic_run(root, run_id)

    def test_full_v3_validator_rejects_same_provider_revision_aliases(self):
        def collapse_judge_identity(result):
            provenance = result["execution_provenance"]
            provenance["judge_model_provider"] = provenance["model_provider"]
            provenance["judge_model_revision"] = provenance["model_revision"]

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(
                root, mutate_result=collapse_judge_identity
            )
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError, "current v3 validator"):
                MODULE.capture_semantic_run(root, run_id)

    def test_v3_request_rejects_same_model_judge(self):
        case = next(iter(MODULE.current_case_index(ROOT).values()))
        with self.assertRaisesRegex(
                BEHAVIOR.BehaviorEvalError, "independent judge_model_id"):
            BEHAVIOR.build_v3_requests(
                [case], "nightly", {case["id"]: ["filter:id"]},
                host_profile="claude-code-plugin-host",
                model_id="fixture/same",
                judge_model_id="fixture/same",
            )

    def test_release_identity_rejects_moving_judge_alias_or_revision(self):
        base = {
            "host_name": "fixture-host",
            "host_version": "1.0.0",
            "model_provider": "fixture",
            "model_id": "fixture/model",
            "model_revision": "sut-snapshot-1",
            "judge_model_provider": "fixture",
            "judge_model_id": "fixture/judge",
            "judge_model_revision": "judge-snapshot-1",
        }

        for field, moving_value in (
                ("judge_model_id", "fixture/judge-moving-alias"),
                ("judge_model_revision", "judge-snapshot-2")):
            rows = [
                {"execution_provenance": copy.deepcopy(base)},
                {"execution_provenance": copy.deepcopy(base)},
            ]
            rows[1]["execution_provenance"][field] = moving_value
            with self.subTest(field=field), self.assertRaisesRegex(
                    RUNNER_MODULE.AblationError, "moving model aliases or revisions"):
                RUNNER_MODULE._release_model_identity(
                    rows, "fixture/model", "fixture/judge"
                )

        null_revision = {"execution_provenance": copy.deepcopy(base)}
        null_revision["execution_provenance"]["judge_model_revision"] = None
        with self.assertRaisesRegex(
                RUNNER_MODULE.AblationError, "immutable SUT and judge revisions"):
            RUNNER_MODULE._release_model_identity(
                [null_revision], "fixture/model", "fixture/judge"
            )

        same_revision = {"execution_provenance": copy.deepcopy(base)}
        same_revision["execution_provenance"]["judge_model_revision"] = (
            base["model_revision"]
        )
        with self.assertRaisesRegex(
                RUNNER_MODULE.AblationError, "share one immutable provider revision"):
            RUNNER_MODULE._release_model_identity(
                [same_revision], "fixture/model", "fixture/judge"
            )

    def test_semantic_completion_cannot_precede_result_end(self):
        def late_result(result):
            result["execution_provenance"]["ended_at"] = (
                "2026-08-01T00:00:02Z"
            )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id, unused = self._semantic_run(
                root, mutate_result=late_result
            )
            with self.assertRaisesRegex(
                    MODULE.PromptProfileEvidenceError,
                    "completion precedes"):
                MODULE.capture_semantic_run(root, run_id)

    def test_post_route_execution_rejects_routing_shards_in_either_arm(self):
        arms = {
            role: {"context": {"model_resources": [{
                "role": "skill-definition",
                "ref": "narrative/trace/example/SKILL.md",
            }]}}
            for role in ("control", "candidate")
        }
        MODULE.validate_post_route_model_resources(arms)
        for role in ("control", "candidate"):
            forged = copy.deepcopy(arms)
            forged[role]["context"]["model_resources"].append({
                "role": "routing-scenario",
                "ref": "references/auto-routing/narrative.md",
            })
            with self.subTest(role=role):
                with self.assertRaisesRegex(
                        MODULE.PromptProfileEvidenceError, "routing shard"):
                    MODULE.validate_post_route_model_resources(forged)

    def test_model_resource_closure_rejects_omitted_required_runtime_read(self):
        contract = json.loads(
            (ROOT / "references/skill-contracts/memory-management.json").read_text(
                encoding="utf-8"
            )
        )

        def resource(ref, role):
            raw = (ROOT / ref).read_bytes()
            return {
                "ref": ref,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "role": role,
            }

        resources = sorted([
            resource(contract["identity"]["path"], "skill-definition"),
            resource("references/skill-contract.md", "shared-contract"),
            resource("references/runtime-invocation.md", "skill-reference"),
        ], key=lambda item: (item["ref"], item["role"]))

        def context(rows):
            return {
                "model_resources": rows,
                "model_resources_sha256": MODULE.sha256_json(rows),
                "model_body_bytes": sum(item["bytes"] for item in rows),
            }

        MODULE._validate_model_resources(
            context(resources), "explicit", "memory-management",
            "claude-code-plugin-host", ROOT,
        )
        omitted = [
            item for item in resources
            if item["ref"] != "references/runtime-invocation.md"
        ]
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "exactly match current required reads"):
            MODULE._validate_model_resources(
                context(omitted), "explicit", "memory-management",
                "claude-code-plugin-host", ROOT,
            )

    def test_timeline_freshness_uses_actual_arm_end_not_fresh_wrapper(self):
        rows = {
            role: [{"execution": {
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": "2026-01-01T00:00:01Z",
            }}]
            for role in ("control", "candidate")
        }
        document = {
            "created_at": "2025-12-31T23:59:59Z",
            "completed_at": "2026-08-01T00:00:00Z",
            "evaluated_at": "2026-08-01T00:00:00Z",
            "expires_at": "2026-08-02T00:00:00Z",
        }
        instant = MODULE.parse_datetime(
            "2026-08-01T00:00:00Z", "fixture instant"
        )
        self.assertFalse(MODULE.validate_evidence_timeline(
            document, rows, {"maximum_age_days": 90}, instant
        ))
        document["created_at"] = "2026-08-01T00:00:00Z"
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "not monotonic"):
            MODULE.validate_evidence_timeline(
                document, rows, {"maximum_age_days": 90}, instant
            )

    def test_promotion_rejects_replayed_or_duplicate_arm_run_sets(self):
        current = "1" * 64

        def certificate(digest):
            return {
                "kind": "prompt-profile-release-certificate",
                "paired_evidence": {"arm_run_set_sha256": digest},
            }

        MODULE.validate_promotion_replay(current, [certificate("2" * 64)])
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "replays"):
            MODULE.validate_promotion_replay(current, [certificate(current)])
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "duplicate arm-run set"):
            MODULE.validate_promotion_replay(
                current, [certificate("2" * 64), certificate("2" * 64)]
            )

    def test_primary_reduction_uses_complete_paired_model_body_bytes(self):
        self.assertEqual(
            0.25, MODULE.paired_model_body_reduction_ratio(1000, 750)
        )
        self.assertEqual(
            0, MODULE.paired_model_body_reduction_ratio(1000, 1200)
        )
        with self.assertRaises(MODULE.PromptProfileEvidenceError):
            MODULE.paired_model_body_reduction_ratio(1000, -1)

    def test_absolute_floors_reject_equally_failing_arms(self):
        policy = json.loads(
            (ROOT / "references/prompt-profiles.json").read_text(encoding="utf-8")
        )["certification_policy"]
        all_fail = {"routing_accuracy": 0.0, "quality_pass_rate": 0.0}
        gates = MODULE.absolute_performance_gates(all_fail, all_fail, policy)
        self.assertTrue(gates)
        self.assertTrue(all(value is False for value in gates.values()))
        all_pass = {"routing_accuracy": 1.0, "quality_pass_rate": 1.0}
        self.assertTrue(all(
            MODULE.absolute_performance_gates(
                all_pass, all_pass, policy
            ).values()
        ))

    def test_complete_provider_metrics_never_imply_token_savings(self):
        pairs = [{"arms": {
            "control": {"execution": {"provider": {
                "input_tokens": 100, "output_tokens": 10, "total_tokens": 110,
                "latency_ms": 100, "tool_calls": 0,
            }}},
            "candidate": {"execution": {"provider": {
                "input_tokens": 200, "output_tokens": 10, "total_tokens": 210,
                "latency_ms": 100, "tool_calls": 0,
            }}},
        }}]
        self.assertFalse(MODULE.token_savings_claims_permitted(pairs))

    def test_arm_projection_refuses_missing_private_run_provenance(self):
        digest = "1" * 64
        binding = {
            "assembly_sha256": "2" * 64,
            "assembly_signature": "3" * 64,
            "context_signature": "4" * 64,
            "host_catalog_sha256": "5" * 64,
            "prompt_policy_sha256": "6" * 64,
            "context_modules_sha256": "7" * 64,
            "capsule_index_sha256": "8" * 64,
            "model_body_bytes": 10,
            "model_reduction_ratio": 0.5,
            "model_resources": [{
                "ref": "skills/example/SKILL.md", "sha256": "9" * 64,
                "bytes": 10, "role": "skill-definition",
            }],
            "model_resources_sha256": digest,
        }
        request = {"request_sha256": "a" * 64, "execution": {"assembly_binding": binding}}
        result = {
            "request_sha256": "a" * 64,
            "outcome": "behavior-failed",
            "routing": {"correct": True},
            "failures": [{"code": "PROMPT_FORBIDDEN_BEHAVIOR"}],
            "assertions": [{
                "id": "forbidden-1", "kind": "forbidden", "verdict": "violated"
            }],
            "context_binding": {
                "prompt_profile": "balanced",
                "candidate_context_sha256": "b" * 64,
                "candidate_sources_sha256": digest,
                **{key: value for key, value in binding.items() if key != "model_resources"},
            },
            "execution_provenance": {
                "execution_mode": "real", "adapter_implementation_sha256": "c" * 64,
                "host_version": "host-1", "model_revision": "snapshot-1",
                "started_at": "2026-08-01T00:00:00Z",
                "ended_at": "2026-08-01T00:00:01Z", "latency_ms": 1000,
            },
            "provider_metrics": {
                "input_tokens": None, "output_tokens": None, "total_tokens": None,
                "latency_ms": None, "tool_calls": None,
            },
        }
        with self.assertRaisesRegex(
                MODULE.PromptProfileEvidenceError, "current full v3 validator"):
            MODULE.arm_from_result(result, request, None)

    def test_release_runner_hard_fails_before_calls_on_simulated_corpus(self):
        with tempfile.TemporaryDirectory() as temporary:
            completed = subprocess.run([
                sys.executable, str(RUNNER),
                "--adapter-command", "/bin/false",
                "--adapter-implementation-ref", "scripts/adapters/codex-behavior-adapter.py",
                "--host-profile", "claude-code-plugin-host",
                "--model-id", "provider/model",
                "--judge-model-id", "provider/judge",
                "--candidate-profile", "balanced",
                "--profile", "smoke",
                "--seed", "test-seed",
                "--context-as-of", "2026-08-01T00:00:00Z",
                "--output", str(Path(temporary) / "evidence.json"),
            ], cwd=ROOT, capture_output=True, text=True, timeout=60)
        self.assertNotEqual(0, completed.returncode)
        self.assertIn("selected case(s) are simulated", completed.stderr)


if __name__ == "__main__":
    unittest.main()
