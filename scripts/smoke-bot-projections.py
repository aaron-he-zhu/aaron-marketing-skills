#!/usr/bin/env python3
"""Hermetic AI Staff roster smoke — generate into a temp dir and assert shape.

Offline / CI-able. Proves the generator writes a complete 8-bot roster with
the exact catalog skill partition, Hermes bundle files, Grok artifacts,
hash-bound manifests, and no secret/user-state paths. It does not install on
a host, publish a template, or attach connectors.

Usage:
  python3 scripts/smoke-bot-projections.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "generate-bot-projections.py"
CATALOG = ROOT / "references" / "system-catalog.json"
CHIEF_BOT = "aaron-chief"
EXPECTED_BOTS = 8
EXPECTED_SKILLS = 120
HERMES_FILES = (
    "distribution.yaml",
    "SOUL.md",
    "README.md",
    "PORTABILITY.md",
    "distribution-manifest.json",
)
GROK_FILES = (
    "bot-cards.md",
    "enable-lists.md",
    "setup-checklist.md",
    "distribution-manifest.json",
)
FORBIDDEN_NAMES = {".env", "auth.json"}
FORBIDDEN_DIRS = {"memories", "sessions"}


class SmokeError(ValueError):
    """A roster smoke assertion failed."""


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SmokeError("cannot read %s: %s" % (path, exc)) from exc


def generate_roster(output: Path, source_root: Path = ROOT) -> subprocess.CompletedProcess:
    result = subprocess.run(
        [sys.executable, str(GENERATOR), "--output", str(output)],
        cwd=source_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise SmokeError(
            "generator failed (%s): %s" % (result.returncode, result.stderr.strip())
        )
    return result


def expected_partition(catalog: dict) -> dict[str, list[str]]:
    partition = {}
    for name, definition in catalog["disciplines"].items():
        partition["aaron-%s" % name] = [
            skill
            for phase in definition["phase_order"]
            for skill in definition["phases"][phase]
        ]
    partition[CHIEF_BOT] = list(catalog["protocol"]["skills"])
    return partition


def _bundle_dir(output: Path, bot: dict) -> Path:
    return output / bot["hermes_bundle"]


def assert_cli_summary(build: subprocess.CompletedProcess, roster: dict, catalog: dict) -> None:
    if "built bot-roster projection" not in build.stdout:
        raise SmokeError("generator stdout missing roster summary")
    if "8 bots, 120 skills" not in build.stdout:
        raise SmokeError("generator stdout missing 8 bots / 120 skills")
    if roster.get("bundle_version") != catalog.get("bundle_version"):
        raise SmokeError("roster bundle_version does not match the system catalog")


def assert_roster_partition(roster: dict, catalog: dict) -> None:
    bots = roster.get("bots")
    if not isinstance(bots, list) or len(bots) != EXPECTED_BOTS:
        raise SmokeError("expected %d bots, got %s" % (EXPECTED_BOTS, len(bots or [])))
    owned = [name for bot in bots for name in bot.get("skills") or []]
    if len(owned) != EXPECTED_SKILLS or len(set(owned)) != EXPECTED_SKILLS:
        raise SmokeError("roster must cover %d skills exactly once" % EXPECTED_SKILLS)
    expected = expected_partition(catalog)
    names = {bot["bot"] for bot in bots}
    if names != set(expected):
        raise SmokeError("roster bots %s != catalog partition %s" % (sorted(names), sorted(expected)))
    for bot in bots:
        want = expected[bot["bot"]]
        if list(bot["skills"]) != want:
            raise SmokeError("skill partition drift for %s" % bot["bot"])
        if bot["bot"] != CHIEF_BOT and len(bot["skills"]) != 16:
            raise SmokeError("%s must own 16 discipline skills" % bot["bot"])
        if bot["bot"] == CHIEF_BOT and len(bot["skills"]) != 8:
            raise SmokeError("%s must own the 8 protocol skills" % CHIEF_BOT)


def assert_hermes_shape(output: Path, roster: dict) -> None:
    for bot in roster["bots"]:
        bundle = _bundle_dir(output, bot)
        if not bundle.is_dir():
            raise SmokeError("missing Hermes bundle %s" % bundle)
        for filename in HERMES_FILES:
            path = bundle / filename
            if not path.is_file():
                raise SmokeError("missing %s" % path)
        yaml_text = (bundle / "distribution.yaml").read_text(encoding="utf-8")
        if 'name: "%s"' % bot["bot"] not in yaml_text:
            raise SmokeError("%s distribution.yaml missing bot name" % bot["bot"])
        if 'version: "%s"' % roster["bundle_version"] not in yaml_text:
            raise SmokeError("%s distribution.yaml missing bundle version" % bot["bot"])
        skill_root = bundle / "skills"
        if not skill_root.is_dir():
            raise SmokeError("%s missing skills/" % bot["bot"])
        skill_dirs = sorted(
            entry.name for entry in skill_root.iterdir() if entry.is_dir()
        )
        if skill_dirs != sorted(bot["skills"]):
            raise SmokeError("%s skills/ dirs != owned partition" % bot["bot"])
        for name in bot["skills"]:
            skill_file = skill_root / name / "SKILL.md"
            if not skill_file.is_file():
                raise SmokeError("missing %s" % skill_file)
            content = skill_file.read_text(encoding="utf-8")
            if "bot-roster static-skill boundary" not in content:
                raise SmokeError("%s missing static-skill boundary" % skill_file)
        kernel = bundle / "references" / "policy-kernel.md"
        if not kernel.is_file():
            raise SmokeError("%s must bundle the policy kernel" % bot["bot"])


def assert_grok_artifacts(output: Path, roster: dict) -> None:
    grok = output / "grok"
    for filename in GROK_FILES:
        path = grok / filename
        if not path.is_file():
            raise SmokeError("missing Grok artifact %s" % path)
    cards = (grok / "bot-cards.md").read_text(encoding="utf-8")
    enable = (grok / "enable-lists.md").read_text(encoding="utf-8")
    checklist = (grok / "setup-checklist.md").read_text(encoding="utf-8")
    for bot in roster["bots"]:
        if "## @%s" % bot["bot"] not in cards:
            raise SmokeError("bot-cards.md missing ## @%s" % bot["bot"])
        heading = "## @%s (%d skills)" % (bot["bot"], len(bot["skills"]))
        if heading not in enable:
            raise SmokeError("enable-lists.md missing %s" % heading)
        for name in bot["skills"]:
            if name not in enable:
                raise SmokeError("enable-lists.md missing skill %s" % name)
    for needle in (
        "share one persistent",
        "NOT_SCORED",
        "written instructions",
        "macOS, Windows, and iOS",
    ):
        if needle not in checklist:
            raise SmokeError("setup-checklist.md missing %r" % needle)


def assert_no_secret_paths(output: Path) -> None:
    for path in output.rglob("*"):
        if path.name in FORBIDDEN_NAMES:
            raise SmokeError("forbidden file: %s" % path)
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            raise SmokeError("forbidden directory: %s" % path)


def assert_manifests_hash_bound(output: Path, roster: dict) -> None:
    manifests = [
        output / "distribution-manifest.json",
        output / "grok" / "distribution-manifest.json",
    ]
    manifests.extend(
        _bundle_dir(output, bot) / "distribution-manifest.json"
        for bot in roster["bots"]
    )
    for manifest_path in manifests:
        if not manifest_path.is_file():
            raise SmokeError("missing manifest %s" % manifest_path)
        manifest = _load_json(manifest_path)
        if manifest.get("hash_algorithm") != "sha256":
            raise SmokeError("%s is not sha256-bound" % manifest_path)
        listed = {item["path"]: item for item in manifest.get("files") or []}
        base = manifest_path.parent
        actual = {
            path.relative_to(base).as_posix()
            for path in base.rglob("*")
            if path.is_file()
            and path.relative_to(base).as_posix() != "distribution-manifest.json"
        }
        if actual != set(listed):
            raise SmokeError("manifest file set drift: %s" % manifest_path)
        for relative, item in listed.items():
            digest = hashlib.sha256((base / relative).read_bytes()).hexdigest()
            if digest != item.get("sha256"):
                raise SmokeError("hash mismatch %s: %s" % (manifest_path, relative))


def assert_contained_markdown_links(output: Path, roster: dict) -> None:
    external = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
    link = re.compile(r"!?\[[^\]\n]*\]\((?P<destination>[^)\n]+)\)")
    for bot in roster["bots"]:
        bundle = _bundle_dir(output, bot)
        for markdown in sorted(bundle.rglob("*.md")):
            relative = markdown.relative_to(bundle).as_posix()
            text = markdown.read_text(encoding="utf-8")
            for match in link.finditer(text):
                destination = match.group("destination").strip()
                if destination.startswith("<"):
                    destination = destination[1:destination.find(">")]
                destination = destination.split()[0] if destination else ""
                path_text = destination.partition("#")[0]
                if (
                    not path_text
                    or external.match(path_text)
                    or path_text.startswith("//")
                ):
                    continue
                if path_text.startswith("/"):
                    raise SmokeError("%s links absolute path %s" % (relative, path_text))
                resolved = posixpath.normpath(
                    posixpath.join(posixpath.dirname(relative), path_text)
                )
                if resolved.startswith(".."):
                    raise SmokeError("%s escapes the bundle: %s" % (relative, path_text))
                if not (bundle / resolved).exists():
                    raise SmokeError("%s links missing target %s" % (relative, resolved))


def assert_roster_complete(output: Path, catalog: dict, roster: dict,
                           build: subprocess.CompletedProcess) -> None:
    assert_cli_summary(build, roster, catalog)
    assert_roster_partition(roster, catalog)
    assert_hermes_shape(output, roster)
    assert_grok_artifacts(output, roster)
    assert_no_secret_paths(output)
    assert_manifests_hash_bound(output, roster)
    assert_contained_markdown_links(output, roster)
    if not (output / "bot-roster.json").is_file():
        raise SmokeError("missing bot-roster.json")
    if not (output / "hermes").is_dir() or not (output / "grok").is_dir():
        raise SmokeError("output must contain hermes/ and grok/")


def run_smoke(source_root: Path = ROOT) -> Path:
    catalog = _load_json(source_root / "references" / "system-catalog.json")
    temporary = tempfile.TemporaryDirectory()
    try:
        output = Path(temporary.name) / "roster"
        build = generate_roster(output, source_root)
        roster = _load_json(output / "bot-roster.json")
        assert_roster_complete(output, catalog, roster, build)
    finally:
        temporary.cleanup()
    return output


def main(argv: list[str] | None = None) -> int:
    del argv
    try:
        run_smoke(ROOT)
    except SmokeError as exc:
        print("bot-roster smoke FAILED: %s" % exc, file=sys.stderr)
        return 1
    print(
        "bot-roster smoke passed: %d bots, %d skills, hermes+grok, "
        "hash-bound manifests, no secret paths"
        % (EXPECTED_BOTS, EXPECTED_SKILLS)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
