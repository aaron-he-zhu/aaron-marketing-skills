<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** TALE
- **Auditor:** narrative-quality-auditor
- **Source digest:** `sha256:a8c490313f9ff3002e2e8a89521fe83d12e30339cd66e30086ea81a045ef04a9`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
  "frameworks": {
    "TALE": {
      "composite_score": false,
      "construct": "separate narrative truth, system coherence, and measured effectiveness reads",
      "dimensions": {
        "A": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "A",
          "name": "Architecture"
        },
        "E": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "E",
          "name": "Evidence"
        },
        "L": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "L",
          "name": "Landing"
        },
        "T": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "T",
          "name": "Truth"
        }
      },
      "item_policies": {
        "A1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "A2": {
          "applicability": "conditional",
          "condition": "a message-house pattern is chosen; pillar count is user-justified rather than universally fixed"
        },
        "A4": {
          "applicability": "conditional",
          "condition": "a change-narrative arc is appropriate to the strategy"
        },
        "A8": {
          "applicability": "conditional",
          "condition": "fixed-length boilerplates are operationally required"
        },
        "E1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "L1": {
          "veto": true
        },
        "T1": {
          "definition": "material differentiation is false, contradictory, or unsubstantiated; a literal onlyness claim is not required",
          "veto": true
        }
      },
      "profiles": {
        "effectiveness": {
          "context_equals": {
            "assessment_mode": "effectiveness"
          },
          "dimensions": {
            "E": 1.0
          }
        },
        "system": {
          "context_equals": {
            "assessment_mode": "system"
          },
          "dimensions": {
            "A": 0.5,
            "L": 0.5
          }
        },
        "truth": {
          "context_equals": {
            "assessment_mode": "truth"
          },
          "dimensions": {
            "T": 1.0
          }
        }
      },
      "required_context": [
        "assessment_mode",
        "brand_scope",
        "market",
        "audience"
      ],
      "source": "references/tale-benchmark.md",
      "unit_of_analysis": "one canon/surface set or one message experiment at one observation date",
      "veto_items": [
        "T1",
        "A1",
        "L1",
        "E1"
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
