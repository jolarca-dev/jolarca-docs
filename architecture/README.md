# Architecture Views

Abstraction-capped architecture views of the `jolarca-dev` platform, at **C4
level 1–2** and by **data category** and **trust boundary**. These are
**navigational** views: they establish shape and boundaries so an assessor or
engineer can orient. The authoritative, detailed architecture (topology, network
matrices, isolation model, sequences, ERD) lives upstream and is cited by pointer.

> **Abstraction cap.** Every label here is a **role**, **category**, or
> **boundary**. There are no addresses, ports, hostnames, schema/table names, or
> segment identifiers — see ADR
> [DOC-0002](../adr/DOC-0002-public-abstraction-cap.md). `scripts/verify.py`
> enforces this with a structural Mermaid check and the deny-pattern scan.
>
> **Dual state.** These views depict the **designed** system. Most components are
> `designed` or `planned`, not `deployed`; per-component status is in the
> [system description](../system-description/README.md). Nothing here asserts a
> live deployment.

## Views

| File | C4 level | Shows |
|---|---|---|
| [context.mmd](context.mmd) | L1 — System context | Actors and external systems around the platform boundary |
| [containers.mmd](containers.mmd) | L2 — Container | The software/datastore roles inside the boundary |
| [data-flow-categories.mmd](data-flow-categories.mmd) | — | How data **categories** move (never table-level) |
| [trust-boundaries.mmd](trust-boundaries.mmd) | — | Where trust changes hands (zero ports/hosts) |

GitHub renders `.mmd` Mermaid sources natively; open any file above to view it.

## What these views are not

- **Not the network policy.** The default-deny matrices and segment detail are
  upstream (`jolarca-infrastructure/security/network-policy.md`) and are cited, not
  reproduced.
- **Not the ERD or sequence diagrams.** Those are upstream
  (`jolarca/docs/architecture/`). This hub links them from the
  [ADR index](../adr/README.md) and the manifest.
- **Not a deployment map.** Host placement is deliberately absent; a version plus a
  host is a fingerprint, and the cap forbids it.

## Upstream sources (by pointer)

The detailed views these summarize are hashed in
[references/manifest.csv](../references/manifest.csv):

<!-- ref: jolarca-infrastructure/docs/architecture.md -->
<!-- ref: jolarca-infrastructure/security/isolation-model.md -->
<!-- ref: jolarca-infrastructure/security/network-policy.md -->
<!-- ref: jolarca/docs/architecture/01-modular-breakdown.md -->
