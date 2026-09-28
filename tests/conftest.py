"""Pytest configuration: make the generator/verifier modules importable.

The scripts live in ``scripts/`` and are run as top-level modules (there is no
package ``__init__.py``), so the tests add that directory to ``sys.path`` once.
``mypy_path = "scripts"`` in pyproject.toml mirrors this for type checking.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "fake-fleet"
FAKE_FLEET = FIXTURES / "fleet"
FAKE_REPO = FIXTURES / "repo"
