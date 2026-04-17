---
name: validate-library
description: Library-level quality gate. Walks all 20 SKILL.md files and verifies description budgets, YAML field order, language coverage, duplicate trigger detection, and frontmatter validity. Maintenance command — run before version bumps and PRs.
argument-hint: "[--skill <name>] [--strict]"
allowed-tools: ["Read", "Glob", "Grep"]
parameters:
  - name: skill
    type: string
    required: false
    description: Scan a single skill directory instead of all 20.
  - name: strict
    type: boolean
    required: false
    description: Report-only by default. Pass --strict to exit non-zero on any failure (CI use).
---

# Validate Library Command

Replaces the previous `scripts/validate-descriptions.py`. This command is pure-markdown and runs entirely in Claude's reasoning + Read/Glob/Grep tools — it preserves the design philosophy that the repo contains no executable code.

## Usage

```
/seo:validate-library                          # scan all 20 skills, report-only
/seo:validate-library --skill keyword-research # scan one skill
/seo:validate-library --strict                 # CI mode: final line reports STATUS: PASS or STATUS: FAIL
```

Run before version bumps, before opening a PR that touches any `SKILL.md`, or whenever bulk-refactoring skills. Complements `/seo:contract-lint` (handoff schema + runbook drift) and `scripts/validate-skill.sh` (per-skill ClawHub spec validation).

## What It Checks

### 1. Description budget (±20% tolerance)

Each `SKILL.md` description (`description:` in YAML frontmatter) should land within this byte budget, measured by `len(text.encode("utf-8"))`. Targets were originally derived empirically from the v7.x release (see [references/skill-contract.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/skill-contract.md)) — tuned so a skill's description fits within Anthropic Skills + Vercel Labs `npx skills find` discovery budgets without truncation:

| Skill category | Target bytes | Tolerance band | Rationale |
|---|---|---|---|
| research | 800 | 640–960 | Market-analysis skills share a common shape; triggers skew short |
| build | 900 | 720–1080 | Content-creation skills need more trigger variety |
| optimize | 900 | 720–1080 | Audit skills need dimension + verb variety |
| monitor | 700 | 560–840 | Alerting skills are narrow-scope |
| cross-cutting | 1000 | 800–1200 | Protocol-layer skills carry more context |

**Report**: one line per skill, showing actual byte length and pass/fail. Skills outside the band are not errors by themselves, but flag for manual review ("content bloat risk" or "too terse for discovery").

### 2. Required YAML frontmatter fields

Every `SKILL.md` must have, in order:
- `name` (required, string, must match directory name exactly, lowercase a-z/0-9/hyphens only, 1-64 chars)
- `description` (required, 1-1024 chars)
- `license` (recommended, default Apache-2.0)
- `compatibility` (recommended, list)
- `metadata` (recommended, mapping with `author`, `version`, `tags`, `triggers` at minimum)

**Optional but order-sensitive**: `when_to_use` (underscores, not hyphens) must come **before** `allowed-tools` if both are present.

### 3. Language coverage

The `metadata.triggers` list must include trigger phrases in at least **EN and ZH**. Additional languages (JA, KO, ES, PT) are encouraged. Flag any skill missing EN or ZH.

### 4. Duplicate triggers

No trigger phrase may appear in more than one skill (case-insensitive, after Unicode normalization). Duplicates cause ambiguous auto-activation. Report the offending phrase plus the list of skills claiming it.

### 5. Frontmatter validity

- YAML must parse cleanly.
- `name` field must match the parent directory name.
- `metadata.version` and the top-level `version:` (if present) must agree.
- No stray BOM, tabs-mixed-with-spaces, or trailing whitespace in frontmatter keys.

## Workflow

1. Enumerate SKILL.md files:
   - If `--skill <name>` is given, locate `<category>/<name>/SKILL.md`.
   - Otherwise, glob `{research,build,optimize,monitor,cross-cutting}/*/SKILL.md` (expect 20 matches).

2. For each file, read the frontmatter (everything between the first `---` and the second `---`).

3. Run all five checks above. Collect findings.

4. Print a summary table:

   ```
   SKILL                           DESC BYTES  YAML  LANG    DUPES  VERSION   STATUS
   -----                           ----------  ----  ----    -----  -------   ------
   keyword-research                862  OK     OK    EN,ZH   OK     9.0.0     PASS
   competitor-analysis             801  OK     OK    EN,ZH   OK     9.0.0     PASS
   ...
   -----
   Total: 20  Passed: 20  Failed: 0
   ```

5. **Strict mode** (`--strict`): end the final report line with exactly `STATUS: PASS` or `STATUS: FAIL`. CI scripts can parse the last line (`tail -n 1`) to decide whether to fail the build. Report-only mode (default) ends with a plain `Total: 20  Passed: N  Failed: M` summary without the STATUS marker.

## Fallback for no-Claude environments

- **Per-skill structural validation**: `bash scripts/validate-skill.sh <category>/<skill-dir>` — covers ClawHub + Agent Skills + Vercel spec checks, written in bash (no Python dependency).
- **Version consistency across all 20 skills**: `bash scripts/validate-skill.sh --status` — compares `version:` vs `metadata.version:` per skill.

These bash fallbacks cover checks 2 + 5 but not the description budget, language coverage, or duplicate triggers. For those, invoke this command via Claude Code CLI or run manually against the rules above.

## Related

- Per-skill spec validation (bash): [scripts/validate-skill.sh](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/scripts/validate-skill.sh)
- Version sync: `/seo:sync-versions`
- Runbook drift scan: `/seo:contract-lint`
