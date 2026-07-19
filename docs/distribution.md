# Distribution — publishing the plugin to every channel

This repo is the SSOT; it fans out to four distribution channels. Every publisher
is **owner-run, dry-run by default, and driven by the repo's committed state** —
no hardcoded queues, no guessing. The single source of truth for "are we fully
distributed?" is `scripts/registry-status.sh`.

> Note: `scripts/build-distribution.py`'s minimal *plugin* profile is the
> ClawHub package source via `publish-package.sh --from-build` — adopted at
> v17.0.0 when the full git archive first exceeded ClawHub's upload limit
> (413). The GitHub-source mode remains the default for as long as it fits.
> The profile's manifest and link-closure are CI-checked. An optional
> `--slim-frontmatter` flag strips the publishing-only frontmatter keys
> (`slug`/`displayName`/`summary` — SkillHub listing identity used only by the
> owner-run publish step) from the shipped SKILL.md files, trimming per-load
> frontmatter cost on every installed host; routing surfaces
> (`description`/`when_to_use`) and host extensions (`metadata.hermes`/
> `openclaw`) are untouched.

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
```

Prints, for every manifest skill, `repo` vs `ClawHub` vs `SkillHub` published version, a per-platform current/stale/missing summary, and the bundle-plugin package version. Read-only — it never publishes.

## Release-time distribution (the full push→distribution runbook, in order)

Validated end-to-end at v18.0.0 (2026-07-13/14). Every step is resumable: a killed
session loses at most one in-flight skill — re-run the same command.

1. **Push**: clean tree → `git pull --rebase` → `git push` → CI green on origin/main.
2. **Release**: `gh release create vX.Y.Z --title … --notes …` (VERSIONS.md entry is the source for the notes).
3. **About**: `bash scripts/sync-about.sh` → review → `--live` — projects `.github/repo-about.json` onto the GitHub sidebar. *This step was silently skipped at v18.0.0 and the About kept advertising the previous release's framework names — it is part of the ritual, not an extra.*
4. **Family prerequisites** (only when the release renamed/reshaped a family repo): `gh repo rename` the mirror first, then manually reconcile any `ids`-mode mirror's content (README + standard file + CHANGELOG + CITATION) — `ids` targets are verify-only and never auto-pushed.
5. **Family**: `bash scripts/sync-family.sh` → review → `--live` → re-run the dry-run until all 15 report ✓.
6. **Package**: `bash scripts/publish-package.sh --from-build` → review → `--live`. On a transport error after upload the script now verifies server-side via `package inspect` before declaring failure.
7. **Registries**: `bash scripts/registry-status.sh` (parallel by default, ~2–4 min) → `bash scripts/publish-registries.sh` → review → `bash scripts/publish-registries.sh --live --parallel` — publishes **only the behind-set**; the two platforms run concurrently. **Exit 8 = SkillHub quota deferrals** (see the quota box below): finish the remainder the next day with `bash scripts/publish-registries.sh --live skillhub`.
8. **Verify**: `bash scripts/registry-status.sh` — 120/120 current on both + package current — plus a glance at the release page and the About sidebar.

> **SkillHub quota (measured, v18.0.0)**: ~**100 publishes per 24h rolling window,
> account-wide**. Past it, every skill returns 发布频率过高 and *retries keep the
> window hot* — never grind retries against it. `publish-registries.sh` therefore
> stops at `--skillhub-budget` (default 90), retries a rate-limit once, defers the
> skill, and aborts the pass after 2 consecutive deferrals. A 120-skill full
> re-release is by design a **two-day publish**: ~90 on day one, the rest after
> the window rolls. Deferred runs exit 8, not 1.

## Gotchas (learned the hard way)

- **GitHub source, never the local folder, for the package** — `clawhub package publish .` ignores `.gitignore` and would bundle `.git`, local settings, and any stray `.claude/worktrees/` copy. `publish-package.sh` always publishes `owner/repo@<committed-sha>` (a git-archive of committed files only).
- **The manifest must be committed + pushed** before a package publish — `publish-package.sh` refuses otherwise.
- **SkillHub slug**: unprefixed `<name>` is preferred (when the account owns the short slug), else `aaron-<name>`. `validate-skill.sh` accepts both. Legacy `aaron-<name>` records from before a slug switch may linger as orphans (most registries can't delete).
- **SkillHub search recall**: `registry-status.sh` reads SkillHub via fuzzy search, so it can report a false `missing`. The publisher self-corrects — an idempotent publish of an already-current version returns `版本已存在` and counts as in-sync.
- **ClawHub rate limits**: brand-new skills are ~5/hour; **version updates to existing skills are not capped** (measured ~37s/skill wall time — packing + upload dominates, not the 6s spacing). SkillHub's real constraint is the ~100/24h rolling account quota (box above), not burst pacing; the publisher spaces 40s and owns the retry policy (`publish-skillhub.sh --attempts 1` in orchestrated mode, so the two retry layers can no longer multiply into 16 requests per limited skill). Both publishers are resumable via the version-keyed state file.
- **Session-death resilience**: publishers hold no in-memory state worth saving — behind-set comes from the server, done-set from the state file, and re-publishing an already-current version is a no-op (`版本已存在`). After any crash/restart: re-run the same command.
- **ClawHub MIT-0**: per-skill publishes relicense to MIT-0 (`--i-accept-mit0`), broader than the repo's Apache-2.0.
- Requires the `clawhub` + `skillhub` CLIs logged in on the owner machine. **Never CI-automated** — pushes to public registries get a human glance.

> Historical note: `finish-registry-publish.sh` (removed) hard-coded its publish queue, which silently rotted out of date. `publish-registries.sh` computes the queue from live `registry-status.sh` output instead — the queue can no longer drift.
