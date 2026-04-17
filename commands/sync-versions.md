---
name: sync-versions
description: Propagate the canonical version from .claude-plugin/plugin.json to all cross-agent manifest files so Gemini, Qwen, CodeBuddy, and the skills.sh marketplace stay in lockstep with the Claude Code manifest. Pure-markdown command — reads and writes JSON files directly, no executable script.
argument-hint: "[--dry-run]"
allowed-tools: ["Read", "Edit"]
parameters:
  - name: dry-run
    type: boolean
    required: false
    description: Report what would change without writing. Default is apply.
---

# Sync Versions Command

Keeps the version field aligned across every manifest the library publishes to. Canonical source is `.claude-plugin/plugin.json`. Targets are the other manifests that declare their own `version`.

**Why this is a slash command, not a script** — this library's design philosophy is zero executable code in the repo. The primary path is markdown (Claude executes this command using Read/Edit tools). A shell fallback with `jq` is documented at the bottom of this file for CI or no-Claude environments.

## Usage

```
/seo:sync-versions
/seo:sync-versions --dry-run
```

Run after editing `.claude-plugin/plugin.json` `version` field. The command reads the new version and propagates it to the four cross-agent manifests listed below. Idempotent: no-op when everything is already in sync.

## Workflow

1. **Read canonical source**:
   - Read [.claude-plugin/plugin.json](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/.claude-plugin/plugin.json). Extract top-level `version`. This is the target value (call it `$V`).
   - If the field is missing or empty, stop with an error and ask the user to set it first.

2. **Update each target file** by writing `$V` into every path listed below. Use the Edit tool with precise old_string → new_string matches; do not re-format unrelated JSON (preserve indentation, key order, trailing newline).

   | Target file | Paths to update |
   |---|---|
   | [marketplace.json](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/marketplace.json) | `metadata.version`, `plugins[0].version` |
   | [gemini-extension.json](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/gemini-extension.json) | top-level `version` |
   | [qwen-extension.json](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/qwen-extension.json) | top-level `version` |
   | [.codebuddy-plugin/marketplace.json](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/.codebuddy-plugin/marketplace.json) | top-level `version`, `plugins[0].version` |

   **Do NOT** touch any other `version` field in the repo (e.g., nested schema versions, legacy changelog copies, SKILL.md `metadata.version`). Those are governed by other rules and should move independently.

3. **Idempotence check**: if a path already equals `$V`, skip it and note "already in sync". If `--dry-run` was passed, report what would change but do not write.

4. **Summary report** (to the user). Example output for an illustrative bump from 9.0.0 → 9.1.0:
   ```
   Sync versions → 9.1.0
     marketplace.json: metadata.version ✓ (was 9.0.0)
     marketplace.json: plugins[0].version ✓ (was 9.0.0)
     gemini-extension.json: version ✓ (was 9.0.0)
     qwen-extension.json: version: already in sync
     .codebuddy-plugin/marketplace.json: version ✓ (was 9.0.0)
     .codebuddy-plugin/marketplace.json: plugins[0].version ✓ (was 9.0.0)
   5 file(s) updated, 1 field already in sync.
   ```

5. **Follow-ups the command does NOT do** (flag these so the user remembers):
   - 20 SKILL.md files each carry their own `metadata.version` — bump manually per the version policy in [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) Contribution Rules
   - [VERSIONS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md) skills table and changelog — add a new entry
   - [CITATION.cff](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CITATION.cff) `version` + `date-released`
   - [README.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/README.md) + 5 localized docs version badges

## Fallback for no-Claude environments

For CI or contributors who cannot invoke Claude Code CLI, a one-liner shell equivalent (requires `jq`):

```bash
V=$(jq -r .version .claude-plugin/plugin.json) && \
  jq --arg v "$V" '.metadata.version=$v | .plugins[0].version=$v' marketplace.json > marketplace.json.tmp && mv marketplace.json.tmp marketplace.json && \
  jq --arg v "$V" '.version=$v' gemini-extension.json > gemini-extension.json.tmp && mv gemini-extension.json.tmp gemini-extension.json && \
  jq --arg v "$V" '.version=$v' qwen-extension.json > qwen-extension.json.tmp && mv qwen-extension.json.tmp qwen-extension.json && \
  jq --arg v "$V" '.version=$v | .plugins[0].version=$v' .codebuddy-plugin/marketplace.json > .codebuddy-plugin/marketplace.json.tmp && mv .codebuddy-plugin/marketplace.json.tmp .codebuddy-plugin/marketplace.json
```

## Related

- Contribution rules: [CLAUDE.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CLAUDE.md) §Contribution Rules
- Version history: [VERSIONS.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
