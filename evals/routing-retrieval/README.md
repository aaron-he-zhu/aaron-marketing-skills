---
status: active
generated: false
sources:
  - evals/README.md
  - docs/context-engineering.md
  - references/wiki/patterns/focused-retrieval.md
stale_after: 2027-03-04
---

# Routing / retrieval suite

Deterministic, credential-free suite. It does **not** add a Skill.

**Guidance:** focused ≤3 modules beat exhaustive dumps. An intent should
resolve to at most three Skill slugs. Name/description-only retrieval is
the CI bar; a light body-aware heuristic is compared so a body dump cannot
silently become the default.

## Why this is not the 734-case corpus

`evals/<skill>/cases.md` remains the authored semantic corpus
(606 + 88 + 40 = 734). This directory is a separate maintainer suite:
intents → expected Skill sets. `scripts/check-evals.py` does not ingest
these cases and must not be `--update`d because of them.

## Run

```bash
python3 scripts/check-routing-retrieval.py
```

CI path: `evals/deterministic-suites.json` id `routing-retrieval`
(`run-behavior-evals.py`). Nightly and S2/S3 PR validation execute that
manifest. The suite is also documented here for a maintainer-scheduled
rerun without a model adapter.

## What it compares

| Mode | Inputs | Role |
|---|---|---|
| `description` | Skill `name` + `description` (quoted triggers + token overlap) | CI gate |
| `body-aware` | description mode plus `when_to_use`, headings, and a short body excerpt | Comparison only; must not regress the description gate |

Neither mode loads `references/wiki/`. Retrieval stays on the 120 Skill
packages.

## Case shape

See `cases.json`. `expected_skills` length must be 1–3. `k` is 3.
`must_not_primary` names a common sibling that must not rank first.
