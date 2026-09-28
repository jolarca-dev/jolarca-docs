#!/usr/bin/env python3
"""The integrity gate — `make verify` / CI `lint`.

Runs the repository's integrity checks fail-fast. This is the Python-native half of
design spec §5; markdownlint (spec step 2) is a separate Make target because it needs
Node, which this repository deliberately does not otherwise require (spec §9). The
`make check` target runs both.

Steps (fail-fast order):

1. Governance files present and non-empty — a *working* reimplementation, because the
   shared ci-base.yml gate is inert (finding F-DOC-01).
2. Link check — every intra-repo relative link resolves; every `<!-- ref: -->`
   pointer has a manifest row.
3. Deny-pattern scan — the abstraction cap (ADR DOC-0002). No path exclusions: the
   scan covers every file in the working tree except non-published tooling dirs, so
   it scans its own source too.
4. ADR-ID uniqueness — no duplicate qualified ID; every prefix is allocated.
5. Hash-manifest freshness — recompute SHA-256 per upstream target and compare
   (sibling-dependent: skipped loudly in CI, enforced by --strict locally).
6. Inventory coherence — fleet.md declared count == row count (== live allow-list
   count when the fleet is present).
7. Mermaid structural check — known diagram type, balanced brackets/quotes.

Modes: without flags, sibling-dependent steps SKIP LOUDLY when the fleet is absent
(CI-safe). With --strict they FAIL instead, and a committed PARTIAL artifact fails —
this is the authoritative local pre-commit gate.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

import hash_manifest
import scan_adrs

REPO_ROOT = Path(__file__).resolve().parent.parent
FLEET_ROOT = REPO_ROOT.parent
CONTROL_REPOS = FLEET_ROOT / "jolarca-control" / "repos"

GOVERNANCE_FILES = ("README.md", "SECURITY.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE")
EXCLUDE_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        ".idea",
        ".vscode",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "node_modules",
        ".tmp",
    }
)
KNOWN_DIAGRAM_TYPES = frozenset(
    {
        "graph",
        "flowchart",
        "sequencediagram",
        "classdiagram",
        "statediagram",
        "statediagram-v2",
        "erdiagram",
        "journey",
        "gantt",
        "pie",
        "c4context",
        "c4container",
        "c4component",
        "c4deployment",
        "gitgraph",
        "mindmap",
        "timeline",
    }
)
# TLDs that are really file extensions — suppresses false positives such as
# "v2.0.0.html" while still flagging real three-label hostnames.
FILE_EXTENSIONS = frozenset(
    {
        "md", "markdown", "mmd", "yml", "yaml", "json", "jsonc", "py", "csv", "toml",
        "txt", "sh", "bash", "html", "htm", "css", "js", "mjs", "cjs", "ts", "tsx",
        "jsx", "xml", "cfg", "ini", "conf", "tf", "tfvars", "sql", "log", "rst",
        "adoc", "pdf", "png", "jpg", "jpeg", "gif", "svg", "lock", "sum", "mod",
        "example", "sample", "service", "timer",
    }
)
# Reserved/internal TLDs are built as a fragment tuple and joined at runtime so this
# file's own source never contains a literal matchable ".local"-style token.
_RESERVED_TLDS = ("internal", "local", "lan", "corp", "intranet", "invalid")
# Public TLDs, used only to RECOGNIZE a real multi-label hostname. A dotted code or
# config identifier such as `result.unparsed.append` or `tool.ruff.lint` ends in a
# label that is not a TLD, so it is never mistaken for a hostname.
_PUBLIC_TLDS = frozenset(
    {
        "com", "net", "org", "io", "dev", "app", "cloud", "ai", "co", "sh", "info",
        "biz", "xyz", "gov", "edu", "int", "eu", "uk", "us", "de", "fr", "nl", "lt",
        "lv", "ee", "se", "no", "fi", "dk", "pl", "cz", "es", "it", "pt", "ch", "at",
        "be", "ie", "ca", "au", "nz", "jp", "cn", "in", "br", "za",
    }
)
_ALL_TLDS = frozenset(_RESERVED_TLDS) | _PUBLIC_TLDS


@dataclass(frozen=True)
class Hit:
    path: str
    line_no: int
    category: str
    matched: str


def _valid_ipv4(matched: str) -> bool:
    parts = matched.split(".")
    return len(parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)


def _hostname_is_hit(matched: str) -> bool:
    tld = matched.rsplit(".", 1)[-1].lower()
    return tld in _ALL_TLDS and tld not in FILE_EXTENSIONS


_IPV4 = r"(?:\d{1,3}\.){3}\d{1,3}"
_Pattern = tuple[str, re.Pattern[str], Callable[[str], bool] | None]
DENY_PATTERNS: tuple[_Pattern, ...] = (
    ("ipv4-address", re.compile(r"(?<![\d.])" + _IPV4 + r"(?![\d.])"), _valid_ipv4),
    ("cidr-block", re.compile(r"(?<![\d.])" + _IPV4 + r"/\d{1,2}(?!\d)"), None),
    ("network-port", re.compile(r"(?<![\d.])" + _IPV4 + r":\d{2,5}(?!\d)"), None),
    ("network-port", re.compile(r"\b(?:tcp|udp)/\d{1,5}\b"), None),
    ("network-port", re.compile(r"\bports?\b\s*[:=]?\s*\d{2,5}\b"), None),
    (
        "hostname",
        re.compile(r"\b(?:[A-Za-z0-9_-]+\.){2,}[A-Za-z]{2,}\b"),
        _hostname_is_hit,
    ),
    (
        "hostname",
        re.compile(r"\b(?:[A-Za-z0-9_-]+\.)+(?:" + "|".join(_RESERVED_TLDS) + r")\b"),
        None,
    ),
    ("cloud-resource-id", re.compile(r"\b(?:vpc|subnet|eni|ami|vol|sg)-[0-9a-f]{6,}\b"), None),
    ("cloud-resource-id", re.compile(r"\bi-[0-9a-f]{8,}\b"), None),
    ("database-identifier", re.compile(r"\bjol(?:arca)?_[A-Za-z0-9_]+\.[A-Za-z0-9_]+"), None),
    ("object-storage-bucket", re.compile(r"\b(?:s3|gs|minio|oss)://\S+"), None),
    ("object-storage-bucket", re.compile(r"\barn:[a-z0-9-]*:s3:::\S+"), None),
    ("key-material", re.compile(r"-----BEGIN [A-Z0-9 ]*(?:PRIVATE KEY|CERTIFICATE)-----"), None),
    ("key-material", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), None),
    ("key-material", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), None),
    ("key-material", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), None),
    ("key-material", re.compile(r"\b(?:[0-9A-Fa-f]{2}:){7,}[0-9A-Fa-f]{2}\b"), None),
    ("k8s-identifier", re.compile(r"\b(?:namespace|networkpolicy|netpol)/[A-Za-z0-9_-]+"), None),
)


def scan_text(text: str) -> list[tuple[int, str, str]]:
    """Return (line_no, category, matched) for every deny-pattern hit in ``text``."""
    hits: list[tuple[int, str, str]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for category, pattern, validator in DENY_PATTERNS:
            for m in pattern.finditer(line):
                matched = m.group(0)
                if validator is not None and not validator(matched):
                    continue
                hits.append((line_no, category, matched))
    return hits


def iter_repo_files(repo_root: Path) -> Iterable[Path]:
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo_root).parts
        if any(part in EXCLUDE_DIRS for part in rel_parts):
            continue
        yield path


def published_files(repo_root: Path) -> list[Path]:
    """Files that could be pushed: git-tracked plus untracked-but-not-ignored.

    This is the precise published surface, so local-only ignored state (IDE config,
    virtualenvs, caches) is naturally out of scope while every committable file is
    in scope — "no path exclusions" over the repository, not over the workstation.
    Falls back to a directory walk minus tooling dirs if git is unusable.
    """
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return list(iter_repo_files(repo_root))
    files = [repo_root / line for line in proc.stdout.splitlines() if line.strip()]
    return [f for f in files if f.is_file()]


def deny_scan(repo_root: Path) -> list[Hit]:
    hits: list[Hit] = []
    for path in published_files(repo_root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary asset; not a text leak
        except OSError as exc:
            hits.append(Hit(path.name, 0, "unreadable-file", str(exc)))
            continue
        rel = path.relative_to(repo_root).as_posix()
        for line_no, category, matched in scan_text(text):
            hits.append(Hit(rel, line_no, category, matched))
    return hits


# ── steps ───────────────────────────────────────────────────────────────────────


def step_governance_files(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for name in GOVERNANCE_FILES:
        path = repo_root / name
        if not path.is_file():
            errors.append(f"missing required governance file: {name}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required governance file: {name}")
    return errors


_MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_EXTERNAL_RE = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|//|#)")


def _manifest_pointers(repo_root: Path) -> set[str]:
    csv_path = repo_root / "references" / "manifest.csv"
    if not csv_path.is_file():
        return set()
    rows = csv_path.read_text(encoding="utf-8").splitlines()
    return {line.split(",", 1)[0] for line in rows[1:] if line.strip()}


def step_links(repo_root: Path) -> list[str]:
    errors: list[str] = []
    manifest = _manifest_pointers(repo_root)
    for path in published_files(repo_root):
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(repo_root).as_posix()
        for target in _MD_LINK_RE.findall(text):
            clean = target.split("#", 1)[0].split("?", 1)[0].strip()
            if not clean or _EXTERNAL_RE.match(clean):
                continue
            resolved = (path.parent / clean).resolve()
            if not resolved.exists():
                errors.append(f"{rel}: broken relative link -> {target}")
        for pointer in hash_manifest.ref_markers_in_file(path):
            if pointer not in manifest:
                errors.append(f"{rel}: cross-repo pointer has no manifest row -> {pointer}")
    return errors


def step_deny_scan(repo_root: Path) -> list[str]:
    return [
        f"{h.path}:{h.line_no}: deny-pattern [{h.category}] matched {h.matched!r}"
        for h in deny_scan(repo_root)
    ]


_QUALIFIED_ID_RE = re.compile(r"^\|\s*([A-Za-z]+-\d{4})\s*\|")


def step_adr_uniqueness(repo_root: Path) -> list[str]:
    errors: list[str] = []
    index = repo_root / "adr" / "README.md"
    if not index.is_file():
        return ["adr/README.md not found — run `make generate`"]
    prefixes = set(scan_adrs.parse_namespace(repo_root / "adr" / "namespace.md").values())
    seen: dict[str, int] = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        m = _QUALIFIED_ID_RE.match(line)
        if not m:
            continue
        qid = m.group(1)
        seen[qid] = seen.get(qid, 0) + 1
        prefix = qid.rsplit("-", 1)[0] + "-"
        if prefix not in prefixes:
            errors.append(f"adr/README.md: qualified ID {qid} has no allocated namespace prefix")
    if not seen:
        errors.append("adr/README.md contains no qualified ADR IDs — index looks broken")
    for qid, count in seen.items():
        if count > 1:
            errors.append(f"adr/README.md: duplicate qualified ID {qid} ({count} rows)")
    return errors


def _read_manifest_rows(repo_root: Path) -> list[tuple[str, str]]:
    csv_path = repo_root / "references" / "manifest.csv"
    if not csv_path.is_file():
        return []
    rows: list[tuple[str, str]] = []
    for line in csv_path.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        pointer, _, digest = line.partition(",")
        rows.append((pointer, digest))
    return rows


def step_hash_freshness(
    repo_root: Path, fleet_root: Path, *, strict: bool
) -> tuple[list[str], bool]:
    """Return (errors, skipped). Sibling-dependent."""
    rows = _read_manifest_rows(repo_root)
    if not rows:
        return ["references/manifest.csv is empty or missing — broken, not minimal"], False
    if not (fleet_root / "jolarca-control").is_dir():
        if strict:
            return ["--strict: sibling fleet absent; cannot verify hash freshness"], False
        return [], True

    errors: list[str] = []
    for pointer, recorded in rows:
        target = fleet_root / pointer
        if not target.is_file():
            errors.append(f"manifest pointer no longer resolves: {pointer}")
            continue
        actual = hash_manifest.hash_file(target)
        if actual != recorded:
            errors.append(f"manifest hash stale for {pointer} (upstream changed — regenerate)")
    return errors, False


_COUNT_RE = re.compile(r"Repository count:\s*(\d+)")
_ROW_RE = re.compile(r"^\|\s*`")


def step_inventory_coherence(repo_root: Path, *, strict: bool) -> tuple[list[str], bool]:
    fleet_md = repo_root / "inventory" / "fleet.md"
    if not fleet_md.is_file():
        return ["inventory/fleet.md not found — run `make generate`"], False
    text = fleet_md.read_text(encoding="utf-8")
    m = _COUNT_RE.search(text)
    if not m:
        return ["inventory/fleet.md has no 'Repository count:' line"], False
    declared = int(m.group(1))
    rows = sum(1 for line in text.splitlines() if _ROW_RE.match(line))
    errors: list[str] = []
    if declared != rows:
        errors.append(f"fleet.md declares {declared} repositories but has {rows} rows")
    if not CONTROL_REPOS.is_dir():
        if strict:
            errors.append("--strict: allow-list absent; cannot verify inventory coherence")
            return errors, False
        return errors, True
    actual = len(list(CONTROL_REPOS.glob("*.yml")))
    if declared != actual:
        errors.append(f"fleet.md declares {declared} but allow-list has {actual} *.yml files")
    return errors, False


_BALANCE = {")": "(", "]": "[", "}": "{"}


def step_mermaid(repo_root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(repo_root.rglob("*.mmd")):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(repo_root).parts):
            continue
        rel = path.relative_to(repo_root).as_posix()
        text = path.read_text(encoding="utf-8")
        first = ""
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("%%"):
                continue
            first = stripped
            break
        if not first:
            errors.append(f"{rel}: empty diagram")
            continue
        kind = first.split()[0].lower()
        if kind not in KNOWN_DIAGRAM_TYPES:
            errors.append(f"{rel}: first token {first.split()[0]!r} is not a known diagram type")
        stack: list[str] = []
        in_quote = False
        balanced = True
        for line in text.splitlines():
            code = line.split("%%", 1)[0]
            for ch in code:
                if ch == '"':
                    in_quote = not in_quote
                elif in_quote:
                    continue
                elif ch in "([{":
                    stack.append(ch)
                elif ch in ")]}" and (not stack or stack.pop() != _BALANCE[ch]):
                    balanced = False
        if in_quote:
            errors.append(f"{rel}: unbalanced double quote")
        if stack or not balanced:
            errors.append(f"{rel}: unbalanced brackets")
    return errors


def _partial_artifacts(repo_root: Path) -> list[str]:
    bad: list[str] = []
    for rel in ("adr/README.md", "inventory/fleet.md"):
        path = repo_root / rel
        if path.is_file() and "PARTIAL" in path.read_text(encoding="utf-8"):
            bad.append(rel)
    return bad


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    fleet_present = (FLEET_ROOT / "jolarca-control").is_dir()
    print(f"verify: repo={REPO_ROOT} fleet_present={fleet_present} strict={strict}")

    checks: list[tuple[str, list[str]]] = []

    def run(name: str, errors: list[str]) -> bool:
        checks.append((name, errors))
        status = "FAIL" if errors else "ok"
        print(f"[{status:>4}] {name}" + (f" — {len(errors)} problem(s)" if errors else ""))
        for e in errors:
            print(f"        {e}")
        return not errors

    ok = True
    ok &= run("1. governance files", step_governance_files(REPO_ROOT))
    print("[note] 2. markdownlint — run as a separate `make` target (needs Node; spec §9)")
    ok &= run("3. link check", step_links(REPO_ROOT))
    ok &= run("4. deny-pattern scan (abstraction cap)", step_deny_scan(REPO_ROOT))
    ok &= run("5. ADR-ID uniqueness", step_adr_uniqueness(REPO_ROOT))

    hash_errors, hash_skipped = step_hash_freshness(REPO_ROOT, FLEET_ROOT, strict=strict)
    if hash_skipped:
        print("[SKIP] 6. hash-manifest freshness — sibling fleet absent (CI mode)")
    else:
        ok &= run("6. hash-manifest freshness", hash_errors)

    inv_errors, inv_skipped = step_inventory_coherence(REPO_ROOT, strict=strict)
    if inv_skipped:
        print("[SKIP] 7. inventory coherence (vs allow-list) — fleet absent; row check only")
        ok &= run("7. inventory coherence (rows)", inv_errors)
    else:
        ok &= run("7. inventory coherence", inv_errors)

    ok &= run("8. mermaid structural check", step_mermaid(REPO_ROOT))

    if strict:
        partial = _partial_artifacts(REPO_ROOT)
        ok &= run(
            "9. no committed PARTIAL artifacts (--strict)",
            [f"{p} is a PARTIAL artifact — regenerate with the full fleet" for p in partial],
        )

    print("verify: PASS" if ok else "verify: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
