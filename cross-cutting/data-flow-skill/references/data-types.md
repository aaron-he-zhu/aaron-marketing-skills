# Dataset Type Reference

Data Flow Skill selects one primary strategy before analysis. Mixed datasets may use a primary strategy with secondary checks.

## `tabular_generic`

Use for structured CSV, TSV, XLSX, database exports, analytics exports, keyword sheets, backlink tables, content inventories, ranking tables, and business metrics.

Check row/column counts, missingness, duplicates, metric ranges, categorical consistency, numeric parsing, date parsing, and segment coverage.

## `questionnaire`

Use for surveys, scales, feedback forms, evaluation forms, and mixed closed/open response data.

Confirm scale direction, response coding, respondent count, skip logic, multi-select representation, missing-response meaning, and grouping variables before summarizing.

## `time_series`

Use when the time index is central to the user question: daily Search Console exports, rankings over time, GA4 trends, revenue by period, logs, or repeated observations.

Confirm time zone, granularity, coverage, gaps, duplicates per timestamp, seasonality, campaign/event annotations, and leakage risk when comparing periods.

## `literary`

Use for poems, novels, scripts, dialogues, essays, song lyrics, or text corpora where genre and textual units matter.

Confirm corpus boundaries, author/source metadata, language, tokenization assumptions, segmentation units, quoted text handling, and whether interpretation should be descriptive or critical.

## Detection Artifact

`dataset_detection.json` should include:

- `strategy`
- `confidence`
- `evidence`
- `alternatives`
- `assumptions`
- `fallback_plan`
- `requires_user_confirmation`