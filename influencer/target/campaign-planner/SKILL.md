---
name: campaign-planner
slug: aaron-campaign-planner
displayName: "Campaign Planner · 活动规划"
summary: "红人活动整体规划:目标、阶段、创作者组合、时间线与风险预案"
description: 'Use when the user asks to "plan an influencer campaign", "build a campaign blueprint", "track or close a creator campaign", or "record a late campaign correction"; produces the plan and, when requested, a non-canonical evidence tracker with scoped identity, publication, reconciliation, close, and reopen receipts. Not for individual creator briefs — use brief-generator; not for overall product launches without creators — use launch-tier-planner; not for sending, publishing, amplifying, or paying — use the owning execution workflow. 达人营销策划/种草方案/活动追踪与关账'
version: "20.1.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when planning a new influencer campaign, launching a product with influencer support, building seasonal or always-on creator programs, or maintaining an existing creator-campaign tracker: recording verified publication checkpoints, deriving exception queues, reconciling payment/measurement evidence, closing creators or the campaign, and handling late evidence or manual reopen. Planning does not write briefs or execute outreach; tracking does not publish, amplify, pay, or mutate external systems."
argument-hint: "<brand or product> [budget] [platform] [timeframe]"
metadata: {"author": "aaron-he-zhu", "version": "20.1.0", "discipline": "influencer", "phase": "target", "geo-relevance": "low", "hermes": {"tags": ["marketing", "influencer", "target"], "category": "influencer"}, "openclaw": {"emoji": "📣", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Campaign Planner

Designs an influencer campaign from strategy to execution plan — an actionable blueprint that ties business objectives to creative execution.

**Scope edge — product launches**: this skill owns the **creator lane** of a launch. The launch itself — tier/type decision, launch calendar, press motion, community launch day, readiness gate — belongs to the launch discipline ([launch-tier-planner](../../../launch/research/launch-tier-planner/SKILL.md) and siblings), which hands this skill the creator-channel sub-plan aligned to the [launch-registry](../../../protocol/launch-registry/SKILL.md) date and stage. "Launch a product with creators" starts here; "launch a product" starts there.

## Quick Start

```
Create an influencer campaign plan for [product launch]
```

```
Plan an influencer campaign for [brand] with [budget] targeting [audience] during [timeframe]
```

## Skill Contract

- **Reads**: requested mode (`plan-only | tracker-only | both`); brand, product, audience, campaign type, budget, timeline, and constraints for plan authoring; and, for execution-ready tracking, an existing `campaign_id`, exact versioned campaign-plan reference/hash, locked §8 measurement contract, and locked non-empty creator scope. If `memory-management` is active, prior audience profiles and past-campaign benchmarks load from the hot cache.
- **Writes**: the campaign plan inline by default. With exact save authorization, write it to `memory/influencer/campaign-planner/YYYY-MM-DD-<topic>.md`. For execution tracking, emit separate JSON artifacts that validate against the shared five-kind control schema (evidence observations, the locked measurement contract, action intents/receipts only for an actual executor action, and the Cycle Retro), then let the controller bind their exact refs/hashes to the selected run ancestry. The Markdown/YAML tracker in [references/templates.md §10](references/templates.md#10-optional-lightweight-campaign-tracker) is a deterministic **read-only Influencer compatibility view**, marked `authoritative: false`; its domain blocks are not themselves schema-valid control artifacts, and editing them never changes runtime state. Standalone hosts without the validator may save a semantic-only compatibility snapshot after exact WARM authorization, but it must be marked `NOT_VERIFIED` and cannot claim single-head, receipt, persistence, or close enforcement. Reuse an explicit upstream/user `campaign_id`; in a plan-authoring mode, generate one random `campaign-<UUIDv4>` if none exists and preserve it through the lineage. `tracker-only` never invents a missing ID, plan, contract, scope, or checkpoint. Every row preserves a stable opaque `creator_ref`; every saved `live_post_ref` is qualified-resolver-backed and opaque. Raw names, handles, URLs, shortcodes, provider IDs, and hidden locator maps remain transient.
- **Promotes**: only with separate exact authorization, promote approved campaign name, objective, budget, go-live date, and KPI targets to `memory/hot-cache.md`; never promote tracker stages or payment state. After a creator row is closed, another exact authorization is required for each registry proposal containing evidence-backed **actual rate**, **signed rights window/expiry**, or **measured performance baseline**; only [creator-registry](../../../protocol/creator-registry/SKILL.md) can make those facts canonical. Forecast targets, `stage`, `next_action`, `due_at`, and `payment_status` remain WARM working state.
- **Done when**:
  - The selected mode is explicit: `plan-only` completes §§1–9, `tracker-only` completes only §10 from its required existing inputs, and `both` completes §§1–9 before §10.
  - In a plan-authoring mode, objectives, strategy, influencer mix, deliverables, timeline, budget allocation, contingency, and KPIs are concrete only where the user supplied them or a compatible source-dated planning anchor supports them. Every unsupported required choice stays `NEEDS_INPUT`; the skill never fills it from a repository default. The §8 measurement design is execution-locked only when its campaign/plan binding, immutable plan hash/version, authorization, non-empty creator scope, and unique per-creator/deliverable checkpoints are present; otherwise report the exact lock inputs as `NEEDS_INPUT`/`DONE_WITH_CONCERNS` and do not create a close-eligible tracker.
  - If tracking was requested, each creator has validated source artifacts and one deterministic non-authoritative projection block with stage, next action, due date, rights expiry, evidence references, and external-payment handoff state. The projection carries its source artifact refs/digests and current head; it is never hand-edited as the state source.
  - Each tracker creator uses one stable opaque `creator_ref`; every identity resolution, publication, terminal-checkpoint resolution, creator close, campaign close, migration, and late event has an immutable ref plus exact campaign/creator scope and a single non-forked current head where applicable.
  - Every saved `live_post_ref` is opaque and qualified-resolver-backed. External actions require current exact authority and matching intent/receipt artifacts; a prior save, plan, gate, path, capability, or projection never grants authority. Raw post locators and reusable blanket approvals never enter the artifact set or projection.
  - A tracked live post has a receipt per required checkpoint, and each checkpoint's latest explicitly unsuperseded receipt controls the close gate; a mismatch, unknown disclosure, or changed/removed post is evidence for review, never silently treated as approved.
  - A closed creator row points to its unique current close-receipt head. A closed campaign points to the unique current campaign-close head, proves exact equality with the locked non-empty creator scope, and passes the strict gates in template §10; neither `closed` value is treated as a synonym for success.
  - A material late event is appended without rewriting prior receipts. A reference correction appends fresh close receipts when corrected gates still pass; a failed gate cannot receive a passing receipt, and manual reopen is reserved for new campaign-owned work under template §10's stage/action baseline.
  - A plan-authoring result names brief generation and open approvals. A tracker-only result instead names the evidence/action owner implied by the current stage, or stops as chain-complete when nothing remains; it never routes backward to brief generation by default.
- **Primary next skill**: in `plan-only`/`both`, [brief-generator](../brief-generator/SKILL.md); in `tracker-only`, use the stage-specific handoff in **Next Best Skill** or stop when complete.

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../../references/skill-contract.md).

## Data Sources

This family is Tier 1: every skill works with no live integrations. Supplied brand, audience, budget, and timeline support a plan skeleton, but do not determine messaging, platform/tier mix, content format, promo mechanics, contingency, rate, or KPI targets. Those choices require user direction or compatible source-dated planning evidence; otherwise retain `NEEDS_INPUT`.

Optional connectors that strengthen the plan when available:

- `~~influencer database` — size the influencer mix and validate tier follower ranges.
- `~~social platform analytics` — set platform-specific reach and engagement benchmarks.
- `~~CRM` — align conversion targets and attribution with existing pipeline data.
- `~~analytics` — pull past-campaign actuals for realistic KPI and budget-efficiency targets.

See [CONNECTORS.md](../../../CONNECTORS.md) for the free/keyless data recipe per category. Without a connector, ask the user for the missing inputs and proceed only with fields supported by user-provided evidence; return a useful skeleton plus `NEEDS_INPUT` for the rest.

## Instructions

Choose and state one mode before doing work. `plan-only` runs §§1–9 and does not instantiate §10. `tracker-only` runs only §10 and requires an existing `campaign_id`, exact versioned `plan_ref` plus plan hash, the current locked §8 measurement contract, and its locked non-empty creator scope; if any binding is missing, mismatched, forked, or unverified, return `NEEDS_INPUT` instead of rebuilding a plan or creating a placeholder tracker. `both` runs §§1–9 before §10. If creator selection is not yet locked, return the plan plus the exact missing scope/contract inputs and, only when explicitly requested, an inline non-close-eligible partial tracker header; do not invent creator identities or call it execution-ready. In `plan-only` or `both`, reuse an explicit upstream/user `campaign_id`; for a new campaign with none, generate random `campaign-<UUIDv4>` once and preserve it unchanged. In `tracker-only`, a missing ID is blocking; never generate or deterministically derive it from a campaign name, date, creator handle, or mutable plan content.

For plan-authoring modes, work the nine steps in order. Each has a fill-in template in [references/templates.md](references/templates.md) — copy the matching block and assemble it in step 9. Replace brackets only with supplied or source-backed values; never invent a number, identity, benchmark, or fact to eliminate a placeholder. Keep an unresolved optional field `Unknown`, and return `NEEDS_INPUT` when a required field is absent.

1. **Gather campaign requirements** — capture `campaign_id`, brand, value prop, audience, campaign type, timeline, budget, and constraints (template §1).
2. **Define objectives** — one SMART primary objective plus secondary objectives, with explicit success and failure definitions (template §2).
3. **Develop strategy** — big idea, strategy statement, audience, key messages, campaign pillars, platform split, and differentiation only from user-approved canon or compatible source-dated evidence; otherwise preserve the decision fields as `NEEDS_INPUT` rather than defaulting to UGC, promo-code, or another tactic (template §3).
4. **Define influencer criteria** — tier mix, must-have and preferred selection criteria, exclusions, ideal profile, and relationship types. Use only a user-declared or compatible source-dated follower taxonomy; [references/influencer-tiers.md](references/influencer-tiers.md) supplies the recording contract, not universal ranges or performance claims (template §4).
5. **Plan content requirements** — deliverables by platform/format, required elements, creative direction, themes, and the approval chain from supplied decisions and current platform/rights evidence; do not invent a default UGC format, promo mechanic, or content mix (template §5).
6. **Create the timeline** — key dates, a four-phase week-by-week plan, and a Gantt view (template §6).
7. **Allocate budget** — break down the supplied total by category, declared follower band, and platform only from user-approved rules or compatible source-dated cost evidence. Add contingency, CPM/CPE, or cost-per-content targets only when their rule/anchor is supplied; otherwise use `NEEDS_INPUT` and do not invent a percentage or rate (template §7).
8. **Establish success metrics** — primary KPIs vs source-dated comparators, secondary and conversion metrics, reporting cadence, and a non-canonical pre-execution measurement contract covering the baseline, outcome unit, readback window, attribution basis, decision rule, decision owner, exact campaign/plan version/hash, lock authorization, non-empty creator scope, and structured unique per-creator/deliverable publication checkpoints (template §8). Every external comparator requires an opaque source ref, observation date, and comparable window/cohort; otherwise keep it `Unknown`/`NEEDS_INPUT` rather than presenting an “industry average.” A scope or contract change is a new immutable version plus explicit §10 migration; never edit the locked block in place.
9. **Compile the plan document** — executive summary, the full sections above, and an appendix with risk mitigation (template §9). Return it inline by default; save only after authorization for the exact WARM path.

For `tracker-only` or `both`, read [references/templates.md §10](references/templates.md#10-optional-lightweight-campaign-tracker) for the Influencer domain fields and compatibility view. On Governed hosts, validate the source control artifacts first and generate the tracker as a read-only projection; never accept a tracker edit as an append, migration, stage/evidence/pointer change, reopen, or close. Creator rows must equal the locked scope and keep the active block at exactly eight fields; identity and close pointers stay adjacent. Identity and state heads must be resolvable, same-scope, unique, and non-forked. Any scope/contract/identity/checkpoint/verification/receipt/close/late-event gap shows `PARTIAL CHECKPOINT COVERAGE — NOT CLOSE-ELIGIBLE`; elapsed time never advances state. On semantic-only hosts, return the same view inline or save a `NOT_VERIFIED` compatibility snapshot after exact path-scoped authorization. `payment_status` records external readiness/evidence only and never sends money.

Each publication checkpoint gets an immutable, same-campaign/creator/checkpoint domain `publication_receipt` under fresh host authorization for the `append-publication-receipt` view update and a single-head supersession chain. This YAML block maps to shared `evidence-observation`; it is not an `action-receipt` and does not prove that this skill published anything. A real publish needs a separate exact `action-intent` before the executor and matching `action-receipt` after it. `live_post_ref` is only a qualified-resolver-backed opaque ref; raw URLs/slugs/provider IDs stay transient, and unresolved input remains `unknown`. `verified` disclosure/version match requires the exact observation, frozen approved asset/auditor, and evidence refs. Missing, mismatched, cross-scope, or forked evidence blocks close and routes the asset to [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md); never infer approval or mutation.

A creator closes only when each applicable checkpoint has one controlling verified publication receipt or evidence-backed terminal non-applicability resolution and every §10 gate passes. A fresh atomic `close-creator` authorization must name its receipt append, row/evidence changes, and pointer update; campaign close needs a separate equivalently scoped `close-campaign` authorization and an exact creator→current-close mapping. Any fork blocks both branches. Corrections preserve history, re-evaluate gates, and append newly authorized close heads only when warranted; a reference-only correction does not manually reopen work.

Late rights/post/attribution/payment/data evidence uses the campaign-bound §10 `late_event_note` under a fresh `append-late-event` authorization. Any accompanying stage/action/evidence/pointer mutation must be named in that atomic authorization or separately approved. `supersede-artifact` binds the exact old and replacement refs of the same scope and meaning. `manual-reopen` is only for new campaign-owned work; otherwise append the correction and, if gates pass, fresh close heads. Preserve history and never auto-reopen or invent a `reopened` stage.

When the user asks what needs attention, generate the template §10 exception queue from the validated source artifacts (or a clearly labeled semantic-only compatibility snapshot) using an explicit `as_of` time and user-selected rights horizon. It is a read-only projection—no cron, polling, automatic stage change, projection write-back, or external mutation.

## Example

**User**: "Create a campaign plan for a new sustainable sneaker launch targeting Gen Z on TikTok and Instagram with a $50K budget"

**Output**: A plan skeleton preserving the supplied audience, platforms, and $50K total. Sustainability claims/message canon, creator mix, content format, promo/attribution mechanic, rates, contingency, KPI targets, and exact dates remain `NEEDS_INPUT` until the user supplies them or compatible source-dated anchors. No micro-heavy, UGC, promo-code, or percentage default is inferred. (Fuller walkthrough in [references/templates.md](references/templates.md#worked-example).)

## Reference Materials

- [references/templates.md](references/templates.md) — fill-in templates for all nine planning steps, the optional lightweight WARM tracker, the worked example, and success tips.
- [references/influencer-tiers.md](references/influencer-tiers.md) — declaration contract for user/source-dated partner models and follower bands; it supplies no universal range or performance claim.
- [skill-contract.md](../../../references/skill-contract.md) — shared contract and handoff schema.
- [state-model.md](../../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../../CONNECTORS.md) — free/keyless data recipes per connector category.
- [audience-mapper](../../scout/audience-mapper/SKILL.md) — define the target audience this plan serves.
- [brief-generator](../brief-generator/SKILL.md) — turn the plan into per-influencer briefs.
- [budget-optimizer](../budget-optimizer/SKILL.md) — refine the budget allocation.
- [influencer-discovery](../../scout/influencer-discovery/SKILL.md) — find influencers matching the criteria.

## Next Best Skill

- **Plan-authoring primary**: [brief-generator](../brief-generator/SKILL.md) — convert an approved plan into concrete influencer briefs.
- **Plan-authoring alternates**: [budget-optimizer](../budget-optimizer/SKILL.md) to pressure-test the split; [influencer-discovery](../../scout/influencer-discovery/SKILL.md) to build or complete the locked creator scope.
- **Tracker-only, publication/approval blocker**: [creator-content-auditor](../../activate/creator-content-auditor/SKILL.md) — verify the cited live post against the frozen approved asset; this does not authorize an edit or amplification.
- **Tracker-only, readback/reconciliation due**: [performance-analyzer](../../report/performance-analyzer/SKILL.md) — produce the dated §8 readback artifact; final reporting may package that artifact only after the evidence exists.
- **Tracker-only, open operational item**: hand off only to the named owner/skill required by the current `next_action`; do not route back to briefing for a late-stage row. If every close gate passes and no action remains, stop and report chain-complete.

Termination note: keep a visited-set of skills invoked this session. If the applicable next skill has already run this session, stop and report the chain complete rather than re-invoking. Do not chain deeper than 3 hops from the originating request.
