# 07 — Criteria Map

**Purpose:** an assessor's navigation aid. This maps the AICPA Trust Services
**description criteria** (DC1.1–DC1.5) to the section of this description that
satisfies them and to the authoritative evidence, which is cited by pointer and
hashed in [references/manifest.csv](../references/manifest.csv).

## Description criteria (DC series)

| Criterion | Requires | Where addressed | Evidence (upstream, by pointer) |
|---|---|---|---|
| DC1.1 | Description of the entity's system and its boundaries | [01](01-scope-and-boundaries.md), [06](06-data.md) | control-plane allow-list; drift-findings register |
| DC1.2 | Complementary user-entity controls | [01](01-scope-and-boundaries.md) §CUECs | payment-boundary decision |
| DC1.3 | Infrastructure, software, and data | [02](02-infrastructure.md), [03](03-software.md), [06](06-data.md) | infrastructure architecture; isolation model |
| DC1.4 | People and procedures | [04](04-people.md), [05](05-procedures.md) | repo-defaults policy; change-management doc |
| DC1.5 | Carve-out of subservice organizations | [01](01-scope-and-boundaries.md) §Carve-out | PCI scope statement; payment-boundary decision |

<!-- ref: jolarca-control/docs/architecture.md -->

## Common criteria (CC series) — high-level navigation

This description supports, but does not itself constitute, the control narratives.
The authoritative control-to-evidence mapping is owned upstream; the pointers below
are where an assessor starts. Status of each is **designed** unless the deviation
register records otherwise.

| CC series | Theme | Starting evidence (upstream) |
|---|---|---|
| CC6.x | Logical & physical access | isolation model; access-review procedure; key custody |
| CC7.x | System operations & monitoring | observability design; incident runbook; documentation-freshness gate |
| CC8.x | Change management | change-management doc; signed-commit and branch-protection policy |
| CC9.x | Risk & inventory | fleet inventory view; drift-findings register |

The control-plane compliance mapping (CC / GDPR Article / ISO 27001 A. / PCI-DSS
Req cross-walk) is declared in the policy of record and cited, not duplicated:

<!-- ref: jolarca-control/policy/repo-defaults.yml -->

## Open deviations that qualify this description

A Type I description must be honest about design-versus-reality gaps. The following
are open in the authoritative register at the time of writing and qualify the
controls above. They are summarized in [findings/register.md](../findings/register.md)
and owned by `jolarca-control/docs/drift-findings.md`.

| ID | Effect on this description |
|---|---|
| D-01 | PCI-scope repositories publicly readable — aggravation risk; the abstraction cap is this hub's mitigation |
| D-04 | Zero required reviewers — segregation-of-duties limitation ([04](04-people.md)) |
| D-05 | Signed-commit enforcement off at provider — signing is by policy |
| D-10 | No teams; single admin |
| D-18 | Two-factor requirement not enforced org-wide |
| D-19 | Member repository-creation / default-permission below baseline |
| D-20 | CODEOWNERS inert fleet-wide |

<!-- ref: jolarca-control/docs/drift-findings.md -->

## Assertion

This description is prepared for a **SOC 2 Type I** readiness posture: it describes
the **design** of the system and its controls at a point in time, states where the
system is `designed` or `planned` rather than `deployed`, and cites open deviations
rather than concealing them. It is not an assertion of operating effectiveness over
a period.
