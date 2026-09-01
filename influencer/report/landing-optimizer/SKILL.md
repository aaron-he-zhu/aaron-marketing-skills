---
name: landing-optimizer
slug: landing-optimizer
displayName: "Landing Optimizer · 落地页优化"
summary: "流量落地页转化优化:信息匹配、首屏、CTA 与信任要素"
description: 'Use when the user asks to "optimize our landing page for influencer traffic", "fix our promo-code landing page", or "improve conversion from a creator campaign"; produces a message-match audit, page-structure and social-proof recommendations, a promo-code/CTA conversion plan, and an A/B test roadmap. Not for measuring campaign results after launch — use performance-analyzer. 落地页优化/达人流量转化提升'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user wants to build or improve a landing page that receives influencer-driven traffic: message match between creator content and the page, dedicated creator pages, promo-code auto-apply, social-proof placement, mobile conversion fixes, friction reduction, or A/B test planning for influencer campaigns."
argument-hint: "<landing page URL or campaign> [influencer handle] [promo code]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Landing Optimizer

This skill helps you create and optimize landing pages specifically for influencer marketing traffic. When users click from an influencer's post, the landing experience should feel connected and optimized for conversion.

> **Cross-discipline (paid ads):** this is also the **paid-ads** post-click skill — the page half of the ROAS **Offer** message-match (it pairs with [ad-creative-builder](../../../ad/orchestrate/ad-creative-builder/SKILL.md), which owns the ad half). The same diagnose-and-fix flow applies to paid landing pages; save paid runs under `memory/ad/landing-optimizer/`. On paid runs, message-match the page against the [offer-claims-registry](../../../protocol/offer-claims-registry/SKILL.md) ledger when present: offer terms, promo codes, and dates against `memory/claims/offers.md`, and claim wording against the approved variants in `memory/claims/claims-ledger.md`.

## Quick Start

Shortest invocation:

```
Optimize our landing page for traffic from [influencer campaign]
```

Common scenario — diagnose and fix a low-converting creator page:

```
Our influencer landing page has [X%] conversion rate. How can we improve it?
```

## Skill Contract

- **Reads**: a transient landing-page locator plus opaque `page_ref`/snapshot ref and current state, conversion rate and goal, traffic source, stable opaque `creator_ref`, platforms/content type, and any proposed creator display name, message, quote, asset, embed, or screenshot. Every creator reuse also reads the exact frozen `approved_asset_ref` plus creator-content-auditor `approval_ref`, and a rights record that is `active`, dated/evidenced, unexpired, and explicitly scoped to channel, territory, format, duration, and paid-vs-organic use. Inputs come from the user when no tool is connected.
- **Writes**: return the optimization plan inline by default; save it to `memory/influencer/landing-optimizer/YYYY-MM-DD-<topic>.md` (or the declared paid path) only with exact WARM-save authorization. Saved artifacts and handoffs keep `creator_ref`, `page_ref`, `snapshot_ref`, frozen asset/approval refs, and opaque rights/evidence refs only—never a raw creator handle/name, profile/content/page URL, email, provider ID, or embedded creator media.
- **Promotes**: only with separate exact authorization, promote durable facts — active campaign ref, opaque page ref, baseline conversion rate, promo code ref, primary `creator_ref` — to `memory/hot-cache.md`.
- **Done when**:
  - Message-match score and named fixes are produced for the page.
  - A prioritized conversion plan (CTA, promo-code experience, friction, mobile) exists with evidence-labeled impact or `Unknown/NEEDS_INPUT`.
  - An A/B test roadmap with at least one hypothesis and success metric is written.
  - Every proposed creator name/quote/asset/embed/screenshot reuse has the exact frozen auditor approval and an active dated scoped-rights row covering the whole implementation/test duration; blocked reuse remains `NEEDS_INPUT` and is neither copied nor tested.
- **Primary next skill**: [performance-analyzer](../performance-analyzer/SKILL.md) — measure whether the optimizations moved conversion.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill works from a transient page locator, current conversion data, opaque creator/page/evidence refs, approved messaging, and the rights inputs supplied by the user. A brief, draft, public post, or contract label does not substitute for the exact frozen creator-content-auditor approval plus current scoped-rights evidence.

Optional connectors that can deepen the analysis when available:

- `~~analytics` — pull live conversion rate, bounce rate, scroll depth, and add-to-cart events instead of asking.
- `~~A/B testing platform` — read past test results and feed sample-size/duration estimates.
- `~~CMS / landing page builder` — inspect current page structure and copy directly.
- `~~social platform analytics` — confirm the creator's actual messaging and audience.

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. Every step degrades gracefully to user-supplied inputs.

## Instructions

When a user requests landing page help, work through these steps. Each step's fill-in template, ASCII layout, and HTML snippet live in [references/templates.md](references/templates.md) — keyed by the same step numbers.

**Creator-reuse gate**: before copying, proposing, publishing, or testing any creator display name, quote, claim excerpt, video, image, thumbnail, embed, screenshot, badge, testimonial, creator-specific path, or creator-linked tracking token, require all of the following for that exact reuse: stable opaque `creator_ref`; exact frozen `approved_asset_ref`; matching [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) `approval_ref` with approved status for that version; rights status `active`; `status_observed_at`; opaque `status_evidence_ref`; unexpired start/end or perpetual duration; and explicit channel, territory, format, duration, and `paid | organic | both` scope matching the page and its entire proposed experiment/flight. Resolve any permitted display name or media locator only transiently at implementation. If any field is missing, stale, non-active, expired during the proposed test, disputed, revoked, unknown, or out of scope, return `NEEDS_INPUT` for that reuse and do not copy the name/quote, embed or screenshot the asset, publish a variant, or start a test. You may still audit non-creator page elements with opaque snapshot refs and propose generic placeholders.

1. **Assess current state** — capture campaign ref, transient page locator plus opaque page/snapshot refs, traffic source, current conversion rate, goal, and the traffic context (`creator_ref`, platforms, content type, approved message ref, promo code ref, audience). Keep raw locators transient.
2. **Evaluate message match** — compare only a creator message cleared by the reuse gate against the supplied page snapshot across message, value prop, offer, product, and tone; produce a Message Match Score (X/10) and named fixes. If the frozen approval or rights row is missing, keep the creator side `Unknown`, return `NEEDS_INPUT`, and do not quote or paraphrase it into page copy. For paid runs, also verify the page's offer/promo terms against `memory/claims/offers.md` when the ledger exists — an ad's "50% off" promise is only true while the offer row is live.
3. **Page structure** — recommend the influencer-traffic layout (hero → social proof → product → more proof → FAQ → final CTA) and give section-by-section fixes. Any creator-specific slot stays an opaque placeholder until the reuse gate passes.
4. **Social proof integration** — use a creator name, quote, asset, embed, screenshot, badge, or testimonial only when its exact frozen approval and rights scope pass; otherwise omit it and return `NEEDS_INPUT`. Apply the same gate separately to every additional creator.
5. **Conversion optimization** — tune CTA copy/placement, design the promo-code experience (auto-apply via URL param, prominent display, confirmation), cut friction, and check mobile (load speed, thumb-friendly CTA, scroll depth).
6. **A/B testing plan** — rank supported tests by impact/effort, then write at least one hypothesis with variants, sample size, duration, and success metric. Do not include or start a creator-name/asset/quote variant unless the approved rights duration covers the full planned test and resulting publication period.
7. **Influencer-specific pages** — decide whether a dedicated creator page is warranted. A creator name in the path or page, creator-linked tracking token, and every personalized asset each require the reuse gate; otherwise use a generic campaign page and opaque tracking ref.
8. **Performance tracking** — set targets for load time, bounce, CR, add-to-cart, AOV; define UTM params and events for attribution.

Return the finished plan inline. Offer `memory/influencer/landing-optimizer/YYYY-MM-DD-<topic>.md` (or `memory/ad/landing-optimizer/` for paid runs) for exact WARM-save authorization, and ask separately before any HOT promotion. Before save/handoff, replace raw creator identities, media/page/profile URLs, and copied creator text with opaque refs; the persisted plan resolves nothing directly.

## Example

**User**: "Our dated analytics export shows 1.2% CR versus our source-dated 2–3% target. Use `creator_ref: creator-042`, `approved_asset_ref: asset-v7`, and its frozen creator-content-auditor `approval_ref`. The supplied rights row is active, observed today with an opaque evidence ref, and covers US web landing-page display of the approved name, exact quote, video embed, and screenshot formats for both paid and organic traffic through the full six-week test/flight. The approved asset says 'smooth texture'; the page snapshot leads with 'high protein', omits the video, does not auto-apply the promo, and places the mobile CTA below the fold. Build a plan."

**Output** (abridged — full version in [references/templates.md](references/templates.md)):

- **Diagnosis**: 1.2% CR, below the supplied 2–3% target for influencer traffic.
- **Issues**: message mismatch (the frozen approved asset says "smooth texture", while the page snapshot leads with "high protein"); the approved creator asset is absent; the promo is not auto-applied; the mobile CTA is below the fold.
- **Priority fixes**: test the exact frozen approved video in the hero within its active scoped rights, auto-apply the promo, match the headline to approved wording, and move the mobile CTA above the fold. Any lift is Unknown until the predeclared A/B test reaches its decision rule; do not add isolated lift estimates into a promised CR.
- **Test plan**: wk1 hero changes, wk2 headline A/B, wk3 CTA copy.

## Reference Materials

- [templates.md](references/templates.md) — all step fill-in templates, ASCII layouts, HTML snippets, the full worked example, and tips.

- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes per connector category.
- [conversion-quality.md](../../../references/scoring-rubrics/conversion-quality.md) — advisory conversion rubric (non-veto) to sanity-check the optimization plan.
- Sibling skills in the influencer-marketing family:
  - [content-amplifier](../../activate/content-amplifier/SKILL.md) — source creator content for landing pages and drive traffic to them.
  - [brief-generator](../../target/brief-generator/SKILL.md) — align creator content with landing goals.

## Next Best Skill

**Primary**: [performance-analyzer](../performance-analyzer/SKILL.md) — measure whether the optimizations actually moved conversion, AOV, and attribution.

**Alternates** (same Report family):

- [content-amplifier](../../activate/content-amplifier/SKILL.md) — when the audit shows the page needs more creator content to feature.
- [roi-calculator](../roi-calculator/SKILL.md) — when the page's conversion is validated and you want to translate it into ROI and payback math.

**Termination note**: Maintain a visited-set this session. If a recommended skill has already been invoked, stop and report the chain as complete rather than re-running it. Hard stop at chain depth 3 to avoid loops.
