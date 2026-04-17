# Biblioteca de Skills SEO & GEO

**20 skills. 12 comandos. Posiciónate en buscadores. Sé citado por IA.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-8.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **Español** | [Português](README.pt.md)

Skills y comandos de Claude para Optimización de Motores de Búsqueda (SEO) y Optimización de Motores Generativos (GEO). Sin dependencias. Compatible con [Claude Code](https://claude.ai/download), [Cursor](https://cursor.com), [Codex](https://openai.com/codex) y [más de 35 agentes](https://skills.sh). Calidad de contenido evaluada por [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 items). Autoridad de dominio evaluada por [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating) (40 items).

> **SEO** te posiciona en los resultados de búsqueda. **GEO** hace que los sistemas de IA (ChatGPT, Perplexity, Google AI Overviews) te citen. Esta biblioteca cubre ambos.

¿No conoces la terminología? Consulta [GLOSSARY.md](../GLOSSARY.md).

### Por qué esta biblioteca

- **120 items de evaluación** — CORE-EEAT (80 items) + CITE (40 items) con puertas de veto
- **8 idiomas, 750+ triggers** — ES, EN, ZH, JA, KO, PT con variantes formales, coloquiales y errores tipográficos
- **Sin dependencias** — skills en Markdown puro, sin Python, sin entorno virtual, sin claves API
- **Agnóstico de herramientas** — funciona solo o con 14 servidores MCP (Ahrefs, Semrush, Cloudflare y más)
- **6 métodos de instalación** — ClawHub, skills.sh, plugin Claude Code, git submodule, fork, manual

## Inicio rápido

```bash
# Instalar los 20 skills (skills.sh)
npx skills add aaron-he-zhu/seo-geo-claude-skills

# Instalar un skill individual
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research

# Instalar via plugin Claude Code
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
```

Después de instalar, usa directamente:
```
Investiga palabras clave para "marketing digital" e identifica oportunidades
```

O ejecuta un comando:
```
/seo:audit-page https://example.com
```

## Skills

### Investigación

| Skill | Función |
|-------|---------|
| `keyword-research` | Descubrimiento de keywords, análisis de intención, dificultad, clustering |
| `competitor-analysis` | Análisis de estrategias SEO/GEO de competidores |
| `serp-analysis` | Análisis de resultados de búsqueda y patrones de respuesta IA |
| `content-gap-analysis` | Oportunidades de contenido que los competidores cubren pero tú no |

### Construcción

| Skill | Función |
|-------|---------|
| `seo-content-writer` | Redacción de contenido optimizado para búsqueda |
| `geo-content-optimizer` | Optimización para ser citado por sistemas de IA |
| `meta-tags-optimizer` | Optimización de títulos, descripciones y etiquetas OG |
| `schema-markup-generator` | Generación de datos estructurados JSON-LD |

### Optimización

| Skill | Función |
|-------|---------|
| `on-page-seo-auditor` | Auditoría SEO on-page con informe puntuado |
| `technical-seo-checker` | Rastreabilidad, indexación, Core Web Vitals |
| `internal-linking-optimizer` | Optimización de estructura de enlaces internos |
| `content-refresher` | Actualización de contenido obsoleto para recuperar rankings |

### Monitoreo

| Skill | Función |
|-------|---------|
| `rank-tracker` | Seguimiento de posiciones de keywords en búsqueda y IA |
| `backlink-analyzer` | Análisis de perfil de backlinks y detección de enlaces tóxicos |
| `performance-reporter` | Generación de informes de rendimiento SEO/GEO |
| `alert-manager` | Alertas de caída de rankings, cambios de tráfico, problemas técnicos |

### Capa de protocolo

| Skill | Función |
|-------|---------|
| `content-quality-auditor` | Auditoría CORE-EEAT de 80 items |
| `domain-authority-auditor` | Auditoría CITE de 40 items |
| `entity-optimizer` | Optimización de grafo de conocimiento de marca/entidad |
| `memory-management` | Persistencia de contexto entre sesiones |

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/seo:audit-page <URL>` | Auditoría SEO + CORE-EEAT de página |
| `/seo:check-technical <URL>` | Chequeo de salud técnica SEO |
| `/seo:generate-schema <type>` | Generación de datos estructurados JSON-LD |
| `/seo:optimize-meta <URL>` | Optimización de título, descripción y OG |
| `/seo:report <domain> <period>` | Informe integral de rendimiento SEO/GEO |
| `/seo:audit-domain <domain>` | Auditoría de autoridad de dominio CITE |
| `/seo:write-content <topic>` | Redacción de contenido optimizado SEO + GEO |
| `/seo:keyword-research <seed>` | Investigación y análisis de keywords |
| `/seo:setup-alert <metric>` | Configuración de alertas de monitoreo |

## Contribuir

Las contribuciones son bienvenidas. Consulta [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md).

## Licencia

Apache License 2.0

*Última sincronización con README en inglés: v7.0.0*
