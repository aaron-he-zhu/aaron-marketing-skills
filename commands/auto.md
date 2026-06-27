---
name: auto
description: "Run the SEO/GEO pack-local Aaron workflow implied by a natural-language goal, at the smallest safe depth. Add --deep for exhaustive, maximum-rigor, or stress-test runs."
argument-hint: "<natural-language-goal> [--deep]"
parameters:
  - name: goal
    type: string
    required: true
    description: "Any SEO/GEO goal, URL, domain, topic, draft, or question"
  - name: deep
    type: boolean
    required: false
    description: "Run maximum-depth, exhaustive, phase-gated orchestration"
---

# Auto Command

Run the SEO/GEO pack-local Aaron workflow implied by a natural-language goal, at the smallest safe depth. Add `--deep` for an exhaustive, phase-gated, maximum-rigor run.

## Route

- resolver across all 20 skills, expressed through the four mode commands: research, create, audit, track

## Rules

- Follow the Product API Contract in `references/aaron-product-api-contract.md`; use `evals/product-api-scenarios.md` as the scenario library. Natural-language auto-invocation is host-dependent unless `/aaron-seo-geo:auto` is explicit; clearly non-SEO/GEO work stops with a pack-boundary note.
- **Memory-management exemption**: memory-management lifecycle operations (query, archive, restore, purge) operate on user-owned project memory regardless of topical scope and are NOT subject to the pack-boundary check; safety is enforced by per-operation user confirmation.
- Algorithm: parse the goal -> assign the closest scenario family -> attach risk gates -> choose the smallest mode command (research / create / audit / track) or chain that completes the outcome -> ask only for blocking inputs -> continue to the natural stopping point.
- Ambiguity rule: with an object (URL/domain/topic/draft) but no clear goal, run lightweight triage and pick the safest useful starting chain; with no actionable object and no outcome, ask one concise blocking question.
- Default to a single mode command when it completes the goal; otherwise chain research -> create -> audit -> track as needed.
- **`--deep`** (absorbs the former `/aaron-seo-geo:max`): run only when the user explicitly asks for maximum-depth, exhaustive, or stress-test work. First output a phase plan, success criteria, evidence inventory, risk gates, permission checkpoints, and stop condition. Phase order: preflight -> research -> audit (tech / quality / visibility / authority) -> optional memory -> create (brief / write / series) -> publish gate (`/aaron-seo-geo:create --publish`) -> track. Do not enable `--deep` for ordinary broad work.
- Apply scenario-library risk gates: publish readiness, YMYL, schema factuality, batch scale, external side effects, memory/entity writes, reputation ethics, GEO visibility claims, insufficient data, technical indexation.
- Respect specialist boundaries: batch content stays chunked; audit/publish readiness require full veto-aware evidence; GEO visibility cannot promise citations; memory cleanup stays with memory-management; canonical entity writes stay with entity-optimizer.
- Do not route repository maintenance, version sync, release, permission, or governance requests through `/aaron-seo-geo:auto`; they fall outside the pack-local SEO/GEO workflow.
- Words such as apply, commit, release, publish, or fix are not automatic permission grants. Publish-package and readiness work routes through `/aaron-seo-geo:create --publish`; actual CMS/external publication, commits, releases, and repo edits require explicit confirmation.
- If input starts with old `/seo:*`, preserve arguments and return one copyable replacement: `audit-page -> /aaron-seo-geo:audit`, `audit-domain -> /aaron-seo-geo:audit --authority`, `check-technical -> /aaron-seo-geo:audit --tech`, `generate-schema -> /aaron-seo-geo:create --schema`, `keyword-research -> /aaron-seo-geo:research`, `optimize-meta -> /aaron-seo-geo:create --meta`, `report -> /aaron-seo-geo:track --report`, `setup-alert -> /aaron-seo-geo:track --alert`, `write-content -> /aaron-seo-geo:create`.
- Return an execution summary by default: completed steps, evidence used, blockers or gate stops, artifacts produced, assumptions, and next safe action. Diagnostic route trace appears only when explicitly requested.
- Never write files unless explicitly requested and supported by the runtime.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
