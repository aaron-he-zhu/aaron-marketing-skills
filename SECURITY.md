# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 5.x     | Yes       |
| 4.x     | Security fixes only |
| < 4.0   | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email: **hello@zhuhe.io**

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial assessment**: Within 5 business days
- **Fix or mitigation**: Within 30 days for critical issues

## Scope

This project consists of markdown-based skill files with no runtime dependencies. The primary security concerns are:

- **Prompt injection**: Skill files that could be manipulated to produce harmful outputs
- **MCP server configuration**: Misconfigured connectors in `.mcp.json` that could expose credentials
- **Placeholder misuse**: `~~tool` placeholders resolving to unintended targets
- **Memory poisoning across sessions** — malicious content written to `memory/` that affects future session behavior (e.g., fake `approved_by: user` decisions, poisoned `memory/entities/` records)
- **WebFetch-injected instructions** — prompt injection via target page HTML/meta/body attempting to manipulate audit outcomes or Artifact Gate validation

## Security Design Principles

- **Zero runtime dependencies**: No packages to compromise via supply chain attacks
- **No credential storage**: Skills never store API keys; credentials live in user-managed `.mcp.json`
- **Tool-agnostic placeholders**: Skills reference tools by category (`~~SEO tool`), never by hardcoded API endpoints
- **Apache 2.0 license**: Full source available for security review

## Scraping Boundaries

> **⚠️ Not legal advice.** The citations below summarize publicly reported authority as of 2026-04-17. Statutes, case law, and regulator guidance evolve; jurisdictional coverage varies. Consult counsel for your specific jurisdiction and fact pattern before acting on any boundary below.

Several skills in this library involve crawling, fetching, or extracting content from web domains (e.g., `competitor-analysis`, `technical-seo-checker`, `on-page-seo-auditor`, `internal-linking-optimizer`, `backlink-analyzer`). Before invoking these skills against a domain that you do not own or operate under written authorization, Claude and the user must verify the following:

### 1. robots.txt compliance

Always fetch and parse `/robots.txt` before issuing any automated request to a third-party domain. If the target path is listed under `Disallow:` for the user agent in use, do not crawl it. Treat `User-agent: *` `Disallow: /` as a full opt-out.

### 2. TOS breach precedents (U.S. CFAA + EU)

Unauthorized automated access can trigger Computer Fraud and Abuse Act (18 U.S.C. § 1030) exposure and EU equivalents. Reference cases:

- **hiQ Labs v. LinkedIn** (9th Cir. preliminary-injunction dictum 2019/2022; district-court remand 2022) — the 9th Circuit's preliminary-injunction framing suggested scraping public data is generally not "without authorization" under the CFAA, but hiQ ultimately *lost* on LinkedIn's breach-of-contract claim at remand. Treat the CFAA-only framing as narrow; contract and tortious-interference exposure can survive even where CFAA does not apply.
- **Meta Platforms v. Bright Data** (N.D. Cal., Jan 2024) — Meta *lost* summary judgment on the logged-out public-data scraping claims; contract-based claims on logged-in activity fared differently. Courts are still sorting public vs. authenticated scraping under state-law theories. Outcomes are jurisdiction-specific and fact-dependent; do not read either case as a green light or a blanket prohibition.

If a target site posts a C&D, invalidates the crawler's account, or lists the user agent in `robots.txt` under `Disallow:`, stop crawling and surface the block to the user rather than attempting workarounds.

### 3. EU DSM Directive Article 4 (TDM opt-out)

The EU Digital Single Market Directive (2019/790) Article 4(3) permits text-and-data mining reservations via machine-readable signals:

- `<meta name="tdm-reservation" content="1">` in HTML `<head>`
- HTTP response header `X-Robots-Tag: noai, notrain`
- W3C TDM Reservation Protocol (TDMRep) assertions

Honor these signals when crawling domains physically served from the EU or to EU users, even when `robots.txt` alone would allow access. When a reservation is found, treat it as an opt-out for AI-adjacent use (training, embedding generation, summarization used downstream for model improvement).

### 4. Crawl-delay respect

When `robots.txt` declares `Crawl-delay: N`, pause at least N seconds between requests. If not declared, a conservative default of 1 request/second/host prevents accidental DoS conditions and reduces the probability of being blocked at the edge (Cloudflare, Akamai, AWS WAF).

### 5. Skill-level pre-flight

Each skill that performs crawling ships a pre-flight preamble in its Data Sources section reiterating these boundaries. Users remain responsible for confirming authorization before acting on any scraping recommendation the skills produce.

---

## Acknowledgments

We thank the security community for responsible disclosure. Contributors who report valid vulnerabilities will be credited in release notes (with permission).
