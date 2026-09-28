"""Tests for the upstream reference manifest (scripts/hash_manifest.py)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import hash_manifest


def test_discovers_real_markers_and_skips_fenced_examples(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text(
        "Real citation:\n"
        "<!-- ref: some-repo/docs/real.md -->\n"
        "Example inside a fence (must be ignored):\n"
        "```text\n"
        "<!-- ref: some-repo/docs/example.md -->\n"
        "```\n",
        encoding="utf-8",
    )
    assert hash_manifest.find_ref_markers(tmp_path) == ["some-repo/docs/real.md"]


def test_missing_target_is_a_hard_error(tmp_path: Path) -> None:
    rows, errors = hash_manifest.build_manifest(["nope/missing.md"], tmp_path)
    assert rows == []
    assert any("does not resolve" in e for e in errors)


def test_hash_matches_and_detects_mutation(tmp_path: Path) -> None:
    target = tmp_path / "repo" / "doc.md"
    target.parent.mkdir(parents=True)
    target.write_text("original\n", encoding="utf-8")
    rows, errors = hash_manifest.build_manifest(["repo/doc.md"], tmp_path)
    assert errors == []
    assert rows[0][1] == hashlib.sha256(b"original\n").hexdigest()
    target.write_text("mutated\n", encoding="utf-8")
    assert hash_manifest.hash_file(target) != rows[0][1]


def test_empty_manifest_is_a_hard_error(tmp_path: Path) -> None:
    (tmp_path / "no-refs.md").write_text("nothing cited here\n", encoding="utf-8")
    _csv, errors = hash_manifest.generate(tmp_path, tmp_path)
    assert any("empty" in e for e in errors)


def test_render_csv_has_header_and_rows(tmp_path: Path) -> None:
    target = tmp_path / "repo" / "a.md"
    target.parent.mkdir(parents=True)
    target.write_text("a\n", encoding="utf-8")
    rows, _ = hash_manifest.build_manifest(["repo/a.md"], tmp_path)
    csv_text = hash_manifest.render_csv(rows)
    lines = csv_text.splitlines()
    assert lines[0] == "pointer,sha256"
    assert lines[1].startswith("repo/a.md,")
