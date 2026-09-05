# Tech Context: cclimits

## Tech Stack

| Component | Technology |
|-----------|------------|
| Core Script | Python 3.9+ |
| npm Wrapper | Node.js 16+ |
| HTTP Client | requests (optional), urllib (fallback) |
| Distribution | npm, GitHub |

## Project Structure

```
cclimits/
├── bin/
│   └── cclimits.js      # Node wrapper
├── lib/
│   └── cclimits.py      # Main Python script
├── memory-bank/         # AI context files
├── package.json         # npm config
├── README.md
└── LICENSE              # MIT
```

## Dependencies

### Runtime
- **Python 3.9+**: Required (type hints deferred with __future__)
- **requests**: Optional (improves HTTP handling)
- **Node.js 16+**: Required for npx distribution

### Development
- `pytest` and `requests` from `requirements-dev.txt`; no build step
- `python3 -m pytest tests/ -q` runs isolated tests, including tmux fake-executable tests
- CI: Python 3.9/3.11/3.13 with requests and genuine urllib-only environments

## Commands

```bash
# Run via npx
npx cclimits
npx cclimits --oneline
npx cclimits --json

# Run directly (if Python script accessible)
python3 lib/cclimits.py --claude
python3 lib/cclimits.py --oneline 7d

# Publish new version
npm version patch  # or minor, major
npm publish
```

## Credential Locations

| Tool | macOS | Linux |
|------|-------|-------|
| Claude | Keychain "Claude Code-credentials" | `~/.claude/.credentials.json` |
| Codex | `~/.codex/auth.json` | `~/.codex/auth.json` |
| Gemini | `~/.gemini/oauth_creds.json` | `~/.gemini/oauth_creds.json` |
| Z.AI | `$ZAI_KEY` env var | `$ZAI_KEY` env var |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GEMINI_OAUTH_CLIENT_ID` | Override Gemini OAuth client ID |
| `GEMINI_OAUTH_CLIENT_SECRET` | Override Gemini OAuth client secret |
| `ZAI_KEY` / `ZAI_API_KEY` | Z.AI API key |
| `CLAUDE_ACCESS_TOKEN` | Override Claude token |
| `OPENAI_API_KEY` | Fallback for Codex |

## npm Publishing

```bash
# Ensure logged in
npm whoami

# Publish (requires 2FA or automation token)
npm publish

# Automated publishing uses the v* tag workflow with npm Trusted Publishing.
# Configure its repository/workflow identity in npm before publishing a fork.
```

## Related Projects

- **daplug**: Plugin that bundles cclimits as a skill
- **rogers_ai_rules**: Parent repo for daplug
