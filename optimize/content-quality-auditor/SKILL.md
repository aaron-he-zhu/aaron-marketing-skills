---
name: content-quality-auditor
description: 'Use when auditing content quality, E-E-A-T, or publish readiness; runs 80-item CORE-EEAT scoring with veto checks and a fix plan. Not for structural on-page tags/headers — use on-page-seo-auditor; not for domain/citation trust — use domain-authority-auditor. 内容质量/EEAT评分'
version: "12.0.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when auditing content quality before publishing. Runs CORE-EEAT 80-item scoring with veto checks. Also when the user asks for E-E-A-T analysis or publish readiness."
argument-hint: "<URL or paste content> [keyword]"
allowed-tools: WebFetch
class: auditor
metadata:
  author: aaron-he-zhu
  version: "12.0.0"
  discipline: seo-geo
  phase: optimize
  geo-relevance: "high"
---

# Content Quality Auditor

> Based on [CORE-EEAT Content Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark). Full benchmark reference: [references/core-eeat-benchmark.md](../../references/core-eeat-benchmark.md)

This skill evaluates content quality across 80 standardized criteria organized in 8 dimensions. It produces a comprehensive audit report with per-item scoring, dimension and system scores, weighted totals by content type, and a prioritized action plan.

## When This Must Trigger

Use this when content needs a quality check before publishing — even if the user doesn't use audit terminology:

- User asks "is this ready to publish" or "how good is this"
- User just finished writing with content-writer (new or refresh mode)
- **PostToolUse hook recommendation**: after content is written or substantially edited, the command-backed hook may recommend this audit. When hook-triggered, skip setup questions — audit the content that was just produced.
- Auditing content quality before publishing
- Evaluating existing content for improvement opportunities
- Benchmarking content against CORE-EEAT standards
- Comparing content quality against competitors
- Assessing both GEO readiness (AI citation potential) and SEO strength (source credibility)
- Running periodic content quality checks as part of a content maintenance program
- After writing or optimizing content with content-writer or geo-content-optimizer

## What This Skill Does

1. **Full 80-Item Audit**: Scores every CORE-EEAT check item as Pass/Partial/Fail
2. **Dimension Scoring**: Calculates scores for all 8 dimensions (0-100 each)
3. **System Scoring**: Computes GEO Score (CORE) and SEO Score (EEAT)
4. **Weighted Totals**: Applies content-type-specific weights for final score
5. **Veto Detection**: Flags critical trust violations (T04, C01, R10)
6. **Priority Ranking**: Identifies Top 5 improvements sorted by impact
7. **Action Plan**: Generates specific, actionable improvement steps

## Quick Start

Start with one of these prompts. Finish with a publish verdict and a handoff summary using the repository format in [Skill Contract](../../references/skill-contract.md).

### Audit Content

```
Audit this content against CORE-EEAT: [content text or URL]
```

```
Run a content quality audit on [URL] as a [content type]
```

### Audit with Content Type

```
CORE-EEAT audit for this product review: [content]
```

```
Score this how-to guide against the 80-item benchmark: [content]
```

### Comparative Audit

```
Audit my content vs competitor: [your content] vs [competitor content]
```

## Skill Contract

**Gate verdict**: **SHIP** (no critical issues, dimension scores above threshold) / **FIX** (issues found but none critical) / **BLOCK** (a critical trust issue failed — see "Critical Issue to Fix" in the report). Always state the verdict prominently at the top of the report using plain language, not item IDs.

**Expected output**: a CORE-EEAT audit report, a publish-readiness verdict, and a short handoff summary ready for `memory/audits/content/`.

- **Reads**: the target content, content type, and supporting evidence.
- **Writes**: a user-facing audit report plus a reusable summary that can be stored under `memory/audits/content/`.
- **Promotes**: veto items and publish blockers to `memory/hot-cache.md` (auto-saved, no user confirmation needed). Top improvement priorities to `memory/open-loops.md`.
- **Done when**: all 80 CORE-EEAT items are scored or marked N/A, a SHIP/FIX/BLOCK verdict is stated, `cap_applied`/`raw_overall_score`/`final_overall_score` are set, and any veto (T04/C01/R10) is surfaced with a fix.
- **Primary next skill**: use the `Next Best Skill` below once the verdict is clear.

## Data Sources

> See [CONNECTORS.md](../../CONNECTORS.md) for tool category placeholders.

**With ~~web crawler + ~~SEO tool connected:**
Fetch only user-provided or authorized URLs after [SECURITY.md §Scraping Boundaries](../../SECURITY.md); then extract HTML, schema, links, and competitor content.

**With manual data only:**
Ask the user to provide:
1. Content text, URL, or file path
2. Content type (if not auto-detectable): Product Review, How-to Guide, Comparison, Landing Page, Blog Post, FAQ Page, Alternative, Best-of, or Testimonial
3. Optional: competitor content for benchmarking

Proceed with the full 80-item audit using provided data. Note in the output which items could not be fully evaluated due to missing access (e.g., backlink data, schema markup, site-level signals).

## Decision Gates

When stopping to ask, always: (1) state the specific value and threshold, (2) offer numbered options with outcomes.

**Stop and ask the user when:**
- Content is under minimum word count for its type (blog/guide: 300 words; product/landing page: 150 words; FAQ: fewer than 3 entries with 50+ words each) — state the actual count and offer: (1) expand to minimum, (2) continue audit with Insufficient Data flags, (3) cancel
- Content type cannot be auto-detected — state what you detected and ask to confirm before proceeding
- Content is primarily media (video/image) with minimal text — ask whether to audit transcript, alt text, or skip
- More than 50% of a dimension's items are N/A — name the dimension and ask: (1) provide supplementary data, (2) mark entire dimension as Insufficient Data
- Any veto item triggers — flag it immediately with the item ID and ask: (1) stop for immediate fix, (2) continue full audit and flag in report

**Continue silently (never stop for):**
- Individual Partial scores within a dimension
- Missing SEO tool data (mark items as N/A and continue)
- Low overall score (the report is the deliverable, not a judgment call)
- User not specifying content type (auto-detect and state your assumption)

## Instructions

When a user requests a content quality audit:

### Step 1: Preparation

```markdown
### Audit Setup

**Content**: [title or URL]
**Content Type**: [auto-detected or user-specified]
**Dimension Weights**: [loaded from content-type weight table]

#### Critical Trust Check (Emergency Brake)

| Check | Status | Action |
|-------|--------|--------|
| Affiliate links disclosed | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Add disclosure banner at page top immediately"] |
| Title matches page content | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Rewrite title and first paragraph to match"] |
| Data points are consistent | ✅ Pass / ⚠️ CRITICAL | [If CRITICAL: "Verify all data before publishing"] |
```

If any veto item triggers, flag it prominently at the top of the report and recommend immediate action before continuing the full audit.

### Step 2: CORE Audit (40 items)

Evaluate each item against the criteria in [references/core-eeat-benchmark.md](../../references/core-eeat-benchmark.md).

Score each item:
- **Pass** = 10 points (fully meets criteria)
- **Partial** = 5 points (partially meets criteria)
- **Fail** = 0 points (does not meet criteria)

```markdown
### C — Contextual Clarity

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| C01 | Intent Alignment | Pass/Partial/Fail | [specific observation] |
| C02 | Direct Answer | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |
| C10 | Semantic Closure | Pass/Partial/Fail | [specific observation] |

**C Score**: [X]/100
```

Repeat the same table format for **O** (Organization), **R** (Referenceability), and **E** (Exclusivity), scoring all 10 items per dimension.

### Step 3: EEAT Audit (40 items)

```markdown
### Exp — Experience

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| Exp01 | First-Person Narrative | Pass/Partial/Fail | [specific observation] |
| ... | ... | ... | ... |

**Exp Score**: [X]/100
```

Repeat the same table format for **Ept** (Expertise), **A** (Authority), and **T** (Trust), scoring all 10 items per dimension.

See [references/item-reference.md](references/item-reference.md) for the complete 80-item ID lookup table and site-level item handling notes.

## Auditor Runbook — read this first

**Before scoring, `Read ../../references/auditor-runbook.md`.** It is the authoritative, framework-agnostic
procedure: §1 Handoff Schema, §2 Critical Fail Cap method + decision table + deterministic rounding,
§4 Artifact Gate 7-item checklist, §5 User-Facing Translation format, and the untrusted-content
security boundary. It loads locally via relative path (no network) — do not skip it. This skill body
carries only the **CORE-EEAT-specific** pieces below: the weighted worked examples, the content-level
guardrails, and the CORE-EEAT veto-ID translation rows.

### Handoff Summary

Emit the auditor-class handoff defined in
[references/auditor-runbook.md §1](../../references/auditor-runbook.md): `status`, `objective`,
`key_findings`, `evidence_summary`, `recommended_next_skill`, plus the auditor fields `cap_applied`,
`raw_overall_score` (content-type weighted, floor-rounded, before cap), and `final_overall_score`.

## §2 (CORE-EEAT) · Worked examples — weighted cap arithmetic

> Walk the runbook's §2 decision table, then mirror the matching example below. `raw_overall_score`
> is the **content-type weighted total** (Σ dimension × weight from
> [core-eeat-benchmark.md §Content-Type Weight Table](../../references/core-eeat-benchmark.md)),
> floor-rounded, before the cap. Never the unweighted /8 mean.

### Worked example 1 — single veto, raw dim above cap (Product Review)

```
Dimensions:  C=75 O=77 R=80 E=75 Exp=78 Ept=77 A=77 T=85
Weights (Product Review): C .10  O .10  R .15  E .20  Exp .20  Ept .05  A .05  T .15
Weighted:    75×.10 + 77×.10 + 80×.15 + 75×.20 + 78×.20 + 77×.05 + 77×.05 + 85×.15
           = 7.5 + 7.7 + 12.0 + 15.0 + 15.6 + 3.85 + 3.85 + 12.75 = 78.25 → raw_overall = 78

Veto check: T04 failed (affiliate links without disclosure)

After cap:  T dimension 85 → 60 (capped down, raw > 60)
            Overall 78 → 60 (any veto forces overall cap)

Handoff:    cap_applied: true   raw_overall_score: 78   final_overall_score: 60
            key_findings:
              - title: "Missing affiliate disclosure"
                severity: veto
                evidence: "No disclosure banner; 3 affiliate links detected in body"
```

### Worked example 2 — single veto, raw dim already below cap (FAQ Page)

```
Dimensions:  C=55 O=75 R=88 E=80 Exp=80 Ept=75 A=82 T=85
Weights (FAQ Page): C .25  O .25  R .15  E .05  Exp .05  Ept .10  A .05  T .10
Weighted:    55×.25 + 75×.25 + 88×.15 + 80×.05 + 80×.05 + 75×.10 + 82×.05 + 85×.10
           = 13.75 + 18.75 + 13.2 + 4.0 + 4.0 + 7.5 + 4.1 + 8.5 = 73.8 → raw_overall = 73

Veto check: C01 failed (clickbait — title doesn't match content)

After cap:  C dimension 55 → 55 (unchanged; cap is a ceiling, not a floor)
            Overall 73 → 60 (overall still capped because a veto is present)

Handoff:    cap_applied: true   raw_overall_score: 73   final_overall_score: 60
            key_findings:
              - title: "Title promises something the page doesn't deliver"
                severity: veto
                evidence: "Title: '10 Free Tools'; body delivers 3 free tools and 7 paid"
```

The C dimension stays 55 in the internal report — it is NOT raised to 60. Note that the weighted
total (73) differs from the unweighted /8 mean (77) — always score with the weighted total.

### Worked example 3 — 2+ veto fails (BLOCKED path)

```
Dimensions:  C=75 O=77 R=80 E=75 Exp=78 Ept=77 A=77 T=85  (Product Review weights → raw_overall = 78)

Veto check: T04 AND R10 both failed

Resolution: status: BLOCKED — do NOT compute capped scores.
            raw_overall_score retained for record; final_overall_score omitted.

Handoff:    status: BLOCKED   cap_applied: false   raw_overall_score: 78
            open_loops:
              - "2 veto items failed: T04 (affiliate disclosure) and R10 (data inconsistency)"
              - "Multi-veto cap calibration pending; page requires manual review before re-scoring"
            key_findings:
              - title: "Missing affiliate disclosure"
                severity: veto
              - title: "Data points contradict each other"
                severity: veto
```

## §3 (CORE-EEAT) · Guardrail Negatives (content / page reframes)

These signals are POSITIVE under the stated condition. Award points, do not deduct. **Conditions are
explicit — unconditional reframes cause false negatives.**

| Signal | Treat as positive WHEN | Example flag rule |
|---|---|---|
| Year marker in title/body | Year is within `[current_year − 2, current_year]` | "2026" in 2026: freshness positive. "2020" in 2026: R-dimension concern — do NOT award freshness |
| Numbered list ("5 best", "Top 10", "3 steps") | Always | CTR positive, counts toward O-dimension structure |
| Qualifier ("Open-Source", "Self-Hosted", "Free", "Local-First") | Always | Narrow intent, counts toward E-dimension exclusivity |
| Short acronym ("SEO", "AI", "CRM", "API") | Always | Never apply length or stop-word filter to these tokens |
| Homepage brand-first title ("Acme \| AI Workflow") | The page IS the homepage | Correct pattern; do not flag under C01 |
| Inner-page keyword-first title ("AI Workflow for Teams — Acme") | The page is NOT the homepage | Correct pattern; do not flag under C01 |

If context contradicts a positive reframe (e.g. an explicitly evergreen page carrying a year stamp),
state the exception in the finding's `evidence` field. Evaluate `current_year` dynamically at audit time.

## §5 (CORE-EEAT) · Veto-ID translation rows

Use alongside the runbook's shared translation rows. These are the **CORE-EEAT** veto meanings —
never the CITE ones.

| Internal | User-facing |
|---|---|
| "T04 failed" | "Missing affiliate disclosure" |
| "C01 veto triggered" | "Title doesn't match what the page delivers" |
| "R10 failure" | "Data on the page contradicts itself" |

### Step 4: Scoring & Report

Calculate scores and generate the final report:

```markdown
## CORE-EEAT Audit Report

### Overview

- **Content**: [title]
- **Content Type**: [type]
- **Audit Date**: [date]
- **Total Score**: [score]/100 ([rating])
- **GEO Score**: [score]/100 | **SEO Score**: [score]/100
- **Veto Status**: ✅ No triggers / ⚠️ [item] triggered

### Dimension Scores

| Dimension | Score | Rating | Weight | Weighted |
|-----------|-------|--------|--------|----------|
| C — Contextual Clarity | [X]/100 | [rating] | [X]% | [X] |
| O — Organization | [X]/100 | [rating] | [X]% | [X] |
| R — Referenceability | [X]/100 | [rating] | [X]% | [X] |
| E — Exclusivity | [X]/100 | [rating] | [X]% | [X] |
| Exp — Experience | [X]/100 | [rating] | [X]% | [X] |
| Ept — Expertise | [X]/100 | [rating] | [X]% | [X] |
| A — Authority | [X]/100 | [rating] | [X]% | [X] |
| T — Trust | [X]/100 | [rating] | [X]% | [X] |
| **Weighted Total** | | | | **[X]/100** |

**Score Calculation**:
- GEO Score = (C + O + R + E) / 4
- SEO Score = (Exp + Ept + A + T) / 4
- Weighted Score = Σ (dimension_score × content_type_weight)

**Rating Scale**: 90-100 Excellent | 75-89 Good | 60-74 Medium | 40-59 Low | 0-39 Poor

### N/A Item Handling

When an item cannot be evaluated (e.g., A01 Backlink Profile requires site-level data not available):

1. Mark the item as "N/A" with reason
2. Exclude N/A items from the dimension score calculation
3. Dimension Score = (sum of scored items) / (number of scored items x 10) x 100
4. If more than 50% of a dimension's items are N/A, flag the dimension as "Insufficient Data" and exclude it from the weighted total
5. Recalculate weighted total using only dimensions with sufficient data, re-normalizing weights to sum to 100%

**Example**: Authority dimension with 8 N/A items and 2 scored items (A05=8, A07=5):
- Dimension score = (8+5) / (2 x 10) x 100 = 65
- But 8/10 items are N/A (>50%), so flag as "Insufficient Data — Authority"
- Exclude A dimension from weighted total; redistribute its weight proportionally to remaining dimensions

### Per-Item Scores

#### CORE — Content Body (40 Items)

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| C01 | Intent Alignment | [Pass/Partial/Fail] | [observation] |
| C02 | Direct Answer | [Pass/Partial/Fail] | [observation] |
| ... | ... | ... | ... |

#### EEAT — Source Credibility (40 Items)

| ID | Check Item | Score | Notes |
|----|-----------|-------|-------|
| Exp01 | First-Person Narrative | [Pass/Partial/Fail] | [observation] |
| ... | ... | ... | ... |

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

#### Quick Wins (< 30 minutes each)
- [ ] [Action 1]
- [ ] [Action 2]

#### Medium Effort (1-2 hours)
- [ ] [Action 3]
- [ ] [Action 4]

#### Strategic (Requires planning)
- [ ] [Action 5]
- [ ] [Action 6]

### Recommended Next Steps

- For full content rewrite: use `content-writer` with CORE-EEAT constraints
- For GEO optimization: use `geo-content-optimizer` targeting failed GEO-First items
- For content refresh: use `content-writer` with weak dimensions as focus
- For technical fixes: run `/aaron-marketing:seo-geo --mode audit --tech` for site-level issues
```

### Step 4.5: Apply Scoring Runbook

Execute in order, using the framework-agnostic procedure in [references/auditor-runbook.md](../../references/auditor-runbook.md) together with the CORE-EEAT-specific §2 worked examples, §3 guardrails, and §5 veto rows in this file:

1. **Cap Enforcement** (Runbook §2): walk the decision table. Identify which scenario matches your input (0 veto, 1 veto above cap, 1 veto below cap, or 2+ veto). Apply the cap rule — remember it's a ceiling, not a floor. Set `cap_applied` in the handoff.
2. **Artifact Gate Self-Check** (Runbook §4): run the 7-item checklist. If any item fails, force `status: BLOCKED` with reason in `open_loops`.
3. **User-Facing Translation** (Runbook §5): translate internal language before rendering the user-facing report. Veto IDs, raw-vs-capped deltas, and internal field names must not appear in the rendered output. The handoff YAML retains the raw values for downstream consumers; the user sees plain-language findings and a single score with the explanatory sentence.

### Save Results

Write the audit artifact to `memory/audits/content/YYYY-MM-DD-<topic>.md` (the per-role path from [skill-contract.md §Write Paths](../../references/skill-contract.md); the PostToolUse Artifact Gate validates anything under `memory/audits/`) with `class: auditor-output` in its frontmatter. Promote any veto issues to `memory/hot-cache.md`. `memory-management` later rolls these into the monthly `memory/audits/YYYY-MM.md` aggregate. Do not save audit artifacts to a bare `memory/` path — that bypasses the gate.

## Validation Checkpoints

### Input Validation
- [ ] Content source identified (text, URL, or file path)
- [ ] Content type confirmed (auto-detected or user-specified)
- [ ] Content is substantial enough for meaningful audit (≥300 words)
- [ ] If comparative audit, competitor content also provided

### Output Validation
- [ ] All 80 items scored (or marked N/A with reason)
- [ ] All 8 dimension scores calculated correctly
- [ ] Weighted total matches content-type weight configuration
- [ ] Veto items checked and flagged if triggered
- [ ] **Findings by Severity Tier section rendered before Top 5** — at least one tier (Critical / Should-fix / Nice-to-have) is non-empty when key_findings has items; empty-tier headers are omitted
- [ ] Top 5 improvements sorted by weighted impact, not arbitrary
- [ ] Every recommendation is specific and actionable (not generic advice)
- [ ] Action plan includes concrete steps with effort estimates
- [ ] No P0/P1/P2 or `severity: …` literals in user-visible output (translation per Runbook §5)

## Example

See [references/item-reference.md](references/item-reference.md) for a complete scored example showing the C dimension with all 10 items, priority improvements, and weighted scoring.

## Tips for Success

1. **Start with veto items** — T04, C01, R10 are deal-breakers regardless of total score
   > These veto items are consistent with the CORE-EEAT benchmark (Section 3), which defines them as items that can override the overall score.
2. **Focus on high-weight dimensions** — Different content types prioritize different dimensions
3. **GEO-First items matter most for AI visibility** — Prioritize items tagged GEO 🎯 if AI citation is the goal
4. **Some EEAT items need site-level data** — Don't penalize content for things only observable at the site level (backlinks, brand recognition)
5. **Use the weighted score, not just the raw average** — A product review with strong Exclusivity matters more than strong Authority
6. **Re-audit after improvements** — Run again to verify score improvements and catch regressions
7. **Pair with CITE for domain-level context** — A high content score on a low-authority domain signals a different priority than the reverse; run [domain-authority-auditor](../../monitor/domain-authority-auditor/SKILL.md) for the full 120-item picture

## Reference Materials

- [CORE-EEAT Content Benchmark](../../references/core-eeat-benchmark.md) — Full 80-item benchmark with dimension definitions, scoring criteria, and GEO-First item markers
- [Item Reference](references/item-reference.md) — All 80 item IDs in a compact lookup table + site-level item handling notes + scored example report
- [Recursive Refinement Loop](references/recursive-refinement.md) — Capped score → revise → rescore loop (MAX 3 rounds) toward the CORE-EEAT target band; a veto stays terminal and is never overridden by the loop
- [Humanizer Slop List](../../references/humanizer-slop.md) — **SOFT penalty (NON-veto)** mapped to the Experience/authenticity axis (E and Exp dimensions). Slop phrasing lowers those item scores; it never triggers a veto and never forces the overall cap.
- [Visual Quality Rubric](../../references/scoring-rubrics/visual-quality.md) — Advisory rubric for charts and graphics. Use to inform O-dimension structure notes when the content carries visuals; advisory only, not part of the 80-item score.
- [AI Citation Patterns](../../build/geo-content-optimizer/references/ai-citation-patterns.md) — Reference for AI-citation factors. Use to inform GEO-First item scoring (C/O/R/E) when AI visibility is the goal.

## Next Best Skill

FIX: [content-writer](../../build/content-writer/SKILL.md). BLOCK: [entity-optimizer](../../protocol/entity-optimizer/SKILL.md). SHIP: [rank-tracker](../../monitor/rank-tracker/SKILL.md).
