"""
Tests for credential discovery functions.
"""

import base64
import json
import os
import stat
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pytest
import cclimits
from cclimits import (
    get_claude_credentials,
    get_openai_credentials,
    get_gemini_oauth_creds,
    get_gemini_credentials,
    get_zai_credentials,
    ensure_claude_token,
    ensure_codex_credentials,
    jwt_claims,
    write_json_secure,
)


class TestGetClaudeCredentials:
    """Tests for get_claude_credentials() function."""

    @patch('cclimits.sys.platform', 'darwin')
    @patch('cclimits.subprocess.run')
    def test_macos_keychain_nested_structure(self, mock_run):
        """Test Claude credentials from macOS Keychain (nested structure)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "claudeAiOauth": {
                "accessToken": "test-token-nested"
            }
        })
        mock_run.return_value = mock_result

        token = get_claude_credentials()
        assert token == "test-token-nested"

    @patch('cclimits.sys.platform', 'darwin')
    @patch('cclimits.subprocess.run')
    def test_macos_keychain_flat_structure(self, mock_run):
        """Test Claude credentials from macOS Keychain (flat structure)."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "accessToken": "test-token-flat"
        })
        mock_run.return_value = mock_result

        token = get_claude_credentials()
        assert token == "test-token-flat"

    @patch('cclimits.sys.platform', 'darwin')
    @patch('cclimits.subprocess.run')
    def test_macos_keychain_failure(self, mock_run):
        """Test macOS Keychain command failure."""
        mock_run.side_effect = Exception("security command failed")

        token = get_claude_credentials()
        # Should fallback to file or env, which won't exist
        assert token is None or isinstance(token, str)

    @patch('cclimits.Path.exists', return_value=False)
    @patch('cclimits.os.environ.get')
    def test_env_variable(self, mock_get, mock_exists):
        """Test Claude credentials from environment variable."""
        mock_get.return_value = "env-token"

        token = get_claude_credentials()
        assert token == "env-token"

    @patch('cclimits.Path.exists', return_value=False)
    @patch('cclimits.os.environ.get')
    def test_no_credentials(self, mock_get, mock_exists):
        """Test when no credentials are found."""
        mock_get.return_value = None

        # Make sure file paths don't exist
        token = get_claude_credentials()
        assert token is None


class TestGetOpenAICredentials:
    """Tests for get_openai_credentials() function."""

    @patch('cclimits.os.environ.get')
    def test_api_key_from_env(self, mock_get):
        """Test OpenAI API key from environment variable."""
        mock_get.return_value = "sk-test-api-key"

        creds = get_openai_credentials()
        assert creds["api_key"] == "sk-test-api-key"

    @patch('cclimits.os.environ.get')
    @patch('cclimits.Path.exists')
    @patch('cclimits.Path.read_text')
    def test_auth_file_with_api_key(self, mock_read, mock_exists, mock_get):
        """Test OpenAI credentials from auth file with API key."""
        mock_get.return_value = None
        mock_exists.return_value = True
        mock_read.return_value = json.dumps({
            "OPENAI_API_KEY": "file-api-key"
        })

        creds = get_openai_credentials()
        assert creds["api_key"] == "file-api-key"

    @patch('cclimits.os.environ.get')
    @patch('cclimits.Path.exists')
    @patch('cclimits.Path.read_text')
    def test_auth_file_with_oauth(self, mock_read, mock_exists, mock_get):
        """Test OpenAI credentials from auth file with OAuth tokens."""
        mock_get.return_value = None
        mock_exists.return_value = True
        mock_read.return_value = json.dumps({
            "tokens": {
                "access_token": "test-access-token",
                "account_id": "test-account-id"
            }
        })

        creds = get_openai_credentials()
        assert creds["access_token"] == "test-access-token"
        assert creds["account_id"] == "test-account-id"

    @patch('cclimits.os.environ.get')
    def test_no_credentials(self, mock_get):
        """Test when no OpenAI credentials are found."""
        mock_get.return_value = None

        # Make sure paths don't exist
        with patch('cclimits.Path.exists', return_value=False):
            creds = get_openai_credentials()
            assert creds == {}


class TestGetGeminiOAuthCreds:
    """Tests for get_gemini_oauth_creds() function."""

    @patch('cclimits.os.environ.get')
    def test_from_environment(self, mock_get):
        """Test Gemini OAuth creds from environment variables."""
        def get_side_effect(key):
            if key == "GEMINI_OAUTH_CLIENT_ID":
                return "test-client-id"
            elif key == "GEMINI_OAUTH_CLIENT_SECRET":
                return "test-client-secret"
            return None
        
        mock_get.side_effect = get_side_effect

        creds = get_gemini_oauth_creds()
        assert creds == ("test-client-id", "test-client-secret")

    @patch('cclimits.os.environ.get')
    def test_partial_env_creds(self, mock_get):
        """Test partial environment credentials (should return None)."""
        def get_side_effect(key):
            if key == "GEMINI_OAUTH_CLIENT_ID":
                return "test-client-id"
            return None
        
        mock_get.side_effect = get_side_effect

        creds = get_gemini_oauth_creds()
        assert creds is None


class TestGetGeminiCredentials:
    """Tests for get_gemini_credentials() function."""

    @patch('cclimits.os.environ.get')
    def test_api_key_from_env(self, mock_get):
        """Test Gemini API key from environment."""
        mock_get.return_value = "test-gemini-api-key"

        creds = get_gemini_credentials()
        assert creds["api_key"] == "test-gemini-api-key"

    @patch('cclimits.os.environ.get')
    def test_google_api_key_fallback(self, mock_get):
        """Test GOOGLE_API_KEY as fallback."""
        def get_side_effect(key):
            if key == "GEMINI_API_KEY":
                return None
            elif key == "GOOGLE_API_KEY":
                return "google-api-key"
            return None
        
        mock_get.side_effect = get_side_effect

        creds = get_gemini_credentials()
        assert creds["api_key"] == "google-api-key"


class TestGetZAICredentials:
    """Tests for get_zai_credentials() function."""

    @patch('cclimits.os.environ.get')
    def test_zai_api_key(self, mock_get):
        """Test Z.AI API key from ZAI_API_KEY."""
        def get_side_effect(key):
            if key == "ZAI_API_KEY":
                return "zai-test-key"
            return None
        
        mock_get.side_effect = get_side_effect

        key = get_zai_credentials()
        assert key == "zai-test-key"

    @patch('cclimits.os.environ.get')
    def test_zai_key_fallback(self, mock_get):
        """Test Z.AI key from ZAI_KEY."""
        def get_side_effect(key):
            if key == "ZAI_API_KEY":
                return None
            elif key == "ZAI_KEY":
                return "zai-key-alt"
            return None
        
        mock_get.side_effect = get_side_effect

        key = get_zai_credentials()
        assert key == "zai-key-alt"

    @patch('cclimits.os.environ.get')
    def test_zhipu_api_key(self, mock_get):
        """Test Z.AI key from ZHIPU_API_KEY."""
        def get_side_effect(key):
            if key in ["ZAI_API_KEY", "ZAI_KEY"]:
                return None
            elif key == "ZHIPU_API_KEY":
                return "zhipu-test-key"
            return None
        
        mock_get.side_effect = get_side_effect

        key = get_zai_credentials()
        assert key == "zhipu-test-key"

    @patch('cclimits.os.environ.get')
    def test_no_credentials(self, mock_get):
        """Test when no Z.AI credentials are found."""
        mock_get.return_value = None

        key = get_zai_credentials()
        assert key is None


def _fake_jwt(claims: dict) -> str:
    """Build an unsigned JWT carrying *claims* (only the payload is read)."""
    def seg(obj):
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()
    return f"{seg({'alg': 'none'})}.{seg(claims)}.signature"


class TestJwtClaims:
    """Tests for jwt_claims() payload decoding."""

    def test_decodes_payload(self):
        assert jwt_claims(_fake_jwt({"exp": 123, "client_id": "app_x"})) == {
            "exp": 123, "client_id": "app_x",
        }

    @pytest.mark.parametrize("token", [None, "", "not-a-jwt", "a.b", "a.!!!.c"])
    def test_rejects_non_jwt(self, token):
        assert jwt_claims(token) is None


class TestGetGrokCredentials:
    """Tests for get_grok_credentials() — reads Grok CLI's ~/.grok/auth.json."""

    @staticmethod
    def _write_auth(tmp_path, monkeypatch, payload):
        auth = tmp_path / "grok-auth.json"
        auth.write_text(json.dumps(payload))
        monkeypatch.setattr(cclimits, "GROK_AUTH_PATHS", [auth])
        return auth

    def test_reads_scoped_entry(self, tmp_path, monkeypatch):
        """The token lives under an '<issuer>::<client_id>' key, not at the root."""
        self._write_auth(tmp_path, monkeypatch, {
            "https://auth.x.ai::client-abc": {
                "key": "token-abc",
                "refresh_token": "refresh-abc",
                "expires_at": "2026-08-10T08:16:35.159114061Z",
            }
        })

        creds = cclimits.get_grok_credentials()
        assert creds["access_token"] == "token-abc"
        assert creds["source"] == "grok-cli"

    def test_picks_latest_expiry_among_scopes(self, tmp_path, monkeypatch):
        """With several scopes present, the longest-lived token is the active one."""
        self._write_auth(tmp_path, monkeypatch, {
            "https://auth.x.ai::old": {"key": "stale", "expires_at": "2026-01-01T00:00:00Z"},
            "https://auth.x.ai::new": {"key": "fresh", "expires_at": "2026-12-01T00:00:00Z"},
        })

        assert cclimits.get_grok_credentials()["access_token"] == "fresh"

    def test_skips_entries_without_key(self, tmp_path, monkeypatch):
        self._write_auth(tmp_path, monkeypatch, {
            "https://auth.x.ai::empty": {"refresh_token": "only-refresh"},
        })

        assert cclimits.get_grok_credentials() is None

    def test_malformed_file_is_not_fatal(self, tmp_path, monkeypatch):
        auth = tmp_path / "grok-auth.json"
        auth.write_text("{not json")
        monkeypatch.setattr(cclimits, "GROK_AUTH_PATHS", [auth])

        assert cclimits.get_grok_credentials() is None

    def test_env_fallback(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cclimits, "GROK_AUTH_PATHS", [tmp_path / "missing.json"])
        monkeypatch.setenv("GROK_ACCESS_TOKEN", "env-token")

        creds = cclimits.get_grok_credentials()
        assert creds["access_token"] == "env-token"
        assert creds["source"] == "GROK_ACCESS_TOKEN"

    def test_auth_file_wins_over_env(self, tmp_path, monkeypatch):
        self._write_auth(tmp_path, monkeypatch, {
            "https://auth.x.ai::c": {"key": "file-token", "expires_at": "2026-12-01T00:00:00Z"},
        })
        monkeypatch.setenv("GROK_ACCESS_TOKEN", "env-token")

        assert cclimits.get_grok_credentials()["access_token"] == "file-token"

    def test_no_credentials(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cclimits, "GROK_AUTH_PATHS", [tmp_path / "missing.json"])

        assert cclimits.get_grok_credentials() is None


class TestGetGrokClientVersion:
    def test_reads_models_cache(self, tmp_path, monkeypatch):
        cache = tmp_path / "models_cache.json"
        cache.write_text(json.dumps({"grok_version": "0.3.1"}))
        monkeypatch.setattr(cclimits, "GROK_MODELS_CACHE_PATHS", [cache])

        assert cclimits._get_grok_client_version() == "0.3.1"

    def test_env_override(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cclimits, "GROK_MODELS_CACHE_PATHS", [tmp_path / "missing.json"])
        monkeypatch.setenv("GROK_CLIENT_VERSION", "9.9.9")

        assert cclimits._get_grok_client_version() == "9.9.9"


class TestWriteJsonSecure:
    """Tests for write_json_secure() — credential files must stay private."""

    def test_writes_0600_and_leaves_no_temp(self, tmp_path):
        target = tmp_path / "creds.json"
        write_json_secure(target, {"a": 1})

        assert json.loads(target.read_text()) == {"a": 1}
        assert stat.S_IMODE(target.stat().st_mode) == 0o600
        assert not (tmp_path / "creds.json.tmp").exists()

    def test_tightens_permissions_on_existing_loose_file(self, tmp_path):
        target = tmp_path / "creds.json"
        target.write_text("{}")
        target.chmod(0o644)

        write_json_secure(target, {"a": 2})

        assert stat.S_IMODE(target.stat().st_mode) == 0o600


@pytest.fixture
def claude_creds(tmp_path, monkeypatch):
    """Point Claude credential lookup at a temp file and return a writer."""
    monkeypatch.delenv("CLAUDE_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("CCLIMITS_NO_TOKEN_REFRESH", raising=False)
    monkeypatch.setattr(cclimits.sys, "platform", "linux")
    path = tmp_path / ".credentials.json"
    monkeypatch.setattr(cclimits, "CLAUDE_CRED_PATHS", [path])

    def write(**overrides):
        oauth = {
            "accessToken": "old-access",
            "refreshToken": "old-refresh",
            "expiresAt": int((time.time() + 3600) * 1000),
            "scopes": ["user:inference"],
            "subscriptionType": "team",
        }
        oauth.update(overrides)
        write_json_secure(path, {"claudeAiOauth": oauth})
        return path

    write.path = path
    return write


class TestEnsureClaudeToken:
    """Tests for ensure_claude_token() refresh-and-write-back."""

    def test_unexpired_token_is_used_as_is(self, claude_creds):
        claude_creds()
        with patch('cclimits.http_post') as mock_post:
            assert ensure_claude_token() == "old-access"
        mock_post.assert_not_called()

    def test_expired_token_is_refreshed_and_written_back(self, claude_creds):
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "new-access",
            "expires_in": 28800,
        })) as mock_post:
            assert ensure_claude_token() == "new-access"

        url, headers, body = mock_post.call_args[0]
        assert url == cclimits.CLAUDE_TOKEN_URL
        assert body["grant_type"] == "refresh_token"
        assert body["refresh_token"] == "old-refresh"
        assert body["client_id"] == cclimits.CLAUDE_OAUTH_CLIENT_ID

        saved = json.loads(path.read_text())["claudeAiOauth"]
        assert saved["accessToken"] == "new-access"
        assert saved["expiresAt"] > time.time() * 1000
        # Untouched fields survive the merge
        assert saved["refreshToken"] == "old-refresh"
        assert saved["subscriptionType"] == "team"
        assert stat.S_IMODE(path.stat().st_mode) == 0o600

    def test_rotated_refresh_token_is_persisted(self, claude_creds):
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "new-access",
            "expires_in": 28800,
            "refresh_token": "rotated-refresh",
            "refresh_token_expires_in": 2592000,
        })):
            ensure_claude_token()

        saved = json.loads(path.read_text())["claudeAiOauth"]
        assert saved["refreshToken"] == "rotated-refresh"
        assert saved["refreshTokenExpiresAt"] > time.time() * 1000

    def test_failed_refresh_leaves_file_untouched(self, claude_creds):
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))
        before = path.read_text()

        with patch('cclimits.http_post', return_value=(400, {"error": "invalid_grant"})):
            assert ensure_claude_token() == "old-access"

        assert path.read_text() == before

    def test_missing_refresh_token_is_not_an_error(self, claude_creds):
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))
        data = json.loads(path.read_text())
        data["claudeAiOauth"].pop("refreshToken")
        write_json_secure(path, data)

        with patch('cclimits.http_post') as mock_post:
            assert ensure_claude_token() == "old-access"
        mock_post.assert_not_called()

    def test_opt_out_disables_refresh(self, claude_creds, monkeypatch):
        claude_creds(expiresAt=int((time.time() - 60) * 1000))
        monkeypatch.setenv("CCLIMITS_NO_TOKEN_REFRESH", "1")

        with patch('cclimits.http_post') as mock_post:
            assert ensure_claude_token() == "old-access"
        mock_post.assert_not_called()

    def test_force_refreshes_an_unexpired_token(self, claude_creds):
        claude_creds()

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "forced-access",
            "expires_in": 28800,
        })):
            assert ensure_claude_token(force=True) == "forced-access"

    def test_busy_lock_falls_back_to_stored_token(self, claude_creds, monkeypatch):
        """Another process mid-refresh must not stall a status line."""
        import fcntl

        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))
        monkeypatch.setattr(cclimits, "TOKEN_LOCK_TIMEOUT", 0.05)

        lock_path = path.with_name(path.name + ".lock")
        holder = os.open(lock_path, os.O_WRONLY | os.O_CREAT, 0o600)
        fcntl.flock(holder, fcntl.LOCK_EX)
        try:
            with patch('cclimits.http_post') as mock_post:
                assert ensure_claude_token() == "old-access"
            mock_post.assert_not_called()
        finally:
            fcntl.flock(holder, fcntl.LOCK_UN)
            os.close(holder)

    def test_stands_down_while_claude_code_is_refreshing(self, claude_creds, monkeypatch):
        """Claude Code's own proper-lockfile dir must block our refresh."""
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))
        monkeypatch.setattr(cclimits, "TOKEN_LOCK_TIMEOUT", 0.05)

        lock_dir = path.parent / cclimits.CLAUDE_REFRESH_LOCK_NAME
        lock_dir.mkdir()
        try:
            with patch('cclimits.http_post') as mock_post:
                assert ensure_claude_token() == "old-access"
            mock_post.assert_not_called()
            # We must not have removed a lock we don't own.
            assert lock_dir.is_dir()
        finally:
            lock_dir.rmdir()

    def test_steals_a_stale_claude_code_lock(self, claude_creds):
        """A crashed CLI's abandoned lock must not block us forever."""
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))
        lock_dir = path.parent / cclimits.CLAUDE_REFRESH_LOCK_NAME
        lock_dir.mkdir()
        stale = time.time() - (cclimits.CLAUDE_REFRESH_LOCK_STALE + 10)
        os.utime(lock_dir, (stale, stale))

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "new-access",
            "expires_in": 28800,
        })):
            assert ensure_claude_token() == "new-access"

        # Released again once we're done.
        assert not lock_dir.exists()

    def test_releases_the_refresh_lock_after_success(self, claude_creds):
        path = claude_creds(expiresAt=int((time.time() - 60) * 1000))

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "new-access",
            "expires_in": 28800,
        })):
            ensure_claude_token()

        assert not (path.parent / cclimits.CLAUDE_REFRESH_LOCK_NAME).exists()

    def test_no_credential_file_returns_none(self, tmp_path, monkeypatch):
        monkeypatch.delenv("CLAUDE_ACCESS_TOKEN", raising=False)
        monkeypatch.setattr(cclimits.sys, "platform", "linux")
        monkeypatch.setattr(cclimits, "CLAUDE_CRED_PATHS", [tmp_path / "nope.json"])

        with patch('cclimits.http_post') as mock_post:
            assert ensure_claude_token() is None
        mock_post.assert_not_called()


@pytest.fixture
def codex_auth(tmp_path, monkeypatch):
    """Point Codex credential lookup at a temp auth.json and return a writer."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("CCLIMITS_NO_TOKEN_REFRESH", raising=False)
    path = tmp_path / "auth.json"
    monkeypatch.setattr(cclimits, "CODEX_AUTH_PATHS", [path])

    def write(exp_offset=3600, **overrides):
        tokens = {
            "access_token": _fake_jwt({
                "exp": int(time.time() + exp_offset),
                "client_id": "app_from_jwt",
            }),
            "refresh_token": "old-refresh",
            "id_token": _fake_jwt({"sub": "user"}),
            "account_id": "acct-old",
        }
        tokens.update(overrides)
        write_json_secure(path, {
            "OPENAI_API_KEY": None,
            "auth_mode": "chatgpt",
            "tokens": tokens,
            "last_refresh": "2026-01-01T00:00:00Z",
        })
        return path

    write.path = path
    return write


class TestEnsureCodexCredentials:
    """Tests for ensure_codex_credentials() refresh-and-write-back."""

    def test_unexpired_token_is_used_as_is(self, codex_auth):
        codex_auth()
        with patch('cclimits.http_post') as mock_post:
            creds = ensure_codex_credentials()
        mock_post.assert_not_called()
        assert creds["account_id"] == "acct-old"

    def test_expired_token_is_refreshed_and_written_back(self, codex_auth):
        path = codex_auth(exp_offset=-60)
        new_id_token = _fake_jwt({
            "https://api.openai.com/auth": {"chatgpt_account_id": "acct-new"},
        })

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "new-access",
            "refresh_token": "rotated-refresh",
            "id_token": new_id_token,
        })) as mock_post:
            creds = ensure_codex_credentials()

        url, headers, body = mock_post.call_args[0]
        assert url == cclimits.CODEX_TOKEN_URL
        assert body["grant_type"] == "refresh_token"
        assert body["refresh_token"] == "old-refresh"
        # client_id comes from the user's own token, not the baked-in default
        assert body["client_id"] == "app_from_jwt"
        assert body["scope"] == cclimits.CODEX_OAUTH_SCOPE

        saved = json.loads(path.read_text())
        assert saved["tokens"]["access_token"] == "new-access"
        # OpenAI rotates the refresh token — persisting it is mandatory
        assert saved["tokens"]["refresh_token"] == "rotated-refresh"
        assert saved["tokens"]["id_token"] == new_id_token
        assert saved["tokens"]["account_id"] == "acct-new"
        assert saved["last_refresh"] != "2026-01-01T00:00:00Z"
        assert saved["auth_mode"] == "chatgpt"
        assert stat.S_IMODE(path.stat().st_mode) == 0o600

        assert creds["access_token"] == "new-access"
        assert creds["account_id"] == "acct-new"

    def test_failed_refresh_leaves_file_untouched(self, codex_auth):
        path = codex_auth(exp_offset=-60)
        before = path.read_text()

        with patch('cclimits.http_post', return_value=(401, "unauthorized")):
            creds = ensure_codex_credentials()

        assert path.read_text() == before
        assert creds["account_id"] == "acct-old"

    def test_unparseable_expiry_does_not_trigger_refresh(self, codex_auth):
        codex_auth(access_token="opaque-not-a-jwt")

        with patch('cclimits.http_post') as mock_post:
            ensure_codex_credentials()
        mock_post.assert_not_called()

    def test_opt_out_disables_refresh(self, codex_auth, monkeypatch):
        codex_auth(exp_offset=-60)
        monkeypatch.setenv("CCLIMITS_NO_TOKEN_REFRESH", "1")

        with patch('cclimits.http_post') as mock_post:
            ensure_codex_credentials()
        mock_post.assert_not_called()

    def test_force_refreshes_an_unexpired_token(self, codex_auth):
        codex_auth()

        with patch('cclimits.http_post', return_value=(200, {
            "access_token": "forced-access",
        })):
            creds = ensure_codex_credentials(force=True)

        assert creds["access_token"] == "forced-access"
