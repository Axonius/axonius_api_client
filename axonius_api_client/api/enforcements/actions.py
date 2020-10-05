# -*- coding: utf-8 -*-
"""API for running actions."""
from typing import List, Optional

from ..mixins import ModelMixins
from ..routers import API_VERSION, Router


class RunAction(ModelMixins):  # pragma: no cover
    """API for running actions.

    Notes:
        Future versions of API client 4.x branch will be expanded quite a bit to make it user
        friendly. The current incarnation should be considered **BETA** until such time.

    """

    @property
    def router(self) -> Router:  # pragma: no cover
        """Router for this API model."""
        return API_VERSION.actions

    def _get(self) -> List[str]:  # pragma: no cover
        """Direct API method to get all actions."""
        path = self.router.root
        return self.request(method="get", path=path)

    def _deploy(
        self,
        action_name: str,
        ids: List[str],
        file_uuid: str,
        file_name: str,
        params: Optional[str] = None,
    ) -> dict:  # pragma: no cover
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

    def _shell(self, action_name: str, ids: List[str], command: str) -> dict:  # pragma: no cover
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
        content: str,
        content_type: Optional[str] = None,
        headers: Optional[dict] = None,
    ) -> str:  # pragma: no cover
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
