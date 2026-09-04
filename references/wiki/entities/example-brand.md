---
type: entity
id: AMS-E-001
title: Example brand pointer
status: draft
generated: false
sources:
  - protocol/entity-registry/SKILL.md
  - protocol/entity-registry/references/entity-type-reference.md
  - memory/README.md
stale_after: 2027-03-04
---

# AMS-E-001 · Example brand pointer

This is a **stub**, not a canonical entity. It exists to show the wiki
entity slot. Live brand, product, and sameAs facts belong to
[`entity-registry`](../../../protocol/entity-registry/SKILL.md).

| Field | Wiki value | Owner |
|---|---|---|
| Display name | Example brand (stub) | Wiki annotation only |
| Canonical record | None in this repository | `entity-registry` |
| SameAs / knowledge panel | Do not invent | `entity-registry` + user evidence |
| Working notes | None | `memory/` after authorized write |

## Rule

If a project has a real entity, write it through `entity-registry` with
current user authorization. Link the resulting projection from a later wiki
page if maintainers need a reading aid. Do not copy the record into this
file and treat the copy as truth.
