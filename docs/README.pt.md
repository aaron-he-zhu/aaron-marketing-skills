<div align="center">

# Aaron Marketing Skills

**120 skills de marketing, 7 disciplinas, um contrato — o teu AI marketing staff, instalável como plugin, skills portáteis ou uma equipa de 8 bots.**

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

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **Português** | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

Um **AI marketing staff que instalas, não que prompts** — 120 agent skills que correm como um plugin com comandos e memória, como skills portáteis em 70+ hosts, ou como um **AI Staff de 8 bots** em hosts de bots nomeados (Grok Bot, Hermes Bot Mode). Sete disciplinas e uma camada de protocolo compartilhada, num relance:

| Camada | Skills | Ciclo de vida (diretórios de fase) | Framework → gate | Ponto de entrada |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **E-mail** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **Influenciadores** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor` (SQS); `fit-scorer` pontua Suitability (S) | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **Camada de protocolo** | 8 | — (maquinaria compartilhada, fora dos fluxos de fase) | 7 registros de verdade (entity · creator · offer/claims · consent · launch · channel · narrative) + memória HOT/WARM/COLD | — |

`/aaron-marketing:auto` roteia qualquer objetivo em linguagem natural por todo o sistema. Skills e comandos são **Markdown puro**; pequenos runtimes de Bash/Python-stdlib fornecem hooks, validação, pontuação, eventos de registro, conectores e checagens de CI (sem `pip`, sem etapa de build). **Toda skill funciona no Tier 1 com os dados que você fornece**; os conectores só automatizam a obtenção de dados ou uma mutação explicitamente aprovada.

A topologia tipada autoritativa é [`references/system-catalog.json`](../references/system-catalog.json); veja a [arquitetura do sistema gerada](system-architecture.md) para o mapa legível de quatro camadas, todos os 120 caminhos, os donos dos registros, os sinks de auditor e os perfis de distribuição.

> Os repos antes autônomos, pré-fusão, agora são **repos-placa** apontando para cá — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (a linha final de 20 skills está preservada na tag `v9.9.12`) e [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (a linha IMPACT final na tag `standalone-final`). Política de repos irmãos: [docs/repo-family.md](repo-family.md).

---

## Conteúdo

- [Por que esta biblioteca](#por-que-esta-biblioteca)
- [Instalação](#instalação)
  - [AI Staff](#ai-staff)
- [Primeira execução](#primeira-execução)
- [Arquitetura](#arquitetura)
  - [O contrato de skill compartilhado](#o-contrato-de-skill-compartilhado)
  - [O sistema: um sistema operacional de marketing de quatro camadas](#o-sistema-um-sistema-operacional-de-marketing-de-quatro-camadas)
  - [Sistema de qualidade: oito frameworks, oito gates](#sistema-de-qualidade-oito-frameworks-oito-gates)
  - [A camada de protocolo](#a-camada-de-protocolo)
  - [Memória & hooks de automação](#memória--hooks-de-automação)
- [Catálogo de skills](#catálogo-de-skills)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO — SITE (16)](#seogeo--site-16)
  - [Influenciadores — STAR (16)](#influenciadores--star-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [Camada de protocolo (8)](#camada-de-protocolo-8)
- [Comandos](#comandos)
- [Conectores & níveis de aprimoramento](#conectores--níveis-de-aprimoramento)
- [Workflows recomendados](#workflows-recomendados)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Filosofia de design](#filosofia-de-design)
- [Guardas de qualidade (CI)](#guardas-de-qualidade-ci)
- [Contribuir & documentos do projeto](#contribuir--documentos-do-projeto)
- [Aviso legal](#aviso-legal)
- [Licença](#licença)

---

## Por que esta biblioteca

| Princípio | O que significa na prática |
|-----------|---------------------------|
| **Keyless por padrão** | Cada skill funciona no **Tier 1** com dados que você cola ou extrai de fontes gratuitas/primárias. Ferramentas pagas e servidores MCP são uma conveniência opcional, nunca um pré-requisito. As skills de paid ads pontuam a partir da sua **exportação manual da própria conta** — APIs de anúncios com chave nunca são exigidas. |
| **Content-first, contratos executáveis** | As skills continuam sendo Markdown. Pequenos runtimes de Bash/Python-stdlib tornam pontuação, estado, segurança e conformidade determinísticos sem adicionar dependências de pacotes. |
| **Um contrato compartilhado** | As 120 skills expõem as mesmas sete seções e autodeclaram os metadados `discipline` + `phase`, então a biblioteca se comporta como um único sistema operacional: cada skill conhece suas entradas, saídas e a melhor próxima skill para passar o bastão. |
| **Qualidade com gate** | Oito benchmarks emitem veredictos estruturados e verificáveis. Hooks limitados sinalizam escritas inválidas; pre-commit/CI protegem apenas conteúdo Git commitado contra PII e não validam artefatos runtime. |
| **A verdade vive em eventos** | Sete streams de registro append-only são canônicos; projeções controladas pelo dono expõem o estado de entidades, criadores, claims, consentimentos, launches, canais e narrativa sem filas destrutivas. |
| **Memória entre turnos** | Um modelo de memória HOT/WARM/COLD carrega descobertas, pontuações e pendências entre skills e sessões, higienizados na entrada. |
| **Voz natural** | As skills incluem um detector de jargão de IA e uma lista de frases banidas para que a saída soe como se uma pessoa a tivesse escrito. |

---

## Instalação

Use com o Claude Code, qualquer host compatível com Agent Skills ou um simples `git clone`:

| Host | Instalação |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` e depois `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Clientes Agent Plugins v1 · Portable Lite** | Baixe `aaron-marketing-skills-20.0.0-agent-plugin-v1-lite.tar.gz` da [release v20.0.0](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v20.0.0), extraia-o e instale o diretório de plugin extraído |
| **Grok Bot · Hermes Bot Mode (AI Staff)** | Gera o roster de 8 bots: `python3 scripts/generate-bot-projections.py --output <private-dir>` — 7 especialistas + `aaron-chief`. Ver [AI Staff](#ai-staff) |
| **[SkillHub.cn](https://skillhub.cn) (comunidade chinesa)** | `skillhub install <frontmatter-slug>` (ex.: `keyword-research`) |
| **Qualquer host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

No Claude Code, `marketplace add` apenas registra o catálogo — execute `/plugin install aaron-marketing@aaron` (ou escolha em `/plugin`) para de fato ativar as skills e os comandos. Para puxar uma **única** skill num host genérico: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Navegue pelo bundle no [registro skills.sh](https://skills.sh/aaron-he-zhu/aaron-marketing-skills). Diretórios por agente, peculiaridades do frontmatter e o que degrada fora do plugin: [docs/agent-compatibility.md](agent-compatibility.md) (verificado 120/120 instaláveis, 2026-07).

Instalar o plugin **não** adiciona nada à sua lista `/mcp` — o catálogo MCP vive em [`docs/mcp-catalog.json`](mcp-catalog.json), deliberadamente fora do caminho `.mcp.json` da raiz do plugin que o Claude Code registra automaticamente, então é apenas uma referência para copiar e colar (veja [Conectores](#conectores--níveis-de-aprimoramento)).

A raiz do repositório é a fonte de autoria, **não** a raiz de instalação padrão do Agent Plugins v1. Use o asset de release acima: ele projeta **120/120 Agent Skills estritas** em `skills/<name>/` e não inclui `mcp.json`, comandos, hooks, conectores nem o runtime do repositório. As camadas de compatibilidade existentes continuam disponíveis; consulte o [pacote Portable Lite e seus limites de capacidade](agent-plugins-v1.md).

### AI Staff

Em hosts de bots nomeados (**Grok Bot** da xAI, **Bot Mode** do Hermes Agent) este bundle não se instala como um monte de 120 skills — instala-se como **equipa**: oito colegas com nome a quem falas como a colegas. Sete especialistas possuem cada um um corredor — `aaron-narrative`, `aaron-seo-geo`, `aaron-social`, `aaron-email`, `aaron-ad`, `aaron-influencer`, `aaron-launch` — e o **`aaron-chief`** conduz a secretária: segura os 8 registos de protocolo e encaminha qualquer objetivo cruzado por @mention (visited set, teto de três handoffs). É o mesmo organograma de chefe de staff mais especialistas para o qual estes hosts foram feitos, derivado do mesmo catálogo tipado das outras formas de instalação: as 120 skills, cobertas exatamente uma vez, sem um segundo inventário.

Diz ao `@aaron-chief` «launch v2 on Product Hunt in three weeks» e o plano volta por `@aaron-launch`, `@aaron-email` e `@aaron-social` — cada bot responde só no seu corredor.

```bash
python3 scripts/generate-bot-projections.py --output /private/path/aaron-bot-roster
```

O gerador escreve 8 bundles de perfil Hermes instaláveis (`hermes/<bot>/`, manifests ligados por hash) mais o pack de setup do Grok Bot (`grok/bot-cards.md`, listas de enable, checklist). Os bundles de staff são **Tier-1 estáticos**: sem conectores, MCP, cron ou runtimes; os auditors devolvem `NOT_SCORED` em vez de adivinhar; as escritas de registo e memória ficam propose-only. No Grok Bot, todos os bots de um membro partilham um computador na nuvem — os nomes dos bots não são fronteiras de segurança. Passos de deploy, ressalvas do host e backlog de smoke owner-run: [agent-compatibility.md](agent-compatibility.md#named-bot-roster-deployment-grok-bot--hermes-bot-mode).

---

## Primeira execução

Se seu host suportar roteamento automático de skills, basta descrever o objetivo:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Ou use os comandos slash — `/auto` para o roteamento, ou um ponto de entrada de disciplina:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` infere a intenção e executa o menor workflow útil, parando apenas em decisões bloqueantes. Cada skill funciona com dados colados; as ferramentas opcionais estão documentadas em [CONNECTORS.md](../CONNECTORS.md).

---

## Arquitetura

### O contrato de skill compartilhado

Cada skill segue o **mesmo contrato de ativação** — sete seções em ordem fixa:

1. **Trigger / quando usar** — quando a skill deve disparar.
2. **Quick Start** — prompts para copiar e colar.
3. **Skill Contract** — Saída esperada · Lê · Escreve · Promove · Feito-quando · Próxima skill principal.
4. **Handoff Summary** — o formato padrão de passagem de bastão para que a próxima skill continue de forma limpa.
5. **Data Sources** — marcadores `~~category`, cada um com um caminho keyless de Tier 1.
6. **Instructions** — o método numerado (trata todas as exportações como entrada não confiável).
7. **Next Best Skill** — para onde ir em seguida (com regras de terminação visited-set + profundidade máxima).

Cada skill também autodeclara `metadata.discipline` (narrative / seo-geo / influencer / ad / email / launch / social / protocol) e `metadata.phase`, para que roteamento e clustering funcionem de forma uniforme. O contrato é documentado uma vez em [skill-contract.md](../references/skill-contract.md); o estado compartilhado entre skills vive em [state-model.md](../references/state-model.md).

### O sistema: um sistema operacional de marketing de quatro camadas

Uma voz de marca, expressa por cinco canais always-on, concentrada em momentos de launch, todos lendo e escrevendo num sistema de registro compartilhado. Sete disciplinas, quatro altitudes — um sistema, não uma pilha.

| Camada | Adote | Disciplinas | Cadência |
|-------|-------|-------------|----------|
| **L1 · Estratégia** — o que dizemos / quem somos | crawl | **Narrative** · TALE | always-on |
| **L2 · Canais** — motores always-on que expressam a estratégia (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **E-mail** · SEND · **Paid Ads** · ROAS · **Influenciadores** · STAR | always-on (influenciadores com viés episódico) |
| **L3 · Orquestração** — o momento delimitado no tempo entre canais | run | **Product Launch** · RAMP | episódico |
| **L4 · Protocolo** — o sistema de registro compartilhado | — | 7 registros de verdade + memória de trabalho · 8 gates de auditor · um contrato de skill | — |

A Narrative é a mensagem; os canais são os meios que a expressam — cada builder central registra o ID/versão exatos do cânone e o offset de projeção de claims que usou, ou um fallback/bloqueio explicitamente aprovado. O loop de 4 fases de cada disciplina vive dentro da sua camada (Narrative = Trace → Architect → Land → Evaluate).

As sete usam **diretórios** de fase (`narrative/trace/`…, `seo-geo/survey/`…, `influencer/scout/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…). Nota: «activate» significa contato com criadores em influenciadores mas gating de conta em paid ads — mesma palavra, escopo específico de cada disciplina.

### Sistema de qualidade: oito frameworks, oito gates

Oito benchmarks tornam «bom» mensurável. Cada um define dimensões, um método de agregação e um pequeno conjunto de **itens de veto** (falhas duras que limitam ou bloqueiam uma pontuação independentemente do resto):

| Framework | Pontua | Itens / dimensões | Agregação | Itens de veto |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | Verdade / sistema / eficácia da narrativa de marca | T / A / L / E | Resultados de perfil `truth`, `system` e `effectiveness` separados; sem composto geral | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | Qualidade de conteúdo com vistas diagnósticas CORE/GEO e EEAT/SEO | 80 itens / 8 dimensões | Resultado completo ponderado por perfil; as vistas diagnósticas não são totais separados | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | Autoridade de domínio e confiança de citação | 40 itens / 4 dimensões | Média aritmética ponderada por perfil | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | Influenciadores Suitability / Trust / Appeal / Return | S / T / A / R; 40 itens / 4 dimensões | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | Contribuição incremental e qualidade operacional dos paid ads | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | E-mail: integridade do remetente / engajamento / nutrição / resultado direto | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | Product launch: prontidão / assets / momentum / prova | R / A / M / P; 40 IDs estáveis | Resultados de perfil `preflight`, `execution` e `outcome` separados; nunca tirar média entre horizontes de tempo | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | Organic social: enraizamento / ofício / hosting / observabilidade | E / C / H / O; 40 IDs estáveis | Um perfil `asset-gate` ou `program-maturity-*` por execução; nunca combinar unidades distintas | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

Cada framework é imposto por um **gate de classe auditor** — uma skill cujo artefato tipado (`class: auditor-output`) é validado pelo validador determinístico e por hooks limitados de ciclo de vida. A CI do repositório testa por regressão o validador e o contrato; não inspeciona artefatos ignorados do runtime do host. Os gates são passos de workflow, então cada um vive na sua disciplina e é contado ali:

| Gate | Framework | Vive em | Veredicto |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | Perfis TALE | `narrative/evaluate/` | Resultados truth/system/effectiveness separados; sem composto |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED; rótulos de confiança são apenas explicativos |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED mais uma tradução voltada ao criador |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | Perfil de ciclo de vida RAMP | `launch/mobilize/` | SHIP / FIX / BLOCK / UNDECIDED para uma leitura de ciclo de vida declarada |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | Perfil ECHO de asset/programa | `social/host/` | SHIP / FIX / BLOCK / UNDECIDED para uma unidade/perfil declarados |

**Política de veto compartilhada:** um veto verificado limita a pontuação final a `min(raw, 59)`; dois ou mais vetos verificados produzem `status: DONE` + `verdict: BLOCK` e nenhuma pontuação final. Evidência ausente é `Unknown`, nunca uma falha automática. As regras tipadas vivem em [auditor-runbook.md](../references/auditor-runbook.md).

### A camada de protocolo

O diretório `protocol/` abriga a **maquinaria compartilhada de verdade & memória** que fica fora dos fluxos de fase das disciplinas — 8 skills, contadas à parte:

| Skill | Função | Ancorada a | Stream de eventos canônico / papel runtime |
|-------|-----|-------------|-----------------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | Perfil canônico de marca/entidade (Knowledge Graph, Wikidata, desambiguação por IA) | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | Roster/dossiê canônico de criadores — handles deduplicados, estatísticas de audiência com rótulo de proveniência, tarifas, histórico de compliance | influenciadores | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | Livro de ofertas & comprovação de claims — o registro contra o qual as verificações de claims O1/T2 são julgadas | paid | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | Registro canônico de consentimento/supressão por sujeito — os vetos S2/N1 julgam contra ele | e-mail | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | Dossiê/calendário canônico de launch — tier, etapa de ciclo de vida de mão única, datas/embargo autoritativos, livro de submissão por canal; o SSOT de verdade do launch contra o qual o veto R1 de verdade de etapa julga | launch | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | Registro canônico por canal — handles, propriedade/autorização, normas de plataforma, defaults de disclosure; o SSOT de verdade de canal contra o qual o veto ECHO E1 de verdade de canal julga | social | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | Cânone canônico de narrativa de marca — narrativa estratégica aprovada, sistema de mensagens, linguagem/léxico, proof points; o SSOT do brand-canon contra o qual o veto TALE T1 de verdade julga | narrative | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | Ciclo de vida de memória HOT/WARM/COLD (capturar · promover · rebaixar · arquivar · consultar) | todas as disciplinas | estado runtime não canônico de `memory/` |

Os registros seguem uma **regra de escritor único** (outras skills submetem via `registry-events.py` proposal events), e eles *curam* — os gates *julgam*. A camada genuinamente horizontal sob tudo são os protocolos de `references/` ([auditor-runbook](../references/auditor-runbook.md), [state-model](../references/state-model.md), [skill-contract](../references/skill-contract.md), [humanizer-slop](../references/humanizer-slop.md), [measurement-protocol](../references/measurement-protocol.md)) — compartilhados por design como documentos, não como skills.

### Memória & hooks de automação

**A memória** é escalonada por temperatura, para que o contexto sobreviva entre skills e sessões sem inchar o prompt:

| Nível | Local | Comportamento |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Carregado automaticamente a cada sessão; limitado a **80 linhas E 25 KB** (o que disparar primeiro). |
| **WARM** | `memory/<subdir>/` | Projeções de trabalho reconstruíveis e artefatos de auditoria com permissões; a verdade canônica dos registros vive em `memory/events/*.ndjson`. |
| **COLD** | `memory/archive/` | Registros rebaixados/mais antigos, mantidos para recuperação. |

**Os hooks** (`hooks/hooks.json`, runner `hooks/claude-hook.sh`) conectam sete eventos do Claude Code:

| Evento | Matcher | O que faz |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Injeta o hot-cache **higienizado** + um ponteiro de pendências (as linhas de injeção de prompt são censuradas; caches em symlink são rejeitados). |
| `UserPromptSubmit` | (todos) | Hook de contexto leve por prompt. |
| `PreToolUse` | ferramentas conhecidas com capacidade de escrita | Verifica antes das escritas suportadas em `memory/**` que o alvo exato do projeto host está ignorado pelo Git; caso contrário, a escrita é negada. |
| `PostToolUse` | ferramentas conhecidas com capacidade de escrita | Auditoria de memória pós-estado + validação limitada do Artifact Gate após escritas bem-sucedidas. |
| `PostToolUseFailure` | ferramentas conhecidas com capacidade de escrita | Executa as mesmas checagens após ferramentas com falha, que podem já ter escrito arquivos. |
| `PostToolBatch` | (todos) | Reverifica a memória operacional e o sink de auditoria reservado após cada lote paralelo. |
| `Stop` | (todos) | Realiza uma última varredura limitada; o guard de active-stop então permite o término. Pre-commit/CI protegem apenas conteúdo Git commitado contra PII, não artefatos runtime ignorados. |

O Artifact Gate é **agnóstico ao framework** — o mesmo hook valida artefatos TALE, CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP e ECHO sem código específico por framework.

---

## Catálogo de skills

Os links de skill abrem cada `SKILL.md`. Expanda os **Detalhes** sob cada disciplina para um propósito em uma linha por skill. A ordem do catálogo segue as [quatro camadas](#o-sistema-um-sistema-operacional-de-marketing-de-quatro-camadas) — Narrative (L1 · Estratégia) primeiro, os cinco canais always-on em seguida, Launch (L3 · Orquestração), depois a camada de protocolo.

### Narrative — TALE (16)

Quatro fases sob `narrative/` seguem Trace → Architect → Land → Evaluate. `narrative-quality-auditor` executa separadamente os perfis truth, system e effectiveness; uma revisão completa vincula três resultados e nunca tira a média deles. A Narrative é a estratégia L1 que os builders de canal herdam.

| Fase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>Propósito por skill (Narrative)</b></summary>

| Skill | Alavanca TALE | O que faz |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | Captura a história de marca atual e real como ela vive nas superfícies próprias — o ponto de partida honesto antes de qualquer redesenho. |
| category-narrative-mapper | T | Mapeia as narrativas dominantes da categoria e as alternativas nomeadas para que a marca possa reivindicar uma posição defensável e diferenciada. |
| audience-belief-mapper | T | Revela o que a audiência-alvo já acredita, duvida e valoriza — as crenças que a narrativa precisa mover. |
| positioning-truth-tracer | T | Rastreia cada claim de posicionamento de volta à comprovação, aposentando tudo o que não tem suporte (a montante do veto T1 de verdade). |
| strategic-narrative-designer | A | Projeta a narrativa estratégica central — o arco de história de mudança-no-mundo, as apostas e a resolução com que a marca lidera. |
| message-system-architect | A | Arquiteta o sistema de mensagens — tagline, pilares, proof points e ângulos por audiência como uma estrutura coerente. |
| brand-language-codifier | A | Codifica voz, tom, léxico e linguagem do/não-do para que cada canal soe como uma só marca. |
| story-bank-builder | A | Constrói um banco reutilizável de proof stories, narrativas de clientes e analogias das quais os canais podem beber. |
| narrative-cascade-planner | L | Planeja como a narrativa cascateia em cada canal e momento sem diluição ou desvio. |
| pitch-narrative-builder | L | Molda a narrativa em forma de pitch — espinha do deck, história de demo e enquadramento para investidores/imprensa. |
| narrative-enablement-kit | L | Kit de enablement que permite a cada equipe contar a história de forma consistente — talk track, FAQ e mapa de mensagens. |
| proof-point-packager | L | Empacota proof points em assets prontos para canal e cientes do claims-ledger. |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | Gate TALE tipado; retorna resultados de perfil separados e nunca tira a média deles. Escreve `memory/audits/narrative/`. |
| message-test-designer | E | Projeta testes de mensagem — matriz de variantes, células de audiência e leitura de ressonância para a narrativa estratégica. |
| narrative-resonance-monitor | E | Acompanha como a narrativa está aterrissando entre canais a partir de fontes keyless (dados proxy rotulados). |
| narrative-drift-monitor | E | Vigia o desvio de narrativa — onde os canais se afastaram do cânone aprovado — e sinaliza correções. |

**Reutilizado entre disciplinas** (contado nas suas fases de origem, não duplicado): [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) (logicamente a frente de Trace, fisicamente em `launch/`), [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker` (denominador de ressonância). **Nenhum conector novo** — a ressonância de narrativa reutiliza `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` — veja [tale-benchmark.md](../references/tale-benchmark.md).

</details>

### SEO/GEO — SITE (16)

Quatro diretórios de fase (4 skills cada) mais os dois gates de qualidade da disciplina (marcados ⛩).

| Fase | Skills |
|-------|--------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Propósito por skill (SEO/GEO)</b></summary>

| Skill | O que faz |
|-------|--------------|
| keyword-research | Inicia o trabalho de keywords para uma página/tema/campanha — intenção, demanda e oportunidades ao alcance. |
| competitor-analysis | Analisa a estratégia SEO de um concorrente, compara domínios, revela suas keywords e lacunas. |
| serp-analysis | Lê uma SERP — features, snippets, People Also Ask, padrões de ranking para uma query. |
| content-gap-analysis | Encontra temas ausentes e buracos de cobertura frente aos concorrentes. |
| content-writer | Escreve e atualiza artigos, landing pages e copy de produto otimizados para SEO. |
| geo-content-optimizer | Otimiza conteúdo para motores de IA (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | Tags Title/Meta/OG/Twitter mais dados estruturados JSON-LD / Schema.org. |
| page-play-builder | Jogadas de página guiadas por template — páginas programáticas, plataformas parasita, páginas de comparação, local/GBP. |
| ⛩ content-quality-auditor | Gate de prontidão para publicação CORE-EEAT de 80 itens (SHIP/FIX/BLOCK). |
| technical-seo-checker | Velocidade do site, Core Web Vitals, indexação, rastreabilidade, robots. |
| on-page-seo-checker | Audita a saúde on-page no nível da página — headings, colocação de keywords, imagens, sinais de qualidade. |
| site-structure-optimizer | Links internos, anchor text, páginas órfãs, hierarquia de páginas, taxonomia de URL, clusters hub/spoke. |
| ⛩ domain-authority-auditor | Gate de confiança de domínio CITE de 40 itens (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Rastreia rankings de keywords, mudanças de posição e quedas. |
| performance-monitor | Relatórios multi-métrica de SEO/GEO, dashboards e alertas de limiar. |
| offsite-signal-analyzer | Perfil de backlinks + qualidade de links, mais tráfego de referência de assistentes de IA nos seus próprios GA4/GSC/logs. |

</details>

### Social — ECHO (16)

Quatro fases sob `social/` seguem Explore → Craft → Host → Observe. `social-quality-auditor` seleciona o `asset-gate` ou um perfil de program-maturity; esses construtos nunca são combinados. A disciplina não contém nenhuma automação de postagem, engajamento ou DM.

| Fase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>Propósito por skill (Social)</b></summary>

| Skill | Alavanca ECHO | O que faz |
|-------|-----------|--------------|
| channel-portfolio-planner | E | Escolhe o mix de plataformas e o papel/cadência por canal a partir de onde a audiência realmente está (registra os canais no registro). |
| voice-dossier-builder | E | Voz, tom, persona e léxico do/não-do da marca para uma presença consistente que soe humana. |
| platform-norm-profiler | E | Normas, formatos, sinais de ranking e regras de linha vermelha por plataforma antes de você postar ali. |
| participation-warmup-planner | E | Plano de aquecimento de comunidade não-promocional — onde aparecer e agregar valor antes de vender. |
| social-calendar-builder | C | Calendário editorial — temas, séries, cadência equilibrada à capacidade real (sem over-posting). |
| social-creative-builder | C | Posts nativos de plataforma (hook/corpo/CTA), com message match e cientes do claims-ledger. |
| short-video-scripter | C | Roteiros de vídeo curto — hook, beats, texto na tela, estrutura de retenção. |
| advocacy-program-designer | C | Programa de advocacy de funcionários/comunidade — opt-in, defaults de disclosure, kit de assets compartilháveis. |
| ⛩ social-quality-auditor | asset gate / program maturity | Gate ECHO tipado para uma unidade/perfil; nunca combina construtos de asset e de operação. Escreve `memory/audits/social/`. |
| engagement-inbox-manager | H | Playbook de triagem de respostas/comentários/DMs — tiers de resposta, escalonamento, disciplina de engajamento genuíno (sem engajamento fabricado/iscado). |
| social-selling-planner | H | Motion de social selling de founder/equipe — outreach relationship-first, sem DMs automatizados. |
| crisis-response-planner | H | Tiers de crise pré-redigidos, holding statements, escada de escalonamento e gatilhos de pause-the-queue. |
| social-pulse-monitor | O | Pulso de menções/sentimento/tópicos a partir de fontes keyless, leituras spike-vs-sustain (dados proxy rotulados). |
| share-of-voice-tracker | O | Share-of-voice vs concorrentes nomeados sobre um denominador estável no período. |
| dark-social-attributor | O | Atribui tráfego dark-social/sem link — disciplina de UTM, captura de atribuição autorreportada, parsing de referral. |
| social-measurement-loop | O | Relê uma mudança lançada contra um baseline ao longo de uma janela → Promote / Keep-testing / Rollback. |

**Reutilizado entre disciplinas** (contado nas suas fases de origem, não duplicado): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — veja [echo-benchmark.md](../references/echo-benchmark.md).

</details>

### Email — SEND (16)

Quatro diretórios de fase sob `email/` (4 skills cada) seguem o loop SEND; o gate (⛩ email-quality-auditor) fica em Deliver. Só o gate calcula a EQS ponderada por objetivo — cada outra skill trabalha uma alavanca e passa o bastão. Agnóstico ao caso de uso (ciclo de vida B2C / cold outbound B2B / newsletter-creator); a coluna de peso por objetivo escolhe a ênfase.

| Fase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Propósito por skill (E-mail)</b></summary>

| Skill | Alavanca SEND | O que faz |
|-------|-----------|--------------|
| deliverability-qa | S | Auth SPF/DKIM/DMARC/BIMI de pré-flight, reputação, inbox-placement, conteúdo de spam e higiene de lista (a verificação S1). |
| list-segment-builder | E | Segmentos por comportamento + etapa de ciclo de vida e regras de supressão a partir da sua própria exportação de lista/CRM/GA4. |
| list-growth-designer | S (+N) | Estratégia de crescimento de lista — canais de aquisição, conceitos de lead magnet, uma spec de fluxo de captura opt-in conforme e mecânicas de referral-loop; alimenta a qualidade de consentimento S capturada na aquisição. |
| list-hygiene-monitor | S | *(NOVO)* Saúde de lista contínua — poda de bounces/reclamações, políticas de sunset, re-permission e supressão de segmentos inativos. |
| email-creative-builder | E (+D) | Assunto/preheader/corpo/CTA, com message match à landing page, ciente do claims-ledger. |
| subject-line-lab | E | *(NOVO)* Ideação e scoring de assunto/preheader — comprimento, spam-trigger, equilíbrio curiosidade/clareza, conjuntos de variantes para testar. |
| email-render-builder | E | *(NOVO)* Build/QA de e-mail HTML — compatibilidade de cliente, dark-mode, acessibilidade, alt de texto puro e checklist de render-test. |
| dynamic-content-personalizer | E | *(NOVO)* Blocos de personalização merge-tag/liquid, regras de conteúdo condicional e segurança de valor de fallback. |
| email-sequence-designer | N | Fluxos de ciclo de vida/automação (welcome, cart, post-purchase, win-back) + governança de frequência. |
| newsletter-monetization-planner | D | Assinatura paga, inventário de patrocínio + rate card e economia do referral growth-loop. |
| preference-frequency-manager | N | *(NOVO)* Design de preference center e governança de frequência de envio para cortar fadiga e descadastros. |
| reactivation-specialist | N | *(NOVO)* Fluxos de win-back / reengajamento para assinantes dormentes com regras de decisão sunset-ou-recuperar. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | Gate SEND de classe auditor: pontua EQS, impõe S1/S2/N1/D1, emite SHIP/FIX/BLOCK; carrega um modo **go/no-go pré-envio**. |
| send-experiment-designer | E | Design de A/B / send-time / hold-out com tamanho de amostra + leitura de significância (promote/kill). |
| inbox-placement-monitor | S | *(NOVO)* Rastreamento contínuo de placement inbox-vs-spam via seed lists e sinais de provider, com alertas de deriva de reputação. |
| cold-outbound-sequencer | D | *(NOVO)* Cadências de cold outbound B2B conformes — ramp seguro para deliverability, tokens de personalização e passos de tratamento de respostas. |

**Reutilizado entre disciplinas** (contado nas suas fases de origem, não duplicado): [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md).

</details>

### Paid Ads — ROAS (16)

Quatro diretórios de fase sob `ad/` (4 skills cada) seguem o loop ROAS; o gate (⛩ ad-account-auditor) fica em Activate. Só o gate calcula a RQS ponderada por objetivo — cada outra skill trabalha uma alavanca e passa o bastão.

| Fase | Skills |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Propósito por skill (Paid Ads)</b></summary>

| Skill | Alavanca ROAS | O que faz |
|-------|-----------|--------------|
| campaign-architect | A + estrutura | Estrutura de conta/campanha, fit do tipo de campanha, tipos de correspondência, negativos/exclusões, canibalização paid↔orgânico; carrega um modo recorrente de **search-term-mining**. |
| audience-segment-builder | A | Transforma sua própria exportação de clientes/CRM/GA4 em audiências seed, seeds lookalike, segmentos de exclusão e um mapa de targeting por etapa de funil. |
| search-term-miner | A | *(NOVO)* Minera o relatório de termos de busca por negativos, novos candidatos a keyword e refinamentos de tipo de correspondência. |
| product-feed-optimizer | O | *(NOVO)* Higiene de feed Shopping/PMax — títulos, atributos, GTINs, mapeamento de categorias e correções de reprovação. |
| ad-creative-builder | O | Headlines/descriptions RSA, hooks e uma matriz de ângulos, com message match à página de destino. |
| ad-test-designer | O (+S) | Projeta testes A/B/n & de incrementalidade (hipótese, matriz de variantes, tamanho de amostra/poder) e lê a significância → promote/kill. |
| bid-strategy-planner | S | *(NOVO)* Escolhe e configura a estratégia de lance por objetivo (tCPA/tROAS/max-conversions), define metas e planeja as transições de fase de aprendizado. |
| landing-experience-checker | O | *(NOVO)* QA de página pós-clique para relevância do anúncio, velocidade de carregamento, mobile e política — a verificação de message match anúncio↔página. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Gate ROAS de classe auditor: pontua RQS, impõe R1/R2/O1/O2/A1, emite SHIP/FIX/BLOCK; carrega um modo **go/no-go de launch**. |
| conversion-signal-qa | R | QA de tracking pré-launch (disparo de eventos, higiene de UTM, gate de dedup, alinhamento de janela, flags iOS-ATT) — o pré-requisito R1/R2 (constrói o sinal; o gate o pontua). |
| placement-exclusion-manager | A | *(NOVO)* Listas de exclusão de placement/audiência — bloqueios de brand safety, poda de placements ruins, supressão de gasto desperdiçado. |
| conversion-value-mapper | R | *(NOVO)* Mapeia ações de conversão a valores/pesos e regras de valor para que o tROAS dê lance na margem real, não em contagens brutas. |
| paid-measurement-loop | R (+S) | Relê uma mudança lançada contra um controle ao longo de uma janela → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Dedup permanente de order-ID contra o conjunto de verdade GA4/ecommerce, normalização de janela/moeda, comparação de modelos, incrementalidade. |
| budget-pacing-monitor | S | *(NOVO)* Rastreia o ritmo de gasto frente ao orçamento ao longo do flight, sinaliza sub/superentrega e recomenda correções de pacing. |
| fatigue-frequency-manager | O | *(NOVO)* Vigia sinais de frequência e decaimento do creative, sinaliza anúncios fatigados e agenda refresh/rotação. |

**Reutilizado entre disciplinas** (contado nas suas fases de origem, não duplicado): [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) (gasto + modo bid-pacing/fase de aprendizado), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md) (pós-clique), [roi-calculator](../influencer/report/roi-calculator/SKILL.md) (cálculo de retorno), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md).

</details>

### Influenciadores — STAR (16)

Quatro diretórios de fase (4 skills cada); o gate da disciplina (⛩ creator-content-auditor) fica em Activate.

| Fase | Skills |
|-------|--------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>Propósito por skill (Influenciadores)</b></summary>

| Skill | O que faz |
|-------|--------------|
| audience-mapper | Perfila a audiência-alvo e mapeia sua subcultura / micro-comunidade antes de colaborar com criadores. |
| trend-spotter | Timing e temas de campanha — hashtags, sons, formatos e momentos culturais em tendência. |
| influencer-discovery | Constrói um roster de criadores do zero, expande para uma nova plataforma, faz sourcing de nano/micro em escala. |
| fit-scorer | Pontuação de fit objetiva e ponderada para uma shortlist (pontuada em STAR Suitability (S)). |
| competitor-tracker | Os criadores, campanhas, formatos, alcance/gasto estimados e lacunas de um concorrente. |
| campaign-planner | Planeja uma campanha, um lançamento de produto, um tentpole ou um programa de criadores always-on. |
| brief-generator | Briefs de influenciador padronizados e templates de equipe reutilizáveis. |
| budget-optimizer | Distribui o gasto entre tiers/plataformas, projeta ROI, modela cenários (também serve ao gasto de paid ads + bid-pacing). |
| outreach-manager | Pitch, cadência de follow-up, reengajamento, negociação de tarifas, rastreamento de status. |
| ⛩ creator-content-auditor | Decisão de gate pré-publicação sobre uma submissão de criador (STAR Trust: divulgação FTC STAR-T1, integridade de claims STAR-T2). |
| contract-helper | Redige/revisa acordos com criadores — direitos de uso, exclusividade, cláusulas padrão. |
| content-amplifier | Estende conteúdo orgânico de criadores com gasto pago e reaproveita UGC em paid, web, e-mail e orgânico. |
| landing-optimizer | Landing pages para tráfego de criadores/paid — message match, mobile, A/B (também serve ao pós-clique paid). |
| performance-analyzer | Avalia resultados de criadores, compara criadores, sentimento, conversões (também o scorecard cross-channel paid). |
| roi-calculator | Mede/projeta ROI, defende orçamentos, valoriza criadores/tiers (motor de cálculo de retorno compartilhado, incl. paid). |
| report-generator | Relatórios escritos para stakeholders após um período (também relatórios de paid ads). |

</details>

### Launch — RAMP (16)

Quatro fases sob `launch/` seguem Research → Assemble → Mobilize → Prove. `launch-readiness-auditor` seleciona um perfil `preflight`, `execution` ou `outcome` por execução; resultados de ciclo de vida são vinculados, mas nunca têm a média tirada.

| Fase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>Propósito por skill (Launch)</b></summary>

| Skill | Alavanca RAMP | O que faz |
|-------|-----------|--------------|
| positioning-mapper | R | Canvas de posicionamento estilo Dunford — alternativas concorrentes nomeadas, atributos únicos, temas de valor, segmento beachhead, declaração de onlyness. |
| launch-tier-planner | R | Decisão de tier (Tier 1 flagship / Tier 2 targeted / Tier 3 changelog-level), declaração de tipo de launch, metas de KPI, registro de riscos com critérios de kill. |
| launch-window-planner | R | Comparação de janelas candidatas (conflitos / ventos favoráveis / risco), decisão launch-week vs rolling-release, buffer de review de store, definição de janela de embargo. |
| early-access-designer | R | Escada de etapas waitlist→concept→alpha→beta→GA com critérios de graduação, gating por coorte, loop de feedback, mecânicas de referral (a montante do veto R1 de verdade de etapa). |
| message-house-builder | A | Message house (tagline, one-liner, pilares de valor, proof points) + espinha PR-FAQ working-backwards + angle packs por canal (a montante de A1). |
| launch-asset-packager | A | Manifesto de assets de launch com escopo por tier — spec de press kit, specs de demo/screenshot, FAQ de launch, metadados de store-listing, checklist técnica de go-live. |
| pricing-packaging-planner | A | Pricing & packaging de launch — estrutura de tiers, mapa valor-preço, escada de ofertas de launch, pricing beta com caminho de graduação, termos de garantia. |
| sales-enablement-kit | A | Enablement interno — battle cards, talk track de vendas, tabela de tratamento de objeções, FAQ interna + macros de CS, anúncio interno com disciplina de embargo. |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | Gate RAMP tipado para uma leitura de ciclo de vida; nunca tira média entre horizontes de tempo. Escreve `memory/audits/launch/`. |
| launch-day-conductor | M | Runbook de dia de launch em blocos horários — check de gate de precondições, veredictos de janela de observação após pushes irreversíveis, escada de incidentes P0–P3 + playbooks de rollback. |
| community-launch-runner | M | Pacotes de submissão por plataforma (Product Hunt, Show HN, subreddits, ondas de diretórios, canais regionais/chineses) sob um check de linha vermelha de plataforma. |
| press-media-relations | M | Lista de mídia/analistas em três tiers, timing de pitch com embargo, rascunho de release em estrutura padrão, roteiro de briefing a analistas. |
| launch-monitor | P | Vigilância de janela T-0→T+30 — verificação de instrumentação (a montante de P1), polling de rank/reviews/news, snapshots KPI D0/W1/M1, leituras spike-vs-sustain. |
| launch-feedback-synthesizer | P | Digest de temas de feedback, loop de status open→shipped («you asked, we shipped»), colheita de social proof conforme. |
| launch-retro-analyzer | P | Retro D1/W1/M1 — actual-vs-target por canal, 5-Whys sobre a maior falha, decisões keep/kill/change, snapshot de resultado ao registro. |
| momentum-planner | P | Plano de momentum T+1→T+30 — calendário de momentos de launch, roteamento de tier de anúncio, decisão de legitimidade de relaunch, próximo momento Tier-1. |

**Reutilizado entre disciplinas** (contado nas suas fases de origem, não duplicado): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-registry`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — veja [ramp-benchmark.md](../references/ramp-benchmark.md).

</details>

### Camada de protocolo (8)

A maquinaria compartilhada de verdade & memória — veja [Arquitetura § A camada de protocolo](#a-camada-de-protocolo) para papéis e regras de escritor único.

| Grupo | Skills |
|-------|--------|
| **Protocolo** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>Propósito por skill (Protocolo)</b></summary>

| Skill | O que faz |
|-------|--------------|
| entity-registry | Perfil de entidade canônico para Knowledge Graph, Wikidata, desambiguação por IA. |
| creator-registry | Roster/dossiê canônico de criadores — handles deduplicados, estatísticas de audiência com rótulo de proveniência, tarifas e histórico de compliance. |
| offer-claims-registry | Livro canônico de ofertas & comprovação de claims — o registro contra o qual as verificações de claims O1/T2 são julgadas. |
| consent-registry | Registro canônico de consentimento/supressão por sujeito — timestamp de opt-in + base legal, prova de double opt-in, histórico append-only de descadastro/bounce/reclamação; o registro contra o qual os vetos S2/N1 julgam. |
| launch-registry | Dossiê canônico por launch + calendário de launch — tier, tipo de launch, etapa de ciclo de vida de mão única (draft→…→GA), datas autoritativas + compromissos de embargo, livro de submissão por canal, snapshot de resultado; o SSOT de verdade do launch. |
| channel-registry | Registro canônico por canal — handles, propriedade/autorização, normas de plataforma, defaults de disclosure; o SSOT de verdade de canal contra o qual o veto ECHO E1 de verdade de canal julga. |
| narrative-registry | Cânone canônico de narrativa de marca — narrativa estratégica aprovada, sistema de mensagens, linguagem/léxico, proof points; o SSOT do brand-canon contra o qual o veto TALE T1 de verdade julga. |
| memory-management | Revisar, promover, rebaixar e arquivar a memória de projeto HOT/WARM/COLD. |

</details>

---

## Comandos

Oito comandos: `/aaron-marketing:auto` roteia qualquer objetivo pelas sete disciplinas, e cada disciplina tem exatamente um ponto de entrada explícito. Fonte: [commands/](../commands).

| Comando | Para quê | Estreitamento |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Descreva qualquer objetivo — infere a intenção e executa o menor workflow útil | `--deep` (exaustivo / stress-test) |
| `/aaron-marketing:narrative` | Narrativa de marca (loop TALE): rastrear a história e a categoria atuais, arquitetar a narrativa estratégica e o sistema de mensagens, aterrissá-la entre canais, o gate de qualidade, ressonância & desvio | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO de ponta a ponta (loop SITE): sondar demanda/concorrentes, implementar conteúdo, ajustar qualidade/técnica/on-page, avaliar autoridade/rankings/relatórios/memória | `--phase survey\|implement\|tune\|evaluate` + flags por fase (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | Influenciadores (loop STAR): insight de audiência, scouting & fit, targeting, outreach, amplificação, relatórios de ROI | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | Paid ads (loop ROAS): segmentos, estrutura, creative, design de experimentos, o gate de auditoria, medição | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | E-mail (loop SEND): deliverability/consent, segmentação, creative, fluxos de ciclo de vida, monetização, send-testing, o gate de auditoria | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch (loop RAMP): posicionamento, tier & janela, message house & assets, o gate de readiness, execução do dia de launch, monitoramento & retro | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Social orgânico (loop ECHO): portfólio de canais & voz, calendário & creative, o gate de qualidade, hosting de engajamento/crise, pulso & medição | `--phase explore\|craft\|host\|observe` |

O trabalho diário normalmente começa com `/aaron-marketing:auto`; os outros sete são pontos de entrada de disciplina explícitos, com `--phase` para estreitar a etapa.

---

## Conectores & níveis de aprimoramento

As skills nomeiam ferramentas com marcadores `~~category` (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) em vez de fornecedores específicos, e cada categoria tem um **caminho keyless de Tier 1**. As receitas completas — incluindo o endpoint gratuito/primário de cada categoria — estão em [CONNECTORS.md](../CONNECTORS.md).

### A camada de conectores é um produto em si

**Mais de 100 caminhos de integração documentados** em três camadas projetadas — e cada um merece seu lugar:

| Camada | O que você obtém |
|-------|--------------|
| **28 conectores empacotados sem dependências** | Python biblioteca padrão puro — sem `pip`, sem passo de build. SERP live keyless + scraping renderizado em JS (Firecrawl, Tavily), uma sonda de citação de respostas de IA, extrações de email-auth via DNS-over-HTTPS, séries de atenção da Wikipedia, menções de notícias GDELT, métricas reais de criadores do YouTube, push IndexNow + Baidu, automação de ESP Resend, e um livro de medição diffável por git que transforma qualquer um deles numa série temporal antes/depois. |
| **Mais de 60 APIs oficiais/gratuitas documentadas** | Cada linha liga a **documentação oficial** do fornecedor, carrega uma data de verificação, e cada link é checado por HTTP antes de publicar. Inclui os caminhos que a maioria das listas de ferramentas ignora: GSC URL Inspection, CrUX History (40 semanas de CWV de campo), a Gmail Postmaster Tools API, a Ad Library da Meta, a Data Export API do Microsoft Clarity. |
| **Servidores MCP de fornecedores** | 18 endpoints remotos catalogados (nunca auto-registrados — sua lista `/mcp` fica limpa) mais os servidores oficiais self-hosted para Google Analytics, Search Console, **Google Ads** e **Microsoft Clarity**. Dois MCPs remotos funcionam sem chave alguma (Firecrawl, Tavily). |

O que os torna confiáveis em vez de apenas numerosos:

- **Três classes de segurança, gates projetados** ([SECURITY.md](../SECURITY.md)): os fetchers hospedados executam um **pré-flight local de robots.txt** antes de cada fetch delegado e recusam em Disallow; tudo que muta estado externo (envios de e-mail, pushes de índice) é **dry-run por padrão** atrás de um flag `--live` explícito, com chaves de idempotência onde o fornecedor as suporta e sem auto-retry onde não.
- **Verificado, depois reverificado**: os endpoints são checados contra a documentação primária do fornecedor com datas, os caminhos keyless são testados ao vivo, um guard de CI impõe o sync de versão/tracking, e um smoke ao vivo pré-release detecta a deriva de endpoints (já detectou mudanças reais de API — duas vezes).
- **Fatos, não veredictos**: os conectores reportam presença de registros, tags parseadas e séries brutas; os gates de auditor fazem o julgamento, e as skills rotulam cada número com **Measured / User-provided / Estimated**.
- **Um playbook escrito** ([docs/connector-playbook.md](connector-playbook.md)) governa cada adição — qualificar, verificar, implementar, testar, cablear, documentar, rastrear, regredir, registrar — para que a qualidade se sustente à medida que o catálogo cresce.

| Nível | Requer | O que você obtém |
|------|----------|---------|
| **Tier 1** (padrão) | Nada | Cole dados, ou extraia-os de fontes gratuitas/públicas. O framework de análise completo roda de qualquer forma. |
| **Tier 2** | Uma API ou MCP gratuita primária | Obtenção automática dos seus próprios dados GSC / GA4 / Core Web Vitals. |
| **Tier 3** | Um conjunto MCP mais completo | Workflows multi-fonte totalmente automatizados. |

- **Helpers empacotados sem dependências** sob `scripts/connectors/` (apenas biblioteca padrão do Python) extraem dados públicos/próprios localmente — ex.: PageSpeed/CrUX, Open PageRank, crawl de página, Wayback CDX, Wikidata SPARQL, Common Crawl, receitas advertools — mais **`resend.py`**, automação direta do ESP Resend para as skills de e-mail (chave free-tier: status de auth de domínio, seed-test sends, sync de supressão, agendamento de broadcasts; os subcomandos que mutam são dry-run por padrão e exigem `--live`), e **`firecrawl.py`** + **`tavily.py`**, automação de fetchers hospedados keyless para as skills de research (Firecrawl: SERP web live + markdown de página renderizada em JS + site maps; Tavily: busca com pontuação + sonda de fontes citadas de um motor de respostas de IA para GEO + extração de URL — ambos gratuitos sem chave alguma, ambos com um pré-flight local de robots.txt embutido).
- **Fontes gratuitas/keyless** documentadas por categoria: Google Search Console & GA4 (dados próprios), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, SERP/scrape keyless do Firecrawl, AI-search keyless do Tavily, registros de email-auth via DNS-over-HTTPS (`doh.py`), séries de atenção da Wikipedia (`pageviews.py`), menções de notícias GDELT (`gdelt.py`), métricas de criadores do YouTube com chave gratuita (`youtube.py`), push IndexNow + Baidu (`indexpush.py`, com gate de dry-run), as bibliotecas de ad-transparency (Meta/Google/TikTok), e linhas de receita para crt.sh, o validador W3C, oEmbed e HN Algolia.
- **Servidores MCP opt-in** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, a suíte gratuita self-hosted **OpenSEO**, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, os keyless Firecrawl e Tavily) estão catalogados em [`docs/mcp-catalog.json`](mcp-catalog.json) como **referência apenas para copiar e colar** — o catálogo fica fora do caminho `.mcp.json` da raiz do plugin auto-registrado, então nada é registrado por você. Copie as entradas que quiser para a sua própria config MCP.

As skills de paid ads pontuam a partir da sua **exportação manual da própria conta** (CSV do gerenciador de anúncios nativo, GA4, ecommerce). As APIs de plataforma de anúncios com chave (Google Ads SDK, Meta Marketing API) são opt-in Tier-2/3 apenas e **nunca** um requisito de Tier 1. As skills de e-mail pontuam da mesma forma — a partir da sua **própria exportação de ESP** — e cada sinal de deliverability é keyless (lookups de DNS, um relatório DMARC RUA e um teste de inbox com seed-list), então uma API de ESP com chave também nunca é um requisito de Tier 1; quando o Resend é seu ESP, o `resend.py` empacotado automatiza o mesmo loop no free-tier.

---

## Workflows recomendados

A maioria dos objetivos reais cruza disciplinas. `/aaron-marketing:auto` roteia um objetivo em linguagem natural para a menor cadeia útil entre as sete — um lançamento de produto, por exemplo, aciona Launch, Email, Social e Paid de uma vez:

```text
/aaron-marketing:auto lançar nossa v2 no Product Hunt em 3 semanas — 1.200 na lista de espera; precisamos da página, dos e-mails e do plano do dia do lançamento
```

Ou conduza o loop de uma disciplina de ponta a ponta (o guia `README.md` em cada diretório de disciplina adiciona jogadas por cenário):

**Narrative (loop TALE)**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor` (⛩ portão TALE) → `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO (loop SITE)**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor` (⛩ portão de publicação) → `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; revisão de confiança com `domain-authority-auditor` (⛩)

**Social (loop ECHO)**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor` (⛩ portão ECHO) → `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**Email (loop SEND)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ portão EQS) antes de qualquer envio

**Paid Ads (loop ROAS)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` para a página)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ portão RQS) antes de qualquer orçamento ao vivo
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Influenciadores (loop STAR)**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (STAR Suitability)
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor` (⛩ portão STAR) → `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Launch (loop RAMP)**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor` (⛩ portão RAMP) → `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

Para uma revisão de confiança completa, combine `content-quality-auditor` com `domain-authority-auditor` para uma avaliação combinada de 120 itens. Com `memory-management` ativo, passagens de bastão e pendências persistem automaticamente na memória HOT/WARM/COLD.

---

## Estrutura do repositório

```
narrative/{trace,architect,land,evaluate}/           # Narrative — TALE (16, incl. seu gate)
seo-geo/{survey,implement,tune,evaluate}/            # SEO/GEO (16, incl. seus 2 gates)
influencer/{scout,target,activate,report}/           # Influenciadores (16, incl. seu gate)
ad/{research,orchestrate,activate,scale}/            # Paid Ads — ROAS (16, incl. seu gate)
email/{setup,engage,nurture,deliver}/                # Email — SEND (16, incl. seu gate)
launch/{research,assemble,mobilize,prove}/           # Launch — RAMP (16, incl. seu gate)
social/{explore,craft,host,observe}/                 # Social — ECHO (16, incl. seu gate)
protocol/                                            # Camada de protocolo (8) — registros de verdade + memória
commands/        # 8 comandos slash (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # contrato compartilhado, modelo de estado, os 8 benchmarks, auditor runbook, packs de plataforma
evals/           # casos de eval estruturais por skill + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (a única lógica de runtime)
scripts/         # validate-skill.sh + connectors/ (stdlib) + guards de CI
memory/          # scaffolding HOT/WARM/COLD + armazenamentos de registro (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # READMEs localizados (zh)
.claude-plugin/  # plugin.json + espelho marketplace.json
```

---

## Filosofia de design

- **As skills são conteúdo.** O único código é o validador Bash, o runner de hooks Bash e helpers de conector/verificação da biblioteca padrão do Python sem dependências. Nunca dependências de terceiros / `pip` — imposto por um guard de dependency-creep.
- **Keyless primeiro.** Cada `~~category` tem uma receita gratuita/de dados próprios; MCP e ferramentas pagas são pura conveniência.
- **Cirúrgico & MECE.** Cada skill possui uma tarefa com um limite de escopo nítido; o trabalho que se sobrepõe é entregue como um *modo* de uma skill existente em vez de uma nova skill fina. Os registros curam, os gates julgam, os analisadores alimentam os gates.
- **Sem números inventados.** As skills rotulam cada cifra com Measured / User-provided / Estimated e incluem um detector de jargão de IA / frases banidas.
- **Compliance é orientação, não lei.** As verificações de divulgação FTC e integridade de claims sinalizam risco; não são aconselhamento jurídico.

---

## Guardas de qualidade (CI)

Cada mudança roda contra um conjunto de guards fail-closed (todos em `scripts/` e `tests/`):

| Guard | Verifica |
|-------|--------|
| `validate-skill.sh` | Frontmatter, seções obrigatórias, consistência de versão, links plugin-relativos nas 120 skills. |
| `golden-auditor-math.py` | Soma de pesos determinística + aritmética dos exemplos trabalhados para os **oito** frameworks. |
| `check-evals.py` | Lint estrutural de eval + `structure-manifest.json` (120/120 skills carregam casos de eval). |
| `check-pii.py` | Bloqueia secrets / PII commitados (allowlist em nível de token, fail-closed). |
| `check-stdlib-only.sh` | Guard de dependency-creep + a linha vermelha de API com chave de Paid Ads. |
| `check-versions.sh` | Guard de sincronização de versões: catálogo do sistema, manifests de plugin/marketplace/OpenClaw, badges do README raiz e localizados, AGENTS/CLAUDE/VERSIONS, About do GitHub e as 120 versões de skills permanecem alinhados. |
| `tests/test_connectors_local.py` | Testes offline de construtores de request e parsers cobrindo todos os 29 módulos de conectores incluídos (sem rede no CI). |
| `tests/test_hook_artifact_gate.sh` | Testes de comportamento do Artifact Gate do hook + higienização SessionStart. |

A deriva de endpoints ao vivo é amostrada separadamente pelo **manual** [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) — uma chamada real mínima por conector hospedado listado nesse script, com asserções de forma (respostas de rate-limit contam como SKIP); execute-o antes de um release, nunca no CI.

---

## Contribuir & documentos do projeto

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — regras de authoring, o checklist de contribuição e a lista autoritativa das 10 superfícies de tracking.
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** — versões por skill + changelog (bundle atual: `20.0.0`).
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** — política de segurança, privacidade e comunidade.
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** — contexto voltado ao agente para este repo.

---

## Aviso legal

Estas skills auxiliam workflows de narrativa de marca, SEO/GEO, influencer-marketing, paid-ads, e-mail-marketing, product-launch e social orgânico mas **não** garantem rankings, citações de IA, tráfego, engajamento, conversões, ROAS, deliverability ou resultados de negócio. As verificações de compliance de influenciadores, anúncios, e-mail e social (divulgação FTC, integridade de claims, política de plataforma, consentimento/opt-in, divulgação de conexão material) são orientação, não aconselhamento jurídico. Verifique as recomendações com profissionais qualificados antes de se basear nelas para decisões importantes de estratégia, financeiras ou jurídicas.

## Licença

Apache License 2.0 — veja [LICENSE](../LICENSE).

*Última sincronização com o README em inglês: v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
