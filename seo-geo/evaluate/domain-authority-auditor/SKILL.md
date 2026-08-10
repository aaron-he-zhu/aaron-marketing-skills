---
name: domain-authority-auditor
slug: domain-authority-auditor
displayName: "Domain Authority Auditor · 域名权威"
summary: "域名权威/网站可信度"
description: 'Use when auditing domain authority, trust, or citation credibility; runs a peer-relative 40-item CITE profile with evidence coverage and verified manipulation/penalty veto checks. Not for page-level content quality — use content-quality-auditor; not for backlink profiling alone — use offsite-signal-analyzer. 域名权威/网站可信度'
version: "19.2.0"
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
homepage: "https://github.com/aaron-he-zhu/aaron-marketing-skills"
when_to_use: "Use when auditing domain trust and citation authority against a declared peer cohort. Runs the typed CITE 40-item profile with explicit evidence gaps and veto verification."
argument-hint: "<domain> <market> <peer cohort> [domain type]"
class: auditor
metadata: {"author": "aaron-he-zhu", "version": "19.2.0", "discipline": "seo-geo", "phase": "evaluate", "geo-relevance": "medium", "hermes": {"tags": ["marketing", "seo-geo", "evaluate"], "category": "seo-geo"}, "openclaw": {"emoji": "🔍", "homepage": "https://github.com/aaron-he-zhu/aaron-marketing-skills"}}
---

# Domain Authority Auditor

Audit one domain's citation-trust signals relative to a declared peer cohort. Produce a complete CITE score only when all applicable evidence and comparison context are present. CITE is advisory; it does not predict whether an answer engine will cite the domain.

## When This Must Trigger

- The user asks whether a domain is trustworthy, authoritative, or citation-ready.
- A campaign needs a peer-relative CITE baseline or rerun.
- Link, entity, penalty, or citation evidence may materially change a domain gate.

## Quick Start

```text
Audit example.com against these five same-stage U.S. SaaS peers.
Run the CITE content-publisher profile; mark every private-data gap Unknown.
```

## Skill Contract

Use `offsite-signal-analyzer` for link diagnosis without a gate, `content-quality-auditor` for one page, and `entity-registry` for canonical entity repair. Compare multiple domains as separate same-profile runs; never score them as one pooled target.

**Reads:** one domain, one locked cohort, and dated citation/identity/trust/eminence evidence. **Writes:** only a permissioned v3 artifact. **Done when:** context is complete, all 40 states are explicit, the scorer result is preserved, and any saved artifact validates.

## Instructions

### Runtime Reads

- `../../../references/auditor-runbook.md`
- `../../../references/scoring-semantics.md`
- `../../../references/cite-domain-rating.md`
- `../../../references/framework-catalog.json`
- `../../../references/runtime-invocation.md`
- `references/auditor-runtime.md`

### Runtime Contract

Read `../../../references/auditor-runbook.md`, `scoring-semantics.md`, `cite-domain-rating.md`, and the `CITE` entry in `framework-catalog.json`. For standalone installs, use bundled immutable `references/auditor-runtime.md`; never fetch mutable `main` or guess missing policy. Before deterministic calls, follow [`runtime-invocation.md`](../../../references/runtime-invocation.md), resolve `AARON_SKILLS_ROOT="${CLAUDE_PLUGIN_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || true)}"`, and require the scorer, validator, and typed catalogs. If unavailable, return `score_state: NOT_SCORED` / `score_confidence: not_scored` with no gate verdict or persistent artifact.

### Required Setup

Declare:

- one canonical domain and observation date;
- market and entity stage;
- domain type/profile: `default`, `content-publisher`, `product-service`, `ecommerce`, `community-ugc`, `tool-utility`, or `authority-institutional`;
- a locked peer cohort with inclusion rules and evidence window.

Without peer cohort, market, stage, or domain type, return `NEEDS_INPUT/UNDECIDED`; the inherited numeric anchors are diagnostic priors, not universal thresholds.

## Data Sources

| Need | Preferred evidence |
|---|---|
| Links | Dated backlink export/index with known coverage |
| Identity | Structured data, canonical profiles, knowledge-graph/public entity evidence |
| Trust | Link-history comparison, security checks, authorized console evidence |
| Eminence | Search/analytics visibility and locked peer/query panels |
| Cohort | Named domains plus inclusion/exclusion, market, stage, type, and window |

### Evidence Procedure

1. Normalize the domain and verify scope (host/subdomain/protocol treatment).
2. Freeze backlink, entity, security, search visibility, citation-panel, and reputation evidence with sources/dates.
3. Evaluate all 40 IDs against the declared cohort. Tool estimates remain `estimated` or `proxy`; user exports remain `user-provided` unless independently verified.
4. Use Unknown for absent backlink indexes, private console data, or comparison universes. Do not mark link-dependent items N/A simply because data is unavailable.
5. Apply catalog-authorized N/A only with a reason, for example an AI-citation item when no locked panel is in scope.
6. Verify vetoes positively:
   - `CITE-T03`: material link/traffic incoherence plus corroborating manipulation evidence relative to the cohort.
   - `CITE-T05`: verified manipulation network after common-source/ecosystem adjustment.
   - `CITE-T09`: verified active manual action or material unresolved deindexing.

Domain youth, privacy-protected WHOIS, low absolute volume, or missing private-console access cannot by themselves fail a veto.

Create a typed `audit-run.schema.json` input and execute `python3 "$AARON_SKILLS_ROOT/scripts/rubric-score.py" score <run.json>` when the verified runtime is available. Never renormalize weights around Unknown items.

## Report

Begin with the auditor-runbook's exact typed conversation header. Never replace `status`, `verdict`, or `score_state` with prose; list each explicitly missing qualified item as ``ID: `unknown``` before findings.

Lead with verdict, profile/cohort/target/date, score or `NOT_SCORED` coverage/interval, and confidence. Then provide:

- C/I/T/E score and coverage table;
- peer-relative evidence and cohort definition;
- verified risks versus unresolved Unknowns;
- top fixes with owner, evidence needed, and rerun condition;
- provenance appendix, including qualified IDs when detailed traceability is requested.

Use SHIP/FIX/BLOCK/UNDECIDED as the canonical artifact verdict. User-facing prose may say trusted/cautious only as a descriptive translation, never as a separate decision system.

## Verdict Rules

- Complete, no veto, healthy score/no failures: `DONE` + `SHIP`.
- Complete, remediation needed or one veto: `DONE_WITH_CONCERNS` + `FIX`; one veto caps final at 59.
- Complete, 2+ verified vetoes: `DONE` + `BLOCK`; no final score.
- Missing applicable/cohort evidence: `NEEDS_INPUT` + `UNDECIDED`; no score.

Route link investigation to `offsite-signal-analyzer`, technical/index evidence to `technical-seo-checker`, entity repair to `entity-registry`, and page quality to `content-quality-auditor`.

## §2 CITE Worked Examples

- Complete product-service profile, raw 78, one verified T09 failure: `DONE_WITH_CONCERNS/FIX`, final 59.
- Complete profile, raw 45, one verified T05 failure: final remains 45; the ceiling never raises a score.
- Verified T03 and T05 failures with complete evidence: `DONE/BLOCK`, raw retained, no final score.
- Missing backlink universe or private-console evidence: affected items are Unknown and no total is emitted.

## §3 CITE Guardrails

- Young domain age and WHOIS privacy are neutral without contradictory evidence.
- A press/launch spike can explain link velocity; test the explanation before labeling manipulation.
- Absolute volume is interpreted within peer cohort, entity stage, market, and domain type.
- Public index absence does not prove a private manual action; T09 requires positive evidence.

## §5 CITE Translation

Use plain descriptions by default. On a trace request, show `CITE-T03`, `CITE-T05`, and `CITE-T09` with source/date/cohort; never expose an unqualified ID.

## Persistence

Persist only after explicit authorization. Assemble the complete v3 draft, validate it against the intended `memory/audits/domain/YYYY-MM-DD-<topic>.md` relative path, persist only through one full-content Write, and revalidate the target. Edit/shell/MCP mutations of the reserved sink are unsupported. Use:

```bash
python3 "$AARON_SKILLS_ROOT/scripts/validate-audit-artifact.py" <draft> --relative-path <target>
```

The audit request itself does not authorize hot-cache, candidate, or registry writes.

## Validation Checkpoints

- Target/profile/market/stage/cohort are explicit and locked.
- All 40 IDs have evidence-backed state, Unknown, or valid N/A.
- Absolute anchors were not applied as cohort-independent laws.
- Vetoes are verified failures, not absence-of-evidence shortcuts.
- Scorer output, coverage, confidence, status, and verdict are preserved.
- Persisted artifact is permissioned, path-correct, minimized, and validator-clean.

## Reference Materials

- [CITE benchmark](../../../references/cite-domain-rating.md)
- [Auditor runbook](../../../references/auditor-runbook.md)
- [Scoring semantics](../../../references/scoring-semantics.md)
- [Offsite signal analyzer](../offsite-signal-analyzer/SKILL.md)

## Next Best Skill

- **Investigate links:** [offsite-signal-analyzer](../offsite-signal-analyzer/SKILL.md)
- **Repair entity state:** [entity-registry](../../../protocol/entity-registry/SKILL.md)
- **Verify technical/index state:** [technical-seo-checker](../../tune/technical-seo-checker/SKILL.md)
- **Audit representative content:** [content-quality-auditor](../../tune/content-quality-auditor/SKILL.md)
