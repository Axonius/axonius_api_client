# -*- coding: utf-8 -*-
"""API models for working with device and user assets."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from .. import constants, exceptions, tools
from . import mixins


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
