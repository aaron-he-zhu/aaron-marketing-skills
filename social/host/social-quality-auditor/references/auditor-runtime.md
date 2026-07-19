<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** ECHO
- **Auditor:** social-quality-auditor
- **Source digest:** `sha256:4c3012cee53e65444d7611bb3a75578dfc6324ef9adb52f1155fb94dbb744d74`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
  "frameworks": {
    "ECHO": {
      "composite_score": false,
      "construct": "separate social asset compliance and program operating maturity reads",
      "dimensions": {
        "C": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "C",
          "name": "Craft"
        },
        "E": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "E",
          "name": "Embeddedness"
        },
        "H": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "H",
          "name": "Hosting"
        },
        "O": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "O",
          "name": "Observability"
        }
      },
      "item_policies": {
        "C1": {
          "applicability": "conditional",
          "condition": "the asset makes a product or offer claim",
          "veto": true
        },
        "C2": {
          "applicability": "conditional",
          "condition": "a material connection or realistic synthetic media exists",
          "veto": true
        },
        "E1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "H1": {
          "veto": true
        },
        "H2": {
          "applicability": "conditional",
          "condition": "third-party UGC is republished outside a native share",
          "veto": true
        },
        "O1": {
          "asset_gate_note": "an observed asset with no performance rate or metric claim may pass this control; do not infer from missing asset access",
          "unknown_policy": "needs-input",
          "veto": true
        }
      },
      "outcomes": "reported as measured metrics with controls; no rubric score until outcome calibration exists",
      "profiles": {
        "asset-gate": {
          "context_equals": {
            "assessment_mode": "asset",
            "program_archetype": "not-applicable"
          },
          "dimensions": {
            "C": 0.6,
            "E": 0.1,
            "H": 0.2,
            "O": 0.1
          },
          "include_items": {
            "E": [
              "E1"
            ],
            "H": [
              "H1",
              "H2"
            ],
            "O": [
              "O1"
            ]
          }
        },
        "program-maturity-b2c": {
          "context_equals": {
            "assessment_mode": "program",
            "program_archetype": "b2c"
          },
          "dimensions": {
            "E": 0.2,
            "H": 0.4,
            "O": 0.4
          }
        },
        "program-maturity-community": {
          "context_equals": {
            "assessment_mode": "program",
            "program_archetype": "community"
          },
          "dimensions": {
            "E": 0.375,
            "H": 0.375,
            "O": 0.25
          }
        },
        "program-maturity-founder": {
          "context_equals": {
            "assessment_mode": "program",
            "program_archetype": "founder"
          },
          "dimensions": {
            "E": 0.285,
            "H": 0.215,
            "O": 0.5
          }
        }
      },
      "required_context": [
        "assessment_mode",
        "program_archetype",
        "channels",
        "window",
        "market"
      ],
      "source": "references/echo-benchmark.md",
      "unit_of_analysis": "one asset gate or one channel portfolio/window, never both in one score",
      "veto_items": [
        "E1",
        "C1",
        "C2",
        "H1",
        "H2",
        "O1"
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
