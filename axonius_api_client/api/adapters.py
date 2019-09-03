# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import time
import warnings

from .. import exceptions, tools
from . import mixins, routers


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

    def _check(self, adapter_name, node_id, config):
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
        path = self._parent._router.clients.format(adapter_name=adapter_name)
        return self._parent._request(
            method="post",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _add(self, adapter_name, node_id, config):
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
        path = self._parent._router.clients.format(adapter_name=adapter_name)
        return self._parent._request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _delete(self, adapter_name, node_id, client_id, delete_entities=False):
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
        path = self._parent._router.clients_id.format(
            adapter_name=adapter_name,
            client_id=client_id,
            error_json_bad_status=False,
            error_code_not_200=False,
        )
        params = {"deleteEntities": delete_entities}
        return self._parent._request(
            method="delete",
            path=path,
            json=data,
            params=params,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _config_parse(self, adapter, settings_client, config):
        """Pass."""
        new_config = {}

        for name, schema in settings_client.items():
            required = schema["required"]
            type_str = schema["type"]
            enum = schema.get("enum", [])

            value = config.get(name, None)

            has_value = name in config
            has_default = "default" in schema

            req = "required" if required else "optional"
            msg = "Processing {req} setting {n!r} with value of {v!r}, schema: {ss}"
            msg = msg.format(req=req, n=name, v=value, ss=schema)
            self._log.debug(msg)

            if not has_value and not has_default:
                if not required:
                    continue
                error = "value was not supplied and has no default value"
                raise exceptions.ClientConfigMissingError(
                    name=name, value=value, schema=schema, error=error
                )

            if not has_value and has_default:
                value = schema["default"]

            if enum and value not in enum:
                error = "invalid value {value!r}, must be one of {enum}"
                error = error.format(value=value, enum=enum)
                raise exceptions.ClientConfigInvalidChoiceError(
                    name=name, value=value, schema=schema, error=error
                )

            if type_str == "file":
                value = self._config_file_check(
                    name=name, value=value, schema=schema, adapter=adapter
                )
            elif type_str in self.SETTING_TYPES:
                self._config_type_check(
                    name=name,
                    schema=schema,
                    value=value,
                    type_cb=self.SETTING_TYPES[type_str],
                )
            else:
                error = "Unknown setting type: {type_str!r}"
                error = error.format(type_str=type_str)
                raise exceptions.ClientConfigUnknownError(
                    name=name, value=value, schema=schema, error=error
                )

            # FUTURE: number/integer need to be coerced???

            new_config[name] = value
        return new_config

    @staticmethod
    def _config_file(d):
        """Pass."""
        return {"uuid": d["uuid"], "filename": d["filename"]}

    def _config_file_check(self, name, value, schema, adapter):
        """Pass."""
        if tools.is_type.str(value) or tools.is_type.path(value):
            uploaded = self._parent.upload_file_path(
                adapter=adapter, field=name, filepath=value
            )
            return self._config_file(uploaded)

        self._config_type_check(
            name=name, schema=schema, value=value, type_cb=tools.is_type.dict
        )

        uuid = value.get("uuid", None)
        filename = value.get("filename", None)
        filepath = value.get("filepath", None)
        filecontent = value.get("filecontent", None)
        filecontent_type = value.get("filecontent_type", None)

        ex_uuid = {
            name: {
                "uuid": "uuid",
                "filename": "filename",
                "filepath": "optional str or pathlib to get filename from",
            }
        }
        ex_filecontent = {
            name: {
                "filename": "filename",
                "filecontent": "binary content",
                "filecontent_type": "optional mime type",
            }
        }

        ex_filepath = {
            name: {"filepath": "path to file", "filecontent_type": "optional mime type"}
        }

        if uuid:
            if not filename:
                if filepath:
                    value["filename"] = tools.path.resolve(filepath).name
                else:
                    error = "must supply {opts} when supplying 'uuid', example: {ex}"
                    error = error.format(
                        n=name, ex=ex_uuid, opts="'filename' or 'filepath'"
                    )
                    raise exceptions.ClientConfigMissingError(
                        name=name, value=value, schema=schema, error=error
                    )

            return self._config_file(value)
        else:
            if filepath:
                uploaded = self._parent.upload_file_path(
                    field=name,
                    adapter=adapter,
                    filepath=filepath,
                    filecontent_type=filecontent_type,
                )
            elif filecontent and filename:
                uploaded = self._parent.upload_file_str(
                    field=name,
                    adapter=adapter,
                    filename=filename,
                    filecontent=filecontent,
                    filecontent_type=filecontent_type,
                )
            else:
                error = [
                    "Must supply one of the following:",
                    ex_filecontent,
                    ex_filepath,
                    ex_uuid,
                ]
                error = tools.join.cr(error)
                raise exceptions.ClientConfigMissingError(
                    name=name, value=value, schema=schema, error=error
                )

            return self._config_file(uploaded)

    def _config_type_check(self, name, value, type_cb, schema):
        """Pass."""
        required = schema["required"]
        pre = "{req} setting {n!r} with value {v!r}"
        pre = pre.format(req="Required" if required else "Optional", n=name, v=value)

        if not type_cb(value):
            error = "is invalid type {st!r}"
            error = error.format(st=type(value).__name__)
            raise exceptions.ClientConfigInvalidTypeError(
                name=name, value=value, schema=schema, error=error
            )

    def _validate_csv(
        self, filename, filecontent, is_users=False, is_installed_sw=False
    ):
        """Pass."""
        if is_users:
            ids = self.CSV_FIELDS["user"]
            ids_type = "user"
        elif is_installed_sw:
            ids = self.CSV_FIELDS["sw"]
            ids_type = "installed software"
        else:
            ids = self.CSV_FIELDS["device"]
            ids_type = "device"

        headers_content = filecontent
        if tools.is_type.bytes(headers_content):
            headers_content = headers_content.decode()

        headers = headers_content.splitlines()[0].lower().split(",")
        headers_has_any_id = any([x in headers for x in ids])

        if not headers_has_any_id:
            msg = "No {ids_type} identifiers {ids} found in CSV file {name} headers {h}"
            msg = msg.format(ids_type=ids_type, ids=ids, name=filename, h=headers)
            warnings.warn(msg, exceptions.ApiWarning)

    @staticmethod
    def _build_known(clients):
        """Pass."""
        tmpl = [
            "Adapter {adapter!r}",
            "id {client_id!r}",
            "uuid {uuid!r}",
            "status {status_bool}",
        ]
        tmpl = tools.join.comma(tmpl)
        return [tmpl.format(**c) for c in clients]

    def get(self, adapter, node="master"):
        """Get all clients for an adapter."""
        if tools.is_type.str(adapter):
            adapter = self._parent.get_single(name=adapter, node=node)
            clients = adapter["clients"]
        elif tools.is_type.los(adapter):
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_names(
                adapters=all_adapters, names=adapter
            )
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, nodes=node
            )
            clients = [c for a in all_adapters for c in a]
        elif tools.is_type.none(adapter):
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, nodes=node
            )
            clients = [c for a in all_adapters for c in a]
        else:
            clients = adapter["clients"]
        return clients

    def filter_by_ids(
        self,
        clients,
        ids=None,
        use_regex=False,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Get all clients for all adapters."""
        matches = []

        for client in clients:
            match = tools.values_match(
                checks=ids, values=client["client_id"], use_regex=use_regex
            )

            if match and client not in matches:
                matches.append(client)

        self._parent._check_counts(
            value=ids,
            value_type="client ids and regex {}".format(use_regex),
            objtype="adapter clients",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(clients),
            error=count_error,
        )

        return matches

    def filter_by_uuids(
        self,
        clients,
        uuids=None,
        use_regex=False,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Get all clients for all adapters."""
        matches = []

        for client in clients:
            match = tools.values_match(
                checks=uuids, values=client["uuid"], use_regex=use_regex
            )

            if match and client not in matches:
                matches.append(client)

        self._parent._check_counts(
            value=uuids,
            value_type="uuids and regex {}".format(use_regex),
            objtype="adapter clients",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(clients),
            error=count_error,
        )

        return matches

    def filter_by_status(
        self, clients, status=None, count_min=None, count_max=None, count_error=True
    ):
        """Get all clients for all adapters."""
        matches = []

        for client in clients:
            match = True

            if client["status_bool"] is True and status is False:
                match = False

            if client["status_bool"] is False and status is True:
                match = False

            if match and client not in matches:
                matches.append(client)

        self._parent._check_counts(
            value=status,
            value_type="by status",
            objtype="adapter clients",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(clients),
            error=count_error,
        )

        return matches

    def delete(
        self,
        clients,
        delete_entities=False,
        force=False,
        warning=True,
        error=True,
        sleep=5,
    ):
        """Pass."""
        clients = tools.listify(clients, dictkeys=False)

        delmode = "client and {} entities of".format("ALL" if delete_entities else "NO")

        done = []

        for client in clients:
            dinfo = {
                "adapter": client["adapter"],
                "node_name": client["node_name"],
                "client_id": client["client_id"],
                "client_uuid": client["uuid"],
                "client_status": client["status_bool"],
            }

            pinfo = ["{}: {!r}".format(k, v) for k, v in dinfo.items()]
            pstr = tools.join.comma(pinfo).format(**client)

            if not force:
                emsg = "Must supply force=True to {d}: {p}"
                emsg = emsg.format(d=delmode, p=pstr)
                raise exceptions.ClientDeleteForceFalse(emsg)

            if warning:
                wmsg = "In {s} seconds will delete {d} {p}"
                wmsg = wmsg.format(s=sleep, d=delmode, p=pstr)
                warnings.warn(wmsg, exceptions.ClientDeleteWarning)

            dargs = {
                "adapter_name": client["adapter_raw"],
                "node_id": client["node_id"],
                "client_id": client["uuid"],
                "delete_entities": delete_entities,
            }

            dpa = "{d} {p} using args: {a}"
            dpa = dpa.format(d=delmode, p=pstr, a=dargs)

            lmsg = "About to delete {dpa}"
            lmsg = lmsg.format(dpa=dpa)
            self._log.info(lmsg)

            time.sleep(sleep)

            result = self._delete(**dargs)

            had_error = tools.is_type.dict(result) and (
                result["status"] == "error" or result["error"]
            )

            lmsg = "Finished deleting {dpa} - had error {he} with return {r}"
            lmsg = lmsg.format(dpa=dpa, he=had_error, r=result)
            self._log.info(lmsg)

            dmsg = "{s} {d} {p}, error: {e}"
            dmsg = dmsg.format(
                s="Failed to delete" if had_error else "Successfully deleted",
                d=delmode,
                p=pstr,
                e=("\n" + tools.json.re_load(result)) if result else None,
            )

            dinfo["delete_success"] = not had_error
            dinfo["delete_msg"] = dmsg

            done.append(dinfo)

            if had_error:
                if warning and not error:
                    warnings.warn(dmsg, exceptions.ClientDeleteWarning)
                elif error:
                    raise exceptions.ClientDeleteFailure(dmsg)

        return done

    def _check_connect_error(self, adapter, node, check_bool, response, error=True):
        """Pass."""
        if error and check_bool:
            raise exceptions.ClientConnectFailure(
                response=response, adapter=adapter, node=node
            )

    def check(self, clients, error=True):
        """Pass."""
        clients = tools.listify(clients, dictkeys=False)
        results = []

        for client in clients:
            checked = self._check(
                adapter_name=client["adapter_raw"],
                config=client["client_config"],
                node_id=client["node_id"],
            )

            self._check_connect_error(
                adapter=client["adapter"],
                node=client["node_name"],
                check_bool=checked,
                response=checked,
                error=error,
            )

            result = {
                "adapter": client["adapter"],
                "node": client["node_name"],
                "status": not bool(checked),
                "response": tools.json.re_load(checked),
            }

            results.append(result)

        return results

    def start_discovery(self, clients, error=True):
        """Pass."""
        clients = tools.listify(clients, dictkeys=False)
        results = []

        for client in clients:
            started = self._add(
                adapter_name=client["adapter_raw"],
                config=client["client_config"],
                node_id=client["node_id"],
            )

            self._check_connect_error(
                adapter=client["adapter"],
                node=client["node_name"],
                check_bool=started["status"] == "error" or started["error"],
                response=started,
                error=error,
            )

            result = {
                "adapter": client["adapter"],
                "node": client["node_name"],
                "status": not bool(started),
                "response": tools.json.re_load(started),
            }

            results.append(result)

        return results

    def add(self, adapter, config, node="master", error=True, adapters=None):
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
        if tools.is_type.str(adapter):
            adapter = self._parent.get_single(
                name=adapter, node=node, adapters=adapters
            )

        parsed_config = self._config_parse(
            adapter=adapter, settings_client=adapter["settings_clients"], config=config
        )

        added = self._add(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            config=parsed_config,
        )

        self._check_connect_error(
            adapter=adapter["name"],
            node=adapter["node_name"],
            check_bool=added["status"] == "error" or added["error"],
            response=added,
            error=error,
        )

        # new clients don't always show up right away, so we wait a sec
        time.sleep(1)

        clients = self.get(adapter=adapter["name"], node=adapter["node_name"])
        found = self.filter_by_uuids(
            clients=clients, uuids=added["id"], count_min=1, count_max=1
        )
        return found[0]

    def add_csv_str(
        self,
        filename,
        filecontent,
        fieldname,
        node="master",
        is_users=False,
        is_installed_sw=False,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(name="csv", node=node)

        self._validate_csv(
            filename=filename,
            filecontent=filecontent,
            is_users=is_users,
            is_installed_sw=is_installed_sw,
        )

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = fieldname
        config["csv"] = {}
        config["csv"]["filename"] = filename
        config["csv"]["filecontent"] = filecontent
        config["csv"]["filecontent_type"] = "text/csv"

        return self.add(adapter=adapter, config=config, error=error)

    def add_csv_file(
        self,
        filepath,
        fieldname,
        node="master",
        is_users=False,
        is_installed_sw=False,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(name="csv", node=node)

        filename, filecontent = self._parent._load_filepath(filepath)

        self._validate_csv(
            filename=filename,
            filecontent=filecontent,
            is_users=is_users,
            is_installed_sw=is_installed_sw,
        )

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = fieldname
        config["csv"] = {}
        config["csv"]["filename"] = filename
        config["csv"]["filecontent"] = filecontent
        config["csv"]["filecontent_type"] = "text/csv"

        return self.add(adapter=adapter, config=config, error=error)

    def add_csv_url(
        self,
        url,
        fieldname,
        node="master",
        is_users=False,
        is_installed_sw=False,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(name="csv", node=node)

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = fieldname
        config["csv_http"] = url

        return self.add(adapter=adapter, config=config, error=error)

    def add_csv_share(
        self,
        share,
        fieldname,
        node="master",
        is_users=False,
        is_installed_sw=False,
        share_username=None,
        share_password=None,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(name="csv", node=node)

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = fieldname
        config["csv_share"] = share
        if share_username:
            config["csv_share_username"] = share_username
        if share_password:
            config["csv_share_password"] = share_password
        return self.add(adapter=adapter, config=config, error=error)


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

    def _upload_file(
        self,
        adapter_name,
        node_id,
        filename,
        field,
        filecontent,
        filecontent_type=None,
        fileheaders=None,
    ):
        """Pass."""
        data = {"field_name": field}
        files = {"userfile": (filename, filecontent, filecontent_type, fileheaders)}

        path = self._router.upload_file.format(
            adapter_name=adapter_name, node_id=node_id
        )

        ret = self._request(method="post", path=path, data=data, files=files)
        ret["filename"] = filename
        return ret

    @staticmethod
    def _load_filepath(filepath):
        """Pass."""
        rpath = tools.path.resolve(filepath)

        if not rpath.is_file():
            msg = "Supplied filepath='{fp}' (resolved='{rp}') does not exist!"
            msg = msg.format(fp=filepath, rp=rpath)
            raise exceptions.ApiError(msg)

        filecontent = rpath.read_bytes()
        filename = rpath.name
        return filename, filecontent

    @staticmethod
    def _build_known(adapters):
        """Pass."""
        tmpl = ["name: {name!r}", "node name {node_name!r}", "clients {client_count}"]
        tmpl = tools.join.comma(tmpl)
        return [tmpl.format(**a) for a in adapters]

    def get(self):
        """Pass."""
        raw = self._get()
        parser = ParserAdapters(raw=raw, parent=self)
        adapters = parser.parse()
        return adapters

    def get_single(self, name, node="master", adapters=None):
        """Pass."""
        adapters = self.get()
        adapters = self.filter_by_names(
            names=name, count_min=1, count_max=1, adapters=adapters
        )
        adapters = self.filter_by_nodes(
            nodes=node, count_min=1, count_max=1, adapters=adapters
        )
        return adapters[0]

    def filter_by_names(
        self,
        adapters,
        names,
        use_regex=False,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Pass."""
        names = [tools.strip.right(name, "_adapter") for name in tools.listify(names)]

        matches = []

        for adapter in adapters:
            match = tools.values_match(
                checks=names, values=adapter["name"], use_regex=use_regex
            )

            if match and adapter not in matches:
                matches.append(adapter)

        self._check_counts(
            value=names,
            value_type="adapter by names using regex {}".format(use_regex),
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(adapters),
            error=count_error,
        )

        return matches

    def filter_by_nodes(
        self,
        adapters,
        nodes,
        use_regex=True,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Pass."""
        matches = []

        for adapter in adapters:
            match = tools.values_match(
                checks=nodes, values=adapter["node_name"], use_regex=use_regex
            )

            if match and adapter not in matches:
                matches.append(adapter)

        self._check_counts(
            value=nodes,
            value_type="adapter by node names using regex {}".format(use_regex),
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(adapters),
            error=count_error,
        )

        return matches

    def filter_by_client_count(
        self,
        adapters,
        client_min=None,
        client_max=None,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Pass."""
        known = []
        matches = []

        for adapter in adapters:
            known_str = (
                "name: {name!r}, node name {node_name!r}, client count: {client_count}"
            )
            known_str = known_str.format(**adapter)

            if known_str not in known:
                known.append(known_str)

            if client_min is not None and not adapter["client_count"] >= client_min:
                continue
            if client_max == 0 and not adapter["client_count"] == 0:
                continue
            if client_max is not None and not adapter["client_count"] <= client_max:
                continue

            matches.append(adapter)

        values = [
            "client_min: {}".format(client_min),
            "client_max: {}".format(client_max),
        ]
        self._check_counts(
            value=values,
            value_type="adapter by client count",
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=known,
            error=count_error,
        )

        return matches

    def filter_by_status(
        self, adapters, status=None, count_min=None, count_max=None, count_error=True
    ):
        """Pass."""
        known = []
        matches = []

        for adapter in adapters:
            known_str = "name: {name!r}, node name {node_name!r}, status: {status_bool}"
            known_str = known_str.format(**adapter)

            if known_str not in known:
                known.append(known_str)

            if adapter["status_bool"] is True and status is True:
                matches.append(adapter)
            elif adapter["status_bool"] is False and status is False:
                matches.append(adapter)
            elif adapter["status_bool"] is None and status is None:
                matches.append(adapter)

        self._check_counts(
            value=status,
            value_type="adapter by client count",
            objtype=self._router._object_type,
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=known,
            error=count_error,
        )

        return matches

    def upload_file_str(
        self,
        adapter,
        field,
        filename,
        filecontent,
        filecontent_type=None,
        node="master",
        adapters=None,
    ):
        """Pass."""
        if tools.is_type.str(adapter):
            adapter = self.get_single(name=adapter, node=node, adapters=adapters)

        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            filename=filename,
            field=field,
            filecontent=filecontent,
            filecontent_type=filecontent_type,
        )

    def upload_file_path(
        self,
        adapter,
        field,
        filepath,
        filecontent_type=None,
        node="master",
        adapters=None,
    ):
        """Pass."""
        if tools.is_type.str(adapter):
            adapter = self.get_single(name=adapter, node=node, adapters=adapters)

        filename, filecontent = self._load_filepath(filepath)
        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            filename=filename,
            field=field,
            filecontent=filecontent,
            filecontent_type=filecontent_type,
        )


class ParserAdapters(mixins.Parser):
    """Pass."""

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
            if ((is_base and base) or (not is_base and not base)) and not settings:
                schema = raw_settings["schema"]
                items = schema["items"]
                required = schema["required"]
                config = raw_settings["config"]

                for item in items:
                    setting_name = item["name"]
                    parsed_settings = {k: v for k, v in item.items()}
                    parsed_settings["required"] = setting_name in required
                    parsed_settings["value"] = config.get(setting_name, None)
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
                value = raw_config.get(setting_name, None)
                parsed_settings[setting_name] = setting_config.copy()
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
            parsed_client["client_config"] = raw_config
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
