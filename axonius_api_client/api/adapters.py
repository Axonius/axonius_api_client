# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import routers
from .. import tools, models, exceptions

# FUTURE: needs tests


class Adapters(models.ApiModel):
    """Adapter related API methods."""

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

    def get(
        self,
        names=None,
        node_names=None,
        client_count=None,
        client_ids=None,
        statuses=None,
        features=None,
        only_broken_clients=False,
        only_working_clients=False,
        only_has_clients=False,
        only_no_clients=False,
        parse_obj=False,
        error=True,
    ):
        """Get all adapters."""
        raw = self._get()
        parser = Parser(raw=raw)

        if parse_obj:
            return parser

        adapters = parser.parse()

        if only_broken_clients:
            adapters = parser.find_by_broken_clients(adapters=adapters)

        if only_working_clients:
            adapters = parser.find_by_working_clients(adapters=adapters)

        if only_has_clients:
            adapters = parser.find_by_has_clients(adapters=adapters)

        if only_no_clients:
            adapters = parser.find_by_no_clients(adapters=adapters)

        if names is not None:
            adapters = parser.find_by_names(
                values=names, adapters=adapters, error=error
            )
        if node_names is not None:
            adapters = parser.find_by_node_names(
                values=node_names, adapters=adapters, error=error
            )
        if statuses is not None:
            adapters = parser.find_by_statuses(
                values=statuses, adapters=adapters, error=error
            )
        if features is not None:
            adapters = parser.find_by_features(
                values=features, adapters=adapters, error=error
            )
        if client_ids is not None:
            adapters = parser.find_by_client_ids(
                values=client_ids, adapters=adapters, error=error
            )
        if client_count is not None:
            adapters = parser.find_by_client_count(
                value=client_count, adapters=adapters, error=error
            )
        return adapters

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


class Parser(object):
    """Pass."""

    _NOTSET = "NOTSET"
    _RAW_SECRET = ["unchanged"]
    _SECRET = "HIDDEN"

    def __init__(self, raw):
        """Pass."""
        self._raw = raw

    def parse(self):
        """Pass."""
        parsed = []

        for adapter_name, raw_adapters in self._raw.items():
            for raw_adapter in raw_adapters:
                parsed.append(
                    self._parse_adapter(
                        adapter_name=adapter_name, raw_adapter=raw_adapter
                    )
                )

        return parsed

    def _parse_adapter(self, adapter_name, raw_adapter):
        """Pass."""
        parsed = {
            "name": tools.rstrip(adapter_name, "_adapter"),
            "name_raw": adapter_name,
            "name_plugin": raw_adapter["unique_plugin_name"],
            "node_name": raw_adapter["node_name"],
            "node_id": raw_adapter["node_id"],
            "status": raw_adapter["status"],
            "features": raw_adapter["supported_features"],
        }

        parsed["clients"] = self._clients(raw_adapter=raw_adapter, parent=dict(parsed))
        parsed["settings_clients"] = self._settings_clients(raw_adapter=raw_adapter)
        parsed["settings_adapter"] = self._settings_adapter(raw_adapter=raw_adapter)
        return parsed

    def _settings_clients(self, raw_adapter):
        """Pass."""
        settings = {}

        schema = raw_adapter["schema"]
        items = schema["items"]
        required = schema["required"]

        for item in items:
            setting_name = item["name"]
            settings[setting_name] = {k: v for k, v in item.items()}
            settings[setting_name]["required"] = setting_name in required

        return settings

    def _settings_adapter(self, raw_adapter):
        """Pass."""
        adv_settings = {"base": {}, "custom": {}}

        for raw_name, raw_settings in raw_adapter["config"].items():
            settings = {}

            schema = raw_settings["schema"]
            items = schema["items"]
            required = schema["required"]

            for item in items:
                setting_name = item["name"]
                parsed_settings = {k: v for k, v in item.items()}
                parsed_settings["required"] = setting_name in required
                settings[setting_name] = parsed_settings

            wrap_settings = {
                "settings": settings,
                "meta": {"name_raw": raw_name, "name_pretty": schema["pretty_name"]},
            }

            if raw_name == "AdapterBase":
                adv_settings["base"] = wrap_settings
            else:
                adv_settings["custom"] = wrap_settings
        return adv_settings

    def _clients(self, raw_adapter, parent):
        """Pass."""
        clients = []

        settings_client = self._settings_clients(raw_adapter=raw_adapter)

        for raw_client in raw_adapter["clients"]:
            raw_config = raw_client["client_config"]
            parsed_config = {}

            for setting_name, setting_config in settings_client.items():
                value = raw_config.get(setting_name, self._NOTSET)
                value = self._SECRET if value == self._RAW_SECRET else value
                parsed_config[setting_name] = setting_config
                parsed_config[setting_name]["value"] = value

            parsed_client = {
                k: v for k, v in raw_client.items() if k != "client_config"
            }
            parsed_client["parent_adapter"] = parent
            parsed_client["config"] = parsed_config
            clients.append(parsed_client)
        return clients

    def find_by_names(self, values, adapters=None, error=True):
        """Pass."""
        if not isinstance(values, (tuple, list)):
            values = [values]
        values = [tools.rstrip(name, "_adapter").lower() for name in values]
        adapters = adapters or self.parse()

        matches = []
        known = []

        for adapter in adapters:

            if adapter["name"] not in known:
                known.append(adapter["name"])

            if adapter["name"].lower() in values:
                matches.append(adapter)

        matches = [x for x in adapters if x["name"] in values]

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by names",
                valid_msg="names",
            )
        return matches

    def find_by_node_names(self, values, adapters=None, error=True):
        """Pass."""
        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]
        adapters = adapters or self.parse()
        matches = []
        known = []

        for adapter in adapters:
            if adapter["node_name"] not in known:
                known.append(adapter["node_name"])
            if adapter["node_name"].lower() in values:
                matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by node names",
                valid_msg="node names",
            )
        return matches

    def find_by_features(self, values, adapters=None, error=True):
        """Pass."""
        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]
        adapters = adapters or self.parse()
        matches = []
        known = []
        for adapter in adapters:
            for feature in adapter["features"]:
                if feature not in known:
                    known.append(feature)
                if feature.lower() in values:
                    matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by features",
                valid_msg="features",
            )
        return matches

    def find_by_statuses(self, values, adapters=None, error=True):
        """Pass."""
        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]
        adapters = adapters or self.parse()
        matches = []
        known = []
        for adapter in adapters:
            if adapter["status"] not in known:
                known.append(adapter["status"])
            if adapter["status"].lower() in values:
                matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by statuses",
                valid_msg="statuses",
            )
        return matches

    def find_by_broken_clients(self, adapters=None):
        """Pass."""
        values = ["", "success"]
        adapters = adapters or self.parse()
        matches = []
        for adapter in adapters:
            if adapter["status"].lower() not in values:
                matches.append(adapter)
        return matches

    def find_by_working_clients(self, adapters=None):
        """Pass."""
        values = ["success"]
        adapters = adapters or self.parse()
        matches = []
        for adapter in adapters:
            if adapter["status"].lower() in values:
                matches.append(adapter)
        return matches

    def find_by_has_clients(self, adapters=None):
        """Pass."""
        adapters = adapters or self.parse()
        matches = []
        for adapter in adapters:
            if adapter["clients"]:
                matches.append(adapter)
        return matches

    def find_by_no_clients(self, adapters=None):
        """Pass."""
        adapters = adapters or self.parse()
        matches = []
        for adapter in adapters:
            if not adapter["clients"]:
                matches.append(adapter)
        return matches

    def find_by_client_count(self, value, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()
        matches = []
        known = []
        for adapter in adapters:
            client_count = len(adapter["clients"])
            if format(client_count) not in known:
                known.append(format(client_count))
            if client_count == value:
                matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=value,
                known=known,
                reason_msg="adapter by client count",
                valid_msg="client counts",
            )
        return matches

    def find_by_client_ids(self, values, adapters=None, error=True):
        """Pass."""
        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]
        adapters = adapters or self.parse()
        matches = []
        known = []
        for adapter in adapters:
            for client in adapter["clients"]:
                if client["client_id"] not in known:
                    known.append(client["client_id"])
                if client["client_id"].lower() in values:
                    matches.append(adapter)
        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by client ID",
                valid_msg="client IDs",
            )
        return matches

    # FUTURE: find by client config key == value
    @property
    def nodes(self):
        """Get list of all nodes."""
        return list(self.parse().keys())

    def __str__(self):
        """Pass."""
        return "Nodes: {n}".format(n=", ".join(self.nodes))

    def __repr__(self):
        """Pass."""
        return self.__str__()
