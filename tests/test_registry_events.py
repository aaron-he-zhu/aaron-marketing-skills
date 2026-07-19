import importlib.util
from concurrent.futures import ThreadPoolExecutor
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("registry_events", ROOT / "scripts" / "registry-events.py")
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)


def event(registry_name, key, aggregate_id="record-1", operation="upsert", **overrides):
    owner = registry.OWNERS[registry_name]
    default_payload = {"set": {"title": "Fixture"}}
    if registry_name == "consent":
        default_payload = {"set": {
            "subscription_status": "subscribed", "basis_ref": "fixture",
        }}
    value = {
        "schema_version": "1.0",
        "idempotency_key": key,
        "aggregate_id": aggregate_id,
        "operation": operation,
        "occurred_at": "2026-07-10T10:00:00Z",
        "actor": {"type": "skill", "id": owner},
        "authorized_by": "user",
        "authorization_ref": "explicit-test-approval",
        "source": {"type": "user-provided", "ref": "fixture", "observed_at": "2026-07-10"},
        "payload": default_payload,
    }
    if operation in {"propose", "upsert", "transition", "tombstone", "restore", "erase"}:
        value["expected_revision"] = 0
    value.update(overrides)
    return value


class RegistryEventTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.host_key = "registry-test-host-key-material-32-bytes-minimum"
        self.previous_host_key = os.environ.get(registry.HOST_KEY_ENV)
        os.environ[registry.HOST_KEY_ENV] = self.host_key
        self.raw_append_event = registry.append_event
        registry.append_event = self.authorized_append_event

    def tearDown(self):
        registry.append_event = self.raw_append_event
        if self.previous_host_key is None:
            os.environ.pop(registry.HOST_KEY_ENV, None)
        else:
            os.environ[registry.HOST_KEY_ENV] = self.previous_host_key
        self.temp.cleanup()

    def capability(self, registry_name, request, *, root=None, expires_at=None,
                   capability_id=None, capability_kind=None):
        if capability_kind is None:
            capability_kind = (
                "safety" if registry_name == "consent"
                and request.get("operation") == "erase"
                and request.get("authorized_by") == "data-subject" else "owner"
            )
        return registry.issue_host_capability(
            self.host_key,
            registry_name,
            request["actor"]["id"],
            [request["operation"]],
            expires_at or "2999-01-01T00:00:00Z",
            capability_id=capability_id,
            request=request,
            project_root=root or self.root,
            capability_kind=capability_kind,
        )

    def authorized_append_event(self, root, registry_name, request, capability_token=None):
        operation = request.get("operation")
        direct = (
            operation == "propose"
            or (registry_name == "consent" and operation == "suppress")
        )
        token = capability_token
        if not direct and token is None:
            token = self.capability(registry_name, request, root=root)
        return self.raw_append_event(
            root, registry_name, request, capability_token=token,
        )

    def cli_append(self, registry_name, request_path):
        request = json.loads(Path(request_path).read_text())
        direct = (
            request.get("operation") == "propose"
            or (registry_name == "consent" and request.get("operation") == "suppress")
        )
        safety = (
            registry_name == "consent" and request.get("operation") == "erase"
            and request.get("authorized_by") == "data-subject"
        )
        command = "append" if direct else ("safety-append" if safety else "owner-append")
        environment = os.environ.copy()
        if not direct:
            environment[registry.HOST_CAPABILITY_ENV] = self.capability(registry_name, request)
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "registry-events.py"),
                "--root", str(self.root), command, registry_name, str(request_path),
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=environment,
        )

    def test_stale_projection_temp_is_reclaimed_under_the_stream_lock(self):
        proposal = event(
            "entities", "proposal-stale-tmp-1", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"title": "Acme"}},
        )
        registry.append_event(self.root, "entities", proposal)
        _, projection_path, _ = registry.memory_paths(self.root, "entities")
        stale = projection_path.parent / (".%s.registry-tmp" % projection_path.name)
        stale.write_text("{}", encoding="utf-8")
        follow_up = event(
            "entities", "proposal-stale-tmp-2", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"title": "Acme Two"}},
        )
        result = registry.append_event(self.root, "entities", follow_up)
        self.assertFalse(result["deduplicated"])
        self.assertFalse(stale.exists())

    def test_projection_install_failure_names_the_committed_event(self):
        proposal = event(
            "entities", "proposal-committed-1", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"title": "Acme"}},
        )
        original = registry.write_projections

        def broken(*args, **kwargs):
            raise OSError("disk full")

        registry.write_projections = broken
        try:
            with self.assertRaisesRegex(registry.RegistryError, "event_committed=true"):
                registry.append_event(self.root, "entities", proposal)
        finally:
            registry.write_projections = original
        stream_path, _, _ = registry.memory_paths(self.root, "entities")
        lines = stream_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 1)
        retry = registry.append_event(self.root, "entities", proposal)
        self.assertTrue(retry["deduplicated"])

    def test_proposal_acceptance_and_idempotent_retry(self):
        proposal = event(
            "entities", "proposal-1", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"title": "Acme"}},
        )
        first = registry.append_event(self.root, "entities", proposal)
        self.assertFalse(first["deduplicated"])
        self.assertIsNone(first["record"])
        retry = registry.append_event(self.root, "entities", proposal)
        self.assertTrue(retry["deduplicated"])
        state = registry.load_state(self.root, "entities")
        self.assertEqual(len(state["pending"]), 1)

        decision_with_revision = event(
            "entities", "accept-with-revision", operation="accept", payload={},
            proposal_event_id=first["event"]["event_id"], expected_revision=0,
        )
        with self.assertRaisesRegex(registry.RegistryError, "inherit.*omit expected_revision"):
            registry.append_event(self.root, "entities", decision_with_revision)

        accept = event(
            "entities", "accept-1", operation="accept", payload={},
            proposal_event_id=first["event"]["event_id"],
        )
        accepted = registry.append_event(self.root, "entities", accept)
        self.assertEqual(accepted["record"]["revision"], 1)
        self.assertEqual(accepted["record"]["data"]["title"], "Acme")
        self.assertEqual(accepted["record"]["last_source"], proposal["source"])
        self.assertEqual(accepted["record"]["source_occurred_at"], proposal["occurred_at"])
        self.assertEqual(registry.load_state(self.root, "entities")["pending"], {})

    def test_reject_requires_reason_and_cannot_smuggle_mutation(self):
        proposal = registry.append_event(
            self.root,
            "entities",
            event(
                "entities", "proposal-reject", operation="propose",
                proposed_operation="upsert", actor={"type": "skill", "id": "content-writer"},
                payload={"set": {"title": "Unsubstantiated"}},
            ),
        )
        without_reason = event(
            "entities", "reject-without-reason", operation="reject", payload={},
            proposal_event_id=proposal["event"]["event_id"],
        )
        with self.assertRaisesRegex(registry.RegistryError, "requires payload.reason"):
            registry.append_event(self.root, "entities", without_reason)
        smuggled = event(
            "entities", "reject-with-mutation", operation="reject",
            payload={"reason": "unsupported", "set": {"title": "Still applied"}},
            proposal_event_id=proposal["event"]["event_id"],
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot carry a second mutation"):
            registry.append_event(self.root, "entities", smuggled)

    def test_idempotency_conflict_and_optimistic_revision(self):
        original = event("claims", "claim-write", payload={"set": {"status": "draft"}})
        registry.append_event(self.root, "claims", original)
        changed = event("claims", "claim-write", payload={"set": {"status": "approved"}})
        with self.assertRaisesRegex(registry.RegistryError, "idempotency"):
            registry.append_event(self.root, "claims", changed)
        stale = event(
            "claims", "claim-stale", expected_revision=0,
            payload={"set": {"status": "approved"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "stale expected_revision"):
            registry.append_event(self.root, "claims", stale)

    def test_concurrent_same_revision_has_one_winner(self):
        registry.append_event(
            self.root, "claims",
            event("claims", "claim-base", payload={"set": {"status": "draft"}}),
        )
        paths = []
        for index, status in enumerate(("approved", "rejected"), 1):
            path = self.root / ("concurrent-%d.json" % index)
            path.write_text(json.dumps(event(
                "claims", "claim-race-%d" % index, expected_revision=1,
                payload={"set": {"status": status}},
            )))
            paths.append(path)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda path: self.cli_append("claims", path), paths))
        self.assertEqual(sorted(result.returncode for result in results), [0, 1])
        self.assertTrue(any("stale expected_revision" in result.stderr for result in results))
        state = registry.load_state(self.root, "claims")
        self.assertEqual(state["records"]["record-1"]["revision"], 2)
        self.assertEqual(state["last_offset"], 2)

    def test_concurrent_identical_retry_is_idempotent(self):
        request = self.root / "same-event.json"
        request.write_text(json.dumps(event("entities", "parallel-identical")))
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(
                lambda _: self.cli_append("entities", request), range(2)
            ))
        self.assertEqual([result.returncode for result in results], [0, 0])
        outputs = [json.loads(result.stdout) for result in results]
        self.assertEqual(sorted(output["deduplicated"] for output in outputs), [False, True])
        stream = self.root / "memory" / "events" / "entities.ndjson"
        self.assertEqual(len(stream.read_text().splitlines()), 1)

    def test_transition_compare_and_set(self):
        registry.append_event(
            self.root, "launches",
            event("launches", "launch-create", payload={"set": {"state": "draft"}}),
        )
        moved = event(
            "launches", "launch-move", operation="transition", expected_revision=1,
            payload={"transition": {"from": "draft", "to": "concept"}},
        )
        result = registry.append_event(self.root, "launches", moved)
        self.assertEqual(result["record"]["data"]["state"], "concept")
        wrong = event(
            "launches", "launch-wrong", operation="transition", expected_revision=2,
            payload={"transition": {"from": "draft", "to": "alpha"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "transition conflict"):
            registry.append_event(self.root, "launches", wrong)

    def test_transition_graph_rejects_jump_and_upsert_bypass(self):
        registry.append_event(
            self.root, "launches",
            event("launches", "launch-init", payload={"set": {"state": "draft"}}),
        )
        jump = event(
            "launches", "launch-jump", operation="transition", expected_revision=1,
            payload={"transition": {"from": "draft", "to": "general-availability"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "invalid launches transition"):
            registry.append_event(self.root, "launches", jump)
        bypass = event(
            "launches", "launch-bypass", expected_revision=1,
            payload={"set": {"state": "general-availability"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "later changes require transition"):
            registry.append_event(self.root, "launches", bypass)

    def test_channel_reactivation_path_is_explicit(self):
        registry.append_event(
            self.root, "channels",
            event("channels", "channel-init", payload={"set": {"state": "proposed"}}),
        )
        revision = 1
        for index, (source, target) in enumerate((
                ("proposed", "warming"), ("warming", "active"),
                ("active", "paused"), ("paused", "warming")), 1):
            result = registry.append_event(
                self.root, "channels",
                event(
                    "channels", "channel-step-%d" % index, operation="transition",
                    expected_revision=revision,
                    payload={"transition": {"from": source, "to": target}},
                ),
            )
            revision = result["record"]["revision"]
        self.assertEqual(result["record"]["data"]["state"], "warming")

    def test_consent_suppression_is_immediate_and_replay_safe(self):
        subject = "sha256-7d9f4b2a"
        suppress = event(
            "consent", "unsubscribe-1", aggregate_id=subject, operation="suppress",
            actor={"type": "data-subject", "id": subject},
            authorized_by="data-subject", authorization_ref="unsubscribe-click-evt-1",
            source={"type": "measured", "ref": "esp-webhook-evt-1", "observed_at": "2026-07-10"},
            payload={"reason": "unsubscribe"},
        )
        registry.append_event(self.root, "consent", suppress)
        self.assertTrue(registry.is_suppressed(self.root, subject))
        projection = json.loads((self.root / "memory/projections/consent-suppressions.json").read_text())
        self.assertIn(subject, projection["suppressed"])

        restore = event(
            "consent", "resubscribe-1", aggregate_id=subject, operation="restore",
            expected_revision=1,
            occurred_at="2026-07-11T10:00:00Z",
            source={"type": "measured", "ref": "doi-event-2",
                    "observed_at": "2026-07-11T09:00:00Z"},
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "doi-event-2",
            }},
        )
        registry.append_event(self.root, "consent", restore)
        self.assertFalse(registry.is_suppressed(self.root, subject))

    def test_consent_erasure_keeps_safety_tombstone(self):
        subject = "sha256-erasure-subject"
        erase = event(
            "consent", "erase-1", aggregate_id=subject, operation="erase",
            actor={"type": "data-subject", "id": subject}, authorized_by="data-subject",
            authorization_ref="subject-erasure-request-1",
            payload={"reason": "data-subject-erasure"},
        )
        result = registry.append_event(self.root, "consent", erase)
        self.assertEqual(result["record"]["data"], {})
        self.assertEqual(result["record"]["status"], "erased")
        self.assertTrue(registry.is_suppressed(self.root, subject))

    def test_consent_rejects_raw_pii(self):
        raw_email = "person" + "@" + "example.test"
        raw = event(
            "consent", "consent-raw-pii", operation="upsert",
            payload={"set": {"email": raw_email}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email|raw PII"):
            registry.append_event(self.root, "consent", raw)
        raw_ref = event(
            "consent", "consent-source-pii", operation="upsert",
            source={"type": "user-provided", "ref": raw_email, "observed_at": "2026-07-10"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email"):
            registry.append_event(self.root, "consent", raw_ref)

    def test_non_owner_cannot_mutate_canonical_state(self):
        request = event(
            "channels", "bad-owner", actor={"type": "skill", "id": "social-calendar-builder"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "channel-registry"):
            registry.append_event(self.root, "channels", request)

    def test_canonical_authority_requires_out_of_band_host_capability(self):
        request = event("entities", "self-reported-owner")
        with self.assertRaisesRegex(registry.RegistryError, "host capability"):
            self.raw_append_event(self.root, "entities", request)
        with self.assertRaisesRegex(registry.RegistryError, "signature"):
            self.raw_append_event(
                self.root, "entities", request, capability_token="e30.invalid",
            )

        token = self.capability("entities", request)
        result = self.raw_append_event(
            self.root, "entities", request, capability_token=token,
        )
        self.assertEqual(result["record"]["revision"], 1)
        self.assertEqual(result["event"]["principal"]["type"], "host-capability")
        self.assertNotIn(token, registry.canonical_json(result["event"]))

        ordinary = self.root / "ordinary-owner.json"
        ordinary.write_text(json.dumps(event("claims", "ordinary-owner")))
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts/registry-events.py"),
             "--root", str(self.root), "append", "claims", str(ordinary)],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            env=os.environ.copy(),
        )
        self.assertEqual(completed.returncode, 1)
        self.assertIn("host capability", completed.stderr)

    def test_capability_is_bound_to_registry_principal_operation_and_expiry(self):
        request = event("entities", "capability-binding")
        claims_request = event("claims", "capability-other-registry")
        wrong_registry = self.capability(
            "claims", claims_request,
        )
        with self.assertRaisesRegex(registry.RegistryError, "registry"):
            self.raw_append_event(
                self.root, "entities", request, capability_token=wrong_registry,
            )
        other_principal_request = event(
            "entities", "capability-other-principal",
            actor={"type": "skill", "id": "content-writer"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "entity-registry"):
            registry.issue_host_capability(
                self.host_key, "entities", "content-writer", ["upsert"],
                "2999-01-01T00:00:00Z", request=other_principal_request,
                project_root=self.root,
            )
        tombstone_request = event(
            "entities", "capability-other-operation", operation="tombstone",
            payload={"reason": "retired"},
        )
        wrong_operation = self.capability(
            "entities", tombstone_request,
        )
        with self.assertRaisesRegex(registry.RegistryError, "operation"):
            self.raw_append_event(
                self.root, "entities", request, capability_token=wrong_operation,
            )
        expired = self.capability(
            "entities", request, expires_at="2000-01-01T00:00:00Z",
        )
        with self.assertRaisesRegex(registry.RegistryError, "expired"):
            self.raw_append_event(
                self.root, "entities", request, capability_token=expired,
            )

    def test_capability_binds_request_identity_root_and_is_single_use(self):
        first = event("entities", "bound-request-1")
        token = self.capability(
            "entities", first, capability_id="single-use-capability",
        )
        changed_aggregate = dict(first)
        changed_aggregate["aggregate_id"] = "record-2"
        with self.assertRaisesRegex(registry.RegistryError, "normalized request"):
            self.raw_append_event(
                self.root, "entities", changed_aggregate, capability_token=token,
            )
        changed_idempotency = dict(first)
        changed_idempotency["idempotency_key"] = "bound-request-other-key"
        with self.assertRaisesRegex(registry.RegistryError, "normalized request"):
            self.raw_append_event(
                self.root, "entities", changed_idempotency, capability_token=token,
            )
        other_root = self.root / "other-project"
        other_root.mkdir()
        with self.assertRaisesRegex(registry.RegistryError, "project root"):
            self.raw_append_event(
                other_root, "entities", first, capability_token=token,
            )

        self.raw_append_event(self.root, "entities", first, capability_token=token)
        second = event(
            "entities", "bound-request-2", expected_revision=1,
            payload={"set": {"title": "Second"}},
        )
        reused_id = self.capability(
            "entities", second, capability_id="single-use-capability",
        )
        with self.assertRaisesRegex(registry.RegistryError, "already been consumed"):
            self.raw_append_event(
                self.root, "entities", second, capability_token=reused_id,
            )

    def test_capability_expiry_is_rechecked_inside_append_lock(self):
        request = event("entities", "expires-under-lock")
        expiry = "2030-01-01T00:00:00Z"
        token = self.capability("entities", request, expires_at=expiry)
        original_verify = registry.verify_host_capability
        calls = []

        def advancing_verify(*args, **kwargs):
            now = dt.datetime(
                2029 if not calls else 2031, 1, 1, tzinfo=dt.timezone.utc,
            )
            calls.append(now)
            kwargs["now"] = now
            return original_verify(*args, **kwargs)

        with mock.patch.object(
                registry, "verify_host_capability", side_effect=advancing_verify):
            with self.assertRaisesRegex(registry.RegistryError, "expired"):
                self.raw_append_event(
                    self.root, "entities", request, capability_token=token,
                )
        stream = self.root / "memory/events/entities.ndjson"
        self.assertTrue(stream.exists())
        self.assertEqual(stream.read_text(), "")

    def test_data_subject_erase_requires_request_bound_safety_capability(self):
        subject = "sha256-safety-erasure"
        request = event(
            "consent", "bound-erasure", aggregate_id=subject, operation="erase",
            actor={"type": "data-subject", "id": subject},
            authorized_by="data-subject",
            payload={"reason": "data-subject-erasure"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "host capability"):
            self.raw_append_event(self.root, "consent", request)
        with self.assertRaisesRegex(registry.RegistryError, "safety capability"):
            registry.issue_host_capability(
                self.host_key, "consent", subject, ["erase"],
                "2999-01-01T00:00:00Z", request=request,
                project_root=self.root, capability_kind="owner",
            )
        token = self.capability("consent", request, capability_kind="safety")
        request_path = self.root / "erasure.json"
        request_path.write_text(json.dumps(request), encoding="utf-8")
        environment = os.environ.copy()
        environment[registry.HOST_CAPABILITY_ENV] = token
        wrong_command = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "registry-events.py"),
                "--root", str(self.root), "owner-append", "consent", str(request_path),
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            check=False, env=environment,
        )
        self.assertNotEqual(wrong_command.returncode, 0)
        self.assertIn("owner-append requires a host-capability", wrong_command.stderr)
        result = self.raw_append_event(
            self.root, "consent", request, capability_token=token,
        )
        self.assertEqual(result["event"]["principal"]["type"], "safety-capability")
        self.assertTrue(result["record"]["suppressed"])

    def test_generic_suppression_is_deny_only_privacy_policy(self):
        request = event(
            "consent", "privacy-first-suppress", aggregate_id="sha256-deny-only",
            operation="suppress", actor={"type": "skill", "id": "esp-webhook"},
            payload={"reason": "complaint"},
        )
        result = self.raw_append_event(self.root, "consent", request)
        self.assertEqual(
            result["event"]["principal"],
            {"type": "privacy-suppression", "id": "esp-webhook"},
        )
        self.assertTrue(registry.is_suppressed(self.root, "sha256-deny-only"))
        restore = event(
            "consent", "untrusted-restore", aggregate_id="sha256-deny-only",
            operation="restore", expected_revision=1,
            occurred_at="2026-07-11T10:00:00Z",
            source={"type": "measured", "ref": "new-opt-in",
                    "observed_at": "2026-07-11T09:00:00Z"},
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "new-opt-in",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "host capability"):
            self.raw_append_event(self.root, "consent", restore)

    def test_data_subject_actor_must_match_consent_aggregate(self):
        request = event(
            "consent", "mismatched-subject", aggregate_id="subject-a", operation="suppress",
            actor={"type": "data-subject", "id": "subject-b"},
            authorized_by="data-subject", payload={"reason": "unsubscribe"},
        )
        request.pop("expected_revision", None)
        with self.assertRaisesRegex(registry.RegistryError, "match.*aggregate_id"):
            self.raw_append_event(self.root, "consent", request)

    def test_restore_requires_newer_trusted_matching_basis(self):
        subject = "sha256-restore-basis"
        registry.append_event(
            self.root, "consent",
            event(
                "consent", "basis-suppress", aggregate_id=subject, operation="suppress",
                occurred_at="2026-07-10T10:00:00Z",
                payload={"reason": "withdrawal"},
            ),
        )
        older = event(
            "consent", "basis-older", aggregate_id=subject, operation="restore",
            expected_revision=1, occurred_at="2026-07-11T10:00:00Z",
            source={"type": "measured", "ref": "doi-new",
                    "observed_at": "2026-07-09T09:00:00Z"},
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "doi-new",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "newer than the withdrawal"):
            registry.append_event(self.root, "consent", older)
        proxy = dict(older)
        proxy["idempotency_key"] = "basis-proxy"
        proxy["source"] = {"type": "proxy", "ref": "doi-new",
                           "observed_at": "2026-07-11T09:00:00Z"}
        with self.assertRaisesRegex(registry.RegistryError, "measured or user-provided"):
            registry.append_event(self.root, "consent", proxy)
        mismatched = dict(older)
        mismatched["idempotency_key"] = "basis-mismatch"
        mismatched["source"] = {
            "type": "measured", "ref": "different-proof",
            "observed_at": "2026-07-11T09:00:00Z",
        }
        with self.assertRaisesRegex(registry.RegistryError, "must equal source.ref"):
            registry.append_event(self.root, "consent", mismatched)
        non_string = dict(older)
        non_string["idempotency_key"] = "basis-not-string"
        non_string["source"] = {"type": "measured", "ref": "doi-new",
                                "observed_at": "2026-07-11T09:00:00Z"}
        non_string["payload"] = {"reason": "new-confirmed-opt-in", "set": {
            "subscription_status": "subscribed", "basis_ref": 7,
        }}
        with self.assertRaisesRegex(registry.RegistryError, "basis_ref.*opaque|string basis_ref"):
            registry.append_event(self.root, "consent", non_string)
        self.assertTrue(registry.is_suppressed(self.root, subject))

    def test_backdated_suppression_cannot_weaken_latest_withdrawal_boundary(self):
        subject = "sha256-backdated-withdrawal"
        registry.append_event(
            self.root, "consent",
            event(
                "consent", "latest-withdrawal", aggregate_id=subject,
                operation="suppress", occurred_at="2026-07-10T10:00:00Z",
                payload={"reason": "withdrawal"},
            ),
        )
        registry.append_event(
            self.root, "consent",
            event(
                "consent", "backdated-withdrawal", aggregate_id=subject,
                operation="suppress", occurred_at="2026-07-09T10:00:00Z",
                payload={"reason": "withdrawal"},
            ),
        )
        restore = event(
            "consent", "restore-after-backdated", aggregate_id=subject,
            operation="restore", expected_revision=2,
            occurred_at="2026-07-11T10:00:00Z",
            source={
                "type": "measured", "ref": "doi-between-withdrawals",
                "observed_at": "2026-07-10T09:00:00Z",
            },
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed",
                "basis_ref": "doi-between-withdrawals",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "newer than the withdrawal"):
            registry.append_event(self.root, "consent", restore)
        state = registry.load_state(self.root, "consent")
        self.assertEqual(
            state["records"][subject]["last_suppressed_at"],
            "2026-07-10T10:00:00Z",
        )

    def test_consent_scans_every_string_leaf_for_raw_email(self):
        raw_email = "nested" + "@" + "example.test"
        request = event(
            "consent", "nested-raw-email",
            payload={"set": {"note": {"nested": ["safe", raw_email]}}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email"):
            registry.append_event(self.root, "consent", request)
        authorization_request = event(
            "consent", "authorization-raw-email", authorization_ref=raw_email,
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email"):
            registry.append_event(self.root, "consent", authorization_request)

    def test_consent_scans_nested_keys_and_values_for_phone_like_contact_pii(self):
        raw_phone = "+1 415-555-1212"
        nested_value = event(
            "consent", "nested-raw-phone-value",
            payload={"set": {"proof": {"arbitrary": ["safe", raw_phone]}}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw phone number"):
            registry.append_event(self.root, "consent", nested_value)
        nested_key = event(
            "consent", "nested-raw-phone-key",
            payload={"set": {"proof": {raw_phone: "copied contact"}}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw phone number"):
            registry.append_event(self.root, "consent", nested_key)

    def test_consent_nfkc_and_closed_shape_block_pii_bypasses(self):
        fullwidth_email = event(
            "consent", "fullwidth-email",
            source={"type": "user-provided", "ref": "ｊａｎｅ＠ｅｘａｍｐｌｅ.test",
                    "observed_at": "2026-07-10"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw email"):
            registry.append_event(self.root, "consent", fullwidth_email)
        fullwidth_phone = event(
            "consent", "fullwidth-phone", authorization_ref="＋１ ４１５－５５５－１２１２",
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw phone"):
            registry.append_event(self.root, "consent", fullwidth_phone)
        date_shaped_phone = event(
            "consent", "date-shaped-phone",
            source={"type": "user-provided", "ref": "20260711123",
                    "observed_at": "2026-07-10"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw phone"):
            registry.append_event(self.root, "consent", date_shaped_phone)
        free_text_name = event(
            "consent", "free-text-name",
            payload={"set": {"note": "Jane Smith"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "non-minimized fields"):
            registry.append_event(self.root, "consent", free_text_name)
        free_text_address = event(
            "consent", "free-text-address", authorization_ref="123 Main Street",
        )
        with self.assertRaisesRegex(registry.RegistryError, "opaque, non-PII"):
            registry.append_event(self.root, "consent", free_text_address)
        unicode_key = event(
            "consent", "fullwidth-key",
            payload={"set": {"ｅｍａｉｌ": "opaque"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "raw PII fields"):
            registry.append_event(self.root, "consent", unicode_key)
        for encoded_reference in (
                "john%40gmail.com", "https://example.test/?email=john%40gmail.com"):
            encoded = event(
                "consent", "encoded-contact-" + str(len(encoded_reference)),
                authorization_ref=encoded_reference,
            )
            with self.assertRaisesRegex(registry.RegistryError, "opaque, non-PII"):
                registry.append_event(self.root, "consent", encoded)

    def test_consent_minimized_payload_accepts_only_typed_reference_fields(self):
        request = event(
            "consent", "minimal-consent",
            occurred_at="2026-07-10T10:00:00Z",
            source={"type": "user-provided", "ref": "form-event-42",
                    "observed_at": "2026-07-10"},
            authorization_ref="approval-42",
            payload={"set": {
                "subscription_status": "subscribed",
                "basis_ref": "form-event-42",
                "proof_ref": "double-opt-in-43",
                "lawful_basis": "consent",
                "consented_at": "2026-07-10T09:59:00Z",
                "jurisdiction": "DE",
                "channel": "email",
            }},
        )
        result = registry.append_event(self.root, "consent", request)
        self.assertEqual(result["record"]["data"]["lawful_basis"], "consent")

    def test_governed_state_cannot_be_unset_or_reinitialized(self):
        registry.append_event(
            self.root, "launches",
            event("launches", "state-init", payload={"set": {"state": "draft"}}),
        )
        unset = event(
            "launches", "state-unset", expected_revision=1,
            payload={"unset": ["state"]},
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot be unset"):
            registry.append_event(self.root, "launches", unset)
        proposed_unset = event(
            "launches", "state-unset-proposal", operation="propose",
            proposed_operation="upsert", expected_revision=1,
            actor={"type": "skill", "id": "launch-monitor"},
            payload={"unset": ["state"]},
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot be unset"):
            registry.append_event(self.root, "launches", proposed_unset)

        missing_state = event(
            "channels", "state-missing-init", payload={"set": {"title": "channel"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "must initialize state"):
            registry.append_event(self.root, "channels", missing_state)

    def test_canonical_mutations_and_proposals_require_revision(self):
        direct = event("entities", "missing-cas")
        direct.pop("expected_revision")
        with self.assertRaisesRegex(registry.RegistryError, "requires expected_revision"):
            registry.append_event(self.root, "entities", direct)

        proposal = event(
            "entities", "missing-proposal-cas", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "content-writer"},
        )
        proposal.pop("expected_revision")
        with self.assertRaisesRegex(registry.RegistryError, "requires expected_revision"):
            registry.append_event(self.root, "entities", proposal)

    def test_effective_operation_rejects_ambiguous_payloads(self):
        bad_proposal = event(
            "entities", "bad-transition-proposal", operation="propose",
            proposed_operation="transition", actor={"type": "skill", "id": "content-writer"},
            payload={"set": {"state": "active"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "requires payload.transition"):
            registry.append_event(self.root, "entities", bad_proposal)

        no_op = event("entities", "empty-upsert", payload={"set": {}})
        with self.assertRaisesRegex(registry.RegistryError, "non-empty"):
            registry.append_event(self.root, "entities", no_op)

        smuggled = event(
            "launches", "transition-with-set", operation="transition",
            payload={"transition": {"from": None, "to": "draft"}, "set": {"title": "x"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "cannot carry set or unset"):
            registry.append_event(self.root, "launches", smuggled)

    def test_restore_requires_prior_suppression_and_terminal_records_do_not_resurrect(self):
        restore = event(
            "consent", "restore-without-suppress", operation="restore",
            occurred_at="2026-07-11T10:00:00Z",
            source={"type": "measured", "ref": "doi-1",
                    "observed_at": "2026-07-11T09:00:00Z"},
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "doi-1",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "existing suppressed"):
            registry.append_event(self.root, "consent", restore)

        registry.append_event(
            self.root, "entities",
            event("entities", "entity-tombstone", operation="tombstone",
                  payload={"reason": "retired"}),
        )
        resurrect = event(
            "entities", "entity-resurrect", expected_revision=1,
            payload={"set": {"title": "Back"}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "terminal"):
            registry.append_event(self.root, "entities", resurrect)

    def test_post_erasure_restore_requires_newer_owner_authorized_basis(self):
        subject = "sha256-erased-then-resubscribed"
        registry.append_event(
            self.root, "consent",
            event(
                "consent", "erase-before-new-basis", aggregate_id=subject,
                operation="erase", occurred_at="2026-07-10T10:00:00Z",
                actor={"type": "data-subject", "id": subject},
                authorized_by="data-subject", payload={"reason": "data-subject-erasure"},
            ),
        )
        stale_restore = event(
            "consent", "stale-post-erasure-restore", aggregate_id=subject,
            operation="restore", expected_revision=1,
            occurred_at="2026-07-11T10:00:00Z",
            source={
                "type": "measured", "ref": "old-opt-in",
                "observed_at": "2026-07-09T10:00:00Z",
            },
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed", "basis_ref": "old-opt-in",
            }},
        )
        with self.assertRaisesRegex(registry.RegistryError, "newer than the withdrawal"):
            registry.append_event(self.root, "consent", stale_restore)
        self.assertTrue(registry.is_suppressed(self.root, subject))

        fresh_restore = event(
            "consent", "fresh-post-erasure-restore", aggregate_id=subject,
            operation="restore", expected_revision=1,
            occurred_at="2026-07-11T10:00:00Z",
            source={
                "type": "measured", "ref": "new-double-opt-in",
                "observed_at": "2026-07-11T09:00:00Z",
            },
            payload={"reason": "new-confirmed-opt-in", "set": {
                "subscription_status": "subscribed",
                "basis_ref": "new-double-opt-in",
            }},
        )
        restored = registry.append_event(self.root, "consent", fresh_restore)
        self.assertEqual(restored["record"]["status"], "active")
        self.assertFalse(registry.is_suppressed(self.root, subject))

    def test_replay_semantically_validates_rehashed_events(self):
        registry.append_event(self.root, "entities", event("entities", "semantic-base"))
        stream = self.root / "memory/events/entities.ndjson"
        stored = json.loads(stream.read_text())
        stored.pop("expected_revision")
        request = {key: stored[key] for key in registry.REQUEST_FIELDS if key in stored}
        stored["request_hash"] = registry.sha256_json(request)
        stored["event_hash"] = registry.event_hash(stored)
        stream.write_text(registry.canonical_json(stored) + "\n")
        with self.assertRaisesRegex(registry.RegistryError, "stored event is invalid"):
            registry.load_state(self.root, "entities")

    def test_replay_rejects_duplicate_keys_and_noncanonical_json(self):
        registry.append_event(self.root, "entities", event("entities", "duplicate-key"))
        stream = self.root / "memory/events/entities.ndjson"
        raw = stream.read_text(encoding="utf-8")
        stream.write_text(
            raw.replace('{"actor":', '{"operation":"erase","actor":', 1),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(registry.RegistryError, "invalid JSON|not canonical"):
            registry.load_state(self.root, "entities")

    def test_malformed_json_types_fail_as_registry_errors_without_traceback(self):
        cases = []
        malformed = event("entities", "bad-operation")
        malformed["operation"] = []
        cases.append(malformed)
        malformed = event("entities", "bad-authorized-by")
        malformed["authorized_by"] = {}
        cases.append(malformed)
        malformed = event("entities", "bad-actor-type")
        malformed["actor"]["type"] = []
        cases.append(malformed)
        malformed = event("entities", "bad-source-type")
        malformed["source"]["type"] = {}
        cases.append(malformed)
        malformed = event("consent", "bad-consent-status")
        malformed["payload"]["set"]["subscription_status"] = []
        cases.append(malformed)
        for request in cases:
            with self.assertRaises(registry.RegistryError):
                registry.validate_request(
                    "consent" if request["idempotency_key"] == "bad-consent-status"
                    else "entities",
                    request,
                )

        request_path = self.root / "malformed.json"
        request_path.write_text(json.dumps(cases[0]), encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "registry-events.py"),
                "--root", str(self.root), "append", "entities", str(request_path),
            ],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
            env=os.environ.copy(),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)

    def test_strict_json_rejects_parser_recursion_as_registry_error(self):
        with mock.patch.object(
                registry.json, "loads", side_effect=RecursionError("deep fixture")):
            with self.assertRaisesRegex(registry.RegistryError, "strict JSON"):
                registry.strict_json_loads("[]", "deep fixture")

        deep = {}
        cursor = deep
        for _ in range(registry.MAX_JSON_DEPTH + 2):
            cursor["nested"] = {}
            cursor = cursor["nested"]
        deeply_nested = event(
            "entities", "deep-payload", payload={"set": {"nested": deep}},
        )
        with self.assertRaisesRegex(registry.RegistryError, "depth limit"):
            registry.validate_request("entities", deeply_nested)

    def test_forged_canonical_replay_fails_after_recomputing_plain_hashes(self):
        registry.append_event(self.root, "entities", event("entities", "signed-canonical"))
        stream = self.root / "memory/events/entities.ndjson"
        stored = json.loads(stream.read_text())
        stored["payload"]["set"]["title"] = "Forged"
        request = {key: stored[key] for key in registry.REQUEST_FIELDS if key in stored}
        stored["request_hash"] = registry.sha256_json(request)
        stored["principal"]["request_hash"] = stored["request_hash"]
        stored["event_hash"] = registry.event_hash(stored)
        stream.write_text(registry.canonical_json(stored) + "\n")
        with self.assertRaisesRegex(registry.RegistryError, "authority signature mismatch"):
            registry.load_state(self.root, "entities")

    def test_canonical_replay_requires_host_verification_key(self):
        registry.append_event(self.root, "entities", event("entities", "signed-offline"))
        os.environ.pop(registry.HOST_KEY_ENV, None)
        with self.assertRaisesRegex(registry.RegistryError, "authority key"):
            registry.load_state(self.root, "entities")
        os.environ[registry.HOST_KEY_ENV] = self.host_key

    def test_hash_chain_detects_tampering(self):
        registry.append_event(self.root, "narrative", event("narrative", "canon-1"))
        stream = self.root / "memory/events/narrative.ndjson"
        stream.write_text(stream.read_text().replace("Fixture", "Tampered"))
        with self.assertRaisesRegex(registry.RegistryError, "bound to the request|hash mismatch"):
            registry.load_state(self.root, "narrative")

    def test_truncated_stream_fails_closed(self):
        registry.append_event(self.root, "narrative", event("narrative", "canon-valid"))
        stream = self.root / "memory/events/narrative.ndjson"
        with stream.open("a", encoding="utf-8") as handle:
            handle.write('{"registry":"narrative"')
        with self.assertRaisesRegex(registry.RegistryError, "invalid JSON"):
            registry.load_state(self.root, "narrative")

    def test_invalid_utf8_stream_fails_as_registry_error(self):
        registry.append_event(self.root, "narrative", event("narrative", "utf8-base"))
        stream = self.root / "memory/events/narrative.ndjson"
        stream.write_bytes(b"\xff\n")
        with self.assertRaisesRegex(registry.RegistryError, "valid UTF-8"):
            registry.load_state(self.root, "narrative")

    def test_overlong_event_line_is_rejected_by_bounded_read(self):
        registry.append_event(self.root, "narrative", event("narrative", "line-base"))
        stream = self.root / "memory/events/narrative.ndjson"
        stream.write_bytes(b"x" * (registry.MAX_EVENT_BYTES + 1))
        with self.assertRaisesRegex(registry.RegistryError, "exceeds size limit"):
            registry.load_state(self.root, "narrative")

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_symlinked_runtime_root_is_rejected(self):
        real_root = self.root / "real-project"
        real_root.mkdir()
        alias = self.root / "project-alias"
        alias.symlink_to(real_root, target_is_directory=True)
        with self.assertRaisesRegex(registry.RegistryError, "root cannot be a symlink"):
            registry.append_event(alias, "entities", event("entities", "alias-write"))

        safe_root = self.root / "safe-project"
        safe_root.mkdir()
        external_memory = self.root / "external-memory"
        external_memory.mkdir()
        (safe_root / "memory").symlink_to(external_memory, target_is_directory=True)
        with self.assertRaisesRegex(registry.RegistryError, "runtime path cannot be a symlink"):
            registry.append_event(safe_root, "entities", event("entities", "memory-alias"))

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_broken_root_symlink_is_rejected_without_creating_target(self):
        missing_target = self.root / "missing-project"
        alias = self.root / "broken-project-alias"
        alias.symlink_to(missing_target, target_is_directory=True)
        proposal = event(
            "entities", "broken-alias-proposal", operation="propose",
            proposed_operation="upsert",
            actor={"type": "skill", "id": "content-writer"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "root cannot be a symlink"):
            registry.append_event(alias, "entities", proposal)
        self.assertFalse(missing_target.exists())

    def test_read_only_get_does_not_create_or_chmod_runtime_paths(self):
        self.assertIsNone(registry.get_record(self.root, "entities", "missing-record"))
        self.assertFalse((self.root / "memory").exists())

        registry.append_event(self.root, "entities", event("entities", "readonly-base"))
        paths_and_modes = {
            self.root / "memory": 0o755,
            self.root / "memory/events": 0o751,
            self.root / "memory/projections": 0o750,
            self.root / "memory/events/entities.ndjson": 0o640,
        }
        for path, mode in paths_and_modes.items():
            path.chmod(mode)
        self.assertIsNotNone(registry.get_record(self.root, "entities", "record-1"))
        for path, mode in paths_and_modes.items():
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), mode)

    def test_inaccessible_suppression_path_fails_closed_in_library(self):
        target = self.root / "memory/events"
        original_lstat = registry.os.lstat

        def deny_events(path, *args, **kwargs):
            candidate = Path(path)
            if candidate.name == target.name and candidate.parent.name == target.parent.name:
                raise PermissionError("simulated inaccessible consent history")
            return original_lstat(path, *args, **kwargs)

        (self.root / "memory").mkdir()
        with mock.patch.object(registry.os, "lstat", side_effect=deny_events):
            with self.assertRaisesRegex(registry.RegistryError, "cannot inspect runtime path"):
                registry.is_suppressed(self.root, "sha256-inaccessible")

    @unittest.skipUnless(os.name == "posix", "POSIX permissions required")
    def test_inaccessible_suppression_path_fails_closed_in_cli(self):
        subject = "sha256-cli-inaccessible"
        registry.append_event(
            self.root, "consent",
            event(
                "consent", "cli-inaccessible-base", aggregate_id=subject,
                operation="suppress", payload={"reason": "unsubscribe"},
            ),
        )
        memory = self.root / "memory"
        memory.chmod(0)
        try:
            completed = subprocess.run(
                [sys.executable, str(ROOT / "scripts/registry-events.py"),
                 "--root", str(self.root), "is-suppressed", subject],
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                check=False, env=os.environ.copy(),
            )
        finally:
            memory.chmod(0o700)
        self.assertEqual(completed.returncode, 1)
        self.assertNotIn('"suppressed": false', completed.stdout.lower())
        self.assertRegex(completed.stderr, "cannot inspect|permission denied|cannot open")

    @unittest.skipUnless(hasattr(os, "link"), "hard links are unavailable")
    def test_hardlinked_event_stream_is_rejected_before_append(self):
        events_dir = self.root / "memory/events"
        projections_dir = self.root / "memory/projections"
        events_dir.mkdir(parents=True)
        projections_dir.mkdir(parents=True)
        outside = self.root / "outside.ndjson"
        outside.write_text("")
        os.link(outside, events_dir / "entities.ndjson")
        proposal = event(
            "entities", "hardlink-proposal", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "exactly one hard link"):
            self.raw_append_event(self.root, "entities", proposal)
        self.assertEqual(outside.read_text(), "")

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO creation is unavailable")
    def test_non_regular_event_stream_is_rejected(self):
        events_dir = self.root / "memory/events"
        projections_dir = self.root / "memory/projections"
        events_dir.mkdir(parents=True)
        projections_dir.mkdir(parents=True)
        os.mkfifo(events_dir / "entities.ndjson", 0o600)
        proposal = event(
            "entities", "fifo-proposal", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "regular file"):
            self.raw_append_event(self.root, "entities", proposal)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_open_stream_stays_dirfd_anchored_if_parent_is_swapped(self):
        proposal = event(
            "entities", "parent-swap-base", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        self.raw_append_event(self.root, "entities", proposal)
        resolved_root = self.root.resolve()
        events = resolved_root / "memory/events"
        original_events = resolved_root / "memory/events-original"
        outside = resolved_root / "outside-events"
        outside.mkdir()
        stream = events / "entities.ndjson"
        try:
            with self.assertRaisesRegex(registry.RegistryError, "directory changed"):
                with registry.locked_stream(stream, exclusive=True) as handle:
                    events.rename(original_events)
                    events.symlink_to(outside, target_is_directory=True)
                    handle.seek(0, os.SEEK_END)
                    handle.write("parent-fd-remained-anchored\n")
                    handle.flush()
            self.assertFalse((outside / "entities.ndjson").exists())
        finally:
            if events.is_symlink():
                events.unlink()
            if original_events.exists():
                original_events.rename(events)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks are unavailable")
    def test_intermediate_parent_swap_before_stream_open_cannot_escape(self):
        proposal = event(
            "entities", "pre-open-parent-swap", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        original_memory_paths = registry.memory_paths
        outside = self.root / "outside-memory"
        (outside / "events").mkdir(parents=True)
        (outside / "projections").mkdir()
        moved = self.root / "memory-original"
        swapped = False

        def swap_after_creation(*args, **kwargs):
            nonlocal swapped
            paths = original_memory_paths(*args, **kwargs)
            if kwargs.get("create") and not swapped:
                (self.root / "memory").rename(moved)
                (self.root / "memory").symlink_to(outside, target_is_directory=True)
                swapped = True
            return paths

        try:
            with mock.patch.object(registry, "memory_paths", side_effect=swap_after_creation):
                with self.assertRaisesRegex(registry.RegistryError, "cannot open runtime directory"):
                    self.raw_append_event(self.root, "entities", proposal)
            self.assertFalse((outside / "events/entities.ndjson").exists())
        finally:
            memory = self.root / "memory"
            if memory.is_symlink():
                memory.unlink()
            if moved.exists():
                moved.rename(memory)

    @unittest.skipUnless(shutil.which("git"), "git is unavailable")
    def test_git_worktree_writes_require_ignored_memory_and_fail_closed(self):
        git_root = self.root / "git-project"
        git_root.mkdir()
        subprocess.run(
            ["git", "init", "--quiet", str(git_root)], check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        proposal = event(
            "entities", "git-ignore-proposal", operation="propose",
            proposed_operation="upsert",
            actor={"type": "skill", "id": "content-writer"},
        )
        with self.assertRaisesRegex(registry.RegistryError, "not Git-ignored"):
            registry.append_event(git_root, "entities", proposal)
        self.assertFalse((git_root / "memory").exists())

        (git_root / ".gitignore").write_text(
            "memory/events/entities.ndjson\n"
            "memory/events/entities.ndjson.lock\n"
            "memory/projections/entities.json\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(registry.RegistryError, "registry-tmp.*not ignored"):
            registry.append_event(git_root, "entities", proposal)
        self.assertFalse((git_root / "memory").exists())

        (git_root / ".gitignore").write_text("memory/**\n", encoding="utf-8")
        result = registry.append_event(git_root, "entities", proposal)
        self.assertEqual(result["event"]["offset"], 1)

    def test_fcntl_less_lock_fallback_remains_dirfd_anchored(self):
        proposal = event(
            "entities", "portable-proposal", operation="propose",
            proposed_operation="upsert",
            actor={"type": "skill", "id": "content-writer"},
        )
        with mock.patch.object(registry, "fcntl", None):
            result = registry.append_event(self.root, "entities", proposal)
            state = registry.load_state(self.root, "entities")
        self.assertEqual(result["event"]["offset"], 1)
        self.assertEqual(state["last_offset"], 1)
        self.assertFalse((self.root / "memory/events/entities.ndjson.lock").exists())

    def test_fcntl_less_projection_installs_only_while_writer_lock_is_held(self):
        proposal = event(
            "entities", "portable-project-base", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        self.raw_append_event(self.root, "entities", proposal)
        lock = self.root / "memory/events/entities.ndjson.lock"
        original_write = registry.write_projections
        observed = []

        def assert_locked(*args, **kwargs):
            observed.append(lock.exists())
            return original_write(*args, **kwargs)

        with mock.patch.object(registry, "fcntl", None), mock.patch.object(
                registry, "write_projections", side_effect=assert_locked):
            state = registry.rebuild_projection(self.root, "entities")
        self.assertEqual(state["last_offset"], 1)
        self.assertEqual(observed, [True])
        self.assertFalse(lock.exists())

    def test_platform_without_safe_dirfd_mutation_fails_before_creating_memory(self):
        proposal = event(
            "entities", "unsafe-platform", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        with mock.patch.object(
                registry, "_safe_mutation_dirfd_available", return_value=False):
            with self.assertRaisesRegex(registry.RegistryError, "unsupported on this platform"):
                self.raw_append_event(self.root, "entities", proposal)
        self.assertFalse((self.root / "memory").exists())

    def test_platform_without_fchmod_fails_before_creating_memory(self):
        proposal = event(
            "entities", "unsafe-permissions", operation="propose",
            proposed_operation="upsert", actor={"type": "skill", "id": "producer"},
        )
        with mock.patch.object(registry.os, "fchmod", None):
            with self.assertRaisesRegex(registry.RegistryError, "unsupported on this platform"):
                self.raw_append_event(self.root, "entities", proposal)
        self.assertFalse((self.root / "memory").exists())

    def test_projection_can_be_rebuilt(self):
        registry.append_event(self.root, "creators", event("creators", "creator-1"))
        projection = self.root / "memory/projections/creators.json"
        projection.unlink()
        state = registry.rebuild_projection(self.root, "creators")
        self.assertEqual(state["last_offset"], 1)
        self.assertTrue(projection.exists())

    def test_pending_report_empty_root_is_quiet_and_creates_nothing(self):
        report = registry.pending_report(self.root)
        self.assertEqual(report["total_pending"], 0)
        self.assertEqual(set(report["registries"]), registry.REGISTRIES)
        self.assertTrue(all(e["verifiable"] for e in report["registries"].values()))
        self.assertTrue(all(
            e["projection_status"] == "not-required"
            for e in report["registries"].values()
        ))
        self.assertFalse((self.root / "memory").exists())

    def test_pending_report_counts_and_ages_proposals(self):
        old = event(
            "entities", "pending-old", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            occurred_at="2026-07-01T00:00:00Z",
        )
        registry.append_event(self.root, "entities", old)
        recent = event(
            "claims", "pending-recent", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            occurred_at="2026-07-09T00:00:00Z",
        )
        registry.append_event(self.root, "claims", recent)
        now = dt.datetime(2026, 7, 18, tzinfo=dt.timezone.utc)
        report = registry.pending_report(self.root, now=now)
        self.assertEqual(report["total_pending"], 2)
        entities = report["registries"]["entities"]
        self.assertEqual(entities["pending"], 1)
        self.assertEqual(entities["oldest_pending_age_days"], 17)
        self.assertEqual(entities["projection_lag"], 0)
        self.assertEqual(entities["projection_status"], "current")
        self.assertEqual(report["registries"]["claims"]["oldest_pending_age_days"], 9)

    def test_pending_report_orders_timezone_offsets_chronologically(self):
        first_instant = event(
            "entities", "pending-offset-first", aggregate_id="record-first",
            operation="propose", proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            occurred_at="2026-07-10T00:30:00+14:00",
        )
        later_instant = event(
            "entities", "pending-offset-later", aggregate_id="record-later",
            operation="propose", proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
            occurred_at="2026-07-09T23:45:00-12:00",
        )
        registry.append_event(self.root, "entities", first_instant)
        registry.append_event(self.root, "entities", later_instant)
        report = registry.pending_report(
            self.root, now=dt.datetime(2026, 7, 12, tzinfo=dt.timezone.utc),
        )
        entities = report["registries"]["entities"]
        self.assertEqual(
            entities["oldest_pending_occurred_at"],
            "2026-07-10T00:30:00+14:00",
        )
        self.assertEqual(entities["oldest_pending_age_days"], 2)

    def test_pending_report_resolved_proposal_drops_out(self):
        proposal = event(
            "entities", "pending-resolved", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
        )
        first = registry.append_event(self.root, "entities", proposal)
        accept = event(
            "entities", "accept-resolved", operation="accept", payload={},
            proposal_event_id=first["event"]["event_id"],
        )
        registry.append_event(self.root, "entities", accept)
        report = registry.pending_report(self.root)
        self.assertEqual(report["registries"]["entities"]["pending"], 0)
        self.assertEqual(report["total_pending"], 0)

    def test_pending_report_detects_projection_lag(self):
        registry.append_event(self.root, "creators", event("creators", "lag-1", aggregate_id="record-1"))
        registry.append_event(self.root, "creators", event("creators", "lag-2", aggregate_id="record-2"))
        projection_path = self.root / "memory/projections/creators.json"
        stored = json.loads(projection_path.read_text(encoding="utf-8"))
        stored["last_offset"] = 1
        projection_path.write_text(json.dumps(stored), encoding="utf-8")
        report = registry.pending_report(self.root)
        creators = report["registries"]["creators"]
        self.assertEqual(creators["stream_offset"], 2)
        self.assertEqual(creators["projection_offset"], 1)
        self.assertEqual(creators["projection_lag"], 1)
        self.assertEqual(creators["projection_status"], "behind")

    def test_pending_report_marks_missing_projection_for_nonempty_stream(self):
        registry.append_event(self.root, "creators", event("creators", "missing-projection"))
        projection_path = self.root / "memory/projections/creators.json"
        projection_path.unlink()
        creators = registry.pending_report(self.root)["registries"]["creators"]
        self.assertEqual(creators["projection_status"], "missing")
        self.assertIsNone(creators["projection_offset"])
        self.assertIsNone(creators["projection_lag"])

    def test_pending_report_marks_invalid_projection(self):
        registry.append_event(self.root, "creators", event("creators", "invalid-projection"))
        projection_path = self.root / "memory/projections/creators.json"
        projection_path.write_text("{not-json", encoding="utf-8")
        creators = registry.pending_report(self.root)["registries"]["creators"]
        self.assertEqual(creators["projection_status"], "invalid")
        self.assertIn("projection_error", creators)
        self.assertIsNone(creators["projection_lag"])

    def test_pending_report_marks_non_utf8_projection_invalid(self):
        registry.append_event(self.root, "creators", event("creators", "binary-projection"))
        projection_path = self.root / "memory/projections/creators.json"
        projection_path.write_bytes(b"\xff")
        creators = registry.pending_report(self.root)["registries"]["creators"]
        self.assertEqual(creators["projection_status"], "invalid")
        self.assertIn("projection_error", creators)

    def test_pending_report_marks_projection_ahead_without_negative_lag(self):
        registry.append_event(self.root, "creators", event("creators", "ahead-projection"))
        projection_path = self.root / "memory/projections/creators.json"
        stored = json.loads(projection_path.read_text(encoding="utf-8"))
        stored["last_offset"] = 2
        projection_path.write_text(json.dumps(stored), encoding="utf-8")
        creators = registry.pending_report(self.root)["registries"]["creators"]
        self.assertEqual(creators["projection_status"], "ahead")
        self.assertEqual(creators["projection_offset"], 2)
        self.assertIsNone(creators["projection_lag"])

    def test_pending_report_marks_unverifiable_stream(self):
        registry.append_event(self.root, "creators", event("creators", "signed-1"))
        stream_path, _, _ = registry.memory_paths(self.root, "creators")
        with stream_path.open("a", encoding="utf-8") as handle:
            handle.write("not-json\n")
        report = registry.pending_report(self.root)
        creators = report["registries"]["creators"]
        self.assertFalse(creators["verifiable"])
        self.assertEqual(creators["projection_status"], "unknown")
        self.assertIn("error", creators)
        self.assertEqual(report["registries"]["entities"]["pending"], 0)

    def test_pending_report_without_host_key_uses_labeled_advisory_read(self):
        proposal = event(
            "entities", "pending-advisory", operation="propose",
            proposed_operation="upsert", expected_revision=0,
            actor={"type": "skill", "id": "content-writer"},
        )
        first = registry.append_event(self.root, "entities", proposal)
        accept = event(
            "entities", "accept-advisory", operation="accept", payload={},
            proposal_event_id=first["event"]["event_id"],
        )
        registry.append_event(self.root, "entities", accept)
        registry.append_event(
            self.root, "entities",
            event("entities", "pending-advisory-2", operation="propose",
                  proposed_operation="upsert", expected_revision=0,
                  aggregate_id="record-2",
                  actor={"type": "skill", "id": "content-writer"}))
        os.environ.pop(registry.HOST_KEY_ENV, None)
        report = registry.pending_report(self.root)
        entities = report["registries"]["entities"]
        self.assertTrue(entities["verifiable"])
        self.assertFalse(entities["authority_verified"])
        self.assertEqual(entities["pending"], 1)
        os.environ[registry.HOST_KEY_ENV] = self.host_key
        strict = registry.pending_report(self.root)
        self.assertTrue(strict["registries"]["entities"]["authority_verified"])
        self.assertEqual(strict["registries"]["entities"]["pending"], 1)


if __name__ == "__main__":
    unittest.main()
