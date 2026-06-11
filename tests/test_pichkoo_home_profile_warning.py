"""Tests for get_pichkoo_home() profile-mode fallback warning.

Regression test for https://github.com/piyushh62/Pichkoo-AI-Agent/issues/18594.

When PICHKOO_HOME is unset but an active_profile file indicates a non-default
profile is active, get_pichkoo_home() should:
  1. STILL return ~/.pichkoo (raising would brick 30+ module-level callers)
  2. Emit a loud one-shot warning to stderr so operators can diagnose
     cross-profile data contamination after the fact.

The warning goes to stderr directly (not through logging) because this
function is called at module-import time from 30+ sites, often before the
logging subsystem has been configured.
"""

from pathlib import Path

import pytest


@pytest.fixture
def fresh_constants(monkeypatch, tmp_path):
    """Import pichkoo_constants fresh and reset the one-shot warn flag."""
    import importlib
    import pichkoo_constants
    importlib.reload(pichkoo_constants)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("PICHKOO_HOME", raising=False)
    return pichkoo_constants


class TestGetPichkooHomeProfileWarning:
    def test_classic_mode_no_active_profile_no_warning(
        self, fresh_constants, tmp_path, capsys
    ):
        """Classic mode: no active_profile file → silent, returns ~/.pichkoo."""
        result = fresh_constants.get_pichkoo_home()
        assert result == tmp_path / ".pichkoo"
        assert "PICHKOO_HOME fallback" not in capsys.readouterr().err

    def test_default_active_profile_no_warning(
        self, fresh_constants, tmp_path, capsys
    ):
        """active_profile=default → still no warning, returns ~/.pichkoo."""
        pichkoo_dir = tmp_path / ".pichkoo"
        pichkoo_dir.mkdir()
        (pichkoo_dir / "active_profile").write_text("default\n")
        result = fresh_constants.get_pichkoo_home()
        assert result == tmp_path / ".pichkoo"
        assert "PICHKOO_HOME fallback" not in capsys.readouterr().err

    def test_named_profile_unset_home_warns_once(
        self, fresh_constants, tmp_path, capsys
    ):
        """active_profile=coder + PICHKOO_HOME unset → warn loudly, still return fallback."""
        pichkoo_dir = tmp_path / ".pichkoo"
        pichkoo_dir.mkdir()
        (pichkoo_dir / "active_profile").write_text("coder\n")

        result = fresh_constants.get_pichkoo_home()

        # 1. Still returns the fallback — no import-time crash
        assert result == tmp_path / ".pichkoo"
        # 2. Stderr got the warning exactly once
        err = capsys.readouterr().err
        assert err.count("PICHKOO_HOME fallback") == 1
        assert "'coder'" in err
        assert "#18594" in err

        # 3. One-shot: second and third calls don't re-warn
        fresh_constants.get_pichkoo_home()
        fresh_constants.get_pichkoo_home()
        err2 = capsys.readouterr().err
        assert "PICHKOO_HOME fallback" not in err2

    def test_pichkoo_home_set_suppresses_warning(
        self, fresh_constants, tmp_path, capsys, monkeypatch
    ):
        """Even if active_profile is 'coder', setting PICHKOO_HOME suppresses warning."""
        profile_dir = tmp_path / ".pichkoo" / "profiles" / "coder"
        profile_dir.mkdir(parents=True)
        (tmp_path / ".pichkoo" / "active_profile").write_text("coder\n")
        monkeypatch.setenv("PICHKOO_HOME", str(profile_dir))

        result = fresh_constants.get_pichkoo_home()

        assert result == profile_dir
        assert "PICHKOO_HOME fallback" not in capsys.readouterr().err

    def test_unreadable_active_profile_no_crash(
        self, fresh_constants, tmp_path, capsys
    ):
        """active_profile that can't be decoded → fall through silently."""
        pichkoo_dir = tmp_path / ".pichkoo"
        pichkoo_dir.mkdir()
        # Write bytes that aren't valid utf-8
        (pichkoo_dir / "active_profile").write_bytes(b"\xff\xfe\x00\x00")

        result = fresh_constants.get_pichkoo_home()

        assert result == tmp_path / ".pichkoo"
        # Shouldn't crash; shouldn't warn either (can't tell what profile was intended)
        assert "PICHKOO_HOME fallback" not in capsys.readouterr().err

    def test_empty_active_profile_no_warning(
        self, fresh_constants, tmp_path, capsys
    ):
        """Empty active_profile file → treated as default, no warning."""
        pichkoo_dir = tmp_path / ".pichkoo"
        pichkoo_dir.mkdir()
        (pichkoo_dir / "active_profile").write_text("")

        result = fresh_constants.get_pichkoo_home()

        assert result == tmp_path / ".pichkoo"
        assert "PICHKOO_HOME fallback" not in capsys.readouterr().err
