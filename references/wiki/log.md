---
type: log
id: AMS-WIKI-LOG
title: Wiki ingest and impact ledger
status: active
generated: false
sources:
  - references/wiki/SCHEMA.md
  - references/auditor-runbook.md
  - references/skill-contract.md
  - CONTRIBUTING.md
  - docs/context-engineering.md
  - memory/README.md
stale_after: 2027-03-04
---

# Wiki ingest and impact ledger

Append-only human ledger. One row per ingest, accept, or reject. Do not
invent campaign metrics. Rejected Skill-evolution proposals stay here even
when no Skill file changed.

| Date | Entry | Pattern / page | Disposition | Sources | Notes |
|---|---|---|---|---|---|
| 2026-09-04 | Demo ingest: compile five operating lessons already stated in-repo | AMS-P-001 … AMS-P-005 | accepted | `references/auditor-runbook.md` §4 Status Is Not Verdict; README sole-writer rule; `docs/context-engineering.md` smallest sufficient context; `references/skill-contract.md` evidence + handoff budget; `memory/README.md` seam | No Skill body rewrite. No path/slug change. No fabricated KPIs. |
| 2026-09-04 | Entity stub that only points at `entity-registry` | AMS-E-001 | accepted | `protocol/entity-registry/SKILL.md`; `memory/README.md` | Wiki must not mint canonical entity facts. |
| 2026-09-04 | Framework annotation wrappers (TALE, CORE-EEAT, CITE) | AMS-F-TALE, AMS-F-CORE-EEAT, AMS-F-CITE | accepted | `references/tale-benchmark.md`; `references/core-eeat-benchmark.md`; `references/cite-domain-rating.md`; `references/auditor-runbook.md` | Annotations only. Veto IDs and scoring unchanged. |
| 2026-09-04 | Wiki-only dry-run example (no Skill diff) | `examples/wiki-annotation-dry-run.md` | accepted | `references/wiki/SCHEMA.md`; AMS-P-003 | Demonstrates the proposal rule: wiki patch first, Skill body optional later. |

## Rejected proposals

None yet. When a proposal is rejected, add a row with `Disposition: rejected`,
the pattern ID it cited (or `missing-pattern-id` if it cited none), and the
rule it violated (path/slug change, new Skill, scoring fork, invented
metrics, or missing source).
