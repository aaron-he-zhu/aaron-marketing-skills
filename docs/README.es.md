# Biblioteca de Skills SEO & GEO

**20 skills. 9 comandos. Posicionate en buscadores. Se citado por IA.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-8.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **Espanol** | [Portugues](README.pt.md)

Skills y comandos de Claude para Optimizacion de Motores de Busqueda (SEO) y Optimizacion de Motores Generativos (GEO). Sin dependencias. Instalacion nativa en [Claude Code](https://claude.ai/download), [OpenClaw](https://openclaw.com), [Gemini CLI](https://geminicli.com), [Qwen Code](https://qwenlm.github.io/qwen-code-docs/), [Amp](https://ampcode.com), [Kimi](https://moonshotai.github.io/kimi-cli/), [CodeBuddy](https://codebuddy.ai). [Mas de 35 agentes adicionales](https://github.com/vercel-labs/skills#supported-agents) via `npx skills`. Calidad de contenido evaluada por [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 items). Autoridad de dominio evaluada por [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating) (40 items).

> **SEO** te posiciona en los resultados de busqueda. **GEO** hace que los sistemas de IA (ChatGPT, Perplexity, Google AI Overviews) te citen. Esta biblioteca cubre ambos.

### Por que esta biblioteca

- **120 items de evaluacion** — CORE-EEAT (80 items) + CITE (40 items) con puertas de veto
- **8 idiomas, 750+ triggers** — ES, EN, ZH, JA, KO, PT con variantes formales, coloquiales y errores tipograficos
- **Sin dependencias** — skills en Markdown puro, sin Python, sin entorno virtual, sin claves API
- **Agnostico de herramientas** — funciona solo o con 14 servidores MCP (Ahrefs, Semrush, Cloudflare y mas)
- **Instalacion nativa en 7 agentes** — Claude Code, OpenClaw, Gemini CLI, Qwen Code, Amp, Kimi, CodeBuddy — mas de 35 agentes adicionales via `npx skills`

## Inicio rapido

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

# CodeBuddy (en la app, 2 pasos)
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
/plugin install aaron-seo-geo

# Alternativa universal (Cursor, Codex, opencode, Windsurf, Copilot y 35+ agentes)
npx skills add aaron-he-zhu/seo-geo-claude-skills

# Solo un skill individual
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research
```

Despues de instalar, usa directamente:
```
Investiga palabras clave para "marketing digital" e identifica oportunidades
```

O ejecuta un comando:
```
/seo:audit-page https://example.com
```

## Skills

### Investigacion

| Skill | Funcion |
|-------|---------|
| `keyword-research` | Descubrimiento de keywords, analisis de intencion, dificultad, clustering |
| `competitor-analysis` | Analisis de estrategias SEO/GEO de competidores |
| `serp-analysis` | Analisis de resultados de busqueda y patrones de respuesta IA |
| `content-gap-analysis` | Oportunidades de contenido que los competidores cubren pero tu no |

### Construccion

| Skill | Funcion |
|-------|---------|
| `seo-content-writer` | Redaccion de contenido optimizado para busqueda |
| `geo-content-optimizer` | Optimizacion para ser citado por sistemas de IA |
| `meta-tags-optimizer` | Optimizacion de titulos, descripciones y etiquetas OG |
| `schema-markup-generator` | Generacion de datos estructurados JSON-LD |

### Optimizacion

| Skill | Funcion |
|-------|---------|
| `on-page-seo-auditor` | Auditoria SEO on-page con informe puntuado |
| `technical-seo-checker` | Rastreabilidad, indexacion, Core Web Vitals |
| `internal-linking-optimizer` | Optimizacion de estructura de enlaces internos |
| `content-refresher` | Actualizacion de contenido obsoleto para recuperar rankings |

### Monitoreo

| Skill | Funcion |
|-------|---------|
| `rank-tracker` | Seguimiento de posiciones de keywords en busqueda y IA |
| `backlink-analyzer` | Analisis de perfil de backlinks y deteccion de enlaces toxicos |
| `performance-reporter` | Generacion de informes de rendimiento SEO/GEO |
| `alert-manager` | Alertas de caida de rankings, cambios de trafico, problemas tecnicos |

### Capa de protocolo

| Skill | Funcion |
|-------|---------|
| `content-quality-auditor` | Auditoria CORE-EEAT de 80 items |
| `domain-authority-auditor` | Auditoria CITE de 40 items |
| `entity-optimizer` | Optimizacion de grafo de conocimiento de marca/entidad |
| `memory-management` | Persistencia de contexto entre sesiones |

## Comandos

| Comando | Descripcion |
|---------|-------------|
| `/seo:audit-page <URL>` | Auditoria SEO + CORE-EEAT de pagina |
| `/seo:check-technical <URL>` | Chequeo de salud tecnica SEO |
| `/seo:generate-schema <type>` | Generacion de datos estructurados JSON-LD |
| `/seo:optimize-meta <URL>` | Optimizacion de titulo, descripcion y OG |
| `/seo:report <domain> <period>` | Informe integral de rendimiento SEO/GEO |
| `/seo:audit-domain <domain>` | Auditoria de autoridad de dominio CITE |
| `/seo:write-content <topic>` | Redaccion de contenido optimizado SEO + GEO |
| `/seo:keyword-research <seed>` | Investigacion y analisis de keywords |
| `/seo:setup-alert <metric>` | Configuracion de alertas de monitoreo |

## Contribuir

Las contribuciones son bienvenidas. Consulta [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md).

## Licencia

Apache License 2.0

*Ultima sincronizacion con README en ingles: v7.0.0*
