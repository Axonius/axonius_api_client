# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import ipaddress
import re
import time

from .. import cli, constants, exceptions, tools
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
        page_sleep=0,
        callbacks=None,
        callback_error=True,
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
        jdump = tools.json_dump
        schemas = self.fields.get_schemas(fields=fields, all_fields=all_fields)
        callbacks = tools.listify(obj=callbacks)
        page_size = self._figure_page_size(page_size=page_size, max_rows=max_rows)
        fetch_start_dt = tools.dt_now()
        getargs = {}
        getargs.update(kwargs)
        store = {
            "query": query,
            "fields": fields,
        }

        state = {
            "page_size": page_size,
            "page_info": {},
            "page_num": 0,
            "page_took": 0,
            "fetch_took": 0,
            "rows_fetched": 0,
            "rows_processed": 0,
            "row_start": page_start * page_size,
            "max_pages": max_pages,
            "max_rows": max_rows,
            "done": False,
        }

        jstate = jdump(state)

        self._log.debug("Starting fetch:\n{}".format(jstate))

        while True:
            page_start_dt = tools.dt_now()
            state["page_num"] += 1

            self._log.debug("Fetching:\n{}".format(jdump(state)))

            page = self._get(
                query=query,
                fields=fields,
                row_start=state["row_start"],
                page_size=page_size,
            )

            assets = page["assets"]
            state["page_info"] = page["page"]
            state["page_rows_fetched"] = len(assets)
            state["rows_fetched"] += len(assets)
            state["row_start"] += len(assets)
            state["page_took"] = tools.dt_sec_ago(obj=page_start_dt)
            state["fetch_took"] = tools.dt_sec_ago(obj=fetch_start_dt)
            self._log.debug("Fetched page:\n{}".format(jdump(state)))

            for asset in assets:
                asset = self._handle_callbacks(
                    asset=asset,
                    callbacks=callbacks,
                    all_fields=all_fields,
                    state=state,
                    schemas=schemas,
                    getargs=getargs,
                    callback_error=callback_error,
                    store=store,
                )

                for item in tools.listify(obj=asset):
                    state["rows_processed"] += 1
                    yield item

                if max_rows and state["rows_processed"] >= max_rows:
                    break

            jstate = jdump(state)

            if not assets:
                msg = "stop fetch loop: page with no assets:\n{}".format(jstate)
                self._log.debug(msg)
                state["done"] = True
            elif state["max_pages"] and state["page_num"] >= state["max_pages"]:
                msg = "stop fetch loop: hit max_pages:\n{}".format(jstate)
                self._log.debug(msg)
                state["done"] = True
            elif state["max_rows"] and state["rows_processed"] >= state["max_rows"]:
                msg = "stop fetch loop: hit max_rows:\n{}".format(jstate)
                self._log.debug(msg)
                state["done"] = True

            if state["done"]:
                self._handle_callbacks(
                    asset="DONE",
                    callbacks=callbacks,
                    all_fields=all_fields,
                    state=state,
                    schemas=schemas,
                    getargs=getargs,
                    callback_error=callback_error,
                )
                break
            time.sleep(page_sleep)

        self._log.debug("Finished fetch:\n{}".format(jstate))

    def _handle_callbacks(
        self,
        asset,
        callbacks,
        all_fields,
        state,
        schemas,
        getargs,
        callback_error,
        store,
    ):
        jdump = tools.json_dump
        this_store = {}

        for callback in callbacks:
            if not callable(callback):
                msg = "Callback provided is not callable! {}".format(callback)
                raise exceptions.ApiError(msg)

            try:
                asset = callback(
                    asset=asset,
                    apiobj=self,
                    callbacks=callbacks,
                    all_fields=all_fields,
                    state=state,
                    this_store=this_store,
                    schemas=schemas,
                    getargs=getargs,
                    store=store,
                )
            except Exception:
                msg = "Error in callback {}:\n{}"
                msg = msg.format(callback, jdump(state))
                self._log.exception(msg)

                if callback_error:
                    raise
        return asset

    def _figure_page_size(self, page_size=None, max_rows=None):
        page_size = page_size or constants.MAX_PAGE_SIZE

        if page_size > constants.MAX_PAGE_SIZE:
            msg = "Changed page_size={ps} to max_page_size={mps}"
            msg = msg.format(ps=page_size, mps=constants.MAX_PAGE_SIZE)
            self._log.debug(msg)
            page_size = constants.MAX_PAGE_SIZE

        if max_rows and max_rows < page_size:
            page_size = max_rows
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
        **kwargs,
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
            check = "aggregated"

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

    def get_flat(self, short=False, all_fields=None):
        """Return a flat dict of fields keyed on the fqdn of field."""
        all_fields = all_fields or self.get()
        if short:
            return {
                f["column_name"]: f for fs in all_fields.values() for f in fs.values()
            }
        return {f["name"]: f for fs in all_fields.values() for f in fs.values()}

    def get_schemas(self, fields, all_fields=None):
        """Get the flattened schema of selected fields."""
        all_fields = all_fields or self.get()
        flat = self.get_flat(all_fields=all_fields)

        schemas = {}
        for field in fields:
            if field in flat:
                schemas[field] = flat[field]
            else:
                self._log.warning("field {} not found in schemas!".format(field))
        return schemas

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
            search_adapter, search_fields = ("aggregated", check)

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

    def _add(self, key, value, dest):
        """Sanity check to make sure a key is not duplicated during parsing.

        Args:
            key (:obj:`str`): key to check in dest
            dest (:obj:`list` of :obj:`str`): obj to check if key already exists in
            desc (:obj:`str`): description of key

        Raises:
            :exc:`exceptions.ApiError`: if key already exists in dest
        """
        if key in dest:
            msg = "Key {key!r} value {value!r} already exists in {dest}"
            msg = msg.format(value=value, key=key, dest=dest)
            raise exceptions.ApiError(msg)
        dest[key] = value

    @property
    def _fmaps(self):
        """Map of field types into their normalized typed.

        Returns:
            :obj:`tuple` of :obj:`tuple`
        """
        return (
            # (type, format, items.type, items.format), normalized
            (("string", "", "", ""), "string"),
            (("string", "date-time", "", ""), "string_datetime"),
            (("string", "image", "", ""), "string_image"),
            (("string", "version", "", ""), "string_version"),
            (("string", "ip", "", ""), "string_ipaddress"),
            (("bool", "", "", ""), "bool"),
            (("integer", "", "", ""), "integer"),
            (("number", "", "", ""), "number"),
            (("array", "table", "array", ""), "complex_table"),
            (("array", "", "array", ""), "complex"),
            (("array", "", "integer", ""), "integer"),
            (("array", "", "string", ""), "string"),
            (("array", "", "string", "tag"), "string"),
            (("array", "version", "string", "version"), "string_version"),
            (("array", "date-time", "string", "date-time"), "string_datetime"),
            (("array", "subnet", "string", "subnet"), "string_subnet"),
            (("array", "discrete", "string", "logo"), "string"),
            (("array", "ip", "string", "ip"), "string_ipaddress"),
        )

    def _normtype(self, field):
        """Get the normalized type of a field."""
        ftype = field["type"]
        ffmt = field.get("format", "")
        fitype = field.get("items", {}).get("type", "")
        fifmt = field.get("items", {}).get("format", "")
        check = (ftype, ffmt, fitype, fifmt)

        for fmap in self._fmaps:
            if check == fmap[0]:
                return fmap[1]

        check = dict(zip(("type", "format", "items.type", "items.format"), check))
        fmsg = "Unmapped normalized type: {}: {}".format(field["name"], check)
        self._log.warning(fmsg)
        return "unknown"

    def is_complex(self, field):
        """Determine if a field is complex from its schema."""
        field_type = field["type"]
        field_items_type = field.get("items", {}).get("type")
        if field_type == "array" and field_items_type == "array":
            return True
        return False

    def is_root(self, name, names):
        """Determine if a field is a root field."""
        dots = name.split(".")
        return not (len(dots) > 1 and dots[0] in names)

    def _handle_complex(self, field):
        """Pass."""
        field["is_complex"] = self.is_complex(field=field)
        if field["is_complex"]:
            col_title = field["column_title"]
            col_name = field["column_name"]
            name_base = field["name_base"]
            prefix = field["adapter"]["prefix"]
            field["sub_fields"] = sub_fields = {}
            items = field.pop("items")["items"]

            field_names = [f["name"] for f in items]

            for sub_field in items:
                sub_title = sub_field["title"]
                sub_name = sub_field["name"]
                sub_name_base = "{}.{}".format(name_base, sub_name)
                sub_name_qual = "{}.{}".format(prefix, sub_name_base)

                sub_field["name_base"] = sub_name_base
                sub_field["name_qual"] = sub_name_qual
                sub_field["is_root"] = self.is_root(name=sub_name, names=field_names)
                sub_field["adapter"] = field["adapter"]
                sub_field["column_title"] = "{}: {}".format(col_title, sub_title)
                sub_field["column_name"] = "{}.{}".format(col_name, sub_name)
                sub_field["type_norm"] = self._normtype(field=sub_field)
                self._handle_complex(field=sub_field)
                self._add(key=sub_field["name"], value=sub_field, dest=sub_fields)

    def _fields(self, name, prefix, prefix_parse, title, raw_fields):
        """Parse fields."""
        fields = {}

        adapter = {
            "prefix": prefix,
            "title": title,
            "prefix_parse": prefix_parse,
            "name": name,
        }

        fields["all"] = {
            "name": name,
            "name_base": name,
            "title": "All data",
            "type": "array",
            "type_norm": "complex_complex",
            "adapter": adapter,
            "is_complex": True,
            "is_root": False,
            "column_title": "{}: All Data".format(title),
            "column_name": "{}:all".format(prefix_parse),
        }

        field_names = [
            tools.strip_left(obj=f["name"], fix=prefix).strip(".") for f in raw_fields
        ]

        for field in raw_fields:
            name_base = tools.strip_left(obj=field["name"], fix=prefix).strip(".")
            field["name_base"] = name_base
            field["name_qual"] = field["name"]
            field["is_root"] = self.is_root(name=name_base, names=field_names)
            field["adapter"] = adapter
            field["column_title"] = "{}: {}".format(title, field["title"])
            field["column_name"] = "{}:{}".format(prefix_parse, name_base)
            field["type_norm"] = self._normtype(field=field)
            self._handle_complex(field=field)
            self._add(key=name_base, value=field, dest=fields)

        return fields

    def parse(self):
        """Parse all generic and adapter specific fields.

        Returns:
            :obj:`dict`: parsed generic and adapter specific fields
        """
        parsed = {}
        parsed["aggregated"] = self._fields(
            name="specific_data",
            prefix="specific_data.data",
            prefix_parse="agg",
            title="Aggregated",
            raw_fields=self._raw["generic"],
        )

        for name, raw_fields in self._raw["specific"].items():
            # name = aws_adapter
            prefix = "adapters_data.{}".format(name)
            # prefix = adapters_data.aws_adapter
            prefix_parse = tools.strip_right(obj=name, fix="_adapter")
            # prefix_parse = aws
            title = " ".join(prefix_parse.split("_")).title()
            # title = "Aws"
            fields = self._fields(
                name=name,
                prefix=prefix,
                prefix_parse=prefix_parse,
                title=title,
                raw_fields=raw_fields,
            )
            self._add(key=prefix_parse, value=fields, dest=parsed)

        return parsed


def nuller(field, schema, asset):
    """Null out missing fields."""
    if schema["is_complex"]:
        asset[field] = asset.get(field, [])
        for entry in asset[field]:
            for sub_field, sub_schema in schema["sub_fields"].items():
                nuller(field=sub_field, schema=sub_schema, asset=entry)
    else:
        asset[field] = asset.get(field, None)


def cb_nulls(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Asset callback to add None values to fields not returned."""
    if not isinstance(asset, dict):
        return asset

    for field, schema in schemas.items():
        nuller(asset=asset, field=field, schema=schema)
    return asset


def cb_excludes(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Asset callback to remove fields from asset."""
    if not isinstance(asset, dict):
        return asset

    excludes = getargs.get("field_excludes", []) or []
    excludes = tools.listify(obj=excludes or [])
    excludes = [i.strip() for f in excludes for i in f.split(",") if i.strip()]

    for field in list(asset):
        for exclude in excludes:
            if field in asset and re.search(exclude, field, re.I):
                asset.pop(field)
    return asset


def cb_firstpage(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Asset callback to echo first page info using an echo method."""
    if not isinstance(asset, dict):
        return asset

    if state.get("first_done", False):
        return asset

    state["first_done"] = True

    page_info = state.get("page_info", {})
    query = state.get("query", "") or ""
    total_assets = page_info.get("totalResources", 0)
    total_pages = page_info.get("totalPages", 0)
    page_assets = page_info.get("size", 0)

    stmpl = "{name} -> {column_title!r}".format
    schemas = [stmpl(**v) for v in schemas.values()]

    lines = [
        "First page received with {} assets".format(page_assets),
        "Total assets: {}, total pages: {}".format(total_assets, total_pages),
        "Using query: {}".format(query),
        "With fields:\n   - {}".format("\n   - ".join(schemas)),
    ]

    for line in lines:
        cli.context.click_echo_ok(line)
    return asset


def cb_jsonstream(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Asset callback to write to jsonstreams context handler."""
    if asset == "DONE":
        stream = getargs["jsonstream"]
        stream.close()
        return asset

    if not isinstance(asset, dict):
        return asset

    if "jsonstream" not in getargs:
        getargs["jsonstream"] = cli.serial.JsonStream(**getargs)

    stream = getargs["jsonstream"]
    stream.write(asset)
    del asset


def cb_joiner(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Join values."""
    if not isinstance(asset, dict):
        return asset

    joiner = getargs.get("export_delim", constants.CELL_JOINER)
    trim = getargs.get("export_trim_cells", True)

    for field in asset:
        if isinstance(asset[field], constants.LIST):
            asset[field] = joiner.join([format(x) for x in asset[field]])

        if trim and isinstance(asset[field], constants.STR):
            if len(asset[field]) >= constants.CELL_MAX_LEN:
                msg = constants.CELL_MAX_STR.format(c=len(asset[field]))
                asset[field] = "\n".join([asset[field][: constants.CELL_MAX_LEN], msg])
    return asset


def cb_flatten(
    asset, apiobj, callbacks, all_fields, state, getargs, schemas, this_store, store
):
    """Asset callback to flatten complex fields."""
    if not isinstance(asset, dict):
        return asset

    for field, schema in schemas.items():
        if not schema["is_complex"]:
            continue

        items = asset.pop(field, []) or []

        for sub_field, sub_schema in schema["sub_fields"].items():
            if not sub_schema["is_root"]:
                continue

            name_qual = sub_schema["name_qual"]
            name = sub_schema["name"]

            if name_qual in asset and name_qual not in state.get("flat_warn", []):
                state["flat_warn"] = state.get("flat_warn", [])
                state["flat_warn"].append(name_qual)
                msg = "overwriting sub_field {!r} in asset!".format(name_qual)
                apiobj._log.warning(msg)

            asset[name_qual] = []

            for item in items:
                if name not in item:
                    continue

                value = item[name]

                if isinstance(value, constants.LIST):
                    asset[name_qual] += value
                else:
                    asset[name_qual].append(value)
    return asset


# XXX cnx getconfig
# XXX cnx add: take in json via stdin or file to create connections
# XXX fields get CLI needs to add at least title (maybe normtype too?)
# XXX CB for % done, time left
# XXX CB for missing adapters report
# XXX CB csv can dictwriter take in sys.stdout as fd?
# XXX CB csv trim=False option
# XXX CB csv needs to check if cb_flatten is in callbacks
# def cb_serialize_values(asset, **kwargs):
#     """Asset callback to serialize values."""
#     trim = kwargs.get('export_trim_cells', False)
#     joiner = kwargs.get('export_delim')

#     for field, value in asset.items():
#         if isinstance(value, constants.SIMPLE_NONE):
#             continue

#         if isinstance(value, constants.LIST):
#             if not value:
#                 asset[field] = None
#                 continue

#             value1 = value[0]

#             if isinstance(value1, constants.SIMPLE_NONE):
#                 asset[field] = join_cell(obj=value, trim=trim, joiner=joiner)
#             elif isinstance(value1, dict):
#                 # SCHEMAS BOO
#         if tools.is_los(value):
#             asset[field] = join_cr(raw_value, is_cell=True, joiner=joiner)
#             continue

#         if is_list(raw_value) and all([is_dos(x) for x in raw_value]):
#             values = {}

#             for raw_item in raw_value:
#                 for k, v in raw_item.items():
#                     new_key = "{}.{}".format(raw_key, k)

#                     values[new_key] = values.get(new_key, [])

#                     values[new_key] += tools.listify(v, dictkeys=False)

#             for k, v in values.items():
#                 row[k] = join_cr(v, is_cell=True, joiner=joiner)

#             continue

#         msg = "Data of type {t} is too complex for this export format"
#         msg = msg.format(t=type(raw_value).__name__)
#         row[raw_key] = msg
#     return rows
