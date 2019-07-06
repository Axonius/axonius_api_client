# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import axonius_api_client


class TestAuthUser(object):
    """Test axonius_api_client.auth.AuthUser."""

    def test_valid_creds(self, api_url, creds_user):
        """Test str/repr has URL."""
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = axonius_api_client.auth.AuthUser(http_client=http_client, **creds_user)
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_invalid_creds(self, api_url):
        """Test str/repr has URL."""
        creds_user = {"username": "bad", "password": "bad"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        with pytest.raises(axonius_api_client.exceptions.InvalidCredentials):
            axonius_api_client.auth.AuthUser(http_client=http_client, **creds_user)


class TestAuthKey(object):
    """Test axonius_api_client.auth.AuthKey."""

    def test_valid_creds(self, api_url, creds_key):
        """Test str/repr has URL."""
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        auth = axonius_api_client.auth.AuthKey(http_client=http_client, **creds_key)
        assert "url" in format(auth)
        assert "url" in repr(auth)

    def test_invalid_creds(self, api_url):
        """Test str/repr has URL."""
        creds_key = {"key": "bad", "secret": "bad"}
        http_client = axonius_api_client.http.HttpClient(url=api_url)
        with pytest.raises(axonius_api_client.exceptions.InvalidCredentials):
            axonius_api_client.auth.AuthKey(http_client=http_client, **creds_key)
