"""Tests for the abstraction-cap deny-pattern scanner (scripts/verify.py).

Forbidden tokens are assembled at RUNTIME from fragments, so this committed file
contains no literal forbidden token — the deny-scan scans this file too, and a
committed sample would (correctly) fail it. This is the concrete realization of the
DOC-0002 rule that no forbidden identifier is ever committed, even in tests.
"""

from __future__ import annotations

import verify


def _join(*parts: str) -> str:
    return ".".join(parts)


# Assembled at runtime; never a literal in source.
FORBIDDEN_IP = _join("203", "0", "113", "7")  # RFC 5737 TEST-NET-3
FORBIDDEN_CIDR = FORBIDDEN_IP + "/" + "24"
FORBIDDEN_HOSTPORT = FORBIDDEN_IP + ":" + "8080"
FORBIDDEN_FQDN = _join("db", "corp", "internal")
FORBIDDEN_THREE_LABEL = _join("api", "payments", "com")
FORBIDDEN_PORT_KW = "port " + "443"
FORBIDDEN_TCP = "tcp/" + "5432"
FORBIDDEN_TABLE = "jol" + "_marketplace." + "orders"
FORBIDDEN_BUCKET = "s3" + "://" + "internal-bucket/key"
FORBIDDEN_AKID = "AKIA" + "A" * 16
FORBIDDEN_PEM = "-----BEGIN " + "PRIVATE KEY-----"
FORBIDDEN_VPC = "vpc-" + "0a1b2c3d4e"

FORBIDDEN = [
    FORBIDDEN_IP,
    FORBIDDEN_CIDR,
    FORBIDDEN_HOSTPORT,
    FORBIDDEN_FQDN,
    FORBIDDEN_THREE_LABEL,
    FORBIDDEN_PORT_KW,
    FORBIDDEN_TCP,
    FORBIDDEN_TABLE,
    FORBIDDEN_BUCKET,
    FORBIDDEN_AKID,
    FORBIDDEN_PEM,
    FORBIDDEN_VPC,
]

# Things that look superficially like violations but MUST NOT be flagged.
CLEAN_SAMPLES = [
    "ADR-0005 authorizes the payment boundary (qualified INFRA-0005).",
    "See ci-base.yml:70 and :109-112 for the inert gate.",
    "Controls: CC8.1, ISO 27001 A.8.32, PCI-DSS Req 1.2/1.3, GDPR Art. 30.",
    "Pinned to 11bd71901bbe5b1630ceea73d27597364c9af683 (v4.2.2).",
    "Runtime dependency pyyaml==6.0.2 on Python 3.12.3.",
    "Public two-label domains github.com and keepachangelog.com are fine.",
    "A semver link v2.0.0.html and a file network-policy.md are fine.",
    "Roles, categories, boundaries, TLS/mTLS, EU residency, status designed.",
    "The word port appears here without a number, and so does important.",
]


def test_forbidden_tokens_are_detected() -> None:
    for token in FORBIDDEN:
        assert verify.scan_text(f"leak: {token} here"), f"no hit for {token!r}"


def test_clean_samples_do_not_fire() -> None:
    for sample in CLEAN_SAMPLES:
        assert verify.scan_text(sample) == [], f"false positive on {sample!r}"


def test_deny_scan_reports_line_and_category(tmp_path: object) -> None:
    del tmp_path
    hits = verify.scan_text("line one is clean\n" + f"bad {FORBIDDEN_IP} line\n")
    assert hits and hits[0][0] == 2 and hits[0][1] == "ipv4-address"


def test_entire_committed_tree_is_clean() -> None:
    # The abstraction cap must hold for the whole published repository, including
    # this file, the scanner's own source, and every generated artifact.
    assert verify.deny_scan(verify.REPO_ROOT) == []
