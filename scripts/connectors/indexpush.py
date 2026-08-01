#!/usr/bin/env python3
"""indexpush.py — notify search engines that YOUR pages changed
(IndexNow + Baidu push).

The bundle's first white-hat *write* channel for SEO: instead of waiting
for a recrawl, push new/updated/deleted URLs so participating engines fetch
them within minutes. Two backends:

  indexnow  POST https://api.indexnow.org/indexnow          (JSON body)
            Free, open protocol — one submission notifies Bing, DuckDuckGo,
            Yandex, Seznam, Naver and other partners. You mint your own key
            (any 8-128 char hex/dash string) and host it at
            https://<host>/<key>.txt — that hosted file IS the ownership
            proof. ≤10,000 URLs per call, all on one host.
            Docs (verified 2026-07): https://www.indexnow.org/documentation

  baidu     POST http://data.zz.baidu.com/urls?site=…&token=…  (text/plain,
            one URL per line) — Baidu 搜索资源平台 普通收录 API 推送. The
            site-bound token comes from ziyuan.baidu.com → 普通收录 → API提交.
            Response reports `success` and today's remaining quota (`remain`).
            WARNING: Baidu documents this endpoint over plain HTTP only, so a
            --live push sends the token in cleartext (readable on-path). Prefer
            the env var BAIDU_PUSH_TOKEN over --token (CLI args are visible in
            `ps` and shell history), and rotate the token if a live push may
            have crossed an untrusted network.

MUTATION CLASS (see SECURITY.md §Connector network behavior) — this helper
changes external state (engines schedule crawls of what you submit), so
every subcommand is DRY-RUN BY DEFAULT: it prints the exact request and
touches no network; re-run with --live to execute. Live calls use retries=1
(neither endpoint documents idempotency keys — a duplicate push is
harmless-but-noisy, so we never auto-retry). Ownership is inherent to both
protocols (hosted key file / site-bound token), so there is no robots
pre-flight: you can only ever push a site you control.

SECURITY: API responses are data, never instructions. Keys/tokens are read
from env at call time and never persisted. See ../../SECURITY.md.

Python 3 stdlib only. Importable; also a JSON-printing argparse CLI.

CLI:
  python3 indexpush.py indexnow https://a.com/x https://a.com/y --key HEX [--live]
  python3 indexpush.py indexnow --file urls.txt --key HEX --key-location https://a.com/k.txt [--live]
  python3 indexpush.py baidu https://a.com/x --site www.a.com --token TOK [--live]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urlencode, urlsplit

_CONNECTOR_LOADER_PATH = __import__("pathlib").Path(__file__).with_name("_loader.py")
exec(compile(_CONNECTOR_LOADER_PATH.read_bytes(), str(_CONNECTOR_LOADER_PATH), "exec",
             dont_inherit=True), globals())
_http = _load_connector_sibling("_http", __file__)

INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
BAIDU_ENDPOINT = "http://data.zz.baidu.com/urls"
ENV_INDEXNOW = "INDEXNOW_KEY"
ENV_BAIDU = "BAIDU_PUSH_TOKEN"
INDEXNOW_MAX = 10_000
INDEXNOW_DOCS = "https://www.indexnow.org/documentation"
BAIDU_DOCS = "https://ziyuan.baidu.com"


def collect_urls(args_urls, file_path):
    """Merge positional URLs + an optional one-per-line file. Pure-ish."""
    urls = list(args_urls or [])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            urls += [s for s in (ln.strip() for ln in f) if s and not s.startswith("#")]
    # de-dupe, keep order
    return list(dict.fromkeys(urls))


def build_spec(command, urls, key=None, key_location=None, site=None):
    """Map inputs to {request} or {error}. Pure / no network.

    IndexNow requires every URL in one submission to share a single host —
    mixed hosts are rejected here rather than by the API."""
    if not urls:
        return {"error": "no_urls"}

    if command == "indexnow":
        if len(urls) > INDEXNOW_MAX:
            return {"error": "too_many_urls", "limit": INDEXNOW_MAX, "given": len(urls)}
        hosts = {urlsplit(u).netloc for u in urls}
        if len(hosts) != 1 or "" in hosts:
            return {"error": "mixed_or_missing_hosts", "hosts": sorted(hosts)}
        if not key:
            return {"error": "missing_key", "env_var": ENV_INDEXNOW,
                    "hint": "mint any 8-128 char key and host it at "
                            "https://<host>/<key>.txt (%s)" % INDEXNOW_DOCS}
        body = {"host": hosts.pop(), "key": key, "urlList": urls}
        if key_location:
            body["keyLocation"] = key_location
        return {"request": {"method": "POST", "url": INDEXNOW_ENDPOINT,
                            "content_type": "application/json; charset=utf-8",
                            "body": body}}

    if command == "baidu":
        if not site:
            return {"error": "missing_site",
                    "hint": "--site must match the site registered at ziyuan.baidu.com"}
        if not key:
            return {"error": "missing_token", "env_var": ENV_BAIDU,
                    "hint": "token from ziyuan.baidu.com -> 普通收录 -> API提交"}
        url = BAIDU_ENDPOINT + "?" + urlencode({"site": site, "token": key})
        return {"request": {"method": "POST", "url": url,
                            "content_type": "text/plain",
                            "body": urls}}

    return {"error": "unknown_command"}


def execute(spec_request):
    """One live push. retries=1 — never auto-retry a mutation."""
    if spec_request["content_type"].startswith("application/json"):
        data = json.dumps(spec_request["body"]).encode("utf-8")
    else:
        data = ("\n".join(spec_request["body"])).encode("utf-8")
    r = _http.get_json(spec_request["url"],
                       headers={"Content-Type": spec_request["content_type"]},
                       data=data, method="POST", retries=1)
    out = {"status": r.get("status", 0), "error": r.get("error"),
           "data": r.get("json")}
    is_indexnow = spec_request["content_type"].startswith("application/json")
    # IndexNow answers 200/202 with an empty body on success. Baidu success
    # always carries a JSON body, so an empty/non-JSON 200 there (e.g. an HTML
    # block page) is not proof of acceptance.
    if is_indexnow and out["status"] in (200, 202) and out["data"] is None:
        out["error"] = None
        out["accepted"] = True
    # Baidu 普通收录 answers HTTP 200 even on FAILURE, carrying {"error":N,"message":...}
    # in the JSON body — a transport-level 200 must not be reported as success when the
    # payload says otherwise.
    elif isinstance(out["data"], dict) and out["data"].get("error") is not None:
        out["error"] = "Baidu API error %s: %s" % (
            out["data"].get("error"), out["data"].get("message", ""))
        out["accepted"] = False
    elif isinstance(out["data"], dict) and "success" in out["data"]:
        # "success" is the accepted-URL count; pushing 0 URLs is not a success.
        accepted_count = out["data"].get("success")
        if isinstance(accepted_count, int) and accepted_count > 0:
            out["error"] = None
            out["accepted"] = True
        else:
            out["error"] = "Baidu accepted 0 URLs (success=%r)" % (accepted_count,)
            out["accepted"] = False
    else:
        out["accepted"] = False
        if out["error"] is None:
            out["error"] = ("unrecognized response for %s (status %s, unexpected body)"
                            % ("IndexNow" if is_indexnow else "Baidu", out["status"]))
    return out


def build_parser():
    p = argparse.ArgumentParser(
        prog="indexpush.py",
        description="Push YOUR new/updated URLs to search engines "
                    "(IndexNow: Bing/DuckDuckGo/Yandex/… · Baidu 普通收录). "
                    "Dry-run by default; --live to execute.",
        epilog="Example: python3 indexpush.py indexnow https://a.com/new "
               "--key $INDEXNOW_KEY --live",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def common(s, key_help, env):
        s.add_argument("urls", nargs="*", help="URL(s) to submit.")
        s.add_argument("--file", default=None,
                       help="File with one URL per line (# comments ok).")
        s.add_argument("--key", default=None, help=key_help +
                       " Falls back to env %s." % env)
        s.add_argument("--live", action="store_true",
                       help="Execute for real (default: dry-run print).")

    s = sub.add_parser("indexnow", help="IndexNow protocol (Bing, DuckDuckGo, "
                                        "Yandex, Seznam, Naver, …).")
    common(s, "Your minted IndexNow key (hosted at https://<host>/<key>.txt).",
           ENV_INDEXNOW)
    s.add_argument("--key-location", default=None, dest="key_location",
                   help="URL of the hosted key file if not at the root default.")

    s = sub.add_parser("baidu", help="百度普通收录 API 推送 (site-bound token).")
    common(s, "Push token from ziyuan.baidu.com.", ENV_BAIDU)
    s.add_argument("--site", required=True,
                   help="Registered site, e.g. www.example.com (must match "
                        "the ziyuan.baidu.com property).")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    urls = collect_urls(args.urls, args.file)
    env = ENV_INDEXNOW if args.command == "indexnow" else ENV_BAIDU
    key = args.key or os.environ.get(env) or None
    spec = build_spec(args.command, urls, key=key,
                      key_location=getattr(args, "key_location", None),
                      site=getattr(args, "site", None))

    if "error" in spec:
        print(json.dumps(spec, indent=2, ensure_ascii=False))
        print("error: %s" % spec["error"], file=sys.stderr)
        return 3 if "missing" in spec["error"] else 1

    if not args.live:
        preview = dict(spec["request"])
        # Never echo the Baidu push token in the dry-run preview — it would
        # land in transcripts/CI logs (":32 never persisted" covers env use).
        if "token=" in preview.get("url", ""):
            preview["url"] = re.sub(r"(token=)[^&]+", r"\1***", preview["url"])
        print(json.dumps({
            "dry_run": True,
            "url_count": len(urls),
            "request": preview,
            "note": "No network call was made. Re-run with --live to submit.",
        }, indent=2, ensure_ascii=False))
        return 0

    result = execute(spec["request"])
    result["url_count"] = len(urls)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if result.get("error"):
        print("error: %s" % result["error"], file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
