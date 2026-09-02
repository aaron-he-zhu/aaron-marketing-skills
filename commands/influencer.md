---
description: "Run an influencer-marketing (STAR) workflow: audience & creator scouting, campaign targeting, briefs, outreach, amplification, and ROI reporting. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-brand> [--phase scout|target|activate|report]"
---

# Influencer Command

Run the influencer-marketing lifecycle along the **STAR loop** (Scout → Target → Activate → Report): understand the audience, find and score creators, plan and brief the campaign, run outreach and amplify, then track ROI. Skills score on the [STAR framework](../references/star-benchmark.md) (Suitability / Trust / Appeal / Return → SQS) and operate from the user's **own data and project memory** — keyed creator-analytics suites are never required; connectors only automate retrieval.

## Route

Infer the phase from the goal (or honor `--phase`) and route to the matching skill:

- **Scout** — audience-mapper (audience/niche modes), trend-spotter, influencer-discovery, fit-scorer (STAR Suitability); creator-registry dedupes candidates against the roster
- **Target** — competitor-tracker, campaign-planner, brief-generator, budget-optimizer
- **Activate** — outreach-manager, creator-content-auditor (STAR gate), contract-helper, content-amplifier (paid whitelisting / UGC repurpose modes) — resolve the carried opaque `creator_ref` through an authorized artifact or verified registry link, then consult the creator-registry projection (`memory/creators/<aggregate-id>.md`: contact path, last agreed rate, exclusivity, compliance history) before outreach or contracting; never derive the path from a raw handle
- **Report** — landing-optimizer (post-click), performance-analyzer, roi-calculator (STAR Return), report-generator

## Rules

- Start where the goal sits in the funnel; do not force the full four-phase chain when the user only needs one stage.
- `creator-content-auditor` is the pre-publish gate: any creator content goes through its STAR **Trust** check (FTC disclosure STAR-T1, claim integrity STAR-T2) before it ships.
- For `sponsored_content_gate`, require disclosure status, claim evidence, and the governing brief. If any applicable evidence is unobserved, keep it Unknown and return `NEEDS_INPUT/UNDECIDED/NOT_SCORED`; missing evidence is not a veto. One independently verified veto maps to `DONE_WITH_CONCERNS/FIX` (Revisions Required); two or more map to `DONE/BLOCK` (Reject/Hold). A business `BLOCK` never becomes execution `status: BLOCKED`.
- Return the audit inline by default. Only with explicit exact-write permission, a validator-clean v3 artifact, and a supported runtime writer may `class: auditor-output` be persisted to `memory/audits/influencer/`; otherwise identify that intended sink and ask for authorization.
- `memory/events/creators.ndjson` is the roster history. Other skills submit authorized `operation: propose` events; `creator-registry` alone accepts/rejects or mutates canonical creator state. Run it when proposals are pending or a campaign cycle closes; `memory/creators/` contains generated views.
- Score creators/content/campaigns on STAR (Suitability/Trust/Appeal/Return → SQS); label every metric Measured / User-provided / Estimated; never fabricate reach or rates.
- Tier 1 by default — works from user-provided data; connectors only automate retrieval. Compliance checks are guidance, not legal advice.
- Follow each skill's Next Best Skill handoff; stop at the documented termination rules rather than auto-chaining the whole discipline.
- **Scope edge — creators vs adjacent lanes**: "launch a product with creators" starts at [campaign-planner](../influencer/target/campaign-planner/SKILL.md) while the launch itself runs on RAMP via [/aaron-marketing:launch](launch.md); "boost / repurpose this" is [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) with paid execution handed to [/aaron-marketing:ad](ad.md); the always-on social calendar belongs to ECHO ([social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md)); contract/rate/exclusivity *records* live in [creator-registry](../protocol/creator-registry/SKILL.md), and any email opt-in evidence in [consent-registry](../protocol/consent-registry/SKILL.md).
- **Paid creator whitelisting order**: after the partner is confirmed, run `contract-helper` first for exact paid usage/whitelisting rights, then `brief-generator` for the governing brief. Only after the agreement/brief and draft asset exist, run `creator-content-auditor` (STAR-T1 disclosure + STAR-T2 claim integrity), followed by `content-amplifier` in its paid-planning mode. Then hand paid execution to `/aaron-marketing:ad --phase activate`, where `ad-account-auditor` gates before spend. Stop for explicit spend approval; no contract, creator audit, or amplification plan authorizes activation by itself.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
