---
name: fit-scorer
slug: fit-scorer
displayName: "Fit Scorer · 红人适配评分"
summary: "用 typed STAR 适配度(S) 维度评估创作者，并将活动商业适配度作为独立矩阵排序"
description: 'Use when the user asks to "score this influencer", "rank these creators for our campaign", or "tell me which influencer is the best fit"; produces the typed STAR Suitability (S) read plus a separately labeled campaign-fit ranking without mixing campaign-specific commercial fit into the Suitability read. Not for finding new influencers — use influencer-discovery; not for sending outreach — use outreach-manager. 达人适配度评分/创作者筛选排名'
version: "19.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a user has a shortlist of influencers and needs an objective, weighted score to prioritize outreach, choose between candidates, justify a selection to stakeholders, set consistent evaluation standards, compare creators across niches or platforms, or build long-term partner tiers. Activates on requests like score @handle for our brand, compare and rank these creators, or which of these is the best fit."
argument-hint: "<brand or campaign> <influencer handle(s)> [campaign goal: awareness|engagement|conversion]"
metadata: {"author": "aaron-he-zhu", "version": "19.0.0", "discipline": "influencer", "phase": "scout", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "scout"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Fit Scorer

Score each shortlisted creator on the typed STAR **Suitability (S)** dimension, then keep campaign-specific commercial fit in a separate prioritization matrix. The Suitability read is portable and brand-independent; the commercial matrix is not a Suitability score and never enters the SQS.

## Quick Start

Score one influencer:

```
Score @[handle] for [brand/campaign] and tell me if they're a good fit
```

Compare and rank a shortlist:

```
Compare and rank these influencers for [campaign]: @influencer1, @influencer2, @influencer3
```

## Skill Contract

- **Reads**: brand/campaign context, target audience definition, campaign goal, and a shortlist of influencer handles (supplied by the user or carried over from `influencer-discovery`). Optional prior audience profiles from `memory/influencer/audience-mapper/` and competitor partner benchmarks from `memory/influencer/competitor-tracker/`. For rostered creators, read partnership history and audience-stat provenance from `memory/creators/<handle-slug>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) roster record — as Partnership Potential inputs.
- **Writes**: only with explicit authorization, a report containing the typed Suitability (S) read plus a separately labeled commercial-fit comparison at `memory/influencer/fit-scorer/YYYY-MM-DD-<topic>.md`.
- **Promotes**: only with separate authorization, evidence-backed top picks and their exact Suitability (S) read and catalog version; never promote an unscored or provisional result.
- **Done when**:
  - Every creator has all 10 Suitability items `S1`–`S10` explicitly Pass/Partial/Fail/Unknown/N/A with dated evidence or a gap reason.
  - The typed goal/context and the Suitability item states are preserved for the gate; Unknown prevents a Suitability read.
  - Any commercial-fit ranking is visibly separate from the Suitability read and cannot override a veto or missing evidence.
- **Primary next skill**: [competitor-tracker](../../target/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already partner with.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). Fit Scorer works end to end by asking the user for the inputs it scores — handles, audience targets, brand values, and any metrics they have. A connector sharpens the numbers but none is required.

- `~~influencer database` — follower counts, audience demographics, and partnership history.
- `~~social platform analytics` — engagement rate, comment quality samples, posting cadence, growth trend.
- `~~audience intelligence` — real-vs-bot follower estimates and audience overlap with your target.
- **Roster record (keyless Tier 1)** — prior contact, response reputation, and delivery history come from `memory/creators/<handle-slug>.md` when the creator is rostered ([creator-registry](../../../protocol/creator-registry/SKILL.md) curates it); `~~CRM` is an optional Tier-2 sharpener for the same history when no roster record exists.

**Measured YouTube inputs (free key)**: for YouTube candidates, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" videos @handle --limit 10` supplies the engagement-authenticity inputs directly — per-video views/likes/comments against the displayed subscriber base (views-to-subs consistency, comment rate, cadence) — so those sub-scores come from **Measured** numbers instead of screenshots. Free `YOUTUBE_API_KEY`; shortlist vetting only (ToS refuses bulk-harvesting quota). See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

With zero integrations, ask the user to supply each value the scoring tables request; the framework and weighting still produce a defensible ranking. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

The commercial comparison layouts live in [references/scoring-templates.md](references/scoring-templates.md). They are optional decision support, not the STAR Suitability rubric.

1. **Lock typed context.** Require the creator `target` and target version, named STAR profile/goal (`awareness|engagement|conversion|brand-building`), `assessment_time: forecast|actual`, shared campaign `rollup_id`, observation date, platform/tier/niche cohort, evidence window, material context object, and current STAR `catalog_version` — the exact typed identity the gate will reuse. If any field is absent, do not invent it: return `NEEDS_INPUT`, name the missing fields, and preserve the supplied identity unchanged for resume.
2. **Freeze evidence.** Use creator analytics, public observations, roster history, and cohort benchmarks with source/date/type/confidence. Missing or refused private access is Unknown, never Fail or Partial.
3. **Score Suitability only.** Evaluate the Suitability items `S1`–`S10` (audience composition/realness, follower-growth integrity, reach reliability, engagement health and authenticity, credibility, and portable brand/category fit) from [star-benchmark.md](../../../references/star-benchmark.md). Campaign-specific commercial terms and availability stay in the separate matrix; cost and measured campaign conversion belong to Return (R), scored later by the gate.
4. **Qualify critical-control evidence for handoff.** `STAR-S2` covers demonstrated follower fraud / real-follower rate below the matching tier × platform × niche benchmark; `STAR-S6` covers demonstrated bought, coordinated, or pod-based engagement. Brand safety is the gate's Trust control `STAR-T3`, not a Suitability item. Mark an item Fail only from qualifying evidence, label it a potential gate finding, and operationally hold outreach while it stands. Do not call it a verified veto or apply the SQS cap/business verdict here; the auditor owns those decisions when it rolls up the full STAR run.
5. **Record the Suitability read for the gate.** Capture the `S1`–`S10` states with source/date/type/confidence as the portable Suitability (S) read. The [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) gate folds this read into the full STAR run and runs the deterministic scorer for the profile-weighted SQS — this skill does not run the scorer or emit the SQS. Unknown means applicable evidence is missing and prevents a Suitability read; never soften Unknown to Partial or hand-calculate a composite.
6. **Build the separate commercial matrix when requested.** Use audience-to-campaign fit, content style, campaign-specific brand/category fit, commercial terms, availability, and partnership potential. Label its 1-5 total `commercial_fit_score`; it is not a Suitability score, cannot clear a Suitability veto, and never enters the SQS.
7. **Rank transparently.** Show the Suitability (S) read (or coverage/interval), critical controls, commercial fit separately, evidence confidence, and an outreach recommendation with owner/rerun condition. Do not rank an Unknown-heavy candidate as definitively superior.
8. **Persist only with permission.** Save the report only after authorization; request separate authorization before any hot-cache promotion or creator-registry proposal.

## Compact Example

**User**: "Compare @ecofashionista, @greenwardrobe, @sustainablesarah for our sustainable fashion brand (goal: conversion)."

**Output**: Each creator receives `S1`–`S10` item states under the same campaign `rollup_id`; a Suitability (S) read exists only at complete applicable coverage, while the separate commercial matrix explains campaign-specific terms and availability. A verified below-benchmark real-follower rate marks `STAR-S2` Fail and holds outreach; refused access stays Unknown and prevents the read. Only creator-content-auditor may apply the later STAR business verdict/cap. Persistence is offered, not assumed.

## Reference Materials

- [references/scoring-templates.md](references/scoring-templates.md) — all per-dimension tables, final-score rollup, comparison report, custom-weighting matrix, worked example, and tips.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Scoring rubric: [star-benchmark.md](../../../references/star-benchmark.md) — the STAR framework, the Suitability (S) dimension this skill reads (incl. the `STAR-S2`/`STAR-S6` veto items), and the profile-weighted SQS the gate computes.
- Sibling skills: [influencer-discovery](../influencer-discovery/SKILL.md), [competitor-tracker](../../target/competitor-tracker/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md), [outreach-manager](../../activate/outreach-manager/SKILL.md).

## Next Best Skill

**Primary**: [competitor-tracker](../../target/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already work with before you commit budget.

**Alternates** (same scout phase):
- [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) — when a complete Suitability read or potential `STAR-S2`/`STAR-S6`/`STAR-T3` control evidence is ready, stop and hand it to this sole STAR gate as a separate invocation; do not auto-run or simulate its verdict.
- [influencer-discovery](../influencer-discovery/SKILL.md) — if the shortlist is too thin to rank, source more candidates.
- [audience-mapper](../audience-mapper/SKILL.md) — if audience-match scores are uncertain, tighten the target-audience definition first.

**Termination note**: Track a visited-set of skills invoked this session. If the recommended next skill has already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops (max-depth 3) and hand back to the user with the saved report path.

## Related Skills

- [influencer-discovery](../influencer-discovery/SKILL.md) - Find influencers to score
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) - Benchmark against competitor partners
- [audience-mapper](../audience-mapper/SKILL.md) - Define target audience
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact top-scored influencers
