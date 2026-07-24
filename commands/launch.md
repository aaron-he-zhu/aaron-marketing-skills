---
description: "Run a product-launch (RAMP) workflow: positioning and launch tiering, window/early-access design, message house and asset kits, the launch-readiness gate with a T-1 go/no-go, launch-day execution, and the post-launch prove loop. Not sure? Use /aaron-marketing:auto."
argument-hint: "<launch goal or product> [--phase research|assemble|mobilize|prove]"
---

# Launch Command

Run the product-launch lifecycle along the **RAMP loop** (Research → Assemble → Mobilize → Prove). Skills operate from the user's **own plan, project memory, and keyless public telemetry** — keyed launch platforms and commercial ASO suites are never required. The auditor selects one typed lifecycle read: `preflight`, `execution`, or `outcome`; it links but never averages results across time horizons.

## Route

Infer the RAMP-loop phase from the goal (or honor `--phase`) and route to the matching skill:

- **Research** — positioning-mapper (Dunford-style canvas: alternatives, unique attributes, beachhead), launch-tier-planner (tier/type + risk register + kill criteria), launch-window-planner (dates, competitor calendar, embargo windows), early-access-designer (waitlist→GA stage ladder + graduation criteria); record decided dates/stages via launch-registry (`memory/launch-registry/`)
- **Assemble** — message-house-builder (tagline/pillars/PR-FAQ spine; unresolved claims become `operation: propose` events), launch-asset-packager (tier-scoped manifest: press kit, store listing specs, technical go-live items), pricing-packaging-planner (tiers, launch offers, guarantees), sales-enablement-kit (battle cards, talk track — sales-led only); reuse landing-optimizer for the launch page UX and technical-seo-checker for the go-live pass
- **Mobilize** — launch-readiness-auditor (typed preflight profile + T-1 go/no-go; R1 judged against launch projection, A1 against claims projection), launch-day-conductor (hour-blocked runbook, requires SHIP plus separate execution approval), community-launch-runner (platform-rule-bound submissions), press-media-relations (media/embargo drafts; outreach remains separate)
- **Prove** — launch-monitor (T-0→T+30 telemetry via `hn.py`/`producthunt.py`/`appstore.py`/`gdelt.py`, spike-vs-sustain), launch-feedback-synthesizer (theme triage + compliant social proof), launch-retro-analyzer (D1/W1/M1 actual-vs-target + 5-Whys), momentum-planner (anti second-week cliff, next moment); reuse roi-calculator / report-generator / performance-analyzer

## Rules

- `launch-readiness-auditor` runs one lifecycle profile at a time: preflight, execution, or outcome. Preflight verifies relevant R1/A1/M1/P1 controls before execution; it never blends future operation/outcomes into readiness.
- For `launch_go_no_go`, bind each preflight veto to its own accepted evidence: `RAMP-R1` uses the accepted launch projection plus a direct access/eligibility check; `RAMP-A1` uses accepted claims/canon projections plus rendered assets; `RAMP-M1` uses dated platform-rule, embargo, and launch-plan evidence; `RAMP-P1` uses verified events/UTMs plus own-data destination checks. A proposal, plan, or manifest alone proves none of these; missing evidence is `NEEDS_INPUT/UNDECIDED/NOT_SCORED`.
- `memory/events/launches.ndjson` is the launch truth history. Mobilize and other producer skills submit idempotent `operation: propose` events, including at T-0; `launch-registry` resolves them in offset order and alone performs canonical transitions. Missing stage evidence is Unknown/NEEDS_INPUT, never pass-by-default.
- Keyless Tier 1 — score from the user's own plan/analytics plus the keyless/free-key connectors (`hn.py`, `producthunt.py`, `appstore.py`, `gdelt.py`); keyed launch platforms are opt-in Tier-2/3 MCP only. Platform folklore (posting hours, karma ladders, vote-velocity targets) is Estimated context with named sources, never a scored rule.
- Only `launch-readiness-auditor` scores a typed RAMP profile. Profiles are not averaged or compared as one construct. Launch-stacking/audience fatigue remains a non-veto operating finding.
- Label every metric Measured / User-provided / Estimated; attribution truth comes from the user's own analytics (UTM set), never platform self-reported numbers. No incentivized store reviews — incentives only where a platform explicitly allows them, with disclosure.
- **Scope edge — creators and distribution**: a launch that runs through creators hands the creator lane to [campaign-planner](../influencer/target/campaign-planner/SKILL.md) ("launch a product with creators" starts there); pitch/follow-up mechanics for media and hunters run on [outreach-manager](../influencer/activate/outreach-manager/SKILL.md); content repurposing and the paid-amplification calendar belong to [content-amplifier](../influencer/activate/content-amplifier/SKILL.md); the launch page UX is [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md); waitlist capture-flow specs stay with [list-growth-designer](../email/setup/list-growth-designer/SKILL.md) and opt-in records with [consent-registry](../protocol/consent-registry/SKILL.md).

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
