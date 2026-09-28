# 03 — Software

**TSC description criteria:** DC1.3 (software).

Software is described by **role and responsibility**, mapped to the namespace that
owns it. **Versions and host placement are deliberately omitted** — a version plus
a host is a fingerprint an attacker can use, and the abstraction cap forbids it.
The authoritative module breakdown, sequence flows, and protocol contracts live
upstream and are cited by pointer.

## Software roles

| Role | Responsibility (category level) | Namespace | Status |
|---|---|---|---|
| Storefront / presentation | Public catalog and customer journeys | `APP-` | designed |
| Domain & application services | Orders, listings, moderation, business rules | `APP-` | designed |
| Payment boundary service | Sole server-side integration with the payment processor | `PAY-` | designed |
| Identity & access service | Authentication, sessions, roles | `ID-` | designed |
| Consent registry | Independent, tamper-evident system of record for consent | `CONSENT-` | designed |
| Analytics platform | Pseudonymous warehouse and ingestion; no cleartext identity | `DATA-` | designed |
| Observability stack | Telemetry collection and alerting | `OBS-` | planned |
| Control plane | Declarative allow-list and policy authority for the fleet | `CTL-` | designed |
| Documentation hub | This repository: index, system description, inventory view | `DOC-` | designed |
| Legal texts service | Versioned legal/regulatory text as build artifacts | `LEGAL-` | designed |
| Vendor management | Vendor and subservice-organization records | `VEN-` | planned |
| Disaster recovery | Recovery orchestration and objectives | `DR-` | planned |
| Runbooks | Operational procedures as versioned artifacts | `RUN-` | designed |

## Design properties relevant to the control environment

- **Single payment boundary.** Exactly one software role integrates with the
  payment processor server-side; all others are clients of it and cannot reach the
  processor directly (`INFRA-0005`, `PAY-`).
- **Consent independence.** The consent registry is a separate system of record
  from the software that requests consent, so the party needing consent does not
  own the proof (`CONSENT-0001`). Records are tamper-evident by an append-only,
  hash-chained design (`CONSENT-0002`).
- **Pseudonymization at ingestion.** Analytics never receives cleartext identity;
  identifiers are pseudonymized at the ingestion boundary (`DATA-0001`).
- **Declarative control plane.** Fleet structure and policy are data, validated by
  scripts, not hand-applied configuration (`CTL-`).

Each property above is a decision owned upstream; the qualified ID is given so an
assessor can retrieve the authoritative record from the
[ADR index](../adr/README.md).

<!-- ref: jolarca/docs/architecture/01-modular-breakdown.md -->
<!-- ref: jolarca/docs/architecture/07-communication-protocols.md -->

## Change control for software

Software changes follow the fleet change-management procedure: pull request,
required status checks, squash-only linear history, and GPG-signed commits. The
procedure is described in [05-procedures.md](05-procedures.md) and owned upstream.
