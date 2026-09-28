# 02 — Infrastructure

**TSC description criteria:** DC1.3 (infrastructure).

Infrastructure is described at **C4 level 1–2** as **roles**, never as addresses,
hostnames, or host placement. The authoritative topology, capacity model, and
isolation design live upstream and are cited by pointer; restating them here would
duplicate the fact and breach the abstraction cap.

## Hosting model

The platform is designed to be **self-hosted** rather than run on a general-purpose
cloud platform, so that data custody and residency stay under the operator's
control (decision `APP-0012`). Residency is **EU**. Status: **designed** — the
decision is ratified; the production estate is not yet fully provisioned.

<!-- ref: jolarca/docs/ARCHITECTURE_DECISION_RECORDS.md -->

## Infrastructure roles

| Role | Responsibility (category level) | Status |
|---|---|---|
| Virtualization / host platform | Provides the compute substrate for all other roles | designed |
| Edge / reverse proxy | Terminates TLS, presents the public surface, rate-limits | designed |
| Application runtime | Hosts the domain and presentation software roles | designed |
| Primary datastore role | System of record for transactional and relational data | designed |
| Cache role | Holds sessions and hot, rebuildable data | designed |
| Search role | Derived, rebuildable index for catalog search | designed |
| Object-storage role | Stores binary/large objects; no cleartext personal data by design | designed |
| Secrets-management role | Custody of key material and credentials | designed |
| Backup role | Scheduled backups with restore verification | designed |
| Observability role | Logs, metrics, traces (telemetry category only) | planned |

A documented resource-split ratio governs allocation between the two program
boundaries; the rationale is an upstream decision (`INFRA-0001`) and is cited, not
restated.

<!-- ref: jolarca-infrastructure/docs/architecture.md -->

## Protection of the infrastructure

- **Segmentation.** A default-deny posture between roles is defined upstream; the
  matrices carry segment and host detail that is deliberately **not** reproduced
  here (abstraction cap). See the isolation model and network policy by pointer.
- **Key custody.** Key material is held in a dedicated custody role; identifiers
  and locations are upstream.
- **Backup and restore.** Backups are scheduled with periodic restore
  verification; the runbook is upstream. State backups are the first runbook step.
- **Hardening baseline.** A CIS-aligned baseline and a deviation register are
  maintained upstream.

Status of these protections: **designed**, except where the authoritative
deviation register records an open gap. Two gaps are material to infrastructure
governance and are cited by ID rather than restated: the single-copy state custody
finding and the organization-settings findings (see
[findings/register.md](../findings/register.md) and the upstream register).

<!-- ref: jolarca-infrastructure/security/isolation-model.md -->
<!-- ref: jolarca-infrastructure/security/key-custody.md -->
<!-- ref: jolarca-infrastructure/docs/backup-restore-runbook.md -->
<!-- ref: jolarca-infrastructure/security/cis-baseline.md -->

## What is deliberately omitted

Addresses, CIDR ranges, ports, hostnames, VM/node names, VPC/subnet names, and the
cardholder-data-environment segmentation detail. An assessor who needs them works
from the private upstream repositories under a confidentiality obligation; this
public description establishes **roles, boundaries, residency, and status**, which
is what the description criteria require.
