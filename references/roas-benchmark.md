# ROAS Benchmark — Paid Ads Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

ROAS evaluates **incremental paid-media contribution and operating quality under declared business constraints**. The mnemonic remains Return · Offer · Audience · Spend Efficiency, but the objective is not to maximize a platform-reported ROAS ratio. A high reported ratio can coexist with weak incrementality, under-spending, attribution inflation, or poor profit.

The framework is advisory. Executable items, profiles, context, and vetoes live in [`framework-catalog.json`](framework-catalog.json); common evidence, missingness, score, status, and verdict rules live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 accepts the user's own exports from ad managers, analytics, ecommerce/CRM, and placement reports. Keyed platform APIs are optional conveniences, never a baseline requirement.

## Unit and Required Context

Score one account or campaign portfolio for one currency, normalized attribution window, observation period, conversion-lag assumption, goal, and business constraint. A change in those fields creates a different run. Platform self-report is evidence, not the outcome truth set.

## The 20 Items

<!-- AUDITOR-ITEMS:BEGIN -->

| ID | Dimension | Criterion |
|---|---|---|
| `R1` | Return | Conversion instrumentation is verified against an own-data truth set. |
| `R2` | Return | Cross-platform attribution is deduplicated; attribution windows and currency are normalized. |
| `R3` | Return | Incremental contribution/profit is evaluated against the declared target/control; platform-attributed ROAS alone leaves incrementality Unknown, a labeled proxy is not a causal result. |
| `R4` | Return | CAC/CPA and payback meet the declared business constraints on normalized own-data outcomes; absent constraint/truth set is Unknown. |
| `R5` | Return | Marginal return uses a completed declared lag window and stated uncertainty; average historical ROAS cannot establish the return on additional spend. |
| `O1` | Offer | Claims and required disclosures are substantiated. |
| `O2` | Offer | Platform policy and restricted-category requirements are satisfied. |
| `O3` | Offer | Offer economics, eligibility, terms, and availability are explicit. |
| `O4` | Offer | Ad-to-landing message and intent match. |
| `O5` | Offer | Creative hook, format, accessibility, and fatigue state fit the placement. |
| `A1` | Audience | Brand and placement safety are verified from the placement evidence. |
| `A2` | Audience | Targeting and query/audience intent fit. |
| `A3` | Audience | Negative keywords, exclusions, and suppression controls are maintained. |
| `A4` | Audience | Campaign/account structure supports the declared objective without avoidable overlap. |
| `A5` | Audience | Reach, overlap and audience saturation use audience-level evidence on one window; frequency alone cannot establish saturation. |
| `S1` | Spend Efficiency | Budget pacing remains within the declared plan and constraints. |
| `S2` | Spend Efficiency | Bid strategy and learning-state changes are governed. |
| `S3` | Spend Efficiency | Marginal CPC/CPM/CTR/CVR efficiency is compared on a normalized window. |
| `S4` | Spend Efficiency | Creative-level frequency/decay is separated from audience saturation; aggregate frequency alone cannot establish creative fatigue. |
| `S5` | Spend Efficiency | Paid/organic and cross-campaign cannibalization are assessed. |

<!-- AUDITOR-ITEMS:END -->

## Profiles and Scoring

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `direct-response` | R 40% · O 20% · A 15% · S 25% | {"goal": "direct-response"} | all items in included dimensions |
| `prospecting` | R 15% · O 30% · A 30% · S 25% | {"goal": "prospecting"} | all items in included dimensions |
| `incremental-profit` | R 50% · O 15% · A 10% · S 25% | {"goal": "incremental-profit"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

- `direct-response`: Conversion program under an explicit CAC/payback constraint.
- `prospecting`: Reach/consideration program with a declared downstream outcome.
- `incremental-profit`: Holdout or causal design centered on contribution/profit.

Per item: Pass = 10, Partial = 5, Fail = 0. The Paid Ads Index (`RQS`) is the floor-rounded profile-weighted mean after 100% applicable evidence coverage. `RQS` is not the literal ROAS ratio and profiles are not interchangeable.

For `R=75 O=80 A=85 S=78`, direct response is `78`; prospecting is `80`; incremental profit is `77`. These are arithmetic fixtures, not outcome predictions.

## Vetoes and Unknowns

| ID | Verified failure |
|---|---|
| `ROAS-R1` | Instrumentation is demonstrably broken or does not reconcile to the named truth set. |
| `ROAS-R2` | The same outcomes are demonstrably double-counted or materially inflated. |
| `ROAS-O1` | A material claim/disclosure is false, unsubstantiated, or missing. |
| `ROAS-O2` | The offer violates an applicable platform/restricted-category rule. |
| `ROAS-A1` | Placement evidence shows a material brand-safety breach. |

No data or no access is `unknown`, producing `NEEDS_INPUT/UNDECIDED`; it is not a veto. iOS/ATT modeled data may be partial or weak evidence but is not automatically a failure. Only an `ad-account-auditor` invocation qualifies veto evidence and applies the truth table: one verified veto caps the final score at 59; two or more produce `verdict: BLOCK` and no final score. Every other skill reports potential ROAS control evidence and hands it off without calling it a verified veto or emitting a gate verdict.

Premature scaling and learning-phase disruption are high-severity `S2` findings, not automatic vetoes.

## Evidence Contract

| Need | Preferred evidence |
|---|---|
| Spend, pacing, queries, placements | Campaign, search-term, audience, and placement exports |
| Outcomes | GA4/ecommerce/CRM order or lead truth set with stable IDs |
| Attribution integrity | Deduplicated IDs/timestamps, normalized windows/currency, documented lag |
| Incrementality | Holdout, geo/market split, causal test, or explicitly labeled proxy |
| Profit constraint | Margin, fulfillment, CAC/payback, and contribution assumptions with provenance |

Use `~~web analytics`, `~~ecommerce`, and `~~ad platform` connector categories from [`CONNECTORS.md`](../CONNECTORS.md). Keep raw platform metrics, calculated reconciliations, and estimates visibly distinct.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for ROAS](benchmark-boundary-examples.md#roas) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Normalize one own-data order/lead, spend, placement and lag batch for the portfolio. Reuse it for reconciliation and business-constraint checks while keeping incrementality, audience saturation and creative decay separate. Reassess changed tracking/claims/creative and dependencies, then submit the complete profile to the scorer.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Research** — `campaign-architect`, `search-term-miner`, and `audience-segment-builder` own structure and audience inputs.
- **Orchestrate** — `ad-creative-builder`, `ad-test-designer`, `landing-optimizer`, and `bid-strategy-planner` own offer/experience and test design.
- **Activate** — [`ad-account-auditor`](../ad/activate/ad-account-auditor/SKILL.md) produces the gate; `conversion-signal-qa` fixes signal prerequisites but does not score them.
- **Scale** — `paid-measurement-loop`, `attribution-reconciler`, `budget-pacing-monitor`, and `fatigue-frequency-manager` supply normalized return and efficiency evidence.

Experiment helpers return statistical facts; the calling skill owns the precommitted business decision under [`measurement-protocol.md`](measurement-protocol.md). ROAS remains advisory until its versioned profiles pass the calibration protocol.
