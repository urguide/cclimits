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
curl -fLo ~/.local/bin/cclimits https://raw.githubusercontent.com/urguide/cclimits/main/lib/cclimits.py
chmod +x ~/.local/bin/cclimits
```

Optionally add the tmux status-line wrapper (see [tmux Integration](#tmux-integration)):

```bash
curl -fLo ~/.local/bin/cclimits-tmux https://raw.githubusercontent.com/urguide/cclimits/main/bin/cclimits-tmux
chmod +x ~/.local/bin/cclimits-tmux
```

Make sure `~/.local/bin` is on your `PATH`.

**Do not drop the `-f`.** Without it `curl` writes the body of an HTTP error
response to the output file *and still exits 0*, so a CDN hiccup silently
leaves a `404: Not Found` string or a Varnish `503` HTML page where the script
should be. `chmod +x` then happily marks it executable and the failure only
surfaces later as a frozen tmux status line. `-f` suppresses the body and
returns exit 22 instead; `-L` follows redirects.

`-f` cannot detect a *truncated* download (that is a successful 200), so it is
worth confirming both files actually parse:

```bash
python3 -c 'import ast,sys; ast.parse(open(sys.argv[1]).read())' ~/.local/bin/cclimits \
  && bash -n ~/.local/bin/cclimits-tmux && echo "install OK"
```

### System-wide (useful for tmux)

`~/.local/bin` is usually added to `PATH` by an interactive shell rc file,
which the tmux **server** never reads — see [tmux Integration](#tmux-integration).
Installing from a git checkout to a directory that is already on the default
`PATH` avoids that class of problem:

```bash
sudo install -m 755 lib/cclimits.py /usr/local/bin/cclimits
sudo install -m 755 bin/cclimits-tmux /usr/local/bin/cclimits-tmux
```

These are copies, so re-run both commands after every update or the installed
version will silently drift from the source.

### Via Git

```bash
git clone https://github.com/urguide/cclimits.git
ln -s $(pwd)/cclimits/lib/cclimits.py ~/.local/bin/cclimits
ln -s $(pwd)/cclimits/bin/cclimits-tmux ~/.local/bin/cclimits-tmux
```

Symlinks (rather than copies) keep the installed command in step with the
checkout, and let the wrapper find `cclimits` via its sibling `../lib`
directory without any `PATH` or `CCLIMITS_BIN` configuration.

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
cclimits --oneline --icons   # Provider names as Nerd Font glyphs (needs a patched font)

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

# Shortest form (--oneline both --compact --resets --icons) - 12 columns narrower
:4%/10%(3h/4d)_:2%(7d)_:55%(7d)

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

### Provider glyphs (`--icons`)

`--icons` replaces each provider name with a one-column [Nerd Font](https://www.nerdfonts.com/)
glyph, which is worth roughly 12 columns on a three-provider tmux line. It is
opt-in: without a patched font every glyph renders as a replacement box, which
is strictly worse than the word it replaced.

| Provider | Glyph | Codepoint | Nerd Font name |
|----------|-------|-----------|----------------|
| Claude | `` | `U+EC82` | `cod-claude` |
| Codex | `` | `U+EC81` | `cod-openai` |
| Grok | `` | `U+EB72` | `cod-twitter` |
| Gemini | `󰫢` | `U+F0AE2` | `md-star_four_points` |
| Antigravity | `󱓞` | `U+F14DE` | `md-rocket_launch` |
| Z.AI | `󰰷` | `U+F0C37` | `md-alpha_z_circle` |
| Kimi | `󰰊` | `U+F0C0A` | `md-alpha_k_circle` |
| OpenRouter | `󱇢` | `U+F11E2` | `md-router` |
| Synthetic | `󰂓` | `U+F0093` | `md-flask` |

Verify your font before enabling it — all three should be glyphs, not boxes:

```bash
printf 'claude=\uec82 openai=\uec81 twitter=\ueb72\n'
```

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

Calling `cclimits` directly from `#(...)` makes the status wait on the API. The
wrapper instead runs as a long-lived status producer: it emits the cached value
every two seconds and refreshes API data in the background only when stale.
Keeping the job alive avoids tmux 3.7b briefly rendering an empty result while
repeatedly restarting a short-lived status command.

Add to `~/.tmux.conf`:

```tmux
set -g status-right-length 150
set -g status-right '#[fg=cyan]#(~/.local/bin/cclimits-tmux --watch)'
```

Reload with `tmux source-file ~/.tmux.conf`. Result in the top/bottom right:

```
Claude: 4.0% (5h) ✅ | Codex: 38% (7d) ✅
```

To keep an existing status-right (e.g. [gitmux](https://github.com/arl/gitmux)),
put both in one option — tmux only honours the last `status-right` it reads:

```tmux
set -g status-right '#[fg=cyan]#(~/.local/bin/cclimits-tmux --watch)#[fg=default,bg=default]  #(gitmux "#{pane_current_path}")'
```

### Configuration

Override via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `CCLIMITS_TMUX_TTL` | `180` | Seconds before the cache is refreshed |
| `CCLIMITS_TMUX_WATCH_INTERVAL` | `2` | Seconds between complete status-line emissions |
| `CCLIMITS_TMUX_PLACEHOLDER` | `cclimits...` | Line shown until the first lookup lands (set empty to disable) |
| `CCLIMITS_TMUX_ERROR` | `cclimits!` | Line shown when the wrapper itself cannot run (corrupt/truncated install) |
| `CCLIMITS_TMUX_SEP` | unset (`_`) | Display string replacing `--compact`'s `_` between providers |
| `CCLIMITS_TMUX_ARGS` | `--claude --codex --grok --oneline both --compact --resets` | Arguments passed to `cclimits` |
| `CCLIMITS_BIN` | auto-detected | Path to the `cclimits` executable |
| `GROK_BIN` | `grok` | Official Grok executable used for safe session refresh |

```tmux
# Refresh every 60s, show all providers with reset countdowns
set -g status-right '#(CCLIMITS_TMUX_TTL=60 CCLIMITS_TMUX_ARGS="--oneline both --resets" ~/.local/bin/cclimits-tmux --watch)'
```

To reclaim the columns spent on provider names, add `--icons` (see
[Provider glyphs](#provider-glyphs---icons)); `set-environment -g` keeps the
`status-right` line itself readable:

```tmux
set-environment -g CCLIMITS_TMUX_ARGS "--claude --codex --grok --oneline both --compact --resets --icons"
set -g status-right '#[fg=cyan]#(~/.local/bin/cclimits-tmux --watch)'
```

#### Separator styling (`CCLIMITS_TMUX_SEP`)

`--compact` separates providers with `_` to save columns. `CCLIMITS_TMUX_SEP`
replaces that single character with any display string, including tmux `#[...]`
style sequences — useful for matching the bar your pane and window dividers
already use:

```tmux
set-environment -g CCLIMITS_TMUX_SEP "#[fg=#ff8800]┃#[fg=cyan]"
```

```
Claude:41%/31%(4h/5d)┃Codex:27%(4d)┃Grok:68%(2d)
```

The trailing `#[fg=cyan]` is not optional: a tmux style persists to the end of
the line, so without it every provider after the first separator is drawn in the
bar's colour too.

Substitution happens when the cached line is *served*, not when it is written,
so the cache always holds the raw `_` form. A separator change therefore takes
effect on the next redraw rather than after the refresh TTL, and the
transient-failure detection below — which matches the raw `_`-delimited text —
keeps working whatever separator you choose. The separator is inserted
literally, so `#`, `|`, `&` and `\` need no escaping.

`status-right-length` truncates on *rendered* width, so the `#[...]` sequences
cost nothing; a single-cell bar like `┃` is exactly as wide as the `_` it
replaced. Only a multi-character separator (e.g. `" ┃ "`) needs extra length.

The wrapper keeps a stable last-known-good display cache, so the tmux segment
does not disappear while a new argument-specific cache is warming up. If Grok's
session is expired, the background refresh runs `grok models` once and then
retries cclimits. This delegates refresh-token rotation, locking and credential
write-back to the official CLI without sending a model prompt or consuming
Grok Build credits. That trigger recognises both the `Grok` label and its
`--icons` glyph, so enabling icons does not disable auto-refresh.

A refresh that reports a *transient* failure — an API error (`ERR`) or an
expired token (`expired`) — is discarded so it cannot overwrite a good reading.
A missing credential (`no key`) is not transient: retrying cannot change it, so
it is accepted normally. Otherwise a single unconfigured provider would reject
every refresh forever and freeze the percentages of the providers that do work.

`cclimits` is resolved in this order: `$CCLIMITS_BIN`, then a sibling
`../lib/cclimits.py` (when run from a git checkout), then `PATH`.

Note that the tmux **server** environment is not your interactive shell's. If
`cclimits` lives somewhere your login shell adds to `PATH` (e.g.
`~/.local/bin`), the server may not see it and the status line will stay empty
or show tmux's `<'...' not ready>` marker. Set `CCLIMITS_BIN` to an absolute
path to make resolution independent of the server's `PATH`:

```tmux
set-environment -g CCLIMITS_BIN "/usr/local/bin/cclimits"
```

Two failure modes are worth calling out together, because they combine into a
silent one:

- **Copy vs symlink.** If `cclimits-tmux` was *copied* to its install
  directory, `readlink -f` resolves to itself, so the sibling `../lib`
  probe looks for a nonexistent `<prefix>/../lib/cclimits.py` and fails.
  A symlink back to the checkout makes that step succeed on its own.
- **This failure is invisible.** The wrapper deliberately preserves the last
  known-good line, so a lookup that fails every time does not blank the status
  bar — it just freezes it at a stale reading. If the numbers look stuck, run
  the wrapper by hand and check that the cache body is actually being written:

  ```bash
  ls -l ${TMPDIR:-/tmp}/cclimits-tmux.$(id -u).*
  ```

  A `.lease`/`.lock` pair with no accompanying `.cache` file means every
  refresh is failing.

### Notes

- `status-interval` (default 15s) controls how often tmux *reads* the cache;
  `CCLIMITS_TMUX_TTL` controls how often the API is actually queried. Leaving
  `status-interval` low is cheap — a cache hit is just a file read.
- The cache lives in `${TMPDIR:-/tmp}/cclimits-tmux.<uid>.<args-hash>.cache` and
  is keyed on the argument list, so different views never serve each other's
  output. Concurrent panes are de-duplicated with `flock`.
- On a cold cache `--watch` emits `CCLIMITS_TMUX_PLACEHOLDER` until the first
  lookup lands. Emitting nothing would make tmux render its own
  `<'...' not ready>` marker instead.
- If the wrapper cannot re-invoke itself it emits `CCLIMITS_TMUX_ERROR`
  (`cclimits!`) rather than the placeholder. A running `--watch` loop is already
  parsed into memory, so it keeps ticking even after the file underneath it is
  truncated or overwritten — sharing one marker with the cold-cache case would
  make a broken install look like a slow first lookup. Seeing `cclimits!`
  means the installed script itself is bad: check `file $(command -v cclimits-tmux)`
  and `bash -n $(command -v cclimits-tmux)`.
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
