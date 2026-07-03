---
name: fit-scorer
description: 'Use when the user asks to "score this influencer", "rank these creators for our campaign", or "tell me which influencer is the best fit"; produces weighted fit scores across audience match, content quality, brand alignment, engagement authenticity, and partnership potential, plus a ranked comparison and a go/pass verdict. Not for finding new influencers — use influencer-discovery; not for sending outreach — use outreach-manager.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when a user has a shortlist of influencers and needs an objective, weighted score to prioritize outreach, choose between candidates, justify a selection to stakeholders, set consistent evaluation standards, compare creators across niches or platforms, or build long-term partner tiers. Activates on requests like score @handle for our brand, compare and rank these creators, or which of these is the best fit."
argument-hint: "<brand or campaign> <influencer handle(s)> [campaign goal: awareness|engagement|conversion]"
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: discover
  family: influencer-marketing
  impact-phase: Map
---

# Fit Scorer

Objectively evaluate how well an influencer matches your brand by scoring them across five weighted dimensions, turning gut feel into a defensible go/pass decision.

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

- **Reads**: brand/campaign context, target audience definition, campaign goal, and a shortlist of influencer handles (supplied by the user or carried over from `influencer-discovery`). Optional prior audience profiles from `memory/influencer/audience-mapper/` and competitor partner benchmarks from `memory/influencer/competitor-tracker/`. For rostered creators, read partnership history and audience-stat provenance from `memory/creators/<handle-slug>.md` — the [creator-registry](../../protocol/creator-registry/SKILL.md) roster record — as Partnership Potential inputs.
- **Writes**: a fit-score report (per-dimension raw scores, weighted totals, verdict, ranked comparison) to `memory/influencer/fit-scorer/YYYY-MM-DD-<topic>.md`.
- **Promotes**: top-ranked handles, final scores, and the go/pass verdict to `memory/hot-cache.md` so downstream skills pick the right targets.
- **Done when**:
  - Every shortlisted influencer has a weighted total score on the 1-5 scale with per-dimension justifications.
  - A ranked comparison and an explicit verdict (Highly Recommended / Recommended / Consider / Pass) exist for each candidate.
  - The report is saved to the family memory path and top picks are promoted to the hot cache.
- **Primary next skill**: [competitor-tracker](../../plan/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already partner with.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

## Data Sources

This family needs no live integrations (Tier 1). Fit Scorer works end to end by asking the user for the inputs it scores — handles, audience targets, brand values, and any metrics they have. A connector sharpens the numbers but none is required.

- `~~influencer database` — follower counts, audience demographics, and partnership history.
- `~~social platform analytics` — engagement rate, comment quality samples, posting cadence, growth trend.
- `~~audience intelligence` — real-vs-bot follower estimates and audience overlap with your target.
- **Roster record (keyless Tier 1)** — prior contact, response reputation, and delivery history come from `memory/creators/<handle-slug>.md` when the creator is rostered ([creator-registry](../../protocol/creator-registry/SKILL.md) curates it); `~~CRM` is an optional Tier-2 sharpener for the same history when no roster record exists.

With zero integrations, ask the user to supply each value the scoring tables request; the framework and weighting still produce a defensible ranking. See [CONNECTORS.md](../../CONNECTORS.md) for the free/keyless recipe per category.

## Instructions

All fill-in tables and the comparison/report layouts live in [references/scoring-templates.md](references/scoring-templates.md) — copy the matching block for each step.

1. **Define the scoring framework.** Set the five dimensions, weights (default below; tune per goal via the custom-weighting matrix), and the 1-5 scale. Use the Step 1 template.

   **C³ ACE alignment & veto gate.** This skill is the C³ **Creator** scorer ([ACE](../../references/c3/ace-creator-benchmark.md)). Map dimensions onto ACE: Audience Match → **A**udience; Engagement Quality → **E**ngagement; the **Brand Safety** sub-check → **C**redibility (C1). Note: the value/aesthetic/messaging-fit part of Brand Alignment is *creator × brand fit*, which C³ scores in ROI.Orchestration (O1), **not** ACE — ACE is brand-independent, so keep brand-fit out of Credibility. Before ranking, screen every creator against the three ACE veto items; any failure is disqualifying → verdict **PASS (do not partner)** AND cap the Final Rating at the Poor / Below-Average band (**≤ 2.9 / 5**, i.e. ACE ≤ 59/100) so the score never contradicts the decline. State the veto ID + evidence:

   | Veto | Item | Fail condition |
   |------|------|----------------|
   | **A2** | Real-Follower Rate | < 70% real followers, or audit refused (follower fraud) |
   | **C1** | Brand Safety | disqualifying content / active scandal |
   | **E2** | Engagement Authenticity | pod / bought engagement |

2. **Score Audience Match** — target-vs-actual demographics plus audience quality (real/active/bot %). Step 2 template.
3. **Score Content Quality** — production value, cadence, content mix, best examples, concerns. Step 3 template.
4. **Score Brand Alignment** — value/aesthetic/messaging fit and the Brand Safety check (feeds ACE C1). Step 4 template.
5. **Score Engagement Quality** — engagement rate vs industry avg, authenticity indicators, pod/buying signs (feeds ACE E2). Step 5 template.
6. **Score Partnership Potential** — partnership history, professionalism, exclusivity/availability, estimated value; pull prior-partnership and response-history facts from the `memory/creators/` roster record when one exists. Step 6 template.
7. **Calculate the final score** — roll raw × weight into the weighted total, apply the interpretation band, write the verdict and expected performance. Step 7 template.
8. **For multiple influencers**, produce the ranking summary, dimension-by-dimension comparison, and prioritize/combine/pass recommendation. Step 8 template.

Save the report to `memory/influencer/fit-scorer/YYYY-MM-DD-<topic>.md` and promote top picks + verdict to `memory/hot-cache.md`.

## Compact Example

**User**: "Compare @ecofashionista, @greenwardrobe, @sustainablesarah for our sustainable fashion brand (goal: conversion)."

**Output**: Each scored across the five dimensions with conversion weighting (Audience 35%, Brand 20%). @sustainablesarah ranks #1 (4.4/5) on highest audience match and authentic engagement; @greenwardrobe flagged DONE_WITH_CONCERNS on a borderline real-follower rate (A2 watch); ranked comparison + go/pass verdicts saved, top pick promoted to hot cache.

## Reference Materials

- [references/scoring-templates.md](references/scoring-templates.md) — all per-dimension tables, final-score rollup, comparison report, custom-weighting matrix, worked example, and tips.
- [skill-contract.md](../../references/skill-contract.md) — shared contract and handoff summary format.
- [state-model.md](../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — free/keyless data recipe per connector category.
- Scoring rubric: [c3-benchmark.md](../../references/c3-benchmark.md) (CVI rollup), [c3/ace-creator-benchmark.md](../../references/c3/ace-creator-benchmark.md) (the ACE Creator rubric this skill emits, incl. A2/C1/E2 veto items), [c3/scoring-architecture.md](../../references/c3/scoring-architecture.md) (weighting and cap methodology).
- Sibling skills: [influencer-discovery](../../discover/influencer-discovery/SKILL.md), [competitor-tracker](../../plan/competitor-tracker/SKILL.md), [audience-mapper](../../discover/audience-mapper/SKILL.md), [outreach-manager](../../activate/outreach-manager/SKILL.md).

## Next Best Skill

**Primary**: [competitor-tracker](../../plan/competitor-tracker/SKILL.md) — benchmark your top-scored picks against the creators competitors already work with before you commit budget.

**Alternates** (same Map phase):
- [influencer-discovery](../../discover/influencer-discovery/SKILL.md) — if the shortlist is too thin to rank, source more candidates.
- [audience-mapper](../../discover/audience-mapper/SKILL.md) — if audience-match scores are uncertain, tighten the target-audience definition first.

**Termination note**: Track a visited-set of skills invoked this session. If the recommended next skill has already run, stop and report the chain complete rather than re-invoking it. Stop after at most 3 hops (max-depth 3) and hand back to the user with the saved report path.

## Related Skills

- [influencer-discovery](../../discover/influencer-discovery/SKILL.md) - Find influencers to score
- [competitor-tracker](../../plan/competitor-tracker/SKILL.md) - Benchmark against competitor partners
- [audience-mapper](../../discover/audience-mapper/SKILL.md) - Define target audience
- [outreach-manager](../../activate/outreach-manager/SKILL.md) - Contact top-scored influencers
