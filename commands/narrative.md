---
description: "Run a brand-narrative & messaging (TALE) workflow: trace the current message and positioning truth, architect the durable message house/voice/story canon, land it consistently across every surface, and evaluate resonance with tests and drift monitoring. Not sure? Use /aaron-marketing:auto."
argument-hint: "<narrative goal or brand> [--phase trace|architect|land|evaluate]"
---

# Narrative Command

Run the brand-narrative & messaging lifecycle along the **TALE loop** (Trace → Architect → Land → Evaluate). Skills operate from the user's **own data, project memory, and keyless public surfaces** — no paid messaging tool is required, and this discipline ships **no new connector**. The auditor runs `truth`, `system`, and `effectiveness` profiles separately; full mode returns three linked results and no overall score. Narrative is the **strategy layer** every channel discipline expresses — what the brand says, above the channels that say it.

## Route

Infer the TALE-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Trace** — narrative-baseline-mapper (what every surface says today + the gap vs intent), category-narrative-mapper (category stories + competitive narrative teardown via `firecrawl.py`/`tavily.py`/`wayback.py`, proxy-labeled), audience-belief-mapper (beliefs/objections/switching forces; reuses [audience-mapper](../influencer/scout/audience-mapper/SKILL.md) for personas), positioning-truth-tracer (reconciles the positioning canvas against shippable reality + the claims ledger — the upstream of `T1`); positioning input is reused from [positioning-mapper](../launch/research/positioning-mapper/SKILL.md)
- **Architect** — strategic-narrative-designer (old-world→new-game→promised-land arc), message-system-architect (the durable brand message house that seeds the canon; the per-launch [message-house-builder](../launch/assemble/message-house-builder/SKILL.md) is reused and derives from it — the upstream of `A1`), brand-language-codifier (voice + tone + lexicon + naming tax; the brand-level source the channel-registry `voice-dossier.md` points up to), story-bank-builder (reusable story units tagged to claim IDs); record durable canon via narrative-registry (`memory/narrative-registry/`)
- **Land** — narrative-cascade-planner (per-surface message-match specs + handoff briefs to each discipline's creative builder — the upstream of `L1`), pitch-narrative-builder (sales + fundraising deck narrative; distinct from launch-window [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md)), narrative-enablement-kit (elevator ladder + spokesperson Q&A + boilerplate/bio pack), proof-point-packager (ledger-approved proofs → reusable proof modules placed where each claim is made)
- **Evaluate** — narrative-quality-auditor (separate truth/system/effectiveness profiles), message-test-designer (preregistered comprehension/panel design), narrative-resonance-monitor (proxy-labeled resonance evidence), narrative-drift-monitor (version-linked drift)

## Rules

- `narrative-quality-auditor` runs independent `truth`, `system`, and `effectiveness` profiles. Full review links three results and aggregates release language conservatively, never scores one blended total. Narrative change frequency is a drift signal, not an automatic veto.
- A pre-publish readiness question runs the `system` profile now and requires a compatible current `truth` result. If that truth result is unavailable, mark the readiness prerequisite Unknown and the overall release decision `UNDECIDED` while still rendering the system profile from its own evidence. If the scorer/runtime is unavailable, still collect the system observations but return `score_state: NOT_SCORED` / `UNDECIDED`. Run `effectiveness` separately only when requested or when the surface asserts an effectiveness claim.
- `memory/events/narrative.ndjson` is the canon history. Narrative skills submit complete-canon `operation: propose` events; `narrative-registry` alone accepts/rejects or lands an atomic version. `canon.md` and `versions.md` are generated views, and missing canon is Unknown/NEEDS_INPUT rather than pass-by-default.
- Keyless Tier 1 — read from own surfaces, the positioning canvas, the claims ledger, and the reused keyless connectors; closed platforms (X/IG/TikTok/LinkedIn) and review sites (G2/Capterra/Trustpilot) enter as user exports (Measured, as-of) or proxy reads that are always labeled proxy, never Measured.
- This discipline never adjudicates a claim: unverified or comparative claims are marked `[needs source]` and submitted as authorized claims proposals for [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md). Every data point is labeled Measured / User-provided / Calculated / Estimated / Proxy.
- **Scope edge — narrative vs launch vs social vs channels**: durable brand positioning, message house, voice canon, and boilerplate are this discipline; a *single launch's* positioning canvas and PR-FAQ start at [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) / [message-house-builder](../launch/assemble/message-house-builder/SKILL.md) (which read this canon when it exists); *per-platform* voice adaptation is the [channel-registry](../protocol/channel-registry/SKILL.md) `voice-dossier.md` (it points up to this canon, never redefines it); machine-facing entity facts are [entity-registry](../protocol/entity-registry/SKILL.md) (its descriptions derive from this canon); finished surface copy stays with each discipline's creative builder (content-writer / ad-creative-builder / email-creative-builder / social-creative-builder).

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
