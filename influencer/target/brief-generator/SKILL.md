---
name: brief-generator
slug: brief-generator
displayName: "Brief Generator · 创作简报生成"
summary: "结构化红人简报:交付物、关键信息、创意方向、时间线、披露要求与报酬条款"
description: 'Use when the user asks to "create an influencer brief" or "write a campaign brief"; produces a structured creator brief with deliverables, key messages, creative direction, timeline, disclosure rules, and compensation terms. Not for choosing how to split spend across creators — use budget-optimizer. 达人合作简报/创作者BF'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user needs to brief one or more influencers for a campaign, standardize brief formats across a team, onboard ambassador partners, build reusable templates for recurring campaigns, or tighten brief clarity after revision-heavy collaborations. Also fires for platform-specific briefs (TikTok review, Instagram Stories takeover, YouTube integration)."
argument-hint: "<campaign or product> [platform] [content type]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Brief Generator

This skill helps you create clear, comprehensive influencer briefs that set creators up for success. Good briefs lead to better content, fewer revisions, and stronger partnerships.

## Quick Start

Shortest invocation:

```
Create an influencer brief for [campaign]
```

Common scenario:

```
Generate a TikTok brief for micro-influencers promoting [product], 1 review video, with disclosure and timeline
```

## Skill Contract

- **Reads**: campaign/product/platform/deliverable/CTA/timeline/compensation inputs plus `memory/projections/narrative.json`, `memory/projections/claims.json`, and relevant creator/channel projections; HOT is only an index to those sources.
- **Writes**: a creator-ready brief in conversation and, with permission, `memory/influencer/brief-generator/YYYY-MM-DD-<topic>.md`; unresolved claims become authorized claims proposals.
- **Done when**:
  - The brief covers all required sections (overview, key messages, deliverables, creative direction, timeline, compliance, compensation, contact).
  - Disclosure requirements and usage rights are stated explicitly, with no placeholder left unresolved that the user gave input for.
  - Deliverables and quantities match what the user requested per platform.
  - Key messages derive from accepted Narrative canon, claims are context-valid or visibly blocked, and the dependency tuple is present.
- **Primary next skill**: [budget-optimizer](../budget-optimizer/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md), including the Narrative/claims dependency tuple.

Required fields: `narrative_canon_id`, `narrative_canon_version`, `claims_projection_offset`, and `dependency_status: verified | approved-fallback | blocked`.

## Data Sources

This family has no live integrations required (Tier 1). The skill works end to end by asking the user for inputs: campaign details, deliverables, key messages, timeline, and compensation. Provide those in the prompt and you get a complete brief with zero setup.

Optional connectors that can enrich a brief when available:

- `~~influencer database` — pull creator handles, audience size, and past collaboration notes to personalize the "Why You" section.
- `~~social platform analytics` — confirm current format specs and best-performing post lengths per platform.
- `~~CRM` — fetch the assigned point of contact and prior brief versions for an ambassador.

Read accepted Narrative and claims projections before drafting. Claim approval is contextual: audience, market, media, offer window, and required disclaimer must match. No usable canon permits only an explicitly approved exploratory brief, never a creator-ready/on-canon label.

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required.

## Instructions

When a user requests a brief:

1. **Gather brief inputs** — capture campaign info, deliverables, key message, CTA, timeline, and compensation; resolve HOT pointers to their actual source records. Read Narrative/claims projections at named offsets. If creator voice is required, capture it via [creator-voice-intake.md](references/creator-voice-intake.md).
2. **Generate the professional brief** — fill the master template and tune it to the platform. Derive key messages from accepted canon and context-valid claims. Mark unresolved wording `[needs source]`, submit it through `registry-events.py` as an authorized `operation: propose` event, and prevent creator-ready status until resolved.
3. **Apply content-type and campaign-type variations** — adjust emphasis per platform (TikTok hook/sounds, IG Reels/Stories/Feed, YouTube integration/Shorts) and per campaign type (launch, review, event, ambassador, giveaway). Variation tables: [references/brief-templates.md](references/brief-templates.md#brief-variations-by-content-type).
4. **Save and route** — after permission, write the finished brief with canon/version/claims-offset fields. Durable creator, channel, claim, or campaign facts route to their owning registry as proposals; do not write HOT or canonical views automatically.

Disclosure and usage rights must be stated explicitly — never leave them as placeholders once the user has given input. Briefs are guidelines, not scripts: respect the creator's voice while pinning the key messages and compliance terms.

## Example

**User**: "Create a brief for micro-influencers to promote our new organic protein powder on Instagram and TikTok"

**Output**: Complete brief — messaging around organic ingredients and clean label, deliverables of 1 IG Reel + 1 TikTok video with platform specs, creative direction for "morning routine" / "workout fuel" angles, timeline with draft + go-live dates, #ad disclosure at caption start, and 12-month repost/paid usage rights. Saved to `memory/influencer/brief-generator/`.

## Reference Materials

- Shared contract: [skill-contract.md](../../../references/skill-contract.md)
- Shared state model: [state-model.md](../../../references/state-model.md)
- Connector recipes: [CONNECTORS.md](../../../CONNECTORS.md)
- STAR benchmark (when scoring brief quality): [references/star-benchmark.md](../../../references/star-benchmark.md)
- Brief templates & variations (master fill-in template, content-type and campaign-type variations, invoke patterns, tips): [brief-templates.md](references/brief-templates.md)
- Creator voice intake (capture real voice before briefing; creator-content-auditor reads the captured voice): [creator-voice-intake.md](references/creator-voice-intake.md)
- Sibling skills:
  - [campaign-planner](../campaign-planner/SKILL.md) - Create the campaign this brief supports
  - [budget-optimizer](../budget-optimizer/SKILL.md) - Allocate spend across the briefed creators
  - [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) - Review submitted content
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) - Deliver briefs to influencers
  - [contract-helper](../../activate/contract-helper/SKILL.md) - Include legal terms

## Next Best Skill

- **Primary**: [budget-optimizer](../budget-optimizer/SKILL.md) - Once the brief defines deliverables, set how spend is split across creators and platforms.
- **Alternates (same Target family)**:
  - [campaign-planner](../campaign-planner/SKILL.md) - Re-plan campaign scope if the brief surfaces new deliverable needs.
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) - Send the finished brief to selected creators.

**Termination note**: Maintain a visited-set. If a recommended skill was already invoked this session, stop and report chain-complete instead of re-running it. Cap any handoff chain at max-depth 3.
