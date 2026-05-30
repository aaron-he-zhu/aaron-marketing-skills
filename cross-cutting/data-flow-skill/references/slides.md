# Slides Reference

Slides should summarize validated findings for a specific audience and decision moment.

## Slide Context Artifact

Before creating slides, save or derive `output/artifacts/report_context.json` with:

- Audience.
- Presentation goal.
- Narrative arc.
- Key messages.
- Figure and table references.
- Known limitations.
- Speaker-note preference.

## Recommended Deck Shape

1. Title and decision question.
2. Executive takeaway.
3. Data scope and method in one slide.
4. Three to five evidence slides with clear chart references.
5. Recommendation or action-priority slide.
6. Risks, limitations, and next steps.
7. Appendix for detailed tables or definitions.

## Rules

- Do not restart analysis from raw data unless the user asks.
- Use `analysis_findings.json` and report context as the source of truth.
- Keep one primary message per slide.
- Pair charts with a takeaway and optional speaker notes.
- Do not hide caveats that affect interpretation.