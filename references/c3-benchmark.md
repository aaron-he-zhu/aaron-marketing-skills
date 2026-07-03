# C³ Benchmark — Influencer Marketing Evaluation Standard

The third framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality) and [CITE](cite-domain-rating.md) (domain authority). C³ scores **influencer marketing** across three nested scopes — **Creator · Content · Campaign** — each on a lean 3-dimension rubric (**ACE · ART · ROI**).

This file is the entry point; the full rubric lives in [references/c3/](c3/).

## The three scopes (C³)

| Scope | Rubric | Core question | Portable? |
|-------|--------|---------------|-----------|
| **Creator** | **ACE** | Is this creator worth partnering with? | reusable across brands/campaigns |
| **Content** | **ART** | Is this deliverable good and compliant? | per-piece |
| **Campaign** | **ROI** | Did / will the campaign deliver? | per-initiative |

Naming order follows the value chain `Creator · Content · Campaign`; report drill-down runs the other way (`Campaign → Creator → Content`, macro → micro).

## The 9 dimensions

| Scope | Dimensions |
|-------|-----------|
| **ACE** (Creator) | **A**udience · **C**redibility 〔veto〕 · **E**ngagement |
| **ART** (Content) | **A**ppeal · **R**elevance · **T**ransparency 〔veto〕 |
| **ROI** (Campaign) | **R**eturn · **O**rchestration · **I**mpact |

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Within a scope (3 dims) | additive weighted mean (weights shift by campaign goal) |
| Across scopes | multiplicative (geometric mean) — a weak link wastes the rest |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | any failed veto item caps that scope's rating at Low (≤ 59) and raises a flag |

**Campaign Value Index**: `CVI = (ACE_avg × ART_avg × ROI)^(1/3)`. Keep the three scope scores beside the CVI — the index ranks and alerts, the three scores diagnose.

### Worked example (golden-math fixture)

Concrete CVI computations (geometric mean, floor-rounded), kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically:

- **No-veto** — `ACE_avg=90 ART_avg=80 ROI=70` → `CVI = floor(504000^(1/3)) = 79`. (The geometric mean 79 sits below the arithmetic mean 80 — a weaker scope drags the whole index, which is the point of the multiplicative rollup.)
- **Veto-capped** — an ACE veto (e.g. A2 real-follower fraud) caps the Creator scope at the Low-band ceiling, so `ACE_avg=59 (capped)` → `CVI = floor(330400^(1/3)) = 69`.
- **Cap-reconciliation boundary** — at a raw scope of exactly 60 with one veto, C³ caps to its Low-band ceiling **≤ 59**, while the framework-agnostic [auditor-runbook.md](auditor-runbook.md) §2 caps the weighted overall at `min(raw, 60) = 60`. These are **band-aligned**: they differ by ≤ 1 point *only* at this boundary (C³'s Low band tops at 59 by definition). No rubric numbers change; the runbook value is authoritative for the Artifact Gate.

## Veto items (red lines)

| Scope | Veto | Trigger |
|-------|------|---------|
| ACE | **A2** Real-Follower Rate | < 70% real / audit refused (follower fraud) |
| ACE | **C1** Brand Safety | disqualifying content / active scandal |
| ACE | **E2** Engagement Authenticity | pod / bought engagement |
| ART | **T1** FTC Disclosure | missing / inadequate disclosure on sponsored content |
| ART | **T2** Claim Integrity | false / unsubstantiated claims |

Regulatory basis for the disclosure vetoes: FTC **16 CFR §255** (Endorsement Guides) and the 2024 Trade Regulation Rule on Consumer Reviews & Testimonials (**16 CFR Part 465**). Not legal advice — consult counsel for your jurisdiction.

## Threshold regimes

Influencer metrics are platform/tier/niche-relative — never hard-code platform-agnostic numbers.

- **Relative (benchmarked)** — Audience reach, Engagement, Return, Impact. Pass = at/above the benchmark for the creator's tier × platform × niche.
- **Absolute (gate)** — Credibility, Appeal, Relevance, Transparency, Orchestration. Pass = criterion met (presence / quality / compliance), independent of platform.

## Components

- [c3/scoring-architecture.md](c3/scoring-architecture.md) — scoring chassis, thresholds, MECE boundaries, rollup math
- [c3/ace-creator-benchmark.md](c3/ace-creator-benchmark.md) — Creator rubric (ACE)
- [c3/art-content-benchmark.md](c3/art-content-benchmark.md) — Content rubric (ART)
- [c3/roi-campaign-benchmark.md](c3/roi-campaign-benchmark.md) — Campaign rubric (ROI)

## Where it is used

The influencer-marketing skills (IMPACT phases: Insight · Map · Plan · Activate · Convert · Track) apply C³:

Three skills apply C³ scoring directly (they emit the rubric scores and enforce the veto items); two more inform those scores without computing them.

- **Map** — [fit-scorer](../discover/fit-scorer/SKILL.md) scores creators on **ACE** and enforces the A2/C1/E2 veto items. [influencer-discovery](../discover/influencer-discovery/SKILL.md) *informs* this step: it shortlists candidates that fit-scorer then scores on ACE (it does not compute ACE itself).
- **Activate** — [content-reviewer](../activate/content-reviewer/SKILL.md) gates deliverables on **ART**, with T1 (FTC disclosure) and T2 (claim integrity) as veto items.
- **Track** — [roi-calculator](../measure/roi-calculator/SKILL.md) computes the **ROI** score and the **CVI** rollup. [performance-analyzer](../measure/performance-analyzer/SKILL.md) *contributes* the measured campaign inputs that feed ROI/CVI (it does not compute the rollup itself).
