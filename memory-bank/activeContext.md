# Active Context

## Current Focus

- Maintenance + provider coverage; `package.json` is at 1.5.0 (activeContext previously lagged at 1.3.0)
- Researching additional AI coding providers (Cursor, Copilot, Replit, etc.)

## Recent Changes (Last 7 Days)

- **2026-08-10**: **tmux wrapper hardened after a live `<'...' not ready>` report.** The empty output was environmental (tmux server PATH lacked `~/.local/bin`, and the installed wrapper was a copy so the sibling `../lib` probe missed too) — resolved out-of-band, resolution chain untouched. Two real code bugs were found underneath: `no key` was classified as a transient failure, so an unconfigured Grok would have rejected every refresh and frozen Claude/Codex percentages forever; and `--watch` emitted nothing on a cold cache, which is exactly what makes tmux print its own marker. Failure regex narrowed to `ERR`/`expired`; watch mode now emits `CCLIMITS_TMUX_PLACEHOLDER`. 291 → 294 tests

- **2026-08-10**: **Grok (xAI) coding-credit usage added.** Official source revealed the internal billing endpoint; live probing confirmed total/per-product percentages and weekly reset. cclimits keeps `~/.grok/auth.json` read-only; the tmux wrapper delegates expired-session refresh to official `grok models`. Compact output uses ceiling values and collapsed reset units. tmux 3.7b flicker was traced to repeated restart of a short-lived `#()` job; `cclimits-tmux --watch` now stays alive and emits a complete line every 2s. 255 → 291 tests
- **2026-08-06**: Claude & Codex OAuth token auto-refresh with write-back to the vendor credential files, interop-locked against Claude Code's own `.oauth_refresh.lock`

- **2026-07-12**: **v1.3.0 released** — first release through the new tag-push pipeline (npm Trusted Publishing/OIDC, provenance attested). Five changes in one release, see `deltas.md`: cache-hit bypass bug fix (openrouter/kimi/antigravity/synthetic no longer fetch live on cache hits), concurrent provider fetching (ThreadPoolExecutor; wall time ≈ slowest provider), GitHub Actions CI (3.9/3.11/3.13 × requests/urllib matrix) + automated publish, data-driven `PROVIDERS` registry refactor (byte-identical output, −93 lines), stale-cache fallback (transient failures serve <24h-old good entries with stale marker). Suite: 155 → 205 tests
- Publishing gotchas hit and fixed: `setup-node` `registry-url` breaks the OIDC exchange (E404); newer npm strips `./`-prefixed bin paths at publish (would have broken `npx cclimits`) — `npm pkg fix` applied
- **2026-07-02**: v1.2.15–1.2.18 released — see `deltas.md`: cache merge, atomic cache writes, provider filters on cache hits, cached-output age labels, Z.AI data cleanup, distinct oneline icons (🔑/⏰/❌)

## Blocked/Waiting

- Replit integration requires a Replit account/token for implementation/testing.

## Next Steps

1. Implement Replit support (High feasibility endpoint identified)
2. Monitor GitHub Copilot/Cursor for future public API availability
3. ~~Add CI/CD for automated npm publishing~~ ✅ Done (2026-07-12) — `.github/workflows/ci.yml` runs tests on push/PR; `.github/workflows/publish.yml` publishes on `v*` tags via npm Trusted Publishing (OIDC, no token)
4. Possible future: Gemini legacy OAuth auto-refresh (CLI retired 2026-06-18; expired token now visible as ⏰ in oneline)

## Key Patterns

- **BYOK Tools**: Aider and Continue use standard API keys; `cclimits` supports them indirectly by monitoring the underlying provider (OpenAI/Anthropic/etc).
- **Integrated Tools**: Cursor, Windsurf, Copilot, JetBrains have "hidden" or internal-only usage APIs, making CLI integration difficult without reverse engineering.
- **Replit**: Uses a specific "usage credits" model with a likely accessible endpoint.
