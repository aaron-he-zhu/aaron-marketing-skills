# Contributing

Thanks for your interest in contributing! This guide covers adding skills, improving existing ones, and submitting changes.

## Requesting a Skill

[Open a Skill Request issue](https://github.com/aaron-he-zhu/aaron-marketing-skills/issues/new?template=skill-request.yml) if you have an idea but don't want to build it yourself.

## Adding a New Skill

### 1. Choose the correct category

| Category | Directory | Use when the skill... |
|----------|-----------|----------------------|
| Research | `research/` | Gathers market data before content creation (SEO/GEO) |
| Build | `build/` | Creates new content or markup (SEO/GEO) |
| Optimize | `optimize/` | Improves existing content or site health (SEO/GEO) |
| Monitor | `monitor/` | Tracks performance over time (SEO/GEO) |
| Protocol | `protocol/` | Cross-cutting layer (truth registries: entity/creator/claims/consent + memory) — shared across disciplines |
| Discover | `discover/` | Audience/niche mapping + influencer discovery & fit (influencer/IMPACT) |
| Plan | `plan/` | Competitor tracking, campaigns, briefs, budgets (influencer/IMPACT) |
| Activate | `activate/` | Outreach, content review (C³ ART gate), contracts, amplification (influencer/IMPACT) |
| Measure | `measure/` | Post-click, performance, ROI, reports (influencer/IMPACT) |
| Paid Ads | `paid/<phase>/` | Builds, audits, and scales paid-ad campaigns (ROAS loop: research/orchestrate/activate/scale) |
| Email | `email/<phase>/` | Grows, sends, and audits email programs (SEND loop: setup/engage/nurture/deliver) |

### 2. Create the skill directory

```bash
mkdir -p <category>/<skill-name>
```

Directory name: 1-64 chars, lowercase `a-z`, numbers, hyphens only. No leading/trailing/consecutive hyphens.

### 3. Create `SKILL.md` with required frontmatter

```yaml
---
name: your-skill-name
version: "1.0.0"
description: 'Use when the user asks to "[trigger]". [What it does]. For [related task], see [other-skill].'
license: Apache-2.0
compatibility: "Claude Code and compatible agent-skill hosts"
metadata:
  author: your-github-username
  version: "1.0.0"
  geo-relevance: "high|medium|low"
  tags: [seo, your-tags]
  triggers: ["trigger phrase 1", "trigger phrase 2"]
---
```

The `name` field must match the directory name exactly.

### 4. Write effective instructions

Use the compact shared skeleton from `references/skill-contract.md`: `Quick Start`, `Skill Contract`, `Handoff Summary`, `Data Sources`, `Instructions`, `Reference Materials`, and `Next Best Skill`. Optional sections such as `What This Skill Does`, `Example`, `Tips for Success`, `Save Results`, and `Validation Checkpoints` are welcome when they improve execution quality. Put detailed references in the skill's `references/` subdirectory.

Auditor-class skills are the exception: they `Read references/auditor-runbook.md` at activation (the framework-agnostic SSOT: handoff schema, cap method, Artifact Gate, translation format) via a plugin-relative path, and keep only their framework-specific §2 worked examples, §3 guardrails, and §5 veto-ID rows inline in the `SKILL.md` body. Five skills are auditor-class gate consumers, each scored against one framework and writing to its own audit sink:

| Auditor-class skill | Framework | Audit sink |
|---------------------|-----------|------------|
| `content-quality-auditor` | CORE-EEAT (publish readiness) | `memory/audits/content/` |
| `domain-authority-auditor` | CITE (citation trust) | `memory/audits/domain/` |
| `content-reviewer` | C³ ART (influencer content gate) | `memory/audits/influencer/` |
| `ad-account-auditor` | ROAS RQS (paid-ads gate) | `memory/audits/paid/` |
| `email-quality-auditor` | SEND EQS (email SEND gate) | `memory/audits/email/` |

Cross-cutting reference protocols apply across disciplines: the humanizer-slop protocol, the measurement-protocol decision protocol, and the per-channel `platforms/` reference packs. These stay references (not skills) by design — each is consumed as a pre-handoff sub-step inside discipline skills, so promoting one to a standalone skill would duplicate that step.

### 5. Validate

```bash
./scripts/validate-skill.sh <category>/<skill-name>
```

CI runs additional guards beyond the per-skill validator:
- **golden-math** — validates the rollup math for all **five** quality frameworks: CORE-EEAT (80-item content quality, SEO/GEO), CITE (40-item domain authority, SEO/GEO), C³ (influencer — ACE/ART/ROI with CVI geometric-mean rollup, veto ACE A2/C1/E2 + ART T1/T2), ROAS (paid ads — R Return / O Offer / A Audience / S Spend-efficiency, RQS arithmetic weighted-mean rollup like CITE, veto R1/R2/O1/O2/A1; see [references/roas-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/roas-benchmark.md)), and SEND (email — S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response, EQS arithmetic goal-weighted-mean rollup like ROAS, veto S1/S2/N1/D1; see [references/send-benchmark.md](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/send-benchmark.md)).
- **check-evals** — structural lint over the eval fixtures.
- **check-pii** — scans for committed PII.
- **check-stdlib-only** — enforces the zero-dependency Python-stdlib rule for connector helpers, including the Paid-Ads keyed-API red line (no keyed paid-ad API calls baked into skills).

### 6. Update tracking files

After adding or updating a skill, keep these **8 tracking files** in sync. **This list is authoritative** — `CLAUDE.md` and `AGENTS.md` point here instead of restating it, so update this list if the set changes.
- `VERSIONS.md` — version and date
- `.claude-plugin/plugin.json` — skills array + version
- `marketplace.json` (repo root) — must match plugin.json
- `.claude-plugin/marketplace.json` — **byte-identical mirror** of the root `marketplace.json` (copy it after editing the root)
- `README.md` — skills table + version badge
- `CLAUDE.md` — category table + version
- `AGENTS.md` — name/count line + framework item/dimension counts (CORE-EEAT / CITE / C³ / ROAS / SEND)
- `docs/README.zh.md` — Chinese README: the 69 · 16 / 16 / 16 / 16 / 5 counts (skills / SEO-GEO / influencer / paid ads / email / protocol) + 5 commands + version badge

For release bumps, also sync README badges and localized README badges.

## Improving Existing Skills

Keep changes focused. Bump both top-level `version` and `metadata.version` together. Update `VERSIONS.md`. Put new reference docs in the skill's `references/` subdirectory.

## Craft Checklist

Beyond the mechanical checks, every skill should pass the senior self-test from [skill-contract.md §Skill Authoring Discipline](https://github.com/aaron-he-zhu/aaron-marketing-skills/blob/main/references/skill-contract.md):

- [ ] **Simplicity** — would a senior engineer call this skill overcomplicated? Every section traces to the user's task.
- [ ] **Boundary** — the `description` ends with a `Not for X — use Y` clause so it doesn't compete with a sibling skill.
- [ ] **Verifiable** — the Skill Contract states a `Done when:` with checkable conditions.
- [ ] **Honest data** — Instructions tell the model to label Measured / User-provided / Estimated and never invent numbers.
- [ ] **Surgical handoff** — Next Best Skill points to exactly one primary move.

## Quality Checklist (mechanical)

Before submitting a PR:

- [ ] `name` matches directory name (lowercase slug `^[a-z0-9][a-z0-9-]*$`)
- [ ] Top-level `version` is present and matches `metadata.version` plus `VERSIONS.md`
- [ ] `description` includes trigger phrases AND scope boundaries (≤1024 chars)
- [ ] Shared compact section contract present (`validate-skill.sh` checks this)
- [ ] Validator passes: `./scripts/validate-skill.sh <category>/<skill-name>`
- [ ] Uses `~~placeholder` pattern for tool references
- [ ] `allowed-tools: WebFetch` added if skill fetches live URLs
- [ ] Includes validation checkpoints and at least one example
- [ ] All tracking and release files updated; plugin.json and marketplace.json arrays identical
- [ ] `.claude-plugin/marketplace.json` byte-identical to repo-root copy

## Submitting

- Fork, create a `feature/your-skill-name` branch, and submit a PR.

## Code of Conduct

Be respectful, constructive, and focused on making the library better for everyone.
