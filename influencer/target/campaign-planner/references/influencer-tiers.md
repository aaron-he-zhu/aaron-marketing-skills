# Influencer Band and Partner-Model Taxonomy

Use this file to record the taxonomy chosen for a campaign. It supplies no
universal follower ranges, rate card, performance ordering, engagement norm, or
recommended creator mix. `fit-scorer` evaluates evidence for creators;
`budget-optimizer` models costs only from user-provided or compatible
source-dated anchors.

## Partner-Model Declaration

Choose or define a model only when the user or an approved plan supplies its
objective and commercial terms. The labels below organize inputs; they do not
imply performance.

| Declared model | Record before use |
|----------------|-------------------|
| Influencer partnership | objective, deliverables, compensation basis, rights, disclosure, duration |
| Affiliate relationship | attribution rule/window, commission basis, eligible outcomes, rights/disclosure |
| Creator program | program objective, contribution/deliverable rules, compensation/benefits, rights, duration |
| Hybrid | exact components, deduplication/attribution rule, compensation and rights for each component |

If the model or terms are not supplied, return `NEEDS_INPUT`; do not select a
model from assumed industry practice.

## Follower-Band Declaration

Follower-band labels vary by platform, market, provider, and date. Copy the
user's taxonomy or a compatible source-dated taxonomy into the plan:

| Band label | Follower range | Platform/market | Source ref | Observed/published date | Decision use |
|------------|----------------|-----------------|------------|-------------------------|--------------|
| [label] | [min-max] | [scope] | [user/source ref] | [date] | [declared planning use] |

Without a compatible row, use `band: Unknown` and request the taxonomy. Never
map a creator into nano/micro/mid/macro from repository defaults.

## Evidence Required for Mix Decisions

Do not infer that one band is cheaper, more authentic, more trusted, more
engaging, or higher-performing than another. For each proposed mix decision,
record:

- the campaign objective and decision rule;
- complete current creator evidence from typed Fit;
- compatible user/source-dated rate or cost evidence;
- comparable platform, market, niche, window, and metric definitions;
- rights, deliverable, and capacity constraints.

Missing evidence remains `NEEDS_INPUT`. A follower count alone never clears
authenticity, audience fit, brand safety, cost, or performance.
