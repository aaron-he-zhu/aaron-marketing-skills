---
name: fit-scorer
slug: fit-scorer
displayName: "Fit Scorer · 红人适配评分"
summary: "用 typed STAR 适配度(S) 维度评估创作者，并将活动商业适配度作为独立矩阵排序"
description: 'Use when the user asks to "score this influencer", "rank these creators for our campaign", or "tell me which influencer is the best fit"; produces the typed STAR Suitability (S) read plus a separately labeled campaign-fit ranking without mixing campaign-specific commercial fit into the Suitability read. Not for finding new influencers — use influencer-discovery; not for sending outreach — use outreach-manager. 达人适配度评分/创作者筛选排名'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a user has a shortlist of influencers and needs an objective, weighted score to prioritize outreach, choose between candidates, justify a selection to stakeholders, set consistent evaluation standards, compare creators across niches or platforms, or build long-term partner tiers. Activates on requests like score @handle for our brand, compare and rank these creators, or which of these is the best fit."
argument-hint: "<brand or campaign> <influencer handle(s)> [campaign goal: awareness|engagement|conversion]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "scout", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "scout"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Fit Scorer

Score each shortlisted creator on the typed STAR **Suitability (S)** dimension, then keep deal-specific commercial fit in a separate prioritization matrix. Suitability includes the `STAR-S8` brand/category and audience-brand evidence that is independent of any single deal; deal terms, availability, and campaign orchestration stay outside it. The commercial matrix is not a Suitability score and never enters the SQS.

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

- **Reads**: brand/campaign context, target audience definition, campaign goal, and shortlist entries carrying a stable opaque `creator_ref` plus either transient handles/profile URLs or resolvable opaque handle refs (supplied by the user or carried over from `influencer-discovery`). Optional prior audience profiles from `memory/influencer/audience-mapper/`, competitor partner benchmarks from `memory/influencer/competitor-tracker/`, and a WARM Campaign Retro Card's `evidence_refs` plus `next_campaign_hypothesis` when the user supplies or authorizes that handoff. For rostered creators, read partnership history and audience-stat provenance from `memory/creators/<aggregate-id>.md` — the [creator-registry](../../../protocol/creator-registry/SKILL.md) roster record — as Partnership Potential inputs.
- **Writes**: return the typed Suitability (S) read and separately labeled commercial-fit comparison inline by default; when a Retro Card is supplied, preserve its hypothesis as a separately labeled next-cycle test constraint with no score or verdict effect. Save the report to `memory/influencer/fit-scorer/YYYY-MM-DD-<topic>.md` only with exact WARM-save authorization. Saved reports and handoffs retain the stable opaque `creator_ref` and opaque evidence refs, never a raw handle, name, profile URL, email, provider ID, or deterministic hash in `creator_ref`.
- **Promotes**: only with separate exact authorization, promote evidence-backed top picks and their exact Suitability (S) read and catalog version to `memory/hot-cache.md`; never promote an unscored/provisional result or the Retro Card's qualitative decision/hypothesis as scored truth.
- **Done when**:
  - Every creator has all 10 Suitability items `S1`–`S10` explicitly Pass/Partial/Fail/Unknown/N/A with dated evidence or a gap reason.
  - Every creator's stable opaque `creator_ref` is preserved from discovery/registry or generated once for this lineage; raw identity locators remain transient.
  - The typed goal/context and the Suitability item states are preserved for the gate; Unknown prevents a Suitability read.
  - Any commercial-fit ranking is visibly separate from the Suitability read and cannot override a veto or missing evidence.
  - If a Retro Card is supplied, its `next_campaign_hypothesis` is visible only as a falsifiable test constraint/commercial-matrix context; its `evidence_refs` are pointers for fresh investigation, not STAR item evidence or an automatic selection rule.
- **Primary next skill**: [campaign-planner](../../target/campaign-planner/SKILL.md) — turn the ranked shortlist into an approved campaign plan. If that plan is already approved and outreach-ready, hand off to [outreach-manager](../../activate/outreach-manager/SKILL.md) instead; competitor benchmarking is optional.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). Fit Scorer works end to end by asking the user for the inputs it scores — transient handles or profile locators, audience targets, brand values, and any metrics they have. A connector sharpens the numbers but none is required.

- `~~influencer database` — follower counts, audience demographics, and partnership history.
- `~~social platform analytics` — engagement rate, comment quality samples, posting cadence, growth trend.
- `~~audience intelligence` — real-vs-bot follower estimates and audience overlap with your target.
- **Roster record (keyless Tier 1)** — prior contact, response reputation, and delivery history come from `memory/creators/<aggregate-id>.md` when the creator is rostered ([creator-registry](../../../protocol/creator-registry/SKILL.md) curates it); `~~CRM` is an optional Tier-2 sharpener for the same history when no roster record exists.

**Measured YouTube inputs (free key)**: for YouTube candidates, `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/youtube.py" videos @handle --limit 10` supplies the engagement-authenticity inputs directly — per-video views/likes/comments against the displayed subscriber base (views-to-subs consistency, comment rate, cadence) — so those sub-scores come from **Measured** numbers instead of screenshots. Free `YOUTUBE_API_KEY`; shortlist vetting only (ToS refuses bulk-harvesting quota). See [scripts/connectors/README.md](../../../scripts/connectors/README.md).

With zero integrations, ask the user to supply each value the scoring tables request; the framework and weighting still produce a defensible ranking. See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

The contract-compatible copied layouts live in [references/scoring-templates.md](references/scoring-templates.md): use the `creator_ref`-only typed `STAR-S1`–`STAR-S10` evidence table for the Suitability read, then the optional `commercial_fit_score` tables for separate decision support. Never copy a raw locator into those outputs.

1. **Lock identity and typed context.** Reuse the opaque `creator_ref` explicitly carried by discovery, or a creator-registry aggregate ID only when its handle link is verified. If the user supplies only a raw handle/profile URL and no verified aggregate exists, generate one random `creator-<UUIDv4>` and reuse it unchanged across this report, any authorized save, and downstream handoffs. Never set `creator_ref` to a raw handle, name, URL, email, provider ID, or deterministic hash of one; keep those locators transient for evidence acquisition. Resolve an opaque ref only through its accompanying authorized artifact or verified registry link. If neither is available, request the transient locator and preserve the identity as unresolved rather than guessing or merging. Then require the creator `target` and target version, named STAR profile/goal (`awareness|engagement|conversion|brand-building`), `assessment_time: forecast|actual`, shared campaign `rollup_id`, observation date, platform/tier/niche cohort, evidence window, material context object, and current STAR `catalog_version` — the exact typed identity the gate will reuse. If any field is absent, do not invent it: return `NEEDS_INPUT`, name the missing fields, and preserve the supplied identity unchanged for resume. When a Campaign Retro Card is supplied, record its `evidence_refs` and `next_campaign_hypothesis` in a separate non-scoring prior-cycle context block; neither becomes part of the STAR typed identity.
2. **Freeze evidence for the current window.** Use current creator analytics, public observations, roster history, and cohort benchmarks with source/date/type/confidence. A Retro Card and its `evidence_refs` are discovery pointers only, never STAR item evidence. If a referenced primary source is independently reacquired and qualifies in the current evidence window, cite that fresh observation rather than the card. Missing or refused private access is Unknown, never Fail or Partial.
3. **Score Suitability only.** Evaluate the Suitability items `S1`–`S10` (audience composition/realness, follower-growth integrity, reach reliability, engagement health and authenticity, credibility, and deal-independent brand/category fit) from [star-benchmark.md](../../../references/star-benchmark.md). Deal-specific commercial terms, availability, and orchestration conflicts stay in the separate matrix; cost and measured campaign conversion belong to Return (R), scored later by the gate.
4. **Qualify critical-control evidence for handoff.** `STAR-S2` covers demonstrated follower fraud / real-follower rate below the matching tier × platform × niche benchmark; `STAR-S6` covers demonstrated bought, coordinated, or pod-based engagement. Brand safety is the gate's Trust control `STAR-T3`, not a Suitability item. Mark an item Fail only from qualifying evidence, label it a potential gate finding, and operationally hold outreach while it stands. Do not call it a verified veto or apply the SQS cap/business verdict here; the auditor owns those decisions when it rolls up the full STAR run.
5. **Record the Suitability read for the gate.** Capture every `S1`–`S10` state as exactly Pass/Partial/Fail/Unknown/N/A with source/date/window/type/confidence or an explicit gap/N/A reason under the locked brand/category/cohort context. This typed table—not any 1–5 aid—is the Suitability read. The [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) gate folds it into the full STAR run and runs the deterministic scorer for the profile-weighted SQS; this skill does not run the scorer or emit the SQS. Unknown means applicable evidence is missing and prevents a complete Suitability read; never soften Unknown to Partial or hand-calculate a composite.
6. **Build the separate commercial matrix when requested.** Use deal-specific audience/goal nuance, content concept, brand conflicts, commercial terms, availability, and partnership potential. A supplied `next_campaign_hypothesis` may appear beside the matrix as a falsifiable test constraint, but contributes zero points and no weight. Label every 1–5 component and its rollup `commercial_fit_score`; never call one “Fit Score” or “Final Score.” It is not a Suitability score, cannot clear a Suitability control finding, and never enters the SQS.
7. **Rank transparently.** Show the typed Suitability read, critical controls, `commercial_fit_score` separately, evidence confidence, and an action tied to the declared rule with owner/rerun condition. Do not emit a generic Verdict or star rating. Route to `campaign-planner` by default; route to `outreach-manager` only when an approved campaign plan is already ready for execution. Offer competitor benchmarking as an optional check, not a mandatory detour. Do not rank an Unknown-heavy candidate as definitively superior, add/subtract points because a Retro hypothesis names a creator or tactic, or automatically select a candidate from a prior-cycle `renew | retest | retire | unknown` decision.
8. **Persist only with permission.** Save the report only after exact WARM authorization; request separate authorization before any hot-cache promotion. Persist and hand off `creator_ref` plus opaque handle/evidence refs, not the transient raw identity locator. The Retro hypothesis remains WARM working context. This skill does not propose provisional commercial rankings or non-gate Suitability results to `creator-registry`.

## Compact Example

**User**: "Compare @ecofashionista, @greenwardrobe, @sustainablesarah for our sustainable fashion brand (goal: conversion)."

**Output**: Each creator reuses an upstream opaque `creator_ref` or receives one random `creator-<UUIDv4>` before scoring; the raw handles remain transient lookup inputs. Each creator then receives `S1`–`S10` item states under the same campaign `rollup_id`; a Suitability (S) read exists only at complete applicable coverage, while the separate commercial matrix explains campaign-specific terms and availability. If a prior Retro Card is supplied, its hypothesis appears only as a zero-weight next-cycle test constraint and its sources are re-observed in the current window. A verified below-benchmark real-follower rate marks `STAR-S2` Fail and holds outreach; refused access stays Unknown and prevents the read. Only creator-content-auditor may apply the later STAR business verdict/cap. Persistence is offered, not assumed.

## Reference Materials

- [references/scoring-templates.md](references/scoring-templates.md) — typed Suitability evidence table plus separate `commercial_fit_score` component/rollup, comparison, custom-weighting, worked-example, and partial-state layouts.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff summary format.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Scoring rubric: [star-benchmark.md](../../../references/star-benchmark.md) — the STAR framework, the Suitability (S) dimension this skill reads (incl. the `STAR-S2`/`STAR-S6` veto items), and the profile-weighted SQS the gate computes.
- Sibling skills: [influencer-discovery](../influencer-discovery/SKILL.md), [competitor-tracker](../../target/competitor-tracker/SKILL.md), [audience-mapper](../audience-mapper/SKILL.md), [outreach-manager](../../activate/outreach-manager/SKILL.md).

## Next Best Skill

**Primary**: [campaign-planner](../../target/campaign-planner/SKILL.md) — turn the ranked shortlist into the campaign plan, budget, timeline, and approval path.

**Conditional next step**:
- [outreach-manager](../../activate/outreach-manager/SKILL.md) — only when an approved campaign plan already defines the offer, budget, target creator, channel, and outreach approval path; this handoff does not authorize a send.

**Optional checks and alternates**:
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) — optionally benchmark top picks against competitor partnerships when that evidence would change the selection.
- [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) — when a complete Suitability read or potential `STAR-S2`/`STAR-S6`/`STAR-T3` control evidence is ready, stop and hand it to this sole STAR gate as a separate invocation; do not auto-run or simulate its verdict.
- [influencer-discovery](../influencer-discovery/SKILL.md) — if the shortlist is too thin to rank, source more candidates.
- [audience-mapper](../audience-mapper/SKILL.md) — if audience-match scores are uncertain, tighten the target-audience definition first.

**Termination note**: Track a visited-set of skills invoked this session. If the recommended next skill has already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops (max-depth 3) and hand back the inline result plus any separately authorized save path.

## Related Skills

- [influencer-discovery](../influencer-discovery/SKILL.md) - Find influencers to score
- [competitor-tracker](../../target/competitor-tracker/SKILL.md) - Benchmark against competitor partners
- [audience-mapper](../audience-mapper/SKILL.md) - Define target audience
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact top-scored influencers
