# 05 — Procedures

**TSC description criteria:** DC1.4 (procedures).

Procedures are **pointed to, never copied.** Each procedure is owned by the
repository that authors and maintains it; this section establishes that the
procedure exists, who owns it, and its design/deployment status. Copying procedure
text here would create a second version that drifts from the authoritative one.

## Procedure inventory

| Procedure | Owner (namespace) | Status | Authoritative source |
|---|---|---|---|
| Change management | `CTL-` | designed | control-plane change-management doc |
| Incident response | `INFRA-` / `COMP-` | designed | infrastructure incident runbook |
| Backup and restore | `INFRA-` | designed | backup/restore runbook |
| Access provisioning & review | `INFRA-` / `SEC-` | designed | access-review procedure |
| Deployment / release | `INFRA-` | designed | deployment-strategy doc |
| Vulnerability management | `SEC-` | designed | CIS baseline + dependency gates |
| Data retention & erasure | `COMP-` / `DATA-` | designed | compliance retention records |
| Security awareness & training | `COMP-` | planned | compliance training records |
| Vendor / subservice management | `VEN-` / `COMP-` | planned | vendor assessments |
| Documentation freshness (this repo) | `DOC-` | designed | the integrity gate (`make verify`) |

<!-- ref: jolarca-control/docs/change-management.md -->
<!-- ref: jolarca-infrastructure/docs/incident-runbook.md -->
<!-- ref: jolarca-infrastructure/docs/backup-restore-runbook.md -->
<!-- ref: jolarca-infrastructure/security/access-review.md -->
<!-- ref: jolarca-infrastructure/docs/deployment-strategy.md -->

## Change management (the procedure this repository depends on)

Changes to fleet structure and policy are made as **data diffs** against the
declarative control plane and as **pull requests** against repositories, not as
hand-applied configuration. The controls that make this auditable:

1. Pull request with required status checks (the `lint` context for this repo).
2. Squash-only, linear history; force-push and branch deletion blocked.
3. GPG-signed commits attributing every change to a key holder.
4. Plan-first for material changes: a design spec precedes implementation.

Status: **designed**, with the single-operator limitations stated in
[04-people.md](04-people.md).

## Documentation freshness as a procedure

This repository adds one procedure of its own: **documentation freshness is a
control, not an intention.** Every upstream citation carries a SHA-256 in
[references/manifest.csv](../references/manifest.csv); the integrity gate recomputes
each hash and fails when an upstream document has moved or changed without this hub
being regenerated. That turns "are the docs current?" into a machine-answered
question (SOC 2 CC7.3 / ISO 27001 A.5.36).

Status: **designed** (implemented by `scripts/verify.py` in this repository).

## What is deliberately omitted

Runbook steps that name hosts, credentials, or infrastructure identifiers. Those
live in the private upstream runbooks; a public procedure index that reproduced
them would breach the abstraction cap.
