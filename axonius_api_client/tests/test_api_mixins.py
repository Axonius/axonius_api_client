# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import requests

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools
from . import utils


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    api = axonapi.api.mixins.Mixins(auth=auth)
    api._router = axonapi.api.routers.ApiV1.devices

    utils.check_apiobj(authobj=auth, apiobj=api)

    return api


class TestMixins(object):
    """Pass."""

    def test__request_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj._request(path=apiobj._router.fields, method="get")
        assert tools.is_type.dict(response)

    def test__request_json_error(self, apiobj):
        """Test exc thrown when json has error status."""
        with pytest.raises(exceptions.JsonError):
            apiobj._request(
                path=apiobj._router.root + "/badwolf",
                method="get",
                error_code_not_200=False,
            )

    def test__request_no_json_error(self, apiobj):
        """Test exc thrown when status code != 200."""
        with pytest.raises(exceptions.ResponseCodeNot200):
            apiobj._request(
                path=apiobj._router.root + "/badwolf",
                method="get",
                error_code_not_200=True,
                is_json=False,
            )

    def test__request_json_invalid(self, apiobj):
        """Test exc thrown when invalid json."""
        with pytest.raises(exceptions.JsonInvalid):
            apiobj._request(path="", method="get")

    def test__request_json_invalid_text(self, apiobj):
        """Test that str is returned when is_json=True and error_json_invalid=False."""
        response = apiobj._request(path="", method="get", error_json_invalid=False)
        assert tools.is_type.str(response)

    def test__request_raw(self, apiobj):
        """Test that response is returned when raw=True."""
        response = apiobj._request(path=apiobj._router.fields, method="get", raw=True)
        assert isinstance(response, requests.Response)

    def test__request_text(self, apiobj):
        """Test that str is returned when raw=False and is_json=False."""
        response = apiobj._request(
            path=apiobj._router.fields, method="get", is_json=False
        )
        assert tools.is_type.str(response)
