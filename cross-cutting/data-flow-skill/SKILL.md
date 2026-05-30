---
name: data-flow-skill
version: "9.9.9"
description: 'Use when the user asks to analyze datasets, detect data types, create charts, summarize findings, and produce report- or slide-ready outputs for SEO, GEO, content, marketing, academic, or business analysis. For live crawling, URL extraction, or SERP collection, use a research or audit skill first.'
license: Apache-2.0
compatibility: "Claude Code ≥1.0, skills.sh marketplace, ClawHub marketplace, Vercel Labs skills ecosystem."
metadata:
  author: aaron-he-zhu
  version: "9.9.9"
  geo-relevance: "medium"
  tags: [seo, geo, analytics, data-analysis, visualization, reporting]
  triggers: ["analyze this dataset", "generate an analytics report", "create charts from this data", "summarize performance data", "build a data report"]
---

# Data Flow Skill

## Quick Start

Use this skill when the user provides a dataset and asks for analysis, visualization, findings, reports, or slide-ready summaries. It supports SEO/GEO analytics, content performance reviews, marketing dashboards, questionnaire analysis, time-series analysis, and academic or business reporting.
First confirm the dataset location, task goal, audience, expected deliverables, language, and style. Detect the dataset type before choosing an analysis strategy. Create `plan.md` and ask the user to confirm it before formal analysis begins.
Do not use this skill as the first step for live crawling, URL extraction, SERP collection, or third-party API collection. Collect data with the appropriate research, audit, or monitoring skill first, then use this skill for analysis.

## Skill Contract

### Inputs

Required:
- A dataset file, directory, or clearly described data source.
- A task description, including the question to answer, metric to explain, report to produce, or audience to serve.
Optional:
- Output type: exploratory analysis, SEO/GEO performance report, business summary, academic report, visualization pack, or slide-ready summary.
- Language, tone, and style preferences.
- Preprocessing preference: `minimal`, `auto`, `strict`, `no preprocessing`, or user-defined rules.
- Field definitions, metric formulas, time windows, target variables, scale direction, or segment definitions.
  
### Outputs

Recommended structure:
```text
output/
  figures/
  tables/
  report/
  slides/
  artifacts/
    dataset_detection.json
    data_profile.json
    preprocessing_log.json
    visualization_plan.json
    analysis_findings.json
    report_context.json
```
Minimum expectations:
- Save structured artifacts in `output/artifacts/`.
- Save charts in `output/figures/` and tables in `output/tables/`.
- Preserve the source data unless the user explicitly requests otherwise.
- Record dataset detection, assumptions, preprocessing actions, findings, limitations, and confidence levels.
  
### Boundaries

This skill can detect dataset types, profile data, run modular analysis, generate charts, summarize evidence-backed findings, and prepare report- or slide-ready outputs.
This skill should not fetch live URLs unless explicitly allowed, claim causality from descriptive analysis, silently modify source data, or complete the whole workflow through one monolithic script.

### Handoff Summary

Before handing work to another skill or stage, summarize:

- Dataset name, source path, file type, row count, column count, and detected strategy.
- User goal, audience, deliverables, language, and style.
- Assumptions and unresolved questions.
- Preprocessing actions and log paths.
- Main findings, evidence, limitations, and confidence levels.
- Paths to charts, tables, artifacts, reports, and slides.
- Recommended next skill if crawling, optimization, publishing, monitoring, or auditing is needed.
  
## Data Sources

Supported inputs include CSV, TSV, XLSX, JSON, JSONL, TXT, exported analytics files, Search Console exports, GA4 exports, ranking tables, conversion reports, keyword sheets, backlink tables, entity coverage sheets, content inventories, questionnaire data, time-indexed metrics, and text corpora.
For SEO/GEO analytics, look for fields such as query, page, URL, country, device, date, search appearance, clicks, impressions, CTR, average position, sessions, engagement, conversions, revenue, rankings, or visibility.
When field semantics are unclear, ask the user before analysis. Pay attention to metric definitions, time zones, scale direction, duplicate identifiers, missing values, and whether higher or lower values represent better outcomes.

## Instructions

### 1. Detect the Dataset Type

Start every formal task by selecting the most appropriate strategy:
- `tabular_generic`: general structured datasets.
- `questionnaire`: surveys, scales, questionnaires, or mixed closed/open-ended responses.
- `time_series`: data with a meaningful time index or repeated observations over time.
- `literary`: poems, couplets, novels, scripts, dialogues, or other literary/textual corpora.
Write the detection result to `output/artifacts/dataset_detection.json`. Include strategy, confidence, evidence, alternatives, assumptions, and fallback plan.

### 2. Create and Confirm a Plan

Before formal analysis, create `plan.md` and ask the user to confirm it. The plan should include objective, audience, dataset summary, detected strategy, open questions, assumptions, preprocessing plan, analysis tasks, visualization outline, expected outputs, risks, and validation checkpoints.
Do not proceed to formal analysis, report generation, or slide generation until the user confirms the plan.

### 3. Understand and Profile the Data

Profile the data before cleaning or modeling. Check file type, parsing issues, row count, column count, data types, unique values, missingness, duplicates, invalid values, outliers, inconsistent categories, date coverage, time granularity, metric distributions, and segment coverage. Save the profile to `output/artifacts/data_profile.json`.

### 4. Preprocess Transparently

Do not silently modify source data. Log every preprocessing action in `output/artifacts/preprocessing_log.json`. Common actions include normalizing column names, parsing dates and numeric fields, removing justified duplicates, standardizing categories, handling missing values, creating explicit derived metrics, and segmenting data.

### 5. Split Analysis into Small Tasks

Keep analysis modular. Avoid a single all-in-one script that reads, cleans, analyzes, visualizes, and writes every output at once. Use separate task units for one preprocessing check, one metric group, one statistical test, one chart, one model, or one finding-generation pass. Inspect each output before deciding the next step.

### 6. Analyze by Strategy

For `tabular_generic`, summarize metrics, compare groups, identify correlations, anomalies, outliers, and practical implications.
For `questionnaire`, validate scale direction, summarize response distributions, compare groups, analyze reliability when scale items exist, and separate closed-ended from open-ended responses.
For `time_series`, confirm time granularity, analyze trend, seasonality, spikes, drops, and period-over-period changes. Avoid leakage when comparing or modeling time windows.
For `literary`, respect genre, corpus boundaries, metadata, and textual units. Analyze vocabulary, structure, themes, entities, motifs, sentiment, or stylistic patterns where appropriate.

### 7. Plan and Generate Visualizations

Create `output/artifacts/visualization_plan.json` before final charts. Each chart entry should include title, question answered, input path, variables, chart type, reason for chart choice, output path, and interpretation notes.
Use a diverse chart set covering overview, trend, distribution, comparison, relationship, composition, and anomaly views unless the user requests a smaller scope. Pair every key chart with at least one analytical paragraph.

### 8. Generate Structured Findings

Save findings to `output/artifacts/analysis_findings.json`. Each finding should include claim, evidence, source artifact or chart path, scope, limitation, confidence level, and recommended action or next question.
For SEO/GEO outputs, separate observed performance changes, plausible explanations, optimization opportunities, and items requiring additional crawling, SERP review, ranking checks, or content audit.

### 9. Produce Reports and Slides

When a report is requested, build it from validated artifacts. Include executive summary, methodology, data quality notes, key metrics, trends, segment analysis, visual evidence, findings, recommendations, limitations, and appendix material. Do not stack charts without explanation.
When slides are requested, derive them from `analysis_findings.json` and `report_context.json`. Include audience, presentation goal, narrative arc, key messages, recommended slide titles, figure/table references, and speaker notes when requested. Do not restart analysis from raw data unless explicitly asked.

## Reference Materials

Detailed guidance may be placed in the skill's `references/` subdirectory instead of inline in `SKILL.md`.
Recommended files:
- `references/workflow.md`
- `references/data-types.md`
- `references/visualization.md`
- `references/reporting.md`
- `references/slides.md`
- `references/validation.md`
  
If the host repository requires placeholder-style tool references, use patterns such as `~~read`, `~~write`, `~~shell`,or `~~webfetch`. Do not assume live web access unless explicitly allowed.

## Validation Checkpoints

Before proceeding past each stage, verify that:
- Dataset type has been detected and documented.
- The user has confirmed `plan.md` before formal analysis begins.
- Field semantics, metric definitions, time windows, and scale directions are clear or documented as assumptions.
- Source data is preserved and preprocessing actions are logged.
- Analysis tasks are split into small, inspectable units.
- Charts have documented purposes and output paths.
- Key charts are paired with interpretation.
- Findings include evidence, limitations, and confidence.
- Reports are based on structured artifacts.
- Slides are based on report or finding context.
- Claims do not exceed the evidence.
- Outputs are saved in predictable paths.
- The handoff summary is complete enough for another skill or contributor to continue.

## Example

User request:
```text
Analyze this Google Search Console export and create a performance report for our SEO team.
```

Expected execution:
1. Confirm file path, date range, target site, audience, and report format.
2. Detect the dataset as `tabular_generic` or `time_series`.
3. Create `plan.md` with assumptions, analysis steps, chart plan, output paths, and checkpoints.
4. After confirmation, profile query, page, country, device, clicks, impressions, CTR, and average position.
5. Check missing values, date coverage, duplicates, branded/non-branded patterns, and segment coverage.
6. Analyze trends, top pages, top queries, declining segments, CTR-position opportunities, device/country differences, and content opportunities.
7. Generate charts for trend, contribution, distribution, segment comparison, and opportunity prioritization.
8. Save structured findings with evidence and confidence.
9. Produce a report with executive summary, visual evidence, recommendations, and limitations.
10. Provide slide-ready key messages if requested.
    
## Tips for Success

- Ask clarifying questions early when metric meaning or output expectations are unclear.
- Prefer reproducible, inspectable artifacts over hidden transformations.
- State what the data shows, what it suggests, and what remains uncertain.
- Separate descriptive findings from recommendations.
- For SEO/GEO datasets, connect findings to search visibility, content coverage, entity relevance, user intent, and measurable outcomes.
  
## Save Results

At the end of the task, provide a concise completion summary with what was analyzed, which strategy was used, main findings, files created or updated, known limitations, and recommended next actions. Use relative paths when reporting outputs.

## Next Best Skill

Use another skill before this one when data still needs to be collected from live sources, crawled pages, SERPs, APIs, or third-party tools.
Use another skill after this one when the user wants to convert findings into SEO briefs, content updates, schema markup, optimization tasks, page audits, monitoring workflows, publishing steps, implementation tickets, or a content roadmap.
