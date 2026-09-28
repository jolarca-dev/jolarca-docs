# 01 — Scope and Boundaries

**TSC description criteria:** DC1.1 (boundaries), DC1.2 (complementary
user-entity controls), DC1.5 (carve-out of subservice organizations).

## System boundary

The system is the `jolarca-dev` marketplace platform: the set of services that
present a storefront, process orders, hold identity and consent records, produce
pseudonymous analytics, and are governed by a declarative control plane. The
boundary is **logical**, drawn around the repositories in the control-plane
allow-list (see the [fleet inventory view](../inventory/fleet.md)).

Status: **designed.** The logical boundary is declared and machine-checked; the
running system it describes is largely unprovisioned.

## In scope

| Component role | Namespace | Status |
|---|---|---|
| Storefront / presentation | `APP-` | designed |
| Application & domain services | `APP-` | designed |
| Payment boundary service | `PAY-` | designed |
| Identity & access | `ID-` | designed |
| Consent registry of record | `CONSENT-` | designed |
| Analytics platform (pseudonymous) | `DATA-` | designed |
| Observability | `OBS-` | planned |
| Control plane (allow-list authority) | `CTL-` | designed |
| Documentation hub (this repository) | `DOC-` | designed |

## Out of scope

- **Mission-program (`jol-*`) systems.** A separate program with its own governance
  boundary; the marketplace fleet never manages a mission repository and vice
  versa (fleet-separation rule, `INFRA-0004`).
- **The corporate identities of operators** beyond their use to authenticate to the
  platform.
- **Third-party subservice organizations** listed as carve-outs below.

## Carve-out: payment processing subservice organization

Card processing is performed by an external **payment processor** used as a
subservice organization, described here with the **carve-out method**: the
processor's own controls are excluded from this description and are covered by its
own attestation.

- The platform's design keeps card data entry inside the processor's own hosted
  interface, so primary account numbers never transit platform infrastructure.
  The intended scope reduction is to the lowest self-assessment questionnaire
  class; the authoritative scope statement lives upstream and is cited, not copied.
- The **single payment boundary** decision (`INFRA-0005`) makes exactly one
  service role speak to the processor server-side; every other role is a client of
  that boundary and structurally cannot reach the processor directly.

Status: **designed.** The boundary is ratified by ADR and enforced in code and
network policy by design; the enforcement controls are recorded upstream with
their own status.

<!-- ref: jolarca-infrastructure/security/pci-dss-scope.md -->
<!-- ref: jolarca-infrastructure/docs/adr/0005-single-payment-boundary.md -->

## Complementary user-entity controls (CUECs)

The design assumes the following controls are operated **by the user entity**
(merchant / end user) and are necessary for the platform's controls to achieve
their objectives:

1. Users safeguard their own credentials and do not share accounts.
2. Card data is entered only into the processor's hosted interface presented in
   the user's browser; the platform never requests card data directly.
3. Users configure their consent preferences; the platform records and honours them
   but cannot supply consent on the user's behalf.
4. Merchant users act within the roles granted to them; role definitions are
   platform-provided, assignment decisions are the user entity's.

## Trust boundaries (category level)

Trust boundaries are described at the level of **roles and data categories**, not
addresses or segments. The authoritative default-deny matrices and the isolation
model live upstream and are cited by pointer; reproducing them here would breach
the abstraction cap and duplicate the fact.

- Public → edge/presentation boundary (untrusted to platform).
- Presentation → application/domain boundary.
- Application → payment boundary → processor (the only egress path for payment).
- Application/registry → datastore boundary (encryption and access controls
  upstream).
- Platform → analytics boundary (pseudonymized at ingestion; identity does not
  cross).

<!-- ref: jolarca-infrastructure/security/network-policy.md -->
<!-- ref: jolarca-infrastructure/security/isolation-model.md -->
