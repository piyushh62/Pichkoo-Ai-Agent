---
sidebar_position: 11
title: "ACP Editor Integration"
description: "Use Pichkoo AI Agent inside ACP-compatible editors such as VS Code, Zed, and JetBrains"
---

# ACP Editor Integration

Pichkoo AI Agent can run as an ACP server, letting ACP-compatible editors talk to Pichkoo over stdio and render:

- chat messages
- tool activity
- file diffs
- terminal commands
- approval prompts
- streamed thinking / response chunks

ACP is a good fit when you want Pichkoo to behave like an editor-native coding agent instead of a standalone CLI or messaging bot.

## What Pichkoo exposes in ACP mode

Pichkoo runs with a curated `pichkoo-acp` toolset designed for editor workflows. It includes:

- file tools: `read_file`, `write_file`, `patch`, `search_files`
- terminal tools: `terminal`, `process`
- web/browser tools
- memory, todo, session search
- skills
- execute_code and delegate_task
- vision

It intentionally excludes things that do not fit typical editor UX, such as messaging delivery and cronjob management.

## Installation

Install Pichkoo normally, then add the ACP extra:

```bash
pip install -e '.[acp]'
```

This installs the `agent-client-protocol` dependency and enables:

- `pichkoo acp`
- `pichkoo-acp`
- `python -m acp_adapter`

For Zed registry installs, Zed launches Pichkoo through the official ACP Registry entry. That entry uses a `uvx` distribution that runs:

```bash
uvx --from 'pichkoo-agent[acp]==<version>' pichkoo-acp
```

Make sure `uv` is available on `PATH` before using the registry install path.

## Launching the ACP server

Any of the following starts Pichkoo in ACP mode:

```bash
pichkoo acp
```

```bash
pichkoo-acp
```

```bash
python -m acp_adapter
```

Pichkoo logs to stderr so stdout remains reserved for ACP JSON-RPC traffic.

For non-interactive checks:

```bash
pichkoo acp --version
pichkoo acp --check
```

### Browser tools (optional)

Browser tools (`browser_navigate`, `browser_click`, etc.) depend on the
`agent-browser` npm package and Chromium, which aren't part of the Python
wheel. Install them with:

```bash
pichkoo acp --setup-browser           # interactive (prompts before ~400 MB download)
pichkoo acp --setup-browser --yes     # accept the download non-interactively
```

This is the standalone command. The Zed registry's terminal-auth flow (`pichkoo acp --setup`) also offers the browser bootstrap as a follow-up question after model selection, so most users never need to run `--setup-browser` directly.

What it does:

- Installs Node.js 22 LTS into `~/.pichkoo/node/` if missing
- `npm install -g agent-browser @askjo/camofox-browser` into that prefix (no sudo needed — `npm`'s `--prefix` points at the user-writable Pichkoo-managed Node)
- Installs Playwright Chromium, or uses a detected system Chrome/Chromium when available

The bootstrap is idempotent — re-running it is fast and skips work that's already done.

## Editor setup

### VS Code

Install the [ACP Client](https://marketplace.visualstudio.com/items?itemName=formulahendry.acp-client) extension.

To connect:

1. Open the ACP Client panel from the Activity Bar.
2. Select **Pichkoo AI Agent** from the built-in agent list.
3. Connect and start chatting.

If you want to define Pichkoo manually, add it through VS Code settings under `acp.agents`:

```json
{
  "acp.agents": {
    "Pichkoo AI Agent": {
      "command": "pichkoo",
      "args": ["acp"]
    }
  }
}
```

### Zed

Zed v0.221.x and newer installs external agents through the official ACP Registry.

1. Open the Agent Panel.
2. Click **Add Agent**, or run the `zed: acp registry` command.
3. Search for **Pichkoo AI Agent**.
4. Install it and start a new Pichkoo external-agent thread.

Prerequisites:

- Configure Pichkoo provider credentials first with `pichkoo model`, or set them in `~/.pichkoo/.env` / `~/.pichkoo/config.yaml`.
- Install `uv` so the registry launcher can run `uvx --from 'pichkoo-agent[acp]==<version>' pichkoo-acp`.

For local development before the registry entry is available, use a custom agent server in Zed settings:

```json
{
  "agent_servers": {
    "pichkoo-agent": {
      "type": "custom",
      "command": "pichkoo",
      "args": ["acp"]
    }
  }
}
```

### JetBrains

Use an ACP-compatible plugin and point it at:

```text
/path/to/pichkoo-agent/acp_registry
```

## Registry manifest

The source copy of Pichkoo' official ACP Registry metadata lives at:

```text
acp_registry/agent.json
acp_registry/icon.svg
```

The upstream registry PR copies those files into the top-level `pichkoo-agent/` directory in `agentclientprotocol/registry`.

The registry entry uses a `uvx` distribution that points directly at the `pichkoo-agent` PyPI release:

```text
uvx --from 'pichkoo-agent[acp]==<version>' pichkoo-acp
```

The registry CI verifies that the pinned version exists on PyPI, so the manifest's `version` and uvx `package` pin must always match `pyproject.toml`. `scripts/release.py` keeps them in lockstep automatically.

## Configuration and credentials

ACP mode uses the same Pichkoo configuration as the CLI:

- `~/.pichkoo/.env`
- `~/.pichkoo/config.yaml`
- `~/.pichkoo/skills/`
- `~/.pichkoo/state.db`

Provider resolution uses Pichkoo' normal runtime resolver, so ACP inherits the currently configured provider and credentials. Pichkoo also advertises a terminal auth method (`--setup`) for first-run registry clients; this opens Pichkoo' interactive model/provider setup.

## Session behavior

ACP sessions are tracked by the ACP adapter's in-memory session manager while the server is running.

Each session stores:

- session ID
- working directory
- selected model
- current conversation history
- cancel event

The underlying `AIAgent` still uses Pichkoo' normal persistence/logging paths, but ACP `list/load/resume/fork` are scoped to the currently running ACP server process.

## Working directory behavior

ACP sessions bind the editor's cwd to the Pichkoo task ID so file and terminal tools run relative to the editor workspace, not the server process cwd.

## Approvals

Dangerous terminal commands can be routed back to the editor as approval prompts. ACP approval options are simpler than the CLI flow:

- allow once
- allow always
- deny

On timeout or error, the approval bridge denies the request.

### Session-scoped edit auto-approval

ACP exposes a third tier between *allow once* and *allow always*: **Allow for session**. Picking it from the editor's permission prompt records the approval inside the current ACP session only — every subsequent matching command in that session goes through without prompting, but a new ACP session (or restarting the editor) resets the slate and re-prompts the first time.

| Option | Editor label | Scope | Persisted across restarts |
|---|---|---|---|
| `allow_once` | Allow once | This one tool call | No |
| `allow_session` | Allow for session | All matching calls in this ACP session | No — cleared when the session ends |
| `allow_always` | Allow always | All future sessions | Yes (written to the Pichkoo permanent allowlist) |
| `deny` | Deny | This one tool call | No |

`allow_session` is the right default for an editor workflow where you trust an agent for the duration of a task but don't want to grant a long-lived allowlist entry. The safety trade-off is straightforward: the broader the scope, the less the editor will interrupt you, and the more damage a misbehaving agent (or prompt injection) can do before you notice. Start with `allow_once` for unfamiliar commands; promote to `allow_session` once you've seen the agent run the same pattern correctly a few times; reserve `allow_always` for truly idempotent commands you trust forever (e.g. `git status`).

The ACP bridge maps these options onto Pichkoo' internal approval semantics — `allow_always` writes a permanent allowlist entry the same way the CLI does, while `allow_session` only affects the in-process approval cache for the current ACP session.

## Troubleshooting

### ACP agent does not appear in the editor

Check:

- In Zed, open the ACP Registry with `zed: acp registry` and search for **Pichkoo AI Agent**.
- For manual/local development, verify the custom `agent_servers` command points to `pichkoo acp`.
- Pichkoo is installed and on your PATH.
- The ACP extra is installed (`pip install -e '.[acp]'`).
- `uv` is installed if launching from the official Zed registry entry.

### ACP starts but immediately errors

Try these checks:

```bash
pichkoo acp --version
pichkoo acp --check
pichkoo doctor
pichkoo status
```

### Missing credentials

ACP mode uses Pichkoo' existing provider setup. Configure credentials with:

```bash
pichkoo model
```

or by editing `~/.pichkoo/.env`. Registry clients can also trigger Pichkoo' terminal auth flow, which runs the same interactive provider/model setup.

### Zed registry launcher cannot find uv

Install `uv` from the official uv installation docs, then retry the Pichkoo AI Agent thread from Zed.

## See also

- [ACP Internals](../../developer-guide/acp-internals.md)
- [Provider Runtime Resolution](../../developer-guide/provider-runtime.md)
- [Tools Runtime](../../developer-guide/tools-runtime.md)
