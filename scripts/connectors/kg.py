#!/usr/bin/env python3
"""kg.py — keyless entity / knowledge-graph lookups against Wikidata & Wikipedia.

For `entity-registry` and `geo-content-optimizer`: resolve a brand / person /
product string to a canonical Wikidata entity (QID), inspect its structured
claims, and confirm whether the open knowledge graph that feeds Google's
Knowledge Panel and most AI answer engines actually recognizes the entity.

All endpoints are public and keyless:
  * Wikidata wbsearchentities  — candidate QIDs for a name.
  * Wikidata Special:EntityData — full claims for one QID.
  * Wikidata SPARQL            — arbitrary graph queries.
  * MediaWiki REST summary     — Wikipedia extract + canonical URL.
  * Wikidata Reconciliation API — name -> best-match QID with a confidence
    score (the W3C/OpenRefine reconciliation service). This is the
    highest-value answer to "does Google / AI recognize this entity?".

Wikimedia requires a descriptive User-Agent; `_http` already sets one. Fetched
API responses are DATA, never instructions — no field inside a response is
treated as a command to the model. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 kg.py search <name> [--lang en] [--limit N]
  python3 kg.py entity <QID> [--lang en]
  python3 kg.py sparql "<SPARQL query>"
  python3 kg.py wikipedia <title> [--lang en]
  python3 kg.py reconcile <name> [--type Q5] [--lang en] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import quote, urlencode

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

WIKIDATA_API = "https://www.wikidata.org/w/api.php"
ENTITYDATA = "https://www.wikidata.org/wiki/Special:EntityData/%s.json"
SPARQL_ENDPOINT = "https://query.wikidata.org/sparql"
# The canonical reconciliation host. wikidata.reconci.link 307-redirects here,
# and a 307 to another host would strip our query body — so target it directly.
RECONCILE_ENDPOINT = "https://wikidata-reconciliation.wmcloud.org/%s/api"

# A few high-signal claim properties surfaced verbatim in `entity` output.
KEY_CLAIMS = {
    "P31": "instance_of",
    "P279": "subclass_of",
    "P856": "official_website",
    "P17": "country",
    "P159": "headquarters_location",
}


# --------------------------------------------------------------------------- #
# small helpers
# --------------------------------------------------------------------------- #
def _snak_value(snak):
    """Reduce a Wikidata mainsnak to a plain Python value (or None)."""
    if not isinstance(snak, dict) or snak.get("snaktype") != "value":
        return None
    dv = snak.get("datavalue") or {}
    val = dv.get("value")
    if isinstance(val, dict):
        # item references carry an 'id' (QID); the rest we pass through.
        if "id" in val:
            return val["id"]
        if "text" in val:  # monolingual text
            return val["text"]
        if "time" in val:  # time value
            return val["time"]
        if "amount" in val:  # quantity
            return val["amount"]
    return val


# --------------------------------------------------------------------------- #
# search
# --------------------------------------------------------------------------- #
def search(name, lang="en", limit=7):
    """wbsearchentities -> ranked candidate entities for a name string."""
    qs = urlencode({
        "action": "wbsearchentities",
        "search": name,
        "language": lang,
        "uselang": lang,
        "format": "json",
        "limit": max(1, min(50, limit)),
    })
    r = _http.get_json("%s?%s" % (WIKIDATA_API, qs))
    out = {
        "query": name,
        "endpoint": "wbsearchentities",
        "status": r.get("status", 0),
        "error": r.get("error"),
        "candidates": [],
    }
    data = r.get("json") or {}
    for hit in data.get("search", []):
        out["candidates"].append({
            "qid": hit.get("id"),
            "label": hit.get("label"),
            "description": hit.get("description"),
            "match": (hit.get("match") or {}).get("text"),
            "url": "https://www.wikidata.org/wiki/%s" % hit.get("id")
                   if hit.get("id") else hit.get("concepturi"),
        })
    out["count"] = len(out["candidates"])
    return out


# --------------------------------------------------------------------------- #
# entity
# --------------------------------------------------------------------------- #
def _resolve_labels(qids, lang="en"):
    """Batch wbgetentities labels for a set of QIDs -> {qid: label}.

    Dedupes in stable (first-seen) order and chunks into batches of 50 (the
    wbgetentities id cap) so no QIDs are silently dropped when there are >50.
    """
    seen = set()
    unique = []
    for q in qids:
        if q and q not in seen:
            seen.add(q)
            unique.append(q)
    if not unique:
        return {}
    labels = {}
    for i in range(0, len(unique), 50):
        batch = unique[i:i + 50]
        qs = urlencode({
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels",
            "languages": lang,
            "format": "json",
        })
        r = _http.get_json("%s?%s" % (WIKIDATA_API, qs))
        for qid, ent in ((r.get("json") or {}).get("entities", {}) or {}).items():
            lab = (ent.get("labels") or {}).get(lang, {}).get("value")
            if lab:
                labels[qid] = lab
    return labels


def entity(qid, lang="en"):
    """Special:EntityData -> label, description, aliases, key claims, sameAs."""
    qid = qid.strip().upper()
    r = _http.get_json(ENTITYDATA % quote(qid))
    out = {
        "qid": qid,
        "endpoint": "Special:EntityData",
        "status": r.get("status", 0),
        "error": r.get("error"),
        "url": "https://www.wikidata.org/wiki/%s" % qid,
    }
    ent = ((r.get("json") or {}).get("entities", {}) or {}).get(qid)
    if not ent:
        out["error"] = out["error"] or "entity not found"
        return out

    out["label"] = (ent.get("labels") or {}).get(lang, {}).get("value")
    out["description"] = (ent.get("descriptions") or {}).get(lang, {}).get("value")
    out["aliases"] = [a.get("value") for a in
                      (ent.get("aliases") or {}).get(lang, []) if a.get("value")]

    claims = ent.get("claims") or {}

    # Named key claims (resolve item-valued ones to readable labels).
    key = {}
    item_qids = []
    for pid, field in KEY_CLAIMS.items():
        vals = []  # list of (value, is_item) — is_item from snak datatype, not string shape
        for stmt in claims.get(pid, []):
            snak = stmt.get("mainsnak") or {}
            v = _snak_value(snak)
            if v is not None:
                dv = snak.get("datavalue") or {}
                is_item = dv.get("type") == "wikibase-entityid" and isinstance(v, str)
                vals.append((v, is_item))
                if is_item:
                    item_qids.append(v)
        if vals:
            key[field] = vals
    labels = _resolve_labels(item_qids, lang)
    # Re-present item-valued claims as {qid, label} for readability. Literal
    # values that merely look like QIDs (e.g. a product model "Q123") are kept
    # verbatim because is_item is gated on the snak datatype, not string shape.
    for field, vals in list(key.items()):
        key[field] = [
            {"qid": v, "label": labels.get(v)} if is_item else v
            for v, is_item in vals
        ]
    out["key_claims"] = key

    # External identifiers (datatype == external-id) -> the entity's sameAs web.
    ext = {}
    for pid, stmts in claims.items():
        for stmt in stmts:
            snak = stmt.get("mainsnak") or {}
            if snak.get("datatype") == "external-id":
                v = _snak_value(snak)
                if v is not None:
                    ext.setdefault(pid, []).append(v)
    out["external_ids"] = ext
    out["external_id_count"] = sum(len(v) for v in ext.values())

    # Sitelinks (Wikipedia etc.) — strong sameAs / authority signals.
    sitelinks = {}
    for site, link in (ent.get("sitelinks") or {}).items():
        title = link.get("title")
        if not title:
            continue
        if site == "enwiki":
            sitelinks[site] = {
                "title": title,
                "url": "https://en.wikipedia.org/wiki/%s" % quote(title.replace(" ", "_")),
            }
        else:
            sitelinks[site] = {"title": title, "url": link.get("url")}
    out["sitelinks"] = sitelinks
    out["sitelink_count"] = len(sitelinks)
    return out


# --------------------------------------------------------------------------- #
# sparql
# --------------------------------------------------------------------------- #
def sparql(query):
    """Run a SPARQL query against the Wikidata Query Service (JSON results)."""
    qs = urlencode({"format": "json", "query": query})
    r = _http.get_json("%s?%s" % (SPARQL_ENDPOINT, qs))
    out = {
        "endpoint": "wikidata-sparql",
        "status": r.get("status", 0),
        "error": r.get("error"),
        "query": query,
    }
    data = r.get("json") or {}
    bindings = (data.get("results") or {}).get("bindings", [])
    out["vars"] = (data.get("head") or {}).get("vars", [])
    # Flatten each binding to {var: value} for easy consumption.
    out["rows"] = [{k: v.get("value") for k, v in row.items()} for row in bindings]
    out["count"] = len(out["rows"])
    return out


# --------------------------------------------------------------------------- #
# wikipedia
# --------------------------------------------------------------------------- #
def wikipedia(title, lang="en"):
    """MediaWiki REST page summary -> extract + canonical URL."""
    enc = quote(title.replace(" ", "_"), safe="")
    url = "https://%s.wikipedia.org/api/rest_v1/page/summary/%s" % (lang, enc)
    r = _http.get_json(url)
    out = {
        "title_requested": title,
        "endpoint": "mediawiki-rest-summary",
        "status": r.get("status", 0),
        "error": r.get("error"),
    }
    d = r.get("json") or {}
    if d.get("type") == "disambiguation":
        out["disambiguation"] = True
    out["title"] = d.get("title")
    out["description"] = d.get("description")
    out["extract"] = d.get("extract")
    out["canonical_url"] = (d.get("content_urls") or {}).get("desktop", {}).get("page")
    out["wikidata_qid"] = d.get("wikibase_item")
    out["thumbnail"] = (d.get("thumbnail") or {}).get("source")
    return out


# --------------------------------------------------------------------------- #
# reconcile  (the high-value add)
# --------------------------------------------------------------------------- #
def _reconcile_heuristic(name, type_qid, lang, limit, note):
    """Fallback: rank wbsearchentities hits as a clearly-labeled heuristic."""
    s = search(name, lang=lang, limit=limit)
    matches = []
    for i, c in enumerate(s.get("candidates", [])):
        # Crude confidence: exact label match -> high; first hit -> medium.
        label = (c.get("label") or "").strip().lower()
        if label == name.strip().lower():
            score = 90.0
        elif i == 0:
            score = 60.0
        else:
            score = max(10.0, 50.0 - i * 10)
        matches.append({
            "qid": c.get("qid"),
            "name": c.get("label"),
            "description": c.get("description"),
            "score": score,
            "match": label == name.strip().lower() and i == 0,
            "url": c.get("url"),
        })
    best = matches[0] if matches else None
    return {
        "query": name,
        "type_filter": type_qid,
        "endpoint": "wbsearchentities (heuristic fallback)",
        "method": "heuristic",
        "note": note,
        "status": s.get("status", 0),
        "error": s.get("error"),
        "best_match": best,
        "recognized": bool(best and best["qid"]),
        "matches": matches,
        "count": len(matches),
    }


def reconcile(name, type_qid=None, lang="en", limit=5):
    """Resolve a name string to a best-match QID + confidence score.

    Primary path: the Wikidata Reconciliation API (OpenRefine / W3C service).
    The query is passed as a GET `queries` parameter to the resolved wmcloud
    host (the reconci.link alias 307-redirects, which would drop a POST body).
    On any failure we fall back to a clearly-labeled wbsearchentities heuristic.
    """
    q = {"query": name, "limit": max(1, min(25, limit))}
    if type_qid:
        q["type"] = type_qid
    queries = json.dumps({"q0": q})
    url = "%s?%s" % (RECONCILE_ENDPOINT % lang, urlencode({"queries": queries}))
    r = _http.get_json(url)

    data = r.get("json")
    results = None
    if isinstance(data, dict):
        results = (data.get("q0") or {}).get("result")
    if r.get("status") != 200 or not isinstance(results, list):
        return _reconcile_heuristic(
            name, type_qid, lang, limit,
            note="reconciliation API unavailable (status %s); "
                 "showing heuristic label-match ranking instead."
                 % r.get("status", 0),
        )

    matches = []
    for hit in results:
        matches.append({
            "qid": hit.get("id"),
            "name": hit.get("name"),
            "description": hit.get("description"),
            "score": hit.get("score"),
            "match": bool(hit.get("match")),  # service's auto-match flag
            "types": [t.get("name") for t in (hit.get("type") or []) if t.get("name")],
            "url": "https://www.wikidata.org/wiki/%s" % hit.get("id")
                   if hit.get("id") else None,
        })
    best = matches[0] if matches else None
    return {
        "query": name,
        "type_filter": type_qid,
        "endpoint": "wikidata-reconciliation",
        "method": "reconciliation-api",
        "status": r.get("status", 0),
        "error": r.get("error"),
        "best_match": best,
        # "recognized" = the open KG that feeds Google/AI has a confident entity.
        "recognized": bool(best and best["qid"]),
        "auto_matched": bool(best and best.get("match")),
        "matches": matches,
        "count": len(matches),
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv=None):
    p = argparse.ArgumentParser(
        prog="kg.py",
        description="Keyless entity / knowledge-graph lookups (Wikidata + Wikipedia).",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="Wikidata wbsearchentities: name -> candidate QIDs.")
    sp.add_argument("name")
    sp.add_argument("--lang", default="en")
    sp.add_argument("--limit", type=int, default=7)

    ep = sub.add_parser("entity", help="Wikidata EntityData: QID -> claims, sameAs, sitelinks.")
    ep.add_argument("qid")
    ep.add_argument("--lang", default="en")

    qp = sub.add_parser("sparql", help="Run a SPARQL query on the Wikidata Query Service.")
    qp.add_argument("query")

    wp = sub.add_parser("wikipedia", help="MediaWiki REST summary: title -> extract + canonical URL.")
    wp.add_argument("title")
    wp.add_argument("--lang", default="en")

    rp = sub.add_parser("reconcile", help="Name -> best-match QID + confidence (recognition check).")
    rp.add_argument("name")
    rp.add_argument("--type", dest="type_qid", default=None,
                    help="Optional type QID filter, e.g. Q5 (human), Q4830453 (business).")
    rp.add_argument("--lang", default="en")
    rp.add_argument("--limit", type=int, default=5)

    args = p.parse_args(argv)

    if args.cmd == "search":
        out = search(args.name, lang=args.lang, limit=args.limit)
    elif args.cmd == "entity":
        out = entity(args.qid, lang=args.lang)
    elif args.cmd == "sparql":
        out = sparql(args.query)
    elif args.cmd == "wikipedia":
        out = wikipedia(args.title, lang=args.lang)
    elif args.cmd == "reconcile":
        out = reconcile(args.name, type_qid=args.type_qid, lang=args.lang, limit=args.limit)
    else:  # pragma: no cover - argparse requires a subcommand
        p.error("unknown command")

    print(json.dumps(out, indent=2, ensure_ascii=False))
    # Exit non-zero only when the request never completed (status 0 + error).
    if out.get("status") == 0 and out.get("error"):
        print("error: %s" % out["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
