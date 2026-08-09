<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 19.2.0
- **Framework:** SEND
- **Auditor:** email-quality-auditor
- **Complete item definitions:** 20
- **Source digest:** `sha256:79d30129a29031d15abb3a7f1cd43e7db1c62abce8e16813fe73ccbf392f5f87`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains every item identity and human benchmark anchor plus the exact typed profile, applicability, veto, missingness, and observation vocabulary needed to collect observations without inventing rules. Repository/plugin installs use the root runbook, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "19.2.0",
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
      "items": {
        "D1": {
          "criterion": "Claims, disclosures, and offer terms match the claims ledger.",
          "dimension": "D",
          "name": null,
          "policy": {
            "veto": true
          },
          "qualified_id": "SEND-D1",
          "veto": true
        },
        "D2": {
          "criterion": "The declared outcome truth set is measured.",
          "dimension": "D",
          "name": null,
          "policy": {
            "benchmark": "truth set follows the program: ecommerce, CRM pipeline, subscription, sponsorship, or declared equivalent"
          },
          "qualified_id": "SEND-D2",
          "veto": false
        },
        "D3": {
          "criterion": "Offer and CTA are clear for this program.",
          "dimension": "D",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-D3",
          "veto": false
        },
        "D4": {
          "criterion": "Email-to-destination message match holds.",
          "dimension": "D",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-D4",
          "veto": false
        },
        "D5": {
          "criterion": "Outcome attribution is reconciled outside provider self-reporting.",
          "dimension": "D",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-D5",
          "veto": false
        },
        "E1": {
          "criterion": "Click or downstream action rate is the primary engagement signal.",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-E1",
          "veto": false
        },
        "E2": {
          "criterion": "Open/CTOR is used only with MPP segmentation and an explicit proxy caveat.",
          "dimension": "E",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "opens or CTOR are used in the assessment"
          },
          "qualified_id": "SEND-E2",
          "veto": false
        },
        "E3": {
          "criterion": "Subject, preheader, and body promise match.",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-E3",
          "veto": false
        },
        "E4": {
          "criterion": "Timing and frequency fit preferences and operating capacity.",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-E4",
          "veto": false
        },
        "E5": {
          "criterion": "Engagement decay and reactivation/sunset behavior are measured.",
          "dimension": "E",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-E5",
          "veto": false
        },
        "N1": {
          "criterion": "One-click opt-out works and live suppression tombstones are honored.",
          "dimension": "N",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "SEND-N1",
          "veto": true
        },
        "N2": {
          "criterion": "Entry, confirmation, and welcome/first-touch logic fit the program.",
          "dimension": "N",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-N2",
          "veto": false
        },
        "N3": {
          "criterion": "Journeys applicable to the declared program type exist and work.",
          "dimension": "N",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "only journeys applicable to the declared program type are scored"
          },
          "qualified_id": "SEND-N3",
          "veto": false
        },
        "N4": {
          "criterion": "Segmentation and progression logic use relevant evidence.",
          "dimension": "N",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-N4",
          "veto": false
        },
        "N5": {
          "criterion": "Preference/frequency controls exist where recurring sends make them applicable.",
          "dimension": "N",
          "name": null,
          "policy": {
            "applicability": "conditional",
            "condition": "the program offers recurring sends or configurable frequency"
          },
          "qualified_id": "SEND-N5",
          "veto": false
        },
        "S1": {
          "criterion": "SPF/DKIM/DMARC alignment is verified from DNS and aggregate evidence.",
          "dimension": "S",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "SEND-S1",
          "veto": true
        },
        "S2": {
          "criterion": "Consent/lawful basis and acquisition provenance are on file.",
          "dimension": "S",
          "name": null,
          "policy": {
            "unknown_policy": "needs-input",
            "veto": true
          },
          "qualified_id": "SEND-S2",
          "veto": true
        },
        "S3": {
          "criterion": "Inbox placement is measured on a declared provider or seed panel.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-S3",
          "veto": false
        },
        "S4": {
          "criterion": "Hard-bounce and complaint rates are normalized by cohort/window.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-S4",
          "veto": false
        },
        "S5": {
          "criterion": "Suppression, hygiene, and sunset controls are active.",
          "dimension": "S",
          "name": null,
          "policy": {},
          "qualified_id": "SEND-S5",
          "veto": false
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
