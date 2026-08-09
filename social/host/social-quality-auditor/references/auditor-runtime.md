<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** ECHO
- **Auditor:** social-quality-auditor
- **Complete item definitions:** 40
- **Source digest:** `sha256:8aba0e4f0e74fc02dd33bacefd3db89c7e2b9dd4e22188d72898bfda2feaece6`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
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
      "items": {
        "C1": {
          "criterion": "claim integrity where claims exist",
          "dimension": "C",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "the asset makes a product or offer claim",
            "veto": true
          },
          "qualified_id": "ECHO-C1",
          "veto": true
        },
        "C10": {
          "criterion": "format-specific execution evidence",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C10",
          "veto": false
        },
        "C2": {
          "criterion": "material-connection/synthetic-media disclosure where applicable",
          "dimension": "C",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "a material connection or realistic synthetic media exists",
            "veto": true
          },
          "qualified_id": "ECHO-C2",
          "veto": true
        },
        "C3": {
          "criterion": "platform-native adaptation",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C3",
          "veto": false
        },
        "C4": {
          "criterion": "hook/payload/spec fit",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C4",
          "veto": false
        },
        "C5": {
          "criterion": "accessibility",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C5",
          "veto": false
        },
        "C6": {
          "criterion": "voice/canon adherence",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C6",
          "veto": false
        },
        "C7": {
          "criterion": "declared editorial mix",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C7",
          "veto": false
        },
        "C8": {
          "criterion": "freshness on reused assets",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C8",
          "veto": false
        },
        "C9": {
          "criterion": "link/placement policy",
          "dimension": "C",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-C9",
          "veto": false
        },
        "E1": {
          "criterion": "channel truth/registry state",
          "dimension": "E",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "ECHO-E1",
          "veto": true
        },
        "E10": {
          "criterion": "cross-community rule-conflict check",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E10",
          "veto": false
        },
        "E2": {
          "criterion": "participation before promotion",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E2",
          "veto": false
        },
        "E3": {
          "criterion": "give/ask evidence",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E3",
          "veto": false
        },
        "E4": {
          "criterion": "current rule digest",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E4",
          "veto": false
        },
        "E5": {
          "criterion": "governed profile/bio/link state",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E5",
          "veto": false
        },
        "E6": {
          "criterion": "owned-space lifecycle where applicable",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E6",
          "veto": false
        },
        "E7": {
          "criterion": "channel-capability fit",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E7",
          "veto": false
        },
        "E8": {
          "criterion": "handle security/governance",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E8",
          "veto": false
        },
        "E9": {
          "criterion": "pinned/bio-link freshness",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-E9",
          "veto": false
        },
        "H1": {
          "criterion": "no manufactured/baited engagement",
          "dimension": "H",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "ECHO-H1",
          "veto": true
        },
        "H10": {
          "criterion": "advocate-roster hygiene",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H10",
          "veto": false
        },
        "H2": {
          "criterion": "UGC permission where republishing occurs",
          "dimension": "H",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "third-party UGC is republished outside a native share",
            "veto": true
          },
          "qualified_id": "ECHO-H2",
          "veto": true
        },
        "H3": {
          "criterion": "response SLA",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H3",
          "veto": false
        },
        "H4": {
          "criterion": "crisis/pause protocol",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H4",
          "veto": false
        },
        "H5": {
          "criterion": "cadence/capacity fit",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H5",
          "veto": false
        },
        "H6": {
          "criterion": "voluntary advocacy",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H6",
          "veto": false
        },
        "H7": {
          "criterion": "warm-touch selling discipline",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H7",
          "veto": false
        },
        "H8": {
          "criterion": "escalation ownership",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H8",
          "veto": false
        },
        "H9": {
          "criterion": "moderation rules/log",
          "dimension": "H",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-H9",
          "veto": false
        },
        "O1": {
          "criterion": "stable named denominators and provenance",
          "dimension": "O",
          "name": null,
          "policy": {
            "asset_gate_note": "an observed asset with no performance rate or metric claim may pass this control; do not infer from missing asset access",
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "ECHO-O1",
          "veto": true
        },
        "O10": {
          "criterion": "learning writeback",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O10",
          "veto": false
        },
        "O2": {
          "criterion": "declared dark-social method",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O2",
          "veto": false
        },
        "O3": {
          "criterion": "locked comparison panel",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O3",
          "veto": false
        },
        "O4": {
          "criterion": "robust per-post rollups and organic/paid separation",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O4",
          "veto": false
        },
        "O5": {
          "criterion": "vanity/EMV exclusion from decision scores",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O5",
          "veto": false
        },
        "O6": {
          "criterion": "attribution instrumentation",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O6",
          "veto": false
        },
        "O7": {
          "criterion": "listening baseline",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O7",
          "veto": false
        },
        "O8": {
          "criterion": "query architecture",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O8",
          "veto": false
        },
        "O9": {
          "criterion": "employee-excluded community health",
          "dimension": "O",
          "name": null,
          "policy": {},
          "qualified_id": "ECHO-O9",
          "veto": false
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
