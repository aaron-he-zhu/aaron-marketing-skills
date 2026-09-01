<div align="center">

# Influencer — STAR

**Find, vet, activate, and measure creators — every partnership STAR-scored.**

English | [简体中文](README.zh.md)

</div>

> One discipline inside **[Aaron Marketing Skills](../README.md)** — 120 skills across seven disciplines on one contract. For the whole system, the four-layer map, and install steps, start at the [main README](../README.md).

Influencer is an **L2 · Channel** (episodic-leaning) — creator partnerships that borrow trusted voices to carry the brand narrative. Sixteen skills run the **STAR** loop — **S**cout the audience and the creators, **T**arget the shortlist and plan the program, **A**ctivate outreach and compliant content, then **R**eport the return. The creator roster and dossiers live in [`creator-registry`](../protocol/creator-registry/SKILL.md) (the influencer truth SSOT); the gate is [`creator-content-auditor`](activate/creator-content-auditor/SKILL.md). The loop and the quality framework now share the name **STAR** — symmetric with ROAS / SEND / ECHO / RAMP / TALE.

## The loop — Scout → Target → Activate → Report

- **Scout** — build the pool: profile the audience and its micro-community, read cultural timing, discover creators from scratch, and score shortlist fit (the Suitability read).
- **Target** — commit the plan: track competitors' creators, plan the campaign/program, generate standardized briefs, and allocate budget across tiers.
- **Activate** — go live safely: run outreach and negotiation, clear each submission through the STAR gate, handle contracts, and amplify/repurpose the content.
- **Report** — prove it worked: optimize creator/paid landing pages, analyze performance, calculate ROI, and write the stakeholder report.

> Note: **Activate** means *creator outreach* here — the same phase word means *account-gating* in the paid-ads discipline.

## The 16 skills

Links open each `SKILL.md`. ⛩ marks the discipline's auditor-class quality gate.

| Phase | Skill | What it does |
|-------|-------|--------------|
| **Scout** | [audience-mapper](scout/audience-mapper/SKILL.md) | Profile the target audience and map its subculture / micro-community before partnering with creators. |
| **Scout** | [trend-spotter](scout/trend-spotter/SKILL.md) | Campaign timing and themes — trending hashtags, sounds, formats, cultural moments. |
| **Scout** | [influencer-discovery](scout/influencer-discovery/SKILL.md) | Build a creator roster from scratch, expand to a new platform, source nano/micro at scale. |
| **Scout** | [fit-scorer](scout/fit-scorer/SKILL.md) | Objective, weighted fit score for a shortlist — produces the STAR **Suitability (S)** read. |
| **Target** | [competitor-tracker](target/competitor-tracker/SKILL.md) | A competitor's creators, campaigns, formats, estimated reach/spend, and gaps. |
| **Target** | [campaign-planner](target/campaign-planner/SKILL.md) | Plan a campaign, product launch, tentpole, or always-on creator program. |
| **Target** | [brief-generator](target/brief-generator/SKILL.md) | Standardized influencer briefs and reusable team templates. |
| **Target** | [budget-optimizer](target/budget-optimizer/SKILL.md) | Allocate spend across tiers/platforms, project ROI, model scenarios (also serves paid-ads spend + bid-pacing). |
| **Activate** | [outreach-manager](activate/outreach-manager/SKILL.md) | Pitch, follow-up cadence, re-engagement, rate negotiation, status tracking. |
| **Activate** | ⛩ [creator-content-auditor](activate/creator-content-auditor/SKILL.md) | Auditor-class STAR gate: pre-publish decision on a creator submission (STAR Trust — FTC disclosure STAR-T1, claim integrity STAR-T2), emits SQS + SHIP/FIX/BLOCK. |
| **Activate** | [contract-helper](activate/contract-helper/SKILL.md) | Draft/review creator agreements — usage rights, exclusivity, standard clauses. |
| **Activate** | [content-amplifier](activate/content-amplifier/SKILL.md) | Extend organic creator content with paid spend and repurpose UGC across paid, web, email, organic. |
| **Report** | [landing-optimizer](report/landing-optimizer/SKILL.md) | Landing pages for creator/paid traffic — message match, mobile, A/B (also serves paid post-click). |
| **Report** | [performance-analyzer](report/performance-analyzer/SKILL.md) | Evaluate creator results, compare creators, sentiment, conversions (also the paid cross-channel scorecard). |
| **Report** | [roi-calculator](report/roi-calculator/SKILL.md) | Measure/project ROI, defend budgets, value creators/tiers (shared return-math engine, incl. paid). |
| **Report** | [report-generator](report/report-generator/SKILL.md) | Written stakeholder reports after a period (also paid-ads reports). |

## Quality gate — STAR

[STAR](../references/star-benchmark.md) scores influencer marketing on four dimensions — **S**uitability · **T**rust · **A**ppeal · **R**eturn (40 items / 4 dimensions). **SQS = floor(profile-weighted mean)** — the same arithmetic rollup family as ROAS (RQS) and SEND (EQS). Veto items are `STAR-S2`/`S6` (audience authenticity) and `STAR-T1`/`T2`/`T3` (disclosure / claims / brand-safety) — always framework-qualified, since the IDs collide textually with SEND/ROAS/RAMP/TALE/CITE/CORE-EEAT. [`fit-scorer`](scout/fit-scorer/SKILL.md) produces the Suitability read at shortlist time; [`creator-content-auditor`](activate/creator-content-auditor/SKILL.md) is the pre-publish gate. Shared mechanics: [auditor-runbook.md](../references/auditor-runbook.md).

## Quick start

```text
/aaron-marketing:influencer              # infers the STAR phase from your input
/aaron-marketing:influencer --phase scout | target | activate | report
```

```text
/aaron-marketing:influencer find TikTok creators for a skincare launch and score their fit
```

Every skill runs at **Tier 1** with data you paste; connector reads are shortlist-vetting scope only.

## Recommended plays

| Your situation | Start here | What you get |
|---|---|---|
| Find creators for a launch | `/aaron-marketing:influencer --phase scout` → `influencer-discovery` → `fit-scorer` | A vetted roster + weighted Suitability scores |
| A creator sent their draft for approval | `--phase activate` → `creator-content-auditor` | STAR pre-publish verdict (FTC disclosure, claim integrity) |
| Is this shortlist actually a fit? | `fit-scorer` | An objective, weighted STAR Suitability read per creator |
| Did the program pay off? | `--phase report` → `roi-calculator` → `report-generator` | ROI math + a stakeholder report |
| What are competitors doing with creators? | `--phase target` → `competitor-tracker` | Their creators, formats, estimated reach/spend, and gaps |

## Shared with other disciplines

Influencer is the **home** of the reusable engine skills — several of its 16 do double duty elsewhere: [budget-optimizer](target/budget-optimizer/SKILL.md), [landing-optimizer](report/landing-optimizer/SKILL.md), [roi-calculator](report/roi-calculator/SKILL.md), [report-generator](report/report-generator/SKILL.md), and [performance-analyzer](report/performance-analyzer/SKILL.md) also serve paid ads; [audience-mapper](scout/audience-mapper/SKILL.md) and [trend-spotter](scout/trend-spotter/SKILL.md) also serve launch and social; [outreach-manager](activate/outreach-manager/SKILL.md) and [content-amplifier](activate/content-amplifier/SKILL.md) serve launch and social too. They are counted once, here.

## Connectors

Shortlist-vetting reads only: [`youtube.py`](../scripts/connectors/youtube.py) (free-key creator metrics — real subscriber/view counts; keyless `--rss` mode too), [`bluesky.py`](../scripts/connectors/bluesky.py) (creator profile + engagement + handle-squat audit), [`fediverse.py`](../scripts/connectors/fediverse.py), and [`tavily.py`](../scripts/connectors/tavily.py) (scored discovery search). Optional proprietary paths stay external: Upfluence is an opt-in remote MCP, NoxInfluencer an external Skill/CLI companion, and Scrumball a REST/API recipe pending authenticated shape verification. These providers supply evidence, not STAR verdicts; modeled audience, authenticity, rate, and ROI fields remain Estimated. Never bulk-harvest or mirror a provider corpus. Full list and approval boundaries: [CONNECTORS.md](../CONNECTORS.md).

---

<sub>Part of [Aaron Marketing Skills](../README.md) · [System architecture](../docs/system-architecture.md) · [STAR benchmark](../references/star-benchmark.md) · [Contributing](../CONTRIBUTING.md)</sub>
