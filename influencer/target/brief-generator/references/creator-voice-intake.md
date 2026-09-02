# Creator Voice Intake

Capture how the creator (or the brand's founder spokesperson) actually talks before you write the brief. A brief that respects the real voice gets content that needs fewer revisions. Drop the filled-out block into the brief's "Why You" and "Creative Direction" sections, and hand it to `creator-content-auditor` so reviewers check submitted content against the captured voice, not their own taste.

**Persistence boundary**: saved intake blocks and handoffs identify the speaker and provenance only with `creator_ref`, `brand_ref` when applicable, and opaque `voice_source_ref` values. Never persist a raw name, handle, profile/content/source URL, email, phone, provider ID, or hidden identity mapping. Raw locators and any permitted display values may be resolved only transiently while inspecting the authorized source or rendering the final creator-facing brief inside its independently authorized dispatch.

Adapted from an external founder-voice intake template (competitive analysis).

## Intake Block

Fill this with the creator's real patterns. Specific and honest beats polished. This is not a persona — it is how they already communicate.

### Reference-Safe Speaker Context

```
Creator: [creator_ref]
Brand (for founder spokesperson): [brand_ref or not applicable]
Voice evidence: [voice_source_ref values]
What they're known for: [niche, format, audience]
```

### Core Beliefs (Things They'd Actually Say)

Real opinions, not mission statements. Include the contrarian or counterintuitive ones — that is where their voice is strongest.

```text
- [Paraphrased belief pattern] — source: [voice_source_ref]
- [Paraphrased counter-position pattern] — source: [voice_source_ref]
- [Paraphrased changed-mind pattern] — source: [voice_source_ref]
```

Keep verbatim source excerpts transient. Persist only the derived, non-identifying pattern plus its opaque provenance ref unless a separate authorized artifact explicitly permits the quoted text.

### GOOD vs BAD Sentence Patterns

Show the difference in plain examples. Short, present tense, active voice on the GOOD side.

```
GOOD: "I cut my supplement stack to three things. Sleep got better."
BAD:  "I strategically optimized my wellness routine for enhanced outcomes."
```

```
GOOD: "This actually works. Here's the one step people skip."
BAD:  "I'm so excited to share this game-changing product with you all!"
```

Add additional **derived pattern** pairs from the authorized `voice_source_ref`; do not save raw post URLs/handles or unattributed copied excerpts.

### Topic Authority Tied to Proof

What can this person credibly speak on, and what is the proof? No proof, no authority claim.

```text
- [Topic]: [evidence-backed experience/result summary] — [voice_source_ref]
- [Topic]: [evidence-backed experience/result summary] — [voice_source_ref]
```

### Signature Moves / Tics (pick 3-5)

The repeatable things that make their content recognizable. Examples to prompt with:

```
1. [Opens with a blunt one-line claim, then proves it]
2. [Uses exact numbers, never "a lot" or "huge"]
3. [Films in the same spot / same framing every time]
4. [Signs off with a recurring catchphrase]
5. [Reads on-screen captions out loud in the first 2 seconds]
```

## What to Avoid

```
- [Phrasing that feels off-brand for them]
- [A tone that doesn't fit, e.g. corporate hype]
- [A topic they would not weigh in on]
```

## Handoff

When the voice intake is filled out, pass forward only `creator_ref`, applicable `brand_ref`, `voice_source_ref`, and the derived non-identifying patterns with the reference-safe brief. `creator-content-auditor` resolves the authorized voice evidence when needed and judges whether submitted content stays consistent with the captured patterns and proof-backed topics—flagging drift instead of imposing a reviewer's preference. Never put raw names, handles, URLs, contact values, or source locators in the handoff.
