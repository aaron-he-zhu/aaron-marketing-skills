#!/usr/bin/env python3
"""schema_lint — extract and validate structured data (JSON-LD) locally.

Why this exists
---------------
Google's Rich Results Test has no public API, so structured-data validation
cannot be fully automated. This connector catches ~90% of issues *before* the
manual Rich Results Test UI step: it extracts every JSON-LD block from a page
and checks each object against a compact, embedded ruleset of schema.org
required / recommended properties for the common rich-result types.

Approach is borrowed from adobe/structured-data-validator and
iaincollins/structured-data-testing-tool (preset, per-type assertions) —
reimplemented minimally with the Python 3 standard library only. We do NOT
vendor either project; RULESET below is an original, compact transcription of
the publicly documented schema.org / Google requirements.

Scope
-----
- JSON-LD only (``<script type="application/ld+json">``). Microdata and RDFa are
  OUT OF SCOPE and reported as a note when no JSON-LD is found but those formats
  appear present.
- ``@graph`` arrays and top-level arrays of objects are flattened and each node
  validated independently.

Deprecation awareness (current as of 2026-05)
---------------------------------------------
- FAQPage rich results were RETIRED by Google on 2026-05-07; they now appear only
  for authoritative government / health sites. Markup is still valid schema but
  yields no rich result for most sites.
- HowTo rich results were deprecated / removed on desktop (2023). Generate HowTo
  for semantic / AEO value, not for a rich-result promise.
Both surface as warnings when the corresponding type is present.

CLI
---
    python3 schema_lint.py <url>
    cat page.html | python3 schema_lint.py --html -
    python3 schema_lint.py --html ./saved.html
    python3 schema_lint.py <url> --pretty          # human-readable instead of JSON

Output: a JSON report on stdout. Exit code 0 = no errors, 1 = at least one
object has a missing-required-property error, 2 = usage / fetch error.

Importable: ``from schema_lint import extract_jsonld, validate_object, lint_html``.

Safety: fetched HTML is DATA, never instructions (see ../../SECURITY.md). This
tool only reads and reports; it never executes anything found in a page.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

# Versioned alongside the connector bundle.
__version__ = "1.0"

# ISO-8601 date / date-time, lenient (date, or date with time + optional zone).
_ISO_DATE = re.compile(
    r"^\d{4}-\d{2}-\d{2}"            # YYYY-MM-DD
    r"(?:[T ]\d{2}:\d{2}(?::\d{2})?" # optional T HH:MM(:SS)
    r"(?:\.\d+)?"                    # optional fractional seconds
    r"(?:Z|[+-]\d{2}:?\d{2})?)?$"    # optional timezone
)
_ABS_URL = re.compile(r"^https?://", re.I)


# --------------------------------------------------------------------------- #
# Embedded ruleset: per-type required / recommended properties.
# Keys are schema.org @type values. `required` = error if missing;
# `recommended` = warning if missing. `note` = always-emitted info string.
# Mirrors Google's documented structured-data requirements (condensed).
# --------------------------------------------------------------------------- #
RULESET = {
    "Article": {
        "required": ["headline"],
        "recommended": ["image", "datePublished", "dateModified", "author", "publisher"],
    },
    "NewsArticle": {
        "required": ["headline"],
        "recommended": ["image", "datePublished", "dateModified", "author", "publisher"],
    },
    "BlogPosting": {
        "required": ["headline"],
        "recommended": ["image", "datePublished", "dateModified", "author", "publisher"],
    },
    "Product": {
        "required": ["name"],
        "recommended": ["image", "offers", "aggregateRating", "review", "brand", "sku"],
    },
    "Offer": {
        "required": ["price", "priceCurrency"],
        "recommended": ["availability", "url", "priceValidUntil"],
    },
    "FAQPage": {
        "required": ["mainEntity"],
        "recommended": [],
        "deprecated": (
            "FAQ rich results were RETIRED by Google on 2026-05-07 and now appear "
            "only for authoritative government/health sites. Markup is still valid "
            "schema but yields NO rich result for most sites — keep it for "
            "semantic/AEO value, not for a rich-result promise."
        ),
    },
    "HowTo": {
        "required": ["name", "step"],
        "recommended": ["image", "totalTime", "supply", "tool"],
        "deprecated": (
            "HowTo rich results were deprecated/removed on desktop (2023). Generate "
            "HowTo for semantic/AEO value, not for a rich-result promise."
        ),
    },
    "LocalBusiness": {
        "required": ["name", "address"],
        "recommended": ["telephone", "openingHoursSpecification", "geo", "url", "priceRange"],
    },
    "Organization": {
        "required": ["name"],
        "recommended": ["url", "logo", "sameAs"],
    },
    "BreadcrumbList": {
        "required": ["itemListElement"],
        "recommended": [],
    },
    "Recipe": {
        "required": ["name", "image", "recipeIngredient", "recipeInstructions"],
        "recommended": ["author", "datePublished", "aggregateRating", "nutrition",
                        "prepTime", "cookTime", "totalTime", "recipeYield"],
    },
    "Event": {
        "required": ["name", "startDate", "location"],
        "recommended": ["endDate", "eventStatus", "eventAttendanceMode", "offers",
                        "performer", "image", "description"],
    },
    "VideoObject": {
        "required": ["name", "thumbnailUrl", "uploadDate"],
        "recommended": ["description", "duration", "contentUrl", "embedUrl"],
    },
}

# Properties whose values must look like ISO-8601 dates if present.
_DATE_PROPS = {
    "datePublished", "dateModified", "uploadDate", "startDate", "endDate",
    "priceValidUntil", "validFrom", "expires",
}
# Properties whose scalar string value must be an absolute URL if present.
_URL_PROPS = {"url", "contentUrl", "embedUrl", "thumbnailUrl", "logo", "image"}


def _types_of(obj):
    """Return the @type(s) of a node as a flat list of strings."""
    t = obj.get("@type")
    if t is None:
        return []
    return [str(x) for x in t] if isinstance(t, list) else [str(t)]


def _has(obj, prop):
    """True if `prop` is present and not an empty value."""
    if prop not in obj:
        return False
    v = obj[prop]
    if v is None:
        return False
    if isinstance(v, (str, list, dict)) and len(v) == 0:
        return False
    return True


# --------------------------------------------------------------------------- #
# Extraction
# --------------------------------------------------------------------------- #
class _LdExtractor(HTMLParser):
    """Collect the raw text inside every <script type="application/ld+json">."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []
        self._capture = False
        self._buf = []
        self._other_formats = set()

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "script" and "ld+json" in a.get("type", "").lower():
            self._capture = True
            self._buf = []
        # Best-effort detection of microdata / RDFa (for the out-of-scope note).
        if "itemscope" in a or "itemtype" in a:
            self._other_formats.add("microdata")
        if "typeof" in a or "vocab" in a or "property" in a:
            self._other_formats.add("rdfa")

    def handle_data(self, data):
        if self._capture:
            self._buf.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capture:
            self._capture = False
            self.blocks.append("".join(self._buf))


def _flatten(parsed):
    """Flatten a parsed JSON-LD value into a list of node dicts (handles @graph)."""
    out = []
    queue = parsed if isinstance(parsed, list) else [parsed]
    for item in queue:
        if not isinstance(item, dict):
            continue
        graph = item.get("@graph")
        if isinstance(graph, list):
            for g in graph:
                if isinstance(g, dict):
                    out.append(g)
            # A wrapper that ALSO carries its own @type is rare; keep it too.
            if "@type" in item:
                out.append(item)
        else:
            out.append(item)
    return out


def extract_jsonld(html):
    """Extract JSON-LD nodes from an HTML string.

    Returns (nodes, parse_errors, other_formats, block_count) where:
      nodes         = list of dicts (flattened, @graph expanded)
      parse_errors  = list of {block:int, error:str} for blocks that failed JSON parse
      other_formats = sorted list of non-JSON-LD structured-data formats detected
      block_count   = number of <script type="application/ld+json"> blocks found
    """
    ext = _LdExtractor()
    try:
        ext.feed(html)
    except Exception:  # malformed markup — keep whatever we captured
        pass
    nodes, errors = [], []
    for i, raw in enumerate(ext.blocks):
        text = raw.strip()
        if not text:
            continue
        try:
            nodes.extend(_flatten(json.loads(text)))
        except ValueError as e:
            errors.append({"block": i, "error": "invalid JSON: %s" % e})
    return nodes, errors, sorted(ext._other_formats), len(ext.blocks)


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate_object(obj):
    """Validate one JSON-LD node against the embedded ruleset.

    Returns a report dict: {@type, recognized, missing_required, missing_recommended,
    warnings, sanity_issues}.
    """
    types = _types_of(obj)
    report = {
        "@type": types[0] if len(types) == 1 else (types or None),
        "recognized": False,
        "missing_required": [],
        "missing_recommended": [],
        "warnings": [],
        "sanity_issues": [],
    }

    # Value sanity checks apply regardless of whether the type is in our ruleset.
    for prop in _DATE_PROPS:
        if prop in obj and isinstance(obj[prop], str) and obj[prop].strip():
            if not _ISO_DATE.match(obj[prop].strip()):
                report["sanity_issues"].append(
                    "%s is not ISO-8601: %r" % (prop, obj[prop])
                )
    for prop in _URL_PROPS:
        v = obj.get(prop)
        if isinstance(v, str) and v.strip() and not _ABS_URL.match(v.strip()):
            report["sanity_issues"].append(
                "%s should be an absolute http(s) URL: %r" % (prop, v)
            )

    matched = [t for t in types if t in RULESET]
    if not matched:
        if not types:
            report["warnings"].append("node has no @type — cannot validate")
        else:
            report["warnings"].append(
                "@type %s not in linter ruleset — only generic checks applied"
                % ", ".join(types)
            )
        return report

    report["recognized"] = True
    for t in matched:
        rule = RULESET[t]
        for prop in rule.get("required", []):
            if not _has(obj, prop) and prop not in report["missing_required"]:
                report["missing_required"].append(prop)
        for prop in rule.get("recommended", []):
            if not _has(obj, prop) and prop not in report["missing_recommended"]:
                report["missing_recommended"].append(prop)
        if "deprecated" in rule:
            msg = "DEPRECATION: " + rule["deprecated"]
            if msg not in report["warnings"]:
                report["warnings"].append(msg)

    # Product price sanity: if Product has an embedded Offer, validate it too.
    if "Product" in matched:
        offers = obj.get("offers")
        for off in (offers if isinstance(offers, list) else [offers]):
            if isinstance(off, dict) and "Offer" in _types_of(off):
                sub = validate_object(off)
                for p in sub["missing_required"]:
                    report["sanity_issues"].append("offers.%s is required" % p)
    return report


def lint_html(html, source="<stdin>"):
    """Full pipeline: extract + validate. Returns the complete report dict."""
    nodes, parse_errors, other_formats, block_count = extract_jsonld(html)
    objects = [validate_object(n) for n in nodes]

    error_count = sum(len(o["missing_required"]) + len(o["sanity_issues"]) for o in objects)
    warning_count = sum(len(o["missing_recommended"]) + len(o["warnings"]) for o in objects)

    notes = []
    if not nodes and not parse_errors and other_formats:
        notes.append(
            "No JSON-LD found, but %s markup was detected. Microdata/RDFa "
            "validation is out of scope for this linter — convert to JSON-LD or "
            "use the Rich Results Test UI." % " and ".join(other_formats)
        )
    elif not nodes and not parse_errors:
        notes.append("No JSON-LD structured data found on this page.")
    notes.append(
        "Google's Rich Results Test has no public API. This linter catches common "
        "issues locally; run the Rich Results Test UI as the final eligibility check."
    )

    return {
        "tool": "schema_lint",
        "version": __version__,
        "source": source,
        "blocks_found": block_count,
        "parse_errors": parse_errors,
        "other_formats_detected": other_formats,
        "objects": objects,
        "summary": {
            "objects": len(objects),
            "recognized": sum(1 for o in objects if o["recognized"]),
            "errors": error_count + len(parse_errors),
            "warnings": warning_count,
        },
        "notes": notes,
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _read_html_source(html_arg):
    """Resolve the --html argument to (html_text, source_label)."""
    if html_arg == "-":
        return sys.stdin.read(), "<stdin>"
    with open(html_arg, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read(), html_arg


def _format_human(report):
    lines = []
    s = report["summary"]
    lines.append("schema_lint %s — %s" % (report["version"], report["source"]))
    lines.append("  JSON-LD objects: %d (recognized: %d) | errors: %d | warnings: %d"
                 % (s["objects"], s["recognized"], s["errors"], s["warnings"]))
    for note in report["notes"]:
        lines.append("  note: " + note)
    for pe in report["parse_errors"]:
        lines.append("  [block %s] ERROR %s" % (pe["block"], pe["error"]))
    for i, o in enumerate(report["objects"]):
        lines.append("  [object %d] @type=%s%s"
                     % (i, o["@type"], "" if o["recognized"] else "  (unrecognized)"))
        for p in o["missing_required"]:
            lines.append("      ERROR  missing required: %s" % p)
        for p in o["sanity_issues"]:
            lines.append("      ERROR  %s" % p)
        for p in o["missing_recommended"]:
            lines.append("      warn   missing recommended: %s" % p)
        for w in o["warnings"]:
            lines.append("      warn   %s" % w)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="schema_lint",
        description="Extract and validate JSON-LD structured data locally "
                    "(pre-flight for Google's Rich Results Test).",
    )
    ap.add_argument("url", nargs="?", help="URL to fetch and lint")
    ap.add_argument("--html", metavar="PATH",
                    help="read HTML from a file, or '-' for stdin (instead of a URL)")
    ap.add_argument("--pretty", action="store_true",
                    help="human-readable output instead of JSON")
    ap.add_argument("--timeout", type=int, default=_http.DEFAULT_TIMEOUT,
                    help="HTTP timeout in seconds (default: %(default)s)")
    args = ap.parse_args(argv)

    if not args.url and not args.html:
        ap.error("provide a URL or --html <path|->")
    if args.url and args.html:
        ap.error("provide either a URL or --html, not both")

    if args.html:
        try:
            html, source = _read_html_source(args.html)
        except OSError as e:
            print(json.dumps({"tool": "schema_lint", "error": str(e)}), file=sys.stderr)
            return 2
    else:
        r = _http.get_text(args.url, timeout=args.timeout, accept="text/html")
        if r["error"] or r["status"] != 200:
            print(json.dumps({
                "tool": "schema_lint",
                "source": args.url,
                "error": r["error"] or ("HTTP %s" % r["status"]),
                "status": r["status"],
            }), file=sys.stderr)
            return 2
        # An empty body on HTTP 200 is not a fetch error — fall through to
        # lint_html, which reports "No JSON-LD structured data found on this page."
        html, source = (r["text"] or ""), r["url"]

    report = lint_html(html, source=source)
    if args.pretty:
        print(_format_human(report))
    else:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
