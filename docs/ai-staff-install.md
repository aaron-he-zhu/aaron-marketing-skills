# AI Staff install (Hermes + Grok)

Minimal in-repo operator guide for the **8-bot AI Staff**. The product is the
existing roster — `aaron-chief` plus seven discipline specialists — generated
from [`references/system-catalog.json`](../references/system-catalog.json) by
[`scripts/generate-bot-projections.py`](../scripts/generate-bot-projections.py).
This page covers generate → install → boundaries. It does not add a 121st
Skill, a Web UI, Usage Gateway, billing, or cloud hosting.

Long-form narrative and SEO live on the
[aaronmarketing.ai docs hub](https://aaronmarketing.ai/docs/ai-staff)
(placeholder hub path until the canonical docs URL is published). Do not treat
that page as shipped metrics or a verified-host claim.

## Prerequisites

- A clone of this repository and **Python 3** (stdlib only; no `pip`).
- An **empty directory outside the repository**. The generator refuses in-repo
  output and never writes a commit-able `skills/` mirror.
- **Hermes path:** Hermes Agent CLI with Bot Mode / profile distributions.
- **Grok path:** Grok Bot app (macOS, Windows, or iOS). There is no public bulk
  bot-import format — setup is semi-manual.

No connector attach, marketplace template publish, or vendor contact is part of
this flow.

## Generate the roster

```bash
python3 scripts/generate-bot-projections.py --output /private/path/aaron-bot-roster
```

The command prints `built bot-roster projection v<bundle>: 8 bots, 120 skills`.
Together the eight bots cover the 120 canonical skills **exactly once**.

## Output layout

```
<output>/
  bot-roster.json                 # hash-bound roster (catalog + host-profile SHAs)
  distribution-manifest.json
  hermes/<bot>/                   # one installable Hermes profile bundle each
    distribution.yaml
    SOUL.md
    README.md
    PORTABILITY.md
    distribution-manifest.json
    skills/<name>/SKILL.md        # that bot's partition only
    references/policy-kernel.md
  grok/
    bot-cards.md                  # name / title / description per bot
    enable-lists.md               # exact per-bot skill enablement
    setup-checklist.md
    distribution-manifest.json
```

`<bot>` directories are `hermes/narrative`, `hermes/seo-geo`, `hermes/social`,
`hermes/email`, `hermes/ad`, `hermes/influencer`, `hermes/launch`, and
`hermes/chief` (`aaron-chief`). Generated files stay **outside** Git.

## Hermes — `profile install`

1. Publish **one** `hermes/<bot>/` directory as its own git repository
   (private is fine). Do not commit the whole roster back into this repo.
2. Install the profile:

   ```bash
   hermes profile install <your-git-url> --alias
   aaron-chief chat
   ```

3. Repeat for the seven specialists, or start with `@aaron-chief` and add
   lanes as you need them.
4. Updates: push the regenerated bundle, then `hermes profile update <alias>`.

Each bundle README repeats the same install block. Profile skills sit below
project skills and above `skills.external_dirs` in Hermes precedence.

**Offline check (this repo, no host):**
`python3 scripts/smoke-bot-projections.py` proves roster completeness, Hermes
bundle shape, Grok artifacts, hash-bound manifests, and no secret/state paths.
It does **not** mark Hermes Bot Mode as a verified host.

## Grok — Bot cards / enable lists / checklist

Grok Bot has no bulk import. Follow `grok/setup-checklist.md` from the
generated pack:

1. **Create bots** from `grok/bot-cards.md` — `@aaron-chief` first, then the
   seven specialists. Paste name/title/description **verbatim** (descriptions
   drive cross-bot routing).
2. **Install skills** via Settings → Plugins when your plan exposes them
   (Portable Lite release asset), or the officially supported fallback: save a
   skill from written instructions pasted in chat. Name each skill exactly as
   listed.
3. **Enable lists** — apply `grok/enable-lists.md` per bot. Do not enable the
   full catalog on every bot.
4. **Standing rules** on each card: approval before send/publish/purchase/
   delete/production change; no social posting/engagement/DM automation;
   registries propose-only; auditors return `NOT_SCORED` without the
   deterministic scorer.
5. **Dry-run** each bot on a safe read-only task and confirm it stops at the
   approval boundary.

## Boundaries (both hosts)

| Rule | Meaning |
|------|---------|
| **Tier-1 static** | No connectors, `mcp.json`, cron, hooks, or repository runtimes in the bundle. |
| **`NOT_SCORED`** | Auditor skills do not hand-calculate TALE/CORE-EEAT/CITE/STAR/ROAS/SEND/RAMP/ECHO verdicts. |
| **Propose-only registries** | Bot sessions prepare proposals. Canonical acceptance is an owner-run step outside bot sessions. |
| **Shared Grok computer** | All bots on one Grok account share one persistent cloud computer. Files, browser sessions, and logins are visible to every bot — names are not security boundaries. |
| **Handoffs** | Cross-lane work goes by `@mention` (`@aaron-chief` first). Visited set; at most three automatic handoffs. |
| **No Gateway** | Phase 1 does not include Usage Gateway, billing, a thin shell UI, or cloud hosting of this roster. |

## Automated smoke vs owner-run host smoke

| Check | Where | Status |
|-------|-------|--------|
| Generator roster contract (8 bots, exact partition, Hermes shape, Grok artifacts, hash-bound manifests, no secrets paths) | `python3 scripts/smoke-bot-projections.py` (CI validate workflow) | **Automated** |
| Hermes `profile install` on a real host; Grok Bot create/enable/dry-run; Grok Build filesystem skills; Hermes `skills.external_dirs` | [agent-compatibility.md](agent-compatibility.md#named-bot--grok-smoke-backlog) | **Owner-run · Pending** |

Owner-run rows stay `Pending` until the owner records host evidence. Automated
smoke never claims a public template publish, a vendor contact, or a verified
client install.

## See also

- [Agent compatibility — named-bot deployment](agent-compatibility.md#named-bot-roster-deployment-grok-bot--hermes-bot-mode)
- [Portable Lite package boundary](agent-plugins-v1.md)
- [Docs index](README.md) — which pages stay in-repo vs the docs hub
