# References — the upstream manifest

This directory holds the **pointer + SHA-256 manifest** that makes documentation
freshness an auditable control instead of an aspiration.

## What the manifest is

`jolarca-docs` copies **no upstream prose** (ADR
[DOC-0001](../adr/DOC-0001-owns-no-fact-another-repo-owns.md)). When a document
here relies on a fact owned elsewhere, it cites that document with a reference
marker:

```text
<!-- ref: jolarca-infrastructure/security/network-policy.md -->
```

`make generate` resolves every marker against the local sibling clones, computes
the SHA-256 of the target, and writes [manifest.csv](manifest.csv). The integrity
gate then:

1. re-scans the repository for markers and confirms **every pointer has a manifest
   row** (a citation with no hash is a broken reference, not a free pass); and
2. **recomputes** each target's hash and compares it to the recorded value — if an
   upstream document changed or moved, the gate fails and names the pointer.

A pointer is a repository-relative path from the fleet root (the directory that
contains all sibling clones). Pointers and hashes are safe to publish: they reveal
that a document exists and whether it changed, never its contents (ADR
[DOC-0002](../adr/DOC-0002-public-abstraction-cap.md)).

## manifest.csv schema

| Column | Meaning |
|---|---|
| `pointer` | Repository-relative path of the upstream document from the fleet root |
| `sha256` | SHA-256 hex digest of the document's bytes at generation time |

The file is **generated** — never hand-edit it. To change a citation, edit the
`<!-- ref: … -->` marker in the citing document and run `make generate`.

## Immutability: supersede, never edit

Manifest rows are **append-and-supersede**, never silently rewritten. When an
upstream document changes, regeneration produces a new hash; the pull-request diff
shows the old row replaced by the new one. That diff *is* the audit trail: a
reviewer sees exactly which upstream fact moved and when. Deleting a row to make a
hash mismatch disappear defeats the control and is treated as a defect.

## Empty is a failure

An **empty manifest is a hard failure.** A hub that references nothing is broken,
not minimal — it means the markers were lost or the sibling clones were unavailable
during generation. The gate fails rather than committing a plausible-looking empty
index (the same failure mode as a scanner that cannot read its input; see
[../CONTRIBUTING.md](../CONTRIBUTING.md)).
