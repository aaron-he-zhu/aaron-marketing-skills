<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** TALE
- **Auditor:** narrative-quality-auditor
- **Complete item definitions:** 40
- **Source digest:** `sha256:1c161b3423d6a7eba8bc157422d3b974590b6c93181a394f031ea96a976de37c`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
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
      "items": {
        "A1": {
          "criterion": "canon existence and internal consistency",
          "dimension": "A",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "TALE-A1",
          "veto": true
        },
        "A10": {
          "criterion": "append-only version/supersession history",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A10",
          "veto": false
        },
        "A2": {
          "criterion": "chosen message hierarchy/pillars where applicable",
          "dimension": "A",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "a message-house pattern is chosen; pillar count is user-justified rather than universally fixed"
          },
          "qualified_id": "TALE-A2",
          "veto": false
        },
        "A3": {
          "criterion": "traceability from messages to positioning/proof",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A3",
          "veto": false
        },
        "A4": {
          "criterion": "strategic change arc where appropriate",
          "dimension": "A",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "a change-narrative arc is appropriate to the strategy"
          },
          "qualified_id": "TALE-A4",
          "veto": false
        },
        "A5": {
          "criterion": "persona proof provenance",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A5",
          "veto": false
        },
        "A6": {
          "criterion": "voice rules",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A6",
          "veto": false
        },
        "A7": {
          "criterion": "naming/lexicon governance",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A7",
          "veto": false
        },
        "A8": {
          "criterion": "fixed-length boilerplates only when operationally required",
          "dimension": "A",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "fixed-length boilerplates are operationally required"
          },
          "qualified_id": "TALE-A8",
          "veto": false
        },
        "A9": {
          "criterion": "concreteness/empty-chair quality",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-A9",
          "veto": false
        },
        "E1": {
          "criterion": "no unsupported effectiveness/resonance assertion or mislabeled proxy",
          "dimension": "E",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "TALE-E1",
          "veto": true
        },
        "E10": {
          "criterion": "revision after failed test",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E10",
          "veto": false
        },
        "E2": {
          "criterion": "differentiating-claim substantiation",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E2",
          "veto": false
        },
        "E3": {
          "criterion": "preregistered comprehension/behavior test",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E3",
          "veto": false
        },
        "E4": {
          "criterion": "defined echo/recall method",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E4",
          "veto": false
        },
        "E5": {
          "criterion": "locked comparison panel",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E5",
          "veto": false
        },
        "E6": {
          "criterion": "answer-engine perception as proxy where used",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E6",
          "veto": false
        },
        "E7": {
          "criterion": "proof assets",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E7",
          "veto": false
        },
        "E8": {
          "criterion": "actual-vs-intended retro",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E8",
          "veto": false
        },
        "E9": {
          "criterion": "win-loss/objection writeback",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-E9",
          "veto": false
        },
        "L1": {
          "criterion": "no material flagship-surface contradiction",
          "dimension": "L",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "TALE-L1",
          "veto": true
        },
        "L10": {
          "criterion": "pre-ship drift check",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L10",
          "veto": false
        },
        "L2": {
          "criterion": "campaign/landing/offer match",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L2",
          "veto": false
        },
        "L3": {
          "criterion": "channel derivation from canon",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L3",
          "veto": false
        },
        "L4": {
          "criterion": "cascade ownership",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L4",
          "veto": false
        },
        "L5": {
          "criterion": "governed localization",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L5",
          "veto": false
        },
        "L6": {
          "criterion": "channel-voice inheritance",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L6",
          "veto": false
        },
        "L7": {
          "criterion": "objection consistency",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L7",
          "veto": false
        },
        "L8": {
          "criterion": "proof at claim location",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L8",
          "veto": false
        },
        "L9": {
          "criterion": "enablement consistency",
          "dimension": "L",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-L9",
          "veto": false
        },
        "T1": {
          "criterion": "material differentiation integrity",
          "dimension": "T",
          "name": null,
          "policy": {
            "definition": "material differentiation is false, contradictory, or unsubstantiated; a literal onlyness claim is not required",
            "veto": true
          },
          "qualified_id": "TALE-T1",
          "veto": true
        },
        "T10": {
          "criterion": "current canon version",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T10",
          "veto": false
        },
        "T2": {
          "criterion": "positioning alternatives/value evidence",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T2",
          "veto": false
        },
        "T3": {
          "criterion": "category-frame defensibility where used",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T3",
          "veto": false
        },
        "T4": {
          "criterion": "beachhead/audience truth",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T4",
          "veto": false
        },
        "T5": {
          "criterion": "claim provenance/needs-source handling",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T5",
          "veto": false
        },
        "T6": {
          "criterion": "superlative basis",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T6",
          "veto": false
        },
        "T7": {
          "criterion": "product-stage reality",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T7",
          "veto": false
        },
        "T8": {
          "criterion": "aspiration/fact separation",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T8",
          "veto": false
        },
        "T9": {
          "criterion": "interview/win-loss grounding",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "TALE-T9",
          "veto": false
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
