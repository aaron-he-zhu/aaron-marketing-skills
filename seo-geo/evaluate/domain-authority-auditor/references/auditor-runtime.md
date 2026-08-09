<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** CITE
- **Auditor:** domain-authority-auditor
- **Complete item definitions:** 40
- **Source digest:** `sha256:7c7308b1b06c62a04c447109130068253cdbb55d4c8c63e3a981200f800b96dd`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
  "frameworks": {
    "CITE": {
      "benchmark_mode": "peer-relative; absolute thresholds are diagnostic starting points only",
      "construct": "domain citation-trust signals relative to a declared peer cohort",
      "dimensions": {
        "C": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "C",
          "name": "Citations"
        },
        "E": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "E",
          "name": "Eminence"
        },
        "I": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "I",
          "name": "Identity"
        },
        "T": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "T",
          "name": "Trust"
        }
      },
      "item_policies": {
        "C05": {
          "applicability": "conditional",
          "condition": "a locked AI-answer query panel is declared"
        },
        "C06": {
          "applicability": "conditional",
          "condition": "AI citations were observed on the locked panel"
        },
        "C07": {
          "applicability": "conditional",
          "condition": "multiple AI engines are in scope"
        },
        "E09": {
          "applicability": "conditional",
          "condition": "multi-region reach is part of the domain objective"
        },
        "I06": {
          "benchmark": "peer-relative by entity stage; domain age alone cannot fail trust"
        },
        "T03": {
          "benchmark": "declared peer distribution required",
          "unknown_policy": "needs-input",
          "veto": true
        },
        "T05": {
          "benchmark": "declared comparison universe required",
          "unknown_policy": "needs-input",
          "veto": true
        },
        "T06": {
          "benchmark": "privacy-protected WHOIS is neutral absent contradictory ownership evidence"
        },
        "T09": {
          "condition": "verified manual-action or deindex evidence; lack of private console access is unknown",
          "unknown_policy": "needs-input",
          "veto": true
        }
      },
      "items": {
        "C01": {
          "criterion": ">=500 unique referring domains",
          "dimension": "C",
          "name": "Referring Domains Volume",
          "policy": {},
          "qualified_id": "CITE-C01",
          "veto": false
        },
        "C02": {
          "criterion": ">=20% of referring domains have DA (Moz Domain Authority™) / DR (Ahrefs Domain Rating™) 50+",
          "dimension": "C",
          "name": "Referring Domains Quality",
          "policy": {},
          "qualified_id": "CITE-C02",
          "veto": false
        },
        "C03": {
          "criterion": "Top sources concentrate outbound links (<1,000 outbound domains)",
          "dimension": "C",
          "name": "Link Equity Distribution",
          "policy": {},
          "qualified_id": "CITE-C03",
          "veto": false
        },
        "C04": {
          "criterion": "Steady natural growth; no month >3x average",
          "dimension": "C",
          "name": "Link Velocity",
          "policy": {},
          "qualified_id": "CITE-C04",
          "veto": false
        },
        "C05": {
          "criterion": "Cited by >=2 AI engines on >=10 niche queries",
          "dimension": "C",
          "name": "AI Citation Frequency",
          "policy": {
            "applicability": "conditional",
            "condition": "a locked AI-answer query panel is declared"
          },
          "qualified_id": "CITE-C05",
          "veto": false
        },
        "C06": {
          "criterion": "Primary/sole source in >=50% of AI citations",
          "dimension": "C",
          "name": "AI Citation Prominence",
          "policy": {
            "applicability": "conditional",
            "condition": "AI citations were observed on the locked panel"
          },
          "qualified_id": "CITE-C06",
          "veto": false
        },
        "C07": {
          "criterion": "Cited by >=3 different AI engines",
          "dimension": "C",
          "name": "Cross-Engine Citation",
          "policy": {
            "applicability": "conditional",
            "condition": "multiple AI engines are in scope"
          },
          "qualified_id": "CITE-C07",
          "veto": false
        },
        "C08": {
          "criterion": ">=80% of citations in positive/neutral context",
          "dimension": "C",
          "name": "Citation Sentiment",
          "policy": {},
          "qualified_id": "CITE-C08",
          "veto": false
        },
        "C09": {
          "criterion": ">=60% of backlinks from editorial decisions",
          "dimension": "C",
          "name": "Editorial Link Ratio",
          "policy": {},
          "qualified_id": "CITE-C09",
          "veto": false
        },
        "C10": {
          "criterion": "Referring domains span >=3 industries, >=5 regions",
          "dimension": "C",
          "name": "Link Source Diversity",
          "policy": {},
          "qualified_id": "CITE-C10",
          "veto": false
        },
        "E01": {
          "criterion": "Ranks for >=1,000 keywords in top 100",
          "dimension": "E",
          "name": "Organic Search Visibility",
          "policy": {},
          "qualified_id": "CITE-E01",
          "veto": false
        },
        "E02": {
          "criterion": ">=10,000 estimated monthly organic visits",
          "dimension": "E",
          "name": "Organic Traffic Estimate",
          "policy": {},
          "qualified_id": "CITE-E02",
          "veto": false
        },
        "E03": {
          "criterion": "Appears in >=3 SERP feature types",
          "dimension": "E",
          "name": "SERP Feature Ownership",
          "policy": {},
          "qualified_id": "CITE-E03",
          "veto": false
        },
        "E04": {
          "criterion": "AI-crawler-friendly robots.txt; clean rendering; <3s load",
          "dimension": "E",
          "name": "Technical Crawlability",
          "policy": {},
          "qualified_id": "CITE-E04",
          "veto": false
        },
        "E05": {
          "criterion": "Official presence on >=3 major platforms with recent activity",
          "dimension": "E",
          "name": "Multi-Platform Footprint",
          "policy": {},
          "qualified_id": "CITE-E05",
          "veto": false
        },
        "E06": {
          "criterion": "Featured in >=3 authoritative publications",
          "dimension": "E",
          "name": "Authoritative Media Coverage",
          "policy": {},
          "qualified_id": "CITE-E06",
          "veto": false
        },
        "E07": {
          "criterion": "Ranks for long-tail (4+ word) keywords deep in niche",
          "dimension": "E",
          "name": "Topical Authority Depth",
          "policy": {},
          "qualified_id": "CITE-E07",
          "veto": false
        },
        "E08": {
          "criterion": "Covers >=70% of sub-topics in primary niche",
          "dimension": "E",
          "name": "Topical Authority Breadth",
          "policy": {},
          "qualified_id": "CITE-E08",
          "veto": false
        },
        "E09": {
          "criterion": "Organic traffic from >=10 countries/regions",
          "dimension": "E",
          "name": "Geographic Reach",
          "policy": {
            "applicability": "conditional",
            "condition": "multi-region reach is part of the domain objective"
          },
          "qualified_id": "CITE-E09",
          "veto": false
        },
        "E10": {
          "criterion": ">=5% visibility share across top 50 industry keywords",
          "dimension": "E",
          "name": "Industry Share of Voice",
          "policy": {},
          "qualified_id": "CITE-E10",
          "veto": false
        },
        "I01": {
          "criterion": "Entity in >=2 knowledge graphs (Google KG, Wikidata, DBpedia)",
          "dimension": "I",
          "name": "Knowledge Graph Presence",
          "policy": {},
          "qualified_id": "CITE-I01",
          "veto": false
        },
        "I02": {
          "criterion": "Brand name >=1,000 monthly exact-match searches",
          "dimension": "I",
          "name": "Brand Search Volume",
          "policy": {},
          "qualified_id": "CITE-I02",
          "veto": false
        },
        "I03": {
          "criterion": "Brand search yields >=7 first-page results you control",
          "dimension": "I",
          "name": "Brand SERP Ownership",
          "policy": {},
          "qualified_id": "CITE-I03",
          "veto": false
        },
        "I04": {
          "criterion": ">=50% of indexable pages with correct Schema.org markup",
          "dimension": "I",
          "name": "Schema.org Coverage",
          "policy": {},
          "qualified_id": "CITE-I04",
          "veto": false
        },
        "I05": {
          "criterion": ">=80% of content has authors with verifiable public identities",
          "dimension": "I",
          "name": "Author Entity Recognition",
          "policy": {},
          "qualified_id": "CITE-I05",
          "veto": false
        },
        "I06": {
          "criterion": "History is coherent relative to entity stage; age alone cannot fail the domain",
          "dimension": "I",
          "name": "Domain Tenure",
          "policy": {
            "benchmark": "peer-relative by entity stage; domain age alone cannot fail trust"
          },
          "qualified_id": "CITE-I06",
          "veto": false
        },
        "I07": {
          "criterion": "Brand name/description/contact identical across all platforms",
          "dimension": "I",
          "name": "Cross-Platform Consistency",
          "policy": {},
          "qualified_id": "CITE-I07",
          "veto": false
        },
        "I08": {
          "criterion": "Same niche for >=3 consecutive years without major pivot",
          "dimension": "I",
          "name": "Niche Consistency",
          "policy": {},
          "qualified_id": "CITE-I08",
          "veto": false
        },
        "I09": {
          "criterion": ">=50 third-party mentions without links",
          "dimension": "I",
          "name": "Unlinked Brand Mentions",
          "policy": {},
          "qualified_id": "CITE-I09",
          "veto": false
        },
        "I10": {
          "criterion": "Brand appears in industry query autocomplete",
          "dimension": "I",
          "name": "Query-Brand Association",
          "policy": {},
          "qualified_id": "CITE-I10",
          "veto": false
        },
        "T01": {
          "criterion": "No month >15% of total backlinks; growth correlates with publishing",
          "dimension": "T",
          "name": "Link Profile Naturalness",
          "policy": {},
          "qualified_id": "CITE-T01",
          "veto": false
        },
        "T02": {
          "criterion": "Dofollow 40-85% of total backlinks",
          "dimension": "T",
          "name": "Dofollow Ratio Normality",
          "policy": {},
          "qualified_id": "CITE-T02",
          "veto": false
        },
        "T03": {
          "criterion": "Link/traffic relationship is coherent within the declared peer distribution (**Veto Item**)",
          "dimension": "T",
          "name": "Link-Traffic Coherence",
          "policy": {
            "benchmark": "declared peer distribution required",
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "CITE-T03",
          "veto": true
        },
        "T04": {
          "criterion": ">=100 unique C-class IP ranges; no single C-class >5%",
          "dimension": "T",
          "name": "IP/Network Diversity",
          "policy": {},
          "qualified_id": "CITE-T04",
          "veto": false
        },
        "T05": {
          "criterion": "No verified manipulation network after common-source adjustment (**Veto Item**)",
          "dimension": "T",
          "name": "Backlink Profile Uniqueness",
          "policy": {
            "benchmark": "declared comparison universe required",
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "CITE-T05",
          "veto": true
        },
        "T06": {
          "criterion": "Ownership history is coherent; privacy-protected WHOIS is neutral",
          "dimension": "T",
          "name": "WHOIS & Registration Transparency",
          "policy": {
            "benchmark": "privacy-protected WHOIS is neutral absent contradictory ownership evidence"
          },
          "qualified_id": "CITE-T06",
          "veto": false
        },
        "T07": {
          "criterion": "Site-wide HTTPS + HSTS; no malware/phishing flags",
          "dimension": "T",
          "name": "Technical Security",
          "policy": {},
          "qualified_id": "CITE-T07",
          "veto": false
        },
        "T08": {
          "criterion": "New/updated content within last 90 days",
          "dimension": "T",
          "name": "Content Freshness Signal",
          "policy": {},
          "qualified_id": "CITE-T08",
          "veto": false
        },
        "T09": {
          "criterion": "No verified active manual action or deindexing (**Veto Item**)",
          "dimension": "T",
          "name": "Penalty & Deindex History",
          "policy": {
            "condition": "verified manual-action or deindex evidence; lack of private console access is unknown",
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "CITE-T09",
          "veto": true
        },
        "T10": {
          "criterion": ">=3.5/5 average on >=2 third-party review platforms",
          "dimension": "T",
          "name": "Review & Reputation Signals",
          "policy": {},
          "qualified_id": "CITE-T10",
          "veto": false
        }
      },
      "profiles": {
        "authority-institutional": {
          "context_equals": {
            "domain_type": "authority-institutional"
          },
          "dimensions": {
            "C": 0.45,
            "E": 0.15,
            "I": 0.2,
            "T": 0.2
          }
        },
        "community-ugc": {
          "context_equals": {
            "domain_type": "community-ugc"
          },
          "dimensions": {
            "C": 0.35,
            "E": 0.3,
            "I": 0.1,
            "T": 0.25
          }
        },
        "content-publisher": {
          "context_equals": {
            "domain_type": "content-publisher"
          },
          "dimensions": {
            "C": 0.4,
            "E": 0.25,
            "I": 0.15,
            "T": 0.2
          }
        },
        "default": {
          "dimensions": {
            "C": 0.35,
            "E": 0.2,
            "I": 0.2,
            "T": 0.25
          }
        },
        "ecommerce": {
          "context_equals": {
            "domain_type": "ecommerce"
          },
          "dimensions": {
            "C": 0.2,
            "E": 0.25,
            "I": 0.2,
            "T": 0.35
          }
        },
        "product-service": {
          "context_equals": {
            "domain_type": "product-service"
          },
          "dimensions": {
            "C": 0.25,
            "E": 0.2,
            "I": 0.3,
            "T": 0.25
          }
        },
        "tool-utility": {
          "context_equals": {
            "domain_type": "tool-utility"
          },
          "dimensions": {
            "C": 0.25,
            "E": 0.2,
            "I": 0.3,
            "T": 0.25
          }
        }
      },
      "required_context": [
        "peer_cohort",
        "market",
        "entity_stage",
        "domain_type"
      ],
      "source": "references/cite-domain-rating.md",
      "unit_of_analysis": "one domain and market at one observation date",
      "veto_items": [
        "T03",
        "T05",
        "T09"
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
