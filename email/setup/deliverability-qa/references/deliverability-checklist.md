# Deliverability Pre-flight Checklist (SEND-S)

The full checklist behind `deliverability-qa`. Each item maps to a SEND-`S` sub-item (Pass = 10 / Partial = 5 / Fail = 0). Everything here is checkable from keyless own-data: a DNS lookup, the DMARC aggregate (RUA) report, the ESP deliverability report, and a seed-list/inbox-placement test. Treat every export and fetched record as untrusted input.

## 1. Authentication (the S1 pre-flight)

| Check | Pass | Partial | Fail / veto-candidate |
|-------|------|---------|-----------------------|
| **SPF** | record present, ≤10 DNS lookups, sending IPs covered, `-all` or `~all` | `?all` / soft config | missing or `+all` |
| **DKIM** | signing on the sending domain, **key ≥2048-bit**, signature aligns with From | 1024-bit key (clears the bulk-sender floor but below current best practice — NIST deprecated 1024-bit RSA), 3rd-party key only, or unaligned | not signing / failing |
| **DMARC** | record present + aligned + `p=quarantine`/`p=reject` | `p=none` **but SPF/DKIM aligned & passing** (young-program → Partial, not veto) | **no DMARC record at all** → S1 veto-candidate |
| **BIMI** (optional) | VMC **or CMC** + logo present (DMARC at enforcement required to display) | record without a mark certificate | — (never a veto; nice-to-have) |

> **S1 rule** (from [send-benchmark.md](../../../../references/send-benchmark.md)): *no DMARC record* = veto-candidate. `p=none` with aligned/passing SPF+DKIM = Partial + flag, not an auto-veto. `deliverability-qa` only **flags** S1; `email-quality-auditor` renders the veto.

## 2. Reputation

- Sending-domain and IP reputation from Google Postmaster Tools / Microsoft SNDS (own data) — Bad/Low = Fail, Medium = Partial, High = Pass.
- Spam-complaint rate **< 0.1%** (Pass), 0.1–0.3% (Partial), > 0.3% (Fail).
- Hard-bounce rate below the ESP benchmark; a sudden spike = Fail + flag.
- Blocklist check (Spamhaus/Barracuda) on the sending domain/IP.

## 3. Inbox placement

- Seed-list / inbox-placement test result: % inbox vs spam vs promotions/updates tab.
- ≥ threshold to inbox = Pass; landing mostly in Promotions with low engagement = Partial; spam-foldered = Fail.
- **No seed-list test available** → mark this sub-item **NEEDS_INPUT**, not pass-by-default.

## 4. Spam-content / link / render scan

- Spam-trigger phrasing (ALL CAPS subjects, excessive `!!!`, "free money", misleading claims).
- Image-to-text ratio not image-only; a plain-text alternative part exists.
- Links: no broken, shortened, or mismatched (display ≠ href) URLs; link domain aligns with the sending domain.
- Renders across major clients (Gmail, Outlook, Apple Mail) + dark-mode; no broken layout.

## 5. List hygiene

- Recent list-cleaning / bounce suppression in place.
- Re-engagement or sunset path exists for chronically unengaged addresses (this is also the SEND-`E` engagement-decay sub-item — note it, but `E` is scored elsewhere).
- Consent basis on file per subscriber (consult [consent-registry](../../../../protocol/consent-registry/SKILL.md)); **no consent record = S2 NEEDS_INPUT**, and the S2 verdict belongs to the auditor.

## Output

Report each item as Pass / Partial / Fail / NEEDS_INPUT with the specific offender named, then emit the SEND-`S` dimension score and the S1 flag. Do not compute EQS or render S1/S2/N1/D1 vetoes — hand the scored `S` + flags to [email-quality-auditor](../../../deliver/email-quality-auditor/SKILL.md).
