# AI Overview Recovery Playbook

Referenced from [SKILL.md](../SKILL.md). Use when AI Overviews are diverting traffic away from your pages.

---

## Symptom profile

- Organic CTR on >=5 queries dropped 20-60% in a 2-4 week window
- SERP screenshots show AI Overview block above organic results
- Impressions stayed flat or rose; clicks fell
- Page still ranks top-3 organically but gets fewer clicks

## Phase 1 — Measure the damage

### 1.1 Identify affected queries
From `~~search console`: filter last 28d vs previous 28d, export queries with CTR change < -20% AND impressions change > -10%. Flag top 20 queries by click loss.

### 1.2 Confirm AI Overview is the cause
For each target query (incognito, location-matched): Is AI Overview present? Does it cite your page? Visible or hidden citation? How many organic results above fold?

### 1.3 Segment the 20 queries

| Segment | Pattern | Recovery strategy |
|---------|---------|-------------------|
| A | AI Overview + cites you | Low priority — optimize carousel ordering |
| B | AI Overview + does NOT cite you | HIGH — lost ranking surface AND citation |
| C | AI Overview + cites competitor | HIGH — identify what competitor has |
| D | No AI Overview, intent shifted | Different problem — re-check ranking |

Focus on segments B and C.

## Phase 2 — Diagnose why AI Overview skipped you

### 2.1 Answerability check
- [ ] First 100 words contain a direct answer (not just the keyword)?
- [ ] Single `<h2>`/`<h3>` rephrases the query as a statement?
- [ ] 3-5 ordered points answering sub-questions?
- [ ] Answer is quote-able — standalone sentence that makes sense out of context?

### 2.2 Freshness check
- [ ] Last-updated date visible in HTML and rendered
- [ ] Published/updated within last 12 months
- [ ] Statistics with year qualifier: "In 2026, X..."
- [ ] Reference links to pages updated in last 12 months

### 2.3 Authority check (E-E-A-T)
- [ ] Author bio visible with credentials
- [ ] Author's Knowledge Graph entity exists
- [ ] External citations from authoritative sources
- [ ] Brand entity recognized by Wikidata / Google KG (see `entity-optimizer`)

### 2.4 Structural / crawlability check
- [ ] Content rendered in initial HTML (not post-hydration)
- [ ] `robots.txt` allows `Googlebot`; do not require `Google-Extended` unless the site intentionally allows Google AI training/product use
- [ ] Schema present: `Article` / `HowTo` / `FAQPage`
- [ ] No paywall blocking first answer

## Phase 3 — Rewrite targets

### 3.1 Answer-first rewrite template
```
**[Direct query-answering sentence in <=30 words.]**
[2-sentence expansion with key specifics — numbers, proper nouns, date.]
[Transition sentence.]
[Jump-linked TOC or 3-5 H2s covering sub-questions.]
```

### 3.2 Quotable-chunk insertion
Add 2-3 standalone sentences (<=30 words each) containing a specific number/year/qualified claim, flanked by attribution.

### 3.3 FAQ appendix
Append `<h2>FAQ</h2>` with 6-10 PAA-matching questions. Each answer 40-60 words. Mark up with `FAQPage` schema.

### 3.4 Structured data that supports citation
Add markup that genuinely matches the page: `Dataset` (real survey/benchmark data you publish),
`HowTo` (actual step-by-step), `Article` with author linked to a KG entity. Only add `Review` /
`aggregateRating` when the page has real first-party reviews — self-assigned ratings to win a rich
result are structured-data spam under Google's review policy and risk a manual action. Schema must
describe what is on the page, never decorate it with claims that aren't.

## Phase 4 — Monitor recovery (T+7, T+14, T+28)

- T+7: SERP AI Overviews changed? (often no)
- T+14: 2-3 pages appearing in citations?
- T+28: CTR recovered to >50% of pre-drop baseline?

If no recovery at T+28:
- Segment C: run `competitor-analysis` on cited page
- Segment B: query likely answered from training data; shift to long-tail + adjacent queries

## Red flags — stop and re-scope

- AI Overviews affecting queries you shouldn't target — that traffic wasn't valuable
- AI Overviews cite 3+ competitors and you're DR <30 — run `entity-optimizer` first
- AI Overviews on branded queries cite competitor comparisons — knowledge-graph gap; hand to `entity-optimizer`

## Handoff

- **Status**: DONE | DONE_WITH_CONCERNS
- **Objective**: "AI Overview recovery plan for [N] affected queries"
- **Key Findings / Output**: segmentation table, per-query rewrite priority, estimated recovery timeline
- **Evidence**: GSC export ref, SERP screenshots, pre/post CTR deltas
- **Open Loops**: monitoring windows (T+7/14/28), pages pending rewrite, entity gaps
- **Recommended Next Skill**: `content-writer`, `entity-optimizer`, `rank-tracker`

## See also

- [entity-optimizer](../../../../protocol/entity-optimizer/SKILL.md)
- [content-writer](../../content-writer/SKILL.md)
- [technical-seo-checker LLM crawler guide](../../../optimize/technical-seo-checker/references/llm-crawler-handling.md)
