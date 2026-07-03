# Client Render Matrix (SEND-E QA)

The per-client support facts `email-render-builder` uses to fill the render-QA matrix. **Every row is Estimated** unless the user ran a real seed-list / inbox-preview test — then that row is Measured. Never present an Estimated render pass as Measured; name the row a call came from.

## Target set (default)

Gmail (app + web), Outlook (desktop Word-engine + web/new Outlook), Apple Mail, iOS Mail, Android (Gmail/Samsung Mail).

## Support facts (Estimated baseline)

| Client | Rendering quirk to check | Common breakage |
|---|---|---|
| **Outlook desktop** | Word (`mso`) engine — no `float`/`flex`/`grid`, spotty `border-radius`, needs ghost tables + VML buttons | broken multi-column, square/clipped buttons, extra gaps |
| **Gmail (web + app)** | strips/relocates `<head>` `<style>`; clips messages >102KB ("[Message clipped]") | media queries dropped, dark-mode auto-inversion, clipped tail |
| **Apple Mail / iOS Mail** | strong CSS + media-query support; aggressive dark-mode inversion | logos/text lost on forced-dark backgrounds |
| **Android (Gmail/Samsung)** | mixed dark-mode handling; smaller tap targets | reflow gaps, sub-44px tap targets |
| **Outlook web / new Outlook** | closer to standards than desktop; still partial | dark-mode + `<style>` handling differs from desktop |

## Matrix template (fill per email)

| Client | Layout | Dark mode | Images-off | Verdict | Label |
|---|---|---|---|---|---|
| Gmail web | ✓ / ✗ | ✓ / ✗ | ✓ / ✗ | pass/fail + note | Measured/Estimated |
| Gmail app | | | | | |
| Outlook desktop | | | | | |
| Outlook web | | | | | |
| Apple Mail | | | | | |
| iOS Mail | | | | | |
| Android | | | | | |

## Labeling rule

- **Measured** — the user ran a seed-list / inbox-preview / render-preview test and you read the actual render.
- **Estimated** — derived from the support facts above; no real render seen. State it plainly and, where a client's behavior is genuinely unknown, return it as an open loop rather than guessing a pass.

Keyed render-preview services (Litmus, Email on Acid) are an optional Tier-2/3 convenience that can upgrade a row to Measured; they are never a Tier-1 precondition.
