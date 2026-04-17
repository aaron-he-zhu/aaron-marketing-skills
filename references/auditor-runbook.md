# Auditor Runbook (authoritative)

> **Runbook version**: 1.1
> **Release**: v7.1.0
> **Last updated**: 2026-04-11
> **Changes since 1.0**: Example 1 arithmetic corrected to integer; added cross-version rerun rule (§5); added BLOCKED-path escape hatch (§5); clarified open_loops scope (§5); dual-hash sync markers (§6).
> **Next scheduled review**: 2026-07-10 (tied to P2 trigger evaluation)

This file is the single source of truth for auditor-class skill output behavior. It is inlined into:
- [cross-cutting/content-quality-auditor/SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)
- [cross-cutting/domain-authority-auditor/SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/domain-authority-auditor/SKILL.md)

Drift detection: `/seo:contract-lint` validates inlined copies against this file via **two** sha256 hashes carried in sync markers: `source_sha256` over the whole Runbook file, and `block_sha256` over the inlined §1-5 content. Either hash mismatch is a drift event. Manual edits to inlined copies are forbidden — edit this source file and re-run the sync procedure (see [AUDITOR-AUTHORS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/AUDITOR-AUTHORS.md)).

## Ownership Routing (read this before asking "which file owns what")

- **Auditor item definitions** (veto IDs, dimension structure) → [core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md) for CORE-EEAT, [cite-domain-rating.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md) for CITE
- **Cap numbers** (the literal "60" and future "40") → [contract-fail-caps.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/contract-fail-caps.md) (v7.2.0); until that file ships, numbers live here in §2
- **Application arithmetic, handoff schema, translation rules** → this file (§1 through §6)
- **General handoff format for all skills** → [skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md)

Any restatement of a rule outside its owning file is a drift bug and will be flagged by `/seo:contract-lint`.

---

## §1 · Handoff Schema (authoritative)

Every auditor-class handoff MUST follow this shape. Emitted audit artifact files (e.g., `memory/audits/**/*.md`) MUST include `class: auditor-output` in their YAML frontmatter so the PostToolUse Artifact Gate and Stop-time archiving hooks can detect them by frontmatter class instead of prose pattern-matching. Files lacking this marker are not treated as audit artifacts regardless of body content.

```yaml
---
class: auditor-output            # REQUIRED frontmatter marker for emitted audit artifacts
---

status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_INPUT
objective: "what was audited"
key_findings:
  - title: short issue name
    severity: veto | high | medium | low
    evidence: direct quote or data point
evidence_summary: URLs / data points reviewed
open_loops: blockers or missing inputs
recommended_next_skill: primary next move

# Cap-related fields — AUDITOR-CLASS ONLY
cap_applied: true | false        # REQUIRED for auditors
raw_overall_score: <number>      # REQUIRED for auditors; score before cap
final_overall_score: <number>    # REQUIRED for auditors; score after cap
```

### Backward compatibility (v7.1.0 → v7.2.0 deprecation window)

Downstream skills consuming handoffs must treat the cap-related fields as **optional with documented defaults** during the deprecation window. If absent, apply these defaults:

- `cap_applied: false` (assume no cap when field missing)
- `raw_overall_score: <use final_overall_score>` (treat as equal)
- `final_overall_score: <use the overall score from the audit, whatever field name>`

This prevents breakage when an audit produced before the upgrade is consumed by a skill after the upgrade. A consuming skill MUST never error on missing cap fields during the deprecation window. After v7.2.0, fields become required for all auditor-class producers; consumers may then treat absence as a BLOCKED upstream.

### Non-auditor skills

Non-auditor skill handoffs follow [skill-contract.md §Handoff Summary Format](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) as-is. Cap-related fields do not apply. Non-auditors never emit `cap_applied` / `raw_overall_score` / `final_overall_score`, and MUST NOT use the `class: auditor-output` frontmatter marker.

---

## §2 · Critical Fail Cap — Decision Table and Worked Examples

> **How to use this section in Step 4.5**: re-read Worked Example 1 below **before** computing your own cap. Mirror its "Before cap / Veto check / After cap / Handoff" format literally. Walk the decision table (4 rows) to identify which scenario matches your input. Count veto failures across all dimensions (not per-dimension). Apply the cap rule — it is a ceiling, not a floor.

**Rule summary**: when any veto item fails, cap the affected dimension and the overall score at **60/100**. Show raw and capped side by side in the internal report. Set `cap_applied: true` in handoff.

**Veto items**:
- CORE-EEAT: T04, C01, R10 — see [core-eeat-benchmark.md §Veto Items](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)
- CITE: T03, T05, T09 — see [cite-domain-rating.md §Veto Items](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/cite-domain-rating.md)

### Decision table

| Scenario | Affected dimension behavior | Overall score behavior | Handoff status |
|---|---|---|---|
| **0 veto fails** | no cap | no cap | `cap_applied: false` |
| **1 veto fails; raw dim > 60** | `min(raw_dim, 60)` → capped down to 60 | `min(raw_overall, 60)` | `cap_applied: true` |
| **1 veto fails; raw dim ≤ 60** | unchanged (no raise, no lower) | `min(raw_overall, 60)` | `cap_applied: true` |
| **2+ veto fails** | `status: BLOCKED`, do NOT emit capped scores | `raw_overall_score` retained for record | `cap_applied: false`, reason in `open_loops` |

**Cap target**: always the post-penalty final dimension value, never the raw pre-penalty value. If non-veto items already penalized the dimension, compute the post-penalty number first, then apply the veto cap to that.

**Rounding rule (deterministic)**: all score arithmetic uses `math.floor` (truncate decimals). `77.5 → 77`, not `78`. `59.9 → 59`, not `60`. Applies to `raw_overall_score`, `final_overall_score`, dimension scores, and all intermediate calculations. QA and regression tests can rely on this — a re-run on the same inputs always produces the same integer. Worked Example 2 demonstrates: `raw_overall = 77.5` appears as `raw_overall_score: 77` in the handoff.

### Worked example 1 — single veto, raw dim above cap (classic case)

```
Before cap:
  Dimensions: C=75 O=77 R=80 E=75 Exp=78 Ept=77 A=77 T=85
  Sum = 624; raw_overall = 624 / 8 = 78 (exact)

Veto check: T04 failed (affiliate links without disclosure)

After cap:
  T dimension: 85 → 60 (capped down because raw > 60)
  Overall: 78 → 60 (capped at 60 because any veto forces overall cap)

Handoff:
  cap_applied: true
  raw_overall_score: 78
  final_overall_score: 60
  key_findings:
    - title: "Missing affiliate disclosure"
      severity: veto
      evidence: "No disclosure banner; 3 affiliate links detected in body"
```

### Worked example 2 — single veto, raw dim already below cap

```
Before cap:
  Dimensions: C=55 O=75 R=88 E=80 Exp=80 Ept=75 A=82 T=85
  raw_overall = 77.5

Veto check: C01 failed (clickbait — title doesn't match content)

After cap:
  C dimension: 55 → 55 (unchanged; cap is a ceiling, not a floor)
  Overall: 77 → 60 (overall still capped because veto present)

Handoff:
  cap_applied: true
  raw_overall_score: 77
  final_overall_score: 60
  key_findings:
    - title: "Title promises something the page doesn't deliver"
      severity: veto
      evidence: "Title: '10 Free Tools'; body delivers 3 free tools and 7 paid"
```

**Important**: the C dimension number in the internal report stays 55. It is NOT raised to 60. The cap is a ceiling only.

### Worked example 3 — 2+ veto fails (BLOCKED path)

```
Before cap:
  Dimensions: C=75 O=77 R=80 E=75 Exp=78 Ept=77 A=77 T=85
  Sum = 624; raw_overall = 624 / 8 = 78 (exact)

Veto check: T04 AND R10 both failed

Resolution:
  status: BLOCKED
  Do NOT compute capped scores.
  raw_overall_score retained for record; final_overall_score omitted.

Handoff:
  status: BLOCKED
  cap_applied: false
  raw_overall_score: 78
  # final_overall_score intentionally omitted
  open_loops:
    - "2 veto items failed: T04 (affiliate disclosure) and R10 (data inconsistency)"
    - "Multi-veto cap calibration pending v7.3; page requires manual review before re-scoring"
  key_findings:
    - title: "Missing affiliate disclosure"
      severity: veto
      evidence: "..."
    - title: "Data points contradict each other"
      severity: veto
      evidence: "..."
```

**Why BLOCKED, not "capped at 40"**: the 40-tier cap number is unvalidated. Blocking forces manual review, which is more honest than publishing an eyeballed number. Calibration trigger: 30+ real multi-veto audits in `memory/audits/`. Review date: 2026-07-10 via `/seo:p2-review`.

**Note on dimension vs count**: the 2+ veto threshold counts **total veto failures across all dimensions**, not per-dimension. Example 3 shows T04 (Trust dim) + R10 (Referenceability dim) on different dimensions, but T03 + T09 both on the Trust dimension would also trigger BLOCKED. The veto count is dimension-agnostic.

---

## §3 · Guardrail Negatives (windowed positive reframes)

These signals are POSITIVE under stated conditions. Award points, do not deduct. **Conditions are explicit — unconditional positive reframes cause false negatives.**

| Signal | Treat as positive WHEN | Example flag rule |
|---|---|---|
| Year marker in title/body | Year is within `[current_year − 2, current_year]` | "2026" in 2026: freshness positive. "2020" in 2026: R-dimension concern, review for staleness — do NOT award freshness |
| Numbered list ("5 best", "Top 10", "3 steps") | Always | CTR positive, counts toward O-dimension structure |
| Qualifier ("Open-Source", "Self-Hosted", "Free", "Local-First") | Always | Narrow intent, counts toward E-dimension exclusivity |
| Short acronym ("SEO", "AI", "CRM", "API") | Always | Never apply length or stop-word filter to these tokens |
| Homepage brand-first title ("Acme \| AI Workflow") | The page IS the homepage | Correct pattern; do not flag under C01 |
| Inner-page keyword-first title ("AI Workflow for Teams — Acme") | The page is NOT the homepage | Correct pattern; do not flag under C01 |

### Exception path

If the content is explicitly evergreen or the context contradicts a positive reframe, state the exception in the finding's `evidence` field. For example:

> "Year 2024 appears in title. Content is labeled 'evergreen guide' and aims for 2+ year longevity; the 2024 stamp will date the page unnecessarily. Flagged for R dimension."

### Current year reference

The windowed year rule depends on the date at audit time, not a hardcoded year in this file. Evaluate `current_year` dynamically when applying §3.

---

## §4 · Artifact Gate Checklist (7-item self-check)

Before emitting the handoff, the auditor verifies:

- [ ] `status` is one of the 4 enum values (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT)
- [ ] `key_findings` is an array (may be empty)
- [ ] Every finding has `title` + `severity` + `evidence`
- [ ] `cap_applied` is explicitly set (true or false) — auditor-class requirement
- [ ] `raw_overall_score` present (auditor-class requirement; may equal `final_overall_score`)
- [ ] `final_overall_score` present UNLESS `status == BLOCKED`
- [ ] `evidence_summary` non-empty
- [ ] `recommended_next_skill` present

If any check fails, force `status: BLOCKED` with `open_loops: ["artifact_gate_failed: <which check>"]`.

> **Reliability note**: v7.2.0 adds a PostToolUse hook that re-validates this checklist outside the self-check loop, in a clean LLM context. Self-check is first line of defense (~35% reliable); external hook is second line (~85%). Together: ~95%. Until the hook ships, rely on self-check with awareness that it is not robust against the auditor's own output bias.

---

## §5 · User-Facing Translation Layer

Before rendering to the user, translate internal language. This respects [skill-contract.md §Response Presentation Norms](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) which forbids internal jargon in user output.

### Forbidden in user-visible output

- Veto item IDs (T04, C01, R10, T03, T05, T09, and any future IDs)
- Phrases combining "dimension" or "capped at" with raw numbers
- Internal field names: `cap_applied`, `raw_overall_score`, `final_overall_score`, `gap_type`
- Raw score deltas like "82 → 60" as the primary presentation

### Required pattern when cap is applied

```markdown
**Overall Score: 60/100**  *(capped due to 1 critical issue)*

**Critical issue to fix:**
- Missing affiliate disclosure on your product review
  *(search engines and AI engines treat unsigned affiliate content as low-trust)*

**Fix this one item and your score rises to approximately 78.**
```

### Required pattern when status is BLOCKED (multi-veto)

```markdown
**Status: Cannot score yet** — 2 critical issues need attention first.

1. Missing affiliate disclosure on your product review
2. Data points contradict each other (prices in intro section don't match the comparison table)

Fix these, then rerun the audit for a score.
```

### Cross-version context (rerun after upgrade)

Before rendering the score to the user, check `memory/audits/` for any prior audit of the same URL (by `target` field match). If a prior audit exists AND the new `final_overall_score` differs from the prior `final_overall_score` by more than 10 points, AND the prior audit was produced by a Runbook version earlier than the current one, **prepend a one-line explainer** to the user output.

**Version detection logic** (process in order):
1. If prior archive has `runbook_version` field → compare directly
2. If prior archive is **missing** the `runbook_version` field entirely → treat as pre-v7.1.0 (this is the common upgrade case — always trigger the explainer)
3. Never use `cap_applied: false` as a version proxy — it is ambiguous between "old audit" and "new clean audit"

Explainer template:

```markdown
> **Note**: This page scored {prior_score} under an older scoring rule. Under v7.1.0's Critical Issue rule, one trust item now caps the score at {final}. The page content is unchanged — only the scoring rule changed.
```

If no prior audit exists, skip this rule silently. Never invent a prior score.

**Why**: users whose rerun drops 82 → 60 without explanation file bug reports. The inline note preserves trust by separating "content quality changed" from "rule changed".

### Escape hatch for explicit user requests (still no IDs, ever)

If a user explicitly asks for "raw scoring details", "which veto items failed", or "why is my score lower", translate to plain language rather than leak IDs or refuse. The escape hatch means "explain more", not "bypass the translation layer". Provide the underlying mechanism in marketer terms:

**Single-veto escape hatch example**:

✅ "The most-critical trust dimension on your page was reduced to the minimum because one trust item failed — specifically, affiliate links without a disclosure banner. Once you add the disclosure, the full score is restored."

❌ "T04 failed, raw T=85, capped to 60" (contains veto ID and raw/capped delta)

❌ "I can't share that information" (refuses a legitimate request, damages trust)

For the BLOCKED case (2+ critical issues), the "Required pattern when status is BLOCKED" template above is the only required user-facing pattern. No separate escape hatch is needed — the template itself provides the plain-language explanation.

### Open_loops field translation (internal vs user-facing)

The `open_loops` field in the handoff YAML is **internal state for downstream skills** (content-refresher, seo-content-writer consume it to pick the next fix). It MAY contain raw veto IDs and internal phrasing because the consumer is another skill, not a user.

However, if a user request ever surfaces `open_loops` to the user directly — for example, "show me all pending issues" or "what's still open on this page" — the surfacing skill MUST translate each open_loops entry to plain language using the Never-say → Always-say mapping below before rendering. The raw open_loops array never reaches a user's screen.

### Never say → Always say (plain-language mapping)

| Internal | User-facing |
|---|---|
| "T04 failed" | "Missing affiliate disclosure" |
| "C01 veto triggered" | "Title doesn't match what the page delivers" |
| "R10 failure" | "Data on the page contradicts itself" |
| "T03 failed" | "HTTPS security is not fully enforced" |
| "T05 failed" | "No published editorial or review policy" |
| "T09 failed" | "Reviews show authenticity concerns" |
| "cap_applied: true" | "capped due to N critical issue(s)" |
| "raw_overall_score: 78" | "your score rises to approximately 78 once this is fixed" |
| "dimension capped at 60" | (never expose; describe the underlying fix instead) |

---

## §6 · Lint Coverage Manifest

This section enumerates what `/seo:contract-lint` (v7.2.0) checks against. When this manifest changes, `commands/contract-lint.md` must be updated in the same commit. `/seo:contract-lint` opens with a reference to this §6 and refuses to run if its internal check list is older than the Runbook version.

### Current coverage (v7.1.0)

- **Handoff schema fields**: `status`, `objective`, `key_findings[]` with `{title, severity, evidence}`, `evidence_summary`, `open_loops`, `recommended_next_skill`, `cap_applied`, `raw_overall_score`, `final_overall_score`
- **Veto items checked**: CORE-EEAT T04/C01/R10, CITE T03/T05/T09
- **Cap arithmetic rule**: `final_dim = min(raw_dim, 60)` when veto failed; `final_overall = min(raw_overall, 60)` when any veto failed; `status = BLOCKED` when ≥2 vetos failed
- **Guardrail reframes**: years windowed to `[current_year − 2, current_year]`; numbered lists / qualifiers / short acronyms unconditionally positive; homepage vs inner-page title patterns
- **Forbidden user-output substrings**: veto IDs (T03, T04, T05, T09, C01, R10), "capped at", "raw_overall_score", "gap_type", "cap_applied", "final_overall_score". Allowed-in-user-output: the word "capped" followed by "due to" (as in "capped due to 1 critical issue")
- **Cross-version rule**: if `memory/audits/` contains a prior audit of the same target with a materially different score (delta > 10) under an earlier Runbook version, the user output must carry an inline explainer distinguishing "content changed" from "rule changed"
- **Open_loops scope**: internal field for downstream skill consumption; veto IDs permitted in handoff YAML; MUST be translated to plain language if ever surfaced to the user
- **Sync markers**: `<!-- runbook-sync start: source_sha256=<hash1> block_sha256=<hash2> -->` and `<!-- runbook-sync end -->` in both auditor SKILL.md files. `source_sha256` matches the full runbook file (detects Attack A — source edited). `block_sha256` matches the bytes between start/end markers (detects Attack B — inlined copy edited). Both must match for a clean lint.
- **Known allowlist exceptions**: the inlined runbook-sync blocks in `cross-cutting/content-quality-auditor/SKILL.md` and `cross-cutting/domain-authority-auditor/SKILL.md` are the ONLY permitted restatements of cap numbers and runbook content. All other files must link-not-restate.

### Update protocol

**When editing §1-5 (execution-critical content)**:

1. Append (or remove) the corresponding entry in §6 if a lintable rule changed
2. Update `commands/contract-lint.md` check list to match
3. Bump Runbook version at the top of this file
4. Recompute both hashes (`source_sha256` over the full runbook file, `block_sha256` over §1-5 content as inlined) and update sync markers in both auditor SKILL.md files
5. Re-inline §1-5 content into both auditor SKILL.md files
6. Commit everything in one commit

**When editing ONLY §6 (Lint Coverage Manifest) or only the header/ownership routing**:

1. Bump Runbook version at the top of this file
2. Recompute `source_sha256` only (the full file hash changed). `block_sha256` stays the same (§1-5 content is unchanged)
3. Update `source_sha256` in both auditor SKILL.md sync markers — but do NOT re-inline the block content (it hasn't changed)
4. Update `commands/contract-lint.md` check list if §6 items changed
5. Commit everything in one commit

This avoids unnecessary re-inline churn on §6-only edits while still ensuring `source_sha256` tracks the full Runbook state. Contract-lint will report a `source_sha256` mismatch if step 2-3 are skipped, which is the intended fail-closed behavior.
