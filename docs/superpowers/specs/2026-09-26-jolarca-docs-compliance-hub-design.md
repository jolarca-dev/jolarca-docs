# jolarca-docs — Compliance Documentation Hub: Design

**Date:** 2026-09-26
**Status:** Approved for planning
**Repo:** `jolarca-docs` (declared in `jolarca-control/repos/jolarca-docs.yml`, `launch_status: planned`)
**Compliance level:** SOC 2 Type II · GDPR · ISO 27001:2022 · PCI-DSS 4.0

---

## 1. Problem

The `jolarca-dev` fleet has substantial architecture and compliance documentation.
It has **no index of it**, and three specific artifacts that no repository owns.
Verified against the 11 repositories present under `/opt/jolarca/repos/` on
2026-09-26.

### 1.1 No SOC 2 description of the system

`jolarca-compliance/certifications/soc2-type1/README.md` lists a readiness
assessment and control narratives. `certifications/README.md` schedules
**SOC 2 Type I readiness in Q4 2026**. No artifact anywhere in the fleet
satisfies the TSC description criteria (infrastructure, software, people,
procedures, data, boundaries, complementary user-entity controls, carve-outs).
This is a genuine audit blocker with a date attached.

### 1.2 Three colliding ADR namespaces

| Registry | ADR-0001 | ADR-0005 |
|---|---|---|
| `jolarca/docs/ARCHITECTURE_DECISION_RECORDS.md` | Monorepo with domain-bounded Django apps | Object storage: MinIO dev / S3-compatible prod |
| `jolarca-infrastructure/docs/adr/README.md` | 90/10 split rationale | **Single payment boundary** |
| `jolarca-compliance/docs/adr/README.md` | Anonymize-don't-delete for financial records | — |

A fourth registry exists at `jolarca-control/docs/adr/`. The collision is
already producing ambiguous citations: `jolarca-infrastructure/security/network-policy.md`
cites "ADR-0005" for the payment boundary, while `jolarca/docs/ARCHITECTURE_DECISION_RECORDS.md`
cites "ADR-0001" for the same invariant. An auditor asking "show me the decision
that authorizes the payment boundary" receives two different ADR-0005s. This is
a SOC 2 CC8.1 / ISO 27001 A.8.32 traceability defect, and no repository owns the fix.

### 1.3 The asset inventory disagrees with itself

| Source | Repo count |
|---|---|
| `.github/profile/README.md` | 5 |
| `jolarca-control/README.md` structure block | 6 `repos/*.yml` |
| `jolarca-control/docs/architecture.md` | "14 YAML files" |
| `jolarca-control/repos/*.yml` (actual) | **15** |
| Present on disk | 10 + `.github` |

ISO 27001 A.5.9 and SOC 2 CC9.2 require an accurate inventory of information
assets. There is currently no accurate one.

### 1.4 DPIA data flows are duplicated, not referenced

The premise that "DPIAs are only as good as the data-flow maps they reference"
is directionally correct, but the actual defect is sharper: the DPIAs do not
reference a data-flow map — **each embeds its own inline copy**.
`jolarca-compliance/dpia/003-payments-and-vat/dpia.md` §1 hand-draws the flow
in ASCII, naming internal tables. Four DPIAs therefore maintain four
independent descriptions of one system, with no canonical map and no
reconciliation mechanism. That is a GDPR Art. 30 / Art. 35 coherence gap.

### 1.5 Existing coverage that must NOT be duplicated

Detailed architecture already exists and stays where it is:

- `jolarca-infrastructure/security/network-policy.md` — default-deny matrices
- `jolarca-infrastructure/security/isolation-model.md` — trust boundaries
- `jolarca-infrastructure/docs/architecture.md` — 90/10 topology
- `jolarca-infrastructure/docs/secrets-flow.md`, `threat-model.md`
- `jolarca/docs/architecture/01-07` — modular breakdown, sequences, ERD, protocols
- `jolarca-compliance/dpia/*` — per-processing flows
- `jolarca-control/docs/architecture.md` — control-plane diagram

The fleet's existing failure mode is **five places for one fact to drift**
(see dual Terraform state ownership, finding D-13). A new repository that
copies architecture prose makes audits harder, not easier.

---

## 2. Decisions taken

Four decisions were settled before this design. Each is binding.

| # | Decision | Choice | Rejected alternatives |
|---|---|---|---|
| D1 | Visibility vs. content sensitivity | **Public-safe, abstraction-capped.** Keep `visibility: public` / `data_classification: public` as declared. Cap content at C4 L1–L2. Detailed network matrices and DPIA flows stay upstream, linked by pointer + hash. | Reclassify to private/internal; two-tier split across a new private repo |
| D2 | Freshness mechanism | **Local-generate, CI-verify.** `make generate` scans local clones; the CI `lint` context only verifies committed output. | CI-generate via GitHub API (needs a PAT reading private PCI-scope repos from a public repo — unacceptable given D-18); hand-written only (reproduces the drift already in evidence) |
| D3 | Designed vs. deployed | **Dual-state.** Every component, control and flow carries an explicit `designed` / `deployed` / `planned` status sourced from verified evidence. | Design-only with a deviations appendix (buries blocking findings D-01/D-18); deployed-only (describes an almost-empty system) |
| D4 | Cross-repo defects | **Register all; fix only `jolarca-control/repos/jolarca-docs.yml`**, which is this repo's own config of record. | Fix the inert CI gates now (extra repo, extra PR, delays landing); register only and touch nothing (provisions the repo from a knowingly wrong declaration) |

### 2.1 Why D1 is the load-bearing constraint

`jolarca-control/policy/repo-defaults.yml` sets `max_classification_for_public: "internal"`.
The default-deny matrices carry hostnames, ports, segment names and the CDE
boundary. Publishing those in a public repository would aggravate **blocking
finding D-01** ("four PCI-scope repos are publicly readable") and cut against
PCI-DSS Req 1.2/1.3. Conversely, the SOC 2 description of the system does not
require port numbers — it requires component roles, boundaries, data categories,
people and procedures. Abstraction capping therefore costs nothing the standard
asks for and removes everything an attacker would want.

### 2.2 Why D3 is required rather than stylistic

`jolarca-control` declares itself "NOT YET AUTHORITATIVE"; staging is
unprovisioned by design; Terraform state is a single copy on one host (D-02);
D-01 and D-18 are blocking; six allow-listed repositories do not exist on
GitHub. A description written in the present tense would misrepresent the
system to the auditor. One written only about live components would describe an
almost-empty system and understate the control environment. Type I assesses
**design** at a point in time, so dual-state is the correct artifact.

---

## 3. Architecture

### 3.1 The load-bearing invariant

> **`jolarca-docs` owns no fact that another repository owns.**

It owns exactly two artifacts that are homeless today, plus one derived view:

| Owned here | Why it is safe to own |
|---|---|
| Cross-repo ADR index (qualified IDs) | No repository can index itself; the collision exists *between* registries |
| SOC 2 description of the system | Exists nowhere in the fleet; due Q4 2026 |
| Fleet inventory **view** | Generated read-only from `jolarca-control/repos/*.yml`, which **remains** the A.5.9 system of record |

Everything else is a **pointer + SHA-256** in `references/manifest.csv`. No
prose is copied. When an upstream document changes, the hash mismatches and CI
fails. Documentation freshness thereby becomes an auditable control
(SOC 2 CC7.3 / ISO 27001 A.5.36) rather than an aspiration.

### 3.2 The abstraction cap — machine-enforced

`scripts/verify.py` runs a deny-pattern scan and hard-fails on:

- IP addresses and CIDR blocks
- Port numbers
- Hostnames, VM names, node names
- VPC and subnet names
- Kubernetes namespace and NetworkPolicy names
- Database schema, table and column names
- Object-storage bucket names
- Cryptographic key identifiers
- CDE segmentation detail

Permitted vocabulary: component **roles**, data **categories**, trust
**boundaries**, protocol classes (TLS/mTLS), residency (EU), and status
(`designed` / `deployed` / `planned`).

**Scan scope:** the entire repository, including this spec. No path exclusions.

**No suppression mechanism.** If the scan produces a false positive, the text is
rewritten — a bypass hatch in the control that enforces the abstraction cap
would defeat its purpose. Git commit digests and CVE identifiers are explicitly
out of scope; they are neither hostnames nor key identifiers.

Concrete consequence for §1.4: DPIA 003 currently names a fully-qualified
internal database table. That identifier **cannot** appear in `jolarca-docs`.
The DPIAs retain their detailed flows (the repository is private);
`jolarca-docs` publishes the category-level flow that each DPIA should cite.

The cap is recorded as **`DOC-0002`** so the constraint is a decision with a
rationale, not a lint rule nobody can explain.

### 3.3 Repository tree

```
jolarca-docs/
├── .github/
│   ├── CODEOWNERS                 # names jolarca-dev — NOT mission-org (ADR-0004 R4)
│   ├── workflows/lint.yml         # job MUST be named `lint` (required context in allow-list)
│   └── dependabot.yml
├── adr/
│   ├── README.md                  # GENERATED — registry of registries, qualified IDs
│   ├── namespace.md               # prefix allocation + collision rationale (OWNED)
│   ├── DOC-0001-owns-no-fact-another-repo-owns.md
│   ├── DOC-0002-public-abstraction-cap.md
│   ├── DOC-0003-single-runtime-dependency-pyyaml.md
│   └── TEMPLATE.md
├── system-description/            # the homeless SOC 2 artifact (OWNED)
│   ├── README.md                  # how to read; TSC description-criteria map
│   ├── 01-scope-and-boundaries.md # in/out of scope, Stripe carve-out, CUECs
│   ├── 02-infrastructure.md       # 90/10 at L1–L2, per-component status
│   ├── 03-software.md             # roles only, never versions+hosts
│   ├── 04-people.md               # solo-operator reality; D-04/D-10 stated plainly
│   ├── 05-procedures.md           # pointers to policies/runbooks, never copies
│   ├── 06-data.md                 # categories + residency; no table names
│   └── 07-criteria-map.md         # DC1.1–DC1.5 → evidence pointer
├── architecture/
│   ├── README.md
│   ├── context.mmd                # C4 L1 system context
│   ├── containers.mmd             # C4 L2 container
│   ├── data-flow-categories.mmd   # by data category, not by table
│   └── trust-boundaries.mmd       # boundaries only — zero ports/hosts
├── inventory/
│   └── fleet.md                   # GENERATED from the allow-list
├── references/
│   ├── manifest.csv               # pointer + sha256 per upstream doc
│   └── README.md                  # immutability: supersede, never edit
├── findings/
│   └── register.md                # cross-repo defects: owner / control / evidence
├── scripts/
│   ├── generate.py                # orchestrator
│   ├── scan_adrs.py
│   ├── build_inventory.py
│   ├── hash_manifest.py
│   └── verify.py                  # the CI gate
├── tests/
│   ├── fixtures/fake-fleet/       # synthetic siblings incl. a PLANTED violation
│   ├── test_scan_adrs.py
│   ├── test_deny_patterns.py
│   └── test_hash_manifest.py
├── docs/superpowers/specs/        # this document
├── .gitignore                     # the repo-defaults required patterns
├── .markdownlint.json             # convention confirmed in jolarca-compliance
├── CHANGELOG.md
├── CONTRIBUTING.md                # states the abstraction cap as an enforced rule
├── LICENSE                        # proprietary notice, mirrors jolarca-data
├── QODER.md                       # org convention (jolarca-data, jolarca-legal)
├── README.md
├── SECURITY.md
├── Makefile                       # generate / verify / test / check
└── pyproject.toml                 # pyyaml runtime; ruff+mypy+pytest dev
```

**Removed:** `main.py` (the `print_hi('PyCharm')` scaffold stub).
**Gitignored:** `.idea/`, `.venv/`.
**Added:** `git init` — the directory is not currently a git repository.

### 3.4 ADR namespace allocation

`adr/namespace.md` is OWNED and hand-maintained, because prefix allocation is a
governance decision rather than a derivable fact:

| Prefix | Repository |
|---|---|
| `APP-` | `jolarca` |
| `INFRA-` | `jolarca-infrastructure` |
| `COMP-` | `jolarca-compliance` |
| `CTL-` | `jolarca-control` |
| `SEC-` | `jolarca-security` |
| `PAY-` | `jolarca-payments` |
| `ID-` | `jolarca-identity` |
| `DATA-` | `jolarca-data` |
| `LEGAL-` | `jolarca-legal` |
| `DOC-` | `jolarca-docs` (this repo) |

Any ADR discovered in a repository with no allocated prefix is a **hard fail**.
Silent pass-through is how the current collision arose.

ADRs are **never renumbered and never moved**. Qualified IDs are applied
read-side in the index only. Renumbering would break live citations in
`network-policy.md` and would violate the org immutability rule
("never delete, only supersede").

---

## 4. Generation pipeline

`make generate` runs locally against sibling clones under `/opt/jolarca/repos/`.

1. **`scan_adrs.py`** — walk each sibling repository for ADR files, extract
   ID / title / status / date, apply the namespace prefix, emit `adr/README.md`.
2. **`build_inventory.py`** — parse `jolarca-control/repos/*.yml`, emit
   `inventory/fleet.md` with name, tier, criticality, launch_status, visibility
   and data_classification. The allow-list remains the system of record; this is
   a view.
3. **`hash_manifest.py`** — compute SHA-256 of every referenced upstream
   document, emit `references/manifest.csv`.
4. **`generate.py`** — orchestrates the three above in order and fails on the
   first error.

Output is **committed**. The PR diff is the audit trail: a reviewer sees exactly
which upstream facts moved, which is what an auditor wants and what a
CI-regenerated artifact can never show.

### 4.1 Dependency decision (`DOC-0003`)

Exactly **one runtime dependency: `pyyaml`, version-pinned.**

`build_inventory.py` must parse YAML and `scan_adrs.py` must parse Markdown
front-matter. The Python standard library has no YAML parser. Hand-rolling one
is more risk than the dependency. `pyyaml` is already the convention in
`jolarca-control` (`scripts/validate_repos.py`) and `jolarca-data`.

The stdlib-only rule belongs to `jolarca-compliance`'s **evidence** supply
chain. `jolarca-docs` is a tier-3 public documentation hub and holds no
evidence, so the rule does not transfer. Dev-only dependencies (`ruff`, `mypy`,
`pytest`) never ship. Dependabot and the `dependency-review` gate apply.

---

## 5. Verification

`make verify` runs the integrity gate fail-fast in this order:

1. **Governance files present and non-empty** — a *working* reimplementation,
   because the shared `ci-base.yml` check is inert (§7.1)
2. **markdownlint**
3. **Link check** — every relative link resolves; every cross-repo pointer has
   a manifest row
4. **Deny-pattern scan** — the abstraction cap (§3.2)
5. **ADR-ID uniqueness** — no duplicate qualified ID; no unassigned namespace
6. **Hash-manifest freshness** — recompute SHA-256 per upstream target, compare
7. **Inventory coherence** — `fleet.md` matches the allow-list, and the declared
   count matches the actual file count
8. **Mermaid structural check** — stdlib only: the first token is a known
   diagram type, brackets and quotes balance, and no node label contains a
   deny-listed token. Full parse validation is a non-goal (§9); it would require
   a Node toolchain this repository does not otherwise need.

Step 7 permanently machine-catches the §1.3 defect.

### 5.1 Make targets and the required CI context

| Target | Runs |
|---|---|
| `make generate` | The four generation scripts (§4) |
| `make verify` | The eight integrity steps above |
| `make test` | `pytest` |
| `make check` | `ruff` + `mypy` + `markdownlint` + `verify` + `test` |

The GitHub Actions job is named **exactly `lint`**, because
`repos/jolarca-docs.yml` declares `lint` as the required status-check context.
That job runs `make check`. The name mismatch between the job and the target is
deliberate and documented here so nobody "fixes" one to match the other and
silently unprotects the branch.

---

## 6. Failure modes

Design rule throughout: **a scanner that cannot read its input must fail, not
produce a smaller output.** A partial ADR index is indistinguishable from a
complete one for a system with fewer decisions — the `${#MISSUES[@]}` failure
mode in a new costume.

| Failure | Behaviour |
|---|---|
| Sibling clone missing | Skip **loudly**; `--strict` (CI) fails. Local non-strict runs succeed but must write a visible `<!-- PARTIAL: N siblings unavailable -->` banner into every generated artifact, so a partial index can never be committed unnoticed |
| Upstream document moved or deleted | Fail; print the pointer and the expected path |
| Unparseable ADR heading | Record in `findings/register.md` — never drop it |
| ADR collision without an allocated prefix | Hard fail |
| Deny-pattern hit | Hard fail with `file:line` and the matched token |
| `manifest.csv` empty | Hard fail — an index referencing nothing is broken, not empty |
| Allow-list count mismatch | Hard fail |

---

## 7. Findings register

`findings/register.md` records defects discovered outside this repository. Each
entry carries: evidence (file:line), affected control, owning repository, and
disposition. Per decision D4, none are fixed here except §7.4.

### 7.1 Governance-file gate cannot fail

`.github/.github/workflows/ci-base.yml:70` tests `${#MISSUES[@]}` — a typo for
`MISSING`. The array is unset, so the length is always 0 and the guard never
triggers. Every repository consuming `ci-base.yml` believes its governance files
are checked. **Control:** SOC 2 CC8.1, ISO 27001 A.8.25. **Owner:** `.github`.

### 7.2 Secret-scan gate is inert

`.github/.github/workflows/ci-base.yml:109-112` pins `gitleaks/gitleaks-action`
to `4f9a10a3b6e2a7a1b5d6b5a5e5e5e5e5e5e5e5e5`, which is not a resolvable digest
(the repeating `5e5e5e5e` tail is a placeholder pattern), and sets
`continue-on-error: true`. Meanwhile `repos/jolarca-docs.yml` declares
`required_gates.secret_scan: true`. **Control:** SOC 2 CC6.3, PCI-DSS Req 6.5.
**Owner:** `.github`.

### 7.3 Inventory counts disagree

Four documents state 5, 6, 14 and (implicitly) 15 repositories; the allow-list
contains 15 files and 10 repositories exist on disk. **Control:** ISO 27001
A.5.9, SOC 2 CC9.2. **Owner:** `.github`, `jolarca-control`.

### 7.4 This repo's own allow-list entry — FIXED in this change

`jolarca-control/repos/jolarca-docs.yml`:

- lines 48-50 declare `frameworks: [soc2, iso27001]`, omitting `pci_dss`, which
  `jolarca-control/docs/architecture.md:28` states applies to **all** repositories
- line 37 sets `require_code_owner_reviews: false` against a baseline of `true`;
  `repo-defaults.yml` whitelists only `.github` for exemption, so this is an
  unregistered deviation

Both are corrected here because this file is the config of record for the
repository being created. Provisioning from a knowingly wrong declaration would
be indefensible. Note that `jolarca-control` `apply.yml` is gated behind
`STATE_MIGRATION_COMPLETE`, so the correction takes effect only when the state
migration lands — the file is still the declaration of record meanwhile.

### 7.5 CODEOWNERS inert fleet-wide

Recorded for completeness as D-20 in `jolarca-control/docs/drift-findings.md`.
This repo's `CODEOWNERS` names `jolarca-dev` paths only (never mission-org
teams, per ADR-0004 R4) and is documented as **routing, not an enforced gate**.

---

## 8. Testing

`tests/` exists because an untested verifier is how §7.1 shipped.

- **`tests/fixtures/fake-fleet/`** — a synthetic sibling tree containing a known
  set of ADRs, a **planted namespace collision**, and a **planted forbidden port
  number**.
- **`test_scan_adrs.py`** — asserts the collision is detected and that every
  fixture ADR appears with the correct qualified ID.
- **`test_deny_patterns.py`** — asserts the planted violation fires and that a
  clean tree passes. Proves the abstraction cap is real.
- **`test_hash_manifest.py`** — asserts a mutated upstream file produces a
  mismatch and that a missing file fails rather than being skipped.

`make check` is defined in §5.1.

---

## 9. Non-goals

- **No static-site generator** (MkDocs / Docusaurus). GitHub renders Markdown
  and Mermaid natively; a site toolchain in a public tier-3 repository is
  unjustified supply-chain surface.
- **No Node toolchain.** Full Mermaid parse validation via `mermaid-cli` is
  excluded for the same reason; §5 step 8 uses a stdlib structural check.
- **No PDF export.** Auditors receive the SOC 2 report, not this repository.
- **No cross-repo writes** beyond `jolarca-control/repos/jolarca-docs.yml`.
- **No `git push`, no remote repository creation.** `apply.yml` refuses plans
  containing visibility changes, and `members_can_create_repositories` should be
  `false` (D-19). Local signed commits only; creating the remote repository
  remains a gated manual step owned by the operator.
- **No duplication of upstream prose.** Enforced by the manifest, not by
  convention.

---

## 10. Org conventions honoured

| Convention | Source | How honoured |
|---|---|---|
| Conventional Commits | `ci-base.yml` PR-title regex | Commit and PR titles |
| GPG-signed commits | `repo-defaults.yml` `commit_signing_policy` | `git commit -S` |
| Squash-only, linear history | `repos/jolarca-docs.yml` | Branch workflow |
| Plan-first change management | `.github/profile/README.md` | This spec precedes code |
| Required governance files | `ci-base.yml` | README, SECURITY, CONTRIBUTING, CHANGELOG, LICENSE |
| Required `.gitignore` patterns | `repo-defaults.yml` `data_handling` | All ten patterns present |
| Proprietary LICENSE for governance repos | `jolarca-data/LICENSE` | Mirrored |
| `QODER.md` agent guidelines | `jolarca-data`, `jolarca-legal` | Present, with the abstraction cap as a project-specific rule |
| Mermaid diagrams | `jolarca/README.md`, `jolarca-infrastructure/docs/architecture.md` | `.mmd` sources |
| `.markdownlint.json` | `jolarca-compliance/audits/` | Present |
| Actions pinned by SHA + version comment | `jolarca-control` convention | `lint.yml` |
| Required status-check context `lint` | `repos/jolarca-docs.yml` | Job named exactly `lint` |

---

## 11. Assumptions

1. Sibling clones remain available at `/opt/jolarca/repos/*` when
   `make generate` runs. Absent clones fail loudly rather than degrading output.
2. `jolarca-compliance` and `jolarca-data` are private. `jolarca-docs` never
   reproduces their contents — only pointers and hashes, which are safe to
   publish.
3. The GitHub repository itself is created by the operator through the gated
   path, not by this work.
4. `jolarca-control` remains the A.5.9 asset-inventory system of record. This
   repository publishes a generated view and asserts coherence, not ownership.
5. Findings D-01 through D-22 in `jolarca-control/docs/drift-findings.md` are
   the authoritative deviation register; this spec cites it and does not fork it.
