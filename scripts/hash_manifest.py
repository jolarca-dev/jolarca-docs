#!/usr/bin/env python3
"""Upstream reference manifest generator.

Discovers every ``<!-- ref: repo/path -->`` marker in this repository's Markdown,
resolves each against the local sibling clones, computes its SHA-256, and writes
``references/manifest.csv``. The manifest is what turns documentation freshness
into an auditable control (SOC 2 CC7.3 / ISO 27001 A.5.36): ``scripts/verify.py``
recomputes each hash and fails when an upstream document has moved or changed.

Fail loud, never degrade (ADR DOC-0001, design spec §6):

* a marker whose target does not resolve is a hard failure — a dangling pointer is
  a broken reference, not something to skip;
* an **empty** manifest is a hard failure — a hub that references nothing is broken,
  not minimal.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLEET_ROOT = REPO_ROOT.parent
OUTPUT_CSV = REPO_ROOT / "references" / "manifest.csv"

REF_LINE_RE = re.compile(r"^<!--\s*ref:\s*(\S+?)\s*-->$")
# Non-published tooling directories; never scanned for markers.
EXCLUDE_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "node_modules",
        ".tmp",
        "fixtures",
    }
)


def iter_markdown(repo_root: Path) -> list[Path]:
    results: list[Path] = []
    for path in sorted(repo_root.rglob("*.md")):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(repo_root).parts):
            continue
        results.append(path)
    return results


def _content_lines(text: str) -> list[str]:
    """Lines of ``text`` with fenced code blocks blanked out.

    Reference markers inside a fenced block are documentation *examples* (see
    CONTRIBUTING.md and references/README.md), not real citations, so they must not
    become manifest rows.
    """
    out: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return out


def ref_markers_in_file(path: Path) -> list[str]:
    """Reference pointers cited in ``path``.

    A real citation is a marker on its **own line** outside any fenced code block.
    Inline examples and fenced examples are documentation, not citations, and are
    ignored — otherwise the manifest would try to hash a placeholder path.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    found: list[str] = []
    for line in _content_lines(text):
        m = REF_LINE_RE.match(line.strip())
        if m:
            found.append(m.group(1))
    return found


def find_ref_markers(repo_root: Path) -> list[str]:
    """Deduplicated, sorted list of upstream pointers cited across the repo."""
    pointers: set[str] = set()
    for path in iter_markdown(repo_root):
        pointers.update(ref_markers_in_file(path))
    return sorted(pointers)


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(
    pointers: list[str], fleet_root: Path
) -> tuple[list[tuple[str, str]], list[str]]:
    """Return (rows, hard_errors). A pointer that does not resolve is an error."""
    rows: list[tuple[str, str]] = []
    errors: list[str] = []
    for pointer in pointers:
        target = fleet_root / pointer
        if not target.is_file():
            errors.append(f"reference pointer does not resolve to a file: {pointer}")
            continue
        rows.append((pointer, hash_file(target)))
    return rows, errors


def render_csv(rows: list[tuple[str, str]]) -> str:
    lines = ["pointer,sha256"]
    lines += [f"{pointer},{digest}" for pointer, digest in rows]
    return "\n".join(lines) + "\n"


def generate(repo_root: Path, fleet_root: Path) -> tuple[str, list[str]]:
    pointers = find_ref_markers(repo_root)
    rows, errors = build_manifest(pointers, fleet_root)
    if not rows and not errors:
        errors.append("manifest is empty — no upstream references were found (broken, not minimal)")
    return render_csv(rows), errors


def main(argv: list[str]) -> int:
    del argv  # no flags; behaviour is identical local and CI (siblings permitting)
    csv_text, errors = generate(REPO_ROOT, FLEET_ROOT)
    if errors:
        for err in errors:
            print(f"hash_manifest: HARD FAIL: {err}", file=sys.stderr)
        return 1
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_CSV.write_text(csv_text, encoding="utf-8")
    rows = csv_text.count("\n") - 1
    print(f"hash_manifest: wrote {OUTPUT_CSV.relative_to(REPO_ROOT)} — {rows} pointer(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
