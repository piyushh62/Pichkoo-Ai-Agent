"""Resolve PICHKOO_HOME for standalone skill scripts.

Skill scripts may run outside the Pichkoo process (e.g. system Python,
nix env, CI) where ``pichkoo_constants`` is not importable.  This module
provides the same ``get_pichkoo_home()`` and ``display_pichkoo_home()``
contracts as ``pichkoo_constants`` without requiring it on ``sys.path``.

When ``pichkoo_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``pichkoo_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``PICHKOO_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from pichkoo_constants import display_pichkoo_home as display_pichkoo_home
    from pichkoo_constants import get_pichkoo_home as get_pichkoo_home
except (ModuleNotFoundError, ImportError):

    def get_pichkoo_home() -> Path:
        """Return the Pichkoo home directory (default: ~/.pichkoo).

        Mirrors ``pichkoo_constants.get_pichkoo_home()``."""
        val = os.environ.get("PICHKOO_HOME", "").strip()
        return Path(val) if val else Path.home() / ".pichkoo"

    def display_pichkoo_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``pichkoo_constants.display_pichkoo_home()``."""
        home = get_pichkoo_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
