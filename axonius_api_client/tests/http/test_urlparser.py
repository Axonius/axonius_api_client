# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
import axonius_api_client


class TestUrlParser(object):
    """Test axonius_api_client.http.urlparser.UrlParser."""

    def test_schemehostport443(self):
        """Test a proper URL gets parsed the same."""
        u = axonius_api_client.http.urlparser.UrlParser("https://host:443/blah")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"
        assert u.parsed.path == "/blah"
        assert u.url_full == "https://host:443/blah"
        assert u.url == "https://host:443"

    def test_str_repr(self):
        """Test str/repr has URL path."""
        u = axonius_api_client.http.urlparser.UrlParser("https://host:443/blah")
        assert u.parsed.path in format(u)
        assert u.parsed.path in repr(u)

    def test_schemehost_noport443(self):
        """Test port gets added for https scheme."""
        u = axonius_api_client.http.urlparser.UrlParser("https://host")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_host_noschemeport(self):
        """Test exc when no port or scheme in URL."""
        exc = axonius_api_client.http.exceptions.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonius_api_client.http.urlparser.UrlParser("host", default_scheme="")

    def test_unknownschemehost_noport(self):
        """Test exc when no port and non http/https scheme."""
        exc = axonius_api_client.http.exceptions.HttpError
        match = "no.*'port'"
        with pytest.raises(exc, match=match):
            axonius_api_client.http.urlparser.UrlParser("httpx://host")

    def test_hostport443_withslash(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonius_api_client.http.urlparser.UrlParser("host:443/")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport443_noscheme(self):
        """Test scheme added with port 443 and no scheme in URL."""
        u = axonius_api_client.http.urlparser.UrlParser("host:443", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 443
        assert u.scheme == "https"

    def test_hostport80_noscheme(self):
        """Test scheme added with port 80 and no scheme in URL."""
        u = axonius_api_client.http.urlparser.UrlParser("host:80", default_scheme="")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"

    def test_schemehost_noport80(self):
        """Test port added with no port and http scheme in URL."""
        u = axonius_api_client.http.urlparser.UrlParser("http://host")
        assert u.hostname == "host"
        assert u.port == 80
        assert u.scheme == "http"
