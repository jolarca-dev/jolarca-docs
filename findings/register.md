# Findings Register

Defects discovered **outside** this repository while building it, plus the internal
design-spec gaps this implementation had to resolve. Each entry carries evidence
(`file:line` where applicable), the affected control, the owning repository, and a
disposition.

**Disposition policy (design spec §2, D4):** register everything; fix only this
repository's own files. Cross-repo defects are recorded here for their owners, not
silently patched — patching another repository from a documentation hub would
itself be an unreviewed change to a system this repo does not own.

The authoritative fleet deviation register is
`jolarca-control/docs/drift-findings.md` (IDs `D-nn`). This register uses `F-DOC-nn`
for documentation-hub-specific findings and cites `D-nn` where they overlap.

<!-- ref: jolarca-control/docs/drift-findings.md -->

## Cross-repo defects (registered, not fixed here)

### F-DOC-01 — Governance-file CI gate can never fail

- **Evidence:** `.github/.github/workflows/ci-base.yml:70` tests `${#MISSUES[@]}`,
  a typo for the `MISSING` array populated on line 63. The tested array is unset, so
  its length is always `0` and the guard on line 71 never runs.
- **Effect:** every repository that consumes the reusable baseline believes its
  required governance files (README, SECURITY, CONTRIBUTING, CHANGELOG, LICENSE) are
  checked. They are not.
- **Control:** SOC 2 CC8.1 · ISO 27001 A.8.25.
- **Owner:** `.github`.
- **Disposition:** registered. This repository does **not** rely on the shared gate —
  `scripts/verify.py` step 1 is a working reimplementation that fails on a missing or
  empty governance file.

### F-DOC-02 — Secret-scan CI gate is inert

- **Evidence:** `.github/.github/workflows/ci-base.yml:109` pins
  `gitleaks/gitleaks-action` to a non-resolvable digest (a repeating placeholder
  tail), and line 112 sets `continue-on-error: true`. Meanwhile
  `jolarca-control/repos/jolarca-docs.yml:55` declares `required_gates.secret_scan:
  true`.
- **Effect:** the declared secret-scan gate neither resolves nor blocks. A secret
  could merge unimpeded.
- **Control:** SOC 2 CC6.3 · PCI-DSS Req 6.5.
- **Owner:** `.github`.
- **Disposition:** registered. This repository does **not** inherit the inert action;
  it relies on org-level secret scanning plus its own deny-pattern scan. A verified
  digest must replace the placeholder — inventing one would reproduce this defect.

### F-DOC-03 — Fleet asset inventory disagrees with itself

- **Evidence:** repository counts of 5, 6, and 14 appear across org and control-plane
  documents, while the allow-list currently contains **15** `repos/*.yml` files.
- **Effect:** no accurate inventory of information assets exists fleet-wide.
- **Control:** ISO 27001 A.5.9 · SOC 2 CC9.2.
- **Owner:** `.github`, `jolarca-control`.
- **Disposition:** registered. `inventory/fleet.md` is generated from the allow-list
  and `scripts/verify.py` step 7 asserts the declared count equals the actual file
  count, so this hub machine-catches the drift going forward. The allow-list remains
  the system of record.

### F-DOC-04 — DPIAs embed data flows instead of referencing one

- **Evidence:** `jolarca-compliance/dpia/` assessments each hand-draw their own
  inline data flow rather than citing a canonical map; one names an internal database
  table.
- **Effect:** four independent descriptions of one system, with no reconciliation —
  a coherence gap and a duplication-drift risk.
- **Control:** GDPR Art. 30 / Art. 35.
- **Owner:** `jolarca-compliance`.
- **Disposition:** registered. This hub publishes the **category-level** canonical
  flow ([../architecture/data-flow-categories.mmd](../architecture/data-flow-categories.mmd))
  that the DPIAs should cite. The detailed flows stay upstream (the compliance repo is
  private); the internal table identifier must never be copied here (abstraction cap).

## Internal design-spec gaps (resolved in this implementation)

### F-DOC-05 — Namespace table in the design spec is incomplete

- **Evidence:** design spec §3.4 allocates ten ADR prefixes; the allow-list has
  fifteen repositories. `jolarca-consent` holds four ADRs but had no prefix, so
  implementing §3.4 verbatim would hard-fail `make generate`.
- **Control:** internal generation correctness.
- **Owner:** `jolarca-docs`.
- **Disposition:** **fixed here** by extending
  [../adr/namespace.md](../adr/namespace.md) to all fifteen allow-list repositories
  (`CONSENT-`, `DR-`, `OBS-`, `RUN-`, `VEN-` added). This is an owned file, not a
  cross-repo write.

### F-DOC-06 — Design spec is internally inconsistent on fixture tokens

- **Evidence:** §3.2 mandates the deny-scan cover the entire repository with **no
  path exclusions**; §8 asks for a committed fixture containing a **planted forbidden
  token**. In a public repository both cannot hold: a committed forbidden token is
  itself published and would either fail the scan or force an exclusion.
- **Control:** PCI-DSS Req 1.2/1.3 · SOC 2 CC6.6 (the abstraction cap).
- **Owner:** `jolarca-docs`.
- **Disposition:** **resolved** in ADR [DOC-0002](../adr/DOC-0002-public-abstraction-cap.md):
  committed fixtures carry only **structural** violations; the deny-pattern test
  materializes forbidden tokens **ephemerally** in a temporary directory. The scanner
  keeps zero content exclusions.

## Config-of-record observation (deferred to the operator)

### F-DOC-07 — This repo's allow-list entry: one deviation remains

- **Evidence:** `jolarca-control/repos/jolarca-docs.yml:37` sets
  `require_code_owner_reviews: false`, against the `repo-defaults.yml` baseline of
  `true` (only `.github` is exempt). Note the framework list at lines 48–52 **now
  includes** `soc2`, `iso27001`, `gdpr`, and `pci-dss`, so the previously recorded
  `pci_dss` omission is already resolved — no action needed there.
- **Control:** SOC 2 CC6.1 / CC8.1.
- **Owner:** `jolarca-control`.
- **Disposition:** **registered, not auto-edited.** Editing the control plane on a
  partly stale premise is exactly the kind of unreviewed cross-repo change this hub
  must not make silently. Two honest options for the operator: (a) set the value to
  `true` to match the (inert) baseline, or (b) register `jolarca-docs` as an exempt
  deviation in `repo-defaults.yml`. Note `require_code_owner_reviews` is inert
  fleet-wide (D-20: no teams exist), so either choice is documentation-accuracy, not
  a live control change. Awaiting operator decision.
