# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re

from .. import exceptions, tools
from . import mixins, routers


class Clients(mixins.Child):
    """Pass."""

    # TODO: Add csv upload file
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

    def get(self, within=None, not_within=None, status=None, **kwargs):
        """Get all adapters."""
        adapters = kwargs.get("adapters", self._parent.get(**kwargs))
        clients = []

        for adapter in adapters:
            for client in adapter["clients"]:
                # FUTURE: date_fetched for client seems to be only for
                # when fetch has been triggered from "save" in adapters>client page??
                minutes_ago = tools.dt.minutes_ago(client["date_fetched"])

                if within is not None:
                    if minutes_ago >= within:
                        continue

                if not_within is not None:
                    if minutes_ago <= not_within:
                        continue

                if client["status_bool"] and status is False:
                    continue

                if not client["status_bool"] and status is True:
                    continue

                clients.append(client)

        return clients


class Adapters(mixins.Mixins):
    """Adapter related API methods."""

    def _init(self, auth, **kwargs):
        """Pass."""
        self.clients = Clients(parent=self)

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

    def _get_parse(self, **kwargs):
        """Pass."""
        if "adapters" in kwargs:
            adapters = kwargs["adapters"]
        else:
            raw = self._get()
            parser = ParserAdapters(raw=raw, parent=self)
            adapters = parser.parse()
        return adapters

    def get(
        self,
        names=None,
        nodes=None,
        client_status=None,
        client_max=None,
        client_min=None,
        **kwargs
    ):
        """Get all adapters."""
        adapters = self._get_parse(**kwargs)
        error = kwargs.get("error", True)

        adapters = self.get_by_names(values=names, adapters=adapters, error=error)
        adapters = self.get_by_nodes(values=nodes, adapters=adapters, error=error)
        adapters = self.get_by_client_count(
            client_max=client_max, client_min=client_min, adapters=adapters
        )
        adapters = self.get_by_client_status(
            client_status=client_status, adapters=adapters
        )
        return adapters

    def get_by_names(self, values=None, **kwargs):
        """Pass."""
        adapters = self._get_parse(**kwargs)
        error = kwargs.get("error", True)

        if not adapters or values is None:
            return adapters

        if not tools.is_type.list(values):
            values = [values]

        values = [tools.strip.right(name, "_adapter").lower() for name in values]

        matches = []
        known = []

        for adapter in adapters:
            check = adapter["name"]

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
                reason_msg="adapter by names",
                valid_msg="names",
            )

        return matches

    def get_by_nodes(self, values=None, **kwargs):
        """Pass."""
        adapters = self._get_parse(**kwargs)
        error = kwargs.get("error", True)

        if not adapters or values is None:
            return adapters

        if not tools.is_type.list(values):
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

    def get_by_features(self, values=None, **kwargs):
        """Pass."""
        adapters = self._get_parse(**kwargs)
        error = kwargs.get("error", True)

        if not adapters or values is None:
            return adapters

        if not tools.is_type.list(values):
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

    def get_by_client_count(self, client_min=None, client_max=None, **kwargs):
        """Pass."""
        adapters = self._get_parse(**kwargs)

        if not adapters or (client_min is None and client_max is None):
            return adapters

        matches = []

        for adapter in adapters:
            client_count = len(adapter["clients"])

            if client_min is not None and not client_count >= client_min:
                continue

            if client_max is not None and not client_count <= client_max:
                continue

            matches.append(adapter)

        return matches

    def get_by_client_status(self, client_status=None, **kwargs):
        """Pass."""
        adapters = self._get_parse(**kwargs)

        if not adapters or client_status is None:
            return adapters

        matches = []

        for adapter in adapters:
            clients = adapter["clients"]
            match = True

            for client in clients:
                if not client["status_bool"] and client_status:
                    match = False
                if client["status_bool"] and not client_status:
                    match = False

            if match:
                matches.append(adapter)

        return matches


class ParserAdapters(mixins.Parser):
    """Pass."""

    _NOTSET = "__NOTSET__"
    _RAW_HIDDEN = ["unchanged"]
    _HIDDEN = "__HIDDEN__"

    def _parse_adapter(self, name, raw):
        """Pass."""
        parsed = {
            "name": tools.strip.right(name, "_adapter"),
            "name_raw": name,
            "name_plugin": raw["unique_plugin_name"],
            "node_name": raw["node_name"],
            "node_id": raw["node_id"],
            "status": raw["status"],
            "features": raw["supported_features"],
        }

        clients = self._clients(raw=raw, parent=parsed)
        client_count = len(clients)
        client_count_ok = len([x for x in clients if x["status_bool"] is True])
        client_count_bad = len([x for x in clients if x["status_bool"] is False])

        if parsed["status"] == "success":
            status_bool = True
        elif parsed["status"] == "warning":
            status_bool = False
        else:
            status_bool = None

        settings_clients = self._settings_clients(raw=raw)
        settings_adapter = self._settings_adapter(raw=raw, base=False)
        settings_advanced = self._settings_adapter(raw=raw, base=True)

        parsed["clients"] = clients
        parsed["client_count"] = client_count
        parsed["client_count_ok"] = client_count_ok
        parsed["client_count_bad"] = client_count_bad
        parsed["status_bool"] = status_bool
        parsed["settings_clients"] = settings_clients
        parsed["settings_adapter"] = settings_adapter
        parsed["settings_advanced"] = settings_advanced
        return parsed

    def _settings_clients(self, raw):
        """Pass."""
        settings = {}

        schema = raw["schema"]
        items = schema["items"]
        required = schema["required"]

        for item in items:
            setting_name = item["name"]
            settings[setting_name] = {k: v for k, v in item.items()}
            settings[setting_name]["required"] = setting_name in required

        return settings

    def _settings_adapter(self, raw, base=True):
        """Pass."""
        settings = {}

        for raw_name, raw_settings in raw["config"].items():
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

    def _clients(self, raw, parent):
        """Pass."""
        clients = []

        settings_client = self._settings_clients(raw=raw)

        for raw_client in raw["clients"]:
            raw_config = raw_client["client_config"]
            parsed_settings = {}

            for setting_name, setting_config in settings_client.items():
                setting_config.pop("name", "")
                value = raw_config.get(setting_name, self._NOTSET)
                value = self._HIDDEN if value == self._RAW_HIDDEN else value
                parsed_settings[setting_name] = setting_config
                parsed_settings[setting_name]["value"] = value

            if raw_client["status"] == "success":
                status_bool = True
            elif raw_client["status"] == "error":
                status_bool = False
            else:
                status_bool = None

            parsed_client = {
                k: v for k, v in raw_client.items() if k != "client_config"
            }
            parsed_client["node_name"] = parent["node_name"]
            parsed_client["node_id"] = parent["node_id"]
            parsed_client["adapter"] = parent["name"]
            parsed_client["adapter_status"] = parent["status"]
            parsed_client["adapter_features"] = parent["features"]
            parsed_client["settings"] = parsed_settings
            parsed_client["status_bool"] = status_bool
            clients.append(parsed_client)
        return clients

    def parse(self):
        """Pass."""
        parsed = []

        for name, raw_adapters in self._raw.items():
            for raw in raw_adapters:
                adapter = self._parse_adapter(name=name, raw=raw)
                parsed.append(adapter)

        return parsed


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
