<div align="center">

# Aaron Marketing Skills

**120 のマーケティングスキル — ブランドナラティブ、SEO/GEO、インフルエンサー、Paid Ads、メール、Launch、ソーシャル — を一つの契約で。**

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

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | **日本語** | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

チャットエージェントをマーケティングオペレーターに変える Claude スキルとスラッシュコマンドのライブラリ。7 つの専門領域と 1 つの共有プロトコル層を一望：

| 層 | スキル | ライフサイクル（フェーズディレクトリ） | フレームワーク → ゲート | エントリポイント |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **ソーシャル** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **メール** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`（EQS） | `/aaron-marketing:email` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`（RQS） | `/aaron-marketing:ad` |
| **インフルエンサー** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor`（SQS）；`fit-scorer` が Suitability (S) を採点 | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **プロトコル層** | 8 | —（フェーズフローの外にある共有機構） | 7 つの真実レジストリ（entity · creator · offer/claims · consent · launch · channel · narrative）+ HOT/WARM/COLD メモリ | — |

`/aaron-marketing:auto` はあらゆる自然言語のゴールをシステム全体にルーティングします。スキルとコマンドは**プレーンな Markdown**です。小さな Bash/Python 標準ライブラリのランタイムが、フック、検証、採点、レジストリイベント、コネクタ、CI チェックを提供します（`pip` なし、ビルドステップなし）。**すべてのスキルは、あなたが提供するデータだけで Tier 1 で動作します**。コネクタが自動化するのは、データ取得か、明示的に承認された変更操作だけです。

権威ある型付きトポロジーは [`references/system-catalog.json`](../references/system-catalog.json) です。読みやすい四層マップ、全 120 パス、レジストリのオーナー、auditor のシンク、配布プロファイルは[生成されたシステムアーキテクチャ](system-architecture.md)を参照してください。

> 統合前に独立していたリポジトリは、いまはここを指す**道標リポジトリ**です —— [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)（最終の 20 スキル系列はタグ `v9.9.12` に保存）と [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)（最終の IMPACT 系列はタグ `standalone-final`）。姉妹リポジトリのポリシー：[docs/repo-family.md](repo-family.md)。

---

## 目次

- [なぜこのライブラリか](#なぜこのライブラリか)
- [インストール](#インストール)
- [初回実行](#初回実行)
- [アーキテクチャ](#アーキテクチャ)
  - [共有スキルコントラクト](#共有スキルコントラクト)
  - [システム：四層のマーケティングオペレーティングシステム](#システム四層のマーケティングオペレーティングシステム)
  - [品質システム：八つのフレームワーク、八つのゲート](#品質システム八つのフレームワーク八つのゲート)
  - [プロトコル層](#プロトコル層)
  - [メモリと自動化フック](#メモリと自動化フック)
- [スキルカタログ](#スキルカタログ)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO — SITE (16)](#seogeo--site-16)
  - [インフルエンサー — STAR (16)](#インフルエンサー--star-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [プロトコル層 (8)](#プロトコル層-8)
- [コマンド](#コマンド)
- [コネクタと拡張ティア](#コネクタと拡張ティア)
- [推奨ワークフロー](#推奨ワークフロー)
- [リポジトリ構成](#リポジトリ構成)
- [設計思想](#設計思想)
- [品質ガード (CI)](#品質ガード-ci)
- [コントリビュートとプロジェクトドキュメント](#コントリビュートとプロジェクトドキュメント)
- [免責事項](#免責事項)
- [ライセンス](#ライセンス)

---

## なぜこのライブラリか

| 原則 | 実務での意味 |
|-----------|---------------------------|
| **デフォルトで keyless** | 各スキルは、貼り付けた、あるいは無料/ファーストパーティのソースから取得したデータで **Tier 1** で動作します。有料ツールや MCP サーバーは任意の利便性であり、決して前提条件ではありません。Paid Ads スキルは**自アカウントの手動エクスポート**から採点します —— キー付き広告 API は決して必要ありません。 |
| **コンテンツファースト、実行可能なコントラクト** | スキルは Markdown のままです。小さな Bash/Python 標準ライブラリのランタイムが、パッケージ依存を追加せずに採点・状態・安全性・適合性を決定論的にします。 |
| **一つの共有コントラクト** | 120 のスキルすべてが同じ 7 セクションを公開し、`discipline` + `phase` メタデータを自己申告するため、ライブラリは一つのオペレーティングシステムのように振る舞います。各スキルは自らの入力・出力、そして次に引き継ぐ最良のスキルを知っています。 |
| **ゲート付きの品質** | 8 つのベンチマークが構造化された機械検証可能な判定を出力します。有界フックが無効な書き込みを検出し、pre-commit/CI はコミット済み Git の PII のみを保護し、runtime 成果物は検証しません。 |
| **真実はイベントに宿る** | 追記専用（append-only）の 7 本のレジストリイベントストリームが正準です。オーナーが管理するプロジェクションが、エンティティ・クリエイター・クレーム・同意・Launch・チャネル・ナラティブの状態を、破壊的キューなしで公開します。 |
| **ターンをまたぐメモリ** | HOT/WARM/COLD メモリモデルが、発見・スコア・未決事項をスキルとセッションの間で運び、入口でサニタイズします。 |
| **人間らしい声** | スキルには AI 臭検出器と禁止フレーズリストが同梱され、出力が人間が書いたように読めるようにします。 |

---

## インストール

Claude Code、Agent Skills 互換の任意のホスト、あるいは単純な `git clone` で使えます：

| ホスト | インストール |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` の後に `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ ホスト](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn)（中国語コミュニティ）** | `skillhub install <frontmatter-slug>`（例：`keyword-research`） |
| **任意のホスト** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

Claude Code では `marketplace add` はカタログを登録するだけです —— スキルとコマンドを実際に有効化するには `/plugin install aaron-marketing@aaron` を実行（または `/plugin` から選択）してください。汎用ホストで**単一**スキルを取得するには：`npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`。バンドルは [skills.sh レジストリ](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)で閲覧できます。エージェントごとのディレクトリ、frontmatter の癖、プラグイン外での劣化については：[docs/agent-compatibility.md](agent-compatibility.md)（120/120 インストール可能を検証、2026-07）。

プラグインをインストールしても `/mcp` リストには**何も**追加されません —— MCP カタログは [`docs/mcp-catalog.json`](mcp-catalog.json) にあり、Claude Code が自動登録するプラグインルートの `.mcp.json` パスの外に意図的に置かれているため、コピー＆ペースト用の参照にすぎません（[コネクタ](#コネクタと拡張ティア)を参照）。

---

## 初回実行

ホストが自動スキルルーティングをサポートしているなら、ゴールを記述するだけです：

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

あるいはスラッシュコマンドを使います —— ルーティングには `/auto`、または専門領域のエントリポイントを：

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` は意図を推論し、最小限の有用なワークフローを実行し、ブロッキングな判断でのみ立ち止まります。各スキルは貼り付けたデータで動作します；任意のツールは [CONNECTORS.md](../CONNECTORS.md) に文書化されています。

---

## アーキテクチャ

### 共有スキルコントラクト

各スキルは**同じ起動コントラクト**に従います —— 固定順の 7 セクション：

1. **Trigger / いつ使うか** —— スキルがいつ発火すべきか。
2. **Quick Start** —— コピー＆ペースト用プロンプト。
3. **Skill Contract** —— 期待される出力 · 読み取り · 書き込み · 昇格 · 完了条件 · 主要な次スキル。
4. **Handoff Summary** —— 次のスキルがきれいに引き継げる標準の受け渡し形式。
5. **Data Sources** —— `~~category` プレースホルダ。各々に keyless な Tier 1 パス。
6. **Instructions** —— 番号付きの手法（すべてのエクスポートを信頼できない入力として扱う）。
7. **Next Best Skill** —— 次にどこへ行くか（visited-set + 最大深度の終了ルール付き）。

各スキルは `metadata.discipline`（narrative / seo-geo / influencer / ad / email / launch / social / protocol）と `metadata.phase` も自己申告するため、ルーティングとクラスタリングが一様に機能します。コントラクトは [skill-contract.md](../references/skill-contract.md) に一度だけ文書化され、スキル間の共有状態は [state-model.md](../references/state-model.md) に宿ります。

### システム：四層のマーケティングオペレーティングシステム

一つのブランドボイスを、常時稼働する 5 つのチャネルを通じて表現し、Launch の瞬間へと凝縮し、そのすべてが共有された記録システムを読み書きします。7 つの専門領域、4 つの高度 —— これは寄せ集めではなく、一つのシステムです。

| 層 | 導入 | 専門領域 | ケイデンス |
|-------|-------|-------------|--------|
| **L1 · 戦略** —— 何を語るか / 我々は何者か | crawl | **Narrative** · TALE | 常時稼働 |
| **L2 · チャネル** —— 戦略を表現する常時稼働のエンジン（自有 → 有料） | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · STAR | 常時稼働（インフルエンサーはエピソード寄り） |
| **L3 · オーケストレーション** —— チャネルをまたぐ時限の瞬間 | run | **Product Launch** · RAMP | エピソード |
| **L4 · プロトコル** —— 共有された記録システム | — | 7 つの真実レジストリ + ワーキングメモリ · 8 つの auditor ゲート · 一つのスキルコントラクト | — |

Narrative はメッセージであり、チャネルはそれを表現する媒体です —— 各コアビルダーは、使用した正典の ID/バージョンとクレーム・プロジェクションのオフセット、あるいは明示的に承認されたフォールバック/ブロックを正確に記録します。各専門領域の 4 フェーズループは、その層の内側に宿ります（Narrative = Trace → Architect → Land → Evaluate）。

7 つすべてがフェーズ**ディレクトリ**（`narrative/trace/`…、`seo-geo/survey/`…、`influencer/scout/`…、`ad/research/`…、`email/setup/`…、`launch/research/`…、`social/explore/`…）を使います。注：「activate」はインフルエンサーではクリエイターへのアウトリーチを、Paid Ads ではアカウントのゲーティングを意味します —— 同じ語でも領域固有のスコープです。

### 品質システム：八つのフレームワーク、八つのゲート

8 つのベンチマークが「良い」を測定可能にします。各々が次元、集約方法、そして少数の**拒否項目**（残りに関わらずスコアを上限で抑える／ブロックするハードな失敗）を定義します：

| フレームワーク | 採点対象 | 項目 / 次元 | 集約 | 拒否項目 |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | ブランドナラティブの真実 / システム / 有効性 | T / A / L / E | `truth`・`system`・`effectiveness` のプロファイル結果は個別。全体の合成スコアなし | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | CORE/GEO と EEAT/SEO の診断ビューを備えたコンテンツ品質 | 80 項目 / 8 次元 | 完全なプロファイル加重結果。診断ビューは独立した合計ではない | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | ドメイン権威と引用信頼 | 40 項目 / 4 次元 | 算術プロファイル加重平均 | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | インフルエンサーの Suitability / Trust / Appeal / Return | S / T / A / R・40 項目 / 4 次元 | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | Paid Ads の増分貢献と運用品質 | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | メールの送信者完全性 / エンゲージメント / ナーチャー / 直接成果 | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | プロダクトローンチの準備 / アセット / モメンタム / 証明 | R / A / M / P・40 の安定 ID | `preflight`・`execution`・`outcome` のプロファイル結果は個別。時間軸をまたいで平均しない | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | オーガニックソーシャルの埋め込み度 / クラフト / ホスティング / 可観測性 | E / C / H / O・40 の安定 ID | 実行ごとに `asset-gate` か `program-maturity-*` プロファイルを一つだけ。異種ユニットは決して混ぜない | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

各フレームワークは **auditor クラスのゲート**によって強制されます —— 型付き成果物（`class: auditor-output`）を決定論的バリデータと有界なライフサイクル Hook で検証します。リポジトリ CI はバリデータと契約を回帰テストしますが、無視されたホストランタイム成果物は検査しません。ゲートはワークフローのステップなので、それぞれが自身の専門領域に宿り、そこで数えられます：

| ゲート | フレームワーク | 所在 | 判定 |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE プロファイル | `narrative/evaluate/` | truth/system/effectiveness の結果は個別。合成スコアなし |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED。信頼ラベルは説明目的のみ |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED に加えクリエイター向けの翻訳 |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP ライフサイクルプロファイル | `launch/mobilize/` | 宣言された一つのライフサイクル読み取りに対する SHIP / FIX / BLOCK / UNDECIDED |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO アセット/プログラムプロファイル | `social/host/` | 宣言された一つのユニット/プロファイルに対する SHIP / FIX / BLOCK / UNDECIDED |

**共有拒否ポリシー：** 検証済みの拒否項目が 1 件なら最終スコアを `min(raw, 59)` で上限化します。2 件以上なら `status: DONE` + `verdict: BLOCK` となり、最終スコアは出ません。証拠の欠落は `Unknown` であり、決して自動的な不合格にはなりません。型付きルールは [auditor-runbook.md](../references/auditor-runbook.md) に宿ります。

### プロトコル層

`protocol/` ディレクトリは、専門領域のフェーズフローの外に位置する**共有の真実＆メモリ機構**を収めます —— 8 スキル、別勘定です：

| スキル | 役割 | アンカー先 | 正準イベントストリーム / ランタイムの役割 |
|-------|-----|-------------|-----------------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | 正準的なブランド/エンティティプロファイル（ナレッジグラフ、Wikidata、AI 曖昧性解消） | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 正準的なクリエイター名簿/ドシエ —— 重複排除されたハンドル、出所ラベル付きのオーディエンス統計、料率、コンプライアンス履歴 | インフルエンサー | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | オファー＆クレーム裏付けの台帳 —— O1/T2 クレームチェックが照合して判定される記録 | Paid | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 被験者ごとの正準的な同意/抑制記録 —— S2/N1 拒否がこれに照らして判定 | メール | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 正準的な Launch ドシエ/カレンダー —— ティア、一方向のライフサイクル段階、権威ある日付/エンバーゴ、チャネル提出台帳；R1 段階真実拒否が照合する Launch 真実の SSOT | Launch | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 正準的なチャネルごとの記録 —— ハンドル、所有権/認可、プラットフォーム規範、開示デフォルト；ECHO E1 チャネル真実拒否が照合するチャネル真実の SSOT | ソーシャル | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 正準的なブランドナラティブの正典 —— 承認済みの戦略ナラティブ、メッセージシステム、言語/レキシコン、証拠点；TALE T1 真実拒否が照合するブランド正典の SSOT | Narrative | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD メモリのライフサイクル（キャプチャ · 昇格 · 降格 · アーカイブ · クエリ） | 全領域 | 非正準の `memory/` ランタイム状態 |

レジストリは**単一書き込み者ルール**に従い（他スキルは `registry-events.py` proposal events 経由で提出）、*キュレート*します —— 判定はゲートが行います。すべての下にある真に水平な層は `references/` プロトコル（[auditor-runbook](../references/auditor-runbook.md)、[state-model](../references/state-model.md)、[skill-contract](../references/skill-contract.md)、[humanizer-slop](../references/humanizer-slop.md)、[measurement-protocol](../references/measurement-protocol.md)）です —— 設計上、スキルではなくドキュメントとして共有されます。

### メモリと自動化フック

**メモリ**は温度で階層化され、プロンプトを膨らませずにコンテキストがスキルとセッションをまたいで生き残ります：

| 層 | 場所 | 振る舞い |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | セッションごとに自動読み込み；**80 行かつ 25 KB**（先に達した方）で上限。 |
| **WARM** | `memory/<subdir>/` | 再構築可能なワーキングプロジェクションと権限管理された監査成果物。正準のレジストリ真実は `memory/events/*.ndjson` に宿ります。 |
| **COLD** | `memory/archive/` | 降格した/古い記録、想起のために保持。 |

**フック**（`hooks/hooks.json`、ランナー `hooks/claude-hook.sh`）は 7 つの Claude Code イベントを配線します：

| イベント | マッチャー | 何をするか |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | **サニタイズ済み**の hot-cache + 未決事項ポインタを注入（プロンプトインジェクション行は塗りつぶし；シンボリックリンクのキャッシュは拒否）。 |
| `UserPromptSubmit` | （すべて） | 軽量なプロンプトごとのコンテキストフック。 |
| `PreToolUse` | 既知の書き込み可能ツール | サポートされる `memory/**` 書き込みの前に、正確なホストプロジェクト側ターゲットが Git-ignore されていることを検証します。そうでなければ書き込みは拒否されます。 |
| `PostToolUse` | 既知の書き込み可能ツール | 書き込み成功後に、事後状態のメモリ監査 + 有界な Artifact Gate 検証を実行します。 |
| `PostToolUseFailure` | 既知の書き込み可能ツール | 失敗したツールもすでにファイルを書いている可能性があるため、同じチェックを実行します。 |
| `PostToolBatch` | （すべて） | 並列ツールバッチのたびに、運用メモリと予約済み監査シンクを再チェックします。 |
| `Stop` | （すべて） | 最後の有界スイープを一度実行し、その後 active-stop ガードが終了を許可します。pre-commit/CI が守るのはコミット済み Git コンテンツの PII のみで、無視されたランタイム成果物は検証しません。 |

Artifact Gate は**フレームワーク非依存**です —— 同じフックが TALE、CORE-EEAT、CITE、STAR、ROAS、SEND、RAMP、ECHO の成果物をフレームワーク固有コードなしで検証します。

---

## スキルカタログ

スキルリンクは各 `SKILL.md` を開きます。各専門領域の下の **詳細** を展開すると、スキルごとの一行の目的が見えます。カタログの順序は[四層のストラータ](#システム四層のマーケティングオペレーティングシステム)に従います —— まず Narrative（L1 · 戦略）、次に 5 つの常時稼働チャネル、続いて Launch（L3 · オーケストレーション）、最後にプロトコル層です。

### Narrative — TALE (16)

`narrative/` 配下の 4 フェーズは Trace → Architect → Land → Evaluate に従います。`narrative-quality-auditor` は truth・system・effectiveness の各プロファイルを別々に実行します。フルレビューは 3 つの結果をリンクするだけで、決して平均しません。Narrative は、チャネルのビルダーたちが継承する L1 戦略です。

| フェーズ | スキル |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>スキルごとの目的（Narrative）</b></summary>

| スキル | TALE レバー | 何をするか |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | 自有面全体に実在する、現在の実際のブランドストーリーを捕捉 —— どんな再設計の前にも、正直な出発点。 |
| category-narrative-mapper | T | カテゴリの支配的なナラティブと名前付き代替をマッピングし、ブランドが守れる差別化ポジションを主張できるように。 |
| audience-belief-mapper | T | ターゲットオーディエンスがすでに信じ、疑い、気にかけていることをあぶり出す —— ナラティブが動かすべき信念。 |
| positioning-truth-tracer | T | 各ポジショニングクレームを裏付けまで遡り、支持されないものを退役させる（T1 真実拒否の上流）。 |
| strategic-narrative-designer | A | 核となる戦略ナラティブを設計 —— ブランドが先導する「世界の変化」の物語弧、賭け、解決。 |
| message-system-architect | A | メッセージシステムを設計 —— タグライン、柱、証拠点、オーディエンス別アングルを一つの首尾一貫した構造として。 |
| brand-language-codifier | A | ボイス、トーン、レキシコン、do/don't の言語を成文化し、あらゆるチャネルが一つのブランドに聞こえるように。 |
| story-bank-builder | A | チャネルが引き出せる、再利用可能な証拠ストーリー、顧客ナラティブ、アナロジーのバンクを構築。 |
| narrative-cascade-planner | L | ナラティブが希薄化やドリフトなく各チャネルと瞬間へどうカスケードするかを計画。 |
| pitch-narrative-builder | L | ナラティブをピッチ形式へ —— デッキの背骨、デモストーリー、投資家/プレス向けフレーミング。 |
| narrative-enablement-kit | L | 各チームがストーリーを一貫して語れるイネーブルメントキット —— トークトラック、FAQ、メッセージマップ。 |
| proof-point-packager | L | 証拠点をチャネル対応・claims-ledger 認識のアセットにパッケージング。 |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | 型付き TALE ゲート。プロファイルごとの結果を別々に返し、決して平均しません。`memory/audits/narrative/` に書き込みます。 |
| message-test-designer | E | メッセージテストを設計 —— バリアントマトリクス、オーディエンスセル、戦略ナラティブの共鳴読み。 |
| narrative-resonance-monitor | E | ナラティブがチャネル全体でどう着地しているかを keyless ソースから追跡（プロキシデータはラベル付き）。 |
| narrative-drift-monitor | E | ナラティブのドリフトを監視 —— チャネルが承認済み正典から逸れた箇所 —— し、修正を提起。 |

**領域横断で再利用**（元フェーズで計上、重複なし）：[positioning-mapper](../launch/research/positioning-mapper/SKILL.md)（論理的には Trace の入口、物理的には `launch/`）、[message-house-builder](../launch/assemble/message-house-builder/SKILL.md)、`audience-mapper`、`share-of-voice-tracker`（共鳴の分母）。**新規コネクタなし** —— ナラティブ共鳴は `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` を再利用 —— [tale-benchmark.md](../references/tale-benchmark.md) を参照。

</details>

### SEO/GEO — SITE (16)

4 つのフェーズディレクトリ（各 4 スキル）＋本領域の 2 つの品質ゲート（⛩ 印）。

| フェーズ | スキル |
|-------|--------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>スキルごとの目的（SEO/GEO）</b></summary>

| スキル | 何をするか |
|-------|--------------|
| keyword-research | ページ/トピック/キャンペーンのキーワード作業を開始 —— 意図、需要、あと一歩の機会。 |
| competitor-analysis | 競合の SEO 戦略を分析し、ドメインを比較し、そのキーワードとギャップをあぶり出す。 |
| serp-analysis | SERP を読み解く —— 機能、スニペット、People Also Ask、あるクエリのランキングパターン。 |
| content-gap-analysis | 競合に対して欠けているトピックとカバレッジの穴を見つける。 |
| content-writer | SEO 最適化された記事、ランディングページ、製品コピーを執筆・リフレッシュ。 |
| geo-content-optimizer | AI エンジン（ChatGPT、Perplexity、AI Overviews、Gemini、Claude、Copilot）向けにコンテンツを最適化。 |
| serp-markup-builder | Title/Meta/OG/Twitter タグ + JSON-LD / Schema.org 構造化データ。 |
| page-play-builder | テンプレート駆動のページ施策 —— プログラマティックページ、パラサイトプラットフォーム、比較ページ、local/GBP。 |
| ⛩ content-quality-auditor | 80 項目の CORE-EEAT 公開準備ゲート（SHIP/FIX/BLOCK）。 |
| technical-seo-checker | サイト速度、Core Web Vitals、インデックス、クロール可能性、robots。 |
| on-page-seo-checker | ページレベルの on-page 健全性を監査 —— 見出し、キーワード配置、画像、品質シグナル。 |
| site-structure-optimizer | 内部リンク、アンカーテキスト、孤立ページ、ページ階層、URL 分類、hub/spoke クラスター。 |
| ⛩ domain-authority-auditor | 40 項目の CITE ドメイン信頼ゲート（TRUSTED/CAUTIOUS/UNTRUSTED）。 |
| rank-tracker | キーワード順位、順位変動、下落を追跡。 |
| performance-monitor | 複数指標の SEO/GEO レポート、ダッシュボード、しきい値アラート。 |
| offsite-signal-analyzer | バックリンクプロファイル + リンク品質、加えて自分の GA4/GSC/ログ内の AI アシスタントからの参照トラフィック。 |

</details>

### Social — ECHO (16)

`social/` 配下の 4 フェーズは Explore → Craft → Host → Observe に従います。`social-quality-auditor` は `asset-gate` か一つの program-maturity プロファイルを選びます。この 2 つの構成概念は決して組み合わせません。この専門領域は投稿・エンゲージメント・DM の自動化を一切含みません。

| フェーズ | スキル |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>スキルごとの目的（Social）</b></summary>

| スキル | ECHO レバー | 何をするか |
|-------|-----------|--------------|
| channel-portfolio-planner | E | オーディエンスが実際にいる場所から、プラットフォームの組み合わせとチャネルごとの役割/ケイデンスを選ぶ（チャネルをレジストリに記録）。 |
| voice-dossier-builder | E | 一貫した人間らしいプレゼンスのためのブランドボイス、トーン、ペルソナ、do/don't レキシコン。 |
| platform-norm-profiler | E | 投稿する前の、プラットフォーム別の規範、フォーマット、ランキングシグナル、レッドラインルール。 |
| participation-warmup-planner | E | 非宣伝的なコミュニティウォームアップ計画 —— 売り込む前にどこに現れて価値を加えるか。 |
| social-calendar-builder | C | 編集カレンダー —— テーマ、シリーズ、実キャパシティに合わせたケイデンス（過剰投稿なし）。 |
| social-creative-builder | C | プラットフォームネイティブな投稿（hook/body/CTA）、メッセージ整合、claims-ledger 認識。 |
| short-video-scripter | C | ショート動画スクリプト —— フック、ビート、画面上テキスト、リテンション構造。 |
| advocacy-program-designer | C | 従業員/コミュニティのアドボカシープログラム —— オプトイン、開示デフォルト、シェア可能なアセットキット。 |
| ⛩ social-quality-auditor | asset gate / program maturity | 一つのユニット/プロファイルに対する型付き ECHO ゲート。アセットと運用の構成概念は決して混ぜません。`memory/audits/social/` に書き込みます。 |
| engagement-inbox-manager | H | 返信/コメント/DM トリアージの playbook —— 応答ティア、エスカレーション、真正なエンゲージメントの規律（捏造/餌付けエンゲージメントなし）。 |
| social-selling-planner | H | 創業者/チームのソーシャルセリング動線 —— 関係優先のアウトリーチ、自動 DM なし。 |
| crisis-response-planner | H | 事前起草した危機ティア、保留声明、エスカレーションラダー、キュー停止トリガー。 |
| social-pulse-monitor | O | keyless ソースからの言及/センチメント/トピックのパルス、spike-vs-sustain の判読（プロキシデータはラベル付き）。 |
| share-of-voice-tracker | O | 期間安定の分母に対する、名前付き競合とのシェアオブボイス。 |
| dark-social-attributor | O | ダークソーシャル/未リンクトラフィックの帰属 —— UTM の規律、自己申告アトリビューションの捕捉、参照元パース。 |
| social-measurement-loop | O | 出荷済みの変更を、あるウィンドウでベースラインに照らして読み戻す → Promote / Keep-testing / Rollback。 |

**領域横断で再利用**（元フェーズで計上、重複なし）：`trend-spotter`、`audience-mapper`、`content-amplifier`、`outreach-manager`、`competitor-tracker`、`landing-optimizer`、`performance-analyzer`、`roi-calculator`、`report-generator`、`offer-claims-registry`、`community-launch-runner`、`creator-registry`、`page-play-builder`、`memory-management` —— [echo-benchmark.md](../references/echo-benchmark.md) を参照。

</details>

### Email — SEND (16)

`email/` 配下の 4 つのフェーズディレクトリ（各 4 スキル）が SEND ループに従います；ゲート（⛩ email-quality-auditor）は Deliver に位置。ゲートだけが目標加重 EQS を計算します —— 他のスキルはそれぞれ 1 つのレバーを動かして引き継ぎます。ユースケース非依存（B2C ライフサイクル / B2B コールドアウトバウンド / newsletter-creator）；目標加重列が力点を選びます。

| フェーズ | スキル |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>スキルごとの目的（メール）</b></summary>

| スキル | SEND レバー | 何をするか |
|-------|-----------|--------------|
| deliverability-qa | S | 送信前の SPF/DKIM/DMARC/BIMI 認証、レピュテーション、inbox-placement、スパムコンテンツ、リスト衛生（S1 チェック）。 |
| list-segment-builder | E | 自社のリスト/CRM/GA4 エクスポートから、行動 + ライフサイクル段階のセグメントと抑制ルール。 |
| list-growth-designer | S (+N) | リスト成長戦略 —— 獲得チャネル、リードマグネット構想、準拠したオプトインキャプチャフロー spec、リファラルループの仕組み；獲得時に捕捉される S 同意品質に寄与。 |
| list-hygiene-monitor | S | 継続的なリスト健全性 —— バウンス/苦情の剪定、サンセットポリシー、再許諾、非アクティブセグメントの抑制。 |
| email-creative-builder | E (+D) | 件名/プリヘッダー/本文/CTA。ランディングページとメッセージ整合、claims-ledger を認識。 |
| subject-line-lab | E | 件名/プリヘッダーの発想とスコアリング —— 長さ、スパムトリガー、好奇心/明確性のバランス、テスト用バリアントセット。 |
| email-render-builder | E | HTML メールのビルド/QA —— クライアント互換性、ダークモード、アクセシビリティ、プレーンテキスト代替、レンダーテストチェックリスト。 |
| dynamic-content-personalizer | E | マージタグ/liquid のパーソナライズブロック、条件付きコンテンツルール、フォールバック値の安全性。 |
| email-sequence-designer | N | ライフサイクル/自動化フロー（welcome、cart、post-purchase、win-back）+ 頻度ガバナンス。 |
| newsletter-monetization-planner | D | 有料購読、スポンサーシップ在庫 + レートカード、リファラル成長ループの経済性。 |
| preference-frequency-manager | N | プリファレンスセンター設計と送信頻度ガバナンスで疲弊と解除を削減。 |
| reactivation-specialist | N | 休眠購読者向けの win-back / 再エンゲージフロー、サンセット-or-回復の判断ルール付き。 |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | auditor クラスの SEND ゲート：EQS を採点、S1/S2/N1/D1 を強制、SHIP/FIX/BLOCK を出力；**送信前 go/no-go** モードを内蔵。 |
| send-experiment-designer | E | A/B / 送信時刻 / ホールドアウト設計、サンプルサイズ + 有意性の判読（promote/kill）。 |
| inbox-placement-monitor | S | シードリストとプロバイダーシグナル経由の inbox-vs-spam プレースメント継続追跡、レピュテーション変動アラート付き。 |
| cold-outbound-sequencer | D | 準拠した B2B コールドアウトバウンドの頻度 —— deliverability に安全なランプ、パーソナライズトークン、返信処理ステップ。 |

**領域横断で再利用**（元フェーズで計上、重複なし）：[audience-mapper](../influencer/scout/audience-mapper/SKILL.md)、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)、[offer-claims-registry](../protocol/offer-claims-registry/SKILL.md)。

</details>

### Paid Ads — ROAS (16)

`ad/` 配下の 4 つのフェーズディレクトリ（各 4 スキル）が ROAS ループに従います；ゲート（⛩ ad-account-auditor）は Activate に位置。ゲートだけが目標加重 RQS を計算します —— 他のスキルはそれぞれ 1 つのレバーを動かして引き継ぎます。

| フェーズ | スキル |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>スキルごとの目的（Paid Ads）</b></summary>

| スキル | ROAS レバー | 何をするか |
|-------|-----------|--------------|
| campaign-architect | A + 構造 | アカウント/キャンペーン構造、キャンペーンタイプの適合、マッチタイプ、除外キーワード/除外、Paid↔オーガニックのカニバリゼーション；再帰的な **search-term-mining** モードを内蔵。 |
| audience-segment-builder | A | 自社の顧客/CRM/GA4 エクスポートをシードオーディエンス、類似シード、除外セグメント、ファネル段階別ターゲティングマップに変換。 |
| search-term-miner | A | 検索語句レポートから除外語、新規キーワード候補、マッチタイプの精緻化を採掘。 |
| product-feed-optimizer | O | Shopping/PMax フィード衛生 —— タイトル、属性、GTIN、カテゴリマッピング、不承認の修正。 |
| ad-creative-builder | O | RSA の見出し/説明文、フック、角度マトリクス。遷移先ページとメッセージ整合。 |
| ad-test-designer | O (+S) | A/B/n & 増分テストを設計（仮説、バリアントマトリクス、サンプルサイズ/検出力）し、有意性を判読 → promote/kill。 |
| bid-strategy-planner | S | 目標別（tCPA/tROAS/max-conversions）に入札戦略を選定・設定し、ターゲットをシード、学習期の移行を計画。 |
| landing-experience-checker | O | クリック後ページの QA —— 広告関連性、読み込み速度、モバイル、ポリシー —— 広告↔ページのメッセージ整合チェック。 |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | auditor クラスの ROAS ゲート：RQS を採点、R1/R2/O1/O2/A1 を強制、SHIP/FIX/BLOCK を出力；**Launch go/no-go** モードを内蔵。 |
| conversion-signal-qa | R | ローンチ前のトラッキング QA（イベント発火、UTM 衛生、重複排除ゲート、ウィンドウ整合、iOS-ATT フラグ）—— R1/R2 の前提（シグナルを構築；ゲートが採点）。 |
| placement-exclusion-manager | A | プレースメント/オーディエンス除外リスト —— ブランドセーフティのブロック、ジャンクプレースメントの剪定、無駄支出の抑制。 |
| conversion-value-mapper | R | コンバージョンアクションを値/重みと値ルールにマッピングし、tROAS が生の件数でなく真のマージンに入札するように。 |
| paid-measurement-loop | R (+S) | 出荷済みの変更を、あるウィンドウで対照に照らして読み戻す → Promote / Keep-testing / Rollback / Unproven。 |
| attribution-reconciler | R | GA4/ecommerce 真値集合に対する常時 order-ID 重複排除、ウィンドウ/通貨の正規化、モデル比較、増分。 |
| budget-pacing-monitor | S | フライト全体で予算に対する消化ペースを追跡、過少/過剰配信を検知、ペーシング修正を推奨。 |
| fatigue-frequency-manager | O | フリークエンシーとクリエイティブ劣化のシグナルを監視、疲弊した広告を検知、リフレッシュ/ローテーションを計画。 |

**領域横断で再利用**（元フェーズで計上、重複なし）：[budget-optimizer](../influencer/target/budget-optimizer/SKILL.md)（支出 + bid-pacing/学習期モード）、[landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)（クリック後）、[roi-calculator](../influencer/report/roi-calculator/SKILL.md)（リターン計算）、[report-generator](../influencer/report/report-generator/SKILL.md)、[performance-analyzer](../influencer/report/performance-analyzer/SKILL.md)。

</details>

### インフルエンサー — STAR (16)

4 つのフェーズディレクトリ（各 4 スキル）；本領域のゲート（⛩ creator-content-auditor）は Activate に位置。

| フェーズ | スキル |
|-------|--------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>スキルごとの目的（インフルエンサー）</b></summary>

| スキル | 何をするか |
|-------|--------------|
| audience-mapper | クリエイターと組む前に、ターゲットオーディエンスをプロファイルし、そのサブカルチャー / マイクロコミュニティを地図化。 |
| trend-spotter | キャンペーンのタイミングとテーマ —— トレンドのハッシュタグ、サウンド、フォーマット、文化的モーメント。 |
| influencer-discovery | クリエイター名簿をゼロから構築、新プラットフォームへ拡大、nano/micro を大規模にソーシング。 |
| fit-scorer | ショートリストの客観的な加重フィットスコア（STAR Suitability (S) で採点）。 |
| competitor-tracker | 競合のクリエイター、キャンペーン、フォーマット、推定リーチ/支出、ギャップ。 |
| campaign-planner | キャンペーン、製品ローンチ、テントポール、常時稼働のクリエイタープログラムを計画。 |
| brief-generator | 標準化されたインフルエンサーブリーフと再利用可能なチームテンプレート。 |
| budget-optimizer | ティア/プラットフォームに支出を配分、ROI を予測、シナリオをモデリング（Paid Ads の支出 + bid-pacing にも寄与）。 |
| outreach-manager | ピッチ、フォローアップの頻度、再エンゲージ、料率交渉、ステータス追跡。 |
| ⛩ creator-content-auditor | クリエイターの提出物への公開前ゲート判断（STAR Trust：FTC 開示 STAR-T1、クレーム完全性 STAR-T2）。 |
| contract-helper | クリエイター契約の起草/レビュー —— 使用権、独占、標準条項。 |
| content-amplifier | オーガニックなクリエイターコンテンツを有料出稿で増幅し、UGC を Paid、Web、メール、オーガニックへ再利用。 |
| landing-optimizer | クリエイター/Paid トラフィック向けランディングページ —— メッセージ整合、モバイル、A/B（Paid のクリック後にも寄与）。 |
| performance-analyzer | クリエイター結果を評価、クリエイターを比較、センチメント、コンバージョン（Paid のクロスチャネルスコアカードも）。 |
| roi-calculator | ROI を測定/予測、予算を擁護、クリエイター/ティアを評価（共有のリターン計算エンジン、Paid を含む）。 |
| report-generator | 期間後のステークホルダー向け書面レポート（Paid Ads レポートも）。 |

</details>

### Launch — RAMP (16)

`launch/` 配下の 4 フェーズは Research → Assemble → Mobilize → Prove に従います。`launch-readiness-auditor` は実行ごとに `preflight`・`execution`・`outcome` のいずれか一つのプロファイルを選びます。ライフサイクルの結果はリンクされますが、決して平均されません。

| フェーズ | スキル |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>スキルごとの目的（Launch）</b></summary>

| スキル | RAMP レバー | 何をするか |
|-------|-----------|--------------|
| positioning-mapper | R | Dunford 流のポジショニングキャンバス —— 名前付き競合代替、独自属性、価値テーマ、beachhead セグメント、onlyness ステートメント。 |
| launch-tier-planner | R | ティア判断（Tier 1 フラッグシップ / Tier 2 ターゲット / Tier 3 changelog レベル）、ローンチタイプ宣言、KPI 目標、kill 基準付きリスクレジスタ。 |
| launch-window-planner | R | 候補ウィンドウ比較（衝突 / 追い風 / リスク）、launch-week vs rolling-release の判断、ストア審査バッファ、エンバーゴウィンドウ定義。 |
| early-access-designer | R | waitlist→concept→alpha→beta→GA の段階ラダー、卒業基準、コホートゲーティング、フィードバックループ、リファラルの仕組み（R1 段階真実拒否の上流）。 |
| message-house-builder | A | メッセージハウス（タグライン、ワンライナー、価値の柱、証拠点）+ working-backwards PR-FAQ の背骨 + チャネル別アングルパック（A1 の上流）。 |
| launch-asset-packager | A | ティア範囲のローンチアセットマニフェスト —— プレスキット spec、デモ/スクショ spec、ローンチ FAQ、ストアリスティングメタデータ、技術的な go-live チェックリスト。 |
| pricing-packaging-planner | A | ローンチの価格 & パッケージング —— ティア構造、価値対価格マップ、ローンチオファーのラダー、卒業パス付きベータ価格、保証条件。 |
| sales-enablement-kit | A | 内部イネーブルメント —— バトルカード、セールストークトラック、反論処理表、内部 FAQ + CS マクロ、エンバーゴを守った内部アナウンス。 |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | 一つのライフサイクル読み取りに対する型付き RAMP ゲート。時間軸をまたいで平均しません。`memory/audits/launch/` に書き込みます。 |
| launch-day-conductor | M | 時間ブロック化したローンチ当日ランブック —— 前提条件ゲートチェック、不可逆プッシュ後の観察ウィンドウ判定、P0–P3 インシデントラダー + ロールバック playbook。 |
| community-launch-runner | M | プラットフォーム別提出パッケージ（Product Hunt、Show HN、subreddit、ディレクトリ波、地域/中国語チャネル）をプラットフォームのレッドラインチェックの下で。 |
| press-media-relations | M | 三層のメディア/アナリストリスト、エンバーゴピッチのタイミング、標準構造のプレスリリース草案、アナリストブリーフィングの骨子。 |
| launch-monitor | P | T-0→T+30 ウィンドウ監視 —— 計測検証（P1 の上流）、rank/レビュー/ニュースのポーリング、D0/W1/M1 の KPI スナップショット、spike-vs-sustain の判読。 |
| launch-feedback-synthesizer | P | フィードバックテーマのダイジェスト、open→shipped ステータスループ（「you asked, we shipped」）、準拠したソーシャルプルーフ収集。 |
| launch-retro-analyzer | P | D1/W1/M1 レトロ —— チャネル別 actual-vs-target、最大のミスへの 5-Whys、keep/kill/change の判断、レジストリへの結果スナップショット。 |
| momentum-planner | P | T+1→T+30 モメンタム計画 —— ローンチモーメントカレンダー、アナウンスのティアルーティング、relaunch の正当性判断、次の Tier-1 モーメント。 |

**領域横断で再利用**（元フェーズで計上、重複なし）：`audience-mapper`、`trend-spotter`、`budget-optimizer`、`landing-optimizer`、`campaign-planner`、`outreach-manager`、`content-amplifier`、`email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`、`campaign-architect` / `ad-creative-builder`、`page-play-builder` / `content-writer`、`technical-seo-checker` / `serp-markup-builder`、`performance-monitor`、`keyword-research`、`entity-registry`、`offer-claims-registry`、`consent-registry`、`list-growth-designer`、`roi-calculator` / `performance-analyzer` / `report-generator` —— [ramp-benchmark.md](../references/ramp-benchmark.md) を参照。

</details>

### プロトコル層 (8)

共有の真実 & メモリ機構 —— 役割と単一書き込み者ルールは [アーキテクチャ § プロトコル層](#プロトコル層) を参照。

| グループ | スキル |
|-------|--------|
| **プロトコル** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>スキルごとの目的（プロトコル）</b></summary>

| スキル | 何をするか |
|-------|--------------|
| entity-registry | ナレッジグラフ、Wikidata、AI 曖昧性解消のための正準的エンティティプロファイル。 |
| creator-registry | 正準的なクリエイター名簿/ドシエ —— 重複排除されたハンドル、出所ラベル付きのオーディエンス統計、料率、コンプライアンス履歴。 |
| offer-claims-registry | 正準的なオファー & クレーム裏付け台帳 —— O1/T2 クレームチェックが照合して判定される記録。 |
| consent-registry | 被験者ごとの正準的な同意/抑制記録 —— オプトインのタイムスタンプ + 法的根拠、ダブルオプトインの証明、追記のみの解除/バウンス/苦情履歴；S2/N1 拒否が照合する記録。 |
| launch-registry | ローンチごとの正準的ドシエ + ローンチカレンダー —— ティア、ローンチタイプ、一方向のライフサイクル段階（draft→…→GA）、権威ある日付 + エンバーゴ約束、チャネル提出台帳、結果スナップショット；Launch 真実の SSOT。 |
| channel-registry | 正準的なチャネルごとの記録 —— ハンドル、所有権/認可、プラットフォーム規範、開示デフォルト；ECHO E1 チャネル真実拒否が照合するチャネル真実の SSOT。 |
| narrative-registry | 正準的なブランドナラティブの正典 —— 承認済みの戦略ナラティブ、メッセージシステム、言語/レキシコン、証拠点；TALE T1 真実拒否が照合するブランド正典の SSOT。 |
| memory-management | HOT/WARM/COLD プロジェクトメモリのレビュー、昇格、降格、アーカイブ。 |

</details>

---

## コマンド

8 つのコマンド：`/aaron-marketing:auto` が任意のゴールを 7 領域すべてにルーティングし、各領域はちょうど 1 つの明示的なエントリポイントを持ちます。ソース：[commands/](../commands)。

| コマンド | 用途 | 絞り込み |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | 任意のゴールを記述 —— 意図を推論し最小限の有用なワークフローを実行 | `--deep`（網羅 / ストレステスト） |
| `/aaron-marketing:narrative` | ブランドナラティブ（TALE ループ）：現在のストーリー & カテゴリをトレース、戦略ナラティブ & メッセージシステムを設計、チャネル全体に着地、品質ゲート、共鳴 & ドリフト | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO をエンドツーエンド（SITE ループ）：需要/競合のサーベイ、コンテンツの実装、品質/技術/オンページのチューニング、権威/順位/レポート/メモリの評価 | `--phase survey\|implement\|tune\|evaluate` + フェーズ別フラグ（`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`） |
| `/aaron-marketing:influencer` | インフルエンサー（STAR ループ）：オーディエンスインサイト、スカウティング & フィット、ターゲティング、アウトリーチ、増幅、ROI レポーティング | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | Paid ads（ROAS ループ）：セグメント、構造、クリエイティブ、実験設計、監査ゲート、測定 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | メール（SEND ループ）：deliverability/consent、セグメンテーション、クリエイティブ、ライフサイクルフロー、収益化、送信テスト、監査ゲート | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch（RAMP ループ）：ポジショニング、ティア & ウィンドウ、メッセージハウス & アセット、readiness ゲート、ローンチ当日の運行、監視 & レトロ | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Organic social（ECHO ループ）：チャネルポートフォリオ & ボイス、カレンダー & クリエイティブ、品質ゲート、エンゲージメント/危機のホスティング、パルス & 測定 | `--phase explore\|craft\|host\|observe` |

日々の作業は通常 `/aaron-marketing:auto` から始まります；他の 7 つは明示的な領域エントリポイントで、`--phase` で段階を絞ります。

---

## コネクタと拡張ティア

スキルは具体的なベンダーではなく `~~category` プレースホルダ（`~~SEO tool`、`~~web analytics`、`~~ad platform`、`~~email platform` など）でツールを命名し、各カテゴリには **keyless な Tier 1 パス**があります。完全なレシピ —— 各カテゴリの無料/ファーストパーティのエンドポイントを含む —— は [CONNECTORS.md](../CONNECTORS.md) にあります。

### コネクタ層はそれ自体が一つの製品

**100 以上の文書化された統合パス**を、設計された 3 つの層に —— そのどれもが席に値します：

| 層 | 得られるもの |
|-------|--------------|
| **28 の同梱・依存関係ゼロのコネクタ** | 純粋な Python 標準ライブラリ —— `pip` 不要、ビルドステップ不要。keyless なライブ SERP + JS レンダースクレイピング（Firecrawl、Tavily）、AI 回答の引用プローブ、DNS-over-HTTPS のメール認証取得、Wikipedia 注目度シリーズ、GDELT ニュース言及、本物の YouTube クリエイター指標、IndexNow + Baidu インデックス送信、Resend ESP 自動化、そしてそれらのいずれをも前後比較の時系列に変える git 差分可能な測定台帳。 |
| **60 以上の文書化された公式/無料 API** | 各行がベンダーの**公式ドキュメント**をリンクし、検証日を持ち、各リンクは公開前に HTTP で確認されます。多くのツールリストが見落とすパスを含みます：GSC URL Inspection、CrUX History（40 週間のフィールド CWV）、Gmail Postmaster Tools API、Meta の Ad Library、Microsoft Clarity の Data Export API。 |
| **ベンダー MCP サーバー** | 18 のリモートエンドポイントをカタログ化（決して自動登録されません —— あなたの `/mcp` リストはきれいなまま）、加えて Google Analytics、Search Console、**Google Ads**、**Microsoft Clarity** の公式セルフホストサーバー。2 つのリモート MCP はキー不要で動作します（Firecrawl、Tavily）。 |

単に数が多いだけでなく信頼できる理由：

- **3 つの安全クラス、設計されたゲート**（[SECURITY.md](../SECURITY.md)）：ホスト型フェッチャーは各委任フェッチの前に**ローカルで robots.txt を事前検査**し、Disallow では拒否します；外部状態を変えるもの（メール送信、インデックス送信）はすべて、明示的な `--live` フラグの背後で**デフォルト dry-run** です。ベンダーが対応する場合は冪等キーを用い、非対応なら自動リトライしません。
- **検証、そして再検証**：エンドポイントは日付付きでベンダー一次ドキュメントに照合され、keyless パスはライブでテストされ、CI ガードがバージョン/追跡の同期を強制し、リリース前のライブスモークがエンドポイントのドリフトを捕捉します（すでに本物の API 変更を捕捉 —— 2 回）。
- **判定ではなく事実**：コネクタはレコードの存在、パース済みタグ、生シリーズを報告します；判定は auditor ゲートが行い、スキルは各数値に **Measured / User-provided / Estimated** を付けます。
- **成文化された playbook**（[docs/connector-playbook.md](connector-playbook.md)）が各追加を統治します —— 適格化、検証、実装、テスト、配線、文書化、追跡、回帰、記録 —— カタログが成長しても品質が崩れないように。

| ティア | 必要なもの | 得られるもの |
|------|----------|---------|
| **Tier 1**（デフォルト） | なし | データを貼り付ける、または無料/公開ソースから取得。分析フレームワークはいずれにせよ走ります。 |
| **Tier 2** | 1 つの無料ファーストパーティ API または MCP | 自分の GSC / GA4 / Core Web Vitals データの自動取得。 |
| **Tier 3** | より充実した MCP セット | 完全自動のマルチソースワークフロー。 |

- **同梱・依存関係ゼロのヘルパー** は `scripts/connectors/` 配下（Python 標準ライブラリのみ）にあり、公開/自有データをローカルで取得します —— 例：PageSpeed/CrUX、Open PageRank、ページクロール、Wayback CDX、Wikidata SPARQL、Common Crawl、advertools レシピ —— 加えて **`resend.py`**（メールスキル向けの Resend ESP 直結自動化：無料枠キーでドメイン認証状態、seed-test 送信、抑制同期、ブロードキャストのスケジューリング；変更系サブコマンドはデフォルト dry-run で `--live` が必要）、および **`firecrawl.py`** + **`tavily.py`**（research スキル向けの keyless ホスト型フェッチャー自動化：Firecrawl はライブ Web SERP + JS レンダーページの markdown + サイトマップ；Tavily はスコア付き検索 + GEO 用の AI 回答エンジンの引用元プローブ + URL 抽出 —— どちらもキー不要で無料、どちらもローカル robots.txt 事前検査を内蔵）。
- **無料/keyless ソース**をカテゴリ別に文書化：Google Search Console & GA4（自有データ）、PageSpeed/CrUX、Wikidata、Common Crawl、Open PageRank、Firecrawl keyless SERP/スクレイプ、Tavily keyless AI 検索、DNS-over-HTTPS メール認証レコード（`doh.py`）、Wikipedia 注目度シリーズ（`pageviews.py`）、GDELT ニュース言及（`gdelt.py`）、無料キーの YouTube クリエイター指標（`youtube.py`）、IndexNow + Baidu インデックス送信（`indexpush.py`、dry-run ゲート付き）、広告透明性ライブラリ（Meta/Google/TikTok）、そして crt.sh、W3C バリデータ、oEmbed、HN Algolia のレシピ行。
- **オプトイン MCP サーバー**（Ahrefs、Semrush、SE Ranking、SISTRIX、SimilarWeb、セルフホストの無料 **OpenSEO** スイート、Cloudflare、Vercel、HubSpot、Amplitude、Notion、Webflow、Sanity、Contentful、Slack、Resend、keyless の Firecrawl と Tavily）は [`docs/mcp-catalog.json`](mcp-catalog.json) に**コピー＆ペースト用の参照としてのみ**カタログ化されています —— カタログは自動登録されるプラグインルートの `.mcp.json` パスの外にあるため、あなたのために何も登録されません。欲しいエントリを自分の MCP 設定にコピーしてください。

Paid Ads スキルは**自アカウントの手動エクスポート**（ネイティブ広告マネージャーの CSV、GA4、ecommerce）から採点します。キー付き広告プラットフォーム API（Google Ads SDK、Meta Marketing API）はオプトインの Tier-2/3 のみで、**決して** Tier 1 の要件ではありません。メールスキルも同様 —— **自分の ESP エクスポート**から採点します —— そして各 deliverability シグナルは keyless（DNS ルックアップ、DMARC RUA レポート、seed-list の inbox テスト）なので、キー付き ESP API もまた決して Tier 1 の要件ではありません；あなたの ESP が Resend なら、同梱の `resend.py` が無料枠で同じループを自動化します。

---

## 推奨ワークフロー

実際のゴールは複数の分野にまたがることがほとんどです。`/aaron-marketing:auto` は自然言語のゴールを 7 分野の最小限のスキルチェーンへルーティングします——たとえばプロダクトローンチなら Launch・Email・Social・Paid を同時に動かします:

```text
/aaron-marketing:auto 3 週間後に Product Hunt で v2 をローンチ——ウェイトリスト 1,200 人。ページ、メール、ローンチ当日のプランが必要
```

1 つの分野のループを端から端まで回すこともできます（各分野ディレクトリの `README.md` ガイドがシナリオ別のプレイを提供します）:

**Narrative（TALE ループ）**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor`（⛩ TALE ゲート）→ `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO（SITE ループ）**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor`（⛩ 公開ゲート）→ `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`；信頼レビューは `domain-authority-auditor`（⛩）

**Social（ECHO ループ）**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor`（⛩ ECHO ゲート）→ `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**Email（SEND ループ）**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` （⛩ EQS ゲート）を送信前に

**Paid Ads（ROAS ループ）**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` （ページは `landing-optimizer`）
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` （⛩ RQS ゲート）を予算投入前に
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**インフルエンサー（STAR ループ）**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer`（STAR Suitability）
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor`（⛩ STAR ゲート）→ `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Launch（RAMP ループ）**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor`（⛩ RAMP ゲート）→ `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

完全な信頼レビューには、`content-quality-auditor` と `domain-authority-auditor` を組み合わせて合計 120 項目の評価に。`memory-management` が有効なら、引き継ぎと未決事項は HOT/WARM/COLD メモリに自動で永続化されます。

---

## リポジトリ構成

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE（16、そのゲートを含む）
seo-geo/{survey,implement,tune,evaluate}/                   # SEO/GEO（16、2 つのゲートを含む）
influencer/{scout,target,activate,report}/                     # インフルエンサー（16、そのゲートを含む）
ad/research|orchestrate|activate|scale/            # Paid Ads — ROAS（16、そのゲートを含む）
email/setup|engage|nurture|deliver/                  # Email — SEND（16、そのゲートを含む）
launch/research|assemble|mobilize|prove/             # Launch — RAMP（16、そのゲートを含む）
social/explore|craft|host|observe/                   # Social — ECHO（16、そのゲートを含む）
protocol/                                            # プロトコル層（8）— 真実レジストリ + メモリ
commands/        # 8 つのスラッシュコマンド（auto, narrative, seo-geo, influencer, ad, email, launch, social）
references/      # 共有コントラクト、状態モデル、8 つのベンチマーク、auditor runbook、プラットフォームパック
evals/           # スキルごとの構造 eval ケース + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh（唯一のランタイムロジック）
scripts/         # validate-skill.sh + connectors/（stdlib）+ CI ガード
memory/          # HOT/WARM/COLD 足場 + レジストリストア（entities/creators/claims/consent/launch/channels/narrative-registry）
docs/            # ローカライズ済み README（zh）
.claude-plugin/  # plugin.json + marketplace.json ミラー
```

---

## 設計思想

- **コンテンツファースト。** スキルは Markdown です。ゼロ依存の Bash/Python 標準ライブラリランタイムがコネクタ、採点、レジストリイベント、検証、チェックを提供します。サードパーティ / `pip` 依存は CI が禁止します。
- **keyless ファースト。** 各 `~~category` には無料/自有データのレシピがある；MCP と有料ツールは純粋な利便性。
- **外科的 & MECE。** 各スキルは境界の明確な 1 つの職務を持つ；重なる作業は薄い新スキルではなく既存スキルの*モード*として出荷。レジストリはキュレート、ゲートは判定、アナライザはゲートに給餌。
- **数字を捏造しない。** スキルは各数値に Measured / User-provided / Estimated を付け、AI 臭 / 禁止フレーズ検出器を同梱。
- **コンプライアンスは指針であり法ではない。** FTC 開示とクレーム完全性のチェックはリスクを示すが、法的助言ではない。

---

## 品質ガード (CI)

各変更は fail-closed なガード群に対して実行されます（すべて `scripts/` と `tests/` 内）：

| ガード | 何を確認するか |
|-------|--------|
| `validate-skill.sh` | 120 スキル全体の frontmatter、必須セクション、バージョン整合、プラグイン相対リンク。 |
| `golden-auditor-math.py` | **8 つすべて**のフレームワークの決定論的な重み合計 + 解例の算術。 |
| `check-evals.py` | eval 構造 lint + `structure-manifest.json`（120/120 スキルが eval ケースを持つ）。 |
| `check-pii.py` | コミットされたシークレット / PII をブロック（トークン級 allowlist、fail-closed）。 |
| `check-stdlib-only.sh` | 依存増殖ガード + Paid Ads のキー付き API レッドライン。 |
| `check-versions.sh` | バージョン同期ガード：system catalog、plugin/marketplace/OpenClaw の各マニフェスト、ルート + ローカライズ README のバッジ、AGENTS/CLAUDE/VERSIONS、GitHub About、全 120 スキルのバージョンが揃っていることを保証。 |
| `tests/test_connectors_local.py` | 同梱する全 29 コネクタモジュールを対象にしたリクエストビルダー／パーサーのオフラインテスト（CI ではネットワークなし）。 |
| `tests/test_hook_artifact_gate.sh` | フックの Artifact Gate + SessionStart サニタイズの挙動テスト。 |

ライブエンドポイントのドリフトは**手動**の [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) で別途サンプリングします —— スクリプトに列挙されたホスト型コネクタごとに最小限の実呼び出し 1 回 + 形状アサーション（レートリミット応答は SKIP 扱い）；リリース前に実行し、決して CI では実行しません。

---

## コントリビュートとプロジェクトドキュメント

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** —— オーサリングルール、コントリビューションチェックリスト、権威ある 10 の追跡サーフェスのリスト。
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** —— スキルごとのバージョン + changelog（現在のバンドル：`19.1.0`）。
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** —— セキュリティ、プライバシー、コミュニティのポリシー。
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** —— この repo のエージェント向けコンテキスト。

---

## 免責事項

これらのスキルはブランドナラティブ、SEO/GEO、インフルエンサーマーケティング、Paid Ads、メールマーケティング、プロダクト Launch、オーガニックソーシャルのワークフローを支援しますが、順位、AI 引用、トラフィック、エンゲージメント、コンバージョン、ROAS、deliverability、ビジネス成果を**保証しません**。インフルエンサー・広告・メール・ソーシャルのコンプライアンスチェック（FTC 開示、クレーム完全性、プラットフォームポリシー、consent/opt-in、実質的なつながりの開示）は指針であり、法的助言ではありません。重要な戦略・財務・法務上の判断に頼る前に、資格ある専門家に推奨内容を確認してください。

## ライセンス

Apache License 2.0 —— [LICENSE](../LICENSE) を参照。

*英語 README との最終同期：v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
