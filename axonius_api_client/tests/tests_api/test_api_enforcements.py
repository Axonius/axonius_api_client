# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.users_devices."""
from __future__ import absolute_import, division, print_function, unicode_literals

import warnings

import pytest

import axonius_api_client as axonapi
from axonius_api_client import exceptions, tools

from .. import utils

LINUX_QUERY = 'specific_data.data.os.type == "Linux"'
SHELL_ACTION_NAME = "Badwolf Shell Action"
SHELL_ACTION_CMD = "echo 'Badwolf' > /tmp/badwolf.txt"
DEPLOY_ACTION_NAME = "Badwolf Deploy Action"
DEPLOY_FILE_NAME = "badwolf.sh"
DEPLOY_FILE_CONTENTS = b"#!/bin/bash\necho badwolf!"

CREATE_EC_NAME = "Badwolf EC Example"
CREATE_EC_TRIGGERS = [
    {
        "name": "Trigger",
        "view": {
            "name": "Users Created in Last 30 Days",
            "entity": "users",
        },  # FUTURE: public create will need to get sq!
        "conditions": {
            "new_entities": False,
            "previous_entities": False,
            "above": 1,
            "below": 0,
        },  # FUTURE: need public build_trigger method
        "period": "never",
        "run_on": "AllEntities",
    }
]
CREATE_EC_ACTION_MAIN = {
    "name": "Badwolf Create Notification",
    "action": {"action_name": "create_notification", "config": {}},
}


@pytest.fixture(scope="module")
def apiobj(request):
    """Pass."""
    auth = utils.get_auth(request)

    with pytest.warns(exceptions.BetaWarning):
        api = axonapi.Enforcements(auth=auth)

    utils.check_apiobj(authobj=auth, apiobj=api)

    utils.check_apiobj_children(
        apiobj=api, runaction=axonapi.api.enforcements.RunAction
    )

    utils.check_apiobj_xref(
        apiobj=api,
        users=axonapi.api.users_devices.Users,
        devices=axonapi.api.users_devices.Devices,
    )

    return api


class TestEnforcements(object):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        assert isinstance(data, dict)

        assets = data["assets"]
        assert isinstance(assets, tools.LIST)

        for asset in assets:
            assert isinstance(asset, dict)

    def test_get(self, apiobj):
        """Pass."""
        data = apiobj.get()
        assert isinstance(data, list)
        for found in data:
            assert isinstance(found["uuid"], tools.STR)
            assert isinstance(found["actions.main"], tools.STR)
            assert isinstance(found["name"], tools.STR)
            assert isinstance(found["date_fetched"], tools.STR)
            assert isinstance(found["last_updated"], tools.STR)
            assert "triggers.last_triggered" in found
            assert "triggers.times_triggered" in found

    def test_get_maxpages(self, apiobj):
        """Pass."""
        found = apiobj.get(max_pages=1, page_size=1)
        assert isinstance(found, list)
        # we can't test for length if there are no enforcements...
        # assert len(found) == 1

    def test_create_get_delete(self, apiobj):
        """Pass."""
        old_found = apiobj.get_by_name(CREATE_EC_NAME, eq_single=False)
        if old_found:
            msg = "Enforcement named {} already exists from previous test, deleting: {}"
            msg = msg.format(CREATE_EC_NAME, old_found)
            warnings.warn(msg)
            deleted = apiobj.delete(rows=old_found)
            assert isinstance(deleted, dict)
            assert isinstance(deleted["deleted"], tools.INT)
            assert deleted["deleted"] == 1

        created = apiobj._create(
            name=CREATE_EC_NAME, main=CREATE_EC_ACTION_MAIN, triggers=CREATE_EC_TRIGGERS
        )
        assert isinstance(created, tools.STR)

        found = apiobj.get_by_name(CREATE_EC_NAME)
        """
        {
            "actions.main": "Badwolf Create Notification",
            "date_fetched": "2019-09-10 23:17:07+00:00",
            "last_updated": "Tue, 10 Sep 2019 23:17:07 GMT",
            "name": "Badwolf EC Example",
            "triggers.last_triggered": null,
            "triggers.times_triggered": 0,
            "triggers.view.name": "Users Created in Last 30 Days",
            "uuid": "5d782ef380ded0001bbe3c47"
        }
        """
        assert isinstance(found, dict)
        assert found["uuid"] == created
        assert found["actions.main"] == CREATE_EC_ACTION_MAIN["name"]
        assert found["name"] == CREATE_EC_NAME
        assert isinstance(found["date_fetched"], tools.STR)
        assert isinstance(found["last_updated"], tools.STR)
        assert "triggers.last_triggered" in found
        assert "triggers.times_triggered" in found
        assert found["triggers.view.name"] == CREATE_EC_TRIGGERS[0]["view"]["name"]

        found_by_id = apiobj.get_by_id(found["uuid"])
        assert isinstance(found_by_id, dict)

        deleted = apiobj.delete(rows=found_by_id)
        assert isinstance(deleted, dict)
        assert isinstance(deleted["deleted"], tools.INT)
        assert deleted["deleted"] == 1

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_id(found["uuid"])

        with pytest.raises(exceptions.ValueNotFound):
            apiobj.get_by_name(found["name"])

        notfound = apiobj.get_by_id(found["uuid"], match_error=False)
        assert notfound is None

        notmatches = apiobj.get_by_name(value=found["name"], value_not=True)
        assert not any([x["name"] == found["name"] for x in notmatches])

        allobjs = apiobj.get()
        if allobjs:
            name = allobjs[0]["name"]
            rematches = apiobj.get_by_name(value=name[0], value_regex=True)
            assert any([x["name"] == name for x in rematches])


class TestRunActions(object):
    """Pass."""

    def test__get(self, apiobj):
        """Pass."""
        data = apiobj.runaction._get()
        for i in ["deploy", "shell", "upload_file"]:
            assert i in data

    # FUTURE:
    # this returns nothing...
    # AND no action shows up in GUI for dvc
    # AND no task shows up in EC
    # BUT: Extended Data Tab shows stuff, but i dont know how to query for that yet
    def test__shell(self, apiobj):
        """Pass."""
        devices = apiobj.devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]

        if not ids:
            reason = "No linux devices found!"
            pytest.skip(reason)

        data = apiobj.runaction._shell(
            action_name=SHELL_ACTION_NAME, ids=ids, command=SHELL_ACTION_CMD
        )
        assert not data

    @pytest.fixture(scope="class")
    def uploaded_file(self, apiobj):
        """Pass."""
        data = apiobj.runaction._upload_file(
            name=DEPLOY_FILE_NAME, content=DEPLOY_FILE_CONTENTS
        )
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], tools.STR)
        assert data["filename"] == DEPLOY_FILE_NAME
        return data

    # FUTURE: returns nadda
    def test__upload_deploy(self, apiobj, uploaded_file):
        """Pass."""
        devices = apiobj.devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]

        if not ids:
            reason = "No linux devices found!"
            pytest.skip(reason)

        data = apiobj.runaction._deploy(
            action_name=DEPLOY_ACTION_NAME,
            ids=ids,
            file_uuid=uploaded_file["uuid"],
            file_name=uploaded_file["filename"],
            params=None,
        )
        assert not data
