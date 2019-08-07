# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import routers
from .. import models

# FUTURE: needs tests


class Adapters(models.ApiModel):
    """Adapter related API methods.

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
        return routers.ApiV1.adapters

    def _get(self):
        """Get all adapters.

        Returns:
            :obj:`dict`

        """
        return self._request(method="get", path=self._router.root)

    def get(self, node_name=None):
        """Get all adapters.

        Returns:
            :obj:`object`

        """
        # raw = self._get()
        # ret = {}
        """
        {
            "master": {
                "id": adapter_instance["node_id"],
                "name": "Master",

                # parse adapter_instance["config"]["AdapterBase"]
                    # merge "config" and "schema"
                "adapter_settings": {},

                # parse adapter_instance["config"] that != "AdapterBase"
                    # merge "config" and "schema"
                "adapter_config": {},

                # parse adapter_instance["schema"], ]
                "client_"
                "clients": [
                ],
            },
        }
        """  # noqa
        # for adapter_name, adapter_instances in raw:
        #     for instance in adapter_instances:
        #         node = {}
        #         if instance["node_name"] not in ret:
        #             nodes[instance["node_name"]] = node
        #         node[adapter_name] = []

    # FUTURE: public method
    def _check_client(self, name, config, node_id):
        """Check connectivity for a client of an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to check client connectivity of.
            config (:obj:`dict`):
                Client configuration.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            :obj:`object`

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id
        path = self._router.clients.format(adapter_name=name)
        return self._request(method="post", path=path, json=data)

    # FUTURE: public method
    def _add_client(self, name, config, node_id):
        """Add a client to an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to add client to.
            config (:obj:`dict`):
                Client configuration.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            :obj:`object`

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        path = self._router.clients.format(adapter_name=name)
        return self._request(method="put", path=path, json=data)

    # FUTURE: public method
    def _delete_client(self, name, id, node_id):
        """Delete a client from an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to delete client from.
            id (:obj:`str`):
                ID of client to remove.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            :obj:`object`

        """
        data = {}
        data["instanceName"] = node_id
        path = self._router.clients.format(adapter_name=name)
        path += "/{id}".format(id=id)
        return self._request(method="delete", path=path, json=data)
