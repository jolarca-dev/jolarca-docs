# Contributing to jolarca-docs

This repository is a **public** compliance artifact. Contributing here is
different from contributing to application code: the primary risk is not a bug,
it is **disclosing a control-plane identifier** or **duplicating a fact another
repository owns**. Both are enforced by machine gates, not by reviewer vigilance.

Read [QODER.md](QODER.md) for the AI-assisted-change rules and
[SECURITY.md](SECURITY.md) for reporting.

## The two invariants

1. **Owns no fact another repository owns** (ADR
   [DOC-0001](adr/DOC-0001-owns-no-fact-another-repo-owns.md)). If another
   repository owns a fact, link it — do not restate it. Restating creates a
   second copy that will drift.
2. **The abstraction cap** (ADR
   [DOC-0002](adr/DOC-0002-public-abstraction-cap.md)). This is a public repo;
   concrete infrastructure identifiers must never appear in it.

## The abstraction cap is enforced, not advisory

`scripts/verify.py` scans every committed file and **hard-fails** on:

- network addresses and CIDR blocks
- port numbers (in any `host:port`, `port N`, or `tcp/N` form)
- hostnames, VM names, node names
- VPC and subnet names, and other cloud resource identifiers
- Kubernetes namespace and NetworkPolicy names
- database schema, table, and column names
- object-storage bucket names
- cryptographic key identifiers and key material
- cardholder-data-environment segmentation detail

**There is no suppression mechanism and no path exclusion.** If the scan fires on
your text, rewrite the text to describe the *role*, *category*, *boundary*, or
*status* instead of the identifier. Do not open a pull request that weakens a
pattern, adds an allow-list entry, or excludes a path — it will be rejected, and
proposing it is itself treated as a red flag.

Write with the **permitted vocabulary**: component roles, data categories, trust
boundaries, protocol classes (TLS/mTLS), residency (for example EU), and status
(`designed` / `deployed` / `planned`).

## Citing upstream documents

Never copy upstream prose. Cite it with a reference marker on its own line:

```text
<!-- ref: jolarca-infrastructure/security/network-policy.md -->
```

`make generate` resolves every marker against the local sibling clones, computes
its SHA-256, and writes `references/manifest.csv`. The verifier then checks that
every marker has a manifest row and that every recorded hash still matches the
live upstream file. If an upstream document moves or changes, the gate fails —
that is the freshness control working, not a nuisance.

## Changing the generated artifacts

`adr/README.md`, `inventory/fleet.md`, and `references/manifest.csv` are
**generated**. Never hand-edit them. Change the generator in `scripts/`, or the
upstream source, then run `make generate` and commit the diff. The committed diff
is the audit trail.

### Adding a repository namespace

ADR prefixes are allocated in [adr/namespace.md](adr/namespace.md), which is
**owned** here (prefix allocation is a governance decision, not a derivable
fact). Every repository in the control-plane allow-list must have a prefix;
`scan_adrs.py` **hard-fails** on an ADR from a repository with no allocated
prefix. To add one, edit the table in `namespace.md` and explain the allocation.
ADRs are never renumbered and never moved — qualified IDs are applied read-side.

## Dual-state honesty

Every component, control, and flow carries an explicit `designed` / `deployed` /
`planned` status. Do not write the system description in the present tense. If you
cannot source a status from verified evidence, mark it `planned` and say why.

## Workflow

1. Create a branch. Commit messages and PR titles follow **Conventional Commits**
   (`feat:`, `fix:`, `docs:`, `chore:`, and so on).
2. Make your change.
3. Run `make generate` if you touched anything a generator reads.
4. Run `make verify-strict` locally (it requires the sibling fleet to be present)
   and `make check`. Both must pass.
5. Commit with `git commit -S` (GPG-signed). Signed commits are mandatory for
   human operators and are the compensating control for the solo-era 0-review
   deviation.
6. Open a pull request. The required status-check context is **`lint`**, which
   runs `make check`.

History is **squash-only and linear**; force-pushes and branch deletion are
blocked.

## Failure behavior is part of the contract

A generator or scanner that cannot read its input must **fail loudly**, never
emit a smaller result. A partial ADR index is indistinguishable from a complete
one for a system with fewer decisions — that is exactly how the fleet's shared CI
gates shipped inert. Do not add `|| true`, a bare `except`, or a silent fallback.
When the fleet is partially unavailable, the generators write a visible
`<!-- PARTIAL: N siblings unavailable -->` banner into every artifact so a
partial result can never be committed unnoticed.

## Markdown conventions

`.markdownlint.json` mirrors the `jolarca-compliance` configuration. `MD013`
(line length) is off; the other disabled rules are documented in that file. Do
not re-enable or disable rules without updating this section.
