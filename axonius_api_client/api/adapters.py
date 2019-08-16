# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re

from . import routers, mixins
from .. import tools, exceptions

# FUTURE: public REST API does not support setting advanced settings
"""
# advanced settings
method=POST
path=/api/plugins/configs/carbonblack_defense_adapter/AdapterBase
body=
{
    "connect_client_timeout": 300,
    "fetching_timeout": 5400,
    "last_fetched_threshold_hours": 49,
    "last_seen_prioritized": false,
    "last_seen_threshold_hours": 43800,
    "minimum_time_until_next_fetch": null,
    "realtime_adapter": false,
    "user_last_fetched_threshold_hours": null,
    "user_last_seen_threshold_hours": null
}
"""

"""
# adapter specific advanced settings
method=POST
path=/api/plugins/configs/carbonblack_defense_adapter/CarbonblackDefenseAdapter
body={"fetch_deregistred":false}
"""

"""
# rule to add to api.py
@api_add_rule('plugins/configs/<plugin_name>/<config_name>', methods=['POST', 'GET'],
    wrap around service.py: plugins_configs_set()
"""


class Adapters(mixins.ApiMixin):
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
        nodes=None,
        features=None,
        client_ids=None,
        client_max=None,
        client_min=None,
        client_bad=False,
        client_ok=False,
        return_parse_obj=False,
        return_clients=True,
        error=True,
        # **client_settings
    ):
        """Get all adapters."""
        raw = self._get()
        parser = Parser(raw=raw, parent=self)

        if return_parse_obj:
            return parser

        adapters = parser.parse()

        adapters = parser.find_by_names(values=names, adapters=adapters, error=error)

        adapters = parser.find_by_nodes(values=nodes, adapters=adapters, error=error)

        adapters = parser.find_by_features(
            values=features, adapters=adapters, error=error
        )

        adapters = parser.find_by_client_ids(
            values=client_ids, adapters=adapters, error=error
        )

        adapters = parser.find_by_client_count(
            client_min=client_min, client_max=client_max, adapters=adapters
        )

        if client_bad:
            adapters = parser.find_by_client_statuses(
                values="error", adapters=adapters, error=False
            )
        elif client_ok:
            adapters = parser.find_by_client_statuses(
                values="success", adapters=adapters, error=False
            )

        if return_clients:
            clients = []
            for adapter in adapters:
                clients += adapter["clients"]
            return clients

        # FUTURE
        # for setting, value in client_settings.items():
        #     adapters = parser.find_by_client_setting(
        #         setting=setting, value=value, adapters=adapters, error=error
        #     )

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

    _NOTSET = "__NOTSET__"
    _RAW_SECRET = ["unchanged"]
    _SECRET = "__HIDDEN__"

    def __init__(self, raw, parent):
        """Pass."""
        self._log = parent._log.getChild(self.__class__.__name__)
        """:obj:`logging.Logger`: Logger for this object."""
        self._parent = parent
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

        msg = "Parsed {n} adapters"
        msg = msg.format(n=len(parsed))
        self._log.debug(msg)

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

        parsed["clients"] = self._clients(raw_adapter=raw_adapter, parent=parsed)
        parsed["settings_clients"] = self._settings_clients(raw_adapter=raw_adapter)
        parsed["settings_adapter"] = self._settings_adapter(
            raw_adapter=raw_adapter, base=False
        )
        parsed["settings_advanced"] = self._settings_adapter(
            raw_adapter=raw_adapter, base=True
        )
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

    def _settings_adapter(self, raw_adapter, base=True):
        """Pass."""
        settings = {}

        for raw_name, raw_settings in raw_adapter["config"].items():
            is_base = raw_name == "AdapterBase"
            if (is_base and not base) or (not is_base and base) or settings:
                continue

            schema = raw_settings["schema"]
            items = schema["items"]
            required = schema["required"]
            config = raw_settings["config"]

            for item in items:
                setting_name = item["name"]
                parsed_settings = {k: v for k, v in item.items()}
                parsed_settings["required"] = setting_name in required
                parsed_settings["value"] = config.get(setting_name, self._NOTSET)
                settings[setting_name] = parsed_settings

        return settings

    def _clients(self, raw_adapter, parent):
        """Pass."""
        clients = []

        settings_client = self._settings_clients(raw_adapter=raw_adapter)

        for raw_client in raw_adapter["clients"]:
            raw_config = raw_client["client_config"]
            parsed_settings = {}

            for setting_name, setting_config in settings_client.items():
                setting_config.pop("name", "")
                value = raw_config.get(setting_name, self._NOTSET)
                value = self._SECRET if value == self._RAW_SECRET else value
                parsed_settings[setting_name] = setting_config
                parsed_settings[setting_name]["value"] = value

            parsed_client = {
                k: v for k, v in raw_client.items() if k != "client_config"
            }
            parsed_client["node_name"] = parent["node_name"]
            parsed_client["node_id"] = parent["node_id"]
            parsed_client["adapter"] = parent["name"]
            parsed_client["adapter_status"] = parent["status"]
            parsed_client["adapter_features"] = parent["features"]
            parsed_client["settings"] = parsed_settings
            clients.append(parsed_client)
        return clients

    def find_by_names(self, values=None, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or values is None:
            return adapters

        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [tools.rstrip(name, "_adapter").lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            check = adapter["name"]

            if check not in known:
                known.append(check)

            for value in values:
                value_re = re.compile(value, re.I)
                if value_re.search(check) and adapter not in matches:
                    msg = "Matched adapter name {a!r} using value {v!r}"
                    msg = msg.format(a=adapter["name"], v=value)
                    self._log.debug(msg)

                    matches.append(adapter)

        if not matches and known and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by names",
                valid_msg="names",
            )

        return matches

    def find_by_nodes(self, values=None, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or values is None:
            return adapters

        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            check = adapter["node_name"]

            if check not in known:
                known.append(check)

            for value in values:
                value_re = re.compile(value, re.I)
                if value_re.search(check) and adapter not in matches:
                    matches.append(adapter)

        if not matches and known and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by node names",
                valid_msg="node names",
            )

        return matches

    def find_by_features(self, values=None, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or values is None:
            return adapters

        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            for check in adapter["features"]:
                if check not in known:
                    known.append(check)

                for value in values:
                    value_re = re.compile(value, re.I)
                    if value_re.search(check) and adapter not in matches:
                        matches.append(adapter)

        if not matches and known and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by features",
                valid_msg="features",
            )

        return matches

    def find_by_client_statuses(self, values=None, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or values is None:
            return adapters

        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            for client in adapter["clients"]:
                check = client["status"]

                if check not in known:
                    known.append(check)

                for value in values:
                    value_re = re.compile(value, re.I)
                    if value_re.search(check) and adapter not in matches:
                        msg = "Matched adapter name {a!r} using client status {v!r}"
                        msg = msg.format(a=adapter["name"], v=value)
                        self._log.debug(msg)

                        matches.append(adapter)

        if not matches and known and error:
            raise exceptions.UnknownError(
                value=values,
                known=known,
                reason_msg="adapter by client statuses",
                valid_msg="client statuses",
            )

        return matches

    def find_by_client_count(self, client_min=None, client_max=None, adapters=None):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or (client_min is None and client_max is None):
            return adapters

        matches = []

        for adapter in adapters:
            client_count = len(adapter["clients"])

            if client_min is not None and not client_count >= client_min:
                continue

            if client_max is not None and not client_count <= client_max:
                continue

            msg = "Matched adapter name {a!r} using client min {cmin!r}, max {cmax!r}"
            msg = msg.format(a=adapter["name"], cmin=client_min, max=client_max)
            self._log.debug(msg)

            matches.append(adapter)

        return matches

    def find_by_client_ids(self, values=None, adapters=None, error=True):
        """Pass."""
        adapters = adapters or self.parse()

        if not adapters or values is None:
            return adapters

        if not isinstance(values, (tuple, list)):
            values = [values]

        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            for client in adapter["clients"]:
                check = client["client_id"]

                if check not in known:
                    known.append(check)

                for value in values:
                    value_re = re.compile(value, re.I)
                    if value_re.search(check) and adapter not in matches:
                        msg = "Matched adapter name {a!r} using client id {v!r}"
                        msg = msg.format(a=adapter["name"], v=value)
                        self._log.debug(msg)

                        matches.append(adapter)

        if not matches and known and error:
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
