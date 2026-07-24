<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.0.0
- **Framework:** RAMP
- **Auditor:** launch-readiness-auditor
- **Source digest:** `sha256:4981618e960d50e82af95895afb074c3b9d1177c49d5ba04747202aab3611c78`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.0.0",
  "frameworks": {
    "RAMP": {
      "composite_score": false,
      "construct": "three non-interchangeable launch reads: preflight readiness, execution quality, and observed outcomes",
      "dimensions": {
        "A": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "A",
          "name": "Assets"
        },
        "M": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "M",
          "name": "Momentum Execution"
        },
        "P": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "P",
          "name": "Proof Outcomes"
        },
        "R": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "R",
          "name": "Readiness"
        }
      },
      "item_policies": {
        "A1": {
          "veto": true
        },
        "M1": {
          "veto": true
        },
        "P1": {
          "definition": "required launch surfaces have verified measurement, using N/A for genuinely non-participating surfaces",
          "unknown_policy": "needs-input",
          "veto": true
        },
        "R1": {
          "definition": "declared lifecycle stage contradicts verifiable access/eligibility; a public pricing page is not universally required",
          "veto": true
        }
      },
      "profiles": {
        "execution": {
          "context_equals": {
            "lifecycle_read": "execution"
          },
          "dimensions": {
            "M": 1.0
          }
        },
        "outcome": {
          "context_equals": {
            "lifecycle_read": "outcome"
          },
          "dimensions": {
            "P": 1.0
          },
          "exclude_items": {
            "P": [
              "P1"
            ]
          }
        },
        "preflight": {
          "context_equals": {
            "lifecycle_read": "preflight"
          },
          "dimensions": {
            "A": 0.4,
            "M": 0.1,
            "P": 0.1,
            "R": 0.4
          },
          "include_items": {
            "M": [
              "M1"
            ],
            "P": [
              "P1"
            ]
          }
        }
      },
      "required_context": [
        "launch_type",
        "lifecycle_read",
        "market",
        "access_model"
      ],
      "source": "references/ramp-benchmark.md",
      "unit_of_analysis": "one launch at one declared lifecycle read",
      "veto_items": [
        "R1",
        "A1",
        "M1",
        "P1"
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
