# RAMP Benchmark — Product Launch Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

RAMP evaluates a launch through four lenses: **Readiness · Assets · Momentum · Proof**. These lenses occur at different times, so v18 reports three distinct reads rather than one temporally incoherent Launch Quality Score.

The framework is advisory. Executable profiles, item identity, context, and vetoes live in [`framework-catalog.json`](framework-catalog.json); shared scoring semantics live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 uses the launch plan, claims and launch registries, own analytics exports, and public/keyless launch telemetry. Platform APIs and commercial ASO tools are optional.

## Unit and Lifecycle Context

Score one launch at one declared `lifecycle_read`, market, launch type, and access model. The same launch may produce preflight, execution, and outcome results, but they remain separate records with separate dates. Never average them into a single score.

## Profiles

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `preflight` | R 40% · A 40% · M 10% · P 10% | {"lifecycle_read": "preflight"} | include_items: {"M": ["M1"], "P": ["P1"]} |
| `execution` | M 100% | {"lifecycle_read": "execution"} | all items in included dimensions |
| `outcome` | P 100% | {"lifecycle_read": "outcome"} | exclude_items: {"P": ["P1"]} |

<!-- GENERATED:END auditor-policy:profiles -->

- `preflight`: Before release; Ready/fix/block before committing the moment.
- `execution`: During/just after the launch window; Whether the plan was executed safely and coherently.
- `outcome`: After the declared lag; What was observed and learned.

Outcome evidence is not backfilled into preflight. Preflight plans are not scored as realized outcomes.

## Stable Item Anchors

<!-- AUDITOR-ITEMS:BEGIN -->

### Readiness (`R1`–`R10`)

| ID | Dimension | Criterion |
|---|---|---|
| `R1` | Readiness | stage truth against declared access/eligibility |
| `R2` | Readiness | positioning and alternatives |
| `R3` | Readiness | ICP/beachhead fit |
| `R4` | Readiness | tier/type and effort |
| `R5` | Readiness | timing/window |
| `R6` | Readiness | competitor launch evidence |
| `R7` | Readiness | early-access graduation where applicable |
| `R8` | Readiness | risk/rollback register |
| `R9` | Readiness | internal ownership/escalation |
| `R10` | Readiness | preregistered D0/W1/M1 targets |

### Assets (`A1`–`A10`)

| ID | Dimension | Criterion |
|---|---|---|
| `A1` | Assets | claim/disclosure integrity |
| `A2` | Assets | narrative/message architecture |
| `A3` | Assets | proof-point completeness |
| `A4` | Assets | press/facts asset manifest |
| `A5` | Assets | channel-specific asset compliance |
| `A6` | Assets | pricing/offer terms where applicable |
| `A7` | Assets | sales/support enablement where applicable |
| `A8` | Assets | announcement/landing/offer match |
| `A9` | Assets | technical go-live verification |
| `A10` | Assets | localization/regional readiness where applicable |

### Momentum (`M1`–`M10`)

| ID | Dimension | Criterion |
|---|---|---|
| `M1` | Momentum Execution | platform/embargo integrity |
| `M2` | Momentum Execution | channel mix and dependency risk |
| `M3` | Momentum Execution | T-minus execution |
| `M4` | Momentum Execution | authoritative date/commitment coordination |
| `M5` | Momentum Execution | owned-channel sequence |
| `M6` | Momentum Execution | media/partner activation |
| `M7` | Momentum Execution | community response operation |
| `M8` | Momentum Execution | live monitoring/alerts |
| `M9` | Momentum Execution | go/rollback observation windows |
| `M10` | Momentum Execution | launch-spacing/capacity guardrail |

### Proof (`P1`–`P10`)

| ID | Dimension | Criterion |
|---|---|---|
| `P1` | Proof Outcomes | preflight instrumentation verification |
| `P2` | Proof Outcomes | actuals vs preregistered targets |
| `P3` | Proof Outcomes | attribution reconciliation |
| `P4` | Proof Outcomes | spike-to-sustain retention |
| `P5` | Proof Outcomes | owned-capture rate |
| `P6` | Proof Outcomes | Feedback loop closure: trace feedback to an owned disposition and reporter follow-up; a collected queue without disposition is Partial, verified abandonment Fails, inaccessible records are Unknown. |
| `P7` | Proof Outcomes | compliant social-proof pipeline |
| `P8` | Proof Outcomes | causal retro/uncertainty |
| `P9` | Proof Outcomes | registry learning/outcome writeback |
| `P10` | Proof Outcomes | T+1→T+30 momentum plan and next decision |

<!-- AUDITOR-ITEMS:END -->

Per item: Pass = 10, Partial = 5, Fail = 0. Each profile requires 100% coverage of its applicable items. The common bands describe each profile only; v18 defines no cross-lifecycle composite.

## Vetoes

| Qualified ID | Verified failure |
|---|---|
| `RAMP-R1` | The announced lifecycle stage materially contradicts verifiable access or eligibility. A public pricing page is required only when the access model promises public paid availability. Missing registry/access evidence is `unknown`. |
| `RAMP-A1` | Launch copy contains a false/unsubstantiated material claim or missing required disclosure. |
| `RAMP-M1` | Verified vote/engagement manipulation, material embargo breach, or launch-blocking platform-policy violation. A genuine feedback request is not vote solicitation. |
| `RAMP-P1` | Required participating surfaces have demonstrably broken instrumentation. A genuinely unused surface is `na`; privacy-limited modeled data may be partial. |

Veto policy applies within the profile that contains the item: `R1/A1/M1/P1` at preflight and `M1` again as observed execution evidence in the execution profile. A preflight plan and its later execution are different dated runs. The outcome profile has no inherited numeric veto; prior verdicts remain linked records. One veto caps at 59; two or more produce `BLOCK` without a final score.

## Evidence Contract

| Need | Preferred evidence |
|---|---|
| Stage/access | Launch registry plus direct access/eligibility check |
| Positioning/assets | Narrative canon, claims ledger, launch manifest, rendered surfaces |
| Rules/commitments | Dated official platform rules, contracts, embargo record |
| Instrumentation | Verified events/UTMs and own-data destination checks |
| Outcomes | Own analytics/CRM/store truth set after declared lag |
| Public echo | `hn.py`, `producthunt.py`, `appstore.py`, `gdelt.py`, each provenance-labeled |

Public telemetry is supporting evidence, not a substitute for own conversion/outcome data. Platform folklore remains dated `estimated` guidance outside the rubric.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for RAMP](benchmark-boundary-examples.md#ramp) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Reuse the versioned launch registry, claims/asset manifest and event-QA capture across their relevant checks. Preflight, execution and outcome remain separate dated runs; resolve feedback in its existing owned record and link its disposition/follow-up rather than introducing a new launch state.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Research** — positioning, launch tier/window, early-access, risk, and target definition supply `R`.
- **Assemble** — message/claim, asset, offer, enablement, and go-live work supply `A` and preflight `P1`.
- **Mobilize** — [`launch-readiness-auditor`](../launch/mobilize/launch-readiness-auditor/SKILL.md) runs preflight; launch-day/community/media operators later supply `M` execution evidence.
- **Prove** — `launch-monitor`, `launch-feedback-synthesizer`, `launch-retro-analyzer`, and `momentum-planner` supply outcome `P2–P10` evidence.

RAMP results remain advisory until each lifecycle profile passes the shared reliability and outcome-calibration protocol.
