# Content-Atom Extraction Method

A method for breaking one piece of UGC into reusable "content atoms" — the smallest standalone units worth repurposing. The agent does this by reading the pasted transcript, caption, or review text. No audio/video processing, no libraries: you read the words and extract.

> Method only. Do NOT install or call whisper, mediapipe, pandas, or any package. If the user has a video, ask them to paste the transcript or captions and work from that text.

## 1. The 7 Atom Tiers

Read the source text and pull every standalone unit that fits one of these tiers. One source usually yields 5–15 atoms. Tag each atom with a timestamp (or text position if no timecodes) and the platforms it suits best.

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
  source_asset: UGC-001 (@creator1, TikTok)
  suggested_platforms: [quote card, website testimonial, ad headline]
  virality_score: 0.71
```

## 2. Virality Heuristic

Score each atom 0–1 so you repurpose the strongest first. Rate three traits on a 0–1 scale by reading the text, then weight them:

```
base = (Novelty × 0.4) + (Controversy × 0.3) + (Utility × 0.3)
```

- **Novelty (0.4)** — how fresh or surprising is the claim? Seen-it-everywhere = low; genuinely new angle = high.
- **Controversy (0.3)** — does it provoke a reaction or take a side? Neutral = low; "you've been doing it wrong" = high.
- **Utility (0.3)** — can a viewer act on it? Vague vibe = low; concrete step or result = high.

### Bonuses (additive, then cap the total at 1.0)

Atom-type bonus:

| Atom tier | Bonus |
|-----------|-------|
| `controversial_take` | +0.10 |
| `data_point` | +0.08 |
| `framework` | +0.06 |
| `quote` | +0.04 |
| others | 0 |

Content bonus (each applies once, stack them):

- +0.05 if it names a specific number or timeframe.
- +0.05 if it directly addresses the viewer ("you", "your").
- +0.05 if it carries clear emotion (relief, frustration, surprise).

```
virality_score = min(1.0, base + atom_type_bonus + content_bonuses)
```

Sort atoms by `virality_score` descending; repurpose the top of the list into paid and hero placements first.

## 3. Near-Duplicate Flag (Jaccard ~0.70)

Before you publish a batch, flag atoms that say almost the same thing so you don't ship five versions of one line.

**Jaccard similarity** = (words shared by both) / (all distinct words across both). Compute it by hand on lowercased word sets, dropping punctuation and common stop-words (the, a, is, and, to, of, it, this).

```
J(A, B) = |words(A) ∩ words(B)| / |words(A) ∪ words(B)|
```

Flag a pair as a near-duplicate when **J ≥ 0.70**.

Check in two places:

1. **Within the current batch** — compare every new atom against the others in this run. Keep the higher-virality one; mark the other `dup_of: A-00X`.
2. **Against recent memory** — read atom records saved in `memory/influencer/content-amplifier/` dated within the last 30 days and compare new atoms against those. If J ≥ 0.70 against a recent atom, flag it as already-used and either skip it or note it as a deliberate refresh.

```markdown
- atom_id: A-007
  text: "It's the only one that actually worked for me."
  near_duplicate: true
  dup_of: A-001            # J = 0.78, within-batch
  decision: drop (lower virality)
```

Worked example: `"this is the only one that actually worked"` vs `"the only one that actually worked for me"` — after stop-word removal the sets are {only, one, that, actually, worked} (5) and {only, one, that, actually, worked, for, me} (7); shared = 5, union = 7, so **J = 5/7 ≈ 0.71** — just over the 0.70 line, so flag it.
