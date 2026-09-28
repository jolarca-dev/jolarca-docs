# 04 — People

**TSC description criteria:** DC1.4 (people).

This section states the human reality of the system plainly, including its
limitations. A description that implied a staffed security function where none
exists would misrepresent the control environment to an assessor.

## Operating model: single-operator era

The platform is operated by a **single org owner** in what the control plane calls
the *single-operator era*. There are **no teams** in the organization; access is
exercised through org ownership by one person. This is recorded upstream as a
deviation and cited here by ID, not restated as though it were a designed control.

| Role | Held by | Status |
|---|---|---|
| Org owner / operator | one named individual | deployed |
| Security & compliance responsibility | same individual (no segregation) | deployed |
| Data protection responsibility | advisory / external, engaged as needed | designed |
| Independent reviewer | none in the single-operator era | planned |
| External SOC 2 assessor | to be engaged for Type I | planned |

## Segregation of duties — stated limitation

With one operator, **segregation of duties cannot be fully achieved.** The
compensating controls are:

1. **GPG-signed commits** attribute every change to a key holder, so no change is
   anonymous even though a second human does not review it. This is the declared
   compensating control for the zero-required-reviewers deviation.
2. **Machine gates** (branch protection, required status checks, the integrity gate
   in this repository) enforce policy that a lone human could otherwise override.
3. **Declarative control plane** means changes to fleet structure are reviewed as
   data diffs rather than applied by hand.

These compensate for, but do not eliminate, the single-operator concentration risk.
The open deviations that describe this honestly are in the authoritative register
and summarized in [findings/register.md](../findings/register.md):

- **D-04** — zero required approving reviewers (solo era).
- **D-05** — GitHub-side signed-commit enforcement is off; operators sign by policy
  as the compensating control.
- **D-10** — no teams; single admin.
- **D-18** — two-factor requirement desired on, live off at the time of record.
- **D-19** — member repository-creation and default-permission settings below the
  desired baseline.

<!-- ref: jolarca-control/policy/repo-defaults.yml -->

## Personnel practices

- Access is granted on least-privilege intent; the desired org baseline is no
  default read access and no member-created repositories.
- Personnel and HR practices, training, and the code of conduct are owned by the
  compliance repository and are cited by pointer, never copied here.
- Access reviews are a defined procedure (see
  [05-procedures.md](05-procedures.md)); their cadence and evidence live upstream.

## On change of operating model

When a second operator onboards, the compensating controls above are intended to be
replaced by real segregation: raise required reviewers from zero, enable
GitHub-side signed-commit enforcement, and create teams. Those transitions are
tracked as deviations in the authoritative register, not assumed here.
