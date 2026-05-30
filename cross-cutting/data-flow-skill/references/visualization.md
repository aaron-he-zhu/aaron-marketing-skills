# Visualization Reference

Use visualizations to answer explicit questions, not to decorate the report.

## Chart Planning

Create `output/artifacts/visualization_plan.json` before final chart generation. Each chart should define:

- Title and question answered.
- Input artifact or table.
- Variables and filters.
- Chart type and reason for choosing it.
- Output path.
- Interpretation notes and limitations.

## Chart Families

- Overview: KPI cards, summary tables, bar charts.
- Trend: line charts, rolling averages, indexed trends, annotated event charts.
- Distribution: histograms, box plots, violin plots, density plots.
- Comparison: grouped bars, dot plots, slope charts, small multiples.
- Relationship: scatter plots, bubble charts, correlation heatmaps.
- Composition: stacked bars, treemaps, area charts when parts sum meaningfully.
- Anomaly: control-style charts, highlighted outliers, before/after panels.

## SEO/GEO Notes

For Search Console, GA4, ranking, or visibility data, pair charts with interpretation around query intent, page type, entity coverage, device/country segments, CTR-position opportunity, content decay, and measurement limitations.

## Quality Bar

Every key chart needs a plain-language takeaway. Avoid chart packs that lack narrative, mislabeled axes, unclear units, hidden filters, or unsupported causal claims.