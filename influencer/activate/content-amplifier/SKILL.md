---
name: content-amplifier
slug: content-amplifier
displayName: "Content Amplifier · 内容放量"
summary: "把跑赢的创作者内容用付费放大，并将 UGC 复用到付费、网站、邮件与自然渠道"
description: 'Use when the user asks to "amplify influencer content with paid media", "set up whitelisting or Spark Ads", "decide which posts to boost", "repurpose influencer content", "turn one video into multiple ads", or "build a UGC asset library"; produces (paid mode) a content-selection scorecard, a paid amplification strategy (whitelisting/boosting/dark posts), audience targeting, and a budget+optimization plan, or (repurpose mode) a rights-tracked content inventory, a 1-video-to-10+-asset repurposing map, per-format transformation specs, and a 30-day distribution plan. Not for gating whether a deliverable is publishable or FTC-compliant — use creator-content-auditor; not for the always-on brand posting calendar — use social-calendar-builder; not for drafting a net-new idea into platform-native packages — use social-creative-builder. 复用达人内容 / 内容放量.'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a brand has live, approved creator content and wants to extract more value from it. Paid mode: extend reach with paid spend — choosing which posts to boost, setting up whitelisted Partnership Ads or TikTok Spark Ads, planning dark posts, allocating an ad budget across creators and platforms, building audience targeting off creator lookalikes, running an optimization and scale/pause playbook. Repurpose mode: reuse one asset across paid, website, email, and organic social — generating ad variations from organic clips, building a searchable rights-tracked library, populating product pages with social proof, or planning a multi-channel rollout from a small source set."
argument-hint: "[--mode paid|repurpose] <campaign or content set> [budget] [platforms/channels]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "activate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "activate"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Content Amplifier

Extract more value from live, approved creator content. Two modes: **paid** (extend reach with paid spend — whitelisting, Spark Ads, dark posts, budget + optimization) and **repurpose** (reuse one asset across paid, website, email, and social — inventory, repurposing map, format specs, distribution plan). Both start from content that is already published and cleared; neither reviews whether the content is publishable — that gate is [creator-content-auditor](../creator-content-auditor/SKILL.md).

**Scope guard**: this skill does NOT score a deliverable for brand alignment, message accuracy, or FTC/disclosure compliance, and it does NOT compute a STAR Trust/Appeal score or run the `STAR-T1`/`STAR-T2` veto — that is the [creator-content-auditor](../creator-content-auditor/SKILL.md) gate's job. This skill works the downstream lever: turning approved content into paid reach or many-channel assets, then hands off. In a product launch, this skill owns the **repurposing map and the paid-amplification / distribution execution calendar** (including the 30-day plan for launch content); the launch discipline's [momentum-planner](../../../launch/prove/momentum-planner/SKILL.md) schedules only the launch *moments* and hands the distribution work here. In always-on organic social the split is the same shape: the standing brand posting calendar belongs to [social-calendar-builder](../../../social/craft/social-calendar-builder/SKILL.md) and net-new idea-to-multi-platform package drafting to [social-creative-builder](../../../social/craft/social-creative-builder/SKILL.md) — this skill keeps repurposing of existing assets and ALL paid amplification, and the social discipline only flags boost-worthy organic winners to it.

## Mode selector

| Mode | Use when | Core output |
|------|----------|-------------|
| **paid** (default) | Extend the reach of organic creator content with paid spend | Content-selection scorecard, amplification strategy (whitelisting / boosting / dark posts), audience targeting, budget allocation, optimization playbook |
| **repurpose** | Reuse one approved asset across paid, website, email, and social | Rights-tracked inventory, 1-video-to-10+ repurposing map, format transformation specs, 30-day distribution plan, content library + rights tracker |

Pick with `--mode paid` or `--mode repurpose`. If unset: "boost / amplify / whitelisting / Spark Ads / dark post / paid spend / budget" → **paid**; "repurpose / reuse / turn one video into many / asset library / social proof on pages / multi-channel rollout" → **repurpose**. If the request spans both (e.g. "cut ad variations *and* plan the paid spend"), run **repurpose** first to produce the assets, then hand to **paid** — do not silently merge; state which mode you ran.

## Quick Start

Shortest invocation:

```
Which influencer content should we amplify from [campaign]?          # paid
How can we repurpose this influencer content across channels?        # repurpose
```

Common scenarios:

```
--mode paid: Create a paid amplification plan for our influencer campaign with $5,000 across TikTok and Instagram
--mode repurpose: We have 3 great TikTok videos. Build a repurposing plan and a 30-day distribution calendar.
```

Output expectation — **paid**: every candidate scored, tiered, and given a spend that sums to budget, plus a scale/pause playbook. **repurpose**: every source asset rights-tagged, at least one mapped to 3+ formats across 2+ channels, plus a dated distribution plan.

## Skill Contract

- **Reads**:
  - *paid* — organic content set (creator handles, platform, content type, reach, engagement rate, views), amplification budget, campaign objective (awareness/traffic/conversions), target platforms, any prior performance data the user provides.
  - *repurpose* — source UGC assets (videos, reels, reviews, images), creator handles and platforms, usage rights per asset, original performance metrics, target channels. For atomizing a source, the pasted transcript/caption/review text.
  - Both pull prior campaign context from `memory/hot-cache.md` when `memory-management` is active.
- **Writes**: the mode's deliverable (paid: selection scorecard, strategy, targeting, budget, optimization playbook; repurpose: inventory, repurposing map, distribution plan, format specs, rights tracker) plus a reusable handoff summary. Save to `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md`.
- **Promotes**: durable facts — *paid*: chosen amplification mix, per-creator spend tiers, winning audiences, scale/pause thresholds; *repurpose*: rights levels, expiration dates, library naming convention, top-performing source assets — to `memory/hot-cache.md` (ask first).
- **Done when**:
  - *paid* — (1) each candidate is scored /25 and tiered (must amplify / consider / do not amplify) with a recommended spend; (2) a budget allocation by content, objective, and platform sums to the stated budget; (3) an optimization plan with KPI targets and scale/pause rules is recorded.
  - *repurpose* — (1) every source asset has a rights level and expiration recorded; (2) at least one source asset is mapped to 3+ distinct output formats across 2+ channels; (3) a dated distribution plan with an asset checklist exists.
- **Primary next skill**: *paid* → [performance-analyzer](../../report/performance-analyzer/SKILL.md) once campaigns are live; *repurpose* → [landing-optimizer](../../report/landing-optimizer/SKILL.md) to place the repurposed social proof where it converts.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md). State which mode ran. Label every metric Measured / User-provided / Estimated — never present a CPM, ROAS, view count, or rights date you were not given as Measured; if it is missing, ask for the export or mark it Estimated with the basis.

## Data Sources

This family is Tier 1: both modes work with no live integrations. Ask the user for the mode's inputs and produce the full artifact from those. Never invent reach, engagement, CPM, ROAS, or rights numbers — if a value is missing, ask for the export or label it Estimated.

Where a connector could sharpen the output (all optional, opt-in Tier 2/3):

- `~~social platform analytics` — pull organic reach, engagement rate, and view counts (both modes) instead of asking the user to paste them.
- `~~ad platform` (Meta Ads Manager, TikTok Ads Manager, Google Ads) — read live CPM/CTR/CPC/ROAS for the paid optimization playbook, and confirm Spark Ads / Partnership Ad authorization status.
- `~~influencer database` — verify creator audience demographics for lookalike targeting (paid); pull handles, platforms, and contract rights terms (repurpose).
- `~~DAM / asset library` — store and tag processed assets; enforce the naming convention (repurpose).
- `~~CRM` — supply retargeting/exclusion audiences (paid); reconcile creator records with usage-rights expirations (repurpose).

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required; absent a connector, the user supplies the numbers.

## Instructions

Select the mode first (see Mode selector), then run that mode's steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — produce the populated artifact, do not skip the table.

### Mode: paid

1. **Assess available content** — build the content inventory: campaign, piece count, budget, and a performance overview table (creator, platform, type, organic reach, ER, views, potential). [Paid Step 1 template](references/templates.md#paid-1-content-inventory-step-1).
2. **Select content for amplification** — weight selection criteria (organic performance, hook quality, message clarity, production quality, CTA), score each piece /25, then tier into Must Amplify / Consider If Budget Allows / Do Not Amplify with recommended spend. [Paid Step 2 template](references/templates.md#paid-2-content-selection-step-2).
3. **Develop amplification strategy** — pick the mix across three methods: whitelisting / Spark Ads (run through the creator's account, best for native feel and social proof), brand account boosting (full targeting control, less authentic), and dark posts (test variations, specific targeting). Output a budget-split table by method. [Paid Step 3 template](references/templates.md#paid-3-amplification-strategy-step-3-method-detail).
4. **Set up targeting** — primary lookalike off the creator's engaged audience, plus expansion segments (interest/behavioral/demographic for awareness; retargeting/custom/lookalike for conversions), ad sets per platform, and exclusions. [Paid Step 4 template](references/templates.md#paid-4-audience-targeting-step-4).
5. **Allocate budget** — split the stated budget by content, by objective, and by platform (with CPM estimates), and set a pacing schedule (learning → optimization → scaling). Allocations must sum to the stated budget. [Paid Step 5 template](references/templates.md#paid-5-budget-allocation-step-5).
6. **Optimization playbook** — KPI table (CPM, CTR, CPC, CVR, ROAS) with below/above-target actions, an optimization schedule, A/B tests, and explicit scale-up / pause / creative-refresh thresholds. [Paid Step 6 template](references/templates.md#paid-6-optimization-playbook-step-6).
7. **Platform-specific setup** — creator authorization + campaign steps for Meta Partnership Ads, TikTok Spark Ads, and YouTube video ads. [Paid Step 7 guide](references/templates.md#paid-7-platform-specific-setup-step-7).

Save the populated artifact and (with the user's OK) promote the chosen mix, per-creator spend tiers, winning audiences, and scale/pause thresholds.

### Mode: repurpose

1. **Audit available content** — build a content inventory and rights summary: every asset gets an ID, creator, platform, type, rights level, and status. [Repurpose Step 1 template](references/templates.md#repurpose-1-content-inventory-step-1).
2. **Map repurposing opportunities** — for each source asset, list output formats, target channels, modifications, and effort (one video → 10+ assets). [Repurpose Step 2 template](references/templates.md#repurpose-2-repurposing-opportunity-map-step-2).
3. **Create the repurposing plan** — rank source assets by performance and rights, then lay out a channel distribution plan across paid, owned, social, and sales. [Repurpose Step 3 template](references/templates.md#repurpose-3-repurposing-plan-step-3).
4. **Specify format transformations** — give aspect ratio, duration, and modification specs for video→video, video→static, quote/review, and image conversions. Per-platform specs live in [references/platforms/](../../../references/platforms). [Repurpose Step 4 specs](references/templates.md#repurpose-4-format-transformation-specs-step-4).
5. **Apply channel guidelines** — website, email, paid (incl. a creative testing matrix), and organic social best practices. [Repurpose Step 5 guidelines](references/templates.md#repurpose-5-channel-specific-guidelines-step-5).
6. **Build the content library** — folder structure, the `[campaign]_[creator]_[platform]_[type]_[variation]_[date]` naming convention, and metadata fields. [Repurpose Step 6 structure](references/templates.md#repurpose-6-content-library-structure-step-6).
7. **Track rights** — rights-by-content matrix, expiring-rights alerts, and rights-expansion opportunities. [Repurpose Step 7 tracker](references/templates.md#repurpose-7-usage-rights-tracker-step-7).

For slicing one source into many output atoms, apply the 7-tier extraction and near-duplicate flag in [references/atom-extraction.md](references/atom-extraction.md). Save the populated artifact and (with the user's OK) promote rights levels, expiration dates, the library naming convention, and top-performing source assets.

## Decision Gates

- **Stop and ask** — only when a mode input needed to proceed is missing and not inferable: (1) *paid* has no budget and none can be inferred — ask for the amplification budget; (2) *repurpose* has assets whose usage rights are unknown — ask for the rights level before recommending any ad/website/email reuse, because reusing a rights-restricted asset is a compliance risk you must not guess through.
- **Continue silently** — do not stop for: which 3 of N pieces to deep-dive (pick by performance); missing optional connector data (mark N/A, ask the user for the numbers, proceed); a platform not in the reference set (apply the nearest analog and note it). Missing organic metrics → ask once, then proceed with the pieces you have, labeling gaps.

## Example

**paid** — *User*: "We have 5 influencer TikToks from our launch campaign. Which should we amplify with our $5,000 paid budget?"

```markdown
| Creator | Views | ER | Hook | Amplify? | Budget |
|---------|-------|-----|------|----------|--------|
| @creator1 | 245K | 8.2% | 5/5 | Yes | $2,000 |
| @creator3 | 89K | 6.5% | 4/5 | Yes | $1,500 |
| @creator4 | 34K | 9.8% | 4/5 | Yes | $800 |
| @creator2 | 156K | 4.1% | 3/5 | Maybe | $500 |
| @creator5 | 67K | 2.3% | 2/5 | No | $0 |
Testing reserve $200. Get Spark Ads auth from top 3; run @creator1 as awareness,
@creator3 as traffic; scale winners after the 3-day learning phase.
```

**repurpose** — *User*: "We have 3 great TikTok videos. How should we repurpose them?" → 3 clips ranked; @creator1's 45s demo expands to 6 assets (Spark Ad, IG Reel, website embed, 3 stills, 15s Stories cut), backed by a 30-day calendar and asset checklist.

Full rankings, strategies, setups, and both worked examples: [references/templates.md](references/templates.md).

## Reference Materials

- [templates.md](references/templates.md) — fill-in templates for every step of both modes, platform setup guides, format transformation specs, both worked examples, and tips.
- [atom-extraction.md](references/atom-extraction.md) — 7-tier content-atom extraction, the virality heuristic, and the Jaccard near-duplicate flag for slicing one source into many (repurpose mode).
- Per-platform format & placement specs: [tiktok](../../../references/platforms/tiktok.md) · [youtube](../../../references/platforms/youtube.md) · [linkedin](../../../references/platforms/linkedin.md) · [x](../../../references/platforms/x.md) · [reddit](../../../references/platforms/reddit.md) · [grokipedia](../../../references/platforms/grokipedia.md).
- [star-benchmark.md](../../../references/star-benchmark.md) — the STAR framework; the Trust vetoes (`STAR-T1` FTC disclosure, `STAR-T2` claim integrity) that creator-content-auditor enforces before this skill runs.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../../references/state-model.md) — HOT/WARM/COLD memory tiers and save conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Sibling skills: [creator-content-auditor](../creator-content-auditor/SKILL.md), [contract-helper](../contract-helper/SKILL.md), [landing-optimizer](../../report/landing-optimizer/SKILL.md), [budget-optimizer](../../target/budget-optimizer/SKILL.md), [performance-analyzer](../../report/performance-analyzer/SKILL.md).

## Save Results

After delivering findings, ask: "Save these results for future sessions?" If yes, write `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md` with: one-line verdict/headline, top 3-5 actionable items, open loops or blockers, and source data references. Only the auditor-class gates may write memory without asking — this skill asks first, and hands veto-like risks (missing disclosure, unsubstantiated claims) to [creator-content-auditor](../creator-content-auditor/SKILL.md) rather than judging them here.

## Next Best Skill

**Primary**:
- *paid mode* → [performance-analyzer](../../report/performance-analyzer/SKILL.md) — measure amplification results once campaigns are live.
- *repurpose mode* → [landing-optimizer](../../report/landing-optimizer/SKILL.md) — drop the repurposed testimonials, hero videos, and quote cards onto the pages that convert.

**Alternates**:
- [content-amplifier --mode paid](SKILL.md) — when repurposed ad variations are ready for paid spend (run only if repurpose ran this session and paid has not).
- [contract-helper](../contract-helper/SKILL.md) — secure or expand usage rights before reuse (repurpose).
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) — reallocate paid budget across the recommended tiers (paid).

**Termination**: maintain a visited-set this session. If a recommended target (including the sibling mode of this skill) already ran, STOP and report the chain complete rather than re-invoking it. Max chain depth 3. When routing is ambiguous, present the options and stop instead of auto-following.
