---
name: audit
description: "Evaluate and harden what exists: on-page SEO, content quality (CORE-EEAT), technical SEO, AI-visibility/GEO readiness, and domain authority (CITE). Not sure? Use /aaron-seo-geo:auto."
argument-hint: "<url-domain-or-content> [--full] [--tech|--visibility|--authority] [--competitors <domains>]"
parameters:
  - name: target
    type: string
    required: true
    description: "URL, domain, pasted content, brand, or entity to evaluate"
  - name: scope
    type: string
    required: false
    description: "full, tech, visibility, or authority (default: page SEO + CORE-EEAT)"
  - name: competitors
    type: string
    required: false
    description: "Competitor domains for authority comparison"
---

# Audit Command

Evaluate and harden any existing asset — page quality, technical health, AI visibility, and domain trust.

## Route

- on-page-seo-auditor
- content-quality-auditor
- technical-seo-checker
- geo-content-optimizer
- entity-optimizer
- domain-authority-auditor
- backlink-analyzer

## Rules

- Default (page audit): check on-page SEO, metadata, headings, images, links, and CORE-EEAT risk. Return `ready`, `ready_with_concerns`, `blocked`, or `needs_input` with evidence and next fixes. Use `--full` to run the full publish-readiness gate when evidence is available.
- `--tech`: crawlability, indexation, Core Web Vitals, mobile, security, structured-data exposure, robots, sitemap, canonical, redirect, and migration risk. Do not guess CWV or crawl data; mark missing evidence and next checks.
- `--visibility`: AI answer inclusion and GEO citation readiness, entity clarity, and trust blockers. Do not claim observed citation proof; require content-quality-auditor before any publish-ready, cite-ready, or GEO Score readiness verdict.
- `--authority`: CITE / domain-trust analysis, backlink quality, and entity credibility; flag trust blockers, toxic-link risks, missing entity proof, and authority-building opportunities. `--competitors` adds comparison.
- Do not produce a publish-ready verdict without full veto-aware audit coverage.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
