# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import axonius_api_client


class TestUrlJoin(object):
    """Test axonius_api_client.tools.urljoin."""

    def test_urljoin_url(self):
        """Test url gets joined properly no matter the slashes."""
        r = axonius_api_client.tools.urljoin("https://test.com")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com/")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com////")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com", "")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com", "", "")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com", "/", "")
        assert r == "https://test.com/"
        r = axonius_api_client.tools.urljoin("https://test.com", "/", "/")
        assert r == "https://test.com/"

    def test_urljoin_url_path(self):
        """Test url, path gets joined properly no matter the slashes."""
        r = axonius_api_client.tools.urljoin("https://test.com", "a")
        assert r == "https://test.com/a"
        r = axonius_api_client.tools.urljoin("https://test.com", "/a")
        assert r == "https://test.com/a"
        r = axonius_api_client.tools.urljoin("https://test.com", "//a")
        assert r == "https://test.com/a"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/")
        assert r == "https://test.com/a/"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/b")
        assert r == "https://test.com/a/b"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/b", "")
        assert r == "https://test.com/a/b"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/b/", "")
        assert r == "https://test.com/a/b/"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/b", "/")
        assert r == "https://test.com/a/b/"
        r = axonius_api_client.tools.urljoin("https://test.com", "a/b", "/////")
        assert r == "https://test.com/a/b/"

    def test_urljoin_url_path_route(self):
        """Test url, path, route gets joined properly no matter the slashes."""
        r = axonius_api_client.tools.urljoin("https://test.com", "a", "b")
        assert r == "https://test.com/a/b"
        r = axonius_api_client.tools.urljoin("https://test.com", "/a", "b")
        assert r == "https://test.com/a/b"
        r = axonius_api_client.tools.urljoin("https://test.com", "//a", "b")
        assert r == "https://test.com/a/b"
        r = axonius_api_client.tools.urljoin("https://test.com", "a", "b/c/d")
        assert r == "https://test.com/a/b/c/d"
