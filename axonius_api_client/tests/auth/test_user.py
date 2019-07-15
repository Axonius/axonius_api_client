# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


@pytest.mark.needs_url
class TestAuthUser(object):
    """Test axonius_api_client.auth.AuthUser."""

    auth_cls = axonius_api_client.auth.AuthUser
    bad_creds = {"username": "bad", "password": "bad"}

    @pytest.mark.needs_user_creds
    def test_valid_creds(self, api_url, creds_user):
        """Test str/repr has URL."""
        creds = {k: v for k, v in creds_user.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = self.auth_cls(http_client=http_client, **creds)
        auth.login()
        assert auth.is_logged_in
        assert "url" in format(auth)
        assert "url" in repr(auth)

    @pytest.mark.needs_user_creds
    def test_logout(self, api_url, creds_user):
        """Test no exc when logout() after login()."""
        creds = {k: v for k, v in creds_user.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = self.auth_cls(http_client=http_client, **creds)
        auth.login()
        auth.logout()
        assert not auth.is_logged_in

    @pytest.mark.needs_user_creds
    def test_logout_not_logged_in(self, api_url, creds_user):
        """Test exc thrown when logout() but login() not called."""
        creds = {k: v for k, v in creds_user.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = self.auth_cls(http_client=http_client, **creds)
        with pytest.raises(axonius_api_client.auth.exceptions.NotLoggedIn):
            auth.logout()

    @pytest.mark.needs_user_creds
    def test_login_already_logged_in(self, api_url, creds_user):
        """Test exc thrown when login() and login() already called."""
        creds = {k: v for k, v in creds_user.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = self.auth_cls(http_client=http_client, **creds)
        auth.login()
        with pytest.raises(axonius_api_client.auth.exceptions.AlreadyLoggedIn):
            auth.login()

    def test_invalid_creds(self, api_url):
        """Test str/repr has URL."""
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = self.auth_cls(http_client=http_client, **self.bad_creds)
        with pytest.raises(axonius_api_client.auth.exceptions.InvalidCredentials):
            auth.login()

    def test_http_lock_fail(self, api_url):
        """Test using an http client from another authmethod throws exc."""
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth1 = self.auth_cls(http_client=http_client, **self.bad_creds)
        assert auth1.http_client._auth_lock
        with pytest.raises(axonius_api_client.auth.exceptions.AuthError):
            self.auth_cls(http_client=http_client, **self.bad_creds)
