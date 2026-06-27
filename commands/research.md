---
name: research
description: "Understand the opportunity: keyword demand, SERP intent, competitors, content gaps, and site/topic/entity maps. Not sure? Use /aaron-seo-geo:auto."
argument-hint: "<topic-or-domain> [--competitors <domains>] [--map]"
parameters:
  - name: target
    type: string
    required: true
    description: "Seed topic, market, domain, or content inventory"
  - name: competitors
    type: string
    required: false
    description: "Competitor domains or brands for comparison"
  - name: map
    type: boolean
    required: false
    description: "Build a topic/entity/site/internal-link architecture map"
---

# Research Command

Understand the opportunity and landscape: keyword demand, SERP intent, competitors, content gaps, and site/topic/entity architecture.

## Route

- keyword-research
- serp-analysis
- content-gap-analysis
- competitor-analysis
- backlink-analyzer
- entity-optimizer
- internal-linking-optimizer

## Rules

- Discover search demand, SERP intent, topic clusters, and content opportunities; keep AI-answer-inclusion diagnosis in `/aaron-seo-geo:audit --visibility`.
- With `--competitors`, compare across rankings, content coverage, backlinks, authority, and AI citation visibility; return a battlecard, gaps, priority opportunities, and evidence mode.
- With `--map` (or a known opportunity set), turn findings into a content architecture, topic/entity map, and internal-link plan: clusters, pillar/supporting pages, orphan risks, anchor guidance, and next briefs.
- Keep evidence mode visible (tool vs. estimate); hand off to `/aaron-seo-geo:create` for production.

## Output

Return inline artifacts by default. Files may be written only when the user explicitly asks and the runtime can write.
