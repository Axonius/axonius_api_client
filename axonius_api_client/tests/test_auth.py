# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

import axonius_api_client as axonapi


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
class TestAuth(object):
    """Test axonius_api_client.auth."""

    @pytest.mark.needs_key_creds
    def test_valid_creds(self, url, creds):
        """Test str/repr has URL."""
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        assert auth.is_logged_in
        assert "url" in format(auth)
        assert "url" in repr(auth)

    @pytest.mark.needs_key_creds
    def test_logout(self, url, creds):
        """Test no exc when logout() after login()."""
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        auth.logout()
        assert not auth.is_logged_in

    @pytest.mark.needs_key_creds
    def test_login_already_logged_in(self, url, creds):
        """Test exc thrown when login() and login() already called."""
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        with pytest.raises(axonapi.AlreadyLoggedIn):
            auth.login()

    @pytest.mark.needs_key_creds
    def test_logout_not_logged_in(self, url, creds):
        """Test exc thrown when logout() but login() not called."""
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        with pytest.raises(axonapi.NotLoggedIn):
            auth.logout()

    def test_invalid_creds(self, url, creds):
        """Test str/repr has URL."""
        http = axonapi.Http(url=url, certwarn=False)
        bad_creds = {k: "badwolf1" for k in creds["creds"]}
        auth = creds["cls"](http=http, **bad_creds)
        with pytest.raises(axonapi.InvalidCredentials):
            auth.login()

    def test_http_lock_fail(self, url, creds):
        """Test using an http client from another authmethod throws exc."""
        http = axonapi.Http(url=url)
        auth = creds["cls"](http=http, **creds["creds"])
        assert auth.http._auth_lock
        with pytest.raises(axonapi.AuthError):
            creds["cls"](http=http, **creds["creds"])
