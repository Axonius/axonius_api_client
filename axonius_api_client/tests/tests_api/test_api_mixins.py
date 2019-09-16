# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import requests

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools

from .. import utils


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    api = axonapi.api.mixins.Mixins(auth=auth)
    api._router = axonapi.api.routers.ApiV1.devices

    utils.check_apiobj(authobj=auth, apiobj=api)

    return api


class MockParser(axonapi.api.mixins.Parser):
    """Pass."""

    def parse(self):
        """Pass."""
        return


class TestMixins(object):
    """Pass."""

    def test_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=True,
            error_status=True,
        )
        assert isinstance(response, dict)

    def test_raw(self, apiobj):
        """Test that response is returned when raw=True."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=True,
            is_json=True,
            error_status=True,
        )
        assert isinstance(response, requests.Response)

    def test_text(self, apiobj):
        """Test that str is returned when raw=False and is_json=False."""
        response = apiobj._request(
            path=apiobj._router.fields,
            method="get",
            raw=False,
            is_json=False,
            error_status=True,
        )
        assert isinstance(response, tools.STR)

    def test_json_error(self, apiobj):
        """Test exc thrown when json has error status."""
        with pytest.raises(exceptions.JsonError):
            apiobj._request(
                path=apiobj._router.root + "/badwolf", method="get", error_status=False
            )

    def test_no_json_error(self, apiobj):
        """Test exc thrown when status code != 200."""
        with pytest.raises(exceptions.ResponseNotOk):
            apiobj._request(
                path=apiobj._router.root + "/badwolf",
                method="get",
                error_status=True,
                is_json=False,
            )

    def test_json_invalid(self, apiobj):
        """Test exc thrown when invalid json."""
        with pytest.raises(exceptions.JsonInvalid):
            apiobj._request(path="", method="get")

    def test_json_invalid_text(self, apiobj):
        """Test that str is returned when is_json=True and error_json_invalid=False."""
        response = apiobj._request(path="", method="get", error_json_invalid=False)
        assert isinstance(response, tools.STR)

    def test_child(self, apiobj):
        """Pass."""
        child = axonapi.api.mixins.Child(parent=apiobj)
        assert format(apiobj) in format(child)
        assert repr(apiobj) in repr(child)

    def test_child_parser(self, apiobj):
        """Pass."""
        child = MockParser(parent=apiobj, raw={})
        assert format(apiobj) in format(child)
        assert repr(apiobj) in repr(child)
