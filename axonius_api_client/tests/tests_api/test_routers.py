# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
import axonius_api_client as axonapi


def test_api_v1_routers():
    """Test api.routers.ApiV1."""
    api_routes = axonapi.api.routers.ApiV1
    for obj in api_routes.all_objects:
        assert isinstance(obj, axonapi.api.routers.Router)
        assert obj._object_type in format(obj)
        assert obj._object_type in repr(obj)
        for route in obj._routes:
            assert hasattr(obj, route)
