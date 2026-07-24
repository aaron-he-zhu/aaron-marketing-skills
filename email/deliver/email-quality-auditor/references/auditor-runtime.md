<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** SEND
- **Auditor:** email-quality-auditor
- **Source digest:** `sha256:dde82492243e8a0d46bb85bd24c9c24b89f5b8411dfc6e8671591261be28571e`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
  "frameworks": {
    "SEND": {
      "construct": "email program integrity, engagement, lifecycle fit, and declared business outcome",
      "dimensions": {
        "D": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "D",
          "name": "Direct Outcome"
        },
        "E": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "E",
          "name": "Engagement"
        },
        "N": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "N",
          "name": "Nurture"
        },
        "S": {
          "id_width": 1,
          "item_count": 5,
          "item_prefix": "S",
          "name": "Sender Integrity"
        }
      },
      "item_definitions": {
        "D1": "claims, disclosures, and offer terms match the claims ledger",
        "D2": "the declared outcome truth set is measured: revenue, pipeline, subscription, sponsorship, or another named outcome",
        "D3": "offer and CTA are clear for the declared program",
        "D4": "email-to-destination message match holds",
        "D5": "outcome attribution is reconciled outside provider self-reporting",
        "E1": "click or downstream action rate is the primary engagement signal",
        "E2": "open/CTOR is used only with MPP segmentation and an explicit proxy caveat",
        "E3": "subject, preheader, and body promise match",
        "E4": "send timing and frequency fit preference and capacity",
        "E5": "engagement decay and reactivation/sunset logic are measured",
        "N1": "one-click opt-out works and live suppression tombstones are honored",
        "N2": "entry, confirmation, and welcome/first-touch logic fit the program",
        "N3": "applicable lifecycle journeys exist for the declared program type",
        "N4": "segmentation and progression logic use relevant evidence",
        "N5": "preference and frequency controls are available where applicable",
        "S1": "SPF/DKIM/DMARC alignment verified from DNS and aggregate evidence",
        "S2": "consent/lawful basis and acquisition provenance are on file",
        "S3": "inbox placement is measured on a declared provider/seed panel",
        "S4": "hard-bounce and complaint rates are normalized by cohort/window",
        "S5": "suppression, hygiene, and sunset controls are active"
      },
      "item_policies": {
        "D1": {
          "veto": true
        },
        "D2": {
          "benchmark": "truth set follows the program: ecommerce, CRM pipeline, subscription, sponsorship, or declared equivalent"
        },
        "E2": {
          "applicability": "conditional",
          "condition": "opens or CTOR are used in the assessment"
        },
        "N1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "N3": {
          "applicability": "conditional",
          "condition": "only journeys applicable to the declared program type are scored"
        },
        "N5": {
          "applicability": "conditional",
          "condition": "the program offers recurring sends or configurable frequency"
        },
        "S1": {
          "unknown_policy": "needs-input",
          "veto": true
        },
        "S2": {
          "unknown_policy": "needs-input",
          "veto": true
        }
      },
      "profiles": {
        "cold-outbound": {
          "context_equals": {
            "program_type": "cold-outbound"
          },
          "dimensions": {
            "D": 0.25,
            "E": 0.25,
            "N": 0.15,
            "S": 0.35
          }
        },
        "newsletter": {
          "context_equals": {
            "program_type": "newsletter"
          },
          "dimensions": {
            "D": 0.2,
            "E": 0.35,
            "N": 0.2,
            "S": 0.25
          }
        },
        "promotional": {
          "context_equals": {
            "program_type": "promotional"
          },
          "dimensions": {
            "D": 0.35,
            "E": 0.2,
            "N": 0.15,
            "S": 0.3
          }
        },
        "retention": {
          "context_equals": {
            "program_type": "retention"
          },
          "dimensions": {
            "D": 0.15,
            "E": 0.35,
            "N": 0.3,
            "S": 0.2
          }
        }
      },
      "required_context": [
        "program_type",
        "provider",
        "window",
        "list_age",
        "market",
        "mpp_share"
      ],
      "source": "references/send-benchmark.md",
      "unit_of_analysis": "one sending program/profile and normalized observation window",
      "veto_items": [
        "S1",
        "S2",
        "N1",
        "D1"
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
