#!/usr/bin/env python3
"""Audit-gate convergence telemetry — Python 3 stdlib only, read-only.

The eight auditor gates produce dated v3 artifacts under memory/audits/. That
is a time series most projects never look at, so the loop question — "are FIX
cycles actually converging, or is the same target audited forever without
reaching SHIP?" — goes unanswered. This tool renders the answer from the
artifacts themselves. It never writes, never mutates state, and treats
unparseable files as skipped rows (reported), never as evidence.

  python3 scripts/audit-trends.py [--root DIR] [--framework CORE-EEAT] [--json]

Convergence signals per (framework, profile, target) series:
  delta      final score change, first to latest scored audit
  stalled    3+ audits of the same target, none verdict SHIP
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

TOP_KEY = re.compile(r"^([A-Za-z][A-Za-z0-9_]*)[ \t]*:[ \t]*(.*)$")
FRAMEWORKS = {"CORE-EEAT", "CITE", "STAR", "ROAS", "SEND", "RAMP", "ECHO", "TALE", "MULTI"}
FIELDS = ("class", "framework", "profile", "target", "observed_at", "status",
          "verdict", "score_state", "veto_count", "raw_overall_score",
          "final_overall_score")


def scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1]
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_artifact(path):
    """Lenient scalar scan of one v3 artifact; returns a dict or None."""
    try:
        if path.is_symlink() or not path.is_file():
            return None
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    values = {}
    for line in text.splitlines():
        match = TOP_KEY.match(line)
        if not match:
            continue
        key, raw = match.groups()
        if key in FIELDS and key not in values:
            values[key] = scalar(raw)
    if values.get("framework") not in FRAMEWORKS or not values.get("observed_at"):
        return None
    for name in ("veto_count", "raw_overall_score", "final_overall_score"):
        if name in values:
            try:
                values[name] = int(values[name])
            except (TypeError, ValueError):
                values.pop(name)
    values["path"] = str(path)
    return values


def collect(root):
    audits_dir = root / "memory" / "audits"
    artifacts, skipped = [], 0
    if audits_dir.is_dir():
        for path in sorted(audits_dir.rglob("*.md")):
            parsed = parse_artifact(path)
            if parsed is None:
                skipped += 1
            else:
                artifacts.append(parsed)
    return artifacts, skipped


def series_report(artifacts):
    series = {}
    for item in artifacts:
        key = (item["framework"], item.get("profile", "?"), item["target"])
        series.setdefault(key, []).append(item)
    rows = []
    for (framework, profile, target), items in sorted(series.items()):
        items.sort(key=lambda i: (i["observed_at"], i["path"]))
        scored = [i for i in items if isinstance(i.get("final_overall_score"), int)]
        delta = scored[-1]["final_overall_score"] - scored[0]["final_overall_score"] \
            if len(scored) >= 2 else None
        rows.append({
            "framework": framework,
            "profile": profile,
            "target": target,
            "audits": len(items),
            "first": items[0]["observed_at"],
            "latest": items[-1]["observed_at"],
            "latest_verdict": items[-1].get("verdict", "?"),
            "latest_score": scored[-1]["final_overall_score"] if scored else None,
            "score_delta": delta,
            "stalled": len(items) >= 3 and not any(
                i.get("verdict") == "SHIP" for i in items),
        })
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root containing memory/.")
    parser.add_argument("--framework", choices=sorted(FRAMEWORKS))
    parser.add_argument("--json", action="store_true", help="Machine-readable output.")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    artifacts, skipped = collect(root)
    if args.framework:
        artifacts = [a for a in artifacts if a["framework"] == args.framework]
    rows = series_report(artifacts)

    if args.json:
        print(json.dumps({"root": str(root), "artifacts": len(artifacts),
                          "skipped_unparseable": skipped, "series": rows},
                         indent=2, ensure_ascii=False))
        return 0

    if not artifacts:
        print("No parseable v3 audit artifacts under %s "
              "(skipped %d unparseable file(s)). Gates have not produced a "
              "time series yet." % (root / "memory" / "audits", skipped))
        return 0

    print("%-10s %-28s %-22s %-6s %-10s %-6s %-6s %s" % (
        "FRAMEWORK", "TARGET", "PROFILE", "#", "LATEST", "VERDICT", "SCORE", "DELTA"))
    for row in rows:
        target = row["target"] if len(row["target"]) <= 28 else row["target"][:25] + "..."
        delta = "%+d" % row["score_delta"] if row["score_delta"] is not None else "-"
        score = str(row["latest_score"]) if row["latest_score"] is not None else "-"
        flag = "  STALLED" if row["stalled"] else ""
        print("%-10s %-28s %-22s %-6d %-10s %-6s %-6s %s%s" % (
            row["framework"], target, row["profile"][:22], row["audits"],
            row["latest"][:10], row["latest_verdict"], score, delta, flag))
    stalled = [r for r in rows if r["stalled"]]
    print("\n%d series across %d artifact(s); %d stalled (3+ audits, no SHIP); "
          "%d file(s) skipped as unparseable."
          % (len(rows), len(artifacts), len(stalled), skipped))
    if stalled:
        print("Stalled series are loops that are NOT converging — escalate the "
              "underlying veto/finding instead of re-auditing the same state.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
