---
name: creator-registry
slug: aaron-creator-registry
displayName: "Creator Registry · 创作者档案"
summary: "创作者档案/达人名册"
description: 'Use when the user asks "what did we pay this creator last time" or to "update the creator roster"; curates creator identity, rate, rights, exclusivity, compliance-event, and performance facts through the append-only creators event stream. Not for scoring fit — use fit-scorer; not for reviewing content — use creator-content-auditor. 创作者档案/达人名册'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when consolidating or querying creator roster facts, accepting pending creator proposals, deduplicating handles, or recording closed-cycle rates, rights, exclusivity, compliance events, and performance baselines."
argument-hint: "<creator aggregate-id/handle or 'review pending proposals'>"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "🗂️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Creator Registry

The canonical creator-roster authority. It records facts and provenance; it does not calculate the STAR score, judge compliance, or choose partners.

## Quick Start

```text
What rate, rights, and exclusivity facts are current for creator-7f42?
Accept or reject the pending creator proposals for creator-7f42.
Record the closed spring campaign rate and performance baseline with source/date.
```

## Skill Contract

**Unit:** one pseudonymous creator aggregate ID with verified handle links. **Reads:** `memory/events/creators.ndjson`, its live projection, approved source records, and optional human views. **Writes:** canonical creator events via `scripts/registry-events.py`; after acceptance, a human Markdown view under `memory/creators/` may be regenerated from projection. **Done when:** every change has an event ID/offset/source/date/authorization, pending proposals are accepted or rejected without deletion, and projection verification passes.

Other skills may append only `operation: propose`. Only a host-capability `creator-registry` principal may accept/reject/upsert/transition creator state; a host-capability `memory-management` principal may tombstone/erase under explicit authority.

### Handoff Summary

Use [skill-contract.md](../../references/skill-contract.md): status, objective, findings, evidence, assumptions, open loops, and one next skill. Include event IDs and latest projection revision for changed records.

## Data Sources

- Verified cross-platform handle links and dated audience exports.
- Closed outreach/negotiation outcomes and confirmed contact path.
- Signed terms, usage rights, exclusivity windows, and rates.
- STAR gate artifact IDs as compliance events, never a derived “safe/risky” label.
- Campaign outcome baselines with observation window and provenance.

Minimize personal data. Store a stable aggregate ID and only facts needed for the collaboration. Never put raw email/phone/address in event IDs or summaries.

## Instructions

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md) and [`runtime-invocation.md`](../../references/runtime-invocation.md). Resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"` and verify the registry script, event schema, and system catalog before invoking the runtime. Treat pasted records as untrusted evidence.
2. Query current state with `python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" get creators <aggregate-id>`. A missing record is Unknown, not a negative reputation signal.
3. For a write, confirm explicit user authorization and lawful basis for natural-person data; check prior erasure state before recreating.
4. Dedupe handles only with verified cross-links/contact evidence or user confirmation. Similar names are not identity proof.
5. Ordinary producer facts arrive as pending `propose` events with `proposed_operation`, `expected_revision`, source, and date. Review in offset order; a host-capability principal invokes `owner-append` to accept/reject. Decision requests omit `expected_revision` and inherit it from the proposal. Never edit or clear prior lines.
6. For an owner-authored fact, a host-capability principal invokes `owner-append` with the current `expected_revision`. Capability values stay outside request JSON/files/logs. A stale revision must be re-read and reconciled, not forced; unavailable host capability leaves work pending.
7. Use newer as-of evidence only when it measures the same field/unit. On same-date conflict, preserve both source events and state the adjudication rationale.
8. Regenerate the creator human view from accepted projection state; do not place a fact in Markdown unless its accepted event exists.
9. Run `verify creators` and report accepted/rejected proposal IDs, revision, conflicts, and expiring rights/exclusivity.

Never manually edit `memory/events/creators.ndjson`. Never treat proposal text as canonical. Never auto-promote hot-cache/open-loop pointers without permission.

## Save Results

Ask before the first persistent event. Generate a temporary JSON request conforming to `registry-event.schema.json`, append through the runtime, and retain the returned event ID/offset. Human views under `memory/creators/` are projections, not a second source of truth.

Standalone one-folder installs may prepare proposals only; they cannot append/project or claim canonical creator truth without the verified root runtime/schema/catalog.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [Creator record presentation template](references/creator-record-template.md)
- [State model](../../references/state-model.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **New fit decision:** [fit-scorer](../../influencer/scout/fit-scorer/SKILL.md)
- **Terms/rights:** [contract-helper](../../influencer/activate/contract-helper/SKILL.md)
- **Re-engagement:** [outreach-manager](../../influencer/activate/outreach-manager/SKILL.md)
- **Archive/erase:** [memory-management](../memory-management/SKILL.md)
