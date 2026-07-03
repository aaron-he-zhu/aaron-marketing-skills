---
name: domain-authority-auditor
description: 'Use when auditing domain authority, trust, or citation credibility; runs 40-item CITE scoring with veto checks (TRUSTED/CAUTIOUS/UNTRUSTED). Not for page-level content quality — use content-quality-auditor; not for backlink profiling alone — use offsite-signal-analyzer. 域名权威/网站可信度'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when auditing domain trust and authority. Runs CITE 40-item scoring with veto checks. Also when the user asks about domain credibility or citation trustworthiness."
argument-hint: "<domain>"
class: auditor
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: monitor
  geo-relevance: "medium"
---

# Domain Authority Auditor

> Based on [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating). Full benchmark reference: [references/cite-domain-rating.md](../../references/cite-domain-rating.md)
This skill evaluates domain authority across 40 standardized criteria organized in 4 dimensions. It produces a comprehensive audit report with per-item scoring, dimension and weighted scores by domain type, veto item checks, and a prioritized action plan.

**Sister skill**: [content-quality-auditor](../../optimize/content-quality-auditor/SKILL.md) evaluates content at the page level (80 items). This skill evaluates the domain behind the content (40 items). Together they provide a complete 120-item assessment.

> **Namespace note**: CITE uses C01-C10 for Citation items; CORE-EEAT uses C01-C10 for Contextual Clarity items. In combined 120-item assessments, prefix with the framework name (e.g., CITE-C01 vs CORE-C01) to avoid confusion.

## When This Must Trigger

Use this when domain credibility or citation trustworthiness is in question — even if the user doesn't use audit terminology:

- User asks "how trustworthy is my site" or "is my domain credible"
- When offsite-signal-analyzer finds toxic link ratio above 15%, its handoff summary recommends this gate check
- Evaluating domain authority before a GEO campaign
- Benchmarking your domain against competitors
- Assessing whether a domain is trustworthy as a citation source
- Running periodic domain health checks or after link building campaigns
- Identifying manipulation red flags (PBNs, link farms, penalty history)
- Cross-referencing with content-quality-auditor for full 120-item assessment

## What This Skill Does

1. **Full 40-Item Audit**: Scores every CITE check item as Pass/Partial/Fail
2. **Dimension Scoring**: Calculates scores for all 4 dimensions (0-100 each)
3. **Weighted Totals**: Applies domain-type-specific weights for CITE Score
4. **Critical Issue Detection**: Flags critical manipulation signals that cap the score
5. **Priority Ranking**: Identifies Top 5 improvements sorted by impact
6. **Action Plan**: Generates specific, actionable improvement steps
7. **Cross-Reference**: Optionally pairs with CORE-EEAT for combined diagnosis

## Quick Start

Start with one of these prompts. Finish with a citation-trust verdict and a handoff summary using the repository format in [Skill Contract](../../references/skill-contract.md).

### Audit Your Domain

```
Audit domain authority for [domain]
Run a CITE domain audit on [domain] as a [domain type]
```

### Audit with Domain Type

```
CITE audit for example.com as an e-commerce site
Score this SaaS domain against the 40-item benchmark: [domain]
```

### Comparative Audit

```
Compare domain authority: [your domain] vs [competitor 1] vs [competitor 2]
```

### Combined Assessment

```
Run full 120-item assessment on [domain]: CITE domain audit + CORE-EEAT content audit on [sample pages]
```

## Skill Contract

**Gate verdict**: **TRUSTED** (no critical issues, scores above threshold) / **CAUTIOUS** (issues found but none critical) / **UNTRUSTED** (a critical trust issue failed — see "Critical Issue to Fix" in the report). Always state the verdict prominently at the top of the report using plain language, not item IDs.

**Expected output**: a CITE audit report, a citation-trust verdict, and a short handoff summary ready for `memory/audits/domain/`.

- **Reads**: the target domain, supporting authority signals, and comparison domains.
- **Writes**: a user-facing authority report plus a reusable summary that can be stored under `memory/audits/domain/`.
- **Promotes**: veto items and domain risks to `memory/hot-cache.md` (auto-saved). Authority context to `memory/audits/domain/`. Results feed into entity-optimizer as authority input for brand's canonical profile.
- **Done when**: all 40 CITE items are scored or marked N/A with a named source, a TRUSTED/CAUTIOUS/UNTRUSTED verdict is stated, and any veto (T03/T05/T09) is surfaced with a fix.
- **Primary next skill**: use the `Next Best Skill` below once the trust picture is clear.

## Data Sources

> See [CONNECTORS.md](../../CONNECTORS.md) for tool category placeholders.

> **Note:** All integrations are optional. This skill works without any API keys — users provide data manually when no tools are connected.

**With ~~link database + ~~SEO tool + ~~AI monitor + ~~knowledge graph + ~~brand monitor connected:**
Automatically pull backlink profiles and link quality metrics from ~~link database, domain authority scores and keyword rankings from ~~SEO tool, AI citation data from ~~AI monitor, entity presence from ~~knowledge graph, and brand mention data from ~~brand monitor.

**With manual data only:**
Ask the user to provide:
1. Domain to evaluate
2. Domain type (if not auto-detectable): Content Publisher, Product & Service, E-commerce, Community & UGC, Tool & Utility, or Authority & Institutional
3. Backlink data: referring domains count, domain authority, top linking domains
4. Traffic estimates (from any SEO tool or SimilarWeb)
5. Competitor domains for comparison (optional)

Proceed with the full 40-item audit using provided data. Note in the output which items could not be fully evaluated due to missing access (e.g., AI citation data, knowledge graph queries, WHOIS history).

## Decision Gates

When stopping to ask, always: (1) state the specific value and threshold, (2) offer numbered options with outcomes.

**Stop and ask the user when:**
- The domain is not resolvable or its type cannot be detected — state what you found and confirm the domain type before scoring
- No backlink / referring-domain data is provided and none is inferable — offer: (1) provide an export, (2) score the observable CITE items and mark link-dependent items N/A
- More than 50% of a CITE dimension's items are N/A — name the dimension and ask: (1) provide supplementary data, (2) mark the dimension Insufficient Data
- Any veto item (T03, T05, or T09) triggers — flag it immediately with the item ID and ask: (1) stop for immediate fix, (2) continue full audit and flag in report

**Continue silently (never stop for):**
- Missing AI-citation data (mark items N/A and continue)
- Individual Partial scores within a dimension
- Low overall score (the report is the deliverable, not a judgment call)

## Instructions

When a user requests a domain authority audit:

### Step 1: Preparation

```markdown
### Audit Setup

**Domain**: [domain]
**Domain Type**: [auto-detected or user-specified]
**Dimension Weights**: [from domain-type weight table below]

#### Domain-Type Weight Table

> Canonical source: `references/cite-domain-rating.md`. This inline copy is for convenience.

| Dim | Default | Content Publisher | Product & Service | E-commerce | Community & UGC | Tool & Utility | Authority & Institutional |
|-----|:-------:|:-:|:-:|:-:|:-:|:-:|:-:|
| C | 35% | **40%** | 25% | 20% | 35% | 25% | **45%** |
| I | 20% | 15% | **30%** | 20% | 10% | **30%** | 20% |
| T | 25% | 20% | 25% | **35%** | 25% | 25% | 20% |
| E | 20% | 25% | 20% | 25% | **30%** | 20% | 15% |

#### Critical Trust Check (Emergency Brake)

| Check | Status | Action |
|-------|--------|--------|
| Link profile matches real traffic | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Audit backlink profile; disavow toxic links"] |
| Backlink profile is unique to this domain | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Flag as manipulation network; investigate link sources"] |
| No Google penalties or deindexing | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Address penalty first; all other optimization is futile"] |
```

If any critical trust check triggers, flag it prominently at the top of the report using plain language. CITE Score is capped per [Runbook §2](../../references/auditor-runbook.md).

### Step 2: C + I Audit (20 items)

Evaluate each item against the criteria in [references/cite-domain-rating.md](../../references/cite-domain-rating.md).

Score each item:
- **Pass** = 10 points (fully meets criteria)
- **Partial** = 5 points (partially meets criteria)
- **Fail** = 0 points (does not meet criteria)

```markdown
### C — Citation

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| C01 | Referring Domains Volume | Pass/Partial/Fail | [specific observation] |
| C02 | Referring Domains Quality | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |
| C10 | Link Source Diversity | Pass/Partial/Fail | [specific observation] |

**C Score**: [X]/100

### I — Identity

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| I01 | Knowledge Graph Presence | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |

**I Score**: [X]/100
```

### Step 3: T + E Audit (20 items)

Same format for Trust and Eminence dimensions.

```markdown
### T — Trust

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| T01 | Link Profile Naturalness | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |

**T Score**: [X]/100

### E — Eminence

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| E01 | Organic Search Visibility | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |

**E Score**: [X]/100
```

**Note**: Some items require specialized data (C05-C08 AI citation data, I01 knowledge graph queries, T04-T05 IP/profile analysis). Score what is observable; mark unverifiable items as "N/A — requires [data source]" and exclude from dimension average.

## Auditor Runbook — read this first

**Before scoring, `Read ../../references/auditor-runbook.md`.** It is the authoritative, framework-agnostic
procedure: §1 Handoff Schema, §2 Critical Fail Cap method + decision table + deterministic rounding,
§4 Artifact Gate 7-item checklist, §5 User-Facing Translation format, and the untrusted-content
security boundary. It loads locally via relative path (no network) — do not skip it. This skill body
carries only the **CITE-specific** pieces below: the weighted worked examples, the domain-level
guardrails, and the CITE veto-ID translation rows.

### Handoff Summary

Emit the auditor-class handoff defined in
[references/auditor-runbook.md §1](../../references/auditor-runbook.md): `status`, `objective`,
`key_findings`, `evidence_summary`, `recommended_next_skill`, plus the auditor fields `cap_applied`,
`raw_overall_score` (CITE weighted `C×0.35 + I×0.20 + T×0.25 + E×0.20`, floor-rounded, before cap),
and `final_overall_score`.

## §2 (CITE) · Worked examples — weighted cap arithmetic

> Walk the runbook's §2 decision table, then mirror the matching example below. The CITE Score is
> the **4-dimension weighted total** `C×0.35 + I×0.20 + T×0.25 + E×0.20`
> (see [cite-domain-rating.md](../../references/cite-domain-rating.md)), floor-rounded, before the cap.
> CITE has four dimensions (C/I/T/E) — there is no 8-dimension /8 average here.

### Worked example 1 — single veto, raw dim above cap

```
Dimensions:  C=80 I=70 T=85 E=75
Weighted:    80×0.35 + 70×0.20 + 85×0.25 + 75×0.20
           = 28.0 + 14.0 + 21.25 + 15.0 = 78.25 → raw_overall = 78

Veto check: T09 failed (Google manual action / deindex history on record)

After cap:  T dimension 85 → 60 (capped down, raw > 60)
            Overall 78 → 60 (any veto forces overall cap)

Handoff:    cap_applied: true   raw_overall_score: 78   final_overall_score: 60
            key_findings:
              - title: "Google manual action on record"
                severity: veto
                evidence: "Search Console shows an active manual action against the domain"
```

### Worked example 2 — single veto, raw dim already below cap

```
Dimensions:  C=55 I=70 T=58 E=72
Weighted:    55×0.35 + 70×0.20 + 58×0.25 + 72×0.20
           = 19.25 + 14.0 + 14.5 + 14.4 = 62.15 → raw_overall = 62

Veto check: T03 failed (backlink volume far exceeds real traffic — link-farm pattern)

After cap:  T dimension 58 → 58 (unchanged; cap is a ceiling, not a floor)
            Overall 62 → 60 (overall still capped because a veto is present)

Handoff:    cap_applied: true   raw_overall_score: 62   final_overall_score: 60
            key_findings:
              - title: "Backlink volume inconsistent with real traffic"
                severity: veto
                evidence: "1.2M referring-domain links but estimated <800 monthly organic visits"
```

The T dimension stays 58 in the internal report — it is NOT raised to 60. The cap is a ceiling only.

### Worked example 3 — 2+ veto fails (BLOCKED path)

```
Dimensions:  C=80 I=70 T=85 E=75  →  raw_overall = 78

Veto check: T05 AND T09 both failed

Resolution: status: BLOCKED — do NOT compute capped scores.
            raw_overall_score retained for record; final_overall_score omitted.

Handoff:    status: BLOCKED   cap_applied: false   raw_overall_score: 78
            open_loops:
              - "2 veto items failed: T05 (manipulation network) and T09 (manual action)"
              - "Multi-veto cap calibration pending; domain requires manual review before re-scoring"
            key_findings:
              - title: "Backlink profile overlaps a known manipulation network"
                severity: veto
              - title: "Google manual action on record"
                severity: veto
```

## §3 (CITE) · Guardrail Negatives (domain-level signals)

These signals are easy to over-flag. Treat them as NEUTRAL or POSITIVE under the stated condition —
do not deduct trust automatically. **Conditions are explicit.**

| Signal | Treat as NOT manipulation WHEN | Flag only IF |
|---|---|---|
| Sudden backlink spike | A real launch, funding round, press hit, or viral post explains it | Spike is from unrelated, low-quality, or templated domains with no editorial context |
| Few backlinks, strong brand | An established offline/branded entity with low link velocity by nature | Thin links AND no brand search demand AND no editorial mentions |
| Shared hosting / same IP block | A CDN, shared host, or platform (Cloudflare, Vercel, Shopify) concentrates many sites on one IP | Distinct PBN fingerprint: same registrant, template, interlinking, and thin content across the set |
| High nofollow share | Links come from legitimate news, UGC, or social platforms that nofollow by policy | nofollow share paired with paid-link or sponsored-without-disclosure patterns |
| Young domain age | A real new business with organic growth and disclosed ownership | Young domain + aggressive exact-match anchors + link velocity inconsistent with traffic |

If context contradicts a neutral reading, state the exception in the finding's `evidence` field
(e.g. "spike of 4,000 links in 48h, all from one templated footer network").

## §5 (CITE) · Veto-ID translation rows

Use alongside the runbook's shared translation rows. These are the **CITE** veto meanings —
never the CORE-EEAT ones (the same ID strings mean different things there).

| Internal | User-facing |
|---|---|
| "T03 failed" | "Backlink volume far exceeds real traffic (link-farm pattern)" |
| "T05 failed" | "Backlink profile nearly identical to another domain (manipulation network)" |
| "T09 failed" | "Google manual action or deindexing on record" |

### Step 4: Scoring & Report

Calculate scores and generate the final report:

```markdown
## CITE Domain Authority Report

### Overview

- **Domain**: [domain]
- **Domain Type**: [type]
- **Audit Date**: [date]
- **CITE Score**: [score]/100 ([rating])
- **Veto Status**: ✅ No triggers / ⚠️ Critical issue present *(score reflects cap per Runbook §2)*

### Dimension Scores

| Dimension | Score | Rating | Weight | Weighted |
|-----------|-------|--------|--------|----------|
| C — Citation | [X]/100 | [rating] | [X]% | [X] |
| I — Identity | [X]/100 | [rating] | [X]% | [X] |
| T — Trust | [X]/100 | [rating] | [X]% | [X] |
| E — Eminence | [X]/100 | [rating] | [X]% | [X] |
| **CITE Score** | | | | **[X]/100** |

**Score Calculation**: CITE Score = C × [w_C] + I × [w_I] + T × [w_T] + E × [w_E]

**Rating Scale**: 90-100 Excellent | 75-89 Good | 60-74 Medium | 40-59 Low | 0-39 Poor

### Per-Item Scores

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| C01 | Referring Domains Volume | [Pass/Partial/Fail] | [observation] |
| C02 | Referring Domains Quality | [Pass/Partial/Fail] | [observation] |
| ... | ... | ... | ... |
| E10 | Industry Share of Voice | [Pass/Partial/Fail] | [observation] |

### Findings by Severity Tier

Render BEFORE "Top 5 Priority Improvements". Group, sort, and translate every `key_findings` entry per [Runbook §5 Severity tier routing + shared translation rows](../../references/auditor-runbook.md) — no `P0/P1/P2` or `severity:` literals in user output; omit empty-tier headers.

```markdown
**Critical issues (must fix)**
- [Item Name] — [plain-language observation]

**Should-fix**
- [Item Name] — [observation]

**Nice-to-have**
- [Item Name] — [observation]
```

### Top 5 Priority Improvements

Sorted by: weight × points lost across all tiers (highest impact first). This is the cross-tier highlight; the per-tier breakdown above is the full picture.

1. **[ID] [Name]** — [specific modification suggestion]
   - Current: [Fail/Partial] | Potential gain: [X] weighted points
   - Action: [concrete step]
2. **[ID] [Name]** — [specific modification suggestion]
   - Current: [Fail/Partial] | Potential gain: [X] weighted points
   - Action: [concrete step]
3–5. [Same format]

### Action Plan

#### Quick Wins (< 1 week)
- [ ] [Action 1]
- [ ] [Action 2]
#### Medium Effort (1-4 weeks)
- [ ] [Action 3]
- [ ] [Action 4]
#### Strategic (1-3 months)
- [ ] [Action 5]
- [ ] [Action 6]

### Cross-Reference with CORE-EEAT

For a complete assessment, pair this CITE audit with a CORE-EEAT content audit:

| Assessment | Score | Rating |
|-----------|-------|--------|
| CITE (Domain) | [X]/100 | [rating] |
| CORE-EEAT (Content) | [Run content-quality-auditor on sample pages] | — |

**Diagnosis Matrix**:
- High CITE + High CORE-EEAT → Maintain and expand
- High CITE + Low CORE-EEAT → Prioritize content quality
- Low CITE + High CORE-EEAT → Build domain authority
- Low CITE + Low CORE-EEAT → Start with content, then domain

### Recommended Next Steps

- For domain authority building: focus on top 5 priorities above
- For content improvement: use `content-quality-auditor` on key pages
- For backlink strategy: use `offsite-signal-analyzer` for detailed link analysis
- For competitor benchmarking: use `competitor-analysis` with CITE scores
- For tracking progress: run `/aaron-marketing:seo-geo --mode track --report` with CITE score trends
```

### Step 4.5: Apply Scoring Runbook

Execute in order, using the framework-agnostic procedure in [references/auditor-runbook.md](../../references/auditor-runbook.md) together with the CITE-specific §2 worked examples, §3 guardrails, and §5 veto rows in this file:

1. **Cap Enforcement** (Runbook §2): walk the decision table. Identify which scenario matches your input (0 veto, 1 veto above cap, 1 veto below cap, or 2+ veto). Apply the cap rule — remember it's a ceiling, not a floor. Set `cap_applied` in the handoff. For CITE, single-veto fails also raise a **Manipulation Alert** entry in `open_loops`.
2. **Artifact Gate Self-Check** (Runbook §4): run the 7-item checklist. If any item fails, force `status: BLOCKED` with reason in `open_loops`.
3. **User-Facing Translation** (Runbook §5): translate internal language before rendering the user-facing report. Veto IDs (T03, T05, T09), raw-vs-capped deltas, and internal field names must not appear in the rendered output. The handoff YAML retains the raw values for downstream consumers; the user sees plain-language findings and a single score with the explanatory sentence.

### Save Results

Write the audit artifact to `memory/audits/domain/YYYY-MM-DD-<topic>.md` (the per-role path from [skill-contract.md §Write Paths](../../references/skill-contract.md); the PostToolUse Artifact Gate validates anything under `memory/audits/`) with `class: auditor-output` in its frontmatter. Promote any veto issues to `memory/hot-cache.md`. `memory-management` later rolls these into the monthly `memory/audits/YYYY-MM.md` aggregate. Do not save audit artifacts to a bare `memory/` path — that bypasses the gate.

## Validation Checkpoints

### Input Validation
- [ ] Domain identified and accessible
- [ ] Domain type confirmed (auto-detected or user-specified)
- [ ] Backlink data available (at minimum: referring domains count, DA (Moz Domain Authority™) / DR (Ahrefs Domain Rating™))
- [ ] If comparative audit, competitor domains also specified

### Output Validation
- [ ] All 40 items scored (or marked N/A with reason)
- [ ] All 4 dimension scores calculated correctly
- [ ] Weighted CITE Score matches domain-type weight configuration
- [ ] All 3 veto items checked first and flagged if triggered
- [ ] **Findings by Severity Tier section rendered before Top 5** — at least one tier (Critical / Should-fix / Nice-to-have) is non-empty when key_findings has items; empty-tier headers are omitted
- [ ] Top 5 improvements sorted by weighted impact, not arbitrary
- [ ] Every recommendation is specific and actionable (not generic advice)
- [ ] Action plan includes concrete steps with effort estimates
- [ ] No P0/P1/P2 or `severity: …` literals in user-visible output (translation per Runbook §5)

## Example

See [Example Report](references/example-report.md) for a complete CITE audit of cloudhosting.com showing veto check, dimension scores, top 5 improvements, action plan, and cross-reference with CORE-EEAT.

## Tips for Success

1. **Start with veto items** — T03, T05, T09 can invalidate the entire score
2. **Identify domain type first** — Different types have very different weight profiles
3. **AI citation items (C05-C08) matter most for GEO** — Test by querying AI engines with niche-relevant questions
4. **Some items need specialized tools** — Knowledge graph queries, AI citation monitoring, and IP diversity analysis may require manual research if tools aren't connected
5. **Pair with CORE-EEAT for full picture** — Domain authority without content quality (or vice versa) tells only half the story

## Reference Materials

- [CITE Domain Rating](../../references/cite-domain-rating.md) — Full 40-item benchmark with dimension definitions, scoring criteria, domain-type weight tables, and veto items
- [references/example-report.md](references/example-report.md) — Complete CITE audit example with scored dimensions, top 5 improvements, action plan, and CORE-EEAT cross-reference

## Next Best Skill

CAUTIOUS + link-quality: [offsite-signal-analyzer](../offsite-signal-analyzer/SKILL.md). UNTRUSTED: [entity-optimizer](../../protocol/entity-optimizer/SKILL.md). TRUSTED: terminal. Visited-set rule applies per [skill-contract.md](../../references/skill-contract.md).
