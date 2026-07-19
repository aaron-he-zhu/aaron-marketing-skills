# Pi session-tree adapter PoC

This directory is a **disposable feasibility probe**, not a runtime dependency. It tests whether selected Pi session primitives can inform this repository's non-authoritative run protocol without invoking a model, Provider, network operation, real tool, persistent session file, `memory/`, or a truth registry. Importing Pi's public package root does transitively load its `pi-ai` compatibility layer and register/construct built-in Provider objects; the probe does not invoke them.

## Decision

**GO for concept reuse in an isolated eval; NO-GO for production installation or runtime replacement.**

The useful seam is Pi's in-memory session tree: branch selection, `moveTo()`, and `fork()` work as advertised. This adapter can also project a deliberately reduced set of adapter-owned event facsimiles into local runtime event names and can build one synthetic turn snapshot per completed turn before flushing at an adapter save point.

Do not interpret that result as proof that Pi provides this repository's exact turn-snapshot schema, save-point durability, capability sandbox, registry protocol, or recovery guarantees. It does not. The snapshot and event-batch entries here are adapter-owned Pi `custom` entries. All accepted inputs are synthetic facsimiles because this probe never creates an `AgentHarness`.

The shapes deliberately differ from real `AgentEvent` values. In the pinned Pi release, real `turn_start` carries only `type`; `turn_end` carries a message and tool results; and `agent_end` carries messages. This adapter instead requires a caller-controlled `turnId` and rejects those payloads. Pi emits its real `save_point` event after the harness has flushed; this adapter's synthetic `save_point` command triggers its own flush, so the direction of the operation is not equivalent.

## Verified baseline

Verified on **2026-07-19** against primary sources:

| Item | Verified value |
|---|---|
| npm release source (`gitHead`) | [`8dc78834cde4e329284cf505f9e3f99763df5529`](https://github.com/earendil-works/pi/tree/8dc78834cde4e329284cf505f9e3f99763df5529/packages/agent) |
| npm package | [`@earendil-works/pi-agent-core@0.80.10`](https://www.npmjs.com/package/@earendil-works/pi-agent-core/v/0.80.10) |
| Package integrity | `sha512-nwnOR3SuLYGRFfyQm8ri4Nj5VGVAvAM9GuqQd3u7BUQj0d6hmD2F8w7OHAAjThE3CuySIdM+v8E22QJG6/RfCg==` |
| Node engine | `>=22.19.0` |
| Pi AI override | `@earendil-works/pi-ai@0.80.10` |
| Storage used | `InMemorySessionRepo` only |

The npm `gitHead` above is the source provenance for the installed tarball. A separate forward-compatibility observation was made against GitHub `main` at [`3da591ab74ab9ab407e72ed882600b2c851fae21`](https://github.com/earendil-works/pi/tree/3da591ab74ab9ab407e72ed882600b2c851fae21/packages/agent); that later commit is not the provenance of npm `0.80.10`.

The pinned release sources expose the APIs exercised here:

- [`src/index.ts`](https://github.com/earendil-works/pi/blob/8dc78834cde4e329284cf505f9e3f99763df5529/packages/agent/src/index.ts) exports the memory repo and session surface.
- [`memory-repo.ts`](https://github.com/earendil-works/pi/blob/8dc78834cde4e329284cf505f9e3f99763df5529/packages/agent/src/harness/session/memory-repo.ts) implements `create()`, `open()`, and `fork()`.
- [`session.ts`](https://github.com/earendil-works/pi/blob/8dc78834cde4e329284cf505f9e3f99763df5529/packages/agent/src/harness/session/session.ts) implements `getBranch()`, `appendCustomEntry()`, and `moveTo()`.
- [`harness/types.ts`](https://github.com/earendil-works/pi/blob/8dc78834cde4e329284cf505f9e3f99763df5529/packages/agent/src/harness/types.ts) defines the real events and the broader event union.

Pi's direct package has `prepublishOnly` but no `preinstall`, `install`, or `postinstall` hook. Its locked transitive dependency graph is different: `@google/genai@1.52.0` and `protobufjs@7.6.5` are marked `hasInstallScript`. Therefore `.npmrc` sets `ignore-scripts=true`, and every documented install command repeats `--ignore-scripts`. The tests fail if this lockfile fact changes silently.

## Concept mapping

| Pi primitive or event | Adapter behavior | Local runtime concept |
|---|---|---|
| `InMemorySessionRepo` | Process-local session only | Non-authoritative eval state |
| `Session.getBranch()` / `moveTo()` | Select a fully validated historical adapter save-point boundary without deleting alternatives | Selected run ancestry |
| `repo.fork(..., { position: "at" })` | Copy a branch from a fully validated adapter save-point boundary into a new in-memory session | Explicit branch/fork |
| Synthetic `turn_start` + `turn_end` facsimiles | Stage one adapter-owned `aaron.turn_snapshot.v1` custom entry | `turn_started`, `turn_finished`, `turn_snapshot_created` |
| Synthetic `save_point` command | Flush staged snapshots and event projections, then append `aaron.save_point.v1` | `save_point_created` |
| Synthetic `session_tree` facsimile | Stage old/new leaf identifiers in a branch projection | `branch_created` |
| Unknown or capability-bearing event | Throw before staging | Fail closed |

The adapter allowlists only synthetic `agent_start`, `turn_start`, `turn_end`, `save_point`, `session_tree`, and `agent_end` facsimiles. Provider, tool, message-payload, queue, compaction, resource, and future event types are rejected. Accepted envelopes require normal data properties and exact keys; accessors, symbols, non-enumerable fields, and Proxies fail closed before values are read. The persisted projection contains identifiers and event types only, not prompt, message, model, or tool-argument fields. Identifiers remain caller-controlled: the adapter enforces only a character/length policy and cannot determine whether a caller has put secret material in an identifier.

Construction owns an exact `new InMemorySessionRepo()` internally. The public constructor, repo/session injection, public `fromSession`, and a raw session getter are intentionally unavailable. Adapter-owned history is revalidated on hydration for exact schemas, projection hashes, increasing sequence/ordinal values, parent links, save-point cross-references, and a one-to-one ordered mapping between projected completed turns and stored snapshots. `moveTo()` and `forkAt()` reject snapshot, event-batch, malformed, and other non-save-point targets before changing Pi state. Valid plain-data third-party Pi entries are retained; non-plain branch data and malformed or unknown `aaron.*` custom entries fail closed.

## Run the probe

Local execution is manual. Automated execution is limited to the path-isolated
[`pi-agent-poc.yml`](../../.github/workflows/pi-agent-poc.yml) workflow, which runs only when this
directory or that workflow changes. The root `validate-skill.yml` job—including its
credential-free semantic-profile checks—does not install or execute this PoC, so ordinary root CI
does not install its 96-package dependency graph.

Use Node `>=22.19.0` and stay inside this directory:

```bash
npm ci --ignore-scripts --no-audit --no-fund
npm test
```

The tests verify:

- exact versions, integrity-backed lock entries, Node engine, and install-script suppression;
- real Pi `moveTo()` and `fork()` behavior with alternate history preserved;
- exactly one snapshot per turn and no session entries before save-point flush;
- fail-closed handling for unknown, Provider, tool, message-payload, malformed, accessor, and Proxy inputs;
- repo/session encapsulation, immutable caller views, and mutation isolation;
- strict hydration of adapter-owned custom history and preservation of valid plain-data third-party entries;
- rejection of ghost/reordered turn projections and non-save-point move/fork targets;
- fail-fast single-flight behavior for `accept()`, `moveTo()`, and `forkAt()` races;
- sequential and cross-adapter fork-ID collision rejection before Pi can overwrite a repo mapping;
- no observed network/subprocess attempt and no changes beneath synthetic `memory/` or `registries/` sentinels.

The network test starts a child process, installs observation/blocking hooks for `fetch`, `http`, `https`, `net`, and `child_process` before dynamically importing the adapter, and then exercises one turn. This is an observation probe, not a security sandbox or proof that a future dependency graph cannot reach the network by another mechanism.

## Hard boundaries

Keep this as an eval-only PoC:

- Do not add the dependency to the repository root or distribution bundle.
- Do not instantiate `Agent`, `AgentHarness`, `JsonlSessionRepo`, `NodeExecutionEnv`, a model, or a tool, and do not invoke a registered Provider. The public root import already loads/registers built-in Provider modules.
- Do not connect these custom entries to authoritative registry writes.
- Do not treat in-memory flushes as atomic, durable, resumable, or crash-safe.
- Do not accept the full Pi event union without a reviewed schema and capability policy.
- Do not commit `node_modules/`.

The adapter is deliberately single-threaded and uses a fail-fast single-flight guard across every public asynchronous read and mutation. A second read or mutation is rejected while another operation is awaiting Pi, and `pendingMutationCount` also fails during that interval. Caller-supplied fork IDs additionally use a repo-scoped reservation around the uniqueness check and fork, because forked adapters share one repo. These controls prevent inconsistent reads, silent double success, and session-ID map overwrite in the covered process, but the multi-entry save-point flush remains non-atomic, process-local, non-durable, and not crash-recoverable.

The dependency graph installs 96 packages, including Provider SDKs that this probe never invokes. That footprint and the absence of a repository-specific permission boundary are the main reasons production adoption remains **NO-GO**. If the concept stops paying for its maintenance cost, remove `evals/pi-agent-poc/`; the repository's Python-standard-library runtime and all existing distribution surfaces remain unchanged.
