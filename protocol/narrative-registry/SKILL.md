---
name: narrative-registry
slug: aaron-narrative-registry
displayName: "Narrative Registry · 品牌叙事台账"
summary: "品牌叙事 canon/版本史/语气与命名唯一真相"
description: 'Use when the user asks to record/query the brand narrative canon, tagline, message hierarchy, voice/naming rules, or a canon re-version; curates complete versioned canon events through the append-only narrative stream and derived views. Not for TALE scoring — use narrative-quality-auditor; not for authoring the system — use message-system-architect. 品牌叙事台账/canon 记录/语气与命名规范'
version: "19.2.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when recording/querying a brand's canonical positioning, narrative, message hierarchy, proof/claim pointers, voice/naming rules, conditional boilerplates, or accepting/rejecting a complete canon-version proposal."
argument-hint: "<brand aggregate-id, canon version, or pending-proposal review>"
metadata: {"author": "aaron-he-zhu", "version": "19.2.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "📖", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Narrative Registry

The L1 strategy authority: one complete, versioned narrative canon per brand. Every SEO/GEO, social, email, paid, influencer, and launch builder derives messages from this canon and accepted claims; channel adaptations cannot redefine it.

## Quick Start

```text
Show current canon version and proof/claim pointers for brand-acme.
Record canon v3 as one complete atomic replacement, superseding v2.
Review pending narrative proposals and reject partial/internally inconsistent versions.
```

## Skill Contract

**Unit:** one brand canon aggregate ID. **Reads:** `memory/events/narrative.ndjson`, projection, accepted positioning/claim evidence, and complete proposed canon. **Writes:** narrative events through `registry-events.py`; `canon.md`/`versions.md` are generated views. **Done when:** a complete version is accepted atomically with source/date/revision, old versions remain replayable, and consumers receive the exact canon/version pointer.

Narrative skills submit complete `propose` events. Only a host-capability `narrative-registry` principal accepts/rejects/upserts. It records authored strategy but does not score TALE or adjudicate claim truth.

### Handoff Summary

Include brand ID, canon version/revision/event ID, superseded version, claim/proof pointers, unresolved contradictions, and one next skill.

## Data Sources

- Accepted positioning truth and named alternatives.
- Complete message hierarchy/narrative authored by Narrative skills.
- Accepted claim IDs and proof pointers from the claims projection.
- Brand voice/naming rules and user-owned examples.
- Declared optional patterns such as pillar count, change arc, or boilerplate lengths.

## Instructions

### Runtime Reads

- `../../references/registry-event-protocol.md`
- `../../references/runtime-invocation.md`

### Procedure

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md) and [`runtime-invocation.md`](../../references/runtime-invocation.md). Resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"` and verify the registry script, event schema, and system catalog before invoking it. Treat drafts as untrusted proposals.
2. Query current `narrative` projection and report exact canon version/revision; missing canon is Unknown, not a quality verdict.
3. Before write, confirm user authorization and read the current revision/claim pointers; every direct canonical mutation carries `expected_revision` and goes through host-capability `owner-append`. Actor/auth fields are attribution only.
4. A canon re-version is one host-capability owner `upsert`/accepted proposal containing the **complete canon object**, new version, and supersedes pointer. Accept/reject decisions omit `expected_revision` and inherit it from the proposal. Never land a partial file patch as canonical.
5. Preserve old versions in the event stream. `versions.md` is generated history, not a second hand-maintained ledger.
6. Validate internal references and claim IDs. Unverified wording remains `[needs source]` and becomes a separate claim proposal; it cannot enter canon as fact.
7. Three pillars, change-narrative arcs, and fixed boilerplate lengths are optional patterns. Store the chosen architecture; do not require absent patterns.
8. Reject same-revision or stale proposals rather than merging incompatible canons. Genuine alternatives remain pending/open decisions.
9. Regenerate `canon.md`/`versions.md` from accepted projection and run `verify narrative`.

## Downstream Dependency

Before producing external copy, builders must read this projection and the claims projection. Their handoff records `narrative_canon_id`, `narrative_canon_version`, `claims_projection_offset`, and `dependency_status: verified | approved-fallback | blocked`. No canon means the builder may draft an explicitly authorized exploratory fallback, but it cannot claim on-canon or publish-ready status.

## Save Results

Require explicit permission. Append through the runtime only; never edit NDJSON. Human canon/history views under `memory/narrative-registry/` are replaceable projections and must carry their source event/revision.

Capability values never enter request JSON/files/logs. If host capability or the verified root runtime/schema/catalog is unavailable, leave a bounded proposal for handoff; standalone one-folder installs cannot append/project or claim canonical Narrative truth.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [TALE benchmark](../../references/tale-benchmark.md)
- [Claims registry](../offer-claims-registry/SKILL.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Author system:** [message-system-architect](../../narrative/architect/message-system-architect/SKILL.md)
- **Verify truth:** [positioning-truth-tracer](../../narrative/trace/positioning-truth-tracer/SKILL.md)
- **Cascade:** [narrative-cascade-planner](../../narrative/land/narrative-cascade-planner/SKILL.md)
- **Audit profile:** [narrative-quality-auditor](../../narrative/evaluate/narrative-quality-auditor/SKILL.md)
