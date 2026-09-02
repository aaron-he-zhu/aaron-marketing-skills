---
name: brief-generator
slug: brief-generator
displayName: "Brief Generator · 创作简报生成"
summary: "结构化红人简报:交付物、关键信息、创意方向、时间线、披露要求与报酬条款"
description: 'Use when the user asks to "create an influencer brief" or "write a campaign brief"; produces a structured creator brief with deliverables, key messages, creative direction, timeline, disclosure rules, and compensation terms. Not for choosing how to split spend across creators — use budget-optimizer. 达人合作简报/创作者BF'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user needs to brief one or more influencers for a campaign, standardize brief formats across a team, onboard ambassador partners, build reusable templates for recurring campaigns, or tighten brief clarity after revision-heavy collaborations. Also fires for platform-specific briefs (TikTok review, Instagram Stories takeover, YouTube integration)."
argument-hint: "<campaign or product> [platform] [content type]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: campaign/product/platform/deliverable/CTA/timeline/compensation inputs; stable opaque `creator_ref`, `brand_ref`, `page_ref`, `shipping_ref`, `contact_ref`, `brand_asset_ref`, `hashtag_ref`, `promo_code_ref`, and (when voice is used) `voice_source_ref`; plus `memory/projections/narrative.json`, `memory/projections/claims.json`, and relevant creator/channel projections. HOT is only an index to those sources. Raw creator/brand names and handles, page/asset-folder URLs, shipping addresses, contact names/emails/phones, hashtags, promo codes, and voice-source locators are transient rendering/dispatch inputs only.
- **Writes**: return a reference-safe creator brief inline by default; save it to `memory/influencer/brief-generator/YYYY-MM-DD-<topic>.md` only with exact authorization. Saved artifacts and handoffs represent creator, brand, landing destination, shipping destination, contact path, assets, hashtags, promo terms, and voice provenance only with `creator_ref`, `brand_ref`, `page_ref`, `shipping_ref`, `contact_ref`, `brand_asset_ref`, `hashtag_ref`, `promo_code_ref`, and `voice_source_ref`; never persist their raw identity/address/URL/contact/content values or a hidden mapping. Each unresolved-claim proposal is a separate exact `operation: propose` authorization; a brief-save approval does not cover it.
- **Done when**:
  - The brief covers all required sections (overview, key messages, deliverables, creative direction, timeline, compliance, compensation, contact).
  - Disclosure requirements and usage rights are stated explicitly, with no placeholder left unresolved that the user gave input for.
  - Deliverables and quantities match what the user requested per platform.
  - Key messages derive from accepted Narrative canon, claims are context-valid or visibly blocked, and the dependency tuple is present.
  - Any saved/handoff copy is reference-only, and creator delivery remains unsent until the separate outreach exact-send gate passes.
- **Primary next skill**: [budget-optimizer](../budget-optimizer/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md), including the Narrative/claims dependency tuple.

Required fields: `narrative_canon_id`, `narrative_canon_version`, `claims_projection_offset`, and `dependency_status: verified | approved-fallback | blocked`, plus the applicable opaque `creator_ref`, `brand_ref`, `page_ref`, `shipping_ref`, `contact_ref`, `brand_asset_ref`, `hashtag_ref`, `promo_code_ref`, and `voice_source_ref` values. Do not include their raw resolved values.

## Data Sources

This family has no live integrations required (Tier 1). The skill works end to end by asking the user for inputs: campaign details, deliverables, key messages, timeline, and compensation. Provide those in the prompt and you get a complete brief with zero setup.

Optional connectors that can enrich a brief when available:

- `~~influencer database` — resolve creator details transiently for personalization while retaining only `creator_ref` and opaque evidence refs in the saved brief/handoff.
- `~~social platform analytics` — confirm current format specs and best-performing post lengths per platform.
- `~~CRM` — fetch the assigned `contact_ref` and prior brief versions; resolve raw contact details only during an authorized dispatch.

Read accepted Narrative and claims projections before drafting. Claim approval is contextual: audience, market, media, offer window, and required disclaimer must match. No usable canon permits only an explicitly approved exploratory brief, never a creator-ready/on-canon label.

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required.

## Instructions

When a user requests a brief:

1. **Gather brief inputs** — capture campaign info, deliverables, key message, CTA, timeline, and compensation plus the applicable `creator_ref`, `brand_ref`, `page_ref`, `shipping_ref`, `contact_ref`, and `voice_source_ref`; resolve HOT pointers to their actual source records. Read Narrative/claims projections at named offsets. Keep raw identity, page, address, contact, and voice-source locators transient. If creator voice is required, capture the reference-safe intake via [creator-voice-intake.md](references/creator-voice-intake.md).
2. **Generate the professional brief** — fill the master template and tune it to the platform. Derive key messages from accepted canon and context-valid claims. Mark unresolved wording `[needs source]`, offer an exact `registry-events.py operation: propose` request for separate authorization, and prevent creator-ready status until resolved.
3. **Apply content-type and campaign-type variations** — adjust emphasis per platform (TikTok hook/sounds, IG Reels/Stories/Feed, YouTube integration/Shorts) and per campaign type (launch, review, event, ambassador, giveaway). Variation tables: [references/brief-templates.md](references/brief-templates.md#brief-variations-by-content-type).
4. **Save and route** — return the reference-safe brief inline. After exact permission, write it with canon/version/claims-offset fields and only the opaque identity/destination/contact/voice refs above. Durable creator, channel, claim, or campaign facts route to their owning registry only as separately authorized proposals; do not write HOT or canonical views automatically.
5. **Prepare delivery, do not imply send** — a `Send`, “deliver,” or “share with creators” request/label creates only a pending outreach handoff; it does not authorize delivery. Hand the brief to [outreach-manager](../../activate/outreach-manager/SKILL.md), resolve raw recipient/brand/page/contact values only transiently inside the delivery job, and pass its exact single-touch gate: independently approve the exact `recipient_ref`, channel, final rendered message/brief payload, and one concrete ISO-8601 `dispatch_at` plus timezone when scheduled, then run fresh eligibility and live-suppression checks immediately before the provider call. Any changed recipient, channel, payload, or schedule requires new approval.

Disclosure and usage rights must be stated explicitly — never leave them as placeholders once the user has given input. Briefs are guidelines, not scripts: respect the creator's voice while pinning the key messages and compliance terms.

## Example

**User**: "Create a brief for our organic protein powder: 1 IG Reel + 1 TikTok, morning-routine/workout-fuel angles, approved clean-label claims, draft due 15 Sep, go-live 22 Sep, $1,200 fee, and 12-month repost/paid rights in the US."

**Output**: Complete reference-safe inline brief using the supplied claims, deliverables, dates, fee, territory, and rights scope, with dated official platform specs or `TBD/NEEDS_INPUT`. Offer the exact `memory/influencer/brief-generator/YYYY-MM-DD-<topic>.md` path; do not claim it was saved without exact authorization. Saving or a `Send` label never authorizes delivery; outreach resolves the raw render only after its separate exact send gate.

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
  - [outreach-manager](../../activate/outreach-manager/SKILL.md) - prepare and, only after its exact single-touch authorization/preflight, deliver the finished brief to selected creators.

**Termination note**: Maintain a visited-set. If a recommended skill was already invoked this session, stop and report chain-complete instead of re-running it. Cap any handoff chain at max-depth 3.
