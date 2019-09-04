# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi

from . import need_creds

tools = axonapi.tools
exceptions = axonapi.exceptions

LINUX_QUERY = 'specific_data.data.os.type == "Linux"'
ACTION_NAME = "Touch Axonius File"
ACTION_CMD = "echo 'Touched by axonius' > /home/ubuntu/axonius_file"


@pytest.mark.needs_url
@pytest.mark.needs_key_creds
@pytest.mark.parametrize("creds", ["creds_key"], indirect=True, scope="class")
class TestEnforcements(object):
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, url, creds):
        """Pass."""
        need_creds(creds)

        http = axonapi.Http(url=url, certwarn=False)

        auth = creds["cls"](http=http, **creds["creds"])
        auth.login()

        with pytest.warns(exceptions.ApiWarning):
            api = axonapi.Enforcements(auth=auth)

        assert format(auth.__class__.__name__) in format(api)
        assert format(auth.__class__.__name__) in repr(api)
        assert http.url in format(api)
        assert http.url in repr(api)

        assert isinstance(api._router, axonapi.api.routers.Router)

        return api

    def test_actions__get(self, apiobj):
        """Pass."""
        data = apiobj.actions._get()
        assert tools.is_type.los(data)
        assert ["deploy", "shell", "upload_file"] == data

    # FUTURE:
    # this returns nothing...
    # AND no action shows up in GUI for dvc
    # AND no task shows up in EC
    def test_actions__shell(self, apiobj):
        """Pass."""
        devices = apiobj.devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]
        data = apiobj.actions._shell(name=ACTION_NAME, ids=ids, command=ACTION_CMD)
        assert not data
