# Subject Line & Preheader Specs

Render limits and variant-labeling for `email-creative-builder`, so the subjects it drafts carry cleanly into [send-experiment-designer](../../../deliver/send-experiment-designer/SKILL.md). Numbers are practical inbox-render limits, not hard protocol limits — treat them as guidance labeled Estimated.

## Render limits (characters before truncation)

| Surface | Desktop | Mobile | Guidance |
|---|---|---|---|
| **Subject line** | ~60 | ~30–40 | Front-load the promise in the first ~30 chars; mobile truncates hardest |
| **Preheader** | ~90–110 | ~40–50 | Extends (never repeats) the subject; set it explicitly or the client pulls body text |
| **From name** | ~20 | ~20 | Recognizable sender; consistency drives opens |

## Variant set (draft 3–5, one angle each)

Label each variant so it maps to a test cell:

| Angle | Pattern | Example shape |
|---|---|---|
| Curiosity | open loop, withhold | "The one thing we changed…" |
| Benefit | lead with outcome | "Cut your setup time in half" |
| Offer | lead with the deal (promo mode) | "24 hours: 20% off everything" |
| Personalization | genuine, verifiable token | "{first_name}, your {plan} renews soon" |
| Question | provoke a mental yes | "Still exporting reports by hand?" |

## Rules

- **One variable per test cell** — if testing subjects, hold preheader/creative/send-time constant (isolation is enforced by [send-experiment-designer](../../../deliver/send-experiment-designer/SKILL.md)).
- No spam-trigger patterns: no ALL-CAPS, no `!!!`, no misleading "RE:"/"FWD:" fakery, no false scarcity. These also fail the [deliverability-qa](../../../setup/deliverability-qa/SKILL.md) spam-content scan.
- Emoji: at most one, only if on-brand; never in cold-outbound (B2B) subjects.
- Label the output so each subject+preheader pair carries a stable variant id (`SUBJ-A`, `SUBJ-B`, …) into the test.
