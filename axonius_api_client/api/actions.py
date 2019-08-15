# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import routers, mixins


# FUTURE: needs tests
class Actions(mixins.ApiMixins):
    """Action related API methods.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.

    """

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.actions

    def get(self):
        """Get all actions.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._request(method="get", path=self._router.root)

    def run(self, name, ids, command):
        """Run an action.

        Args:
            name (:obj:`str`):
                Name of action to run.
            ids (:obj:`list` of :obj:`str`):
                Internal axonius IDs of device to run action against.
            command (:obj:`str`):
                Command to run.

        Returns:
            :obj:`object`

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["command"] = command
        return self._request(method="post", path=self._router.shell, json=data)

    # FUTURE: Figure out return.
    def deploy(self, name, ids, binary_uuid, binary_filename, params=None):
        """Deploy an action.

        Args:
            name (:obj:`str`):
                Name of action to deploy.
            ids (:obj:`list` of :obj:`str`):
                Internal axonius IDs of device to deploy action against.
            binary_uuid (:obj:`str`):
                UUID of binary to use in deployment.
            binary_filename (:obj:`str`):
                Filename of binary to use in deployment.
            params (:obj:`str`, optional):
                Defaults to: None.

        Returns:
            :obj:`object`

        """
        data = {}
        data["action_name"] = name
        data["internal_axon_ids"] = ids
        data["binary"] = {}
        data["binary"]["filename"] = binary_filename
        data["binary"]["uuid"] = binary_uuid
        if params:
            data["params"] = params
        return self._request(method="post", path=self._router.deploy, json=data)

    def upload_file(self, binary, filename):
        """Upload a file to the system for use in deployment.

        Args:
            binary (:obj:`io.BytesIO`):
                Binary bits of file to upload.
            filename (:obj:`str`):
                Name of file to upload.

        Returns:
            :obj:`str`: UUID of uploaded file.

        """
        data = {}
        data["field_name"] = "binary"
        files = {}
        files["userfile"] = (filename, binary)
        return self._request(
            method="post", path=self._router.upload_file, data=data, files=files
        )
