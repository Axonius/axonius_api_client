# -*- coding: utf-8 -*-
"""API models for working with adapters and connections."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import re
import time
import warnings

from .. import constants, exceptions, tools
from . import mixins, routers


class Adapters(mixins.Model, mixins.Mixins):
    """API model for working with adapters."""

    def get(self):
        """Get the metadata for all adapters.

        Returns:
            (:obj:`list` of :obj:`dict`): list of metadata for all adapters
            parsed using :obj:`ParserAdapters`

        """
        raw = self._get()
        parser = ParserAdapters(raw=raw, parent=self)
        adapters = parser.parse()
        return adapters

    def get_known(self, adapters=None, **kwargs):
        """Get str descriptors of known/valid adapters.

        Args:
            adapters (:obj:`list` of :obj:`dict`, optional): default :meth:`get` -
                list of adapters to include in return

        Returns:
            :obj:`list` of :obj:`str`: list of str describing each adapter

        """
        adapters = adapters or self.get()
        tmpl = [
            "name: {name!r}",
            "node name: {node_name!r}",
            "cnx count: {cnx_count}",
            "status: {status}",
        ]
        tmpl = tools.join_comma(obj=tmpl).format
        return [tmpl(**a) for a in adapters]

    def get_single(self, adapter, node=constants.DEFAULT_NODE):
        """Get metadata for a single adapter.

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to get the metadata for
                * If :obj:`dict`, the metadata for a previously fetched adapter
            node (:obj:`str`, optional): default
                :data:`.constants.DEFAULT_NODE` -
                if str supplied to **adapter**, find an adapter running on this node name

        Raises:
            :exc:`.exceptions.ValueNotFound`: if **adapter** is str and no adapter by
                that name found on supplied **node**

        Returns:
            :obj:`dict`: metadata for a single adapter
        """
        if isinstance(adapter, dict):
            return adapter

        all_adapters = self.get()

        by_nodes = self.filter_by_nodes(value=node, adapters=all_adapters)
        by_names = self.filter_by_names(value=adapter, adapters=by_nodes)

        if len(by_names) != 1:
            value = "name {a!r} and node name {n!r}".format(a=adapter, n=node)
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapters by name and node name",
                known=self.get_known,
                known_msg="Adapters",
                match_type="equals",
                adapters=all_adapters,
            )

        return by_names[0]

    def filter_by_names(
        self,
        adapters,
        value=None,
        value_regex=False,
        value_ignore_case=True,
        match_count=None,
        match_error=True,
    ):
        """Filter adapters by names.

        Args:
            adapters (:obj:`list` of :obj:`dict`): list of adapter metadata to filter
                using **value**
            value (:obj:`str` or :obj:`list` of :obj:`str`, optional): default ``None`` -

                * if ``None`` return **adapters** as is
                * if :obj:`str` or :obj:`list` of :obj:`str` only return adapters whose
                  ``name`` key matches the supplied value(s)
            ignore_case (:obj:`bool`, optional): default ``True`` -

                * if ``True`` ignore case when matching **value** against the ``name``
                  key in each adapter in **adapters**
                * if ``False`` do not ignore case when matching **value** against the
                  ``name`` key in each adapter in **adapters**
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and match_error
                is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: adapters that matched supplied **value**
        """
        checks = tools.strip_right(obj=tools.listify(obj=value), fix="_adapter")
        matches = [] if checks else adapters

        for check in checks:
            re_flags = re.I if value_ignore_case else 0

            if value_regex:
                re_pattern = check
                re_method = re.search
            else:
                re_pattern = "^{}$".format(check)
                re_method = re.match

            for adapter in adapters:
                string = adapter["name"]
                is_match = re_method(
                    pattern=re_pattern.strip(), string=string, flags=re_flags
                )

                msg = "Matched adapter by name {s!r} using {p!r}: {r}"
                msg = msg.format(s=string, p=re_pattern, r=bool(is_match))
                self._log.debug(msg) if constants.DEBUG_MATCHES else None

                if is_match and adapter not in matches:
                    matches.append(adapter)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapters by names",
                known=self.get_known,
                known_msg="Adapters",
                adapters=adapters,
            )

        return matches

    def filter_by_nodes(
        self,
        adapters,
        value=None,
        value_regex=False,
        value_ignore_case=True,
        match_count=None,
        match_error=True,
    ):
        """Filter adapters with matching node names.

        Args:
            adapters (:obj:`list` of :obj:`dict`): list of adapter metadata to filter
                using **value**
            value (:obj:`str` or :obj:`list` of :obj:`str`, optional): default ``None`` -

                * if ``None`` return **adapters** as is
                * if :obj:`str` or :obj:`list` of :obj:`str` only return adapters whose
                  ``node_name`` key matches the supplied value(s)
            ignore_case (:obj:`bool`, optional): default ``True`` -

                * if ``True`` ignore case when matching **value** against the
                  ``node_name`` key in each adapter in **adapters**
                * if ``False`` do not ignore case when matching **value** against the
                  ``node_name`` key in each adapter in **adapters**
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: adapters that matched supplied **value**
        """
        checks = tools.listify(obj=value)
        matches = [] if checks else adapters

        for check in checks:
            re_flags = re.I if value_ignore_case else 0

            if value_regex:
                re_pattern = check
                re_method = re.search
            else:
                re_pattern = "^{}$".format(check)
                re_method = re.match

            for adapter in adapters:
                string = adapter["node_name"]
                is_match = re_method(
                    pattern=re_pattern.strip(), string=string, flags=re_flags
                )

                msg = "Matched adapter by node name {s!r} using {p!r}: {r}"
                msg = msg.format(s=string, p=re_pattern, r=bool(is_match))
                self._log.debug(msg) if constants.DEBUG_MATCHES else None

                if is_match and adapter not in matches:
                    matches.append(adapter)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapters by node names",
                known=self.get_known,
                known_msg="Adapters",
                adapters=adapters,
            )

        return matches

    def filter_by_cnx_count(
        self,
        adapters,
        min_value=None,
        max_value=None,
        match_count=None,
        match_error=True,
    ):
        """Filter adapters with matching connection counts.

        Args:
            adapters (:obj:`list` of :obj:`dict`): list of adapter metadata to filter
                using **value**
            min_value (:obj:`int`, optional): default ``None`` -

                * if ``None`` return **adapters** as is
                * if :obj:`int` only return adapters whose connection count
                  is at least this value
            max_value (:obj:`int`, optional): default ``None`` -

                * if ``None`` return **adapters** as is
                * if :obj:`int` only return adapters whose connection count
                  is at most this value
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: adapters that matched supplied **min_value**
            and **max_value**
        """
        matches = []

        for adapter in adapters:
            cnx_count = adapter["cnx_count"]

            if min_value is not None and cnx_count < min_value:
                continue

            if max_value is not None and cnx_count > max_value:
                continue

            if adapter not in matches:
                matches.append(adapter)

        if (match_count and len(matches) != match_count) and match_error:
            value = "min_value {} and max_value {}".format(min_value, max_value)
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapters by connection count",
                known=self.get_known,
                known_msg="Adapters",
                adapters=adapters,
                match_type="is",
            )

        return matches

    def filter_by_status(self, adapters, value=None, match_count=None, match_error=True):
        """Filter adapters with matching statuses.

        Args:
            adapters (:obj:`list` of :obj:`dict`): list of adapter metadata to filter
                using **value**
            value (:obj:`bool` or :obj:`list` of :obj:`bool`, optional):
                default ``None`` -

                * if ``None`` return **adapters** as is
                * if :obj:`bool` only return adapters whose connection status
                  equals this value
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: adapters that matched supplied **value**
        """
        matches = []

        for adapter in adapters:
            status = adapter["status"]
            if isinstance(value, constants.LIST):
                if value and status not in value:
                    continue
            elif value is not None and status != value:
                continue

            if adapter not in matches:
                matches.append(adapter)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapters by status",
                known=self.get_known,
                known_msg="Adapters",
                adapters=adapters,
            )

        return matches

    def upload_file_str(
        self,
        adapter,
        field,
        name,
        content,
        node=constants.DEFAULT_NODE,
        content_type=None,
    ):
        """Upload a str as a file to a specific adapter on a specific node.

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to get the metadata for
                * If :obj:`dict`, the metadata for a previously fetched adapter
            field (:obj:`str`): name of field to store data in
            name (:obj:`str`): filename to use when uploading file
            content (:obj:`str` or :obj:`bytes`): content of file to upload
            node (:obj:`str`, optional): default
                :data:`.constants.DEFAULT_NODE` -
                node name running ``adapter``
            content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        adapter = self.get_single(adapter=adapter, node=node)

        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            name=name,
            field=field,
            content=content,
            content_type=content_type,
        )

    def upload_file_path(
        self, adapter, field, path, node=constants.DEFAULT_NODE, content_type=None
    ):
        """Upload the contents of a file to a specific adapter on a specific node.

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to get the metadata for
                * If :obj:`dict`, the metadata for a previously fetched adapter
            field (:obj:`str`): name of field to store data in
            name (:obj:`str`): filename to use when uploading file
            path (:obj:`str` or :obj:`pathlib.Path`): path to file containing contents
                to upload
            node (:obj:`str`, optional): default
                :data:`.constants.DEFAULT_NODE` -
                node name running ``adapter``
            content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        adapter = self.get_single(adapter=adapter, node=node)

        path, content = tools.path_read(obj=path, binary=True, is_json=False)

        name = path.name

        return self._upload_file(
            adapter_name=adapter["name_raw"],
            node_id=adapter["node_id"],
            name=name,
            field=field,
            content=content,
            content_type=content_type,
        )

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        self.cnx = Cnx(parent=self)
        super(Adapters, self)._init(auth=auth, **kwargs)

    def _get(self):
        """Direct API method to get all adapters.

        Returns:
            :obj:`dict`: raw metadata for all adapters
        """
        path = self._router.root
        return self._request(method="get", path=path)

    def _set_config(self, adapter_name, config_name, config):
        """Direct API method to set advanced settings for an adapter.

        Args:
            adapter_name (:obj:`str`): unique plugin name of adapter to set
                advanced settings for. unique plugin name refers to the name of
                an adapter for a specific node
            config_name (:obj:`str`): name of advanced settings to set -
                either AdapterBase for generic advanced settings or
                AwsSettings for adapter specific settings, if applicable
            config (:obj:`dict`): the configuration values to set

        Returns:
            :obj:`str`: empty str
        """
        path = self._router.config.format(
            adapter_name=adapter_name, config_name=config_name
        )
        return self._request(
            method="post", path=path, json=config, error_json_invalid=False
        )

    def _get_config(self, adapter_name, config_name):
        """Direct API method to set advanced settings for an adapter.

        Args:
            adapter_name (:obj:`str`): unique plugin name of adapter to set
                advanced settings for. unique plugin name refers to the name of
                an adapter for a specific node i.e. aws_adapter_0
            config_name (:obj:`str`): name of advanced settings to set -
                either AdapterBase for generic advanced settings or
                AwsSettings for adapter specific settings, if applicable

        Returns:
            :obj:`dict`: current settings for config_name of adapter_name
        """
        path = self._router.config.format(
            adapter_name=adapter_name, config_name=config_name
        )
        return self._request(method="get", path=path)

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.adapters

    def _download_file(self, adapter_name, node_id, cnx_id, schema_key):
        """Direct API method to download a file.

        Notes:
            WORK IN PROGRESS!

        """
        data = {"uuid": cnx_id, "schema_key": schema_key}
        path = self._router.download_file.format(
            adapter_name=adapter_name, node_id=node_id
        )
        ret = self._request(method="post", path=path, json=data, raw=True)
        return ret

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
        """Direct API method to upload a file to a specific adapter on a specifc node.

        Args:
            adapter (:obj:`str`): name of the adapter to upload a file to
            node_id (:obj:`str`): ID of node running **adapter**
            name (:obj:`str`): filename to use when uploading file
            field (:obj:`str`): field to associate with this file
            content (:obj:`str` or :obj:`bytes`): content to upload
            content_type (:obj:`str`, optional): default ``None`` -
                mime type of **content**
            headers (:obj:`dict`, optional): default ``None`` -
                headers to use for file **content**

        Returns:
            :obj:`dict`: dict that can be used in a connection parameter of type
            file that contains the keys:

              * uuid: UUID of uploaded file
              * filename: filename of uploaded file
        """
        data = {"field_name": field}
        files = {"userfile": (name, content, content_type, headers)}

        path = self._router.upload_file.format(
            adapter_name=adapter_name, node_id=node_id
        )

        ret = self._request(method="post", path=path, data=data, files=files)
        ret["filename"] = name
        return ret


class Cnx(mixins.Child):
    """API model for working with adapter connections."""

    def add(
        self,
        adapter,
        config,
        parse_config=True,
        node=constants.DEFAULT_NODE,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Add a connection to an adapter.

        Notes:
            * connection will always be added even when the connection fails the
              initial reachability test and fetch performed when adding a connection

        Args:
            adapter (:obj:`str` or :obj:`dict`):

                * If :obj:`str`, the name of the adapter to add a connection to
                * If :obj:`dict`, the metadata for a previously fetched adapter
            config (:obj:`dict`): configuration of connection to add
            parse_config (:obj:`bool`, optional): default ``True`` -

                * if ``True`` validate the supplied ``config`` using
                  :meth:`ParserCnxConfig.parse`
                * if ``False`` do not validate the supplied ``config``
            node (:obj:`str`, optional): default
                :data:`.constants.DEFAULT_NODE` -
                if str supplied to **adapter**, find an adapter running on this node name
            retry (:obj:`int`, optional): default ``15`` - times to retry
            sleep (:obj:`int`, optional): default ``15`` - secs to wait between retries
            error (:obj:`bool`, optional): default ``True`` -

                * If ``True`` throw exc if the newly added configuration
                  has an error in the initial reachability test and fetch performed
                  when adding a connection
                * If ``False`` do not throw an exc

        Raises:
            :exc:`.exceptions.CnxConnectFailure`: if the newly added connection has an
                error in the initial reachability test and fetch performed

        Returns:
            :obj:`dict`: metadata for the newly added configuration
        """
        adapter = self._parent.get_single(adapter=adapter, node=node)

        if parse_config:
            parser = ParserCnxConfig(raw=config, parent=self)
            config = parser.parse(adapter=adapter, settings=adapter["cnx_settings"])

        response = self._add(
            adapter_name=adapter["name_raw"], node_id=adapter["node_id"], config=config
        )

        had_error = response.get("status", "") == "error" or response.get("error", "")
        has_uuid = "id" in response
        has_id = "client_id" in response

        if (had_error and error) or (not has_uuid or not has_id):
            raise exceptions.CnxConnectFailure(
                response=response, adapter=adapter["name"], node=adapter["node_name"]
            )

        """
        add call return when cnx added:
        {
            "client_id": "", # client ID
            "error": "",  # will not be empty when connection to adapter product fails
            "id": "",  # UUID
            "status": "",  # will be "error" when error not blank, or "success" when ok
        }

        add call return when... REST API breaks???
        {
            "status": "error",
            "type": "AttributeError",
            "message": "",
        }

        """

        # we refetch the CNX by UUID; add call doesnt return the full cnx obj
        refetched_cnx = self.refetch(
            adapter_name=adapter["name"],
            node_name=adapter["node_name"],
            response=response,
            retry=retry,
            sleep=sleep,
            filter_method=self.filter_by_uuids,
            filter_value=response["id"],
        )

        ret = {}
        ret["response_had_error"] = had_error
        ret["response"] = response
        ret["cnx"] = refetched_cnx

        return ret

    def add_csv_str(
        self,
        name,
        content,
        field,
        is_users=False,
        is_installed_sw=False,
        node=constants.DEFAULT_NODE,
        **kwargs,
    ):
        """Add a connection to the csv adapter using contents of str as a CSV file.

        Args:
            name (:obj:`str`): filename to use when uploading file
            content (:obj:`str` or :obj:`bytes`): content of CSV file to upload
            field (:obj:`str`): name of field to store data in
            node (:obj:`str`, optional): default
                :data:`.constants.DEFAULT_NODE` -
                if str supplied to **adapter**, find an adapter running on this node name
            is_users (:obj:`bool`, optional): default ``False`` - value to supply to
                connection settings **is_users_csv**
            is_installed_sw (:obj:`bool`, optional): default ``False`` - value to supply
                to connection settings **is_installed_sw**
            **kwargs: passed to :meth:`add`

        Returns:
            :obj:`dict`: metadata for the newly added configuration
        """
        adapter = self._parent.get_single(adapter=constants.CSV_ADAPTER, node=node)

        validate_csv(
            name=name,
            content=content,
            is_users=is_users,
            is_installed_sw=is_installed_sw,
        )
        meta_keys = constants.CSV_KEYS_META
        config = {}
        config[meta_keys["is_users_csv"]] = is_users
        config[meta_keys["is_installed_sw"]] = is_installed_sw
        config[meta_keys["id"]] = field
        config[meta_keys["file"]] = {}
        config[meta_keys["file"]]["filename"] = name
        config[meta_keys["file"]]["filecontent"] = content
        config[meta_keys["file"]]["filecontent_type"] = "text/csv"

        return self.add(adapter=adapter, config=config, node=node, **kwargs)

    def add_csv_file(self, path, field, **kwargs):
        """Add a connection to the csv adapter using a files contents as a CSV file.

        Args:
            path (:obj:`str` or :obj:`pathlib.Path`): path to file containing CSV
                contents to upload as a CSV file
            field (:obj:`str`): name of field to store data in
            **kwargs: passed to :meth:`add_csv_str`

        Returns:
            :obj:`dict`: metadata for the newly added configuration
        """
        path, content = tools.path_read(obj=path, binary=True, is_json=False)

        return self.add_csv_str(name=path.name, content=content, field=field, **kwargs)

    def check(self, cnx, retry=15, sleep=15, error=True):
        """Perform a reachability test for an adapter connection.

        Args:
            cnx (:obj:`dict`): the metadata for an adapter connection
            retry (:obj:`int`, optional): default ``15`` - times to retry
            sleep (:obj:`int`, optional): default ``15`` - secs to wait between retries
            error (:obj:`bool`, optional): default ``True`` -

                * If ``True`` throw exc if the connection has an
                  error during the reachability test
                * If ``False`` do not throw an exc

        Raises:
            :exc:`.exceptions.CnxConnectFailure`: if the connection has an
                error during the reachability test

        Returns:
            :obj:`dict`: metadata for the checked configuration
        """
        cnx = cnx.get("cnx", cnx)

        response = self._check(
            adapter_name=cnx["adapter_name_raw"],
            config=cnx["config_raw"],
            node_id=cnx["node_id"],
        )

        response_text = (response.text or "").strip()
        response_json = response.json() if response_text else {}

        had_error = not response.ok or bool(response_text)

        if had_error and error:
            raise exceptions.CnxConnectFailure(
                response=response, adapter=cnx["adapter_name"], node=cnx["node_name"]
            )

        ret = {}
        ret["response_had_error"] = had_error
        ret["response"] = response_json
        ret["cnx"] = cnx

        return ret

    def delete(
        self,
        cnx,
        delete_entities=False,
        force=False,
        warning=True,
        error=True,
        sleep=15,
    ):
        """Delete an adapter connection.

        Args:
            cnx (:obj:`dict`): the metadata for an adapter connection
            delete_entities (:obj:`bool`, optional): default ``False`` -

                * If ``True`` while deleting the connection also delete all asset
                  entities that have been fetched from this connection
                * If ``False`` delete only the connection
            force (:obj:`bool`, optional): default ``False`` -

                * If ``True`` actually delete the connection
                * If ``False`` do not delete the connection and throw an exc
            warning (:obj:`bool`, optional): default ``True`` -

                * If ``True`` throw a warning when deleting the connection
                * If ``False`` do not throw a warning when deleting the connection

            error (:obj:`bool`, optional): default ``True`` -

                * If ``True`` throw an exc if an error happens while deleting
                * If ``False`` do not throw an exc
            sleep (:obj:`int`, optional): default ``15`` - seconds to wait before
                deleting the connection


        Raises:
            :exc:`.exceptions.CnxDeleteForce`: if **force** is False
            :exc:`.exceptions.CnxDeleteWarning`: if **warning** is True
            :exc:`.exceptions.CnxDeleteFailedWarning`: if **warning** is True and
                and **error** is False and an error happens while deleting connection
            :exc:`.exceptions.CnxDeleteFailed`: if **error** is True and an error
                happens while deleting connection

        Returns:
            :obj:`dict`: metadata for the deleted configuration
        """
        cnx = cnx.get("cnx", cnx)

        cnxinfo = [
            "Adapter name: {adapter_name}",
            "Node name: {node_name}",
            "Connection ID: {id}",
            "Connection UUID: {uuid}",
            "Connection status: {status}",
            "Delete all entities: {de}",
        ]
        cnxinfo = tools.join_cr(obj=cnxinfo).format(de=delete_entities, **cnx)

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
        lsmsg = tools.join_cr(obj=lsmsg).format(cnxinfo=cnxinfo, s=sleep, a=dargs)
        self._log.warning(lsmsg)

        time.sleep(sleep)

        response = self._delete(**dargs)

        had_error = isinstance(response, dict) and (
            response["status"] == "error" or response["error"]
        )

        lfmsg = [
            "Connection info: {cnxinfo}",
            "Deleted connection with error {he} and return {r}",
        ]
        lfmsg = tools.join_cr(obj=lfmsg).format(
            cnxinfo=cnxinfo, he=had_error, r=response
        )
        self._log.info(lfmsg)

        if had_error:
            if warning and not error:
                warnings.warn(
                    exceptions.CnxDeleteFailedWarning(cnxinfo=cnxinfo, response=response)
                )
            elif error:
                raise exceptions.CnxDeleteFailed(cnxinfo=cnxinfo, response=response)

        ret = {}
        ret["response_had_error"] = had_error
        ret["response"] = response
        ret["cnx"] = cnx

        return ret

    def filter_by_ids(
        self,
        cnxs,
        value=None,
        value_regex=False,
        value_ignore_case=True,
        match_count=None,
        match_error=True,
    ):
        """Filter connections based on connection ID.

        Args:
            cnxs (:obj:`list` of :obj:`dict`): list of connection metadata to filter
                using **value**
            value (:obj:`str` or :obj:`list` of :obj:`str`): only return connections
                whose ``id`` key matches the supplied value(s)
            value_regex (:obj:`bool`, optional): default ``False`` -

                * if ``True`` treat **value** as a free form regex search
                * if ``False`` treat **value** as an exact regex search
            value_ignore_case (:obj:`bool`, optional): default ``True`` -

                * if ``True`` ignore case in **value** when searching
                * if ``False`` treat **value** as an exact regex search
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: connections that matched supplied **value**
        """
        checks = tools.listify(obj=value)
        matches = [] if checks else cnxs

        for check in checks:
            re_flags = re.I if value_ignore_case else 0

            if value_regex:
                re_pattern = check
                re_method = re.search
            else:
                re_pattern = "^{}$".format(check)
                re_method = re.match

            for cnx in cnxs:
                string = cnx["id"]

                is_match = re_method(
                    pattern=re_pattern.strip(), string=string, flags=re_flags
                )

                if is_match and cnx not in matches:
                    matches.append(cnx)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapter connections by id",
                known=self.get_known,
                known_msg="Adapter connections",
                cnxs=cnxs,
            )

        return matches

    def filter_by_uuids(
        self,
        cnxs,
        value=None,
        value_regex=False,
        value_ignore_case=True,
        match_count=None,
        match_error=True,
    ):
        """Filter connections based on connection UUID.

        Args:
            cnxs (:obj:`list` of :obj:`dict`): list of connection metadata to filter
                using **value**
            value (:obj:`str` or :obj:`list` of :obj:`str`): only return connections
                whose ``uuid`` key matches the supplied value(s)
            value_regex (:obj:`bool`, optional): default ``False`` -

                * if ``True`` treat **value** as a free form regex search
                * if ``False`` treat **value** as an exact regex search
            value_ignore_case (:obj:`bool`, optional): default ``True`` -

                * if ``True`` ignore case in **value** when searching
                * if ``False`` treat **value** as an exact regex search
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: connections that matched supplied **value**
        """
        checks = tools.listify(obj=value)
        matches = [] if checks else cnxs

        for check in checks:
            re_flags = re.I if value_ignore_case else 0

            if value_regex:
                re_pattern = check
                re_method = re.search
            else:
                re_pattern = "^{}$".format(check)
                re_method = re.match

            for cnx in cnxs:
                string = cnx["uuid"]

                is_match = re_method(
                    pattern=re_pattern.strip(), string=string, flags=re_flags
                )

                if is_match and cnx not in matches:
                    matches.append(cnx)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapter connections by uuid",
                known=self.get_known,
                known_msg="Adapter connections",
                cnxs=cnxs,
            )

        return matches

    def filter_by_status(self, cnxs, value=None, match_count=None, match_error=True):
        """Filter connections based on connection status.

        Args:
            cnxs (:obj:`list` of :obj:`dict`): list of connection metadata to filter
                using **value**
            value (:obj:`bool` or :obj:`list` of :obj:`bool`): only return connections
                whose ``status`` key matches the supplied value(s)
            match_count (:obj:`int`, optional): default ``None`` -
                number of items that must match **value**
            match_error (:obj:`bool`, optional): default ``True`` -

                * if ``True`` and **match_count** is not None, raise exception if number
                  of matches does not equal **match_count**
                * if ``False`` do not raise an exception regardless of
                  the number of matches to **value**

        Raises:
            :exc:`.exceptions.ValueNotFound`: if match_count is not None and
                match_error is True and number of matches does not equal match_count

        Returns:
            :obj:`list` of :obj:`dict`: connections that matched supplied **value**
        """
        matches = []

        for cnx in cnxs:
            status = cnx["status"]

            if isinstance(value, constants.LIST):
                if value and status not in value:
                    continue
            elif value is not None and status != value:
                continue

            if cnx not in matches:
                matches.append(cnx)

        if (match_count and len(matches) != match_count) and match_error:
            raise exceptions.ValueNotFound(
                value=value,
                value_msg="Adapter connections by status",
                known=self.get_known,
                known_msg="Adapter connections",
                cnxs=cnxs,
            )

        return matches

    def get(self, adapter=None, node=None):
        """Get all connections for a specific adapter on a specific node.

        Args:
            adapter (:obj:`object`, optional): default ``None`` -

                * if :obj:`str` return connections from the name of an adapter
                  running on **node**
                * if :obj:`list` of :obj:`str` return connections from adapters
                  that match the supplied names that are running on **node**.
                * if ``None`` return the connections for all adapters
            node (:obj:`str`, optional): default ``None`` -
                if str or list of str supplied to **adapter**, return connections
                for adapter(s) running on this node name

        Returns:
            :obj:`list` of :obj:`dict`: connections for the supplied adapter(s)/node
        """
        if isinstance(adapter, constants.LIST):
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_names(
                adapters=all_adapters, value=adapter
            )
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, value=node
            )
            return [c for a in all_adapters for c in a["cnx"]]

        if not adapter:
            all_adapters = self._parent.get()
            all_adapters = self._parent.filter_by_nodes(
                adapters=all_adapters, value=node
            )
            return [c for a in all_adapters for c in a["cnx"]]

        adapter = self._parent.get_single(adapter=adapter, node=node)
        return adapter["cnx"]

    def get_known(self, cnxs=None, **kwargs):
        """Get str descriptors of known/valid adapter connections.

        Args:
            cnxs (:obj:`list` of :obj:`dict`, optional): default ``None`` - connections
                to return descriptors from.

                * if ``None`` return the descriptors for the output from :meth:`get`
                * if :obj:`list` of :obj:`dict` return the descriptors for supplied
                  connections

        Returns:
            :obj:`list` of :obj:`str`: list of str describing each connection
        """
        cnxs = cnxs or self.get()
        tmpl = [
            "Adapter: {adapter_name!r}",
            "Node: {node_name!r}",
            "cnx id: {id!r}",
            "cnx uuid: {uuid!r}",
            "cnx status: {status}",
        ]
        tmpl = tools.join_comma(obj=tmpl)
        return [tmpl.format(**c) for c in cnxs]

    def refetch(
        self,
        adapter_name,
        node_name,
        response,
        filter_method,
        filter_value,
        retry=15,
        sleep=15,
    ):
        """Refetch a connection after it has been updated/added.

        Args:
            adapter_name (:obj:`str`): adapter name to refetch connection from
            node_name (:obj:`str`): node name to refetch connection from
            response (:obj:`dict`): response from adding/updating a connection
            filter_method (:obj:`callable`): filter method to use to find connection
            filter_value (:obj:`object`): value to pass to filter method
            retry (:obj:`int`, optional): default ``15`` - amount of times to try
                refetching connection
            sleep (:obj:`int`, optional): default ``15`` - secs to wait in between
                each retry

        Raises:
            :exc:`.exceptions.CnxRefetchFailure`: if connection could not be refeteched

        Returns:
            :obj:`dict`: refetched connection
        """
        count = 0
        retry = retry or 1

        # new connections don't always show up right away, so we have to do some magic
        while count < retry:
            # re-fetch all connections for this adapter
            # try to find the newly created connection
            all_cnxs = self.get(adapter=adapter_name, node=node_name)

            msg = "Retry count {c}/{r} and sleep {s} - find {fv!r} using {fm!r}"
            msg = msg.format(
                c=count, r=retry, s=sleep, fv=filter_value, fm=filter_method
            )
            self._log.debug(msg)

            cnxs = filter_method(
                cnxs=all_cnxs, value=filter_value, match_count=1, match_error=False
            )

            msg = "Found {c} matches out of {ct} cnxs using {fv!r}"
            msg = msg.format(c=len(cnxs), ct=len(all_cnxs), fv=filter_value)
            self._log.debug(msg)

            if len(cnxs) == 1:
                return cnxs[0]

            count += 1

            dmsg = [
                "Connection not in system yet",
                "try {c} of {r}",
                "sleeping another {s} seconds",
                "Looking for connection: {response}",
            ]
            dmsg = tools.join_comma(obj=dmsg).format(
                response=response, c=count, r=retry, s=sleep
            )
            self._log.debug(dmsg)

            time.sleep(sleep)

        raise exceptions.CnxRefetchFailure(
            response=response,
            adapter=adapter_name,
            node=node_name,
            filter_method=filter_method,
            filter_value=filter_value,
            known=self.get_known,
            cnxs=all_cnxs,
        )

    def update(
        self, cnx, new_config=None, parse_config=True, retry=15, sleep=15, error=True
    ):
        """Update a connections configuration.

        Args:
            cnx (:obj:`dict`): connection to update
            new_config (:obj:`dict`, optional): default ``None`` -

                * if :obj:`dict` update the configuration with the supplied values
                * if ``None`` update the configuration with the current values
                  which will trigger a reachability test and a fetch to start
            parse_config (:obj:`bool`, optional): default ``True`` -

                * if ``True`` validate the supplied ``new_config`` using
                  :meth:`ParserCnxConfig.parse`
                * if ``False`` do not validate the supplied ``new_config``
            retry (:obj:`int`, optional): default ``15`` - times to retry
            sleep (:obj:`int`, optional): default ``15`` - secs to wait between retries
            error (:obj:`bool`, optional): default ``True`` -

                * If ``True`` throw exc if the updated configuration
                  has an error in the reachability test and fetch performed
                  when updating a connection
                * If ``False`` do not throw an exc

        Raises:
            :exc:`.exceptions.CnxConnectFailure`: if the updated connection has an
                error in the reachability test and fetch performed

        Returns:
            :obj:`dict`: metadata for the updated configuration
        """
        cnx = cnx.get("cnx", cnx)

        if parse_config and new_config:
            adapter = self._parent.get_single(adapter=cnx["adapter_name"])
            parser = ParserCnxConfig(raw=new_config, parent=self)
            new_config = parser.parse(adapter=adapter, settings=adapter["cnx_settings"])

        msg = [
            "Updating cnx id={id}",
            "uuid={uuid}",
            "adapter={adapter_name}",
            "node={node_name}",
        ]
        msg = tools.join_comma(obj=msg).format(**cnx)
        self._log.debug(msg)

        response = self._update(
            adapter_name=cnx["adapter_name_raw"],
            node_id=cnx["node_id"],
            config=new_config or cnx["config_raw"],
            cnx_uuid=cnx["uuid"],
        )

        msg = "Updating cnx response {r}".format(r=response)
        self._log.debug(msg)

        had_error = response["status"] == "error" or response["error"]

        if had_error and error:
            raise exceptions.CnxConnectFailure(
                response=response, adapter=cnx["adapter_name"], node=cnx["node_name"]
            )

        # we refetch the CNX by ID; update call changes the UUID
        refetched_cnx = self.refetch(
            adapter_name=cnx["adapter_name"],
            node_name=cnx["node_name"],
            response=response,
            retry=retry,
            sleep=sleep,
            filter_method=self.filter_by_uuids,
            filter_value=response["id"],
        )

        ret = {}
        ret["response_had_error"] = had_error
        ret["response"] = response
        ret["cnx"] = refetched_cnx

        return ret

    def _add(self, adapter_name, node_id, config):
        """Direct API method to add a connection to an adapter.

        Args:
            adapter (:obj:`str`): name of adapter
            node_id (:obj:`str`): id of node running **adapter**
            config (:obj:`dict`): configuration values for new connection

        Returns:
            :obj:`str`: an empty str
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
            error_status=False,
        )

    def _check(self, adapter_name, node_id, config):
        """Direct API method to add a connection to an adapter.

        Args:
            adapter (:obj:`str`): name of adapter
            node_id (:obj:`str`): id of node running **adapter**
            config (:obj:`dict`): configuration values to test reachability for

        Returns:
            :obj:`str`: an empty str
        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id

        path = self._parent._router.cnxs.format(adapter_name=adapter_name)

        return self._parent._request(method="post", path=path, json=data, raw=True)

    def _delete(self, adapter_name, node_id, cnx_uuid, delete_entities=False):
        """Direct API method to delete a connection from an adapter.

        Args:
            adapter_name (:obj:`str`): name of adapter
            node_id (:obj:`str`): id of node running **adapter**
            cnx_uuid (:obj:`str`): uuid of connection to delete
            delete_entities (:obj:`bool`, optional): default ``False`` -

                * if ``True`` delete the connection and also delete all asset entities
                  fetched by this connection
                * if ``False`` just delete the connection

        Returns:
            :obj:`str`: an empty str
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
            error_status=False,
        )

    def _update(self, adapter_name, node_id, config, cnx_uuid):
        """Direct API method to update a connection on an adapter.

        Args:
            adapter_name (:obj:`str`): name of adapter
            node_id (:obj:`str`): id of node running **adapter**
            config (:obj:`dict`): configuration of connection to update
            cnx_uuid (:obj:`str`): uuid of connection to update

        Returns:
            :obj:`str`: an empty str
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
            error_status=False,
        )


class ParserCnxConfig(mixins.Parser):
    """Parser to validate a users supplied connection settings."""

    def parse(self, adapter, settings):
        """Parser to validate a users supplied connection settings.

        Args:
            adapter (:obj:`dict`): metadata of adapter for connection
            settings (:obj:`dict`): supplied connection settings to parse

        Returns:
            :obj:`dict`: validated and processed connection settings

        Raises:
            :exc:`.exceptions.CnxSettingMissing`: if a required setting is missing or
                has no value
        """
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

    def check_value(self, name, value, schema, adapter):
        """Validate and process the supplied value for a connection setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`object`): user supplied value for setting
            schema (:obj:`dict`): schema for setting
            adapter (:obj:`dict`): metadata of adapter for connection

        Returns:
            :obj:`object`: the validated and processed value

        Raises:
            :exc:`.exceptions.CnxSettingInvalidChoice`: if setting is an enum
                and user supplied value is not one of enums
            :exc:`.exceptions.CnxSettingInvalidType`: if type of setting does not match
                type of user supplied value
            :exc:`.exceptions.CnxSettingUnknownType`: if type of setting is not one
                of the types this method knows about
        """
        type_str = schema["type"]
        enum = schema.get("enum", [])

        if value == constants.SETTING_UNCHANGED:
            return value

        if enum and value not in enum:
            raise exceptions.CnxSettingInvalidChoice(
                name=name, value=value, schema=schema, enum=enum, adapter=adapter
            )

        if type_str == "file":
            return self.check_file(
                name=name, value=value, schema=schema, adapter=adapter
            )
        elif type_str == "bool":
            return tools.coerce_bool(obj=value)
        elif type_str in ["number", "integer"]:
            return tools.coerce_int(obj=value)
        elif type_str == "array":
            if isinstance(value, constants.STR):
                value = [x.strip() for x in value.split(",")]
            if isinstance(value, constants.LIST) and all(
                [isinstance(x, constants.STR) for x in value]
            ):
                return value
        elif type_str == "string":
            if isinstance(value, constants.STR):
                return value
        else:
            raise exceptions.CnxSettingUnknownType(
                name=name,
                value=value,
                schema=schema,
                type_str=type_str,
                adapter=adapter,
            )

        raise exceptions.CnxSettingInvalidType(
            name=name, value=value, schema=schema, adapter=adapter, mustbe=type_str
        )

    def check_file(self, name, value, schema, adapter):
        """Validate and process a file type setting.

        Args:
            name (:obj:`str`): setting name
            value (:obj:`dict` or :obj:`str` or :obj:`pathlib.Path`):

                * if :obj:`dict` a dict containing **uuid** and **filename** keys
                    of an already uploaded file
                * if :obj:`str` the content to upload as a file to **adapter**
                * if :obj:`pathlib.Path` the path to a file to upload the contents of
                    as a file to **adapter**
            schema (:obj:`dict`): schema for setting
            adapter (:obj:`dict`): metadata of adapter for connection

        Returns:
            :obj:`dict`: the validated and processed value

        Raises:
            :exc:`.exceptions.CnxSettingFileMissing`: if the supplied value points to
                a file that does not exist
            :exc:`.exceptions.CnxSettingInvalidType`: if the supplied value is not
                a dict, str, or pathlib.Path
        """
        is_str = isinstance(value, constants.STR)
        is_dict = isinstance(value, dict)
        is_path = isinstance(value, tools.pathlib.Path)

        if not any([is_dict, is_str, is_path]):
            raise exceptions.CnxSettingInvalidType(
                name=name,
                value=value,
                schema=schema,
                mustbe="dict or str",
                adapter=adapter,
            )

        if is_str or is_path:
            value = {"filepath": format(value)}

        uuid = value.get("uuid", None)
        filename = value.get("filename", None)
        filepath = value.get("filepath", None)
        filecontent = value.get("filecontent", None)
        filecontent_type = value.get("filecontent_type", None)

        if uuid and filename:
            return {"uuid": uuid, "filename": filename}

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
    """Parser to turn adapters metadata into a more friendly format."""

    def parse(self):
        """Parser to turn adapters metadata into a more friendly format.

        Returns:
            :obj:`dict`: parsed adapters metadata
        """
        parsed = []

        for name, raw_adapters in self._raw.items():
            for idx, raw in enumerate(raw_adapters):
                adapter = self._adapter(name=name, raw=raw)
                adapter["idx"] = idx
                parsed.append(adapter)

        return parsed

    def _adapter(self, name, raw):
        """Parse a single adapter.

        Args:
            name (:obj:`str`): name of adapter
            raw (:obj:`dict`): original adapter metadata returned from API

        Returns:
            :obj:`dict`: parsed adapter metadata
        """
        parsed = {
            "name": tools.strip_right(obj=name, fix="_adapter"),
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
        """Parse the advanced settings for an adapter.

        Args:
            raw (:obj:`dict`): original adapter metadata returned from API
            base (:obj:`bool`, optional): default ``True`` -

                * if ``True`` parse the generic adapter advanced settings
                * if ``False`` parse the adapter specific advanced settings

        Returns:
            :obj:`dict`: parsed advanced settings for this adapter
        """
        settings = {}

        for raw_name, raw_settings in raw["config"].items():
            is_base = raw_name == "AdapterBase"
            if ((is_base and base) or (not is_base and not base)) and not settings:
                schema = raw_settings["schema"]
                items = schema["items"]
                required = schema["required"]
                config = raw_settings["config"]

                for idx, item in enumerate(items):
                    setting_name = item["name"]
                    parsed_settings = {k: v for k, v in item.items()}
                    parsed_settings["required"] = setting_name in required
                    parsed_settings["value"] = config.get(setting_name, None)
                    parsed_settings["idx"] = idx
                    settings[setting_name] = parsed_settings

        return settings

    def _cnx_settings(self, raw):
        """Parse the connection settings for this adapter.

        Args:
            raw (:obj:`dict`): original adapter metadata returned from API

        Returns:
            :obj:`dict`: parsed connection settings for this adapter
        """
        settings = {}

        schema = raw["schema"]
        items = schema["items"]
        required = schema["required"]

        for idx, item in enumerate(items):
            setting_name = item["name"]
            settings[setting_name] = {k: v for k, v in item.items()}
            settings[setting_name]["required"] = setting_name in required
            settings[setting_name]["idx"] = idx

        return settings

    def _cnx(self, raw, parent):
        """Parse the connection metadata for this adapter.

        Args:
            raw (:obj:`dict`): original adapter metadata returned from API

        Returns:
            :obj:`dict`: parsed connection metadata for this adapter
        """
        cnx = []

        cnx_settings = self._cnx_settings(raw=raw)

        for idx, raw_cnx in enumerate(raw["clients"]):
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
            pcnx["idx"] = idx
            cnx.append(pcnx)

        return cnx


def validate_csv(name, content, is_users=False, is_installed_sw=False):
    """Validate the contents of a CSV to ensure it has the necessary columns.

    Args:
        name (:obj:`str`): name of csv file
        content (:obj:`str` or :obj:`bytes`): content of csv file
        is_users (:obj:`bool`, optional): default ``False`` -
            validate content as a users csv file
        is_installed_sw (:obj:`bool`, optional): default ``False`` -
            validate content as an installed software for devices CSV file

    Raises:
        :exc:`.exceptions.CsvIdentifierWarning`: if the supplied CSV contents do not have
            at least one of the strong identifiers for this type of CSV file
    """
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
    if isinstance(headers_content, constants.BYTES):
        headers_content = headers_content.decode()

    headers = headers_content.splitlines()[0].lower().split(",")
    headers_has_any_id = any([x in headers for x in ids])

    if not headers_has_any_id:
        warnings.warn(
            exceptions.CsvIdentifierWarning(
                ids_type=ids_type, ids=ids, name=name, headers=headers
            )
        )
