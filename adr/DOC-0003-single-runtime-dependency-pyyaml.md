# DOC-0003: Exactly one runtime dependency (pyyaml)

- **Status:** Accepted
- **Date:** 2026-09-28
- **Deciders:** org owner (solo era)
- **Compliance:** SOC 2 CC7.1 · ISO 27001 A.8.8 · PCI-DSS Req 6.5

## Context

The generation pipeline must parse two formats: the control-plane allow-list
(`jolarca-control/repos/*.yml`, YAML) and ADR front-matter/headings (Markdown). The
Python standard library has **no YAML parser**. An earlier claim that these scripts
would be "standard library only" was wrong for that reason and is corrected here.

A fleet convention exists that some repositories stay standard-library-only. That
convention belongs to the **evidence supply chain** in the private compliance
repository, where every dependency is a potential integrity risk to stored
evidence. `jolarca-docs` is a tier-3 public documentation hub that holds **no
evidence and no personal data**, so that rule does not transfer.

## Decision

Exactly **one runtime dependency: `pyyaml`, version-pinned.** Hand-rolling a YAML
parser is more risk than adopting the de-facto standard one, which is already the
convention in `jolarca-control` and `jolarca-data`.

- The pin is exact so Dependabot owns every bump as an auditable change.
- Dev-only tooling (`ruff`, `mypy`, `pytest`, `types-pyyaml`) is declared under an
  optional dependency group and **never ships**; it is not part of the runtime
  surface.
- The `dependency-review` gate and Dependabot apply to every change.

## Consequences

- (+) The runtime supply-chain surface is a single, widely-audited package.
- (+) Consistent with the rest of the fleet's tooling repositories.
- (−) One dependency to track. Accepted: Dependabot proposes bumps and the pin
  makes each bump an explicit, reviewed diff.
- Adding a second runtime dependency requires a new ADR that **supersedes** this
  one — it is not a casual change.

## Related

- [DOC-0001](DOC-0001-owns-no-fact-another-repo-owns.md) — the pipeline this feeds.
- Design spec §4.1.
