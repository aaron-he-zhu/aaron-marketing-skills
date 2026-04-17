# SEO & GEO 技能库

**20 个技能。15 个命令。搜索排名 + AI 引用，一次搞定。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | **中文** | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | [Português](README.pt.md)

面向搜索引擎优化（SEO）和生成式引擎优化（GEO）的 Claude 技能与命令集。零依赖，原生支持 [Claude Code](https://claude.ai/download)、[OpenClaw](https://openclaw.com)、[Gemini CLI](https://geminicli.com)、[Qwen Code](https://qwenlm.github.io/qwen-code-docs/)、[Amp](https://ampcode.com)、[Kimi](https://moonshotai.github.io/kimi-cli/)、[CodeBuddy](https://codebuddy.ai)，以及 [35+ 其他代理](https://github.com/vercel-labs/skills#supported-agents) 通过 `npx skills`。内容质量由 [CORE-EEAT 基准](https://github.com/aaron-he-zhu/core-eeat-content-benchmark)（80 项）评分，域名权威由 [CITE 域名评级](https://github.com/aaron-he-zhu/cite-domain-rating)（40 项）评分。

> **SEO** 让你在搜索结果中获得排名。**GEO** 让你被 AI 系统（ChatGPT、Perplexity、Google AI Overviews）引用。本库同时覆盖两者。

不熟悉术语？请查看 [GLOSSARY.md](../GLOSSARY.md)。

### 为什么选择这个技能库

- **120 项质量评分框架** — CORE-EEAT（80 项）+ CITE（40 项），带一票否决机制
- **8 种语言，750+ 触发词** — 中英日韩西葡，含正式、口语和拼写变体
- **零依赖** — 纯 Markdown 技能文件，无需 Python、虚拟环境或 API 密钥
- **工具无关** — 独立运行，或通过 14 个 MCP 服务器连接（Ahrefs、Semrush、Cloudflare 等）
- **7 个代理原生安装** — Claude Code、OpenClaw、Gemini CLI、Qwen Code、Amp、Kimi、CodeBuddy — 外加 35+ 代理通过 `npx skills`

## 快速开始

```bash
# Claude Code
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills

# OpenClaw / ClawHub
clawhub install aaron-he-zhu/<skill>

# Gemini CLI
gemini extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills

# Qwen Code
qwen extensions install https://github.com/aaron-he-zhu/seo-geo-claude-skills

# Amp
amp skill add aaron-he-zhu/seo-geo-claude-skills

# Kimi Code CLI
kimi plugin install https://github.com/aaron-he-zhu/seo-geo-claude-skills.git

# CodeBuddy（应用内，2 步）
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
/plugin install aaron-seo-geo

# 通用回退（Cursor、Codex、opencode、Windsurf、Copilot 等 35+ 代理）
npx skills add aaron-he-zhu/seo-geo-claude-skills

# 仅安装单个技能
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research
```

安装后即可使用：
```
帮我研究"云原生"相关的关键词机会
```

或运行命令：
```
/seo:audit-page https://example.com
```

## 技能总览

### 研究阶段 — 创建内容前先了解市场

| 技能 | 功能 |
|------|------|
| `keyword-research` | 关键词发现、意图分析、难度评分、话题聚类 |
| `competitor-analysis` | 竞争对手 SEO/GEO 策略分析 |
| `serp-analysis` | 搜索结果和 AI 回答模式分析 |
| `content-gap-analysis` | 发现竞争对手覆盖但你缺失的内容机会 |

### 构建阶段 — 创建搜索和 AI 优化内容

| 技能 | 功能 |
|------|------|
| `seo-content-writer` | 编写搜索优化内容 |
| `geo-content-optimizer` | 让内容更容易被 AI 系统引用 |
| `meta-tags-optimizer` | 优化标题、描述和 Open Graph 标签 |
| `schema-markup-generator` | 生成 JSON-LD 结构化数据 |

### 优化阶段 — 改进现有内容和技术健康度

| 技能 | 功能 |
|------|------|
| `on-page-seo-auditor` | 页面 SEO 审计，含评分报告 |
| `technical-seo-checker` | 可爬取性、索引、Core Web Vitals 检查 |
| `internal-linking-optimizer` | 优化内链结构 |
| `content-refresher` | 更新过时内容以恢复排名 |

### 监控阶段 — 追踪表现，及早发现问题

| 技能 | 功能 |
|------|------|
| `rank-tracker` | 追踪关键词在搜索和 AI 中的排名 |
| `backlink-analyzer` | 外链分析，发现机会和有毒链接 |
| `performance-reporter` | 生成 SEO/GEO 表现报告 |
| `alert-manager` | 排名下降、流量变化、技术问题告警 |

### 协议层 — 跨所有阶段的质量控制

| 技能 | 功能 |
|------|------|
| `content-quality-auditor` | 80 项 CORE-EEAT 内容质量审计 |
| `domain-authority-auditor` | 40 项 CITE 域名权威审计 |
| `entity-optimizer` | 品牌/实体知识图谱优化 |
| `memory-management` | 项目上下文的跨会话持久化 |

## 命令

| 命令 | 说明 |
|------|------|
| `/seo:audit-page <URL>` | 页面 SEO + CORE-EEAT 内容质量审计 |
| `/seo:check-technical <URL>` | 技术 SEO 健康检查 |
| `/seo:generate-schema <type>` | 生成 JSON-LD 结构化数据 |
| `/seo:optimize-meta <URL>` | 优化标题、描述和 OG 标签 |
| `/seo:report <domain> <period>` | SEO/GEO 综合表现报告 |
| `/seo:audit-domain <domain>` | CITE 域名权威审计 |
| `/seo:write-content <topic>` | SEO + GEO 优化内容写作 |
| `/seo:keyword-research <seed>` | 关键词研究与分析 |
| `/seo:setup-alert <metric>` | 配置监控告警 |
| `/seo:geo-drift-check [URL]` | (实验性,v9.0+) 验证预测 GEO Score 与 AI 引擎实际引用情况的偏差 |

### 维护命令(供库维护者 / 高级用户,日常可忽略)

| 命令 | 说明 |
|------|------|
| `/seo:wiki-lint` | Wiki 健康检查:矛盾、孤儿、过时声明、缺失页面 |
| `/seo:contract-lint` | Auditor Runbook 漂移检测、handoff schema 检查、术语泄漏扫描 (v7.1.0+) |
| `/seo:p2-review` | 评估 v7.1.0 延期项目触发条件;tombstone 复审 (2026-07-10) |
| `/seo:sync-versions` | 将 `.claude-plugin/plugin.json` 的版本号传播到所有跨 agent manifest(v9.0+,替代 `scripts/sync-versions.py`) |
| `/seo:validate-library` | 库级质量闸:描述预算、YAML 字段顺序、语言覆盖、重复触发词检测(v9.0+,替代 `scripts/validate-descriptions.py`) |

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md)。

## 许可证

Apache License 2.0

*最后同步英文 README：v9.0.0*
