# Distribution — publishing the plugin to every channel

This repo is the SSOT; it fans out to four distribution channels. Every publisher
is **owner-run, dry-run by default, and driven by the repo's committed state** —
no hardcoded queues, no guessing. The single source of truth for "are we fully
distributed?" is `scripts/registry-status.sh`.

The release has four physical archives. The three Claude-oriented plugin
archives contain the same 120 skills and eight commands with different runtime
ceilings. The fourth is a strict, static Agent Plugins v1 projection:

| Archive | Physical ceiling | Fresh-project effective profile |
|---|---|---|
| Lite | authored workflows, routing, scoring, inline delivery, canonical reads | Lite |
| Pro | Lite plus connectors and saved audits | Lite until Pro is explicitly selected |
| Governed | Pro plus state writes, run/context/controller and workflow/audit loops | Lite until Pro or Governed is explicitly selected |
| Agent Plugins v1 Portable Lite | 120 strict static Agent Skills plus their reachable static references; no commands, hooks, connectors, runtime, or `mcp.json` | Portable Lite static workflows only |

The Governed archive is therefore the backward-compatible **bundle-plugin**
payload without being an opt-in to Governed behavior. A standalone one-folder
skill declares a Lite ceiling and degrades fail-closed when the root runtime is
absent. Package selection is an installer/admin control; logical selection uses
the closed config/environment/runtime surfaces in
[`references/capability-profiles.md`](../references/capability-profiles.md).
Neither changes the eight-command grammar.

Portable Lite is additive and does not change that capability lattice. The
repository root is its authoring source, **not** an Agent Plugins install root.
The release builder generates the required flat `skills/<name>/` package and
strict frontmatter without adding a committed mirror. Install the extracted
`aaron-marketing-skills-19.2.0-agent-plugin-v1-lite.tar.gz` directory; see the
exact [Agent Plugins v1 package and capability
boundary](agent-plugins-v1.md).

The standalone manifest names only capabilities physically supported by the
one-folder payload: `authored-workflows`, `inline-delivery`, and
`canonical-state-read`. It does not claim `deterministic-scoring`, audit
persistence, or context planning. Auditor folders include a complete typed
observation fallback, but without the root scorer and validator they must return
`NOT_SCORED/UNDECIDED` and cannot persist under `memory/audits/`.

## Host capability projections

The physical `lite|pro|governed` profile and the host capability profile are
orthogonal. The former bounds which deterministic runtimes are present; the
latter selects how the installed host discovers routes, references, and
connectors. The typed source is
[`host-capability-profiles.json`](../references/host-capability-profiles.json).

| Host profile | Compatible payload | Routing surface | Generated routing files |
|---|---|---|---|
| `claude-code-plugin-host` | plugin/repository | eight slash commands | none; `commands/` remains authoritative |
| `generic-shared-root-host` | plugin/repository | eight router-skill facades | `router-facades/<discipline>/SKILL.md` plus a typed sidecar manifest |
| `standalone-skill-host` | one-folder standalone skill | direct skill invocation | none |
| `agent-plugins-v1` | Portable Lite Agent Plugin | direct Skill discovery | exactly 120 immediate `skills/<name>/SKILL.md` directories |
| `hermes-bot-host` (roster-projection-only) | `bot-roster` output of `generate-bot-projections.py` | named-bot roster (8 bots, handoff by @mention) | 8 Hermes profile-distribution bundles (`hermes/<bot>/`) |
| `grok-bot-host` (roster-projection-only) | `bot-roster` output of `generate-bot-projections.py` | named-bot roster (8 bots, handoff by @mention) | `grok/bot-cards.md`, `enable-lists.md`, `setup-checklist.md` |

The two `*-bot-host` rows are declared in the separate
[`references/bot-roster-profiles.json`](../references/bot-roster-profiles.json)
catalog (`context_assembly: excluded`), not in `host-capability-profiles.json`:
they describe generated deployment surfaces only and never enter
`build-distribution.py` payload selection, prompt/context assembly, or the
certified resolver chain.

Every plugin host projection, at every physical profile, ships the typed host,
prompt, and context-module catalogs, `context-profile-resolver.py`, and the
compact `policy-kernel.md`. This is model/control-plane support data, not a
second Skill inventory. A one-folder standalone distribution deliberately does
not acquire those root files: its complete `SKILL.md` remains the embedded
explicit-policy representation, and its direct-skill semantics stay intact.

The Governed physical profile additionally ships the generated
`references/skill-capsules/` tree (120 per-skill capsules plus its index) and
both capsule schemas. It also ships `context-assembly.py` and
`context-assembly.schema.json`, which project a verified manifest into separate
controller, model, tool, and deferred resource sets. The resolver selects a
capsule only for the typed lean prompt representation; balanced keeps the
complete business Skill while replacing repeated shared policy with the kernel,
and explicit keeps both complete representations. Capsules are
reference/control artifacts, never `SKILL.md` files: they are absent from every
Skill catalog and do not change the canonical count of 120. Lite and Pro omit
the capsule tree and the assembly runtime. Compact-profile certificates remain
evaluation artifacts only: because the package does not yet carry complete
paired evidence for trusted revalidation or a signed release attestation, every
distribution build and manifest verification rejects non-empty
`certified_bindings`. Production therefore remains `explicit`-only.

Build an explicit generic-host projection with:

```bash
python3 scripts/build-distribution.py \
  --plugin --profile lite \
  --host-profile generic-shared-root-host \
  --output /private/path/aaron-generic-host
```

The generic projection removes the unsupported command tree and sets
`.claude-plugin/plugin.json.commands` to an empty list while preserving its
exact 120 canonical business-skill declarations. It then generates eight
non-canonical routing helpers: Narrative, SEO/GEO, Social, Email, Paid Ads,
Influencer, Launch, and Protocol. There is deliberately no overlapping `auto`
facade: these eight groups partition all 120 targets exactly once. A
cross-discipline or ambiguous request stops with candidates for user selection.

[`router-facade-sidecar.schema.json`](../references/router-facade-sidecar.schema.json)
defines `router-facades/sidecar-manifest.json`. The sidecar binds the selected
host-profile digest, system-catalog digest, all eight generated facade hashes,
and all 120 target names, paths, phases, and source hashes. The distribution
manifest binds the sidecar again. A missing, duplicate, unknown, stale, or
multiply covered target fails the build. Facades carry
`metadata.class: router` and `canonical_business_skill: false`; they are not
added to `system-catalog.json`, `.claude-plugin/plugin.json.skills`,
`skills.sh.json`, registry publication queues, or the canonical 120 count.

Omitting `--host-profile` preserves existing behavior: plugin builds select
`claude-code-plugin-host`; `--skill` builds select `standalone-skill-host`.
An incompatible combination fails closed. Manifest 1.2 records the selected
host profile and surfaces; read-only verification remains compatible with
legacy manifest 1.0 and physical-profile manifest 1.1.

### Bot roster deployment (Grok Bot / Hermes Bot Mode)

Named-bot hosts consume a fifth, separately generated surface — never a
committed tree and never a `build-distribution.py` payload:

```bash
python3 scripts/generate-bot-projections.py --output /private/path/aaron-bot-roster
```

That command derives the 8-bot roster (7 discipline bots plus
`aaron-chief-of-staff`, which owns the 8 protocol skills and the routing table)
from `references/system-catalog.json`, covering the 120 skills exactly once. It
writes 8 self-contained Hermes profile-distribution bundles (`distribution.yaml`,
generated `SOUL.md`, Portable-Lite-projected `skills/`, static reference
closure, hash-bound manifest) plus the Grok Bot cards, per-bot enable lists,
and setup checklist. Degradation is identical in spirit to Portable Lite and is
stamped into every bundle: no connectors, `mcp.json`, cron, hooks, or
deterministic runtimes; auditors return `NOT_SCORED`; registry and
durable-memory work is propose-only with owner-run acceptance; links to skills
owned by another bot redirect to the bundle boundary and hand off by name.
Deployment steps, host caveats (including Grok Bot's shared cloud computer),
and the owner-run smoke backlog live in
[agent-compatibility.md](agent-compatibility.md#named-bot-roster-deployment-grok-bot--hermes-bot-mode).

Build the complete release-asset set with one command. The builder exports the
exact Git object into a private directory, builds all three runtime profiles
plus the Portable Lite projection from that export, creates four canonical
archives, safely unpacks each archive, and verifies its
manifest/profile/provenance before installing the output directory:

```bash
python3 scripts/build-release-assets.py \
  --source-repo /path/to/aaron-marketing-skills \
  --source-repository aaron-he-zhu/aaron-marketing-skills \
  --source-commit <exact-40-hex-release-commit> \
  --version 19.2.0 \
  --output /private/path/v19.2.0-release-assets
```

Build and strictly validate the standalone Agent Plugins projection during
development with:

```bash
python3 scripts/build-distribution.py \
  --agent-plugin --profile portable-lite \
  --output /private/path/aaron-agent-plugin
python3 scripts/validate-agent-plugin.py \
  /private/path/aaron-agent-plugin
python3 scripts/build-distribution.py \
  --verify-manifest /private/path/aaron-agent-plugin \
  --profile portable-lite
```

The dedicated validator checks `plugin.json`, all 120 strict Skills and links,
filesystem containment, forbidden executable/MCP surfaces, the projection, and
the complete distribution manifest. The last command independently rechecks
the manifest and expected profile; add `--source-repository owner/repo` and
`--source-commit <40-or-64-hex-object-id>` for an exact provenance match. Build
only into an untracked output directory outside the repository. Never commit a
generated root `skills/` mirror.

Bare `--plugin` is a deprecated Governed-ceiling alias through v20; release
automation must use `--profile`. The `publish-package.sh --from-build` channel
publishes that Governed physical ceiling. An optional `--slim-frontmatter`
strips only publishing-card keys (`slug`, `displayName`, `summary`) while
preserving routing and host-extension metadata.

Every built payload contains `distribution-manifest.json`: one SHA-256, byte
count, and mode for every shipped file plus an aggregate hash. The builder
rejects symbolic links, special files, and multiply linked regular files in
both source inputs and output, then immediately verifies the completed payload.
Verify an existing payload without rebuilding it with
`python3 scripts/build-distribution.py --verify-manifest <dir>`.

The manifest also binds `profile`, `capability_ceiling`, resolved capabilities,
the catalog and profile-definition hashes, package budget, and optional pinned
repository/commit provenance. `build-release-assets.py` emits the fixed
`aaron-marketing-skills-19.2.0-{lite,pro,governed}.tar.gz` runtime archives,
`aaron-marketing-skills-19.2.0-agent-plugin-v1-lite.tar.gz`, `SHA256SUMS`, and
the machine-readable `release-assets.json` ledger defined by
[`release-assets.schema.json`](../references/release-assets.schema.json).
Archive paths are sorted under a fixed root; timestamps and owner fields are
zeroed; modes are normalized; and the gzip header has a zero timestamp plus a
stable OS byte. Links, special files, path traversal, unexpected output files,
and a payload that differs from a fresh build of the exact source commit all
fail closed. The checksum file covers all four archives; the ledger records
their bytes, digests, distribution-manifest digests, profile-definition
digests, and source identity.

For a release candidate, run the one command twice into two new directories and
require all six files to be byte-identical: four archives, `SHA256SUMS`, and
`release-assets.json`. Existing output is verified
read-only with the same exact source identity by replacing `--output <dir>` with
`--verify <dir>`. Never repackage one profile or projection by deleting files
from another.

To stay inside the Governed hard ceiling, that archive replaces the verbose
`references/skill-contracts/` tree with the deterministic
`references/skill-contracts.pack.json.gz` derived output. The context resolver
exposes the same 121 logical contract records only after bounded decompression
and exact per-record plus aggregate hash verification. The source repository
keeps the expanded generated tree for review and CI; do not hand-edit either
representation.

Every release-time **live** mutation entrypoint (`publish-clawhub.sh`,
`publish-skillhub.sh`, `publish-package.sh`, `publish-registries.sh`,
`sync-about.sh`, and `sync-family.sh`) requires a completely clean tree,
successfully refreshes `origin/main`, and proves HEAD is reachable from it.
For v19 and later it also validates the private engineering receipt together
with its exact maturity report and original raw semantic-evidence chain,
immutable final tag, non-draft GitHub Release, exact six downloaded release
assets, and a successful owner-run release-validation workflow on the same
commit. These private inputs are read locally and never uploaded. The
registry parent passes a commit/receipt-bound gate token to its children so this
expensive read-only verification runs once without weakening direct
per-publisher calls.
Receipt issuance and `create-github-release.py --live` always enforce the
24-hour current-freshness gate. A later publisher resume first proves the
immutable final tag, non-draft Release, exact six downloaded assets, and owner
workflow, and only then internally selects the explicit
`--post-release-continuation` verifier mode. That mode relaxes only the
wall-clock-since-issuance check: issuance-time 24-hour freshness plus every
receipt, report, raw-chain, tool, policy, source, commit, and version binding
still must pass. Continuation is bounded by the committed semantic policy
(`maximum_age_days`, currently 30); it is not a release-creation option or an
independent authorization flag. If that policy window expires, collect fresh
provider evidence against the same immutable release commit and issue a new
private report/receipt before resuming.
The origin itself must be a canonical `github.com` HTTPS, SSH, or scp URL;
lookalike hosts, local paths, non-HTTPS web URLs, and Git `insteadOf` rewrites
fail closed. The fetch uses that already-validated literal URL rather than
re-resolving the mutable `origin` name, then rechecks the origin/rewrite
configuration before returning one indivisible `<owner>/<repo>, commit`
identity. Every live entrypoint consumes only that tuple; the registry
orchestrator additionally requires each independently gated child publisher
to match the parent's exact tuple, so an origin switch cannot splice repo A's
verified bytes onto repo B's label or resume state.
Per-skill publishers export that exact Git commit into a private temporary
source tree, build from the export, bind `<owner>/<repo>@<commit>` into the
manifest, verify it again, and only then hand the isolated payload to the
registry. `publish-package.sh --from-build --live` follows the same pinned,
verified build path and is the only allowed live package mode; a bare `--live`
fails closed.
`sync-about.sh --live` reads `.github/repo-about.json` only from that private
commit export, and `sync-family.sh --live` likewise reads its plugin manifest
and every benchmark/reference source only from the export. A worktree edit that
races after the release gate therefore cannot enter any live projection.
Dry-runs remain previews and do not apply the live clean-tree gate.

## Channels

| Channel | What ships | Tool | Cadence |
|---------|-----------|------|---------|
| Downstream repo family (15 repos) | benchmark mirrors + signpost READMEs | [`sync-family.sh`](../scripts/sync-family.sh) | release |
| SkillHub.cn | 120 skills (per-skill, 中文 community) | [`publish-registries.sh`](../scripts/publish-registries.sh) → `publish-skillhub.sh` | release / on-change |
| ClawHub — skills | 120 skills (per-skill, relicensed MIT-0) | [`publish-registries.sh`](../scripts/publish-registries.sh) → `publish-clawhub.sh` | release / on-change |
| ClawHub — bundle-plugin | the whole plugin as one installable package | [`publish-package.sh`](../scripts/publish-package.sh) | release |

`skills.sh` / Hermes / other SKILL.md hosts are **pull-based** (they read `.claude-plugin/plugin.json`); no publish step.

## The one command that tells the truth

```bash
bash scripts/registry-status.sh          # per-skill alignment matrix + package version
bash scripts/registry-status.sh --json   # machine-readable (drives the publisher)
bash scripts/registry-status.sh --require-current # release gate: canonical 120/120 on both + package
```

JSON snapshots bind the canonical 120 unique skill/slug set to an exact
repository, bundle version, and commit. `publish-registries.sh --from-json`
rejects truncated, duplicated, hand-edited, cross-repository, or cross-commit
snapshots. Its private resume file and every done entry are commit-scoped, so a
done marker from older source cannot skip a registry that is behind on the
current commit. Done markers are consulted only with an explicit reused
`--from-json` snapshot; a fresh remote behind-set always wins and republishes.
Every clean live pass finishes by rerunning
`registry-status.sh --require-current --platform <selected-scope>`; only quota
deferral exits 8 before that final truth gate. Bare `--require-current` checks
both registries and the package.

Prints, for every manifest skill, `repo` vs `ClawHub` vs `SkillHub` published version, a per-platform current/stale/missing summary, and the bundle-plugin package version. Read-only — it never publishes.

## Release-only gates

v19 is an **engineering-validated** formal release. Repository CI verifies code,
contracts, generators, all 120 paths, and reproducible profile packages. The
owner-local current-source real-provider run and five-dimension maturity checker
verify the exact RC before a private `engineering-validation-v19` receipt is
issued. That provider run invokes real models, but it runs the repository's
simulated semantic fixtures. It is engineering evidence, not real-project or
customer-outcome evidence.

First perform the narrow release transaction and generated-surface checks:

```bash
python3 scripts/bump-release.py \
  --to X.Y.Z --date YYYY-MM-DD --align-all-skills
python3 scripts/bump-release.py \
  --to X.Y.Z --date YYYY-MM-DD --align-all-skills --write
python3 scripts/generate-release-surfaces.py --write
python3 scripts/generate-release-surfaces.py --check
bash scripts/check-versions.sh --release-all-current
```

Run the full release validation, current-source real-provider engineering
maturity gate, and the two-build comparison for Lite, Pro, Governed, and Agent
Plugins v1 Portable Lite. Re-run
all generator `--write` commands and require a zero diff, then commit that
frozen tree as the release candidate. Issue the private engineering receipt
against that exact clean commit:

```bash
RC_NAME="19.2.0-rc.1"
python3 scripts/issue-engineering-release-receipt.py \
  --root "$PWD" \
  --semantic-evidence-run-id "<fresh-current-source-run-uuid>" \
  --evidence-root "/private/project-root" \
  --release-candidate "$RC_NAME" \
  --owner-authorization "release-v19-without-real-project-outcomes" \
  --maturity-report-output "/private/path/v19-engineering-maturity-report.json" \
  --output "/private/path/v19-engineering-release-receipt.json"
```

The issuer directly runs the current maturity audit and, in the same invocation,
writes both the exact private report and its receipt outside the repository as
distinct O_EXCL/no-follow mode-0600 files. The receipt hashes the actual report
bytes and binds the current
issuer/verifier/checker/rubric/policy bytes, real execution, distinct judge,
complete 24-case smoke cohort, all five 100/100 maturity dimensions, and
P19/P20/H20. Keep both outputs private and never overwrite them; export
the complete three-part verification bundle before any live release or
distribution command:

```bash
export AARON_RELEASE_RECEIPT="/private/path/v19-engineering-release-receipt.json"
export AARON_RELEASE_MATURITY_REPORT="/private/path/v19-engineering-maturity-report.json"
export AARON_RELEASE_EVIDENCE_ROOT="/absolute/private/project-root"
python3 scripts/verify-release-receipt.py "$AARON_RELEASE_RECEIPT" \
  --source-commit "$(git rev-parse --verify 'HEAD^{commit}')" \
  --release-version 19.2.0 \
  --required-gate engineering-validation-v19 \
  --maturity-report "$AARON_RELEASE_MATURITY_REPORT" \
  --evidence-root "$AARON_RELEASE_EVIDENCE_ROOT"
```

The fast verifier replays the current semantic verifier over the original
event chain, then matches that result to both the exact report bytes and
receipt. The evidence root may be a real directory outside the repository. It
may instead be the repository's absolute root only when the bound
`memory/runs/<run-id>` directory is Git-ignored and wholly untracked. The
receipt, report, and raw evidence remain private local inputs. Never upload
them. Any source change invalidates the binding and requires a fresh
provider run, maturity audit, assets, report, and receipt.

## Post-release Governed promotion gate

Real-project outcomes are **unvalidated at v19 release time**. Governed ships as
an explicitly selectable capability ceiling, but capability availability is
not evidence of better outcomes and does not validate Governed as the default.
After release, complete the full Governed-promotion evidence set against the
exact released source:

- the same minimum 14 exact-source pilots: at least 2 per discipline;
- 70 randomized paired Lite/Governed projects: 10 per discipline, with the
  required single/multi/cross-discipline mix and two distinct blind reviewers;
- 28 shadow projects: 4 per discipline, including trace and interruption
  recovery observations.

Keep this material private under the same no-PII, pseudonymous, owner-attested
rules and verify it separately:

```bash
RELEASE_COMMIT="<exact-40-hex-v19-release-commit>"
RC_NAME="19.2.0-rc.1"
python3 scripts/verify-profile-outcomes.py \
  /private/path/v19-governed-promotion-outcomes.json \
  --stage governed-promotion \
  --source-commit "$RELEASE_COMMIT" \
  --release-candidate "$RC_NAME" \
  --evidence-manifest /private/path/v19-promotion-evidence-manifest.json \
  --receipt /private/path/v19-governed-promotion-receipt.json \
  --json
```

This stage enforces paired quality/efficiency/escalation, universal safety,
Governed trace/recovery, cost ceilings, randomized-order balance, and the
complete cohort. It also reruns every `release-pilot` rule on the pilot subset.
The `release-pilot` stage and `profile-pilots-v19` receipt name remain available
for compatibility and incremental cohort checking, but neither authorizes a
release. Only the complete 14 pilot + 70 paired + 28 shadow cohort validates
Governed outcome claims or a future default-profile promotion. Until it passes,
Lite remains the fresh-project default. A failed or missing promotion cohort
does not retroactively invalidate the engineering-validated, Lite-default
package.

## Release-time distribution (the full push→distribution runbook, in order)

Validated end-to-end at v18.0.0 (2026-07-13/14). Every step is resumable: a killed
session loses at most one in-flight skill — re-run the same command.

1. **Gate**: refresh/rebase deliberately, freeze one clean RC commit, pass the exact 120/120 version and complete local validation gates, run the current-source real-provider engineering-maturity gate, retain the original raw evidence root, issue the private maturity report plus engineering release receipt, and build two byte-identical release-asset sets against that exact commit.
2. **Push and remote validation**: push the exact RC ref → require its ordinary PR CI → owner-dispatch release validation for that already-pushed ref/commit → integrate through the reviewed default-branch path without changing the RC tree. The release-validation workflow rejects a missing or differently resolved remote ref. The RC commit must remain reachable from refreshed `origin/main`; do not squash or rebase it during integration.
3. **Release**: preview with `python3 scripts/create-github-release.py`, then run `python3 scripts/create-github-release.py --live --receipt "$AARON_RELEASE_RECEIPT" --maturity-report "$AARON_RELEASE_MATURITY_REPORT" --evidence-root "$AARON_RELEASE_EVIDENCE_ROOT" --asset-dir /private/path/v19.2.0-release-assets`. The owner-run command rapidly revalidates the private three-part evidence bundle and original semantic chain, then rechecks the exact six assets, green release workflow, clean/main-reachable source, annotated tag, `VERSIONS.md` notes, and downloaded GitHub assets. It never uploads the private inputs, resumes a same-commit tag safely, and treats an existing release as read-only; it never moves a tag or replaces assets.
4. **About**: `bash scripts/sync-about.sh` → review → `--live` — projects `.github/repo-about.json` onto the GitHub sidebar. *This step was silently skipped at v18.0.0 and the About kept advertising the previous release's framework names — it is part of the ritual, not an extra.*
5. **Family prerequisites** (only when the release renamed/reshaped a family repo): rename the mirror first, then manually reconcile any `ids`-mode mirror's content (README + standard file + CHANGELOG + CITATION) — `ids` targets are verify-only and never auto-pushed.
6. **Family**: `bash scripts/sync-family.sh` → review → `--live` → re-run the dry-run until all 15 report ✓.
7. **Package**: `bash scripts/publish-package.sh --from-build` → review → `bash scripts/publish-package.sh --from-build --live`. This publishes the Governed-ceiling package whose fresh logical default remains Lite. On a transport error after upload the script accepts success only when `package inspect --json` returns the exact source repository/commit and the remotely served distribution manifest has the attempted build's `files_sha256`; an older CLI without those fields fails closed.
8. **Registries**: `bash scripts/registry-status.sh` (parallel by default, ~2–4 min) → `bash scripts/publish-registries.sh` → review → `bash scripts/publish-registries.sh --live --parallel` — publishes **only the behind-set**; the two platforms run concurrently. **Exit 8 = SkillHub quota deferrals** (see the quota box below): finish the remainder the next day with `bash scripts/publish-registries.sh --live skillhub`.
9. **Verify**: `bash scripts/registry-status.sh --require-current` — canonical 120/120 current on both + package current, with a non-zero exit on any drift — plus the release page, four archive manifests (including the strict 120/120 Portable Lite projection), About sidebar, 15 family targets, and installed-profile diagnostics. Client UI/install smokes remain a non-blocking client-verification backlog until recorded in [`agent-compatibility.md`](agent-compatibility.md); each `Pending` row blocks a client-verified claim, not release of the schema- and repository-validator-conformant archive.

## Rollback and interrupted rollout

Profile rollback is non-destructive. Selecting Lite or Pro stops higher-profile
mechanisms but never removes registries, projections, audits, memory, context
manifests, or run evidence. Before replacing a runtime package, finish or abort
its active runs with that same pinned runtime. In particular, pre-v19
nonterminal runs must be closed by the pre-v19 runtime; v19 returns
`LEGACY_RUN_BLOCKED` and will not append a terminal event for them.

Use this decision order:

1. **Before tag/release** — stop, fix the RC, rerun current-source provider and
   maturity validation, rebuild all three runtime profiles plus Portable Lite
   twice, retain the new raw
   evidence root, issue a fresh private maturity report and engineering release
   receipt, and create a new RC commit.
2. **After release but before live distribution** — pause all live scripts.
   Keep the published tag/assets immutable; correct the defect with a new patch
   release rather than moving the tag or replacing assets in place.
3. **During downstream distribution** — stop at the current channel, record
   which surfaces are current, and rerun dry-run/status commands. Publishers are
   version-aware and resumable; do not force the remaining queue.
4. **After users received the release** — for an operational issue, an admin
   may select a lower logical profile or reinstall a verified lower-ceiling
   archive while preserving state read-only. For a code or safety defect, ship
   a new patch from a known-good commit and redistribute it in the normal order.
   Never reuse a version, overwrite an archive, hand-edit a manifest, or resume
   an active run with a different runtime identity.

If one registry is quota-deferred, the release is only partially distributed.
Report that state explicitly and resume after the window rolls; do not call the
release fully distributed until `registry-status.sh`, the package, About, family
repos, and all six release assets agree.

> **SkillHub quota (measured, v18.0.0)**: ~**100 publishes per 24h rolling window,
> account-wide**. Past it, every skill returns 发布频率过高 and *retries keep the
> window hot* — never grind retries against it. `publish-registries.sh` therefore
> stops at `--skillhub-budget` (default 90), retries a rate-limit once, defers the
> skill, and aborts the pass after 2 consecutive deferrals. A 120-skill full
> re-release is by design a **two-day publish**: ~90 on day one, the rest after
> the window rolls. Deferred runs exit 8, not 1. The resumed publisher may reuse
> the original private evidence bundle after 24 hours only because it first
> re-proves the immutable final Release gates and remains inside the committed
> semantic-policy window (currently 30 days). Past that window, rerun the
> real-provider smoke against the same release commit and issue a new report and
> receipt.

## Gotchas (learned the hard way)

- **Verified build, never the worktree, for the package** — `clawhub package publish .` ignores `.gitignore` and would bundle `.git`, local settings, and any stray `.claude/worktrees/` copy. Live `publish-package.sh` requires `--from-build`, exports the committed source privately, builds and verifies the Governed distribution, and uploads only that isolated payload.
- **The manifest must be committed + pushed** before a package publish — `publish-package.sh` uses the shared fail-closed release gate and refuses a dirty tree, a failed `origin/main` refresh, an unreachable HEAD, or a package manifest missing from that exact commit.
- **SkillHub slug**: unprefixed `<name>` is preferred (when the account owns the short slug), else `aaron-<name>`. `validate-skill.sh` accepts both. Legacy `aaron-<name>` records from before a slug switch may linger as orphans (most registries can't delete).
- **SkillHub search recall**: `registry-status.sh` reads SkillHub via fuzzy search, so it can report a false `missing`. The publisher self-corrects — an idempotent publish of an already-current version returns `版本已存在` and counts as in-sync.
- **ClawHub rate limits**: brand-new skills are ~5/hour; **version updates to existing skills are not capped** (measured ~37s/skill wall time — packing + upload dominates, not the 6s spacing). SkillHub's real constraint is the ~100/24h rolling account quota (box above), not burst pacing; the publisher spaces 40s and owns the retry policy (`publish-skillhub.sh --attempts 1` in orchestrated mode, so the two retry layers can no longer multiply into 16 requests per limited skill). Both publishers are resumable via commit-bound state.
- **Session-death resilience**: publishers hold no in-memory state worth saving — behind-set comes from a repository/version/commit-bound canonical status snapshot, done-set from a private repository/version/commit-scoped state file under `$XDG_STATE_HOME` (or `~/.local/state`), and re-publishing an already-current version is a no-op (`版本已存在`). State updates use a lock and atomic replacement; every done key repeats the commit identity, and no shared fixed `/tmp` file is used. After any crash/restart: re-run the same command.
- **ClawHub MIT-0**: per-skill publishes relicense to MIT-0 (`--i-accept-mit0`), broader than the repo's Apache-2.0.
- Requires the `clawhub` + `skillhub` CLIs logged in on the owner machine. **Never CI-automated** — pushes to public registries get a human glance.

> Historical note: `finish-registry-publish.sh` (removed) hard-coded its publish queue, which silently rotted out of date. `publish-registries.sh` computes the queue from live `registry-status.sh` output instead — the queue can no longer drift.
