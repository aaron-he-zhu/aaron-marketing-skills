<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** ROAS
- **Auditor:** ad-account-auditor
- **Source digest:** `sha256:b1a08e620f3c06a3752453da57de3cabc02a924faa9b4d5ab7772e666c8f4441`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
  "frameworks": {
    "ROAS": {
      "construct": "incremental paid-media contribution and operating quality under declared business constraints",
      "dimensions": {
        "A": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "A",
          "name": "Audience"
        },
        "O": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "O",
          "name": "Offer"
        },
        "R": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "R",
          "name": "Return"
        },
        "S": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "S",
          "name": "Spend Efficiency"
        }
      },
      "item_definitions": {
        "A1": "brand and placement safety verified from the placement evidence",
        "A2": "targeting and query/audience intent fit",
        "A3": "negative keywords, exclusions, and suppression controls are maintained",
        "A4": "campaign/account structure supports the declared objective without avoidable overlap",
        "A5": "reach, overlap, and audience saturation are measured",
        "O1": "claims and required disclosures are substantiated",
        "O2": "platform policy and restricted-category requirements are satisfied",
        "O3": "offer economics, eligibility, terms, and availability are explicit",
        "O4": "ad-to-landing message and intent match",
        "O5": "creative hook, format, accessibility, and fatigue state fit the placement",
        "R1": "conversion instrumentation verified against an own-data truth set",
        "R2": "cross-platform attribution deduplicated and windows/currency normalized",
        "R3": "incremental contribution or profit measured against the declared target/control",
        "R4": "CAC/CPA and payback satisfy the declared business constraint",
        "R5": "marginal return is read after conversion lag with uncertainty stated",
        "S1": "budget pacing stays within the declared plan and constraints",
        "S2": "bid strategy and learning-state changes are governed",
        "S3": "marginal CPC/CPM/CTR/CVR efficiency is compared on a normalized window",
        "S4": "frequency and creative decay are separated from audience saturation",
        "S5": "paid/organic and cross-campaign cannibalization are assessed"
      },
      "item_policies": {
        "A1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "O1": {
          "veto": true
        },
        "O2": {
          "veto": true
        },
        "R1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "R2": {
          "unknown_policy": "needs-input",
          "veto": true
        }
      },
      "profiles": {
        "direct-response": {
          "context_equals": {
            "goal": "direct-response"
          },
          "dimensions": {
            "A": 0.15,
            "O": 0.2,
            "R": 0.4,
            "S": 0.25
          }
        },
        "incremental-profit": {
          "context_equals": {
            "goal": "incremental-profit"
          },
          "dimensions": {
            "A": 0.1,
            "O": 0.15,
            "R": 0.5,
            "S": 0.25
          }
        },
        "prospecting": {
          "context_equals": {
            "goal": "prospecting"
          },
          "dimensions": {
            "A": 0.3,
            "O": 0.3,
            "R": 0.15,
            "S": 0.25
          }
        }
      },
      "required_context": [
        "currency",
        "window",
        "conversion_lag",
        "business_constraint",
        "goal"
      ],
      "source": "references/roas-benchmark.md",
      "unit_of_analysis": "one account/campaign portfolio, currency, attribution window, and observation period",
      "veto_items": [
        "R1",
        "R2",
        "O1",
        "O2",
        "A1"
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
