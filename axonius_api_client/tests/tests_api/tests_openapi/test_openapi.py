# -*- coding: utf-8 -*-
"""Test suite."""


def validate_openapi_spec(data):
    assert isinstance(data, str) and data

    split = data.splitlines()
    searches = ["openapi", "info", "components", "paths"]
    for search in searches:
        check = f"{search}:"
        found = any([x.startswith(f"{check}") for x in split])
        assert found, f"{check!r} not found"


class OpenAPIBase:
    pass


class TestOpenAPIPrivate(OpenAPIBase):
    def test_get_spec(self, api_client):
        data = api_client.openapi._get_spec()
        validate_openapi_spec(data=data)


class TestOpenAPIPublic(OpenAPIBase):
    def test_get_spec(self, api_client):
        data = api_client.openapi.get_spec()
        validate_openapi_spec(data=data)
