<div align="center">

# Aaron Marketing Skills

**120개의 마케팅 스킬 — 브랜드 내러티브, SEO/GEO, 인플루언서, Paid Ads, 이메일, Launch, 소셜 — 을 하나의 계약으로.**

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

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | **한국어** | [Português](README.pt.md) | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

챗 에이전트를 마케팅 오퍼레이터로 바꾸는 Claude 스킬과 슬래시 명령어 라이브러리. 일곱 개의 분야와 하나의 공유 프로토콜 계층을 한눈에:

| 계층 | 스킬 | 라이프사이클(단계 디렉터리) | 프레임워크 → 게이트 | 진입점 |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **이메일** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor`(EQS) | `/aaron-marketing:email` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor`(RQS) | `/aaron-marketing:ad` |
| **인플루언서** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor`(SQS); `fit-scorer`가 Suitability (S) 채점 | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **프로토콜 계층** | 8 | —(단계 흐름 밖의 공유 기계장치) | 7개의 진실 레지스트리(entity · creator · offer/claims · consent · launch · channel · narrative) + HOT/WARM/COLD 메모리 | — |

`/aaron-marketing:auto`는 어떤 자연어 목표든 시스템 전체로 라우팅합니다. 스킬과 명령어는 **순수 Markdown**이며, 작은 Bash/Python 표준 라이브러리 런타임이 훅, 검증, 채점, 레지스트리 이벤트, 커넥터, CI 점검을 제공합니다(`pip` 없음, 빌드 단계 없음). **모든 스킬은 당신이 제공하는 데이터만으로 Tier 1에서 동작합니다**; 커넥터는 데이터 조회 또는 명시적으로 승인된 변경 작업만 자동화합니다.

권위 있는 타입 지정 토폴로지는 [`references/system-catalog.json`](../references/system-catalog.json)입니다. 읽기 좋은 4계층 지도, 전체 120개 경로, 레지스트리 소유자, auditor 싱크, 배포 프로파일은 [생성된 시스템 아키텍처](system-architecture.md)를 참조하세요.

> 병합 전의 독립 리포지토리들은 이제 여기를 가리키는 **이정표 리포지토리** 입니다 — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills)(최종 20개 스킬 라인은 태그 `v9.9.12`에 보존)와 [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills)(최종 IMPACT 라인은 태그 `standalone-final`). 형제 리포지토리 정책: [docs/repo-family.md](repo-family.md).

---

## 목차

- [왜 이 라이브러리인가](#왜-이-라이브러리인가)
- [설치](#설치)
- [첫 실행](#첫-실행)
- [아키텍처](#아키텍처)
  - [공유 스킬 컨트랙트](#공유-스킬-컨트랙트)
  - [시스템: 4계층 마케팅 운영체제](#시스템-4계층-마케팅-운영체제)
  - [품질 시스템: 여덟 프레임워크, 여덟 게이트](#품질-시스템-여덟-프레임워크-여덟-게이트)
  - [프로토콜 계층](#프로토콜-계층)
  - [메모리 & 자동화 훅](#메모리--자동화-훅)
- [스킬 카탈로그](#스킬-카탈로그)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO — SITE (16)](#seogeo--site-16)
  - [인플루언서 — STAR (16)](#인플루언서--star-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [프로토콜 계층 (8)](#프로토콜-계층-8)
- [명령어](#명령어)
- [커넥터 & 향상 티어](#커넥터--향상-티어)
- [권장 워크플로](#권장-워크플로)
- [저장소 구조](#저장소-구조)
- [설계 철학](#설계-철학)
- [품질 가드 (CI)](#품질-가드-ci)
- [기여 & 프로젝트 문서](#기여--프로젝트-문서)
- [면책 조항](#면책-조항)
- [라이선스](#라이선스)

---

## 왜 이 라이브러리인가

| 원칙 | 실무에서의 의미 |
|-----------|---------------------------|
| **기본이 keyless** | 모든 스킬은 붙여넣거나 무료/퍼스트파티 소스에서 가져온 데이터로 **Tier 1** 에서 동작합니다. 유료 도구와 MCP 서버는 선택적 편의일 뿐, 결코 전제 조건이 아닙니다. Paid Ads 스킬은 **자기 계정의 수동 내보내기**로 채점합니다 — 키가 필요한 광고 API는 절대 필요하지 않습니다. |
| **콘텐츠 우선, 실행 가능한 계약** | 스킬은 여전히 Markdown입니다. 작은 Bash/Python 표준 라이브러리 런타임이 패키지 의존성 추가 없이 채점, 상태, 안전, 규약 적합성을 결정론적으로 만듭니다. |
| **하나의 공유 계약** | 120개 스킬 모두가 같은 일곱 섹션을 노출하고 `discipline` + `phase` 메타데이터를 스스로 선언하므로, 라이브러리가 하나의 운영체제처럼 동작합니다: 각 스킬은 자신의 입력, 출력, 그리고 넘겨줄 최선의 다음 스킬을 압니다. |
| **게이트가 있는 품질** | 여덟 개의 벤치마크가 구조화되고 기계 검증 가능한 판정을 냅니다. 제한된 훅이 잘못된 쓰기를 드러내며, pre-commit/CI는 커밋된 Git의 PII만 보호하고 runtime 산출물은 검증하지 않습니다. |
| **진실은 이벤트에 산다** | 추가 전용(append-only) 레지스트리 이벤트 스트림 일곱 개가 정준입니다. 소유자가 통제하는 프로젝션이 파괴적 큐 없이 엔티티, 크리에이터, 클레임, 동의, Launch, 채널, 내러티브 상태를 노출합니다. |
| **턴을 가로지르는 메모리** | HOT/WARM/COLD 메모리 모델이 발견, 점수, 미해결 사항을 스킬과 세션 사이로 나르며 입구에서 정화합니다. |
| **사람다운 목소리** | 스킬은 AI 티 감지기와 금지 문구 목록을 탑재해, 출력이 사람이 쓴 것처럼 읽히도록 합니다. |

---

## 설치

Claude Code, 임의의 Agent Skills 호환 호스트, 또는 단순한 `git clone`과 함께 사용하세요:

| 호스트 | 설치 |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` 후 `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ 호스트](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Agent Plugins v1 클라이언트 · Portable Lite** | [v20.0.0 릴리스](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v20.0.0)에서 `aaron-marketing-skills-20.0.0-agent-plugin-v1-lite.tar.gz`를 내려받아 압축을 풀고 추출된 플러그인 디렉터리를 설치 |
| **[SkillHub.cn](https://skillhub.cn)(중국어 커뮤니티)** | `skillhub install <frontmatter-slug>`(예: `keyword-research`) |
| **임의의 호스트** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

Claude Code에서 `marketplace add`는 카탈로그만 등록합니다 — 스킬과 명령어를 실제로 활성화하려면 `/plugin install aaron-marketing@aaron`을 실행(또는 `/plugin`에서 선택)하세요. 범용 호스트에서 **단일** 스킬을 가져오려면: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. 번들은 [skills.sh 레지스트리](https://skills.sh/aaron-he-zhu/aaron-marketing-skills)에서 둘러볼 수 있습니다. 에이전트별 디렉터리, frontmatter 특이점, 플러그인 밖에서 무엇이 저하되는지: [docs/agent-compatibility.md](agent-compatibility.md)(120/120 설치 가능 검증, 2026-07).

플러그인을 설치해도 `/mcp` 목록에 **아무것도** 추가되지 않습니다 — MCP 카탈로그는 [`docs/mcp-catalog.json`](mcp-catalog.json)에 있으며, Claude Code가 자동 등록하는 플러그인 루트 `.mcp.json` 경로 밖에 의도적으로 두어 복사-붙여넣기 참조일 뿐입니다([커넥터](#커넥터--향상-티어) 참조).

저장소 루트는 작성용 SSOT이며 Agent Plugins v1의 표준 설치 루트가 **아닙니다**. 위 릴리스 자산을 사용하세요. **120/120개의 엄격한 Agent Skills**를 `skills/<name>/`에 투영하며 `mcp.json`, 명령, hooks, 커넥터 또는 저장소 런타임을 포함하지 않습니다. 기존 클라이언트 호환 계층은 유지됩니다. 자세한 내용은 [Portable Lite 패키지 및 기능 경계](agent-plugins-v1.md)를 참조하세요.

---

## 첫 실행

호스트가 자동 스킬 라우팅을 지원하면, 목표를 설명하기만 하면 됩니다:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

또는 슬래시 명령어를 사용하세요 — 라우팅에는 `/auto`, 아니면 분야 진입점을:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto`는 의도를 추론하고 가장 작은 유용한 워크플로를 실행하며, 차단성 결정에서만 멈춥니다. 모든 스킬은 붙여넣은 데이터로 동작합니다; 선택적 도구는 [CONNECTORS.md](../CONNECTORS.md)에 문서화되어 있습니다.

---

## 아키텍처

### 공유 스킬 컨트랙트

모든 스킬은 **동일한 활성화 계약**을 따릅니다 — 고정된 순서의 일곱 섹션:

1. **Trigger / 언제 사용하는가** — 스킬이 언제 발동해야 하는지.
2. **Quick Start** — 복사-붙여넣기 프롬프트.
3. **Skill Contract** — 예상 출력 · 읽기 · 쓰기 · 승격 · 완료 조건 · 주요 다음 스킬.
4. **Handoff Summary** — 다음 스킬이 깔끔하게 이어받도록 하는 표준 인계 형식.
5. **Data Sources** — `~~category` 플레이스홀더, 각각 keyless Tier 1 경로 보유.
6. **Instructions** — 번호가 매겨진 방법(모든 내보내기를 신뢰할 수 없는 입력으로 취급).
7. **Next Best Skill** — 다음으로 어디로(visited-set + 최대 깊이 종료 규칙 포함).

각 스킬은 `metadata.discipline`(narrative / seo-geo / influencer / ad / email / launch / social / protocol)과 `metadata.phase`도 스스로 선언하므로 라우팅과 클러스터링이 일관되게 작동합니다. 계약은 [skill-contract.md](../references/skill-contract.md)에 한 번 문서화되고, 스킬 간 공유 상태는 [state-model.md](../references/state-model.md)에 삽니다.

### 시스템: 4계층 마케팅 운영체제

하나의 브랜드 보이스가 다섯 개의 상시 채널을 통해 표현되고, 출시 순간으로 집약되며, 이 모두가 공유된 기록 시스템을 읽고 씁니다. 일곱 분야, 네 고도 — 더미가 아니라 시스템입니다.

| 계층 | 도입 | 분야 | 케이던스 |
|-------|-------|-------------|---------|
| **L1 · Strategy** — 무엇을 말하는가 / 우리는 누구인가 | crawl | **Narrative** · TALE | 상시 |
| **L2 · Channels** — 전략을 표현하는 상시 엔진(owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · STAR | 상시(인플루언서는 에피소딕 성향) |
| **L3 · Orchestration** — 채널을 가로지르는 시간 한정 순간 | run | **Product Launch** · RAMP | 에피소딕 |
| **L4 · Protocol** — 공유된 기록 시스템 | — | 7개의 진실 레지스트리 + 워킹 메모리 · 8개의 auditor 게이트 · 하나의 스킬 계약 | — |

Narrative는 메시지이고, 채널은 그것을 표현하는 매체입니다 — 각 코어 빌더는 자신이 사용한 정확한 캐논 ID/버전과 클레임 프로젝션 오프셋, 또는 명시적으로 승인된 폴백/차단을 기록합니다. 각 분야의 4단계 루프는 자신의 계층 안에 삽니다(Narrative = Trace → Architect → Land → Evaluate).

일곱 모두 단계 **디렉터리**(`narrative/trace/`…, `seo-geo/survey/`…, `influencer/scout/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…)를 사용합니다. 참고: "activate"는 인플루언서에서는 크리에이터 아웃리치를, Paid Ads에서는 계정 게이팅을 의미합니다 — 같은 단어, 분야별 범위.

### 품질 시스템: 여덟 프레임워크, 여덟 게이트

여덟 벤치마크가 "좋음"을 측정 가능하게 만듭니다. 각각은 차원, 롤업 방법, 그리고 소수의 **거부 항목**(나머지와 무관하게 점수를 상한 처리하거나 차단하는 하드 실패)을 정의합니다:

| 프레임워크 | 채점 대상 | 항목 / 차원 | 롤업 | 거부 항목 |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | 브랜드 내러티브의 진실 / 시스템 / 효과 | T / A / L / E | `truth`, `system`, `effectiveness` 프로파일 결과는 각각 별개; 전체 합성 점수 없음 | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | CORE/GEO 및 EEAT/SEO 진단 뷰를 갖춘 콘텐츠 품질 | 80개 항목 / 8개 차원 | 완전한 프로파일 가중 결과; 진단 뷰는 별도 합계가 아님 | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | 도메인 권위와 인용 신뢰 | 40개 항목 / 4개 차원 | 산술 프로파일 가중 평균 | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | 인플루언서 Suitability / Trust / Appeal / Return | S / T / A / R · 40개 항목 / 4개 차원 | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | Paid Ads의 증분 기여와 운영 품질 | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | 이메일의 발신자 무결성 / 인게이지먼트 / 너처링 / 직접 성과 | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | 제품 출시의 준비도 / 자산 / 모멘텀 / 증명 | R / A / M / P · 40개의 안정 ID | `preflight`, `execution`, `outcome` 프로파일 결과는 각각 별개; 시간 지평을 결코 평균하지 않음 | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | 오가닉 소셜의 임베디드니스 / 크래프트 / 호스팅 / 관측 가능성 | E / C / H / O · 40개의 안정 ID | 실행마다 `asset-gate` 또는 `program-maturity-*` 프로파일 하나만; 서로 다른 단위는 결코 결합하지 않음 | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

각 프레임워크는 **auditor 클래스 게이트**로 강제됩니다 — 타입이 지정된 산출물(`class: auditor-output`)을 결정론적 검증기와 제한된 수명주기 Hook으로 검증합니다. 저장소 CI는 검증기와 계약을 회귀 테스트하지만 무시된 호스트 런타임 산출물은 검사하지 않습니다. 게이트는 워크플로 단계이므로 각자가 자신의 분야에 살며 거기서 계수됩니다:

| 게이트 | 프레임워크 | 위치 | 판정 |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE 프로파일 | `narrative/evaluate/` | truth/system/effectiveness 결과는 각각 별개; 합성 점수 없음 |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED; 신뢰 라벨은 설명용일 뿐 |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED에 더해 크리에이터용 번역 제공 |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP 라이프사이클 프로파일 | `launch/mobilize/` | 선언된 하나의 라이프사이클 읽기에 대한 SHIP / FIX / BLOCK / UNDECIDED |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | ECHO 자산/프로그램 프로파일 | `social/host/` | 선언된 하나의 단위/프로파일에 대한 SHIP / FIX / BLOCK / UNDECIDED |

**공유 거부 정책:** 검증된 거부 항목이 하나면 최종 점수를 `min(raw, 59)`로 상한 처리합니다. 둘 이상이면 `status: DONE` + `verdict: BLOCK`이 되며 최종 점수는 없습니다. 증거 누락은 `Unknown`이며, 결코 자동 실패가 아닙니다. 타입 지정 규칙은 [auditor-runbook.md](../references/auditor-runbook.md)에 있습니다.

### 프로토콜 계층

`protocol/` 디렉터리는 분야 단계 흐름 밖에 앉는 **공유 진실 & 메모리 기계장치**를 담습니다 — 8개 스킬, 별도로 계수됩니다:

| 스킬 | 역할 | 앵커 대상 | 정준 이벤트 스트림 / 런타임 역할 |
|-------|-----|-------------|-----------------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | 정준적 브랜드/엔티티 프로필(Knowledge Graph, Wikidata, AI 중의성 해소) | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | 정준적 크리에이터 명부/도시에 — 중복 제거된 핸들, 출처 라벨이 붙은 오디언스 통계, 요율, 컴플라이언스 이력 | 인플루언서 | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | 오퍼 & 클레임 입증 원장 — O1/T2 클레임 점검이 대조하여 판정되는 기록 | Paid | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | 대상별 정준적 동의/억제 기록 — S2/N1 거부가 이에 비추어 판정 | 이메일 | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | 정준적 Launch 도시에/캘린더 — 티어, 단방향 라이프사이클 단계, 권위 있는 날짜/엠바고, 채널 제출 원장; R1 단계 진실 거부가 대조하는 Launch 진실 SSOT | Launch | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | 채널별 정준적 기록 — 핸들, 소유권/승인, 플랫폼 규범, 공개 기본값; ECHO E1 채널 진실 거부가 대조하는 채널 진실 SSOT | Social | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | 정준적 브랜드 내러티브 캐논 — 승인된 전략 내러티브, 메시지 시스템, 언어/렉시콘, 증거점; TALE T1 진실 거부가 대조하는 브랜드 캐논 SSOT | Narrative | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | HOT/WARM/COLD 메모리 라이프사이클(캡처 · 승격 · 강등 · 아카이브 · 조회) | 모든 분야 | 비정준 `memory/` 런타임 상태 |

레지스트리는 **단독 기록자 규칙**을 따르며(다른 스킬은 `registry-events.py` proposal events를 통해 제출), *큐레이트*합니다 — 판정은 게이트가 합니다. 모든 것 아래에 있는 진정으로 수평적인 계층은 `references/` 프로토콜([auditor-runbook](../references/auditor-runbook.md), [state-model](../references/state-model.md), [skill-contract](../references/skill-contract.md), [humanizer-slop](../references/humanizer-slop.md), [measurement-protocol](../references/measurement-protocol.md))입니다 — 설계상 스킬이 아니라 문서로 공유됩니다.

### 메모리 & 자동화 훅

**메모리**는 온도로 계층화되어, 프롬프트를 부풀리지 않으면서 컨텍스트가 스킬과 세션을 가로질러 살아남습니다:

| 계층 | 위치 | 동작 |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | 세션마다 자동 로드; **80줄 그리고 25 KB**(먼저 걸리는 쪽)로 상한. |
| **WARM** | `memory/<subdir>/` | 재구축 가능한 워킹 프로젝션과 권한이 부여된 감사 산출물; 정준 레지스트리 진실은 `memory/events/*.ndjson`에 삽니다. |
| **COLD** | `memory/archive/` | 강등된/오래된 기록, 회상을 위해 보관. |

**훅**(`hooks/hooks.json`, 러너 `hooks/claude-hook.sh`)은 일곱 개의 Claude Code 이벤트를 배선합니다:

| 이벤트 | 매처 | 하는 일 |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | **정화된** hot-cache + 미해결 사항 포인터를 주입(프롬프트 인젝션 줄은 마스킹; 심링크 캐시는 거부). |
| `UserPromptSubmit` | (전부) | 프롬프트별 경량 컨텍스트 훅. |
| `PreToolUse` | 쓰기 가능한 것으로 알려진 도구 | 지원되는 `memory/**` 쓰기 전에 정확한 호스트 프로젝트 대상이 Git-ignore 되어 있는지 검증합니다. 아니면 쓰기가 거부됩니다. |
| `PostToolUse` | 쓰기 가능한 것으로 알려진 도구 | 쓰기 성공 후 사후 상태 메모리 감사 + 제한된 Artifact Gate 검증을 수행합니다. |
| `PostToolUseFailure` | 쓰기 가능한 것으로 알려진 도구 | 실패한 도구도 이미 파일을 썼을 수 있으므로 같은 점검을 수행합니다. |
| `PostToolBatch` | (전부) | 병렬 도구 배치마다 운영 메모리와 예약된 감사 싱크를 재점검합니다. |
| `Stop` | (전부) | 마지막 제한 스윕을 한 번 수행하며, 이후 active-stop 가드가 종료를 허용합니다. pre-commit/CI는 커밋된 Git 콘텐츠의 PII만 보호하고, 무시된 런타임 산출물은 검증하지 않습니다. |

Artifact Gate는 **프레임워크 비의존적**입니다 — 같은 훅이 TALE, CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP, ECHO 산출물을 프레임워크별 코드 없이 검증합니다.

---

## 스킬 카탈로그

스킬 링크는 각 `SKILL.md`를 엽니다. 각 분야 아래의 **세부사항**을 펼치면 스킬별 한 줄 목적이 보입니다. 카탈로그 순서는 [4계층 스트라타](#시스템-4계층-마케팅-운영체제)를 따릅니다 — Narrative(L1 · Strategy)가 먼저, 다섯 개의 상시 채널이 다음, Launch(L3 · Orchestration), 그리고 프로토콜 계층.

### Narrative — TALE (16)

`narrative/` 아래 4단계는 Trace → Architect → Land → Evaluate를 따릅니다. `narrative-quality-auditor`는 truth, system, effectiveness 프로파일을 따로 실행합니다. 전체 리뷰는 세 결과를 연결할 뿐 결코 평균하지 않습니다. Narrative는 채널 빌더들이 상속하는 L1 전략입니다.

| 단계 | 스킬 |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>스킬별 목적(Narrative)</b></summary>

| 스킬 | TALE 레버 | 하는 일 |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | 현재 실제 브랜드 스토리를 owned 표면 전반에 걸쳐 있는 그대로 포착 — 어떤 재설계보다 앞선 정직한 출발점. |
| category-narrative-mapper | T | 카테고리의 지배적 내러티브와 명명된 대안을 지도화하여 브랜드가 방어 가능하고 차별화된 위치를 주장할 수 있게 함. |
| audience-belief-mapper | T | 타깃 오디언스가 이미 믿고, 의심하고, 신경 쓰는 것을 드러냄 — 내러티브가 움직여야 할 신념. |
| positioning-truth-tracer | T | 모든 포지셔닝 클레임을 입증으로 역추적하고 뒷받침 없는 것을 폐기(T1 진실 거부의 상류). |
| strategic-narrative-designer | A | 핵심 전략 내러티브 설계 — 브랜드가 이끄는 세상-변화 스토리 아크, 이해관계, 해결. |
| message-system-architect | A | 메시지 시스템 설계 — 태그라인, 기둥, 증거점, 오디언스별 앵글을 하나의 일관된 구조로. |
| brand-language-codifier | A | 보이스, 톤, 렉시콘, do/don't 언어를 성문화하여 모든 채널이 하나의 브랜드처럼 들리게 함. |
| story-bank-builder | A | 채널이 끌어 쓸 수 있는 재사용 가능한 증거 스토리, 고객 내러티브, 유추의 뱅크 구축. |
| narrative-cascade-planner | L | 내러티브가 희석이나 표류 없이 각 채널과 순간으로 어떻게 흘러내리는지 계획. |
| pitch-narrative-builder | L | 내러티브를 피치 형태로 다듬기 — 덱 척추, 데모 스토리, 투자자/프레스 프레이밍. |
| narrative-enablement-kit | L | 모든 팀이 스토리를 일관되게 말하게 하는 인에이블먼트 킷 — 토크 트랙, FAQ, 메시지 맵. |
| proof-point-packager | L | 증거점을 채널 준비된, claims-ledger 인지 에셋으로 패키징. |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | 타입 지정 TALE 게이트: 프로파일별 결과를 따로 반환하며 결코 평균하지 않습니다. `memory/audits/narrative/`에 기록합니다. |
| message-test-designer | E | 메시지 테스트 설계 — 변형 매트릭스, 오디언스 셀, 전략 내러티브의 공명 판독. |
| narrative-resonance-monitor | E | keyless 소스에서 내러티브가 채널 전반에 어떻게 안착하는지 추적(프록시 데이터 라벨링). |
| narrative-drift-monitor | E | 내러티브 표류 감시 — 채널이 승인된 캐논에서 벗어난 지점 — 및 교정 표시. |

**분야 간 재사용**(원래 단계에서 계수, 중복 없음): [positioning-mapper](../launch/research/positioning-mapper/SKILL.md)(논리적으로 Trace의 앞단, 물리적으로 `launch/`), [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker`(공명 분모). **새 커넥터 없음** — 내러티브 공명은 `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py`를 재사용 — [tale-benchmark.md](../references/tale-benchmark.md) 참조.

</details>

### SEO/GEO — SITE (16)

네 개의 단계 디렉터리(각 4개 스킬) + 분야의 두 품질 게이트(⛩ 표시).

| 단계 | 스킬 |
|-------|--------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>스킬별 목적(SEO/GEO)</b></summary>

| 스킬 | 하는 일 |
|-------|--------------|
| keyword-research | 페이지/주제/캠페인의 키워드 작업 시작 — 의도, 수요, 코앞의 기회. |
| competitor-analysis | 경쟁사 SEO 전략 분석, 도메인 비교, 그들의 키워드와 격차 발굴. |
| serp-analysis | SERP 해석 — 기능, 스니펫, People Also Ask, 특정 쿼리의 랭킹 패턴. |
| content-gap-analysis | 경쟁사 대비 누락 주제와 커버리지 구멍 발견. |
| content-writer | SEO 최적화된 기사, 랜딩 페이지, 제품 카피 작성 및 리프레시. |
| geo-content-optimizer | AI 엔진(ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot)을 위한 콘텐츠 최적화. |
| serp-markup-builder | Title/Meta/OG/Twitter 태그 + JSON-LD / Schema.org 구조화 데이터. |
| page-play-builder | 템플릿 구동 페이지 플레이 — 프로그래매틱 페이지, 패러사이트 플랫폼, 비교 페이지, local/GBP. |
| ⛩ content-quality-auditor | 80항목 CORE-EEAT 게시 준비 게이트(SHIP/FIX/BLOCK). |
| technical-seo-checker | 사이트 속도, Core Web Vitals, 색인, 크롤 가능성, robots. |
| on-page-seo-checker | 페이지 수준 on-page 건강도 감사 — 헤딩, 키워드 배치, 이미지, 품질 신호. |
| site-structure-optimizer | 내부 링크, 앵커 텍스트, 고아 페이지, 페이지 계층, URL 분류, hub/spoke 클러스터. |
| ⛩ domain-authority-auditor | 40항목 CITE 도메인 신뢰 게이트(TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | 키워드 랭킹, 순위 변동, 하락 추적. |
| performance-monitor | 다중 지표 SEO/GEO 리포트, 대시보드, 임계값 알림. |
| offsite-signal-analyzer | 백링크 프로필 + 링크 품질, 그리고 자신의 GA4/GSC/로그 내 AI 어시스턴트 추천 트래픽. |

</details>

### Social — ECHO (16)

`social/` 아래 4단계는 Explore → Craft → Host → Observe를 따릅니다. `social-quality-auditor`는 `asset-gate` 또는 하나의 program-maturity 프로파일을 선택하며, 두 구성은 결코 결합하지 않습니다. 이 분야는 게시, 인게이지먼트, DM 자동화를 일절 포함하지 않습니다.

| 단계 | 스킬 |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>스킬별 목적(Social)</b></summary>

| 스킬 | ECHO 레버 | 하는 일 |
|-------|-----------|--------------|
| channel-portfolio-planner | E | 오디언스가 실제로 있는 곳으로부터 플랫폼 믹스와 채널별 역할/케이던스 선택(채널을 레지스트리에 기록). |
| voice-dossier-builder | E | 일관되고 사람 같은 존재감을 위한 브랜드 보이스, 톤, 페르소나, do/don't 렉시콘. |
| platform-norm-profiler | E | 게시하기 전 플랫폼별 규범, 포맷, 랭킹 신호, 레드라인 규칙. |
| participation-warmup-planner | E | 비홍보성 커뮤니티 워밍업 계획 — 판매하기 전 어디에 나타나 가치를 더할지. |
| social-calendar-builder | C | 편집 캘린더 — 테마, 시리즈, 실제 용량에 맞춘 케이던스 균형(과다 게시 없음). |
| social-creative-builder | C | 플랫폼 네이티브 게시물(훅/본문/CTA), 메시지 매치, claims-ledger 인지. |
| short-video-scripter | C | 숏폼 비디오 스크립트 — 훅, 비트, 온스크린 텍스트, 리텐션 구조. |
| advocacy-program-designer | C | 직원/커뮤니티 애드보커시 프로그램 — 옵트인, 공개 기본값, 공유 가능 에셋 킷. |
| ⛩ social-quality-auditor | asset gate / program maturity | 하나의 단위/프로파일에 대한 타입 지정 ECHO 게이트: 자산과 운영 구성을 결코 섞지 않습니다. `memory/audits/social/`에 기록합니다. |
| engagement-inbox-manager | H | 회신/댓글/DM 트리아지 playbook — 응답 티어, 에스컬레이션, 진정성 있는 인게이지먼트 규율(조작/유인된 인게이지먼트 없음). |
| social-selling-planner | H | 파운더/팀 소셜 셀링 모션 — 관계 우선 아웃리치, 자동 DM 없음. |
| crisis-response-planner | H | 사전 초안된 위기 티어, 보류 성명, 에스컬레이션 사다리, 큐 일시정지 트리거. |
| social-pulse-monitor | O | keyless 소스에서 언급/센티먼트/토픽 펄스, spike-vs-sustain 판독(프록시 데이터 라벨링). |
| share-of-voice-tracker | O | 기간 안정 분모에 대한 명명된 경쟁사 대비 share-of-voice. |
| dark-social-attributor | O | 다크소셜/링크 없는 트래픽 어트리뷰션 — UTM 규율, 자기보고 어트리뷰션 포착, 리퍼럴 파싱. |
| social-measurement-loop | O | 출시된 변경을 윈도에 걸쳐 베이스라인과 대비해 다시 읽음 → Promote / Keep-testing / Rollback. |

**분야 간 재사용**(원래 단계에서 계수, 중복 없음): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — [echo-benchmark.md](../references/echo-benchmark.md) 참조.

</details>

### Email — SEND (16)

`email/` 아래 네 개의 단계 디렉터리(각 4개 스킬)가 SEND 루프를 따릅니다; 게이트(⛩ email-quality-auditor)는 Deliver에 위치. 오직 게이트만 목표 가중 EQS를 계산합니다 — 다른 모든 스킬은 하나의 레버를 다루고 인계합니다. 유스케이스 비의존(B2C 라이프사이클 / B2B 콜드 아웃바운드 / newsletter-creator); 목표 가중 열이 강조점을 선택합니다.

| 단계 | 스킬 |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>스킬별 목적(이메일)</b></summary>

| 스킬 | SEND 레버 | 하는 일 |
|-------|-----------|--------------|
| deliverability-qa | S | 발송 전 SPF/DKIM/DMARC/BIMI 인증, 평판, inbox-placement, 스팸 콘텐츠, 리스트 위생(S1 점검). |
| list-segment-builder | E | 자신의 리스트/CRM/GA4 내보내기에서 행동 + 라이프사이클 단계 세그먼트와 억제 규칙. |
| list-growth-designer | S (+N) | 리스트 성장 전략 — 획득 채널, 리드 마그넷 콘셉트, 준수하는 옵트인 캡처 플로 spec, 리퍼럴 루프 메커니즘; 획득 시 포착되는 S 동의 품질에 기여. |
| list-hygiene-monitor | S | *(신규)* 지속적 리스트 건강도 — 바운스/불만 가지치기, 선셋 정책, 재허가, 비활성 세그먼트 억제. |
| email-creative-builder | E (+D) | 제목/프리헤더/본문/CTA, 랜딩 페이지와 메시지 매치, claims-ledger 인지. |
| subject-line-lab | E | *(신규)* 제목/프리헤더 발상과 스코어링 — 길이, 스팸 트리거, 호기심/명확성 균형, 테스트용 변형 세트. |
| email-render-builder | E | *(신규)* HTML 이메일 빌드/QA — 클라이언트 호환, 다크 모드, 접근성, 평문 대체, 렌더 테스트 체크리스트. |
| dynamic-content-personalizer | E | *(신규)* 머지태그/liquid 개인화 블록, 조건부 콘텐츠 규칙, 폴백 값 안전성. |
| email-sequence-designer | N | 라이프사이클/자동화 플로(welcome, cart, post-purchase, win-back) + 빈도 거버넌스. |
| newsletter-monetization-planner | D | 유료 구독, 스폰서십 인벤토리 + 레이트 카드, 리퍼럴 성장 루프 경제학. |
| preference-frequency-manager | N | *(신규)* 프리퍼런스 센터 설계와 발송 빈도 거버넌스로 피로와 수신 거부 감축. |
| reactivation-specialist | N | *(신규)* 휴면 구독자용 win-back / 재참여 플로, 선셋-또는-회복 결정 규칙 포함. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | auditor 클래스 SEND 게이트: EQS 채점, S1/S2/N1/D1 강제, SHIP/FIX/BLOCK 출력; **발송 전 go/no-go** 모드 내장. |
| send-experiment-designer | E | A/B / 발송 시간 / 홀드아웃 설계, 표본 크기 + 유의성 판독(promote/kill). |
| inbox-placement-monitor | S | *(신규)* 시드 리스트와 프로바이더 신호를 통한 inbox-vs-spam 지속 추적, 평판 표류 알림 포함. |
| cold-outbound-sequencer | D | *(신규)* 준수하는 B2B 콜드 아웃바운드 케이던스 — deliverability 안전 램프, 개인화 토큰, 회신 처리 단계. |

**분야 간 재사용**(원래 단계에서 계수, 중복 없음): [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md).

</details>

### Paid Ads — ROAS (16)

`ad/` 아래 네 개의 단계 디렉터리(각 4개 스킬)가 ROAS 루프를 따릅니다; 게이트(⛩ ad-account-auditor)는 Activate에 위치. 오직 게이트만 목표 가중 RQS를 계산합니다 — 다른 모든 스킬은 하나의 레버를 다루고 인계합니다.

| 단계 | 스킬 |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>스킬별 목적(Paid Ads)</b></summary>

| 스킬 | ROAS 레버 | 하는 일 |
|-------|-----------|--------------|
| campaign-architect | A + 구조 | 계정/캠페인 구조, 캠페인 유형 적합, 매치 유형, 부정어/제외, Paid↔오가닉 잠식; 반복적인 **search-term-mining** 모드 내장. |
| audience-segment-builder | A | 자신의 고객/CRM/GA4 내보내기를 시드 오디언스, 유사 시드, 제외 세그먼트, 퍼널 단계 타기팅 맵으로 변환. |
| search-term-miner | A | *(신규)* 검색어 리포트에서 부정어, 새 키워드 후보, 매치 유형 정제를 채굴. |
| product-feed-optimizer | O | *(신규)* Shopping/PMax 피드 위생 — 제목, 속성, GTIN, 카테고리 매핑, 비승인 수정. |
| ad-creative-builder | O | RSA 헤드라인/설명, 훅, 앵글 매트릭스, 도착 페이지와 메시지 매치. |
| ad-test-designer | O (+S) | A/B/n & 증분 테스트 설계(가설, 변형 매트릭스, 표본 크기/검정력)하고 유의성 판독 → promote/kill. |
| bid-strategy-planner | S | *(신규)* 목표별(tCPA/tROAS/max-conversions) 입찰 전략 선택·구성, 목표 시드, 학습 단계 전환 계획. |
| landing-experience-checker | O | *(신규)* 클릭 후 페이지 QA — 광고 관련성, 로드 속도, 모바일, 정책 — 광고↔페이지 메시지 매치 점검. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | auditor 클래스 ROAS 게이트: RQS 채점, R1/R2/O1/O2/A1 강제, SHIP/FIX/BLOCK 출력; **Launch go/no-go** 모드 내장. |
| conversion-signal-qa | R | 출시 전 추적 QA(이벤트 발화, UTM 위생, 중복 제거 게이트, 윈도 정렬, iOS-ATT 플래그) — R1/R2 전제(신호를 구축; 게이트가 채점). |
| placement-exclusion-manager | A | *(신규)* 지면/오디언스 제외 목록 — 브랜드 안전 차단, 정크 지면 가지치기, 낭비 지출 억제. |
| conversion-value-mapper | R | *(신규)* 전환 액션을 값/가중치와 값 규칙에 매핑하여 tROAS가 원시 카운트가 아닌 실제 마진에 입찰하도록. |
| paid-measurement-loop | R (+S) | 출시된 변경을 윈도에 걸쳐 대조군과 대비해 다시 읽음 → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | GA4/ecommerce 진실 세트에 대한 상시 order-ID 중복 제거, 윈도/통화 정규화, 모델 비교, 증분. |
| budget-pacing-monitor | S | *(신규)* 플라이트 전반의 예산 대비 지출 속도 추적, 과소/과다 전달 표시, 페이싱 교정 권고. |
| fatigue-frequency-manager | O | *(신규)* 프리퀀시와 크리에이티브 감쇠 신호 감시, 피로한 광고 표시, 리프레시/로테이션 예약. |

**분야 간 재사용**(원래 단계에서 계수, 중복 없음): [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md)(지출 + bid-pacing/학습 단계 모드), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md)(클릭 후), [roi-calculator](../influencer/report/roi-calculator/SKILL.md)(리턴 계산), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md).

</details>

### 인플루언서 — STAR (16)

네 개의 단계 디렉터리(각 4개 스킬); 분야의 게이트(⛩ creator-content-auditor)는 Activate에 위치.

| 단계 | 스킬 |
|-------|--------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>스킬별 목적(인플루언서)</b></summary>

| 스킬 | 하는 일 |
|-------|--------------|
| audience-mapper | 크리에이터와 협업하기 전 타깃 오디언스를 프로파일링하고 그 서브컬처 / 마이크로 커뮤니티를 지도화. |
| trend-spotter | 캠페인 타이밍과 테마 — 트렌드 해시태그, 사운드, 포맷, 문화적 순간. |
| influencer-discovery | 크리에이터 명부를 처음부터 구축, 새 플랫폼으로 확장, nano/micro를 대규모로 소싱. |
| fit-scorer | 쇼트리스트에 대한 객관적 가중 적합도 점수(STAR Suitability (S)로 채점). |
| competitor-tracker | 경쟁사의 크리에이터, 캠페인, 포맷, 추정 도달/지출, 격차. |
| campaign-planner | 캠페인, 제품 출시, 텐트폴, 상시 크리에이터 프로그램 기획. |
| brief-generator | 표준화된 인플루언서 브리프와 재사용 가능한 팀 템플릿. |
| budget-optimizer | 티어/플랫폼에 지출 배분, ROI 예측, 시나리오 모델링(Paid Ads 지출 + bid-pacing에도 기여). |
| outreach-manager | 피치, 팔로업 케이던스, 재참여, 요율 협상, 상태 추적. |
| ⛩ creator-content-auditor | 크리에이터 제출물에 대한 게시 전 게이트 결정(STAR Trust: FTC 공개 STAR-T1, 클레임 무결성 STAR-T2). |
| contract-helper | 크리에이터 계약 초안/검토 — 사용권, 독점, 표준 조항. |
| content-amplifier | 오가닉 크리에이터 콘텐츠를 유료 지출로 증폭하고 UGC를 Paid, 웹, 이메일, 오가닉에 재활용. |
| landing-optimizer | 크리에이터/Paid 트래픽용 랜딩 페이지 — 메시지 매치, 모바일, A/B(Paid 클릭 후에도 기여). |
| performance-analyzer | 크리에이터 결과 평가, 크리에이터 비교, 센티먼트, 전환(Paid 크로스채널 스코어카드도). |
| roi-calculator | ROI 측정/예측, 예산 방어, 크리에이터/티어 가치 평가(공유 리턴 계산 엔진, Paid 포함). |
| report-generator | 기간 후 이해관계자용 서면 리포트(Paid Ads 리포트도). |

</details>

### Launch — RAMP (16)

`launch/` 아래 4단계는 Research → Assemble → Mobilize → Prove를 따릅니다. `launch-readiness-auditor`는 실행마다 `preflight`, `execution`, `outcome` 중 하나의 프로파일만 선택합니다. 라이프사이클 결과는 연결될 뿐 결코 평균되지 않습니다.

| 단계 | 스킬 |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>스킬별 목적(Launch)</b></summary>

| 스킬 | RAMP 레버 | 하는 일 |
|-------|-----------|--------------|
| positioning-mapper | R | Dunford 스타일 포지셔닝 캔버스 — 명명된 경쟁 대안, 고유 속성, 가치 테마, beachhead 세그먼트, onlyness 선언. |
| launch-tier-planner | R | 티어 결정(Tier 1 플래그십 / Tier 2 타깃 / Tier 3 changelog 수준), 출시 유형 선언, KPI 목표, kill 기준이 있는 리스크 레지스터. |
| launch-window-planner | R | 후보 윈도 비교(충돌 / 순풍 / 리스크), launch-week vs rolling-release 결정, 스토어 심사 버퍼, 엠바고 윈도 정의. |
| early-access-designer | R | waitlist→concept→alpha→beta→GA 단계 사다리, 졸업 기준, 코호트 게이팅, 피드백 루프, 리퍼럴 메커니즘(R1 단계 진실 거부의 상류). |
| message-house-builder | A | 메시지 하우스(태그라인, 원라이너, 가치 기둥, 증거점) + working-backwards PR-FAQ 척추 + 채널별 앵글 팩(A1의 상류). |
| launch-asset-packager | A | 티어 범위의 출시 에셋 매니페스트 — 프레스 킷 spec, 데모/스크린샷 spec, 출시 FAQ, 스토어 리스팅 메타데이터, 기술적 go-live 체크리스트. |
| pricing-packaging-planner | A | 출시 가격 & 패키징 — 티어 구조, 가치-가격 맵, 출시 오퍼 사다리, 졸업 경로가 있는 베타 가격, 보증 조건. |
| sales-enablement-kit | A | 내부 인에이블먼트 — 배틀 카드, 세일즈 토크 트랙, 이의 처리 표, 내부 FAQ + CS 매크로, 엠바고를 준수한 내부 공지. |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | 하나의 라이프사이클 읽기에 대한 타입 지정 RAMP 게이트: 시간 지평을 결코 평균하지 않습니다. `memory/audits/launch/`에 기록합니다. |
| launch-day-conductor | M | 시간 블록화된 출시 당일 런북 — 전제조건 게이트 점검, 되돌릴 수 없는 푸시 후 관찰 윈도 판정, P0–P3 인시던트 사다리 + 롤백 playbook. |
| community-launch-runner | M | 플랫폼별 제출 패키지(Product Hunt, Show HN, subreddit, 디렉터리 웨이브, 지역/중국어 채널)를 플랫폼 레드라인 점검 아래에서. |
| press-media-relations | M | 3티어 미디어/애널리스트 리스트, 엠바고 피치 타이밍, 표준 구조의 보도자료 초안, 애널리스트 브리핑 개요. |
| launch-monitor | P | T-0→T+30 윈도 감시 — 계측 검증(P1의 상류), rank/리뷰/뉴스 폴링, D0/W1/M1 KPI 스냅샷, spike-vs-sustain 판독. |
| launch-feedback-synthesizer | P | 피드백 테마 다이제스트, open→shipped 상태 루프("you asked, we shipped"), 준수하는 소셜 프루프 수확. |
| launch-retro-analyzer | P | D1/W1/M1 레트로 — 채널별 actual-vs-target, 최대 미스에 대한 5-Whys, keep/kill/change 결정, 레지스트리로의 결과 스냅샷. |
| momentum-planner | P | T+1→T+30 모멘텀 계획 — 출시 순간 캘린더, 공지 티어 라우팅, relaunch 정당성 결정, 다음 Tier-1 순간. |

**분야 간 재사용**(원래 단계에서 계수, 중복 없음): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-registry`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — [ramp-benchmark.md](../references/ramp-benchmark.md) 참조.

</details>

### 프로토콜 계층 (8)

공유 진실 & 메모리 기계장치 — 역할과 단독 기록자 규칙은 [아키텍처 § 프로토콜 계층](#프로토콜-계층)을 참조.

| 그룹 | 스킬 |
|-------|--------|
| **프로토콜** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>스킬별 목적(프로토콜)</b></summary>

| 스킬 | 하는 일 |
|-------|--------------|
| entity-registry | Knowledge Graph, Wikidata, AI 중의성 해소를 위한 정준적 엔티티 프로필. |
| creator-registry | 정준적 크리에이터 명부/도시에 — 중복 제거된 핸들, 출처 라벨이 붙은 오디언스 통계, 요율, 컴플라이언스 이력. |
| offer-claims-registry | 정준적 오퍼 & 클레임 입증 원장 — O1/T2 클레임 점검이 대조하여 판정되는 기록. |
| consent-registry | 대상별 정준적 동의/억제 기록 — 옵트인 타임스탬프 + 법적 근거, 더블 옵트인 증빙, 추가 전용 수신거부/바운스/불만 이력; S2/N1 거부가 대조하는 기록. |
| launch-registry | 출시별 정준적 도시에 + 출시 캘린더 — 티어, 출시 유형, 단방향 라이프사이클 단계(draft→…→GA), 권위 있는 날짜 + 엠바고 약속, 채널 제출 원장, 결과 스냅샷; Launch 진실 SSOT. |
| channel-registry | 채널별 정준적 기록 — 핸들, 소유권/승인, 플랫폼 규범, 공개 기본값; ECHO E1 채널 진실 거부가 대조하는 채널 진실 SSOT. |
| narrative-registry | 정준적 브랜드 내러티브 캐논 — 승인된 전략 내러티브, 메시지 시스템, 언어/렉시콘, 증거점; TALE T1 진실 거부가 대조하는 브랜드 캐논 SSOT. |
| memory-management | HOT/WARM/COLD 프로젝트 메모리의 검토, 승격, 강등, 아카이브. |

</details>

---

## 명령어

여덟 명령어: `/aaron-marketing:auto`가 임의의 목표를 일곱 분야로 라우팅하고, 각 분야는 정확히 하나의 명시적 진입점을 가집니다. 소스: [commands/](../commands).

| 명령어 | 용도 | 좁히기 |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | 임의의 목표를 설명 — 의도를 추론하고 가장 작은 유용한 워크플로 실행 | `--deep`(전수 / 스트레스 테스트) |
| `/aaron-marketing:narrative` | 브랜드 내러티브(TALE 루프): 현재 스토리 & 카테고리 추적, 전략 내러티브 & 메시지 시스템 설계, 채널 전반에 안착, 품질 게이트, 공명 & 표류 | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO 엔드투엔드(SITE 루프): 수요/경쟁사 서베이, 콘텐츠 구현, 품질/기술/온페이지 튜닝, 권위/랭킹/리포트/메모리 평가 | `--phase survey\|implement\|tune\|evaluate` + 단계별 플래그(`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | 인플루언서(STAR 루프): 오디언스 인사이트, 스카우팅 & 적합, 타기팅, 아웃리치, 증폭, ROI 리포팅 | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | Paid ads(ROAS 루프): 세그먼트, 구조, 크리에이티브, 실험 설계, 감사 게이트, 측정 | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | 이메일(SEND 루프): deliverability/consent, 세그먼테이션, 크리에이티브, 라이프사이클 플로, 수익화, 발송 테스트, 감사 게이트 | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch(RAMP 루프): 포지셔닝, 티어 & 윈도, 메시지 하우스 & 에셋, readiness 게이트, 출시 당일 진행, 모니터링 & 레트로 | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | 오가닉 소셜(ECHO 루프): 채널 포트폴리오 & 보이스, 캘린더 & 크리에이티브, 품질 게이트, 인게이지먼트/위기 호스팅, 펄스 & 측정 | `--phase explore\|craft\|host\|observe` |

일상 작업은 보통 `/aaron-marketing:auto`로 시작합니다; 나머지 일곱은 명시적 분야 진입점이며, `--phase`로 단계를 좁힙니다.

---

## 커넥터 & 향상 티어

스킬은 특정 벤더가 아니라 `~~category` 플레이스홀더(`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform` 등)로 도구를 명명하며, 각 카테고리에는 **keyless Tier 1 경로**가 있습니다. 전체 레시피 — 각 카테고리의 무료/퍼스트파티 엔드포인트 포함 — 는 [CONNECTORS.md](../CONNECTORS.md)에 있습니다.

### 커넥터 계층은 그 자체로 하나의 제품

**100개 이상의 문서화된 통합 경로**가 세 개의 설계된 계층에 — 그리고 그 하나하나가 제 자리를 얻습니다:

| 계층 | 얻는 것 |
|-------|--------------|
| **28개의 번들 의존성 없는 커넥터** | 순수 Python 표준 라이브러리 — `pip` 없음, 빌드 단계 없음. keyless 라이브 SERP + JS 렌더 스크래핑(Firecrawl, Tavily), AI 답변 인용 프로브, DNS-over-HTTPS 이메일 인증 가져오기, Wikipedia 주목도 시계열, GDELT 뉴스 언급, 실제 YouTube 크리에이터 지표, IndexNow + Baidu 색인 푸시, Resend ESP 자동화, 그리고 이들 중 무엇이든 전후 비교 시계열로 바꾸는 git 디프 가능한 측정 원장. |
| **60개 이상의 문서화된 공식/무료 API** | 각 행이 벤더의 **공식 문서**를 링크하고, 검증 날짜를 담으며, 각 링크는 출시 전 HTTP 확인됩니다. 대부분의 도구 목록이 놓치는 경로를 포함: GSC URL Inspection, CrUX History(40주간 필드 CWV), Gmail Postmaster Tools API, Meta의 Ad Library, Microsoft Clarity의 Data Export API. |
| **벤더 MCP 서버** | 18개 원격 엔드포인트를 카탈로그화(절대 자동 등록되지 않음 — 당신의 `/mcp` 목록은 깨끗하게 유지)하고, Google Analytics, Search Console, **Google Ads**, **Microsoft Clarity**의 공식 셀프호스트 서버 추가. 두 개의 원격 MCP는 키 없이 동작합니다(Firecrawl, Tavily). |

단지 수가 많은 게 아니라 신뢰할 수 있게 만드는 이유:

- **세 개의 안전 클래스, 설계된 게이트**([SECURITY.md](../SECURITY.md)): 호스트형 페처는 각 위임 가져오기 전에 **로컬로 robots.txt를 사전 점검**하고 Disallow에서 거부합니다; 외부 상태를 바꾸는 것(이메일 발송, 색인 푸시)은 모두 명시적 `--live` 플래그 뒤의 **기본 dry-run** 이며, 벤더가 지원하면 멱등 키를 사용하고 아니면 자동 재시도하지 않습니다.
- **검증, 그리고 재검증**: 엔드포인트는 날짜와 함께 벤더 1차 문서에 대조되고, keyless 경로는 라이브로 테스트되며, CI 가드가 버전/추적 동기화를 강제하고, 릴리스 전 라이브 스모크가 엔드포인트 표류를 잡습니다(이미 실제 API 변경을 잡음 — 두 번).
- **판정이 아니라 사실**: 커넥터는 레코드 존재, 파싱된 태그, 원시 시계열을 보고합니다; 판정은 auditor 게이트가 하고, 스킬은 각 숫자에 **Measured / User-provided / Estimated** 를 붙입니다.
- **성문화된 playbook**([docs/connector-playbook.md](connector-playbook.md))이 각 추가를 통치합니다 — 적격화, 검증, 구현, 테스트, 배선, 문서화, 추적, 회귀, 기록 — 카탈로그가 커져도 품질이 무너지지 않도록.

| 티어 | 필요 | 얻는 것 |
|------|----------|---------|
| **Tier 1**(기본) | 없음 | 데이터를 붙여넣거나 무료/공개 소스에서 가져옴. 전체 분석 프레임워크는 어느 쪽이든 실행됩니다. |
| **Tier 2** | 하나의 무료 퍼스트파티 API 또는 MCP | 자신의 GSC / GA4 / Core Web Vitals 데이터 자동 가져오기. |
| **Tier 3** | 더 완전한 MCP 세트 | 완전 자동화된 멀티소스 워크플로. |

- **번들 의존성 없는 헬퍼**는 `scripts/connectors/` 아래(Python 표준 라이브러리만)에서 공개/자체 데이터를 로컬로 가져옵니다 — 예: PageSpeed/CrUX, Open PageRank, 페이지 크롤, Wayback CDX, Wikidata SPARQL, Common Crawl, advertools 레시피 — 그리고 **`resend.py`**(이메일 스킬용 Resend ESP 직결 자동화: 무료 티어 키로 도메인 인증 상태, seed-test 발송, 억제 동기화, 브로드캐스트 예약; 변경 서브커맨드는 기본 dry-run이며 `--live` 필요), 그리고 **`firecrawl.py`** + **`tavily.py`**(research 스킬용 keyless 호스트형 페처 자동화: Firecrawl은 라이브 웹 SERP + JS 렌더 페이지 markdown + 사이트맵; Tavily는 점수 검색 + GEO용 AI 답변 엔진 인용 소스 프로브 + URL 추출 — 둘 다 키 없이 무료, 둘 다 로컬 robots.txt 사전 점검 내장).
- **무료/keyless 소스**를 카테고리별로 문서화: Google Search Console & GA4(자체 데이터), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, Firecrawl keyless SERP/스크래프, Tavily keyless AI 검색, DNS-over-HTTPS 이메일 인증 레코드(`doh.py`), Wikipedia 주목도 시계열(`pageviews.py`), GDELT 뉴스 언급(`gdelt.py`), 무료 키의 YouTube 크리에이터 지표(`youtube.py`), IndexNow + Baidu 색인 푸시(`indexpush.py`, dry-run 게이트), 광고 투명성 라이브러리(Meta/Google/TikTok), 그리고 crt.sh, W3C 검증기, oEmbed, HN Algolia의 레시피 행.
- **옵트인 MCP 서버**(Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, 셀프호스트 무료 **OpenSEO** 스위트, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, keyless Firecrawl과 Tavily)는 [`docs/mcp-catalog.json`](mcp-catalog.json)에 **복사-붙여넣기 참조로만** 카탈로그화되어 있습니다 — 카탈로그는 자동 등록되는 플러그인 루트 `.mcp.json` 경로 밖에 있어 당신을 위해 아무것도 등록되지 않습니다. 원하는 항목을 자신의 MCP 설정에 복사하세요.

Paid Ads 스킬은 **자기 계정의 수동 내보내기**(네이티브 광고 관리자 CSV, GA4, ecommerce)로 채점합니다. 키가 필요한 광고 플랫폼 API(Google Ads SDK, Meta Marketing API)는 옵트인 Tier-2/3 전용이며 **결코** Tier 1 요건이 아닙니다. 이메일 스킬도 같은 방식 — **자신의 ESP 내보내기**로 채점 — 이며 각 deliverability 신호는 keyless(DNS 조회, DMARC RUA 리포트, seed-list inbox 테스트)이므로 키가 필요한 ESP API도 결코 Tier 1 요건이 아닙니다; 당신의 ESP가 Resend라면 번들 `resend.py`가 무료 티어에서 같은 루프를 자동화합니다.

---

## 권장 워크플로

실제 목표는 대부분 여러 분야에 걸쳐 있습니다. `/aaron-marketing:auto`는 자연어 목표를 7개 분야의 최소 스킬 체인으로 라우팅합니다 — 예컨대 제품 론칭은 Launch·Email·Social·Paid를 동시에 가동합니다:

```text
/aaron-marketing:auto 3주 뒤 Product Hunt에서 v2 론칭 — 대기자 1,200명; 랜딩 페이지, 이메일, 론칭 당일 플랜 필요
```

하나의 분야 루프를 끝까지 돌릴 수도 있습니다(각 분야 디렉터리의 `README.md` 가이드가 시나리오 단위 플레이를 제공합니다):

**Narrative (TALE 루프)**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor` (⛩ TALE 게이트) → `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO (SITE 루프)**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor` (⛩ 게시 게이트) → `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; 신뢰 리뷰는 `domain-authority-auditor`(⛩)

**Social (ECHO 루프)**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor` (⛩ ECHO 게이트) → `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**Email (SEND 루프)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ EQS 게이트) — 발송 전

**Paid Ads (ROAS 루프)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (페이지는 `landing-optimizer`)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ RQS 게이트) — 예산 집행 전
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**인플루언서 (STAR 루프)**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (STAR Suitability)
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor` (⛩ STAR 게이트) → `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Launch (RAMP 루프)**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor` (⛩ RAMP 게이트) → `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

완전한 신뢰 검토를 위해 `content-quality-auditor`를 `domain-authority-auditor`와 짝지어 합계 120항목 평가를. `memory-management`가 활성이면 인계와 미해결 사항이 HOT/WARM/COLD 메모리에 자동으로 지속됩니다.

---

## 저장소 구조

```
narrative/{trace,architect,land,evaluate}/           # Narrative — TALE (16, 게이트 포함)
seo-geo/{survey,implement,tune,evaluate}/            # SEO/GEO (16, 두 게이트 포함)
influencer/{scout,target,activate,report}/           # 인플루언서 (16, 게이트 포함)
ad/{research,orchestrate,activate,scale}/            # Paid Ads — ROAS (16, 게이트 포함)
email/{setup,engage,nurture,deliver}/                # Email — SEND (16, 게이트 포함)
launch/{research,assemble,mobilize,prove}/           # Launch — RAMP (16, 게이트 포함)
social/{explore,craft,host,observe}/                 # Social — ECHO (16, 게이트 포함)
protocol/                                            # 프로토콜 계층 (8) — 진실 레지스트리 + 메모리
commands/        # 8개 슬래시 명령어 (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # 공유 계약, 상태 모델, 8개 벤치마크, auditor runbook, 플랫폼 팩
evals/           # 스킬별 구조 eval 케이스 + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (유일한 런타임 로직)
scripts/         # validate-skill.sh + connectors/ (stdlib) + CI 가드
memory/          # HOT/WARM/COLD 스캐폴딩 + 레지스트리 저장소 (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # 현지화된 README (de, es, fr, it, ja, ko, pt, zh, zh-Hant)
.claude-plugin/  # plugin.json + marketplace.json 미러
```

---

## 설계 철학

- **콘텐츠 우선.** 스킬은 Markdown입니다. 의존성 없는 Bash/Python 표준 라이브러리 런타임이 커넥터, 채점, 레지스트리 이벤트, 검증, 점검을 제공합니다. 서드파티 / `pip` 의존성은 CI가 금지합니다.
- **keyless 우선.** 각 `~~category`에는 무료/자체 데이터 레시피가 있음; MCP와 유료 도구는 순수한 편의.
- **외과적 & MECE.** 각 스킬은 경계가 명확한 하나의 직무를 소유; 겹치는 작업은 얇은 새 스킬이 아니라 기존 스킬의 *모드*로 출하. 레지스트리는 큐레이트, 게이트는 판정, 분석기는 게이트에 공급.
- **숫자를 지어내지 않음.** 스킬은 각 수치에 Measured / User-provided / Estimated를 붙이고 AI 티 / 금지 문구 감지기를 탑재.
- **컴플라이언스는 지침이지 법이 아님.** FTC 공개와 클레임 무결성 점검은 위험을 표시하지만 법적 조언이 아님.

---

## 품질 가드 (CI)

각 변경은 fail-closed 가드 세트에 대해 실행됩니다(모두 `scripts/`와 `tests/` 내):

| 가드 | 점검 |
|-------|--------|
| `validate-skill.sh` | 120개 스킬 전체의 frontmatter, 필수 섹션, 버전 일관성, 플러그인 상대 링크. |
| `golden-auditor-math.py` | **여덟 모두** 프레임워크의 결정론적 가중 합 + 풀이 예제 산술. |
| `check-evals.py` | eval 구조 lint + `structure-manifest.json`(120/120 스킬이 eval 케이스 보유). |
| `check-pii.py` | 커밋된 시크릿 / PII 차단(토큰 수준 allowlist, fail-closed). |
| `check-stdlib-only.sh` | 의존성 증식 가드 + Paid Ads 키 API 레드라인. |
| `check-versions.sh` | 버전 동기화 가드: system catalog, plugin/marketplace/OpenClaw 매니페스트, 루트 + 현지화 README 배지, AGENTS/CLAUDE/VERSIONS, GitHub About, 그리고 120개 스킬 버전이 모두 정렬 상태를 유지합니다. |
| `tests/test_connectors_local.py` | 번들된 29개 커넥터 모듈 전체의 요청 빌더/파서 오프라인 테스트(CI에서 네트워크 없음). |
| `tests/test_hook_artifact_gate.sh` | 훅의 Artifact Gate + SessionStart 정화의 동작 테스트. |

라이브 엔드포인트 표류는 **수동** [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh)로 별도 표본 점검합니다 — 스크립트에 나열된 호스트형 커넥터마다 최소 실호출 1회 + 형태 어서션(레이트 리밋 응답은 SKIP 처리); 릴리스 전에 실행하고 결코 CI에서는 실행하지 않습니다.

---

## 기여 & 프로젝트 문서

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — 오서링 규칙, 기여 체크리스트, 권위 있는 10개 추적 표면 목록.
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** — 스킬별 버전 + changelog(현재 번들: `20.0.0`).
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** — 보안, 프라이버시, 커뮤니티 정책.
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** — 이 repo의 에이전트용 컨텍스트.

---

## 면책 조항

이 스킬들은 브랜드 내러티브, SEO/GEO, 인플루언서 마케팅, Paid Ads, 이메일 마케팅, 프로덕트 Launch, 오가닉 소셜 워크플로를 지원하지만 랭킹, AI 인용, 트래픽, 인게이지먼트, 전환, ROAS, deliverability, 비즈니스 성과를 **보장하지 않습니다**. 인플루언서·광고·이메일·소셜 컴플라이언스 점검(FTC 공개, 클레임 무결성, 플랫폼 정책, consent/opt-in, material-connection 공개)은 지침이지 법적 조언이 아닙니다. 중요한 전략·재무·법률 결정에 의존하기 전에 자격 있는 전문가에게 권장 사항을 확인하세요.

## 라이선스

Apache License 2.0 — [LICENSE](../LICENSE) 참조.

*영어 README와 마지막 동기화: v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
