# -*- coding: utf-8 -*-
"""Test suite for axonius_api_client.auth."""
import axonius_api_client as axonapi


def test_api_v1_routers():
    """Test api.routers.ApiV1."""
    api_routes = axonapi.api.routers.ApiV1
    for obj in api_routes.all_objects:
        assert isinstance(obj, axonapi.api.routers.Router)
        assert obj.OBJ_TYPE in format(obj)
        assert obj.OBJ_TYPE in repr(obj)
        for route in obj.ROUTES:
            assert hasattr(obj, route)


def test_api_v4_routers():
    """Test api.routers.ApiV4."""
    api_routes = axonapi.api.routers.ApiV4
    for obj in api_routes.all_objects:
        assert isinstance(obj, axonapi.api.routers.Router)
        assert obj.OBJ_TYPE in format(obj)
        assert obj.OBJ_TYPE in repr(obj)
        for route in obj.ROUTES:
            assert hasattr(obj, route)
