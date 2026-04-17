# Glossary

Plain-language definitions for every term this library uses. Keep this page open while you explore the skills.

## Core concepts

**SEO (Search Engine Optimization)**
The practice of improving a page so it ranks higher in Google, Bing, and other traditional search engines. See [README.md](README.md).

**GEO (Generative Engine Optimization)**
The practice of structuring content so AI assistants (ChatGPT, Perplexity, Google AI Overviews) cite it in their answers. See [README.md](README.md).

**CORE-EEAT**
An 80-item content quality framework scored across 8 dimensions. `GEO Score = CORE avg`, `SEO Score = EEAT avg`. See [references/core-eeat-benchmark.md](references/core-eeat-benchmark.md).

**CITE**
A 40-item domain authority framework scored across 4 dimensions (Credibility, Infrastructure, Trust, Endorsement). See [references/cite-domain-rating.md](references/cite-domain-rating.md).

## Quality gates

**Veto item**
A single scoring item that — when failed — blocks publication or authority approval regardless of overall score. CORE-EEAT has three (T04, C01, R10); CITE has three (T03, T05, T09). See [references/core-eeat-benchmark.md](references/core-eeat-benchmark.md) and [references/cite-domain-rating.md](references/cite-domain-rating.md).

**Cap (Critical Fail Cap)**
A ceiling applied to the final score when certain items fail. A cap limits the top score a page or domain can earn until the underlying issue is fixed. See [references/contract-fail-caps.md](references/contract-fail-caps.md).

**Gate verdict**
The auditor's ship/no-ship decision: `SHIP`, `FIX_BEFORE_SHIP`, or `BLOCK`. Driven by veto items, caps, and score thresholds. See [references/auditor-runbook.md](references/auditor-runbook.md).

**Protocol layer**
The four cross-cutting skills that enforce quality across all phases: `content-quality-auditor` (publish gate), `domain-authority-auditor` (citation trust gate), `entity-optimizer` (canonical entity profile), `memory-management` (campaign memory loop). See [references/skill-contract.md](references/skill-contract.md).

## Memory model

**HOT / WARM / COLD tiers**
Three-temperature memory model. HOT is auto-loaded (80 lines, 25KB cap) in `memory/hot-cache.md`. WARM is on-demand under `memory/` subdirectories. COLD is archival under `memory/archive/`. See [references/state-model.md](references/state-model.md).

**Handoff summary**
The structured packet one skill passes to the next: objective, key findings, evidence, open loops, target keyword, content type, completion status (DONE / DONE_WITH_CONCERNS / BLOCKED / NEEDS_INPUT), scores, priority items, content URL. See [references/skill-contract.md](references/skill-contract.md).

## Skills vs. commands

**Skill vs. command**
A *skill* is a markdown capability that auto-activates from a user prompt (e.g., "research keywords for..."). A *command* is invoked explicitly with `/seo:<name>` and runs a deterministic one-shot task. See [README.md](README.md).

## Tool integration

**Tier 1 / 2 / 3 integration**
Tier 1 is zero dependencies — every skill works standalone. Tier 2 adds MCP connectors (Ahrefs, Semrush, GA4, etc.) for richer data. Tier 3 is full toolchain integration with persistent webhooks and two-way sync. See [CONNECTORS.md](CONNECTORS.md).
