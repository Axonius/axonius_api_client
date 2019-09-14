# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.tools."""
from __future__ import absolute_import, division, print_function, unicode_literals

from axonius_api_client import exceptions, tools

# FUTURE: Test subclassing/strings/etc


class TestKnownCb(object):
    """Test axonius_api_client.tools.join_url."""

    def known_cb_error(self, **kwargs):
        """Pass."""
        raise Exception()

    def known_cb(self, **kwargs):
        """Pass."""
        return list(kwargs)

    def test_known_cb_error(self):
        """Pass."""
        x = exceptions.known_cb(known=self.known_cb_error)
        assert isinstance(x, tools.LIST)
        assert len(x) == 1
        assert "failed with exception" in x[0]
        assert format(self.known_cb_error) in x[0]

    def test_known_cb(self):
        """Pass."""
        x = exceptions.known_cb(known=[1, 2, 3])
        assert x == [1, 2, 3]
