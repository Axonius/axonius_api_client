# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# import pytest

import axonius_api_client


class TestApiClient(object):
    """Test axonius_api_client.api.ApiClient."""

    def test_str_repr(self, auth_objs):
        """Test str/repr has URL."""
        for auth_obj in auth_objs:
            api_client = axonius_api_client.api.ApiClient(auth=auth_obj)
            assert "auth" in format(api_client)
            assert "auth" in repr(api_client)
