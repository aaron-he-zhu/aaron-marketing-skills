# SEO & GEO 스킬 라이브러리

**20개 스킬. 15개 명령. 검색 순위 + AI 인용을 한번에.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | **한국어** | [Español](README.es.md) | [Português](README.pt.md)

검색 엔진 최적화(SEO)와 생성형 엔진 최적화(GEO)를 위한 Claude 스킬 및 명령 세트. 의존성 제로. [Claude Code](https://claude.ai/download), [OpenClaw](https://openclaw.com), [Gemini CLI](https://geminicli.com), [Qwen Code](https://qwenlm.github.io/qwen-code-docs/), [Amp](https://ampcode.com), [Kimi](https://moonshotai.github.io/kimi-cli/), [CodeBuddy](https://codebuddy.ai) 네이티브 지원. [35개 이상의 에이전트](https://github.com/vercel-labs/skills#supported-agents)는 `npx skills`로. 콘텐츠 품질은 [CORE-EEAT 벤치마크](https://github.com/aaron-he-zhu/core-eeat-content-benchmark)(80개 항목), 도메인 권위는 [CITE 도메인 등급](https://github.com/aaron-he-zhu/cite-domain-rating)(40개 항목)으로 평가.

> **SEO**는 검색 결과에서 순위를 올립니다. **GEO**는 AI 시스템(ChatGPT, Perplexity, Google AI Overviews)에서 인용됩니다. 이 라이브러리는 둘 다 다룹니다.

용어가 생소하신가요? [GLOSSARY.md](../GLOSSARY.md)를 참조하세요.

### 왜 이 스킬 라이브러리인가

- **120개 항목 품질 프레임워크** — CORE-EEAT(80개) + CITE(40개), 거부권 게이트 포함
- **8개 언어, 750+ 트리거** — 한국어 포함 다국어 지원 (공식, 일상, 오타 변형)
- **의존성 제로** — 순수 Markdown 스킬, Python 불필요, 가상환경 불필요, API 키 불필요
- **도구 무관** — 독립 실행 또는 MCP를 통해 14개 서버(Ahrefs, Semrush, Cloudflare 등) 연동
- **7개 에이전트에서 네이티브 설치** — Claude Code, OpenClaw, Gemini CLI, Qwen Code, Amp, Kimi, CodeBuddy — 그 외 35+ 에이전트는 `npx skills`로

## 빠른 시작

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

# CodeBuddy (앱 내, 2단계)
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
/plugin install aaron-seo-geo

# 범용 폴백 (Cursor, Codex, opencode, Windsurf, Copilot 등 35+ 에이전트)
npx skills add aaron-he-zhu/seo-geo-claude-skills

# 단일 스킬만 설치
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research
```

설치 후 바로 사용:
```
"클라우드 네이티브" 키워드 리서치를 해주세요
```

또는 명령 실행:
```
/seo:audit-page https://example.com
```

## 스킬 목록

### 리서치 — 콘텐츠 제작 전 시장 파악

| 스킬 | 기능 |
|------|------|
| `keyword-research` | 키워드 발견, 의도 분석, 난이도 점수, 토픽 클러스터링 |
| `competitor-analysis` | 경쟁사 SEO/GEO 전략 분석 |
| `serp-analysis` | 검색 결과 및 AI 답변 패턴 분석 |
| `content-gap-analysis` | 경쟁사가 다루지만 내가 놓친 콘텐츠 기회 발견 |

### 빌드 — 검색 및 AI에 최적화된 콘텐츠 생성

| 스킬 | 기능 |
|------|------|
| `seo-content-writer` | 검색 최적화 콘텐츠 작성 |
| `geo-content-optimizer` | AI 시스템에 인용되기 쉬운 콘텐츠로 최적화 |
| `meta-tags-optimizer` | 제목, 설명, OG 태그 최적화 |
| `schema-markup-generator` | JSON-LD 구조화 데이터 생성 |

### 최적화 — 기존 콘텐츠 및 기술 건강도 개선

| 스킬 | 기능 |
|------|------|
| `on-page-seo-auditor` | 점수 보고서 포함 페이지 SEO 감사 |
| `technical-seo-checker` | 크롤링, 인덱싱, Core Web Vitals 점검 |
| `internal-linking-optimizer` | 내부 링크 구조 최적화 |
| `content-refresher` | 오래된 콘텐츠 업데이트로 순위 회복 |

### 모니터링 — 성과 추적 및 문제 조기 발견

| 스킬 | 기능 |
|------|------|
| `rank-tracker` | 검색 및 AI에서 키워드 순위 추적 |
| `backlink-analyzer` | 백링크 분석, 기회 발견, 유해 링크 감지 |
| `performance-reporter` | SEO/GEO 성과 보고서 생성 |
| `alert-manager` | 순위 하락, 트래픽 변화, 기술 문제 알림 |

### 프로토콜 레이어 — 전 단계 품질 관리

| 스킬 | 기능 |
|------|------|
| `content-quality-auditor` | 80개 항목 CORE-EEAT 콘텐츠 품질 감사 |
| `domain-authority-auditor` | 40개 항목 CITE 도메인 권위 감사 |
| `entity-optimizer` | 브랜드/엔티티 지식 그래프 최적화 |
| `memory-management` | 프로젝트 컨텍스트의 세션 간 영구 저장 |

## 명령

| 명령 | 설명 |
|------|------|
| `/seo:audit-page <URL>` | 페이지 SEO + CORE-EEAT 콘텐츠 품질 감사 |
| `/seo:check-technical <URL>` | 기술 SEO 건강 점검 |
| `/seo:generate-schema <type>` | JSON-LD 구조화 데이터 생성 |
| `/seo:optimize-meta <URL>` | 제목, 설명, OG 태그 최적화 |
| `/seo:report <domain> <period>` | SEO/GEO 종합 성과 보고서 |
| `/seo:audit-domain <domain>` | CITE 도메인 권위 감사 |
| `/seo:write-content <topic>` | SEO + GEO 최적화 콘텐츠 작성 |
| `/seo:keyword-research <seed>` | 키워드 리서치 및 분석 |
| `/seo:setup-alert <metric>` | 모니터링 알림 설정 |
| `/seo:geo-drift-check [URL]` | (실험적, v9.0+) 예측 GEO Score와 실제 AI 엔진 인용 동작의 차이 검증 |

### 유지보수 명령 (라이브러리 유지보수자 / 파워 유저용, 일상 사용 시 무시 가능)

| 명령 | 설명 |
|------|------|
| `/seo:wiki-lint` | Wiki 건강 검사: 모순, 고아, 오래된 주장, 누락 페이지 감지 |
| `/seo:contract-lint` | Auditor Runbook 드리프트 감지, handoff 스키마 검사, 전문 용어 누출 스캔 (v7.1.0+) |
| `/seo:p2-review` | v7.1.0 연기 항목의 트리거 조건 평가; tombstone 재검토 (2026-07-10) |
| `/seo:sync-versions` | `.claude-plugin/plugin.json`의 버전을 모든 크로스 에이전트 manifest로 전파 (v9.0+, `scripts/sync-versions.py` 대체) |
| `/seo:validate-library` | 라이브러리 레벨 품질 게이트: 설명 예산, YAML 필드 순서, 언어 커버리지, 중복 트리거 감지 (v9.0+, `scripts/validate-descriptions.py` 대체) |

## 기여

기여를 환영합니다! [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md)를 참조하세요.

## 라이선스

Apache License 2.0

*영문 README 최종 동기화: v9.0.0*
