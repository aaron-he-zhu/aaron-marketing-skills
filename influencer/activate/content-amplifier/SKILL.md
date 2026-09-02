---
name: content-amplifier
slug: content-amplifier
displayName: "Content Amplifier · 内容放量"
summary: "把跑赢的创作者内容用付费放大，并将 UGC 复用到付费、网站、邮件与自然渠道"
description: 'Use when the user asks to "amplify influencer content with paid media", "set up whitelisting or Spark Ads", "decide which posts to boost", "repurpose influencer content", "turn one video into multiple ads", or "build a UGC asset library"; produces (paid mode) a content-selection scorecard, a paid amplification strategy (whitelisting/boosting/dark posts), audience targeting, and a budget+optimization plan, or (repurpose mode) a rights-tracked content inventory, a 1-video-to-10+-asset repurposing map, per-format transformation specs, and a 30-day distribution plan. Not for gating whether a deliverable is publishable or FTC-compliant — use creator-content-auditor; not for the always-on brand posting calendar — use social-calendar-builder; not for drafting a net-new idea into platform-native packages — use social-creative-builder. 复用达人内容 / 内容放量.'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a brand has a frozen, auditor-approved creator asset with active scoped rights and wants to extract more value from it. Paid mode: extend reach with paid spend — choosing which posts to boost, setting up whitelisted Partnership Ads or TikTok Spark Ads, planning dark posts, allocating an ad budget across creators and platforms, building audience targeting off creator lookalikes, running an optimization and scale/pause playbook. Repurpose mode: reuse one asset across paid, website, email, and organic social — generating ad variations from organic clips, building a searchable rights-tracked library, populating product pages with social proof, or planning a multi-channel rollout from a small source set."
argument-hint: "[--mode paid|repurpose] <campaign or content set> [budget] [platforms/channels]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "activate", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "activate"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Content Amplifier

Extract more value from a frozen, approved creator asset. Two modes: **paid** (extend reach with paid spend — whitelisting, Spark Ads, dark posts, budget + optimization) and **repurpose** (reuse one asset across paid, website, email, and social — inventory, repurposing map, format specs, distribution plan). Both start from the exact version cleared by [creator-content-auditor](../creator-content-auditor/SKILL.md) and active scoped rights. Spark/boost paths additionally require the platform state and live post they depend on; a dark post need not have been published organically.

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
Which frozen auditor-approved asset with current active paid rights should we amplify from [campaign]?  # paid
How can we repurpose this frozen approved asset within its evidenced active destination scope?           # repurpose
```

Common scenarios:

```
--mode paid: Create a $5,000 TikTok/Instagram plan from these frozen approved assets and supplied current active scoped-rights records
--mode repurpose: Build a 30-day plan from these 3 frozen approved videos and supplied current active rights records covering the requested destinations
```

Output expectation — **paid**: every evidence-complete candidate scored, tiered, and given a spend that sums to budget, plus a scale/pause playbook. Any candidate missing organic-performance evidence or a Hook/Message/Quality/CTA observation remains `NOT_SCORED/NEEDS_INPUT` with no `/25`, rank, tier, or spend. **repurpose**: every source asset rights-tagged, at least one eligible asset mapped to 3+ formats across 2+ channels, plus a dated distribution plan.

## Skill Contract

- **Reads**:
  - *paid* — stable opaque `creator_ref` values plus transient creator locators, platform, content type, dated organic reach/engagement/views evidence, separate dated Hook/Message/Quality/CTA observations, amplification budget, campaign objective (awareness/traffic/conversions), target platforms, any prior performance data the user provides, and each candidate asset's current rights status/evidence plus existing placements when present.
  - *repurpose* — source UGC assets (videos, reels, reviews, images), stable opaque `creator_ref` values plus transient creator locators and platforms, exact frozen `approved_asset_ref`, opaque authorized `source_ref`, usage rights per asset, rights status with observation time/evidence, original performance metrics, target channels, and existing placements. For atomizing a source, the pasted transcript/caption/review text is transient evidence bound to that three-ref source identity; a raw handle or content URL never becomes `source_ref`.
  - Both pull prior campaign context from `memory/hot-cache.md` when `memory-management` is active.
- **Writes**: return the mode's deliverable and handoff inline by default; save to `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md` only with exact WARM-save authorization. Saved artifacts and handoffs reuse an explicitly carried opaque `creator_ref`, or a verified creator-registry aggregate ID; otherwise generate one random `creator-<UUIDv4>` once for the lineage. Never persist a raw handle, creator name, profile/content URL, email, provider ID, or deterministic hash as identity. Keep only `creator_ref`, frozen asset/approval refs, opaque evidence/rights/contact/placement refs, and non-identifying campaign data; every saved atom source must carry `creator_ref` + exact `approved_asset_ref` + opaque `source_ref`. If no authorized resolver exists, mark identity unresolved and require the transient locator again when needed.
- **Promotes**: only with separate exact authorization, promote durable facts — *paid*: chosen amplification mix, per-creator spend tiers, winning audiences, scale/pause thresholds; *repurpose*: rights levels, expiration dates, library naming convention, top-performing source assets — to `memory/hot-cache.md`. A newly observed revocation, dispute, expiry, or other rights-status change is not made canonical here: offer only a separately authorized handoff to the existing [creator-registry](../../../protocol/creator-registry/SKILL.md) proposal path with the exact status evidence. This skill does not append or accept that proposal.
- **Done when**:
  - *paid* — (1) each evidence-complete candidate has dated evidence for organic performance plus Hook/Message/Quality/CTA and is scored /25 before any tier or spend; every incomplete candidate is `NOT_SCORED/NEEDS_INPUT` with no total/rank/tier/spend; (2) a budget allocation across only evidence-complete eligible content, objectives, and platforms sums to the stated budget; (3) an optimization plan with supplied KPI targets and scale/pause rules is recorded, or those rules stay `NEEDS_INPUT`; (4) every selected asset has current `active` rights evidence covering the intended use.
  - *repurpose* — (1) every source asset has a rights level, expiration, `active | expired | revoked | disputed | unknown` status, `status_observed_at`, and `status_evidence_ref`; (2) at least one source asset is mapped to 3+ distinct output formats across 2+ channels; (3) a dated distribution plan with an asset checklist exists; (4) any existing placement affected by a non-active or out-of-scope status appears in the manual removal queue.
- **Primary next skill**: *paid* → [performance-analyzer](../../report/performance-analyzer/SKILL.md) once campaigns are live; *repurpose* → [landing-optimizer](../../report/landing-optimizer/SKILL.md) to place the repurposed social proof where it converts.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md). State which mode ran. Label every metric Measured / User-provided / Calculated / Estimated / Unknown. Never fill a missing CPM, ROAS, view count, rights date, or decision threshold with an example value: ask for the export or use `Unknown`/`NEEDS_INPUT`. Organic performance and the Hook/Message/Quality/CTA observations are selection evidence, not forecast fields: if any is missing, do not substitute `Estimated`; set that asset to `NOT_SCORED/NEEDS_INPUT` and emit no `/25`, rank, tier, or spend. Use Estimated elsewhere only when the user supplied or approved the calculation inputs and assumptions, and show that basis.

## Data Sources

This family is Tier 1: both modes work with no live integrations. Ask the user for the mode's inputs and produce the supported portion of the artifact from those. Never invent reach, engagement, CPM, ROAS, rights numbers, or selection observations. Missing organic reach/engagement/views evidence or Hook/Message/Quality/CTA evidence is never `Estimated`; it makes that asset `NOT_SCORED/NEEDS_INPUT`. Other forecast fields may be Estimated only from supplied or explicitly approved inputs and assumptions; otherwise use `Unknown/NEEDS_INPUT`.

Where a connector could sharpen the output (all optional, opt-in Tier 2/3):

- `~~social platform analytics` — pull organic reach, engagement rate, and view counts (both modes) instead of asking the user to paste them.
- `~~ad platform` (Meta Ads Manager, TikTok Ads Manager, Google Ads) — read live CPM/CTR/CPC/ROAS for the paid optimization playbook, and confirm Spark Ads / Partnership Ad authorization status.
- `~~influencer database` — verify creator audience demographics for lookalike targeting (paid); transiently resolve creator locators while retaining only `creator_ref`, platform, and contract-rights refs in saved repurpose artifacts.
- `~~DAM / asset library` — store and tag processed assets; enforce the naming convention (repurpose).
- `~~CRM` — supply retargeting/exclusion audiences (paid); reconcile creator records with usage-rights expirations (repurpose).

See [CONNECTORS.md](../../../CONNECTORS.md) for the verified free/keyless recipe per category. None are required; absent a connector, the user supplies the numbers.

## Instructions

Select the mode first (see Mode selector), then run that mode's steps. Each step has a fill-in template in [references/templates.md](references/templates.md) — produce the populated artifact, do not skip the table.

### Mode: paid

1. **Assess available content** — build the content inventory: campaign, piece count, budget, `creator_ref`, platform/type, and dated organic reach/ER/views values with evidence refs. Do not create an organic-performance score from an absent, undated, or unevidenced metric. [Paid Step 1 template](references/templates.md#paid-1-content-inventory-step-1).
2. **Select content for amplification** — record separate 1–5 observations for organic performance, Hook, Message, Quality, and CTA, each with `source_ref` and `observed_at`. Only when all five are present may the asset receive `/25`, rank, tier, or spend. If any component or its evidence is missing, preserve supplied observations, set `score_state: NOT_SCORED` and execution `NEEDS_INPUT`, list the exact gaps, and do not estimate, normalize, prorate, or hand-calculate a partial total. [Paid Step 2 template](references/templates.md#paid-2-content-selection-step-2).
3. **Develop amplification strategy** — describe three operational methods neutrally: whitelisting / Partnership / Spark Ads use the creator identity and require matching platform authorization; brand-account ads use the brand identity and require the licensed asset in the brand ad account; dark posts are unpublished ad-account placements. Do not claim that one method improves engagement, preserves authenticity, boosts credibility, or performs better/worse without supplied comparative evidence. Treat method choice and budget mix as a declared test or user decision. [Paid Step 3 template](references/templates.md#paid-3-amplification-strategy-step-3-method-detail).
4. **Set up targeting** — primary lookalike off the creator's engaged audience, plus expansion segments (interest/behavioral/demographic for awareness; retargeting/custom/lookalike for conversions), ad sets per platform, and exclusions. [Paid Step 4 template](references/templates.md#paid-4-audience-targeting-step-4).
5. **Allocate budget** — split the stated budget only across rights-eligible, fully scored assets, then by objective and platform; set a pacing schedule (learning → optimization → scaling). Allocations must sum to the stated budget. If no fully scored eligible asset remains, return `NEEDS_INPUT` and no hypothetical allocation. [Paid Step 5 template](references/templates.md#paid-5-budget-allocation-step-5).
6. **Optimization playbook** — KPI table (CPM, CTR, CPC, CVR, ROAS) with below/above-target actions, an optimization schedule, A/B tests, and explicit scale-up / pause / creative-refresh thresholds. [Paid Step 6 template](references/templates.md#paid-6-optimization-playbook-step-6).
7. **Platform-specific setup** — verify the frozen asset version is auditor-approved and its rights tracker says `active` with a dated evidence reference; separately confirm the grant is unexpired and scoped to the intended platform, territory, format, and paid use. `expired`, `revoked`, `disputed`, or `unknown` fails closed for new use. Spark/boost or other existing-post methods also require the matching live post and platform authorization; dark-post setup does not require prior organic publication. Missing approval, required live state, or usable rights stops activation with `NEEDS_INPUT`; none may be inferred. [Paid Step 7 guide](references/templates.md#paid-7-platform-specific-setup-step-7).

Return the populated artifact inline. Offer its exact WARM path for save authorization, then ask separately before any HOT promotion. Any ad-account setup, upload, launch, or spend is a further external mutation requiring exact action approval.

### Mode: repurpose

1. **Audit available content** — build a content inventory and rights summary: every asset gets an ID, creator, platform, type, rights level/expiry, rights status, `status_observed_at`, and `status_evidence_ref`. [Repurpose Step 1 template](references/templates.md#repurpose-1-content-inventory-step-1).
2. **Map repurposing opportunities** — for each source asset, list output formats, target channels, modifications, and effort (one video → 10+ assets). [Repurpose Step 2 template](references/templates.md#repurpose-2-repurposing-opportunity-map-step-2).
3. **Create the repurposing plan** — rank source assets by performance and rights, then lay out a channel distribution plan across paid, owned, social, and sales. [Repurpose Step 3 template](references/templates.md#repurpose-3-repurposing-plan-step-3).
4. **Specify format transformations** — give aspect ratio, duration, and modification specs for video→video, video→static, quote/review, and image conversions. Per-platform specs live in [references/platforms/](../../../references/platforms). [Repurpose Step 4 specs](references/templates.md#repurpose-4-format-transformation-specs-step-4).
5. **Apply channel guidelines** — website, email, paid (incl. a creative testing matrix), and organic social best practices. [Repurpose Step 5 guidelines](references/templates.md#repurpose-5-channel-specific-guidelines-step-5).
6. **Build the content library** — folder structure, the `[campaign]_[creator_ref]_[platform]_[type]_[variation]_[date]` naming convention, and metadata fields. [Repurpose Step 6 structure](references/templates.md#repurpose-6-content-library-structure-step-6).
7. **Track rights** — rights-by-content matrix, expiring-rights alerts, rights-expansion opportunities, and a manual removal queue derived only from existing placements. Before recommending a destination, require `status: active` with `status_observed_at` and `status_evidence_ref`, then verify that the grant is unexpired and covers that channel, territory, format, and use. `expired`, `revoked`, `disputed`, `unknown`, and out-of-scope rights remain blocked for new use. Put affected existing placements in the queue with destination, owner, `due_at`, and `completion_ref`; a blank completion reference means removal is not proven. [Repurpose Step 7 tracker](references/templates.md#repurpose-7-usage-rights-tracker-step-7).

For slicing one source into many output atoms, apply the 7-tier extraction in [references/atom-extraction.md](references/atom-extraction.md). Bind every atom to `creator_ref`, exact `approved_asset_ref`, and an opaque authorized `source_ref`. Any atom ranking, virality score, near-duplicate threshold, paid-placement choice, or hero-placement choice requires a user-approved rule or source-dated rule ref; without one, retain the atoms as `NOT_SCORED/NEEDS_INPUT` and do not auto-rank/drop/select them. Return the populated artifact inline; request one exact authorization for its WARM save and a separate authorization for any HOT promotion.

For either mode, the removal queue is a hand-operated follow-up view, not authorization to remove or edit anything. Never pause an ad, delete a post, unpublish a page, edit a platform, or mark `completion_ref` without separate exact action approval and completion evidence. When rights status changes, offer the exact evidence to the existing creator-registry proposal workflow only after separate authorization; do not create a new rights registry or treat the WARM tracker as canonical.

## Decision Gates

- **Stop and ask** — only when a mode input needed to proceed is missing and not inferable: (1) *paid* has no budget — ask for the amplification budget; (2) a paid candidate lacks dated/evidenced organic metrics or any Hook/Message/Quality/CTA observation — return that asset as `NOT_SCORED/NEEDS_INPUT` with no total/rank/tier/spend; (3) either mode lacks the frozen asset's auditor-approval reference, has assets whose rights are `expired`, `revoked`, `disputed`, `unknown`, lack dated status evidence, or do not cover the intended channel/territory/format/use — return `NEEDS_INPUT` for the exact approval or rights gap before recommending activation or reuse, because neither approval nor a restricted grant may be guessed through.
- **Continue silently** — do not stop for a missing optional connector or a platform absent from the reference set; use user-supplied evidence or the nearest documented format analog and disclose it. You may continue rights inventory or evidence-gap reporting for an incomplete candidate, but may not deep-dive, rank, tier, allocate spend, or create a paid recommendation for it.

## Example

**paid** — *User*: "The dated organic export supplies views/ER and Hook observations for five frozen, auditor-approved assets with active scoped paid rights, but we have no Message, Quality, or CTA observations. Allocate our $5,000 budget."

```markdown
Evidence basis: organic metrics, Hook observations, frozen approval refs, and rights status/scope are user-provided; Message, Quality, and CTA evidence is missing.

| Creator Ref | Organic | Hook | Message | Quality | CTA | Score State | Total / Rank / Spend |
|-------------|---------|------|---------|---------|-----|-------------|----------------------|
| [creator_ref per asset] | supplied | supplied | Unknown | Unknown | Unknown | `NOT_SCORED/NEEDS_INPUT` | none |

No `/25`, rank, tier, or allocation is emitted. Request dated Message/Quality/CTA observations with opaque evidence refs; never fill them with `Estimated` or force a partial total.
```

**repurpose** — *User*: "Use three supplied frozen, auditor-approved assets mapped to `creator_ref-1`, `creator_ref-2`, and `creator_ref-3`. Their rights records are `active`, dated, evidenced, unexpired, and cover the requested derivative edits and US paid, website, email, organic-social, and YouTube destinations. Build a 30-day reuse plan." → Map only those evidenced uses and retain `creator_ref` plus opaque asset/evidence refs in the plan.

If either request omitted the frozen approval reference or current scoped-rights evidence, return `NEEDS_INPUT` with those exact gaps and do not rank, allocate, transform, or schedule the asset. Paid selection additionally stays `NOT_SCORED/NEEDS_INPUT` when organic metrics/evidence or any Hook/Message/Quality/CTA observation/evidence is missing.

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

After delivering findings inline, ask: "Save these results for future sessions?" If yes, obtain exact authorization for `memory/influencer/content-amplifier/YYYY-MM-DD-<topic>.md` and write the one-line verdict/headline, top 3-5 actionable items, open loops or blockers, and opaque source references. Saved identity is `creator_ref` only; remove raw handles, names, profile/content URLs, emails, and provider IDs. Saving does not authorize HOT promotion or any ad-platform mutation. This skill hands veto-like risks (missing disclosure, unsubstantiated claims) to [creator-content-auditor](../creator-content-auditor/SKILL.md) rather than judging them here.

## Next Best Skill

**Primary**:
- *paid mode* → [performance-analyzer](../../report/performance-analyzer/SKILL.md) — measure amplification results once campaigns are live.
- *repurpose mode* → [landing-optimizer](../../report/landing-optimizer/SKILL.md) — drop the repurposed testimonials, hero videos, and quote cards onto the pages that convert.

**Alternates**:
- [content-amplifier --mode paid](SKILL.md) — when repurposed ad variations are ready for paid spend (run only if repurpose ran this session and paid has not).
- [contract-helper](../contract-helper/SKILL.md) — secure or expand usage rights before reuse (repurpose).
- [budget-optimizer](../../target/budget-optimizer/SKILL.md) — reallocate paid budget across the recommended tiers (paid).

**Termination**: maintain a visited-set this session. If a recommended target (including the sibling mode of this skill) already ran, STOP and report the chain complete rather than re-invoking it. Max chain depth 3. When routing is ambiguous, present the options and stop instead of auto-following.
