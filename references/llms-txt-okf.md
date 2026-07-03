# The Agent-Readable File Stack (llms.txt + OKF)

A layered set of files that tell crawlers and AI agents what your site contains and which parts you most want read. This is protocol-layer registration: shipping these files makes you discoverable to agents that adopt the conventions, but none of them carries a confirmed ranking or citation signal today. Treat it as the same kind of early bet that `schema.org` was a decade ago.

## The stack, layer by layer

Each layer answers a different question. They stack rather than compete: `llms.txt` is the signpost, the OKF bundle is the library.

| Layer | File / path | What it does for an agent |
|---|---|---|
| Crawl map | `sitemap.xml` | Lists which URLs exist |
| Access rules | `robots.txt` (with AI-bot lines) | Permits or blocks specific AI crawlers |
| Reading list | `llms.txt` (site root) | Points an agent at the handful of pages you most want read |
| Buyer data | `/pricing.md` | Structured pricing for agent-buyer comparison |
| Content bundle | `/okf/` (OKF bundle) | Hands over the content itself as cross-linked concept files |
| Per-page data | Schema markup | Structured data per page (Article, FAQPage, Product, etc.) |

## Minimal `llms.txt`

A plain Markdown file at the site root. An H1 with the site name, an optional one-line summary, then linked sections. Keep it to the pages you actually want an agent to read.

```markdown
# Example Co

> Project management software for small teams.

## Docs
- [Getting started](https://example.com/docs/start): setup in five minutes
- [API reference](https://example.com/docs/api): endpoints and auth

## Product
- [Pricing](https://example.com/pricing.md): plans and per-seat cost
- [Knowledge bundle](https://example.com/okf/index.md): full content as OKF
```

The last line points agents that read `llms.txt` today at the OKF bundle, so they can discover it later.

## OKF: the content bundle

OKF (Open Knowledge Format) is Google's v0.1 Markdown spec for representing site content as an agent-readable bundle, introduced on the Google Cloud blog on 2026-06-12 and shipped inside Knowledge Catalog. It is a directory of cross-linked Markdown files. Each file has:

- YAML frontmatter (`type` required; `title`, `description`, `resource`, `tags`, `timestamp` recommended)
- A standard Markdown body
- Standard Markdown links to other files in the bundle, which the spec reads as concept relationships

An optional `index.md` lists every file so an agent sees the bundle's shape before opening each one. Ship it as a git repo, a tarball, or a subdirectory. Serve it at `yoursite.com/okf/`, starting with `/okf/index.md`.

One concept file:

```markdown
---
type: Article
title: How to Connect a Project to the API
description: Auth, the endpoint, and a worked example.
resource: https://example.com/docs/connect-api/
tags: [api, auth]
---

# How to Connect a Project to the API

The body of the page, as clean Markdown.
```

Google built OKF for data teams sharing catalog metadata (BigQuery tables, metrics, playbooks), not blog posts. Pointing it at a marketing site is a repurposing popularized by Suganthan Mohanadasan; it is a valid use of the format but not Google's primary one. Frame it that way when you explain it.

## Honest framing

- **No confirmed AI-search effect today.** Nothing crawls the web for OKF bundles yet, no AI engine has announced reading `llms.txt` or OKF as a ranking input, and Knowledge Catalog ingests OKF only for paying enterprise data teams. Anyone claiming a current ranking or citation lift is guessing.
- **Why ship it anyway.** Protocol-layer registration is a cheap, reversible bet. Schema.org took most of a decade to pay off and early adopters were still glad they shipped it. These files are the same shape of bet.
- **A benefit that pays off now.** Building an OKF bundle is an internal-linking audit in disguise: drawing every page as a node and every internal link as an edge makes orphan and island pages obvious.
- **Generate from your own data.** Build the bundle from your own pages or sitemap (manual export, or a free generator that crawls a URL list and returns a downloadable directory). No paid API is required, and the files live on hosting you already control.

## When to skip

- Site is under ~10 pages: the overhead beats the payoff.
- Closed platform (Wix, Squarespace, most page-builders) that won't serve files at custom paths.
- You aren't maintaining `llms.txt`, schema, or other machine-readable files: OKF compounds with those and does little alone.
- You can't budget ~30 minutes a quarter to refresh the bundle as content changes.

## What to watch (all currently no-signal)

- Whether Google announces OKF support in AI Overviews or the Knowledge Graph.
- Whether non-Google engines (ChatGPT, Perplexity, Claude) announce reading OKF or `llms.txt`.
- Whether the spec moves to v1.0 (breaking changes possible below 1.0).
- Adoption signals: search GitHub for `okf/index.md` to see who is shipping bundles.

## Which skills consume this

- **`geo-content-optimizer`**: recommends and structures the `llms.txt` reading list and OKF concept files as part of AI-visibility prep.
- **`entity-optimizer`**: uses the cross-linked bundle to express entity relationships consistently across pages (the canonical entity profile).
- **`serp-markup-builder`**: produces the per-page schema layer that sits alongside the bundle; OKF `type` values map to schema types (Article, FAQPage, Product).

See also `skill-contract.md` for the shared handoff contract.
