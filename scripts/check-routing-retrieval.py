#!/usr/bin/env python3
"""Deterministic routing/retrieval suite — Python 3 stdlib only.

Given an intent, rank the 120 Skills from name/description (CI bar) and from
a light body-aware heuristic (comparison arm). Expected sets must be size
≤3. Focused top-k retrieval is the contract: exhaustive dumps are not a
pass. This suite adds no Skill and does not load references/wiki/.

Usage:
  python3 scripts/check-routing-retrieval.py   # CI gate; exit 1 on fail
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_PATH = ROOT / ".claude-plugin" / "plugin.json"
CASES_PATH = ROOT / "evals" / "routing-retrieval" / "cases.json"
QUOTED = re.compile(r'"([^"]{3,})"')
WS = re.compile(r"\s+")
TOKEN = re.compile(r"[a-z0-9]+")
HEADING = re.compile(r"^#{1,3}\s+(.+)$", re.M)
STOP = {
    "a", "an", "and", "are", "as", "at", "be", "before", "for", "from",
    "in", "is", "it", "my", "of", "on", "or", "our", "the", "then",
    "this", "to", "use", "when", "with", "asks", "user", "not",
}

MAX_EXPECTED = 3
DEFAULT_K = 3
BODY_EXCERPT_LINES = 40


class RetrievalError(ValueError):
    pass


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RetrievalError("cannot load %s: %s" % (path.relative_to(ROOT), exc)) from exc


def frontmatter_and_body(text: str, rel: str):
    if not text.startswith("---"):
        raise RetrievalError("%s has no frontmatter" % rel)
    try:
        end = text.index("\n---", 3)
    except ValueError as exc:
        raise RetrievalError("%s has unterminated frontmatter" % rel) from exc
    return text[3:end], text[end + 4:]


def field(block: str, key: str):
    match = re.search(r"^%s:\s*(.*)$" % re.escape(key), block, re.M)
    if not match:
        return ""
    return match.group(1).strip().strip("'\"")


def tokens(text: str):
    return {tok for tok in TOKEN.findall(text.lower()) if tok not in STOP and len(tok) > 1}


def load_skills():
    plugin = load_json(PLUGIN_PATH)
    skills = []
    for entry in plugin["skills"]:
        rel_entry = entry[2:] if entry.startswith("./") else entry
        skill_file = ROOT / rel_entry / "SKILL.md"
        rel = str(skill_file.relative_to(ROOT))
        text = skill_file.read_text(encoding="utf-8")
        block, body = frontmatter_and_body(text, rel)
        slug = rel_entry.rstrip("/").split("/")[-1]
        name = field(block, "name") or slug
        description = field(block, "description")
        when_to_use = field(block, "when_to_use")
        triggers = {WS.sub(" ", phrase.lower()).strip() for phrase in QUOTED.findall(description)}
        headings = [WS.sub(" ", h.lower()).strip() for h in HEADING.findall(body)]
        excerpt_lines = []
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            excerpt_lines.append(stripped)
            if len(excerpt_lines) >= BODY_EXCERPT_LINES:
                break
        excerpt = "\n".join(excerpt_lines)
        skills.append({
            "slug": slug,
            "name": name,
            "description": description,
            "when_to_use": when_to_use,
            "triggers": triggers,
            "name_tokens": set(slug.split("-")),
            "desc_tokens": tokens(name + " " + description),
            "body_tokens": tokens(when_to_use + " " + " ".join(headings) + " " + excerpt),
            "headings": headings,
        })
    if len(skills) != 120:
        raise RetrievalError("expected 120 skills, found %d" % len(skills))
    return skills


def score_skill(intent: str, skill: dict, body_aware: bool) -> int:
    intent_l = WS.sub(" ", intent.lower()).strip()
    intent_tokens = tokens(intent)
    score = 0
    for trigger in skill["triggers"]:
        if trigger and trigger in intent_l:
            score += 120
    score += 10 * len(skill["name_tokens"] & intent_tokens)
    score += 3 * len(skill["desc_tokens"] & intent_tokens)
    if body_aware:
        score += len(skill["body_tokens"] & intent_tokens)
        for heading in skill["headings"]:
            if heading and heading in intent_l:
                score += 8
    return score


def rank(intent: str, skills: list, body_aware: bool, k: int):
    scored = [(score_skill(intent, skill, body_aware), skill["slug"]) for skill in skills]
    scored.sort(key=lambda item: (-item[0], item[1]))
    return scored[:k]


def evaluate_case(case: dict, skills: list, k: int):
    expected = case["expected_skills"]
    must_not = case.get("must_not_primary") or []
    results = {}
    for mode, body_aware in (("description", False), ("body-aware", True)):
        ranked = rank(case["intent"], skills, body_aware, k)
        slugs = [slug for _, slug in ranked]
        missing = [slug for slug in expected if slug not in slugs]
        primary = slugs[0] if slugs else None
        forbidden_hit = [slug for slug in must_not if slug == primary]
        results[mode] = {
            "ranked": ranked,
            "slugs": slugs,
            "missing": missing,
            "forbidden_hit": forbidden_hit,
            "ok": not missing and not forbidden_hit,
        }
    return results


def main():
    fails = []

    def fail(msg):
        fails.append(msg)
        print("FAIL  " + msg)

    try:
        payload = load_json(CASES_PATH)
        skills = load_skills()
    except (RetrievalError, OSError) as exc:
        print("ROUTING RETRIEVAL FAILED — %s" % exc)
        return 1

    k = payload.get("k", DEFAULT_K)
    if k != DEFAULT_K:
        fail("cases.json k must be %d (focused retrieval); found %s" % (DEFAULT_K, k))
    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        fail("cases.json has no cases")
        print("\nROUTING RETRIEVAL FAILED — %d issue(s)." % len(fails))
        return 1

    slugs = {skill["slug"] for skill in skills}
    print(payload.get("guidance", ""))
    print("k=%d skills=%d cases=%d" % (k, len(skills), len(cases)))
    print("Focused ≤3 modules beat exhaustive dumps.\n")

    desc_pass = 0
    body_pass = 0
    for case in cases:
        cid = case.get("id", "<missing-id>")
        expected = case.get("expected_skills") or []
        if not (1 <= len(expected) <= MAX_EXPECTED):
            fail("%s expected_skills must have 1–%d slugs" % (cid, MAX_EXPECTED))
            continue
        unknown = [slug for slug in expected + (case.get("must_not_primary") or []) if slug not in slugs]
        if unknown:
            fail("%s names unknown skill(s) %s" % (cid, unknown))
            continue
        results = evaluate_case(case, skills, k)
        for mode in ("description", "body-aware"):
            row = results[mode]
            mark = "ok" if row["ok"] else "FAIL"
            print("%s %s %s expected=%s retrieved=%s"
                  % (mark, cid, mode, expected, row["slugs"]))
            if row["missing"]:
                fail("%s %s missed %s" % (cid, mode, row["missing"]))
            if row["forbidden_hit"]:
                fail("%s %s ranked forbidden primary %s"
                     % (cid, mode, row["forbidden_hit"]))
        if results["description"]["ok"]:
            desc_pass += 1
        if results["body-aware"]["ok"]:
            body_pass += 1
        if results["description"]["ok"] and not results["body-aware"]["ok"]:
            fail("%s body-aware regressed a description-only pass" % cid)

    print("\ndescription-only %d/%d  body-aware %d/%d"
          % (desc_pass, len(cases), body_pass, len(cases)))
    if fails:
        print("\nROUTING RETRIEVAL FAILED — %d issue(s)." % len(fails))
        return 1
    print("Routing retrieval passed: %d intents, k=%d, description-only and "
          "body-aware both kept the expected set inside the focused window."
          % (len(cases), k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
