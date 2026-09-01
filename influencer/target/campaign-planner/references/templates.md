# Campaign Plan Templates

Fill-in templates for each step of [campaign-planner](../SKILL.md). Select `plan-only` for §§1–9, `tracker-only` for §10 from an existing campaign ID/plan/measurement contract, or `both` for §§1–9 followed by §10. Copy only the blocks for that mode. Replace a bracket only with a user-provided value or compatible source-dated planning evidence; an unsupported required choice remains `NEEDS_INPUT` and an optional field remains `Unknown`/omitted. §10 is a WARM execution tracker plus read-only derived views, not a campaign-plan schema or workflow runtime.

Back to the repo: [skill-contract.md](../../../../references/skill-contract.md) · [state-model.md](../../../../references/state-model.md) · [CONNECTORS.md](../../../../CONNECTORS.md).

## 1. Gather Campaign Requirements

```markdown
### Campaign Brief Input

**Brand Information**:
- Brand: [name]
- Product/Service: [description]
- Value Proposition: [key benefits]
- Target Audience: [demographics, psychographics]

**Campaign Context**:
- Campaign ID: [explicit upstream/user ID, or random campaign-<UUIDv4> generated once for a new plan]
- Campaign Type: [launch/awareness/seasonal/always-on]
- Reason for Campaign: [why now]
- Timeline: [start-end dates]
- Budget: [total budget or range]

**Constraints**:
- Must include: [requirements]
- Must avoid: [restrictions]
- Approvals needed: [stakeholders]
```

## 2. Define Campaign Objectives

```markdown
## Campaign Objectives

### Campaign Name: [Name]

### Primary Objective

**Goal**: [Specific objective]
**Metric**: [How it will be measured]
**Target**: [Specific number/percentage]

### Secondary Objectives

| Objective | Metric | Target |
|-----------|--------|--------|
| [Objective 1] | [metric] | [target] |
| [Objective 2] | [metric] | [target] |
| [Objective 3] | [metric] | [target] |

### SMART Goal Check

- ✅ **S**pecific: [how it's specific]
- ✅ **M**easurable: [how it's measured]
- ✅ **A**chievable: [why it's realistic]
- ✅ **R**elevant: [business alignment]
- ✅ **T**ime-bound: [timeline]

### Success Definition

**This campaign is successful if**:
- [Success criteria 1]
- [Success criteria 2]
- [Success criteria 3]

**This campaign fails if**:
- [Failure indicator 1]
- [Failure indicator 2]
```

## 3. Develop Campaign Strategy

```markdown
## Campaign Strategy

### Strategic Approach

**Big Idea**: [One-line campaign concept]

**Strategy Statement**:
We will [action] to [audience] by [method] resulting in [outcome].

### Target Audience

**Primary Audience**:
- Demographics: [details]
- Psychographics: [values, interests, lifestyle]
- Pain points: [challenges we address]
- Media behavior: [where they consume content]

**Secondary Audience** (if applicable):
- [Description]

### Key Messages

**Primary Message**:
> "[Core message]"

**Supporting Messages**:
1. [Message 1]
2. [Message 2]
3. [Message 3]

**Proof Points**:
- [Evidence/claim 1]
- [Evidence/claim 2]

### Campaign Pillars

| Pillar | Focus | Content Angle |
|--------|-------|---------------|
| [Pillar 1] | [focus area] | [content approach] |
| [Pillar 2] | [focus area] | [content approach] |
| [Pillar 3] | [focus area] | [content approach] |

### Platform Strategy

| Platform | Role | Content Focus | % Budget |
|----------|------|---------------|----------|
| [Platform 1] | Primary | [focus] | [%] |
| [Platform 2] | Secondary | [focus] | [%] |
| [Platform 3] | Supporting | [focus] | [%] |

### Competitive Differentiation

**What makes this campaign different**:
- [Differentiator 1]
- [Differentiator 2]
```

## 4. Define Influencer Criteria

See [influencer-tiers.md](influencer-tiers.md) for the declaration contract. This repository supplies no universal follower bands or partner-model choice; use a user-declared or compatible source-dated taxonomy, otherwise keep the band/mix `Unknown/NEEDS_INPUT`.

```markdown
## Influencer Strategy

### Creator Mix

| Declared band | Follower range | Platform/market | Taxonomy source/date | Quantity | Role | Budget % |
|---------------|----------------|-----------------|----------------------|----------|------|----------|
| [user/source-declared label or Unknown] | [range or NEEDS_INPUT] | [scope] | [opaque ref + date or NEEDS_INPUT] | [# or NEEDS_INPUT] | [role or NEEDS_INPUT] | [% or NEEDS_INPUT] |

### Selection Criteria

**Must-Have Requirements**:

| Criterion | Requirement | Priority |
|-----------|-------------|----------|
| Niche | [category] | Required |
| Platform | [platforms] | Required |
| Engagement Rate | >[%] | Required |
| Audience Demographics | [specs] | Required |
| Brand Safety | [criteria] | Required |
| Content Quality | [standard] | Required |

**Preferred Criteria**:

| Criterion | Preference | Weight |
|-----------|------------|--------|
| [Criterion 1] | [preference] | [weight] |
| [Criterion 2] | [preference] | [weight] |

**Exclusions**:
- No current competitor partnerships
- No controversial content history
- [Other exclusions]

### Ideal Influencer Profile

**Profile: "[Persona Name]"**

- Age: [range]
- Platform focus: [primary platform]
- Content style: [description]
- Audience: [description]
- Posting frequency: [frequency]
- Brand partnership style: [authentic/polished/etc.]
- Example creators: [creator_ref 1], [creator_ref 2]

### Relationship Type

| Type | Description | Quantity | Terms |
|------|-------------|----------|-------|
| [Type 1] | [description] | [#] | [terms] |
| [Type 2] | [description] | [#] | [terms] |
```

## 5. Plan Content Requirements

```markdown
## Content Plan

### Content Deliverables

| Deliverable | Platform | Format | Quantity/Influencer | Total |
|-------------|----------|--------|---------------------|-------|
| [Type 1] | [platform] | [format] | [#] | [#] |
| [Type 2] | [platform] | [format] | [#] | [#] |
| [Type 3] | [platform] | [format] | [#] | [#] |

**Total Content Pieces**: [#]

### Content Guidelines

**Required Elements**:
- [ ] Brand mention
- [ ] Product feature/demo
- [ ] Call-to-action: [specific CTA]
- [ ] Disclosure (#ad, #sponsored, etc.)
- [ ] Hashtags: [required hashtags]
- [ ] Link/Swipe-up: [URL]
- [ ] Promo code: [code]

**Creative Direction**:
- Tone: [description]
- Visual style: [description]
- Do's: [what to include]
- Don'ts: [what to avoid]

**Creative Freedom Level**: [High/Medium/Low]
- [Explanation of boundaries]

### Content Themes

| Theme | Description | % of Content | Example |
|-------|-------------|--------------|---------|
| [Theme 1] | [description] | [%] | [example] |
| [Theme 2] | [description] | [%] | [example] |

### Approval Process

| Stage | Reviewer | Timeline | Notes |
|-------|----------|----------|-------|
| Script/Concept | [who] | [days] before | [notes] |
| Draft Content | [who] | [days] before | [notes] |
| Final Approval | [who] | [days] before | [notes] |
```

## 6. Create Campaign Timeline

```markdown
## Campaign Timeline

### Key Dates

| Milestone | Date | Owner |
|-----------|------|-------|
| Campaign Kick-off | [date] | [owner] |
| Influencer Selection Complete | [date] | [owner] |
| Outreach Complete | [date] | [owner] |
| Contracts Signed | [date] | [owner] |
| Product Shipment | [date] | [owner] |
| Brief Delivery | [date] | [owner] |
| Content Due | [date] | [owner] |
| Content Review/Approval | [date] | [owner] |
| Content Goes Live | [date] | [owner] |
| Campaign Ends | [date] | [owner] |
| Final Report Due | [date] | [owner] |

### Detailed Timeline

**Phase 1: Pre-Campaign (Weeks 1-2)**

| Week | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 1 | Finalize strategy | [owner] | Strategy doc |
| 1 | Influencer identification | [owner] | Shortlist |
| 2 | Influencer outreach | [owner] | Confirmed partners |
| 2 | Contract negotiation | [owner] | Signed contracts |

**Phase 2: Production (Weeks 3-4)**

| Week | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 3 | Brief distribution | [owner] | Briefs sent |
| 3 | Product shipment | [owner] | Products delivered |
| 4 | Content creation | Influencers | Draft content |
| 4 | Content review | [owner] | Approved content |

**Phase 3: Activation (Weeks 5-6)**

| Week | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 5 | Content goes live | Influencers | Live posts |
| 5-6 | Community management | [owner] | Engagement |
| 5-6 | Real-time optimization | [owner] | Adjustments |

**Phase 4: Post-Campaign (Week 7+)**

| Week | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 7 | Data collection | [owner] | Raw data |
| 7 | Performance analysis | [owner] | Analysis |
| 8 | Final report | [owner] | Campaign report |

### Gantt View

\`\`\`
Week:        1    2    3    4    5    6    7    8
Strategy     ████
Selection    ████ ████
Contracts         ████ ████
Briefing               ████
Production              ████ ████
Live                         ████ ████
Analysis                               ████ ████
\`\`\`
```

## 7. Allocate Budget

```markdown
## Budget Allocation

### Total Budget: $[X]

### Budget Breakdown by Category

| Category | Amount | % of Total | Notes |
|----------|--------|------------|-------|
| Influencer Fees | $[X] | [%] | [notes] |
| Product/Gifting | $[X] | [%] | [notes] |
| Content Production | $[X] | [%] | [notes] |
| Paid Amplification | $[X] | [%] | [notes] |
| Agency/Tools | $[X] | [%] | [notes] |
| Contingency | $[X or NEEDS_INPUT] | [% or NEEDS_INPUT] | [user-approved rule or compatible source/date; omit if none] |
| **Total** | **$[X]** | **100%** | |

### Budget by Declared Creator Band

| Declared band | Taxonomy source/date | # Creators | Cost Each | Total | % |
|---------------|----------------------|------------|-----------|-------|---|
| [user/source-declared label or Unknown] | [opaque ref + date or NEEDS_INPUT] | [# or NEEDS_INPUT] | $[X or NEEDS_INPUT] | $[X or NEEDS_INPUT] | [% or NEEDS_INPUT] |

### Budget by Platform

| Platform | Budget | % | Rationale |
|----------|--------|---|-----------|
| [Platform 1] | $[X] | [%] | [reason] |
| [Platform 2] | $[X] | [%] | [reason] |

### Cost Efficiency Targets

| Metric | Target | Calculation | Planning anchor |
|--------|--------|-------------|-----------------|
| CPM | $[X or NEEDS_INPUT] | Budget ÷ (Estimated impressions/1000) | [user/source ref + date/window] |
| CPE | $[X or NEEDS_INPUT] | Budget ÷ Estimated engagements | [user/source ref + date/window] |
| Cost per Content | $[X or NEEDS_INPUT] | Budget ÷ Content pieces | [user/source ref + date/window] |
```

## 8. Establish Success Metrics

```markdown
## Success Metrics & KPIs

### Primary KPIs

| KPI | Target | External comparator | Comparator source/date/window/cohort | Measurement |
|-----|--------|---------------------|--------------------------------------|-------------|
| [KPI 1] | [target or NEEDS_INPUT] | [value or Unknown] | [opaque ref + date/window/cohort or NEEDS_INPUT] | [how measured] |
| [KPI 2] | [target or NEEDS_INPUT] | [value or Unknown] | [opaque ref + date/window/cohort or NEEDS_INPUT] | [how measured] |
| [KPI 3] | [target or NEEDS_INPUT] | [value or Unknown] | [opaque ref + date/window/cohort or NEEDS_INPUT] | [how measured] |

### Secondary Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Total Reach | [X] | |
| Total Impressions | [X] | |
| Engagement Rate | [%] | |
| Video Views | [X] | |
| Link Clicks | [X] | |
| Promo Code Uses | [X] | |
| EMV Generated | $[X] | |

### Conversion Metrics (if applicable)

| Metric | Target | Attribution |
|--------|--------|-------------|
| Website Visits | [X] | UTM tracking |
| Conversions | [X] | Promo codes + pixels |
| Revenue | $[X] | Attribution model |
| ROAS | [X]:1 | Revenue ÷ Spend |

### Benchmarks

| Metric | Our Target | External Comparator | Comparator Source | Observed At | Window/Cohort | Past Campaign Ref |
|--------|------------|---------------------|-------------------|-------------|---------------|-------------------|
| [metric] | [target] | [value or Unknown] | [source_ref or NEEDS_INPUT] | [date] | [window/cohort] | [opaque artifact ref or Unknown] |

Do not invent an "industry average" or carry an undated comparator forward. If the source, observation date, or comparable window/cohort is missing, keep the comparator `Unknown`/`NEEDS_INPUT`; a target remains a planning assumption, not measured evidence.

### Reporting Cadence

| Report | Frequency | Contents | Audience |
|--------|-----------|----------|----------|
| Daily Tracker | Daily | Live metrics | Team |
| Weekly Update | Weekly | Performance summary | Stakeholders |
| Final Report | Post-campaign | Full analysis | Leadership |

### Pre-Execution Measurement Contract

Lock this non-canonical agreement before execution. It is `locked` only when the exact campaign/plan binding, immutable plan version/hash, authorization, non-empty creator scope, and complete structured checkpoint list exist. Otherwise use `contract_status: needs-input`, list the missing values, and do not supply this block to a close-eligible tracker.

measurement_contract:
  measurement_contract_ref: measurement-contract-[random UUIDv4]
  campaign_id: [same stable campaign ID as §§1 and 9]
  plan_ref: [exact immutable/versioned plan artifact ref]
  plan_version: [immutable plan version]
  plan_sha256: [SHA-256 of the exact plan version]
  contract_version: [immutable contract version]
  supersedes_measurement_contract_ref: [exact prior contract head or null]
  contract_status: locked
  locked_at: [ISO-8601 timestamp]
  lock_authorization_ref: [exact current approval/decision reference]
  baseline_ref: [dated source, entity, metric, and comparison window]
  outcome_unit: [single decision unit, such as verified orders or qualified leads]
  readback_window: [measurement start/end dates or explicit post-publication lag]
  attribution_basis: [promo code, UTM plus analytics rule, lift design, or other stated basis]
  decision_rule: [numeric renew/retest/stop threshold and treatment of inconclusive data]
  decision_owner: [person or role authorized to apply the rule]
  creator_scope:
    creator_scope_ref: creator-scope-[random UUIDv4]
    scope_version: [immutable scope version]
    scope_authorization_ref: [exact approval for this roster]
    creator_refs: [non-empty, duplicate-free list of stable opaque creator_ref values]
  required_publication_checkpoints:
    - checkpoint_ref: publication-checkpoint-[random UUIDv4]
      campaign_id: [same campaign_id]
      creator_ref: [one exact creator_ref from creator_scope.creator_refs]
      deliverable_ref: [exact contracted/planned deliverable ref]
      checkpoint_type: [first-observed | preregistered-readback | pre-amplification]
      trigger_at: [ISO-8601 timestamp or evidence-defined trigger]
      applicability: required

Every `checkpoint_ref` is unique across the contract and binds exactly one campaign, creator, deliverable, and checkpoint type. Include every required instance for every creator in scope; do not use a global `readback` label as a reusable checkpoint ID. A locked contract has one non-forked supersession head. Changing the plan hash/version, creator scope, checkpoint set, attribution, window, or decision rule creates a new contract ref and requires the explicit §10 migration—never edit the locked block in place. A missing creator roster can remain a clearly labeled planning open loop, but execution tracking and close stay blocked until a non-empty scope and its checkpoint instances are locked.
```

## 9. Compile Campaign Plan Document

```markdown
# Campaign Plan: [Campaign Name]

## Executive Summary

**Campaign ID**: [stable campaign_id]
**Campaign**: [Name]
**Brand**: [Brand]
**Timeline**: [Dates]
**Budget**: $[X]
**Goal**: [Primary objective in one sentence]

**The Plan in Brief**:
[2-3 sentence summary of the campaign approach]

---

[Full sections as detailed above]

---

## Appendix

### A. Influencer Shortlist
[Link to influencer discovery results]

### B. Brief Template
[Link to brief-generator output]

### C. Content Examples
[Reference content examples]

### D. Approval Workflows
[Detailed approval process]

### E. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk 1] | [H/M/L] | [H/M/L] | [action] |
| [Risk 2] | [H/M/L] | [H/M/L] | [action] |

---

**Document Version**: 1.0
**Last Updated**: [date]
**Owner**: [name]
**Approvals**: [required approvals]
```

## 10. Optional Lightweight Campaign Tracker

Use this only in `tracker-only` or `both` mode. `tracker-only` requires an existing `campaign_id`, exact immutable/versioned `plan_ref`, `plan_version`, `plan_sha256`, and the one current locked §8 contract head with a locked non-empty creator scope and complete unique checkpoints. Verify that every binding agrees before creating rows. Missing, mismatched, or forked input returns `NEEDS_INPUT`; never generate a tracker-only ID, reconstruct §§1–9, borrow another campaign's contract, or create placeholder evidence. In `both`, use the ID and plan from §§1–9. If creator selection is not locked, the plan may finish with an open loop, but any requested view remains explicitly partial and not close-eligible.

The source of record for governed tracking is the validated set of control artifacts and selected run ancestry, not this Markdown. Generate this section as a deterministic read-only projection and include:

```yaml
projection_metadata:
  authoritative: false
  verification_status: <VERIFIED | NOT_VERIFIED>
  source_artifact_refs: [<exact validated refs>]
  source_artifact_sha256: [<matching digests>]
  selected_head_ref: <exact non-forked head or null>
  generated_at: <ISO-8601 timestamp>
```

The YAML below is an **Influencer domain compatibility view**, not an instance of `references/control-artifact.schema.json`. Do not pass `tracker_write_authorization`, `publication_receipt`, `close_receipt`, or another domain block to `validate-control-artifact.py` or call that YAML schema-valid. Project only independently validated JSON controls using this deterministic mapping:

| Domain compatibility block | Shared control mapping |
|---|---|
| `tracker_write_authorization` and every `*_authorization_ref` / `write_authorization_ref` | Host authorization provenance only. When the host models the proposed mutation, put the exact provenance ref and observation time in `action-intent.permission_ref` / `permission_observed_at` with `permission_effect: provenance-only`; it never creates a sixth authorization artifact or grants authority. A matching `action-receipt` may record the host's actual completed mutation, never the approval alone. |
| `campaign_tracker_state`, locked scope/checkpoints, `tracker_migration`, identity/rights/payment state | Exact bindings and field facts projected from `measurement-contract` and `evidence-observation`; the view does not establish currentness. |
| `identity_resolution`, `publication_receipt`, `checkpoint_terminal_resolution`, and `late_event_note` | `evidence-observation` with the exact campaign/creator/checkpoint target binding, dated source bindings, field states, missingness/conflict, and readiness. A post observed live is evidence, not proof that this skill executed publication. |
| A real send, publish, amplify, pay, save, or other executor mutation | Exact `action-intent` before execution plus matching `action-receipt` after an observed executor result. The receipt binds the intent and actual target/content/scope; neither artifact authorizes the action. |
| `close_receipt` and `campaign_close_receipt` | A domain read of a validated `cycle-retro` plus its measurement contract and evidence observations. Closing the view is a decision projection, not an external-action receipt. |

The shared schema still has exactly five kinds: `evidence-observation`, `measurement-contract`, `action-intent`, `action-receipt`, and `cycle-retro`. The labels retained below exist for backward-compatible Influencer rendering only.

Changing or tampering with the projection does not change source artifacts, current head, close eligibility, or runtime state; regenerate it from the source set. A standalone host without the validator may return the same structure inline or, after exact path-scoped WARM authorization, save a **semantic-only compatibility snapshot** at a path such as `memory/influencer/campaign-planner/YYYY-MM-DD-<campaign>-tracker.md`. Such a snapshot must say `authoritative: false` and `verification_status: NOT_VERIFIED`; it does not create a schema, drive a workflow runtime, mutate a registry, prove persistence/currentness, or authorize outreach, publication, amplification, payment, or another external action.

### Legacy Compatibility-Snapshot Save Gate

This gate applies only to saving a semantic-only compatibility snapshot when governed projection is unavailable. Return the complete proposed snapshot inline, then obtain a fresh exact WARM authorization naming the normalized snapshot path and bounded save operation. Future changes are new complete snapshots projected from the available source evidence; never treat an edit to the old Markdown as a runtime mutation. A prior save approval, a blanket "keep tracking" instruction, a business decision, or authority for another path/operation is not reusable and never authorizes an external action.

Record or cite the authorization beside the mutation, never inside the eight-field active creator block:

```yaml
tracker_write_authorization:
  authorization_ref: <fresh exact user/authorized-artifact ref>
  tracker_path: <exact normalized WARM path>
  operation: <exact single mutation or explicitly bounded atomic transaction>
  target_refs: [<new/existing object refs and exact fields/pointers>]
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref, or null only for campaign-level mutation>
```

An atomic operation such as `close-creator`, `close-campaign`, `manual-reopen`, or `migrate-contract-scope` is authorized only when `operation`/`target_refs` enumerate every included append, stage/evidence change, and pointer update. Anything not named needs another new authorization. Missing, stale, reused, wrong-path, or broader-than-proposed authorization returns the patch inline and performs no write.

### Campaign Binding and Current State

Put campaign-level state in this separate header; it is not a creator field:

```yaml
campaign_tracker_state:
  campaign_id: <exact bound campaign ID>
  plan_ref: <exact immutable/versioned campaign-plan ref>
  plan_version: <exact bound plan version>
  plan_sha256: <exact bound SHA-256>
  measurement_contract_ref: <exact current locked §8 contract head>
  creator_scope_ref: <exact locked non-empty scope ref from that contract>
  scope_version: <exact immutable scope version>
  expected_creator_refs: [<duplicate-free non-empty list exactly equal to the locked scope>]
  current_state: open
  evidence_refs: [<plan, contract, scope, migration, and campaign-level evidence refs>]
  current_close_receipt_ref: null
```

The set of creator rows must exactly equal `expected_creator_refs`; an omitted, duplicated, or extra creator blocks close. `current_state` is `open | closed`. It is `closed` only when `current_close_receipt_ref` points to the unique non-forked current campaign-close head and that receipt still passes every gate. Historical close refs remain in `evidence_refs`. Update any header field only with a fresh authorization naming this exact tracker path, field/pointer, old value, and new value.

### Explicit Contract/Scope Migration

Never edit a locked plan binding, contract, creator scope, or checkpoint list in place. First append a new contract version whose `supersedes_measurement_contract_ref` points to the exact prior contract head, then record this migration:

```yaml
tracker_migration:
  migration_ref: tracker-migration-<UUIDv4>
  campaign_id: <same campaign_id>
  supersedes_migration_ref: <exact prior migration head or null>
  from_plan_ref: <old exact plan ref>
  to_plan_ref: <new exact plan ref>
  from_measurement_contract_ref: <old exact contract head>
  to_measurement_contract_ref: <new exact locked contract head>
  from_creator_scope_ref: <old exact scope ref>
  to_creator_scope_ref: <new exact non-empty scope ref>
  creator_ref_mapping: [<old→new mapping refs, including null for authorized additions/removals>]
  checkpoint_ref_mapping: [<old→new mapping refs, including preserved completed evidence>]
  removed_creator_resolution_refs: [<evidence that removed rows have no remaining campaign obligation>]
  migrated_at: <ISO-8601 timestamp>
  migration_authorization_ref: <exact approval for this migration>
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + migrate-contract-scope operation>
  unresolved_mappings: []
```

The new contract must bind its new plan version/hash and full non-empty scope. `migration_authorization_ref` authorizes the business binding change; it does not authorize the tracker write. `write_authorization_ref` must be new and path+operation-scoped, and its atomic migration operation must enumerate the migration append plus every header, row, stage, evidence, and pointer update. Every preserved receipt remains historical and may control only a checkpoint explicitly mapped to an equivalent new checkpoint of the same campaign, creator, deliverable, unit, window, and meaning. A missing mapping, non-empty `unresolved_mappings`, removed creator with unresolved obligations, contract/migration fork, or header still pointing to the old binding blocks tracking transitions and close. Only after an authorized complete migration may the header and rows move to the new refs.

### Close-Ineligible Banner

Place this exact banner at the top whenever **any** close blocker exists:

```text
PARTIAL CHECKPOINT COVERAGE — NOT CLOSE-ELIGIBLE
```

Blockers include a missing/mismatched/forked plan, contract, migration, or creator scope; empty scope or row/scope inequality; unresolved/forked identity or live-post ref; missing/not-yet-observed/unknown/mismatched/cross-scope/forked checkpoint evidence; missing typed verification refs; invalid/forked terminal-checkpoint resolution; stale/forked close pointers; or an unresolved material late event. Show the exact blocker list. Ordinary tracker-save approval is insufficient: persist that snapshot only after a fresh single-use authorization names the exact WARM path, the exact partial-snapshot operation, and every listed blocker; otherwise return it inline and write nothing. A future checkpoint that is not yet due is still legitimately incomplete and keeps the banner—it is not evidence of failure.

### Creator Identity, Current Pointers, and Eight-Field Row

Reuse the explicitly carried opaque `creator_ref` from discovery/fit, or a creator-registry aggregate ID only when its identity link is verified. If only a raw handle/profile URL is available, generate one random `creator-<UUIDv4>` and reuse it for that unresolved lineage. A raw handle, name, URL, email, provider ID, or deterministic hash is never a `creator_ref`; do not persist the transient locator or a hidden map.

Keep one adjacent state block per scoped creator:

```yaml
creator_tracker_state:
  campaign_id: <same campaign_id>
  creator_ref: <same scoped creator_ref>
  current_identity_resolution_ref: <exact unique identity-resolution head>
  current_close_receipt_ref: null
```

Identity observations are immutable and same-scope superseding:

```yaml
identity_resolution:
  resolution_ref: identity-resolution-<UUIDv4>
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref>
  supersedes_resolution_ref: <exact prior identity-resolution head or null>
  identity_status: <resolved | unresolved>
  resolver_ref: <exact authorized identity artifact or verified registry-link ref; null when unresolved>
  verification_evidence_refs: [<refs proving resolver_ref binds this creator; empty when unresolved>]
  observed_at: <ISO-8601 timestamp>
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + identity append/pointer operation>
```

The current pointer must identify the one unsuperseded same-campaign/same-creator head. Two resolutions that supersede the same prior head, a cross-scope pointer, or a missing link is a fork and blocks action/close even if the pointer selects one branch. `resolved` requires non-null `resolver_ref` and non-empty qualified `verification_evidence_refs`; add all exact refs to the active row only when the fresh `write_authorization_ref` names the identity append, evidence append, and pointer update. Otherwise retain `unresolved`, request the transient locator again next session, and block cross-session external action and close.

Copy this active block once per `expected_creator_refs` value and keep it at **exactly eight fields**:

```yaml
campaign_id: <existing campaign identifier>
creator_ref: <creator-UUIDv4 or verified creator-registry aggregate ID>
stage: shortlisted
next_action: <single concrete action and owner>
due_at: <ISO-8601 timestamp or null>
rights_expiry: <ISO-8601 date or null>
evidence_refs: [<identity, state, receipt, and dated evidence refs>]
payment_status: not-ready
```

- `stage`: `shortlisted | contacted | negotiating | contracted | submitted | revision | approved | published | measured | closed`.
- `payment_status`: `not-ready | handoff-ready | externally-paid | not-applicable`.

Advance or roll back `stage`, or change any other active-row field, only from exact supporting refs and after a fresh authorization names the exact tracker path, creator, field, old value, and new value. For `published`, `due_at` is the next scheduled readback; otherwise it is the next campaign-owned action due date. `handoff-ready` never means paid. `externally-paid` needs external completion evidence. `not-applicable` needs terms/terminal evidence proving no obligation; it is never a substitute for unknown or overdue. None of these values sends money.

Generate each resolution/receipt/event/migration ref once from random UUIDv4 using the shown prefix. Preserve it, never recycle it, and never derive it from timestamps, handles, content, or evidence. All adjacent objects must match the tracker campaign; creator-level objects must also match the row creator. A cross-scope object is invalid, not reusable evidence.

### Publication Receipt and Typed Verification Gate

Append a receipt for each observation of an exact checkpoint from the current locked contract:

```yaml
publication_receipt:
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref as the checkpoint and row>
  checkpoint_ref: <exact unique checkpoint_ref from the current locked contract>
  receipt_ref: publication-receipt-<UUIDv4>
  supersedes_receipt_ref: <exact current head for this campaign/creator/checkpoint or null>
  live_post_ref: <opaque qualified-resolver-backed live-post ref or unknown>
  live_post_resolver_ref: <exact qualified resolver/artifact ref or null>
  observed_at: <ISO-8601 timestamp>
  live_snapshot_ref: <dated screenshot/platform export or unknown>
  observation_source_ref: <exact user-supplied or qualified-tool observation ref>
  approved_asset_ref: <frozen approved asset/caption version or unknown>
  approved_asset_audit_ref: <exact creator-content-auditor approval ref or null>
  disclosure_status: unknown
  disclosure_evidence_ref: null
  approved_match_status: unknown
  approved_match_evidence_ref: null
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + append-publication-receipt/evidence operation>
```

- `disclosure_status`: `verified | mismatch | unknown | not-applicable`.
- `approved_match_status`: `verified | mismatch | unknown` for live media, caption, claims, CTA, and all approved elements.

Refs other than the new `receipt_ref` must already be supplied by the user, carried from authorized artifacts, or observed through a qualified connector; never invent them. `live_post_ref` is saved only when it is an opaque object/artifact ref that `live_post_resolver_ref` can resolve to this exact post. A raw/canonical URL, slug, shortcode, handle, provider post ID, or deterministic hash remains transient lookup input: never put it in any tracker field (including `live_post_ref`, `observation_source_ref`, or `evidence_refs`) or a hidden map; if no qualified opaque ref exists, use `live_post_ref: unknown` and `live_post_resolver_ref: null`. `disclosure_status: verified | mismatch | not-applicable` requires a non-null exact `disclosure_evidence_ref`; `not-applicable` additionally requires evidence of no disclosure obligation. `approved_match_status: verified | mismatch` requires a non-null exact `approved_match_evidence_ref`, a non-unknown frozen `approved_asset_ref`, non-null `approved_asset_audit_ref`, and non-unknown opaque live-post ref, resolver, live snapshot, plus observation source. Thus `approved_match_status: verified` can never coexist with an unknown/unresolved `live_post_ref` or `approved_asset_ref: unknown`. Missing evidence stays `unknown`.

The first receipt for the `(campaign_id, creator_ref, checkpoint_ref)` chain uses `supersedes_receipt_ref: null`; every later one points to that tuple's exact single current head. Missing/cyclic/cross-scope links or two receipts superseding the same head create a fork and block both branches. Close uses only the unique unsuperseded head. A later evidence-backed verified receipt may supersede an initial unknown without deleting history. Append the receipt and row evidence only after its fresh exact `write_authorization_ref`; it may cover both only when the bounded operation names both changes. A mismatch, removed/private post, unresolved raw locator, or changed live asset stays blocked and routes to [creator-content-auditor](../../../../influencer/activate/creator-content-auditor/SKILL.md); the tracker never edits the post or starts amplification.

### Terminal Checkpoint Non-Applicability Resolution

`declined`, `cancelled`, or `no-response` may make an unfulfilled publication checkpoint inapplicable. Do not fabricate a publication receipt. Append this evidence-backed alternative head for each such checkpoint:

```yaml
checkpoint_terminal_resolution:
  resolution_ref: checkpoint-resolution-<UUIDv4>
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref>
  checkpoint_ref: <exact checkpoint from the current locked contract>
  supersedes_resolution_ref: <exact prior resolution head for this tuple or null>
  terminal_outcome: <declined | cancelled | no-response>
  resolution_status: not-applicable
  resolved_at: <ISO-8601 timestamp>
  resolution_authorization_ref: <exact authorized terminal decision/cadence-stop ref>
  evidence_refs: [<decline, cancellation, cadence-stop, and no-obligation evidence>]
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + append-terminal-resolution/evidence operation>
```

The same-scope chain must have one head; a fork blocks close. `resolution_authorization_ref` authorizes the terminal business decision; it does not authorize a tracker mutation, which requires the separate fresh `write_authorization_ref`. A resolution cannot hide an already observed mismatch, removed post, live obligation, or unpaid commitment. `completed` never uses it. `measurement-unavailable` still requires verified publication heads for fulfilled deliverables. For each checkpoint, creator close must cite either its unique verified publication head or its unique terminal-resolution head, never neither or both for the same unresolved obligation.

### Creator Close Receipt and Gate

Append beside the creator only when moving to `stage: closed`:

```yaml
close_receipt:
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref>
  receipt_ref: creator-close-receipt-<UUIDv4>
  supersedes_receipt_ref: <exact most recent historical creator-close head or null>
  terminal_outcome: <completed | declined | cancelled | no-response | measurement-unavailable>
  closed_at: <ISO-8601 timestamp>
  identity_resolution_ref: <exact current resolved identity head>
  checkpoint_receipt_refs: [<controlling verified publication heads>]
  checkpoint_terminal_resolution_refs: [<controlling allowed non-applicability heads>]
  measurement_readback_ref: <exact §8 readback/accepted limitation ref or null>
  rights_evidence_ref: <exact signed rights/no-obligation ref or null>
  payment_evidence_ref: <exact external-paid/no-obligation ref or null>
  terminal_evidence_refs: [<outcome-specific evidence refs>]
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + atomic close-creator transaction>
```

Minimum gates:

| Terminal outcome | Evidence required before close |
|------------------|--------------------------------|
| `completed` | Resolved identity; every checkpoint has its current verified publication head; contracted deliverables were approved/fulfilled; exact measured §8 readback, signed rights scope/expiry, and external-paid/not-applicable evidence exist. No terminal checkpoint resolution is allowed. |
| `declined` | Explicit decline, no commitment/obligation, and a current terminal-resolution head for every unfulfilled checkpoint. Silence is not decline. |
| `cancelled` | Authorized cancellation/effective date, resolved deliverable/rights/payment obligations, and current receipt or terminal-resolution coverage for every checkpoint as applicable. |
| `no-response` | Approved cadence and wait/stop condition ended, no follow-up/other obligation remains, and a current terminal-resolution head covers every unfulfilled checkpoint. |
| `measurement-unavailable` | Resolved identity and verified publication heads for fulfilled checkpoints; unusable source evidence; explicit §8 decision-owner acceptance; resolved rights/payment. |

Every close ref is unique and same-scope. The first creator close uses `supersedes_receipt_ref: null`; every correction/reclose supersedes the exact most recent historical creator-close head, including after manual reopen. A fork blocks all branches. The fresh `write_authorization_ref` must name the close-receipt append, `stage: closed`, `next_action`, `due_at`, evidence append, and `creator_tracker_state.current_close_receipt_ref` update as one atomic `close-creator` transaction; anything omitted needs a different new authorization. Apply them only after the gate passes. On a separately authorized manual reopen set the pointer to null but retain historical heads. A close pointer that is not the unique head is stale and blocks campaign close. `closed` means no remaining campaign-owned action, not success.

At close, do not promote the tracker wholesale. With separate authorization, only evidence-backed actual rate, signed rights window/expiry, and measured performance baseline may be proposed to [creator-registry](../../../../protocol/creator-registry/SKILL.md).

### Campaign Close Receipt and Gate

Append only after deriving exact state from the locked scope and current creator-close heads:

```yaml
campaign_close_receipt:
  campaign_id: <same campaign_id>
  receipt_ref: campaign-close-receipt-<UUIDv4>
  supersedes_receipt_ref: <exact most recent historical campaign-close head or null>
  creator_scope_ref: <exact current locked non-empty scope ref>
  measurement_contract_ref: <exact current locked contract head>
  closed_at: <ISO-8601 timestamp after latest supporting evidence>
  creator_close_receipts:
    - creator_ref: <exact scoped creator_ref>
      receipt_ref: <that creator state’s exact current close head>
  terminal_counts:
    completed: <count>
    declined: <count>
    cancelled: <count>
    no-response: <count>
    measurement-unavailable: <count>
  measurement_report_ref: <dated performance/final report and §8 readback ref>
  budget_payment_reconciliation_ref: <dated actual-budget/payment reconciliation>
  unresolved_exceptions: []
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + atomic close-campaign transaction>
```

The campaign gate passes only when:

1. The plan/contract/migration chains are non-forked and current; creator scope is locked, non-empty, and duplicate-free; header, rows, contract checkpoints, and `creator_close_receipts` have exact creator-set equality. Each mapping uses that creator's unique current close head once—no ref reuse.
2. Every creator is `closed`, its state pointer matches its close head, identity head is resolved, and every contract checkpoint has exactly one applicable controlling object: a typed verified publication head, or an allowed terminal-resolution head consistent with that creator's terminal outcome. Mixed terminal outcomes are valid evidence states, not campaign success.
3. No unknown/mismatch, chain fork, cross-scope object, removed/private post, rights issue, unresolved material late event, or other close blocker remains.
4. `measurement_report_ref` covers the locked §8 campaign readback. Each `measurement-unavailable` limitation is explicitly accepted by the §8 decision owner and preserved, not counted as measured.
5. `budget_payment_reconciliation_ref` reconciles planned/actual spend and every creator's payment evidence. No row is `not-ready` or `handoff-ready`; each is evidence-backed `externally-paid` or `not-applicable`.
6. Every row has `due_at: null`; no campaign-owned exception remains; terminal counts derive from the mapped close heads, sum exactly to the non-zero scope count, and `unresolved_exceptions` is exactly `[]`.

The first campaign close has `supersedes_receipt_ref: null`; every later correction/reclose supersedes the exact most recent historical campaign-close head, even after a manual reopen. A fork blocks close. If a gate fails, keep `current_state: open`, do not append a partial close receipt, and show the banner. When all gates pass, the fresh `write_authorization_ref` must name the campaign-close append, campaign-evidence append, `current_state: closed`, and `current_close_receipt_ref` update as one atomic `close-campaign` transaction; apply only those named changes.

### Material Late Event, Correction, and Manual Reopen

Append one immutable note per exactly affected object; never insert it into the eight-field row:

```yaml
late_event_note:
  event_ref: late-event-<UUIDv4>
  campaign_id: <same campaign_id>
  creator_ref: <same creator_ref, or null only for a campaign-level object>
  observed_at: <ISO-8601 timestamp>
  event_type: <allowed value>
  source_ref: <dated external evidence ref>
  affected_evidence_ref: <one exact existing same-scope object ref>
  impact: <fact, close gate, or action that may change>
  decision: <no-change | supersede-artifact | manual-reopen>
  supersedes_ref: <exact old comparable artifact/receipt ref or null>
  replacement_ref: <exact newly appended corrected artifact/receipt ref or null>
  campaign_owned_next_action: <one concrete action or null>
  action_owner: <named owner or null>
  due_at: <ISO-8601 timestamp or null>
  write_authorization_ref: <fresh exact WARM approval binding this tracker path + append-late-event operation and any named state/pointer changes>
```

- `event_type`: `rights-revoked | rights-disputed | post-removed | late-attribution | payment-reversal | data-correction`.
- `affected_evidence_ref` identifies one existing object. Put new external evidence in `source_ref`. If multiple creator/campaign receipts are directly affected, append separately scoped notes so each pointer is singular.
- `no-change` requires evidence that no support/action changes; both supersession fields and all three action fields are null.
- `supersede-artifact` requires non-null `supersedes_ref` and `replacement_ref`. The replacement must already exist, be same campaign/creator/type/unit/window/meaning, have equal-or-higher authority, and itself point to the old current head where its schema has a supersession field. The two refs cannot be equal. A second replacement of the same head is a fork, not a selectable correction. Its three action fields are null when no work is created.
- `manual-reopen` keeps both supersession fields null and requires non-null `campaign_owned_next_action`, `action_owner`, and real `due_at`; it invalidates current close use without rewriting or superseding historical close receipts.

If a comparable corrected measurement, reconciliation, identity, checkpoint, or receipt changes close-support refs but all gates still pass and no new work exists, preserve history and append fresh same-chain creator/campaign close receipts as affected, moving pointers directly to the fresh heads without an open/reopen cycle. If corrected evidence fails a gate, do not append a passing receipt. Either record an evidence-backed campaign-owned resolution action and use `manual-reopen`, or report the tracker stale/not close-eligible until an owner supplies that resolution; never leave a known-invalid receipt presented as current.

Use this baseline only after evidence creates new campaign-owned work:

| Event type | Baseline stage | Required `next_action` baseline |
|------------|----------------|---------------------------------|
| `rights-revoked` / `rights-disputed` | `published` if the post remains live; otherwise latest supported pre-publication stage | Named rights owner resolves pause/remove/re-license scope and records evidence. |
| `post-removed` | `approved` if the frozen approved asset remains valid; otherwise `submitted`/`revision` as supported | Named content owner verifies cause and obtains restore, replacement, or authorized waiver evidence. |
| `late-attribution` | `published` until corrected §8 readback completes | Named measurement owner reruns locked readback/reconciliation. |
| `payment-reversal` | `measured` if measurement remains valid; otherwise latest supported earlier stage | Named finance/ops owner resolves reversal and records external payment evidence. |
| `data-correction` | Latest stage whose prerequisites remain supported | Named evidence owner regenerates the affected artifact/gate and records the corrected ref. |

Latest non-forked evidence overrides the baseline; an event never advances stage by itself. Append the event/evidence refs only under its fresh path-and-operation-scoped `write_authorization_ref`. For a creator-specific manual reopen, that atomic authorization must also name copying its action/owner/due date into the active row, returning the creator to the supported existing stage, and nulling its current-close pointer. For a campaign-level event (`creator_ref: null`), keep unaffected creator rows and pointers closed and carry the campaign-owned action only in this note. In both cases, any campaign `current_state: open` and `current_close_receipt_ref: null` changes must also be named; otherwise request another new authorization. Retain all historical refs and do not add a `reopened` stage. After resolution, each fresh creator close and campaign close requires its own new path+operation-scoped authorization and supersedes its most recent historical same-scope head. Every live-post, rights, payment, or other external mutation still needs separate exact approval.

### Read-Only Exception Queue

Generate only when requested, using explicit `as_of` and user-selected rights horizon. A creator may appear in multiple rows:

| Queue | Derived condition |
|-------|-------------------|
| Evidence/scope blocker | Any condition requiring the close-ineligible banner. |
| Overdue action | `stage != closed` and non-null `due_at < as_of`. |
| Published, measurement due | `stage == published` and non-null `due_at <= as_of`. |
| Payment handoff pending | `payment_status == handoff-ready`. |
| Rights expiring | Non-null `rights_expiry` falls from `as_of` through `as_of + selected horizon`. |

Render only `queue`, `campaign_id`, `creator_ref` (or null for campaign-level blockers), trigger date, current `next_action`, and existing evidence refs. This is an inline read-only projection: never write it back, schedule/poll it, or mutate state from it without a new exact authorization naming the tracker path and exact operation.

## Worked Example

**User**: "Create a campaign plan for a new sustainable sneaker launch targeting Gen Z on TikTok and Instagram with a $50K budget"

**Output**: Return a useful plan skeleton with the supplied audience, platforms,
and $50K total. Mark sustainability claim/message canon, creator mix, content
format, promo/attribution mechanic, rates, contingency, KPI targets, and exact
dates `NEEDS_INPUT` unless the user supplies them or compatible source-dated
planning anchors. Do not infer a micro-heavy mix, UGC focus, promo code, 10%
buffer, or any other strategy/budget default from this prompt.

## Tips for Success

1. **Start with clear objectives** — everything else flows from goals.
2. **Know your audience deeply** — use audience-mapper insights.
3. **Anchor the mix** — use the user-approved or source-dated taxonomy and decision rule; do not apply a universal tier mix.
4. **Build in flexibility** — plans need room to adapt.
5. **Set realistic targets** — use benchmarks from past campaigns.
