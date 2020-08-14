# -*- coding: utf-8 -*-
"""API model for working with system configuration."""
from ..mixins import ChildMixins, Model


class Nodes(ChildMixins):
    """Child API model for working with instances."""

    def get(self) -> dict:
        """Get instances.

        Returns:
            :obj:`dict`: instances
        """
        return self._get()["instances"]

    # XXX add get_by_name, get_core, get_collectors

    def _init(self, parent: Model):
        """Post init method for subclasses to use for extra setup.

        Args:
            parent (:obj:`.api.mixins.Model`): parent API model of this child
        """
        super(Nodes, self)._init(parent=parent)

    def _get(self) -> dict:
        """Direct API method to get instances.

        Returns:
            :obj:`dict`: instances
        """
        """Example return
        {
            "connection_data": {
                "host": "<axonius-hostname>",
                "key": "QV2bu53oV3HMGugMOvgNSa1B5dNCDCY0"
            },
            "instances": [
                {
                    "hostname": "builds-vm-jim-2-15-b-1581114965-000",
                    "ips": [
                        "10.20.0.100"
                    ],
                    "last_seen": "Sun, 09 Feb 2020 22:19:22 GMT",
                    "node_id": "a7afe3af5d05428dbecc55704fc7e3ea",
                    "node_name": "Master",
                    "node_user_password": "",
                    "status": "Activated",
                    "tags": {}
                }
            ]
        }
        """
        return self.request(method="get", path=self.router.instances)

    def _delete(self, node_id: str):  # pragma: no cover
        """Pass."""
        data = {"nodeIds": node_id}
        path = self.router.instances
        return self.request(method="delete", path=path, json=data)

    def _update(
        self, node_id: str, node_name: str, hostname: str
    ) -> dict:  # pragma: no cover
        """Direct API method to update an instance.

        Args:
            node_id (:obj:`str`): node id of instance
            node_name (:obj:`str`): node name of instance
            hostname (:obj:`str`): hostname of instance

        Returns:
            :obj:`dict`: updated instance
        """
        """Example return

        {
            "nodeIds": "a7afe3af5d05428dbecc55704fc7e3ea",
            "node_name": "Masterx",
            "hostname": "builds-vm-jim-2-15-b-1581114965-000"
        }
        """
        data = {"nodeIds": node_id, "node_name": node_name, "hostname": hostname}
        path = self.router.instances
        return self.request(method="post", path=path, json=data)
