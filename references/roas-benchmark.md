# ROAS Benchmark — Paid Ads Evaluation Standard

The fourth framework in this library, alongside [CORE-EEAT](core-eeat-benchmark.md) (content quality), [CITE](cite-domain-rating.md) (domain authority), and [C³](c3-benchmark.md) (influencer). ROAS scores **paid advertising** — named after the metric paid acquisition exists to maximize (Return On Ad Spend) — across four goal-weighted levers whose initials spell the name.

**Keyless by design**: every input comes from the user's **own account, manually exported** (native ad-manager CSV, GA4/ecommerce export, screenshots). Keyed ad-platform APIs (Google Ads SDK, Meta Marketing API) are an optional Tier-2/3 MCP convenience, **never a Tier-1 precondition**.

## The four dimensions (R · O · A · S)

| Letter | Dimension | What it measures |
|--------|-----------|------------------|
| **R** | **Return** | ROAS / CPA vs target, profitability, **+ measurement-signal integrity** (conversion tracking, attribution, UTM/offline imports, iOS-ATT modeled gaps) |
| **O** | **Offer** | the ad unit: creative quality & hook, ad↔landing-page message match, Quality-Score relevance lever, format fit, **+ claim & policy compliance** |
| **A** | **Audience** | targeting, match types, campaign-type fit (Search/PMax/broad), account structure, negatives/exclusions, **+ brand/placement safety** |
| **S** | **Spend-efficiency** | CPC / CPM / CTR / CVR vs benchmark, budget pacing & allocation, learning-phase respect, paid↔organic cannibalization |

Mnemonic for the levers: **who sees it (A) → what they see (O) → how much you pay (S) → what comes back (R)**. The same four letters also frame the lifecycle as a **ROAS loop**: Research → Orchestrate → Activate → Scale.

## Scoring chassis

| | |
|---|---|
| Per sub-item | Pass = 10 · Partial = 5 · Fail = 0 |
| Dimension score | mean of sub-items × 10 → 0–100 |
| Rollup | **arithmetic goal-weighted mean** (same chassis as CITE), floor-rounded — **not** C³'s geometric CVI |
| Rating bands | 90–100 Excellent · 75–89 Good · 60–74 Medium · 40–59 Low · 0–39 Poor |
| Veto-cap | delegated to [auditor-runbook.md](auditor-runbook.md) §2 — single veto caps the weighted overall at `min(raw, 60)`; 2+ veto fails → `status: BLOCKED` |

**Paid Ads Index (RQS — ROAS Quality Score, 0–100)** = `floor(weighted({R, O, A, S}, goal-weights))`. ⚠ The RQS (a 0–100 quality score) is **not** the literal roas ratio (e.g. 4.2×); the roas ratio is one input to the **Return** dimension.

### Goal-weight columns (each sums to 1.0)

| Goal | R | O | A | S |
|------|---|---|---|---|
| **DR / Performance** | 0.40 | 0.20 | 0.15 | 0.25 |
| **Prospecting / Awareness** | 0.15 | 0.30 | 0.30 | 0.25 |

- DR weights: `RQS_DR = R×0.40 + O×0.20 + A×0.15 + S×0.25`
- Prospecting weights: `RQS_PR = R×0.15 + O×0.30 + A×0.30 + S×0.25`

### Worked examples (golden-math fixture)

Kept here so `scripts/golden-auditor-math.py` can assert the arithmetic deterministically. Input vector `R=75 O=80 A=85 S=78`:

- **DR / Performance goal** → 30 + 16 + 12.75 + 19.5 = `floor(78.25) = 78`.
- **Prospecting / Awareness goal** (same vector) → 11.25 + 24 + 25.5 + 19.5 = `floor(80.25) = 80`. (Weighting toward Audience + Offer raises a prospecting score on the same account — the weights encode the goal.)
- **Veto-capped** — if R1 (conversion tracking broken) fails on the DR example, the weighted overall is capped: `min(78, 60) = 60`, `cap_applied: true`.

## Veto items (red lines — stable IDs, distributed R:2 / O:2 / A:1)

| ID | Dimension | Trigger |
|----|-----------|---------|
| **R1** | Return | Conversion tracking broken / unverifiable. *No data* = veto; iOS-ATT **modeled/partial** data = Partial/flag, **not** an auto-veto (or it fires on nearly every modern account). |
| **R2** | Return | Cross-platform attribution double-counting / inflation (same conversion credited on Meta + Google, or stacked last-click). Detect by matching order IDs / timestamps across the GA4/ecommerce export and each platform export; normalize attribution windows + currency first. |
| **O1** | Offer | Claim integrity — false / unsubstantiated claim or missing required disclosure. |
| **O2** | Offer | Platform-policy compliance — prohibited category, trademark misuse, restricted vertical → disapproval or account risk. |
| **A1** | Audience | Brand / placement safety — unsafe placements or brand-adjacency. Needs the **placements report** export; if absent, A1 = NEEDS_INPUT (not pass-by-default). |

**Premature scaling / learning-phase violation** is a high-severity **guardrail/flag under S**, *not* a veto — it is a process error that wastes spend, but it does not make the RQS itself untrustworthy.

## Data contract (keyless export columns)

| Need | Source export (own data) |
|------|--------------------------|
| S / CTR / CVR / pacing | campaign + search-terms report |
| A / negatives | search-terms + audience/placement reports |
| A1 (placement safety) | **placements report** (else NEEDS_INPUT) |
| R (ROAS/CPA) | conversions from GA4 / ecommerce export (own data) |
| R1 / R2 (signal integrity) | GA4 Conversions + Traffic-acquisition (source/medium); order-ID truth set from GA4/ecommerce, **not** the ad platform's reported conversion count |

Reuse the existing `~~web analytics` (GA4) and `~~ecommerce` connector categories plus `~~ad platform` (own-data manual export) — see [CONNECTORS.md](../CONNECTORS.md). Do **not** invent a `~~conversion tracking` category.

## Naming disambiguation

ROAS's letters **R/O/A** overlap C³'s ACE/ART/**ROI (R/O/I)** and the veto IDs R1/R2/O1/O2 textually resemble other frameworks' item IDs — but each framework's IDs are independent (C³'s ROI scope has **no** veto). In any shared document (e.g. [auditor-runbook.md](auditor-runbook.md) §5) always qualify the letter with the framework name (`ROAS-R` vs `C³ ROI-R` vs `CITE-...`). The runbook lists ROAS vetoes under a Paid-Ads sub-heading.

## Where it is used

The paid-ads skills apply ROAS across the conceptual **ROAS loop** — Research → Orchestrate → Activate → Scale (directories under `paid/<phase>/`). Only [ad-account-auditor](../paid/activate/ad-account-auditor/SKILL.md) computes the goal-weighted RQS and runs the five vetoes; every other skill operates on a single lever and hands off.

- **Research (A)** — [campaign-architect](../paid/research/campaign-architect/SKILL.md) scores **A** + structure; recurring S-lever mining (negatives/new keywords from the search-terms export) is owned by [search-term-miner](../paid/research/search-term-miner/SKILL.md), not a mode of campaign-architect; [audience-segment-builder](../paid/research/audience-segment-builder/SKILL.md) turns the user's own customer/CRM/GA4 export into seed/lookalike/exclusion segments. Reuse: [budget-optimizer](../plan/budget-optimizer/SKILL.md) allocates spend (**S**).
- **Orchestrate (O)** — [ad-creative-builder](../paid/orchestrate/ad-creative-builder/SKILL.md) produces **O** units (ad↔LP message-match + claim/policy checks baked in); [ad-test-designer](../paid/orchestrate/ad-test-designer/SKILL.md) owns experiment design + the significance read (promote/kill). Reuse: [landing-optimizer](../measure/landing-optimizer/SKILL.md) fixes the post-click page.
- **Activate (R-gate)** — [ad-account-auditor](../paid/activate/ad-account-auditor/SKILL.md) is the auditor-class gate: it scores RQS, enforces R1/R2/O1/O2/A1, runs a **launch go/no-go mode**, and emits the [auditor-runbook](auditor-runbook.md) handoff schema to `memory/audits/paid/`. [conversion-signal-qa](../paid/activate/conversion-signal-qa/SKILL.md) BUILDS/FIXES the measurement signal pre-flight (the R1/R2 prerequisite) but does not score it — the auditor judges.
- **Scale (S/R)** — [paid-measurement-loop](../paid/scale/paid-measurement-loop/SKILL.md) reads ROAS/CPA against a control per [measurement-protocol.md](measurement-protocol.md), reusing `ledger.py` + `roi-calculator` (in-flight pacing read is owned by [budget-pacing-monitor](../paid/scale/budget-pacing-monitor/SKILL.md) and bid-strategy by [bid-strategy-planner](../paid/orchestrate/bid-strategy-planner/SKILL.md), plus the auditor's S guardrail); [attribution-reconciler](../paid/scale/attribution-reconciler/SKILL.md) is the standing order-ID de-dup + incrementality workbook (delegates ratio math to [roi-calculator](../measure/roi-calculator/SKILL.md); does not re-run the R2 veto). Reuse: [report-generator](../measure/report-generator/SKILL.md), [performance-analyzer](../measure/performance-analyzer/SKILL.md).

> **Provisional**: ROAS is a new framework. Treat its bands as provisional until calibrated against ~30 real manually-exported account audits in `memory/audits/paid/`, per the runbook's calibration discipline.
