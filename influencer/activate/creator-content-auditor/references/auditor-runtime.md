<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.0.0
- **Framework:** STAR
- **Auditor:** creator-content-auditor
- **Source digest:** `sha256:cac545f4f4563724c6645a1f0aa807811d870e59444412f251a4fdf46d059789`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.0.0",
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
