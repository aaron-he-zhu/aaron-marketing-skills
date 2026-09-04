# Maintenance Wiki Schema

This file is the **schema and boundary contract** for `references/wiki/`. It is
maintenance-time documentation. It is not a Skill, not a registry, not an
auditor, and not a runtime context module.

**Runtime must not inject wiki.** Controllers, prompt profiles, `/auto` shards,
Skill capsules, `### Runtime Reads` blocks, and distribution allowlists must
not load this tree by default. A human or maintainer may open a page on
purpose. That is lookup, not assembly.

## Directory roles

| Path | Role | Writes |
|---|---|---|
| `SCHEMA.md` | Boundary, field meanings, review rules | Maintainer |
| `index.md` | Catalog of live pages | Maintainer after ingest |
| `log.md` | Chronological ingest / accept / reject ledger | Maintainer |
| `patterns/` | Reusable operating lessons with stable IDs | Maintainer |
| `entities/` | Thin pointers to registry-owned entities | Maintainer (never canonical facts) |
| `frameworks/` | Annotations and reading context only | Maintainer (never scoring SSOT) |
| `skill-evolution-proposal.md` | Proposal checklist / PR template | Maintainer |
| `evolution-pipeline.md` | Trace/Run → wiki → optional Skill PR | Maintainer |
| `okf-terminology.md` | OKF ↔ AMS artifact map | Maintainer |
| `ops-cadence.md` | Weekly / post-Accept lint cadence | Maintainer |
| `examples/` | Dry-run wiki-only patches | Maintainer |

## Who writes and who reviews

- **Writes:** a maintainer compiling an Accept, a Trace/Run lesson, or a
  rejected-proposal record. Ordinary Skills propose; they do not silently
  append wiki pages.
- **Reviews:** a human maintainer before merge. Wiki copy is evidence-backed
  documentation, not an auditor verdict and not a registry event.
- **Does not write:** runtime hooks, connectors, `/auto`, compact prompt
  profiles, or any Skill acting without current user authorization.

## Three layers (do not collapse)

| Layer | Home | What it is | What it is not |
|---|---|---|---|
| **Raw** | `memory/` (live, usually Git-ignored), run events, user exports | Operational residue of a project | Curated doctrine; installable Skills |
| **Wiki** | `references/wiki/` | Curated, cited, reviewable lessons | Canonical brand/offer/consent state; gate math |
| **Skills** | 120 `SKILL.md` packages + shared contract | Installable execution procedures | A dumping ground for campaign notes |

Wiki **sits beside** `memory/`, the seven registries, and `evals/`. It does
not replace them.

## Boundary versus registries and auditors

- **Registries** remain the sole writers of canonical entity, creator, claim,
  consent, launch, channel, and narrative state. A wiki entity page may only
  point at a registry record. It must not mint, mutate, or shadow that record.
- **Auditors** remain the only Skills that may render typed `SHIP`, `FIX`,
  `BLOCK`, or `UNDECIDED`. A wiki page may explain a lesson that led to a
  verdict. It must not re-score, fork a veto ID, or rewrite
  `references/*-benchmark.md` / `references/scoring-semantics.md`.
- **Skill contract** remains the seven-section execution contract. Wiki
  evolution may propose a body clarification. It must not invent an eighth
  required section or a 121st Skill.
- **Paths and slugs** of the existing 120 Skills are frozen by this process.
  A proposal that renames, moves, or re-slugs a Skill is rejected and logged.

## Raw vs Wiki vs Skills — ingest rule

1. Start from **in-repo** evidence: auditor-runbook lessons, CONTRIBUTING /
   evolution notes, checked-in memory templates, eval guidance, or a real
   Accept write-up. Do not invent campaign metrics.
2. Compile one **atomic** wiki patch (one pattern, one log row, or one
  annotation). Cite sources.
3. Only after the wiki pattern exists may a later PR touch a Skill body.
  That later PR must cite the pattern ID. It must not change Skill
  path, directory, URL, or slug.

## OKF-subset frontmatter (pilot)

Wiki pages other than this schema file use YAML frontmatter. Required keys:

| Field | Meaning |
|---|---|
| `type` | `index` · `log` · `pattern` · `entity` · `framework-annotation` · `procedure` · `proposal-template` · `terminology` · `example` |
| `id` | Stable page id (`AMS-P-…`, `AMS-E-…`, `AMS-F-…`, or a named doc id) |
| `title` | Human title |
| `status` | `active` · `draft` · `deprecated` · `rejected` |
| `generated` | `false` for hand-authored pages; `true` only for an explicitly generated view |
| `sources` | List of in-repo paths or quoted repo documents this page compiles |

As applicable:

| Field | Meaning |
|---|---|
| `stale_after` | ISO date when the page must be re-read or marked draft |
| `pattern_id` | For proposals and log rows that cite a pattern |

`generated: true` pages must still name their generator and source. Wiki is
not a second generated Skill tree.

## Runtime exclusion (normative)

The following must remain true:

1. No `### Runtime Reads` bullet may name `references/wiki/`.
2. `references/context-modules.json` must not list a wiki module.
3. `references/distribution-files.json` must not allowlist this tree into a
   plugin or Portable Lite payload. The distribution builder treats
   `references/wiki/` plus `scripts/check-wiki.py` and
   `scripts/check-routing-retrieval.py` as maintenance paths: README may
   name them, but the runtime closure must not copy them.
4. Context assembly defaults (`explicit` / `balanced` / `lean`) must not
   attach wiki pages as model or controller bodies.
5. Adding a page here must not create a 121st installable Skill package.

`scripts/check-wiki.py` enforces these exclusions plus stale / orphan /
frontmatter checks. That script is a maintainer guard, not a Skill.

## Review checklist (every wiki PR)

- [ ] No Skill path, directory, URL, or slug change
- [ ] No new Skill package
- [ ] Sources are in-repo or explicitly user-provided; no invented metrics
- [ ] Pattern IDs are unique
- [ ] Framework pages annotate only; scoring SSOT unchanged
- [ ] Local Markdown links resolve
- [ ] Runtime exclusion still holds
