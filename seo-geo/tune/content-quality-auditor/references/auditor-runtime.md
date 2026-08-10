<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** CORE-EEAT
- **Auditor:** content-quality-auditor
- **Complete item definitions:** 80
- **Source digest:** `sha256:93c1c1aba364430ebb776df31e720c261a0c1f51616dc17c0a7d228d2b0caae5`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
  "frameworks": {
    "CORE-EEAT": {
      "construct": "content-quality controls for one declared content artifact",
      "dimensions": {
        "A": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "A",
          "name": "Authority"
        },
        "C": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "C",
          "name": "Content"
        },
        "E": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "E",
          "name": "Exclusivity"
        },
        "Ept": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "Ept",
          "name": "Expertise"
        },
        "Exp": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "Exp",
          "name": "Experience"
        },
        "O": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "O",
          "name": "Organization"
        },
        "R": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "R",
          "name": "Research"
        },
        "T": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "T",
          "name": "Trust"
        }
      },
      "item_policies": {
        "A07": {
          "applicability": "conditional",
          "condition": "knowledge-graph presence is material to the audit objective"
        },
        "E01": {
          "applicability": "conditional",
          "condition": "original data is part of the content promise"
        },
        "E02": {
          "applicability": "conditional",
          "condition": "the content claims a novel framework"
        },
        "E03": {
          "applicability": "conditional",
          "condition": "primary research is part of the content promise"
        },
        "E04": {
          "applicability": "conditional",
          "condition": "the content takes a contrarian position"
        },
        "E05": {
          "applicability": "conditional",
          "condition": "original visuals are needed to support the artifact"
        },
        "E10": {
          "applicability": "conditional",
          "condition": "the content makes forward-looking claims"
        },
        "Exp01": {
          "applicability": "conditional",
          "condition": "first-person experience is claimed or required by the profile"
        },
        "Exp02": {
          "applicability": "conditional",
          "condition": "sensory observation is material to the subject"
        },
        "Exp04": {
          "applicability": "conditional",
          "condition": "the artifact claims hands-on use"
        },
        "Exp05": {
          "applicability": "conditional",
          "condition": "usage duration is material"
        },
        "Exp07": {
          "applicability": "conditional",
          "condition": "a before/after claim is made"
        },
        "Exp09": {
          "applicability": "conditional",
          "condition": "repeat testing is claimed"
        },
        "O03": {
          "applicability": "conditional",
          "condition": "the artifact contains comparable structured data"
        },
        "O05": {
          "applicability": "conditional",
          "condition": "the artifact is an indexable web page eligible for structured data"
        },
        "O10": {
          "applicability": "conditional",
          "condition": "multimedia is part of the declared artifact"
        },
        "T04": {
          "applicability": "conditional",
          "condition": "a material connection, paid placement, or affiliate relationship exists",
          "veto": true
        },
        "T08": {
          "applicability": "conditional",
          "condition": "the artifact makes YMYL or other material-risk claims"
        }
      },
      "items": {
        "A01": {
          "criterion": "Cited by authoritative sites (.edu, .gov, leaders)",
          "dimension": "A",
          "name": "Backlink Profile",
          "policy": {},
          "qualified_id": "CORE-EEAT-A01",
          "veto": false
        },
        "A02": {
          "criterion": "\"Featured in\" with media logos",
          "dimension": "A",
          "name": "Media Mentions",
          "policy": {},
          "qualified_id": "CORE-EEAT-A02",
          "veto": false
        },
        "A03": {
          "criterion": "Displays relevant industry awards or recognition",
          "dimension": "A",
          "name": "Industry Awards",
          "policy": {},
          "qualified_id": "CORE-EEAT-A03",
          "veto": false
        },
        "A04": {
          "criterion": "Conference talks, publications, patents",
          "dimension": "A",
          "name": "Publishing Record",
          "policy": {},
          "qualified_id": "CORE-EEAT-A04",
          "veto": false
        },
        "A05": {
          "criterion": "Brand has search volume",
          "dimension": "A",
          "name": "Brand Recognition",
          "policy": {},
          "qualified_id": "CORE-EEAT-A05",
          "veto": false
        },
        "A06": {
          "criterion": "Authentic user testimonials with real details",
          "dimension": "A",
          "name": "Social Proof",
          "policy": {},
          "qualified_id": "CORE-EEAT-A06",
          "veto": false
        },
        "A07": {
          "criterion": "Has Wikipedia entry or Google Knowledge Panel",
          "dimension": "A",
          "name": "Knowledge Graph Presence",
          "policy": {
            "applicability": "conditional",
            "condition": "knowledge-graph presence is material to the audit objective"
          },
          "qualified_id": "CORE-EEAT-A07",
          "veto": false
        },
        "A08": {
          "criterion": "Brand/author info consistent across the web",
          "dimension": "A",
          "name": "Entity Consistency",
          "policy": {},
          "qualified_id": "CORE-EEAT-A08",
          "veto": false
        },
        "A09": {
          "criterion": "Shows partnerships with authoritative organizations",
          "dimension": "A",
          "name": "Partnership Signals",
          "policy": {},
          "qualified_id": "CORE-EEAT-A09",
          "veto": false
        },
        "A10": {
          "criterion": "Active and influential in professional communities",
          "dimension": "A",
          "name": "Community Standing",
          "policy": {},
          "qualified_id": "CORE-EEAT-A10",
          "veto": false
        },
        "C01": {
          "criterion": "Title promise = content delivery",
          "dimension": "C",
          "name": "Intent Alignment",
          "policy": {},
          "qualified_id": "CORE-EEAT-C01",
          "veto": true
        },
        "C02": {
          "criterion": "Core answer in first 150 words",
          "dimension": "C",
          "name": "Direct Answer",
          "policy": {},
          "qualified_id": "CORE-EEAT-C02",
          "veto": false
        },
        "C03": {
          "criterion": "Covers ≥3 query variants (synonyms, long-tail)",
          "dimension": "C",
          "name": "Query Coverage",
          "policy": {},
          "qualified_id": "CORE-EEAT-C03",
          "veto": false
        },
        "C04": {
          "criterion": "Key terms defined on first use",
          "dimension": "C",
          "name": "Definition First",
          "policy": {},
          "qualified_id": "CORE-EEAT-C04",
          "veto": false
        },
        "C05": {
          "criterion": "Explicitly states what is and isn't covered",
          "dimension": "C",
          "name": "Topic Scope",
          "policy": {},
          "qualified_id": "CORE-EEAT-C05",
          "veto": false
        },
        "C06": {
          "criterion": "States \"this article is for...\"",
          "dimension": "C",
          "name": "Audience Targeting",
          "policy": {},
          "qualified_id": "CORE-EEAT-C06",
          "veto": false
        },
        "C07": {
          "criterion": "Logical flow between paragraphs, no jumps",
          "dimension": "C",
          "name": "Semantic Coherence",
          "policy": {},
          "qualified_id": "CORE-EEAT-C07",
          "veto": false
        },
        "C08": {
          "criterion": "Decision framework: when to choose A vs B",
          "dimension": "C",
          "name": "Use Case Mapping",
          "policy": {},
          "qualified_id": "CORE-EEAT-C08",
          "veto": false
        },
        "C09": {
          "criterion": "Structured FAQ covering long-tail follow-ups",
          "dimension": "C",
          "name": "FAQ Coverage",
          "policy": {},
          "qualified_id": "CORE-EEAT-C09",
          "veto": false
        },
        "C10": {
          "criterion": "Conclusion answers the opening question + next steps",
          "dimension": "C",
          "name": "Semantic Closure",
          "policy": {},
          "qualified_id": "CORE-EEAT-C10",
          "veto": false
        },
        "E01": {
          "criterion": "First-party surveys, experiments, or statistics",
          "dimension": "E",
          "name": "Original Data",
          "policy": {
            "applicability": "conditional",
            "condition": "original data is part of the content promise"
          },
          "qualified_id": "CORE-EEAT-E01",
          "veto": false
        },
        "E02": {
          "criterion": "Named, citable original framework or model",
          "dimension": "E",
          "name": "Novel Framework",
          "policy": {
            "applicability": "conditional",
            "condition": "the content claims a novel framework"
          },
          "qualified_id": "CORE-EEAT-E02",
          "veto": false
        },
        "E03": {
          "criterion": "Original experiments/surveys with documented process",
          "dimension": "E",
          "name": "Primary Research",
          "policy": {
            "applicability": "conditional",
            "condition": "primary research is part of the content promise"
          },
          "qualified_id": "CORE-EEAT-E03",
          "veto": false
        },
        "E04": {
          "criterion": "Challenges consensus with evidence",
          "dimension": "E",
          "name": "Contrarian View",
          "policy": {
            "applicability": "conditional",
            "condition": "the content takes a contrarian position"
          },
          "qualified_id": "CORE-EEAT-E04",
          "veto": false
        },
        "E05": {
          "criterion": "≥2 original infographics, charts, or diagrams",
          "dimension": "E",
          "name": "Proprietary Visuals",
          "policy": {
            "applicability": "conditional",
            "condition": "original visuals are needed to support the artifact"
          },
          "qualified_id": "CORE-EEAT-E05",
          "veto": false
        },
        "E06": {
          "criterion": "Covers questions competitors don't",
          "dimension": "E",
          "name": "Gap Filling",
          "policy": {},
          "qualified_id": "CORE-EEAT-E06",
          "veto": false
        },
        "E07": {
          "criterion": "Downloadable templates, checklists, or calculators",
          "dimension": "E",
          "name": "Practical Tools",
          "policy": {},
          "qualified_id": "CORE-EEAT-E07",
          "veto": false
        },
        "E08": {
          "criterion": "Deeper than competing content on same topic",
          "dimension": "E",
          "name": "Depth Advantage",
          "policy": {},
          "qualified_id": "CORE-EEAT-E08",
          "veto": false
        },
        "E09": {
          "criterion": "Cross-domain knowledge combination (A+B=C)",
          "dimension": "E",
          "name": "Synthesis Value",
          "policy": {},
          "qualified_id": "CORE-EEAT-E09",
          "veto": false
        },
        "E10": {
          "criterion": "Data-backed predictions and trend analysis",
          "dimension": "E",
          "name": "Forward Insights",
          "policy": {
            "applicability": "conditional",
            "condition": "the content makes forward-looking claims"
          },
          "qualified_id": "CORE-EEAT-E10",
          "veto": false
        },
        "Ept01": {
          "criterion": "Byline + avatar + bio (>30 words)",
          "dimension": "Ept",
          "name": "Author Identity",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept01",
          "veto": false
        },
        "Ept02": {
          "criterion": "Relevant degrees, certs, years of experience",
          "dimension": "Ept",
          "name": "Credentials Display",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept02",
          "veto": false
        },
        "Ept03": {
          "criterion": "Accurate industry jargon, no misuse",
          "dimension": "Ept",
          "name": "Professional Vocabulary",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept03",
          "veto": false
        },
        "Ept04": {
          "criterion": "Parameters, thresholds, examples are actionable",
          "dimension": "Ept",
          "name": "Technical Depth",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept04",
          "veto": false
        },
        "Ept05": {
          "criterion": "Analysis method is reproducible",
          "dimension": "Ept",
          "name": "Methodology Rigor",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept05",
          "veto": false
        },
        "Ept06": {
          "criterion": "Discusses ≥2 exceptions or \"when this doesn't apply\"",
          "dimension": "Ept",
          "name": "Edge Case Awareness",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept06",
          "veto": false
        },
        "Ept07": {
          "criterion": "Shows knowledge of the field's evolution",
          "dimension": "Ept",
          "name": "Historical Context",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept07",
          "veto": false
        },
        "Ept08": {
          "criterion": "\"We chose A over B because...\" with tradeoffs",
          "dimension": "Ept",
          "name": "Reasoning Transparency",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept08",
          "veto": false
        },
        "Ept09": {
          "criterion": "Connects knowledge across fields",
          "dimension": "Ept",
          "name": "Cross-domain Integration",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept09",
          "veto": false
        },
        "Ept10": {
          "criterion": "\"Reviewed by\" or \"Fact-checked by\" labels",
          "dimension": "Ept",
          "name": "Editorial Process",
          "policy": {},
          "qualified_id": "CORE-EEAT-Ept10",
          "veto": false
        },
        "Exp01": {
          "criterion": "Contains \"I tested\" or \"We found\" + action verbs",
          "dimension": "Exp",
          "name": "First-Person Narrative",
          "policy": {
            "applicability": "conditional",
            "condition": "first-person experience is claimed or required by the profile"
          },
          "qualified_id": "CORE-EEAT-Exp01",
          "veto": false
        },
        "Exp02": {
          "criterion": "≥10 sensory words (smooth, heavy, bright)",
          "dimension": "Exp",
          "name": "Sensory Details",
          "policy": {
            "applicability": "conditional",
            "condition": "sensory observation is material to the subject"
          },
          "qualified_id": "CORE-EEAT-Exp02",
          "veto": false
        },
        "Exp03": {
          "criterion": "Step-by-step process with timeline",
          "dimension": "Exp",
          "name": "Process Documentation",
          "policy": {},
          "qualified_id": "CORE-EEAT-Exp03",
          "veto": false
        },
        "Exp04": {
          "criterion": "≥2 original photos/screenshots with timestamps",
          "dimension": "Exp",
          "name": "Tangible Proof",
          "policy": {
            "applicability": "conditional",
            "condition": "the artifact claims hands-on use"
          },
          "qualified_id": "CORE-EEAT-Exp04",
          "veto": false
        },
        "Exp05": {
          "criterion": "States \"after X months of use...\"",
          "dimension": "Exp",
          "name": "Usage Duration",
          "policy": {
            "applicability": "conditional",
            "condition": "usage duration is material"
          },
          "qualified_id": "CORE-EEAT-Exp05",
          "veto": false
        },
        "Exp06": {
          "criterion": "Shares ≥2 real problems + solutions",
          "dimension": "Exp",
          "name": "Problems Encountered",
          "policy": {},
          "qualified_id": "CORE-EEAT-Exp06",
          "veto": false
        },
        "Exp07": {
          "criterion": "Shows change, improvement, or difference",
          "dimension": "Exp",
          "name": "Before/After Comparison",
          "policy": {
            "applicability": "conditional",
            "condition": "a before/after claim is made"
          },
          "qualified_id": "CORE-EEAT-Exp07",
          "veto": false
        },
        "Exp08": {
          "criterion": "Measurable experience data (time, cost, success rate)",
          "dimension": "Exp",
          "name": "Quantified Metrics",
          "policy": {},
          "qualified_id": "CORE-EEAT-Exp08",
          "veto": false
        },
        "Exp09": {
          "criterion": "Multiple tests or long-term tracking",
          "dimension": "Exp",
          "name": "Repeated Testing",
          "policy": {
            "applicability": "conditional",
            "condition": "repeat testing is claimed"
          },
          "qualified_id": "CORE-EEAT-Exp09",
          "veto": false
        },
        "Exp10": {
          "criterion": "States \"we only tested X scenario\"",
          "dimension": "Exp",
          "name": "Limitations Acknowledged",
          "policy": {},
          "qualified_id": "CORE-EEAT-Exp10",
          "veto": false
        },
        "O01": {
          "criterion": "H1→H2→H3, no level skipping",
          "dimension": "O",
          "name": "Heading Hierarchy",
          "policy": {},
          "qualified_id": "CORE-EEAT-O01",
          "veto": false
        },
        "O02": {
          "criterion": "Has TL;DR or Key Takeaways section",
          "dimension": "O",
          "name": "Summary Box",
          "policy": {},
          "qualified_id": "CORE-EEAT-O02",
          "veto": false
        },
        "O03": {
          "criterion": "Comparisons and specs presented in tables",
          "dimension": "O",
          "name": "Data Tables",
          "policy": {
            "applicability": "conditional",
            "condition": "the artifact contains comparable structured data"
          },
          "qualified_id": "CORE-EEAT-O03",
          "veto": false
        },
        "O04": {
          "criterion": "Parallel items use bullet or numbered lists",
          "dimension": "O",
          "name": "List Formatting",
          "policy": {},
          "qualified_id": "CORE-EEAT-O04",
          "veto": false
        },
        "O05": {
          "criterion": "Appropriate JSON-LD (Article/FAQ/HowTo/etc.)",
          "dimension": "O",
          "name": "Schema Markup",
          "policy": {
            "applicability": "conditional",
            "condition": "the artifact is an indexable web page eligible for structured data"
          },
          "qualified_id": "CORE-EEAT-O05",
          "veto": false
        },
        "O06": {
          "criterion": "Each section has single topic; paragraphs 3–5 sentences",
          "dimension": "O",
          "name": "Section Chunking",
          "policy": {},
          "qualified_id": "CORE-EEAT-O06",
          "veto": false
        },
        "O07": {
          "criterion": "Key concepts bolded or highlighted",
          "dimension": "O",
          "name": "Visual Hierarchy",
          "policy": {},
          "qualified_id": "CORE-EEAT-O07",
          "veto": false
        },
        "O08": {
          "criterion": "Table of contents with jump links",
          "dimension": "O",
          "name": "Anchor Navigation",
          "policy": {},
          "qualified_id": "CORE-EEAT-O08",
          "veto": false
        },
        "O09": {
          "criterion": "No filler; consistent terminology throughout",
          "dimension": "O",
          "name": "Information Density",
          "policy": {},
          "qualified_id": "CORE-EEAT-O09",
          "veto": false
        },
        "O10": {
          "criterion": "Images/videos have captions and carry information",
          "dimension": "O",
          "name": "Multimedia Structure",
          "policy": {
            "applicability": "conditional",
            "condition": "multimedia is part of the declared artifact"
          },
          "qualified_id": "CORE-EEAT-O10",
          "veto": false
        },
        "R01": {
          "criterion": "≥5 precise numbers with units (%, $, ms)",
          "dimension": "R",
          "name": "Data Precision",
          "policy": {},
          "qualified_id": "CORE-EEAT-R01",
          "veto": false
        },
        "R02": {
          "criterion": "≥1 external citation per 500 words",
          "dimension": "R",
          "name": "Citation Density",
          "policy": {},
          "qualified_id": "CORE-EEAT-R02",
          "veto": false
        },
        "R03": {
          "criterion": "Primary sources first; ≥3 Tier 1–2 sources",
          "dimension": "R",
          "name": "Source Hierarchy",
          "policy": {},
          "qualified_id": "CORE-EEAT-R03",
          "veto": false
        },
        "R04": {
          "criterion": "Every claim backed by evidence immediately after",
          "dimension": "R",
          "name": "Evidence-Claim Mapping",
          "policy": {},
          "qualified_id": "CORE-EEAT-R04",
          "veto": false
        },
        "R05": {
          "criterion": "Sample size, steps, and criteria documented",
          "dimension": "R",
          "name": "Methodology Transparency",
          "policy": {},
          "qualified_id": "CORE-EEAT-R05",
          "veto": false
        },
        "R06": {
          "criterion": "Last updated <1 year; version changes noted",
          "dimension": "R",
          "name": "Timestamp & Versioning",
          "policy": {},
          "qualified_id": "CORE-EEAT-R06",
          "veto": false
        },
        "R07": {
          "criterion": "Full names for people/orgs/products; no \"a company\"",
          "dimension": "R",
          "name": "Entity Precision",
          "policy": {},
          "qualified_id": "CORE-EEAT-R07",
          "veto": false
        },
        "R08": {
          "criterion": "Descriptive anchor texts forming topic clusters",
          "dimension": "R",
          "name": "Internal Link Graph",
          "policy": {},
          "qualified_id": "CORE-EEAT-R08",
          "veto": false
        },
        "R09": {
          "criterion": "Uses `<article>`, `<figure>`, `<time>`, `<cite>",
          "dimension": "R",
          "name": "HTML Semantics",
          "policy": {},
          "qualified_id": "CORE-EEAT-R09",
          "veto": false
        },
        "R10": {
          "criterion": "No material internal factual contradiction; isolated broken links are remediable findings",
          "dimension": "R",
          "name": "Content Consistency",
          "policy": {},
          "qualified_id": "CORE-EEAT-R10",
          "veto": true
        },
        "T01": {
          "criterion": "Privacy Policy + Terms of Service present",
          "dimension": "T",
          "name": "Legal Compliance",
          "policy": {},
          "qualified_id": "CORE-EEAT-T01",
          "veto": false
        },
        "T02": {
          "criterion": "Physical address or ≥2 contact methods",
          "dimension": "T",
          "name": "Contact Transparency",
          "policy": {},
          "qualified_id": "CORE-EEAT-T02",
          "veto": false
        },
        "T03": {
          "criterion": "Site-wide HTTPS, no security warnings",
          "dimension": "T",
          "name": "Security Standards",
          "policy": {},
          "qualified_id": "CORE-EEAT-T03",
          "veto": false
        },
        "T04": {
          "criterion": "Material connections are clearly disclosed where present (conditional veto)",
          "dimension": "T",
          "name": "Disclosure Statements",
          "policy": {
            "applicability": "conditional",
            "condition": "a material connection, paid placement, or affiliate relationship exists",
            "veto": true
          },
          "qualified_id": "CORE-EEAT-T04",
          "veto": true
        },
        "T05": {
          "criterion": "Content standards and review process published",
          "dimension": "T",
          "name": "Editorial Policy",
          "policy": {},
          "qualified_id": "CORE-EEAT-T05",
          "veto": false
        },
        "T06": {
          "criterion": "Has corrections page or changelog",
          "dimension": "T",
          "name": "Correction & Update Policy",
          "policy": {},
          "qualified_id": "CORE-EEAT-T06",
          "veto": false
        },
        "T07": {
          "criterion": "Ads <30% of page; no intrusive popups",
          "dimension": "T",
          "name": "Ad Experience",
          "policy": {},
          "qualified_id": "CORE-EEAT-T07",
          "veto": false
        },
        "T08": {
          "criterion": "YMYL topics have necessary disclaimers",
          "dimension": "T",
          "name": "Risk Disclaimers",
          "policy": {
            "applicability": "conditional",
            "condition": "the artifact makes YMYL or other material-risk claims"
          },
          "qualified_id": "CORE-EEAT-T08",
          "veto": false
        },
        "T09": {
          "criterion": "Reviews show authenticity signals",
          "dimension": "T",
          "name": "Review Authenticity",
          "policy": {},
          "qualified_id": "CORE-EEAT-T09",
          "veto": false
        },
        "T10": {
          "criterion": "Clear return policy, complaint channels, response SLA",
          "dimension": "T",
          "name": "Customer Support",
          "policy": {},
          "qualified_id": "CORE-EEAT-T10",
          "veto": false
        }
      },
      "profiles": {
        "alternative": {
          "context_equals": {
            "content_type": "alternative"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.05,
            "Ept": 0.05,
            "Exp": 0.15,
            "O": 0.15,
            "R": 0.25,
            "T": 0.2
          }
        },
        "best-of": {
          "context_equals": {
            "content_type": "best-of"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.15,
            "Ept": 0.1,
            "Exp": 0.05,
            "O": 0.25,
            "R": 0.2,
            "T": 0.1
          }
        },
        "blog-post": {
          "context_equals": {
            "content_type": "blog-post"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.25,
            "E": 0.2,
            "Ept": 0.1,
            "Exp": 0.1,
            "O": 0.1,
            "R": 0.1,
            "T": 0.1
          }
        },
        "comparison": {
          "context_equals": {
            "content_type": "comparison"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.1,
            "Ept": 0.15,
            "Exp": 0.05,
            "O": 0.2,
            "R": 0.25,
            "T": 0.1
          }
        },
        "faq-page": {
          "context_equals": {
            "content_type": "faq-page"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.25,
            "E": 0.05,
            "Ept": 0.1,
            "Exp": 0.05,
            "O": 0.25,
            "R": 0.15,
            "T": 0.1
          }
        },
        "how-to-guide": {
          "context_equals": {
            "content_type": "how-to-guide"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.2,
            "E": 0.05,
            "Ept": 0.2,
            "Exp": 0.05,
            "O": 0.2,
            "R": 0.1,
            "T": 0.15
          }
        },
        "landing-page": {
          "context_equals": {
            "content_type": "landing-page"
          },
          "dimensions": {
            "A": 0.25,
            "C": 0.2,
            "E": 0.05,
            "Ept": 0.05,
            "Exp": 0.05,
            "O": 0.1,
            "R": 0.05,
            "T": 0.25
          }
        },
        "product-review": {
          "context_equals": {
            "content_type": "product-review"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.2,
            "Ept": 0.05,
            "Exp": 0.2,
            "O": 0.1,
            "R": 0.15,
            "T": 0.15
          }
        },
        "testimonial": {
          "context_equals": {
            "content_type": "testimonial"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.1,
            "Ept": 0.05,
            "Exp": 0.3,
            "O": 0.05,
            "R": 0.15,
            "T": 0.2
          }
        }
      },
      "required_context": [
        "content_type",
        "market",
        "publication_state"
      ],
      "source": "references/core-eeat-benchmark.md",
      "unit_of_analysis": "one content artifact at one observation date",
      "veto_items": [
        "T04",
        "C01",
        "R10"
      ]
    }
  },
  "semantics": {
    "bands": [
      {
        "maximum": 100,
        "minimum": 90,
        "name": "Excellent"
      },
      {
        "maximum": 89,
        "minimum": 75,
        "name": "Good"
      },
      {
        "maximum": 74,
        "minimum": 60,
        "name": "Medium"
      },
      {
        "maximum": 59,
        "minimum": 40,
        "name": "Low"
      },
      {
        "maximum": 39,
        "minimum": 0,
        "name": "Poor"
      }
    ],
    "confidence_factors": {
      "high": 1.0,
      "low": 0.5,
      "medium": 0.75
    },
    "evidence_types": {
      "calculated": 0.8,
      "estimated": 0.5,
      "measured": 1.0,
      "proxy": 0.4,
      "user-provided": 0.8
    },
    "external_validity": "advisory-until-outcome-calibrated",
    "item_points": {
      "fail": 0,
      "partial": 5,
      "pass": 10
    },
    "missingness": {
      "missing": "treated as unknown, never as partial or fail",
      "na": "genuinely inapplicable under an item policy; requires a reason and is excluded",
      "unknown": "applicable but not observed; prevents a comparable total score"
    },
    "multi_veto": {
      "emit_final_score": false,
      "minimum": 2,
      "verdict": "BLOCK"
    },
    "required_coverage": 100,
    "rounding": "floor",
    "score_states": [
      "pass",
      "partial",
      "fail",
      "unknown",
      "na"
    ],
    "veto_ceiling": 59
  },
  "standalone_observation_contract": {
    "evidence_types": [
      "measured",
      "user-provided",
      "calculated",
      "estimated",
      "proxy"
    ],
    "item_states": [
      "pass",
      "partial",
      "fail",
      "unknown",
      "na"
    ],
    "result": {
      "score_confidence": "not_scored",
      "score_state": "NOT_SCORED",
      "status": [
        "NEEDS_INPUT",
        "BLOCKED"
      ],
      "verdict": "UNDECIDED"
    }
  }
}
```

## Standalone Execution Policy

1. Select exactly one declared profile from the typed snapshot and record it with the catalog version and source digest above.
2. Collect one state per applicable item using the run-schema vocabulary: `pass`, `partial`, `fail`, `na`, or `unknown` — the same states the root scorer replays later. Every non-unknown state needs evidence; never convert missing evidence into a pass.
3. Record veto observations by their qualified framework item IDs, but do not calculate dimension, raw, capped, or final scores without the root deterministic scorer.
4. Return `status: NEEDS_INPUT` or `status: BLOCKED` with `verdict: UNDECIDED`, `score_state: NOT_SCORED`, and `score_confidence: not_scored`. Clearly identify the unavailable root runtime as the reason.
5. Do not write under `memory/audits/`, mutate registries, or claim a publish/ship decision. Offer the observation set for later execution in a full plugin or repository install.
6. Do not search parent directories, accept an unverified runtime root, download repository files, or hand-calculate a substitute score.

The complete item definitions above are compiled from the authoritative benchmark. The source digest binds this compact fallback to the runbook, scoring semantics, benchmark, run schema, and artifact schema; those maintenance documents remain repository-only and are not misrepresented as separately bundled files.

---

End of generated standalone runtime.
