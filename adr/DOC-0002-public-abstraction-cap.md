# DOC-0002: Public abstraction cap, machine-enforced

- **Status:** Accepted
- **Date:** 2026-09-28
- **Deciders:** org owner (solo era)
- **Compliance:** PCI-DSS Req 1.2/1.3 · SOC 2 CC6.1/CC6.6 · ISO 27001 A.5.9/A.8.25 · GDPR Art. 5(1)(f)/Art. 25

## Context

`jolarca-docs` is declared `visibility: public` and `data_classification: public`
in the control-plane allow-list, and `repo-defaults.yml` caps a public repository
at classification `internal`. Much of the fleet's architecture detail — default-deny
network matrices, segment names, the cardholder-data-environment boundary, internal
database identifiers — is more sensitive than `internal` and must never be
published. Publishing it would aggravate the fleet's blocking finding that
PCI-scope repositories are publicly readable, and would cut against PCI-DSS Req
1.2/1.3.

Conversely, a SOC 2 description of the system does **not** require addresses,
ports, or table names. It requires component roles, boundaries, data categories,
people, and procedures. Capping abstraction therefore costs nothing the standard
asks for and removes everything an attacker would want.

## Decision

Content is capped at **C4 level 1–2** and enforced by a deny-pattern scan in
`scripts/verify.py` that runs over **every committed file** and hard-fails on:

- network addresses and CIDR blocks
- port numbers (any `host:port`, `port N`, or `tcp/N` / `udp/N` form)
- hostnames, VM names, node names, and reserved internal domains
- VPC, subnet, and other cloud resource identifiers
- Kubernetes namespace and NetworkPolicy names
- database schema, table, and column names (targeting the internal schema
  prefixes and `schema.table.column` forms)
- object-storage bucket names and bucket URIs
- cryptographic key identifiers and key material
- cardholder-data-environment segmentation detail

**Permitted vocabulary:** component **roles**, data **categories**, trust
**boundaries**, protocol classes (TLS/mTLS), residency (for example EU), and status
(`designed` / `deployed` / `planned`).

### No suppression, no content exclusion

There is **no suppression mechanism and no allow-list**. A false positive is fixed
by rewriting the text, never by weakening the control — a bypass hatch in the gate
that enforces the cap would defeat its purpose. The scan walks the whole working
tree; the only directories it does not read are non-published tooling dirs
(`.git/`, virtualenvs, linter/type/test caches), which are never committed. Every
authored and generated file is scanned.

### Explicitly out of scope

Git commit digests and CVE identifiers are **not** hostnames or key identifiers and
are permitted. The pattern set is written so that a 40/64-hex digest, a
`file:line` citation, a semantic-version string, an ADR/control identifier, and a
public two-label documentation domain do not trip it — while a three-label internal
hostname, an address, or a port does.

### Test fixtures may not contain real identifiers

A committed forbidden token — even a synthetic one — in a **public** repository
would itself be published and would force either a scan failure or an exclusion
that weakens the control. The design spec (§3.2 "no exclusions" vs §8 "planted
forbidden port in a fixture") is internally inconsistent on this point. Resolution:
committed fixtures under `tests/fixtures/` contain **only structural** violations
(for example a namespace collision or an unparseable heading); the deny-pattern
test materializes forbidden tokens **ephemerally** in a pytest temporary directory
and asserts the scanner fires. The scanner therefore runs with zero content
exclusions and the published tree stays clean. Recorded as F-DOC-06.

## Consequences

- (+) The public repository cannot leak a control-plane identifier without failing
  CI, and the failure names the file, line, and matched token.
- (+) The cap is a decision with a rationale, not a lint rule nobody can explain.
- (−) Authors must think in roles and categories. Accepted: that is the point.
- (−) The pattern set needs maintenance as new identifier shapes appear. A miss is
  treated as a defect: strengthen the pattern and add a test, never exclude a path.

## Related

- [DOC-0001](DOC-0001-owns-no-fact-another-repo-owns.md) — why nothing is copied.
- [../CONTRIBUTING.md](../CONTRIBUTING.md) — the contributor-facing rules.
- Design spec §2.1 (why this is the load-bearing constraint) and §3.2.
