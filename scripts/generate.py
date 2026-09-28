#!/usr/bin/env python3
"""Generation orchestrator.

Runs the three generators in order and fails on the first error (design spec §4):

1. ``scan_adrs``       -> adr/README.md
2. ``build_inventory`` -> inventory/fleet.md
3. ``hash_manifest``   -> references/manifest.csv

Generation is **local**: it reads the sibling clones under the fleet root. CI never
runs this (a public repo must not be given credentials to read private upstream
repos — design spec §2, D2); CI runs ``scripts/verify.py`` against the committed
output instead. The generated artifacts are committed so the pull-request diff is
the audit trail.

Pass ``--strict`` to fail when any sibling clone or upstream target is missing;
without it, generators stamp a visible PARTIAL banner instead.
"""

from __future__ import annotations

import sys
from collections.abc import Callable

import build_inventory
import hash_manifest
import scan_adrs

STEPS: list[tuple[str, Callable[[list[str]], int]]] = [
    ("scan_adrs", scan_adrs.main),
    ("build_inventory", build_inventory.main),
    ("hash_manifest", hash_manifest.main),
]


def main(argv: list[str]) -> int:
    for name, step in STEPS:
        print(f"== generate: {name} ==", flush=True)
        rc = step(argv)
        if rc != 0:
            print(f"generate: {name} failed (rc={rc}); aborting", file=sys.stderr)
            return rc
    print("generate: OK — all artifacts regenerated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
