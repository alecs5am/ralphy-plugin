#!/usr/bin/env python3
"""Build plugins/ralphy/ from an exported ralphy source tree.

Usage: build.py <exported-ralphy-tree> <ralphy-commit-sha>

Deterministic: the same source tree produces the same plugin bytes.
Only committed files reach the source tree (sync.sh uses `git archive`),
so uncommitted local changes in a ralphy checkout never leak in.
"""

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLUGIN = ROOT / "plugins" / "ralphy"
STATIC = ROOT / "src"

# Skills that are maintainer tooling, legacy compatibility shims, or
# vendored third-party render-engine skills (installed separately with
# the HyperFrames CLI) stay out of the public plugin.
EXCLUDE_SKILLS = {
    "ralphy-remotion",
    "remotion-to-hyperframes",
    # Bound to the maintainer's own social accounts; not general-purpose.
    "social-publish",
}
# Folders inside skills that hold repo-coupled helper code (they import
# from the ralphy source tree and cannot run from an installed plugin).
EXCLUDE_SKILL_SUBDIRS = {"scripts"}
# Always-bundled reference docs (repo-relative paths).
BASE_REFERENCES = [
    "AGENTS.md",
    "MODELS.md",
    "CLI.md",
    "docs/playbooks",
    "docs/skills-vs-templates.md",
    "docs/content-modes.md",
    "docs/content-mode-coverage.md",
    "docs/use-cases.md",
    "docs/agent-guide.md",
    "docs/assets-catalog.md",
    "docs/workspace-evaluators.md",
    "docs/perf-targets.md",
    "guidelines",
]
# Repo-relative doc references that are never bundled (dev-only context).
NEVER_BUNDLE = re.compile(r"^(docs/(developing-ralphy|release-runbook|superpowers|migration-|render-test-|template-audit-|architecture|branding)|notes/|cli/|scripts/|tests/|apps/)")
REF_PATTERN = re.compile(r"(?<![\w/.-])(?:\.\./)*((?:docs|guidelines)/[A-Za-z0-9_./-]+?|MODELS\.md|CLI\.md)(?=[)`'\"\s#:,;]|\.(?:\s|$)|$)")
# Text fixes applied to every bundled Markdown file. Each must match at
# least once, so a fix that lands upstream fails the build and gets removed.
SUBSTITUTIONS = [
    # Check a voice through the CLI instead of sending the user's key with xh.
    (
        'xh GET "https://api.elevenlabs.io/v1/voices/<voice-id>" \\\n'
        '  "xi-api-key:$ELEVENLABS_API_KEY" | jq .voice_id  # must not 404',
        "ralphy voice list | jq -e '.voices[] | select(.voice_id == \"<voice-id>\")'"
        "  # must match; add the voice to your ElevenLabs account first",
    ),
    # Document the header without reading the key from the environment.
    ("xi-api-key: $ELEVENLABS_API_KEY,", "xi-api-key: <ElevenLabs account key>,"),
]
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
MAX_FILE = 256 * 1024

NOTE = (
    "\n> **Ralphy plugin note.** Repo paths in this skill resolve inside the plugin: "
    "`docs/…`, `guidelines/…`, `MODELS.md`, and `CLI.md` live under the `ralphy` skill's "
    "`references/` folder (same relative layout); `.agents/skills/<name>/` is the sibling "
    "skill `<name>`. Paths under `cli/`, `scripts/`, or `notes/` are source files of "
    "github.com/alecs5am/ralphy and are not needed to operate. Run Ralphy through the "
    "installed `ralphy` CLI (see the `ralphy` skill for setup).\n"
)


def namespace(skill_md: Path) -> str:
    text = skill_md.read_text(encoding="utf-8")
    m = re.search(r"^namespace:\s*(\S+)", text, re.M)
    return m.group(1) if m else ""


def copy_file(src: Path, dst: Path) -> None:
    if src.name in SKIP_NAMES:
        return
    if src.stat().st_size > MAX_FILE:
        raise SystemExit(f"file over 256 KiB: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def copy_tree(src: Path, dst: Path, skip_dirs=frozenset()) -> None:
    for p in sorted(src.rglob("*")):
        rel = p.relative_to(src)
        if rel.parts and rel.parts[0] in skip_dirs:
            continue
        if p.is_symlink():
            raise SystemExit(f"symlink in source: {p}")
        if p.is_file():
            copy_file(p, dst / rel)


def add_note(skill_md: Path) -> None:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n.*?\n---\n", text, re.S)
    if not m:
        raise SystemExit(f"no front matter: {skill_md}")
    skill_md.write_text(text[: m.end()] + NOTE + text[m.end():], encoding="utf-8")


def referenced_paths(text: str):
    for m in REF_PATTERN.finditer(text):
        path = m.group(1).rstrip("/.")
        if not NEVER_BUNDLE.match(path):
            yield path


def main() -> None:
    src, sha = Path(sys.argv[1]), sys.argv[2]
    if PLUGIN.exists():
        shutil.rmtree(PLUGIN)

    # 1. Static plugin files (manifests, README, LICENSE, icon, router skill).
    copy_tree(STATIC, PLUGIN)
    copy_file(src / "LICENSE", PLUGIN / "LICENSE")

    # 2. User-facing skills from the source tree.
    skills_src = src / ".agents" / "skills"
    included = []
    for d in sorted(skills_src.iterdir()):
        md = d / "SKILL.md"
        if not md.is_file() or d.name in EXCLUDE_SKILLS or namespace(md) != "user":
            continue
        copy_tree(d, PLUGIN / "skills" / d.name, EXCLUDE_SKILL_SUBDIRS)
        add_note(PLUGIN / "skills" / d.name / "SKILL.md")
        included.append(d.name)

    # 3. Reference docs: the base set plus the closure of every docs/ or
    #    guidelines/ path referenced from bundled markdown.
    refs_root = PLUGIN / "skills" / "ralphy" / "references"
    queue, seen = list(BASE_REFERENCES), set()
    while queue:
        rel = queue.pop()
        if rel in seen:
            continue
        seen.add(rel)
        p = src / rel
        if p.is_dir():
            copy_tree(p, refs_root / rel)
        elif p.is_file():
            copy_file(p, refs_root / rel)
        else:
            continue
    # Scan everything bundled so far for more references, to a fixpoint.
    while True:
        before = len(seen)
        for md in sorted(PLUGIN.rglob("*.md")):
            for rel in referenced_paths(md.read_text(encoding="utf-8")):
                if rel in seen:
                    continue
                seen.add(rel)
                p = src / rel
                if p.is_dir():
                    copy_tree(p, refs_root / rel)
                elif p.is_file():
                    copy_file(p, refs_root / rel)
        if len(seen) == before:
            break

    # 4. Text fixes.
    for old, new in SUBSTITUTIONS:
        hits = 0
        for md in sorted(PLUGIN.rglob("*.md")):
            text = md.read_text(encoding="utf-8")
            if old in text:
                hits += text.count(old)
                md.write_text(text.replace(old, new), encoding="utf-8")
        if not hits:
            raise SystemExit(f"substitution no longer matches, remove it: {old[:60]!r}")

    # 5. Provenance.
    (PLUGIN / "SOURCE.json").write_text(
        json.dumps({"repository": "https://github.com/alecs5am/ralphy", "commit": sha, "skills": included}, indent=2) + "\n",
        encoding="utf-8",
    )
    files = [p for p in PLUGIN.rglob("*") if p.is_file()]
    print(json.dumps({"skills": len(included), "files": len(files), "bytes": sum(p.stat().st_size for p in files)}))


if __name__ == "__main__":
    main()
