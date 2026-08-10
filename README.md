# cclimits

[![CI](https://github.com/urguide/cclimits/actions/workflows/ci.yml/badge.svg)](https://github.com/urguide/cclimits/actions/workflows/ci.yml)

Check quota/usage for AI coding CLI tools: Claude Code, OpenAI Codex, Google Gemini CLI, Google Antigravity, Z.AI, OpenRouter, Kimi K2 (Moonshot AI), Synthetic.new, and Grok (xAI). It also supports checking keys used by **Aider** and **Continue**.

## Features

- **Auto-discovers credentials** from standard locations
- **Auto-refreshes expired tokens** (Gemini OAuth, Antigravity OAuth)
- **Multiple output formats**: detailed, JSON, compact one-liner
- **Caching support** for fast statusline integration
- **Cross-platform**: macOS and Linux support

## Installation

**Requires**: Python 3.9+ installed on your system.

### Download (recommended)

```bash
curl -o ~/.local/bin/cclimits https://raw.githubusercontent.com/urguide/cclimits/main/lib/cclimits.py
chmod +x ~/.local/bin/cclimits
```

Optionally add the tmux status-line wrapper (see [tmux Integration](#tmux-integration)):

```bash
curl -o ~/.local/bin/cclimits-tmux https://raw.githubusercontent.com/urguide/cclimits/main/bin/cclimits-tmux
chmod +x ~/.local/bin/cclimits-tmux
```

Make sure `~/.local/bin` is on your `PATH`.

### Via Git

```bash
git clone https://github.com/urguide/cclimits.git
ln -s $(pwd)/cclimits/lib/cclimits.py ~/.local/bin/cclimits
ln -s $(pwd)/cclimits/bin/cclimits-tmux ~/.local/bin/cclimits-tmux
```

## Usage

```bash
cclimits              # Check all tools (detailed)
cclimits --claude     # Claude only
cclimits --codex      # Codex only
cclimits --gemini     # Gemini only
cclimits --zai        # Z.AI only
cclimits --openrouter # OpenRouter only
cclimits --kimi       # Kimi only
cclimits --antigravity # Google Antigravity only
cclimits --synthetic  # Synthetic.new only
cclimits --grok       # Grok (xAI) credits only
cclimits --json       # JSON output
cclimits --oneline           # Compact one-liner (5h window)
cclimits --oneline 7d        # Compact one-liner (7d window)
cclimits --oneline both      # Compact one-liner (5h/7d combined)
cclimits --oneline both --compact # Ceil values; reset shown compactly as (7d)/(16h)/(35m)
cclimits --oneline --noemoji # Color-coded text instead of emojis
cclimits --oneline --resets  # Append reset countdowns (alias: --timeremaining)

# Caching (for statusline integration)
cclimits --oneline --cached        # Use cache if fresh (<60s)
cclimits --oneline --cache-ttl 30  # Custom TTL in seconds
```

## Example Output

### Compact One-liner (--oneline)

```bash
# Single window (5h or 7d)
Claude: 4.0% (5h) ✅ | Codex: 0% (5h) ✅ | Z.AI: 1% (5h) ✅ | Gemini: ( 3-Flash 7% ✅ | Flash 1% ✅ | Pro 10% ✅ ) | OpenRouter: $47.91 ✅ | Kimi: $49.59 ✅ | Antigravity: 35% (8 models) ✅ | Grok: 55% (7d) ✅

# Both windows (--oneline both) - shows 5h/7d combined (Z.AI: 5h-tokens%/monthly-MCP-tools%)
Claude: 4.0%/10.0% ✅ | Codex: 0%/2% ✅ | Z.AI: 1%/16% ✅ | OpenRouter: $47.91 ✅

# Compact tmux-friendly output (--oneline both --compact --resets)
Claude:4%/10%(3h/4d)_Codex:2%(7d)_Grok:55%(7d)

# During Z.AI peak hours (06:00-10:00 UTC) a ⚡3x quota-rate marker appears
Z.AI: 1% (5h) ✅ ⚡3x

# No emoji mode (--noemoji) - colorizes percentages directly (green/yellow/red)
Claude: 4.0% (5h) | Codex: 0% (5h) | Z.AI: 1% (5h) | OpenRouter: $47.91 | Antigravity: 35% (8 models)

# With reset countdowns (--resets / --timeremaining) - ↻5h-reset/7d-reset; Antigravity shows its earliest model reset
Claude: 4.0%/10.0% ✅ ↻2h15m/3d17h | Codex: 0%/2% ✅ ↻1h05m/6d23h | Z.AI: 1% (5h) ✅ ↻3h02m | Antigravity: 3% (20 models) ✅ ↻10m

# --resets in both mode also shows Z.AI's monthly MCP-tools reset as the second countdown
Z.AI: 1%/16% ✅ ↻3h28m/5d10h
```

Status icons: ✅ ok · ⚠️ high usage · ❌ error · 🔑 no credentials found · ⏰ token expired. Cached results (`--cached`) are suffixed with their age, e.g. `(cached 42s)`.

Grok's credit period is supplied by xAI and may be weekly or monthly. Example:
`Grok: 55% (7d) ✅ ↻6d4h`.

### Detailed Output (default)

```
🔍 AI CLI Usage Checker
   2025-12-31 21:30:00

==================================================
  Claude Code
==================================================
  🔑 Auth: Bearer token
  ✅ Connected

  5-Hour Window:
    Used:      15.2%
    Remaining: 84.8%
    Resets in: 3h 24m

  7-Day Window:
    Used:      42.0%
    Remaining: 58.0%
    Resets in: 4d 12h

==================================================
  OpenAI Codex
==================================================
  🔑 Auth: OAuth (ChatGPT)
  ✅ Connected
  📊 Plan: pro

  5h Window:
    Used:      8%
    Remaining: 92%
    Resets in: 2h 15m

==================================================
  Gemini CLI
==================================================
  🔑 Auth: OAuth (Google Account)
  ✅ Connected
  📊 Tier: standard

  Quota by Tier:
    3-Flash: 7.0% used, 93.0% remaining
    Flash: 1.0% used, 99.0% remaining
    Pro: 10.0% used, 90.0% remaining

==================================================
  Z.AI (5h shared - GLM-4.x)
==================================================
  ✅ Connected
  📊 Plan: max

  Token Quota:
    Used:      1%
    Remaining: 99%
    Resets in: 4h 30m

  Quota Rate: 1x (promo) off-peak — peak in 1h 30m

  MCP Tools (monthly):
    Used:      650 / 4,000
    Remaining: 3,350
    Resets in: 6d 1h
      search-prime: 625
      web-reader: 13
      zread: 12

==================================================
  OpenRouter
==================================================
  ✅ Connected

  Balance:     $47.91
  Total Used:  $2.09

==================================================
  Kimi K2 (Moonshot AI)
==================================================
  ✅ Connected

  Balance (USD):
    Total:     $49.5889
    Cash:      $3.0000
    Voucher:   $46.5889

==================================================
  Google Antigravity
==================================================
  ✅ Connected
  📦 Project: my-cloud-code-project
  📊 Tier: free

  Model Quotas:
    Models:    8
    Tightest:  65% remaining
    Average:   83% remaining

    Model                             Remaining  Reset
    -------------------------------- ----------  ----------------
    claude-opus-4-5-thinking               65%  2026-05-30T18:00:00Z
    claude-sonnet-4-6                      71%  2026-05-30T18:00:00Z
    gemini-3-flash                         88%  2026-05-30T18:00:00Z

==================================================
  Synthetic.new
==================================================
  ✅ Connected

  Subscription:
    Used:      0 / 1,500 (0%)
    Remaining: 1,500
    Renews in: 4h 59m

  5-Hour Rolling:
    Used:      0 / 1,500 (0%)
    Remaining: 1,500
    Next tick: 0h 1m

  Weekly Credits:
    Remaining: $72.00 / $72.00 (100%)
    Next regen: 2h 53m (+$1.44)

==================================================
  Grok (xAI)
==================================================
  👤 Account: you@example.com
  ✅ Connected
  📊 Plan: GrokPro
  ⏱️  Token expires in: 5h 13m

  Credits (7d):
    Used:      55%
    Resets in: 6d 4h

  Product Usage:
    GrokBuild    53%
    GrokChat     2%
    GrokImagine  0%
  💳 Prepaid balance: $0.00
  🤖 CLI Access: yes
  📡 Source: grok-cli
  🔗 https://grok.com
```

## Status Icons

| Icon | Meaning |
|------|---------|
| ✅ | Under 70% - plenty of capacity |
| ⚠️ | 70-90% - moderate usage |
| 🔴 | 90-100% - near limit |
| ❌ | 100% or unavailable |

## tmux Integration

`bin/cclimits-tmux` shows your usage in the tmux status line — on the same row as
your window tabs.

tmux runs `#(...)` **synchronously**, so calling `cclimits` directly freezes the
whole status line while it waits on the API (~0.6s). The wrapper avoids this: it
prints the cached value instantly and refreshes in the background only when the
cache is stale.

Add to `~/.tmux.conf`:

```tmux
set -g status-right-length 150
set -g status-right '#[fg=cyan]#(~/.local/bin/cclimits-tmux)'
```

Reload with `tmux source-file ~/.tmux.conf`. Result in the top/bottom right:

```
Claude: 4.0% (5h) ✅ | Codex: 38% (7d) ✅
```

To keep an existing status-right (e.g. [gitmux](https://github.com/arl/gitmux)),
put both in one option — tmux only honours the last `status-right` it reads:

```tmux
set -g status-right '#[fg=cyan]#(~/.local/bin/cclimits-tmux)#[fg=default,bg=default]  #(gitmux "#{pane_current_path}")'
```

### Configuration

Override via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CCLIMITS_TMUX_TTL` | `180` | Seconds before the cache is refreshed |
| `CCLIMITS_TMUX_ARGS` | `--claude --codex --grok --oneline both --compact --resets` | Arguments passed to `cclimits` |
| `CCLIMITS_BIN` | auto-detected | Path to the `cclimits` executable |
| `GROK_BIN` | `grok` | Official Grok executable used for safe session refresh |

```tmux
# Refresh every 60s, show all providers with reset countdowns
set -g status-right '#(CCLIMITS_TMUX_TTL=60 CCLIMITS_TMUX_ARGS="--oneline both --resets" ~/.local/bin/cclimits-tmux)'
```

The wrapper keeps a stable last-known-good display cache, so the tmux segment
does not disappear while a new argument-specific cache is warming up. If Grok's
session is expired, the background refresh runs `grok models` once and then
retries cclimits. This delegates refresh-token rotation, locking and credential
write-back to the official CLI without sending a model prompt or consuming
Grok Build credits.

`cclimits` is resolved in this order: `$CCLIMITS_BIN`, then a sibling
`../lib/cclimits.py` (when run from a git checkout), then `PATH`.

### Notes

- `status-interval` (default 15s) controls how often tmux *reads* the cache;
  `CCLIMITS_TMUX_TTL` controls how often the API is actually queried. Leaving
  `status-interval` low is cheap — a cache hit is just a file read.
- The cache lives in `${TMPDIR:-/tmp}/cclimits-tmux.<uid>.<args-hash>.cache` and
  is keyed on the argument list, so different views never serve each other's
  output. Concurrent panes are de-duplicated with `flock`.
- On a cold cache the first render is empty; the value appears on the next
  status refresh.
- The wrapper calls `cclimits` without `--cached`, so no `(cached 42s)` suffix
  appears in the status line.

## Credential Locations

Credentials are auto-discovered from these locations:

| Tool | Location |
|------|----------|
| **Claude** | `~/.claude/.credentials.json` (Linux, auto-refreshes) or macOS Keychain |
| **Codex** | `~/.codex/auth.json` (auto-refreshes) |
| **Gemini** | `~/.gemini/oauth_creds.json` (auto-refreshes) |
| **Z.AI** | `$ZAI_KEY` or `$ZAI_API_KEY` environment variable |
| **OpenRouter** | `$OPENROUTER_API_KEY` environment variable |
| **Kimi** | `$MOONSHOT_API_KEY` environment variable |
| **Antigravity** | `~/.gemini/antigravity-cli/antigravity-oauth-token` (auto-refreshes); fallback `$ANTIGRAVITY_REFRESH_TOKEN` / `$ANTIGRAVITY_ACCESS_TOKEN` |
| **Synthetic.new** | `$SYNTHETIC_API_KEY` environment variable |
| **Grok** | `~/.grok/auth.json` (written by `grok login`); fallback `$GROK_ACCESS_TOKEN` session token |

## Setup (One-Time)

If credentials are missing, run the corresponding CLI tool to authenticate:

```bash
claude           # Login to Claude Code
codex login      # Login to OpenAI Codex
gemini           # Login to Gemini CLI
agy -p hello                 # Login to Google Antigravity (prompts for OAuth)
grok login       # Login to Grok CLI (xAI)
export ZAI_KEY=your-key           # Add to ~/.zshrc or ~/.bashrc
export OPENROUTER_API_KEY=your-key  # Add to ~/.zshrc or ~/.bashrc
export MOONSHOT_API_KEY=your-key    # Add to ~/.zshrc or ~/.bashrc
export SYNTHETIC_API_KEY=your-key   # Add to ~/.zshrc or ~/.bashrc
```

### Claude & Codex Token Refresh

Claude Code and codex only refresh their own OAuth tokens while they're
running. Claude's access token lasts ~8h, so leaving Claude Code closed
overnight used to leave every lookup returning `Token expired` — and in a tmux
status line that reads as a frozen percentage, because the wrapper keeps
serving the last good value rather than overwrite it with an error.

cclimits now redeems the stored refresh token itself when the access token has
expired (or when the API rejects it), and **writes the result back to the CLI's
own credential file** so Claude Code / codex pick it up too:

| | Claude | Codex |
|---|---|---|
| Token endpoint | `platform.claude.com/v1/oauth/token` | `auth.openai.com/oauth/token` |
| Access token life | ~8h | ~10d |
| Expiry read from | `expiresAt` in the credential file | `exp` claim of the access-token JWT |
| Refresh token rotates | **yes** | **yes** |

Both providers rotate the refresh token on every exchange, so writing the
response back isn't just a convenience — skip it and the CLI is left holding a
token the server has already retired.

Details:

- Writes are atomic and `0600`; every other field in the file is preserved.
- Refresh + write is serialized across cclimits processes with a `.lock` file
  next to the credential file, and cclimits re-reads the file under that lock
  so it skips the refresh if someone else got there first.
- For Claude it additionally takes **Claude Code's own** refresh lock — the
  proper-lockfile directory `~/.claude/.oauth_refresh.lock` — so the CLI and
  cclimits can't rotate the token out from under each other. If Claude Code
  holds it, cclimits stands down; if the lock is more than 60s stale (crashed
  CLI) it's stolen, matching proper-lockfile's own rule.
- codex exposes no equivalent lock file, so there the coordination is
  cclimits-vs-cclimits only.
- macOS Keychain-stored Claude credentials are **read-only** here — cclimits
  won't write to the Keychain, so expiry there still reports as expired.
- Opt out with `CCLIMITS_NO_TOKEN_REFRESH=1` to restore the previous
  read-only behaviour.

### Antigravity Authentication

The `agy` CLI writes its OAuth tokens to `~/.gemini/antigravity-cli/antigravity-oauth-token`; cclimits reads that file and auto-refreshes the access token via Google's OAuth endpoint. As a fallback (e.g. shared CI machines without the agy install), set `ANTIGRAVITY_REFRESH_TOKEN` (or `ANTIGRAVITY_ACCESS_TOKEN`) in your environment.

### Grok (xAI) Billing

Grok Build exposes its coding-credit usage through the same internal billing
endpoint used by the official `xai-org/grok-build` client:

```text
GET https://cli-chat-proxy.grok.com/v1/billing?format=credits
X-XAI-Token-Auth: xai-grok-cli
x-userid: <Grok user ID>
x-grok-client-version: <installed CLI version>
```

The response includes `creditUsagePercent`, a weekly or monthly current period,
per-product usage (`GrokBuild`, `GrokChat`, `GrokImagine`), prepaid balance and
on-demand billing fields. The endpoint was confirmed against the official
source in `crates/codegen/xai-grok-shell/src/extensions/billing.rs` and with a
live Grok CLI account.

cclimits reads `~/.grok/auth.json` read-only and never refreshes or writes it.
If the access token has expired, run `grok` to let the official CLI refresh it.

### Gemini Token Refresh

For Gemini token auto-refresh to work, cclimits needs OAuth client credentials. It will automatically extract these from your Gemini CLI installation. If that fails, set environment variables:

```bash
# Extract from Gemini CLI (run once to get values)
grep -E "CLIENT_(ID|SECRET)" ~/.npm/_npx/*/node_modules/@google/gemini-cli-core/dist/src/code_assist/oauth2.js

# Then add to ~/.zshrc or ~/.bashrc
export GEMINI_OAUTH_CLIENT_ID="..."
export GEMINI_OAUTH_CLIENT_SECRET="..."
```

## BYOK & Other Tools

`cclimits` can monitor usage for "Bring Your Own Key" (BYOK) tools by checking the underlying provider directly:

- **Aider / Continue**: If you use these with an API key (OpenAI, Anthropic, OpenRouter, Gemini), simply set the corresponding environment variable (e.g., `OPENROUTER_API_KEY`) and run `cclimits --openrouter` (or the relevant flag) to check your balance/quota.

**Note on Integrated Providers:**
- **GitHub Copilot**: Currently not supported as GitHub does not expose a public API for individual user quota/rate limits.
- **Cursor / Windsurf**: Not supported yet as they do not provide public quota APIs.

## Requirements

- Python 3.9+
- `requests` library (optional, falls back to urllib)
- `bash`, `flock` (only for `cclimits-tmux`)

## License

MIT
