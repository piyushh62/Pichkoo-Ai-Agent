# Langfuse Observability Plugin

This plugin ships bundled with Pichkoo but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

Pick one:

```bash
# Interactive: walks you through credentials + SDK install + enable
pichkoo tools  # → Langfuse Observability

# Manual
pip install langfuse
pichkoo plugins enable observability/langfuse
```

## Required credentials

Set these in `~/.pichkoo/.env` (or via `pichkoo tools`):

```bash
PICHKOO_LANGFUSE_PUBLIC_KEY=pk-lf-...
PICHKOO_LANGFUSE_SECRET_KEY=sk-lf-...
PICHKOO_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
pichkoo plugins list                 # observability/langfuse should show "enabled"
pichkoo chat -q "hello"              # then check Langfuse for a "Pichkoo turn" trace
```

## Optional tuning

```bash
PICHKOO_LANGFUSE_ENV=production       # environment tag
PICHKOO_LANGFUSE_RELEASE=v1.0.0       # release tag
PICHKOO_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
PICHKOO_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
PICHKOO_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
pichkoo plugins disable observability/langfuse
```
