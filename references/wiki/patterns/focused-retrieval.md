---
type: pattern
id: AMS-P-003
title: Focused retrieval beats exhaustive dumps
status: active
generated: false
sources:
  - docs/context-engineering.md
  - CLAUDE.md
  - evals/README.md
stale_after: 2027-03-04
---

# AMS-P-003 · Focused retrieval beats exhaustive dumps

**Lesson (compiled, not invented):** give the model the smallest sufficient
decision context. A focused set of at most three modules outperforms dumping
the catalog.

## In-repo source

`docs/context-engineering.md` states the operational rule: smallest
sufficient decision context; authority and validation stay in the controller.
CLAUDE.md progressive loading and `/auto` shard limits encode the same
bound. The routing/retrieval suite in `evals/routing-retrieval/` treats
expected Skill sets of size ≤3 as the success shape.

## When this pattern applies

- Choosing Skills for a user intent
- Reviewing a proposal that adds “just in case” Runtime Reads
- Writing retrieval eval cases

## Must not

- Attach this wiki tree to every invocation
- Expand `/auto` from three shards to an exhaustive dump to raise recall
- Add a 121st Skill to make routing “easier”
