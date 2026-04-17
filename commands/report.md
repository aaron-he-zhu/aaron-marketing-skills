---
name: report
description: Generate a comprehensive SEO and GEO performance report for a single domain, a named project, or across all projects in memory.
argument-hint: "<domain|project=slug|project=all> <time period>"
parameters:
  - name: domain
    type: string
    required: false
    description: "Single domain to report on (e.g., example.com). Mutually exclusive with --project."
  - name: project
    type: string
    required: false
    description: "Project slug (e.g., acme-q2) to load from memory/wiki/<slug>/index.md. Use `all` to aggregate every project registered in memory/wiki/*/index.md (agency cross-client mode). Mutually exclusive with domain."
  - name: period
    type: string
    required: true
    description: "Time period: last-month, last-quarter, Q[N]-[YYYY], [YYYY-MM-DD] to [YYYY-MM-DD], last-30-days, last-90-days"
  - name: comparison
    type: string
    required: false
    description: "Comparison period: vs previous-quarter, vs last-year, vs previous-period"
  - name: format
    type: string
    required: false
    description: "Output format: detailed (default) or executive (condensed for stakeholders)"
---

# Report Command

A comprehensive **SEO and GEO performance report** that aggregates data across all channels, identifies trends, and delivers actionable recommendations prioritized by impact.

## Usage

Single domain:
```
/seo:report example.com last-month
/seo:report example.com last-quarter vs previous-quarter
/seo:report example.com [YYYY-MM-DD] to [YYYY-MM-DD]
/seo:report example.com last-90-days format=executive
```

Named project (loads from `memory/wiki/<slug>/index.md`):
```
/seo:report project=acme-q2 last-month
```

Agency cross-client mode — aggregate all registered projects:
```
/seo:report project=all last-week
/seo:report project=all last-month format=executive
```

**Arguments:**
- Either `domain` OR `project=<slug>` OR `project=all` (required — exactly one)
- Time period (required): `last-month`, `last-quarter`, `Q[N]-[YYYY]`, `[YYYY-MM-DD] to [YYYY-MM-DD]`, `last-30-days`, `last-90-days`
- Comparison period (optional): `vs previous-quarter`, `vs last-year`, `vs previous-period`
- `format=executive` (optional): Condensed summary for stakeholders (default: `detailed`)

## Workflow

### Single-domain or single-project mode

1. **Resolve scope** — If `domain=X`, use X. If `project=<slug>`, read `memory/wiki/<slug>/index.md` to pull the domain(s) registered for that project (a project can own multiple domains).
2. **Generate Performance Report** — Invoke `performance-reporter` with resolved domain(s), period, and comparison. Collects data across all channels (organic traffic, rankings, backlinks, GEO visibility, technical health).
3. **Include CITE/CORE-EEAT Context** (optional) — If `domain-authority-auditor` or `content-quality-auditor` have been run previously for this domain, include latest scores.
4. **Compile Output** — Format below. For `format=executive`, include only Executive Summary and Prioritized Action Plan.

### Cross-project mode (`project=all`)

1. **Enumerate projects** — List every `memory/wiki/<slug>/index.md` file. Extract project name + owning domain(s).
2. **Per-project loop** — Run steps 2-3 of the single-project flow for each project. Collect per-project sections.
3. **Aggregate** — Build a cross-project executive summary: total traffic, aggregate rank movement, number of P0/P1 issues per project, cross-project patterns (e.g., "3 of 5 projects show Core Web Vitals regression"). The per-project detail sections render below the aggregate summary, each labeled with the project slug.
4. **Output** — Use the `CROSS-PROJECT` output format (below). `format=executive` collapses to aggregate summary + per-project one-liners.

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEO & GEO PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOMAIN: [domain]
PERIOD: [date range]
COMPARISON: [vs period]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXECUTIVE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE SNAPSHOT: key metrics with period-over-period changes
KEY WINS / CRITICAL CONCERNS / STRATEGIC RECOMMENDATIONS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DETAILED FINDINGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Organic Traffic Performance
2. Keyword Rankings & Visibility
3. Domain Authority (CITE Score)
4. Backlink Profile Health
5. Technical SEO Health
6. GEO Performance
7. Content Performance

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRIORITIZED ACTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

P0 CRITICAL / P1 HIGH / P2 MEDIUM / P3 LOW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
APPENDIX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Data Sources, Methodology, Historical Trends, Competitor Benchmarking

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Cross-Project Output Format (`project=all`)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CROSS-PROJECT PERFORMANCE REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECTS: [count] ([slug1], [slug2], ...)
PERIOD: [date range]
COMPARISON: [vs period]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AGGREGATE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total organic sessions: X (vs prev: Y, delta Z%)
Rank winners / losers: A / B (top-3 positions)
P0 issues across portfolio: N (by project: slug=n, ...)
Cross-project patterns: [1-3 bullets]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PER-PROJECT DETAIL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## [slug1] — [domain]
  [same 7-section structure as single-domain report, condensed]

## [slug2] — [domain]
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PORTFOLIO ACTION PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

P0 items across all projects, grouped by theme (not by project).
Useful for agencies planning the team's focus for the coming period.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Tips

- Compare to same period last year to account for seasonality
- Use `format=executive` for stakeholder presentations
- Verify analytics tracking is firing correctly before investigating drops
- Focus on trend analysis over absolute numbers when using manual data
- For `project=all`, ensure each project has a populated `memory/wiki/<slug>/index.md` first; otherwise run `/seo:wiki-lint` to see which projects are registered

## Related Skills

- [performance-reporter](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/monitor/performance-reporter/SKILL.md) -- Comprehensive performance reporting
- [domain-authority-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/domain-authority-auditor/SKILL.md) -- CITE domain authority scoring
- [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md) -- CORE-EEAT content quality scoring
