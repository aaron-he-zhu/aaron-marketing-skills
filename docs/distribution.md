# Distribution — publishing the plugin to every channel

This repo is the SSOT; it fans out to four distribution channels. Every publisher
is **owner-run, dry-run by default, and driven by the repo's committed state** —
no hardcoded queues, no guessing. The single source of truth for "are we fully
distributed?" is `scripts/registry-status.sh`.

The release has three physical plugin archives. Each contains the same 120
skills and eight commands; only the runtime ceiling changes:

| Archive | Physical ceiling | Fresh-project effective profile |
|---|---|---|
| Lite | authored workflows, routing, scoring, inline delivery, canonical reads | Lite |
| Pro | Lite plus connectors and saved audits | Lite until Pro is explicitly selected |
| Governed | Pro plus state writes, run/context/controller and workflow/audit loops | Lite until Pro or Governed is explicitly selected |

The Governed archive is therefore the backward-compatible **bundle-plugin**
payload without being an opt-in to Governed behavior. A standalone one-folder
skill declares a Lite ceiling and degrades fail-closed when the root runtime is
absent. Package selection is an installer/admin control; logical selection uses
the closed config/environment/runtime surfaces in
[`references/capability-profiles.md`](../references/capability-profiles.md).
Neither changes the eight-command grammar.

Build the complete release-asset set with one command. The builder exports the
exact Git object into a private directory, builds all three profiles from that
export, creates canonical archives, safely unpacks each archive, and verifies
its manifest/profile/provenance before installing the output directory:

```bash
python3 scripts/build-release-assets.py \
  --source-repo /path/to/aaron-marketing-skills \
  --source-repository aaron-he-zhu/aaron-marketing-skills \
  --source-commit <exact-40-hex-release-commit> \
  --version 19.0.0 \
  --output /private/path/v19.0.0-release-assets
```

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
repository/commit provenance. `build-release-assets.py` emits fixed
`aaron-marketing-skills-19.0.0-{lite,pro,governed}.tar.gz` names for v19,
`SHA256SUMS`, and the machine-readable `release-assets.json` ledger defined by
[`release-assets.schema.json`](../references/release-assets.schema.json).
Archive paths are sorted under a fixed root; timestamps and owner fields are
zeroed; modes are normalized; and the gzip header has a zero timestamp plus a
stable OS byte. Links, special files, path traversal, unexpected output files,
and a payload that differs from a fresh build of the exact source commit all
fail closed. The checksum file covers the three archives; the ledger records
their bytes, digests, distribution-manifest digests, profile-definition
digests, and source identity.

For a release candidate, run the one command twice into two new directories and
require all five files to be byte-identical. Existing output is verified
read-only with the same exact source identity by replacing `--output <dir>` with
`--verify <dir>`. Never repackage one profile by deleting files from another.

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
For v19 and later it also validates the private outcome receipt, immutable final
tag, non-draft GitHub Release, exact five downloaded release assets, and a
successful owner-run release-validation workflow on the same commit. The
registry parent passes a commit/receipt-bound gate token to its children so this
expensive read-only verification runs once without weakening direct
per-publisher calls.
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

Release candidates have two evidence classes. Repository CI verifies code,
contracts, generators, all 120 paths, and reproducible profile packages.
Private outcome evidence verifies that the profile split works on real work.
Neither substitutes for the other.

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
maturity gate, and the two-build comparison for Lite, Pro, and Governed. Re-run
all generator `--write` commands and require a zero diff, then commit that frozen
tree as the release candidate.

Against that exact candidate commit, collect a pseudonymous, owner-attested
manifest that conforms to
[`profile-outcome-evidence.schema.json`](../references/profile-outcome-evidence.schema.json)
and is bound to the exact release-candidate commit. It must contain real-project
evidence—not semantic fixtures or simulated briefs—for at least:

- 14 pilot projects: 2 in each of the seven disciplines;
- 70 randomized paired Lite/Governed projects: 10 per discipline, with the
  required single/multi/cross-discipline mix and two distinct blind reviewers;
- 28 shadow projects: 4 per discipline, including trace and interruption
  recovery observations.

Keep the manifest, briefs, reviewer material, and project artifacts outside the
repository. The checked manifest is pseudonymous but is still private release
evidence:

```bash
RC_COMMIT="$(git rev-parse --verify 'HEAD^{commit}')"
RC_NAME="19.0.0-rc.1"
python3 scripts/verify-profile-outcomes.py \
  /private/path/v19-profile-outcomes.json \
  --source-commit "$RC_COMMIT" \
  --release-candidate "$RC_NAME" \
  --evidence-manifest /private/path/v19-private-evidence-manifest.json \
  --receipt /private/path/v19-profile-outcome-receipt.json \
  --json
```

The verifier enforces the quality, Lite completion/efficiency/escalation,
universal-safety, Governed trace/recovery, and cost ceilings. Missing, simulated,
duplicated project/brief/evidence identities, unbalanced randomization, an
unmatched private-manifest digest, or failing evidence is a hard stop **before
tag, GitHub release, or any live distributor**. The verifier creates a
project-data-free private receipt bound to the exact RC, evidence digests,
verifier, model, and toolset; it refuses to overwrite a receipt or place one in
the repository. Do not create a synthetic manifest or receipt to unblock a
schedule. Any source change after collection creates a new release-candidate
commit and requires fresh bound evidence; the release tag and all archive
manifests must name the candidate that actually passed. Export
`AARON_RELEASE_RECEIPT=/private/path/v19-profile-outcome-receipt.json` for every
live distribution command.

## Release-time distribution (the full push→distribution runbook, in order)

Validated end-to-end at v18.0.0 (2026-07-13/14). Every step is resumable: a killed
session loses at most one in-flight skill — re-run the same command.

1. **Gate**: pass the private real-outcome check, release validation, engineering-maturity gate, exact 120/120 version check, and two byte-identical release-asset builds against one RC commit.
2. **Push**: clean tree → refresh/rebase deliberately → push the exact RC ref → run release validation for that ref/commit → integrate through the reviewed default-branch path without changing the RC tree. The RC commit must be reachable from refreshed `origin/main`.
3. **Release**: preview with `python3 scripts/create-github-release.py`, then run `python3 scripts/create-github-release.py --live --receipt /private/path/v19-profile-outcome-receipt.json --asset-dir /private/path/v19.0.0-release-assets`. The owner-run command rechecks the receipt, exact five assets, green release workflow, clean/main-reachable source, annotated tag, `VERSIONS.md` notes, and downloaded GitHub assets. It resumes a same-commit tag safely and treats an existing release as read-only; it never moves a tag or replaces assets.
4. **About**: `bash scripts/sync-about.sh` → review → `--live` — projects `.github/repo-about.json` onto the GitHub sidebar. *This step was silently skipped at v18.0.0 and the About kept advertising the previous release's framework names — it is part of the ritual, not an extra.*
5. **Family prerequisites** (only when the release renamed/reshaped a family repo): rename the mirror first, then manually reconcile any `ids`-mode mirror's content (README + standard file + CHANGELOG + CITATION) — `ids` targets are verify-only and never auto-pushed.
6. **Family**: `bash scripts/sync-family.sh` → review → `--live` → re-run the dry-run until all 15 report ✓.
7. **Package**: `bash scripts/publish-package.sh --from-build` → review → `bash scripts/publish-package.sh --from-build --live`. This publishes the Governed-ceiling package whose fresh logical default remains Lite. On a transport error after upload the script accepts success only when `package inspect --json` returns the exact source repository/commit and the remotely served distribution manifest has the attempted build's `files_sha256`; an older CLI without those fields fails closed.
8. **Registries**: `bash scripts/registry-status.sh` (parallel by default, ~2–4 min) → `bash scripts/publish-registries.sh` → review → `bash scripts/publish-registries.sh --live --parallel` — publishes **only the behind-set**; the two platforms run concurrently. **Exit 8 = SkillHub quota deferrals** (see the quota box below): finish the remainder the next day with `bash scripts/publish-registries.sh --live skillhub`.
9. **Verify**: `bash scripts/registry-status.sh --require-current` — canonical 120/120 current on both + package current, with a non-zero exit on any drift — plus the release page, three asset manifests, About sidebar, 15 family targets, and installed-profile diagnostics.

## Rollback and interrupted rollout

Profile rollback is non-destructive. Selecting Lite or Pro stops higher-profile
mechanisms but never removes registries, projections, audits, memory, context
manifests, or run evidence. Before replacing a runtime package, finish or abort
its active runs with that same pinned runtime. In particular, pre-v19
nonterminal runs must be closed by the pre-v19 runtime; v19 returns
`LEGACY_RUN_BLOCKED` and will not append a terminal event for them.

Use this decision order:

1. **Before tag/release** — stop, fix the RC, rebuild all three profiles twice,
   rerun both evidence classes, and create a new RC commit.
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
repos, and all five release assets agree.

> **SkillHub quota (measured, v18.0.0)**: ~**100 publishes per 24h rolling window,
> account-wide**. Past it, every skill returns 发布频率过高 and *retries keep the
> window hot* — never grind retries against it. `publish-registries.sh` therefore
> stops at `--skillhub-budget` (default 90), retries a rate-limit once, defers the
> skill, and aborts the pass after 2 consecutive deferrals. A 120-skill full
> re-release is by design a **two-day publish**: ~90 on day one, the rest after
> the window rolls. Deferred runs exit 8, not 1.

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
