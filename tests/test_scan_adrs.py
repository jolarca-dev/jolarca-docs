"""Tests for the cross-repo ADR scanner (scripts/scan_adrs.py).

The committed fixture fleet under ``tests/fixtures/fake-fleet`` plants *structural*
violations only — an ID collision, an orphan repository with no prefix, and an
unparseable heading. It contains no forbidden identifiers (ADR DOC-0002).
"""

from __future__ import annotations

from pathlib import Path

import scan_adrs

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "fake-fleet"
FAKE_FLEET = FIXTURES / "fleet"
FAKE_REPO = FIXTURES / "repo"


def _scan() -> scan_adrs.ScanResult:
    return scan_adrs.scan(FAKE_FLEET, FAKE_REPO, strict=False)


def test_detects_planted_id_collision() -> None:
    result = _scan()
    assert any("duplicate qualified ID FC-0001" in e for e in result.hard_errors)


def test_orphan_repository_without_prefix_hard_fails() -> None:
    result = _scan()
    assert any("fake-orphan" in e and "no prefix" in e for e in result.hard_errors)


def test_every_parseable_adr_is_indexed() -> None:
    ids = {a.qualified_id for a in _scan().adrs}
    assert {"FA-0001", "FA-0002", "FC-0001"} <= ids


def test_consolidated_table_and_section_forms_both_parsed() -> None:
    consolidated = {a.qualified_id for a in _scan().adrs if a.repo == "fake-consolidated"}
    assert consolidated == {"FCON-0001", "FCON-0002", "FCON-0003"}


def test_unparseable_heading_is_recorded_not_dropped() -> None:
    result = _scan()
    assert any(u.repo == "fake-broken" and "no H1" in u.reason for u in result.unparsed)


def test_title_status_and_date_extracted() -> None:
    first = next(a for a in _scan().adrs if a.qualified_id == "FA-0001")
    assert first.title == "First synthetic decision"
    assert first.status == "Accepted"
    assert first.date == "2026-01-01"


def test_render_flags_collision_and_marks_attention() -> None:
    rendered = scan_adrs.render(_scan())
    assert "Cross-Repository ADR Index" in rendered
    assert "Requires attention" in rendered
    assert "fake-broken" in rendered
