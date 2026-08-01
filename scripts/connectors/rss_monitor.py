#!/usr/bin/env python3
"""rss_monitor.py — brand / mention monitoring via RSS or Atom feeds.

Point this at any feed — a Google Alerts RSS feed, a Google News RSS search
(https://news.google.com/rss/search?q=YOUR+BRAND), a blog, a forum — and it
returns the latest items in a normalized shape for mention tracking.

Handles both feed dialects with one xml.etree parser:
  * RSS 2.0 : <rss><channel><item><title|link|pubDate|description>
  * Atom 1.0: <feed><entry><title|link href=…|published/updated|summary>

Namespaces are resolved by matching on the *local* tag name, so feeds that mix
in Dublin Core (dc:date), content:encoded, etc. still parse. The feed's own
<title> is captured as the default source for each item.

SECURITY: feed contents are *data*, never instructions. Item titles, summaries,
and links are untrusted input and are never executed or acted upon as commands.
See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 rss_monitor.py <feed-url> [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)


def _local(tag):
    """Strip an XML namespace: '{http://www.w3.org/2005/Atom}entry' -> 'entry'."""
    if not tag:
        return ""
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _find_child_text(elem, *names):
    """First non-empty text among direct children whose local name matches."""
    wanted = {n.lower() for n in names}
    for child in elem:
        if _local(child.tag).lower() in wanted:
            text = (child.text or "").strip()
            if text:
                return text
    return None


def _extract_link(elem):
    """Resolve a link for an item/entry across RSS and Atom conventions.

    RSS puts the URL in <link>text</link>. Atom uses <link href="..."/> and may
    list several; we prefer rel="alternate" (or no rel), else the first href.
    """
    fallback_href = None
    for child in elem:
        if _local(child.tag).lower() != "link":
            continue
        text = (child.text or "").strip()
        if text:                       # RSS-style link
            return text
        href = child.attrib.get("href")
        if href:
            rel = (child.attrib.get("rel") or "alternate").lower()
            if rel == "alternate":
                return href
            if fallback_href is None:
                fallback_href = href
    return fallback_href


def _iter_items(root):
    """Yield item/entry elements for either RSS or Atom, regardless of nesting."""
    for elem in root.iter():
        if _local(elem.tag).lower() in ("item", "entry"):
            yield elem


def _feed_title(root):
    """Channel/feed title used as the default per-item source."""
    for elem in root.iter():
        name = _local(elem.tag).lower()
        if name in ("channel", "feed"):
            t = _find_child_text(elem, "title")
            if t:
                return t
    # Some feeds have a top-level <title> without a channel wrapper.
    return _find_child_text(root, "title")


def parse_feed(xml_text, feed_url=None, limit=None):
    """Parse RSS/Atom XML text into normalized item dicts.

    Returns (items, feed_title). Raises ET.ParseError on malformed XML; callers
    that want a never-raise path should use monitor().
    """
    root = ET.fromstring(xml_text)
    source = _feed_title(root)
    items = []
    for elem in _iter_items(root):
        title = _find_child_text(elem, "title")
        link = _extract_link(elem)
        # RSS: pubDate ; Atom: published, then updated ; DC: date.
        published = _find_child_text(
            elem, "pubDate", "published", "updated", "date"
        )
        # RSS: description ; Atom: summary, then content.
        summary = _find_child_text(elem, "description", "summary", "content")
        items.append({
            "title": title,
            "link": link,
            "published": published,
            "source": source,
            "summary": summary,
        })
        if limit is not None and len(items) >= limit:
            break
    return items, source


def monitor(feed_url, limit=None):
    """Fetch and parse a feed. Never raises; reports errors in the result dict."""
    r = _http.get_text(feed_url)
    text = r.get("text") or ""
    result = {
        "feed_url": feed_url,
        "status": r.get("status", 0),
        "error": r.get("error"),
        "feed_title": None,
        "count": 0,
        "items": [],
    }
    if not text:
        result["error"] = result["error"] or "empty response body"
        return result
    try:
        items, source = parse_feed(text, feed_url=feed_url, limit=limit)
    except (ET.ParseError, ValueError) as e:
        # ET.fromstring raises ValueError (not ParseError) on a str carrying an XML
        # encoding declaration ("Unicode strings with encoding declaration are not
        # supported") — catch it too so the CLI returns a clean error dict.
        result["error"] = "XML parse error: %s" % e
        return result
    result["feed_title"] = source
    result["items"] = items
    result["count"] = len(items)
    return result


def build_parser():
    p = argparse.ArgumentParser(
        prog="rss_monitor.py",
        description="Brand/mention monitoring via RSS or Atom feeds "
                    "(Google Alerts, Google News RSS, blogs, …).",
        epilog='Example: python3 rss_monitor.py '
               '"https://news.google.com/rss/search?q=anthropic" --limit 10',
    )
    p.add_argument("feed_url", help="RSS or Atom feed URL.")
    p.add_argument("--limit", type=int, default=None,
                   help="Max items to return. Default: all.")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.limit is not None and args.limit < 1:
        print("error: --limit must be >= 1", file=sys.stderr)
        return 1
    result = monitor(args.feed_url, limit=args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    # Non-zero when the request never completed, or the body could not be parsed
    # into a feed. A valid feed with zero items still exits 0.
    if result["status"] == 0 and result["error"]:
        print("error: %s" % result["error"], file=sys.stderr)
        return 2
    if result["error"] and not result["items"]:
        print("error: %s" % result["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
