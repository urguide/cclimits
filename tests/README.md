# Test Suite for cclimits

## Running Tests

```bash
python3 -m pip install -r requirements-dev.txt
python3 -m pytest tests/ -q
python3 -m pytest tests/test_credentials.py -v
python3 -m pytest tests/ --collect-only -q
```

For a genuine zero-requests environment, use a separate virtual environment:

```bash
python3 -m venv /tmp/cclimits-urllib-tests
/tmp/cclimits-urllib-tests/bin/python -m pip install pytest
/tmp/cclimits-urllib-tests/bin/python -m pytest tests/ -k "not WithRequests" -q
```

The nine `WithRequests` cases require the optional library. CI tests both
backends on Python 3.9, 3.11, and 3.13. Use collection output for current test
counts rather than maintaining duplicate counts here.

## Coverage

| File | Scope |
|------|-------|
| `test_isolation.py` | Empty default credentials and isolated discovery paths |
| `test_credentials.py` | Discovery, source selection, refresh locks, write-back, recovery data |
| `test_http.py` | requests and urllib request/response behavior |
| `test_usage.py` | Mocked provider quotas, HTTP failures, reset windows |
| `test_utils.py` | Cache ages, concurrent writes, stale eligibility, time formatting |
| `test_output.py` | Detailed/oneline output, compact mode, icons and reset placeholders |
| `test_cli.py` | Flags, JSON contract, cache selection, repeated outages and parallel fetches |
| `test_tmux_wrapper.py` | Fake-executable end-to-end tests for watch mode and per-provider merging |

## Isolation Rules

- `conftest.py` redirects HOME, cache paths, and import-time credential paths to
  temporary directories, clears provider/cclimits environment overrides, and
  stubs the application's external credential-discovery commands.
- Network access is blocked at requests, urllib, and socket boundaries. An
  attempted unmocked request fails the test, including at teardown if swallowed.
- Mock a provider's HTTP or credential boundary explicitly. Claude usage tests
  patch `ensure_claude_token`; refresh tests use real temporary credential files
  and mock only the token endpoint.
- Wrapper tests override TMPDIR, cclimits, and Grok paths. Never launch a real
  provider CLI from tests; fake executables simulate state transitions.
- Time-sensitive regressions should freeze the clock. Test consecutive cache
  reads/writes, not just a single stale-fallback call.

Tests do not validate live provider schemas or real macOS Keychain behavior.
Run live account checks separately and intentionally, never as part of pytest.
