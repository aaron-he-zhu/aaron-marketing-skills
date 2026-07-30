#!/usr/bin/env python3
"""stats-dashboard.py — cross-registry download/install stats for the skills.

The README badges show registry totals. ClawHub, SkillHub, and skills.sh use the
owner-wide number printed by each platform. ClaudeSkills is the sum of the two
explicit collection pages that make up this repository family.

  ClawHub    GET https://clawhub.ai/<owner>                    -> profile "downloads"
  SkillHub   GET https://api.skillhub.cn/api/v1/users/<h>/skills -> totalDownloads
  skills.sh  GET https://www.skills.sh/<owner>                 -> "N total installs"
             (aggregates every repo under the owner)
  ClaudeSkills
             GET https://claudeskills.info/skills/<owner>/<repo>/ -> "N total installs"
             (summed for aaron-marketing-skills + seo-geo-claude-skills)

A per-skill detail table (this bundle's declared skills) is still available in
the default / --out / --json modes for "which skills are most downloaded";
ClawHub + SkillHub expose per-skill numbers publicly, skills.sh needs a Vercel
OIDC token (SKILLS_SH_TOKEN) for its per-skill column.

Usage:
  python3 scripts/stats-dashboard.py                 # owner totals + per-skill table
  python3 scripts/stats-dashboard.py --json          # machine-readable
  python3 scripts/stats-dashboard.py --out FILE.md   # also write markdown
  python3 scripts/stats-dashboard.py --badges DIR    # owner totals -> shields.io JSONs

--badges is the fast path used by the scheduled GitHub Action. It writes one
shields.io "endpoint" JSON per platform so the README renders live-looking
badges via img.shields.io/endpoint. A transient fetch failure (value None)
keeps the previously committed value instead of zeroing the badge.
"""
from __future__ import annotations
import json, os, re, sys, time, urllib.request, urllib.parse, pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
CLAWHUB_OWNER = "aaron-he-zhu"        # also the skills.sh owner handle
SKILLHUB_OWNER = "user_2c0f1e77"
CLAUDESKILLS_REPOS = ("aaron-marketing-skills", "seo-geo-claude-skills")
SKILLS_SH_TOKEN = os.environ.get("SKILLS_SH_TOKEN")


def _get(url, headers=None):
    """Fetch JSON. Returns parsed object, or None on any failure."""
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "stats/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)
    except Exception:
        return None


def _get_text(url):
    """Fetch text (HTML). Returns the body, or None on any failure."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "stats/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.read().decode("utf-8", "ignore")
    except Exception:
        return None


def _parse_human(s):
    """'49.4k' / '126.8K' / '1,234' / '84260' -> int. None if unparseable."""
    m = re.match(r"\s*([\d.,]+)\s*([kmb]?)\s*$", s, re.I)
    if not m:
        return None
    mult = {"": 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[m.group(2).lower()]
    try:
        # group(1) is [\d.,]+, which still admits unparseable forms like "." or
        # "1.2.3"; honor the documented None-on-parse-failure contract.
        return int(round(float(m.group(1).replace(",", "")) * mult))
    except ValueError:
        return None


# ---- owner-wide totals (what the badges show) -----------------------------

def clawhub_owner_total(owner):
    """Owner-wide download total from the ClawHub publisher page — ClawHub has no
    JSON endpoint for it, so scrape the profile the same figure is printed on.
    Prefers the exact integer in the OG-card URL (…downloads=N, HTML-escaped as
    &amp;); falls back to the humanized profile stat. Returns int, or None on a
    fetch/parse failure so the caller preserves the prior badge."""
    html = _get_text(f"https://clawhub.ai/{urllib.parse.quote(owner)}")
    if html is None:
        return None
    m = re.search(r"[?&;]downloads=(\d+)", html)          # exact, from OG card url
    if m:
        return int(m.group(1))
    m = re.search(r'stat-value">\s*([\d.,]+\s*[kmb]?)\s*</dd>\s*'
                  r'<dt[^>]*stat-label">\s*downloads', html, re.I)   # humanized fallback
    return _parse_human(m.group(1)) if m else None


def skillhub_owner_total(owner):
    """Owner-wide download total from SkillHub's user API. totalDownloads spans
    every skill the owner has published (105 at writing) — more than this
    bundle's declared set. pageSize=1 keeps it to one cheap request. Returns int,
    or None on failure."""
    d = _get(f"https://api.skillhub.cn/api/v1/users/{urllib.parse.quote(owner)}/skills?pageSize=1")
    if not d or d.get("totalDownloads") is None:
        return None
    return d.get("totalDownloads")


def skills_sh_owner_total(owner):
    """Owner-wide install total from the skills.sh publisher page — it already
    aggregates every repo under the owner ('N total installs across M
    repositories'), so no per-repo list to maintain. Humanized on the page
    ('126.8K'). Hits www.skills.sh directly (the apex host 308-redirects there,
    which urllib < 3.11 won't follow). Returns int, or None on failure."""
    html = _get_text(f"https://www.skills.sh/{urllib.parse.quote(owner)}")
    if html is None:
        return None
    clean = re.sub(r"<!--.*?-->", "", html)  # drop React SSR comment markers first
    m = re.search(r"([\d.,]+\s*[kmb]?)\s*total installs", clean, re.I)
    return _parse_human(m.group(1)) if m else None


def claudeskills_repos_total(owner, repos):
    """Combined install total for the explicitly tracked ClaudeSkills pages.

    ClaudeSkills exposes a humanized total on each collection page but no
    collection lookup in its public search API. Treat the pair as one atomic
    source: if either page cannot be fetched or parsed, return None so the
    previously committed combined badge is preserved instead of undercounting.
    """
    total = 0
    for repo in repos:
        url = (
            "https://claudeskills.info/skills/"
            f"{urllib.parse.quote(owner)}/{urllib.parse.quote(repo)}/"
        )
        page = _get_text(url)
        if page is None:
            return None
        clean = re.sub(r"<!--.*?-->", "", page, flags=re.S)
        clean = re.sub(r"<[^>]+>", " ", clean)
        clean = re.sub(r"\s+", " ", clean)
        match = re.search(r"([\d.,]+\s*[kmb]?)\s+total installs", clean, re.I)
        value = _parse_human(match.group(1)) if match else None
        if value is None:
            return None
        total += value
    return total


# ---- per-skill detail (this bundle's declared skills) ---------------------

def clawhub(slug):
    d = _get(f"https://clawhub.ai/api/v1/search?q={urllib.parse.quote(slug)}")
    if not d:
        return None
    for r in d.get("results", []):
        if r.get("slug") == slug and r.get("ownerHandle") == CLAWHUB_OWNER:
            return {"downloads": r.get("downloads", 0)}
    return None


def skillhub(slug):
    d = _get(f"https://api.skillhub.cn/api/v1/skills/{urllib.parse.quote(slug)}")
    if not d or d.get("owner", {}).get("handle") != SKILLHUB_OWNER:
        return None
    st = d.get("skill", {}).get("stats", {}) or {}
    return {"downloads": st.get("downloads", 0), "installs": st.get("installs", 0),
            "stars": st.get("stars", 0)}


def skills_sh(owner, repo, slug):
    if not SKILLS_SH_TOKEN:
        return None
    d = _get(f"https://skills.sh/api/v1/skills/{owner}/{repo}/{slug}",
             headers={"Authorization": f"Bearer {SKILLS_SH_TOKEN}", "User-Agent": "stats/1.0"})
    return {"installs": d.get("installs", 0)} if d else None


def main():
    # Registry totals displayed by the README badges.
    owner = {
        "clawhub": clawhub_owner_total(CLAWHUB_OWNER),
        "skillhub": skillhub_owner_total(SKILLHUB_OWNER),
        "skillssh": skills_sh_owner_total(CLAWHUB_OWNER),
        "claudeskills": claudeskills_repos_total(CLAWHUB_OWNER, CLAUDESKILLS_REPOS),
    }

    # Fast path for the scheduled badge refresh; no per-skill crawl.
    for i, a in enumerate(sys.argv):
        if a == "--badges" and i + 1 < len(sys.argv):
            write_badges(pathlib.Path(sys.argv[i + 1]),
                         owner["clawhub"], owner["skillhub"], owner["skillssh"],
                         owner["claudeskills"])
            return

    # Per-skill detail for this bundle's declared skills (a subset of the owner's
    # published skills — hence the table can sum to less than the owner totals).
    with open(REPO / ".claude-plugin/plugin.json", encoding="utf-8") as f:
        plugin_data = json.load(f)
    names = [p[2:].split("/")[-1] for p in plugin_data.get("skills", [])]
    rows = []
    for n in names:
        ch = clawhub(n)
        time.sleep(0.2)
        sh = skillhub(n) or skillhub(f"aaron-{n}")
        time.sleep(0.2)
        ssh = skills_sh(CLAWHUB_OWNER, "aaron-marketing-skills", n)
        rows.append({
            "skill": n,
            "clawhub_downloads": (ch or {}).get("downloads", 0),
            "skillhub_downloads": (sh or {}).get("downloads", 0),
            "skillhub_installs": (sh or {}).get("installs", 0),
            "skillhub_stars": (sh or {}).get("stars", 0),
            "skillssh_installs": (ssh or {}).get("installs", 0),
        })
    for r in rows:
        r["total_downloads"] = r["clawhub_downloads"] + r["skillhub_downloads"]
    rows.sort(key=lambda r: r["total_downloads"], reverse=True)

    if "--json" in sys.argv:
        print(json.dumps({"owner_totals": owner, "skills": rows},
                         indent=2, ensure_ascii=False))
        return

    fmt = lambda n: f"{n:,}" if n is not None else "n/a"
    out = ["# Skill stats — cross-registry snapshot", "",
           f"Owner-wide totals (what the badges show) — ClawHub downloads: "
           f"**{fmt(owner['clawhub'])}** · SkillHub downloads: **{fmt(owner['skillhub'])}** · "
           f"skills.sh installs: **{fmt(owner['skillssh'])}** (across all skills/repos "
           f"under the owner, present and future) · ClaudeSkills installs: "
           f"**{fmt(owner['claudeskills'])}** (combined across the two tracked repos).", "",
           "Per-skill breakdown below covers this bundle's declared skills only:", "",
           "| Skill | ClawHub ↓ | SkillHub ↓ | SkillHub installs | ★ |",
           "|-------|-----------|------------|-------------------|---|"]
    for r in rows:
        out.append(f"| {r['skill']} | {r['clawhub_downloads']:,} | "
                   f"{r['skillhub_downloads']:,} | {r['skillhub_installs']:,} | {r['skillhub_stars']} |")
    text = "\n".join(out)
    print(text)
    for i, a in enumerate(sys.argv):
        if a == "--out" and i + 1 < len(sys.argv):
            pathlib.Path(sys.argv[i + 1]).write_text(text + "\n", encoding="utf-8")
            print(f"\n[written to {sys.argv[i + 1]}]", file=sys.stderr)


def _human(n):
    if n >= 1000:
        return f"{n/1000:.1f}k".replace(".0k", "k")
    return str(n)


def write_badges(dirpath, clawhub, skillhub, skillssh, claudeskills):
    """Write shields.io endpoint-badge JSONs. A value of None (transient fetch
    failure) preserves the previously committed value so the badge never zeroes;
    a genuine 0 is written normally."""
    dirpath.mkdir(parents=True, exist_ok=True)
    # label = platform name only (mirrors the skills.sh "Skills <n>" badge);
    # the number is the message. No "downloads"/"下载" suffix.
    specs = [
        ("clawhub.json", "ClawHub", clawhub, "FF6B35"),
        ("skillhub.json", "SkillHub", skillhub, "00A9A5"),
        ("skillssh.json", "skills.sh", skillssh, "0A0A0A"),
        ("claudeskills.json", "ClaudeSkills", claudeskills, "D97757"),
    ]
    for fname, label, value, color in specs:
        path = dirpath / fname
        # Preserve the committed logoSvg (platform icon) across refreshes — it
        # lives only in the JSON, not hardcoded here.
        prior = {}
        if path.exists():
            try:
                prior = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                prior = {}
        if value is None:  # fetch failure → keep prior committed value
            if prior:
                print(f"[badge {fname}: fetch was empty, kept existing]", file=sys.stderr)
                continue
            value = 0
        obj = {"schemaVersion": 1, "label": label, "message": _human(value), "color": color}
        if prior.get("logoSvg"):
            obj["logoSvg"] = prior["logoSvg"]
        path.write_text(json.dumps(obj, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[badge {fname}: {_human(value)}]", file=sys.stderr)


if __name__ == "__main__":
    main()
