# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import ipaddress
import pdb  # noqa

from .. import constants, exceptions, tools
from . import adapters, mixins, routers


class UserDeviceMixin(mixins.ModelUserDevice, mixins.Mixins):
    """Mixins for User & Device models."""

    _LAST_GET = None

    def _init(self, auth, **kwargs):
        """Pass."""
        # cross reference
        self.adapters = adapters.Adapters(auth=auth, **kwargs)

        # children
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)
        self.fields = Fields(parent=self)

        super(UserDeviceMixin, self)._init(auth=auth, **kwargs)

    def _count(self, query=None, use_post=False):
        """Pass."""
        params = {}
        if query:
            if len(query) >= constants.QUERY_USE_POST_LENGTH:
                use_post = True

            params["filter"] = query

        if use_post:
            return self._request(method="post", path=self._router.count, json=params)
        else:
            return self._request(method="get", path=self._router.count, params=params)

    # FUTURE: BR for use_post, defaults to limit == 2000
    def _get(self, query=None, fields=None, row_start=0, page_size=0, use_post=False):
        """Get a page for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select rows to return.

                Defaults to: None.
            fields (:obj:`list` of :obj:`str` or :obj:`str`):
                List of fields to include in return.
                If str, CSV seperated list of fields.
                If list, strs of fields.

                Defaults to: None.
            row_start (:obj:`int`, optional):
                If not 0, skip N rows in the return.

                Defaults to: 0.
            page_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page size from {ps} to max page size {mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        params = {}
        params["skip"] = row_start
        params["limit"] = page_size

        if query:
            if len(query) >= constants.QUERY_USE_POST_LENGTH:
                use_post = True

            params["filter"] = query

        if fields:
            if isinstance(fields, tools.LIST):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        if use_post:
            return self._request(method="post", path=self._router.root, json=params)
        else:
            return self._request(method="get", path=self._router.root, params=params)

    def _get_by_id(self, id):
        """Pass."""
        path = self._router.by_id.format(id=id)
        return self._request(method="get", path=path)

    def count(self, query=None, use_post=False):
        """Get the number of matches for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI.

        Returns:
            :obj:`int`

        """
        return self._count(query=query, use_post=use_post)

    def find_by_value(
        self,
        value,
        field,
        use_regex=False,
        not_flag=False,
        match_count=None,
        match_error=True,
        **kwargs,
    ):
        """Build query to perform equals or regex search."""
        field = self.fields.find_single(field=field)

        if use_regex:
            query = '{field} == regex("{value}", "i")'
            query = query.format(field=field, value=value)
        elif isinstance(value, tools.LIST):
            jvalue = " ".join(["'{}'".format(v) for v in value])
            query = "{field} in [{value}]"
            query = query.format(field=field, value=jvalue)
        else:
            query = '{field} == "{value}"'
            query = query.format(field=field, value=value)

            if not not_flag:
                kwargs["max_rows"] = 1
                match_count = 1
                match_error = 1

        if not_flag:
            query = "not {q}".format(q=query)

        kwargs["query"] = query
        rows = self.get(**kwargs)

        if (match_count and len(rows) != match_count) and match_error:
            value_msg = "{o} by field {f!r} value {v!r}"
            value_msg = value_msg.format(o=self._router._object_type, f=field, v=value)
            raise exceptions.ValueNotFound(value=query, value_msg=value_msg)

        if match_count == 1 and len(rows) == 1:
            return rows[0]

        return rows

    def get(
        self,
        query=None,
        fields=None,
        fields_default=True,
        fields_error=True,
        max_rows=None,
        max_pages=None,
        page_size=None,
        use_post=False,
    ):
        """Get objects for a given query using paging."""
        fields = self.fields.validate(
            fields=fields, error=fields_error, default=fields_default
        )

        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page_size={ps} to max_page_size={mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        page_info = 0
        page_num = 0
        rows_fetched = 0
        rows = []
        fetch_start = tools.dt_now()

        msg = [
            "Starting get: page_size={}".format(page_size),
            "query={!r}".format(query or ""),
            "fields={!r}".format(fields),
        ]
        self._log.debug(tools.join_comma(msg))

        while True:
            page_start = tools.dt_now()
            page_num += 1
            rows_left = max_rows - len(rows) if max_rows else -1

            if 0 < rows_left < page_size:
                msg = "Changed page_size={ps} to rows_left={rl} (max_rows={mr})"
                msg = msg.format(ps=page_size, rl=rows_left, mr=max_rows)
                self._log.debug(msg)

                page_size = rows_left

            msg = [
                "Fetching page_num={}".format(page_num),
                "page_size={}".format(page_size),
                "rows_fetched={}".format(rows_fetched),
                "use_post={}".format(use_post),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            page = self._get(
                query=query,
                fields=fields,
                row_start=rows_fetched,
                page_size=page_size,
                use_post=use_post,
            )

            assets = page["assets"]
            page_info = page["page"]

            rows += assets
            rows_fetched += len(assets)

            msg = [
                "Fetched page_num={}".format(page_num),
                "page_took={}".format(tools.dt_sec_ago(obj=page_start)),
                "rows_fetched={}".format(rows_fetched),
                "page_info={}".format(page_info),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            if not assets:
                msg = "Stopped fetch loop, page with no assets returned"
                self._log.debug(msg)
                break

            if max_pages and page_num >= max_pages:
                msg = "Stopped fetch loop, hit max_pages={mp}"
                msg = msg.format(mp=max_pages)
                self._log.debug(msg)
                break

            if max_rows and len(rows) >= max_rows:
                msg = "Stopped fetch loop, hit max_rows={mr} with rows_fetched={rf}"
                msg = msg.format(mr=max_rows, rf=rows_fetched)
                self._log.debug(msg)
                break

        msg = [
            "Finished get: rows_fetched={}".format(rows_fetched),
            "total_rows={}".format(page_info["totalResources"]),
            "fetch_took={}".format(tools.dt_sec_ago(obj=fetch_start)),
            "query={!r}".format(query or ""),
            "fields={!r}".format(fields),
        ]
        self._log.info(tools.join_comma(obj=msg))

        return rows

    def get_by_id(self, id):
        """Get an object by internal_axon_id.

        Args:
           id (:obj:`str`):
               internal_axon_id of object to get.

        Returns:
           :obj:`dict`

        """
        try:
            return self._get_by_id(id=id)
        except exceptions.JsonError as exc:
            msg = "Axonius ID for {t}".format(t=self._router._object_type)
            raise exceptions.ValueNotFound(value=id, value_msg=msg, exc=exc)

    def get_by_saved_query(
        self, name, max_rows=None, max_pages=None, page_size=None, use_post=False
    ):
        """Pass."""
        sq = self.saved_query.find_by_name(value=name, use_regex=False)

        return self.get(
            query=sq["view"]["query"]["filter"],
            fields={"manual": sq["view"]["fields"]},
            max_rows=max_rows,
            max_pages=max_pages,
            page_size=page_size,
            use_post=use_post,
        )

    # def report_adapters(
    #     self, rows, serial=False, unconfigured=False, others_not_seen=False
    # ):
    #     """Pass."""
    #     return ParserReportsAdapter(raw=rows, parent=self).parse(
    #         fields=self._parent.fields.get(),
    #         adapters=self.adapters.get(),
    #         serial=serial,
    #         unconfigured=unconfigured,
    #         others_not_seen=others_not_seen,
    #     )


class Users(UserDeviceMixin):
    """User related API methods."""

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.users

    @property
    def _default_fields(self):
        """Fields to set as default for methods with fields as kwargs.

        Returns:
            :obj:`dict`

        """
        return [
            "labels",
            "specific_data.data.id",
            "specific_data.data.fetch_time",
            "specific_data.data.username",
            "specific_data.data.mail",
        ]

    def find_by_username(self, value, field="username", **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        return self.find_by_value(value=value, field=field, **kwargs)

    def find_by_mail(self, value, field="mail", **kwargs):
        """Get objects by email using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "mail".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        return self.find_by_value(value=value, field=field, **kwargs)


class Devices(UserDeviceMixin):
    """Device related API methods."""

    @property
    def _router(self):
        """Router for this API client.

        Returns:
            :obj:`axonius_api_client.api.routers.Router`

        """
        return routers.ApiV1.devices

    @property
    def _default_fields(self):
        """Fields to set as default for methods with fields as kwargs.

        Returns:
            :obj:`dict`

        """
        return [
            "labels",
            "specific_data.data.id",
            "specific_data.data.fetch_time",
            "specific_data.data.hostname",
            "specific_data.data.network_interfaces.ips",
        ]

    def _build_subnet_query(self, value, not_flag=False):
        """Pass."""
        network = ipaddress.ip_network(value)

        begin = int(network.network_address)
        end = int(network.broadcast_address)

        match_field = "specific_data.data.network_interfaces.ips_raw"

        match = 'match({{"$gte": {begin}, "$lte": {end}}})'
        match = match.format(begin=begin, end=end)
        if not_flag:
            query = "not {match_field} == {match}"
        else:
            query = "{match_field} == {match}"
        query = query.format(match_field=match_field, match=match)
        return query

    def find_by_hostname(self, value, field="hostname", **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        return self.find_by_value(value=value, field=field, **kwargs)

    def find_by_mac(self, value, field="network_interfaces.mac", **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        return self.find_by_value(value=value, field=field, **kwargs)

    def find_by_ip(self, value, field="network_interfaces.ips", **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        return self.find_by_value(value=value, field=field, **kwargs)

    def find_by_in_subnet(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["query"] = self._build_subnet_query(value=value, not_flag=False)
        return self.get(**kwargs)

    def find_by_not_in_subnet(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.find_by_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["query"] = self._build_subnet_query(value=value, not_flag=True)
        return self.get(**kwargs)


class SavedQuery(mixins.Child):
    """Pass."""

    def _add(
        self,
        name,
        query,
        fields,
        sort=None,
        sort_descending=True,
        column_filters=None,
        gui_page_size=None,
    ):
        """Create a saved query.

        Args:
            name (:obj:`str`):
                Name of saved query to create.
            query (:obj:`str`):
                Query built from Query Wizard in GUI to use in saved query.
            page_size (:obj:`int`, optional):
                Number of rows to show in each page in GUI.

                Defaults to: first item in
                :data:`axonius_api_client.constants.GUI_PAGE_SIZES`.
            sort (:obj:`str`, optional):
                Name of field to sort results on.

                Defaults to: "".
            sort_descending (:obj:`bool`, optional):
                Sort sort descending.

                Defaults to: True.
            sort_adapter (:obj:`str`, optional):
                Name of adapter sort is from.

                Defaults to: "generic".

        Returns:
            :obj:`str`: The ID of the new saved query.

        """
        if gui_page_size not in constants.GUI_PAGE_SIZES:
            gui_page_size = constants.GUI_PAGE_SIZES[0]

        data = {}
        data["name"] = name
        data["query_type"] = "saved"

        data["view"] = {}
        data["view"]["fields"] = fields
        data["view"]["colFilters"] = column_filters or {}
        data["view"]["pageSize"] = gui_page_size

        data["view"]["query"] = {}
        data["view"]["query"]["filter"] = query

        data["view"]["sort"] = {}
        data["view"]["sort"]["desc"] = sort_descending
        data["view"]["sort"]["field"] = sort or ""

        path = self._parent._router.views

        return self._parent._request(method="post", path=path, json=data)

    def _delete(self, ids):
        """Delete saved queries by ids.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of UUID's of saved queries to delete.

        Returns:
            :obj:`str`: empty string

        """
        data = {"ids": tools.listify(ids)}

        path = self._parent._router.views

        return self._parent._request(method="delete", path=path, json=data)

    def _get(self, query=None, row_start=0, page_size=None):
        """Get device saved queries.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`find_saved_query_by_name` for an example query. Empty
                query will return all rows.

                Defaults to: None.
            row_start (:obj:`int`, optional):
                If not 0, skip N rows in the return.

                Defaults to: 0.
            page_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page size from {ps} to max page size {mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        params = {}
        params["limit"] = page_size
        params["skip"] = row_start

        if query:
            params["filter"] = query

        path = self._parent._router.views

        return self._parent._request(method="get", path=path, params=params)

    def add(
        self,
        name,
        query,
        fields=None,
        fields_default=True,
        fields_error=True,
        sort=None,
        sort_descending=True,
        column_filters=None,
        gui_page_size=None,
    ):
        """Create a saved query.

        Args:
            name (:obj:`str`):
                Name of saved query to create.
            query (:obj:`str`):
                Query built from Query Wizard in GUI to use in saved query.
            page_size (:obj:`int`, optional):
                Number of rows to show in each page in GUI.

                Defaults to: first item in
                :data:`axonius_api_client.constants.GUI_PAGE_SIZES`.
            sort (:obj:`str`, optional):
                Name of field to sort results on.

                Defaults to: "".
            sort_descending (:obj:`bool`, optional):
                Sort sort descending.

                Defaults to: True.
            sort_adapter (:obj:`str`, optional):
                Name of adapter sort is from.

                Defaults to: "generic".

        Returns:
            :obj:`str`: The ID of the new saved query.

        """
        all_fields = self._parent.fields.get()

        fields = self._parent.fields.validate(
            fields=fields,
            default=fields_default,
            error=fields_error,
            all_fields=all_fields,
        )

        find_single = self._parent.fields.find_single

        if sort:
            sort = find_single(field=sort, all_fields=all_fields)

        if column_filters:
            column_filters = {
                find_single(field=k, all_fields=all_fields): v
                for k, v in column_filters.items()
            }

        added = self._add(
            name=name,
            query=query,
            fields=fields,
            column_filters=column_filters,
            sort=sort,
            sort_descending=sort_descending,
            gui_page_size=gui_page_size,
        )

        return self.find_by_id(value=added)

    def delete(self, rows):
        """Delete a saved query by name.

        Args:
            name (:obj:`str`):
                Name of saved query to delete.
            use_regex (:obj:`bool`, optional):
                Search for name using use_regex.

                Defaults to: False.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Returns:
            :obj:`str`: empty string

        """
        return self._delete(ids=[x["uuid"] for x in tools.listify(rows)])

    def get(self, query=None, max_rows=None, max_pages=None, page_size=None):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get` for an example query.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`axonius_api_client.constants.DEFAULT_PAGE_SIZE`.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.

        Yields:
            :obj:`dict`: Each row found in 'assets' from return.

        """
        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page_size={ps} to max_page_size={mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        page_info = 0
        page_num = 0
        rows_fetched = 0
        rows = []
        fetch_start = tools.dt_now()

        # objtype = self._parent._router._object_type
        # objtype = "Saved Query filter for {o}".format(o=objtype)

        msg = [
            "Starting get: page_size={}".format(page_size),
            "query={!r}".format(query or ""),
        ]
        self._log.debug(tools.join_comma(msg))

        while True:
            page_start = tools.dt_now()
            page_num += 1
            rows_left = max_rows - len(rows) if max_rows else -1

            if 0 < rows_left < page_size:
                msg = "Changed page_size={ps} to rows_left={rl} (max_rows={mr})"
                msg = msg.format(ps=page_size, rl=rows_left, mr=max_rows)
                self._log.debug(msg)

                page_size = rows_left

            msg = [
                "Fetching page_num={}".format(page_num),
                "page_size={}".format(page_size),
                "rows_fetched={}".format(rows_fetched),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            page = self._get(query=query, page_size=page_size, row_start=rows_fetched)

            assets = page["assets"]
            page_info = page["page"]

            rows += assets
            rows_fetched += len(assets)

            msg = [
                "Fetched page_num={}".format(page_num),
                "page_took={}".format(tools.dt_sec_ago(obj=page_start)),
                "rows_fetched={}".format(rows_fetched),
                "page_info={}".format(page_info),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            if not assets:
                msg = "Stopped fetch loop, page with no assets returned"
                self._log.debug(msg)
                break

            if max_pages and page_num >= max_pages:
                msg = "Stopped fetch loop, hit max_pages={mp}"
                msg = msg.format(mp=max_pages)
                self._log.debug(msg)
                break

            if max_rows and len(rows) >= max_rows:
                msg = "Stopped fetch loop, hit max_rows={mr} with rows_fetched={rf}"
                msg = msg.format(mr=max_rows, rf=rows_fetched)
                self._log.debug(msg)
                break

        msg = [
            "Finished get: rows_fetched={}".format(rows_fetched),
            "total_rows={}".format(page_info["totalResources"]),
            "fetch_took={}".format(tools.dt_sec_ago(obj=fetch_start)),
            "query={!r}".format(query or ""),
        ]
        self._log.info(tools.join_comma(obj=msg))

        return rows

    def find_by_id(self, value, match_error=True, **kwargs):
        """Get saved queries using paging."""
        rows = self.get(**kwargs)

        for row in rows:
            if row["uuid"] == value:
                return row

        if match_error:
            ktmpl = "name: {name!r}, uuid: {uuid!r}".format
            known = [ktmpl(**row) for row in rows]
            known_msg = "Saved Queries"
            value_msg = "Saved Query by UUID"
            raise exceptions.ValueNotFound(
                value=value, value_msg=value_msg, known=known, known_msg=known_msg
            )

        return None

    def find_by_name(
        self,
        value,
        use_regex=False,
        not_flag=False,
        match_count=None,
        match_error=True,
        **kwargs,
    ):
        """Get saved queries using paging.

        Args:
            name (:obj:`str`):
                Name of saved query to get.
            use_regex (:obj:`bool`, optional):
                Search for name using regex.

                Defaults to: True.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        if use_regex:
            query = 'name == regex("{value}", "i")'
            query = query.format(value=value)
        else:
            query = 'name == "{value}"'
            query = query.format(value=value)

            if not not_flag:
                kwargs["max_rows"] = 1
                match_count = 1
                match_error = 1

        if not_flag:
            query = "not {}".format(query)

        kwargs["query"] = query
        rows = self.get(**kwargs)

        if (match_count and len(rows) != match_count) and match_error:
            ktmpl = "name: {name!r}, uuid: {uuid!r}".format
            known = [ktmpl(**row) for row in self.get()]
            known_msg = "Saved Queries"
            value_msg = "Saved Query by name"
            raise exceptions.ValueNotFound(
                value=value, value_msg=value_msg, known=known, known_msg=known_msg
            )

        if match_count == 1 and len(rows) == 1:
            return rows[0]

        return rows


class Labels(mixins.Child):
    """Pass."""

    def _add(self, labels, ids):
        """Add labels to object IDs.

        Args:
            labels (:obj:`list` of `str`):
                Labels to add to ids.
            ids (:obj:`list` of `str`):
                Axonius internal object IDs to add to labels.

        Returns:
            :obj:`int`: Number of objects that had labels added

        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self._parent._router.labels

        return self._parent._request(method="post", path=path, json=data)

    def _get(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        path = self._parent._router.labels

        return self._parent._request(method="get", path=path)

    def _remove(self, labels, ids):
        """Delete labels from object IDs.

        Args:
            labels (:obj:`list` of `str`):
                Labels to delete from ids.
            ids (:obj:`list` of `str`):
                Axonius internal object IDs to delete from labels.

        Returns:
            :obj:`int`: Number of objects that had labels deleted.

        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self._parent._router.labels

        return self._parent._request(method="delete", path=path, json=data)

    def add(self, rows, labels):
        """Add labels to objects using rows returned from :meth:`get`.

        Args:
            rows (:obj:`list` of :obj:`dict`):
                Rows returned from :meth:`get`
            labels (:obj:`list` of `str`):
                Labels to add to rows.

        Returns:
            :obj:`int`: Number of objects that had labels added

        """
        ids = [row["internal_axon_id"] for row in rows]

        processed = 0

        # only do 100 labels at a time, more seems to break API
        for group in tools.grouper(ids, 100):
            group = [x for x in group if x is not None]
            response = self._add(labels=labels, ids=group)
            processed += response

        return processed

    def get(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._get()

    def remove(self, rows, labels):
        """Delete labels from objects using rows returned from :meth:`get`.

        Args:
            rows (:obj:`list` of :obj:`dict`):
                Rows returned from :meth:`get`
            labels (:obj:`list` of `str`):
                Labels to delete from rows.

        Returns:
            :obj:`int`: Number of objects that had labels deleted.

        """
        ids = [row["internal_axon_id"] for row in rows]

        processed = 0

        # only do 100 labels at a time, more seems to break API
        for group in tools.grouper(ids, 100):
            group = [x for x in group if x is not None]
            response = self._remove(labels=labels, ids=group)
            processed += response

        return processed


class Fields(mixins.Child):
    """Pass."""

    _GENERIC_ALTS = ["generic", "general", "specific"]
    _ALL_ALTS = ["all", "*", "specific_data"]

    def _get(self):
        """Get the fields.

        Returns:
            :obj:`dict`

        """
        return self._parent._request(method="get", path=self._parent._router.fields)

    def find_adapter(self, adapter, error=True, all_fields=None):
        """Find an adapter by name."""
        all_fields = all_fields or self.get()

        check = tools.strip_right(obj=adapter.lower().strip(), fix="_adapter")

        if check in self._GENERIC_ALTS:
            check = "generic"

        if check in all_fields:
            vmsg = "Validated adapter name {cn!r} (supplied {n!r})"
            vmsg = vmsg.format(n=adapter, cn=check)
            self._log.debug(vmsg)

            return check, all_fields[check]

        if error:
            raise exceptions.ValueNotFound(
                value=adapter,
                value_msg="adapter by name",
                known=list(all_fields),
                known_msg="adapter names",
            )

        fmsg = "Failed to validate adapter {cn!r} (supplied {n!r})"
        fmsg = fmsg.format(n=adapter, cn=check)
        self._log.warning(fmsg)

        return None, {}

    def find_single(self, field, all_fields=None):
        """Find a single field."""
        found = self.find(field=field, error=True, all_fields=all_fields)
        return found[0]

    def find(self, field, error=True, all_fields=None):
        """Find a field for a given adapter."""
        all_fields = all_fields or self.get()

        all_fq = [f["name"] for af in all_fields.values() for f in af.values()]

        check = field.strip()

        if check in all_fq:
            fqmsg = "Validated field {sf!r} as already fully qualified"
            fqmsg = fqmsg.format(sf=field)
            self._log.debug(fqmsg)

            return [check]

        if ":" in check:
            search_adapter, search_fields = check.split(":", 1)
        else:
            search_adapter, search_fields = ("generic", check)

        search_adapter = search_adapter.strip()
        search_fields = [
            x.strip().lower() for x in search_fields.split(",") if x.strip()
        ]

        real_adapter, real_fields = self.find_adapter(
            adapter=search_adapter, error=error, all_fields=all_fields
        )

        found = []

        if not real_adapter:
            return found

        for search_field in search_fields:
            found_field = None

            if search_field in self._ALL_ALTS:
                found_field = real_fields["all"]["name"]
            elif search_field in all_fq:
                found_field = search_field
            elif search_field in real_fields:
                found_field = real_fields[search_field]["name"]

            if not found_field:
                if error:
                    value_msg = "adapter {a!r} field"
                    value_msg = value_msg.format(a=real_adapter)

                    known_msg = "field names for adapter {a!r}"
                    known_msg = known_msg.format(a=real_adapter)

                    raise exceptions.ValueNotFound(
                        value=search_field,
                        known=list(real_fields),
                        value_msg=value_msg,
                        known_msg=known_msg,
                    )

                wmsg = "Failed to validate field {sf!r} for adapter {a!r} as {ff!r}"
                wmsg = wmsg.format(a=real_adapter, sf=search_field, ff=found_field)
                self._log.warning(wmsg)
            else:
                if found_field not in found:
                    found.append(found_field)

                vfmsg = "Validated field {sf!r} for adapter {a!r} as {ff!r}"
                vfmsg = vfmsg.format(a=real_adapter, sf=search_field, ff=found_field)
                self._log.debug(vfmsg)

        vsmsg = "Validated field search {s!r} as {f!r}"
        vsmsg = vsmsg.format(s=field, f=found)
        self._log.debug(vsmsg)

        return found

    def get(self):
        """Pass."""
        raw = self._get()
        parser = ParserFields(raw=raw, parent=self)
        return parser.parse()

    def validate(self, fields=None, default=True, error=True, all_fields=None):
        """Validate provided fields."""
        if isinstance(fields, dict) and "manual" in fields:
            return fields["manual"]

        all_fields = all_fields or self.get()
        fields = tools.listify(fields)

        if default:
            val_fields = self._parent._default_fields
        else:
            val_fields = []

        for field in [x for x in fields if isinstance(x, tools.STR) and x]:
            found = self.find(field=field, all_fields=all_fields, error=error)
            val_fields += [x for x in found if x not in val_fields]

        return val_fields


class ParserFields(mixins.Parser):
    """Pass."""

    def _exists(self, item, source, desc):
        """Pass."""
        if item in source:
            msg = "{d} {i!r} already exists, duplicate??"
            msg = msg.format(d=desc, i=item)
            raise exceptions.ApiError(msg)

    def _generic(self):
        """Pass."""
        fields = {
            "all_data": {
                "name": "specific_data.data",
                "title": "All data subsets for generic adapter",
                "type": "array",
                "adapter_prefix": "specific_data",
            },
            "all": {
                "name": "specific_data",
                "title": "All data for generic adapter",
                "type": "array",
                "adapter_prefix": "specific_data",
            },
        }

        for field in self._raw["generic"]:
            field["adapter_prefix"] = "specific_data"
            field_name = tools.strip_left(
                obj=field["name"], fix="specific_data.data"
            ).strip(".")
            self._exists(field_name, fields, "Generic field")
            fields[field_name] = field

        return fields

    def _adapter(self, name, raw_fields):
        short_name = tools.strip_right(obj=name, fix="_adapter")

        prefix = "adapters_data.{adapter_name}"
        prefix = prefix.format(adapter_name=name)

        fields = {
            "all": {
                "name": prefix,
                "title": "All data for {} adapter".format(prefix),
                "type": "array",
                "adapter_prefix": prefix,
            },
            "raw": {
                "name": "{}.raw".format(prefix),
                "title": "All raw data for {} adapter".format(prefix),
                "type": "array",
                "adapter_prefix": prefix,
            },
        }

        for field in raw_fields:
            field["adapter_prefix"] = prefix
            field_name = tools.strip_left(obj=field["name"], fix=prefix).strip(".")
            self._exists(field_name, fields, "Adapter {} field".format(short_name))
            fields[field_name] = field

        return short_name, fields

    def parse(self):
        """Pass."""
        ret = {}
        ret["generic"] = self._generic()

        for name, raw_fields in self._raw["specific"].items():
            short_name, fields = self._adapter(name=name, raw_fields=raw_fields)
            self._exists(short_name, ret, "Adapter {}".format(name))
            ret[short_name] = fields

        return ret


'''
class ParserReportsAdapter(mixins.Parser):
    """Pass."""

    def _mkserial(self, obj):
        """Pass."""
        if self._serial and isinstance(obj, tools.LIST):
            return tools.join_cr(obj=obj, pre=False)
        return obj

    def _row(self, raw_row):
        """Pass."""
        row = {}
        missing = []

        adapters = tools.strip_right(obj=raw_row.get("adapters", []), fix="_adapter")
        row["adapters"] = self._mkserial(adapters)

        for k, v in raw_row.items():
            if "." in k or k in ["labels"]:
                row[k] = self._mkserial(v)

        ftimes = raw_row.get("specific_data.data.fetch_time", []) or []

        if not isinstance(ftimes, tools.LIST):
            ftimes = [ftimes]

        ftimes = [x for x in tools.dt_parse(obj=ftimes)]

        for adapter in self._adapters:
            name = adapter["name"]

            otype = self._parent.__class__.__name__.upper()
            others_have_seen = name in self._fields

            is_unconfigured = not adapter["cnx"] or adapter["status"] is None

            skips = [
                is_unconfigured and not self._unconfigured,
                not others_have_seen and not self._others_not_seen,
            ]

            if any(skips):
                continue

            ftime = "NEVER; NO CONNECTIONS"

            if adapter["status"] is False:
                ftime = "NEVER; CONNECTIONS BROKEN"
            elif adapter["status"] is True:
                ftime = "NEVER; CONNECTIONS OK"

            if name in row["adapters"]:
                name_idx = row["adapters"].index(name)
                try:
                    ftime = ftimes[name_idx]
                except Exception:
                    ftime = "UNABLE TO DETERMINE"
            elif others_have_seen and name not in missing:
                missing.append(name)

            if self._serial:
                ftime = format(ftime)
                status_lines = [
                    "FETCHED THIS {}: {}".format(otype.rstrip("S"), ftime),
                    "FETCHED OTHER {}: {}".format(otype, others_have_seen),
                    "CONNECTIONS OK: {}".format(adapter["cnx_count_ok"]),
                    "CONNECTIONS BAD: {}".format(adapter["cnx_count_bad"]),
                ]
            else:
                status_lines = {
                    "FETCHED_THIS_{}".format(otype.rstrip("S")): ftime,
                    "FETCHED_OTHER_{}".format(otype): others_have_seen,
                    "CONNECTIONS_OK": adapter["cnx_count_ok"],
                    "CONNECTIONS_BAD": adapter["cnx_count_bad"],
                }

            row["adapter: {}".format(name)] = self._mkserial(status_lines)

        row["adapters_missing"] = self._mkserial(missing)
        return row

    def parse(
        self, adapters, fields, serial=False, unconfigured=False, others_not_seen=False
    ):
        """Pass."""
        self._adapters = adapters
        self._fields = fields
        self._serial = serial
        self._unconfigured = unconfigured
        self._others_not_seen = others_not_seen

        self._broken_adapters = [x for x in adapters if x["status"] is False]
        self._unconfig_adapters = [x for x in adapters if x["status"] is None]
        self._config_adapters = [x for x in adapters if x["status"] is True]

        return [self._row(x) for x in self._raw]

'''
