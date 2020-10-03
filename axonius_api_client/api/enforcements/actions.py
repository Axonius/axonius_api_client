# -*- coding: utf-8 -*-
"""API for running actions."""
from typing import IO, List, Optional

from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class RunAction(ModelMixins):
    """Child API model for working with actions.

    Notes:
        The REST API will need to be updated to allow more power in this library.
        Until then, this class should be considered **BETA**.
    """

    @property
    def router(self) -> Router:
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return API_VERSION.actions

    # sort of pointless
    def _get(self) -> List[str]:
        """Direct API method to get all actions.

        Returns:
            :obj:`list` of :obj:`str`: all actions known to system
        """
        path = self.router.root
        return self.request(method="get", path=path)

    def _deploy(
        self,
        action_name: str,
        ids: List[str],
        file_uuid: str,
        file_name: str,
        params: Optional[str] = None,
    ) -> dict:
        """Deploy an action.

        Args:
            name: name of action to deploy
            ids: internal_axon_ids of devices to process
            uuid: UUID of binary to use in deployment
            filename: filename of binary to use in deployment
            params: parameters to pass to action
        """
        data = {}
        data["action_name"] = action_name
        data["internal_axon_ids"] = ids
        data["binary"] = {}
        data["binary"]["filename"] = file_name
        data["binary"]["uuid"] = file_uuid
        data["params"] = params

        path = self.router.deploy

        return self.request(method="post", path=path, json=data)

    def _shell(self, action_name: str, ids: List[str], command: str) -> dict:
        """Run an action.

        Args:
            action_name: name of action to run
            ids: internal_axon_ids of devices to process
            command: command to run
        """
        data = {}
        data["action_name"] = action_name
        data["internal_axon_ids"] = ids
        data["command"] = command

        path = self.router.shell
        return self.request(method="post", path=path, json=data)

    def _upload_file(
        self,
        name: str,
        content: IO,
        content_type: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> str:
        """Upload a file to the system for use in deployment and get the UUID of new file.

        Args:
            binary: binary bits of file to upload
            filename: name of file to upload
        """
        data = {"field_name": "binary"}
        files = {"userfile": (name, content, content_type, headers)}
        path = API_VERSION.alerts.upload_file

        ret = self.request(method="post", path=path, data=data, files=files)
        ret["filename"] = name
        return ret
