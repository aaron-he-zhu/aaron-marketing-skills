---
description: "Run an influencer (IMPACT) workflow: audience & creator discovery, campaign planning, briefs, outreach, amplification, and ROI measurement. Not sure? Use /aaron-marketing:auto."
argument-hint: "<goal-or-brand> [--phase discover|plan|activate|measure]"
---

# Impact Command

Run the influencer-marketing (IMPACT) lifecycle: understand the audience, find and score creators, plan and brief the campaign, run outreach, amplify and convert, then track ROI. Skills score on the [C³ framework](../references/c3-benchmark.md).

## Route

Infer the IMPACT phase from the goal (or honor `--phase`) and route to the matching skill:

- **Discover** — audience-mapper (audience/niche modes), trend-spotter, influencer-discovery, fit-scorer (C³ ACE); creator-registry dedupes candidates against the roster
- **Plan** — competitor-tracker, campaign-planner, brief-generator, budget-optimizer
- **Activate** — outreach-manager, content-reviewer (C³ ART gate), contract-helper, content-amplifier (paid whitelisting / UGC repurpose modes) — consult creator-registry's dossier (`memory/creators/<handle-slug>.md`: contact path, last agreed rate, exclusivity, compliance history) before outreach or contracting
- **Measure** — landing-optimizer (post-click), performance-analyzer, roi-calculator (CVI), report-generator

## Rules

- Start where the goal sits in the funnel; do not force the full four-phase chain when the user only needs one stage.
- `content-reviewer` is the pre-publish gate: any creator content goes through its C³ **ART** check (FTC disclosure T1, claim integrity T2) before it ships.
- `creator-registry` is the roster SSOT: only it writes canonical records under `memory/creators/`; other skills submit updates to `memory/creators/candidates.md`, and it should be run when 3+ candidate updates accumulate for one creator or a campaign cycle closes.
- Score creators/content/campaigns on C³ (ACE/ART/ROI → CVI); label every metric Measured / User-provided / Estimated; never fabricate reach or rates.
- Tier 1 by default — works from user-provided data; connectors only automate retrieval. Compliance checks are guidance, not legal advice.
- Follow each skill's Next Best Skill handoff; stop at the documented termination rules rather than auto-chaining the whole discipline.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
