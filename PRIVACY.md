# Privacy Policy

## Overview

The SEO & GEO Skills Library is a collection of markdown-based skill files that run locally within your Claude Code environment. This project does not collect, store, or transmit any user data by itself. When users invoke certain skills, those skills may fetch URLs or call connected MCP servers — the specifics are documented below.

## Data Transmission (accurate as of 2026-04)

### Default behavior
By default, this library:
- **Does NOT** transmit any data to external servers
- **Does NOT** include telemetry or analytics
- **Does NOT** automatically exfiltrate `memory/` contents

### When data DOES leave your machine (user-initiated)

**1. WebFetch-enabled skills** (`content-quality-auditor`, `on-page-seo-auditor`, `technical-seo-checker`, `schema-markup-generator`, `serp-analysis`):
- These skills fetch URLs you provide
- Your request headers (IP, User-Agent) reach the target server
- Fetched page content re-enters your Claude session as context
- Caveat: fetched content is treated as **untrusted data** (see each skill's Security boundary note), not instructions

**2. MCP connectors** (listed in `.mcp.json`):
- Each active connector sends data to its vendor per the vendor's privacy policy
- Connectors: Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack (14 total, all HTTPS)
- **No connector is enabled without explicit OAuth / API key setup**

**3. Memory files contain third-party data**:
- `memory/audits/` may contain competitor URLs, target keywords, audit findings
- `memory/entities/` may contain third-party brand/person names
- Not transmitted by this library — but users should be aware when committing repo to public Git, sharing with AI agents, or syncing across devices
- See [memory-management SKILL.md §GDPR / Privacy Compliance](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md) for retention + deletion guidance

### In scope for security review
- Memory poisoning across sessions (malicious content written to `memory/` affecting future sessions)
- WebFetch-injected instructions (prompt injection via target page HTML/meta)
- Cross-session trust boundary (Stop hook auto-writes memory on user "save" confirmation — verify before approving)

See [SECURITY.md](SECURITY.md) for responsible disclosure.

## Third-Party Services

This project references but does not bundle or depend on:

- **ClawHub** / **skills.sh**: Skill distribution platforms (their privacy policies apply during installation)
- **GitHub**: Source code hosting (GitHub's privacy policy applies)

## Contact

For privacy-related questions: **hello@zhuhe.io**

## Changes

This privacy policy may be updated as the project evolves. Changes will be documented in commit history.

*Last updated: 2026-04-17*
