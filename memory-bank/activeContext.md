# Active Context

## Current Focus

- Maintenance + provider coverage; `package.json` is at 1.5.0 (activeContext previously lagged at 1.3.0)
- Researching additional AI coding providers (Cursor, Copilot, Replit, etc.)

## Recent Changes (Last 7 Days)

- **2026-08-10**: **Grok (xAI) coding-credit usage added.** Official `xai-org/grok-build` source revealed the internal `/v1/billing?format=credits` endpoint and its required session/user/version headers; live account probe returned total + per-product percentages and a weekly reset. Grok now appears in oneline and detailed/JSON output. `~/.grok/auth.json` remains read-only. Compact/tmux includes Grok, uses ceiling values, removes pictorial icons and spacing, hides cache/stale age, and collapses reset countdowns to `(7d)` / `(16h)` / `(35m)`. Also closed a test-isolation gap where a logged-in developer's real Grok account changed the provider set during tests. 255 → 287 tests
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
