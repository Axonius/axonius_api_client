# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

import axonius_api_client as axonapi

from . import utils

exceptions = axonapi.exceptions

LINUX_QUERY = 'specific_data.data.os.type == "Linux"'
ACTION_NAME = "Touch Axonius File"
ACTION_CMD = "echo 'Touched by axonius' > /home/ubuntu/axonius_file"


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    with pytest.warns(exceptions.BetaWarning):
        api = axonapi.Enforcements(auth=auth)

    utils.check_apiobj(authobj=auth, apiobj=api)

    utils.check_apiobj_xref(
        apiobj=api,
        users=axonapi.api.users_devices.Users,
        devices=axonapi.api.users_devices.Devices,
    )

    return api


class TestEnforcements(object):
    """Pass."""

    def test_actions__get(self, apiobj):
        """Pass."""
        data = apiobj.actions._get()
        assert ["deploy", "shell", "upload_file"] == data

    # FUTURE:
    # this returns nothing...
    # AND no action shows up in GUI for dvc
    # AND no task shows up in EC
    def test_actions__shell(self, apiobj):
        """Pass."""
        devices = apiobj.devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]
        if not ids:
            reason = "No linux devices found!"
            pytest.skip(reason)

        data = apiobj.actions._shell(name=ACTION_NAME, ids=ids, command=ACTION_CMD)
        assert not data
