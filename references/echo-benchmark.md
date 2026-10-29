# ECHO Benchmark — Organic Social Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

ECHO evaluates organic social through **Embeddedness · Craft · Hosting · Observability**. v18 separates an individual asset's Craft gate from a channel portfolio's operating maturity. It does not let a polished post compensate for manufactured engagement, weak governance, or unobservable reporting.

The framework is advisory. Executable profiles, item policies, context, and vetoes live in [`framework-catalog.json`](framework-catalog.json); shared scoring semantics live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 uses registry state, own platform/analytics exports, and compliant public surfaces. Closed-platform data enters as user-provided exports or explicitly labeled proxies. Platform folklore belongs in dated norm cards as `estimated`, never as a universal rubric threshold.

## Units and Profiles

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `asset-gate` | E 10% · C 60% · H 20% · O 10% | {"assessment_mode": "asset", "program_archetype": "not-applicable"} | include_items: {"E": ["E1"], "H": ["H1", "H2"], "O": ["O1"]} |
| `program-maturity-community` | E 37.5% · H 37.5% · O 25% | {"assessment_mode": "program", "program_archetype": "community"} | all items in included dimensions |
| `program-maturity-b2c` | E 20% · H 40% · O 40% | {"assessment_mode": "program", "program_archetype": "b2c"} | all items in included dimensions |
| `program-maturity-founder` | E 28.5% · H 21.5% · O 50% | {"assessment_mode": "program", "program_archetype": "founder"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

- `asset-gate`: One post/asset package for named channels and market; Pre-publish channel truth, content, anti-manipulation/UGC rights, and metric-integrity gate.
- `program-maturity-community`: One channel portfolio/window; Community-led operating maturity.
- `program-maturity-b2c`: One channel portfolio/window; Feed-led brand operating maturity.
- `program-maturity-founder`: One channel portfolio/window; Founder-led operating maturity.

The asset gate contains only controls observable on the publish package and its governing records. An observed asset with no performance rate or metric claim passes O1 because there is no denominator assertion to misrepresent; missing access to the asset remains Unknown. Do not combine the asset gate and program maturity into one score. Report outcomes such as qualified reach, retention, pipeline, or community health as measured metrics with controls; they receive no rubric score until outcome calibration exists.

## Stable Item Anchors

<!-- AUDITOR-ITEMS:BEGIN -->

### Embeddedness (`E1`–`E10`)

| ID | Dimension | Criterion |
|---|---|---|
| `E1` | Embeddedness | channel truth/registry state |
| `E2` | Embeddedness | participation before promotion |
| `E3` | Embeddedness | give/ask evidence |
| `E4` | Embeddedness | current rule digest |
| `E5` | Embeddedness | governed profile/bio/link state |
| `E6` | Embeddedness | owned-space lifecycle where applicable |
| `E7` | Embeddedness | channel-capability fit |
| `E8` | Embeddedness | handle security/governance |
| `E9` | Embeddedness | pinned/bio-link freshness |
| `E10` | Embeddedness | cross-community rule-conflict check |

### Craft (`C1`–`C10`)

| ID | Dimension | Criterion |
|---|---|---|
| `C1` | Craft | claim integrity where claims exist |
| `C2` | Craft | material-connection/synthetic-media disclosure where applicable |
| `C3` | Craft | Adapt the asset to the named platform’s documented/observed format and audience context; native execution Passes, remediable mismatch is Partial, verified blocking incompatibility Fails; folklore is not policy. |
| `C4` | Craft | hook/payload/spec fit |
| `C5` | Craft | accessibility |
| `C6` | Craft | voice/canon adherence |
| `C7` | Craft | declared editorial mix |
| `C8` | Craft | freshness on reused assets |
| `C9` | Craft | link/placement policy |
| `C10` | Craft | format-specific execution evidence |

### Hosting (`H1`–`H10`)

| ID | Dimension | Criterion |
|---|---|---|
| `H1` | Hosting | no manufactured/baited engagement |
| `H2` | Hosting | UGC permission where republishing occurs |
| `H3` | Hosting | response SLA |
| `H4` | Hosting | crisis/pause protocol |
| `H5` | Hosting | cadence/capacity fit |
| `H6` | Hosting | voluntary advocacy |
| `H7` | Hosting | warm-touch selling discipline |
| `H8` | Hosting | escalation ownership |
| `H9` | Hosting | moderation rules/log |
| `H10` | Hosting | advocate-roster hygiene |

### Observability (`O1`–`O10`)

| ID | Dimension | Criterion |
|---|---|---|
| `O1` | Observability | stable named denominators and provenance |
| `O2` | Observability | declared dark-social method |
| `O3` | Observability | locked comparison panel |
| `O4` | Observability | robust per-post rollups and organic/paid separation |
| `O5` | Observability | vanity/EMV exclusion from decision scores |
| `O6` | Observability | attribution instrumentation |
| `O7` | Observability | listening baseline |
| `O8` | Observability | query architecture |
| `O9` | Observability | employee-excluded community health |
| `O10` | Observability | learning writeback |

<!-- AUDITOR-ITEMS:END -->

Per item: Pass = 10, Partial = 5, Fail = 0. Every profile requires 100% coverage of applicable items. `C1`, `C2`, and `H2` may be `na` only under their catalog conditions and with a reason.

Typed context is profile-bound: `asset-gate` uses `assessment_mode: asset` and `program_archetype: not-applicable`; program profiles use `assessment_mode: program` and the exact `community`, `b2c`, or `founder` archetype. A mismatched profile/context pair is invalid rather than a weighting choice.

## Vetoes

| Qualified ID | Verified failure |
|---|---|
| `ECHO-E1` | Activity materially contradicts the governed channel record. No record/access is `unknown`, not a veto. |
| `ECHO-C1` | An asset makes a false/unapproved material product or offer claim. Opinion with no such claim is `na`. |
| `ECHO-C2` | Required material-connection or realistic-synthetic-media disclosure is missing. |
| `ECHO-H1` | Verified bought/coordinated/bot engagement or prohibited engagement bait. Genuine feedback requests and independent disclosed advocates are not failures. |
| `ECHO-H2` | Third-party UGC is republished without applicable permission. A native attributed share is not automatically republishing. |
| `ECHO-O1` | A reported rate hides/switches its denominator or presents proxy data as measured. |

One verified veto caps the containing profile at 59; two or more produce `BLOCK` without a final score. A previous asset verdict is linked to, not averaged into, the program-maturity profile.

## Evidence Contract

| Need | Preferred evidence |
|---|---|
| Channel/governance | Projected channel registry, dated rules, account-control records |
| Asset truth | Narrative canon, claims state, rendered asset, platform requirements |
| Permission/advocacy | Append-only permission/consent events and current projections |
| Own performance | User-exported native analytics plus GA4/GSC truth set |
| Public participation | `discourse.py`, `hn.py`, `bluesky.py`, `fediverse.py`, public RSS |
| Public echo | `gdelt.py`, `tavily.py`, and adjacent sources labeled `proxy` |

No compliant keyless read surface is assumed for X, Instagram, TikTok, LinkedIn, or Xiaohongshu. Missing private exports produce Unknown, not fabricated measurement.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for ECHO](benchmark-boundary-examples.md#echo) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Capture the asset, named platform requirements, rights records and stable denominator panel once. Reuse them for craft, permissions and observability without treating one source as multiple corroborating sources; asset changes reopen dependent controls and program outcomes remain separate.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Explore** — channel portfolio, voice dossier, norm profile, warmup, and channel registry supply `E`.
- **Craft** — calendar/creative/video/advocacy skills produce assets; [`social-quality-auditor`](../social/host/social-quality-auditor/SKILL.md) applies `asset-gate` before publication.
- **Host** — inbox, selling, crisis, moderation, permission, and advocacy operations supply `H`.
- **Observe** — pulse, share-of-voice, dark-social, and measurement-loop skills supply `O` and separately report outcomes.

ECHO remains advisory until each versioned profile passes the shared reliability and outcome-calibration protocol.
