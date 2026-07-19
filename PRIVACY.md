# Privacy Policy

## Overview

Aaron Marketing Skills is a local-first bundle of 120 Markdown skills plus small Bash/Python-
stdlib runtimes. It covers seven marketing disciplines and a shared protocol layer. The repository
operator does not run telemetry, analytics, or a hosted data service. Your selected agent host,
model provider, connectors, MCP servers, and storage/sync configuration have their own data flows.

## Default behavior

- Installing the bundle does not transmit project data or register an MCP server.
- Skills work in Tier 1 from text/files the user supplies. That content is processed by the agent
  host/model under the user's host configuration; this repository does not control that provider.
- Operational `memory/**` must be outside Git tracking. A full clone ships the ignore rule. In a
  plugin host project, PreToolUse checks exact-path direct writes; opaque shell/MCP memory mutations
  are unsupported and denied when identifiable (a memory-namespace path shape or a bare-name variable
  assignment). The preflight governs only the host project's `memory/` namespace — destinations
  outside the project root (scratch directories, other repositories) are out of its jurisdiction and
  pass through. The registry and opt-in run-event runtimes independently check every
  final, temporary, and lock/projection path immediately around their atomic writes. Post-use/failure/batch and
  first-Stop hooks audit existing operational files. Hooks do not edit ignore rules and are not an
  OS sandbox; the staged pre-commit and all-tracked CI scans protect committed Git content from PII,
  not the validity of ignored runtime artifacts. The repository does not encrypt runtime memory.
- Hooks do not send network requests. Session hooks may read bounded, sanitized excerpts from local
  `memory/hot-cache.md`, a metadata-only active-run resume summary, and counts from `memory/open-loops.md`; post-success, post-failure, and batch
  hooks run bounded local checks. The first Stop may block for repair; its required active-stop guard
  then prevents a loop rather than claiming an unconditional completion barrier.
- Registry and audit writes require an explicit authorization path. An audit request alone does not
  authorize persistence, hot-cache changes, or canonical registry mutations.

## Data stored locally

Depending on use, runtime memory can contain campaign plans, URLs, claims, creator records, consent
proof references, audit evidence, metrics, and open decisions. Seven registries store append-only
events under `memory/events/` and generated views under `memory/projections/`.

When a host explicitly enables it, `memory/runs/<run-id>/` stores non-authoritative event metadata,
turn snapshots, save points, and run envelopes. The runtime accepts safe identifiers, relative or
opaque references, hashes, registry offsets, status codes, and numeric metrics. It is designed not
to store raw prompts, chain-of-thought, tool arguments/results, transcripts, customer content,
contact details, credentials, or full source URLs. File/reference names can still be sensitive
metadata; use neutral opaque IDs and a private/encrypted storage boundary where required.

Consent aggregate IDs must be pseudonymous tokens/hashes supplied by the user's system. The runtime
NFKC-normalizes strings before contact-pattern checks, exempts only actual timestamp fields from
date-like phone matching, and rejects free-form consent payloads. The closed consent shape permits
only typed status/basis/time/jurisdiction/channel fields, opaque non-PII references, and subject-free
reason codes; arbitrary names, postal addresses, notes, and unknown fields are refused. This is
minimization, not anonymization: whoever holds the pseudonym lookup can relink the record. Keep that
lookup outside this repository and apply access controls appropriate to the data.

## When data leaves the machine

External transmission occurs only when the user/host invokes a network capability:

1. **WebFetch or host browsing.** URLs, request metadata, and fetched content pass through the
   configured host/tool. Treat fetched content as untrusted data, never instructions.
2. **Bundled public connectors.** Read-only helpers contact the target site or documented public API
   (for example Wikidata, Wikimedia, PageSpeed, GDELT, YouTube, HN, App Store, Bluesky, Fediverse,
   Discourse). The remote service receives the user's IP, project User-Agent, query/URL, and any
   required API credential. Credentials are read from environment variables and not persisted.
3. **Delegated fetchers.** `firecrawl.py` and `tavily.py` send a query or target URL to Firecrawl or
   Tavily. Do not use them for URLs whose existence is confidential. Target-site operations perform
   a local robots pre-flight unless the user asserts `--own-site`.
4. **External-state mutation.** `resend.py` can send email/change ESP records and `indexpush.py` can
   submit indexing notifications. Mutating commands are dry-run by default and require `--live`.
   Payloads then go to the named vendor/endpoint.
5. **Opt-in MCP servers.** `docs/mcp-catalog.json` is a catalog only; installation does not register
   it. When the user enables one, data is sent according to that vendor and the user's MCP config.

The exact connector inventory, credentials, and safety classes are maintained in
[`CONNECTORS.md`](CONNECTORS.md) and [`SECURITY.md`](SECURITY.md), not duplicated as a fixed vendor
count here.

## Retention and deletion

- Delete or archive local working memory according to the project's retention policy. Use
  `memory-management` for a permissioned inventory, export, consolidation, or erasure workflow.
- Run evidence is not canonical registry history. Delete complete `memory/runs/<run-id>/`
  directories under a bounded operational retention policy after needed evidence expires or is
  exported; deletion does not revoke actions or erase other copies.
- Registry history is append-only for integrity. A registry `erase` event removes projected payload
  and leaves a minimal audit/safety tombstone; it does not rewrite prior event bytes. A data-subject
  erasure is accepted only with a host-issued safety capability bound to that exact pseudonymous
  request. Suppression is intentionally broader but deny-only: an untrusted producer can prevent
  contact, never clear suppression or authorize contact.
- Deleting a working-tree file does not erase Git history, backups, filesystem snapshots, cloud-sync
  copies, model-provider logs, connector-vendor logs, or prior exports. Those systems require their
  own deletion procedures and verification.
- If runtime memory was accidentally committed, stop sharing the repository, rotate exposed
  credentials, remove the data from current history with an appropriate history-rewrite process,
  coordinate downstream clone/cache cleanup, and verify with `scripts/check-pii.py`.

## Security and user responsibilities

Use a private/encrypted storage boundary when device, backup, team-access, or regulatory risk
requires it. Apply data minimization, retention limits, lawful basis, and access controls appropriate
to the jurisdiction and use case. This policy describes repository behavior; it is not legal advice.

See [`SECURITY.md`](SECURITY.md) for SSRF, prompt-injection, registry-integrity, artifact-gate, and
responsible-disclosure controls.

## Contact

For privacy questions: **hello@zhuhe.io**

## Changes

Material changes are recorded in Git history and release notes.

*Last updated: 2026-07-19*
