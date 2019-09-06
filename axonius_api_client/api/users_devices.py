# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import ipaddress

from .. import constants, exceptions, tools
from . import adapters, mixins, routers

# TODO: include outdated!


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

    # FUTURE: BR for use_post, defaults to limit == 2000
    def _get(self, query=None, fields=None, row_start=0, paging_size=0, use_post=False):
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
            paging_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        params = {}
        params["skip"] = row_start
        params["limit"] = paging_size

        if query:
            if len(query) >= constants.QUERY_USE_POST_LENGTH:
                use_post = True

            params["filter"] = query

        if fields:
            if tools.is_type.list(fields):
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

    def count(self, query=None, use_post=False):
        """Get the number of matches for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI.

        Returns:
            :obj:`int`

        """
        return self._count(query=query, use_post=use_post)

    def get(
        self,
        *fields,
        query=None,
        fields_default=True,
        fields_error=True,
        count_min=None,
        count_max=None,
        count_error=True,
        paging_size=None,
        use_post=False,
    ):
        """Get objects for a given query using paging.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select rows to return.

                Defaults to: None.
            paging_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`axonius_api_client.constants.DEFAULT_PAGING_SIZE`.
            fields_default (:obj:`bool`, optional):
                Update fields with :attr:`_default_fields` if no fields supplied.

                Defaults to: True.
            kwargs: Fields to include in result.

                >>> generic=['f1', 'f2'] # for generic fields.
                >>> adapter=['f1', 'f2'] # for adapter specific fields.

        Returns:
            :obj:`list` of :obj:`dict` or :obj:`dict`

        """
        if paging_size is None:
            paging_size = constants.DEFAULT_PAGING_SIZE

        val_fields = self.fields.validate(
            searches=fields, error=fields_error, default=fields_default
        )

        if count_max is not None:
            if count_max < paging_size:
                paging_size = count_max

        count_total = 0

        rows = []

        msg = "Starting get with query {q!r} and fields {f!r}"
        msg = msg.format(q=query, f=val_fields)
        self._log.debug(msg)

        start = tools.dt.now()

        while True:
            page = self._get(
                query=query,
                fields=val_fields,
                row_start=count_total,
                paging_size=paging_size,
                use_post=use_post,
            )

            rows += page["assets"]
            count_total += len(page["assets"])

            do_break = self._check_counts(
                value=query,
                value_type="query",
                objtype=self._router._object_type,
                count_min=count_min,
                count_max=count_max,
                count_total=count_total,
                error=count_error,
            )

            if not page["assets"]:
                do_break = True

            if do_break:
                break

        msg = "Finished get with query {q!r} - returned {c} assets in {s} seconds"
        msg = msg.format(q=query, c=len(rows), s=tools.dt.seconds_ago(start))
        self._log.debug(msg)

        if count_max is not None:
            if count_max == 1 and rows:
                return rows[0]
            elif rows:
                return rows[:count_max]

        return rows

    def get_by_field_value(
        self,
        *fields,
        value,
        field,
        fields_default=True,
        fields_error=True,
        use_regex=False,
        not_flag=False,
        count_min=None,
        count_max=None,
        count_error=True,
        paging_size=None,
        use_post=False,
    ):
        """Build query to perform equals or regex search.

        Args:
            value (:obj:`str`):
                Value to search for equals or regex query against name.
            name (:obj:`str`):
                Field to use when building equals or regex query.
            adapter_name (:obj:`str`):
                Adapter name is from.
            regex (:obj:`bool`, optional):
                Build a regex instead of equals query.
            kwargs:
                Passed through to :meth:`get`.

        Returns:
            :obj:`list` of :obj:`dict` or :obj:`dict`

        """
        all_fields = self.fields.get()

        field = self.fields.find(field=field, all_fields=all_fields, error=True)[0]

        if use_regex:
            query = '{field} == regex("{value}", "i")'
            query = query.format(field=field, value=value)
        elif tools.is_type.list(value):
            jvalue = " ".join(["'{}'".format(v) for v in value])
            query = "{field} in [{value}]"
            query = query.format(field=field, value=jvalue)
        else:
            query = '{field} == "{value}"'
            query = query.format(field=field, value=value)
            count_min = 1
            count_max = 1
            count_error = True

        if not_flag:
            query = "not {q}".format(q=query)

        return self.get(
            *fields,
            query=query,
            fields_default=fields_default,
            fields_error=fields_error,
            count_min=count_min,
            count_max=count_max,
            count_error=count_error,
            paging_size=paging_size,
            use_post=use_post,
        )

    def get_by_id(self, id):
        """Get an object by internal_axon_id.

        Args:
           id (:obj:`str`):
               internal_axon_id of object to get.

        Raises:
           :exc:`exceptions.ObjectNotFound`:

        Returns:
           :obj:`dict`

        """
        try:
            return self._get_by_id(id=id)
        except exceptions.JsonError as exc:
            # ResponseError or JsonError??
            raise exceptions.ObjectNotFound(
                value=id,
                value_type="Axonius ID",
                object_type=self._router._object_type,
                exc=exc,
            )

    def get_by_saved_query(
        self,
        name,
        count_min=None,
        count_max=None,
        count_error=True,
        paging_size=None,
        use_post=False,
    ):
        """Pass."""
        sq = self.saved_query.get_by_name(
            value=name, use_regex=False, count_min=1, count_max=1
        )

        return self.get(
            *sq["view"]["fields"],
            query=sq["view"]["query"]["filter"],
            count_min=count_min,
            count_max=count_max,
            count_error=count_error,
            paging_size=paging_size,
            use_post=use_post,
        )

    def report_adapters(
        self, rows, serial=False, unconfigured=False, others_not_seen=False
    ):
        """Pass."""
        return ParserReportsAdapter(raw=rows, parent=self).parse(
            fields=self._parent.fields.get(),
            adapters=self.adapters.get(),
            serial=serial,
            unconfigured=unconfigured,
            others_not_seen=others_not_seen,
        )


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

    def get_by_username(self, *fields, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs["field"] = "specific_data.data.username"
        return self.get_by_field_value(*fields, value=value, **kwargs)

    def get_by_mail(self, *fields, value, **kwargs):
        """Get objects by email using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "mail".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["field"] = "specific_data.data.mail"
        return self.get_by_field_value(*fields, value=value, **kwargs)


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

    def get_by_hostname(self, *fields, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs["field"] = "specific_data.data.hostname"
        return self.get_by_field_value(*fields, value=value, **kwargs)

    def get_by_mac(self, *fields, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["field"] = "specific_data.data.network_interfaces.mac"
        return self.get_by_field_value(*fields, value=value, **kwargs)

    def get_by_ip(self, *fields, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["field"] = "specific_data.data.network_interfaces.ips"
        return self.get_by_field_value(*fields, value=value, **kwargs)

    def get_by_in_subnet(self, *fields, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["query"] = self._build_subnet_query(value=value, not_flag=False)
        return self.get(*fields, **kwargs)

    def get_by_not_in_subnet(self, *fields, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs["query"] = self._build_subnet_query(value=value, not_flag=True)
        return self.get(*fields, **kwargs)


class SavedQuery(mixins.Child):
    """Pass."""

    def _get(self, query=None, row_start=0, paging_size=None):
        """Get device saved queries.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get_saved_query_by_name` for an example query. Empty
                query will return all rows.

                Defaults to: None.
            row_start (:obj:`int`, optional):
                If not 0, skip N rows in the return.

                Defaults to: 0.
            paging_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        if paging_size is None:
            paging_size = constants.DEFAULT_PAGING_SIZE

        params = {}
        params["limit"] = paging_size
        params["skip"] = row_start

        if query:
            params["filter"] = query

        path = self._parent._router.views
        return self._parent._request(method="get", path=path, params=params)

    def _delete(self, ids):
        """Delete saved queries by ids.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of UUID's of saved queries to delete.

        Returns:
            :obj:`str`: empty string

        """
        data = {"ids": ids}
        path = self._parent._router.views
        return self._parent._request(method="delete", path=path, json=data)

    def _create(
        self,
        name,
        query,
        fields,
        sort_field=None,
        sort_field_descending=True,
        column_filters=None,
        gui_paging_size=None,
    ):
        """Create a saved query.

        Args:
            name (:obj:`str`):
                Name of saved query to create.
            query (:obj:`str`):
                Query built from Query Wizard in GUI to use in saved query.
            paging_size (:obj:`int`, optional):
                Number of rows to show in each page in GUI.

                Defaults to: first item in
                :data:`axonius_api_client.constants.GUI_PAGING_SIZES`.
            sort_field (:obj:`str`, optional):
                Name of field to sort results on.

                Defaults to: "".
            sort_descending (:obj:`bool`, optional):
                Sort sort_field descending.

                Defaults to: True.
            sort_adapter (:obj:`str`, optional):
                Name of adapter sort_field is from.

                Defaults to: "generic".

        Returns:
            :obj:`str`: The ID of the new saved query.

        """
        if gui_paging_size not in constants.GUI_PAGING_SIZES:
            gui_paging_size = constants.GUI_PAGING_SIZES[0]

        data = {}
        data["name"] = name
        data["query_type"] = "saved"

        data["view"] = {}
        data["view"]["fields"] = fields
        data["view"]["colFilters"] = column_filters or {}
        data["view"]["pageSize"] = gui_paging_size

        data["view"]["query"] = {}
        data["view"]["query"]["filter"] = query

        data["view"]["sort"] = {}
        data["view"]["sort"]["desc"] = sort_field_descending
        data["view"]["sort"]["field"] = sort_field or ""

        path = self._parent._router.views

        return self._parent._request(method="post", path=path, json=data)

    def create(
        self,
        *fields,
        name,
        query,
        fields_default=True,
        fields_error=True,
        sort_field=None,
        sort_field_manual=False,
        sort_field_descending=True,
        column_filters=None,
        gui_paging_size=None,
    ):
        """Create a saved query.

        Args:
            name (:obj:`str`):
                Name of saved query to create.
            query (:obj:`str`):
                Query built from Query Wizard in GUI to use in saved query.
            paging_size (:obj:`int`, optional):
                Number of rows to show in each page in GUI.

                Defaults to: first item in
                :data:`axonius_api_client.constants.GUI_PAGING_SIZES`.
            sort_field (:obj:`str`, optional):
                Name of field to sort results on.

                Defaults to: "".
            sort_descending (:obj:`bool`, optional):
                Sort sort_field descending.

                Defaults to: True.
            sort_adapter (:obj:`str`, optional):
                Name of adapter sort_field is from.

                Defaults to: "generic".

        Returns:
            :obj:`str`: The ID of the new saved query.

        """
        all_fields = self._parent.fields.get()

        val_fields = self._parent.fields.validate(
            *fields, default=fields_default, error=fields_error, all_fields=all_fields
        )

        if sort_field and not sort_field_manual:
            sort_field = self._parent.fields.find(
                field=sort_field, all_fields=all_fields, error=True
            )[0]

        created = self._create(
            name=name,
            query=query,
            fields=val_fields,
            column_filters=column_filters,
            sort_field=sort_field,
            sort_field_descending=sort_field_descending,
            gui_paging_size=gui_paging_size,
        )

        return self.get_by_id(value=created)

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
        if tools.is_type.list(rows):
            ids = [x["uuid"] for x in rows]
        else:
            ids = [rows["uuid"]]

        return self._delete(ids=ids)

    def get(self, query=None, count_min=None, count_max=None, paging_size=None):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional):
                Query to filter rows to return. This is NOT a query built by
                the Query Wizard in the GUI. This is something else. See
                :meth:`get` for an example query.

                Defaults to: None.
            paging_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`axonius_api_client.constants.DEFAULT_PAGING_SIZE`.
            max_rows (:obj:`int`, optional):
                If not 0, only return up to N rows.

                Defaults to: 0.

        Yields:
            :obj:`dict`: Each row found in 'assets' from return.

        """
        rows = []
        count_total = 0

        objtype = self._parent._router._object_type
        objtype = "Saved Query filter for {o}".format(o=objtype)

        while True:
            page = self._get(
                query=query, paging_size=paging_size, row_start=count_total
            )

            rows += page["assets"]
            count_total += len(page["assets"])

            do_break = self._parent._check_counts(
                value=query,
                value_type="query",
                objtype=objtype,
                count_min=count_min,
                count_max=count_max,
                count_total=count_total,
                known=sorted([x["name"] for x in self._get()]),
            )

            if not page["assets"]:
                do_break = True

            if do_break:
                break

        if count_max is not None:
            if count_max == 1 and rows:
                return rows[0]
            elif rows:
                return rows[:count_max]

        return rows

    def get_by_name(self, value, use_regex=False, not_flag=False, **kwargs):
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

        Raises:
            :exc:`exceptions.ObjectNotFound`

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
                kwargs.setdefault("count_min", 1)
                kwargs.setdefault("count_max", 1)
                kwargs.setdefault("count_error", True)

        if not_flag:
            query = "not {}".format(query)

        rows = self.get(query=query, **kwargs)

        count_max = kwargs.get("count_max", None)

        if count_max is not None:
            if count_max == 1 and rows:
                return rows[0]
            elif rows:
                return rows[:count_max]

        return rows

    def get_by_id(self, value, paging_size=None):
        """Get saved queries using paging.

        Args:
            name (:obj:`str`):
                Name of saved query to get.
            regex (:obj:`bool`, optional):
                Search for name using regex.

                Defaults to: True.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Raises:
            :exc:`exceptions.ObjectNotFound`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        rows = self.get(paging_size=paging_size)

        for row in rows:
            if row["uuid"] == value:
                return row

        objtype = self._parent._router._object_type
        objtype = "Saved Query by ID for {o}".format(o=objtype)

        raise exceptions.ObjectNotFound(
            value=value, value_type="Saved Query ID", object_type=objtype
        )


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

    def _delete(self, labels, ids):
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

    def _get(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        path = self._parent._router.labels

        return self._parent._request(method="get", path=path)

    def get(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._get()

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
            response = self._delete(labels=labels, ids=group)
            processed += response

        return processed


# FUTURE: how to get raw_data fields without using 'specific_data'
class Fields(mixins.Child):
    """Pass."""

    _GENERIC_ALTS = ["generic", "general", "specific"]
    _ALL_ALTS = ["all", "", "*", "specific_data"]
    _FORCE_SINGLE = ["specific_data", "specific_data.data"]

    def _get(self):
        """Get the fields.

        Returns:
            :obj:`dict`

        """
        return self._parent._request(method="get", path=self._parent._router.fields)

    def get(self):
        """Pass."""
        raw = self._get()
        parser = ParserFields(raw=raw, parent=self)
        return parser.parse()

    def find_adapter(self, adapter, error=True, all_fields=None):
        """Find an adapter by name."""
        all_fields = all_fields or self.get()

        check = tools.strip.right(adapter.lower(), "_adapter")

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
                known=list(all_fields),
                value_msg="adapter by name",
                known_msg="adapter names",
            )

        fmsg = "Failed to validate adapter {cn!r} (supplied {n!r})"
        fmsg = fmsg.format(n=adapter, cn=check)
        self._log.warning(fmsg)

        return None, {}

    def find(self, field, error=True, all_fields=None):
        """Find a field for a given adapter."""
        all_fields = all_fields or self.get()

        all_fq = [f["name"] for af in all_fields.values() for f in af.values()]

        if field.lower() in all_fq:
            fqmsg = "Validated field {sf!r} as already fully qualified"
            fqmsg = fqmsg.format(sf=field)
            self._log.debug(fqmsg)

            return [field]

        if ":" in field.lower():
            search_adapter, search_fields = field.lower().split(":", 1)
        else:
            search_adapter, search_fields = ("generic", field.lower())

        search_adapter = search_adapter.strip()
        search_fields = [x.strip() for x in search_fields.split(",") if x.strip()]

        real_adapter, real_fields = self.find_adapter(
            adapter=search_adapter, error=error, all_fields=all_fields
        )

        found = []

        if not real_adapter:
            return found

        for search_field in search_fields:
            found_field = None

            if search_field in self._ALL_ALTS:
                found_field = real_fields["all"]
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

    def validate(self, *fields, default=True, error=True, all_fields=None):
        """Validate provided fields."""
        all_fields = all_fields or self.get()

        if default:
            val_fields = self._parent._default_fields
        else:
            val_fields = []

        for field in fields:
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
        prefix = constants.GENERIC_FIELD_PREFIX
        all_prefix = prefix.split(".")[0]

        fields = {"all_data": {"name": prefix}, "all": {"name": all_prefix}}

        for field in self._raw["generic"]:
            field["adapter_prefix"] = prefix
            field_name = tools.strip.left(field["name"], prefix).strip(".")
            self._exists(field_name, fields, "Generic field")
            fields[field_name] = field

        return fields

    def _adapter(self, name, raw_fields):
        short_name = tools.strip.right(name, "_adapter")

        prefix = constants.ADAPTER_FIELD_PREFIX
        prefix = prefix.format(adapter_name=name)

        fields = {"all": {"name": prefix}, "raw": {"name": "{}.raw".format(prefix)}}

        for field in raw_fields:
            field["adapter_prefix"] = prefix
            field_name = tools.strip.left(field["name"], prefix).strip(".")
            self._exists(field_name, fields, "Adapter {} field".format(short_name))
            fields[field_name] = field

        return short_name, fields

    def parse(self):
        """Pass."""
        ret = {}
        ret["generic"] = self._generic()

        for name, raw_fields in self._raw["specific"].items():
            short_name, fields = self._adapter(name=name, raw_fields=raw_fields)
            self._exists(short_name, ret, "Adapter")
            ret[short_name] = fields

        return ret


class ParserReportsAdapter(mixins.Parser):
    """Pass."""

    def _mkserial(self, obj):
        """Pass."""
        if self._serial and tools.is_type.list(obj):
            return tools.join.cr(obj, pre=False)
        return obj

    def _row(self, raw_row):
        """Pass."""
        row = {}
        missing = []

        adapters = tools.strip.right(raw_row.get("adapters", []), "_adapter")
        row["adapters"] = self._mkserial(adapters)

        for k, v in raw_row.items():
            if "." in k or k in ["labels"]:
                row[k] = self._mkserial(v)

        ftimes = raw_row.get("specific_data.data.fetch_time", []) or []
        ftimes = ftimes if tools.is_type.list(ftimes) else [ftimes]
        ftimes = [x for x in tools.dt.parse(ftimes)]

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
