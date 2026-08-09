<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** STAR
- **Auditor:** creator-content-auditor
- **Complete item definitions:** 40
- **Source digest:** `sha256:8b5918c92e73bc471e44c2d29d69310e912dae0f15a00688dbe00f1fb0e752a6`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
  "frameworks": {
    "STAR": {
      "construct": "influencer partnership quality across creator suitability, trust and compliance, content appeal, and campaign return",
      "context_allowed": {
        "assessment_time": [
          "forecast",
          "actual"
        ]
      },
      "dimensions": {
        "A": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "A",
          "name": "Appeal"
        },
        "R": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "R",
          "name": "Return"
        },
        "S": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "S",
          "name": "Suitability"
        },
        "T": {
          "id_width": 1,
          "item_count": 10,
          "item_prefix": "T",
          "name": "Trust"
        }
      },
      "item_definitions": {
        "A1": "the hook earns attention within the platform's first-impression window",
        "A10": "originality — the piece is not a templated re-run of prior sponsorships",
        "A2": "creative quality (production, editing, pacing) meets the platform bar",
        "A3": "the brand integration feels native to the creator, not bolted-on",
        "A4": "storytelling and format choice fit the platform's native behavior",
        "A5": "message accuracy — the brief's key message is conveyed without distortion",
        "A6": "audience relevance — the content speaks to the target's beliefs and needs",
        "A7": "the call-to-action is present, clear, and matched to the declared goal",
        "A8": "on-brand tone, terminology, and visual identity are respected",
        "A9": "accessibility (captions, alt text, legibility) is handled",
        "R1": "measured ROI/ROAS is read against the declared target",
        "R10": "the measurement plan (UTMs, codes, controls) is defined before launch",
        "R2": "CPE/CPM/CPA are benchmarked on a normalized window",
        "R3": "value-for-spend beats the declared alternative-channel baseline",
        "R4": "KPI attainment versus the pre-registered target is reported",
        "R5": "conversions and outcomes are attributed with a stated method and rigor",
        "R6": "incremental impact is separated from baseline where measurable",
        "R7": "creator-mix and channel choices fit the goal (orchestration, knowable at plan time)",
        "R8": "budget split and timing across creators and phases are justified",
        "R9": "the deliverable schedule and cadence match the campaign window",
        "S1": "audience composition, geography, and language match the target within a stated window",
        "S10": "commercial saturation and disclosed category history are transparent and acceptable",
        "S2": "real-follower rate is at/above the tier x platform x niche benchmark",
        "S3": "follower growth is organic and stable, with no purchase or spike anomalies",
        "S4": "typical reach reliability across recent posts is benchmarked, not cherry-picked",
        "S5": "engagement rate meets the niche median for the creator's tier and platform",
        "S6": "engagement is authentic, not pod-coordinated or bought",
        "S7": "repeat audience action (saves/shares/returns) shows durable influence, not campaign conversion",
        "S8": "brand/category fit and audience-brand overlap are evidenced, independent of any single deal",
        "S9": "creator reliability, professionalism, and delivery history support the partnership",
        "T1": "required FTC/ASA disclosure is present, clear, and conspicuous on sponsored content",
        "T10": "rights, usage, whitelisting, and exclusivity terms are represented truthfully",
        "T2": "every material claim in the deliverable is truthful and substantiated",
        "T3": "no disqualifying brand-safety evidence exists under the declared policy and window",
        "T4": "disclosure meets platform-specific tool and caption placement requirements",
        "T5": "prohibited or restricted-category rules for the product are satisfied",
        "T6": "prior disclosure and compliance history shows no unresolved violations",
        "T7": "the material connection (gifting/affiliate/paid) is accurately represented to the audience",
        "T8": "comparative or performance claims carry evidence at the point of claim",
        "T9": "sensitive-audience, health, financial, and age-gating requirements are met where applicable"
      },
      "item_policies": {
        "R1": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "R2": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "R3": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "R4": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "R5": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "fail_flag": "results-unverified",
          "unknown_policy": "needs-input"
        },
        "R6": {
          "applicability": "conditional",
          "applicable_when": {
            "assessment_time": "actual"
          },
          "unknown_policy": "needs-input"
        },
        "S2": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "S6": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "S7": {
          "definition": "durable repeat-audience influence; campaign conversion is scored in R"
        },
        "S8": {
          "definition": "brand-independent fit; a specific brand conflict is scored in R7 orchestration"
        },
        "T1": {
          "veto": true
        },
        "T2": {
          "veto": true
        },
        "T3": {
          "unknown_policy": "needs-input",
          "veto": true
        }
      },
      "items": {
        "A1": {
          "criterion": "The hook earns attention within the platform's first-impression window.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A1",
          "veto": false
        },
        "A10": {
          "criterion": "Originality — the piece is not a templated re-run of prior sponsorships.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A10",
          "veto": false
        },
        "A2": {
          "criterion": "Creative quality (production, editing, pacing) meets the platform bar.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A2",
          "veto": false
        },
        "A3": {
          "criterion": "The brand integration feels native to the creator, not bolted-on.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A3",
          "veto": false
        },
        "A4": {
          "criterion": "Storytelling and format choice fit the platform's native behavior.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A4",
          "veto": false
        },
        "A5": {
          "criterion": "Message accuracy — the brief's key message is conveyed without distortion.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A5",
          "veto": false
        },
        "A6": {
          "criterion": "Audience relevance — the content speaks to the target's beliefs and needs.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A6",
          "veto": false
        },
        "A7": {
          "criterion": "The call-to-action is present, clear, and matched to the declared goal.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A7",
          "veto": false
        },
        "A8": {
          "criterion": "On-brand tone, terminology, and visual identity are respected.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A8",
          "veto": false
        },
        "A9": {
          "criterion": "Accessibility (captions, alt text, legibility) is handled.",
          "dimension": "A",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-A9",
          "veto": false
        },
        "R1": {
          "criterion": "Measured ROI/ROAS is read against the declared target.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R1",
          "veto": false
        },
        "R10": {
          "criterion": "The measurement plan (UTMs, codes, controls) is defined before launch.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-R10",
          "veto": false
        },
        "R2": {
          "criterion": "CPE/CPM/CPA are benchmarked on a normalized window.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R2",
          "veto": false
        },
        "R3": {
          "criterion": "Value-for-spend beats the declared alternative-channel baseline.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R3",
          "veto": false
        },
        "R4": {
          "criterion": "KPI attainment versus the pre-registered target is reported.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R4",
          "veto": false
        },
        "R5": {
          "criterion": "Conversions and outcomes are attributed with a stated method and rigor.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "fail_flag": "results-unverified",
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R5",
          "veto": false
        },
        "R6": {
          "criterion": "Incremental impact is separated from baseline where measurable.",
          "dimension": "R",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "applicable_when": {
              "assessment_time": "actual"
            },
            "unknown_policy": "needs-input"
          },
          "qualified_id": "STAR-R6",
          "veto": false
        },
        "R7": {
          "criterion": "Creator-mix and channel choices fit the goal (orchestration, knowable at plan time).",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-R7",
          "veto": false
        },
        "R8": {
          "criterion": "Budget split and timing across creators and phases are justified.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-R8",
          "veto": false
        },
        "R9": {
          "criterion": "The deliverable schedule and cadence match the campaign window.",
          "dimension": "R",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-R9",
          "veto": false
        },
        "S1": {
          "criterion": "Audience composition, geography, and language match the target within a stated window.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S1",
          "veto": false
        },
        "S10": {
          "criterion": "Commercial saturation and disclosed category history are transparent and acceptable.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S10",
          "veto": false
        },
        "S2": {
          "criterion": "Real-follower rate is at/above the tier x platform x niche benchmark.",
          "dimension": "S",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "STAR-S2",
          "veto": true
        },
        "S3": {
          "criterion": "Follower growth is organic and stable, with no purchase or spike anomalies.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S3",
          "veto": false
        },
        "S4": {
          "criterion": "Typical reach reliability across recent posts is benchmarked, not cherry-picked.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S4",
          "veto": false
        },
        "S5": {
          "criterion": "Engagement rate meets the niche median for the creator's tier and platform.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S5",
          "veto": false
        },
        "S6": {
          "criterion": "Engagement is authentic, not pod-coordinated or bought.",
          "dimension": "S",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "STAR-S6",
          "veto": true
        },
        "S7": {
          "criterion": "Repeat audience action (saves/shares/returns) shows durable influence, not campaign conversion.",
          "dimension": "S",
          "name": null,
          "policy": {
            "definition": "durable repeat-audience influence; campaign conversion is scored in R"
          },
          "qualified_id": "STAR-S7",
          "veto": false
        },
        "S8": {
          "criterion": "Brand/category fit and audience-brand overlap are evidenced, independent of any single deal.",
          "dimension": "S",
          "name": null,
          "policy": {
            "definition": "brand-independent fit; a specific brand conflict is scored in R7 orchestration"
          },
          "qualified_id": "STAR-S8",
          "veto": false
        },
        "S9": {
          "criterion": "Creator reliability, professionalism, and delivery history support the partnership.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-S9",
          "veto": false
        },
        "T1": {
          "criterion": "Required FTC/ASA disclosure is present, clear, and conspicuous on sponsored content.",
          "dimension": "T",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "STAR-T1",
          "veto": true
        },
        "T10": {
          "criterion": "Rights, usage, whitelisting, and exclusivity terms are represented truthfully.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T10",
          "veto": false
        },
        "T2": {
          "criterion": "Every material claim in the deliverable is truthful and substantiated.",
          "dimension": "T",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "STAR-T2",
          "veto": true
        },
        "T3": {
          "criterion": "No disqualifying brand-safety evidence exists under the declared policy and window.",
          "dimension": "T",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "STAR-T3",
          "veto": true
        },
        "T4": {
          "criterion": "Disclosure meets platform-specific tool and caption placement requirements.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T4",
          "veto": false
        },
        "T5": {
          "criterion": "Prohibited or restricted-category rules for the product are satisfied.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T5",
          "veto": false
        },
        "T6": {
          "criterion": "Prior disclosure and compliance history shows no unresolved violations.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T6",
          "veto": false
        },
        "T7": {
          "criterion": "The material connection (gifting/affiliate/paid) is accurately represented to the audience.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T7",
          "veto": false
        },
        "T8": {
          "criterion": "Comparative or performance claims carry evidence at the point of claim.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T8",
          "veto": false
        },
        "T9": {
          "criterion": "Sensitive-audience, health, financial, and age-gating requirements are met where applicable.",
          "dimension": "T",
          "name": null,
          "policy": {},
          "qualified_id": "STAR-T9",
          "veto": false
        }
      },
      "profiles": {
        "awareness": {
          "context_equals": {
            "goal": "awareness"
          },
          "dimensions": {
            "A": 0.35,
            "R": 0.15,
            "S": 0.3,
            "T": 0.2
          }
        },
        "brand-building": {
          "context_equals": {
            "goal": "brand-building"
          },
          "dimensions": {
            "A": 0.2,
            "R": 0.15,
            "S": 0.3,
            "T": 0.35
          }
        },
        "conversion": {
          "context_equals": {
            "goal": "conversion"
          },
          "dimensions": {
            "A": 0.2,
            "R": 0.35,
            "S": 0.25,
            "T": 0.2
          }
        },
        "engagement": {
          "context_equals": {
            "goal": "engagement"
          },
          "dimensions": {
            "A": 0.4,
            "R": 0.15,
            "S": 0.25,
            "T": 0.2
          }
        }
      },
      "required_context": [
        "goal",
        "assessment_time",
        "platform",
        "market"
      ],
      "source": "references/star-benchmark.md",
      "unit_of_analysis": "one creator partnership — creator, deliverable, and attributed outcome — at one observation time; forecast and actual reads are never merged",
      "veto_items": [
        "S2",
        "S6",
        "T1",
        "T2",
        "T3"
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
