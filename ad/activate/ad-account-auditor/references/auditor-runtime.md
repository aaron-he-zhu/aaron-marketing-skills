<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 20.2.0
- **Framework:** ROAS
- **Auditor:** ad-account-auditor
- **Complete item definitions:** 20
- **Source digest:** `sha256:4ecdc592b224cde70f44ba1974b846d9c27e724d65ca3d1c32da8385ae9ff39a`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "20.2.0",
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
      "items": {
        "A1": {
          "criterion": "Brand and placement safety are verified from the placement evidence.",
          "dimension": "A",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "ROAS-A1",
          "veto": true
        },
        "A2": {
          "criterion": "Targeting and query/audience intent fit.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-A2",
          "veto": false
        },
        "A3": {
          "criterion": "Negative keywords, exclusions, and suppression controls are maintained.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-A3",
          "veto": false
        },
        "A4": {
          "criterion": "Campaign/account structure supports the declared objective without avoidable overlap.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-A4",
          "veto": false
        },
        "A5": {
          "criterion": "Reach, overlap and audience saturation use audience-level evidence on one window; frequency alone cannot establish saturation.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-A5",
          "veto": false
        },
        "O1": {
          "criterion": "Claims and required disclosures are substantiated.",
          "dimension": "O",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "ROAS-O1",
          "veto": true
        },
        "O2": {
          "criterion": "Platform policy and restricted-category requirements are satisfied.",
          "dimension": "O",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "ROAS-O2",
          "veto": true
        },
        "O3": {
          "criterion": "Offer economics, eligibility, terms, and availability are explicit.",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-O3",
          "veto": false
        },
        "O4": {
          "criterion": "Ad-to-landing message and intent match.",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-O4",
          "veto": false
        },
        "O5": {
          "criterion": "Creative hook, format, accessibility, and fatigue state fit the placement.",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-O5",
          "veto": false
        },
        "R1": {
          "criterion": "Conversion instrumentation is verified against an own-data truth set.",
          "dimension": "R",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "ROAS-R1",
          "veto": true
        },
        "R2": {
          "criterion": "Cross-platform attribution is deduplicated; attribution windows and currency are normalized.",
          "dimension": "R",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "ROAS-R2",
          "veto": true
        },
        "R3": {
          "criterion": "Incremental contribution/profit is evaluated against the declared target/control; platform-attributed ROAS alone leaves incrementality Unknown, a labeled proxy is not a causal result.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-R3",
          "veto": false
        },
        "R4": {
          "criterion": "CAC/CPA and payback meet the declared business constraints on normalized own-data outcomes; absent constraint/truth set is Unknown.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-R4",
          "veto": false
        },
        "R5": {
          "criterion": "Marginal return uses a completed declared lag window and stated uncertainty; average historical ROAS cannot establish the return on additional spend.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-R5",
          "veto": false
        },
        "S1": {
          "criterion": "Budget pacing remains within the declared plan and constraints.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-S1",
          "veto": false
        },
        "S2": {
          "criterion": "Bid strategy and learning-state changes are governed.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-S2",
          "veto": false
        },
        "S3": {
          "criterion": "Marginal CPC/CPM/CTR/CVR efficiency is compared on a normalized window.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-S3",
          "veto": false
        },
        "S4": {
          "criterion": "Creative-level frequency/decay is separated from audience saturation; aggregate frequency alone cannot establish creative fatigue.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-S4",
          "veto": false
        },
        "S5": {
          "criterion": "Paid/organic and cross-campaign cannibalization are assessed.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "ROAS-S5",
          "veto": false
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
2. Collect one state per applicable item using the run-schema vocabulary: `pass`, `partial`, `fail`, `na`, or `unknown` — the same states the root scorer replays later. Observed pass/partial/fail states need evidence. Unknown needs a gap reason; catalog-authorized na needs a reason and no evidence. Never convert missing evidence into a pass.
3. Record veto observations by their qualified framework item IDs, but do not calculate dimension, raw, capped, or final scores without the root deterministic scorer.
4. Return `status: NEEDS_INPUT` or `status: BLOCKED` with `verdict: UNDECIDED`, `score_state: NOT_SCORED`, and `score_confidence: not_scored`. Clearly identify the unavailable root runtime as the reason.
5. Do not write under `memory/audits/`, mutate registries, or claim a publish/ship decision. Offer the observation set for later execution in a full plugin or repository install.
6. Do not search parent directories, accept an unverified runtime root, download repository files, or hand-calculate a substitute score.

The complete item definitions above are compiled from the authoritative benchmark. The source digest binds this compact fallback to the runbook, scoring semantics, benchmark, run schema, and artifact schema; those maintenance documents remain repository-only and are not misrepresented as separately bundled files.

---

End of generated standalone runtime.
