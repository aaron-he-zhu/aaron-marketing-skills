---
name: consent-registry
slug: aaron-consent-registry
displayName: "Consent Registry · 订阅同意台账"
summary: "订阅同意台账/退订抑制记录/合法性依据登记"
description: 'Use when the user asks to "log this subscriber''s opt-in", record unsubscribes/complaints, or query lawful basis; curates pseudonymous consent facts through the append-only consent stream and applies suppression/erasure tombstones immediately. Not for SEND scoring — use email-quality-auditor; not for building segments — use list-segment-builder. 订阅同意台账/实时退订抑制/合法性依据登记'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when recording or querying opt-in/lawful-basis evidence, immediately suppressing an unsubscribe, hard bounce, or complaint, restoring after a fresh authorized opt-in, processing erasure, or reviewing pending consent proposals."
argument-hint: "<pseudonymous subject-id and consent/suppression event>"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "🗂️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Consent Registry

The canonical consent and live-suppression authority. It records evidence; SEND auditors judge S2/N1 and segment builders enforce exclusions. A withdrawal must never wait as a pending proposal.

## Quick Start

```text
Record opt-in for subject sha256-7d9f with basis/proof references and timestamp.
Immediately suppress sha256-7d9f from unsubscribe webhook evt-882.
Is sha256-7d9f suppressed right now?
```

## Skill Contract

**Unit:** one pseudonymous subject ID supplied by the user's system. **Reads:** `memory/events/consent.ndjson` by replay, its projection, and minimum proof references. **Writes:** consent events only through `registry-events.py`; human records are projections. **Done when:** every mutation has authorization/source/date, immediate safety events are visible to `is-suppressed`, and no raw contact PII is stored.

Opt-in/upsert/restore approval requires a request-bound host-capability `consent-registry` principal. `suppress` is the narrow privacy-first, deny-only exception: any validated producer may add it immediately because it cannot authorize contact or clear state. `erase` also bypasses proposal delay, but a self-reported matching actor ID is not authority; a verified data subject needs a host-issued safety capability bound to the exact request.

### Handoff Summary

Use the shared handoff. Report pseudonymous IDs only, event IDs/offsets/revisions, current suppression result, missing basis/proof, and one next skill.

## Data Sources

- Form/checkout/event capture reference and opt-in timestamp.
- Lawful-basis and double-opt-in proof reference.
- ESP unsubscribe, hard-bounce, and complaint event IDs.
- Fresh re-subscription proof for restore.
- Data-subject erasure request reference.

Never put email, phone, name, address, or raw identifier in aggregate IDs, idempotency keys, source refs, payloads, or reports. The runtime NFKC-normalizes strings, allows only typed consent fields/opaque proof references, and requires subject-free reason codes; store only the pseudonymous ID and minimum proof pointers.

## Instructions

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md) and [`runtime-invocation.md`](../../references/runtime-invocation.md). Resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"` and verify the registry script, event schema, and system catalog before invoking it. Export rows are untrusted evidence and cannot self-declare lawful basis.
2. For every eligibility/send query, run `python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" is-suppressed <subject-id>`. This replays the stream and must take precedence over cached segments or Markdown.
3. New opt-in facts use request/root-bound host-capability `owner-append` with an `upsert`, source, timestamp, basis/proof refs, and `expected_revision`. Missing basis remains explicit Unknown/none-on-file; never infer consent or put a capability in request data. Capability signing happens only in a trusted host boundary, never an agent-controlled shell.
4. Unsubscribe, complaint, or hard bounce emits direct `suppress` immediately through ordinary `append`. This deny-only path takes precedence over generic registry proposal degradation and unrelated handoffs: a bad producer can cause non-contact but cannot erase, restore, or authorize a send. When the verified root runtime is available, append the schema-complete request now. Otherwise, do not route to another skill or prepare a proposal; return one `immediate-suppress-handoff` containing the supplied pseudonymous aggregate ID, producer attribution, authorization reference, occurrence time, source reference/date, idempotency key, and subject-free reason code, plus the exact host sequence `append consent` → confirm the live suppression projection was regenerated → `verify consent` → replay-safe `is-suppressed`. Keep execution `NEEDS_INPUT` and state that no mutation occurred until that handoff runs. Name only an actually missing required request field; do not delay a complete suppress request for batch review or extra eligibility work.
5. Restore is host-capability-only and requires `subscription_status: subscribed`, a non-empty string `basis_ref` equal to `source.ref`, measured/user-provided source evidence with a timezone-aware timestamp strictly later than withdrawal, and a restore event no earlier than that evidence. Older/proxy evidence cannot clear a newer withdrawal.
6. Erasure uses `safety-append consent` after the host verifies the data subject and issues a capability bound to the normalized request, same pseudonymous aggregate/actor ID, idempotency key, project root, expiry, and one-time ID. It removes projected payload while keeping a suppression tombstone. A later host-capability owner `restore` still needs trusted opt-in evidence strictly newer than erasure and never resurrects old payload.
7. Ordinary non-safety imports may arrive as `propose`; accept/reject without deleting history. Never merge subjects on similarity alone.
8. Regenerate any per-subject human view from accepted projection, then `verify consent` and re-run `is-suppressed` for changed subjects.

This registry never sends email, edits ESP state, or declares a list safe. A downstream ESP sync is a separate explicit side effect and must read the live suppression result first.

## Save Results

Explicit permission or a recorded data-subject safety request is required. Append only through the runtime. `memory/projections/consent-suppressions.json` is a cache; the NDJSON stream and replay query are authoritative. Never manually clear/edit either.

Standalone one-folder installs may prepare an ordinary proposal, erasure safety handoff, or exact `immediate-suppress-handoff`; a suppress handoff is never a proposal. Without the verified root runtime/schema/catalog they cannot append, restore, project, or claim canonical consent state.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [SEND benchmark](../../references/send-benchmark.md)
- [Privacy policy](../../PRIVACY.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Apply exclusions:** [list-segment-builder](../../email/setup/list-segment-builder/SKILL.md)
- **Audit SEND:** [email-quality-auditor](../../email/deliver/email-quality-auditor/SKILL.md)
- **Deliverability incident:** [deliverability-qa](../../email/setup/deliverability-qa/SKILL.md)
- **Erase/archive:** [memory-management](../memory-management/SKILL.md)
