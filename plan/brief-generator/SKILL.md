---
name: brief-generator
description: 'Use when the user asks to "create an influencer brief" or "write a campaign brief"; produces a structured creator brief with deliverables, key messages, creative direction, timeline, disclosure rules, and compensation terms. Not for choosing how to split spend across creators — use budget-optimizer.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user needs to brief one or more influencers for a campaign, standardize brief formats across a team, onboard ambassador partners, build reusable templates for recurring campaigns, or tighten brief clarity after revision-heavy collaborations. Also fires for platform-specific briefs (TikTok review, Instagram Stories takeover, YouTube integration)."
argument-hint: "<campaign or product> [platform] [content type]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: plan
  family: influencer-marketing
  impact-phase: Plan
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

- **Reads**: campaign name, brand, product/service, target platforms, content types and quantities, key message, CTA, timeline, compensation terms. Pulls any prior campaign facts from `memory/hot-cache.md` when present.
- **Writes**: a complete creator-ready brief saved to `memory/influencer/brief-generator/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable campaign facts (brand handle, campaign hashtag, disclosure standard, posting window, usage-rights duration) to `memory/hot-cache.md`.
- **Done when**:
  - The brief covers all required sections (overview, key messages, deliverables, creative direction, timeline, compliance, compensation, contact).
  - Disclosure requirements and usage rights are stated explicitly, with no placeholder left unresolved that the user gave input for.
  - Deliverables and quantities match what the user requested per platform.
- **Primary next skill**: [budget-optimizer](../../plan/budget-optimizer/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family has no live integrations required (Tier 1). The skill works end to end by asking the user for inputs: campaign details, deliverables, key messages, timeline, and compensation. Provide those in the prompt and you get a complete brief with zero setup.

Optional connectors that can enrich a brief when available:

- `~~influencer database` — pull creator handles, audience size, and past collaboration notes to personalize the "Why You" section.
- `~~social platform analytics` — confirm current format specs and best-performing post lengths per platform.
- `~~CRM` — fetch the assigned point of contact and prior brief versions for an ambassador.

When the brief makes marketing claims (performance figures, guarantees, health/finance statements), pull approved claim wording and claim-level disclaimers from `memory/claims/claims-ledger.md` — the [offer-claims-registry](../../protocol/offer-claims-registry/SKILL.md) ledger — when present (keyless Tier 1).

See [CONNECTORS.md](../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required.

## Instructions

When a user requests a brief:

1. **Gather brief inputs** — capture campaign info, deliverables (platform, content type, quantity), key message, CTA, timeline, and compensation. Use the input checklist in [references/brief-templates.md](references/brief-templates.md#brief-input-capture). Pull prior campaign facts from `memory/hot-cache.md` if present. If the user wants the brief to reflect the creator's real voice, capture it first via [creator-voice-intake.md](references/creator-voice-intake.md).
2. **Generate the professional brief** — fill the master template (overview, key messages, deliverables, creative direction, product details, campaign assets, timeline, approval process, legal/compliance with disclosure + usage rights, compensation, contact, FAQ, acknowledgment). Full fill-in template: [references/brief-templates.md](references/brief-templates.md#master-brief-template). Tune wording to the platform. Source claim-bearing key messages from the approved wording in `memory/claims/claims-ledger.md` when the claim is registered; mark unregistered claims `[needs source]` in the brief and drop them as one-line candidates in `memory/claims/candidates.md` for [offer-claims-registry](../../protocol/offer-claims-registry/SKILL.md) to resolve.
3. **Apply content-type and campaign-type variations** — adjust emphasis per platform (TikTok hook/sounds, IG Reels/Stories/Feed, YouTube integration/Shorts) and per campaign type (launch, review, event, ambassador, giveaway). Variation tables: [references/brief-templates.md](references/brief-templates.md#brief-variations-by-content-type).
4. **Save and promote** — write the finished brief to `memory/influencer/brief-generator/YYYY-MM-DD-<topic>.md`. Promote durable facts (brand handle, campaign hashtag, disclosure standard, posting window, usage-rights duration) to `memory/hot-cache.md`.

Disclosure and usage rights must be stated explicitly — never leave them as placeholders once the user has given input. Briefs are guidelines, not scripts: respect the creator's voice while pinning the key messages and compliance terms.

## Example

**User**: "Create a brief for micro-influencers to promote our new organic protein powder on Instagram and TikTok"

**Output**: Complete brief — messaging around organic ingredients and clean label, deliverables of 1 IG Reel + 1 TikTok video with platform specs, creative direction for "morning routine" / "workout fuel" angles, timeline with draft + go-live dates, #ad disclosure at caption start, and 12-month repost/paid usage rights. Saved to `memory/influencer/brief-generator/`.

## Reference Materials

- Shared contract: [skill-contract.md](../../references/skill-contract.md)
- Shared state model: [state-model.md](../../references/state-model.md)
- Connector recipes: [CONNECTORS.md](../../CONNECTORS.md)
- C3 scoring architecture (when scoring brief quality): [references/c3/scoring-architecture.md](../../references/c3/scoring-architecture.md)
- Brief templates & variations (master fill-in template, content-type and campaign-type variations, invoke patterns, tips): [brief-templates.md](references/brief-templates.md)
- Creator voice intake (capture real voice before briefing; content-reviewer reads the captured voice): [creator-voice-intake.md](references/creator-voice-intake.md)
- Sibling skills:
  - [campaign-planner](../campaign-planner/SKILL.md) - Create the campaign this brief supports
  - [budget-optimizer](../budget-optimizer/SKILL.md) - Allocate spend across the briefed creators
  - [content-reviewer](../../activate/content-reviewer/SKILL.md) - Review submitted content
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) - Deliver briefs to influencers
  - [contract-helper](../../activate/contract-helper/SKILL.md) - Include legal terms

## Next Best Skill

- **Primary**: [budget-optimizer](../../plan/budget-optimizer/SKILL.md) - Once the brief defines deliverables, set how spend is split across creators and platforms.
- **Alternates (same Plan family)**:
  - [campaign-planner](../campaign-planner/SKILL.md) - Re-plan campaign scope if the brief surfaces new deliverable needs.
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) - Send the finished brief to selected creators.

**Termination note**: Maintain a visited-set. If a recommended skill was already invoked this session, stop and report chain-complete instead of re-running it. Cap any handoff chain at max-depth 3.
