# SEO & GEO スキルライブラリ

**20スキル。15コマンド。検索ランキング + AI引用を同時に。**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | **日本語** | [한국어](README.ko.md) | [Español](README.es.md) | [Português](README.pt.md)

検索エンジン最適化（SEO）と生成エンジン最適化（GEO）のためのClaudeスキル＆コマンド集。依存関係ゼロ。[Claude Code](https://claude.ai/download)、[OpenClaw](https://openclaw.com)、[Gemini CLI](https://geminicli.com)、[Qwen Code](https://qwenlm.github.io/qwen-code-docs/)、[Amp](https://ampcode.com)、[Kimi](https://moonshotai.github.io/kimi-cli/)、[CodeBuddy](https://codebuddy.ai)にネイティブ対応。[35以上のエージェント](https://github.com/vercel-labs/skills#supported-agents)は `npx skills` 経由。コンテンツ品質は[CORE-EEATベンチマーク](https://github.com/aaron-he-zhu/core-eeat-content-benchmark)（80項目）、ドメイン権威は[CITEドメイン評価](https://github.com/aaron-he-zhu/cite-domain-rating)（40項目）で評価。

> **SEO**は検索結果でのランキングを獲得します。**GEO**はAIシステム（ChatGPT、Perplexity、Google AI Overviews）からの引用を獲得します。このライブラリは両方をカバーします。

用語に慣れていませんか？ [GLOSSARY.md](../GLOSSARY.md) をご覧ください。

### なぜこのスキルライブラリか

- **120項目の品質フレームワーク** — CORE-EEAT（80項目）+ CITE（40項目）、拒否権ゲート付き
- **8言語、750以上のトリガー** — 日本語を含む多言語対応（フォーマル、カジュアル、タイプミス変形）
- **依存関係ゼロ** — 純粋なMarkdownスキル、Python不要、仮想環境不要、APIキー不要
- **ツール非依存** — 単独動作、またはMCP経由で14サーバー（Ahrefs、Semrush、Cloudflareなど）と連携
- **7エージェントでネイティブインストール** — Claude Code、OpenClaw、Gemini CLI、Qwen Code、Amp、Kimi、CodeBuddy — その他 35+ エージェントは `npx skills` 経由

## クイックスタート

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

# CodeBuddy（アプリ内、2ステップ）
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
/plugin install aaron-seo-geo

# 汎用フォールバック（Cursor、Codex、opencode、Windsurf、Copilotなど35+エージェント）
npx skills add aaron-he-zhu/seo-geo-claude-skills

# 単一スキルのみ
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research
```

インストール後すぐに使えます：
```
「クラウドネイティブ」のキーワードリサーチをしてください
```

またはコマンドを実行：
```
/seo:audit-page https://example.com
```

## スキル一覧

### リサーチ — コンテンツ作成前に市場を理解する

| スキル | 機能 |
|--------|------|
| `keyword-research` | キーワード発見、意図分析、難易度スコアリング、トピッククラスタリング |
| `competitor-analysis` | 競合のSEO/GEO戦略分析 |
| `serp-analysis` | 検索結果とAI回答パターンの分析 |
| `content-gap-analysis` | 競合がカバーしているが自社にないコンテンツ機会の発見 |

### ビルド — 検索とAI向けに最適化されたコンテンツを作成

| スキル | 機能 |
|--------|------|
| `seo-content-writer` | 検索最適化コンテンツの執筆 |
| `geo-content-optimizer` | AIシステムに引用されやすいコンテンツに最適化 |
| `meta-tags-optimizer` | タイトル、ディスクリプション、OGタグの最適化 |
| `schema-markup-generator` | JSON-LD構造化データの生成 |

### 最適化 — 既存コンテンツと技術的健全性の改善

| スキル | 機能 |
|--------|------|
| `on-page-seo-auditor` | スコア付きページSEO監査 |
| `technical-seo-checker` | クロール性、インデックス、Core Web Vitalsチェック |
| `internal-linking-optimizer` | 内部リンク構造の最適化 |
| `content-refresher` | 古いコンテンツの更新によるランキング回復 |

### モニタリング — パフォーマンス追跡と問題の早期発見

| スキル | 機能 |
|--------|------|
| `rank-tracker` | 検索とAIでのキーワード順位追跡 |
| `backlink-analyzer` | 被リンク分析、機会発見、有害リンク検出 |
| `performance-reporter` | SEO/GEOパフォーマンスレポート生成 |
| `alert-manager` | ランキング低下、トラフィック変化、技術的問題のアラート |

### プロトコル層 — 全フェーズ横断の品質管理

| スキル | 機能 |
|--------|------|
| `content-quality-auditor` | 80項目CORE-EEATコンテンツ品質監査 |
| `domain-authority-auditor` | 40項目CITEドメイン権威監査 |
| `entity-optimizer` | ブランド/エンティティのナレッジグラフ最適化 |
| `memory-management` | プロジェクトコンテキストのセッション間永続化 |

## コマンド

| コマンド | 説明 |
|----------|------|
| `/seo:audit-page <URL>` | ページSEO + CORE-EEATコンテンツ品質監査 |
| `/seo:check-technical <URL>` | 技術SEOヘルスチェック |
| `/seo:generate-schema <type>` | JSON-LD構造化データ生成 |
| `/seo:optimize-meta <URL>` | タイトル、ディスクリプション、OGタグ最適化 |
| `/seo:report <domain> <period>` | SEO/GEO総合パフォーマンスレポート |
| `/seo:audit-domain <domain>` | CITEドメイン権威監査 |
| `/seo:write-content <topic>` | SEO + GEO最適化コンテンツ執筆 |
| `/seo:keyword-research <seed>` | キーワードリサーチ＆分析 |
| `/seo:setup-alert <metric>` | モニタリングアラート設定 |
| `/seo:geo-drift-check [URL]` | (実験的、v9.0+) 予測GEOスコアと実際のAIエンジン引用動作の差異を検証 |

### メンテナンスコマンド(ライブラリメンテナー / パワーユーザー向け、日常利用では無視可)

| コマンド | 説明 |
|----------|------|
| `/seo:wiki-lint` | Wikiヘルスチェック:矛盾、孤立、古い主張、欠落ページの検出 |
| `/seo:contract-lint` | Auditor Runbookドリフト検出、handoffスキーマ検証、専門用語リーク走査 (v7.1.0+) |
| `/seo:p2-review` | v7.1.0延期項目のトリガー条件評価;tombstone 再審 (2026-07-10) |
| `/seo:sync-versions` | `.claude-plugin/plugin.json` のバージョン番号を全クロスエージェント manifest に伝播 (v9.0+、`scripts/sync-versions.py` の代替) |
| `/seo:validate-library` | ライブラリレベルの品質ゲート:ディスクリプション予算、YAMLフィールド順序、言語カバレッジ、重複トリガー検出 (v9.0+、`scripts/validate-descriptions.py` の代替) |

## コントリビューション

コントリビューションを歓迎します！[CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md)をご覧ください。

## ライセンス

Apache License 2.0

*英語READMEとの最終同期：v9.0.0*
