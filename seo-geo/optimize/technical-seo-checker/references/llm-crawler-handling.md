# LLM Crawler Handling

Use robots.txt and server policy to decide which AI crawlers can access content. This is a policy and technical SEO decision, not only a crawler-control task.

## Crawler Matrix

| Bot | Operator / Use | Typical Rule |
|-----|----------------|--------------|
| OAI-SearchBot | OpenAI search/citation discovery | Allow when ChatGPT search visibility is desired |
| GPTBot | OpenAI training/crawling | Allow if AI visibility/data use is acceptable; block for TDM restriction |
| ChatGPT-User | OpenAI user-requested browsing/actions | Usually allow for user-triggered access; robots.txt may not apply |
| ClaudeBot / anthropic-ai | Anthropic crawling/training | Same policy decision as GPTBot |
| Claude-SearchBot | Anthropic search/citation discovery for Claude | Allow when Claude search-citation visibility is desired (the retrieval analog of OAI-SearchBot) |
| Claude-User | Anthropic user-triggered browsing/actions | Usually allow for user-triggered access; robots.txt may not apply |
| Google-Extended | Google AI training opt-out | Block to restrict training while Googlebot can still index. Does not affect AI Overviews / AI Mode, which use the Google index — opting out of those is not available via robots.txt |
| Googlebot | Search indexing | Usually allow |
| Bingbot | Search indexing / Copilot ecosystem | Usually allow |
| PerplexityBot | AI answer retrieval | Allow when citation visibility is desired |
| Perplexity-User | Perplexity user-triggered fetcher | Allow only if logs/IP docs confirm this access path is wanted |
| CCBot | Common Crawl | Block when broad dataset reuse is not desired |

## Policy Modes

| Mode | Use When | Robots Pattern |
|------|----------|----------------|
| default-open | AI visibility and citation discovery are goals | Allow search, retrieval, and selected AI bots; block only sensitive paths |
| default-closed | Licensed, paid, private, or TDM-reserved content | Block broad AI crawlers by default; allow only approved search/retrieval bots |
| split | Search indexing yes, AI training no | Allow Googlebot/Bingbot/OAI-SearchBot/Claude-SearchBot/selected retrieval bots; block GPTBot, ClaudeBot, CCBot, Google-Extended |

## Search-Only Starter

```txt
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: anthropic-ai
User-agent: CCBot
User-agent: Google-Extended
Disallow: /

User-agent: OAI-SearchBot
Disallow:

User-agent: ChatGPT-User
Disallow:

User-agent: PerplexityBot
User-agent: Perplexity-User
Disallow:

User-agent: Claude-SearchBot
User-agent: Claude-User
Disallow:

User-agent: Googlebot
User-agent: Bingbot
Disallow:

Sitemap: https://example.com/sitemap.xml
```

> **Note**: this "search-only" pattern blocks `ClaudeBot` (training) but explicitly allows
> `Claude-SearchBot`/`Claude-User` — otherwise you silently lose Claude's search citations while
> only meaning to opt out of training. Mirror the same allow/block split for every assistant.

## Technical Checks

| Check | Why |
|-------|-----|
| robots.txt returns 200 and parses | Crawler policy must be readable |
| Search bots still allowed | Avoid accidental SEO loss |
| Sitemap references current canonical URLs | Supports discovery |
| Retrieval bots include OAI-SearchBot, ChatGPT-User, PerplexityBot, Perplexity-User, Claude-SearchBot, and Claude-User where desired | Prevents accidental citation loss |
| Published IP ranges match provider JSON when edge rules are used | Avoids spoofing and stale allowlists |
| Private/gated paths use auth or noindex, not only robots.txt | robots.txt is not access control |
| Logs confirm bot behavior | Validate crawl policy after launch |

## Cloudflare Edge-Override Gotcha

Cloudflare and other edge tools can override origin robots.txt, block user agents before they reach the file, or serve different rules by host/path. Check WAF/bot rules, Workers, Transform Rules, cache variants, and raw origin response before concluding the published robots.txt is the effective crawler policy.

## Legal/Compliance Notes

EU AI Act Art 53 and EU DSM TDM reservations may matter for rights-reserved content. Robots.txt can signal intent, but it is not a complete training opt-out or licensing mechanism. For regulated/licensed content, pair crawler policy with contracts, access controls, rights-reservation notices (for example TDM reservation where adopted), and any `X-Robots-Tag` directives your target crawlers actually honor.

## Reporting Fields

Policy mode, allowed bots, blocked bots, affected paths, business rationale, source/date, expected SEO/GEO effect, and retest date.
