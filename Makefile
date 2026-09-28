# ──────────────────────────────────────────────────────────────────────────────
# jolarca-docs — Makefile
# ──────────────────────────────────────────────────────────────────────────────
# Targets: generate / verify / verify-strict / test / check
# See the design spec §5 (fail-fast verify order) and ADR DOC-0002 (abstraction
# cap). The GitHub Actions job named `lint` runs `make check` — the job/target
# name mismatch is deliberate (spec §5.1): `lint` is the required status-check
# context declared in jolarca-control/repos/jolarca-docs.yml.
# ──────────────────────────────────────────────────────────────────────────────

# Prefer the project venv; fall back to PATH (CI installs into the runner).
ifeq ($(wildcard .venv/bin/python),)
PYTHON  := python3
TOOLBIN :=
else
PYTHON  := .venv/bin/python
TOOLBIN := .venv/bin/
endif
RUFF := $(TOOLBIN)ruff
MYPY := $(TOOLBIN)mypy

.DEFAULT_GOAL := help
.PHONY: help generate verify verify-strict test ruff mypy markdownlint check clean

help:
	@echo "jolarca-docs — targets"
	@echo "  generate       regenerate adr/README.md, inventory/fleet.md, references/manifest.csv"
	@echo "                 from local sibling clones under ../ (never in CI)"
	@echo "  verify         integrity gate; sibling-dependent steps run when the fleet is"
	@echo "                 present, otherwise they SKIP LOUDLY (CI-safe)"
	@echo "  verify-strict  integrity gate that FAILS if any expected upstream input is"
	@echo "                 missing — run this locally before committing"
	@echo "  test           pytest"
	@echo "  check          ruff + mypy + markdownlint + verify + test  (the CI 'lint' job)"

generate:
	$(PYTHON) scripts/generate.py

verify:
	$(PYTHON) scripts/verify.py

verify-strict:
	$(PYTHON) scripts/verify.py --strict

test:
	$(PYTHON) -m pytest

ruff:
	$(RUFF) check .

mypy:
	$(MYPY)

markdownlint:
	@if command -v markdownlint-cli2 >/dev/null 2>&1; then \
		markdownlint-cli2; \
	elif command -v npx >/dev/null 2>&1; then \
		npx --yes markdownlint-cli2; \
	else \
		echo "SKIP (loud): markdownlint unavailable — no markdownlint-cli2 and no npx."; \
		echo "              Enforced in CI where Node is present. Not a silent pass."; \
	fi

check: ruff mypy markdownlint verify test
	@echo "make check: PASS"

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
