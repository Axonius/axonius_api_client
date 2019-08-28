# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import, division, print_function, unicode_literals

import ipaddress

from .. import constants, exceptions, tools
from . import adapters, mixins, routers


class SavedQuery(mixins.Child):
    """Pass."""

    def _get_direct(self, query=None, row_start=0, page_size=0):
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
            page_size (:obj:`int`, optional):
                If not 0, include N rows in the return.

                Defaults to: 0.

        Returns:
            :obj:`dict`

        """
        self._parent._check_max_page_size(page_size=page_size)

        params = {}

        if page_size:
            params["limit"] = page_size

        if row_start:
            params["skip"] = row_start

        if query:
            params["filter"] = query

        return self._parent._request(
            method="get", path=self._parent._router.views, params=params
        )

    def _get(self, query=None, count_min=None, count_max=None, **kwargs):
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
        page_size = kwargs.pop("page_size", constants.DEFAULT_PAGE_SIZE)
        known_cb = kwargs.pop("known_callback", self.get_names)

        rows = []
        count_total = 0
        objtype = self._parent._router._object_type
        objtype = "Saved Query filter for {o}".format(o=objtype)

        while True:
            page = self._get_direct(
                query=query, page_size=page_size, row_start=count_total
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
                known_callback=known_cb,
            )

            if not page["assets"]:
                do_break = True

            if do_break:
                break

        return rows

    def _delete(self, ids):
        """Delete saved queries by ids.

        Args:
            ids (:obj:`list` of :obj:`str`):
                List of UUID's of saved queries to delete.

        Returns:
            :obj:`str`: empty string

        """
        data = {"ids": ids}
        return self._parent._request(
            method="delete", path=self._parent._router.views, json=data
        )

    def create(
        self,
        name,
        query,
        sort_field="",
        sort_descending=True,
        sort_adapter="generic",
        manual_fields=None,
        page=0,
        page_size=None,
        historical=None,
        **kwargs
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
        page_size = page_size or constants.GUI_PAGE_SIZES[0]

        if page_size not in constants.GUI_PAGE_SIZES:
            msg = "page_size {size} invalid, must be one of {sizes}"
            msg = msg.format(size=page_size, sizes=constants.GUI_PAGE_SIZES)
            raise exceptions.ApiError(msg)

        self._parent._check_max_page_size(page_size=page_size)

        if "fields" not in kwargs:
            kwargs["fields"] = self._parent.fields.get()

        if manual_fields:
            val_fields = manual_fields
        else:
            val_fields = self._parent.fields.validate(**kwargs)

        if sort_field:
            sort_field = self._parent.fields.find(
                name=sort_field, adapter_name=sort_adapter, **kwargs
            )

        data = {}
        data["name"] = name
        data["query_type"] = "saved"

        data["view"] = {}
        data["view"]["fields"] = val_fields
        data["view"]["columnSizes"] = []
        # FUTURE: find out what this does (historical data toggle?)
        data["view"]["historical"] = historical
        # FUTURE: find out what this does (first page shown in GUI?)
        data["view"]["page"] = page
        data["view"]["pageSize"] = page_size

        data["view"]["query"] = {}
        data["view"]["query"]["filter"] = query

        data["view"]["sort"] = {}
        data["view"]["sort"]["desc"] = sort_descending
        data["view"]["sort"]["field"] = sort_field

        created = self._parent._request(
            method="post", path=self._parent._router.views, json=data
        )
        found = self.get(name=name)
        assert found["uuid"] == created, "UUID Mismatch between created and found!"
        return found

    def delete(self, name, regex=False, **kwargs):
        """Delete a saved query by name.

        Args:
            name (:obj:`str`):
                Name of saved query to delete.
            regex (:obj:`bool`, optional):
                Search for name using regex.

                Defaults to: False.
            only1 (:obj:`bool`, optional):
                Only allow one match to name.

                Defaults to: True.

        Returns:
            :obj:`str`: empty string

        """
        found = self.get(name=name, regex=regex, **kwargs)
        found = found if tools.is_type.list(found) else [found]
        return self._delete(ids=[x["uuid"] for x in found])

    # FUTURE add get_by_create_user
    # FUTURE add get_by_mod_time
    # FUTURE add get_by_fetch_time
    def get(self, name=None, regex=False, **kwargs):
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
        if name:
            if regex:
                query = 'name == regex("{name}", "i")'.format(name=name)
                kwargs.setdefault("query", query)
            else:
                query = 'name == "{name}"'.format(name=name)
                kwargs.setdefault("count_min", 1)
                kwargs.setdefault("count_max", 1)
                kwargs.setdefault("query", query)

        found = self._get(**kwargs)

        count_min = kwargs.get("count_min", None)
        count_max = kwargs.get("count_max", None)

        return found[0] if count_min == 1 and count_max == 1 else found

    def get_names(self, **kwargs):
        """Pass."""
        return sorted([x["name"] for x in self._get()])


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
        return self._parent._request(
            method="post", path=self._parent._router.labels, json=data
        )

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
        return self._parent._request(
            method="delete", path=self._parent._router.labels, json=data
        )

    def get(self):
        """Get the labels.

        Returns:
            :obj:`list` of :obj:`str`

        """
        return self._parent._request(method="get", path=self._parent._router.labels)

    def add_by_rows(self, rows, labels):
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

    def add(self, query, labels):
        """Add labels to objects using a query to select objects.

        Args:
            query (:obj:`str`):
                Query built from Query Wizard in GUI to select objects to add labels to.
            labels (:obj:`list` of `str`):
                Labels to add to rows returned from query.

        Returns:
            :obj:`int`: Number of objects that had labels added

        """
        rows = self._parent.get(query=query, default_fields=False)
        return self.add_by_rows(rows=rows, labels=labels)

    def delete_by_rows(self, rows, labels):
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

    def delete(self, query, labels):
        """Delete labels from objects using a query to select objects.

        Args:
            query (:obj:`str`):
                Query built from Query Wizard in GUI to select objects to delete labels
                from.
            labels (:obj:`list` of `str`):
                Labels to delete from rows returned from query.

        Returns:
            :obj:`int`: Number of objects that had labels deleted

        """
        rows = self._parent.get(query=query, default_fields=False)
        return self.delete_by_rows(rows=rows, labels=labels)


# FUTURE: how to get raw_data fields without using 'specific_data'
class Fields(mixins.Child):
    """Pass."""

    _GENERIC_ALTS = ["generic", "general", "specific"]
    _ALL_ALTS = ["all", "", "*", "specific_data"]
    _FORCE_SINGLE = ["specific_data", "specific_data.data"]
    _INVALID = "INVALID_"

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

    def find_adapter(self, name, error=True, **kwargs):
        """Find an adapter by name.

        Args:
            name (:obj:`str`):
                Name of adapter to find.
            fields (:obj:`dict`, optional):
                Return from :meth:`get`.

                Defaults to: None.

        Raises:
            :exc:`exceptions.UnknownError`: If name can not be found in known.

        Returns:
            :obj:`str`, :obj:`dict`

        """
        fields = kwargs.get("fields", None) or self.get()
        check_name = tools.strip.right(name, "_adapter").lower()

        if check_name in self._GENERIC_ALTS:
            check_name = "generic"

        if check_name in fields:
            return check_name, fields[check_name]

        if error:
            raise exceptions.UnknownError(
                value=name,
                known=list(fields),
                reason_msg="adapter by name",
                valid_msg="adapter names",
            )

        msg = "Failed to validate adapter {cn!r} (supplied {n!r})"
        msg = msg.format(n=name, cn=check_name)
        self._log.warning(msg)

        return self._INVALID + name, {}

    def find(self, name, adapter_name, error=True, **kwargs):
        """Find a field for a given adapter.

        Args:
            name (:obj:`str`):
                Name of field to find.
            adapter_name (:obj:`str`):
                Name of adapter to look for field in.

        Raises:
            :exc:`exceptions.UnknownError`:
                If fields is not None and name can not be found in fields.

        Returns:
            :obj:`str`

        """
        fields = kwargs.get("fields", None) or self.get()

        aname, afields = self.find_adapter(
            name=adapter_name, fields=fields, error=error
        )

        check_name = name.lower()

        if check_name in self._ALL_ALTS:
            check_name = "all"

        for short_name, field_info in afields.items():
            if check_name in [short_name, field_info["name"]]:
                vfield = field_info["name"]

                msg = "Validated adapter name {a!r} field {f!r} as {v!r}"
                msg = msg.format(a=aname, f=name, v=vfield)
                self._log.debug(msg)

                return aname, vfield

        if error:
            raise exceptions.UnknownError(
                value=name,
                known=list(afields),
                reason_msg="adapter {a!r} by field".format(a=aname),
                valid_msg="field names",
            )

        msg = "Failed to validate field {cn!r} (supplied {n!r}) for adapter {a!r}"
        msg = msg.format(n=name, cn=check_name, a=aname)
        self._log.warning(msg)

        return aname, self._INVALID + name

    @staticmethod
    def _conjoin_dol(cd, d):
        for k, v in d.items():
            if tools.is_type.str(k):
                if k not in cd:
                    cd[k] = []
                for x in tools.listify(v):
                    if x not in cd[k] and tools.is_type.str(x):
                        cd[k].append(x)

    def validate(self, fields=None, fields_error=True, default_fields=True, **kwargs):
        """Validate provided fields.

        Args:
            **kwargs: Fields to validate.
                * generic=['f1', 'f2'] for generic fields.
                * adapter=['f1', 'f2'] for adapter specific fields.

        Returns:
            :obj:`list` of :obj:`str`

        """
        fields = fields or self.get()
        pfields = {}
        vfields = {}
        ofields = getattr(self._parent, "_default_fields", {})

        if default_fields and ofields and tools.is_type.dict(ofields):
            self._conjoin_dol(pfields, ofields)

        self._conjoin_dol(pfields, kwargs)

        for aname, afields in pfields.items():
            for afield in afields:
                vaname, vafield = self.find(
                    name=afield, adapter_name=aname, fields=fields, error=fields_error
                )

                if any([x.startswith(self._INVALID) for x in [vafield, vaname]]):
                    continue

                if vafield in self._FORCE_SINGLE:
                    vfields[vaname] = [vafield]
                    break

                if vaname not in vfields:
                    vfields[vaname] = []

                if vafield not in vfields[vaname]:
                    vfields[vaname].append(vafield)

        return [i for l in vfields.values() for i in l]


class Reports(mixins.Child):
    """Pass."""

    def adapters(
        self,
        serial_lines=False,
        serial_dates=False,
        unconfigured=False,
        others_not_seen=False,
        **kwargs
    ):
        """Pass."""
        sys_adapters = self._parent.adapters.get()
        broken_adapters = [x for x in sys_adapters if x["status_bool"] is False]
        unconfig_adapters = [x for x in sys_adapters if x["status_bool"] is None]

        fields = self._parent.fields.get()

        kwargs["fields"] = fields
        raw_rows = self._parent.get(**kwargs)
        rows = []

        for raw_row in raw_rows:
            row = {}
            missing = []
            row["adapters"] = tools.strip.right(raw_row.get("adapters", []), "_adapter")

            for k, v in raw_row.items():
                if "." in k or k in ["labels"]:
                    row[k] = v

            ftimes = raw_row.get("specific_data.data.fetch_time", []) or []
            ftimes = ftimes if tools.is_type.list(ftimes) else [ftimes]
            ftimes = [x for x in tools.dt.parse(ftimes)]

            for adapter in sys_adapters:
                name = adapter["name"]

                otype = self._parent.__class__.__name__.upper()
                other_status = name in fields

                if not other_status and not others_not_seen:
                    continue

                if not adapter["clients"] or adapter["status_bool"] is None:
                    if not unconfigured:
                        continue
                    ftime = "NEVER; NO CLIENTS"
                elif adapter["status_bool"] is False:
                    ftime = "NEVER; CLIENTS BROKEN"
                elif adapter["status_bool"] is True:
                    ftime = "NEVER; CLIENTS OK"

                if name in row["adapters"]:
                    try:
                        ftime = ftimes[row["adapters"].index(name)]
                    except Exception:
                        ftime = "UNABLE TO DETERMINE"
                elif other_status and name not in missing:
                    missing.append(name)

                if serial_dates:
                    ftime = format(ftime)

                if serial_lines:
                    status_lines = [
                        "FETCHED THIS {}: {}".format(otype.rstrip("S"), ftime),
                        "FETCHED OTHER {}: {}".format(otype, other_status),
                        "CLIENTS OK: {}".format(adapter["client_count_ok"]),
                        "CLIENTS BAD: {}".format(adapter["client_count_bad"]),
                    ]
                else:
                    status_lines = {
                        "FETCHED_THIS_{}".format(otype.rstrip("S")): ftime,
                        "FETCHED_OTHER_{}".format(otype): other_status,
                        "CLIENTS_OK": adapter["client_count_ok"],
                        "CLIENTS_BAD": adapter["client_count_bad"],
                    }

                row["adapter: {}".format(name)] = status_lines

            row["count_not_fetched"] = len(missing)
            row["count_fetched"] = len(row["adapters"])
            row["count_total"] = len(sys_adapters)
            row["count_total_broken"] = len(broken_adapters)
            row["count_total_unconfigured"] = len(unconfig_adapters)

            rows.append(row)

        return rows


class UserDeviceMixin(mixins.ModelUserDevice, mixins.Mixins):
    """Mixins for User & Device models."""

    def _init(self, auth, **kwargs):
        """Pass."""
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)
        self.fields = Fields(parent=self)
        self.reports = Reports(parent=self)
        self.adapters = adapters.Adapters(auth=auth, **kwargs)
        super(UserDeviceMixin, self)._init(auth=auth, **kwargs)

    def _get(self, query=None, fields=None, row_start=0, page_size=0, use_post=True):
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
        self._check_max_page_size(page_size=page_size)
        params = {}

        if row_start:
            params["skip"] = row_start

        if page_size:
            params["limit"] = page_size

        if query:
            params["filter"] = query

        if fields:
            params["fields"] = (
                ",".join(fields) if tools.is_type.list(fields) else fields
            )

        if use_post:
            return self._request(method="post", path=self._router.root, json=params)
        else:
            return self._request(method="get", path=self._router.root, params=params)

    def _check_counts(
        self,
        value,
        value_type,
        objtype,
        count_total,
        count_min,
        count_max,
        error=True,
        known_callback=None,
    ):
        """Pass."""
        if count_min == 1 and count_max == 1:
            if count_total != 1 and error:
                raise exceptions.ObjectNotFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    known_callback=known_callback,
                )
            return True

        if count_min is not None and count_total < count_min:
            if error:
                raise exceptions.TooFewObjectsFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    count_total=count_total,
                    count_min=count_min,
                )
            return True

        if count_max is not None and count_total > count_max:
            if error:
                raise exceptions.TooManyObjectsFound(
                    value=value,
                    value_type=value_type,
                    object_type=objtype,
                    count_total=count_total,
                    count_max=count_max,
                )
            return True
        return False

    def count(self, query=None, use_post=True):
        """Get the number of matches for a given query.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI.

        Returns:
            :obj:`int`

        """
        params = {}
        if query:
            params["filter"] = query

        if use_post:
            return self._request(method="post", path=self._router.count, json=params)
        else:
            return self._request(method="get", path=self._router.count, params=params)

    def get(
        self,
        query=None,
        count_min=None,
        count_max=None,
        count_error=True,
        page_size=None,
        manual_fields=None,
        use_post=True,
        **kwargs
    ):
        """Get objects for a given query using paging.

        Args:
            query (:obj:`str`, optional):
                Query built from Query Wizard in GUI to select rows to return.

                Defaults to: None.
            page_size (:obj:`int`, optional):
                Get N rows per page.

                Defaults to: :data:`axonius_api_client.constants.DEFAULT_PAGE_SIZE`.
            default_fields (:obj:`bool`, optional):
                Update fields with :attr:`_default_fields` if no fields supplied.

                Defaults to: True.
            kwargs: Fields to include in result.

                >>> generic=['f1', 'f2'] # for generic fields.
                >>> adapter=['f1', 'f2'] # for adapter specific fields.

        Returns:
            :obj:`list` of :obj:`dict` or :obj:`dict`

        """
        page_size = page_size or constants.DEFAULT_PAGE_SIZE

        if manual_fields:
            val_fields = manual_fields
        else:
            val_fields = self.fields.validate(**kwargs)

        count_less = count_max is not None and count_max < page_size
        page_size = count_max if count_less else page_size

        count_total = 0

        rows = []

        while True:
            page = self._get(
                query=query,
                fields=val_fields,
                row_start=count_total,
                page_size=page_size,
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

        return rows[0] if count_min == 1 and count_max == 1 else rows

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
        path = self._router.by_id.format(id=id)
        try:
            data = self._request(method="get", path=path)
        except exceptions.ResponseError as exc:
            raise exceptions.ObjectNotFound(
                value=id,
                value_type="Axonius ID",
                object_type=self._router._object_type,
                exc=exc,
            )
        return data

    def get_by_saved_query(self, name, **kwargs):
        """Pass."""
        sq = self.saved_query.get(name=name, regex=False, count_min=1, count_max=1)

        kwargs["query"] = sq["view"]["query"]["filter"]
        kwargs["manual_fields"] = sq["view"]["fields"]
        return self.get(**kwargs)

    def get_by_field_value(self, value, name, adapter_name, regex=False, **kwargs):
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
        if regex:
            query = '{field} == regex("{value}", "i")'
        else:
            query = '{field} == "{value}"'
            kwargs.setdefault("count_min", 1)
            kwargs.setdefault("count_max", 1)

        aname, afield = self.fields.find(name=name, adapter_name=adapter_name)
        kwargs.setdefault("query", query.format(field=afield, value=value))
        return self.get(**kwargs)


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
        return {"generic": ["id", "fetch_time", "labels", "username", "mail"]}

    def get_by_username(self, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs.setdefault("name", "username")
        kwargs.setdefault("adapter_name", "generic")
        return self.get_by_field_value(value=value, **kwargs)

    def get_by_mail(self, value, **kwargs):
        """Get objects by email using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "mail".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("name", "mail")
        kwargs.setdefault("adapter_name", "generic")
        return self.get_by_field_value(value=value, **kwargs)


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
        return {
            "generic": [
                "id",
                "fetch_time",
                "labels",
                "hostname",
                "network_interfaces.ips",
            ]
        }

    def get_by_hostname(self, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs.setdefault("name", "hostname")
        kwargs.setdefault("adapter_name", "generic")
        return self.get_by_field_value(value=value, **kwargs)

    def get_by_mac(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("name", "network_interfaces.mac")
        kwargs.setdefault("adapter_name", "generic")
        return self.get_by_field_value(value=value, **kwargs)

    def get_by_ip(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("name", "network_interfaces.ips")
        kwargs.setdefault("adapter_name", "generic")
        return self.get_by_field_value(value=value, **kwargs)

    def get_by_in_subnet(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        network = ipaddress.ip_network(value)

        begin = int(network.network_address)
        end = int(network.broadcast_address)

        match_field = "specific_data.data.network_interfaces.ips_raw"

        match = 'match({{"$gte": {begin}, "$lte": {end}}})'
        match = match.format(begin=begin, end=end)

        query = "{match_field} == {match}"
        query = query.format(match_field=match_field, match=match)

        kwargs["query"] = query
        return self.get(**kwargs)

    def get_by_not_in_subnet(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        network = ipaddress.ip_network(value)

        ip_begin = int(ipaddress.ip_address("0.0.0.0"))
        ip_end = int(ipaddress.ip_address("255.255.255.255"))

        begin = int(network.network_address)
        end = int(network.broadcast_address)

        field = "specific_data.data.network_interfaces.ips_raw"

        match1 = 'match({{"$gte": {ip_begin}, "$lte": {begin}}})'
        match1 = match1.format(begin=begin, ip_begin=ip_begin)

        match2 = 'match({{"$gte": {end}, "$lte": {ip_end}}})'
        match2 = match2.format(end=end, ip_end=ip_end)

        query = "{field} == {match1} or {field} == {match2}"
        query = query.format(field=field, match1=match1, match2=match2)

        kwargs["query"] = query
        return self.get(**kwargs)


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

        fields = {"all": {"name": prefix}}

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
