<!-- GENERATED FILE: run `python3 scripts/workflow-graph.py --write`; do not edit. -->

# Workflow Graph

The authoritative source is [`references/workflow-graph.source.json`](../references/workflow-graph.source.json). Existing `Next Best Skill` prose is a bidirectionally checked documentation surface, never the authority.
The source manifest pins context-budgeted authoritative edge shards by SHA-256; consumers load only the shards they need.

- Nodes: **120**
- Edges: **376**
- Named workflows: **1**
- Graph digest: `sha256:5313dd3635b163061ca84957c3cc9a1cd49ce2bf883fd7494b2afcea4d9b9990`

## Named Workflows

### product-launch-execution

Package the approved launch, fan out gated execution across launch-day, community, and media lanes, join their evidence in launch monitoring, and close with an outcome retro.

- Entry: `launch-asset-packager`
- Terminals: `launch-retro-analyzer`
- Selected authoritative edges: **8**
- Maximum cycles: 3

- Fan-out from `launch-asset-packager`: community → `community-launch-runner`, execution-gate → `launch-readiness-auditor`, media → `press-media-relations`
- Join `launch-lanes-complete` at `launch-monitor` requires `community-launch-runner`, `launch-day-conductor`, `press-media-relations` (all-required).

## Contract

An edge typed `gate` with `gate` bound to its source auditor is a release gate: `audit-evidence` and an independent `execution-approval` are both required before its successor may open. Non-SHIP verdicts remain closed.

`python3 scripts/workflow-graph.py --check` detects projection drift, dangling edges, documentation drift, orphan nodes, unreachable workflow nodes, illegal cycles, undeclared phase inversions, and undeclared dead ends.
