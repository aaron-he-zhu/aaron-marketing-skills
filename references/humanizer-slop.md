# Humanizer / AI-Slop Reference

Named anti-patterns that make writing read as machine-generated, each with a one-line tell, a point deduction, and a terse before/after rewrite. This is a structural complement to the banned-word list: words are one tell among many, but most slop is *sentence shape* (inflation, fake-depth phrases, vague attribution), which a vocabulary list cannot catch.

Ported from the 24 "signs of AI writing" patterns (Wikipedia-derived, via Eric Osiu's humanizer panel) and an AI-writing-detection word list (Corey Haines, citing Grammarly 2025 and others). No proven ranking effect is claimed — this is a *quality/voice* gate, not an SEO tactic.

## Banned vocabulary — single source of truth

The canonical banned-word and banned-phrase list lives in [skill-contract.md → Output Voice](skill-contract.md#output-voice). Use that first. Do not duplicate it here.

This file **extends** that list. The additions below are slop words/phrases not already in Output Voice — treat the Output Voice list as the SSOT and this as an appendix:

| Added word/phrase | Why it's slop |
|---|---|
| utilize, whilst, endeavour | inflated forms of "use", "while", "try" |
| underscore (verb), garner, bolster | thesaurus verbs for "show", "get", "strengthen" |
| transformative, groundbreaking, innovative, commendable, meticulous | empty praise adjectives |
| testament, profound, nestled, renowned | promotional puffery |
| "shed light on", "pave the way for", "a plethora of" | academic AI tells |
| "prior to / subsequent to", "in light of", "in terms of", "the fact that" | wordy connectors → "before/after", "because", "for", "that" |
| "that being said", "with that in mind", "at its core", "this begs the question" | filler transitions |

## The slop patterns

Tell = the one thing to grep for. Fix = rewrite with a concrete noun, number, or simple verb.

| # | Pattern | Tell | -pts | Before → After |
|---|---|---|---|---|
| 1 | Significance inflation | "stands as", "marks a pivotal moment", "underscores its importance" | 10 | "a pivotal moment in digital marketing" → "launched its first programmatic campaign in 2019" |
| 2 | Undue-notability claims | media-mention list with no substance | 5 | "featured in Forbes, Inc, and Entrepreneur" → "in a 2024 Forbes interview, argued most brand-awareness spend is wasted" |
| 3 | Shallow -ing analysis | trailing "highlighting / underscoring / ensuring / reflecting" | 8 | "grew 40% YoY, showcasing the team's commitment" → "grew 40% YoY, mostly from one referral loop built in Q2" |
| 4 | Promotional language | "boasts a", "rich" (figurative), "must-visit", "in the heart of" | 8 | "boasts a vibrant team with a commitment to results" → "45 employees; revenue grew 32%" |
| 5 | Vague attribution | "experts argue", "industry reports", "several sources" | 8 | "experts believe AI will transform marketing" → "a 2024 Gartner survey: 67% of CMOs plan more AI spend" |
| 6 | Formulaic "challenges/future" section | "Despite these challenges, continues to…", "Future Outlook" | 10 | "despite challenges, continues to thrive" → "churn hit 8% in Q3; they hired a retention team in October" |
| 7 | Negative parallelism | "not just X, it's Y", "not only…but" | 5 | "not just content, it's a lasting relationship" → "good content gets replies" |
| 8 | Copula avoidance | "serves as", "represents", "features", "offers" for plain "is/has" | 5 | "serves as a valuable resource" → "is a resource; 12K weekly opens" |
| 9 | Rule-of-three filler | forced triples of adjectives, nouns, or clauses | 8 | "keynotes, panels, and networking opportunities" → "talks and panels, plus time to network" |
| 10 | Elegant variation | synonym-cycling one subject (CEO → business leader → company head) | 5 | three labels for one person → name them once |
| 11 | False ranges | "from X to Y" where X/Y aren't on a scale | 5 | "from content to SEO to paid media, the field shifts" → "content, SEO, and paid media are all changing" |
| 12 | Em-dash-as-drama | >1 em dash per ~200 words; dash where a comma/period works | 5 | "this—unlike old methods—allows…" → "this, unlike old methods, allows…" |
| 13 | Sycophancy | "Great question!", "You're absolutely right!" | 8 | delete; answer the question |
| 14 | Collaborative artifacts | "I hope this helps", "Certainly!", "Would you like…" | 10 | delete; it's a deliverable, not a chat turn |
| 15 | Cutoff disclaimers | "As of [date]", "based on available information" | 10 | delete or cite the actual source + date |
| 16 | Excessive hedging | "could potentially possibly", "might have some effect" | 8 | "could potentially have some impact" → "works — here's the data" |
| 17 | Generic positive conclusion | "the future looks bright", "exciting times ahead" | 10 | "the future looks bright for AI" → "they plan to double AI budget next quarter" |
| 18 | Filler phrases | "in order to", "due to the fact that", "at this point in time" | 5 | → "to", "because", "now" |

Style tells worth a quick scan (-2 to -5 each): title-case headings, emoji on headings/bullets, curly quotes, bold on every key term, lists where every item is a bold-header-colon.

## Scoring

Start at 100; subtract per occurrence. Same pattern stacks up to 2× its base penalty. Bands: 90–100 clean · 70–89 minor tells, quick fix · 50–69 obvious AI, real rewrite · <50 full rewrite. The score is advisory — flag the specific lines, don't just report a number.

## What good looks like

Opinions (not just reporting) · varied sentence rhythm · concrete names/dates/numbers · simple verbs (is, has, does) · honest uncertainty · first person where it fits.

## How the four content skills use this

| Skill | Use | Weight |
|---|---|---|
| `content-writer` | pre-publish self-check before handing off a draft | gate before DONE |
| `geo-content-optimizer` | same self-check after AI-readability edits | gate before DONE |
| `content-quality-auditor` | maps to CORE-EEAT **Experience** | **SOFT penalty** — never a veto; vetoes stay T04/C01/R10 |
| `content-reviewer` | maps to the **ART** (content quality) dimension of C³ | **NON-veto** — ART vetoes stay T1/T2 only |

Run it as the *last* pass on a draft. It flags voice; it does not check facts, structure, or schema — those are owned by the auditor gates.
