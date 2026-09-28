# jolarca-docs

The **public compliance-documentation hub** for the `jolarca-dev` fleet. It
exists to make the fleet auditable: one index of architecture decisions, one
description of the system for SOC 2, and one generated view of the fleet
inventory — each verified against its upstream source by cryptographic hash.

> **Load-bearing invariant (ADR [DOC-0001](adr/DOC-0001-owns-no-fact-another-repo-owns.md)):**
> `jolarca-docs` owns **no fact that another repository owns.** It indexes,
> describes, and verifies; it does not restate. When an upstream document
> changes, the recorded hash mismatches and CI fails — documentation freshness
> is an auditable control, not an aspiration.

## What this repository owns

Exactly three artifacts that are homeless elsewhere in the fleet, plus one
derived view:

| Owned here | Why it belongs here |
|---|---|
| [Cross-repo ADR index](adr/README.md) | No repository can index itself; the ID collisions exist *between* registries. See [adr/namespace.md](adr/namespace.md). |
| [SOC 2 description of the system](system-description/README.md) | Exists nowhere in the fleet; the Type I readiness date makes it a blocker. |
| [Fleet inventory view](inventory/fleet.md) | Generated read-only from the control-plane allow-list, which **remains** the ISO 27001 A.5.9 system of record. |

Everything else is a **pointer + SHA-256** in
[references/manifest.csv](references/manifest.csv). No upstream prose is copied.

## The abstraction cap (read this before contributing)

This repository is **public**. Every file is scanned by
[`scripts/verify.py`](scripts/verify.py) against a deny-pattern list, and the
scan **hard-fails** on any network address, port, hostname, VM/node name,
VPC/subnet name, Kubernetes namespace or NetworkPolicy name, database
schema/table/column name, object-storage bucket name, cryptographic key
identifier, or CDE segmentation detail.

Permitted vocabulary is **component roles, data categories, trust boundaries,
protocol classes (TLS/mTLS), residency, and status**. There is **no suppression
mechanism and no path exclusion**: a false positive is fixed by rewriting the
text, never by weakening the control. The rationale is
[ADR DOC-0002](adr/DOC-0002-public-abstraction-cap.md); the rules for
contributors are in [CONTRIBUTING.md](CONTRIBUTING.md).

## Dual-state: designed / deployed / planned

The fleet is largely unprovisioned. Every component, control, and flow in the
[system description](system-description/README.md) carries an explicit status —
`designed`, `deployed`, or `planned` — sourced from verified evidence. Nothing
here is written in the present tense, because describing an unbuilt control as
live would misrepresent the system to an auditor.

## Repository layout

```text
adr/                 cross-repo ADR index (generated) + namespace allocation (owned)
system-description/  the SOC 2 description of the system (owned)
architecture/        C4 L1–L2 diagrams + data-flow/trust-boundary views (.mmd)
inventory/           fleet inventory view (generated from the allow-list)
references/          pointer + SHA-256 manifest of every upstream document cited
findings/            cross-repo defects register (owner / control / evidence)
scripts/             generation pipeline + the integrity gate
tests/               the verifier is tested; an untested verifier is how gates ship inert
docs/superpowers/    the approved design spec
```

## How it stays fresh

Generation is **local**; CI **verifies committed output** (design spec §2, D2).
A public repository is never given credentials to read private upstream repos.

```text
make generate       # regenerate the derived artifacts from local sibling clones
make verify         # integrity gate (CI-safe: sibling steps skip loudly if absent)
make verify-strict  # integrity gate that fails if any upstream input is missing
make test           # pytest
make check          # ruff + mypy + markdownlint + verify + test  (the CI 'lint' job)
```

The generated artifacts are **committed**: the pull-request diff is the audit
trail, showing an auditor exactly which upstream facts moved.

## Compliance mapping

| Framework | Where addressed |
|---|---|
| SOC 2 Type II | [system-description/07-criteria-map.md](system-description/07-criteria-map.md) |
| ISO 27001:2022 | A.5.9 inventory view · A.5.36 freshness control · A.8.32 change management |
| GDPR | Category-level data flows the DPIAs cite · Art. 30/35 coherence |
| PCI-DSS 4.0 | Abstraction cap keeps CDE detail out of a public repo (Req 1.2/1.3) |

The authoritative deviation register for the whole fleet lives in
`jolarca-control/docs/drift-findings.md`; this repository cites it and records
documentation-specific findings in [findings/register.md](findings/register.md).

## Design of record

The approved design is
[docs/superpowers/specs/2026-09-26-jolarca-docs-compliance-hub-design.md](docs/superpowers/specs/2026-09-26-jolarca-docs-compliance-hub-design.md).

## Security

See [SECURITY.md](SECURITY.md). If you believe you have found a control-plane
identifier or secret in this repository, treat it as a security incident and
report it privately — do **not** open a public issue.

## License

Proprietary — published for transparency, not licensed for redistribution. See
[LICENSE](LICENSE).
