<div align="center">

# Aaron Marketing Skills

**120 skills marketing — brand narrative, SEO/GEO, influence, paid ads, e-mail, launch, social — sur un seul contrat.**

<p align="center">
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills"><img src="https://img.shields.io/github/stars/aaron-he-zhu/aaron-marketing-skills?style=flat" alt="GitHub Stars"></a>
<!-- GENERATED:BEGIN release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/VERSIONS.md"><img src="https://img.shields.io/badge/version-19.2.0-orange" alt="Version"></a>
<!-- GENERATED:END release-surface:version-badge -->
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-green" alt="License"></a>
  <a href="https://github.com/aaron-he-zhu/aaron-marketing-skills/commits/main"><img src="https://img.shields.io/github/last-commit/aaron-he-zhu/aaron-marketing-skills" alt="Last Commit"></a>
</p>
<p align="center">
  <a href="https://www.skills.sh/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillssh.json" alt="skills.sh"></a>
  <a href="https://clawhub.ai/aaron-he-zhu"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/clawhub.json" alt="ClawHub"></a>
  <a href="https://skillhub.cn/user/user_2c0f1e77"><img src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/aaron-he-zhu/aaron-marketing-skills/main/badges/skillhub.json" alt="SkillHub"></a>
</p>

[English](../README.md) | [Deutsch](README.de.md) | [Español](README.es.md) | **Français** | [Italiano](README.it.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português](README.pt.md) | [简体中文](README.zh.md) | [繁體中文](README.zh-Hant.md)

</div>

Une bibliothèque de skills Claude et de commandes slash qui transforme un agent de chat en opérateur marketing. Sept disciplines et une couche de protocole partagée, en un coup d'œil :

| Couche | Skills | Cycle de vie (répertoires de phase) | Framework → gate | Point d'entrée |
|-------|--------|-------------------------------|------------------|------------|
| **Narrative** | 16 | trace → architect → land → evaluate | [TALE](../references/tale-benchmark.md) → `narrative-quality-auditor` (truth / system / effectiveness profiles) | `/aaron-marketing:narrative` |
| **SEO/GEO** | 16 | survey → implement → tune → evaluate | [CORE-EEAT](../references/core-eeat-benchmark.md) → `content-quality-auditor` · [CITE](../references/cite-domain-rating.md) → `domain-authority-auditor` | `/aaron-marketing:seo-geo` |
| **Social** | 16 | explore → craft → host → observe | [ECHO](../references/echo-benchmark.md) → `social-quality-auditor` (asset / program-maturity profiles) | `/aaron-marketing:social` |
| **E-mail** | 16 | setup → engage → nurture → deliver | [SEND](../references/send-benchmark.md) → `email-quality-auditor` (EQS) | `/aaron-marketing:email` |
| **Paid Ads** | 16 | research → orchestrate → activate → scale | [ROAS](../references/roas-benchmark.md) → `ad-account-auditor` (RQS) | `/aaron-marketing:ad` |
| **Influence** | 16 | scout → target → activate → report | [STAR](../references/star-benchmark.md) → `creator-content-auditor` (SQS) ; `fit-scorer` note Suitability (S) | `/aaron-marketing:influencer` |
| **Launch** | 16 | research → assemble → mobilize → prove | [RAMP](../references/ramp-benchmark.md) → `launch-readiness-auditor` (preflight / execution / outcome profiles) | `/aaron-marketing:launch` |
| **Couche de protocole** | 8 | — (machinerie partagée, hors des flux de phase) | 7 registres de vérité (entity · creator · offer/claims · consent · launch · channel · narrative) + mémoire HOT/WARM/COLD | — |

`/aaron-marketing:auto` route n'importe quel objectif en langage naturel à travers l'ensemble. Les skills et les commandes sont du **Markdown pur** ; de petits runtimes Bash/Python-stdlib fournissent les hooks, la validation, le scoring, les événements de registre, les connecteurs et les checks CI (pas de `pip`, pas d'étape de build). **Chaque skill fonctionne au Tier 1 avec les données que vous fournissez** ; les connecteurs n'automatisent que la récupération de données ou une mutation explicitement approuvée.

La topologie typée faisant autorité est [`references/system-catalog.json`](../references/system-catalog.json) ; voir l'[architecture système générée](system-architecture.md) pour la carte lisible à quatre couches, les 120 chemins, les propriétaires de registres, les puits d'auditeur et les profils de distribution.

> Les repos autrefois autonomes, avant la fusion, sont désormais des **repos-panneaux** pointant ici — [seo-geo-claude-skills](https://github.com/aaron-he-zhu/seo-geo-claude-skills) (la ligne finale à 20 skills est conservée au tag `v9.9.12`) et [influencer-marketing-agent-skills](https://github.com/aaron-he-zhu/influencer-marketing-agent-skills) (la ligne IMPACT finale au tag `standalone-final`). Politique des repos frères : [docs/repo-family.md](repo-family.md).

---

## Sommaire

- [Pourquoi cette bibliothèque](#pourquoi-cette-bibliothèque)
- [Installation](#installation)
- [Première utilisation](#première-utilisation)
- [Architecture](#architecture)
  - [Le contrat de skill partagé](#le-contrat-de-skill-partagé)
  - [Le système : un système d'exploitation marketing à quatre couches](#le-système--un-système-dexploitation-marketing-à-quatre-couches)
  - [Système de qualité : huit frameworks, huit gates](#système-de-qualité--huit-frameworks-huit-gates)
  - [La couche de protocole](#la-couche-de-protocole)
  - [Mémoire & hooks d'automatisation](#mémoire--hooks-dautomatisation)
- [Catalogue de skills](#catalogue-de-skills)
  - [Narrative — TALE (16)](#narrative--tale-16)
  - [SEO/GEO — SITE (16)](#seogeo--site-16)
  - [Influence — STAR (16)](#influence--star-16)
  - [Paid Ads — ROAS (16)](#paid-ads--roas-16)
  - [Email — SEND (16)](#email--send-16)
  - [Launch — RAMP (16)](#launch--ramp-16)
  - [Social — ECHO (16)](#social--echo-16)
  - [Couche de protocole (8)](#couche-de-protocole-8)
- [Commandes](#commandes)
- [Connecteurs & paliers d'amélioration](#connecteurs--paliers-damélioration)
- [Workflows recommandés](#workflows-recommandés)
- [Structure du dépôt](#structure-du-dépôt)
- [Philosophie de conception](#philosophie-de-conception)
- [Contrôles qualité (CI)](#contrôles-qualité-ci)
- [Contribuer & docs du projet](#contribuer--docs-du-projet)
- [Avertissement](#avertissement)
- [Licence](#licence)

---

## Pourquoi cette bibliothèque

| Principe | Ce que cela signifie en pratique |
|-----------|---------------------------|
| **Keyless par défaut** | Chaque skill fonctionne en **Tier 1** avec des données que vous collez ou tirez de sources gratuites/de première partie. Les outils payants et les serveurs MCP sont un confort optionnel, jamais un prérequis. Les skills paid ads notent à partir de votre **export manuel de votre propre compte** — les API publicitaires à clé ne sont jamais requises. |
| **Content-first, contrats exécutables** | Les skills restent du Markdown. De petits runtimes Bash/Python-stdlib rendent le scoring, l'état, la sécurité et la conformité déterministes sans ajouter de dépendances de paquets. |
| **Un contrat partagé** | Les 120 skills exposent les mêmes sept sections et déclarent elles-mêmes les métadonnées `discipline` + `phase`, de sorte que la bibliothèque se comporte comme un unique système d'exploitation : chaque skill connaît ses entrées, ses sorties et le meilleur skill suivant auquel passer la main. |
| **Qualité sous gate** | Huit benchmarks produisent des verdicts structurés et vérifiables. Les hooks bornés signalent les écritures invalides ; pre-commit/CI protègent seulement le contenu Git commité contre les PII et ne valident pas les artefacts runtime. |
| **La vérité vit dans des événements** | Sept flux de registre en append-only sont canoniques ; des projections contrôlées par leur propriétaire exposent l'état des entités, créateurs, claims, consentements, launchs, canaux et narratives, sans files d'attente destructrices. |
| **Mémoire entre les tours** | Un modèle de mémoire HOT/WARM/COLD transporte les découvertes, les scores et les boucles ouvertes entre skills et sessions, assainis à l'entrée. |
| **Voix naturelle** | Les skills embarquent un détecteur de jargon d'IA et une liste de phrases bannies pour que la sortie se lise comme écrite par un humain. |

---

## Installation

Utilisez-la avec Claude Code, n'importe quel host compatible Agent Skills ou un simple `git clone` :

| Host | Installation |
|------|---------|
| **Claude Code** | `/plugin marketplace add aaron-he-zhu/aaron-marketing-skills` puis `/plugin install aaron-marketing@aaron` |
| **Codex · Cursor · OpenCode · Antigravity · Gemini CLI · Copilot CLI · OpenClaw · Hermes · [70+ hosts](https://github.com/vercel-labs/skills#supported-agents)** | `npx skills add aaron-he-zhu/aaron-marketing-skills` |
| **Clients Agent Plugins v1 · Portable Lite** | Téléchargez `aaron-marketing-skills-19.2.0-agent-plugin-v1-lite.tar.gz` depuis la [release v19.2.0](https://github.com/aaron-he-zhu/aaron-marketing-skills/releases/tag/v19.2.0), décompressez-le puis installez le répertoire du plugin extrait |
| **[SkillHub.cn](https://skillhub.cn) (communauté chinoise)** | `skillhub install <frontmatter-slug>` (p. ex. `keyword-research`) |
| **N'importe quel host** | `git clone https://github.com/aaron-he-zhu/aaron-marketing-skills` |

Dans Claude Code, `marketplace add` ne fait qu'enregistrer le catalogue — exécutez `/plugin install aaron-marketing@aaron` (ou choisissez-le dans `/plugin`) pour réellement activer les skills et les commandes. Pour tirer un **seul** skill sur un host générique : `npx skills add aaron-he-zhu/aaron-marketing-skills -s keyword-research`. Parcourez le bundle sur le [registre skills.sh](https://skills.sh/aaron-he-zhu/aaron-marketing-skills). Répertoires par agent, particularités du frontmatter et ce qui se dégrade hors du plugin : [docs/agent-compatibility.md](agent-compatibility.md) (vérifié 120/120 installables, 2026-07).

Installer le plugin n'ajoute **rien** à votre liste `/mcp` — le catalogue MCP vit dans [`docs/mcp-catalog.json`](mcp-catalog.json), délibérément hors du chemin `.mcp.json` de la racine du plugin que Claude Code enregistre automatiquement, si bien que c'est une référence à copier-coller uniquement (voir [Connecteurs](#connecteurs--paliers-damélioration)).

La racine du dépôt est la source d'édition, **pas** la racine d'installation standard Agent Plugins v1. Utilisez l'asset de release ci-dessus : il projette **120/120 Agent Skills stricts** dans `skills/<name>/` et n'inclut ni `mcp.json`, ni commandes, hooks, connecteurs ou runtime du dépôt. Les couches de compatibilité existantes sont conservées ; consultez le [paquet Portable Lite et ses limites de capacité](agent-plugins-v1.md).

---

## Première utilisation

Si votre host prend en charge le routage automatique des skills, décrivez simplement l'objectif :

```text
Research keywords for my SaaS product targeting small teams
```
```text
Find TikTok creators for a skincare launch and score their fit
```
```text
Audit this Google Ads account before I scale — exports attached
```

Ou utilisez les commandes slash — `/auto` pour le routage, ou un point d'entrée de discipline :

```text
/aaron-marketing:auto turn our pricing page into an AI-citable comparison hub
```
```text
/aaron-marketing:seo-geo https://example.com/blog/my-article --phase tune
```

`/aaron-marketing:auto` infère l'intention et exécute le plus petit workflow utile, ne s'arrêtant qu'aux décisions bloquantes. Chaque skill fonctionne avec des données collées ; les outils optionnels sont documentés dans [CONNECTORS.md](../CONNECTORS.md).

---

## Architecture

### Le contrat de skill partagé

Chaque skill suit le **même contrat d'activation** — sept sections dans un ordre fixe :

1. **Trigger / quand l'utiliser** — quand le skill doit se déclencher.
2. **Quick Start** — prompts à copier-coller.
3. **Skill Contract** — Sortie attendue · Lit · Écrit · Promeut · Terminé-quand · Skill suivant principal.
4. **Handoff Summary** — la forme standard de passage de main pour que le skill suivant enchaîne proprement.
5. **Data Sources** — marqueurs `~~category`, chacun avec un chemin keyless de Tier 1.
6. **Instructions** — la méthode numérotée (traite tous les exports comme entrée non fiable).
7. **Next Best Skill** — où aller ensuite (avec règles de terminaison visited-set + profondeur maximale).

Chaque skill déclare aussi lui-même `metadata.discipline` (narrative / seo-geo / influencer / ad / email / launch / social / protocol) et `metadata.phase`, pour que le routage et le clustering fonctionnent uniformément. Le contrat est documenté une fois dans [skill-contract.md](../references/skill-contract.md) ; l'état partagé entre skills vit dans [state-model.md](../references/state-model.md).

### Le système : un système d'exploitation marketing à quatre couches

Une voix de marque, exprimée à travers cinq canaux toujours actifs, concentrée dans des moments de launch, tous lisant et écrivant un système de record partagé. Sept disciplines, quatre altitudes — un système, pas un tas.

| Couche | Adopte | Disciplines | Cadence |
|-------|-------|-------------|---------|
| **L1 · Stratégie** — ce que nous disons / qui nous sommes | crawl | **Narrative** · TALE | toujours actif |
| **L2 · Canaux** — moteurs toujours actifs qui expriment la stratégie (owned → bought) | walk | **SEO/GEO** · CORE-EEAT + CITE · **Organic Social** · ECHO · **Email** · SEND · **Paid Ads** · ROAS · **Influence** · STAR | toujours actif (influence à tendance épisodique) |
| **L3 · Orchestration** — le moment délimité dans le temps à travers les canaux | run | **Product Launch** · RAMP | épisodique |
| **L4 · Protocole** — le système de record partagé | — | 7 registres de vérité + mémoire de travail · 8 gates d'auditeur · un contrat de skill | — |

Narrative est le message ; les canaux sont les médiums qui l'expriment — chaque builder central consigne l'ID/la version exacts du canon et l'offset de projection des claims qu'il a utilisés, ou un fallback/blocage explicitement approuvé. La boucle à 4 phases de chaque discipline vit dans sa couche (Narrative = Trace → Architect → Land → Evaluate).

Les sept utilisent des **répertoires** de phase (`narrative/trace/`…, `seo-geo/survey/`…, `influencer/scout/`…, `ad/research/`…, `email/setup/`…, `launch/research/`…, `social/explore/`…). Note : « activate » signifie l'approche des créateurs en influence mais le gating de compte en paid ads — même mot, portée spécifique à la discipline.

### Système de qualité : huit frameworks, huit gates

Huit benchmarks rendent « bon » mesurable. Chacun définit des dimensions, une méthode d'agrégation et un petit ensemble d'**items de veto** (échecs durs qui plafonnent ou bloquent un score indépendamment du reste) :

| Framework | Note | Items / dimensions | Agrégation | Items de veto |
|-----------|--------|--------------------|--------|------------|
| **[TALE](../references/tale-benchmark.md)** | Vérité / système / efficacité de la narrative de marque | T / A / L / E | Résultats de profil `truth`, `system` et `effectiveness` séparés ; pas de composite global | TALE `T1`/`A1`/`L1`/`E1` |
| **[CORE-EEAT](../references/core-eeat-benchmark.md)** | Qualité de contenu avec vues diagnostiques CORE/GEO et EEAT/SEO | 80 items / 8 dimensions | Résultat complet pondéré par profil ; les vues diagnostiques ne sont pas des totaux séparés | `T04`/`C01`/`R10` |
| **[CITE](../references/cite-domain-rating.md)** | Autorité de domaine et confiance de citation | 40 items / 4 dimensions | Moyenne arithmétique pondérée par profil | `T03`/`T05`/`T09` |
| **[STAR](../references/star-benchmark.md)** | Influence Suitability / Trust / Appeal / Return | S / T / A / R ; 40 items / 4 dimensions | `SQS = floor(profile-weighted mean)` | `STAR-S2`/`S6`, `STAR-T1`/`T2`/`T3` |
| **[ROAS](../references/roas-benchmark.md)** | Contribution incrémentale et qualité opérationnelle des paid ads | R / O / A / S | `RQS = floor(profile-weighted mean)` | `R1`/`R2`/`O1`/`O2`/`A1` |
| **[SEND](../references/send-benchmark.md)** | Email : intégrité de l'expéditeur / engagement / nurture / résultat direct | S / E / N / D | `EQS = floor(profile-weighted mean)` | `S1`/`S2`/`N1`/`D1` |
| **[RAMP](../references/ramp-benchmark.md)** | Product launch : préparation / assets / momentum / preuve | R / A / M / P ; 40 IDs stables | Résultats de profil `preflight`, `execution` et `outcome` séparés ; ne jamais moyenner les horizons temporels | RAMP `R1`/`A1`/`M1`/`P1` |
| **[ECHO](../references/echo-benchmark.md)** | Organic social : ancrage / artisanat / hosting / observabilité | E / C / H / O ; 40 IDs stables | Un profil `asset-gate` ou `program-maturity-*` par exécution ; ne jamais combiner des unités dissemblables | ECHO `E1`/`C1`/`C2`/`H1`/`H2`/`O1` |

Chaque framework est appliqué par un **gate de classe auditeur** — un skill dont l'artefact typé (`class: auditor-output`) est validé par le validateur déterministe et des hooks bornés du cycle de vie. La CI du dépôt teste le validateur et le contrat en régression ; elle n'inspecte pas les artefacts runtime de l'hôte ignorés. Les gates sont des étapes de workflow, donc chacun vit dans sa discipline et y est compté :

| Gate | Framework | Vit dans | Verdict |
|------|-----------|----------|---------|
| [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | Profils TALE | `narrative/evaluate/` | Résultats truth/system/effectiveness séparés ; pas de composite |
| [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `seo-geo/tune/` | SHIP / FIX / BLOCK / UNDECIDED |
| [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `seo-geo/evaluate/` | SHIP / FIX / BLOCK / UNDECIDED ; les labels de confiance sont purement explicatifs |
| [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md) | STAR SQS | `influencer/activate/` | SHIP / FIX / BLOCK / UNDECIDED plus une traduction à destination du créateur |
| [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `ad/activate/` | SHIP / FIX / BLOCK / UNDECIDED |
| [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `email/deliver/` | SHIP / FIX / BLOCK / UNDECIDED |
| [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md) | Profil de cycle de vie RAMP | `launch/mobilize/` | SHIP / FIX / BLOCK / UNDECIDED pour une lecture de cycle de vie déclarée |
| [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md) | Profil ECHO asset/programme | `social/host/` | SHIP / FIX / BLOCK / UNDECIDED pour une unité/un profil déclarés |

**Politique de veto partagée :** un veto vérifié plafonne le score final à `min(raw, 59)` ; deux vetos vérifiés ou plus produisent `status: DONE` + `verdict: BLOCK` et aucun score final. Une preuve manquante vaut `Unknown`, jamais un échec automatique. Les règles typées vivent dans [auditor-runbook.md](../references/auditor-runbook.md).

### La couche de protocole

Le répertoire `protocol/` héberge la **machinerie partagée de vérité & de mémoire** qui se situe hors des flux de phase des disciplines — 8 skills, comptés séparément :

| Skill | Rôle | Ancré à | Flux d'événements canonique / rôle runtime |
|-------|-----|-------------|-----------------|
| [entity-registry](../protocol/entity-registry/SKILL.md) | Profil canonique de marque/entité (Knowledge Graph, Wikidata, désambiguïsation IA) | SEO/GEO | `memory/events/entities.ndjson` |
| [creator-registry](../protocol/creator-registry/SKILL.md) | Roster/dossier canonique de créateurs — handles dédupliqués, stats d'audience étiquetées par provenance, tarifs, historique de conformité | influence | `memory/events/creators.ndjson` |
| [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md) | Grand livre d'offres & de substantiation de claims — l'enregistrement contre lequel les vérifications de claims O1/T2 sont jugées | paid | `memory/events/claims.ndjson` |
| [consent-registry](../protocol/consent-registry/SKILL.md) | Enregistrement canonique de consentement/suppression par sujet — les vetos S2/N1 jugent contre lui | e-mail | `memory/events/consent.ndjson` |
| [launch-registry](../protocol/launch-registry/SKILL.md) | Dossier/calendrier canonique de launch — tier, étape de cycle de vie à sens unique, dates/embargo faisant autorité, grand livre de soumission par canal ; le SSOT de vérité du launch contre lequel le veto R1 de vérité d'étape juge | launch | `memory/events/launches.ndjson` |
| [channel-registry](../protocol/channel-registry/SKILL.md) | Enregistrement canonique par canal — handles, propriété/autorisation, normes de plateforme, défauts de divulgation ; le SSOT de vérité du canal contre lequel le veto ECHO E1 de vérité de canal juge | social | `memory/events/channels.ndjson` |
| [narrative-registry](../protocol/narrative-registry/SKILL.md) | Canon canonique de brand-narrative — narrative stratégique approuvée, système de messages, langage/lexique, proof points ; le SSOT du canon de marque contre lequel le veto TALE T1 de vérité juge | narrative | `memory/events/narrative.ndjson` |
| [memory-management](../protocol/memory-management/SKILL.md) | Cycle de vie mémoire HOT/WARM/COLD (capturer · promouvoir · rétrograder · archiver · interroger) | toutes les disciplines | état runtime non canonique de `memory/` |

Les registres suivent une **règle d'écrivain unique** (les autres skills soumettent via `registry-events.py` proposal events), et ils *curatent* — les gates *jugent*. La couche véritablement horizontale sous tout le reste, ce sont les protocoles de `references/` ([auditor-runbook](../references/auditor-runbook.md), [state-model](../references/state-model.md), [skill-contract](../references/skill-contract.md), [humanizer-slop](../references/humanizer-slop.md), [measurement-protocol](../references/measurement-protocol.md)) — partagés par conception en tant que documents, pas en tant que skills.

### Mémoire & hooks d'automatisation

**La mémoire** est étagée par température, pour que le contexte survive entre skills et sessions sans gonfler le prompt :

| Niveau | Emplacement | Comportement |
|------|----------|----------|
| **HOT** | `memory/hot-cache.md` | Chargé automatiquement à chaque session ; plafonné à **80 lignes ET 25 Ko** (le premier atteint l'emporte). |
| **WARM** | `memory/<subdir>/` | Projections de travail reconstructibles et artefacts d'audit à permissions ; la vérité canonique des registres vit dans `memory/events/*.ndjson`. |
| **COLD** | `memory/archive/` | Enregistrements rétrogradés/plus anciens, conservés pour rappel. |

**Les hooks** (`hooks/hooks.json`, exécuteur `hooks/claude-hook.sh`) câblent sept événements Claude Code :

| Événement | Matcher | Ce qu'il fait |
|-------|---------|--------------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Injecte le hot-cache **assaini** + un pointeur vers les boucles ouvertes (les lignes d'injection de prompt sont caviardées ; les caches en symlink sont rejetés). |
| `UserPromptSubmit` | (tous) | Hook de contexte léger par prompt. |
| `PreToolUse` | outils connus capables d'écrire | Vérifie avant les écritures prises en charge dans `memory/**` que la cible exacte du projet hôte est ignorée par Git ; sinon l'écriture est refusée. |
| `PostToolUse` | outils connus capables d'écrire | Audit mémoire post-état + validation bornée de l'Artifact Gate après les écritures réussies. |
| `PostToolUseFailure` | outils connus capables d'écrire | Exécute les mêmes vérifications après les outils en échec, qui peuvent déjà avoir écrit des fichiers. |
| `PostToolBatch` | (tous) | Revérifie la mémoire opérationnelle et le puits d'audit réservé après chaque lot parallèle. |
| `Stop` | (tous) | Effectue un dernier balayage borné ; le garde active-stop autorise ensuite l'arrêt. Pre-commit/CI ne protègent que le contenu Git commité contre les PII, pas les artefacts runtime ignorés. |

L'Artifact Gate est **agnostique au framework** — le même hook valide les artefacts TALE, CORE-EEAT, CITE, STAR, ROAS, SEND, RAMP et ECHO sans code spécifique par framework.

---

## Catalogue de skills

Les liens de skill ouvrent chaque `SKILL.md`. Dépliez les **Détails** sous chaque discipline pour un objectif en une ligne par skill. L'ordre du catalogue suit les [quatre couches](#le-système--un-système-dexploitation-marketing-à-quatre-couches) — Narrative (L1 · Stratégie) en premier, les cinq canaux toujours actifs ensuite, Launch (L3 · Orchestration), puis la couche de protocole.

### Narrative — TALE (16)

Quatre phases sous `narrative/` suivent Trace → Architect → Land → Evaluate. `narrative-quality-auditor` exécute séparément les profils truth, system et effectiveness ; une revue complète relie trois résultats et ne les moyenne jamais. Narrative est la stratégie L1 dont héritent les builders de canaux.

| Phase | Skills |
|-------|--------|
| **Trace** | [narrative-baseline-mapper](../narrative/trace/narrative-baseline-mapper/SKILL.md), [category-narrative-mapper](../narrative/trace/category-narrative-mapper/SKILL.md), [audience-belief-mapper](../narrative/trace/audience-belief-mapper/SKILL.md), [positioning-truth-tracer](../narrative/trace/positioning-truth-tracer/SKILL.md) |
| **Architect** | [strategic-narrative-designer](../narrative/architect/strategic-narrative-designer/SKILL.md), [message-system-architect](../narrative/architect/message-system-architect/SKILL.md), [brand-language-codifier](../narrative/architect/brand-language-codifier/SKILL.md), [story-bank-builder](../narrative/architect/story-bank-builder/SKILL.md) |
| **Land** | [narrative-cascade-planner](../narrative/land/narrative-cascade-planner/SKILL.md), [pitch-narrative-builder](../narrative/land/pitch-narrative-builder/SKILL.md), [narrative-enablement-kit](../narrative/land/narrative-enablement-kit/SKILL.md), [proof-point-packager](../narrative/land/proof-point-packager/SKILL.md) |
| **Evaluate** | ⛩ [narrative-quality-auditor](../narrative/evaluate/narrative-quality-auditor/SKILL.md), [message-test-designer](../narrative/evaluate/message-test-designer/SKILL.md), [narrative-resonance-monitor](../narrative/evaluate/narrative-resonance-monitor/SKILL.md), [narrative-drift-monitor](../narrative/evaluate/narrative-drift-monitor/SKILL.md) |

<details><summary><b>Objectif par skill (Narrative)</b></summary>

| Skill | Levier TALE | Ce qu'il fait |
|-------|-----------|--------------|
| narrative-baseline-mapper | T | Capture l'histoire de marque actuelle et réelle telle qu'elle vit à travers les surfaces owned — le point de départ honnête avant toute refonte. |
| category-narrative-mapper | T | Cartographie les narratives dominantes de la catégorie et les alternatives nommées pour que la marque puisse revendiquer une position défendable et différenciée. |
| audience-belief-mapper | T | Fait émerger ce que l'audience cible croit, doute et à quoi elle tient déjà — les croyances que la narrative doit faire bouger. |
| positioning-truth-tracer | T | Relie chaque claim de positionnement à sa substantiation, retirant tout ce qui n'est pas étayé (en amont du veto T1 de vérité). |
| strategic-narrative-designer | A | Conçoit la narrative stratégique de base — l'arc d'histoire de changement-dans-le-monde, les enjeux et la résolution avec lesquels la marque mène. |
| message-system-architect | A | Architecture le système de messages — tagline, piliers, proof points et angles par audience comme une unique structure cohérente. |
| brand-language-codifier | A | Codifie voix, ton, lexique et langage do/don't pour que chaque canal sonne comme une seule marque. |
| story-bank-builder | A | Construit une banque réutilisable d'histoires de preuve, de narratives clients et d'analogies dans laquelle les canaux peuvent puiser. |
| narrative-cascade-planner | L | Planifie comment la narrative se diffuse dans chaque canal et moment sans dilution ni dérive. |
| pitch-narrative-builder | L | Modèle la narrative en forme de pitch — colonne du deck, histoire de démo et framing investisseurs/presse. |
| narrative-enablement-kit | L | Kit d'enablement qui permet à chaque équipe de raconter l'histoire de façon cohérente — talk track, FAQ et message map. |
| proof-point-packager | L | Empaquette les proof points en assets prêts pour le canal et conscients du claims-ledger. |
| ⛩ narrative-quality-auditor | truth / system / effectiveness | Gate TALE typé ; renvoie des résultats de profil séparés et ne les moyenne jamais. Écrit `memory/audits/narrative/`. |
| message-test-designer | E | Conçoit des tests de message — matrice de variantes, cellules d'audience et lecture de résonance pour la narrative stratégique. |
| narrative-resonance-monitor | E | Suit comment la narrative atterrit à travers les canaux depuis des sources keyless (données proxy étiquetées). |
| narrative-drift-monitor | E | Surveille la dérive narrative — où les canaux se sont éloignés du canon approuvé — et signale les corrections. |

**Réutilisé entre disciplines** (compté dans leurs phases d'origine, non dupliqué) : [positioning-mapper](../launch/research/positioning-mapper/SKILL.md) (logiquement le front de Trace, physiquement dans `launch/`), [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), `audience-mapper`, `share-of-voice-tracker` (dénominateur de résonance). **Aucun nouveau connecteur** — la résonance narrative réutilise `bluesky.py` / `gdelt.py` / `tavily.py` / `wayback.py` — voir [tale-benchmark.md](../references/tale-benchmark.md).

</details>

### SEO/GEO — SITE (16)

Quatre répertoires de phase (4 skills chacun) plus les deux gates de qualité de la discipline (marqués ⛩).

| Phase | Skills |
|-------|--------|
| **Survey** | [keyword-research](../seo-geo/survey/keyword-research/SKILL.md), [competitor-analysis](../seo-geo/survey/competitor-analysis/SKILL.md), [serp-analysis](../seo-geo/survey/serp-analysis/SKILL.md), [content-gap-analysis](../seo-geo/survey/content-gap-analysis/SKILL.md) |
| **Implement** | [content-writer](../seo-geo/implement/content-writer/SKILL.md), [geo-content-optimizer](../seo-geo/implement/geo-content-optimizer/SKILL.md), [serp-markup-builder](../seo-geo/implement/serp-markup-builder/SKILL.md), [page-play-builder](../seo-geo/implement/page-play-builder/SKILL.md) |
| **Tune** | ⛩ [content-quality-auditor](../seo-geo/tune/content-quality-auditor/SKILL.md), [technical-seo-checker](../seo-geo/tune/technical-seo-checker/SKILL.md), [on-page-seo-checker](../seo-geo/tune/on-page-seo-checker/SKILL.md), [site-structure-optimizer](../seo-geo/tune/site-structure-optimizer/SKILL.md) |
| **Evaluate** | ⛩ [domain-authority-auditor](../seo-geo/evaluate/domain-authority-auditor/SKILL.md), [rank-tracker](../seo-geo/evaluate/rank-tracker/SKILL.md), [performance-monitor](../seo-geo/evaluate/performance-monitor/SKILL.md), [offsite-signal-analyzer](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md) |

<details><summary><b>Objectif par skill (SEO/GEO)</b></summary>

| Skill | Ce qu'il fait |
|-------|--------------|
| keyword-research | Démarre le travail de mots-clés pour une page/un sujet/une campagne — intention, demande et opportunités à portée de main. |
| competitor-analysis | Analyse la stratégie SEO d'un concurrent, compare les domaines, met au jour ses mots-clés et ses lacunes. |
| serp-analysis | Lit une SERP — features, snippets, People Also Ask, motifs de classement pour une requête. |
| content-gap-analysis | Trouve les sujets manquants et les trous de couverture face aux concurrents. |
| content-writer | Rédige et rafraîchit des articles, landing pages et textes produit optimisés SEO. |
| geo-content-optimizer | Optimise le contenu pour les moteurs IA (ChatGPT, Perplexity, AI Overviews, Gemini, Claude, Copilot). |
| serp-markup-builder | Balises Title/Meta/OG/Twitter plus données structurées JSON-LD / Schema.org. |
| page-play-builder | Plays de page pilotés par template — pages programmatiques, plateformes parasites, pages de comparaison, local/GBP. |
| ⛩ content-quality-auditor | Gate de préparation à la publication CORE-EEAT à 80 items (SHIP/FIX/BLOCK). |
| technical-seo-checker | Vitesse du site, Core Web Vitals, indexation, crawlabilité, robots. |
| on-page-seo-checker | Audite la santé on-page au niveau de la page — titres, placement des mots-clés, images, signaux de qualité. |
| site-structure-optimizer | Liens internes, ancres, pages orphelines, hiérarchie de pages, taxonomie d'URL, clusters hub/spoke. |
| ⛩ domain-authority-auditor | Gate de confiance de domaine CITE à 40 items (TRUSTED/CAUTIOUS/UNTRUSTED). |
| rank-tracker | Suit les classements de mots-clés, les changements de position et les chutes. |
| performance-monitor | Rapports SEO/GEO multi-métriques, dashboards et alertes de seuil. |
| offsite-signal-analyzer | Profil de backlinks + qualité des liens, plus trafic de référence des assistants IA dans vos propres GA4/GSC/logs. |

</details>

### Social — ECHO (16)

Quatre phases sous `social/` suivent Explore → Craft → Host → Observe. `social-quality-auditor` sélectionne l'`asset-gate` ou un profil de program-maturity ; ces constructions ne sont jamais combinées. La discipline ne contient aucune automatisation de publication, d'engagement ou de DM.

| Phase | Skills |
|-------|--------|
| **Explore** | [channel-portfolio-planner](../social/explore/channel-portfolio-planner/SKILL.md), [voice-dossier-builder](../social/explore/voice-dossier-builder/SKILL.md), [platform-norm-profiler](../social/explore/platform-norm-profiler/SKILL.md), [participation-warmup-planner](../social/explore/participation-warmup-planner/SKILL.md) |
| **Craft** | [social-calendar-builder](../social/craft/social-calendar-builder/SKILL.md), [social-creative-builder](../social/craft/social-creative-builder/SKILL.md), [short-video-scripter](../social/craft/short-video-scripter/SKILL.md), [advocacy-program-designer](../social/craft/advocacy-program-designer/SKILL.md) |
| **Host** | ⛩ [social-quality-auditor](../social/host/social-quality-auditor/SKILL.md), [engagement-inbox-manager](../social/host/engagement-inbox-manager/SKILL.md), [social-selling-planner](../social/host/social-selling-planner/SKILL.md), [crisis-response-planner](../social/host/crisis-response-planner/SKILL.md) |
| **Observe** | [social-pulse-monitor](../social/observe/social-pulse-monitor/SKILL.md), [share-of-voice-tracker](../social/observe/share-of-voice-tracker/SKILL.md), [dark-social-attributor](../social/observe/dark-social-attributor/SKILL.md), [social-measurement-loop](../social/observe/social-measurement-loop/SKILL.md) |

<details><summary><b>Objectif par skill (Social)</b></summary>

| Skill | Levier ECHO | Ce qu'il fait |
|-------|-----------|--------------|
| channel-portfolio-planner | E | Choisit le mix de plateformes et le rôle/cadence par canal depuis là où l'audience est réellement (enregistre les canaux dans le registre). |
| voice-dossier-builder | E | Voix de marque, ton, persona et lexique do/don't pour une présence cohérente et au son humain. |
| platform-norm-profiler | E | Normes, formats, signaux de classement et règles de ligne rouge par plateforme avant d'y publier. |
| participation-warmup-planner | E | Plan de warm-up non promotionnel de la communauté — où se montrer et apporter de la valeur avant de vendre. |
| social-calendar-builder | C | Calendrier éditorial — thèmes, séries, cadence équilibrée à la capacité réelle (pas de sur-publication). |
| social-creative-builder | C | Posts natifs par plateforme (hook/corps/CTA), avec message match et conscients du claims-ledger. |
| short-video-scripter | C | Scripts de vidéo short-form — hook, beats, texte à l'écran, structure de rétention. |
| advocacy-program-designer | C | Programme d'advocacy employés/communauté — opt-in, défauts de divulgation, kit d'assets partageables. |
| ⛩ social-quality-auditor | asset gate / program maturity | Gate ECHO typé pour une unité/un profil ; ne combine jamais les constructions d'asset et d'exploitation. Écrit `memory/audits/social/`. |
| engagement-inbox-manager | H | Playbook de triage de reply/commentaires/DM — tiers de réponse, escalation, discipline d'engagement authentique (pas d'engagement fabriqué/appâté). |
| social-selling-planner | H | Motion de social selling founder/équipe — outreach relation-d'abord, pas de DM automatisés. |
| crisis-response-planner | H | Tiers de crise pré-rédigés, déclarations d'attente, échelle d'escalation et déclencheurs de mise-en-pause-de-la-file. |
| social-pulse-monitor | O | Pulse de mentions/sentiment/sujets depuis des sources keyless, lectures spike-vs-sustain (données proxy étiquetées). |
| share-of-voice-tracker | O | Share of voice vs concurrents nommés sur un dénominateur stable dans le temps. |
| dark-social-attributor | O | Attribue le trafic dark-social/non lié — discipline UTM, capture d'attribution auto-déclarée, parsing des référents. |
| social-measurement-loop | O | Relit un changement livré contre une baseline sur une fenêtre → Promote / Keep-testing / Rollback. |

**Réutilisé entre disciplines** (compté dans leurs phases d'origine, non dupliqué) : `trend-spotter`, `audience-mapper`, `content-amplifier`, `outreach-manager`, `competitor-tracker`, `landing-optimizer`, `performance-analyzer`, `roi-calculator`, `report-generator`, `offer-claims-registry`, `community-launch-runner`, `creator-registry`, `page-play-builder`, `memory-management` — voir [echo-benchmark.md](../references/echo-benchmark.md).

</details>

### Email — SEND (16)

Quatre répertoires de phase sous `email/` (4 skills chacun) suivent la boucle SEND ; le gate (⛩ email-quality-auditor) siège en Deliver. Seul le gate calcule l'EQS pondérée par objectif — chaque autre skill travaille un levier et passe la main. Agnostique au cas d'usage (cycle de vie B2C / cold outbound B2B / newsletter-creator) ; la colonne de poids par objectif choisit l'accent.

| Phase | Skills |
|-------|--------|
| **Setup** | [deliverability-qa](../email/setup/deliverability-qa/SKILL.md), [list-segment-builder](../email/setup/list-segment-builder/SKILL.md), [list-growth-designer](../email/setup/list-growth-designer/SKILL.md), [list-hygiene-monitor](../email/setup/list-hygiene-monitor/SKILL.md) |
| **Engage** | [email-creative-builder](../email/engage/email-creative-builder/SKILL.md), [subject-line-lab](../email/engage/subject-line-lab/SKILL.md), [email-render-builder](../email/engage/email-render-builder/SKILL.md), [dynamic-content-personalizer](../email/engage/dynamic-content-personalizer/SKILL.md) |
| **Nurture** | [email-sequence-designer](../email/nurture/email-sequence-designer/SKILL.md), [newsletter-monetization-planner](../email/nurture/newsletter-monetization-planner/SKILL.md), [preference-frequency-manager](../email/nurture/preference-frequency-manager/SKILL.md), [reactivation-specialist](../email/nurture/reactivation-specialist/SKILL.md) |
| **Deliver** | ⛩ [email-quality-auditor](../email/deliver/email-quality-auditor/SKILL.md), [send-experiment-designer](../email/deliver/send-experiment-designer/SKILL.md), [inbox-placement-monitor](../email/deliver/inbox-placement-monitor/SKILL.md), [cold-outbound-sequencer](../email/deliver/cold-outbound-sequencer/SKILL.md) |

<details><summary><b>Objectif par skill (E-mail)</b></summary>

| Skill | Levier SEND | Ce qu'il fait |
|-------|-----------|--------------|
| deliverability-qa | S | Auth SPF/DKIM/DMARC/BIMI de pré-flight, réputation, inbox-placement, contenu spam et hygiène de liste (la vérification S1). |
| list-segment-builder | E | Segments par comportement + étape de cycle de vie et règles de suppression depuis votre propre export liste/CRM/GA4. |
| list-growth-designer | S (+N) | Stratégie de croissance de liste — canaux d'acquisition, concepts de lead magnet, une spec de flux de capture opt-in conforme et des mécaniques de referral-loop ; alimente la qualité de consentement S capturée à l'acquisition. |
| list-hygiene-monitor | S | *(NOUVEAU)* Santé de liste continue — élagage bounces/plaintes, politiques de sunset, re-permission et suppression de segments inactifs. |
| email-creative-builder | E (+D) | Objet/preheader/corps/CTA, avec message match vers la landing page, conscient du claims-ledger. |
| subject-line-lab | E | *(NOUVEAU)* Idéation et scoring d'objet/preheader — longueur, spam-trigger, équilibre curiosité/clarté, jeux de variantes à tester. |
| email-render-builder | E | *(NOUVEAU)* Build/QA d'e-mail HTML — compatibilité client, dark-mode, accessibilité, alt texte brut et checklist de render-test. |
| dynamic-content-personalizer | E | *(NOUVEAU)* Blocs de personnalisation merge-tag/liquid, règles de contenu conditionnel et sécurité de valeur de fallback. |
| email-sequence-designer | N | Flux de cycle de vie/automatisation (welcome, cart, post-purchase, win-back) + gouvernance de fréquence. |
| newsletter-monetization-planner | D | Abonnement payant, inventaire de sponsoring + rate card et économie du referral growth-loop. |
| preference-frequency-manager | N | *(NOUVEAU)* Conception de preference center et gouvernance de fréquence d'envoi pour réduire la fatigue et les désabonnements. |
| reactivation-specialist | N | *(NOUVEAU)* Flux de win-back / réengagement pour abonnés dormants avec règles de décision sunset-ou-récupérer. |
| ⛩ email-quality-auditor | S+E+N+D (EQS) | Gate SEND de classe auditeur : note l'EQS, applique S1/S2/N1/D1, émet SHIP/FIX/BLOCK ; porte un mode **go/no-go pré-envoi**. |
| send-experiment-designer | E | Conception A/B / send-time / hold-out avec taille d'échantillon + lecture de significativité (promote/kill). |
| inbox-placement-monitor | S | *(NOUVEAU)* Suivi continu de placement inbox-vs-spam via seed lists et signaux de provider, avec alertes de dérive de réputation. |
| cold-outbound-sequencer | D | *(NOUVEAU)* Cadences de cold outbound B2B conformes — ramp sûr pour la deliverability, tokens de personnalisation et étapes de gestion des réponses. |

**Réutilisé entre disciplines** (compté dans leurs phases d'origine, non dupliqué) : [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md).

</details>

### Paid Ads — ROAS (16)

Quatre répertoires de phase sous `ad/` (4 skills chacun) suivent la boucle ROAS ; le gate (⛩ ad-account-auditor) siège en Activate. Seul le gate calcule la RQS pondérée par objectif — chaque autre skill travaille un levier et passe la main.

| Phase | Skills |
|-------|--------|
| **Research** | [campaign-architect](../ad/research/campaign-architect/SKILL.md), [audience-segment-builder](../ad/research/audience-segment-builder/SKILL.md), [search-term-miner](../ad/research/search-term-miner/SKILL.md), [product-feed-optimizer](../ad/research/product-feed-optimizer/SKILL.md) |
| **Orchestrate** | [ad-creative-builder](../ad/orchestrate/ad-creative-builder/SKILL.md), [ad-test-designer](../ad/orchestrate/ad-test-designer/SKILL.md), [bid-strategy-planner](../ad/orchestrate/bid-strategy-planner/SKILL.md), [landing-experience-checker](../ad/orchestrate/landing-experience-checker/SKILL.md) |
| **Activate** | ⛩ [ad-account-auditor](../ad/activate/ad-account-auditor/SKILL.md), [conversion-signal-qa](../ad/activate/conversion-signal-qa/SKILL.md), [placement-exclusion-manager](../ad/activate/placement-exclusion-manager/SKILL.md), [conversion-value-mapper](../ad/activate/conversion-value-mapper/SKILL.md) |
| **Scale** | [paid-measurement-loop](../ad/scale/paid-measurement-loop/SKILL.md), [attribution-reconciler](../ad/scale/attribution-reconciler/SKILL.md), [budget-pacing-monitor](../ad/scale/budget-pacing-monitor/SKILL.md), [fatigue-frequency-manager](../ad/scale/fatigue-frequency-manager/SKILL.md) |

<details><summary><b>Objectif par skill (Paid Ads)</b></summary>

| Skill | Levier ROAS | Ce qu'il fait |
|-------|-----------|--------------|
| campaign-architect | A + structure | Structure de compte/campagne, adéquation du type de campagne, types de correspondance, négatifs/exclusions, cannibalisation paid↔organique ; porte un mode récurrent de **search-term-mining**. |
| audience-segment-builder | A | Transforme votre propre export clients/CRM/GA4 en audiences seed, seeds lookalike, segments d'exclusion et une carte de ciblage par étape de funnel. |
| search-term-miner | A | *(NOUVEAU)* Mine le rapport de termes de recherche pour des négatifs, de nouveaux candidats mots-clés et des affinages de type de correspondance. |
| product-feed-optimizer | O | *(NOUVEAU)* Hygiène de feed Shopping/PMax — titres, attributs, GTINs, mapping de catégories et corrections de refus. |
| ad-creative-builder | O | Titres/descriptions RSA, hooks et une matrice d'angles, avec message match vers la page de destination. |
| ad-test-designer | O (+S) | Conçoit des tests A/B/n & d'incrémentalité (hypothèse, matrice de variantes, taille d'échantillon/puissance) et lit la significativité → promote/kill. |
| bid-strategy-planner | S | *(NOUVEAU)* Choisit et configure la stratégie d'enchère selon l'objectif (tCPA/tROAS/max-conversions), fixe les cibles et planifie les transitions de phase d'apprentissage. |
| landing-experience-checker | O | *(NOUVEAU)* QA de page post-clic pour la pertinence de l'annonce, la vitesse de chargement, le mobile et la policy — la vérification de message match annonce↔page. |
| ⛩ ad-account-auditor | R+O+A+S (RQS) | Gate ROAS de classe auditeur : note la RQS, applique R1/R2/O1/O2/A1, émet SHIP/FIX/BLOCK ; porte un mode **go/no-go de launch**. |
| conversion-signal-qa | R | QA de tracking pré-launch (déclenchement d'événements, hygiène UTM, gate de dédup, alignement de fenêtre, flags iOS-ATT) — le prérequis R1/R2 (construit le signal ; le gate le note). |
| placement-exclusion-manager | A | *(NOUVEAU)* Listes d'exclusion de placement/audience — blocages de brand safety, élagage des placements pourris, suppression de dépense gaspillée. |
| conversion-value-mapper | R | *(NOUVEAU)* Mappe les actions de conversion à des valeurs/poids et des règles de valeur pour que le tROAS enchérisse sur la vraie marge, pas sur des comptages bruts. |
| paid-measurement-loop | R (+S) | Relit un changement livré contre un contrôle sur une fenêtre → Promote / Keep-testing / Rollback / Unproven. |
| attribution-reconciler | R | Dédup permanente d'order-ID contre le set de vérité GA4/ecommerce, normalisation de fenêtre/devise, comparaison de modèles, incrémentalité. |
| budget-pacing-monitor | S | *(NOUVEAU)* Suit le rythme de dépense face au budget sur le flight, signale sous/sur-livraison et recommande des corrections de pacing. |
| fatigue-frequency-manager | O | *(NOUVEAU)* Surveille les signaux de fréquence et de décroissance du creative, signale les annonces fatiguées et planifie refresh/rotation. |

**Réutilisé entre disciplines** (compté dans leurs phases d'origine, non dupliqué) : [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) (dépense + mode bid-pacing/phase d'apprentissage), [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md) (post-clic), [roi-calculator](../influencer/report/roi-calculator/SKILL.md) (calcul de retour), [report-generator](../influencer/report/report-generator/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md).

</details>

### Influence — STAR (16)

Quatre répertoires de phase (4 skills chacun) ; le gate de la discipline (⛩ creator-content-auditor) siège en Activate.

| Phase | Skills |
|-------|--------|
| **Scout** | [audience-mapper](../influencer/scout/audience-mapper/SKILL.md), [trend-spotter](../influencer/scout/trend-spotter/SKILL.md), [influencer-discovery](../influencer/scout/influencer-discovery/SKILL.md), [fit-scorer](../influencer/scout/fit-scorer/SKILL.md) |
| **Target** | [competitor-tracker](../influencer/target/competitor-tracker/SKILL.md), [campaign-planner](../influencer/target/campaign-planner/SKILL.md), [brief-generator](../influencer/target/brief-generator/SKILL.md), [budget-optimizer](../influencer/target/budget-optimizer/SKILL.md) |
| **Activate** | [outreach-manager](../influencer/activate/outreach-manager/SKILL.md), ⛩ [creator-content-auditor](../influencer/activate/creator-content-auditor/SKILL.md), [contract-helper](../influencer/activate/contract-helper/SKILL.md), [content-amplifier](../influencer/activate/content-amplifier/SKILL.md) |
| **Report** | [landing-optimizer](../influencer/report/landing-optimizer/SKILL.md), [performance-analyzer](../influencer/report/performance-analyzer/SKILL.md), [roi-calculator](../influencer/report/roi-calculator/SKILL.md), [report-generator](../influencer/report/report-generator/SKILL.md) |

<details><summary><b>Objectif par skill (Influence)</b></summary>

| Skill | Ce qu'il fait |
|-------|--------------|
| audience-mapper | Profile l'audience cible et cartographie sa sous-culture / micro-communauté avant de collaborer avec des créateurs. |
| trend-spotter | Timing et thèmes de campagne — hashtags, sons, formats et moments culturels en tendance. |
| influencer-discovery | Construit un roster de créateurs de zéro, étend à une nouvelle plateforme, source du nano/micro à l'échelle. |
| fit-scorer | Score de fit objectif et pondéré pour une shortlist (noté sur STAR Suitability (S)). |
| competitor-tracker | Les créateurs, campagnes, formats, portée/dépense estimées et lacunes d'un concurrent. |
| campaign-planner | Planifie une campagne, un lancement produit, un tentpole ou un programme de créateurs always-on. |
| brief-generator | Briefs d'influence standardisés et templates d'équipe réutilisables. |
| budget-optimizer | Répartit la dépense entre tiers/plateformes, projette le ROI, modélise des scénarios (sert aussi la dépense paid ads + le bid-pacing). |
| outreach-manager | Pitch, cadence de relance, réengagement, négociation de tarifs, suivi de statut. |
| ⛩ creator-content-auditor | Décision de gate pré-publication sur une soumission de créateur (STAR Trust : divulgation FTC STAR-T1, intégrité des claims STAR-T2). |
| contract-helper | Rédige/relit des accords de créateurs — droits d'usage, exclusivité, clauses standard. |
| content-amplifier | Étend le contenu organique de créateurs avec de la dépense payante et réutilise l'UGC en paid, web, e-mail et organique. |
| landing-optimizer | Landing pages pour trafic créateurs/paid — message match, mobile, A/B (sert aussi le post-clic paid). |
| performance-analyzer | Évalue les résultats de créateurs, compare les créateurs, sentiment, conversions (aussi la scorecard cross-canal paid). |
| roi-calculator | Mesure/projette le ROI, défend les budgets, valorise créateurs/tiers (moteur de calcul de retour partagé, incl. paid). |
| report-generator | Rapports écrits pour parties prenantes après une période (aussi rapports paid ads). |

</details>

### Launch — RAMP (16)

Quatre phases sous `launch/` suivent Research → Assemble → Mobilize → Prove. `launch-readiness-auditor` sélectionne un profil `preflight`, `execution` ou `outcome` par exécution ; les résultats de cycle de vie sont reliés mais jamais moyennés.

| Phase | Skills |
|-------|--------|
| **Research** | [positioning-mapper](../launch/research/positioning-mapper/SKILL.md), [launch-tier-planner](../launch/research/launch-tier-planner/SKILL.md), [launch-window-planner](../launch/research/launch-window-planner/SKILL.md), [early-access-designer](../launch/research/early-access-designer/SKILL.md) |
| **Assemble** | [message-house-builder](../launch/assemble/message-house-builder/SKILL.md), [launch-asset-packager](../launch/assemble/launch-asset-packager/SKILL.md), [pricing-packaging-planner](../launch/assemble/pricing-packaging-planner/SKILL.md), [sales-enablement-kit](../launch/assemble/sales-enablement-kit/SKILL.md) |
| **Mobilize** | ⛩ [launch-readiness-auditor](../launch/mobilize/launch-readiness-auditor/SKILL.md), [launch-day-conductor](../launch/mobilize/launch-day-conductor/SKILL.md), [community-launch-runner](../launch/mobilize/community-launch-runner/SKILL.md), [press-media-relations](../launch/mobilize/press-media-relations/SKILL.md) |
| **Prove** | [launch-monitor](../launch/prove/launch-monitor/SKILL.md), [launch-feedback-synthesizer](../launch/prove/launch-feedback-synthesizer/SKILL.md), [launch-retro-analyzer](../launch/prove/launch-retro-analyzer/SKILL.md), [momentum-planner](../launch/prove/momentum-planner/SKILL.md) |

<details><summary><b>Objectif par skill (Launch)</b></summary>

| Skill | Levier RAMP | Ce qu'il fait |
|-------|-----------|--------------|
| positioning-mapper | R | Canvas de positionnement façon Dunford — alternatives concurrentes nommées, attributs uniques, thèmes de valeur, segment beachhead, énoncé d'onlyness. |
| launch-tier-planner | R | Décision de tier (Tier 1 flagship / Tier 2 targeted / Tier 3 changelog-level), déclaration de type de launch, cibles KPI, registre de risques avec critères de kill. |
| launch-window-planner | R | Comparaison de fenêtres candidates (conflits / vents porteurs / risque), décision launch-week vs rolling-release, buffer de review de store, définition de fenêtre d'embargo. |
| early-access-designer | R | Échelle d'étapes waitlist→concept→alpha→beta→GA avec critères de graduation, gating par cohorte, boucle de feedback, mécaniques de referral (en amont du veto R1 de vérité d'étape). |
| message-house-builder | A | Message house (tagline, one-liner, piliers de valeur, proof points) + colonne PR-FAQ working-backwards + angle packs par canal (en amont d'A1). |
| launch-asset-packager | A | Manifeste d'assets de launch cadré par tier — spec de press kit, specs de démo/screenshot, FAQ de launch, métadonnées de store-listing, checklist technique de go-live. |
| pricing-packaging-planner | A | Pricing & packaging de launch — structure de tiers, carte valeur-à-prix, échelle d'offres de launch, pricing beta avec chemin de graduation, termes de garantie. |
| sales-enablement-kit | A | Enablement interne — battle cards, talk track de vente, tableau de traitement des objections, FAQ interne + macros CS, annonce interne disciplinée par l'embargo. |
| ⛩ launch-readiness-auditor | preflight / execution / outcome | Gate RAMP typé pour une lecture de cycle de vie ; ne moyenne jamais les horizons temporels. Écrit `memory/audits/launch/`. |
| launch-day-conductor | M | Runbook de jour de launch par blocs horaires — check de gate des préconditions, verdicts de fenêtre d'observation après pushes irréversibles, échelle d'incidents P0–P3 + playbooks de rollback. |
| community-launch-runner | M | Packages de soumission par plateforme (Product Hunt, Show HN, subreddits, vagues d'annuaires, canaux régionaux/chinois) sous un check de ligne rouge de plateforme. |
| press-media-relations | M | Liste médias/analystes à trois tiers, timing de pitch avec embargo, brouillon de communiqué de presse en structure standard, plan de briefing analystes. |
| launch-monitor | P | Surveillance de fenêtre T-0→T+30 — vérification d'instrumentation (en amont de P1), polling rank/reviews/news, snapshots KPI D0/W1/M1, lectures spike-vs-sustain. |
| launch-feedback-synthesizer | P | Digest des thèmes de feedback, boucle de statut open→shipped (« you asked, we shipped »), récolte de social proof conforme. |
| launch-retro-analyzer | P | Rétro D1/W1/M1 — actual-vs-target par canal, 5-Whys sur le plus gros raté, décisions keep/kill/change, snapshot d'issue vers le registre. |
| momentum-planner | P | Plan de momentum T+1→T+30 — calendrier des moments de launch, routage de tier d'annonce, décision de légitimité de relaunch, prochain moment Tier-1. |

**Réutilisé entre disciplines** (compté dans leurs phases d'origine, non dupliqué) : `audience-mapper`, `trend-spotter`, `budget-optimizer`, `landing-optimizer`, `campaign-planner`, `outreach-manager`, `content-amplifier`, `email-creative-builder` / `email-sequence-designer` / `cold-outbound-sequencer`, `campaign-architect` / `ad-creative-builder`, `page-play-builder` / `content-writer`, `technical-seo-checker` / `serp-markup-builder`, `performance-monitor`, `keyword-research`, `entity-registry`, `offer-claims-registry`, `consent-registry`, `list-growth-designer`, `roi-calculator` / `performance-analyzer` / `report-generator` — voir [ramp-benchmark.md](../references/ramp-benchmark.md).

</details>

### Couche de protocole (8)

La machinerie partagée de vérité & de mémoire — voir [Architecture § La couche de protocole](#la-couche-de-protocole) pour les rôles et les règles d'écrivain unique.

| Groupe | Skills |
|-------|--------|
| **Protocole** | [entity-registry](../protocol/entity-registry/SKILL.md), [creator-registry](../protocol/creator-registry/SKILL.md), [offer-claims-registry](../protocol/offer-claims-registry/SKILL.md), [consent-registry](../protocol/consent-registry/SKILL.md), [launch-registry](../protocol/launch-registry/SKILL.md), [channel-registry](../protocol/channel-registry/SKILL.md), [narrative-registry](../protocol/narrative-registry/SKILL.md), [memory-management](../protocol/memory-management/SKILL.md) |

<details><summary><b>Objectif par skill (Protocole)</b></summary>

| Skill | Ce qu'il fait |
|-------|--------------|
| entity-registry | Profil d'entité canonique pour Knowledge Graph, Wikidata, désambiguïsation IA. |
| creator-registry | Roster/dossier canonique de créateurs — handles dédupliqués, stats d'audience étiquetées par provenance, tarifs et historique de conformité. |
| offer-claims-registry | Grand livre canonique d'offres & de substantiation de claims — l'enregistrement contre lequel les vérifications de claims O1/T2 sont jugées. |
| consent-registry | Enregistrement canonique de consentement/suppression par sujet — timestamp d'opt-in + base légale, preuve de double opt-in, historique append-only de désabo/bounce/plainte ; l'enregistrement contre lequel les vetos S2/N1 jugent. |
| launch-registry | Dossier canonique par launch + calendrier de launch — tier, type de launch, étape de cycle de vie à sens unique (draft→…→GA), dates faisant autorité + engagements d'embargo, grand livre de soumission par canal, snapshot d'issue ; le SSOT de vérité du launch. |
| channel-registry | Enregistrement canonique par canal — handles, propriété/autorisation, normes de plateforme, défauts de divulgation ; le SSOT de vérité du canal contre lequel le veto ECHO E1 de vérité de canal juge. |
| narrative-registry | Canon canonique de brand-narrative — narrative stratégique approuvée, système de messages, langage/lexique, proof points ; le SSOT du canon de marque contre lequel le veto TALE T1 de vérité juge. |
| memory-management | Réviser, promouvoir, rétrograder et archiver la mémoire de projet HOT/WARM/COLD. |

</details>

---

## Commandes

Huit commandes : `/aaron-marketing:auto` route n'importe quel objectif à travers les sept disciplines, et chaque discipline a exactement un point d'entrée explicite. Source : [commands/](../commands).

| Commande | Pour quoi | Restriction |
|---------|-----------|-----------|
| `/aaron-marketing:auto` | Décrivez n'importe quel objectif — infère l'intention et exécute le plus petit workflow utile | `--deep` (exhaustif / stress-test) |
| `/aaron-marketing:narrative` | Brand narrative (boucle TALE) : tracer l'histoire actuelle & la catégorie, architecturer la narrative stratégique & le système de messages, la faire atterrir à travers les canaux, le gate de qualité, résonance & dérive | `--phase trace\|architect\|land\|evaluate` |
| `/aaron-marketing:seo-geo` | SEO/GEO de bout en bout (boucle SITE) : sonder demande/concurrents, implémenter le contenu, affiner qualité/technique/on-page, évaluer autorité/classements/rapports/mémoire | `--phase survey\|implement\|tune\|evaluate` + flags par phase (`--competitors` `--map` · `--brief` `--series` `--refresh` `--publish` `--meta` `--schema` `--type` · `--full` `--tech` `--visibility` · `--authority` `--alert` `--report` `--remember` `--period`) |
| `/aaron-marketing:influencer` | Influence (boucle STAR) : insight d'audience, scouting & fit, targeting, outreach, amplification, reporting du ROI | `--phase scout\|target\|activate\|report` |
| `/aaron-marketing:ad` | Paid ads (boucle ROAS) : segments, structure, creative, conception d'expériences, le gate d'audit, mesure | `--phase research\|orchestrate\|activate\|scale` |
| `/aaron-marketing:email` | E-mail (boucle SEND) : deliverability/consent, segmentation, creative, flux de cycle de vie, monétisation, send-testing, le gate d'audit | `--phase setup\|engage\|nurture\|deliver` |
| `/aaron-marketing:launch` | Product launch (boucle RAMP) : positionnement, tier & fenêtre, message house & assets, le gate de readiness, déroulé du jour de launch, monitoring & rétro | `--phase research\|assemble\|mobilize\|prove` |
| `/aaron-marketing:social` | Organic social (boucle ECHO) : portfolio de canaux & voix, calendrier & creative, le gate de qualité, hosting d'engagement/crise, pulse & mesure | `--phase explore\|craft\|host\|observe` |

Le travail quotidien démarre normalement par `/aaron-marketing:auto` ; les sept autres sont des points d'entrée de discipline explicites, avec `--phase` pour restreindre l'étape.

---

## Connecteurs & paliers d'amélioration

Les skills nomment les outils avec des marqueurs `~~category` (`~~SEO tool`, `~~web analytics`, `~~ad platform`, `~~email platform`, …) au lieu de fournisseurs spécifiques, et chaque catégorie a un **chemin keyless de Tier 1**. Les recettes complètes — y compris l'endpoint gratuit/de première partie de chaque catégorie — sont dans [CONNECTORS.md](../CONNECTORS.md).

### La couche de connecteurs est un produit en soi

**Plus de 100 chemins d'intégration documentés** sur trois couches conçues — et chacun mérite sa place :

| Couche | Ce que vous obtenez |
|-------|--------------|
| **28 connecteurs embarqués sans dépendances** | Python bibliothèque standard pur — pas de `pip`, pas d'étape de build. SERP live keyless + scraping rendu par JS (Firecrawl, Tavily), une sonde de citation de réponses IA, extractions d'email-auth par DNS-over-HTTPS, séries d'attention Wikipedia, mentions news GDELT, vraies métriques de créateurs YouTube, push IndexNow + Baidu, automatisation ESP Resend, et un grand livre de mesure diffable par git qui transforme chacun d'eux en série temporelle avant/après. |
| **Plus de 60 API officielles/gratuites documentées** | Chaque ligne lie la **documentation officielle** du fournisseur, porte une date de vérification, et chaque lien est vérifié par HTTP avant publication. Inclut les chemins que la plupart des listes d'outils manquent : GSC URL Inspection, CrUX History (40 semaines de CWV terrain), la Gmail Postmaster Tools API, l'Ad Library de Meta, la Data Export API de Microsoft Clarity. |
| **Serveurs MCP de fournisseurs** | 18 endpoints distants catalogués (jamais auto-enregistrés — votre liste `/mcp` reste propre) plus les serveurs officiels auto-hébergés pour Google Analytics, Search Console, **Google Ads** et **Microsoft Clarity**. Deux MCP distants fonctionnent sans aucune clé (Firecrawl, Tavily). |

Ce qui les rend fiables plutôt que simplement nombreux :

- **Trois classes de sécurité, des gates conçus** ([SECURITY.md](../SECURITY.md)) : les fetchers hébergés exécutent un **pré-flight local de robots.txt** avant chaque fetch délégué et refusent sur Disallow ; tout ce qui mute un état externe (envois d'e-mail, pushes d'index) est **dry-run par défaut** derrière un flag `--live` explicite, avec des clés d'idempotence là où le fournisseur les supporte et pas d'auto-retry là où non.
- **Vérifié, puis re-vérifié** : les endpoints sont contrôlés contre la documentation primaire du fournisseur avec dates, les chemins keyless sont testés en live, un guard de CI impose le sync version/tracking, et un smoke live pré-release attrape la dérive d'endpoints (il a déjà attrapé de vrais changements d'API — deux fois).
- **Des faits, pas des verdicts** : les connecteurs rapportent la présence d'enregistrements, les tags parsés et les séries brutes ; les gates d'auditeur font le jugement, et les skills étiquettent chaque nombre **Measured / User-provided / Estimated**.
- **Un playbook écrit** ([docs/connector-playbook.md](connector-playbook.md)) gouverne chaque ajout — qualifier, vérifier, implémenter, tester, câbler, documenter, tracker, régresser, consigner — pour que la qualité tienne à mesure que le catalogue grandit.

| Palier | Requiert | Ce que vous obtenez |
|------|----------|---------|
| **Tier 1** (par défaut) | Rien | Collez des données, ou tirez-les de sources gratuites/publiques. Le framework d'analyse complet tourne quoi qu'il arrive. |
| **Tier 2** | Une API ou MCP gratuite de première partie | Récupération automatique de vos propres données GSC / GA4 / Core Web Vitals. |
| **Tier 3** | Un set MCP plus complet | Workflows multi-sources entièrement automatisés. |

- **Helpers embarqués sans dépendances** sous `scripts/connectors/` (Python bibliothèque standard uniquement) tirent des données publiques/propres localement — p. ex. PageSpeed/CrUX, Open PageRank, crawl de page, Wayback CDX, Wikidata SPARQL, Common Crawl, recettes advertools — plus **`resend.py`**, automatisation directe de l'ESP Resend pour les skills e-mail (clé free-tier : statut d'auth de domaine, seed-test sends, sync de suppression, planification de broadcasts ; les sous-commandes qui mutent sont dry-run par défaut et requièrent `--live`), et **`firecrawl.py`** + **`tavily.py`**, automatisation de fetchers hébergés keyless pour les skills research (Firecrawl : SERP web live + markdown de page rendue par JS + site maps ; Tavily : recherche notée + sonde de sources citées d'un moteur de réponses IA pour GEO + extraction d'URL — les deux gratuits sans aucune clé, les deux avec un pré-flight local de robots.txt intégré).
- **Sources gratuites/keyless** documentées par catégorie : Google Search Console & GA4 (données propres), PageSpeed/CrUX, Wikidata, Common Crawl, Open PageRank, SERP/scrape keyless Firecrawl, AI-search keyless Tavily, enregistrements d'email-auth par DNS-over-HTTPS (`doh.py`), séries d'attention Wikipedia (`pageviews.py`), mentions news GDELT (`gdelt.py`), métriques de créateurs YouTube sur clé gratuite (`youtube.py`), push IndexNow + Baidu (`indexpush.py`, sous gate dry-run), les bibliothèques d'ad-transparency (Meta/Google/TikTok), et des lignes de recette pour crt.sh, le validateur W3C, oEmbed et HN Algolia.
- **Serveurs MCP opt-in** (Ahrefs, Semrush, SE Ranking, SISTRIX, SimilarWeb, la suite gratuite auto-hébergée **OpenSEO**, Cloudflare, Vercel, HubSpot, Amplitude, Notion, Webflow, Sanity, Contentful, Slack, Resend, les keyless Firecrawl et Tavily) sont catalogués dans [`docs/mcp-catalog.json`](mcp-catalog.json) comme **référence à copier-coller uniquement** — le catalogue se situe hors du chemin `.mcp.json` de la racine du plugin auto-enregistré, si bien que rien n'est enregistré pour vous. Copiez les entrées voulues dans votre propre config MCP.

Les skills paid ads notent à partir de votre **export manuel de votre propre compte** (CSV du gestionnaire d'annonces natif, GA4, ecommerce). Les API de plateforme publicitaire à clé (Google Ads SDK, Meta Marketing API) sont opt-in Tier-2/3 uniquement et **jamais** un prérequis de Tier 1. Les skills e-mail notent de même — à partir de votre **propre export ESP** — et chaque signal de deliverability est keyless (lookups DNS, un rapport DMARC RUA et un test d'inbox par seed-list), si bien qu'une API ESP à clé n'est jamais non plus un prérequis de Tier 1 ; quand Resend est votre ESP, le `resend.py` embarqué automatise la même boucle sur le free-tier.

---

## Workflows recommandés

La plupart des objectifs réels traversent plusieurs disciplines. `/aaron-marketing:auto` route un objectif en langage naturel vers la chaîne minimale utile parmi les sept — un lancement produit mobilise par exemple Launch, Email, Social et Paid à la fois :

```text
/aaron-marketing:auto lancer notre v2 sur Product Hunt dans 3 semaines — 1 200 inscrits en liste d'attente ; il nous faut la page, les e-mails et le plan du jour J
```

Ou dérouler la boucle d'une discipline de bout en bout (le guide `README.md` de chaque répertoire de discipline ajoute des plays par scénario) :

**Narrative (boucle TALE)**
1. **Trace** — `narrative-baseline-mapper` → `category-narrative-mapper` → `audience-belief-mapper` → `positioning-truth-tracer`
2. **Architect** — `strategic-narrative-designer` → `message-system-architect` → `brand-language-codifier` → `story-bank-builder`
3. **Land** — `narrative-cascade-planner` → `pitch-narrative-builder` → `narrative-enablement-kit` → `proof-point-packager`
4. **Evaluate** — `narrative-quality-auditor` (⛩ porte TALE) → `message-test-designer` → `narrative-resonance-monitor` → `narrative-drift-monitor`

**SEO/GEO (boucle SITE)**
1. **Survey** — `keyword-research` → `competitor-analysis` → `content-gap-analysis`
2. **Implement** — `content-writer` → `geo-content-optimizer` → `serp-markup-builder` / `page-play-builder`
3. **Tune** — `content-quality-auditor` (⛩ porte de publication) → `on-page-seo-checker` → `technical-seo-checker` → `site-structure-optimizer`
4. **Evaluate** — `rank-tracker` → `performance-monitor` → `offsite-signal-analyzer` ; revue de confiance avec `domain-authority-auditor` (⛩)

**Social (boucle ECHO)**
1. **Explore** — `channel-portfolio-planner` → `voice-dossier-builder` → `platform-norm-profiler` → `participation-warmup-planner`
2. **Craft** — `social-calendar-builder` → `social-creative-builder` → `short-video-scripter` → `advocacy-program-designer`
3. **Host** — `social-quality-auditor` (⛩ porte ECHO) → `engagement-inbox-manager` → `social-selling-planner` → `crisis-response-planner`
4. **Observe** — `social-pulse-monitor` → `share-of-voice-tracker` → `dark-social-attributor` → `social-measurement-loop`

**Email (boucle SEND)**
1. **Setup** — `deliverability-qa` → `list-segment-builder`
2. **Engage** — `email-creative-builder`
3. **Nurture** — `email-sequence-designer` → `newsletter-monetization-planner`
4. **Deliver** — `send-experiment-designer` → `email-quality-auditor` (⛩ porte EQS) avant tout envoi

**Paid Ads (boucle ROAS)**
1. **Research** — `audience-segment-builder` → `campaign-architect`
2. **Orchestrate** — `ad-creative-builder` → `ad-test-designer` (+ `landing-optimizer` pour la page)
3. **Activate** — `conversion-signal-qa` → `ad-account-auditor` (⛩ porte RQS) avant toute mise en ligne de budget
4. **Scale** — `paid-measurement-loop` → `attribution-reconciler` → `roi-calculator` → `report-generator`

**Influence (boucle STAR)**
1. **Scout** — `audience-mapper` → `trend-spotter` → `influencer-discovery` → `fit-scorer` (STAR Suitability)
2. **Target** — `competitor-tracker` → `campaign-planner` → `brief-generator` → `budget-optimizer`
3. **Activate** — `outreach-manager` → `creator-content-auditor` (⛩ porte STAR) → `contract-helper` → `content-amplifier`
4. **Report** — `landing-optimizer` → `performance-analyzer` → `roi-calculator` → `report-generator`

**Launch (boucle RAMP)**
1. **Research** — `positioning-mapper` → `launch-tier-planner` → `launch-window-planner` → `early-access-designer`
2. **Assemble** — `message-house-builder` → `launch-asset-packager` → `pricing-packaging-planner` → `sales-enablement-kit`
3. **Mobilize** — `launch-readiness-auditor` (⛩ porte RAMP) → `launch-day-conductor` → `community-launch-runner` → `press-media-relations`
4. **Prove** — `launch-monitor` → `launch-feedback-synthesizer` → `launch-retro-analyzer` → `momentum-planner`

Pour une revue de confiance complète, associez `content-quality-auditor` à `domain-authority-auditor` pour une évaluation combinée de 120 items. Avec `memory-management` actif, les passages de main et les boucles ouvertes persistent automatiquement dans la mémoire HOT/WARM/COLD.

---

## Structure du dépôt

```
narrative/{trace,architect,land,evaluate}/                  # Narrative — TALE (16, incl. son gate)
seo-geo/{survey,implement,tune,evaluate}/                   # SEO/GEO (16, incl. ses 2 gates)
influencer/{scout,target,activate,report}/                     # Influence (16, incl. son gate)
ad/research|orchestrate|activate|scale/            # Paid Ads — ROAS (16, incl. son gate)
email/setup|engage|nurture|deliver/                  # Email — SEND (16, incl. son gate)
launch/research|assemble|mobilize|prove/             # Launch — RAMP (16, incl. son gate)
social/explore|craft|host|observe/                   # Social — ECHO (16, incl. son gate)
protocol/                                            # Couche de protocole (8) — registres de vérité + mémoire
commands/        # 8 commandes slash (auto, narrative, seo-geo, influencer, ad, email, launch, social)
references/      # contrat partagé, modèle d'état, les 8 benchmarks, auditor runbook, packs de plateforme
evals/           # cas d'eval structurels par skill + structure-manifest.json
hooks/           # hooks.json + claude-hook.sh (la seule logique de runtime)
scripts/         # validate-skill.sh + connectors/ (stdlib) + guards de CI
memory/          # échafaudage HOT/WARM/COLD + stockages de registre (entities/creators/claims/consent/launch/channels/narrative-registry)
docs/            # READMEs localisés (zh)
.claude-plugin/  # plugin.json + miroir marketplace.json
```

---

## Philosophie de conception

- **Les skills sont du contenu.** Le seul code est le validateur Bash, l'exécuteur de hooks Bash et des helpers de connecteur/vérification de la bibliothèque standard Python sans dépendances. Jamais de dépendances tierces / `pip` — imposé par un guard de dependency-creep.
- **Keyless d'abord.** Chaque `~~category` a une recette gratuite/de données propres ; MCP et les outils payants sont pur confort.
- **Chirurgical & MECE.** Chaque skill possède une tâche avec une frontière de portée nette ; le travail qui se recoupe est livré comme un *mode* d'un skill existant plutôt qu'un nouveau skill mince. Les registres curatent, les gates jugent, les analyseurs alimentent les gates.
- **Pas de chiffres inventés.** Les skills étiquettent chaque chiffre Measured / User-provided / Estimated et embarquent un détecteur de jargon d'IA / phrases bannies.
- **La conformité est un guide, pas une loi.** Les vérifications de divulgation FTC et d'intégrité de claims signalent le risque ; elles ne sont pas un conseil juridique.

---

## Contrôles qualité (CI)

Chaque changement est exécuté contre un ensemble de guards fail-closed (tous dans `scripts/` et `tests/`) :

| Guard | Vérifie |
|-------|--------|
| `validate-skill.sh` | Frontmatter, sections requises, cohérence de version, liens plugin-relatifs sur les 120 skills. |
| `golden-auditor-math.py` | Somme de poids déterministe + arithmétique des exemples travaillés pour les **huit** frameworks. |
| `check-evals.py` | Lint structurel d'eval + `structure-manifest.json` (120/120 skills portent des cas d'eval). |
| `check-pii.py` | Bloque secrets / PII commités (allowlist au niveau token, fail-closed). |
| `check-stdlib-only.sh` | Guard de dependency-creep + la ligne rouge API à clé de Paid Ads. |
| `check-versions.sh` | Guard de synchronisation des versions : le catalogue système, les manifestes plugin/marketplace/OpenClaw, les badges du README racine et localisés, AGENTS/CLAUDE/VERSIONS, le About GitHub et les 120 versions de skills restent alignés. |
| `tests/test_connectors_local.py` | Tests offline des constructeurs de requête et parseurs couvrant les 29 modules de connecteurs fournis (pas de réseau en CI). |
| `tests/test_hook_artifact_gate.sh` | Tests de comportement de l'Artifact Gate du hook + assainissement SessionStart. |

La dérive d'endpoints en live est échantillonnée séparément par le **manuel** [`scripts/connectors/smoke-live.sh`](../scripts/connectors/smoke-live.sh) — un appel réel minimal par connecteur hébergé listé dans ce script, avec assertions de forme (les réponses de rate-limit comptent comme SKIP) ; exécutez-le avant un release, jamais en CI.

---

## Contribuer & docs du projet

- **[CONTRIBUTING.md](../CONTRIBUTING.md)** — règles d'authoring, la checklist de contribution et la liste autoritaire des 10 surfaces de tracking.
<!-- GENERATED:BEGIN release-surface:current-bundle -->
- **[VERSIONS.md](../VERSIONS.md)** — versions par skill + changelog (bundle actuel : `19.2.0`).
<!-- GENERATED:END release-surface:current-bundle -->
- **[SECURITY.md](../SECURITY.md)** · **[PRIVACY.md](../PRIVACY.md)** · **[CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)** — politique de sécurité, de confidentialité et de communauté.
- **[CLAUDE.md](../CLAUDE.md)** / **[AGENTS.md](../AGENTS.md)** — contexte côté agent pour ce repo.

---

## Avertissement

Ces skills assistent les workflows brand-narrative, SEO/GEO, influence-marketing, paid-ads, e-mail-marketing, product-launch et organic-social mais ne **garantissent pas** les classements, citations IA, trafic, engagement, conversions, ROAS, deliverability ou résultats business. Les vérifications de conformité influence, ads, e-mail et social (divulgation FTC, intégrité des claims, policy de plateforme, consentement/opt-in, divulgation de connexion matérielle) sont un guide, pas un conseil juridique. Vérifiez les recommandations avec des professionnels qualifiés avant de vous y fier pour des décisions majeures de stratégie, financières ou juridiques.

## Licence

Apache License 2.0 — voir [LICENSE](../LICENSE).

*Dernière synchronisation avec le README anglais : v18.0.0*

## Star History

<a href="https://www.star-history.com/?repos=aaron-he-zhu%2Faaron-marketing-skills&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=aaron-he-zhu/aaron-marketing-skills&type=date&legend=top-left" />
 </picture>
</a>
