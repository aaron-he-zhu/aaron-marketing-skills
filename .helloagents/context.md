# 项目上下文

## 概述
seo-geo-claude-skills 是 SEO/GEO 能力包仓库，包含 20 个 Markdown 技能、20 个 slash commands、共享引用资料、跨宿主 manifest 与轻量 Bash/Node 验证脚本。

## 技术栈
- 主体内容：Markdown/YAML/JSON。
- 维护脚本：Bash、Node.js CommonJS。
- 主要验证：`node .github/scripts/sync-skills.js --check`、`bash scripts/validate-slimming-guardrails.sh`、`bash scripts/validate-skill.sh <skill-dir>`。

## 架构
- `research/`、`build/`、`optimize/`、`monitor/`、`cross-cutting/`：技能目录。
- `commands/`：`/aaron:*` 命令。
- `references/`：共享框架、协议和决策记录。
- `.claude-plugin/`、`.codebuddy-plugin/`、`.codex-plugin/`、`.agents/plugins/`、`marketplace.json`、`distribution/platforms.json`：跨宿主分发与市场入口。

## 目录结构
- `.claude-plugin/plugin.json`：Claude/OpenClaw 兼容插件 manifest。
- `.codex-plugin/plugin.json`：Codex 插件 manifest。
- `.agents/plugins/marketplace.json`：Codex repo marketplace。
- `.github/scripts/sync-skills.js`：同步技能数组到 manifest/marketplace。
- `marketplaces/README.md`：分发面规则。

## 模块文档
暂无单独模块文档。

## 最近变更
见 [CHANGELOG.md](CHANGELOG.md)。
