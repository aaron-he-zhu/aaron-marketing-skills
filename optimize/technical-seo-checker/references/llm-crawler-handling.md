# LLM Crawler Handling (GPTBot / ClaudeBot / PerplexityBot / etc.)

Referenced from [SKILL.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/optimize/technical-seo-checker/SKILL.md). Use during technical audits to decide whether (and how) to allow AI-engine crawlers. As of 2026, this is a required technical-SEO decision, not an optional one.

---

## Why this matters

AI engines (ChatGPT Search, Claude Search, Perplexity, Google AI Overview, Gemini) crawl the web to populate training data AND real-time answer retrieval. Blocking them can:

- Prevent citation in AI answers (GEO visibility loss)
- Reduce brand mentions in AI-generated summaries
- Lock out traffic from the fastest-growing discovery channel

Allowing them can:

- Expose content to training without compensation
- Increase server load
- Leak competitive content to rivals who scrape via AI

**The decision is per-organization.** Common stances:

| Stance | Typical choice | Rationale |
|--------|----------------|-----------|
| Default-open (marketing-led orgs) | Allow all AI crawlers | GEO visibility > training-data concerns |
| Default-closed (IP-heavy orgs) | Block all | Proprietary research, legal docs, customer data |
| Split (most common in 2026) | Allow retrieval bots, block training bots | Best of both — see mapping below |

---

## Known crawler inventory (2026)

### OpenAI

| User-Agent | Purpose | Typical robots.txt choice |
|-----------|---------|---------------------------|
| `GPTBot` | Training data for future ChatGPT models | Most orgs block |
| `ChatGPT-User` | Real-time retrieval when ChatGPT answers with browsing | Most orgs allow (loses citation if blocked) |
| `OAI-SearchBot` | ChatGPT Search (retrieval-focused) | Allow for GEO visibility |

### Anthropic

| User-Agent | Purpose | Typical choice |
|-----------|---------|-----------------|
| `ClaudeBot` / `Claude-Web` | Training data | Most orgs block |
| `Claude-User` | Real-time fetch when user asks Claude to look up a URL | Allow |
| `anthropic-ai` (legacy) | Legacy tag; treat as `ClaudeBot` | Block if blocking training |

### Google

| User-Agent | Purpose | Typical choice |
|-----------|---------|-----------------|
| `Googlebot` | Search + AI Overview | Always allow |
| `Google-Extended` | Opt-out for Bard / Gemini training (does NOT affect Search ranking) | Block if opting out of training only |
| `GoogleOther` | Internal research / product testing | Allow |

### Perplexity

| User-Agent | Purpose | Typical choice |
|-----------|---------|-----------------|
| `PerplexityBot` | Crawl for retrieval answers | Allow for GEO visibility |
| `Perplexity-User` | Real-time fetch for user queries | Allow |

### Common Crawl (downstream training data for many LLMs)

| User-Agent | Purpose | Typical choice |
|-----------|---------|-----------------|
| `CCBot` | Feeds Common Crawl dataset used by many LLMs | Blocking here is indirect training opt-out |

### Other 2026 notable

| User-Agent | Purpose |
|-----------|---------|
| `Bytespider` | TikTok / Doubao / ByteDance LLMs |
| `Applebot-Extended` | Apple Intelligence training opt-out |
| `cohere-ai` | Cohere training |
| `Meta-ExternalAgent` | Meta Llama training |
| `Diffbot` | B2B data scraping (may power enterprise LLMs) |
| `omgili` | Data broker — often blocked |
| `DataForSeoBot`, `AhrefsBot`, `SemrushBot` | SEO tool crawlers — allow if you use the tool |

---

## Recommended robots.txt patterns

### Pattern 1 — Default-open (maximize GEO visibility, accept training)

```txt
# Allow all AI engines for both retrieval and training
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: cohere-ai
Allow: /

# Block only data resellers / scrapers
User-agent: omgili
Disallow: /
```

### Pattern 2 — Default-closed (training opt-out, retrieval in)

```txt
# Allow retrieval bots (needed for GEO visibility)
User-agent: ChatGPT-User
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Perplexity-User
Allow: /

User-agent: Googlebot
Allow: /

# Block training bots
User-agent: GPTBot
Disallow: /

User-agent: ClaudeBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: cohere-ai
Disallow: /

User-agent: Meta-ExternalAgent
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: Bytespider
Disallow: /
```

### Pattern 3 — Section-specific (e.g., allow blog, block pricing)

```txt
User-agent: GPTBot
Allow: /blog/
Allow: /guides/
Disallow: /pricing/
Disallow: /customers/
Disallow: /
# The trailing Disallow: / is the default; Allow: entries above it take precedence
```

---

## Legal layer beyond robots.txt

Robots.txt alone is **not a legal opt-out** under EU law. For full compliance as content rights holder:

### EU DSM Directive Art 4(3) — TDM reservation
Machine-readable reservation required (robots.txt is advisory, not legally binding for TDM):

```html
<!-- In page HEAD -->
<meta name="tdm-reservation" content="1" />
```

Or HTTP response header:

```
X-Robots-Tag: noai, notrain
```

Reference: [W3C TDM Reservation Protocol](https://www.w3.org/2022/tdmrep/).

### EU AI Act Art 53(1)(c) — GPAI provider obligations

> **Phased application of the AI Act**: the Act entered into force 2024-08; prohibited-practice provisions applied from 2025-02; **GPAI provider obligations (Art 51-55, including Art 53 summary-of-training-data) applied from 2025-08-02**; general applicability to high-risk systems phases through 2026-08. The date below refers specifically to when Art 53 GPAI obligations became applicable, not the whole Act.

Art 53 applicable date: **2025-08-02**. General-Purpose AI Model providers (OpenAI, Anthropic, Google, etc.) must:
- Publish summary of training data content
- Respect opt-out signals including `tdm-reservation`
- Establish copyright policy

Content owners: monitor published training data summaries; file DMCA/EU copyright complaints if your content appears despite opt-out.

### CCPA — 2026 California extension
California AG 2025 guidance extends §1798.135 "right to opt-out of sale/share" to training data. Use `Global Privacy Control (GPC)` HTTP header on requests + respect inbound GPC signals if you process user data.

### Post-training content removal
If content was scraped before opt-out was in place:
- **OpenAI**: submit removal at https://platform.openai.com/privacy-removal-request (documented as of 2024)
- **Google Bard/Gemini training**: opt-out via Search Console > Settings > Crawling (Google-Extended block)
- **Perplexity**: email legal@perplexity.ai with URL + copyright assertion
- **Anthropic**: email privacy@anthropic.com (no public removal form as of 2026)

### Enforcement timeline summary
| Jurisdiction | Regulation | Effective | Status |
|---|---|---|---|
| EU | DSM Art 4 | 2019 / 2021 transposition deadline | Active |
| EU | AI Act Art 53 GPAI | 2025-08 | Active |
| US CA | CCPA training data | 2025 AG guidance | Enforceable |
| UK | TDM exception | 2025 consultation | Pending |

## Diagnostic signals during a technical audit

| Signal | Action |
|--------|--------|
| No `User-agent: GPTBot` / `ClaudeBot` / `PerplexityBot` rules in robots.txt | Site is using default-allow; confirm this is intentional with user |
| `Disallow: /` under `User-agent: *` | All bots blocked including Googlebot — usually accidental |
| Rules in robots.txt but no `<meta name="robots">` counterpart on high-value pages | Inconsistent — AI bots may honor meta tag differently |
| Server logs show `GPTBot` / `ClaudeBot` 429s or 403s | Firewall / CDN rate-limiting the bot (Cloudflare's default AI scraper rule, for example) — decide explicitly |
| Cloudflare "Block AI scrapers" toggle on | Check if user expects this — it overrides robots.txt |

## Cloudflare-specific (2026)

Cloudflare added a one-click "Block AI scrapers" toggle that blocks GPTBot, ClaudeBot, CCBot, and others at the edge — **before** robots.txt is evaluated. Audit step:

1. Log into Cloudflare dashboard
2. Security → Bots → AI Scrapers and Crawlers
3. Verify the toggle state matches the org's stance

If Cloudflare is blocking but robots.txt allows, the bot will never reach robots.txt — Cloudflare wins.

## Handoff addition

When the technical audit covers LLM crawler handling, include in the handoff:

- `ai_crawler_stance`: `default-open` | `default-closed` | `mixed` | `unknown`
- `ai_crawler_blocked`: list of bot user-agents blocked (e.g., `[GPTBot, ClaudeBot, CCBot]`)
- `ai_crawler_allowed`: list allowed for retrieval (e.g., `[ChatGPT-User, PerplexityBot]`)
- `ai_crawler_edge_override`: `true` if Cloudflare / Cloudfront is enforcing rules ahead of robots.txt
- Open loop: ask user to confirm or modify stance if unknown

## See also

- [geo-content-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/SKILL.md) — downstream skill that depends on AI engines actually seeing your content
- [entity-optimizer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/entity-optimizer/SKILL.md) — blocking retrieval bots breaks AI entity recognition
