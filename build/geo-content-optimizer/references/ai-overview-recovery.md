# AI Overview Recovery Playbook

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md). Use when AI Overviews (Google) or similar AI-generated answer boxes are diverting traffic away from your pages — specifically for the recovery workflow, not generic GEO optimization.

---

## Symptom profile

This playbook fits when:

- Organic CTR on ≥5 queries dropped 20-60% in a 2-4 week window
- SERP screenshots show AI Overview block above organic results for those queries
- Impressions stayed flat or rose; clicks fell
- Your page still ranks top-3 organically but gets fewer clicks

This is different from a general ranking drop (which would show position change, not just CTR change).

## Phase 1 — Measure the damage

### 1.1 Identify affected queries

From `~~search console`:

```
Filter: last 28 days vs previous 28 days
Export: queries with CTR change < -20% AND impressions change > -10%
```

Flag the top 20 queries by click loss — these are the AI Overview recovery targets.

### 1.2 Confirm AI Overview is the cause

For each target query:

1. Run it in Google (incognito, location-matched)
2. Screenshot the SERP
3. Record:
   - Is an AI Overview present? Y/N
   - Does it cite your page? Y/N
   - If cited, is your page in the visible citation carousel or hidden?
   - How many organic results above the fold now vs before?

### 1.3 Segment the 20 queries

| Segment | Pattern | Recovery strategy |
|---------|---------|-------------------|
| A | AI Overview present + cites you | Low priority — you're still visible; optimize for carousel ordering |
| B | AI Overview present + does NOT cite you | HIGH priority — you lost both ranking surface AND citation |
| C | AI Overview present + cites competitor | HIGH priority — identify what competitor has that you don't |
| D | No AI Overview, but intent shifted | Different problem — re-check ranking, not AI |

Focus effort on segments B and C.

## Phase 2 — Diagnose why AI Overview skipped (or unchose) you

For each Segment B / C query, run a structural diagnostic:

### 2.1 Answerability check

AI Overview favors content that directly answers the query in ≤60 words. Check your page:

- [ ] Does the first 100 words contain a direct answer to the query (not just the keyword)?
- [ ] Is there a single `<h2>` or `<h3>` that rephrases the query as a statement?
- [ ] Are there 3-5 ordered points, clearly numbered, answering sub-questions?
- [ ] Is the answer quote-able — a single standalone sentence that makes sense out of context?

### 2.2 Freshness check

AI Overview heavily favors recent content:

- [ ] Last-updated date visible in HTML and rendered (not hidden)
- [ ] Published / updated within last 12 months
- [ ] Statistics / data points with year qualifier: "In 2026, X..."
- [ ] Reference links to other pages updated in last 12 months

### 2.3 Authority check (Ept / E-E-A-T)

- [ ] Author bio visible with credentials
- [ ] Author's Knowledge Graph entity exists (search their name + your org)
- [ ] External citations from authoritative sources (.edu, .gov, major news, peer-reviewed)
- [ ] Your brand entity recognized by Wikidata / Google Knowledge Graph (see `entity-optimizer`)

### 2.4 Structural / crawlability check

- [ ] Content rendered in initial HTML (not post-hydration)
- [ ] `robots.txt` allows `GoogleBot` AND `Google-Extended` (unless training opt-out is policy)
- [ ] Schema present: `Article` or `HowTo` or `FAQPage` depending on intent
- [ ] No paywall blocking first answer

## Phase 3 — Rewrite targets

For each affected page, apply:

### 3.1 Answer-first rewrite

Move the direct answer into the first paragraph. Use this template:

```
**[Direct query-answering sentence in ≤30 words.]**

[2-sentence expansion with key specifics — numbers, proper nouns, date.]

[Transition: "Here's what this means / why it matters / how to apply it:"]

[Jump-linked TOC or 3-5 H2s covering sub-questions.]
```

### 3.2 Quotable-chunk insertion

Add 2-3 standalone sentences (within paragraphs or as blockquotes) that make sense without context:

- Factual: "As of 2026, 64% of small businesses use at least one AI-powered SEO tool."
- Definitional: "Technical SEO is the practice of optimizing crawlability, indexability, and rendering for search engines."
- Prescriptive: "For teams under 20 people, pick a PM tool priced under $10 per seat per month."

Each should:
- Be a single sentence (≤30 words)
- Contain a specific number, year, or qualified claim
- Be flanked by attribution ("According to X, ..." or "Our 2026 survey found ...")

### 3.3 FAQ appendix

Append a `<h2>FAQ</h2>` with 6-10 questions matching known SERP-PAA patterns for your target keyword. Each answer 40-60 words. Mark up with `FAQPage` schema.

### 3.4 Citation-bait — structured data

Add one of:

- `Dataset` schema for unique survey / benchmark data you published
- `HowTo` schema for step-by-step guides
- `Review` schema with `aggregateRating` for product review pages
- `Article` schema with `author` linked to a Knowledge Graph entity

## Phase 4 — Monitor recovery (T+7, T+14, T+28)

Re-run Phase 1.2 for each target query:

- T+7: have SERP AI Overviews changed at all? (often no — early)
- T+14: have 2-3 of your pages started appearing in citations?
- T+28: has CTR recovered to >50% of pre-drop baseline?

If no recovery at T+28:

- Segment C (competitor cited): run `competitor-analysis` on the cited page — what does it have that yours doesn't? Usually it's original data, a clearer direct answer, or stronger author entity.
- Segment B (no citation): likely the query is being answered from training data (not retrieval). Shift strategy to long-tail + adjacent queries where retrieval is still the dominant mechanism.

## Red flags — stop and re-scope

- If AI Overviews are affecting queries you *shouldn't* be targeting (e.g., your home page ranks for a generic query with no commercial intent) — that traffic wasn't valuable; don't chase it.
- If AI Overviews cite 3+ competitors uniformly and you're DR <30 — entity authority may be the blocker, not content. Run `entity-optimizer` first.
- If AI Overviews appear for branded queries about your product but cite competitor comparisons — this is a knowledge-graph gap; hand to `entity-optimizer` with priority flag.

## Handoff

- **Status**: DONE | DONE_WITH_CONCERNS (for in-progress recovery)
- **Objective**: "AI Overview recovery plan for [N] affected queries"
- **Key Findings / Output**: segmentation table, per-query rewrite priority, estimated recovery timeline
- **Evidence**: GSC export ref, SERP screenshots per query, pre/post CTR deltas
- **Open Loops**: monitoring windows (T+7, T+14, T+28), pages pending rewrite, entity gaps requiring `entity-optimizer`
- **Recommended Next Skill**:
  - `content-refresher` for the rewrite execution
  - `entity-optimizer` if segment C pattern is "competitor cited due to Knowledge Graph presence"
  - `rank-tracker` to watch post-rewrite CTR recovery

## See also

- [entity-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md) — fix the entity gap if competitors cite because they have Knowledge Graph presence you lack
- [content-refresher](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/content-refresher/SKILL.md) — execute the rewrites identified in Phase 3
- [technical-seo-checker LLM crawler guide](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/references/llm-crawler-handling.md) — ensure AI engines can actually see your content
