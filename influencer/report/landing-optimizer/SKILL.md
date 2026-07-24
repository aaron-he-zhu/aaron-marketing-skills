---
name: landing-optimizer
slug: landing-optimizer
displayName: "Landing Optimizer · 落地页优化"
summary: "流量落地页转化优化:信息匹配、首屏、CTA 与信任要素"
description: 'Use when the user asks to "optimize our landing page for influencer traffic", "fix our promo-code landing page", or "improve conversion from a creator campaign"; produces a message-match audit, page-structure and social-proof recommendations, a promo-code/CTA conversion plan, and an A/B test roadmap. Not for measuring campaign results after launch — use performance-analyzer. 落地页优化/达人流量转化提升'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user wants to build or improve a landing page that receives influencer-driven traffic: message match between creator content and the page, dedicated creator pages, promo-code auto-apply, social-proof placement, mobile conversion fixes, friction reduction, or A/B test planning for influencer campaigns."
argument-hint: "<landing page URL or campaign> [influencer handle] [promo code]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "report", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "report"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
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

- **Reads**: landing page URL and current state, conversion rate and goal, traffic source (influencer handles, platforms, content type), the influencer's key message/quote, promo code, audience demographics. Inputs come from the user when no tool is connected.
- **Writes**: optimization plan saved to `memory/influencer/landing-optimizer/YYYY-MM-DD-<topic>.md` (message-match audit, structure and social-proof recommendations, conversion/CTA plan, A/B test roadmap).
- **Promotes**: durable facts — active campaign name, page URL, baseline conversion rate, promo code, primary creator — to `memory/hot-cache.md`.
- **Done when**:
  - Message-match score and named fixes are produced for the page.
  - A prioritized conversion plan (CTA, promo-code experience, friction, mobile) exists with expected impact.
  - An A/B test roadmap with at least one hypothesis and success metric is written.
- **Primary next skill**: [performance-analyzer](../performance-analyzer/SKILL.md) — measure whether the optimizations moved conversion.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). The skill works by asking the user for the page URL, current conversion rate, the influencer's message, and the promo code, then producing the audit and plan from those inputs.

Optional connectors that can deepen the analysis when available:

- `~~analytics` — pull live conversion rate, bounce rate, scroll depth, and add-to-cart events instead of asking.
- `~~A/B testing platform` — read past test results and feed sample-size/duration estimates.
- `~~CMS / landing page builder` — inspect current page structure and copy directly.
- `~~social platform analytics` — confirm the creator's actual messaging and audience.

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. Every step degrades gracefully to user-supplied inputs.

## Instructions

When a user requests landing page help, work through these steps. Each step's fill-in template, ASCII layout, and HTML snippet live in [references/templates.md](references/templates.md) — keyed by the same step numbers.

1. **Assess current state** — capture campaign, URL, traffic source, current conversion rate, goal, and the traffic context (influencers, platforms, content type, key message, promo code, audience).
2. **Evaluate message match** — compare what the influencer says against what the page shows across message, value prop, offer, product, and tone; produce a Message Match Score (X/10) and named fixes. Mismatch causes confusion and abandonment. For paid runs, also verify the page's offer/promo terms against `memory/claims/offers.md` when the ledger exists — an ad's "50% off" promise is only true while the offer row is live.
3. **Page structure** — recommend the influencer-traffic layout (hero → social proof → product → more proof → FAQ → final CTA) and give section-by-section hero/social-proof/product fixes.
4. **Social proof integration** — place the driving creator most prominently, then the proof hierarchy: other influencers → customer reviews → trust indicators.
5. **Conversion optimization** — tune CTA copy/placement, design the promo-code experience (auto-apply via URL param, prominent display, confirmation), cut friction, and check mobile (load speed, thumb-friendly CTA, scroll depth).
6. **A/B testing plan** — rank tests by impact/effort, then write at least one hypothesis with variants, sample size, duration, and success metric.
7. **Influencer-specific pages** — decide whether a dedicated `/creator-name` page is warranted and what to personalize.
8. **Performance tracking** — set targets for load time, bounce, CR, add-to-cart, AOV; define UTM params and events for attribution.

Save the finished plan to `memory/influencer/landing-optimizer/YYYY-MM-DD-<topic>.md` (paid runs to `memory/ad/landing-optimizer/`) and promote durable facts to `memory/hot-cache.md`.

## Example

**User**: "Our landing page for @fitnessanna's protein powder campaign has a 1.2% conversion rate. How can we improve it?"

**Output** (abridged — full version in [references/templates.md](references/templates.md)):

- **Diagnosis**: 1.2% CR, below the 2-3% benchmark for influencer traffic.
- **Issues**: message mismatch (Anna says "smooth texture", page leads with "high protein"); Anna's content not featured; code `ANNA20` not auto-applied; mobile CTA below the fold.
- **Priority fixes**: Anna's video in hero (+0.5%), auto-apply promo (+0.3%), headline match (+0.3%), CTA above fold on mobile (+0.2%) → combined 1.2% → 2.5% CR.
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
