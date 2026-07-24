# Authoritative Workflow Graph Protocol

Use this protocol when you add or change an inter-skill handoff, a named multi-skill workflow, or a bounded graph exception.

## Authority model

The graph has one authority chain:

1. `references/system-catalog.json` owns the complete 120-skill node inventory and phase ordering.
2. `references/workflow-graph.source.json` owns the shard manifest, node exceptions, terminal declarations, and named execution workflows; its SHA-256-pinned `references/workflow-graph/edges-*.json` shards own every inter-skill edge and edge-level exception.
3. `references/workflow-graph.json` and `docs/workflow-graph.md` are deterministic generated projections.
4. Each skill's `## Next Best Skill` block is checked documentation. It is never imported during normal generation and never becomes authoritative prose.

The initial edge inventory records a one-time explicit import in `bootstrap_provenance`. After that import, edit the relevant edge shard and reindex its digest in the source manifest. `--write` never scrapes prose to make routing decisions. Every manifest and shard stays below the repository's 50 KB single-reference budget, so a consumer can progressively disclose only the edge partition it needs.

## Edge contract

Every edge declares:

- stable `id`, `from`, and `to` identities;
- an execution `type`, including `fan-out` and `join` where concurrency semantics matter;
- a non-empty selection `condition` and concrete `preconditions`;
- required `permissions` and an optional auditor `gate`;
- a bounded `loop_policy`;
- whether the edge must have a matching Markdown declaration; and
- an explicit exception code and reason when normal phase or cycle rules do not apply.

Use `documentation_required: true` for user-facing Next Best Skill routes. The checker enforces both directions: a required source edge must appear in Markdown, and every explicit Markdown target must exist as a required source edge.

## Named workflow contract

A named workflow selects an explicit `edge_ids` subgraph. Its `nodes` field is not enough: the selected edge list prevents unrelated edges between the same skills from silently entering runtime execution.

Each workflow declares one entry, one or more terminals, fan-out branch starts, all-required joins, maximum cycles, a deadline, and event/action/verification/memory/stall budgets. The selected operational topology must be acyclic; bounded rework happens through the outer verification loop rather than an implicit graph cycle.

The initial `product-launch-execution` workflow is a real Product Launch path:

1. `launch-asset-packager` fans out to the RAMP gate, community submission, and media relations.
2. The gate advances to `launch-day-conductor`.
3. `launch-day-conductor`, `community-launch-runner`, and `press-media-relations` all join at `launch-monitor`.
4. Monitoring advances to `launch-retro-analyzer`, the workflow terminal.

All eight selected transitions already exist in their skills' authored Next Best Skill declarations.

## Validation and drift

Run:

```bash
python3 scripts/workflow-graph.py --write
python3 scripts/workflow-graph.py --check
```

`--check` fails for stale generated files, dangling nodes or edges, orphan nodes, undeclared dead ends, workflow-unreachable nodes, selected workflow cycles, illegal unbounded graph cycles, undeclared phase inversions, invalid fan-out/join edges, and Markdown/source drift.

The complete graph may contain remediation cycles only when every internal cycle edge has a bounded policy. A same-discipline move to an earlier phase additionally requires the `documented-bounded-reentry` exception. Do not use an exception merely to silence the checker; its reason must explain the legitimate operational return.

## Change procedure

1. Add or change the edge in the relevant `references/workflow-graph/edges-*.json` shard.
2. Run `python3 scripts/workflow-graph.py --reindex-shards` to refresh the source manifest's count, boundary, and digest metadata.
3. Update the originating skill's `## Next Best Skill` block when `documentation_required` is true.
4. Add explicit exception metadata when a bounded cycle or phase inversion is intentional.
5. If the edge participates in runtime orchestration, add its ID to a named workflow and declare the fan-out or join semantics.
6. Regenerate and run `--check`.
7. Run `python3 -m unittest tests.test_workflow_graph tests.test_workflow_loop` when workflow execution semantics changed.
