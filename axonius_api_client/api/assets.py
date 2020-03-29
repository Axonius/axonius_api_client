# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ipaddress
import re

from .. import constants, exceptions, tools
from . import adapters, mixins, routers


class AssetMixin(mixins.ModelAsset, mixins.Mixins):
    """API model for working with user and device assets."""

    def _init(self, auth, **kwargs):
        """Post init method for subclasses to use for extra setup.

        Args:
            auth (:obj:`.auth.Model`): object to use for auth and sending API requests
        """
        # cross reference
        self.adapters = adapters.Adapters(auth=auth, **kwargs)

        # children
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)
        self.fields = Fields(parent=self)
        self.reports = Reports(parent=self)

        super(AssetMixin, self)._init(auth=auth, **kwargs)

    def _count(self, query=None):
        """Direct API method to get the count of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return the count of all assets
                * if :obj:`str` return the count of assets that match a
                  query built by the GUI query wizard

        Returns:
            :obj:`int`: count of assets matching query
        """
        params = {}
        if query:
            params["filter"] = query

        return self._request(method="post", path=self._router.count, json=params)

    def _get(self, query=None, fields=None, row_start=0, page_size=0):
        """Direct API method to get a page of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return all assets
                * if :obj:`str` return the assets that match a query built
                  by the GUI query wizard
            fields (:obj:`list` of :obj:`str` or :obj:`str`): default ``None`` -

                * if :obj:`str` CSV seperated list of fields (columns) to include in
                  return
                * if :obj:`list` of :obj:`str` the strs of fields (columns) to include
                  in return
            row_start (:obj:`int`, optional): default ``0`` - for paging, skip N rows
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows

        Returns:
            :obj:`list` of :obj:`dict`: assets matching **query** with key/value pairs
                requested as per **fields**
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
            params["filter"] = query

        if fields:
            if isinstance(fields, constants.LIST):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self._request(method="post", path=self._router.root, json=params)

    def _get_by_id(self, id):
        """Direct API method to get the full metadata of all adapters for a single asset.

        Args:
            id (:obj:`str`): internal_axon_id of asset to get all metadata for

        Returns:
            :obj:`dict`: dict with all metadata for all adapters for asset with
                **id** of internal_axon_id
        """
        path = self._router.by_id.format(id=id)
        return self._request(method="get", path=path)

    def count(self, query=None):
        """Get the count of assets.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return the count of all assets
                * if :obj:`str` return the count of assets that match a
                  query built by the GUI query wizard

        Returns:
            :obj:`int`: count of assets matching query
        """
        return self._count(query=query)

    def count_by_saved_query(self, name):
        """Get the count of assets that would be returned by a saved query.

        Args:
            name (:obj:`str`): name of saved query to get count of assets from

        Returns:
            :obj:`int`: count of assets matching query in saved query
        """
        sq = self.saved_query.get_by_name(value=name, match_count=1, match_error=True)
        return self._count(query=sq["view"]["query"]["filter"])

    def get(self, generator=False, **kwargs):
        """Get objects for a given query using paging.

        Args:
            generator (:obj:`bool`, optional): default ``False`` -

                * True: return an iterator for assets that will yield assets
                  as they are fetched
                * False: return a list of assets after all assets have been fetched
            **kwargs: passed to :meth:`get_generator`

        Yields:
            :obj:`dict`: asset matching **query** if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching **query** if generator is False
        """
        kwargs.setdefault("all_fields", self.fields.get())
        gen = self.get_generator(**kwargs)

        if generator:
            return gen

        return list(gen)

    def get_generator(
        self,
        query=None,
        fields=None,
        fields_manual=None,
        fields_regex=None,
        fields_default=True,
        fields_error=True,
        max_rows=None,
        max_pages=None,
        page_size=constants.MAX_PAGE_SIZE,
        page_start=0,
        all_fields=None,
    ):
        """Get an iterator of objects for a given query using paging.

        Args:
            query (:obj:`str`, optional): default ``None`` -

                * if ``None`` return all assets
                * if :obj:`str` return the assets that match a query built
                  by the GUI query wizard
            fields (:obj:`list` of :obj:`str`, optional): default ``None`` -
                the fields to include for each asset, will be validated and
                processed into their fully qualified name using
                :meth:`Fields.validate`
            fields_manual (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fully qualified fields to include for each asset
            fields_regex (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fields to add using regular expression matches, will be
                validated and process into the matching fully qualified names using
                :meth:`Fields.validate`
            fields_default (:obj:`bool`, optional): default ``True`` -
                Include the fields in _default_fields
            fields_error (:obj:`bool`, optional): default ``True`` -
                throw an exception if fields fail to be validated by
                :meth:`Fields.validate`
            max_rows (:obj:`int`, optional): default ``None`` - return N assets
            max_pages (:obj:`int`, optional): default ``None`` - return N pages of assets
            page_size (:obj:`int`, optional):
                default default :data:`constants.MAX_PAGE_SIZE` -
                return N assets per page
            page_start (:obj:`int`, optional): default ``0`` - start at page N
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                fields to validate against in :meth:`Fields.validate`.
                If not supplied, will use return of :meth:`Fields.get`

        Yields:
            :obj:`dict`: asset matching **query**
        """
        fields = self.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            error=fields_error,
            default=fields_default,
            all_fields=all_fields,
        )

        if not page_size or page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page_size={ps} to max_page_size={mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)

            page_size = constants.MAX_PAGE_SIZE

        page_info = {}
        page_num = 0
        rows_fetched = 0
        row_start = page_start * page_size
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
            ]
            self._log.debug(tools.join_comma(obj=msg))
            page = self._get(
                query=query, fields=fields, row_start=row_start, page_size=page_size,
            )

            assets = page["assets"]
            page_info = page["page"]

            this_rows_fetched = len(assets)
            rows_fetched += this_rows_fetched
            row_start += this_rows_fetched

            msg = [
                "Fetched page_num={}".format(page_num),
                "page_took={}".format(tools.dt_sec_ago(obj=page_start)),
                "rows_fetched={}".format(rows_fetched),
                "page_info={}".format(page_info),
            ]
            self._log.debug(tools.join_comma(obj=msg))

            for asset in assets:
                yield asset

            if not assets:
                msg = "Stopped fetch loop, page with no assets returned"
                self._log.debug(msg)
                break

            if max_pages and page_num >= max_pages:
                msg = "Stopped fetch loop, hit max_pages={mp}"
                msg = msg.format(mp=max_pages)
                self._log.debug(msg)
                break

            if max_rows and rows_fetched >= max_rows:
                msg = "Stopped fetch loop, hit max_rows={mr} with rows_fetched={rf}"
                msg = msg.format(mr=max_rows, rf=rows_fetched)
                self._log.debug(msg)
                break

        msg = [
            "Finished get: rows_fetched={}".format(rows_fetched),
            "total_rows={}".format(page_info.get("totalResources", 0)),
            "fetch_took={}".format(tools.dt_sec_ago(obj=fetch_start)),
            "query={!r}".format(query or ""),
            "fields={!r}".format(fields),
        ]
        self._log.debug(tools.join_comma(obj=msg))

    def get_by_id(self, id):
        """Get the full metadata of all adapters for a single asset.

        Args:
            id (:obj:`str`): internal_axon_id of asset to get all metadata for

        Raises:
            :exc:`exceptions.ValueNotFound`: if asset is not found with supplied **id**

        Returns:
            :obj:`dict`: dict with all metadata for all adapters for asset with
                **id** of internal_axon_id
        """
        try:
            return self._get_by_id(id=id)
        except exceptions.JsonError as exc:
            msg = "Axonius ID for {t}".format(t=self._router._object_type)
            raise exceptions.ValueNotFound(value=id, value_msg=msg, exc=exc)

    def get_by_saved_query(self, name, **kwargs):
        """Get assets that would be returned by a saved query.

        Args:
            name (:obj:`str`): name of saved query to get count of assets from
            **kwargs: passed to :meth:`get`

        Yields:
            :obj:`dict`: asset matching **query** if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching **query** if generator is False
        """
        sq = self.saved_query.get_by_name(value=name, match_count=1, match_error=True)
        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["fields_manual"] = sq["view"]["fields"]
        kwargs["fields_default"] = False
        return self.get(**kwargs)

    def get_by_value(
        self,
        value,
        field,
        value_regex=False,
        value_not=False,
        query_pre="",
        query_post="",
        match_count=None,
        match_error=True,
        eq_single=True,
        **kwargs
    ):
        """Build query to get an asset by field value.

        Args:
            value (:obj:`str` or :obj:`list` of :obj:`str`): value of **field** to
                build query for
            field (:obj:`str`): field to build query for
            value_regex (:obj:`bool`, optional): default ``False`` - build a query
                that uses a regular expression to find **field** matching **value**
            value_not (:obj:`bool`, optional): default ``False`` - build a query
                where **field** does NOT match **value**
            query_pre (:obj:`str`, optional): default ``True`` - str to prefix to query
                that is built
            query_post (:obj:`str`, optional): default ``True`` - str to postfix to
                query that is built
            match_count (:obj:`int`, optional): default ``True`` - number of assets
                that are expected to be returned
            match_error (:obj:`bool`, optional): default ``True`` - throw error if
                **match_count** is supplied and number of assets returned is not
                equal to supplied value
            eq_single (:obj:`bool`, optional): default ``True`` - if **value_regex**
                is False and **value_not** is False and value is str and query_post
                is not supplied, set **max_rows** to 1, **match_count** to 1,
                and match_error to True
            **kwargs: passed to :meth:`get`

        Raises:
            :exc:`exceptions.ValueNotFound`: if **match_count** is supplied and
                **match_error** is True and the number of matches does not equal
                **match_count**

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        all_fields = kwargs.get("all_fields") or self.fields.get()

        field = self.fields.find_single(field=field, all_fields=all_fields)

        if isinstance(value, constants.LIST):
            value = ", ".join(["'{}'".format(v.strip()) for v in value])
            search = "in [{}]".format(value)
        else:
            if value_regex:
                search = '== regex("{}", "i")'.format(value)
            else:
                search = '== "{}"'.format(value)

                if eq_single and (not query_post and not value_not):
                    kwargs["max_rows"] = 1
                    match_count = 1
                    match_error = True

        not_flag = "not " if value_not else ""
        query = "{query_pre} {not_flag}({field} {search}) {query_post}"
        query = query.format(
            not_flag=not_flag,
            field=field,
            search=search,
            query_pre=query_pre,
            query_post=query_post,
        ).strip()

        kwargs["query"] = query
        kwargs["all_fields"] = all_fields
        rows = self.get(**kwargs)

        if (match_count and len(rows) != match_count) and match_error:
            value_msg = "{o} by field {f!r} value {v!r}"
            value_msg = value_msg.format(o=self._router._object_type, f=field, v=value)
            raise exceptions.ValueNotFound(value=query, value_msg=value_msg)

        if match_count == 1 and len(rows) == 1:
            return rows[0]

        return rows


class Users(AssetMixin):
    """User related API methods."""

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.users

    @property
    def _default_fields(self):
        """Fields to add to **fields** arg for :meth:`get_generator`.

        Returns:
            :obj:`list` of :obj:`dict`: Fields to add to **fields** arg for
                :meth:`get_generator`
        """
        return [
            "labels",
            "adapters",
            "specific_data.data.id",
            "specific_data.data.fetch_time",
            "specific_data.data.username",
            "specific_data.data.mail",
        ]

    def get_by_username(self, value, **kwargs):
        """Build a query to get assets by value of field ``name``.

        Args:
            value (:obj:`str`): value to that must match field "username"
            **kwargs: passed to :meth:`AssetMixin.get_by_value`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        kwargs.pop("field", None)
        return self.get_by_value(
            value=value, field="specific_data.data.username", **kwargs
        )

    def get_by_mail(self, value, **kwargs):
        """Build a query to get assets by value of field ``mail``.

        Args:
            value (:obj:`str`): value to that must match field "mail"
            **kwargs: passed to :meth:`AssetMixin.get_by_value`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        kwargs.pop("field", None)
        return self.get_by_value(value=value, field="specific_data.data.mail", **kwargs)


class Devices(AssetMixin):
    """Device related API methods."""

    @property
    def _router(self):
        """Router for this API model.

        Returns:
            :obj:`.routers.Router`: REST API route defs
        """
        return routers.ApiV1.devices

    @property
    def _default_fields(self):
        """Fields to add to **fields** arg for :meth:`get_generator`.

        Returns:
            :obj:`list` of :obj:`dict`: Fields to add to **fields** arg for
                :meth:`get_generator`
        """
        return [
            "labels",
            "adapters",
            "specific_data.data.id",
            "specific_data.data.fetch_time",
            "specific_data.data.hostname",
            "specific_data.data.network_interfaces.ips",
        ]

    def get_by_hostname(self, value, **kwargs):
        """Build a query to get assets by value of field ``hostname``.

        Args:
            value (:obj:`str`): value to that must match field "hostname"
            **kwargs: passed to :meth:`AssetMixin.get_by_value`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        kwargs.pop("field", None)
        return self.get_by_value(
            value=value, field="specific_data.data.hostname", **kwargs
        )

    def get_by_mac(self, value, **kwargs):
        """Build a query to get assets by value of field ``network_interfaces.mac``.

        Args:
            value (:obj:`str`): value to that must match field "network_interfaces.mac"
            **kwargs: passed to :meth:`AssetMixin.get_by_value`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        kwargs.pop("field", None)
        return self.get_by_value(
            value=value, field="specific_data.data.network_interfaces.mac", **kwargs
        )

    def get_by_ip(self, value, **kwargs):
        """Build a query to get assets by value of field ``network_interfaces.ips``.

        Args:
            value (:obj:`str`): value to that must match field "network_interfaces.ips"
            **kwargs: passed to :meth:`AssetMixin.get_by_value`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        kwargs.pop("field", None)
        return self.get_by_value(
            value=value, field="specific_data.data.network_interfaces.ips", **kwargs
        )

    def get_by_subnet(
        self, value, value_not=False, query_pre="", query_post="", **kwargs
    ):
        """Build a query to get assets by value of field ``network_interfaces.ips_raw``.

        Args:
            value (:obj:`str`): value to that must match field
                "network_interfaces.ips_raw"
            **kwargs: passed to :meth:`AssetMixin.get`

        Yields:
            :obj:`dict`: asset matching query that is built if generator is True

        Returns:
            :obj:`list` of :obj:`dict`: assets matching query that is built
                if generator is False
        """
        network = ipaddress.ip_network(value)

        begin = int(network.network_address)
        end = int(network.broadcast_address)

        field = "specific_data.data.network_interfaces.ips_raw"

        search = '== match({{"$gte": {begin}, "$lte": {end}}})'
        search = search.format(begin=begin, end=end)

        not_flag = "not " if value_not else ""
        query = "{query_pre} {not_flag}{field} {search} {query_post}"
        query = query.format(
            not_flag=not_flag,
            field=field,
            search=search,
            query_pre=query_pre,
            query_post=query_post,
        ).strip()

        kwargs.pop("query", None)
        kwargs.pop("value_regex", None)
        return self.get(query=query, **kwargs)


class SavedQuery(mixins.Child):
    """Child API model for working with saved queries for the parent asset type."""

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
        """Direct API method to create a saved query.

        Warning:
            Queries created with this method will NOT show the filters in the
            query wizard!

        Args:
            name (:obj:`str`): name of saved query to create
            query (:obj:`str`): query built by GUI query wizard
            fields (:obj:`object`): fields/columns
            sort (:obj:`str`, optional): default ``None`` - field to sort results on
            sort_descending (:obj:`bool`, optional): default ``True`` - sort on
                **field** in descending order
            column_filters (:obj:`dict`, optional): default ``None`` - column
                filters keyed as field_name:value
            gui_page_size (:obj:`int`, optional): default ``None`` -
                show N rows per page in GUI

        Returns:
            :obj:`str`: ID of the saved query that was created
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
        """Direct API method to delete saved queries.

        Args:
            ids (:obj:`list` of :obj:`str`): list of saved query uuid's to delete

        Returns:
            :obj:`str`: empty string
        """
        data = {"ids": tools.listify(ids)}

        path = self._parent._router.views

        return self._parent._request(method="delete", path=path, json=data)

    def _get(self, query=None, row_start=0, page_size=None):
        """Direct API method to get saved queries.

        Args:
            query (:obj:`str`, optional): default ``None`` - filter rows to return

                This is NOT a query built by the query wizard!
            row_start (:obj:`int`, optional): default ``0`` - for paging, skip N rows
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows

        Returns:
            :obj:`list` of :obj:`dict`: list of saved query metadata
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
        fields_regex=None,
        fields_manual=None,
        fields_default=True,
        fields_error=True,
        sort=None,
        sort_descending=True,
        column_filters=None,
        gui_page_size=None,
    ):
        """Create a saved query.

        Warning:
            Queries created with this method will NOT show the filters in the
            query wizard!

        Args:
            name (:obj:`str`): name of saved query to create
            query (:obj:`str`): query built by GUI query wizard
            fields (:obj:`object`): fields/columns
            fields_manual (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fully qualified fields to include for each asset
            fields_regex (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fields to add using regular expression matches, will be
                validated and process into the matching fully qualified names using
                :meth:`Fields.validate`
            fields_default (:obj:`bool`, optional): default ``True`` -
                Include the fields in _default_fields
            fields_error (:obj:`bool`, optional): default ``True`` -
                throw an exception if fields fail to be validated by
                :meth:`Fields.validate`
            sort (:obj:`str`, optional): default ``None`` - field to sort results on
            sort_descending (:obj:`bool`, optional): default ``True`` - sort on
                **field** in descending order
            column_filters (:obj:`dict`, optional): default ``None`` - column
                filters keyed as field_name:value
            gui_page_size (:obj:`int`, optional): default ``None`` -
                show N rows per page in GUI

        Returns:
            :obj:`dict`: metadata of saved query that was created
        """
        all_fields = self._parent.fields.get()

        fields = self._parent.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
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

        return self.get_by_id(value=added)

    def delete(self, rows):
        """Delete a saved query by name.

        Args:
            rows (:obj:`list` of :obj:`dict`): metadata of saved queries to delete

        Returns:
            :obj:`str`: empty string
        """
        return self._delete(
            ids=[x["uuid"] for x in tools.listify(obj=rows, dictkeys=False)]
        )

    def get(self, query=None, max_rows=None, max_pages=None, page_size=None):
        """Get saved queries using paging.

        Args:
            query (:obj:`str`, optional): default ``None`` - filter rows to return

                This is NOT a query built by the query wizard!
            page_size (:obj:`int`, optional): default ``0`` - for paging, return N rows
            max_rows (:obj:`int`, optional): default ``None`` - return N assets

        Returns:
            :obj:`list` of :obj:`dict`: list of saved query metadata
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
        self._log.debug(tools.join_comma(obj=msg))

        return rows

    def get_by_id(self, value, match_error=True, **kwargs):
        """Get a saved query by ID.

        Args:
            value (:obj:`str`): id of saved query to get
            match_error (:obj:`bool`, optional): default ``True`` - throw exc
                if match count is not 1
            **kwargs: passed to :meth:`get`

        Returns:
            :obj:`dict`: metadata for saved query with matching id of **value**

        Raises:
            :exc:`exceptions.ValueNotFound`: if **match_error** is True and the
                number of matches does not equal 1
        """
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

    def get_by_name(
        self,
        value,
        value_regex=False,
        value_not=False,
        match_count=None,
        match_error=True,
        eq_single=True,
        **kwargs
    ):
        """Get saved queries using paging.

        Args:
            value (:obj:`str`): name of saved query to get
            value_regex (:obj:`bool`, optional): default ``False`` - build a query
                that uses a regular expression to find name equals **value**
            value_not (:obj:`bool`, optional): default ``False`` - build a query
                where name does NOT match **value**
            match_count (:obj:`int`, optional): default ``True`` - number of assets
                that are expected to be returned
            match_error (:obj:`bool`, optional): default ``True`` - throw error if
                **match_count** is supplied and number of assets returned is not
                equal to supplied value
            eq_single (:obj:`bool`, optional): default ``True`` - if **value_regex**
                is False and **value_not** is False, set **max_rows** to 1,
                **match_count** to 1, and match_error to True
            **kwargs: passed to :meth:`get`

        Returns:
            :obj:`list` of :obj:`dict` or :obj:`dict`: object(s) matching query
        """
        if value_regex:
            search = '== regex("{}", "i")'.format(value)
        else:
            search = '== "{}"'.format(value)

            if eq_single and not value_not:
                kwargs["max_rows"] = 1
                match_count = 1
                match_error = True

        field = "name"
        not_flag = "not " if value_not else ""
        query = "{not_flag}{field} {search}"
        query = query.format(not_flag=not_flag, field=field, search=search).strip()
        kwargs["query"] = query

        rows = self.get(**kwargs)

        if (match_count and len(rows) != match_count) and match_error:
            ktmpl = "name: {name!r}, uuid: {uuid!r}".format
            known = [ktmpl(**row) for row in self.get()]
            known_msg = "Saved Queries"
            value_msg = "Saved Query by name using query {q}".format(q=query)
            raise exceptions.ValueNotFound(
                value=value, value_msg=value_msg, known=known, known_msg=known_msg
            )

        if match_count == 1 and len(rows) == 1:
            return rows[0]

        return rows


class Labels(mixins.Child):
    """Child API model for working with labels/tags for the parent asset type."""

    def _add(self, labels, ids):
        """Direct API method to add labels/tags to assets.

        Args:
            labels (:obj:`list` of `str`): labels to process
            ids (:obj:`list` of `str`): internal_axon_id of assets to add **labels** to

        Returns:
            :obj:`int`: number of labels processed
        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self._parent._router.labels
        return self._parent._request(method="post", path=path, json=data)

    def _get(self):
        """Direct API method to get all known labels/tags.

        Returns:
            :obj:`list` of :obj:`str`: all labels that exist in Axonius
        """
        path = self._parent._router.labels
        return self._parent._request(method="get", path=path)

    def _remove(self, labels, ids):
        """Direct API method to remove labels/tags from assets.

        Args:
            labels (:obj:`list` of `str`): labels to process
            ids (:obj:`list` of `str`): internal_axon_id of assets to remove
                **labels** from

        Returns:
            :obj:`int`: number of labels processed
        """
        data = {}
        data["entities"] = {}
        data["entities"]["ids"] = ids
        data["labels"] = labels

        path = self._parent._router.labels

        return self._parent._request(method="delete", path=path, json=data)

    def add(self, rows, labels):
        """Add labels/tags to assets.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets returned from :meth:`get`
                to process
            labels (:obj:`list` of `str`): labels to process

        Returns:
            :obj:`int`: number of labels processed
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
        """Get all known labels/tags.

        Returns:
            :obj:`list` of :obj:`str`: all labels that exist in Axonius
        """
        return self._get()

    def remove(self, rows, labels):
        """Remove labels/tags from assets.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets returned from :meth:`get`
                to process
            labels (:obj:`list` of `str`): labels to process

        Returns:
            :obj:`int`: number of labels processed
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
    """Child API model for working with fields for the parent asset type."""

    _GENERIC_ALTS = ["generic", "general", "specific", "agg", "aggregated"]
    """:obj:`list` of :obj:`str`: list of alternatives for 'generic' adapter."""
    _ALL_ALTS = ["all", "*", "specific_data"]
    """:obj:`list` of :obj:`str`: list of alternatives for getting 'all' fields."""

    def _get(self):
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: schema of all fields
        """
        return self._parent._request(method="get", path=self._parent._router.fields)

    def find_adapter(self, adapter, error=True, all_fields=None):
        """Find an adapter by name.

        Args:
            adapter (:obj:`str`): Description
            error (:obj:`bool`, optional): default ``True`` - throw exc if no
                matches found for **adapter**
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`tuple` of (:obj:`str`, :obj:`dict`):
                fully qualified name of adapter and its field schemas

        Raises:
            exceptions.ValueNotFound: if **adapter** does not match the name keys
                of any keys in **all_fields**
        """
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
        """Find a single field.

        Args:
            field (:obj:`str`): name of field to find
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`str`: validated and processed field
        """
        found = self.find(field=field, error=True, all_fields=all_fields)
        return found[0]

    def find(self, field, error=True, all_fields=None):
        """Find a field for a given adapter.

        Args:
            field (:obj:`str` or :obj:`list` of :obj:`str`): name(s) of fields
                to find
            error (:obj:`bool`, optional): default ``True`` - throw exc if field
                can not be found
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: validated and processed fields

        Raises:
            :exc:`exceptions.ValueNotFound`: if **field** not found and **error** is True
        """
        if field.startswith("MANUAL:"):
            return [tools.strip_left(obj=field, fix="MANUAL:").strip()]

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

    def find_regex(self, field, all_fields=None):
        """Find a field for a given adapter using regexes.

        Args:
            field (:obj:`str` or :obj:`list` of :obj:`str`): regex(es) of fields
                to find
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: validated and processed fields
        """
        all_fields = all_fields or self.get()

        check = field.strip()

        if ":" in check:
            search_adapter, search_fields = check.split(":", 1)
        else:
            search_adapter, search_fields = (".", check)

        search_adapter_fix = tools.strip_right(
            obj=search_adapter.lower().strip(), fix="_adapter"
        )

        search_adapter_re = re.compile(search_adapter_fix, re.I)
        found_adapters = {
            k: v for k, v in all_fields.items() if search_adapter_re.search(k)
        }

        search_fields_re = [
            re.compile(x.strip().lower(), re.I)
            for x in search_fields.split(",")
            if x.strip()
        ]

        found_fields = []

        for field_re in search_fields_re:
            for adapter, adapter_fields in found_adapters.items():
                for adapter_field, adapter_field_info in adapter_fields.items():
                    if field_re.search(adapter_field):
                        found_fields.append(adapter_field_info["name"])

        return found_fields

    def get(self):
        """Direct API method to get the schema of all fields.

        Returns:
            :obj:`dict`: parsed output from :meth:`ParserFields.parse`
        """
        raw = self._get()
        parser = ParserFields(raw=raw, parent=self)
        return parser.parse()

    def validate(
        self,
        fields=None,
        fields_regex=None,
        fields_manual=None,
        default=True,
        error=True,
        all_fields=None,
    ):
        """Validate provided fields.

        Args:
            fields (:obj:`list` of :obj:`str`, optional): default ``None`` -
                fields to parse, find, and add
            fields_regex (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fields to find and add using regular expression matches
            fields_manual (:obj:`list` of :obj:`str`, optional): default ``None`` -
                list of fully qualified fields to add
            fields_default (:obj:`bool`, optional): default ``True`` -
                add the fields in _default_fields from the parent asset object
            error (:obj:`bool`, optional): default ``True`` - throw exc if field
                can not be found
            all_fields (:obj:`list` of :obj:`dict`, optional): default ``None`` -
                if not supplied, will use return of :meth:`get`

        Returns:
            :obj:`list` of :obj:`str`: fields that have been parsed, fully qualified,
                and validated
        """

        def listify(obj):
            return [
                x for x in tools.listify(obj=obj) if isinstance(x, constants.STR) and x
            ]

        fields = listify(obj=fields)
        fields_manual = listify(obj=fields_manual)
        fields_regex = listify(obj=fields_regex)
        all_fields = all_fields or self.get()

        val_fields = []

        if default:
            val_fields += self._parent._default_fields

        val_fields += fields_manual

        for field in fields:
            found = self.find(field=field, all_fields=all_fields, error=error)
            val_fields += [x for x in found if x not in val_fields]

        for field_re in fields_regex:
            found_re = self.find_regex(field=field_re, all_fields=all_fields)
            val_fields += [x for x in found_re if x not in val_fields]

        return val_fields


class Reports(mixins.Child):
    """Child API model that provides special reports for the parent asset type."""

    def missing_adapters(self, rows, adapters=None, fields=None):
        """Report on assets that do not have data from configured adapters.

        Args:
            rows (:obj:`list` of :obj:`dict`): assets to add fields

                * 'missing' - adapters that have a connection and have fetched
                  at least one other asset yet are missing from an asset
                * 'missing_nocnx' - all adapters that do not have a connection and
                  as such are missing from an asset
            adapters (:obj:`dict`, optional): default ``None`` - previously fetched
                metadata for all adapters. will use
                :meth:`.adapters.Adapters.get` if not provided
            fields (:obj:`dict`, optional): default ``None`` - previously fetched
                fields for all adapters. will use :meth:`Fields.get` if not provided

        Returns:
            (:obj:`list` of :obj:`dict`): assets with 'missing' and 'missing_nocnx'
                fields added
        """
        adapters = adapters or self._parent.adapters.get()
        fields = fields or self._parent.fields.get()
        new_rows = []

        for raw_row in rows:
            # row = {k: v for k, v in raw_row.items() if "." in k or k in ["labels"]}
            row = {k: v for k, v in raw_row.items()}
            row["adapters"] = tools.strip_right(
                obj=tools.listify(obj=raw_row.get("adapters", [])), fix="_adapter"
            )
            row["missing_nocnx"] = []
            row["missing"] = []

            for adapter in adapters:
                # this row does not have data from this adapter
                if adapter["name"] not in row["adapters"]:
                    # this adapter has no connections
                    if not adapter["cnx"]:
                        row["missing_nocnx"].append(adapter["name"])
                    # this adapter has been fetched by other assets, but not this one
                    elif adapter["name"] in fields:
                        row["missing"].append(adapter["name"])

            new_rows.append(row)

        return new_rows


class ParserFields(mixins.Parser):
    """Parser to make the raw fields returned by the API into a more usable format."""

    def _exists(self, item, source, desc):
        """Sanity check to make sure an item is not duplicated during parsing.

        Args:
            item (:obj:`str`): name of item
            source (:obj:`list` of :obj:`str`): obj to check if item already exists in
            desc (:obj:`str`): description of item

        Raises:
            :exc:`exceptions.ApiError`: if item already exists in source
        """
        if item in source:
            msg = "{d} {i!r} already exists, duplicate??"
            msg = msg.format(d=desc, i=item)
            raise exceptions.ApiError(msg)

    def _generic(self):
        """Parse generic/aggregated fields.

        Returns:
            :obj:`dict`: parsed generic/aggregated fields
        """
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
        """Parse adapter specific fields.

        Args:
            name (:obj:`str`): adapter name
            raw_fields (:obj:`list` of :obj:`dict`): the raw unparsed fields for name

        Returns:
            :obj:`dict`: parsed adapter specific fields
        """
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
            # this does not work any more as of 2.1.2 - unsure why
            # "raw": {
            #     "name": "{}.raw".format(prefix),
            #     "title": "All raw data for {} adapter".format(prefix),
            #     "type": "array",
            #     "adapter_prefix": prefix,
            # },
        }

        for field in raw_fields:
            field["adapter_prefix"] = prefix
            field_name = tools.strip_left(obj=field["name"], fix=prefix).strip(".")
            self._exists(field_name, fields, "Adapter {} field".format(short_name))
            fields[field_name] = field

        return short_name, fields

    def parse(self):
        """Parse all generic and adapter specific fields.

        Returns:
            :obj:`dict`: parsed generic and adapter specific fields
        """
        ret = {}
        ret["generic"] = self._generic()

        for name, raw_fields in self._raw["specific"].items():
            short_name, fields = self._adapter(name=name, raw_fields=raw_fields)
            self._exists(short_name, ret, "Adapter {}".format(name))
            ret[short_name] = fields

        return ret
