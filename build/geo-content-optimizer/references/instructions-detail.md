# GEO Content Optimizer — Detailed Instructions

Full workflow templates, CORE-EEAT GEO mapping, scoring tables, examples, and tips for the GEO Content Optimizer skill.

---

## Step-by-Step Workflow

### 1. Load CORE-EEAT GEO-First Optimization Targets

Before optimizing, load GEO-critical items from the [CORE-EEAT Benchmark](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md):

```markdown
### CORE-EEAT GEO-First Targets

These items have the highest impact on AI engine citation. Use as optimization checklist:

**Top 6 Priority Items**:
| Rank | ID | Standard | Why It Matters |
|------|----|----------|---------------|
| 1 | C02 | Direct Answer in first 150 words | All engines extract from first paragraph |
| 2 | C09 | Structured FAQ with Schema | Directly matches AI follow-up queries |
| 3 | O03 | Data in tables, not prose | Most extractable structured format |
| 4 | O05 | JSON-LD Schema Markup | Helps AI understand content type |
| 5 | E01 | Original first-party data | AI prefers exclusive, verifiable sources |
| 6 | O02 | Key Takeaways / Summary Box | First choice for AI summary citations |

**All GEO-First Items** (optimize for all when possible):
C02, C04, C05, C07, C08, C09 | O02, O03, O04, O05, O06, O09
R01, R02, R03, R04, R05, R07, R09 | E01, E02, E03, E04, E06, E08, E09, E10
Exp10 | Ept05, Ept08 | A08

**AI Engine Preferences**:
| Engine | Priority Items |
|--------|----------------|
| Google AI Overview | C02, O03, O05, C09 |
| ChatGPT Browse | C02, R01, R02, E01 |
| Perplexity AI | E01, R03, R05, Ept05 |
| Claude | R04, Ept08, Exp10, R03 |

_Full benchmark: [references/core-eeat-benchmark.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/references/core-eeat-benchmark.md)_
```

### 2. Analyze Current Content

```markdown
## GEO Analysis: [Content Title]

### Current State Assessment

| GEO Factor | Current Score (1-10) | Notes |
|------------|---------------------|-------|
| Clear definitions | [X] | [notes] |
| Quotable statements | [X] | [notes] |
| Factual density | [X] | [notes] |
| Source citations | [X] | [notes] |
| Q&A format | [X] | [notes] |
| Authority signals | [X] | [notes] |
| Content freshness | [X] | [notes] |
| Structure clarity | [X] | [notes] |
| **GEO Readiness** | **[avg]/10** | **Average across factors** |

**Primary Weaknesses**:
1. [Weakness 1]
2. [Weakness 2]
3. [Weakness 3]

**Quick Wins**:
1. [Quick improvement 1]
2. [Quick improvement 2]
```

### 3. Apply GEO Optimization Techniques

> **GEO fundamentals**: AI systems prioritize content that is authoritative (expert credentials, proper citations), accurate (verifiable, up-to-date), clear (well-structured, unambiguous), and quotable (standalone answers, specific data). See [references/geo-optimization-techniques.md](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/build/geo-content-optimizer/references/geo-optimization-techniques.md) for details.

Apply the six core optimization techniques: definition optimization, quotable statement creation, authority signal enhancement, structure optimization, factual density improvement, and FAQ schema implementation.

Key principles:
- **Definitions**: 25-50 words, standalone, starting with the term
- **Quotable statements**: Specific statistics with sources, verifiable facts
- **Authority signals**: Expert quotes with credentials, proper source citations
- **Structure**: Q&A format, comparison tables, numbered lists
- **Factual density**: Replace vague claims with specific data points
- **FAQ schema**: JSON-LD FAQPage markup matching visible content

### 4. Generate GEO-Optimized Output

```markdown
## GEO Optimization Report

### Changes Made

**Definitions Added/Improved**:
1. [Definition 1] - [location in content]
2. [Definition 2] - [location in content]

**Quotable Statements Created**:
1. "[Statement 1]"
2. "[Statement 2]"

**Authority Signals Added**:
1. [Expert quote/citation]
2. [Source attribution]

**Structural Improvements**:
1. [Change 1]
2. [Change 2]

### Before/After GEO Score

| GEO Factor | Before (1-10) | After (1-10) | Change |
|------------|---------------|--------------|--------|
| Clear definitions | [X] | [X] | +[X] |
| Quotable statements | [X] | [X] | +[X] |
| Factual density | [X] | [X] | +[X] |
| Source citations | [X] | [X] | +[X] |
| Q&A format | [X] | [X] | +[X] |
| Authority signals | [X] | [X] | +[X] |
| **Overall GEO Score** | **[avg]/10** | **[avg]/10** | **+[X]** |

### AI Query Coverage

This content is now optimized to answer:
- "What is [topic]?"
- "How does [topic] work?"
- "Why is [topic] important?"
- "[Topic] vs [alternative]"
- "Best [topic] for [use case]"
```

### 5. CORE-EEAT GEO Self-Check

After optimization, verify GEO-First items:

```markdown
### CORE-EEAT GEO Post-Optimization Check

| ID | Standard | Status | Notes |
|----|----------|--------|-------|
| C02 | Direct Answer in first 150 words | Pass/Warn/Fail | [notes] |
| C04 | Key terms defined on first use | Pass/Warn/Fail | [notes] |
| C09 | Structured FAQ with Schema | Pass/Warn/Fail | [notes] |
| O02 | Summary Box / Key Takeaways | Pass/Warn/Fail | [notes] |
| O03 | Comparisons in tables | Pass/Warn/Fail | [notes] |
| O05 | JSON-LD Schema Markup | Pass/Warn/Fail | [notes] |
| O06 | Section chunking (3–5 sentences) | Pass/Warn/Fail | [notes] |
| R01 | ≥5 precise data points with units | Pass/Warn/Fail | [notes] |
| R02 | ≥1 citation per 500 words | Pass/Warn/Fail | [notes] |
| R04 | Claims backed by evidence | Pass/Warn/Fail | [notes] |
| R07 | Full entity names | Pass/Warn/Fail | [notes] |
| E01 | Original first-party data | Pass/Warn/Fail | [notes] |
| Exp10 | Limitations acknowledged | Pass/Warn/Fail | [notes] |
| Ept08 | Reasoning transparency | Pass/Warn/Fail | [notes] |

**Items Needing Attention**: [list any Warn/Fail items]

_For full 80-item audit, use [content-quality-auditor](https://github.com/aaron-he-zhu/seo-geo-claude-skills/blob/main/cross-cutting/content-quality-auditor/SKILL.md)_
```

---

## Example

**User**: "Optimize this paragraph for GEO: 'Email marketing is a good way to reach customers. It's been around for a while and many businesses use it. You can send newsletters, promotions, and other messages.'"

**Output**:

```markdown
## GEO-Optimized Version

**Email marketing** is a digital marketing strategy that uses email to promote 
products, build customer relationships, and drive conversions. According to 
the Data & Marketing Association, email marketing delivers an average ROI 
of $42 for every $1 invested, making it the highest-performing digital 
marketing channel.

### Key email marketing formats include:

1. **Newsletters**: Regular updates sharing company news, industry insights, 
   and valuable content to maintain subscriber engagement
2. **Promotional emails**: Time-sensitive offers, discounts, and product 
   announcements designed to drive immediate sales
3. **Transactional emails**: Order confirmations, shipping updates, and 
   account notifications with 8x higher open rates than marketing emails
4. **Automated sequences**: Pre-scheduled email series triggered by user 
   actions, such as welcome series or abandoned cart reminders

> **Key statistic**: 81% of small businesses rely on email as their primary 
> customer acquisition channel (Emarsys, 2024).

---

### Changes Made:

Changes: added clear definition, 2 stats with sources, structured list, DMA/Emarsys citations, 3 quotable facts. **GEO Score**: 1/10 → 8/10.
```

---

## Tips for Success

1. **Answer the question first** - Put the answer in the first sentence
2. **Be specific** - Vague content doesn't get cited
3. **Cite sources** - AI systems trust verifiable information
4. **Stay current** - Update statistics and facts regularly
5. **Match query format** - Questions deserve direct answers
6. **Build authority** - Expert credentials increase citation likelihood
