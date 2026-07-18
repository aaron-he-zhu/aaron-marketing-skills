#!/usr/bin/env bash
# check-versions.sh — version-sync guard for the 10-surface tracking contract.
#
# CONTRIBUTING.md §6 requires the bundle version and every skill version to
# stay in sync across the typed system catalog, VERSIONS.md, plugin.json, both
# marketplace mirrors, root/localized README badges, AGENTS.md, and CLAUDE.md. Keeping
# these release surfaces aligned by
# hand is exactly the kind of mechanical step that drifts, so CI enforces it:
#
#   1. Bundle version (plugin.json) == every "version" field in both
#      marketplace.json mirrors == README + zh badge == "current bundle"
#      lines == CLAUDE.md declaration == VERSIONS.md "Current release" line,
#      and the changelog has a `### v<bundle>` entry.
#   2. Every SKILL.md: top-level `version` == `metadata.version` == its row
#      in the VERSIONS.md table (per-skill last-changed versioning means
#      rows may differ from the bundle — they must only match their skill).
#   3. VERSIONS.md has exactly one row per skill directory, none extra.
#   4. The GitHub About SSOT (.github/repo-about.json) leads with the current
#      skill count — the About is not a versioned file, so it silently drifted
#      on the v13/v14 discipline bumps; this keeps its count honest offline, and
#      scripts/sync-about.sh + about-drift.yml handle projecting/verifying it on GitHub.
#
# Bash plus Python stdlib JSON parsing (repo dependency policy). Exit 0 clean, 1 on any
# mismatch, with one FAIL line per finding.

set -u
cd "$(cd "$(dirname "$0")/.." && pwd)"

fail=0
err() { echo "FAIL: $*" >&2; fail=1; }

# ---- 1. bundle-level sync ---------------------------------------------------
BUNDLE=$(sed -n 's/^  "version": "\([0-9][0-9.]*\)",$/\1/p' .claude-plugin/plugin.json | head -1)
if [ -z "$BUNDLE" ]; then
  err "cannot read bundle version from .claude-plugin/plugin.json"
else
  for f in marketplace.json .claude-plugin/marketplace.json; do
    vers=$(sed -n 's/.*"version": "\([0-9][0-9.]*\)".*/\1/p' "$f")
    # Fail CLOSED: a missing/renamed "version" key extracts nothing — that must
    # FAIL, not silently pass (a `grep -qv` on empty input returns no-match).
    if [ -z "$vers" ]; then
      err "$f has no readable \"version\" key (bundle-sync cannot verify)"
    else
      while read -r v; do
        [ "$v" = "$BUNDLE" ] || err "$f carries version $v != bundle $BUNDLE"
      done <<< "$vers"
    fi
  done
  catalog_bundle=$(sed -n 's/.*"bundle_version": "\([0-9][0-9.]*\)".*/\1/p' references/system-catalog.json | head -1)
  [ "$catalog_bundle" = "$BUNDLE" ] || err "references/system-catalog.json bundle_version $catalog_bundle != bundle $BUNDLE"
  framework_catalog=$(sed -n 's/.*"catalog_version": "\([0-9][0-9.]*\)".*/\1/p' references/framework-catalog.json | head -1)
  if [ -z "$framework_catalog" ]; then
    err "references/framework-catalog.json has no readable \"catalog_version\" (bundle-sync cannot verify)"
  else
    [ "$framework_catalog" = "$BUNDLE" ] || err "references/framework-catalog.json catalog_version $framework_catalog != bundle $BUNDLE"
  fi
  grep -q "version-$BUNDLE-orange" README.md || err "README.md badge != $BUNDLE"
  grep -q "version-$BUNDLE-orange" docs/README.zh.md || err "docs/README.zh.md badge != $BUNDLE"
  # Full version-lock over the localized README set (owner decision 2026-07-05):
  # every translated README carries the machine-checkable version badge AND a
  # current-bundle prose line — the [VERSIONS.md](…) link line must carry the
  # backticked bundle version and nothing stale (the v17 review found
  # translations whose badge was bumped while that line still claimed the
  # previous bundle); the remaining count words in prose are human-maintained.
  check_bundle_line() { # $1 file
    if ! grep -E "VERSIONS\.md\]" "$1" | grep -q "\`$BUNDLE\`"; then
      err "$1 VERSIONS.md current-bundle line != $BUNDLE"
    elif grep -E "VERSIONS\.md\]" "$1" | grep -oE '`[0-9]+\.[0-9]+(\.[0-9]+)?`' | grep -v "\`$BUNDLE\`" | grep -q .; then
      err "$1 VERSIONS.md line carries a non-current bundle version"
    fi
  }
  check_bundle_line README.md
  check_bundle_line docs/README.zh.md
  for lf in docs/README.de.md docs/README.es.md docs/README.fr.md docs/README.it.md \
            docs/README.ja.md docs/README.ko.md docs/README.pt.md docs/README.zh-Hant.md; do
    [ -f "$lf" ] || { err "$lf missing (localized README set is version-locked)"; continue; }
    grep -q "version-$BUNDLE-orange" "$lf" || err "$lf badge != $BUNDLE"
    check_bundle_line "$lf"
  done
  grep -q "current bundle: \`$BUNDLE\`" README.md || err "README.md 'current bundle' line != $BUNDLE"
  grep -q "当前包：\`$BUNDLE\`" docs/README.zh.md || err "docs/README.zh.md 当前包 line != $BUNDLE"
  grep -q "Current bundle version: \`$BUNDLE\`" CLAUDE.md || err "CLAUDE.md bundle declaration != $BUNDLE"
  grep -Fq -- "- **Current bundle**: $BUNDLE" AGENTS.md || err "AGENTS.md bundle declaration != $BUNDLE"
  grep -Fq -- "120 skills (16 × 7 disciplines + 8 protocol)" AGENTS.md || err "AGENTS.md skill shape is not 120 = 16 × 7 + 8"
  grep -Fq -- "8 commands" AGENTS.md || err "AGENTS.md command count is not 8"
  while IFS= read -r framework_contract; do
    grep -Fq -- "$framework_contract" AGENTS.md || err "AGENTS.md framework contract drift: $framework_contract"
  done <<'FRAMEWORKS'
**CORE-EEAT** (80 items, 8 dimensions)
**CITE** (40 items, 4 dimensions)
**STAR** (S Suitability / T Trust / A Appeal / R Return
**ROAS** (R Return / O Offer / A Audience / S Spend-efficiency
**SEND** (S Sender-integrity/deliverability / E Engagement / N Nurture-lifecycle / D Direct-response
**RAMP** (40 stable IDs across R Readiness / A Assets / M Momentum / P Proof
**ECHO** (40 stable IDs across E Embeddedness / C Craft / H Hosting / O Observability
**TALE** (T Truth / A Architecture / L Landing / E Evidence
FRAMEWORKS
  grep -q "^\*\*Current release\*\*: \`$BUNDLE\`" VERSIONS.md || err "VERSIONS.md 'Current release' line != $BUNDLE"
  grep -q "^### v$BUNDLE " VERSIONS.md || err "VERSIONS.md changelog entry '### v$BUNDLE …' missing"
  # openclaw.plugin.json is the OpenClaw bundle-plugin manifest (ClawHub package publish).
  # It carries the bundle version too — keep it in the version-lock so it can't drift.
  if [ -f openclaw.plugin.json ]; then
    grep -q "\"version\": \"$BUNDLE\"" openclaw.plugin.json || err "openclaw.plugin.json version != $BUNDLE"
  else
    err "openclaw.plugin.json missing — the OpenClaw bundle manifest is a locked surface"
  fi
fi

# ---- 2. per-skill sync ------------------------------------------------------
skill_count=0
for f in seo-geo/*/*/SKILL.md influencer/*/*/SKILL.md ad/*/*/SKILL.md \
         email/*/*/SKILL.md launch/*/*/SKILL.md social/*/*/SKILL.md \
         narrative/*/*/SKILL.md protocol/*/SKILL.md; do
  [ -f "$f" ] || continue
  skill_count=$((skill_count + 1))
  name=$(sed -n 's/^name: *//p' "$f" | head -1)
  top=$(sed -n 's/^version: *"\([0-9][0-9.]*\)".*/\1/p' "$f" | head -1)
  # metadata is a single-line JSON object (OpenClaw parser requirement) —
  # pull its "version" member off the metadata: line
  meta=$(sed -n 's/^metadata: .*"version": *"\([0-9][0-9.]*\)".*/\1/p' "$f" | head -1)
  if [ -z "$name" ] || [ -z "$top" ]; then
    err "$f: missing name or top-level version"
    continue
  fi
  [ "$top" = "$meta" ] || err "$f: version \"$top\" != metadata.version \"$meta\""
  rowver=$(awk -F'|' -v s=" $name " '$2 == s {gsub(/ /,"",$4); print $4; exit}' VERSIONS.md)
  if [ -z "$rowver" ]; then
    err "$name: no row in VERSIONS.md"
  elif [ "$rowver" != "$top" ]; then
    err "$name: SKILL.md $top != VERSIONS.md row $rowver"
  fi
done

# ---- 3. row count -----------------------------------------------------------
rows=$(grep -cE '^\| [a-z0-9-]+ \| [a-z-]+ \| [0-9][0-9.]* \| ' VERSIONS.md)
[ "$rows" -eq "$skill_count" ] || \
  err "VERSIONS.md has $rows skill rows but the tree has $skill_count skills"

# ---- 4. root + Chinese README topology/command surfaces --------------------
# CONTRIBUTING.md makes these overview tables and command inventories part of
# the authoritative tracking contract. Derive their expected shape from the
# typed catalog so a stale 16/8/120 count or missing command cannot hide behind
# a current version badge.
readme_contract_output=$(python3 - <<'PY'
import json
import re
import sys
from pathlib import Path

catalog = json.loads(Path("references/system-catalog.json").read_text(encoding="utf-8"))
commands = catalog["commands"]
discipline_commands = [command for command in commands if command != "auto"]
discipline_counts = {
    name: sum(len(skills) for skills in catalog["disciplines"][name]["phases"].values())
    for name in discipline_commands
}
protocol_count = len(catalog["protocol"]["skills"])
total_count = sum(discipline_counts.values()) + protocol_count
errors = []

def table_after(lines, header_fragment):
    try:
        start = next(index for index, line in enumerate(lines) if header_fragment in line)
    except StopIteration:
        return []
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) >= 5:
            rows.append(cells)
    return rows

for filename, header, headline in (
    ("README.md", "| Layer | Skills |", "**%d marketing skills" % total_count),
    ("docs/README.zh.md", "| 层 | 技能 |", "**%d 个营销技能" % total_count),
):
    text = Path(filename).read_text(encoding="utf-8")
    lines = text.splitlines()
    if headline not in text:
        errors.append("%s headline does not declare %d skills" % (filename, total_count))
    overview = table_after(lines, header)
    if len(overview) != len(discipline_commands) + 1:
        errors.append(
            "%s overview has %d rows; expected %d discipline/protocol rows"
            % (filename, len(overview), len(discipline_commands) + 1)
        )
    else:
        for position, command in enumerate(discipline_commands):
            cells = overview[position]
            expected_count = str(discipline_counts[command])
            expected_entry = chr(96) + "/aaron-marketing:%s" % command + chr(96)
            if cells[1] != expected_count or cells[4] != expected_entry:
                errors.append(
                    "%s overview row %d must carry %s skills and entrypoint %s"
                    % (filename, position + 1, expected_count, expected_entry)
                )
        protocol = overview[-1]
        if protocol[1] != str(protocol_count) or "/aaron-marketing:" in protocol[4]:
            errors.append(
                "%s protocol overview row must carry %d skills and no command"
                % (filename, protocol_count)
            )
    command_rows = re.findall(
        r"^\| \x60/aaron-marketing:([^\x60]+)\x60 \|", text, flags=re.MULTILINE
    )
    if len(command_rows) != len(commands) or set(command_rows) != set(commands):
        errors.append(
            "%s command table is %r; expected %r" % (filename, command_rows, commands)
        )

if errors:
    print("\n".join(errors))
    sys.exit(1)
PY
)
readme_contract_status=$?
if [ "$readme_contract_status" -ne 0 ]; then
  while IFS= read -r message; do
    [ -n "$message" ] && err "$message"
  done <<< "$readme_contract_output"
fi

# ---- 5. GitHub About SSOT tracks the skill count ----------------------------
# The repo About (sidebar description + topics) is not a versioned file, so it is
# invisible to the checks above and drifted on the v13/v14 bumps. Its SSOT is
# .github/repo-about.json; its description MUST lead with the current skill count.
# Offline assertion (no network — the live projection/verify is sync-about.sh +
# about-drift.yml): the leading integer of the description == skill_count.
ABOUT=".github/repo-about.json"
if [ ! -f "$ABOUT" ]; then
  err "$ABOUT missing — the GitHub About SSOT (see scripts/sync-about.sh)"
else
  about_n=$(python3 - "$ABOUT" <<'PY' 2>/dev/null
import json, re, sys
with open(sys.argv[1], encoding="utf-8") as handle:
    value = json.load(handle)
description = value.get("description")
match = re.match(r"([0-9]+)\b", description) if isinstance(description, str) else None
if match:
    print(match.group(1))
PY
)
  if [ -z "$about_n" ]; then
    err "$ABOUT: description must lead with the skill count (so this check can read it)"
  elif [ "$about_n" != "$skill_count" ]; then
    err "$ABOUT says $about_n skills but the tree has $skill_count — update it, then run: bash scripts/sync-about.sh --live"
  fi
fi

# ---- 6. auto-routing scenarios cover every command discipline ---------------
# references/auto-routing-scenarios.md is the runtime routing data commands/auto.md
# consults. It silently froze at the v12 four-discipline era (launch/social/narrative
# shipped with ZERO expected_route scenarios) — assert every command discipline keeps
# at least one routing scenario so a new discipline cannot ship uncovered again.
# The discipline list is derived from the typed catalog so an 8th discipline
# extends these guards automatically instead of silently skipping them.
DISCIPLINES=$(python3 - <<'PY'
import json
with open("references/system-catalog.json", encoding="utf-8") as handle:
    catalog = json.load(handle)
print(" ".join(sorted(catalog["disciplines"])))
PY
)
if [ -z "$DISCIPLINES" ]; then
  err "cannot derive discipline list from references/system-catalog.json"
fi
DISC_COUNT=$(wc -w <<< "$DISCIPLINES" | tr -d ' ')
ROUTING="references/auto-routing-scenarios.md"
if [ ! -f "$ROUTING" ]; then
  err "$ROUTING missing — the /aaron-marketing:auto routing contract"
else
  for cmd in $DISCIPLINES; do
    grep -q "expected_route: \"/aaron-marketing:$cmd" "$ROUTING" \
      || err "$ROUTING has no expected_route scenario for /aaron-marketing:$cmd (auto routing coverage gap)"
  done
fi

# ---- 7. every discipline command Route names all its own skills -------------
# commands/<disc>.md is the human-facing skill catalog for its discipline. ad.md
# and email.md once listed only 2 of 4 skills per phase (and ad.md's Rules even
# claimed 3 real skills were "not separate skills"). Assert every skill physically
# under a discipline dir is named in that discipline's command, so a new skill
# cannot ship unlisted. (Protocol skills have no dedicated command — exempt.)
for disc in $DISCIPLINES; do
  cmd="commands/$disc.md"
  if [ ! -f "$cmd" ]; then err "$cmd missing — the $disc command"; continue; fi
  while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    grep -qw "$skill" "$cmd" \
      || err "$cmd Route does not name skill '$skill' (command coverage gap)"
  done < <(find "$disc" -name SKILL.md 2>/dev/null | sed 's#/SKILL.md##; s#.*/##' | sort -u)
done

# ---- 8. per-discipline README guides + CLAUDE.md name every discipline skill -
# <disc>/README.md(.zh.md) are self-contained discipline catalogs (linked from
# the root README as "Discipline guide") and CLAUDE.md carries the master phase
# tables; none are machine-generated, so assert every skill physically under a
# discipline dir is named in all of them. Guides carry no version badge by
# design — coverage, not version, is the locked surface here.
for disc in $DISCIPLINES; do
  for guide in "$disc/README.md" "$disc/README.zh.md"; do
    if [ ! -f "$guide" ]; then err "$guide missing — the $disc discipline guide"; continue; fi
    while IFS= read -r skill; do
      [ -n "$skill" ] || continue
      grep -qw "$skill" "$guide" \
        || err "$guide does not name skill '$skill' (guide coverage gap)"
    done < <(find "$disc" -name SKILL.md 2>/dev/null | sed 's#/SKILL.md##; s#.*/##' | sort -u)
  done
done
while IFS= read -r skill; do
  [ -n "$skill" ] || continue
  grep -qw "$skill" CLAUDE.md || err "CLAUDE.md does not name skill '$skill' (catalog rot)"
done < <(find $DISCIPLINES protocol -name SKILL.md 2>/dev/null | sed 's#/SKILL.md##; s#.*/##' | sort -u)

if [ $fail -eq 0 ]; then
  echo "version-sync clean — bundle $BUNDLE, $skill_count skills consistent across the 10 tracking surfaces + README topology/commands + localized badges + OpenClaw manifest + About SSOT; auto-routing covers all $DISC_COUNT disciplines; every discipline command, guide pair, and the CLAUDE.md catalog list their full skill sets"
fi
exit $fail
