# Content-Atom Extraction Method

A method for breaking one piece of UGC into reusable "content atoms" — the smallest standalone units worth repurposing. The agent does this by reading the pasted transcript, caption, or review text. No audio/video processing, no libraries: you read the words and extract.

> Method only. Do NOT install or call whisper, mediapipe, pandas, or any package. If the user has a video, ask them to paste the transcript or captions and work from that text.

**Source identity boundary**: before extraction, bind the transient source text to exactly three persistent fields: stable opaque `creator_ref`, exact frozen `approved_asset_ref`, and an opaque authorized `source_ref`. Never persist a raw handle, creator name, profile/content URL, provider ID, or a raw URL disguised as `source_ref`. If any of the three refs is missing, return `NEEDS_INPUT` and do not save or hand off atom records.

## 1. The 7 Atom Tiers

Read the source text and pull every standalone unit that fits one of these tiers. Tag each atom with a timestamp (or text position if no timecodes) and candidate formats. The tier does not itself rank, score, approve, or choose a paid/hero placement.

| Tier | What it is | Looks like | Suggested platforms |
|------|-----------|-----------|--------------------|
| `narrative_arc` | The whole before→after journey in one line | "I had X problem, tried this, now Y" | YouTube, landing page hero, case study |
| `quote` | A short, quotable line in the creator's voice | "This is the only one that actually worked." | quote card, website testimonial, ad headline, email |
| `controversial_take` | A claim that splits opinion or pushes back on common advice | "Everyone says X — they're wrong." | X, Reddit, TikTok hook, ad hook |
| `data_point` | A specific number, result, or measurable claim | "Saved 4 hours a week." "Down 12 lbs in 6 weeks." | ad copy, landing-page stat, email subject |
| `story` | A self-contained anecdote with a beginning and payoff | "So last Tuesday I…" | Reels, TikTok, Stories, blog snippet |
| `framework` | A named or numbered method the creator teaches | "My 3-step morning routine" | carousel, LinkedIn, YouTube Short, blog |
| `prediction` | A forward-looking claim about a trend or outcome | "By next year everyone will…" | X, LinkedIn, thought-leadership post |

### Per-atom record

```markdown
- atom_id: A-001
  tier: quote
  text: "This is the only one that actually worked."
  timestamp: 00:00:18   # or char-offset / "para 2" if no timecodes
  creator_ref: creator-opaque-ref
  approved_asset_ref: frozen-approved-asset-ref
  source_ref: opaque-authorized-source-ref
  candidate_formats: [quote card, website testimonial, ad headline]
  selection_rule_ref: NEEDS_INPUT
  selection_score: null
  score_state: NOT_SCORED
```

## 2. Selection Rule — No Built-In Score

This reference supplies no default “virality” weights, bonuses, cutoff, ranking, or placement priority. Extracting an atom is not evidence that it should receive paid spend or a hero placement.

Before assigning any numeric score, rank, keep/drop decision, or placement, require one of:

- a user-approved rule that explicitly defines criteria, weights, scale, cutoff, intended use, and approval ref; or
- a source-dated rule whose evidence ref, population/context, date, and intended use are compatible with this campaign.

If neither exists, set `selection_rule_ref: NEEDS_INPUT`, `selection_score: null`, and `score_state: NOT_SCORED/NEEDS_INPUT`. Preserve the extracted atoms without ranking them and do not automatically select anything for paid, hero, or another destination.

If a qualifying rule exists, copy its criteria and weights exactly, show the calculation inputs and result, and record `selection_rule_ref`. Do not add an atom-type bonus, content bonus, or unstated tie-breaker.

## 3. Near-Duplicate Evidence (No Default Threshold)

Before you publish a batch, you may calculate lexical similarity as descriptive evidence. Similarity alone does not authorize dropping or suppressing an atom.

**Jaccard similarity** = (words shared by both) / (all distinct words across both). Compute it by hand on lowercased word sets, dropping punctuation and common stop-words (the, a, is, and, to, of, it, this).

```
J(A, B) = |words(A) ∩ words(B)| / |words(A) ∪ words(B)|
```

Require a user-approved or source-dated compatible `duplicate_rule_ref` before applying a threshold or keep/drop decision. Without it, report the calculated similarity and `duplicate_state: NOT_DECIDED/NEEDS_INPUT`; do not assume a cutoff.

Check in two places:

1. **Within the current batch** — compare atoms only when requested. Apply a flag/keep/drop action only under the cited `duplicate_rule_ref`; a selection score is unavailable unless its separate rule passed.
2. **Against recent memory** — read authorized atom records from the user-supplied/source-dated lookback window. Apply an already-used flag or skip action only under the cited `duplicate_rule_ref`.

```markdown
- atom_id: A-007
  creator_ref: creator-opaque-ref
  approved_asset_ref: frozen-approved-asset-ref
  source_ref: opaque-authorized-source-ref
  text: "It's the only one that actually worked for me."
  jaccard_similarity: 0.71
  duplicate_rule_ref: NEEDS_INPUT
  duplicate_state: NOT_DECIDED/NEEDS_INPUT
  decision: none
```

Worked calculation: `"this is the only one that actually worked"` vs `"the only one that actually worked for me"` — after the declared tokenization/stop-word treatment, shared = 5 and union = 7, so **J = 5/7 ≈ 0.71**. With no approved `duplicate_rule_ref`, report only that calculated value; do not flag or drop either atom.
