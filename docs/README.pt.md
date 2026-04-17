# Biblioteca de Skills SEO & GEO

**20 skills. 15 comandos. Ranqueie nas buscas. Seja citado por IA.**

[![GitHub Stars](https://img.shields.io/github/stars/aaron-he-zhu/seo-geo-claude-skills?style=flat)](https://github.com/aaron-he-zhu/seo-geo-claude-skills)
[![Version](https://img.shields.io/badge/version-9.0.0-orange)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/VERSIONS.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-green)](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/LICENSE)

[English](../README.md) | [中文](README.zh.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Español](README.es.md) | **Português**

Skills e comandos Claude para Otimização de Mecanismos de Busca (SEO) e Otimização de Mecanismos Generativos (GEO). Zero dependências. Instalação nativa em [Claude Code](https://claude.ai/download), [OpenClaw](https://openclaw.com), [Gemini CLI](https://geminicli.com), [Qwen Code](https://qwenlm.github.io/qwen-code-docs/), [Amp](https://ampcode.com), [Kimi](https://moonshotai.github.io/kimi-cli/), [CodeBuddy](https://codebuddy.ai). [Mais de 35 agentes adicionais](https://github.com/vercel-labs/skills#supported-agents) via `npx skills`. Qualidade de conteúdo avaliada pelo [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/core-eeat-content-benchmark) (80 itens). Autoridade de domínio avaliada pelo [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating) (40 itens).

> **SEO** posiciona você nos resultados de busca. **GEO** faz com que sistemas de IA (ChatGPT, Perplexity, Google AI Overviews) citem você. Esta biblioteca cobre ambos.

Não conhece a terminologia? Consulte [GLOSSARY.md](../GLOSSARY.md).

### Por que esta biblioteca

- **120 itens de avaliação** — CORE-EEAT (80 itens) + CITE (40 itens) com portões de veto
- **8 idiomas, 750+ gatilhos** — PT, EN, ZH, JA, KO, ES com variantes formais, coloquiais e erros de digitação
- **Zero dependências** — skills em Markdown puro, sem Python, sem ambiente virtual, sem chaves de API
- **Agnóstico de ferramentas** — funciona sozinho ou com 14 servidores MCP (Ahrefs, Semrush, Cloudflare e mais)
- **Instalação nativa em 7 agentes** — Claude Code, OpenClaw, Gemini CLI, Qwen Code, Amp, Kimi, CodeBuddy — mais de 35 agentes adicionais via `npx skills`

## Início rápido

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

Após instalar, use diretamente:
```
Pesquise palavras-chave para "marketing digital" e identifique oportunidades
```

Ou execute um comando:
```
/seo:audit-page https://example.com
```

## Skills

### Pesquisa

| Skill | Função |
|-------|--------|
| `keyword-research` | Descoberta de keywords, análise de intenção, dificuldade, clustering |
| `competitor-analysis` | Análise de estratégias SEO/GEO dos concorrentes |
| `serp-analysis` | Análise de resultados de busca e padrões de resposta IA |
| `content-gap-analysis` | Oportunidades de conteúdo que concorrentes cobrem mas você não |

### Construção

| Skill | Função |
|-------|--------|
| `seo-content-writer` | Redação de conteúdo otimizado para busca |
| `geo-content-optimizer` | Otimização para ser citado por sistemas de IA |
| `meta-tags-optimizer` | Otimização de títulos, descrições e tags OG |
| `schema-markup-generator` | Geração de dados estruturados JSON-LD |

### Otimização

| Skill | Função |
|-------|--------|
| `on-page-seo-auditor` | Auditoria SEO on-page com relatório pontuado |
| `technical-seo-checker` | Rastreabilidade, indexação, Core Web Vitals |
| `internal-linking-optimizer` | Otimização da estrutura de links internos |
| `content-refresher` | Atualização de conteúdo desatualizado para recuperar rankings |

### Monitoramento

| Skill | Função |
|-------|--------|
| `rank-tracker` | Acompanhamento de posições de keywords em busca e IA |
| `backlink-analyzer` | Análise de perfil de backlinks e detecção de links tóxicos |
| `performance-reporter` | Geração de relatórios de desempenho SEO/GEO |
| `alert-manager` | Alertas de queda de rankings, mudanças de tráfego, problemas técnicos |

### Camada de protocolo

| Skill | Função |
|-------|--------|
| `content-quality-auditor` | Auditoria CORE-EEAT de 80 itens |
| `domain-authority-auditor` | Auditoria CITE de 40 itens |
| `entity-optimizer` | Otimização do grafo de conhecimento de marca/entidade |
| `memory-management` | Persistência de contexto entre sessões |

## Comandos

| Comando | Descrição |
|---------|-----------|
| `/seo:audit-page <URL>` | Auditoria SEO + CORE-EEAT de página |
| `/seo:check-technical <URL>` | Verificação de saúde técnica SEO |
| `/seo:generate-schema <type>` | Geração de dados estruturados JSON-LD |
| `/seo:optimize-meta <URL>` | Otimização de título, descrição e OG |
| `/seo:report <domain> <period>` | Relatório integral de desempenho SEO/GEO |
| `/seo:audit-domain <domain>` | Auditoria de autoridade de domínio CITE |
| `/seo:write-content <topic>` | Redação de conteúdo otimizado SEO + GEO |
| `/seo:keyword-research <seed>` | Pesquisa e análise de keywords |
| `/seo:setup-alert <metric>` | Configuração de alertas de monitoramento |
| `/seo:geo-drift-check [URL]` | (experimental, v9.0+) Valida GEO Score previsto vs. citações reais de motores IA |

### Comandos de manutenção (para mantenedores da biblioteca / usuários avançados; podem ser ignorados no uso diário)

| Comando | Descrição |
|---------|-----------|
| `/seo:wiki-lint` | Verificação de saúde do Wiki: contradições, órfãos, afirmações obsoletas, páginas faltantes |
| `/seo:contract-lint` | Detecção de drift no Auditor Runbook, verificação de esquema handoff, varredura de vazamento de jargão (v7.1.0+) |
| `/seo:p2-review` | Avaliar itens adiados da v7.1.0 contra condições de gatilho; revisão de tombstone (2026-07-10) |
| `/seo:sync-versions` | Propaga a versão canônica de `.claude-plugin/plugin.json` para todos os manifests cross-agent (v9.0+, substitui `scripts/sync-versions.py`) |
| `/seo:validate-library` | Portão de qualidade em nível de biblioteca: orçamento de descrições, ordem de campos YAML, cobertura de idiomas, detecção de gatilhos duplicados (v9.0+, substitui `scripts/validate-descriptions.py`) |

## Contribuir

Contribuições são bem-vindas! Consulte [CONTRIBUTING.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/CONTRIBUTING.md).

## Licença

Apache License 2.0

*Última sincronização com README em inglês: v9.0.0*
