# Runtime Memory

`memory/` is the local operational state used by the protocol layer. It can contain consent,
creator, customer, campaign, claim, and audit data, so runtime contents are **ignored by Git by
default**.

The tracked files under `memory/templates/` are inert examples. `memory-management` creates live
files from those templates only after the user approves a memory write. The registry event runtime
creates its own `memory/events/`, `memory/projections/`, and canonical registry directories as
needed. The opt-in operational runtime creates metadata-only, non-authoritative run records under
`memory/runs/<run-id>/`; see [`references/runtime-protocol.md`](../references/runtime-protocol.md).
Run events, turn snapshots, save points, and envelopes do not grant registry authority or external-
action approval. They may be deleted under the project's run-evidence retention policy after needed
evidence is exported or expires.

If a project intentionally stores memory in a separate private repository or encrypted backend,
configure that storage explicitly. Do not remove the ignore rule in a public source checkout merely
to persist state.

For a repository that tracked memory before v17, removing the files from the current index does not
erase prior commits. Follow the history-erasure and verification procedure in
[`protocol/memory-management/SKILL.md`](../protocol/memory-management/SKILL.md).
