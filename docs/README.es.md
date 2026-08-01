<div align="center">

# Aaron Marketing Skills

**120 skills de marketing — brand narrative, SEO/GEO, influencers, paid ads, email, launch, social — sobre un único contrato.**

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

[English](../README.md) | [Deutsch](README.de.md) | **Español** | [Français](README.fr.md) | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

Una biblioteca de skills de Claude y comandos slash que convierte a un agente de chat en un operador de marketing. Siete disciplinas y una capa de protocolo compartida, de un vistazo:

| Capa | Skills | Ciclo de vida (directorios de fase) | Framework → gate | Punto de entrada |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **Email** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **Influencers** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor` (SQS); `fit-scorer` puntúa Suitability (S) | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **Capa de protocolo** | 8 | — (maquinaria compartida, fuera de los flujos de fase) | 7 registros de verdad (entity · creator · offer/claims · consent · launch · channel · narrative) + memoria HOT/WARM/COLD | — |

`/aaron-marketing:auto` enruta cualquier objetivo en lenguaje natural a través de todo el sistema. Las skills y los comandos son **Markdown puro**; pequeños runtimes de Bash/Python-stdlib aportan hooks, validación, puntuación, eventos de registro, conectores y checks de CI (sin `pip`, sin paso de build). **Cada skill funciona en Tier 1 con los datos que tú aportas**; los conectores solo automatizan la obtención de datos o una mutación aprobada explícitamente.

La topología tipada autoritativa es [`references/system-catalog.json`](../references/system-catalog.json); consulta la [arquitectura del sistema generada](system-architecture.md) para el mapa legible de cuatro capas, las 120 rutas, los propietarios de registros, los sumideros de auditor y los perfiles de distribución.

> Los repos independientes previos a la fusión son ahora **repos indicadores** que apuntan aquí — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (la línea final de 20 skills se conserva en el tag `v9.9.12`) e [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (la línea IMPACT final en el tag `standalone-final`). Política de repos hermanos: [docs/repo-family.md](repo-family.md).

---

## Contenido

- [Por qué esta biblioteca](#por-qué-esta-biblioteca)
- [Instalación](#instalación)
- [Primera ejecución](#primera-ejecución)
- [Arquitectura](#arquitectura)
  - [El contrato de skill compartido](#el-contrato-de-skill-compartido)
  - [El sistema: un sistema operativo de marketing de cuatro capas](#el-sistema-un-sistema-operativo-de-marketing-de-cuatro-capas)
  - [Sistema de calidad: ocho frameworks, ocho gates](#sistema-de-calidad-ocho-frameworks-ocho-gates)
  - [La capa de protocolo](#la-capa-de-protocolo)
  - [Memoria y hooks de automatización](#memoria-y-hooks-de-automatización)
- [Catálogo de skills](#catálogo-de-skills)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO — SITE (16)](#seogeo--site-16)
  - [Influencers — STAR (16)](#influencers--star-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [Capa de protocolo (8)](#capa-de-protocolo-8)
- [Comandos](#comandos)
- [Conectores y niveles de mejora](#conectores-y-niveles-de-mejora)
- [Flujos de trabajo recomendados](#flujos-de-trabajo-recomendados)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Filosofía de diseño](#filosofía-de-diseño)
- [Guardas de calidad (CI)](#guardas-de-calidad-ci)
- [Contribuir y documentación del proyecto](#contribuir-y-documentación-del-proyecto)
- [Aviso legal](#aviso-legal)
- [Licencia](#licencia)

---

## Por qué esta biblioteca

| Principio | Qué significa en la práctica |
|-----------|---------------------------|
| **Keyless por defecto** | Cada skill funciona en **Tier 1** con datos que pegas o extraes de fuentes gratuitas/de primera parte. Las herramientas de pago y los servidores MCP son una comodidad opcional, nunca un requisito previo. Las skills de paid ads puntúan a partir de tu **exportación manual de tu propia cuenta** — nunca se requieren APIs de anuncios con clave. |
| **Content-first, contratos ejecutables** | Las skills siguen siendo Markdown. Pequeños runtimes de Bash/Python-stdlib hacen deterministas la puntuación, el estado, la seguridad y la conformidad sin añadir dependencias de paquetes. |
| **Un contrato compartido** | Las 120 skills exponen las mismas siete secciones y declaran por sí mismas los metadatos `discipline` + `phase`, de modo que la biblioteca se comporta como un único sistema operativo: cada skill conoce sus entradas, salidas y la siguiente mejor skill a la que hacer el traspaso. |
| **Calidad con gates** | Ocho benchmarks emiten veredictos estructurados y verificables. Los hooks acotados detectan escrituras inválidas; pre-commit/CI solo protegen contenido Git comprometido frente a PII y no validan artefactos runtime. |
| **La verdad vive en eventos** | Siete streams de registro de solo anexado (append-only) son canónicos; proyecciones controladas por su propietario exponen el estado de entidades, creadores, claims, consentimientos, launches, canales y narrativa sin colas destructivas. |
| **Memoria entre turnos** | Un modelo de memoria HOT/WARM/COLD traslada hallazgos, puntuaciones y cabos sueltos entre skills y sesiones, saneados a la entrada. |
| **Voz natural** | Las skills incluyen un detector de jerga de IA y una lista de frases prohibidas para que la salida se lea como si la hubiera escrito una persona. |

---

## Instalación

Úsalo con Claude Code, cualquier host compatible con Agent Skills o un simple `git clone`:

| Host | Instalación |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` y luego `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [más de 70 hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **[SkillHub.cn](https://skillhub.cn) (comunidad china)** | `skillhub install <frontmatter-slug>` (p. ej. `keyword-research`) |
| **Cualquier host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

En Claude Code, `marketplace add` solo registra el catálogo — ejecuta `/plugin install aaron-marketing@aaron` (o elígelo en `/plugin`) para activar realmente las skills y los comandos. Para obtener una **única** skill en un host genérico: `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Explora el bundle en el [registro skills.sh](https://skills.sh/aaron-he-zhu/aaron-marketing-skills). Directorios por agente, peculiaridades del frontmatter y qué se degrada fuera del plugin: [docs/agent-compatibility.md](agent-compatibility.md) (verificado 120/120 instalables, 2026-07).

Instalar el plugin **no** añade nada a tu lista `/mcp` — el catálogo MCP vive en [`docs/mcp-catalog.json`](mcp-catalog.json), deliberadamente fuera de la ruta `.mcp.json` de la raíz del plugin que Claude Code registra automáticamente, así que es solo una referencia para copiar y pegar (véase [Conectores](#conectores-y-niveles-de-mejora)).

---

## Primera ejecución

Si tu host admite el enrutamiento automático de skills, solo describe el objetivo:

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

O usa los comandos slash — `/auto` para el enrutamiento, o un punto de entrada de disciplina:

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` infiere la intención y ejecuta el flujo de trabajo mínimo útil, deteniéndose solo en decisiones bloqueantes. Cada skill funciona con datos pegados; las herramientas opcionales están documentadas en [CONNECTORS.md](../CONNECTORS.md).

---

## Arquitectura

### El contrato de skill compartido

Cada skill sigue el **mismo contrato de activación** — siete secciones en un orden fijo:

1. **Trigger / cuándo usar** — cuándo debe dispararse la skill.
2. **Quick Start** — prompts para copiar y pegar.
3. **Skill Contract** — Salida esperada · Lee · Escribe · Promueve · Hecho-cuando · Skill siguiente principal.
4. **Handoff Summary** — la forma estándar de traspaso para que la siguiente skill continúe sin fricción.
5. **Data Sources** — marcadores `~~category`, cada uno con una ruta keyless de Tier 1.
6. **Instructions** — el método numerado (trata todas las exportaciones como entrada no confiable).
7. **Next Best Skill** — adónde ir después (con reglas de terminación de visited-set + profundidad máxima).

Cada skill también declara por sí misma `metadata.discipline` (narrative / seo-geo / influencer / ad / email / launch / social / protocol) y `metadata.phase`, para que el enrutamiento y la agrupación funcionen de manera uniforme. El contrato está documentado una vez en [skill-contract.md](../references/skill-contract.md); el estado compartido entre skills vive en [state-model.md](../references/state-model.md).

### El sistema: un sistema operativo de marketing de cuatro capas

Una voz de marca, expresada a través de cinco canales siempre activos, concentrada en momentos de lanzamiento, todos leyendo y escribiendo en un sistema de registro compartido. Siete disciplinas, cuatro altitudes — un sistema, no un montón.

| Capa | Adoptar | Disciplinas | Cadencia |
|-------|-------|-------------|---------|
| **L1 · Estrategia** — qué decimos / quiénes somos | crawl | **Narrative** · TALE | siempre activo |
| **L2 · Canales** — motores siempre activos que expresan la estrategia (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influencer** · STAR | siempre activo (influencer con sesgo episódico) |
| **L3 · Orquestación** — el momento acotado en el tiempo a través de canales | run | **Product Launch** · RAMP | episódico |
| **L4 · Protocolo** — el sistema de registro compartido | — | 7 registros de verdad + memoria de trabajo · 8 gates de auditor · un contrato de skill | — |

Narrative es el mensaje; los canales son los medios que lo expresan — cada builder central registra el ID/versión exactos del canon y el offset de proyección de claims que usó, o un fallback/bloqueo aprobado explícitamente. El bucle de 4 fases de cada disciplina vive dentro de su capa (Narrative = Trace → Architect → Land → Evaluate).

Las siete usan **directorios** de fase (`narrative/trace/`…, `seo-geo/survey/`…, `influencer/scout/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…). Nota: «activate» significa contacto con creadores en influencers pero gating de cuenta en paid ads — misma palabra, alcance específico de cada disciplina.

### Sistema de calidad: ocho frameworks, ocho gates

Ocho benchmarks hacen medible lo «bueno». Cada uno define dimensiones, un método de agregación y un pequeño conjunto de **ítems de veto** (fallos duros que limitan o bloquean una puntuación con independencia del resto):

| Framework | Puntúa | Ítems / dimensiones | Agregación | Ítems de veto |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | Verdad / sistema / efectividad de la narrativa de marca | T / A / L / E | Resultados de perfil `truth`, `system` y `effectiveness` separados; sin compuesto global | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | Calidad de contenido con vistas diagnósticas CORE/GEO y EEAT/SEO | 80 ítems / 8 dimensiones | Resultado completo ponderado por perfil; las vistas diagnósticas no son totales separados | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | Autoridad de dominio y confianza de citación | 40 ítems / 4 dimensiones | Media aritmética ponderada por perfil | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | Influencer Suitability / Trust / Appeal / Return | S / T / A / R; 40 ítems / 4 dimensiones | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | Contribución incremental y calidad operativa de paid ads | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | Email: integridad del remitente / engagement / nurture / resultado directo | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | Product launch: preparación / assets / momentum / prueba | R / A / M / P; 40 IDs estables | Resultados de perfil `preflight`, `execution` y `outcome` separados; nunca promediar horizontes temporales | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | Organic social: arraigo / oficio / hosting / observabilidad | E / C / H / O; 40 IDs estables | Un perfil `asset-gate` o `program-maturity-*` por ejecución; nunca combinar unidades distintas | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

Cada framework se impone mediante un **gate de clase auditor** — una skill cuyo artefacto tipado (`class: auditor-output`) se valida con el validador determinista y hooks acotados del ciclo de vida. La CI del repositorio prueba por regresión el validador y el contrato; no inspecciona artefactos ignorados del runtime del host. Los gates son pasos del flujo de trabajo, así que cada uno vive en su disciplina y se cuenta ahí:

| Gate | Framework | Vive en | Veredicto |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | Perfiles TALE | `narrative/evaluate/` | Resultados truth/system/effectiveness separados; sin compuesto |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED; las etiquetas de confianza son solo explicativas |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED más una traducción de cara al creador |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | Perfil de ciclo de vida RAMP | `launch/mobilize/` | SHIP / FIX / BLOCK / UNDECIDED para una lectura de ciclo de vida declarada |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | Perfil ECHO de asset/programa | `social/host/` | SHIP / FIX / BLOCK / UNDECIDED para una unidad/perfil declarados |

**Política de veto compartida:** un veto verificado limita la puntuación final a `min(raw, 59)`; dos o más vetos verificados producen `status: DONE` + `verdict: BLOCK` y ninguna puntuación final. La evidencia ausente es `Unknown`, nunca un fallo automático. Las reglas tipadas viven en [auditor-runbook.md](../references/auditor-runbook.md).

### La capa de protocolo

El directorio `protocol/` alberga la **maquinaria compartida de verdad y memoria** que se sitúa fuera de los flujos de fase de las disciplinas — 8 skills, contadas por separado:

| Skill | Función | Anclada a | Stream de eventos canónico / rol runtime |
|-------|-----|-------------|-----------------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | Perfil canónico de marca/entidad (Knowledge Graph, Wikidata, desambiguación por IA) | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | Roster/dossier canónico de creadores — handles deduplicados, estadísticas de audiencia con etiqueta de procedencia, tarifas, historial de compliance | influencers | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | Libro de ofertas y sustanciación de claims — el registro contra el que se juzgan las comprobaciones de claims O1/T2 | paid | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | Registro canónico de consentimiento/supresión por sujeto — los vetos S2/N1 juzgan contra él | email | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | Dossier/calendario canónico de lanzamiento — tier, etapa de ciclo de vida de una sola dirección, fechas/embargo autoritativos, libro de envíos por canal; el SSOT de verdad de lanzamiento contra el que juzga el veto R1 de verdad de etapa | launch | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | Registro canónico por canal — handles, propiedad/autorización, normas de plataforma, defaults de divulgación; el SSOT de verdad de canal contra el que juzga el veto E1 de verdad de canal de ECHO | social | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | Canon canónico de brand-narrative — narrativa estratégica aprobada, sistema de mensajes, lenguaje/léxico, proof points; el SSOT de canon de marca contra el que juzga el veto T1 de verdad de TALE | narrative | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | Ciclo de vida de memoria HOT/WARM/COLD (capturar · promover · degradar · archivar · consultar) | todas las disciplinas | estado runtime no canónico de `memory/` |

Los registros siguen una **regla de escritor único** (otras skills envían vía `registry-events.py` proposal events), y *curan* — los gates *juzgan*. La capa genuinamente horizontal bajo todo son los protocolos de `references/` ([auditor-runbook](../references/auditor-runbook.md), [state-model](../references/state-model.md), [skill-contract](../references/skill-contract.md), [humanizer-slop](../references/humanizer-slop.md), [measurement-protocol](../references/measurement-protocol.md)) — compartidos por diseño como documentos, no como skills.

### Memoria y hooks de automatización

**La memoria** está escalonada por temperatura, para que el contexto sobreviva entre skills y sesiones sin inflar el prompt:

| Nivel | Ubicación | Comportamiento |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Cargado automáticamente en cada sesión; limitado a **80 líneas Y 25 KB** (lo que se dispare primero). |
| **WARM** | `memory/<subdir>/` | Proyecciones de trabajo reconstruibles y artefactos de auditoría con permisos; la verdad canónica de los registros vive en `memory/events/*.ndjson`. |
| **COLD** | `memory/archive/` | Registros degradados/más antiguos, conservados para su recuperación. |

**Los hooks** (`hooks/hooks.json`, ejecutor `hooks/claude-hook.sh`) conectan siete eventos de Claude Code:

| Evento | Matcher | Qué hace |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Inyecta el hot-cache **saneado** + un puntero a cabos sueltos (las líneas de inyección de prompt se redactan; los caches con symlink se rechazan). |
| `UserPromptSubmit` | (todos) | Hook de contexto ligero por prompt. |
| `PreToolUse` | herramientas conocidas con capacidad de escritura | Verifica antes de las escrituras soportadas en `memory/**` que el objetivo exacto del proyecto anfitrión esté ignorado por Git; de lo contrario, la escritura se deniega. |
| `PostToolUse` | herramientas conocidas con capacidad de escritura | Auditoría de memoria post-estado + validación acotada del Artifact Gate tras escrituras exitosas. |
| `PostToolUseFailure` | herramientas conocidas con capacidad de escritura | Ejecuta las mismas comprobaciones tras herramientas fallidas que podrían haber escrito archivos igualmente. |
| `PostToolBatch` | (todos) | Revalida la memoria operativa y el sumidero de auditoría reservado tras cada lote paralelo. |
| `Stop` | (todos) | Realiza un último barrido acotado; el guard de active-stop permite después la terminación. Pre-commit/CI solo protegen contenido Git comprometido frente a PII, no artefactos runtime ignorados. |

El Artifact Gate es **agnóstico al framework** — el mismo hook valida artefactos TALE, CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP y ECHO sin código específico por framework.

---

## Catálogo de skills

Los enlaces de skill abren cada `SKILL.md`. Despliega los **Detalles** bajo cada disciplina para ver el propósito en una línea por skill. El orden del catálogo sigue las [cuatro capas de estratos](#el-sistema-un-sistema-operativo-de-marketing-de-cuatro-capas) — Narrative (L1 · Estrategia) primero, los cinco canales siempre activos a continuación, Launch (L3 · Orquestación), y luego la capa de protocolo.

### Narrative — TALE (16)

Cuatro fases bajo `narrative/` siguen Trace → Architect → Land → Evaluate. `narrative-quality-auditor` ejecuta por separado los perfiles truth, system y effectiveness; una revisión completa enlaza tres resultados y nunca los promedia. Narrative es la estrategia L1 que heredan los builders de canal.

| Fase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>Propósito por skill (Narrative)</b></summary>

| Skill | Palanca TALE | Qué hace |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | Captura la historia de marca actual y real tal como vive en las superficies propias — el punto de partida honesto antes de cualquier rediseño. |
| category-narrative-mapper | T | Mapea las narrativas dominantes de la categoría y las alternativas nombradas para que la marca pueda reclamar una posición defendible y diferenciada. |
| audience-belief-mapper | T | Aflora lo que la audiencia objetivo ya cree, duda y le importa — las creencias que la narrativa debe mover. |
| positioning-truth-tracer | T | Rastrea cada claim de posicionamiento hasta su sustanciación, retirando todo lo no respaldado (aguas arriba del veto T1 de verdad). |
| strategic-narrative-designer | A | Diseña la narrativa estratégica central — el arco de historia de cambio-en-el-mundo, las apuestas y la resolución con la que lidera la marca. |
| message-system-architect | A | Arquitecta el sistema de mensajes — tagline, pilares, proof points y ángulos por audiencia como una estructura coherente. |
| brand-language-codifier | A | Codifica voz, tono, léxico y lenguaje do/don't para que cada canal suene como una única marca. |
| story-bank-builder | A | Construye un banco reutilizable de historias de prueba, narrativas de clientes y analogías del que los canales puedan tirar. |
| narrative-cascade-planner | L | Planifica cómo la narrativa desciende a cada canal y momento sin dilución ni deriva. |
| pitch-narrative-builder | L | Da forma de pitch a la narrativa — columna del deck, historia de la demo y encuadre para inversores/prensa. |
| narrative-enablement-kit | L | Kit de enablement que permite a cada equipo contar la historia de forma consistente — talk track, FAQ y mapa de mensajes. |
| proof-point-packager | L | Empaqueta proof points en assets listos para canal, conscientes del claims-ledger. |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | Gate TALE tipado; devuelve resultados de perfil separados y nunca los promedia. Escribe `memory/audits/narrative/`. |
| message-test-designer | E | Diseña tests de mensaje — matriz de variantes, celdas de audiencia y lectura de resonancia para la narrativa estratégica. |
| narrative-resonance-monitor | E | Rastrea cómo aterriza la narrativa a través de los canales desde fuentes keyless (datos proxy etiquetados). |
| narrative-drift-monitor | E | Vigila la deriva de narrativa — dónde los canales se han desviado del canon aprobado — y señala correcciones. |

**Reutilizado entre disciplinas** (contado en sus fases de origen, no duplicado): [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) (lógicamente el frente de Trace, físicamente en `launch/`), [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker` (denominador de resonancia). **Ningún conector nuevo** — la resonancia de narrativa reutiliza `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` — véase [tale-benchmark.md](../references/tale-benchmark.md).

</details>

### SEO/GEO — SITE (16)

Cuatro directorios de fase (4 skills cada uno) más los dos gates de calidad de la disciplina (marcados con ⛩).

| Fase | Skills |
|-------|--------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Propósito por skill (SEO/GEO)</b></summary>

| Skill | Qué hace |
|-------|--------------|
| keyword-research | Inicia el trabajo de keywords para una página/tema/campaña — intención, demanda y oportunidades a tiro de piedra. |
| competitor-analysis | Analiza la estrategia SEO de un competidor, compara dominios, descubre sus keywords y brechas. |
| serp-analysis | Lee una SERP — features, snippets, People Also Ask, patrones de ranking para una consulta. |
| content-gap-analysis | Encuentra temas ausentes y huecos de cobertura frente a competidores. |
| content-writer | Escribe y actualiza artículos, landing pages y copy de producto optimizados para SEO. |
| geo-content-optimizer | Optimiza contenido para motores de IA (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | Etiquetas Title/Meta/OG/Twitter más datos estructurados JSON-LD / Schema.org. |
| page-play-builder | Jugadas de página basadas en plantilla — páginas programáticas, plataformas parásito, páginas de comparación, local/GBP. |
| ⛩ content-quality-auditor | Gate de preparación para publicar CORE-EEAT de 80 ítems (SHIP/FIX/BLOCK). |
| technical-seo-checker | Velocidad del sitio, Core Web Vitals, indexación, rastreabilidad, robots. |
| on-page-seo-checker | Audita la salud on-page a nivel de página — encabezados, colocación de keywords, imágenes, señales de calidad. |
| site-structure-optimizer | Enlaces internos, anchor text, páginas huérfanas, jerarquía de páginas, taxonomía de URL, clústeres hub/spoke. |
| ⛩ domain-authority-auditor | Gate de confianza de dominio CITE de 40 ítems (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Rastrea rankings de keywords, cambios de posición y caídas. |
| performance-monitor | Informes multi-métrica de SEO/GEO, dashboards y alertas de umbral. |
| offsite-signal-analyzer | Perfil de backlinks + calidad de enlaces, más tráfico de referencia de asistentes de IA en tus propios GA4/GSC/logs. |

</details>

### Social — ECHO (16)

Cuatro fases bajo `social/` siguen Explore → Craft → Host → Observe. `social-quality-auditor` selecciona el `asset-gate` o un perfil de program-maturity; esos constructos nunca se combinan. La disciplina no contiene automatización alguna de publicación, engagement o DMs.

| Fase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>Propósito por skill (Social)</b></summary>

| Skill | Palanca ECHO | Qué hace |
|-------|-----------|--------------|
| channel-portfolio-planner | E | Elige la mezcla de plataformas y el rol/cadencia por canal desde donde la audiencia realmente está (registra canales al registro). |
| voice-dossier-builder | E | Voz de marca, tono, persona y léxico do/don't para una presencia consistente y de sonido humano. |
| platform-norm-profiler | E | Normas, formatos, señales de ranking y reglas de línea roja por plataforma antes de que publiques ahí. |
| participation-warmup-planner | E | Plan de warm-up comunitario no promocional — dónde aparecer y aportar valor antes de vender. |
| social-calendar-builder | C | Calendario editorial — temas, series, cadencia equilibrada a la capacidad real (sin sobre-publicar). |
| social-creative-builder | C | Posts nativos de plataforma (hook/cuerpo/CTA), con message match y conscientes del claims-ledger. |
| short-video-scripter | C | Guiones de vídeo de formato corto — hook, beats, texto en pantalla, estructura de retención. |
| advocacy-program-designer | C | Programa de advocacy de empleados/comunidad — opt-in, defaults de divulgación, kit de assets compartibles. |
| ⛩ social-quality-auditor | asset gate / program maturity | Gate ECHO tipado para una unidad/perfil; nunca combina constructos de asset y de operación. Escribe `memory/audits/social/`. |
| engagement-inbox-manager | H | Playbook de triage de reply/comment/DM — tiers de respuesta, escalado, disciplina de engagement genuino (sin engagement fabricado/con cebo). |
| social-selling-planner | H | Motion de social-selling de founder/equipo — outreach que prioriza la relación, sin DMs automatizados. |
| crisis-response-planner | H | Tiers de crisis pre-redactados, holding statements, escalera de escalado y disparadores de pausar-la-cola. |
| social-pulse-monitor | O | Pulso de menciones/sentimiento/temas desde fuentes keyless, lecturas spike-vs-sustain (datos proxy etiquetados). |
| share-of-voice-tracker | O | Share-of-voice frente a competidores nombrados sobre un denominador estable por periodo. |
| dark-social-attributor | O | Atribuye tráfico dark-social/sin enlace — disciplina de UTM, captura de atribución autorreportada, parsing de referencias. |
| social-measurement-loop | O | Lee un cambio ya lanzado contra una baseline a lo largo de una ventana → Promote / Keep-testing / Rollback. |

**Reutilizado entre disciplinas** (contado en sus fases de origen, no duplicado): `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — véase [echo-benchmark.md](../references/echo-benchmark.md).

</details>

### Email — SEND (16)

Cuatro directorios de fase bajo `email/` (4 skills cada uno) siguen el bucle SEND; el gate (⛩ email-quality-auditor) está en Deliver. Solo el gate calcula la EQS ponderada por objetivo — cada otra skill trabaja una palanca y hace el traspaso. Agnóstico al caso de uso (ciclo de vida B2C / cold outbound B2B / newsletter-creator); la columna de peso por objetivo elige el énfasis.

| Fase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Propósito por skill (Email)</b></summary>

| Skill | Palanca SEND | Qué hace |
|-------|-----------|--------------|
| deliverability-qa | S | Auth SPF/DKIM/DMARC/BIMI de pre-flight, reputación, inbox-placement, contenido spam e higiene de lista (la comprobación S1). |
| list-segment-builder | E | Segmentos por comportamiento + etapa de ciclo de vida y reglas de supresión desde tu propia exportación de lista/CRM/GA4. |
| list-growth-designer | S (+N) | Estrategia de crecimiento de lista — canales de adquisición, conceptos de lead magnet, una spec de flujo de captura opt-in conforme y mecánicas de referral-loop; alimenta la calidad de consentimiento S capturada en la adquisición. |
| list-hygiene-monitor | S | *(NUEVO)* Salud de lista continua — poda de bounces/quejas, políticas de sunset, re-permission y supresión de segmentos inactivos. |
| email-creative-builder | E (+D) | Asunto/preheader/cuerpo/CTA, con message match a la landing page, consciente del claims-ledger. |
| subject-line-lab | E | *(NUEVO)* Ideación y scoring de asunto/preheader — longitud, spam-trigger, equilibrio curiosidad/claridad, conjuntos de variantes para testear. |
| email-render-builder | E | *(NUEVO)* Build/QA de email HTML — compatibilidad de cliente, dark-mode, accesibilidad, alt de texto plano y checklist de render-test. |
| dynamic-content-personalizer | E | *(NUEVO)* Bloques de personalización merge-tag/liquid, reglas de contenido condicional y seguridad de valor de fallback. |
| email-sequence-designer | N | Flujos de ciclo de vida/automatización (welcome, cart, post-purchase, win-back) + governance de frecuencia. |
| newsletter-monetization-planner | D | Suscripción de pago, inventario de patrocinio + rate card y economía de referral growth-loop. |
| preference-frequency-manager | N | *(NUEVO)* Diseño de preference center y governance de frecuencia de envío para reducir fatiga y bajas. |
| reactivation-specialist | N | *(NUEVO)* Flujos de win-back / re-engagement para suscriptores inactivos con reglas de decisión sunset-o-recuperar. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | Gate SEND de clase auditor: puntúa EQS, impone S1/S2/N1/D1, emite SHIP/FIX/BLOCK; incluye un modo **go/no-go pre-envío**. |
| send-experiment-designer | E | Diseño de A/B / send-time / hold-out con tamaño de muestra + lectura de significancia (promote/kill). |
| inbox-placement-monitor | S | *(NUEVO)* Seguimiento continuo de placement inbox-vs-spam vía seed lists y señales de proveedor, con alertas de deriva de reputación. |
| cold-outbound-sequencer | D | *(NUEVO)* Cadencias de cold outbound B2B conformes — ramp seguro para deliverability, tokens de personalización y pasos de manejo de respuestas. |

**Reutilizado entre disciplinas** (contado en sus fases de origen, no duplicado): [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md).

</details>

### Paid Ads — ROAS (16)

Cuatro directorios de fase bajo `ad/` (4 skills cada uno) siguen el bucle ROAS; el gate (⛩ ad-account-auditor) está en Activate. Solo el gate calcula la RQS ponderada por objetivo — cada otra skill trabaja una palanca y hace el traspaso.

| Fase | Skills |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Propósito por skill (Paid Ads)</b></summary>

| Skill | Palanca ROAS | Qué hace |
|-------|-----------|--------------|
| campaign-architect | A + estructura | Estructura de cuenta/campaña, ajuste de tipo de campaña, tipos de concordancia, negativos/exclusiones, canibalización paid↔orgánico; incluye un modo recurrente de **search-term-mining**. |
| audience-segment-builder | A | Convierte tu propia exportación de clientes/CRM/GA4 en audiencias semilla, semillas de lookalike, segmentos de exclusión y un mapa de targeting por etapa de funnel. |
| search-term-miner | A | *(NUEVO)* Mina el informe de términos de búsqueda buscando negativos, nuevos candidatos a keyword y refinamientos de tipo de concordancia. |
| product-feed-optimizer | O | *(NUEVO)* Higiene de feed de Shopping/PMax — títulos, atributos, GTINs, mapeo de categorías y correcciones de rechazos. |
| ad-creative-builder | O | Titulares/descripciones RSA, hooks y una matriz de ángulos, con message match a la página de destino. |
| ad-test-designer | O (+S) | Diseña tests A/B/n e incrementalidad (hipótesis, matriz de variantes, tamaño de muestra/potencia) y lee la significancia → promote/kill. |
| bid-strategy-planner | S | *(NUEVO)* Elige y configura la estrategia de puja según objetivo (tCPA/tROAS/max-conversions), fija objetivos y planifica las transiciones de fase de aprendizaje. |
| landing-experience-checker | O | *(NUEVO)* QA de página post-click para relevancia del anuncio, velocidad de carga, móvil y política — la comprobación de message match anuncio↔página. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Gate ROAS de clase auditor: puntúa RQS, impone R1/R2/O1/O2/A1, emite SHIP/FIX/BLOCK; incluye un modo **go/no-go de lanzamiento**. |
| conversion-signal-qa | R | QA de tracking pre-lanzamiento (disparo de eventos, higiene de UTM, gate de dedup, alineación de ventana, flags iOS-ATT) — el prerrequisito R1/R2 (construye la señal; el gate la puntúa). |
| placement-exclusion-manager | A | *(NUEVO)* Listas de exclusión de placement/audiencia — bloqueos de brand safety, poda de placements basura, supresión de gasto desperdiciado. |
| conversion-value-mapper | R | *(NUEVO)* Mapea acciones de conversión a valores/pesos y reglas de valor para que tROAS puje sobre el margen real, no sobre conteos brutos. |
| paid-measurement-loop | R (+S) | Lee un cambio ya lanzado contra un control a lo largo de una ventana → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Dedup permanente de order-ID contra el conjunto de verdad de GA4/ecommerce, normalización de ventana/moneda, comparación de modelos, incrementalidad. |
| budget-pacing-monitor | S | *(NUEVO)* Rastrea el ritmo de gasto frente al presupuesto durante el flight, señala sub/sobre-entrega y recomienda correcciones de pacing. |
| fatigue-frequency-manager | O | *(NUEVO)* Vigila señales de frecuencia y decaimiento del creative, señala anuncios fatigados y programa refresh/rotación. |

**Reutilizado entre disciplinas** (contado en sus fases de origen, no duplicado): [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) (gasto + modo bid-pacing/fase de aprendizaje), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md) (post-click), [roi-calculator](../influencer/report/roi-calculator/SKILL.md) (cálculo de retorno), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md).

</details>

### Influencers — STAR (16)

Cuatro directorios de fase (4 skills cada uno); el gate de la disciplina (⛩ creator-content-auditor) está en Activate.

| Fase | Skills |
|-------|--------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>Propósito por skill (Influencers)</b></summary>

| Skill | Qué hace |
|-------|--------------|
| audience-mapper | Perfila la audiencia objetivo y mapea su subcultura / micro-comunidad antes de colaborar con creadores. |
| trend-spotter | Timing y temas de campaña — hashtags, sonidos, formatos y momentos culturales en tendencia. |
| influencer-discovery | Construye un roster de creadores desde cero, expande a una nueva plataforma, obtén nano/micro a escala. |
| fit-scorer | Puntuación de fit objetiva y ponderada para una shortlist (puntúa en STAR Suitability (S)). |
| competitor-tracker | Los creadores, campañas, formatos, alcance/gasto estimados y brechas de un competidor. |
| campaign-planner | Planifica una campaña, un lanzamiento de producto, un tentpole o un programa de creadores always-on. |
| brief-generator | Briefs de influencer estandarizados y plantillas de equipo reutilizables. |
| budget-optimizer | Distribuye el gasto entre tiers/plataformas, proyecta ROI, modela escenarios (también sirve al gasto de paid ads + bid-pacing). |
| outreach-manager | Pitch, cadencia de seguimiento, reactivación, negociación de tarifas, seguimiento de estado. |
| ⛩ creator-content-auditor | Decisión de gate previa a la publicación sobre un envío de un creador (STAR Trust: divulgación FTC STAR-T1, integridad de claims STAR-T2). |
| contract-helper | Redacta/revisa acuerdos con creadores — derechos de uso, exclusividad, cláusulas estándar. |
| content-amplifier | Amplía el contenido orgánico de creadores con gasto pagado y reutiliza UGC en paid, web, email y orgánico. |
| landing-optimizer | Landing pages para tráfico de creadores/paid — message match, móvil, A/B (también sirve al post-click de paid). |
| performance-analyzer | Evalúa resultados de creadores, compara creadores, sentimiento, conversiones (también el scorecard cross-channel de paid). |
| roi-calculator | Mide/proyecta ROI, defiende presupuestos, valora creadores/tiers (motor de cálculo de retorno compartido, incl. paid). |
| report-generator | Informes escritos para stakeholders tras un periodo (también informes de paid ads). |

</details>

### Launch — RAMP (16)

Cuatro fases bajo `launch/` siguen Research → Assemble → Mobilize → Prove. `launch-readiness-auditor` selecciona un perfil `preflight`, `execution` u `outcome` por ejecución; los resultados de ciclo de vida se enlazan pero nunca se promedian.

| Fase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>Propósito por skill (Launch)</b></summary>

| Skill | Palanca RAMP | Qué hace |
|-------|-----------|--------------|
| positioning-mapper | R | Canvas de posicionamiento estilo Dunford — alternativas competitivas nombradas, atributos únicos, temas de valor, segmento beachhead, declaración de onlyness. |
| launch-tier-planner | R | Decisión de tier (Tier 1 flagship / Tier 2 targeted / Tier 3 changelog-level), declaración de tipo de lanzamiento, objetivos KPI, registro de riesgos con criterios de kill. |
| launch-window-planner | R | Comparación de ventanas candidatas (conflictos / vientos de cola / riesgo), decisión launch-week vs rolling-release, buffer de revisión de store, definición de ventana de embargo. |
| early-access-designer | R | Escalera de etapas waitlist→concept→alpha→beta→GA con criterios de graduación, gating por cohorte, bucle de feedback, mecánicas de referral (aguas arriba del veto R1 de verdad de etapa). |
| message-house-builder | A | Message house (tagline, one-liner, pilares de valor, proof points) + columna PR-FAQ working-backwards + angle packs por canal (aguas arriba de A1). |
| launch-asset-packager | A | Manifiesto de assets de lanzamiento con alcance por tier — spec de press kit, specs de demo/screenshot, FAQ de lanzamiento, metadatos de store-listing, checklist técnica de go-live. |
| pricing-packaging-planner | A | Pricing y packaging de lanzamiento — estructura de tiers, mapa valor-a-precio, escalera de ofertas de lanzamiento, pricing beta con ruta de graduación, términos de garantía. |
| sales-enablement-kit | A | Enablement interno — battle cards, talk track de ventas, tabla de manejo de objeciones, FAQ interna + macros de CS, anuncio interno con disciplina de embargo. |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | Gate RAMP tipado para una lectura de ciclo de vida; nunca promedia horizontes temporales. Escribe `memory/audits/launch/`. |
| launch-day-conductor | M | Runbook de día de lanzamiento por bloques horarios — chequeo de gate de precondiciones, veredictos de ventana de observación tras pushes irreversibles, escalera de incidentes P0–P3 + playbooks de rollback. |
| community-launch-runner | M | Paquetes de envío por plataforma (Product Hunt, Show HN, subreddits, olas de directorios, canales regionales/chinos) bajo un chequeo de línea roja de plataforma. |
| press-media-relations | M | Lista de medios/analistas de tres tiers, timing de pitch con embargo, borrador de nota de prensa en estructura estándar, guion de briefing a analistas. |
| launch-monitor | P | Vigilancia de ventana T-0→T+30 — verificación de instrumentación (aguas arriba de P1), polling de rank/reviews/news, snapshots KPI D0/W1/M1, lecturas spike-vs-sustain. |
| launch-feedback-synthesizer | P | Digest de temas de feedback, bucle de estado open→shipped («you asked, we shipped»), cosecha de social proof conforme. |
| launch-retro-analyzer | P | Retro D1/W1/M1 — actual-vs-target por canal, 5-Whys sobre el mayor fallo, decisiones keep/kill/change, snapshot de resultado al registro. |
| momentum-planner | P | Plan de momentum T+1→T+30 — calendario de momentos de lanzamiento, enrutamiento de tier de anuncio, decisión de legitimidad de relaunch, próximo momento Tier-1. |

**Reutilizado entre disciplinas** (contado en sus fases de origen, no duplicado): `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-registry`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — véase [ramp-benchmark.md](../references/ramp-benchmark.md).

</details>

### Capa de protocolo (8)

La maquinaria compartida de verdad y memoria — véase [Arquitectura § La capa de protocolo](#la-capa-de-protocolo) para roles y reglas de escritor único.

| Grupo | Skills |
|-------|--------|
| **Protocolo** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>Propósito por skill (Protocolo)</b></summary>

| Skill | Qué hace |
|-------|--------------|
| entity-registry | Perfil de entidad canónico para Knowledge Graph, Wikidata, desambiguación por IA. |
| creator-registry | Roster/dossier canónico de creadores — handles deduplicados, estadísticas de audiencia con etiqueta de procedencia, tarifas e historial de compliance. |
| offer-claims-registry | Libro canónico de ofertas y sustanciación de claims — el registro contra el que se juzgan las comprobaciones de claims O1/T2. |
| consent-registry | Registro canónico de consentimiento/supresión por sujeto — timestamp de opt-in + base legal, prueba de doble opt-in, historial append-only de unsub/bounce/queja; el registro contra el que juzgan los vetos S2/N1. |
| launch-registry | Dossier canónico por lanzamiento + calendario de lanzamiento — tier, tipo de lanzamiento, etapa de ciclo de vida de una sola dirección (draft→…→GA), fechas autoritativas + compromisos de embargo, libro de envíos por canal, snapshot de resultado; el SSOT de verdad de lanzamiento. |
| channel-registry | Registro canónico por canal — handles, propiedad/autorización, normas de plataforma, defaults de divulgación; el SSOT de verdad de canal contra el que juzga el veto E1 de verdad de canal de ECHO. |
| narrative-registry | Canon canónico de brand-narrative — narrativa estratégica aprobada, sistema de mensajes, lenguaje/léxico, proof points; el SSOT de canon de marca contra el que juzga el veto T1 de verdad de TALE. |
| memory-management | Revisar, promover, degradar y archivar la memoria de proyecto HOT/WARM/COLD. |

</details>

---

## Comandos

Ocho comandos: `/aaron-marketing:auto` enruta cualquier objetivo por las siete disciplinas, y cada disciplina tiene exactamente un punto de entrada explícito. Fuente: [commands/](../commands).

| Comando | Para qué | Acotación |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Describe cualquier objetivo — infiere la intención y ejecuta el flujo de trabajo mínimo útil | `--deep` (exhaustivo / stress-test) |
| `/aaron-marketing:narrative` | Brand narrative (bucle TALE): rastrear la historia actual y la categoría, arquitectar la narrativa estratégica y el sistema de mensajes, aterrizarla a través de los canales, el gate de calidad, resonancia y deriva | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO de principio a fin (bucle SITE): sondear demanda/competidores, implementar contenido, afinar calidad/técnica/on-page, evaluar autoridad/rankings/informes/memoria | `--phase survey\|implement\|tune\|evaluate` + flags por fase (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | Influencers (bucle STAR): insight de audiencia, scouting y fit, targeting, outreach, amplificación, reporting de ROI | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | Paid ads (bucle ROAS): segmentos, estructura, creative, diseño de experimentos, el gate de auditoría, medición | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | Email (bucle SEND): deliverability/consent, segmentación, creative, flujos de ciclo de vida, monetización, send-testing, el gate de auditoría | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch (bucle RAMP): posicionamiento, tier y ventana, message house y assets, el gate de readiness, ejecución del día de lanzamiento, monitoreo y retro | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Organic social (bucle ECHO): portafolio de canales y voz, calendario y creative, el gate de calidad, hosting de engagement/crisis, pulso y medición | `--phase explore\|craft\|host\|observe` |

El trabajo diario normalmente empieza con `/aaron-marketing:auto`; los otros siete son puntos de entrada explícitos de disciplina, con `--phase` para acotar la etapa.

---

## Conectores y niveles de mejora

Las skills nombran las herramientas con marcadores `~~category` (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) en lugar de proveedores específicos, y cada categoría tiene una **ruta keyless de Tier 1**. Las recetas completas — incluido el endpoint gratuito/de primera parte de cada categoría — están en [CONNECTORS.md](../CONNECTORS.md).

### La capa de conectores es un producto en sí misma

**Más de 100 rutas de integración documentadas** en tres capas diseñadas — y cada una se gana su lugar:

| Capa | Qué obtienes |
|-------|--------------|
| **28 conectores empaquetados sin dependencias** | Python de biblioteca estándar puro — sin `pip`, sin paso de build. SERP en vivo keyless + scraping renderizado con JS (Firecrawl, Tavily), una sonda de citación de respuestas de IA, extracciones de email-auth por DNS-over-HTTPS, series de atención de Wikipedia, menciones de noticias GDELT, métricas reales de creadores de YouTube, push a IndexNow + Baidu, automatización de ESP Resend y un libro de medición diffeable por git que convierte a cualquiera de ellos en una serie temporal antes/después. |
| **Más de 60 APIs oficiales/gratuitas documentadas** | Cada fila enlaza la **documentación oficial** del proveedor, lleva una fecha de verificación, y cada enlace se comprueba por HTTP antes de publicarse. Incluye las rutas que la mayoría de listas de herramientas omiten: GSC URL Inspection, CrUX History (40 semanas de CWV de campo), la Gmail Postmaster Tools API, la Ad Library de Meta, la Data Export API de Microsoft Clarity. |
| **Servidores MCP de proveedores** | 18 endpoints remotos catalogados (nunca auto-registrados — tu lista `/mcp` se mantiene limpia) más los servidores oficiales auto-hospedados para Google Analytics, Search Console, **Google Ads** y **Microsoft Clarity**. Dos MCP remotos funcionan sin ninguna clave (Firecrawl, Tavily). |

Lo que los hace fiables en lugar de solo numerosos:

- **Tres clases de seguridad, gates diseñados** ([SECURITY.md](../SECURITY.md)): los fetchers alojados ejecutan un **pre-flight local de robots.txt** antes de cada fetch delegado y rehúsan ante Disallow; todo lo que muta estado externo (envíos de email, pushes de índice) es **dry-run por defecto** tras un flag `--live` explícito, con claves de idempotencia donde el proveedor las admite y sin auto-retry donde no.
- **Verificado, y luego re-verificado**: los endpoints se comprueban contra la documentación primaria del proveedor con fechas, las rutas keyless se prueban en vivo, un guard de CI impone el sync de versión/tracking, y un smoke en vivo previo al release detecta la deriva de endpoints (ya ha detectado cambios reales de API — dos veces).
- **Hechos, no veredictos**: los conectores informan presencia de registros, tags parseados y series en bruto; los gates de auditor hacen el juicio, y las skills etiquetan cada número con **Measured / User-provided / Estimated**.
- **Un playbook escrito** ([docs/connector-playbook.md](connector-playbook.md)) gobierna cada adición — calificar, verificar, implementar, testear, cablear, documentar, trackear, regresar, registrar — para que la calidad se mantenga mientras el catálogo crece.

| Nivel | Requiere | Qué obtienes |
|------|----------|---------|
| **Tier 1** (por defecto) | Nada | Pega datos, o extráelos de fuentes gratuitas/públicas. El framework de análisis completo funciona de cualquier modo. |
| **Tier 2** | Una API o MCP gratuita de primera parte | Obtención automática de tus propios datos de GSC / GA4 / Core Web Vitals. |
| **Tier 3** | Un conjunto MCP más completo | Flujos de trabajo multi-fuente totalmente automatizados. |

- **Ayudantes empaquetados sin dependencias** bajo `scripts/connectors/` (solo biblioteca estándar de Python) extraen datos públicos/propios localmente — p. ej. PageSpeed/CrUX, Open PageRank, crawl de página, Wayback CDX, Wikidata SPARQL, Common Crawl, recetas de advertools — más **`resend.py`**, automatización directa del ESP Resend para las skills de email (clave de free-tier: estado de auth de dominio, seed-test sends, sync de supresión, programación de broadcasts; los subcomandos que mutan son dry-run por defecto y requieren `--live`), y **`firecrawl.py`** + **`tavily.py`**, automatización de fetchers alojados keyless para las skills de research (Firecrawl: SERP web en vivo + markdown de página renderizada con JS + site maps; Tavily: búsqueda con puntuación + sonda de fuentes citadas de un motor de respuestas de IA para GEO + extracción de URL — ambos gratis sin ninguna clave, ambos con un pre-flight local de robots.txt incorporado).
- **Fuentes gratuitas/keyless** documentadas por categoría: Google Search Console y GA4 (datos propios), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, SERP/scrape keyless de Firecrawl, AI-search keyless de Tavily, registros de email-auth por DNS-over-HTTPS (`doh.py`), series de atención de Wikipedia (`pageviews.py`), menciones de noticias GDELT (`gdelt.py`), métricas de creadores de YouTube con una clave gratuita (`youtube.py`), push a IndexNow + Baidu (`indexpush.py`, con gate de dry-run), las bibliotecas de ad-transparency (Meta/Google/TikTok), y filas de receta para crt.sh, el validador W3C, oEmbed y HN Algolia.
- **Servidores MCP opt-in** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, la suite gratuita auto-hospedada **OpenSEO**, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, los keyless Firecrawl y Tavily) están catalogados en [`docs/mcp-catalog.json`](mcp-catalog.json) como **referencia solo para copiar y pegar** — el catálogo se sitúa fuera de la ruta `.mcp.json` de la raíz del plugin que se auto-registra, así que no se registra nada por ti. Copia las entradas que quieras en tu propia configuración MCP.

Las skills de paid ads puntúan a partir de tu **exportación manual de tu propia cuenta** (CSV del gestor de anuncios nativo, GA4, ecommerce). Las APIs de plataforma de anuncios con clave (Google Ads SDK, Meta Marketing API) son opt-in solo de Tier-2/3 y **nunca** un requisito de Tier 1. Las skills de email puntúan igual — a partir de tu **propia exportación de ESP** — y cada señal de deliverability es keyless (lookups de DNS, un informe DMARC RUA y un test de inbox con seed-list), así que una API de ESP con clave tampoco es nunca un requisito de Tier 1; cuando Resend es tu ESP, el `resend.py` empaquetado automatiza el mismo bucle en el free-tier.

---

## Flujos de trabajo recomendados

La mayoría de los objetivos reales cruzan disciplinas. `/aaron-marketing:auto` enruta un objetivo en lenguaje natural a la cadena mínima útil entre las siete — un lanzamiento de producto, por ejemplo, activa Launch, Email, Social y Paid a la vez:

```text
/aaron-marketing:auto lanzar nuestra v2 en Product Hunt en 3 semanas — 1.200 en la lista de espera; necesitamos la página, los correos y el plan del día de lanzamiento
```

O recorre el bucle de una disciplina de punta a punta (la guía `README.md` de cada directorio de disciplina añade jugadas a nivel de escenario):

**Narrative (bucle TALE)**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor` (⛩ puerta TALE) → `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO (bucle SITE)**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor` (⛩ puerta de publicación) → `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer`; revisión de confianza con `domain-authority-auditor` (⛩)

**Social (bucle ECHO)**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor` (⛩ puerta ECHO) → `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**Email (bucle SEND)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ puerta EQS) antes de cualquier envío

**Paid Ads (bucle ROAS)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` para la página)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ puerta RQS) antes de activar presupuesto
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Influencers (bucle STAR)**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (STAR Suitability)
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor` (⛩ puerta STAR) → `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Launch (bucle RAMP)**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor` (⛩ puerta RAMP) → `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

Para una revisión de confianza completa, combina `content-quality-auditor` con `domain-authority-auditor` para una evaluación combinada de 120 ítems. Con `memory-management` activo, los traspasos y cabos sueltos persisten automáticamente en la memoria HOT/WARM/COLD.

---

## Estructura del repositorio

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE (16, incl. su gate)
seo-geo/{survey,implement,tune,evaluate}/                   # SEO/GEO (16, incl. sus 2 gates)
influencer/{scout,target,activate,report}/                     # Influencers (16, incl. su gate)
ad/research|orchestrate|activate|scale/            # Paid Ads — ROAS (16, incl. su gate)
email/setup|engage|nurture|deliver/                  # Email — SEND (16, incl. su gate)
launch/research|assemble|mobilize|prove/             # Launch — RAMP (16, incl. su gate)
social/explore|craft|host|observe/                   # Social — ECHO (16, incl. su gate)
protocol/                                            # Capa de protocolo (8) — registros de verdad + memoria
commands/        # 8 comandos slash (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # contrato compartido, modelo de estado, los 8 benchmarks, auditor runbook, packs de plataforma
evals/           # casos de eval estructurales por skill + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (la única lógica de runtime)
scripts/         # validate-skill.sh + connectors/ (stdlib) + guards de CI
memory/          # andamiaje HOT/WARM/COLD + almacenes de registro (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # READMEs localizados (zh)
.claude-plugin/  # plugin.json + espejo marketplace.json
```

---

## Filosofía de diseño

- **Las skills son contenido.** El único código es el validador en Bash, el ejecutor de hooks en Bash y ayudantes de conector/comprobación de la biblioteca estándar de Python sin dependencias. Nunca dependencias de terceros / `pip` — impuesto por un guard de dependency-creep.
- **Keyless primero.** Cada `~~category` tiene una receta gratuita/de datos propios; MCP y las herramientas de pago son pura comodidad.
- **Quirúrgico y MECE.** Cada skill posee una tarea con un límite de alcance nítido; el trabajo solapado se entrega como un *modo* de una skill existente en lugar de una nueva skill fina. Los registros curan, los gates juzgan, los analizadores alimentan a los gates.
- **Sin números inventados.** Las skills etiquetan cada cifra con Measured / User-provided / Estimated e incluyen un detector de jerga de IA / frases prohibidas.
- **El compliance es guía, no ley.** Las comprobaciones de divulgación FTC e integridad de claims señalan riesgo; no son asesoramiento legal.

---

## Guardas de calidad (CI)

Cada cambio se ejecuta contra un conjunto de guards fail-closed (todos en `scripts/` y `tests/`):

| Guard | Comprueba |
|-------|--------|
| `validate-skill.sh` | Frontmatter, secciones requeridas, consistencia de versión, enlaces plugin-relativos en las 120 skills. |
| `golden-auditor-math.py` | Suma de pesos determinista + aritmética de ejemplos trabajados para los **ocho** frameworks. |
| `check-evals.py` | Lint estructural de eval + `structure-manifest.json` (120/120 skills llevan casos de eval). |
| `check-pii.py` | Bloquea secrets / PII commiteados (allowlist a nivel de token, fail-closed). |
| `check-stdlib-only.sh` | Guard de dependency-creep + la línea roja de API con clave de Paid Ads. |
| `check-versions.sh` | Guard de sincronización de versiones: el catálogo del sistema, los manifiestos de plugin/marketplace/OpenClaw, los badges del README raíz y localizados, AGENTS/CLAUDE/VERSIONS, el About de GitHub y las 120 versiones de skills se mantienen alineados. |
| `tests/test_connectors_local.py` | Tests offline de constructores de request y parsers que abarcan los 29 módulos de conectores incluidos (sin red en CI). |
| `tests/test_hook_artifact_gate.sh` | Tests de comportamiento del Artifact Gate del hook + saneamiento de SessionStart. |

La deriva de endpoints en vivo se muestrea por separado con el **manual** [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) — una llamada real mínima por conector alojado listado en ese script, con aserciones de forma (las respuestas de rate-limit cuentan como SKIP); ejecútalo antes de un release, nunca en CI.

---

## Contribuir y documentación del proyecto

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — reglas de autoría, la checklist de contribución y la lista autoritativa de las 10 superficies de tracking.
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** — versiones por skill + changelog (bundle actual: `19.1.0`).
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** — política de seguridad, privacidad y comunidad.
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** — contexto de cara al agente para este repo.

---

## Aviso legal

Estas skills asisten flujos de trabajo de brand-narrative, SEO/GEO, influencer-marketing, paid-ads, email-marketing, product-launch y organic-social pero **no** garantizan rankings, citaciones de IA, tráfico, engagement, conversiones, ROAS, deliverability ni resultados de negocio. Las comprobaciones de compliance de influencers, anuncios, email y social (divulgación FTC, integridad de claims, política de plataforma, consentimiento/opt-in, divulgación de conexión material) son guía, no asesoramiento legal. Verifica las recomendaciones con profesionales cualificados antes de basar en ellas decisiones importantes de estrategia, financieras o legales.

## Licencia

Apache License 2.0 — véase [LICENSE](../LICENSE).

*Última sincronización con el README en inglés: v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
