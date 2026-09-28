#!/usr/bin/env python3
"""Cross-repo ADR scanner.

Walks the sibling fleet for Architecture Decision Records, applies the
namespace prefix allocated in ``adr/namespace.md`` (the single source of truth
for prefixes), and renders ``adr/README.md`` — a registry of registries with
qualified IDs.

Design rules (design spec §4, §6; ADR DOC-0001):

* Only ID / title / status / date are extracted. Bodies are NEVER copied — they
  contain hostnames, paths, and internal identifiers that would breach the public
  abstraction cap (ADR DOC-0002). The generated index is itself deny-scanned.
* Fail loud, never degrade. A collision or an unassigned namespace is a hard
  failure. An unparseable heading is recorded in a "Requires attention" section
  of the generated index (never dropped), which is the visible, always-fresh
  realization of spec §6's "record it" requirement.
* A missing sibling clone is skipped loudly; ``--strict`` turns that into a
  failure; a non-strict run stamps a PARTIAL banner into the artifact so a
  partial index can never be committed unnoticed.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLEET_ROOT = REPO_ROOT.parent
NAMESPACE_MD = REPO_ROOT / "adr" / "namespace.md"
OUTPUT_MD = REPO_ROOT / "adr" / "README.md"

CONSOLIDATED_NAME = "ARCHITECTURE_DECISION_RECORDS.md"
SKIP_NAMES = frozenset({"README.md", "TEMPLATE.md", "namespace.md"})
# Siblings keep ADRs under docs/adr; this hub keeps its own under adr/.
ADR_SUBDIRS = ("docs/adr", "adr")
CONSOLIDATED_RELPATHS = (f"docs/{CONSOLIDATED_NAME}", CONSOLIDATED_NAME)

# "0001-slug.md", "ADR-0001-slug.md", "DOC-0001-slug.md" -> local id "0001".
ADR_FILE_RE = re.compile(r"^(?:[A-Za-z]+-)?(\d{4})[-_]")
# Registry table row: "| ADR-0011 | Title |".
CONSOLIDATED_ROW_RE = re.compile(r"^\|\s*ADR-(\d{4})\s*\|\s*(.+?)\s*\|")
# Section heading: "## ADR-0011 — Title" (em/en dash or hyphen).
CONSOLIDATED_HEAD_RE = re.compile(r"^##\s+ADR-(\d{4})\s*[\u2014\u2013-]\s*(.+?)\s*$")
H1_RE = re.compile(r"^#\s+(.+?)\s*$")
STATUS_KEYWORDS = ("accepted", "proposed", "deprecated", "superseded", "draft", "rejected")


@dataclass(frozen=True)
class ADR:
    qualified_id: str
    local_id: str
    title: str
    status: str
    date: str
    repo: str
    pointer: str


@dataclass(frozen=True)
class Unparsed:
    repo: str
    pointer: str
    reason: str


@dataclass
class ScanResult:
    adrs: list[ADR] = field(default_factory=list)
    unparsed: list[Unparsed] = field(default_factory=list)
    unavailable: list[str] = field(default_factory=list)
    hard_errors: list[str] = field(default_factory=list)


def parse_namespace(namespace_md: Path) -> dict[str, str]:
    """Return ``{repository: prefix}`` parsed from the namespace table."""
    mapping: dict[str, str] = {}
    for raw in namespace_md.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        prefix, repo = cells[0], cells[1]
        if not re.fullmatch(r"[A-Z]+-", prefix) or not re.fullmatch(r"[\w.-]+", repo):
            continue  # header row, separator row, or prose
        mapping[repo] = prefix
    if not mapping:
        raise ValueError(f"no prefix rows parsed from {namespace_md}")
    return mapping


def _clean_title(raw: str) -> str:
    """Strip a leading 'ADR-0001:' / 'DOC-0001:' / '0001:' qualifier from a title."""
    return re.sub(r"^(?:[A-Za-z]+-)?\d{4}\s*[:\u2014\u2013-]\s*", "", raw.strip()).strip()


def _find_status(text: str) -> str:
    m = re.search(r"\*\*Status:\*\*\s*(.+)", text)
    if not m:
        m = re.search(r"^-\s*Status:\s*(.+)", text, re.MULTILINE)
    if not m:
        m = re.search(r"^##\s+Status\s*\n+\s*(.+)", text, re.MULTILINE)
    if not m:
        return "unknown"
    value = m.group(1).strip()
    lowered = value.lower()
    for kw in STATUS_KEYWORDS:
        if lowered.startswith(kw):
            return kw.capitalize()
    return "unknown"  # a status we cannot classify is reported honestly, not guessed


def _find_date(text: str) -> str:
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    return m.group(1) if m else ""


def _parse_individual(
    path: Path, repo: str, repo_dir: Path, prefix: str, result: ScanResult
) -> None:
    match = ADR_FILE_RE.match(path.name)
    if match is None:
        return
    local_id = match.group(1)
    pointer = f"{repo}/{path.relative_to(repo_dir).as_posix()}"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:  # never drop it — record it
        result.unparsed.append(Unparsed(repo, pointer, f"unreadable: {exc}"))
        return
    heading: re.Match[str] | None = None
    for line in text.splitlines():
        heading = H1_RE.match(line)
        if heading is not None:
            break
    if heading is None:
        result.unparsed.append(Unparsed(repo, pointer, "no H1 heading"))
        return
    result.adrs.append(
        ADR(
            qualified_id=f"{prefix}{local_id}",
            local_id=local_id,
            title=_clean_title(heading.group(1)),
            status=_find_status(text),
            date=_find_date(text),
            repo=repo,
            pointer=pointer,
        )
    )


def _parse_consolidated(
    path: Path, repo: str, repo_dir: Path, prefix: str, result: ScanResult
) -> None:
    pointer = f"{repo}/{path.relative_to(repo_dir).as_posix()}"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        result.unparsed.append(Unparsed(repo, pointer, f"unreadable: {exc}"))
        return
    doc_status = _find_status(text)
    for line in text.splitlines():
        row = CONSOLIDATED_ROW_RE.match(line.strip())
        if row:
            local_id, title = row.group(1), _clean_title(row.group(2))
            result.adrs.append(
                ADR(f"{prefix}{local_id}", local_id, title, doc_status, "", repo, pointer)
            )
            continue
        head = CONSOLIDATED_HEAD_RE.match(line)
        if head:
            local_id = head.group(1)
            result.adrs.append(
                ADR(
                    f"{prefix}{local_id}",
                    local_id,
                    _clean_title(head.group(2)),
                    doc_status,
                    "",
                    repo,
                    pointer,
                )
            )


def _scan_repo(repo_dir: Path, repo: str, prefix: str, result: ScanResult) -> None:
    for sub in ADR_SUBDIRS:
        adr_dir = repo_dir / sub
        if adr_dir.is_dir():
            for path in sorted(adr_dir.glob("*.md")):
                if path.name in SKIP_NAMES:
                    continue
                _parse_individual(path, repo, repo_dir, prefix, result)
    for rel in CONSOLIDATED_RELPATHS:
        consolidated = repo_dir / rel
        if consolidated.is_file():
            _parse_consolidated(consolidated, repo, repo_dir, prefix, result)


def _repos_with_adr_content(fleet_root: Path) -> list[str]:
    """Sibling directories that actually hold ADR content (adr dir or consolidated file)."""
    found: list[str] = []
    for entry in sorted(p for p in fleet_root.iterdir() if p.is_dir()):
        if entry.name.startswith(".") and entry.name != ".github":
            continue
        has_adr = any((entry / sub).is_dir() for sub in ADR_SUBDIRS) or any(
            (entry / rel).is_file() for rel in CONSOLIDATED_RELPATHS
        )
        if has_adr:
            found.append(entry.name)
    return found


def scan(fleet_root: Path, repo_root: Path, *, strict: bool) -> ScanResult:
    result = ScanResult()
    namespace = parse_namespace(repo_root / "adr" / "namespace.md")

    # Hard-fail: an ADR-bearing repository with no allocated prefix (spec §3.4).
    for repo in _repos_with_adr_content(fleet_root):
        if repo not in namespace:
            result.hard_errors.append(
                f"repository '{repo}' has ADRs but no prefix in adr/namespace.md"
            )

    for repo, prefix in sorted(namespace.items()):
        repo_dir = fleet_root / repo
        if not repo_dir.is_dir():
            result.unavailable.append(repo)
            continue
        _scan_repo(repo_dir, repo, prefix, result)

    # Hard-fail: duplicate qualified ID (a collision the index must never hide).
    seen: dict[str, str] = {}
    for adr in result.adrs:
        if adr.qualified_id in seen:
            result.hard_errors.append(
                f"duplicate qualified ID {adr.qualified_id}: "
                f"{seen[adr.qualified_id]} and {adr.pointer}"
            )
        seen[adr.qualified_id] = adr.pointer

    if strict and result.unavailable:
        result.hard_errors.append(
            f"--strict: {len(result.unavailable)} sibling clone(s) unavailable: "
            + ", ".join(sorted(result.unavailable))
        )
    return result


def render(result: ScanResult) -> str:
    lines: list[str] = [
        "<!-- GENERATED by scripts/scan_adrs.py — DO NOT EDIT. Edit the generator",
        "     or the upstream ADR, then run `make generate`. -->",
        "# Cross-Repository ADR Index",
        "",
        "A registry of registries. Every ADR in the fleet is listed with its",
        "**namespace-qualified ID** so a bare `ADR-0005` citation is never ambiguous.",
        "IDs are applied read-side; upstream files are never renumbered or moved",
        "(see [namespace.md](namespace.md)).",
        "",
    ]
    if result.unavailable:
        lines += [
            f"<!-- PARTIAL: {len(result.unavailable)} siblings unavailable "
            f"({', '.join(sorted(result.unavailable))}) — regenerate with the full "
            "fleet before trusting this index. -->",
            "",
            f"> **PARTIAL INDEX.** {len(result.unavailable)} sibling clone(s) were "
            "unavailable at generation time: "
            + ", ".join(sorted(result.unavailable))
            + ". This index is incomplete; do not rely on it until regenerated.",
            "",
        ]
    lines += [
        f"Indexed ADRs: **{len(result.adrs)}** across "
        f"**{len({a.repo for a in result.adrs})}** repositories.",
        "",
        "| Qualified ID | Repository | Local | Title | Status | Date |",
        "|---|---|---|---|---|---|",
    ]
    for adr in sorted(result.adrs, key=lambda a: a.qualified_id):
        title = adr.title.replace("|", "\\|")
        lines.append(
            f"| {adr.qualified_id} | `{adr.repo}` | {adr.local_id} | {title} "
            f"| {adr.status} | {adr.date or '—'} |"
        )
    if result.unparsed:
        lines += [
            "",
            "## Requires attention (never dropped)",
            "",
            "These ADR sources could not be parsed into the index. They are recorded",
            "here rather than silently omitted; promote persistent entries to",
            "[findings/register.md](../findings/register.md).",
            "",
            "| Repository | Source | Reason |",
            "|---|---|---|",
        ]
        for item in result.unparsed:
            lines.append(f"| `{item.repo}` | `{item.pointer}` | {item.reason} |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    result = scan(FLEET_ROOT, REPO_ROOT, strict=strict)
    if result.hard_errors:
        for err in result.hard_errors:
            print(f"scan_adrs: HARD FAIL: {err}", file=sys.stderr)
        return 1
    OUTPUT_MD.write_text(render(result), encoding="utf-8")
    note = " (PARTIAL)" if result.unavailable else ""
    print(f"scan_adrs: wrote {OUTPUT_MD.relative_to(REPO_ROOT)} — {len(result.adrs)} ADRs{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
