<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** CITE
- **Auditor:** domain-authority-auditor
- **Source digest:** `sha256:6eb213ca78b35e7afb9fbb453defc0b3fe3bd573efc52765c8fe515db2f967c4`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
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

The source digest binds this compact fallback to the authoritative runbook, scoring semantics, framework benchmark, run schema, and artifact schema without copying those maintenance sources into every standalone bundle.

---

End of generated standalone runtime.
