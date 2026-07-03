# Robots.txt Reference Guide

Use robots.txt to control crawling, not indexing. To prevent indexing, use `noindex` meta or `X-Robots-Tag`.

## Directives

| Directive | Use | Notes |
|-----------|-----|-------|
| `User-agent: *` | All bots | Group consecutive user-agent lines before rules |
| `Disallow: /path/` | Block crawl path | `/admin/` is safer than `/admin` for directories |
| `Allow: /path/` | Override a broader block | Supported by Google, Bing, most major crawlers |
| `Sitemap: https://example.com/sitemap.xml` | Declare XML sitemap | Absolute URL; multiple lines allowed |
| `Crawl-delay: 10` | Slow some crawlers | Googlebot ignores it; use Search Console for Google |

## Common User Agents

`Googlebot`, `Bingbot`, `DuckDuckBot`, `OAI-SearchBot`, `GPTBot`, `ChatGPT-User`, `ClaudeBot`, `anthropic-ai`, `PerplexityBot`, `Perplexity-User`, `CCBot`, `Google-Extended`.

## AI Crawler Patterns

Block AI training and broad dataset crawlers while allowing search indexing and selected AI retrieval bots:

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

User-agent: Googlebot
Disallow:

User-agent: Bingbot
Disallow:

Sitemap: https://example.com/sitemap.xml
```

Allow only search engines: block `User-agent: *`, then explicitly allow Googlebot, Bingbot, DuckDuckBot, and required commercial crawlers.

## SEO-Critical Configs

| Scenario | Starter rules |
|----------|---------------|
| Parameter crawl waste | `Disallow: /*?` then `Allow: /?` only if homepage/search needs it |
| Ecommerce | Block account/cart/checkout/admin, parameter filters/sort/search; allow `/products/` |
| WordPress | Block `/wp-admin/`, allow `/wp-admin/admin-ajax.php`, allow uploads, block feeds/search/trackbacks when needed |
| Staging | `Disallow: /` plus noindex/auth; remove via Search Console if indexed |

## Mistakes and Fixes

| Mistake | Risk | Fix |
|---------|------|-----|
| Blocking CSS/JS | Google cannot render pages | Allow asset paths |
| Relative sitemap | May not parse | Use absolute sitemap URL |
| Spaces before colons | Invalid syntax | `User-agent: Googlebot` |
| Missing trailing slash | Over-blocks similar paths | Use `/admin/` for directory only |
| Using robots.txt for de-indexing | URL can still be indexed if linked | Use noindex/meta/header |
| Case mismatch | Paths are case-sensitive | Cover real URL variants |

## File Requirements

Returns 200, plain text UTF-8, located at `/robots.txt`, lowercase filename, under 500KB, tested in Search Console.

## Monitoring

Monthly: accessibility, blocked URLs, crawl stats. Quarterly: blocked paths, private sections, AI crawler changes. After migrations: retest URL structures and sitemap references.

## Emergency Fixes

If the site is accidentally blocked, change to `User-agent: *` plus empty `Disallow:`, include Sitemap, test in Search Console, and request recrawl. If CSS/JS is blocked, add asset `Allow` rules and re-render key URLs.
