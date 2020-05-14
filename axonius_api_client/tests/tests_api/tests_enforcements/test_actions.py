# -*- coding: utf-8 -*-
"""Test suite for axonapi.api.enforcements."""
import pytest

from ...meta import (
    DEPLOY_ACTION_NAME,
    DEPLOY_FILE_CONTENTS,
    DEPLOY_FILE_NAME,
    LINUX_QUERY,
    SHELL_ACTION_CMD,
    SHELL_ACTION_NAME,
)


class TestRunActionBase:
    """Pass."""

    @pytest.fixture(scope="class")
    def apiobj(self, api_run_action):
        """Pass."""
        return api_run_action


class TestRunActionPrivate(TestRunActionBase):
    """Pass."""

    def test_private_get(self, apiobj):
        """Pass."""
        data = apiobj._get()
        for i in ["deploy", "shell", "upload_file"]:
            assert i in data

    # this returns nothing...
    # AND no action shows up in GUI for dvc
    # AND no task shows up in EC
    # BUT: Extended Data Tab shows stuff, but i dont know how to query for that yet
    def test_private_shell(self, apiobj, api_devices):
        """Pass."""
        devices = api_devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]

        if not ids:
            pytest.skip("No linux devices found!")

        data = apiobj._shell(
            action_name=SHELL_ACTION_NAME, ids=ids, command=SHELL_ACTION_CMD,
        )
        assert not data

    @pytest.fixture(scope="class")
    def uploaded_file(self, apiobj):
        """Pass."""
        data = apiobj._upload_file(name=DEPLOY_FILE_NAME, content=DEPLOY_FILE_CONTENTS)
        assert isinstance(data, dict)
        assert isinstance(data["uuid"], str)
        assert data["filename"] == DEPLOY_FILE_NAME
        return data

    # returns nadda
    def test_private_upload_deploy(self, apiobj, api_devices, uploaded_file):
        """Pass."""
        devices = api_devices._get(query=LINUX_QUERY, page_size=1, row_start=0)
        ids = [x["internal_axon_id"] for x in devices["assets"]]

        if not ids:
            reason = "No linux devices found!"
            pytest.skip(reason)

        data = apiobj._deploy(
            action_name=DEPLOY_ACTION_NAME,
            ids=ids,
            file_uuid=uploaded_file["uuid"],
            file_name=uploaded_file["filename"],
            params=None,
        )
        assert not data
