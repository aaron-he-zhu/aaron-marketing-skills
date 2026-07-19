<!-- GENERATED FILE: run `python3 scripts/generate-auditor-runtime.py --write`; do not edit. -->

# Standalone Auditor Runtime

- **Runtime version:** 3.0.0
- **Catalog version:** 18.0.0
- **Framework:** CORE-EEAT
- **Auditor:** content-quality-auditor
- **Source digest:** `sha256:56d2b5fb41d53916d6f21dc71835b70a5269e4a2098afb43daa291b30a2f8e82`

This immutable bundle is the fail-closed standalone fallback for this auditor. It contains the exact typed framework slice needed to collect observations without inventing rules. Repository/plugin installs use the root policy, schemas, and deterministic scorer. A standalone one-folder install must not fetch mutable sources, compute a score, claim a gate verdict, or persist an audit artifact.

## Typed Framework Snapshot

```json
{
  "catalog_version": "18.0.0",
  "frameworks": {
    "CORE-EEAT": {
      "construct": "content-quality controls for one declared content artifact",
      "dimensions": {
        "A": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "A",
          "name": "Authority"
        },
        "C": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "C",
          "name": "Content"
        },
        "E": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "E",
          "name": "Exclusivity"
        },
        "Ept": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "Ept",
          "name": "Expertise"
        },
        "Exp": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "Exp",
          "name": "Experience"
        },
        "O": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "O",
          "name": "Organization"
        },
        "R": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "R",
          "name": "Research"
        },
        "T": {
          "id_width": 2,
          "item_count": 10,
          "item_prefix": "T",
          "name": "Trust"
        }
      },
      "item_policies": {
        "A07": {
          "applicability": "conditional",
          "condition": "knowledge-graph presence is material to the audit objective"
        },
        "E01": {
          "applicability": "conditional",
          "condition": "original data is part of the content promise"
        },
        "E02": {
          "applicability": "conditional",
          "condition": "the content claims a novel framework"
        },
        "E03": {
          "applicability": "conditional",
          "condition": "primary research is part of the content promise"
        },
        "E04": {
          "applicability": "conditional",
          "condition": "the content takes a contrarian position"
        },
        "E05": {
          "applicability": "conditional",
          "condition": "original visuals are needed to support the artifact"
        },
        "E10": {
          "applicability": "conditional",
          "condition": "the content makes forward-looking claims"
        },
        "Exp01": {
          "applicability": "conditional",
          "condition": "first-person experience is claimed or required by the profile"
        },
        "Exp02": {
          "applicability": "conditional",
          "condition": "sensory observation is material to the subject"
        },
        "Exp04": {
          "applicability": "conditional",
          "condition": "the artifact claims hands-on use"
        },
        "Exp05": {
          "applicability": "conditional",
          "condition": "usage duration is material"
        },
        "Exp07": {
          "applicability": "conditional",
          "condition": "a before/after claim is made"
        },
        "Exp09": {
          "applicability": "conditional",
          "condition": "repeat testing is claimed"
        },
        "O03": {
          "applicability": "conditional",
          "condition": "the artifact contains comparable structured data"
        },
        "O05": {
          "applicability": "conditional",
          "condition": "the artifact is an indexable web page eligible for structured data"
        },
        "O10": {
          "applicability": "conditional",
          "condition": "multimedia is part of the declared artifact"
        },
        "T04": {
          "applicability": "conditional",
          "condition": "a material connection, paid placement, or affiliate relationship exists",
          "veto": true
        },
        "T08": {
          "applicability": "conditional",
          "condition": "the artifact makes YMYL or other material-risk claims"
        }
      },
      "profiles": {
        "alternative": {
          "context_equals": {
            "content_type": "alternative"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.05,
            "Ept": 0.05,
            "Exp": 0.15,
            "O": 0.15,
            "R": 0.25,
            "T": 0.2
          }
        },
        "best-of": {
          "context_equals": {
            "content_type": "best-of"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.15,
            "Ept": 0.1,
            "Exp": 0.05,
            "O": 0.25,
            "R": 0.2,
            "T": 0.1
          }
        },
        "blog-post": {
          "context_equals": {
            "content_type": "blog-post"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.25,
            "E": 0.2,
            "Ept": 0.1,
            "Exp": 0.1,
            "O": 0.1,
            "R": 0.1,
            "T": 0.1
          }
        },
        "comparison": {
          "context_equals": {
            "content_type": "comparison"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.1,
            "Ept": 0.15,
            "Exp": 0.05,
            "O": 0.2,
            "R": 0.25,
            "T": 0.1
          }
        },
        "faq-page": {
          "context_equals": {
            "content_type": "faq-page"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.25,
            "E": 0.05,
            "Ept": 0.1,
            "Exp": 0.05,
            "O": 0.25,
            "R": 0.15,
            "T": 0.1
          }
        },
        "how-to-guide": {
          "context_equals": {
            "content_type": "how-to-guide"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.2,
            "E": 0.05,
            "Ept": 0.2,
            "Exp": 0.05,
            "O": 0.2,
            "R": 0.1,
            "T": 0.15
          }
        },
        "landing-page": {
          "context_equals": {
            "content_type": "landing-page"
          },
          "dimensions": {
            "A": 0.25,
            "C": 0.2,
            "E": 0.05,
            "Ept": 0.05,
            "Exp": 0.05,
            "O": 0.1,
            "R": 0.05,
            "T": 0.25
          }
        },
        "product-review": {
          "context_equals": {
            "content_type": "product-review"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.2,
            "Ept": 0.05,
            "Exp": 0.2,
            "O": 0.1,
            "R": 0.15,
            "T": 0.15
          }
        },
        "testimonial": {
          "context_equals": {
            "content_type": "testimonial"
          },
          "dimensions": {
            "A": 0.05,
            "C": 0.1,
            "E": 0.1,
            "Ept": 0.05,
            "Exp": 0.3,
            "O": 0.05,
            "R": 0.15,
            "T": 0.2
          }
        }
      },
      "required_context": [
        "content_type",
        "market",
        "publication_state"
      ],
      "source": "references/core-eeat-benchmark.md",
      "unit_of_analysis": "one content artifact at one observation date",
      "veto_items": [
        "T04",
        "C01",
        "R10"
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
