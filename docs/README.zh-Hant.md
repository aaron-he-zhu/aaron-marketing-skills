<div align="center">

# Aaron 行銷技能庫

**120 個行銷技能 —— 品牌敘事、SEO/GEO、紅人、付費廣告、郵件、產品發布、社媒 —— 共享一套契約。**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
<!-- GENERATED:BEGIN release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-20.0.0-orange" alt="Version"></a>
<!-- GENERATED:END release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | **繁體中文**

</div>

一套 Claude 技能與斜線命令，讓聊天 Agent 成為行銷操作員。七個學科 + 一個共享協議層，一圖總覽：

| 層 | 技能 | 生命週期（階段目錄） | 框架 → 門 | 入口命令 |
|----|------|----------------------|-----------|----------|
| **品牌敘事** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **社媒** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **郵件** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`（EQS） | `/aaron-marketing:email` |
| **付費廣告** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`（RQS） | `/aaron-marketing:ad` |
| **紅人** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor`（SQS）；`fit-scorer` 打 Suitability (S) 分 | `/aaron-marketing:influencer` |
| **產品發布** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **協議層** | 8 | ——（階段流程之外的共享機件） | 7 個真相註冊表（entity · creator · offer/claims · consent · launch · channel · narrative）+ HOT/WARM/COLD 記憶 | —— |

`/aaron-marketing:auto` 可把任意自然語言目標路由到整套體系。技能與命令都是**純 Markdown**；小型 Bash/Python 標準庫執行時提供 hooks、驗證、評分、註冊表事件、連接器與 CI 檢查（無 `pip`、無建置步驟）。**每個技能都在 Tier 1 用你提供的資料即可執行**；連接器只自動化資料拉取，或一次經明確核准的變更。

權威的型別化拓撲是 [`references/system-catalog.json`](../references/system-catalog.json)；可讀的四層地圖、全部 120 條路徑、註冊表所有者、auditor 落點與分發檔案見[生成的系統架構文件](system-architecture.md)。

> 合併前的兩個獨立倉庫現均為**純路標倉庫**——[seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)（最終 20 技能版本線保留於 tag `v9.9.12`）與 [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)（最終 IMPACT 版本線保留於 tag `standalone-final`），安裝一律指向本倉庫。兄弟倉庫策略見 [docs/repo-family.md](repo-family.md)。

---

## 目錄

- [為什麼選它](#為什麼選它)
- [安裝](#安裝)
- [初次使用](#初次使用)
- [架構](#架構)
  - [共享技能契約](#共享技能契約)
  - [系統：四層行銷作業系統](#系統四層行銷作業系統)
  - [品質體系：八框架、八門](#品質體系八框架八門)
  - [協議層](#協議層)
  - [記憶與自動化](#記憶與自動化)
- [技能目錄](#技能目錄)
  - [品牌敘事 — TALE（16）](#品牌敘事--tale16)
  - [SEO/GEO — SITE（16）](#seogeo--site16)
  - [紅人 — STAR（16）](#紅人--star16)
  - [付費廣告 — ROAS（16）](#付費廣告--roas16)
  - [郵件行銷 — SEND（16）](#郵件行銷--send16)
  - [產品發布 — RAMP（16）](#產品發布--ramp16)
  - [社媒 — ECHO（16）](#社媒--echo16)
  - [協議層（8）](#協議層8)
- [命令](#命令)
- [連接器與層級](#連接器與層級)
- [推薦工作流](#推薦工作流)
- [倉庫結構](#倉庫結構)
- [設計哲學](#設計哲學)
- [品質守衛](#品質守衛)
- [貢獻與文檔](#貢獻與文檔)
- [免責聲明](#免責聲明)
- [授權條款](#授權條款)

---

## 為什麼選它

| 原則 | 落到實處 |
|------|----------|
| **預設 keyless** | 每個技能都能在 **Tier 1** 僅憑貼上的資料、或從免費/第一方來源拉取的資料執行。付費工具與 MCP 伺服器是選配，絕非前提。付費廣告技能基於**自有帳戶手動匯出**評分——帶金鑰的廣告 API 永不必需。 |
| **內容優先、契約可執行** | 技能始終是 Markdown。小型 Bash/Python 標準庫執行時讓評分、狀態、安全與契約一致性都可確定性執行，且不新增任何套件相依。 |
| **一套共享契約** | 120 個技能暴露同樣的七段結構，並自帶 `discipline` + `phase` 中繼資料，整個庫像一套作業系統：每個技能都知道自己的輸入、輸出，以及下一個該交棒的技能。 |
| **帶門的品質** | 八套基準驅動八個 auditor-class 門，產出結構化、可機器驗證的判定——不是憑感覺。成功/失敗/批次 hook 以有界檢查揭露無效寫入；pre-commit/CI 只兜底已提交 Git 內容中的 PII，不驗證 runtime 產物。 |
| **真相住在事件裡** | 七條只追加（append-only）的註冊表事件流是規範真相；由所有者掌控的投影對外暴露實體、創作者、聲明、同意、發布、通路與敘事狀態，全程不再有破壞性佇列。 |
| **跨輪記憶** | HOT/WARM/COLD 記憶模型在技能與工作階段之間攜帶發現、分數與未決事項，並在寫入時淨化。 |
| **人話** | 技能內建 AI 腔偵測器與禁用詞表，讓輸出讀起來像人寫的。 |

---

## 安裝

可搭配 Claude Code、任意 Agent Skills 相容宿主，或直接 `git clone`：

| 宿主 | 安裝 |
|------|------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 然後 `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ 宿主](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Agent Plugins v1 客戶端 · Portable Lite** | 從 [v20.0.0 Release](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v20.0.0)下載 `aaron-marketing-skills-20.0.0-agent-plugin-v1-lite.tar.gz`，解壓後安裝其中的外掛目錄 |
| **[SkillHub.cn](https://skillhub.cn)（中文社群）** | `skillhub install <frontmatter-slug>`（如 `keyword-research`） |
| **任意宿主** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

在 Claude Code 中，`marketplace add` 只是註冊目錄——還需執行 `/plugin install aaron-marketing@aaron`（或在 `/plugin` 中選擇）才能真正啟用技能與命令。通用宿主單技能安裝：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。可在 [skills.sh 註冊表](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)瀏覽本技能庫。各宿主的技能目錄、frontmatter 相容細節、以及脫離外掛安裝時的降級行為見 [docs/agent-compatibility.md](agent-compatibility.md)（2026-07 實測 120/120 可安裝）。

安裝外掛**不會**往你的 `/mcp` 清單新增任何東西——MCP 目錄位於 [`docs/mcp-catalog.json`](mcp-catalog.json)，刻意放在 Claude Code 會自動註冊的外掛根 `.mcp.json` 路徑之外，僅作複製貼上參考（見[連接器與層級](#連接器與層級)）。

儲存庫根目錄是編寫單一事實來源，**不是** Agent Plugins v1 的標準安裝根。請使用上述 Release 資產；它把 **120/120 個嚴格 Agent Skills** 投影為扁平的 `skills/<name>/`，且不含 `mcp.json`、命令、hooks、連接器或儲存庫執行環境。現有客戶端相容層繼續保留；詳見 [Portable Lite 套件結構與能力邊界](agent-plugins-v1.md)。

---

## 初次使用

若宿主支援自動技能路由，直接描述目標即可：

```text
幫我研究面向小團隊的 SaaS 產品的關鍵字
```
```text
幫一個保養品牌找 TikTok 紅人並為適配度評分
```
```text
在我加預算前，稽核這個 Google Ads 帳戶——匯出檔案已附上
```

或用斜線命令 —— `/auto` 負責路由，學科入口直達：

```text
/aaron-marketing:auto 把我們的定價頁改造成可被 AI 引用的對比中心
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` 會推斷意圖並執行最小夠用的工作流，只在阻塞性決策處停下。每個技能都能用貼上的資料執行；選配工具見 [CONNECTORS.md](../CONNECTORS.md)。

---

## 架構

### 共享技能契約

每個技能都遵循**同一套啟動契約**——固定順序的七段：

1. **觸發 / 何時使用** —— 何時該啟用。
2. **Quick Start** —— 可複製貼上的提示。
3. **Skill Contract** —— 預期輸出 · 讀取 · 寫入 · 提升 · 完成條件 · 主下一技能。
4. **Handoff Summary** —— 標準交棒結構，讓下一個技能乾淨接力。
5. **Data Sources** —— `~~category` 佔位符，每個都有 keyless 的 Tier-1 路徑。
6. **Instructions** —— 編號方法（把所有匯出當作不可信輸入）。
7. **Next Best Skill** —— 下一步去哪（帶 visited-set + 最大深度終止規則）。

每個技能還自帶 `metadata.discipline`（narrative / seo-geo / influencer / ad / email / launch / social / protocol）與 `metadata.phase`，路由與聚類因此全庫統一。契約在 [skill-contract.md](../references/skill-contract.md) 中定義一次；跨技能共享狀態見 [state-model.md](../references/state-model.md)。

### 系統：四層行銷作業系統

一種品牌聲音，透過五個常駐通路表達，在發布時刻凝聚爆發，全部讀寫同一份共享記錄系統。七個學科、四個高度——是一套系統，不是一堆技能。

| 層 | 採用門檻 | 學科 | 節奏 |
|----|----------|------|------|
| **L1 · Strategy** —— 我們說什麼 / 我們是誰 | crawl | **品牌敘事** · TALE | 常駐 |
| **L2 · Channels** —— 表達策略的常駐引擎（owned → bought） | walk | **SEO/GEO** · CORE-EEAT + CITE · **社媒** · ECHO · **郵件** · SEND · **付費廣告** · ROAS · **紅人** · STAR | 常駐（紅人偏 episodic） |
| **L3 · Orchestration** —— 跨通路的限時時刻 | run | **產品發布** · RAMP | episodic |
| **L4 · Protocol** —— 共享的記錄系統 | — | 7 個真相註冊表 + 工作記憶 · 8 個 auditor 門 · 一套技能契約 | — |

敘事是訊息；通路是表達它的媒介。每個核心 builder 都會記錄它所使用的確切正典 ID/版本與聲明投影偏移量（offset），或一次經明確核准的回退/阻斷。每個學科的 4 階段循環都住在自己的層裡（敘事 = Trace → Architect → Land → Evaluate）。

七個學科都用階段**目錄**（`narrative/trace/`…、`seo-geo/survey/`…、`influencer/scout/`…、`ad/research/`…、`email/setup/`…、`launch/research/`…、`social/explore/`…）。注意 "activate" 在紅人裡指創作者外聯、在付費裡指帳戶門控——同詞不同域。

### 品質體系：八框架、八門

八套基準讓「好」可度量。每套定義維度、彙總方法，以及一小組**否決項**（無視其餘分數直接封頂或阻斷的硬性失敗）：

| 框架 | 評分對象 | 項數 / 維度 | 彙總 | 否決項 |
|------|----------|-------------|------|--------|
| **[TALE](../references/tale-benchmark.md)** | 品牌敘事的真相 / 體系 / 效果 | T / A / L / E | `truth`、`system`、`effectiveness` 三個 profile 結果各自獨立；無總合成分 | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | 內容品質，附 CORE/GEO 與 EEAT/SEO 診斷視圖 | 80 項 / 8 維 | 完整的 profile 加權結果；診斷視圖不是獨立總分 | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | 網域權威與引用信任 | 40 項 / 4 維 | 算術 profile 加權平均 | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | 紅人 Suitability / Trust / Appeal / Return | S / T / A / R；40 項 / 4 維 | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | 付費廣告的增量貢獻與營運品質 | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | 郵件的寄件者完整性 / 互動 / 培育 / 直接成效 | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | 產品發布的就緒 / 資產 / 動能 / 證明 | R / A / M / P；40 個穩定 ID | `preflight`、`execution`、`outcome` 三個 profile 結果各自獨立；絕不跨時間視界取平均 | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | 自然社媒的嵌入度 / 工藝 / 營運 / 可觀測性 | E / C / H / O；40 個穩定 ID | 每次只跑一個 `asset-gate` 或 `program-maturity-*` profile；絕不混合不同類單元 | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

每套框架由一個 **auditor-class 門**執行——其型別化產物（`class: auditor-output`）由確定性 validator 與有界生命週期 hooks 驗證。儲存庫 CI 只回歸測試 validator 與契約，不會檢查被忽略的主機執行期產物。門是工作流步驟，所以駐留並計入各自學科：

| 門 | 框架 | 所在 | 判定 |
|----|------|------|------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE 三 profile | `narrative/evaluate/` | truth/system/effectiveness 結果各自獨立；無合成總分 |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED；信任標籤僅作解釋 |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED，另附面向創作者的轉述 |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP 生命週期 profile | `launch/mobilize/` | 對一個已宣告的生命週期讀數給出 SHIP / FIX / BLOCK / UNDECIDED |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO 資產/專案 profile | `social/host/` | 對一個已宣告的單元/profile 給出 SHIP / FIX / BLOCK / UNDECIDED |

**共享否決策略：** 一條經核實的否決項把最終分封頂在 `min(raw, 59)`；兩條以上經核實的否決項產生 `status: DONE` + `verdict: BLOCK` 且不給最終分。證據缺失記為 `Unknown`，絕不自動判負。型別化規則見 [auditor-runbook.md](../references/auditor-runbook.md)。

### 協議層

`protocol/` 目錄承載學科階段流程之外的**共享真相與記憶機件** —— 8 個技能，單獨計數：

| 技能 | 職責 | 錨定 | 規範事件流 / 執行期角色 |
|------|------|------|----------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | 規範品牌/實體檔案（知識圖譜、Wikidata、AI 消歧） | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 規範創作者名冊/檔案——去重 handle、帶溯源標籤的受眾資料、費率、合規歷史 | 紅人 | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | offer 與聲明實證台帳——O1/T2 聲明檢查所對照評判的那份記錄 | 付費 | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 規範的逐主體同意/抑制記錄——S2/N1 否決項對照評判的那份記錄 | 郵件 | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 規範的逐次發布檔案/發布行事曆——分級、單向生命週期階段、權威日期/禁運期、通路提交台帳；R1 階段真相否決所對照評判的 launch 真相 SSOT | 產品發布 | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 規範的逐通路記錄——handle、所有權/授權、平台規範、揭露預設值；ECHO E1 通路真相否決所對照評判的通路真相 SSOT | 社媒 | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 規範的品牌敘事正典——核准的策略敘事、訊息體系、語言/詞彙、證明點；TALE T1 真相否決所對照評判的品牌正典 SSOT | 敘事 | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD 記憶生命週期（擷取 · 提升 · 降級 · 封存 · 查詢） | 全部學科 | 非規範的 `memory/` 執行期狀態 |

註冊表遵循**唯一寫入者規則**（其他技能經 `registry-events.py` proposal events 投遞），且註冊表只*存證*——評判歸門。最底層真正橫向的是 `references/` 協議（[auditor-runbook](../references/auditor-runbook.md)、[state-model](../references/state-model.md)、[skill-contract](../references/skill-contract.md)、[humanizer-slop](../references/humanizer-slop.md)、[measurement-protocol](../references/measurement-protocol.md)）——按設計以文件而非技能的形式共享。

### 記憶與自動化

**記憶**按溫度分層，讓上下文跨技能與工作階段留存而不撐爆提示：

| 層 | 位置 | 行為 |
|----|------|------|
| **HOT** | `memory/hot-cache.md` | 每次工作階段自動載入；封頂 **80 行 且 25 KB**（先觸發者為準）。 |
| **WARM** | `memory/<subdir>/` | 可重建的工作投影與經許可的稽核產物；規範的註冊表真相住在 `memory/events/*.ndjson`。 |
| **COLD** | `memory/archive/` | 降級/較舊記錄，留作召回。 |

**Hooks**（`hooks/hooks.json`，runner `hooks/claude-hook.sh`）接入七個 Claude Code 事件：

| 事件 | 比對 | 作用 |
|------|------|------|
| `SessionStart` | `startup\|resume\|clear\|compact` | 注入**淨化後**的 hot-cache + 未決事項指標（提示注入行被塗掉；符號連結快取被拒）。 |
| `UserPromptSubmit` | （全部） | 輕量逐提示上下文 hook。 |
| `PreToolUse` | 已知可寫工具 | 精確路徑的直接 `memory/**` 寫入必須被 Git 忽略；可識別的 opaque shell/MCP 記憶變更不受支援並會被拒絕。Registry runtime 會再次檢查最終/暫存/鎖定路徑。 |
| `PostToolUse` | 已知可寫工具 | 成功寫入後複核整個 operational-memory 命名空間，並驗證準確審計目標或執行有界保留區掃描。 |
| `PostToolUseFailure` | 已知可寫工具 | 工具失敗後執行相同的寫後隱私與 Artifact Gate 檢查，因為失敗命令仍可能已寫入檔案。 |
| `PostToolBatch` | （全部） | 每批平行工具結束後複核 operational memory 與完整審計保留區。 |
| `Stop` | （全部） | 執行最後一次有界掃描並可阻止一次以便修復；`stop_hook_active` 會放行後續停止。pre-commit/CI 僅保護已提交 Git 內容中的 PII，不驗證被忽略的 runtime 產物。 |

Artifact Gate 是**框架無關**的——同一個 hook 驗證 TALE、CORE-EEAT、CITE、STAR、ROAS、SEND、RAMP、ECHO 產物，無任何針對單框架的程式碼。

---

## 技能目錄

技能連結開啟各自的 `SKILL.md`。展開每個學科下的 **詳情** 可看每個技能的一句話用途。目錄順序遵循[四層系統](#系統四層行銷作業系統)——先品牌敘事（L1 · Strategy），接著五個常駐通路，再 Launch（L3 · Orchestration），最後協議層。

### 品牌敘事 — TALE（16）

`narrative/` 下四個階段按 Trace → Architect → Land → Evaluate 排布。`narrative-quality-auditor` 分別執行 truth、system、effectiveness 三個 profile；完整評審只把三個結果關聯起來，絕不取平均。敘事是各通路 builder 所繼承的 L1 策略。

| 階段 | 技能 |
|------|------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>逐技能用途（品牌敘事）</b></summary>

| 技能 | TALE 槓桿 | 用途 |
|------|-----------|------|
| narrative-baseline-mapper | T | 擷取當前散落於自有陣地的真實品牌故事——任何重設計之前那個誠實的起點。 |
| category-narrative-mapper | T | 梳理品類的主導敘事與具名替代品，讓品牌能主張一個可防守、有差異的位置。 |
| audience-belief-mapper | T | 揭示目標受眾已經相信、懷疑與在意什麼——敘事必須撼動的那些信念。 |
| positioning-truth-tracer | T | 把每一條定位主張追溯回實證，淘汰任何無支撐者（T1 真相否決的上游）。 |
| strategic-narrative-designer | A | 設計核心策略敘事——品牌所領銜的「改變世界」故事弧、賭注與收束。 |
| message-system-architect | A | 架構訊息體系——slogan、支柱、證明點與逐受眾角度，構成一套連貫結構。 |
| brand-language-codifier | A | 編纂聲音、語氣、詞彙、do/don't 用語，讓每個通路聽起來都是同一個品牌。 |
| story-bank-builder | A | 建立可複用的證明故事、客戶敘事與類比庫，供各通路取用。 |
| narrative-cascade-planner | L | 規劃敘事如何無稀釋、無漂移地級聯進每個通路與時刻。 |
| pitch-narrative-builder | L | 把敘事塑成 pitch 形態——deck 骨架、demo 故事、投資人/媒體框架。 |
| narrative-enablement-kit | L | 讓每個團隊都能一致講故事的賦能包——talk track、FAQ、訊息地圖。 |
| proof-point-packager | L | 把證明點打包成通路就緒、感知聲明台帳的資產。 |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | 型別化 TALE 門：分別回傳各 profile 結果，絕不取平均。寫入 `memory/audits/narrative/`。 |
| message-test-designer | E | 設計訊息測試——變體矩陣、受眾分組、對策略敘事的共鳴判讀。 |
| narrative-resonance-monitor | E | 用 keyless 來源追蹤敘事在各通路的落地情況（proxy 資料已標註）。 |
| narrative-drift-monitor | E | 監視敘事漂移——各通路偏離核准正典之處——並標記校正。 |

**跨學科複用**（計入原階段，不重複造輪子）：[positioning-mapper](../launch/research/positioning-mapper/SKILL.md)（邏輯上是 Trace 的最前端，實體在 `launch/`）、[message-house-builder](../launch/assemble/message-house-builder/SKILL.md)、`audience-mapper`、`share-of-voice-tracker`（共鳴分母）。**無新連接器**——敘事共鳴複用 `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py`——見 [tale-benchmark.md](../references/tale-benchmark.md)。

</details>

### SEO/GEO — SITE（16）

四個階段目錄（各 4 技能）沿 SITE 循環（Survey → Implement → Tune → Evaluate）排布，外加本學科的兩個品質門（標 ⛩）；品質基準仍是 CORE-EEAT + CITE，循環品牌與基準名彼此獨立。

| 階段 | 技能 |
|------|------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>逐技能用途（SEO/GEO）</b></summary>

| 技能 | 用途 |
|------|------|
| keyword-research | 為頁面/主題/活動開啟關鍵字工作——意圖、需求、臨門一腳機會。 |
| competitor-analysis | 分析競品 SEO 策略，對比網域，挖出其關鍵字與缺口。 |
| serp-analysis | 讀懂 SERP——特性、摘要、People Also Ask、某查詢的排名規律。 |
| content-gap-analysis | 找出相對競品缺失的主題與覆蓋空洞。 |
| content-writer | 撰寫並刷新 SEO 最佳化的文章、著陸頁、產品文案。 |
| geo-content-optimizer | 為 AI 引擎（ChatGPT、Perplexity、AI Overviews、Gemini、Claude、Copilot）最佳化內容。 |
| serp-markup-builder | 標題/meta/OG/Twitter 標籤 + JSON-LD / Schema.org 結構化資料。 |
| page-play-builder | 範本驅動頁面打法——批量頁、第三方平台發布、對比頁、本地/GBP。 |
| ⛩ content-quality-auditor | 80 項 CORE-EEAT 發布就緒門（SHIP/FIX/BLOCK）。 |
| technical-seo-checker | 網站速度、Core Web Vitals、索引、可抓取性、robots。 |
| on-page-seo-checker | 稽核頁面級 on-page 健康度——標題層級、關鍵字佈局、圖片、品質訊號。 |
| site-structure-optimizer | 內部連結、錨文字、孤立頁、頁面層級、URL 分類、hub/spoke 主題叢集。 |
| ⛩ domain-authority-auditor | 40 項 CITE 網域信任門（TRUSTED/CAUTIOUS/UNTRUSTED）。 |
| rank-tracker | 追蹤關鍵字排名、位次變化與跌幅。 |
| performance-monitor | 多指標 SEO/GEO 報告、看板與閾值告警。 |
| offsite-signal-analyzer | 外連檔案 + 連結品質，加上在你自己的 GA4/GSC/日誌中度量 AI 助手引薦流量。 |

</details>

### 社媒 — ECHO（16）

`social/` 下四個階段按 Explore → Craft → Host → Observe 排布。`social-quality-auditor` 選用 `asset-gate` 或一個 program-maturity profile；兩類構念絕不混用。本學科不含任何發文、互動或私訊自動化。

| 階段 | 技能 |
|------|------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>逐技能用途（社媒）</b></summary>

| 技能 | ECHO 槓桿 | 用途 |
|------|-----------|------|
| channel-portfolio-planner | E | 從受眾真正所在之處挑選平台組合與逐通路角色/節奏（把通路記錄進註冊表）。 |
| voice-dossier-builder | E | 品牌聲音、語氣、人設、do/don't 詞彙，以維持一致的、像人的存在感。 |
| platform-norm-profiler | E | 發文前的逐平台規範、格式、排名訊號與紅線規則。 |
| participation-warmup-planner | E | 非推廣的社群暖場計畫——在推銷之前，在哪裡現身並創造價值。 |
| social-calendar-builder | C | 內容行事曆——主題、系列、與真實產能平衡的節奏（不過度發文）。 |
| social-creative-builder | C | 平台原生貼文（hook/內文/CTA），訊息一致且感知聲明台帳。 |
| short-video-scripter | C | 短影音腳本——hook、節拍、螢幕文字、留存結構。 |
| advocacy-program-designer | C | 員工/社群倡導計畫——opt-in、揭露預設值、可分享資產包。 |
| ⛩ social-quality-auditor | asset gate / program maturity | 型別化 ECHO 門，一次只審一個單元/profile；絕不混合資產與營運兩類構念。寫入 `memory/audits/social/`。 |
| engagement-inbox-manager | H | 回覆/留言/私訊分診 playbook——回應分層、升級、真誠互動紀律（不製造/誘餌式互動）。 |
| social-selling-planner | H | 創辦人/團隊社群銷售動作——關係優先外聯，不做自動化私訊。 |
| crisis-response-planner | H | 預先草擬的危機分層、緩衝聲明、升級階梯、暫停排程觸發條件。 |
| social-pulse-monitor | O | 從 keyless 來源獲取提及/情感/主題脈動、spike-vs-sustain 判讀（proxy 資料已標註）。 |
| share-of-voice-tracker | O | 在週期穩定的分母上，對比具名競品的聲量占比。 |
| dark-social-attributor | O | 歸因 dark-social/無連結流量——UTM 紀律、自報歸因擷取、引薦解析。 |
| social-measurement-loop | O | 把一次上線的改動相對基線在視窗內回讀 → Promote / Keep-testing / Rollback。 |

**跨學科複用**（計入原階段，不重複造輪子）：`trend-spotter`、`audience-mapper`、`content-amplifier`、`outreach-manager`、`competitor-tracker`、`landing-optimizer`、`performance-analyzer`、`roi-calculator`、`report-generator`、`offer-claims-registry`、`community-launch-runner`、`creator-registry`、`page-play-builder`、`memory-management`——見 [echo-benchmark.md](../references/echo-benchmark.md)。

</details>

### 郵件行銷 — SEND（16）

`email/` 下四個階段目錄（各 4 技能）按 SEND 循環排布；門（⛩ email-quality-auditor）位於 Deliver。只有門計算目標加權 EQS——其餘技能各管一個槓桿並交棒。用例無關（B2C 生命週期 / B2B 冷觸達 / newsletter-creator），由目標權重欄決定側重。

| 階段 | 技能 |
|------|------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>逐技能用途（郵件行銷）</b></summary>

| 技能 | SEND 槓桿 | 用途 |
|------|-----------|------|
| deliverability-qa | S | 發送前 SPF/DKIM/DMARC/BIMI 認證、聲譽、收件匣落位、垃圾內容、清單衛生（S1 檢查）。 |
| list-segment-builder | E | 從自有清單/CRM/GA4 匯出建構行為 + 生命週期階段分群與抑制規則。 |
| list-growth-designer | S（+N） | 清單成長策略——獲取通路、lead magnet 構思、合規的雙重確認擷取流程 spec、推薦環機制；在獲取點餵入 S 同意品質。 |
| list-hygiene-monitor | S | ** 持續的清單健康度——退信/投訴清理、sunset 政策、再確認、非活躍分群抑制。 |
| email-creative-builder | E（+D） | 主旨/預覽文字/內文/CTA，與著陸頁訊息一致，感知聲明台帳。 |
| subject-line-lab | S | ** 主旨/預覽文字構思與評分——長度、垃圾觸發詞、好奇/清晰平衡、測試用變體集。 |
| email-render-builder | E | ** HTML 郵件建置/QA——用戶端相容、暗色模式、可存取性、純文字替代、渲染測試清單。 |
| dynamic-content-personalizer | E | ** 合併標籤/liquid 個人化塊、條件內容規則、回退值安全。 |
| email-sequence-designer | N | 生命週期/自動化流程（歡迎、棄購、購後、召回）+ 頻次治理。 |
| newsletter-monetization-planner | D | 付費訂閱、贊助位庫存 + 刊例、推薦成長循環經濟。 |
| preference-frequency-manager | N | ** 偏好中心設計與發送頻次治理，以削減疲勞與退訂。 |
| reactivation-specialist | N | ** 沉睡訂閱者的 win-back / 再互動流程，含 sunset-or-recover 決策規則。 |
| ⛩ email-quality-auditor | S+E+N+D（EQS） | auditor-class SEND 門：算 EQS、跑 S1/S2/N1/D1、產出 SHIP/FIX/BLOCK；含**發送前 go/no-go**模式。 |
| send-experiment-designer | E | A/B / 發送時間 / hold-out 設計，含樣本量 + 顯著性判讀（promote/kill）。 |
| inbox-placement-monitor | S | ** 透過 seed 清單與供應商訊號持續追蹤收件匣 vs 垃圾落位，並帶聲譽漂移告警。 |
| cold-outbound-sequencer | D | ** 合規 B2B 冷觸達節奏——送達安全的爬坡、個人化 token、回覆處理步驟。 |

**跨學科複用**（計入原階段，不重複造輪子）：[audience-mapper](../influencer/scout/audience-mapper/SKILL.md)、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)。

</details>

### 付費廣告 — ROAS（16）

`ad/` 下四個階段目錄（各 4 技能）按 ROAS 循環排布；門（⛩ ad-account-auditor）位於 Activate。只有門計算目標加權 RQS——其餘技能各管一個槓桿並交棒。

| 階段 | 技能 |
|------|------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>逐技能用途（付費廣告）</b></summary>

| 技能 | ROAS 槓桿 | 用途 |
|------|-----------|------|
| campaign-architect | A + 結構 | 帳戶/活動結構、campaign 類型選型、比對類型、否定詞/排除、付費↔自然蠶食；含常態化**搜尋詞挖掘**模式。 |
| audience-segment-builder | A | 把自有客戶/CRM/GA4 匯出轉為種子受眾、相似種子、排除人群、漏斗分層鎖定地圖。 |
| search-term-miner | A | ** 從搜尋詞報告挖掘否定詞、新增關鍵字候選與比對類型收斂。 |
| product-feed-optimizer | O | ** Shopping/PMax feed 品質——標題、屬性、GTIN、品類對應與拒登修復。 |
| ad-creative-builder | O | RSA 標題/描述、hook、角度矩陣，並與目標頁訊息一致。 |
| ad-test-designer | O（+S） | 設計 A/B/n 與增量實驗（假設、變體矩陣、樣本量/檢定力），判讀顯著性 → promote/kill。 |
| bid-strategy-planner | S | ** 選型並配置出價策略（tCPA/tROAS/max-conversions）、設定目標種子、規劃學習期過渡。 |
| landing-experience-checker | O | ** 點擊後頁面 QA——廣告相關性、載入速度、行動裝置、政策——即廣告↔頁面訊息一致檢查。 |
| ⛩ ad-account-auditor | R+O+A+S（RQS） | auditor-class ROAS 門：算 RQS、跑 R1/R2/O1/O2/A1、產出 SHIP/FIX/BLOCK；含**上線 go/no-go**模式。 |
| conversion-signal-qa | R | 上線前追蹤 QA（事件觸發、UTM 規範、去重門控、視窗對齊、iOS-ATT 標記）——R1/R2 的前置（建訊號，門打分）。 |
| placement-exclusion-manager | A | ** 版位/受眾排除名單——品牌安全封鎖、垃圾版位剪除、浪費花費抑制。 |
| conversion-value-mapper | R | ** 把轉換動作對應到價值/權重與價值規則，讓 tROAS 依真實毛利而非原始次數出價。 |
| paid-measurement-loop | R（+S） | 把一次上線的改動相對對照在視窗內回讀 → Promote / Keep-testing / Rollback / Unproven。 |
| attribution-reconciler | R | 針對 GA4/ecommerce 訂單 ID 真值集做常態去重、視窗/幣別歸一、模型對比、增量。 |
| budget-pacing-monitor | S | ** 在投放期追蹤消耗節奏對比預算，標記欠投/超投，並建議配速校正。 |
| fatigue-frequency-manager | O | ** 監視頻次與創意衰減訊號，標記疲勞廣告，並排程刷新/輪換。 |

**跨學科複用**（計入原階段，不重複造輪子）：[budget-optimizer](../influencer/target/budget-optimizer/SKILL.md)（花費 + 出價節奏/學習期模式）、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)（點擊後）、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)（回報計算）、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)。

</details>

### 紅人 — STAR（16）

四個階段目錄（各 4 技能）沿 STAR 循環（Scout → Target → Activate → Report）排布；循環與品質基準現同為 STAR（Suitability · Trust · Appeal · Return）；本學科的門（⛩ creator-content-auditor）位於 Activate。

| 階段 | 技能 |
|------|------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>逐技能用途（紅人）</b></summary>

| 技能 | 用途 |
|------|------|
| audience-mapper | 在與創作者合作前做受眾畫像，並摸清其亞文化 / 微社群。 |
| trend-spotter | 活動節奏與主題——趨勢話題、聲音、內容格式、文化時刻。 |
| influencer-discovery | 從零搭建紅人名單、拓展新平台、規模化找 nano/micro。 |
| fit-scorer | 對候選名單做客觀加權適配打分（基於 STAR Suitability (S)）。 |
| competitor-tracker | 競品的合作紅人、活動、格式、估算觸及/花費與缺口。 |
| campaign-planner | 規劃活動、產品發布、tentpole 或常態化創作者專案。 |
| brief-generator | 標準化紅人 brief 與可複用團隊範本。 |
| budget-optimizer | 跨層級/平台分配預算、預測 ROI、建模情境（同時服務付費廣告的花費 + 出價節奏）。 |
| outreach-manager | pitch、跟進節奏、再啟用、費率談判、狀態追蹤。 |
| ⛩ creator-content-auditor | 對紅人提交內容做發布前門決策（STAR Trust：FTC 揭露 STAR-T1、聲明真實性 STAR-T2）。 |
| contract-helper | 起草/審閱創作者協議——使用權、獨家、標準條款。 |
| content-amplifier | 用付費投放放大自然創作者內容，並把 UGC 二次利用到付費、網站、郵件、自然社媒。 |
| landing-optimizer | 面向創作者/付費流量的著陸頁——訊息一致、行動裝置、A/B（同時服務付費點擊後）。 |
| performance-analyzer | 評估創作者結果、橫比創作者、情感、轉換（同時是付費跨通路記分卡）。 |
| roi-calculator | 度量/預測 ROI、為預算辯護、評估創作者/層級價值（共享回報計算引擎，含付費）。 |
| report-generator | 週期結束後面向利害關係人的書面報告（同時出付費廣告報告）。 |

</details>

### 產品發布 — RAMP（16）

`launch/` 下四個階段按 Research → Assemble → Mobilize → Prove 排布。`launch-readiness-auditor` 每次執行只選一個 `preflight`、`execution` 或 `outcome` profile；生命週期結果只做關聯，絕不取平均。

| 階段 | 技能 |
|------|------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>逐技能用途（產品發布）</b></summary>

| 技能 | RAMP 槓桿 | 用途 |
|------|-----------|------|
| positioning-mapper | R | Dunford 式定位畫布——具名競爭替代品、獨特屬性、價值主題、灘頭細分、onlyness 陳述。 |
| launch-tier-planner | R | 分級決策（Tier 1 旗艦 / Tier 2 定向 / Tier 3 changelog 級）、發布類型宣告、KPI 目標、帶 kill criteria 的風險登記冊。 |
| launch-window-planner | R | 候選視窗對比（衝突 / 順風 / 風險）、launch-week vs 滾動發布裁決、商店審核緩衝、禁運期視窗定義。 |
| early-access-designer | R | waitlist→concept→alpha→beta→GA 階段階梯，含畢業標準、cohort 門控、回饋閉環、推薦機制（R1 階段真相否決的上游）。 |
| message-house-builder | A | 訊息屋（tagline、one-liner、價值支柱、證明點）+ working-backwards PR-FAQ 骨架 + 逐通路角度包（A1 的上游）。 |
| launch-asset-packager | A | 分級化發布資產清單——press kit 規格、demo/截圖規格、發布 FAQ、商店 listing 中繼資料、技術上線檢查表。 |
| pricing-packaging-planner | A | 發布定價與打包——層級結構、價值到定價地圖、launch-offer 階梯、帶畢業路徑的 beta 定價、保證條款。 |
| sales-enablement-kit | A | 內部賦能——battle card、銷售 talk track、異議處理表、內部 FAQ + CS macros、遵守禁運紀律的內部公告。 |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | 型別化 RAMP 門，一次只審一個生命週期讀數；絕不跨時間視界取平均。寫入 `memory/audits/launch/`。 |
| launch-day-conductor | M | 逐小時分塊的發布日 runbook——前置條件門檢查、不可逆推送後的觀察窗裁決、P0–P3 事件階梯 + 回滾 playbook。 |
| community-launch-runner | M | 逐平台提交包（Product Hunt、Show HN、subreddit、目錄波次、區域/中文通路），置於平台紅線檢查之下。 |
| press-media-relations | M | 三層媒體/分析師名單、禁運 pitch 擇時、標準結構新聞稿草稿、分析師簡報大綱。 |
| launch-monitor | P | T-0→T+30 視窗監控——儀表化驗證（P1 的上游）、排名/評論/新聞輪詢、D0/W1/M1 KPI 快照、spike-vs-sustain 判讀。 |
| launch-feedback-synthesizer | P | 回饋主題摘要、open→shipped 狀態環（「you asked, we shipped」）、合規社證收割。 |
| launch-retro-analyzer | P | D1/W1/M1 複盤——逐通路實際 vs 目標、對最大偏差做 5-Whys、keep/kill/change 決策、成果快照寫回註冊表。 |
| momentum-planner | P | T+1→T+30 勢能計畫——發布時刻行事曆、公告分級路由、relaunch 正當性裁決、下一個 Tier-1 時刻。 |

**跨學科複用**（計入原階段，不重複造輪子）：`audience-mapper`、`trend-spotter`、`budget-optimizer`、`landing-optimizer`、`campaign-planner`、`outreach-manager`、`content-amplifier`、`email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`、`campaign-architect` / `ad-creative-builder`、`page-play-builder` / `content-writer`、`technical-seo-checker` / `serp-markup-builder`、`performance-monitor`、`keyword-research`、`entity-registry`、`offer-claims-registry`、`consent-registry`、`list-growth-designer`、`roi-calculator` / `performance-analyzer` / `report-generator`——見 [ramp-benchmark.md](../references/ramp-benchmark.md)。

</details>

### 協議層（8）

共享真相與記憶機件——角色與唯一寫入者規則見上文[架構 § 協議層](#協議層)。

| 組 | 技能 |
|----|------|
| **協議層** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>逐技能用途（協議層）</b></summary>

| 技能 | 用途 |
|------|------|
| entity-registry | 面向知識圖譜、Wikidata、AI 消歧的規範實體檔案。 |
| creator-registry | 規範創作者名冊/檔案——去重 handle、帶溯源標籤的受眾資料、費率、合規歷史。 |
| offer-claims-registry | 規範 offer 與聲明實證台帳——O1/T2 聲明檢查所對照評判的那份記錄。 |
| consent-registry | 規範的逐主體同意/抑制記錄——opt-in 時間戳 + 合法依據、雙重確認證明、僅追加的退訂/退信/投訴歷史；S2/N1 否決項對照評判的那份記錄。 |
| launch-registry | 規範的逐次發布檔案 + 發布行事曆——分級、發布類型、單向生命週期階段（draft→…→GA）、權威日期 + 禁運期承諾、通路提交台帳、成果快照；launch 真相 SSOT。 |
| channel-registry | 規範的逐通路記錄——handle、所有權/授權、平台規範、揭露預設值；ECHO E1 通路真相否決所對照評判的通路真相 SSOT。 |
| narrative-registry | 規範的品牌敘事正典——核准的策略敘事、訊息體系、語言/詞彙、證明點；TALE T1 真相否決所對照評判的品牌正典 SSOT。 |
| memory-management | 審閱、提升、降級、封存 HOT/WARM/COLD 專案記憶。 |

</details>

---

## 命令

8 個命令：`/aaron-marketing:auto` 跨全部七學科路由任意目標；每個學科恰有一個顯式入口。原始檔：[commands/](../commands)。

| 命令 | 用途 | 收窄 |
|------|------|------|
| `/aaron-marketing:auto` | 描述任意目標——推斷意圖並執行最小夠用的工作流 | `--deep`（窮盡/壓測） |
| `/aaron-marketing:narrative` | 品牌敘事（TALE 循環）：追溯當前故事與品類、架構策略敘事與訊息體系、落地到各通路、品質門、共鳴與漂移 | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO 端到端（SITE 循環）：勘測需求/競品、實施內容、調優品質/技術/頁面、評估權威/排名/報告/記憶 | `--phase survey\|implement\|tune\|evaluate` + 各階段子參數（`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`） |
| `/aaron-marketing:influencer` | 紅人（STAR 循環）：受眾洞察、偵察與適配、鎖定規劃、外聯、放大、ROI 匯報 | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | 付費廣告（ROAS 循環）：分群、結構、創意、實驗設計、稽核門、衡量 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | 郵件行銷（SEND 循環）：送達/同意、分群、創意、生命週期流程、變現、發送測試、稽核門 | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | 產品發布（RAMP 循環）：定位、分級與擇時、訊息屋與資產、就緒門、發布日執行、監控與複盤 | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | 自然社媒（ECHO 循環）：通路組合與聲音、行事曆與創意、品質門、互動/危機主持、脈動與衡量 | `--phase explore\|craft\|host\|observe` |

日常工作通常從 `/aaron-marketing:auto` 開始；其餘七個是顯式的學科入口，用 `--phase` 收窄階段。

---

## 連接器與層級

技能用 `~~category` 佔位符（`~~SEO tool`、`~~web analytics`、`~~ad platform`、`~~email platform` 等）而非具體廠商命名，且每個類別都有 **keyless 的 Tier-1 路徑**。完整配方（含每個類別的免費/第一方端點）見 [CONNECTORS.md](../CONNECTORS.md)。

### 連接器層本身就是一件產品

**100+ 條記錄在案的整合路徑**，分三個精心設計的層——每一條都名副其實：

| 層 | 你得到什麼 |
|----|------------|
| **28 個內建零依賴連接器** | 純 Python 標準庫——無 `pip`、無建置。keyless 即時 SERP + JS 渲染抓取（Firecrawl、Tavily）、AI 答案引用探針、DNS-over-HTTPS 郵件認證拉取、維基百科關注度序列、GDELT 新聞提及、真實 YouTube 創作者指標、IndexNow + 百度收錄推送、Resend ESP 自動化，以及能把上述任一變成前後對比時間序列的 git 可差分測量台帳。 |
| **60+ 個記錄在案的官方/免費 API** | 每一行都連結廠商**官方文件**、帶核驗日期，且每條連結入庫前都經過 HTTP 實測。包含多數工具清單遺漏的路徑：GSC URL Inspection、CrUX History（40 週真實使用者 CWV）、Gmail Postmaster Tools API、Meta 廣告庫、微軟 Clarity 資料匯出 API。 |
| **廠商 MCP 伺服器** | 18 個遠端端點入目錄（絕不自動註冊——你的 `/mcp` 清單保持乾淨），外加 Google Analytics、Search Console、**Google Ads**、**微軟 Clarity** 的官方自架伺服器。其中兩個遠端 MCP 完全免鑑權（Firecrawl、Tavily）。 |

讓它們可信而不只是數量多的四個理由：

- **三類安全等級、工程化門控**（[SECURITY.md](../SECURITY.md)）：託管抓取器在每次委託抓取前**本地預檢 robots.txt**、遇 Disallow 拒絕執行；一切改變外部狀態的操作（發郵件、推送收錄）**預設 dry-run**，必須顯式 `--live` 才執行，廠商支援冪等鍵就用、不支援就絕不自動重試。
- **核驗，然後再核驗**：端點對照廠商一手文件帶日期核實、keyless 路徑經過真實呼叫測試、CI 守衛強制版本/追蹤同步、發版前的 live 冒煙專抓端點漂移（它已經兩次抓到真實的 API 變更）。
- **只報事實、不下判定**：連接器輸出記錄存在性、解析標籤和原始序列；裁決交給 auditor 門，技能給每個數字標註 **Measured / User-provided / Estimated**。
- **成文的 playbook**（[docs/connector-playbook.md](connector-playbook.md)）管轄每一次新增——定性、驗證、實作、測試、接線、文件、追蹤、回歸、歸檔——目錄再成長，品質不滑坡。

| 層級 | 需要 | 你獲得 |
|------|------|--------|
| **Tier 1**（預設） | 無 | 貼上資料，或從免費/公開來源拉取。分析框架照常執行。 |
| **Tier 2** | 一個免費第一方 API 或 MCP | 自動取你自己的 GSC / GA4 / Core Web Vitals 資料。 |
| **Tier 3** | 更完整的 MCP 集 | 全自動多源工作流。 |

- **內建零依賴助手** 位於 `scripts/connectors/`（僅 Python 標準庫），在本地拉取公開/自有資料——如 PageSpeed/CrUX、Open PageRank、頁面抓取、Wayback CDX、Wikidata SPARQL、Common Crawl、advertools 配方——外加 **`resend.py`**：郵件技能直連 Resend ESP 的自動化（免費檔 key：寄件網域認證狀態、種子測試投遞、抑制名單同步、廣播定時發送；變更類子命令預設 dry-run，需 `--live` 才執行）；以及 **`firecrawl.py`** + **`tavily.py`**：研究類技能直連託管抓取器的 keyless 自動化（Firecrawl：即時搜尋結果 + JS 渲染頁 markdown + 站點 URL 清單；Tavily：帶評分的搜尋 + AI 答案引擎引用來源探針（GEO 用）+ URL 擷取——兩者完全無需 key，均內建本地 robots.txt 預檢）。
- **免費/keyless 來源** 按類別記錄：Google Search Console 與 GA4（自有資料）、PageSpeed/CrUX、Wikidata、Common Crawl、Open PageRank、Firecrawl keyless SERP/抓取、Tavily keyless AI 搜尋、DNS-over-HTTPS 郵件認證記錄（`doh.py`）、維基百科關注度序列（`pageviews.py`）、GDELT 新聞提及（`gdelt.py`）、免費 key 的 YouTube 創作者指標（`youtube.py`）、IndexNow + 百度收錄推送（`indexpush.py`，dry-run 門控）、廣告透明庫（Meta/Google/TikTok），以及 crt.sh、W3C 驗證器、oEmbed、HN Algolia 的配方行。
- **選配 MCP 伺服器**（Ahrefs、Semrush、SE Ranking、SISTRIX、SimilarWeb、自架免費的 **OpenSEO** 套件、Cloudflare、Vercel、HubSpot、Amplitude、Notion、Webflow、Sanity、Contentful、Slack、Resend、keyless 的 Firecrawl 與 Tavily）在 [`docs/mcp-catalog.json`](mcp-catalog.json) 中作為**僅複製貼上參考**——目錄位於會被自動註冊的外掛根 `.mcp.json` 路徑之外，不會為你註冊任何東西。把你想要的條目複製進自己的 MCP 設定即可。

付費廣告技能基於你的**自有帳戶手動匯出**（原生廣告管理後台 CSV、GA4、電商）評分。帶金鑰的廣告 API（Google Ads SDK、Meta Marketing API）僅是 opt-in Tier-2/3，**絕不**作為 Tier-1 要求。郵件技能同理——基於你**自己的 ESP 匯出**評分，所有送達率訊號均 keyless（DNS 查詢、DMARC RUA 報告、種子收件測試），帶金鑰的 ESP API 也絕不是 Tier-1 要求；若你的 ESP 是 Resend，內建的 `resend.py` 可在免費檔上自動化同一閉環。

---

## 推薦工作流

真實目標大多橫跨多個學科。`/aaron-marketing:auto` 會把一句自然語言目標路由到七個學科中最小可用的技能鏈——例如一次產品發布會同時調動 Launch、Email、Social 與 Paid：

```text
/aaron-marketing:auto 三週後在 Product Hunt 發布 v2——等候名單 1,200 人；需要發布頁、郵件序列與發布日計畫
```

也可以端到端驅動單一學科的循環（各學科目錄下的 `README.zh.md` 學科指南提供場景級打法）：

**品牌敘事（TALE 循環）**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor`（⛩ TALE 門）→ `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO（SITE 循環）**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor`（⛩ 發布門）→ `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`；信任評審用 `domain-authority-auditor`（⛩）

**社媒（ECHO 循環）**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor`（⛩ ECHO 門）→ `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**郵件行銷（SEND 循環）**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` （⛩ EQS 門），在任何發送前

**付費廣告（ROAS 循環）**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` （落地頁配 `landing-optimizer`）
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` （⛩ RQS 門），在任何預算上線前
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**紅人（STAR 循環）**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer`（STAR Suitability）
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor`（⛩ STAR 門）→ `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**產品發布（RAMP 循環）**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor`（⛩ RAMP 門）→ `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

要做完整信任評審，把 `content-quality-auditor` 與 `domain-authority-auditor` 搭配，得到合計 120 項的評估。開啟 `memory-management` 後，交棒與未決事項自動留存在 HOT/WARM/COLD 記憶中。

---

## 倉庫結構

```
narrative/{trace,architect,land,evaluate}/                  # 品牌敘事 — TALE(16，含其門)
seo-geo/{survey,implement,tune,evaluate}/                  # SEO/GEO(16，含其 2 個門)
influencer/{scout,target,activate,report}/                   # 紅人(16，含其門)
ad/research|orchestrate|activate|scale/            # 付費廣告 — ROAS(16，含其門)
email/setup|engage|nurture|deliver/                  # 郵件行銷 — SEND(16，含其門)
launch/research|assemble|mobilize|prove/             # 產品發布 — RAMP(16，含其門)
social/explore|craft|host|observe/                   # 社媒 — ECHO(16，含其門)
protocol/                                            # 協議層(8) — 真相註冊表 + 記憶
commands/        # 8 個斜線命令(auto、narrative、seo-geo、influencer、ad、email、launch、social)
references/      # 共享契約、狀態模型、八套基準、auditor runbook、平台資料包
evals/           # 各技能結構化 eval 用例 + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh(唯一執行邏輯)
scripts/         # validate-skill.sh + connectors/(標準庫) + CI 守衛
memory/          # HOT/WARM/COLD 鷹架 + 註冊表儲存(entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # 在地化 README（zh）
.claude-plugin/  # plugin.json + marketplace.json 鏡像
```

---

## 設計哲學

- **內容優先。** 技能是 Markdown；零相依的 Bash/Python 標準庫執行時提供連接器、評分、註冊表事件、驗證與檢查。第三方 / `pip` 相依被 CI 明令禁止。
- **keyless 優先。** 每個 `~~category` 都有免費/自有資料配方；MCP 與付費工具純屬便利。
- **外科手術式 & MECE。** 每個技能只擔一項職責，邊界清晰；重疊的工作做成現有技能的*模式*，而非新堆一個薄技能。註冊表存證、門評判、分析器餵門。
- **不編數字。** 技能為每個資料標註 Measured / User-provided / Estimated，並內建 AI 腔 / 禁用詞偵測。
- **合規是指引，不是法律。** FTC 揭露與聲明真實性檢查標註風險，但不構成法律意見。

---

## 品質守衛

每次變更都跑一組 fail-closed 守衛（均在 `scripts/` 與 `tests/`）：

| 守衛 | 檢查 |
|------|------|
| `validate-skill.sh` | 全部 120 個技能的 frontmatter、必備章節、版本一致性、外掛相對連結。 |
| `golden-auditor-math.py` | **八套**框架的權重和 + 工作範例算術的確定性驗證。 |
| `check-evals.py` | eval 結構 lint + `structure-manifest.json`（120/120 技能均帶 eval 用例）。 |
| `check-pii.py` | 攔截提交的金鑰 / PII（token 級允許名單，fail-closed）。 |
| `check-stdlib-only.sh` | 依賴蔓延守衛 + 付費廣告帶金鑰 API 紅線。 |
| `check-versions.sh` | 版本同步守衛：system catalog、plugin/marketplace/OpenClaw manifests、根與本地化 README 徽章、AGENTS/CLAUDE/VERSIONS、GitHub About 和 120 個 skill 版本保持一致。 |
| `tests/test_connectors_local.py` | 覆蓋全部 29 個內建連接器模組之請求建構器／解析器的離線測試（CI 不連網）。 |
| `tests/test_hook_artifact_gate.sh` | hook 的 Artifact Gate + SessionStart 淨化的行為測試。 |

線上端點漂移由**手動**的 [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) 另行抽樣——對腳本中列出的每個託管連接器做一次最小真實呼叫 + 回應形狀斷言（限速應答記 SKIP）；發版前手動跑，絕不進 CI。

---

## 貢獻與文檔

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** —— 撰寫規則、貢獻清單、權威的 10 個追蹤面列表。
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** —— 各技能版本 + 變更日誌（目前套件：`20.0.0`）。
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** —— 安全、隱私、社群政策。
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** —— 面向 Agent 的本倉庫上下文。

---

## 免責聲明

這些技能用於輔助品牌敘事、SEO/GEO、紅人行銷、付費廣告、郵件行銷、產品發布與自然社媒工作流，但**不**保證排名、AI 引用、流量、互動、轉換、ROAS、送達率或任何業務結果。紅人、廣告、郵件與社媒合規檢查（FTC 揭露、聲明真實性、平台政策、同意/opt-in、實質關聯揭露）為指引，非法律意見。在用於重大策略、財務或法律決策之前，請與具備資格的專業人士核實建議。

## 授權條款

Apache License 2.0 —— 見 [LICENSE](../LICENSE)。

*最後同步英文 README：v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
