# QODER.md

Behavioral guidelines to reduce common LLM coding mistakes when using Qoder in
PyCharm. Merge with project-specific instructions as needed.

**Tradeoff:** these guidelines bias toward caution over speed. For trivial tasks,
use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" that wasn't requested.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Every changed line should trace directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified. Evidence before assertions.**

- "Add validation" → "write tests for invalid inputs, then make them pass".
- Never claim success without running the command and showing the output.
- For multi-step tasks, state a brief plan with a verify check per step.

---

## Project-Specific Guidelines — jolarca-docs

This repository is a **public** compliance-documentation hub. It is scanned by
`scripts/verify.py` on every change. The full rules live in `CONTRIBUTING.md`;
these constrain AI-assisted changes and are non-negotiable.

### The abstraction cap (ADR DOC-0002) — the headline rule

- This repo is `visibility: public`. It must never contain a network address,
  CIDR block, port number, hostname, VM/node name, VPC/subnet name, Kubernetes
  namespace or NetworkPolicy name, database schema/table/column name,
  object-storage bucket name, cryptographic key identifier, or CDE segmentation
  detail.
- Describe **roles, data categories, trust boundaries, protocol classes
  (TLS/mTLS), residency, and status** — never concrete identifiers.
- There is **no suppression mechanism and no path exclusion** in the deny-scan.
  If the scan fires on your text, **rewrite the text**. Never propose weakening
  a pattern, adding an allow-list entry, or bypassing the gate to make a commit
  pass.
- Upstream detail stays upstream. Cite it with a `<!-- ref: repo/path -->`
  pointer; `references/manifest.csv` carries the SHA-256. Copy no prose.

### Owns no fact another repository owns (ADR DOC-0001)

- Before adding content, ask which repository owns that fact. If another repo
  owns it, **link it, don't restate it**. Duplication is how the fleet's
  five-copies-of-one-fact drift problem started.
- Generated files (`adr/README.md`, `inventory/fleet.md`,
  `references/manifest.csv`) are produced by `make generate` — **never
  hand-edit them**. Edit the generator or the upstream source.

### Dual-state honesty

- Every component, control, and flow carries an explicit `designed` /
  `deployed` / `planned` status. Never write the system description in the
  present tense; the system is largely unprovisioned and overstating it to an
  auditor is a defect, not polish.

### Failure behavior

- A generator or scanner that cannot read its input must **fail**, not emit a
  smaller result. Never add a bare `except: pass`, a `|| true`, or a silent
  fallback that could turn a broken index into a plausible-looking partial one.

### Governance gates

- `make check` (ruff + mypy + markdownlint + verify + test) must pass before a
  change is proposed as complete. `make verify-strict` is the authoritative
  local gate (it requires the sibling fleet to be present).
- Exactly one runtime dependency (`pyyaml`). Do not add another without a new
  ADR superseding DOC-0003.
- Commits are GPG-signed and follow Conventional Commits. Never suggest
  `--no-verify` or an unsigned commit.
- Do not create the remote repository or push; that is a gated operator step.
