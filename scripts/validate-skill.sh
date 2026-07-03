#!/usr/bin/env bash
# validate-skill.sh — Validate a SKILL.md against the Agent Skills spec (frontmatter, shared contract, termination)
# Required frontmatter (FAIL if missing): name, version, description, license, compatibility, metadata.
# Recommended frontmatter (WARN if missing): when_to_use (underscores — `when-to-use` is a FAIL), argument-hint.
# blob/main GitHub URL ban covers SKILL.md AND every .md under the skill's references/.
# Usage: ./scripts/validate-skill.sh <path-to-skill-directory>
# Example: ./scripts/validate-skill.sh research/keyword-research

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# --status: verify version: == metadata.version: within each SKILL.md (internal consistency)
#           and display library version from plugin.json and marketplace.json for reference
if [ "$1" = "--status" ]; then
    REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
    PLUGIN_JSON="$REPO_ROOT/.claude-plugin/plugin.json"
    MARKETPLACE_JSON="$REPO_ROOT/marketplace.json"

    if [ ! -f "$PLUGIN_JSON" ]; then
        echo -e "${RED}ERROR${NC}: plugin.json not found at $PLUGIN_JSON"
        exit 1
    fi
    if [ ! -f "$MARKETPLACE_JSON" ]; then
        echo -e "${RED}ERROR${NC}: marketplace.json not found at $MARKETPLACE_JSON"
        exit 1
    fi

    # Library-level version (single entry in plugin.json / marketplace.json)
    lib_plugin=$(grep '"version"' "$PLUGIN_JSON" | head -1 | sed 's/.*"version" *: *"//' | sed 's/".*//' | tr -d '\r')
    lib_market=$(grep '"version"' "$MARKETPLACE_JSON" | head -1 | sed 's/.*"version" *: *"//' | sed 's/".*//' | tr -d '\r')
    echo ""
    echo "Library version — plugin.json: ${lib_plugin}  marketplace.json: ${lib_market}"
    if [ "$lib_plugin" != "$lib_market" ]; then
        echo -e "${RED}WARN${NC}: plugin.json and marketplace.json library versions differ"
    fi
    echo ""

    SPLIT=0

    printf "%-30s %-12s %-18s %s\n" "SKILL" "version:" "metadata.version:" "STATUS"
    printf "%-30s %-12s %-18s %s\n" "-----" "--------" "-----------------" "------"

    while IFS= read -r skill_file; do
        skill_dir="$(dirname "$skill_file")"
        skill_name="$(basename "$skill_dir")"

        # Extract top-level version: from SKILL.md frontmatter
        skill_ver=$(awk '/^---/{if(++n==2)exit} n && /^version:/{gsub(/version: */, ""); gsub(/["'"'"']/, ""); print; exit}' "$skill_file" | tr -d '\r')

        # Extract metadata.version: (indented) from SKILL.md frontmatter
        meta_ver=$(awk '/^---/{if(++n==2)exit} n && /^  version:/{gsub(/ *version: */, ""); gsub(/["'"'"']/, ""); print; exit}' "$skill_file" | tr -d '\r')

        # Determine status
        if [ -z "$skill_ver" ]; then
            status="${RED}MISSING${NC}"
            SPLIT=1
        elif [ -z "$meta_ver" ]; then
            status="${RED}MISSING${NC}"
            SPLIT=1
        elif [ "$skill_ver" = "$meta_ver" ]; then
            status="${GREEN}OK${NC}"
        else
            status="${RED}SPLIT${NC}"  # version: and metadata.version: disagree within SKILL.md
            SPLIT=1
        fi

        printf "%-30s %-12s %-18s " "$skill_name" "${skill_ver:-—}" "${meta_ver:-—}"
        echo -e "$status"
    done < <(find "$REPO_ROOT" -name "SKILL.md" -not -path "$REPO_ROOT/docs/*" -not -path "$REPO_ROOT/.claude/*" -not -path "$REPO_ROOT/reference-oss/*" | sort)

    echo ""
    # Regression guard: the bundle version string must never appear glued to a numeric
    # threshold unit (a past release-bump sed replaced the literal "10,000" with the
    # version string across rubric thresholds). Legitimate version mentions never look like
    # "9.9.10/mo" or "9.9.10px". (A bare trailing "+" — e.g. a "requires 9.9.10+" compat
    # note — is intentionally NOT flagged; only unit-glued forms are.)
    CORRUPT=$(grep -rnE "${lib_plugin//./\\.}[0-9]*[[:space:]]*(/mo|px|visits|domains|estimated)" "$REPO_ROOT" --include='*.md' 2>/dev/null | grep -vE '/\.git/' | head -5)
    if [ -n "$CORRUPT" ]; then
        echo -e "${RED}CORRUPTION${NC}: bundle version string glued to a numeric threshold (release-bump likely clobbered a real number):"
        echo "$CORRUPT"
        SPLIT=1
    fi

    echo ""
    if [ "$SPLIT" -gt 0 ]; then
        echo -e "${RED}SPLIT/CORRUPTION detected — fix before release${NC}"
        exit 1
    else
        echo -e "${GREEN}All skill versions internally consistent; no threshold corruption${NC}"
        exit 0
    fi
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_DIR="${1:-.}"
SKILL_FILE="$SKILL_DIR/SKILL.md"

PASS=0
FAIL=0
WARN=0

pass() { echo -e "${GREEN}  ✅ PASS${NC}: $1"; PASS=$((PASS + 1)); }
fail() { echo -e "${RED}  ❌ FAIL${NC}: $1"; FAIL=$((FAIL + 1)); }
warn() { echo -e "${YELLOW}  ⚠️  WARN${NC}: $1"; WARN=$((WARN + 1)); }

echo ""
echo "Validating: $SKILL_FILE"
echo "Spec: Agent Skills (frontmatter + shared contract)"
echo "=============================================="

# Check file exists
if [ ! -f "$SKILL_FILE" ]; then
    echo -e "${RED}ERROR${NC}: SKILL.md not found at $SKILL_FILE"
    exit 1
fi

# Extract frontmatter (between first --- and second ---)
FRONTMATTER=$(awk '/^---/{if(++n==2)exit} n' "$SKILL_FILE")

# --- Required field: name ---
# Agent Skills: lowercase, hyphens, ≤64 chars, matches dir name
NAME=$(echo "$FRONTMATTER" | grep -E '^name:' | sed 's/name: *//' | tr -d '"'"'" | tr -d '\r')
if [ -z "$NAME" ]; then
    fail "Missing required field: name"
else
    # Agent Skills: must start with letter
    if echo "$NAME" | grep -qE '^[a-z][a-z0-9-]*[a-z0-9]$' || echo "$NAME" | grep -qE '^[a-z]$'; then
        if echo "$NAME" | grep -q '\-\-'; then
            fail "name contains consecutive hyphens: $NAME"
        elif [ ${#NAME} -gt 64 ]; then
            fail "name exceeds 64 chars: ${#NAME} chars"
        else
            pass "name is valid: $NAME"
        fi
    else
        fail "name must be lowercase letters, numbers, hyphens only (got: $NAME)"
    fi

    # Check name matches directory
    DIR_NAME=$(basename "$SKILL_DIR")
    if [ "$NAME" != "$DIR_NAME" ]; then
        fail "name '$NAME' does not match directory '$DIR_NAME'"
    else
        pass "name matches directory name"
    fi
fi

# --- Required field: version ---
VERSION=$(echo "$FRONTMATTER" | grep -E '^version:' | sed 's/version: *//' | tr -d '"'"'" | tr -d '\r')
if [ -z "$VERSION" ]; then
    fail "Missing required field: version"
elif echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9]+)?$'; then
    pass "version is valid semver-like value: $VERSION"
else
    fail "version must be semver-like (got: $VERSION)"
fi

# --- Required field: description ---
DESCRIPTION=$(echo "$FRONTMATTER" | grep -E '^description:' | sed "s/description: *//")
if [ -z "$DESCRIPTION" ]; then
    fail "Missing required field: description"
else
    DESC_LEN=${#DESCRIPTION}
    if [ "$DESC_LEN" -gt 1024 ]; then
        fail "description exceeds 1024 chars: $DESC_LEN chars"
    elif [ "$DESC_LEN" -lt 10 ]; then
        fail "description too short: $DESC_LEN chars"
    else
        pass "description is valid ($DESC_LEN chars)"
    fi

    # Check for trigger phrases pattern
    if echo "$DESCRIPTION" | grep -qiE '"[^"]+"|Use when'; then
        pass "description contains trigger phrases"
    else
        warn "description should include trigger phrases (e.g., 'Use when the user asks to \"...\"')"
    fi
fi

# --- Required field: license ---
if echo "$FRONTMATTER" | grep -qE '^license:'; then
    LICENSE=$(echo "$FRONTMATTER" | grep -E '^license:' | sed 's/license: *//')
    pass "license present: $LICENSE"
else
    fail "Missing required field: license"
fi

# --- Required field: compatibility ---
if echo "$FRONTMATTER" | grep -qE '^compatibility:'; then
    pass "compatibility field present"
else
    fail "Missing required field: compatibility"
fi

# --- Required field: metadata ---
if echo "$FRONTMATTER" | grep -qE '^metadata:'; then
    pass "metadata block present"
    if echo "$FRONTMATTER" | grep -qE '  author:'; then
        pass "metadata.author present"
    else
        warn "metadata.author not found"
    fi
    if echo "$FRONTMATTER" | grep -qE '  version:'; then
        pass "metadata.version present"
    else
        warn "metadata.version not found"
    fi
else
    fail "Missing required field: metadata"
fi

# --- Recommended field: when_to_use (key spelling enforced: underscores, not hyphens) ---
if echo "$FRONTMATTER" | grep -qE '^when-to-use:'; then
    fail "frontmatter key must be 'when_to_use' (underscores), not 'when-to-use' (hyphens)"
elif echo "$FRONTMATTER" | grep -qE '^when_to_use:'; then
    pass "when_to_use present (correct underscore key)"
else
    warn "Missing recommended field: when_to_use"
fi

# --- Recommended field: argument-hint ---
if echo "$FRONTMATTER" | grep -qE '^argument-hint:'; then
    pass "argument-hint present"
else
    warn "Missing recommended field: argument-hint"
fi

# --- Body length advisory ---
BODY_LINES=$(awk 'BEGIN{n=0} /^---/{n++; next} n>=2{print}' "$SKILL_FILE" | wc -l | tr -d ' ')
IS_AUDITOR=$(echo "$FRONTMATTER" | grep -qE '^class: *auditor' && echo "yes" || echo "no")
# Influencer (IMPACT) skills intentionally inline their step matrices rather than
# extracting to references/ (see CLAUDE.md Contribution Rules); exempt them from the
# >250-line references/ advisory by phase directory.
PHASE_DIR=$(basename "$(dirname "$SKILL_DIR")")
case "$PHASE_DIR" in discover|plan|activate|measure) IS_INFLUENCER="yes";; *) IS_INFLUENCER="no";; esac

if [ "$IS_AUDITOR" = "yes" ]; then
    pass "Auditor skill reads the shared runbook + keeps framework-specific examples inline ($BODY_LINES lines)"
elif [ "$IS_INFLUENCER" = "yes" ] && [ "$BODY_LINES" -gt 250 ] && [ ! -d "$SKILL_DIR/references" ]; then
    pass "Influencer (IMPACT) skill intentionally inlines its step matrices ($BODY_LINES lines) — see CLAUDE.md"
elif [ "$BODY_LINES" -gt 250 ] && [ ! -d "$SKILL_DIR/references" ]; then
    warn "Skill body is $BODY_LINES lines but no references/ directory found. Consider extracting detailed tables/rubrics."
else
    pass "Skill body length OK: $BODY_LINES lines"
fi

# --- Eval coverage advisory (non-fatal) ---
if [ -n "$NAME" ] && [ -f "$REPO_ROOT/evals/$NAME/cases.md" ]; then
    pass "eval cases present: evals/$NAME/cases.md"
elif [ -n "$NAME" ]; then
    warn "no eval cases at evals/$NAME/cases.md — add a simulated seed case (see evals/README.md)"
fi

# --- Shared contract section checks ---
REQUIRED_HEADINGS=(
    "## Quick Start"
    "## Skill Contract"
    "## Data Sources"
    "## Instructions"
    "## Reference Materials"
    "## Next Best Skill"
)

for heading in "${REQUIRED_HEADINGS[@]}"; do
    if grep -Fxq "$heading" "$SKILL_FILE"; then
        pass "shared contract heading present: $heading"
    else
        fail "Missing shared contract heading: $heading"
    fi
done

if grep -Fxq "### Handoff Summary" "$SKILL_FILE"; then
    pass "shared contract handoff heading present: ### Handoff Summary"
elif [ "$IS_AUDITOR" = "yes" ] && grep -q "auditor-runbook.md" "$SKILL_FILE"; then
    pass "auditor references the runbook handoff schema (auditor-runbook.md)"
else
    fail "Missing shared contract handoff section: ### Handoff Summary"
fi

if [ "$IS_AUDITOR" = "yes" ]; then
    if grep -Fxq "## When This Must Trigger" "$SKILL_FILE"; then
        pass "auditor heading present: ## When This Must Trigger"
    else
        fail "Auditor skill missing heading: ## When This Must Trigger"
    fi
    if grep -Fxq "## Validation Checkpoints" "$SKILL_FILE"; then
        pass "auditor heading present: ## Validation Checkpoints"
    else
        fail "Auditor skill missing heading: ## Validation Checkpoints"
    fi
fi

# --- Next Best Skill termination contract ---
NEXT_BEST_BLOCK=$(awk 'found && /^## /{exit} found{print} /^## Next Best Skill$/{found=1}' "$SKILL_FILE")
if [ -z "$NEXT_BEST_BLOCK" ]; then
    fail "Next Best Skill block is empty"
elif echo "$NEXT_BEST_BLOCK" | grep -qiE 'visited-set|chain-complete|terminal|verdict|max-depth|stop|BLOCK|SHIP|TRUSTED|CAUTIOUS|UNTRUSTED|FIX'; then
    pass "Next Best Skill block has explicit termination or branching language"
elif grep -q "Global default termination rule applies to every Next Best Skill block" "$REPO_ROOT/references/skill-contract.md"; then
    pass "Next Best Skill block inherits global visited-set/max-depth termination contract"
else
    fail "Next Best Skill block lacks termination language and no global default contract was found"
fi

# --- Regression guard: runtime files must use relative links, not blob/main URLs ---
# (A skill that WebFetches GitHub HTML instead of Reading the installed file breaks
#  version pinning and offline use. Human-facing docs may still use absolute URLs.)
# Documented rule covers SKILL.md AND references/ — scan both.
if grep -q 'blob/main/' "$SKILL_FILE"; then
    BLOB_HITS=$(grep -c 'blob/main/' "$SKILL_FILE")
    fail "SKILL.md contains ${BLOB_HITS} blob/main GitHub URL(s) — use plugin-relative paths so the agent Reads the installed file (offline-safe, version-pinned)"
else
    pass "no blob/main GitHub URLs in SKILL.md (references load via relative paths)"
fi

if [ -d "$SKILL_DIR/references" ]; then
    REF_BLOB_HITS=$(grep -rn 'blob/main/' "$SKILL_DIR/references" --include='*.md' 2>/dev/null || true)
    if [ -n "$REF_BLOB_HITS" ]; then
        fail "references/ contains blob/main GitHub URL(s) — use plugin-relative paths (file:line):"
        echo "$REF_BLOB_HITS"
    else
        pass "no blob/main GitHub URLs in references/"
    fi
fi

# --- File type check (text only, no binaries) ---
NON_TEXT=$(find "$SKILL_DIR" -type f ! -name "*.md" ! -name "*.txt" ! -name "*.json" ! -name "*.yaml" ! -name "*.yml" ! -name "*.sh" ! -name "*.csv" ! -name ".gitignore" 2>/dev/null | grep -v '/\.' | head -5)
if [ -n "$NON_TEXT" ]; then
    warn "non-text files found (skills should be text-based): $NON_TEXT"
else
    pass "all files are text-based"
fi

# --- Description length for discovery ---
if echo "$FRONTMATTER" | grep -qE '^description:'; then
    DESC=$(echo "$FRONTMATTER" | grep -E '^description:' | sed "s/description: *//")
    DESC_LEN=${#DESC}
    if [ "$DESC_LEN" -gt 50 ]; then
        pass "description suitable for 'npx skills find' discovery ($DESC_LEN chars)"
    else
        warn "description may be too short for effective 'npx skills find' discovery"
    fi
fi

# --- Summary ---
echo ""
echo "=============================================="
echo -e "Results: ${GREEN}$PASS passed${NC}, ${YELLOW}$WARN warnings${NC}, ${RED}$FAIL failed${NC}"

if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}Validation FAILED — fix errors above before publishing${NC}"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo -e "${YELLOW}Validation PASSED with warnings — review recommendations above${NC}"
    exit 0
else
    echo -e "${GREEN}Validation PASSED — skill is spec-compliant${NC}"
    exit 0
fi
