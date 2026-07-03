---
name: outreach-manager
description: 'Use when the user asks to "write influencer outreach", "follow up with a creator", or "negotiate partnership terms"; produces personalized pitches, multi-touch follow-up sequences, negotiation scripts with objection handling, and a status pipeline tracker. Not for finalizing signed agreements — use contract-helper.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate the skill when the user wants to contact a creator, draft or personalize a pitch message, build a follow-up cadence for non-responders, re-engage a past partner, negotiate rate or scope, handle pricing objections, or track outreach status across a list of influencers."
argument-hint: "<influencer handle or list> [platform] [budget]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: activate
  family: influencer-marketing
  impact-phase: Activate
---

# Outreach Manager

Craft personal, professional, persistent influencer outreach; manage negotiations; track relationship progress.

## Quick Start

Shortest invocation:

```
Write an outreach message to @[influencer] for [campaign]
```

Negotiate a gap between ask and budget:

```
Help me negotiate with @[influencer] who is asking for $[X] when our budget is $[Y]
```

## Skill Contract

- **Reads**: target influencer handle(s), platform, follower count, niche; campaign and product context; compensation type and budget; deliverables and timeline; any prior contact history supplied by the user or loaded from memory. Before any outreach, check `memory/creators/<handle-slug>.md` — the [creator-registry](../../protocol/creator-registry/SKILL.md) roster record — for the confirmed contact path, last agreed rate, and negotiation/response history.
- **Writes**: outreach artifact (pitches, follow-up sequence, negotiation guide, pipeline tracker) to `memory/influencer/outreach-manager/YYYY-MM-DD-<topic>.md`. When a cycle closes, the closed outcome (final agreed rate, response history, confirmed contact path) goes as a one-line update to `memory/creators/candidates.md` — only `creator-registry` writes canonical roster records.
- **Promotes**: durable facts (confirmed partners, agreed rates, top objection patterns, response-rate baselines) to `memory/hot-cache.md`.
- **Done when**:
  - A personalized pitch (plus at least one variation) exists for each target influencer.
  - A follow-up cadence and pipeline status are recorded for every contacted creator.
  - Confirmed partners are flagged with agreed terms for handoff.
- **Primary next skill**: [content-reviewer](../../activate/content-reviewer/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill works entirely from inputs you provide — paste the influencer handles, follower counts, niche, budget, and deliverables, and it produces every artifact without any tool connection.

Where a connector could speed up the work, use these `~~` placeholders:

- `~~influencer database` — pull handle, follower count, niche, and past partnerships instead of typing them.
- `~~social platform analytics` — verify audience demographics and recent posts for personalization.
- `~~CRM` — sync pipeline status, last-contact dates, and next actions.
- `~~email/DM tool` — schedule and send the follow-up cadence.

See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category. No integration is required; when one is absent, ask the user for the inputs directly.

## Instructions

When a user requests outreach help, run these steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block and replace the placeholders. Apply the hard copy rules in [references/cold-copy-rules.md](references/cold-copy-rules.md) before any message ships.

1. **Gather outreach context** — capture campaign/product context, target handle(s), platform, followers, niche, compensation type, budget, deliverables, and timeline. Load the `memory/creators/<handle-slug>.md` roster record first when it exists — re-engaging a rostered creator starts from the confirmed contact path and last agreed rate, not a cold pitch. Template: [Step 1](references/templates.md#step-1--outreach-parameters).
2. **Create personalized outreach** — list personalization points (recent content, style, audience, values, past partners), then write the primary message plus a DM-friendly short version and a formal email/management version. Template: [Step 2](references/templates.md#step-2--personalized-outreach).
3. **Create follow-up sequence** — build a 4-touch cadence (Day 0 / 3-4 / 7-8 / 14, then archive at Day 21), each touch adding new value and getting shorter. Cap at 3-4 follow-ups; make it easy to say no. Template: [Step 3](references/templates.md#step-3--follow-up-sequence).
4. **Provide negotiation support** — map the ask/budget gap, then apply value-exchange, scope-adjustment, or future-value strategies with ready scripts and an objection/response table. Template: [Step 4](references/templates.md#step-4--negotiation-guide).
5. **Track outreach pipeline** — record stage counts and conversion rates, a per-creator detailed pipeline, today's prioritized actions, and pipeline health (response rate, confirmation rate, time-to-confirm, top objection). Template: [Step 5](references/templates.md#step-5--outreach-pipeline-tracker). Active-cycle tracking lives here; when a cycle closes (confirmed or archived), submit the closed outcome as a one-line update to `memory/creators/candidates.md` for [creator-registry](../../protocol/creator-registry/SKILL.md) to reconcile.

## Example

**User**: "Write outreach for @sustainablesarah (45K Instagram followers, eco-lifestyle) for our organic skincare launch"

**Output** (abridged):

```markdown
## Outreach for @sustainablesarah

### Personalization Points
- Recent post: "5 swaps for a zero-waste bathroom"  •  Style: educational, authentic  •  Past partners: Grove Collaborative

### Primary Message
Subject: Love your zero-waste content – collab with [Brand]?

Hi Sarah! I just watched your "zero-waste bathroom" post and added reusable cotton rounds to my cart 😊 I'm [Name] from [Brand] — organic skincare in fully compostable packaging. We're launching a new collection and thought of you. We'd love to send the full line, and if you love it, partner on a post + Stories. Offering $[X] plus product and full creative freedom. Interested?
```

Full multi-version output, follow-up cadence, negotiation guide, and pipeline tracker live in [references/templates.md](references/templates.md).

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for all five steps, the full worked example, and outreach tips.
- [references/cold-copy-rules.md](references/cold-copy-rules.md) — hard cold-outreach copy rules: first-line bans, per-step sentence caps, soft CTAs, observation framing, no link in step 1.
- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- C3 benchmark scoring at [references/c3/scoring-architecture.md](../../references/c3/scoring-architecture.md) — quality scoring reference for downstream review.
- [expert-panel.md](../../references/expert-panel.md) — multi-persona review method for pressure-testing outreach copy before sending.
- Sibling skills: [influencer-discovery](../../discover/influencer-discovery/SKILL.md), [fit-scorer](../../discover/fit-scorer/SKILL.md), [brief-generator](../../plan/brief-generator/SKILL.md), [contract-helper](../contract-helper/SKILL.md), [content-reviewer](../../activate/content-reviewer/SKILL.md).

## Next Best Skill

- **Primary**: [content-reviewer](../../activate/content-reviewer/SKILL.md) — once a partner is confirmed and creates content, review the draft against the brief before it ships.
- **Alternate**: [contract-helper](../contract-helper/SKILL.md) — finalize agreed terms into a partnership agreement.
- **Alternate**: [brief-generator](../../plan/brief-generator/SKILL.md) — send a full campaign brief to a creator who asked for more detail.

Termination note: keep a visited-set. If a skill in this chain was already invoked this session, stop and report chain-complete rather than re-running it. Max handoff depth is 3.

## Related Skills

- [influencer-discovery](../../discover/influencer-discovery/) - Find influencers to reach out to
- [fit-scorer](../../discover/fit-scorer/) - Prioritize who to contact first
- [brief-generator](../../plan/brief-generator/) - Send briefs to confirmed partners
- [contract-helper](../contract-helper/) - Finalize agreements
