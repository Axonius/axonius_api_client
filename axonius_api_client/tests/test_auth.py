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

    @pytest.mark.needs_user_creds
    def test_valid_creds(self, api_url, creds_user):
        """Test str/repr has URL."""
        creds = {k: v for k, v in creds_user.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = axonius_api_client.auth.AuthUser(http_client=http_client, **creds)
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_invalid_creds(self, api_url):
        """Test str/repr has URL."""
        creds = {"username": "bad", "password": "bad"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        with pytest.raises(axonius_api_client.exceptions.InvalidCredentials):
            axonius_api_client.auth.AuthUser(http_client=http_client, **creds)


@pytest.mark.needs_url
class TestAuthKey(object):
    """Test axonius_api_client.auth.AuthKey."""

    @pytest.mark.needs_key_creds
    def test_valid_creds(self, api_url, creds_key):
        """Test str/repr has URL."""
        creds = {k: v for k, v in creds_key.items() if k != "cls"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = axonius_api_client.auth.AuthKey(http_client=http_client, **creds)
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_invalid_creds(self, api_url):
        """Test str/repr has URL."""
        creds = {"key": "bad", "secret": "bad"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        with pytest.raises(axonius_api_client.exceptions.InvalidCredentials):
            axonius_api_client.auth.AuthKey(http_client=http_client, **creds)
