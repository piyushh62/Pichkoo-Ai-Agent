"""Regression tests for _apply_profile_override PICHKOO_HOME guard (issue #22502).

When PICHKOO_HOME is set to the pichkoo root (e.g. systemd hardcodes
PICHKOO_HOME=/root/.pichkoo), _apply_profile_override must still read
active_profile and update PICHKOO_HOME to the profile directory.

When PICHKOO_HOME is already a profile directory (.../profiles/<name>),
_apply_profile_override must trust it and return without re-reading
active_profile (child-process inheritance contract).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path



def _run_apply_profile_override(
    tmp_path, monkeypatch, *, pichkoo_home: str | None, active_profile: str | None,
    argv: list[str] | None = None,
):
    """Run _apply_profile_override in isolation.

    Returns the value of os.environ["PICHKOO_HOME"] after the call,
    or None if unset.
    """
    pichkoo_root = tmp_path / ".pichkoo"
    pichkoo_root.mkdir(parents=True, exist_ok=True)

    if active_profile is not None:
        (pichkoo_root / "active_profile").write_text(active_profile)

    if active_profile and active_profile != "default":
        (pichkoo_root / "profiles" / active_profile).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    if pichkoo_home is not None:
        monkeypatch.setenv("PICHKOO_HOME", pichkoo_home)
    else:
        monkeypatch.delenv("PICHKOO_HOME", raising=False)

    monkeypatch.setattr(sys, "argv", argv or ["pichkoo", "gateway", "start"])

    from pichkoo_cli.main import _apply_profile_override
    _apply_profile_override()

    return os.environ.get("PICHKOO_HOME")


class TestApplyProfileOverridePichkooHomeGuard:
    """Regression guard for issue #22502.

    Verifies that PICHKOO_HOME pointing to the pichkoo root does NOT suppress
    the active_profile check, while PICHKOO_HOME already pointing to a
    profile directory IS trusted as-is.
    """

    def test_pichkoo_home_at_root_with_active_profile_is_redirected(
        self, tmp_path, monkeypatch
    ):
        """PICHKOO_HOME=/root/.pichkoo + active_profile=coder must redirect
        PICHKOO_HOME to .../profiles/coder.

        Bug scenario from #22502: systemd sets PICHKOO_HOME to the pichkoo root
        and the user switches to a profile via `pichkoo profile use`.
        Before the fix, the guard returned early and active_profile was ignored.
        """
        pichkoo_root = tmp_path / ".pichkoo"
        pichkoo_root.mkdir(parents=True, exist_ok=True)

        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            pichkoo_home=str(pichkoo_root),
            active_profile="coder",
        )

        assert result is not None, "PICHKOO_HOME must be set after profile redirect"
        assert "profiles" in result, (
            f"Expected PICHKOO_HOME to point into profiles/ dir, got: {result!r}"
        )
        assert result.endswith("coder"), (
            f"Expected PICHKOO_HOME to end with 'coder', got: {result!r}"
        )

    def test_pichkoo_home_already_profile_dir_is_trusted(self, tmp_path, monkeypatch):
        """PICHKOO_HOME=.../profiles/coder must not be overridden even when
        active_profile says something different.

        Preserves the child-process inheritance contract: a subprocess spawned
        with PICHKOO_HOME already set to a specific profile must stay in that
        profile.
        """
        pichkoo_root = tmp_path / ".pichkoo"
        profile_dir = pichkoo_root / "profiles" / "coder"
        profile_dir.mkdir(parents=True, exist_ok=True)

        (pichkoo_root / "active_profile").write_text("other")

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.setenv("PICHKOO_HOME", str(profile_dir))
        monkeypatch.setattr(sys, "argv", ["pichkoo", "gateway", "start"])

        from pichkoo_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("PICHKOO_HOME") == str(profile_dir), (
            "PICHKOO_HOME must remain unchanged when already pointing to a profile dir"
        )

    def test_pichkoo_home_unset_reads_active_profile(self, tmp_path, monkeypatch):
        """Classic case: PICHKOO_HOME unset + active_profile=coder must set
        PICHKOO_HOME to the profile directory (existing behaviour must not regress).
        """
        result = _run_apply_profile_override(
            tmp_path,
            monkeypatch,
            pichkoo_home=None,
            active_profile="coder",
        )

        assert result is not None
        assert "coder" in result

    def test_pichkoo_home_unset_default_profile_no_redirect(self, tmp_path, monkeypatch):
        """active_profile=default must not redirect PICHKOO_HOME."""
        pichkoo_root = tmp_path / ".pichkoo"
        pichkoo_root.mkdir(parents=True, exist_ok=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        monkeypatch.delenv("PICHKOO_HOME", raising=False)
        monkeypatch.setattr(sys, "argv", ["pichkoo", "gateway", "start"])
        (pichkoo_root / "active_profile").write_text("default")

        from pichkoo_cli.main import _apply_profile_override
        _apply_profile_override()

        assert os.environ.get("PICHKOO_HOME") is None
