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

The platform-specific guidance below was re-verified on **2026-07-28** against first-party documentation. Product behavior and crawler policies change; re-check the linked sources before treating these notes as permanent.

- **Google AI Overviews / AI Mode:** Google's **2026-05-27** Search update expanded **Preferred Sources** into AI Overviews and AI Mode and added **Highly Cited** labels and more in-text links to original sources. For publishers, the durable action is to make original claims easy to identify and support, then encourage loyal readers to select the site as a Preferred Source. [Google announcement](https://blog.google/products-and-platforms/products/search/original-high-quality-content-search/)
- **ChatGPT Search:** OpenAI documents separate controls for `OAI-SearchBot` (search visibility), `GPTBot` (potential model training), and `ChatGPT-User` (user-triggered visits). A site can allow `OAI-SearchBot` while blocking `GPTBot`; crawler IP ranges are published alongside the documentation. [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots)
- **Perplexity:** `PerplexityBot` supports search indexing, while `Perplexity-User` performs user-requested fetches and generally ignores `robots.txt`. Perplexity publishes separate IP ranges for both, so WAF rules should be checked in addition to `robots.txt`. [Perplexity crawler documentation](https://docs.perplexity.ai/docs/resources/perplexity-crawlers)
- **Claude:** Anthropic separates `ClaudeBot` (model development), `Claude-SearchBot` (search indexing), and `Claude-User` (user-directed retrieval), with independent `robots.txt` controls. Anthropic's `web_search_20260209` and later tool versions can dynamically filter search results before they enter the context window. [Anthropic crawler guidance](https://support.anthropic.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) · [Claude web-search documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- **Gemini / Google Search grounding:** The Gemini API's `google_search` tool handles search, result processing, and citation automatically and returns grounding metadata for source attribution. Separately, `Google-Extended` controls whether crawled content may be used for Gemini model development and grounding; Google states that it does **not** affect inclusion or ranking in Google Search. [Gemini grounding documentation](https://ai.google.dev/gemini-api/docs/google-search) · [Google crawler documentation](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers)

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
