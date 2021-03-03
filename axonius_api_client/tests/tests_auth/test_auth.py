# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
import pytest

# from axonius_api_client.api.routers import API_VERSION
from axonius_api_client.auth import ApiKey
from axonius_api_client.exceptions import (
    AlreadyLoggedIn,
    AuthError,
    InvalidCredentials,
    NotLoggedIn,
)
from axonius_api_client.http import Http

from ..utils import get_key_creds, get_url


class TestApiKey:
    """Test axonius_api_client.auth."""

    def test_valid_creds(self, request):
        """Test str/repr has URL."""
        http = Http(url=get_url(request), certwarn=False)

        auth = ApiKey(http=http, **get_key_creds(request))

        auth.login()

        assert auth.is_logged_in
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_logout(self, request):
        """Test no exc when logout() after login()."""
        http = Http(url=get_url(request), certwarn=False)

        auth = ApiKey(http=http, **get_key_creds(request))

        auth.login()

        assert auth.is_logged_in

        auth.logout()

        assert not auth.is_logged_in

    # def test_old_version(self, request, monkeypatch):
    #     """Test exc thrown when login() and login() already called."""
    #     monkeypatch.setattr(ApiKey, "_validate_path", "api/badwolf")

    #     http = Http(url=get_url(request), certwarn=False)
    #     auth = ApiKey(http=http, **get_key_creds(request))
    #     with pytest.raises(AuthError):
    #         auth.login()

    def test_login_already_logged_in(self, request):
        """Test exc thrown when login() and login() already called."""
        http = Http(url=get_url(request), certwarn=False)

        auth = ApiKey(http=http, **get_key_creds(request))

        auth.login()

        with pytest.raises(AlreadyLoggedIn):
            auth.login()

    def test_logout_not_logged_in(self, request):
        """Test exc thrown when logout() but login() not called."""
        http = Http(url=get_url(request), certwarn=False)

        auth = ApiKey(http=http, **get_key_creds(request))

        with pytest.raises(NotLoggedIn):
            auth.logout()

    def test_invalid_creds(self, request):
        """Test str/repr has URL."""
        http = Http(url=get_url(request), certwarn=False)

        bad = "badwolf"

        auth = ApiKey(http=http, key=bad, secret=bad)

        with pytest.raises(InvalidCredentials):
            auth.login()

    def test_http_lock_fail(self, request):
        """Test using an http client from another authmethod throws exc."""
        http = Http(url=get_url(request), certwarn=False)

        auth = ApiKey(http=http, **get_key_creds(request))

        assert auth.http._auth_lock

        with pytest.raises(AuthError):
            auth = ApiKey(http=http, **get_key_creds(request))
