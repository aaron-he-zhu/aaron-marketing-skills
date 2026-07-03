# Aaron Marketing Skills

**69 skills. 5 commands. Four marketing disciplines — SEO/GEO, influencer, paid ads, email — on one operating contract.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat)](https://github.com/aaron-he-zhu/aaron-marketing-skills)
[![Version](https://img.shields.io/badge/version-12.0.0-orange)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills)](https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-compatible-purple)](https://claude.ai/download)

[English](README.md) | [中文](docs/README.zh.md)

A library of Claude Skills and slash commands that turns a chat agent into a marketing operator. Four disciplines and a shared protocol layer, at a glance:

| Layer | Skills | Lifecycle (phase directories) | Framework → gate | Entrypoint |
|-------|--------|-------------------------------|------------------|------------|
| **SEO/GEO** | 16 | research → build → optimize → monitor | [CORE-EEAT](references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Influencer (IMPACT)** | 16 | discover → plan → activate → measure | [C³](references/c3-benchmark.md) → `content-reviewer` (ART); `fit-scorer` scores ACE | `/aaron-marketing:impact` |
| **Paid ads (ROAS)** | 16 | research → orchestrate → activate → scale | [ROAS](references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:paid` |
| **Email (SEND)** | 16 | setup → engage → nurture → deliver | [SEND](references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Protocol layer** | 5 | — (shared machinery, outside the phase flows) | 4 truth registries (entity · creator · offer/claims · consent) + HOT/WARM/COLD memory | — |

`/aaron-marketing:auto` routes any natural-language goal across all of it. Everything is **plain Markdown** — the only code is a Bash hook runner, a Bash validator, and zero-dependency Python-stdlib data helpers (no `pip`, no build step). **Every skill runs at Tier 1 with nothing but data you paste in**; connectors only automate retrieval.

> The SEO/GEO half also ships on its own, unchanged, at [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) for users who only want SEO/GEO work.

---

## Contents

- [Why this library](#why-this-library)
- [Install](#install)
- [First run](#first-run)
- [Architecture](#architecture)
  - [The shared skill contract](#the-shared-skill-contract)
  - [One lifecycle, four dialects](#one-lifecycle-four-dialects)
  - [Quality system: five frameworks, five gates](#quality-system-five-frameworks-five-gates)
  - [The protocol layer](#the-protocol-layer)
  - [Memory & automation hooks](#memory--automation-hooks)
- [Skill catalog](#skill-catalog)
  - [SEO/GEO (16)](#seogeo-16)
  - [Influencer — IMPACT (16)](#influencer--impact-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Protocol layer (5)](#protocol-layer-5)
- [Commands](#commands)
- [Connectors & enhancement tiers](#connectors--enhancement-tiers)
- [Recommended workflows](#recommended-workflows)
- [Repository layout](#repository-layout)
- [Design philosophy](#design-philosophy)
- [Quality guards (CI)](#quality-guards-ci)
- [Contributing & project docs](#contributing--project-docs)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Why this library

| Principle | What it means in practice |
|-----------|---------------------------|
| **Keyless by default** | Every skill works at **Tier 1** with data you paste or pull from free/first-party sources. Paid tools and MCP servers are an opt-in convenience, never a precondition. Paid-ads skills score from your **own-account manual export** — keyed ad APIs are never required. |
| **Markdown, not a framework** | Skills are content. The only executable code is `hooks/claude-hook.sh` (Bash), `scripts/validate-skill.sh` (Bash), and `scripts/connectors/*.py` (Python **standard library only**). Nothing to install, audit, or keep up to date. |
| **One shared contract** | All 69 skills expose the same seven sections and self-declare `discipline` + `phase` metadata, so the library behaves like one operating system: each skill knows its inputs, outputs, and the next best skill to hand off to. |
| **Gated quality** | Five benchmarks drive five auditor-class gates that emit structured, machine-checkable verdicts — not vibes. A PostToolUse hook validates every gated artifact before it lands. |
| **Truth lives in registries** | Canonical facts (brand entities, creator dossiers, offer/claim substantiation, per-subject consent) live in dedicated protocol-layer registries with sole-writer rules — gates judge against them instead of re-deriving them. |
| **Memory across turns** | A HOT/WARM/COLD memory model carries findings, scores, and open loops between skills and sessions, sanitized on the way in. |
| **Plain voice** | Skills ship an AI-slop detector and a banned-phrase list so output reads like a human wrote it. |

---

## Install

Use it with Claude Code, any Agent Skills-compatible host, or a plain `git clone`:

| Host | Install |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` then `/plugin install aaron-marketing@aaron` |
| **skills.sh / generic Agent Skills hosts** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Any host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

In Claude Code, `marketplace add` only registers the catalog — run `/plugin install aaron-marketing@aaron` (or pick it from `/plugin`) to actually enable the skills and commands. To pull a **single** skill on a generic host: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`.

Installing the plugin adds **nothing** to your `/mcp` list — the MCP catalogue lives in [`docs/mcp-catalog.json`](docs/mcp-catalog.json), deliberately outside the plugin-root `.mcp.json` path that Claude Code auto-registers, so it is a copy-paste reference only (see [Connectors](#connectors--enhancement-tiers)).

---

## First run

If your host supports automatic skill routing, just describe the goal:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Or use the slash commands — `/auto` for routing, or a discipline entrypoint:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --mode audit
```

`/aaron-marketing:auto` infers intent and runs the smallest useful workflow, stopping only at blocking decisions. Every skill works with pasted data; optional tools are documented in [CONNECTORS.md](CONNECTORS.md).

---

## Architecture

### The shared skill contract

Every skill follows the **same activation contract** — seven sections in a fixed order:

1. **Trigger / when-to-use** — when the skill should fire.
2. **Quick Start** — copy-paste prompts.
3. **Skill Contract** — Expected output · Reads · Writes · Promotes · Done-when · Primary next skill.
4. **Handoff Summary** — the standard hand-off shape so the next skill picks up cleanly.
5. **Data Sources** — `~~category` placeholders, each with a keyless Tier-1 path.
6. **Instructions** — the numbered method (treats all exports as untrusted input).
7. **Next Best Skill** — where to go next (with visited-set + max-depth termination rules).

Every skill also self-declares `metadata.discipline` (seo-geo / influencer / paid / protocol) and `metadata.phase`, so routing and clustering work uniformly. The contract is documented once in [skill-contract.md](references/skill-contract.md); the shared cross-skill state lives in [state-model.md](references/state-model.md).

### One lifecycle, four dialects

The four disciplines share one meta-lifecycle spine; each adapts the granularity to its own workflow (phase *counts* differ by design):

| Meta-stage | SEO/GEO | Influencer (IMPACT) | Paid (ROAS) | Email (SEND) |
|------------|---------|---------------------|-------------|--------------|
| **Understand** | research | discover | research | setup |
| **Plan / create** | build | plan | orchestrate | engage |
| **Activate / optimize** | optimize | activate | activate | nurture |
| **Measure** | monitor | measure | scale | deliver |

All four use phase **directories** (`research/`…, `discover/`…, `paid/research/`…, `email/setup/`…). Note "activate" means creator outreach in IMPACT but account-gating in ROAS — same word, discipline-specific scope.

### Quality system: five frameworks, five gates

Five benchmarks make "good" measurable. Each defines dimensions, a rollup method, and a small set of **veto items** (hard fails that cap or block a score regardless of the rest):

| Framework | Scores | Items / dimensions | Rollup | Veto items |
|-----------|--------|--------------------|--------|------------|
| **[CORE-EEAT](references/core-eeat-benchmark.md)** | Content quality (GEO = CORE avg, SEO = EEAT avg) | 80 items / 8 dimensions | per-dimension averages | `T04`, `C01`, `R10` |
| **[CITE](references/cite-domain-rating.md)** | Domain authority & citation trust | 40 items / 4 dimensions | arithmetic weighted mean | `T03`, `T05`, `T09` |
| **[C³](references/c3-benchmark.md)** | Influencer Creator / Content / Campaign | ACE / ART / ROI · 9 dimensions | **CVI = (ACE × ART × ROI)^⅓** (geometric) | ACE `A2`/`C1`/`E2`, ART `T1`/`T2` |
| **[ROAS](references/roas-benchmark.md)** | Paid ads Return / Offer / Audience / Spend-efficiency | R / O / A / S | **RQS = floor(goal-weighted mean)** (arithmetic) | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](references/send-benchmark.md)** | Email marketing Sender-integrity / Engagement / Nurture / Direct-response | S / E / N / D | **EQS = floor(goal-weighted mean)** (arithmetic) | `S1`/`S2`/`N1`/`D1` |

Each framework is enforced by an **auditor-class gate** — a skill that writes a gated artifact (`class: auditor-output`) validated by the PostToolUse hook. Gates are workflow steps, so each lives in its discipline and is counted there:

| Gate | Framework | Lives in | Verdict |
|------|-----------|----------|---------|
| [content-quality-auditor](optimize/content-quality-auditor/SKILL.md) | CORE-EEAT | `optimize/` (SEO/GEO) | SHIP / FIX / BLOCK before publishing |
| [domain-authority-auditor](monitor/domain-authority-auditor/SKILL.md) | CITE | `monitor/` (SEO/GEO) | TRUSTED / CAUTIOUS / UNTRUSTED |
| [content-reviewer](activate/content-reviewer/SKILL.md) | C³ ART | `activate/` (influencer) | APPROVED / REVISIONS / REJECTED before a creator post ships |
| [ad-account-auditor](paid/activate/ad-account-auditor/SKILL.md) | ROAS RQS | `paid/activate/` (paid) | SHIP / FIX / BLOCK before budgets scale |
| [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md) | SEND EQS | `email/deliver/` (email) | SHIP / FIX / BLOCK before send |

**Shared cap chassis:** a single veto caps the affected dimension and the overall at `min(raw, 60)`; **two or more vetoes → `BLOCKED`** (no final score). Verdicts are translated to plain language (no item IDs in user-facing reports). Gate mechanics — handoff schema, cap arithmetic, artifact-gate checklist — are specified once in [auditor-runbook.md](references/auditor-runbook.md), and the arithmetic of all five frameworks is locked by a deterministic golden test (see [Quality guards](#quality-guards-ci)).

### The protocol layer

The `protocol/` directory holds the **shared truth & memory machinery** that sits outside the discipline phase-flows — 5 skills, counted separately:

| Skill | Job | Anchored to | Canonical store |
|-------|-----|-------------|-----------------|
| [entity-optimizer](protocol/entity-optimizer/SKILL.md) | Canonical brand/entity profile (Knowledge Graph, Wikidata, AI disambiguation) | SEO/GEO | `memory/entities/` |
| [creator-registry](protocol/creator-registry/SKILL.md) | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history | influencer | `memory/creators/` |
| [offer-claims-registry](protocol/offer-claims-registry/SKILL.md) | Offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against | paid | `memory/claims/` |
| [consent-registry](protocol/consent-registry/SKILL.md) | Canonical per-subject consent/suppression record — the S2/N1 vetoes judge against it | email | `memory/consent/` |
| [memory-management](protocol/memory-management/SKILL.md) | HOT/WARM/COLD memory lifecycle (capture · promote · demote · archive · query) | all disciplines | `memory/` |

The registries follow a **sole-writer rule** (other skills submit via `candidates.md`), and they *curate* — the gates *judge*. The genuinely horizontal layer beneath everything is the `references/` protocols ([auditor-runbook](references/auditor-runbook.md), [state-model](references/state-model.md), [skill-contract](references/skill-contract.md), [humanizer-slop](references/humanizer-slop.md), [measurement-protocol](references/measurement-protocol.md)) — shared by design as documents, not skills.

### Memory & automation hooks

**Memory** is temperature-tiered, so context survives across skills and sessions without bloating the prompt:

| Tier | Location | Behavior |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Auto-loaded each session; capped at **80 lines AND 25 KB** (whichever trips first). |
| **WARM** | `memory/<subdir>/` | Per-skill working state, gated audit artifacts (`memory/audits/`), and the registries' canonical stores (`memory/entities\|creators\|claims/`). |
| **COLD** | `memory/archive/` | Demoted/older records, kept for recall. |

**Hooks** (`hooks/hooks.json`, runner `hooks/claude-hook.sh`) wire four Claude Code events:

| Event | Matcher | What it does |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Injects the **sanitized** hot-cache + an open-loops pointer (prompt-injection lines are redacted; symlinked caches are rejected). |
| `UserPromptSubmit` | (all) | Lightweight per-prompt context hook. |
| `PostToolUse` | `Write\|Edit` | Hot-cache size warning **+ the Artifact Gate**: any file under `memory/audits/` that declares `class: auditor-output` is validated against the handoff schema and cap fields, or the write is blocked. The five auditor-class gates must declare that marker by contract; unmarked files are not auditor artifacts and pass through. |
| `Stop` | (all) | No-op (exits silently). |

The Artifact Gate is **framework-agnostic** — the same hook validates CORE-EEAT, CITE, C³, ROAS, and SEND artifacts with no per-framework code.

---

## Skill catalog

Skill links open each `SKILL.md`. Expand the **Details** under each discipline for a one-line purpose per skill.

### SEO/GEO (16)

Four phase directories (4 skills each) plus the discipline's two quality gates (marked ⛩).

| Phase | Skills |
|-------|--------|
| **Research** | [keyword-research](research/keyword-research/SKILL.md), [competitor-analysis](research/competitor-analysis/SKILL.md), [serp-analysis](research/serp-analysis/SKILL.md), [content-gap-analysis](research/content-gap-analysis/SKILL.md) |
| **Build** | [content-writer](build/content-writer/SKILL.md), [geo-content-optimizer](build/geo-content-optimizer/SKILL.md), [serp-markup-builder](build/serp-markup-builder/SKILL.md), [page-play-builder](build/page-play-builder/SKILL.md) |
| **Optimize** | ⛩ [content-quality-auditor](optimize/content-quality-auditor/SKILL.md), [technical-seo-checker](optimize/technical-seo-checker/SKILL.md), [on-page-seo-auditor](optimize/on-page-seo-auditor/SKILL.md), [site-structure-optimizer](optimize/site-structure-optimizer/SKILL.md) |
| **Monitor** | ⛩ [domain-authority-auditor](monitor/domain-authority-auditor/SKILL.md), [rank-tracker](monitor/rank-tracker/SKILL.md), [performance-monitor](monitor/performance-monitor/SKILL.md), [offsite-signal-analyzer](monitor/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Per-skill purpose (SEO/GEO)</b></summary>

| Skill | What it does |
|-------|--------------|
| keyword-research | Start keyword work for a page/topic/campaign — intent, demand, and striking-distance opportunities. |
| competitor-analysis | Analyze a competitor's SEO strategy, compare domains, surface their keywords and gaps. |
| serp-analysis | Read a SERP — features, snippets, People Also Ask, ranking patterns for a query. |
| content-gap-analysis | Find missing topics and coverage holes versus competitors. |
| content-writer | *(merge: seo-content-writer + content-refresher)* Write and refresh SEO-optimized articles, landing pages, and product copy. |
| geo-content-optimizer | Optimize content for AI engines (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | *(merge: meta-tags-optimizer + schema-markup-generator)* Title/meta/OG/Twitter tags plus JSON-LD / Schema.org structured data. |
| page-play-builder | *(merge: programmatic + parasite + comparison + local SEO, 4 modes)* Template-driven page plays — programmatic pages, parasite platforms, comparison pages, local/GBP. |
| ⛩ content-quality-auditor | 80-item CORE-EEAT publish-readiness gate (SHIP/FIX/BLOCK). |
| technical-seo-checker | Site speed, Core Web Vitals, indexing, crawlability, robots. |
| on-page-seo-auditor | Audit page-level on-page health — headings, keyword placement, images, quality signals. |
| site-structure-optimizer | *(merge: internal-linking-optimizer + site-architecture)* Internal links, anchor-text, orphan pages, page hierarchy, URL taxonomy, hub/spoke clusters. |
| ⛩ domain-authority-auditor | 40-item CITE domain-trust gate (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Track keyword rankings, position changes, and drops. |
| performance-monitor | *(merge: performance-reporter + alert-manager)* Multi-metric SEO/GEO reports, dashboards, and threshold alerts. |
| offsite-signal-analyzer | *(merge: backlink-analyzer + ai-traffic)* Backlink profile + link quality, plus referral traffic from AI assistants in your own GA4/GSC/logs. |

</details>

### Influencer — IMPACT (16)

Four phase directories (4 skills each); the discipline's gate (⛩ content-reviewer) sits in Activate.

| Phase | Skills |
|-------|--------|
| **Discover** | [audience-mapper](discover/audience-mapper/SKILL.md), [trend-spotter](discover/trend-spotter/SKILL.md), [influencer-discovery](discover/influencer-discovery/SKILL.md), [fit-scorer](discover/fit-scorer/SKILL.md) |
| **Plan** | [competitor-tracker](plan/competitor-tracker/SKILL.md), [campaign-planner](plan/campaign-planner/SKILL.md), [brief-generator](plan/brief-generator/SKILL.md), [budget-optimizer](plan/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](activate/outreach-manager/SKILL.md), ⛩ [content-reviewer](activate/content-reviewer/SKILL.md), [contract-helper](activate/contract-helper/SKILL.md), [content-amplifier](activate/content-amplifier/SKILL.md) |
| **Measure** | [landing-optimizer](measure/landing-optimizer/SKILL.md), [performance-analyzer](measure/performance-analyzer/SKILL.md), [roi-calculator](measure/roi-calculator/SKILL.md), [report-generator](measure/report-generator/SKILL.md) |

<details><summary><b>Per-skill purpose (Influencer)</b></summary>

| Skill | What it does |
|-------|--------------|
| audience-mapper | *(merge: audience-analyzer + niche-researcher)* Profile the target audience and map its subculture / micro-community before partnering with creators. |
| trend-spotter | Campaign timing and themes — trending hashtags, sounds, formats, cultural moments. |
| influencer-discovery | Build a creator roster from scratch, expand to a new platform, source nano/micro at scale. |
| fit-scorer | Objective, weighted fit score for a shortlist (scored on C³ ACE). |
| competitor-tracker | A competitor's creators, campaigns, formats, estimated reach/spend, and gaps. |
| campaign-planner | Plan a campaign, product launch, tentpole, or always-on creator program. |
| brief-generator | Standardized influencer briefs and reusable team templates. |
| budget-optimizer | Allocate spend across tiers/platforms, project ROI, model scenarios (also serves paid-ads spend + bid-pacing). |
| outreach-manager | Pitch, follow-up cadence, re-engagement, rate negotiation, status tracking. |
| ⛩ content-reviewer | Pre-publish gate decision on a creator submission (C³ ART: FTC disclosure T1, claim integrity T2). |
| contract-helper | Draft/review creator agreements — usage rights, exclusivity, standard clauses. |
| content-amplifier | *(merge: content-amplifier + ugc-repurposer)* Extend organic creator content with paid spend and repurpose UGC across paid, web, email, and organic. |
| landing-optimizer | Landing pages for creator/paid traffic — message match, mobile, A/B (also serves paid post-click). |
| performance-analyzer | Evaluate creator results, compare creators, sentiment, conversions (also the paid cross-channel scorecard). |
| roi-calculator | Measure/project ROI, defend budgets, value creators/tiers (shared return-math engine, incl. paid). |
| report-generator | Written stakeholder reports after a period (also paid-ads reports). |

</details>

### Paid Ads — ROAS (16)

Four phase directories under `paid/` (4 skills each) follow the ROAS loop; the gate (⛩ ad-account-auditor) sits in Activate. Only the gate computes the goal-weighted RQS — every other skill works one lever and hands off.

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](paid/research/campaign-architect/SKILL.md), [audience-segment-builder](paid/research/audience-segment-builder/SKILL.md), [search-term-miner](paid/research/search-term-miner/SKILL.md), [product-feed-optimizer](paid/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](paid/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](paid/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](paid/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](paid/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](paid/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](paid/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](paid/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](paid/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](paid/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](paid/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](paid/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](paid/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Per-skill purpose (Paid Ads)</b></summary>

| Skill | ROAS lever | What it does |
|-------|-----------|--------------|
| campaign-architect | A + structure | Account/campaign structure, campaign-type fit, match types, negatives/exclusions, paid↔organic cannibalization; carries a recurring **search-term-mining** mode. |
| audience-segment-builder | A | Turns your own customer/CRM/GA4 export into seed audiences, lookalike seeds, exclusion segments, and a funnel-stage targeting map. |
| search-term-miner | A | *(NEW)* Mine the search-terms report for negatives, new keyword candidates, and match-type refinements. |
| product-feed-optimizer | O | *(NEW)* Shopping/PMax feed hygiene — titles, attributes, GTINs, category mapping, and disapproval fixes. |
| ad-creative-builder | O | RSA headlines/descriptions, hooks, and an angle matrix, message-matched to the destination page. |
| ad-test-designer | O (+S) | Design A/B/n & incrementality tests (hypothesis, variant matrix, sample size/power) and read out significance → promote/kill. |
| bid-strategy-planner | S | *(NEW)* Pick and configure bid strategy vs goal (tCPA/tROAS/max-conversions), seed targets, and plan learning-phase transitions. |
| landing-experience-checker | O | *(NEW)* Post-click page QA for ad relevance, load speed, mobile, and policy — the ad↔page message-match check. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Auditor-class ROAS gate: scores RQS, enforces R1/R2/O1/O2/A1, emits SHIP/FIX/BLOCK; carries a **launch go/no-go** mode. |
| conversion-signal-qa | R | Pre-launch tracking QA (event firing, UTM hygiene, dedup gate, window alignment, iOS-ATT flags) — the R1/R2 prerequisite (builds the signal; the gate scores it). |
| placement-exclusion-manager | A | *(NEW)* Placement/audience exclusion lists — brand-safety blocks, junk-placement pruning, wasted-spend suppression. |
| conversion-value-mapper | R | *(NEW)* Map conversion actions to values/weights and value rules so tROAS bids on true margin, not raw counts. |
| paid-measurement-loop | R (+S) | Read one shipped change back against a control over a window → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Standing order-ID de-dup against the GA4/ecommerce truth set, window/currency normalization, model comparison, incrementality. |
| budget-pacing-monitor | S | *(NEW)* Track spend pace against budget over the flight, flag under/over-delivery, and recommend pacing corrections. |
| fatigue-frequency-manager | O | *(NEW)* Watch frequency and creative-decay signals, flag fatigued ads, and schedule refresh/rotation. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [budget-optimizer](plan/budget-optimizer/SKILL.md) (spend + bid-pacing/learning-phase mode), [landing-optimizer](measure/landing-optimizer/SKILL.md) (post-click), [roi-calculator](measure/roi-calculator/SKILL.md) (return math), [report-generator](measure/report-generator/SKILL.md), [performance-analyzer](measure/performance-analyzer/SKILL.md).

</details>

### Email — SEND (16)

Four phase directories under `email/` (4 skills each) follow the SEND loop; the gate (⛩ email-quality-auditor) sits in Deliver. Only the gate computes the goal-weighted EQS — every other skill works one lever and hands off. Use-case-agnostic (B2C lifecycle / B2B cold outbound / newsletter-creator); the goal-weight column picks the emphasis.

| Phase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](email/setup/deliverability-qa/SKILL.md), [list-segment-builder](email/setup/list-segment-builder/SKILL.md), [list-growth-designer](email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](email/engage/email-creative-builder/SKILL.md), [subject-line-lab](email/engage/subject-line-lab/SKILL.md), [email-render-builder](email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Per-skill purpose (Email)</b></summary>

| Skill | SEND lever | What it does |
|-------|-----------|--------------|
| deliverability-qa | S | Pre-flight SPF/DKIM/DMARC/BIMI auth, reputation, inbox-placement, spam-content, and list hygiene (the S1 check). |
| list-segment-builder | E | Behavioral + lifecycle-stage segments and suppression rules from your own list/CRM/GA4 export. |
| list-growth-designer | S (+N) | List-growth strategy — acquisition channels, lead-magnet concepts, a compliant opt-in capture-flow spec, and referral-loop mechanics; feeds S consent-quality captured at acquisition. |
| list-hygiene-monitor | S | *(NEW)* Ongoing list health — bounce/complaint pruning, sunset policies, re-permission, and inactive-segment suppression. |
| email-creative-builder | E (+D) | Subject/preheader/body/CTA, message-matched to the landing page, claims-ledger-aware. |
| subject-line-lab | E | *(NEW)* Subject/preheader ideation and scoring — length, spam-trigger, curiosity/clarity balance, variant sets for testing. |
| email-render-builder | E | *(NEW)* HTML email build/QA — client compatibility, dark-mode, accessibility, plain-text alt, and render-test checklist. |
| dynamic-content-personalizer | E | *(NEW)* Merge-tag/liquid personalization blocks, conditional content rules, and fallback-value safety. |
| email-sequence-designer | N | Lifecycle/automation flows (welcome, cart, post-purchase, win-back) + frequency governance. |
| newsletter-monetization-planner | D | Paid-sub, sponsorship inventory + rate card, and referral growth-loop economics. |
| preference-frequency-manager | N | *(NEW)* Preference-center design and send-frequency governance to cut fatigue and unsubscribes. |
| reactivation-specialist | N | *(NEW)* Win-back / re-engagement flows for dormant subscribers with sunset-or-recover decision rules. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | Auditor-class SEND gate: scores EQS, enforces S1/S2/N1/D1, emits SHIP/FIX/BLOCK; carries a **pre-send go/no-go** mode. |
| send-experiment-designer | E | A/B / send-time / hold-out design with sample-size + significance read (promote/kill). |
| inbox-placement-monitor | S | *(NEW)* Ongoing inbox-vs-spam placement tracking via seed lists and provider signals, with reputation-drift alerts. |
| cold-outbound-sequencer | D | *(NEW)* Compliant B2B cold-outbound cadences — deliverability-safe ramp, personalization tokens, and reply-handling steps. |

**Reused cross-discipline** (counted in their home phases, not duplicated): [audience-mapper](discover/audience-mapper/SKILL.md), [landing-optimizer](measure/landing-optimizer/SKILL.md), [roi-calculator](measure/roi-calculator/SKILL.md), [report-generator](measure/report-generator/SKILL.md), [performance-analyzer](measure/performance-analyzer/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md).

</details>

### Protocol layer (5)

The shared truth & memory machinery — see [Architecture § The protocol layer](#the-protocol-layer) for roles and sole-writer rules.

| Group | Skills |
|-------|--------|
| **Protocol** | [entity-optimizer](protocol/entity-optimizer/SKILL.md), [creator-registry](protocol/creator-registry/SKILL.md), [offer-claims-registry](protocol/offer-claims-registry/SKILL.md), [consent-registry](protocol/consent-registry/SKILL.md), [memory-management](protocol/memory-management/SKILL.md) |

<details><summary><b>Per-skill purpose (Protocol)</b></summary>

| Skill | What it does |
|-------|--------------|
| entity-optimizer | Canonical entity profile for Knowledge Graph, Wikidata, AI disambiguation. |
| creator-registry | Canonical creator roster/dossier — deduped handles, provenance-labeled audience stats, rates, compliance history. |
| offer-claims-registry | Canonical offer & claim-substantiation ledger — the record the O1/T2 claim checks are judged against. |
| consent-registry | Canonical per-subject consent/suppression record — opt-in timestamp + lawful basis, double-opt-in proof, append-only unsub/bounce/complaint history; the record the S2/N1 vetoes judge against. |
| memory-management | Review, promote, demote, and archive HOT/WARM/COLD project memory. |

</details>

---

## Commands

Five commands: `/aaron-marketing:auto` routes any goal across all four disciplines, and each discipline has exactly one explicit entrypoint. Source: [commands/](commands/).

| Command | Use it for | Narrowing |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Describe any goal — infers intent and runs the smallest useful workflow | `--deep` (exhaustive / stress-test) |
| `/aaron-marketing:seo-geo` | SEO/GEO end-to-end: research demand/competitors, create content, audit quality/tech/visibility/authority, track rankings/reports/memory | `--mode research\|create\|audit\|track` + per-mode flags (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` `--authority` · `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:impact` | Influencer (IMPACT): audience insight, discovery & fit, planning, outreach, amplification, ROI | `--phase discover\|plan\|activate\|measure` |
| `/aaron-marketing:paid` | Paid ads (ROAS loop): segments, structure, creative, experiment design, the audit gate, measurement | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | Email (SEND loop): deliverability/consent, segmentation, creative, lifecycle flows, monetization, send-testing, the audit gate | `--phase setup\|engage\|nurture\|deliver` |

Daily work normally starts with `/aaron-marketing:auto`; the other four are explicit discipline entrypoints, with `--mode` / `--phase` to narrow the stage.

**Rename note:** commands use the `/aaron-marketing:` prefix. The former `research` / `create` / `audit` / `track` commands are now modes of `/aaron-marketing:seo-geo` (flags unchanged). Older `/seo:*` and `/aaron-seo-geo:*` names recover via `auto` — e.g. `/aaron-marketing:auto /aaron-seo-geo:audit https://example.com/blog/post` returns `/aaron-marketing:seo-geo https://example.com/blog/post --mode audit`.

---

## Connectors & enhancement tiers

Skills name tools with `~~category` placeholders (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) instead of specific vendors, and every category has a **keyless Tier-1 path**. Full recipes — including the free/first-party endpoint for each category — are in [CONNECTORS.md](CONNECTORS.md).

| Tier | Requires | You get |
|------|----------|---------|
| **Tier 1** (default) | Nothing | Paste data, or pull it from free/public sources. The full analysis framework runs either way. |
| **Tier 2** | One free first-party API or MCP | Automatic retrieval of your own GSC / GA4 / Core Web Vitals data. |
| **Tier 3** | A fuller MCP set | Fully automated multi-source workflows. |

- **Bundled zero-dependency helpers** under `scripts/connectors/` (Python stdlib only) pull public/own data locally — e.g. PageSpeed/CrUX, Open PageRank, page crawl, Wayback CDX, Wikidata SPARQL, Common Crawl, advertools recipes.
- **Free/keyless sources** documented per category: Google Search Console & GA4 (own data), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, and more.
- **Opt-in MCP servers** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, the self-hosted free **OpenSEO** suite, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack) are catalogued in [`docs/mcp-catalog.json`](docs/mcp-catalog.json) as a **copy-paste reference only** — the catalog sits outside the auto-registered plugin-root `.mcp.json` path, so nothing is registered for you. Copy the entries you want into your own MCP config.

Paid-ads skills score from your **own-account manual export** (native ad-manager CSV, GA4, ecommerce). Keyed ad-platform APIs (Google Ads SDK, Meta Marketing API) are opt-in Tier-2/3 only and **never** a Tier-1 requirement. Email skills score the same way — from your **own ESP export** — and every deliverability signal is keyless (DNS lookups, a DMARC RUA report, and a seed-list inbox test), so a keyed ESP API is never a Tier-1 requirement either.

---

## Recommended workflows

**SEO/GEO**
1. **Research** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Build** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Optimize** — `content-quality-auditor` (⛩ publish gate) → `on-page-seo-auditor` → `technical-seo-checker` → `site-structure-optimizer`
4. **Monitor** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; `domain-authority-auditor` (⛩) for the trust review

**Influencer (IMPACT)**
1. **Discover** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (C³ ACE)
2. **Plan** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `content-reviewer` (⛩ ART gate) → `contract-helper` → `content-amplifier`
4. **Measure** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Paid Ads (ROAS loop)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` for the page)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ RQS gate) before any budget goes live
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Email (SEND loop)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ EQS gate) before send

For a full trust review, pair `content-quality-auditor` with `domain-authority-auditor` for a combined 120-item assessment. With `memory-management` active, handoffs and open loops persist in HOT/WARM/COLD memory automatically.

---

## Repository layout

```
research/ build/ optimize/ monitor/                  # SEO/GEO (16, incl. its 2 gates)
discover/ plan/ activate/ measure/                   # Influencer — IMPACT (16, incl. its gate)
paid/research|orchestrate|activate|scale/            # Paid Ads — ROAS (16, incl. its gate)
email/setup|engage|nurture|deliver/                  # Email — SEND (16, incl. its gate)
protocol/                                            # Protocol layer (5) — truth registries + memory
commands/        # 5 slash commands (auto, seo-geo, impact, paid, email)
references/      # shared contract, state model, the 5 benchmarks, auditor runbook, platform packs
evals/           # per-skill structural eval cases + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (the only runtime logic)
scripts/         # validate-skill.sh + connectors/ (stdlib) + CI guards
memory/          # HOT/WARM/COLD scaffolding + registry stores (entities/creators/claims/consent)
docs/            # localized README (zh)
.claude-plugin/  # plugin.json + marketplace.json mirror
```

---

## Design philosophy

- **Skills are content.** The only code is the Bash validator, the Bash hook runner, and zero-dependency Python-stdlib connector/check helpers. No third-party / `pip` dependencies, ever — enforced by a dependency-creep guard.
- **Keyless first.** Every `~~category` has a free/own-data recipe; MCP and paid tools are pure convenience.
- **Surgical & MECE.** Each skill owns one job with a crisp scope boundary; overlapping work ships as a *mode* of an existing skill rather than a new thin skill. Registries curate, gates judge, analyzers feed gates.
- **No invented numbers.** Skills label every figure Measured / User-provided / Estimated and ship an AI-slop / banned-phrase detector.
- **Compliance is guidance, not law.** FTC-disclosure and claim-integrity checks flag risk; they are not legal advice.

---

## Quality guards (CI)

Every change runs against a set of fail-closed guards (all in `scripts/` and `tests/`):

| Guard | Checks |
|-------|--------|
| `validate-skill.sh` | Frontmatter, required sections, version consistency, plugin-relative links across all 69 skills. |
| `golden-auditor-math.py` | Deterministic weight-sum + worked-example arithmetic for **all five** frameworks. |
| `check-evals.py` | Eval structural lint + `structure-manifest.json` (69/69 skills carry eval cases). |
| `check-pii.py` | Blocks committed secrets / PII (token-level allowlist, fail-closed). |
| `check-stdlib-only.sh` | Dependency-creep guard + the Paid-Ads keyed-API red line. |
| `tests/test_hook_artifact_gate.sh` | Behavior tests for the hook's Artifact Gate + SessionStart sanitization. |

---

## Contributing & project docs

- **[CONTRIBUTING.md](CONTRIBUTING.md)** — authoring rules, the contribution checklist, and the authoritative 8-file tracking list.
- **[VERSIONS.md](VERSIONS.md)** — per-skill versions + changelog (current bundle: `12.0.0`).
- **[SECURITY.md](SECURITY.md)** · **[PRIVACY.md](PRIVACY.md)** · **[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)** — security, privacy, and community policy.
- **[CLAUDE.md](CLAUDE.md)** / **[AGENTS.md](AGENTS.md)** — agent-facing context for this repo.

---

## Disclaimer

These skills assist SEO/GEO, influencer-marketing, paid-ads, and email-marketing workflows but do **not** guarantee rankings, AI citations, traffic, engagement, conversions, ROAS, deliverability, or business outcomes. Influencer-, ad-, and email-compliance checks (FTC disclosure, claim integrity, platform policy, consent/opt-in) are guidance, not legal advice. Verify recommendations with qualified professionals before relying on them for major strategy, financial, or legal decisions.

## License

Apache License 2.0 — see [LICENSE](LICENSE).

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
