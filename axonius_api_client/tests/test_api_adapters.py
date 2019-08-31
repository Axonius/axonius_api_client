# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi

from . import need_creds

tools = axonapi.tools


@pytest.mark.needs_url
@pytest.mark.needs_any_creds
@pytest.mark.parametrize(
    "creds", ["creds_user", "creds_key"], indirect=True, scope="class"
)
class TestAdapters(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)

        http = axonapi.Http(url=url, certwarn=False)

        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()

        api = axonapi.api.Adapters(auth=auth)

        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)

        assert isinstance(api.clients, axonapi.api.mixins.Child)
        assert isinstance(api.clients, axonapi.api.adapters.Clients)
        assert api.clients.__class__.__name__ in format(api.clients)
        assert api.clients.__class__.__name__ in repr(api.clients)

        assert isinstance(api._router, axonapi.api.routers.Router)

        return api

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert tools.is_type.dict(data)
