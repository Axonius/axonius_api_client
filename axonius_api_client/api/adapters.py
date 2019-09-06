# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import pdb  # noqa
import time
import warnings

from .. import constants, exceptions, tools
from . import mixins, routers


class Adapters(mixins.Model, mixins.Mixins):
    """Adapter related API methods."""

    def _init(self, auth, **kwargs):
        """Pass."""
        # children
        self.cnx = Cnx(parent=self)

        super(Adapters, self)._init(auth=auth, **kwargs)

    @staticmethod
    def _build_known(adapters):
        """Pass."""
        tmpl = ["name: {name!r}", "node name {node_name!r}", "connections {cnx_count}"]
        tmpl = tools.join.comma(tmpl)
        return [tmpl.format(**a) for a in adapters]

    def _get(self):
        """Get all adapters.

        Returns:
            :obj:`dict`

        """
        return self._request(method="get", path=self._router.root)

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

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.adapters

    def _upload_file(
        self,
        adapter_name,
        node_id,
        name,
        field,
        content,
        content_type=None,
        headers=None,
    ):
        """Pass."""
        data = {"field_name": field}
        files = {"userfile": (name, content, content_type, headers)}

        path = self._router.upload_file.format(
            adapter_name=adapter_name, node_id=node_id
        )

        ret = self._request(method="post", path=path, data=data, files=files)
        ret["filename"] = name
        return ret

    def get(self):
        """Pass."""
        raw = self._get()
        parser = ParserAdapters(raw=raw, parent=self)
        adapters = parser.parse()
        return adapters

    def get_single(self, adapter, node="master"):
        """Pass."""
        if tools.is_type.dict(adapter):
            return adapter

        adapters = self.get()
        adapters = self.filter_by_names(
            names=adapter, count_min=1, count_max=1, count_error=True, adapters=adapters
        )
        adapters = self.filter_by_nodes(
            nodes=node, count_min=1, count_max=1, count_error=True, adapters=adapters
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
        self, adapter, field, name, content, node="master", content_type=None
    ):
        """Pass."""
        adapter = self.get_single(adapter=adapter, node=node)

        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            name=name,
            field=field,
            content=content,
            content_type=content_type,
        )

    def upload_file_path(self, adapter, field, path, node="master", content_type=None):
        """Pass."""
        adapter = self.get_single(adapter=adapter, node=node)

        name, content = self._load_filepath(path)

        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            name=name,
            field=field,
            content=content,
            content_type=content_type,
        )


class Cnx(mixins.Child):
    """Pass."""

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

    @staticmethod
    def _build_known(cnxs):
        """Pass."""
        tmpl = [
            "Adapter: {adapter_name!r}",
            "ID: {id!r}",
            "UUID: {uuid!r}",
            "Status: {status}",
        ]
        tmpl = tools.join.comma(tmpl)
        return [tmpl.format(**c) for c in cnxs]

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

    def _update(self, adapter_name, node_id, config, cnx_uuid):
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
        data["oldInstanceName"] = node_id

        path = self._parent._router.cnxs_uuid.format(
            adapter_name=adapter_name, cnx_uuid=cnx_uuid
        )
        return self._parent._request(
            method="put",
            path=path,
            json=data,
            error_json_bad_status=False,
            error_code_not_200=False,
        )

    def add(
        self,
        adapter,
        config,
        parse_config=True,
        node="master",
        retry=15,
        sleep=15,
        error=True,
    ):
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
        adapter = self._parent.get_single(adapter=adapter, node=node)

        if parse_config:
            parser = ParserCnxConfig(raw=config, parent=self)
            config = parser.parse(adapter=adapter, settings=adapter["cnx_settings"])

        response = self._add(
            adapter_name=adapter["name_raw"], node_id=adapter["node_id"], config=config
        )

        had_error = response["status"] == "error" or response["error"]
        if had_error and error:
            raise exceptions.CnxConnectFailure(
                response=response, adapter=adapter["name"], node=adapter["node_name"]
            )

        refetched = {}
        refetched["response_had_error"] = had_error
        refetched["response"] = response
        refetched["cnx"] = self.refetch(
            adapter_name=adapter["name"],
            node_name=adapter["node_name"],
            response=response,
            retry=retry,
            sleep=sleep,
            uuid=response["id"],
            id=None,
        )

        return refetched

    def add_csv_str(
        self,
        name,
        content,
        field,
        node="master",
        is_users=False,
        is_installed_sw=False,
        parse_config=True,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(adapter="csv", node=node)

        validate_csv(
            name=name,
            content=content,
            is_users=is_users,
            is_installed_sw=is_installed_sw,
        )

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = field
        config["csv"] = {}
        config["csv"]["filename"] = name
        config["csv"]["filecontent"] = content
        config["csv"]["filecontent_type"] = "text/csv"

        return self.add(
            adapter=adapter,
            config=config,
            parse_config=parse_config,
            retry=retry,
            sleep=sleep,
            error=error,
        )

    def add_csv_file(
        self,
        path,
        field,
        node="master",
        is_users=False,
        is_installed_sw=False,
        parse_config=True,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(adapter="csv", node=node)

        name, content = self._parent._load_filepath(path)

        validate_csv(
            name=name,
            content=content,
            is_users=is_users,
            is_installed_sw=is_installed_sw,
        )

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = field
        config["csv"] = {}
        config["csv"]["filename"] = name
        config["csv"]["filecontent"] = content
        config["csv"]["filecontent_type"] = "text/csv"

        return self.add(
            adapter=adapter,
            config=config,
            parse_config=parse_config,
            retry=retry,
            sleep=sleep,
            error=error,
        )

    def add_csv_url(
        self,
        url,
        field,
        node="master",
        is_users=False,
        is_installed_sw=False,
        parse_config=True,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(adapter="csv", node=node)

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = field
        config["csv_http"] = url

        return self.add(
            adapter=adapter,
            config=config,
            parse_config=parse_config,
            retry=retry,
            sleep=sleep,
            error=error,
        )

    def add_csv_share(
        self,
        share,
        field,
        node="master",
        is_users=False,
        is_installed_sw=False,
        username=None,
        password=None,
        parse_config=True,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Pass."""
        adapter = self._parent.get_single(adapter="csv", node=node)

        config = {}
        config["is_users_csv"] = is_users
        config["is_installed_sw"] = is_installed_sw
        config["user_id"] = field
        config["csv_share"] = share
        if username:
            config["csv_share_username"] = username
        if password:
            config["csv_share_password"] = password

        return self.add(
            adapter=adapter,
            config=config,
            parse_config=parse_config,
            retry=retry,
            sleep=sleep,
            error=error,
        )

    def check(self, cnx, retry=15, sleep=15, error=True):
        """Pass."""
        response = self._check(
            adapter_name=cnx["adapter_name_raw"],
            config=cnx["config_raw"],
            node_id=cnx["node_id"],
        )

        had_error = bool(response)

        if had_error and error:
            raise exceptions.CnxConnectFailure(
                response=response, adapter=cnx["adapter_name"], node=cnx["node_name"]
            )

        refetched = {}
        refetched["response_had_error"] = had_error
        refetched["response"] = response
        refetched["cnx"] = self.refetch(
            adapter_name=cnx["adapter_name"],
            node_name=cnx["node_name"],
            response=response,
            retry=retry,
            sleep=sleep,
            uuid=None,
            id=cnx["id"],
        )

        return refetched

    def delete(
        self,
        cnx,
        delete_entities=False,
        force=False,
        warning=True,
        error=True,
        sleep=15,
    ):
        """Pass."""
        cnxinfo = [
            "Adapter name: {adapter_name}",
            "Node name: {node_name}",
            "Connection ID: {id}",
            "Connection UUID: {uuid}",
            "Connection status: {status}",
            "Delete all entities: {de}",
        ]
        cnxinfo = tools.join.cr(cnxinfo).format(de=delete_entities, **cnx)

        if not force:
            raise exceptions.CnxDeleteForce(cnxinfo=cnxinfo)

        if warning:
            warnings.warn(exceptions.CnxDeleteWarning(cnxinfo=cnxinfo, sleep=sleep))

        dargs = {
            "adapter_name": cnx["adapter_name_raw"],
            "node_id": cnx["node_id"],
            "cnx_uuid": cnx["uuid"],
            "delete_entities": delete_entities,
        }

        lsmsg = [
            "Connection info: {cnxinfo}",
            "About to delete connection in {s} seconds using args: {a}",
        ]
        lsmsg = tools.join.cr(lsmsg).format(cnxinfo=cnxinfo, s=sleep, a=dargs)
        self._log.info(lsmsg)

        time.sleep(sleep)

        response = self._delete(**dargs)

        had_error = tools.is_type.dict(response) and (
            response["status"] == "error" or response["error"]
        )

        lfmsg = [
            "Connection info: {cnxinfo}",
            "Deleted connection with error {he} and return {r}",
        ]
        lfmsg = tools.join.cr(lfmsg).format(cnxinfo=cnxinfo, he=had_error, r=response)
        self._log.info(lfmsg)

        if had_error:
            if warning and not error:
                warnings.warn(
                    exceptions.CnxDeleteFailedWarning(
                        cnxinfo=cnxinfo, response=response
                    )
                )
            elif error:
                raise exceptions.CnxDeleteFailed(cnxinfo=cnxinfo, response=response)

        ret = {}
        ret["response_had_error"] = had_error
        ret["response"] = response
        ret["cnx"] = cnx

        return ret

    def get(self, adapter, node="master"):
        """Get all connections for an adapter."""
        if tools.is_type.lostr(adapter):
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
            return [c for a in all_adapters for c in a["cnx"]]

        adapter = self._parent.get_single(adapter=adapter, node=node)
        return adapter["cnx"]

    def refetch(self, adapter_name, node_name, response, uuid, id, retry=15, sleep=15):
        """Pass."""
        count = 0

        # new connections don't always show up right away, so we have to do some magic
        while count < retry:
            # re-fetch all connections for this adapter
            # try to find the newly created connection
            cnxs = self.get(adapter=adapter_name, node=node_name)
            cnxs = self.filter_by_uuids(cnxs=cnxs, uuids=uuid, count_error=False)
            cnxs = self.filter_by_ids(cnxs=cnxs, ids=id, count_error=False)

            if len(cnxs) == 1:
                return cnxs[0]

            count += 1

            dmsg = [
                "Connection not in system yet",
                "try {c} of {r}",
                "sleeping another {s} seconds",
                "Looking for connection: {response}",
            ]
            dmsg = tools.join.comma(dmsg).format(
                response=response, c=count, r=retry, s=sleep
            )
            self._log.debug(dmsg)

            time.sleep(sleep)

        raise exceptions.CnxRefetchFailure(
            response=response, adapter=adapter_name, node=node_name
        )

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

    def update(
        self, cnx, new_config=None, parse_config=True, retry=15, sleep=15, error=True
    ):
        """Pass."""
        if parse_config and new_config:
            adapter = self._parent.get_single(adapter=cnx["adapter_name"])
            parser = ParserCnxConfig(raw=new_config, parent=self)
            new_config = parser.parse(adapter=adapter, settings=adapter["cnx_settings"])

        response = self._update(
            adapter_name=cnx["adapter_name_raw"],
            node_id=cnx["node_id"],
            config=new_config or cnx["config_raw"],
            cnx_uuid=cnx["uuid"],
        )

        had_error = response["status"] == "error" or response["error"]

        if had_error and error:
            raise exceptions.CnxConnectFailure(
                response=response, adapter=cnx["adapter_name"], node=cnx["node_name"]
            )

        refetched = {}
        refetched["response_had_error"] = had_error
        refetched["response"] = response
        refetched["cnx"] = self.refetch(
            adapter_name=cnx["adapter_name"],
            node_name=cnx["node_name"],
            response=response,
            retry=retry,
            sleep=sleep,
            uuid=response["id"],
            id=None,
        )

        return refetched


class ParserCnxConfig(mixins.Parser):
    """Pass."""

    SETTING_TYPES = {
        "bool": tools.is_type.bool,
        "number": tools.is_type.str_int,
        "integer": tools.is_type.str_int,
        "array": tools.is_type.lostr,
        "string": tools.is_type.str,
    }

    def check_value(self, name, value, schema, adapter):
        """Pass."""
        type_str = schema["type"]
        enum = schema.get("enum", [])

        if value == constants.SETTING_UNCHANGED:
            return value

        if enum and value not in enum:
            raise exceptions.CnxSettingInvalidChoice(
                name=name, value=value, schema=schema, enum=enum, adapter=adapter
            )

        if type_str == "file":
            if not tools.is_type.dict(value):
                raise exceptions.CnxSettingInvalidType(
                    name=name,
                    value=value,
                    schema=schema,
                    mustbe="dict",
                    adapter=adapter,
                )

            return self.parse_file(
                name=name, value=value, schema=schema, adapter=adapter
            )

        if type_str in self.SETTING_TYPES:
            type_cb = self.SETTING_TYPES[type_str]

            if not type_cb(value):
                raise exceptions.CnxSettingInvalidType(
                    name=name,
                    value=value,
                    schema=schema,
                    adapter=adapter,
                    mustbe=type_str,
                )
            return value

        raise exceptions.CnxSettingUnknownType(
            name=name, value=value, schema=schema, type_str=type_str, adapter=adapter
        )

    def parse(self, adapter, settings):
        """Pass."""
        new_config = {}

        for name, schema in settings.items():
            required = schema["required"]

            value = self._raw.get(name, None)

            has_value = name in self._raw
            has_default = "default" in schema

            req = "required" if required else "optional"
            msg = "Processing {req} setting {n!r} with value of {v!r}, schema: {ss}"
            msg = msg.format(req=req, n=name, v=value, ss=schema)
            self._log.debug(msg)

            if not has_value and not has_default:
                if not required:
                    continue

                raise exceptions.CnxSettingMissing(
                    name=name, value=value, schema=schema, adapter=adapter
                )

            if not has_value and has_default:
                value = schema["default"]

            new_config[name] = self.check_value(
                name=name, value=value, schema=schema, adapter=adapter
            )

        return new_config

    def parse_file(self, name, value, schema, adapter):
        """Pass."""
        uuid = value.get("uuid", None)
        filename = value.get("filename", None)
        filepath = value.get("filepath", None)
        filecontent = value.get("filecontent", None)
        filecontent_type = value.get("filecontent_type", None)

        if uuid and filename:
            return {"uuid": uuid, "filename": filename}

        # TODO: try here
        if filepath:
            uploaded = self._parent._parent.upload_file_path(
                field=name,
                adapter=adapter,
                path=filepath,
                content_type=filecontent_type,
            )

            return {"uuid": uploaded["uuid"], "filename": uploaded["filename"]}

        if filecontent and filename:
            uploaded = self._parent._parent.upload_file_str(
                field=name,
                adapter=adapter,
                name=filename,
                content=filecontent,
                content_type=filecontent_type,
            )
            return {"uuid": uploaded["uuid"], "filename": uploaded["filename"]}

        raise exceptions.CnxSettingFileMissing(
            name=name, value=value, schema=schema, adapter=adapter
        )


class ParserAdapters(mixins.Parser):
    """Pass."""

    def _adapter(self, name, raw):
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

    def _cnx(self, raw, parent):
        """Pass."""
        cnx = []

        cnx_settings = self._cnx_settings(raw=raw)

        for raw_cnx in raw["clients"]:
            raw_config = raw_cnx["client_config"]
            parsed_settings = {}

            for setting_name, setting_config in cnx_settings.items():
                value = raw_config.get(setting_name, None)

                if value == constants.SETTING_UNCHANGED:
                    value = "__HIDDEN__"

                if setting_name not in raw_config:
                    value = "__NOTSET__"

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
                adapter = self._adapter(name=name, raw=raw)
                parsed.append(adapter)

        return parsed


def validate_csv(name, content, is_users=False, is_installed_sw=False):
    """Pass."""
    if is_users:
        ids = constants.CSV_FIELDS["user"]
        ids_type = "user"
    elif is_installed_sw:
        ids = constants.CSV_FIELDS["sw"]
        ids_type = "installed software"
    else:
        ids = constants.CSV_FIELDS["device"]
        ids_type = "device"

    headers_content = content
    if tools.is_type.bytes(headers_content):
        headers_content = headers_content.decode()

    headers = headers_content.splitlines()[0].lower().split(",")
    headers_has_any_id = any([x in headers for x in ids])

    if not headers_has_any_id:
        warnings.warn(
            exceptions.CnxCsvWarning(
                ids_type=ids_type, ids=ids, name=name, headers=headers
            )
        )


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
