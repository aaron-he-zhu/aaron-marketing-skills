# Fit Scorer — Scoring Templates

Typed Suitability evidence tables, commercial-fit component tables, the commercial rollup, the multi-creator comparison report, custom weighting, and a worked example. The numbered steps in [SKILL.md](../SKILL.md) reference these blocks. Fill in the bracketed cells per candidate.

**Copy contract**: copied output uses only stable opaque `creator_ref` values and opaque evidence/identity refs; raw handles, names, profile URLs, emails, and provider IDs stay in transient lookup context. The Suitability read is the `STAR-S1`–`STAR-S10` typed-state table below, with dated evidence or an explicit gap/N/A reason for every item. It has no hand-calculated total. Every 1–5 value in this file is an optional campaign-specific `commercial_fit_score` component, never Suitability or SQS, and cannot clear a potential `STAR-S2`/`STAR-S6` control finding or missing Suitability evidence. Do not rename it “Fit Score,” “Final Score,” “Suitability score,” or “SQS.”

---

## Step 0 — Identity and Typed STAR Context

```markdown
### Identity and Typed Context

- `creator_ref`: [creator-<UUIDv4> or verified registry aggregate ID]
- `identity_status`: [resolved/unresolved/conflict]
- `identity_evidence_refs`: [[opaque authorized artifact/registry refs] or []]
- `target`: [creator partnership target]
- `target_version`: [version]
- `profile`: [awareness/engagement/conversion/brand-building]
- `assessment_time`: [forecast/actual]
- `rollup_id`: [shared campaign rollup ID]
- `observation_date`: [YYYY-MM-DD]
- `cohort`: [platform + tier + niche]
- `evidence_window`: [start/end]
- `material_context`: [market/category/campaign constraints object]
- `catalog_version`: [current STAR catalog version]
- `context_status`: [READY/NEEDS_INPUT]
- `context_gaps`: [[missing field], ...]
```

Do not start the Suitability read when `context_status` is `NEEDS_INPUT`. Preserve the supplied `creator_ref` and return the gap list. If identity cannot be resolved through an authorized artifact or verified registry link, keep `identity_status: unresolved`; do not create a hidden raw-handle mapping.

---

## Step 1 — Typed Suitability (S) Read

```markdown
## Typed Suitability (S) Read

**creator_ref**: [creator_ref]
**Suitability read status**: [COMPLETE/NEEDS_INPUT]

Allowed item states are exactly `Pass | Partial | Fail | Unknown | N/A`. `Pass`, `Partial`, and `Fail` require current dated evidence. `Unknown` requires a gap reason and prevents a complete Suitability read. `N/A` requires an applicability reason.

| STAR item | Requirement | Typed state | Evidence refs | observed_at | Evidence window | Evidence type | Confidence | Gap / N/A reason |
|-----------|-------------|-------------|---------------|-------------|-----------------|---------------|------------|------------------|
| `STAR-S1` | Audience composition, geography, and language match | [state] | [opaque refs] | [date] | [window] | [Measured/Calculated/Estimated/User-provided/Proxy] | [confidence] | [reason/none] |
| `STAR-S2` | Real-follower rate meets the matching cohort benchmark | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S3` | Follower growth is organic and stable | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S4` | Typical reach is reliable across a recent sample | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S5` | Engagement rate meets the matching cohort median | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S6` | Engagement is authentic, not bought or coordinated | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S7` | Repeat audience action shows durable influence | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S8` | Deal-independent brand/category and audience-brand fit is evidenced | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S9` | Reliability, professionalism, and delivery history support partnership | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |
| `STAR-S10` | Commercial saturation and disclosed category history are acceptable | [state] | [opaque refs] | [date] | [window] | [type] | [confidence] | [reason/none] |

### Coverage and Control Handoff

- `applicable_items`: [count]
- `evidenced_applicable_items`: [count]
- `unknown_items`: [[STAR item IDs], ...]
- `potential_control_findings`: [[STAR-S2/STAR-S6 + evidence refs] or []]
- `outreach_status`: [HOLD_FOR_INPUT/HOLD_FOR_POTENTIAL_CONTROL/ELIGIBLE_FOR_PLANNING]
- `auditor_handoff_required`: [yes/no + reason]

This table is the Suitability read. Do not average its states, convert them to 1–5 values, emit a Suitability total, apply a cap, or label it SQS. Only `creator-content-auditor` may verify the potential control finding and compute the later STAR verdict/SQS.
```

---

## Step 2 — Commercial-Fit Framework

```markdown
### Commercial-Fit Framework

**Brand/Campaign**: [name]
**Campaign Goal**: [awareness/consideration/conversion]
**Target Audience**: [description]

### `commercial_fit_score` Components

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Campaign Audience Activation Fit | [%] | Deal-specific segment, channel, and CTA fit; does not rescore `STAR-S1`/`STAR-S8` |
| Concept & Format Fit | [%] | Fit to this campaign's supplied concept and deliverable format |
| Message & Offer Fit | [%] | Fit to this campaign's approved message and offer constraints |
| Activation & Commercial Fit | [%] | Supplied terms, rights readiness, availability, timing, and budget feasibility |
| Partnership Execution Fit | [%] | Evidence-backed ability to execute this campaign workflow; does not rescore `STAR-S9` |
| **Total** | **100%** | |

**Commercial scale**: 1–5 against the declared campaign criteria. A missing criterion or evidence row is `NOT_SCORED`/`NEEDS_INPUT`, never a neutral 3. Record the explicit decision rule and user-approved weights. These values are never SQS.
```

---

## Step 3 — Campaign Audience Activation Fit

```markdown
## Campaign Audience Activation Fit

**creator_ref**: [creator_ref]

### Campaign-Specific Comparison

| Campaign criterion | Supplied requirement | Creator evidence/read | Evidence refs | observed_at | Commercial implication |
|--------------------|----------------------|-----------------------|---------------|-------------|------------------------|
| Priority segment | [campaign segment] | [evidenced audience read] | [opaque refs] | [date] | [implication] |
| Required market/language | [requirement] | [evidenced read] | [opaque refs] | [date] | [implication] |
| Planned channel/CTA | [activation plan] | [evidenced behavior/format fit] | [opaque refs] | [date] | [implication] |

### Suitability Dependencies — Zero Commercial Points

| STAR item | Typed state from Suitability read | Evidence refs | Effect here |
|-----------|-----------------------------------|---------------|-------------|
| `STAR-S1` | [state] | [refs] | Context only; do not rescore |
| `STAR-S2` | [state] | [refs] | A potential finding holds ranking/outreach; commercial points cannot offset it |
| `STAR-S8` | [state] | [refs] | Context only; do not rescore |

### `commercial_fit_score.campaign_audience_activation_fit`: [1–5/NOT_SCORED]

**Evidence-backed rationale**: [campaign-specific explanation with refs]

**Weighted `commercial_fit_score` contribution**: [X] × [weight%] = [weighted points]
```

---

## Step 4 — Concept & Format Fit

```markdown
## Concept & Format Fit

**creator_ref**: [creator_ref]

### Supplied Deliverable Requirements

| Requirement | Creator evidence/read | Evidence refs | observed_at | Commercial implication |
|-------------|-----------------------|---------------|-------------|------------------------|
| Deliverable format | [read] | [opaque refs] | [date] | [implication] |
| Production constraints | [read] | [opaque refs] | [date] | [implication] |
| Concept compatibility | [read] | [opaque refs] | [date] | [implication] |
| Revision/approval workflow | [read] | [opaque refs] | [date] | [implication] |

### Current Evidence

- **Format sample refs**: [[opaque content refs], ...]
- **Sample window**: [start/end]
- **Observed at**: [date]
- **Evidence type/confidence**: [type/confidence]

### Gaps and Hypotheses

- `evidence_gaps`: [[gap], ...]
- `concept_hypothesis`: [falsifiable campaign hypothesis or none; zero score/weight]

### `commercial_fit_score.concept_format_fit`: [1–5/NOT_SCORED]

**Evidence-backed rationale**: [campaign-specific explanation with refs]

**Weighted `commercial_fit_score` contribution**: [X] × [weight%] = [weighted points]
```

---

## Step 5 — Message & Offer Fit

```markdown
## Message & Offer Fit

**creator_ref**: [creator_ref]

### Campaign-Specific Requirements

| Requirement | Supplied campaign constraint | Creator evidence/read | Evidence refs | observed_at | Commercial implication |
|-------------|------------------------------|-----------------------|---------------|-------------|------------------------|
| Approved message | [message] | [read] | [opaque refs] | [date] | [implication] |
| Offer/CTA | [offer/CTA] | [read] | [opaque refs] | [date] | [implication] |
| Required tone/format | [constraint] | [read] | [opaque refs] | [date] | [implication] |
| Campaign conflict | [exclusion] | [read] | [opaque refs] | [date] | [implication] |

### Suitability and Trust Boundaries — Zero Commercial Points

| Control/read | Status | Evidence refs | Effect here |
|--------------|--------|---------------|-------------|
| `STAR-S8` deal-independent brand/category fit | [typed state] | [refs] | Context only; do not rescore |
| `STAR-T3` brand-safety control | [not assessed/potential finding from supplied evidence] | [refs] | Hand off to auditor; never turn it into commercial points or a verdict |

### Gaps and Hypotheses

- `evidence_gaps`: [[gap], ...]
- `message_hypothesis`: [falsifiable test or none; zero score/weight]

### `commercial_fit_score.message_offer_fit`: [1–5/NOT_SCORED]

**Evidence-backed rationale**: [campaign-specific explanation with refs]

**Weighted `commercial_fit_score` contribution**: [X] × [weight%] = [weighted points]
```

---

## Step 6 — Activation & Commercial Fit

```markdown
## Activation & Commercial Fit

**creator_ref**: [creator_ref]

### Deal and Activation Inputs

| Factor | Supplied requirement/term | Creator response/evidence | Evidence refs | observed_at | Commercial implication |
|--------|---------------------------|---------------------------|---------------|-------------|------------------------|
| Availability/window | [requirement] | [status] | [opaque refs] | [date] | [implication] |
| Deliverables/revisions | [requirement] | [status] | [opaque refs] | [date] | [implication] |
| Rights/usage scope | [requirement] | [status] | [opaque refs] | [date] | [implication] |
| Category conflicts/exclusivity | [constraint] | [status] | [opaque refs] | [date] | [implication] |
| Commercial terms/budget | [approved range] | [quoted terms or Unknown] | [opaque refs] | [date] | [implication] |

### STAR Boundaries — Zero Commercial Points

| STAR item | Typed state from Suitability read | Evidence refs | Effect here |
|-----------|-----------------------------------|---------------|-------------|
| `STAR-S5` | [state] | [refs] | Context only; do not rescore |
| `STAR-S6` | [state] | [refs] | A potential finding holds ranking/outreach; commercial points cannot offset it |
| `STAR-S7` | [state] | [refs] | Context only; do not rescore |

### Gaps

- `commercial_input_gaps`: [[missing quote/rights/availability/conflict evidence], ...]
- `decision_rule`: [supplied rule or NEEDS_INPUT]

### `commercial_fit_score.activation_commercial_fit`: [1–5/NOT_SCORED]

**Evidence-backed rationale**: [campaign-specific explanation with refs]

**Weighted `commercial_fit_score` contribution**: [X] × [weight%] = [weighted points]
```

---

## Step 7 — Partnership Execution Fit

```markdown
## Partnership Execution Fit

**creator_ref**: [creator_ref]

### Campaign-Relevant Execution Evidence

| Factor | Evidence/read | Evidence refs | observed_at | Commercial implication |
|--------|---------------|---------------|-------------|------------------------|
| Response/coordination history | [read] | [opaque refs] | [date] | [implication] |
| Delivery/revision history | [read] | [opaque refs] | [date] | [implication] |
| Asset handoff readiness | [read] | [opaque refs] | [date] | [implication] |
| Campaign-team workflow fit | [read] | [opaque refs] | [date] | [implication] |

### Suitability and Trust Boundaries — Zero Commercial Points

| Control/read | Status | Evidence refs | Effect here |
|--------------|--------|---------------|-------------|
| `STAR-S9` reliability/professionalism | [typed state] | [refs] | Context only; do not rescore |
| `STAR-S10` saturation/category history | [typed state] | [refs] | Context only; do not rescore |
| `STAR-T1` disclosure control | [not assessed/potential finding from supplied evidence] | [refs] | Hand off to auditor; never turn it into commercial points or a verdict |

### Contact and Source Hygiene

- `recipient_ref`: [opaque ref or Unknown]
- `contact_source_ref`: [opaque ref or Unknown]
- `evidence_gaps`: [[gap], ...]

### `commercial_fit_score.partnership_execution_fit`: [1–5/NOT_SCORED]

**Evidence-backed rationale**: [campaign-specific explanation with refs]

**Weighted `commercial_fit_score` contribution**: [X] × [weight%] = [weighted points]
```

---

## Step 8 — `commercial_fit_score` Rollup

```markdown
## `commercial_fit_score` Rollup

**creator_ref**: [creator_ref]
**Suitability read status**: [COMPLETE/NEEDS_INPUT]
**Potential Suitability control hold**: [none/STAR-S2/STAR-S6]
**Commercial scoring status**: [COMPLETE/PROVISIONAL/NEEDS_INPUT]

| `commercial_fit_score` component | Component score | User-approved weight | Weighted contribution | Evidence refs | observed_at |
|----------------------------------|-----------------|----------------------|-----------------------|---------------|-------------|
| Campaign audience activation fit | [1–5/NOT_SCORED] | [%] | [points] | [opaque refs] | [date] |
| Concept & format fit | [1–5/NOT_SCORED] | [%] | [points] | [opaque refs] | [date] |
| Message & offer fit | [1–5/NOT_SCORED] | [%] | [points] | [opaque refs] | [date] |
| Activation & commercial fit | [1–5/NOT_SCORED] | [%] | [points] | [opaque refs] | [date] |
| Partnership execution fit | [1–5/NOT_SCORED] | [%] | [points] | [opaque refs] | [date] |
| **`commercial_fit_score`** | | **100%** | **[X/5.00 or NOT_SCORED]** | | |

### Decision Readiness

- `commercial_fit_score`: [X/5.00/NOT_SCORED]
- `ranking_eligibility`: [ELIGIBLE/HOLD_FOR_SUITABILITY_INPUT/HOLD_FOR_COMMERCIAL_INPUT/HOLD_FOR_POTENTIAL_CONTROL]
- `declared_decision_rule`: [rule + owner + source ref, or NEEDS_INPUT]
- `action_under_declared_rule`: [PRIORITIZE_FOR_CAMPAIGN_PLANNING/RETEST/DEPRIORITIZE/NEEDS_INPUT]
- `rationale`: [rule + evidence refs; no generic rating]
- `rerun_condition`: [missing evidence or changed term/date]

Do not emit a generic “Verdict,” star rating, “Final Fit Score,” or “Final Score.” If the Suitability read is incomplete or a potential `STAR-S2`/`STAR-S6` finding stands, the creator is not ranking-eligible even when `commercial_fit_score` is numerically high. The action above is commercial planning advice under the declared rule, not a STAR gate verdict.
```

---

## Step 9 — Multi-Creator Comparison Report

```markdown
# Creator Commercial-Fit Comparison

**Campaign**: [name]
**Date**: [date]
**Creator refs evaluated**: [[creator_ref], ...]
**Shared typed context ref**: [opaque ref]
**Declared decision rule**: [rule + owner + source ref]

## Ranking-Eligible Creators

Rank only candidates with a complete applicable Suitability read, no unresolved potential control hold, complete commercial inputs, and the same campaign criteria/weights.

| Rank | creator_ref | Suitability read status | S2/S6 hold | `commercial_fit_score` | Evidence confidence | Action under declared rule |
|------|-------------|-------------------------|------------|------------------------|---------------------|----------------------------|
| [rank] | [creator_ref] | COMPLETE | none | [X/5] | [confidence] | [explicit action] |

## Not Ranked

| creator_ref | Suitability gaps/control | Commercial gaps | Status | Rerun condition |
|-------------|--------------------------|-----------------|--------|-----------------|
| [creator_ref] | [Unknown items/hold] | [gaps] | [NEEDS_INPUT/HOLD] | [condition] |

## Component Comparison

| `commercial_fit_score` component | [creator_ref-1] | [creator_ref-2] | [creator_ref-3] |
|----------------------------------|-----------------|-----------------|-----------------|
| Campaign audience activation fit | [X/5] | [X/5] | [X/5] |
| Concept & format fit | [X/5] | [X/5] | [X/5] |
| Message & offer fit | [X/5] | [X/5] | [X/5] |
| Activation & commercial fit | [X/5] | [X/5] | [X/5] |
| Partnership execution fit | [X/5] | [X/5] | [X/5] |
| **`commercial_fit_score`** | **[X/5]** | **[X/5]** | **[X/5]** |

## Planning Actions

1. [creator_ref]: [explicit action under the declared rule + evidence refs]
2. [creator_ref]: [explicit action under the declared rule + evidence refs]

No row in this comparison is a Suitability total, SQS, or auditor verdict.
```

---

## Custom Commercial Weighting

Record one approved weight set per campaign; do not silently select a preset.

| Weight-set ref | Campaign goal | Audience activation | Concept/format | Message/offer | Activation/commercial | Partnership execution | Total | Approved by/date |
|----------------|---------------|---------------------|----------------|---------------|-----------------------|-----------------------|-------|------------------|
| [opaque ref] | [goal] | [%] | [%] | [%] | [%] | [%] | 100% | [owner/date] |

Weights belong only to `commercial_fit_score`. They never alter the typed `STAR-S1`–`STAR-S10` states or the gate's profile weights.

---

## Worked Example

**User**: "Compare `creator-11111111-1111-4111-8111-111111111111`, `creator-22222222-2222-4222-8222-222222222222`, and `creator-33333333-3333-4333-8333-333333333333` for our sustainable-fashion campaign. The authorized discovery artifact supplies the typed campaign context, current dated evidence for every applicable `STAR-S1`–`STAR-S10` item, commercial criteria, approved weights, and decision rule."

**Output**: Emit one dated typed Suitability table per `creator_ref`, then the separately labeled `commercial_fit_score` components and rollup. Rank only eligible refs under the supplied rule; place incomplete or potential-control candidates in **Not Ranked** with exact gaps. Persist only opaque refs. Emit no raw identity locator, Suitability composite, SQS, generic Verdict, “Final Fit Score,” or “Final Score.”

---

## Tips for Success

1. **Be consistent** — use the same criteria for all influencers.
2. **Gather data** — more data = more accurate scores.
3. **Consider context** — scores are relative to campaign needs.
4. **Update regularly** — influencer quality changes over time.
5. **Trust but verify** — spot-check high scores before outreach.
