---
type: procedure
id: AMS-WIKI-EVOLUTION
title: Proposal-style skill evolution pipeline
status: active
generated: false
sources:
  - references/wiki/SCHEMA.md
  - CONTRIBUTING.md
  - references/skill-contract.md
  - references/wiki/patterns/focused-retrieval.md
stale_after: 2027-03-04
---

# Trace / Run → wiki patch → optional Skill body PR

Path-safe evolution. The 120 Skill URLs, directories, and slugs stay frozen.

## Flow

```text
Trace or Run evidence (in-repo or authorized project)
        │
        ▼
  wiki patch (one atomic diff, cites or creates a pattern id)
        │
        ├─ rejected → row in log.md (impact ledger) → stop
        │
        ▼
  optional Skill body PR (same pattern id; no path/slug/name change)
        │
        ▼
  human review → merge
```

1. **Trace / Run.** Collect a lesson from auditor-runbook, CONTRIBUTING,
   evals, a checked-in template, or an authorized Accept write-up. Label
   evidence per [AMS-P-004](patterns/evidence-taxonomy.md).
2. **Wiki patch.** One atomic diff: one pattern, one annotation, or one log
   row. Use [skill-evolution-proposal.md](skill-evolution-proposal.md).
3. **Optional Skill PR.** Only after the pattern id exists. Touch the Skill
   body or a non-Skill `references/` annotation. Do not bulk-rewrite
   `SKILL.md` files in the same change.
4. **Reject and record.** A proposal that renames, moves, or re-slugs a
   Skill, adds a 121st Skill, forks scoring, or cites no pattern id is
   rejected. Write the rejection in [log.md](log.md).

## Hard reject rules

- Skill slug, directory, URL, or `name` change
- New installable Skill package
- Wiki added to `### Runtime Reads`, context modules, or distribution
  allowlists
- Replacement of the seven-section contract or the eight auditor gates
- Invented campaign metrics
- More than one atomic concern per proposal

## Atomic diff

“Atomic” means one reviewable claim. Allowed examples:

- add `AMS-P-00N` plus its log row
- annotate one framework wrapper
- later, a single Skill body clarification that cites `AMS-P-00N`

Not atomic: “refresh every auditor SKILL.md and also rename a phase.”
