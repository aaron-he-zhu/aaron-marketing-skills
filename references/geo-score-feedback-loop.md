# GEO Score Feedback Loop

Closes the open loop flagged by Panel P5 (GEO specialist): the library's `GEO Score = CORE avg` is a **prediction** of AI citation likelihood, but there is no mechanism to verify the prediction against actual AI-engine behavior. This file defines a lightweight feedback loop that records predicted vs actual and surfaces model drift.

Referenced by:
- [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) — produces the prediction
- [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) — consumes the prediction
- [ai-overview-recovery playbook](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/ai-overview-recovery.md) — ground-truth source for actuals

---

## The prediction

When `content-quality-auditor` runs, it produces a `GEO Score` (0-100) equal to the average of the CORE dimensions (C/O/R/E). The claim: higher GEO Score predicts higher likelihood of being cited by AI engines.

This is a hypothesis, not a proven fact. Validation requires checking actual AI behavior.

## The feedback structure

Each audited URL gets a feedback record appended to `memory/geo-feedback/<YYYY-MM>.md`. One record per URL per measurement date.

### Record format

```yaml
---
url: https://example.com/blog/email-marketing-guide
predicted_geo_score: 72              # CORE avg at audit time
audit_date: 2026-04-17
first_measured: 2026-05-01           # at least 2 weeks post-audit
---

## Measurements

### 2026-05-01 (T+14)

**Queries tested** (natural AI engine prompts related to the URL's target):
- "What is email marketing automation"
- "Best email marketing practices for small business"
- "Email marketing vs newsletter"

**AI engine behavior**:
| Engine     | Cited? | Position in carousel | Quote used? | Notes |
|------------|--------|----------------------|-------------|-------|
| ChatGPT    | yes    | 2 of 4               | yes         | Quoted stat "64% open rate" verbatim |
| Perplexity | yes    | 1 of 6               | yes         | Quoted CTA template |
| Claude     | no     | —                    | —           | Cited a competitor instead |
| Gemini     | partial| —                    | no          | Mentioned domain but no quote |
| AI Overview (Google) | yes | 3 of 5 | no | Cited as source |

**Actual citation rate**: 3.5 / 5 engines = 70% weighted
**Predicted GEO Score**: 72
**Delta**: −2 (within noise; prediction tracked actual)

### 2026-06-01 (T+45)

<same structure>

---

## Drift assessment (after N≥10 records)

Run monthly via `/seo:geo-drift-review`:

- Mean absolute error (|predicted − actual|)
- Rank correlation (Spearman) between predicted scores and actual citation rates
- Systematic bias direction (does the model over- or under-predict on average?)
- Per-dimension attribution (does weighting the dimensions differently help?)

If drift > 15 points MAE across 10+ records, the GEO Score formula itself needs revisiting. This is a governance signal for the Auditor Runbook `§6 Lint Coverage Manifest`.
```

## Measurement protocol

Measurements follow this cadence:

- **T+0 (audit day)**: `content-quality-auditor` produces GEO Score; skill writes initial record with `predicted_geo_score` and `audit_date`, no measurements yet.
- **T+14**: first measurement. User (or agency) runs each engine with the target queries, records citation behavior.
- **T+45**: second measurement. Re-run same queries.
- **T+90**: third measurement. Compare to T+14 — has the prediction held over time?

After T+90, the record is considered closed. Archive to `memory/geo-feedback/archive/<YYYY>.md`.

## Test query selection

For a given URL, 3-5 test queries should:

1. **Natural** — phrase as a user would search, not as SEO keywords
2. **Within the URL's intent scope** — if URL targets "email marketing for small business", queries span that topic
3. **Include at least 1 comparison / question format** — AI engines over-index on these
4. **Include at least 1 competitor-mention query** — tests citation vs competitor

Default templates (adapt to URL's topic):

- `What is <primary topic>`
- `How to <primary action>`
- `Best <thing> for <audience>`
- `<entity> vs <competitor>` (if entity profile exists)
- `Why is <pain point> happening`

## Engine test procedure (manual for Tier 1 users)

For each engine, paste the query in its native UI. Record:

- Was the URL's domain cited? (yes / no / partial)
- Position in citation carousel (if shown)
- Was a quote from the URL used verbatim? (yes / no)
- If not cited: who was cited instead? (competitor / unrelated / none)

For Tier 3 users with `~~AI monitor` MCP connected, this can be automated.

## Honesty note

GEO Score as CORE-average is a reasonable hypothesis (CORE dimensions correlate with the signals AI engines appear to favor based on public statements from Perplexity / ChatGPT / Google). But:

- No vendor publishes the actual weighting AI engines use.
- Weightings likely change as AI engines update retrieval models.
- The feedback loop above is the only way to detect when the library's hypothesis diverges from reality.

Agencies and serious GEO teams should feed data into this loop monthly. Individual users can skip it — the feedback is a governance feature, not a per-audit requirement.

## Handoff additions

`content-quality-auditor` handoff gains optional feedback seeding fields:

```yaml
geo_validation:
  predicted_geo_score: 72
  feedback_record: memory/geo-feedback/2026-04.md  # path where prediction was seeded
  measurement_due: 2026-05-01                      # T+14
```

These fields are OPTIONAL — omit for single-use audits. Include when the user is running on a tracked project that wants long-term GEO quality signals.
