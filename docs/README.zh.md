# SEO & GEO 技能库

**20 个技能。5 个命令。规划、审计、监控 SEO/GEO 工作。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.9.10-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | **中文**

面向搜索引擎优化（SEO）和生成式引擎优化（GEO）的 Claude 技能与命令集。技能内容为零依赖 Markdown；Claude Code hooks 使用轻量 Bash runner。安装入口见下方“快速开始”。内容质量使用 CORE-EEAT（80 项），域名权威使用 CITE（40 项）。

## 快速开始

常用安装方式如下。

| 工具 | 安装 |
|------|------|
| Claude Code | `/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills` 然后 `/plugin install aaron-seo-geo@aaron` |
| skills.sh / 通用 Agent Skills 宿主 | `npx skills add aaron-he-zhu/seo-geo-claude-skills` |
| 任意宿主 | `git clone https://github.com/aaron-he-zhu/seo-geo-claude-skills` |

单技能安装：`npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research`。

自然语言示例（需宿主支持自动路由）：

```text
帮我研究"云原生"相关的关键词机会
```

Slash 命令宿主的稳定入口：

```text
/aaron-seo-geo:auto audit https://example.com
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
5 个命令，按 SEO/GEO 意图组织。日常工作从 `/aaron-seo-geo:auto` 开始；其余四个是显式的模式入口：

- `/aaron-seo-geo:auto` — 推断意图并执行最小够用的工作流（加 `--deep` 进行穷尽/压测）
- `/aaron-seo-geo:research` — 关键词需求、SERP 意图、竞品、内容缺口、站点/主题/实体地图
- `/aaron-seo-geo:create` — brief、写作、系列、刷新、CMS 中立发布包（`--brief`/`--series`/`--refresh`/`--publish`/`--meta`/`--schema`）
- `/aaron-seo-geo:audit` — on-page + CORE-EEAT 质量、技术 SEO、AI 可见性、域权威（`--full`/`--tech`/`--visibility`/`--authority`）
- `/aaron-seo-geo:track` — 排名、告警、绩效报告、项目记忆（`--alert`/`--report`/`--remember`）

破坏性改名说明：当前命令使用 `/aaron-seo-geo:`。旧 `/seo:*` 命令可粘贴给 `/aaron-seo-geo:auto` 来恢复新路由；例如 `/aaron-seo-geo:auto /seo:audit-page https://example.com/blog/post` 会返回 `/aaron-seo-geo:audit https://example.com/blog/post`。

## 运行模型

每个技能都遵循统一结构：Quick Start、Skill Contract、Handoff Summary、Data Sources、Instructions、Reference Materials、Next Best Skill。四个跨阶段技能负责协议层：`content-quality-auditor` 做发布质量门，`domain-authority-auditor` 做信任门，`entity-optimizer` 维护实体事实，`memory-management` 管理 HOT/WARM/COLD 项目记忆。

可选工具连接器见 [CONNECTORS.md](../CONNECTORS.md)；没有工具时，每个技能仍可用用户提供的数据运行。

## 质量框架

| 框架 | 作用 |
|------|------|
| [CORE-EEAT](../references/core-eeat-benchmark.md) | 80 项内容质量评分 |
| [CITE](../references/cite-domain-rating.md) | 40 项域名权威评分 |
| [Auditor Runbook](../references/auditor-runbook.md) | 审计 handoff、分数封顶、Artifact Gate |

## 贡献与许可

贡献规则见 [CONTRIBUTING.md](../CONTRIBUTING.md)。版本见 [VERSIONS.md](../VERSIONS.md)。许可证：Apache License 2.0。

*最后同步英文 README：v9.9.10*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Fseo-geo-claude-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/seo-geo-claude-skills&type=date&legend=top-left" />
 </picture>
</a>
