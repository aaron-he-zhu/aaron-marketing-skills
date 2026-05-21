# SEO & GEO 技能库

**20 个技能。20 个命令。规划、审计、监控 SEO/GEO 工作。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.9.9-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | **中文**

面向搜索引擎优化（SEO）和生成式引擎优化（GEO）的 Agent 技能与命令集。本仓库是 slash-aaron 的候选 SEO/GEO anchor 能力包。技能内容为零依赖 Markdown；Claude Code hooks 使用轻量 Bash runner；Codex 集成使用 `.codex-plugin/plugin.json` 和 `.agents/plugins/marketplace.json`。安装入口、发布面和支持证据统一维护在 [Marketplace 模块](../marketplaces/README.md) 与 [平台注册表](../distribution/platforms.json)。内容质量使用 CORE-EEAT（80 项），域名权威使用 CITE（40 项）。

## 快速开始

常用安装方式如下。支持级别、证据、manifest 归属与发布规则见 [marketplaces/README.md](../marketplaces/README.md) 和 [distribution/platforms.json](../distribution/platforms.json)。

| 工具 | 安装 |
|------|------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` |
| Codex | `codex plugin marketplace add aaron-he-zhu/seo-geo-claude-skills`，重启 Codex 后在插件目录安装 `aaron-seo-geo` |
| ClawHub.ai / OpenClaw | 整包：`clawhub install aaron-he-zhu/aaron-seo-geo`；单技能：`clawhub install aaron-he-zhu/<skill>` |
| Gemini CLI | `gemini extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Qwen Code | `qwen extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills` |
| Amp | `amp skill add aaron-he-zhu/seo-geo-claude-skills` |
| Kimi Code CLI | `kimi plugin install https://github.com/aaron-he-zhu/seo-geo-claude-skills.git` |
| CodeBuddy | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` 后 `/plugin install aaron-seo-geo` |
| skills.sh / 通用 Agent Skills 宿主 | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |

单技能安装：`npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research`。

自然语言示例（需宿主支持自动路由）：

```text
帮我研究"云原生"相关的关键词机会
```

支持 `./commands/` 或命令 playbook 的宿主稳定入口：

```text
/aaron:auto audit https://example.com
```

## 技能

| 阶段 | 技能与用途 |
|------|------------|
| 研究 | `keyword-research` 关键词机会与选题；`competitor-analysis` 竞品差距；`serp-analysis` 搜索结果与意图；`content-gap-analysis` 内容缺口与编辑日历 |
| 构建 | `seo-content-writer` SEO/GEO 内容草稿；`geo-content-optimizer` AI 引用优化；`meta-tags-optimizer` 标题与元描述；`schema-markup-generator` JSON-LD 结构化数据 |
| 优化 | `on-page-seo-auditor` 页面 SEO 与 CORE-EEAT；`technical-seo-checker` 抓取、索引、速度、安全；`internal-linking-optimizer` 内链与站点架构；`content-refresher` 旧内容刷新 |
| 监控 | `rank-tracker` 排名与 SERP 变化；`backlink-analyzer` 外链质量与机会；`performance-reporter` SEO/GEO 报告；`alert-manager` 预警与监控规则 |
| 协议层 | `content-quality-auditor` 发布质量门；`domain-authority-auditor` CITE 域名可信度；`entity-optimizer` 实体与知识图谱；`memory-management` 项目记忆 |

## 命令
SEO/GEO pack-local 入口：`/aaron:auto`；例外最大深度模式：`/aaron:max`（二者也包含在用户命令中）。
用户命令：`/aaron:auto`, `/aaron:max`, `/aaron:discover`, `/aaron:compete`, `/aaron:map`, `/aaron:brief`, `/aaron:write`, `/aaron:series`, `/aaron:refresh`, `/aaron:publish`, `/aaron:audit`, `/aaron:visibility`, `/aaron:tech`, `/aaron:authority`, `/aaron:watch`, `/aaron:report`, `/aaron:remember`。

维护命令：`/aaron:skillify`, `/aaron:evolve`, `/aaron:guard`。

日常 SEO/GEO 工作通常从 `/aaron:auto` 开始；它会按用户目标执行 SEO/GEO pack-local 工作流，并只在阻塞决策点暂停。只有明确需要当前 pack 内最大深度、穷尽式分析或压力测试时才使用 `/aaron:max`。其余命令是重复任务的专家快捷入口。检查拟新增技能或路由时使用 `/aaron:skillify`；改进技能库本身时使用 `/aaron:evolve`；维护验收时使用 `/aaron:guard`。

破坏性改名说明：当前命令使用 `/aaron:`。旧 `/seo:*` 命令可粘贴给 `/aaron:auto` 来恢复新路由；例如 `/aaron:auto /seo:audit-page https://example.com/blog/post` 会返回 `/aaron:audit https://example.com/blog/post`。

## 运行模型

每个技能都遵循统一结构：Quick Start、Skill Contract、Handoff Summary、Data Sources、Instructions、Reference Materials、Next Best Skill。四个跨阶段技能负责协议层：`content-quality-auditor` 做发布质量门，`domain-authority-auditor` 做信任门，`entity-optimizer` 维护实体事实，`memory-management` 管理 HOT/WARM/COLD 项目记忆。

可选工具连接器见 [CONNECTORS.md](../CONNECTORS.md)；没有工具时，每个技能仍可用用户提供的数据运行。Codex 通过 `.codex-plugin/plugin.json` 加载插件；仓库级 marketplace 文件位于 `.agents/plugins/marketplace.json`，开发测试时以本仓库根目录作为 local source。

## 质量框架

| 框架 | 作用 |
|------|------|
| [CORE-EEAT](../references/core-eeat-benchmark.md) | 80 项内容质量评分 |
| [CITE](../references/cite-domain-rating.md) | 40 项域名权威评分 |
| [Auditor Runbook](../references/auditor-runbook.md) | 审计 handoff、分数封顶、Artifact Gate |

## 贡献与许可

贡献规则见 [CONTRIBUTING.md](../CONTRIBUTING.md)。版本见 [VERSIONS.md](../VERSIONS.md)。许可证：Apache License 2.0。

*最后同步英文 README：v9.9.9*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Fseo-geo-claude-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
 </picture>
</a>
