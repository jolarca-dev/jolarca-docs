# ADR Namespace Allocation

**Status:** Owned — hand-maintained. **This file is the single source of truth for
ADR prefixes.** `scripts/scan_adrs.py` parses the table below to qualify every ADR
ID in the generated [index](README.md). Prefix allocation is a governance decision,
not a derivable fact, so it lives here and nowhere else.

## Why namespaces exist

The fleet has multiple independent ADR registries that all number from `0001`.
`ADR-0005` means *single payment boundary* in `jolarca-infrastructure` and
*object storage* in `jolarca`, so a bare `ADR-0005` citation is ambiguous — an
auditor asking "show me the decision that authorizes the payment boundary" gets two
different answers. Qualifying every ID with a per-repository prefix
(`INFRA-0005` vs `APP-0005`) removes the collision without touching any upstream
registry.

## Allocation

Every repository in the control-plane allow-list
(`jolarca-control/repos/*.yml`) **must** have a prefix. `scan_adrs.py` hard-fails on
an ADR from a repository with no allocated prefix — silent pass-through is how the
collision arose in the first place.

| Prefix | Repository | Rationale |
|---|---|---|
| `APP-` | `jolarca` | Flagship marketplace application |
| `INFRA-` | `jolarca-infrastructure` | Infrastructure and network policy |
| `COMP-` | `jolarca-compliance` | Compliance program of record |
| `CONSENT-` | `jolarca-consent` | Consent registry of record |
| `CTL-` | `jolarca-control` | Control plane / allow-list authority |
| `SEC-` | `jolarca-security` | Security engineering |
| `PAY-` | `jolarca-payments` | Payment boundary service |
| `ID-` | `jolarca-identity` | Identity and access |
| `DATA-` | `jolarca-data` | Analytics platform |
| `LEGAL-` | `jolarca-legal` | Legal texts and obligations |
| `DR-` | `jolarca-dr` | Disaster recovery |
| `OBS-` | `jolarca-observability` | Observability stack |
| `RUN-` | `jolarca-runbooks` | Operational runbooks |
| `VEN-` | `jolarca-vendor` | Vendor management |
| `HERMES-` | `jolarca-hermes-agents` | Hermes AI agent implementations |
| `DOC-` | `jolarca-docs` | This repository |

### Deviation from the design spec

The design spec (§3.4) allocated ten prefixes. The allow-list has since grown to
fifteen repositories; `CONSENT-`, `DR-`, `OBS-`, `RUN-`, and `VEN-` are added here
so the completeness check passes. This matters concretely: `jolarca-consent` holds
four ADRs, so implementing the spec's ten-row table verbatim would hard-fail
`make generate`. The gap is recorded in
[findings/register.md](../findings/register.md) (F-DOC-05).

## Rules

1. **Never renumber, never move.** Qualified IDs are applied *read-side* in the
   generated index only. Upstream ADR files keep their local numbering, because
   live citations in other repositories (for example the network policy citing a
   payment-boundary ADR) would break, and renumbering violates the org
   immutability rule ("never delete, only supersede").
2. **One prefix per repository.** A prefix is never reused or reassigned. Retiring
   a repository retires its prefix; it is not recycled.
3. **A new allow-list repository needs a prefix here before it can hold an ADR.**
   Adding the row is a normal governance change and is the fix for a
   `scan_adrs.py` hard-fail.
4. **Prefixes are uppercase and end in a hyphen** so the qualified form reads
   `PREFIX-0000`.
