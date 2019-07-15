# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from axonius_api_client import api


def test_api_v1_routers():
    """Test api.routers.ApiV1."""
    api_routes = api.routers.ApiV1
    for obj in api_routes.all_objects:
        assert isinstance(obj, api.routers.Router)
        assert obj._object_type in format(obj)
        assert obj._object_type in repr(obj)
        for route in obj._routes:
            assert hasattr(obj, route)
