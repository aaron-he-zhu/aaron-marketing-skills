# Biblioteca de Skills SEO & GEO

**20 skills. 9 comandos. Ranqueie nas buscas. Seja citado por IA.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-8.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Espanol](README.es.md) | **Portugues**

Skills e comandos Claude para Otimizacao de Mecanismos de Busca (SEO) e Otimizacao de Mecanismos Generativos (GEO). Zero dependencias. Instalacao nativa em [Claude Code](https://claude.ai/download), [OpenClaw](https://openclaw.com), [Gemini CLI](https://geminicli.com), [Qwen Code](https://qwenlm.github.io/qwen-code-docs/), [Amp](https://ampcode.com), [Kimi](https://moonshotai.github.io/kimi-cli/), [CodeBuddy](https://codebuddy.ai). [Mais de 35 agentes adicionais](https://github.com/vercel-labs/skills#supported-agents) via `npx skills`. Qualidade de conteudo avaliada pelo [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 itens). Autoridade de dominio avaliada pelo [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating) (40 itens).

> **SEO** posiciona voce nos resultados de busca. **GEO** faz com que sistemas de IA (ChatGPT, Perplexity, Google AI Overviews) citem voce. Esta biblioteca cobre ambos.

### Por que esta biblioteca

- **120 itens de avaliacao** — CORE-EEAT (80 itens) + CITE (40 itens) com portoes de veto
- **8 idiomas, 750+ gatilhos** — PT, EN, ZH, JA, KO, ES com variantes formais, coloquiais e erros de digitacao
- **Zero dependencias** — skills em Markdown puro, sem Python, sem ambiente virtual, sem chaves de API
- **Agnostico de ferramentas** — funciona sozinho ou com 14 servidores MCP (Ahrefs, Semrush, Cloudflare e mais)
- **Instalacao nativa em 7 agentes** — Claude Code, OpenClaw, Gemini CLI, Qwen Code, Amp, Kimi, CodeBuddy — mais de 35 agentes adicionais via `npx skills`

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

# CodeBuddy (no app, 2 passos)
/plugin marketplace add aaron-he-zhu/seo-geo-claude-skills
/plugin install aaron-seo-geo

# Alternativa universal (Cursor, Codex, opencode, Windsurf, Copilot e 35+ agentes)
npx skills add aaron-he-zhu/seo-geo-claude-skills

# Apenas um skill individual
npx skills add aaron-he-zhu/seo-geo-claude-skills -s keyword-research
```

Apos instalar, use diretamente:
```
Pesquise palavras-chave para "marketing digital" e identifique oportunidades
```

Ou execute um comando:
```
/seo:audit-page https://example.com
```

## Skills

### Pesquisa

| Skill | Funcao |
|-------|--------|
| `keyword-research` | Descoberta de keywords, analise de intencao, dificuldade, clustering |
| `competitor-analysis` | Analise de estrategias SEO/GEO dos concorrentes |
| `serp-analysis` | Analise de resultados de busca e padroes de resposta IA |
| `content-gap-analysis` | Oportunidades de conteudo que concorrentes cobrem mas voce nao |

### Construcao

| Skill | Funcao |
|-------|--------|
| `seo-content-writer` | Redacao de conteudo otimizado para busca |
| `geo-content-optimizer` | Otimizacao para ser citado por sistemas de IA |
| `meta-tags-optimizer` | Otimizacao de titulos, descricoes e tags OG |
| `schema-markup-generator` | Geracao de dados estruturados JSON-LD |

### Otimizacao

| Skill | Funcao |
|-------|--------|
| `on-page-seo-auditor` | Auditoria SEO on-page com relatorio pontuado |
| `technical-seo-checker` | Rastreabilidade, indexacao, Core Web Vitals |
| `internal-linking-optimizer` | Otimizacao da estrutura de links internos |
| `content-refresher` | Atualizacao de conteudo desatualizado para recuperar rankings |

### Monitoramento

| Skill | Funcao |
|-------|--------|
| `rank-tracker` | Acompanhamento de posicoes de keywords em busca e IA |
| `backlink-analyzer` | Analise de perfil de backlinks e deteccao de links toxicos |
| `performance-reporter` | Geracao de relatorios de desempenho SEO/GEO |
| `alert-manager` | Alertas de queda de rankings, mudancas de trafego, problemas tecnicos |

### Camada de protocolo

| Skill | Funcao |
|-------|--------|
| `content-quality-auditor` | Auditoria CORE-EEAT de 80 itens |
| `domain-authority-auditor` | Auditoria CITE de 40 itens |
| `entity-optimizer` | Otimizacao do grafo de conhecimento de marca/entidade |
| `memory-management` | Persistencia de contexto entre sessoes |

## Comandos

| Comando | Descricao |
|---------|-----------|
| `/seo:audit-page <URL>` | Auditoria SEO + CORE-EEAT de pagina |
| `/seo:check-technical <URL>` | Verificacao de saude tecnica SEO |
| `/seo:generate-schema <type>` | Geracao de dados estruturados JSON-LD |
| `/seo:optimize-meta <URL>` | Otimizacao de titulo, descricao e OG |
| `/seo:report <domain> <period>` | Relatorio integral de desempenho SEO/GEO |
| `/seo:audit-domain <domain>` | Auditoria de autoridade de dominio CITE |
| `/seo:write-content <topic>` | Redacao de conteudo otimizado SEO + GEO |
| `/seo:keyword-research <seed>` | Pesquisa e analise de keywords |
| `/seo:setup-alert <metric>` | Configuracao de alertas de monitoramento |

## Contribuir

Contribuicoes sao bem-vindas! Consulte [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md).

## Licenca

Apache License 2.0

*Ultima sincronizacao com README em ingles: v7.0.0*
