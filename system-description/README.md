# SOC 2 Description of the System

This is the **description of the system** for the `jolarca-dev` marketplace
platform, prepared to satisfy the AICPA Trust Services Criteria description
requirements (DC1.1–DC1.5) for a **SOC 2 Type I** readiness assessment. Type I
assesses the **design** of controls at a point in time; it does not assert
operating effectiveness over a period (that is Type II).

It is the artifact the fleet did not previously have. It is owned here
(ADR [DOC-0001](../adr/DOC-0001-owns-no-fact-another-repo-owns.md)) because no
single repository can describe a system that spans all of them.

## How to read this

Three rules apply to every page:

1. **Dual-state.** Every component, control, and flow carries an explicit status.
   Nothing is written in the present tense unless it is `deployed` with evidence.

   | Status | Meaning |
   |---|---|
   | `deployed` | Provisioned and relied upon; operational evidence exists |
   | `designed` | Specified in an approved design or ADR; not yet provisioned |
   | `planned` | Intended; not yet specified in implementable detail |

2. **Abstraction-capped.** This is a public document. It describes **roles,
   categories, boundaries, and status** only — never addresses, ports, hostnames,
   or database identifiers (ADR
   [DOC-0002](../adr/DOC-0002-public-abstraction-cap.md)). Detail lives upstream
   and is cited by pointer.

3. **Pointer, not copy.** Authoritative evidence stays in the repository that owns
   it. Citations appear as `<!-- ref: … -->` markers resolved into
   [references/manifest.csv](../references/manifest.csv) with a SHA-256, so a
   change upstream is detected rather than silently drifting.

## Current posture (read before relying on this)

The platform is **predominantly `designed` and `planned`, not `deployed`.** The
control plane describes itself as not yet authoritative, staging is unprovisioned
by design, and several fleet-wide deviations are open in the authoritative register
(`jolarca-control/docs/drift-findings.md`). A description written as though the
system were live would misrepresent it to an assessor. Where a control is
`designed`, that is stated; where an open deviation undercuts it, the deviation ID
is cited.

## Sections

| # | Section | TSC description criteria |
|---|---|---|
| 01 | [Scope and boundaries](01-scope-and-boundaries.md) | DC1.1, DC1.2, DC1.5 |
| 02 | [Infrastructure](02-infrastructure.md) | DC1.3 |
| 03 | [Software](03-software.md) | DC1.3 |
| 04 | [People](04-people.md) | DC1.4 |
| 05 | [Procedures](05-procedures.md) | DC1.4 |
| 06 | [Data](06-data.md) | DC1.1, DC1.3 |
| 07 | [Criteria map](07-criteria-map.md) | DC1.1–DC1.5 navigation |

The authoritative deviation register for the fleet is
`jolarca-control/docs/drift-findings.md`; this description cites it and does not
fork it.

<!-- ref: jolarca-control/docs/drift-findings.md -->
<!-- ref: jolarca-compliance/certifications/README.md -->
