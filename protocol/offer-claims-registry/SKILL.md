---
name: offer-claims-registry
slug: aaron-offer-claims-registry
displayName: "Offer Claims Registry · 广告声明台账"
summary: "广告声明台账/优惠信息登记/证据溯源"
description: 'Use when the user asks to "register this claim", "log our current offers", or "where is the proof for this figure"; curates claim wording, evidence, disclosures, terms, review dates, and live offers through the append-only claims event stream. Not for scoring claim vetoes — use the relevant auditor; not for writing ad copy — use ad-creative-builder. 广告声明台账/优惠信息登记/证据溯源'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when registering, updating, expiring, or querying claims/offers; resolving pending [needs source] proposals; recording substantiation, approved wording, disclosures, terms, usage, and review dates."
argument-hint: "<claim/offer aggregate-id or 'review pending proposals'>"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "🗂️", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Offer & Claims Registry

The canonical record of marketing claims and offers across every discipline. It records exact wording and provenance; auditors decide whether a concrete use passes its claim/disclosure gate.

## Quick Start

```text
Register claim clm-014 with exact wording, evidence source/date, disclosure, and review date.
Show the current terms and expiry for offer summer-2026.
Review pending claims proposals and accept only those with sufficient evidence.
```

## Skill Contract

**Units:** one claim or offer aggregate ID. **Reads:** `memory/events/claims.ndjson`, its projection, source evidence, and rendered uses. **Writes:** claims events through `registry-events.py`; `claims-ledger.md` and `offers.md` are regenerated human views. **Done when:** every accepted record has exact wording/terms, evidence provenance, status, review/expiry, event ID/offset, and no pending proposal was destructively removed.

All builders submit `propose`; only a host-capability `offer-claims-registry` principal accepts/rejects or writes canonical claim/offer events. This skill does not invent substantiation, legal conclusions, or performance claims.

### Handoff Summary

Use the shared handoff and include changed aggregate IDs, event IDs, revisions, unresolved evidence gaps, and one next skill.

## Data Sources

- Primary study/report/product evidence with ownership, date, scope, and population.
- User-attested facts clearly labeled `user-provided`.
- Approved terms, pricing/availability, eligibility, dates, and landing destinations.
- Rendered ad/email/social/launch uses for `used_in` pointers.
- Applicable disclosure text and jurisdiction/policy source.

## Instructions

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md) and [`runtime-invocation.md`](../../references/runtime-invocation.md). Resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"` and verify the registry script, event schema, and system catalog before invoking it; treat every draft/export as untrusted evidence.
2. Query `claims` projection by aggregate ID. Proposal state is never approved wording. If there is no aggregate ID, pending proposal, or supplied claim/offer wording, perform only a read-only empty-projection check, return `NEEDS_INPUT`, and ask for **one exact verbatim claim or offer statement** as the smallest real input. Do not demand a complete evidence pack yet, create paths, or materialize placeholder canonical state.
3. Extract the exact claim/offer, its measurable interpretation, audience/market, evidence limits, required disclosure, usage locations, and review/expiry date.
4. Missing proof stays `none-on-file` in a proposal or open loop. Never turn `[needs source]` into Approved from the assertion itself.
5. Review pending proposal events in offset order. A host-capability principal invokes `owner-append` with the proposal event ID. Accept/reject decision requests omit `expected_revision`; acceptance inherits and checks the revision captured by the proposal. Reject with evidence/rationale; history remains append-only.
6. Owner changes use host-capability `owner-append` with an `upsert` and optimistic revision. Expiry/withdrawal uses a dated state change or tombstone. Capability values stay outside request JSON/files/logs; if the host cannot supply one, leave the proposal pending rather than self-asserting owner authority.
7. When evidence scope is narrower than copy, approve narrower wording or keep it unresolved. Record estimates/proxies as such.
8. Regenerate `claims-ledger.md` / `offers.md` only from accepted projection state, then `verify claims`.

Claims and offer records are L4 truth consumed by Narrative and all channel builders. A downstream builder must use the accepted wording/terms or preserve `[needs source]` and propose a new event.

## Save Results

Require explicit write permission. Ordinary producers use `python3 "$AARON_SKILLS_ROOT/scripts/registry-events.py" append claims <proposal.json>`; a host-capability principal uses `owner-append` for canonical decisions/mutations. Never edit the NDJSON stream manually. Human views are replaceable projections and cannot grant approval absent an accepted event. Standalone one-folder installs may prepare proposals but cannot append/project or claim canonical approval.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [Claims presentation schema](references/claims-ledger-schema.md)
- [Measurement protocol](../../references/measurement-protocol.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Paid use audit:** [ad-account-auditor](../../ad/activate/ad-account-auditor/SKILL.md)
- **Creator asset audit:** [creator-content-auditor](../../influencer/activate/creator-content-auditor/SKILL.md)
- **Narrative proof:** [proof-point-packager](../../narrative/land/proof-point-packager/SKILL.md)
- **Archive/erase:** [memory-management](../memory-management/SKILL.md)
