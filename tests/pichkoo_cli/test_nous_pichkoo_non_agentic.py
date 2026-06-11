"""Tests for the Nous-Pichkoo-3/4 non-agentic warning detector.

Prior to this check, the warning fired on any model whose name contained
``"pichkoo"`` anywhere (case-insensitive). That false-positived on unrelated
local Modelfiles such as ``pichkoo-brain:qwen3-14b-ctx16k`` — a tool-capable
Qwen3 wrapper that happens to live under the "pichkoo" tag namespace.

``is_nous_pichkoo_non_agentic`` should only match the actual Nous Research
Pichkoo-3 / Pichkoo-4 chat family.
"""

from __future__ import annotations

import pytest

from pichkoo_cli.model_switch import (
    _PICHKOO_MODEL_WARNING,
    _check_pichkoo_model_warning,
    is_nous_pichkoo_non_agentic,
)


@pytest.mark.parametrize(
    "model_name",
    [
        "NousResearch/Pichkoo-3-Llama-3.1-70B",
        "NousResearch/Pichkoo-3-Llama-3.1-405B",
        "pichkoo-3",
        "Pichkoo-3",
        "pichkoo-4",
        "pichkoo-4-405b",
        "pichkoo_4_70b",
        "openrouter/pichkoo3:70b",
        "openrouter/nousresearch/pichkoo-4-405b",
        "NousResearch/Pichkoo3",
        "pichkoo-3.1",
    ],
)
def test_matches_real_nous_pichkoo_chat_models(model_name: str) -> None:
    assert is_nous_pichkoo_non_agentic(model_name), (
        f"expected {model_name!r} to be flagged as Nous Pichkoo 3/4"
    )
    assert _check_pichkoo_model_warning(model_name) == _PICHKOO_MODEL_WARNING


@pytest.mark.parametrize(
    "model_name",
    [
        # Kyle's local Modelfile — qwen3:14b under a custom tag
        "pichkoo-brain:qwen3-14b-ctx16k",
        "pichkoo-brain:qwen3-14b-ctx32k",
        "pichkoo-honcho:qwen3-8b-ctx8k",
        # Plain unrelated models
        "qwen3:14b",
        "qwen3-coder:30b",
        "qwen2.5:14b",
        "claude-opus-4-6",
        "anthropic/claude-sonnet-4.5",
        "gpt-5",
        "openai/gpt-4o",
        "google/gemini-2.5-flash",
        "deepseek-chat",
        # Non-chat Pichkoo models we don't warn about
        "pichkoo-llm-2",
        "pichkoo2-pro",
        "nous-pichkoo-2-mistral",
        # Edge cases
        "",
        "pichkoo",  # bare "pichkoo" isn't the 3/4 family
        "pichkoo-brain",
        "brain-pichkoo-3-impostor",  # "3" not preceded by /: boundary
    ],
)
def test_does_not_match_unrelated_models(model_name: str) -> None:
    assert not is_nous_pichkoo_non_agentic(model_name), (
        f"expected {model_name!r} NOT to be flagged as Nous Pichkoo 3/4"
    )
    assert _check_pichkoo_model_warning(model_name) == ""


def test_none_like_inputs_are_safe() -> None:
    assert is_nous_pichkoo_non_agentic("") is False
    # Defensive: the helper shouldn't crash on None-ish falsy input either.
    assert _check_pichkoo_model_warning("") == ""
