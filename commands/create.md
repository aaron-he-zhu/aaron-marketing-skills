---
name: create
description: "Produce SEO/GEO content end-to-end: brief, draft one asset or a series, refresh stale content, and prepare a CMS-neutral publish package. Not sure? Use /aaron-seo-geo:auto."
argument-hint: "<topic-brief-or-url> [--brief|--series|--refresh|--publish|--meta|--schema] [--type article|landing|faq|comparison]"
parameters:
  - name: input
    type: string
    required: true
    description: "Topic, brief, keyword cluster, draft, URL, or series plan"
  - name: mode
    type: string
    required: false
    description: "brief, series, refresh, publish, meta, or schema (default: write one asset)"
  - name: type
    type: string
    required: false
    description: "Content type when known: article, landing, faq, comparison"
---

# Create Command

Produce SEO/GEO content end-to-end — brief, draft, series, refresh, and publish package — from one entry point.

## Route

- keyword-research
- serp-analysis
- content-gap-analysis
- seo-content-writer
- geo-content-optimizer
- content-refresher
- meta-tags-optimizer
- schema-markup-generator
- internal-linking-optimizer
- content-quality-auditor

## Rules

- Default (no mode): write ONE asset — SEO structure, GEO answer-ready elements, metadata suggestions, proof requirements, and open quality risks. Use provided research/brief evidence when available; ask for missing blocking inputs.
- `--brief`: turn demand, intent, audience, and evidence into a single executable brief (angle, target keyword, intent, outline, proof requirements, GEO structure, internal-link notes, quality risks).
- `--series`: plan / write / continue a content series. Default a topic to planning and a valid series_plan to writing; cap at 3 articles per run (≤6 with chunking); return stable `series_plan` / `batch_summary` continuation state. A batch cannot be `ready` unless every article has full veto-aware audit coverage.
- `--refresh`: diagnose freshness, decay, outdated facts, and ranking loss; return a refresh plan, evidence gaps, update scope, and quality-gate status.
- `--publish`: prepare a CMS-neutral publish package (quality gate + metadata + schema + media + internal-link checks); do not publish directly. Allow `ready` only with full veto-aware audit coverage at SHIP, `cap_applied: false`, no BLOCKED status, no veto/blocker open loops, no unresolved required evidence, and `ready_verdict_allowed: true`.
- `--meta`: title / meta / Open Graph variants only. `--schema`: JSON-LD only; never invent unsupported rich-result facts.
- Do not claim publish-ready status without `/aaron-seo-geo:audit` or `--publish` quality-gate evidence.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
