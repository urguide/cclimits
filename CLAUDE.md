# CLAUDE.md

Project instructions for Claude Code when working in this repository.

## Quick Orientation

**cclimits** is a CLI tool that checks quota/usage for AI coding assistants (Claude Code, OpenAI Codex, Google Gemini CLI, Google Antigravity, Z.AI, Kimi/Moonshot, OpenRouter, Synthetic.new, Grok/xAI). Distributed via npm, runs Python under the hood.

**Repository**: https://github.com/cruzanstx/cclimits
**npm**: https://www.npmjs.com/package/cclimits

## Project Structure

```
cclimits/
├── bin/
│   └── cclimits.js      # Node wrapper (spawns Python)
├── lib/
│   └── cclimits.py      # Main script (~1000 lines)
├── memory-bank/         # AI context files (read these first)
├── package.json         # npm config
├── README.md
├── LICENSE              # MIT
└── CLAUDE.md            # This file
```

## Memory Bank

Read `memory-bank/` files at the start of each task:
1. `deltas.md` - Most recent changes
2. `activeContext.md` - Current focus
3. `progress.md` - What works, known issues
4. `systemPatterns.md` - Architecture patterns
5. `techContext.md` - Tech stack, commands

## Key Patterns

### Dual Distribution
- **npm package**: Users run `npx cclimits`
- **Node wrapper** (`bin/cclimits.js`): Spawns Python
- **Python script** (`lib/cclimits.py`): Does actual work

### Credential Discovery
Each tool has a `get_X_credentials()` function that checks:
1. Platform-specific storage (macOS Keychain)
2. Config files (~/.claude, ~/.codex, ~/.gemini)
3. Environment variables (fallback)

### HTTP Client
Zero-dependency fallback pattern:
```python
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
```

### No Hardcoded Secrets
Gemini OAuth credentials are extracted from the user's Gemini CLI installation, not hardcoded (GitHub push protection). Antigravity uses public installed-app OAuth credentials; never hardcode user refresh/access tokens.

## Commands

```bash
# Development
python3 lib/cclimits.py --oneline
python3 lib/cclimits.py --json

# Test via npx (uses published version)
npx cclimits

# Test local changes via npx
npm link
npx cclimits
npm unlink

# Publish new version
npm version patch  # bumps to x.x.X
npm version minor  # bumps to x.X.0
npm publish
git push --tags
```

## Publishing Workflow

There are two paths:

### Automated (CI publish via tag push)

1. Make changes to `lib/cclimits.py`
2. Update `memory-bank/deltas.md` and `progress.md`
3. Bump version: `npm version patch` (creates the tag)
4. Push the tag: `git push --tags`
5. The `publish.yml` workflow runs the test suite, verifies the tag matches `package.json`, then runs `npm publish --access public` via npm Trusted Publishing (OIDC — no token secret; provenance is automatic)

**Prerequisite**: A Trusted Publisher must be configured on npmjs.com for the `cclimits` package (package Settings → Trusted Publisher → GitHub Actions: owner `cruzanstx`, repo `cclimits`, workflow `publish.yml`). No npm token or GitHub secret is needed.

### Manual (fallback)

1. `npm version patch`
2. `npm publish`
3. `git push --tags`

**Note**: npm publish requires 2FA or automation token with bypass.

## API Endpoints

| Tool | Endpoint | Auth Header |
|------|----------|-------------|
| Claude | `api.anthropic.com/api/oauth/usage` | `Bearer {token}` |
| Codex | `chatgpt.com/backend-api/wham/usage` | `Bearer {oauth}` + `chatgpt-account-id` |
| Gemini | `cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota` | `Bearer {oauth}` |
| Antigravity | `cloudcode-pa.googleapis.com/v1internal:loadCodeAssist` | `Bearer {oauth}` |
| Antigravity | `cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels` | `Bearer {oauth}` |
| Z.AI | `api.z.ai/api/monitor/usage/quota/limit` | `Authorization: {api_key}` |
| OpenRouter | `openrouter.ai/api/v1/credits` | `Authorization: Bearer {api_key}` |
| Kimi (Moonshot) | `api.moonshot.ai/v1/users/me/balance` | `Authorization: Bearer {api_key}` |
| Synthetic.new | `api.synthetic.new/v2/quotas` | `Authorization: Bearer {api_key}` |
| Grok (xAI) | `cli-chat-proxy.grok.com/v1/billing?format=credits` | `Bearer {oauth}` + `X-XAI-Token-Auth: xai-grok-cli` + user/version headers |

### Token Refresh Endpoints

| Tool | Endpoint | Notes |
|------|----------|-------|
| Claude | `platform.claude.com/v1/oauth/token` | JSON body + `anthropic-beta: oauth-2025-04-20`; refresh token **is** rotated (`refreshTokenExpiresAt` stays put, so it's not a rotation signal) |
| Codex | `auth.openai.com/oauth/token` | JSON body; refresh token **is** rotated |
| Gemini | `oauth2.googleapis.com/token` | form body, needs client id/secret from the Gemini CLI install |

Both Claude and Codex rotate the refresh token, so write-back is mandatory —
dropping the response strands the vendor CLI on a retired token.

Refreshed tokens are written back to the vendor's own credential file via
`write_json_secure()` (atomic, 0600) under `credential_lock()`. For Claude,
`claude_refresh_lock()` additionally takes the CLI's own proper-lockfile
directory `<config-dir>/.oauth_refresh.lock` (60s stale steal) so the two
can't rotate concurrently. Tests must never touch the real files — the autouse
`isolated_credentials` fixture in `tests/conftest.py` redirects
`CLAUDE_CRED_PATHS` / `CODEX_AUTH_PATHS`.

## Testing Checklist

Before publishing:
- [ ] `python3 lib/cclimits.py` - All tools checked
- [ ] `python3 lib/cclimits.py --oneline` - Compact output works
- [ ] `python3 lib/cclimits.py --json` - Valid JSON output
- [ ] `python3 lib/cclimits.py --claude` - Single tool filter works
- [ ] Test on machine without `requests` installed (urllib fallback)

## Known Limitations

1. **Python required**: npm package needs Python 3.9+ on user's system
2. **Gemini OAuth (legacy)**: Gemini CLI was retired 2026-06-18; legacy token refresh needs an installed Gemini CLI package or env overrides
3. **Antigravity credentials**: Read from `~/.gemini/antigravity-cli/antigravity-oauth-token` (written by `agy` CLI). Falls back to `ANTIGRAVITY_REFRESH_TOKEN` / `ANTIGRAVITY_ACCESS_TOKEN` if absent
4. **Z.AI**: 5h shared quota across GLM-4.7, GLM-4.6, GLM-4.5V, GLM-4.5, GLM-4.5-Air, and Visual Analysis
5. **Codex API key mode**: No quota info (only OAuth has it)
6. **Synthetic.new**: Reports three buckets — subscription (period requests), rolling 5h tokens, and weekly $ credits. Calls to `/quotas` don't count against any bucket
7. **Windows**: Untested, may have path issues; `credential_lock()` degrades to no locking without `fcntl`
8. **macOS Claude credentials**: Keychain-stored tokens are read-only — cclimits won't write a refreshed token back into the Keychain, so expiry there still reports as expired
9. **Codex has no shared lock**: `credential_lock()` only serializes cclimits against itself, and codex exposes no lock file (just an in-process mutex), so a simultaneous codex refresh is still possible. Claude is covered by `claude_refresh_lock()`
10. **Grok credentials are read-only**: coding-credit usage comes from the official CLI's internal `/v1/billing?format=credits` endpoint. `~/.grok/auth.json` is read but never refreshed or written by cclimits, so an expired token reports as expired until `grok` is run. The endpoint requires the Grok session token plus `X-XAI-Token-Auth`, `x-userid`, `x-grok-client-version`, and `x-grok-client-mode` headers
