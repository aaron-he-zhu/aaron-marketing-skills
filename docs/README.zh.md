<div align="center">

# Aaron 营销技能库

**120 个营销技能 —— 品牌叙事、SEO/GEO、红人、付费广告、邮件、产品发布、自然社媒 —— 共享一套契约。**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
<!-- GENERATED:BEGIN release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-19.1.0-orange" alt="Version"></a>
<!-- GENERATED:END release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | **简体中文** | [繁體中文](README.zh-Hant.md)

</div>

一套 Claude 技能与斜杠命令，让聊天 Agent 成为营销操作员。七个学科 + 一个共享协议层，一图总览（逻辑顺序：叙事 → 各常态频道 → 发布 → 协议）：

| 层 | 技能 | 生命周期（阶段目录） | 框架 → 门 | 入口命令 |
|----|------|----------------------|-----------|----------|
| **品牌叙事** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **自然社媒** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **邮件营销** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`（EQS） | `/aaron-marketing:email` |
| **付费广告** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`（RQS） | `/aaron-marketing:ad` |
| **红人** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor`（SQS）；`fit-scorer` 打 Suitability (S) 分 | `/aaron-marketing:influencer` |
| **产品发布** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **协议层** | 8 | ——（阶段流程之外的共享机件） | 7 个真相注册表（实体 · 创作者 · offer/声明 · 同意 · 发布 · 频道 · 叙事）+ HOT/WARM/COLD 记忆 | —— |

`/aaron-marketing:auto` 可把任意自然语言目标路由到整套体系。技能与命令都是**纯 Markdown**；小型 Bash/Python 标准库运行时提供 hooks、校验、评分、注册表事件、连接器与 CI 检查（无 `pip`、无构建步骤）。**每个技能都在 Tier 1 用你提供的数据即可运行**；连接器只自动化数据拉取，或一次经明确批准的变更。

权威的类型化拓扑是 [`references/system-catalog.json`](../references/system-catalog.json)；可读的四层地图、全部 120 条路径、注册表所有者、auditor 落点与分发档案见[生成的系统架构文档](system-architecture.md)。

> 合并前的两个独立仓库现均为**纯路标仓库**——[seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)（最终 20 技能版本线保留于 tag `v9.9.12`）与 [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)（最终 IMPACT 版本线保留于 tag `standalone-final`），安装一律指向本仓库。兄弟仓库策略见 [docs/repo-family.md](repo-family.md)。

---

## 目录

- [为什么选它](#为什么选它)
- [安装](#安装)
- [初次使用](#初次使用)
- [架构](#架构)
  - [共享技能契约](#共享技能契约)
  - [四层营销操作系统](#四层营销操作系统)
  - [质量体系：八框架、八门](#质量体系八框架八门)
  - [协议层](#协议层)
  - [记忆与自动化](#记忆与自动化)
- [技能目录](#技能目录)
  - [品牌叙事 — TALE（16）](#品牌叙事--tale16)
  - [SEO/GEO — SITE（16）](#seogeo--site16)
  - [红人 — STAR（16）](#红人--star16)
  - [付费广告 — ROAS（16）](#付费广告--roas16)
  - [邮件营销 — SEND（16）](#邮件营销--send16)
  - [产品发布 — RAMP（16）](#产品发布--ramp16)
  - [自然社媒 — ECHO（16）](#自然社媒--echo16)
  - [协议层（8）](#协议层8)
- [命令](#命令)
- [连接器与层级](#连接器与层级)
- [推荐工作流](#推荐工作流)
- [仓库结构](#仓库结构)
- [设计哲学](#设计哲学)
- [质量守卫](#质量守卫)
- [贡献与文档](#贡献与文档)
- [免责声明](#免责声明)
- [许可证](#许可证)

---

## 为什么选它

| 原则 | 落到实处 |
|------|----------|
| **默认 keyless** | 每个技能都能在 **Tier 1** 仅凭粘贴的数据、或从免费/第一方来源拉取的数据运行。付费工具与 MCP 服务器是可选项，绝非前提。付费广告技能基于**自有账户手动导出**评分——带密钥的广告 API 永不必需。 |
| **内容优先、契约可执行** | 技能始终是 Markdown。小型 Bash/Python 标准库运行时让评分、状态、安全与契约一致性都可确定性执行，且不新增任何包依赖。 |
| **一套共享契约** | 120 个技能暴露同样的七段结构，并自带 `discipline` + `phase` 元数据，整个库像一套操作系统：每个技能都知道自己的输入、输出，以及下一个该交棒的技能。 |
| **带门的质量** | 八套基准驱动八个 auditor-class 门，产出结构化、可机器校验的判定——不是凭感觉。成功/失败/批次 hook 通过有界检查暴露无效写入；pre-commit/CI 只兜底已提交 Git 内容中的 PII，不校验 runtime 工件。 |
| **真相住在事件里** | 七条只追加（append-only）的注册表事件流是规范真相；由所有者掌控的投影对外暴露实体、创作者、声明、同意、发布、频道与叙事状态，全程不再有破坏性队列。 |
| **跨轮记忆** | HOT/WARM/COLD 记忆模型在技能与会话之间携带发现、分数与未决事项，并在写入时净化。 |
| **人话** | 技能内置 AI 腔检测器与禁用词表，让输出读起来像人写的。 |

---

## 安装

可配合 Claude Code、任意 Agent Skills 兼容宿主，或直接 `git clone`：

| 宿主 | 安装 |
|------|------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 然后 `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ 宿主](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn)(中文社区)** | `skillhub install <frontmatter-slug>`(如 `keyword-research`) |
| **任意宿主** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

在 Claude Code 中，`marketplace add` 只是注册目录——还需运行 `/plugin install aaron-marketing@aaron`（或在 `/plugin` 中选择）才能真正启用技能与命令。通用宿主单技能安装：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。可在 [skills.sh 注册表](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)浏览本技能库。各宿主的技能目录、frontmatter 兼容细节、以及脱离插件安装时的降级行为见 [docs/agent-compatibility.md](agent-compatibility.md)（2026-07 实测 120/120 可安装）。

安装插件**不会**往你的 `/mcp` 列表添加任何东西——MCP 目录位于 [`docs/mcp-catalog.json`](mcp-catalog.json)，刻意放在 Claude Code 会自动注册的插件根 `.mcp.json` 路径之外，仅作复制粘贴参考（见[连接器与层级](#连接器与层级)）。

---

## 初次使用

若宿主支持自动技能路由，直接描述目标即可：

```text
帮我研究面向小团队的 SaaS 产品的关键词
```
```text
帮一个护肤品牌找 TikTok 红人并给适配度打分
```
```text
在我加预算前，审计这个 Google Ads 账户——导出文件已附上
```

或用斜杠命令 —— `/auto` 负责路由，学科入口直达：

```text
/aaron-marketing:auto 把我们的定价页改造成可被 AI 引用的对比中心
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` 会推断意图并执行最小够用的工作流，只在阻塞性决策处停下。每个技能都能用粘贴的数据运行；可选工具见 [CONNECTORS.md](../CONNECTORS.md)。

---

## 架构

### 共享技能契约

每个技能都遵循**同一套激活契约**——固定顺序的七段：

1. **触发 / 何时使用** —— 何时该启用。
2. **Quick Start** —— 可复制粘贴的提示。
3. **Skill Contract** —— 预期输出 · 读取 · 写入 · 提升 · 完成条件 · 主下一技能。
4. **Handoff Summary** —— 标准交棒结构，让下一个技能干净接力。
5. **Data Sources** —— `~~category` 占位符，每个都有 keyless 的 Tier-1 路径。
6. **Instructions** —— 编号方法（把所有导出当作不可信输入）。
7. **Next Best Skill** —— 下一步去哪（带 visited-set + 最大深度终止规则）。

每个技能还自带 `metadata.discipline`（narrative / seo-geo / influencer / ad / email / launch / social / protocol）与 `metadata.phase`，路由与聚类因此全库统一。契约在 [skill-contract.md](../references/skill-contract.md) 中定义一次；跨技能共享状态见 [state-model.md](../references/state-model.md)。

### 四层营销操作系统

> **本系统——一套四层营销操作系统。** 一种品牌嗓音，经五条常态频道表达，在发布时刻集中释放，全都读写同一份系统级记录。七个学科、四个高度——是一套系统，不是一堆技能。
>
> | 层 | 上手节奏 | 学科 | 节律 |
> |----|----------|------|------|
> | **L1 · 策略** —— 我们说什么 / 我们是谁 | crawl | **品牌叙事** · TALE | 常态 |
> | **L2 · 频道** —— 表达策略的常态引擎（自有 → 付费） | walk | **SEO/GEO** · CORE-EEAT + CITE · **自然社媒** · ECHO · **邮件** · SEND · **付费广告** · ROAS · **红人** · STAR | 常态（红人偏阶段性） |
> | **L3 · 编排** —— 跨频道的限时时刻 | run | **产品发布** · RAMP | 阶段性 |
> | **L4 · 协议** —— 共享的系统级记录 | —— | 7 个真相注册表 + 工作记忆 · 8 个 auditor 门 · 一套技能契约 | —— |
>
> 叙事是消息，频道是表达它的媒介。每个核心 builder 都会记录它所使用的确切准则 ID/版本与声明投影偏移量（offset），或一次经明确批准的回退/阻断。每个学科自己的 4 阶段循环都活在它所属的层里（叙事 = Trace → Architect → Land → Evaluate）。

七个学科都用阶段**目录**（`narrative/trace/`…、`seo-geo/survey/`…、`influencer/scout/`…、`ad/research/`…、`email/setup/`…、`launch/research/`…、`social/explore/`…）。注意 "activate" 在红人里指创作者外联、在付费里指账户门控——同词不同域。

### 质量体系：八框架、八门

八套基准让"好"可度量。每套定义维度、汇总方法，以及一小组**否决项**（无视其余分数直接封顶或阻断的硬性失败）：

| 框架 | 评分对象 | 项数 / 维度 | 汇总 | 否决项 |
|------|----------|-------------|------|--------|
| **[TALE](../references/tale-benchmark.md)** | 品牌叙事的真相 / 体系 / 效果 | T / A / L / E | `truth`、`system`、`effectiveness` 三个 profile 结果各自独立；无总合成分 | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | 内容质量，附 CORE/GEO 与 EEAT/SEO 诊断视图 | 80 项 / 8 维 | 完整的 profile 加权结果；诊断视图不是独立总分 | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | 域名权威与引用信任 | 40 项 / 4 维 | 算术 profile 加权平均 | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | 红人 Suitability / Trust / Appeal / Return | S / T / A / R；40 项 / 4 维 | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | 付费广告的增量贡献与运营质量 | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | 邮件的发件人完整性 / 互动 / 培育 / 直接成效 | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | 产品发布的就绪 / 资产 / 势能 / 证明 | R / A / M / P；40 个稳定 ID | `preflight`、`execution`、`outcome` 三个 profile 结果各自独立；绝不跨时间视界取平均 | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | 自然社媒的嵌入度 / 工艺 / 运营 / 可观测性 | E / C / H / O；40 个稳定 ID | 每次只跑一个 `asset-gate` 或 `program-maturity-*` profile；绝不混合不同类单元 | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

每套框架由一个 **auditor-class 门**执行——其类型化工件（`class: auditor-output`）由确定性 validator 与有界生命周期 hooks 校验。仓库 CI 只回归测试 validator 与契约，不会检查被忽略的主机运行时工件。门是工作流步骤，所以驻留并计入各自学科：

| 门 | 框架 | 所在 | 判定 |
|----|------|------|------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE 三 profile | `narrative/evaluate/` | truth/system/effectiveness 结果各自独立；无合成总分 |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED；信任标签仅作解释 |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED，另附面向创作者的转述 |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP 生命周期 profile | `launch/mobilize/` | 对一个已声明的生命周期读数给出 SHIP / FIX / BLOCK / UNDECIDED |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO 资产/项目 profile | `social/host/` | 对一个已声明的单元/profile 给出 SHIP / FIX / BLOCK / UNDECIDED |

**共享否决策略：** 一条经核实的否决项把最终分封顶在 `min(raw, 59)`；两条及以上经核实的否决项产生 `status: DONE` + `verdict: BLOCK` 且不给最终分。证据缺失记为 `Unknown`，绝不自动判负。类型化规则见 [auditor-runbook.md](../references/auditor-runbook.md)。

### 协议层

`protocol/` 目录承载学科阶段流程之外的**共享真相与记忆机件** —— 8 个技能，单独计数：

| 技能 | 职责 | 锚定 | 规范事件流 / 运行时角色 |
|------|------|------|----------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | 规范品牌/实体档案（知识图谱、Wikidata、AI 消歧） | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 规范创作者名册/档案——去重 handle、带溯源标签的受众数据、费率、合规历史 | 红人 | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | offer 与声明实证台账——O1/T2 声明检查所对照评判的那份记录 | 付费 | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 规范的按主体同意/抑制记录——S2/N1 否决项对照评判的那份记录 | 邮件 | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 发布台账——每次发布的规范档案与发布日历：分级/类型、生命周期阶段（draft→GA 单向）、权威日期与禁运期承诺、渠道提交台账（launch 真相 SSOT） | 产品发布 | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 规范频道台账——去重 handle、按平台归属、粉丝/互动率基线（带溯源标签的命名/周期稳定分母）、认领状态与运营史；ECHO `E1` 否决项对照评判的那份记录（无记录 = NEEDS_INPUT） | 自然社媒 | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 规范品牌准则 SSOT——叙事、消息系统、语言/词表红线与定位真相；TALE 门与各频道 creative builder 对照评判并继承嗓音与声明的那份记录 | 品牌叙事 | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD 记忆生命周期（捕获 · 提升 · 降级 · 归档 · 查询） | 全部学科 | 非规范的 `memory/` 运行时状态 |

注册表遵循**唯一写入者规则**（其他技能经 `registry-events.py` proposal events 投递），且注册表只*存证*——评判归门。最底层真正横向的是 `references/` 协议（[auditor-runbook](../references/auditor-runbook.md)、[state-model](../references/state-model.md)、[skill-contract](../references/skill-contract.md)、[humanizer-slop](../references/humanizer-slop.md)、[measurement-protocol](../references/measurement-protocol.md)）——按设计以文档而非技能的形式共享。

### 记忆与自动化

**记忆**按温度分层，让上下文跨技能与会话留存而不撑爆提示：

| 层 | 位置 | 行为 |
|----|------|------|
| **HOT** | `memory/hot-cache.md` | 每次会话自动加载；封顶 **80 行 且 25 KB**（先触发者为准）。 |
| **WARM** | `memory/<subdir>/` | 可重建的工作投影与经许可的审计工件；规范的注册表真相住在 `memory/events/*.ndjson`。 |
| **COLD** | `memory/archive/` | 降级/较旧记录，留作召回。 |

**Hooks**（`hooks/hooks.json`，runner `hooks/claude-hook.sh`）接入七个 Claude Code 事件：

| 事件 | 匹配 | 作用 |
|------|------|------|
| `SessionStart` | `startup\|resume\|clear\|compact` | 注入**净化后**的 hot-cache + 未决事项指针（提示注入行被涂掉；符号链接缓存被拒）。 |
| `UserPromptSubmit` | （全部） | 轻量逐提示上下文 hook。 |
| `PreToolUse` | 已知可写工具 | 精确路径的直接 `memory/**` 写入必须被 Git 忽略；可识别的 opaque shell/MCP 内存变更不受支持并会被拒绝。Registry runtime 会再次检查最终/临时/锁路径。 |
| `PostToolUse` | 已知可写工具 | 成功写入后复核整个 operational-memory 命名空间，并校验准确审计目标或执行有界保留区扫描。 |
| `PostToolUseFailure` | 已知可写工具 | 工具失败后执行同样的写后隐私与 Artifact Gate 检查，因为失败命令仍可能已写文件。 |
| `PostToolBatch` | （全部） | 每批并行工具结束后复核 operational memory 与完整审计保留区。 |
| `Stop` | （全部） | 执行最后一次有界扫描并可阻止一次以便修复；`stop_hook_active` 会放行后续停止。pre-commit/CI 仅保护已提交 Git 内容中的 PII，不校验被忽略的 runtime 工件。 |

Artifact Gate 是**框架无关**的——同一个 hook 校验 CORE-EEAT、CITE、STAR、ROAS、SEND、RAMP、ECHO、TALE 工件，无任何针对单框架的代码。

---

## 技能目录

技能链接打开各自的 `SKILL.md`。展开每个学科下的 **详情** 可看每个技能的一句话用途。学科按逻辑分层排序（策略层的品牌叙事居首）。

### 品牌叙事 — TALE（16）

`narrative/` 下四个阶段按 Trace → Architect → Land → Evaluate 排布。`narrative-quality-auditor` 分别运行 truth、system、effectiveness 三个 profile；完整评审只把三个结果关联起来，绝不取平均。叙事是各频道 builder 所继承的 L1 策略。

| 阶段 | 技能 |
|------|------|
| **Trace 溯源** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect 架构** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land 落地** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate 评估** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>逐技能用途（品牌叙事）</b></summary>

| 技能 | TALE 杠杆 | 用途 |
|------|-----------|------|
| narrative-baseline-mapper | T | 盘点现有叙事基线——散落在各资产/频道里的消息、口径漂移、缺口。 |
| category-narrative-mapper | T | 品类叙事地图——竞争替代品的说法、品类框架、可占领的语义空白。 |
| audience-belief-mapper | T | 受众信念地图——现有认知、异议、要跨越的信念鸿沟。 |
| positioning-truth-tracer | T | 把定位主张回溯到可证事实——每条声明有出处、可实证（复用 positioning-mapper）。 |
| strategic-narrative-designer | A | 战略叙事设计——变革叙事弧、赌注、"为何是现在"。 |
| message-system-architect | A | 消息系统架构——tagline、支柱、PR-FAQ 脊柱，感知声明台账（复用 message-house-builder）。 |
| brand-language-codifier | A | 品牌语言编纂——词表、嗓音、口吻红线，写入 narrative-registry 供各频道继承。 |
| story-bank-builder | A | 故事库——客户故事、类比、证据叙事的可复用素材库。 |
| narrative-cascade-planner | L | 叙事级联计划——把 L1 消息落到各频道/受众/阶段的分发地图。 |
| pitch-narrative-builder | L | pitch 叙事——面向媒体/投资人/销售的一页叙事与演示脊柱。 |
| narrative-enablement-kit | L | 叙事赋能包——供内部/合作方一致复述的话术、FAQ、do/don't。 |
| proof-point-packager | L | 证据点打包——把主张配上可核验证据、数据、第三方背书。 |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | 类型化 TALE 门：分别返回各 profile 结果，绝不取平均。写入 `memory/audits/narrative/`。 |
| message-test-designer | E | 消息测试设计——A/B 消息、信念位移测量、受众验证实验。 |
| narrative-resonance-monitor | E | 叙事共鸣监控——消息采纳、复述保真、共鸣信号（复用 bluesky.py/gdelt.py/tavily.py/wayback.py 为 proxy，始终标注）。 |
| narrative-drift-monitor | E | 叙事漂移监控——跨频道口径偏离、失控消息、准则违规预警。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[positioning-mapper](../launch/research/positioning-mapper/SKILL.md)（物理留在 launch，逻辑读作 TALE Trace 最前端）、[message-house-builder](../launch/assemble/message-house-builder/SKILL.md)、[audience-mapper](../influencer/scout/audience-mapper/SKILL.md)、[share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md)。**无新增连接器**——叙事共鸣复用 `bluesky.py`/`gdelt.py`/`tavily.py`/`wayback.py`。品牌叙事真相注册表 `narrative-registry` 位于协议层。

</details>

### SEO/GEO — SITE（16）

四个阶段目录沿 SITE 循环（Survey 勘测 → Implement 实施 → Tune 调优 → Evaluate 评估），外加本学科的两个质量门（标 ⛩）；质量基准仍是 CORE-EEAT + CITE，循环品牌与基准名彼此独立。

| 阶段 | 技能 |
|------|------|
| **Survey 勘测** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement 实施** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune 调优** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate 评估** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>逐技能用途（SEO/GEO）</b></summary>

| 技能 | 用途 |
|------|------|
| keyword-research | 为页面/主题/活动开启关键词工作——意图、需求、临门一脚机会。 |
| competitor-analysis | 分析竞品 SEO 策略，对比域名，挖出其关键词与缺口。 |
| serp-analysis | 读懂 SERP——特性、摘要、People Also Ask、某查询的排名规律。 |
| content-gap-analysis | 找出相对竞品缺失的主题与覆盖空洞。 |
| content-writer | 撰写并刷新 SEO 优化的文章、博文、落地页、产品文案。 |
| geo-content-optimizer | 为 AI 引擎（ChatGPT、Perplexity、AI Overviews、Gemini、Claude、Copilot）优化内容。 |
| serp-markup-builder | 标题标签、元描述、Open Graph、Twitter Cards + JSON-LD / Schema.org 结构化数据。 |
| page-play-builder | programmatic / parasite / comparison / local 四模式页面打法——模板批量页、第三方平台发布、对比页、本地 SEO。 |
| ⛩ content-quality-auditor | 80 项 CORE-EEAT 发布就绪门（SHIP/FIX/BLOCK）。 |
| technical-seo-checker | 站点速度、Core Web Vitals、索引、可抓取性、robots。 |
| on-page-seo-checker | 审计页面级 on-page 健康度——标题层级、关键词布局、图片、质量信号。 |
| site-structure-optimizer | 内链结构、锚文本分布、孤立页 + 页面层级、导航、URL 分类、hub/spoke 主题集群。 |
| ⛩ domain-authority-auditor | 40 项 CITE 域名信任门（TRUSTED/CAUTIOUS/UNTRUSTED）。 |
| rank-tracker | 跟踪关键词排名、位次变化与跌幅。 |
| performance-monitor | 多指标 SEO/GEO 绩效报告与看板 + 排名/流量/外链/技术/AI 可见性告警。 |
| offsite-signal-analyzer | 外链档案、链接质量、毒链、锚文本分布 + 在你自己的 GA4 / GSC / 服务器日志中度量 AI 助手引荐流量。 |

</details>

### 自然社媒 — ECHO（16）

`social/` 下四个阶段按 Explore → Craft → Host → Observe 排布。`social-quality-auditor` 选用 `asset-gate` 或一个 program-maturity profile；两类构念绝不混用。本学科不含任何发帖、互动或私信自动化。

| 阶段 | 技能 |
|------|------|
| **Explore 探索** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft 创作** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host 运营** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe 观测** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>逐技能用途（自然社媒）</b></summary>

| 技能 | ECHO 杠杆 | 用途 |
|------|-----------|------|
| channel-portfolio-planner | E | 频道组合选型——按 ICP/资源在西方平台与 **中文平台（小红书 / 微信公众号 / 视频号 / 抖音）** 之间分配投入、主/辅频道定位、频道对照 channel-registry 认领。 |
| voice-dossier-builder | C | 品牌语气档案——嗓音、口吻、词表与红线，跨频道一致。 |
| platform-norm-profiler | E | 平台规范画像——每个平台的格式、节奏、社区红线与算法偏好（含中文平台差异）。 |
| participation-warmup-planner | E | 冷启动前的真实参与预热——先融入社群再发声，genuine-question 才是入场券（非刷量）。 |
| social-calendar-builder | C | 社媒排期表——主题支柱、频次上限、跨频道内容日历（over-posting 是 H 守卫项）。 |
| social-creative-builder | C | 单条社媒创意——钩子、正文、CTA、话题标签，感知声明台账（C1）。 |
| short-video-scripter | C | 短视频脚本——Reels/Shorts/TikTok/**视频号/抖音** 的分镜、口播与开头 3 秒钩子。 |
| advocacy-program-designer | C | 员工/用户倡导计划——UGC 采集需**记录授权**（H2），披露物质关联（C2）。 |
| ⛩ social-quality-auditor | asset gate / program maturity | 类型化 ECHO 门，一次只审一个单元/profile；绝不混合资产与运营两类构念。写入 `memory/audits/social/`。 |
| engagement-inbox-manager | H | 互动收件箱**规划**——回复优先级、升级路径、模板库（不含任何自动回复/私信）。 |
| social-selling-planner | H | 社交销售规划——创始人 IP、真实关系建立、去自动化的触达节奏。 |
| crisis-response-planner | H | 危机响应预案——分级、发言人、暂停发布、模板（H1 不做刷量/操纵互动）。 |
| social-pulse-monitor | O | 社媒脉搏监控——提及、情感、话题（gdelt.py/tavily.py 为 proxy，始终标注）。 |
| share-of-voice-tracker | O | 声量份额追踪——对竞品的相对声量、周期稳定分母（O1）。 |
| dark-social-attributor | O | 暗社交归因——不可追踪引荐、self-reported 渠道、复制粘贴分享估算。 |
| social-measurement-loop | O | 把一次社媒动作相对基线在窗口内回读 → Promote / Keep-testing / Rollback / Unproven。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[trend-spotter](../influencer/scout/trend-spotter/SKILL.md)、[audience-mapper](../influencer/scout/audience-mapper/SKILL.md)、[content-amplifier](../influencer/activate/content-amplifier/SKILL.md)、[outreach-manager](../influencer/activate/outreach-manager/SKILL.md)、[competitor-tracker](../influencer/target/competitor-tracker/SKILL.md)、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)、[report-generator](../influencer/report/report-generator/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)、[community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md)、[creator-registry](../protocol/creator-registry/SKILL.md)、[page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md)、[memory-management](../protocol/memory-management/SKILL.md)。社媒真相注册表 `channel-registry` 位于协议层。

**中文平台覆盖：** 小红书 / 微信公众号 / 视频号 / 抖音以**手动数据包 / 用户导出**方式接入（无 keyless 官方公开 API）——技能照常在 Tier 1 用你粘贴或导出的数据运行；西方平台另配 keyless 连接器 `bluesky.py`、`fediverse.py`、`discourse.py` 与 `youtube.py --rss`。平台接入细节见 [social-platform-access.md](../references/social-platform-access.md)。

</details>

### 邮件营销 — SEND（16）

`email/` 下四个阶段目录按 SEND 循环排布；本学科的门（⛩ email-quality-auditor）位于 Deliver。只有门计算目标加权 EQS——其余技能各管一个杠杆并交棒。用例无关（B2C 生命周期 / B2B 冷触达 / newsletter-creator），由目标权重列决定侧重。

| 阶段 | 技能 |
|------|------|
| **Setup 搭建** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage 触达** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture 培育** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver 投递** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>逐技能用途（邮件营销）</b></summary>

| 技能 | SEND 杠杆 | 用途 |
|------|-----------|------|
| deliverability-qa | S | 发送前 SPF/DKIM/DMARC/BIMI 认证、声誉、收件箱落位、垃圾内容、列表卫生（S1 检查）。 |
| list-segment-builder | E | 从自有列表/CRM/GA4 导出构建行为 + 生命周期阶段分群与抑制规则。 |
| list-growth-designer | S（+N） | 列表增长策略——获取渠道、lead magnet 构思、合规的双重确认捕获流程 spec、推荐环机制；在获取点保证 S 同意质量。 |
| list-hygiene-monitor | S | 列表卫生监控——退信/未互动清理、sunset 政策、垃圾陷阱与投诉率治理。 |
| email-creative-builder | E / D | 主题行/预览文本/正文/CTA，与落地页信息一致，感知声明台账。 |
| subject-line-lab | E | 主题行/预览文本创意与迭代——角度矩阵、长度/emoji/个性化实验、垃圾触发词规避。 |
| email-render-builder | E / D | 邮件 HTML 渲染 QA——跨客户端兼容、暗色模式、纯文本 fallback、可访问性。 |
| dynamic-content-personalizer | E | 动态内容/合并标签个性化——受众条件块、回退值、渲染安全校验。 |
| email-sequence-designer | N | 生命周期/自动化流程（欢迎、弃购、购后、召回）+ 频次治理。 |
| newsletter-monetization-planner | D | 付费订阅、赞助位库存 + 刊例、推荐增长循环经济。 |
| preference-frequency-manager | N | 偏好中心与频次治理——订阅主题、频次上限、降频而非退订路径。 |
| reactivation-specialist | N | 沉睡用户召回——win-back 序列、再确认、sunset 前最后一搏。 |
| ⛩ email-quality-auditor | S+E+N+D（EQS） | auditor-class SEND 门：算 EQS、跑 S1/S2/N1/D1、产出 SHIP/FIX/BLOCK；含**发送前 go/no-go**模式。写入 `memory/audits/email/`。 |
| send-experiment-designer | E | A/B / 发送时间 / hold-out 设计，含样本量 + 显著性判读（promote/kill）。 |
| inbox-placement-monitor | S | 收件箱落位监控——seed 列表、垃圾/推广标签分布、ISP 级声誉追踪。 |
| cold-outbound-sequencer | D | B2B 冷触达序列——分步跟进节奏、合规同意/退订、送达与回复优化。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[audience-mapper](../influencer/scout/audience-mapper/SKILL.md)、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)（点击后）、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)（回报计算）、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)。

</details>

### 付费广告 — ROAS（16）

`ad/` 下四个阶段目录按 ROAS 循环排布；本学科的门（⛩ ad-account-auditor）位于 Activate。只有门计算目标加权 RQS——其余技能各管一个杠杆并交棒。

| 阶段 | 技能 |
|------|------|
| **Research 研究** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate 编排** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate 激活** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale 放大** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>逐技能用途（付费广告）</b></summary>

| 技能 | ROAS 杠杆 | 用途 |
|------|-----------|------|
| campaign-architect | A + 结构 | 账户/活动结构、campaign 类型选型、匹配类型、否定词/排除、付费↔自然蚕食。 |
| audience-segment-builder | A | 把自有客户/CRM/GA4 导出转为种子受众、相似种子、排除人群、跨平台漏斗分层地图。 |
| search-term-miner | A | 从搜索词报告挖掘新增否定词与拓展词，收敛匹配类型漏斗。 |
| product-feed-optimizer | O | Shopping/PMax 商品 feed 质量——标题/属性/GTIN、feed 覆盖与拒登修复。 |
| ad-creative-builder | O | RSA 标题/描述、hook、角度矩阵，并与落地页信息一致。 |
| ad-test-designer | O（+S） | 设计 A/B/n 与增量实验（假设、变体矩阵、样本量/功效），判读显著性 → promote/kill。 |
| bid-strategy-planner | S | 出价策略选型、tCPA/tROAS 目标设定、学习期与出价上限规划。 |
| landing-experience-checker | O | 点击后落地体验 QA——信息一致、加载速度、移动端、转化路径。 |
| ⛩ ad-account-auditor | R+O+A+S（RQS） | auditor-class ROAS 门：算 RQS、跑 R1/R2/O1/O2/A1、产出 SHIP/FIX/BLOCK；含**上线 go/no-go**模式。 |
| conversion-signal-qa | R | 上线前追踪 QA（事件触发、UTM 规范、去重门控、窗口对齐、iOS-ATT 标记）——R1/R2 的前置（建信号，门打分）。 |
| placement-exclusion-manager | S | 版位/展示位排除——低质站点、app 品类、品牌安全清单治理。 |
| conversion-value-mapper | R | 把转化事件映射到价值/毛利，配置价值规则与 tROAS 目标信号。 |
| paid-measurement-loop | R（+S） | 把一次上线的改动相对对照在窗口内回读 → Promote / Keep-testing / Rollback / Unproven。 |
| attribution-reconciler | R | 针对 GA4/ecommerce 订单ID真值集做常态去重、窗口/币种归一、模型对比、增量。 |
| budget-pacing-monitor | S | 预算消耗节奏监控——超支/欠支告警、日内配速、月度落点预测。 |
| fatigue-frequency-manager | O（+S） | 创意疲劳与频次治理——频次上限、轮换节奏、衰减信号识别。 |

**跨学科复用**（计入原阶段，不重复造轮子）：[budget-optimizer](../influencer/target/budget-optimizer/SKILL.md)（花费 + 出价节奏/学习期模式）、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)（点击后）、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)（回报计算）、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)。

</details>

### 红人 — STAR（16）

四个阶段目录沿 STAR 循环（Scout 侦察 → Target 锁定 → Activate 启动 → Report 汇报；原 6 阶段 insight+map→scout、activate+convert→activate、track→report）；循环与质量基准现同为 STAR（Suitability · Trust · Appeal · Return）；本学科的门（⛩ creator-content-auditor）位于 Activate。

| 阶段 | 技能 |
|------|------|
| **Scout 侦察** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target 锁定** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate 启动** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report 汇报** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>逐技能用途（红人）</b></summary>

| 技能 | 用途 |
|------|------|
| audience-mapper | 在项目开始或进入新细分时做受众画像，并摸清某个亚文化 / 微社群。 |
| trend-spotter | 活动节奏与主题——趋势话题、声音、内容格式、文化时刻。 |
| influencer-discovery | 从零搭建红人名单、拓展新平台、规模化找 nano/micro。 |
| fit-scorer | 对候选名单做客观加权适配打分（基于 STAR Suitability (S)）。 |
| competitor-tracker | 竞品的合作红人、活动、格式、估算触达/花费与缺口。 |
| campaign-planner | 规划活动、产品发布、tentpole 或常态化创作者项目。 |
| brief-generator | 标准化红人 brief 与可复用团队模板。 |
| budget-optimizer | 跨层级/平台分配预算、预测 ROI、建模场景（同时服务付费广告的花费 + 出价节奏）。 |
| outreach-manager | pitch、跟进节奏、再激活、费率谈判、状态跟踪。 |
| ⛩ creator-content-auditor | 对红人提交内容做发布前门决策（STAR Trust：FTC 披露 STAR-T1、声明真实性 STAR-T2）。 |
| contract-helper | 起草/审阅创作者协议——使用权、独家、标准条款。 |
| content-amplifier | 用付费投放放大自然创作者内容（白名单、Spark Ads、暗帖），并把 UGC 二次利用到付费、网站、邮件、自然社媒。 |
| landing-optimizer | 面向创作者/付费流量的落地页——信息一致、移动端、A/B（同时服务付费点击后）。 |
| performance-analyzer | 评估创作者结果、横比创作者、情感、转化（同时是付费跨渠道记分卡）。 |
| roi-calculator | 度量/预测 ROI、为预算辩护、评估创作者/层级价值（共享回报计算引擎，含付费）。 |
| report-generator | 周期结束后面向特定利益相关者的书面报告（同时出付费广告报告）。 |

</details>

### 产品发布 — RAMP（16）

`launch/` 下四个阶段按 Research → Assemble → Mobilize → Prove 排布。`launch-readiness-auditor` 每次运行只选一个 `preflight`、`execution` 或 `outcome` profile；生命周期结果只做关联，绝不取平均。

| 阶段 | 技能 |
|------|------|
| **Research 研究** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble 组装** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize 动员** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove 证明** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>逐技能用途（产品发布）</b></summary>

| 技能 | 用途 |
|------|------|
| positioning-mapper | 定位画布——竞争替代品、独特价值、滩头细分。 |
| launch-tier-planner | 发布分级与发布类型选型、风险登记册、kill criteria。 |
| launch-window-planner | 发布择时——竞品日历、禁运期窗口、平台审核缓冲。 |
| early-access-designer | waitlist 与内测阶梯、毕业标准、反馈闭环。 |
| message-house-builder | 消息屋 / PR-FAQ——价值支柱与发布叙事。 |
| launch-asset-packager | 资产清单、press kit、商店 listing 规格、上线检查。 |
| pricing-packaging-planner | 发布定价、梯度打包、早鸟优惠、保证设计。 |
| sales-enablement-kit | battle card、销售叙事、异议处理、内部 FAQ。 |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | 类型化 RAMP 门，一次只审一个生命周期读数；绝不跨时间视界取平均。写入 `memory/audits/launch/`。 |
| launch-day-conductor | 发布日 runbook——作战室、观察窗、回滚裁决。 |
| community-launch-runner | 社区发布——PH/HN 提交包、目录波次、平台红线。 |
| press-media-relations | 媒体名单、禁运期 pitch、新闻稿、分析师简报。 |
| launch-monitor | 发布监控——排名轮询、火焰战比、spike-vs-sustain。 |
| launch-feedback-synthesizer | 反馈分诊、状态环、社证收割、you-asked-we-shipped。 |
| launch-retro-analyzer | 发布复盘——渠道归因、5-Whys、keep/kill 决策。 |
| momentum-planner | 抗第二周断崖——changelog-as-GTM、relaunch、下一发布时刻。 |

</details>

### 协议层（8）

共享真相与记忆机件——角色与唯一写入者规则见上文[架构 § 协议层](#协议层)。

| 组 | 技能 |
|----|------|
| **协议层** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>逐技能用途（协议层）</b></summary>

| 技能 | 用途 |
|------|------|
| entity-registry | 面向知识图谱、Wikidata、AI 消歧的规范实体档案。 |
| creator-registry | 规范创作者名册/档案——去重 handle、带溯源标签的受众数据、费率与合规历史。 |
| offer-claims-registry | 规范 offer 与声明实证台账——O1/T2 声明检查所对照评判的那份记录。 |
| consent-registry | 规范的按主体邮件同意/抑制 SSOT——退订/退信/投诉历史，S2/N1 否决项对照评判。 |
| launch-registry | 发布台账/发布日历——分级、阶段（draft→GA 单向）、权威日期与禁运期承诺的唯一真相（launch SSOT）。 |
| channel-registry | 规范频道台账——去重 handle、按平台归属、粉丝/互动率基线（命名/周期稳定分母）、认领状态与运营史（social SSOT，ECHO E1 对照评判）。 |
| narrative-registry | 规范品牌准则 SSOT——叙事、消息系统、语言红线与定位真相；TALE 门与各频道 creative builder 对照评判并继承（narrative SSOT）。 |
| memory-management | 审阅、提升、降级、归档 HOT/WARM/COLD 项目记忆。 |

</details>

---

## 命令

8 个命令：`/aaron-marketing:auto` 跨七学科路由任意目标；每个学科恰有一个显式入口。源文件：[commands/](../commands)。

| 命令 | 用途 | 收窄 |
|------|------|------|
| `/aaron-marketing:auto` | 描述任意目标——推断意图并执行最小够用的工作流 | `--deep`（穷尽/压测） |
| `/aaron-marketing:narrative` | 品牌叙事（TALE 循环）：溯源现状与品类/受众信念、架构消息系统、级联落地与赋能、审计门与共鸣/漂移监控 | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO 端到端（SITE 循环）：勘测需求/竞品、实施内容、调优质量/技术/页面、评估权威/排名/报告/记忆 | `--phase survey\|implement\|tune\|evaluate` + 各阶段子参数（`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`） |
| `/aaron-marketing:influencer` | 红人（STAR 循环）：受众洞察、侦察与适配、锁定规划、外联、放大、ROI 汇报 | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | 付费广告（ROAS 循环）：分群、结构、创意、实验设计、审计门、衡量 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | 邮件营销（SEND 循环）：送达/同意、分群、创意、生命周期流程、变现、发送测试、审计门 | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | 产品发布（RAMP 循环）：定位与分级、择时、消息屋与资产组装、就绪审计门、发布日执行、复盘与势能 | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | 自然社媒（ECHO 循环）：频道组合与语气、内容日历与创作、运营与质量门、脉搏与度量 | `--phase explore\|craft\|host\|observe` |

日常工作通常从 `/aaron-marketing:auto` 开始；其余七个是显式的学科入口，用 `--phase` 收窄阶段。

---

## 连接器与层级

技能用 `~~category` 占位符（`~~SEO tool`、`~~web analytics`、`~~ad platform` 等）而非具体厂商命名，且每个类别都有 **keyless 的 Tier-1 路径**。完整配方（含每个类别的免费/第一方端点）见 [CONNECTORS.md](../CONNECTORS.md)。

### 连接器层本身就是一件产品

**100+ 条记录在案的集成路径**，分三个精心设计的层——每一条都名副其实：

| 层 | 你得到什么 |
|----|------------|
| **28 个内置零依赖连接器** | 纯 Python 标准库——无 `pip`、无构建。keyless 实时 SERP + JS 渲染抓取（Firecrawl、Tavily）、AI 答案引用探针、DNS-over-HTTPS 邮件认证拉取、维基百科关注度序列、GDELT 新闻提及、真实 YouTube 创作者指标、IndexNow + 百度收录推送、Resend ESP 自动化，以及能把任何数据源变成前后对比时间序列的 git 可差分测量台账。 |
| **60+ 个记录在案的官方/免费 API** | 每一行都链接厂商**官方文档**、带核验日期，且每条链接入库前都经过 HTTP 实测。包含多数工具清单遗漏的路径：GSC URL Inspection、CrUX History（40 周真实用户 CWV）、Gmail Postmaster Tools API、Meta 广告库、微软 Clarity 数据导出 API。 |
| **厂商 MCP 服务器** | 18 个远程端点入目录（绝不自动注册——你的 `/mcp` 列表保持干净），外加 Google Analytics、Search Console、**Google Ads**、**微软 Clarity** 的官方自托管服务器。其中两个远程 MCP 完全免鉴权（Firecrawl、Tavily）。 |

让它们可信而不只是数量多的四个理由：

- **三类安全等级、工程化门控**（[SECURITY.md](../SECURITY.md)）：托管抓取器在每次委托抓取前**本地预检 robots.txt**、遇 Disallow 拒绝执行；一切改变外部状态的操作（发邮件、推送收录）**默认 dry-run**，必须显式 `--live` 才执行，厂商支持幂等键就用、不支持就绝不自动重试。
- **核验，然后再核验**：端点对照厂商一手文档带日期核实、keyless 路径经过真实调用测试、CI 守卫强制版本/跟踪同步、发版前的 live 冒烟专抓端点漂移（它已经两次抓到真实的 API 变更）。
- **只报事实、不下判定**：连接器输出记录存在性、解析标签和原始序列；裁决交给 auditor 门，技能给每个数字标注 **Measured / User-provided / Estimated**。
- **成文的 playbook**（[docs/connector-playbook.md](connector-playbook.md)）管辖每一次新增——定性、验证、实现、测试、接线、文档、跟踪、回归、归档——目录再增长，质量不滑坡。

| 层级 | 需要 | 你获得 |
|------|------|--------|
| **Tier 1**（默认） | 无 | 粘贴数据，或从免费/公开来源拉取。分析框架照常运行。 |
| **Tier 2** | 一个免费第一方 API 或 MCP | 自动取你自己的 GSC / GA4 / Core Web Vitals 数据。 |
| **Tier 3** | 更完整的 MCP 集 | 全自动多源工作流。 |

- **内置零依赖助手** 位于 `scripts/connectors/`（仅 Python 标准库），在本地拉取公开/自有数据——如 PageSpeed/CrUX、Open PageRank、页面抓取、Wayback CDX、Wikidata SPARQL、Common Crawl、advertools 配方——外加 **`resend.py`**：邮件技能直连 Resend ESP 的自动化（免费档 key：发件域认证状态、种子测试投递、抑制名单同步、广播定时发送；变更类子命令默认 dry-run，需 `--live` 才执行）；以及 **`firecrawl.py`** + **`tavily.py`**：研究类技能直连托管抓取器的 keyless 自动化（Firecrawl：实时搜索结果 + JS 渲染页 markdown + 站点 URL 清单；Tavily：带评分的搜索 + AI 答案引擎引用来源探针（GEO 用）+ URL 提取——两者完全无需 key，均内置本地 robots.txt 预检）。
- **免费/keyless 来源** 按类别记录：Google Search Console 与 GA4（自有数据）、PageSpeed/CrUX、Wikidata、Common Crawl、Open PageRank、Firecrawl keyless SERP/抓取、Tavily keyless AI 搜索、DNS-over-HTTPS 邮件认证记录（`doh.py`）、维基百科关注度序列（`pageviews.py`）、GDELT 新闻提及（`gdelt.py`）、免费 key 的 YouTube 创作者指标（`youtube.py`）、IndexNow + 百度收录推送（`indexpush.py`，dry-run 门控）、广告透明库（Meta/Google/TikTok），以及 crt.sh、W3C 校验器、oEmbed、HN Algolia 的配方行。
- **可选 MCP 服务器**（Ahrefs、Semrush、SE Ranking、SISTRIX、SimilarWeb、自托管免费的 **OpenSEO** 套件、Cloudflare、Vercel、HubSpot、Amplitude、Notion、Webflow、Sanity、Contentful、Slack、Resend、keyless 的 Firecrawl 与 Tavily）在 [`docs/mcp-catalog.json`](mcp-catalog.json) 中作为**仅复制粘贴参考**——目录位于会被自动注册的插件根 `.mcp.json` 路径之外，不会为你注册任何东西。把你想要的条目复制进自己的 MCP 配置即可。

付费广告技能基于你的**自有账户手动导出**（原生广告管理后台 CSV、GA4、电商）评分。带密钥的广告 API（Google Ads SDK、Meta Marketing API）仅是 opt-in Tier-2/3，**绝不**作为 Tier-1 要求。邮件技能同理——基于你**自己的 ESP 导出**评分，所有送达率信号均 keyless（DNS 查询、DMARC RUA 报告、种子收件测试），带密钥的 ESP API 也绝不是 Tier-1 要求；若你的 ESP 是 Resend，内置的 `resend.py` 可在免费档上自动化同一闭环。

---

## 推荐工作流

真实目标大多横跨多个学科。`/aaron-marketing:auto` 会把一句自然语言目标路由到七个学科中最小可用的技能链——比如一次产品发布会同时调动 Launch、Email、Social 与 Paid：

```text
/aaron-marketing:auto 三周后在 Product Hunt 发布 v2——等候名单 1,200 人；需要发布页、邮件序列和发布日计划
```

也可以端到端驱动单个学科的循环（各学科目录下的 `README.zh.md` 学科指南提供场景级打法）：

**品牌叙事（TALE 循环）**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor`（⛩ TALE 门）→ `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO（SITE 循环）**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor`（⛩ 发布门）→ `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`；信任评审用 `domain-authority-auditor`（⛩）

**自然社媒（ECHO 循环）**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor`（⛩ ECHO 门）→ `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**邮件营销（SEND 循环）**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` （⛩ EQS 门），在任何发送前

**付费广告（ROAS 循环）**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` （落地页配 `landing-optimizer`）
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` （⛩ RQS 门），在任何预算上线前
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**红人（STAR 循环）**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer`（STAR Suitability）
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor`（⛩ STAR 门）→ `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**产品发布（RAMP 循环）**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor`（⛩ RAMP 门）→ `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

要做完整信任评审，把 `content-quality-auditor` 与 `domain-authority-auditor` 搭配，得到合计 120 项的评估。开启 `memory-management` 后，交棒与未决事项自动留存在 HOT/WARM/COLD 记忆中。

---

## 仓库结构

```
narrative/{trace,architect,land,evaluate}/          # 品牌叙事 — TALE(16，含其门)
seo-geo/{survey,implement,tune,evaluate}/                  # SEO/GEO(16，含其 2 个门)
influencer/{scout,target,activate,report}/                   # 红人(16，含其门)
ad/research|orchestrate|activate|scale/            # 付费广告 — ROAS(16，含其门)
email/setup|engage|nurture|deliver/                  # 邮件营销 — SEND(16，含其门)
launch/research|assemble|mobilize|prove/             # 产品发布 — RAMP(16，含其门)
social/explore|craft|host|observe/                   # 自然社媒 — ECHO(16，含其门)
protocol/                                            # 协议层(8) — 真相注册表 + 记忆
commands/        # 8 个斜杠命令(auto、narrative、seo-geo、influencer、ad、email、launch、social)
references/      # 共享契约、状态模型、八套基准、auditor runbook、平台资料包
evals/           # 各技能结构化 eval 用例 + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh(唯一运行逻辑)
scripts/         # validate-skill.sh + connectors/(标准库) + CI 守卫
memory/          # HOT/WARM/COLD 脚手架 + 注册表存储(entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # 本地化 README(zh)
.claude-plugin/  # plugin.json + marketplace.json 镜像
```

---

## 设计哲学

- **内容优先。** 技能是 Markdown；零依赖的 Bash/Python 标准库运行时提供连接器、评分、注册表事件、校验与检查。第三方 / `pip` 依赖被 CI 明令禁止。
- **keyless 优先。** 每个 `~~category` 都有免费/自有数据配方；MCP 与付费工具纯属便利。
- **外科手术式 & MECE。** 每个技能只担一项职责，边界清晰；重叠的工作做成现有技能的*模式*，而非新堆一个薄技能。注册表存证、门评判、分析器喂门。
- **不编数字。** 技能为每个数据标注 Measured / User-provided / Estimated，并内置 AI 腔 / 禁用词检测。
- **合规是指引，不是法律。** FTC 披露与声明真实性检查标注风险，但不构成法律意见。

---

## 质量守卫

每次变更都跑一组 fail-closed 守卫（均在 `scripts/` 与 `tests/`）：

| 守卫 | 检查 |
|------|------|
| `validate-skill.sh` | 全部 120 个技能的 frontmatter、必备章节、版本一致性、插件相对链接。 |
| `golden-auditor-math.py` | **八套**框架的权重和 + 工作示例算术的确定性校验。 |
| `check-evals.py` | eval 结构 lint + `structure-manifest.json`（120/120 技能均带 eval 用例）。 |
| `check-pii.py` | 拦截提交的密钥 / PII（token 级允许名单，fail-closed）。 |
| `check-stdlib-only.sh` | 依赖蔓延守卫 + 付费广告带密钥 API 红线。 |
| `check-versions.sh` | 版本同步守卫：system catalog、plugin/marketplace/OpenClaw manifests、根与本地化 README 徽章、AGENTS/CLAUDE/VERSIONS、GitHub About 和 120 个 skill 版本保持一致。 |
| `tests/test_connectors_local.py` | 覆盖全部 29 个内置连接器模块之请求构建器／解析器的离线测试（CI 不联网）。 |
| `tests/test_hook_artifact_gate.sh` | hook 的 Artifact Gate + SessionStart 净化的行为测试。 |

线上端点漂移由**手动**的 [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) 另行抽样——对脚本中列出的每个托管连接器做一次最小真实调用 + 响应形状断言（限速应答记 SKIP）；发版前手动跑，绝不进 CI。

---

## 贡献与文档

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** —— 撰写规则、贡献清单，以及权威的 10 个追踪面清单。
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** —— 各技能版本 + 变更日志（当前包：`19.1.0`）。
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** —— 安全、隐私、社区政策。
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** —— 面向 Agent 的本仓库上下文。

---

## 免责声明

这些技能用于辅助品牌叙事、SEO/GEO、红人营销、付费广告、邮件营销、产品发布与自然社媒工作流，但**不**保证排名、AI 引用、流量、互动、转化、ROAS 或任何业务结果。红人与广告合规检查（FTC 披露、声明真实性、平台政策）为指引，非法律意见。在用于重大策略、财务或法律决策之前，请与具备资质的专业人士核实建议。

## 许可证

Apache License 2.0 —— 见 [LICENSE](../LICENSE)。

*最后同步英文 README：v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left&sealed_token=K6urMhBIrcVIXJvMDWhgZP6KneM8cTo073XO6c-99j4vYWm7J_YIu_W3HFewr-QySk00ZWB9V0Btf-aJPMWiYZjcmuIqBh2G6aEd69Sw43PX7ypi90Il-lwwtdBkmx_1g_Sw589a2axs_lHmFfnANYjjmJwtTtmXy7RY07-HAASvV5LxsgpYwabVPwKZ" />
 </picture>
</a>
