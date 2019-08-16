# -*- coding: utf-8 -*-
"""Axonius API Client package."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import routers, mixins
from .. import tools, constants, exceptions, models


class SavedQuery(object):
    """Pass."""

    def __init__(self, parent):
        """Pass."""
        self._parent = parent

    def __str__(self):
        """Pass."""
        return "Saved Query commands for {}".format(self._parent)

    def __repr__(self):
        """Pass."""
        return self.__str__()

    def create(
        self,
        name,
        query,
        sort_field="",
        sort_descending=True,
        sort_adapter="generic",
        default_fields=True,
        manual_fields=None,
        **fields
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
        page_size = fields.pop("page_size", constants.GUI_PAGE_SIZES[0])

        if page_size not in constants.GUI_PAGE_SIZES:
            msg = "page_size {size} invalid, must be one of {sizes}"
            msg = msg.format(size=page_size, sizes=constants.GUI_PAGE_SIZES)
            raise exceptions.ApiError(msg)

        self._parent._check_max_page_size(page_size=page_size)

        if not fields and default_fields:
            for k, v in self._parent._default_fields.items():
                fields.setdefault(k, v)

        known = self._parent.fields()

        if manual_fields:
            validated_fields = manual_fields
        else:
            validated_fields = self._parent._validate_fields(known=known, **fields)

        if sort_field:
            sort_field = self._parent._find_field(
                name=sort_field, known=known, adapter=sort_adapter
            )

        data = {}
        data["name"] = name
        data["query_type"] = "saved"

        data["view"] = {}
        data["view"]["fields"] = validated_fields
        # FUTURE: find out what this is (historical data?)
        data["view"]["historical"] = None
        data["view"]["columnSizes"] = []
        # FUTURE: find out if this only impacts GUI
        data["view"]["page"] = 0
        data["view"]["pageSize"] = page_size

        data["view"]["query"] = {}
        data["view"]["query"]["filter"] = query

        data["view"]["sort"] = {}
        data["view"]["sort"]["desc"] = sort_descending
        data["view"]["sort"]["field"] = sort_field

        return self._parent._request(
            method="post", path=self._parent._router.views, json=data
        )

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
        if not isinstance(found, (list, tuple)):
            found = [found]
        return self._delete(ids=[x["uuid"] for x in found])

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

        only1 = (
            kwargs.get("count_min", None) == 1 and kwargs.get("count_max", None) == 1
        )

        return found[0] if only1 else found

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
            )

            if not page["assets"]:
                do_break = True

            if do_break:
                break

        return rows

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


class Labels(object):
    """Pass."""

    def __init__(self, parent):
        """Pass."""
        self._parent = parent

    def __str__(self):
        """Pass."""
        return "Label commands for {}".format(self._parent)

    def __repr__(self):
        """Pass."""
        return self.__str__()

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

    # FUTURE: needs tests
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

    # FUTURE: needs tests
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


class UserDeviceMixin(models.ApiModelUserDevice, mixins.ApiMixin):
    """Mixins for User & Device models."""

    def _init(self, auth, **kwargs):
        """Pass."""
        self.labels = Labels(parent=self)
        self.saved_query = SavedQuery(parent=self)

    def fields(self):
        """Get the fields.

        Notes:
            Will only return fields on Axonius v2.7 or greater. Caches result to self.

        Returns:
            :obj:`dict`

        """
        return self._request(method="get", path=self._router.fields)

    def count(self, query=None):
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
        return self._request(method="get", path=self._router.count, params=params)

    def _check_counts(
        self, value, value_type, objtype, count_total, count_min, count_max
    ):
        """Pass."""
        if count_min == 1 and count_max == 1:
            if count_total != 1:
                raise exceptions.ObjectNotFound(
                    value=value, value_type=value_type, object_type=objtype, exc=None
                )
            return True

        if count_min is not None and count_total < count_min:
            raise exceptions.TooFewObjectsFound(
                value=value,
                value_type=value_type,
                object_type=objtype,
                count_total=count_total,
                count_min=count_min,
            )

        if count_max is not None and count_total > count_max:
            raise exceptions.TooManyObjectsFound(
                value=value,
                value_type=value_type,
                object_type=objtype,
                count_total=count_total,
                count_max=count_max,
            )
        return False

    def get(self, query=None, count_min=None, count_max=None, **fields):
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
            fields: Fields to include in result.

                >>> generic=['f1', 'f2'] # for generic fields.
                >>> adapter=['f1', 'f2'] # for adapter specific fields.

        Returns:
            :obj:`list` of :obj:`dict` or :obj:`dict`

        """
        page_size = fields.pop("page_size", constants.DEFAULT_PAGE_SIZE)
        manual_fields = fields.pop("manual_fields", False)
        default_fields = fields.pop("default_fields", True)

        if not fields and default_fields:
            for k, v in self._default_fields.items():
                fields.setdefault(k, v)

        if manual_fields:
            validated_fields = manual_fields
        else:
            validated_fields = self._validate_fields(**fields)

        if count_max is not None and count_max < page_size:
            page_size = count_max

        count_total = 0

        rows = []

        while True:
            page = self._get(
                query=query,
                fields=validated_fields,
                row_start=count_total,
                page_size=page_size,
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
        """Pass.

        Future: Flush out.
        """
        # TODO THROW ERROR WHEN NAME DOES NOT EXIST
        page_size = kwargs.pop("page_size", constants.DEFAULT_PAGE_SIZE)
        sq = self.saved_query.get(name=name, regex=False, count_min=1, count_max=1)
        query = sq["view"]["query"]["filter"]
        manual_fields = sq["view"]["fields"]
        return self.get(query=query, page_size=page_size, manual_fields=manual_fields)

    def get_by_field_value(self, value, field, field_adapter, regex=False, **kwargs):
        """Build query to perform equals or regex search.

        Args:
            value (:obj:`str`):
                Value to search for equals or regex query against field.
            field (:obj:`str`):
                Field to use when building equals or regex query.
            field_adapter (:obj:`str`):
                Adapter field is from.
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

        field = self._find_field(name=field, adapter=field_adapter)

        kwargs.setdefault("query", query.format(field=field, value=value))

        return self.get(**kwargs)

    def _get(self, query=None, fields=None, row_start=0, page_size=0):
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
            if isinstance(fields, (list, tuple)):
                fields = ",".join(fields)
            params["fields"] = fields
        return self._request(method="get", path=self._router.root, params=params)

    def _find_adapter(self, name, known=None):
        """Find an adapter by name.

        Args:
            name (:obj:`str`):
                Name of adapter to find.
            known (:obj:`dict`, optional):
                Return from :meth:`fields`.

                Defaults to: None.

        Raises:
            :exc:`exceptions.UnknownError`: If name can not be found in known.

        Returns:
            :obj:`str`

        """
        known = known or self.fields()
        postfix = "_adapter"

        known_adapters = list(known["specific"].keys())

        checks = [name, name + postfix]

        found = None

        for check in checks:
            if check in known_adapters:
                found = known_adapters[known_adapters.index(check)]

        if not found:
            raise exceptions.UnknownError(
                value=name,
                known=tools.rstrip(obj=known_adapters, postfix=postfix),
                reason_msg="adapter by name",
                valid_msg="adapter names",
            )

        msg = "Resolved adapter name {name!r} to {found!r}"
        msg = msg.format(name=name, found=found)
        self._log.debug(msg)

        return found

    def _find_field(self, name, adapter, known=None):
        """Find a field for a given adapter.

        Args:
            name (:obj:`str`):
                Name of field to find.
            adapter (:obj:`str`):
                Name of adapter to look for field in.
                If 'generic' look for the field in generic fields.
            known (:obj:`dict`, optional):
                Return from :meth:`fields`.

                Defaults to: None.

        Notes:
            If adapter 'generic', ensure name begins with
            :attr:`axonius_api_client.constants.GENERIC_FIELD_PREFIX`,
            otherwise ensure name begins with
            :attr:`axonius_api_client.constants.ADAPTER_FIELD_PREFIX`.

            If fields is None, we can't validate that the field exists, so we just ensure
            the name is fully qualified.

            If name in "all" or prefix, returns prefix.

        Raises:
            :exc:`exceptions.UnknownError`:
                If fields is not None and name can not be found in fields.

        Returns:
            :obj:`str`

        """
        known = known or self.fields()

        if adapter in ["generic", "specific", "general"]:
            prefix = constants.GENERIC_FIELD_PREFIX
            container = known["generic"]
        else:
            adapter = self._find_adapter(name=adapter, known=known)
            prefix = constants.ADAPTER_FIELD_PREFIX.format(adapter_name=adapter)
            container = known["specific"][adapter]

        if not name.startswith(prefix):
            fq_name = ".".join([x for x in [prefix, name] if x])
        else:
            fq_name = name

        found = None

        if not container:
            found = name if name in ["adapters", "labels"] else fq_name
        else:
            known = [x["name"] for x in container]

            for check in [name, fq_name]:
                if check in ["all", prefix]:
                    found = prefix
                    break
                if check in known:
                    found = known[known.index(check)]
                    break

        if not found:
            known = tools.lstrip(obj=known, prefix=prefix + ".")
            known += ["all", prefix]
            raise exceptions.UnknownError(
                value=name,
                known=known,
                reason_msg="adapter {adapter} by field".format(adapter=adapter),
                valid_msg="field names",
            )

        msg = "Resolved {adapter!r} field name {name!r} to {found!r}"
        msg = msg.format(adapter=adapter, name=name, found=found)
        self._log.debug(msg)

        return found

    def _validate_fields(self, known=None, **fields):
        """Validate provided fields are valid.

        Args:
            known (:obj:`dict`):
                Known fields from
                :meth:`axonius_api_client.api.interfaces.UserDeviceModel.fields`.
            **fields: Fields to validate.
                * generic=['f1', 'f2'] for generic fields.
                * adapter=['f1', 'f2'] for adapter specific fields.

        Notes:
            This will try to use known to validate the device
            fields, but if known is empty it will just ensure the fields are
            fully qualified.

            * generic=['field1'] => ['specific_data.data.field1']
            * adapter=['field1'] =>['adapters_data.adapter_name.field1']

        Returns:
            :obj:`list` of :obj:`str`

        """
        validated_fields = []
        known = known or self.fields()

        for name, afields in fields.items():
            if not isinstance(afields, (tuple, list)):
                continue
            for field in afields:
                field = self._find_field(name=field, known=known, adapter=name)
                if field not in validated_fields:
                    validated_fields.append(field)

        msg = "Resolved fields {fields} to {validated_fields}"
        msg = msg.format(fields=fields, validated_fields=validated_fields)
        self._log.debug(msg)
        return validated_fields


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
        return {
            "generic": [
                "adapters",
                "labels",
                "specific_data.data.username",
                "specific_data.data.last_seen",
                "specific_data.data.mail",
            ]
        }

    def get_by_name(self, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.username")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)

    def get_by_email(self, value, **kwargs):
        """Get objects by email using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.mail".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.mail")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)


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
                "adapters",
                "labels",
                "specific_data.data.hostname",
                "specific_data.data.network_interfaces.ips",
                "specific_data.data.last_seen",
            ]
        }

    def get_by_name(self, value, **kwargs):
        """Get objects by name using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.username".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching name or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.hostname")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)

    # TODO: get_by_ip
    # TODO: get_by_in_subnet
    # TODO: get_by_not_in_subnet
    def get_by_mac(self, value, **kwargs):
        """Get objects by MAC using paging.

        Args:
            value (:obj:`int`):
                Value to find using field "specific_data.data.network_interfaces.mac".
            **kwargs: Passed thru to :meth:`UserDeviceModel.get_by_field_value`

        Returns:
            :obj:`list` of :obj:`dict`: Each row matching email or :obj:`dict` if only1.

        """
        kwargs.setdefault("field", "specific_data.data.network_interfaces.mac")
        kwargs.setdefault("field_adapter", "generic")
        kwargs["value"] = value
        return self.get_by_field_value(**kwargs)
