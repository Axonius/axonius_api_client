# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest
import requests

import axonius_api_client as axonapi

from . import need_creds

tools = axonapi.tools


@pytest.mark.needs_url
@pytest.mark.needs_key_creds
@pytest.mark.parametrize("creds", ["creds_key"], indirect=True, scope="class")
class TestMixins(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)

        http = axonapi.Http(url=url, certwarn=False)

        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()

        api = axonapi.api.mixins.Mixins(auth=auth)
        api._router = axonapi.api.routers.ApiV1.users

        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)
        return api

    def test__request_json(self, apiobj):
        """Test that JSON is returned when is_json=True."""
        response = apiobj._request(path=apiobj._router.fields, method="get")
        assert tools.is_type.dict(response)

    def test__request_json_error(self, apiobj):
        """Test exc thrown when json has error status."""
        with pytest.raises(axonapi.exceptions.JsonError):
            apiobj._request(
                path=apiobj._router.root + "/badwolf",
                method="get",
                error_code_not_200=False,
            )

    def test__request_no_json_error(self, apiobj):
        """Test exc thrown when status code != 200."""
        with pytest.raises(axonapi.exceptions.ResponseCodeNot200):
            apiobj._request(
                path=apiobj._router.root + "/badwolf",
                method="get",
                error_code_not_200=True,
                is_json=False,
            )

    def test__request_json_invalid(self, apiobj):
        """Test exc thrown when invalid json."""
        with pytest.raises(axonapi.exceptions.JsonInvalid):
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

    def test_not_logged_in(self, url, creds):
        """Test exc thrown when auth method not logged in."""
        need_creds(creds)
        http = axonapi.Http(url=url, certwarn=False)
        auth = creds["cls"](http=http, **creds["creds"])
        with pytest.raises(axonapi.NotLoggedIn):
            axonapi.api.mixins.Mixins(auth=auth)

    def test__check_max_page_size(self, apiobj):
        """Pass."""
        page_size = axonapi.constants.MAX_PAGE_SIZE + 1000
        with pytest.raises(axonapi.exceptions.ApiError):
            apiobj._check_max_page_size(page_size)
