"""Tests."""
import pytest

from axonius_api_client.projects.cf_token.flows import (
    GetTokenError,
    flow_get_token_cloudflared,
    flow_get_token,
)
from axonius_api_client.projects.cf_token import constants
from .meta import (
    get_url_bad,
    get_url_good,
    patch_find_cloudflared,
    patch_run_completed,
    patch_clear_token_envs,
    get_token_good,
    get_token_bad,
    patch_run_error,
)


class TestGetTokenError:
    def test_default(self):
        exc = GetTokenError("badwolf")
        assert "badwolf" in str(exc)

    def test_default_list(self):
        exc = GetTokenError(["badwolf", "rose"])
        assert "badwolf\nrose" in str(exc)

    def test_exception(self):
        exception = ValueError("cyberman")
        exc = GetTokenError("badwolf", exception=exception)
        assert "cyberman" in str(exc)
        assert f"Exception type {type(exception)}" in str(exc)

    def test_source(self):
        exc = GetTokenError("badwolf", source="rose")
        assert "While in rose" in str(exc)
        assert "badwolf" in str(exc)


class TestGetTokenCloudflared:
    def test_no_url(self, monkeypatch):
        for clear_key in constants.URL_ENVS:
            monkeypatch.delenv(clear_key, raising=False)

        with pytest.raises(ValueError) as exc:
            flow_get_token_cloudflared()
        assert constants.ERR_TRY_URL in str(exc.value)

    def test_url_env_bad(self, monkeypatch):
        url = get_url_bad()

        for key in constants.URL_ENVS:
            for clear_key in constants.URL_ENVS:
                monkeypatch.delenv(clear_key, raising=False)

            monkeypatch.setenv(key, url)
            with pytest.raises(ValueError) as exc:
                flow_get_token_cloudflared()
            assert constants.ERR_TRY_URL in str(exc.value)

    def test_path_bad(self):
        url = get_url_good()
        path = "badwolf"
        with pytest.raises(FileNotFoundError) as exc:
            flow_get_token_cloudflared(url=url, path=path)
        assert constants.ERR_FILE_NOT_FOUND in str(exc.value)

    def test_run_both_false(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url, run_login=False, run_access=False)
        assert constants.ERR_RUN_ACCESS_LOGIN in str(exc.value)

    def test_run_login_false_access_failure(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url, run_login=False)
        assert constants.ERR_RUN_ACCESS in str(exc.value)

    def test_run_access_false_login_failure(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url, run_access=False)
        assert constants.ERR_RUN_LOGIN in str(exc.value)

    def test_run_login_true_switched_false_access_failure(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url)
        assert constants.ERR_RUN_ACCESS in str(exc.value)

    def test_run_login_true_switched_false_no_error(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        data = flow_get_token_cloudflared(url=url, error=False, error_access=False)
        assert data is None

    def test_run_login_true_switched_false_error_access(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url, error=False, error_access=True)
        assert constants.ERR_RUN_ACCESS in str(exc.value)

    def test_run_login_true_switched_false_error(self, monkeypatch):
        url = get_url_good()

        patch_find_cloudflared(monkeypatch)

        with pytest.raises(GetTokenError) as exc:
            flow_get_token_cloudflared(url=url, error=True, error_access=False)
        assert constants.ERR_RUN_ACCESS_LOGIN in str(exc.value)

    def test_run_access_success_valid_token(self, monkeypatch):
        token = get_token_good()
        url = get_url_good()
        stdout = f"\n\n{token}"

        patch_find_cloudflared(monkeypatch)
        patch_run_completed(monkeypatch, cmd=constants.CMD_ACCESS_STR, stdout=stdout)

        data = flow_get_token_cloudflared(url=url)
        assert data == token

    def test_run_access_success_invalid_token(self, monkeypatch):
        token = get_token_bad()
        url = get_url_good()
        stdout = f"\n\n{token}"

        patch_find_cloudflared(monkeypatch)
        patch_run_completed(monkeypatch, cmd=constants.CMD_ACCESS_STR, stdout=stdout)

        with pytest.raises(ValueError) as exc:
            flow_get_token_cloudflared(url=url)
        assert constants.ERR_TOKEN_FOUND_INVALID in str(exc.value)

    def test_run_login_success(self, monkeypatch):
        token = get_token_good()
        url = get_url_good()
        stdout = f"\n\n{token}"

        patch_find_cloudflared(monkeypatch)
        patch_run_completed(monkeypatch, cmd=constants.CMD_LOGIN_STR, stdout=stdout)

        data = flow_get_token_cloudflared(url=url, run_access=False)
        assert data == token

    def test_run_login_error_login_true(self, monkeypatch):
        token = get_token_bad()
        url = get_url_good()
        stdout = f"\n\n{token}"

        patch_find_cloudflared(monkeypatch)
        patch_run_completed(monkeypatch, cmd=constants.CMD_LOGIN_STR, stdout=stdout)

        with pytest.raises(ValueError) as exc:
            flow_get_token_cloudflared(url=url, run_access=False, run_login=True, error_login=True)
        assert constants.ERR_TOKEN_FOUND_INVALID in str(exc.value)

    def test_run_login_error_login_false(self, monkeypatch, caplog):
        url = get_url_good()
        stdout = f""
        stderr = "some error"

        patch_find_cloudflared(monkeypatch)
        patch_run_error(monkeypatch, cmd=constants.CMD_LOGIN_STR, stdout=stdout, stderr=stderr)

        data = flow_get_token_cloudflared(
            url=url,
            run_access=False,
            error_login=False,
            run_login=True,
            error=False,
        )
        assert not data
        assert constants.ERR_RUN_LOGIN in caplog.text


class TestFlowGetToken:
    def test_supplied_token_valid(self):
        token = get_token_good()

        data = flow_get_token(token=token)
        assert data == token

    def test_supplied_token_invalid(self):
        token = get_token_bad()

        with pytest.raises(ValueError) as exc:
            flow_get_token(token=token)
        assert constants.ERR_TOKEN_FOUND_INVALID in str(exc.value)

    def test_all_false(self):
        with pytest.raises(ValueError) as exc:
            flow_get_token(run=False, run_login=False, run_access=False, env=False)
        assert constants.ERR_RUN_NONE in str(exc.value)

    def test_env_success(self, monkeypatch):
        token = get_token_good()

        patch_clear_token_envs(monkeypatch)
        monkeypatch.setenv(constants.TOKEN_ENVS[0], token)

        data = flow_get_token(env=True, run=False, run_login=False, run_access=False)
        assert data == token

    def test_env_failure_error(self, monkeypatch):
        token = get_token_bad()

        patch_clear_token_envs(monkeypatch)
        monkeypatch.setenv(constants.TOKEN_ENVS[0], token)

        with pytest.raises(ValueError) as exc:
            flow_get_token(env=True, run=False, run_login=False, run_access=False)
        assert constants.ERR_TOKEN_ENV in str(exc.value)

    def test_env_failure_no_error(self, monkeypatch):
        token = get_token_bad()

        patch_clear_token_envs(monkeypatch)
        monkeypatch.setenv(constants.TOKEN_ENVS[0], token)

        data = flow_get_token(env=True, error=False, run=False, run_login=False, run_access=False)
        assert data is None

    def test_run_mock(self, monkeypatch):
        token = get_token_good()
        stdout = f"\n\n{token}"

        patch_find_cloudflared(monkeypatch)
        patch_run_completed(monkeypatch, cmd=constants.CMD_ACCESS_STR, stdout=stdout)

        data = flow_get_token(run=True, run_login=False, run_access=True, env=False)
        assert data == token
