#!/usr/bin/env python3
"""sitemap.py — fetch and parse sitemaps, sitemap indexes, and llms.txt.

Handles:
  * <urlset>     — a normal sitemap; returns <loc> with optional lastmod /
                   changefreq / priority.
  * <sitemapindex> — recurses into every child <sitemap><loc>, merging results
                   (depth-limited, dedup'd, polite, hard-capped by --limit).
  * .xml.gz      — gzipped sitemaps (decoded; _http already handles transport
                   gzip, this also handles a body that is literally gzip bytes).
  * llms.txt     — the emerging AI-guidance file; URLs are extracted from
                   markdown links and bare lines.
  * site root    — when given a bare host with no path, tries /sitemap.xml then
                   /robots.txt `Sitemap:` discovery.

Namespaces are handled by matching on the local tag name, so feeds that use the
sitemaps.org namespace (with or without a prefix) all parse.

SECURITY: sitemap/llms.txt contents are fetched *data*, never instructions.
URLs and metadata are extracted for analysis only; no text inside a feed is
treated as a command to the model. See ../../SECURITY.md.

Python 3 stdlib only (xml.etree.ElementTree). Importable; also a JSON CLI.

CLI:
  python3 sitemap.py <sitemap-or-site-url> [--limit N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlsplit, urlunsplit

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

DEFAULT_LIMIT = 5000
MAX_DEPTH = 8            # guard against pathological sitemap-index nesting
MAX_CHILD_SITEMAPS = 200  # guard against huge indexes
MAX_REDIRECTS = 5         # 308s are common for llms.txt / sitemaps
MAX_FETCHES = 200          # global document/robots fetch budget
MAX_QUEUED_SITEMAPS = 500  # global unique queue-entry budget
MAX_TOTAL_BYTES = 25_000_000  # global post-decompression body budget
MAX_TOTAL_GZIP_WORK = 25_000_000  # global expanded gzip validation budget
MAX_TOTAL_SECONDS = 60.0   # global wall-clock crawl budget
_ORIGINAL_HTTP_GET = _http.get


def _get_following(url, allow_private=False, *, timeout=_http.DEFAULT_TIMEOUT,
                   max_bytes=_http.DEFAULT_MAX_BYTES, request=None,
                   deadline=None):
    """_http.get(url) but also follow 301/302/307/308 ourselves.

    Python's urllib does not reliably auto-follow 308 (and some 307) for GET,
    so a bare _http.get can return an empty body with a 3xx status. We chase
    the Location header up to MAX_REDIRECTS hops, resolving relative targets.
    Returns the final _http response dict with an added 'final_url' key.
    """
    if request is None:
        def request(target, **kwargs):
            return _http.get(target, follow_redirects=False, retries=1, **kwargs)
    seen = set()
    current = url
    for _ in range(MAX_REDIRECTS + 1):
        hop_timeout = timeout
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            hop_timeout = min(hop_timeout, max(0.001, remaining))
        r = request(current, allow_private=allow_private, timeout=hop_timeout,
                    max_bytes=max_bytes)
        if r is None:
            return None
        status = r.get("status", 0)
        transport_url = r.get("url") or current
        if transport_url != current:
            # The child already pinned/validated the endpoint it actually
            # contacted. Keep this parent-side check non-resolving so a hostile
            # resolver cannot escape the wall-clock boundary.
            transport_error = _http.redirect_safety_error(
                current,
                transport_url,
                allow_private=allow_private,
                resolve_target=False,
            )
            if transport_error:
                r["status"] = 0
                r["error"] = "blocked transport final URL: %s" % transport_error
                r["final_url"] = current
                return r
        if status in (301, 302, 303, 307, 308) and not r.get("body"):
            loc = None
            for k, v in (r.get("headers") or {}).items():
                if k.lower() == "location":
                    loc = v
                    break
            if not loc:
                r["final_url"] = transport_url
                return r
            nxt = urljoin(transport_url, loc.strip())
            # Validate syntax/credentials/downgrade now. The next request_hop
            # resolves and validates every A/AAAA answer inside the terminable
            # child before opening a socket.
            safety_error = _http.redirect_safety_error(
                transport_url,
                nxt,
                allow_private=allow_private,
                resolve_target=False,
            )
            if safety_error:
                r["status"] = 0
                r["error"] = "blocked redirect: %s" % safety_error
                r["final_url"] = transport_url
                return r
            if nxt in seen or nxt == current:
                r["final_url"] = transport_url
                return r
            seen.add(current)
            current = nxt
            continue
        # _http normally follows redirects itself.  Its response URL is the
        # authoritative transport endpoint; do not overwrite it with the
        # originally requested URL when classifying .gz or llms.txt content.
        r["final_url"] = transport_url
        return r
    r["status"] = 0
    r["error"] = "maximum redirect hops exceeded"
    r["final_url"] = r.get("url") or current
    return r


def _localname(tag):
    """Strip an XML namespace, e.g. '{ns}url' -> 'url'."""
    return tag.rsplit("}", 1)[-1].lower() if "}" in tag else tag.lower()


def _maybe_gunzip(body, url, max_bytes=_http.DEFAULT_MAX_BYTES,
                   max_validation_bytes=_http.DEFAULT_MAX_GZIP_VALIDATION_BYTES):
    """Return ``(body, truncated, error, expanded_work)`` for literal gzip."""
    if not body:
        return body, False, None, 0
    # Content-Encoding gzip has already been decoded by _http even when the URL
    # still ends in .gz. Only the magic bytes prove a second, literal gzip layer
    # remains; suffix-only detection would double-decode transport gzip.
    if body[:2] == b"\x1f\x8b":
        return _http.decompress_gzip(
            body,
            max_bytes,
            max_validation_bytes=max_validation_bytes,
            return_work=True,
        )
    return body, False, None, 0


def _normalize_input_url(arg):
    """Add an https scheme when missing; return (full_url, has_explicit_path)."""
    raw = arg.strip()
    if "://" not in raw:
        raw = "https://" + raw
    parts = urlsplit(raw)
    has_path = bool(parts.path.strip("/"))
    return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, "")), has_path


# ---- llms.txt -------------------------------------------------------------
_MD_LINK = re.compile(r"\[[^\]]*\]\((https?://[^)\s]+)\)")
_BARE_URL = re.compile(r"(?<![\w(])https?://[^\s<>\")]+")


def _parse_llms_txt(text):
    """Extract URLs from an llms.txt: markdown links first, then bare URLs."""
    seen = []
    seen_set = set()
    for m in _MD_LINK.finditer(text):
        u = m.group(1).rstrip(".,);")
        if u not in seen_set:
            seen_set.add(u)
            seen.append(u)
    for m in _BARE_URL.finditer(text):
        u = m.group(0).rstrip(".,);")
        if u not in seen_set:
            seen_set.add(u)
            seen.append(u)
    return seen


# ---- XML sitemap ----------------------------------------------------------
def _parse_xml(body):
    """Parse sitemap XML bytes. Returns (kind, items) or ('error', msg).

    kind is 'urlset', 'index', or 'error'. For 'urlset', items is a list of
    dicts {loc, lastmod?, changefreq?, priority?}. For 'index', items is a list
    of child sitemap loc strings.
    """
    try:
        root = ET.fromstring(body)
    except ET.ParseError as e:
        return "error", "XML parse error: %s" % e
    rootname = _localname(root.tag)
    if rootname == "sitemapindex":
        locs = []
        for sm in root:
            if _localname(sm.tag) != "sitemap":
                continue
            for child in sm:
                if _localname(child.tag) == "loc" and (child.text or "").strip():
                    locs.append(child.text.strip())
        return "index", locs
    if rootname == "urlset":
        items = []
        for url in root:
            if _localname(url.tag) != "url":
                continue
            entry = {}
            for child in url:
                name = _localname(child.tag)
                val = (child.text or "").strip()
                if not val:
                    continue
                if name == "loc":
                    entry["loc"] = val
                elif name in ("lastmod", "changefreq", "priority"):
                    entry[name] = val
            if entry.get("loc"):
                items.append(entry)
        return "urlset", items
    # Some feeds wrap content unexpectedly; try to scavenge <loc> values.
    locs = [(_localname(e.tag), (e.text or "").strip())
            for e in root.iter() if _localname(e.tag) == "loc"]
    scavenged = [v for _, v in locs if v]
    if scavenged:
        return "urlset", [{"loc": v} for v in scavenged]
    return "error", "unrecognized root element <%s>" % rootname


# ---- crawl orchestration --------------------------------------------------
def _robots_sitemaps(text, robots_url):
    """Extract and resolve Sitemap directives from robots.txt text."""
    out = []
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, _, value = line.partition(":")
        if field.strip().lower() == "sitemap" and value.strip():
            out.append(urljoin(robots_url, value.strip()))
    return out


def _discover_from_robots(base_url):
    """Return Sitemap: URLs declared in the site's robots.txt (best-effort)."""
    parts = urlsplit(base_url)
    robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    r = _http.get_text(robots_url)
    return _robots_sitemaps(r.get("text") or "", robots_url), robots_url


def collect(start_url, limit=DEFAULT_LIMIT, *, max_fetches=MAX_FETCHES,
            max_queue=MAX_QUEUED_SITEMAPS, max_total_bytes=MAX_TOTAL_BYTES,
            max_gzip_work=MAX_TOTAL_GZIP_WORK,
            max_seconds=MAX_TOTAL_SECONDS):
    """Fetch `start_url` and gather URLs, recursing into sitemap indexes.

    Returns a result dict (JSON-serializable). Never raises for HTTP/parse
    issues — they are recorded under `sources` and `errors`.  All nested work
    shares hard fetch, queue, post-decompression byte, and wall-clock budgets;
    per-call values may lower but never raise the module security ceilings.
    """
    max_fetches = min(MAX_FETCHES, max(1, int(max_fetches)))
    max_queue = min(MAX_QUEUED_SITEMAPS, max(1, int(max_queue)))
    max_total_bytes = min(MAX_TOTAL_BYTES, max(1, int(max_total_bytes)))
    max_gzip_work = min(MAX_TOTAL_GZIP_WORK, max(1, int(max_gzip_work)))
    max_seconds = min(MAX_TOTAL_SECONDS, max(0.001, float(max_seconds)))
    started = time.monotonic()
    full_url, has_path = _normalize_input_url(start_url)
    deadline = started + max_seconds
    result = {
        "input": start_url,
        "resolved_url": full_url,
        "type": None,
        "url_count": 0,
        "limit": limit,
        "truncated": False,
        "urls": [],
        "child_sitemaps_fetched": 0,
        "sources": [],
        "errors": [],
        "budget": {
            "max_fetches": max_fetches,
            "max_queue": max_queue,
            "max_total_bytes": max_total_bytes,
            "max_gzip_work": max_gzip_work,
            "max_seconds": max_seconds,
            "fetches_used": 0,
            "queue_entries_used": 0,
            "bytes_used": 0,
            "gzip_work_used": 0,
            "elapsed_seconds": 0.0,
        },
    }

    queue = []          # list of (url, depth)
    visited = set()
    enqueued = set()
    seen_locs = set()
    budget_errors = set()

    def budget_error(kind, url=None):
        """Record one deterministic error per exhausted global budget."""
        if kind in budget_errors:
            return
        budget_errors.add(kind)
        message = "global %s budget exhausted" % kind
        entry = {"error": message}
        if url:
            entry["url"] = url
        result["errors"].append(entry)
        result["truncated"] = True

    def enqueue(url, depth):
        if url in enqueued or url in visited:
            return True
        if len(enqueued) >= max_queue:
            budget_error("queue", url)
            return False
        enqueued.add(url)
        queue.append((url, depth))
        result["budget"]["queue_entries_used"] = len(enqueued)
        return True

    def request_hop(url, **kwargs):
        """Perform one real HTTP hop under the shared fetch/deadline budget."""
        remaining_time = deadline - time.monotonic()
        if remaining_time <= 0:
            budget_error("time", url)
            return None
        if result["budget"]["fetches_used"] >= max_fetches:
            budget_error("fetch", url)
            return None
        if result["budget"]["bytes_used"] >= max_total_bytes:
            budget_error("byte", url)
            return None
        remaining_work = max_gzip_work - result["budget"]["gzip_work_used"]
        if remaining_work <= 0:
            budget_error("gzip work", url)
            return None
        result["budget"]["fetches_used"] += 1
        request_kwargs = {
            "url": url,
            "allow_private": kwargs.get("allow_private", False),
            "timeout": min(kwargs.get("timeout", _http.DEFAULT_TIMEOUT),
                           max(0.001, remaining_time)),
            "max_bytes": kwargs.get("max_bytes", _http.DEFAULT_MAX_BYTES),
            "retries": 1,
            "follow_redirects": False,
            "max_gzip_validation_bytes": remaining_work,
        }
        # Tests and embedding hosts may intentionally inject a transport by
        # replacing _http.get. The shipped transport uses an isolated process;
        # the injected callable remains directly observable to its owner.
        if _http.get is not _ORIGINAL_HTTP_GET:
            return _http.get(**request_kwargs)
        response = _http.get_hard_deadline(deadline=deadline, **request_kwargs)
        if response.get("deadline_exceeded"):
            budget_error("time", url)
            return None
        return response

    def fetch(url):
        """Perform one budgeted document fetch and decode its body."""
        remaining_bytes = max_total_bytes - result["budget"]["bytes_used"]
        if remaining_bytes <= 0:
            budget_error("byte", url)
            return None
        request_bytes = min(_http.DEFAULT_MAX_BYTES, remaining_bytes)
        response = _get_following(
            url,
            timeout=_http.DEFAULT_TIMEOUT,
            max_bytes=request_bytes,
            request=request_hop,
            deadline=deadline,
        )
        if response is None:
            if time.monotonic() >= deadline:
                budget_error("time", url)
            return None
        final_url = response.get("final_url") or response.get("url") or url
        transport_body = response.get("body") or b""
        transport_gzip_work = max(0, int(response.get("gzip_expanded_bytes", 0)))
        remaining_work = max_gzip_work - result["budget"]["gzip_work_used"]
        charged_transport_work = min(remaining_work, transport_gzip_work)
        result["budget"]["gzip_work_used"] += charged_transport_work
        remaining_work -= charged_transport_work
        if transport_gzip_work > charged_transport_work:
            response["truncated"] = True
            budget_error("gzip work", url)

        transport_error = str(response.get("error") or "")
        if "validation work limit exceeded" in transport_error:
            response["truncated"] = True
            budget_error("gzip work", url)

        if transport_body[:2] == b"\x1f\x8b" and remaining_work <= 0:
            body, gzip_truncated, gzip_error, literal_gzip_work = (
                b"", True,
                "invalid gzip response: validation work limit exceeded", 0,
            )
            budget_error("gzip work", url)
        else:
            body, gzip_truncated, gzip_error, literal_gzip_work = _maybe_gunzip(
                transport_body,
                final_url,
                max_bytes=request_bytes,
                max_validation_bytes=max(1, remaining_work),
            )
        charged_literal_work = min(remaining_work, max(0, literal_gzip_work))
        result["budget"]["gzip_work_used"] += charged_literal_work
        if literal_gzip_work >= remaining_work and gzip_error and "work limit" in gzip_error:
            gzip_truncated = True
            budget_error("gzip work", url)
        response["body"] = body
        response["truncated"] = bool(response.get("truncated") or gzip_truncated)
        if gzip_error:
            response["error"] = response.get("error") or gzip_error
        # Charge the larger of transport bytes and retained decoded bytes. This
        # bounds invalid/compressed responses as well as expanded sitemap data
        # without double-counting the same payload representation.
        charged_bytes = max(
            int(response.get("transport_bytes", len(transport_body))),
            len(body),
        )
        result["budget"]["bytes_used"] += charged_bytes
        if response.get("truncated"):
            result["truncated"] = True
            # A response may be truncated solely because the independent gzip
            # validation-work budget was exhausted. Attribute byte exhaustion
            # only when this document actually consumed the remaining byte
            # allowance; request_bytes is merely a cap and may equal the
            # allowance even when very few bytes were charged.
            if charged_bytes >= remaining_bytes:
                budget_error("byte", url)
        if time.monotonic() >= deadline:
            budget_error("time", url)
            return None
        return response

    # ---- entry-point resolution ---------------------------------------
    if not has_path:
        # Bare host: try /sitemap.xml, then robots.txt Sitemap: discovery.
        parts = urlsplit(full_url)
        guess = urlunsplit((parts.scheme, parts.netloc, "/sitemap.xml", "", ""))
        enqueue(guess, 0)
        robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
        robots_response = fetch(robots_url)
        sm_urls = []
        if robots_response is not None:
            robots_body = robots_response.get("body") or b""
            sm_urls = _robots_sitemaps(
                robots_body.decode("utf-8", "replace"),
                robots_response.get("final_url") or robots_url,
            )
        result["sources"].append({"discovery": "robots.txt", "url": robots_url,
                                   "found": sm_urls})
        for u in sm_urls:
            if not enqueue(u, 0):
                break
    elif urlsplit(full_url).path.rstrip("/").lower().endswith("llms.txt"):
        enqueue(full_url, 0)
    else:
        enqueue(full_url, 0)

    while queue:
        if len(result["urls"]) >= limit:
            result["truncated"] = True
            break
        url, depth = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        r = fetch(url)
        if r is None:
            break
        status = r.get("status", 0)
        final_url = r.get("final_url") or r.get("url") or url
        visited.add(final_url)
        src = {"url": url, "status": status, "depth": depth}
        if final_url != url:
            src["final_url"] = final_url
        # Classify by the post-redirect URL so a 308 to a .gz / llms.txt still
        # routes correctly.
        is_llms = urlsplit(final_url).path.rstrip("/").lower().endswith("llms.txt")
        if status != 200 or not r.get("body"):
            src["note"] = r.get("error") or ("HTTP %s" % status)
            result["sources"].append(src)
            if r.get("error"):
                result["errors"].append({"url": url, "error": r["error"]})
            continue

        body = r["body"]

        if is_llms:
            text = body.decode("utf-8", "replace")
            found = _parse_llms_txt(text)
            src["kind"] = "llms.txt"
            src["found"] = len(found)
            result["sources"].append(src)
            if result["type"] is None:
                result["type"] = "llms.txt"
            for loc in found:
                if loc in seen_locs:
                    continue
                seen_locs.add(loc)
                result["urls"].append({"loc": loc})
                if len(result["urls"]) >= limit:
                    result["truncated"] = True
                    break
            continue

        kind, items = _parse_xml(body)
        src["kind"] = kind
        if kind == "error":
            src["note"] = items
            result["sources"].append(src)
            result["errors"].append({"url": url, "error": items})
            continue

        if kind == "index":
            resolved_children = [urljoin(final_url, c) for c in items]
            child = [c for c in resolved_children if c not in visited]
            if len(child) > MAX_CHILD_SITEMAPS:
                child = child[:MAX_CHILD_SITEMAPS]
                result["truncated"] = True
                result["errors"].append({
                    "url": url,
                    "error": "per-index child sitemap limit reached",
                })
            src["children"] = len(child)
            result["sources"].append(src)
            if result["type"] is None:
                result["type"] = "sitemapindex"
            if depth < MAX_DEPTH:
                for c in child:
                    if not enqueue(c, depth + 1):
                        break
            else:
                result["errors"].append({"url": url,
                                         "error": "max sitemap depth reached"})
            continue

        # kind == "urlset"
        if depth > 0:
            result["child_sitemaps_fetched"] += 1
        src["found"] = len(items)
        result["sources"].append(src)
        if result["type"] is None:
            result["type"] = "sitemap"
        elif result["type"] == "sitemapindex":
            pass  # keep top-level type as index
        for entry in items:
            loc = entry["loc"]
            if loc in seen_locs:
                continue
            seen_locs.add(loc)
            result["urls"].append(entry)
            if len(result["urls"]) >= limit:
                result["truncated"] = True
                break

    result["url_count"] = len(result["urls"])
    if result["type"] is None:
        result["type"] = "unknown"
    result["budget"]["elapsed_seconds"] = round(time.monotonic() - started, 6)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="sitemap.py",
        description="Fetch + parse sitemap.xml / sitemap-index (recursive) / "
                    ".xml.gz / llms.txt; emit URLs with lastmod & changefreq.",
    )
    p.add_argument("target", metavar="sitemap-or-site-url",
                   help="A sitemap URL, llms.txt URL, or a bare site root "
                        "(https assumed; root triggers /sitemap.xml + robots "
                        "Sitemap: discovery).")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                   help="Hard cap on total URLs returned (default %d)." % DEFAULT_LIMIT)
    args = p.parse_args(argv)

    limit = args.limit if args.limit and args.limit > 0 else DEFAULT_LIMIT
    result = collect(args.target, limit=limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # Exit non-zero only when nothing was retrieved at all (no URLs and every
    # source failed). A partial parse with some URLs is a success.
    if result["url_count"] == 0 and (result["errors"] or not result["sources"]):
        any_ok = any(s.get("status") == 200 for s in result["sources"])
        if not any_ok:
            print("error: no sitemap URLs retrieved", file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
