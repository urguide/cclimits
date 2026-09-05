"""Guard the test suite's credential-discovery defaults."""

from pathlib import Path

import cclimits


def test_all_provider_credentials_are_absent_by_default(tmp_path):
    assert Path.home().is_relative_to(tmp_path)
    assert cclimits.get_claude_credentials() is None
    assert cclimits.get_openai_credentials() == {}
    assert cclimits.get_gemini_credentials() is None
    for provider in cclimits.PROVIDERS:
        if provider["creds"]:
            assert getattr(cclimits, provider["creds"])() is None
    assert cclimits.get_zai_credentials() is None


def test_import_time_credential_paths_are_isolated(tmp_path):
    for name in ("CLAUDE_CRED_PATHS", "CODEX_AUTH_PATHS", "GROK_AUTH_PATHS",
                 "GROK_MODELS_CACHE_PATHS", "ANTIGRAVITY_TOKEN_PATHS"):
        assert all(path.is_relative_to(tmp_path) for path in getattr(cclimits, name))
