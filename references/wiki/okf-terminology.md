---
type: terminology
id: AMS-WIKI-OKF
title: OKF Executor / Receipt / Attester map
status: active
generated: false
sources:
  - references/llms-txt-okf.md
  - references/measurement-protocol.md
  - references/auditor-runbook.md
  - references/profile-outcome-receipt.schema.json
  - references/control-artifact.schema.json
  - references/wiki/SCHEMA.md
stale_after: 2027-03-04
---

# OKF terminology map

Pilot map only. It does not change framework IDs, scoring, or the public
`llms.txt` / site-OKF guidance in
[`references/llms-txt-okf.md`](../llms-txt-okf.md).

OKF (Open Knowledge Format) is a Markdown bundle convention. AMS already
has measurement, control, and auditor artifacts. Use these aliases when a
knowledge-bypass page needs OKF-subset fields (`sources`, `generated`,
`status`, `stale_after`).

| OKF role | AMS artifact | What it proves | What it does not prove |
|---|---|---|---|
| **Executor** | A Skill invocation, measurement-protocol test step, or controller run | Who attempted the work and under which contract | That the work was correct or shippable |
| **Receipt** | Profile-outcome receipt, control artifact, operational run event, measurement export bound by provenance | That a named action or checkpoint occurred | A TALE / CORE-EEAT / CITE / ECHO / SEND / ROAS / STAR / RAMP verdict |
| **Attester** | One of the eight auditor-class gates, plus `validate-audit-artifact.py` / typed scorer when an audit is persisted | A typed `SHIP` / `FIX` / `BLOCK` / `UNDECIDED` on stated evidence | Canonical registry mutation; release publication by itself |

## How the roles stay separate

- Executors propose and measure. They do not self-attest a gate.
- Receipts are evidence objects. They are not wiki pages and not Skills.
- Attesters are only the eight named auditors. Wiki annotations are not
  Attesters ([AMS-P-001](patterns/status-is-not-verdict.md)).

## Knowledge-bypass pages

Indexes and runbook wrappers may carry the OKF-subset fields so maintainers
can see origin and freshness. Those fields are documentation metadata.
They must not:

- alter `references/*-benchmark.md` item IDs
- change `references/scoring-semantics.md`
- become Runtime Reads
