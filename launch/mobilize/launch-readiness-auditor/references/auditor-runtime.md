<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** RAMP
- **Auditor:** launch-readiness-auditor
- **Complete item definitions:** 40
- **Source digest:** `sha256:e025913cc7d543dcef6813f16926607823766cc53ca93702fc2ddc1001444c69`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
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
      "items": {
        "A1": {
          "criterion": "claim/disclosure integrity",
          "dimension": "A",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "RAMP-A1",
          "veto": true
        },
        "A10": {
          "criterion": "localization/regional readiness where applicable",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A10",
          "veto": false
        },
        "A2": {
          "criterion": "narrative/message architecture",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A2",
          "veto": false
        },
        "A3": {
          "criterion": "proof-point completeness",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A3",
          "veto": false
        },
        "A4": {
          "criterion": "press/facts asset manifest",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A4",
          "veto": false
        },
        "A5": {
          "criterion": "channel-specific asset compliance",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A5",
          "veto": false
        },
        "A6": {
          "criterion": "pricing/offer terms where applicable",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A6",
          "veto": false
        },
        "A7": {
          "criterion": "sales/support enablement where applicable",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A7",
          "veto": false
        },
        "A8": {
          "criterion": "announcement/landing/offer match",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A8",
          "veto": false
        },
        "A9": {
          "criterion": "technical go-live verification",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-A9",
          "veto": false
        },
        "M1": {
          "criterion": "platform/embargo integrity",
          "dimension": "M",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "RAMP-M1",
          "veto": true
        },
        "M10": {
          "criterion": "launch-spacing/capacity guardrail",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M10",
          "veto": false
        },
        "M2": {
          "criterion": "channel mix and dependency risk",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M2",
          "veto": false
        },
        "M3": {
          "criterion": "T-minus execution",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M3",
          "veto": false
        },
        "M4": {
          "criterion": "authoritative date/commitment coordination",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M4",
          "veto": false
        },
        "M5": {
          "criterion": "owned-channel sequence",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M5",
          "veto": false
        },
        "M6": {
          "criterion": "media/partner activation",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M6",
          "veto": false
        },
        "M7": {
          "criterion": "community response operation",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M7",
          "veto": false
        },
        "M8": {
          "criterion": "live monitoring/alerts",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M8",
          "veto": false
        },
        "M9": {
          "criterion": "go/rollback observation windows",
          "dimension": "M",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-M9",
          "veto": false
        },
        "P1": {
          "criterion": "preflight instrumentation verification",
          "dimension": "P",
          "name": null,
          "policy": {
            "definition": "required launch surfaces have verified measurement, using N/A for genuinely non-participating surfaces",
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "RAMP-P1",
          "veto": true
        },
        "P10": {
          "criterion": "T+1→T+30 momentum plan and next decision",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P10",
          "veto": false
        },
        "P2": {
          "criterion": "actuals vs preregistered targets",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P2",
          "veto": false
        },
        "P3": {
          "criterion": "attribution reconciliation",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P3",
          "veto": false
        },
        "P4": {
          "criterion": "spike-to-sustain retention",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P4",
          "veto": false
        },
        "P5": {
          "criterion": "owned-capture rate",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P5",
          "veto": false
        },
        "P6": {
          "criterion": "feedback loop closure",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P6",
          "veto": false
        },
        "P7": {
          "criterion": "compliant social-proof pipeline",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P7",
          "veto": false
        },
        "P8": {
          "criterion": "causal retro/uncertainty",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P8",
          "veto": false
        },
        "P9": {
          "criterion": "registry learning/outcome writeback",
          "dimension": "P",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-P9",
          "veto": false
        },
        "R1": {
          "criterion": "stage truth against declared access/eligibility",
          "dimension": "R",
          "name": null,
          "policy": {
            "definition": "declared lifecycle stage contradicts verifiable access/eligibility; a public pricing page is not universally required",
            "veto": true
          },
          "qualified_id": "RAMP-R1",
          "veto": true
        },
        "R10": {
          "criterion": "preregistered D0/W1/M1 targets",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R10",
          "veto": false
        },
        "R2": {
          "criterion": "positioning and alternatives",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R2",
          "veto": false
        },
        "R3": {
          "criterion": "ICP/beachhead fit",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R3",
          "veto": false
        },
        "R4": {
          "criterion": "tier/type and effort",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R4",
          "veto": false
        },
        "R5": {
          "criterion": "timing/window",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R5",
          "veto": false
        },
        "R6": {
          "criterion": "competitor launch evidence",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R6",
          "veto": false
        },
        "R7": {
          "criterion": "early-access graduation where applicable",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R7",
          "veto": false
        },
        "R8": {
          "criterion": "risk/rollback register",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R8",
          "veto": false
        },
        "R9": {
          "criterion": "internal ownership/escalation",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "RAMP-R9",
          "veto": false
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
