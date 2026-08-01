#!/usr/bin/env python3
"""doh.py — keyless DNS lookups over DNS-over-HTTPS (Google, Cloudflare fallback).

Turns the email discipline's "paste a DNS export" step into a live, Measured
record read: the `auth` subcommand fetches a sending domain's SPF, DMARC,
BIMI, and MX records and probes common DKIM selectors — the raw evidence for
the SEND S1 authentication pre-flight (deliverability-qa) and the auditor's
S1 row. `query` is the general-purpose lookup.

  Resolvers: https://dns.google/resolve            (JSON, keyless)
             https://cloudflare-dns.com/dns-query  (accept: application/dns-json)
  Auth:      none — both are free public resolvers, no key, no signup.

FACTS ONLY — this helper reports which records exist and their parsed tags
(p=, rua=, v=spf1 …). It never emits a pass/veto verdict: whether a DMARC
`p=none` is Partial or a missing record is a veto-candidate is the skill's
rubric, not the connector's. Two structural findings ARE reported as flags
because they are record facts, not judgments: more than one SPF record
(RFC 7208 permerror) and no SPF `all` mechanism.

DKIM caveat: selectors are not discoverable from DNS alone. `auth` probes a
short list of common selectors (plus any you pass via --selector); "none
found" therefore means "none of the CHECKED selectors exist", never "DKIM is
absent" — the checked list is included so the skill can mark NEEDS_INPUT.

A DNS record shows *setup*, not *passing mail*: SPF/DKIM alignment on real
traffic still comes from the DMARC aggregate (RUA) report.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 doh.py query _dmarc.example.com --type TXT
  python3 doh.py auth example.com [--selector s1,s2] [--resolver google|cloudflare]
"""
from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlencode

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

RESOLVERS = {
    "google": {"url": "https://dns.google/resolve", "accept": "application/json"},
    "cloudflare": {"url": "https://cloudflare-dns.com/dns-query",
                   "accept": "application/dns-json"},
}
# Common DKIM selectors across major ESPs — a probe list, not an exhaustive one.
DEFAULT_DKIM_SELECTORS = [
    "default", "google", "selector1", "selector2", "k1", "s1", "s2",
    "mail", "dkim", "resend", "mandrill", "pm", "zoho",
]
RECORD_TYPES = {"A", "AAAA", "TXT", "MX", "CNAME", "NS"}


def build_url(name, rtype="TXT", resolver="google"):
    """The resolver URL a lookup WOULD hit. Pure / no network."""
    r = RESOLVERS[resolver]
    return r["url"] + "?" + urlencode({"name": name, "type": rtype})


def _strip_txt(data):
    """DoH TXT payloads come quoted (and sometimes chunked): '"a" "b"' -> 'ab'."""
    s = (data or "").strip()
    if '"' in s:
        parts = []
        for chunk in s.split('"'):
            if chunk.strip() in ("", " "):
                continue
            parts.append(chunk)
        return "".join(parts)
    return s


def lookup(name, rtype="TXT", resolver="google", _fallback=True):
    """One DoH lookup -> {name, type, status, records:[str], error}.

    DNS Status 0 = NOERROR, 3 = NXDOMAIN (record simply absent — not an HTTP
    failure). On resolver/network failure, retries once via the other
    resolver before giving up.
    """
    r = RESOLVERS[resolver]
    url = build_url(name, rtype, resolver)
    resp = _http.get_json(url, accept=r["accept"])
    payload = resp.get("json")
    if not isinstance(payload, dict):
        if _fallback:
            other = "cloudflare" if resolver == "google" else "google"
            return lookup(name, rtype, other, _fallback=False)
        return {"name": name, "type": rtype, "status": None,
                "records": [], "error": resp.get("error") or "no JSON answer"}
    records = []
    for ans in payload.get("Answer") or []:
        data = ans.get("data", "")
        records.append(_strip_txt(data) if rtype == "TXT" else data)
    return {"name": name, "type": rtype, "status": payload.get("Status"),
            "records": records, "error": None}


def parse_tags(record):
    """'v=DMARC1; p=none; rua=mailto:x' -> {'v':'DMARC1','p':'none',...}."""
    tags = {}
    for part in record.split(";"):
        part = part.strip()
        if "=" in part:
            k, _, v = part.partition("=")
            tags[k.strip().lower()] = v.strip()
    return tags


def spf_facts(txt_records):
    """SPF facts from a domain's TXT records. Pure / no network."""
    spf_records = [r for r in txt_records if r.lower().startswith("v=spf1")]
    spf = {"present": bool(spf_records), "records": spf_records, "flags": []}
    if len(spf_records) > 1:
        spf["flags"].append("multiple_spf_records")  # RFC 7208 permerror
    if spf_records:
        first = spf_records[0].lower()
        # A record closed by neither an `all` mechanism nor a `redirect=`
        # modifier leaves unlisted senders undefined (RFC 7208 §4.7 / §6.1).
        # Match any `all` mechanism token (qualified -/~/?/+ or bare, = +all).
        has_all = any(t == "all" or t[1:] == "all"
                      for t in first.split())
        if not has_all and "redirect=" not in first:
            spf["flags"].append("no_all_or_redirect")
    return spf


def auth_check(domain, selectors=None, resolver="google"):
    """Fetch the email-auth record set for a sending domain. Facts only."""
    domain = domain.strip().strip(".").lower()
    out = {"domain": domain, "resolver": resolver}

    def transport_guard(res, label):
        # A transport/resolver failure (error set, no DNS status) is NOT the same
        # as a name that genuinely has no record — surface it (main() then exits
        # non-zero) instead of silently reporting a false "no records present".
        if res.get("error") and res.get("status") is None:
            msg = "DNS fetch failed for %s: %s" % (label, res["error"])
            out["error"] = (out["error"] + "; " + msg) if out.get("error") else msg

    root_txt = lookup(domain, "TXT", resolver)
    transport_guard(root_txt, domain + " TXT")
    out["spf"] = spf_facts(root_txt["records"])

    dmarc_txt = lookup("_dmarc." + domain, "TXT", resolver)
    transport_guard(dmarc_txt, "_dmarc." + domain + " TXT")
    dmarc_records = [r for r in dmarc_txt["records"] if r.lower().startswith("v=dmarc1")]
    dmarc = {"present": bool(dmarc_records), "records": dmarc_records}
    if dmarc_records:
        tags = parse_tags(dmarc_records[0])
        dmarc["policy"] = tags.get("p")
        dmarc["subdomain_policy"] = tags.get("sp")
        dmarc["rua"] = tags.get("rua")
        dmarc["adkim"] = tags.get("adkim", "r")
        dmarc["aspf"] = tags.get("aspf", "r")
    out["dmarc"] = dmarc

    bimi_txt = lookup("default._bimi." + domain, "TXT", resolver)
    transport_guard(bimi_txt, "default._bimi." + domain + " TXT")
    bimi_records = [r for r in bimi_txt["records"] if r.lower().startswith("v=bimi1")]
    out["bimi"] = {"present": bool(bimi_records), "records": bimi_records}

    mx = lookup(domain, "MX", resolver)
    transport_guard(mx, domain + " MX")
    out["mx"] = {"present": bool(mx["records"]), "records": mx["records"]}

    checked = list(dict.fromkeys((selectors or []) + DEFAULT_DKIM_SELECTORS))
    found = {}
    for sel in checked:
        rec = lookup("%s._domainkey.%s" % (sel, domain), "TXT", resolver)
        transport_guard(rec, "%s._domainkey.%s TXT" % (sel, domain))
        hits = [r for r in rec["records"] if "p=" in r]
        if hits:
            found[sel] = hits[0][:120] + ("…" if len(hits[0]) > 120 else "")
    out["dkim"] = {
        "found_selectors": found,
        "checked_selectors": checked,
        "note": "absence among checked selectors is not proof DKIM is missing",
    }
    return out


def build_parser():
    p = argparse.ArgumentParser(
        prog="doh.py",
        description="Keyless DNS-over-HTTPS lookups; `auth` pulls a sending "
                    "domain's SPF/DMARC/BIMI/MX records and probes common "
                    "DKIM selectors (facts only — no verdicts).",
        epilog="Example: python3 doh.py auth example.com --selector mycustomsel",
    )
    p.add_argument("--resolver", default="google", choices=sorted(RESOLVERS),
                   help="DoH resolver (auto-falls back to the other on failure).")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("query", help="One DNS lookup.")
    s.add_argument("name", help="Record name, e.g. _dmarc.example.com")
    s.add_argument("--type", default="TXT", dest="rtype",
                   choices=sorted(RECORD_TYPES))

    s = sub.add_parser("auth", help="Email-auth record set for a domain.")
    s.add_argument("domain", help="Sending domain, e.g. example.com")
    s.add_argument("--selector", default=None,
                   help="Comma-separated DKIM selector(s) to probe first "
                        "(your ESP's docs name them).")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.command == "query":
        result = lookup(args.name, args.rtype, args.resolver)
    else:
        selectors = [s.strip() for s in (args.selector or "").split(",") if s.strip()]
        result = auth_check(args.domain, selectors, args.resolver)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if isinstance(result, dict) and result.get("error"):
        print("error: %s" % result["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
