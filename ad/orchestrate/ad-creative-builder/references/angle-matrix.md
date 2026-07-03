# Angle Matrix and Message-Match Map

How to build distinct angles, generate hooks per angle, and prove each unit matches the destination page.

## Angles (pick 3+, keep them distinct)

| Angle | What it leads with | Hook starters |
|-------|--------------------|---------------|
| **Benefit** | the outcome the buyer gets | "Get [outcome] in [timeframe]" / "[Outcome] without [pain]" |
| **Pain** | the problem they want gone | "Tired of [pain]?" / "Stop [bad outcome]" |
| **Proof** | evidence / numbers / names | "[N] teams switched to…" / "Rated [X] by [source]" |
| **Urgency / scarcity** | a real deadline or limit | "Ends [date]" / "Last [N] spots" — only if true |
| **Objection** | the reason they hesitate | "No [common blocker]. No [other]." |
| **Category re-frame** | a fresh way to see the choice | "Not [old category]. [New category]." |

Two angles that produce near-identical copy count as one — vary the lead, not just the wording.

## Hook quality

- Lead with the buyer's outcome or problem, not your brand name (brand goes in the path/business-name field).
- One idea per hook. If it needs a comma-spliced second clause, it is two hooks.
- Specifics beat adjectives: "cuts onboarding to 2 days" over "incredibly fast onboarding".

## Message-match map (required output)

For every unit, record the destination claim it echoes. If a unit has no matching destination claim, either cut it or flag the page gap.

```
| Unit (headline/desc)        | Angle   | Destination claim it echoes            | Match? |
|-----------------------------|---------|----------------------------------------|--------|
| "Cut onboarding to 2 days"  | Benefit | Hero: "Onboard in 2 days"              | yes    |
| "Free for 30 days"          | Benefit | Pricing: "30-day free trial"           | yes    |
| "Rated #1 by G2"            | Proof   | (no such claim on page)                | NO →flag|
```

- `Match? = yes` → keep. `NO` → cut the unit or send the page gap to `landing-optimizer`.
- A mismatch is both a Quality-Score relevance loss and a ROAS **O1** (claim integrity) risk.

## Claim and policy pre-check (feeds ROAS O1 / O2)

- **O1 (claim integrity)**: superlatives ("best", "#1", "guaranteed"), numbers, health/finance/earnings claims → need an on-page or provided source. No source → `[needs source]`, do not ship as fact.
- **O2 (policy)**: prohibited/restricted categories, competitor trademarks in copy, before/after or sensitive-attribute targeting language → flag for the auditor; these cause disapprovals or account risk.

Flag risks in the handoff; never silently delete a user-provided claim — tell them why it is risky.
