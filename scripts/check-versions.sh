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
#   3. VERSIONS.md has exactly one row per catalog skill target, none extra.
#   4. The GitHub About SSOT (.github/repo-about.json) leads with the current
#      skill count — the About is not a versioned file, so it silently drifted
#      on the v13/v14 discipline bumps; this keeps its count honest offline, and
#      scripts/sync-about.sh + about-drift.yml handle projecting/verifying it on GitHub.
#   5. SECURITY.md names the bundle major as the only supported major line and
#      marks every earlier major unsupported. This is a release-policy guard,
#      not an additional skill-authoring tracking surface.
#   6. Live Portable Lite install rows (README / localized READMEs /
#      docs/agent-compatibility.md / registry-submissions / SECURITY.md) that
#      hardcode `aaron-marketing-skills-<ver>-agent-plugin-v1-lite.tar.gz` must
#      name the current bundle, not a prior release tag.
#
# ``--release-all-current`` adds the coordinated-major-release invariant:
# exactly 120 unique skills must all equal the bundle version and every
# VERSIONS.md row must carry the Current release date. Normal no-argument mode
# deliberately keeps per-skill patch skew legal between bundle releases.
#
# Bash plus Python stdlib JSON parsing (repo dependency policy). Exit 0 clean, 1 on any
# mismatch, with one FAIL line per finding. Invalid CLI usage exits 2.

set -u

RELEASE_ALL_CURRENT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --release-all-current)
      if [ "$RELEASE_ALL_CURRENT" -eq 1 ]; then
        echo "usage: scripts/check-versions.sh [--release-all-current]" >&2
        exit 2
      fi
      RELEASE_ALL_CURRENT=1
      ;;
    -h|--help)
      echo "usage: scripts/check-versions.sh [--release-all-current]"
      exit 0
      ;;
    *)
      echo "usage: scripts/check-versions.sh [--release-all-current]" >&2
      exit 2
      ;;
  esac
  shift
done

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
  # SECURITY.md intentionally tracks the supported major, not every point
  # release. Parse the table fail-closed so a missing row, duplicate row, or
  # stale unsupported boundary cannot silently pass.
  bundle_major=${BUNDLE%%.*}
  if [ ! -f SECURITY.md ]; then
    err "SECURITY.md missing — supported-version policy cannot be verified"
  else
    security_current=$(sed -n 's/^| *\([0-9][0-9]*\)\.x *| *Yes (current line) *|$/\1/p' SECURITY.md)
    security_unsupported=$(sed -n 's/^| *< *\([0-9][0-9]*\) *| *No *|$/\1/p' SECURITY.md)
    [ "$security_current" = "$bundle_major" ] || \
      err "SECURITY.md current supported major ${security_current:-missing} != bundle major $bundle_major"
    [ "$security_unsupported" = "$bundle_major" ] || \
      err "SECURITY.md unsupported boundary ${security_unsupported:-missing} != bundle major $bundle_major"
  fi
  # openclaw.plugin.json is the OpenClaw bundle-plugin manifest (ClawHub package publish).
  # It carries the bundle version too — keep it in the version-lock so it can't drift.
  if [ -f openclaw.plugin.json ]; then
    grep -q "\"version\": \"$BUNDLE\"" openclaw.plugin.json || err "openclaw.plugin.json version != $BUNDLE"
  else
    err "openclaw.plugin.json missing — the OpenClaw bundle manifest is a locked surface"
  fi
  # Portable Lite install rows must name the current release asset, not a
  # prior tag. Historical changelog (VERSIONS.md) may mention older asset
  # names; this guard only covers the live install surfaces. A file that
  # never names a versioned lite tarball is skipped so fixtures stay valid.
  check_portable_lite_asset() {
    local f="$1" found stale
    [ -f "$f" ] || return 0
    found=$(grep -oE 'aaron-marketing-skills-[0-9]+\.[0-9]+\.[0-9]+-agent-plugin-v1-lite\.tar\.gz' "$f" || true)
    [ -n "$found" ] || return 0
    stale=$(printf '%s\n' "$found" | grep -Fvx "aaron-marketing-skills-$BUNDLE-agent-plugin-v1-lite.tar.gz" || true)
    if [ -n "$stale" ]; then
      err "$f names a stale Portable Lite asset (want $BUNDLE): $(printf '%s' "$stale" | tr '\n' ' ')"
    fi
    if grep -E 'aaron-marketing-skills-[0-9.]+-agent-plugin-v1-lite\.tar\.gz' "$f" \
         | grep -E 'releases/tag/v[0-9]+\.[0-9]+\.[0-9]+' \
         | grep -v "releases/tag/v$BUNDLE" | grep -q .; then
      err "$f Portable Lite release URL != v$BUNDLE"
    fi
  }
  check_portable_lite_asset README.md
  check_portable_lite_asset docs/agent-compatibility.md
  check_portable_lite_asset docs/registry-submissions.md
  check_portable_lite_asset SECURITY.md
  for lf in docs/README.zh.md docs/README.de.md docs/README.es.md docs/README.fr.md \
            docs/README.it.md docs/README.ja.md docs/README.ko.md docs/README.pt.md \
            docs/README.zh-Hant.md; do
    check_portable_lite_asset "$lf"
  done
fi

# ---- 2. catalog-derived product inventory + per-skill sync ------------------
# The typed system catalog is the product inventory. Never discover release
# targets by walking for arbitrary SKILL.md files: examples, fixtures, or local
# experiments may use the same filename without becoming one of the 120
# products. Fail closed on unsafe, duplicate, or missing catalog targets.
catalog_skill_output=$(python3 - <<'PY'
import collections
import json
from pathlib import Path
import re
import stat
import sys

errors = []
try:
    catalog = json.loads(
        Path("references/system-catalog.json").read_text(encoding="utf-8")
    )
except (OSError, ValueError) as exc:
    print("cannot read typed skill inventory: %s" % exc)
    sys.exit(1)

disciplines = catalog.get("disciplines")
protocol = catalog.get("protocol")
if not isinstance(disciplines, dict) or not isinstance(protocol, dict):
    print("typed skill inventory requires disciplines and protocol objects")
    sys.exit(1)

component = re.compile(r"^[a-z0-9][a-z0-9-]*$")
targets = []
skill_ids = []
for discipline, specification in disciplines.items():
    if (
            not isinstance(discipline, str)
            or not component.fullmatch(discipline)
            or discipline == "protocol"):
        errors.append("catalog discipline is not a canonical path component: %r" % discipline)
        continue
    if not isinstance(specification, dict):
        errors.append("catalog discipline %s must be an object" % discipline)
        continue
    phase_order = specification.get("phase_order")
    phases = specification.get("phases")
    if (
            not isinstance(phase_order, list)
            or not phase_order
            or not isinstance(phases, dict)
            or any(not isinstance(phase, str) for phase in phase_order)
            or len(phase_order) != len(set(phase_order))
            or set(phase_order) != set(phases)):
        errors.append(
            "catalog discipline %s phase_order must uniquely and exactly name phases"
            % discipline
        )
        continue
    for phase in phase_order:
        if not isinstance(phase, str) or not component.fullmatch(phase):
            errors.append(
                "catalog phase is not a canonical path component: %s/%r"
                % (discipline, phase)
            )
            continue
        skills = phases.get(phase)
        if not isinstance(skills, list):
            errors.append("catalog phase %s/%s must contain a skill list" % (discipline, phase))
            continue
        for skill in skills:
            if not isinstance(skill, str) or not component.fullmatch(skill):
                errors.append(
                    "catalog skill is not a canonical path component: %s/%s/%r"
                    % (discipline, phase, skill)
                )
                continue
            skill_ids.append(skill)
            targets.append("%s/%s/%s/SKILL.md" % (discipline, phase, skill))

protocol_skills = protocol.get("skills")
if not isinstance(protocol_skills, list):
    errors.append("catalog protocol.skills must contain a skill list")
else:
    for skill in protocol_skills:
        if not isinstance(skill, str) or not component.fullmatch(skill):
            errors.append("catalog protocol skill is not canonical: %r" % skill)
            continue
        skill_ids.append(skill)
        targets.append("protocol/%s/SKILL.md" % skill)

duplicate_targets = sorted(
    target for target, count in collections.Counter(targets).items() if count != 1
)
if duplicate_targets:
    errors.append("catalog has duplicate skill targets: %s" % ", ".join(duplicate_targets))
duplicate_ids = sorted(
    skill for skill, count in collections.Counter(skill_ids).items() if count != 1
)
if duplicate_ids:
    errors.append("catalog has duplicate skill IDs: %s" % ", ".join(duplicate_ids))

for relative in targets:
    path = Path(relative)
    try:
        status = path.lstat()
    except OSError:
        errors.append("catalog target is missing: %s" % relative)
        continue
    if stat.S_ISLNK(status.st_mode) or not stat.S_ISREG(status.st_mode):
        errors.append("catalog target must be a real regular file: %s" % relative)

if errors:
    print("\n".join(errors))
    sys.exit(1)
print("\n".join(targets))
PY
)
catalog_skill_status=$?
if [ "$catalog_skill_status" -ne 0 ]; then
  while IFS= read -r message; do
    [ -n "$message" ] && err "$message"
  done <<< "$catalog_skill_output"
  CATALOG_SKILL_FILES=""
else
  CATALOG_SKILL_FILES="$catalog_skill_output"
fi

skill_count=0
while IFS= read -r f; do
  [ -n "$f" ] || continue
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
done <<< "$CATALOG_SKILL_FILES"

# ---- 3. row count -----------------------------------------------------------
rows=$(grep -cE '^\| [a-z0-9-]+ \| [a-z-]+ \| [0-9][0-9.]* \| ' VERSIONS.md)
[ "$rows" -eq "$skill_count" ] || \
  err "VERSIONS.md has $rows skill rows but the catalog has $skill_count skill targets"

# ---- 3a. coordinated release cohort ----------------------------------------
# The normal guard intentionally permits per-skill patch versions. A major
# release that promises all 120 skills moved together needs a stronger,
# explicitly requested gate. Keep this parser separate so daily patch releases
# do not accidentally inherit the all-current/date constraint.
if [ "$RELEASE_ALL_CURRENT" -eq 1 ] && [ -n "$BUNDLE" ]; then
  release_output=$(BUNDLE="$BUNDLE" CATALOG_SKILL_FILES="$CATALOG_SKILL_FILES" python3 - <<'PY'
import collections
import datetime
import json
import os
from pathlib import Path
import re
import sys

bundle = os.environ["BUNDLE"]
errors = []
versions_path = Path("VERSIONS.md")
try:
    versions_text = versions_path.read_text(encoding="utf-8")
except OSError as exc:
    print("release-all-current cannot read VERSIONS.md: %s" % exc)
    sys.exit(1)

current_match = re.search(
    r"^\*\*Current release\*\*: \x60([^\x60]+)\x60 "
    r"\((\d{4}-\d{2}-\d{2})\)(?:\.|$)",
    versions_text,
    flags=re.MULTILINE,
)
release_date = None
if current_match is None:
    errors.append(
        "release-all-current requires Current release to include an ISO date"
    )
else:
    current_version, release_date = current_match.groups()
    if current_version != bundle:
        errors.append(
            "release-all-current Current release %s != bundle %s"
            % (current_version, bundle)
        )
    try:
        datetime.date.fromisoformat(release_date)
    except ValueError:
        errors.append(
            "release-all-current Current release date is invalid: %s" % release_date
        )

row_pattern = re.compile(
    r"^\| ([a-z0-9-]+) \| ([a-z-]+) \| "
    r"([0-9]+\.[0-9]+\.[0-9]+) \| (\d{4}-\d{2}-\d{2}) \|$",
    flags=re.MULTILINE,
)
rows = row_pattern.findall(versions_text)
row_counts = collections.Counter(row[0] for row in rows)
row_by_name = {row[0]: row for row in rows}
if len(rows) != 120:
    errors.append(
        "release-all-current requires exactly 120 VERSIONS.md rows; found %d"
        % len(rows)
    )
for row_name, _category, _version, row_date in rows:
    try:
        datetime.date.fromisoformat(row_date)
    except ValueError:
        errors.append(
            "release-all-current %s has an invalid date: %s" % (row_name, row_date)
        )
duplicates = sorted(name for name, count in row_counts.items() if count != 1)
if duplicates:
    errors.append(
        "release-all-current VERSIONS.md has duplicate skill rows: %s"
        % ", ".join(duplicates)
    )

skill_paths = [
    Path(relative)
    for relative in os.environ.get("CATALOG_SKILL_FILES", "").splitlines()
    if relative
]
if len(skill_paths) != 120:
    errors.append(
        "release-all-current requires exactly 120 catalog skill targets; found %d"
        % len(skill_paths)
    )

skill_names = []
for path in skill_paths:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append("release-all-current cannot read %s: %s" % (path, exc))
        continue
    name_match = re.search(r"^name: *([a-z0-9-]+) *$", text, flags=re.MULTILINE)
    top_match = re.search(
        r'^version: *"([0-9]+\.[0-9]+\.[0-9]+)" *$',
        text,
        flags=re.MULTILINE,
    )
    metadata_match = re.search(r"^metadata: *(.+)$", text, flags=re.MULTILINE)
    if name_match is None or top_match is None or metadata_match is None:
        errors.append(
            "release-all-current %s lacks a parseable name/version/metadata line"
            % path
        )
        continue
    name = name_match.group(1)
    top_version = top_match.group(1)
    skill_names.append(name)
    try:
        metadata = json.loads(metadata_match.group(1))
        metadata_version = metadata.get("version")
    except (ValueError, AttributeError):
        metadata_version = None
    if top_version != bundle:
        errors.append(
            "release-all-current %s top-level version %s != bundle %s"
            % (name, top_version, bundle)
        )
    if metadata_version != bundle:
        errors.append(
            "release-all-current %s metadata.version %r != bundle %s"
            % (name, metadata_version, bundle)
        )
    row = row_by_name.get(name)
    if row is None:
        errors.append("release-all-current %s has no VERSIONS.md row" % name)
        continue
    row_version, row_date = row[2], row[3]
    if row_version != bundle:
        errors.append(
            "release-all-current %s VERSIONS.md version %s != bundle %s"
            % (name, row_version, bundle)
        )
    if release_date is not None and row_date != release_date:
        errors.append(
            "release-all-current %s date %s != release date %s"
            % (name, row_date, release_date)
        )

name_counts = collections.Counter(skill_names)
duplicate_skills = sorted(name for name, count in name_counts.items() if count != 1)
if duplicate_skills:
    errors.append(
        "release-all-current has duplicate SKILL.md names: %s"
        % ", ".join(duplicate_skills)
    )
extra_rows = sorted(set(row_by_name) - set(skill_names))
if extra_rows:
    errors.append(
        "release-all-current VERSIONS.md has non-skill rows: %s"
        % ", ".join(extra_rows)
    )

if errors:
    print("\n".join(errors))
    sys.exit(1)
PY
)
  release_status=$?
  if [ "$release_status" -ne 0 ]; then
    if [ -z "$release_output" ]; then
      err "release-all-current validation failed without diagnostics"
    fi
    while IFS= read -r message; do
      [ -n "$message" ] && err "$message"
    done <<< "$release_output"
  fi
fi

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
    err "$ABOUT says $about_n skills but the catalog has $skill_count — update it, then run: bash scripts/sync-about.sh --live"
  fi
fi

# ---- 6. auto-routing scenarios cover every command discipline ---------------
# evals/auto-routing-scenarios.source.md is the one authoritative case corpus;
# the runtime index/shards are generated from it. It silently froze at the v12
# four-discipline era (launch/social/narrative shipped with ZERO expected_route
# scenarios) — assert every command discipline keeps at least one routing case.
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
ROUTING="evals/auto-routing-scenarios.source.md"
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
# claimed 3 real skills were "not separate skills"). Assert every catalog skill
# in a discipline is named in that discipline's command, so a new product skill
# cannot ship unlisted. (Protocol skills have no dedicated command — exempt.)
for disc in $DISCIPLINES; do
  cmd="commands/$disc.md"
  if [ ! -f "$cmd" ]; then err "$cmd missing — the $disc command"; continue; fi
  while IFS= read -r skill; do
    [ -n "$skill" ] || continue
    grep -qw "$skill" "$cmd" \
      || err "$cmd Route does not name skill '$skill' (command coverage gap)"
  done < <(
    printf '%s\n' "$CATALOG_SKILL_FILES" |
      awk -F/ -v discipline="$disc" '$1 == discipline {print $(NF-1)}' |
      sort -u
  )
done

# ---- 8. per-discipline README guides + CLAUDE.md name every discipline skill -
# <disc>/README.md(.zh.md) are self-contained discipline catalogs (linked from
# the root README as "Discipline guide") and CLAUDE.md carries the master phase
# tables; none are machine-generated, so assert every catalog skill in a
# discipline is named in all of them. Guides carry no version badge by
# design — coverage, not version, is the locked surface here.
for disc in $DISCIPLINES; do
  for guide in "$disc/README.md" "$disc/README.zh.md"; do
    if [ ! -f "$guide" ]; then err "$guide missing — the $disc discipline guide"; continue; fi
    while IFS= read -r skill; do
      [ -n "$skill" ] || continue
      grep -qw "$skill" "$guide" \
        || err "$guide does not name skill '$skill' (guide coverage gap)"
    done < <(
      printf '%s\n' "$CATALOG_SKILL_FILES" |
        awk -F/ -v discipline="$disc" '$1 == discipline {print $(NF-1)}' |
        sort -u
    )
  done
done
while IFS= read -r skill; do
  [ -n "$skill" ] || continue
  grep -qw "$skill" CLAUDE.md || err "CLAUDE.md does not name skill '$skill' (catalog rot)"
done < <(
  printf '%s\n' "$CATALOG_SKILL_FILES" |
    awk -F/ '{print $(NF-1)}' |
    sort -u
)

if [ $fail -eq 0 ]; then
  release_note=""
  if [ "$RELEASE_ALL_CURRENT" -eq 1 ]; then
    release_note="; release-all-current cohort is exactly 120/120"
  fi
  echo "version-sync clean — bundle $BUNDLE, $skill_count skills consistent across the 10 tracking surfaces + SECURITY support policy + README topology/commands + localized badges + OpenClaw manifest + About SSOT; auto-routing covers all $DISC_COUNT disciplines; every discipline command, guide pair, and the CLAUDE.md catalog list their full skill sets$release_note"
fi
exit $fail
