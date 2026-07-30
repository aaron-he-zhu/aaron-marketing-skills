# AI Citation Patterns

This is an evidence-bounded operating reference, not a ranking-factor list or a
live benchmark. Platform behavior changes, eligibility never guarantees
selection, and controls for search visibility, model training, and
user-triggered retrieval are not interchangeable. Re-check the linked
first-party documentation and record dated observations before making a
platform-specific claim.

## Documented discovery and retrieval controls

Re-verified on **2026-07-30**. The table includes only behavior that the named
provider documents publicly; it does not infer undisclosed ranking weights or
search backends.

| Surface | Documented route and control | Site-owner action |
|---------|------------------------------|-------------------|
| **Google AI Overviews / AI Mode** | Supporting links come from Google Search. A page must be indexed and eligible to appear with a snippet; there is no additional technical requirement or special schema for these AI features. `Googlebot` and Search preview controls govern Search. `Google-Extended` is a separate control for Gemini model development and grounding in certain non-Search systems; it does not affect Google Search inclusion or ranking. | Apply normal technical SEO and people-first content guidance. Keep important content crawlable and textual, ensure structured data matches visible content, and use `nosnippet`, `data-nosnippet`, `max-snippet`, or `noindex` when appropriate. Do not treat `llms.txt`, content “chunking,” or special AI markup as Google Search requirements. [AI features guidance](https://developers.google.com/search/docs/appearance/ai-features) · [2026 optimization guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) · [Google-Extended](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers#google-extended) |
| **ChatGPT Search** | `OAI-SearchBot` controls eligibility for ChatGPT search results. `GPTBot` is for content that may be used to improve foundation models. `ChatGPT-User` performs certain user-triggered visits and does not control Search inclusion. OpenAI publishes separate IP ranges for these agents. | Allow `OAI-SearchBot` and its published IP ranges when Search visibility is desired. Set `GPTBot` independently according to training policy; do not substitute `ChatGPT-User` for the Search crawler. [OpenAI crawler documentation](https://developers.openai.com/api/docs/bots) |
| **Perplexity** | `PerplexityBot` surfaces and links websites in search results. `Perplexity-User` performs user-requested fetches and generally ignores `robots.txt`. Perplexity publishes separate IP ranges and WAF guidance for both. | Configure `robots.txt` for `PerplexityBot`, then verify CDN/WAF rules against the published user agents and current IP endpoints. Treat `Perplexity-User` as a separate user-directed retrieval path. [Perplexity crawler documentation](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) |
| **Claude** | `Claude-SearchBot` supports search indexing, `Claude-User` supports user-directed retrieval, and `ClaudeBot` is for potential model-development use. Anthropic documents `robots.txt` controls for all three. | Configure each agent for its actual purpose; allowing `ClaudeBot` alone is not a search-visibility control. Verify current agents and source IPs in Anthropic's guidance. [Anthropic crawler guidance](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) |
| **Gemini API with Google Search grounding** | The `google_search` tool handles searching, result processing, and citation. Current API responses expose inline citation `annotations` plus `google_search_call` and `google_search_result` steps. This developer API behavior is distinct from eligibility in Google Search AI features. | Preserve and render the returned citation annotations when building a grounded application. Do not present Gemini API response fields as Google Search ranking controls. [Gemini grounding documentation](https://ai.google.dev/gemini-api/docs/google-search) |
| **Bing-backed Copilot Studio public-web grounding** | Microsoft's documented Copilot Studio flow uses Bing Custom Search for configured public-web knowledge sources, then performs grounding and provenance checks. Microsoft recommends sitemaps, `Bingbot` crawlability, and IndexNow or URL/content submission for Bing index freshness. This documentation is scoped to Copilot Studio, not every consumer Copilot surface. | Keep Bing discovery and indexation healthy, and label conclusions with the exact Copilot product tested. Do not generalize Copilot Studio architecture to all Microsoft assistants. [Microsoft Copilot Studio guidance](https://learn.microsoft.com/en-us/microsoft-copilot-studio/guidance/generative-ai-public-websites) |
| **Brave Search** | Brave documents an independent index and a crawler without a differentiated user-agent string. If a page is not crawlable by Googlebot, Brave says its crawler will not crawl it. Brave uses `noindex`, after a re-fetch, for delisting. | Verify actual visibility in Brave Search and use its documented re-fetch/delisting path. Do not assume Brave is Claude's fixed or exclusive search backend without current Anthropic documentation. [Brave crawler guidance](https://search.brave.com/help/brave-search-crawler) |

If a provider does not publish a crawler, index, or publisher-control contract,
record that gap instead of reverse-engineering a durable rule from a single
answer or referral.

## Dated 2026 changes worth monitoring

- **Google, 2026-05-27:** Preferred Sources expanded into AI Overviews and AI
  Mode. Google also announced prominent link carousels for some queries and
  broader use of **Highly Cited** labels on Search result links. These are
  product presentation changes, not proof of a new ranking factor.
  [Google announcement](https://blog.google/products-and-platforms/products/search/original-high-quality-content-search/)
- **Claude web-search API:** `web_search_20260209` and later can dynamically
  filter results before relevant material enters the context window. This
  describes API tool execution, not a publisher ranking signal.
  [Claude web-search documentation](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool)
- **Google's 2026 publisher guidance:** Google explicitly rejects special
  generative-search requirements such as `llms.txt`, artificial content
  chunking, rewriting solely for AI, and special schema. The durable guidance
  remains crawlability, technical clarity, and unique, useful content.
  [Google optimization guidance](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)

## Cross-platform content principles

Treat these as defensible editorial and measurement practices, not universal
ranking weights:

- **Correctness and provenance:** make material claims verifiable with named,
  dated primary sources; distinguish measured facts from estimates and
  interpretation.
- **Original value:** contribute first-hand evidence, expert analysis, or a
  useful synthesis rather than restating commodity summaries.
- **Retrievability:** keep important content available in crawlable text and
  verify that `robots.txt`, preview directives, authentication, CDN, and WAF
  behavior match the intended surface.
- **Reader-first structure:** use headings, lists, tables, definitions, and
  procedures when they improve comprehension. No provider guarantees citation
  because a page uses one of these formats.
- **Freshness with substance:** show publication and review dates when time
  matters, and update the underlying evidence—not only the timestamp.
- **Platform-specific measurement:** record query, locale, account state,
  device, date, surfaced URL, cited passage, and repeat observations. Do not
  convert a one-off answer into a cross-platform rule.

## Reader-first content structures

### Definition Blocks

```
**[Term]** is [clear category] that [primary function], [key characteristic].
```

Use when a scoped definition helps the reader. Avoid manufacturing multiple
definitions solely to meet a citation quota.

### Statistic Blocks

```
According to [Source], [specific statistic] as of [timeframe].
```

Link the original source, state the measurement window and denominator, and
avoid quoting a number whose methodology cannot be checked.

### Q&A Pairs

Use the reader's real question as a heading when that improves navigation.
Answer at the length the question requires; there is no universal word-count
threshold for citation.

### Comparison Tables

Keep dimensions comparable, units explicit, and unknown values visible. Use a
table because it helps comparison, not because citation is guaranteed.

### Step-by-Step Processes

State prerequisites, ordered actions, decision points, and failure modes. Mark
steps that depend on a particular platform version.

### Key Insight Callouts

`> **Key insight**: [Memorable, quotable statement with attribution]`

Use callouts sparingly and keep the source adjacent. Visual emphasis is not
evidence of authority.

## Optimization by Query Type

| Query type | Reader need | Useful structure |
|------------|-------------|------------------|
| **Informational** ("What is", "How does") | Correct scope and explanation | Definition, why it matters, mechanism, examples, limitations |
| **Comparison** ("X vs Y", "Best") | Consistent decision criteria | Comparable table, tradeoffs, evidence, "choose X when" conditions |
| **How-to** ("How to", "Steps to") | Safe completion of a task | Prerequisites, ordered steps, verification, troubleshooting |
| **Statistical** ("How much", "Statistics about") | Traceable numbers and context | Key result, primary source, date/window, denominator, methodology, caveats |

## Optimization Checklist

- [ ] Target surfaces and their current documented controls are named.
- [ ] Search visibility, training, and user-triggered retrieval controls are not conflated.
- [ ] `robots.txt`, CDN, authentication, and WAF behavior have been verified.
- [ ] Material claims link to primary sources with dates and scope.
- [ ] Statistics include a denominator, time window, and checkable methodology.
- [ ] Important content is available in crawlable text.
- [ ] Structured data, when used, matches visible content.
- [ ] Headings, tables, lists, or Q&A are chosen for reader utility—not a fabricated quota.
- [ ] Platform observations record query, locale, date, account/device context, surfaced URL, and cited passage.
- [ ] Recommendations distinguish official requirements, measured observations, and hypotheses.
- [ ] Promotional claims and unsupported ranking guarantees have been removed.
