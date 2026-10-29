# TALE Benchmark — Narrative and Messaging Evaluation Standard

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

TALE governs the L1 narrative system through **Truth · Architecture · Landing · Evidence**. v18 reports three distinct reads: whether the narrative is defensible, whether the message system is coherent across surfaces, and whether effectiveness is actually observed. A coherent story cannot compensate for a false claim, and a truthful canon cannot be declared effective without outcome evidence.

The framework is advisory. Executable profiles, item policies, context, and vetoes live in [`framework-catalog.json`](framework-catalog.json); shared scoring semantics live in [`scoring-semantics.md`](scoring-semantics.md).

**Keyless by design:** Tier 1 uses the narrative canon, claims state, owned surfaces, interviews/win-loss evidence, and compliant public signals. Closed-platform or review-site data must be user-provided or labeled proxy.

## Units and Profiles

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `truth` | T 100% | {"assessment_mode": "truth"} | all items in included dimensions |
| `system` | A 50% · L 50% | {"assessment_mode": "system"} | all items in included dimensions |
| `effectiveness` | E 100% | {"assessment_mode": "effectiveness"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

- `truth`: One canon/positioning claim set for a market and audience; Is the strategic narrative materially true and defensible?.
- `system`: One canon plus a declared flagship-surface set; Is the message system coherent and consistently landed?.
- `effectiveness`: One message experiment or locked observation panel/date; What evidence shows the message was understood or changed behavior?.

There is no v18 overall composite. Preserve the three profile results and their dates. A later effectiveness read must link to the exact canon version tested.

## Stable Item Anchors

<!-- AUDITOR-ITEMS:BEGIN -->

### Truth (`T1`–`T10`)

| ID | Dimension | Criterion |
|---|---|---|
| `T1` | Truth | material differentiation integrity |
| `T2` | Truth | positioning alternatives/value evidence |
| `T3` | Truth | category-frame defensibility where used |
| `T4` | Truth | beachhead/audience truth |
| `T5` | Truth | claim provenance/needs-source handling |
| `T6` | Truth | superlative basis |
| `T7` | Truth | product-stage reality |
| `T8` | Truth | aspiration/fact separation |
| `T9` | Truth | interview/win-loss grounding |
| `T10` | Truth | current canon version |

### Architecture (`A1`–`A10`)

| ID | Dimension | Criterion |
|---|---|---|
| `A1` | Architecture | canon existence and internal consistency |
| `A2` | Architecture | chosen message hierarchy/pillars where applicable |
| `A3` | Architecture | traceability from messages to positioning/proof |
| `A4` | Architecture | strategic change arc where appropriate |
| `A5` | Architecture | persona proof provenance |
| `A6` | Architecture | voice rules |
| `A7` | Architecture | naming/lexicon governance |
| `A8` | Architecture | fixed-length boilerplates only when operationally required |
| `A9` | Architecture | Concrete message quality: a reader can identify the intended audience, problem and stated value without the speaker filling gaps; specifics need evidence and a chosen stylistic pattern is not mandatory. |
| `A10` | Architecture | append-only version/supersession history |

### Landing (`L1`–`L10`)

| ID | Dimension | Criterion |
|---|---|---|
| `L1` | Landing | no material flagship-surface contradiction |
| `L2` | Landing | campaign/landing/offer match |
| `L3` | Landing | channel derivation from canon |
| `L4` | Landing | cascade ownership |
| `L5` | Landing | governed localization |
| `L6` | Landing | channel-voice inheritance |
| `L7` | Landing | objection consistency |
| `L8` | Landing | proof at claim location |
| `L9` | Landing | enablement consistency |
| `L10` | Landing | pre-ship drift check |

### Evidence (`E1`–`E10`)

| ID | Dimension | Criterion |
|---|---|---|
| `E1` | Evidence | no unsupported effectiveness/resonance assertion or mislabeled proxy |
| `E2` | Evidence | differentiating-claim substantiation |
| `E3` | Evidence | preregistered comprehension/behavior test |
| `E4` | Evidence | defined echo/recall method |
| `E5` | Evidence | locked comparison panel |
| `E6` | Evidence | answer-engine perception as proxy where used |
| `E7` | Evidence | proof assets |
| `E8` | Evidence | actual-vs-intended retro |
| `E9` | Evidence | win-loss/objection writeback |
| `E10` | Evidence | revision after failed test |

<!-- AUDITOR-ITEMS:END -->

`T1` does not require an “onlyness” sentence. It asks whether the material differentiation actually asserted is false, contradictory, or unsubstantiated against named alternatives.

Three pillars, a Raskin-style change arc, and 25/50/100-word boilerplates are optional design patterns, not universal quality requirements. When a pattern is chosen, score its execution; otherwise use catalog-authorized `na` with reason.

Per item: Pass = 10, Partial = 5, Fail = 0. Each profile requires 100% applicable evidence coverage. A test not yet run is Unknown, not Partial and not evidence of failure.

## Vetoes

| Qualified ID | Verified failure |
|---|---|
| `TALE-T1` | A material differentiation is false, internally contradictory, or unsubstantiated. Aspirational framing clearly labeled as future intent is not present-tense differentiation. |
| `TALE-A1` | The canon demonstrably contradicts itself. No canon/access is `unknown`; a governed draft can be assessed as a draft. |
| `TALE-L1` | A declared flagship surface materially contradicts the tested canon/approved claim wording, excluding governed localization. |
| `TALE-E1` | An effectiveness claim is asserted without evidence, or proxy evidence is presented as measured. Missing results alone are `unknown`. |

One verified veto caps the containing profile at 59; two or more produce `BLOCK` without a final score. Vetoes do not transfer numerically between profiles; linked prior failures remain visible in the audit record.

## Evidence Contract

| Need | Preferred evidence |
|---|---|
| Positioning truth | Interviews, win-loss, product truth, named alternatives, approved claims |
| Canon/system | Versioned narrative registry and claims projection |
| Landing | Rendered/live flagship surfaces with canon-version linkage |
| Effectiveness | Preregistered comprehension, recall, preference, behavior, or win-loss read |
| Public resonance | Locked query/panel signals with own/proxy provenance |
| History | Append-only canon events and `wayback.py` where public history is relevant |

Echo, share-of-voice, sentiment, and answer-engine descriptions are not interchangeable with comprehension or behavior. State the construct and denominator for every metric.

A9 tests specificity, not the truth of an assertion: traceability and substantiation remain with A3/T controls. Do not invent a number or a mandatory boilerplate to make a message concrete.

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for TALE](benchmark-boundary-examples.md#tale) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Reuse the exact canon/version, claim evidence, flagship surface captures and preregistered experiment binding. Review canon→surface→experiment dependencies after a change, preserving prior dated results; consistency, truth and effectiveness do not substitute for each other.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.

## Skill Ownership

- **Trace** — baseline/category/audience/positioning skills and claims state supply `T`.
- **Architect** — narrative, message-system, language, and story-bank skills produce the governed canon and `A` evidence.
- **Land** — cascade, pitch, enablement, and proof packaging supply `L` evidence to downstream channel builders.
- **Evaluate** — [`narrative-quality-auditor`](../narrative/evaluate/narrative-quality-auditor/SKILL.md) runs the selected profile; message tests, resonance monitoring, and drift monitoring supply `E` evidence without claiming causality beyond their design.

TALE remains advisory until each versioned profile passes the shared reliability and outcome-calibration protocol.
