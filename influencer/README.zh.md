<div align="center">

# 红人 — STAR

**发现、甄别、激活、度量创作者 —— 每次合作都用 STAR 打分。**

[English](README.md) | 简体中文

</div>

> 这是 **[Aaron 营销技能库](../docs/README.zh.md)** 中的一个学科 —— 全库 120 个技能、七个学科、共享一套契约。要看整套体系、四层地图与安装步骤，请从[主 README](../docs/README.zh.md) 开始。

红人是一个 **L2 · 频道**（偏 episodic）—— 通过创作者合作，借可信声音承载品牌叙事。十六个技能跑通 **STAR** 循环 —— **S**cout 侦察受众与创作者，**T**arget 锁定短名单并规划项目，**A**ctivate 激活触达与合规内容，再 **R**eport 汇报回报。创作者名册与档案存在 [`creator-registry`](../protocol/creator-registry/SKILL.md)（红人真相 SSOT）；质量门是 [`creator-content-auditor`](activate/creator-content-auditor/SKILL.md)。循环与质量框架现在共用 **STAR** 之名 —— 与 ROAS / SEND / ECHO / RAMP / TALE 对称。

## 循环 — Scout → Target → Activate → Report

- **Scout（侦察）** —— 建池子：刻画受众及其微社群、读文化时机、从零发现创作者，并给短名单打匹配分（Suitability 读数）。
- **Target（锁定）** —— 定方案：追踪竞品的创作者、规划 campaign/项目、生成标准化 brief，并按层级分配预算。
- **Activate（激活）** —— 安全上线：跑触达与谈判、让每一份投稿过 STAR 门、处理合同，并放大/再利用内容。
- **Report（汇报）** —— 证明有效：优化创作者/付费落地页、分析表现、计算 ROI，并撰写利益相关方报告。

> 注：这里的 **Activate** 指*创作者触达* —— 同一个阶段词在付费广告学科里指*账户放行*。

## 16 个技能

链接指向各自的 `SKILL.md`。⛩ 标记本学科的 auditor 级质量门。

| 阶段 | 技能 | 作用 |
|------|------|------|
| **Scout** | [audience-mapper](scout/audience-mapper/SKILL.md) | 在与创作者合作前，刻画目标受众并绘制其亚文化/微社群。 |
| **Scout** | [trend-spotter](scout/trend-spotter/SKILL.md) | Campaign 时机与主题 —— 走红的话题标签、音频、格式、文化时刻。 |
| **Scout** | [influencer-discovery](scout/influencer-discovery/SKILL.md) | 从零建创作者名册、扩展到新平台、规模化寻源 nano/micro。 |
| **Scout** | [fit-scorer](scout/fit-scorer/SKILL.md) | 为短名单给出客观、加权的匹配分 —— 产出 STAR **Suitability (S)** 读数。 |
| **Target** | [competitor-tracker](target/competitor-tracker/SKILL.md) | 某竞品的创作者、campaign、格式、估算触达/花费与缺口。 |
| **Target** | [campaign-planner](target/campaign-planner/SKILL.md) | 规划一次 campaign、产品发布、tentpole，或常态创作者项目。 |
| **Target** | [brief-generator](target/brief-generator/SKILL.md) | 标准化红人 brief 与可复用的团队模板。 |
| **Target** | [budget-optimizer](target/budget-optimizer/SKILL.md) | 在层级/平台间分配花费、预测 ROI、建模情景（也服务付费广告花费 + 出价配速）。 |
| **Activate** | [outreach-manager](activate/outreach-manager/SKILL.md) | Pitch、跟进节奏、再触达、费率谈判、状态追踪。 |
| **Activate** | ⛩ [creator-content-auditor](activate/creator-content-auditor/SKILL.md) | Auditor 级 STAR 门：对创作者投稿做发布前判定（STAR Trust —— FTC 披露 STAR-T1、声明诚信 STAR-T2），产出 SQS + SHIP/FIX/BLOCK。 |
| **Activate** | [contract-helper](activate/contract-helper/SKILL.md) | 起草/审阅创作者协议 —— 使用权、独家、标准条款。 |
| **Activate** | [content-amplifier](activate/content-amplifier/SKILL.md) | 用付费花费延展自然创作者内容，并把 UGC 跨付费、网站、邮件、自然渠道再利用。 |
| **Report** | [landing-optimizer](report/landing-optimizer/SKILL.md) | 面向创作者/付费流量的落地页 —— 信息匹配、移动端、A/B（也服务付费点击后）。 |
| **Report** | [performance-analyzer](report/performance-analyzer/SKILL.md) | 评估创作者结果、对比创作者、情绪、转化（也是付费的跨频道记分卡）。 |
| **Report** | [roi-calculator](report/roi-calculator/SKILL.md) | 度量/预测 ROI、为预算辩护、给创作者/层级估值（共享回报算法引擎，含付费）。 |
| **Report** | [report-generator](report/report-generator/SKILL.md) | 一个周期后的书面利益相关方报告（也用于付费广告报告）。 |

## 质量门 — STAR

[STAR](../references/star-benchmark.md) 从四个维度评估红人营销 —— **S**uitability 契合度 · **T**rust 信任 · **A**ppeal 吸引力 · **R**eturn 回报（40 项 / 4 维）。**SQS = floor(档加权平均)** —— 与 ROAS（RQS）、SEND（EQS）同一算术汇总家族。否决项为 `STAR-S2`/`S6`（受众真实性）与 `STAR-T1`/`T2`/`T3`（披露/声明/品牌安全）—— 务必带框架名限定，因为这些 ID 与 SEND/ROAS/RAMP/TALE/CITE/CORE-EEAT 在文字上撞号。[`fit-scorer`](scout/fit-scorer/SKILL.md) 在短名单阶段产出 Suitability 读数；[`creator-content-auditor`](activate/creator-content-auditor/SKILL.md) 是发布前的门。共享机制见 [auditor-runbook.md](../references/auditor-runbook.md)。

## 快速开始

```text
/aaron-marketing:influencer              # 从你的输入推断 STAR 阶段
/aaron-marketing:influencer --phase scout | target | activate | report
```

```text
/aaron-marketing:influencer 为护肤新品找 TikTok 创作者并给他们打匹配分
```

每个技能都在 **Tier 1** 用你粘贴的数据即可运行；连接器读取仅限短名单甄别范围。

## 推荐场景

| 你的处境 | 从这里开始 | 得到什么 |
|---|---|---|
| 为一次发布找创作者 | `/aaron-marketing:influencer --phase scout` → `influencer-discovery` → `fit-scorer` | 一份甄别过的名册 + 加权 Suitability 分 |
| 创作者发来初稿待审 | `--phase activate` → `creator-content-auditor` | STAR 发布前判定（FTC 披露、声明诚信） |
| 这份短名单真的契合吗？ | `fit-scorer` | 每位创作者一个客观、加权的 STAR Suitability 读数 |
| 这个项目赚回来了吗？ | `--phase report` → `roi-calculator` → `report-generator` | ROI 算法 + 利益相关方报告 |
| 竞品在用创作者做什么？ | `--phase target` → `competitor-tracker` | 他们的创作者、格式、估算触达/花费与缺口 |

## 与其他学科共享

红人是可复用引擎技能的**主场** —— 它的 16 个技能里有几个在别处兼职：[budget-optimizer](target/budget-optimizer/SKILL.md)、[landing-optimizer](report/landing-optimizer/SKILL.md)、[roi-calculator](report/roi-calculator/SKILL.md)、[report-generator](report/report-generator/SKILL.md) 与 [performance-analyzer](report/performance-analyzer/SKILL.md) 也服务付费广告；[audience-mapper](scout/audience-mapper/SKILL.md) 与 [trend-spotter](scout/trend-spotter/SKILL.md) 也服务产品发布与社媒；[outreach-manager](activate/outreach-manager/SKILL.md) 与 [content-amplifier](activate/content-amplifier/SKILL.md) 也服务产品发布与社媒。它们只在此处计数一次。

## 连接器

仅短名单甄别读取：[`youtube.py`](../scripts/connectors/youtube.py)（免费 key 的创作者指标 —— 真实订阅/观看数；也有 keyless `--rss` 模式）、[`bluesky.py`](../scripts/connectors/bluesky.py)（创作者档案 + 互动 + 抢注审计）、[`fediverse.py`](../scripts/connectors/fediverse.py)，以及 [`tavily.py`](../scripts/connectors/tavily.py)（打分发现搜索）。专有服务保持外置：Upfluence 是 opt-in 远程 MCP，NoxInfluencer 是外部 Skill/CLI companion，Scrumball 在完成认证字段验证前只是 REST/API recipe。它们只提供证据，不提供 STAR 判决；模型推断的受众、真实性、费率和 ROI 仍标 Estimated。不得批量抓取或镜像供应商数据库。完整清单与授权边界见 [CONNECTORS.md](../CONNECTORS.md)。

---

<sub>属于 [Aaron 营销技能库](../docs/README.zh.md) · [系统架构](../docs/system-architecture.md) · [STAR 基准](../references/star-benchmark.md) · [贡献指南](../CONTRIBUTING.md)</sub>
