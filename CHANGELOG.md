# Changelog

All notable changes to `jolarca-docs` are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Changes are grouped by the control they affect, because this repository exists to
be audited. A generated-artifact refresh is recorded when an upstream fact moved.

## [Unreleased]

### Added

- Nothing yet.

## [0.1.0] - 2026-09-28

Initial provisioning of the compliance-documentation hub from the approved design
spec (`docs/superpowers/specs/2026-09-26-jolarca-docs-compliance-hub-design.md`).

### Added

- **Governance:** `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `LICENSE`
  (proprietary notice for a public repo), `QODER.md`, `.markdownlint.json`.
- **Owned artifacts:** the SOC 2 description of the system
  (`system-description/01`–`07`), the ADR namespace allocation
  (`adr/namespace.md`), and ADRs `DOC-0001` (owns no fact another repo owns),
  `DOC-0002` (public abstraction cap), `DOC-0003` (single runtime dependency).
- **Generated artifacts:** the cross-repo ADR index (`adr/README.md`), the fleet
  inventory view (`inventory/fleet.md`), and the upstream hash manifest
  (`references/manifest.csv`).
- **Architecture views:** C4 L1 context, C4 L2 containers, category-level data
  flow, and trust boundaries (`architecture/*.mmd`) — abstraction-capped.
- **Pipeline:** `scripts/generate.py`, `scan_adrs.py`, `build_inventory.py`,
  `hash_manifest.py`, and the integrity gate `verify.py`.
- **Integrity gate:** eight fail-fast checks (governance files, markdownlint,
  link check, deny-pattern abstraction cap, ADR-ID uniqueness, hash-manifest
  freshness, inventory coherence, Mermaid structural check).
- **Tests:** the deny-pattern scanner, the ADR scanner, and the hash manifest,
  each with a planted violation to prove the gate can fail.
- **CI:** the required status-check context `lint` running `make check`, with
  `actions/checkout` pinned by commit SHA; Dependabot for pip and actions.
- **Findings register:** cross-repo defects recorded with owner, affected
  control, and evidence (`findings/register.md`).

### Notes

- The repository holds no secret, no personal data, and no control-plane
  identifier by construction; the deny-pattern scan enforces this with no path
  exclusions.
- Remote repository creation and push remain a gated operator step and are
  deliberately not performed by this change.

[Unreleased]: https://github.com/jolarca-dev/jolarca-docs/compare/HEAD
[0.1.0]: https://github.com/jolarca-dev/jolarca-docs/releases/tag/v0.1.0
