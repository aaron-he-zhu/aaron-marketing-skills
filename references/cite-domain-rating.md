# CITE Domain Rating — Skills Reference

**Human-anchor revision: 2026-10-27-a.** The delimited item tables own criteria; detailed boundaries and examples below interpret those same IDs. Profiles, applicability, weights, veto identity, coverage and rounding remain in the typed catalog/scorer. This revision is not outcome calibration; preserve prior audit source digests and do not relabel historical observations.

> Based on [CITE Domain Rating](https://github.com/aaron-he-zhu/cite-domain-rating) **v1.0** (2026-02-10)
>
> This file is a reference adaptation for Aaron Marketing Skills. For the full specification with examples, see the source repository.
>
> **Version sync**: When the source spec updates, check: item count references in README (currently "40 items"), skill validation checkpoints, and Sections 2, 3, 7 below.

> **v18 execution contract**: this file owns human item anchors. Profiles, required comparison context, conditional applicability, and veto identity live in [`framework-catalog.json`](framework-catalog.json); Unknown/N/A, evidence, coverage, score, status, and verdict semantics live in [`scoring-semantics.md`](scoring-semantics.md). CITE is advisory and peer-relative until outcome-calibrated.

**4 dimensions × 10 items = 40 evaluation criteria** for assessing domain authority in the Generative Engine Optimization (GEO) era.

**Sister benchmark**: [CORE-EEAT Content Benchmark](core-eeat-benchmark.md) — content-level quality assessment (80 items).

---

## 1. Framework Overview

### CITE + CORE-EEAT: The Complete Picture

| Benchmark | Evaluates | Level | Items | Core Question |
|-----------|-----------|-------|-------|---------------|
| **CORE-EEAT** | Content quality | Single page/article | 80 | Is this content worth citing? |
| **CITE** | Domain authority | Entire domain | 40 | Is this domain worth trusting as a source? |
| **Combined** | Full diagnostic assessment | Content + Domain | **120** | What content and source controls support citation trust? |

### 4 Dimensions

| Dim | Full Name | Default Weight | Core Question | Primary Ownership |
|-----|-----------|:-:|---------------|---------------|
| **C** | Citation | 35% | How strongly is this domain referenced — through links AND AI citations? | All "others pointing to you" signals |
| **I** | Identity | 20% | How clearly is this domain recognized as a distinct entity? | Entity presence and brand recognition |
| **T** | Trust | 25% | Are there red flags suggesting manipulation? | All "is this suspicious?" detection signals |
| **E** | Eminence | 20% | How visible and influential is this domain? | Visibility, reach, and industry standing |

### Ownership Boundary Rule

- **C** = positive referencing signals (links + AI citations + editorial endorsements)
- **I** = entity existence and brand coherence (who you are, not how visible you are)
- **T** = suspicion and manipulation detection (negative/defensive signals)
- **E** = visibility and influence outcomes (how much you're seen)

These constructs are intentionally assigned one scoring owner, but they are not empirically independent. For example, links affect both Citation evidence and visibility outcomes; entity coherence influences trust. Preserve dependencies in findings and avoid counting one observation twice.

### Peer-Relative Benchmark Rule

Every scored run declares a comparison cohort, market, entity stage, and domain type. Numeric thresholds below are **diagnostic starting points inherited from the source benchmark**, not universal pass/fail laws. Before scoring, replace them with a dated peer distribution or an explicitly justified criterion for the declared cohort. If the necessary cohort or private evidence is absent, use `unknown`; do not force the item to Fail.

---

## 2. Complete 40-Item Checklist

### C — Citation (10 Items)

<!-- AUDITOR-ITEMS:BEGIN -->

| ID | Check Item | One-Line Diagnostic Anchor |
|----|-----------|-------------------|
| C01 | Referring Domains Volume | Referring-domain volume against a dated, frozen cohort-specific criterion; absent comparison basis is Unknown, never an automatic small-domain Fail. |
| C02 | Referring Domains Quality | >=20% of referring domains have DA (Moz Domain Authority™) / DR (Ahrefs Domain Rating™) 50+ |
| C03 | Link Equity Distribution | Top sources concentrate outbound links (<1,000 outbound domains) |
| C04 | Link Velocity | Steady natural growth; no month >3x average |
| C05 | AI Citation Frequency | Cited by >=2 AI engines on >=10 niche queries |
| C06 | AI Citation Prominence | Primary/sole source in >=50% of AI citations |
| C07 | Cross-Engine Citation | Cited by >=3 different AI engines |
| C08 | Citation Sentiment | >=80% of citations in positive/neutral context |
| C09 | Editorial Link Ratio | >=60% of backlinks from editorial decisions |
| C10 | Link Source Diversity | Referring domains span >=3 industries, >=5 regions |

### I — Identity (10 Items)

| ID | Check Item | One-Line Standard |
|----|-----------|-------------------|
| I01 | Knowledge Graph Presence | Entity in >=2 knowledge graphs (Google KG, Wikidata, DBpedia) |
| I02 | Brand Search Volume | Brand name >=1,000 monthly exact-match searches |
| I03 | Brand SERP Ownership | Brand search yields >=7 first-page results you control |
| I04 | Schema.org Coverage | >=50% of indexable pages with correct Schema.org markup |
| I05 | Author Entity Recognition | >=80% of content has authors with verifiable public identities |
| I06 | Domain Tenure | History is coherent relative to entity stage; age alone cannot fail the domain |
| I07 | Cross-Platform Consistency | Brand name/description/contact identical across all platforms |
| I08 | Niche Consistency | Same niche for >=3 consecutive years without major pivot |
| I09 | Unlinked Brand Mentions | >=50 third-party mentions without links |
| I10 | Query-Brand Association | Brand appears in industry query autocomplete |

### T — Trust (10 Items)

| ID | Check Item | One-Line Standard |
|----|-----------|-------------------|
| T01 | Link Profile Naturalness | No month >15% of total backlinks; growth correlates with publishing |
| T02 | Dofollow Ratio Normality | Dofollow 40-85% of total backlinks |
| T03 | Link-Traffic Coherence | Link/traffic relationship is coherent within the declared peer distribution (**Veto Item**) |
| T04 | IP/Network Diversity | >=100 unique C-class IP ranges; no single C-class >5% |
| T05 | Backlink Profile Uniqueness | No verified manipulation network after common-source adjustment (**Veto Item**) |
| T06 | WHOIS & Registration Transparency | Ownership history is coherent; privacy-protected WHOIS is neutral |
| T07 | Technical Security | Site-wide HTTPS + HSTS; no malware/phishing flags |
| T08 | Content Freshness Signal | New/updated content within last 90 days |
| T09 | Penalty & Deindex History | No verified active manual action or deindexing (**Veto Item**) |
| T10 | Review & Reputation Signals | >=3.5/5 average on >=2 third-party review platforms |

### E — Eminence (10 Items)

| ID | Check Item | One-Line Standard |
|----|-----------|-------------------|
| E01 | Organic Search Visibility | Ranks for >=1,000 keywords in top 100 |
| E02 | Organic Traffic Estimate | >=10,000 estimated monthly organic visits |
| E03 | SERP Feature Ownership | Appears in >=3 SERP feature types |
| E04 | Technical Crawlability | AI-crawler-friendly robots.txt; clean rendering; <3s load |
| E05 | Multi-Platform Footprint | Official presence on >=3 major platforms with recent activity |
| E06 | Authoritative Media Coverage | Featured in >=3 authoritative publications |
| E07 | Topical Authority Depth | Ranks for long-tail (4+ word) keywords deep in niche |
| E08 | Topical Authority Breadth | Covers >=70% of sub-topics in primary niche |
| E09 | Geographic Reach | Organic traffic from >=10 countries/regions |
| E10 | Industry Share of Voice | >=5% visibility share across top 50 industry keywords |

<!-- AUDITOR-ITEMS:END -->

---

## 3. Scoring System

### Per-Item Scoring

| Result | Score |
|--------|-------|
| Pass | 10 |
| Partial | 5 |
| Fail | 0 |

Applicable but unobserved items are `unknown`; omitted items are also `unknown`. Catalog-authorized inapplicable items are `na` with a reason. A comparable profile score requires 100% applicable evidence coverage and the declared peer/market/stage/type context.

### Score Calculation

- **Dimension score** = mean of the applicable items × 10 (0–100; catalog-authorized `na` items drop out of the mean)
- **Default diagnostic** = C × 0.35 + I × 0.20 + T × 0.25 + E × 0.20
- **Comparable profile score** = C × w_C + I × w_I + T × w_T + E × w_E, after peer-relative anchors and complete evidence are locked

### Domain-Type Weight Table

<!-- GENERATED:BEGIN auditor-policy:profiles -->

| Profile | Dimension weights | Context match | Item subset |
|---|---|---|---|
| `default` | C 35% · I 20% · T 25% · E 20% | none | all items in included dimensions |
| `content-publisher` | C 40% · I 15% · T 20% · E 25% | {"domain_type": "content-publisher"} | all items in included dimensions |
| `product-service` | C 25% · I 30% · T 25% · E 20% | {"domain_type": "product-service"} | all items in included dimensions |
| `ecommerce` | C 20% · I 20% · T 35% · E 25% | {"domain_type": "ecommerce"} | all items in included dimensions |
| `community-ugc` | C 35% · I 10% · T 25% · E 30% | {"domain_type": "community-ugc"} | all items in included dimensions |
| `tool-utility` | C 25% · I 30% · T 25% · E 20% | {"domain_type": "tool-utility"} | all items in included dimensions |
| `authority-institutional` | C 45% · I 20% · T 20% · E 15% | {"domain_type": "authority-institutional"} | all items in included dimensions |

<!-- GENERATED:END auditor-policy:profiles -->

### Rating Scale

| Score Range | Rating |
|-------------|--------|
| 90–100 | Excellent |
| 75–89 | Good |
| 60–74 | Medium |
| 40–59 | Low |
| 0–39 | Poor |

### Veto Items

Failing any veto item activates the Critical Fail Cap. The cap arithmetic and thresholds are defined in [auditor-runbook.md §4](auditor-runbook.md). The table below explains the domain-specific failures; executable policy and its generated views remain catalog-owned.

| Veto ID | Dimension | Check |
|---------|-----------|-------|
| **T03** | Trust | Verified, materially incoherent link/traffic pattern relative to the declared cohort, with manipulation evidence |
| **T05** | Trust | Verified backlink manipulation network after common-source and ecosystem adjustment |
| **T09** | Trust | Verified active manual action or material deindexing |

**Single veto fail**: cap applies per [Runbook §4 Scoring Semantics](auditor-runbook.md). Also raises a **Manipulation Alert** in the handoff `open_loops` field.

**2+ verified veto fails**: the completed audit returns `status: DONE`, `verdict: BLOCK`, and no final score. One verified veto caps the final score at 59. Missing cohort/private-console evidence remains Unknown and does not trigger a veto.

---

## 4. Domain Type Decision Tree

```
What is the domain's primary function?
├── Publishes articles, news, guides, or research     → Content Publisher
├── Sells/markets a product or service                 → Product & Service
├── Operates an online store or marketplace            → E-commerce
├── Hosts user-generated content, forums, or Q&A       → Community & UGC
├── Provides web tools, utilities, or applications     → Tool & Utility
└── Academic, government, non-profit, or standards     → Authority & Institutional
```

---

## 5. AI Engine Citation Preferences (Domain Signals)

| Engine | Preferred Domain Signals | Priority CITE Items |
|--------|-------------------------|---------------------|
| Google AI Overview | High organic rankings, Schema.org, SERP features | E01, E03, I04, C01 |
| ChatGPT Browse | Original data, authoritative sources, clear conclusions | C05, C06, I01, E06 |
| Perplexity AI | Research-grade content, methodology transparency, tiered sources | C09, C10, E07, I05 |
| Google Gemini | Knowledge graph presence, brand recognition, topical authority | I01, I02, E07, E08 |
| Claude | Trustworthy sources, balanced perspectives, transparent methodology | T01-T10, C08, I08 |

### Top 6 CITE Priority Items for AI Visibility

| Rank | ID | Name | Why It Matters |
|------|----|------|----------------|
| 1 | C05 | AI Citation Frequency | Direct measurement of AI engine citation |
| 2 | I01 | Knowledge Graph Presence | AI engines use KG to verify entity identity |
| 3 | T03 | Link-Traffic Coherence | Veto item that invalidates all other scores |
| 4 | E07 | Topical Authority Depth | AI prefers deep niche experts over generalists |
| 5 | C01 | Referring Domains Volume | Foundation signal — links remain the backbone |
| 6 | I04 | Schema.org Coverage | Structured data helps AI parse your content |

---

## 6. CITE + CORE-EEAT Integration Map

| CITE Item | Related CORE-EEAT Items | Relationship |
|-----------|------------------------|--------------|
| C05-C08 (AI Citations) | C02 (Direct Answer), O02 (Summary Box), E01 (Original Data) | Domain gets cited when content is citable |
| I01 (Knowledge Graph) | A07 (Knowledge Graph Presence), A08 (Entity Consistency) | EEAT-A items build the identity that I items measure |
| I04 (Schema.org) | O05 (Schema Markup), R09 (HTML Semantics) | Content-level schema contributes to domain-level coverage |
| I05 (Author Entity) | Ept01 (Author Identity), Ept02 (Credentials Display) | Content author signals build domain author recognition |
| T07 (Technical Security) | T03 (Security Standards) | Same signal, different scope (domain vs page) |
| E07-E08 (Topical Authority) | C03 (Query Coverage), E08 (Depth Advantage) | Content depth builds domain topical authority |

### Combined Diagnosis Matrix

| CITE Score | CORE-EEAT Score | Diagnosis | Priority Action |
|-----------|-----------------|-----------|-----------------|
| High | High | Ideal state | Maintain and expand |
| High | Low | Authority wasted on poor content | Prioritize content quality (CORE-EEAT) |
| Low | High | Great content, invisible domain | Build domain authority (CITE) |
| Low | Low | Fundamental issues | Start with CORE-EEAT, then CITE |

---

## 7. Detailed Criteria Reference

### C — Citation

**C01: Referring Domains Volume**
Freeze the market, entity stage/domain type, comparison cohort, source date/window, and the justified Pass/Partial/Fail boundaries before reading the target result. Count unique referring domains, not total backlinks. A different cohort or date is a different run.
- **Pass**: The observed domain count meets the frozen cohort-specific Pass criterion.
- **Partial**: It meets that cohort’s intermediate band but not Pass.
- **Fail**: Reliable observation places it below that cohort’s declared minimum; small size alone is not a universal trust failure.
- **Unknown**: The cohort/criterion or reliable comparable domain count is missing.
- **Historical illustration only**: 500/50 were source-benchmark starting points. A 30-domain early-stage site may pass a justified precommitted >=20 cohort criterion; 600 domains with no comparison basis remain Unknown. Never select the criterion after seeing the target or present the historical counts as machine-enforced universal thresholds.

**C02: Referring Domains Quality**
- **Pass**: >=20% of referring domains have DA/DR 50+.
- **Partial**: 5-19% have strong authority.
- **Fail**: <5% have notable authority.

**C03: Link Equity Distribution**
- **Pass**: Top sources avg <1,000 outbound domains; meaningful equity.
- **Partial**: Mixed concentrated and diluted sources.
- **Fail**: Most sources link to >10,000 domains (diluted equity).

**C04: Link Velocity**
- **Pass**: Steady growth; no month >3x average monthly acquisition.
- **Partial**: Mostly steady with 1-2 explainable spikes.
- **Fail**: Sudden spikes suggesting bulk acquisition.

**C05: AI Citation Frequency**
- **Pass**: Cited on >=10 distinct niche queries across >=2 AI engines.
- **Partial**: Cited on 3-9 queries.
- **Fail**: Cited on 0-2 queries or not cited.

**C06: AI Citation Prominence**
- **Pass**: Primary/sole source in >=50% of citations.
- **Partial**: One of several sources in most citations.
- **Fail**: Only supplementary mentions or footnotes.

**C07: Cross-Engine Citation**
- **Pass**: Cited by >=3 different AI engines.
- **Partial**: Cited by 2 AI engines.
- **Fail**: Cited by 0-1 AI engines.

**C08: Citation Sentiment**
- **Pass**: >=80% positive/neutral citations.
- **Partial**: 50-79% positive/neutral.
- **Fail**: >50% negative citations.

**C09: Editorial Link Ratio**
- **Pass**: >=60% editorial links (in-content from articles, guides, research).
- **Partial**: 30-59% editorial links.
- **Fail**: <30% (dominated by directories, forums, comments).

**C10: Link Source Diversity**
- **Pass**: >=3 industries and >=5 geographic regions.
- **Partial**: 2 industries or 3-4 regions.
- **Fail**: 1 industry or <3 regions.

### I — Identity

**I01: Knowledge Graph Presence**
- **Pass**: Entity in >=2 major knowledge graphs.
- **Partial**: In 1 knowledge graph.
- **Fail**: Not in any knowledge graph.

**I02: Brand Search Volume**
- **Pass**: >=1,000 monthly exact-match searches.
- **Partial**: 100-999 searches.
- **Fail**: <100 or no measurable brand search volume.

**I03: Brand SERP Ownership**
- **Pass**: >=7 first-page results controlled by the domain.
- **Partial**: 4-6 controlled results.
- **Fail**: <4 controlled results.

**I04: Schema.org Coverage**
- **Pass**: >=50% of indexable pages with correct Schema.org markup.
- **Partial**: 20-49% coverage or incorrect types.
- **Fail**: <20% coverage or no markup.

**I05: Author Entity Recognition**
- **Pass**: >=80% of content has authors with verifiable identities.
- **Partial**: 40-79% attributed.
- **Fail**: <40% or unverifiable authors.

**I06: Domain Tenure**
- **Pass**: History is coherent and stable relative to the declared entity stage and peer cohort.
- **Partial**: Limited history or an ownership/purpose transition is documented but not yet well established.
- **Fail**: Verified deceptive expired-domain reuse or materially contradictory ownership/purpose history. Domain youth alone is not a failure.

**I07: Cross-Platform Consistency**
- **Pass**: Identical brand info across all platforms.
- **Partial**: Mostly consistent with minor discrepancies.
- **Fail**: Significant inconsistencies.

**I08: Niche Consistency**
- **Pass**: Same niche >=3 consecutive years.
- **Partial**: 1-2 years or 1 minor pivot.
- **Fail**: Frequent niche changes or recent unrelated pivot.

**I09: Unlinked Brand Mentions**
- **Pass**: >=50 distinct third-party mentions without links.
- **Partial**: 10-49 unlinked mentions.
- **Fail**: <10 unlinked mentions.

**I10: Query-Brand Association**
- **Pass**: Brand appended to industry queries in autocomplete.
- **Partial**: Some query-brand association visible.
- **Fail**: No measurable association.

### T — Trust

**T01: Link Profile Naturalness**
- **Pass**: Natural distribution; no month >15% of total backlinks.
- **Partial**: Mostly natural with 1-2 explainable anomalies.
- **Fail**: Obvious unnatural patterns or bulk acquisition.

**T02: Dofollow Ratio Normality**
- **Pass**: 40-85% dofollow.
- **Partial**: 85-90% (slightly elevated).
- **Fail**: >90% (manipulation signal) or <20%.

**T03: Link-Traffic Coherence** | **VETO ITEM**
- **Pass**: The link/traffic relationship falls within the declared peer distribution or has a documented, credible explanation.
- **Partial**: The relationship is anomalous but evidence does not establish manipulation.
- **Fail**: A material anomaly plus corroborating manipulation evidence is verified against the declared cohort → **Veto triggered**.
- **Unknown**: No suitable peer distribution or reliable traffic/link evidence is available.

**T04: IP/Network Diversity**
- **Pass**: >=100 unique C-class ranges; no single C-class >5%.
- **Partial**: 50-99 C-class ranges.
- **Fail**: <50 C-class ranges or >20% from one C-class (PBN signature).

**T05: Backlink Profile Uniqueness** | **VETO ITEM**
- **Pass**: Overlap is ordinary for the declared ecosystem after ubiquitous/common sources are removed.
- **Partial**: Unusual overlap exists but shared ownership, syndication, or niche structure remains a plausible explanation.
- **Fail**: A declared comparison universe and corroborating network evidence establish coordinated manipulation → **Veto triggered**.
- **Unknown**: No defensible comparison universe or cross-domain backlink evidence is available.

**T06: WHOIS & Registration Transparency**
- **Pass**: Available registration/history evidence is stable and consistent with the entity.
- **Partial**: History is limited or contains a documented transition without contradictory evidence.
- **Fail**: Verified ownership churn or registration evidence materially contradicts the represented entity.
- **Neutral**: Privacy-protected WHOIS alone is neither Partial nor Fail.

**T07: Technical Security**
- **Pass**: Site-wide HTTPS + HSTS; no security flags.
- **Partial**: HTTPS but missing HSTS or minor mixed-content.
- **Fail**: HTTP-only, expired certs, or flagged by security services.

**T08: Content Freshness Signal**
- **Pass**: Content published/updated within last 90 days.
- **Partial**: Last update 90-365 days ago.
- **Fail**: No updates for >1 year.

**T09: Penalty & Deindex History** | **VETO ITEM**
- **Pass**: Authorized console evidence and index checks show no active action/deindexing.
- **Partial**: A historical action is documented as resolved, with recovery evidence.
- **Fail**: An active manual action or material unresolved deindexing is verified → **Veto triggered**.
- **Unknown**: Private-console access is absent and public observations cannot establish the state; never pass by absence of evidence.

**T10: Review & Reputation Signals**
- **Pass**: >=3.5/5 average on >=2 review platforms.
- **Partial**: Mixed (3.0-3.4) or only 1 platform.
- **Fail**: <3.0 average or no review presence for consumer-facing domain.

### E — Eminence

**E01: Organic Search Visibility**
- **Pass**: Ranks for >=1,000 keywords.
- **Partial**: 100-999 keywords.
- **Fail**: <100 keywords.

**E02: Organic Traffic Estimate**
- **Pass**: >=10,000 monthly organic visits.
- **Partial**: 1,000-9,999.
- **Fail**: <1,000.

**E03: SERP Feature Ownership**
- **Pass**: >=3 SERP feature types.
- **Partial**: 1-2 feature types.
- **Fail**: No SERP feature appearances.

**E04: Technical Crawlability**
- **Pass**: Permissive robots.txt for AI crawlers; clean SSR; <3s load.
- **Partial**: Partially blocks AI crawlers or minor rendering issues.
- **Fail**: Blocks all AI crawlers, heavy JS without SSR, or >10s load.

**E05: Multi-Platform Footprint**
- **Pass**: Official presence on >=3 major platforms with recent activity.
- **Partial**: 1-2 platforms or present but inactive.
- **Fail**: No presence beyond the domain itself.

**E06: Authoritative Media Coverage**
- **Pass**: Featured in >=3 authoritative publications.
- **Partial**: 1-2 media mentions.
- **Fail**: No authoritative media coverage.

**E07: Topical Authority Depth**
- **Pass**: Ranks for long-tail keywords deep within niche.
- **Partial**: Some long-tail rankings but gaps.
- **Fail**: Only broad/head terms; no niche depth.

**E08: Topical Authority Breadth**
- **Pass**: Covers >=70% of niche sub-topics.
- **Partial**: 40-69%.
- **Fail**: <40% (significant gaps).

**E09: Geographic Reach**
- **Pass**: Traffic from >=10 countries/regions.
- **Partial**: 5-9 regions.
- **Fail**: <5 regions.

**E10: Industry Share of Voice**
- **Pass**: >=5% visibility across top 50 industry keywords.
- **Partial**: 1-4%.
- **Fail**: <1% or not ranking for most industry keywords.

---

## 8. Data Source Mapping

> Maps each check item to data sources, tools, and audit methods. Use `~~placeholder` categories from [CONNECTORS.md](../CONNECTORS.md) when integrations are available.

| Check Item | Data Source | Tools | Audit Method |
|-----------|------------|-------|-------------|
| C01 Referring Domains Volume | Backlink index | `~~link database` | API query: unique referring domains count |
| C02 Referring Domains Quality | Backlink index + authority scores | `~~link database` (DR/DA of sources) | Aggregate authority of top 100 referring domains |
| C03 Link Equity Distribution | Outbound link analysis of sources | `~~link database` (outgoing links per domain) | Avg outbound domains of top 50 referring domains |
| C04 Link Velocity | Historical backlink data | `~~link database` (new/lost over time) | Month-over-month link growth trend analysis |
| C05 AI Citation Frequency | AI engine output monitoring | `~~AI monitor`, manual testing | Query 20+ niche questions across 4+ AI engines |
| C06 AI Citation Prominence | AI engine output analysis | `~~AI monitor`, manual review | Classify citations as primary/supplementary/footnote |
| C07 Cross-Engine Citation | Multi-engine monitoring | `~~AI monitor` | Count distinct engines that cite the domain |
| C08 Citation Sentiment | NLP sentiment analysis | `~~AI monitor` + sentiment classifier | Classify citation context as positive/neutral/negative |
| C09 Editorial Link Ratio | Backlink type classification | `~~link database` (link context) | Categorize links: editorial vs directory/comment/sidebar |
| C10 Link Source Diversity | Referring domain metadata | `~~link database` + IP geolocation | Cluster referring domains by industry and geography |
| I01 Knowledge Graph Presence | Knowledge graph APIs | `~~knowledge graph` | Query entity name across knowledge graphs |
| I02 Brand Search Volume | Search volume data | `~~SEO tool` | Exact-match monthly search volume for brand name |
| I03 Brand SERP Ownership | SERP analysis | `~~SEO tool` (SERP checker) | Search brand name; count owned results on page 1 |
| I04 Schema.org Coverage | Technical crawl | `~~web crawler`, `~~schema validator` | Crawl site; % of pages with valid Schema.org |
| I05 Author Entity Recognition | Author page analysis + KG | Manual review + `~~knowledge graph` | Check author pages for verifiable public identities |
| I06 Domain Tenure | WHOIS + Web Archive | WHOIS lookup, Wayback Machine | Registration date + continuous activity verification |
| I07 Cross-Platform Consistency | Multi-platform scraping | `~~brand monitor`, manual audit | Compare brand info across website + social profiles |
| I08 Niche Consistency | Web Archive + content analysis | Wayback Machine + topic modeling | Historical content analysis over time |
| I09 Unlinked Brand Mentions | Brand mention monitoring | `~~brand monitor` | Count brand mentions minus linked mentions |
| I10 Query-Brand Association | Search suggest data | `~~SEO tool` (autocomplete) | Check if brand appears in industry query suggestions |
| T01 Link Profile Naturalness | Historical link data | `~~link database` (timeline) | Statistical analysis of growth curve distribution |
| T02 Dofollow Ratio Normality | Link attribute data | `~~link database` (link attributes) | Calculate dofollow % of total referring domains |
| T03 Link-Traffic Coherence | Links + traffic estimates | `~~link database` + `~~SEO tool` (traffic) | Ratio: organic visits per referring domain |
| T04 IP/Network Diversity | IP data of referring domains | `~~link database` (referring IPs) | Count unique C-class IP ranges; check concentration |
| T05 Backlink Profile Uniqueness | Cross-domain link comparison | `~~link database` (link intersect) | Check overlap % with other domains' link profiles |
| T06 WHOIS & Registration Transparency | WHOIS database | WHOIS lookup, DomainTools | Check registration info, registrar, ownership history |
| T07 Technical Security | Security scanners | Google Safe Browsing API, SSL Labs | HTTPS check + security header audit + malware scan |
| T08 Content Freshness Signal | Crawl timestamps | `~~web crawler` (cache dates) | Check last-modified dates across site pages |
| T09 Penalty & Deindex History | `~~search console` + archives | GSC Manual Actions report, Web Archive | Check for manual actions; verify index status |
| T10 Review & Reputation Signals | Third-party review platforms | Trustpilot, G2, BBB | Aggregate ratings across review platforms |
| E01 Organic Search Visibility | Keyword ranking data | `~~SEO tool` (visibility index) | Count keywords ranking in top 100 |
| E02 Organic Traffic Estimate | Traffic estimation models | `~~SEO tool`, `~~analytics` | Estimated monthly organic visits |
| E03 SERP Feature Ownership | SERP feature tracking | `~~SEO tool` (SERP features report) | Count distinct SERP feature types domain appears in |
| E04 Technical Crawlability | Technical audit | `~~web crawler`, robots.txt analyzer | Check robots.txt AI crawler policies + render test |
| E05 Multi-Platform Footprint | Platform presence check | `~~brand monitor`, manual audit | Verify official profiles on major platforms |
| E06 Authoritative Media Coverage | Media mention databases | `~~brand monitor`, Google News | Count authoritative media mentions |
| E07 Topical Authority Depth | Long-tail keyword rankings | `~~SEO tool` (4+ word keyword filter) | Count long-tail keyword rankings in primary niche |
| E08 Topical Authority Breadth | Topic clustering | `~~SEO tool` (topic research) | Map sub-topics covered vs total niche sub-topics |
| E09 Geographic Reach | Geographic traffic data | `~~SEO tool`, `~~analytics` | Count countries with organic traffic |
| E10 Industry Share of Voice | Competitive visibility | `~~SEO tool` (position tracking) | Calculate visibility % across top 50 industry keywords |

---

## 9. Common Evaluation Mistakes

| # | Mistake | Item | Wrong | Right |
|---|---------|------|-------|-------|
| 1 | Ignoring AI citations | C05 | Only checking backlinks | Also monitor AI engine citations across major platforms |
| 2 | Counting total links, not domains | C01 | "We have 50,000 backlinks!" | Count unique referring domains, not total link count |
| 3 | Link quality conflated with quantity | C02 | 10,000 low-authority links = good | 200 high-authority editorial links > 10,000 directory links |
| 4 | Ignoring entity identity | I01 | Focus only on links and traffic | Check knowledge graph presence; it's how AI verifies sources |
| 5 | Neglecting Schema markup | I04 | "Schema doesn't matter for authority" | Schema helps AI engines understand your domain's scope |
| 6 | Not checking veto items first | T03 | Full evaluation before checking fundamentals | Always check T03, T05, T09 first — they can invalidate everything |
| 7 | Treating abandoned domains as trustworthy | T08 | "Old domain = authoritative domain" | A domain dormant for 3 years has decayed authority |
| 8 | Overlooking AI crawler policies | E04 | Blocking all bots for "security" | Review robots.txt; blocking AI crawlers kills GEO potential |
| 9 | Equating social presence with authority | E05 | "We have 100K followers = high authority" | Social presence is one of 40 items, not a proxy for overall authority |
| 10 | Using single-metric shortcuts | — | "Our Moz DA is 60, so we're good" | No single metric captures the full picture; CITE evaluates 40 signals |

---

## 10. Commonly Confused Pairs

When unsure which dimension owns a signal, use the ownership boundary rule (Section 1). For frequently confused items:

| Pair | Disambiguation |
|------|---------------|
| **C01 (Referring Domains)** vs **E01 (Organic Visibility)** | C01 = who links to you (input); E01 = where you rank (output) |
| **I09 (Unlinked Mentions)** vs **E06 (Media Coverage)** | I09 = any third-party mention without a link; E06 = authoritative media specifically |
| **I08 (Niche Consistency)** vs **E07/E08 (Topical Authority)** | I08 = how long you've stayed in one niche (identity); E07/E08 = how deep/broad your rankings are (visibility) |
| **C09 (Editorial Link Ratio)** vs **T01 (Link Naturalness)** | C09 = positive quality (what % are editorial); T01 = negative detection (is the growth pattern natural) |
| **T06 (WHOIS Transparency)** vs **I06 (Domain Tenure)** | T06 = is the registration suspicious (trust); I06 = how long has it been active (identity) |

## Fixed Boundary Cases (2026-10-27-a)

See the [fixed factual examples for CITE](benchmark-boundary-examples.md#cite) when calibrating a disputed boundary. These examples are lookup material; retain the item anchors and complete evidence rules above for execution.

## Evidence Reuse and Targeted Review

Freeze one cohort/market/stage/window and collect a common backlink, identity and visibility panel once. Keep public observations separate from unavailable private-console facts; a new panel or date creates a new run rather than silently changing the old benchmark.

Follow the existing [auditor runbook](auditor-runbook.md) for evidence, authority and final complete-coverage scoring; reuse does not create independent corroboration.
