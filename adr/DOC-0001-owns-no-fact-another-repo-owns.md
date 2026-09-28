# DOC-0001: jolarca-docs owns no fact another repository owns

- **Status:** Accepted
- **Date:** 2026-09-28
- **Deciders:** org owner (solo era)
- **Compliance:** SOC 2 CC8.1 · ISO 27001 A.5.9/A.5.36/A.8.32 · GDPR Art. 30/35

## Context

The `jolarca-dev` fleet already has substantial architecture and compliance
documentation spread across many repositories. The recurring failure mode is not
missing content — it is **the same fact maintained in several places that then
drift**. The asset inventory disagrees with itself across four documents; each DPIA
embeds its own copy of a data-flow diagram; three ADR registries number from
`0001`. A new documentation repository that copies architecture prose would add a
sixth place for one fact to drift and make audits harder, not easier.

## Decision

`jolarca-docs` owns **no fact that another repository owns.** It owns exactly the
artifacts that are homeless today, plus one derived view:

1. **Cross-repo ADR index** — no repository can index itself; the collisions exist
   *between* registries. Qualified IDs are applied read-side (see
   [namespace.md](namespace.md)).
2. **SOC 2 description of the system** — exists nowhere in the fleet and is due for
   the Type I readiness assessment.
3. **Fleet inventory view** — generated read-only from the control-plane
   allow-list, which **remains** the ISO 27001 A.5.9 system of record. This
   repository asserts coherence with it; it does not take ownership of it.

Everything else is referenced by **pointer + SHA-256** in
`references/manifest.csv`. No upstream prose is copied. When an upstream document
changes, the recorded hash mismatches and the integrity gate fails — documentation
freshness becomes an auditable control (SOC 2 CC7.3 / ISO 27001 A.5.36) rather
than an aspiration.

## Consequences

- (+) One authoritative index and one system description, with no sixth copy of
  upstream prose to drift.
- (+) A reviewer sees exactly which upstream facts moved in a pull-request diff,
  because generated artifacts are committed.
- (+) The allow-list, DPIAs, network policy, and architecture stay in the
  repositories that own them; this hub cannot silently become a stale fork.
- (−) Every claim here must carry a pointer, which is more discipline than pasting
  prose. Accepted: the discipline *is* the control.
- (−) The generated artifacts depend on local sibling clones to regenerate.
  Mitigated by the local-generate / CI-verify model (design spec §2, D2) and the
  loud-partial behavior when a sibling is unavailable.

## Related

- [DOC-0002](DOC-0002-public-abstraction-cap.md) — what may be published.
- [namespace.md](namespace.md) — the read-side qualification mechanism.
- Design spec §3.1 (the load-bearing invariant).
