# Data Flow Workflow Reference

Use this reference when a task needs more detail than the compact `SKILL.md` workflow.

## Stage Order

1. Confirm the user goal, audience, dataset location, deliverables, language, and style.
2. Detect the dataset strategy and save `output/artifacts/dataset_detection.json`.
3. Draft `plan.md` and wait for user confirmation before formal analysis.
4. Profile the raw data and save `output/artifacts/data_profile.json`.
5. Preprocess only when justified, preserving source files and logging each action.
6. Run analysis in small, inspectable task units.
7. Draft a visualization plan before final chart production.
8. Generate evidence-backed findings with scope, limitation, confidence, and next action.
9. Build reports or slides from validated artifacts instead of restarting from raw data.
10. End with a handoff summary containing outputs, assumptions, limitations, and next skill.

## Planning Requirements

`plan.md` should include:

- Objective and decision context.
- Audience and expected output format.
- Dataset path, file type, size estimate, and detected strategy.
- Open questions and working assumptions.
- Preprocessing rules and what will not be changed.
- Analysis tasks, statistics, charts, and deliverables.
- Risks, limitations, and validation checkpoints.

## Artifact Discipline

Prefer stable JSON or Markdown artifacts over hidden notebook state. If code is needed in the host environment, keep scripts scoped to one task: one profiling pass, one cleaning step, one chart, one table, or one finding group.