# Skill Contract

This repository uses one contract across all 69 skills — 16 SEO/GEO, 16 influencer, 16 paid, 16 email, and 5 protocol. The contract keeps each skill specialized while making the full library feel like one operating system. The SEO/GEO skills score on [CORE-EEAT](core-eeat-benchmark.md) and [CITE](cite-domain-rating.md); the influencer skills on [C³](c3-benchmark.md); the paid-ads skills on [ROAS](roas-benchmark.md); the email skills on [SEND](send-benchmark.md).

## Skill Authoring Discipline

Four principles every skill must satisfy (high-signal LLM-coding guidance, adapted for skills):

1. **Focus & simplicity.** Every section traces to the user's task; cut speculative options and single-use abstraction. *Test: would a senior engineer call this skill overcomplicated?*
2. **Verifiable success criteria.** Define what "done" looks like and a checkable output, not a vague imperative. *Test: could someone confirm the skill succeeded without re-reading the request?*
3. **Surface assumptions; never fabricate.** State assumptions and proceed labeled (or ask on genuine ambiguity); label every metric **Measured / User-provided / Estimated** and never present an estimate as measured. *Test: can a reader tell which numbers are real?*
4. **Surgical handoff.** Recommend exactly one primary next move and let the global termination rules end the chain. *Test: does the handoff point somewhere, then stop?*

These are operationalized below in Description Standard, the Skill Contract `Done when` line, Decision Gates, and the Termination rules. Execution skills should **restate** the load-bearing rule in-body so it loads at activation, not only link it.

## Required Top Sections

Every `SKILL.md` must expose these compact operating sections:

- `Quick Start`
- `Skill Contract`
- `Handoff Summary` (regular skills use a `### Handoff Summary` subsection; auditor-class skills point theirs at the [auditor-runbook.md §1](auditor-runbook.md) schema, which they `Read` at activation)
- `Data Sources`
- `Instructions`
- `Reference Materials`
- `Next Best Skill`

Auditor-class skills must additionally expose:

- `When This Must Trigger`
- `Validation Checkpoints`
- A runbook activation step that `Read`s [auditor-runbook.md](auditor-runbook.md) (the framework-agnostic SSOT: §1 handoff schema, §2 cap method, §4 Artifact Gate, §5 translation), keeping only the framework-specific §2 worked examples, §3 guardrails, and §5 veto-ID rows inline

Optional sections such as `What This Skill Does`, `Example`, `Tips for Success`, `Save Results`, and non-auditor `Validation Checkpoints` may be present when they materially improve execution quality. They are not required for the compact skill skeleton.

## Frontmatter Fields Reference

| Field | Format | Required | Effect |
|-------|--------|----------|--------|
| `name` | kebab-case | Yes | Skill identifier, must match directory |
| `description` | String ≤1024 chars | Yes | UI display + vector search discovery |
| `version` | Semver | Yes | Skill version tracking |
| `metadata.discipline` | `seo-geo` / `influencer` / `paid` / `protocol` | Recommended | Uniform discipline tag on every skill — enables clustering / routing / discovery |
| `metadata.phase` | phase slug | Recommended | Lifecycle phase within the discipline (see [CLAUDE.md § Skills by Phase](../CLAUDE.md) meta-lifecycle table) |
| `when_to_use` | String (underscores) | Recommended | Detailed trigger scenarios for auto-invocation |
| `argument-hint` | String | Recommended | Shows argument format in command picker |
| `allowed-tools` | String or array | Optional | Pre-approved tools (e.g., `WebFetch`) |
| `license` | SPDX string | Optional | Default: Apache-2.0 |
| `compatibility` | String | Optional | Platform compatibility statement |
| `homepage` | URL | Optional | Skill homepage |
| `class` | `auditor` | Optional (required for auditor-class) | Marks the skill as an auditor-class gate that `Read`s [auditor-runbook.md](auditor-runbook.md) at activation. |

Note: `when_to_use` uses underscores (not hyphens). This matches Claude Code's internal parser. Place `allowed-tools` after `argument-hint` and before `metadata` for consistency.

## Description Standard

`description` is the primary activation surface (vector-search discovery). Write it as:

> Use when the user asks to "&lt;trigger&gt;"; &lt;2-4 concrete outcomes&gt;. Not for &lt;adjacent intent&gt; — use &lt;sibling-skill&gt;.

- Lead with the quoted user phrasing, name concrete outputs, and end with **one scope-boundary clause** routing adjacent intent to the right sibling skill. That boundary is what stops two skills competing for the same request.
- `metadata.triggers`: keep ≤ ~10 canonical phrases that are NOT already in the description and are uniquely owned by this skill — do not mirror the description or the tags block. Collapse multilingual phrasing to the 1-2 highest-value non-English entries; the rest belong in `tags`.
- Keep `description` and `when_to_use` scope-consistent — neither broader than the other.

## Section Meanings

### When This Must Trigger

This section answers:

- what intent should activate the skill
- when the skill is a strong recommendation
- when it becomes the required first move

Prefer:

- direct user phrasing
- short operational bullets
- high-frequency business scenarios

### Quick Start

This section should get a user moving in under 30 seconds.

Include:

- one shortest valid invocation
- one common scenario
- one short output expectation

### Skill Contract

This section defines operational behavior:

- **Reads**: user-provided inputs and tool data specific to this skill. (All skills implicitly read prior project state from `CLAUDE.md` and the State Model when available — do not repeat that global read in each skill's Reads line.)
- **Writes**: the main user-facing deliverable plus a reusable handoff summary
- **Promotes**: stable facts, blockers, and decisions worth storing for future work
- **Done when**: 2-3 checkable conditions confirming the deliverable is complete (the skill's verifiable success criteria)
- **Primary next skill**: the most natural follow-up skill in the library

### Termination rules for Next Best Skill chains

Skill handoff chains MUST not recurse indefinitely. **Global default termination rule applies to every Next Best Skill block**:

1. **Visited-set check**: if the Next Best target was already invoked in this session's chain, STOP and report chain-complete.
2. **Depth limit**: default `max-depth: 3` unless a stricter block-level limit is stated.
3. **Ambiguity stop**: when routing is ambiguous, stop and report the recommended options instead of auto-following.

Individual `Next Best Skill` blocks may add verdict-conditional branching, explicit terminal outcomes, or a stricter `max-depth`, but they inherit the global visited-set and depth rules even when those rules are not repeated locally.

## Handoff Summary Format

Every skill should be able to produce a concise handoff summary using this shape:

```markdown
### Handoff Summary

- **Status**: DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT
- **Objective**: what was analyzed, created, or fixed
- **Key Findings / Output**: the highest-signal result
- **Evidence**: URLs, data points, or sections reviewed (label each Measured / User-provided / Estimated)
- **Assumptions**: any inferences made to proceed, or "none"
- **Open Loops**: blockers, missing inputs, or unresolved risks
- **Recommended Next Skill**: one primary next move
```

### Auditor-class Extension (v7.1.0)

Auditor-class skills (whose deliverable is a scored audit with a verdict — the five gates `content-quality-auditor` (CORE-EEAT), `domain-authority-auditor` (CITE), `content-reviewer` (C³ ART), `ad-account-auditor` (ROAS), and `email-quality-auditor` (SEND)) extend this format with 3 additional fields:

- `cap_applied` — boolean; set by Critical Fail Cap rule
- `raw_overall_score` — number; score before cap
- `final_overall_score` — number; score after cap

These fields are authoritative in [references/auditor-runbook.md §1](auditor-runbook.md). Non-auditor skills do not emit them.

New auditor-class outputs MUST include the three auditor-extension fields; the Artifact Gate treats missing `cap_applied`, `raw_overall_score`, or `final_overall_score` (unless `status: BLOCKED`) as a validation failure.

## Decision Gates

When a skill can hit a genuine ambiguity or missing-input fork, give it a compact two-column gate so it neither guesses nor over-asks:

- **Stop and ask** — only for blocking ambiguities; present numbered options with their outcomes (e.g., no target provided and none inferable from context).
- **Continue silently** — list the non-blocking cases the skill must NOT stop for (e.g., which 3 of 5 competitors to deep-dive; missing optional tool data → mark N/A and proceed).

Keep it to the 1-2 real forks per skill. The two SEO/GEO auditors' `## Decision Gates` sections are the reference implementation.

## Promotion Rules

Promote only durable information:

- current strategic priorities
- approved decisions
- stable brand/entity facts
- critical blockers
- recurring terminology
- high-signal audit findings

Do not promote:

- transient tool logs
- low-signal observations
- large raw datasets
- speculative claims without evidence

### Provenance requirement for memory/decisions.md (v8.0.1+)

Every entry MUST include an `approved_by:` field with one of three values:

- `user` — explicit confirmation this session
- `skill_inferred` — promotable pending review
- `migrated` — from prior sessions

Auditor-class gates (`content-quality-auditor`, `domain-authority-auditor`, `content-reviewer`, `ad-account-auditor`, `email-quality-auditor`) MUST ignore decisions with `approved_by != user` when deciding verdict. Non-auditor skills propose via `open-loops.md` status `pending-decision` instead of directly writing to `decisions.md`. This prevents prompt-injection attacks that inject fake "approved decisions" via pasted content.

## Category Defaults

### Research

- Reads: topics, competitors, search behavior, user goals
- Writes: opportunity summaries and strategic findings
- Promotes: priorities, terminology, competitor facts, and candidate entity signals

### Build

- Reads: briefs, target keywords, page intent, entity inputs
- Writes: drafts, metadata, markup, optimization outputs
- Promotes: chosen messaging, approved structure, publish blockers

### Optimize

- Reads: existing assets, audits, issues, performance symptoms
- Writes: repair plans and scored findings
- Promotes: blockers, recurring defects, remediation priorities

### Monitor

- Reads: previous baselines, new performance data, thresholds
- Writes: deltas, trend summaries, alerts, reports
- Promotes: major changes, confirmed anomalies, follow-up actions

### Protocol layer

The 5 shared-machinery skills under `protocol/` (4 truth registries + memory). The auditor-class **gate role** is separate: its 5 skills (`content-quality-auditor`, `domain-authority-auditor`, `content-reviewer`, `ad-account-auditor`, `email-quality-auditor`) live in and are counted under their home disciplines (SEO/GEO, influencer, paid, email) — not here — and `Read` [auditor-runbook.md](auditor-runbook.md) at activation, keeping only framework-specific content inline.

- Reads: outputs from every other category
- Writes: truth records and memory structure
- Promotes: the canonical state other skills should trust

### Influencer categories (IMPACT discipline)

The 16 influencer skills span four phases (discover / plan / activate / measure) and score on the [C³ framework](c3-benchmark.md) (Creator/Content/Campaign on ACE/ART/ROI). They write to `memory/influencer/<skill>/`.

- **Discover** (audience-mapper, trend-spotter, influencer-discovery, fit-scorer) — Reads: audience signals, niche, trends, brand/campaign context, creator shortlists. Writes: audience profiles, niche dossiers, trend reports, shortlists, fit scores. Promotes: target-audience facts, niche positioning, durable trends, vetted creators, fit verdicts.
- **Plan** (competitor-tracker, campaign-planner, brief-generator, budget-optimizer) — Reads: competitor partnerships, goals, KPIs, budget, creator set. Writes: competitor partner maps, campaign plans, briefs, budget allocations. Promotes: competitor benchmarks, approved plan, budget envelope, key messages.
- **Activate** (outreach-manager, content-reviewer, contract-helper, content-amplifier) — Reads: shortlists, briefs, content submissions, deal terms, published/UGC assets. Writes: outreach threads, review decisions, contract drafts, amplification and repurposing plans. Promotes: confirmed partnerships, approved content, signed terms, winning creatives and blockers.
- **Measure** (landing-optimizer, performance-analyzer, roi-calculator, report-generator) — Reads: landing pages, campaign metrics, costs, baselines. Writes: landing-page optimizations, performance analyses, ROI/CVI calculations, reports. Promotes: conversion blockers, confirmed results, ROI verdicts, follow-up actions.

## Protocol Layer vs Execution Layer

The auditor-class gates are discipline-resident Execution-layer skills with extra powers, so they get their own column:

| Behavior | Execution Layer (59 skills) | Auditor-class gates (5 skills, discipline-resident) | Protocol Layer (5 skills) |
|----------|---------------------------|-----------------------------------------------------|--------------------------|
| Triggering | User invocation or intent match | User + hook auto-trigger + other skill recommendation | User invocation + other skill recommendation |
| Output format | Report or asset + handoff summary | Gate verdict + auditor-class handoff (cap schema) | Truth records / memory structure + handoff summary |
| Write scope | Own category WARM path only | Own audit sink under `memory/audits/` + one veto marker to HOT without asking | Own registry path (`memory/entities/`, `memory/creators/`, `memory/claims/`); `memory-management` additionally writes HOT + manages archives + cross-category aggregation |
| Cross-reference | Via Next Best Skill | Mandatory gate check in handoff summaries | Via Next Best Skill |

## Gate Verdicts

The five auditor-class gates must produce a clear verdict, not just scores:

- `content-quality-auditor` (optimize/): **SHIP** (no veto items, scores above threshold) / **FIX** (issues found, none are veto) / **BLOCK** (veto item T04, C01, or R10 failed)
- `domain-authority-auditor` (monitor/): **TRUSTED** (no veto items, scores above threshold) / **CAUTIOUS** (issues found, none are veto) / **UNTRUSTED** (veto item T03, T05, or T09 failed)
- `content-reviewer` (activate/): **APPROVED** / **APPROVED WITH MINOR CHANGES** / **REVISIONS REQUIRED** / **REJECTED** (ART veto T1 or T2 forces REJECTED; maps to status via APPROVED→DONE, MINOR→DONE_WITH_CONCERNS, REVISIONS→NEEDS_INPUT, REJECTED→BLOCKED)
- `ad-account-auditor` (paid/activate/): **SHIP** (no veto, RQS in a healthy band) / **FIX** (issues found, no veto, or a single-veto capped score) / **BLOCK** (2+ vetoes among R1/R2/O1/O2/A1 — `status: BLOCKED`)
- `email-quality-auditor` (email/deliver/): **SHIP** (no veto, EQS in a healthy band) / **FIX** (issues found, no veto, or a single-veto capped score) / **BLOCK** (2+ vetoes among S1/S2/N1/D1 — `status: BLOCKED`)

## Completion Status

Completion Status describes whether a skill finished executing. Gate Verdicts describe auditor-gate evaluation conclusions. A content-quality-auditor that successfully produces a BLOCK verdict has Completion Status = DONE (it completed its job). The two are orthogonal: Status tracks execution health; Verdicts track findings.

Every skill must declare one of these states when it finishes:

- **DONE** — all steps completed, deliverables provided with data sources cited
- **DONE_WITH_CONCERNS** — completed but with data gaps or caveats; list each concern
- **BLOCKED** — cannot proceed; state reason, what was tried, and recommendation
- **NEEDS_INPUT** — missing required information; state exactly what is needed

Include the status as the first field of the Handoff Summary (see format above).

## Escalation Protocol

Three triggers require a skill to stop and report instead of continuing:

1. **3 failed attempts** at any step — STOP, declare BLOCKED, state what was tried
2. **Data confidence below useful threshold** — declare DONE_WITH_CONCERNS, list which metrics are estimated vs verified, name the data source for each
3. **Scope exceeds verifiable range** — STOP, declare what can vs cannot be assessed (e.g., medical accuracy claims, legal compliance)

Report format:

- **Status**: BLOCKED / DONE_WITH_CONCERNS / NEEDS_INPUT
- **Reason**: one-sentence explanation
- **Attempted**: what was tried and why it failed
- **Recommendation**: what the user should do next

## Output Voice

When producing deliverables (reports, content, audits), follow these rules:

**Banned vocabulary** — never use in output: crucial, robust, leverage, delve, nuanced, multifaceted, furthermore, moreover, additionally, pivotal, landscape (metaphorical), tapestry, foster, showcase, intricate, vibrant, cutting-edge, game-changer, unlock, harness, elevate, empower, streamline, synergy, holistic, seamless, seamlessly, realm, paramount, myriad.

**Conditional restrictions:**

- "comprehensive" — do not use as filler. OK only when the deliverable covers every item in a defined checklist (e.g., "comprehensive 80-item audit"). Prefer "complete" or "full" otherwise.
- "navigate" — banned in metaphorical use ("navigate the landscape"); fine in literal use ("help users navigate the site").

**Banned phrases:** "In today's digital landscape", "It is important to note", "It's worth noting that", "Let's dive in", "Without further ado", "At the end of the day", "When it comes to [topic]", "In the world of [topic]".

**Style rules:**

1. Lead with the finding, not the preamble
2. Use specific numbers — "KD 34, vol 2,400/mo" not "moderate difficulty"
3. Short paragraphs — 4 sentences max; use bullets for lists
4. Name the data source — "Per Ahrefs data" or "User-provided estimate", not "according to available data"

| ❌ Avoid | ✅ Prefer |
|---------|----------|
| "This keyword has good potential" | "Vol 4,800, KD 28, transactional intent — realistic target for DA 35 sites" |
| "Consider creating content around this topic" | "Write '[A] vs [B] for small teams' — 1,200/mo searches, current #1 is a 2022 article with 12 backlinks" |

## Save Results Template

Every skill must include this flow at the end of its execution:

After delivering findings to the user, ask:

> "Save these results for future sessions?"

If yes, write a dated summary to the appropriate WARM path using filename `YYYY-MM-DD-<topic>.md` containing:

- One-line verdict or headline finding
- Top 3-5 actionable items
- Open loops or blockers
- Source data references

Only the five auditor-class gates (`content-quality-auditor`, `domain-authority-auditor`, `content-reviewer`, `ad-account-auditor`, `email-quality-auditor`) may append one veto marker to `memory/hot-cache.md` without asking when a veto-level issue is found. Other skills must ask before writing memory and should hand off veto-like risks to the relevant auditor gate instead.

## Response Presentation Norms

When answering cross-skill queries or presenting information drawn from project memory, follow these norms in addition to the Output Voice rules above:

1. **Conclusion first** — lead with the finding or recommendation, not the file path or methodology
2. **Natural language** — say "your homepage has 2 issues to fix" not "CORE-EEAT T04 and C01 veto items failed"
3. **Collapsible technical detail** — place file paths, raw scores, and veto IDs in a details block so light users can skip them
4. **End with next step** — every cross-skill answer should conclude with a suggested action
5. **No internal jargon in user-facing output** — do not surface terms like "WARM tier" or "frontmatter" to end users; use "your project records" or "previous analysis" instead

These norms apply to all skills when their output incorporates data from multiple memory files.

## Write Paths by Category

| Category | Write Path | Content |
|----------|-----------|---------|
| Research (4 skills) | `memory/research/<skill>/` | keyword opportunities, competitor findings, SERP notes, content gaps |
| Build (4 skills) | `memory/content/` | content briefs, meta tag decisions, schema annotations, publish status |
| Optimize (4 skills) | `memory/audits/<skill>/` † | per-skill audit summaries, veto items, fix priorities |
| Monitor (4 skills) | `memory/monitoring/` † | rank deltas, alert history, backlink changes |
| Protocol layer (5 skills) | per-role paths | see protocol-layer definitions (incl. `consent-registry` → `memory/consent/`) |
| Influencer / IMPACT (16 skills) | `memory/influencer/<skill>/` (working state) + `memory/audits/influencer/` (content-reviewer's gated C³ ART verdicts) | audience profiles, creator fit scores, campaign plans, briefs, outreach, content reviews, ROI/CVI calculations, reports |
| Paid Ads / ROAS (16 skills) | `memory/paid-ads/<skill>/` (working state) + `memory/audits/paid/` (ad-account-auditor's gated RQS verdicts) | account/campaign structures, audience segments, ad-creative scores, experiment designs, account-audit gates, conversion-signal QA, measurement-loop results, attribution reconciliations |
| Email / SEND (16 skills) | `memory/email/<skill>/` (working state) + `memory/audits/email/` (email-quality-auditor's gated EQS verdicts); consent/suppression facts in `memory/consent/` (consent-registry SSOT) | deliverability pre-flights, list-growth plans, segment maps + suppression, email creative, lifecycle-flow designs, newsletter monetization models, send-test designs, EQS gate verdicts |
| **Auditor gate aggregate (v7.1.0+)** | `memory/audits/YYYY-MM.md` | **owned by `memory-management`**; monthly archive of auditor-class gate handoffs in the structured format defined in [memory-management SKILL.md §Writes](../protocol/memory-management/SKILL.md); consumed by the Runbook §5 cross-version rule |

† **Auditor-gate exceptions**: `content-quality-auditor` (Optimize) writes its gated artifacts to `memory/audits/content/`, and `domain-authority-auditor` (Monitor) writes to `memory/audits/domain/` — the per-role audit sinks the Artifact Gate validates, not the category default. (The other three gates' sinks — `content-reviewer` → `memory/audits/influencer/`, `ad-account-auditor` → `memory/audits/paid/`, `email-quality-auditor` → `memory/audits/email/` — are already named in their discipline rows.)

**Note on `memory/audits/`**: three conventions coexist. The `<skill>/` subdirectory pattern (non-gate Optimize skills, per-skill files) is for skill-specific audit artifacts (e.g., `memory/audits/technical-seo-checker/2026-04-11-example.md`). The per-role gate sinks (`content/`, `domain/`, `influencer/`, `paid/`, `email/`) hold the five auditor-class gates' `class: auditor-output` artifacts. The flat `YYYY-MM.md` pattern (auditor gate aggregate, monthly) is the gate handoff archive. They are siblings, not a conflict.
