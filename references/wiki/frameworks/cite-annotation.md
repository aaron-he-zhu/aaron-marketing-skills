---
type: framework-annotation
id: AMS-F-CITE
title: CITE reading context
status: active
generated: false
sources:
  - references/cite-domain-rating.md
  - references/auditor-runbook.md
  - references/scoring-semantics.md
stale_after: 2027-03-04
---

# AMS-F-CITE · reading context

**Authoritative scoring:** [`references/cite-domain-rating.md`](../../cite-domain-rating.md)
and [`references/scoring-semantics.md`](../../scoring-semantics.md).
**Gate:** `domain-authority-auditor`.

This page does **not** fork CITE’s 40 items or vetoes (`CITE-T03`,
`CITE-T05`, `CITE-T09`). CITE is citation-trust, not a backlink-only score
and not a CORE-EEAT page-quality substitute.

## Why the annotation exists

Maintainers sometimes collapse CITE into “domain rating.” The benchmark is
peer-relative citation trust. Offsite profiling stays on
`offsite-signal-analyzer`; this annotation must not move that work.

## What to read first

1. The CITE benchmark
2. The auditor runbook
3. This page only for the “not backlinks-only” reminder
