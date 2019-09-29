# -*- coding: utf-8 -*-
"""API module for working with adapters."""
from __future__ import absolute_import, division, print_function, unicode_literals

import re
import time
import warnings

from .. import constants, exceptions, tools
from . import mixins, routers


class Adapters(mixins.Model, mixins.Mixins):
    """Adapter API.

    Attributes:
        cnx (Cnx): Child object for working with adapter connections.

    """

    def get(self):
        """Get the metadata for all adapters.

        Returns:
            (list) of (dict): List of parsed metadata for all adapters.

        """
        raw = self._get()
        parser = ParserAdapters(raw=raw, parent=self)
        adapters = parser.parse()
        return adapters

    def get_known(self, adapters=None, **kwargs):
        """Get the name, node name, cnx count, and status of all adapters.

        Args:
            adapters ((list) of (dict), optional): List of adapters to include in
                return.

                Defaults to: Return from :meth:`get`.

        Returns:
            (list) of (str): List of human readable strings representing each adapter.

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

    def get_single(self, adapter, node="master"):
        """Get the metadata for a single adapter.

        Args:
            adapter ((str) or (dict)): Adapter to find.

                * If str, the name of the adapter to get the
                metadata for.
                * If dict, the metadata for a single adapter returned from
                  :meth:`get`, :meth:`filter_by_names`,
                  :meth:`filter_by_nodes`, :meth:`filter_by_status`, or
                  :meth:`filter_by_cnx_count`.

            node (str, optional):
                If ``adapter`` is str, the name of the node running the ``adapter``
                to find.

                Defaults to: "master".

        Raises:
            exceptions.ValueNotFound:
                If searching for ``node`` using :meth:`filter_by_nodes` and
                ``adapter`` using :meth:`filter_by_names` does not return exactly
                one match.

        Returns:
            dict: The metadata of a single adapter.

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
        """Filter adapters with matching adapter names.

        Args:
            adapters (list) of (dict): The list of metadata for adapters to filter on
                returned from :meth:`get`, :meth:`filter_by_names`,
                :meth:`filter_by_nodes`, :meth:`filter_by_status`, or
                :meth:`filter_by_cnx_count`.
            value ((list) of (str) or (str), optional): The names to match in
                ``adapters``.

                * If value is None, the list of adapters will be returned as
                  is.
                * Any string value starting with "RE:" will be treated as a regex.

                Defaults to: None.
            ignore_case (bool, optional): Ignore case when checking ``value`` against
                each adapter name.

                Defaults to: True.
            match_count (int, optional): The number of matches that should be found
                for ``value``.

                Defaults to: None.
            match_error (bool, optional): Raise error if the number of matches does not
                equal ``match_count``.

                Defaults to: True.

        Raises:
            exceptions.ValueNotFound:
                If ``match_count`` does not equal the number of matches found and
                ``match_error`` is True.

        Returns:
            (list) of (dict): List of matching adapters.

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
                self._log.debug(msg)

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
            adapters (list) of (dict): The list of metadata for adapters to filter on
                returned from :meth:`get`, :meth:`filter_by_names`,
                :meth:`filter_by_nodes`, :meth:`filter_by_status`, or
                :meth:`filter_by_cnx_count`.
            value ((list) of (str) or (str), optional): The node names to match in
                ``adapters``. If value is None, the list of adapters will be returned as
                is. Any string value starting with "RE:" will be treated as a regex.
                Defaults to: None.
                Any string value starting with "RE:" will be treated as a regex.
            ignore_case (bool, optional): Ignore case when checking value against
                each node name. Defaults to: True.
            match_count (int, optional): The number of matches that should be found
                for ``value``. Defaults to: None.
            match_error (bool, optional): Raise error if the number of matches does not
                equal ``match_count``. Defaults to: True.

        Raises:
            exceptions.ValueNotFound: If ``match_count`` does not equal the number of
                matches found and ``match_error`` is True.

        Returns:
            (list) of (dict): List of matching adapters.

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
                self._log.debug(msg)

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
            adapters (list) of (dict): The list of metadata for adapters to filter on
                returned from :meth:`get`, :meth:`filter_by_names`,
                :meth:`filter_by_nodes`, :meth:`filter_by_status`, or
                :meth:`filter_by_cnx_count`.
            value (int, optional): The number of connections to
                match in ``adapters``. If value is None, the list of adapters will be
                returned as is. Defaults to: None.
            match_count (int, optional): The number of matches that should be found
                for ``value``. Defaults to: None.
            match_error (bool, optional): Raise error if the number of matches does not
                equal ``match_count``. Defaults to: True.

        Raises:
            exceptions.ValueNotFound: If ``match_count`` does not equal the number of
                matches found and ``match_error`` is True.

        Returns:
            (list) of (dict): List of matching adapters.

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

    def filter_by_status(
        self, adapters, value=None, match_count=None, match_error=True
    ):
        """Filter adapters with matching statuses.

        Args:
            adapters (list) of (dict): The list of metadata for adapters to filter on
                returned from :meth:`get`, :meth:`filter_by_names`,
                :meth:`filter_by_nodes`, :meth:`filter_by_status`, or
                :meth:`filter_by_cnx_count`.
            value (((list) of (bool) or (None)) or ((bool) or (None)), optional):
                The status or statuses to match against each adapter.

                * True: All connections for an adapter are working.
                * False: At least one of the connections for an adapter is broken.
                * None: No connections exist on an adapter.

                Defaults to: None.
            match_count (int, optional): The number of matches that should be found
                for ``value``. Defaults to: None.
            match_error (bool, optional): Raise error if the number of matches does not
                equal ``match_count``. Defaults to: True.

        Raises:
            exceptions.ValueNotFound: If ``match_count`` does not equal the number of
                matches found and ``match_error`` is True.

        Returns:
            (list) of (dict): List of matching adapters.

        """
        matches = []

        for adapter in adapters:
            status = adapter["status"]
            if isinstance(value, tools.LIST):
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
        self, adapter, field, name, content, node="master", content_type=None
    ):
        """Upload a string to an adapter on a node.

        Args:
            adapter (str): Name of adapter to upload to.
            field (str): Name of field to store data in.
            name (str): Filename to use when uploading file.
            content ((str) or (bytes)): Content to upload.
            node (str, optional): Node name running ``adapter``. Defaults to: "master"
            content_type (str, optional): Mime type of ``content``. Defaults to: None.

        Returns:
            dict: Example:

                  {"uuid": "UUID of file", "filename": "name of file"}

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

    def upload_file_path(self, adapter, field, path, node="master", content_type=None):
        """Upload the contents of a file to an adapter on a node.

        Args:
            adapter (str): Name of adapter to upload file to.
            field (str): Name of field to store data in.
            path ((str) or (pathlib.Path)): File to upload contents of.
            node (str, optional): Node name running ``adapter``. Defaults to: "master"
            content_type (str, optional): Mime type of ``path`` contents.
                Defaults to: None.

        Returns:
            dict: Output from :meth:`upload_file_str`

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
        """Post init setup.

        Args:
            auth (axonius_api_client.auth.Model): Authentication object.

        """
        self.cnx = Cnx(parent=self)
        super(Adapters, self)._init(auth=auth, **kwargs)

    def _get(self):
        """Direct API method to get all adapters.

        Returns:
            dict: The raw metadata for all adapters.

        """
        return self._request(method="get", path=self._router.root)

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            routers.Router: The object holding the REST API routes for this object type.

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
        """Direct API method to upload a file to an adapter instance on a node.

        Args:
            adapter_name (str): Name of adapter to upload file to.
            node_id (str): ID of node running ``adapter_name``.
            name (str): Name of file to upload.
            field (str): Field to associate with this file.
            content ((str) or (bytes)): Contents of file to upload.
            content_type (str, optional): Mime type of ``content``. Defaults to: None.
            headers (dict, optional): Mime headers for ``content``. Defaults to: None.

        Returns:
            dict: UUID and filename of uploaded file.

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
    """Adapter connections API."""

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
            adapter ((str) or (dict)): If str, name of adapter to add connection to.
                If dict, an adapters metadata returned from :meth:`Adapters.get_single`
                or a single adapter returned from :meth:Adapt
            config (dict): Configuration of connection to add.
            parse_config (bool, optional): Check the supplied ``config`` using
                :meth:`ParserCnxConfig.parse`. Defaults to: True.
            node (str, optional): Name of node running ``adapter``.
                Defaults to: "master".
            retry (int, optional): Number of times to retry fetching the newly added
                connection. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the newly added configuration
                returns an error from connecting to the product for the adapter.
                The connection will always be added even if it has an error connecting.
                Defaults to: True.

        Raises:
            exceptions.CnxConnectFailure: If the newly added connection fails to
                connect to the product for the adapter and ``error`` is True.

        Returns:
            dict: The metadata for the newly added configuration.

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

        """
        add call returns:
        {
            "client_id": "", # client ID
            "error": "",
            "id": "",  # UUID
            "status": "",
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
        node="master",
        is_users=False,
        is_installed_sw=False,
        parse_config=True,
        retry=15,
        sleep=15,
        error=True,
    ):
        """Add a connection for the CSV adapter using str contents.

        Args:
            name (str): Name to use for the uploaded CSV file.
            content ((str) or (bytes)): CSV contents to upload.
            field (str): Field to store connection in.
            node (str, optional): Node name running CSV adapter to add connection to.
                Defaults to: "master".
            is_users (bool, optional): ``content`` is for users. Defaults to: False.
            is_installed_sw (bool, optional): ``content`` is for installed software for
                devices. Defaults to: False.
            retry (int, optional): Number of times to retry fetching the newly added
                connection. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the newly added configuration
                returns an error from connecting to the product for the adapter.
                The connection will always be added even if it has an error connecting.
                Defaults to: True.

        Notes:
            If ``is_users`` and ``is_installed_sw`` is False, the ``content`` is
            for devices.

        Returns:
            dict: The output of :meth:`add`.

        """
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
        """Add a connection for the CSV adapter using file contents.

        Args:
            name (str): Name to use for the uploaded CSV file.
            path ((str) or (pathlib.Path)): Path to file with CSV contents to upload.
            field (str): Field to store connection in.
            node (str, optional): Node name running CSV adapter to add connection to.
                Defaults to: "master".
            is_users (bool, optional): ``content`` is for users. Defaults to: False.
            is_installed_sw (bool, optional): ``content`` is for installed software for
                devices. Defaults to: False.
            retry (int, optional): Number of times to retry fetching the newly added
                connection. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the newly added configuration
                returns an error from connecting to the product for the adapter.
                The connection will always be added even if it has an error connecting.
                Defaults to: True.

        Notes:
            If ``is_users`` and ``is_installed_sw`` is False, the ``content`` is
            for devices.

        Returns:
            dict: The output of :meth:`add`.

        """
        adapter = self._parent.get_single(adapter="csv", node=node)

        path, content = tools.path_read(obj=path, binary=True, is_json=False)

        name = path.name

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
        """Add a connection for the CSV adapter that reads from a URL.

        Args:
            name (str): Name to use for the uploaded CSV file.
            url (str): URL to file with CSV contents to load on each fetch.
            field (str): Field to store connection in.
            node (str, optional): Node name running CSV adapter to add connection to.
                Defaults to: "master".
            is_users (bool, optional): ``content`` is for users. Defaults to: False.
            is_installed_sw (bool, optional): ``content`` is for installed software for
                devices. Defaults to: False.
            retry (int, optional): Number of times to retry fetching the newly added
                connection. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the newly added configuration
                returns an error from connecting to the product for the adapter.
                The connection will always be added even if it has an error connecting.
                Defaults to: True.

        Notes:
            If ``is_users`` and ``is_installed_sw`` is False, the ``content`` is
            for devices.

        Returns:
            dict: The output of :meth:`add`.

        """
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
        """Add a connection for the CSV adapter that reads from a SMB share.

        Args:
            name (str): Name to use for the uploaded CSV file.
            share (str): SMB path to file with CSV contents to load on each fetch.
            field (str): Field to store connection in.
            node (str, optional): Node name running CSV adapter to add connection to.
                Defaults to: "master".
            is_users (bool, optional): ``content`` is for users. Defaults to: False.
            is_installed_sw (bool, optional): ``content`` is for installed software for
                devices. Defaults to: False.
            username (str, optional): Username to use when accessing ``share``.
                Defaults to: None.
            password (str, optional): Password to use when accessing ``share``.
                Defaults to: None.
            retry (int, optional): Number of times to retry fetching the newly added
                connection. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the newly added configuration
                returns an error from connecting to the product for the adapter.
                The connection will always be added even if it has an error connecting.
                Defaults to: True.

        Notes:
            If ``is_users`` and ``is_installed_sw`` is False, the ``content`` is
            for devices.

        Returns:
            dict: The output of :meth:`add`.

        """
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
        """Pass.

        Args:
            cnx (dict): The metadata of a single connection returned from :meth:`get`.
            retry (int, optional): Number of times to retry fetching the connection after
                checking. Defaults to: 15.
            sleep (int, optional): Number of seconds to wait in between each fetch
                retry. Defaults to: 15.
            error (bool, optional): Raise an error if the connection returns an error
                from connecting to the product for the adapter. Defaults to: True.

        Raises:
            exceptions.CnxConnectFailure: If the connection fails to
                connect to the product for the adapter and ``error`` is True.

        Returns:
            dict: The metadata with the new UUID for the checked configuration.

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
        """Pass.

        Args:
            cnx (TYPE): Description
            delete_entities (bool, optional): Description
            force (bool, optional): Description
            warning (bool, optional): Description
            error (bool, optional): Description
            sleep (int, optional): Description

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

    def filter_by_ids(
        self,
        cnxs,
        value=None,
        value_regex=False,
        value_ignore_case=True,
        match_count=None,
        match_error=True,
    ):
        """Get all connections for all adapters.

        Args:
            cnxs (TYPE): Description
            value (None, optional): Description
            ignore_case (bool, optional): Description
            match_count (None, optional): Description
            match_error (bool, optional): Description

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
        """Get all connections for all adapters.

        Args:
            cnxs (TYPE): Description
            value (None, optional): Description
            ignore_case (bool, optional): Description
            match_count (None, optional): Description
            match_error (bool, optional): Description

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
        """Get all connections for all adapters.

        Args:
            cnxs (TYPE): Description
            value (None, optional): Description
            match_count (None, optional): Description
            match_error (bool, optional): Description

        Returns:
            TYPE: Description

        Raises:
            exceptions.ValueNotFound: Description

        """
        matches = []

        for cnx in cnxs:
            status = cnx["status"]

            if isinstance(value, tools.LIST):
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
        """Get all connections for an adapter.

        Args:
            adapter (None, optional): Description
            node (None, optional): Description

        Returns:
            TYPE: Description

        """
        if isinstance(adapter, tools.LIST):
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

    def get_known(self, **kwargs):
        """Pass.

        Args:
            **kwargs: Description

        Returns:
            TYPE: Description

        """
        cnxs = kwargs.get("cnxs") or self.get()
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
        """Pass.

        Args:
            adapter_name (TYPE): Description
            node_name (TYPE): Description
            response (TYPE): Description
            filter_method (TYPE): Description
            filter_value (TYPE): Description
            retry (int, optional): Description
            sleep (int, optional): Description

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
        """Pass.

        Args:
            cnx (TYPE): Description
            new_config (None, optional): Description
            parse_config (bool, optional): Description
            retry (int, optional): Description
            sleep (int, optional): Description
            error (bool, optional): Description

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
        """Add a connection to an adapter.

        Args:
            adapter_name (TYPE): Description
            node_id (:obj:`str`): Node ID.
            config (:obj:`dict`): Client configuration.

        Returns:
            :obj: `object`

        Deleted Parameters:
            adapter (:obj:`str`): Name of adapter to add connection to.

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
        """Test an adapter connection.

        Args:
            adapter_name (TYPE): Description
            node_id (:obj:`str`): Node ID.
            config (:obj:`dict`): Connection configuration.

        Returns:
            :obj: `object`

        Deleted Parameters:
            name (:obj:`str`): Name of adapter to test connection of.

        """
        data = {}
        data.update(config)
        data["instanceName"] = node_id
        data["oldInstanceName"] = node_id

        path = self._parent._router.cnxs.format(adapter_name=adapter_name)

        return self._parent._request(method="post", path=path, json=data, raw=True)

    def _delete(self, adapter_name, node_id, cnx_uuid, delete_entities=False):
        """Delete a connection from an adapter.

        Args:
            adapter_name (TYPE): Description
            node_id (:obj:`str`): Node ID.
            cnx_uuid (TYPE): Description
            delete_entities (bool, optional): Description

        Returns:
            :obj: `object`

        Deleted Parameters:
            name (:obj:`str`): Name of adapter to delete connection from.
            id (:obj:`str`): ID of connection to remove.

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
        """Add a connection to an adapter.

        Args:
            adapter_name (TYPE): Description
            node_id (:obj:`str`): Node ID.
            config (:obj:`dict`): Client configuration.
            cnx_uuid (TYPE): Description

        Returns:
            :obj: `object`

        Deleted Parameters:
            adapter (:obj:`str`): Name of adapter to add connection to.

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
    """Pass."""

    def parse(self, adapter, settings):
        """Pass.

        Args:
            adapter (TYPE): Description
            settings (TYPE): Description

        Returns:
            TYPE: Description

        Raises:
            exceptions.CnxSettingMissing: Description

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
        """Pass.

        Args:
            name (TYPE): Description
            value (TYPE): Description
            schema (TYPE): Description
            adapter (TYPE): Description

        Returns:
            TYPE: Description

        Raises:
            exceptions.CnxSettingInvalidChoice: Description
            exceptions.CnxSettingInvalidType: Description
            exceptions.CnxSettingUnknownType: Description

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
            if isinstance(value, tools.STR):
                value = [x.strip() for x in value.split(",")]
            if isinstance(value, tools.LIST) and all(
                [isinstance(x, tools.STR) for x in value]
            ):
                return value
        elif type_str == "string":
            if isinstance(value, tools.STR):
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
        """Pass.

        Args:
            name (TYPE): Description
            value (TYPE): Description
            schema (TYPE): Description
            adapter (TYPE): Description

        Returns:
            TYPE: Description

        Raises:
            exceptions.CnxSettingFileMissing: Description
            exceptions.CnxSettingInvalidType: Description

        """
        is_str = isinstance(value, tools.STR)
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
    """Pass."""

    def parse(self):
        """Pass.

        Returns:
            TYPE: Description

        """
        parsed = []

        for name, raw_adapters in self._raw.items():
            for raw in raw_adapters:
                adapter = self._adapter(name=name, raw=raw)
                parsed.append(adapter)

        return parsed

    def _adapter(self, name, raw):
        """Pass.

        Args:
            name (TYPE): Description
            raw (TYPE): Description

        Returns:
            TYPE: Description

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
        """Pass.

        Args:
            raw (TYPE): Description
            base (bool, optional): Description

        Returns:
            TYPE: Description

        """
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
        """Pass.

        Args:
            raw (TYPE): Description

        Returns:
            TYPE: Description

        """
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
        """Pass.

        Args:
            raw (TYPE): Description
            parent (TYPE): Description

        Returns:
            TYPE: Description

        """
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


def validate_csv(name, content, is_users=False, is_installed_sw=False):
    """Pass.

    Args:
        name (TYPE): Description
        content (TYPE): Description
        is_users (bool, optional): Description
        is_installed_sw (bool, optional): Description

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
    if isinstance(headers_content, tools.BYTES):
        headers_content = headers_content.decode()

    headers = headers_content.splitlines()[0].lower().split(",")
    headers_has_any_id = any([x in headers for x in ids])

    if not headers_has_any_id:
        warnings.warn(
            exceptions.CnxCsvWarning(
                ids_type=ids_type, ids=ids, name=name, headers=headers
            )
        )


# REST API FR: public REST API does not support setting advanced settings
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

# REST API FR: date_fetched for client seems to be only for
# when fetch has been triggered from "save" in adapters>client page??
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
