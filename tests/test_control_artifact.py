import copy
import hashlib
import importlib.util
import json
import pathlib
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "references" / "control-artifact.schema.json").read_text(encoding="utf-8")
)
SPEC = importlib.util.spec_from_file_location(
    "control_artifact_validator", ROOT / "scripts" / "validate-control-artifact.py"
)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def binding(ref="opaque:asset-1", digest=None, version="v1"):
    return {
        "ref": ref,
        "sha256": digest or ("a" * 64),
        "version": version,
    }


def artifact(kind, artifact_id, created_at, payload):
    return {
        "$schema": "references/control-artifact.schema.json",
        "schema_version": "1.0",
        "kind": kind,
        "artifact_id": artifact_id,
        "created_at": created_at,
        "authoritative": False,
        "authority": "non-authoritative-operational-evidence",
        "registry_effect": False,
        "external_mutation_authorized": False,
        "payload": payload,
    }


def evidence_artifact():
    return artifact(
        "evidence-observation",
        "evidence-1",
        "2026-08-01T12:00:00Z",
        {
            "target": binding(),
            "observation_window": {
                "start_at": "2026-07-01T00:00:00Z",
                "end_at": "2026-07-31T23:59:59Z",
            },
            "fields": [
                {
                    "field_id": "conversion_rate",
                    "state": "observed",
                    "sources": [
                        {
                            "evidence_type": "measured",
                            "ref": "opaque:analytics-export-1",
                            "observed_at": "2026-08-01T10:00:00Z",
                            "window": {
                                "start_at": "2026-07-01T00:00:00Z",
                                "end_at": "2026-07-31T23:59:59Z",
                            },
                        }
                    ],
                    "value_ref": "opaque:metric-value-1",
                    "freshness": "current",
                    "missing_reason": None,
                    "conflict_group": None,
                }
            ],
            "readiness": "ready",
            "unresolved_conflicts": [],
        },
    )


def measurement_artifact():
    target = binding("opaque:campaign-head-1", "b" * 64, "campaign-v3")
    return artifact(
        "measurement-contract",
        "measurement-1",
        "2026-08-01T09:00:00Z",
        {
            "target": target,
            "contract_version": "contract-v1",
            "population_ref": "opaque:population-snapshot-1",
            "scope_ref": "opaque:campaign-scope-1",
            "analysis_unit": "campaign",
            "counterfactual_type": "holdout",
            "control": binding("opaque:control-1", "c" * 64, "campaign-v2"),
            "candidate": target,
            "primary_metric": {
                "metric_id": "conversion_rate",
                "unit": "ratio",
                "direction": "increase",
                "truth_source_ref": "opaque:warehouse-view-1",
                "attribution_rule_ref": "opaque:attribution-rule-1",
                "conversion_lag_ref": "opaque:lag-7d",
            },
            "guardrail_metric_ids": ["unsubscribe_rate"],
            "start_at": "2026-08-02T00:00:00Z",
            "stop_at": "2026-08-09T00:00:00Z",
            "read_at": "2026-08-16T00:00:00Z",
            "decision_rule_ref": "opaque:decision-rule-1",
            "decision_owner_ref": "opaque:decision-owner-1",
            "locked_at": "2026-08-01T08:00:00Z",
            "exploratory": False,
        },
    )


def intent_artifact():
    return artifact(
        "action-intent",
        "intent-1",
        "2026-08-02T08:00:00Z",
        {
            "operation": "send",
            "target": binding("opaque:send-target-1", "d" * 64, "target-v1"),
            "content": binding("opaque:message-bytes-1", "e" * 64, "message-v4"),
            "audience_ref": "opaque:segment-snapshot-1",
            "channel_ref": "opaque:channel-email-1",
            "constraint_refs": ["opaque:schedule-1"],
            "safety_checks": [binding("opaque:suppression-check-1", "f" * 64, "check-v1")],
            "permission_ref": "opaque:user-request-1",
            "permission_observed_at": "2026-08-02T07:59:00Z",
            "permission_effect": "provenance-only",
            "requested_at": "2026-08-02T08:00:00Z",
            "expires_at": "2026-08-02T09:00:00Z",
            "single_use": True,
        },
    )


def receipt_artifact(intent_ref, intent_digest):
    intent = intent_artifact()
    return artifact(
        "action-receipt",
        "receipt-1",
        "2026-08-02T08:06:00Z",
        {
            "intent": binding(intent_ref, intent_digest, "1.0"),
            "intent_id": "intent-1",
            "operation": "send",
            "actual_target": intent["payload"]["target"],
            "actual_content": intent["payload"]["content"],
            "actual_audience_ref": intent["payload"]["audience_ref"],
            "actual_channel_ref": intent["payload"]["channel_ref"],
            "applied_constraint_refs": intent["payload"]["constraint_refs"],
            "status": "succeeded",
            "attempted_at": "2026-08-02T08:05:00Z",
            "completed_at": "2026-08-02T08:06:00Z",
            "provider_operation_ref": "opaque:provider-operation-1",
            "evidence": [binding("opaque:provider-receipt-1", "1" * 64, "receipt-v1")],
            "failure_code": None,
            "permission_effect": "provenance-only",
        },
    )


def retro_artifact(measurement_ref, measurement_digest):
    measurement = measurement_artifact()
    return artifact(
        "cycle-retro",
        "retro-1",
        "2026-08-16T12:00:00Z",
        {
            "measurement_contract": binding(measurement_ref, measurement_digest, "1.0"),
            "measurement_contract_id": "measurement-1",
            "current_head": measurement["payload"]["target"],
            "head_state": {
                "is_current": True,
                "fork_count": 0,
                "selected_ancestry_ref": "opaque:selected-ancestry-1",
            },
            "evidence": [binding("opaque:readback-evidence-1", "2" * 64, "readback-v1")],
            "decision_code": "promote",
            "decision_taxonomy_ref": "opaque:paid-cycle-decisions-v1",
            "decision_owner_ref": "opaque:decision-owner-1",
            "decided_at": "2026-08-16T12:00:00Z",
            "limitations": [],
            "hypothesis_ref": "opaque:next-hypothesis-1",
            "hypothesis_evidence_weight": 0,
            "next_read_at": None,
        },
    )


class ControlArtifactTests(unittest.TestCase):
    def write(self, root, relative, record, canonical=True):
        path = pathlib.Path(root) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if canonical:
            path.write_bytes(validator.canonical_bytes(record))
        else:
            path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def validate_record(self, record, relative="memory/control/artifact.json"):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, relative, record)
            return validator.validate(str(path), directory)

    def test_schema_is_closed_discriminated_union_without_authorization_kind(self):
        self.assertFalse(SCHEMA["additionalProperties"])
        self.assertEqual(
            set(SCHEMA["properties"]["kind"]["enum"]), validator.KINDS,
        )
        self.assertEqual(len(SCHEMA["oneOf"]), 5)
        self.assertIn("artifact_binding", SCHEMA["$defs"])
        self.assertIn("opaque_ref", SCHEMA["$defs"])
        self.assertIn("project_ref", SCHEMA["$defs"])
        self.assertEqual(
            [item["$ref"] for item in SCHEMA["$defs"]["reference"]["oneOf"]],
            ["#/$defs/opaque_ref", "#/$defs/artifact_binding"],
        )
        self.assertFalse(SCHEMA["$defs"]["artifact_binding"]["additionalProperties"])
        serialized = json.dumps(SCHEMA, sort_keys=True)
        self.assertNotIn('"action-authorization"', serialized)
        self.assertIn('"permission_effect": {"const": "provenance-only"}', serialized)
        self.assertNotIn('"decision": {"enum"', serialized)
        self.assertIn('"decision_taxonomy_ref"', serialized)

    def test_anchored_reads_reject_linked_symlinks_and_inode_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory).resolve()
            real_dir = root / "real"
            real_dir.mkdir()
            source = real_dir / "source.bin"
            source.write_bytes(b"stable evidence\n")
            alias = root / "alias"
            alias.symlink_to(real_dir, target_is_directory=True)
            with self.assertRaisesRegex(
                    validator.ControlArtifactError, "symlink"):
                validator._read_regular(
                    validator._project_reference_path(
                        root, "alias/source.bin", "linked evidence",
                    ),
                    1024, "linked evidence",
                )

            target = root / "target.bin"
            target.write_bytes(b"first inode\n")
            replacement = root / "replacement.bin"
            replacement.write_bytes(b"second-inode\n")
            original_open = validator.os.open
            replaced = False

            def replace_before_final_open(path, flags, *args, **kwargs):
                nonlocal replaced
                if (
                        not replaced and path == target.name
                        and kwargs.get("dir_fd") is not None
                        and not flags & getattr(validator.os, "O_DIRECTORY", 0)):
                    replaced = True
                    target.rename(root / "old-target.bin")
                    replacement.rename(target)
                return original_open(path, flags, *args, **kwargs)

            with (
                mock.patch.object(
                    validator.os, "open", side_effect=replace_before_final_open,
                ),
                self.assertRaisesRegex(
                    validator.ControlArtifactError, "changed during anchored open",
                ),
            ):
                validator._read_regular(target, 1024, "linked evidence")

    def test_all_five_kinds_validate(self):
        for record in (evidence_artifact(), measurement_artifact(), intent_artifact()):
            self.assertEqual([], self.validate_record(record)[1])
        with tempfile.TemporaryDirectory() as directory:
            intent_path = self.write(directory, "memory/control/intent.json", intent_artifact())
            intent_digest = hashlib.sha256(intent_path.read_bytes()).hexdigest()
            receipt = receipt_artifact("memory/control/intent.json", intent_digest)
            self.assertEqual([], validator.validate(
                str(self.write(directory, "memory/control/receipt.json", receipt)), directory,
            )[1])
            measurement_path = self.write(
                directory, "memory/control/measurement.json", measurement_artifact(),
            )
            measurement_digest = hashlib.sha256(measurement_path.read_bytes()).hexdigest()
            retro = retro_artifact("memory/control/measurement.json", measurement_digest)
            self.assertEqual([], validator.validate(
                str(self.write(directory, "memory/control/retro.json", retro)), directory,
            )[1])

    def test_canonical_json_duplicate_keys_and_unknown_fields_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            noncanonical = self.write(
                directory, "memory/control/noncanonical.json", evidence_artifact(), canonical=False,
            )
            self.assertTrue(any(
                "not canonical JSON" in error
                for error in validator.validate(str(noncanonical), directory)[1]
            ))
            duplicate = pathlib.Path(directory) / "memory/control/duplicate.json"
            duplicate.write_text('{"a":1,"a":2}\n', encoding="utf-8")
            self.assertTrue(any(
                "duplicate key" in error
                for error in validator.validate(str(duplicate), directory)[1]
            ))
        unknown = evidence_artifact()
        unknown["permission_granted"] = True
        errors = self.validate_record(unknown)[1]
        self.assertTrue(any("unknown fields" in error for error in errors))

    def test_action_intent_permission_ref_is_only_provenance(self):
        record = intent_artifact()
        record["external_mutation_authorized"] = True
        record["payload"]["permission_effect"] = "grants-authority"
        errors = self.validate_record(record)[1]
        self.assertTrue(any("cannot authorize" in error for error in errors))
        self.assertTrue(any("provenance-only" in error for error in errors))

        forbidden = intent_artifact()
        forbidden["kind"] = "action-authorization"
        errors = self.validate_record(forbidden)[1]
        self.assertTrue(any("no authorization/control kind" in error for error in errors))

    def test_pii_urls_and_filesystem_locators_are_rejected(self):
        raw_email = intent_artifact()
        raw_email["payload"]["audience_ref"] = "person@example.com"
        self.assertTrue(any("email" in error for error in self.validate_record(raw_email)[1]))

        raw_phone = intent_artifact()
        raw_phone["payload"]["audience_ref"] = "13812345678"
        self.assertTrue(any("phone" in error for error in self.validate_record(raw_phone)[1]))

        locator = intent_artifact()
        locator["payload"]["channel_ref"] = "https://provider.example/channel"
        errors = self.validate_record(locator)[1]
        self.assertTrue(any("locator" in error or "URL" in error for error in errors))

        absolute = intent_artifact()
        absolute["payload"]["target"]["ref"] = "/tmp/target.json"
        errors = self.validate_record(absolute)[1]
        self.assertTrue(any("locator" in error for error in errors))

    def test_local_refs_require_bindings_and_key_refs_cannot_drift(self):
        source_path = "memory/evidence/source.json"
        bare_source = evidence_artifact()
        bare_source["payload"]["fields"][0]["sources"][0]["ref"] = source_path
        errors = self.validate_record(bare_source)[1]
        self.assertTrue(any(
            "artifact-binding" in error and "sources[0].ref" in error
            for error in errors
        ))

        bare_rule = measurement_artifact()
        bare_rule["payload"]["decision_rule_ref"] = "memory/rules/decision.json"
        errors = self.validate_record(bare_rule)[1]
        self.assertTrue(any(
            "artifact-binding" in error and "decision_rule_ref" in error
            for error in errors
        ))

        with tempfile.TemporaryDirectory() as directory:
            source = {
                "domain": "example.com",
                "query": "running shoe comparison",
                "url": "https://example.com/search?q=running+shoes",
                "version": "source-v1",
            }
            source_file = self.write(directory, source_path, source)
            digest = hashlib.sha256(source_file.read_bytes()).hexdigest()
            record = evidence_artifact()
            record["payload"]["fields"][0]["sources"][0]["ref"] = binding(
                source_path, digest, "source-v1",
            )
            artifact_path = self.write(directory, "memory/control/evidence.json", record)
            self.assertEqual([], validator.validate(str(artifact_path), directory)[1])

            wrong_version = copy.deepcopy(record)
            wrong_version["payload"]["fields"][0]["sources"][0]["ref"]["version"] = "source-v2"
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-version.json", wrong_version)),
                directory,
            )[1]
            self.assertTrue(any("embedded version" in error for error in errors))

            wrong_hash = copy.deepcopy(record)
            wrong_hash["payload"]["fields"][0]["sources"][0]["ref"]["sha256"] = "0" * 64
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-hash.json", wrong_hash)),
                directory,
            )[1]
            self.assertTrue(any("digest" in error for error in errors))

    def test_local_binding_content_is_privacy_checked_without_misclassifying_web_data(self):
        with tempfile.TemporaryDirectory() as directory:
            clean_ref = "memory/evidence/seo-snapshot.json"
            clean = {
                "domain": "example.com",
                "query": "site:example.com/@creator best running shoes",
                "url": "https://example.com/@creator/shoes?sort=rank",
                "version": "snapshot-v1",
            }
            clean_file = self.write(directory, clean_ref, clean)
            record = evidence_artifact()
            record["payload"]["target"] = binding(
                clean_ref,
                hashlib.sha256(clean_file.read_bytes()).hexdigest(),
                "snapshot-v1",
            )
            artifact_path = self.write(directory, "memory/control/clean.json", record)
            self.assertEqual([], validator.validate(str(artifact_path), directory)[1])

            sensitive_ref = "memory/evidence/sensitive.json"
            sensitive = {
                "contact": "person@example.com",
                "version": "snapshot-v1",
            }
            sensitive_file = self.write(directory, sensitive_ref, sensitive)
            record["payload"]["target"] = binding(
                sensitive_ref,
                hashlib.sha256(sensitive_file.read_bytes()).hexdigest(),
                "snapshot-v1",
            )
            errors = validator.validate(
                str(self.write(directory, "memory/control/sensitive.json", record)), directory,
            )[1]
            self.assertTrue(any("email address" in error for error in errors))

            for offset, sensitive_key in enumerate(
                    (
                        "access_token", "refreshToken", "client-secret", "private_key",
                        "APIKey", "APIToken", "AWSSecretAccessKey", "apikey",
                        "awssecretaccesskey", "access_t\u043eken",
                    )):
                credential_ref = "memory/evidence/credential-%d.json" % offset
                credential = {
                    sensitive_key: "sk-example-must-not-persist",
                    "version": "snapshot-v1",
                }
                credential_file = self.write(directory, credential_ref, credential)
                record["payload"]["target"] = binding(
                    credential_ref,
                    hashlib.sha256(credential_file.read_bytes()).hexdigest(),
                    "snapshot-v1",
                )
                errors = validator.validate(
                    str(self.write(
                        directory, "memory/control/credential-%d.json" % offset, record,
                    )),
                    directory,
                )[1]
                self.assertTrue(
                    any("sensitive/PII key" in error for error in errors),
                    sensitive_key,
                )

            for offset, sensitive_key in enumerate(
                    ("accessToken", "APIKey", "APIToken", "AWSSecretAccessKey",
                     "awssecretaccesskey", '"accessToken"', "'access_token'",
                     '"api\\u004bey"', '"api\\x4bey"',
                     "access_t\u043eken", "access\u200btoken")):
                yaml_ref = "memory/evidence/credential-%d.yaml" % offset
                yaml_file = pathlib.Path(directory) / yaml_ref
                yaml_file.parent.mkdir(parents=True, exist_ok=True)
                yaml_file.write_text(
                    "---\nversion: snapshot-v1\n%s: sk-example\n---\n" % sensitive_key,
                    encoding="utf-8",
                )
                record["payload"]["target"] = binding(
                    yaml_ref,
                    hashlib.sha256(yaml_file.read_bytes()).hexdigest(),
                    "snapshot-v1",
                )
                errors = validator.validate(
                    str(self.write(
                        directory, "memory/control/credential-yaml-%d.json" % offset, record,
                    )),
                    directory,
                )[1]
                self.assertTrue(
                    any("sensitive/PII field" in error for error in errors),
                    sensitive_key,
                )

            for offset, body in enumerate((
                    "settings: {accessToken: sk-example}",
                    "!!str accessToken: sk-example",
                    "a\u0301piKey: sk-example",
                    '"access\\\n  _token": sk-example',
                    'contact: "person@\\\n  example.com"',
                    )):
                yaml_ref = "memory/evidence/structured-credential-%d.yaml" % offset
                yaml_file = pathlib.Path(directory) / yaml_ref
                yaml_file.write_text(
                    "---\nversion: snapshot-v1\n%s\n---\n" % body,
                    encoding="utf-8",
                )
                record["payload"]["target"] = binding(
                    yaml_ref,
                    hashlib.sha256(yaml_file.read_bytes()).hexdigest(),
                    "snapshot-v1",
                )
                errors = validator.validate(
                    str(self.write(
                        directory,
                        "memory/control/structured-credential-%d.json" % offset,
                        record,
                    )),
                    directory,
                )[1]
                self.assertTrue(errors, body)

            unversioned_ref = "memory/evidence/unversioned.json"
            unversioned_file = self.write(directory, unversioned_ref, {"query": "brand shoes"})
            record["payload"]["target"] = binding(
                unversioned_ref,
                hashlib.sha256(unversioned_file.read_bytes()).hexdigest(),
                "snapshot-v1",
            )
            errors = validator.validate(
                str(self.write(directory, "memory/control/unversioned.json", record)), directory,
            )[1]
            self.assertTrue(any("embed version" in error for error in errors))

    def test_project_root_file_is_also_a_local_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.write(directory, "evidence.json", {"version": "v1"})
            record = evidence_artifact()
            record["payload"]["target"] = binding(
                "evidence.json", hashlib.sha256(source.read_bytes()).hexdigest(), "v1",
            )
            artifact_path = self.write(directory, "memory/control/root-ref.json", record)
            self.assertEqual([], validator.validate(str(artifact_path), directory)[1])

    def test_evidence_readiness_conflicts_and_missingness_are_consistent(self):
        stale_ready = evidence_artifact()
        stale_ready["payload"]["fields"][0]["freshness"] = "stale"
        self.assertTrue(any("ready evidence" in error for error in self.validate_record(stale_ready)[1]))

        conflict = evidence_artifact()
        field = conflict["payload"]["fields"][0]
        field.update({
            "state": "conflict",
            "sources": field["sources"] * 2,
            "value_ref": None,
            "freshness": "unknown",
            "missing_reason": "conflicting-sources",
            "conflict_group": "conflict-1",
        })
        conflict["payload"]["readiness"] = "needs-refresh"
        conflict["payload"]["unresolved_conflicts"] = []
        errors = self.validate_record(conflict)[1]
        self.assertTrue(any("exactly list conflict" in error for error in errors))
        conflict["payload"]["unresolved_conflicts"] = ["conflict-1"]
        self.assertEqual([], self.validate_record(conflict)[1])

    def test_measurement_lock_window_and_counterfactual_are_fail_closed(self):
        late_lock = measurement_artifact()
        late_lock["payload"]["locked_at"] = "2026-08-03T00:00:00Z"
        self.assertTrue(any("locked_at" in error for error in self.validate_record(late_lock)[1]))

        missing_control = measurement_artifact()
        missing_control["payload"]["control"] = None
        self.assertTrue(any(
            "requires a control" in error for error in self.validate_record(missing_control)[1]
        ))

        exploratory = measurement_artifact()
        exploratory["payload"].update({
            "counterfactual_type": "none-exploratory", "control": None, "exploratory": True,
        })
        self.assertEqual([], self.validate_record(exploratory)[1])

    def test_receipt_verifies_exact_intent_digest_and_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            intent_path = self.write(directory, "memory/control/intent.json", intent_artifact())
            digest = hashlib.sha256(intent_path.read_bytes()).hexdigest()
            receipt = receipt_artifact("memory/control/intent.json", digest)
            receipt_path = self.write(directory, "memory/control/receipt.json", receipt)
            self.assertEqual([], validator.validate(str(receipt_path), directory)[1])

            wrong_digest = copy.deepcopy(receipt)
            wrong_digest["payload"]["intent"]["sha256"] = "0" * 64
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-digest.json", wrong_digest)), directory,
            )[1]
            self.assertTrue(any("digest" in error for error in errors))

            wrong_scope = copy.deepcopy(receipt)
            wrong_scope["payload"]["operation"] = "publish"
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-scope.json", wrong_scope)), directory,
            )[1]
            self.assertTrue(any("operation does not match" in error for error in errors))

            wrong_audience = copy.deepcopy(receipt)
            wrong_audience["payload"]["actual_audience_ref"] = "opaque:segment-snapshot-2"
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-audience.json", wrong_audience)),
                directory,
            )[1]
            self.assertTrue(any("actual_audience_ref" in error for error in errors))

            late = copy.deepcopy(receipt)
            late["payload"]["attempted_at"] = "2026-08-02T10:00:00Z"
            late["payload"]["completed_at"] = "2026-08-02T10:01:00Z"
            late["created_at"] = "2026-08-02T10:01:00Z"
            errors = validator.validate(
                str(self.write(directory, "memory/control/late.json", late)), directory,
            )[1]
            self.assertTrue(any("outside the intent" in error for error in errors))

    def test_retro_binds_measurement_current_head_owner_and_read_date(self):
        with tempfile.TemporaryDirectory() as directory:
            measurement_path = self.write(
                directory, "memory/control/measurement.json", measurement_artifact(),
            )
            digest = hashlib.sha256(measurement_path.read_bytes()).hexdigest()
            retro = retro_artifact("memory/control/measurement.json", digest)
            retro_path = self.write(directory, "memory/control/retro.json", retro)
            self.assertEqual([], validator.validate(str(retro_path), directory)[1])

            forked = copy.deepcopy(retro)
            forked["payload"]["head_state"]["fork_count"] = 1
            self.assertTrue(any(
                "non-forked" in error
                for error in validator.validate(
                    str(self.write(directory, "memory/control/forked.json", forked)), directory,
                )[1]
            ))

            wrong_head = copy.deepcopy(retro)
            wrong_head["payload"]["current_head"] = binding(
                "opaque:campaign-head-2", "3" * 64, "campaign-v4",
            )
            errors = validator.validate(
                str(self.write(directory, "memory/control/wrong-head.json", wrong_head)), directory,
            )[1]
            self.assertTrue(any("current_head" in error for error in errors))

            early = copy.deepcopy(retro)
            early["payload"]["decided_at"] = "2026-08-15T12:00:00Z"
            early["created_at"] = "2026-08-15T12:00:00Z"
            errors = validator.validate(
                str(self.write(directory, "memory/control/early.json", early)), directory,
            )[1]
            self.assertTrue(any("before the preregistered" in error for error in errors))

    def test_retro_decision_codes_are_domain_neutral(self):
        with tempfile.TemporaryDirectory() as directory:
            measurement_path = self.write(
                directory, "memory/control/measurement.json", measurement_artifact(),
            )
            digest = hashlib.sha256(measurement_path.read_bytes()).hexdigest()
            for code, taxonomy in (
                ("retain", "opaque:narrative-decisions-v1"),
                ("try", "opaque:social-decisions-v1"),
                ("hold", "opaque:launch-decisions-v1"),
            ):
                retro = retro_artifact("memory/control/measurement.json", digest)
                retro["artifact_id"] = "retro-" + code
                retro["payload"]["decision_code"] = code
                retro["payload"]["decision_taxonomy_ref"] = taxonomy
                path = self.write(directory, "memory/control/retro-%s.json" % code, retro)
                self.assertEqual([], validator.validate(str(path), directory)[1])

    def test_projection_is_deterministic_read_only_and_tamper_has_no_backflow(self):
        with tempfile.TemporaryDirectory() as directory:
            measurement_path = self.write(
                directory, "memory/control/measurement.json", measurement_artifact(),
            )
            digest = hashlib.sha256(measurement_path.read_bytes()).hexdigest()
            retro_path = self.write(
                directory,
                "memory/control/retro.json",
                retro_artifact("memory/control/measurement.json", digest),
            )
            before_files = sorted(
                path.relative_to(directory).as_posix()
                for path in pathlib.Path(directory).rglob("*") if path.is_file()
            )
            before_source = measurement_path.read_bytes()
            first, errors = validator.project_artifacts(
                [str(retro_path), str(measurement_path)], directory,
            )
            self.assertEqual([], errors)
            second, errors = validator.project_artifacts(
                [str(measurement_path), str(retro_path)], directory,
            )
            self.assertEqual([], errors)
            self.assertEqual(first, second)
            self.assertIn("authoritative: false", first)
            self.assertIn("source_refs:", first)
            self.assertIn("current_heads:", first)
            self.assertIn("opaque:campaign-head-1", first)

            tampered_projection = first.replace("authoritative: false", "authoritative: true")
            self.assertNotEqual(first, tampered_projection)
            self.assertEqual(before_source, measurement_path.read_bytes())
            self.assertEqual([], validator.validate(str(measurement_path), directory)[1])
            third, errors = validator.project_artifacts(
                [str(retro_path), str(measurement_path)], directory,
            )
            self.assertEqual(first, third)
            after_files = sorted(
                path.relative_to(directory).as_posix()
                for path in pathlib.Path(directory).rglob("*") if path.is_file()
            )
            self.assertEqual(before_files, after_files)

    def test_projection_rejects_a_parent_directory_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.write(
                directory, "memory/control/measurement.json", measurement_artifact(),
            )
            alias = pathlib.Path(directory) / "memory" / "control-alias"
            alias.symlink_to(source.parent, target_is_directory=True)
            output, errors = validator.project_artifacts(
                [str(alias / source.name)], directory,
            )
            self.assertIsNone(output)
            self.assertTrue(any("symlink" in error for error in errors))

    def test_projection_source_refs_preserve_valid_paths_as_quoted_strings(self):
        with tempfile.TemporaryDirectory() as directory:
            for relative in (
                    "evidence.json", "memory/control/2026-08-01_Evidence.v1.json",
                    "a/" * 249 + "evidence1.json"):
                with self.subTest(relative=relative):
                    source = self.write(directory, relative, evidence_artifact())
                    output, errors = validator.project_artifacts([str(source)], directory)
                    self.assertEqual([], errors)
                    frontmatter = output.split("---\n", 2)[1].splitlines()
                    refs = [line.removeprefix("  - ref: ") for line in frontmatter
                            if line.startswith("  - ref: ")]
                    self.assertEqual([relative], [json.loads(ref) for ref in refs])
                    self.assertEqual(1, frontmatter.count("authoritative: false"))
                    self.assertNotIn("authoritative: true", frontmatter)
                    self.assertIn("; %s;" % validator.markdown_code_span(relative), output)

    def test_markdown_code_span_escapes_paths_that_would_break_markup(self):
        self.assertEqual("`memory/control/evidence.json`",
                         validator.markdown_code_span("memory/control/evidence.json"))
        self.assertEqual("``memory/control/evidence`injected`.json``",
                         validator.markdown_code_span("memory/control/evidence`injected`.json"))
        self.assertEqual("```memory/control/``nested``.json```",
                         validator.markdown_code_span("memory/control/``nested``.json"))
        self.assertEqual("`` `starts.json ``",
                         validator.markdown_code_span("`starts.json"))
        self.assertEqual("`memory/control/evidence\\n.json`",
                         validator.markdown_code_span("memory/control/evidence\n.json"))
        self.assertEqual("`memory/control/evidence\\r.json`",
                         validator.markdown_code_span("memory/control/evidence\r.json"))
        self.assertEqual("`memory/control/evidence\\u2028.json`",
                         validator.markdown_code_span("memory/control/evidence\u2028.json"))
        rendered = "- %s — %s; %s; %s" % (
            validator.markdown_code_span("evidence-1"),
            validator.markdown_code_span("evidence-observation"),
            validator.markdown_code_span("memory/control/evidence`injected`.json"),
            validator.markdown_code_span("sha256:" + ("a" * 64)),
        )
        self.assertEqual(1, rendered.count("\n") + 1)
        self.assertNotIn("\n# ", rendered)
        self.assertNotIn("\n- ", rendered)
        self.assertTrue(rendered.startswith("- `"))
        self.assertIn("``memory/control/evidence`injected`.json``", rendered)

    def test_projection_rejects_filename_injection_in_yaml_and_markdown(self):
        with tempfile.TemporaryDirectory() as directory:
            for relative in (
                    'a"\n    sha256: "fake"\nauthoritative: true\n'
                    'source_refs:\n  - ref: "b.json',
                    'memory/control/evidence".json',
                    "memory/control/evidence\n.json",
                    "memory/control/evidence\r.json",
                    "memory/control/evidence\t.json",
                    "memory/control/evidence\\n.json",
                    "memory/control/evidence\u2028.json",
                    "memory/control/evidence`injected`.json",
                    "memory/control/evidence [injected].json",
                    "opaque:source.json",
                    "a/" * 250 + "evidence.json"):
                with self.subTest(relative=relative):
                    source = self.write(directory, relative, evidence_artifact())
                    self.assertEqual([], validator.validate(str(source), directory)[1])
                    output, errors = validator.project_artifacts([str(source)], directory)
                    self.assertIsNone(output)
                    self.assertTrue(any("projection source ref" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
