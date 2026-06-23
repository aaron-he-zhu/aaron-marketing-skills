# Connectors

> Skills use `~~category` placeholders instead of specific tool names. **Every skill runs at Tier 1 with zero external dependencies** — paste data manually, or pull it yourself from the free/public sources below. MCP servers (further down) are an optional Tier 2/3 convenience, never required.

All endpoints below were verified against primary vendor/source docs (2026-05). If a call 404s, re-check the linked doc — vendors move endpoints.

## Bundled helpers — run the data fetch locally (zero-dependency)

For the bundle-able categories the repo ships small **Python-3-stdlib** helpers under [`scripts/connectors/`](scripts/connectors/README.md) — no `pip`, no key (except where noted). They turn the recipes below into one command, so a skill can pull real data itself instead of asking you to paste it. Run from the repo root:

| Capability | Helper | Needs |
|---|---|---|
| Crawl a site (→ page records) | `crawl.py <url>` | — |
| On-page audit (title/meta/headings/canonical/JSON-LD) | `onpage.py <url>` | — |
| robots.txt eval + AI-bot check | `robots.py <url> --check-ai-bots` | — |
| sitemap / sitemap-index / llms.txt | `sitemap.py <url>` | — |
| Internal-link graph (orphans / depth / internal PageRank) | `crawl.py … \| linkgraph.py -` | — |
| Page speed + Core Web Vitals | `psi.py <url>` | free key for automation |
| Structured-data extract + validate (+ FAQ/HowTo deprecation) | `schema_lint.py <url>` | — |
| Entity → Wikidata QID + claims | `kg.py reconcile "<name>"` | — |
| Archive history / change tracking | `wayback.py <url>` | — |
| Domain-authority signal | `openpagerank.py <domain> --key …` | free key |
| Keyword ideas (⚠️ unofficial endpoint) | `suggest.py "<seed>" --expand` | — |
| Brand / mention RSS | `rss_monitor.py <feed-url>` | — |

See [scripts/connectors/README.md](scripts/connectors/README.md) for the full list, the safety contract, and what intentionally stays external (proprietary / own-data → MCP/API).

## Free & public data sources (no paid tool, no MCP)

The fastest way to keep a skill zero-dependency is to feed it data from a free, first-party, or keyless public endpoint, then paste the response when the skill asks for the matching `~~category` data.

### Your own site — first-party, free

| Need (`~~category`) | Source | Endpoint / how | Auth | Free limit |
|---|---|---|---|---|
| Keywords + rankings (`~~SEO tool`, `~~search console`) | Google Search Console Search Analytics API | `POST https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/searchAnalytics/query` (URL-encode siteUrl, or use `sc-domain:example.com`) | OAuth 2.0, scope `https://www.googleapis.com/auth/webmasters.readonly` | 1,200 queries/min per site |
| Keywords + rankings on Bing | Bing Webmaster Tools API | REST API; key from BWT → Settings → API Access | `apikey` query param **or** OAuth Bearer (token `https://www.bing.com/webmasters/oauth/token`) | free account |
| Traffic & behavior (`~~analytics`) | Google Analytics Data API (GA4) | `POST https://analyticsdata.googleapis.com/v1beta/{property=properties/*}:runReport` | OAuth 2.0, scope `https://www.googleapis.com/auth/analytics.readonly` | 200,000 tokens/property/day |
| Backlinks to your site (`~~link database`) | GSC Links report | Search Console UI → Links → Export top linking sites | GSC login | free |

### Public / keyless — any site

| Need (`~~category`) | Source | Endpoint / how | Auth | Limit |
|---|---|---|---|---|
| Keyword ideas / autocomplete (`~~SEO tool`) | Google Suggest — **⚠️ unofficial, undocumented** | `https://suggestqueries.google.com/complete/search?client=chrome&q=QUERY&hl=en&gl=US` | none | undocumented; backoff on 429/503, may change without notice |
| Domain authority signal (`~~link database`) | Open PageRank | `GET https://openpagerank.com/api/v1.0/getPageRank?domains[]=example.com` | free key in header `API-OPR: KEY` | 10,000 calls/hr, ≤100 domains/call (domain-rank scores, not raw link lists) |
| Inbound links / web graph (`~~link database`, `~~web crawler`) | Common Crawl CDX index | `https://index.commoncrawl.org/CC-MAIN-YYYY-WW-index?url=URL&output=json` — crawl list at `https://index.commoncrawl.org/collinfo.json` | none | shared server, keep < 10 req/s (expect `503 SlowDown`) |
| Historical pages / change tracking (`~~competitive intel`) | Wayback Machine CDX API | `http://web.archive.org/cdx/search/cdx?url=URL&output=json` (matchType `exact`/`prefix`/`host`/`domain`) | none | be gentle |
| Entity / knowledge-graph facts (`~~knowledge graph`) | Wikidata SPARQL | `https://query.wikidata.org/sparql?query=...&format=json` (GET or POST) | none — **descriptive User-Agent required** | ~60s query CPU per 60s per IP (429 on excess) |
| Entity lookup via Google (`~~knowledge graph`) | Google Knowledge Graph Search API — **⚠️ soft-migrating to Cloud Enterprise KG** | `GET https://kgsearch.googleapis.com/v1/entities:search?query=...&key=KEY` | API key | 100,000 calls/day (no sunset date announced; prefer Wikidata for durable keyless access) |

### Optional authenticated public social data

Use these when a skill needs public social context for competitor reactions, brand mentions, launch language, or objection patterns. They are optional convenience sources; pasted exports keep every skill usable at Tier 1.

| Need (`~~category`) | Source | Endpoint / how | Auth | Limit |
|---|---|---|---|---|
| Public X/Twitter search context (`~~social signals`, `~~competitive intel`, `~~brand monitor`) | Xquik API | `GET https://xquik.com/api/v1/x/tweets/search` with `q`, `queryType=Top`, and `limit`; docs: `https://docs.xquik.com/api-reference/x/search-tweets` | `X-API-Key` header | current account plan |

### Page speed / Core Web Vitals — free (`~~page speed tool`)

| Data | Source | Endpoint | Auth | Limit |
|---|---|---|---|---|
| Lab Lighthouse score | PageSpeed Insights API v5 | `GET https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=URL&strategy=mobile` | key optional (recommended for automation) | — |
| Real-user field CWV | Chrome UX Report (CrUX) API | `POST https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=KEY` | Google Cloud API key (query param) | 150 queries/min (free; no paid increase) |
| Local lab run | Lighthouse CLI | `npx lighthouse URL --output json --output-path=./lh.json` | none | — |

### Open-source / self-host / DIY

| Need (`~~category`) | Tool | How |
|---|---|---|
| Crawl, robots.txt, sitemaps, SERP, logs (`~~web crawler`) | **advertools** (Python, OSS) | `pip install advertools` — site crawl, `sitemap_to_df`, `robotstxt_test`, SERP analysis, log-file parsing |
| Desktop crawl (`~~web crawler`) | Screaming Frog SEO Spider | free tier ≤ 500 URLs |
| Privacy analytics you own (`~~analytics`) | **Plausible** / **Matomo** (OSS, self-host) | Plausible Stats API v2: `POST https://plausible.io/api/v2/query` (`Authorization: Bearer KEY`, 600 req/hr); self-host uses the same path on your host |
| Schema / structured-data check (`~~schema validator`) | validator.schema.org · Google Rich Results Test | **UI only — paste markup; no public API** |
| Brand / mention monitoring (`~~brand monitor`) | Google Alerts (RSS) · F5Bot | free email/RSS alerts on brand or keyword mentions |
| AI-answer citation check (`~~AI monitor`) | Manual prompt-testing (ChatGPT / Perplexity / Google AI Overviews) · OSS GEO trackers | **no free API** — run target prompts, record which sources each engine cites, track over time |

**Zero-tool DIY pattern:** for most technical and content checks you need nothing but `fetch` — pull `robots.txt`, `sitemap.xml`, `llms.txt`, and the page HTML directly, and paste them in.

## Tool Categories (placeholder → tools)

| Category | Placeholder | Example paid tools | Free alternative (above) |
|----------|-------------|--------------------|--------------------------|
| SEO Platform | `~~SEO tool` | Ahrefs, Semrush, Moz, SISTRIX, SE Ranking | GSC + Google Suggest |
| Analytics | `~~analytics` | GA, Adobe Analytics, Plausible, Matomo | GA4 Data API / self-host Plausible |
| Search Console | `~~search console` | Google Search Console, Bing Webmaster | GSC + Bing WMT APIs |
| AI Visibility | `~~AI monitor` | Otterly, Profound, Scrunch AI | manual prompt-testing |
| Web Crawler | `~~web crawler` | Screaming Frog, Sitebulb, Lumar | advertools / Screaming Frog free / DIY fetch |
| Link Database | `~~link database` | Ahrefs, Majestic, Moz | Open PageRank + Common Crawl + GSC Links |
| Competitive Intel | `~~competitive intel` | SimilarWeb, SpyFu, Semrush | Wayback CDX + Common Crawl |
| Page Speed | `~~page speed tool` | GTmetrix, WebPageTest | PSI / CrUX / Lighthouse |
| Schema Validator | `~~schema validator` | — | validator.schema.org / Rich Results Test |
| Knowledge Graph | `~~knowledge graph` | Google KG API, CrunchBase | Wikidata SPARQL |
| Brand Monitor | `~~brand monitor` | Brand24, Mention, Brandwatch | Google Alerts / F5Bot |
| Public Social Signals | `~~social signals` | Xquik | manual public post exports |
| CRM / Marketing | `~~CRM` | HubSpot, Salesforce, Marketo | — |
| Content / CMS | `~~content platform` / `~~CMS` | WordPress, Webflow, Contentful, Sanity, Notion | — |
| Communication | `~~team chat` | Slack, Teams, Discord | — |
| Reporting | `~~reporting` | Looker Studio, Tableau, Power BI | — |

## How placeholders work

A skill might say: *"Pull keyword rankings from `~~SEO tool` and cross-reference with `~~search console` impressions."* If you use Ahrefs + Google Search Console, read it as Ahrefs + GSC. If you use no paid tool, read it as "the Search Console Search Analytics API (above)" — or just paste the data.

## Optional MCP servers (Tier 2/3 automation)

`.mcp.json` ships official **remote HTTP MCP endpoints** (auth happens interactively on first use). MCP automates retrieval but is never required — the free sources above cover the same data.

**SEO data** (endpoints verified 2026-05):

| Vendor | Endpoint (`.mcp.json`) | Transport | Auth | Sample tools |
|--------|------------------------|-----------|------|--------------|
| Ahrefs | `https://api.ahrefs.com/mcp/mcp` | streamable HTTP | API key (MCP scope; Lite+ plan) | keyword & backlink data, site audit |
| Semrush | `https://mcp.semrush.com/v1/mcp` | streamable HTTP | OAuth, or `Authorization: Apikey KEY` | `organic_research`, `keyword_research`, `backlink_research` |
| SE Ranking | `https://api.seranking.com/mcp` | streamable HTTP | OAuth or API key (`X-Api-Key`) | keyword/backlink/domain, AI-search visibility (160+ tools) |
| SISTRIX | `https://api.sistrix.com/mcp/` | HTTP | OAuth / Bearer / `X-API-Key` | `domain`, `keyword`, `links`, `ai` modules |
| SimilarWeb | `https://mcp.similarweb.com` | HTTP | OAuth / key | traffic estimates, competitive intel |

**Free Google data via MCP** (not shipped in `.mcp.json` — these run locally and need your own Google credentials):

- **Google Analytics** — official ([github.com/googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp)): `pipx run analytics-mcp`, stdio, ADC scope `analytics.readonly`; tools `run_report`, `run_realtime_report`, `get_account_summaries`.
- **Google Search Console** — community ([github.com/AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc), MIT): `uvx mcp-search-console`, stdio, OAuth or service account; tools `get_search_analytics`, `inspect_url_enhanced`, `list_properties`.

**Infra / CMS / CRM / comms** (shipped in `.mcp.json`, official remote endpoints, OAuth on first use): Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack. See each vendor's MCP docs for its current tool list.

To add a server for local use, edit your host/user MCP config; only change the published project `.mcp.json` when contributing a default endpoint.

## Progressive enhancement tiers

| Tier | Integration | Experience |
|------|-------------|------------|
| **Tier 1** | None | Paste data, or pull it from the free sources above. Skills provide the full analysis framework. |
| **Tier 2** | A free first-party API or one MCP | Automatic retrieval of your own GSC/GA4/CWV data. |
| **Tier 3** | Full MCP set | Fully automated multi-source workflows. |

Every skill works at Tier 1. Connecting tools only automates data retrieval.

## Environment variables

Soft dependencies — skills work without them.

| Variable | Used by | Skills |
|----------|---------|--------|
| `AHREFS_API_KEY` | Ahrefs MCP | keyword-research, competitor-analysis, serp-analysis, content-gap-analysis, backlink-analyzer, rank-tracker, internal-linking-optimizer |
| `AMPLITUDE_API_KEY` | Amplitude MCP | performance-reporter, alert-manager |
| `XQUIK_API_KEY` | Xquik API | competitor-analysis, domain-authority-auditor, entity-optimizer |

Most servers (Semrush, SE Ranking, SISTRIX, SimilarWeb, Cloudflare, Vercel, Webflow, Sanity, Contentful) use **OAuth** — no env var needed. The free Google APIs use OAuth (GSC/GA4) or an API key (PSI/CrUX/Knowledge Graph) you supply at call time.

## Freshness & caveats

- **Google Knowledge Graph Search API** is in soft-migration to Cloud Enterprise Knowledge Graph (no sunset date). Prefer **Wikidata SPARQL** for durable, keyless entity data.
- **Google Suggest/autocomplete** is unofficial and undocumented — it may change or rate-limit without notice; add exponential backoff.
- **Common Crawl**'s shared index server has been rate-limited since Nov 2023 — expect `503 SlowDown`; run your own index for heavy use (data is free on AWS S3 `commoncrawl`).
- **Google Rich Results Test** and **validator.schema.org** expose no public API — paste markup into the UI.
- **AI-citation visibility** has no free API from any engine — the realistic free method is manual prompt-testing recorded over time.
