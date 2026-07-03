---
description: "Run the marketing (SEO/GEO + influencer/IMPACT + paid/ROAS) pack-local Aaron workflow implied by a natural-language goal, at the smallest safe depth. Add --deep for exhaustive, maximum-rigor, or stress-test runs."
argument-hint: "<natural-language-goal> [--deep]"
---

# Auto Command

Run the marketing pack-local Aaron workflow (SEO/GEO + influencer/IMPACT + paid/ROAS + email/SEND) implied by a natural-language goal, at the smallest safe depth — the natural-language front door to `/aaron-marketing:seo-geo`, `/aaron-marketing:impact`, `/aaron-marketing:paid`, and `/aaron-marketing:email`. Add `--deep` for an exhaustive, phase-gated, maximum-rigor run.

## Route

- resolver across all 69 skills (16 SEO/GEO + 16 influencer + 16 paid + 16 email + 5 protocol): SEO/GEO through `/aaron-marketing:seo-geo` (--mode research|create|audit|track), influencer through `/aaron-marketing:impact`, paid through `/aaron-marketing:paid`, email through `/aaron-marketing:email` (--phase setup|engage|nurture|deliver); or describe any goal here and it routes to the right skill

## Rules

- Follow the routing contract in [references/aaron-product-api-contract.md](../references/aaron-product-api-contract.md); use [references/auto-routing-scenarios.md](../references/auto-routing-scenarios.md) as the scenario library (both under the plugin root — resolve against `${CLAUDE_PLUGIN_ROOT}` when installed). Natural-language auto-invocation is host-dependent unless `/aaron-marketing:auto` is explicit. For influencer goals, route to the matching IMPACT skill by name or `/aaron-marketing:impact` phase; for paid-ads goals, route to the matching ROAS-phase skill by name or `/aaron-marketing:paid` phase; for email goals, route to the matching SEND-phase skill by name or `/aaron-marketing:email` phase (`/aaron-marketing:seo-geo` covers SEO/GEO only). Only clearly non-marketing work stops with a pack-boundary note — influencer, paid, and email goals are in scope and are routed, never declined.
- **Memory-management exemption**: memory-management lifecycle operations (query, archive, restore, purge) operate on user-owned project memory regardless of topical scope and are NOT subject to the pack-boundary check; safety is enforced by per-operation user confirmation.
- Algorithm: parse the goal -> assign the closest scenario family -> attach risk gates -> choose the smallest `/aaron-marketing:seo-geo` mode (research / create / audit / track), `/aaron-marketing:impact` phase, `/aaron-marketing:paid` phase, `/aaron-marketing:email` phase, or chain that completes the outcome -> ask only for blocking inputs -> continue to the natural stopping point.
- Ambiguity rule: with an object (URL/domain/topic/draft) but no clear goal, run lightweight triage and pick the safest useful starting chain; with no actionable object and no outcome, ask one concise blocking question.
- Default to a single seo-geo mode / impact phase / paid phase / email phase when it completes the goal; otherwise chain (for SEO/GEO: research -> create -> audit -> track) as needed.
- **`--deep`** (absorbs the former `/aaron-marketing:max`): run only when the user explicitly asks for maximum-depth, exhaustive, or stress-test work. First output a phase plan, success criteria, evidence inventory, risk gates, permission checkpoints, and stop condition. Phase order for SEO/GEO goals: preflight -> research -> audit (tech / quality / visibility / authority) -> optional memory -> create (brief / write / series) -> publish gate (`/aaron-marketing:seo-geo --mode create --publish`) -> track; for influencer/paid/email goals, coordinate the `/aaron-marketing:impact` / `/aaron-marketing:paid` / `/aaron-marketing:email` phases without bypassing their gates. Do not enable `--deep` for ordinary broad work.
- Apply scenario-library risk gates: publish readiness, YMYL, schema factuality, batch scale, external side effects, memory/entity writes, reputation ethics, GEO visibility claims, insufficient data, technical indexation.
- Respect specialist boundaries: batch content stays chunked; audit/publish readiness require full veto-aware evidence; GEO visibility cannot promise citations; memory cleanup stays with memory-management; canonical entity writes stay with entity-optimizer.
- Do not route repository maintenance, version sync, release, permission, or governance requests through `/aaron-marketing:auto`; they fall outside the pack-local marketing workflow.
- Words such as apply, commit, release, publish, or fix are not automatic permission grants. Publish-package and readiness work routes through `/aaron-marketing:seo-geo --mode create --publish`; actual CMS/external publication, commits, releases, and repo edits require explicit confirmation.
- If input starts with old `/seo:*`, preserve arguments and return one copyable replacement: `audit-page -> /aaron-marketing:seo-geo --mode audit`, `audit-domain -> /aaron-marketing:seo-geo --mode audit --authority`, `check-technical -> /aaron-marketing:seo-geo --mode audit --tech`, `generate-schema -> /aaron-marketing:seo-geo --mode create --schema`, `keyword-research -> /aaron-marketing:seo-geo --mode research`, `optimize-meta -> /aaron-marketing:seo-geo --mode create --meta`, `report -> /aaron-marketing:seo-geo --mode track --report`, `setup-alert -> /aaron-marketing:seo-geo --mode track --alert`, `write-content -> /aaron-marketing:seo-geo --mode create`. Old `/aaron-seo-geo:*` names map to `/aaron-marketing:seo-geo --mode <name>` for research/create/audit/track (flags preserved); other names map 1:1 to `/aaron-marketing:*`.
- Return an execution summary by default: completed steps, evidence used, blockers or gate stops, artifacts produced, assumptions, and next safe action. Diagnostic route trace appears only when explicitly requested.
- Never write files unless explicitly requested and supported by the runtime.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
