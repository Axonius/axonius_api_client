# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ipaddress
import math
import time

from .. import constants, exceptions, tools
from . import (adapters, asset_callbacks, fields, labels, mixins, reports,
               routers, saved_query)


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
        self.labels = labels.Labels(parent=self)
        self.saved_query = saved_query.SavedQuery(parent=self)
        self.fields = fields.Fields(parent=self)
        self.reports = reports.Reports(parent=self)

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

    def _get_cursor(
        self, query=None, fields=None, page_size=constants.PAGE_SIZE, cursor=None
    ):
        """Get a page for a given query."""
        page_size = self._page_size(page_size=page_size, max_rows=None)

        params = {}
        params["cursor"] = cursor
        params["limit"] = page_size

        if query:
            params["filter"] = query

        if fields:
            if isinstance(fields, tools.LIST):
                fields = ",".join(fields)

            params["fields"] = fields

        self._LAST_GET = params

        return self._request(method="post", path=self._router.cached, json=params)

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
        page_sleep=0,
        use_cursor=False,
        all_fields=None,
        **kwargs,
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
        all_fields = all_fields or self.fields.get()

        fields = self.fields.validate(
            fields=fields,
            fields_manual=fields_manual,
            fields_regex=fields_regex,
            error=fields_error,
            default=fields_default,
            all_fields=all_fields,
        )

        page_size = self._page_size(page_size=page_size, max_rows=max_rows)

        store = {
            "query": query,
            "fields": fields,
        }

        state = {
            "page": {},
            "page_cursor": None,
            "page_left": 0,
            "page_max": max_pages,
            "page_num": page_start,
            "page_size": page_size,
            "page_sleep": page_sleep,
            "page_total": 0,
            "rows_fetched": 0,
            "rows_max": max_rows,
            "rows_page": 0,
            "rows_start": page_start * page_size,
            "rows_total": 0,
            "time_fetch": 0,
            "time_page": 0,
        }

        cb_handler = asset_callbacks.Callbacks(
            apiobj=self, all_fields=all_fields, getargs=kwargs, store=store, state=state,
        )

        cb_handler.start()

        self._log.info("START FETCH store={}".format(store))

        while True:
            rows = self._page_get(state=state, store=store, use_cursor=use_cursor)

            for row in rows:
                row_items = cb_handler.row(row=row)

                for row_item in tools.listify(obj=row_items):
                    yield row_item

                if self._stop_rows(row=row, state=state, store=store, rows=rows):
                    break

            if self._stop_fetch(rows=rows, state=state, store=store):
                cb_handler.stop()
                break

            time.sleep(state["page_sleep"])

        self._log.info("FINISH FETCH store={}".format(store))

    def _page_handle(self, rows, state, store):
        rows_total_page = state["page"].get("page", {}).get("totalResources")
        rows_total = state["rows_total"]
        page_cursor = state["page_cursor"]
        page_size = state["page_size"]
        page_num = state["page_num"]

        if tools.is_int(rows_total_page):
            if page_cursor:
                if rows_total and rows_total_page != rows_total:
                    msg = "Total rows changed - old:{} new:{}"
                    msg = msg.format(rows_total, rows_total_page)
                    self._log.warning(msg)
            rows_total = rows_total_page

        page_total = math.ceil(rows_total_page / page_size)
        state["page_total"] = page_total
        state["page_left"] = page_total - page_num
        state["rows_total"] = rows_total

    def _page_get_cursor(self, state, store):
        state["page"] = self._get_cursor(
            query=store["query"],
            fields=store["fields"],
            page_size=state["page_size"],
            cursor=state["page_cursor"],
        )
        rows = state["page"].pop("assets", [])

        this_cursor = state["page"].get("cursor")
        old_cursor = state["page_cursor"]

        if old_cursor and this_cursor != old_cursor:
            raise exceptions.ApiError(
                "CURSOR CHANGED {!r} -> {!r} state={}, store={}".format(
                    old_cursor, this_cursor, state, store
                )
            )

        if not this_cursor:
            raise exceptions.ApiError("NO CURSOR RETURNED state={}".format(state))

        state["page_cursor"] = this_cursor
        return rows

    def _page_get_normal(self, state, store):
        state["page"] = self._get(
            query=store["query"],
            fields=store["fields"],
            row_start=state["rows_start"],
            page_size=state["page_size"],
        )
        rows = state["page"].pop("assets", [])
        return rows

    def _page_get(self, state, store, use_cursor=False):
        page_start = tools.dt_now()
        state["page_num"] += 1

        if use_cursor:
            rows = self._page_get_cursor(state=state, store=store)
        else:
            rows = self._page_get_normal(state=state, store=store)

        self._page_handle(state=state, store=store, rows=rows)
        time_page = tools.dt_sec_ago(obj=page_start)
        rows_page = len(rows)

        state["rows_start"] += rows_page
        state["rows_fetched"] += rows_page
        state["rows_page"] = rows_page
        state["time_page"] = time_page
        state["time_fetch"] += time_page

        self._log.debug("FETCHED PAGE: {}".format(state))

        return rows

    def _stop_rows(self, row, rows, state, store):
        pre = "STOPPED ROW LOOP: "
        if state["rows_max"] and state["rows_fetched"] >= state["rows_max"]:
            self._log.debug("{}hit rows_max".format(pre))
            return True
        return False

    def _stop_fetch(self, rows, state, store):
        pre = "STOPPED FETCH LOOP: "
        if not rows:
            self._log.debug("{}page with no rows returned".format(pre))
            return True

        if state["page_max"] and state["page_num"] >= state["page_max"]:
            self._log.debug("{}hit page_max".format(pre))
            return True

        if state["rows_max"] and state["rows_fetched"] >= state["rows_max"]:
            self._log.debug("{}hit rows_max".format(pre))
            return True

        if state.get("stop", False):
            self._log.debug("{}stop called".format(pre))
            return True

        return False

    def _page_size(self, page_size=constants.MAX_PAGE_SIZE, max_rows=None):
        max_page_size = constants.MAX_PAGE_SIZE

        pre = "CHANGED PAGE SIZE {} to ".format(page_size)

        if max_rows and max_rows < page_size:
            self._log.debug("{}max_rows={}".format(pre, max_rows))
            page_size = max_rows

        if page_size > max_page_size:
            self._log.debug("{}max_page_size={}, too high!".format(pre, max_page_size))
            page_size = max_page_size

        return page_size

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
        **kwargs,
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
            "internal_axon_id",
            "labels",
            "adapters",
            "adapter_list_length",
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
            "internal_axon_id",
            "labels",
            "adapters",
            "adapter_list_length",
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
