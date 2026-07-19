# Session Checkpoint (inert template — copy to memory/session-checkpoint.md)

Machine-readable resume pointer for post-compact / next-session recovery. The
SessionStart hook injects at most the first 40 lines / 8 KB of the live file as
untrusted context, so keep every line short and factual. memory-management
refreshes it after each completed skill handoff and clears it when no work is
in flight. It is a pointer, never canonical truth: registry offsets here are
hints to re-read, not state to trust.

```yaml
updated_at: YYYY-MM-DD
active_skill: <slug or none>
chain_visited: [<slugs already run in this chain — visited-set guard>]
chain_depth: <0-3 automatic handoffs used>
pending_handoff: <next skill slug or none>
pending_handoff_reason: <one line>
registry_offsets: {entities: 0, creators: 0, claims: 0, consent: 0, launches: 0, channels: 0, narrative: 0}
pending_proposals: <count awaiting owner ritual>
last_gate: <framework verdict YYYY-MM-DD or none>
resume_instruction: <the first concrete action on resume, one line>
```
