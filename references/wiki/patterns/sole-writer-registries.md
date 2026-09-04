---
type: pattern
id: AMS-P-002
title: Sole-writer registries
status: active
generated: false
sources:
  - README.md
  - CONTRIBUTING.md
  - references/skill-contract.md
  - CLAUDE.md
stale_after: 2027-03-04
---

# AMS-P-002 · Sole-writer registries

**Lesson (compiled, not invented):** ordinary Skills propose durable truth;
only the owning registry accepts or transitions canonical state. Gates judge.
Analyzers feed gates. Wiki pages point; they do not become a second ledger.

## In-repo source

README and CLAUDE.md state the sole-writer rule and the split: registries
curate, gates judge. The skill contract requires Skills to propose truth they
do not own.

## When this pattern applies

- A Skill wants to “just update” an entity, claim, consent, or launch record
- A wiki entity stub is being added
- A proposal tries to store canonical facts only in `SKILL.md` or wiki

## Must not

- Mint or mutate registry records from a wiki page
- Let a non-owner Skill write canonical state because a prior turn “already
  approved something”
- Replace `memory/events/` or registry projections with wiki prose
