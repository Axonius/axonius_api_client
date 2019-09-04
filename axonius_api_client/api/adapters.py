# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb  # noqa

import time
import warnings

from .. import exceptions, tools
from . import mixins, routers


class Cnx(mixins.Child):
    """Pass."""

    _CSV_FIELDS = {
        "device": ["id", "serial", "mac_address", "hostname", "name"],
        "user": ["id", "username", "mail", "name"],
        "sw": ["hostname", "installed_sw_name"],
    }

    _SETTING_TYPES = {
        "bool": tools.is_type.bool,
        "number": tools.is_type.str_int,
        "integer": tools.is_type.str_int,
        "array": tools.is_type.los,
        "string": tools.is_type.str,
    }

    _ADD_REFETCH_RETRY = 5
    _ADD_REFETCH_SLEEP = 1

    def _check(self, adapter_name, node_id, config):
        """Test an adapter connection.

        Args:
            name (:obj:`str`):
                Name of adapter to test connection of.
            config (:obj:`dict`):
                Connection configuration.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            :obj:`object`

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id

        path = self._parent._router.cnxs.format(adapter_name=adapter_name)

        return self._parent._request(
            method="post",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _add(self, adapter_name, node_id, config):
        """Add a connection to an adapter.

        Args:
            adapter (:obj:`str`):
                Name of adapter to add connection to.
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

        path = self._parent._router.cnxs.format(adapter_name=adapter_name)

        return self._parent._request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _delete(self, adapter_name, node_id, cnx_uuid, delete_entities=False):
        """Delete a connection from an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to delete connection from.
            id (:obj:`str`):
                ID of connection to remove.
            node_id (:obj:`str`):
                Node ID.

        Returns:
            :obj:`object`

        """
        data = {}
        data["instanceName"] = node_id

        params = {"deleteEntities": delete_entities}

        path = self._parent._router.cnxs_uuid.format(
            adapter_name=adapter_name, cnx_uuid=cnx_uuid
        )

        return self._parent._request(
            method="delete",
            path=path,
            json=data,
            params=params,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def _config_parse(self, adapter, settings, config):
        """Pass."""
        new_config = {}

        for name, schema in settings.items():
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
                raise exceptions.CnxSettingMissing(
                    name=name, value=value, schema=schema, error=error
                )

            if not has_value and has_default:
                value = schema["default"]

            if enum and value not in enum:
                error = "invalid value {value!r}, must be one of {enum}"
                error = error.format(value=value, enum=enum)
                raise exceptions.CnxSettingInvalidChoice(
                    name=name, value=value, schema=schema, error=error
                )

            if type_str == "file":
                value = self._config_file_check(
                    name=name, value=value, schema=schema, adapter=adapter
                )
            elif type_str in self._SETTING_TYPES:
                self._config_type_check(
                    name=name,
                    schema=schema,
                    value=value,
                    type_cb=self._SETTING_TYPES[type_str],
                )
            else:
                error = "Unknown setting type: {type_str!r}"
                error = error.format(type_str=type_str)
                raise exceptions.CnxSettingUnknownType(
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
                    raise exceptions.CnxSettingMissing(
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
                raise exceptions.CnxSettingMissing(
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
            raise exceptions.CnxSettingInvalidType(
                name=name, value=value, schema=schema, error=error
            )

    def _validate_csv(
        self, filename, filecontent, is_users=False, is_installed_sw=False
    ):
        """Pass."""
        if is_users:
            ids = self._CSV_FIELDS["user"]
            ids_type = "user"
        elif is_installed_sw:
            ids = self._CSV_FIELDS["sw"]
            ids_type = "installed software"
        else:
            ids = self._CSV_FIELDS["device"]
            ids_type = "device"

        headers_content = filecontent
        if tools.is_type.bytes(headers_content):
            headers_content = headers_content.decode()

        headers = headers_content.splitlines()[0].lower().split(",")
        headers_has_any_id = any([x in headers for x in ids])

        if not headers_has_any_id:
            msg = "No {ids_type} identifiers {ids} found in CSV file {name} headers {h}"
            msg = msg.format(ids_type=ids_type, ids=ids, name=filename, h=headers)
            warnings.warn(msg, exceptions.CnxCsvWarning)

    @staticmethod
    def _build_known(cnxs):
        """Pass."""
        tmpl = [
            "Adapter {adapter_name!r}",
            "id {id!r}",
            "uuid {uuid!r}",
            "status {status}",
        ]
        tmpl = tools.join.comma(tmpl)
        return [tmpl.format(**c) for c in cnxs]

    def _check_connect_error(self, adapter, node, check_bool, response, error=True):
        """Pass."""
        if error and check_bool:
            raise exceptions.CnxFailure(response=response, adapter=adapter, node=node)

    def get(self, adapter, node="master"):
        """Get all connections for an adapter."""
        if tools.is_type.str(adapter):
            adapter = self._parent.get_single(name=adapter, node=node)
            return adapter["cnx"]

        if tools.is_type.los(adapter):
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_names(
                adapters=all_adapters, names=adapter
            )
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, nodes=node
            )
            return [c for a in all_adapters for c in a["cnx"]]

        if tools.is_type.none(adapter):
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, nodes=node
            )
            return [c for a in all_adapters for c in a]
        else:
            return adapter["cnx"]

    def filter_by_ids(
        self,
        cnxs,
        ids=None,
        use_regex=False,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Get all connections for all adapters."""
        matches = []

        for cnx in cnxs:
            match = tools.values_match(
                checks=ids, values=cnx["id"], use_regex=use_regex
            )

            if match and cnx not in matches:
                matches.append(cnx)

        self._parent._check_counts(
            value=ids,
            value_type="connection ids and regex {}".format(use_regex),
            objtype="adapter connections",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(cnxs),
            error=count_error,
        )

        return matches

    def filter_by_uuids(
        self,
        cnxs,
        uuids=None,
        use_regex=False,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Get all connections for all adapters."""
        matches = []

        for cnx in cnxs:
            match = tools.values_match(
                checks=uuids, values=cnx["uuid"], use_regex=use_regex
            )

            if match and cnx not in matches:
                matches.append(cnx)

        self._parent._check_counts(
            value=uuids,
            value_type="uuids and regex {}".format(use_regex),
            objtype="adapter connections",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(cnxs),
            error=count_error,
        )

        return matches

    def filter_by_status(
        self, cnxs, status=None, count_min=None, count_max=None, count_error=True
    ):
        """Get all connections for all adapters."""
        matches = []

        for cnx in cnxs:
            match = True

            if cnx["status"] is True and status is False:
                match = False

            if cnx["status"] is False and status is True:
                match = False

            if match and cnx not in matches:
                matches.append(cnx)

        self._parent._check_counts(
            value=status,
            value_type="by status",
            objtype="adapter connections",
            count_min=count_min,
            count_max=count_max,
            count_total=len(matches),
            known=self._build_known(cnxs),
            error=count_error,
        )

        return matches

    def delete(
        self,
        cnxs,
        delete_entities=False,
        force=False,
        warning=True,
        error=True,
        sleep=5,
    ):
        """Pass."""
        cnxs = tools.listify(cnxs, dictkeys=False)

        delmode = "connection and {} entities of"
        delmode = delmode.format("ALL" if delete_entities else "NO")

        done = []

        for cnx in cnxs:
            dinfo = {
                "adapter_name": cnx["adapter_name"],
                "node_name": cnx["node_name"],
                "id": cnx["id"],
                "uuid": cnx["uuid"],
                "status": cnx["status"],
            }

            pinfo = ["{}: {!r}".format(k, v) for k, v in dinfo.items()]
            pstr = tools.join.comma(pinfo).format(**cnx)

            if not force:
                emsg = "Must supply force=True to {d}: {p}"
                emsg = emsg.format(d=delmode, p=pstr)
                raise exceptions.CnxDeleteForce(emsg)

            if warning:
                wmsg = "In {s} seconds will delete {d} {p}"
                wmsg = wmsg.format(s=sleep, d=delmode, p=pstr)
                warnings.warn(wmsg, exceptions.CnxDeleteWarning)

            dargs = {
                "adapter_name": cnx["adapter_name_raw"],
                "node_id": cnx["node_id"],
                "cnx_uuid": cnx["uuid"],
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
                    warnings.warn(dmsg, exceptions.CnxDeleteWarning)
                elif error:
                    raise exceptions.CnxDeleteFailure(dmsg)

        return done

    def check(self, cnxs, error=True):
        """Pass."""
        cnxs = tools.listify(cnxs, dictkeys=False)
        results = []

        for cnx in cnxs:
            checked = self._check(
                adapter_name=cnx["adapter_name_raw"],
                config=cnx["config_raw"],
                node_id=cnx["node_id"],
            )

            self._check_connect_error(
                adapter=cnx["adapter_name"],
                node=cnx["node_name"],
                check_bool=checked,
                response=checked,
                error=error,
            )

            result = {
                "adapter_name": cnx["adapter_name"],
                "node_name": cnx["node_name"],
                "status": not bool(checked),
                "response": tools.json.re_load(checked),
            }

            results.append(result)

        return results

    def start_discovery(self, cnxs, error=True):
        """Pass."""
        cnxs = tools.listify(cnxs, dictkeys=False)
        results = []

        for cnx in cnxs:
            started = self._add(
                adapter_name=cnx["adapter_name_raw"],
                config=cnx["config_raw"],
                node_id=cnx["node_id"],
            )

            self._check_connect_error(
                adapter=cnx["adapter_name"],
                node=cnx["node_name"],
                check_bool=started["status"] == "error" or started["error"],
                response=started,
                error=error,
            )

            result = {
                "adapter": cnx["adapter_name"],
                "node": cnx["node_name"],
                "status": not bool(started),
                "response": tools.json.re_load(started),
            }

            results.append(result)

        return results

    def add(self, adapter, config, node="master", error=True, adapters=None):
        """Add a connection to an adapter.

        Args:
            name (:obj:`str`):
                Name of adapter to add connection to.
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
            adapter=adapter, settings=adapter["cnx_settings"], config=config
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

        # new connections don't always show up right away, so we have to do some magic
        count = 0

        while count < self._ADD_REFETCH_RETRY:
            # re-fetch all connections for this adapter
            cnxs = self.get(adapter=adapter["name"], node=adapter["node_name"])

            # try to find the newly created connection
            found = self.filter_by_uuids(
                cnxs=cnxs,
                uuids=added["id"],
                count_min=1,
                count_max=1,
                count_error=count >= self._ADD_REFETCH_RETRY,
            )

            if len(found) == 1:
                return found[0]
            else:  # pragma: no cover
                # not always triggered, so ignore test coverage
                dmsg = "Added connection {added} not in system yet, try {c} of {r}"
                dmsg = dmsg.format(added=added, c=count, r=self._ADD_REFETCH_RETRY)
                self._log.debug(dmsg)

                count += 1

                time.sleep(self._ADD_REFETCH_SLEEP)

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
        # children
        self.cnx = Cnx(parent=self)

        super(Adapters, self)._init(auth=auth, **kwargs)

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
        tmpl = ["name: {name!r}", "node name {node_name!r}", "connections {cnx_count}"]
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

    def filter_by_cnx_count(
        self,
        adapters,
        cnx_min=None,
        cnx_max=None,
        count_min=None,
        count_max=None,
        count_error=True,
    ):
        """Pass."""
        known = []
        matches = []

        for adapter in adapters:
            known_str = [
                "name: {name!r}",
                "node name {node_name!r}",
                "connection counts: {cnx_count}",
            ]
            known_str = tools.join.comma(known_str).format(**adapter)

            if known_str not in known:
                known.append(known_str)

            if cnx_min is not None and not adapter["cnx_count"] >= cnx_min:
                continue
            if cnx_max == 0 and not adapter["cnx_count"] == 0:
                continue
            if cnx_max is not None and not adapter["cnx_count"] <= cnx_max:
                continue

            matches.append(adapter)

        values = ["cnx_min: {}".format(cnx_min), "cnx_max: {}".format(cnx_max)]
        self._check_counts(
            value=values,
            value_type="adapter by connection count",
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
            known_str = "name: {name!r}, node name {node_name!r}, status: {status}"
            known_str = known_str.format(**adapter)

            if known_str not in known:
                known.append(known_str)

            if adapter["status"] is True and status is True:
                matches.append(adapter)
            elif adapter["status"] is False and status is False:
                matches.append(adapter)
            elif adapter["status"] is None and status is None:
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
            "status_raw": raw["status"],
            "features": raw["supported_features"],
        }

        if parsed["status_raw"] == "success":
            parsed["status"] = True
        elif parsed["status_raw"] == "warning":
            parsed["status"] = False
        else:
            parsed["status"] = None

        cnx = self._cnx(raw=raw, parent=parsed)
        cnx_ok = [x for x in cnx if x["status"] is True]
        cnx_bad = [x for x in cnx if x["status"] is False]

        parsed["cnx"] = cnx
        parsed["cnx_ok"] = cnx_ok
        parsed["cnx_bad"] = cnx_bad
        parsed["cnx_settings"] = self._cnx_settings(raw=raw)
        parsed["cnx_count"] = len(cnx)
        parsed["cnx_count_ok"] = len(cnx_ok)
        parsed["cnx_count_bad"] = len(cnx_bad)
        parsed["settings"] = self._adapter_settings(raw=raw, base=False)
        parsed["adv_settings"] = self._adapter_settings(raw=raw, base=True)

        return parsed

    def _cnx_settings(self, raw):
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

    def _adapter_settings(self, raw, base=True):
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

    def _cnx(self, raw, parent):
        """Pass."""
        cnx = []

        cnx_settings = self._cnx_settings(raw=raw)

        for raw_cnx in raw["clients"]:
            raw_config = raw_cnx["client_config"]
            parsed_settings = {}

            for setting_name, setting_config in cnx_settings.items():
                value = raw_config.get(setting_name, None)
                parsed_settings[setting_name] = setting_config.copy()
                parsed_settings[setting_name]["value"] = value

            pcnx = {}
            pcnx["node_name"] = parent["node_name"]
            pcnx["node_id"] = parent["node_id"]
            pcnx["adapter_name"] = parent["name"]
            pcnx["adapter_name_raw"] = parent["name_raw"]
            pcnx["adapter_status"] = parent["status"]
            pcnx["config"] = parsed_settings
            pcnx["config_raw"] = raw_config
            pcnx["status_raw"] = raw_cnx["status"]
            pcnx["status"] = raw_cnx["status"] == "success"
            pcnx["id"] = raw_cnx["client_id"]
            pcnx["uuid"] = raw_cnx["uuid"]
            pcnx["date_fetched"] = raw_cnx["date_fetched"]
            pcnx["error"] = raw_cnx["error"]
            cnx.append(pcnx)

        return cnx

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
