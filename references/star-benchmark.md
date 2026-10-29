# STAR Benchmark — Influencer Marketing Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

STAR evaluates **influencer partnership quality** across **Suitability · Trust · Appeal · Return** for one creator partnership. The mnemonic matches the STAR loop (Scout → Target → Activate → Report), but the framework scores *quality*, not workflow: a suitable creator with non-compliant or weak content must not pass on a comfortable average alone — the vetoes and the profile weighting keep each concern visible.

The framework is advisory. Executable items, profiles, context, and vetoes live in [`framework-catalog.json`](framework-catalog.json); common evidence, missingness, score, status, and verdict rules live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 accepts the user's own exports — creator media kits, platform analytics, campaign reports, and the brand's own conversion data. Keyed creator-analytics suites are optional conveniences, never a baseline requirement.

## Unit and Required Context

Score one creator partnership — the creator, their deliverable, and the attributed campaign outcome — for one `goal`, `assessment_time`, `platform`, and `market`. Suitability is read pre-engagement (Scout), Trust and Appeal pre-publish (Activate), and Return after the campaign (Report); a change in those fields creates a different run. Forecast and actual reads never merge. For a multi-creator campaign, score each partnership separately; a budget-weighted mean of the partnership scores may summarize but never replaces the per-partnership diagnosis.

Audience, reach, engagement, and return are relative to a locked creator-tier × platform × niche cohort and stated window; compliance and craft items use explicit criterion anchors. A platform-wide number without cohort, source, and date is an estimate, not a universal pass/fail threshold.

## The 40 Items

Vetoes are marked ⛔.

<!-- AUDITOR-ITEMS:BEGIN -->

| ID | Dimension | Criterion |
|---|---|---|
| `S1` | Suitability | Audience composition, geography, and language match the target within a stated window. |
| `S2` ⛔ | Suitability | Real-follower rate meets the locked creator-tier x platform x niche benchmark; verified below-benchmark rate/fraud Fails, missing audit is Unknown. |
| `S3` | Suitability | Follower growth is organic and stable, with no purchase or spike anomalies. |
| `S4` | Suitability | Typical reach reliability across recent posts is benchmarked, not cherry-picked. |
| `S5` | Suitability | Engagement rate meets the niche median for the creator's tier and platform. |
| `S6` ⛔ | Suitability | Observed engagement is authentic; verified bought/coordinated/pod activity Fails, an unusual engagement rate alone does not establish fraud. |
| `S7` | Suitability | Repeat audience action (saves/shares/returns) shows durable influence, not campaign conversion. |
| `S8` | Suitability | Brand/category fit and audience-brand overlap are evidenced, independent of any single deal. |
| `S9` | Suitability | Creator reliability, professionalism, and delivery history support the partnership. |
| `S10` | Suitability | Commercial saturation and disclosed category history are transparent and acceptable. |
| `T1` ⛔ | Trust | Required FTC/ASA disclosure is present, clear, and conspicuous on sponsored content. |
| `T2` ⛔ | Trust | Every material claim in the deliverable is truthful and substantiated. |
| `T3` ⛔ | Trust | No disqualifying brand-safety evidence exists under the declared policy and window. |
| `T4` | Trust | Disclosure meets platform-specific tool and caption placement requirements. |
| `T5` | Trust | Prohibited or restricted-category rules for the product are satisfied. |
| `T6` | Trust | Prior disclosure and compliance history shows no unresolved violations. |
| `T7` | Trust | The material connection (gifting/affiliate/paid) is accurately represented to the audience. |
| `T8` | Trust | Comparative or performance claims carry evidence at the point of claim. |
| `T9` | Trust | Sensitive-audience, health, financial, and age-gating requirements are met where applicable. |
| `T10` | Trust | Rights, usage, whitelisting, and exclusivity terms are represented truthfully. |
| `A1` | Appeal | The hook earns attention within the platform's first-impression window. |
| `A2` | Appeal | Creative quality (production, editing, pacing) meets the platform bar. |
| `A3` | Appeal | Brand integration fits the creator’s observed voice and format; native, understandable integration Passes, awkward but connected placement is Partial, unrelated bolted-on copy Fails. |
| `A4` | Appeal | Storytelling and format choice fit the platform's native behavior. |
| `A5` | Appeal | Message accuracy — the brief's key message is conveyed without distortion. |
| `A6` | Appeal | Audience relevance — the content speaks to the target's beliefs and needs. |
| `A7` | Appeal | The call-to-action is present, clear, and matched to the declared goal. |
| `A8` | Appeal | On-brand tone, terminology, and visual identity are respected. |
| `A9` | Appeal | Accessibility (captions, alt text, legibility) is handled. |
| `A10` | Appeal | Originality — the piece is not a templated re-run of prior sponsorships. |
| `R1` | Return | Measured ROI/ROAS is read against the declared target. |
| `R2` | Return | CPE/CPM/CPA are benchmarked on a normalized window. |
| `R3` | Return | Value-for-spend beats the declared alternative-channel baseline. |
| `R4` | Return | KPI attainment versus the pre-registered target is reported. |
| `R5` | Return | Conversions and outcomes are attributed with a stated method and rigor. |
| `R6` | Return | Incremental impact is separated from baseline where measurable. |
| `R7` | Return | Creator-mix and channel choices fit the goal (orchestration, knowable at plan time). |
| `R8` | Return | Budget split and timing across creators and phases are justified. |
| `R9` | Return | The deliverable schedule and cadence match the campaign window. |
| `R10` | Return | The measurement plan (UTMs, codes, controls) is defined before launch. |

<!-- AUDITOR-ITEMS:END -->

## Profiles and Scoring

Per item: Pass = 10, Partial = 5, Fail = 0. A dimension score is the mean of its applicable items × 10 (0–100). The **SQS** (Star Quality Score) is the floor-rounded, profile-weighted arithmetic mean of the four dimensions — the same rollup family as ROAS (RQS) and SEND (EQS). A score is emitted only at 100% coverage of applicable items; missing evidence is `unknown` and prevents a score, and catalog-authorized `na` requires a reason.

Return items `R1`–`R6` apply only to an `actual` assessment; in a `forecast` (pre-publish) read they are `na` with reason, exactly as a paid go/no-go scores Return before spend exists.

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `awareness` | S 30% · T 20% · A 35% · R 15% | {"goal": "awareness"} | all items in included dimensions |
| `engagement` | S 25% · T 20% · A 40% · R 15% | {"goal": "engagement"} | all items in included dimensions |
| `conversion` | S 25% · T 20% · A 20% · R 35% | {"goal": "conversion"} | all items in included dimensions |
| `brand-building` | S 30% · T 35% · A 20% · R 15% | {"goal": "brand-building"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

- `awareness`: Reach/impressions program where audience and craft carry the objective.
- `engagement`: Interaction program where content appeal dominates.
- `conversion`: Response program judged on measured return.
- `brand-building`: Reputation program where suitability and trust lead.

Do not compare profiles as though their weights were identical.

Exactly one verified veto caps SQS at `min(raw, 59)` and raises a flag; two or more verified vetoes produce `verdict: BLOCK` with no final score. Missing veto evidence is `unknown`, not a failure.

## Veto Items

| Qualified ID | Dimension | Trigger |
|---|---|---|
| `STAR-S2` | Suitability | Verified follower fraud, or a real-follower rate below the tier × platform × niche benchmark. Refused/missing audit is `unknown`. |
| `STAR-S6` | Suitability | Verified bought, coordinated, or pod-based engagement. |
| `STAR-T1` | Trust | Missing or materially inadequate FTC/ASA disclosure where a material connection exists. |
| `STAR-T2` | Trust | False or unsubstantiated material claim in the deliverable. |
| `STAR-T3` | Trust | Documented disqualifying brand-safety evidence under the declared policy and observation window. |

Disclosure vetoes use FTC **16 CFR §255** (Endorsement Guides) and the 2024 Trade Regulation Rule on Consumer Reviews & Testimonials (**16 CFR Part 465**) as compliance inputs. Not legal advice — consult counsel for your jurisdiction.

**Cross-framework ID note:** STAR's `S`/`T`/`A`/`R` item prefixes collide textually with SEND `S`, ROAS `A`/`S`, RAMP `A`/`R`, TALE `T`/`A`, CITE `T`, and CORE-EEAT `A`/`T`. Always qualify IDs as `STAR-S2`, `STAR-T1`, etc. outside a single-framework table.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for STAR](benchmark-boundary-examples.md#star) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Collect the creator-window analytics, the frozen deliverable and current rights/disclosure records once. Suitability, craft and actual return judge different objects; a changed asset reopens its affected T/A checks, while a new outcome window creates a separate actual run, never a rewritten forecast.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Scout** — [`fit-scorer`](../influencer/scout/fit-scorer/SKILL.md) supplies the Suitability (S) read (audience audit, reach reliability, engagement health, brand/category fit); it feeds the dimension, it does not emit the composite.
- **Activate** — [`creator-content-auditor`](../influencer/activate/creator-content-auditor/SKILL.md) is the STAR gate and the sole SQS authority: it scores Trust (T) and Appeal (A) on the deliverable, folds in the Suitability read, computes the profile-weighted SQS (Return per `assessment_time`), applies the `S2`/`S6`/`T1`/`T2`/`T3` vetoes, and returns the pre-publish go/no-go. Every other skill works one lever and hands off.
- **Report** — [`roi-calculator`](../influencer/report/roi-calculator/SKILL.md) supplies the measured Return (R) evidence for an `actual` SQS re-read; `performance-analyzer` supplies the measured inputs.

All outputs remain advisory until the versioned profile passes the reliability and outcome-calibration protocol in [`scoring-semantics.md`](scoring-semantics.md).
