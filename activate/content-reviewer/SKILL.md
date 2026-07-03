---
name: content-reviewer
description: 'Use when the user asks to "review this influencer content" or "check if this post meets brand guidelines"; produces a structured review (brand alignment, message accuracy, compliance, quality, technical specs), an approve/revise/reject decision, and a constructive feedback message for the creator. Not for drafting the brief that sets the criteria — use brief-generator; not for the partnership agreement — use contract-helper.'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Activate when the user has an influencer content submission (draft post, video, image, caption) and needs a gate decision before it goes live. Triggers include reviewing content against a brief, checking FTC/disclosure compliance, scoring creative quality, building a review checklist, or writing revision feedback for a creator. Use after the brief exists and before the content is published or amplified."
argument-hint: "<content submission or link> [platform] [campaign]"
class: auditor
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: influencer
  phase: activate
  family: influencer-marketing
  impact-phase: Activate
---

# Content Reviewer

Systematically review influencer content submissions against brand guidelines, campaign objectives, and legal requirements, then issue a gate decision before the content goes live.

## When This Must Trigger

Run this before any influencer content goes live, even if the user doesn't use review terminology:

- User asks "can we post this", "is this submission okay", or "does this meet our guidelines"
- A creator delivers a draft (post, video, image, caption) against a brief from `brief-generator`
- User suspects a disclosure, claim-substantiation, or brand-safety problem in submitted content
- Before `content-amplifier` puts paid or owned reach behind a creator post
- Compliance re-check when FTC/platform disclosure rules or campaign claims change mid-flight

## Quick Start

Shortest invocation:

```
Review this influencer content submission: [content description/link]
```

Common scenario — gate a submission against a campaign brief:

```
Check if this TikTok post meets our brand guidelines for [campaign], then give me an approve/revise/reject decision and feedback I can send the creator
```

## Skill Contract

- **Reads**: the content submission (link, description, caption, media notes), the campaign brief and key messages, brand guidelines, disclosure/FTC requirements, platform technical specs, prior review artifacts in `memory/audits/influencer/`, and the [auditor-runbook](../../references/auditor-runbook.md) handoff/cap schema (content-reviewer is the C³ **ART gate consumer**).
- **Writes**: a gated review artifact at `memory/audits/influencer/YYYY-MM-DD-<topic>.md` with `class: auditor-output` and the auditor-runbook handoff schema (status / key_findings / evidence_summary / recommended_next_skill / cap_applied / raw_overall_score / final_overall_score), computed from C³ **ART** scoring — so the PostToolUse Artifact Gate validates the verdict — plus the human-facing feedback message.
- **Promotes**: durable facts (final approval status, recurring compliance gaps, creator-specific notes) to `memory/hot-cache.md`.
- **Done when**:
  1. Every must-pass category (brand alignment, message accuracy, compliance, technical specs) has an explicit pass/fail with evidence.
  2. A single decision is recorded — APPROVED, APPROVED WITH MINOR CHANGES, REVISIONS REQUIRED, or REJECTED.
  3. A constructive feedback message for the creator exists (when changes are needed).
  4. The gated artifact follows the auditor-runbook schema: `raw_overall_score` = the ART score; a **T1/T2 veto → `status: BLOCKED`** (Reject) with `cap_applied: false`, `raw_overall_score` retained, and no `final_overall_score`; a non-veto pass → `status: DONE`/`DONE_WITH_CONCERNS` with `final_overall_score`; a non-veto REVISIONS decision → `status: NEEDS_INPUT`, still **with** `final_overall_score` (`cap_applied: false`) — BLOCKED is the only branch that omits the final score. Map the decision to the status enum (APPROVED→DONE, MINOR→DONE_WITH_CONCERNS, REVISIONS→NEEDS_INPUT, REJECTED→BLOCKED).
- **Primary next skill**: [contract-helper](../../activate/contract-helper/SKILL.md)

### Handoff Summary

> Emit the standard shape from [skill-contract.md §Handoff Summary Format](../../references/skill-contract.md).

Specifically, emit the auditor-class handoff from [auditor-runbook.md §1](../../references/auditor-runbook.md): `status` (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT), `objective`, `target`, `key_findings`, `evidence_summary`, `recommended_next_skill`, plus the auditor fields `cap_applied`, `raw_overall_score` (the ART score, floor-rounded, before cap), and `final_overall_score` (omitted only when BLOCKED).

## Data Sources

This family needs no live integrations (Tier 1). The skill works end to end from inputs you provide: paste the content link or description, the brief, brand guidelines, and platform specs, and it produces the review.

Optional connectors can speed up evidence gathering where available:

- `~~social platform analytics` — pull native post specs, engagement signals, and platform disclosure flags (e.g. "Paid partnership" label).
- `~~influencer database` — load the creator's history, prior submissions, and past compliance flags.
- `~~CRM` — link the review back to the deal, campaign owner, and approval chain.
- `~~compliance reference` — current FTC / platform disclosure rules for the relevant market.

With no connector configured, ask the user for the missing inputs and proceed. See [CONNECTORS.md](../../CONNECTORS.md) for the keyless data recipes.

## Instructions

**Before scoring, `Read ../../references/auditor-runbook.md` and `../../references/c3/art-content-benchmark.md`.** The runbook is the framework-agnostic SSOT (§1 handoff schema, §2 cap method, §4 Artifact Gate, §5 veto-ID translation); the ART benchmark owns the Content dimensions and the T1/T2 veto definitions this gate enforces.

Run the review steps in order. Each step has a fill-in template in [references/review-templates.md](references/review-templates.md).

1. **Establish review criteria** — set campaign, creator, platform, content type, and the weighted category table (brand alignment, message accuracy, compliance must-pass; quality 80%+; technical must-pass). Template Step 1.
2. **Brand alignment review** — visual brand check, brand-safety check, value alignment; score X/10. Template Step 2.
3. **Message accuracy review** — key messages, talking points, prohibited claims, CTA; score X/10. Template Step 3.
4. **Compliance review** — disclosure, platform rules, legal/regulatory, required elements; score X/10 (no partial pass). This is the C³ **ART veto gate** — see below. Template Step 4.
5. **Quality assessment** — production, effectiveness, platform optimization, creative; score X/10. Template Step 5. Run the SOFT AI-slop / persona / per-platform aids in [references/quality-review-aids.md](references/quality-review-aids.md).
6. **Technical specifications check** — platform specs and caption requirements; pass/fail. Template Step 6.
7. **Generate final review** — submission details, score table, single decision, feedback pointer. Template Step 7.
8. **Create feedback message** — constructive, positives-first message for the creator when changes are needed. Template Step 8.

### C³ ART veto enforcement

Step 4's compliance gate is the C³ **Content** review ([ART](../../references/c3/art-content-benchmark.md)). Two ART items are veto-level — a failure forces the overall decision to **Reject** (never "revise"). Record the veto ID (T1/T2) in the gated artifact and handoff YAML only; the decision and creator feedback the user sees carry the plain-language translation per [auditor-runbook §5](../../references/auditor-runbook.md):

- **T1 · FTC Disclosure** (Disclosure Check + FTC compliance rows) — missing or inadequate disclosure on sponsored content → Reject. Regulatory basis: FTC 16 CFR §255 and the 2024 Trade Regulation Rule (16 CFR Part 465). Not legal advice.
- **T2 · Claim Integrity** (Claims substantiation) — false or unsubstantiated claims → Reject.

**ART veto-ID translation rows** (use alongside the runbook's shared rows — these are the C³ ART meanings, never CORE-EEAT/CITE/ROAS):

| Internal (artifact/handoff only) | User-facing |
|---|---|
| "T1 failed" | "Rejected — sponsored content is missing the required ad disclosure" |
| "T2 failed" | "Rejected — the content makes a claim that isn't substantiated" |

## Worked Example

**User**: "Review this TikTok video submission for our protein powder campaign"

A submission with strong visuals (Brand 9/10, Quality 9/10) but no visible #ad disclosure scores Compliance 5/10 and triggers the FTC-disclosure veto (T1 — recorded in the artifact/handoff only). The user-facing decision is **❌ REJECTED — missing the required ad disclosure**, not a revise: the creator must add #ad in caption and/or verbal disclosure in the first 3 seconds, then resubmit. Non-veto gaps (missing "20g protein" key message, missing promo code "FIONA20") are listed as required-on-resubmission, and the feedback message leads with what worked (authentic workout integration, engaging hook). Full output in [references/review-templates.md § Worked Example](references/review-templates.md#worked-example).

## Validation Checkpoints

### Input Validation
- [ ] Content submission identified (link, file, caption text, or description)
- [ ] Campaign brief and key messages available (else NEEDS_INPUT — the review has no criteria without them)
- [ ] Platform and content type confirmed (technical specs and disclosure norms differ per platform)
- [ ] Disclosure context known: paid, sponsored, gifted, or organic

### Output Validation
- [ ] Every must-pass category (brand alignment, message accuracy, compliance, technical specs) has an explicit pass/fail with evidence
- [ ] ART vetoes T1 (FTC disclosure) and T2 (claim integrity) checked; any veto forces REJECTED, never "revise"
- [ ] Exactly one decision recorded (APPROVED / APPROVED WITH MINOR CHANGES / REVISIONS REQUIRED / REJECTED) and mapped to the status enum
- [ ] `cap_applied`, `raw_overall_score`, `final_overall_score` set per the runbook (final omitted only when BLOCKED — NEEDS_INPUT still carries it)
- [ ] Decision and creator feedback use plain language; veto IDs and internal field names appear only in the gated artifact/handoff YAML

## Reference Materials

- [references/review-templates.md](references/review-templates.md) — fill-in templates for every step, the full worked example, the quick review checklist, and review tips.
- [references/quality-review-aids.md](references/quality-review-aids.md) — wires the AI-slop checklist ([humanizer-slop.md](../../references/humanizer-slop.md)) as a SOFT, non-veto ART quality penalty (ART vetoes stay T1/T2 only), the multi-persona method ([expert-panel.md](../../references/expert-panel.md)), and per-platform format/disclosure norms ([platforms/](../../references/platforms/)).
- [skill-contract.md](../../references/skill-contract.md) — shared contract and Handoff Summary format.
- [state-model.md](../../references/state-model.md) — memory tiers and save-path conventions.
- [CONNECTORS.md](../../CONNECTORS.md) — keyless data recipes for the `~~` connector placeholders.
- C³ scoring: [c3-benchmark.md](../../references/c3-benchmark.md) and [c3/art-content-benchmark.md](../../references/c3/art-content-benchmark.md) — the ART Content rubric this review gates on, incl. the T1 (FTC disclosure) and T2 (claim integrity) veto items.
- [offer-claims-registry](../../protocol/offer-claims-registry/SKILL.md) — the claim-substantiation record consulted for the T2 check.
- [creator-registry](../../protocol/creator-registry/SKILL.md) — the creator's disclosure/compliance history; log dated verdicts back to it.
- [brief-generator](../../plan/brief-generator/SKILL.md) — the brief whose criteria this review checks against.
- [contract-helper](../../activate/contract-helper/SKILL.md) — bake content guidelines and approval terms into the agreement.
- [content-amplifier](../../activate/content-amplifier/SKILL.md) — amplify content once approved.
- [performance-analyzer](../../measure/performance-analyzer/SKILL.md) — track how approved content performs.

## Next Best Skill

**Primary**: [contract-helper](../../activate/contract-helper/SKILL.md) — once content is approved (or once review feedback exposes a gap the agreement should cover), fold guidelines, usage rights, and approval terms into the partnership contract.

**Alternates** (same Activate family):
- [content-amplifier](../../activate/content-amplifier/SKILL.md) — when content is approved and ready to scale through paid or owned channels.
- [performance-analyzer](../../measure/performance-analyzer/SKILL.md) — when the piece is live and you want to measure outcomes.

Termination note (visited-set): if a recommended skill has already been invoked this session, stop and report the chain as complete rather than re-running it. Cap any handoff chain at max-depth 3.
