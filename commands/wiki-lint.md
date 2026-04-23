---
name: wiki-lint
description: Run wiki health check — detect contradictions, orphan pages, stale claims, missing pages, and source hash mismatches across wiki and WARM files
argument-hint: "[--fix] [--project <name>] [--retire-preview]"
parameters:
  - name: fix
    type: boolean
    required: false
    description: Auto-resolve contradictions where confidence is HIGH (time-series data). MEDIUM/LOW contradictions still require user confirmation.
  - name: project
    type: string
    required: false
    description: Limit lint to a specific project. If omitted, lints the active project from hot-cache or all projects.
  - name: retire-preview
    type: boolean
    required: false
    description: "Phase 3: List WARM files fully covered by wiki compiled pages as retirement candidates. Does not execute any archival — requires explicit user confirmation."
---

# Wiki Lint Command

> Wiki health check for the [SEO & GEO Skills Library](https://github.com/aaron-he-zhu/seo-geo-claude-skills). Full wiki spec: [references/proposal-wiki-layer-v3.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/proposal-wiki-layer-v3.md)

Scans `memory/wiki/` compiled pages and `memory/` WARM files for inconsistencies, then produces a structured report.

## Usage

```
/seo:wiki-lint
/seo:wiki-lint --project acme-campaign-q2
/seo:wiki-lint --fix
/seo:wiki-lint --retire-preview
```

## Workflow

1. **Discover pages** — Glob `memory/wiki/*.md` (filtered by `--project` if specified) to enumerate all compiled wiki pages.
2. **Build WARM index** — Read all `memory/` WARM files (`*.md`, excluding `wiki/`) to map entity/keyword → source path + current content hash.
3. **Contradiction scan** — For each entity/keyword appearing in two or more pages or WARM files, compare claim values. Tag each conflict HIGH / MEDIUM / LOW per the resolution table below.
4. **Stale claim scan** — For each `sources.hash` entry in a compiled wiki page, recompute `shasum -a 256` on the referenced WARM file and compare. Drift = stale claim.
5. **Orphan detection** — Build an inbound-link index from all wiki pages; flag any page with zero inbound links from other wiki pages.
6. **Missing page detection** — Count entity/keyword mentions across all wiki pages; flag any entity mentioned 3+ times with no dedicated page.
7. **Cross-reference gap detection** — For each pair of pages sharing a topic, confirm both pages link to each other; flag missing reciprocal links.
8. **HOT drift check** — Compare active values in `memory/hot-cache.md` against the current wiki page for each entity/keyword.
9. **Hash recheck** — Re-run the hash comparison from step 4 to catch any file changes during the scan.
10. **Report** — Produce structured output in the format below and append to `memory/wiki/log.md`.

## Checks Performed

| Check | Description | Auto-fixable |
|-------|-------------|-------------|
| **Contradiction** | Two wiki pages or WARM files assert conflicting facts about the same entity/keyword | Only if confidence=HIGH (time-series: use latest value + changelog) |
| **Stale claim** | Wiki page cites a WARM file whose source hash no longer matches current content | Yes (re-compile from source) |
| **Orphan page** | Wiki page with zero inbound links from other wiki pages | No (suggest deletion or linking) |
| **Missing page** | Entity or keyword mentioned 3+ times across wiki pages but has no dedicated page | No (suggest creation) |
| **Missing cross-reference** | Two pages discuss the same topic but don't link to each other | Yes (add link) |
| **HOT drift** | hot-cache.md references an entity/keyword whose wiki page has materially changed | No (suggest HOT update) |
| **Hash mismatch** | Compiled page `sources.hash` differs from current WARM file content hash | Yes (re-compile) |

## Contradiction Resolution

Each resolution is tagged with a confidence level:

- **HIGH**: Time-series data (e.g., DR values) — automatically use latest value, preserve older value as changelog entry
- **MEDIUM**: Judgment calls where evidence is available but ambiguous — LLM proposes resolution, marked `[待确认]` until user confirms
- **LOW**: Insufficient evidence to resolve — flagged for user attention, not auto-resolved even with `--fix`

## Output Format

```markdown
## Wiki Lint Report — [project name] (YYYY-MM-DD)

### Contradictions (N found)
| # | Entity/Keyword | Claim A (source, date) | Claim B (source, date) | Resolution | Confidence |
|---|---------------|----------------------|----------------------|------------|------------|
| 1 | Acme Corp DR | DR 68 (Jan audit) | DR 72 (Mar audit) | Use 72, changelog 68→72 | HIGH |

### Stale Claims (N found)
| # | Wiki Page | Source File | Expected Hash | Actual Hash |
|---|-----------|-------------|--------------|-------------|

### Orphan Pages (N found)
| # | Page | Suggestion |
|---|------|------------|

### Missing Pages (N suggested)
| # | Entity/Keyword | Mention Count | Suggested Type |
|---|---------------|---------------|----------------|

### Missing Cross-References (N found)
| # | Page A | Page B | Shared Topic |
|---|--------|--------|-------------|

### HOT Drift (N found)
| # | Entity/Keyword | HOT Value | Wiki Value | Suggestion |
|---|---------------|-----------|------------|------------|

### Hash Mismatches (N found)
| # | Compiled Page | Source File | Recorded Hash | Actual Hash |
|---|--------------|-------------|--------------|-------------|

### Summary
- Total checks: N
- Issues found: N
- Auto-fixed (--fix): N
- Requires user action: N
```

Results are appended to `memory/wiki/log.md`.
