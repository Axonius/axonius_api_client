# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

import axonius_api_client as axonapi


class TestJoin(object):
    """Test axonius_api_client.tools.join."""

    def test_url(self):
        """Test url gets joined properly no matter the slashes."""
        r = axonapi.tools.join.url("https://test.com")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com/")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com////")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com", "")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com", "", "")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com", "/", "")
        assert r == "https://test.com/"
        r = axonapi.tools.join.url("https://test.com", "/", "/")
        assert r == "https://test.com/"

    def test_url_path(self):
        """Test url, path gets joined properly no matter the slashes."""
        r = axonapi.tools.join.url("https://test.com", "a")
        assert r == "https://test.com/a"
        r = axonapi.tools.join.url("https://test.com", "/a")
        assert r == "https://test.com/a"
        r = axonapi.tools.join.url("https://test.com", "//a")
        assert r == "https://test.com/a"
        r = axonapi.tools.join.url("https://test.com", "a/")
        assert r == "https://test.com/a/"
        r = axonapi.tools.join.url("https://test.com", "a/b")
        assert r == "https://test.com/a/b"
        r = axonapi.tools.join.url("https://test.com", "a/b", "")
        assert r == "https://test.com/a/b"
        r = axonapi.tools.join.url("https://test.com", "a/b/", "")
        assert r == "https://test.com/a/b/"
        r = axonapi.tools.join.url("https://test.com", "a/b", "/")
        assert r == "https://test.com/a/b/"
        r = axonapi.tools.join.url("https://test.com", "a/b", "/////")
        assert r == "https://test.com/a/b/"

    def test_url_path_route(self):
        """Test url, path, route gets joined properly no matter the slashes."""
        r = axonapi.tools.join.url("https://test.com", "a", "b")
        assert r == "https://test.com/a/b"
        r = axonapi.tools.join.url("https://test.com", "/a", "b")
        assert r == "https://test.com/a/b"
        r = axonapi.tools.join.url("https://test.com", "//a", "b")
        assert r == "https://test.com/a/b"
        r = axonapi.tools.join.url("https://test.com", "a", "b/c/d")
        assert r == "https://test.com/a/b/c/d"
