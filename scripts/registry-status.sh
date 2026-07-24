#!/usr/bin/env bash
# registry-status.sh — the distribution drift detector (owner-run, read-only).
#
# The single source of truth for "is every skill's latest version live on both
# registries, and is the bundle-plugin package current?" For each skill declared
# in .claude-plugin/plugin.json it compares:
#   repo version (VERSIONS.md)  vs  ClawHub published  vs  SkillHub published
# and reports the OpenClaw bundle-plugin package version too. Read-only — it
# never publishes; feed its --json to scripts/publish-registries.sh to act.
#
# Usage:
#   bash scripts/registry-status.sh                      # alignment table + summary
#   bash scripts/registry-status.sh --json               # machine-readable (per-skill records)
#   bash scripts/registry-status.sh --require-current    # release gate: exact 120/120 + package
#   bash scripts/registry-status.sh --platform clawhub   # one platform only (clawhub|skillhub|both)
#   bash scripts/registry-status.sh --workers 1          # serial lookups (default 8 parallel;
#                                                        # 120 skills: ~2 min parallel vs >12 min serial)
#
# Requires the `clawhub` and `skillhub` CLIs, logged in (owner machine). See
# docs/distribution.md. CAVEAT: SkillHub state is read via fuzzy search, so a
# "missing" can be a search-recall artifact (the item may be published but not
# surfaced). publish-registries.sh self-corrects — an idempotent publish of an
# already-current version returns "版本已存在" and is treated as in-sync.
set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"

OWNER="aaron-he-zhu"
PKG_NAME="aaron-marketing"        # OpenClaw bundle-plugin package name (openclaw.plugin.json id)
JSON=0
PLAT="both"
WORKERS=8
REQUIRE_CURRENT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --json) JSON=1 ;;
    --require-current) REQUIRE_CURRENT=1 ;;
    --platform) shift; PLAT="${1:-both}" ;;
    --workers) shift; WORKERS="${1:-8}" ;;
    -h|--help) sed -n '2,23p' "$0"; exit 0 ;;
    *) echo "usage: $0 [--json] [--require-current] [--platform clawhub|skillhub|both] [--workers N]" >&2; exit 1 ;;
  esac
  shift
done
case "$PLAT" in clawhub|skillhub|both) ;; *) echo "bad --platform: $PLAT" >&2; exit 1 ;; esac
case "$WORKERS" in
  ''|*[!0-9]*) echo "FAIL: --workers must be a positive integer" >&2; exit 1 ;;
  0) echo "FAIL: --workers must be a positive integer" >&2; exit 1 ;;
esac

need(){ command -v "$1" >/dev/null 2>&1 || { echo "FAIL: '$1' CLI not found on PATH — log in on the owner machine (see docs/distribution.md)" >&2; exit 2; }; }
[ "$PLAT" = skillhub ] || need clawhub
[ "$PLAT" = clawhub ] || need skillhub

# Fail before any network lookup unless plugin discovery is the exact canonical
# catalog: 120 ordered, unique paths and names; 120 unique SkillHub slugs; one
# matching version on every local skill and VERSIONS.md row.  This prevents a
# truncated/duplicated manifest from ever being reported as "120/120".
DIRS=$(/usr/bin/python3 - <<'PY'
import json
import os
from pathlib import Path
import re
import stat
import sys

root = Path(".")
try:
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    catalog = json.loads((root / "references/system-catalog.json").read_text(encoding="utf-8"))
except (OSError, ValueError) as exc:
    print("FAIL: cannot read canonical plugin/catalog identity: %s" % exc, file=sys.stderr)
    raise SystemExit(1)

paths = []
for discipline in catalog.get("logical_order", []):
    if discipline == "protocol":
        paths.extend("protocol/%s" % slug for slug in catalog.get("protocol", {}).get("skills", []))
        continue
    spec = catalog.get("disciplines", {}).get(discipline, {})
    for phase in spec.get("phase_order", []):
        paths.extend(
            "%s/%s/%s" % (discipline, phase, slug)
            for slug in spec.get("phases", {}).get(phase, [])
        )
declared = [
    value[2:] if isinstance(value, str) and value.startswith("./") else value
    for value in plugin.get("skills", [])
]
if (len(paths) != 120 or len(set(paths)) != 120 or declared != paths
        or len({Path(path).name for path in paths}) != 120):
    print("FAIL: plugin discovery must equal the ordered canonical 120-skill catalog", file=sys.stderr)
    raise SystemExit(1)
bundle = plugin.get("version")
if not isinstance(bundle, str) or catalog.get("bundle_version") != bundle:
    print("FAIL: plugin and system catalog bundle versions differ", file=sys.stderr)
    raise SystemExit(1)

version_rows = {}
for line in (root / "VERSIONS.md").read_text(encoding="utf-8").splitlines():
    columns = [item.strip() for item in line.split("|")]
    if (len(columns) >= 5 and columns[1]
            and re.fullmatch(r"[a-z0-9][a-z0-9-]*", columns[1])
            and re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", columns[3])):
        if columns[1] in version_rows:
            print("FAIL: duplicate VERSIONS.md row for %s" % columns[1], file=sys.stderr)
            raise SystemExit(1)
        version_rows[columns[1]] = columns[3]

slugs = set()
names = set()
for relative in paths:
    skill_file = root / relative / "SKILL.md"
    try:
        metadata = skill_file.lstat()
        text = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        print("FAIL: cannot read %s: %s" % (skill_file, exc), file=sys.stderr)
        raise SystemExit(1)
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        print("FAIL: canonical SKILL.md must be a single-link regular file: %s" % skill_file, file=sys.stderr)
        raise SystemExit(1)
    name = Path(relative).name
    values = {}
    for line in text.splitlines()[1:]:
        if line == "---":
            break
        matched = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if matched:
            values[matched.group(1)] = matched.group(2).strip("\"'")
    slug = values.get("slug", "")
    if values.get("name") != name:
        print("FAIL: canonical name drift in %s" % skill_file, file=sys.stderr)
        raise SystemExit(1)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", slug):
        print("FAIL: invalid SkillHub slug in %s" % skill_file, file=sys.stderr)
        raise SystemExit(1)
    if name in names or slug in slugs:
        print("FAIL: canonical skill names and slugs must be unique", file=sys.stderr)
        raise SystemExit(1)
    version = values.get("version", "")
    if (not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version)
            or version_rows.get(name) != version):
        print("FAIL: VERSIONS.md does not match SKILL.md for %s" % name, file=sys.stderr)
        raise SystemExit(1)
    names.add(name)
    slugs.add(slug)
if set(version_rows) != names:
    print("FAIL: VERSIONS.md must contain exactly the canonical 120 skills", file=sys.stderr)
    raise SystemExit(1)
print("\n".join(paths))
PY
) || exit 1

BUNDLE=$(/usr/bin/python3 -c "import json;print(json.load(open('.claude-plugin/plugin.json'))['version'])") || exit 1
REPOSITORY=$(/usr/bin/python3 - <<'PY'
import json
import re
import sys
value = json.load(open(".claude-plugin/plugin.json"))["repository"]
matched = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?", value)
if matched is None:
    print("FAIL: plugin repository must be a canonical github.com HTTPS URL", file=sys.stderr)
    raise SystemExit(1)
print("%s/%s" % matched.groups())
PY
) || exit 1
COMMIT="$(git rev-parse --verify 'HEAD^{commit}' 2>/dev/null)" || {
  echo "FAIL: registry status must be produced from a Git commit" >&2
  exit 1
}
printf '%s' "$COMMIT" | grep -Eq '^[0-9a-f]{40}$|^[0-9a-f]{64}$' || {
  echo "FAIL: registry status commit identity is invalid" >&2
  exit 1
}

# skill dir -> (name, slug, repo version)
repover(){ awk -F'|' -v s=" $1 " '$2==s{gsub(/ /,"",$4);print $4;exit}' VERSIONS.md; }
slugof(){ sed -n 's/^slug: *//p' "$1/SKILL.md" | head -1; }
chver(){ [ "$PLAT" = skillhub ] && { echo "-"; return; }; clawhub inspect "$OWNER/$1" 2>/dev/null | grep -E '(^|[^a-zA-Z])Latest' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1; }
shver(){ [ "$PLAT" = clawhub ] && { echo "-"; return; }
  # Search by the exact SLUG, not the skill name: a name query (e.g. "content-writer")
  # buries an aaron-prefixed entry (aaron-content-writer) past the result cutoff and
  # reads as a false "missing". The slug query surfaces it precisely.
  skillhub search "$1" --search-limit 20 --search-timeout 8 --json 2>/dev/null | /usr/bin/python3 -c "import sys,json
try:
 d=json.load(sys.stdin); r=d if isinstance(d,list) else d.get('results',d.get('skills',[]))
 print(next((str(x.get('version','?')) for x in r if str(x.get('slug',x.get('id','')))==sys.argv[1]),''))
except Exception: print('')" "$1"; }

row(){ # $1 skill dir → one TSV row on stdout
  local d="$1" name slug rv ch sh
  [ -f "$d/SKILL.md" ] || return 0
  name="$(basename "$d")"; slug="$(slugof "$d")"; rv="$(repover "$name")"
  ch="$(chver "$name")"; [ -z "$ch" ] && ch="MISSING"
  sh="$(shver "$slug")"; [ -z "$sh" ] && sh="MISSING"
  printf '%s\t%s\t%s\t%s\t%s\n' "$name" "$rv" "$ch" "$sh" "$slug"
}

tmp="$(mktemp)"; trap 'rm -f "$tmp"' EXIT
if [ "$WORKERS" -gt 1 ]; then
  # Read-only CLI lookups parallelize safely; each row is one short atomic
  # append. Completion order is nondeterministic, so sort for stable output.
  export PLAT OWNER
  export -f row slugof repover chver shver
  printf '%s\n' $DIRS | xargs -P "$WORKERS" -n 1 bash -c 'row "$1"' _ >> "$tmp"
  sort -o "$tmp" "$tmp"
else
  for d in $DIRS; do row "$d" >> "$tmp"; done
fi

# bundle-plugin package version
pkgv="-"
if [ "$PLAT" != skillhub ]; then
  pkgv="$(clawhub package inspect "$PKG_NAME" --json 2>/dev/null | /usr/bin/python3 -c '
import json,sys
try:
    value=json.load(sys.stdin).get("package",{}).get("latestVersion","")
    print(value if isinstance(value,str) else "")
except Exception:
    print("")
')"
  [ -z "$pkgv" ] && pkgv="MISSING"
fi

gate_ok="$(
  BUNDLE="$BUNDLE" PLAT="$PLAT" pkgv="$pkgv" _TMP="$tmp" /usr/bin/python3 - <<'PY'
import os
rows = [line.rstrip("\n").split("\t") for line in open(os.environ["_TMP"], encoding="utf-8")]
platform = os.environ["PLAT"]
valid = (
    len(rows) == 120
    and len({row[0] for row in rows}) == 120
    and len({row[4] for row in rows}) == 120
    and all(
        len(row) == 5
        and (platform == "skillhub" or row[2] == row[1])
        and (platform == "clawhub" or row[3] == row[1])
        for row in rows
    )
    and (platform == "skillhub" or os.environ["pkgv"] == os.environ["BUNDLE"])
)
print("1" if valid else "0")
PY
)"

if [ "$JSON" -eq 1 ]; then
  BUNDLE="$BUNDLE" PLAT="$PLAT" pkgv="$pkgv" PKG_NAME="$PKG_NAME" \
    REPOSITORY="$REPOSITORY" COMMIT="$COMMIT" _TMP="$tmp" /usr/bin/python3 -c "
import json,os,sys
rows=[]
for ln in open(os.environ['_TMP']):
    n,rv,ch,sh,slug=ln.rstrip('\n').split('\t')
    rows.append({'skill':n,'slug':slug,'repo':rv,'clawhub':ch,'skillhub':sh,
                 'clawhub_ok':(ch==rv),'skillhub_ok':(sh==rv)})
print(json.dumps({'schema_version':'1.0','repository':os.environ['REPOSITORY'],
  'commit':os.environ['COMMIT'],'bundle':os.environ['BUNDLE'],'platform':os.environ['PLAT'],
  'package':{'name':os.environ['PKG_NAME'],'clawhub':os.environ['pkgv'],'ok':os.environ['pkgv']==os.environ['BUNDLE']},
  'skills':rows},indent=2))
  " _TMP="$tmp"
  if [ "$REQUIRE_CURRENT" -eq 1 ] && [ "$gate_ok" != 1 ]; then
    echo "FAIL: registry release gate is not current for platform scope $PLAT (bare --require-current checks both registries + package)" >&2
    exit 1
  fi
  exit 0
fi

# human table + summary
awk -F'\t' -v plat="$PLAT" '
function mark(v,r){return (v==r)?"ok":((v=="MISSING")?"MISS":"OLD")}
BEGIN{printf "%-30s %-8s %-9s %-9s\n","SKILL","REPO","CLAWHUB","SKILLHUB"
      printf "%-30s %-8s %-9s %-9s\n","-----","----","-------","--------"}
{
 chs=(plat=="skillhub")?"-":mark($3,$2); shs=(plat=="clawhub")?"-":mark($4,$2)
 flag=((chs=="ok"||chs=="-")&&(shs=="ok"||shs=="-"))?"":"  <-"
 printf "%-30s %-8s %-9s %-9s%s\n",$1,$2,$3" "chs,$4" "shs,flag
 tot++
 if(chs=="ok")cok++; else if(chs=="MISS")cmiss++; else if(chs!="-")cold++
 if(shs=="ok")sok++; else if(shs=="MISS")smiss++; else if(shs!="-")sold++
}
END{
 print ""
 print "== summary ("tot" skills) =="
 if(plat!="skillhub") printf "  ClawHub : %d current, %d stale, %d missing\n",cok,cold,cmiss
 if(plat!="clawhub")  printf "  SkillHub: %d current, %d stale, %d missing\n",sok,sold,smiss
}' "$tmp"

if [ "$PLAT" != skillhub ]; then
  if [ "$pkgv" = "$BUNDLE" ]; then echo "  Package : $PKG_NAME@$pkgv (current)"; else echo "  Package : $PKG_NAME@$pkgv != bundle $BUNDLE  <- publish-package.sh"; fi
fi
if [ "$REQUIRE_CURRENT" -eq 1 ] && [ "$gate_ok" != 1 ]; then
  echo "FAIL: registry release gate is not current for platform scope $PLAT (bare --require-current checks both registries + package)" >&2
  exit 1
fi
