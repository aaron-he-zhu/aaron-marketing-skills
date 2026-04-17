# State Model

Plan C standardizes where reusable project state belongs. All state follows a three-tier temperature model with automatic lifecycle management.

## Temperature Tiers

### HOT — `memory/hot-cache.md`

- Capacity: 80 lines max
- Loaded automatically by SessionStart hook every session
- Content: project goals, hero keywords (max 10), primary competitors (max 5), active veto items, unresolved open loops from `memory/open-loops.md`
- Promotion trigger: finding referenced by 2 or more skills, or mentioned in 2 or more consecutive sessions
- Demotion trigger: 30 days unreferenced — move entry out of hot-cache.md, content remains in its WARM file

### WARM — `memory/<category>/<skill>/`

- Capacity: 200 lines per file
- Loaded on demand when a skill matches the topic
- Paths follow the Durable State definitions below
- Promotion trigger: referenced 3 or more times within 7 days — extract core conclusion (max 3 lines) to HOT
- Demotion trigger: 90 days unreferenced — move file to `memory/archive/` with date prefix `YYYY-MM-DD-`

### WIKI Compilation View — `memory/wiki/`

- Nature: read-only compiled index and synthesis of WARM files — a derived layer, not an independent temperature tier
- Project isolation: `memory/wiki/<project>/index.md` partitioned by hot-cache `project` field; no `project` field = global index only
- Auto-loaded: SessionStart loads the current project's `index.md` (skips silently if absent)
- Auto-refreshed: PostToolUse silently updates `index.md` after any WARM file write (low risk — fully rebuildable)
- **Sole writer**: `memory-management` owns all wiki writes semantically. For performance, two narrowly-scoped auto-refresh operations are delegated to PostToolUse and Stop hooks (updating `memory/wiki/index.md` and `memory/wiki/log.md`). These hooks act on behalf of `memory-management` and MUST use the schema documented in [memory-management SKILL.md §Wiki Layer](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/memory-management/SKILL.md). Any wiki-compiled page (entity/keyword/topic) still requires explicit `memory-management` invocation.
- Rollback: delete `memory/wiki/` to return to pre-wiki behavior with zero side effects
- Does not participate in promotion/demotion lifecycle
- Index fields are split into **precise** (score, status, next_action, mtime — extracted directly) and **best-effort** (summary — LLM inferred)
- 健康度 mapping: score ≥80 → 良好, 60-79 → 需改进, <60 → 紧急, no score → —

Capacity rules:

| File | Limit |
|------|-------|
| Project-level `index.md` | 200 lines |
| Global `index.md` | 300 lines |
| Changelog (index bottom) | 5 entries (older entries move to `log.md` in Phase 2) |
| `log.md` (Phase 2) | 500 lines; overflow archived to `log-archive/YYYY.md` |
| Compiled pages (Phase 2) | 200 lines per page |

WARM file frontmatter optional extension:

```yaml
project: acme-campaign-q2   # Optional. Tags file to a project for wiki isolation
```

If hot-cache declares an active project but the WARM file lacks a `project` field, `memory-management` auto-tags it during ingest.

Compiled pages (Phase 2) use source hashing for freshness verification:

```yaml
---
name: competitor-acme-corp
type: entity           # entity | keyword | topic | comparison | synthesis
project: acme-campaign-q2
sources:
  - path: memory/research/competitors/acme.md
    hash: a1b2c3d4     # First 8 chars of SHA-256 of file content
  - path: memory/audits/domain/acme-cite.md
    hash: e5f6a7b8
last_compiled: 2026-04-05
---
```

Log timeline (Phase 2): `memory/wiki/log.md` — append-only record of ingest, query, and lint operations. 500-line limit; overflow archived annually to `memory/wiki/log-archive/YYYY.md`. Parseable: `grep "^## \[" memory/wiki/log.md | tail -5`

Contradiction reconciliation (Phase 2): each resolution tagged `confidence: HIGH | MEDIUM | LOW`. LOW-confidence resolutions marked `[待确认]` in compiled pages; lint reminds until user confirms.

Terminal architecture (Phase 3): when wiki compiled pages fully cover a WARM category, those WARM files become retirement candidates. Use `wiki-lint --retire-preview` to list candidates (dry-run only). After user confirmation, retired WARM files move to COLD (`memory/archive/YYYY-MM-DD-filename.md`). The terminal model is HOT / WIKI / COLD — wiki absorbs WARM's role as the primary knowledge layer, with COLD holding raw source files.

> Full specification: [proposal-wiki-layer-v3.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/proposal-wiki-layer-v3.md)

### COLD — `memory/archive/`

- No capacity limit
- Queried only when `memory-management` is explicitly invoked
- Never auto-deleted, only archived
- Filename format: `YYYY-MM-DD-original-filename.md`

### Lifecycle Rules

```
2+ skill references within 7 days     → WARM promotes to HOT (extract ≤3 lines)
3+ references within 7 days            → WARM promotes to HOT
30 days unreferenced                   → HOT demotes to WARM
90 days unreferenced                   → WARM demotes to COLD
```

### Dual Truncation Rule

HOT tier is limited to 80 lines AND 25KB (whichever triggers first). Truncation occurs at newline boundaries — no mid-line cuts. If exceeded, the FileChanged hook warns the user.

### Staleness Protocol

| Age | Treatment |
|-----|-----------|
| ≤7 days | Current — use without caveat |
| 8–30 days | Point-in-time — verify against current state before asserting as fact |
| 31–90 days | Stale — flag for review in SessionStart hook |
| >90 days | Archive candidate — recommend archival via memory-management |

## Memory File Frontmatter

Every file in `memory/` SHOULD include YAML frontmatter. Two shapes are valid:

**WARM files** — subject matter state (audits, research, decisions, entities, etc.):

```yaml
---
name: campaign-q2-seo
description: Q2 SEO campaign targeting 50 keywords across 3 verticals
type: project
---
```

Valid `type` values: `project`, `reference`, `decision`, `entity`, `glossary`, `open-loops`, `entity-candidates`

The `description` field enables future semantic search across memory files.

**HOT file** (`memory/hot-cache.md`) — session scope declaration:

```yaml
---
tier: hot
project: acme-q2     # null for global scope; set to a project slug to scope wiki/memory reads
---
```

When `project` is non-null, the SessionStart hook and `memory-management` preferentially load `memory/wiki/<project>/index.md` over the global wiki. Switching projects between sessions = swap this field. See §Project Isolation above.

## Durable State

### `memory/decisions.md`

Store:

- major strategic choices
- accepted tradeoffs
- abandoned directions worth remembering

### `memory/open-loops.md`

Store:

- unresolved blockers
- missing evidence
- follow-up tasks
- risks that should not be forgotten

### `memory/glossary.md`

Store:

- project terminology
- internal acronyms
- shorthand labels
- segment definitions
- historical naming context

### `memory/entities/`

Store:

- canonical names
- sameAs and profile links
- entity type
- topic associations
- disambiguation notes
- knowledge-base status

Only `entity-optimizer` should write canonical records here. Other skills should keep raw entity leads in their own category notes until canonicalization is needed.

### `memory/research/`

Common subfolders:

- `keywords/`
- `competitors/`
- `serp/`
- `content-gaps/`

Store:

- keyword opportunities
- competitor findings
- SERP notes
- content gap summaries

### `memory/content/`

Common subfolders:

- `briefs/`
- `calendar/`
- `published/`

Store:

- content briefs
- approved angles
- meta tag decisions
- schema notes
- refresh plans

### `memory/audits/`

Common subfolders:

- `content/`
- `domain/`
- `technical/`
- `internal-linking/`

Store:

- audit summaries
- veto items
- prioritized fixes
- pass/fail gate decisions

### `memory/monitoring/`

Common subfolders:

- `rank-history/`
- `reports/`
- `alerts/`
- `snapshots/`

Store:

- ranking deltas
- alert history
- backlink changes
- stakeholder reporting summaries
- dated supporting CSV or export files when helpful

## Writing Guidance

When a skill describes state updates, it should:

- prefer summaries over raw dumps
- distinguish facts from assumptions
- note missing data explicitly
- avoid inventing data when tools are unavailable
- keep raw exports beside the dated summary they support

## Ownership

- `memory-management` is the sole executor of WARM → COLD archival operations
- `entity-optimizer` is the sole writer of canonical records in `memory/entities/<name>.md`
- Other skills write entity candidates to `memory/entities/candidates.md` only
- `content-quality-auditor` owns publish-readiness state in `memory/audits/content/`
- `domain-authority-auditor` owns citation-trust state in `memory/audits/domain/`

See [skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md) for the full protocol-layer vs execution-layer behavior matrix.
