# Marketplace Module
This module owns marketplace and agent-host distribution rules. Runtime manifests stay at platform-required paths; do not move `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, root `marketplace.json`, `.codebuddy-plugin/`, or extension manifests here unless upstream supports that path. Platform claims are scoped by [`distribution/platforms.json`](../distribution/platforms.json).

| Area | Rule |
|------|------|
| Install targets | Claude Code, Codex, ClawHub.ai/OpenClaw, skills.sh/Agent Skills, CodeBuddy, Gemini CLI, Qwen Code, Amp, Kimi, and generic `npx skills` agents; command support is claimed only where the platform registry says `commands: supported`. |
| Manifest files | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `marketplace.json`, `.claude-plugin/marketplace.json`, `.codebuddy-plugin/marketplace.json`, `gemini-extension.json`, `qwen-extension.json`, `openclaw.plugin.json`, and skill frontmatter. |
| Sync and new marketplaces | Canonical version: `.claude-plugin/plugin.json`; skill arrays/root discovery setting: `.github/scripts/sync-skills.js`; platform evidence: `distribution/platforms.json`; checks: `node .github/scripts/sync-skills.js --check` and `bash scripts/validate-slimming-guardrails.sh`; Codex repo marketplace follows OpenAI Codex plugin docs (`.agents/plugins/marketplace.json` with `policy.installation`, `policy.authentication`, and `category`); live outreach/prospect data stays outside public package surfaces. |
