---
name: geo-drift-check
description: Check whether audited content is being cited by AI engines (Claude, ChatGPT, Gemini, Perplexity, Google AI Overviews) and record drift between predicted GEO Score and actual citation rate. Uses only already-connected MCP tools; no API keys bundled.
argument-hint: "<URL or leave empty to re-check all records due>"
allowed-tools: ["WebFetch", "Read", "Write", "Edit"]
parameters:
  - name: url
    type: string
    required: false
    description: URL to check. If omitted, re-checks all URLs in memory/geo-feedback/ whose next T+14 / T+45 / T+90 measurement is due.
---

# GEO Drift Check Command

Closes the open loop defined in [references/geo-score-feedback-loop.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/geo-score-feedback-loop.md): validates each **predicted GEO Score** (from `content-quality-auditor`) against **actual AI-engine citation behavior** at T+14 / T+45 / T+90 intervals.

**Design philosophy — this is a pure-markdown command.** No Python script, no scheduled runner, no bundled API keys. The command uses whichever AI-engine MCP servers the user has already connected. When no MCP is available for an engine, the command degrades to a fill-in-the-blank prompt where the user pastes responses manually.

## Usage

```
/seo:geo-drift-check https://example.com/blog/my-article
/seo:geo-drift-check              # re-checks all records whose measurements are due
```

## Workflow

1. **Resolve target records**
   - If `<URL>` provided: locate or create the record in `memory/geo-feedback/<YYYY-MM>.md`.
   - Otherwise: scan `memory/geo-feedback/*.md` for records whose next scheduled measurement (T+14, T+45, or T+90 from `audit_date`) has arrived.
   - If nothing is due: report "No drift checks due" and exit.

2. **For each target URL**, re-run the validation loop from `references/geo-score-feedback-loop.md`:

   a. Read `predicted_geo_score`, `audit_date`, and past `queries_tested`. If no prior queries exist, derive 3-5 natural prompts a user would ask an AI engine about the URL's target keyword.

   b. Query each AI engine using whatever MCP the user has connected. Typical mappings:
      - **Claude** → Anthropic API (or skip if not configured)
      - **ChatGPT** → OpenAI MCP
      - **Perplexity** → Perplexity MCP
      - **Gemini** → Google AI MCP
      - **Google AI Overview** → SERP MCP (Ahrefs / SerpAPI / Semrush)

   c. If no MCP is available for an engine, prompt the user to paste that engine's response once. Mark skipped engines in the record.

   d. For each engine response, parse: **Cited?** (URL, domain, or verbatim quote appears) · **Position** (1-of-N in citation carousel) · **Quote used?** (verbatim sentence or stat from the page).

3. **Append measurement** to the record under `## Measurements`:
   ```yaml
   ### <today> (T+<days since audit>)
   Queries tested: [list]
   | Engine     | Cited? | Position | Quote? | Notes |
   | Claude     | yes    | 2 of 4   | yes    | Quoted "X%" stat |
   | ChatGPT    | no     | —        | —      | Cited a competitor |
   Actual citation rate: <cited/checked>
   Predicted GEO Score: <from audit>
   Delta: <predicted − actual×100>
   ```

4. **If the record has ≥3 measurements**, compute drift stats in-line and write them under `## Drift summary`:
   - **MAE** (mean absolute error) across all measurements
   - **Direction bias** (systematic over- or under-prediction)
   - **Best-tracking CORE dimension** (C/O/R/E with highest correlation to actual)

5. **Governance signal**: if aggregate MAE across ≥10 records exceeds 15, flag for `references/auditor-runbook.md §6 Lint Coverage Manifest` — the GEO Score formula itself may need recalibration.

## Output format

```
GEO Drift Check — N records processed

URL: https://example.com/blog/post-a
  Measurement: T+45 (2026-06-01)
  Predicted GEO Score: 72 | Actual citation rate: 70 (3.5/5 engines)
  Delta: −2 (within noise) ✓

URL: https://example.com/blog/post-b
  Measurement: T+14 (2026-05-01)
  Predicted GEO Score: 85 | Actual citation rate: 40 (2/5 engines)
  Delta: −45 ⚠ outlier — investigate
  Likely causes: low authority on target domain, recency cutoff, citation by competitor

Aggregate drift (N=12 records):
  MAE: 8.2 (< 15 threshold ✓)
  Direction: slight over-prediction (+3.1 avg)
  Best CORE tracker: R (relevance), r=0.71
```

## Experimental status

Marked **experimental in v9.0.0**. Requires:
- At least one AI engine MCP connected, OR user availability to paste engine responses manually
- Manual invocation (no CI cron by design)
- Monthly cadence is aspirational — if data accumulates and MAE stabilizes, v9.1 may promote this command to stable and relax the experimental warning

## Related

- [references/geo-score-feedback-loop.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/geo-score-feedback-loop.md) — full spec
- [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) — produces the prediction
- [memory-management](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md) — record storage
