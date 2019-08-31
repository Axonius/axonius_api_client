# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re
import warnings

from .. import exceptions, tools
from . import mixins, routers


def load_filepath(filepath):
    """Pass."""
    rpath = tools.path.resolve(filepath)

    if not rpath.is_file():
        msg = "Supplied filepath='{fp}' (resolved='{rp}') does not exist!"
        msg = msg.format(fp=filepath, rp=rpath)
        raise exceptions.ApiError(msg)

    filecontent = rpath.read_text()
    filename = rpath.name
    return filename, filecontent


class Clients(mixins.Child):
    """Pass."""

    CSV_FIELDS = {
        "device": ["id", "serial", "mac_address", "hostname", "name"],
        "user": ["id", "username", "mail", "name"],
        "sw": ["hostname", "installed_sw_name"],
    }

    SETTING_TYPES = {
        "bool": tools.is_type.bool,
        "number": tools.is_type.str_int,
        "integer": tools.is_type.str_int,
        "array": tools.is_type.los,
        "string": tools.is_type.str,
    }

    # TODO: Add fetch method
    # TODO: public delete method
    def _check(self, adapter, config, node_id):
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
        path = self._parent._router.clients.format(adapter_name=adapter)
        return self._parent._request(method="post", path=path, json=data, raw=True)

    def _add(self, adapter, config, node_id):
        """Add a client to an adapter.

        Args:
            adapter (:obj:`str`):
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
        path = self._parent._router.clients.format(adapter_name=adapter)
        return self._parent._request(method="put", path=path, json=data)

    # FUTURE: how to delete assets too?
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

    def _parse_config(self, adapter_data, **kwargs):
        """Pass."""
        config = {}

        for name, schema in adapter_data["settings_clients"].items():
            required = schema["required"]
            type_str = schema["type"]
            enum = schema.get("enum", [])
            default = schema.get("default", None)
            value = kwargs.get(name, None)

            msg = "Processing {req} setting {n!r} with value of {v!r}, schema: {ss}"
            msg = msg.format(
                req="required" if required else "optional", n=name, v=value, ss=schema
            )
            self._log.debug(msg)

            if value is None:
                if default is None and required:
                    error = "was not supplied"
                    raise exceptions.ClientSettingError(
                        name=name, value=value, schema=schema, error=error
                    )
                elif default is not None:
                    value = default
                else:
                    continue

            if enum and value not in enum:
                error = "invalid choice, must be one of {enum}"
                error = error.format(enum=enum)
                raise exceptions.ClientSettingError(
                    name=name, value=value, schema=schema, error=error
                )

            if type_str == "file":
                value = self._check_file(
                    name=name, value=value, schema=schema, adapter_data=adapter_data
                )

            if type_str in self.SETTING_TYPES:
                self._check_type(
                    name=name,
                    schema=schema,
                    value=value,
                    type_cb=self.SETTING_TYPES[type_str],
                )

            # FUTURE: number/integer need to be coerced???
            # FUTURE: warning/error for unhandled types?

            config[name] = value
        return config

    @staticmethod
    def _upload_dict(d):
        """Pass."""
        return {"uuid": d["uuid"], "filename": d["filename"]}

    def _check_file(self, name, value, schema, adapter_data):
        """Pass."""
        if tools.is_type.str(value) or tools.is_type.path(value):
            uploaded = self._parent.upload_file(
                adapter_data=adapter_data, field=name, path=value
            )
            return self._upload_dict(uploaded)

        self._check_type(
            name=name, schema=schema, value=value, type_cb=tools.is_type.dict
        )

        uuid = value.get("uuid", None)
        filename = value.get("filename", None)
        filepath = value.get("filepath", None)
        filecontent = value.get("filecontent", None)
        filecontent_type = value.get("filecontent_type", None)

        if uuid:
            if not filename:
                ex = {name: {"uuid": "uuid", "filename": "filename"}}

                if filepath:
                    value["filename"] = tools.path.resolve(filepath).name
                else:
                    error = (
                        "must supply 'filename' when supplying 'uuid', example: {ex}"
                    )
                    error = error.format(n=name, ex=ex)
                    raise exceptions.ClientSettingError(
                        name=name, value=value, schema=schema, error=error
                    )

            return self._upload_dict(value)
        else:
            if not filepath and (not filecontent or not filename):
                ex1 = "('filecontent' and 'filename') (example: {})".format(
                    {
                        name: {
                            "filename": "filename",
                            "filecontent": "binary content",
                            "filecontent_type": "optional mime type",
                        }
                    }
                )
                ex2 = "'filepath' (example: {})".format(
                    {
                        name: {
                            "filepath": "path to file",
                            "filecontent_type": "optional mime type",
                        }
                    }
                )

                error = "Must supply {ex1} or {ex2}!"
                error = error.format(ex1=ex1, ex2=ex2)
                raise exceptions.ClientSettingError(
                    name=name, value=value, schema=schema, error=error
                )

            uploaded = self._parent.upload_file(
                adapter_data=adapter_data,
                filename=filename,
                filepath=filepath,
                filecontent=filecontent,
                filecontent_type=filecontent_type,
                field=name,
            )

            return self._upload_dict(uploaded)

    def _check_type(self, name, value, type_cb, schema):
        """Pass."""
        required = schema["required"]
        pre = "{req} setting {n!r} with value {v!r}"
        pre = pre.format(req="Required" if required else "Optional", n=name, v=value)

        if not type_cb(value):
            error = "is invalid type {st!r}"
            error = error.format(st=type(value).__name__)
            raise exceptions.ClientSettingError(
                name=name, value=value, schema=schema, error=error
            )

    def get(self, ids=None, status=None, error=True, **kwargs):
        """Get all clients for all adapters."""
        all_adapters = self._parent.get(error=error, **kwargs)
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

    def check(self, ids=None, adapters=None, nodes=None, error_check=True, **kwargs):
        """Pass."""
        clients = self.get(ids=ids, names=adapters, nodes=nodes, **kwargs)

        results = []

        for client in clients:
            response = self._check(
                adapter=client["adapter_raw"],
                config=client["client_config"],
                node_id=client["node_id"],
            )

            adapter = client["adapter"]
            node = client["node_name"]
            status = not response.text
            error = tools.json.re_load(response.text)

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

    def add(self, adapter, node="master", **kwargs):
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
        kwargs["adapter_data"] = self._parent.get(
            names=adapter,
            nodes=node,
            count_min=1,
            count_max=1,
            count_error=True,
            use_regex=False,
        )

        name_raw = kwargs["adapter_data"]["name_raw"]
        node_id = kwargs["adapter_data"]["node_id"]

        config = self._parse_config(**kwargs)

        return self._add(adapter=name_raw, config=config, node_id=node_id)

    def add_csv(
        self,
        node="master",
        fieldname=None,
        is_users=False,
        is_installed_sw=False,
        filename=None,
        filecontent=None,
        filepath=None,
        url=None,
        share=None,
        share_username=None,
        share_password=None,
    ):
        """Add a client to the CSV adapter.

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
        if not any([fieldname, filename, filepath]):
            error = "Must supply 'fieldname' or 'filename' or 'filepath'"
            raise exceptions.ApiError(error)

        if filepath:
            filename, filecontent = load_filepath(filepath)

        fieldname = fieldname or filename

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = fieldname

        if filename and filecontent:
            if is_users:
                ids = self.CSV_FIELDS["user"]
                ids_type = "user"
            elif is_installed_sw:
                ids = self.CSV_FIELDS["sw"]
                ids_type = "installed software"
            else:
                ids = self.CSV_FIELDS["device"]
                ids_type = "device"

            headers = filecontent.splitlines()[0].lower().split(",")
            headers_has_any_id = any([x in headers for x in ids])

            if not headers_has_any_id:
                error = "No {ids_type} identifiers {ids} found in CSV headers {h}"
                error = error.format(ids_type=ids_type, ids=ids, h=headers)
                warnings.warn(error, exceptions.ApiWarning)

            config["csv"] = {}
            config["csv"]["filename"] = filename
            config["csv"]["filecontent"] = filecontent
            config["csv"]["filecontent_type"] = "text/csv"
        elif url:
            config["csv_http"] = url
        elif share:
            config["csv_share"] = share
            config["csv_share_username"] = share_username
            config["csv_share_password"] = share_password
        else:
            opts = [
                "'filepath': path to CSV file to load",
                "'filename' and 'filecontent': name and contents of CSV to load",
                "'url': URL of CSV to fetch",
                "'share' (optional: 'share_username' and 'share_password'): "
                "SMB share path of CSV to fetch",
            ]
            error = "Must supply one of the following:{opts}"
            error = error.format(opts=tools.join.cr(opts))
            raise exceptions.ApiError(error)

        return self.add(adapter="csv", node=node, **config)


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

    def _upload_file(
        self, adapter, node_id, filename, field, filecontent, filecontent_type=None
    ):
        """Pass."""
        data = {"field_name": field}

        if filecontent_type:
            files = {"userfile": (filename, filecontent, filecontent_type)}
        else:
            files = {"userfile": (filename, filecontent)}

        path = self._router.clients_upload_file.format(
            adapter_name=adapter, node_id=node_id
        )
        ret = self._request(method="post", path=path, data=data, files=files)
        ret["filename"] = filename
        return ret

    def get(
        self,
        names=None,
        nodes=None,
        status=None,
        client_max=None,
        client_min=None,
        count_min=None,
        count_max=None,
        count_error=True,
        all_adapters=None,
        use_regex=False,
        error=True,
    ):
        """Get all adapters."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        adapters = self.get_by_names(
            values=names, all_adapters=all_adapters, error=error, use_regex=use_regex
        )
        adapters = self.get_by_nodes(
            values=nodes, all_adapters=adapters, error=error, use_regex=use_regex
        )
        adapters = self.get_by_client_count(
            client_max=client_max, client_min=client_min, all_adapters=adapters
        )
        adapters = self.get_by_status(status=status, all_adapters=adapters)

        value = [
            "names: {!r}".format(names),
            "nodes: {!r}".format(nodes),
            "status: {}".format(status),
            "client_max: {}".format(client_max),
            "client_min: {}".format(client_min),
            "count_max: {}".format(count_max),
            "count_min: {}".format(count_min),
            "use_regex: {}".format(use_regex),
        ]
        value = tools.join.comma(value)

        self._check_counts(
            value=value,
            value_type="adapter filters",
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(adapters),
            known=self.get_brief,
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

    def get_by_names(self, values=None, error=True, all_adapters=None, use_regex=False):
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
                if use_regex:
                    value_re = re.compile(value, re.I)
                    match = value_re.search(check)
                else:
                    match = check.lower() == value.lower()

                if match and adapter not in matches:
                    matches.append(adapter)

        if not matches and error:
            reason_msg = "adapter by names using regex {}".format(use_regex)
            raise exceptions.UnknownError(
                value=values,
                known=known or self.get_brief,
                reason_msg=reason_msg,
                valid_msg="names",
            )

        return matches

    def get_by_nodes(self, values=None, error=True, all_adapters=None, use_regex=False):
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
                if use_regex:
                    value_re = re.compile(value, re.I)
                    match = value_re.search(check)
                else:
                    match = check.lower() == value.lower()

                if match and adapter not in matches:
                    matches.append(adapter)

        if not matches and error:
            reason_msg = "adapter by node names using regex {}".format(use_regex)
            raise exceptions.UnknownError(
                value=values,
                known=known or self.get_brief,
                reason_msg=reason_msg,
                valid_msg="node names",
            )

        return matches

    def get_by_features(
        self, values=None, error=True, all_adapters=None, use_regex=False
    ):
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
                    if use_regex:
                        value_re = re.compile(value, re.I)
                        match = value_re.search(check)
                    else:
                        match = check.lower() == value.lower()

                    if match and adapter not in matches:
                        matches.append(adapter)

        if not matches and known and error:
            reason_msg = "adapter by features using regex {}".format(use_regex)
            raise exceptions.UnknownError(
                value=values,
                known=known or self.get_brief,
                reason_msg=reason_msg,
                valid_msg="features",
            )

        return matches

    def get_by_client_count(
        self, client_min=None, client_max=None, error=True, all_adapters=None
    ):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        matches = []

        for adapter in all_adapters:
            client_count = len(adapter["clients"])

            if client_min is not None and not client_count >= client_min:
                continue

            if client_max is not None and not client_count <= client_max:
                continue

            matches.append(adapter)

        if not matches and error:
            values = [
                "client_min: {}".format(client_min),
                "client_max: {}".format(client_max),
            ]
            values = tools.join.comma(values)
            raise exceptions.UnknownError(
                value=values,
                known=self.get_brief,
                reason_msg="adapter by client count",
                valid_msg="adapters with client counts",
            )

        return matches

    def get_by_status(self, status=None, all_adapters=None):
        """Pass."""
        all_adapters = self._get_parse(all_adapters=all_adapters)

        if status is None:
            return all_adapters

        matches = []

        for adapter in all_adapters:
            if adapter["status_bool"] is True and status is True:
                matches.append(adapter)
            elif adapter["status_bool"] is False and status is False:
                matches.append(adapter)

        return matches

    def upload_file(
        self,
        field,
        filename=None,
        filecontent=None,
        filecontent_type=None,
        filepath=None,
        name=None,
        node="master",
        adapter_data=None,
        all_adapters=None,
    ):
        """Pass."""
        if not adapter_data and (not name or not node):
            msg = "Must supply adapter ('name' and 'node') or 'adapter_data'!"
            raise exceptions.ApiError(msg)

        if not filepath and (not filecontent or not filename):
            msg = "Must supply ('filecontent' and 'filename') or 'filepath'!"
            raise exceptions.ApiError(msg)

        if filepath:
            filename, filecontent = load_filepath(filepath)

        if not tools.is_type.bytes(filecontent):
            filecontent = filecontent.encode()

        adapter_data = adapter_data or self.get(
            names=name,
            nodes=node,
            count_min=1,
            count_max=1,
            count_error=True,
            all_adapters=all_adapters,
        )

        return self._upload_file(
            adapter=adapter_data["name_raw"],
            node_id=adapter_data["node_id"],
            filename=filename,
            field=field,
            filecontent=filecontent,
            filecontent_type=filecontent_type,
        )


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
