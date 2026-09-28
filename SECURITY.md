# Security Policy

## Scope of this repository

`jolarca-docs` is a **public** documentation hub. By design it holds **no
secrets, no credentials, no personal data, and no control-plane identifiers**.
It describes the fleet at the level of component roles, data categories, trust
boundaries, and control status, and points at upstream evidence by reference and
SHA-256 digest (ADR [DOC-0002](adr/DOC-0002-public-abstraction-cap.md)).

The abstraction cap is **machine-enforced**: `scripts/verify.py` runs a
deny-pattern scan over every committed file and fails the build on any network
address, port, hostname, infrastructure identifier, database identifier,
object-storage bucket, key identifier, or CDE segmentation detail. There is no
suppression mechanism.

## Reporting a vulnerability or a leaked identifier

Please report privately. **Do not open a public issue** — a public report of a
leaked identifier is itself a disclosure.

- Preferred: the private vulnerability-reporting path on the `jolarca-dev`
  organization (GitHub private vulnerability reporting is enabled fleet-wide via
  `repo-defaults.yml`).
- Alternative: contact the organization owner through the channel recorded in the
  org profile.

When reporting, include: the file and line, the class of identifier exposed, and
whether the content is committed or only present in a branch/fork.

## What counts as a security incident here

Because this repository is public, the following are treated as incidents of the
highest severity class, not as ordinary bugs:

1. Any real network address, port, hostname, or infrastructure identifier that
   passes review and lands on `main`.
2. Any database schema/table/column name or object-storage bucket name.
3. Any credential, key material, token, or connection string.
4. Any cardholder-data-environment segmentation detail.
5. Any personal data (this repository must never contain personal data; DPIAs and
   processing records live in the private compliance repository).

If you find any of the above, report it privately so it can be removed from
history and the deny-pattern list strengthened to catch the class automatically.

## Supported integrity controls

| Control | Mechanism |
|---|---|
| Abstraction cap | `scripts/verify.py` deny-pattern scan (no exclusions) |
| Secret scanning | Org-level gate (`repo-defaults.yml` `secret_scanning`); see the findings register for the status of the shared CI gate |
| Upstream freshness | `references/manifest.csv` SHA-256 vs. live upstream |
| Signed history | GPG-signed commits (`repo-defaults.yml` `commit_signing_policy`) |
| Branch protection | Required status-check context `lint` (this repo's `make check`) |

## Dependencies

Exactly one runtime dependency (`pyyaml`); dev tooling never ships. Dependabot
proposes every bump as an auditable change (SOC 2 CC7.1, ISO 27001 A.8.8). See
[ADR DOC-0003](adr/DOC-0003-single-runtime-dependency-pyyaml.md).
