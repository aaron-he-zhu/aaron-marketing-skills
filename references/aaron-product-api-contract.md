# Aaron Product API Contract
`/aaron-seo-geo:auto` is the SEO/GEO pack-local Product API entry; its `--deep` flag (`/aaron-seo-geo:auto --deep`) is the maximum-depth mode. `/aaron` is an optional host alias for `/aaron-seo-geo:auto`, not a physical command. Cross-pack capability selection belongs to the future `slash-aaron` product repo; this pack must decline clearly non-SEO/GEO work instead of routing it into a fake SEO/GEO workflow. The five commands (`auto`, `research`, `create`, `audit`, `track`) remain the execution surface; scenario detail belongs in `evals/product-api-scenarios.md`.
## `/aaron-seo-geo:auto`
- Accept natural-language SEO/GEO tasks when invoked directly or by verified host routing, then identify the scenario family and risk gates.
- Execute the end-to-end command chain (`research`, `create`, `audit`, `track`) implied by the user goal, using the smallest depth that can produce the requested outcome.
- Ask only blocking questions required for that chain, then continue until the natural stopping point is reached.
- If the user gives an object but no clear outcome, run a lightweight triage and choose the safest useful starting chain; if the user gives neither object nor outcome, ask one concise blocking question.
- Stop at evidence gaps, permission/write gates, external side effects, publish/readiness gates, oversized batches, repo governance, or memory/entity writes; do not treat ordinary action words as approval.
- Do not redirect to `/aaron-seo-geo:auto --deep` unless the user explicitly asks for maximum-depth, exhaustive, or stress-test mode; decline clearly non-SEO/GEO work with a pack-boundary note unless a verified slash-aaron product registry provides another capability route.
- Do not publish, write, commit, release, or claim readiness without the relevant specialist gate and explicit permission.
## `/aaron-seo-geo:auto --deep`
- Run only when the user explicitly asks for maximum-depth, exhaustive, or stress-test work.
- Infer depth without parameters, then start with phase plan, evidence inventory, risk gates, permission checkpoints, and stop condition.
- Coordinate the specialist commands (`research`, `create`, `audit`, `track`) without bypassing their gates.
- Do not publish, write, commit, release, or claim ready by summary alone.
## Risk Gate Set
The canonical gates are `publish_readiness`, `ymyl`, `schema_factuality`, `batch_scale`, `external_side_effect`, `memory_or_entity_write`, `reputation_ethics`, `geo_visibility_claim`, `data_insufficient`, and `technical_indexation`.
New high-frequency or high-risk behavior must land as a scenario first, with a real `target_skill`, expected route, blocking inputs, and failure modes, before `/aaron-seo-geo:auto` (including its `--deep` mode) changes.
