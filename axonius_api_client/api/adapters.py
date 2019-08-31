# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re

from .. import exceptions, tools
from . import mixins, routers


class Clients(mixins.Child):
    """Pass."""

    # TODO: Add csv upload file method
    # TODO: Add fetch method
    # TODO: public add method
    # TODO: public delete method
    def _check(self, adapter_name, client_config, node_id):
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
        data.update(client_config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id
        path = self._parent._router.clients.format(adapter_name=adapter_name)
        return self._parent._request(method="post", path=path, json=data, raw=True)

    def _upload_file(
        self,
        adapter_name,
        node_id,
        file_name,
        file_contents,
        field_name=None,
        content_type=None,
    ):
        """Pass."""
        data = {"field_name": field_name or file_name}

        if content_type:
            files = {"userfile": (file_name, file_contents, content_type)}
        else:
            files = {"userfile": (file_name, file_contents)}

        path = self._parent._router.clients_upload_file.format(
            adapter_name=adapter_name, node_id=node_id
        )
        return self._parent._request(method="post", path=path, json=data, files=files)

    def _add(self, adapter_name, config, node_id):
        """Add a client to an adapter.

        Args:
            adapter_name (:obj:`str`):
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
        path = self._router.clients.format(adapter_name=adapter_name)
        return self._request(method="put", path=path, json=data)

    def _delete(self, name, id, node_id):
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
        path = self._router.clients_id.format(adapter_name=name, id=id)
        return self._request(method="delete", path=path, json=data)

    def get(
        self,
        ids=None,
        status=None,
        error=True,
        all_clients=None,
        all_adapters=None,
        **kwargs
    ):
        """Get all clients for all adapters."""
        if not all_clients:
            all_adapters = all_adapters or self._parent.get(error=error, **kwargs)
            all_clients = [
                client for adapter in all_adapters for client in adapter["clients"]
            ]

        matches = []
        known_ids = []

        for client in all_clients:
            # FUTURE: date_fetched for client seems to be only for
            # when fetch has been triggered from "save" in adapters>client page??
            # need to submit BR
            """
            date_fetched = client["date_fetched"]
            minutes_ago = tools.dt.minutes_ago(date_fetched)

            if within is not None:
                if minutes_ago >= within:
                    continue

            if not_within is not None:
                if minutes_ago <= not_within:
                    continue
            """

            client_id = client["client_id"]

            skips = [
                client["status_bool"] and status is False,
                not client["status_bool"] and status is True,
            ]

            client_str = "Adapter {adapter!r} client id {client_id!r}"
            client_str = client_str.format(**client)

            if client_str not in known_ids:
                known_ids.append(client_str)

            for value in tools.listify(ids):
                value_re = re.compile(value, re.I)
                skips.append(not value_re.search(client_id))

            if any(skips):
                continue

            if client not in matches:
                matches.append(client)

        if error:
            if not all_clients:
                raise exceptions.UnknownError(
                    value=ids,
                    known=known_ids,
                    reason_msg="adapters with clients",
                    valid_msg="adapter client ids",
                )

            if not matches and ids is not None and known_ids:
                raise exceptions.UnknownError(
                    value=ids,
                    known=known_ids,
                    reason_msg="adapter client by ids",
                    valid_msg="adapter client ids",
                )

        return matches

    def check(
        self, adapter_names=None, ids=None, nodes=None, error_check=True, **kwargs
    ):
        """Pass."""
        clients = self.get(ids=ids, names=adapter_names, nodes=nodes, **kwargs)

        results = []

        for client in clients:
            response = self._check(
                adapter_name=client["adapter_raw"],
                client_config=client["client_config"],
                node_id=client["node_id"],
            )

            status = not response.text
            adapter = client["adapter"]
            error = tools.json.re_load(response.text)
            node = client["node_name"]

            if error_check and not status:
                raise exceptions.ClientConnectFailure(
                    response=response, adapter=adapter, node=node
                )

            result = {
                "adapter": adapter,
                "node": node,
                "status": status,
                "response": error,
            }

            results.append(result)

        return results[0] if len(results) == 1 else results

    def add(self, adapter_name, node_name, all_adapters=None, **kwargs):
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
        adapter = self._parent.get(
            names=adapter_name,
            nodes=node_name,
            count_min=1,
            count_max=1,
            count_error=True,
            all_adapters=all_adapters,
        )

        # client_config = {}

        errors = []

        for setting, schema in adapter["settings_clients"]:
            if setting not in kwargs:
                if schema["required"]:
                    msg = "Required client setting {s!r} was not supplied"
                    msg = msg.format(s=setting)
                    errors.append(msg)
                continue

            try:
                self._check_setting_type(setting=setting, schema=schema, **kwargs)
            except exceptions.ApiError as exc:
                errors.append(format(exc))

        if errors:
            msg = "Errors when trying to add a client for adapter {name!r}:{errors}"
            msg = msg.format(name=adapter["name"], errors=tools.join.cr(errors))
            raise exceptions.ApiError(msg)

        return adapter

    def _check_setting_type(self, setting_name, schema, **kwargs):
        """Pass."""
        type_str = schema["type"]
        value = kwargs.get(setting_name, None)

        if type_str == "bool":
            type_result = tools.is_type.bool(value)
        elif type_str in ["number", "integer"]:
            type_result = tools.is_type.str_int(value)
        elif type_str == "file":
            type_result = self._check_upload_file(**kwargs)
            # TODO: this doesn't work -- we need to ensure it's
            # "csv": {"uuid": resp["uuid"], "filename": CSV_FILENAME}
            # we could do is type dict
            # if has uuid in it, already uploaded use that
            # if has filename/filepath/etc, upload it and get uuid
        else:
            type_result = tools.is_type.str(value)
        if not type_result:
            msg = [
                "Setting {s!r} is invalid type",
                "must be type {mt!r}",
                "supplied type {st!r}",
            ]
            msg = tools.join.comma(msg).format(
                s=setting_name, mt=type_str, st=type(value).__name__
            )
            raise exceptions.ApiError(msg)

    def _check_upload_file(**kwargs):
        """Pass."""
        pre_keys = [
            "file_path",
            "file_name",
            "file_contents",
            "content_type",
            "field_name",
        ]
        pre_keys = {x: kwargs.get("pre", "") + x for x in pre_keys}
        lookup = {k: kwargs.get(v, None) for k, v in pre_keys.items()}

        if lookup["file_path"]:
            path = tools.path.resolve(lookup["file_path"])

            if not path.is_file():
                msg = "Supplied {fp_key!r}='{fp}' resolved='{rp}' does not exist!"
                msg = msg.format(
                    fp=lookup["file_path"], rp=path, fp_key=pre_keys["file_path"]
                )

                raise exceptions.ApiError(msg)

            lookup["file_contents"] = path.read_bytes()
            lookup["file_name"] = lookup["file_name"] or path.name
        elif lookup["file_contents"] and lookup["file_name"]:
            lookup["file_name"] = lookup["file_name"]
            lookup["file_contents"] = lookup["file_contents"]
        else:
            msg = "Must supply {fp_key!r} or {fc_key!r} and {fn_key}!"
            msg = msg.format(
                fp_key=pre_keys["file_path"],
                fc_key=pre_keys["file_contents"],
                fn_key=pre_keys["file_name"],
            )
            raise exceptions.ApiError(msg)

        return lookup

    def upload_file(self, adapter_name=None, node_name=None, **kwargs):
        """Pass."""
        adapter_data = kwargs.get("adapter_data", None)
        file_checked = kwargs.get("file_checked", None) or self._check_upload_file(
            **kwargs
        )

        if (not adapter_name and not node_name) or not adapter_data:
            msg = "Must supply 'adapter_name' and 'node_name' or 'adapter_data'!"
            raise exceptions.ApiError(msg)

        adapter_data = adapter_data or self._parent.get(
            names=adapter_name,
            nodes=node_name,
            count_min=1,
            count_max=1,
            count_error=True,
            all_adapters=kwargs.get("all_adapters", None),
        )

        return self._upload_file(
            adapter_name=adapter_data["name_raw"],
            node_id=adapter_data["node_id"],
            file_name=file_checked["file_name"],
            file_contents=file_checked["file_contents"],
            field_name=file_checked["field_name"],
            content_type=file_checked["content_type"],
        )


class Adapters(mixins.Model, mixins.Mixins):
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

    def _get_parse(self, all_adapters=None):
        """Pass."""
        if not all_adapters:
            raw = self._get()
            parser = ParserAdapters(raw=raw, parent=self)
            all_adapters = parser.parse()
        return all_adapters

    def get(
        self,
        names=None,
        nodes=None,
        client_status=None,
        client_max=None,
        client_min=None,
        count_min=None,
        count_max=None,
        count_error=True,
        all_adapters=None,
        error=True,
    ):
        """Get all adapters."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        adapters = self.get_by_names(
            values=names, all_adapters=all_adapters, error=error
        )
        adapters = self.get_by_nodes(values=nodes, all_adapters=adapters, error=error)
        adapters = self.get_by_client_count(
            client_max=client_max, client_min=client_min, all_adapters=adapters
        )
        adapters = self.get_by_client_status(
            client_status=client_status, all_adapters=adapters
        )

        value = [
            "names: {names!r}",
            "nodes: {nodes!r}",
            "client_status: {client_status}",
            "client_max: {client_max}",
            "client_min: {client_min}",
            "count_max: {count_max}",
            "count_min: {count_min}",
        ]
        value = tools.join.comma(value)
        value = value.format(
            names=names,
            nodes=nodes,
            client_max=client_max,
            client_min=client_min,
            client_status=client_status,
            count_min=count_min,
            count_max=count_max,
        )

        self._check_counts(
            value=value,
            value_type="adapter filters",
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(adapters),
            known_callback=self.get_brief,
            error=count_error,
        )

        return self._only1(rows=adapters, count_min=count_min, count_max=count_max)

    def get_brief(self, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        adapter_strs = []
        for adapter in all_adapters:
            adapter_str = [
                "adapter name: {name!r}",
                "node name: {node_name!r}",
                "status: {status_bool}",
                "clients: {client_count}",
            ]
            adapter_str = tools.join.comma(adapter_str).format(**adapter)
            adapter_strs.append(adapter_str)
        return adapter_strs

    def get_by_names(self, values=None, error=True, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if values is None:
            return all_adapters

        values = tools.listify(values)
        values = [tools.strip.right(name, "_adapter").lower() for name in values]

        matches = []
        known = []

        for adapter in all_adapters:
            check = adapter["name"]

            if check not in known:
                known.append(check)

            for value in values:
                value_re = re.compile(value, re.I)
                if value_re.search(check) and adapter not in matches:
                    matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known or self.get_brief,
                reason_msg="adapter by names",
                valid_msg="names",
            )

        return matches

    def get_by_nodes(self, values=None, error=True, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if values is None:
            return all_adapters

        values = tools.listify(values)
        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in all_adapters:
            check = adapter["node_name"]

            if check not in known:
                known.append(check)

            for value in values:
                value_re = re.compile(value, re.I)
                if value_re.search(check) and adapter not in matches:
                    matches.append(adapter)

        if not matches and error:
            raise exceptions.UnknownError(
                value=values,
                known=known or self.get_brief,
                reason_msg="adapter by node names",
                valid_msg="node names",
            )

        return matches

    def get_by_features(self, values=None, error=True, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if values is None:
            return all_adapters

        values = tools.listify(values)
        values = [name.lower() for name in values]

        matches = []
        known = []

        for adapter in all_adapters:
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
                known=known or self.get_brief,
                reason_msg="adapter by features",
                valid_msg="features",
            )

        return matches

    def get_by_client_count(
        self, client_min=None, client_max=None, error=True, all_adapters=None
    ):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if client_min is None and client_max is None:
            return all_adapters

        matches = []

        for adapter in all_adapters:
            client_count = len(adapter["clients"])

            if client_min is not None and not client_count >= client_min:
                continue

            if client_max is not None and not client_count <= client_max:
                continue

            matches.append(adapter)

        if not matches and error:
            values = ["client_min: {client_min}", "client_max: {client_max}"]
            values = tools.join.comma(values).format(
                client_min=client_min, client_max=client_max
            )
            raise exceptions.UnknownError(
                value=values,
                known=self.get_brief,
                reason_msg="adapter by client count",
                valid_msg="adapters with client counts",
            )

        return matches

    def get_by_client_status(self, client_status=None, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if client_status is None:
            return all_adapters

        matches = []

        for adapter in all_adapters:
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
                value = raw_config.get(setting_name, self._NOTSET)
                value = self._HIDDEN if value == self._RAW_HIDDEN else value
                parsed_settings[setting_name] = setting_config
                parsed_settings[setting_name]["value"] = value

            status_bool = None

            if raw_client["status"] == "success":
                status_bool = True
            elif raw_client["status"] == "error":
                status_bool = False

            parsed_client = raw_client.copy()
            parsed_client["node_name"] = parent["node_name"]
            parsed_client["node_id"] = parent["node_id"]
            parsed_client["adapter"] = parent["name"]
            parsed_client["adapter_raw"] = parent["name_raw"]
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
