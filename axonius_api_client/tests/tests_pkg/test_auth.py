# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions

from .. import utils


class TestApiKey(object):
    """Test axonius_api_client.auth."""

    def test_valid_creds(self, request):
        """Test str/repr has URL."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))

        auth.login()

        assert auth.is_logged_in
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_logout(self, request):
        """Test no exc when logout() after login()."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))

        auth.login()

        assert auth.is_logged_in

        auth.logout()

        assert not auth.is_logged_in

    def test_login_already_logged_in(self, request):
        """Test exc thrown when login() and login() already called."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))

        auth.login()

        with pytest.raises(exceptions.AlreadyLoggedIn):
            auth.login()

    def test_logout_not_logged_in(self, request):
        """Test exc thrown when logout() but login() not called."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))

        with pytest.raises(exceptions.NotLoggedIn):
            auth.logout()

    def test_invalid_creds(self, request):
        """Test str/repr has URL."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        bad = "badwolf"

        auth = axonapi.ApiKey(http=http, key=bad, secret=bad)

        with pytest.raises(exceptions.InvalidCredentials):
            auth.login()

    def test_http_lock_fail(self, request):
        """Test using an http client from another authmethod throws exc."""
        http = axonapi.Http(url=utils.get_url(request), certwarn=False)

        auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))

        assert auth.http._auth_lock

        with pytest.raises(exceptions.AuthError):
            auth = axonapi.ApiKey(http=http, **utils.get_key_creds(request))
