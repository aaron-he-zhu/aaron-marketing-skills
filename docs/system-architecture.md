<!-- GENERATED FILE: run `python3 scripts/generate-system-docs.py --write`; do not edit. -->

# System Architecture

This is the generated human view of [`references/system-catalog.json`](../references/system-catalog.json). The JSON catalog is authoritative.

- Architecture contract: `18.0.0`
- Bundle version: `18.0.0`
- Catalog digest: `sha256:304866b82d8ff14076ffb6a4638fbcf16f2585461248159ad8ec3c627639834b`
- Shape: **112 discipline skills across 7 disciplines + 8 protocol skills = 120 skills; 8 commands**

## Runtime Capability Profiles

The capability matrix is delegated to [`references/capability-profiles.json`](../references/capability-profiles.json) (`sha256:a1bb5825bc677a4a5a452254f5d0b87a5fc21efb8ddc1dcecf31107f1318bc40`), preserving **Lite ⊂ Pro ⊂ Governed** without duplicating it in the system catalog.

Universal overlays applied to every profile: `consent` · `claims` · `pii-secrets` · `external-mutation` · `audit-verdict` · `release-provenance`.

| Profile | Rank | Capability count | Adds at this tier |
|---|---:|---:|---|
| **Lite** | 0 | 5 | `authored-workflows` · `auto-routing` · `deterministic-scoring` · `inline-delivery` · `canonical-state-read` |
| **Pro** | 1 | 7 | `connectors` · `audit-persistence` |
| **Governed** | 2 | 16 | `working-memory-write` · `registry-write` · `run-evidence` · `context-planning` · `runtime-controller` · `workflow-execution` · `workflow-loop` · `audit-loop` · `owner-capability` |

## Four Layers

| Layer | Purpose | Disciplines | Cadence |
|---|---|---|---|
| **L1 · Strategy** | what we say and who we are | narrative | always-on |
| **L2 · Channels** | always-on engines that express strategy | seo-geo → social → email → ad → influencer | always-on |
| **L3 · Orchestration** | time-boxed moments coordinated across channels | launch | episodic |
| **L4 · Protocol** | truth registries, governance, and working memory | protocol | continuous |

Canonical logical order: **narrative → seo-geo → social → email → ad → influencer → launch → protocol**.

## Discipline Topology

| Discipline | Layer | Framework | Loop | Skills |
|---|---|---|---|---:|
| **Brand Narrative** | L1 | TALE | Trace -> Architect -> Land -> Evaluate | 16 |
| **SEO/GEO** | L2 | CORE-EEAT + CITE | Survey -> Implement -> Tune -> Evaluate | 16 |
| **Organic Social** | L2 | ECHO | Explore -> Craft -> Host -> Observe | 16 |
| **Email Marketing** | L2 | SEND | Setup -> Engage -> Nurture -> Deliver | 16 |
| **Paid Ads** | L2 | ROAS | Research -> Orchestrate -> Activate -> Scale | 16 |
| **Influencer Marketing** | L2 | STAR | Scout -> Target -> Activate -> Report | 16 |
| **Product Launch** | L3 | RAMP | Research -> Assemble -> Mobilize -> Prove | 16 |

### Brand Narrative

- **trace:** [`narrative-baseline-mapper`](../narrative/trace/narrative-baseline-mapper/SKILL.md) · [`category-narrative-mapper`](../narrative/trace/category-narrative-mapper/SKILL.md) · [`audience-belief-mapper`](../narrative/trace/audience-belief-mapper/SKILL.md) · [`positioning-truth-tracer`](../narrative/trace/positioning-truth-tracer/SKILL.md)
- **architect:** [`strategic-narrative-designer`](../narrative/architect/strategic-narrative-designer/SKILL.md) · [`message-system-architect`](../narrative/architect/message-system-architect/SKILL.md) · [`brand-language-codifier`](../narrative/architect/brand-language-codifier/SKILL.md) · [`story-bank-builder`](../narrative/architect/story-bank-builder/SKILL.md)
- **land:** [`narrative-cascade-planner`](../narrative/land/narrative-cascade-planner/SKILL.md) · [`pitch-narrative-builder`](../narrative/land/pitch-narrative-builder/SKILL.md) · [`narrative-enablement-kit`](../narrative/land/narrative-enablement-kit/SKILL.md) · [`proof-point-packager`](../narrative/land/proof-point-packager/SKILL.md)
- **evaluate:** [`narrative-quality-auditor`](../narrative/evaluate/narrative-quality-auditor/SKILL.md) · [`message-test-designer`](../narrative/evaluate/message-test-designer/SKILL.md) · [`narrative-resonance-monitor`](../narrative/evaluate/narrative-resonance-monitor/SKILL.md) · [`narrative-drift-monitor`](../narrative/evaluate/narrative-drift-monitor/SKILL.md)

### SEO/GEO

- **survey:** [`keyword-research`](../seo-geo/survey/keyword-research/SKILL.md) · [`competitor-analysis`](../seo-geo/survey/competitor-analysis/SKILL.md) · [`serp-analysis`](../seo-geo/survey/serp-analysis/SKILL.md) · [`content-gap-analysis`](../seo-geo/survey/content-gap-analysis/SKILL.md)
- **implement:** [`content-writer`](../seo-geo/implement/content-writer/SKILL.md) · [`geo-content-optimizer`](../seo-geo/implement/geo-content-optimizer/SKILL.md) · [`serp-markup-builder`](../seo-geo/implement/serp-markup-builder/SKILL.md) · [`page-play-builder`](../seo-geo/implement/page-play-builder/SKILL.md)
- **tune:** [`content-quality-auditor`](../seo-geo/tune/content-quality-auditor/SKILL.md) · [`technical-seo-checker`](../seo-geo/tune/technical-seo-checker/SKILL.md) · [`on-page-seo-checker`](../seo-geo/tune/on-page-seo-checker/SKILL.md) · [`site-structure-optimizer`](../seo-geo/tune/site-structure-optimizer/SKILL.md)
- **evaluate:** [`domain-authority-auditor`](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) · [`rank-tracker`](../seo-geo/evaluate/rank-tracker/SKILL.md) · [`performance-monitor`](../seo-geo/evaluate/performance-monitor/SKILL.md) · [`offsite-signal-analyzer`](../seo-geo/evaluate/offsite-signal-analyzer/SKILL.md)

### Organic Social

- **explore:** [`channel-portfolio-planner`](../social/explore/channel-portfolio-planner/SKILL.md) · [`voice-dossier-builder`](../social/explore/voice-dossier-builder/SKILL.md) · [`platform-norm-profiler`](../social/explore/platform-norm-profiler/SKILL.md) · [`participation-warmup-planner`](../social/explore/participation-warmup-planner/SKILL.md)
- **craft:** [`social-calendar-builder`](../social/craft/social-calendar-builder/SKILL.md) · [`social-creative-builder`](../social/craft/social-creative-builder/SKILL.md) · [`short-video-scripter`](../social/craft/short-video-scripter/SKILL.md) · [`advocacy-program-designer`](../social/craft/advocacy-program-designer/SKILL.md)
- **host:** [`social-quality-auditor`](../social/host/social-quality-auditor/SKILL.md) · [`engagement-inbox-manager`](../social/host/engagement-inbox-manager/SKILL.md) · [`social-selling-planner`](../social/host/social-selling-planner/SKILL.md) · [`crisis-response-planner`](../social/host/crisis-response-planner/SKILL.md)
- **observe:** [`social-pulse-monitor`](../social/observe/social-pulse-monitor/SKILL.md) · [`share-of-voice-tracker`](../social/observe/share-of-voice-tracker/SKILL.md) · [`dark-social-attributor`](../social/observe/dark-social-attributor/SKILL.md) · [`social-measurement-loop`](../social/observe/social-measurement-loop/SKILL.md)

### Email Marketing

- **setup:** [`deliverability-qa`](../email/setup/deliverability-qa/SKILL.md) · [`list-segment-builder`](../email/setup/list-segment-builder/SKILL.md) · [`list-growth-designer`](../email/setup/list-growth-designer/SKILL.md) · [`list-hygiene-monitor`](../email/setup/list-hygiene-monitor/SKILL.md)
- **engage:** [`email-creative-builder`](../email/engage/email-creative-builder/SKILL.md) · [`subject-line-lab`](../email/engage/subject-line-lab/SKILL.md) · [`email-render-builder`](../email/engage/email-render-builder/SKILL.md) · [`dynamic-content-personalizer`](../email/engage/dynamic-content-personalizer/SKILL.md)
- **nurture:** [`email-sequence-designer`](../email/nurture/email-sequence-designer/SKILL.md) · [`newsletter-monetization-planner`](../email/nurture/newsletter-monetization-planner/SKILL.md) · [`preference-frequency-manager`](../email/nurture/preference-frequency-manager/SKILL.md) · [`reactivation-specialist`](../email/nurture/reactivation-specialist/SKILL.md)
- **deliver:** [`email-quality-auditor`](../email/deliver/email-quality-auditor/SKILL.md) · [`send-experiment-designer`](../email/deliver/send-experiment-designer/SKILL.md) · [`inbox-placement-monitor`](../email/deliver/inbox-placement-monitor/SKILL.md) · [`cold-outbound-sequencer`](../email/deliver/cold-outbound-sequencer/SKILL.md)

### Paid Ads

- **research:** [`campaign-architect`](../ad/research/campaign-architect/SKILL.md) · [`audience-segment-builder`](../ad/research/audience-segment-builder/SKILL.md) · [`search-term-miner`](../ad/research/search-term-miner/SKILL.md) · [`product-feed-optimizer`](../ad/research/product-feed-optimizer/SKILL.md)
- **orchestrate:** [`ad-creative-builder`](../ad/orchestrate/ad-creative-builder/SKILL.md) · [`ad-test-designer`](../ad/orchestrate/ad-test-designer/SKILL.md) · [`bid-strategy-planner`](../ad/orchestrate/bid-strategy-planner/SKILL.md) · [`landing-experience-checker`](../ad/orchestrate/landing-experience-checker/SKILL.md)
- **activate:** [`ad-account-auditor`](../ad/activate/ad-account-auditor/SKILL.md) · [`conversion-signal-qa`](../ad/activate/conversion-signal-qa/SKILL.md) · [`placement-exclusion-manager`](../ad/activate/placement-exclusion-manager/SKILL.md) · [`conversion-value-mapper`](../ad/activate/conversion-value-mapper/SKILL.md)
- **scale:** [`paid-measurement-loop`](../ad/scale/paid-measurement-loop/SKILL.md) · [`attribution-reconciler`](../ad/scale/attribution-reconciler/SKILL.md) · [`budget-pacing-monitor`](../ad/scale/budget-pacing-monitor/SKILL.md) · [`fatigue-frequency-manager`](../ad/scale/fatigue-frequency-manager/SKILL.md)

### Influencer Marketing

- **scout:** [`audience-mapper`](../influencer/scout/audience-mapper/SKILL.md) · [`trend-spotter`](../influencer/scout/trend-spotter/SKILL.md) · [`influencer-discovery`](../influencer/scout/influencer-discovery/SKILL.md) · [`fit-scorer`](../influencer/scout/fit-scorer/SKILL.md)
- **target:** [`competitor-tracker`](../influencer/target/competitor-tracker/SKILL.md) · [`campaign-planner`](../influencer/target/campaign-planner/SKILL.md) · [`brief-generator`](../influencer/target/brief-generator/SKILL.md) · [`budget-optimizer`](../influencer/target/budget-optimizer/SKILL.md)
- **activate:** [`outreach-manager`](../influencer/activate/outreach-manager/SKILL.md) · [`creator-content-auditor`](../influencer/activate/creator-content-auditor/SKILL.md) · [`contract-helper`](../influencer/activate/contract-helper/SKILL.md) · [`content-amplifier`](../influencer/activate/content-amplifier/SKILL.md)
- **report:** [`landing-optimizer`](../influencer/report/landing-optimizer/SKILL.md) · [`performance-analyzer`](../influencer/report/performance-analyzer/SKILL.md) · [`roi-calculator`](../influencer/report/roi-calculator/SKILL.md) · [`report-generator`](../influencer/report/report-generator/SKILL.md)

### Product Launch

- **research:** [`positioning-mapper`](../launch/research/positioning-mapper/SKILL.md) · [`launch-tier-planner`](../launch/research/launch-tier-planner/SKILL.md) · [`launch-window-planner`](../launch/research/launch-window-planner/SKILL.md) · [`early-access-designer`](../launch/research/early-access-designer/SKILL.md)
- **assemble:** [`message-house-builder`](../launch/assemble/message-house-builder/SKILL.md) · [`launch-asset-packager`](../launch/assemble/launch-asset-packager/SKILL.md) · [`pricing-packaging-planner`](../launch/assemble/pricing-packaging-planner/SKILL.md) · [`sales-enablement-kit`](../launch/assemble/sales-enablement-kit/SKILL.md)
- **mobilize:** [`launch-readiness-auditor`](../launch/mobilize/launch-readiness-auditor/SKILL.md) · [`launch-day-conductor`](../launch/mobilize/launch-day-conductor/SKILL.md) · [`community-launch-runner`](../launch/mobilize/community-launch-runner/SKILL.md) · [`press-media-relations`](../launch/mobilize/press-media-relations/SKILL.md)
- **prove:** [`launch-monitor`](../launch/prove/launch-monitor/SKILL.md) · [`launch-feedback-synthesizer`](../launch/prove/launch-feedback-synthesizer/SKILL.md) · [`launch-retro-analyzer`](../launch/prove/launch-retro-analyzer/SKILL.md) · [`momentum-planner`](../launch/prove/momentum-planner/SKILL.md)

## Protocol Layer

The protocol layer contains 8 skills: [`entity-registry`](../protocol/entity-registry/SKILL.md) · [`creator-registry`](../protocol/creator-registry/SKILL.md) · [`offer-claims-registry`](../protocol/offer-claims-registry/SKILL.md) · [`consent-registry`](../protocol/consent-registry/SKILL.md) · [`launch-registry`](../protocol/launch-registry/SKILL.md) · [`channel-registry`](../protocol/channel-registry/SKILL.md) · [`narrative-registry`](../protocol/narrative-registry/SKILL.md) · [`memory-management`](../protocol/memory-management/SKILL.md).

### Truth Registries

| Registry | Owner | Canonical stream | Projection | State machine |
|---|---|---|---|---|
| `entities` | [`entity-registry`](../protocol/entity-registry/SKILL.md) | `memory/events/entities.ndjson` | `memory/projections/entities.json` | — |
| `creators` | [`creator-registry`](../protocol/creator-registry/SKILL.md) | `memory/events/creators.ndjson` | `memory/projections/creators.json` | — |
| `claims` | [`offer-claims-registry`](../protocol/offer-claims-registry/SKILL.md) | `memory/events/claims.ndjson` | `memory/projections/claims.json` | — |
| `consent` | [`consent-registry`](../protocol/consent-registry/SKILL.md) | `memory/events/consent.ndjson` | `memory/projections/consent.json` | — |
| `launches` | [`launch-registry`](../protocol/launch-registry/SKILL.md) | `memory/events/launches.ndjson` | `memory/projections/launches.json` | initial draft; draft→concept, concept→alpha, alpha→beta, beta→general-availability, general-availability→archived, archived→terminal |
| `channels` | [`channel-registry`](../protocol/channel-registry/SKILL.md) | `memory/events/channels.ndjson` | `memory/projections/channels.json` | initial proposed; proposed→warming/retired, warming→active/paused/retired, active→paused/retired, paused→warming/retired, retired→terminal |
| `narrative` | [`narrative-registry`](../protocol/narrative-registry/SKILL.md) | `memory/events/narrative.ndjson` | `memory/projections/narrative.json` | — |

## Auditor Gates

| Auditor | Framework | Exclusive sink | Standalone contract |
|---|---|---|---|
| [`narrative-quality-auditor`](../narrative/evaluate/narrative-quality-auditor/SKILL.md) | TALE | `memory/audits/narrative/` | generated `references/auditor-runtime.md` |
| [`content-quality-auditor`](../seo-geo/tune/content-quality-auditor/SKILL.md) | CORE-EEAT | `memory/audits/content/` | generated `references/auditor-runtime.md` |
| [`domain-authority-auditor`](../seo-geo/evaluate/domain-authority-auditor/SKILL.md) | CITE | `memory/audits/domain/` | generated `references/auditor-runtime.md` |
| [`social-quality-auditor`](../social/host/social-quality-auditor/SKILL.md) | ECHO | `memory/audits/social/` | generated `references/auditor-runtime.md` |
| [`email-quality-auditor`](../email/deliver/email-quality-auditor/SKILL.md) | SEND | `memory/audits/email/` | generated `references/auditor-runtime.md` |
| [`ad-account-auditor`](../ad/activate/ad-account-auditor/SKILL.md) | ROAS | `memory/audits/ad/` | generated `references/auditor-runtime.md` |
| [`creator-content-auditor`](../influencer/activate/creator-content-auditor/SKILL.md) | STAR | `memory/audits/influencer/` | generated `references/auditor-runtime.md` |
| [`launch-readiness-auditor`](../launch/mobilize/launch-readiness-auditor/SKILL.md) | RAMP | `memory/audits/launch/` | generated `references/auditor-runtime.md` |

## L1 Dependency

The seven core downstream builders must carry `narrative_canon_id`, `narrative_canon_version`, `claims_projection_offset`, `dependency_status`; `dependency_status` is exactly `verified | approved-fallback | blocked`.

- [`content-writer`](../seo-geo/implement/content-writer/SKILL.md)
- [`social-creative-builder`](../social/craft/social-creative-builder/SKILL.md)
- [`email-creative-builder`](../email/engage/email-creative-builder/SKILL.md)
- [`ad-creative-builder`](../ad/orchestrate/ad-creative-builder/SKILL.md)
- [`brief-generator`](../influencer/target/brief-generator/SKILL.md)
- [`message-house-builder`](../launch/assemble/message-house-builder/SKILL.md)
- [`launch-asset-packager`](../launch/assemble/launch-asset-packager/SKILL.md)

## Symmetry Contract

Every discipline satisfies each column or cites a licensed deviation (see below); `check-architecture.py` enforces conform-or-declared and fails stale deviations.

| Discipline | Loop | Command | Registry | Gate(s) | Score surface |
|---|---|---|---|---|---|
| **Brand Narrative** | TALE (Trace -> Architect -> Land -> Evaluate) | `/narrative --phase trace\|architect\|land\|evaluate` | `narrative` (DEV-HUMANVIEW-NARRATIVE) | `narrative-quality-auditor` | profiles-only |
| **SEO/GEO** | SITE (Survey -> Implement -> Tune -> Evaluate) | `/seo-geo --phase survey\|implement\|tune\|evaluate` | `entities` | `content-quality-auditor` · `domain-authority-auditor` | Comparable overall (weighted-arithmetic-mean) · Default diagnostic (weighted-arithmetic-mean) |
| **Organic Social** | ECHO (Explore -> Craft -> Host -> Observe) | `/social --phase explore\|craft\|host\|observe` | `channels` | `social-quality-auditor` | profiles-only |
| **Email Marketing** | SEND (Setup -> Engage -> Nurture -> Deliver) | `/email --phase setup\|engage\|nurture\|deliver` | `consent` | `email-quality-auditor` | EQS (weighted-arithmetic-mean) |
| **Paid Ads** | ROAS (Research -> Orchestrate -> Activate -> Scale) | `/ad --phase research\|orchestrate\|activate\|scale` | `claims` | `ad-account-auditor` | RQS (weighted-arithmetic-mean) |
| **Influencer Marketing** | STAR (Scout -> Target -> Activate -> Report) | `/influencer --phase scout\|target\|activate\|report` | `creators` | `creator-content-auditor` | SQS (weighted-arithmetic-mean) |
| **Product Launch** | RAMP (Research -> Assemble -> Mobilize -> Prove) | `/launch --phase research\|assemble\|mobilize\|prove` | `launches` (DEV-HUMANVIEW-LAUNCHES) | `launch-readiness-auditor` | profiles-only |

### Licensed Deviations

| ID | Rule | Scope | Since | Rationale |
|---|---|---|---|---|
| `DEV-HUMANVIEW-LAUNCHES` | `SYM-09-human-view` | `registry:launches` | 18.0.0 | memory/launch/<skill>/ is the launch discipline's working-notes namespace, and the dossier/calendar view predates v18 in end-user projects; renaming the human view would orphan user state. (source: `references/skill-contract.md`) |
| `DEV-HUMANVIEW-NARRATIVE` | `SYM-09-human-view` | `registry:narrative` | 18.0.0 | memory/narrative/<skill>/ is the narrative discipline's working-notes namespace, and canon.md/versions.md predate v18 in end-user projects; renaming the human view would orphan user state. (source: `references/skill-contract.md`) |

## Distribution Profiles

| Profile | Shared root references | Executable runtime | Auditor contract |
|---|---|---|---|
| `repository` | True | True | root references plus typed scorer |
| `standalone-skill` | False | False | generated immutable references/auditor-runtime.md |
| `npx-skills` | False | host-dependent | skill directory including generated references |

Generated from the typed catalog; edit the JSON source and regenerate.
