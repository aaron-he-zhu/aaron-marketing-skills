# Email Render Specs (SEND-E build)

Build patterns and QA checklists for `email-render-builder`. The layout carries the approved copy from [email-creative-builder](../../email-creative-builder/SKILL.md) unchanged; this pack governs the *build*, not the words. All checklists feed the render-QA report that [email-quality-auditor](../../../deliver/email-quality-auditor/SKILL.md) reads before scoring the E/D unit.

## Layout skeleton

- **Table-based, single column.** Nested `<table>`/`<td>` for structure — not `float`, `flex`, or `grid` (Outlook's Word rendering engine ignores them).
- **Constrained width ≈600px** content area inside a full-width background wrapper; content column set with a fixed `width` attribute *and* inline `max-width` so mobile can reflow.
- **Inline styles only** for anything load-bearing; a `<style>` block may hold media queries and dark-mode rules but must degrade gracefully — Gmail strips/relocates `<head>` styles.
- **No external dependency** — no linked stylesheet, no web-font `@import` that blocks render; use a system-font stack with brand-font as an enhancement only.

## Responsive approach

| Approach | How | Client support |
|---|---|---|
| **Fluid / hybrid** | percentage widths + `max-width` + `mso` ghost tables | widest — works even where media queries are stripped |
| **Media-query** | `@media max-width` reflow in `<style>` | good on Apple/iOS/Android; unreliable on some Gmail/Outlook contexts |

Default to fluid/hybrid for a broad target set; note the choice. Tap targets ≥44px; body font ≥14px (≥16px preferred) so mobile reads without zoom.

## Dark-mode checklist (pass / fail each)

- [ ] Explicit `color` + `background-color` set on text containers (do not rely on client defaults).
- [ ] Every foreground/background pair passes contrast in **light** mode (≥4.5:1 body text).
- [ ] Every pair still passes after a **dark-mode inversion** (text not buried, logo not lost on a now-dark panel).
- [ ] Logos / dark-on-transparent images have a padded solid backing or a dark-mode variant.
- [ ] No color-only meaning (a link is underlined/bolded, not only colored).

## Accessibility checklist (pass / fail each)

- [ ] Semantic reading order — content order in source matches visual order.
- [ ] Meaningful `alt` on every content image; `alt=""` only for pure decoration.
- [ ] `lang` attribute set; a real `<title>`/preheader present.
- [ ] Body contrast ≥4.5:1; base font size holds on mobile.
- [ ] Links are descriptive (no bare "click here" as the only cue).

## Image-off fallbacks (required)

Many clients block images by default — the email must still work.

- Every image has `alt` text that conveys its message.
- **No offer, price, claim, or CTA lives only inside an image.**
- Background images carry a solid `bgcolor` fallback.
- Each CTA is a **bulletproof button** — HTML/CSS, not an image:

```html
<!--[if mso]><v:roundrect ... fillcolor="#1a56db"><![endif]-->
<a href="{{DEST_URL}}" style="background:#1a56db;color:#ffffff;
   padding:14px 28px;border-radius:6px;text-decoration:none;
   display:inline-block;font-size:16px;">{{CTA label}}</a>
<!--[if mso]></v:roundrect><![endif]-->
```

## Plain-text parity

The `text/plain` alternate must carry the same core message, the same primary CTA, and the same destination URL as the HTML. Diff the shipped plain-text alt against the HTML; if none shipped, produce one. A copy-driven mismatch (subject too long to render, CTA label overflows the button) is not a build fix — flag it and route to [email-creative-builder](../../email-creative-builder/SKILL.md).
