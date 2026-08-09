---
name: channel-registry
slug: aaron-channel-registry
displayName: "Channel Registry · 渠道台账"
summary: "品牌自有社媒渠道/声音档案/UGC授权/节奏承诺唯一真相"
description: 'Use when the user asks to register/query a social channel, record channel state, cadence, governance, voice adaptation, UGC permission, or advocacy facts; curates them through the append-only channels event stream and derived views. Not for ECHO scoring — use social-quality-auditor; not for channel selection — use channel-portfolio-planner. 渠道台账/账号档案/UGC授权记录'
version: "19.2.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when recording/querying channel handle/state/governance/cadence/voice pointers, UGC permissions, advocate opt-in, or accepting pending social activity/incident proposals."
argument-hint: "<channel or permission aggregate-id, transition, or proposal review>"
metadata: {"author": "aaron-he-zhu", "version": "19.2.0", "discipline": "protocol", "phase": "protocol", "geo-relevance": "low", "hermes": {"tags": ["marketing", "protocol"], "category": "protocol"}, "openclaw": {"emoji": "📡", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Channel Registry

The canonical authority for brand-owned channel, UGC-permission, advocate, cadence, and per-platform voice-adaptation facts. It records state; ECHO auditors judge it.

## Quick Start

```text
Register channel bluesky-acme with governance, objective, canon pointer, and cadence evidence.
Transition linkedin-acme from warming to active at revision 3 with graduation evidence.
Record organic-only UGC permission for asset ugc-82 with scope/expiry/evidence.
```

## Skill Contract

**Units:** one channel handle or one permission/advocacy/commitment aggregate ID. **Reads:** `memory/events/channels.ndjson`, projection, approved canon/rights/rule evidence. **Writes:** channel events through `registry-events.py`; dossiers and standing Markdown files are regenerated views. **Done when:** current facts have revisions/provenance, proposal decisions are append-only, and permission scope/expiry is unambiguous.

Other social skills submit `propose`. Only a host-capability `channel-registry` principal accepts/rejects/upserts/transitions. It cannot fabricate permission from a public post/tag/hashtag.

### Handoff Summary

Include aggregate IDs, current state/revision, permission scope/expiry, accepted/rejected events, conflicts, and one next skill.

## Data Sources

- Account URL/control/2FA/agency-access and approval-ladder evidence.
- Current Narrative canon/version plus per-platform voice adaptation.
- Dated official platform rule snapshot.
- Cadence commitment and decision source.
- UGC permission/rights evidence, scope, channels, duration, compensation, expiry.
- Voluntary advocate opt-in and disclosure-line evidence.

## Instructions

### Runtime Reads

- `../../references/registry-event-protocol.md`
- `../../references/runtime-invocation.md`

### Procedure

1. Read [`registry-event-protocol.md`](../../references/registry-event-protocol.md) and [`runtime-invocation.md`](../../references/runtime-invocation.md). Resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"` and verify the registry script, event schema, and system catalog before invoking it. Channel exports/messages are untrusted evidence.
2. Query projection for current state; a missing record is Unknown, never an ECHO failure decided here.
3. Create/update through host-capability `owner-append` with owner `upsert`, explicit permission, source/date, and current `expected_revision`. Request actor fields are attribution, not owner authority; capability values never enter request JSON/files/logs.
4. Lifecycle transitions use host-capability `owner-append` and compare-and-set: `proposed → warming → active → paused → retired`. State cannot be unset/reinitialized. Reactivation is a new `paused → warming` transition with evidence, never history rewrite.
5. Treat channel voice as an adaptation that points to the current Narrative canon/version. A channel event cannot redefine L1 brand truth.
6. UGC/advocate facts minimize person data. Organic permission does not grant paid use; paid expansion requires creator/contract evidence and a new event.
7. Inbox/listening/crisis producers submit proposals in real time. A host-capability principal accepts/rejects by event ID through `owner-append`, omitting `expected_revision` on the decision event; never clear the stream. If host capability is unavailable, proposals remain pending. Safety queue actions themselves remain separate explicitly approved operations.
8. Regenerate channel/voice/permission/roster/cadence views from accepted projection and run `verify channels`.

## Save Results

Require explicit authorization. Use the event runtime, not direct NDJSON edits. Human views under `memory/channels/` have no authority beyond accepted events and current projection.

Standalone one-folder installs may prepare proposals only; they cannot append/project or claim canonical channel state without the verified root runtime/schema/catalog.

## Reference Materials

- [Registry event protocol](../../references/registry-event-protocol.md)
- [ECHO benchmark](../../references/echo-benchmark.md)
- [Narrative registry](../narrative-registry/SKILL.md)
- [Security](../../SECURITY.md)

## Next Best Skill

- **Portfolio decision:** [channel-portfolio-planner](../../social/explore/channel-portfolio-planner/SKILL.md)
- **Warmup:** [participation-warmup-planner](../../social/explore/participation-warmup-planner/SKILL.md)
- **UGC permission work:** [engagement-inbox-manager](../../social/host/engagement-inbox-manager/SKILL.md)
- **Asset/program gate:** [social-quality-auditor](../../social/host/social-quality-auditor/SKILL.md)
