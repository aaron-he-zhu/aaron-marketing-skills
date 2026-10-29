# SEND Benchmark — Email Marketing Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

SEND evaluates one email program across **Sender Integrity · Engagement · Nurture · Direct Outcome**. It supports promotional, retention, cold-outbound, and newsletter programs without pretending their journeys or outcome truth sets are identical.

The framework is advisory. Executable items, profiles, conditional applicability, and vetoes live in [`framework-catalog.json`](framework-catalog.json); common evidence and scoring rules live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 uses own-account exports, DNS/DMARC evidence, message headers, seed-panel results, and own analytics/CRM/subscription records. ESP APIs are optional conveniences.

## Unit and Required Context

Score one sending program/profile over one normalized window. Declare program type, provider mix, list age, market, and estimated Apple Mail Privacy Protection (`mpp_share`) exposure. Cohort, provider, and window changes create a new run.

## The 20 Items

<!-- AUDITOR-ITEMS:BEGIN -->

| ID | Dimension | Criterion |
|---|---|---|
| `S1` | Sender Integrity | SPF/DKIM/DMARC alignment is verified from DNS and aggregate evidence. |
| `S2` | Sender Integrity | Consent/lawful basis and acquisition provenance are on file. |
| `S3` | Sender Integrity | Inbox placement is measured on a declared provider or seed panel. |
| `S4` | Sender Integrity | Hard-bounce and complaint rates are normalized by cohort/window. |
| `S5` | Sender Integrity | Suppression, hygiene, and sunset controls are active. |
| `E1` | Engagement | Click or downstream action rate is the primary engagement signal. |
| `E2` | Engagement | If opens/CTOR are used, require MPP segmentation and an explicit proxy caveat; unused metrics permit catalog-authorized N/A with reason, missing segmentation is Unknown. |
| `E3` | Engagement | Subject, preheader, and body promise match. |
| `E4` | Engagement | Send timing and frequency fit user preferences and operating capacity. |
| `E5` | Engagement | Engagement decay and reactivation/sunset logic are measured. |
| `N1` | Nurture | Required one-click opt-out works and current suppression tombstones are honored; a verified delivery after a recorded effective suppression Fails, missing logs are Unknown. |
| `N2` | Nurture | Entry, confirmation, and welcome/first-touch logic fit the program. |
| `N3` | Nurture | Applicable lifecycle journeys exist and work for the declared program type. |
| `N4` | Nurture | Segmentation and progression logic use relevant evidence. |
| `N5` | Nurture | Preference and frequency controls are available where the declared program offers recurring sends or configurable frequency. |
| `D1` | Direct Outcome | Claims, disclosures, and offer terms match the claims ledger. |
| `D2` | Direct Outcome | Measure the declared program truth set: ecommerce revenue/value, CRM pipeline, subscription, sponsorship or a named equivalent; opens and provider attribution alone do not establish it. |
| `D3` | Direct Outcome | Offer and CTA are clear for the declared program. |
| `D4` | Direct Outcome | Email-to-destination message match holds. |
| `D5` | Direct Outcome | Outcome attribution is reconciled outside provider self-reporting. |

<!-- AUDITOR-ITEMS:END -->

`E2`, `N3`, and `N5` are conditional. If opens/CTOR are not used, `E2` may be `na` with reason. A newsletter need not have an abandoned-cart flow; cold outbound need not have post-purchase automation. Applicability comes from the declared program, not from an ecommerce template.

## Profiles and Scoring

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `promotional` | S 30% · E 20% · N 15% · D 35% | {"program_type": "promotional"} | all items in included dimensions |
| `retention` | S 20% · E 35% · N 30% · D 15% | {"program_type": "retention"} | all items in included dimensions |
| `cold-outbound` | S 35% · E 25% · N 15% · D 25% | {"program_type": "cold-outbound"} | all items in included dimensions |
| `newsletter` | S 25% · E 35% · N 20% · D 20% | {"program_type": "newsletter"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

Per item: Pass = 10, Partial = 5, Fail = 0. `EQS` is the floor-rounded profile-weighted mean after 100% applicable evidence coverage. Profiles are separate measurement contracts, not labels pasted onto one universal program.

For `S=80 E=75 N=70 D=78`, promotional=`76`, retention=`74`, cold-outbound=`76`, and newsletter=`75`. These are arithmetic fixtures, not performance forecasts.

## Engagement and Outcome Truth

Apple MPP can preload tracking pixels, so opens and metrics derived from opens are proxy evidence unless segmented and caveated. Use clicks, replies, qualified downstream actions, and declared business outcomes as primary signals where available.

`D2` follows the program:

- Ecommerce: deduplicated orders, contribution, or customer value.
- B2B/outbound: qualified replies, meetings, opportunities, and CRM pipeline/revenue.
- Paid newsletter: subscriptions, churn/retention, and net subscription revenue.
- Sponsored newsletter: contracted delivery, qualified sponsor outcomes, and recognized sponsorship revenue.
- Other: one named, independently observable truth set declared before the read.

## Vetoes

| Qualified ID | Verified failure |
|---|---|
| `SEND-S1` | Required authentication is demonstrably broken/unaligned. A monitored `p=none` policy with aligned SPF/DKIM is not automatically a failure. |
| `SEND-S2` | The program uses a purchased, scraped, or otherwise unlawful list without a recorded lawful basis. Missing records are `unknown`. |
| `SEND-N1` | Required opt-out is absent/broken, or a recorded suppression is not honored. Provider bulk-sender requirements and statutes must be named separately. |
| `SEND-D1` | A material claim/disclosure/offer term is false, unsubstantiated, or missing. |

One verified veto caps the score at 59; two or more produce `verdict: BLOCK` without a final score. Missing evidence is `unknown`, never a veto. Over-frequency is a serious `E4/E5` finding, not an automatic veto.

## Evidence Contract

| Need | Preferred evidence |
|---|---|
| Authentication | DNS plus DMARC aggregate records and message headers |
| Placement/reputation | Declared seed/provider panel and dated provider reports |
| Consent/suppression | Append-only consent events and current suppression projection |
| Engagement | ESP export segmented by provider/MPP exposure and cohort |
| Lifecycle | Flow configuration and event-level flow export |
| Outcome | Ecommerce, CRM, subscription, sponsorship, or named equivalent truth set |
| Claims | Approved claims/disclosures and the rendered message/destination |

Use `~~email platform`, `~~web analytics`, and the relevant outcome connector from [`CONNECTORS.md`](../CONNECTORS.md). Keep provider-reported attribution separate from reconciled own-data outcomes.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for SEND](benchmark-boundary-examples.md#send) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Collect one DNS/header/DMARC, consent/suppression, MPP-segmented engagement and program-specific outcome batch. Reuse the current suppression evidence across relevant checks; a changed provider/cohort/window or new suppression state requires a fresh applicable review, not a recycled total.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Setup** — `deliverability-qa`, `list-segment-builder`, and `list-growth-designer` supply Sender Integrity and consent evidence.
- **Engage** — `email-creative-builder`, `subject-line-lab`, `email-render-builder`, and `dynamic-content-personalizer` supply engagement/creative evidence.
- **Nurture** — `email-sequence-designer`, `preference-frequency-manager`, `reactivation-specialist`, and `newsletter-monetization-planner` own applicable program journeys.
- **Deliver** — [`email-quality-auditor`](../email/deliver/email-quality-auditor/SKILL.md) produces the SEND gate; `send-experiment-designer` returns experiment evidence, not an automatic promote/kill policy.

SEND remains advisory until each versioned profile passes the shared reliability and outcome-calibration protocol.
