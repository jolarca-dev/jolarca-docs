# 06 — Data

**TSC description criteria:** DC1.1 (data), DC1.3.

Data is described by **category and residency**, never by schema, table, or column
name. The authoritative classification scheme, records of processing, and DPIAs live
upstream and are cited by pointer. The category-level flow diagram is in
[architecture/data-flow-categories.mmd](../architecture/data-flow-categories.mmd).

## Residency

Personal data is designed to reside in the **EU**, consistent with the self-hosted
model (`APP-0012`) and the data-sovereignty rationale behind it. No category is
designed to leave EU residency except where a carve-out subservice (the payment
processor) processes it under its own terms.

## Data categories

| Category | Sensitivity | Pseudonymized? | Residency | Status |
|---|---|---|---|---|
| Customer identity & contact | confidential | no | EU | designed |
| Authentication credentials | restricted | n/a (secret) | EU | designed |
| Consent records | confidential | no | EU | designed |
| Order & transaction data | confidential | no | EU | designed |
| Payment references / tokens | confidential | no PAN held | EU | designed |
| Catalog & listing data | internal | no | EU | designed |
| Analytics warehouse data | internal | **yes, at ingestion** | EU | designed |
| Observability telemetry | internal | minimized | EU | planned |
| Legal & regulatory texts | public/internal | no | EU | designed |
| Governance & documentation | public | no | EU | designed |
| Vendor / subservice records | internal | no | EU | planned |

**Card data.** Primary account numbers are **not** a stored category: card entry
occurs in the payment processor's hosted interface (carve-out, see
[01-scope-and-boundaries.md](01-scope-and-boundaries.md)), so the platform holds
payment references and tokens, not PANs.

## Minimization and pseudonymization

- Analytics receives **pseudonymous** data only: identifiers are salted hashes and
  free-text identifiers are dropped at the ingestion boundary (`DATA-0001`). The
  warehouse is designed so it cannot answer "who" questions; identity questions
  route back to the product boundary through the data-subject-request process.
- Consent records are held in an **independent, tamper-evident** registry separate
  from the software that requests consent (`CONSENT-0001`, `CONSENT-0002`).
- This repository holds **no personal data and no credentials** by construction; the
  abstraction cap and the deny-pattern scan enforce it.

<!-- ref: jolarca-control/docs/data-classification.md -->
<!-- ref: jolarca-compliance/dpia/register.md -->
<!-- ref: jolarca-data/docs/adr/0001-pseudonymize-at-ingestion.md -->

## Records of processing and DPIAs

The GDPR Article 30 record of processing and the Article 35 DPIAs are owned by the
compliance repository. This hub publishes the **category-level data-flow view** that
those DPIAs should cite, so that four processing assessments describe one system
coherently instead of each embedding its own divergent copy. The DPIA register is
cited by pointer above; the individual assessments are not reproduced here.

## Retention and erasure

Retention schedules and the erasure/anonymization procedure are owned upstream
(`COMP-`, `DATA-`). Design intent: financial records are **anonymized, not
deleted**, to preserve legal obligations while removing identifiability
(`COMP-0001`); erasure is **verifiable** because the analytics warehouse checks that
nothing attributable to an erased subject remains.

## What is deliberately omitted

Schema, table, and column names; bucket names; record counts; and any sample of
real or plausibly real personal data.
