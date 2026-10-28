# Progress

## Working Features

- **Claude Code**: OAuth token from keychain (macOS) or `~/.claude/.credentials.json` (Linux); expired tokens are refreshed against `platform.claude.com/v1/oauth/token` and written back to the credential file — including the rotated refresh token — while holding the CLI's own `.oauth_refresh.lock` (file-backed creds only; Keychain stays read-only)
- **OpenAI Codex**: JWT from `~/.codex/auth.json`; expiry read from the token's own `exp` claim, refreshed against `auth.openai.com/oauth/token` with the rotated refresh token + `id_token` + `last_refresh` written back
- **Gemini CLI** (legacy — CLI retired 2026-06-18): OAuth from `~/.gemini/oauth_creds.json`; token refresh needs an installed Gemini CLI package or env overrides, otherwise reports ⏰ expired
- **Google Antigravity**: OAuth tokens read from `~/.gemini/antigravity-cli/antigravity-oauth-token` (written by `agy` CLI) or `ANTIGRAVITY_REFRESH_TOKEN`; per-model quota tracking, live-verified against real install
- **Z.AI**: API token from environment variable (`$ZAI_KEY` or `$ZAI_API_KEY`), 5h shared token quota + monthly MCP-tools quota (`mcp_quota` with per-tool breakdown & reset) + client-side peak/off-peak quota-rate indicator (`quota_rate`, ⚡3x oneline marker during peak)
- **OpenRouter**: API token from environment variable (`$OPENROUTER_API_KEY`)
- **Kimi K2 (Moonshot)**: API token from env var (`$MOONSHOT_API_KEY`), prepaid balance tracking
- **Synthetic.new**: API token from env var (`$SYNTHETIC_API_KEY`), reports subscription/rolling-5h/weekly-credits buckets via `GET /v2/quotas` (free probe)
- **Grok (xAI)**: OAuth token read (read-only, never written) from the scope-keyed `~/.grok/auth.json` or `$GROK_ACCESS_TOKEN`; coding-credit usage from the official CLI's internal `/v1/billing?format=credits` endpoint, including total/per-product percentage, weekly/monthly reset, prepaid and on-demand fields. When xAI omits `creditUsagePercent` immediately after a recognized period reset, it is normalized to 0% so Grok stays visible. Live-verified: 55% total = GrokBuild 53% + GrokChat 2%
- **Display modes**: JSON, detailed, compact one-liner, noemoji color mode, `--icons` Nerd Font glyph labels (opt-in; one cell per provider, ~12 columns saved on a three-provider tmux line; every codepoint verified present in the installed font by parsing its `cmap`/`post` tables), and `--compact` icon-free statusline mode; compact percentages use ceiling (never under-report), reset countdowns collapse to one ceiled unit (`7d` / `16h` / `35m`; dual windows `4h/2d`), cache/stale age tags are hidden, providers use a tight underscore separator (`Claude:99%_Grok:55%`), and failures render as plain `no key` / `expired` / `ERR`
- **Time windows**: 5h and 7d for Claude/Codex (Codex windows classified by `limit_window_seconds`, not slot position — weekly-only accounts return one window in the primary slot; renderer degrades gracefully to whichever window exists), 5h for Z.AI (shared across GLM models; `both` mode shows tokens%/monthly-MCP%, `--resets` there shows both countdowns), 5h rolling + weekly credits for Synthetic.new
- **Reset countdowns** (`--resets`, alias `--timeremaining`): appends `↻` countdowns per provider in oneline; Grok uses its server-supplied weekly/monthly credit-period end, Antigravity shows its earliest model reset, and prepaid-balance providers have nothing to reset. In a *dual*-window suffix an absent/`N/A` countdown renders as `-` (`↻-/21h50m`, compact `(-/22h)`) so slot position still identifies the window — Claude reports `resets_at: null` whenever its 5h window is idle, which previously collapsed to a bare `(14h)` that could have been either window. When *every* slot is absent the suffix is dropped entirely, which is what keeps single-window providers (Grok, Antigravity, Gemini, weekly-only Codex) printing their `(7d)`/`(5h)` label instead of a useless `(-)`
- **tmux wrapper resilience**: `--watch` is a long-running `#()` producer that emits a complete cached line every 2s, avoiding tmux 3.7b's blank interval when short-lived jobs restart; on a cold cache it emits `CCLIMITS_TMUX_PLACEHOLDER` (default `cclimits...`) so tmux never falls back to its own `<'...' not ready>` marker, and on a *failed* self-invocation it emits the distinct `CCLIMITS_TMUX_ERROR` (default `cclimits!`) — a live loop survives its own file being truncated/overwritten, so sharing one marker made a corrupt install look like a slow first lookup. Argument-keyed caches also feed a stable last-known-good display cache. *Transient* failures (`ERR`/`expired`) preserve only that provider's prior good field while healthy providers from the same refresh still advance; `no key` is accepted normally and replaces an old reading when a provider is deliberately left unconfigured. Expired Grok triggers one background `grok models`, delegating rotation/write-back to the official CLI without inference — that trigger matches both the `Grok` label and its `--icons` glyph, since matching only the word would silently disable auto-refresh for icon users. `CCLIMITS_TMUX_SEP` restyles `--compact`'s `_` provider separator (e.g. a coloured `┃` matching the pane dividers); the substitution runs on *serve*, never on write, so the cache keeps the raw form used for provider-level last-good merging and a separator change lands on the next redraw instead of after the TTL
- **Caching** (`--cached`, `~/.cache/cclimits/usage.json`): version 2 per-provider timestamps; locked read/merge/write with unique 0600 temp files. Partial runs and preserved readings never renew old timestamps; TTL/stale limits are checked per provider. Legacy global-timestamp caches are invalidated on upgrade.
- **Review hardening (2026-09-05)**: OAuth locks fail closed, file staging precedes rotation, and Claude refresh is bound to the selected credential source. Codex preserves HTTP outage status; Gemini quota failures remain errors even when authentication succeeds. Gemini write warnings go to stderr. tmux provider merging handles compact, normal, icon, and ANSI output without splitting Gemini's tiers or rejecting numeric 100% readings.
- **BYOK Support**: Explicit documentation for monitoring Aider/Continue via their underlying provider keys.

## Current Status

- ✅ All core AI tool integrations functional (Claude, Codex, Gemini, Antigravity, Z.AI, OpenRouter, Kimi, Synthetic.new, Grok)
- ✅ Full local pytest suite passes with isolated cache and module-level patch targets
- ✅ Cross-platform credential detection (macOS/Linux)
- ✅ npm package published as `cclimits`
- ✅ Gemini models grouped by quota tier (3-Flash, Flash, Pro)
- ✅ Antigravity detailed output lists all full model names, remaining quotas and resets; `--oneline both` shows fixed Claude / Argon family slots with paired resets and a Google G icon. General Gemini usage is omitted from this view. Direct requests use the CLI client identity to include Argon. Single-window mode retains the all-model summary.
- ✅ Research on additional providers completed (`research/ai-coding-providers.md`)
- ✅ Providers fetched concurrently; cache hits skip all network/credential calls; transient failures fall back to <24h-old cached data with stale marker (v1.3.0)
- ✅ Data-driven `PROVIDERS` registry — adding a provider is one registry entry + one fetch function
- ✅ Claude/Codex OAuth tokens self-heal: expiry- and 401-driven refresh, atomic 0600 write-back to the vendor's own credential file, `flock`-serialized plus interop with Claude Code's own `.oauth_refresh.lock`, opt-out via `CCLIMITS_NO_TOKEN_REFRESH=1`
- ✅ CI (GitHub Actions matrix) + automated npm publish on `v*` tags via Trusted Publishing (OIDC); test counts are reported by pytest collection

## Known Issues

- System-wide `/usr/local/bin` copies still need reinstall after the 2026-09-05 changes; sudo requires a password in this environment.
- Codex/vendor concurrent refresh remains uncoordinated (no vendor lock). Staging cannot guarantee write-back against a later disk failure or crash; recovery data may need manual intervention.
- macOS/Windows live behavior was not exercised locally. Without `fcntl`, refresh and cache writes are disabled.

## What's Left to Build

### High Priority
- **Replit Integration**: Endpoint identified (`usage-credits-balance`), awaiting implementation.

### Medium Priority
- ~~CI/CD pipeline for npm publishing~~ ✅ Done (2026-07-12) — GitHub Actions workflows added for CI (pytest on push/PR) and automated publish (tag push → npm with provenance)
- Gemini legacy OAuth auto-refresh or graceful retirement (CLI retired 2026-06-18; expired token renders ⏰)

### Low Priority
- TypeScript rewrite to remove Python dependency
- **Cursor / Windsurf / Copilot**: Feasibility is currently low due to lack of public APIs.
- Configurable output formats
- Historical usage tracking
