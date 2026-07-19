# AI Citation Patterns

Heuristic patterns for AI visibility work, not a sourced live benchmark; validate with dated observations before making platform-specific claims.

## AI System Comparison

| Factor | Google AI Overviews | ChatGPT | Perplexity | Claude |
|--------|---------------------|---------|------------|--------|
| **Freshness bias** | High | Medium | Very high | N/A (training data) |
| **Authority weight** | Very high | High | High | High |
| **Structure importance** | High | Medium | Very high | Medium |
| **Citation count** | 3-8 | 1-6 | 5-10 | N/A |
| **Quotable focus** | High | Medium | Very high | High |
| **Domain trust** | Very high | High | Medium | High |
| **Factual density** | High | High | Very high | Very high |

> ⚠ The **Claude** column reflects the no-web-search baseline (answers from training data — hence the N/A freshness/citation cells). With web search **on**, Claude retrieves live via **Brave** (see the per-engine table below), and freshness/citations then apply.

---

## Per-Engine Source Selection (9 engines)

Each engine runs its own index and ranking logic. Below: what backend it uses and the strongest reported citation lever for each. Figures are **as reported** by the cited studies (Princeton GEO study KDD 2024; SE Ranking 129K-domain study; ZipTie 400K-page analysis) — validate before quoting as fact.

| Engine | Search backend | Strongest lever (as reported) | What to do |
|--------|----------------|-------------------------------|------------|
| **Google AI Overviews** | Google index | Schema + cited sources; ~15% overlap with traditional Top 10 | Article/FAQ/HowTo schema (reported 30-40% lift), named citations (reported +132%), authoritative tone (reported +89%), E-E-A-T |
| **ChatGPT** | Bing-based index | Content-answer fit (reported ~55% of citation likelihood) | Write the way ChatGPT answers; update monthly (reported 3.2x for <30-day content); domain authority |
| **Perplexity** | Own index + Google, multi-pass rerank | FAQ schema + public PDFs + publishing velocity | FAQPage JSON-LD, host PDFs publicly, allow PerplexityBot, self-contained paragraphs |
| **Claude** | Brave Search | Factual density; very selective, low citation rate | Verify Brave visibility; allow ClaudeBot/anthropic-ai; specific numbers + named, dated sources |
| **Copilot** | Bing index | Microsoft-ecosystem signals + page speed | Bing Webmaster Tools, IndexNow, sub-2s load, LinkedIn + GitHub presence, explicit entity definitions |
| **Gemini / AI Overviews** | Google index | Same E-E-A-T + schema base as AI Overviews | Allow Google-Extended; Knowledge Graph entry (accurate Wikipedia helps); structured, extractable answers |
| **Grok** | X / real-time web | Recency + on-platform (X) signals | Maintain credible X presence; timely, dated takes; see [Grokipedia tactics](../../../../references/platforms/grokipedia.md) and [X surface](../../../../references/platforms/x.md) |
| **Brave** | Own independent index | Independent crawl — separate from Google/Bing | Confirm you appear at search.brave.com; gates Claude citations too |
| **Bing** | Bing index | Index inclusion + IndexNow freshness | Submit to Bing Webmaster Tools; IndexNow; gates both Copilot and ChatGPT |

**robots.txt user agents to allow:** `GPTBot`, `ChatGPT-User` (ChatGPT), `PerplexityBot` (Perplexity), `ClaudeBot` + `anthropic-ai` (Claude), `Google-Extended` (Gemini + AI Overviews), `Bingbot` (Copilot + Bing). `CCBot` (Common Crawl) is training-only — safe to block without losing search citations.

**Where to start:** Google AI Overviews first (reaches ~45% of Google searches), then ChatGPT, then Perplexity; Copilot/Gemini/Grok/Brave/Bing as audience skews enterprise, Google, X, or developer/analyst. Fundamentals — schema, cited sources, clean headings — help on all nine.

---

## 2026 platform updates (dated & sourced)

The per-engine table above covers the durable levers; this section adds the 2026 platform shifts that move tactics, each with a verification date and primary source. These surfaces change quarterly — re-verify before quoting.

**Google AI Overviews / AI Mode** — *verified 2026-07-16 (blog.google, Search Engine Land, Pew Research).* Gemini 3 became the default for AI Overviews + AI Mode (Jan 2026), and citation-vs-Top-10 overlap collapsed from ~76% to ~38% — passage quality now outweighs raw ranking for inclusion. The **2026-05-27** update added **Preferred Sources** (users ~2× as likely to click; prompt loyal audiences to add you as one), **"Subscribed" labels**, expanded **"Highly Cited" badges**, and **in-text citation links** beside the specific claim they support (rewards claim-level citability). Optimal extracted-passage length **134–167 words**; ~44% of citations come from the first 30% of the page body. Google **does not use `llms.txt`** (Illyes; developer guidance Jun 2026).

**ChatGPT / ChatGPT Search** — *verified 2026-07-16 (developers.openai.com/api/docs/bots; Search Engine Land Jul 2026).* Reverse-engineering surfaces **multi-backend retrieval** (a `result_source` field shows "Labrador" ~88% of primary sources, plus Bright Data / Oxylabs / SERP), and retrieval is **non-deterministic** — ~12% of repeated prompts switch backends, so audit citations across repeated runs, not a single snapshot. **Thinking mode is a distinct citation surface**: only ~26% domain overlap with Instant, citation rate 50%→68%, shifting away from Reddit/UGC toward official docs and gov/academic. **Crawler split (official):** `OAI-SearchBot` controls Search visibility; `GPTBot` is training-only; `ChatGPT-User` is user-triggered — allow OAI-SearchBot even if you block GPTBot. **Referring-domain count gatekeeps retrieval** (sites with 32K+ referring domains ~3.5× more likely cited). The Mar 2026 model transition cut cited web sources ~20%.

**Perplexity** — *verified 2026-07-16 (docs.perplexity.ai; Perplexity blog; Jun 2026 funding coverage).* Now on the in-house **Sonar** model family (external GPT/Claude routing deprecated Feb 2025). Two crawlers: `PerplexityBot` (index) and `Perplexity-User` (live per-query fetch that generally **ignores robots.txt** since it's user-initiated — allowlist by UA *and* published IP ranges in your WAF, the common accidental-block point). **Comet publisher rev-share:** citations pay out (80/20) **even without click-through**, so being cited has direct monetization for qualifying publishers. Levers: a direct answer in the first **40–60 words** of each section, **atomic paragraphs** that parse without surrounding context, and **freshness** (updates boost citation ~37% in the first 48h).

**Claude** — *verified 2026-07-16 (platform.claude.com web-search docs).* Anthropic formalized a **three-crawler framework** (Feb 2026): `ClaudeBot` (training) · `Claude-SearchBot` (search index) · `Claude-User` (live user-directed fetch) — block training while staying citable by allowing the latter two; no stable IP ranges are published, so robots.txt UA rules are the only control. `web_search_20260209` added **dynamic filtering** — Claude code-filters raw results before they enter context, so cleanly-structured pages are likelier to survive the pass. `llms.txt` consumption by Claude is **unconfirmed** — treat as unproven.

**Gemini app** — *verified 2026-07-16 (ai.google.dev/gemini-api/docs/google-search).* Cites via **Grounding with Google Search** — same stack as AI Overviews, different surface. **No separate Gemini crawler exists:** Googlebot indexability *is* Gemini visibility (Google-Extended only controls training opt-out), so optimizing for Gemini = Google Search technical health + the AI Overviews playbook. Citation share skews hard to platforms (Reddit ~27.5%, YouTube ~13.7%, Wikipedia ~12.7% — ~54% combined). Google **explicitly ignores `llms.txt`**.

**On `llms.txt` across the board:** cheap agent-readiness hygiene, **not** a rankings or citation lever on any platform — Google states its systems ignore it, there is no confirmed third-party consumption by Claude, and server-log studies show ~97% of `llms.txt` files receive zero AI requests.

---

## Universal Citation Factors

**Content quality**: Factual accuracy, clear unambiguous language, comprehensive coverage, up-to-date information.

**Structure**: Scannable format (headings, lists, tables), logical organization, short paragraphs, clear visual hierarchy.

**Authority**: Domain credibility, author credentials, source citations in content, E-E-A-T signals.

**Relevance**: Precise match to query intent, topic focus, depth of coverage on specific topic.

---

## Optimal Content Structures for Citation

### Definition Blocks
```
**[Term]** is [clear category] that [primary function], [key characteristic].
```
Why: Standalone, complete, unambiguous, proper scope.

### Statistic Blocks
```
According to [Source], [specific statistic] as of [timeframe].
```
Why: Specific, attributed, recent, verifiable.

### Q&A Pairs
Use exact question as H2/H3, answer in 40-60 words, then optional supporting detail. Matches AI query patterns directly.

### Comparison Tables
Structured rows with specific values, clear labels, and "Best for" recommendations. AI systems parse and cite these readily.

### Step-by-Step Processes
Numbered lists with bold action headers and brief explanations. Clear process, actionable, logical sequence.

### Key Insight Callouts
`> **Key insight**: [Memorable, quotable statement with attribution]`
Visually distinct, authoritative, quotable.

---

## Citation Likelihood Factors

**High likelihood**: Authority domain, updated within 12 months, clear standalone statements, specific statistics with dates, structured with headings/lists/tables, comprehensive coverage, author credentials visible, consensus with other sources.

**Low likelihood**: Unknown domain, 3+ years old without updates, vague statements, no sources cited, walls of text, thin coverage, promotional tone, factual inconsistencies.

---

## Optimization by Query Type

| Query Type | AI Priorities | Optimal Structure |
|-----------|--------------|-------------------|
| **Informational** ("What is", "How does") | Clear definitions, comprehensive explanations, statistics | Definition first, "why it matters", how it works, examples |
| **Comparison** ("X vs Y", "Best") | Comparison tables, pros/cons, recommendations | Table upfront, feature-by-feature, "Choose X if..." |
| **How-To** ("How to", "Steps to") | Numbered steps, prerequisites, time estimates | Prerequisites, numbered steps, troubleshooting |
| **Statistical** ("How much", "Statistics about") | Specific numbers with sources, recent data, trends | Lead with key stat, source attribution, context, related data |

---

## Optimization Checklist

Content ready for AI citation should have:
- [ ] At least 3 clear, quotable definitions
- [ ] 5+ specific statistics with sources and dates
- [ ] Q&A format sections covering top queries
- [ ] Comparison tables where relevant
- [ ] Numbered lists for processes
- [ ] Updated within 12 months
- [ ] Author credentials visible
- [ ] External citations to authoritative sources
- [ ] Clear H2/H3 headings
- [ ] Short paragraphs (2-4 sentences)
- [ ] No promotional language

---

*The dated "2026 platform updates" section is contributed and maintained — with the full per-platform detail and source list — at [abouchard11/ai-citation-patterns](https://github.com/abouchard11/ai-citation-patterns).*
