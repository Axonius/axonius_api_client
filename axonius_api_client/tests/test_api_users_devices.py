# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

import requests

# import six

import axonius_api_client as axonapi

methods = [axonapi.api.Users, axonapi.Devices]


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize("creds", ["creds_user", "creds_key"], indirect=True)
@pytest.mark.parametrize("method", methods, scope="session")
class TestUserDevices(object):
    """Pass."""

    @pytest.fixture(scope="session")
    def api_client(self, api_url, method, creds):
        """Pass."""
        if not any(list(creds["creds"].values())):
            pytest.skip("No credentials provided for {cls}: {creds}".format(**creds))

        http = axonapi.Http(url=api_url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()
        api = method(auth=auth)
        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        return api

    def test__request_json(self, api_client):
        """Test that JSON is returned when is_json=True."""
        response = api_client._request(
            path=api_client._router.fields,
            method="get",
            raw=False,
            is_json=True,
            check_status=True,
        )
        assert axonapi.tools.is_type.dict(response)

    def test__request_raw(self, api_client):
        """Test that response is returned when raw=True."""
        response = api_client._request(
            path=api_client._router.fields,
            method="get",
            raw=True,
            is_json=True,
            check_status=True,
        )
        assert isinstance(response, requests.Response)

    def test__request_text(self, api_client):
        """Test that str is returned when raw=False and is_json=False."""
        response = api_client._request(
            path=api_client._router.fields,
            method="get",
            raw=False,
            is_json=False,
            check_status=True,
        )
        assert axonapi.tools.is_type.str(response)

    # test response error by using invalid route
    # test "error" in json response somehow (need to add code for it too)
    # test invalid json response somehow
